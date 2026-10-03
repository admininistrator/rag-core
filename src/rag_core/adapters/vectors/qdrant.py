"""Qdrant queries always carry PG-derived exact pairs before candidate selection."""

import asyncio
import math
from collections.abc import Awaitable
from typing import TypeVar
from uuid import UUID

from pydantic import ValidationError
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as qm
from qdrant_client.http.exceptions import UnexpectedResponse

from rag_core.domain.metadata import ScopeSnapshot
from rag_core.domain.models import Embedding
from rag_core.domain.vectors import (
    GenerationScope,
    IndexProfile,
    SearchBranch,
    VectorChunk,
    VectorError,
    VectorHit,
    VectorWrite,
    point_id,
)
from rag_core.ports.metadata import SessionRepository
from rag_core.ports.vectors import GenerationAuthority

T = TypeVar("T")
PAYLOAD_INDEXES = {
    **dict.fromkeys(
        (
            "app_id",
            "owner_id",
            "document_id",
            "document_version_id",
            "index_generation",
            "chunk_id",
            "language",
            "unit_id",
        ),
        qm.PayloadSchemaType.KEYWORD,
    ),
    "ordinal": qm.PayloadSchemaType.INTEGER,
}


def _match(key: str, value: str) -> qm.FieldCondition:
    return qm.FieldCondition(key=key, match=qm.MatchValue(value=value))


class QdrantVectorRepository:
    """Internal DI adapter. Only operator setup accepts a collection, derived from profile."""

    def __init__(
        self,
        client: AsyncQdrantClient,
        profile: IndexProfile,
        sessions: SessionRepository,
        generations: GenerationAuthority,
    ) -> None:
        self._client = client
        self._profile = profile
        self._sessions = sessions
        self._generations = generations
        self._collection = profile.collection_name

    async def _call(self, operation: Awaitable[T]) -> T:
        try:
            async with asyncio.timeout(10):
                return await operation
        except (VectorError, asyncio.CancelledError):
            raise
        except Exception:
            raise VectorError("vector_dependency_unavailable") from None

    async def ensure_collection(self) -> None:
        if not await self._call(self._client.collection_exists(self._collection)):
            try:
                await self._client.create_collection(
                    self._collection,
                    vectors_config={
                        "dense": qm.VectorParams(size=1024, distance=qm.Distance.COSINE)
                    },
                    sparse_vectors_config={
                        "sparse": qm.SparseVectorParams(index=qm.SparseIndexParams(on_disk=False))
                    },
                    metadata={"index_fingerprint": self._profile.fingerprint},
                    timeout=10,
                )
            except UnexpectedResponse as exc:
                if exc.status_code != 409:  # Another setup caller may have created it.
                    raise VectorError("vector_dependency_unavailable") from None
            except Exception:
                raise VectorError("vector_dependency_unavailable") from None
        info = await self._call(self._client.get_collection(self._collection))
        vectors = info.config.params.vectors
        sparse = info.config.params.sparse_vectors
        if (
            not isinstance(vectors, dict)
            or set(vectors) != {"dense"}
            or vectors["dense"].size != 1024
            or vectors["dense"].distance != qm.Distance.COSINE
            or vectors["dense"].multivector_config is not None
            or vectors["dense"].quantization_config is not None
            or info.config.quantization_config is not None
            or sparse is None
            or set(sparse) != {"sparse"}
            or sparse["sparse"].modifier is not None
            or sparse["sparse"].index is None
            or sparse["sparse"].index.on_disk is not False
            or info.config.metadata != {"index_fingerprint": self._profile.fingerprint}
        ):
            raise VectorError("incompatible_vector_collection")
        for key, schema in PAYLOAD_INDEXES.items():
            if key in info.payload_schema:
                if info.payload_schema[key].data_type != schema:
                    raise VectorError("incompatible_payload_index")
            else:
                await self._call(
                    self._client.create_payload_index(
                        self._collection, key, field_schema=schema, wait=True
                    )
                )

    def _model(self, fingerprint: str) -> None:
        if fingerprint != self._profile.model_fingerprint:
            raise VectorError("index_model_mismatch")

    def _filter(
        self,
        scope: ScopeSnapshot,
        languages: tuple[str, ...] | None,
    ) -> qm.Filter:
        if not scope.pairs or len(scope.pairs) > 50 or len(set(scope.pairs)) != len(scope.pairs):
            raise VectorError("invalid_vector_scope")
        conditions: list[qm.FieldCondition | qm.Filter] = [
            _match("app_id", scope.principal.app_id),
            _match("owner_id", scope.principal.user_id),
            qm.Filter(
                should=[
                    qm.Filter(
                        must=[
                            _match("document_id", str(p.document_id)),
                            _match("document_version_id", str(p.version_id)),
                            _match("index_generation", str(p.generation_id)),
                        ]
                    )
                    for p in scope.pairs
                ]
            ),
        ]
        if languages is not None:
            if not languages or len(languages) > 3 or not set(languages) <= {"en", "vi", "und"}:
                raise VectorError("invalid_vector_languages")
            conditions.append(
                qm.FieldCondition(key="language", match=qm.MatchAny(any=list(languages)))
            )
        return qm.Filter(must=conditions)

    def _hits(
        self,
        scope: ScopeSnapshot,
        points: list[qm.ScoredPoint] | list[qm.Record],
        languages: tuple[str, ...] | None,
    ) -> tuple[VectorHit, ...]:
        result = []
        for point in points:
            payload = dict(point.payload or {})
            if (
                payload.pop("app_id", None) != scope.principal.app_id
                or payload.pop("owner_id", None) != scope.principal.user_id
            ):
                raise VectorError("vector_scope_violation")
            try:
                chunk = VectorChunk.model_validate(payload)
            except ValidationError:
                raise VectorError("invalid_vector_payload") from None
            if (
                chunk.pair not in scope.pairs
                or str(point.id) != str(point_id(scope.principal, chunk))
                or (languages is not None and chunk.language not in languages)
            ):
                raise VectorError("vector_scope_violation")
            score = point.score if isinstance(point, qm.ScoredPoint) else None
            if score is not None and not math.isfinite(score):
                raise VectorError("invalid_vector_score")
            result.append(VectorHit(chunk, score))
        return tuple(result)

    async def upsert(
        self,
        scope: GenerationScope,
        points: tuple[VectorWrite, ...],
        model_fingerprint: str,
    ) -> None:
        self._model(model_fingerprint)
        if (
            not points
            or len(points) > 64
            or len({p.chunk.chunk_id for p in points}) != len(points)
            or any(p.chunk.pair != scope.pair for p in points)
        ):
            raise VectorError("invalid_vector_write")
        async with self._generations.access(scope, self._profile.fingerprint, "write"):
            await self._call(
                self._client.upsert(
                    self._collection,
                    points=[
                        qm.PointStruct(
                            id=str(point_id(scope.principal, p.chunk)),
                            vector={
                                "dense": list(p.embedding.dense),
                                "sparse": qm.SparseVector(
                                    indices=list(p.embedding.sparse_indices),
                                    values=list(p.embedding.sparse_values),
                                ),
                            },
                            payload={
                                **p.chunk.model_dump(mode="json"),
                                "app_id": scope.principal.app_id,
                                "owner_id": scope.principal.user_id,
                            },
                        )
                        for p in points
                    ],
                    wait=True,
                )
            )

    async def search(
        self,
        scope: ScopeSnapshot,
        query: Embedding,
        model_fingerprint: str,
        *,
        branch: SearchBranch = "hybrid",
        limit: int = 30,
        languages: tuple[str, ...] | None = None,
    ) -> tuple[VectorHit, ...]:
        self._model(model_fingerprint)
        if branch not in {"dense", "sparse", "hybrid"} or not 1 <= limit <= 100:
            raise VectorError("invalid_vector_query")
        if not scope.pairs:
            return ()  # Never call Qdrant with query=None/filter=None for empty authority.
        query_filter = self._filter(scope, languages)
        await self._sessions.validate_snapshot(scope)
        sparse = qm.SparseVector(
            indices=list(query.sparse_indices), values=list(query.sparse_values)
        )
        if branch == "sparse" and not query.sparse_indices:
            return ()
        if branch == "hybrid" and query.sparse_indices:
            response = await self._call(
                self._client.query_points(
                    self._collection,
                    query=qm.FusionQuery(fusion=qm.Fusion.RRF),
                    prefetch=[
                        qm.Prefetch(
                            query=list(query.dense), using="dense", filter=query_filter, limit=limit
                        ),
                        qm.Prefetch(query=sparse, using="sparse", filter=query_filter, limit=limit),
                    ],
                    query_filter=query_filter,
                    limit=limit,
                    with_payload=True,
                    with_vectors=False,
                )
            )
        else:
            using = "sparse" if branch == "sparse" else "dense"
            response = await self._call(
                self._client.query_points(
                    self._collection,
                    query=sparse if using == "sparse" else list(query.dense),
                    using=using,
                    query_filter=query_filter,
                    limit=limit,
                    with_payload=True,
                    with_vectors=False,
                )
            )
        hits = self._hits(scope, response.points, languages)
        await self._sessions.validate_snapshot(scope)
        return hits

    async def fetch(
        self,
        scope: ScopeSnapshot,
        chunk_ids: tuple[UUID, ...],
        *,
        languages: tuple[str, ...] | None = None,
    ) -> tuple[VectorHit, ...]:
        if not scope.pairs or not chunk_ids:
            return ()
        if len(chunk_ids) > 100:
            raise VectorError("invalid_vector_fetch")
        query_filter = self._filter(scope, languages)
        query_filter.must = [
            *(query_filter.must or []),
            qm.FieldCondition(key="chunk_id", match=qm.MatchAny(any=[str(i) for i in chunk_ids])),
        ]
        await self._sessions.validate_snapshot(scope)
        points, _ = await self._call(
            self._client.scroll(
                self._collection,
                scroll_filter=query_filter,
                limit=100,
                with_payload=True,
                with_vectors=False,
            )
        )
        hits = self._hits(scope, points, languages)
        await self._sessions.validate_snapshot(scope)
        return hits

    async def fetch_neighbors(
        self,
        scope: ScopeSnapshot,
        anchor_id: UUID,
        *,
        radius: int = 1,
        languages: tuple[str, ...] | None = None,
    ) -> tuple[VectorHit, ...]:
        if not 0 <= radius <= 3:
            raise VectorError("invalid_neighbor_radius")
        anchors = await self.fetch(scope, (anchor_id,), languages=languages)
        if not anchors:
            return ()
        if len(anchors) != 1:
            raise VectorError("ambiguous_vector_anchor")
        anchor = anchors[0].chunk
        query_filter = self._filter(scope, languages)
        query_filter.must = [
            *(query_filter.must or []),
            _match("document_id", str(anchor.document_id)),
            _match("document_version_id", str(anchor.document_version_id)),
            _match("index_generation", str(anchor.index_generation)),
            _match("unit_id", anchor.unit_id),
            qm.FieldCondition(
                key="ordinal",
                range=qm.Range(gte=max(0, anchor.ordinal - radius), lte=anchor.ordinal + radius),
            ),
        ]
        await self._sessions.validate_snapshot(scope)
        points, _ = await self._call(
            self._client.scroll(
                self._collection,
                scroll_filter=query_filter,
                limit=7,
                with_payload=True,
                with_vectors=False,
            )
        )
        hits = self._hits(scope, points, languages)
        await self._sessions.validate_snapshot(scope)
        return tuple(sorted(hits, key=lambda hit: hit.chunk.ordinal))

    def _generation_filter(self, scope: GenerationScope) -> qm.Filter:
        return qm.Filter(
            must=[
                _match("app_id", scope.principal.app_id),
                _match("owner_id", scope.principal.user_id),
                _match("document_id", str(scope.pair.document_id)),
                _match("document_version_id", str(scope.pair.version_id)),
                _match("index_generation", str(scope.pair.generation_id)),
            ]
        )

    async def verify_generation(
        self, scope: GenerationScope, points: tuple[VectorWrite, ...]
    ) -> None:
        """Bounded reconciliation of acknowledged IDs, metadata and both actual vectors."""
        if not points or len(points) > 64 or any(p.chunk.pair != scope.pair for p in points):
            raise VectorError("invalid_vector_write")
        async with self._generations.access(scope, self._profile.fingerprint, "count"):
            rows = await self._call(self._client.retrieve(
                self._collection, ids=[str(point_id(scope.principal, p.chunk)) for p in points],
                with_payload=True, with_vectors=True,
            ))
            actual = {str(r.id): r for r in rows}
            for p in points:
                row = actual.get(str(point_id(scope.principal, p.chunk)))
                expected = {**p.chunk.model_dump(mode="json"), "app_id": scope.principal.app_id,
                            "owner_id": scope.principal.user_id}
                if row is None or row.payload != expected or not isinstance(row.vector, dict):
                    raise VectorError("vector_manifest_mismatch")
                dense = row.vector.get("dense")
                sparse = row.vector.get("sparse")
                if (not isinstance(dense, list) or len(dense) != 1024
                    or any(not isinstance(a, (int, float)) or not math.isfinite(a)
                           or abs(a-b) > 0.00001
                           for a, b in zip(dense, p.embedding.dense, strict=True))
                    or not isinstance(sparse, qm.SparseVector)
                    or sparse.indices != list(p.embedding.sparse_indices)
                    or len(sparse.values) != len(p.embedding.sparse_values)
                    or any(not math.isfinite(a) or abs(a-b) > 0.00001 for a, b in
                           zip(sparse.values, p.embedding.sparse_values, strict=True))):
                    raise VectorError("vector_manifest_mismatch")

    async def count_generation(self, scope: GenerationScope) -> int:
        async with self._generations.access(scope, self._profile.fingerprint, "count"):
            result = await self._call(
                self._client.count(
                    self._collection, count_filter=self._generation_filter(scope), exact=True
                )
            )
            return result.count

    async def cleanup_generation(self, scope: GenerationScope) -> None:
        async with self._generations.access(scope, self._profile.fingerprint, "cleanup"):
            await self._call(
                self._client.delete(
                    self._collection,
                    points_selector=qm.FilterSelector(filter=self._generation_filter(scope)),
                    wait=True,
                )
            )
