# Implementation Summary

> Sổ ghi chú thực thi theo phase/task/attempt. Chỉ ghi implementation đã làm; kế hoạch tương lai nằm ở plan/tasks.
> Output commands ở [handoffs.md](handoffs.md); [tasks.md](tasks.md) là nguồn trạng thái task.

## Tổng quan hiện tại

| Hạng mục | Trạng thái thật |
| --- | --- |
| Bối cảnh/kiến trúc/backlog/agent workflow | Đã viết và kiểm chứng T00; completion commit là bằng chứng đóng task |
| README/RUNBOOK | Skeleton có thiết kế và ownership; chưa có quickstart ứng dụng đã chạy |
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
