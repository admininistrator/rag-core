"""Diagnostic observers must neither leak text nor prevent early provider cleanup."""

import json
from contextlib import aclosing

import pytest

from rag_core.domain.llm import GenerationRequest, LlmDelta
from tests.fixtures.live_diagnostics import ObservedLiveProvider

pytestmark = pytest.mark.unit


def request():
    return GenerationRequest(
        system="trusted policy",
        user_data=json.dumps(
            {"citation_allowlist": [{"id": "c1", "quote": "PRIVATE DOCUMENT QUOTE"}]}
        ),
    )


def test_diagnostic_redacts_unknown_field_names_answer_and_quotes(capsys):
    output = json.dumps(
        {
            "answer": "PRIVATE ANSWER [c1]",
            "citations": [{"id": "c1", "quote": "PRIVATE DOCUMENT QUOTE"}],
            "PRIVATE FIELD NAME": "PRIVATE VALUE",
        }
    )
    ObservedLiveProvider(None).describe(request(), [output], True, "json")
    logged = capsys.readouterr().out
    assert "PRIVATE" not in logged
    report = json.loads(logged)
    assert report["extra_fields_count"] == 1 and report["quote_mismatch_count"] == 0


@pytest.mark.asyncio
async def test_observer_early_close_preserves_underlying_cleanup(capsys):
    closed = []

    class Provider:
        async def stream(self, _request):
            try:
                yield LlmDelta(text='{"answer":"PRIVATE OUTPUT')
                yield LlmDelta(text='"}')
            finally:
                closed.append(True)

    async with aclosing(ObservedLiveProvider(Provider()).stream(request())) as stream:
        assert (await anext(stream)).text.endswith("PRIVATE OUTPUT")
    assert closed == [True]
    assert "PRIVATE" not in capsys.readouterr().out
