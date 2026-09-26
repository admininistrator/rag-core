# Agent State — RAG Core

## Hiện hành: một task/session

User xác nhận ngày 2026-09-26 agent hiện tại trực tiếp triển khai, kiểm chứng, cập nhật docs, commit và push task được giao; bỏ Orchestrator/Worker/Kanban cũ. T07-A06 COMPLETE khi completion commit `feat(T07): prepare XQuAD bilingual evaluation slices` thành công và được kiểm; runtime Codex gpt-6-sol/xhigh, không subagent.21bilingual+138regression tests, real setup/validator, rerun491published+3cache, Ruff/mypy17 và docs checks có evidence tại [H-T07-A06](handoffs.md#h-t07-a06). Commit hash/push result trả sau commit; resolve subject trong Git. Legacy scratch giữ nguyên local. **Dừng sau T07**; T08 TODO và đủ dependencies để người dùng mở session mới. AGENTS/P14 là workflow hiện hành; [prompt mẫu](task-session-prompt.md).

## Lịch sử Hermes (đã kết thúc)

- Board: `2026-09-26-0058-rag-core-corpus-drain` (mới, xác minh ban đầu 0 cards; workspace `C:/Users/Admin/Documents/GitHub/rag-core`).
- Current phase: Phase 1 / T07, sau Hermes Phase 0 retrospective review PASS.
- Phase status: Phase 0 T00–T03 Hermes Reviewer PASS card `t_9dfeffd9`; Phase 1 T04–T06 COMPLETE, T07 BLOCKED (A05 terminal safety gate persists), T08 TODO; Phase 1 review chưa chạy.
- Current task(s): T07-A05 card `t_90838461` blocked; A01–A04 blocked, no resumes.
- Running Hermes cards: none; A01–A05 blocked, Phase 0 Reviewer done.
- Last accepted task: T06-A03, `7d40fc4affbb009dbdda51d6d659cdf2371915d6`.
- Last reviewer result: Phase 0 PASS, card `t_9dfeffd9`; independent pytest rerun exit 1 do 4 Windows tmp_path setup errors, 86 passed, historical acceptance evidence retained.
- Human blockers: T-H2 chat authorization already received and recorded; terminal runtime nevertheless denies exact inspection again in A05. Operator must enable/approve precisely this runtime operation or provide an explicit acceptable resolution; no blanket bypass/scratch deletion/DoD relaxation. Earlier optional path-length denial remains skipped only; T-H1 COMPLETE.
- Technical blockers: terminal safety gate rejects approved read-only hash/mtime/source snapshot (A04 and A05). A04 setup/validator and 5/5 bilingual tests PASS with short Windows temp; deterministic rerun/hash and D1–D5 closure absent. No T07 completion claim.
- Backlog blockers: T08 clean-clone reproduction vẫn TODO, không phải bằng chứng T07 bị chặn.
- Git baseline: bootstrap/review commit `7696f83fa2d718bcad3ca6d69f627ff886f2d10d`; clean `main` tại 2026-09-26 01:21:49 SEAST trước T07-A01. Các docs orchestration T07 IN_PROGRESS phát sinh sau baseline, Worker không sửa.
- Next action: STOP T07 branch pending operator-level safety gate resolution for precisely the approved read-only inspection; do not dispatch A06 or T08, do not retry/rephrase/alternate-tool the denied outcome. Preserve dirty candidate and scratch.
- Updated at: 2026-09-26 01:21:49 SEAST (kiểm bằng `date`).

## Chuyển giao Codex → Hermes

Quyết định trực tiếp của người dùng supersede các quy định điều phối cũ tương ứng tại AGENTS.md/P14/handoffs: Orchestrator là bên duy nhất ghi `docs/`, quản lý Kanban và tạo completion commit task sau khi kiểm diff/evidence; Worker chỉ triển khai source/tests/config và README/RUNBOOK ngoài `docs/`, không commit completion; Reviewer chỉ đọc và trả handoff. Artifact thuộc docs do Worker sinh staging ngoài docs rồi bàn giao để Orchestrator kiểm và đưa nguyên nội dung vào docs. Không sửa prompt corpus gốc; không thay bất biến sản phẩm, phạm vi hoặc DoD. ID T00–T36 và trạng thái TODO/IN_PROGRESS/BLOCKED/COMPLETE được giữ nguyên để `scripts/check_docs.py` hoạt động. Không resume terminal/session Worker/Reviewer; mỗi attempt/review dùng session cô lập mới. Worker/Reviewer không spawn agent cháu; không chạy song song. Model profile thực tế lúc bootstrap: Orchestrator `gpt-6-sol` (openai-codex), Worker `gpt-6-luna` (openai-codex), Reviewer `gpt-5.6-sol` (openai-codex); người dùng đã chủ động cho phép dùng đúng cấu hình hiện tại, không đòi đổi model/reasoning_effort. Không suy luận effort thực tế từ tên model hoặc prompt. Lịch sử Codex T00–T06 giữ nguyên, không coi nghiệm thu Codex là Hermes phase review.
