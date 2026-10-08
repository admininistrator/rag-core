"""Redacted observation of actual provider output; never a fake response or fallback."""

import json
import re
from contextlib import aclosing

from rag_core.domain.llm import LlmCompleted, LlmDelta, LlmError
from rag_core.domain.streaming import ProvisionalAnswer


class ObservedLiveProvider:
    def __init__(self, provider):
        self.provider = provider

    async def rewrite(self, request):
        try:
            result = await self.provider.rewrite(request)
        except LlmError as exc:
            print(json.dumps({"live_diagnostic": True, "mode": "rewrite", "error_code": exc.code}))
            raise
        print(json.dumps({"live_diagnostic": True, "mode": "rewrite", "status": "PASS"}))
        return result

    def describe(self, request, parts, completed, mode):
        allowed = {c["id"]: c["quote"] for c in json.loads(request.user_data)["citation_allowlist"]}
        raw = "".join(parts)
        report = {
            "live_diagnostic": True,
            "mode": mode,
            "completed": completed,
            "output_chars": len(raw),
            "output": "[REDACTED]",
        }
        try:
            value = json.loads(raw)
            declarations = value["citations"]
            answer = value["answer"]
            report.update(
                json_valid=True,
                required_fields_present={"answer", "citations"} <= value.keys(),
                extra_fields_count=len(value.keys() - {"answer", "citations"}),
                declaration_count=len(declarations),
                marker_count=len(re.findall(r"\[([ce][^\]]*)\]", answer, re.I)),
                unknown_ids=sum(c["id"] not in allowed for c in declarations),
                quote_mismatch_count=sum(c["quote"] != allowed.get(c["id"]) for c in declarations),
                marker_declaration_match=set(re.findall(r"\[([ce][^\]]*)\]", answer, re.I))
                == {c["id"] for c in declarations},
            )
            decoder = ProvisionalAnswer(set(allowed), 4096)
            for part in parts:
                decoder.feed(part)
            decoder.finish()
            report.update(decoder_answer_matches=decoder.text == answer, deferred=decoder.deferred)
        except Exception as exc:
            # Exception type only: JSON/parser messages can contain document/model data.
            report["diagnostic_error_type"] = type(exc).__name__
        print(json.dumps(report))

    async def generate(self, request):
        try:
            result = await self.provider.generate(request)
        except LlmError as exc:
            print(json.dumps({"live_diagnostic": True, "mode": "json", "error_code": exc.code}))
            raise
        self.describe(request, [result.text], True, "json")
        return result

    async def stream(self, request):
        parts, completed = [], False
        try:
            async with aclosing(self.provider.stream(request)) as upstream:
                async for event in upstream:
                    if isinstance(event, LlmDelta):
                        parts.append(event.text)
                    elif isinstance(event, LlmCompleted):
                        completed = True
                    yield event
        finally:
            self.describe(request, parts, completed, "sse")
