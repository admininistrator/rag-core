"""Async API/worker client, deliberately contains no model runtime imports."""

import asyncio
from contextlib import suppress
from uuid import uuid4

import httpx
from pydantic import ValidationError

from rag_core.domain.models import InferenceError, InferenceRequest, InferenceResult


class HttpModelInference:
    def __init__(self, client: httpx.AsyncClient, expected_fingerprint: str) -> None:
        self.client = client
        self.expected_fingerprint = expected_fingerprint

    async def infer(self, request: InferenceRequest) -> InferenceResult:
        path = f"/internal/infer/{uuid4()}"
        try:
            response = await self.client.post(path, json=request.model_dump(mode="json"),
                                              timeout=request.timeout_seconds + 5)
            if response.status_code != 200:
                payload = response.json()
                if not isinstance(payload, dict):
                    raise InferenceError("model_invalid_response")
                code = payload.get("code")
                if not isinstance(code, str) or code not in {"model_busy", "model_token_limit", "model_cancelled",
                                "model_timeout", "model_failed", "invalid_model_request"}:
                    code = "model_unavailable"
                raise InferenceError(code)
            result = InferenceResult.model_validate(response.json())
            if result.fingerprint != self.expected_fingerprint:
                raise InferenceError("model_revision_mismatch")
            count = len(result.embeddings) if request.operation == "embed" else len(result.scores)
            if count != len(request.texts):
                raise InferenceError("model_invalid_response")
            if ((request.operation == "embed" and result.scores)
                or (request.operation == "rerank" and result.embeddings)):
                raise InferenceError("model_invalid_response")
            return result
        except asyncio.CancelledError:
            # Cleanup has its own short bound; native slot remains owned until current batch ends.
            with suppress(httpx.HTTPError):
                await asyncio.shield(self.client.delete(path, timeout=2))
            raise
        except httpx.TimeoutException as exc:
            with suppress(httpx.HTTPError):
                await self.client.delete(path, timeout=2)
            raise InferenceError("model_timeout") from exc
        except httpx.HTTPError as exc:
            raise InferenceError("model_unavailable") from exc
        except (ValueError, ValidationError) as exc:
            raise InferenceError("model_invalid_response") from exc
