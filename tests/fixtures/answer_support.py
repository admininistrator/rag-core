"""Synthetic LLM wire responses through real adapters, explicitly NOT live generation."""

import json
from contextlib import asynccontextmanager

import httpx
import httpx2
from pydantic import SecretStr

from rag_core.adapters.llm.anthropic import AnthropicProvider
from rag_core.adapters.llm.config import AnthropicSettings, DeepSeekSettings
from rag_core.adapters.llm.deepseek import DeepSeekProvider
from tests.contract.test_llm_providers import MODEL, SYNTHETIC_KEY, json_response


def good_answer(data):
    if data["answerability"] == "insufficient_evidence":
        return {
            "answer": "Tài liệu hiện tại chưa đủ bằng chứng để trả lời. Bạn có thể cung cấp thêm thông tin?",
            "citations": [],
        }
    c = data["citation_allowlist"][0]
    return {
        "answer": f"Hà Nội là thủ đô của Việt Nam. [{c['id']}]",
        "citations": [{"id": c["id"], "quote": c["quote"]}],
    }


@asynccontextmanager
async def protocol_provider(provider="deepseek", responses=(), *, hook=None, usage=True):
    calls = []
    generation = []
    module = httpx if provider == "deepseek" else httpx2

    async def handler(request):
        body = json.loads(request.content)
        data = json.loads(body["messages"][-1]["content"])
        calls.append(body)
        if "answerability" not in data:  # Actual T23 rewrite protocol boundary.
            result = {"standalone_question": data["question"], "question_language": "vi"}
        else:
            generation.append(data)
            if hook is not None:
                await hook(data)
            result = (
                responses[min(len(generation) - 1, len(responses) - 1)]
                if responses
                else good_answer(data)
            )
            if callable(result):
                result = result(data)
        text = result if isinstance(result, str) else json.dumps(result, ensure_ascii=False)
        return module.Response(200, json=json_response(provider, text, usage=usage))

    settings_class = DeepSeekSettings if provider == "deepseek" else AnthropicSettings
    settings = settings_class(
        api_key=SecretStr(SYNTHETIC_KEY), model=MODEL, _env_file=None, max_attempts=1
    )
    async with module.AsyncClient(
        transport=module.MockTransport(handler), trust_env=False
    ) as client:
        adapter = (
            DeepSeekProvider(settings, client)
            if provider == "deepseek"
            else AnthropicProvider(settings, client)
        )
        yield adapter, generation, calls
