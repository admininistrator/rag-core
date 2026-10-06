"""Generation transport seam; citation/scope assembly belongs to its caller."""

from collections.abc import AsyncGenerator
from typing import Protocol

from rag_core.domain.llm import GenerationRequest, GenerationResult, LlmEvent


class LlmProvider(Protocol):
    async def generate(self, request: GenerationRequest) -> GenerationResult: ...

    def stream(self, request: GenerationRequest) -> AsyncGenerator[LlmEvent, None]:
        """Consumer must close the iterator on early exit (contextlib.aclosing)."""
        ...
