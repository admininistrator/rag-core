# Prompt bắt đầu một task trong session mới

Thay `Txx` bằng task được giao, ví dụ `T29`. Phần Git bên dưới cho phép push;
nếu chỉ muốn commit local, đổi thành “không push”. Không cần đính kèm protocol Hermes.
Từ 2026-10-30 dự án chuyển sang máy macOS; `<REPO>` là thư mục clone
`https://github.com/admininistrator/rag-core.git` trên máy đang làm việc.

## Chuẩn bị máy mới (làm một lần, trước session đầu tiên)

1. `git clone https://github.com/admininistrator/rag-core.git` rồi `cd rag-core`.
2. Chép `.env` (gitignored, chứa provider keys) từ máy cũ qua kênh an toàn; không commit, không dán vào chat.
3. Cài `uv` và Docker Desktop; `uv sync`.
4. Corpus không nằm trong Git; chỉ cần cho task đánh giá (T30/T31), tạo lại bằng
   `uv run python corpus-documents/scripts/setup_corpus.py --all` và
   `uv run python corpus-documents/scripts/validate_corpus.py --all`.
5. Image local (`rag-core-*:t17-cpu`, `:t19`, `:t26`) phải build lại trên máy mới. Image ngoài được pin
   theo digest; trên Apple Silicon cần xác nhận digest chạy được arm64 hoặc qua emulation — đây là việc
   kiểm tra đầu tiên của session, lỗi thì ghi vào handoffs, không tự đổi pin ngoài scope task.

## Prompt chung

```text
Làm việc trong <REPO> (clone của https://github.com/admininistrator/rag-core, máy macOS).
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

Máy đã chuyển từ Windows sang macOS: các lệnh PowerShell/đường dẫn Windows trong
README/RUNBOOK/handoffs cũ là lịch sử. Lệnh cần cho task mà chỉ có bản Windows thì
chạy bản tương đương trên macOS, ghi lệnh thật vào handoffs và cập nhật RUNBOOK
trong phạm vi task. Ghi OS/kiến trúc CPU/Docker version vào evidence.

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

## Prompt sẵn dùng cho T29

Dán nguyên prompt chung ở trên với `Txx` = `T29`, rồi thêm đoạn sau:

```text
Bối cảnh T29: T27/T28 COMPLETE (HEAD 34e5540 = origin/main lúc chuyển máy).
Playwright chưa có trong pyproject/uv.lock; thêm dependency pin bản thực và
cài browser là một phần T29. tests/e2e/test_admin_browser.py chưa tồn tại.
Backend phải là Docker stack thật (PG/Redis/Qdrant/MinIO/inference/worker),
không dùng mock data/ảnh. Admin credentials/browser profile/screenshots chứa
secrets không được vào Git; screenshots/log paths ghi trong handoffs.
Commit dự kiến: test(T29): verify administration browser workflows.
```

## Trạng thái sẵn sàng (2026-10-30)

**T29 có thể bắt đầu ngay** về mặt dependency: T27 và T28 COMPLETE, completion commit
`34e5540` đã có trên `origin/main`, `scripts/check_docs.py` PASS (37 tasks, acyclic).
Điều kiện môi trường cần có trước khi chạy DoD: đã làm xong các bước ở mục
“Chuẩn bị máy mới” (1–3, 5), Docker stack lên được trên Mac. Bước 4 (corpus) không cần cho T29.
T30–T36 vẫn TODO và nối tiếp tuần tự (T30 cần T29 COMPLETE, rồi T31 → … → T36),
nên chưa task nào trong số đó bắt đầu được trước khi T29 xong.
