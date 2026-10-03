"""Single-device FlagEmbedding adapter. Instantiate once in inference process only."""

import hashlib
import json
import os
from importlib.metadata import version
from pathlib import Path
from typing import Any

from rag_core.adapters.models.artifacts import DEFAULT_PINS, verify_cache
from rag_core.domain.models import Embedding, InferenceError, InferenceRequest, InferenceResult


class FlagModels:
    def __init__(self, cache: Path, *, device: str = "cpu", pins: Path = DEFAULT_PINS) -> None:
        if device not in {"cpu", "cuda:0"}:
            raise ValueError("unsupported_model_device")
        self.spec = verify_cache(cache, pins)
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        import torch
        from FlagEmbedding import BGEM3FlagModel, FlagReranker  # type: ignore[import-untyped]

        if device != "cpu" and not torch.cuda.is_available():
            raise ValueError("gpu_not_available")
        torch.set_num_threads(2)
        self.device = device
        self.batch_size = 2
        self.embedder: Any = BGEM3FlagModel(
            str(cache / "embedding"), devices=[device], use_fp16=device != "cpu",
            normalize_embeddings=True, batch_size=2, passage_max_length=512,
            query_max_length=512, return_dense=True, return_sparse=True,
            return_colbert_vecs=False, trust_remote_code=False,
        )
        self.reranker: Any = FlagReranker(
            str(cache / "reranker"), devices=[device], use_fp16=device != "cpu",
            batch_size=2, max_length=768, query_max_length=768, normalize=False,
            trust_remote_code=False,
        )
        self.runtime = {p: version(p) for p in (
            "FlagEmbedding", "torch", "transformers", "tokenizers", "sentence-transformers", "peft"
        )}
        self._fingerprint = hashlib.sha256(json.dumps({
            "artifacts": self.spec, "runtime": self.runtime, "device": device,
            "precision": "fp32" if device == "cpu" else "fp16", "policy": "bge-v1-512-768",
            "normalized_dense": True, "raw_rerank": True,
        }, sort_keys=True).encode()).hexdigest()

    @property
    def fingerprint(self) -> str:
        return self._fingerprint

    def resources(self) -> dict[str, int]:
        import torch
        if self.device == "cpu":
            return {"vram_allocated_bytes": 0, "vram_peak_reserved_bytes": 0}
        return {"vram_allocated_bytes": torch.cuda.memory_allocated(0),
                "vram_peak_reserved_bytes": torch.cuda.max_memory_reserved(0)}

    def infer(self, request: InferenceRequest) -> InferenceResult:
        # Check actual tokenizer lengths before any inference; never silently truncate.
        tokenizer = self.embedder.tokenizer if request.operation == "embed" else self.reranker.tokenizer
        lengths = [len(tokenizer(t, truncation=False)["input_ids"])
                   if request.operation == "embed"
                   else len(tokenizer(request.query, t, truncation=False)["input_ids"])
                   for t in request.texts]
        limit = 512 if request.operation == "embed" else 768
        if any(n > limit for n in lengths) or sum(lengths) > 16384:
            raise InferenceError("model_token_limit")
        if request.operation == "embed":
            output = self.embedder.encode(
                request.texts, batch_size=self.batch_size, max_length=512,
                return_dense=True, return_sparse=True, return_colbert_vecs=False,
            )
            embeddings = []
            for dense, sparse in zip(output["dense_vecs"], output["lexical_weights"], strict=True):
                ordered = sorted((int(i), float(v)) for i, v in sparse.items())
                embeddings.append(Embedding(dense=tuple(float(v) for v in dense),
                                            sparse_indices=tuple(i for i, _ in ordered),
                                            sparse_values=tuple(v for _, v in ordered)))
            return InferenceResult(fingerprint=self.fingerprint, embeddings=tuple(embeddings))
        scores = self.reranker.compute_score(
            [[request.query, t] for t in request.texts], batch_size=self.batch_size,
            max_length=768, query_max_length=768, normalize=False,
        )
        return InferenceResult(fingerprint=self.fingerprint, scores=tuple(float(s) for s in scores))
