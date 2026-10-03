"""Trusted domain configuration and untrusted rewrite data; no provider/framework SDKs."""

from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import TYPE_CHECKING, Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from rag_core.contracts.v1 import HistoryMetadata, Language, QueryRequest, Text

if TYPE_CHECKING:
    from rag_core.application.query import ScopedRetrievalContext

DomainId = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_-]{0,63}$")]


class QueryPreparationError(Exception):
    """Safe technical/config error, never an insufficient-evidence result."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class FrozenModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid", frozen=True, hide_input_in_errors=True, validate_default=True
    )


class DomainQuery(QueryRequest):
    """Internal extension seam. Public v1 still advertises only the three shipped domains."""

    # Deliberately widens the INTERNAL type; public QueryRequest stays closed.
    domain: DomainId = "default"  # type: ignore[assignment]


class DomainConfig(FrozenModel):
    # Server-owned profile references, not executable prompts/code from a request.
    retrieval_policy: Text = "hybrid-v1"
    chunking_profile: Text = "structural-512-64-v1"
    prompt_template: Text = "grounded-v1"
    evidence_policy: Text = "bounded-v1"
    citation_renderer: Text = "source-locator-v1"
    evaluation_profile: Text = "session-v1"
    history_messages: Annotated[int, Field(strict=True, ge=1, le=20)] = 20
    history_tokens: Annotated[int, Field(strict=True, ge=1, le=8000)] = 8000
    rewrite_timeout_seconds: Annotated[
        float, Field(strict=True, gt=0, le=60, allow_inf_nan=False)
    ] = 30.0


class RewriteMessage(FrozenModel):
    role: Literal["user", "assistant"]
    content: Text


class RewriteInput(FrozenModel):
    """All fields are untrusted data; history supplies references, never factual evidence.

    Adapter system policy must remain separate. There are no structured tool, identity,
    scope, citation, evidence or storage parameters, or system/developer roles. Arbitrary
    strings within content retain no authority even if they name IDs, URLs or citations.
    """

    question: Annotated[Text, Field(max_length=4000)]
    history: tuple[RewriteMessage, ...] = ()


class RewriteResult(FrozenModel):
    """Question transformation only. Language is that of the ORIGINAL question."""

    standalone_question: Annotated[Text, Field(max_length=4000)]
    question_language: Language


class FrozenHistoryMetadata(HistoryMetadata):
    model_config = ConfigDict(extra="forbid", frozen=True)


DomainHook = Callable[["ScopedRetrievalContext"], Awaitable[RewriteResult]]


class DomainDefinition(FrozenModel):
    id: DomainId
    version: Annotated[int, Field(strict=True, ge=1)] = 1
    subset_policy: Literal["all", "required", "optional"]
    config: DomainConfig = DomainConfig()


@dataclass(frozen=True)
class RegisteredDomain:
    definition: DomainDefinition
    transform: DomainHook | None = None


class DomainRegistry:
    """Immutable DI registry. Hooks come only from trusted application code."""

    def __init__(self, domains: tuple[RegisteredDomain, ...]) -> None:
        # Recheck instances assembled via model_construct/model_copy by trusted code.
        checked = tuple(
            RegisteredDomain(
                DomainDefinition.model_validate(entry.definition.model_dump()), entry.transform
            )
            for entry in domains
        )
        items = {entry.definition.id: entry for entry in checked}
        if not domains or len(items) != len(domains):
            raise QueryPreparationError("invalid_domain_registry")
        self._domains: Mapping[str, RegisteredDomain] = MappingProxyType(items)

    def get(self, domain_id: str) -> RegisteredDomain:
        try:
            return self._domains[domain_id]
        except KeyError:
            raise QueryPreparationError("unknown_domain") from None


def builtin_domains() -> tuple[RegisteredDomain, ...]:
    return (
        RegisteredDomain(DomainDefinition(id="default", subset_policy="all")),
        RegisteredDomain(
            DomainDefinition(
                id="document",
                subset_policy="required",
                config=DomainConfig(prompt_template="document-structure-v1"),
            )
        ),
        RegisteredDomain(
            DomainDefinition(
                id="multilingual",
                subset_policy="optional",
                config=DomainConfig(
                    prompt_template="grounded-en-vi-v1", evaluation_profile="xquad-en-vi-v1"
                ),
            )
        ),
    )
