# Handoffs — Bàn giao giữa các session

> Current checkpoint ở đầu; lịch sử attempt/evidence append ở dưới. Không xóa output cũ để che lỗi.

## Current checkpoint

- **Giai đoạn:** Phase 0 / T01 / attempt T01-A01 đề nghị COMPLETE; hiệu lực khi completion commit thành công và Orchestrator review evidence.
- **Dependency:** T00 COMPLETE tại commit `7025eeac080b481c17f7d68f0290b1ee3e3165e9` (`docs(T00): establish RAG core implementation blueprint`).
- **Branch/starting HEAD:** `main` / `7025eeac080b481c17f7d68f0290b1ee3e3165e9`.
- **Baseline dirty files:** chỉ `?? corpus-documents/`; prompt gốc SHA-256 byte-level `7EC6E58AE4C24DB27AF4320BCB30222BBF2B67961D99C62980CEA4410AEE2C46`, được người dùng giao T01 đưa nguyên bản vào Git.
- **Runtime worker:** record `turn_context` xác minh `gpt-5.6-sol`, effort `xhigh`, turn ID `01a0a5a1-fedd-7a73-801f-d5afc48b106c`, cwd repo; thread riêng parent, phù hợp `fork_turns="none"`.
- **Tooling T01:** `uv 0.11.16` tìm thấy CPython 3.12.4 tại Miniconda khi chạy ngoài filesystem sandbox và tạo `.venv` Python 3.12.4; lock yêu cầu `==3.12.*`. Host `python` vẫn 3.13.2 và không được dùng thay baseline. Cache/install dir local `.uv-cache`/`.uv-python` đã ignore.
- **Implementation:** src package/settings/docs check và quality config đã kiểm chứng; prompt corpus giữ nguyên byte. Chưa chạy app/service/corpus setup. Docker không thuộc T01; Orchestrator preflight daemon riêng và báo server 29.5.2. Không kiểm provider/GPU.
- **Task tiếp theo:** T02 sau khi Orchestrator xác minh commit/diff/evidence T01; không reuse worker T01.
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
