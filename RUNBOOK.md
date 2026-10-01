# RAG Core — Runbook vận hành và tích hợp ứng dụng

> **T01–T16 IMPLEMENTED/VERIFIED local.** Default100QA/986documents, Document150QA/84PDF, Bilingual240EN+240VI và1190QA mỗi slice; all-domain setup/tải mới/rerun đã kiểm. Auth, metadata, read-only storage, registration/outbox và native text/Office tables đã kiểm thật. T15 CPU OCR đã kiểm trong worker image; T16 thêm chunking512/64 với tokenizer thật và source maps. API chỉ mount health; business HTTP/query/SSE và Celery ingestion orchestration vẫn DESIGNED. T17–T36 chưa bắt đầu.
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
| Service identity/JWT/JWKS/local issuer | VERIFIED local HTTP; protected endpoint chỉ trong tests | T09 |
| Session/schema/scope repository | VERIFIED real PostgreSQL; HTTP routes chưa mount | T10 |
| S3/MinIO read adapter | VERIFIED real local MinIO; chưa nối HTTP/job | T11 |
| Upload registration, job repository/outbox | VERIFIED real PG/MinIO/Redis; HTTP chưa mount, worker chưa có | T12 |
| PDF text/DOCX/TXT/MD/HTML parsers | VERIFIED real native parsers trên fixtures EN/VI; chưa nối worker | T13 |
| XLSX/CSV/PPTX tables | VERIFIED real parsers, locators/header/unit/formula cache và archive safety; chưa nối worker | T14 |
| OCR scan/mixed PDF, PNG/JPEG | VERIFIED worker image, engine thật EN/VI + locator/status/limits/cancel | T15 |
| Structural chunks/source maps | VERIFIED real tokenizer + parser fixtures trên host, actual worker OCR output mapped | T16 |
| Embedding/index ingestion orchestration | DESIGNED | T17–T19 |
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
uv sync --locked --group dev --group api --group ingestion
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
| ingestion | T11–T15 VERIFIED adapters/OCR worker runtime; orchestration T19 DESIGNED | Metadata, boto3, Celery, Qdrant/Redis; Docling Parse7.22.1/slim2.132.0 convert-core, pandas3.0.6, PDFium5.13.0, Office/native parsers; CPU OCR image có Tesseract5.3.0 + eng/vie/osd, không Torch/layout/VLM weights |
| metadata | IMPLEMENTED/VERIFIED T10 | SQLAlchemy2.0.53 async + greenlet3.5.6, Psycopg, Alembic1.20.0; được include bởi api/ingestion |
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
| `AUTH_CONFIG_FILE` | path; `None` | Cho `/v1` | T09 JSON app registry; absent = 503, invalid/unreadable = startup failure; không chứa private signing key |

`rag_core.config.load_settings()` đọc environment rồi `.env`, bỏ qua giá trị rỗng. Thiếu config trả `SettingsError` dạng `Missing required RAG Core configuration: DATABASE_URL, QDRANT_URL, REDIS_URL`; giá trị malformed không được echo qua error/traceback. T02 readiness dùng PostgreSQL `SELECT 1`, Redis `PING` và Qdrant `/readyz`, mỗi probe có deadline.

| Nhóm env mục tiêu | Nội dung | Task |
| --- | --- | --- |
| Runtime | APP_ENV, LOG_LEVEL, API_BIND/API_PORT, request timeout đã typed; body limits còn DESIGNED | T01–T02 |
| Metadata/broker | DATABASE_URL, REDIS_URL | T02/T10/T12 |
| Vector/model | QDRANT_URL đã typed T02; API key, INFERENCE_URL, model IDs/revisions/device/batches còn DESIGNED | T02/T17–T18 |
| App identity | cấu hình app_id, service-key hash/reference, JWT issuer/audience/JWKS, algorithms | T09 |
| Source storage | `STORAGE_CONFIG_FILE` trỏ JSON app/alias/endpoint/region/bucket/prefix và credential file read-only | T11 |
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

Nếu readiness lỗi, dùng `docker compose --profile local-storage ps --all` rồi `docker compose logs --no-color <service>`; không render `docker compose config` đầy đủ vào ticket vì có thể lộ config khi operator tự thêm biến. Business quickstart (migration, ingest/query, model, admin) vẫn DESIGNED cho các task sau. Host auth/local issuer đã VERIFIED ở R03; Compose mặc định chưa mount app registry hay issuer.

<a id="r03"></a>
## R03. Auth, app registration và trust boundary

**T09 authentication VERIFIED local; T11 storage reader VERIFIED local; T12 registration/outbox VERIFIED local. App vẫn chịu trách nhiệm xác nhận user/session upload ownership; admin T27 vẫn DESIGNED.**

- Core operator đăng ký app bằng cấu hình tin cậy: app ID, service credential, JWT issuer/audience/JWKS và storage alias/prefix.
- Mỗi API nghiệp vụ gửi `Authorization: Bearer <user-JWT>` và `X-RAG-Service-Key: <app-service-key>`.
- Core lấy subject từ JWT đã verify; app ID từ service identity đã verify; không cho request body ghi đè identity.
- Backend app phải xác minh người dùng được phép dùng object trước đăng ký. Core không có quyền tự đọc DB quyền của Scarlet; chữ ký/trust contract này là trách nhiệm tích hợp.
- `Principal(app_id, user_id)` là immutable domain type; API middleware xác thực toàn `/v1` trước body/handler, `require_principal` inject cho handlers. Không dùng body/query/history làm identity. Principal chưa thay thế session/document scope resolver T10.
- Không đưa token/service key vào query string, metrics label, logs hoặc browser JS. Không dùng chung admin credential với API app.

401 `invalid_credentials`: credentials invalid/missing/duplicate hoặc unknown signing kid; có `WWW-Authenticate: Bearer`. 503 `dependency_unavailable`: chưa cấu hình registry hoặc JWKS không dùng được khi cần refresh. Error theo T03 envelope, request UUID mới, không chứa token/key/URL/exception, `Cache-Control: no-store`. 403 role và 404 resource ngoài scope là contract cho task sau. Route chưa mount chỉ trả framework 404 sau auth thành công; trước đó guard có thể trả 401/503. Không tắt auth để tránh lỗi tích hợp.

### App registry và JWT contract

Đặt `AUTH_CONFIG_FILE` vào environment hoặc `.env`, trỏ tới JSON operator-owned,
giới hạn 256 KiB/100 apps; giữ file ngoài Git, chỉ account chạy core được sửa.
`apps` phải nonempty; `app_id` và `service_key_sha256` phải unique. Mỗi app có
`app_id`, SHA256 hex của service key random 32 bytes trở lên, exact `issuer`,
`audience`, `jwks_url`. CLI dưới đây tạo registry đúng schema. Không dùng password
ngắn làm service key; core chỉ giữ SHA256 và so sánh bằng constant-time digest check.

JWT có `sub` nonempty <=256 ký tự, signed `app_id` khớp service app (kể cả hai app
dùng chung issuer/audience/JWKS), exact issuer và expected audience, integer NumericDate
`iat`/`nbf`/`exp`; `exp` phải sau `iat` và `nbf`. Cả bảy claims bắt buộc; zero clock
leeway, kiểm cả future `iat`. Header phải `alg=RS256`, `kid` nonempty <=128; JWT <=16KiB.
Không nhận `none`/HS algorithms hoặc token headers `jku`, `jwk`, `x5u`, `x5c`, `crit`.
JWT payload `user_id`/`jwks_url` không cấp quyền và không chọn URL. Backend tích hợp
sau này phải phát đúng claims; đây là contract T09 mới, chưa có client business cũ cần migrate.

JWKS URL chỉ từ config: HTTPS mặc định, không userinfo/query/fragment, không redirect
hoặc environment proxy. `allow_loopback_http=true` chỉ mở HTTP literal `127.0.0.1`
hoặc `::1`; bị cấm khi `APP_ENV=production`. Local CLI chỉ bind IPv4 loopback.
Không fetch URL do token/body cung cấp. RSA public keys 2048–8192 bits, <=32 keys,
JWKS <=128KiB; private RSA material/duplicate kid bị từ chối. Other algorithms/use
không được chọn. Auth dùng PyJWT 2.15.0 crypto trong group `api`; fixed algorithm
allowlist và required claims theo [PyJWT API](https://pyjwt.readthedocs.io/en/stable/api.html).

### Cache, rotation và thu hồi

Registry được load một lần lúc tạo app. Sửa app/service-key/issuer policy cần restart
mọi API process. Xóa app/hash cũ và restart để revoke service key ngay; không có
per-token logout/revocation list ở T09. JWT còn hiệu lực tới exp hoặc signing-key removal
được nhìn thấy qua refresh, tùy điều kiện nào đến trước.

Cache JWKS tách theo app/process, TTL mặc định300s (1–3600),
`refresh_interval_seconds=5` (1–60, <=TTL), `jwks_timeout_seconds=3` (>0–10).
Known kid dùng cache tới TTL; unknown kid có thể refresh sớm, tối đa một lần mỗi
refresh interval. Lock coalesce concurrent fetch và không tạo negative cache theo
attacker kid. New kid trong cooldown trả401; publisher nên prepublish khóa mới trước
khi phát token, giữ khóa cũ đến hết token lifetime + TTL. Refresh thay toàn bộ key set,
không merge giữ khóa đã xóa. Không có cache vô hạn theo từng signing key.

Revoke signing key: bỏ nó khỏi trusted JWKS; existing cached key có thể còn dùng tối
đa TTL (mặc định300s). Restart mọi verifier để xóa cache sớm, đồng thời ngừng phát token
bằng key đó. Refresh lỗi không kéo dài expiry; known cached key còn hạn vẫn dùng được,
expired/unknown key cần refresh mà JWKS lỗi thì503, không stale fallback. Empty JWKS
trả503 khi refresh; valid nonempty set không chứa kid đã revoke trả401. Timeout là
deadline cả fetch, bounded body; cancellation truyền ra ngoài. Response/cache metadata
của upstream không thay TTL operator. HTTP tests kiểm removal bằng elapsed TTL thật;
security suite kiểm rotation/grace/refresh flood/recovery với controlled cache clock.

### Local issuer và HTTP acceptance đã chạy

Từ root repository, sync dev+api. Dùng thư mục mới dưới `.local/` đã ignore; bảo vệ ACL
parent trên Windows vì mode0600 không thay Windows ACL. Không chia sẻ/copy private.pem,
service-key hoặc JWT vào Git/log/browser. CLI từ chối directory/output đã tồn tại.

```powershell
uv run python -m rag_core.auth.local_issuer init --directory .local/auth
uv run python -m rag_core.auth.local_issuer token --directory .local/auth --subject local-user --output .local/auth/user.jwt --ttl 300
uv run python -m rag_core.auth.local_issuer serve --directory .local/auth
```

Init tạo RSA2048 private PEM, public `jwks.json`, random `service-key`, `apps.json`.
Issuer `http://127.0.0.1:8765`, audience `rag-core:local-dev`, app `local-dev`;
TTL token1–3600s. Serve chỉ trả `/.well-known/jwks.json`, không serve directory/private
files, và đọc lại public file khi rotation. Không có HTTP endpoint mint token.
`serve` là foreground process; dừng bằng Ctrl+C. Với API host, đặt
`$env:AUTH_CONFIG_FILE='.local/auth/apps.json'` và giữ DSN/Redis/Qdrant theo R02.
Compose hiện không mount registry; loopback trong container không trỏ về host issuer.
Docker issuer wiring/server deployment chưa được claim VERIFIED ở T09.

Acceptance tự tạo credentials trong pytest temp đã ignore, khởi động CLI JWKS process
và Uvicorn protected test app trên ephemeral loopback ports, rồi tự dừng đúng process:

```powershell
$env:PYTEST_ADDOPTS='--basetemp=.local/9s-new'
uv run pytest tests/security/test_auth.py
$env:PYTEST_ADDOPTS='--basetemp=.local/9h-new'
uv run pytest tests/security/test_local_auth_http.py -s
```

Dùng tên basetemp mới mỗi lần. `/v1/auth-test` chỉ tồn tại trong test app, nhận
`{"external_session_id":"http-test-session"}` và headers redacted
`Authorization: Bearer [REDACTED]`, `X-RAG-Service-Key: [REDACTED]`.
Real HTTP trả200 principal `local-dev/http-user`, missing auth401, forged body422,
unmounted route404 sau auth, empty JWKS sau TTL503, private file404. Không mock JWT,
crypto/JWKS/HTTP; không gọi DB/LLM và không claim session authorization. Evidence
[H-T09-A01](docs/handoffs.md#h-t09-a01). Business API vẫn chưa mount; T10 thêm
repository/scope gate bên dưới, không thay auth hoặc mount query/registration.

<a id="r04"></a>
## R04. Session mapping và upload registration

**T10 schema/session repository/scope VERIFIED trên PG thật; T11 storage reader VERIFIED trên MinIO thật; T12 registration/outbox VERIFIED trên PG/MinIO/Redis thật; business HTTP/worker vẫn DESIGNED — T26/T19.**

### Schema ownership và migration T10

Core sở hữu PostgreSQL metadata riêng. App không ghi trực tiếp DB; app identity nằm
trong registry T09, owner là JWT subject, không tạo user-account database. Revision
`0001_session_metadata` tạo `sessions`, `documents`, `document_versions`,
`index_generations`, `session_documents`, `ingestion_jobs`, `outbox_events`; revision
`0002_upload_registrations` thêm idempotency records với unique app+owner+session+key
và app+owner+session+external upload ID.
Composite foreign keys mang app+owner xuyên session/link/document/version/generation/
job/outbox. FK không cascade delete; lifecycle chỉ UPDATE session/link. Source references
và retained generation/job/outbox rows được giữ. Binary nguồn, transcript và chunks
chưa có trong schema này; chunks/ingestion theo task sau.

Từ checkout root, sync dev+api (hoặc nhóm metadata cho migration-only). Alembic đọc
**process environment**, không tự load `.env`, không cần Redis/Qdrant/auth config:

```powershell
uv sync --locked --group dev --group api
# Set DATABASE_URL to the operator-verified target; never paste its password into logs.
uv run alembic upgrade head
uv run alembic current
```

`DATABASE_URL` chấp nhận `postgresql://` hoặc `postgresql+psycopg://`, driver luôn Psycopg3.
Optional `DATABASE_PASSWORD_FILE` đọc UTF-8 secret riêng, override password của DSN.
Migration có transactional DDL và advisory transaction lock, không chạy ngầm khi boot.
Đây là schema đầu tiên, không chuyển dữ liệu của app hay sửa T02 fixture table. Backup
DB trước migration trên môi trường có dữ liệu. `downgrade base` **xóa bảng metadata**;
chỉ test replay trên DB do fixture tạo, không dùng làm undo session delete hoặc thao tác
vận hành thông thường. Recovery production/backup rehearsal vẫn T34.
Migration files cần checkout; API image hiện chưa đóng gói migration CLI assets và
không claim Docker image rebuild/production migration ở T10.

### Session mapping và transaction contract

`PostgresSessionRepository(engine)` implements framework-free `SessionRepository`.
App phải giữ mapping `(app_id, JWT subject, external_session_id) -> core UUID`.
`create_session` concurrent/idempotent theo đúng tuple; external ID có thể trùng giữa
app/users. Deleted mapping giữ tombstone: create/get/query lại trả `session_deleted`
(410) cho owner, resource ngoài owner hoặc không tồn tại trả404. Repeated delete của
owner trả cùng deleted record/revision; session mới cần external ID mới và không có links.

`attach_version(conn, principal, session_id, version_id, upload_registration_id)` là
primitive **internal trusted registration**, không là public attach-by-UUID. T12 phải
verify nguồn/upload, ghi registration + job + outbox trong cùng caller transaction.
Primitive kiểm owner/session, max50 active documents, version-specific link, unique
registration trong session và một attached version/document. Existing registration
khác version trả409; replay registration đã detach giữ detached; chỉ registration mới
mới cấp link mới. Không âm thầm chuyển version cũ sang version mới. Attach/detach/delete
khóa row session và bump revision trong cùng transaction; rollback không để link/revision lẻ.

`resolve_scope` nhận principal đã authenticate, session UUID và optional nonempty unique
tuple document UUIDs (tối đa50). Nó dùng một SELECT/READ COMMITTED snapshot cho revision,
active links, versions và published generations. Empty session ->409 `no_session_documents`;
subset ngoài session ->404; bất kỳ selected version/generation chưa ready ->409
`documents_not_ready`, không trả partial selection. Resolver không xử lý domain/language
(T20) và không xem history là quyền. Version/gen giữ **cặp**, không hai independent lists.

Immutable `ScopeSnapshot` chứa principal, session, revision, requested subset và tuple
`VersionGeneration(document_id, version_id, generation_id)`. Cache/retrieval consumers
phải mang đủ các trường này; `validate_snapshot` đọc snapshot mới và so cả revision/pairs.
Detach/delete hoặc publish generation mới làm snapshot cũ trả409 `session_scope_changed`,
kể cả reindex không đổi revision. Staging generation không thay active ready generation.
Consumer T18/T24/T25 phải kiểm lại trước evidence/answer/delta/done; snapshot không giữ
DB lock suốt LLM call và không tự thu hồi bytes đã gửi. Job completion không hồi sinh links.

Async engine bounded5 connections/max_overflow0, pool wait5s, connect5s, statement10s,
lock5s. Không dùng blocking DB I/O trong async repository. Host Windows cần
`asyncio.SelectorEventLoop` cho Psycopg; integration suite tự chọn bằng pytest-asyncio
loop factory. Future host entrypoint phải chọn loop tương thích; Linux Docker không
có Proactor limitation. Xem [Psycopg async documentation](https://www.psycopg.org/psycopg3/docs/advanced/async.html).

### Kiểm chứng PostgreSQL tách biệt

`compose.metadata-test.yaml` là project riêng `rag-core-metadata-test`, pinnedPG17.11,
loopback55432 và **tmpfs disposable**, không volume hoặc network chung với stack app.
Stop/recreate mất dữ liệu test; không dùng service này để giữ dữ liệu thật. Main Compose
PG/Qdrant/Redis vẫn không publish host. Cần port55432 trống, secret mới đã ignore:

```powershell
uv run python -c "from pathlib import Path; import secrets; p=Path('.local/secrets'); p.mkdir(parents=True, exist_ok=True); f=(p/'t10_postgres_password').open('x', encoding='utf-8'); f.write(secrets.token_hex(32)); f.close()"
docker compose -f compose.metadata-test.yaml up -d --wait
$env:DATABASE_URL='postgresql://rag_core_test@127.0.0.1:55432/t10_acceptance'
$env:DATABASE_PASSWORD_FILE='.local/secrets/t10_postgres_password'
$env:RAG_TEST_DATABASE_URL=$env:DATABASE_URL
$env:PYTEST_ADDOPTS='--basetemp=.local/10-new --tb=short -o cache_dir=.local/10-test-cache'
uv run alembic upgrade head
uv run alembic current
uv run pytest tests/integration/test_session_scope.py -v -s
uv run pytest tests/integration/test_metadata_migrations.py -v -s
docker compose -f compose.metadata-test.yaml stop
```

Secret creation exclusive: nếu đã có file, giữ file hiện có và bỏ dòng tạo; không
overwrite credential. Dùng basetemp mới cho lần test sau; bảo vệ ACL của `.local`.
Tests cần role CREATEDB trong test service, tạo `t10_test_<random UUID>` riêng từng
module, kiểm DB trống trước migration và chỉ drop DB chính fixture vừa tạo. Thiếu URL,
DB sai tên hoặc không kết nối được thì FAIL, không skip/mock/SQLite. Gate migration
kiểm columns/defaults/constraints/indexes sau upgrade/idempotent head/downgrade/re-upgrade.
Gate lifecycle kiểm real locks, owner FKs, readiness/subsets, rollback/max50, concurrent
create/delete, retained source/version/generation/job/outbox metadata không đổi.

Test chỉ gọi PostgreSQL; adapter không có storage/vector client hay DELETE binary/chunks/
vectors. T10 không claim live MinIO/Qdrant retention/query, HTTP session routes, provider,
retrieval hoặc index publication worker. Evidence [H-T10-A01](docs/handoffs.md#h-t10-a01).
Giữ traceback ngắn/redacted: exception thư viện có thể in connection kwargs/credential
khi pytest dựng long traceback. Không chép raw traceback vào Git/handoff.

### T11 storage reader VERIFIED trên MinIO local

`rag_core.ports.storage.StorageReader` chỉ có `read(app_id, SourceObject)` trả context manager chứa file tạm, byte count, SHA-256 và version ID. Caller phải đọc trong `with`; đóng context xóa file cả khi exception. Adapter `S3StorageReader` chỉ gọi HEAD/GET. Đây là boto3 đồng bộ, nên worker tương lai dùng worker thread/process; không gọi trực tiếp trên async API loop. T12 xác thực principal/session/upload và nối adapter vào registration; T11 không cấp quyền cho object chỉ vì key tồn tại.

`STORAGE_CONFIG_FILE` là JSON operator-owned ngoài Git, tối đa 256 KiB/100 vị trí; một `(app_id, alias)` duy nhất. Ví dụ cấu trúc local (tên file chứa credential, không chứa giá trị):

```json
{
  "locations": [{
    "app_id": "test-app", "alias": "test-store",
    "endpoint": "http://127.0.0.1:9000", "region": "us-east-1",
    "bucket": "rag-core-storage-test", "prefix": "allowed/",
    "access_key_file": ".local/secrets/minio_reader_user",
    "secret_key_file": ".local/secrets/minio_reader_password",
    "allow_loopback_http": true, "max_bytes": 104857600, "timeout_seconds": 10
  }]
}
```

Production yêu cầu HTTPS, không cho loopback HTTP; URL không được có userinfo/path/query/fragment. App ID và alias lấy từ identity/config đã xác thực, không từ URL request. Bucket/prefix exact allowlist; key loại absolute/traversal/encoded percent/control; không dùng ETag như SHA-256. Nguồn cần `version_id` hoặc `sha256`: versioned HEAD/GET + If-Match cho bản cụ thể, hoặc HEAD/GET If-Match + tính SHA-256 từ stream + HEAD sau tải để phát hiện đổi nguồn. Size kiểm trước và trong stream, timeout hữu hạn, temp cleanup. `source_changed`, `source_too_large`, `storage_forbidden`, `storage_unavailable` là lỗi an toàn, không in credential/provider URL. Không truyền redirect sang host khác. Reader credential chỉ có `GetObject/GetObjectVersion` trong prefix; app uploader dùng principal riêng. App backup và sở hữu nguồn; core không PUT/DELETE.

Reproduce live T11 từ root trên Docker Desktop (test bucket và users riêng, secrets ignored; không xóa MinIO volume):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\bootstrap_local.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\bootstrap_storage_test.ps1
docker compose -f compose.yaml -f compose.storage-test.yaml --profile local-storage --profile storage-test up -d --wait minio
docker compose -f compose.yaml -f compose.storage-test.yaml --profile local-storage --profile storage-test run --rm storage-fixture
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'
$env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'
uv sync --locked --group dev --group api --group ingestion
uv run --no-sync pytest -q tests/integration/test_storage_reader.py --basetemp .local/t11-pytest
```

Fixture script enables versioning only on `rag-core-storage-test`, creates separate reader/uploader IAM users and policies. Test uses unique object key, deletes only its own fixture via uploader, and checks real GET, denied prefix, old version, source change, oversized body, interrupted stream/temp cleanup, denied PUT/DELETE, redirect target not reached and source hash unchanged. [H-T11-A01](docs/handoffs.md#h-t11-a01) contains actual outputs. T12 nối reader vào registration; worker T19 chưa có; API readiness vẫn chỉ kiểm PG/Redis/Qdrant.

### Upload registration T12 — service/dispatcher VERIFIED, HTTP contract DESIGNED

Luồng app bắt buộc:

1. User chọn/upload tài liệu trong một phiên chat của app.
2. App upload vào S3/MinIO của app; xác minh quyền object thuộc user và upload của session đó.
3. App tạo/resolve core session bằng external_session_id; lưu core session UUID trong metadata app.
4. App backend register upload cho core session với Idempotency-Key; không dùng UUID browser gửi mà bỏ ownership checks. T12 service nội bộ hoạt động, HTTP route sẽ mount ở T26.
5. Khi HTTP route được mount, nhận 202 với document/job IDs và poll job đến ready hoặc lỗi có cấu trúc. Trước T19, job chỉ có thể `queued` hoặc bị huỷ/thất bại qua fixture; chưa có worker tạo `ready`.
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

Idempotency-Key scope app+owner+session+request hash; cùng key/body trả cùng job, khác body 409. External upload ID dùng lại với key khác cũng trả409; một registration đã detach replay vẫn detached. App retry lỗi transport bằng cùng key; không tạo upload mới chỉ vì HTTP response bị mất. Đọc nguồn được thực hiện qua thread trước PG transaction; app xác nhận user/session ownership bằng identity đã xác thực, còn core đối chiếu storage config và bytes/version/hash thật. Core không thể suy ownership từ S3 key hay ACL.

T12 ghi document/version/job/registration/link/outbox trong một transaction. Outbox dispatcher phát Celery task `rag_core.ingest` vào queue `rag_core_ingestion` trên Redis rồi đánh dấu dispatched trong PG. Crash sau publish trước PG commit có thể tạo hai message cùng event ID; `claim_job` chỉ chuyển `queued -> fetching` một lần, tăng attempts/lease một lần. Dispatcher và consumer kiểm session/link hiện hành, nên deleted/detached session không được hồi sinh. Khi broker lỗi, transaction rollback giữ event pending; rerun phát lại. T19 sẽ triển khai worker parser và lease recovery; chưa gọi `ready` hoặc claim live ingestion.

Chạy trên host từ root với env `DATABASE_URL`, optional `DATABASE_PASSWORD_FILE`, `REDIS_URL` trỏ các service đã kiểm; migration thực hiện riêng trước dispatcher:

```powershell
uv sync --locked --group dev --group api --group ingestion
uv run alembic upgrade head
uv run python -m rag_core.adapters.broker.dispatcher --once
uv run python -m rag_core.adapters.broker.dispatcher
```

`--once` phát tối đa một event và exit0 khi không có event; lỗi broker/PG exit1, event vẫn chờ. `--interval` 0.1–60 giây, mặc định1. Compose image riêng `rag-core-dispatcher:t12` ở profile `registration`; chỉ bật sau migration và khi muốn publish vào Redis. Chưa có worker nhận queue trước T19. Stop/start giữ PG/Redis volumes; không dùng down-v. Isolated acceptance: `docker compose -f compose.metadata-test.yaml -f compose.registration-test.yaml up -d --wait postgres redis`, MinIO T11 test fixture theo R04, đặt `RAG_TEST_DATABASE_URL`/`DATABASE_PASSWORD_FILE` như T10 và chạy `uv run pytest tests/integration/test_registration_jobs.py -v -s`; Redis test ở loopback16379/DB15 và đo queue delta, không flush dữ liệu. [H-T12-A01](docs/handoffs.md#h-t12-a01) ghi output thực.

**Ví dụ HTTP mục tiêu, chưa serve trước T26:** `POST /v1/sessions/{session_id}/documents` với `Idempotency-Key: <opaque-key>` và payload trên → `202` cùng `session_id`, `scope_revision`, `document` và `job` (`state: queued`, `retryable: false`). `GET /v1/jobs/{job_id}` poll trạng thái; `POST /v1/jobs/{job_id}/retry` chỉ khi `failed` và `attempts < max_attempts`, chuyển lại `queued`, thêm outbox event; retry cùng lúc khi đã `queued` trả cùng job. Cùng key khác body → `409 idempotency_conflict`; ngoài owner → `404 not_found`; session deleted → `410 session_deleted`; source đổi → `409 source_changed`; broker lỗi không làm register thất bại, job vẫn `queued`. Đừng coi ví dụ là response runtime HTTP đã verify.

<a id="r05"></a>
## R05. Endpoint inventory và lỗi

**T03 schemas/snapshots/examples VERIFIED; health runtime VERIFIED tại T02; mọi business/admin route còn DESIGNED và chưa mount.** [P06](docs/plan.md#p06) là nguồn thiết kế, modules `rag_core.contracts.v1`/`sse` là nguồn machine-readable hiện tại. T26 sẽ mount business routes sau runtime gates tương ứng.

| Method / route | Contract request → response | Trạng thái runtime / owner |
| --- | --- | --- |
| POST `/v1/sessions` | SessionCreateRequest → SessionResponse | T10 repository VERIFIED; HTTP chưa mount / T26 |
| GET/DELETE `/v1/sessions/{session_id}` | path UUID → SessionResponse | T10 repository VERIFIED; HTTP chưa mount / T26 |
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

**T03 locator schemas, T10 PG session scope/lifecycle và T13–T16 text/table/OCR/chunk provenance VERIFIED; citation resolver/stream revalidation DESIGNED — T24/T25.**

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

**T13–T14 và T16 VERIFIED trên Windows/Python3.12.4; T15 OCR VERIFIED trong Linux worker/Python3.12.13; embedding/index orchestration DESIGNED — T17–T19.**

| Format / MIME (extension allowlist) | Extraction và locator đã kiểm | Trạng thái / giới hạn |
| --- | --- | --- |
| PDF / `application/pdf` (`.pdf`) | Docling Parse7.22.1 native Unicode textline; physical page one-based, native block/bbox, printed label riêng | VERIFIED EN/VI hai trang và text bảng/header/unit; không suy ra cấu trúc ô từ layout PDF |
| DOCX / `application/vnd.openxmlformats-officedocument.wordprocessingml.document` (`.docx`) | python-docx1.2.0; headings, paragraphs, bảng/nested tables, headers/footers; XML part/path | VERIFIED EN/VI page-break/table fixture; không bịa pages |
| TXT / `text/plain` (`.txt`) | UTF-8, BOM/CRLF giữ vị trí, line/paragraph/offset | VERIFIED EN/VI; encoding khác báo `invalid_encoding` |
| Markdown / `text/markdown` (`.md`) | UTF-8 source blocks; ATX/Setext headings, fenced code và bảng pipe cơ bản | VERIFIED EN/VI/source offsets; raw syntax giữ nguyên, không render/execute |
| HTML / `text/html` (`.html`, `.htm`) | stdlib HTMLParser; heading/block/raw source span, entity text, table rows | VERIFIED; script/style/template/iframe/object không là text evidence; 0 HTTP canary requests |
| PDF scan/mixed, PNG/JPEG | Tesseract vie/eng qua Docling OCR stage, per-page fallback, PDF physical page và image raw pixel bbox | VERIFIED T15; bật OCR operator-side; giới hạn OCR region ở dưới |
| XLSX/CSV/PPTX | openpyxl sheet/cell/formula cache, stdlib CSV records/header, python-pptx slide/shape/XML | VERIFIED T14 text/tables, no chart/image reasoning |
| `.doc/.xls/.ppt`, audio/video | Không hỗ trợ | Không có parser; không cam kết hiểu charts/images |

Reproduce từ root (chọn basetemp mới mỗi lần để pytest không xóa artifact cũ):

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'
uv sync --locked --group dev --group api --group ingestion
uv run --no-sync pytest tests/integration/test_text_parsers.py -v -s --tb=short --basetemp=.local/t13-check
uv run --no-sync pytest tests/integration/test_text_parsers.py -k safety -v -s --tb=short --basetemp=.local/t13-safety
```

19 tests chạy parser thật, 8 safety tests chạy riêng; không services/provider/model,
không đọc corpus `qa/`. Fixtures tạo local trong ignored test temp; before/after
source bytes và parser sandbox-empty được assert cả lỗi. [H-T13-A01](docs/handoffs.md#h-t13-a01)
ghi command/config/output; completion subject `feat(T13): parse text documents with source provenance`.

Interface: `rag_core.ports.parsers.DocumentParser.parse(path, filename=..., content_type=...,
source=SourceIdentity(...))`; implementation `ParserRegistry(temp_root, ParserLimits())`.
SHA-256 phải bằng bytes được copy, source document/version UUIDs là metadata đã xác minh,
không chứng minh quyền truy xuất. Chỉ gọi với T11 `DownloadedSource` của registration
đã được T12/worker authorize; parser không tìm bucket, không auto-attach/reuse index.
Đây là synchronous CPU boundary: future async callers phải offload; share một registry
trong worker, một slot không queue (`parser_busy`). T19 chưa nối parser vào job/ready.

`ParsedDocument` schema1 có source, format, parser_revision, blocks, page_count,
quality, needs_ocr_pages và warnings; `Block` giữ text/kind/T03 SourceLocator,
heading_path, rows, XML source_part/source_path hoặc native PDF bbox. Bảng DOCX/HTML
giữ hàng/cột cùng header/units, không tách ô khi extraction; T14 thêm common normalization/context, T16 token chunking được mô tả bên dưới.
Mọi offsets là half-open **Unicode character**, không byte: TXT/MD vào original decoded
source (kể cả BOM/CRLF); HTML span vào original HTML gồm tags/entities, decoded text
không nhất thiết bằng raw substring. PDF vào canonical page text = native textline
cells theo backend order joined by LF; native block index tính cả empty cells. DOCX
offset vào exact paragraph.text hoặc canonical table rows joined bằng TAB/LF.
DOCX paragraph indices tính body top-level paragraphs kể cả blank rồi các header/footer
parts unique; table indices depth-first qua body/nested/header/footer. XML member+XPath
giữ định vị gốc cho nested tables/header/footer. Các indices zero-based; không có page
DOCX. PDF native bbox theo coordinate system của backend, không giả image pixel bbox.

`ParserLimits` là operator config, không request override: max100MiB input, max1000
PDF pages, deadline60s (copy+subprocess+result; <=300s), max4096 ZIP members, 256MiB
expanded ZIP, per-entry compression ratio200, max100000 blocks/8Mi Unicode chars/32MiB
serialized result. Có thể giảm để chạy boundary tests. Registry đối chiếu extension,
normalized declared MIME, PDF/ZIP signature và OOXML main content type; TXT/MD không
có magic riêng nên yêu cầu UTF-8/nonbinary và suffix/MIME phù hợp. DOCX archive đọc
CRC/XML trong process, không extract members ra disk; traversal/duplicate member/VBA,
encrypted ZIP, DTD/entities và archive bombs bị từ chối. External relationships được
ghi warning `external_relationships_ignored`, không fetch. HTML không browser/render,
không chạy JS/event attributes hay tải CSS/link/image/frame.

Input copy, request/result và worker TMP/TEMP/TMPDIR nằm trong unique parser directory
dưới temp_root operator-owned. Timeout hoặc caller exception kill/reap process trước
cleanup; backend stdout/stderr discarded để không lộ source/private paths. Không
đưa registry vào thư mục nguồn; T11 temp vẫn thuộc lifecycle của storage reader.
Error public chỉ code: `unsupported_format`, `mime_mismatch`, `invalid_encoding`,
`source_too_large`, `source_changed`, `archive_limit`, `unsafe_archive`, `page_limit`,
`extraction_limit`, `encrypted_document`, `corrupt_document`, `parser_timeout`,
`parser_busy`, `parser_failed`, `empty_extraction`, `ocr_required`. Không thử password,
không coi empty thành success. PDF có trang thiếu text trả `quality=partial` + physical
`needs_ocr_pages`; T15 OCR có thể xử lý khi bật, T19 phải từ chối ready nếu còn partial,
không bỏ trang âm thầm.

Limits/compatibility: schema trung gian mới, không DB/index/API migration; T03 locators
và OpenAPI giữ nguyên. New pins chỉ ingestion group, không vào API/inference/weights.
Docling native backend theo P02 ([upstream API](https://github.com/docling-project/docling-parse#sequential-parsing));
không tải Docling layout/OCR models trong T13. Windows host verified; worker image,
OCR quality, general PDF semantic table/layout accuracy và RAM/latency corpus chưa đo.
Job state PG/outbox giữ T12 semantics; publication/retry/lease/reindex ở T19.

### Office/CSV policy và source mapping T14

Commands ở root repo, với ingestion group ở trên; dùng basetemp mới:

```powershell
uv run --no-sync pytest tests/integration/test_office_tables.py -v -s --tb=short --basetemp=.local/t14-check
uv run --no-sync pytest tests/integration/test_office_tables.py -k safety -v -s --tb=short --basetemp=.local/t14-safety
```

**VERIFIED native parsers**, không mock/LLM/services/weights, fixtures synthetic EN/VI.
Evidence từng DoD: [H-T14-A01](docs/handoffs.md#h-t14-a01). Registry signature/source
identity/time/temp contract giữ nguyên. Thêm MIME chính xác:
`application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`, `text/csv`,
`application/vnd.openxmlformats-officedocument.presentationml.presentation`.
Không nhận `.xlsm/.pptm/.doc/.xls/.ppt`; macro-enabled main content hoặc VBA member
đổi suffix thành `.xlsx/.pptx` vẫn bị từ chối. Không có Office automation/calculation.
ZIP preflight chung DOCX/XLSX/PPTX kiểm CRC, main part/type, XML DTD/entities,
duplicate/traversal/encryption/bomb trước backend; không extract members. External
relationships là inert metadata và warning `external_relationships_ignored`; không
fetch/update linked workbooks. Embedded objects/media không mở hoặc thực thi.

`Block.rows` giữ source cell strings, empty cells và embedded newlines; common
TAB/LF text normalization cho DOCX/HTML/XLSX/CSV/PPTX, MD giữ nguyên source text/offset.
`table_headers` lưu context rows tách khỏi rows. XLSX có thêm `cells` với reference,
value, formula, value_origin, number_format, merged_origin. Context convention là
first nonempty row và các text-only leading rows trước data numeric/formula, reset
sau blank row; numeric year headers được giữ. Đây là source context convention,
không cam kết tự nhận diện mọi bảng phức tạp. Merged header context lặp anchor text
trong các cột liên quan; raw rows không fill giá trị giả, cells giữ anchor mapping.
Mỗi XLSX block là một source row/range + context; T16 giữ context khi chia chunks.
Source part lấy từ workbook relationships; XPath dùng prefix `s` với namespace
`http://schemas.openxmlformats.org/spreadsheetml/2006/main`. Locators không có page.

Formula text giữ trong metadata riêng, không đưa expression vào text numeric evidence.
`value_origin=stored|formula_cache|missing_formula_cache`; missing cache có text
`[formula cache unavailable]` + `formula_cache_missing`, không là0 hoặc computed value.
Cache có sẵn giữ nguyên và cảnh báo `formula_cached_values_unverified`; không bảo
đảm cache mới. Unsupported formula representation trả `unsupported_formula`.
Stored number/date/bool giữ canonical backend value (ISO date/time, TRUE/FALSE),
Excel number_format riêng và trong evidence text khi khác General: ví dụ raw0.25
với0% không bị trình bày như25 đã render. Header units giữ nguyên, không đoán unit.
Theo [openpyxl API](https://openpyxl.readthedocs.io/en/stable/api/openpyxl.reader.excel.html),
hai lần load `data_only=False/True`, đều `keep_vba=False/keep_links=False`, không save.

CSV chỉ UTF-8, optional BOM; sniff64Ki chars cho comma/semicolon/TAB/pipe và strict
parse toàn file. Không tự đoán legacy encoding; malformed quotes, unequal widths,
blank record hoặc delimiter không xác định trả `invalid_csv`/`invalid_encoding`.
Single-column không delimiter được nhận. First logical record là header/context,
nhưng vẫn có source block; không drop first-row values. Empty header nhận label
`Column N` theo vị trí, raw context giữ nguyên. `row_start/end` là **logical record**
one-based, không phải physical line khi quoted field chứa newline. Record có empty
fields vẫn giữ raw rows, text marker `[empty CSV fields]` nếu cần; file chỉ có empty
fields trả `empty_extraction`. Formula/HTML-looking fields là text data.
Không export CSV sang Office hoặc chạy formula.

PPTX slide order là presentation order one-based; shape là top-level z-order index
zero-based; block là paragraph index (blank counted) hoặc table slot. Group shapes
dùng depth-first flattened blocks trong top-level group, mỗi table tính một slot,
paragraph blank vẫn tăng index; source_part/XPath chỉ đúng child XML. Text/bảng lấy
bằng [python-pptx shapes API](https://python-pptx.readthedocs.io/en/latest/api/shapes.html).
Không extract notes/master/chart/image/media; warning `non_text_shapes_not_extracted`
hoặc `chartsheets_not_extracted` khi gặp. Không cam kết suy luận biểu đồ/hình.

Thêm operator limits:250000 actual table cells/cumulative merge expansion, max128
sheets/max1000slides, `table_limit`/`sheet_limit`/`slide_limit`. XLSX còn giới hạn
combined bounding rectangles <=250000cells trước load để không densify sparse/huge
merged ranges; forged dimension không dùng làm loop bounds. Các limits input/archive/
output/deadline T13 vẫn áp dụng; không benchmark RAM hoặc worker image trong T14.
Intermediate schema1 thêm fields có default; API T03/PG/index không đổi. Revisions
`openpyxl-3.1.5/table-v1`, `python-pptx-1.0.2/table-v1`, `stdlib-csv/table-v1` và DOCX/
MD/HTML `table-v2` phải vào pipeline fingerprints T16/T19 khi tái sử dụng kết quả.

### OCR worker CPU T15

**VERIFIED: full20tests và separate13status checks trong worker image.** Build/test commands trong
[README OCR](README.md#ocr-envi-t15). `worker` target là non-root10001 parser runtime;
`ocr-test` kế thừa runtime này và thêm pytest/DejaVu font cho synthetic fixtures.
T19 mới nối Celery/job/ready/index. Không chạy service ingestion giả trong Compose.

```python
from rag_core.adapters.parsers import ParserRegistry
from rag_core.domain.documents import OcrConfig, ParserLimits

parser = ParserRegistry(temp_root, ParserLimits(), ocr=OcrConfig(enabled=True))
# parser.parse(verified_path, filename=..., content_type=..., source=..., cancel=event)
```

`OcrConfig` chỉ từ operator/DI, không từ upload body/document text. Default disabled;
optional `tessdata_path` là local trusted directory, truyền `TESSDATA_PREFIX` cho child.
Ngôn ngữ cố định `vie+eng`, PSM3, `OcrMode.FULL_PAGE` **chỉ trên selected pages**,
PDF216dpi, ảnh native resolution. Tesseract order ảnh hưởng kết quả; T15 đo cùng PNG
và thấy eng+vie mất dấu “đạt”, vie+eng giữ đúng. Không spell-correct theo gold.
[Docling OCR options](https://docling-project.github.io/docling/reference/pipeline_options/)
và [Tesseract CLI](https://tesseract-ocr.github.io/tessdoc/Command-Line-Usage.html) là
nguồn API; code thực được kiểm trên slim2.132.0 đã pin trong lock.

Native Docling Parse pass giữ nguyên textline/offset/bbox. Trang không có text mới
vào Docling `TesseractOcrCliModel`, PDFium chỉ render selected pages; không OCR mọi
trang hoặc ghép OCR vào text layer có sẵn. Mixed PDF là mixed **pages**; trang có
native text nhưng còn bitmap text riêng chưa được OCR region detection. Đây là
giới hạn rõ, không claim đã hiểu tất cả nội dung ảnh trong trang có native text.
OCR stage độc lập layout pipeline, không download model/network, không remote OCR.

`Block.extraction_method=native|ocr`; OCR blocks là word cells theo Docling/Tesseract
order. PDF physical page one-based + printed label riêng; OCR block indices zero-based,
offsets vào canonical OCR page text = words joined LF, half-open Unicode chars.
OCR PDF bbox là page points, **top-left**; native PDF bbox vẫn native coordinate system.
Ảnh giữ `format=image`, image ID=source SHA256, `ocr_block` và T03 bbox trong raw
source pixels/top-left. EXIF orientation/DPI được strip trên bản copy để bbox trỏ
raw pixels gốc; không hứa camera EXIF auto-rotation. PNG/JPEG single frame, MIME
và suffix phải khớp decoder. T16 regroup words bằng khoảng trắng và giữ source locators.

`quality=text` khi native-only, `ocr` khi OCR thành công (kể cả mixed), `partial`
khi còn failed PDF pages. `ocr` là extraction method, không calibrated accuracy.
Partial có `needs_ocr_pages` và `ocr_unreadable_pages`; worker T19 phải xử lý/fail
trước publication, không coi partial ready. `OcrReport` ghi engine/version/languages,
attempted/completed physical pages (ảnh logical1), OCR-stage elapsed (không gồm copy,
native pass và import), parser/child Linux peak RSS. RSS child high-water có thể
bao gồm inherited fork memory, không cộng hai số như total RAM. Tests in cgroup2
báo whole-container peak và acceptance wall; không là benchmark full corpus/10GiB gate.

T13 byte/page/archive/text/result/deadline limits giữ nguyên; thêm max25million
pixels trước image decode và trước PDF render (tính cả PDFium1.5x intermediate).
One registry/one process, không queue; OMP thread limit1. Optional
`cancel=threading.Event()` kiểm mỗi50ms/copy, deadline60s default <=300s cho toàn parse.
Linux child là new session/process group, timeout/cancel kill group rồi reap parser
trước temp cleanup. `docker run --init` giúp reap orphan CLI; cancellation tests
quan sát PID Tesseract thật. Windows tree cleanup dùng taskkill, native parser
regression kiểm host; OCR acceptance chuẩn là Linux Docker.

| Code / state | Ý nghĩa / xử lý |
| --- | --- |
| `ocr_required` | OCR disabled; bật cấu hình tại worker có engine/data, không ready scan |
| `ocr_engine_missing` | Không tìm thấy CLI; kiểm worker image/PATH |
| `ocr_tessdata_missing` | Thiếu eng/vie hoặc không load directory; kiểm data/env |
| `ocr_failed` | Engine CLI lỗi kỹ thuật, gồm data corrupt; không đổi thành empty success |
| `ocr_empty` | Toàn file OCR không có readable text, gồm white image; extraction failed |
| `partial` + `needs_ocr_pages` | Có text nhưng còn PDF pages không đọc được; không ready |
| `image_limit` | Pixel/render/multiframe vượt limit; không tăng limit theo request |
| `parser_timeout` / `parser_cancelled` | Deadline/caller cancel; process tree stopped + cleanup |
| `corrupt_document` / `mime_mismatch` | Image/PDF hỏng hoặc không khớp format; nguồn giữ nguyên |

Diagnostics đã chạy trên worker/test image (không cần API/PG/LLM key):

```powershell
docker run --rm --network none --entrypoint tesseract rag-core-worker:t15 --version
docker run --rm --network none --entrypoint tesseract rag-core-worker:t15 --list-langs
docker run --rm --network none --entrypoint python rag-core-worker:t15 -c "import os; from importlib.metadata import version; print('uid', os.getuid(), 'docling-slim', version('docling-slim')); print('tessdata', os.environ.get('TESSDATA_PREFIX', 'system default'))"
```

Expected Tesseract5.3.0, eng/vie/osd and uid10001/Docling slim2.132.0. Custom data
directory needs both actual traineddata files; no network download at runtime.
Full DoD output/status/elapsed/RAM and failures retained at [H-T15-A01](docs/handoffs.md#h-t15-a01).
Additive intermediate fields, existing T03 locator/API unchanged; no PG/index migration.
OCR config/order/DPI/Docling+engine+traineddata revisions must enter T16/T19 pipeline
fingerprints before reuse. Engine/data package versions pinned; transitive OS packages
use Debian repositories at build time, no claim of byte-identical future apt rebuilds.

<a id="r09-t16"></a>
### Structural chunking T16: tokenizer, source mapping và reindex

**VERIFIED**: actual tokenizer + native parsers/independent original source round-trip,
và actual T15 OCR word mapping; [H-T16-A01](docs/handoffs.md#h-t16-a01).
Không cần PG/Qdrant/LLM key để nghiệm thu T16. API/job/ready không được nối ở task này.

```powershell
uv sync --locked --group dev --group api --group ingestion
uv run --no-sync python scripts/setup_tokenizer.py
uv run --no-sync pytest tests/unit/test_chunking.py --basetemp=.local/t16-unit-check
uv run --no-sync pytest tests/integration/test_source_locators.py --basetemp=.local/t16-source-check
```

Chọn basetemp mới mỗi lần. Operator setup tải HTTPS tokenizer JSON của
`BAAI/bge-m3@5617a9f61b028005a4858fdac845db406aefb181`, SHA256
`21106b6d7dab2952c1d496fb21d5dc9db75c28ed361a05f5020bbba27810dd08`,
17,098,108bytes, runtime `tokenizers==0.22.2`. Local artifact và manifest nằm trong
`.local/tokenizers/bge-m3/`, không commit. Existing corrupt file không bị overwrite;
adapter kiểm hash/runtime rồi disable truncation/padding, không download khi ingest.
Container mount/cache wiring và model weights/inference thuộc T17/T19.

```python
from rag_core.adapters.tokenizer import BgeM3Tokenizer
from rag_core.domain.chunking import ChunkProfiles, StructuralChunker

profile = ChunkProfiles().for_domain("document")  # trusted operator/domain config
chunker = StructuralChunker(BgeM3Tokenizer(tokenizer_path), profile)
chunks = chunker.chunk(parsed_document, generation_id=generation_id,
                       extraction_fingerprint=extraction_config_fingerprint)
```

Đây là synchronous CPU API, async worker caller phải offload. `default`, `document`,
`multilingual` cùng baseline512/64; static `ChunkProfiles({...})` là hook cho trusted
code/config. Unknown domain báo `unknown_chunk_profile`, không fallback rộng scope.
Client/upload/history không được đăng ký hook hoặc override config.

`ChunkProfile(name, revision, max_tokens=512, overlap_tokens=64)` đếm **embedding tokens
gồm special tokens**, tối đa8192; overlap đếm riêng content tokens, là upper bound
chứ không hứa luôn đúng64 vì Unicode/biên token/paragraph. Token offsets dùng để cắt
**original Unicode characters**, rồi tokenize lại mỗi chunk; không cắt theo số ký tự
hoặc decode token IDs đã normalization. Prefer paragraph/heading boundaries; long
block dùng token windows. Overlap ở cùng đơn vị, không qua heading, PDF page,
PPTX slide/shape, native/OCR boundary hoặc bảng. OCR words ghép space, native blocks LF.

Bảng giữ cả ô/hàng, grouping consecutive XLSX/CSV rows cùng context/vùng; DOCX/PPTX/
HTML/MD table riêng. Blank XLSX row, sheet, table hoặc unit/header context đổi là biên.
Header repeated mapping về source cells; merged XLSX context trỏ stored anchor thật.
Formula expressions chỉ ở `cells` metadata, không là embedding text; formats/cache
policy note có trong text nhưng không là source quote. Không infer cell layout từ
native/OCR PDF; native PDF không có normalized rows chỉ chunk text provenance.
Row/header không vừa budget báo `table_row_too_large`/`table_header_too_large`; operator
xử lý/reindex với trusted profile hoặc source mới, không silently split cell/drop units.

`Chunk` giữ UUID/document/version/source SHA/generation/ordinal, checksum, token_count,
pipeline/parsed fingerprints, heading path, source segments và cell metadata. Segment
có half-open chunk chars và normalized block/cell chars, zero-based block/row/column,
original locator/XML part/path/bbox, role content/context/overlap. PDF page luôn physical
one-based; DOCX/XLSX không có page. `chunk.quotes(parsed, start, end)` rechecks exact
parsed/source identity và substring, trả từng `MappedQuote`; separators và policy notes
không có quote. Original offsets chỉ được thu hẹp khi chúng mô tả verbatim block text;
HTML entities/MD table syntax giữ coarse raw span + exact normalized cell coordinates.
Không lấy một locator của chunk ghép làm vị trí cho toàn quote. T24 phải authorize
app/user/current session/link/ready version-generation trước khi resolve; UUID chỉ là
provenance, không là quyền. Chunker không đọc storage, attach link, publish hoặc query.

`structure-v1` pipeline fingerprint gồm chunker revision, full trusted profile,
tokenizer model/revision/artifact SHA/runtime, parser_revision và extraction fingerprint.
IDs còn gồm document/version/SHA, generation, parsed content/maps digest, ordinal/checksum.
Same input/config/generation cho IDs như nhau; source version hoặc bất kỳ thành phần
trên đổi thì IDs đổi. Parsed digest bỏ elapsed/RSS để OCR measurements không gây drift.
Native standard config có default `native-v1`; custom extraction phải supply full config
fingerprint. OCR bắt buộc supply fingerprint engine/version/traineddata SHA/language
order/DPI/PSM/Docling/config; thiếu trả `missing_extraction_fingerprint`.
T17/T19 phải compose tiếp embedding model/index revision vào full index fingerprint.

Config/tokenizer/parser/extraction/model revision đổi cần **generation/reindex mới**,
không reuse/overwrite generation cũ. T19 mới triển khai atomic ready publication: giữ
generation cũ đến khi generation mới đủ chunks/vectors/PG publication. T16 không có
DB/API migration, không tự reindex retained data, không đổi session retention semantics.
Partial extraction bị từ chối `partial_extraction`; output vượt100000chunks hoặc32Mi
characters báo `chunk_output_limit`, không trả partial success. Khả năng hình/bảng phức
tạp và corpus throughput/RAM/tuning chưa đo; chưa có calibrated retrieval quality.

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
