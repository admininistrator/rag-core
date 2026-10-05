"""Native Messages schema through the pinned Anthropic SDK, with SDK retries disabled."""

import json
from collections.abc import AsyncGenerator
from typing import Any

import anthropic
import httpx2

from rag_core.adapters.llm.common import (
    BaseProvider,
    bounded_body,
    object_value,
    sse_frames,
    status_error,
    stop_reason,
    text_value,
    token_count,
)
from rag_core.adapters.llm.config import AnthropicSettings
from rag_core.domain.llm import (
    GenerationRequest,
    GenerationResult,
    LlmCompleted,
    LlmDelta,
    LlmError,
    LlmEvent,
    LlmUsage,
)


class AnthropicProvider(BaseProvider):
    provider = "anthropic"

    def __init__(self, settings: AnthropicSettings, client: httpx2.AsyncClient) -> None:
        super().__init__(settings)
        if client.follow_redirects:
            raise LlmError("llm_invalid_config")
        # Explicit options override environmental SDK key/base URL and hidden retries.
        # Caller owns the HTTP pool and closes it after all adapter requests.
        self.client = anthropic.AsyncAnthropic(
            api_key=self.settings.api_key.get_secret_value(),
            base_url=self.settings.base_url,
            max_retries=0,
            timeout=self.settings.timeout_seconds,
            http_client=client,
        )

    def _error(self, exc: Exception) -> LlmError:
        if isinstance(exc, anthropic.APITimeoutError | httpx2.TimeoutException):
            return LlmError("llm_timeout", retryable=True)
        if isinstance(exc, anthropic.APIStatusError):
            return status_error(exc.status_code)
        if isinstance(exc, anthropic.APIConnectionError | httpx2.TransportError):
            return LlmError("llm_unavailable", retryable=True)
        return super()._error(exc)

    def _usage_payload(self, payload: dict[str, Any], model: str) -> LlmUsage:
        raw = payload.get("usage")
        if raw is None:
            return self._usage(model)
        raw = object_value(raw)
        inp = token_count(raw.get("input_tokens"))
        # Anthropic reports uncached input separately from cache reads/creation.
        cache = [
            token_count(raw.get(k))
            for k in ("cache_creation_input_tokens", "cache_read_input_tokens")
        ]
        if inp is not None:
            inp += sum(c or 0 for c in cache)
        return self._usage(model, inp, raw.get("output_tokens"))

    async def _generate(self, request: GenerationRequest) -> GenerationResult:
        async with self.client.messages.with_streaming_response.create(
            model=self.settings.model,
            max_tokens=request.max_output_tokens,
            system=request.system,
            messages=[{"role": "user", "content": request.user_data}],
            stream=False,
        ) as response:
            payload = object_value(json.loads(await bounded_body(response.iter_bytes())))
            if payload.get("type") != "message" or payload.get("role") != "assistant":
                raise LlmError("llm_invalid_response")
            stop_reason(payload.get("stop_reason"), anthropic=True)
            blocks = payload.get("content")
            if not isinstance(blocks, list) or not blocks:
                raise LlmError("llm_invalid_response")
            text = ""
            for item in blocks:
                block = object_value(item)
                if block.get("type") != "text":
                    raise LlmError("llm_invalid_response")
                text += text_value(block.get("text"))
            return GenerationResult(
                text=text, usage=self._usage_payload(payload, text_value(payload.get("model")))
            )

    async def _stream(self, request: GenerationRequest) -> AsyncGenerator[LlmEvent, None]:
        # SDK raw response API keeps native auth/request semantics while enforcing byte bounds.
        async with self.client.messages.with_streaming_response.create(
            model=self.settings.model,
            max_tokens=request.max_output_tokens,
            system=request.system,
            messages=[{"role": "user", "content": request.user_data}],
            stream=True,
        ) as response:
            if response.headers.get("content-type", "").split(";")[0] != "text/event-stream":
                raise LlmError("llm_invalid_response")
            model: str | None = None
            usage: LlmUsage | None = None
            block_index: int | None = None
            next_index = 0
            finished = False
            closing_message = False
            async for name, data in sse_frames(response.iter_bytes()):
                payload = object_value(json.loads(data))
                kind = payload.get("type")
                if kind != name:
                    raise LlmError("llm_invalid_response")
                if kind == "ping":
                    continue
                if kind == "error":
                    error = object_value(payload.get("error"))
                    code = error.get("type")
                    if code == "rate_limit_error":
                        raise status_error(429)
                    if code in {"overloaded_error", "api_error"}:
                        raise status_error(529)
                    raise LlmError("llm_request_rejected")
                if kind == "message_start":
                    if model is not None:
                        raise LlmError("llm_invalid_response")
                    message = object_value(payload.get("message"))
                    if message.get("role") != "assistant" or message.get("content") != []:
                        raise LlmError("llm_invalid_response")
                    model = text_value(message.get("model"))
                    usage = self._usage_payload(message, model)
                elif kind == "content_block_start":
                    if (
                        model is None
                        or closing_message
                        or block_index is not None
                        or payload.get("index") != next_index
                    ):
                        raise LlmError("llm_invalid_response")
                    block = object_value(payload.get("content_block"))
                    if block.get("type") != "text":
                        raise LlmError("llm_invalid_response")
                    block_index = next_index
                    text = text_value(block.get("text"))
                    if text:
                        yield LlmDelta(text=text)
                elif kind == "content_block_delta":
                    if block_index is None or payload.get("index") != block_index or finished:
                        raise LlmError("llm_invalid_response")
                    delta = object_value(payload.get("delta"))
                    if delta.get("type") != "text_delta":
                        raise LlmError("llm_invalid_response")
                    text = text_value(delta.get("text"))
                    if text:
                        yield LlmDelta(text=text)
                elif kind == "content_block_stop":
                    if block_index is None or payload.get("index") != block_index:
                        raise LlmError("llm_invalid_response")
                    block_index = None
                    next_index += 1
                elif kind == "message_delta":
                    if model is None or block_index is not None or next_index == 0:
                        raise LlmError("llm_invalid_response")
                    reason = object_value(payload.get("delta")).get("stop_reason")
                    if reason is not None:
                        stop_reason(reason, anthropic=True)
                        finished = True
                    final_usage = self._usage_payload(payload, model)
                    assert usage is not None
                    usage = self._usage(
                        model,
                        final_usage.input_tokens
                        if final_usage.input_tokens is not None
                        else usage.input_tokens,
                        final_usage.output_tokens
                        if final_usage.output_tokens is not None
                        else (usage.output_tokens if closing_message else None),
                    )
                    closing_message = True
                elif kind == "message_stop":
                    if not finished or usage is None:
                        raise LlmError("llm_stream_incomplete")
                    yield LlmCompleted(usage=usage)
                    return
                # Future named events are ignored per Anthropic's versioning contract.
            raise LlmError("llm_stream_incomplete")
