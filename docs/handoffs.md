# Handoffs — Bàn giao giữa các session

> Current checkpoint ở đầu; lịch sử attempt/evidence append ở dưới. Không xóa output cũ để che lỗi.

## Current checkpoint

- **Current:** Phase 1 / T06 / T06-A03 documentation and evidence closure on CLEAN `main`/A02 implementation commit `6863abf221db2d387e141656610c710ceac14dff`; root accepted A02 technical DoD and verified actual `gpt-5.6-sol`/`xhigh` runtime. A03 worker `/root/t06_a03`, fresh `fork_turns="none"`, began 2026-09-22 08:43 +07:00. Original A02 results remain at [H-T06-A02](#h-t06-a02); recovered exact historical invocations at [H-T06-A03](#h-t06-a03).
- **Boundary:** real FinanceBench setup/validator PASS: official pin `cc39aeb4afdf33909ee1412188bf89035950c2eb`, 150 open QA, 84/368 referenced PDFs, 189 evidence, 165,527,662B/12,013pages, zero-based pages0–303 all in range. A02 rerun preserved91published+84cache hashes/mtimes/150IDs/downloaded_at without PDF redownload;19document+81common+37default tests, Ruff/mypy16 PASS. No T07/API/model/retrieval work.
- **Next/risks:** A03 documentation check passed; closure commit subject is `docs(T06): finalize acceptance evidence and paused checkpoint`, with actual hash returned after commit for root review. Then **USER-PAUSED AFTER T06**. T07 may start only on a new user request. Raw/PDF/normalized FinanceBench QA are local/ignored: GitHub has no explicit dataset/PDF grant, publisher card separately declares CC-BY-NC-4.0 and company rights remain separate. Tracked-ready/ignored-payload clean-clone recovery remains T08; hard crash requires operator lock/stage review.
- **Invariants:** query current-session-only, retained index không cấp quyền; app sở hữu source/history. Prompt corpus/AGENTS nguyên byte; plan chỉ thêm user-approved T05 sourceexception tạiP11. Không cloud/server/Scarlet/push/merge. Worker mới/attempt, một worker active, Orchestrator read-only.

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

<a id="h-t01-a01"></a>
## H-T01-A01 — Phase 0 / T01 / attempt T01-A01

### Identity, baseline và nguồn đã đọc

- Worker runtime record: thread `01a0a5a1-fe2a-70d3-8733-938e64399f17`, turn `01a0a5a1-fedd-7a73-801f-d5afc48b106c`, model `gpt-5.6-sol`, effort `xhigh`, cwd `C:\Users\Admin\Documents\GitHub\rag-core`; thread khác parent, khớp fresh context/`fork_turns="none"` do Orchestrator spawn.
- Started/ended: 2026-09-15 22:16–22:35 +07:00. Branch/starting HEAD: `main` / `7025eeac080b481c17f7d68f0290b1ee3e3165e9`, subject `docs(T00): establish RAG core implementation blueprint`.
- Baseline `git status --short`: warning global ignore permission có sẵn + `?? corpus-documents/`; không có dirty code/task khác. Prompt duy nhất do người dùng giao T01, 15,665 bytes, SHA-256 `7EC6E58AE4C24DB27AF4320BCB30222BBF2B67961D99C62980CEA4410AEE2C46`.
- Đã đọc AGENTS; T00/T01 notes; P01/P02/P13/P14/P15; handoff/summary/README/RUNBOOK; toàn bộ 712 dòng prompt corpus trước implementation. Allowed files giữ đúng brief T01; không sửa AGENTS/plan semantics và không chạy T02/corpus setup.

### Implementation và môi trường

- Python package `src/rag_core` có version + `py.typed`; typed settings public qua `rag_core.config`.
- `pyproject.toml` có requires Python 3.12, uv groups `api`/`ingestion`/`inference`/`dev`, Ruff, strict mypy + Pydantic plugin, pytest markers `unit/integration/contract/e2e/security/live/slow`; `uv.lock` revision 3 khóa `requires-python = "==3.12.*"` và 70 packages từ `https://pypi.org/simple` với artifact hashes.
- Base/dev là phần chạy ở T01. API/ingestion packages chỉ LOCKED/DESIGNED theo P02, không có service được khởi động. Inference group rỗng có chủ đích đến T17; không tải ML/model weights.
- Settings typed: defaults runtime + required PostgreSQL/Redis DSN. Error wrapper chỉ nêu field/message, suppress raw cause, Pydantic hide inputs; DSNs `repr=False`. Unit tests chứng minh missing fields, valid coercion và malformed credential-bearing input không hiện trong rendered traceback/repr.
- `scripts/check_docs.py` dùng standard library, prune cache/runtime/generated corpus trong lúc walk; kiểm UTF-8/nonempty source Markdown, local links/anchors, đủ field/status và ordered acyclic graph T00–T36.
- `.gitattributes` dùng UTF-8 + LF cho source; exact prompt path bỏ text/encoding/eol filters. `.gitignore` anchor runtime/model directories tại root, ignore generated corpus/raw và artifacts; không che source adapter `models` hay corpus scripts.
- Services/provider/model/index revision: không áp dụng T01. Docker/app/API/PG/Redis/Qdrant/provider/GPU không khởi động. Orchestrator preflight Docker riêng báo server 29.5.2; không tính là DoD T01.

### Tooling failures đã gặp và sửa trong cùng attempt

CWD cho mọi command: `C:\Users\Admin\Documents\GitHub\rag-core`.

1. `uv lock` và lần đầu `uv sync --locked --group dev` trong filesystem/network sandbox: exit **1**. Tail output thật của lỗi chung:

```text
error: Request failed after 3 retries in 6.1s
  Caused by: Failed to download https://github.com/astral-sh/python-build-standalone/releases/download/20260510/cpython-3.12.13%2B20260510-x86_64-pc-windows-msvc-install_only_stripped.tar.gz
  Caused by: error sending request for url (https://github.com/astral-sh/python-build-standalone/releases/download/20260510/cpython-3.12.13%2B20260510-x86_64-pc-windows-msvc-install_only_stripped.tar.gz)
  Caused by: client error (Connect)
  Caused by: tcp connect error
  Caused by: An attempt was made to access a socket in a way forbidden by its access permissions. (os error 10013)
```

Đây là sandbox network/outside-interpreter visibility, không phải lock hỏng. Theo escalation flow, uv dùng CPython 3.12.4 có sẵn tại `C:\Users\Admin\miniconda3\python.exe`; `uv lock` exit **0**, `Resolved 70 packages in 2.47s`. Lần sync escalated tạo `.venv`, build project, tải/cài 20 packages dev; exit **0**. Không đổi baseline sang host Python 3.13.2.

2. Lượt Ruff đầu exit **1** với hai `I001` import order ở docs script/test; sửa imports. Lượt mypy đầu exit **1** với `IPvAnyAddress` callable + hai missing constructor args; dùng typed `IPv4Address` default và Pydantic mypy plugin. Không hạ rule.

3. Lượt docs check sau khi thêm summary link exit **1**. Tool capture Windows render separator Unicode thành U+FFFD; annotation này không phải nội dung source. Output excerpt bỏ separator:

```text
DOCUMENTATION CHECK: FAIL
Missing anchor in C:\Users\Admin\Documents\GitHub\rag-core\docs\implementation-summary.md: handoffs.md#h-t01-a01
```

Anchor attempt này được thêm rồi validator chạy lại; lỗi chứng minh broken target bị bắt, không được đổi thành PASS giả.

### DoD-1 — locked env và quality commands

Trước các lệnh dưới, phiên PowerShell đặt `UV_CACHE_DIR=$PWD\.uv-cache` và `UV_PYTHON_INSTALL_DIR=$PWD\.uv-python`; cả hai paths nằm trong repo và ignored. Expected: dùng lock/Python 3.12, không resolve drift; checks pass. Actual:

Command:

```powershell
uv sync --locked --group dev
```

Exit **0**; output thật final:

```text
Resolved 70 packages in 1ms
Checked 20 packages in 1ms
```

Lần tạo sạch `.venv` ngay trước đó cũng exit **0**. Output thật đầy đủ:

```text
Using CPython 3.12.4 interpreter at: C:\Users\Admin\miniconda3\python.exe
Creating virtual environment at: .venv
Resolved 70 packages in 3ms
   Building rag-core @ file:///C:/Users/Admin/Documents/GitHub/rag-core
Downloading pygments (1.2MiB)
Downloading mypy (10.4MiB)
Downloading pydantic-core (1.9MiB)
Downloading ruff (10.1MiB)
 Downloaded pydantic-core
 Downloaded pygments
 Downloaded ruff
 Downloaded mypy
      Built rag-core @ file:///C:/Users/Admin/Documents/GitHub/rag-core
Prepared 20 packages in 3.80s
Installed 20 packages in 1.04s
 + annotated-types==0.8.0
 + colorama==0.4.6
 + iniconfig==2.3.0
 + librt==0.15.0
 + mypy==1.20.2
 + mypy-extensions==1.1.0
 + packaging==26.3
 + pathspec==1.1.1
 + pluggy==1.6.0
 + pydantic==2.13.5
 + pydantic-core==2.46.5
 + pydantic-settings==2.15.0
 + pygments==2.21.0
 + pytest==9.1.1
 + pytest-asyncio==1.4.0
 + python-dotenv==1.2.3
 + rag-core==0.1.0 (from file:///C:/Users/Admin/Documents/GitHub/rag-core)
 + ruff==0.16.7
 + typing-extensions==4.16.0
 + typing-inspection==0.4.4
```

Command `uv run ruff check .`: exit **0**, output `All checks passed!`.

Command `uv run mypy src`: exit **0**, output `Success: no issues found in 3 source files`.

Command:

```powershell
uv run pytest tests/unit/test_settings.py
```

Exit **0**; output thật:

```text
platform win32 -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Admin\Documents\GitHub\rag-core
configfile: pyproject.toml
plugins: asyncio-1.4.0
collected 3 items
tests\unit\test_settings.py ...                                          [100%]
============================== 3 passed in 0.14s ==============================
```

DoD-1 actual = expected: PASS. Test missing config exact message là `Missing required RAG Core configuration: DATABASE_URL, REDIS_URL`; invalid DATABASE_URL có synthetic marker `do-not-echo`, test rendered traceback xác minh marker vắng mặt. Không dùng credential thật.

### DoD-2 — docs, lock/interpreter và ignore policy

Command `uv run python scripts/check_docs.py`: exit **0**. Output thật final:

```text
PASS UTF-8/nonempty Markdown: 8 files
PASS internal links/anchors: 135
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```

Command `uv run python --version; Get-Content .venv\pyvenv.cfg; uv lock --check`: exit **0**. Output thật liên quan:

```text
Python 3.12.4
home = C:\Users\Admin\miniconda3
implementation = CPython
uv = 0.11.16
version_info = 3.12.4
include-system-site-packages = false
prompt = rag-core
Resolved 70 packages in 1ms
```

Ignore assertion command nguyên văn:

```powershell
$paths=@('.env','corpus-documents/default/raw/source.json','corpus-documents/default/documents/source.md','models/bge/model.safetensors','runtime/rag-core.pid','logs/rag-core.log'); $matches=@(git check-ignore -v --no-index -- $paths); if($LASTEXITCODE -ne 0 -or $matches.Count -ne $paths.Count){Write-Error "Expected $($paths.Count) ignored paths, found $($matches.Count)"; exit 1}; $matches
```

Exit **0**, đủ 6/6 matches. Output thật:

```text
.gitignore:22:.env    .env
.gitignore:43:corpus-documents/*/raw/    corpus-documents/default/raw/source.json
.gitignore:44:corpus-documents/*/documents/    corpus-documents/default/documents/source.md
.gitignore:50:/models/    models/bge/model.safetensors
.gitignore:30:/runtime/    runtime/rag-core.pid
.gitignore:29:/logs/    logs/rag-core.log
```

Assertion ngược command nguyên văn:

```powershell
$paths=@('.env.example','src/rag_core/adapters/models/client.py','corpus-documents/scripts/setup_corpus.py','corpus-documents/Codex Prompt – Build RAG Evaluation Corpus.md'); foreach($path in $paths){git check-ignore -q --no-index -- $path; if($LASTEXITCODE -eq 0){Write-Error "Unexpectedly ignored: $path"; exit 1}; Write-Output "PASS not ignored: $path"}
```

Exit **0**; output thật (warning global ignore lặp trước mỗi dòng, giữ một lần ở đây):

```text
warning: unable to access 'C:\Users\Admin/.config/git/ignore': Permission denied
PASS not ignored: .env.example
PASS not ignored: src/rag_core/adapters/models/client.py
PASS not ignored: corpus-documents/scripts/setup_corpus.py
PASS not ignored: corpus-documents/Codex Prompt – Build RAG Evaluation Corpus.md
```

Không sửa global config.

Command nguyên văn:

```powershell
git check-attr text eol working-tree-encoding -- .gitattributes pyproject.toml README.md scripts/check_docs.py 'corpus-documents/Codex Prompt – Build RAG Evaluation Corpus.md'; Get-FileHash -Algorithm SHA256 -LiteralPath 'corpus-documents\Codex Prompt – Build RAG Evaluation Corpus.md' | Select-Object -ExpandProperty Hash
```

Exit **0**; output thật:

```text
.gitattributes: text: auto
.gitattributes: eol: lf
.gitattributes: working-tree-encoding: unspecified
pyproject.toml: text: set
pyproject.toml: eol: lf
pyproject.toml: working-tree-encoding: UTF-8
README.md: text: set
README.md: eol: lf
README.md: working-tree-encoding: UTF-8
scripts/check_docs.py: text: set
scripts/check_docs.py: eol: lf
scripts/check_docs.py: working-tree-encoding: UTF-8
"corpus-documents/Codex Prompt \342\200\223 Build RAG Evaluation Corpus.md": text: unset
"corpus-documents/Codex Prompt \342\200\223 Build RAG Evaluation Corpus.md": eol: unspecified
"corpus-documents/Codex Prompt \342\200\223 Build RAG Evaluation Corpus.md": working-tree-encoding: unspecified
7EC6E58AE4C24DB27AF4320BCB30222BBF2B67961D99C62980CEA4410AEE2C46
```

### D1–D6, docs và handoff

- **D1/D2:** dependency notes đã đọc; final `git diff --check`, scope diff và quality rerun được ghi ở final review dưới đây.
- **D3:** từng command DoD chạy riêng; expected/actual/exit ở các mục trên. Không có skip/mock/live replacement.
- **D4:** README prerequisites/commands/settings status; RUNBOOK bootstrap/dependency/env table; task note, handoff và implementation summary cập nhật đồng thời, có VERIFIED/DESIGNED.
- **D5:** review secrets/raw corpus/weights/cache và staged prompt blob proof ghi ở final review. Không migration/schema breaking change.
- **D6:** stage explicit paths, cached diff check và commit subject `feat(T01): scaffold Python project and quality checks`; actual hash chỉ trả sau commit.
- **Result/limitations:** completion candidate; chưa app/service/integration/live/provider/model/corpus benchmark. Default sandbox không thấy outside Python/cache/network, nhưng local-cache + approved network run tái tạo env thành công. Next là Orchestrator review rồi worker mới cho T02.

Final scope/hygiene review trước stage:

- Command `git diff --check; git status --short; git diff --stat; rg --files -g '!.git' -g '!.venv' -g '!.uv-cache' -g '!.uv-python' | Sort-Object`: exit **0**. `git diff --check` stdout rỗng; status/source listing chỉ có 18 candidate paths T01 và các file baseline docs; không có ignored artifact. Git lặp warning không đọc global ignore ngoài repo; không chỉnh global config.
- Secret review command nguyên văn:

```powershell
$candidate=@('.env.example','.gitattributes','.gitignore','.python-version','pyproject.toml','uv.lock','scripts/check_docs.py','src/rag_core/__init__.py','src/rag_core/config/__init__.py','src/rag_core/config/settings.py','src/rag_core/py.typed','tests/unit/test_settings.py','README.md','RUNBOOK.md','docs/tasks.md','docs/handoffs.md','docs/implementation-summary.md','corpus-documents/Codex Prompt – Build RAG Evaluation Corpus.md'); $matches=@(rg -n -i '(api[_-]?key|secret|password|bearer|private[_-]?key|access[_-]?key|token)' -- $candidate); $nonEmpty=@(rg -n '^(QDRANT_API_KEY|DEEPSEEK_API_KEY|ANTHROPIC_API_KEY|STORAGE_ACCESS_KEY_ID|STORAGE_SECRET_ACCESS_KEY|ADMIN_SECRET)=.+' -- .env.example); Write-Output "Sensitive-name matches manually reviewed: $($matches.Count)"; if($nonEmpty.Count -ne 0){Write-Error 'Secret-designated .env.example value is nonempty'; exit 1}; Write-Output 'PASS secret-designated .env.example values are empty; no real credential found in reviewed matches'
```

Exit **0**; output thật:

```text
Sensitive-name matches manually reviewed: 49
PASS secret-designated .env.example values are empty; no real credential found in reviewed matches
```

- Size review dùng cùng array `$candidate`, command nguyên văn phần kiểm: `$items=@($candidate | ForEach-Object {Get-Item -LiteralPath $_}); $large=@($items | Where-Object Length -gt 1048576); if($large.Count -ne 0){$large | Select-Object FullName,Length; exit 1}; Write-Output "PASS candidate_files=$($items.Count) files_over_1MiB=0 uv_lock_bytes=$((Get-Item -LiteralPath uv.lock).Length) prompt_bytes=$((Get-Item -LiteralPath 'corpus-documents/Codex Prompt – Build RAG Evaluation Corpus.md').Length)"`. Exit **0**; output `PASS candidate_files=18 files_over_1MiB=0 uv_lock_bytes=104538 prompt_bytes=15665`. Không raw downloaded corpus/model/runtime artifact trong candidate.
- Lock source command nguyên văn:

```powershell
$sources=@(rg '^source = ' uv.lock | Sort-Object -Unique); $sources; $unexpected=@($sources | Where-Object {$_ -ne 'source = { registry = "https://pypi.org/simple" }' -and $_ -ne 'source = { editable = "." }'}); if($unexpected.Count -ne 0){Write-Error 'Unexpected uv.lock source'; exit 1}; Write-Output 'PASS uv.lock sources: local editable project + PyPI registry only'
```

Exit **0**; output thật:

```text
source = { editable = "." }
source = { registry = "https://pypi.org/simple" }
PASS uv.lock sources: local editable project + PyPI registry only
```

Helper đầu tiên đã exit **1** vì kỳ vọng sai chỉ một source và không cho local editable; sửa assertion, không sửa lock để che kết quả.
- Helper size đầu tiên exit **1** do recurse vào ignored env/cache; thay bằng explicit 18-path task scope và PASS. Đây là lỗi command review, không phải candidate chứa file lớn.
- Prompt working-tree check: exit **0**, SHA-256 `7EC6E58AE4C24DB27AF4320BCB30222BBF2B67961D99C62980CEA4410AEE2C46`, 15,665 bytes. Staged blob OID/raw filter equality được kiểm ở bước D6.

### D6 staged review

Stage command nguyên văn:

```powershell
git add -- .env.example .gitattributes .gitignore .python-version pyproject.toml uv.lock scripts/check_docs.py src/rag_core/__init__.py src/rag_core/config/__init__.py src/rag_core/config/settings.py src/rag_core/py.typed tests/unit/test_settings.py README.md RUNBOOK.md docs/tasks.md docs/handoffs.md docs/implementation-summary.md 'corpus-documents/Codex Prompt – Build RAG Evaluation Corpus.md'
```

Exit **0**, stdout rỗng; không dùng `git add .`. `git diff --cached --check`: exit **0**, ngoài warning global ignore đã biết không có output. `git diff --cached --name-status` liệt kê đúng 18 files: 13 add (root config, prompt, pyproject/lock, script/package/test) và 5 modify (README, RUNBOOK, ba docs); `git status --short` không có unstaged/untracked path.

Prompt blob proof command nguyên văn:

```powershell
$path='corpus-documents/Codex Prompt – Build RAG Evaluation Corpus.md'; $raw=(git hash-object --no-filters -- "$path").Trim(); $filtered=(git hash-object --path="$path" -- "$path").Trim(); $staged=(git rev-parse ":$path").Trim(); $sha=(Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash; [pscustomobject]@{RawObject=$raw;FilteredObject=$filtered;StagedObject=$staged;WorkingSHA256=$sha;Bytes=(Get-Item -LiteralPath $path).Length} | Format-List; if($raw -ne $filtered -or $raw -ne $staged -or $sha -ne '7EC6E58AE4C24DB27AF4320BCB30222BBF2B67961D99C62980CEA4410AEE2C46'){Write-Error 'Prompt staged blob differs from original bytes'; exit 1}; Write-Output 'PASS prompt filter/raw/staged object IDs equal and SHA256 unchanged'
```

Exit **0**, output thật:

```text
RawObject      : 81ab3c77530722968d847391d8095284f1a874a9
FilteredObject : 81ab3c77530722968d847391d8095284f1a874a9
StagedObject   : 81ab3c77530722968d847391d8095284f1a874a9
WorkingSHA256  : 7EC6E58AE4C24DB27AF4320BCB30222BBF2B67961D99C62980CEA4410AEE2C46
Bytes          : 15665
PASS prompt filter/raw/staged object IDs equal and SHA256 unchanged
```

Sau khi thêm chính evidence D6 này, chỉ ba sổ docs được restage explicit; final cached check/docs check chạy lại trước commit. Completion commit chạy sau log này; actual hash/output trả trong báo cáo worker và có thể resolve bằng subject, không tự ghi hash vào commit.

<a id="h-t02-a01"></a>
## H-T02-A01 — Phase 0 / T02 / attempt T02-A01

Attempt kết thúc trước mọi repo mutation. Bằng chứng do Orchestrator cung cấp là runtime event sau, không phải shell command và không có exit code:

```text
Agent errored: You've hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/codex/settings/usage to purchase more credits or try again at Sep 16th, 2026 3:11 AM.
```

Không có repo checks/logs/code của A01 để ghi; root xác minh worktree sạch rồi tạo worker/context mới cho A02.

<a id="h-t02-a02"></a>
## H-T02-A02 — Phase 0 / T02 / attempt T02-A02

### Identity, baseline và kế hoạch

- Started: 2026-09-16 10:08 +07:00. Runtime record: thread `01a0a82f-8df3-7701-8a25-9ceff7d4dce9`, turn `01a0a82f-8e7e-7762-bb12-c2f9c7fd7971`, model `gpt-5.6-sol`, effort `xhigh`, cwd `C:\Users\Admin\Documents\GitHub\rag-core`; thread khác parent, khớp fresh context/`fork_turns="none"`.
- Baseline command `git status --short; git branch --show-current; git rev-parse HEAD`: exit **0**; stdout status rỗng, branch `main`, HEAD `ff8069abfd2e41fb9618eb7d35fa22bf220a39d6`. Warning không đọc `C:\Users\Admin/.config/git/ignore` có sẵn; không sửa global config.
- Đã đọc AGENTS; T02 và toàn execution notes T01; P01/P02/P12/P13/P14/P15; handoffs, implementation-summary, README, RUNBOOK; source/settings/lock T01 trước implementation. T01 completion commit đã được Orchestrator nghiệm thu.
- Allowed scope và kế hoạch đúng task note: chỉ Compose/Docker, dependency/config/API health/test/bootstrap/smoke T02 và tài liệu; pin image tag+digest thật, dependency health thật, persistence thật; không thêm fake worker/dispatcher/inference, business API/schema/migration/T03, provider/GPU hoặc sửa prompt corpus.

### Implementation và evidence

CWD cho mọi command dưới đây: `C:\Users\Admin\Documents\GitHub\rag-core`. Không có provider/model/GPU/live external call trong T02; integration ở đây là local Docker services thật.

- Files/runtime: `compose.yaml`, `.dockerignore`, `docker/api.Dockerfile`; health-only `rag_core.api`; settings/dependency lock; unit tests; bootstrap/smoke/Qdrant fixture helpers; README/RUNBOOK và ba sổ docs. API image non-root, chỉ cài base+`api`, không có OCR/ML/ingestion worker. Compose chỉ có PG/Qdrant/Redis/API và MinIO + bootstrap dưới profile; không fake worker/dispatcher/inference.
- `powershell.exe -NoProfile -ExecutionPolicy Bypass -File '.\scripts\bootstrap_local.ps1'`: exit **0**, tạo ba file ignored `.local/secrets/{postgres_password,minio_root_user,minio_root_password}` và output `Local Docker secret files are ready; values were not printed.` Không in/stage secret.
- Image manifest resolution dùng `docker buildx imagetools inspect <tag> --format '{{json .Manifest}}'`. Official tag/digest thực: Python `3.12.13-slim-bookworm@sha256:4766d8...`, uv `0.11.16@sha256:440fd6...`, PG `17.11-bookworm@sha256:051f7b...`, Redis `8.10.1-alpine3.23@sha256:becdda...`, Qdrant `v1.19.1-unprivileged@sha256:801777...`, MinIO `RELEASE.2025-07-23T15-54-02Z@sha256:d249d1...`, MC `RELEASE.2025-07-21T05-28-08Z@sha256:fb8f77...`. Lượt Docker Hub MinIO trả exit **1**, `pull access denied ... insufficient_scope`; cùng release resolve thành công từ official `quay.io/minio/*`, không dùng `latest`/digest giả.
- `uv lock` trong network sandbox: exit **1**, lỗi thật `Failed to fetch: https://pypi.org/simple/pydantic/` / socket permissions `os error 10013`. Rerun approved network cùng command: exit **0**, `Resolved 72 packages in 2.78s`, thêm `psycopg`/`psycopg-binary` 3.3.5. `uv sync --locked --group dev --group api`: exit **0**, cài locked FastAPI 0.141.1, HTTPX 0.28.1, psycopg 3.3.5, Redis client 7.4.1, Uvicorn 0.53.0; API image sync 27 packages trên Python 3.12.13.
- Initial Ruff exit **1** `SIM117` và mypy exit **1** cho dynamic psycopg kwargs/Redis awaitable; sửa context + typed conninfo/cast, không hạ rule. Initial quoted Qdrant one-liner exit **1** `SyntaxError` trước HTTP/mutation do Windows argument quoting; thay bằng tracked idempotent helper, `docker compose cp ...` + `docker compose exec -T api python /tmp/t02_qdrant_fixture.py seed|verify` đều exit **0**. Helper kiểm collection config và upsert; không delete/recreate; verify sau restart không reseed.

### DoD-1 — Compose build/start và dependency-aware health

Command `docker compose config --quiet`: exit **0**, stdout rỗng. Không render full config/secrets.

Command `docker compose --profile local-storage up -d --build`: exit **0** cả initial pull/build và final rebuild. Final excerpt thật:

```text
Using CPython 3.12.13 interpreter at: /usr/local/bin/python3
Resolved 72 packages in 3ms
Installed 27 packages in 81ms
exporting manifest list sha256:5d1716913419a968ee8b5f03706cff853a0d86968b476a6d05f883ac98f7f2a5
Image rag-core-api:t02 Built
Container rag-core-api-1 Recreated
Container rag-core-postgres-1 Healthy
Container rag-core-redis-1 Healthy
Container rag-core-minio-1 Healthy
Container rag-core-qdrant-1 Healthy
Container rag-core-api-1 Started
```

Command `docker compose --profile local-storage up -d --wait postgres qdrant redis api minio`: exit **0**; final output báo cả năm service `Healthy`. Command `powershell.exe -NoProfile -ExecutionPolicy Bypass -File '.\scripts\smoke_local.ps1'`: exit **0**:

```text
PASS /health/live status=ok
PASS /health/ready status=ready components=postgres,redis,qdrant
```

Dependency outage thật: `docker compose stop redis` exit **0**; command `curl.exe --silent --show-error --write-out "`nHTTP=%{http_code}`n" http://127.0.0.1:8000/health/live; curl.exe --silent --show-error --write-out "`nHTTP=%{http_code}`n" http://127.0.0.1:8000/health/ready` exit **0**, output:

```text
{"status":"ok"}
HTTP=200
{"status":"unavailable","components":{"postgres":"ok","redis":"unavailable","qdrant":"ok"}}
HTTP=503
```

`docker compose start redis; docker compose up -d --wait postgres qdrant redis api` exit **0** và smoke sau đó lại PASS ready. Actual = expected: live chỉ process; ready phản ánh dependency thật, không stub success.

### DoD-2 — status, ports, inspect và persistence restart

Command `docker compose --profile local-storage ps --all`: exit **0**. Final actual: API/PG/Qdrant/Redis/MinIO `healthy`, `minio-bootstrap` `Exited (0)`; ports hiển thị API `127.0.0.1:8000`, MinIO `127.0.0.1:9000-9001`, PG chỉ `5432/tcp`, Qdrant chỉ `6333-6334/tcp`, Redis chỉ `6379/tcp`.

Redacted inspect command nguyên văn (chỉ chọn image/health/ports/mount type+name+destination, không đọc env/secret value):

```powershell
$names=@('rag-core-api-1','rag-core-postgres-1','rag-core-qdrant-1','rag-core-redis-1','rag-core-minio-1'); $items=docker inspect $names | ConvertFrom-Json; foreach($item in $items){$ports=@(); foreach($property in $item.NetworkSettings.Ports.PSObject.Properties){$bindings=$property.Value; if($null -eq $bindings){$ports += "$($property.Name)=internal-only"}else{foreach($binding in $bindings){$ports += "$($property.Name)=$($binding.HostIp):$($binding.HostPort)"}}}; $mounts=@($item.Mounts | ForEach-Object {"$($_.Type):$($_.Name)->$($_.Destination)"}); [pscustomobject]@{Name=$item.Name.TrimStart('/'); Image=$item.Config.Image; Health=$item.State.Health.Status; Ports=($ports -join ', '); Mounts=($mounts -join ', ')} | Format-List}
```

Exit **0**; output excerpt thật đã redacted theo fields:

```text
Name   : rag-core-api-1
Image  : rag-core-api:t02
Health : healthy
Ports  : 8000/tcp=127.0.0.1:8000
Mounts : bind:->/run/secrets/postgres_password

Name   : rag-core-postgres-1
Health : healthy
Ports  : 5432/tcp=internal-only
Mounts : volume:rag-core_postgres_data->/var/lib/postgresql/data, bind:->/run/secrets/postgres_password

Name   : rag-core-qdrant-1
Health : healthy
Ports  : 6333/tcp=internal-only, 6334/tcp=internal-only
Mounts : volume:rag-core_qdrant_data->/qdrant/storage

Name   : rag-core-redis-1
Health : healthy
Ports  : 6379/tcp=internal-only
Mounts : volume:rag-core_redis_data->/data

Name   : rag-core-minio-1
Health : healthy
Ports  : 9000/tcp=127.0.0.1:9000, 9001/tcp=127.0.0.1:9001
Mounts : volume:rag-core_minio_data->/data, bind:->/run/secrets/minio_root_password, bind:->/run/secrets/minio_root_user
```

Actual: PG/Qdrant/Redis use pinned image digests and internal-only ports/named volumes; MinIO uses pinned Quay digest, loopback ports/named volume. Secret mounts chỉ hiện destination, không source/value. Không bind database files NTFS.

Synthetic fixtures trước restart:

- PG command `docker compose exec -T postgres psql -U rag_core -d rag_core -v ON_ERROR_STOP=1 -Atc "CREATE TABLE IF NOT EXISTS t02_persistence_fixture (id integer PRIMARY KEY, marker text NOT NULL); INSERT INTO t02_persistence_fixture (id, marker) VALUES (1, 'rag-core-t02-persistence-v1') ON CONFLICT (id) DO UPDATE SET marker = EXCLUDED.marker; SELECT marker FROM t02_persistence_fixture WHERE id = 1;"`: exit **0**, output `CREATE TABLE`, `INSERT 0 1`, `rag-core-t02-persistence-v1`.
- Qdrant commands nguyên văn: `docker compose cp scripts/t02_qdrant_fixture.py api:/tmp/t02_qdrant_fixture.py`; `docker compose exec -T api python /tmp/t02_qdrant_fixture.py seed`; `docker compose exec -T api python /tmp/t02_qdrant_fixture.py verify`. Cả ba exit **0**; cp output `rag-core-api-1 Copied scripts/t02_qdrant_fixture.py to rag-core-api-1:/tmp/t02_qdrant_fixture.py`; seed và verify mỗi lệnh output `rag-core-t02-persistence-v1`.
- `docker compose logs --no-color minio-bootstrap`: exit **0**, object `t02-persistence.txt`, Date `2026-09-16 03:20:12 UTC`, Size `28 B`, ETag `f9eb58fcfbb8e28513335e6d2fcc6b52-1`.

Command `docker compose --profile local-storage restart postgres qdrant minio`: exit **0**. Command `docker compose --profile local-storage up -d --wait postgres qdrant redis api minio`: exit **0**, services healthy.

Verification sau restart, **không reseed** PG/Qdrant:

```powershell
docker compose exec -T postgres psql -U rag_core -d rag_core -v ON_ERROR_STOP=1 -Atc "SELECT marker FROM t02_persistence_fixture WHERE id = 1;"
docker compose exec -T api python /tmp/t02_qdrant_fixture.py verify
docker compose --profile local-storage run --rm minio-bootstrap
```

Ba command exit **0**. Output thật lần lượt:

```text
rag-core-t02-persistence-v1
rag-core-t02-persistence-v1
Name      : t02-persistence.txt
Date      : 2026-09-16 03:20:12 UTC
Size      : 28 B
ETag      : f9eb58fcfbb8e28513335e6d2fcc6b52-1
Type      : file
Checksum  : CRC32C:TNGhSQ==-1
```

Smoke sau restart exit **0**. Actual = expected: named volumes giữ fixture. Không chạy `down -v`, không xóa volume/source.

### D1–D6, quality, docs và limitations

- **D1:** dependency T01 notes/commit đã đọc; final `git diff --check`/scope review và changed paths ghi ở staged review dưới. Không sửa prompt corpus/AGENTS/plan semantics/T03.
- **D2:** final commands riêng: `uv run ruff check .` exit **0**, `All checks passed!`; `uv run mypy src` exit **0**, `Success: no issues found in 6 source files`; `uv run pytest tests/unit` exit **0**, 7 tests PASS trên Python 3.12.4. Settings regression chứng minh empty optional secret path thành `None`.
- **D3:** hai DoD và outage/persistence dùng service thật; output/cwd/exit/config/images ở trên. Không mock integration, provider live hoặc GPU claim.
- **D4:** README/RUNBOOK có prerequisites/bootstrap/start/wait/stop/ports/health/secrets/persistence boundary; task/handoff/summary cập nhật. Final `uv run python scripts/check_docs.py` exit **0**: `PASS UTF-8/nonempty Markdown: 8 files`, `PASS internal links/anchors: 139`, `PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic`, `DOCUMENTATION CHECK: PASS`.
- **D5:** `.dockerignore` chặn `.env*` trừ example, key/pem/cache/corpus/runtime; `.gitignore` chặn `.local`; secret values không in/stage. `uv lock --check` exit **0**, `Resolved 72 packages in 1ms`. Không business migration/contract breaking change.
- **D6:** stage explicit paths và completion commit `feat(T02): add local Docker infrastructure`; actual hash chỉ trả sau commit.
- **Known limits:** API chỉ health; MinIO chưa là API readiness dependency vì storage adapter thuộc T11. MinIO/MC là pinned historical community releases dùng local simulation. Chưa schema/auth/business routes, worker/dispatcher/inference, provider/GPU/load/cloud/Scarlet.

Final scope/hygiene review trước stage:

- Command `git diff --check; git status --short; git diff --stat; git var GIT_AUTHOR_IDENT`: exit **0**. `git diff --check` stdout rỗng; status chỉ có 21 T02 candidate paths trong allowed scope; Git author đã cấu hình sẵn `Vincent <zayncaster24@gmail.com>`. Warning global ignore permission có sẵn, không sửa config.
- Ignore assertion command `$paths=@('.env','.local/secrets/postgres_password','.local/secrets/minio_root_user','.local/secrets/minio_root_password'); $matches=@(git check-ignore -v --no-index -- $paths); $matches; if($matches.Count -ne $paths.Count){Write-Error "Expected 4 ignored secret paths, got $($matches.Count)"; exit 1}; Write-Output 'PASS all local secret paths ignored'`: exit **0**, 4/4 match `.gitignore`, output final `PASS all local secret paths ignored`.
- Explicit 21-file size/tracking/secret-example review: exit **0**, output `PASS candidate_files=21 files_over_1MiB=0 local_secret_paths_tracked=0 secret_example_values=0`. Prompt source check exit **0**, SHA-256 `7EC6E58AE4C24DB27AF4320BCB30222BBF2B67961D99C62980CEA4410AEE2C46`, raw blob `81ab3c77530722968d847391d8095284f1a874a9` unchanged.

<a id="h-t02-a03"></a>
## H-T02-A03 — Phase 0 / T02 / attempt T02-A03

### Phục hồi, identity và baseline

- Started: 2026-09-16 16:51 +07:00; worker `/root/t02_a03`, model `gpt-5.6-sol`, effort `xhigh`, fresh context `fork_turns="none"`. Runtime đọc từ thread `01a0a9a0-7c47-7b43-bd6c-09b38a8303a8`, chỉ chọn model/effort/cwd/turn ID, không dump prompt/reasoning/auth.
- A02 chưa COMPLETE: không có completion commit T02. Orchestrator báo khi người dùng continue, lifecycle chỉ còn root; nguyên nhân A02 không còn active chưa xác định. Không gán quota/crash; quota event chỉ thuộc A01. Giữ nguyên source và toàn evidence A02.
- Đã đọc AGENTS; T02 + toàn execution notes T01; P01/P02/P12/P13/P14/P15; current/T01/A01/A02 handoffs, implementation-summary, README/RUNBOOK, toàn diff và newfiles T02 trước implementation. T01 COMPLETE đã được Orchestrator nghiệm thu.
- Allowed files/baseline: modified `.env.example`, `.gitignore`, README/RUNBOOK, `docs/{tasks,handoffs,implementation-summary}.md`, `pyproject.toml`, `uv.lock`, settings và settings tests; untracked `.dockerignore`, `compose.yaml`, `docker/api.Dockerfile`, ba helpers bootstrap/smoke/Qdrant, ba API files và health tests = **21 files**. Ignored `.local/secrets`, caches, `.venv` giữ nguyên; không đọc giá trị secret. T02 được trả về IN_PROGRESS trước review/verification.
- CWD mọi command A03: `C:\Users\Admin\Documents\GitHub\rag-core`; provider/model/GPU/live external không áp dụng T02, integration dùng local services thật. A03 sẽ kế thừa outage/persistence A02 nếu source/config liên quan không đổi, ghi riêng phần kiểm current.

Baseline command nguyên văn `git status --short; git branch --show-current; git rev-parse HEAD`: exit **0**; output status đúng paths ở trên, branch/HEAD thật:

```text
main
ff8069abfd2e41fb9618eb7d35fa22bf220a39d6
```

Warning global ignore permission có sẵn, không sửa global config. Runtime metadata command nguyên văn:

```powershell
$taskThreadId = $env:CODEX_THREAD_ID; Write-Output "thread_id=$taskThreadId"; if ($taskThreadId) { rg --files C:/Users/Admin/.codex/sessions -g "*$taskThreadId*" }
$runtimePath='C:/Users/Admin/.codex/sessions/2026/09/16/rollout-2026-09-16T16-51-02-01a0a9a0-7c47-7b43-bd6c-09b38a8303a8.jsonl'; Get-Content -Encoding UTF8 -LiteralPath $runtimePath | ForEach-Object { $record=$_ | ConvertFrom-Json; if($record.type -eq 'turn_context'){ [pscustomobject]@{model=$record.payload.model;effort=$record.payload.effort;cwd=$record.payload.cwd;turn_id=$record.payload.turn_id} | ConvertTo-Json -Compress } }
```

Cả hai exit **0**; output metadata thật:

```text
thread_id=01a0a9a0-7c47-7b43-bd6c-09b38a8303a8
{"model":"gpt-5.6-sol","effort":"xhigh","cwd":"C:\\Users\\Admin\\Documents\\GitHub\\rag-core","turn_id":"01a0a9a0-7cc9-7031-adb0-83aed0d1bcdf"}
```

Expected = actual: model/effort/cwd đúng contract và thread/turn mới.

### Current Docker, DoD-1 và image/source

- Orchestrator báo preflight mới exit **1** do pipe Linux daemon không tồn tại: `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine; check if the path is correct and if the daemon is running: open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.` Đây là observation root, không phải lỗi A03/không phải quota. A03 kiểm lại daemon đã online, không chạy Start-Process, không đổi context/reset hoặc xóa volumes.
- Command nguyên văn `docker context show; docker context ls; Get-Process -Name 'Docker Desktop','com.docker.backend' -ErrorAction SilentlyContinue | Select-Object ProcessName,Id; Test-Path -LiteralPath 'C:\Program Files\Docker\Docker\Docker Desktop.exe'; docker version --format '{{.Server.Version}}'`: exit **0**. Output excerpt thật: `desktop-linux`, context `desktop-linux *` dùng `npipe:////./pipe/dockerDesktopLinuxEngine`, `29.5.2`, Docker Desktop/backend process list và `True`. Actual daemon hoạt động đúng expected; không cần thay đổi trạng thái Desktop.
- `docker compose config --quiet`: exit **0**, stdout rỗng; không render secret/config đầy đủ.
- Current image ban đầu đã khớp SHA-256 cả 6 Python source files, bao gồm `env_ignore_empty=True` ở settings cuối. A03 vẫn chạy lại DoD build/start sau cập nhật README/RUNBOOK evidence links để image mang đúng metadata/source cuối.

Command build/start nguyên văn:

```powershell
docker compose --profile local-storage up -d --build 2>&1 | Tee-Object -FilePath '.local/t02-a03-build.redacted.log'; $composeExit=$LASTEXITCODE; exit $composeExit
```

Exit **0** (exec session `87790` hoàn tất); full build log ignored tại `.local/t02-a03-build.redacted.log`, đã review không secret/private content. Build output đầu có PowerShell `NativeCommandError` wrapper vì Docker ghi progress vào stderr; process thực exit 0, không coi wrapper là lỗi build. Output excerpt thật:

```text
#15 0.352 Using CPython 3.12.13 interpreter at: /usr/local/bin/python3
#15 0.381 Resolved 72 packages in 13ms
#15 1.343 Installed 27 packages in 198ms
#18 exporting manifest list sha256:64673d7032b879f4a76bcb65b48766fcbd29165802343f664f7133f3e69bba42 0.0s done
 Image rag-core-api:t02 Built
 Container rag-core-api-1 Recreated
 Container rag-core-redis-1 Healthy
 Container rag-core-qdrant-1 Healthy
 Container rag-core-postgres-1 Healthy
 Container rag-core-minio-1 Healthy
 Container rag-core-api-1 Started
 Container rag-core-minio-bootstrap-1 Started
```

- `docker compose --profile local-storage up -d --wait postgres qdrant redis api minio`: exit **0**, output thật báo `Container rag-core-postgres-1 Healthy`, `Container rag-core-minio-1 Healthy`, `Container rag-core-api-1 Healthy`, `Container rag-core-qdrant-1 Healthy`, `Container rag-core-redis-1 Healthy` trong final wait; expected đủ năm services healthy đạt.
- `powershell.exe -NoProfile -ExecutionPolicy Bypass -File '.\scripts\smoke_local.ps1'`: exit **0**, output thật:

```text
PASS /health/live status=ok
PASS /health/ready status=ready components=postgres,redis,qdrant
```

Post-build command image/source SHA-256 nguyên văn (không đọc secret; Python chỉ hashes source code đã track):

```powershell
$hashScript = @'
import hashlib
import json
from pathlib import Path
import rag_core
root = Path(rag_core.__file__).parent
print(json.dumps({path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest().upper() for path in sorted(root.rglob("*.py"))}, sort_keys=True))
'@
$imageHashOutput = $hashScript | docker compose exec -T api python -
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$imageHashes = $imageHashOutput | ConvertFrom-Json
$sourceRoot = (Resolve-Path -LiteralPath 'src/rag_core').Path
$sourceFiles = @(Get-ChildItem -LiteralPath $sourceRoot -Recurse -File -Filter '*.py')
if ($sourceFiles.Count -ne @($imageHashes.PSObject.Properties).Count) { throw 'Image/source Python file count differs' }
foreach ($sourceFile in $sourceFiles) {
    $relativePath = $sourceFile.FullName.Substring($sourceRoot.Length + 1).Replace('\','/')
    $sourceHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $sourceFile.FullName).Hash
    $imageHash = $imageHashes.$relativePath
    if ($sourceHash -ne $imageHash) { throw "Image/source SHA256 differs: $relativePath" }
}
Write-Output "PASS image/source SHA256 equality: $($sourceFiles.Count) Python files, including final settings.py"
docker image inspect rag-core-api:t02 --format '{{.Id}} {{.Created}} {{.Config.User}}'
$tagImageId = (docker image inspect rag-core-api:t02 --format '{{.Id}}').Trim()
$containerImageId = (docker inspect rag-core-api-1 --format '{{.Image}}').Trim()
if ($tagImageId -ne $containerImageId) { throw 'Running container differs from final image tag' }
Write-Output "PASS running API container image matches tag: $containerImageId"
```

Exit **0**; output thật:

```text
PASS image/source SHA256 equality: 6 Python files, including final settings.py
sha256:64673d7032b879f4a76bcb65b48766fcbd29165802343f664f7133f3e69bba42 2026-09-16T09:54:55.686026004Z 10001:10001
PASS running API container image matches tag: sha256:64673d7032b879f4a76bcb65b48766fcbd29165802343f664f7133f3e69bba42
```

DoD-1 **PASS**: config/up-build/health hiện tại thật; readiness code không đổi A02 và Redis outage 200/503/200 kế thừa [H-T02-A02](#h-t02-a02), không gọi là A03 đã chạy outage lại.

### DoD-2 current status, inspect và fixture còn nguyên

Command nguyên văn `docker compose ps; docker compose --profile local-storage ps --all; docker compose exec -T postgres psql -U rag_core -d rag_core -v ON_ERROR_STOP=1 -Atc "SELECT marker FROM t02_persistence_fixture WHERE id = 1;"; docker compose logs --no-color --tail 12 minio-bootstrap`: exit **0**; ps thực báo API mới `Up 40 seconds (healthy)`, PG/Qdrant/Redis/MinIO `Up 3 minutes (healthy)`, bootstrap `Exited (0) 39 seconds ago`; cả ps commands hiển thị đúng internal PG 5432/Qdrant 6333-6334/Redis 6379 và loopback API 8000/MinIO 9000-9001.

Output excerpt thật của PG readonly và MinIO metadata (prefix log giữ nguyên):

```text
rag-core-t02-persistence-v1
minio-bootstrap-1  | Name      : t02-persistence.txt
minio-bootstrap-1  | Date      : 2026-09-16 03:20:12 UTC
minio-bootstrap-1  | Size      : 28 B
minio-bootstrap-1  | ETag      : f9eb58fcfbb8e28513335e6d2fcc6b52-1
minio-bootstrap-1  | Type      : file
minio-bootstrap-1  | Checksum  : CRC32C:TNGhSQ==-1
```

Qdrant helper commands chạy riêng, vì API recreated mất `/tmp` helper cũ (không seed):

```powershell
docker compose cp scripts/t02_qdrant_fixture.py api:/tmp/t02_qdrant_fixture.py
docker compose exec -T api python /tmp/t02_qdrant_fixture.py verify
```

Exit mỗi command **0**; output thật lần lượt:

```text
 rag-core-api-1 Copying scripts/t02_qdrant_fixture.py to rag-core-api-1:/tmp/t02_qdrant_fixture.py
 rag-core-api-1 Copied scripts/t02_qdrant_fixture.py to rag-core-api-1:/tmp/t02_qdrant_fixture.py
rag-core-t02-persistence-v1
```

Inspect nguyên văn, chỉ output image/health/ports/mount type+name+destination; không output env/secret source/value:

```powershell
$names=@('rag-core-api-1','rag-core-postgres-1','rag-core-qdrant-1','rag-core-redis-1','rag-core-minio-1'); $items=docker inspect $names | ConvertFrom-Json; if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}; foreach($item in $items){$ports=@(); foreach($property in $item.NetworkSettings.Ports.PSObject.Properties){$bindings=$property.Value; if($null -eq $bindings){$ports += "$($property.Name)=internal-only"}else{foreach($binding in $bindings){$ports += "$($property.Name)=$($binding.HostIp):$($binding.HostPort)"}}}; $mounts=@($item.Mounts | ForEach-Object {"$($_.Type):$($_.Name)->$($_.Destination)"}); [pscustomobject]@{Name=$item.Name.TrimStart('/'); Image=$item.Config.Image; Health=$item.State.Health.Status; Ports=($ports -join ', '); Mounts=($mounts -join ', ')} | Format-List}
```

Exit **0**. Output excerpt thật (bỏ blank lines và image dài; full pins nằm ở Compose/source và A02 evidence):

```text
Name   : rag-core-api-1
Image  : rag-core-api:t02
Health : healthy
Ports  : 8000/tcp=127.0.0.1:8000
Mounts : bind:->/run/secrets/postgres_password

Name   : rag-core-postgres-1
Health : healthy
Ports  : 5432/tcp=internal-only
Mounts : bind:->/run/secrets/postgres_password, volume:rag-core_postgres_data->/var/lib/postgresql/data

Name   : rag-core-qdrant-1
Health : healthy
Ports  : 6333/tcp=internal-only, 6334/tcp=internal-only
Mounts : volume:rag-core_qdrant_data->/qdrant/storage

Name   : rag-core-redis-1
Health : healthy
Ports  : 6379/tcp=internal-only
Mounts : volume:rag-core_redis_data->/data

Name   : rag-core-minio-1
Health : healthy
Ports  : 9000/tcp=127.0.0.1:9000, 9001/tcp=127.0.0.1:9001
Mounts : bind:->/run/secrets/minio_root_password, bind:->/run/secrets/minio_root_user,
         volume:rag-core_minio_data->/data
```

DoD-2 **PASS**: ps/inspect/current fixture hiện tại đạt; controlled restart trước/sau với nguyên fixture kế thừa A02. A03 không restart lần nữa vì persistence source/config không đổi; chỉ kiểm hiện fixture còn nguyên, không reseed PG/Qdrant. Build chạy bootstrap idempotent và MinIO timestamp/size/ETag không đổi. Không `down -v`, reset/xóa volume/source.

### D2/D4 quality và docs commands hiện tại

Mỗi command dưới là một tool/shell invocation riêng; nguyên văn có cache assignments trong workspace. Expected mọi check PASS, lock không drift, Python 3.12.

- Command `$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'; uv sync --locked --group dev --group api`: exit **0**.
- Command `$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'; uv run ruff check .`: exit **0**.
- Command `$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'; uv run mypy src`: exit **0**.
- Command `$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'; uv run pytest tests/unit`: exit **0**.
- Command `$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'; uv lock --check`: exit **0**.
- Command `$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'; uv run python scripts/check_docs.py`: exit **0**.

Output thật tương ứng (sync, Ruff, mypy, pytest excerpt, lockcheck, final docs trước append evidence này):

```text
Resolved 72 packages in 2ms
Checked 39 packages in 101ms
All checks passed!
Success: no issues found in 6 source files
platform win32 -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0
collected 7 items
tests\unit\test_health.py ...                                            [ 42%]
tests\unit\test_settings.py ....                                         [100%]
============================== 7 passed in 0.80s ==============================
Resolved 72 packages in 0.95ms
PASS UTF-8/nonempty Markdown: 8 files
PASS internal links/anchors: 145
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```

Tests có injection deterministic chỉ chứng minh unit route/config behavior; Docker smoke/outage/persistence mới là integration thật. Không gọi unit mock là live. Không provider/LLM/model/GPU/cloud claim.

### D1/D5 scope, secrets, lock source và PowerShell

Đã review toàn diff/source/newfiles baseline; A03 chỉ thay README/RUNBOOK và ba sổ docs, không thay source/test/config candidate A02. Không migration/index/schema nghiệp vụ; settings yêu cầu QDRANT_URL và blank optional path giữ contract README/RUNBOOK từ A02.

Command hygiene nguyên văn:

```powershell
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new(); git diff --check; git diff --name-only; git status --short; git var GIT_AUTHOR_IDENT; $candidate=@('.env.example','.gitignore','.dockerignore','README.md','RUNBOOK.md','docs/handoffs.md','docs/implementation-summary.md','docs/tasks.md','pyproject.toml','uv.lock','compose.yaml','docker/api.Dockerfile','src/rag_core/config/settings.py','src/rag_core/api/__init__.py','src/rag_core/api/app.py','src/rag_core/api/health.py','tests/unit/test_settings.py','tests/unit/test_health.py','scripts/bootstrap_local.ps1','scripts/smoke_local.ps1','scripts/t02_qdrant_fixture.py'); $large=@($candidate | ForEach-Object {Get-Item -LiteralPath $_} | Where-Object Length -gt 1048576); $trackedSecrets=@(git ls-files -- .env .local); $nonEmpty=@(rg -n '^(QDRANT_API_KEY|DEEPSEEK_API_KEY|ANTHROPIC_API_KEY|STORAGE_ACCESS_KEY_ID|STORAGE_SECRET_ACCESS_KEY|ADMIN_SECRET)=.+' -- .env.example); if($large.Count -ne 0 -or $trackedSecrets.Count -ne 0 -or $nonEmpty.Count -ne 0){throw 'Scope/secret/size review failed'}; Write-Output "PASS candidate_files=$($candidate.Count) files_over_1MiB=$($large.Count) local_secret_paths_tracked=$($trackedSecrets.Count) secret_example_values=$($nonEmpty.Count)"; $path='corpus-documents/Codex Prompt – Build RAG Evaluation Corpus.md'; $raw=(git hash-object --no-filters -- "$path").Trim(); $sha=(Get-FileHash -Algorithm SHA256 -LiteralPath $path).Hash; if($raw -ne '81ab3c77530722968d847391d8095284f1a874a9' -or $sha -ne '7EC6E58AE4C24DB27AF4320BCB30222BBF2B67961D99C62980CEA4410AEE2C46'){throw 'Prompt bytes changed'}; Write-Output "PASS original prompt blob=$raw SHA256=$sha"; $paths=@('.env','.local/secrets/postgres_password','.local/secrets/minio_root_user','.local/secrets/minio_root_password','.local/t02-a03-build.redacted.log'); $matches=@(git check-ignore -v --no-index -- $paths); $matches; if($matches.Count -ne $paths.Count){throw 'Ignored secret/log path count differs'}; Write-Output 'PASS all local secret/log paths ignored'
```

Exit **0**; `git diff --check` stdout rỗng, status đúng baseline 21 paths, author đã cấu hình sẵn (không sửa identity). Output excerpt thật:

```text
PASS candidate_files=21 files_over_1MiB=0 local_secret_paths_tracked=0 secret_example_values=0
PASS original prompt blob=81ab3c77530722968d847391d8095284f1a874a9 SHA256=7EC6E58AE4C24DB27AF4320BCB30222BBF2B67961D99C62980CEA4410AEE2C46
.gitignore:22:.env	.env
.gitignore:32:/.local/	.local/secrets/postgres_password
.gitignore:32:/.local/	.local/secrets/minio_root_user
.gitignore:32:/.local/	.local/secrets/minio_root_password
.gitignore:32:/.local/	.local/t02-a03-build.redacted.log
PASS all local secret/log paths ignored
```

Command secret-name/lock-source/helper parse nguyên văn:

```powershell
Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz'; $candidate=@('.env.example','.gitignore','.dockerignore','README.md','RUNBOOK.md','docs/handoffs.md','docs/implementation-summary.md','docs/tasks.md','pyproject.toml','uv.lock','compose.yaml','docker/api.Dockerfile','src/rag_core/config/settings.py','src/rag_core/api/__init__.py','src/rag_core/api/app.py','src/rag_core/api/health.py','tests/unit/test_settings.py','tests/unit/test_health.py','scripts/bootstrap_local.ps1','scripts/smoke_local.ps1','scripts/t02_qdrant_fixture.py'); $matches=@(rg -n -i '(api[_-]?key|secret|password|bearer|private[_-]?key|access[_-]?key|token)' -- $candidate); Write-Output "Sensitive-name matches reviewed in source/docs: $($matches.Count)"; $unexpected=@(rg '^source = ' uv.lock | Sort-Object -Unique | Where-Object {$_ -ne 'source = { registry = "https://pypi.org/simple" }' -and $_ -ne 'source = { editable = "." }'}); if($unexpected.Count -ne 0){throw 'Unexpected lock source'}; Write-Output 'PASS uv.lock sources: local editable project + PyPI registry only'; $parsedScripts=@('scripts/bootstrap_local.ps1','scripts/smoke_local.ps1'); foreach($scriptPath in $parsedScripts){$parseTokens=$null;$parseErrors=$null; [void][System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path -LiteralPath $scriptPath).Path,[ref]$parseTokens,[ref]$parseErrors); if($parseErrors.Count -ne 0){throw "PowerShell parse failed: $scriptPath"}}; Write-Output 'PASS PowerShell helpers parse: 2 files'
```

Exit **0**; sensitive-name matches kiểm thủ công trên nội dung đã đọc, chỉ docs/placeholders/secret mounts và synthetic unit credentials, không real key/value. Output thật:

```text
2026-09-16 16:56:48 +07:00
Sensitive-name matches reviewed in source/docs: 112
PASS uv.lock sources: local editable project + PyPI registry only
PASS PowerShell helpers parse: 2 files
```

### D1–D6 và kết luận trước completion commit

- **D1 PASS:** dependency T01 notes/actual commit đã đọc; diff check/scope baseline đúng 21 T02 files; prompt nguyên byte, AGENTS/plan/T03 không đổi.
- **D2 PASS:** locked dev/api sync, Ruff, strict mypy và 7 unit tests hiện tại; PowerShell helpers parse PASS.
- **D3 PASS:** từng DoD-1/2 current command/observation thật ở trên; outage và controlled restart inherited A02 với source/config không đổi.
- **D4 PASS:** README/RUNBOOK giữ quickstart VERIFIED/DESIGNED và thêm A03 evidence boundary; tasks/handoffs/summary ghi recovery, identity, outputs, interfaces/limits và resolver; final docs check sau append/restage ghi ở D6 dưới.
- **D5 PASS:** review source/lock/image pins, secrets/ignore/scope/size/prompt; không raw corpus/weights/cache/private data. Không business migration; QDRANT_URL config addition và blank optional value behavior có RUNBOOK/tests.
- **D6:** stage explicit 21 paths, cached check/docs/commit kiểm ở phần dưới; subject `feat(T02): add local Docker infrastructure`; task COMPLETE chỉ hợp lệ sau commit thành công và Orchestrator review. Actual hash/output post-commit trả root, không tự nhét hash vào commit.
- **Limitations/blockers:** không còn blocker T02 cần user input. A02 lifecycle nguyên nhân chưa xác định và đã ghi trung thực. API chỉ health; MinIO chưa là API readiness dependency trước T11; chưa business schema/auth/routes/worker/dispatcher/inference/provider/GPU/load/cloud/Scarlet. Outage/restart A03 kế thừa evidence A02, không claim chạy lại.
- **Next:** completion commit + Orchestrator review rồi worker/context mới T03; A03 kết thúc và không nhận task/retry tiếp.

### D6 staged review và completion commit boundary

Stage command nguyên văn:

```powershell
git add -- .env.example .gitignore .dockerignore README.md RUNBOOK.md docs/handoffs.md docs/implementation-summary.md docs/tasks.md pyproject.toml uv.lock compose.yaml docker/api.Dockerfile src/rag_core/config/settings.py src/rag_core/api/__init__.py src/rag_core/api/app.py src/rag_core/api/health.py tests/unit/test_settings.py tests/unit/test_health.py scripts/bootstrap_local.ps1 scripts/smoke_local.ps1 scripts/t02_qdrant_fixture.py
```

Exit **0**, stdout rỗng. Cached review command nguyên văn:

```powershell
git diff --cached --check; if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}; git diff --cached --name-status; git diff --cached --stat; $stagedPaths=@(git diff --cached --name-only); if($stagedPaths.Count -ne 21){throw "Expected 21 staged T02 files, found $($stagedPaths.Count)"}; $forbidden=@($stagedPaths | Where-Object {$_ -match '^(.local/|.env$|corpus-documents/|AGENTS.md$|docs/plan.md$|.venv/|.uv-cache/)'}); if($forbidden.Count -ne 0){throw 'Forbidden staged path'}; Write-Output "PASS staged T02 scope: $($stagedPaths.Count) files, no forbidden artifacts"; git status --short
```

Exit **0**; cached whitespace check stdout rỗng. Output thật name-status và scope assertion (stat đầy đủ không lặp trong excerpt):

```text
A	.dockerignore
M	.env.example
M	.gitignore
M	README.md
M	RUNBOOK.md
A	compose.yaml
A	docker/api.Dockerfile
M	docs/handoffs.md
M	docs/implementation-summary.md
M	docs/tasks.md
M	pyproject.toml
A	scripts/bootstrap_local.ps1
A	scripts/smoke_local.ps1
A	scripts/t02_qdrant_fixture.py
A	src/rag_core/api/__init__.py
A	src/rag_core/api/app.py
A	src/rag_core/api/health.py
M	src/rag_core/config/settings.py
A	tests/unit/test_health.py
M	tests/unit/test_settings.py
M	uv.lock
 21 files changed, 1175 insertions(+), 46 deletions(-)
PASS staged T02 scope: 21 files, no forbidden artifacts
```

Status chỉ staged đúng 21 paths, không unstaged/untracked path. Global ignore permission warning giữ nguyên, không chỉnh global config. Prompt corpus không thuộc staged changes và đã hash-check nguyên bytes ở D5.

Docs check sau append A03 evidence/task/summary, command nguyên văn `$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'; uv run python scripts/check_docs.py`: exit **0**, output thật:

```text
PASS UTF-8/nonempty Markdown: 8 files
PASS internal links/anchors: 146
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```

Chỉ ba sổ docs được restage explicit sau bổ sung staged-review/current completion proposal này; cached whitespace/docs checks chạy lại trước commit. Không code/config/test thay đổi sau final Docker image/source proof và quality PASS.

Theo P14, `COMPLETE` trong nội dung completion commit là đề nghị đóng task, chỉ có hiệu lực khi commit thành công và Orchestrator review. Completion command kế tiếp `git commit -m "feat(T02): add local Docker infrastructure"`; actual exit/output/hash/time và post-commit git status trả trong worker report, không tạo vòng self-reference/amend để ghi hash vào chính commit. Nếu commit fail, task chưa COMPLETE và phải báo root với reproduction.

<a id="h-t03-a01"></a>
## H-T03-A01 — Phase 0 / T03 / attempt T03-A01 — Recovery record

- **Status:** attempt kết thúc do runtime quota, chưa COMPLETE/commit. A02 append record này từ recovery brief của Orchestrator; không phải evidence shell đã chạy trong A01.
- **Runtime:** worker `/root/t03_a01`, `gpt-5.6-sol`/`xhigh`, fresh context; started 2026-09-16 17:05 +07:00, turn `01a0a9ad-1977-7a52-a89d-5c49faa92f74`. Root đã kiểm lifecycle không còn A01 trước spawn A02.
- **Runtime event nguyên văn:** `Agent errored: You've hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/codex/settings/usage to purchase more credits or try again at 9:49 PM.` Đây là runtime event, không shell output; không suy ngày/giờ kết thúc từ “9:49 PM”.
- **Candidate/last good:** HEAD T02 `851ff1d10b49b6a4d7ae7e1756f2c2a1b8562e96`; 16 dirty/untracked T03 files: README/RUNBOOK/tasks/handoffs, pyproject/lock, 3 JSON artifacts, exporter, 5 contract modules, contract tests. Summary chưa ghi T03; checkpoint/links stale. Không có actual shell logs A01 được recovery brief cung cấp, nên không fabricate command/exit/output.
- **Reports only:** A01 messages báo Ruff PASS, mypy 11 source PASS, 7 unit PASS, 83 contract PASS và export 13 designed operations/2 served health/48 schemas/37 synthetic examples PASS. Những messages này không dùng làm current DoD evidence; A02 chạy checks mới và lưu output thật riêng.
- **Candidate decisions reported/reviewed:** Default dump bỏ document_ids=None; SSE whitespace delta hợp lệ; bbox finite nonnegative floats; validation qua OpenAPI model + Draft2020-12/UUID format checker + Pydantic/roundtrip. JSON roundtrip fixture tránh shared-object deepcopy làm evidence/done cùng thay đổi. A02 review implementation trước nghiệm thu.
- **Next:** fresh worker T03-A02 review/actual checks/docs/explicit completion commit. Không đổi semantics hoặc gate để vượt quota.

<a id="h-t03-a02"></a>
## H-T03-A02 — Phase 0 / T03 / attempt T03-A02

### Identity, recovery, baseline và review

- Worker `/root/t03_a02`, `gpt-5.6-sol`/`xhigh`, fresh context `fork_turns="none"` theo spawn/runtime verification của Orchestrator; started 2026-09-17 11:51 +07:00. Không spawn agent/chạy task tiếp. Local repo không có `.codex`/`.agents` turn_context metadata; read-only `rg --files --hidden .codex .agents -g '*context*' -g '*runtime*' -g '*session*'` báo hai directory không tồn tại, không đọc session/auth ngoài repo hoặc tự đổi model. Runtime verification do Orchestrator cung cấp, không gọi prompt tự đổi model.
- A01 đã kết thúc do quota, không writer active khác. Event/report boundary/last-good ở [H-T03-A01](#h-t03-a01); không fabricate A01 shell evidence.
- Đã đọc AGENTS, T03/T01/T02 toàn notes; P01/P03/P04/P05/P06/P07/P09/P13; handoffs/implementation-summary/README/RUNBOOK và source/test/config candidate trước mutation. T01/T02 COMPLETE được root nghiệm thu.
- CWD mọi commands dưới đây: `C:\Users\Admin\Documents\GitHub\rag-core`. Không cần DSN/secrets/Docker services/provider/model/GPU cho T03. Config: projectPython3.12.*, uv0.11.16, CPython3.12.4, dev+api locked groups; no skip/mock thay live. Unit health có injection; exporter inspect factory không probe service; contract/SSE chỉ structural/logical checks.
- Baseline command nguyên văn `git status --short; git branch --show-current; git rev-parse HEAD`, exit **0**, output thật:

```text
warning: unable to access 'C:\Users\Admin/.config/git/ignore': Permission denied
warning: unable to access 'C:\Users\Admin/.config/git/ignore': Permission denied
 M README.md
 M RUNBOOK.md
 M docs/handoffs.md
 M docs/tasks.md
 M pyproject.toml
 M uv.lock
?? docs/api/
?? scripts/export_openapi.py
?? src/rag_core/contracts/
?? tests/contract/
main
851ff1d10b49b6a4d7ae7e1756f2c2a1b8562e96
```

Exact untracked inventory read qua `git ls-files --others --exclude-standard` (**0**): 3 docs/api JSON, exporter, 5 contracts modules, `tests/contract/test_api_schema.py`; tổng 16 candidate files. Completion allowed scope thêm summary thành 17 files, không file lạ. Git ignore permission warning baseline giữ nguyên; không sửa global config.

A02 review candidate v1/SSE/OpenAPI/examples/exporter/test và dev dependency/lock; không có code blocker cần đổi semantics, giữ source/test/config. Contracts cấm extra client identity/policy/system roles, quy định subsets/languages/limits/history metadata/locators/error/evidence links; sequence kiểm logical complete trace, không runtime stream. App health source/config giữ nguyên T02, không build/re-run integration liên quan.

### D2 — Locked env, quality và unit regression

Mỗi command riêng, exit **0**, expected = clean locked CPython 3.12 environment và quality/unit PASS, actual như output. Log `.local/` đã ignore và kiểm không private content; không cần redaction giá trị (filename `.redacted.log` là convention, không claim có credential đã được đọc).

Sync command nguyên văn:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'; uv sync --locked --group dev --group api 2>&1 | Tee-Object -FilePath .local/t03-a02-sync.redacted.log; exit $LASTEXITCODE
```

Output excerpt thật; full output `.local/t03-a02-sync.redacted.log`:

```text
uv : Resolved 77 packages in 2ms
Checked 44 packages in 168ms
```

PowerShell 5 redirection format stderr `Resolved` thành NativeCommandError với command source line/category metadata; actual uv exit 0, không dependency failure. Các checks sau dùng `ForEach-Object { $_.ToString() }` giữ native output string trong log.

Interpreter/lock command nguyên văn:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'; uv --version; uv run python --version; uv lock --check; exit $LASTEXITCODE
```

Output thật:

```text
uv 0.11.16 (135a36367 2026-05-21 x86_64-pc-windows-msvc)
Python 3.12.4
Resolved 77 packages in 0.88ms
```

Ruff command nguyên văn:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'; uv run ruff check . 2>&1 | ForEach-Object { $_.ToString() } | Tee-Object -FilePath .local/t03-a02-ruff.redacted.log; exit $LASTEXITCODE
```

Output thật `All checks passed!`.

Mypy command nguyên văn:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'; uv run mypy src 2>&1 | ForEach-Object { $_.ToString() } | Tee-Object -FilePath .local/t03-a02-mypy.redacted.log; exit $LASTEXITCODE
```

Output thật `Success: no issues found in 11 source files`.

Unit command nguyên văn:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'; uv run pytest tests/unit 2>&1 | ForEach-Object { $_.ToString() } | Tee-Object -FilePath .local/t03-a02-unit.redacted.log; exit $LASTEXITCODE
```

Output excerpt thật; full log `.local/t03-a02-unit.redacted.log`:

```text
platform win32 -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0
configfile: pyproject.toml
plugins: anyio-4.15.1, asyncio-1.4.0
collected 7 items

tests\unit\test_health.py ...                                            [ 42%]
tests\unit\test_settings.py ....                                         [100%]

============================== 7 passed in 1.20s ==============================
```

<a id="h-t03-a02-dod1"></a>
### DoD-1 — Domain/subset/history/language/limits/locator/error/SSE contracts

Command nguyên văn:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'; uv run pytest tests/contract/test_api_schema.py 2>&1 | ForEach-Object { $_.ToString() } | Tee-Object -FilePath .local/t03-a02-contract.redacted.log; exit $LASTEXITCODE
```

Exit **0**, expected = requested validation including client identity/system override refusal, actual **83 PASS, không skip**. Output excerpt thật; full log `.local/t03-a02-contract.redacted.log`:

```text
platform win32 -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Admin\Documents\GitHub\rag-core
configfile: pyproject.toml
plugins: anyio-4.15.1, asyncio-1.4.0
collected 83 items

tests\contract\test_api_schema.py ...................................... [ 45%]
.............................................                            [100%]

============================= 83 passed in 2.06s ==============================
```

Coverage thực: Default subset refusal/serialization; Document required nonempty unique <=50; Multilingual optional subset/EN-VI unique languages; banned privileged body/history roles; question 1/4000/4001 +blank, measured file 100 MiB/1000 pages; history above processing budget accepted +counts/warnings consistency; immutable source fingerprint/no arbitrary URL; invalid locators/ranges/page zero/fake page/nonfinite timing; evidence/citation/reason/unknown usage; complete SSE order/terminal/ID/scope/evidence/early error/whitespace delta/heartbeat; snapshots/examples JSON Schema+Pydantic; all 11 designed business ops framework 404, no stub success. Structural validation không auth/owner/query/provider/live/factual verification.

<a id="h-t03-a02-dod2"></a>
### DoD-2 — Export, snapshot/example validation và served/design boundary

Export command nguyên văn:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'; uv run python scripts/export_openapi.py 2>&1 | ForEach-Object { $_.ToString() } | Tee-Object -FilePath .local/t03-a02-export.redacted.log; exit $LASTEXITCODE
```

Exit **0**, expected = 3 reproducible JSON artifacts, valid schemas/examples and clear health-only served routes, actual = **PASS**. Output thật:

```text
PASS exported docs/api/openapi-v1.designed.json
PASS exported docs/api/openapi.served.json
PASS exported docs/api/examples-v1.json
PASS designed_operations=13 served_health_routes=2 synthetic_examples=37
PASS OpenAPI model + Draft2020-12 schemas=48; examples JSON Schema + Pydantic
CONTRACT EXPORT: PASS (business endpoints unmounted; no runtime query/stream verification)
```

Drift command nguyên văn:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'; uv run python scripts/export_openapi.py --check 2>&1 | ForEach-Object { $_.ToString() } | Tee-Object -FilePath .local/t03-a02-export-check.redacted.log; exit $LASTEXITCODE
```

Exit **0**, expected = existing snapshots equal regenerated machine schemas/examples without writes, actual = **PASS**. Output thật:

```text
PASS checked docs/api/openapi-v1.designed.json
PASS checked docs/api/openapi.served.json
PASS checked docs/api/examples-v1.json
PASS designed_operations=13 served_health_routes=2 synthetic_examples=37
PASS OpenAPI model + Draft2020-12 schemas=48; examples JSON Schema + Pydantic
CONTRACT EXPORT: PASS (business endpoints unmounted; no runtime query/stream verification)
```

Designed health ops `x-served=true`/VERIFIED theo T02; 11 business ops `x-served=false`/DESIGNED chưa mount. Served export inspect factory chỉ `/health/live`/`/health/ready`; không có readiness probe hay HTTP call đến Docker/provider. `/metrics`/admin còn deferred inventory. JSON examples có explicit synthetic design status, không endpoint output. Pydantic additional relational checks ghi RUNBOOK, không nói JSON Schema đủ ownership/factual enforcement.

### D1/D5 — Scope, diff, secrets/artifacts/dependency/prompt review

Read-only diff/identity/time command nguyên văn:

```powershell
git diff --check; if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}; git diff --stat; git diff --name-only; git ls-files --others --exclude-standard; git var GIT_AUTHOR_IDENT; Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz'
```

Exit **0**, whitespace check stdout rỗng; tracked 6 +untracked 10 đúng baseline 16 paths trước summary append, không ngoài allowed 17. Git author sẵn có, không cấu hình identity. Output excerpt thật:

```text
 6 files changed, 157 insertions(+), 33 deletions(-)
Vincent <zayncaster24@gmail.com> 1789620815 +0700
2026-09-17 11:53:35 +07:00
```

CRLF→LF warning xuất hiện vì PowerShell append vào hai docs; final docs normalize UTF-8/LF theo attributes trước staged review, giữ prompt exception nguyên byte. Không sửa code/test/config T02 hoặc plan/AGENTS.

Review command nguyên văn (sensitive matches chỉ đếm, không in credential; source/docs đã đọc thủ công):

```powershell
$candidate=@('README.md','RUNBOOK.md','docs/handoffs.md','docs/tasks.md','docs/implementation-summary.md','pyproject.toml','uv.lock','docs/api/examples-v1.json','docs/api/openapi-v1.designed.json','docs/api/openapi.served.json','scripts/export_openapi.py','src/rag_core/contracts/__init__.py','src/rag_core/contracts/examples.py','src/rag_core/contracts/openapi.py','src/rag_core/contracts/sse.py','src/rag_core/contracts/v1.py','tests/contract/test_api_schema.py'); $items=@($candidate | ForEach-Object {Get-Item -LiteralPath $_}); if(@($items | Where-Object Length -gt 1048576).Count -ne 0){throw 'Large artifact found'}; $changed=@(git diff --name-only); $untracked=@(git ls-files --others --exclude-standard); if(@(($changed+$untracked) | Where-Object {$_ -notin $candidate}).Count -ne 0){throw 'Out-of-scope changed path'}; $suspicious=@(rg -l '(sk-[A-Za-z0-9_-]{20,}|AKIA[A-Z0-9]{16}|-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----)' -- $candidate); if($suspicious.Count -ne 0){throw 'Credential marker found; review without printing values'}; $matches=@(rg -n -i '(api[_-]?key|secret|password|bearer|private[_-]?key|access[_-]?key|token)' -- $candidate); Write-Output "Sensitive-name matches reviewed in source/docs: $($matches.Count)"; $unexpected=@(rg '^source = ' uv.lock | Sort-Object -Unique | Where-Object {$_ -ne 'source = { registry = "https://pypi.org/simple" }' -and $_ -ne 'source = { editable = "." }'}); if($unexpected.Count -ne 0){throw 'Unexpected lock source'}; $promptPath='corpus-documents/Codex Prompt – Build RAG Evaluation Corpus.md'; $raw=(git hash-object --no-filters -- "$promptPath").Trim(); $sha=(Get-FileHash -Algorithm SHA256 -LiteralPath $promptPath).Hash; if($raw -ne '81ab3c77530722968d847391d8095284f1a874a9' -or $sha -ne '7EC6E58AE4C24DB27AF4320BCB30222BBF2B67961D99C62980CEA4410AEE2C46'){throw 'Prompt bytes changed'}; Write-Output "PASS candidate_files=$($items.Count) files_over_1MiB=0 changed_paths=$($changed.Count+$untracked.Count) out_of_scope=0 credential_markers=0"; Write-Output 'PASS uv.lock sources: local editable project + PyPI registry only'; Write-Output "PASS original prompt blob=$raw SHA256=$sha"; $paths=@('.env','.local/secrets/postgres_password','.local/secrets/minio_root_user','.local/secrets/minio_root_password','.local/t03-a02-contract.redacted.log','.uv-cache/placeholder','.uv-python/placeholder'); $ignored=@(git check-ignore -v --no-index -- $paths); $ignored; if($ignored.Count -ne $paths.Count){throw 'Ignored path count differs'}; Write-Output 'PASS all local secret/cache/log paths ignored'
```

Exit **0**, expected = no out-of-scope files/secrets/raw corpus/weights/runtime and prompt bytes unchanged, actual PASS. Output thật (global ignore/CRLF warnings baseline omitted here):

```text
Sensitive-name matches reviewed in source/docs: 172
PASS candidate_files=17 files_over_1MiB=0 changed_paths=16 out_of_scope=0 credential_markers=0
PASS uv.lock sources: local editable project + PyPI registry only
PASS original prompt blob=81ab3c77530722968d847391d8095284f1a874a9 SHA256=7EC6E58AE4C24DB27AF4320BCB30222BBF2B67961D99C62980CEA4410AEE2C46
.gitignore:22:.env	.env
.gitignore:32:/.local/	.local/secrets/postgres_password
.gitignore:32:/.local/	.local/secrets/minio_root_user
.gitignore:32:/.local/	.local/secrets/minio_root_password
.gitignore:32:/.local/	.local/t03-a02-contract.redacted.log
.gitignore:10:.uv-cache/	.uv-cache/placeholder
.gitignore:11:.uv-python/	.uv-python/placeholder
PASS all local secret/cache/log paths ignored
```

Dev-only jsonschema 4.26.0 và 4 transitive packages, PyPI+local editable sources, lock 77; không heavyweight/provider/runtime dependency hoặc migration. Initial v1 DESIGN không có business client cần migration; RUNBOOK future compatibility contract regenerate+checks/client impact ghi cùng schema changes. Không fake author/hook bypass/rebase/reset/amend/push/merge, không original/volume deletes/cloud/Scarlet. History/docs mentions tokens/credentials/secret policies là safe text; JSON UUID/content synthetic, không private data.

### D4 — README/RUNBOOK và implementation memory

README/RUNBOOK có exact export/quality commands, schema/artifact links, R05 matrix mọi business route DESIGNED và health served, R06 subset/history/language/limits/unknown measurements, R07 logical SSE vs transport, R08 format locators/version IDs/lifecycle. Actual evidence links chuyển A02, giữ A01 recovery. Tasks có attempt/files/DoD/D1–D6/commit resolver/limits; summary append Phase 0/T03/A01 recovery và A02 interfaces/decisions/tests/migrations/known limits. Current checkpoint đầu cập nhật khỏi stale A01. Docs check actual output và D6 staged/commit boundary append sau.

### D1–D6 và completion boundary

- **D1 PASS:** dependencies notes/evidence đọc, candidate review và diff check/scope/prompt proof như trên; final staged scope assertion bên dưới.
- **D2 PASS:** locked dev/api sync, Ruff, strict mypy 11 source, 7 unit và 83 contract tests. Không skip hoặc live provider requirement ở T03.
- **D3 PASS:** riêng DoD-1 contract 83 và DoD-2 export+drift 13 ops/2 health/48 schemas/37 examples có commands/cwd/exit/expected/actual ở trên.
- **D4:** docs/summary/evidence cập nhật; docs check current output bên dưới trước completion commit.
- **D5 PASS:** source/test/design/example/dependency diff manual review, sensitive-name/artifact/ignore/lock/prompt proof; không migrations, future contract compatibility trong RUNBOOK.
- **D6:** stage explicit 17 paths/cached review/completion commit theo subject `feat(T03): define versioned API contracts`; COMPLETE chỉ hợp lệ sau actual successful commit +root review. Actual hash trả root post-commit, không self-reference/amend.
- **Blockers/limits:** không blocker T03 cần user input; runtime auth/ownership/current-session/readiness/tokenizers/factual citation/revision checks/provider/transport/cancel/UI chưa implement và không claim VERIFIED. T02 integration không chạy lại khi source/config không đổi. Next: root review rồi worker fresh T04; A02 kết thúc, không nhận task tiếp.

### D4 actual docs check sau append recovery/evidence/summary

Command nguyên văn (chỉ normalize hai docs thuộc scope, prompt không được đụng):

```powershell
$utf8NoBom = New-Object System.Text.UTF8Encoding $false; foreach($docPath in @('docs/handoffs.md','docs/implementation-summary.md')){$absolutePath=(Resolve-Path -LiteralPath $docPath).Path; $docText=[System.IO.File]::ReadAllText($absolutePath,[System.Text.Encoding]::UTF8).Replace("`r`n","`n"); [System.IO.File]::WriteAllText($absolutePath,$docText,$utf8NoBom)}; Write-Output 'PASS appended docs normalized UTF-8 without BOM / LF: 2 files'; $env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'; uv run python scripts/check_docs.py 2>&1 | ForEach-Object { $_.ToString() } | Tee-Object -FilePath .local/t03-a02-docs.redacted.log; exit $LASTEXITCODE
```

Exit **0**, expected = UTF-8/LF, links including recovered H-T03-A01/current H-T03-A02 + task fields/dependencies valid, actual PASS; output thật:

```text
PASS appended docs normalized UTF-8 without BOM / LF: 2 files
PASS UTF-8/nonempty Markdown: 8 files
PASS internal links/anchors: 163
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```

**D4 PASS.** Final execution notes/staged review additions được docs-check lại trước commit ở D6; không chạy lại quality/tests khi source/test/config không thay đổi sau PASS.

<a id="h-t03-a02-d6"></a>
### D6 — Explicit staging, cached review và final commit boundary

Stage command nguyên văn:

```powershell
git add -- README.md RUNBOOK.md docs/tasks.md docs/handoffs.md docs/implementation-summary.md pyproject.toml uv.lock docs/api/examples-v1.json docs/api/openapi-v1.designed.json docs/api/openapi.served.json scripts/export_openapi.py src/rag_core/contracts/__init__.py src/rag_core/contracts/examples.py src/rag_core/contracts/openapi.py src/rag_core/contracts/sse.py src/rag_core/contracts/v1.py tests/contract/test_api_schema.py
```

Exit **0**, stdout rỗng; approved sandbox escalation chỉ ghi `.git` index cho 17 files T03 đã được giao, không push/history changes. Không dùng `git add .`.

Cached review command nguyên văn:

```powershell
git diff --cached --check; if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}; git diff --cached --name-status; git diff --cached --stat; $expected=@('README.md','RUNBOOK.md','docs/handoffs.md','docs/tasks.md','docs/implementation-summary.md','pyproject.toml','uv.lock','docs/api/examples-v1.json','docs/api/openapi-v1.designed.json','docs/api/openapi.served.json','scripts/export_openapi.py','src/rag_core/contracts/__init__.py','src/rag_core/contracts/examples.py','src/rag_core/contracts/openapi.py','src/rag_core/contracts/sse.py','src/rag_core/contracts/v1.py','tests/contract/test_api_schema.py'); $staged=@(git diff --cached --name-only); if($staged.Count -ne 17 -or @(Compare-Object ($expected | Sort-Object) ($staged | Sort-Object)).Count -ne 0){throw 'Staged scope differs from exact T03 17 files'}; $unstaged=@(git diff --name-only); $untracked=@(git ls-files --others --exclude-standard); if($unstaged.Count -ne 0 -or $untracked.Count -ne 0){throw 'Unexpected unstaged/untracked paths'}; Write-Output 'PASS staged T03 exact scope=17 files; no unstaged/untracked paths'; git status --short
```

Exit **0**; cached whitespace check stdout rỗng. Output excerpt thật tại initial staged boundary (trước final docs-only additions):

```text
M	README.md
M	RUNBOOK.md
A	docs/api/examples-v1.json
A	docs/api/openapi-v1.designed.json
A	docs/api/openapi.served.json
M	docs/handoffs.md
M	docs/implementation-summary.md
M	docs/tasks.md
M	pyproject.toml
A	scripts/export_openapi.py
A	src/rag_core/contracts/__init__.py
A	src/rag_core/contracts/examples.py
A	src/rag_core/contracts/openapi.py
A	src/rag_core/contracts/sse.py
A	src/rag_core/contracts/v1.py
A	tests/contract/test_api_schema.py
M	uv.lock
 17 files changed, 7189 insertions(+), 35 deletions(-)
PASS staged T03 exact scope=17 files; no unstaged/untracked paths
```

Global ignore permission warning giữ nguyên; status chỉ staged 17 paths, không file lạ. Manual review source/design/test/dependency/docs và actual D1–D5 evidence hoàn thành. Chỉ tasks/handoffs được restage explicit sau final notes/checkpoint/staged evidence này; code/tests/config/artifacts không đổi sau DoD PASS. Final docs/cached whitespace checks output ghi dưới; completion command kế tiếp `git commit -m "feat(T03): define versioned API contracts"`.

Theo P14, COMPLETE trong candidate commit là đề nghị đóng task và chỉ hợp lệ sau successful actual commit +root review. Actual commit hash/exit/output/end/current status trả trong worker report, không nhét hash vào chính commit hoặc tạo amend/self-reference. Nếu commit fail thì T03 chưa COMPLETE, phải cập nhật reproduction/dirty files/last-good và báo root.

Final docs command nguyên văn:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'; uv run python scripts/check_docs.py 2>&1 | ForEach-Object { $_.ToString() } | Tee-Object -FilePath .local/t03-a02-docs-final.redacted.log; exit $LASTEXITCODE
```

Exit **0**, output thật sau task results/checkpoint/staged evidence/status proposal; literal output append này không thêm link/anchor:

```text
PASS UTF-8/nonempty Markdown: 8 files
PASS internal links/anchors: 168
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```

Restage docs-only command `git add -- docs/tasks.md docs/handoffs.md`; final cached whitespace/exact-scope/unstaged checks +actual commit output trả root post-commit. Completion commit là bằng chứng D6, resolver theo subject/Task-ID, không sửa history để ghi hash.

<a id="h-t04-a01"></a>
## H-T04-A01 — Phase 1 / T04 / attempt T04-A01

### Identity, baseline, scope and environment

- Worker `/root/t04_a01`, requested model `gpt-5.6-sol`/effort `xhigh`, fresh `fork_turns="none"`; actual runtime metadata verification is the Orchestrator's acceptance check. No model is inferred from this prompt, no child agent or next task. Started 2026-09-17 12:03 +07:00; ended/hash reported after successful commit.
- All commands below run at `C:\Users\Admin\Documents\GitHub\rag-core`, Windows PowerShell. Config: uv0.11.16/CPython3.12.4, existing dev/api groups/jsonschema4.26.0; `UV_CACHE_DIR=<repo>\.uv-cache`, `UV_PYTHON_INSTALL_DIR=<repo>\.uv-python`, both ignored. No DSNs/auth/provider/model/inference/storage credentials read; no production DB/index/service use.
- Read AGENTS, full T03/T01 dependency execution notes, P01/P11/P13/P14, handoffs/implementation-summary/README/RUNBOOK, original corpus prompt (all sections). Baseline command `git status --short; git branch --show-current; git rev-parse HEAD`, exit0, actual output:

```text
warning: unable to access 'C:\Users\Admin/.config/git/ignore': Permission denied
warning: unable to access 'C:\Users\Admin/.config/git/ignore': Permission denied
main
e4db5e3203b6c7052caa8943118b1999d84f51d8
```

No dirty/untracked baseline files. Root accepted T03 commit above and T01 `ff8069abfd2e41fb9618eb7d35fa22bf220a39d6`; earlier evidence preserved. Allowed changes: corpus shared scripts/schemas/inventory/manifests/README/license notices, common unit test, README/RUNBOOK/three living docs; ignore/dependency edits only if needed (none needed). Original prompt/API/business/AGENTS/plan/Scarlet unchanged.

<a id="h-t04-a01-sources"></a>
### DoD-2 — Official source versions, URLs and separate license scopes

Expected: real official upstream versions/license evidence, no invented local corpus measurements. Actual: metadata/readmes/tree/HEAD inspected live; no full corpus or dataset-byte download.

Revision command (first sandbox call exit1 `Invoke-RestMethod : Unable to connect to the remote server`; approved public metadata network escalation then exit0, same command):

```powershell
$ErrorActionPreference='Stop'; foreach($source in @(@('hotpotqa/hotpot','master'),@('patronus-ai/financebench','main'),@('google-deepmind/xquad','master'))){$uri='https://api.github.com/repos/'+$source[0]+'/commits/'+$source[1]; $reply=Invoke-RestMethod -Uri $uri -TimeoutSec 20; Write-Output ($source[0]+' '+$reply.sha+' '+$reply.commit.committer.date)}
```

The dates below are upstream commit timestamps, not download timestamps. Actual output:

```text
hotpotqa/hotpot 3635853403a8735609ee997664e1528f4480762a 2019-02-14T18:01:48Z
patronus-ai/financebench cc39aeb4afdf33909ee1412188bf89035950c2eb 2024-12-03T17:29:01Z
google-deepmind/xquad 7d30520c717524000f0d9d2f9c10a069acd9d285 2021-11-12T10:48:06Z
```

Pinned tree/README/publisher-card metadata command, approved public network read, exit0:

```powershell
$ErrorActionPreference='Stop'
foreach($source in @(@('hotpotqa/hotpot','3635853403a8735609ee997664e1528f4480762a'),@('patronus-ai/financebench','cc39aeb4afdf33909ee1412188bf89035950c2eb'),@('google-deepmind/xquad','7d30520c717524000f0d9d2f9c10a069acd9d285'))){
$tree=Invoke-RestMethod -Uri ('https://api.github.com/repos/'+$source[0]+'/git/trees/'+$source[1]+'?recursive=1') -TimeoutSec 20
Write-Output ($source[0]+' tree_truncated='+$tree.truncated)
$tree.tree | Where-Object {$_.path -match '(LICENSE|COPYING|README|financebench_.*jsonl$|xquad.(en|vi).json$)'} | Select-Object path,sha,size | Format-Table -AutoSize
}
$hf=Invoke-RestMethod -Uri 'https://huggingface.co/api/datasets/PatronusAI/financebench' -TimeoutSec 20
Write-Output ('PatronusAI/financebench hf_revision='+$hf.sha+' license='+$hf.cardData.license)
foreach($readme in @('https://raw.githubusercontent.com/hotpotqa/hotpot/3635853403a8735609ee997664e1528f4480762a/README.md','https://raw.githubusercontent.com/patronus-ai/financebench/cc39aeb4afdf33909ee1412188bf89035950c2eb/README.md','https://raw.githubusercontent.com/google-deepmind/xquad/7d30520c717524000f0d9d2f9c10a069acd9d285/README.md')){
Write-Output ('SOURCE '+$readme)
$sourceText=(Invoke-WebRequest -Uri $readme -UseBasicParsing -TimeoutSec 20).Content
$sourceText -split "`n" | Where-Object {$_ -match '(licen|CC |Creative|ZERO|zero|copyright|http.*hotpot_dev_distractor)'}
}
```

Actual output excerpt (all trees `tree_truncated=False`; sizes below are upstream tree metadata, **not local downloaded bytes/counts**):

```text
hotpotqa/hotpot tree_truncated=False
LICENSE.txt f3290f572e36d634ffb079fbb11a8acd50f6711a 11338
README.md   2329f6ae30c4ef5becf3ab57730fbb4860f91e61 6839
patronus-ai/financebench tree_truncated=False
README.md                                    bed5639eaeb17f93a818f55b99d03b398a469864 5094
data/financebench_document_information.jsonl decdfa948630f289d05cc0048417b3b9107cfb9f 88781
data/financebench_open_source.jsonl          4aef1d43a443474ba193f158f2baf70550ff528d 929848
vectorstores/README.md                       2d72261b38d5187fb97a42c8f78c10356d34be59 39
google-deepmind/xquad tree_truncated=False
README.md     addee0cf67354cbaeb9a7c77470c9b0c2f86b05d 7747
xquad.en.json cc0e3e8b94910097d29d2e9df5f266e1b30b2810 609383
xquad.vi.json 2c0b4bfe0f5808424fd353dcaecd388ecab8b87f 911401
PatronusAI/financebench hf_revision=e04404e3a97f69f79c14d42f24981a1c9c3bcd18 license=cc-by-nc-4.0
```

Observed pinned Hotpot README explicitly separates datasetCC-BY-SA-4.0 and codeApache-2.0; XQuAD README explicitly grants datasetCC-BY-SA-4.0. FinanceBench tree/README has no LICENSE/explicit dataset or company PDF grant, README says evidence pages ZERO-indexed. No claim is made that HF card terms automatically apply to GitHub/PDFs. Publisher card inspection command, exit0:

```powershell
$ErrorActionPreference='Stop'
$uri='https://huggingface.co/datasets/PatronusAI/financebench/raw/e04404e3a97f69f79c14d42f24981a1c9c3bcd18/README.md'
$card=(Invoke-WebRequest -Uri $uri -UseBasicParsing -TimeoutSec 20).Content
Write-Output ('SOURCE '+$uri)
$card -split "`n" | Where-Object {$_ -match '(license:|github.com/patronus-ai/financebench|CC|[Ll]icense|[Cc]opyright)'}
$uri='https://hotpotqa.github.io/'
$page=(Invoke-WebRequest -Uri $uri -UseBasicParsing -TimeoutSec 20).Content
[regex]::Matches($page,'href="([^"]+)"[^>]*>[^<]*(?:[Dd]ev|[Dd]istractor)') | ForEach-Object {Write-Output $_.Value}
```

Output included `license: cc-by-nc-4.0` and a publisher link to GitHub PDFs, no PDF permission grant. No matches from the first homepage regex; a later line-based official homepage inspection below confirmed the CMU link. FinanceBench local-use rights decision was reported early to root; T06 needs user decision or upstream grant before dataset/PDF downloads. Inventory keeps its license_status unresolved, metadata-only commit policy, company PDF rights separate. This is a next-task dependency risk; T04 uses only public metadata and does not require a data-use decision to finish shared utilities.

HEAD command, approved network read, shell exit0 (per-endpoint failures intentionally reported as observations, not hidden PASS):

```powershell
$ErrorActionPreference='Stop'
foreach($uri in @('http://curtis.ml.cmu.edu/datasets/hotpot/hotpot_dev_distractor_v1.json','https://raw.githubusercontent.com/patronus-ai/financebench/cc39aeb4afdf33909ee1412188bf89035950c2eb/data/financebench_open_source.jsonl','https://raw.githubusercontent.com/patronus-ai/financebench/cc39aeb4afdf33909ee1412188bf89035950c2eb/data/financebench_document_information.jsonl','https://raw.githubusercontent.com/google-deepmind/xquad/7d30520c717524000f0d9d2f9c10a069acd9d285/xquad.en.json','https://raw.githubusercontent.com/google-deepmind/xquad/7d30520c717524000f0d9d2f9c10a069acd9d285/xquad.vi.json')){
try{$response=Invoke-WebRequest -Method Head -Uri $uri -UseBasicParsing -TimeoutSec 20; Write-Output ('HEAD '+$uri+' status='+$response.StatusCode+' content_type='+$response.Headers['Content-Type'])}catch{Write-Output ('HEAD '+$uri+' failed='+$_.Exception.Message)}
}
```

Actual output:

```text
HEAD http://curtis.ml.cmu.edu/datasets/hotpot/hotpot_dev_distractor_v1.json failed=The operation has timed out.
HEAD https://raw.githubusercontent.com/patronus-ai/financebench/cc39aeb4afdf33909ee1412188bf89035950c2eb/data/financebench_open_source.jsonl status=200 content_type=text/plain; charset=utf-8
HEAD https://raw.githubusercontent.com/patronus-ai/financebench/cc39aeb4afdf33909ee1412188bf89035950c2eb/data/financebench_document_information.jsonl status=200 content_type=text/plain; charset=utf-8
HEAD https://raw.githubusercontent.com/google-deepmind/xquad/7d30520c717524000f0d9d2f9c10a069acd9d285/xquad.en.json status=200 content_type=text/plain; charset=utf-8
HEAD https://raw.githubusercontent.com/google-deepmind/xquad/7d30520c717524000f0d9d2f9c10a069acd9d285/xquad.vi.json status=200 content_type=text/plain; charset=utf-8
```

Same-host HTTPS HEAD command, shell exit0/observed timeout:

```powershell
$uri='https://curtis.ml.cmu.edu/datasets/hotpot/hotpot_dev_distractor_v1.json'; try{$response=Invoke-WebRequest -Method Head -Uri $uri -UseBasicParsing -TimeoutSec 15; Write-Output ('HEAD '+$uri+' status='+$response.StatusCode+' content_type='+$response.Headers['Content-Type'])}catch{Write-Output ('HEAD '+$uri+' failed='+$_.Exception.Message)}
```

Output `HEAD https://curtis.ml.cmu.edu/datasets/hotpot/hotpot_dev_distractor_v1.json failed=The operation has timed out.` Official homepage inspection exit0:

```powershell
$ErrorActionPreference='Stop'
$page=(Invoke-WebRequest -Uri 'https://hotpotqa.github.io/' -UseBasicParsing -TimeoutSec 20).Content
$page -split "`n" | Where-Object {$_ -match '(hotpot_dev|distractor|drive.google|Download|download|datasets/hotpot)'}
```

Actual output included:

```text
"contentUrl":"http://curtis.ml.cmu.edu/datasets/hotpot/hotpot_dev_distractor_v1.json"
```

T05 must prove actual access/download or report upstream-availability BLOCKED; no unofficial mirror, full JSON fetch or checksum fabrication attempted. No published byte pin in inspected README; first semantic-validated download must record measuredSHA256. HEAD200 only proves endpoint access, not exact bytes.

Inventory/schema/root+domain manifests were reviewed: all three `not_downloaded`, downloaded_at/document_count/qa_count null, checksum{} and artifacts[]; expected_sha256 null. Git commit/blob IDs above are real upstream pins, not claims of local downloads. Existing raw/documents/.downloads ignore policy retained; licensed lightweight metadata/attribution remains trackable, normalized QA only with applicable rights. README/RUNBOOK explicitly say full command completes T08. **DoD-2 PASS for honest verified inventory/no-data manifest state**, with access/rights risks preserved.

<a id="h-t04-a01-dod1"></a>
### DoD-1 — Setup help and meaningful synthetic fault tests

Command, exit0; expected help only/no mutation/network, actual:

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR=Join-Path (Get-Location) '.uv-python'; uv run python corpus-documents/scripts/setup_corpus.py --help 2>&1 | ForEach-Object {$_.ToString()} | Tee-Object -FilePath corpus-documents/.downloads/t04-a01-help.log; exit $LASTEXITCODE
```

```text
usage: setup_corpus.py [-h] (--all | --domain {default,document,bilingual})

Reproduce official RAG evaluation corpus (domain preparation pending T05-T07).

options:
  -h, --help            show this help message and exit
  --all                 Prepare all domains (complete in T08).
  --domain {default,document,bilingual}
                        Prepare one corpus domain.
```

Command, exit0; expected corrupt/interrupted/retry/idempotency/reference safety, actual **78 PASS/no empty/skipped tests**:

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR=Join-Path (Get-Location) '.uv-python'; uv run pytest tests/unit/test_corpus_common.py 2>&1 | ForEach-Object {$_.ToString()} | Tee-Object -FilePath corpus-documents/.downloads/t04-a01-tests-final.log; exit $LASTEXITCODE
```

Actual output excerpt; full reviewed public/synthetic log at `corpus-documents/.downloads/t04-a01-tests-final.log`, ignored, no private content to redact:

```text
platform win32 -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Admin\Documents\GitHub\rag-core
configfile: pyproject.toml
plugins: anyio-4.15.1, asyncio-1.4.0
collected 78 items
tests\unit\test_corpus_common.py ....................................... [ 50%]
.......................................                                  [100%]
============================= 78 passed in 1.89s ==============================
```

Coverage: corrupt content pin refusal/no new file/prior preservation; stream interruption/IncompleteRead/retry recovery and bounded attempts/timeouts/backoff; OSError/KeyboardInterrupt during write, fsync/validator/replace failures preserve published bytes; zero/truncated/excess/oversize streams; SHA256+Git blob checks; pinned cache reuse/no network/stable mtime/cache corruption repair; required semantic validator for unpinned content; atomic JSON Unicode/idempotency; traversal/absolute/Windows stream/reserved names/unofficial URLs/redirects; real Windows directory junction escape refusal without deleting target; JSON duplicate/nonfinite/malformed data; invalid/empty references/question/answers/duplicate IDs/empty QA/JSONL records; honest schemas/ready measurement refusal/provenance+aggregate drift; all four setup/validation selections nonzero/nonmutation. Tests use synthetic fixtures and injected network responses only, **not live corpus integrity verification**.

Metadata-only command, exit0, expected source/schema/aggregate consistency without data acceptance:

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR=Join-Path (Get-Location) '.uv-python'; uv run python corpus-documents/scripts/validate_corpus.py --metadata-only 2>&1 | ForEach-Object {$_.ToString()} | Tee-Object -FilePath corpus-documents/.downloads/t04-a01-metadata-final.log; exit $LASTEXITCODE
```

Actual output `CORPUS METADATA: PASS - 3 domain manifests + inventory; corpus data NOT validated.`

Honest unavailable gates, each run separately:

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR=Join-Path (Get-Location) '.uv-python'; uv run python corpus-documents/scripts/setup_corpus.py --all 2>&1 | ForEach-Object {$_.ToString()} | Tee-Object -FilePath corpus-documents/.downloads/t04-a01-unavailable-setup.log; exit $LASTEXITCODE
```

Expected/actual exit **2**; output:

```text
CORPUS SETUP: UNAVAILABLE - domain preparation not implemented: default, document, bilingual. Required tasks: T05 (default), T06 (document), T07 (bilingual); full acceptance T08.
```

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR=Join-Path (Get-Location) '.uv-python'; uv run python corpus-documents/scripts/validate_corpus.py --all 2>&1 | ForEach-Object {$_.ToString()} | Tee-Object -FilePath corpus-documents/.downloads/t04-a01-unavailable-validation.log; exit $LASTEXITCODE
```

Expected/actual exit **1**, output `CORPUS VALIDATION: FAIL - default: corpus is not_downloaded; run domain setup after its implementation`. No setup/full-validation PASS claim. **DoD-1 PASS.**

<a id="h-t04-a01-quality"></a>
### D2 — Locked environment and code quality

Each command below ran separately, exit0, expected=lockedPython3.12/quality PASS, actual outputs shown; logs below are ignored and reviewed public/synthetic output.

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR=Join-Path (Get-Location) '.uv-python'; uv sync --locked --group dev --group api 2>&1 | ForEach-Object {$_.ToString()} | Tee-Object -FilePath corpus-documents/.downloads/t04-a01-sync.log; exit $LASTEXITCODE
```

```text
Resolved 77 packages in 0.90ms
Checked 44 packages in 2ms
```

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR=Join-Path (Get-Location) '.uv-python'; uv run ruff check . 2>&1 | ForEach-Object {$_.ToString()} | Tee-Object -FilePath corpus-documents/.downloads/t04-a01-ruff.log; exit $LASTEXITCODE
```

Actual output `All checks passed!`.

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR=Join-Path (Get-Location) '.uv-python'; uv run mypy src corpus-documents/scripts 2>&1 | ForEach-Object {$_.ToString()} | Tee-Object -FilePath corpus-documents/.downloads/t04-a01-mypy.log; exit $LASTEXITCODE
```

Actual output `Success: no issues found in 14 source files`. Includes unchanged11 application source +3new corpus scripts. Existing jsonschema package lacks bundled stubs; two exact `import-untyped` annotations document this third-party boundary, no new dependency or config-wide mypy ignore. Final common unit command/output is above; no requirement to re-run T02/T03 integration when application source/config/contracts unchanged.

### Fixed helper/check failures in this attempt

- First inventory helper had an extra `)` after `foreach($readme in @(...))`, shell exit1 before HTTP calls. Actual error: `Missing statement body in foreach loop.` / `Unexpected token ')' in expression or statement.` Fixed multiline command is recorded above; no fabricated inventory from this failure.
- Initial `uv run ruff check corpus-documents/scripts tests/unit/test_corpus_common.py --fix` reported B023 closure binding, RUF001/002 en-dashes and one fixed unused import: `Found 8 errors (1 fixed, 7 remaining).` Its combined shell subsequently ran formatter and returned0; this was **not** treated as a quality PASS. Bound advertised length in generator default and replaced ambiguous dashes. An attempted non-ASCII PowerShell-to-Python replacement did not replace en-dashes; subsequent separate `uv run ruff check .` exit1: `Found 5 errors.` Correct UTF-8 patch and import spacing fixes yielded final independent Ruff exit0 above.
- First `uv run mypy src corpus-documents/scripts`, exit1: `Found 3 errors in 2 files (checked 14 source files)`; actual errors: common QA loop reused a variable previously inferred as str (`Any | None` assignment), and jsonschema/import exceptions lacked stubs. Renamed document-ID loop variable and explicitly documented the two external untyped imports; strict final14-source check PASS. No product/test semantics changed to pass.
- First metadata output emitted an em-dash that PowerShell native capture rendered U+FFFD; changed CLI status separators to ASCII and re-ran current metadata/unavailable evidence above. No private content was involved.
- First summary apply_patch failed verification of a mistyped existing source line (`current-session` vs actual `current-scope`); no partial mutation. Re-read exact line and applied correct patch. This did not affect code/tests.

<a id="h-t04-a01-review"></a>
### D1/D4/D5/D6 — Scope, docs, review and completion boundary

- D1: dependencies notes read, baseline clean, diff check/manual source/schema/inventory/unit review done; final exact19-file scope/prompt proof below.
- D2: locked sync/Ruff/strictmypy14/commonunit78 PASS; tests no skip/no external datasets.
- D3: separate help/test/manual official-source/license/no-data manifest DoD commands/expected/actual/exit above; access timeouts and rights decision reported honestly. Metadata-only never substitutes corpus acceptance.
- D4: README/RUNBOOK and task execution notes/current checkpoint/Phase1-T04-A01 summary append updated. Corpus README/license notices document setup pending T08, unknown counts, source pins/terms, retry/atomic/cache/ref interfaces, raw/documents/qa hygiene and conventions. Final docs-check actual output follows.
- D5: no secret/raw corpus/PDF/model/cache/runtime artifact staged; original prompt bytes unchanged. No DB/index/API/model/retrieval change or migration. Source/manifest schema is initial corpus metadata v1; later fields/interfaces must update validation and docs in the same domain task. Corpus source download tooling does not ingest production or access app-owned storage; all query scopes remain current session only.
- D6: exact19 explicit paths, stage/cached scope/whitespace review, completion subject `feat(T04): add reproducible corpus tooling`; COMPLETE only after successful actual commit/root review. Actual hash/end/post-commit status returned to root, not embedded in its own commit.
- Risks/next: no T04 code blocker; T05 verify official Hotpot access/hash or BLOCKED, T06 user decision/upstreamgrant on local GitHub QA/PDF use. No mock success/live corpus claim. Full setup/validation/gold alignment/actual counts belong T05–T08; no next task run by this worker.

#### D4 actual documentation check

Command, exit0; expected UTF-8/internal links/anchors/task fields/dependencies valid, actual:

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR=Join-Path (Get-Location) '.uv-python'; uv run python scripts/check_docs.py 2>&1 | ForEach-Object {$_.ToString()} | Tee-Object -FilePath corpus-documents/.downloads/t04-a01-docs.log; exit $LASTEXITCODE
```

```text
PASS UTF-8/nonempty Markdown: 10 files
PASS internal links/anchors: 186
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```

#### D1/D5 actual scope, secrets, prompt and ignore review

Command, exit0; manual diff/source/schema/inventory/test/docs review plus explicit assertions (sensitive matches counted only, not printed):

```powershell
git diff --check; if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}; $candidate=@('README.md','RUNBOOK.md','docs/tasks.md','docs/handoffs.md','docs/implementation-summary.md','corpus-documents/README.md','corpus-documents/source-license-inventory.json','corpus-documents/manifest.json','corpus-documents/default/manifest.json','corpus-documents/document/manifest.json','corpus-documents/bilingual/manifest.json','corpus-documents/licenses/README.md','corpus-documents/schemas/domain-manifest.schema.json','corpus-documents/schemas/root-manifest.schema.json','corpus-documents/schemas/source-inventory.schema.json','corpus-documents/scripts/common.py','corpus-documents/scripts/setup_corpus.py','corpus-documents/scripts/validate_corpus.py','tests/unit/test_corpus_common.py'); $changed=@(git diff --name-only)+@(git ls-files --others --exclude-standard); if(@(Compare-Object ($candidate | Sort-Object) ($changed | Sort-Object)).Count -ne 0){throw 'Changed paths differ from exact19file T04 scope'}; $items=@($candidate | ForEach-Object {Get-Item -LiteralPath $_}); if(@($items | Where-Object Length -gt 1048576).Count -ne 0){throw 'Large artifact found'}; $suspicious=@(rg -l '(sk-[A-Za-z0-9_-]{20,}|AKIA[A-Z0-9]{16}|-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----)' -- $candidate); if($suspicious.Count -ne 0){throw 'Credential marker found; review without exposing values'}; $sensitive=@(rg -n -i '(secret|password|bearer|api[_-]?key|token)' -- $candidate); Write-Output ('Sensitive-name matches manually reviewed: '+$sensitive.Count); $promptPath='corpus-documents/Codex Prompt – Build RAG Evaluation Corpus.md'; $raw=(git hash-object --no-filters -- $promptPath).Trim(); $sha=(Get-FileHash -Algorithm SHA256 -LiteralPath $promptPath).Hash; if($raw -ne '81ab3c77530722968d847391d8095284f1a874a9' -or $sha -ne '7EC6E58AE4C24DB27AF4320BCB30222BBF2B67961D99C62980CEA4410AEE2C46'){throw 'Original prompt bytes changed'}; Write-Output ('PASS exact_scope='+$items.Count+' files_over_1MiB=0 credential_markers=0'); Write-Output ('PASS prompt_blob='+$raw+' SHA256='+$sha); $ignored=@('corpus-documents/default/raw/source.json','corpus-documents/document/documents/report.pdf','corpus-documents/.downloads/t04-a01-tests-final.log','.env','.uv-cache/test','.uv-python/test'); $matches=@(git check-ignore -v --no-index -- $ignored); if($matches.Count -ne $ignored.Count){throw 'Expected ignored artifact missing'}; $matches; foreach($path in @('corpus-documents/scripts/common.py','corpus-documents/schemas/domain-manifest.schema.json','corpus-documents/source-license-inventory.json','corpus-documents/licenses/README.md','corpus-documents/default/qa/eval.jsonl')){git check-ignore -q --no-index -- $path; if($LASTEXITCODE -eq 0){throw 'Lightweight source/metadata unexpectedly ignored'}}; Write-Output 'PASS source/license/schema/QA metadata trackable; raw/PDF/log/cache/env ignored'; git diff --stat
```

Output excerpt (repeated baseline global ignore warnings preserved once):

```text
warning: unable to access 'C:\Users\Admin/.config/git/ignore': Permission denied
Sensitive-name matches manually reviewed: 111
PASS exact_scope=19 files_over_1MiB=0 credential_markers=0
PASS prompt_blob=81ab3c77530722968d847391d8095284f1a874a9 SHA256=7EC6E58AE4C24DB27AF4320BCB30222BBF2B67961D99C62980CEA4410AEE2C46
.gitignore:44:corpus-documents/*/raw/ corpus-documents/default/raw/source.json
.gitignore:45:corpus-documents/*/documents/ corpus-documents/document/documents/report.pdf
.gitignore:46:corpus-documents/.downloads/ corpus-documents/.downloads/t04-a01-tests-final.log
.gitignore:22:.env .env
.gitignore:10:.uv-cache/ .uv-cache/test
.gitignore:11:.uv-python/ .uv-python/test
PASS source/license/schema/QA metadata trackable; raw/PDF/log/cache/env ignored
```

Diff whitespace stdout empty; candidate exact19, all under1MiB, no raw/model/runtime/credentials. Sensitive terms are policy descriptions/synthetic fixture markers/historical commands, manually reviewed; original user prompt unchanged. No `.gitignore`/pyproject/lock/app/contract changes required. **D1/D2/D3/D4/D5 PASS.** D6 actual cached review/commit boundary appended next.

#### Final finite JSON number review and updated DoD-1 evidence

Final review found that Python's ordinary float parser can turn valid JSON exponent
syntax such as `1e400` into an infinite float. Added a finite float guard to strict
JSON parsing plus positive/negative overflow regression cases. An initial patch
failed verification against the formatter's one-line parametrization before any
mutation; exact line re-read and patched. This is shared validation correctness,
not a domain pipeline/gold change. Historical78-test output above is retained;
**current final source passed80 tests**, no skips, after this last code change.

Command, exit0:

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR=Join-Path (Get-Location) '.uv-python'; uv run pytest tests/unit/test_corpus_common.py 2>&1 | ForEach-Object {$_.ToString()} | Tee-Object -FilePath corpus-documents/.downloads/t04-a01-tests-finite-json.log; exit $LASTEXITCODE
```

Actual output excerpt; full reviewed synthetic log `corpus-documents/.downloads/t04-a01-tests-finite-json.log`:

```text
platform win32 -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0
collected 80 items
tests\unit\test_corpus_common.py ....................................... [ 48%]
.........................................                                [100%]
============================= 80 passed in 1.87s ==============================
```

Separate current-quality commands, each exit0:

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR=Join-Path (Get-Location) '.uv-python'; uv run ruff check .; exit $LASTEXITCODE
```

Actual `All checks passed!`.

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR=Join-Path (Get-Location) '.uv-python'; uv run mypy src corpus-documents/scripts; exit $LASTEXITCODE
```

Actual `Success: no issues found in 14 source files`.

#### D6 actual explicit stage and cached review

Stage command:

```powershell
git add -- README.md RUNBOOK.md docs/tasks.md docs/handoffs.md docs/implementation-summary.md corpus-documents/README.md corpus-documents/source-license-inventory.json corpus-documents/manifest.json corpus-documents/default/manifest.json corpus-documents/document/manifest.json corpus-documents/bilingual/manifest.json corpus-documents/licenses/README.md corpus-documents/schemas/domain-manifest.schema.json corpus-documents/schemas/root-manifest.schema.json corpus-documents/schemas/source-inventory.schema.json corpus-documents/scripts/common.py corpus-documents/scripts/setup_corpus.py corpus-documents/scripts/validate_corpus.py tests/unit/test_corpus_common.py
```

Initial sandbox exit1, actual `fatal: Unable to create 'C:/Users/Admin/Documents/GitHub/rag-core/.git/index.lock': Permission denied`. Approved escalation for exact task paths then exit0/stdoutempty. No push/amend/rebase/reset/history mutation. Initial cached review before the finite-JSON guard ran as:

```powershell
git diff --cached --check; if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}; git diff --cached --name-status; git diff --cached --stat; $expected=@('README.md','RUNBOOK.md','docs/tasks.md','docs/handoffs.md','docs/implementation-summary.md','corpus-documents/README.md','corpus-documents/source-license-inventory.json','corpus-documents/manifest.json','corpus-documents/default/manifest.json','corpus-documents/document/manifest.json','corpus-documents/bilingual/manifest.json','corpus-documents/licenses/README.md','corpus-documents/schemas/domain-manifest.schema.json','corpus-documents/schemas/root-manifest.schema.json','corpus-documents/schemas/source-inventory.schema.json','corpus-documents/scripts/common.py','corpus-documents/scripts/setup_corpus.py','corpus-documents/scripts/validate_corpus.py','tests/unit/test_corpus_common.py'); $staged=@(git diff --cached --name-only); if($staged.Count -ne 19 -or @(Compare-Object ($expected | Sort-Object) ($staged | Sort-Object)).Count -ne 0){throw 'Staged scope differs from exact19file T04 scope'}; if(@(git diff --name-only).Count -ne 0 -or @(git ls-files --others --exclude-standard).Count -ne 0){throw 'Unstaged or untracked files remain'}; Write-Output 'PASS staged T04 exact19files; no unstaged/untracked files'; git status --short
```

Exit0, whitespace stdoutempty, exactly19 staged files (5modify/14add), initial stat
`19 files changed, 2486 insertions(+), 18 deletions(-)`, output
`PASS staged T04 exact19files; no unstaged/untracked files`.
Final common/test +docs-only edits must be restaged explicitly and current
docs/cached checks run before completion commit below; prior stats are historical,
not final diff claims. Completion subject `feat(T04): add reproducible corpus tooling`;
successful actual hash/end/commit output/root review is the COMPLETE boundary.

Final docs command after task COMPLETE proposal and finite-JSON evidence, exit0:

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR=Join-Path (Get-Location) '.uv-python'; uv run python scripts/check_docs.py 2>&1 | ForEach-Object {$_.ToString()} | Tee-Object -FilePath corpus-documents/.downloads/t04-a01-docs-final.log; exit $LASTEXITCODE
```

Actual output:

```text
PASS UTF-8/nonempty Markdown: 10 files
PASS internal links/anchors: 186
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```

Read-only `git diff -- corpus-documents/scripts/common.py tests/unit/test_corpus_common.py; git diff --check; if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}; Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz'` exit0, diff only math finite-float parser and two overflow test cases, whitespace stdoutempty; actual time `2026-09-17 12:25:02 +07:00`. No remaining code/test concern after final80-test/Ruff/mypy PASS. This final literal evidence adds no new link/anchor. Explicit restage command next:

```powershell
git add -- corpus-documents/scripts/common.py tests/unit/test_corpus_common.py docs/tasks.md docs/handoffs.md docs/implementation-summary.md
```

Final cached exact19 scope/whitespace/unstaged check must pass before
`git commit -m "feat(T04): add reproducible corpus tooling"`. Actual commit/hash/end
and current clean status returned to Orchestrator post-commit; never amend to embed
its own hash. If commit fails, not COMPLETE and reproduction/checkpoint must be
written before handing back. Root verifies model/effort/runtime before acceptance.

Final cached command actually ran after the restage above, exit0:

```powershell
git diff --cached --check; if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}; $expected=@('README.md','RUNBOOK.md','docs/tasks.md','docs/handoffs.md','docs/implementation-summary.md','corpus-documents/README.md','corpus-documents/source-license-inventory.json','corpus-documents/manifest.json','corpus-documents/default/manifest.json','corpus-documents/document/manifest.json','corpus-documents/bilingual/manifest.json','corpus-documents/licenses/README.md','corpus-documents/schemas/domain-manifest.schema.json','corpus-documents/schemas/root-manifest.schema.json','corpus-documents/schemas/source-inventory.schema.json','corpus-documents/scripts/common.py','corpus-documents/scripts/setup_corpus.py','corpus-documents/scripts/validate_corpus.py','tests/unit/test_corpus_common.py'); $staged=@(git diff --cached --name-only); if($staged.Count -ne 19 -or @(Compare-Object ($expected | Sort-Object) ($staged | Sort-Object)).Count -ne 0){throw 'Wrong final staged scope'}; if(@(git diff --name-only).Count -ne 0 -or @(git ls-files --others --exclude-standard).Count -ne 0){throw 'Unstaged/untracked files remain'}; git diff --cached --stat; Write-Output 'PASS final staged exact19 T04 files; whitespace clean; no unstaged/untracked paths'
```

Actual output excerpt before this final evidence-only append:

```text
19 files changed, 2598 insertions(+), 18 deletions(-)
PASS final staged exact19 T04 files; whitespace clean; no unstaged/untracked paths
```

Cached whitespace stdoutempty; final source365lines/test546lines, actual80-test
evidence above matches the staged source. Restage only this handoff and run cached
whitespace/19count/no-unstaged assertions once more before the actual task commit;
this output-only addition changes docs line counts, not code/tests or schema pins.

<a id="h-t05-a01"></a>
## H-T05-A01 — Phase 1 / T05 / runtime quota recovery

Root recovery brief reported worker `/root/t05_a01` ended immediately with this
runtime event (not a shell command/output):

```text
Agent errored: You've hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/codex/settings/usage to purchase more credits or try again at 4:46 PM.
```

No repo changes/attempt notes/shell execution/commit were created. Start/end/timezone
are not inferred from the runtime message. User said continue; root verified only
root was live, worktree CLEAN, T05 TODO and accepted T04 HEAD. A02 is a fresh worker;
A01 is never reused and its nonexistent shell logs are not fabricated.

<a id="h-t05-a02"></a>
## H-T05-A02 — Phase 1 / T05 / attempt T05-A02

### Identity, baseline, scope and configuration

- Sole worker `/root/t05_a02`, requested `gpt-5.6-sol`/`xhigh`, fresh `fork_turns="none"`;
  actual runtime checked by root, not inferred from prompt. Started2026-09-17 23:22+07:00;
  end/hash/status returned post-commit. No children/next task.
- **cwd for every command below:** `C:\Users\Admin\Documents\GitHub\rag-core`, Windows
  PowerShell, Asia/Bangkok. CPython3.12.4/uv0.11.16, dev+api groups; no DSNs/services,
  provider/model/productionstorage/index or secrets read. Actual source HF revision
  `1908d6afbbead072334abe2965f91bd2709910ab`; corpus-only, no live RAG/provider benchmark.
- Prefix used verbatim by each uv command:

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR=Join-Path (Get-Location) '.uv-python';
```

Separate baseline commands `git status --short`, `git branch --show-current`,
`git rev-parse HEAD`, each exit0; expected CLEAN accepted T04, actual:

```text
warning: unable to access 'C:\Users\Admin/.config/git/ignore': Permission denied
warning: unable to access 'C:\Users\Admin/.config/git/ignore': Permission denied
main
ad49ecc53a1998758f419e00ac5d03bf468ba989
```

Read AGENTS/T05/fullT04 execution notes/P01/P11/P13/fulloriginalprompt/T04handoff+summary/
README/RUNBOOK/corpusREADME before edits. Initially allowed default/sharedtools/QA/
metadata/common+defaulttests/docs; user source authorization later added only P11
exception, exact HF source/CDN/Parquetdevdependency.22completionpaths, no other
domain preparation, API/model/retrieval/Scarlet/storage modification or push/merge.

<a id="h-t05-a02-source"></a>
### Actual source access failures, explicit source authorization and verified bytes

Initial curl helper with `$ErrorActionPreference='Stop'` and progress stderr exited1
on PowerShell `NativeCommandError` before useful connection evidence. It is not
counted as a source timeout. Corrected actual commands:

```powershell
$ErrorActionPreference='Continue'; curl.exe --silent --show-error --fail --location --max-time 20 --output corpus-documents/.downloads/t05-a02-official-access.json http://curtis.ml.cmu.edu/datasets/hotpot/hotpot_dev_distractor_v1.json 2>&1 | ForEach-Object {$_.ToString()} | Tee-Object -FilePath corpus-documents/.downloads/t05-a02-access-sandbox-final.log; exit $LASTEXITCODE
```

Sandbox exit7, actual `curl: (7) Failed to connect to curtis.ml.cmu.edu port 80 after 5 ms: Couldn't connect to server`.
Same command with approved network and log `t05-a02-access-approved.log` exited28:
`curl: (28) Connection timed out after 20008 milliseconds`. Same-host HTTPS
command differed only URL=`https://curtis.ml.cmu.edu/datasets/hotpot/hotpot_dev_distractor_v1.json`,
output=`t05-a02-official-https-access.json`, log=`t05-a02-access-https-approved.log`;
approved exit28, actual `curl: (28) Connection timed out after 20002 milliseconds`.
Expected fetch official JSON; actual source unavailable, zero corpus publication.

Primary web inspection: official homepage, pinned Hotpot README and download.sh
still point to CMUHTTPv1 and designate no alternative in those sources. Root
researched the specific HF derivative and asked the user; user replied verbatim:
**“Cho phép bản Hugging Face (đề xuất)”**. Authorization received in this active A02
on2026-09-17, before any HF dataset download. [P11](plan.md#p11) records exception
without editing originalprompt or gold/seed/target/DoD. Community/HF-maintained
derivative, not asserted official-author mirror or byte-identical CMUJSON.

Approved network public metadata command, exit0:

```powershell
$ErrorActionPreference='Stop'; $uri='https://huggingface.co/api/datasets/hotpotqa/hotpot_qa/tree/1908d6afbbead072334abe2965f91bd2709910ab/distractor?expand=false'; $tree=Invoke-RestMethod -Uri $uri -TimeoutSec 20; $tree | Where-Object {$_.path -eq 'distractor/validation-00000-of-00001.parquet'} | Select-Object path,size,@{Name='published_sha256';Expression={$_.lfs.oid}} | Format-List; $card=(Invoke-WebRequest -UseBasicParsing -Uri 'https://huggingface.co/datasets/hotpotqa/hotpot_qa/raw/1908d6afbbead072334abe2965f91bd2709910ab/README.md' -TimeoutSec 20).Content; $card -split "`n" | Where-Object {$_ -match '(license:|num_examples: 7405|homepage|HotpotQA)' } | Select-Object -First 12
```

Actual excerpt (metadata count was not claimed measured until downloaded):

```text
path             : distractor/validation-00000-of-00001.parquet
size             : 27452575
published_sha256 : c20b638ca82b21d04fe12e14ff417ad05153d4d215a65de54497fca4e972f7c6
    num_examples: 7405
HotpotQA is distributed under a [CC BY-SA 4.0 License](http://creativecommons.org/licenses/by-sa/4.0/).
```

Pinned commit page also identifies HF staff Parquetconversion; sourcecard attributes
Yang etal./originalWikipedia. Originalcode Apache2 does not relicense dataset.
QA/index/report adaptations CC BY-SA4 with attribution/change notices; rawdatasets/
Parquet/convertedJSON/materializeddocuments remain ignored, no companyPDFdownload.

First HF CLI run (`--domain default`, approvednetwork), log
`.downloads/t05-a02-default-setup-live.log`, exit1, actual:
`CORPUS SETUP: FAIL - default: Download failed after 1 attempt(s): source verification or local publication failure; no data acceptance`.
Cause: overly narrow delivery-host allowlist, no published corpus. Bounded HEAD
inspection via inline Python `HTTPRedirectHandler`, `.venv/Scripts/python.exe -`,
request exact `common.APPROVED_HF_URL` with timeout20, emitted only scheme/hostname/
path and boolean signed-query presence (never query contents), exit0/log
`.downloads/t05-a02-hf-delivery-hosts.log`:

```text
redirect 302 https us.aws.cdn.hf.co /xet-bridge-us/621ffdd236468d709f181e65/6f4264cffe19511caba92594db23f1a32eb76fdeebbb04f7a98a589a3726423e signed_query_present=True
final status=200 host=us.aws.cdn.hf.co content_length=27452575
```

Correction scopes redirects to exactapprovedHFstart + observedHTTPSdeliveryhost/
`/xet-bridge-us/`, mandatorypublishedSHA256, no arbitrary sourceoverride. Next CLI
run/log`default-setup-live-final.log`, exit1, same genericfailure caused semanticgate.
Transportpin verification separated from domainsemantic validation so verified
stagedbytes remain on failure. Diagnostic CLI/log`default-setup-semantic.log`, exit1:
`CORPUS SETUP: FAIL - default: HotpotQA supporting fact has no valid context sentence; no data acceptance`.
Last-good state remained unprepared manifest/aggregate; forensic stages retained.
Private mkdtemp directories from approved process denied sandbox inspection; new
stages use UUID-named normal mkdir inheriting repositoryACL, not userACL changes.

Real primary-byte diagnostic used inline Python `.venv/Scripts/python.exe -`,
`parquet_records`+`sha256_file` on retained
`.downloads/default-stage-622dc0af97b9411cbbb5c04c281cd888/default/raw/hf-hotpotqa-distractor-validation.parquet`,
checked every sourcefact against title/sentencecount and ambiguous titles, exit0,
log`.downloads/t05-a02-source-diagnostics.log`; actual:

```text
actual_sha256=c20b638ca82b21d04fe12e14ff417ad05153d4d215a65de54497fca4e972f7c6
actual_bytes=27452575
actual_rows=7405
distribution={"by_level": {"hard": 7405}, "by_type": {"bridge": 5918, "comparison": 1487}, "strata": {"bridge/hard": 5918, "comparison/hard": 1487}}
invalid_facts=1 ambiguous_titles=0
[{"id": "5ae61bfd5542992663a4f261", "title": "Jimmy Butler (basketball)", "index": 902, "sentence_count": 5}]
```

Separate inline diagnostic `sample_records(records)` before changing source-range
handling, exit0/log`source-selection-diagnostics.log`, actual:

```text
selected_qa=100
upstream_invalid_fact_selected=False
selected_distribution={'by_type': {'bridge': 50, 'comparison': 50}, 'by_level': {'hard': 100}, 'strata': {'bridge/hard': 50, 'comparison/hard': 50}}
```

Root confirmed technicalcorrection withinT05: preserve exactrawannotation and
unchanged sample; fullsource structure/title checks and explicitanomalyreport,
strictsample ranges/mapping, no goldbaseddrop/edit/resample. Selectedanomaly would
fail. This removes an invented allupstream-range gate; all requiredsubset DoD gates
stay strict. Tests cover anomalyinside/outside sample; no claim7405annotationsclean.

<a id="h-t05-a02-dod1"></a>
### DoD-1 — Separate real setup and default validation

Commands below use envprefix/cwd/config above; expected realapprovedsourcebytes,
100uniqueQA, allcontexts/distractors materialized, supporting-only originalgold,
validmanifests/receipts/strictselectedranges. Actual live setup approvednetwork:

```powershell
uv run python corpus-documents/scripts/setup_corpus.py --domain default 2>&1 | ForEach-Object {$_.ToString()} | Tee-Object -FilePath corpus-documents/.downloads/t05-a02-default-setup-accepted.log; exit $LASTEXITCODE
```

Exit0, actual:

```text
CORPUS SETUP: PASS - default/HotpotQA; documents=986 QA=100 seed=42 source_sha256=c20b638ca82b21d04fe12e14ff417ad05153d4d215a65de54497fca4e972f7c6
Selected distribution: {'by_type': {'bridge': 50, 'comparison': 50}, 'by_level': {'hard': 100}, 'strata': {'bridge/hard': 50, 'comparison/hard': 50}}
```

Separate actual validation command, normal sandbox/read-only:

```powershell
uv run python corpus-documents/scripts/validate_corpus.py --domain default 2>&1 | ForEach-Object {$_.ToString()} | Tee-Object -FilePath corpus-documents/.downloads/t05-a02-default-validation.log; exit $LASTEXITCODE
```

Exit0, actual:

```text
CORPUS VALIDATION: PASS - default; documents=986 QA=100 seed=42 source_sha256=c20b638ca82b21d04fe12e14ff417ad05153d4d215a65de54497fca4e972f7c6
```

Validation re-decodes pinnedParquet and compares exactconvertedJSON, regenerated
sample/gold/type/level/facts, documentbodies/QA/index/report, every991receipt bytehash/
size/role, measuredcounts and exactmanagedfileset.996paragraphinstances become986
documents after10duplicateinstances; allcontextparagraphs materialized. Live slice
has0titleswithdifferenttext collisions; synthetictests prove that edge case.
No RAG/provider/model benchmark or productioningestion. **DoD-1 PASS** under explicit
user source exception; canonicalCMUdownload itself remains unavailable.

<a id="h-t05-a02-dod2"></a>
### DoD-2 — Actual rerun stability and meaningful synthetic tests

Pre-rerun inline command `.venv/Scripts/python.exe -` records sourcefiles as actual
`sha256_file`+`st_mtime_ns`, aggregate+all defaultfiles, selectedIDlist and original
downloadtimestamp into ignored`.downloads/t05-a02-repro-before.json`; exit0/log
`repro-before.log`: `Recorded actual pre-rerun hashes/mtimes for 993 files and 100 unique selected IDs.`
Separate required rerun, normal sandbox/cache reuse:

```powershell
uv run python corpus-documents/scripts/setup_corpus.py --domain default 2>&1 | ForEach-Object {$_.ToString()} | Tee-Object -FilePath corpus-documents/.downloads/t05-a02-default-setup-rerun.log; exit $LASTEXITCODE
```

Exit0, same exact two-linePASS output as acceptedsetup above. Post-rerun inline
`.venv/Scripts/python.exe -` compares fullfile maps/hash+mtime, IDs/count uniqueness,
timestamp, actual986MD count and calls`validate_default`; exit0/log`repro-after.log`:

```text
REPRODUCIBILITY: PASS - 993 file hashes/mtimes unchanged; 100 IDs unchanged and unique; 986 documents; original download timestamp retained; validator rejects duplicate/unmanaged paths.
downloaded_at=2026-09-17T16:39:41.497557+00:00
selected_ids_sha256=40045c404f9bc627004e7c48bd2df9ac6165be2342595832ed7590487e436d63
converted_json_sha256=b09f53f982e5bd22197c5f2e775bc324c087f438592eb6d95fa5fa3338887d27
```

Actual no-duplicate file sets verified by validator; duplicatepath/content scenarios
covered in unitfaults. Snapshot includes993paths (986docs+3QA+2raw+defaultmanifest+
aggregate). ConvertedJSON hash is conversionbytes, not originalCMUrawhash.

Required defaulttests run separately; earlier33/35PASS logs preserved, final37 adds
two-title multi-hop mapping and existing-ready-data publicationrollback regressions:

```powershell
uv run pytest tests/unit/test_corpus_default.py 2>&1 | ForEach-Object {$_.ToString()} | Tee-Object -FilePath corpus-documents/.downloads/t05-a02-default-tests-completion.log; exit $LASTEXITCODE
```

Exit0, actualexcerpt:

```text
platform win32 -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0
collected 37 items
tests\unit\test_corpus_default.py .....................................  [100%]
============================= 37 passed in 56.53s =============================
```

Tests are synthetic/no network and never liveacceptance substitutes. Cover supporting
versus distractors/multiple supporttitles, originalgold/type/level, same-titledifferent
content and sharedparagraph dedup, no provenance/goldinMD, sourceorder-independent
seed42sampling/differentseeds/exhaustedstrata/hardonlysource, invalidsource/ambiguous
withinQA title/boolindex/undersizedsource, exactParquetconversion, anomalyoutside
sample preservesIDs/gold and inside fails withoutresampling, rerunhashes/mtime/time,
download/stagedvalidation/directoryrename/aggregate/KeyboardInterrupt rollback including
existingreadydata, cache/lock/no userfileoverwrite, primarypin/convertedJSON/gold/support/
document/duplicate/missing/receiptcorruption rejection. **DoD-2 PASS:100realQA and
stableactualrerun;37meaningfultests,0skip.**

<a id="h-t05-a02-quality"></a>
### D2 — Locked environment and applicable shared quality checks

Approved public PyPI metadata read `Invoke-RestMethod https://pypi.org/pypi/pyarrow/json
-TimeoutSec20`, exit0, actual`pyarrow latest=25.0.1 python=>=3.10`; exactpin in existingdevgroup.
Separate `uv lock` with envprefix/tee`corpus-documents/.downloads/t05-a02-lock.log`,
approved network, exit0: `Resolved 78 packages in 7.31s` / `Added pyarrow v25.0.1`.
Separate actual command:

```powershell
uv sync --locked --group dev --group api 2>&1 | ForEach-Object {$_.ToString()} | Tee-Object -FilePath corpus-documents/.downloads/t05-a02-sync.log; exit $LASTEXITCODE
```

Approved publicPyPI download, exit0, realexcerpt:

```text
Resolved 78 packages in 1ms
Downloading pyarrow (26.7MiB)
 Downloaded pyarrow
Prepared 2 packages in 1m 19s
Uninstalled 1 package in 7ms
Installed 2 packages in 414ms
 + pyarrow==25.0.1
 ~ rag-core==0.1.0 (from file:///C:/Users/Admin/Documents/GitHub/rag-core)
```

Dev-onlyreader; `docker/api.Dockerfile:14` remains
`uv sync --locked --no-dev --group api --no-editable`, no pyarrow/API dependency addition.

```powershell
uv run ruff check . 2>&1 | ForEach-Object {$_.ToString()} | Tee-Object -FilePath corpus-documents/.downloads/t05-a02-ruff-final.log; exit $LASTEXITCODE
uv run mypy src corpus-documents/scripts 2>&1 | ForEach-Object {$_.ToString()} | Tee-Object -FilePath corpus-documents/.downloads/t05-a02-mypy-final.log; exit $LASTEXITCODE
uv run pytest tests/unit/test_corpus_common.py 2>&1 | ForEach-Object {$_.ToString()} | Tee-Object -FilePath corpus-documents/.downloads/t05-a02-common-tests-final.log; exit $LASTEXITCODE
```

Each command ran separately, each exit0, expected relevantquality/stricttyping/no
regression or liveunitdownload. Actual respectively`All checks passed!`,
`Success: no issues found in 15 source files`, and:

```text
collected 82 items
tests\unit\test_corpus_common.py ....................................... [ 47%]
...........................................                              [100%]
============================= 82 passed in 10.48s =============================
```

Commonunavailable regressions now skip implementeddefaultCLI networkcalls, mock only
its failure in a unit test; unimplementeddomains/all setup still nonzero/nonmutation.
Readydefault metadata expected and fabricatednotdownloaded checks constructed from
explicitsyntheticnotdownloaded state. Added exactHFURL/publishedpin/HTTPSsigneddelivery
scope tests; existingdownload/path/JSON/schema tests retained. Alllogs public/synthetic,
ignored`corpus-documents/.downloads/`; no secrets/privatecontent to redact. Signed
query contents intentionally never emitted (hostdiagnostic prints boolean only).

<a id="h-t05-a02-review"></a>
### D1/D3/D4/D5/D6 — Completion review boundary

D1 dependency/scope/prompt and D3 eachliveDoD/commands/config/exit/actual evidence
above; D4 README/RUNBOOK/corpusREADME/licenses/tasks/handoff/summary and user-approved
P11 exception updated alongsideimplementation. D5 no DB/index/API schema migration:
threev1corpus schemas unchanged; exactsource provenance differs by explicitlyapproved
exception. RawParquet/convertedJSON/documents/cache/logs ignored; lightweightnormalized
QA/index/report withverifiedCC-BY-SA attribution/change notices only. Sourcecomment,
license/data hygiene/readerrollback/cachestamp limits preserved. Detailed diff/secrets/
docs/explicitstage/actualcommit checks appended below after execution. Commit subject
`feat(T05): prepare HotpotQA evaluation corpus`; actualhash/end outside owncommit,
COMPLETE only if those checks+commit+rootreview succeed. No nexttask assigned.

#### Executed D1/D4/D5 review checks

Separate command`git diff --check; exit $LASTEXITCODE`, exit0/stdoutempty (whitespaceclean).
Final code diff/read reviewed `common/setup/validate/prepare_default`, default/common
tests, pyproject/lock, authorizedP11exception and docs/inventory/aggregate/report:
supporting-only mapping/distractors, faithfulsemanticconversion, goldanomaly handling,
fixedsource/must-matchpin, safe staging/rollback/no userfileoverwrite, no signedquery
logging or API/core imports. No unreviewed change outside22candidatepaths.

Separate command with uv envprefix, exit0:

```powershell
uv run python scripts/check_docs.py 2>&1 | ForEach-Object {$_.ToString()} | Tee-Object -FilePath corpus-documents/.downloads/t05-a02-docs.log; exit $LASTEXITCODE
```

Actualoutput:

```text
PASS UTF-8/nonempty Markdown: 10 files
PASS internal links/anchors: 201
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```

Final Ruff command uses sameenvprefix/`uv run ruff check .`/tee
`corpus-documents/.downloads/t05-a02-ruff-completion.log`, exit0, `All checks passed!`.
Only errorwording/comments/inventory assembly timestamp were clarified after quality;
no tested behavior changed. Inventory notes now distinguish publishedsourcepin from
independentlymeasured matchingT05bytes/7405rows; otherdomainentries unchanged.

Actual scope/secrets/artifact/prompt command, exit0:

```powershell
$candidate=@('README.md','RUNBOOK.md','docs/tasks.md','docs/handoffs.md','docs/implementation-summary.md','docs/plan.md','corpus-documents/README.md','corpus-documents/licenses/README.md','corpus-documents/source-license-inventory.json','corpus-documents/manifest.json','corpus-documents/default/manifest.json','corpus-documents/default/qa/eval.jsonl','corpus-documents/default/qa/documents.json','corpus-documents/default/qa/preparation.json','corpus-documents/scripts/common.py','corpus-documents/scripts/setup_corpus.py','corpus-documents/scripts/validate_corpus.py','corpus-documents/scripts/prepare_default.py','tests/unit/test_corpus_common.py','tests/unit/test_corpus_default.py','pyproject.toml','uv.lock'); $changed=@(git diff --name-only); $untracked=@(git ls-files --others --exclude-standard); if(@(Compare-Object ($candidate | Sort-Object) (($changed+$untracked) | Sort-Object)).Count -ne 0){throw 'Out-of-scope or missing candidate path'}; $items=@($candidate | ForEach-Object {Get-Item -LiteralPath $_}); if(@($items | Where-Object Length -gt 1048576).Count -ne 0){throw 'Candidate file larger than1MiB'}; $suspicious=@(rg -l '(sk-[A-Za-z0-9_-]{20,}|AKIA[A-Z0-9]{16}|-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----|Signature=[A-Za-z0-9_-]{20,})' -- $candidate); if($suspicious.Count -ne 0){throw 'Credential or signed-query marker found; inspect without printing values'}; $trackedSecrets=@(git ls-files -- .env .local); if($trackedSecrets.Count -ne 0){throw 'Unexpected tracked local secret path'}; $promptPath='corpus-documents/Codex Prompt – Build RAG Evaluation Corpus.md'; $blob=(git hash-object --no-filters -- "$promptPath").Trim(); $sha=(Get-FileHash -Algorithm SHA256 -LiteralPath $promptPath).Hash; if($blob -ne '81ab3c77530722968d847391d8095284f1a874a9' -or $sha -ne '7EC6E58AE4C24DB27AF4320BCB30222BBF2B67961D99C62980CEA4410AEE2C46'){throw 'Original prompt bytes changed'}; $paths=@('corpus-documents/default/raw/hf-hotpotqa-distractor-validation.parquet','corpus-documents/default/raw/hotpot_dev_distractor_v1.json','corpus-documents/default/documents/sample.md','corpus-documents/.downloads/hf-hotpotqa-download.json','.uv-cache/sample','.env'); $ignored=@(git check-ignore -v --no-index -- $paths); if($ignored.Count -ne $paths.Count){throw 'Corpus/cache/secret ignore mismatch'}; $ignored; Write-Output "PASS candidate22/changed22; out_of_scope0; files_over1MiB0; credential_markers0; tracked_local_secrets0"; Write-Output "PASS original prompt blob=$blob SHA256=$sha"; Write-Output 'PASS raw/Parquet/materializeddocuments/cache/logs/secrets excluded; licensed lightweight QA/metadata permitted'; git diff --check; exit $LASTEXITCODE
```

Actualexcerpt (baselineglobalignorewarning omitted here, retained atbaseline):

```text
.gitignore:44:corpus-documents/*/raw/ corpus-documents/default/raw/hf-hotpotqa-distractor-validation.parquet
.gitignore:44:corpus-documents/*/raw/ corpus-documents/default/raw/hotpot_dev_distractor_v1.json
.gitignore:45:corpus-documents/*/documents/ corpus-documents/default/documents/sample.md
.gitignore:46:corpus-documents/.downloads/ corpus-documents/.downloads/hf-hotpotqa-download.json
.gitignore:10:.uv-cache/ .uv-cache/sample
.gitignore:22:.env .env
PASS candidate22/changed22; out_of_scope0; files_over1MiB0; credential_markers0; tracked_local_secrets0
PASS original prompt blob=81ab3c77530722968d847391d8095284f1a874a9 SHA256=7EC6E58AE4C24DB27AF4320BCB30222BBF2B67961D99C62980CEA4410AEE2C46
PASS raw/Parquet/materializeddocuments/cache/logs/secrets excluded; licensed lightweight QA/metadata permitted
```

Expected no out-of-scopefiles/secrets/rawdata/weights/cache and promptunchanged,
actualPASS. LightweightQA sizes measured138452B/index465747B/report5041B; no file
over1MiB. D1–D5PASS with the evidence above; D6 explicitstaging/cachedscope/commit
is finalstep. Successfulcommit/rootruntime/diff/DoD acceptance required for COMPLETE.

#### D6 actual stage/cached checks and final commit boundary

Original inline command text is retained verbatim in ignored public/synthetic
`corpus-documents/.downloads/t05-a02-repro-before.ps1`, `t05-a02-repro-after.ps1`,
`t05-a02-source-diagnostics.ps1` and `t05-a02-selection-diagnostics.ps1` (same directory).
These are evidence copies of the earlier commands, not additional reruns or tracked
scripts; outputs/exits above remain original. The first evidence-artifact patch failed
on mismatched handoff context and made no changes; corrected patch succeeded.

After evidence append, separate docscheck with sameuvprefix/tee
`.downloads/t05-a02-docs-completion.log`, exit0, same10Markdown/201links/37tasks/
81edges acyclic PASS. Separate `uv run python corpus-documents/scripts/validate_corpus.py --metadata-only`
with sameprefix/tee`.downloads/t05-a02-metadata-completion.log`, exit0, actual
`CORPUS METADATA: PASS - 3 domain manifests + inventory; corpus data NOT validated.`

Explicit Git staging, approved `.git` mutation, exit0/stdoutempty:

```powershell
git add -- README.md RUNBOOK.md docs/tasks.md docs/handoffs.md docs/implementation-summary.md docs/plan.md corpus-documents/README.md corpus-documents/licenses/README.md corpus-documents/source-license-inventory.json corpus-documents/manifest.json corpus-documents/default/manifest.json corpus-documents/default/qa/eval.jsonl corpus-documents/default/qa/documents.json corpus-documents/default/qa/preparation.json corpus-documents/scripts/common.py corpus-documents/scripts/setup_corpus.py corpus-documents/scripts/validate_corpus.py corpus-documents/scripts/prepare_default.py tests/unit/test_corpus_common.py tests/unit/test_corpus_default.py pyproject.toml uv.lock
```

Cached `git diff --cached --check`, exact22pathset assertion against candidatearray,
no unstaged/untracked assertions and `git diff --cached --stat`, exit0; actualexcerpt
before this evidence-only append:

```text
22 files changed, 18725 insertions(+), 87 deletions(-)
PASS staged exact22 T05 files; whitespace clean; no unstaged/untracked paths
```

All stagedcode/tests/licensedQA/docs reviewed; raw/weights/cache/secrets absent.
Restage onlythishandoff; repeat cachedwhitespace/22scope/no-unstaged checks, then
`git commit -m "feat(T05): prepare HotpotQA evaluation corpus"`. Actualhash/end/output
returnedpostcommit to root, never amendowncommit. COMPLETE candidate takes effect
only after actualcommit and rootruntime/diff/DoD review; failure keepswork/blocker.

<a id="h-t06-a01"></a>
## H-T06-A01 — Phase 1 / T06 / runtime quota recovery

Exact runtime event before any task action:

```text
Agent errored: You've hit your usage limit. Upgrade to Pro (https://chatgpt.com/explore/pro), visit https://chatgpt.com/codex/settings/usage to purchase more credits or try again at 4:19 AM.
```

Worker `/root/t06_a01` did not execute shell commands, write repo files, run validation,
or create a commit. No start/end timestamp is invented. User continued on 2026-09-19;
Orchestrator spawned fresh T06-A02 rather than reusing A01.

<a id="h-t06-a02"></a>
## H-T06-A02 — Phase 1 / T06 / attempt T06-A02

### Identity, accepted dependency, baseline and scope

- Worker `/root/t06_a02`, requested `gpt-5.6-sol`/`xhigh`, fresh
  `fork_turns="none"`; actual runtime metadata is an Orchestrator acceptance check.
  Started 2026-09-19 16:52 +07:00. No child agent or next task.
- Root accepted T05 commit `a2a94fbba00ee8c2f6462134af03035a86f524e3`
  (`feat(T05): prepare HotpotQA evaluation corpus`) after source/test/diff/evidence
  and Sol/xhigh runtime review. Accepted T04 is
  `ad49ecc53a1998758f419e00ac5d03bf468ba989`.
- CWD for commands: `C:\Users\Admin\Documents\GitHub\rag-core`, Windows
  PowerShell, Asia/Bangkok. Task uv config uses `UV_CACHE_DIR=<repo>\.uv-cache`
  and `UV_PYTHON_INSTALL_DIR=<repo>\.uv-python`; no DSN/provider/model/inference,
  production storage, DB, index, or service is used.
- Baseline command `git status --short; git branch --show-current; git rev-parse HEAD;
  git log -1 --format='%H%n%s'`, exit0. Actual output, aside from the known global
  Git-ignore permission warning:

```text
main
a2a94fbba00ee8c2f6462134af03035a86f524e3
a2a94fbba00ee8c2f6462134af03035a86f524e3
feat(T05): prepare HotpotQA evaluation corpus
```

Worktree was clean. Read AGENTS, complete T05/T04 notes/evidence/interfaces,
P01/P07/P11/P13/P14, complete original corpus prompt, README/RUNBOOK and corpus
README/license/inventory/manifests/scripts/tests before code. Allowed scope and plan
are recorded under T06 in `docs/tasks.md`. Existing authorization covers local
official FinanceBench QA/PDF downloads and evaluation; it does not resolve upstream
redistribution/commercial applicability. Raw/PDF and normalized FinanceBench QA will
remain ignored/local while that applicability remains unresolved.

<a id="h-t06-a02-sources"></a>
### Official sources, exact PDF selection and rights evidence

Pinned JSONL files were downloaded to the ignored local cache from the two manifest
URLs. Approved public network command exit0; actual measurements:

```text
financebench_open_source.jsonl bytes=929848 sha256=a5a2aa673e573e55675fc3c0f9aa38c1cf59d2abc91edb077534f71f10a71877
financebench_document_information.jsonl bytes=88781 sha256=1c69127783879de8cdadb159d2181f39bc3123b8e0ebf74031c3969d69189575
```

`git hash-object` independently returned upstream blob IDs
`4aef1d43a443474ba193f158f2baf70550ff528d` and
`decdfa948630f289d05cc0048417b3b9107cfb9f`, matching the manifest pins.
Actual strict parse: 150 QA, 361 metadata rows/360 unique names,84 referenced
document names,189 evidence records, all `OPEN_SOURCE`; no QA/evidence document
missing metadata. Source pages min0/max303. The raw source has50 null
`question_reasoning` and50 null `justification` values; normalization preserves null.
Two metadata rows conflict only for unreferenced `FOOTLOCKER_2023_annualreport`
(period2023 vs2022 with otherwise same link/identity); report records it and code
fails if a referenced name is duplicated, without selecting different gold.

Approved read-only official metadata recheck command queried GitHub current main,
pinned recursive tree/README and pinned publisher HF card, exit0; retained public
output `.downloads/t06-a02-source-license-check.log`:

```text
pinned_commit=cc39aeb4afdf33909ee1412188bf89035950c2eb
current_main=cc39aeb4afdf33909ee1412188bf89035950c2eb
tree_truncated=False
tree_pdf_count=368
qa_referenced_pdf_count=84
matched_referenced_pdf_count=84
missing_referenced_pdf_count=0
repository_license_file_count=0
publisher_card_revision=e04404e3a97f69f79c14d42f24981a1c9c3bcd18
publisher_card_license=cc-by-nc-4.0
pinned_readme_matching_lines=7
```

Every PDF URL is the exact `raw.githubusercontent.com/patronus-ai/financebench/<pin>/pdfs/<doc_name>.pdf`
path derived only after QA→metadata resolution. Setup downloaded84 referenced PDFs,
not the other284. The plan's existing authorization covers this local evaluation;
it is not a redistribution/commercial grant. GitHub has no explicit dataset/PDF
grant, the publisher card scope is recorded separately, and company PDF rights remain
separate. Therefore raw JSONL, PDFs and normalized FinanceBench QA/evidence stay
ignored/local; tracked manifest receipts contain no source content.

### Implementation failures found and fixed in this attempt

- First real setup command was the DoD setup command below, exit1, actual output
  `CORPUS SETUP: FAIL - document: Download failed after 1 attempt(s): source verification or local publication failure; no data acceptance`.
  Direct strict-parser diagnosis exit1 showed `CorpusError: FinanceBench justification
  must be a nonempty string`. Inspection proved50 official null justifications and50
  null reasoning labels. Parser/normalizer now accepts only null or nonempty source
  values and preserves them exactly; no replacement text was invented.
- Next metadata diagnosis found the unreferenced conflicting pair above. It is preserved
  in raw, reported, excluded from no QA, and referenced duplicates fail. No row was
  edited/dropped. Failed stage stayed ignored for forensics; published manifest stayed
  `not_downloaded`.
- Second real setup, same command, exit1 during the seventh PDF with actual traceback
  ending `pypdf.errors.DependencyError: cryptography>=3.1 is required for AES algorithm`.
  Added exact dev-only `pypdf[crypto]==6.19.0`; locked resolution added
  cryptography50.0.1/cffi2.1.1/pycparser3.0. Resumable verified receipts reused the
  six already accepted PDFs; no gate was bypassed. Third setup below passed all84.
- First final Ruff command exit1 on `I001` for the new test import block. Scoped Ruff
  `--fix` only organized imports; independent full Ruff below passed. An optional
  PowerShell aggregate-hash diagnostic used unavailable `.NET SHA256.HashData` and
  errored after all printed measurements; it was not treated as a check. A portable
  rerun separately confirmed189 evidence/pages0–303/minimum remaining page1/0 invalid.

<a id="h-t06-a02-dod1"></a>
### DoD-1 — Separate real setup and Document validation

Setup command, CWD/config as above, approved official public downloads, final exit0.
Expected: exact pinned open QA→metadata→referenced real PDFs; unchanged gold and
valid zero-based pages. Actual output retained at `.downloads/t06-a02-setup-third.log`:

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR=Join-Path (Get-Location) '.uv-python'; uv run python corpus-documents/scripts/setup_corpus.py --domain document 2>&1 | ForEach-Object {$_.ToString()} | Tee-Object -FilePath corpus-documents/.downloads/t06-a02-setup-third.log; exit $LASTEXITCODE
```

```text
CORPUS SETUP: PASS - document/FinanceBench; PDFs=84 QA=150 evidence=189 page_indexing=zero_based source_sha256=a5a2aa673e573e55675fc3c0f9aa38c1cf59d2abc91edb077534f71f10a71877
```

Measured real PDFs:165,527,662 bytes/12,013 physical pages; per-PDF page count
min4/max549. Evidence pages0–303, minimum one physical page remains after the largest
referenced zero-based page,0 out-of-range. Normalized QA SHA256
`7d7dbf4760f7f8f1f2a9ff60216a0a8709cee26d6c9f65773a773441a2768869`;
document index `089b8f1c132ffd66cc6fb67f9322eedeb10059f4fd5b8d237afa5b178dae871c`;
89 artifact receipts/checksums. The validator rebuilds these bytes from pinned raw,
compares every answer/evidence/full-page text/justification/metadata field, opens every
PDF and checks exact files/receipts. No fake PDF or mock source was used.

Separate validator final command, exit0; output retained at
`.downloads/t06-a02-validation-final.log`:

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR=Join-Path (Get-Location) '.uv-python'; uv run python corpus-documents/scripts/validate_corpus.py --domain document 2>&1 | ForEach-Object {$_.ToString()} | Tee-Object -FilePath corpus-documents/.downloads/t06-a02-validation-final.log; exit $LASTEXITCODE
```

```text
CORPUS VALIDATION: PASS - document; PDFs=84 QA=150 evidence=189 page_indexing=zero_based source_sha256=a5a2aa673e573e55675fc3c0f9aa38c1cf59d2abc91edb077534f71f10a71877
```

**DoD-1 PASS.** Product citations remain physical one-based; only a future eval
adapter converts these preserved zero-based gold pages.

<a id="h-t06-a02-dod2"></a>
### DoD-2 — Actual rerun stability and meaningful Document tests

Rerun command captured all root aggregate + Document file SHA256/UTC mtime values and
all84 transport-cache PDF values in memory, invoked the same setup command, then
compared. Command exit0; setup output as above followed by:

```text
RERUN published_files=91 changed_hash_or_mtime=0 cache_pdfs=84 changed_cache_hash_or_mtime=0 downloaded_at_stable=True artifacts=89
```

The 150 normalized IDs and QA content hash also stayed unchanged; verified cache pins
made every PDF call local reuse, so no duplicate network download or extra PDF file.

Required unit command, final exit0; real PDF byte fixtures use pypdf but all external
transport is injected, no live-data substitution. Full output at
`.downloads/t06-a02-document-tests-final.log`:

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR=Join-Path (Get-Location) '.uv-python'; uv run pytest tests/unit/test_corpus_document.py 2>&1 | ForEach-Object {$_.ToString()} | Tee-Object -FilePath corpus-documents/.downloads/t06-a02-document-tests-final.log; exit $LASTEXITCODE
```

```text
collected 19 items
tests\unit\test_corpus_document.py ...................                   [100%]
============================= 19 passed in 13.07s =============================
```

Coverage: original filename and unambiguous mapping; exact answers/evidence/full-page
text/justification/null metadata; zero-based last page accepted/out-of-range refused;
closed/invalid/duplicate IDs and cross-document evidence refused; unreferenced metadata
anomaly reported/referenced ambiguity refused; real PDF parse/count/non-PDF refusal;
complete prepare/validate/rerun/no-redownload; gold/evidence/page/PDF/receipt/extra-file
corruption; unknown user file, writer lock and aggregate publication rollback.
**DoD-2 PASS.**

### D2 — Locked environment, quality and regressions

Each command ran separately with the task uv env/CWD above and exit0:

```text
uv sync --locked --group dev --group api
Resolved 82 packages in 1ms
Checked 49 packages in 2ms

uv run ruff check .
All checks passed!

uv run mypy src corpus-documents/scripts
Success: no issues found in 16 source files

uv run pytest tests/unit/test_corpus_common.py
collected 81 items; 81 passed in 2.61s

uv run pytest tests/unit/test_corpus_default.py
collected 37 items; 37 passed in 30.02s
```

Logs: `.downloads/t06-a02-sync.log`, `t06-a02-ruff-final.log`,
`t06-a02-mypy.log`, `t06-a02-common-tests.log`, `t06-a02-default-tests.log`.
No skip marker. T02/T03 integration/contracts were not rerun because application/
Compose/API contracts are unchanged; default/common are the genuinely affected
corpus regressions.

<a id="h-t06-a02-review"></a>
### D1/D3/D4/D5/D6 — Scope, docs, source review and completion boundary

- **D1 PASS:** accepted T05/T04 full notes/evidence/interfaces read; clean baseline;
  manual implementation/test/manifest/docs diff review. Exact scope is18 files below;
  no T07/bilingual/API/model/retrieval/Scarlet/server work. Original prompt SHA256
  `7ec6e58ae4c24db27af4320bcb30222bbf2b67961d99c62980cea4410aee2c46`
  and Git blob `81ab3c77530722968d847391d8095284f1a874a9` unchanged.
- **D3 PASS:** both required DoD commands ran separately with actual cwd/config/exit/
  output above; source checks and two corrected live failures are not hidden. Synthetic
  tests are not called live verification.
- **D4 PASS:** root README/RUNBOOK, corpus README/licenses/inventory/manifests,
  task/handoff/Phase1-T06-A02 summary updated with working commands, hashes/counts,
  zero/one-based boundary, null/anomaly facts, rights/cache/rollback/crash/T08 limits.
  `uv run python scripts/check_docs.py`, exit0:10Markdown/210links/37tasks/81edges
  acyclic PASS. Metadata-only validator separately exit0:
  `CORPUS METADATA: PASS - 3 domain manifests + inventory; corpus data NOT validated.`
- **D5 PASS:** official pin/tree/blob/source hashes and current notices reviewed;
  real manifest has84 PDF +2 raw +3 QA receipts. `.gitignore` proofs show raw/PDF and
  narrowly DocumentQA ignored; no raw source/PDF/normalized gold/cache/log/secret/model
  staged. No credentials/query tokens printed. License remains unresolved honestly;
  no source override. Schema v1 unchanged and validators cover generated receipts.
- **D6 initial stage/review PASS:** approved exact `git add -- <18 explicit paths>`
  exit0/stdoutempty. Cached path-set assertion, `git diff --cached --check`, no
  unstaged/untracked assertion and status/stat command exit0. Actual output:

```text
PASS staged exact18 T06 files; whitespace clean; no unstaged/untracked paths
18 files changed, 2198 insertions(+), 82 deletions(-)
```

  Status contained16 modified +2 added expected paths only. After this evidence append,
  restage only `docs/handoffs.md`, repeat exact18/whitespace/no-unstaged review, then
  `git commit -m "feat(T06): prepare FinanceBench evaluation corpus"`. COMPLETE
  candidate takes effect only after successful commit and root runtime/diff/DoD review;
  actual hash/end are returned outside the commit, never amended into itself.

Known limits: tracked ready manifests plus ignored data do not yet reproduce from a
fresh clone; T08 owns clean-state recovery/all-domain setup. Writer rollback covers
ordinary exceptions/KeyboardInterrupt, while hard termination needs operator inspection
of retained lock/stage/backup. No benchmark score, provider/model, production ingestion,
DB/index/API migration or server deployment. Next action is root acceptance, then a
fresh T07 worker; this attempt does not continue.

<a id="h-t06-a03"></a>
## H-T06-A03 — Phase 1 / T06 / attempt T06-A03 — Acceptance evidence closure

Root reviewed A02 implementation commit `6863abf221db2d387e141656610c710ceac14dff`,
technical DoD, and actual Sol/xhigh runtime (thread
`01a0b914-5327-7d20-866b-6f60b4f65bed`, ended 2026-09-19 17:25:14 +07:00).
A03 began 2026-09-22 08:43 +07:00 with clean `main`/that HEAD and no dirty or
untracked files. CWD for all commands is
`C:\Users\Admin\Documents\GitHub\rag-core`, PowerShell. Historical commands below
were recovered verbatim from the A02 public runtime `custom_tool_call` inputs in
`rollout-2026-09-19T16-51-52-01a0b914-5327-7d20-866b-6f60b4f65bed.jsonl`;
the matching `custom_tool_call_output` blocks gave the excerpts below. This is
archival recovery, not an A03 rerun. A02 handoff records nested exit0; the preserved
`functions.exec` wrapper output says `Script completed` but does not separately
print the nested `exec_command.exit_code`. Original A02 source/DoD failures remain
unchanged above. No data, code, tests, config, source pins or rights policy changed.

### Recovered A02 DoD-2 rerun command

Runtime call `call_xQeQkQyEM2vutuZdz3KzH6v9`; original uv cache/Python-install
dirs were `<repo>\.uv-cache`/`<repo>\.uv-python`. The command captured aggregate
+ Document published file SHA256/UTC mtime and all84 cached PDF SHA256/UTC mtime
before setup, compared them afterward and exited nonzero on drift:

```powershell
$ErrorActionPreference='Stop'; $env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR=Join-Path (Get-Location) '.uv-python'; $paths=@((Resolve-Path -LiteralPath 'corpus-documents\manifest.json').Path)+@(Get-ChildItem -LiteralPath 'corpus-documents\document' -Recurse -File | ForEach-Object {$_.FullName}); $before=@{}; foreach($p in $paths){$item=Get-Item -LiteralPath $p; $before[$p]=@((Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant(),$item.LastWriteTimeUtc.Ticks)}; $cachePaths=@(Get-ChildItem -LiteralPath 'corpus-documents\.downloads\financebench-pdfs' -File | ForEach-Object {$_.FullName}); $cacheBefore=@{}; foreach($p in $cachePaths){$item=Get-Item -LiteralPath $p; $cacheBefore[$p]=@((Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant(),$item.LastWriteTimeUtc.Ticks)}; $manifestBefore=Get-Content -LiteralPath 'corpus-documents\document\manifest.json' -Raw | ConvertFrom-Json; & uv run python corpus-documents/scripts/setup_corpus.py --domain document 2>&1 | ForEach-Object {$_.ToString()} | Tee-Object -FilePath corpus-documents/.downloads/t06-a02-setup-rerun.log; if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}; $changed=@(); foreach($p in $paths){$item=Get-Item -LiteralPath $p; $now=@((Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant(),$item.LastWriteTimeUtc.Ticks); if($now[0] -ne $before[$p][0] -or $now[1] -ne $before[$p][1]){$changed+=$p}}; $cacheChanged=@(); foreach($p in $cachePaths){$item=Get-Item -LiteralPath $p; $now=@((Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant(),$item.LastWriteTimeUtc.Ticks); if($now[0] -ne $cacheBefore[$p][0] -or $now[1] -ne $cacheBefore[$p][1]){$cacheChanged+=$p}}; $manifestAfter=Get-Content -LiteralPath 'corpus-documents\document\manifest.json' -Raw | ConvertFrom-Json; Write-Output ("RERUN published_files=$($paths.Count) changed_hash_or_mtime=$($changed.Count) cache_pdfs=$($cachePaths.Count) changed_cache_hash_or_mtime=$($cacheChanged.Count) downloaded_at_stable=$($manifestBefore.downloaded_at -eq $manifestAfter.downloaded_at) artifacts=$($manifestAfter.artifacts.Count)"); if($changed.Count -or $cacheChanged.Count -or $manifestBefore.downloaded_at -ne $manifestAfter.downloaded_at){exit 3}; exit 0
```

Actual preserved output (also setup log `corpus-documents/.downloads/t06-a02-setup-rerun.log`):

```text
CORPUS SETUP: PASS - document/FinanceBench; PDFs=84 QA=150 evidence=189 page_indexing=zero_based source_sha256=a5a2aa673e573e55675fc3c0f9aa38c1cf59d2abc91edb077534f71f10a71877
RERUN published_files=91 changed_hash_or_mtime=0 cache_pdfs=84 changed_cache_hash_or_mtime=0 downloaded_at_stable=True artifacts=89
```

DoD-1 setup/validator exact commands, exits and output remain at
[H-T06-A02 DoD-1](#h-t06-a02-dod1); DoD-2 19-test exact command/output remain at
[H-T06-A02 DoD-2](#h-t06-a02-dod2). All A02 DoD evidence is **REUSED**, dated
2026-09-19, from implementation commit `6863abf`.

### Recovered A02 official source/license metadata command

Runtime call `call_wE3ZYzh2qoZMPhCBMwSRaQKb` was an approved read-only official
GitHub/Hugging Face metadata check, not a rights grant. It printed counts/pins
only; raw source content was not logged:

```powershell
$ErrorActionPreference='Stop'; $pin='cc39aeb4afdf33909ee1412188bf89035950c2eb'; $repo=Invoke-RestMethod -Uri 'https://api.github.com/repos/patronus-ai/financebench/commits/main' -TimeoutSec 30; $tree=Invoke-RestMethod -Uri ('https://api.github.com/repos/patronus-ai/financebench/git/trees/'+$pin+'?recursive=1') -TimeoutSec 60; $readme=(Invoke-WebRequest -Uri ('https://raw.githubusercontent.com/patronus-ai/financebench/'+$pin+'/README.md') -UseBasicParsing -TimeoutSec 30).Content; $hf=Invoke-RestMethod -Uri 'https://huggingface.co/api/datasets/PatronusAI/financebench/revision/e04404e3a97f69f79c14d42f24981a1c9c3bcd18' -TimeoutSec 30; $qa=Get-Content -LiteralPath 'corpus-documents\.downloads\financebench_open_source.jsonl'|ForEach-Object {$_|ConvertFrom-Json}; $names=@($qa.doc_name+$qa.evidence.doc_name|Sort-Object -Unique); $pdfs=@($tree.tree|Where-Object {$_.type -eq 'blob' -and $_.path -like 'pdfs/*.pdf'}); $referenced=@($pdfs|Where-Object {[IO.Path]::GetFileNameWithoutExtension($_.path) -in $names}); $missing=@($names|Where-Object {$n=$_; ('pdfs/'+$n+'.pdf') -notin $pdfs.path}); $licenseFiles=@($tree.tree|Where-Object {$_.path -match '(^|/)(LICENSE|COPYING)(\.|$)'}); $openLines=@($readme -split "`n"|Where-Object {$_ -match 'open.source|n=150|Citation|license'}); @("pinned_commit=$pin","current_main=$($repo.sha)","tree_truncated=$($tree.truncated)","tree_pdf_count=$($pdfs.Count)","qa_referenced_pdf_count=$($names.Count)","matched_referenced_pdf_count=$($referenced.Count)","missing_referenced_pdf_count=$($missing.Count)","repository_license_file_count=$($licenseFiles.Count)","publisher_card_revision=$($hf.sha)","publisher_card_license=$($hf.cardData.license)","pinned_readme_matching_lines=$($openLines.Count)") | Tee-Object -FilePath 'corpus-documents\.downloads\t06-a02-source-license-check.log'; exit 0
```

Actual preserved output, also in ignored
`corpus-documents/.downloads/t06-a02-source-license-check.log`:

```text
pinned_commit=cc39aeb4afdf33909ee1412188bf89035950c2eb
current_main=cc39aeb4afdf33909ee1412188bf89035950c2eb
tree_truncated=False
tree_pdf_count=368
qa_referenced_pdf_count=84
matched_referenced_pdf_count=84
missing_referenced_pdf_count=0
repository_license_file_count=0
publisher_card_revision=e04404e3a97f69f79c14d42f24981a1c9c3bcd18
publisher_card_license=cc-by-nc-4.0
pinned_readme_matching_lines=7
```

### Recovered A02 D6 explicit staging and scope assertion

Runtime call `call_4zzD46Dm6OrAF23I54FBaWW1`, original staging command:

```powershell
git add -- .gitignore README.md RUNBOOK.md corpus-documents/README.md corpus-documents/document/manifest.json corpus-documents/licenses/README.md corpus-documents/manifest.json corpus-documents/scripts/prepare_document.py corpus-documents/scripts/setup_corpus.py corpus-documents/scripts/validate_corpus.py corpus-documents/source-license-inventory.json docs/handoffs.md docs/implementation-summary.md docs/tasks.md pyproject.toml tests/unit/test_corpus_common.py tests/unit/test_corpus_document.py uv.lock
```

Preserved wrapper output: `Script completed`, no stdout; A02 records exit0.
Runtime call `call_0A6zNmQ9ZMc8EDbNnfdMAxsh`, original exact18 cached
path assertion/whitespace/no-unstaged-or-untracked review command:

```powershell
$ErrorActionPreference='Stop'; $expected=@('.gitignore','README.md','RUNBOOK.md','corpus-documents/README.md','corpus-documents/document/manifest.json','corpus-documents/licenses/README.md','corpus-documents/manifest.json','corpus-documents/scripts/prepare_document.py','corpus-documents/scripts/setup_corpus.py','corpus-documents/scripts/validate_corpus.py','corpus-documents/source-license-inventory.json','docs/handoffs.md','docs/implementation-summary.md','docs/tasks.md','pyproject.toml','tests/unit/test_corpus_common.py','tests/unit/test_corpus_document.py','uv.lock')|Sort-Object; $cached=@(git diff --cached --name-only|Sort-Object); $missing=@($expected|Where-Object {$_ -notin $cached}); $extra=@($cached|Where-Object {$_ -notin $expected}); if($missing.Count -or $extra.Count){Write-Output ('missing='+($missing-join ',')); Write-Output ('extra='+($extra-join ',')); exit 2}; git diff --cached --check; if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}; $unstaged=@(git diff --name-only); $untracked=@(git ls-files --others --exclude-standard); if($unstaged.Count -or $untracked.Count){Write-Output ('unstaged='+($unstaged-join ',')); Write-Output ('untracked='+($untracked-join ',')); exit 3}; Write-Output 'PASS staged exact18 T06 files; whitespace clean; no unstaged/untracked paths'; git diff --cached --stat; git status --short
```

Actual preserved excerpt:

```text
PASS staged exact18 T06 files; whitespace clean; no unstaged/untracked paths
18 files changed, 2198 insertions(+), 82 deletions(-)
```

These recovered commands replace the `<18 explicit paths>` shorthand as
provenance; the A02 implementation completion commit remains unchanged.

### A03 D1–D5 actual checks and reused DoD mapping

Environment: Windows PowerShell, CWD `C:\Users\Admin\Documents\GitHub\rag-core`,
uv0.11.16/CPython3.12.4; `UV_CACHE_DIR=<repo>\.uv-cache`,
`UV_PYTHON_INSTALL_DIR=<repo>\.uv-python`. No service, DSN, provider, model,
inference, PDF download, corpus setup, test suite or migration was used in A03.
At baseline `git status --short --branch`, exit0, returned
`## main...origin/main [gone]` with no changed paths; `git log -3 --oneline`,
exit0, began `6863abf feat(T06): prepare FinanceBench evaluation corpus`,
`a2a94fb feat(T05): prepare HotpotQA evaluation corpus`,
`ad49ecc feat(T04): add reproducible corpus tooling`. Git emitted the known
global ignore permission warning without changing exit status.

- **DoD-1 REUSED PASS:** A02's real setup and separate validator, each exit0,
  output at [H-T06-A02 DoD-1](#h-t06-a02-dod1). The same implementation commit
  and local corpus are under review; no A03 claim of new live verification.
- **DoD-2 REUSED PASS:** A02 real rerun command/output recovered above;
  91 published and84 cached PDF hashes/mtimes unchanged, timestamp stable;
  A02's19 Document tests exit0 and report real result at
  [H-T06-A02 DoD-2](#h-t06-a02-dod2).
- **D1 PASS:** `git diff --name-only`, exit0, returned exactly:

```text
README.md
RUNBOOK.md
docs/handoffs.md
docs/implementation-summary.md
docs/tasks.md
```

  `git diff --name-only -- corpus-documents src tests pyproject.toml uv.lock .gitignore docs/plan.md AGENTS.md`,
  exit0/stdout empty. `git ls-files --others --exclude-standard`, exit0/no
  untracked paths (known global ignore warning). `git diff --check`,
  exit0/stdout empty. Dependencies T04/T05 are accepted and their full task
  notes/evidence/interfaces plus P01/P07/P11/P13/P14/P15 were read.
- **D2 PASS (A03 applicable quality):** exact command:

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR=Join-Path (Get-Location) '.uv-python'; uv run python scripts/check_docs.py
```

  Exit0, actual output:

```text
PASS UTF-8/nonempty Markdown: 10 files
PASS internal links/anchors: 217
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```

  A02's locked82/49 sync, Ruff, strict mypy16, 81 common/37 Default/
  19 Document tests are REUSED with 2026-09-19 commands/output at
  [H-T06-A02 D2](#h-t06-a02-review) and preceding A02 sections; no A03 code
  changed that warrants rerunning them.
- **D3 PASS:** exact historical rerun/source/staging/assertion invocations above
  were matched as full strings against the original A02 runtime inputs;
  each check yielded `True`. A02 retained exact DoD-1 setup/validator and
  DoD-2 test commands, CWD/config/output; the archival wrapper's missing
  numeric nested exit field is disclosed above, not reconstructed.
- **D4 PASS:** README/RUNBOOK top status and R00 table now include T06 Document
  VERIFIED local and T07–T36 pending with user pause; task, handoff and
  Phase1/T06/A03 summary updated. Actual docs check output above.
- **D5 PASS:** full five-file diff and `git diff --stat`, exit0, reviewed;
  stat was `5 files changed, 110 insertions(+), 6 deletions(-)` before this
  evidence append. No raw/PDF/normalized QA, payload, secret, model weight,
  source, test, config, schema, API or migration file changed. Original prompt
  `Get-FileHash -LiteralPath 'corpus-documents/Codex Prompt – Build RAG Evaluation Corpus.md' -Algorithm SHA256`,
  exit0, returned SHA256
  `7EC6E58AE4C24DB27AF4320BCB30222BBF2B67961D99C62980CEA4410AEE2C46`;
  `git hash-object -- "corpus-documents/Codex Prompt – Build RAG Evaluation Corpus.md"`,
  exit0, returned `81ab3c77530722968d847391d8095284f1a874a9`.

Historical provenance was verified by a read-only Python scan of exactly the
four cited `custom_tool_call` inputs.

An A03 documentation recheck after the first evidence append used the same exact
command, exit0, with `PASS internal links/anchors: 220` and the other three
output lines unchanged. `git diff --check`, exit0/stdout empty; changed paths
remained the same five.

Exact read-only transcription verification command, exit0:

```powershell
python -X utf8 -c "import json,pathlib; p=pathlib.Path('C:/Users/Admin/.codex/sessions/2026/09/19/rollout-2026-09-19T16-51-52-01a0b914-5327-7d20-866b-6f60b4f65bed.jsonl'); h=pathlib.Path('docs/handoffs.md').read_text(encoding='utf-8'); ids={'call_xQeQkQyEM2vutuZdz3KzH6v9','call_wE3ZYzh2qoZMPhCBMwSRaQKb','call_4zzD46Dm6OrAF23I54FBaWW1','call_0A6zNmQ9ZMc8EDbNnfdMAxsh'}; rows=(json.loads(s) for s in p.open(encoding='utf-8')); xs=[r['payload'] for r in rows if r.get('type')=='response_item' and r.get('payload',{}).get('type')=='custom_tool_call' and r.get('payload',{}).get('call_id') in ids]; print([(x['call_id'],json.JSONDecoder().raw_decode(x['input'].split('tools.exec_command(',1)[1])[0]['cmd'] in h) for x in xs])"
```

Actual output:

Its actual output was:

```text
[('call_xQeQkQyEM2vutuZdz3KzH6v9', True), ('call_wE3ZYzh2qoZMPhCBMwSRaQKb', True), ('call_4zzD46Dm6OrAF23I54FBaWW1', True), ('call_0A6zNmQ9ZMc8EDbNnfdMAxsh', True)]
```

D6 exact-five-file stage, cached review and completion commit follow below.

### A03 D6 — Explicit stage, cached review and completion boundary

Final pre-stage `uv run python scripts/check_docs.py` with the uv env above,
exit0, returned10 Markdown/220 internal links/37 tasks/81 dependencies acyclic
and `DOCUMENTATION CHECK: PASS`; `git diff --check`, exit0/stdout empty;
`git diff --name-only`, exit0, still showed exactly the five permitted files.

First attempted exact stage command, exit1 because this sandbox denies `.git/index.lock`:

```powershell
git add -- README.md RUNBOOK.md docs/tasks.md docs/handoffs.md docs/implementation-summary.md
```

```text
fatal: Unable to create 'C:/Users/Admin/Documents/GitHub/rag-core/.git/index.lock': Permission denied
```

The same exact command was then auto-reviewed with `require_escalated` and
`prefix_rule=["git","add"]`; approved execution exit0/stdout empty. No
identity/config was changed and no hook bypassed. Exact cached review command:

```powershell
$ErrorActionPreference='Stop'; $expected=@('README.md','RUNBOOK.md','docs/handoffs.md','docs/implementation-summary.md','docs/tasks.md')|Sort-Object; $cached=@(git diff --cached --name-only|Sort-Object); $missing=@($expected|Where-Object {$_ -notin $cached}); $extra=@($cached|Where-Object {$_ -notin $expected}); if($missing.Count -or $extra.Count){Write-Output ('missing='+($missing-join ',')); Write-Output ('extra='+($extra-join ',')); exit 2}; git diff --cached --check; if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}; $unstaged=@(git diff --name-only); $untracked=@(git ls-files --others --exclude-standard); if($unstaged.Count -or $untracked.Count){Write-Output ('unstaged='+($unstaged-join ',')); Write-Output ('untracked='+($untracked-join ',')); exit 3}; Write-Output 'PASS staged exact5 T06 documentation files; whitespace clean; no unstaged/untracked paths'; git diff --cached --stat; git status --short; exit 0
```

Exit0; actual excerpt (aside from the pre-existing global Git-ignore warning):

```text
PASS staged exact5 T06 documentation files; whitespace clean; no unstaged/untracked paths
 README.md                      |   2 +-
 RUNBOOK.md                     |   4 +-
 docs/handoffs.md               | 195 ++++++++++++++++++++++++++++++++++++++++-
 docs/implementation-summary.md |   7 ++
 docs/tasks.md                  |   4 +
 5 files changed, 206 insertions(+), 6 deletions(-)
M  README.md
M  RUNBOOK.md
M  docs/handoffs.md
M  docs/implementation-summary.md
M  docs/tasks.md
```

After this evidence append, restage only `docs/handoffs.md`, repeat exact-five
cached scope/whitespace/no-unstaged review, then commit
`docs(T06): finalize acceptance evidence and paused checkpoint`. This is a
documentation supplement to existing T06 implementation commit `6863abf`,
not a second implementation. Formal T06 acceptance follows successful
documentation commit and root review. Actual A03 hash/end/status are reported
outside this self-referential commit; no T07 work is authorized.
