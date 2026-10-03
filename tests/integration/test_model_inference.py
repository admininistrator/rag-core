"""Real offline BGE weights, deliberately fails if cache/runtime is absent."""

import asyncio
import math
import os
import time
from pathlib import Path
from uuid import uuid4

import pytest

from rag_core.adapters.models.flag import FlagModels
from rag_core.domain.models import InferenceError, InferenceRequest
from rag_core.inference.scheduler import InferenceScheduler

pytestmark = [pytest.mark.integration, pytest.mark.slow]


@pytest.fixture(scope="module")
def backend():
    started = time.monotonic()
    model = FlagModels(Path(os.environ.get("MODEL_CACHE", ".local/models")),
                       device=os.environ.get("MODEL_DEVICE", "cpu"))
    print(f"REAL MODEL LOAD seconds={time.monotonic()-started:.3f} device={model.device} "
          f"runtime={model.runtime} fingerprint={model.fingerprint}")
    yield model
    resources = model.resources()
    assert resources["vram_peak_reserved_bytes"] <= 7*1024**3
    print(f"REAL MODEL RESOURCES {resources}")


def test_dense_sparse_english_vietnamese_and_cross_language(backend):
    texts = ["The capital of Vietnam is Hanoi.", "Thủ đô của Việt Nam là Hà Nội.",
             "The ocean contains many species of fish."]
    started = time.monotonic()
    result = backend.infer(InferenceRequest(operation="embed", texts=texts))
    assert len(result.embeddings) == 3
    for text, vector in zip(texts, result.embeddings, strict=True):
        assert len(vector.dense) == 1024
        assert math.isclose(sum(v*v for v in vector.dense), 1, abs_tol=0.005)
        assert vector.sparse_indices and len(vector.sparse_values) == len(vector.sparse_indices)
        assert all(math.isfinite(v) and v > 0 for v in vector.sparse_values)
        assert all(4 <= i < 250002 for i in vector.sparse_indices)
        actual_tokens = set(backend.embedder.tokenizer(text)["input_ids"])
        assert set(vector.sparse_indices) <= actual_tokens
    en, vi, distractor = [v.dense for v in result.embeddings]
    def dot(a, b):
        return sum(x*y for x, y in zip(a, b, strict=True))
    assert dot(en, vi) > dot(en, distractor)
    print(f"REAL EMBED elapsed={time.monotonic()-started:.3f}s "
          f"dense=1024 sparse_counts={[len(v.sparse_indices) for v in result.embeddings]} "
          f"cross_language={dot(en,vi):.4f} distractor={dot(en,distractor):.4f}")


@pytest.mark.parametrize("query", ["What is the capital of Vietnam?", "Thủ đô Việt Nam là gì?"])
def test_raw_rerank_relevant_beats_irrelevant(backend, query):
    started = time.monotonic()
    result = backend.infer(InferenceRequest(operation="rerank", query=query,
                          texts=["Hà Nội là thủ đô của Việt Nam.", "Cá sống ở đại dương."]))
    assert len(result.scores) == 2 and all(math.isfinite(v) for v in result.scores)
    assert result.scores[0] > result.scores[1]
    print(f"REAL RERANK elapsed={time.monotonic()-started:.3f}s raw_scores={result.scores}")


@pytest.mark.parametrize("operation", ["embed", "rerank"])
def test_actual_tokenizer_refuses_silent_truncation(backend, operation):
    with pytest.raises(InferenceError, match="model_token_limit"):
        backend.infer(InferenceRequest(operation=operation, texts=["hello "*1000],
                                      query="capital?" if operation == "rerank" else None))


@pytest.mark.parametrize("operation,limit", [("embed", 512), ("rerank", 768)])
def test_full_configured_token_budget_runs_without_oom_or_truncation(backend, operation, limit):
    tokenizer = backend.embedder.tokenizer if operation == "embed" else backend.reranker.tokenizer
    query = "capital?" if operation == "rerank" else None
    def count(text):
        return len(tokenizer(text)["input_ids"] if query is None
                   else tokenizer(query, text)["input_ids"])
    # Repetition changes subword boundaries; select by actual encoded length.
    base = "a "
    text = next(base*n for n in range(1, limit+1) if count(base*n) == limit)
    assert count(text) == limit
    started = time.monotonic()
    result = backend.infer(InferenceRequest(operation=operation, texts=[text], query=query))
    assert len(result.embeddings if operation == "embed" else result.scores) == 1
    with pytest.raises(InferenceError, match="model_token_limit"):
        backend.infer(InferenceRequest(operation=operation, texts=[text+base], query=query))
    print(f"REAL FULL BUDGET {operation} tokens={limit} elapsed={time.monotonic()-started:.3f}s PASS")


def test_real_cancel_timeout_recovery_does_not_release_native_slot(backend):
    async def run():
        scheduler = InferenceScheduler(backend)
        try:
            request = InferenceRequest(operation="embed", texts=["Hà Nội là thủ đô Việt Nam."]*32)
            request_id = uuid4()
            task = asyncio.create_task(scheduler.infer(request_id, request))
            while request_id not in scheduler.jobs:
                await asyncio.sleep(0)
            await asyncio.sleep(0.02)
            scheduler.cancel(request_id)
            with pytest.raises(InferenceError, match="model_cancelled"):
                await task
            with pytest.raises(InferenceError, match="model_timeout"):
                await scheduler.infer(uuid4(), request.model_copy(update={"timeout_seconds":0.001}))
            # Previous native work is reaped before next successful inference.
            result = await scheduler.infer(uuid4(), InferenceRequest(operation="embed",
                                          texts=["The capital of Vietnam is Hanoi."]))
            assert len(result.embeddings) == 1
            assert not scheduler.jobs
            print("REAL CANCEL/TIMEOUT/RECOVERY PASS; shared native executor slots=1")
        finally:
            await scheduler.close()
    asyncio.run(run())
