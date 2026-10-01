# RAG Core

RAG core độc lập để các ứng dụng chat gọi qua API: hỏi đáp trên tài liệu, trích dẫn có vị trí nguồn và truy xuất xuyên tiếng Việt/tiếng Anh.

> **Trạng thái: T01–T13 nền tảng, corpus, authentication, metadata, storage reader, registration/outbox và text parsers đã triển khai, kiểm chứng local.** T13 parse PDF text/DOCX/TXT/MD/HTML với provenance EN/VI, giới hạn và cleanup; OCR/scan chưa verified. T12 xác minh nguồn trên MinIO, ghi idempotency/link/job/outbox trong PostgreSQL và phát job qua Redis/Celery; ingestion worker T19 chưa có nên tài liệu vẫn queued. T11 S3 reader/IAM chỉ đọc đã kiểm trên MinIO thật; T10 schema/scope trên PostgreSQL thật; T09 xác thực qua HTTP thật. Compose chạy PostgreSQL 17, Qdrant, Redis và API health skeleton; profile `local-storage` thêm MinIO, `registration` thêm dispatcher. Default có 100 QA/986 documents; Document có 150 QA/84 PDF; Bilingual có 240 paragraphs mỗi ngôn ngữ và bốn XQuAD slices. Business HTTP API, ingestion, retrieval, LLM, SSE runtime và admin UI chưa hoạt động. T14–T36 còn trong backlog.

## Phạm vi đã chốt

- Default RAG: toàn bộ tài liệu đã upload/đăng ký cho **session hiện tại**.
- Document RAG: tập tài liệu được chọn trong session hiện tại.
- Multilingual RAG: cùng phạm vi session, hỗ trợ EN/VI và tìm xuyên ngôn ngữ.
- API JSON/SSE trả `answer`, `answerability`, `citations`, `contexts`; hiểu câu hỏi nối tiếp từ history do app gửi.
- App sở hữu tài liệu gốc trong S3/MinIO và lịch sử chat. RAG core sở hữu metadata/index; xóa session giữ nguyên tài liệu gốc và index.
- UI quản trị local cho trạng thái tài liệu/jobs/sessions/index/evaluation, có auth và audit.
- Technical/Custom Domain thêm qua registry sau này. Scarlet chưa được tích hợp trong đợt này.

**Tài liệu ngoài session không được tham gia truy vấn, kể cả của cùng người dùng.** Giữ index không cấp quyền cho session mới.

## Kiến trúc hiện tại và dự kiến

T02 đã có Python 3.12/FastAPI health skeleton, PostgreSQL 17, Qdrant, Redis và MinIO tùy chọn trong Docker Compose trên Windows. T12 thêm outbox dispatcher qua Celery/Redis trong profile `registration`; T13 thêm registry với Docling native PDF và các text adapters. Worker nhận và xử lý task, Tesseract OCR, BGE-M3 + multilingual reranker, DeepSeek/Anthropic adapters và Admin UI Jinja2/CSS/JavaScript vẫn là thiết kế cho task sau. Compose chưa khai báo worker/inference.

Máy mục tiêu: RAM 16 GB, RTX 4060 Laptop 8 GB VRAM; tài liệu nguồn khoảng <=1 GB; kiểm thử 15–20 người dùng đồng thời. Chưa có số đo RAM/VRAM/độ trễ hoặc benchmark chất lượng.

## Prerequisites, quality và local Docker

T01/T02 đã kiểm chứng trên Windows/PowerShell với uv 0.11.16, CPython 3.12.4 cho host checks, Docker Desktop Linux containers và Docker server 29.5.2. Project chấp nhận Python `3.12.*`; API image dùng Python 3.12.13 đã pin digest. Cài [uv](https://docs.astral.sh/uv/) và Docker Desktop, rồi từ root repository chạy quality:

```powershell
uv sync --locked --group dev --group api --group ingestion
uv run ruff check .
uv run mypy src
uv run pytest tests/unit
uv run pytest tests/contract/test_api_schema.py
uv run python scripts/export_openapi.py --check
uv run python scripts/check_docs.py
```

Trong sandbox hoặc máy không ghi được cache uv của user, đặt `UV_CACHE_DIR` và `UV_PYTHON_INSTALL_DIR` vào `.uv-cache`/`.uv-python` trong repository trước khi chạy; hai thư mục đã được ignore. `uv sync` tạo `.venv` từ lock. Nhóm `api` đã IMPLEMENTED cho health skeleton và bao gồm nhóm `metadata` từ T10 (SQLAlchemy async, Psycopg, Alembic); nhóm `ingestion` bao gồm metadata nhưng worker vẫn DESIGNED. Nhóm `inference` để trống đến T17.

Typed settings đọc environment hoặc `.env`: `DATABASE_URL`, `REDIS_URL` và `QDRANT_URL` là bắt buộc; `DATABASE_PASSWORD_FILE` cho phép API đọc Docker secret tách khỏi DSN. Biến rỗng trong example được bỏ qua, DSN/credential không xuất hiện trong repr hoặc traceback chuẩn hóa. Bảng đầy đủ nằm ở [RUNBOOK R02](RUNBOOK.md#r02).

Bootstrap tạo secret local ngẫu nhiên dưới `.local/secrets/` đã ignore và không in giá trị. Sau đó render/start/check stack:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\bootstrap_local.ps1
docker compose config --quiet
docker compose --profile local-storage up -d --build
docker compose --profile local-storage up -d --wait postgres qdrant redis api minio
docker compose --profile local-storage ps --all
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\smoke_local.ps1
```

API chỉ bind `http://127.0.0.1:8000`; MinIO API/console tùy chọn bind `127.0.0.1:9000/9001`. PostgreSQL, Qdrant và Redis chỉ ở mạng Compose, không publish host. `/health/live` kiểm process; `/health/ready` chạy `SELECT 1`, Redis `PING` và Qdrant `/readyz`, trả 503 nếu dependency lỗi. MinIO không phải dependency readiness của API health skeleton T02.

Bằng chứng local outage/persistence nằm ở [T02-A02](docs/handoffs.md#h-t02-a02); [T02-A03](docs/handoffs.md#h-t02-a03) tiếp quản candidate chưa commit, kiểm lại quality/stack hiện tại và đối chiếu SHA-256 source với API image cuối trước completion commit.

Dừng/khởi động lại mà giữ named volumes:

```powershell
docker compose --profile local-storage stop
docker compose --profile local-storage up -d
docker compose --profile local-storage up -d --wait postgres qdrant redis api minio
```

Không dùng `docker compose down -v` trong flow mặc định. T19/T26 sẽ thêm ingest/query; T28–T29 thêm admin UI; T35 kiểm lại hướng dẫn tích hợp.

## Hợp đồng API v1 T03

Pydantic contracts tại `src/rag_core/contracts/` đã kiểm structural validation cho domain/subset, history roles, EN/VI, initial limits, locators, evidence links, error và logical SSE traces. Export/kiểm lại từ root với dev+api groups:

```powershell
uv run python scripts/export_openapi.py
uv run python scripts/export_openapi.py --check
```

[OpenAPI v1 thiết kế](docs/api/openapi-v1.designed.json) có 13 operations với `x-served`/`x-implementation-status`; [OpenAPI đang serve](docs/api/openapi.served.json) chỉ có 2 health routes. [37 examples](docs/api/examples-v1.json) là dữ liệu synthetic minh họa, không phải response runtime. Export kiểm OpenAPI model, JSON Schema Draft 2020-12 và examples bằng cả JSON Schema/Pydantic; không đọc secret hoặc chạy dependency/provider probes. Hợp đồng và các gate runtime còn thiếu nằm ở [RUNBOOK R05–R08](RUNBOOK.md#r05), actual evidence [H-T03-A02](docs/handoffs.md#h-t03-a02); [H-T03-A01](docs/handoffs.md#h-t03-a01) ghi recovery do runtime quota trước commit.

## Authentication T09

`AUTH_CONFIG_FILE` trỏ tới JSON registry do operator quản lý. Mỗi request `/v1` cần
`Authorization: Bearer <JWT>` và `X-RAG-Service-Key`; app lấy từ service identity,
user lấy từ `sub` đã verify. JWT phải có signed `app_id` khớp app, `iss`, `aud`,
`exp`, `nbf`, `iat`; chỉ RS256. Chưa cấu hình auth thì `/v1` trả 503, không bypass.
Health routes vẫn public. T10 repository kiểm thêm owner/session/link/version/generation; principal tự nó không cấp quyền tài liệu.

```powershell
uv run python -m rag_core.auth.local_issuer init --directory .local/auth
uv run python -m rag_core.auth.local_issuer token --directory .local/auth --subject local-user --output .local/auth/user.jwt
uv run python -m rag_core.auth.local_issuer serve --directory .local/auth
```

CLI tạo key/service credential ngẫu nhiên, không in secrets và không ghi đè file.
JWKS chỉ phục vụ public key trên loopback port 8765; giữ terminal này chạy khi thử
API host với `AUTH_CONFIG_FILE=.local/auth/apps.json`. Quy trình đầy đủ, HTTP check
tự quản lý hai server và rotation/revocation: [RUNBOOK R03](RUNBOOK.md#r03).

```powershell
uv run pytest tests/security/test_auth.py
uv run pytest tests/security/test_local_auth_http.py -s
```

Endpoint `/v1/auth-test` chỉ được mount trong test. Application hiện vẫn chỉ có
hai health routes; request đã authenticate tới business route chưa implement trả
404. T09 chưa dựng issuer trong Compose hay tích hợp Scarlet. Evidence:
[H-T09-A01](docs/handoffs.md#h-t09-a01).

## Metadata và session scope T10

`PostgresSessionRepository` triển khai create/get/delete session, detach và snapshot
scope từ một SQL statement. External session ID chỉ unique trong app + user; session
mới rỗng. Tombstone không hồi sinh, delete/detach lặp lại giữ revision, link mới cần
registration mới. Scope chỉ chứa các cặp version/generation đã ready trong session;
subset ngoài quyền trả404, rỗng409, deleted410, selected chưa ready409.

Migration `0001_session_metadata` chạy bằng lệnh operator, không tự chạy khi API boot.
Với `DATABASE_URL` và optional `DATABASE_PASSWORD_FILE` trỏ tới DB đích đã kiểm:

```powershell
uv run alembic upgrade head
uv run alembic current
```

[RUNBOOK R04](RUNBOOK.md#r04) có schema ownership, mapping, transaction/revision contract,
credential riêng và commands cho PostgreSQL kiểm thử tách biệt. Acceptance đã chạy:

```powershell
uv run pytest tests/integration/test_session_scope.py -v -s --tb=short
uv run pytest tests/integration/test_metadata_migrations.py -v -s --tb=short
```

Tests cần `RAG_TEST_DATABASE_URL` tới service riêng, không tự thay PG bằng mock.
Evidence: [H-T10-A01](docs/handoffs.md#h-t10-a01). Business routes vẫn chưa mount theo
R05/T26; storage reader đã VERIFIED ở T11, registration/outbox dispatch đã VERIFIED ở T12;
worker/chunks/vector T19 chưa triển khai. Snapshot phải được consumer revalidate trước khi phát evidence/answer.

## Upload registration và outbox T12

`PostgresRegistrationRepository` nhận principal đã xác thực, core session UUID,
`Idempotency-Key` và `DocumentRegisterRequest`. App backend phải xác minh upload thuộc
user/session trước khi gọi; core đọc đúng app storage alias/prefix và kiểm bytes thực,
version/SHA-256. Cùng key/body trong app+owner+session trả cùng job; khác body hoặc
external upload ID dùng lại với key khác trả409. Link/job/outbox ghi trong một PG
transaction; Redis mất kết nối giữ event chờ. Dispatcher phát Celery task
`rag_core.ingest`, consumer T19 sẽ dùng `claim_job` để chống xử lý lặp.

Migration `0002_upload_registrations` chạy bằng `uv run alembic upgrade head` trên DB
đã kiểm. Dispatcher có CLI `uv run python -m rag_core.adapters.broker.dispatcher`
với `DATABASE_URL`, optional `DATABASE_PASSWORD_FILE` và `REDIS_URL`; Compose profile
`registration` có image riêng, không tự mount HTTP routes. Test tích hợp thật:

```powershell
uv sync --locked --group dev --group api --group ingestion
uv run pytest tests/integration/test_registration_jobs.py -v -s
```

Test cần isolated PostgreSQL `RAG_TEST_DATABASE_URL`, MinIO test IAM và Redis test
theo [RUNBOOK R04](RUNBOOK.md#r04). Khi T19 chưa triển khai, dispatcher chỉ đưa
message vào broker, job không thể đạt `ready`; không dùng message Redis làm trạng
thái nguồn. [H-T12-A01](docs/handoffs.md#h-t12-a01) ghi bằng chứng và giới hạn.

## Text parsers T13

`ParserRegistry(temp_root, ParserLimits())` nhận local path đã tải bằng storage reader,
filename, MIME và `SourceIdentity(document_id, version_id, sha256)`. Kết quả
`ParsedDocument/Block` giữ T03 locators, heading/table context và hash nguồn; parser
không cấp quyền session. T19 phải nối worker và T10 scope checks trước publication.
Một registry chạy tối đa một process, timeout mặc định60s và cleanup cả khi lỗi.

```powershell
uv sync --locked --group dev --group api --group ingestion
uv run --no-sync pytest tests/integration/test_text_parsers.py -v -s --tb=short --basetemp=.local/t13-check
```

Không cần services/provider/weights; fixtures synthetic tạo PDF Unicode hai trang,
DOCX page break/bảng/header/footer và TXT/MD/HTML EN/VI, chạy parser thật. PDF giữ
physical page one-based + native textline/bbox; DOCX paragraph/table + XML part/path,
không có page giả. HTML không render/fetch/execute. File rỗng/hỏng/mã hóa có safe
error; PDF có trang thiếu text trả `partial`/`needs_ocr_pages`, toàn bộ thiếu text
trả `ocr_required`. Scan/OCR, Office tables T14, chunking/index vẫn chưa verified.
MIME/limits/offset conventions/format matrix: [RUNBOOK R09](RUNBOOK.md#r09).
Evidence: [H-T13-A01](docs/handoffs.md#h-t13-a01).

## Corpus T04–T08: setup và tái tạo

T08 nghiệm thu tải mới vào output root/cache độc lập, all-domain validation và rerun. Workflow hiện hành là một task/session theo [AGENTS.md](AGENTS.md). Bằng chứng corpus và giới hạn tại [H-T08-A01](docs/handoffs.md#h-t08-a01).

[Corpus README](corpus-documents/README.md) và [source/license inventory](corpus-documents/source-license-inventory.json) ghi URLs/pins/license và ngoại lệ nguồn T05 được user phê duyệt tại [P11](docs/plan.md#p11). Default `ready`: 100 QA, 986 Markdown từ toàn context gồm distractors, supporting-only gold; 50 bridge/50 comparison, all hard theo nguồn thật. Document `ready` local: 150 open FinanceBench QA, 84 PDF được reference, 189 evidence giữ zero-based pages. Bilingual `ready`: XQuAD EN/VI v1.1, 240 aligned paragraphs per language and 1190 QA rows in each of four evaluation slices. Bilingual test checks alignment, counterpart gold, answer spans, setup/validation and deterministic reruns. Commands from root:

```powershell
uv run python corpus-documents/scripts/setup_corpus.py --all
uv run python corpus-documents/scripts/validate_corpus.py --all
uv run python corpus-documents/scripts/validate_corpus.py --metadata-only
uv run python corpus-documents/scripts/setup_corpus.py --domain default
uv run python corpus-documents/scripts/validate_corpus.py --domain default
uv run python corpus-documents/scripts/setup_corpus.py --domain document
uv run python corpus-documents/scripts/validate_corpus.py --domain document
uv run python corpus-documents/scripts/setup_corpus.py --domain bilingual
uv run python corpus-documents/scripts/validate_corpus.py --domain bilingual
uv run pytest tests/unit/test_corpus_bilingual.py
```

`--metadata-only` không nghiệm thu data. Setup/validation of all three domains pass with real bytes. XQuAD sources are pinned to revision `7d30520c717524000f0d9d2f9c10a069acd9d285`, source SHAs and artifact hashes are recorded in bilingual manifests; rerun preserves published file hashes, mtimes, slice IDs and original timestamp. Four slices are en-en, vi-vi, vi-en and en-vi; QA/gold is evaluator-only and must not be ingested. Bilingual `bilingual` is a corpus label only; product API domain remains `multilingual`. T08 all-domain clean reproduction is verified; see the commands below. Document limits: FinanceBench redistribution applicability unresolved; XQuAD has no unanswerable examples. Only `documents/` is eligible for future ingestion; `qa/`/source IDs/gold are not retrieval hints. See [H-T06-A02](docs/handoffs.md#h-t06-a02), [H-T05-A02](docs/handoffs.md#h-t05-a02), [Corpus README](corpus-documents/README.md) and [RUNBOOK R11](RUNBOOK.md#r11).

To reproduce without touching the standard corpus, use a new short name below the
ignored `corpus-documents/.repro/` directory (the `a1` run was verified in T08):

```powershell
uv run python corpus-documents/scripts/setup_corpus.py --all --output-root corpus-documents/.repro/a1
uv run python corpus-documents/scripts/validate_corpus.py --all --output-root corpus-documents/.repro/a1
```

Use an unused name for another cold download; the same name resumes or reuses verified
local bytes. Output roots share only source metadata and schemas, never dataset caches.
A metadata-only checkout rebuilds ignored payloads automatically after checking retained
QA hashes. Partially missing/corrupt payloads fail; unknown files are preserved.
See [RUNBOOK R11](RUNBOOK.md#r11) for fingerprint/rerun and recovery instructions.

## Tài liệu

| File | Nội dung |
| --- | --- |
| [AGENTS.md](AGENTS.md) | Luật agent, scope và workflow |
| [docs/plan.md](docs/plan.md) | Toàn bộ bối cảnh và kiến trúc |
| [docs/tasks.md](docs/tasks.md) | Phases, tasks, dependency và DoD |
| [docs/handoffs.md](docs/handoffs.md) | Current checkpoint và output kiểm chứng |
| [docs/implementation-summary.md](docs/implementation-summary.md) | Ghi chú theo phase/task |
| [RUNBOOK.md](RUNBOOK.md) | Vận hành và hợp đồng tích hợp app tương lai |
| [Prompt corpus](corpus-documents/Codex%20Prompt%20%E2%80%93%20Build%20RAG%20Evaluation%20Corpus.md) | Yêu cầu chuẩn bị HotpotQA, FinanceBench, XQuAD |

## Các phần sẽ được cập nhật cùng implementation

- **T01 VERIFIED:** Python prerequisites và quality nền tảng. **T02 VERIFIED:** Docker start/stop/health, dependency probes, loopback/internal ports và restart persistence.
- **T03 VERIFIED contracts:** schemas, designed/served OpenAPI snapshots và examples; ownership/readiness/tokenizer enforcement/query/SSE runtime vẫn theo task sau.
- **T04–T08 VERIFIED corpus:** từng domain và all-domain setup/validation, tải mới vào root độc lập, unchanged gold, stable reruns và missing-file rejection. Mỗi session thực hiện một task theo [prompt mẫu](docs/task-session-prompt.md).
- **T09 VERIFIED authentication:** service identity + RS256 JWT, local issuer, bounded JWKS rotation/cache và HTTP acceptance.
- **T10 VERIFIED metadata:** PG migrations, owner-bound session/link repository, revision và exact version/generation snapshots.
- **T11 VERIFIED storage reader:** HEAD/GET theo app/alias/bucket/prefix cấu hình; checksum hoặc version ID, giới hạn stream/temp, MinIO IAM reader chỉ đọc kiểm chứng thật. [RUNBOOK R04](RUNBOOK.md#r04) có cấu hình/test/trust contract.
- **T12 VERIFIED registration/outbox:** real MinIO/PG/Redis integration, owner/session idempotency, detach, retry, crash redelivery và dispatcher image/CLI. Business HTTP mount và ingestion worker vẫn DESIGNED ở T26/T19.
- **T13 VERIFIED text parsers:** PDF native text, DOCX, TXT/MD/HTML EN/VI; provenance và process/MIME/size/archive/time/cleanup gates. OCR/scan chưa verified.
- **T14–T19:** Office tables/OCR, model setup, chunking và ingestion commands.
- **T20–T26:** query JSON/SSE, history, citations, provider configuration và live smoke.
- **T27–T29:** admin URL/login, UI workflows.
- **T30–T34:** benchmark reports, performance, reliability, backup/restore.
- **T35–T36:** quickstart tích hợp đã kiểm chứng và trạng thái nghiệm thu cuối.

## Nguyên tắc cập nhật

README và RUNBOOK được cập nhật trong từng task; mục mới ghi rõ `DESIGNED`, `IMPLEMENTED` hoặc `VERIFIED` cùng task/evidence. Không quảng cáo tính năng, format hay tốc độ chưa đo. Secrets, tài liệu gốc, model weights và database dumps không thuộc source code.
