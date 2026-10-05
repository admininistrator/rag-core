"""Private provider-neutral generation contracts; no SDK or transport dependencies."""

from typing import Annotated, Literal

from pydantic import Field

from rag_core.domain.query import FrozenModel

Provider = Literal["deepseek", "anthropic"]
TokenCount = Annotated[int, Field(strict=True, ge=0)]


class LlmError(Exception):
    """Code-only technical failure, never a document answerability result."""

    def __init__(self, code: str, *, retryable: bool = False) -> None:
        self.code = code
        self.retryable = retryable
        super().__init__(code)


class GenerationRequest(FrozenModel):
    # Internal trusted caller supplies policy; never deserialize this from public body.
    system: Annotated[str, Field(strict=True, min_length=1, max_length=16000, repr=False)]
    user_data: Annotated[str, Field(strict=True, min_length=1, max_length=128000, repr=False)]
    max_output_tokens: Annotated[int, Field(strict=True, ge=1, le=1024)] = 1024
    json_output: Annotated[bool, Field(strict=True)] = False


class LlmUsage(FrozenModel):
    provider: Provider
    model: Annotated[str, Field(strict=True, min_length=1, max_length=200)]
    input_tokens: TokenCount | None = None
    output_tokens: TokenCount | None = None


class GenerationResult(FrozenModel):
    text: Annotated[str, Field(strict=True, min_length=1, repr=False)]
    usage: LlmUsage


class LlmDelta(FrozenModel):
    kind: Literal["delta"] = "delta"
    text: Annotated[str, Field(strict=True, min_length=1, repr=False)]


class LlmCompleted(FrozenModel):
    kind: Literal["completed"] = "completed"
    usage: LlmUsage


LlmEvent = LlmDelta | LlmCompleted
