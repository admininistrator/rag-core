# Handoffs — Bàn giao giữa các session

> Current checkpoint ở đầu; lịch sử attempt/evidence append ở dưới. Không xóa output cũ để che lỗi.

## Current checkpoint

- **Current:** Phase 0 / T03 / `T03-A02` đề nghị COMPLETE tại completion commit `feat(T03): define versioned API contracts`, chỉ hợp lệ sau commit thành công và Orchestrator review. Worker `/root/t03_a02`, `gpt-5.6-sol`/`xhigh`, context mới `fork_turns="none"`, spawn/runtime được Orchestrator xác minh; bắt đầu 2026-09-17 11:51 +07:00, ended timestamp/hash/output trả root post-commit. Baseline `main`/`851ff1d10b49b6a4d7ae7e1756f2c2a1b8562e96`, đúng 16 candidate files T03 dirty/untracked; completion scope 17 files tại [T03](tasks.md#t03).
- **Recovery:** A01 đã kết thúc do runtime quota, không có completion commit; đã có contracts/exporter/tests/snapshots/examples và README/RUNBOOK candidate, checkpoint cũ “chưa code/DoD” đã stale. A02 review và thu actual evidence mới; [H-T03-A01](#h-t03-a01) giữ runtime event/report boundary trung thực.
- **Dependencies accepted:** T02 `851ff1d10b49b6a4d7ae7e1756f2c2a1b8562e96`, T01 `ff8069abfd2e41fb9618eb7d35fa22bf220a39d6`, T00 `7025eeac080b481c17f7d68f0290b1ee3e3165e9`; notes/summary/evidence đã đọc. T02 historical evidence phía dưới giữ nguyên.
- **Verified boundary/next:** actual A02 locked sync/Ruff/mypy 11 source/unit 7/contract 83/export +drift 13 ops/2 health/48 schemas/37 synthetic examples/docs/scope/secrets/prompt PASS; explicit stage 17/cached review PASS. Evidence [H-T03-A02](#h-t03-a02). Business/auth/ingestion/retrieval/provider/SSE transport/UI vẫn DESIGNED. Resolve completion hash/current status và root review, rồi fresh worker T04; A02 kết thúc, không tự nhận task sau.
- **Invariants:** mọi query current-session-only, index retained không cấp quyền; app sở hữu source/history. Không sửa prompt corpus/plan/AGENTS, không cloud/server/Scarlet/push/merge. Worker mới từng attempt, chỉ một worker active, Orchestrator read-only.

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
