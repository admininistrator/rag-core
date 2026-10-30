"""Evaluation protocol, split definitions, and anti-leakage boundaries."""

import json
import random
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SplitKind = Literal["tuning", "held_out"]
EvaluationStage = Literal["ingest", "retrieval", "generation", "report", "all"]
EvaluationDomain = Literal["default", "document", "bilingual", "multilingual"]


class EvaluationLeakageError(Exception):
    """Raised when evaluation ground truth or out-of-scope data leaks into ingestion or retrieval."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class GoldEvidence(BaseModel):
    """Ground truth evidence reference."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    document: str
    page: int | None = None  # Zero-based in FinanceBench raw annotations
    text: str | None = None


class EvalSample(BaseModel):
    """Normalized question/answer item for evaluation."""

    model_config = ConfigDict(extra="ignore", frozen=True)

    id: str
    domain: str
    question: str
    expected_answers: list[str] = Field(default_factory=list)
    expected_documents: list[str] = Field(default_factory=list)
    evidence: list[GoldEvidence] = Field(default_factory=list)
    supporting_facts: list[tuple[str, int]] = Field(default_factory=list)
    question_language: str = "en"
    corpus_languages: list[str] = Field(default_factory=lambda: ["en"])
    answer_language: str = "en"
    category: str | None = None
    difficulty: str | None = None
    parallel_group_id: str | None = None
    evaluation_slice: str | None = None
    answerable: bool = True
    source_dataset: str = ""
    justification: str | None = None


class DatasetSplits(BaseModel):
    """Frozen deterministic splits for tuning vs held-out and generation sampling."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    seed: int = 42
    default_tuning_ids: list[str]
    default_held_out_ids: list[str]
    document_tuning_ids: list[str]
    document_held_out_ids: list[str]
    document_tuning_pdfs: list[str]
    document_held_out_pdfs: list[str]
    bilingual_tuning_group_ids: list[str]
    bilingual_held_out_group_ids: list[str]
    generation_sample_ids: list[str]


def is_ingestable_document(path: Path) -> bool:
    """Determine whether a path is an ingestable corpus document or a ground truth QA file.

    Strictly rejects QA directories, JSONL question files, and files containing answer annotations.
    """
    parts = set(path.parts)
    if "qa" in parts or "raw" in parts:
        return False
    if path.name.endswith(".jsonl"):
        return False
    if path.name.startswith("eval.") or "eval" in path.stem:
        return False

    # Check for known ground truth markers if it is a JSON or text file
    if path.suffix.lower() in (".json", ".txt"):
        try:
            content = path.read_text(encoding="utf-8")
            if any(
                marker in content
                for marker in (
                    '"expected_answers"',
                    '"supporting_facts"',
                    '"justification"',
                    '"source_qa_id"',
                )
            ):
                return False
        except Exception:
            pass

    return True


def assert_no_qa_leakage(paths: Iterable[Path]) -> None:
    """Validate that none of the target paths for ingestion contain QA or ground-truth annotations."""
    for p in paths:
        if not is_ingestable_document(p):
            raise EvaluationLeakageError(
                f"Evaluation ground truth leakage detected: path '{p}' is a QA/ground-truth file and must not be ingested."
            )


def generate_deterministic_splits(corpus_root: Path, seed: int = 42) -> DatasetSplits:
    """Generate reproducible tuning vs held-out splits and the 130-question generation benchmark sample.

    Anti-leakage invariants:
    1. Document RAG: Disjoint by referenced PDF documents (zero overlap).
    2. Bilingual RAG: Disjoint by parallel_group_id across all slices (zero overlap).
    3. Default RAG: Disjoint by connected components of expected documents (zero overlap).
    4. Generation benchmark: exactly 130 questions (20 Default, 30 Document, 20 each bilingual slice).
    """
    # 1. Document (FinanceBench)
    doc_qa_path = corpus_root / "document" / "qa" / "eval.jsonl"
    doc_qa = [
        json.loads(line)
        for line in doc_qa_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    all_pdfs = sorted(list(set(q["expected_documents"][0] for q in doc_qa)))
    rng_doc = random.Random(seed)
    shuffled_pdfs = list(all_pdfs)
    rng_doc.shuffle(shuffled_pdfs)
    split_point_doc = len(shuffled_pdfs) // 2
    tuning_pdfs = sorted(shuffled_pdfs[:split_point_doc])
    held_out_pdfs = sorted(shuffled_pdfs[split_point_doc:])
    tuning_pdf_set = set(tuning_pdfs)
    held_out_pdf_set = set(held_out_pdfs)
    assert not (tuning_pdf_set & held_out_pdf_set), "Document PDFs must be disjoint!"

    doc_tuning_ids = [q["id"] for q in doc_qa if q["expected_documents"][0] in tuning_pdf_set]
    doc_held_out_ids = [q["id"] for q in doc_qa if q["expected_documents"][0] in held_out_pdf_set]

    # 2. Bilingual (XQuAD)
    enen_qa_path = corpus_root / "bilingual" / "qa" / "en_en.jsonl"
    enen_qa = [
        json.loads(line)
        for line in enen_qa_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    all_groups = sorted(list(set(q["parallel_group_id"] for q in enen_qa)))
    rng_bi = random.Random(seed)
    shuffled_groups = list(all_groups)
    rng_bi.shuffle(shuffled_groups)
    split_point_bi = len(shuffled_groups) // 2
    tuning_groups = sorted(shuffled_groups[:split_point_bi])
    held_out_groups = sorted(shuffled_groups[split_point_bi:])
    assert not (set(tuning_groups) & set(held_out_groups)), "Bilingual groups must be disjoint!"

    # 3. Default (HotpotQA)
    default_qa_path = corpus_root / "default" / "qa" / "eval.jsonl"
    default_qa = [
        json.loads(line)
        for line in default_qa_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    doc_to_qas: dict[str, set[str]] = defaultdict(set)
    qa_to_docs: dict[str, tuple[str, ...]] = {}
    for q in default_qa:
        qid = q["id"]
        docs = tuple(q.get("expected_documents", []))
        qa_to_docs[qid] = docs
        for d in docs:
            doc_to_qas[d].add(qid)

    visited: set[str] = set()
    components: list[list[str]] = []
    for q in default_qa:
        qid = q["id"]
        if qid in visited:
            continue
        comp: set[str] = set()
        queue = [qid]
        while queue:
            curr = queue.pop(0)
            if curr in comp:
                continue
            comp.add(curr)
            visited.add(curr)
            for d in qa_to_docs[curr]:
                for neighbor in doc_to_qas[d]:
                    if neighbor not in comp:
                        queue.append(neighbor)
        components.append(sorted(list(comp)))

    rng_def = random.Random(seed)
    shuffled_components = list(components)
    rng_def.shuffle(shuffled_components)
    def_tuning_ids: list[str] = []
    def_held_out_ids: list[str] = []
    for comp_items in shuffled_components:
        if len(def_tuning_ids) <= len(def_held_out_ids):
            def_tuning_ids.extend(comp_items)
        else:
            def_held_out_ids.extend(comp_items)

    # 4. Deterministic Generation Sample (130 questions total)
    # Target: 20 Default (10 tuning, 10 held_out)
    #         30 Document (15 tuning, 15 held_out)
    #         20 en_en (10 tuning, 10 held_out)
    #         20 vi_vi (10 tuning, 10 held_out)
    #         20 vi_en (10 tuning, 10 held_out)
    #         20 en_vi (10 tuning, 10 held_out)
    rng_sample = random.Random(seed)
    gen_samples: list[str] = []

    def sample_half_and_half(
        tuning_list: list[str], held_out_list: list[str], count: int
    ) -> list[str]:
        t_count = count // 2
        h_count = count - t_count
        sampled_t = sorted(rng_sample.sample(tuning_list, min(t_count, len(tuning_list))))
        sampled_h = sorted(rng_sample.sample(held_out_list, min(h_count, len(held_out_list))))
        return sampled_t + sampled_h

    # Default
    gen_samples.extend(sample_half_and_half(def_tuning_ids, def_held_out_ids, 20))

    # Document
    gen_samples.extend(sample_half_and_half(doc_tuning_ids, doc_held_out_ids, 30))

    # Bilingual 4 slices
    tuning_group_set = set(tuning_groups)
    for slice_name in ("en_en", "vi_vi", "vi_en", "en_vi"):
        slice_path = corpus_root / "bilingual" / "qa" / f"{slice_name}.jsonl"
        slice_qa = [
            json.loads(line)
            for line in slice_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        slice_t = [q["id"] for q in slice_qa if q["parallel_group_id"] in tuning_group_set]
        slice_h = [q["id"] for q in slice_qa if q["parallel_group_id"] not in tuning_group_set]
        gen_samples.extend(sample_half_and_half(slice_t, slice_h, 20))

    assert len(gen_samples) == 130, f"Expected 130 generation samples, got {len(gen_samples)}"

    return DatasetSplits(
        seed=seed,
        default_tuning_ids=sorted(def_tuning_ids),
        default_held_out_ids=sorted(def_held_out_ids),
        document_tuning_ids=sorted(doc_tuning_ids),
        document_held_out_ids=sorted(doc_held_out_ids),
        document_tuning_pdfs=tuning_pdfs,
        document_held_out_pdfs=held_out_pdfs,
        bilingual_tuning_group_ids=tuning_groups,
        bilingual_held_out_group_ids=held_out_groups,
        generation_sample_ids=sorted(gen_samples),
    )


def load_splits(path: Path) -> DatasetSplits:
    """Load and validate frozen splits from a JSON file."""
    if not path.is_file():
        raise FileNotFoundError(f"Splits file not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    return DatasetSplits.model_validate(data)


def save_splits(splits: DatasetSplits, path: Path) -> None:
    """Save dataset splits to a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(splits.model_dump_json(indent=2) + "\n", encoding="utf-8")
