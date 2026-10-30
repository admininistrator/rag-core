"""Evaluation metrics for RAG retrieval, generation, citation, and numeric verification."""

import math
import re
import unicodedata
from collections import Counter
from typing import Any

from rag_core.contracts.v1 import PdfLocator, QueryResponse


def normalize_text(text: str, language: str = "en") -> str:
    """Normalize text with Unicode NFKC, lowercasing, punctuation, and whitespace handling.

    Preserves Vietnamese tone marks and diacritics canonically (NFC/NFKC).
    Preserves numerical decimal points and signs while removing surrounding punctuation.
    """
    # 1. Canonical Unicode normalization
    normalized = unicodedata.normalize("NFKC", text)

    # 2. Lowercase
    lowered = normalized.lower()

    # 3. Remove English articles
    if language == "en":
        lowered = re.sub(r"\b(a|an|the)\b", " ", lowered)

    # 4. Remove punctuation except numbers, decimal points, and minus signs
    # Replace citation tags like [c1], [c2] with space
    cleaned = re.sub(r"\[c[1-9][0-9]*\]", " ", lowered)

    # Replace punctuation characters with space, but keep periods and commas between digits
    # and keep characters in Unicode letter/number categories
    chars: list[str] = []
    for i, ch in enumerate(cleaned):
        if (
            ch.isalnum()
            or ch.isspace()
            or (
                ch in (".", ",")
                and 0 < i < len(cleaned) - 1
                and cleaned[i - 1].isdigit()
                and cleaned[i + 1].isdigit()
            )
            or (ch == "-" and i < len(cleaned) - 1 and cleaned[i + 1].isdigit())
        ):
            chars.append(ch)
        else:
            chars.append(" ")

    result = "".join(chars)
    # 5. Collapse whitespace
    return re.sub(r"\s+", " ", result).strip()


def compute_token_f1(prediction: str, gold_answer: str, language: str = "en") -> float:
    """Compute token-level F1 score between prediction and gold answer."""
    pred_tokens = normalize_text(prediction, language=language).split()
    gold_tokens = normalize_text(gold_answer, language=language).split()

    if not pred_tokens and not gold_tokens:
        return 1.0
    if not pred_tokens or not gold_tokens:
        return 0.0

    common = Counter(pred_tokens) & Counter(gold_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        return 0.0

    precision = num_same / len(pred_tokens)
    recall = num_same / len(gold_tokens)
    return (2 * precision * recall) / (precision + recall)


def f1_score(prediction: str, gold_answers: list[str], language: str = "en") -> float:
    """Maximum token F1 score across all acceptable gold answers."""
    if not gold_answers:
        return 0.0
    return max(compute_token_f1(prediction, gold, language=language) for gold in gold_answers)


def extract_numbers(text: str) -> list[tuple[float, str]]:
    """Extract numeric values, signs, and units from text.

    Supports:
    - Financial negative notation: (370) or ($1,577.00) -> -370.0, -1577.0
    - Currencies: $, €, £, ¥, USD, VND
    - Thousands commas: 1,577.00 -> 1577.0
    - Vietnamese decimal comma: 12,5 -> 12.5
    - Percentages: 1.9% -> 1.9, unit='%'
    """
    results: list[tuple[float, str]] = []

    # 1. Replace parenthesized negative numbers like (370) or ($1,577) with -370 or -$1,577
    transformed = re.sub(
        r"\(\s*([\$€£¥]?\s*[\d,]+(?:\.\d+)?|\d+(?:,\d+)?)\s*(%|[a-zA-Z]+)?\s*\)",
        r"-\1\2",
        text,
    )

    # 2. Pattern to find numbers with optional signs, currencies, and units
    pattern = (
        r"([+-]?)\s*[\$€£¥]?\s*"
        r"(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+,\d+|\d+(?:\.\d+)?)\s*"
        r"(%|[a-zA-Z]+)?"
    )

    for m in re.finditer(pattern, transformed):
        sign = -1.0 if m.group(1) == "-" else 1.0
        num_str = m.group(2)
        unit = (m.group(3) or "").strip().lower()

        if not num_str:
            continue

        # Convert comma to dot if Vietnamese decimal (e.g. 12,5)
        if "," in num_str and "." not in num_str:
            parts = num_str.split(",")
            if len(parts) == 2 and len(parts[1]) in (1, 2):
                num_str = f"{parts[0]}.{parts[1]}"
            else:
                num_str = num_str.replace(",", "")
        else:
            num_str = num_str.replace(",", "")

        try:
            val = sign * float(num_str)
            results.append((val, unit))
        except ValueError:
            continue

    return results


def numeric_match(prediction: str, gold_answers: list[str], tolerance: float = 1e-4) -> bool:
    """Check if prediction contains a numeric value matching any gold answer within tolerance.

    Returns False if gold answers contain no numbers.
    """
    pred_nums = extract_numbers(prediction)
    if not pred_nums:
        return False

    for gold in gold_answers:
        gold_nums = extract_numbers(gold)
        if not gold_nums:
            continue

        for gold_val, gold_unit in gold_nums:
            for pred_val, pred_unit in pred_nums:
                # Compare units if both are specified (e.g. % must match %)
                if gold_unit and pred_unit and gold_unit != pred_unit:
                    continue

                abs_diff = abs(pred_val - gold_val)
                allowed_tol = max(tolerance * abs(gold_val), tolerance)
                if abs_diff <= allowed_tol:
                    return True

    return False


def exact_match(prediction: str, gold_answers: list[str], language: str = "en") -> float:
    """Exact match scoring with text normalization and numeric tolerance fallback."""
    if not gold_answers:
        return 0.0

    norm_pred = normalize_text(prediction, language=language)
    for gold in gold_answers:
        norm_gold = normalize_text(gold, language=language)
        if norm_pred == norm_gold:
            return 1.0
        # If prediction contains normalized gold or vice-versa for brief answers
        if norm_gold and norm_gold in norm_pred.split():
            return 1.0

    # Fallback to numeric match if numbers are present
    if numeric_match(prediction, gold_answers):
        return 1.0

    return 0.0


def calculate_retrieval_metrics(
    retrieved_docs: list[str],
    expected_docs: list[str],
    k_list: tuple[int, ...] = (1, 5, 10, 20),
) -> dict[str, float]:
    """Compute Hit@K, Recall@K, MRR, and nDCG@K for retrieved document identifiers."""
    metrics: dict[str, float] = {}
    expected_set = set(expected_docs)
    if not expected_set:
        return {f"recall_at_{k}": 1.0 for k in k_list} | {"mrr": 1.0, "ndcg_at_10": 1.0}

    # Hit@K and Recall@K
    for k in k_list:
        top_k = retrieved_docs[:k]
        hits = expected_set & set(top_k)
        metrics[f"recall_at_{k}"] = len(hits) / len(expected_set)

    # MRR (Mean Reciprocal Rank)
    mrr = 0.0
    for idx, doc in enumerate(retrieved_docs, start=1):
        if doc in expected_set:
            mrr = 1.0 / idx
            break
    metrics["mrr"] = mrr

    # nDCG@10 (binary relevance)
    dcg = 0.0
    idcg = sum(1.0 / math.log2(i + 1) for i in range(1, min(len(expected_set), 10) + 1))
    for idx, doc in enumerate(retrieved_docs[:10], start=1):
        if doc in expected_set:
            dcg += 1.0 / math.log2(idx + 1)
    metrics["ndcg_at_10"] = dcg / idcg if idcg > 0 else 0.0

    return metrics


def supporting_document_recall(
    retrieved_docs: list[str],
    expected_docs: list[str],
    k: int = 10,
) -> float:
    """Measure fraction of multi-hop supporting documents successfully retrieved within top-K."""
    if not expected_docs:
        return 1.0
    hits = set(expected_docs) & set(retrieved_docs[:k])
    return len(hits) / len(expected_docs)


def page_recall(
    retrieved_locators: list[Any],
    expected_one_based_pages: list[int],
    k: int = 10,
) -> float:
    """Calculate whether any of the expected one-based pages are in the top-K retrieved PdfLocators."""
    if not expected_one_based_pages:
        return 1.0

    exp_set = set(expected_one_based_pages)
    for loc in retrieved_locators[:k]:
        if isinstance(loc, PdfLocator) or getattr(loc, "kind", None) == "pdf":
            page = getattr(loc, "page", None)
            if page in exp_set:
                return 1.0

    return 0.0


def citation_validity(response: QueryResponse | Any) -> float:
    """Verify citation validity: all citations [cN] in answer text exist in response.citations.

    Returns 1.0 if all cited IDs are valid, 0.0 otherwise.
    """
    if not hasattr(response, "answer") or not hasattr(response, "citations"):
        return 0.0

    referenced_ids = set(re.findall(r"\[(c[1-9][0-9]*)\]", response.answer))
    if not referenced_ids and getattr(response, "answerability", None) == "supported":
        # Supported answer must cite at least one citation
        return 0.0

    allowed_ids = {c.id for c in response.citations}
    if not referenced_ids.issubset(allowed_ids):
        return 0.0

    return 1.0
