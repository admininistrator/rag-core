# RAG Core

RAG core độc lập để các ứng dụng chat gọi qua API: hỏi đáp trên tài liệu, trích dẫn có vị trí nguồn và truy xuất xuyên tiếng Việt/tiếng Anh.

> **Trạng thái: T01–T04 nền tảng, T05 HotpotQA Default và T06 FinanceBench Document đã triển khai, kiểm chứng local.** Compose chạy PostgreSQL 17, Qdrant, Redis và API health skeleton; profile `local-storage` thêm MinIO. T03 có contracts; T04 có tooling; T05 có 100QA/986documents từ nguồn Hugging Face được user phê duyệt; T06 có 150QA/84PDF từ FinanceBench. Business API, ingestion, retrieval, LLM, SSE runtime và UI chưa hoạt động. T07–T36 còn trong backlog; theo yêu cầu người dùng, công việc tạm dừng sau khi đóng T06.

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

T02 đã có Python 3.12/FastAPI health skeleton, PostgreSQL 17, Qdrant, Redis và MinIO tùy chọn trong Docker Compose trên Windows. Celery/outbox, Docling/Tesseract OCR, BGE-M3 + multilingual reranker, DeepSeek/Anthropic adapters và Admin UI Jinja2/CSS/JavaScript vẫn là thiết kế cho task sau. Compose không khai báo worker/dispatcher/inference khi các process đó chưa được triển khai.

Máy mục tiêu: RAM 16 GB, RTX 4060 Laptop 8 GB VRAM; tài liệu nguồn khoảng <=1 GB; kiểm thử 15–20 người dùng đồng thời. Chưa có số đo RAM/VRAM/độ trễ hoặc benchmark chất lượng.

## Prerequisites, quality và local Docker

T01/T02 đã kiểm chứng trên Windows/PowerShell với uv 0.11.16, CPython 3.12.4 cho host checks, Docker Desktop Linux containers và Docker server 29.5.2. Project chấp nhận Python `3.12.*`; API image dùng Python 3.12.13 đã pin digest. Cài [uv](https://docs.astral.sh/uv/) và Docker Desktop, rồi từ root repository chạy quality:

```powershell
uv sync --locked --group dev --group api
uv run ruff check .
uv run mypy src
uv run pytest tests/unit
uv run pytest tests/contract/test_api_schema.py
uv run python scripts/export_openapi.py --check
uv run python scripts/check_docs.py
```

Trong sandbox hoặc máy không ghi được cache uv của user, đặt `UV_CACHE_DIR` và `UV_PYTHON_INSTALL_DIR` vào `.uv-cache`/`.uv-python` trong repository trước khi chạy; hai thư mục đã được ignore. `uv sync` tạo `.venv` từ lock. Nhóm `api` đã IMPLEMENTED cho health skeleton; nhóm `ingestion` mới LOCKED/DESIGNED và nhóm `inference` để trống đến T17 để không kéo model runtime nặng vào API.

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

## Corpus tooling T04, Default T05 và Document T06

[Corpus README](corpus-documents/README.md) và [source/license inventory](corpus-documents/source-license-inventory.json) ghi URLs/pins/license và ngoại lệ nguồn T05 được user phê duyệt tại [P11](docs/plan.md#p11). Default `ready`: 100QA, 986Markdown từ toàn context gồm distractors, supporting-only gold; 50bridge/50comparison, allhard theo nguồn thật. Document `ready` local: 150 open FinanceBench QA, 84 PDF được reference, 189 evidence giữ zero-based pages. Utilities kiểm download hỏng/ngắt, rollback publication, retry hữu hạn, idempotency và reference safety. Bilingual còn `not_downloaded`, counts/timestamps null. Commands từ root:

```powershell
uv run python corpus-documents/scripts/setup_corpus.py --help
uv run python corpus-documents/scripts/validate_corpus.py --metadata-only
uv run pytest tests/unit/test_corpus_common.py
uv run python corpus-documents/scripts/setup_corpus.py --domain default
uv run python corpus-documents/scripts/validate_corpus.py --domain default
uv run pytest tests/unit/test_corpus_default.py
uv run python corpus-documents/scripts/setup_corpus.py --domain document
uv run python corpus-documents/scripts/validate_corpus.py --domain document
uv run pytest tests/unit/test_corpus_document.py
```

`--metadata-only` không nghiệm thu data. Default và Document setup/validation PASS với real bytes; rerun giữ IDs/hashes/timestamp/mtimes và không tải lại PDF. FinanceBench pin `cc39aeb4afdf33909ee1412188bf89035950c2eb`, QA SHA256 `a5a2aa673e573e55675fc3c0f9aa38c1cf59d2abc91edb077534f71f10a71877`, metadata SHA256 `1c69127783879de8cdadb159d2181f39bc3123b8e0ebf74031c3969d69189575`; 84 PDF thực có 12,013 trang/165,527,662 bytes và mọi page gold trong range. Dev-only `pypdf[crypto]==6.19.0` chỉ dùng cho corpus. Raw/PDF/normalized FinanceBench QA local bị ignore vì redistribution applicability chưa rõ; publisher card riêng khai CC BY-NC4.0 và company PDF rights riêng. Chỉ `documents/` được ingest sau này; `qa/`/source IDs/gold không là retrieval hints. Setup `--all` và bilingual vẫn fail nonzero; T07–T08 pending. Evidence [H-T06-A02](docs/handoffs.md#h-t06-a02), [H-T05-A02](docs/handoffs.md#h-t05-a02); vận hành [RUNBOOK R11](RUNBOOK.md#r11).

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
- **T03 VERIFIED contracts:** schemas, designed/served OpenAPI snapshots và examples; auth/ownership/readiness/tokenizer enforcement/query/SSE runtime vẫn theo task sau.
- **T04 VERIFIED tooling; T05 VERIFIED Default; T06 VERIFIED Document local:** real setup/validation, unchanged gold và stable reruns. **T07–T08 PLANNED:** Bilingual/all-domain clean reproduction.
- **T09–T12:** authentication, session và storage registration.
- **T13–T19:** format/OCR matrix, model setup, ingestion commands.
- **T20–T26:** query JSON/SSE, history, citations, provider configuration và live smoke.
- **T27–T29:** admin URL/login, UI workflows.
- **T30–T34:** benchmark reports, performance, reliability, backup/restore.
- **T35–T36:** quickstart tích hợp đã kiểm chứng và trạng thái nghiệm thu cuối.

## Nguyên tắc cập nhật

README và RUNBOOK được cập nhật trong từng task; mục mới ghi rõ `DESIGNED`, `IMPLEMENTED` hoặc `VERIFIED` cùng task/evidence. Không quảng cáo tính năng, format hay tốc độ chưa đo. Secrets, tài liệu gốc, model weights và database dumps không thuộc source code.
