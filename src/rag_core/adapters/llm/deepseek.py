"""DeepSeek Chat Completions HTTPX adapter; reasoning/tool text is never answer text."""

import json
from collections.abc import AsyncGenerator
from typing import Any

import httpx

from rag_core.adapters.llm.common import (
    BaseProvider,
    bounded_body,
    object_value,
    sse_frames,
    status_error,
    stop_reason,
    text_value,
)
from rag_core.adapters.llm.config import DeepSeekSettings
from rag_core.domain.llm import (
    GenerationRequest,
    GenerationResult,
    LlmCompleted,
    LlmDelta,
    LlmError,
    LlmEvent,
    LlmUsage,
)


class DeepSeekProvider(BaseProvider):
    provider = "deepseek"

    def __init__(self, settings: DeepSeekSettings, client: httpx.AsyncClient) -> None:
        super().__init__(settings)
        # Caller owns pooled client lifetime; redirects cannot forward the provider key.
        self.client = client

    def _payload(self, request: GenerationRequest, stream: bool) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.settings.model,
            "messages": [
                {"role": "system", "content": request.system},
                {"role": "user", "content": request.user_data},
            ],
            "max_tokens": request.max_output_tokens,
            "stream": stream,
            "thinking": {"type": "disabled"},
        }
        if request.json_output:
            payload["response_format"] = {"type": "json_object"}
        if stream:
            payload["stream_options"] = {"include_usage": True}
        return payload

    def _error(self, exc: Exception) -> LlmError:
        if isinstance(exc, httpx.TimeoutException):
            return LlmError("llm_timeout", retryable=True)
        if isinstance(exc, httpx.TransportError):
            return LlmError("llm_unavailable", retryable=True)
        return super()._error(exc)

    def _usage_payload(self, payload: dict[str, Any], model: str) -> LlmUsage:
        usage = payload.get("usage")
        if usage is None:
            return self._usage(model)
        usage = object_value(usage)
        return self._usage(model, usage.get("prompt_tokens"), usage.get("completion_tokens"))

    def _choice(self, payload: dict[str, Any]) -> dict[str, Any]:
        choices = payload.get("choices")
        if not isinstance(choices, list) or len(choices) != 1:
            raise LlmError("llm_invalid_response")
        choice = object_value(choices[0])
        if choice.get("index") != 0:
            raise LlmError("llm_invalid_response")
        return choice

    async def _generate(self, request: GenerationRequest) -> GenerationResult:
        async with self.client.stream(
            "POST",
            self.settings.base_url + "/chat/completions",
            headers={"Authorization": "Bearer " + self.settings.api_key.get_secret_value()},
            json=self._payload(request, False),
            timeout=self.settings.timeout_seconds,
            follow_redirects=False,
        ) as response:
            if response.status_code != 200:
                raise status_error(response.status_code)
            payload = object_value(json.loads(await bounded_body(response.aiter_bytes())))
            choice = self._choice(payload)
            stop_reason(choice.get("finish_reason"))
            message = object_value(choice.get("message"))
            if message.get("role") != "assistant" or message.get("tool_calls"):
                raise LlmError("llm_invalid_response")
            return GenerationResult(
                text=text_value(message.get("content")),
                usage=self._usage_payload(payload, text_value(payload.get("model"))),
            )

    async def _stream(self, request: GenerationRequest) -> AsyncGenerator[LlmEvent, None]:
        async with self.client.stream(
            "POST",
            self.settings.base_url + "/chat/completions",
            headers={"Authorization": "Bearer " + self.settings.api_key.get_secret_value()},
            json=self._payload(request, True),
            timeout=self.settings.timeout_seconds,
            follow_redirects=False,
        ) as response:
            if response.status_code != 200:
                raise status_error(response.status_code)
            if response.headers.get("content-type", "").split(";")[0] != "text/event-stream":
                raise LlmError("llm_invalid_response")
            finished = False
            model: str | None = None
            usage: LlmUsage | None = None
            async for _, data in sse_frames(response.aiter_bytes()):
                if data == "[DONE]":
                    if not finished or model is None:
                        raise LlmError("llm_stream_incomplete")
                    yield LlmCompleted(usage=usage or self._usage(model))
                    return
                payload = object_value(json.loads(data))
                current_model = text_value(payload.get("model"))
                if model is not None and current_model != model:
                    raise LlmError("llm_invalid_response")
                model = current_model
                if payload.get("usage") is not None:
                    usage = self._usage_payload(payload, model)
                if payload.get("choices") == [] and payload.get("usage") is not None and finished:
                    continue  # Legacy usage-only chunk.
                choice = self._choice(payload)
                delta = object_value(choice.get("delta"))
                if (
                    finished
                    or delta.get("tool_calls")
                    or delta.get("role", "assistant") != "assistant"
                ):
                    raise LlmError("llm_invalid_response")
                content = delta.get("content")
                if content is not None:
                    content = text_value(content)
                    if content:
                        yield LlmDelta(text=content)
                if choice.get("finish_reason") is not None:
                    stop_reason(choice["finish_reason"])
                    finished = True
            raise LlmError("llm_stream_incomplete")
