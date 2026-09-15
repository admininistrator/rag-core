# RAG Core — Runbook vận hành và tích hợp ứng dụng

> **T01 IMPLEMENTED/VERIFIED — nền tảng Python.** Project Python 3.12, uv lock, typed runtime settings và quality commands đã được kiểm chứng. Chưa có command khởi động app/API thực tế hoặc endpoint được kiểm chứng; phần đó vẫn DESIGNED.
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
| Compose/services | DESIGNED | T02 |
| Corpus | DESIGNED; chỉ có prompt người dùng | T04–T08 |
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

**T01 IMPLEMENTED/VERIFIED cho Python/settings/quality; Docker và model runtime vẫn DESIGNED cho T02/T17.**

- Windows/PowerShell, Git, Python 3.12 và uv. T01 chạy thật với uv 0.11.16 + CPython 3.12.4; `pyproject.toml`/`uv.lock` khóa interpreter ở `3.12.*`. Docker sẽ là runtime chuẩn của ứng dụng từ T02.
- RAM 16 GB, GPU NVIDIA 8 GB tùy chọn cho inference; CPU path dùng để xác minh chức năng. Driver/WSL GPU passthrough phải kiểm thực tế.
- Chừa disk cho source <=1 GB, corpus benchmark, parsed text/index, Docker images và model cache riêng; không dùng 1 GB làm dự báo dung lượng tổng.
- `.env.example` chỉ chứa tên biến/default không bí mật. Copy thành `.env`, điền URL bắt buộc, và giữ mọi credential trong `.env`/secret store; không commit hoặc paste vào handoff.

### Bootstrap và quality gate T01

Chạy từ root repository. Trong môi trường bị giới hạn quyền ghi cache user, dùng hai biến local ở đầu; môi trường thường có thể bỏ hai dòng đó.

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'
$env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'
uv sync --locked --group dev
uv run ruff check .
uv run mypy src
uv run pytest tests/unit/test_settings.py
uv run python scripts/check_docs.py
```

Kết quả T01: sync tạo `.venv` bằng Python 3.12.4; Ruff/mypy/docs check PASS; settings suite có 3 tests PASS. Evidence command/output ở [H-T01-A01](docs/handoffs.md#h-t01-a01). Không đổi `.python-version` sang 3.13 khi host chỉ expose 3.13.

| Dependency group | Trạng thái T01 | Nội dung/phạm vi |
| --- | --- | --- |
| base | IMPLEMENTED/VERIFIED | Pydantic v2 + pydantic-settings cho typed config |
| dev | IMPLEMENTED/VERIFIED | Ruff, mypy, pytest, pytest-asyncio |
| api | LOCKED/DESIGNED | FastAPI, HTTPX, Uvicorn; chưa có API process |
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
| `DATABASE_URL` | PostgreSQL DSN | Có | Có thể chứa credential; bị loại khỏi repr/error chuẩn hóa |
| `REDIS_URL` | Redis DSN | Có | Có thể chứa credential; bị loại khỏi repr/error chuẩn hóa |

`rag_core.config.load_settings()` đọc environment rồi `.env`. Thiếu config trả `SettingsError` dạng `Missing required RAG Core configuration: DATABASE_URL, REDIS_URL`; giá trị malformed không được echo qua error/traceback do loader trả. T01 chỉ định nghĩa contract; readiness tới PostgreSQL/Redis thuộc T02.

| Nhóm env mục tiêu | Nội dung | Task |
| --- | --- | --- |
| Runtime | APP_ENV, LOG_LEVEL, API_BIND/API_PORT, request timeout đã typed; body limits còn DESIGNED | T01–T02 |
| Metadata/broker | DATABASE_URL, REDIS_URL | T02/T10/T12 |
| Vector/model | QDRANT_URL/API_KEY, INFERENCE_URL, model IDs/revisions/device/batches | T17–T18 |
| App identity | cấu hình app_id, service-key hash/reference, JWT issuer/audience/JWKS, algorithms | T09 |
| Source storage | storage alias, endpoint, region, bucket/prefix allowlist, read-only credential reference | T11 |
| Providers | DEEPSEEK_API_KEY/MODEL, ANTHROPIC_API_KEY/MODEL; base URLs phía server | T23 |
| Admin | password hash/secret, cookie config, expiration/CSRF | T27 |

Tên biến chính xác và defaults phải đồng bộ settings/`.env.example` khi implement; bảng này là nhóm contract, không phải danh sách env đã tồn tại.

### Quickstart ứng dụng sẽ được kiểm chứng

1. Clone/checkout đúng commit và tạo env từ example.
2. Khởi tạo local dev app credentials/JWT key; cấu hình read-only storage, provider/admin secrets.
3. Build/start Compose, migration metadata và readiness checks.
4. Tải/pin model cache; bật GPU override nếu đã verified.
5. Upload fixture bằng app simulator, create session, register, poll ready, query JSON/SSE.
6. Mở admin UI; stop/start giữ volumes.

Chưa có các command ứng dụng trên ở T01. Khi bổ sung, dùng PowerShell-safe examples; không đưa `docker compose down -v` vào luồng mặc định.

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

**Tất cả DESIGNED tại T00.** [P06](docs/plan.md#p06) là hợp đồng đầy đủ; OpenAPI thực được tạo ở T03 và hoàn thiện ở T26.

| Method / route | Ý nghĩa | Implementation owner |
| --- | --- | --- |
| POST `/v1/sessions` | Create/resolve external session | T10 |
| GET/DELETE `/v1/sessions/{session_id}` | Metadata / tombstone | T10 |
| POST/GET `/v1/sessions/{session_id}/documents` | Register/list trong session | T12 |
| DELETE `/v1/sessions/{session_id}/documents/{document_id}` | Detach, giữ source/index | T12 |
| GET `/v1/jobs/{job_id}` | Job status/progress | T12/T19 |
| POST `/v1/jobs/{job_id}/retry` | Idempotent allowed retry | T12/T19 |
| POST `/v1/query` | Final answer JSON | T24/T26 |
| POST `/v1/query/stream` | SSE | T25/T26 |
| GET `/v1/sessions/{session_id}/citations/{chunk_id}` | Resolve citation trong current scope | T24 |
| GET `/health/live`, `/health/ready` | Process/dependency status | T02 |
| `/admin/*`, `/v1/admin/*`, protected `/metrics` | UI và metadata operations | T27–T29 |

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

Error JSON: `error.code`, `error.message`, `error.retryable`, `request_id`; details không chứa secrets. Exact examples/request schemas sẽ được verify trong T03/T26/T35.

<a id="r06"></a>
## R06. Query, history và languages

**DESIGNED — T20–T26.**

- Bắt buộc session_id và câu hỏi; `domain` mặc định `default` nếu vắng mặt. Examples gửi rõ domain để người tích hợp dễ đối chiếu.
- Default: tất cả ready documents của session; không nhận document subset.
- Document: `document_ids` bắt buộc, nonempty, mọi ID là subset của session.
- Multilingual: toàn bộ session hoặc subset, optional `corpus_languages`, `answer_language`; chỉ EN/VI được nghiệm thu bản đầu.
- Empty array là lỗi, không “all”. Tài liệu selected chưa ready không âm thầm bị loại khỏi câu trả lời.
- App gửi history `user/assistant` trong request, core không lưu transcript mặc định. Giới hạn mục tiêu 20 messages/8.000 tokens; trả metadata khi truncation.
- History giúp rewrite câu hỏi nối tiếp; không cung cấp factual evidence từ session/tài liệu khác. Core chỉ trích dẫn passages vừa được xác minh current scope.
- Default answer language theo câu hỏi; có override cho evaluation/app. Cross-lingual evaluation dùng language của gold answer, không nhầm với default sản phẩm.

Response đầy đủ: `request_id`, `session_id`, `scope_revision`, `domain`, `answer`, `answerability`, `reason_code`, `citations`, `contexts`, `usage`, `timings_ms`, `warnings` theo [P06](docs/plan.md#p06).

### App gọi LLM viết lại

Scarlet có thể dùng contexts/citations cùng answer của core làm input LLM riêng. App phải giữ source IDs/locator và trạng thái insufficient; không tự tạo citations mới rồi gắn nhãn đã được core verify. Nếu app đổi factual content, phần trả lời đó cần quy trình validation của app.

<a id="r07"></a>
## R07. Streaming client và cancellation

**DESIGNED — T25/T35.**

- Dùng HTTPX async stream hoặc fetch streaming cho POST có headers auth; không dựa native EventSource GET.
- Parse UTF-8 incremental và SSE event frames theo dòng trống; chunk TCP không đồng nghĩa một event hoặc một ký tự hoàn chỉnh.
- Event order: `meta -> evidence -> answer_delta* -> done|error`; heartbeat comments không là answer text.
- Hiển thị delta là tạm; chỉ lưu transcript final khi nhận `done` hợp lệ. Nhận `error`/EOF không done thì đánh dấu incomplete.
- `done` chứa final response đã validate; citations/contexts không tự lấy từ một stream trước để bù phần thiếu.
- UI cancel/disconnect phải đóng upstream HTTP connection; server giải phóng semaphore. Không retry stream đang phát rồi nối thêm answer mới.
- Detach/delete giữa stream: core kiểm scope revision, phát `session_scope_changed` và dừng. Bytes đã gửi không thể thu hồi; client phải ngừng dùng answer chưa hoàn tất.
- Event IDs chỉ trong request; chưa hỗ trợ resume/replay. Heartbeat/idle/total timeout defaults sẽ ghi sau đo thực.

T35 sẽ thêm client FastAPI/HTTPX độc lập chạy thật, xử lý chunk boundaries, lỗi, history và cancellation. Không gọi pseudocode hiện tại là integration đã kiểm chứng.

<a id="r08"></a>
## R08. Citations, xóa chat và retained index

**DESIGNED — T10/T16/T24/T25.**

| Format | Vị trí nguồn |
| --- | --- |
| PDF | Physical page one-based, optional block/offset; printed label field riêng |
| DOCX | Heading + paragraph/table index; không có page giả |
| XLSX | Sheet + cell range/header context |
| PPTX | Slide one-based + block |
| TXT/MD/HTML/CSV/image | Lines/paragraphs/rows/OCR block tương ứng |

App hiển thị filename+locator, dùng citation resolver có auth/current session để lấy metadata/quote. Core không phát URL public của object; app tự cấp download link nếu quyền ứng dụng cho phép. Resolver recheck scope; retained chunk UUID không là vé truy cập.

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

**DESIGNED — T04–T08/T30–T31.**

Prompt gốc: [Build RAG Evaluation Corpus](corpus-documents/Codex%20Prompt%20%E2%80%93%20Build%20RAG%20Evaluation%20Corpus.md).

- Default: HotpotQA dev distractor, deterministic 100 QA, corpus riêng khỏi QA.
- Document: FinanceBench open-source QA/PDF/evidence; giữ zero-based gold pages, chuyển ở adapter eval.
- Bilingual dataset: full XQuAD EN/VI với en_en/vi_vi/vi_en/en_vi; runtime domain là multilingual.
- Official licenses/source revision/checksum/counts phải ghi manifest thực; raw data/PDF không mặc định commit.
- Evaluation chỉ ingest documents, không QA/answers/supporting facts/justification. Không lọc gold pages hoặc gold docs để làm đẹp retrieval.
- XQuAD không có unanswerable; kiểm refusal/insufficient bằng fixture riêng và báo riêng.

Commands mục tiêu **chưa tồn tại tại T00**:

```text
python corpus-documents/scripts/setup_corpus.py --all
python corpus-documents/scripts/validate_corpus.py --all
```

T08 điền output/counts thật và clean reproduction. T30–T31 điền commands eval/splits/models/config, full retrieval + generation sample >=130 QA, metrics từng slice/gates/errors/costs, report locations. Không có điểm số baseline tại T00.

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
