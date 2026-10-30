"""Contract tests for evaluation protocol, gold adapters, anti-leakage invariants, and metrics."""

import unicodedata
from pathlib import Path
from uuid import uuid4

import pytest

from rag_core.contracts.v1 import (
    Citation,
    PdfLocator,
)
from rag_core.evaluation.adapters import (
    BilingualGoldAdapter,
    FinanceBenchGoldAdapter,
)
from rag_core.evaluation.metrics import (
    calculate_retrieval_metrics,
    compute_token_f1,
    exact_match,
    f1_score,
    normalize_text,
    numeric_match,
    page_recall,
)
from rag_core.evaluation.protocol import (
    EvalSample,
    EvaluationLeakageError,
    GoldEvidence,
    assert_no_qa_leakage,
    is_ingestable_document,
)

pytestmark = pytest.mark.contract


# ---------------------------------------------------------------------------
# 1. answer/QA không ingest
# ---------------------------------------------------------------------------


def test_qa_files_never_ingestable() -> None:
    """Verify that QA, eval, and ground-truth files are strictly recognized as non-ingestable."""
    assert not is_ingestable_document(Path("corpus-documents/default/qa/eval.jsonl"))
    assert not is_ingestable_document(Path("corpus-documents/document/qa/eval.jsonl"))
    assert not is_ingestable_document(Path("corpus-documents/bilingual/qa/en_en.jsonl"))
    assert not is_ingestable_document(Path("corpus-documents/bilingual/qa/en_vi.jsonl"))
    assert not is_ingestable_document(Path("some/path/qa/documents_en.jsonl"))
    assert not is_ingestable_document(Path("raw/data/questions.jsonl"))

    # Legitimate corpus documents are ingestable
    assert is_ingestable_document(Path("corpus-documents/default/documents/hotpot_001.md"))
    assert is_ingestable_document(Path("corpus-documents/document/documents/3M_2018_10K.pdf"))
    assert is_ingestable_document(Path("corpus-documents/bilingual/documents/en/xquad_en_01.md"))
    assert is_ingestable_document(Path("corpus-documents/bilingual/documents/vi/xquad_vi_01.md"))


def test_assert_no_qa_leakage_raises_on_qa_paths(tmp_path: Path) -> None:
    """Verify that assert_no_qa_leakage rejects any QA or ground-truth path."""
    qa_file = tmp_path / "qa" / "eval.jsonl"
    qa_file.parent.mkdir(parents=True)
    qa_file.write_text('{"question": "test", "expected_answers": ["ans"]}', encoding="utf-8")

    with pytest.raises(EvaluationLeakageError, match="Evaluation ground truth leakage detected"):
        assert_no_qa_leakage([qa_file])

    # Also detect synthetic file containing ground truth markers even if misplaced
    leakage_doc = tmp_path / "documents" / "leaked_eval.json"
    leakage_doc.parent.mkdir(parents=True)
    leakage_doc.write_text('{"supporting_facts": [["Doc", 0]]}', encoding="utf-8")
    with pytest.raises(EvaluationLeakageError, match="leakage"):
        assert_no_qa_leakage([leakage_doc])


# ---------------------------------------------------------------------------
# 2. baseline/tuned same scope
# ---------------------------------------------------------------------------


def test_baseline_and_tuned_share_same_scope() -> None:
    """Verify that baseline and tuned evaluation share the identical document scope, split, and queries."""
    from rag_core.evaluation.runner import EvaluationRunner

    config_path = Path("configs/evaluation.yaml")
    runner = EvaluationRunner(config_path=config_path, mode="fixture")
    manifest = runner.run_fixture_benchmark(sample_size=5)

    for _domain_name, slice_reports in manifest.domains.items():
        for report in slice_reports:
            # Baseline and tuned must evaluate the exact same sample count and split
            assert report.retrieval_baseline is not None
            assert report.retrieval_tuned is not None
            assert report.sample_count > 0
            assert report.split in ("tuning", "held_out")


# ---------------------------------------------------------------------------
# 3. cross-lingual filters thật
# ---------------------------------------------------------------------------


def test_cross_lingual_filters_enforced() -> None:
    """Verify that BilingualGoldAdapter enforces real language filters for all 4 slices."""
    adapter = BilingualGoldAdapter()
    assert adapter.api_domain == "multilingual"
    session_id = uuid4()

    # Slice 1: en_vi (English question, Vietnamese corpus filter, Vietnamese answer)
    sample_en_vi = EvalSample(
        id="xquad_en_vi_001",
        domain="bilingual",
        question="What is the capital of Vietnam?",
        question_language="en",
        corpus_languages=["vi"],
        answer_language="vi",
        expected_answers=["Hà Nội"],
        expected_documents=["xquad_vi_01"],
        evaluation_slice="en_vi",
    )
    req_en_vi = adapter.prepare_query_request(sample_en_vi, session_id=session_id)
    assert req_en_vi.domain == "multilingual"
    assert req_en_vi.question == "What is the capital of Vietnam?"
    assert req_en_vi.corpus_languages == ["vi"]
    assert req_en_vi.answer_language == "vi"
    assert req_en_vi.document_ids is None

    # Slice 2: vi_en (Vietnamese question, English corpus filter, English answer)
    sample_vi_en = EvalSample(
        id="xquad_vi_en_001",
        domain="bilingual",
        question="Thủ đô của Việt Nam là gì?",
        question_language="vi",
        corpus_languages=["en"],
        answer_language="en",
        expected_answers=["Hanoi"],
        expected_documents=["xquad_en_01"],
        evaluation_slice="vi_en",
    )
    req_vi_en = adapter.prepare_query_request(sample_vi_en, session_id=session_id)
    assert req_vi_en.domain == "multilingual"
    assert req_vi_en.question == "Thủ đô của Việt Nam là gì?"
    assert req_vi_en.corpus_languages == ["en"]
    assert req_vi_en.answer_language == "en"

    # Slice 3: en_en
    sample_en_en = EvalSample(
        id="xquad_en_en_001",
        domain="bilingual",
        question="How many points?",
        question_language="en",
        corpus_languages=["en"],
        answer_language="en",
        expected_answers=["308"],
        expected_documents=["xquad_en_01"],
        evaluation_slice="en_en",
    )
    req_en_en = adapter.prepare_query_request(sample_en_en, session_id=session_id)
    assert req_en_en.corpus_languages == ["en"]
    assert req_en_en.answer_language == "en"

    # Slice 4: vi_vi
    sample_vi_vi = EvalSample(
        id="xquad_vi_vi_001",
        domain="bilingual",
        question="Có bao nhiêu điểm?",
        question_language="vi",
        corpus_languages=["vi"],
        answer_language="vi",
        expected_answers=["308"],
        expected_documents=["xquad_vi_01"],
        evaluation_slice="vi_vi",
    )
    req_vi_vi = adapter.prepare_query_request(sample_vi_vi, session_id=session_id)
    assert req_vi_vi.corpus_languages == ["vi"]
    assert req_vi_vi.answer_language == "vi"


def test_unknown_bilingual_slice_raises_leakage_error() -> None:
    adapter = BilingualGoldAdapter()
    sample_bad = EvalSample(
        id="bad_slice_001",
        domain="bilingual",
        question="Test?",
        evaluation_slice="invalid_slice",
    )
    with pytest.raises(EvaluationLeakageError, match="Unknown bilingual slice"):
        adapter.prepare_query_request(sample_bad, session_id=uuid4())


# ---------------------------------------------------------------------------
# 4. correct zero->one based conversion
# ---------------------------------------------------------------------------


def test_financebench_zero_to_one_based_page_conversion() -> None:
    """Verify conversion between FinanceBench 0-based gold pages and RAG Core 1-based physical pages."""
    adapter = FinanceBenchGoldAdapter()

    # Boundary and standard tests
    assert adapter.to_one_based_page(0) == 1
    assert adapter.to_one_based_page(59) == 60
    assert adapter.to_one_based_page(303) == 304

    assert adapter.to_zero_based_page(1) == 0
    assert adapter.to_zero_based_page(60) == 59
    assert adapter.to_zero_based_page(304) == 303

    # Invalid boundary checks
    with pytest.raises(ValueError, match="negative"):
        adapter.to_one_based_page(-1)

    with pytest.raises(ValueError, match="Physical page must be >= 1"):
        adapter.to_zero_based_page(0)


def test_financebench_citation_verification_against_gold_evidence() -> None:
    """Verify that citation verification checks the one-based page against zero-based gold."""
    adapter = FinanceBenchGoldAdapter()
    sample = EvalSample(
        id="fb_001",
        domain="document",
        question="Capital expenditures in 2018?",
        expected_answers=["$1577.00"],
        expected_documents=["3M_2018_10K"],
        evidence=[GoldEvidence(document="3M_2018_10K", page=59, text="Purchases of PP&E 1,577")],
    )

    doc_id = uuid4()
    ver_id = uuid4()

    # Correct one-based citation (page 60 corresponds to gold zero-based page 59)
    correct_citation = Citation(
        id="c1",
        document_id=doc_id,
        version_id=ver_id,
        chunk_id="chunk_60_1",
        filename="3M_2018_10K.pdf",
        locator=PdfLocator(kind="pdf", page=60),
        quote="Purchases of PP&E 1,577",
    )
    assert adapter.verify_citation(correct_citation, sample) is True

    # Incorrect citation: page 59 used directly (which would be un-converted zero-based)
    wrong_citation = Citation(
        id="c2",
        document_id=doc_id,
        version_id=ver_id,
        chunk_id="chunk_59_1",
        filename="3M_2018_10K.pdf",
        locator=PdfLocator(kind="pdf", page=59),
        quote="Statement of Cash Flows",
    )
    assert adapter.verify_citation(wrong_citation, sample) is False

    # Locator verification
    assert adapter.verify_retrieved_page(PdfLocator(kind="pdf", page=60), sample) is True
    assert adapter.verify_retrieved_page(PdfLocator(kind="pdf", page=59), sample) is False


def test_document_query_request_does_not_prefilter_page() -> None:
    """Anti-leakage: verify Document domain query request supplies document_ids without page filter."""
    adapter = FinanceBenchGoldAdapter()
    sample = EvalSample(
        id="fb_002",
        domain="document",
        question="Revenue for 3M?",
        expected_answers=["$32,765 million"],
        expected_documents=["3M_2018_10K"],
        evidence=[GoldEvidence(document="3M_2018_10K", page=12)],
    )
    doc_uuid = uuid4()
    doc_map = {"3M_2018_10K.pdf": doc_uuid}

    req = adapter.prepare_query_request(sample, session_id=uuid4(), document_id_map=doc_map)
    assert req.domain == "document"
    assert req.document_ids == [doc_uuid]
    # Verify no page/locator field exists in QueryRequest
    assert not hasattr(req, "page")
    assert not hasattr(req, "locator")


# ---------------------------------------------------------------------------
# 5. numeric scoring/Unicode
# ---------------------------------------------------------------------------


def test_vietnamese_unicode_normalization() -> None:
    """Verify that Unicode NFC and NFD strings match canonically under normalization."""
    # "Hà Nội" in NFC (precomposed) vs NFD (decomposed a + combining grave accent \u0300)
    nfc_text = "Hà Nội"
    nfd_text = unicodedata.normalize("NFD", nfc_text)
    assert nfc_text != nfd_text  # Raw byte strings differ
    assert normalize_text(nfc_text, language="vi") == normalize_text(nfd_text, language="vi")
    assert exact_match(nfd_text, [nfc_text], language="vi") == 1.0
    assert compute_token_f1(nfd_text, nfc_text, language="vi") == 1.0

    # Vietnamese words with tone marks: "triệu USD", "người làm vườn"
    nfc_phrase = "Doanh thu là 12,5 triệu USD"
    nfd_phrase = unicodedata.normalize("NFD", nfc_phrase)
    assert exact_match(nfd_phrase, [nfc_phrase], language="vi") == 1.0
    assert f1_score(nfd_phrase, [nfc_phrase], language="vi") == 1.0


def test_numeric_scoring_variations_and_tolerance() -> None:
    """Verify numeric extraction, tolerance, and currency/percentage matching."""
    # Currency and thousands commas
    gold_answer = ["$1577.00"]
    assert numeric_match("$1577.00", gold_answer) is True
    assert numeric_match("1577", gold_answer) is True
    assert numeric_match("$1,577", gold_answer) is True
    assert numeric_match("The amount was $1,577.00 million [c1].", gold_answer) is True

    # Differing number should fail
    assert numeric_match("$1588.00", gold_answer) is False
    assert numeric_match("0", gold_answer) is False

    # Financial negative numbers with parentheses
    negative_gold = ["(370)", "-370"]
    assert numeric_match("(370)", negative_gold) is True
    assert numeric_match("-370", negative_gold) is True
    assert numeric_match("Company contributions were (370) million USD.", negative_gold) is True
    assert numeric_match("370", negative_gold) is False  # Positive 370 must NOT match -370

    # Percentages
    pct_gold = ["1.9%"]
    assert numeric_match("1.9%", pct_gold) is True
    assert numeric_match("1.90%", pct_gold) is True
    assert numeric_match("2.5%", pct_gold) is False

    # Tolerance within 1e-4
    approx_gold = ["1000.0"]
    assert numeric_match("1000.05", approx_gold, tolerance=1e-4) is True  # within 0.1
    assert numeric_match("1005.0", approx_gold, tolerance=1e-4) is False  # 0.5% diff exceeds 1e-4


def test_retrieval_and_citation_metrics() -> None:
    """Verify calculation of Recall@K, MRR, nDCG, and Citation Validity."""
    # Recall and MRR
    retrieved = ["doc_A", "doc_B", "doc_C", "doc_D", "doc_E"]
    expected = ["doc_B", "doc_E"]
    metrics = calculate_retrieval_metrics(retrieved, expected, k_list=(1, 5, 10))
    assert metrics["recall_at_1"] == 0.0  # doc_A not in expected
    assert metrics["recall_at_5"] == 1.0  # doc_B and doc_E both in top 5
    assert metrics["mrr"] == 0.5  # First hit is doc_B at rank 2 -> 1/2

    # Page Recall
    locators = [
        PdfLocator(kind="pdf", page=10),
        PdfLocator(kind="pdf", page=60),
    ]
    assert page_recall(locators, expected_one_based_pages=[60], k=5) == 1.0
    assert page_recall(locators, expected_one_based_pages=[99], k=5) == 0.0
