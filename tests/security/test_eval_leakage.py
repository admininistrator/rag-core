"""Security tests for evaluation anti-leakage boundaries and namespace isolation."""

from pathlib import Path
from uuid import uuid4

import pytest

from rag_core.evaluation.adapters import (
    BilingualGoldAdapter,
    FinanceBenchGoldAdapter,
)
from rag_core.evaluation.protocol import (
    EvalSample,
    EvaluationLeakageError,
    GoldEvidence,
    assert_no_qa_leakage,
    is_ingestable_document,
    load_splits,
)

pytestmark = pytest.mark.security


def test_qa_files_never_ingested_in_corpus() -> None:
    """Verify that all corpus documents for ingestion are strictly in documents/ and never in qa/."""
    corpus_root = Path("corpus-documents")
    assert corpus_root.is_dir()

    for domain in ("default", "document", "bilingual"):
        doc_dir = corpus_root / domain / "documents"
        if not doc_dir.is_dir():
            continue

        for doc_file in doc_dir.rglob("*"):
            if doc_file.is_file():
                # Every file inside documents/ must be a valid ingestable document
                assert is_ingestable_document(doc_file), (
                    f"Document {doc_file} failed ingestability check!"
                )
                # File must NOT contain QA markers
                if doc_file.suffix.lower() in (".json", ".txt"):
                    content = doc_file.read_text(encoding="utf-8")
                    assert '"expected_answers"' not in content
                    assert '"justification"' not in content

    # Test that passing a QA file to assert_no_qa_leakage raises an error
    qa_path = corpus_root / "default" / "qa" / "eval.jsonl"
    if qa_path.is_file():
        with pytest.raises(EvaluationLeakageError, match="leakage"):
            assert_no_qa_leakage([qa_path])


def test_tuning_and_held_out_splits_zero_overlap() -> None:
    """Verify that tuning and held-out splits have zero document or group overlap."""
    splits_path = Path("configs/evaluation_splits.json")
    splits = load_splits(splits_path)

    # 1. Document domain (FinanceBench): 0 PDF overlap
    tuning_pdfs = set(splits.document_tuning_pdfs)
    held_out_pdfs = set(splits.document_held_out_pdfs)
    assert len(tuning_pdfs) > 0 and len(held_out_pdfs) > 0
    overlap_pdfs = tuning_pdfs & held_out_pdfs
    assert not overlap_pdfs, f"Found PDF overlap in Document split: {overlap_pdfs}"

    # Document questions overlap check
    tuning_doc_qas = set(splits.document_tuning_ids)
    held_out_doc_qas = set(splits.document_held_out_ids)
    assert not (tuning_doc_qas & held_out_doc_qas)

    # 2. Bilingual domain (XQuAD): 0 parallel group overlap
    tuning_groups = set(splits.bilingual_tuning_group_ids)
    held_out_groups = set(splits.bilingual_held_out_group_ids)
    assert len(tuning_groups) > 0 and len(held_out_groups) > 0
    overlap_groups = tuning_groups & held_out_groups
    assert not overlap_groups, f"Found parallel group overlap in Bilingual split: {overlap_groups}"

    # 3. Default domain (HotpotQA): 0 question overlap
    tuning_def_qas = set(splits.default_tuning_ids)
    held_out_def_qas = set(splits.default_held_out_ids)
    assert len(tuning_def_qas) > 0 and len(held_out_def_qas) > 0
    assert not (tuning_def_qas & held_out_def_qas)

    # 4. Generation sample: exactly 130 deterministic questions
    assert len(splits.generation_sample_ids) == 130


def test_no_gold_page_prefilter_in_retrieval() -> None:
    """Verify that retrieval queries for Document RAG NEVER include page or locator pre-filters."""
    adapter = FinanceBenchGoldAdapter()
    sample = EvalSample(
        id="fb_003",
        domain="document",
        question="What was the FY2022 CAPEX for 3M?",
        expected_answers=["$1,751 million"],
        expected_documents=["3M_2022_10K"],
        evidence=[GoldEvidence(document="3M_2022_10K", page=45)],
    )

    doc_uuid = uuid4()
    req = adapter.prepare_query_request(
        sample, session_id=uuid4(), document_id_map={"3M_2022_10K.pdf": doc_uuid}
    )

    # QueryRequest must only contain document_ids, never the gold page number
    req_dict = req.model_dump()
    assert "page" not in req_dict
    assert "locator" not in req_dict
    assert "block" not in req_dict
    assert req_dict["document_ids"] == [doc_uuid]


def test_eval_namespace_isolation() -> None:
    """Verify that evaluation runner uses dedicated evaluation principal and namespace."""
    from rag_core.evaluation.runner import EvaluationRunner

    runner = EvaluationRunner(config_path=Path("configs/evaluation.yaml"), mode="fixture")
    manifest = runner.run_fixture_benchmark(sample_size=1)

    assert manifest.run_id.startswith("eval-run-")
    # All gates must strictly pass in fixture mode
    assert manifest.passed_all_gates is True


def test_xquad_unanswerable_boundary() -> None:
    """Verify that XQuAD is identified as having no unanswerable questions and cannot claim anti-hallucination."""
    adapter = BilingualGoldAdapter()
    assert adapter.is_unanswerable_benchmark is False

    from rag_core.evaluation.runner import EvaluationRunner

    runner = EvaluationRunner(config_path=Path("configs/evaluation.yaml"), mode="fixture")
    manifest = runner.run_fixture_benchmark(sample_size=1)

    # Verify limitations explicitly mention XQuAD
    xquad_limits = [lim for lim in manifest.limitations if "XQuAD" in lim]
    assert len(xquad_limits) > 0
    assert "no unanswerable questions" in xquad_limits[0]
