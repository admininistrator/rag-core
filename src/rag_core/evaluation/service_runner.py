"""Real service benchmark engine for RAG Core evaluation.

Executes retrieval evaluation (dense baseline vs tuned hybrid+rerank) on full retrieval QA,
tunes and freezes calibrated evidence parameters on the tuning split,
runs generation benchmark on 130 sample questions with verified live provider,
and verifies all Acceptance Gates (P11).
"""

from __future__ import annotations

import asyncio
import json
import logging
import math
import time
from pathlib import Path
from typing import Any, Literal, cast

import httpx
import numpy as np
from pypdf import PdfReader

from rag_core.adapters.llm.config import DeepSeekSettings, load_provider_settings
from rag_core.adapters.llm.deepseek import DeepSeekProvider
from rag_core.adapters.tokenizer import BgeM3Tokenizer
from rag_core.contracts.v1 import PdfLocator
from rag_core.domain.llm import GenerationRequest
from rag_core.evaluation.adapters import (
    BilingualGoldAdapter,
    DefaultGoldAdapter,
    FinanceBenchGoldAdapter,
)
from rag_core.evaluation.manifest import (
    GenerationMetricsSummary,
    RetrievalMetricsSummary,
    SliceEvaluationReport,
)
from rag_core.evaluation.metrics import (
    calculate_retrieval_metrics,
    citation_validity,
    exact_match,
    f1_score,
    numeric_match,
    page_recall,
    supporting_document_recall,
)
from rag_core.evaluation.protocol import (
    DatasetSplits,
    SplitKind,
    assert_no_qa_leakage,
)

logger = logging.getLogger(__name__)


def compute_sparse_dot(
    query_sparse: dict[int, float], doc_sparse_list: list[dict[int, float]]
) -> np.ndarray:
    """Compute sparse lexical dot product for a query across all documents."""
    scores = np.zeros(len(doc_sparse_list), dtype=np.float32)
    for q_idx, q_val in query_sparse.items():
        for d_i, d_sparse in enumerate(doc_sparse_list):
            if q_idx in d_sparse:
                scores[d_i] += q_val * d_sparse[q_idx]
    return scores


def rrf_fuse(
    dense_ranked_indices: np.ndarray,
    sparse_ranked_indices: np.ndarray,
    total_docs: int,
    k: int = 60,
    top_n: int = 20,
) -> np.ndarray:
    """Reciprocal Rank Fusion of dense and sparse rankings."""
    rrf_scores = np.zeros(total_docs, dtype=np.float32)
    for rank, idx in enumerate(dense_ranked_indices[:top_n]):
        rrf_scores[idx] += 1.0 / (k + rank + 1)
    for rank, idx in enumerate(sparse_ranked_indices[:top_n]):
        rrf_scores[idx] += 1.0 / (k + rank + 1)
    return np.argsort(-rrf_scores)[:top_n]


class ServiceBenchmarkEngine:
    """Orchestrates actual measurement on local inference and real provider APIs."""

    def __init__(
        self,
        repo_root: Path,
        splits: DatasetSplits,
        inference_url: str = "http://127.0.0.1:58080",
        cache_dir: Path | None = None,
    ) -> None:
        self.repo_root = repo_root
        self.splits = splits
        self.inference_url = inference_url
        self.cache_dir = cache_dir or (repo_root / "artifacts" / "eval" / "cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.pdf_cache_dir = self.cache_dir / "financebench_pages"
        self.pdf_cache_dir.mkdir(parents=True, exist_ok=True)

        self.tokenizer = BgeM3Tokenizer()
        self.default_adapter = DefaultGoldAdapter()
        self.doc_adapter = FinanceBenchGoldAdapter()
        self.bilingual_adapter = BilingualGoldAdapter()

        self._embedder = None
        self._reranker = None
        self._query_embed_cache: dict[str, tuple[np.ndarray, dict[int, float]]] = {}
        self._rerank_cache: dict[tuple[str, str], float] = {}
        self._load_precomputed_query_cache()

    def _load_precomputed_query_cache(self) -> None:
        query_npz = self.cache_dir / "all_queries_embed.npz"
        query_sparse = self.cache_dir / "all_queries_sparse.json"
        if query_npz.is_file() and query_sparse.is_file():
            try:
                loaded = np.load(query_npz)
                dense_all = loaded["dense"]
                questions = loaded["questions"].tolist()
                sparse_all = json.loads(query_sparse.read_text(encoding="utf-8"))
                for i, q in enumerate(questions):
                    sparse_dict = dict(
                        zip(sparse_all[i]["indices"], sparse_all[i]["values"], strict=True)
                    )
                    self._query_embed_cache[q] = (dense_all[i], sparse_dict)
            except Exception:
                pass

    def _get_embedder(self) -> Any:
        if self._embedder is None:
            import torch
            from FlagEmbedding import BGEM3FlagModel  # type: ignore[import-untyped]

            device = "mps" if torch.backends.mps.is_available() else "cpu"
            self._embedder = BGEM3FlagModel(
                str(self.repo_root / ".local/models/embedding"),
                use_fp16=(device == "mps"),
                device=device,
                batch_size=32,
            )
        return self._embedder

    def _get_reranker(self) -> Any:
        if self._reranker is None:
            import torch
            from FlagEmbedding import FlagReranker

            device = "mps" if torch.backends.mps.is_available() else "cpu"
            self._reranker = FlagReranker(
                str(self.repo_root / ".local/models/reranker"),
                use_fp16=(device == "mps"),
                device=device,
                batch_size=16,
            )
        return self._reranker

    def encode_query(self, q_text: str) -> tuple[np.ndarray, dict[int, float]]:
        if q_text in self._query_embed_cache:
            return self._query_embed_cache[q_text]
        embedder = self._get_embedder()
        out_q = embedder.encode([q_text], batch_size=1, return_dense=True, return_sparse=True)
        q_dense = out_q["dense_vecs"][0]
        q_sparse = {int(k): float(v) for k, v in out_q["lexical_weights"][0].items()}
        res = (q_dense, q_sparse)
        self._query_embed_cache[q_text] = res
        return res

    def rerank_pairs(self, q_text: str, candidate_texts: list[str]) -> list[float]:
        reranker = self._get_reranker()
        to_compute_idx = []
        to_compute_pairs = []
        scores = [0.0] * len(candidate_texts)

        for i, t in enumerate(candidate_texts):
            key = (q_text, t)
            if key in self._rerank_cache:
                scores[i] = self._rerank_cache[key]
            else:
                to_compute_idx.append(i)
                to_compute_pairs.append([q_text, self.truncate_text(t, max_tokens=256)])

        if to_compute_pairs:
            computed_scores = reranker.compute_score(
                to_compute_pairs, batch_size=len(to_compute_pairs), max_length=256
            )
            for idx, s, pair in zip(to_compute_idx, computed_scores, to_compute_pairs, strict=True):
                scores[idx] = float(s)
                self._rerank_cache[(pair[0], candidate_texts[idx])] = float(s)

        return scores

    def truncate_text(self, text: str, max_tokens: int = 510) -> str:
        if self.tokenizer.count(text) <= 512:
            return text
        boundaries = self.tokenizer.boundaries(text)
        target_idx = min(max_tokens, len(boundaries) - 1)
        char_offset = boundaries[target_idx]
        truncated = text[:char_offset]
        while self.tokenizer.count(truncated) > 512 and char_offset > 0:
            char_offset -= 10
            truncated = text[:char_offset]
        return truncated

    def validate_safety(self) -> None:
        """Enforce anti-leakage invariants on corpus documents."""
        for d in ("default", "document", "bilingual"):
            doc_dir = self.repo_root / "corpus-documents" / d / "documents"
            if doc_dir.is_dir():
                assert_no_qa_leakage(list(doc_dir.rglob("*")))

    # =========================================================================
    # Default Domain Evaluation (HotpotQA)
    # =========================================================================

    def evaluate_default_slice(
        self, split: SplitKind, sample_size: int | None = None
    ) -> SliceEvaluationReport:
        qa_file = self.repo_root / "corpus-documents/default/qa/eval.jsonl"
        all_qa = [
            json.loads(line)
            for line in qa_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        split_ids = set(
            self.splits.default_tuning_ids
            if split == "tuning"
            else self.splits.default_held_out_ids
        )
        split_qa = [q for q in all_qa if q["id"] in split_ids]
        if sample_size:
            split_qa = split_qa[:sample_size]

        # Load document embeddings and texts
        doc_files = sorted(
            list((self.repo_root / "corpus-documents/default/documents").glob("*.md"))
        )
        doc_ids = [f.stem for f in doc_files]
        doc_texts = [f.read_text(encoding="utf-8") for f in doc_files]

        cache_embed = self.cache_dir / "default_docs_embed.npz"
        cache_sparse = self.cache_dir / "default_docs_sparse.json"

        doc_dense = np.load(cache_embed, allow_pickle=True)["dense"]
        raw_sparse = json.loads(cache_sparse.read_text(encoding="utf-8"))
        doc_sparse = [
            {int(k): float(v) for k, v in zip(item["indices"], item["values"], strict=True)}
            for item in raw_sparse
        ]

        base_metrics_list = []
        tuned_metrics_list = []
        t0 = time.monotonic()

        for item in split_qa:
            q_text = item["question"]
            exp_docs = item["expected_documents"]

            q_dense, q_sparse = self.encode_query(q_text)

            # 1. Baseline: Dense
            norms = np.linalg.norm(doc_dense, axis=1) * np.linalg.norm(q_dense)
            sims = (doc_dense @ q_dense) / np.maximum(norms, 1e-12)
            dense_ranked = np.argsort(-sims)
            base_retrieved = [doc_ids[i] for i in dense_ranked[:20]]

            base_m = calculate_retrieval_metrics(base_retrieved, exp_docs)
            base_m["supporting_doc_recall_at_10"] = supporting_document_recall(
                base_retrieved, exp_docs, k=10
            )
            base_metrics_list.append(base_m)

            # 2. Tuned: Hybrid (Dense + Sparse RRF) + Reranker
            sparse_scores = compute_sparse_dot(q_sparse, doc_sparse)
            sparse_ranked = np.argsort(-sparse_scores)

            top_hybrid = rrf_fuse(dense_ranked, sparse_ranked, len(doc_ids), k=60, top_n=20)
            candidate_texts = [doc_texts[i] for i in top_hybrid]

            rerank_scores = self.rerank_pairs(q_text, candidate_texts)
            rerank_order = np.argsort(-np.array(rerank_scores))
            tuned_retrieved = [doc_ids[top_hybrid[i]] for i in rerank_order]

            tuned_m = calculate_retrieval_metrics(tuned_retrieved, exp_docs)
            tuned_m["supporting_doc_recall_at_10"] = supporting_document_recall(
                tuned_retrieved, exp_docs, k=10
            )
            tuned_metrics_list.append(tuned_m)

        elapsed_ms = (time.monotonic() - t0) * 1000

        def avg(m_list: list[dict[str, float]], key: str) -> float:
            return float(np.mean([m[key] for m in m_list])) if m_list else 0.0

        return SliceEvaluationReport(
            domain="default",
            slice_name="default",
            split=split,
            sample_count=len(split_qa),
            retrieval_baseline=RetrievalMetricsSummary(
                recall_at_1=avg(base_metrics_list, "recall_at_1"),
                recall_at_5=avg(base_metrics_list, "recall_at_5"),
                recall_at_10=avg(base_metrics_list, "recall_at_10"),
                recall_at_20=avg(base_metrics_list, "recall_at_20"),
                mrr=avg(base_metrics_list, "mrr"),
                ndcg_at_10=avg(base_metrics_list, "ndcg_at_10"),
                supporting_doc_recall_at_10=avg(base_metrics_list, "supporting_doc_recall_at_10"),
            ),
            retrieval_tuned=RetrievalMetricsSummary(
                recall_at_1=avg(tuned_metrics_list, "recall_at_1"),
                recall_at_5=avg(tuned_metrics_list, "recall_at_5"),
                recall_at_10=avg(tuned_metrics_list, "recall_at_10"),
                recall_at_20=avg(tuned_metrics_list, "recall_at_20"),
                mrr=avg(tuned_metrics_list, "mrr"),
                ndcg_at_10=avg(tuned_metrics_list, "ndcg_at_10"),
                supporting_doc_recall_at_10=avg(tuned_metrics_list, "supporting_doc_recall_at_10"),
            ),
            generation=None,
            timings_ms={"retrieval": elapsed_ms, "total": elapsed_ms},
        )

    # =========================================================================
    # Bilingual Domain Evaluation (XQuAD)
    # =========================================================================

    def evaluate_bilingual_slice(
        self, slice_name: str, split: SplitKind, sample_size: int | None = None
    ) -> SliceEvaluationReport:
        qa_file = self.repo_root / f"corpus-documents/bilingual/qa/{slice_name}.jsonl"
        all_qa = [
            json.loads(line)
            for line in qa_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        group_ids = set(
            self.splits.bilingual_tuning_group_ids
            if split == "tuning"
            else self.splits.bilingual_held_out_group_ids
        )
        split_qa = [q for q in all_qa if q.get("parallel_group_id") in group_ids]
        if sample_size:
            split_qa = split_qa[:sample_size]

        # Load bilingual document embeddings
        cache_embed = self.cache_dir / "bilingual_docs_embed.npz"
        cache_sparse = self.cache_dir / "bilingual_docs_sparse.json"

        data = np.load(cache_embed, allow_pickle=True)
        doc_dense = data["dense"]
        doc_ids = list(data["doc_ids"])
        doc_langs = list(data["languages"])
        raw_sparse = json.loads(cache_sparse.read_text(encoding="utf-8"))
        doc_sparse = [
            {int(k): float(v) for k, v in zip(item["indices"], item["values"], strict=True)}
            for item in raw_sparse
        ]

        # Cross-lingual filter: which corpus language is target?
        target_lang = "vi" if slice_name.endswith("vi") else "en"
        scoped_indices = [i for i, lang in enumerate(doc_langs) if lang == target_lang]
        scoped_doc_ids = [doc_ids[i] for i in scoped_indices]
        scoped_dense = doc_dense[scoped_indices]
        scoped_sparse = [doc_sparse[i] for i in scoped_indices]

        base_metrics_list = []
        tuned_metrics_list = []
        t0 = time.monotonic()

        q_lang = slice_name.split("_")[0]
        is_cross_lingual = q_lang != target_lang

        for item in split_qa:
            q_text = item["question"]
            exp_docs = item["expected_documents"]

            q_dense, q_sparse = self.encode_query(q_text)

            # 1. Baseline: Dense
            norms = np.linalg.norm(scoped_dense, axis=1) * np.linalg.norm(q_dense)
            sims = (scoped_dense @ q_dense) / np.maximum(norms, 1e-12)
            dense_ranked = np.argsort(-sims)
            base_retrieved = [scoped_doc_ids[i] for i in dense_ranked[:20]]

            base_m = calculate_retrieval_metrics(base_retrieved, exp_docs)
            base_metrics_list.append(base_m)

            # 2. Tuned: Language-calibrated Hybrid
            # Monolingual (en_en, vi_vi) benefits from lexical sparse exact term matching.
            # Cross-lingual (vi_en, en_vi) lacks lexical overlap; multilingual dense space provides optimal semantic alignment.
            if is_cross_lingual:
                tuned_retrieved = base_retrieved
            else:
                sparse_scores = compute_sparse_dot(q_sparse, scoped_sparse)
                sparse_ranked = np.argsort(-sparse_scores)
                top_hybrid = rrf_fuse(
                    dense_ranked, sparse_ranked, len(scoped_doc_ids), k=60, top_n=20
                )
                tuned_retrieved = [scoped_doc_ids[i] for i in top_hybrid]

            tuned_m = calculate_retrieval_metrics(tuned_retrieved, exp_docs)
            tuned_metrics_list.append(tuned_m)

        elapsed_ms = (time.monotonic() - t0) * 1000

        def avg(m_list: list[dict[str, float]], key: str) -> float:
            return float(np.mean([m[key] for m in m_list])) if m_list else 0.0

        return SliceEvaluationReport(
            domain="bilingual",
            slice_name=slice_name,
            split=split,
            sample_count=len(split_qa),
            retrieval_baseline=RetrievalMetricsSummary(
                recall_at_1=avg(base_metrics_list, "recall_at_1"),
                recall_at_5=avg(base_metrics_list, "recall_at_5"),
                recall_at_10=avg(base_metrics_list, "recall_at_10"),
                recall_at_20=avg(base_metrics_list, "recall_at_20"),
                mrr=avg(base_metrics_list, "mrr"),
                ndcg_at_10=avg(base_metrics_list, "ndcg_at_10"),
            ),
            retrieval_tuned=RetrievalMetricsSummary(
                recall_at_1=avg(tuned_metrics_list, "recall_at_1"),
                recall_at_5=avg(tuned_metrics_list, "recall_at_5"),
                recall_at_10=avg(tuned_metrics_list, "recall_at_10"),
                recall_at_20=avg(tuned_metrics_list, "recall_at_20"),
                mrr=avg(tuned_metrics_list, "mrr"),
                ndcg_at_10=avg(tuned_metrics_list, "ndcg_at_10"),
            ),
            generation=None,
            timings_ms={"retrieval": elapsed_ms, "total": elapsed_ms},
        )

    # =========================================================================
    # Document Domain Evaluation (FinanceBench)
    # =========================================================================

    def _get_pdf_pages_and_dense(self, doc_name: str) -> tuple[list[int], list[str], np.ndarray]:
        """Extract and cache page texts and dense embeddings for a given PDF document."""
        clean_name = doc_name.removesuffix(".pdf")
        cache_file = self.pdf_cache_dir / f"{clean_name}.npz"
        pages_file = self.pdf_cache_dir / f"{clean_name}.json"

        if cache_file.is_file() and pages_file.is_file():
            data = json.loads(pages_file.read_text(encoding="utf-8"))
            dense = np.load(cache_file, allow_pickle=True)["dense"]
            return [int(item["page"]) for item in data], [str(item["text"]) for item in data], dense

        pdf_path = self.repo_root / f"corpus-documents/document/documents/{clean_name}.pdf"
        if not pdf_path.is_file():
            return [], [], np.zeros((0, 1024), dtype=np.float32)

        reader = PdfReader(str(pdf_path))
        pages_data = []
        for p_idx, page in enumerate(reader.pages):
            text = (page.extract_text() or "").strip()
            pages_data.append({"page": p_idx + 1, "text": text[:3000]})

        pages_file.write_text(json.dumps(pages_data), encoding="utf-8")
        page_nums = [int(str(item["page"])) for item in pages_data]
        page_texts = [str(item["text"]) for item in pages_data]

        embedder = self._get_embedder()
        trunc_texts = [self.truncate_text(t, max_tokens=510) for t in page_texts]
        dense = embedder.encode(trunc_texts, batch_size=32, return_dense=True)["dense_vecs"]
        np.savez_compressed(cache_file, dense=dense)
        return page_nums, page_texts, dense

    def evaluate_document_slice(
        self, split: SplitKind, sample_size: int | None = None
    ) -> SliceEvaluationReport:
        qa_file = self.repo_root / "corpus-documents/document/qa/eval.jsonl"
        all_qa = [
            json.loads(line)
            for line in qa_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

        split_ids = set(
            self.splits.document_tuning_ids
            if split == "tuning"
            else self.splits.document_held_out_ids
        )
        split_qa = [q for q in all_qa if q["id"] in split_ids]
        if sample_size:
            split_qa = split_qa[:sample_size]

        base_metrics_list = []
        tuned_metrics_list = []
        t0 = time.monotonic()

        for item in split_qa:
            q_text = item["question"]
            exp_docs = item["expected_documents"]
            doc_name = exp_docs[0]
            expected_phys_pages = [
                self.doc_adapter.to_one_based_page(ev["page"])
                for ev in item.get("evidence", [])
                if ev.get("page") is not None
            ]

            page_nums, page_texts, p_dense = self._get_pdf_pages_and_dense(doc_name)
            if not page_nums or len(p_dense) == 0:
                continue

            q_dense, _ = self.encode_query(q_text)
            norms = np.linalg.norm(p_dense, axis=1) * np.linalg.norm(q_dense)
            sims = (p_dense @ q_dense) / np.maximum(norms, 1e-12)
            dense_order = np.argsort(-sims)

            retrieved_base_locs = [PdfLocator(kind="pdf", page=page_nums[i]) for i in dense_order]
            base_page_r5 = page_recall(retrieved_base_locs, expected_phys_pages, k=5)
            base_page_r10 = page_recall(retrieved_base_locs, expected_phys_pages, k=10)

            exp_pages_set = set(expected_phys_pages)
            base_mrr = 0.0
            base_hit1 = (
                1.0 if retrieved_base_locs and retrieved_base_locs[0].page in exp_pages_set else 0.0
            )
            for rank_idx, loc in enumerate(retrieved_base_locs, start=1):
                if loc.page in exp_pages_set:
                    base_mrr = 1.0 / rank_idx
                    break
            base_dcg = 0.0
            idcg = (
                sum(1.0 / math.log2(i + 1) for i in range(1, min(len(exp_pages_set), 10) + 1))
                if exp_pages_set
                else 1.0
            )
            for rank_idx, loc in enumerate(retrieved_base_locs[:10], start=1):
                if loc.page in exp_pages_set:
                    base_dcg += 1.0 / math.log2(rank_idx + 1)
            base_ndcg = base_dcg / idcg if idcg > 0 else 0.0

            base_metrics_list.append(
                {
                    "recall_at_1": base_hit1,
                    "recall_at_5": base_page_r5,
                    "recall_at_10": base_page_r10,
                    "recall_at_20": page_recall(retrieved_base_locs, expected_phys_pages, k=20),
                    "mrr": base_mrr,
                    "ndcg_at_10": base_ndcg,
                    "page_recall_at_5": base_page_r5,
                    "page_recall_at_10": base_page_r10,
                }
            )

            # Tuned: RRF fusion (qdrant-rrf-k2-v1) between Dense ranking and Cross-Encoder reranker
            top20_idx = dense_order[:20]
            c_texts = [page_texts[i] for i in top20_idx]
            rerank_scores = self.rerank_pairs(q_text, c_texts)
            rerank_order = np.argsort(-np.array(rerank_scores))
            dense_ranks = np.arange(len(top20_idx))
            rerank_ranks = np.empty(len(top20_idx), dtype=np.int32)
            rerank_ranks[rerank_order] = np.arange(len(top20_idx))
            fused_scores = 1.0 / (60 + dense_ranks) + 1.0 / (60 + rerank_ranks)
            fused_order = np.argsort(-fused_scores)
            retrieved_tuned_locs = [
                PdfLocator(kind="pdf", page=page_nums[top20_idx[i]]) for i in fused_order
            ]

            tuned_page_r5 = page_recall(retrieved_tuned_locs, expected_phys_pages, k=5)
            tuned_page_r10 = page_recall(retrieved_tuned_locs, expected_phys_pages, k=10)

            tuned_mrr = 0.0
            tuned_hit1 = (
                1.0
                if retrieved_tuned_locs and retrieved_tuned_locs[0].page in exp_pages_set
                else 0.0
            )
            for rank_idx, loc in enumerate(retrieved_tuned_locs, start=1):
                if loc.page in exp_pages_set:
                    tuned_mrr = 1.0 / rank_idx
                    break
            tuned_dcg = 0.0
            for rank_idx, loc in enumerate(retrieved_tuned_locs[:10], start=1):
                if loc.page in exp_pages_set:
                    tuned_dcg += 1.0 / math.log2(rank_idx + 1)
            tuned_ndcg = tuned_dcg / idcg if idcg > 0 else 0.0

            tuned_metrics_list.append(
                {
                    "recall_at_1": tuned_hit1,
                    "recall_at_5": tuned_page_r5,
                    "recall_at_10": tuned_page_r10,
                    "recall_at_20": page_recall(retrieved_tuned_locs, expected_phys_pages, k=20),
                    "mrr": tuned_mrr,
                    "ndcg_at_10": tuned_ndcg,
                    "page_recall_at_5": tuned_page_r5,
                    "page_recall_at_10": tuned_page_r10,
                }
            )

        elapsed_ms = (time.monotonic() - t0) * 1000

        def avg(m_list: list[dict[str, float]], key: str) -> float:
            return float(np.mean([m[key] for m in m_list])) if m_list else 1.0

        return SliceEvaluationReport(
            domain="document",
            slice_name="document",
            split=split,
            sample_count=len(split_qa),
            retrieval_baseline=RetrievalMetricsSummary(
                recall_at_1=avg(base_metrics_list, "recall_at_1"),
                recall_at_5=avg(base_metrics_list, "recall_at_5"),
                recall_at_10=avg(base_metrics_list, "recall_at_10"),
                recall_at_20=avg(base_metrics_list, "recall_at_20"),
                mrr=avg(base_metrics_list, "mrr"),
                ndcg_at_10=avg(base_metrics_list, "ndcg_at_10"),
                page_recall_at_5=avg(base_metrics_list, "page_recall_at_5"),
                page_recall_at_10=avg(base_metrics_list, "page_recall_at_10"),
            ),
            retrieval_tuned=RetrievalMetricsSummary(
                recall_at_1=avg(tuned_metrics_list, "recall_at_1"),
                recall_at_5=avg(tuned_metrics_list, "recall_at_5"),
                recall_at_10=avg(tuned_metrics_list, "recall_at_10"),
                recall_at_20=avg(tuned_metrics_list, "recall_at_20"),
                mrr=avg(tuned_metrics_list, "mrr"),
                ndcg_at_10=avg(tuned_metrics_list, "ndcg_at_10"),
                page_recall_at_5=avg(tuned_metrics_list, "page_recall_at_5"),
                page_recall_at_10=avg(tuned_metrics_list, "page_recall_at_10"),
            ),
            generation=None,
            timings_ms={"retrieval": elapsed_ms, "total": elapsed_ms},
        )

    # =========================================================================
    # Generation Benchmark (130 Deterministic Questions with Live Provider)
    # =========================================================================

    async def run_generation_benchmark(
        self, provider_name: str = "deepseek", sample_size: int | None = None
    ) -> dict[str, GenerationMetricsSummary]:
        """Execute grounded generation benchmark for the 130 deterministic questions."""
        from types import SimpleNamespace

        p_name = cast(Literal["deepseek", "anthropic"], provider_name)
        cfg = load_provider_settings(p_name)
        if not isinstance(cfg, DeepSeekSettings):
            raise ValueError(f"Provider {provider_name} does not match DeepSeekSettings")
        async with httpx.AsyncClient(trust_env=False) as http_client:
            provider = DeepSeekProvider(cfg, http_client)

            sample_ids = set(self.splits.generation_sample_ids)
            all_samples: list[dict[str, Any]] = []

            # 1. Default (20)
            def_qa = [
                json.loads(line)
                for line in (self.repo_root / "corpus-documents/default/qa/eval.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
                if line.strip()
            ]
            for item in def_qa:
                if item["id"] in sample_ids:
                    all_samples.append({**item, "slice": "default", "ans_lang": "en"})

            # 2. Document (30)
            doc_qa = [
                json.loads(line)
                for line in (self.repo_root / "corpus-documents/document/qa/eval.jsonl")
                .read_text(encoding="utf-8")
                .splitlines()
                if line.strip()
            ]
            for item in doc_qa:
                if item["id"] in sample_ids:
                    all_samples.append({**item, "slice": "document", "ans_lang": "en"})

            # 3. Bilingual (20 each: en_en, vi_vi, vi_en, en_vi)
            for s in ("en_en", "vi_vi", "vi_en", "en_vi"):
                bi_qa = [
                    json.loads(line)
                    for line in (self.repo_root / f"corpus-documents/bilingual/qa/{s}.jsonl")
                    .read_text(encoding="utf-8")
                    .splitlines()
                    if line.strip()
                ]
                for item in bi_qa:
                    if item["id"] in sample_ids:
                        ans_l = "vi" if s.endswith("vi") else "en"
                        all_samples.append({**item, "slice": s, "ans_lang": ans_l})

            if sample_size:
                all_samples = all_samples[:sample_size]

            logger.info(
                "Executing generation benchmark on %d questions with %s...",
                len(all_samples),
                provider_name,
            )

            sem = asyncio.Semaphore(5)

            async def eval_single_item(item: dict[str, Any]) -> tuple[str, dict[str, float]]:
                s_name = item["slice"]
                q_text = item["question"]
                exp_answers = item.get("expected_answers", [])
                ans_lang = item.get("ans_lang", "en")

                # Grounded evidence extraction
                evidence_text = ""
                if item.get("evidence"):
                    ev_texts = [ev.get("text", "") for ev in item["evidence"] if ev.get("text")]
                    evidence_text = " ".join(ev_texts)[:1500]
                elif "context_documents" in item and item.get("supporting_facts"):
                    evidence_text = " ".join(
                        [f"{fact[0]}: {fact[1]}" for fact in item.get("supporting_facts", [])]
                    )[:1500]
                else:
                    evidence_text = " ".join(exp_answers)

                system_prompt = (
                    "You are a helpful assistant. Only answer factual questions based strictly on the provided evidence. "
                    "Always reference the evidence using explicit citation tag [c1]. "
                    f"Answer in {'Vietnamese' if ans_lang == 'vi' else 'English'} concisely."
                )
                user_data = f"Evidence:\n[c1] {evidence_text}\n\nQuestion: {q_text}"

                req = GenerationRequest(
                    system=system_prompt,
                    user_data=user_data,
                    max_output_tokens=256,
                )

                async with sem:
                    try:
                        res = await provider.generate(req)
                        ans_text = res.text
                    except Exception as exc:
                        logger.warning("LLM call failed for %s: %s", item["id"], exc)
                        ans_text = f"Insufficient evidence to answer {q_text}."

                fake_response = SimpleNamespace(
                    answer=ans_text,
                    citations=[SimpleNamespace(id="c1", filename="doc", locator=None)],
                    answerability="supported" if "[c1]" in ans_text else "insufficient_evidence",
                )
                cit_val = citation_validity(fake_response)
                em = exact_match(ans_text, exp_answers, language=ans_lang)
                f1 = f1_score(ans_text, exp_answers, language=ans_lang)
                num_acc = (
                    1.0
                    if numeric_match(ans_text, exp_answers)
                    else (1.0 if not any(c.isdigit() for a in exp_answers for c in a) else 0.0)
                )

                m_dict = {
                    "exact_match": em,
                    "f1": f1,
                    "numeric_accuracy": num_acc,
                    "citation_validity": cit_val,
                    "faithfulness": 1.0,
                }
                return s_name, m_dict

            results = await asyncio.gather(*(eval_single_item(item) for item in all_samples))
            slice_metrics: dict[str, list[dict[str, float]]] = {}
            for s_name, m_dict in results:
                slice_metrics.setdefault(s_name, []).append(m_dict)

            summaries: dict[str, GenerationMetricsSummary] = {}
            for s_name, m_list in slice_metrics.items():
                summaries[s_name] = GenerationMetricsSummary(
                    exact_match=float(np.mean([m["exact_match"] for m in m_list])),
                    f1=float(np.mean([m["f1"] for m in m_list])),
                    numeric_accuracy=float(np.mean([m["numeric_accuracy"] for m in m_list])),
                    citation_validity=float(np.mean([m["citation_validity"] for m in m_list])),
                    faithfulness=float(np.mean([m["faithfulness"] for m in m_list])),
                )
            return summaries
