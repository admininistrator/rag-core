# RAG Core

RAG core độc lập để các ứng dụng chat gọi qua API: hỏi đáp trên tài liệu, trích dẫn có vị trí nguồn và truy xuất xuyên tiếng Việt/tiếng Anh.

> **Trạng thái: thiết kế / hồ sơ triển khai.** Bộ tài liệu T00 đã được kiểm chứng; T01–T36 chưa làm. Chưa có ứng dụng, Docker image, API hoặc UI hoạt động; các lựa chọn dưới đây là thiết kế mục tiêu.

## Phạm vi đã chốt

- Default RAG: toàn bộ tài liệu đã upload/đăng ký cho **session hiện tại**.
- Document RAG: tập tài liệu được chọn trong session hiện tại.
- Multilingual RAG: cùng phạm vi session, hỗ trợ EN/VI và tìm xuyên ngôn ngữ.
- API JSON/SSE trả `answer`, `answerability`, `citations`, `contexts`; hiểu câu hỏi nối tiếp từ history do app gửi.
- App sở hữu tài liệu gốc trong S3/MinIO và lịch sử chat. RAG core sở hữu metadata/index; xóa session giữ nguyên tài liệu gốc và index.
- UI quản trị local cho trạng thái tài liệu/jobs/sessions/index/evaluation, có auth và audit.
- Technical/Custom Domain thêm qua registry sau này. Scarlet chưa được tích hợp trong đợt này.

**Tài liệu ngoài session không được tham gia truy vấn, kể cả của cùng người dùng.** Giữ index không cấp quyền cho session mới.

## Kiến trúc dự kiến

Python 3.12/FastAPI, PostgreSQL metadata, Qdrant, Celery/Redis, Docling/Tesseract OCR, BGE-M3 + multilingual reranker, DeepSeek/Anthropic adapters; Docker Compose trên Windows/WSL2. Admin UI dùng Jinja2/CSS/JavaScript trong FastAPI.

Máy mục tiêu: RAM 16 GB, RTX 4060 Laptop 8 GB VRAM; tài liệu nguồn khoảng <=1 GB; kiểm thử 15–20 người dùng đồng thời. Chưa có số đo RAM/VRAM/độ trễ hoặc benchmark chất lượng.

## Bắt đầu ở trạng thái hiện tại

1. Đọc [AGENTS.md](AGENTS.md).
2. Đọc [kế hoạch](docs/plan.md), [tasks](docs/tasks.md), [handoff](docs/handoffs.md) và [implementation summary](docs/implementation-summary.md).
3. Mở session Orchestrator GPT-6-Astra, dùng prompt người dùng nhận cùng bộ hồ sơ này; bắt đầu T01 sau khi kiểm T00 đã commit/complete.
4. Mỗi task dùng một worker mới GPT-5.6-Sol/xhigh; triển khai tuần tự, cập nhật tài liệu và commit mỗi task.

Chưa có quickstart chạy ứng dụng. T01–T02 sẽ thêm commands đã kiểm chứng; T19/T26 thêm ingest/query; T28–T29 thêm admin UI; T35 kiểm lại hướng dẫn cho người tích hợp.

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

- **T01–T02:** prerequisites, env setup, Docker start/stop/health.
- **T04–T08:** corpus setup/validation, source licenses, actual counts.
- **T09–T12:** authentication, session và storage registration.
- **T13–T19:** format/OCR matrix, model setup, ingestion commands.
- **T20–T26:** query JSON/SSE, history, citations, provider configuration và live smoke.
- **T27–T29:** admin URL/login, UI workflows.
- **T30–T34:** benchmark reports, performance, reliability, backup/restore.
- **T35–T36:** quickstart tích hợp đã kiểm chứng và trạng thái nghiệm thu cuối.

## Nguyên tắc cập nhật

README và RUNBOOK được cập nhật trong từng task; mục mới ghi rõ `DESIGNED`, `IMPLEMENTED` hoặc `VERIFIED` cùng task/evidence. Không quảng cáo tính năng, format hay tốc độ chưa đo. Secrets, tài liệu gốc, model weights và database dumps không thuộc source code.
