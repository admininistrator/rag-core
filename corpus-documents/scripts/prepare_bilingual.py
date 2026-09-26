"""Prepare complete aligned XQuAD EN/VI paragraphs and evaluator-only QA slices."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import uuid
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from common import (
    CORPUS_ROOT,
    CorpusError,
    atomic_write,
    download,
    git_blob_file,
    read_json,
    read_jsonl,
    safe_path,
    sha256_file,
    validate_qa_records,
    write_json,
)

REVISION = "7d30520c717524000f0d9d2f9c10a069acd9d285"
RAW_EN = "raw/xquad.en.json"
RAW_VI = "raw/xquad.vi.json"
SLICES = ("en_en", "vi_vi", "vi_en", "en_vi")
_SOURCE_FIELDS = {"version", "data"}


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")


def _digest(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def parallel_group_id(title: str, qa_ids: Iterable[str]) -> str:
    return "xquad_parallel_" + _digest([title, sorted(qa_ids)])


def _document_id(language: str, group: str) -> str:
    return f"xquad_{language}_{group.removeprefix('xquad_parallel_')}"


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_source_file(path: Path, language: str) -> None:
    source_records(read_json(path), language)


def source_records(value: Any, language: str) -> list[dict[str, Any]]:
    if language not in {"en", "vi"}:
        raise CorpusError("XQuAD language must be en or vi")
    if not isinstance(value, dict) or set(value) != _SOURCE_FIELDS or value["version"] != "1.1":
        raise CorpusError("XQuAD source must match the pinned SQuAD v1.1 structure")
    articles = value["data"]
    if not isinstance(articles, list) or not articles:
        raise CorpusError("XQuAD source articles must be a nonempty list")
    records: list[dict[str, Any]] = []
    qa_ids: set[str] = set()
    paragraph_keys: set[tuple[str, tuple[str, ...]]] = set()
    for article in articles:
        if not isinstance(article, dict) or set(article) != {"title", "paragraphs"}:
            raise CorpusError("XQuAD article structure is invalid")
        title, paragraphs = article["title"], article["paragraphs"]
        if not _nonempty(title) or not isinstance(paragraphs, list) or not paragraphs:
            raise CorpusError("XQuAD article title/paragraphs are empty")
        for paragraph in paragraphs:
            if not isinstance(paragraph, dict) or set(paragraph) != {"context", "qas"}:
                raise CorpusError("XQuAD paragraph structure is invalid")
            context, qas = paragraph["context"], paragraph["qas"]
            if not _nonempty(context) or not isinstance(qas, list) or not qas:
                raise CorpusError("XQuAD paragraph context/QA list is empty")
            normalized_qas = []
            local_ids: set[str] = set()
            for qa in qas:
                if not isinstance(qa, dict) or set(qa) != {"id", "question", "answers"}:
                    raise CorpusError("XQuAD QA structure is invalid")
                identifier, question, answers = qa["id"], qa["question"], qa["answers"]
                if not _nonempty(identifier) or identifier in qa_ids or identifier in local_ids:
                    raise CorpusError("XQuAD QA IDs must be unique nonempty strings")
                if not _nonempty(question) or not isinstance(answers, list) or not answers:
                    raise CorpusError("XQuAD QA question and answers must be nonempty")
                local_ids.add(identifier)
                qa_ids.add(identifier)
                normalized_answers = []
                for answer in answers:
                    if not isinstance(answer, dict) or set(answer) != {"text", "answer_start"}:
                        raise CorpusError("XQuAD answer structure is invalid")
                    text, start = answer["text"], answer["answer_start"]
                    if not _nonempty(text) or type(start) is not int or start < 0:
                        raise CorpusError("XQuAD answer text/offset is invalid")
                    if (
                        start + len(text) > len(context)
                        or context[start : start + len(text)] != text
                    ):
                        raise CorpusError("XQuAD answer span does not match its source context")
                    normalized_answers.append({"text": text, "answer_start": start})
                normalized_qas.append(
                    {"id": identifier, "question": question, "answers": normalized_answers}
                )
            key = (title, tuple(sorted(local_ids)))
            if key in paragraph_keys:
                raise CorpusError("XQuAD has duplicate title/QA paragraph identity")
            paragraph_keys.add(key)
            records.append(
                {"title": title, "context": context, "qas": normalized_qas, "language": language}
            )
    return records


def align_paragraphs(
    english: list[dict[str, Any]], vietnamese: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    def keyed(
        records: list[dict[str, Any]], language: str
    ) -> dict[tuple[str, tuple[str, ...]], dict[str, Any]]:
        result = {}
        for record in records:
            if record["language"] != language:
                raise CorpusError("XQuAD paragraph language label is inconsistent")
            key = (record["title"], tuple(sorted(qa["id"] for qa in record["qas"])))
            if key in result:
                raise CorpusError("XQuAD paragraph alignment key is not unique")
            result[key] = record
        return result

    en_map, vi_map = keyed(english, "en"), keyed(vietnamese, "vi")
    if en_map.keys() != vi_map.keys():
        en_qas = {qa["id"] for row in english for qa in row["qas"]}
        vi_qas = {qa["id"] for row in vietnamese for qa in row["qas"]}
        if en_qas != vi_qas:
            raise CorpusError("XQuAD QA ID counterpart sets differ")
        en_titles = {key[0] for key in en_map}
        vi_titles = {key[0] for key in vi_map}
        if en_titles != vi_titles:
            raise CorpusError("XQuAD parallel article title sets differ")
        raise CorpusError("XQuAD paragraph title/QA ID structures do not align")
    aligned = []
    for title, qa_ids in sorted(en_map):
        group = parallel_group_id(title, qa_ids)
        aligned.append(
            {
                "title": title,
                "qa_ids": list(qa_ids),
                "parallel_group_id": group,
                "en": en_map[(title, qa_ids)],
                "vi": vi_map[(title, qa_ids)],
            }
        )
    return aligned


def _document_bytes(language: str, title: str, group: str, context: str) -> bytes:
    header = {
        "document_id": _document_id(language, group),
        "parallel_group_id": group,
        "language": language,
        "title": title,
        "source_dataset": "xquad",
    }
    return (
        "---\n"
        + "".join(
            f"{key}: {json.dumps(value, ensure_ascii=False)}\n" for key, value in header.items()
        )
        + "---\n\n"
        + context
        + "\n"
    ).encode("utf-8")


def build_artifacts(
    english: list[dict[str, Any]],
    vietnamese: list[dict[str, Any]],
    groups: list[dict[str, Any]],
    *,
    source_hashes: dict[str, str],
) -> tuple[dict[str, bytes], dict[str, Any]]:
    if set(source_hashes) != {"en", "vi"} or any(
        not re.fullmatch(r"[0-9a-f]{64}", value) for value in source_hashes.values()
    ):
        raise CorpusError("XQuAD source SHA256 receipts are incomplete")
    contents: dict[str, bytes] = {}
    docs_by_language: dict[str, dict[str, dict[str, Any]]] = {"en": {}, "vi": {}}
    qa_by_language: dict[str, dict[str, dict[str, Any]]] = {"en": {}, "vi": {}}
    for group in groups:
        title, group_id = group["title"], group["parallel_group_id"]
        for language in ("en", "vi"):
            paragraph = group[language]
            doc_id = _document_id(language, group_id)
            path = f"documents/{language}/{doc_id}.md"
            document = _document_bytes(language, title, group_id, paragraph["context"])
            if path in contents:
                raise CorpusError("XQuAD generated duplicate document path")
            contents[path] = document
            docs_by_language[language][doc_id] = {
                "document_id": doc_id,
                "parallel_group_id": group_id,
                "language": language,
                "title": title,
                "path": f"{doc_id}.md",
                "sha256": hashlib.sha256(document).hexdigest(),
                "paragraph_sha256": hashlib.sha256(
                    paragraph["context"].encode("utf-8")
                ).hexdigest(),
            }
            for qa in paragraph["qas"]:
                qa_by_language[language][qa["id"]] = qa
    if len(qa_by_language["en"]) != len(qa_by_language["vi"]):
        raise CorpusError("XQuAD QA cardinality differs across languages")
    slice_inputs = {
        "en_en": ("en", "en"),
        "vi_vi": ("vi", "vi"),
        "vi_en": ("vi", "en"),
        "en_vi": ("en", "vi"),
    }
    slice_counts: dict[str, int] = {}
    for slice_name, (question_language, corpus_language) in slice_inputs.items():
        rows = []
        target_by_group = {item["parallel_group_id"]: item["qa_ids"] for item in groups}
        source_to_group = {
            qa_id: group_id for group_id, ids in target_by_group.items() for qa_id in ids
        }
        for source_qa_id in sorted(qa_by_language[question_language]):
            question = qa_by_language[question_language][source_qa_id]
            answer_qa = qa_by_language[corpus_language][source_qa_id]
            group_id = source_to_group[source_qa_id]
            doc_id = _document_id(corpus_language, group_id)
            rows.append(
                {
                    "id": f"bilingual_{slice_name}_{source_qa_id}",
                    "domain": "bilingual",
                    "source_qa_id": source_qa_id,
                    "question": question["question"],
                    "question_language": question_language,
                    "corpus_language": corpus_language,
                    "answer_language": corpus_language,
                    "expected_answers": [answer["text"] for answer in answer_qa["answers"]],
                    "expected_documents": [doc_id],
                    "evidence": [
                        {"document": doc_id, "text": answer["text"]}
                        for answer in answer_qa["answers"]
                    ],
                    "parallel_group_id": group_id,
                    "evaluation_slice": slice_name,
                    "answerable": True,
                    "source_dataset": "xquad",
                }
            )
        contents[f"qa/{slice_name}.jsonl"] = b"".join(
            (json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
            for row in rows
        )
        slice_counts[slice_name] = len(rows)
    for language in ("en", "vi"):
        contents[f"qa/documents_{language}.jsonl"] = b"".join(
            (
                json.dumps(docs_by_language[language][key], ensure_ascii=False, allow_nan=False)
                + "\n"
            ).encode("utf-8")
            for key in sorted(docs_by_language[language])
        )
    report = {
        "schema_version": 1,
        "source_revision": REVISION,
        "source_sha256": source_hashes,
        "alignment": "article title + exact sorted counterpart QA ID set; paragraph order ignored",
        "parallel_group_id_algorithm": "sha256(title, sorted source QA IDs)",
        "parallel_group_count": len(groups),
        "paragraph_count_by_language": {
            language: len(docs_by_language[language]) for language in ("en", "vi")
        },
        "qa_count_by_slice": slice_counts,
        "paragraph_group_ids": [item["parallel_group_id"] for item in groups],
        "normalization_changes": "SQuAD fields are normalized into language-specific documents and four evaluator-only slices; source questions/answers are preserved verbatim, no translation or subset selection.",
        "license": "CC-BY-SA-4.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "attribution": "Artetxe, Ruder and Yogatama (2019), XQuAD; EN derives from SQuAD v1.1 and VI is professionally translated.",
    }
    contents["qa/preparation.json"] = json_bytes(report)
    return contents, report


def _tree_files(root: Path) -> dict[str, Path]:
    result = {}
    for parent, directories, files in os.walk(root, followlinks=False):
        for name in directories + files:
            path = Path(parent) / name
            if path.is_symlink() or path.is_junction():
                raise CorpusError("Bilingual corpus cannot contain links or junctions")
        for name in files:
            relative = (Path(parent) / name).relative_to(root).as_posix()
            result[relative] = safe_path(root, relative, must_exist=True)
    return result


def validate_bilingual(domain_root: Path) -> dict[str, Any]:
    from validate_corpus import validate_manifest

    manifest = read_json(safe_path(domain_root, "manifest.json", must_exist=True))
    validate_manifest(manifest)
    if manifest["domain"] != "bilingual" or manifest["status"] != "ready":
        raise CorpusError("bilingual corpus is not ready")
    sources = {item["id"]: item for item in manifest["sources"]}
    raw_files = {"en": ("xquad_en", RAW_EN), "vi": ("xquad_vi", RAW_VI)}
    source_content: dict[str, Any] = {}
    source_hashes = {}
    for language, (source_id, path) in raw_files.items():
        source = sources[source_id]
        raw_path = safe_path(domain_root, path, must_exist=True)
        if git_blob_file(raw_path) != source["git_blob_sha1"]:
            raise CorpusError("XQuAD raw source Git blob differs from its pinned upstream blob")
        source_hashes[language] = sha256_file(raw_path)
        if source["expected_sha256"] and source_hashes[language] != source["expected_sha256"]:
            raise CorpusError("XQuAD raw source SHA256 differs from its pinned checksum")
        source_content[language] = read_json(raw_path)
    english = source_records(source_content["en"], "en")
    vietnamese = source_records(source_content["vi"], "vi")
    groups = align_paragraphs(english, vietnamese)
    contents, report = build_artifacts(english, vietnamese, groups, source_hashes=source_hashes)
    if manifest["document_count"] != len(groups) * 2 or manifest["qa_count"] != sum(
        report["qa_count_by_slice"].values()
    ):
        raise CorpusError("Bilingual manifest counts differ from full source alignment")
    expected = {"manifest.json", RAW_EN, RAW_VI, *contents}
    if set(_tree_files(domain_root)) != expected:
        raise CorpusError("Bilingual corpus has missing, duplicate, or unmanaged artifacts")
    for reference, body in contents.items():
        if safe_path(domain_root, reference, must_exist=True).read_bytes() != body:
            raise CorpusError(f"Bilingual artifact differs from pinned source: {reference}")
    artifacts = manifest["artifacts"]
    if {item["path"] for item in artifacts} != expected - {"manifest.json"}:
        raise CorpusError("Bilingual receipts differ from the complete materialized corpus")
    checksums = {}
    for artifact in artifacts:
        if artifact["role"] != artifact["path"].split("/", 1)[0]:
            raise CorpusError("Bilingual artifact role differs from its path")
        artifact_path = safe_path(domain_root, artifact["path"], must_exist=True)
        digest = sha256_file(artifact_path)
        if digest != artifact["sha256"] or artifact_path.stat().st_size != artifact["bytes"]:
            raise CorpusError("Bilingual artifact receipt hash/size differs from actual bytes")
        checksums[artifact["path"]] = digest
    if manifest["checksum"] != checksums:
        raise CorpusError("Bilingual checksum map differs from actual receipts")
    for slice_name in SLICES:
        language = "en" if slice_name in {"en_en", "vi_en"} else "vi"
        index = list(read_jsonl(domain_root / f"qa/documents_{language}.jsonl"))
        mapping = {item["document_id"]: item["path"] for item in index}
        rows = list(read_jsonl(domain_root / f"qa/{slice_name}.jsonl"))
        validate_qa_records(rows, domain_root / f"documents/{language}", mapping)
        if any(
            row["evaluation_slice"] != slice_name or row["corpus_language"] != language
            for row in rows
        ):
            raise CorpusError("Bilingual slice contains a mismatched corpus language")
    return report


def _published_hashes(root: Path) -> dict[str, str]:
    paths = [
        root / "manifest.json",
        *[path for path in (root / "bilingual").rglob("*") if path.is_file()],
    ]
    return {path.relative_to(root).as_posix(): sha256_file(path) for path in paths}


def _same_tree(first: Path, second: Path) -> bool:
    old, new = _tree_files(first), _tree_files(second)
    return set(old) == set(new) and all(
        sha256_file(old[key]) == sha256_file(new[key]) for key in old
    )


def _publish(stage: Path, root: Path) -> None:
    current, proposed = root / "bilingual", stage / "bilingual"
    aggregate, aggregate_new = root / "manifest.json", stage / "manifest.json"
    if _same_tree(current, proposed) and aggregate.read_bytes() == aggregate_new.read_bytes():
        return
    backup, aggregate_backup = stage / "previous-bilingual", stage / "previous-aggregate.json"
    shutil.copy2(aggregate, aggregate_backup)
    moved_old = moved_new = False
    try:
        os.replace(current, backup)
        moved_old = True
        os.replace(proposed, current)
        moved_new = True
        atomic_write(aggregate, [aggregate_new.read_bytes()])
    except BaseException:
        try:
            if moved_new:
                os.replace(current, proposed)
            if moved_old:
                os.replace(backup, current)
            os.replace(aggregate_backup, aggregate)
        except BaseException as rollback_error:
            raise CorpusError(
                "Bilingual publication rollback failed; inspect retained stage"
            ) from rollback_error
        raise


def prepare_bilingual(root: Path = CORPUS_ROOT) -> dict[str, Any]:
    from validate_corpus import validate_metadata

    root = root.resolve(strict=True)
    cache = safe_path(root, ".downloads")
    cache.mkdir(exist_ok=True)
    lock = safe_path(root, ".downloads/bilingual-setup.lock")
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise CorpusError(
            "Bilingual setup lock exists; inspect the active/stopped setup first"
        ) from None
    stage: Path | None = None
    success = False
    try:
        validate_metadata(root)
        prior_root = safe_path(root, "bilingual")
        prior = read_json(prior_root / "manifest.json")
        if prior["status"] == "ready":
            validate_bilingual(prior_root)
        elif set(_tree_files(prior_root)) != {"manifest.json"}:
            raise CorpusError("Refuse to replace unrecognized bilingual corpus files")
        stage = cache / ("bilingual-stage-" + uuid.uuid4().hex)
        stage.mkdir()
        destination = stage / "bilingual"
        destination.mkdir()
        (destination / "raw").mkdir()
        (destination / "documents/en").mkdir(parents=True)
        (destination / "documents/vi").mkdir(parents=True)
        (destination / "qa").mkdir()
        cache_receipt_path = safe_path(root, ".downloads/xquad-download.json")
        cache_info = (
            read_json(cache_receipt_path)
            if cache_receipt_path.is_file()
            else {"revision": REVISION, "downloaded_at": None, "sources": {}}
        )
        sources = {item["id"]: item for item in prior["sources"]}
        source_specs = (
            ("en", "xquad_en", RAW_EN, "xquad.en.json"),
            ("vi", "xquad_vi", RAW_VI, "xquad.vi.json"),
        )
        source_hashes = {}
        timestamps = []
        for language, source_id, raw_path, cache_name in source_specs:
            source = sources[source_id]
            cached = safe_path(root, ".downloads/" + cache_name)
            entry = cache_info["sources"].get(source_id)
            if entry and (
                entry.get("url") != source["url"]
                or entry.get("git_blob_sha1") != source["git_blob_sha1"]
            ):
                raise CorpusError("XQuAD cached source receipt differs from pinned provenance")

            def validate_source(path: Path, lang: str = language) -> None:
                _validate_source_file(path, lang)

            receipt = download(
                source["url"],
                cached,
                expected_sha256=source["expected_sha256"],
                expected_git_blob=source["git_blob_sha1"],
                validate=validate_source,
                timeout=30,
                attempts=2,
                max_bytes=16 * 1024 * 1024,
            )
            cache_info["sources"][source_id] = {
                "url": source["url"],
                "git_blob_sha1": source["git_blob_sha1"],
                "sha256": receipt.sha256,
                "bytes": receipt.byte_count,
                "downloaded_at": receipt.downloaded_at
                or (entry.get("downloaded_at") if entry else None),
            }
            timestamps.append(cache_info["sources"][source_id]["downloaded_at"])
            source_hashes[language] = receipt.sha256
            shutil.copy2(cached, safe_path(destination, raw_path))
        cache_info["revision"] = REVISION
        cache_info["downloaded_at"] = cache_info.get("downloaded_at") or next(
            (time for time in timestamps if time), None
        )
        write_json(cache_receipt_path, cache_info)
        english = source_records(read_json(destination / RAW_EN), "en")
        vietnamese = source_records(read_json(destination / RAW_VI), "vi")
        groups = align_paragraphs(english, vietnamese)
        contents, report = build_artifacts(english, vietnamese, groups, source_hashes=source_hashes)
        for reference, body in contents.items():
            output_path = safe_path(destination, reference)
            atomic_write(output_path, [body])
        artifacts_paths = sorted([RAW_EN, RAW_VI, *contents])
        artifacts = [
            {
                "path": path,
                "role": path.split("/", 1)[0],
                "sha256": sha256_file(safe_path(destination, path, must_exist=True)),
                "bytes": safe_path(destination, path, must_exist=True).stat().st_size,
            }
            for path in artifacts_paths
        ]
        downloaded_at = (
            prior["downloaded_at"] or cache_info["downloaded_at"] or datetime.now(UTC).isoformat()
        )
        manifest = {
            **prior,
            "status": "ready",
            "downloaded_at": downloaded_at,
            "document_count": report["paragraph_count_by_language"]["en"]
            + report["paragraph_count_by_language"]["vi"],
            "qa_count": sum(report["qa_count_by_slice"].values()),
            "checksum": {item["path"]: item["sha256"] for item in artifacts},
            "artifacts": artifacts,
            "notes": "Full pinned XQuAD EN/VI paragraphs and QA; alignment validated by article title and counterpart QA ID sets. Four full language-controlled slices use exact source counterpart answers; only documents/ is ingestable. QA remains evaluator-only; CC BY-SA 4.0 attribution/change notices apply.",
        }
        write_json(destination / "manifest.json", manifest)
        aggregate = read_json(root / "manifest.json")
        aggregate["domains"]["bilingual"] = {
            "manifest": "bilingual/manifest.json",
            "status": "ready",
            "document_count": manifest["document_count"],
            "qa_count": manifest["qa_count"],
        }
        aggregate["notes"] = (
            "Default, Document and Bilingual corpora prepared; clean all-domain reproduction and acceptance T08."
        )
        write_json(stage / "manifest.json", aggregate)
        shutil.copy2(
            root / "source-license-inventory.json", stage / "source-license-inventory.json"
        )
        for domain in ("default", "document"):
            (stage / domain).mkdir()
            shutil.copy2(root / domain / "manifest.json", stage / domain / "manifest.json")
        validate_metadata(stage)
        report = validate_bilingual(destination)
        _publish(stage, root)
        success = True
        return report
    finally:
        os.close(descriptor)
        lock.unlink(missing_ok=True)
        if success and stage is not None:
            resolved = stage.resolve(strict=True)
            if not resolved.is_relative_to(
                cache.resolve(strict=True)
            ) or not resolved.name.startswith("bilingual-stage-"):
                raise CorpusError("Refuse to clean staging outside the corpus download cache")
            shutil.rmtree(resolved)
