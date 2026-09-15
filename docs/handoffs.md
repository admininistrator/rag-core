# Handoffs — Bàn giao giữa các session

> Current checkpoint ở đầu; lịch sử attempt/evidence append ở dưới. Không xóa output cũ để che lỗi.

## Current checkpoint

- **Giai đoạn:** T00 — hồ sơ đã kiểm chứng; COMPLETE có hiệu lực khi completion commit T00 tồn tại. Chưa triển khai code.
- **Task tiếp theo:** T01; Orchestrator kiểm completion commit T00 trước giao việc.
- **Branch ban đầu:** `main`, chưa có commit ở thời điểm inspect.
- **Files có sẵn khi nhận việc:** README.md và RUNBOOK.md rỗng; prompt corpus gốc có nội dung, tất cả untracked.
- **Files thuộc T00:** AGENTS.md, README.md, RUNBOOK.md, docs/plan.md, docs/tasks.md, docs/handoffs.md, docs/implementation-summary.md.
- **File người dùng giữ nguyên:** `corpus-documents/Codex Prompt – Build RAG Evaluation Corpus.md`; chưa stage trong T00, T01 được giao đưa nguyên bản vào Git.
- **Code/services/corpus data:** chưa tạo hoặc chạy. Docker CLI và Python 3.13 có mặt, chưa kiểm Docker daemon/GPU/provider credentials. Baseline implementation sẽ dùng Python 3.12.
- **Bất biến cần nhớ:** mọi query session-only; index retained không cấp quyền; app sở hữu source/history; không tích hợp Scarlet trong backlog này.
- **Orchestrator:** GPT-6-Astra, chỉ điều phối; worker GPT-5.6-Sol/xhigh mới từng task/attempt, không fork history, không song song. Đọc AGENTS trước giao việc.
- **Quyết định người dùng còn thiếu:** không còn yêu cầu sản phẩm pending. Secrets/môi trường implementation cần kiểm tại task tương ứng, không giả định đã có.
- **Commit T00:** subject `docs(T00): establish RAG core implementation blueprint`. Resolve bằng `git log -1 --format=%H --grep="^docs(T00):"`; nếu không tồn tại thì T00 còn ở bước commit và không được bắt đầu T01. Hash/output commit trả sau commit trong báo cáo session, tránh tự tham chiếu hash vào chính commit đó.

## Cách ghi bằng chứng

Mỗi task/attempt có anchor `h-tXX-aYY`. Ghi task/phase, agent/model/effort, thời điểm, cwd, commands nguyên văn, expected/actual/exit code, output thật, services/provider/model/index revisions, changed files, docs updates và blockers. Output dài có file log đã redacted kèm excerpt thật. Không ghi SKIP thành PASS; không tạo output giả từ expected.

Hash completion commit trả sau commit; hash không thể nằm trong chính commit đó. Dùng subject/Task-ID để resolve; task sau có thể ghi actual hash task trước. Orchestrator kiểm commit/evidence trước chuyển task.

<a id="h-t00"></a>
## H-T00 — Phase 0 / T00 / initial documentation session

### Phạm vi và quyết định

- Người dùng đã kết thúc củng cố yêu cầu và cho phép tạo hồ sơ ban đầu.
- Tạo kế hoạch chi tiết + task backlog, skeleton nhật ký/README/RUNBOOK; không triển khai T01 hoặc corpus.
- Quy định mới nhất thay cách hiểu “Default trên toàn kho user”: Default chỉ trên tài liệu session; Document subset trong session; Multilingual vẫn session-only.
- Admin UI được thêm vào kế hoạch bằng Jinja2/CSS/JS trong FastAPI để phục vụ local.
- README/RUNBOOK phải được cập nhật trong mỗi task; RUNBOOK chuẩn bị agent tích hợp Scarlet/app khác sau này.

### Evidence E00 — Inspect repository trước chỉnh sửa

CWD: `C:\Users\Admin\Documents\GitHub\rag-core`

Commands thực tế (trích các lệnh liên quan từ lượt inspect):

```powershell
rg --files --hidden -g '!.git' -g '!node_modules' -g '!.venv'
git status --short
git log -3 --oneline
```

Output thật:

```text
RUNBOOK.md
README.md
corpus-documents\Codex Prompt – Build RAG Evaluation Corpus.md
warning: unable to access 'C:\Users\Admin/.config/git/ignore': Permission denied
?? README.md
?? RUNBOOK.md
?? corpus-documents/
fatal: your current branch 'main' does not have any commits yet
```

Exit code của command group: **1**, do `git log` trên branch chưa có commit. Đây là trạng thái repo ban đầu, không phải kiểm thử ứng dụng fail. Đọc README/RUNBOOK bằng UTF-8 xác nhận hai file rỗng. Không có AGENTS.md trong repo hoặc các thư mục cha đã kiểm.

### Evidence E01 — Tooling hiện có

```powershell
Get-Command python, py, docker, git -ErrorAction SilentlyContinue | Select-Object Name,Source
git config --local --get user.name
git config --local --get user.email
```

Output thật:

```text
Name       Source
python.exe C:\Users\Admin\AppData\Local\Programs\Python\Python313\python.exe
py.exe     C:\Users\Admin\AppData\Local\Programs\Python\Launcher\py.exe
docker.exe C:\Program Files\Docker\Docker\resources\bin\docker.exe
git.exe    C:\Program Files\Git\cmd\git.exe
```

Hai `git config --local --get` không có giá trị, command group exit **1**. Chưa kết luận global Git identity thiếu; kiểm lúc tạo commit. Có launcher không chứng minh Python 3.12 đã được cài.

### Evidence E02 — Kiểm chứng tài liệu

Lần đầu validator chạy qua PowerShell stdin bị chuyển ký tự tiếng Việt trong script sang dấu `?`; exit **1**. Đây là lỗi encoding của command kiểm tra, không phải thiếu trường trong file UTF-8:

```text
PASS UTF-8/nonempty: 7 files
PASS internal links/anchors: 136
Traceback (most recent call last):
  File "<stdin>", line 43, in <module>
AssertionError: Missing Tr?ng th?i: T00
```

Đã sửa script kiểm tra dùng Unicode escapes trong mã nguồn truyền qua stdin; không đổi nội dung tiếng Việt của tài liệu để né lỗi. Command thực tế chạy lại (cwd như E00):

```powershell
@'
from pathlib import Path
from urllib.parse import unquote
import re

root = Path.cwd()
files = [Path(p) for p in (
    "AGENTS.md", "README.md", "RUNBOOK.md", "docs/plan.md",
    "docs/tasks.md", "docs/handoffs.md", "docs/implementation-summary.md"
)]
texts = {}
for rel in files:
    text = (root / rel).read_text(encoding="utf-8")
    assert text.strip(), f"Empty: {rel}"
    assert "\ufffd" not in text, f"Replacement character: {rel}"
    texts[rel.as_posix()] = text
print(f"PASS UTF-8/nonempty: {len(files)} files")

links = 0
for rel in files:
    for target in re.findall(r"\[[^\]\n]+\]\(([^)\n]+)\)", texts[rel.as_posix()]):
        target = target.strip("<>")
        if re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", target):
            continue
        filename, _, fragment = target.partition("#")
        dest = (root / rel.parent / unquote(filename)).resolve() if filename else (root / rel).resolve()
        assert dest.is_file(), f"Broken link in {rel}: {target}"
        if fragment:
            content = dest.read_text(encoding="utf-8")
            anchors = set(re.findall(r'<a id="([^"]+)"></a>', content))
            assert unquote(fragment) in anchors, f"Missing anchor in {rel}: {target}"
        links += 1
print(f"PASS internal links/anchors: {links}")

task_text = texts["docs/tasks.md"]
matches = list(re.finditer(r"^### (T\d{2}) \u2014 (.+)$", task_text, re.M))
assert [m.group(1) for m in matches] == [f"T{i:02d}" for i in range(37)]
fields = ["Tr\u1ea1ng th\u00e1i", "Ph\u1ee5 thu\u1ed9c", "Tham chi\u1ebfu k\u1ebf ho\u1ea1ch", "C\u00f4ng vi\u1ec7c",
          "Xong khi th\u1ecfa m\u00e3n DoD", "C\u1ea1m b\u1eaby", "Ghi ch\u00fa th\u1ef1c thi"]
graph, statuses = {}, {}
for i, m in enumerate(matches):
    body = task_text[m.end():matches[i + 1].start() if i + 1 < len(matches) else len(task_text)]
    for field in fields:
        assert f"**{field}:**" in body, f"Missing {field}: {m.group(1)}"
    task_id = m.group(1)
    status = re.search(r"\*\*Tr\u1ea1ng th\u00e1i:\*\* (\w+)", body).group(1)
    assert status in {"TODO", "IN_PROGRESS", "BLOCKED", "COMPLETE"}
    statuses[task_id] = status
    dependency = re.search(r"\*\*Ph\u1ee5 thu\u1ed9c:\*\* ([^\n]+)", body).group(1)
    deps = re.findall(r"T\d{2}", dependency)
    assert all(int(d[1:]) < i for d in deps), (task_id, deps)
    if i:
        assert f"T{i - 1:02d}" in deps, f"Missing sequential predecessor: {task_id}"
    assert re.search(r"  1\. ", body) and re.search(r"  2\. ", body), task_id
    graph[task_id] = deps
assert all(statuses[f"T{i:02d}"] == "TODO" for i in range(1, 37))
assert statuses["T00"] in {"IN_PROGRESS", "COMPLETE"}
print("PASS task fields/status/dependencies: T00-T36, sequential and acyclic")
print(f"PASS implementation untouched: T01-T36 TODO; T00 {statuses['T00']}")

plan = texts["docs/plan.md"]
assert len(re.findall(r'<a id="p\d{2}"></a>', plan)) == 18
for phrase in ("session", "gpt-5.6-sol", "xhigh", 'fork_turns="none"', "README", "RUNBOOK"):
    assert phrase in texts["AGENTS.md"] and phrase in plan, phrase
assert "app/owner AND" in plan
print("PASS plan anchors and critical orchestration/scope/doc rules")
for rel in files:
    print(f"{rel.as_posix()}: {len(texts[rel.as_posix()].splitlines())} lines")
print("DOCUMENTATION CHECK: PASS")
'@ | python -
```

Exit code: **0**. Output thật tại thời điểm kiểm (trước khi bổ sung entry này):

```text
PASS UTF-8/nonempty: 7 files
PASS internal links/anchors: 136
PASS task fields/status/dependencies: T00-T36, sequential and acyclic
PASS implementation untouched: T01-T36 TODO; T00 IN_PROGRESS
PASS plan anchors and critical orchestration/scope/doc rules
AGENTS.md: 122 lines
README.md: 59 lines
RUNBOOK.md: 337 lines
docs/plan.md: 458 lines
docs/tasks.md: 517 lines
docs/handoffs.md: 110 lines
docs/implementation-summary.md: 54 lines
DOCUMENTATION CHECK: PASS
```

### Evidence E03 — Git identity và review

Command thực tế:

```powershell
$authorCheck = git var GIT_AUTHOR_IDENT 2>&1; if ($LASTEXITCODE -eq 0) { Write-Output 'GIT_AUTHOR_IDENT configured' } else { Write-Output $authorCheck; exit 1 }; git status --short
```

Exit code: **0**. Output thật:

```text
GIT_AUTHOR_IDENT configured
warning: unable to access 'C:\Users\Admin/.config/git/ignore': Permission denied
?? AGENTS.md
?? README.md
?? RUNBOOK.md
?? corpus-documents/
?? docs/
```

Không sửa Git identity/global config. `git diff --check` ở lượt inspect exit **0**, không có output; vì các file còn untracked, bước này chưa chứng minh staged patch sạch. Staged check bắt buộc trước commit.

Review nội dung: đã đồng bộ default domain parameter, session-only ở cả ba domains, exact version/generation pair filtering, GPU tùy chọn có capability evidence, admission gate tránh tính PASS bằng cách reject toàn bộ load, list/detach routes và corpus-vs-runtime domain mapping.

### Evidence E04 — Staging và patch check

Đã stage đúng bảy file bằng command dưới đây; exit **0**. Git cảnh báo LF sẽ thành CRLF theo cấu hình máy; T01 sẽ thêm `.gitattributes`. Không sửa config Git toàn cục.

```powershell
git add -- AGENTS.md README.md RUNBOOK.md docs/plan.md docs/tasks.md docs/handoffs.md docs/implementation-summary.md
```

Commands review thực tế:

```powershell
git diff --cached --check; git diff --cached --stat; git diff --cached --name-only
```

Exit code: **0**. Output thật tại thời điểm review, trước khi thêm entry này và cập nhật trạng thái T00:

```text
warning: unable to access 'C:\Users\Admin/.config/git/ignore': Permission denied
warning: unable to access 'C:\Users\Admin/.config/git/ignore': Permission denied
 AGENTS.md                      | 122 ++++++++++
 README.md                      |  59 +++++
 RUNBOOK.md                     | 337 +++++++++++++++++++++++++++
 docs/handoffs.md               | 244 +++++++++++++++++++
 docs/implementation-summary.md |  54 +++++
 docs/plan.md                   | 458 ++++++++++++++++++++++++++++++++++++
 docs/tasks.md                  | 517 +++++++++++++++++++++++++++++++++++++++++
 7 files changed, 1791 insertions(+)
warning: unable to access 'C:\Users\Admin/.config/git/ignore': Permission denied
AGENTS.md
README.md
RUNBOOK.md
docs/handoffs.md
docs/implementation-summary.md
docs/plan.md
docs/tasks.md
```

Validator E02 cũng đã chạy lại sau bổ sung logs với exit **0**, vẫn 136 links/anchors và 37 tasks hợp lệ. Không kiểm chứng application runtime ở T00.

### Evidence E05 — Final precommit

Đã chạy lại command validator nguyên văn ở E02 sau cập nhật trạng thái T00. Exit **0**; trích nguyên văn các dòng kết quả (bỏ bảng line counts):

```text
PASS UTF-8/nonempty: 7 files
PASS internal links/anchors: 136
PASS task fields/status/dependencies: T00-T36, sequential and acyclic
PASS implementation untouched: T01-T36 TODO; T00 COMPLETE
PASS plan anchors and critical orchestration/scope/doc rules
DOCUMENTATION CHECK: PASS
```

Đã stage lại đúng bảy file. Chạy riêng `git diff --cached --check`, exit **0**, stdout rỗng; stderr thật:

```text
warning: unable to access 'C:\Users\Admin/.config/git/ignore': Permission denied
```

Cảnh báo đọc global ignore không làm patch check thất bại; không chỉnh file cấu hình ngoài repo. T00 là task tài liệu đã được người dùng cho phép, dùng Git identity hiện có. Completion commit được thực hiện sau ghi log này, hash/exit/output xem báo cáo session và `git log` theo subject T00. Không điền hash hoặc output commit giả trước khi commit chạy.

### DoD T00 — Kết quả

- DoD-1 UTF-8/link/anchor/task fields/dependencies: PASS (E02).
- DoD-2 consistency/scope/orchestration/docs: PASS, review như E03; chưa task implementation nào thực thi.
- DoD-3 staged diff: PASS E04. Completion commit là bằng chứng D6 trong Git; actual hash/output trả sau commit ở báo cáo session, không bịa trước vào file đang commit.
- D1/D2/D3: documentation checks phù hợp T00; không có pytest/app/live service tests.
- D4: cả README/RUNBOOK và task/handoff/summary đã viết.
- D5: chỉ bảy file Markdown trong scope; prompt corpus gốc giữ nguyên, chưa stage.
- D6: commit theo subject T00 là điều kiện đóng task; thiếu completion commit thì coi T00 chưa đóng.
- Prompt Orchestrator được chuyển trong phản hồi hoàn tất; người dùng mở session mới để thực thi.


### Bàn giao implementation

Worker T01 đọc docs và prompt corpus, ghi baseline untracked trước sửa. Không coi các command có trong task TODO/RUNBOOK DESIGNED là đã tồn tại. Không khởi chạy đồng thời nhiều workers; không reuse agent attempt trước.

## Mẫu append cho attempt sau

```text
Anchor: h-tXX-aYY
Phase/task/attempt:
Agent/model/effort/context mode:
Started/ended + timezone:
CWD / branch / starting HEAD / baseline dirty files:
Plan refs + dependency notes đã đọc:
Implementation/files:
DoD item -> command -> exit code -> actual output:
Environment/services/provider/model/revisions:
README/RUNBOOK changes (hoặc N/A và lý do):
Commit subject + actual hash nếu có sau commit:
Result: COMPLETE / BLOCKED / IN_PROGRESS
Blocker/reproduction/last-good-state/next action:
```
