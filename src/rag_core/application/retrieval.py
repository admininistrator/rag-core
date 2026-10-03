"""One bounded query embedding/search/neighbor pass; no gold, history or global fallback."""

import asyncio
import time
from collections.abc import Mapping
from types import MappingProxyType

from pydantic import ValidationError

from rag_core.application.query import ScopedRetrievalContext
from rag_core.domain.models import InferenceError, InferenceRequest, InferenceResult
from rag_core.domain.retrieval import (
    RetrievalError,
    RetrievalPolicy,
    RetrievalResult,
    RetrievalTrace,
    ScoreKind,
)
from rag_core.domain.vectors import IndexProfile, VectorHit
from rag_core.ports.models import ModelInference


class RetrievalPipeline:
    def __init__(
        self,
        models: ModelInference,
        model_fingerprint: str,
        policies: Mapping[str, RetrievalPolicy] | None = None,
    ) -> None:
        IndexProfile(model_fingerprint)  # Same trusted revision as the ready index.
        profiles = (
            policies
            if policies is not None
            else {
                "hybrid-v1": RetrievalPolicy(),
                "dense-v1": RetrievalPolicy(branch="dense"),
            }
        )
        if not profiles:
            raise RetrievalError("invalid_retrieval_profiles")
        self._policies = MappingProxyType(
            {
                key: RetrievalPolicy.model_validate(value.model_dump())
                for key, value in profiles.items()
            }
        )
        self._models = models
        self._fingerprint = model_fingerprint

    async def retrieve(self, context: ScopedRetrievalContext) -> RetrievalResult:
        policy = self._policies.get(context.domain.config.retrieval_policy)
        if policy is None:
            raise RetrievalError("unknown_retrieval_policy")
        started = time.monotonic()
        try:
            async with asyncio.timeout(policy.timeout_seconds):
                await context.vectors.validate_scope()
                if not context.scope.pairs:
                    return self._result(context, policy, (), 0, 0, 0, "none", started)
                response = await self._models.infer(
                    InferenceRequest(
                        operation="embed",
                        priority="query",
                        texts=[context.question],
                        timeout_seconds=policy.timeout_seconds,
                    )
                )
                try:
                    result = InferenceResult.model_validate(response.model_dump())
                except ValidationError:
                    raise InferenceError("model_invalid_response") from None
                if result.fingerprint != self._fingerprint:
                    raise InferenceError("model_revision_mismatch")
                if len(result.embeddings) != 1 or result.scores:
                    raise InferenceError("model_invalid_response")
                await context.vectors.validate_scope()
                embedding = result.embeddings[0]
                hits = await context.vectors.search(
                    embedding,
                    self._fingerprint,
                    branch=policy.branch,
                    limit=policy.prefetch_limit,
                )
                # Deterministic tie ordering; dense/sparse/RRF magnitudes stay separate.
                ranked = sorted(
                    hits,
                    key=lambda h: (
                        -(h.score if h.score is not None else float("-inf")),
                        str(h.chunk.chunk_id),
                    ),
                )
                seeds = []
                seen = set()
                for hit in ranked:
                    if hit.chunk.chunk_id not in seen:
                        seeds.append(hit)
                        seen.add(hit.chunk.chunk_id)
                    if len(seeds) == policy.top_k:
                        break
                candidates = list(seeds)
                calls = 0
                for anchor in seeds[: policy.neighbor_anchors]:
                    if len(candidates) == policy.candidate_budget:
                        break
                    neighbors = await context.vectors.fetch_neighbors(
                        anchor.chunk.chunk_id,
                        radius=policy.neighbor_radius,
                    )
                    calls += 1
                    for hit in sorted(
                        neighbors, key=lambda h: (h.chunk.ordinal, str(h.chunk.chunk_id))
                    ):
                        if hit.chunk.chunk_id not in seen:
                            candidates.append(hit)
                            seen.add(hit.chunk.chunk_id)
                        if len(candidates) == policy.candidate_budget:
                            break
                await context.vectors.validate_scope()
                kind: ScoreKind = "sparse-dot" if policy.branch == "sparse" else "cosine"
                if policy.branch == "hybrid" and embedding.sparse_indices:
                    kind = "rrf"
                return self._result(
                    context,
                    policy,
                    tuple(candidates),
                    len(seeds),
                    calls,
                    len(candidates) - len(seeds),
                    kind,
                    started,
                )
        except TimeoutError:
            raise RetrievalError("retrieval_timeout") from None

    def _result(
        self,
        context: ScopedRetrievalContext,
        policy: RetrievalPolicy,
        candidates: tuple[VectorHit, ...],
        seeds: int,
        calls: int,
        neighbors: int,
        kind: ScoreKind,
        started: float,
    ) -> RetrievalResult:
        return RetrievalResult(
            candidates,
            RetrievalTrace(
                policy=policy,
                policy_fingerprint=policy.fingerprint,
                model_fingerprint=self._fingerprint,
                corpus_languages=context.corpus_languages,
                allowed_documents=len(context.scope.pairs),
                seed_count=seeds,
                neighbor_calls=calls,
                neighbor_count=neighbors,
                candidate_count=len(candidates),
                score_kind=kind,
                elapsed_ms=(time.monotonic() - started) * 1000,
            ),
        )
