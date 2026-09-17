# RAG evaluation corpus

**T04 IMPLEMENTED/VERIFIED: shared tooling, source inventory and metadata schemas.**
No official corpus bytes have been downloaded or normalized. Setup for each domain
is implemented in T05–T07; full clean-state reproduction and acceptance belong to T08.
The [original prompt](Codex%20Prompt%20%E2%80%93%20Build%20RAG%20Evaluation%20Corpus.md)
remains unchanged.

| Corpus domain | Purpose | Data status | Measured documents / QA |
| --- | --- | --- | --- |
| `default` / HotpotQA | Generic multi-hop retrieval with supporting paragraphs and distractors | `not_downloaded` | unknown / unknown |
| `document` / FinanceBench | Long financial PDFs, numeric answers, evidence and page-aware citations | `not_downloaded`; license decision pending | unknown / unknown |
| `bilingual` / XQuAD | Parallel EN/VI QA and cross-lingual retrieval | `not_downloaded` | unknown / unknown |

Targets from the prompt (100 HotpotQA QA; approximately 150 FinanceBench QA;
approximately 240 paragraphs per language and 1190 XQuAD QA per slice) are planned
targets, **not measured counts**. Manifests store unknown counts and download
timestamps as JSON `null`, with empty checksum/receipt collections. Inventory
`verified_at` records when source metadata was assembled, not a dataset download.

## Sources and rights

[Source/license inventory](source-license-inventory.json) records official URLs,
upstream commit dates, exact Git commit/blob IDs, attribution and limitations.
Git blob IDs were read from the official GitHub trees; they are not local SHA256
measurements. README statements, trees and the publisher card were checked live
on 2026-09-17; actual commands/output are in [H-T04-A01](../docs/handoffs.md#h-t04-a01).

| Dataset | Pinned upstream | Dataset rights |
| --- | --- | --- |
| [HotpotQA](https://github.com/hotpotqa/hotpot) | `3635853403a8735609ee997664e1528f4480762a`; dev distractor `v1` | [README dataset terms](https://github.com/hotpotqa/hotpot/blob/3635853403a8735609ee997664e1528f4480762a/README.md#license): CC BY-SA 4.0. Apache 2.0 is the code license. |
| [FinanceBench](https://github.com/patronus-ai/financebench) | `cc39aeb4afdf33909ee1412188bf89035950c2eb` | GitHub files have no explicit grant in the inspected tree/README. [Publisher HF card](https://huggingface.co/datasets/PatronusAI/financebench/blob/e04404e3a97f69f79c14d42f24981a1c9c3bcd18/README.md) declares CC BY-NC 4.0; GitHub QA/PDF permissions remain unresolved. |
| [XQuAD](https://github.com/google-deepmind/xquad) | `7d30520c717524000f0d9d2f9c10a069acd9d285` | [README dataset terms](https://github.com/google-deepmind/xquad/blob/7d30520c717524000f0d9d2f9c10a069acd9d285/README.md#license): CC BY-SA 4.0. |

Keep dataset/paper attribution, upstream titles/filenames, license links and a
description of normalization changes in any permitted lightweight outputs.
CC BY-SA adaptations must preserve the applicable ShareAlike terms. Company
reports retain their own rights; a QA dataset card does not automatically license
the PDFs. T06 must obtain a user decision on permitted local evaluation use of
official GitHub QA/PDFs or an upstream permission grant before downloading them.
No dataset source is silently substituted. See [license notices](licenses/README.md).

Raw datasets and materialized document/PDF directories are ignored by existing
repository policy. Scripts, manifests, inventory, schemas and attribution notices
are tracked. Lightweight normalized QA may be tracked in later tasks only with
verified applicable rights and attribution; FinanceBench remains metadata-only
until the license decision. No new broad ignore rules hide source or QA metadata.

## Commands and directory layout

Use Python `3.12.*` from the repository root. Install the existing dev group
(`jsonschema` is already locked; no new dependency or baseline model is needed):

```powershell
uv sync --locked --group dev --group api
uv run python corpus-documents/scripts/setup_corpus.py --help
uv run python corpus-documents/scripts/validate_corpus.py --metadata-only
uv run pytest tests/unit/test_corpus_common.py
```

`--metadata-only` validates inventory/schema/provenance and aggregate consistency.
Its success message explicitly states that corpus data was **not validated**.
The following setup/full-validation selections currently fail nonzero with a
clear unavailable/not-downloaded message and preserve files:

```powershell
uv run python corpus-documents/scripts/setup_corpus.py --all
uv run python corpus-documents/scripts/setup_corpus.py --domain default
uv run python corpus-documents/scripts/setup_corpus.py --domain document
uv run python corpus-documents/scripts/setup_corpus.py --domain bilingual
uv run python corpus-documents/scripts/validate_corpus.py --all
uv run python corpus-documents/scripts/validate_corpus.py --domain default
```

These become working preparation/validation commands sequentially in T05–T07;
the one-command, all-domain setup is accepted in T08. There are no hidden manual
downloads, success stubs or legacy training/model setup calls in T04.

```text
corpus-documents/
  scripts/{common,setup_corpus,validate_corpus}.py
  schemas/{domain-manifest,root-manifest,source-inventory}.schema.json
  source-license-inventory.json
  manifest.json
  {default,document,bilingual}/manifest.json
  licenses/README.md
```

Each domain will create separate `raw/`, `documents/` and `qa/` directories.
All download/normalization scripts and corpus outputs stay below this directory.
`documents/` alone contains ingestable content. `qa/`, answers, justification,
supporting flags and raw source QA are evaluator inputs and must never be ingested
or used to prefilter retrieval to known gold documents/pages. Source question IDs
are provenance metadata and must not become retrieval text or answer hints.

## Shared interfaces and validation

`scripts/common.py` provides portable safe references, strict UTF-8 JSON/JSONL
parsing (no duplicate keys/nonfinite constants), SHA256 and Git-blob hashing,
bounded streamed downloads and per-file atomic writes. Downloads validate byte
limits, advertised length, supplied checksum/blob pins and optional content checks
before replacing a valid prior file. Retries apply only to transport failures and
selected HTTP 408/429/5xx statuses: default 3 attempts, at most 5, bounded timeout
and backoff. Corrupt content and local publication failures fail immediately.
The allowlist permits official GitHub hosts and the legacy CMU HotpotQA host;
redirects are checked before following and HTTPS downgrades are rejected.

A verified cached file is reused only when a byte pin exists and passes; a reuse
receipt has `downloaded_at=null`, `reused=true` and measured hash/size. Domain
callers must preserve the original download timestamp rather than overwrite it
with a reuse time. Equal atomic writes preserve mtime. Failure cleans only the
call's staged `.part` file, leaving previously published bytes intact. Atomicity
is per file; complete domain-generation publication belongs to T05–T08.

The legacy HotpotQA URL is version-named but not a content-addressed Git blob.
No expected SHA256 was found in the inspected official README. Its first download
must use domain semantic validation and record a measured SHA256; later runs
must reuse that measured pin. T04 does not claim immutable bytes for this source.
The four pinned GitHub JSON/JSONL endpoints returned HEAD 200. HotpotQA's official
CMU HTTP HEAD timed out after 20 seconds; HTTPS on the same host timed out after
15 seconds. The official homepage still advertises the HTTP link. T05 must verify
access/download or report an upstream availability blocker; no alternate mirror
was chosen. Successful HEAD establishes endpoint access only, not byte integrity.

Common QA validation requires unique IDs, nonempty questions/expected answers and
existing nonempty expected documents. Callers supply a document-ID to safe path
map relative to `documents/`. References reject traversal, absolute/Windows drive
or alternate-stream paths, reserved device names and symlink/junction escapes.
Domain validators will additionally compare original gold, supporting documents,
PDF/evidence pages and parallel counterpart alignment in T05–T07.

Domain manifests use `schema_version=1`, `not_downloaded|preparing|ready`, sources,
download timestamp, measured counts, languages, path-to-SHA256 map and artifact
receipts (`path`, `role`, `sha256`, `bytes`). Ready manifests need measured values;
not-downloaded manifests cannot claim counts, downloads or artifacts. Receipt paths
must match `raw/`, `documents/` or `qa/` roles. The aggregate points to the exact
three domain manifests and repeats their status/counts. No DB/index/API migration
or ingestion is performed by these independent corpus tools.

## Evaluation conventions and limits

Planned normalized QA retains `id`, `domain`, `question`, `expected_answers`,
`expected_documents`, `answerable` and `source_dataset` plus domain provenance.
FinanceBench retains original human gold/evidence/justification and **zero-based**
evidence pages in `document/manifest.json`; converting to product one-based physical
PDF citations belongs to the evaluation adapter, not source rewriting.

| Slice | Question language | Retrieved corpus | Gold answer language |
| --- | --- | --- | --- |
| `en_en` | EN | EN | EN |
| `vi_vi` | VI | VI | VI |
| `vi_en` | VI | EN | EN counterpart |
| `en_vi` | EN | VI | VI counterpart |

XQuAD alignment must be validated before assigning deterministic parallel group
IDs. `bilingual` is the corpus label; product API domain remains `multilingual`.
XQuAD has no unanswerable questions, so its results cannot establish complete
hallucination/refusal behavior. No retrieval/generation benchmark has run. All
eventual RAG queries still require uploads/registration in the current app/user
session; this corpus directory confers no production retrieval permissions.
