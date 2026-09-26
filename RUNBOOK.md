# RAG Core — Runbook vận hành và tích hợp ứng dụng

> **T01–T08 nền tảng và corpus IMPLEMENTED/VERIFIED local.** Default100QA/986documents, Document150QA/84PDF, Bilingual240EN+240VI và1190QA mỗi slice; all-domain setup, tải mới độc lập và rerun đã kiểm. API hiện chỉ serve health; business/auth/query/SSE runtime vẫn DESIGNED. Dừng sau T08 theo workflow một task/session; T09–T36 chưa bắt đầu.
> Nguồn thiết kế: [plan.md](docs/plan.md). Trạng thái thực: [tasks.md](docs/tasks.md) và [handoffs.md](docs/handoffs.md).
> README/RUNBOOK phải được cập nhật trong từng task, không đợi T35 mới viết.

<a id="r00"></a>
## R00. Cách dùng và trạng thái

| Nhãn | Ý nghĩa |
| --- | --- |
| DESIGNED | Đặc tả mục tiêu; chưa được phép nói đang hoạt động |
| IMPLEMENTED | Có code, chưa đủ bằng chứng nghiệm thu môi trường thật |
| VERIFIED | Có task COMPLETE, command/output/commit chứng minh |

| Phần | Trạng thái hiện tại | Task chịu trách nhiệm |
| --- | --- | --- |
| Python setup/settings/quality | VERIFIED | T01 |
| Compose/services + health skeleton | VERIFIED local | T02 |
| API v1 schemas/design snapshots/examples | VERIFIED structural contracts; business routes chưa mount | T03 |
| Corpus | Ba domain và all-domain clean reproduction VERIFIED local | T04–T08 |
| Auth/session/storage | DESIGNED | T09–T12 |
| Parsing/OCR/index | DESIGNED | T13–T19 |
| Query/domains/LLM/SSE | DESIGNED | T20–T26 |
| Admin UI | DESIGNED | T27–T29 |
| Evaluation/load/recovery | DESIGNED | T30–T34 |
| Client tích hợp mẫu/final acceptance | DESIGNED | T35–T36 |

Mỗi mục sau này ghi: task + commit reference, prerequisites, exact command/request, expected output, evidence link và limitations. Không điền PASS mẫu vào log thực thi.

<a id="r01"></a>
## R01. Bối cảnh cho agent tích hợp Scarlet/app khác

Scarlet có FastAPI backend, JWT authentication và PostgreSQL lịch sử hội thoại; hiện gửi prompt tới DeepSeek/Anthropic. RAG core là dịch vụ riêng; tích hợp Scarlet là **công việc sau backlog hiện tại**.

| Trách nhiệm | Ứng dụng chat | RAG core |
| --- | --- | --- |
| User login/JWT issuance | Có | Verify user JWT + app credential |
| Tài liệu gốc | Upload và sở hữu S3/MinIO, backup nguồn | Chỉ HEAD/GET nguồn đã đăng ký |
| Session UI/history | Sở hữu transcript và external session ID | Lưu mapping session, links và scope revision |
| Quyền nguồn object | Backend app chứng thực upload cho user/session | Kiểm principal/session/storage allowlist |
| Metadata/jobs/chunks/vector | Không truy cập DB nội bộ core | PostgreSQL, Celery, Qdrant riêng |
| Generation | Có thể viết lại bằng LLM của app | Trả answer hoàn chỉnh + citations + contexts |
| Delete chat | Gọi delete core và cập nhật transcript app | Tombstone session/links, giữ source/index |

Không import module nội bộ RAG core vào Scarlet, không dùng DB chat của Scarlet làm metadata DB của core. Giao tiếp qua API v1 có schema. App backend giữ service key; browser không gọi core với service key.

<a id="r02"></a>
## R02. Local prerequisites và cấu hình

**T01 IMPLEMENTED/VERIFIED cho Python/settings/quality; T02 IMPLEMENTED/VERIFIED cho Docker local và health; model runtime vẫn DESIGNED cho T17.**

- Windows/PowerShell, Git, Python 3.12, uv và Docker Desktop chạy Linux containers. T01/T02 chạy thật với uv 0.11.16 + CPython 3.12.4 trên host; `pyproject.toml`/`uv.lock` khóa interpreter ở `3.12.*`. API image dùng Python 3.12.13 pin digest. Docker daemon đã verify server 29.5.2.
- RAM 16 GB, GPU NVIDIA 8 GB tùy chọn cho inference; CPU path dùng để xác minh chức năng. Driver/WSL GPU passthrough phải kiểm thực tế.
- Chừa disk cho source <=1 GB, corpus benchmark, parsed text/index, Docker images và model cache riêng; không dùng 1 GB làm dự báo dung lượng tổng.
- `.env.example` chỉ chứa tên biến/default không bí mật. Copy thành `.env`, điền URL bắt buộc, và giữ mọi credential trong `.env`/secret store; không commit hoặc paste vào handoff.

### Bootstrap và quality gate T01–T03

Chạy từ root repository. Trong môi trường bị giới hạn quyền ghi cache user, dùng hai biến local ở đầu; môi trường thường có thể bỏ hai dòng đó.

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'
$env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'
uv sync --locked --group dev --group api
uv run ruff check .
uv run mypy src
uv run pytest tests/unit
uv run pytest tests/contract/test_api_schema.py
uv run python scripts/export_openapi.py --check
uv run python scripts/check_docs.py
```

Kết quả T01: sync tạo `.venv` bằng Python 3.12.4; quality/settings suite PASS tại [H-T01-A01](docs/handoffs.md#h-t01-a01). T02 sync cả `api`, chạy Ruff/mypy/docs và 7 unit tests health/settings; evidence tại [H-T02-A02](docs/handoffs.md#h-t02-a02). Không đổi `.python-version` sang 3.13 khi host chỉ expose 3.13.

[H-T02-A03](docs/handoffs.md#h-t02-a03) ghi việc tiếp quản candidate A02 chưa commit, kiểm lại locked env/quality/current Docker và SHA-256 toàn Python source trong API image cuối. Outage và restart persistence kế thừa evidence A02, không được gọi là đã chạy lại trong A03.

| Dependency group | Trạng thái T01 | Nội dung/phạm vi |
| --- | --- | --- |
| base | IMPLEMENTED/VERIFIED | Pydantic v2 + pydantic-settings cho typed config |
| dev | IMPLEMENTED/VERIFIED | Ruff, mypy, pytest, pytest-asyncio; jsonschema 4.26.0 từ T03 để validate exported schemas/examples, không vào API image |
| api | IMPLEMENTED/VERIFIED T02 | FastAPI, HTTPX, Uvicorn, psycopg, Redis client; health-only API process, không có business routes |
| ingestion | LOCKED/DESIGNED | Alembic, boto3, Celery, Qdrant client, Redis, SQLAlchemy; chưa có worker |
| inference | RESERVED/DESIGNED | Rỗng có chủ đích; T17 pin model runtime/revisions sau capability checks |

### Typed settings đã triển khai

| Biến | Kiểu / mặc định | Bắt buộc | Bí mật / lưu ý |
| --- | --- | --- | --- |
| `APP_ENV` | `development\|test\|production`; `development` | Không | Không |
| `LOG_LEVEL` | `DEBUG\|INFO\|WARNING\|ERROR\|CRITICAL`; `INFO` | Không | Không |
| `API_BIND` | địa chỉ IPv4/IPv6; `127.0.0.1` | Không | Không |
| `API_PORT` | integer 1–65535; `8000` | Không | Không |
| `REQUEST_TIMEOUT_SECONDS` | >0 và <=300; `30` | Không | Không |
| `HEALTH_TIMEOUT_SECONDS` | >0 và <=30; `2` | Không | Deadline cho từng probe readiness |
| `DATABASE_URL` | PostgreSQL DSN | Có | Có thể chứa credential; bị loại khỏi repr/error chuẩn hóa |
| `DATABASE_PASSWORD_FILE` | path; `None` | Không | Docker secret tách khỏi DSN; chuỗi rỗng được bỏ qua |
| `REDIS_URL` | Redis DSN | Có | Có thể chứa credential; bị loại khỏi repr/error chuẩn hóa |
| `QDRANT_URL` | HTTP(S) URL | Có | Endpoint vector nội bộ; bị loại khỏi repr |

`rag_core.config.load_settings()` đọc environment rồi `.env`, bỏ qua giá trị rỗng. Thiếu config trả `SettingsError` dạng `Missing required RAG Core configuration: DATABASE_URL, QDRANT_URL, REDIS_URL`; giá trị malformed không được echo qua error/traceback. T02 readiness dùng PostgreSQL `SELECT 1`, Redis `PING` và Qdrant `/readyz`, mỗi probe có deadline.

| Nhóm env mục tiêu | Nội dung | Task |
| --- | --- | --- |
| Runtime | APP_ENV, LOG_LEVEL, API_BIND/API_PORT, request timeout đã typed; body limits còn DESIGNED | T01–T02 |
| Metadata/broker | DATABASE_URL, REDIS_URL | T02/T10/T12 |
| Vector/model | QDRANT_URL đã typed T02; API key, INFERENCE_URL, model IDs/revisions/device/batches còn DESIGNED | T02/T17–T18 |
| App identity | cấu hình app_id, service-key hash/reference, JWT issuer/audience/JWKS, algorithms | T09 |
| Source storage | storage alias, endpoint, region, bucket/prefix allowlist, read-only credential reference | T11 |
| Providers | DEEPSEEK_API_KEY/MODEL, ANTHROPIC_API_KEY/MODEL; base URLs phía server | T23 |
| Admin | password hash/secret, cookie config, expiration/CSRF | T27 |

Tên biến chính xác và defaults phải đồng bộ settings/`.env.example` khi implement; bảng này là nhóm contract, không phải danh sách env đã tồn tại.

### Quickstart Docker health skeleton T02

Các lệnh sau đã chạy thật từ root repository. Script bootstrap tạo ba file secret local dưới `.local/secrets/` đã ignore, giữ file có sẵn và không in giá trị:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\bootstrap_local.ps1
docker compose config --quiet
docker compose --profile local-storage up -d --build
docker compose --profile local-storage up -d --wait postgres qdrant redis api minio
docker compose --profile local-storage ps --all
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\smoke_local.ps1
```

Expected/verified: `api`, `postgres`, `qdrant`, `redis`, `minio` healthy; `minio-bootstrap` exit 0 sau khi tạo/kiểm fixture. API ở `http://127.0.0.1:8000`, MinIO API/console ở `http://127.0.0.1:9000` và `http://127.0.0.1:9001`. PG 5432, Qdrant 6333/6334 và Redis 6379 chỉ nội bộ. Profile MinIO mô phỏng app storage; API health T02 chưa dùng storage nên MinIO không nằm trong readiness.

Health contract:

```text
GET /health/live   -> 200 {"status":"ok"} khi process phục vụ HTTP
GET /health/ready  -> 200 status=ready khi PG/Redis/Qdrant đều đạt
GET /health/ready  -> 503 status=unavailable + component status khi một dependency lỗi
```

Stop/start giữ nguyên named volumes và fixtures:

```powershell
docker compose --profile local-storage stop
docker compose --profile local-storage up -d
docker compose --profile local-storage up -d --wait postgres qdrant redis api minio
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\smoke_local.ps1
```

Không dùng `docker compose down -v` trong flow mặc định. Không commit `.local/`, `.env`, key hoặc database files. MinIO/MC dùng release community lịch sử đã pin từ official Quay cho local simulation; server/cloud deployment ngoài scope.

Nếu readiness lỗi, dùng `docker compose --profile local-storage ps --all` rồi `docker compose logs --no-color <service>`; không render `docker compose config` đầy đủ vào ticket vì có thể lộ config khi operator tự thêm biến. Business quickstart (migration, ingest/query, model, auth/admin) vẫn DESIGNED cho các task sau.

<a id="r03"></a>
## R03. Auth, app registration và trust boundary

**DESIGNED — T09/T11/T27.**

- Core operator đăng ký app bằng cấu hình tin cậy: app ID, service credential, JWT issuer/audience/JWKS và storage alias/prefix.
- Mỗi API nghiệp vụ gửi `Authorization: Bearer <user-JWT>` và `X-RAG-Service-Key: <app-service-key>`.
- Core lấy subject từ JWT đã verify; app ID từ service identity đã verify; không cho request body ghi đè identity.
- Backend app phải xác minh người dùng được phép dùng object trước đăng ký. Core không có quyền tự đọc DB quyền của Scarlet; chữ ký/trust contract này là trách nhiệm tích hợp.
- Key rotation, JWKS cache TTL, revoked key behavior và local token generation command: điền sau T09 với evidence.
- Không đưa token/service key vào query string, metrics label, logs hoặc browser JS. Không dùng chung admin credential với API app.

401: credentials invalid/missing. 403: role không đủ. 404: resource không thuộc principal/scope. Không tắt auth để tránh lỗi tích hợp.

<a id="r04"></a>
## R04. Session mapping và upload registration

**DESIGNED — T10–T12/T19.**

Luồng app bắt buộc:

1. User chọn/upload tài liệu trong một phiên chat của app.
2. App upload vào S3/MinIO của app; xác minh quyền object thuộc user và upload của session đó.
3. App tạo/resolve core session bằng external_session_id; lưu core session UUID trong metadata app.
4. App backend register upload cho core session với Idempotency-Key; không dùng UUID browser gửi mà bỏ ownership checks.
5. Nhận HTTP 202 với document/job IDs; poll job đến ready hoặc lỗi có cấu trúc.
6. Chỉ query tập tài liệu ready, đúng core session; document subset ngoài session bị từ chối.

Payload mục tiêu cho `POST /v1/sessions/{session_id}/documents`:

```json
{
  "external_upload_id": "upload-event-id-from-app",
  "source": {
    "storage_alias": "configured-app-storage",
    "bucket": "allowed-bucket",
    "key": "allowed-owner-prefix/report.pdf",
    "version_id": "object-version-if-available",
    "sha256": "expected-content-sha256"
  },
  "filename": "report.pdf",
  "content_type": "application/pdf"
}
```

Các chuỗi trên là placeholders, không là dữ liệu đã verify. Schema source version/checksum yêu cầu ít nhất một cách xác minh immutable object; core tính hash từ stream. Không xem ETag multipart là SHA-256. Endpoint lấy từ server config, không nhận arbitrary URL/presigned URL trong bản đầu.

Session mới không tự dùng index cũ. Upload registration mới của cùng file có thể reuse computation cùng owner/fingerprint, nhưng phải tạo link mới hợp lệ. Link ràng buộc version cụ thể, không tự đổi nguồn của citations cũ.

Idempotency-Key scope app+owner+session+request hash; cùng key/body trả cùng job, khác body 409. App retry lỗi transport bằng cùng key; không tạo upload mới chỉ vì HTTP response bị mất.

<a id="r05"></a>
## R05. Endpoint inventory và lỗi

**T03 schemas/snapshots/examples VERIFIED; health runtime VERIFIED tại T02; mọi business/admin route còn DESIGNED và chưa mount.** [P06](docs/plan.md#p06) là nguồn thiết kế, modules `rag_core.contracts.v1`/`sse` là nguồn machine-readable hiện tại. T26 sẽ mount business routes sau runtime gates tương ứng.

| Method / route | Contract request → response | Trạng thái runtime / owner |
| --- | --- | --- |
| POST `/v1/sessions` | SessionCreateRequest → SessionResponse | DESIGNED, chưa mount / T10 |
| GET/DELETE `/v1/sessions/{session_id}` | path UUID → SessionResponse | DESIGNED, chưa mount / T10 |
| POST `/v1/sessions/{session_id}/documents` | DocumentRegisterRequest → 202 DocumentRegisterResponse | DESIGNED, chưa mount / T12 |
| GET `/v1/sessions/{session_id}/documents` | cursor, limit 1–50 → DocumentListResponse | DESIGNED, chưa mount / T12 |
| DELETE `/v1/sessions/{session_id}/documents/{document_id}` | path UUIDs → DetachResponse | DESIGNED, chưa mount / T12 |
| GET `/v1/jobs/{job_id}` | path UUID → JobResponse | DESIGNED, chưa mount / T12/T19 |
| POST `/v1/jobs/{job_id}/retry` | path UUID → JobResponse | DESIGNED, chưa mount / T12/T19 |
| POST `/v1/query` | QueryRequest → QueryResponse | DESIGNED, chưa mount / T24/T26 |
| POST `/v1/query/stream` | QueryRequest → SSE frames (parsed SSEEvent contract) | DESIGNED, chưa mount / T25/T26 |
| GET `/v1/sessions/{session_id}/citations/{chunk_id}` | path UUID/chunk ID → CitationResolveResponse | DESIGNED, chưa mount / T24 |
| GET `/health/live`, `/health/ready` | LiveResponse / ReadyResponse, ready lỗi 503 | VERIFIED served / T02 |
| `/admin/*`, `/v1/admin/*`, protected `/metrics` | Deferred metadata/UI/metrics inventory; chưa chốt action schemas | DESIGNED / T27–T29/T32 |

Không có route xóa object nguồn, arbitrary search hoặc user-wide query bỏ session.

| Tình huống | Contract mục tiêu | Hành động client |
| --- | --- | --- |
| Auth invalid | 401 | Làm mới JWT/sửa service config; không retry vô hạn |
| Resource ngoài scope | 404 | Không fallback sang session/kho khác |
| Session đã xóa (đúng owner) | 410 | Dừng query; không tự recreate rồi attach file cũ |
| Session rỗng | 409 `no_session_documents` | Yêu cầu upload/register trong session |
| Selected document chưa ready | 409 `documents_not_ready` | Poll job, retry hoặc chọn ready subset hợp lệ |
| Idempotency key khác body | 409 | Sửa logic request/key, không overwrite |
| Invalid domain/subset/limits | 422 | Sửa payload |
| Thiếu bằng chứng sau retrieval | 200 + `insufficient_evidence` | Hiển thị answer tự nhiên, không bịa nguồn |
| Rate limit/queue full | 429 + Retry-After | Backoff có giới hạn, ghi admission failures |
| Provider/dependency/timeout | 502/503/504 | Hiển thị lỗi kỹ thuật; không coi là insufficient |

Error JSON: `error.code`, `error.message`, `error.retryable`, `request_id`; `error.details` là list chỉ gồm allowlisted field/reason, không có raw input/stack. Adapter tương lai phải chọn message public đã redacted, không dump trực tiếp ValidationError/exception. 429 có `Retry-After`. Health 503 giữ body riêng `status/components` của T02. Route chưa mount hiện trả framework 404 `{"detail":"Not Found"}`, chưa là business error envelope đã implement.

### Export và validation T03

```powershell
uv run python scripts/export_openapi.py
uv run python scripts/export_openapi.py --check
uv run pytest tests/contract/test_api_schema.py
```

Prerequisites: `uv sync --locked --group dev --group api`, Python 3.12; không cần DSN/secrets/services/provider. [Designed snapshot](docs/api/openapi-v1.designed.json) có 13 operations với `x-served`/`x-implementation-status`; [served snapshot](docs/api/openapi.served.json) được inspect từ factory, chỉ 2 health paths. `/openapi.json` của app là served schema, không quảng cáo business routes. [JSON examples](docs/api/examples-v1.json) gồm 37 trường hợp synthetic với `schema` và `value`: default/document/multilingual queries, registration/lifecycle, supported/insufficient response, notified history truncation, đủ locators và SSE done/error traces. Không dùng những examples này làm live result.

Exporter validate OpenAPI qua FastAPI OpenAPI model, refs local và từng schema bằng `jsonschema` Draft 2020-12, mỗi example theo exported component schema có UUID format checker, rồi theo Pydantic và serialization round-trip. `--check` kiểm snapshot drift, không ghi file. Schema biểu diễn domain/subset conditional constraints, enum, lengths/bounds, unique document/language lists, source fingerprint và discriminated locator/event. Quan hệ citation/context, answer IDs/reason, locator range ordering, history count consistency và SSE event sequence là additional Pydantic checks; JSON Schema không thay thế các checks này. Auth, ownership, trusted upload link/allowlist, ready version/generation, measured file parsing, tokenizer budgets, factual quote/support và scope revalidation là runtime gates ở task sau. Actual evidence [H-T03-A02](docs/handoffs.md#h-t03-a02); [H-T03-A01](docs/handoffs.md#h-t03-a01) chỉ ghi recovery/runtime reports, không thay command outputs A02.

Compatibility: đây là design v1 đầu tiên, không có client business/runtime trước đó hoặc DB migration. Khi schema thay đổi, regenerate snapshots/examples và chạy contract/export checks trong cùng task; breaking v1 change cần ghi migration/client impact theo P13, không sửa snapshot riêng để tránh gate.

<a id="r06"></a>
## R06. Query, history và languages

**T03 structural contracts VERIFIED; retrieval/history processing/generation runtime DESIGNED — T20–T26.**

- Bắt buộc session_id và câu hỏi; `domain` mặc định `default` nếu vắng mặt. Examples gửi rõ domain để người tích hợp dễ đối chiếu.
- Default: tất cả ready documents của session; không nhận document subset.
- Document: `document_ids` bắt buộc, nonempty, mọi ID là subset của session.
- Multilingual: toàn bộ session hoặc subset, optional `corpus_languages`, `answer_language`; chỉ EN/VI được nghiệm thu bản đầu.
- Empty array là lỗi, không “all”. Tài liệu selected chưa ready không âm thầm bị loại khỏi câu trả lời.
- Default không nhận `document_ids`, kể cả explicit null; serialization Pydantic tự bỏ `document_ids=None` để request hợp lệ round-trip. Với Multilingual, bỏ/null subset nghĩa toàn bộ tài liệu hợp lệ trong session; `[]` vẫn invalid. `bilingual` là nhãn corpus, không là API domain.
- App gửi history `user/assistant` trong request, core không lưu transcript mặc định. Giới hạn mục tiêu 20 messages/8.000 tokens; trả metadata khi truncation.
- Schema chấp nhận history vượt processing budget, không cắt/reject theo token ước lượng. Runtime T20 phải cắt bằng tokenizer thật; SSE `meta.history` và JSON `warnings[{code:history_truncated,message,history}]` báo received/retained message và token counts + `truncated`. Token counts chưa đo dùng cả hai null; không bịa 0. Schema kiểm count consistency, không hứa đã xử lý history.
- History giúp rewrite câu hỏi nối tiếp; không cung cấp factual evidence từ session/tài liệu khác. Core chỉ trích dẫn passages vừa được xác minh current scope.
- Default answer language theo câu hỏi; có override cho evaluation/app. Cross-lingual evaluation dùng language của gold answer, không nhầm với default sản phẩm.

Response đầy đủ: `request_id`, `session_id`, `scope_revision`, `domain`, `answer`, `answerability`, `reason_code`, `citations`, `contexts`, `usage`, `timings_ms`, `warnings` theo [P06](docs/plan.md#p06).

`ContractLimits` giữ defaults: 50 documents/session, 104857600 bytes/file (100 MiB), 1000 pages/file, 20 history messages/8000 tokens, question 4000 characters, context 8000/output 1024 tokens. Question/subset/metadata/file measurements có boundary tests; file bytes/pages phải đo từ nguồn và enforce ở ingestion, tổng session docs ở lifecycle, context/output/history tokens bằng tokenizer runtime. Client không override limit/provider/model/system instructions/identity trong body. `usage.provider/model/input_tokens/output_tokens` và `timings_ms.retrieval/generation/total` chưa có dùng null; ví dụ không có measurement giả.

### App gọi LLM viết lại

Scarlet có thể dùng contexts/citations cùng answer của core làm input LLM riêng. App phải giữ source IDs/locator và trạng thái insufficient; không tự tạo citations mới rồi gắn nhãn đã được core verify. Nếu app đổi factual content, phần trả lời đó cần quy trình validation của app.

<a id="r07"></a>
## R07. Streaming client và cancellation

**T03 payload/logical trace contracts VERIFIED; streaming transport/provider/cancel runtime DESIGNED — T25/T35.**

- Dùng HTTPX async stream hoặc fetch streaming cho POST có headers auth; không dựa native EventSource GET.
- Parse UTF-8 incremental và SSE event frames theo dòng trống; chunk TCP không đồng nghĩa một event hoặc một ký tự hoàn chỉnh.
- Event order: `meta -> evidence -> answer_delta* -> done|error`; heartbeat comments không là answer text.
- Retrieval/scope failure sau meta có thể kết thúc `meta -> error` trước evidence. Logical completed trace có đúng một terminal, ID integer dương tăng trong request; final request/session/revision/domain/evidence và history truncation metadata phải khớp meta/evidence. EOF không terminal là incomplete. Whitespace delta hợp lệ.
- Wire là UTF-8 SSE `id: ...`, `event: ...`, `data: <JSON>` và dòng trống; snapshot `SSEEvent` là representation của event đã parse, không là JSON response body trực tiếp. `SSESequence` là validator của complete event trace; heartbeat `: keep-alive` không có event/id/data và không nằm trong trace.
- Hiển thị delta là tạm; chỉ lưu transcript final khi nhận `done` hợp lệ. Nhận `error`/EOF không done thì đánh dấu incomplete.
- `done` chứa final response đã validate; citations/contexts không tự lấy từ một stream trước để bù phần thiếu.
- UI cancel/disconnect phải đóng upstream HTTP connection; server giải phóng semaphore. Không retry stream đang phát rồi nối thêm answer mới.
- Detach/delete giữa stream: core kiểm scope revision, phát `session_scope_changed` và dừng. Bytes đã gửi không thể thu hồi; client phải ngừng dùng answer chưa hoàn tất.
- Runtime phải revalidate trước evidence, mỗi batch delta và done; JSON revalidate trước serialize. T03 chưa thực hiện những checks runtime này và chưa claim query/SSE live verification.
- Event IDs chỉ trong request; chưa hỗ trợ resume/replay. Heartbeat/idle/total timeout defaults sẽ ghi sau đo thực.

T35 sẽ thêm client FastAPI/HTTPX độc lập chạy thật, xử lý chunk boundaries, lỗi, history và cancellation. Không gọi pseudocode hiện tại là integration đã kiểm chứng.

<a id="r08"></a>
## R08. Citations, xóa chat và retained index

**T03 locator structural schemas VERIFIED; parsing/resolver/scope/lifecycle runtime DESIGNED — T10/T16/T24/T25.**

| Format | Vị trí nguồn |
| --- | --- |
| PDF | Physical page one-based, optional block/offset; printed label field riêng |
| DOCX | Heading + paragraph/table index; không có page giả |
| XLSX | Sheet + cell range/header context |
| PPTX | Slide one-based + block |
| TXT/MD/HTML/CSV/image | Lines/paragraphs/rows/OCR block tương ứng |

App hiển thị filename+locator, dùng citation resolver có auth/current session để lấy metadata/quote. Core không phát URL public của object; app tự cấp download link nếu quyền ứng dụng cho phép. Resolver recheck scope; retained chunk UUID không là vé truy cập.

Machine fields: PDF `page` physical one-based + optional `printed_page_label`; DOCX `heading_path` + `paragraph` hoặc `table`; XLSX `sheet/cell_range/headers/unit`; PPTX `slide/shape/block`; TXT/MD `line_start/line_end` hoặc `paragraph`, optional half-open `offsets.start/end`; CSV `row_start/row_end/columns`; HTML `heading_path/block`; image `image_id/ocr_block/bbox` (pixel x0/y0/x1/y1). Lines/rows/slides/pages one-based; paragraph/table/shape/block indices zero-based. DOCX/XLSX/PPTX/text/CSV/HTML/image không nhận page giả. Storage `source.version_id` là chuỗi opaque, còn response/citation `version_id` là UUID DocumentVersion nội bộ; không lẫn hai định danh.

Xóa chat:

1. App gọi DELETE core session, core tombstone và tăng scope revision.
2. App cập nhật/xóa transcript UI theo policy app; HTTP failure phải retry idempotent hoặc reconcile, không giả định core đã xóa.
3. Tài liệu gốc, chunks và vector giữ nguyên; old session không còn query/resolve citations được.
4. Session mới chỉ dùng tài liệu có upload registration/link của chính session đó.

Không có auto-delete derivative khi session hết link ở bản đầu. Admin theo dõi disk; chính sách retention/purge trong tương lai cần quyết định riêng, không tự thêm TTL.

<a id="r09"></a>
## R09. Ingestion, formats và xử lý lỗi

**DESIGNED — T13–T19.**

Format nghiệm thu mục tiêu: PDF text/scan/mixed, DOCX, XLSX, PPTX, TXT, MD, CSV, HTML, PNG/JPEG; OCR eng/vie. Không hỗ trợ Office legacy/audio/video trong bản đầu.

Job: queued/fetching/parsing/chunking/embedding/indexing/ready hoặc failed/cancelled. Trạng thái PG là nguồn bền; Redis chỉ broker. Index generation chỉ visible sau publication thành công.

Limits mục tiêu: 100 MiB/file, 1.000 trang, 50 docs/session; sẽ đồng bộ config và boundary tests. XLSX formula không được execute; cached value thiếu phải thông báo. Mixed PDF tránh OCR trùng text layer. Source changed giữa download báo lỗi, không index bản trộn.

Điền sau implementation: register/poll/retry examples, progress fields, supported-format matrix với fixture/evidence, concurrency/batch controls, source_changed/extraction_failed/error codes, reindex/cancel behavior và orphan cleanup scoped.

<a id="r10"></a>
## R10. UI quản trị

**DESIGNED — T27–T29.**

URL mục tiêu local: `http://127.0.0.1:8000/admin`. Chưa có UI tại T00.

Login riêng; screens Overview/Documents/Jobs/Sessions/Index/Evaluation reports. Admin có thể xem metadata, retry/cancel jobs, detach/tombstone sessions, enqueue reindex trong policy; mọi action audit actor/target/time/request ID và CSRF protection.

Không xem raw chunks/answers/prompts của user, không xem secrets hoặc xóa source. Không có arbitrary query trên toàn kho. Khi cần thử RAG, dùng app/user/session fixture qua public API chuẩn.

Điền sau T29: admin secret generation/login/logout, permissions, cookie expiration, browser flows, screenshots redacted, diagnostics và cách xử lý job lỗi.

<a id="r11"></a>
## R11. Corpus và quality evaluation

**T04–T08 tooling, ba domain và all-domain clean reproduction VERIFIED local; evaluation DESIGNED — T30–T31.**

Prompt gốc: [Build RAG Evaluation Corpus](corpus-documents/Codex%20Prompt%20%E2%80%93%20Build%20RAG%20Evaluation%20Corpus.md).

- Default: HotpotQA dev distractor, deterministic 100 QA, corpus riêng khỏi QA.
- Document: FinanceBench open-source QA/PDF/evidence; giữ zero-based gold pages, chuyển ở adapter eval.
- Bilingual dataset: full XQuAD EN/VI với en_en/vi_vi/vi_en/en_vi; runtime domain là multilingual.
- Official licenses/source revision/checksum/counts phải ghi manifest thực; raw data/PDF không mặc định commit.
- Evaluation chỉ ingest documents, không QA/answers/supporting facts/justification. Không lọc gold pages hoặc gold docs để làm đẹp retrieval.
- XQuAD không có unanswerable; kiểm refusal/insufficient bằng fixture riêng và báo riêng.

Prerequisites: Python `3.12.*`, `uv sync --locked --group dev --group api`; shared utilities stdlib, schema dev-only jsonschema; T05 thêm `pyarrow==25.0.1`, T06 thêm dev-only `pypdf[crypto]==6.19.0` để đếm trang PDF/AES. Không dependency nào vào API image/model runtime. Không cần DSNs/services/providers/models. Commands từ root:

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
uv run python corpus-documents/scripts/setup_corpus.py --domain bilingual
uv run python corpus-documents/scripts/validate_corpus.py --domain bilingual
uv run pytest tests/unit/test_corpus_bilingual.py
```

`--metadata-only` chỉ kiểm inventory/schema/provenance/aggregate; không nghiệm thu data. [Corpus README](corpus-documents/README.md), [inventory](corpus-documents/source-license-inventory.json), [manifest](corpus-documents/manifest.json) ghi Default ready 100 QA/986 documents, Document ready 150 QA/84 PDF và Bilingual ready 480 language-specific documents/4760 QA slice rows. Default source có measured 7405 rows/27,452,575 B; JSON conversion hash và distributions/report tại `default/qa/preparation.json`, document ID/path/hash/source-question map tại `default/qa/documents.json` (evaluator only). Markdown chỉ title/dataset/document ID/original paragraph, toàn distractors được materialize. 996 instances dedup còn 986; identity dùng title+exact concatenated sentences. Sample seed42 cân bằng available type/level: 50 bridge/50 comparison/all hard; upstream không có medium. Default validator recompute source conversion, sampled IDs, gold/type/level/supporting-only mapping, every document/receipt/count và exact file set. Bilingual pinned XQuAD EN/VI version 1.1 at `7d30520c717524000f0d9d2f9c10a069acd9d285`: 240 aligned paragraph groups, 240 EN and 240 VI retrieval documents, and 1190 rows in each `en_en`, `vi_vi`, `vi_en`, `en_vi` QA slice. Alignment keys are article title + exact counterpart QA-ID sets (not positional order); source questions/answers do not enter retrieval document text. Measured raw SHA256, source receipts, and output checksums are in `bilingual/qa/preparation.json` and the bilingual manifest. Validation rechecks source hashes/pins, structure/alignment, evaluator gold-answer spans, and exact artifact sets. XQuAD is CC-BY-SA-4.0 and has no unanswerable examples.

Utilities bounded retries/timeout/size, exact pins/content/length trước atomic replace; references reject traversal/Windows streams/links/junctions. Default setup lock `.downloads/default-setup.lock` ngăn concurrent writers; stage nguyên domain, validate rồi swap + aggregate publication; ordinary failure/interruption rollback giữ last good. Readers/eval phải chờ setup kết thúc (directory rename không là concurrent reader transaction). Equal trees không publish lại, giữ timestamp/mtimes. Source download receipt giữ original downloaded_at khi cache reuse; failed stages/rollback backups nằm ignored `.downloads/default-stage-*`, không tự xóa. Unknown files trong default bị refuse, không overwrite user files. Nếu lock còn sau process crash: kiểm process và stage/backup trước khi operator gỡ lock; không tự bypass lock hoặc xóa dữ liệu.

T07-A06: [evidence](docs/handoffs.md#h-t07-a06) records separate real setup/validation,
491 published files plus 3 cache receipts/files unchanged on rerun (hashes, mtimes,
slice IDs and downloaded_at), and isolated synthetic unit tests. This verifies the
existing local corpus; fresh downloads are verified separately in T08 below.

Windows tests can use a fresh short ignored basetemp to avoid inherited TEMP ACLs:
set `$env:PYTEST_ADDOPTS='--basetemp=.local/<fresh-run-name>'` before pytest. Use a
new name each run; pytest may remove an existing basetemp. Bilingual fixtures use
compact directory names while keeping full SHA256 document IDs. `.local` is local
test/runtime state, excluded from documentation traversal. Legacy Hermes scratch
is preserved and must not be committed or deleted as part of task completion.

Bilingual publication uses `.downloads/bilingual-setup.lock`, complete staging under
`.downloads/bilingual-stage-*`, validation before swap and aggregate rollback on
failure. Corrupt published data, unknown files or an existing lock cause refusal;
inspect the relevant process and retained stage before operator recovery. No
automatic lock bypass, source deletion or concurrent-reader transaction is provided.

All-domain setup and validation are **VERIFIED in T08**:

```powershell
uv run python corpus-documents/scripts/setup_corpus.py --all
uv run python corpus-documents/scripts/validate_corpus.py --all
```

Default data verified theo ngoại lệ user-approved ngày2026-09-17 tại [P11](docs/plan.md#p11): CMU HTTP/HTTPS GET timeout20s, dùng HF community derivative `hotpotqa/hotpot_qa` distractor/validation revision `1908d6afbbead072334abe2965f91bd2709910ab`. Exact published/downloaded Parquet SHA256 `c20b638ca82b21d04fe12e14ff417ad05153d4d215a65de54497fca4e972f7c6` và bytes27452575; HTTPS delivery allowlist chỉ exact HF source + inspected `us.aws.cdn.hf.co/xet-bridge-us/`, mandatory pin, signed queries không log. Không claim official author mirror/CMU byte-equivalence; sourceoriginal repository vẫn `3635853403a8735609ee997664e1528f4480762a`, legacy JSON là semantic conversion. Dataset/card CC BY-SA4.0 và attribution/change notices trong [licenses](corpus-documents/licenses/README.md). One full-source annotation anomaly: ID`5ae61bfd5542992663a4f261`, `Jimmy Butler (basketball)`, index902/5sentences; giữ rawgold, report ngoài100subset. Selected sentence ranges/title checks nghiêm; anomaly trong sample fail, không sửa/drop/resample. Không claim toàn7405annotations sạch.

Document T06 dùng FinanceBench pin `cc39aeb4afdf33909ee1412188bf89035950c2eb`: 150 `OPEN_SOURCE` QA, 84/368 repository PDFs được reference, 189 evidence; không tải 284 PDF ngoài QA. Hai source SHA256 là `a5a2aa673e573e55675fc3c0f9aa38c1cf59d2abc91edb077534f71f10a71877` và `1c69127783879de8cdadb159d2181f39bc3123b8e0ebf74031c3969d69189575`. PDF thực tổng165,527,662B/12,013pages; gold pages0–303 zero-based, 0 out-of-range. Validator reconstruct normalized QA từ raw, giữ exact answer/evidence/full-page text/justification/metadata, mở từng PDF và kiểm exact89artifact receipts. 50 justification/reasoning null giữ null; duplicate metadata `FOOTLOCKER_2023_annualreport` không được QA reference nên report, duplicate referenced sẽ fail. Future eval adapter mới đổi citation sang physical one-based.

Document writer dùng `.downloads/document-setup.lock`, resumable verified PDF cache, complete-domain stage và rollback domain+aggregate. Rerun giữ91 published hashes/mtimes/150IDs/downloaded_at và84 PDF cache hashes/mtimes, không network download lại. Failed stage giữ ở `.downloads/document-stage-*`; reader/eval chờ setup xong. Existing user plan authorizes local evaluation download nhưng không phải upstream redistribution/commercial grant. GitHub tree/README không có explicit dataset/PDF grant; publisher card `e04404e3a97f69f79c14d42f24981a1c9c3bcd18` riêng khai CC-BY-NC4.0; company PDF rights riêng. Vì vậy raw/PDF/normalized FinanceBench QA đều local ignored, chỉ manifest hashes/counts/attribution track. Bilingual T07/XQuAD pin `7d30520c717524000f0d9d2f9c10a069acd9d285`, datasetCC-BY-SA4.0; all-domain clean reproduction verified in T08. Không arbitrary source override hoặc mirror khác.

Troubleshooting: all-domain setup/validation đã hoạt động từ T08. Default/Document network failure giữ prior corpus và forensic stage; cache-only rerun không thay thế first live download proof. Corrupt/truncated/PDF parse/page-range failure fail trước publication; T06 transfer2attempts, metadata30s/4MiB, PDF60s/32MiB. `pypdf` AES `DependencyError` cần locked crypto extra, không bỏ page gate. Source checksum/gold/evidence/file drift fail nonzero, không sửa/drop/resample source. Actual T06 live setup/validator/rerun và synthetic document tests tại [H-T06-A02](docs/handoffs.md#h-t06-a02); Default tại [H-T05-A02](docs/handoffs.md#h-t05-a02); historical tooling [H-T04-A01](docs/handoffs.md#h-t04-a01). Không DB/index/API migration/production ingestion. Full clean reproduction verified in T08; evaluation reports/metrics/provider costs T30–T31, chưa benchmark score.

### T08 clean reproduction and deterministic rerun

Use a new short output name for a cold download. Paths are relative to the current
working directory (repository root in these commands), or absolute. Only direct
children of `corpus-documents/.repro/` are accepted; traversal, reserved Windows names,
trailing dots/spaces, symlinks/junctions and source/script/domain directories are refused.
The directory is ignored in Git and documentation scanning. No canonical corpus is deleted.

```powershell
uv run python corpus-documents/scripts/setup_corpus.py --all --output-root corpus-documents/.repro/a1
uv run python corpus-documents/scripts/validate_corpus.py --all --output-root corpus-documents/.repro/a1
uv run python corpus-documents/scripts/verify_reproduction.py record --output-root corpus-documents/.repro/a1
uv run python corpus-documents/scripts/setup_corpus.py --all --output-root corpus-documents/.repro/a1
uv run python corpus-documents/scripts/verify_reproduction.py check --output-root corpus-documents/.repro/a1
```

The standard corpus must already exist for the fingerprint comparison. `record` writes
one ignored `.verification.json`, refuses to overwrite it, and compares all published
files/QA IDs/counts with the standard corpus. Manifest JSON is compared canonically,
excluding only `downloaded_at`; payload bytes are compared exactly. `check` additionally
requires every published/cache hash, byte count, mtime and download timestamp to match
that baseline. It is a fingerprint check, not a replacement for `validate_corpus.py`.
T08 measured 1574 published files and 92 cache files; content/IDs/counts match the standard
corpus, with new download timestamps. Evidence and every prompt acceptance row:
[H-T08-A01](docs/handoffs.md#h-t08-a01).

A fresh checkout retains ready manifests and some licensed QA but lacks ignored raw/docs.
Setup recognizes this case only when both payload directories are absent and every retained
QA file matches its receipt. It reconstructs via complete domain staging, with measured
new download timestamps. It never silently resets partially missing data or changed QA.
The validator does not bootstrap or repair files; missing or corrupt artifacts fail nonzero.

All/domain CLI runs use `.downloads/corpus-setup.lock`; each domain retains its own lock,
verified transport cache, staging and rollback. An all-domain run publishes domains
sequentially; a failure preserves completed domains, returns nonzero and stops before the
next domain. Rerun can resume verified downloads. Readers must wait until setup finishes.
Inspect interrupted initialization, retained stages and stale locks before operator recovery;
no automatic deletion or lock bypass. Network failures remain failures, never synthetic success.

<a id="r12"></a>
## R12. Hiệu năng và observability

**DESIGNED — T17/T25/T32–T33.**

Target 15–20 virtual users; chưa có SLA latency. Một inference process, bounded queue, ingestion concurrency=1, query ưu tiên hơn indexing. API không load model mỗi worker.

Metrics: request/job stage timings, queue depth, active streams, admitted/rejected, provider errors, RAM/VRAM, storage/index sizes. p50/p95 TTFT chỉ token answer đầu, không tính meta/heartbeat; total tính đến done. Stub và live benchmark báo riêng.

Logs JSON có request/job ID nhưng không ghi raw prompts/docs/tokens/service keys/presigned signatures. `/metrics` được bảo vệ và không dùng user/query làm labels.

Điền sau đo: CPU/GPU profiles, model revisions, batching/concurrency/timeouts, actual RAM/VRAM, latency/throughput/429/error rates, reference hardware, giới hạn được biết và cách nhận biết overload.

<a id="r13"></a>
## R13. Backup, restore và thay đổi index/schema

**DESIGNED — T34.**

- Backup metadata PG và Qdrant snapshot cùng maintenance boundary; ghi model/index/corpus/config revisions, checksum và thời điểm.
- App backup S3 nguồn riêng; core không xóa/sao chép toàn bộ app storage như một phần backup thường lệ.
- Restore sang Compose project/volumes mới; verify session scope, link/version/counts và citations trước chấp nhận.
- Reindex tạo generation mới, publish atomic trong PG, giữ generation cũ khi thất bại. Đổi embedding dimension/revision cần index version mới.
- Migration có explicit command và rollback/recovery plan; không để nhiều worker tự migrate lúc boot.
- Stop/start giữ volumes. Không `down -v` hoặc restore đè môi trường đang dùng trong quickstart.

Điền exact backup/restore commands, manifest schema, quyền truy cập, write pause procedure, test evidence và dữ liệu nào chưa được backup sau T34.

<a id="r14"></a>
## R14. Troubleshooting và incident response

**DESIGNED — cập nhật dần khi lỗi được kiểm chứng.**

| Triệu chứng | Kiểm tra mục tiêu | Không làm |
| --- | --- | --- |
| 401/403 | Issuer/audience/expiry/service app mapping, admin role | Tắt verify JWT |
| Không tìm thấy tài liệu | Session/link/version/readiness/language scope | Mở rộng sang kho user để có answer |
| Job queued mãi | Outbox dispatcher, Redis, worker lease | Đánh ready bằng tay |
| PDF scan rỗng | Tessdata eng/vie, OCR page selection/quality | Tạo text giả hoặc skip OCR DoD |
| Citation sai | Locator/source version/zero-one based adapter | Sửa gold để khớp output |
| Source changed | S3 version/checksum consistency | Index binary khác với version đăng ký |
| GPU/RAM OOM | Batch/token/process/model duplication/queue | Spawn thêm model workers |
| SSE ngắt | Disconnect, provider timeout, scope_revision, terminal event | Lưu partial answer như success |
| Qdrant/PG lệch | Ready generation/outbox/recovery manifest | Xóa toàn bộ volume |

Mỗi mục được triển khai phải bổ sung command chẩn đoán redacted, cách xử lý đã thử, task/evidence và ảnh hưởng dữ liệu. Không paste secrets vào ticket/handoff.

<a id="r15"></a>
## R15. Checklist dành cho agent tích hợp Scarlet sau này

- [ ] Đọc AGENTS, plan P01/P04/P05/P06/P09/P15, final handoff và versions/limitations của core.
- [ ] Xác nhận RAG core đã VERIFIED, API v1/OpenAPI và reference client test đang pass.
- [ ] Đăng ký app service identity, JWT issuer/audience/JWKS; cấu hình storage alias read-only.
- [ ] Tạo mapping Scarlet session -> core session theo authenticated user; không tin browser IDs trực tiếp.
- [ ] Nối app upload -> S3 object -> registration idempotent -> poll ready; mỗi session có link riêng.
- [ ] Truyền query/history/languages/subset đúng scope; render insufficient và technical error riêng.
- [ ] Nối POST SSE với streaming proxy, timeout/cancel/backpressure; không buffer toàn bộ ở proxy vô tình.
- [ ] Render citations filename/page/paragraph/cell đúng, resolve/download có quyền app/current session.
- [ ] Nếu Scarlet gọi LLM lần hai, giữ evidence IDs và answerability; validate factual content theo policy app.
- [ ] Nối detach/delete chat idempotent, retry/reconcile thất bại; giữ source và index, không inherit session mới.
- [ ] Test 2 users + 2 sessions cùng user, prompt history cũ, stale citation, invalid JWT, mixed-language và stream cancellation.
- [ ] Kiểm observability không lộ secrets/nội dung; đối chiếu performance/timeouts và cập nhật README/RUNBOOK của cả hai dự án trong scope được giao.

Checklist này chuẩn bị cho công việc tương lai, **không cho phép agent tự bắt đầu sửa Scarlet trong T00–T36**.
