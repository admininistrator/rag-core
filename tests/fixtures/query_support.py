"""Explicit synthetic protocol collaborators; never evidence of real persistence/model success."""

from dataclasses import dataclass
from uuid import uuid4

from rag_core.adapters.tokenizer import BgeM3Tokenizer
from rag_core.application.query import QueryPreparation
from rag_core.auth import Principal
from rag_core.domain.metadata import ScopeError, ScopeSnapshot, VersionGeneration
from rag_core.domain.query import DomainRegistry, RewriteResult, builtin_domains


class TestRewriter:
    __test__ = False

    def __init__(self, *, question="What was Acme's revenue?", language="en"):
        self.result = dict(standalone_question=question, question_language=language)
        self.calls = []
        self.action = None

    async def rewrite(self, request):
        self.calls.append(request)
        if self.action is not None:
            await self.action()
        return RewriteResult.model_validate(self.result)


class SyntheticSessions:
    def __init__(self, snapshot):
        self.snapshot = snapshot
        self.resolve_calls = []
        self.stale = False

    async def resolve_scope(self, principal, session_id, document_ids=None):
        self.resolve_calls.append((principal, session_id, document_ids))
        if principal != self.snapshot.principal or session_id != self.snapshot.session_id:
            raise ScopeError("not_found")
        if document_ids is not None and set(document_ids) != {
            p.document_id for p in self.snapshot.pairs
        }:
            raise ScopeError("not_found")
        return self.snapshot

    async def validate_snapshot(self, snapshot):
        if snapshot != self.snapshot or self.stale:
            raise ScopeError("session_scope_changed")


@dataclass
class SyntheticEnvironment:
    prepare: QueryPreparation
    sessions: SyntheticSessions
    rewrite: TestRewriter
    scope: ScopeSnapshot


def synthetic_environment(*, registry=None, rewriter=None):
    owner = Principal("test-app", "test-user")
    scope = ScopeSnapshot(owner, uuid4(), 1, None, (VersionGeneration(uuid4(), uuid4(), uuid4()),))
    sessions = SyntheticSessions(scope)
    rewrite = rewriter or TestRewriter()
    # Contract tests don't invoke vector methods; security tests use actual PG/Qdrant.
    prepare = QueryPreparation(
        registry or DomainRegistry(builtin_domains()), sessions, None, BgeM3Tokenizer(), rewrite
    )
    return SyntheticEnvironment(prepare, sessions, rewrite, scope)
