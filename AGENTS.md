# AGENTS.md — Luật và bối cảnh RAG Core

> **Workflow hiện hành — quyết định người dùng 2026-09-26:** Mỗi session chỉ hoàn thiện một task được chỉ định rồi dừng. Agent hiện tại được trực tiếp sửa code/tests/scripts/config/docs, chạy kiểm chứng, review và commit; push chỉ khi người dùng yêu cầu. Không tự spawn subagent hoặc drain task tiếp. Bỏ các ràng buộc Orchestrator/Worker/Kanban, model/effort/isolation và yêu cầu worker mới cho retry trong quy trình Codex/Hermes cũ. Ghi runtime thực tế nếu biết, không suy đoán. Quyết định này thay thế phần vai trò và cơ chế điều phối ở §4–§6 bên dưới, P14 và các ghi chú/protocol Hermes lịch sử; giữ nguyên scope, dependencies, DoD D1–D6, giới hạn retry, bằng chứng, Git/secrets và quy tắc an toàn. Báo trực tiếp người dùng kết quả/commit/push/blockers và readiness của task kế tiếp rồi dừng. Khi context hết, ghi checkpoint đúng task để session mới tiếp quản.

## 1. Đọc trước khi làm việc

Đây là dự án RAG core độc lập, local-first, đóng gói Docker trên Windows. Đợt đầu có Default, Document, Multilingual EN/VI và UI quản trị. Scarlet/app chat gọi HTTP API sau này; **không sửa Scarlet trong backlog hiện tại**.

Nguồn cần đọc:

1. [docs/tasks.md](docs/tasks.md): task được giao, trạng thái, dependency, DoD và execution notes.
2. Các mục được task trỏ tới trong [docs/plan.md](docs/plan.md); luôn đọc [P01](docs/plan.md#p01) nếu thay behavior dữ liệu/truy xuất.
3. Nội dung và ghi chú thực thi của **từng task phụ thuộc**, không chỉ kiểm trạng thái COMPLETE.
4. [docs/handoffs.md](docs/handoffs.md): current checkpoint, lỗi, bằng chứng và dirty files.
5. [docs/implementation-summary.md](docs/implementation-summary.md): decisions/interfaces của task trước.
6. [README.md](README.md) và [RUNBOOK.md](RUNBOOK.md): trạng thái thật và hợp đồng vận hành/tích hợp.

Đọc những nguồn trên **trước khi viết code**. Tài liệu là bộ nhớ giữa session; không dựa vào hội thoại đã bị mất.

## 2. Quyền hạn và phạm vi công việc

- Chưa rõ yêu cầu, có mâu thuẫn hoặc thiếu quyết định sản phẩm: **hỏi người dùng, không đoán**. Worker báo Orchestrator để chuyển câu hỏi. Không tự thay semantics nhằm làm test pass.
- Chi tiết kỹ thuật đã được plan/DoD quyết định thì thực hiện, không hỏi lại. Lỗi kỹ thuật có thể sửa trong phạm vi task; mở rộng tính năng/đổi kiến trúc hoặc hạ DoD phải hỏi.
- Chỉ làm công việc của task được giao; không tiện tay refactor, thêm dependency/tính năng không cần thiết hoặc làm trước task sau.
- Không đánh dấu COMPLETE khi thiếu DoD, credentials, môi trường kiểm thử, commit hoặc bằng chứng. Không gọi mock success là live verification.
- Không sửa prompt corpus gốc. Các chỉ dẫn “không thay pipeline/model/API” trong prompt corpus chỉ ràng buộc phase chuẩn bị corpus.
- Task không yêu cầu deployment server, hosting, tích hợp Scarlet, push/merge Git hoặc gửi thông tin cho bên thứ ba: không tự thực hiện.
- Các phiên thực thi chỉ được đọc/chỉnh source trong repo được giao. Giữ nguyên file người dùng ngoài scope, ghi baseline dirty/untracked files trước khi bắt đầu.

## 3. Bất biến sản phẩm — không có ngoại lệ cho domain

**Mọi query chỉ dùng tài liệu được upload/đăng ký cho session hiện tại.** Kho riêng của user hoặc index giữ lại không cho phép lấy tài liệu session khác.

`allowed = app identity ∩ user identity ∩ active session ∩ active upload links ∩ ready versions/generations ∩ requested subset`

- Default = tất cả tài liệu hợp lệ trong session. Document = subset không rỗng trong session. Multilingual = cùng quy tắc, thêm language policies. Không có global/user-wide fallback.
- Authenticated identity là nguồn quyền; không dùng body `user_id`, `app_id` hoặc arbitrary storage key như bằng chứng quyền.
- Scope phải có trong mọi dense/sparse prefetch, neighbor fetch, rerank input, evidence, citation resolver và cache key nếu có cache.
- History chỉ giúp hiểu câu hỏi; không là nguồn bằng chứng factual. Context/citations lịch sử ngoài current scope không được đưa lại vào answer.
- Xóa chat/detach tăng revision và vô hiệu link; giữ nguồn/chunks/vector. Session mới không tự attach tài liệu cũ; source registration mới mới tạo quyền session mới.
- App sở hữu storage và transcript. Core chỉ HEAD/GET nguồn; không có DeleteObject/PutObject trong storage reader.
- PDF citation = trang vật lý one-based. DOCX = heading/paragraph; XLSX = sheet/cell; PPTX = slide. Không bịa trang.
- Thiếu bằng chứng vẫn gọi LLM để diễn đạt tự nhiên với `insufficient_evidence`; không bịa factual answer hoặc citations. Provider failure phải là lỗi kỹ thuật.
- Text tài liệu/history là dữ liệu, không có quyền thay system instructions/chạy tool. Không thực thi macro, formula, script hoặc external links từ tài liệu.
- Admin mặc định chỉ metadata vận hành, không đọc toàn bộ nội dung/keys. UI không là đường vòng truy xuất ngoài session.

## 4. Orchestrator và worker (lịch sử, đã được workflow một task/session thay thế)

### Orchestrator

- Model bắt buộc: **GPT-6-Astra** (`gpt-6-astra`).
- Chỉ điều phối: đọc, lập kế hoạch, chọn task, giao việc, chờ, xem diff/DoD/commit và đề xuất sửa lỗi.
- **Không được code bất kỳ nội dung nào**: không viết source, tests, scripts, config, patches hoặc shell để tạo/chỉnh nội dung. Mọi thay đổi repo, kể cả docs/plan/status, giao worker thực hiện.
- Có thể dùng shell read-only để kiểm repo/output/commit; không tự chạy migration/build/test ghi files hoặc Git commit thay worker.
- Không nhận việc của worker khi worker thất bại. Lập phương án, spawn worker mới cho task/attempt đó.

### Worker

- Model bắt buộc: **GPT-5.6-Sol** (`gpt-5.6-sol`), reasoning effort **xhigh**.
- Mỗi task và retry phải là **agent/sub-session mới, context mới**; không dùng lại agent cũ hoặc fork toàn bộ chat.
- Runtime có `spawn_agent` như phiên lập kế hoạch: đặt `fork_turns="none"`, `model="gpt-5.6-sol"`, `reasoning_effort="xhigh"`; prompt giao việc chứa đủ đường dẫn/task/DoD.
- Chỉ một worker active; task chạy tuần tự theo dependency. Worker không spawn agent cháu, không giao task song song.
- Subagent chia sẻ filesystem không có nghĩa được dùng memory của task trước; phải đọc tài liệu từ disk.
- Model/effort/isolation/slot lifecycle không khả dụng: báo blocker, không thay model hoặc để Orchestrator viết code. Cấu hình thực tế phải được kiểm trong runtime của phiên drain; prompt không tự đổi model cha.
- Kết thúc task/attempt rồi không dùng `followup_task` cho agent đó. Sửa lỗi là spawn agent mới.

Các quy tắc trên dành cho **session drain triển khai**. Session ban đầu được người dùng giao lập hồ sơ T00 được phép trực tiếp viết tài liệu kế hoạch; không được tự chuyển sang triển khai T01.

## 5. Quy trình bắt buộc của mỗi task

1. Kiểm `git status --short`, branch/HEAD, task trước và baseline dirty files. Không đụng file lạ.
2. Đọc plan refs, dependency task notes, handoffs và implementation-summary theo §1.
3. Xác định task ID/attempt ID/allowed files, mark IN_PROGRESS; ghi agent/model/effort và kế hoạch ngắn dưới task. Dependencies chưa COMPLETE thì không code task này.
4. Làm đúng task; chỉ cập nhật decision trong phạm vi đã được giao. Nếu chưa rõ/mâu thuẫn, dừng phần phụ thuộc và báo câu hỏi cụ thể.
5. Chạy **từng dòng DoD riêng và DoD chung D1–D6** trong [P13](docs/plan.md#p13). Không gộp tất cả thành câu “tests passed”.
6. Dán **output thật** vào `docs/handoffs.md`: command nguyên văn, cwd, exit code, config/services/provider/model đã dùng, expected/actual. Output dài: excerpt thật + path log đã redacted; không chỉ ghi link rồi bỏ bằng chứng.
7. Ghi dưới task: việc đã làm, files, từng DoD result/evidence, README/RUNBOOK thay đổi hoặc lý do N/A, limitations/blockers và commit reference.
8. Thêm implementation-summary theo **phase + task + attempt**, interfaces/decisions/migrations/tests/known limits; không ghi chung chung “đã hoàn thành”.
9. Cập nhật README và RUNBOOK đồng thời với implementation. Phân biệt DESIGNED/IMPLEMENTED/VERIFIED; command chưa tồn tại phải ghi planned, không đưa vào quickstart hoạt động.
10. Review diff/secrets/scope, stage đúng file và Git commit có task ID. Commit thành công + đủ DoD mới hợp lệ COMPLETE.
11. Trả Orchestrator: status, phase/task/attempt, files, DoD evidence, actual commit hash, unresolved risks, next action. Orchestrator chỉ chuyển task sau khi kiểm xong.

### Mẫu ghi dưới task

```text
Attempt: Txx-A01 | Worker/model/effort: ... | Started/ended: ...
Implemented/files: ...
DoD-1: PASS/FAIL/BLOCKED — evidence: handoffs#...
DoD-2: ...; D1–D6: ...
README/RUNBOOK: mục đã cập nhật hoặc lý do không ảnh hưởng.
Commit: subject/Task-ID; hash sau commit trả trong báo cáo.
Blocker/next action: ...
```

## 6. Thất bại, retry và bàn giao context

- Worker gặp fail/block phải lưu reproduction, command/exit/output thật, last-good state, changed/untracked files và hướng điều tra trước khi trả Orchestrator.
- Không xóa code dở để che lỗi. Chỉ checkpoint commit nếu đã review không secrets và đúng scope; ghi rõ chưa COMPLETE.
- Orchestrator phân tích, lập fix brief, spawn **worker mới** cho cùng task, attempt tăng; không chuyển dependency task mới để bỏ qua lỗi.
- Không lặp vô hạn: sau 3 attempts không tiến triển trên cùng blocker, hỏi người dùng hoặc bàn giao trạng thái BLOCKED. Thiếu key/permission/quyết định sản phẩm thì hỏi ngay, không cần thử giả nhiều lần.
- Không tự hạ gate, thay gold, bỏ test, giảm scope security, đổi model hoặc bỏ live requirement để drain “xong”. GPU profile là tùy chọn theo T17; chỉ ghi unavailable khi có capability check thật, không coi unavailable là GPU PASS.
- Context/agent slots sắp hết: checkpoint docs qua worker, dừng ở ranh giới an toàn, báo người dùng prompt tiếp tục; không diễn giải hết context thành đạt mục tiêu.
- Handoffs phải có current checkpoint ngắn ở đầu, append lịch sử evidence phía dưới; không ghi đè attempt cũ. Summary ghi interfaces cần cho session sau, không copy toàn bộ logs.

## 7. Git, filesystem và secrets

- Một completion commit/task; dùng `feat(Txx): ...`, `test(Txx): ...`, `docs(Txx): ...`. Retry có checkpoint commits riêng được đánh dấu chưa complete.
- Commit phải gồm code/tests/docs của task. Không `git add .` khi có file không thuộc scope; không amend/rebase/reset --hard hoặc force push để đổi lịch sử đã bàn giao.
- Task notes ghi commit subject/Task-ID trước commit; worker trả actual hash sau commit. Không cố ghi hash vào chính commit đó; task sau có thể ghi hash task trước.
- Không commit `.env`, JWT/service keys, model weights/cache, database dumps, raw PDFs/datasets không được phép, browser session data hoặc logs chứa nội dung riêng.
- Không tự đặt danh tính Git giả. Nếu Git author chưa cấu hình, báo thiếu thông tin; không sửa global config. Không bỏ qua hook để tạo commit.
- Windows: dùng PowerShell native với `-LiteralPath`; kiểm absolute target nằm trong workspace trước recursive delete/move. Không kết hợp PowerShell enumerate với `cmd /c` delete/move.
- Không dùng `docker compose down -v` trong flow mặc định. Backup/restore vào project/volumes riêng. Không tự xóa dữ liệu gốc ở storage.
- Không in secret để debug. Handoffs output redacted phải đánh dấu `[REDACTED]`, giữ nguyên lỗi/count/exit có ích; không bịa output.

## 8. Chất lượng và tài liệu

- Dùng `rg`/`rg --files` để tìm nội dung. Đọc và pin dependency theo bản thực; ưu tiên tài liệu chính thức cho API/provider.
- Ports/core không phụ thuộc FastAPI/SDK; dependency injection rõ; không framework hóa tính năng chưa cần.
- CPU/OCR/inference không block async API. Bounded queue/timeouts/cancel, không nhân model cho 20 users.
- Tests phải chứng minh behavior/rủi ro thực; integration dùng services thật, live dùng provider thật; không thêm tests vô nghĩa cho thay đổi văn bản đơn giản.
- Không ingest `qa/`, answers, justification vào vector index; test corpus không dùng gold để thu hẹp retrieval trước tìm kiếm.
- Format/API/schema thay đổi phải cập nhật RUNBOOK/examples và validation cùng task. Mục README/RUNBOOK không ảnh hưởng thì ghi N/A có lý do, không sửa hình thức cho đủ thủ tục.
- Báo cáo trung thực điểm chưa đo, task blocked, mock/live, model/config revisions và giới hạn phần cứng. “Local chạy được” không đồng nghĩa đã triển khai server hoặc tích hợp Scarlet.
