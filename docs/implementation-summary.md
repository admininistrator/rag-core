# Implementation Summary

> Sổ ghi chú thực thi theo phase/task/attempt. Chỉ ghi implementation đã làm; kế hoạch tương lai nằm ở plan/tasks.
> Output commands ở [handoffs.md](handoffs.md); [tasks.md](tasks.md) là nguồn trạng thái task.

## Tổng quan hiện tại

| Hạng mục | Trạng thái thật |
| --- | --- |
| Bối cảnh/kiến trúc/backlog/agent workflow | Đã viết và kiểm chứng T00; completion commit là bằng chứng đóng task |
| Python project/config/quality | T01 implemented + verified trên CPython 3.12.4; completion commit là bằng chứng đóng task |
| README/RUNBOOK | Có prerequisites, quality và Docker health quickstart T01–T02 đã kiểm; business quickstart chưa tồn tại |
| Runtime/API/Docker | T02 Compose + health-only API implemented/verified local; không có business API/worker/inference |
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
