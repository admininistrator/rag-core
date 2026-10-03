"""Client protocol errors are operational errors, never trusted content or revision changes."""

import asyncio

import httpx
import pytest

from rag_core.adapters.models.http import HttpModelInference
from rag_core.domain.models import InferenceError, InferenceRequest

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("response,code", [
    (httpx.Response(200, json={"fingerprint":"changed", "scores":[1.0]}), "model_revision_mismatch"),
    (httpx.Response(200, json={"fingerprint":"pinned", "scores":[]}), "model_invalid_response"),
    (httpx.Response(200, content=b"PRIVATE upstream malformed"), "model_invalid_response"),
    (httpx.Response(503, json={"code":"PRIVATE"}), "model_unavailable"),
    (httpx.Response(429, json={"code":"model_busy"}), "model_busy"),
    (httpx.Response(503, json=["PRIVATE"]), "model_invalid_response"),
    (httpx.Response(503, json={"code":["PRIVATE"]}), "model_unavailable"),
])
def test_protocol_refuses_invalid_responses_without_echo(response, code):
    async def run():
        async with httpx.AsyncClient(base_url="http://inference", transport=httpx.MockTransport(
            lambda request: response,
        )) as client:
            with pytest.raises(InferenceError) as error:
                await HttpModelInference(client,"pinned").infer(InferenceRequest(
                    operation="rerank", query="q", texts=["PRIVATE"],
                ))
            assert str(error.value) == code
    asyncio.run(run())


def test_timeout_sends_cancel_and_has_safe_error():
    paths = []

    def transport(request):
        paths.append((request.method, request.url.path))
        if request.method == "POST":
            raise httpx.ReadTimeout("PRIVATE", request=request)
        return httpx.Response(204)

    async def run():
        async with httpx.AsyncClient(base_url="http://inference", transport=httpx.MockTransport(
            transport,
        )) as client:
            with pytest.raises(InferenceError, match="model_timeout"):
                await HttpModelInference(client,"pinned").infer(InferenceRequest(
                    operation="embed", texts=["PRIVATE"],
                ))
        assert paths[0][0] == "POST" and paths[1][0] == "DELETE" and paths[0][1] == paths[1][1]
    asyncio.run(run())
