# Implementation Summary

> Sổ ghi chú thực thi theo phase/task/attempt. Chỉ ghi implementation đã làm; kế hoạch tương lai nằm ở plan/tasks.
> Output commands ở [handoffs.md](handoffs.md); [tasks.md](tasks.md) là nguồn trạng thái task.

## Tổng quan hiện tại

| Hạng mục | Trạng thái thật |
| --- | --- |
| Bối cảnh/kiến trúc/backlog/agent workflow | Đã viết và kiểm chứng T00; completion commit là bằng chứng đóng task |
| Python project/config/quality | T01 implemented + verified trên CPython 3.12.4; completion commit là bằng chứng đóng task |
| README/RUNBOOK | Có prerequisites, env/quality commands T01 đã kiểm; quickstart ứng dụng chưa tồn tại |
| Runtime/API/Docker/UI | Chưa triển khai |
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
