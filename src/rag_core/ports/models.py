"""No FastAPI/FlagEmbedding/Torch imports in model ports."""

from typing import Protocol

from rag_core.domain.models import InferenceRequest, InferenceResult


class ModelBackend(Protocol):
    @property
    def fingerprint(self) -> str: ...

    def infer(self, request: InferenceRequest) -> InferenceResult: ...


class ModelInference(Protocol):
    async def infer(self, request: InferenceRequest) -> InferenceResult: ...
