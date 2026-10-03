"""Scope is resolved outside hooks. History never enters the retrieval/evidence context."""

import asyncio
from dataclasses import dataclass, replace
from uuid import UUID

from rag_core.auth import Principal
from rag_core.contracts.v1 import HistoryWarning, Language, QueryRequest
from rag_core.domain.metadata import ScopeError, ScopeSnapshot
from rag_core.domain.models import Embedding
from rag_core.domain.query import (
    DomainConfig,
    DomainDefinition,
    DomainQuery,
    DomainRegistry,
    FrozenHistoryMetadata,
    QueryPreparationError,
    RewriteInput,
    RewriteMessage,
    RewriteResult,
)
from rag_core.domain.vectors import SearchBranch, VectorError, VectorHit
from rag_core.ports.metadata import SessionRepository
from rag_core.ports.rewrite import QueryRewriter
from rag_core.ports.tokenizer import EmbeddingTokenizer
from rag_core.ports.vectors import VectorRepository


def budget_history(
    messages: tuple[RewriteMessage, ...], tokenizer: EmbeddingTokenizer, config: DomainConfig
) -> tuple[tuple[RewriteMessage, ...], FrozenHistoryMetadata]:
    # Charge the actual tokenizer for role framing and special tokens per message.
    # These are a reproducible core budget, not provider billable-token estimates.
    counts = tuple(tokenizer.count(f"{m.role}\n{m.content}") for m in messages)
    retained: list[RewriteMessage] = []
    tokens = 0
    for message, count in zip(reversed(messages), reversed(counts), strict=True):
        if len(retained) == config.history_messages or tokens + count > config.history_tokens:
            break  # Keep a contiguous recent suffix; never cut a message into misleading text.
        retained.append(message)
        tokens += count
    return tuple(reversed(retained)), FrozenHistoryMetadata(
        received_messages=len(messages),
        retained_messages=len(retained),
        received_tokens=sum(counts),
        retained_tokens=tokens,
        truncated=len(retained) < len(messages),
    )


class ScopedVectors:
    """Read-only capability with bound snapshot/languages. No caller-supplied scope argument.

    Trusted Python hooks are not sandboxed; private attributes are not a Python security
    boundary. The production repository independently revalidates PG and prefilters Qdrant.
    """

    def __init__(
        self,
        repository: VectorRepository,
        sessions: SessionRepository,
        scope: ScopeSnapshot,
        languages: tuple[Language, ...] | None,
    ) -> None:
        self.__repository = repository
        self.__sessions = sessions
        self.__scope = scope
        self.__languages = languages

    async def _checked(self, hits: tuple[VectorHit, ...]) -> tuple[VectorHit, ...]:
        await self.__sessions.validate_snapshot(self.__scope)
        if any(
            hit.chunk.pair not in self.__scope.pairs
            or (self.__languages is not None and hit.chunk.language not in self.__languages)
            for hit in hits
        ):
            raise ScopeError("session_scope_changed")
        return hits

    async def search(
        self,
        query: Embedding,
        model_fingerprint: str,
        *,
        branch: SearchBranch = "hybrid",
        limit: int = 30,
    ) -> tuple[VectorHit, ...]:
        await self.__sessions.validate_snapshot(self.__scope)
        return await self._checked(
            await self.__repository.search(
                self.__scope,
                query,
                model_fingerprint,
                branch=branch,
                limit=limit,
                languages=self.__languages,
            )
        )

    async def fetch(self, chunk_ids: tuple[UUID, ...]) -> tuple[VectorHit, ...]:
        await self.__sessions.validate_snapshot(self.__scope)
        return await self._checked(
            await self.__repository.fetch(self.__scope, chunk_ids, languages=self.__languages)
        )

    async def fetch_neighbors(self, anchor_id: UUID, *, radius: int = 1) -> tuple[VectorHit, ...]:
        await self.__sessions.validate_snapshot(self.__scope)
        return await self._checked(
            await self.__repository.fetch_neighbors(
                self.__scope, anchor_id, radius=radius, languages=self.__languages
            )
        )


@dataclass(frozen=True)
class ScopedRetrievalContext:
    scope: ScopeSnapshot
    domain: DomainDefinition
    question: str
    answer_language: Language
    corpus_languages: tuple[Language, ...] | None
    history_metadata: FrozenHistoryMetadata
    vectors: ScopedVectors

    @property
    def warnings(self) -> tuple[HistoryWarning, ...]:
        if not self.history_metadata.truncated:
            return ()
        return (
            HistoryWarning(
                code="history_truncated",
                message="Conversation history was truncated to the configured processing budget.",
                history=self.history_metadata,
            ),
        )


class QueryPreparation:
    def __init__(
        self,
        registry: DomainRegistry,
        sessions: SessionRepository,
        vectors: VectorRepository,
        tokenizer: EmbeddingTokenizer,
        rewriter: QueryRewriter,
    ) -> None:
        self._registry = registry
        self._sessions = sessions
        self._vectors = vectors
        self._tokenizer = tokenizer
        self._rewriter = rewriter

    async def prepare(
        self, principal: Principal, request: QueryRequest | DomainQuery
    ) -> ScopedRetrievalContext:
        # Revalidate even objects constructed/copied without Pydantic validation, and
        # isolate mutable API lists from caller mutation while awaiting dependencies.
        query = DomainQuery.model_validate(request.model_dump(exclude_unset=True))
        registered = self._registry.get(query.domain)
        definition = registered.definition
        ids = tuple(query.document_ids) if query.document_ids is not None else None
        if (definition.subset_policy == "all" and ids is not None) or (
            definition.subset_policy == "required" and not ids
        ):
            raise ScopeError("invalid_request")
        scope = await self._sessions.resolve_scope(principal, query.session_id, ids)
        messages = tuple(RewriteMessage(role=m.role, content=m.content) for m in query.history)
        history, metadata = await asyncio.to_thread(
            budget_history, messages, self._tokenizer, definition.config
        )
        rewrite_input = RewriteInput(question=query.question, history=history)
        try:
            async with asyncio.timeout(definition.config.rewrite_timeout_seconds):
                result = await self._rewriter.rewrite(rewrite_input)
                rewritten = RewriteResult.model_validate(result.model_dump())
        except TimeoutError:
            raise QueryPreparationError("rewrite_timeout") from None
        except Exception:
            raise QueryPreparationError("rewrite_provider_error") from None
        await self._sessions.validate_snapshot(scope)
        languages = tuple(query.corpus_languages) if query.corpus_languages is not None else None
        context = ScopedRetrievalContext(
            scope=scope,
            domain=definition,
            question=rewritten.standalone_question,
            answer_language=query.answer_language or rewritten.question_language,
            corpus_languages=languages,
            history_metadata=metadata,
            vectors=ScopedVectors(self._vectors, self._sessions, scope, languages),
        )
        if registered.transform is not None:
            try:
                async with asyncio.timeout(definition.config.rewrite_timeout_seconds):
                    result = await registered.transform(context)
                    transformed = RewriteResult.model_validate(result.model_dump())
            except (ScopeError, VectorError, QueryPreparationError, asyncio.CancelledError):
                raise
            except Exception:
                raise QueryPreparationError("domain_transform_error") from None
            # A domain may transform the question; never scope/languages/config or evidence.
            context = replace(context, question=transformed.standalone_question)
        await self._sessions.validate_snapshot(scope)
        return context
