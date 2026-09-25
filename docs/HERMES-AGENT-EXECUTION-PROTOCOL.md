# HERMES AGENT EXECUTION PROTOCOL

> **Mục đích:** Đây là đặc tả chuẩn, dùng lại cho mọi dự án triển khai bằng Hermes Agent theo mô hình **Orchestrator + Worker + Reviewer**, với chiến lược **drain-tasks**.
>
> File này mô tả **cách thực thi kế hoạch**, không thay thế `plan.md` hoặc `tasks.md`.
>
> Trong mọi trường hợp, **người sở hữu dự án là người quyết định cuối cùng**. Agent không được tự mở rộng phạm vi sản phẩm hoặc tự thay đổi quyết định gốc của người dùng.

---

## 0. Phạm vi và thuật ngữ chuẩn

### 0.1. Ba profile duy nhất

Workflow chỉ sử dụng ba profile:

| Profile | Vai trò |
|---|---|
| **Orchestrator** | Session chính. Đọc kế hoạch, điều phối Kanban, giao task, kiểm chứng DoD, cập nhật tài liệu quản trị, quyết định task tiếp theo |
| **Worker** | Session cô lập. Thực hiện đúng **một task**: code / config / migration / test / fix theo assignment; tự chạy validation và trả evidence |
| **Reviewer** | Session cô lập. Review **toàn phase** sau khi phase hoàn thành; final cross-phase review; khi cần, phân tích các phase xa còn sơ lược và đề xuất cách mở rộng |

Không sử dụng các profile riêng kiểu `Coder`, `Tester`, `Fixer`.

Worker là profile generic. Loại công việc được thể hiện bằng **job label**, ví dụ `[Code]`, `[Fix]`, `[Experiment]`, không phải bằng profile khác nhau.

### 0.2. Thuật ngữ Kanban

- **Board**: Kanban Board của một lần drain-tasks.
- **Task/Card**: một card bên trong Board.
- Không gọi Task/Card là “board nhỏ”.
- Mỗi Worker invocation gắn với **một Task/Card duy nhất**.
- Mỗi Worker invocation là một **session/context mới**.

### 0.3. Từ khóa quy phạm

- **MUST / PHẢI**: bắt buộc.
- **MUST NOT / KHÔNG ĐƯỢC**: cấm.
- **SHOULD / NÊN**: mặc định nên làm; chỉ khác khi có lý do rõ ràng.
- **MAY / CÓ THỂ**: tùy tình huống.

---

# 1. Nguyên tắc nền tảng

## 1.1. Plan-driven, không ad-hoc

Orchestrator PHẢI triển khai dựa trên:

```text
docs/plan.md
docs/tasks.md
```

Orchestrator không tự nghĩ ra roadmap mới trong lúc code.

Nếu repo dùng `KE-HOACH.md` thay cho `plan.md`, có thể map tương đương, nhưng trong protocol này tên chuẩn là `plan.md`.

## 1.2. Drain-tasks

Sau khi bắt đầu workflow, Orchestrator PHẢI tiếp tục điều phối các task đủ điều kiện cho tới khi:

1. toàn bộ task hiện tại đã hoàn tất;
2. workflow gặp Human Task / hard blocker cần người quyết định;
3. Worker gặp failure loại cần human escalation;
4. Reviewer yêu cầu quyết định kiến trúc/scope từ người;
5. toàn bộ roadmap khả dụng đã drain xong và final review hoàn tất.

Orchestrator KHÔNG ĐƯỢC dừng chỉ vì một Worker đang chạy.

Khi không có hành động điều phối ngay lập tức, Orchestrator phải chờ/sleep/poll theo cơ chế Hermes phù hợp và tiếp tục khi Worker trả kết quả.

## 1.3. Một Worker = một task = một lượt sống

Mặc định:

```text
1 Worker invocation
= 1 Hermes Task/Card
= 1 task trong tasks.md
= 1 execution session
= 1 lần trả kết quả
```

Worker KHÔNG ĐƯỢC implement cả phase trong một invocation.

Sau khi Worker đã trả kết quả, session Worker đó được coi là **terminal**.

**Tuyệt đối không resume, recall hoặc giao việc lần hai cho Worker cũ.**

Nếu cần sửa, kiểm tra lại hoặc tiếp tục:

```text
tạo Task/Card mới
→ dispatch Worker mới
→ context mới
```

## 1.4. Just-in-time Kanban

Khi bắt đầu một lần drain-tasks, Orchestrator:

1. tạo **một Board mới hoàn toàn**;
2. Board ban đầu PHẢI trống;
3. KHÔNG tạo trước toàn bộ card từ `tasks.md`;
4. chỉ tạo card ngay trước khi thực sự giao việc.

Mục tiêu là tránh:

- board phình to;
- trạng thái Kanban lệch khỏi trạng thái thực tế;
- khóa cứng roadmap chưa đủ thông tin;
- tràn context điều phối.

## 1.5. Orchestrator không code

Orchestrator:

- KHÔNG sửa source code;
- KHÔNG implement feature;
- KHÔNG fix bug trực tiếp;
- KHÔNG tự “tiện tay” làm task thay Worker.

Orchestrator chỉ:

- đọc;
- phân tích;
- điều phối;
- kiểm chứng evidence;
- quản lý trạng thái;
- quản lý tài liệu trong `docs/`;
- quản lý Kanban;
- quyết định bước tiếp theo.

## 1.6. Reviewer không implement

Reviewer:

- đọc code;
- đọc diff;
- đọc evidence;
- có thể chạy các kiểm tra read-only / test cần thiết để review;
- phân tích kiến trúc;
- phân tích security / regression / maintainability;
- đề xuất task sửa;
- đề xuất cách mở rộng phase tương lai.

Reviewer KHÔNG sửa source code và KHÔNG sửa trực tiếp file trong `docs/`.

---

# 2. Cấu trúc tài liệu chuẩn trong `docs/`

Một dự án dùng protocol này NÊN có tối thiểu:

```text
docs/
├── plan.md
├── tasks.md
├── agent-state.md
├── handoffs.md
├── implementation-summary.md
├── review-report.md
└── HERMES-AGENT-EXECUTION-PROTOCOL.md
```

Có thể đặt thêm:

```text
docs/META-LAP-KE-HOACH.md
```

để làm chuẩn cho việc lập `plan.md` và `tasks.md`.

## 2.1. Quyền ghi file

### Orchestrator

**Là agent duy nhất được phép chỉnh sửa file bên trong `docs/`.**

Bao gồm:

- `plan.md`
- `tasks.md`
- `agent-state.md`
- `handoffs.md`
- `implementation-summary.md`
- `review-report.md`
- các file quản trị khác trong `docs/`

### Worker

Worker:

- được đọc `docs/`;
- KHÔNG được sửa bất kỳ file nào trong `docs/`;
- được sửa source/config/migration/test files nằm ngoài `docs/` nếu task yêu cầu.

### Reviewer

Reviewer:

- được đọc `docs/`;
- KHÔNG được sửa `docs/`;
- KHÔNG được sửa source code.

Reviewer trả structured output cho Orchestrator; Orchestrator mới là bên ghi kết quả vào `docs/`.

## 2.2. Không sửa nội dung gốc của kế hoạch

Sau khi implementation bắt đầu:

- Orchestrator có thể **append**, annotate, mark status, thêm evidence, thêm Backlog, mở rộng phần roadmap chưa chi tiết.
- Orchestrator **KHÔNG ĐƯỢC âm thầm viết lại/xóa quyết định gốc** của người dùng trong `plan.md` hoặc `tasks.md`.
- Nếu quyết định gốc thật sự cần thay đổi, phải ghi rõ:
  - lý do;
  - tác động;
  - quyết định của người;
  - phần cũ được supersede bởi phần nào.

---

# 3. Quy tắc `tasks.md`

`tasks.md` là execution queue chuẩn.

## 3.1. Một task chuẩn

Mỗi task chi tiết PHẢI có:

1. Trạng thái
2. Phụ thuộc
3. Ước lượng
4. Tham chiếu `plan.md`
5. Việc cần làm
6. Xong khi / DoD
7. Cạm bẫy, nếu thực tế có

Ví dụ:

```markdown
### T-1.3 — JWT authentication
- **Trạng thái:** ☐
- **Phụ thuộc:** T-1.1
- **Ước lượng:** 3h
- **Plan:** §6.2, §8.1
- **Việc:**
  - [ ] ...
- **Xong khi (DoD):**
  - [ ] <command hoặc observable behavior>
- **Cạm bẫy:**
  - ...
```

## 3.2. Kích thước task

Mặc định một task nên nằm trong khoảng:

```text
1–4 giờ
```

Task lớn hơn một buổi NÊN được tách trước khi dispatch.

Worker chỉ nhận đúng một task.

## 3.3. DoD bắt buộc kiểm chứng được

DoD PHẢI là:

- lệnh chạy được; hoặc
- hành vi quan sát được; hoặc
- assertion có thể PASS/FAIL rõ ràng.

Không dùng:

```text
"hoạt động đúng"
"đã test kỹ"
"xử lý lỗi tốt"
"code sạch"
"ổn định"
```

Một DoD tốt phải trả lời được:

> **DoD này có thể FAIL không?**

Nếu câu trả lời là “không”, DoD đó không có giá trị kiểm chứng và phải viết lại.

## 3.4. Progressive elaboration

Không chi tiết toàn bộ roadmap từ ngày đầu.

Mức chi tiết chuẩn:

| Khoảng roadmap | Mức chi tiết |
|---|---|
| Phase gần / khoảng 1/3 đầu | task đầy đủ |
| Phase trung gian | bảng tóm tắt |
| Phase xa | bullet / intention level |

Reviewer được dùng để review những gì đã học từ các phase trước và đề xuất cách mở rộng phase xa trước khi bắt đầu phase đó.

---

# 4. Board lifecycle

## 4.1. Tạo Board

Mỗi lần bắt đầu một workflow drain-tasks mới, Orchestrator PHẢI tạo Board mới.

Tên chuẩn:

```text
YYYY-MM-DD-HHmm-<project>-<feature>-drain
```

Ví dụ:

```text
2026-09-21-1800-scarlet-github-integration-drain
```

Quy tắc:

- lowercase;
- dùng dấu `-`;
- tên đủ ngắn để đọc được;
- có project;
- có feature/workstream;
- có timestamp.

## 4.2. Board ban đầu phải trống

Ngay sau khi tạo:

```text
Board = tồn tại
Cards = 0
```

Không pre-populate toàn bộ `tasks.md`.

## 4.3. Tạo card Just-in-Time

Card chỉ được tạo khi:

- dependency đã thỏa;
- task thực sự sắp dispatch;
- Orchestrator đã chuẩn bị instruction cho Worker/Reviewer.

## 4.4. Đóng Board

Board chỉ được đóng sau khi:

- toàn bộ task thuộc phạm vi drain hiện tại đã hoàn tất;
- mọi phase review bắt buộc đã PASS;
- final cross-phase review đã hoàn tất;
- không còn blocker chưa ghi nhận;
- `agent-state.md` phản ánh trạng thái cuối;
- `tasks.md` phản ánh trạng thái cuối.

---

# 5. Quy ước Task/Card

Hermes có thể hiển thị dạng:

```text
task-id | status | assignee | title
```

Ví dụ:

```text
t_1234abcd  done  worker    [Code] JWT Authentication
t_abcd1234  done  worker    [Fix] JWT Authentication errors
```

Phần do Orchestrator đặt là **title**, ví dụ:

```text
[Code] T-1.3 JWT Authentication
[Fix] T-1.3 JWT Authentication — DoD failure
[Review] Phase 1 — Authentication Foundation
[Review] Final Cross-Phase Review
```

Không nhét status, worker name hoặc Hermes task ID vào title.

## 5.1. Job labels chuẩn

Tối thiểu:

```text
[Code]
[Fix]
[Review]
[Experiment]
```

Có thể thêm label khi project cần, nhưng label không tạo ra profile mới.

---

# 6. Context isolation

## 6.1. Session chính

Orchestrator luôn ở Session chính.

Session chính giữ:

- trạng thái workflow;
- quyết định của người;
- Kanban;
- dependency;
- DoD acceptance;
- Human Task;
- phase transition.

## 6.2. Worker session

Mỗi Worker chạy trong context riêng.

Worker không được giả định rằng nó biết các Worker trước đã làm gì.

Instruction của Orchestrator PHẢI cung cấp đủ context task-specific và yêu cầu Worker đọc các nguồn persistent cần thiết.

## 6.3. Persistent context

Nguồn context bền vững:

```text
plan.md
tasks.md
agent-state.md
handoffs.md
implementation-summary.md
review-report.md
Git history / diff / current codebase
```

Worker và Reviewer dùng các file này để hiểu trạng thái.

Tuy nhiên, vì `docs/` là write-protected đối với Worker/Reviewer, mọi cập nhật phải quay về Orchestrator.

---

# 7. Luồng thực thi một task

Luồng mặc định:

```text
Orchestrator
    │
    ├─ đọc plan.md + tasks.md + state
    │
    ├─ chọn task tiếp theo đủ dependency
    │
    ├─ tạo Kanban card JIT
    │
    ├─ dispatch Worker mới
    │
    ▼
Worker
    │
    ├─ đọc task + context
    ├─ kiểm tra Git state
    ├─ implement đúng scope
    ├─ chạy targeted tests / validation
    ├─ kiểm tra DoD
    ├─ trả structured handoff
    ▼
Orchestrator
    │
    ├─ đọc output + evidence
    ├─ tự kiểm chứng DoD ở mức điều phối
    ├─ cập nhật docs
    │
    ├─ PASS ───────────────► task kế tiếp
    │
    ├─ implementation lỗi ─► Worker mới [Fix]
    │
    └─ hard blocker ───────► Human decision
```

---

# 8. Worker assignment contract

Mỗi assignment cho Worker PHẢI chứa tối thiểu:

```text
Task ID
Phase
Job type
Goal
Exact scope
Dependencies already satisfied
Relevant plan.md sections
Relevant tasks.md section
Expected files/modules
DoD
Guardrails
Git rules
Required validation
Required output schema
```

Orchestrator KHÔNG được gửi prompt kiểu:

```text
"Implement task T-1.3"
```

mà thiếu DoD và scope.

---

# 9. Worker rules

Worker PHẢI:

1. chỉ làm task được giao;
2. đọc đúng context cần thiết;
3. không sửa `docs/`;
4. không mở rộng scope;
5. giữ behavior ngoài scope nếu task không yêu cầu thay đổi;
6. chạy validation phù hợp;
7. cung cấp evidence;
8. báo mọi phát hiện ngoài scope dưới dạng **Backlog Candidate**;
9. không tự thêm Backlog vào `tasks.md`;
10. không tự mark task done trong `tasks.md`;
11. không tự sửa plan;
12. không gọi Worker khác;
13. không chờ được gọi lại;
14. kết thúc bằng structured handoff chuẩn.

---

# 10. Structured Worker Handoff — BẮT BUỘC

Worker phải kết thúc bằng format sau.

```markdown
# WORKER HANDOFF

## Identity
- Task ID:
- Phase:
- Job:
- Result: PASS | FAIL | BLOCKED
- Base Git SHA:
- End Git SHA: <nếu có commit>
- Worker session/task:

## Scope Executed
- ...

## Changes
- ...

## Files Changed
- `path/to/file`
- `path/to/file`

## Commands Run
1. `...`
2. `...`

## Test / Validation Results
| Check | Result | Evidence |
|---|---|---|
| ... | PASS/FAIL | ... |

## DoD Evidence
| DoD item | Result | Evidence |
|---|---|---|
| DoD-1 | PASS/FAIL | command/output/behavior |
| DoD-2 | PASS/FAIL | ... |

## Git State
- Start:
- End:
- Uncommitted changes:
- Commit(s), if any:

## Issues / Blockers
- ...

## Backlog Candidates
- <chỉ những việc nằm ngoài scope task hiện tại>

## Risks
- ...

## Suggested Next Action
- ...
```

Nếu không có nội dung ở một mục, ghi:

```text
None
```

Không bỏ mục.

---

# 11. Orchestrator DoD verification

Worker tự chạy test, nhưng **Worker không có quyền quyết định cuối cùng rằng task đã hoàn thành**.

Orchestrator là bên accept/reject task.

## 11.1. Điều kiện accept task

Task chỉ được mark `✅` khi:

- Worker trả `PASS`;
- mọi DoD bắt buộc có evidence;
- evidence phù hợp với acceptance criteria;
- không có blocker unresolved;
- Git state không cho thấy thay đổi ngoài scope đáng ngờ;
- dependency/integration không bị phá rõ ràng;
- Orchestrator không phát hiện contradiction giữa output và code/diff.

## 11.2. Không có evidence = chưa hoàn thành

Các câu như:

```text
"should work"
"looks correct"
"implemented successfully"
"tests should pass"
```

không được coi là evidence.

---

# 12. Failure taxonomy

Để tránh retry vô hạn, Orchestrator phân failure thành hai loại.

## 12.1. Implementation Defect

Ví dụ:

- test đỏ;
- DoD không đạt;
- bug rõ ràng;
- thiếu case trong scope;
- Reviewer phát hiện defect có cách sửa cụ thể.

Xử lý:

```text
không resume Worker cũ
→ tạo card mới
→ [Fix] <task name>
→ dispatch Worker mới
```

Worker Fix cũng chỉ sống một lượt.

## 12.2. Execution / Hard Blocker

Ví dụ:

- thiếu quyết định sản phẩm;
- thiếu credential/human action;
- môi trường hỏng không xác định;
- spec mâu thuẫn;
- dependency ngoài repo không khả dụng;
- Worker không thể hoàn thành task mà không thay đổi scope lớn;
- failure lặp lại khiến phương án hiện tại đáng nghi.

Xử lý:

```text
Worker → Orchestrator
Orchestrator đánh giá
→ ghi blocker
→ hỏi người quyết định
```

Không auto-spawn Worker vô hạn.

---

# 13. Backlog policy

Worker tuyệt đối không tự triển khai việc ngoài scope.

Nếu phát hiện việc cần làm ngoài kế hoạch:

```text
Worker
→ Backlog Candidates trong handoff
→ Orchestrator đánh giá
→ Orchestrator append vào Backlog trong tasks.md
```

## 13.1. Append-only

Orchestrator:

- được thêm Backlog;
- được thêm dependency tới Backlog mới;
- được annotate lý do phát sinh;
- không được âm thầm sửa/xóa nội dung task gốc.

## 13.2. Task phụ thuộc Backlog

Nếu Task B cần Backlog B-1 mới có thể thực hiện:

```text
B-1 chưa xong
→ B bị blocked
→ không dispatch B
```

Orchestrator phải drain B-1 trước nếu đã đủ thông tin.

---

# 14. Human Tasks — `T-H<N>`

`tasks.md` PHẢI có mục riêng cho những việc chỉ người có thể làm.

Ví dụ:

```markdown
### T-H1 — Obtain Cloudflare Site Key
- **Trạng thái:** ☐
- **Chặn:** T-2.4, T-2.5
- **Người cần thực hiện:**
  - đăng nhập Cloudflare
  - tạo Turnstile Site Key
  - đặt secret vào `.env`
- **Xong khi:**
  - application nhận được config cần thiết mà không có secret trong Git/docs
```

## 14.1. Khi gặp T-H

Orchestrator:

1. xác định task nào bị chặn;
2. không dispatch task phụ thuộc;
3. yêu cầu người hoàn thành `T-H<N>`;
4. nêu rõ cần trả lại **kết quả gì**, không chỉ nói “hãy làm việc này”;
5. tiếp tục các task độc lập nếu dependency cho phép;
6. nếu không còn task độc lập, workflow chuyển sang chờ Human;
7. sau khi người submit kết quả, Orchestrator kiểm tra điều kiện hoàn tất;
8. mark `T-H<N>` done;
9. tiếp tục drain.

## 14.2. Secrets

Secret như:

- API key;
- password;
- private token;
- signing secret;
- cloud credential;

KHÔNG được ghi vào:

- `plan.md`;
- `tasks.md`;
- `handoffs.md`;
- `agent-state.md`;
- `implementation-summary.md`;
- `review-report.md`;
- Kanban card/comment;
- Git commit.

Nếu phù hợp, secret được đặt trực tiếp vào:

```text
.env
secret store
deployment environment
CI/CD secret manager
provider secret manager
```

Docs chỉ ghi **tên biến** hoặc placeholder.

---

# 15. Parallel execution

Orchestrator CÓ THỂ dispatch Worker song song nếu và chỉ nếu các task:

- không phụ thuộc nhau;
- không sửa cùng logical unit theo cách có nguy cơ conflict;
- không cần output của nhau;
- có thể validate độc lập.

Ví dụ:

```text
T-2.1 frontend component
T-2.2 backend endpoint
```

có thể chạy song song nếu contract đã chốt và không có dependency.

Không parallelize chỉ để nhanh nếu điều đó làm tăng nguy cơ conflict.

Khi song song, mỗi Worker vẫn tuân thủ:

```text
1 Worker = 1 task
```

---

# 16. Phase lifecycle

Một phase có trạng thái tổng quát:

```text
NOT_STARTED
→ IN_PROGRESS
→ TASKS_COMPLETE
→ UNDER_REVIEW
→ PASSED
```

Nếu review thất bại:

```text
UNDER_REVIEW
→ FIX_REQUIRED
→ Worker [Fix]
→ TASKS_COMPLETE
→ Reviewer mới
```

Không resume Reviewer cũ nếu cần một lượt review mới. Mỗi review invocation cũng là session độc lập.

---

# 17. Phase Review

Sau khi tất cả task trong một phase được Orchestrator accept:

```text
Orchestrator
→ tạo card [Review] Phase N
→ dispatch Reviewer mới
```

Reviewer review **toàn phase**, không review từng task nhỏ một.

## 17.1. Reviewer phải kiểm tra

Tùy loại dự án, tối thiểu:

- task/DoD coverage;
- correctness;
- architecture consistency;
- regression risk;
- security;
- backward compatibility;
- test evidence;
- maintainability;
- Git diff/commit consistency;
- scope compliance;
- unresolved TODO/blocker;
- docs-vs-code consistency theo evidence Orchestrator cung cấp.

---

# 18. Structured Reviewer Handoff — BẮT BUỘC

```markdown
# REVIEWER HANDOFF

## Identity
- Review Type: PHASE | FINAL | PHASE-EXPANSION
- Phase:
- Result: PASS | FAIL | NEEDS_HUMAN_DECISION

## Scope Reviewed
- Tasks:
- Commits / Diff:
- Modules:

## Acceptance Review
| Area | Result | Evidence / Note |
|---|---|---|
| DoD coverage | PASS/FAIL | ... |
| Correctness | PASS/FAIL | ... |
| Architecture | PASS/FAIL | ... |
| Security | PASS/FAIL | ... |
| Regression | PASS/FAIL | ... |
| Test evidence | PASS/FAIL | ... |

## Blocking Issues
- ...

## Non-Blocking Recommendations
- ...

## Backlog Candidates
- ...

## Phase Expansion Proposal
- <chỉ dùng khi review chuẩn bị phase chưa chi tiết>

## Risks
- ...

## Suggested Next Action
- ...
```

Reviewer KHÔNG sửa `review-report.md`.

Orchestrator nhận handoff rồi mới cập nhật `review-report.md`.

---

# 19. Mở rộng phase chưa chi tiết

Roadmap xa cố ý không chi tiết sớm.

Trước khi bắt đầu một phase đang ở dạng bảng/bullet:

```text
Orchestrator
→ gọi Reviewer với job PHASE-EXPANSION
```

Reviewer phải đọc:

- `plan.md`;
- `tasks.md`;
- các phase đã hoàn thành;
- `implementation-summary.md`;
- `handoffs.md`;
- `review-report.md`;
- codebase hiện tại;
- Git history liên quan.

Reviewer đề xuất:

- task decomposition;
- dependency mới;
- DoD kiểm chứng được;
- cạm bẫy dựa trên lỗi thật đã gặp;
- estimate điều chỉnh theo tốc độ thực tế;
- assumption chưa đủ thông tin;
- Human Task mới nếu có.

## 19.1. Reviewer chỉ đề xuất

Reviewer không ghi file.

Orchestrator:

1. đánh giá proposal;
2. đảm bảo không thay đổi quyết định gốc trái phép;
3. append/mở rộng phase trong `tasks.md`;
4. khi cần, annotate `plan.md`;
5. chỉ sau đó mới bắt đầu dispatch Worker.

---

# 20. `agent-state.md`

Chỉ Orchestrator cập nhật.

Tối thiểu ghi:

```markdown
# Agent State

- Board:
- Current phase:
- Phase status:
- Current task(s):
- Running Hermes cards:
- Last accepted task:
- Last reviewer result:
- Human blockers:
- Technical blockers:
- Backlog blockers:
- Git baseline:
- Next action:
- Updated at:
```

File này là trạng thái điều phối hiện tại, không phải nhật ký dài.

---

# 21. `handoffs.md`

Chỉ Orchestrator ghi.

Mỗi Worker/Reviewer hoàn tất, Orchestrator append một entry.

Mẫu:

```markdown
## <timestamp> — <agent type> — <Task/Card>

- From:
- To:
- Phase:
- Task:
- Result:
- Files changed:
- Tests/validation:
- DoD:
- Git SHA / diff:
- Blockers:
- Backlog candidates:
- Risks:
- Exact next action:
```

Không ghi secret.

---

# 22. `implementation-summary.md`

Chỉ Orchestrator ghi dựa trên accepted Worker handoff.

Nên tổ chức theo phase:

```markdown
# Implementation Summary

## Phase N — <name>

### Accepted Tasks
- T-N.1
- T-N.2

### Product Changes
- ...

### Config / Schema / Migration Changes
- ...

### API / Contract Changes
- ...

### Tests Added / Changed
- ...

### Git
- ...

### Known Limitations
- ...

### Deferred Backlog
- ...
```

Chỉ ghi implementation đã được accept.

Không ghi một thay đổi failed như thể nó đã hoàn tất.

---

# 23. `review-report.md`

Chỉ Orchestrator ghi từ Reviewer handoff.

Mẫu:

```markdown
# Review Report

## Phase N Review
- Status:
- Reviewer card:
- Architecture:
- Correctness:
- Security:
- Regression:
- Test evidence:
- Blocking issues:
- Non-blocking recommendations:
- Backlog:
- Decision:
```

Final review phải có section riêng.

---

# 24. Git protocol — BẮT BUỘC

Mọi Worker làm code phải quản lý Git có chủ đích.

## 24.1. Preflight

Trước khi sửa code, Worker phải ghi nhận tối thiểu:

```bash
git status --short
git rev-parse HEAD
git branch --show-current
```

Nếu working tree có thay đổi không thuộc task:

- không được xóa;
- không được overwrite;
- không được reset;
- phải báo trong handoff nếu ảnh hưởng task.

## 24.2. Cấm destructive Git

Worker KHÔNG ĐƯỢC tự ý dùng các thao tác phá hủy như:

```text
git reset --hard
git clean -fd
force push
xóa branch chứa work chưa merge
checkout đè thay đổi người khác
```

trừ khi người dùng đã ra lệnh rõ ràng cho đúng trường hợp đó.

## 24.3. Task-scoped changes

Diff phải nằm trong scope task.

Nếu thấy cần sửa ngoài scope:

```text
không sửa
→ Backlog Candidate
```

trừ khi đó là thay đổi tối thiểu bắt buộc để task build/test được; khi đó Worker phải giải thích rõ trong handoff.

## 24.4. Commit policy

Protocol này không bắt buộc mọi repo phải dùng cùng một branching model.

Tuy nhiên:

- Worker phải báo Base SHA;
- phải báo End SHA;
- phải báo working tree status;
- nếu Worker tạo commit, commit phải task-scoped;
- nếu repo/project có convention commit riêng, Worker phải tuân theo;
- Orchestrator phải lưu accepted SHA/diff trong handoff/state khi cần.

Không được tạo một commit chứa nhiều task độc lập.

## 24.5. Integration conflict

Nếu các Worker song song tạo conflict:

- Orchestrator không tự sửa conflict trong source;
- tạo Worker mới với job `[Fix]` hoặc `[Integration]`;
- Worker mới giải quyết conflict theo task riêng và chạy validation lại.

---

# 25. Orchestrator documentation transaction

Sau mỗi Worker PASS được accept, Orchestrator cập nhật theo thứ tự:

```text
1. tasks.md
2. implementation-summary.md
3. handoffs.md
4. agent-state.md
```

Sau Reviewer:

```text
1. review-report.md
2. handoffs.md
3. agent-state.md
4. tasks.md / plan.md nếu có phase expansion hoặc backlog hợp lệ
```

Mục tiêu là docs luôn phản ánh state đã accept, không phản ánh state agent “nói là xong” nhưng chưa được kiểm chứng.

---

# 26. Task state policy

Trạng thái chuẩn trong `tasks.md`:

```text
☐  chưa làm
🔄 đang làm
🚧 BLOCKED
✅ xong
⏭️ bỏ qua
```

Chỉ Orchestrator được đổi trạng thái.

## 26.1. Khi dispatch

```text
☐ → 🔄
```

## 26.2. Khi Worker PASS và Orchestrator accept

```text
🔄 → ✅
```

## 26.3. Khi blocked

```text
🔄 → 🚧 BLOCKED
```

Phải ghi:

- blocker;
- ai cần quyết định;
- task nào bị ảnh hưởng;
- điều kiện unblock.

## 26.4. Skip

`⏭️` chỉ dùng khi có quyết định rõ từ người hoặc ADR/decision tương đương.

Không skip để “drain cho hết”.

---

# 27. Reviewer failure handling

Nếu Reviewer phát hiện blocking implementation defect:

```text
Reviewer FAIL
→ Orchestrator ghi finding
→ tạo [Fix] card mới
→ Worker mới
→ Worker test
→ Orchestrator verify
→ Reviewer mới review lại phase
```

Không gọi lại Reviewer cũ.

Nếu Reviewer phát hiện vấn đề cần thay đổi architecture/scope/decision:

```text
Reviewer NEEDS_HUMAN_DECISION
→ Orchestrator ghi blocker
→ hỏi người
→ cập nhật plan/tasks theo quyết định
→ tiếp tục
```

---

# 28. Final Cross-Phase Review

Sau khi tất cả phase trong phạm vi hiện tại PASS:

```text
Orchestrator
→ [Review] Final Cross-Phase Review
→ Reviewer mới
```

Reviewer phải review toàn bộ hệ thống, không chỉ phase cuối.

Tối thiểu kiểm tra:

- toàn bộ task đã được xử lý đúng trạng thái;
- dependency giữa phase;
- integration;
- architecture consistency;
- security;
- backward compatibility;
- regression;
- test coverage/evidence;
- unresolved TODO;
- backlog chưa được biến nhầm thành feature đã hoàn thành;
- docs consistency;
- deploy/runtime implications;
- rollback concerns;
- Git history/diff sanity.

Final Reviewer trả:

```text
PASS
FAIL
NEEDS_HUMAN_DECISION
```

Workflow chỉ được coi là hoàn tất khi final review không còn blocker chưa xử lý.

---

# 29. Human authority

Người dùng giữ quyền quyết định đối với:

- scope;
- architecture change quan trọng;
- provider/service;
- budget;
- secret/account;
- chấp nhận trade-off;
- bỏ task;
- thay roadmap;
- retry sau hard blocker;
- quyết định khi Worker failure không còn là bug sửa đơn giản.

Agent không được “đoán thay”.

---

# 30. Không tự sửa kế hoạch gốc

Nếu implementation thực tế cho thấy kế hoạch thiếu việc:

```text
Worker → Backlog Candidate
Reviewer → Finding/Proposal
Orchestrator → append Backlog / annotation
```

Không được:

```text
xóa requirement gốc
đổi acceptance criteria để biến test đỏ thành xanh
thu hẹp DoD chỉ để mark complete
viết lại lịch sử như thể quyết định mới luôn tồn tại
```

---

# 31. Dependency-first scheduling

Orchestrator chọn task tiếp theo theo thứ tự:

1. dependency satisfied;
2. không bị Human Task block;
3. phase hiện tại;
4. rủi ro/phụ thuộc theo `tasks.md`;
5. parallel-safe nếu chạy song song.

Không chạy task tương lai chỉ vì Worker đang rảnh nếu dependency/phase logic chưa cho phép.

---

# 32. Orchestrator main loop

Pseudo-protocol:

```text
CREATE fresh empty board

LOAD:
  plan.md
  tasks.md
  agent-state.md
  handoffs.md
  implementation-summary.md
  review-report.md

WHILE workflow not finished:

  if human decision/blocker exists:
      run independent ready tasks if safe
      otherwise ask human and wait

  if current phase is not detailed enough:
      create [Review] phase-expansion card
      dispatch NEW Reviewer
      receive proposal
      Orchestrator updates tasks/plan append-only

  ready_tasks = tasks with satisfied dependencies

  if multiple ready tasks are parallel-safe:
      for each selected task:
          create JIT card
          dispatch NEW Worker
  else:
      create JIT card for next task
      dispatch NEW Worker

  while workers running:
      do not terminate orchestration
      wait/poll/sleep
      react to completed workers

  for each worker result:
      verify structured handoff
      verify DoD evidence

      if PASS and accepted:
          mark task done
          update docs
      elif implementation defect:
          create NEW [Fix] card
          dispatch NEW Worker
      elif hard blocker:
          record blocker
          ask human

  if all tasks in phase accepted:
      create [Review] phase card
      dispatch NEW Reviewer

      if review PASS:
          mark phase passed
          continue
      elif review finds implementation defect:
          create NEW [Fix] worker task(s)
          re-review with NEW Reviewer
      elif review needs human decision:
          ask human

AFTER all phases:
  dispatch NEW Reviewer for final cross-phase review

IF final PASS:
  update final docs
  close board
ELSE:
  resolve findings using the same rules
```

---

# 33. Anti-context-overflow rules

Orchestrator phải giảm context noise bằng cách:

- không pre-create toàn bộ Kanban;
- không giữ output raw dài của mọi Worker trong main prompt khi đã tóm tắt vào persistent docs;
- dùng `agent-state.md` làm current state;
- dùng `handoffs.md` làm audit trail;
- dùng `implementation-summary.md` làm accepted implementation history;
- dùng `review-report.md` làm review history;
- Worker đọc task-specific context thay vì toàn bộ lịch sử chat nếu không cần;
- mỗi Worker là context mới;
- không resume Worker cũ.

---

# 34. Security and secret handling

Mặc định:

- không log secret;
- không commit `.env` thật;
- không đưa credential vào handoff;
- không đưa token vào Kanban;
- env example chỉ dùng placeholder;
- không paste secret vào `docs/`;
- nếu Worker nhìn thấy secret không cần thiết, không echo lại trong output;
- secret rotation / destructive credential action cần human approval khi phù hợp.

---

# 35. Những điều bị cấm

## Orchestrator KHÔNG ĐƯỢC

- code thay Worker;
- fix source trực tiếp;
- tạo trước toàn bộ Kanban cards;
- mark task done không có evidence;
- sửa DoD chỉ để pass;
- sửa/xóa quyết định gốc không có human decision;
- resume Worker cũ;
- auto-retry hard blocker vô hạn;
- bỏ qua phase review;
- bỏ qua final review.

## Worker KHÔNG ĐƯỢC

- làm nhiều task trong một invocation;
- sửa `docs/`;
- tự mark task complete;
- tự sửa plan/tasks;
- mở rộng scope;
- implement Backlog Candidate;
- gọi Worker khác;
- chờ được recall;
- dùng destructive Git tùy tiện;
- expose secret.

## Reviewer KHÔNG ĐƯỢC

- sửa source;
- sửa `docs/`;
- trở thành Worker trá hình;
- tự thay đổi roadmap;
- tự mark phase PASS trong `tasks.md`;
- tự mở rộng phase trực tiếp trong file.

---

# 36. Bootstrap checklist cho Orchestrator

Trước card đầu tiên:

```markdown
- [ ] Xác định repo root
- [ ] Xác định docs path
- [ ] Đọc plan.md
- [ ] Đọc tasks.md
- [ ] Đọc agent-state.md nếu tồn tại
- [ ] Đọc handoffs.md nếu tồn tại
- [ ] Kiểm tra current Git state
- [ ] Xác định phase hiện tại
- [ ] Xác định dependency
- [ ] Xác định Human Task đang block
- [ ] Tạo Board mới, Board trống
- [ ] Ghi board ID/name vào agent-state.md
- [ ] Chọn task đầu tiên đủ điều kiện
- [ ] Tạo card JIT
- [ ] Dispatch Worker mới
```

---

# 37. Task acceptance checklist cho Orchestrator

Trước khi mark `✅`:

```markdown
- [ ] Worker đúng task
- [ ] Không có scope creep
- [ ] Không sửa docs trái phép
- [ ] Files changed hợp lý
- [ ] Commands run được ghi rõ
- [ ] Tests có kết quả
- [ ] Mọi DoD có evidence
- [ ] Không còn blocker
- [ ] Backlog Candidate đã được xem xét
- [ ] Git state hợp lệ
- [ ] implementation-summary.md đã cập nhật
- [ ] handoffs.md đã append
- [ ] agent-state.md đã cập nhật
```

---

# 38. Phase acceptance checklist

```markdown
- [ ] Tất cả task thuộc phase đã được Orchestrator accept
- [ ] Không còn task 🔄
- [ ] Không còn blocker chưa xử lý
- [ ] Reviewer phase đã chạy
- [ ] Reviewer PASS
- [ ] review-report.md đã cập nhật
- [ ] implementation-summary.md phản ánh đúng phase
- [ ] Backlog phát sinh đã được ghi
- [ ] agent-state.md đã chuyển sang phase tiếp theo
```

---

# 39. Final completion checklist

```markdown
- [ ] Mọi phase trong phạm vi đã PASS
- [ ] Human Tasks cần thiết đã hoàn thành
- [ ] Không còn blocker ẩn
- [ ] Backlog được phân biệt rõ với committed scope
- [ ] Final Cross-Phase Reviewer đã chạy
- [ ] Final Reviewer PASS
- [ ] tasks.md cập nhật đúng trạng thái
- [ ] implementation-summary.md hoàn chỉnh
- [ ] review-report.md có final review
- [ ] handoffs.md đầy đủ
- [ ] agent-state.md = COMPLETE
- [ ] Git state không có thay đổi bất ngờ
- [ ] Board được đóng
```

---

# 40. Nguyên tắc tương thích với META-LAP-KE-HOACH

Protocol thực thi này giả định planning tuân theo các nguyên tắc:

1. Phase gần được viết chi tiết; phase xa cố ý chưa chi tiết.
2. Task đủ nhỏ để một Worker xử lý độc lập.
3. DoD phải kiểm chứng được.
4. Có mục Human Task `T-H`.
5. Có Backlog.
6. Task có dependency rõ.
7. Task tham chiếu ngược về kế hoạch.
8. Khi tới gần phase chưa chi tiết, phase mới được mở rộng dựa trên kiến thức thực tế đã tích lũy.

Hai file có trách nhiệm khác nhau:

```text
META-LAP-KE-HOACH.md
→ cách tạo plan/tasks tốt

HERMES-AGENT-EXECUTION-PROTOCOL.md
→ cách Hermes thực thi plan/tasks đó
```

---

# 41. Quy tắc ưu tiên khi có xung đột

Nếu instruction xung đột, ưu tiên theo thứ tự:

```text
1. Quyết định trực tiếp mới nhất của người dùng
2. Ràng buộc an toàn / bảo mật / dữ liệu
3. plan.md
4. tasks.md
5. HERMES-AGENT-EXECUTION-PROTOCOL.md
6. agent-state.md / handoffs.md / implementation-summary.md / review-report.md
7. Suy luận của agent
```

Nếu xung đột ở cấp 1–4 không thể tự giải quyết mà không thay đổi intent:

```text
STOP affected branch
→ ghi blocker
→ hỏi người
```

Không tự chọn phương án “có vẻ hợp lý nhất” khi lựa chọn đó thay đổi architecture hoặc scope.

---

# 42. Tóm tắt workflow chuẩn

```text
HUMAN
  │
  ├─ tạo/chốt plan.md + tasks.md
  ▼
ORCHESTRATOR — main session
  │
  ├─ tạo fresh empty Board
  ├─ đọc plan/tasks/state
  │
  ├─ JIT create card
  ├──────────────► NEW WORKER — one task
  │                    │
  │                    ├─ code/fix
  │                    ├─ test
  │                    ├─ DoD evidence
  │                    └─ terminal handoff
  │
  ├─ verify DoD
  ├─ update docs
  │
  ├─ next task / parallel independent tasks
  │
  ├─ phase complete
  ├──────────────► NEW REVIEWER — phase review
  │                    │
  │                    └─ terminal handoff
  │
  ├─ PASS → next phase
  ├─ defect → NEW [Fix] Worker
  ├─ hard decision → HUMAN
  │
  ├─ future phase still vague
  ├──────────────► NEW REVIEWER — phase expansion
  │
  ├─ Orchestrator appends expanded tasks
  │
  └─ drain continues
        │
        ▼
ALL PHASES COMPLETE
        │
        └──────────────► NEW REVIEWER — final cross-phase review
                              │
                              ▼
                         PASS / FIX / HUMAN
                              │
                              ▼
                         CLOSE BOARD
```

---

# 43. One-line invariant

> **Orchestrator owns state and docs; Worker owns exactly one implementation task and its tests; Reviewer owns phase-level judgment; Human owns decisions that agents must not guess. Every new unit of work gets a new isolated agent session.**
