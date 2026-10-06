# RAG Core

RAG core độc lập để các ứng dụng chat gọi qua API: hỏi đáp trên tài liệu, trích dẫn có vị trí nguồn và truy xuất xuyên tiếng Việt/tiếng Anh.

> **T01–T22 VERIFIED local; T23 VERIFIED protocol/configuration; T24 VERIFIED application/citation fixtures.** T24 nối answer assembly, scoped source allowlist/one repair và citation resolver vào preparation/retrieval/evidence. PG/Qdrant/BGE/parsers/source thật, LLM protocol synthetic; live verification vẫn ở T26. Compose chuẩn bật worker/dispatcher/inference; MinIO vẫn là profile local-storage. API chỉ mount health; public HTTP/SSE/admin còn thuộc T25–T36. [Evidence T24](docs/handoffs.md#h-t24-a01).

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

T02 có Python3.12/FastAPI health skeleton, PostgreSQL17/Qdrant/Redis và MinIO tùy chọn. T12 thêm dispatcher; T13–T16 có native/Office/OCR parsers và chunking. T17 thêm dedicated inference process dùng BGE-M3 + multilingual reranker qua CPU hoặc GPU override. T19 thêm Celery worker và PG chunk persistence/publication. T20–T24 nối domain preparation, retrieval, evidence, provider adapters và grounded JSON assembly; public HTTP/SSE và Admin UI thuộc các task sau.

Máy mục tiêu: RAM16GB, RTX4060Laptop8GB, nguồn<=1GB và15–20users. T17 đã đo inference trên synthetic fixtures, xem RUNBOOK/evidence; chưa có benchmark chất lượng/tải/full-stack budget.

## Prerequisites, quality và local Docker

T22 có session-authorized PG passage/source-map hydration,
reranker thật, versioned raw-score baseline, tối đa20candidates/8passages/8000tokens,
whole-passage budget và context gate trước generation. Kiểm mâu thuẫn số bảo thủ
`numeric-claim-v1` trên các claim có cùng nhãn/ngữ cảnh/thời điểm/đơn vị trước khi
áp passage budget; conflict trả insufficient với reason `conflicting_evidence`.
Không phải detector mọi mâu thuẫn ngữ nghĩa. Threshold0.0 là raw reranker logit,
không là confidence/xác suất đúng; calibration pending T31.
[Nghiệm thu thật T22](docs/handoffs.md#h-t22-a02),
[hợp đồng và cách kiểm tra](RUNBOOK.md#r06-t22).

T01/T02 đã kiểm chứng trên Windows/PowerShell với uv 0.11.16, CPython 3.12.4 cho host checks, Docker Desktop Linux containers và Docker server 29.5.2. Project chấp nhận Python `3.12.*`; API image dùng Python 3.12.13 đã pin digest. Cài [uv](https://docs.astral.sh/uv/) và Docker Desktop, rồi từ root repository chạy quality:

```powershell
uv sync --locked --group dev --group api --group ingestion --group inference
uv run ruff check .
uv run mypy src
uv run pytest tests/unit
uv run pytest tests/contract/test_api_schema.py
uv run python scripts/export_openapi.py --check
uv run python scripts/check_docs.py
```

Trong sandbox hoặc máy không ghi được cache user, đặt `UV_CACHE_DIR` và `UV_PYTHON_INSTALL_DIR` vào `.uv-cache`/`.uv-python` trong repo (ignored). `uv sync` tạo `.venv` từ lock. API/ingestion include metadata nhưng không include model runtime; chọn thêm group `inference` cho CPU hoặc `inference-gpu` cho CUDA. Ingestion orchestration T19 VERIFIED trên services/models thật.

Typed settings đọc environment hoặc `.env`: `DATABASE_URL`, `REDIS_URL` và `QDRANT_URL` là bắt buộc; `DATABASE_PASSWORD_FILE` cho phép API đọc Docker secret tách khỏi DSN. Biến rỗng trong example được bỏ qua, DSN/credential không xuất hiện trong repr hoặc traceback chuẩn hóa. Bảng đầy đủ nằm ở [RUNBOOK R02](RUNBOOK.md#r02).

Trước khi start toàn bộ Compose T19: chuẩn bị model cache T17, migration và worker/storage config theo [RUNBOOK T19](RUNBOOK.md#r09-t19). Chỉ kiểm health có thể start explicit `postgres qdrant redis api`; full stack cần đủ cấu hình. Bootstrap tạo secret local ngẫu nhiên dưới `.local/secrets/` đã ignore và không in giá trị. Sau đó render/start/check stack:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\bootstrap_local.ps1
docker compose config --quiet
docker compose --profile local-storage up -d --build postgres qdrant redis api minio minio-bootstrap
docker compose --profile local-storage up -d --wait postgres qdrant redis api minio
docker compose --profile local-storage ps --all
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\smoke_local.ps1
```

API chỉ bind `http://127.0.0.1:8000`; MinIO API/console tùy chọn bind `127.0.0.1:9000/9001`. PostgreSQL, Qdrant và Redis chỉ ở mạng Compose, không publish host. `/health/live` kiểm process; `/health/ready` chạy `SELECT 1`, Redis `PING` và Qdrant `/readyz`, trả 503 nếu dependency lỗi. MinIO không phải dependency readiness của API health skeleton T02.

Bằng chứng local outage/persistence nằm ở [T02-A02](docs/handoffs.md#h-t02-a02); [T02-A03](docs/handoffs.md#h-t02-a03) tiếp quản candidate chưa commit, kiểm lại quality/stack hiện tại và đối chiếu SHA-256 source với API image cuối trước completion commit.

Dừng/khởi động lại mà giữ named volumes:

```powershell
docker compose --profile local-storage stop
docker compose --profile local-storage up -d postgres qdrant redis api minio minio-bootstrap
docker compose --profile local-storage up -d --wait postgres qdrant redis api minio
```

Không dùng `docker compose down -v` trong flow mặc định. T19 đã thêm ingestion; T26 sẽ mount HTTP query; T28–T29 thêm admin UI; T35 kiểm lại hướng dẫn tích hợp.

## Hợp đồng API v1 T03

Pydantic contracts tại `src/rag_core/contracts/` đã kiểm structural validation cho domain/subset, history roles, EN/VI, initial limits, locators, evidence links, error và logical SSE traces. Export/kiểm lại từ root với dev+api groups:

```powershell
uv run python scripts/export_openapi.py
uv run python scripts/export_openapi.py --check
```

[OpenAPI v1 thiết kế](docs/api/openapi-v1.designed.json) có 13 operations với `x-served`/`x-implementation-status`; [OpenAPI đang serve](docs/api/openapi.served.json) chỉ có 2 health routes. [37 examples](docs/api/examples-v1.json) là dữ liệu synthetic minh họa, không phải response runtime. Export kiểm OpenAPI model, JSON Schema Draft 2020-12 và examples bằng cả JSON Schema/Pydantic; không đọc secret hoặc chạy dependency/provider probes. Hợp đồng và các gate runtime còn thiếu nằm ở [RUNBOOK R05–R08](RUNBOOK.md#r05), actual evidence [H-T03-A02](docs/handoffs.md#h-t03-a02); [H-T03-A01](docs/handoffs.md#h-t03-a01) ghi recovery do runtime quota trước commit.

## Domain preparation và hội thoại T20

`QueryPreparation` resolve scope từ authenticated principal/current session trước rewrite hoặc domain hook. Hook chỉ nhận `ScopedRetrievalContext` với read capability cố định scope/languages; search/fetch/neighbor vẫn được PG/Qdrant kiểm quyền. Registry tĩnh chỉ nạp code/config tin cậy; custom test domain dùng cùng dispatcher, không thành domain public thứ tư.

| Domain | Tập tài liệu | Language policy |
| --- | --- | --- |
| `default` | Tất cả ready links trong session; không nhận subset | Answer theo câu hỏi gốc hoặc `answer_language` |
| `document` | `document_ids` nonempty, mọi ID thuộc session | Cùng default; profile cấu trúc tài liệu |
| `multilingual` | Session hoặc subset nonempty | EN/VI; `corpus_languages` lọc độc lập với answer language |

History chỉ là dữ liệu cho rewrite, không vào retrieval/evidence context. Giữ suffix gần nhất trong 20 messages/8000 tokens đo bằng pinned BGE-M3 tokenizer, trả counts và warning khi cắt. Rewrite output chỉ có câu hỏi độc lập và ngôn ngữ câu hỏi gốc; lỗi/timeout là lỗi kỹ thuật, scope thay đổi thì dừng. Provider test đã kiểm cả ba domain và EN/VI overrides; real DeepSeek/Anthropic adapters thuộc T23, live smoke T26. [RUNBOOK R06](RUNBOOK.md#r06) ghi DI/schema, budgets và lệnh kiểm chứng trên PG/Qdrant thật. Chưa có query HTTP handler hoặc factual-answer verification trong T20.

## Provider adapters T23

**VERIFIED protocol/configuration tests; live verification remains T26.**
`DeepSeekProvider` uses HTTPX Chat Completions; `AnthropicProvider` uses the pinned
Anthropic1.11.0 SDK and native Messages schema. Both implement private
`LlmProvider.generate/stream` and T20 `QueryRewriter.rewrite`. System policy stays
separate from untrusted question/history/evidence; no tools or provider fallback.
T24 assembles scoped prompts/citations; T25/T26 wire public query/SSE.

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'
uv sync --locked --group dev --group api
uv run --no-sync pytest tests/contract/test_llm_providers.py
uv run --no-sync pytest tests/contract/test_llm_providers.py -k 'config or redirect_following'
```

No provider keys/services are needed for these synthetic protocol tests. Configure
the selected provider's own `API_KEY` and `MODEL` in ignored `.env`/environment,
using `DEEPSEEK_` or `ANTHROPIC_` prefixes; model IDs have no default. Independent
HTTPS endpoints, deadlines, retry and token-budget settings are in `.env.example`.
Usage missing from upstream stays `null`; retries stop after the first delta,
including whitespace. Cancel/early close releases upstream. Consumers use
`contextlib.aclosing` when ending a stream early.
[RUNBOOK T23](RUNBOOK.md#r06-t23) documents DI, conservative prompt charge,
nullable usage, error codes, limits and planned live gates;
[evidence](docs/handoffs.md#h-t23-a01) records separate DoDs and quality checks.

## Answer assembly và citations T24

**VERIFIED local acceptance T24-A01; LLM protocol synthetic.** `AnswerPipeline` nối preparation,
bounded retrieval/rerank và `AnswerAssembler`; `CitationResolver` đọc chunk trong
current session qua PostgreSQL. Prompt tách system policy khỏi question/evidence;
history chỉ đi qua rewrite. Core cấp ID theo từng mapped source segment, kiểm exact
quote/ID/locator/version và scope trước mỗi LLM call, sau call và trước final response.
Một lần repair tối đa; vẫn sai trả `invalid_citation`. Insufficient vẫn gọi LLM,
trả citations/contexts rỗng; provider failure giữ lỗi kỹ thuật.

Full prompt dùng tokenizer BGE-M3 thật, ceiling8000 processing tokens và32768UTF-8
bytes gồm framing; output<=1024, deadline chung60s cho assembly/repair. Usage của hai
call repair được cộng, thiếu bất kỳ count nào giữ `null`. Contexts chỉ gồm chunks
được cite. IDs `cN` chỉ có ý nghĩa trong response; resolver stateless trả segment
đầu của current chunk, không lưu transcript/citation cache hay phát storage URL.
[RUNBOOK T24](RUNBOOK.md#r06-t24) có DI, errors và JSON examples;
[evidence](docs/handoffs.md#h-t24-a01) phân biệt PG/Qdrant/BGE/source thật với LLM
protocol fixtures synthetic. Live model behavior còn T26; public HTTP/SSE còn T25/T26.
Citation validation kiểm provenance/quote, không chứng minh semantic entailment của
mọi model claim; calibration/corpus quality còn T31.

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
worker/chunk persistence T19 đã VERIFIED; vector repository T18 đã VERIFIED bên dưới. Snapshot phải được consumer revalidate trước khi phát evidence/answer.

## Upload registration và outbox T12

`PostgresRegistrationRepository` nhận principal đã xác thực, core session UUID,
`Idempotency-Key` và `DocumentRegisterRequest`. App backend phải xác minh upload thuộc
user/session trước khi gọi; core đọc đúng app storage alias/prefix và kiểm bytes thực,
version/SHA-256. Cùng key/body trong app+owner+session trả cùng job; khác body hoặc
external upload ID dùng lại với key khác trả409. Link/job/outbox ghi trong một PG
transaction; Redis mất kết nối giữ event chờ. Dispatcher phát Celery task
`rag_core.ingest`, consumer T19 dùng fenced `PostgresIngestionRepository.claim`, generation riêng từng attempt và lease watchdog để chống xử lý lặp.

Migration `0002_upload_registrations` chạy bằng `uv run alembic upgrade head` trên DB
đã kiểm. Dispatcher có CLI `uv run python -m rag_core.adapters.broker.dispatcher`
với `DATABASE_URL`, optional `DATABASE_PASSWORD_FILE` và `REDIS_URL`; Compose chuẩn có dispatcher image riêng, không tự mount HTTP routes. Test tích hợp thật:

```powershell
uv sync --locked --group dev --group api --group ingestion
uv run pytest tests/integration/test_registration_jobs.py -v -s
```

Test cần isolated PostgreSQL `RAG_TEST_DATABASE_URL`, MinIO test IAM và Redis test
theo [RUNBOOK R04](RUNBOOK.md#r04). T19 worker tạo `ready` sau reconciliation/publication; PG là nguồn trạng thái, không dùng message Redis làm trạng thái nguồn. [H-T12-A01](docs/handoffs.md#h-t12-a01) ghi bằng chứng và giới hạn.

## Text parsers T13

`ParserRegistry(temp_root, ParserLimits())` nhận local path đã tải bằng storage reader,
filename, MIME và `SourceIdentity(document_id, version_id, sha256)`. Kết quả
`ParsedDocument/Block` giữ T03 locators, heading/table context và hash nguồn; parser
không cấp quyền session. T19 nối worker và kiểm current session/link trước publication.
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
trả `ocr_required` khi OCR chưa bật. T15 thêm OCR bên dưới; T16 chunking đã kiểm, index orchestration vẫn DESIGNED.
MIME/limits/offset conventions/format matrix: [RUNBOOK R09](RUNBOOK.md#r09).
Evidence: [H-T13-A01](docs/handoffs.md#h-t13-a01).

## Office tables T14

**VERIFIED trên Windows/Python3.12:** cùng `ParserRegistry` nhận XLSX/CSV/PPTX,
giữ sheet/cell ranges, logical CSV records và slide/shape/block/XML nguồn.
XLSX dùng `openpyxl==3.1.5`, PPTX dùng `python-pptx==1.0.2`, chỉ trong ingestion group.

```powershell
uv sync --locked --group dev --group api --group ingestion
uv run --no-sync pytest tests/integration/test_office_tables.py -v -s --tb=short --basetemp=.local/t14-check
uv run --no-sync pytest tests/integration/test_office_tables.py -k safety -v -s --tb=short --basetemp=.local/t14-safety
```

Dùng basetemp mới mỗi lần chạy. Fixtures synthetic, parser thật, không services/provider/model.
Bảng giữ empty cells, header/unit context; merged XLSX có anchor mapping. Formula và
cached value là hai fields riêng: không tính lại, cache thiếu ghi rõ, cache hiện có
được cảnh báo chưa xác minh độ mới. Stored numbers giữ Excel format như `0%`; không
âm thầm đổi `0.25` thành giá trị đã render. CSV UTF-8/BOM hỗ trợ comma/semicolon/TAB/pipe,
quoted multiline và logical row one-based; first record là context/header convention.
PPTX lấy text/bảng, kể cả group shapes. Không hỗ trợ `.doc/.xls/.ppt`, không cam kết
suy luận charts/images. ZIP/macro/XML/external-link safety và giới hạn cụ thể ở
[RUNBOOK R09](RUNBOOK.md#r09); [H-T14-A01](docs/handoffs.md#h-t14-a01) ghi evidence.
T19 nối parser vào ingestion worker/index; parser không cấp quyền truy xuất session.

## OCR EN/VI T15

**VERIFIED trong worker image:** worker Docker có Tesseract5.3.0, tessdata
vie/eng/osd và Docling slim2.132.0 OCR stage. CPU, không tải layout/VLM/Torch weights.
Synthetic scan PDF EN/VI, PNG/JPEG, mixed PDF và searchable scan kiểm engine thật.

```powershell
docker build --target worker -f docker/worker.Dockerfile -t rag-core-worker:t15 .
docker build --target ocr-test -f docker/worker.Dockerfile -t rag-core-ocr-test:t15 .
docker run --rm --init --network none --memory=2g --cpus=2 rag-core-ocr-test:t15
docker run --rm --init --network none --memory=2g --cpus=2 rag-core-ocr-test:t15 uv run --no-sync pytest tests/integration/test_ocr.py -k status -v -s --tb=short --basetemp=/tmp/ocr-status -o cache_dir=/tmp/pytest-cache
```

Operator bật bằng `ParserRegistry(temp_root, limits, ocr=OcrConfig(enabled=True))`.
Mặc định tắt để native-only callers giữ hợp đồng T13. Native text layer được giữ,
chỉ OCR trang PDF không có native text; ảnh luôn cần OCR. `quality=text|ocr|partial`,
`needs_ocr_pages` và `OcrReport` giúp T19 từ chối publication còn thiếu trang.
PDF physical pages/printed labels riêng; ảnh dùng SHA256 image ID + raw pixel bbox.
`cancel=threading.Event()` hoặc deadline dừng cả process group và cleanup.
[RUNBOOK R09](RUNBOOK.md#r09) có lỗi/diagnostics/offsets/giới hạn;
[evidence T15](docs/handoffs.md#h-t15-a01) có output/elapsed/RAM thật.
Image này cung cấp parser runtime và T19 Celery consumer; models nằm trong inference service riêng.

## Chunking và source maps T16

**VERIFIED trên host với tokenizer BGE-M3 thật**: 512 tokens gồm special tokens,
overlap tối đa64 ở cùng đơn vị/heading; PDF page, PPTX shape, bảng và vùng XLSX là
biên cứng. Bảng chia nhóm hàng nguyên, lặp header có nguồn, giữ đơn vị/number format
và trạng thái formula cache. Hàng/ô quá dài báo lỗi, không cắt hoặc bỏ text âm thầm.
OCR word cells được ghép bằng khoảng trắng nhưng giữ locator/bbox từng từ.

Từ root, sau locked sync dev+api+ingestion ở trên:

```powershell
uv run --no-sync python scripts/setup_tokenizer.py
uv run --no-sync pytest tests/unit/test_chunking.py --basetemp=.local/t16-unit-check
uv run --no-sync pytest tests/integration/test_source_locators.py --basetemp=.local/t16-source-check
```

Setup tải riêng tokenizer17,098,108bytes từ revision/hash cố định vào ignored `.local`,
không tải weights. Runtime/tests đọc offline, checksum mismatch hoặc thiếu artifact
là lỗi. `StructuralChunker` nhận parsed source/generation và trusted profile; UUID ổn
định theo version/generation/pipeline/source maps. `Chunk.quotes` trả từng đoạn nguồn,
không biến separators/metadata thành citation. Quyền resolver/session vẫn ở T24.
[RUNBOOK T16](RUNBOOK.md#r09-t16) nêu API nội bộ, fingerprint/reindex và lỗi;
[evidence](docs/handoffs.md#h-t16-a01) ghi từng DoD và OCR thật bổ sung.
T19 ingestion/publication đã VERIFIED trên isolated real stack.

## Shared inference T17

**VERIFIED trên real weights và Docker CPU/GPU; [evidence T17](docs/handoffs.md#h-t17-a01).**
Một process nội bộ dùng chung BGE-M3 dense1024+sparse và reranker-v2-m3; API/Celery
chỉ dùng async HTTP client, không load weights. CPU FP32 mặc định, CUDA12.8/FP16 qua
override. Cache tải rõ ràng, checksum/revision pin; runtime offline, cache read-only.

```powershell
uv sync --locked --group dev --group api --group ingestion --group inference
uv run --no-sync python scripts/setup_models.py
uv run --no-sync pytest tests/integration/test_model_inference.py -v -s --tb=short --basetemp=.local/t17-check
docker build --target inference-test -f docker/inference.Dockerfile -t rag-core-inference-test:t17-cpu .
```

Queue32 jobs, tối đa24 indexing để chừa query; batch2 và query được ưu tiên giữa
các batch. Embed tối đa32 texts/512tokens mỗi text, rerank20pairs/768tokens mỗi pair;
quá giới hạn báo lỗi, không truncate âm thầm. Cancel/deadline bỏ queue và các batch
chưa chạy, giữ native slot đến hết batch hiện tại. Raw rerank score không là xác suất
answer đúng. [RUNBOOK T17](RUNBOOK.md#r09-t17) có named volume, CPU/GPU smoke,
startup/latency/RAM/VRAM, errors và fingerprint/reindex. Chưa có retrieval/public query API.

## Scoped Qdrant repository T18

**VERIFIED trên Qdrant1.19.1/PostgreSQL17.11 thật**: `QdrantVectorRepository`
nhận immutable `ScopeSnapshot` từ T10, kiểm lại PG trước/sau read. Dense/sparse và
cả hai hybrid prefetch đều có app/owner AND các cặp document/version/generation;
fetch/neighbor có cùng scope và language policy. Scope rỗng không gửi query/scroll.
Collection versioned theo fingerprint T17; PG xác minh và khóa generation khi ghi/
count/cleanup. Active generation không được ghi đè hoặc cleanup; retry giữ point IDs.

```powershell
docker compose -f compose.metadata-test.yaml -f compose.qdrant-test.yaml up -d --wait postgres qdrant
$env:RAG_TEST_DATABASE_URL='postgresql://rag_core_test@127.0.0.1:55432/t10_acceptance'
$env:DATABASE_PASSWORD_FILE='.local/secrets/t10_postgres_password'
$env:RAG_TEST_QDRANT_URL='http://127.0.0.1:56333'
uv run --no-sync pytest tests/integration/test_qdrant_scope.py -v -s --tb=short --basetemp=.local/18-new
docker compose -f compose.metadata-test.yaml -f compose.qdrant-test.yaml stop postgres qdrant
```

Prerequisites: locked dev+api+ingestion groups và test secret T10 theo
[RUNBOOK R04](RUNBOOK.md#r04). Dùng basetemp mới. Test dùng vectors synthetic để
chứng minh quyền/filter trên server thật; không là benchmark embedding hay live
model gate T17. Collection configuration, internal interfaces, reindex/retention
và giới hạn tại [RUNBOOK T18](RUNBOOK.md#r09-t18); [evidence](docs/handoffs.md#h-t18-a01).
T19 nối worker/chunk persistence, T21 bounded retrieval VERIFIED; public query HTTP thuộc T26.

## Durable ingestion T19

**VERIFIED:** 12 real-stack ingestion tests và 4 DoD-2 checks riêng; [evidence](docs/handoffs.md#h-t19-a01). T19 nối toàn bộ các adapters đã kiểm ở T11–T18, không load Torch/models trong worker.
Job có lease với token riêng, heartbeat và tối đa3 attempts; dispatcher thu hồi lease
quá hạn và phát lại qua PG outbox với backoff. Mỗi attempt có generation staging mới.
PG lưu text/checksum/source maps/cell context; Qdrant giữ metadata và dense/sparse.
Worker đối soát từng batch trên server thật và count toàn generation trước transaction
PG công bố generation/version/job `ready`. Reindex giữ generation cũ đến khi replacement
đủ dữ liệu. Detach/delete huỷ quyền hiện hành, không attach lại hoặc xóa nguồn/chunks/index.

Reproduce riêng trên Docker (đã có T17 model volume và ignored local secrets T10/T11):

```powershell
docker compose -f compose.ingestion-test.yaml config --quiet
docker build --target ingestion-test -f docker/worker.Dockerfile -t rag-core-ingestion-test:t19 .
docker compose -f compose.ingestion-test.yaml up -d --wait postgres redis qdrant minio inference storage-fixture
docker compose -f compose.ingestion-test.yaml run --rm ingestion-tests
docker compose -f compose.ingestion-test.yaml run --rm ingestion-tests uv run --no-sync pytest tests/integration/test_ingestion_pipeline.py -k 'scan_xlsx or visibility or duplicate_pending' -v -s --tb=short --basetemp=/tmp/ingestion-visibility -o cache_dir=/tmp/pytest-cache
docker compose -f compose.ingestion-test.yaml stop
```

Fixtures synthetic EN/VI, actual MinIO/PG/Redis/Qdrant/BGE-M3/Tesseract; không ingest
QA/gold. Standard Compose setup và compatibility ở [RUNBOOK T19](RUNBOOK.md#r09-t19).
HTTP registration/query vẫn chưa mount trước T26. [Evidence](docs/handoffs.md#h-t19-a01).

## Dense/hybrid retrieval T21

**VERIFIED với CPU BGE-M3, PostgreSQL17.11 và Qdrant1.19.1 thật:**
`RetrievalPipeline(models, model_fingerprint).retrieve(scoped_context)` nhận context T20,
embed question với query priority, search trong scope/language đã bind, trả tối đa20
candidate metadata cho T22. Profile server `hybrid-v1` dùng RRF, `dense-v1` là baseline;
mặc định30 candidates mỗi branch, chọn20 seeds, neighbors tắt cho tới khi trusted
profile chừa budget và bật anchors. Neighbors cùng version/generation/source unit,
dedup và dùng chung candidate budget. PG revalidate cả trước/sau model/search/neighbor
và trước return; detach/delete/reindex làm abort. Không có query cache hoặc gold input.

`result.trace.model_dump_json()` chỉ chứa policy/hash/model fingerprint/language,
counts/timing/score kind; không query/history/text/identity/chunk IDs. `candidates`
là metadata riêng tư có scope, không phải log. RRF/cosine chưa xác định đủ bằng chứng;
unrelated dense query vẫn có thể trả candidates. Rerank/hydration/evidence T22
VERIFIED local; public query T26 còn DESIGNED; full corpus quality T31 chưa đo.

Setup model image/cache theo [RUNBOOK T17](RUNBOOK.md#r09-t17), test secrets theo R03:

```powershell
docker compose -p rag-core-t21-test -f compose.metadata-test.yaml -f compose.qdrant-test.yaml -f compose.retrieval-test.yaml up -d --wait
$env:RAG_TEST_DATABASE_URL='postgresql://rag_core_test@127.0.0.1:55432/t10_acceptance'
$env:DATABASE_PASSWORD_FILE=Join-Path (Get-Location) '.local/secrets/t10_postgres_password'
$env:RAG_TEST_QDRANT_URL='http://127.0.0.1:56333'
$env:RAG_TEST_INFERENCE_URL='http://127.0.0.1:58080'
uv run --no-sync pytest tests/integration/test_retrieval.py
uv run --no-sync pytest tests/unit/test_retrieval_policy.py tests/integration/test_retrieval.py::test_real_dense_hybrid_toggle_reproducible_and_max_budget
docker compose -p rag-core-t21-test -f compose.metadata-test.yaml -f compose.qdrant-test.yaml -f compose.retrieval-test.yaml stop
```

Host dùng locked dev/api/ingestion groups; whole-source mypy thêm inference group.
Use fresh short ignored basetemp như R11. Services test loopback/tmpfs, cache read-only,
không application volumes; fixtures synthetic index mọi source/distractor, không QA/gold.
Tunables/DI/limits: [RUNBOOK T21](RUNBOOK.md#r06-t21); [evidence](docs/handoffs.md#h-t21-a01).

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
- **T12 VERIFIED registration/outbox:** real MinIO/PG/Redis integration, owner/session idempotency, detach, retry, crash redelivery và dispatcher image/CLI. Business HTTP mount vẫn DESIGNED ở T26; worker T19 đã VERIFIED.
- **T13 VERIFIED text parsers:** PDF native text, DOCX, TXT/MD/HTML EN/VI; provenance và process/MIME/size/archive/time/cleanup gates.
- **T14 VERIFIED Office tables:** XLSX sheet/cells/formula cache, CSV records và PPTX slide/shape; common headers/units và archive bounds.
- **T15 VERIFIED OCR:** Docker CPU Tesseract vie/eng + Docling stage, page/image provenance, quality/error/cancel/process bounds; 20 full + 13 separate status checks thật.
- **T17 VERIFIED:** shared inference/offline model setup, CPU/GPU real smoke, batching/queue/query priority/cancel and resource measurements.
- **T18 VERIFIED:** exact-pair scoped Qdrant search/fetch/neighbors, versioned collections, idempotent upserts và PG-guarded generation cleanup.
- **T19 VERIFIED:** ingestion orchestration, fenced leases/recovery, durable chunks/source maps và atomic ready publication; gates/evidence ở trên.
- **T20–T21 VERIFIED:** domain registry/scoped preparation/history rewrite port và bounded dense/hybrid retrieval với redacted trace.
- **T23 VERIFIED protocol/config:** DeepSeek HTTPX và Anthropic SDK generate/stream/rewrite; synthetic fixtures, independent secrets/models/budgets. Live smoke remains T26.
- **T24–T26:** query JSON/SSE, citations, provider wiring và live smoke.
- **T27–T29:** admin URL/login, UI workflows.
- **T30–T34:** benchmark reports, performance, reliability, backup/restore.
- **T35–T36:** quickstart tích hợp đã kiểm chứng và trạng thái nghiệm thu cuối.

## Nguyên tắc cập nhật

README và RUNBOOK được cập nhật trong từng task; mục mới ghi rõ `DESIGNED`, `IMPLEMENTED` hoặc `VERIFIED` cùng task/evidence. Không quảng cáo tính năng, format hay tốc độ chưa đo. Secrets, tài liệu gốc, model weights và database dumps không thuộc source code.
