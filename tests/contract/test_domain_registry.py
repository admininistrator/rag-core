"""T20 domain/rewrite contracts with the actual pinned offline tokenizer."""

import asyncio
from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest
from pydantic import ValidationError

from rag_core.adapters.tokenizer import BgeM3Tokenizer
from rag_core.application.query import budget_history
from rag_core.contracts.v1 import HistoryMessage, QueryRequest
from rag_core.domain.metadata import ScopeError
from rag_core.domain.query import (
    DomainConfig,
    DomainDefinition,
    DomainQuery,
    DomainRegistry,
    QueryPreparationError,
    RegisteredDomain,
    RewriteInput,
    RewriteMessage,
    RewriteResult,
    builtin_domains,
)
from tests.fixtures.query_support import TestRewriter, synthetic_environment

pytestmark = pytest.mark.contract


def request(env, **kwargs):
    return DomainQuery(session_id=env.scope.session_id, question="How much was it?", **kwargs)


@pytest.mark.asyncio
async def test_unknown_domain_rejected_before_rewrite_or_scope():
    env = synthetic_environment()
    with pytest.raises(QueryPreparationError, match="unknown_domain"):
        await env.prepare.prepare(env.scope.principal, request(env, domain="bilingual"))
    assert not env.sessions.resolve_calls and not env.rewrite.calls


@pytest.mark.parametrize("domain", ["default", "document", "multilingual"])
def test_empty_subset_rejected(domain):
    with pytest.raises(ValidationError):
        QueryRequest(session_id=uuid4(), domain=domain, question="Why?", document_ids=[])


def test_default_and_document_subset_contracts():
    with pytest.raises(ValidationError):
        QueryRequest(session_id=uuid4(), question="Why?", document_ids=None)
    with pytest.raises(ValidationError):
        QueryRequest(session_id=uuid4(), domain="document", question="Why?")


@pytest.mark.parametrize(
    "config",
    [
        {"history_messages": 21},
        {"history_messages": 0},
        {"history_tokens": 8001},
        {"history_tokens": 0},
        {"history_tokens": True},
        {"rewrite_timeout_seconds": 0.0},
        {"rewrite_timeout_seconds": float("nan")},
        {"system_prompt": "injected"},
    ],
)
def test_trusted_config_bounds(config):
    with pytest.raises(ValidationError):
        DomainConfig(**config)


def test_registry_duplicate_and_invalid_ids():
    with pytest.raises(QueryPreparationError, match="invalid_domain_registry"):
        DomainRegistry(builtin_domains() + builtin_domains())
    with pytest.raises(ValidationError):
        DomainDefinition(id="../module.py", subset_policy="optional")
    assert [d.definition.id for d in builtin_domains()] == ["default", "document", "multilingual"]


@pytest.mark.asyncio
async def test_custom_domain_uses_same_dispatcher_and_scope():
    seen = []

    async def transform(context):
        seen.append(context)
        assert not hasattr(context, "history") and not hasattr(context, "evidence")
        return RewriteResult(standalone_question="Acme revenue in 2023?", question_language="vi")

    registry = DomainRegistry(
        (
            *builtin_domains(),
            RegisteredDomain(
                DomainDefinition(id="custom-test", subset_policy="required"), transform
            ),
        )
    )
    env = synthetic_environment(registry=registry)
    with pytest.raises(ScopeError, match="invalid_request"):
        await env.prepare.prepare(env.scope.principal, request(env, domain="custom-test"))
    context = await env.prepare.prepare(
        env.scope.principal,
        request(env, domain="custom-test", document_ids=[env.scope.pairs[0].document_id]),
    )
    assert context.scope == env.scope and context.question == "Acme revenue in 2023?"
    assert context.answer_language == "en"  # hook can't change resolved language
    assert len(seen) == 1
    with pytest.raises(FrozenInstanceError):
        context.question = "changed"
    with pytest.raises(ValidationError):
        context.history_metadata.truncated = True


@pytest.mark.asyncio
@pytest.mark.parametrize("domain", ["default", "document", "multilingual"])
@pytest.mark.parametrize(
    "language,override", [("en", None), ("vi", None), ("en", "vi"), ("vi", "en")]
)
async def test_followup_rewrite_schema_session_and_language_defaults(domain, language, override):
    env = synthetic_environment(rewriter=TestRewriter(language=language))
    subset = {"document_ids": [env.scope.pairs[0].document_id]} if domain == "document" else {}
    q = request(
        env,
        domain=domain,
        answer_language=override,
        corpus_languages=["en"],
        history=[
            HistoryMessage(role="user", content="I am reading Acme's 2023 report."),
            HistoryMessage(role="assistant", content="Which measure interests you?"),
        ],
        **subset,
    )
    context = await env.prepare.prepare(env.scope.principal, q)
    sent = env.rewrite.calls[0]
    assert set(sent.model_dump()) == {"question", "history"}
    assert len(sent.history) == 2 and sent.question == q.question
    assert context.scope.session_id == q.session_id
    assert context.answer_language == (override or language)
    assert context.corpus_languages == ("en",)  # never inferred from answer/question language
    assert context.question == "What was Acme's revenue?"
    assert not context.history_metadata.truncated and not context.warnings


def test_actual_tokenizer_message_and_token_budget_boundaries():
    tokenizer = BgeM3Tokenizer()
    messages = tuple(
        RewriteMessage(role="user", content="Doanh thu năm 2023 là bao nhiêu?") for _ in range(21)
    )
    kept, meta = budget_history(messages, tokenizer, DomainConfig())
    assert kept == messages[-20:] and meta.received_messages == 21 and meta.retained_messages == 20
    count = tokenizer.count(f"user\n{messages[0].content}")
    assert meta.received_tokens == 21 * count and meta.retained_tokens == 20 * count
    kept, meta = budget_history(messages[-2:], tokenizer, DomainConfig(history_tokens=count))
    assert len(kept) == 1 and meta.retained_tokens == count
    kept, meta = budget_history(messages[-2:], tokenizer, DomainConfig(history_tokens=count - 1))
    assert kept == () and meta.retained_tokens == 0 and meta.truncated
    kept, meta = budget_history((), tokenizer, DomainConfig())
    assert not kept and not meta.truncated and meta.received_tokens == 0


@pytest.mark.asyncio
async def test_actual_8000_token_budget_and_warning():
    env = synthetic_environment()
    context = await env.prepare.prepare(
        env.scope.principal,
        request(env, history=[HistoryMessage(role="user", content="doanh thu " * 5000)]),
    )
    assert context.history_metadata.received_tokens > 8000
    assert context.history_metadata.retained_messages == 0
    assert context.warnings[0].code == "history_truncated"
    assert env.rewrite.calls[0].history == ()


@pytest.mark.parametrize("field", ["session_id", "app_id", "system_prompt", "tools", "evidence"])
def test_rewrite_schema_cannot_add_authority_or_evidence(field):
    with pytest.raises(ValidationError):
        RewriteInput.model_validate({"question": "Why?", field: "injected"})
    with pytest.raises(ValidationError):
        RewriteResult.model_validate(
            {"standalone_question": "Why?", "question_language": "en", field: "injected"}
        )


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["schema", "provider", "timeout", "cancel"])
async def test_rewrite_failure_is_technical_and_cancellation_propagates(failure):
    rewriter = TestRewriter()
    registry = DomainRegistry(
        tuple(
            RegisteredDomain(
                d.definition.model_copy(
                    update={"config": DomainConfig(rewrite_timeout_seconds=0.01)}
                )
            )
            for d in builtin_domains()
        )
    )
    env = synthetic_environment(registry=registry, rewriter=rewriter)
    if failure == "schema":
        rewriter.result["evidence"] = "forged"

    async def action():
        if failure == "provider":
            raise RuntimeError("private-key-and-document-text")
        if failure == "cancel":
            raise asyncio.CancelledError()
        if failure == "timeout":
            await asyncio.sleep(1)

    rewriter.action = action
    expected = asyncio.CancelledError if failure == "cancel" else QueryPreparationError
    with pytest.raises(expected) as raised:
        await env.prepare.prepare(env.scope.principal, request(env))
    assert "private-key" not in str(raised.value)


@pytest.mark.asyncio
async def test_rewriter_constructed_result_is_revalidated():
    class InvalidRewriter:
        async def rewrite(self, request):
            return RewriteResult.model_construct(standalone_question="Why?", question_language="fr")

    env = synthetic_environment(rewriter=InvalidRewriter())
    with pytest.raises(QueryPreparationError, match="rewrite_provider_error"):
        await env.prepare.prepare(env.scope.principal, request(env))


@pytest.mark.asyncio
async def test_custom_transform_failure_is_redacted():
    async def custom(context):
        raise RuntimeError("private-document-and-key")

    registry = DomainRegistry(
        (RegisteredDomain(DomainDefinition(id="test-failure", subset_policy="all"), custom),)
    )
    env = synthetic_environment(registry=registry)
    with pytest.raises(QueryPreparationError, match="domain_transform_error") as caught:
        await env.prepare.prepare(env.scope.principal, request(env, domain="test-failure"))
    assert "private-document" not in str(caught.value)
