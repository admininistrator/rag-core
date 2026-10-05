"""Scoped hydration, bounded real rerank and private source-mapped evidence output."""

import asyncio
import time
from collections.abc import Mapping
from types import MappingProxyType

from pydantic import ValidationError

from rag_core.application.query import ScopedRetrievalContext
from rag_core.domain.chunking import Chunk
from rag_core.domain.evidence import (
    EvidenceError,
    EvidencePassage,
    EvidencePolicy,
    EvidenceReason,
    EvidenceSelection,
    EvidenceTrace,
)
from rag_core.domain.metadata import ScopeError
from rag_core.domain.models import InferenceError, InferenceRequest, InferenceResult
from rag_core.domain.retrieval import RetrievalResult
from rag_core.domain.vectors import IndexProfile, VectorChunk
from rag_core.ports.evidence import EvidenceRepository
from rag_core.ports.models import ModelInference
from rag_core.ports.tokenizer import EmbeddingTokenizer


class EvidenceSelector:
    def __init__(
        self,
        repository: EvidenceRepository,
        models: ModelInference,
        model_fingerprint: str,
        tokenizer: EmbeddingTokenizer,
        policies: Mapping[str, EvidencePolicy] | None = None,
    ) -> None:
        IndexProfile(model_fingerprint)
        profiles = policies if policies is not None else {"bounded-v1": EvidencePolicy()}
        if not profiles:
            raise EvidenceError("invalid_evidence_profiles")
        self._policies = MappingProxyType(
            {k: EvidencePolicy.model_validate(v.model_dump()) for k, v in profiles.items()}
        )
        self._repository = repository
        self._models = models
        self._fingerprint = model_fingerprint
        self._tokenizer = tokenizer

    async def _hydrate(
        self, context: ScopedRetrievalContext, candidates: tuple[VectorChunk, ...]
    ) -> tuple[Chunk, ...]:
        await context.vectors.validate_scope()
        if any(
            c.pair not in context.scope.pairs
            or (context.corpus_languages is not None and c.language not in context.corpus_languages)
            for c in candidates
        ):
            raise ScopeError("session_scope_changed")
        actual = (
            await context.vectors.fetch(tuple(c.chunk_id for c in candidates)) if candidates else ()
        )
        if {h.chunk.chunk_id: h.chunk for h in actual} != {c.chunk_id: c for c in candidates}:
            raise ScopeError("session_scope_changed")
        chunks = await self._repository.hydrate(context.scope, candidates)
        if len(chunks) != len(candidates) or any(
            c.id != v.chunk_id
            or c.source.document_id != v.document_id
            or c.source.version_id != v.document_version_id
            or c.generation_id != v.index_generation
            for c, v in zip(chunks, candidates, strict=True)
        ):
            raise EvidenceError("evidence_mapping_mismatch")
        await context.vectors.validate_scope()
        return chunks

    async def select(
        self, context: ScopedRetrievalContext, retrieval: RetrievalResult
    ) -> EvidenceSelection:
        policy = self._policies.get(context.domain.config.evidence_policy)
        if policy is None:
            raise EvidenceError("unknown_evidence_policy")
        started = time.monotonic()
        try:
            async with asyncio.timeout(policy.timeout_seconds):
                if len(retrieval.candidates) > 20 or len(
                    {h.chunk.chunk_id for h in retrieval.candidates}
                ) != len(retrieval.candidates):
                    raise EvidenceError("invalid_evidence_candidates")
                # Validate ALL supplied IDs before limiting top candidates.
                metadata = tuple(h.chunk for h in retrieval.candidates)
                chunks = await self._hydrate(context, metadata)
                chunks = chunks[: policy.candidate_limit]
                scores: tuple[float, ...] = ()
                if chunks:
                    response = await self._models.infer(
                        InferenceRequest(
                            operation="rerank",
                            priority="query",
                            query=context.question,
                            texts=[c.text for c in chunks],
                            timeout_seconds=policy.timeout_seconds,
                        )
                    )
                    try:
                        result = InferenceResult.model_validate(response.model_dump())
                    except ValidationError:
                        raise InferenceError("model_invalid_response") from None
                    if result.fingerprint != self._fingerprint:
                        raise InferenceError("model_revision_mismatch")
                    if result.embeddings or len(result.scores) != len(chunks):
                        raise InferenceError("model_invalid_response")
                    scores = result.scores
                await context.vectors.validate_scope()
                relevant = sorted(
                    (
                        (c, s)
                        for c, s in zip(chunks, scores, strict=True)
                        if s >= policy.raw_score_floor
                    ),
                    key=lambda item: (-item[1], str(item[0].id)),
                )
                passages: list[EvidencePassage] = []
                tokens = skipped = 0
                for chunk, score in relevant:
                    if len(passages) == policy.passage_limit:
                        break
                    evidence_id = f"e{len(passages) + 1}"
                    count = await asyncio.to_thread(
                        self._tokenizer.count, f"[{evidence_id}]\n{chunk.text}"
                    )
                    # Whole passage only: never split a number/unit/header/source map.
                    if tokens + count > policy.context_tokens:
                        skipped += 1
                        continue
                    passages.append(EvidencePassage(evidence_id, chunk, score, count))
                    tokens += count
                reason: EvidenceReason
                reason = "relevant_evidence"
                if not relevant:
                    reason = "no_relevant_evidence"
                elif not passages:
                    reason = "context_budget_exhausted"
                elif len(passages) < policy.minimum_passages:
                    reason = "insufficient_coverage"
                await context.vectors.validate_scope()
                return EvidenceSelection(
                    context.scope,
                    "supported" if reason == "relevant_evidence" else "insufficient_evidence",
                    reason,
                    tuple(passages),
                    EvidenceTrace(
                        policy=policy,
                        policy_fingerprint=policy.fingerprint,
                        model_fingerprint=self._fingerprint,
                        tokenizer_fingerprint=self._tokenizer.fingerprint,
                        candidate_count=len(chunks),
                        relevant_count=len(relevant),
                        selected_count=len(passages),
                        context_tokens=tokens,
                        budget_skipped=skipped,
                        elapsed_ms=(time.monotonic() - started) * 1000,
                    ),
                )
        except TimeoutError:
            raise EvidenceError("evidence_timeout") from None

    async def context_for_generation(
        self, context: ScopedRetrievalContext, selection: EvidenceSelection
    ) -> tuple[str, ...]:
        """Last scope/content gate for T24. Contains evidence data only, never history.

        T24 must keep these strings separate from system policy and revalidate before
        provider I/O/final response. No provider is invoked by this task.
        """
        policy = self._policies.get(context.domain.config.evidence_policy)
        if policy is None or selection.trace.policy != policy or selection.scope != context.scope:
            raise ScopeError("session_scope_changed")
        try:
            async with asyncio.timeout(policy.timeout_seconds):
                if len(selection.passages) > policy.passage_limit:
                    raise EvidenceError("invalid_evidence_selection")
                metadata = await context.vectors.fetch(
                    tuple(p.chunk.id for p in selection.passages)
                )
                by_id = {h.chunk.chunk_id: h.chunk for h in metadata}
                if len(by_id) != len(selection.passages):
                    raise ScopeError("session_scope_changed")
                chunks = await self._hydrate(
                    context, tuple(by_id[p.chunk.id] for p in selection.passages)
                )
                if chunks != tuple(p.chunk for p in selection.passages):
                    raise EvidenceError("evidence_mapping_mismatch")
                texts = tuple(p.context_text for p in selection.passages)
                counts = await asyncio.to_thread(
                    lambda: tuple(self._tokenizer.count(t) for t in texts)
                )
                if sum(counts) > policy.context_tokens or any(
                    p.id != f"e{i}" or p.context_tokens != count
                    for i, (p, count) in enumerate(zip(selection.passages, counts, strict=True), 1)
                ):
                    raise EvidenceError("invalid_evidence_selection")
                await context.vectors.validate_scope()
                return texts
        except TimeoutError:
            raise EvidenceError("evidence_timeout") from None
