"""Evaluation gold adapters for Default, Document (FinanceBench), and Bilingual (XQuAD)."""

from typing import Any
from uuid import UUID

from rag_core.contracts.v1 import (
    Citation,
    PdfLocator,
    QueryRequest,
    SourceLocator,
)
from rag_core.evaluation.protocol import EvalSample, EvaluationLeakageError


class BaseGoldAdapter:
    """Base gold adapter interface."""

    domain: str = "default"
    api_domain: str = "default"

    def prepare_query_request(
        self,
        sample: EvalSample,
        session_id: UUID,
        document_id_map: dict[str, UUID] | None = None,
    ) -> QueryRequest:
        raise NotImplementedError

    def verify_citation(self, citation: Citation, sample: EvalSample) -> bool:
        raise NotImplementedError

    def verify_retrieved_document(self, doc_identifier: str, sample: EvalSample) -> bool:
        return doc_identifier in sample.expected_documents


class DefaultGoldAdapter(BaseGoldAdapter):
    """Gold adapter for HotpotQA Default domain."""

    domain: str = "default"
    api_domain: str = "default"

    def prepare_query_request(
        self,
        sample: EvalSample,
        session_id: UUID,
        document_id_map: dict[str, UUID] | None = None,
    ) -> QueryRequest:
        return QueryRequest(
            session_id=session_id,
            domain="default",
            question=sample.question,
            document_ids=None,
        )

    def verify_citation(self, citation: Citation, sample: EvalSample) -> bool:
        # Check if cited document filename or identifier matches expected documents
        return any(
            exp_doc in citation.filename or exp_doc in citation.chunk_id
            for exp_doc in sample.expected_documents
        )


class FinanceBenchGoldAdapter(BaseGoldAdapter):
    """Gold adapter for FinanceBench Document domain.

    FinanceBench evidence page numbers are ZERO-BASED in raw annotations.
    RAG Core uses physical ONE-BASED page numbers in PdfLocator.
    """

    domain: str = "document"
    api_domain: str = "document"
    page_indexing: str = "zero_based"

    @staticmethod
    def to_one_based_page(zero_based_page: int) -> int:
        """Convert zero-based annotation page to physical one-based page."""
        if zero_based_page < 0:
            raise ValueError(f"Page cannot be negative: {zero_based_page}")
        return zero_based_page + 1

    @staticmethod
    def to_zero_based_page(one_based_page: int) -> int:
        """Convert physical one-based page to zero-based annotation page."""
        if one_based_page < 1:
            raise ValueError(f"Physical page must be >= 1: {one_based_page}")
        return one_based_page - 1

    def prepare_query_request(
        self,
        sample: EvalSample,
        session_id: UUID,
        document_id_map: dict[str, UUID] | None = None,
    ) -> QueryRequest:
        if not document_id_map:
            raise ValueError("document_id_map is required for Document domain queries")

        # Map expected document names to session UUIDs
        doc_uuids: list[UUID] = []
        for exp_doc in sample.expected_documents:
            # Handle with or without .pdf extension
            norm_name = exp_doc if exp_doc.endswith(".pdf") else f"{exp_doc}.pdf"
            stem_name = exp_doc.removesuffix(".pdf")
            uuid_val = document_id_map.get(norm_name) or document_id_map.get(stem_name)
            if uuid_val is None:
                raise KeyError(
                    f"Expected document '{exp_doc}' not found in session document_id_map"
                )
            if uuid_val not in doc_uuids:
                doc_uuids.append(uuid_val)

        # Anti-leakage pitfall check: NEVER pre-filter by page in the query request!
        # The query must only specify document_ids and the question.
        return QueryRequest(
            session_id=session_id,
            domain="document",
            question=sample.question,
            document_ids=doc_uuids,
        )

    def verify_citation(self, citation: Citation, sample: EvalSample) -> bool:
        """Verify that citation points to the expected document and expected physical page."""
        if citation.locator.kind != "pdf":
            return False

        physical_page = citation.locator.page
        citation_filename = citation.filename.removesuffix(".pdf")

        for ev in sample.evidence:
            ev_doc = ev.document.removesuffix(".pdf")
            if ev_doc in citation_filename or ev_doc in citation.chunk_id:
                if ev.page is not None:
                    expected_physical_page = self.to_one_based_page(ev.page)
                    if physical_page == expected_physical_page:
                        return True
                else:
                    return True

        return False

    def verify_retrieved_page(self, locator: SourceLocator | Any, sample: EvalSample) -> bool:
        """Check if retrieved locator hits one of the expected physical pages."""
        if not isinstance(locator, PdfLocator):
            return False

        physical_page = locator.page
        for ev in sample.evidence:
            if ev.page is not None and self.to_one_based_page(ev.page) == physical_page:
                return True
        return False


class BilingualGoldAdapter(BaseGoldAdapter):
    """Gold adapter for XQuAD Bilingual domain.

    Maps evaluation domain 'bilingual' to API domain 'multilingual', and
    enforces real cross-lingual corpus and answer language filters.
    """

    domain: str = "bilingual"
    api_domain: str = "multilingual"
    is_unanswerable_benchmark: bool = False

    VALID_SLICES = ("en_en", "vi_vi", "vi_en", "en_vi")

    def prepare_query_request(
        self,
        sample: EvalSample,
        session_id: UUID,
        document_id_map: dict[str, UUID] | None = None,
    ) -> QueryRequest:
        slice_name = sample.evaluation_slice
        if slice_name and slice_name not in self.VALID_SLICES:
            raise EvaluationLeakageError(f"Unknown bilingual slice: {slice_name}")

        # Real cross-lingual filters
        corpus_langs = sample.corpus_languages or ["en"]
        ans_lang = sample.answer_language or "en"

        return QueryRequest(
            session_id=session_id,
            domain="multilingual",  # Mapped from 'bilingual' to API 'multilingual'
            question=sample.question,
            corpus_languages=corpus_langs,  # Real filter!
            answer_language=ans_lang,  # Real filter!
            document_ids=None,
        )

    def verify_citation(self, citation: Citation, sample: EvalSample) -> bool:
        return any(
            exp_doc in citation.filename or exp_doc in citation.chunk_id
            for exp_doc in sample.expected_documents
        )
