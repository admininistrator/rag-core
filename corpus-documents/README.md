# RAG evaluation corpus

**T04 shared tooling, T05 Default and T06 Document preparation are VERIFIED locally.**
Default uses the exact Hugging Face derivative approved by the user after the
canonical CMU endpoint timed out. Document uses the pinned official FinanceBench
open sample and only its referenced repository PDFs. Bilingual is pending T07;
full clean-state reproduction and acceptance belong to T08.
The [original prompt](Codex%20Prompt%20%E2%80%93%20Build%20RAG%20Evaluation%20Corpus.md)
remains unchanged.

| Corpus domain | Purpose | Data status | Measured documents / QA |
| --- | --- | --- | --- |
| `default` / HotpotQA | Generic multi-hop retrieval with supporting paragraphs and distractors | `ready`; approved HF derivative | 986 / 100 |
| `document` / FinanceBench | Long financial PDFs, numeric answers, evidence and page-aware citations | `ready` locally; redistribution applicability unresolved | 84 PDFs / 150 QA |
| `bilingual` / XQuAD | Parallel EN/VI QA and cross-lingual retrieval | `not_downloaded` | unknown / unknown |

The remaining prompt targets (approximately 240 paragraphs per language and 1190
XQuAD QA per slice) are planned, **not measured counts**. The bilingual manifest
stores unknown counts/download timestamp as JSON `null` with empty receipts. Inventory
`verified_at` records when source metadata was assembled, not a dataset download.

## Sources and rights

[Source/license inventory](source-license-inventory.json) records official URLs,
upstream commit dates, exact Git commit/blob IDs, attribution and limitations.
Git blob IDs were read from the official GitHub trees; they are not local SHA256
measurements. README statements, trees and publisher cards were checked live on
2026-09-17; FinanceBench pins/notices were rechecked on 2026-09-19. Evidence is in
[H-T04-A01](../docs/handoffs.md#h-t04-a01) and [H-T06-A02](../docs/handoffs.md#h-t06-a02).

| Dataset | Pinned upstream | Dataset rights |
| --- | --- | --- |
| [HotpotQA](https://github.com/hotpotqa/hotpot) | Original repository `3635853403a8735609ee997664e1528f4480762a`; approved HF `hotpotqa/hotpot_qa` revision `1908d6afbbead072334abe2965f91bd2709910ab`, distractor/validation | [Original dataset terms](https://github.com/hotpotqa/hotpot/blob/3635853403a8735609ee997664e1528f4480762a/README.md#license) and [pinned HF card](https://huggingface.co/datasets/hotpotqa/hotpot_qa/blob/1908d6afbbead072334abe2965f91bd2709910ab/README.md): CC BY-SA 4.0. Apache 2.0 is the code license. |
| [FinanceBench](https://github.com/patronus-ai/financebench) | `cc39aeb4afdf33909ee1412188bf89035950c2eb` | GitHub files have no explicit grant in the inspected tree/README. [Publisher HF card](https://huggingface.co/datasets/PatronusAI/financebench/blob/e04404e3a97f69f79c14d42f24981a1c9c3bcd18/README.md) declares CC BY-NC 4.0; GitHub QA/PDF permissions remain unresolved. |
| [XQuAD](https://github.com/google-deepmind/xquad) | `7d30520c717524000f0d9d2f9c10a069acd9d285` | [README dataset terms](https://github.com/google-deepmind/xquad/blob/7d30520c717524000f0d9d2f9c10a069acd9d285/README.md#license): CC BY-SA 4.0. |

Keep dataset/paper attribution, upstream titles/filenames, license links and a
description of normalization changes in any permitted lightweight outputs.
CC BY-SA adaptations must preserve the applicable ShareAlike terms. Company
reports retain their own rights; a QA dataset card does not automatically license
the PDFs. The approved project plan authorizes this local evaluation download but
does not supply an upstream redistribution or commercial-use grant.
No dataset source is silently substituted. See [license notices](licenses/README.md).

Raw datasets and materialized document/PDF directories are ignored by existing
repository policy. Scripts, manifests, inventory, schemas and attribution notices
are tracked. T05 tracks lightweight normalized QA, its document index and preparation
report with CC BY-SA attribution/change notices. FinanceBench raw JSONL, PDFs and
normalized gold/evidence QA remain local and ignored while redistribution applicability
is unresolved; the tracked manifest contains hashes/counts/receipts and attribution.

## Commands and directory layout

Use Python `3.12.*` from the repository root. Install the dev group; it includes
schema checks, Hotpot Parquet support and pinned PDF page/crypto parsing, with no
dataset baseline model:

```powershell
uv sync --locked --group dev --group api
uv run python corpus-documents/scripts/setup_corpus.py --help
uv run python corpus-documents/scripts/validate_corpus.py --metadata-only
uv run pytest tests/unit/test_corpus_common.py
uv run pytest tests/unit/test_corpus_default.py
uv run python corpus-documents/scripts/setup_corpus.py --domain default
uv run python corpus-documents/scripts/validate_corpus.py --domain default
uv run python corpus-documents/scripts/setup_corpus.py --domain document
uv run python corpus-documents/scripts/validate_corpus.py --domain document
uv run pytest tests/unit/test_corpus_document.py
```

`--metadata-only` validates inventory/schema/provenance and aggregate consistency.
Its success message explicitly states that corpus data was **not validated**.
Default and Document setup/validation PASS with real downloaded bytes. The following
setup/full-validation selections currently fail nonzero with a
clear unavailable/not-downloaded message and preserve files:

```powershell
uv run python corpus-documents/scripts/setup_corpus.py --all
uv run python corpus-documents/scripts/setup_corpus.py --domain bilingual
uv run python corpus-documents/scripts/validate_corpus.py --all
```

The bilingual domain becomes a working preparation/validation command in T07;
the one-command, all-domain setup is accepted in T08. There are no hidden manual
downloads, success stubs or legacy training/model setup calls in T04.

```text
corpus-documents/
  scripts/{common,prepare_default,prepare_document,setup_corpus,validate_corpus}.py
  schemas/{domain-manifest,root-manifest,source-inventory}.schema.json
  source-license-inventory.json
  manifest.json
  {default,document,bilingual}/manifest.json
  licenses/README.md
```

Default and Document have separate `raw/`, `documents/` and `qa/` directories;
Bilingual follows in T07.
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
redirects are checked before following and HTTPS downgrades are rejected. The
user-approved exception permits exactly the pinned HF Parquet URL with its mandatory
published SHA256 and inspected HTTPS `us.aws.cdn.hf.co/xet-bridge-us/` delivery.
Temporary signed queries are accepted only for that transfer and never logged.

A verified cached file is reused only when a byte pin exists and passes; a reuse
receipt has `downloaded_at=null`, `reused=true` and measured hash/size. Domain
callers must preserve the original download timestamp rather than overwrite it
with a reuse time. Equal atomic writes preserve mtime. Failure cleans only the
call's staged `.part` file, leaving previously published bytes intact. Atomicity
is per file; T05/T06 stage and validate a complete domain before directory
publication, with exclusive per-domain setup locks and rollback of the domain and
aggregate on publication errors. Equal complete trees skip publication and retain
all mtimes. Readers must wait for setup to finish: directory swaps are not a concurrent
reader transaction. Failed stages and rollback backups stay in ignored `.downloads/`
for inspection; unknown files and links/junctions cause refusal before replacement.

The legacy HotpotQA URL is version-named but not a content-addressed Git blob.
No expected SHA256 was found in the inspected official README. Its first download
must use domain semantic validation and record a measured SHA256; later runs
must reuse that measured pin. T04 does not claim immutable bytes for this source.
T05 actual CMU HTTP and same-host HTTPS GET each timed out after 20 seconds.
On 2026-09-17 the user approved the exact HF source exception recorded in
[P11](../docs/plan.md#p11). This is a community/HF-maintained Parquet derivative;
it is not asserted to be an official author mirror or byte-identical CMU JSON.
The downloaded Parquet is **27,452,575 bytes**, SHA256
`c20b638ca82b21d04fe12e14ff417ad05153d4d215a65de54497fca4e972f7c6`, matching
the pinned repository's published LFS checksum. Its 7405 measured rows are converted
without rewriting semantic fields to legacy JSON; the converted JSON hash is separate
in `default/qa/preparation.json`. Dev-only `pyarrow==25.0.1` reads Parquet; it is not
an API/model dependency. Raw Parquet/converted JSON and Markdown documents stay ignored.

Common QA validation requires unique IDs, nonempty questions/expected answers and
existing nonempty expected documents. Callers supply a document-ID to safe path
map relative to `documents/`. References reject traversal, absolute/Windows drive
or alternate-stream paths, reserved device names and symlink/junction escapes.
Default validation compares every generated QA/document/report to the pinned source,
checks original answers/type/level/supporting mapping, all receipts and exact file sets,
and reruns the seed42 sampling. Document validation recomputes every normalized
FinanceBench field, opens every real PDF, checks every zero-based evidence page against
its page count and verifies the exact file/receipt set. Parallel alignment follows T07.

## Default measured data and evaluation contract

Source: 7405 rows, 5918 bridge and 1487 comparison, **all hard**; no medium examples
are available in this split. Sampling sorts source IDs, balances available type/level
strata with capacity redistribution, samples with `random.Random(42)`, then sorts the
selected IDs. The unchanged 100-QA subset is 50 bridge + 50 comparison, all hard.
Selected-ID SHA256: `40045c404f9bc627004e7c48bd2df9ac6165be2342595832ed7590487e436d63`.
996 context paragraph instances become 986 documents after 10 duplicate instances
are merged. Identity hashes the exact title and concatenated original sentence text;
same-title/different-text paragraphs have different IDs. Every distractor is included.

Markdown contains only `document_id`, title, dataset origin and original paragraph
text. `qa/documents.json` holds source-question provenance and ID-to-path/hash mapping;
it is evaluator-only metadata. `qa/eval.jsonl` retains source IDs, original question,
answer/type/level/supporting facts, supporting-only expected documents and context IDs.
Never use those context/source IDs or expected documents as retrieval hints. Ingest
all `documents/*.md`, search the materialized corpus and score against QA gold afterward.

The full source has one unchanged annotation anomaly: source ID
`5ae61bfd5542992663a4f261`, title `Jimmy Butler (basketball)`, sentence index902
for a 5-sentence paragraph. It is outside the deterministic selected100. The report
records the anomaly; full-source structural/title checks do not claim every annotation
is valid. Sampled supporting sentence ranges must pass; an anomaly in the subset fails
without dropping, editing or resampling the question. Live checks/rerun/37 synthetic
default tests are recorded in [H-T05-A02](../docs/handoffs.md#h-t05-a02).

## Document measured data and evaluation contract

Pinned FinanceBench commit `cc39aeb4afdf33909ee1412188bf89035950c2eb`
provides 150 `OPEN_SOURCE` QA and metadata with 361 rows/360 unique document names.
The QA reference exactly 84 of the repository's 368 PDFs; setup downloads those 84
and no others. QA JSONL SHA256 is
`a5a2aa673e573e55675fc3c0f9aa38c1cf59d2abc91edb077534f71f10a71877`;
metadata SHA256 is `1c69127783879de8cdadb159d2181f39bc3123b8e0ebf74031c3969d69189575`.
The 84 PDFs total 165,527,662 bytes and 12,013 pages. The 189 evidence entries use
pages 0–303; all are in range against the real PDFs. Dev-only pinned
`pypdf[crypto]==6.19.0` handles page counts, including AES-encrypted source files;
it is not an API/model dependency.

`document/qa/eval.jsonl` retains all source questions, answers, evidence and full-page
evidence strings, justification, question/reasoning types, company/document/subset
metadata and domain-question number. Field names are normalized; values and source
order are unchanged. `document/qa/documents.json` maps each original PDF filename to
company metadata, immutable repository URL, SHA256, bytes and measured page count.
`document/qa/preparation.json` records counts/hashes/distributions and anomalies.
Fifty source rows have null justification and null reasoning labels; they remain null.
The metadata source contains two conflicting rows for unreferenced
`FOOTLOCKER_2023_annualreport`; the report records this anomaly, while any duplicate
for a referenced document fails as ambiguous. No question is dropped, corrected or
resampled. These QA files remain local/ignored under the rights boundary above.

The document setup uses an exclusive `.downloads/document-setup.lock`, verified
transport cache, complete-domain staging and aggregate rollback. Its rerun preserved
all 91 published file hashes/mtimes, 150 IDs and the original download timestamp;
all 84 cached PDF hashes/mtimes were unchanged, so no PDF was downloaded again.
Failed stages remain under ignored `.downloads/document-stage-*` for diagnosis.
Live setup/validator/rerun and synthetic tests are at
[H-T06-A02](../docs/handoffs.md#h-t06-a02).

Domain manifests use `schema_version=1`, `not_downloaded|preparing|ready`, sources,
download timestamp, measured counts, languages, path-to-SHA256 map and artifact
receipts (`path`, `role`, `sha256`, `bytes`). Ready manifests need measured values;
not-downloaded manifests cannot claim counts, downloads or artifacts. Receipt paths
must match `raw/`, `documents/` or `qa/` roles. The aggregate points to the exact
three domain manifests and repeats their status/counts. No DB/index/API migration
or ingestion is performed by these independent corpus tools.

## Evaluation conventions and limits

Normalized QA retains `id`, `domain`, `question`, `expected_answers`,
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
