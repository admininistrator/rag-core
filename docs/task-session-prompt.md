# Prompt bắt đầu một task trong session mới

Thay `Txx` bằng task được giao, ví dụ `T08`. Phần Git bên dưới cho phép push;
nếu chỉ muốn commit local, đổi thành “không push”. Không cần đính kèm protocol Hermes.

```text
Làm việc trong C:\Users\Admin\Documents\GitHub\rag-core.
Hoàn thiện duy nhất task Txx trong docs/tasks.md rồi dừng, không tự drain/task tiếp.

Áp dụng chế độ một task/session đã được tôi xác nhận ngày 2026-09-26:
agent hiện tại trực tiếp sửa code/tests/docs, kiểm chứng và commit;
không dùng cơ chế Orchestrator/Worker/Kanban/model bắt buộc cũ, không spawn subagent.
Giữ nguyên scope sản phẩm, dependencies và toàn bộ DoD.

Trước khi sửa, đọc AGENTS.md; task Txx và execution notes của từng dependency;
các plan references (P01 nếu liên quan dữ liệu/truy xuất), P13;
current checkpoint trong docs/handoffs.md, docs/implementation-summary.md,
README.md và RUNBOOK.md. Kiểm branch/HEAD/Git status và baseline dirty files.
Nếu task dở, đối chiếu disk/checkpoint và tiếp quản phần dở, không làm lại tùy tiện.
Chỉ triển khai khi mọi dependency COMPLETE; ghi task/attempt và kế hoạch ngắn.

Làm đúng phạm vi task. Chạy từng dòng DoD riêng và D1–D6; ghi command/cwd/config,
exit code và output thật đã che secrets vào handoffs. Không dùng mock thay live,
không skip/hạ DoD, không sửa gold để pass. Nếu thiếu quyền/credential hoặc mâu thuẫn
yêu cầu, hỏi tôi; lưu checkpoint/reproduction thay vì nhận COMPLETE.

Cập nhật task notes, implementation-summary, README/RUNBOOK cùng implementation
(N/A phải có lý do). Giữ session-only retrieval, retention và app-owned storage/history;
không sửa prompt corpus gốc, không tích hợp Scarlet hoặc triển khai server.

Review diff/secrets/scope, stage đúng code/tests/docs của task và tạo completion commit
có task ID. Tôi cho phép push commit lên origin/nhánh hiện tại sau khi kiểm remote;
không force push, merge, rewrite lịch sử hoặc commit secrets/raw restricted data/cache/scratch.
Kiểm commit và remote hash sau push.

Báo task/attempt/status, commit/link GitHub, từng DoD và evidence, blockers/giới hạn,
và task kế tiếp đã đủ điều kiện bắt đầu hay chưa. Dừng sau task này.
```
