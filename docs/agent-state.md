# Agent State — RAG Core Hermes drain

- Board: `2026-09-26-0058-rag-core-corpus-drain` (mới, xác minh ban đầu 0 cards; workspace `C:/Users/Admin/Documents/GitHub/rag-core`).
- Current phase: Phase 1 / T07, sau Hermes Phase 0 retrospective review PASS.
- Phase status: Phase 0 T00–T03 Hermes Reviewer PASS card `t_9dfeffd9` (review-report); Phase 1 T04–T06 COMPLETE, T07–T08 TODO, toàn Phase 1 sẽ review sau T08.
- Current task(s): T-H1 COMPLETE; chuẩn bị JIT T07-A01 sau bootstrap/review commit.
- Running Hermes cards: none; Reviewer card `t_9dfeffd9` `done`, run 1/session `20260926_010005_c64172`.
- Last accepted task: T06-A03, `7d40fc4affbb009dbdda51d6d659cdf2371915d6`.
- Last reviewer result: Phase 0 PASS, card `t_9dfeffd9`; independent pytest rerun exit 1 do 4 Windows tmp_path setup errors, 86 passed, historical acceptance evidence retained.
- Human blockers: none. T-H1 COMPLETE: `git var GIT_AUTHOR_IDENT` exit 0 sau khi người dùng cấu hình, không in identity. Người dùng đã kết thúc `USER-PAUSED AFTER T06` và phê duyệt dùng cấu hình model/reasoning hiện tại của các profile.
- Technical blockers: chưa ghi nhận; capability/evidence sẽ xác minh tại từng task.
- Backlog blockers: T08 clean-clone reproduction vẫn TODO, không phải bằng chứng T07 bị chặn.
- Git baseline: clean `main`, HEAD `7d40fc4affbb009dbdda51d6d659cdf2371915d6` trước bootstrap; baseline sau bootstrap chỉ gồm tài liệu quản trị Hermes do Orchestrator tạo/sửa, chưa commit.
- Next action: kiểm docs/diff, stage đúng docs rồi commit bootstrap/review độc lập; dispatch Worker mới T07-A01. Sau T08 review toàn Phase 1 T04–T08. Một Worker hoặc Reviewer active tối đa; chỉ tạo card JIT.
- Updated at: 2026-09-26 00:58 SEAST (board timestamp; kiểm bằng `date`).

## Chuyển giao Codex → Hermes

Quyết định trực tiếp của người dùng supersede các quy định điều phối cũ tương ứng tại AGENTS.md/P14/handoffs: Orchestrator là bên duy nhất ghi `docs/`, quản lý Kanban và tạo completion commit task sau khi kiểm diff/evidence; Worker chỉ triển khai source/tests/config và README/RUNBOOK ngoài `docs/`, không commit completion; Reviewer chỉ đọc và trả handoff. Artifact thuộc docs do Worker sinh staging ngoài docs rồi bàn giao để Orchestrator kiểm và đưa nguyên nội dung vào docs. Không sửa prompt corpus gốc; không thay bất biến sản phẩm, phạm vi hoặc DoD. ID T00–T36 và trạng thái TODO/IN_PROGRESS/BLOCKED/COMPLETE được giữ nguyên để `scripts/check_docs.py` hoạt động. Không resume terminal/session Worker/Reviewer; mỗi attempt/review dùng session cô lập mới. Worker/Reviewer không spawn agent cháu; không chạy song song. Model profile thực tế lúc bootstrap: Orchestrator `gpt-6-sol` (openai-codex), Worker `gpt-6-luna` (openai-codex), Reviewer `gpt-5.6-sol` (openai-codex); người dùng đã chủ động cho phép dùng đúng cấu hình hiện tại, không đòi đổi model/reasoning_effort. Không suy luận effort thực tế từ tên model hoặc prompt. Lịch sử Codex T00–T06 giữ nguyên, không coi nghiệm thu Codex là Hermes phase review.
