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

## Prompt chuyển dự án hoàn toàn sang macOS (chạy một lần, trước T29)

Đây là việc bảo trì nền tảng ngoài backlog T00–T36, người dùng duyệt ngày 2026-10-30.
Chạy session này trước task T29; sau khi xong, các task dùng prompt chung bên dưới.

```text
Làm việc trong <REPO> (clone của https://github.com/admininistrator/rag-core) trên macOS.
Nhiệm vụ duy nhất: chuyển nền tảng phát triển/vận hành local của dự án từ Windows sang
macOS hoàn toàn, rồi dừng. Đây là việc bảo trì ngoài backlog, tôi duyệt ngày 2026-10-30;
không làm T29 hay task nào khác, không thêm tính năng, không đổi behavior sản phẩm/API.

Quyết định của tôi (ghi vào docs như decision 2026-10-30):
- macOS là nền tảng local duy nhất được hỗ trợ từ nay; Windows chỉ còn là lịch sử.
- Script PowerShell (scripts/bootstrap_local.ps1, bootstrap_storage_test.ps1,
  smoke_local.ps1) được thay bằng bản POSIX shell hoặc Python cùng hành vi; chỉ xóa
  bản .ps1 sau khi bản thay thế chạy thật PASS trên Mac.
- Không viết lại lịch sử: evidence/attempt cũ trong handoffs, tasks notes của task
  COMPLETE và implementation-summary giữ nguyên; chỉ thêm ghi chú migration.

Workflow: áp dụng AGENTS.md, chế độ một task/session 2026-09-26 (agent trực tiếp sửa,
kiểm chứng, commit; không spawn subagent). Mọi bất biến §3, quy tắc Git/secrets §7,
DoD chung D1–D6 (P13) vẫn giữ. Trước khi sửa, đọc AGENTS.md, docs/plan.md (P00, P02,
P12, P13, P14), current checkpoint docs/handoffs.md, docs/task-session-prompt.md,
README.md, RUNBOOK.md. Ghi baseline: branch/HEAD = origin/main?, git status, macOS
version, kiến trúc CPU (uname -m), RAM, Docker Desktop/Compose version, uv/Python.

Phạm vi phải làm:
1. Inventory: rg -i "windows|powershell|LiteralPath|\.ps1|C:\\\\" trên toàn repo (trừ
   evidence lịch sử) và phân loại: (a) lệnh/hướng dẫn vận hành phải chuyển,
   (b) code phụ thuộc nền tảng, (c) validation bảo mật đa nền tảng phải GIỮ
   (ví dụ chặn tên reserved/backslash/traversal trong corpus_root/common.py),
   (d) lịch sử để nguyên. Ghi bảng phân loại vào handoffs.
2. Code/scripts: chỉ sửa chỗ hỏng hoặc chỉ-Windows trên macOS (ví dụ nhánh
   WindowsSelectorEventLoopPolicy trong dispatcher.py, comment ACL/POSIX mode trong
   local_issuer.py/setup_admin.py: bảo đảm file secret local được tạo mode 0600 trên
   Mac). Không refactor ngoài nhu cầu migration.
3. Line endings: hiện có file working tree CRLF/mixed; kiểm .gitattributes, chuẩn hóa
   LF cho script/config chạy trong container hoặc shell; đặt bit thực thi cho script.
4. Docker trên Apple Silicon: build lại image local (rag-core-*:t17-cpu, :t19, :t26...).
   Với image ngoài pin theo digest, kiểm từng digest có manifest linux/arm64 không.
   Nếu thiếu: ưu tiên pin lại digest multi-arch index của CÙNG version (ghi digest
   cũ/mới); không nâng version. Không làm được thì dừng hỏi tôi giữa emulation amd64
   và phương án khác. Model weights/tokenizer/revision (BGE-M3, reranker) giữ nguyên;
   ghi fingerprint và nếu embedding arm64 khác amd64 thì báo rủi ro tương thích index.
5. GPU profile (compose.gpu.yaml, CUDA): không khả dụng trên Mac. Chạy capability
   check thật và ghi "unavailable", không coi là PASS, không tự port sang MPS/Metal
   (đó là thay đổi kiến trúc, phải hỏi).
6. Local config: tạo lại .local/ (auth/api/storage/worker config, admin) bằng các
   script setup của repo trên Mac, không chép .local từ Windows. .env do tôi đã chép
   sang: chỉ kiểm tồn tại và các key bắt buộc có giá trị; không in, không commit.
7. Docs: cập nhật AGENTS.md (§1 "Docker trên Windows" → macOS; §7 thay quy tắc
   PowerShell/-LiteralPath bằng quy tắc tương đương: kiểm absolute target nằm trong
   workspace trước rm -r/mv, không dùng glob chưa kiểm), plan.md P00/P12 (nền tảng và
   phần cứng thật đo được; ngân sách RAM/VRAM của T33 không tự đổi số — ghi phần cứng
   mới và hỏi tôi ngân sách mới nếu cần), README/RUNBOOK (quickstart, bootstrap, smoke,
   troubleshooting bằng lệnh macOS đã chạy thật; DESIGNED/IMPLEMENTED/VERIFIED đúng),
   tasks.md T29–T36 (chỉ chỗ nhắc nền tảng; không đổi DoD), agent-state.md (bỏ trạng
   thái cũ "dừng sau T07", ghi trạng thái hiện hành), task-session-prompt.md.
8. Kiểm chứng lại trên Mac bằng services thật, ghi command/cwd/exit/output thật đã che
   secrets vào handoffs:
   - uv sync --locked; Ruff, format check, mypy; scripts/check_docs.py.
   - Full unit/contract/security suite.
   - Integration suites dùng Docker thật (metadata, storage, registration, qdrant,
     ingestion, retrieval) và tests/e2e/test_public_api.py, test_streaming.py.
   - Bootstrap + smoke local bằng script mới; stack mặc định compose.yaml healthy.
   - Live provider smoke của T26 chạy MỘT lần mỗi provider (DeepSeek, Anthropic) với
     .env hiện có; lỗi credential thì báo, không thay bằng mock.
   - Corpus: setup_corpus.py --all và validate_corpus.py --all; checksum/manifest phải
     khớp bản pin (chứng minh tái tạo được trên Mac).
   Test hỏng do nền tảng thì sửa root cause; không skip/xfail/hạ assertion. Sau 3 lần
   không tiến triển trên cùng blocker thì dừng, ghi checkpoint và hỏi tôi.

Không được: sửa prompt corpus gốc, đổi model/provider/semantics, giảm security,
commit .env/.local/keys/model cache/corpus raw/scratch, force push, rewrite lịch sử.
Scratch T07 của máy Windows không tồn tại ở đây; không tạo lại.

Kết thúc: thêm current checkpoint đầu docs/handoffs.md và mục implementation-summary
"Platform migration macOS (2026-10-30)" gồm decisions/digest thay đổi/known limits.
Review diff/secrets/scope, stage đúng file, commit theo nhóm hợp lý với subject
"chore(macos): ..." / "docs(macos): ..."; tôi cho phép push lên origin/main sau khi kiểm
remote, không force push. Kiểm hash local = remote.

Báo cáo: phần cứng/OS/Docker thật, danh sách thay đổi, từng mục kiểm chứng PASS/FAIL/
BLOCKED kèm evidence, digest đã đổi, giới hạn còn lại (GPU, emulation, ngân sách T33),
commit/link GitHub, và T29 đã sẵn sàng bắt đầu trên Mac hay chưa. Dừng tại đó.
```

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
Thứ tự khuyến nghị: chạy session “Prompt chuyển dự án hoàn toàn sang macOS” trước, rồi mới
mở session T29 khi session migration báo T29 sẵn sàng.
T30–T36 vẫn TODO và nối tiếp tuần tự (T30 cần T29 COMPLETE, rồi T31 → … → T36),
nên chưa task nào trong số đó bắt đầu được trước khi T29 xong.
