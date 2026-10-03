"""Framework-independent inference requests/results and operational bounds."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Priority = Literal["query", "index"]


class InferenceError(Exception):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class Embedding(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", allow_inf_nan=False)
    dense: tuple[float, ...] = Field(min_length=1024, max_length=1024)
    sparse_indices: tuple[int, ...]
    sparse_values: tuple[float, ...]

    @model_validator(mode="after")
    def validate_vector(self) -> "Embedding":
        if (len(self.sparse_indices) != len(self.sparse_values)
            or tuple(sorted(set(self.sparse_indices))) != self.sparse_indices
            or any(i < 4 or i >= 250002 for i in self.sparse_indices)
            or any(v <= 0 for v in self.sparse_values)
            or abs(sum(v * v for v in self.dense) - 1) > 0.01):
            raise ValueError("invalid_model_vector")
        return self


class InferenceRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)
    operation: Literal["embed", "rerank"]
    priority: Priority = "query"
    texts: list[str] = Field(min_length=1, max_length=32)
    query: str | None = Field(default=None, max_length=32768)
    timeout_seconds: float = Field(default=60, gt=0, le=120)

    @field_validator("texts")
    @classmethod
    def bounded_texts(cls, values: list[str]) -> list[str]:
        if any(not v.strip() or len(v) > 32768 for v in values):
            raise ValueError("invalid_model_text")
        return values

    @model_validator(mode="after")
    def valid_operation(self) -> "InferenceRequest":
        if self.operation == "rerank":
            if self.query is None or not self.query.strip() or len(self.texts) > 20:
                raise ValueError("invalid_rerank_request")
        elif self.query is not None:
            raise ValueError("unexpected_query")
        return self


class InferenceResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", allow_inf_nan=False)
    fingerprint: str
    embeddings: tuple[Embedding, ...] = ()
    scores: tuple[float, ...] = ()
