# Implementation Summary

> Sổ ghi chú thực thi theo phase/task/attempt. Chỉ ghi implementation đã làm; kế hoạch tương lai nằm ở plan/tasks.
> Output commands ở [handoffs.md](handoffs.md); [tasks.md](tasks.md) là nguồn trạng thái task.

## Tổng quan hiện tại

| Hạng mục | Trạng thái thật |
| --- | --- |
| Bối cảnh/kiến trúc/backlog/agent workflow | Đã viết và kiểm chứng T00; completion commit là bằng chứng đóng task |
| Python project/config/quality | T01 implemented + verified trên CPython 3.12.4; completion commit là bằng chứng đóng task |
| README/RUNBOOK | Có prerequisites, quality, Docker health quickstart và contract export T01–T03 đã kiểm; business quickstart chưa tồn tại |
| Runtime/API/Docker | T02 Compose + health-only API implemented/verified local; không có business API/worker/inference |
| API contracts | T03 schemas/design inventory/served snapshot/37 synthetic examples structural validation PASS trong A02; chỉ health được mount |
| UI | Chưa triển khai |
| Corpus | Chỉ có prompt gốc; chưa download/normalize/validate |
| LLM/OCR/embedding/retrieval | Chưa chạy |
| Evaluation/load/restore | Chưa đo hoặc kiểm thử |
| Scarlet integration | Ngoài phạm vi backlog hiện tại |

<a id="s-t00"></a>
## S-T00 — Phase 0 / T00 — Bộ hồ sơ ban đầu

- **Loại công việc:** thiết kế và tài liệu, không viết ứng dụng.
- **Trạng thái:** COMPLETE khi completion commit T00 tồn tại; không có task implementation nào COMPLETE.
- **Input:** yêu cầu người dùng + trả lời củng cố + prompt corpus nguyên bản; README/RUNBOOK có sẵn nhưng rỗng.
- **Files:** AGENTS.md; README.md; RUNBOOK.md; docs/plan.md; docs/tasks.md; docs/handoffs.md; docs/implementation-summary.md.
- **Kiến trúc đã ghi:** Python 3.12/FastAPI, PostgreSQL metadata, Qdrant, Celery/Redis/outbox, app-owned S3/MinIO, Docling/Tesseract, BGE-M3 + reranker, DeepSeek/Anthropic, local Compose, Jinja2 admin.
- **Quyết định quan trọng:** scope bắt buộc app+user+active session+upload links+ready versions+subset; không dùng toàn kho user. Giữ index sau delete chat, nhưng không hồi sinh quyền/link hoặc tự attach session mới.
- **Hợp đồng chuẩn bị:** REST/SSE v1, auth/trust app backend, job lifecycle, citation locator theo định dạng, history stateless, answerability, error/cancellation semantics.
- **Backlog:** T00–T36, phases 0–9; dependencies tuần tự; corpus thật tách implementation/benchmark; DoD riêng + D1–D6.
- **Agent workflow:** Orchestrator GPT-6-Astra read-only/điều phối; worker GPT-5.6-Sol/xhigh, fresh context/task/attempt, không song song, mọi task có docs/commit/evidence.
- **README/RUNBOOK:** ghi rõ DESIGNED, task chịu trách nhiệm từng mục; RUNBOOK có integration contract và checklist để session sau nối Scarlet/app khác.
- **Validation:** PASS UTF-8/nonempty 7 files, 136 links/anchors, đủ fields T00–T36, dependencies tuần tự không chu trình, review scope/orchestration/docs, staged diff --check exit 0. Lượt đầu validator lỗi encoding PowerShell đã sửa trong script kiểm tra; giữ failure và output PASS thật ở [H-T00](handoffs.md#h-t00).
- **Commit reference:** `docs(T00): establish RAG core implementation blueprint`; actual hash resolve từ Git sau commit.
- **Giới hạn:** chưa có app/API/services/corpus/model/live tests; chưa có số đo hiệu năng/chất lượng; chưa kiểm provider credentials/GPU runtime.
- **Next:** T01 khởi tạo Python structure/checks rồi T02 Docker, theo tasks; không thực thi tự động ở session lập hồ sơ này.

## Mẫu entry bắt buộc cho task tiếp theo

```text
## Phase N / Txx / Attempt Axx — Tên task
Status + agent/model/effort:
Start/end + timezone:
Plan refs/dependencies:
Implemented behavior (trigger -> result):
Files/modules/interfaces/schemas:
Decisions và lý do trong phạm vi task:
Database/index/config migrations và compatibility:
Validation: DoD IDs, actual evidence links, mock/integration/live distinction:
README/RUNBOOK: mục cập nhật hoặc N/A có lý do:
Commit subject / hash resolver / actual prior hash nếu cần:
Risks/limitations/blockers:
Next task và thông tin cần chuyển:
```

Không thêm entry “đã triển khai” cho task TODO; không copy plan thành kết quả thực thi. Khi task retry, giữ entry attempt cũ và giải thích điều gì đã thay đổi.

<a id="s-t01-a01"></a>
## Phase 0 / T01 / Attempt T01-A01 — Python project và quality commands

- **Status + agent/model/effort:** đề nghị COMPLETE; worker fresh `gpt-5.6-sol`/`xhigh`, runtime record xác minh turn `01a0a5a1-fedd-7a73-801f-d5afc48b106c` và cwd repo.
- **Thời gian/dependency:** 2026-09-15 22:16–22:35 +07:00; T00 commit `7025eeac080b481c17f7d68f0290b1ee3e3165e9` đã đọc cùng execution notes, P01/P02/P13/P14/P15 và living docs.
- **Behavior:** `.python-version` và project metadata buộc Python `3.12.*`; `uv sync --locked --group dev` tạo env từ lock. `rag_core.config.load_settings()` đọc env/`.env`, trả typed `Settings`, và chuyển lỗi Pydantic thành `SettingsError` chỉ nêu field/message an toàn. `DATABASE_URL`/`REDIS_URL` bắt buộc; DSN không xuất hiện trong repr hay traceback chuẩn hóa.
- **Interfaces/files:** public `Settings`, `SettingsError`, `load_settings`; package marker `py.typed`; `scripts/check_docs.py` kiểm UTF-8/nonempty Markdown source, internal file/anchor, task fields/status/order/dependency graph. Validator prune caches/runtime và generated corpus nhưng vẫn duyệt corpus source docs/licenses/scripts.
- **Dependencies:** base Pydantic/settings và dev tools được cài/kiểm; API + ingestion clients từ P02 được lock theo group nhưng component còn DESIGNED. `inference=[]` dành cho T17 để tránh kéo FlagEmbedding/PyTorch/model weights vào API/dev trước capability check.
- **Hygiene:** `.gitattributes` bắt UTF-8/LF cho source; exception exact path giữ prompt người dùng byte-for-byte. `.gitignore` loại `.env`, caches, runtime/logs, generated corpus và root model weights; đường source `src/rag_core/adapters/models` và corpus scripts vẫn trackable.
- **Migration/compatibility:** không database/index/schema migration. Python 3.13 không nằm trong supported interpreter range; `.env` cũ thiếu hai DSN sẽ fail sớm với field names.
- **Validation:** DoD commands PASS trên Python 3.12.4: sync, Ruff, strict mypy, 3 unit tests, docs validator, lock/Python/ignore/attribute/blob checks. Không service, integration, live provider, model hoặc corpus benchmark; output và failures đã sửa nằm ở [H-T01-A01](handoffs.md#h-t01-a01).
- **README/RUNBOOK:** prerequisites, exact quality commands, dependency group status, typed env table và sandbox cache workaround đã thêm; phân biệt VERIFIED T01 với Docker/app DESIGNED.
- **Commit:** subject `feat(T01): scaffold Python project and quality checks`; actual hash trả sau commit, resolve bằng subject/Task-ID.
- **Known limits/next:** settings mới là config contract, chưa probe PG/Redis; API/worker/inference chưa chạy. T02 tiếp tục Compose tuần tự sau Orchestrator review, bằng worker mới.

<a id="s-t02-a02"></a>
## Phase 0 / T02 / Attempt T02-A02 — Docker Compose nền tảng

- **Status + agent/model/effort:** đề nghị COMPLETE; attempt A01 chỉ có runtime quota failure, A02 là worker fresh `gpt-5.6-sol`/`xhigh`, runtime record thread `01a0a82f-8df3-7701-8a25-9ceff7d4dce9`, turn `01a0a82f-8e7e-7762-bb12-c2f9c7fd7971`.
- **Thời gian/dependency:** bắt đầu 2026-09-16 10:08 +07:00; T01 actual commit `ff8069abfd2e41fb9618eb7d35fa22bf220a39d6` đã được Orchestrator nghiệm thu; baseline worktree sạch.
- **Behavior:** Compose mặc định chạy PostgreSQL/Qdrant/Redis và health-only FastAPI. Profile `local-storage` thêm MinIO + one-shot bootstrap fixture. `/health/live` chỉ báo process; `/health/ready` chạy PG `SELECT 1`, Redis `PING`, Qdrant `/readyz` đồng thời với deadline và trả component status đã redacted/HTTP 503 khi dependency lỗi.
- **Images/build:** multi-stage API image cài đúng uv `api` group, chạy non-root, không có ingestion/model/OCR dependency. Base/service images khóa patch tag + multi-platform manifest digest: Python 3.12.13, uv 0.11.16, PostgreSQL 17.11, Redis 8.10.1, Qdrant 1.19.1 unprivileged, MinIO/MC release 2025-07-23/2025-07-21 từ official Quay.
- **Ports/persistence/secrets:** API 8000 và MinIO 9000/9001 bind loopback; PG/Qdrant/Redis chỉ internal Compose. Named volumes cho PG/Qdrant/Redis/MinIO, không bind database files NTFS. Bootstrap tạo ignored secret files; Compose mounts secret files, không ghi credential plaintext vào YAML/output.
- **Interfaces/files:** public `rag_core.api.create_app`; `HealthChecks` hỗ trợ adapter thật/injection test; typed `QDRANT_URL`, `HEALTH_TIMEOUT_SECONDS`, optional `DATABASE_PASSWORD_FILE`. `.dockerignore` loại env/key/cache/corpus/runtime. `scripts/bootstrap_local.ps1`, `scripts/smoke_local.ps1`, `scripts/t02_qdrant_fixture.py` phục vụ local acceptance.
- **Migrations/compatibility:** không business schema/Alembic/index migration. T02 tạo synthetic table/collection/object chỉ trong local acceptance volumes. Settings cũ nay cần thêm `QDRANT_URL`; empty optional env values được ignore. Worker/dispatcher/inference không được khai báo trước task sở hữu.
- **Validation:** Compose config/build/up/ps PASS; actual health và Redis outage chứng minh ready 200→503→200 trong khi live vẫn 200. Restart giữ PG/Qdrant marker và MinIO timestamp/size/ETag; inspect chứng minh ports/volumes/images/health. Ruff, strict mypy, unit/settings/docs checks PASS. Output và failure đã sửa nằm ở [H-T02-A02](handoffs.md#h-t02-a02); không mock persistence/provider/GPU.
- **README/RUNBOOK:** thêm Docker Desktop prerequisites, exact bootstrap/start/stop/health commands, ports, secret handling, dependency groups và VERIFIED/DESIGNED boundary.
- **Commit:** subject `feat(T02): add local Docker infrastructure`; actual hash trả sau commit, resolve bằng subject/Task-ID.
- **Known limits/next:** API mới có health routes; MinIO chưa là readiness dependency vì storage adapter thuộc T11; không có schema/auth/business routes, worker, dispatcher, inference, provider, GPU, performance hoặc cloud deployment. T03 chỉ bắt đầu sau Orchestrator review completion commit này.

<a id="s-t02-a03"></a>
## Phase 0 / T02 / Attempt T02-A03 — Tiếp quản review và completion commit

- **Status + agent/model/effort:** completion candidate; worker `/root/t02_a03`, fresh `gpt-5.6-sol`/`xhigh`, thread `01a0a9a0-7c47-7b43-bd6c-09b38a8303a8`, turn `01a0a9a0-7cc9-7031-adb0-83aed0d1bcdf`; bắt đầu 2026-09-16 16:51 +07:00, kết thúc sau completion commit/timestamp trong báo cáo post-commit.
- **Phục hồi/dependency:** A02 đã để lại implementation và bằng chứng local nhưng không có completion commit, nên chưa COMPLETE. Khi người dùng continue, Orchestrator chỉ thấy root trong lifecycle; nguyên nhân A02 không còn active chưa xác định. Giữ lịch sử A01/A02; T01 completion `ff8069abfd2e41fb9618eb7d35fa22bf220a39d6` vẫn là last-good.
- **Scope/interfaces/files:** tiếp quản đúng 21 file T02 dirty/untracked; không thay code/test/config A02, chỉ cập nhật README/RUNBOOK và ba sổ docs recovery/evidence. Public `create_app`, `HealthChecks`, typed `QDRANT_URL`/`HEALTH_TIMEOUT_SECONDS`/`DATABASE_PASSWORD_FILE` và empty-env behavior giữ theo S-T02-A02. Không database/index/business schema migration, không thay product/session semantics.
- **Validation:** DoD-1 config/up-build/wait/current smoke PASS trên Docker29.5.2; final rebuilt image `sha256:64673d7032b879f4a76bcb65b48766fcbd29165802343f664f7133f3e69bba42`, Python3.12.13/non-root10001, SHA256 all6Python source và running container/tag equality PASS. DoD-2 current ps/redacted inspect đúng named volumes/internal DB-broker/loopbackAPI-MinIO; readonly PG/Qdrant marker và MinIO Date03:20:12/28B/ETagf9eb58fcfbb8e28513335e6d2fcc6b52-1 không đổi. Controlled restart và Redis outage kế thừa A02 vì source/config liên quan không đổi, không claim A03 chạy lại. Locked sync72/39, Ruff, strict mypy6source, 7unit trên hostCPython3.12.4, docs/lock/PowerShell parse/scope/secrets/prompt checks PASS; D1–D5 có output nguyên văn, D6 cached review/commit dưới handoff. Integration là Docker thật; unit injection không là live provider.
- **README/RUNBOOK:** giữ commands/prerequisites/VERIFIED-DESIGNED boundary đã triển khai A02, bổ sung A03 recovery/current-image/inherited-evidence links.
- **Evidence/commit:** output/cwd/commands/exit/expected/actual từng DoD/D1–D6 tại [H-T02-A03](handoffs.md#h-t02-a03); completion subject `feat(T02): add local Docker infrastructure`, hash/output post-commit trả root; đề nghị COMPLETE có hiệu lực sau commit thành công và Orchestrator review.
- **Known limits/next:** giữ toàn bộ giới hạn T02-A02; T03 chỉ sau completion commit và Orchestrator review.

<a id="s-t03-a01"></a>
## Phase 0 / T03 / Attempt T03-A01 — Candidate recovery

- **Status/runtime:** A01 kết thúc do runtime quota trước completion commit; worker `/root/t03_a01`, `gpt-5.6-sol`/`xhigh`, fresh context, started 2026-09-16 17:05 +07:00. Recovery event nguyên văn tại [H-T03-A01](handoffs.md#h-t03-a01), không shell output.
- **Recovered implementation:** 16 dirty/untracked T03 candidate files: contracts v1/SSE/design/examples, exporter, contract tests, 3 JSON artifacts, dev-only jsonschema dependency/lock, README/RUNBOOK/tasks/handoffs. Không có T03 summary hoặc completion commit; stale checkpoint/links được A02 sửa.
- **Validation boundary:** các PASS được A01 báo qua messages, không có actual logs trong recovery brief; không dùng reports đó thay current DoD evidence. A02 review candidate và chạy actual checks mới. Không suy đoán timestamp quota/end từ runtime message.
- **Migration/limits:** v1 design đầu tiên, không business runtime/client hay DB/index migration; không auth, session persistence, ingestion, retrieval, provider hoặc SSE transport implementation.

<a id="s-t03-a02"></a>
## Phase 0 / T03 / Attempt T03-A02 — Versioned API structural contracts

- **Status/runtime/dependencies:** completion candidate; worker `/root/t03_a02`, model `gpt-5.6-sol`/effort `xhigh`, fresh `fork_turns="none"` theo spawn/runtime verification của Orchestrator; started 2026-09-17 11:51 +07:00, end sau completion commit trả root. Baseline `main`/T02 `851ff1d10b49b6a4d7ae7e1756f2c2a1b8562e96`; T01 `ff8069abfd2e41fb9618eb7d35fa22bf220a39d6`/T02 COMPLETE đã nghiệm thu, notes/summary/evidence đọc lại. A02 giữ source/test/config candidate đúng, bổ sung recovery/actual evidence/summary/docs.
- **Interfaces/files:** `rag_core.contracts.v1` có strict-extra models, literals domain/language/session/link/job/answerability/error, server `ContractLimits`/`INITIAL_LIMITS` và measured `FileMeasurements`; request/response session/document/job/query/citation/health/error. `rag_core.contracts.sse` có discriminated `SSEEvent`, payloads meta/evidence/delta/done/error, `SSEHeartbeat` và `SSESequence` complete-trace validator. Modules không phụ thuộc FastAPI/provider SDK; design module chỉ sinh inventory/schema, không mount handlers.
- **Query decisions:** session UUID bắt buộc; default không document_ids kể cả explicit null, dump bỏ None để hợp lệ round-trip; document subset nonempty/unique <=50; multilingual optional nonempty subset, EN/VI languages unique. Cấm unknown body fields như authenticated identity/system/developer prompt/tools/limits. Không kiểm quyền từ body hoặc arbitrary storage key. Mọi scope/runtime gate vẫn current-session-only theo P01, không fallback kho user.
- **History/limits:** history chỉ user/assistant và luôn untrusted, không evidence/transcript store. Chấp nhận input vượt processing budget để T20 truncate bằng tokenizer thật; `HistoryMetadata` kiểm received/retained counts, retained <=20 messages/8000 tokens, cả hai token counts null nếu chưa đo, truncated nhất quán; JSON warning/SSE meta thông báo. Defaults còn lại: file 100 MiB/1000 pages, 50 docs/session, question 4000 characters, context 8000/output 1024 tokens. T03 đo/parse/tokenizer/runtime enforcement chưa implement.
- **Lifecycle/storage:** source `version_id` opaque hoặc SHA256 bắt buộc, alias/bucket/key không là bằng chứng quyền; không arbitrary URL/credentials. Response/citation `version_id` là UUID DocumentVersion khác storage version. Session/link states + scope_revision contracts diễn tả tombstone/detach giữ source/index; persistence/revision/registration/reuse/auth thuộc tasks sau.
- **Evidence/locator decisions:** PDF physical page one-based, printed label riêng; DOCX heading + paragraph/table; XLSX sheet/cell/header/unit với range ordering/sheet bounds; PPTX one-based slide; text lines/paragraph/offset, CSV rows/columns, HTML heading/block, image/OCR bbox finite nonnegative pixels. Non-PDF không nhận page giả. Citation IDs unique; contexts tham chiếu cùng document/chunk; supported có permitted answer citation, insufficient cần reason, no_relevant_evidence không citations/contexts giả. Missing usage/timings null. Structural checks không xác minh factual support/quote/ownership.
- **SSE decisions:** tăng ID dương trong request; meta đầu, evidence trước delta/done, đúng một done/error terminal, early meta->error hợp lệ; EOF partial invalid. Done identity/revision/domain/evidence/history match meta/evidence; whitespace delta hợp lệ; heartbeat comment single-line riêng. Không implement wire transport/token buffers/revision checks/upstream cancellation/replay và không gọi logical traces là streaming live.
- **Design/export:** `ENDPOINTS` 13 operations, 11 business DESIGNED/unmounted +2 health served; auth design yêu cầu UserJWT AND AppServiceKey; idempotency header/pagination/error statuses/Retry-After và deferred admin/metrics inventory. `scripts/export_openapi.py` sinh designed+served+examples, kiểm OpenAPI model/local refs/48 Draft2020-12 schemas/37 synthetic examples UUID format +Pydantic roundtrip; `--check` đọc/kiểm drift không ghi. Served factory inspection không load secrets/probe services; app business requests vẫn framework 404, không stub success.
- **Dependencies/migrations:** chỉ thêm dev jsonschema 4.26.0 +transitive attrs/jsonschema-specifications/referencing/rpds-py, lock 77 packages; không API image dependency mới. v1 design đầu tiên không business clients hoặc DB/index migration; future changes phải regenerate artifacts, kiểm compatibility/client impact theo P13 cùng task.
- **Validation:** locked dev/api sync PASS trên CPython 3.12.4/uv 0.11.16; Ruff PASS; strict mypy 11 source PASS; 7 unit PASS; 83 contract PASS; exporter và --check PASS: 13 operations/2 health/48 schemas/37 examples; scope/secrets/ignore/prompt unchanged PASS. T03 không yêu cầu/có live provider, auth/factual/services integration test; không chạy lại T02 integration vì source/config T02 giữ nguyên. Actual output/cwd/commands/exit/DoD/D1–D6 tại [H-T03-A02](handoffs.md#h-t03-a02).
- **README/RUNBOOK:** quality/export commands, design/served snapshots và synthetic examples links, R05 endpoint matrix DESIGNED vs served health, R06 history/languages/limits, R07 logical trace vs runtime, R08 locators/storage version/lifecycle; sửa evidence sang A02 và giữ A01 recovery link.
- **Completion scope:** đúng 17 files: README/RUNBOOK, docs tasks/handoffs/summary, pyproject/lock, 3 docs/apiJSON, exporter, 5 contracts modules, contracttests. Commit subject `feat(T03): define versioned API contracts`; actual hash/output trả post-commit, COMPLETE chỉ hợp lệ sau successful commit +root review. Không amend/self-reference hash.
- **Known limits/next:** không blocker T03 cần user input. Auth/ownership/current-scope/readiness/tokenizer/factual/cancellation gates chưa implement, business API/runtime/worker/UI vẫn DESIGNED. Root review completion diff/DoD/hash rồi fresh worker T04; A02 kết thúc, không nhận task tiếp/retry.
