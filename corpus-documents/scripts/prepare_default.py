"""Prepare HotpotQA paragraphs and evaluator-only gold; never ingest or retrieve."""

from __future__ import annotations

import hashlib
import json
import os
import random
import re
import shutil
import uuid
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from common import (
    APPROVED_HF_REVISION,
    CORPUS_ROOT,
    CorpusError,
    atomic_write,
    download,
    read_json,
    read_jsonl,
    safe_path,
    sha256_file,
    validate_qa_records,
    write_json,
)

SEED = 42
TARGET_QA = 100
RAW_PATH = "raw/hotpot_dev_distractor_v1.json"
PARQUET_PATH = "raw/hf-hotpotqa-distractor-validation.parquet"
QA_PATH = "qa/eval.jsonl"
INDEX_PATH = "qa/documents.json"
REPORT_PATH = "qa/preparation.json"
ALGORITHM = "balanced-present-type-level-v1"


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode(
        "utf-8"
    )


def digest(value: Any) -> str:
    content = json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def paragraph_id(title: str, sentences: list[str]) -> str:
    # Title alone is not an identity. Preserve exact paragraph text, including spaces.
    return "hotpot_" + digest([title, "".join(sentences)])


def source_records(path: Path) -> list[dict[str, Any]]:
    records = read_json(path)
    if not isinstance(records, list) or not records:
        raise CorpusError("HotpotQA source must be a nonempty JSON array")
    identifiers: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            raise CorpusError("HotpotQA examples must be objects")
        identifier = record.get("_id")
        if (
            not isinstance(identifier, str)
            or not re.fullmatch(r"[A-Za-z0-9_-]+", identifier)
            or identifier in identifiers
        ):
            raise CorpusError("HotpotQA source IDs must be unique portable identifiers")
        identifiers.add(identifier)
        if not _nonempty(record.get("question")) or not _nonempty(record.get("answer")):
            raise CorpusError("HotpotQA original question/answer must be nonempty strings")
        if record.get("type") not in ("bridge", "comparison"):
            raise CorpusError("HotpotQA question type is unsupported")
        if record.get("level") not in ("easy", "medium", "hard"):
            raise CorpusError("HotpotQA difficulty is unsupported; do not relabel source gold")
        context = record.get("context")
        if not isinstance(context, list) or len(context) < 2:
            raise CorpusError("HotpotQA context must include multiple paragraphs")
        by_title: dict[str, list[str]] = {}
        for paragraph in context:
            if not isinstance(paragraph, list) or len(paragraph) != 2:
                raise CorpusError("HotpotQA context paragraph must be [title, sentences]")
            title, sentences = paragraph
            if (
                not _nonempty(title)
                or not isinstance(sentences, list)
                or not sentences
                or any(not isinstance(sentence, str) for sentence in sentences)
                or not "".join(sentences).strip()
            ):
                raise CorpusError("HotpotQA paragraph title/text must be nonempty")
            # Within one QA, a gold title cannot distinguish two different paragraphs.
            if title in by_title and by_title[title] != sentences:
                raise CorpusError("Ambiguous same-title paragraphs within a HotpotQA example")
            by_title[title] = sentences
        facts = record.get("supporting_facts")
        if not isinstance(facts, list) or not facts:
            raise CorpusError("HotpotQA original supporting facts must be nonempty")
        for fact in facts:
            if (
                not isinstance(fact, list)
                or len(fact) != 2
                or not isinstance(fact[0], str)
                or type(fact[1]) is not int
                or fact[0] not in by_title
            ):
                raise CorpusError("HotpotQA supporting fact has no valid title/integer sentence index")
    return records


def annotation_anomalies(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for record in records:
        context = dict(record["context"])
        for title, index in record["supporting_facts"]:
            count = len(context[title])
            if not 0 <= index < count:
                result.append({
                    "source_id": record["_id"], "title": title,
                    "sent_id": index, "sentence_count": count,
                })
    return result


def validate_download(path: Path) -> None:
    if len(source_records(path)) < TARGET_QA:
        raise CorpusError("HotpotQA source cannot supply the 100-QA target")


def parquet_records(path: Path) -> list[dict[str, Any]]:
    # Dev-only Parquet reader; no datasets loader, pandas, baseline or model setup.
    import pyarrow.parquet as pq  # type: ignore[import-untyped]

    try:
        parquet = pq.ParquetFile(path)
        expected_columns = {"id", "question", "answer", "type", "level", "supporting_facts", "context"}
        if set(parquet.schema_arrow.names) != expected_columns:
            raise CorpusError("Approved HF Parquet columns differ from the expected semantic fields")
        result = []
        for batch in parquet.iter_batches(batch_size=1024, use_threads=False):
            for row in batch.to_pylist():
                facts, context = row["supporting_facts"], row["context"]
                if not isinstance(facts, dict) or not isinstance(context, dict):
                    raise CorpusError("Approved HF nested facts/context must be structured objects")
                result.append(
                    {
                        "_id": row["id"], "question": row["question"], "answer": row["answer"],
                        "type": row["type"], "level": row["level"],
                        "supporting_facts": [list(pair) for pair in zip(facts["title"], facts["sent_id"], strict=True)],
                        "context": [list(pair) for pair in zip(context["title"], context["sentences"], strict=True)],
                    }
                )
        return result
    except CorpusError:
        raise
    except (OSError, ValueError, TypeError, KeyError):
        raise CorpusError("Approved HF Parquet could not be decoded with aligned semantic fields") from None


def validate_parquet(path: Path) -> None:
    records = parquet_records(path)
    if len(records) < TARGET_QA:
        raise CorpusError("Approved HF source cannot supply the 100-QA target")
    # Reuse strict source semantics before the domain can be published.
    # This temporary conversion is below the same ignored staging directory.
    temporary = path.with_name(path.name + ".semantic-check.json")
    try:
        atomic_write(temporary, [json_bytes(records)], validate=validate_download)
    finally:
        temporary.unlink(missing_ok=True)


def distribution(records: list[dict[str, Any]]) -> dict[str, Any]:
    strata = Counter(f"{r['type']}/{r['level']}" for r in records)
    return {
        "by_type": dict(sorted(Counter(r["type"] for r in records).items())),
        "by_level": dict(sorted(Counter(r["level"] for r in records).items())),
        "strata": dict(sorted(strata.items())),
    }


def sample_records(
    records: list[dict[str, Any]], *, size: int = TARGET_QA, seed: int = SEED
) -> list[dict[str, Any]]:
    if not 0 < size <= len(records):
        raise CorpusError("HotpotQA source cannot supply the requested subset")
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for record in sorted(records, key=lambda item: item["_id"]):
        groups[(record["type"], record["level"])].append(record)
    keys = sorted(groups)
    quotas = dict.fromkeys(keys, 0)
    # Equal round-robin quotas over available strata; redistribute exhausted capacities.
    remaining = size
    while remaining:
        for key in keys:
            if quotas[key] < len(groups[key]):
                quotas[key] += 1
                remaining -= 1
                if not remaining:
                    break
    rng = random.Random(seed)
    selected = [record for key in keys for record in rng.sample(groups[key], quotas[key])]
    return sorted(selected, key=lambda record: record["_id"])


def build_artifacts(
    records: list[dict[str, Any]], source_sha256: str, *, size: int = TARGET_QA, seed: int = SEED,
    converted_json_sha256: str | None = None,
) -> tuple[dict[str, bytes], dict[str, Any]]:
    selected = sample_records(records, size=size, seed=seed)
    if annotation_anomalies(selected):
        raise CorpusError("Selected HotpotQA supporting annotation has an out-of-range sentence; do not resample")
    contents: dict[str, bytes] = {}
    documents: dict[str, dict[str, Any]] = {}
    qa: list[dict[str, Any]] = []
    context_instances = 0
    for record in selected:
        by_title: dict[str, str] = {}
        context_ids: list[str] = []
        for title, sentences in record["context"]:
            context_instances += 1
            identifier = paragraph_id(title, sentences)
            paragraph = "".join(sentences)
            # No question IDs, answer, supporting flag, or other evaluator metadata here.
            rendered = (
                "---\n"
                f"document_id: {identifier}\n"
                f"title: {json.dumps(title, ensure_ascii=False)}\n"
                "source_dataset: hotpotqa\n"
                "---\n\n" + paragraph + "\n"
            ).encode("utf-8")
            file_path = f"documents/{identifier}.md"
            if file_path in contents and contents[file_path] != rendered:
                raise CorpusError("HotpotQA paragraph digest collision")
            contents[file_path] = rendered
            if identifier not in documents:
                documents[identifier] = {
                    "document_id": identifier,
                    "title": title,
                    "path": identifier + ".md",
                    "sha256": hashlib.sha256(rendered).hexdigest(),
                    "paragraph_sha256": hashlib.sha256(paragraph.encode("utf-8")).hexdigest(),
                    "source_question_ids": [],
                }
            origins = documents[identifier]["source_question_ids"]
            if record["_id"] not in origins:
                origins.append(record["_id"])
            by_title[title] = identifier
            if identifier not in context_ids:
                context_ids.append(identifier)
        expected = list(dict.fromkeys(by_title[title] for title, _ in record["supporting_facts"]))
        qa.append(
            {
                "id": "default_" + record["_id"],
                "domain": "default",
                "source_id": record["_id"],
                "question": record["question"],
                "expected_answers": [record["answer"]],
                "expected_documents": expected,
                "supporting_facts": record["supporting_facts"],
                "category": record["type"],
                "difficulty": record["level"],
                "language": "en",
                "answerable": True,
                "source_dataset": "hotpotqa",
                "context_documents": context_ids,
            }
        )
    report = {
        "schema_version": 1,
        "algorithm": ALGORITHM,
        "seed": seed,
        "target_qa": size,
        "source_sha256": source_sha256,
        "source_format": "HF Parquet distractor/validation",
        "source_revision": APPROVED_HF_REVISION,
        "converted_json_sha256": converted_json_sha256,
        "cmu_byte_comparison": "unavailable: canonical CMU HTTP/HTTPS GET timed out; user-approved HF derivative",
        "source_qa_count": len(records),
        "source_distribution": distribution(records),
        "source_annotation_anomalies": annotation_anomalies(records),
        "selected_annotation_anomalies": [],
        "selected_distribution": distribution(selected),
        "selected_source_ids": [record["_id"] for record in selected],
        "selected_ids_sha256": digest([record["_id"] for record in selected]),
        "qa_count": len(qa),
        "document_count": len(documents),
        "context_paragraph_instances": context_instances,
        "deduplicated_instances": context_instances - len(documents),
        "normalization_changes": (
            "Seed42 stratified subset; preserve original gold/type/level/supporting facts. "
            "Concatenate original sentences without rewriting; title+text content IDs; "
            "all context including distractors materialized. Provenance/gold stay in qa/."
        ),
        "license": "CC-BY-SA-4.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "attribution": "Yang et al. (2018), HotpotQA; original Wikipedia titles preserved.",
    }
    contents[QA_PATH] = b"".join(
        (json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
        for record in qa
    )
    contents[INDEX_PATH] = json_bytes([documents[key] for key in sorted(documents)])
    contents[REPORT_PATH] = json_bytes(report)
    return contents, report


def _tree_files(root: Path) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for parent, directories, files in os.walk(root, followlinks=False):
        for name in directories + files:
            path = Path(parent) / name
            if path.is_symlink() or path.is_junction():
                raise CorpusError("Default corpus tree cannot contain links or junctions")
        for name in files:
            relative = (Path(parent) / name).relative_to(root).as_posix()
            result[relative] = safe_path(root, relative, must_exist=True)
    return result


def validate_default(domain_root: Path) -> dict[str, Any]:
    from validate_corpus import validate_manifest

    manifest = read_json(safe_path(domain_root, "manifest.json", must_exist=True))
    validate_manifest(manifest)
    if manifest["domain"] != "default" or manifest["status"] != "ready":
        raise CorpusError("default: corpus is not ready")
    raw = safe_path(domain_root, RAW_PATH, must_exist=True)
    parquet = safe_path(domain_root, PARQUET_PATH, must_exist=True)
    if sha256_file(parquet) != manifest["sources"][0]["expected_sha256"]:
        raise CorpusError("Approved source bytes differ from the published Parquet checksum")
    if raw.read_bytes() != json_bytes(parquet_records(parquet)):
        raise CorpusError("Converted JSON semantic fields differ from the pinned HF Parquet")
    validate_download(raw)
    contents, report = build_artifacts(
        source_records(raw), sha256_file(parquet), converted_json_sha256=sha256_file(raw)
    )
    if manifest["qa_count"] != report["qa_count"] or manifest["document_count"] != report[
        "document_count"
    ]:
        raise CorpusError("Default manifest counts differ from actual artifacts")
    expected_paths = {"manifest.json", RAW_PATH, PARQUET_PATH, *contents}
    if set(_tree_files(domain_root)) != expected_paths:
        raise CorpusError("Default corpus has missing, duplicate, or unmanaged artifacts")
    for reference, expected_bytes in contents.items():
        if safe_path(domain_root, reference, must_exist=True).read_bytes() != expected_bytes:
            raise CorpusError(f"Default artifact differs from original source: {reference}")
    artifacts = manifest["artifacts"]
    if {item["path"] for item in artifacts} != {RAW_PATH, PARQUET_PATH, *contents}:
        raise CorpusError("Default receipts differ from the complete materialized corpus")
    actual_checksums = {}
    for artifact in artifacts:
        path = safe_path(domain_root, artifact["path"], must_exist=True)
        checksum = sha256_file(path)
        if (
            checksum != artifact["sha256"]
            or path.stat().st_size != artifact["bytes"]
            or not artifact["path"].startswith(artifact["role"] + "/")
        ):
            raise CorpusError("Default receipt hash, bytes, or role differs from actual file")
        actual_checksums[artifact["path"]] = checksum
    if manifest["checksum"] != actual_checksums:
        raise CorpusError("Default checksum map differs from actual artifacts")
    index = read_json(domain_root / INDEX_PATH)
    mapping = {item["document_id"]: item["path"] for item in index}
    validate_qa_records(read_jsonl(domain_root / QA_PATH), domain_root / "documents", mapping)
    return report


def _same_files(first: Path, second: Path) -> bool:
    old, new = _tree_files(first), _tree_files(second)
    return set(old) == set(new) and all(
        sha256_file(old[name]) == sha256_file(new[name]) for name in old
    )


def _publish(stage: Path, root: Path) -> None:
    """Validate before directory swap; roll back both pointers on publication failure.

    One exclusive setup lock protects writers. Directory renames are not a concurrent
    reader transaction; evaluation must run after setup completes. Staging/backup
    paths remain available if rollback itself fails. Never remove a user directory.
    """
    proposed = stage / "default"
    current = safe_path(root, "default")
    aggregate = safe_path(root, "manifest.json", must_exist=True)
    if _same_files(current, proposed) and aggregate.read_bytes() == (stage / "manifest.json").read_bytes():
        return
    backup = stage / "previous-default"
    aggregate_backup = stage / "previous-aggregate.json"
    shutil.copy2(aggregate, aggregate_backup)
    moved_old = False
    moved_new = False
    try:
        os.replace(current, backup)
        moved_old = True
        os.replace(proposed, current)
        moved_new = True
        atomic_write(aggregate, [(stage / "manifest.json").read_bytes()])
    except BaseException:
        # Restoration uses renames, never a recursive delete of published data.
        try:
            if moved_new:
                os.replace(current, proposed)
            if moved_old:
                os.replace(backup, current)
            os.replace(aggregate_backup, aggregate)
        except BaseException as rollback_error:
            raise CorpusError(
                f"Publication rollback failed; inspect retained recovery stage {stage}"
            ) from rollback_error
        raise


def prepare_default(root: Path = CORPUS_ROOT) -> dict[str, Any]:
    from validate_corpus import validate_metadata

    root = root.resolve(strict=True)
    cache = safe_path(root, ".downloads")
    cache.mkdir(exist_ok=True)
    lock = safe_path(root, ".downloads/default-setup.lock")
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise CorpusError("Default setup lock exists; inspect the active/stopped setup first") from None
    stage: Path | None = None
    succeeded = False
    try:
        validate_metadata(root)
        prior_root = safe_path(root, "default")
        prior = read_json(prior_root / "manifest.json")
        if prior["status"] == "ready":
            validate_default(prior_root)
        elif set(_tree_files(prior_root)) != {"manifest.json"}:
            raise CorpusError("Refuse to replace unrecognized existing default corpus files")
        # Inherit the repo directory ACL on Windows; private mkdtemp ACLs created
        # under an approved network process can deny later sandbox read-only checks.
        stage = cache / ("default-stage-" + uuid.uuid4().hex)
        stage.mkdir()
        destination = stage / "default"
        destination.mkdir()
        raw = safe_path(destination, RAW_PATH)
        raw.parent.mkdir()
        parquet = safe_path(destination, PARQUET_PATH)
        cache_parquet = safe_path(root, ".downloads/hf-hotpotqa-distractor-validation.parquet")
        cache_info_path = safe_path(root, ".downloads/hf-hotpotqa-download.json")
        cache_info = read_json(cache_info_path) if cache_info_path.is_file() else None
        source = prior["sources"][0]
        if cache_info and (
            not isinstance(cache_info, dict)
            or cache_info.get("url") != source["url"]
            or cache_info.get("sha256") != source["expected_sha256"]
            or not _nonempty(cache_info.get("downloaded_at"))
        ):
            raise CorpusError("Approved source cache receipt is invalid; published corpus is unchanged")
        pin = prior["checksum"].get(PARQUET_PATH)
        if pin:
            shutil.copy2(safe_path(prior_root, PARQUET_PATH, must_exist=True), parquet)
        elif cache_info and cache_parquet.is_file():
            shutil.copy2(cache_parquet, parquet)
        receipt = download(
            source["url"],
            parquet,
            expected_sha256=pin or source["expected_sha256"],
            timeout=30,
            attempts=2,
            max_bytes=128 * 1024 * 1024,
        )
        downloaded_at = receipt.downloaded_at or prior["downloaded_at"] or (
            cache_info["downloaded_at"] if cache_info else None
        )
        if receipt.downloaded_at:
            atomic_write(cache_parquet, [parquet.read_bytes()])
            write_json(cache_info_path, {
                "url": source["url"], "sha256": receipt.sha256, "bytes": receipt.byte_count,
                "downloaded_at": receipt.downloaded_at,
            })
        # The published upstream byte pin verifies transport before this semantic
        # check. Retain exact verified Parquet bytes in the failed stage for diagnosis.
        validate_parquet(parquet)
        atomic_write(raw, [json_bytes(parquet_records(parquet))], validate=validate_download)
        contents, report = build_artifacts(
            source_records(raw), receipt.sha256, converted_json_sha256=sha256_file(raw)
        )
        for reference, content in contents.items():
            atomic_write(safe_path(destination, reference), [content])
        artifacts = [
            {
                "path": reference,
                "role": reference.split("/", 1)[0],
                "sha256": sha256_file(safe_path(destination, reference, must_exist=True)),
                "bytes": safe_path(destination, reference, must_exist=True).stat().st_size,
            }
            for reference in sorted([RAW_PATH, PARQUET_PATH, *contents])
        ]
        manifest = {
            **prior,
            "status": "ready",
            "downloaded_at": downloaded_at,
            "document_count": report["document_count"],
            "qa_count": report["qa_count"],
            "checksum": {item["path"]: item["sha256"] for item in artifacts},
            "artifacts": artifacts,
            "notes": (
                "User-approved HF community derivative distractor/validation, pinned revision/Parquet SHA256. "
                "Semantic fields converted to legacy JSON; CMU byte equivalence unverified after GET timeouts. "
                "Seed42 balanced available type/level strata; source gold unchanged. "
                "All contexts/distractors in documents/; gold/provenance/report only in qa/. "
                "See qa/preparation.json for measured distributions and normalization notices."
            ),
        }
        write_json(destination / "manifest.json", manifest)
        aggregate = read_json(root / "manifest.json")
        aggregate["domains"]["default"] = {
            "manifest": "default/manifest.json",
            "status": "ready",
            "document_count": report["document_count"],
            "qa_count": report["qa_count"],
        }
        aggregate["notes"] = "Default prepared; other domains remain pending. Full corpus acceptance T08."
        write_json(stage / "manifest.json", aggregate)
        shutil.copy2(root / "source-license-inventory.json", stage / "source-license-inventory.json")
        for domain in ("document", "bilingual"):
            (stage / domain).mkdir()
            shutil.copy2(root / domain / "manifest.json", stage / domain / "manifest.json")
        validate_metadata(stage)
        validate_default(destination)
        _publish(stage, root)
        succeeded = True
        return report
    finally:
        os.close(descriptor)
        lock.unlink()
        # Failed stages are ignored forensic checkpoints, including any rollback backup.
        if succeeded and stage is not None:
            resolved = stage.resolve(strict=True)
            if not resolved.is_relative_to(cache.resolve(strict=True)) or not resolved.name.startswith(
                "default-stage-"
            ):
                raise CorpusError("Refuse to clean a staging path outside the corpus cache")
            shutil.rmtree(resolved)
