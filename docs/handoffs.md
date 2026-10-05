# Handoffs — Bàn giao giữa các session

T07-A06 closure evidence: [H-T07-A06](#h-t07-a06).

> Current checkpoint ở đầu; lịch sử attempt/evidence append ở dưới. Không xóa output cũ để che lỗi.

## Current checkpoint

- **Current 2026-10-06 / T23-A01 acceptance closure:** direct Codex agent, exact model/effort unavailable, no subagents. Baseline main/T22 `3e6821b814282ef0a6859a9414ecf8f8d29fdf72` equals origin/main (read-only escalation verified). No partial T23 candidate; inherited T07 scratch preserved. DeepSeek HTTPX and Anthropic SDK1.11.0 generate/stream/rewrite implemented with distinct schemas, independent configuration, prompt/output bounds, nullable usage, shared total deadline/bounded retries/no retry after emitted delta/cancel cleanup. DoD-1 synthetic127PASS4.63s and separate DoD-2 config18PASS2.22s; 645regressionPASS200.23s, Ruff/format/mypy85/lock177/OpenAPI/docs/review PASS; final staged commit/push boundary below. Evidence [H-T23-A01](#h-t23-a01), interfaces [S-T23-A01](implementation-summary.md#s-t23-a01). No live provider/model behavior claim; T26 retains real-provider gates. Completion subject `feat(T23): support DeepSeek and Anthropic generation`, COMPLETE effective only after inspected commit succeeds; actual hash/authorized origin/main equality reported post-execution. T24 remains TODO, dependencies ready after closure; STOP T23, no drain/merge/deploy/Scarlet/source/cache/scratch deletion.

- **Current 2026-10-06 / T22-A02 acceptance closure:** direct Codex agent, exact model/effort unavailable, no subagents. User delegates optimal conflict-policy choice; numeric-claim-v1 mapped-source baseline implemented over A01 checkpoint `74bb13019410bc2baf1fe911a2183ff5933716ea` (origin/main verified equal), preserving all partial work/scratch. DoD-1 **14actualCPUreranker/PG/Qdrant PASS103.34s**, separate DoD-2 **14PASS65.89s**,45focused unitPASS0.32s; final regression/quality/review/commit/push at closure below. Evidence [H-T22-A02](#h-t22-a02), interfaces [S-T22-A02](implementation-summary.md#s-t22-a02). Conflict cannot disappear under passage budget, scope/history/foreign guards retained. Threshold calibration T31 pending; semantic contradiction/translation/unit-conversion/full-corpus accuracy not claimed. Completion subject `feat(T22): select ranked evidence with answerability state`; COMPLETE effective only with successful inspected commit. Actual hash/authorized origin/main equality returned post-execution. T23 dependencies T22/T20 ready after closure, remains TODO. **STOP T22**, no drain/merge/deploy/Scarlet/source/cache deletion.

- **Current 2026-10-06 / T22-A01 PARTIAL, NOT COMPLETE:** direct Codex agent, exact model/effort unavailable, no subagents. Baseline main/T21 `2c84157ba5bcac83560191573d8a26fa944bb1cf` verified equal origin/main; T07 scratch retained. Scoped PG source-map hydration, real rerank, whole-passage budgets and generation-context guards implemented; current conflict detection is absent, pending user decision (same-label/unit numeric baseline or semantic contradiction coverage before LLM). DoD-1 cannot close without this decision/test; no threshold calibration claim (T31 pending). Evidence [H-T22-A01](#h-t22-a01), interfaces [S-T22-A01](implementation-summary.md#s-t22-a01). Checkpoint review/commit/push hash reported after actual execution; this is not a completion commit. Preserve partial work and logs, resume only T22. T23 is not dependency-ready. **STOP T22**, no task drain/merge/deploy; Scarlet/source/cache unchanged.

- **Current 2026-10-03 / T21-A01 acceptance ready, COMPLETE effective with successful inspected completion commit:** direct Codex agent, exact model/effort unavailable, no subagents. Baseline main/T20 `938bee71ac537e386e8472efc6f9eed7951026d1` equals origin/main, inherited T07 scratch retained. Bounded dense/hybrid pipeline/trusted profiles/optional same-scope neighbors/redacted trace implemented. Real CPU BGE-M3/PG/Qdrant DoD-1 **16PASS42.73s**, separate DoD-2 **29PASS5.25s**; **459regressionPASS135.41s**, **35dependencyPASS13.79s**, Ruff/mypy73/locked169/OpenAPI PASS. Evidence [H-T21-A01](#h-t21-a01), interfaces [S-T21-A01](implementation-summary.md#s-t21-a01). Final docs/scope/secrets/staging/commit/push review is closure boundary. Subject `feat(T21): add scoped hybrid multilingual retrieval`; actual hash/authorized origin/main equality returned post-execution. Candidate metadata is private, trace redacted, text hydration/rerank/evidence remain T22; real providers/public query/full corpus/load remain future gates. Own test services stopped at closure without source/cache/volume deletion; Scarlet untouched. T22 dependencies T21/T17 ready after closure; stays TODO. **STOP AFTER T21**, no merge/deploy/drain.

- **Current 2026-10-03 / T20-A01 acceptance ready, COMPLETE effective with successful inspected completion commit:** direct Codex agent, exact model/effort unavailable, no subagents. Baseline main/T19 `0b3d6f40dfc85034788c3dd9a3c285749cd19449` equals origin/main; inherited T07 scratch preserved. Registry/scoped preparation/history budgeting/rewrite port implemented; final DoD-1 **56PASS30.56s** with actual PG/Qdrant/tokenizer, DoD-2 **12PASS7.53s** provider-test schema/language matrix, **431regressionPASS146.59s**. [H-T20-A01](#h-t20-a01), [S-T20-A01](implementation-summary.md#s-t20-a01). Ruff/mypy71/locked169/OpenAPI PASS; final docs/scope/secrets/commit review is closure boundary. Own PG/Qdrant test services stopped without volume deletion; Scarlet untouched. Subject `feat(T20): compose extensible session-scoped domains`; actual hash/authorized origin/main push equality returned post-execution. Real rewrite adapters T23, public HTTP T26, no live provider claim. T21 dependencies T20/T18/T17 ready after closure; stays TODO. **STOP AFTER T20**, no merge/deploy/drain.

- **Current 2026-10-03 / T19-A01 acceptance ready, COMPLETE effective with successful inspected completion commit:** direct Codex agent, exact model/effort unavailable, no subagents. Baseline main/T18 `969b402e9f21e4ca38bea4f37f7c23839078eeec` equals origin/main; inherited T07 scratch preserved. Durable ingestion/Celery lease fences/recovery/chunks/atomic publication/default Compose implemented and VERIFIED. Final real DoD-1 12PASS106.74s and separate DoD-2 4PASS39.02s,363regression +12newstorage-security +36realPG/migration/Qdrant PASS; Ruff/mypy68/lock/OpenAPI/config/images PASS. Evidence [H-T19-A01](#h-t19-a01), interfaces [S-T19-A01](implementation-summary.md#s-t19-a01). Exact task paths reviewed, completion subject `feat(T19): complete durable document ingestion`; actual hash/authorized origin/main push equality reported after execution. No unresolved blocker; business HTTP/query and trusted language annotation/computation reuse limits documented. Own test services stopped, model cache/source/app volumes retained; Scarlet untouched. T20 dependencies ready after closure, stays TODO; **STOP AFTER T19**, no merge/deploy/drain.

- **Current 2026-10-03 / T18-A01 acceptance ready, COMPLETE effective with successful inspected completion commit:** direct Codex agent/no subagents; baseline main/T17 `919d4e43ab58158f1421982ae9dee6b95809396c` equals origin/main, inherited T07 scratch preserved. Versioned dense/sparse Qdrant repository, exact-pair filters in every branch/fetch/neighbor, before/after PG snapshot revalidation, stable point IDs and PG-locked scoped generation write/count/cleanup implemented. Final17real PG/Qdrant tests and separate4DoD-2 PASS;363unit/contract/security +19real PG dependency tests, Ruff/mypy60/lock/OpenAPI PASS. Evidence [H-T18-A01](#h-t18-a01), interfaces [S-T18-A01](implementation-summary.md#s-t18-a01). Exact12task paths, completion subject `feat(T18): enforce scoped Qdrant access`; actual commit and authorized origin/main equality reported post-execution, no self-hash/amend. No unresolved blocker; synthetic vectors are authorization fixtures, not quality benchmark. Worker/chunk persistence/atomic publication remain T19. Own test PG/Qdrant stopped, no source/volume cleanup. T19 dependencies T18/T12/T15/T16 ready after closure; **STOP AFTER T18**, no merge/deploy/drain.

- **Current 2026-10-03 / T17-A01 acceptance ready, COMPLETE effective with successful inspected completion commit:** direct agent/no subagents; resumed existing code/logs on main/T16 `9633cfcb872a89ccb1f472e6361c201e94d83588`, preserving inherited T07 scratch. Final real CPU8/GPU8, HTTP CPU/GPU smokes and both Compose profiles PASS; one inference owner/two fixed models, four clients samePID. Final21unit, full361regression,29real parser/source, Ruff/mypy55/lock169/OpenAPI/docs/scope/secrets PASS; source55 plus config/setup/test/smoke hashes equal in four images. Evidence [H-T17-A01](#h-t17-a01). Final exact27file stage/inspection, commit `feat(T17): add bounded multilingual model inference`, authorized origin/main push and remote equality are closure steps; actual hash returned after execution, no self-hash/amend. No T17 blocker; local synthetic resources are not full-stack SLA. Inference stopped after verification, cache retained. T18 dependencies T17/T10 ready after inspected completion; **STOP AFTER T17**, no merge/deploy.

- **Current 2026-10-01 / T16-A01 acceptance ready, COMPLETE effective with successful inspected completion commit:** direct Codex agent, no subagents; baseline main/T15 `e1e348d45b7a83872c420f5b6f647551db21e751` equals origin/main. Pinned BGE-M3 tokenizer, structural512/64 chunks, source segments/table header-row groups/stable IDs/trusted profiles implemented. DoD-1 final17 actual-tokenizer PASS; DoD-2 final10 parser/source PASS; additional actual worker T15 OCR output mappings PASS. [T16 evidence](#h-t16-a01). Ruff/mypy45/native42/locked117/OpenAPI/docs/scope/secrets pass; full regression341PASS with shorter basetemp, initial10Windows long-path failures retained. Final review27tests PASS including header format metadata. README/RUNBOOK updated. Completion subject `feat(T16): chunk documents with stable source mappings`; actual hash/remote equality reported after commit/push, resolve by subject. Inherited T07 scratch preserved. No unresolved T16 blocker; T17 dependencies T16/T02 ready after closure. **STOP AFTER T16**.

- **Current 2026-10-01 / T15-A01 acceptance ready, COMPLETE effective with successful inspected completion commit:** direct Codex agent, no subagents; baseline main/`cc6345dfb4b957a8f57d0ff6b3e9d31a016e606c` equals origin/main, inherited T07 scratch retained. CPU Docling/Tesseract vie+eng OCR/image runtime, provenance/quality/process bounds implemented; final DoD-1 actual20PASS and separate DoD-2 status13PASS in non-root Linux worker image, source SHA42/testSHA2 equal. Native42/regression325/Ruff/mypy42/locked112/OpenAPI/docs/scope/secrets pass. Full acceptance peak810.703MiB, status peak867.703MiB including21.6MP stress below25MP cap; fixture measurements, not full-stack budget. [T15 evidence](#h-t15-a01). Completion subject `feat(T15): support Vietnamese and English OCR`; actual hash/remote equality returned post-commit/push, resolve by subject. No T15 blocker; T16 dependencies ready after closure. **STOP AFTER T15**.

- **Current 2026-10-01 / T14-A01 acceptance ready, COMPLETE effective with successful inspected completion commit:** direct Codex agent, exact model/effort not exposed, no subagents. Baseline `main`/T13 `d3e57b29de892ff360e2e255e9d1680bf179faaf` equals origin/main. XLSX/CSV/PPTX tables, formula/cache/source context and common bounded OOXML preflight implemented; final DoD-1 23PASS, separate DoD-2 9PASS, regression344PASS, Ruff/mypy41/locked105/OpenAPI/docs/scope/secrets review PASS. [T14 evidence](#h-t14-a01). Completion subject `feat(T14): preserve spreadsheet and table evidence`; actual hash/remote equality reported post-commit/push (resolve by subject). Inherited T07 scratch untouched. No T14 blocker; T15 dependencies ready after closure. **STOP AFTER T14**.

- **Current 2026-10-01 / T13-A01 acceptance ready, COMPLETE effective with successful inspected completion commit:** direct Codex agent, no subagents; baseline main/T12 `094f74452307a8645eeb1d00a0a0af738b4403e9` equals origin/main. Native PDF/DOCX/TXT/MD/HTML EN/VI provenance and bounded registry implemented. Final DoD1 19 PASS, separate DoD2 8 PASS, regression325 PASS, Ruff/mypy38/locked101/OpenAPI/docs/scope/secrets review PASS. [T13 evidence](#h-t13-a01). Completion subject `feat(T13): parse text documents with source provenance`; actual hash/remote equality reported post-commit/push (resolve by subject). T14 ready after closure; no T13 blocker. Inherited T07 scratch preserved; **STOP AFTER T13**.

- **Current 2026-09-30 / T12-A01 completion candidate:** direct Codex agent, model/effort unavailable, no subagents. Baseline `main`/T11 `06185be330c090d59a5924e449f2502f7b3dc4cb`; two inherited T07 scratch directories unchanged. Registration, migration, job polling/retry, outbox dispatcher/CLI and Compose profile implemented. Separate DoD real PG/Redis/MinIO tests 2+1 PASS, T10 regression19 PASS, unit/contract/security325 PASS with short Windows basetemp; dispatcher image built and CLI checked. [T12 evidence](#h-t12-a01). Final docs/scope/commit/push review pending; T13 readiness only after closure. **STOP AFTER T12**.

- **Current 2026-09-30 / T11-A01 completion candidate:** direct Codex agent, exact model/effort unavailable, no subagents. Baseline `main`/T10 `2a67f8b53b65371a71ca72719cd6d0cd5025b899`. Real MinIO versioned fixture: 5 storage integration tests, separate DoD runs 3+2, 325 unit/contract/security PASS; Ruff/mypy27/OpenAPI PASS. [T11 evidence](#h-t11-a01). Completion only after docs/scope review and inspected `feat(T11): add read-only application storage adapter` commit/push. T07 inaccessible scratch untouched. T12 ready after closure; **STOP AFTER T11**.

- **Current 2026-09-27 / T10-A01 COMPLETE after inspected completion commit:** direct Codex agent, exact model/effort unavailable, no subagents. Baseline main/T09 `9e67d5d513c751930e4548ae9c292501444963a4` matched origin/main. Metadata schema/repository/scope implemented; real PG18scope +1migration and325unit/contract/security PASS. [T10 evidence](#h-t10-a01). Completion subject `feat(T10): add session-scoped metadata persistence`; COMPLETE effective only after successful inspected commit. Authorized origin/main push/hash equality reported post-execution. T11 dependencies T10/T02 ready after closure; **STOP AFTER T10**. Inherited T07 scratch retained. Initial pytest long traceback exposed existing local PG credential; value excluded from this handoff/Git, T10 now uses separate ignored credential, original credential not rotated (outside scoped change; operator follow-up).


- **Current 2026-09-27 / T09-A01 COMPLETE after inspected completion commit:** direct agent, exact model/effort unavailable, no subagents. Service identity/RS256/JWKS/local issuer implemented;51security +1real HTTP +269unit/contract PASS, Ruff/mypy16/locked83/50/OpenAPI PASS. Scoped19files; inherited T07 scratch retained. [T09 evidence](#h-t09-a01). Completion subject `feat(T09): implement authenticated application principals`; COMPLETE requires successful inspected commit; authorized push and remote hash equality reported post-execution. T10/T02 dependencies ready after T09 commit; **STOP AFTER T09**, do not implement T10.

- **Previous 2026-09-26 / T08-A01 COMPLETE after inspected completion commit:** `test(T08): verify complete corpus reproduction`; actual hash returned post-commit, resolve with `git log -1 --format=%H --grep="^test(T08):"`. Canonical all-domain setup/validator, final cold a2 setup/validator,1574published/92cache equality/stable rerun and missing-file exit1 all PASS.268full unit+contract then21focused tests, Ruff/mypy19/docs PASS. Direct agent, model/effort not exposed, no subagents; inherited T07 scratch preserved. User authorized origin/main push; actual remote equality reported post-push. [T08 evidence](#h-t08-a01). T09 dependencies T08/T03 ready after completion; **STOP AFTER T08**, no T09 implementation.


- **Previous checkpoint 2026-09-26 / T07-A06 COMPLETE after inspected completion commit:** `feat(T07): prepare XQuAD bilingual evaluation slices`, resolve actual hash with `git log -1 --format=%H --grep="^feat(T07):"`. User authorized commit/push GitHub and stop; confirmed direct one-task/session workflow. Runtime `gpt-6-sol`/`xhigh`; no subagents. Base `main`/`7696f83`; inherited candidate completed, old scratch retained local. Real setup/validator,21bilingual+138regression tests, Ruff/mypy17 and deterministic491published+3cache rerun PASS; [evidence](#h-t07-a06). Push result/actual hash reported post-commit. **STOP AFTER T07**; T08 TODO/dependencies ready, only start on a new user request. AGENTS/P14 replace historical Hermes workflow below. No scratch deletion or skipped path-length diagnostic executed.

### Lịch sử checkpoint Hermes (không còn workflow hiện hành)

- **Hermes handover 2026-09-26:** Người dùng chấm dứt `USER-PAUSED AFTER T06`, phê duyệt dùng model/reasoning hiện tại của profile. Baseline `main` CLEAN, HEAD `7d40fc4affbb009dbdda51d6d659cdf2371915d6` (T06-A03 đã được Codex accept), Python 3.12.4, uv 0.11.16. Board mới `2026-09-26-0058-rag-core-corpus-drain` xác minh 0 card khi tạo; Hermes Reviewer Phase 0 PASS tại card `t_9dfeffd9`; bootstrap/review commit `7696f83fa2d718bcad3ca6d69f627ff886f2d10d`. **Current: T07-A05 BLOCKED** vì terminal vẫn từ chối đúng phép hash/mtime inspection dù user phê duyệt hẹp; cần operator giải quyết runtime gate, không retry/bypass. T07 chưa nghiệm thu/commit; T08–T36 TODO, Phase 1 review/final review chưa chạy. Pause T06 bên dưới là lịch sử.
- **Quyền và mô hình Hermes:** Theo quyết định người dùng supersede AGENTS/P14 phần điều phối: chỉ Orchestrator ghi `docs/` và tạo completion commit sau khi kiểm handoff/diff/DoD; Worker chỉ viết source/tests/config và README/RUNBOOK ngoài `docs/`, Reviewer chỉ đọc. Artifact docs do Worker sinh staging ngoài docs; Orchestrator kiểm rồi đưa nguyên bản vào docs. Không resume Worker/Reviewer; card/session mới mỗi attempt/review, không song song. `tasks.md` giữ ID T00–T36 và TODO/IN_PROGRESS/BLOCKED/COMPLETE. Profile thực tế: orchestrator `gpt-6-sol`/openai-codex, worker `gpt-6-luna`/openai-codex, reviewer `gpt-5.6-sol`/openai-codex; user cho phép giữ nguyên model/effort. Không claim đã kiểm effort runtime khi chưa có log.
- **Bootstrap:** Protocol gốc tại `C:/Users/Admin/Downloads/HERMES-AGENT-EXECUTION-PROTOCOL.md` được copy nguyên vào `docs/HERMES-AGENT-EXECUTION-PROTOCOL.md`; `docs/agent-state.md` và `docs/review-report.md` được khởi tạo. Không sửa prompt corpus. Chỉ các file docs quản trị Hermes là dirty lúc chuẩn bị Phase 0 review; không commit chúng như completion của T07 hoặc coi review là PASS trước handoff.

### Hermes Reviewer handoff — Phase 0 / card t_9dfeffd9

- From: Reviewer mới, profile/model/provider `reviewer`/`gpt-5.6-sol`/`openai-codex`, effort không lộ; run 1, session `20260926_010005_c64172`. To: Orchestrator. Result: **PASS** Phase 0 T00–T03, card `done`; không thực thi lại implementation hoặc sửa file. Chi tiết acceptance/security/Git và caveat ghi tại [Review Report — Phase 0](review-report.md).
- Reviewed commits: T00 `7025eeac`, T01 `ff8069ab`, T02 `851ff1d`, T03 `e4db5e3`; linear, `git show --check` sạch. Historical DoD refs nằm trong các entry T00–T03 bên dưới. No blockers/backlog candidates; future runtime scope/auth còn thuộc T09–T26.
- Actual reviewer commands (cwd `C:/Users/Admin/Documents/GitHub/rag-core`): `PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -B scripts/check_docs.py` exit 0, output 13 Markdown /220 links/37 tasks; `PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -B scripts/export_openapi.py --check` exit 0, 13 operations/2 served health/48 schemas/37 examples. `PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -B -m pytest -p no:cacheprovider tests/unit/test_settings.py tests/unit/test_health.py tests/contract/test_api_schema.py -q` exit **1**: 86 passed, **4 setup errors** do Windows temp `C:/Users/Admin/AppData/Local/Temp/pytest-of-Admin` không truy cập được; không gọi invocation này PASS. Historical T01–T03 tests/service evidence không được nói là rerun.
- Risks: README/RUNBOOK trên HEAD còn câu paused; Worker T07 cập nhật trong task theo quyền ngoài docs. T02 Docker real-service evidence là lịch sử; không claim current daemon state. Bootstrap docs là uncommitted transition transaction, không lẫn T00–T03 evidence.
- Next: Orchestrator ghi review-report/state; Git author preflight sau docs check cho biết identity thiếu, nên commit docs bootstrap+review và dispatch T07 phải chờ T-H1. Phase 1 chỉ review sau T08.

### Hermes bootstrap Git author blocker — T-H1

- CWD `C:/Users/Admin/Documents/GitHub/rag-core`, `main` HEAD `7d40fc4affbb009dbdda51d6d659cdf2371915d6`. Exact compound command: `PYTHONDONTWRITEBYTECODE=1 .venv/Scripts/python.exe -B scripts/check_docs.py && git diff --check && git status --short && git diff --stat && git diff --name-only && git ls-files --others --exclude-standard && git var GIT_AUTHOR_IDENT >/dev/null && printf 'Git author configured\n'`; overall **exit 128** chỉ ở `git var GIT_AUTHOR_IDENT`.
- Actual output excerpt trước lỗi: `PASS UTF-8/nonempty Markdown: 13 files`; `PASS internal links/anchors: 221`; `PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic`; `DOCUMENTATION CHECK: PASS`; `git diff --check` không có stdout; modified `docs/handoffs.md`; untracked `docs/HERMES-AGENT-EXECUTION-PROTOCOL.md`, `docs/agent-state.md`, `docs/review-report.md` tại thời điểm đó (sau đó thêm `docs/tasks.md` cho T-H1).
- Actual Git output: `Author identity unknown` / `fatal: unable to auto-detect email address (got 'Admin@Vincent.(none)')`. Khi đó không in secret, không cấu hình danh tính giả/global/local, không stage/commit, không dispatch T07. Người dùng sau đó xác nhận đã cấu hình Git author: exact check `git var GIT_AUTHOR_IDENT >/dev/null && printf 'Git author configured\n'` exit **0**, actual output `Git author configured`; không in identity. Đồng thời `git status --short` chỉ hiển thị bootstrap docs, HEAD `7d40fc4`, `scripts/check_docs.py` exit 0 (13 Markdown/221 links/37 tasks/81 edges), board có 1 Reviewer `done`/0 active. T-H1 COMPLETE; Orchestrator stage đúng docs/ và commit bootstrap/review riêng trước T07.

### Hermes T07-A01 blocker

<a id="hermes-t07-a01-blocker"></a>

- From: Worker profile `worker` configured `gpt-6-luna`/`openai-codex`; card `t_2a19f514`, run 2. To: Orchestrator. Phase 1 / T07-A01. Board status `blocked`, elapsed ~23m; terminal session ended, **do not resume**. Result: BLOCKED, no structured DoD handoff, no verified setup/validation/test result, no commit or task acceptance.
- Exact rejected command reported by Worker/board: `rm -rf .t .tmp-test .verify-temp`; terminal explicitly denied it and instructed stop. Board summary: `Verification is paused because the terminal explicitly denied the cleanup command ... and instructed me to stop; generated pytest scratch artifacts remain untracked.` This is a safety-gate denial, not permission to retry with another syntax/tool or skip a required inspection silently. Worker requested a human choice to retain or authorize cleanup of precisely these three repo-local scratch directories.
- Preexisting Orchestrator docs edits `docs/tasks.md`, `docs/agent-state.md`, `docs/handoffs.md` after clean baseline commit `7696f83`. Latest-good accepted code T06; no T07 candidate accepted. User selected: **authorize cleanup of exactly the three repo-local scratch directories after verifying path is in repo**. Orchestrator read-only check `pwd && git status --short && git rev-parse HEAD && for p in .t .tmp-test .verify-temp; do if test -e "$p"; then printf 'path=%s resolved=%s\n' "$p" "$(realpath "$p")"; stat -c 'type=%F size=%s' "$p"; else printf 'path=%s missing\n' "$p"; fi; done && git diff --name-only && git ls-files --others --exclude-standard`, exit 0, confirmed all three top-level directories resolve to `C:/Users/Admin/Documents/GitHub/rag-core/<name>` with `type=directory`; status excerpt lists modified README/RUNBOOK/corpus scripts/manifests/common tests and docs; untracked three scratch dirs + bilingual QA/prepare script/test. Output of complete untracked list was large and is not reproduced as QA data; do not accidentally stage scratch. No cleanup performed by Orchestrator. Nested reparse points still need Worker check before operation. If tool still refuses, stop; no alternate syntax/outcome bypass. New A02 fresh card/session after preserving code/diffs. T08 and Phase 1 review remain gated.

### Hermes T07-A02 handoff

<a id="hermes-t07-a02-handoff"></a>

- From: fresh Worker `worker`, configured `gpt-6-luna`/`openai-codex` (effort not verified), card `t_b2a34702` run 3. To: Orchestrator. T07-A02 result **BLOCKED**; `main` HEAD/base `7696f83fa2d718bcad3ca6d69f627ff886f2d10d`, no stage/commit, no `docs/` edits by Worker. Full structured comment in Kanban card, no claim T07 complete.
- Approved cleanup: Worker ran PowerShell native absolute path/reparse inspection; counted `.t` 23 files/10 dirs, `.tmp-test` 21 files/27 dirs, `.verify-temp` 1,959 files/343 dirs; no reparse points. Removed only the three approved targets with `Remove-Item -LiteralPath ... -Recurse -Force`, verified absence, exit 0. New `.tmp-t07-a02/`, `.pytmp-t07-a02/` scratch retained and **not** authorized for deletion automatically.
- Actual DoD commands, cwd repo root, config `UV_CACHE_DIR=.uv-cache UV_PYTHON_INSTALL_DIR=.uv-python`: `uv run python corpus-documents/scripts/setup_corpus.py --domain bilingual` exit 0 → `CORPUS SETUP: PASS - bilingual/XQuAD; documents={'en': 240, 'vi': 240} QA_slices={'en_en': 1190, 'vi_vi': 1190, 'vi_en': 1190, 'en_vi': 1190} parallel_groups=240`; separate `uv run python corpus-documents/scripts/validate_corpus.py --domain bilingual` exit 0 → `CORPUS VALIDATION: PASS - bilingual; paragraphs={'en': 240, 'vi': 240} QA_slices={'en_en': 1190, 'vi_vi': 1190, 'vi_en': 1190, 'en_vi': 1190} parallel_groups=240`. `uv run pytest tests/unit/test_corpus_bilingual.py` exit **1**, 4 passed and 1 Windows temp setup error; two repo-local temp retries exit **1**, 4 passed/1 failed `FileNotFoundError` from `tempfile.mkstemp` under deeply nested stage/documents/en path. Worker added unproven parent-mkdir patch in `prepare_bilingual.py`; repeat still failed. DoD-1 has A02 PASS commands, DoD-2 FAIL, D1–D5 incomplete, D6 not attempted. Measured source SHA receipts/rerun hash+mtime not supplied; no claim PASS.
- Subsequent read-only diagnostic requested exact command from board log:

```text
python -c "from pathlib import Path; p=Path.cwd()/'.p'/'test_prepare_validate_and_reru0'/'.downloads'/('bilingual-stage-'+'a'*32)/'bilingual'/'documents'/'en'/('.xquad_en_'+'a'*64+'.md.'+'a'*8+'.part'); print(len(str(p))); print(p)"
```

  Terminal output: `Timeout — denying command`, elapsed 60.5s; Worker stopped immediately. Do not retry/rephrase/use another tool to obtain the same denied diagnostic. This denial is separate from the already approved cleanup. User selected: **skip only this optional diagnostic**; mandatory bilingual test and all original T07 DoD remain unchanged and must PASS via a fresh Worker. Do not use alternate syntax/tool to re-attempt the denied measurement.
- Next: A03 fresh Worker after decision, inspect partial diff/scratch without deleting unapproved dirs; isolate Windows `FileNotFoundError` using permitted evidence and run all checks separately. T08 not dispatchable.

### Hermes T07-A03 stale recovery

<a id="hermes-t07-a03-stale"></a>

- From: card `t_9bc95bc3` run 4 / Worker profile configured `gpt-6-luna`/`openai-codex`; no terminal handoff. To: Orchestrator. A03 was still marked `running` after 12.5h, claim expired; read-only `MSYS_NO_PATHCONV=1 tasklist.exe /FI 'PID eq 34724'`, exit 0, actual `INFO: No tasks are running which match the specified criteria.` Initial Git-bash `tasklist /FI` attempt exit 1 due MSYS path conversion; corrected with environment flag, not a denied safety gate. `hermes kanban ... runs t_9bc95bc3` showed 12.5h `running`; board diagnostics none.
- Board-native `hermes kanban --board 2026-09-26-0058-rag-core-corpus-drain log --tail 5000 t_9bc95bc3` showed source/docs reads, two pytest attempts exit1 using repo/Windows temp arguments, third invocation preview 3.2s without displayed exit, then patch removing a previously added `output_path.parent.mkdir` line in `prepare_bilingual.py`. No structured result; cannot claim DoD, pytest or rerun PASS. Base HEAD remained `7696f83fa2d718bcad3ca6d69f627ff886f2d10d`. `git diff --check` exit0; source/test/manifests/README/RUNBOOK and orchestration docs modified, untracked bilingual QA/script/test and four scratch trees. Preserve all, do not stage scratch or delete unapproved paths.
- Recovery exact actions: `hermes kanban --board 2026-09-26-0058-rag-core-corpus-drain reclaim t_9bc95bc3 --reason 'A03 stale: claim expired, worker PID 34724 absent, log stops after partial patch; preserve changes and require fresh T07-A04 card'` → `Reclaimed t_9bc95bc3`, exit0; then `hermes kanban --board 2026-09-26-0058-rag-core-corpus-drain block t_9bc95bc3 'A03 terminal after stale reclaim; no handoff or DoD; do not resume; T07-A04 new card must inspect partial patch and tests'` → blocked, exit0. Board now done1/blocked3/running0/ready0.
- Result: A03 terminal/incomplete, no T07 acceptance or commit; A04 fresh card and session with exact inherited state. No repetition of optional denied diagnostic; mandatory test/DoD unchanged. After repeated attempts on related Windows test issue, escalate if A04 makes no progress or needs product decision.

### Hermes T07-A04 — test fixed; rerun evidence denied

<a id="hermes-t07-a04"></a>

- From: fresh Worker `worker`, configured `gpt-6-luna`/`openai-codex`, effort not independently available; card `t_88f601c9` run 6, Phase 1 T07-A04 [Fix], result **BLOCKED**. To: Orchestrator. Base `main`/`7696f83fa2d718bcad3ca6d69f627ff886f2d10d`, no stage/commit, no A04 source/docs changes or cleanup. Board structured comment has full handoff and Git inventory. Baseline dirty inherited A01–A03 plus Orchestrator docs; untracked four temp trees, bilingual QA/script/test retained. No new T08 work.
- Actual cwd for commands: `C:/Users/Admin/Documents/GitHub/rag-core`; env for corpus/test `UV_CACHE_DIR=.uv-cache UV_PYTHON_INSTALL_DIR=.uv-python`. `UV_CACHE_DIR=.uv-cache UV_PYTHON_INSTALL_DIR=.uv-python uv run pytest tests/unit/test_corpus_bilingual.py` exit1: 4 passed/1 setup error `PermissionError: [WinError 5] Access is denied` at user Temp `pytest-of-Admin`. `if test -e /c/t07-a04-btemp; then printf 'Refusing existing basetemp\n'; exit 2; fi; UV_CACHE_DIR=.uv-cache UV_PYTHON_INSTALL_DIR=.uv-python uv run pytest -p no:cacheprovider --basetemp='C:/t07-a04-btemp' tests/unit/test_corpus_bilingual.py` exit0: `5 passed in 2.33s`; fresh short Windows-native temp path, no cleanup. Đây là test PASS có cấu hình temp rõ, không claim lệnh mặc định PASS.
- `UV_CACHE_DIR=.uv-cache UV_PYTHON_INSTALL_DIR=.uv-python uv run python corpus-documents/scripts/setup_corpus.py --domain bilingual` exit0, output thực `CORPUS SETUP: PASS - bilingual/XQuAD; documents={'en': 240, 'vi': 240} QA_slices={'en_en': 1190, 'vi_vi': 1190, 'vi_en': 1190, 'en_vi': 1190} parallel_groups=240`. Lệnh riêng `UV_CACHE_DIR=.uv-cache UV_PYTHON_INSTALL_DIR=.uv-python uv run python corpus-documents/scripts/validate_corpus.py --domain bilingual` exit0, output `CORPUS VALIDATION: PASS - bilingual; paragraphs={'en': 240, 'vi': 240} QA_slices={'en_en': 1190, 'vi_vi': 1190, 'vi_en': 1190, 'en_vi': 1190} parallel_groups=240`.
- Safety gate: read-only Python `python -c` snapshot toàn `corpus-documents/bilingual` để tính file tree SHA256, mtime-map SHA256, 4 QA slice SHA256 và đọc `qa/preparation.json` source hashes/counts bị terminal `Timeout — denying command` sau 60.4s, output `BLOCKED: User denied this command. The user has NOT consented to this action. Do NOT retry this command, do NOT rephrase it, and do NOT attempt the same outcome via a different command. Stop the current workflow...`; **không chạy (exit -1)**. Exact attempted command lưu trong board-native log `hermes kanban --board 2026-09-26-0058-rag-core-corpus-drain log --tail 7000 t_88f601c9`, chưa được phép retry dưới bất kỳ dạng nào. Phép đo path-length tùy chọn bị từ chối A02 không được lặp lại. Không có before/after rerun checksum/mtime hoặc source receipts independent; Worker dừng ngay.
- DoD-1: real setup+validator separate PASS, rerun/source receipts BLOCKED; DoD-2: 5/5 unit PASS với basetemp cụ thể, hash/mtime rerun chưa đo. D1 scope final chưa đóng; D2 Ruff/mypy/regression chưa chạy; D3 incomplete; D4 README/RUNBOOK candidate A01–A03 chưa review A04, docs/ do Orchestrator; D5 diff/secrets/license/ignored data chưa final; D6 commit chưa có. Không giả T07 COMPLETE. Human Task T-H2 đã được user quyết định sau handoff: “Tôi phê duyệt riêng phép kiểm hash/mtime bị từ chối ở card t_88f601c9.” Scope chỉ đúng phép read-only inspection của A04, không cho phép bỏ DoD, blanket bypass, phép đo path-length tùy chọn hay xóa scratch. A05 mới được giao kiểm đúng scope, nhưng runtime vẫn từ chối; xem entry A05 dưới đây. A04 không resume; T08 không dispatch.

### Hermes T07-A05 — runtime denied despite narrow human approval

<a id="hermes-t07-a05"></a>

- From: fresh Worker `worker`, configured `gpt-6-luna`/`openai-codex`, effort not independently verified; card `t_90838461`, run 7, Phase 1 T07-A05 [Fix]. Result **BLOCKED**; no code/docs/source edits, stage, commit, scratch cleanup, setup rerun, validator or test in A05. Branch `main`/base HEAD `7696f83fa2d718bcad3ca6d69f627ff886f2d10d`; inherited dirty T07 candidate + docs + four untracked scratch dirs and bilingual QA/script/test preserved. Worker read T-H2 authorization and exact original invocation in A04 board log; did not retry A02 optional diagnostic.
- Approved operation: exactly the read-only bilingual tree hash/mtime/source-receipt snapshot denied at A04. Exact original command remains in board-native `hermes kanban --board 2026-09-26-0058-rag-core-corpus-drain log --tail 7000 t_88f601c9`; A05 attempted same, no alternate. Terminal again denied with exit **-1**, actual response: `BLOCKED: User denied this command. The user has NOT consented to this action. Do NOT retry this command, do NOT rephrase it, and do NOT attempt the same outcome via a different command. Stop the current workflow and wait for the user to respond before taking any further destructive or irreversible action.` No snapshot output; Worker stopped immediately. Chat approval had been recorded but did not change runtime terminal decision.
- DoD-1 BLOCKED: A04 historical real setup/validator pass only, no A05 rerun/hash. DoD-2 NOT RUN in A05 (A04 historical 5/5 targeted tests with short temp), no deterministic before/after evidence. D1–D5 closure NOT RUN; D6 no commit. No T07 acceptance or T08 dispatch. Board 1 Reviewer done/5 Worker blocked/0 running at terminal state. Escalate runtime safety gate to operator for precise approval path; no auto-spawn A06, no rephrase/alternate tool/skip DoD. Full structured Worker comment on `t_90838461`.

### Historical checkpoint retained below (before Hermes handover)

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

<a id="h-t07-a06"></a>
## H-T07-A06 — XQuAD closure in one-task Codex session

- **Authorization/runtime:** user explicitly requested finishing T07 only, committing/pushing to GitHub and stopping; confirmed agent may directly edit code/tests/docs under one-task/session workflow. Actual root runtime `gpt-6-sol`/`xhigh`; no subagents. AGENTS/P14/state updated accordingly; historical Hermes attempts retained. No T08 implementation, model/API/retrieval/Scarlet/deployment work.
- **Baseline/recovery:** `main` / `7696f83fa2d718bcad3ca6d69f627ff886f2d10d`. Inherited modified README/RUNBOOK/corpus README, bilingual/root manifests, setup/validator, inventory, docs agent-state/handoffs/tasks, common test; untracked bilingual QA, preparation script/test and Hermes scratch `.ptmp-t07-a02/`, `.tmp-t07-a02/`. Git also reports inaccessible `.pytmp-t07-a02/` and `UsersAdminAppDataLocalTempt07a03/`. Scratch preserved/excluded from commit, no permission or deletion workaround. The previously approved read-only hash/mtime operation succeeded normally in Codex; historical Hermes terminal refusals remain in A04/A05. Optional path-length diagnostic was not repeated.
- **Dependencies/read scope:** full T04/T06 notes and summaries, P01/P03/P11/P13/P14, original prompt §3/§§6–7, handoffs, README/RUNBOOK read. T06 closure `7d40fc4`, implementation `6863abf`; T04 `ad49ecc`. Original prompt SHA256 remains `7EC6E58AE4C24DB27AF4320BCB30222BBF2B67961D99C62980CEA4410AEE2C46`.
- **Implemented:** accepted and completed inherited XQuAD full-source preparation/alignment/four-slice pipeline. Strengthened source SHA pin and artifact role validation. Replaced live-data common unit test with injected failure; 21 bilingual tests cover counterpart languages/gold, regrouped paragraphs, duplicate IDs/invalid spans, corruption, unknown files/locks, rollback, synthetic CLI success/failure, deterministic rerun. Compact fixture directory names avoid Windows deep paths. Documentation traversal now excludes existing ignored `.local` runtime/test state; no meaningful docs excluded. No dependency/schema/API migration.
- **Environment:** cwd for every command below `C:\\Users\\Admin\\Documents\\GitHub\\rag-core`; Windows, Python3.12.4, pytest9.1.1, local uv cache/install directories, fresh short basetemps. Unit tests use synthetic sources/injected transport only; real DoD uses existing official pinned XQuAD bytes (verified Git blobs + SHA256 + source semantics), not mocks. A06 setup reuses validated cache; fresh-download/clean-clone proof remains T08. No provider/model inference/service required in T07.
- **Measured:** revision `7d30520c717524000f0d9d2f9c10a069acd9d285`; 240 aligned groups, 240 EN+240 VI documents, 1190 original parallel QA per language, 1190 rows in each of four slices (4760 slice rows, not unique QA). Manifest has 489 artifact receipts; original source/gold text and language policy retained, no translation/subsetting. XQuAD lacks unanswerable examples. CC-BY-SA4.0 attribution/change/ShareAlike notices updated; raw/documents and FinanceBench QA stay ignored.
- **DoD-1 PASS:** separate real setup and validator below. **DoD-2 PASS:** 21 tests and actual rerun of 491 published +3 cache files preserving byte hashes, mtimes, all IDs and downloaded_at. **D1:** dependencies/scope/original-prompt review and final diff check. **D2:** Ruff PASS, strict mypy17 PASS, 138 corpus regressions PASS; unrelated broader export-script mypy failure retained below, not claimed fixed. **D3:** actual commands/output below. **D4:** README/RUNBOOK/corpus/license docs, tasks/handoffs/summary/state/workflow; final documentation check below. **D5:** explicit path review; no raw/restricted payload, credentials, scratch or caches staged. **D6:** completion subject `feat(T07): prepare XQuAD bilingual evaluation slices`; COMPLETE effective only after successful commit and inspected tree/hash; actual hash returned post-commit (resolve with `git log -1 --format=%H --grep="^feat(T07):"`). User authorized push to origin/main; verify remote hash after push, no force/merge.
- **Attempt troubleshooting:** initial PowerShell→Python documentation edit lost UTF-8 on stdin and stopped at assertion (exit1); only two previously clean files touched by that edit were restored from HEAD, then scoped Unicode patches applied. Inherited candidate remained intact. First bilingual run:20pass/1fail because synthetic CLI fixture omitted schemas; added fixture schemas, rerun21pass. Initial docs check saw an intentionally empty synthetic Markdown under ignored .local; fixed traversal to exclude that existing runtime directory. Historical scratch permission warnings retained, no cleanup. Start date2026-09-26; exact starting wall-clock not captured; review timestamp measured `2026-09-26T17:05:20.5114250+07:00`.
- **Next:** stop after T07. T08 dependencies T07/T05/T06 are complete once this commit is accepted; user may start T08 in a fresh session. T08 owns all-domain CLI, output-root safety, clean downloads/rerun and missing-file rejection. No full-phase/final-product acceptance claim.

### Actual commands and output

#### DoD-2 initial fixture failure

Command (PowerShell), exit **1**; full local log `.local/t07-a06/tests1.log`:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'; $env:PYTEST_ADDOPTS = '--basetemp=.local/p7a6'; uv run pytest tests/unit/test_corpus_bilingual.py
```

```text
============================= test session starts =============================
platform win32 -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Admin\Documents\GitHub\rag-core
configfile: pyproject.toml
plugins: anyio-4.15.1, asyncio-1.4.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 21 items

tests\unit\test_corpus_bilingual.py ....................F                [100%]

================================== FAILURES ===================================
____ test_domain_commands_dispatch_to_synthetic_corpus_and_report_failure _____

corpus_root = WindowsPath('C:/Users/Admin/Documents/GitHub/rag-core/.local/p7a6/b11')
monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x000001D6DA90D3A0>
capsys = <_pytest.capture.CaptureFixture object at 0x000001D6DA933470>

    def test_domain_commands_dispatch_to_synthetic_corpus_and_report_failure(
        corpus_root: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        prepare = bilingual.prepare_bilingual
        monkeypatch.setattr(bilingual, "prepare_bilingual", lambda: prepare(corpus_root))
        monkeypatch.setattr(validate_corpus, "CORPUS_ROOT", corpus_root)
>       assert setup_corpus.main(["--domain", "bilingual"]) == 0
E       AssertionError: assert 1 == 0
E        +  where 1 = <function main at 0x000001D6DA7428E0>(['--domain', 'bilingual'])
E        +    where <function main at 0x000001D6DA7428E0> = setup_corpus.main

tests\unit\test_corpus_bilingual.py:380: AssertionError
---------------------------- Captured stderr call -----------------------------
CORPUS SETUP: FAIL - bilingual: JSON file is missing, unreadable, or not UTF-8; no data acceptance
=========================== short test summary info ===========================
FAILED tests/unit/test_corpus_bilingual.py::test_domain_commands_dispatch_to_synthetic_corpus_and_report_failure
======================== 1 failed, 20 passed in 13.11s ========================
```

#### DoD-2 final bilingual tests

Command (PowerShell), exit **0**; full local log `.local/t07-a06/tests2.log`:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'; $env:PYTEST_ADDOPTS = '--basetemp=.local/p7a6b'; uv run pytest tests/unit/test_corpus_bilingual.py
```

```text
============================= test session starts =============================
platform win32 -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Admin\Documents\GitHub\rag-core
configfile: pyproject.toml
plugins: anyio-4.15.1, asyncio-1.4.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 21 items

tests\unit\test_corpus_bilingual.py .....................                [100%]

============================= 21 passed in 15.05s =============================
```

#### D2 corpus regression

Command (PowerShell), exit **0**; full local log `.local/t07-a06/regression.log`:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'; $env:PYTEST_ADDOPTS = '--basetemp=.local/p7reg'; uv run pytest tests/unit/test_corpus_common.py tests/unit/test_corpus_default.py tests/unit/test_corpus_document.py
```

```text
============================= test session starts =============================
platform win32 -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Admin\Documents\GitHub\rag-core
configfile: pyproject.toml
plugins: anyio-4.15.1, asyncio-1.4.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 138 items

tests\unit\test_corpus_common.py ....................................... [ 28%]
...........................................                              [ 59%]
tests\unit\test_corpus_default.py .....................................  [ 86%]
tests\unit\test_corpus_document.py ...................                   [100%]

============================ 138 passed in 46.22s =============================
```

#### D2 broad type-check diagnostic (existing unrelated missing stub)

Command (PowerShell), exit **1**; full local log `.local/t07-a06/types1.log`:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'; uv run mypy src scripts corpus-documents/scripts
```

```text
scripts\export_openapi.py:11: error: Library stubs not installed for
"jsonschema"  [import-untyped]
    from jsonschema import Draft202012Validator, FormatChecker
    ^
scripts\export_openapi.py:11: note: Hint: "python3 -m pip install types-jsonschema"
scripts\export_openapi.py:11: note: (or run "mypy --install-types" to install all missing stub packages)
scripts\export_openapi.py:11: note: See https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-imports
Found 1 error in 1 file (checked 20 source files)
```

#### D2 established source/corpus type-check

Command (PowerShell), exit **0**; full local log `.local/t07-a06/types2.log`:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'; uv run mypy src corpus-documents/scripts
```

```text
Success: no issues found in 17 source files
```

#### D2 final Ruff

Command (PowerShell), exit **0**; full local log `.local/t07-a06/quality_final.log`:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'; uv run ruff check src tests scripts corpus-documents/scripts
```

```text
All checks passed!
```

#### DoD-2 before snapshot

Command (PowerShell), exit **0**; full local log `.local/t07-a06/before.log`:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'; $env:PYTEST_ADDOPTS = '--basetemp=.local/p7reg'; uv run python corpus-documents/.downloads/t07-a06-snapshot.py before
```

```text
BEFORE: 491 published files; 3 cache files; slice IDs={'en_en': 1190, 'vi_vi': 1190, 'vi_en': 1190, 'en_vi': 1190}
source_sha256={"en": "e4c57d1c9143aaa1c5d265ba5987a65f4e69528d2a98f29d6e75019b10344f29", "vi": "f619a1eb11fb42d3ab0834259e488a65f585447ef6154437bfb7199d85161a04"}
downloaded_at=2026-09-25T18:35:30.879042+00:00
en_en_sha256=784609bd8822fa25db35fe32723387ba96e77b64756fc30dcd1104ed11e0acbf
vi_vi_sha256=384741e6c840fcf48c5cbc3f29ee8b4ea45d276ad95e8fb41d4f74019aab8ecc
vi_en_sha256=859df1cb47b251d4b5432f2815a76245f4eba087516a0fbccb1ecd320c12a8ba
en_vi_sha256=74184b2a56090fa85d677569b2e0c7c455e1521af746a9d0018a8e1d6bd40102
```

#### DoD-1 real setup / rerun

Command (PowerShell), exit **0**; full local log `.local/t07-a06/live_setup.log`:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'; uv run python corpus-documents/scripts/setup_corpus.py --domain bilingual
```

```text
CORPUS SETUP: PASS - bilingual/XQuAD; documents={'en': 240, 'vi': 240} QA_slices={'en_en': 1190, 'vi_vi': 1190, 'vi_en': 1190, 'en_vi': 1190} parallel_groups=240
```

#### DoD-1 independent real validator

Command (PowerShell), exit **0**; full local log `.local/t07-a06/live_validate.log`:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'; uv run python corpus-documents/scripts/validate_corpus.py --domain bilingual
```

```text
CORPUS VALIDATION: PASS - bilingual; paragraphs={'en': 240, 'vi': 240} QA_slices={'en_en': 1190, 'vi_vi': 1190, 'vi_en': 1190, 'en_vi': 1190} parallel_groups=240
```

#### DoD-2 after snapshot

Command (PowerShell), exit **0**; full local log `.local/t07-a06/after.log`:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'; uv run python corpus-documents/.downloads/t07-a06-snapshot.py after
```

```text
RERUN PASS: 491 published + 3 cache hashes/mtimes, all slice IDs and downloaded_at unchanged
source_sha256={"en": "e4c57d1c9143aaa1c5d265ba5987a65f4e69528d2a98f29d6e75019b10344f29", "vi": "f619a1eb11fb42d3ab0834259e488a65f585447ef6154437bfb7199d85161a04"}
downloaded_at=2026-09-25T18:35:30.879042+00:00
en_en_sha256=784609bd8822fa25db35fe32723387ba96e77b64756fc30dcd1104ed11e0acbf
vi_vi_sha256=384741e6c840fcf48c5cbc3f29ee8b4ea45d276ad95e8fb41d4f74019aab8ecc
vi_en_sha256=859df1cb47b251d4b5432f2815a76245f4eba087516a0fbccb1ecd320c12a8ba
en_vi_sha256=74184b2a56090fa85d677569b2e0c7c455e1521af746a9d0018a8e1d6bd40102
```

#### D4 initial docs failure

Command (PowerShell), exit **1**; full local log `.local/t07-a06/docs_initial.log`:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'; uv run python scripts/check_docs.py
```

```text
DOCUMENTATION CHECK: FAIL: Empty Markdown file: C:\Users\Admin\Documents\GitHub\rag-core\.local\p7reg\test_invalid_qa_reference_or_c2\documents\doc.md
```

### Final documentation and scope checks

D4 documentation, cwd repo root, exit **0**:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'; uv run python scripts/check_docs.py
```

```text
PASS UTF-8/nonempty Markdown: 14 files
PASS internal links/anchors: 240
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```

D1 whitespace/scope, cwd repo root, exit **0**:

```powershell
git diff --check
```

```text
(no output)
```



### Staging and secret/scope review

D6 explicit staging, cwd repo root, exit **0**:

```powershell
git add -- 'AGENTS.md' 'README.md' 'RUNBOOK.md' 'corpus-documents/README.md' 'corpus-documents/bilingual/manifest.json' 'corpus-documents/manifest.json' 'corpus-documents/source-license-inventory.json' 'corpus-documents/licenses/README.md' 'corpus-documents/scripts/prepare_bilingual.py' 'corpus-documents/scripts/setup_corpus.py' 'corpus-documents/scripts/validate_corpus.py' 'corpus-documents/bilingual/qa/documents_en.jsonl' 'corpus-documents/bilingual/qa/documents_vi.jsonl' 'corpus-documents/bilingual/qa/en_en.jsonl' 'corpus-documents/bilingual/qa/en_vi.jsonl' 'corpus-documents/bilingual/qa/vi_en.jsonl' 'corpus-documents/bilingual/qa/vi_vi.jsonl' 'corpus-documents/bilingual/qa/preparation.json' 'docs/agent-state.md' 'docs/handoffs.md' 'docs/plan.md' 'docs/tasks.md' 'docs/implementation-summary.md' 'docs/task-session-prompt.md' 'scripts/check_docs.py' 'tests/unit/test_corpus_common.py' 'tests/unit/test_corpus_bilingual.py'
```

```text
(no output)
```

D5 staged review, cwd repo root, exit **0**:

```powershell
$OutputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new(); @'
import hashlib, re, subprocess
from pathlib import Path
expected = ["AGENTS.md","README.md","RUNBOOK.md","corpus-documents/README.md","corpus-documents/bilingual/manifest.json","corpus-documents/manifest.json","corpus-documents/source-license-inventory.json","corpus-documents/licenses/README.md","corpus-documents/scripts/prepare_bilingual.py","corpus-documents/scripts/setup_corpus.py","corpus-documents/scripts/validate_corpus.py","corpus-documents/bilingual/qa/documents_en.jsonl","corpus-documents/bilingual/qa/documents_vi.jsonl","corpus-documents/bilingual/qa/en_en.jsonl","corpus-documents/bilingual/qa/en_vi.jsonl","corpus-documents/bilingual/qa/vi_en.jsonl","corpus-documents/bilingual/qa/vi_vi.jsonl","corpus-documents/bilingual/qa/preparation.json","docs/agent-state.md","docs/handoffs.md","docs/plan.md","docs/tasks.md","docs/implementation-summary.md","docs/task-session-prompt.md","scripts/check_docs.py","tests/unit/test_corpus_common.py","tests/unit/test_corpus_bilingual.py"]
actual = subprocess.check_output(['git','diff','--cached','--name-only'], text=True).splitlines()
assert set(actual) == set(expected), (set(actual)-set(expected),set(expected)-set(actual))
patterns=[rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',rb'(?<![A-Za-z0-9])(?:sk-[A-Za-z0-9_-]{32,}|gh[pousr]_[A-Za-z0-9]{30,}|AKIA[A-Z0-9]{16})(?![A-Za-z0-9])']
for name in actual:
    body=subprocess.check_output(['git','show',':'+name])
    body.decode('utf-8')
    assert not any(re.search(p,body) for p in patterns), 'Secret-like token in '+name
    assert not any(part in {'.env','.downloads','.local','raw','documents'} for part in Path(name).parts),name
prompt=Path('corpus-documents/Codex Prompt – Build RAG Evaluation Corpus.md')
assert hashlib.sha256(prompt.read_bytes()).hexdigest().upper()=='7EC6E58AE4C24DB27AF4320BCB30222BBF2B67961D99C62980CEA4410AEE2C46'
print(f'PASS staged scope: {len(actual)} exact approved files; UTF-8; no raw/restricted corpus/cache/scratch; no private-key/provider-token patterns')
print('PASS original prompt SHA256 unchanged')
'@ | .venv/Scripts/python.exe -
```

```text
warning: unable to access 'C:\Users\Admin/.config/git/ignore': Permission denied
PASS staged scope: 27 exact approved files; UTF-8; no raw/restricted corpus/cache/scratch; no private-key/provider-token patterns
PASS original prompt SHA256 unchanged
```

D1/D6 staged diff check, cwd repo root, exit **0**:

```powershell
git diff --cached --check
```

```text
warning: unable to access 'C:\Users\Admin/.config/git/ignore': Permission denied
```

Network preflight: sandbox `git ls-remote --heads origin` failed with GitHub443 connection denied (exit1). Approved network retry of the same read-only command exited0 with no branch refs; author already configured, no Git identity changes. Push is explicitly user-authorized. After recording this evidence, re-stage only handoffs and run `git commit -m "feat(T07): prepare XQuAD bilingual evaluation slices"`; validate actual commit tree/hash, then `git push -u origin main` and compare `git ls-remote --heads origin main`. Actual commit/push output is reported after commit, avoiding a self-referential hash or fabricated pre-commit result.

### Snapshot helper provenance

The exact ignored local helper used above (snapshot JSON at `corpus-documents/.downloads/t07-a06-before.json`; no clean-download claim):

```python
"""Local T07-A06 evidence helper; never a shipped corpus command."""
import hashlib
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
domain = root / "bilingual"
paths = [root / "manifest.json", *sorted(p for p in domain.rglob("*") if p.is_file())]
cache = [root / ".downloads" / name for name in ("xquad.en.json", "xquad.vi.json", "xquad-download.json")]
def receipt(path):
    return {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "mtime_ns": path.stat().st_mtime_ns}
snapshot = {
    "files": {str(p.relative_to(root)): receipt(p) for p in paths},
    "cache": {p.name: receipt(p) for p in cache},
    "ids": {name: [json.loads(line)["id"] for line in (domain / "qa" / (name + ".jsonl")).read_text(encoding="utf-8").splitlines()] for name in ("en_en", "vi_vi", "vi_en", "en_vi")},
    "downloaded_at": json.loads((domain / "manifest.json").read_text(encoding="utf-8"))["downloaded_at"],
}
baseline = root / ".downloads/t07-a06-before.json"
if sys.argv[1] == "before":
    baseline.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"BEFORE: {len(paths)} published files; {len(cache)} cache files; slice IDs={ {name: len(ids) for name, ids in snapshot['ids'].items()} }")
else:
    assert snapshot == json.loads(baseline.read_text(encoding="utf-8")), "Rerun changed bytes/mtime/IDs/timestamp"
    print(f"RERUN PASS: {len(paths)} published + {len(cache)} cache hashes/mtimes, all slice IDs and downloaded_at unchanged")
report = json.loads((domain / "qa/preparation.json").read_text(encoding="utf-8"))
print("source_sha256=" + json.dumps(report["source_sha256"], sort_keys=True))
print("downloaded_at=" + snapshot["downloaded_at"])
for name in snapshot["ids"]:
    print(name + "_sha256=" + hashlib.sha256((domain / "qa" / (name + ".jsonl")).read_bytes()).hexdigest())
```


<a id="h-t08-a01"></a>
## H-T08-A01 - Complete corpus reproduction

- **Task/runtime:** Phase1/T08/A01, direct Codex agent; model/effort not exposed by runtime, no subagents. First recorded implementation timestamp `2026-09-26T17:35:06.9735939+07:00`; reading/preflight preceded it. User explicitly authorizes task-only changes, commit/push to origin/current branch, then stop. No merge/force/deploy.
- **Baseline:** `main` HEAD `1d36c0906c918106eafaecc42e457c1a1ae3827b`; `git ls-remote origin refs/heads/main` returned the same hash (exit0 after approved network escalation). Initial restricted-network invocation failed to connect (exit128); this was network sandboxing, not a changed remote. Git author preflight exit0, no identity printed/changed. `git status --short` showed only inherited `.ptmp-t07-a02/` and `.tmp-t07-a02/`; inaccessible `.pytmp-t07-a02/`, `.tmp-t07-a02/pytest-tmp/`, `UsersAdminAppDataLocalTempt07a03/` and global-ignore warnings preserved. No scratch deletion, no historical denied optional diagnostic repeated.
- **Read/dependencies:** AGENTS/task-session-prompt, full T07/T05/T06 and shared T04 notes, P01/P11/P13, entire original corpus prompt, handoffs/summary/README/RUNBOOK. T07 `1d36c09`, T06 closure `7d40fc4` + implementation `6863abf`, T05 `a2a94fb`, T04 `ad49ecc` COMPLETE. Original prompt SHA256 `7EC6E58AE4C24DB27AF4320BCB30222BBF2B67961D99C62980CEA4410AEE2C46` unchanged.
- **Environment for all commands below:** cwd `C:\Users\Admin\Documents\GitHub\rag-core`, Windows PowerShell, CPython3.12.4, uv0.11.16, pytest9.1.1. Environment prelude used before uv commands: `$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR = Join-Path (Get-Location) '.uv-python'`. Pytest basetemps are listed with commands. stdout/stderr captured to ignored `.local/t08-a01/*.log`; PowerShell wrapper saves `$LASTEXITCODE`, prints log and exits with that code. Logged commands below are the exact native process invocations with their redirects, independent gates executed separately. No DB/broker/inference/provider/model services needed; real source download is explicit live upstream I/O, unit fixtures are synthetic and never substitute for live DoD.
- **Config/sources:** inherited approved HF `hotpotqa/hotpot_qa` revision `1908d6afbbead072334abe2965f91bd2709910ab`, published Parquet SHA256 `c20b638ca82b21d04fe12e14ff417ad05153d4d215a65de54497fca4e972f7c6`; official FinanceBench `cc39aeb4afdf33909ee1412188bf89035950c2eb`; official XQuAD `7d30520c717524000f0d9d2f9c10a069acd9d285`, immutable source blob/SHA pins unchanged. Bounded transfer policies inherited; no new mirror/source override, no credentials needed, no LLM/model call or benchmark. License statements retained from dependency verification; no new redistribution/legal grant asserted.
- **Implementation/scope:** `corpus_root.py`, setup/validator, minimal three-domain preparation glue, generic aggregate notes, fingerprint helper, reproduction/common/bilingual tests, `.gitignore`/docs traversal, README/RUNBOOK/corpus/license notices and three execution documents. No schemas, dependency lock, API, DB/index, production ingestion, source prompt, source gold or model change. Isolated `.repro/` roots and legacy scratch excluded from commit.

<a id="h-t08-a01-dod1"></a>
### DoD-1 - all-domain setup, validation and prompt acceptance

Expected: canonical setup and standalone validator exit0 against real corpus; summary derived from validated reports. Actual: Default986docs/100QA, Document84PDF/150QA/189evidence with zero-based pages, Bilingual240EN+240VI/240groups/1190QA per four slices. Detailed outputs below.

| Prompt acceptance | Result and evidence |
| --- | --- |
| 1. Directory with three domains | PASS: canonical and isolated root manifests/data validated for default/document/bilingual. |
| 2. One setup command from clean state | PASS: absent `.repro/a2` checked before final cold setup; independent cache, live downloads, no manual source copying. Initial a1 diagnostic/fix preserved below. |
| 3. Hotpot documents and normalized QA | PASS: Default validator recomputes pinned source conversion, seed42 selection, all contexts/distractors and supporting-only gold;986docs/100QA. |
| 4. FinanceBench PDFs and human QA/evidence | PASS:84 real PDFs,150QA,189evidence; full exact source fields and page ranges validated. |
| 5. XQuAD EN and VI corpus | PASS:240 language-specific documents each,240 aligned groups. |
| 6. Four bilingual slices | PASS: en_en/vi_vi/vi_en/en_vi each1190, exact target-language counterpart answers/evidence. |
| 7. Every QA has valid document references | PASS: all three existing semantic validators reconstruct artifacts and validate references, unique IDs/nonempty values/gold/page/alignment. QA remains evaluator-only. |
| 8. Validator PASS | PASS: separate canonical and isolated `--all` invocations; missing-file negative control exits1. |
| 9. README source/license/counts/use | PASS: root README/RUNBOOK and corpus README/licenses updated; sources/pins, actual counts, QA/language/page policies, reproduction and limits documented. |
| 10. No hidden manual source steps | PASS: locked Python/dev dependencies plus one final clean setup; only runtime network approval required. No baseline training, auth workaround, cache seeding or restricted payload commit. |
| 11. Rerun no duplicates | PASS: all published/cache hashes/mtimes/IDs/counts/download timestamps unchanged; strict exact artifact sets. |
| 12. Final measured summary | PASS: setup/validator print validated per-domain counts/distribution/evidence/language slices and Validation: PASS. |

<a id="h-t08-a01-dod2"></a>
### DoD-2 - clean equality, rerun and missing-file failure

`verify_reproduction.py` compares 1574 published files, all normalized QA IDs/counts and exact payload hashes with the canonical corpus. Domain manifests compare canonical JSON excluding only downloaded_at. New download timestamps remain separate; rerun checks all published/cache byte hashes, sizes, mtimes and timestamps against its ignored baseline.92 cache files. Content digest `79a34f80d7e80995f519d2e0224beb0d891de28274b4628af2f36fa7a1f51646`; QA IDs digest `0b7e36c079dd013cceeccb1c8f65860f2e88163c51f10a392849877b7210f9f8`.

Deliberate missing-file test moved only the fresh a1 Default QA file to a checked backup path inside that same isolated root, invoked the real all-domain validator, expected/observed exit1, then restored in finally. Post-restore fingerprint check PASS proves hashes/mtimes/IDs/counts/receipts retained. No canonical file or user source deleted.

### Attempt diagnostics retained

- Initial apply_patch rejected duplicate operations on setup_corpus.py before mutation; split patch/write succeeded.
- First reproduction+bilingual run:40passed/1failed; Windows abspath erased trailing dot and let `.repro/a.` pass. Fixed by lexical rejection before normalization; final path tests pass. Ruff nested-with warning fixed.
- First fingerprint mypy found mixed list element inference; replaced repeated heterogeneous indexing with named string byte hash. Strict mypy19 later PASS.
- First record failed with `KeyError: 'id'`: bilingual paragraph indexes are JSONL document metadata, not QA rows. Helper now hashes every index as content and collects IDs only from question slice files; regression added.
- Next record correctly found inventory bytes differed while parsed JSON values were equal: bootstrap write_json reserialized provenance. Fixed initialization to copy exact inventory bytes. a1 diagnostic copy was corrected only after asserting semantic equality; no source/cache bytes copied. Final a2 cold setup uses corrected code with no manual repair, superseding a1 as one-command cold proof. Initial errors are not reported as PASS or discarded.
- Broad Ruff root scan emits inherited inaccessible-scratch warnings but exits0/All checks passed. Explicit src/tests/scripts/corpus scripts scan covers all code changed. No files excluded merely to hide a new failure.

### D1-D6 closure and limits

- **D1:** dependency scope and prompt read, changed-path review, `git diff --check`; baseline scratch preserved, T08 only.
- **D2:** locked sync resolved82/checked49;268 unit+contract PASS, final focused reproduction21 PASS (includes added fingerprint case); strict mypy19 and Ruff PASS. Failed interim runs retained below.
- **D3:** separate real canonical setup/validator, final cold setup/validator, fingerprint and rerun, negative control, and 12 prompt rows above. No mock-as-live substitution.
- **D4:** README/RUNBOOK/corpus README/license notices/tasks/handoffs/phase-task-attempt summary; docs links/UTF-8/dependency graph checked. No N/A docs waiver.
- **D5:** explicit diff/secrets/ignore/prompt review; raw/PDF/QA output copies/cache/scratch not staged. No migration/schema/contract breaking change or source pin/license expansion.
- **D6:** explicit task paths, staged diff check and commit `test(T08): verify complete corpus reproduction`; COMPLETE effective only after successful inspected commit. User allows push origin/main; actual commit and remote hash reported post-commit, no hash inserted into its own commit.
- **Known limits:** HF derivative not asserted CMU byte-equivalent; FinanceBench redistribution/company rights unresolved/local only; XQuAD has no unanswerable questions. All-domain publication is sequential; late failure retains earlier valid domains, returns nonzero and stops. Partial initialization/stale locks need operator inspection, no auto bypass. Fingerprints are not semantic validation. No benchmark/provider/model/GPU/deploy/Scarlet result claimed. T09/T03 dependency readiness only; stop after T08.

### Actual command outputs

#### Canonical setup / DoD-1

Command, exit **0**; local log `.local/t08-a01/setup-all.log`:

```powershell
uv run python corpus-documents/scripts/setup_corpus.py --all *> .local/t08-a01/setup-all.log
```

```text
Preparing default...
Preparing document...
Preparing bilingual...
RAG Evaluation Corpus
Default / HotpotQA: documents=986 QA=100
  seed=42 distribution={'by_type': {'bridge': 50, 'comparison': 50}, 'by_level': {'hard': 100}, 'strata': {'bridge/hard': 50, 'comparison/hard': 50}}
Document / FinanceBench: PDFs=84 QA=150
  evidence=189 page_indexing=zero_based
Bilingual / XQuAD: documents={'en': 240, 'vi': 240}
  QA_slices={'en_en': 1190, 'vi_vi': 1190, 'vi_en': 1190, 'en_vi': 1190} parallel_groups=240
Validation: PASS
CORPUS SETUP: PASS
```

#### Canonical standalone validator / DoD-1

Command, exit **0**; local log `.local/t08-a01/validate-all.log`:

```powershell
uv run python corpus-documents/scripts/validate_corpus.py --all *> .local/t08-a01/validate-all.log
```

```text
RAG Evaluation Corpus
Default / HotpotQA: documents=986 QA=100
  seed=42 distribution={'by_type': {'bridge': 50, 'comparison': 50}, 'by_level': {'hard': 100}, 'strata': {'bridge/hard': 50, 'comparison/hard': 50}}
Document / FinanceBench: PDFs=84 QA=150
  evidence=189 page_indexing=zero_based
Bilingual / XQuAD: documents={'en': 240, 'vi': 240}
  QA_slices={'en_en': 1190, 'vi_vi': 1190, 'vi_en': 1190, 'en_vi': 1190} parallel_groups=240
Validation: PASS
CORPUS VALIDATION: PASS
```

#### First clean setup a1 / diagnostic run

Command, exit **0**; local log `.local/t08-a01/clean-setup.log`:

```powershell
if (Test-Path -LiteralPath corpus-documents/.repro/a1) { throw 'Clean output root already exists' }; uv run python corpus-documents/scripts/setup_corpus.py --all --output-root corpus-documents/.repro/a1 *> .local/t08-a01/clean-setup.log
```

```text
Preparing default...
Preparing document...
Preparing bilingual...
RAG Evaluation Corpus
Default / HotpotQA: documents=986 QA=100
  seed=42 distribution={'by_type': {'bridge': 50, 'comparison': 50}, 'by_level': {'hard': 100}, 'strata': {'bridge/hard': 50, 'comparison/hard': 50}}
Document / FinanceBench: PDFs=84 QA=150
  evidence=189 page_indexing=zero_based
Bilingual / XQuAD: documents={'en': 240, 'vi': 240}
  QA_slices={'en_en': 1190, 'vi_vi': 1190, 'vi_en': 1190, 'en_vi': 1190} parallel_groups=240
Validation: PASS
CORPUS SETUP: PASS
```

#### First clean standalone validator

Command, exit **0**; local log `.local/t08-a01/clean-validate.log`:

```powershell
uv run python corpus-documents/scripts/validate_corpus.py --all --output-root corpus-documents/.repro/a1 *> .local/t08-a01/clean-validate.log
```

```text
RAG Evaluation Corpus
Default / HotpotQA: documents=986 QA=100
  seed=42 distribution={'by_type': {'bridge': 50, 'comparison': 50}, 'by_level': {'hard': 100}, 'strata': {'bridge/hard': 50, 'comparison/hard': 50}}
Document / FinanceBench: PDFs=84 QA=150
  evidence=189 page_indexing=zero_based
Bilingual / XQuAD: documents={'en': 240, 'vi': 240}
  QA_slices={'en_en': 1190, 'vi_vi': 1190, 'vi_en': 1190, 'en_vi': 1190} parallel_groups=240
Validation: PASS
CORPUS VALIDATION: PASS
```

#### First fixture/path failure

Command, exit **1**; local log `.local/t08-a01/tests1.log`:

```powershell
$env:PYTEST_ADDOPTS = '--basetemp=.local/p8a'; uv run pytest tests/unit/test_corpus_reproduction.py tests/unit/test_corpus_bilingual.py *> .local/t08-a01/tests1.log
```

```text
============================= test session starts =============================
platform win32 -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Admin\Documents\GitHub\rag-core
configfile: pyproject.toml
plugins: anyio-4.15.1, asyncio-1.4.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 41 items

tests\unit\test_corpus_reproduction.py ........F...........              [ 48%]
tests\unit\test_corpus_bilingual.py .....................                [100%]

================================== FAILURES ===================================
__________ test_output_refuses_unsafe_or_protected_paths[.repro/a.] ___________

metadata_root = WindowsPath('C:/Users/Admin/Documents/GitHub/rag-core/.local/p8a/test_output_refuses_unsafe_or_8/c')
relative = '.repro/a.'

    @pytest.mark.parametrize("relative", ["..", "default", "scripts", ".downloads/x", ".repro", ".repro/a/b", ".repro/CON", ".repro/a:stream", ".repro/a.", ".repro/../outside"])
    def test_output_refuses_unsafe_or_protected_paths(metadata_root: Path, relative: str) -> None:
>       with pytest.raises(common.CorpusError):
E       Failed: DID NOT RAISE CorpusError

tests\unit\test_corpus_reproduction.py:38: Failed
=========================== short test summary info ===========================
FAILED tests/unit/test_corpus_reproduction.py::test_output_refuses_unsafe_or_protected_paths[.repro/a.]
======================== 1 failed, 40 passed in 21.11s ========================
```

#### Initial fingerprint index error

Command, exit **1**; local log `.local/t08-a01/record.log`:

```powershell
uv run python corpus-documents/scripts/verify_reproduction.py record --output-root corpus-documents/.repro/a1 *> .local/t08-a01/record.log
```

```text
uv : Traceback (most recent call last):
At line:2 char:127
+ ... uv-python'; uv run python corpus-documents/scripts/verify_reproductio ...
+                 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (Traceback (most recent call last)::String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError

  File "C:\Users\Admin\Documents\GitHub\rag-core\corpus-documents\scripts\verify_reproduction.py", line 101, in
<module>
    raise SystemExit(main())
                     ^^^^^^
  File "C:\Users\Admin\Documents\GitHub\rag-core\corpus-documents\scripts\verify_reproduction.py", line 80, in main
    candidate = snapshot(root)
                ^^^^^^^^^^^^^^
  File "C:\Users\Admin\Documents\GitHub\rag-core\corpus-documents\scripts\verify_reproduction.py", line 42, in snapshot
    identifiers = [item["id"] for item in read_jsonl(path)]
                   ~~~~^^^^^^
KeyError: 'id'
```

#### Inventory byte equality diagnostic

Command, exit **1**; local log `.local/t08-a01/record2.log`:

```powershell
uv run python corpus-documents/scripts/verify_reproduction.py record --output-root corpus-documents/.repro/a1 *> .local/t08-a01/record2.log
```

```text
uv : REPRODUCTION: FAIL - Reproduction differs from standard corpus: content
At line:2 char:127
+ ... uv-python'; uv run python corpus-documents/scripts/verify_reproductio ...
+                 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (REPRODUCTION: F...corpus: content:String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError
```

#### a1 fingerprint after bootstrap correction

Command, exit **0**; local log `.local/t08-a01/record3.log`:

```powershell
uv run python corpus-documents/scripts/verify_reproduction.py record --output-root corpus-documents/.repro/a1 *> .local/t08-a01/record3.log
```

```text
REPRODUCTION record: PASS
published_files=1574 cache_files=92
content_sha256=79a34f80d7e80995f519d2e0224beb0d891de28274b4628af2f36fa7a1f51646 IDs_sha256=0b7e36c079dd013cceeccb1c8f65860f2e88163c51f10a392849877b7210f9f8
counts={'default': [986, 100], 'document': [84, 150], 'bilingual': [480, 4760]}
downloaded_at={'default': '2026-09-26T10:38:52.979498+00:00', 'document': '2026-09-26T10:39:11.741202+00:00', 'bilingual': '2026-09-26T10:41:54.153313+00:00'}
```

#### a1 rerun

Command, exit **0**; local log `.local/t08-a01/clean-rerun.log`:

```powershell
uv run python corpus-documents/scripts/setup_corpus.py --all --output-root corpus-documents/.repro/a1 *> .local/t08-a01/clean-rerun.log
```

```text
Preparing default...
Preparing document...
Preparing bilingual...
RAG Evaluation Corpus
Default / HotpotQA: documents=986 QA=100
  seed=42 distribution={'by_type': {'bridge': 50, 'comparison': 50}, 'by_level': {'hard': 100}, 'strata': {'bridge/hard': 50, 'comparison/hard': 50}}
Document / FinanceBench: PDFs=84 QA=150
  evidence=189 page_indexing=zero_based
Bilingual / XQuAD: documents={'en': 240, 'vi': 240}
  QA_slices={'en_en': 1190, 'vi_vi': 1190, 'vi_en': 1190, 'en_vi': 1190} parallel_groups=240
Validation: PASS
CORPUS SETUP: PASS
```

#### a1 rerun fingerprint

Command, exit **0**; local log `.local/t08-a01/rerun-check.log`:

```powershell
uv run python corpus-documents/scripts/verify_reproduction.py check --output-root corpus-documents/.repro/a1 *> .local/t08-a01/rerun-check.log
```

```text
REPRODUCTION check: PASS
published_files=1574 cache_files=92
content_sha256=79a34f80d7e80995f519d2e0224beb0d891de28274b4628af2f36fa7a1f51646 IDs_sha256=0b7e36c079dd013cceeccb1c8f65860f2e88163c51f10a392849877b7210f9f8
counts={'default': [986, 100], 'document': [84, 150], 'bilingual': [480, 4760]}
downloaded_at={'default': '2026-09-26T10:38:52.979498+00:00', 'document': '2026-09-26T10:39:11.741202+00:00', 'bilingual': '2026-09-26T10:41:54.153313+00:00'}
```

#### Full unit and contract regression

Command, exit **0**; local log `.local/t08-a01/tests2.log`:

```powershell
$env:PYTEST_ADDOPTS = '--basetemp=.local/p8b'; uv run pytest tests/unit tests/contract/test_api_schema.py *> .local/t08-a01/tests2.log
```

```text
============================= test session starts =============================
platform win32 -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Admin\Documents\GitHub\rag-core
configfile: pyproject.toml
plugins: anyio-4.15.1, asyncio-1.4.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 268 items

tests\unit\test_corpus_bilingual.py ......................               [  8%]
tests\unit\test_corpus_common.py ....................................... [ 22%]
.........................................                                [ 38%]
tests\unit\test_corpus_default.py .....................................  [ 51%]
tests\unit\test_corpus_document.py ...................                   [ 58%]
tests\unit\test_corpus_reproduction.py ....................              [ 66%]
tests\unit\test_health.py ...                                            [ 67%]
tests\unit\test_settings.py ....                                         [ 69%]
tests\contract\test_api_schema.py ...................................... [ 83%]
.............................................                            [100%]

======================= 268 passed in 73.89s (0:01:13) ========================
```

#### Final focused reproduction regression

Command, exit **0**; local log `.local/t08-a01/tests-final.log`:

```powershell
$env:PYTEST_ADDOPTS = '--basetemp=.local/p8c'; uv run pytest tests/unit/test_corpus_reproduction.py *> .local/t08-a01/tests-final.log
```

```text
============================= test session starts =============================
platform win32 -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Admin\Documents\GitHub\rag-core
configfile: pyproject.toml
plugins: anyio-4.15.1, asyncio-1.4.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 21 items

tests\unit\test_corpus_reproduction.py .....................             [100%]

============================= 21 passed in 3.88s ==============================
```

#### Final cold setup a2 / DoD-2

Command, exit **0**; local log `.local/t08-a01/final-clean-setup.log`:

```powershell
if (Test-Path -LiteralPath corpus-documents/.repro/a2) { throw 'Clean output root already exists' }; uv run python corpus-documents/scripts/setup_corpus.py --all --output-root corpus-documents/.repro/a2 *> .local/t08-a01/final-clean-setup.log
```

```text
Preparing default...
Preparing document...
Preparing bilingual...
RAG Evaluation Corpus
Default / HotpotQA: documents=986 QA=100
  seed=42 distribution={'by_type': {'bridge': 50, 'comparison': 50}, 'by_level': {'hard': 100}, 'strata': {'bridge/hard': 50, 'comparison/hard': 50}}
Document / FinanceBench: PDFs=84 QA=150
  evidence=189 page_indexing=zero_based
Bilingual / XQuAD: documents={'en': 240, 'vi': 240}
  QA_slices={'en_en': 1190, 'vi_vi': 1190, 'vi_en': 1190, 'en_vi': 1190} parallel_groups=240
Validation: PASS
CORPUS SETUP: PASS
```

#### Final standalone clean validator

Command, exit **0**; local log `.local/t08-a01/final-clean-validate.log`:

```powershell
uv run python corpus-documents/scripts/validate_corpus.py --all --output-root corpus-documents/.repro/a2 *> .local/t08-a01/final-clean-validate.log
```

```text
RAG Evaluation Corpus
Default / HotpotQA: documents=986 QA=100
  seed=42 distribution={'by_type': {'bridge': 50, 'comparison': 50}, 'by_level': {'hard': 100}, 'strata': {'bridge/hard': 50, 'comparison/hard': 50}}
Document / FinanceBench: PDFs=84 QA=150
  evidence=189 page_indexing=zero_based
Bilingual / XQuAD: documents={'en': 240, 'vi': 240}
  QA_slices={'en_en': 1190, 'vi_vi': 1190, 'vi_en': 1190, 'en_vi': 1190} parallel_groups=240
Validation: PASS
CORPUS VALIDATION: PASS
```

#### Final clean fingerprint baseline

Command, exit **0**; local log `.local/t08-a01/final-record.log`:

```powershell
uv run python corpus-documents/scripts/verify_reproduction.py record --output-root corpus-documents/.repro/a2 *> .local/t08-a01/final-record.log
```

```text
REPRODUCTION record: PASS
published_files=1574 cache_files=92
content_sha256=79a34f80d7e80995f519d2e0224beb0d891de28274b4628af2f36fa7a1f51646 IDs_sha256=0b7e36c079dd013cceeccb1c8f65860f2e88163c51f10a392849877b7210f9f8
counts={'default': [986, 100], 'document': [84, 150], 'bilingual': [480, 4760]}
downloaded_at={'default': '2026-09-26T10:48:40.607938+00:00', 'document': '2026-09-26T10:48:57.865950+00:00', 'bilingual': '2026-09-26T10:50:39.594444+00:00'}
```

#### Final root Ruff

Command, exit **0**; local log `.local/t08-a01/ruff-all.log`:

```powershell
uv run ruff check . *> .local/t08-a01/ruff-all.log
```

```text
uv : warning: Encountered error: Access is denied. (os error 5)
At line:25 char:127
+ ... uv-python'; uv run ruff check . *> .local/t08-a01/ruff-all.log; $resu ...
+                 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (warning: Encoun...d. (os error 5):String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError

warning: Encountered error: Access is denied. (os error 5)
warning: Encountered error: Access is denied. (os error 5)
All checks passed!
```

#### Final strict types

Command, exit **0**; local log `.local/t08-a01/mypy-final2.log`:

```powershell
uv run mypy src corpus-documents/scripts *> .local/t08-a01/mypy-final2.log
```

```text
Success: no issues found in 19 source files
```


#### Missing-file negative control and restoration

Exact PowerShell command after the common uv environment prelude, overall exit **0**;
inner validator exit **1** as expected, fingerprint after restoration exit **0**:

```powershell
$probeRoot = (Resolve-Path -LiteralPath corpus-documents/.repro/a1).Path; $probeSource = [IO.Path]::GetFullPath((Join-Path $probeRoot 'default/qa/eval.jsonl')); $probeBackup = [IO.Path]::GetFullPath((Join-Path $probeRoot '.missing-eval.jsonl')); if (-not $probeSource.StartsWith($probeRoot + '\') -or -not $probeBackup.StartsWith($probeRoot + '\') -or (Test-Path -LiteralPath $probeBackup)) { throw 'Unsafe probe paths' }; Move-Item -LiteralPath $probeSource -Destination $probeBackup; try { uv run python corpus-documents/scripts/validate_corpus.py --all --output-root corpus-documents/.repro/a1 *> .local/t08-a01/missing-file.log; $probeExit = $LASTEXITCODE; Get-Content .local/t08-a01/missing-file.log; Write-Output "missing-file validator exit=$probeExit (expected 1)"; if ($probeExit -ne 1) { throw 'Missing-file gate failed' } } finally { Move-Item -LiteralPath $probeBackup -Destination $probeSource }; uv run python corpus-documents/scripts/verify_reproduction.py check --output-root corpus-documents/.repro/a1 *> .local/t08-a01/restored-check.log; $result = $LASTEXITCODE; Get-Content .local/t08-a01/restored-check.log; exit $result
```

Actual excerpt (PowerShell stderr decoration omitted; full local log
`.local/t08-a01/missing-file.log`):

```text
uv : CORPUS VALIDATION: FAIL - Default corpus has missing, duplicate, or unmanaged artifacts
missing-file validator exit=1 (expected 1)
```

Restoration output, `.local/t08-a01/restored-check.log`:

```text
REPRODUCTION check: PASS
published_files=1574 cache_files=92
content_sha256=79a34f80d7e80995f519d2e0224beb0d891de28274b4628af2f36fa7a1f51646 IDs_sha256=0b7e36c079dd013cceeccb1c8f65860f2e88163c51f10a392849877b7210f9f8
counts={'default': [986, 100], 'document': [84, 150], 'bilingual': [480, 4760]}
downloaded_at={'default': '2026-09-26T10:38:52.979498+00:00', 'document': '2026-09-26T10:39:11.741202+00:00', 'bilingual': '2026-09-26T10:41:54.153313+00:00'}
```

#### Initial environment and review checks

Commands `uv sync --locked --group dev --group api`, `git var GIT_AUTHOR_IDENT | Out-Null`
and `Get-FileHash -Algorithm SHA256 -LiteralPath 'corpus-documents/Codex Prompt – Build RAG Evaluation Corpus.md'`
ran with the stated cwd; exits0.
Actual sync output: `Resolved 82 packages in 2ms` / `Checked 49 packages in 57ms`.
Author preflight emitted no identity. Prompt hash as recorded above.

`git check-ignore corpus-documents/.repro/a2/document/qa/eval.jsonl corpus-documents/.repro/a2/document/documents/3M_2018_10K.pdf corpus-documents/.repro/a2/.verification.json corpus-documents/.downloads/xquad.en.json`
exit0 returned every path, proving payload/QA/verification/cache exclusion. Existing global-ignore
permission warning remained. Initial `git diff --check` detected trailing whitespace only in
newly pasted PowerShell error excerpts; removed trailing display whitespace from the new
T08 section, preserving historical evidence and substantive output. Final check recorded below.


#### Final a2 rerun

Command, exit **0**; local log `.local/t08-a01/final-rerun.log`:

```powershell
uv run python corpus-documents/scripts/setup_corpus.py --all --output-root corpus-documents/.repro/a2 *> .local/t08-a01/final-rerun.log
```

```text
Preparing default...
Preparing document...
Preparing bilingual...
RAG Evaluation Corpus
Default / HotpotQA: documents=986 QA=100
  seed=42 distribution={'by_type': {'bridge': 50, 'comparison': 50}, 'by_level': {'hard': 100}, 'strata': {'bridge/hard': 50, 'comparison/hard': 50}}
Document / FinanceBench: PDFs=84 QA=150
  evidence=189 page_indexing=zero_based
Bilingual / XQuAD: documents={'en': 240, 'vi': 240}
  QA_slices={'en_en': 1190, 'vi_vi': 1190, 'vi_en': 1190, 'en_vi': 1190} parallel_groups=240
Validation: PASS
CORPUS SETUP: PASS
```


#### Final a2 rerun equality

Command, exit **0**; local log `.local/t08-a01/final-rerun-check.log`:

```powershell
uv run python corpus-documents/scripts/verify_reproduction.py check --output-root corpus-documents/.repro/a2 *> .local/t08-a01/final-rerun-check.log
```

```text
REPRODUCTION check: PASS
published_files=1574 cache_files=92
content_sha256=79a34f80d7e80995f519d2e0224beb0d891de28274b4628af2f36fa7a1f51646 IDs_sha256=0b7e36c079dd013cceeccb1c8f65860f2e88163c51f10a392849877b7210f9f8
counts={'default': [986, 100], 'document': [84, 150], 'bilingual': [480, 4760]}
downloaded_at={'default': '2026-09-26T10:48:40.607938+00:00', 'document': '2026-09-26T10:48:57.865950+00:00', 'bilingual': '2026-09-26T10:50:39.594444+00:00'}
```


#### Explicit source Ruff

Command, exit **0**; local log `.local/t08-a01/ruff-explicit.log`:

```powershell
uv run ruff check src tests scripts corpus-documents/scripts *> .local/t08-a01/ruff-explicit.log
```

```text
All checks passed!
```


#### Documentation validation

Command, exit **0**; local log `.local/t08-a01/docs1.log`:

```powershell
uv run python scripts/check_docs.py *> .local/t08-a01/docs1.log
```

```text
PASS UTF-8/nonempty Markdown: 14 files
PASS internal links/anchors: 247
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```


### Final D1/D4/D5/D6 review boundary

`git diff --check` exit0 (no whitespace errors). `uv --version` exit0:
`uv 0.11.16 (135a36367 2026-05-21 x86_64-pc-windows-msvc)`.
Explicit path/UTF-8/size/credential-pattern/original-prompt inspection output:

```text
D1/D5 review: PASS; 20 explicit task files, UTF-8/size/credential-pattern/prompt checks; no unexpected tracked changes.
No raw/PDF/QA copies, weights, cache, scratch, source prompt, API, schema or dependency lock in scope.
```

Actual stage command, exit0 after user-authorized Git write escalation:

```powershell
git add -- .gitignore README.md RUNBOOK.md corpus-documents/README.md corpus-documents/licenses/README.md corpus-documents/manifest.json corpus-documents/scripts/corpus_root.py corpus-documents/scripts/verify_reproduction.py corpus-documents/scripts/setup_corpus.py corpus-documents/scripts/validate_corpus.py corpus-documents/scripts/prepare_default.py corpus-documents/scripts/prepare_document.py corpus-documents/scripts/prepare_bilingual.py docs/tasks.md docs/handoffs.md docs/implementation-summary.md scripts/check_docs.py tests/unit/test_corpus_common.py tests/unit/test_corpus_bilingual.py tests/unit/test_corpus_reproduction.py
```

`git diff --cached --check` exit0/no output; `git diff --cached --stat` reported
`20 files changed, 1156 insertions(+), 157 deletions(-)` before this final evidence append.
Cached name list matched all20 explicit paths; no raw/corpus QA/cache/scratch. Added this
review evidence, then restaged only handoffs and reran cached/docs checks before commit.
`uv run python scripts/check_docs.py *> .local/t08-a01/docs-final.log` exit0:

```text
PASS UTF-8/nonempty Markdown: 14 files
PASS internal links/anchors: 250
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```

Completion command: `git commit -m "test(T08): verify complete corpus reproduction"`.
Actual commit output/hash and authorized `git push origin main` result are returned to the
user after commit, together with `git ls-remote origin refs/heads/main` equality. No self hash
or claimed push success is embedded before execution. Completion status is valid only after
the successful inspected commit; failure would require a new checkpoint, not COMPLETE.


<a id="h-t09-a01"></a>
## H-T09-A01 — Phase 2 / JWT, service identity and local issuer

Direct Codex agent, exact model/effort not exposed; no subagents. Started/ended2026-09-27.
CWD for all commands: `C:\Users\Admin\Documents\GitHub\rag-core`.
Scope:19 files listed in final review below, no corpus/prompt/Scarlet/T10 changes.
Baseline main/HEAD `5f851c38ede7430a2dd41f32beed2108ad7d3e64` (T08 COMPLETE);
T03 COMPLETE notes/summary, T08 notes/summary, AGENTS/task-session prompt,
P01/P05/P06/P13, README/RUNBOOK/current checkpoint read before implementation.
Baseline dirty: untracked `.ptmp-t07-a02/`, `.tmp-t07-a02/`; preserved.
Git reported legacy ACL warnings for `.pytmp-t07-a02/`,
`.tmp-t07-a02/pytest-tmp/`, `UsersAdminAppDataLocalTempt07a03/`
and user global ignore file. No cleanup or optional historical denied diagnostic.

### Environment and dependency preparation

PowerShell environment used for uv commands:

```powershell
$env:UV_CACHE_DIR='.uv-cache'
$env:UV_PYTHON_INSTALL_DIR='.uv-python'
```

`uv add --group api 'pyjwt[crypto]==2.15.0'` initially exit1: sandbox network
`Failed to fetch: https://pypi.org/simple/httpx/` / `os error 10013`.
Same scoped dependency operation retried with approved network escalation, then
`uv sync --locked --group dev --group api`: exit0, actual excerpt:

```text
Resolved 83 packages in 1.26s
Prepared 2 packages in 1.62s
 + pyjwt==2.15.0
Resolved 83 packages in 1ms
Checked 50 packages in 2ms
```

No automatic approval rejection. PyPI official artifacts only, exact PyJWT2.15.0
pin+wheel/sdist hashes in uv.lock; no unrelated dependency upgrade. Official
[PyJWT API reference](https://pyjwt.readthedocs.io/en/stable/api.html) and
[usage](https://pyjwt.readthedocs.io/en/stable/usage.html) inspected for fixed
algorithm allowlist/required claims/signature validation, not token-selected algorithms.

Commands `uv --version` and the following version check exit0:

```powershell
uv run python -c "import sys, jwt, cryptography, httpx, uvicorn; print('Python', sys.version.split()[0], 'PyJWT', jwt.__version__, 'cryptography', cryptography.__version__, 'HTTPX', httpx.__version__, 'Uvicorn', uvicorn.__version__)"
```

```text
Python 3.12.4 PyJWT 2.15.0 cryptography 50.0.1 HTTPX 0.28.1 Uvicorn 0.53.0
uv 0.11.16 (135a36367 2026-05-21 x86_64-pc-windows-msvc)
```

Services: generated ephemeral local RSA2048/public JWKS over real loopback HTTP;
DoD-2 uses CLI JWKS process + Uvicorn test API. No DB/Redis/Qdrant/MinIO/model/provider
used or claimed live; HealthChecks injection in test only avoids unrelated health probes,
not auth/crypto/network. API app itself retains real health adapter defaults.

<a id="h-t09-a01-dod1"></a>
### DoD-1 — Security and fail-closed identity

Initial `uv run pytest tests/security/test_auth.py -q` with
`PYTEST_ADDOPTS=--basetemp=.local/t09-security-01`: exit0, `49 passed in 32.06s`.
Added meaningful deadline/cancellation/startup-failure coverage, then final exact command:

```powershell
$env:PYTEST_ADDOPTS='--basetemp=.local/9s'
uv run pytest tests/security/test_auth.py *> .local/t09-a01/security.log
```

Exit **0**, expected rejection/identity/rotation/config gates all pass. Actual excerpt
from ignored local log `.local/t09-a01/security.log`:

```text
platform win32 -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0
collected 51 items
tests\security\test_auth.py ............................................ [ 86%]
.......                                                                  [100%]
============================= 51 passed in 32.20s =============================
```

- Wrong signature, none/HS alg, issuer/audience/exp/nbf/future iat, missing claims,
  app mismatch including shared trust tuple, invalid/empty subject/NumericDates -> rejected.
- Token `jku/jwk/x5u/x5c/crit` rejected before fetch; signed user_id/JWKS URL cannot
  override subject/config; forged body user_id/app_id/jwks_url422; duplicate headers401.
- Real JWKS endpoint, per-app cache isolation, old+new key rotation, removed key401,
  TTL, unknown-kid flood/coalescing, expired-cache outage503/recovery; no stale extension.
  Clock is controlled for cache boundaries only; RSA signatures/HTTP JWKS are real.
- Untrusted transport/URL, duplicate app/key mapping, private/ambiguous/oversized/malformed
  JWKS/weak key/redirect, deadline/cancellation checked; no auth config503 and explicit
  bad config startup failure. T03 ErrorEnvelope validates401/503 without secrets.

<a id="h-t09-a01-dod2"></a>
### DoD-2 — CLI JWT consumed over real HTTP

Initial `uv run pytest tests/security/test_local_auth_http.py -q -s`,
`PYTEST_ADDOPTS=--basetemp=.local/t09-http-01`: exit0, `1 passed in 4.61s`.
Final after formatting, separate invocation:

```powershell
$env:PYTEST_ADDOPTS='--basetemp=.local/9h'
uv run pytest tests/security/test_local_auth_http.py -s *> .local/t09-a01/http.log
```

Exit **0**, log `.local/t09-a01/http.log`; actual output:

```text
collected 1 item
tests\security\test_local_auth_http.py REAL HTTP AUTH: PASS; CLI RS256 -> public JWKS -> protected API 200; missing credentials 401; forged identity 422; unmounted route 404; empty JWKS after TTL 503; private files 404; no credentials displayed
.
============================== 1 passed in 4.07s ==============================
```

Test launches actual CLI `init --directory <fresh-temp>/auth --port <ephemeral>`,
`token --directory ... --subject http-user --output .../user.jwt`, and
`serve --directory ... --port ...` subprocess; generates256bit-service-key/RSA2048 fixture
at runtime. File credentials never printed; exclusive directory/token overwrite refusal
verified. Uvicorn serves a test-only `/v1/auth-test` handler using production auth middleware
and `require_principal`, strict SessionCreateRequest. HTTPX uses real TCP/trust_env=False.
JWT is resolved against live JWKS, gives `local-dev/http-user`; old cache expires after
real1.1s elapsed against configTTL1s, empty JWKS503. No mocked provider/ASGI-only success
substitutes this DoD. Both servers stopped in finally; test endpoint not mounted in app.
README/RUNBOOK document generated secrets, redacted headers, cache/revocation and limits.

### D2 regression, failures retained and resolution

Initial command (before adapting T03 assertion):

```powershell
$env:PYTEST_ADDOPTS='--basetemp=.local/t09-regression-01'
uv run pytest tests/unit tests/contract -q
```

Exit **1**, actual output excerpts (initial full output was in terminal, not saved to disk):

```text
FAILED tests/unit/test_corpus_default.py::test_prepare_and_rerun_preserve_ids_content_timestamp_and_mtimes
E                   assert 503 == 404
FAILED tests/contract/test_api_schema.py::test_designed_business_endpoints_are_unmounted_and_never_stub_success
11 failed, 258 passed in 47.51s
```

Ten Default corpus tests failed while creating deep atomic `.part` paths under the long
Windows basetemp. No corpus code/data/gold change: use short fresh ignored basetemp as
existing RUNBOOK advises. Remaining failure is the intended T09 behavior change: `/v1`
now fails closed before routing. Contract regression now asserts no business route mounted
plus503 dependency_unavailable without registry, not a stub success; real authenticated
unmounted404 verified in DoD-2. Final exact command:

```powershell
$env:PYTEST_ADDOPTS='--basetemp=.local/9r'
uv run pytest tests/unit tests/contract -q *> .local/t09-a01/regression.log
```

Exit **0**, output `.local/t09-a01/regression.log`:

```text
........................................................................ [ 26%]
........................................................................ [ 53%]
........................................................................ [ 80%]
.....................................................                    [100%]
269 passed in 65.47s (0:01:05)
```

Earlier Ruff found SIM105 in new deadline fixture; replaced try/except/pass with
contextlib.suppress, no behavior/test weakening. Source/new-test formatting only.

### Quality, docs and final review

Commands executed separately, all exit0:

```powershell
uv run ruff check .
uv run mypy src
uv sync --locked --group dev --group api
uv run python scripts/export_openapi.py --check
git diff --check
```

Actual output excerpts:

```text
All checks passed!
Success: no issues found in 16 source files
Resolved 83 packages in 0.98ms
Checked 50 packages in 1ms
PASS checked docs/api/openapi-v1.designed.json
PASS checked docs/api/openapi.served.json
PASS checked docs/api/examples-v1.json
PASS designed_operations=13 served_health_routes=2 synthetic_examples=37
PASS OpenAPI model + Draft2020-12 schemas=48; examples JSON Schema + Pydantic
CONTRACT EXPORT: PASS (business endpoints unmounted; no runtime query/stream verification)
```

Ruff additionally reported three inherited `Access is denied (os error5)` traversal
warnings; final explicit changed-source checks also run to avoid relying on inaccessible
scratch scanning. `git diff --check` had no whitespace errors; initial tasks CRLF advisory
fixed by final UTF-8/LF write. No runtime schema snapshot/DB/index migration.

`git remote get-url origin`, branch/log/author check: exit0,
`https://github.com/admininistrator/rag-core.git`, `main`, `Git author configured`.
`git ls-remote origin refs/heads/main` initially exit1 sandbox connection blocked;
approved read-only network escalation exit0:

```text
5f851c38ede7430a2dd41f32beed2108ad7d3e64 refs/heads/main
```

Full completion scope (19 files): `.env.example`, README.md, RUNBOOK.md,
`docs/{tasks,handoffs,implementation-summary}.md`, pyproject.toml, uv.lock,
`src/rag_core/api/{app,auth}.py`, `src/rag_core/auth/{__init__,config,verifier,local_issuer}.py`,
`src/rag_core/config/settings.py`, `tests/contract/test_api_schema.py`,
`tests/security/{conftest,test_auth,test_local_auth_http}.py`.
D1 scope/dependency/P01 review; D2 checks above; D3 each DoD separately;
D4 README/RUNBOOK/task/summary/evidence; D5 fixed algorithm/no token URLs/no raw corpus,
keys/cache/scratch/secrets in explicit stage. D6 subject
`feat(T09): implement authenticated application principals`, actual commit/hash and
remote equality reported after execution; no self-reference hash or preclaimed push.

Known limits: no Docker image/issuer wiring rerun, production JWKS/LLM/services/session
scope/query/admin verification. HTTP fixture alone grants no data access. T10 dependencies
T09/T02 ready only after successful closure. **Stop after T09**, no next task implementation.


### D4/D5/D6 final closure evidence

`uv run python scripts/check_docs.py *> .local/t09-a01/docs-final.log` exit0:

```text
PASS UTF-8/nonempty Markdown: 14 files
PASS internal links/anchors: 258
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```

`uv run ruff check src/rag_core tests/security tests/contract/test_api_schema.py`
exit0 `All checks passed!`; `uv run mypy src` exit0
`Success: no issues found in 16 source files`. `git diff --check` and
`git diff --exit-code -- corpus-documents AGENTS.md docs/plan.md` exit0/no output.
`git check-ignore .local/9h .local/9s .local/t09-a01` exit0, all three paths ignored.
Explicit file-set/UTF-8/size/credential-pattern inspection exit0:

```text
D1/D5 review: PASS; 19 explicit UTF-8 task files; no unexpected tracked/src/test/doc files; no private-key material or JWT literals.
Runtime credentials/logs remain ignored; original corpus/prompt/AGENTS/plan unchanged. No DB/index/schema migration.
```

Actual stage command, exit0 (approved Git-index write escalation):

```powershell
git add -- .env.example README.md RUNBOOK.md docs/tasks.md docs/handoffs.md docs/implementation-summary.md pyproject.toml uv.lock src/rag_core/api/app.py src/rag_core/api/auth.py src/rag_core/auth/__init__.py src/rag_core/auth/config.py src/rag_core/auth/verifier.py src/rag_core/auth/local_issuer.py src/rag_core/config/settings.py tests/contract/test_api_schema.py tests/security/conftest.py tests/security/test_auth.py tests/security/test_local_auth_http.py
```

`git diff --cached --check` exit0/no output. Cached stat before this evidence append:
`19 files changed, 1460 insertions(+), 23 deletions(-)`.
Staged-vs-reviewed exact-file/content/secret check exit0:

```text
D6 staged review: PASS; exact 19 files; staged content matches reviewed worktree; no credential material detected.
```

After this append, restage only handoffs and rerun docs/cached checks.
Completion command `git commit -m "feat(T09): implement authenticated application principals"`;
then inspect actual commit19file inventory/whitespace, execute authorized
`git push origin main`, and compare `git rev-parse HEAD` with
`git ls-remote origin refs/heads/main`. Post-execution results are reported to the user,
not embedded as fabricated pre-commit success. If commit fails, T09 is not COMPLETE.

<a id="h-t10-a01"></a>
## H-T10-A01 — Phase 2 / Metadata schema and session scope

Direct Codex agent; exact model/effort unavailable, no subagents. Started/ended2026-09-27.
CWD for every command below: `C:\Users\Admin\Documents\GitHub\rag-core`.
Baseline main/HEAD `9e67d5d513c751930e4548ae9c292501444963a4`, T09 COMPLETE;
`git ls-remote origin refs/heads/main` returned the same hash. T02/T09 execution notes,
summaries, current handoff, AGENTS/task-session prompt, P01/P04/P06/P13, README/RUNBOOK
read before code. Inherited untracked `.ptmp-t07-a02/`, `.tmp-t07-a02/` and ACL warnings
for legacy `.pytmp-t07-a02/`, nested pytest temp, `UsersAdminAppDataLocalTempt07a03/`
and global Git ignore retained; no cleanup. No existing T10 candidate.

Allowed: core domain/port + PG adapter, frozen Alembic revision/environment, isolated
test Compose, integration/config tests, dependency groups/lock, five living docs.
User authorizes scoped commit and origin/current-branch push; no force/merge/deploy.
R05 explicitly leaves business HTTP mounting to T26; T10 implements repository methods,
not placeholder HTTP success or T12 registration/worker.

### Environment and failures retained

PowerShell uv environment for commands below:

```powershell
$env:UV_CACHE_DIR='.uv-cache'
$env:UV_PYTHON_INSTALL_DIR='.uv-python'
```

Initial sandbox `docker compose ps` could not read user Docker config and daemon pipe;
escalated `docker context show; docker compose ps` reported `desktop-linux` and missing
`dockerDesktopLinuxEngine` pipe. Started installed Docker Desktop hidden:

```powershell
Start-Process -FilePath 'C:\Program Files\Docker\Docker\Docker Desktop.exe' -WindowStyle Hidden
docker info --format '{{.ServerVersion}}'
docker compose ps
```

Exit0; actual server `29.5.2`, existing application project had no running containers.
No automatic approval rejection. Escalated calls permit Docker/network/loopback tests.
Application volumes and sources were not reset or migrated.

After adding shared metadata group to api/ingestion, `uv lock` then
`uv sync --locked --group dev --group api`: exit0, actual excerpt:

```text
Resolved 83 packages in 807ms
Installed 6 packages in 141ms
 + alembic==1.20.0
 + greenlet==3.5.6
 + mako==1.4.1
 + markupsafe==3.0.3
 ~ rag-core==0.1.0 (from file:///C:/Users/Admin/Documents/GitHub/rag-core)
 + sqlalchemy==2.0.53
```

No package version upgrades; existing locked packages enter installed graph. Lock adds
asyncio extra and official same-version greenlet platform wheels, no heavyweight model
dependency. Official [SQLAlchemy Psycopg dialect](https://docs.sqlalchemy.org/en/20/dialects/postgresql.html),
[Alembic tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html),
[Psycopg async](https://www.psycopg.org/psycopg3/docs/advanced/async.html) and
[pytest-asyncio loop factory](https://pytest-asyncio.readthedocs.io/en/stable/reference/hooks.html)
informed driver/migration/Windows configuration.

First `uv run pytest tests/integration/test_session_scope.py -v -s` (basetemp `.local/10a`)
exit1,16setup errors; migration had already succeeded. Exact redacted diagnostic:

```text
0001_session_metadata (head)
Psycopg cannot use the 'ProactorEventLoop' to run in async mode. Please use a compatible event loop
======================= 2 warnings, 16 errors in 5.51s ========================
```

Long pytest traceback printed driver connection kwargs including an existing local
PostgreSQL password `[REDACTED]`. It is not copied into this file or any tracked artifact.
This was an actual diagnostic disclosure, not a hypothetical warning. T10 test service
was changed to an independently generated ignored `t10_postgres_password`, recreated
with disposable tmpfs, and subsequent runs use `--tb=short` and fresh local cache.
Original T02 credential/file/database was not changed; operator should rotate the
exposed original local credential separately. New test credential is not a rotation
of the original. No claim that previous tool transcript can be erased.

Fix: integration-only pytest-asyncio SelectorEventLoop factory, as required by Psycopg
on Windows. Initial Ruff SIM117 and six mypy RowMapping-vs-Mapping diagnostics fixed
using combined transaction context and SQLAlchemy RowMapping types; no test skip or
semantics change. Initial docs check failed missing `h-t10-a01` before this evidence
was appended; final documentation check below supersedes it.

`uv run python -c "import sys, sqlalchemy, alembic, psycopg; print('Python',sys.version.split()[0], 'SQLAlchemy',sqlalchemy.__version__, 'Alembic',alembic.__version__, 'Psycopg',psycopg.__version__)"`
exit0:

```text
Python 3.12.4 SQLAlchemy 2.0.53 Alembic 1.20.0 Psycopg 3.3.5
```

### DoD-1 — Empty DB migration and real PG scope

Separate secret creation (exit0, no credential output):

```powershell
uv run python -c "from pathlib import Path; import secrets; p=Path('.local/secrets/t10_postgres_password'); p.touch(exist_ok=False); p.write_text(secrets.token_hex(32),encoding='utf-8'); print('Created separate ignored T10 PostgreSQL secret')"
docker compose -f compose.metadata-test.yaml up -d --force-recreate --wait
$env:DATABASE_URL='postgresql://rag_core_test@127.0.0.1:55432/t10_acceptance'
$env:DATABASE_PASSWORD_FILE='.local/secrets/t10_postgres_password'
$env:RAG_TEST_DATABASE_URL=$env:DATABASE_URL
$env:PYTEST_ADDOPTS='--basetemp=.local/10b --tb=short -o cache_dir=.local/10cache'
uv run alembic upgrade head
uv run alembic current
uv run pytest tests/integration/test_session_scope.py -v -s
```

Each command exit0. Recreate is only the disposable T10 project, never application
Compose. Expected: new empty PG database, revision head, owner/session isolation.
Actual excerpt:

```text
Created separate ignored T10 PostgreSQL secret
 Container rag-core-metadata-test-postgres-1 Recreated
 Container rag-core-metadata-test-postgres-1 Healthy
0001_session_metadata (head)
============================= 16 passed in 3.04s ==============================
```

After adding source/generation/job/outbox constraint coverage and explicit assertion
that newly created DBs have zero public tables, final DoD-1 command (exit0):

```powershell
$env:PYTEST_ADDOPTS='--basetemp=.local/10d --tb=short -o cache_dir=.local/10cache'
uv run pytest tests/integration/test_session_scope.py -v -s
```

Actual output excerpt, all18tests executed with PG and no mocks:

```text
collecting ... collected 18 items
Real PostgreSQL: separate database t10_test_d59c32c0009943d0a70a2f66ea63f3ce, public tables before migration=0
Real PostgreSQL: migrated separate database t10_test_d59c32c0009943d0a70a2f66ea63f3ce
PASS isolation: app/user/current-session, explicit new registration, independent detach
PASS repeated/concurrent delete: one revision, retained rows byte-equivalent, no resurrection
PASS real lock race: old coherent snapshot then revision invalidation; replay stays detached
============================= 18 passed in 2.47s ==============================
```

Coverage: app/user/same-owner-other-session; concurrent create unique mapping; same
external ID legal under other principals; empty/deleted/unknown/duplicate/oversized
subset; mixed ready + every8nonready states fail without partial scope; foreign subset
404; explicit ready subset; exact version/generation pairs and owner FKs; unpublished
generation refusal; source fingerprint required; max50active; transactional rollback.
No broad library listing or global fallback exists.

### DoD-2 — Idempotent delete, concurrent snapshot and separate DB reproduction

Lifecycle tests above execute real concurrent connections: five concurrent deletes
produce one tombstone/revision bump; all source/document/version/generation/job/outbox
rows compare equal before/after. Pending worker publication does not recreate links;
detached registration replay stays detached, new registration can attach explicitly.
A held row lock plus observed `pg_stat_activity.wait_event_type='Lock'` proves detach
was blocked while old consistent snapshot was read; after commit revision invalidates
that snapshot. Reindex publication invalidates by pair equality even without revision
change; staging generation leaves old active scope unchanged. No mock clock/DB/lock.

Separate command, same safe environment, exit0:

```powershell
uv run pytest tests/integration/test_metadata_migrations.py -v -s
```

Actual output:

```text
collecting ... collected 1 item
Real PostgreSQL: separate database t10_test_362ebdcee89f489f9e3cd9a9e93ddd8c, public tables before migration=0
Real PostgreSQL: migrated separate database t10_test_362ebdcee89f489f9e3cd9a9e93ddd8c
PASS separate empty PG migration -> repeat head -> downgrade base -> upgrade head: identical schema
============================== 1 passed in 2.99s ==============================
```

Compares columns/types/defaults/nullability plus every constraint/index. Tests drop only
their own random `t10_test_<uuid>` databases. Migration admin URL is restricted to
loopback `t10_acceptance`; fail missing config/service, never skip/SQLite substitution.
`downgrade base` is destructive only inside this throwaway test DB. Main app data untouched.

Service/version inspection, both exit0:

```powershell
docker compose -f compose.metadata-test.yaml ps
docker compose -f compose.metadata-test.yaml exec -T postgres psql -U rag_core_test -d t10_acceptance -c 'SELECT version(); SELECT version_num FROM alembic_version;'
```

Actual excerpt:

```text
rag-core-metadata-test-postgres-1 ... Up 43 seconds (healthy) 127.0.0.1:55432->5432/tcp
PostgreSQL 17.11 (Debian 17.11-1.pgdg12+2) on x86_64-pc-linux-gnu, compiled by gcc (Debian 12.2.0-14+deb12u1) 12.2.0, 64-bit
0001_session_metadata
```

Pinned image digest `sha256:051f7b7b3abdd564d5d1bd1e8c4b9c1b6e77087d1dd22020ede611c096a272e0`;
separate project/tmpfs, no application volume/host-port changes. Real services used:
PostgreSQL17.11 for T10; loopback JWKS/Uvicorn for inherited T09 regression only.
No provider/model/LLM/Qdrant/MinIO inference/retention call was claimed live. T10 adapter
has no storage/vector clients or derivative deletion methods; retained metadata rows
are verified, actual pipeline/chunks/vector integration remains T19/T32.

### D2 — Regression, types, lint and locked environment

Separate regression shell (no DB environment required), exit0:

```powershell
$env:PYTEST_ADDOPTS='--basetemp=.local/ar --tb=short -o cache_dir=.local/10regcache'
uv run pytest tests/unit tests/contract tests/security
uv run python scripts/export_openapi.py --check
```

Actual output excerpt:

```text
collected 325 items
tests\unit\test_metadata_config.py ....                                  [ 57%]
tests\security\test_local_auth_http.py .                                 [100%]
======================= 325 passed in 108.13s (0:01:48) =======================
PASS checked docs/api/openapi-v1.designed.json
PASS checked docs/api/openapi.served.json
PASS checked docs/api/examples-v1.json
PASS designed_operations=13 served_health_routes=2 synthetic_examples=37
PASS OpenAPI model + Draft2020-12 schemas=48; examples JSON Schema + Pydantic
CONTRACT EXPORT: PASS (business endpoints unmounted; no runtime query/stream verification)
```

`uv run ruff check .`, `uv run mypy src`,
`uv sync --locked --group dev --group api` each exit0:

```text
warning: Encountered error: Access is denied. (os error 5)
warning: Encountered error: Access is denied. (os error 5)
warning: Encountered error: Access is denied. (os error 5)
All checks passed!
Success: no issues found in 24 source files
Resolved 83 packages in 2ms
Checked 55 packages in 4ms
```

Root Ruff warnings are inherited inaccessible scratch; explicit
`uv run ruff check src tests/integration tests/unit/test_metadata_config.py migrations`
exit0 `All checks passed!`. Config tests check malformed/missing DSN and password file
errors without echoing input; no tests written for prose-only changes.

### D1/D3/D4/D5/D6 — Review and completion boundary

- D1: task/dependency scope reviewed, `git diff --check` exit0/no output; no AGENTS/plan,
  corpus/prompt, auth/runtime API, application Compose, source data or Scarlet edits.
- D3: both DoD rows above run individually on real PG; no credential/provider gate
  substituted. Current final acceptance19integration +325regression tests.
- D4: README/RUNBOOK describe schema ownership, mapping, CLI env, migrations/recovery,
  internal registration transaction, revision/pair revalidation, test setup, Windows
  loop and HTTP/storage/worker limitations; tasks/summary/evidence updated together.
- D5: schema is first revision, frozen DDL/transaction advisory lock, no startup migration,
  no destructive lifecycle cascade. Forward upgrade/no app client change; downgrade
  documented destructive and tested only in own DB. Lock official sources/no upgrades.
  Credential diagnostic incident above is retained/redacted; no secret value in Git.
- D6: stage exact task files; completion subject
  `feat(T10): add session-scoped metadata persistence`. COMPLETE only valid after
  successful inspected commit. Actual hash/push/remote equality returned post-execution,
  not fabricated inside its own commit. T11 dependencies T10/T02 ready then; stop.

Final review command outputs are appended below after documentation closure.

### Final D4/D5/D6 evidence

Final migration helper is injected as a fixture rather than importing `conftest`
directly, avoiding cross-suite module name collisions. Checked alongside auth tests
(same PG environment; basetemp `.local/10e`), exit0:

```powershell
uv run pytest tests/integration/test_metadata_migrations.py tests/security/test_auth.py -q -s
```

```text
Real PostgreSQL: separate database t10_test_d6fcc54bf30f42c49c55d58dd1334585, public tables before migration=0
Real PostgreSQL: migrated separate database t10_test_d6fcc54bf30f42c49c55d58dd1334585
PASS separate empty PG migration -> repeat head -> downgrade base -> upgrade head: identical schema
52 passed in 35.47s
```

`uv run ruff check src tests/integration tests/unit/test_metadata_config.py migrations`,
`uv run mypy src`, `uv run python scripts/check_docs.py`, `git diff --check` each exit0:

```text
All checks passed!
Success: no issues found in 24 source files
PASS UTF-8/nonempty Markdown: 14 files
PASS internal links/anchors: 265
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```

`git check-ignore .local/secrets/t10_postgres_password .local/secrets/postgres_password`
exit0, both paths ignored. Git author was already configured; not changed. Read/reviewed
actual adapter/domain/port/migration/test code and README/RUNBOOK/dependency diff. No
unrelated dependency upgrade, source/prompt edit, URL service credential or fake identity.

Completion contains exactly24task files; task COMPLETE label is contingent on the
successful commit below. Expected inherited scratch remains untracked after commit.

Actual explicit staging command (exit0), no `git add .`:

```powershell
git add -- README.md RUNBOOK.md docs/tasks.md docs/handoffs.md docs/implementation-summary.md pyproject.toml uv.lock alembic.ini compose.metadata-test.yaml migrations/env.py migrations/script.py.mako migrations/versions/0001_session_metadata.py src/rag_core/adapters/__init__.py src/rag_core/adapters/persistence/__init__.py src/rag_core/adapters/persistence/database.py src/rag_core/adapters/persistence/sessions.py src/rag_core/domain/__init__.py src/rag_core/domain/metadata.py src/rag_core/ports/__init__.py src/rag_core/ports/metadata.py tests/integration/conftest.py tests/integration/test_session_scope.py tests/integration/test_metadata_migrations.py tests/unit/test_metadata_config.py
git diff --cached --check
git diff --cached --stat
git diff --name-only
```

Cached check and unstaged diff empty; stage24files, code/tests/migration/config/docs
only. Before this final evidence append, stat reported1887insertions/19deletions.
Actual secret/artifact check below exit0; it prints only the verdict, never secret values:

```powershell
uv run python -c "from pathlib import Path; import subprocess; names=subprocess.check_output(['git','diff','--cached','--name-only'],text=True).splitlines(); secrets=[Path('.local/secrets/postgres_password').read_bytes().strip(),Path('.local/secrets/t10_postgres_password').read_bytes().strip()]; blobs=[subprocess.check_output(['git','show',':'+name]) for name in names]; assert len(names)==24; assert all(not name.startswith(('.local/','corpus-documents/','.env','.ptmp','.tmp')) for name in names); assert not any(secret and secret in blob for secret in secrets for blob in blobs), 'staged credential detected'; assert not any(b'-----BEGIN PRIVATE KEY-----' in blob for blob in blobs); print('PASS exact 24-file stage; no local credentials/private keys or excluded artifacts')"
```

```text
PASS exact 24-file stage; no local credentials/private keys or excluded artifacts
```

Stopped only test PostgreSQL after verification; `docker compose -f compose.metadata-test.yaml stop`
and `docker compose -f compose.metadata-test.yaml ps --all` exit0:

```text
 Container rag-core-metadata-test-postgres-1 Stopped
rag-core-metadata-test-postgres-1 ... Exited (0) Less than a second ago
```

After this append, restage only handoffs, rerun docs/cached review, then execute
`git commit -m "feat(T10): add session-scoped metadata persistence"`. Inspect commit24files
and `git show --check`; authorized `git push origin main`, then compare
`git rev-parse HEAD` against `git ls-remote origin refs/heads/main`. Actual post-execution
hash/status belongs in user report; no self-reference hash or fabricated future success.

<a id="h-t11-a01"></a>
## H-T11-A01 — T11 read-only S3/MinIO adapter, 2026-09-30

All commands below ran in `C:\Users\Admin\Documents\GitHub\rag-core` (PowerShell, Windows). Baseline `main`/`2a67f8b53b65371a71ca72719cd6d0cd5025b899`; `origin` is `https://github.com/admininistrator/rag-core.git`. Initial `git status --short` exit 0: only inherited `?? .ptmp-t07-a02/`, `?? .tmp-t07-a02/`; access warnings on old T07 scratch and user Git ignore. Those directories and old app sources untouched. Runtime model/effort not exposed. Config: Docker 29.5.2, pinned local MinIO `RELEASE.2025-07-23T15-54-02Z`, MC `RELEASE.2025-07-21T05-28-08Z`, boto3 1.43.94, botocore 1.43.94; no provider/model. Secrets read from ignored `.local/secrets`; no values logged.

**Setup / real service:** `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\bootstrap_local.ps1` exit 0 (`Kept existing ignored local secret file` x3); `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\bootstrap_storage_test.ps1` exit 0 (`T11 ignored reader/uploader secret files ready; values not printed.`). `docker compose -f compose.yaml -f compose.storage-test.yaml --profile local-storage --profile storage-test config --quiet` exit 0/no output. `docker compose -f compose.yaml -f compose.storage-test.yaml --profile local-storage --profile storage-test up -d --wait minio` exit 0: `Container rag-core-minio-1 Healthy`. `docker compose -f compose.yaml -f compose.storage-test.yaml --profile local-storage --profile storage-test run --rm storage-fixture` exit 0: `T11 isolated bucket and separate reader/uploader principals are ready.` Isolated bucket versioning enabled; separate reader and uploader IAM policies, root used solely for provisioner. `docker compose -f compose.yaml -f compose.storage-test.yaml --profile local-storage --profile storage-test ps --all` exit 0: MinIO `Up 12 minutes (healthy)`, `127.0.0.1:9000-9001->9000-9001/tcp`; other T02 services stopped as at baseline.

**DoD-1 expected:** actual MinIO GET correct bytes, denied prefix, old pinned version, changed source, size cap, interrupted download and temp cleanup. Command `$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv run --no-sync pytest -q tests/integration/test_storage_reader.py --basetemp .local/t11-pytest` exit **0**:

```text
.....                                                                    [100%]
5 passed in 1.79s
```

Separate DoD-1 line command `$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv run --no-sync pytest -q tests/integration/test_storage_reader.py::test_real_read_and_reader_iam tests/integration/test_storage_reader.py::test_real_version_id_pins_old_bytes tests/integration/test_storage_reader.py::test_scope_change_size_and_interrupted_stream --basetemp .local/t11-dod1` exit **0**:

```text
...                                                                      [100%]
3 passed in 0.58s
```

**DoD-2 expected/actual:** test `test_real_read_and_reader_iam` observes actual MinIO `AccessDenied` for core reader PUT/DELETE/outside-prefix GET and confirms SHA-256 of uploader GET before/after identical; `test_operator_endpoint_and_redirect_guard` rejects arbitrary HTTP endpoint/userinfo/path/query plus redirect event; local HTTP 307 redirect test confirms source endpoint received request and target received zero. No fake IAM success. Separate command `$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv run --no-sync pytest -q tests/integration/test_storage_reader.py::test_operator_endpoint_and_redirect_guard tests/integration/test_storage_reader.py::test_live_http_redirect_never_reaches_target --basetemp .local/t11-dod2` exit **0**:

```text
..                                                                       [100%]
2 passed in 1.36s
```

**D1/D2/D3:** `git diff --check` exit 0/no output; T11-only files reviewed against T10/T02 notes/P01/P04/P05/P07/P13. `$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv run --no-sync ruff check .` exit 0, `All checks passed!` (three inherited inaccessible scratch warnings). `$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv run --no-sync mypy src` exit 0, `Success: no issues found in 27 source files`. `$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv run --no-sync pytest -q tests/unit tests/contract tests/security --basetemp .local/t11-suite` exit **0**, `325 passed in 107.31s (0:01:47)`. `$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv run --no-sync python scripts/export_openapi.py --check` exit 0: designed/served/examples PASS, `designed_operations=13 served_health_routes=2 synthetic_examples=37`; business endpoints unmounted. DoD lines run separately above; no external AWS/provider verification claimed.

**Diagnostic preserved:** first bootstrap storage script exit1 under Windows PowerShell 5 because `RandomNumberGenerator.Fill` then `Convert.ToHexString` unavailable; fixed with `Create().GetBytes()` and byte hex formatting, rerun exit0. Initial `uv run --group dev --group ingestion ...` without sandbox escalation failed to fetch locked `vine`/`h2` (`os error 10013`); approved `uv sync --locked --group dev --group api --group ingestion` with local `.uv-cache` exit0, `Resolved 83 packages`, then checks used `--no-sync`. Docker API also required approved daemon access; `docker version --format '{{.Server.Version}}'` exit0 `29.5.2`. Initial live redirect test exit1 `RecursionError: maximum recursion depth exceeded` in botocore's region redirect handler; fixed by rejecting HTTP 3xx at `needs-retry.s3` before botocore redirect logic. Final 5 tests and separate DoD runs exit0. No secret from local files included here.

**D4:** README/RUNBOOK/.env.example and task/summary updated with trust boundary, config, exact live commands and limits. `$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv run --no-sync python scripts/check_docs.py` exit **0**: `PASS UTF-8/nonempty Markdown: 14 files`, `PASS internal links/anchors: 271`, `PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic`, `DOCUMENTATION CHECK: PASS`.

**D5/D6 review:** `git check-ignore .local/secrets/minio_reader_password .local/secrets/minio_uploader_password .local/t11-pytest` exit0, all three paths ignored. `git diff --cached --name-only` exit0 lists exactly 16 T11 files (adapter/port/config, integration tests, isolated Compose/policies/bootstrap, README/RUNBOOK/.env and three task docs); inherited T07 scratch absent. PowerShell in-memory comparison of four ignored local password values with staged diff exit0: `PASS staged diff contains no local secret values`; no values printed. First `git diff --cached --check` exit1 found one new blank line at EOF in storage package `__init__.py`; corrected and restaged before final check. No schema/API migration, provider/model change, raw corpus or log. `docker compose -f compose.yaml -f compose.storage-test.yaml --profile local-storage --profile storage-test stop minio` exit0, `Container rag-core-minio-1 Stopped`, volume preserved. Completion subject `feat(T11): add read-only application storage adapter`; actual commit/hash/remote equality reported post-execution, not self-referenced here.

<a id="h-t12-a01"></a>
## H-T12-A01 — Phase 2 / Upload registration and durable jobs, 2026-09-30

**Baseline/scope:** cwd `C:\Users\Admin\Documents\GitHub\rag-core`, branch `main`, HEAD `06185be330c090d59a5924e449f2502f7b3dc4cb` (`feat(T11): add read-only application storage adapter`). `git status --short` at start: `?? .ptmp-t07-a02/`, `?? .tmp-t07-a02/`; inaccessible historical scratch retained. `git remote -v` shows `origin https://github.com/admininistrator/rag-core.git` fetch/push. Initial `git ls-remote origin refs/heads/main` exit128 under sandbox: `Failed to connect to github.com port 443`; remote verification must use approved access before push. T11/T10 COMPLETE. Read AGENTS/task-session-prompt, complete dependency notes, P01/P04/P06/P12/P13, current handoff, summary, README/RUNBOOK before code. Authenticated app/user and app-confirmed upload ID are trusted assertion boundary; storage key alone never grants ownership.

**Environment/services:** Python3.12.4, uv0.11.16, PostgreSQL17.11 in isolated `compose.metadata-test.yaml` project on loopback55432 with tmpfs, Redis8.10.1 via `compose.registration-test.yaml` on loopback16379/DB15 (no flush), MinIO T11 fixture on loopback9000, separate uploader and read-only core IAM. Passwords remain under ignored `.local/secrets/`; `DATABASE_URL=postgresql://rag_core_test@127.0.0.1:55432/t10_acceptance`, `DATABASE_PASSWORD_FILE=.local/secrets/t10_postgres_password`, `RAG_TEST_DATABASE_URL=$env:DATABASE_URL`, `UV_CACHE_DIR=.uv-cache`; values not logged. No external provider/model/Qdrant/worker. First unprivileged `docker compose ... up` exit1 `permission denied ... npipe:////./pipe/docker_engine`; approved escalation then commands `docker compose -f compose.metadata-test.yaml -f compose.registration-test.yaml up -d --wait postgres redis` exit0, both healthy; `docker compose --profile local-storage up -d --wait minio` exit0 healthy; `docker compose -f compose.yaml -f compose.storage-test.yaml --profile local-storage --profile storage-test run --rm storage-fixture` exit0 `T11 isolated bucket and separate reader/uploader principals are ready.`

**DoD-1 — PASS, actual services.** Expected: same key/body same job; changed body409; concurrent duplicates one registration; Redis unavailable leaves pending event and recovery publishes; wrong app/owner 404. Command (PowerShell, cwd above), exit0:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'
$env:DATABASE_URL='postgresql://rag_core_test@127.0.0.1:55432/t10_acceptance'
$env:DATABASE_PASSWORD_FILE='.local/secrets/t10_postgres_password'
$env:RAG_TEST_DATABASE_URL=$env:DATABASE_URL
uv run --no-sync pytest tests/integration/test_registration_jobs.py -k 'not crash_redelivery_delete_and_retry_are_safe' -v -s --tb=short --basetemp=.local/t12-final-d1 -o cache_dir=.local/t12-final-cd1
```

```text
Real PostgreSQL: separate database t10_test_9deaa591efa9487bb9dbb56c021ab12a, public tables before migration=0
Real PostgreSQL: migrated separate database t10_test_9deaa591efa9487bb9dbb56c021ab12a
PASS real PG/MinIO/Redis: idempotency, concurrent duplicate, owner, broker recovery
PASS real MinIO/PG: invalid prefix rollback; detached replay; fresh session upload binding
======================= 2 passed, 1 deselected in 9.05s =======================
```

Test also checks untrusted prefix rejection leaves zero PG rows, owner isolation before storage access, fresh session starts empty, detached key replay stays detached and only new registration binds. Redis publisher uses real Celery protocol/queue; `dispatcher --once` subprocess connects to migrated PG and real Redis. HTTP 202 itself not served pending T26.

**DoD-2 — PASS, actual crash/redelivery observation.** Expected: simulated crash after Redis publish before PG commit leaves event pending; replay yields duplicate broker message but one consumer claim/job/link; deletion before retry publish cancels without resurrection. Same environment, separate command exit0:

```powershell
uv run --no-sync pytest tests/integration/test_registration_jobs.py -k crash_redelivery_delete_and_retry_are_safe -v -s --tb=short --basetemp=.local/t12-final-d2 -o cache_dir=.local/t12-final-cd2
```

```text
Real PostgreSQL: separate database t10_test_1d76798480b1446d9c773f8c8031e32f, public tables before migration=0
Real PostgreSQL: migrated separate database t10_test_1d76798480b1446d9c773f8c8031e32f
PASS real PG/Redis: crash redelivery claim-once; tombstone blocks reattach/publish
======================= 1 passed, 2 deselected in 1.52s =======================
```

Consumer gate is `claim_job`, not a T19 parser/LLM worker. Session deletion is tested before publishing a retry event. Job status/retry method tested against real PG; no `ready` claim.

**D1–D3 quality/regression:** `git diff --check` exit0/no output. T10 regression `$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; $env:DATABASE_URL='postgresql://rag_core_test@127.0.0.1:55432/t10_acceptance'; $env:DATABASE_PASSWORD_FILE='.local/secrets/t10_postgres_password'; $env:RAG_TEST_DATABASE_URL=$env:DATABASE_URL; uv run --no-sync pytest tests/integration/test_session_scope.py tests/integration/test_metadata_migrations.py -q --tb=short --basetemp=.local/t12-t10-regression2 -o cache_dir=.local/t12-cache-t10-2` exit0 `19 passed in 6.23s`; T12 migration table added to historical schema expectation. `$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv run --no-sync pytest -q tests/unit tests/contract tests/security --tb=short --basetemp=.t12a -o cache_dir=.local/t12-cache-regression-short` exit0 `325 passed in 167.71s (0:02:47)`; self-created `.t12a` removed after checking resolved target within repo. Initial longer `--basetemp=.local/t12-regression` exit1 `10 failed, 315 passed` from Windows `FileNotFoundError` on >path-limit corpus temp paths; rerun short path PASS, no corpus code/gold edited. Source-targeted Ruff exit0 `All checks passed!`; strict mypy exit0 `Success: no issues found in 32 source files`. `docker compose --profile registration build dispatcher` exit0 `Image rag-core-dispatcher:t12 Built`; `docker run --rm rag-core-dispatcher:t12 python -m rag_core.adapters.broker.dispatcher --help` exit0, shows `--once`/`--interval`. Compose config quiet exit0. Docker image uses locked ingestion group, no model/OCR runtime.

**D4:** README/RUNBOOK describe working service/CLI, migration, ownership assertion, 202/poll/retry/error *target* HTTP examples and unmounted T26 boundary; tasks/summary/handoff updated. `$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv run --no-sync python scripts/export_openapi.py --check` exit0 `designed_operations=13 served_health_routes=2 synthetic_examples=37`; no contract change. Initial `scripts/check_docs.py` exit1 because this handoff anchor had not yet been written; after adding anchor, `uv run --no-sync python scripts/check_docs.py` exit0: `PASS UTF-8/nonempty Markdown: 14 files`, `PASS internal links/anchors: 278`, `PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic`, `DOCUMENTATION CHECK: PASS`. `uv lock --check` exit0 `Resolved 83 packages in 1ms`; no dependency/lock changes.

**D5/D6 final review:** `$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv run --no-sync ruff check .; uv run --no-sync mypy src` both exit0: `All checks passed!` (three inherited inaccessible scratch warnings), `Success: no issues found in 32 source files`. `git diff --check` exit0/no output. `git ls-remote origin refs/heads/main` with approved network access exit0 `06185be330c090d59a5924e449f2502f7b3dc4cb refs/heads/main`, equal baseline. Full task test command `$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; $env:DATABASE_URL='postgresql://rag_core_test@127.0.0.1:55432/t10_acceptance'; $env:DATABASE_PASSWORD_FILE='.local/secrets/t10_postgres_password'; $env:RAG_TEST_DATABASE_URL=$env:DATABASE_URL; uv run --no-sync pytest tests/integration/test_registration_jobs.py -v -s --tb=short --basetemp=.local/t12-final-all -o cache_dir=.local/t12-final-call` exit0 `3 passed in 9.37s`. Initial unprivileged `git add -- ...` exit128 `Unable to create .git/index.lock: Permission denied`; approved staging of explicit 16 T12 files exit0. `git diff --cached --check` exit0, file list exactly README/RUNBOOK, 2 Compose, dispatcher Dockerfile, 3 task docs, migration, broker package/adapter/CLI, registration repository/domain, 2 integration test files. Two inherited T07 scratch directories remain untracked and unstaged. PowerShell compared ignored local PostgreSQL/MinIO password values in memory against staged diff, exit0 `PASS staged diff contains no compared local secret values`; no values printed. Additive schema, owner checks, worker/HTTP limits, no raw corpus/model/secret or provider changes reviewed. Completion subject `feat(T12): register uploads with durable ingestion jobs`; actual commit/hash/remote equality returned post-execution, not self-referenced.

**Service teardown:** `docker compose -f compose.metadata-test.yaml -f compose.registration-test.yaml stop postgres redis` exit0, both test containers `Stopped`; `docker compose --profile local-storage stop minio` exit0, `rag-core-minio-1 Stopped`. No `down -v`, volume deletion or source object deletion outside unique test keys.

<a id="h-t13-a01"></a>
## H-T13-A01 — Phase 3 / Intermediate model and text parsers, 2026-10-01

**Baseline/runtime/scope:** cwd `C:\Users\Admin\Documents\GitHub\rag-core`, `main`, HEAD/T12 `094f74452307a8645eeb1d00a0a0af738b4403e9`. Direct Codex agent (GPT-6 family; exact model/effort not exposed), no subagents. T12/T03 COMPLETE; task/dependency notes, P01/P02/P07/P13, AGENTS/task-session-prompt and living docs/checkpoint/summary read before code. `git status --short` returned only `?? .ptmp-t07-a02/`, `?? .tmp-t07-a02/`, with inherited inaccessible scratch/global-ignore warnings; untouched. No unfinished T13 files. `git log -3 --format='%h %s'` exit0:

```text
094f744 feat(T12): register uploads with durable ingestion jobs
06185be feat(T11): add read-only application storage adapter
2a67f8b feat(T10): add session-scoped metadata persistence
```

`git ls-remote origin refs/heads/main` first exit128 (`Failed to connect to github.com port 443` in sandbox); authorized network escalation exit0:

```text
094f74452307a8645eeb1d00a0a0af738b4403e9	refs/heads/main
```

`git var GIT_AUTHOR_IDENT | Out-Null; if ($LASTEXITCODE -eq 0) { Write-Output 'Git author configured' }` exit0, `Git author configured`; no identity change. User explicitly permits scoped commit/push origin/current branch; no force/merge/deploy.

**Environment/dependencies:** host Python3.12.4/uv0.11.16, pytest9.1.1. No service/provider/model/weights/OCR involved. Native Docling Parse7.22.1 API verified against [official README](https://github.com/docling-project/docling-parse#sequential-parsing) and installed package; DOCX python-docx1.2.0, pypdf6.19.0 crypto, defusedxml0.7.1. Pins only ingestion; inference remains empty. `UV_CACHE_DIR=.uv-cache`; unique parser sandbox below test temp; fixtures synthetic, not corpus QA/raw licensed PDFs.

Setup commands (cwd above), each exit0; network add/sync used authorized escalation:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv add --group ingestion 'docling-parse==7.22.1' 'python-docx==1.2.0' 'pypdf[crypto]==6.19.0' --no-sync
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv sync --locked --group dev --group api --group ingestion
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv add --offline --group ingestion 'defusedxml==0.7.1' --no-sync
```

Actual setup excerpts:

```text
Resolved 101 packages in 2.22s
Resolved 101 packages in 1ms
Prepared 19 packages in 3.12s
Installed 19 packages in 578ms
+ docling-core==2.99.0
+ docling-parse==7.22.1
+ python-docx==1.2.0
+ defusedxml==0.7.1
Resolved 101 packages in 62ms
```

Two upstream invalid-version-specifier normalization warnings did not fail resolution. Official wheel URLs/hashes locked; later locked offline sync below.

**Diagnostics retained:** initial read probes used nonexistent `domain/locators.py`/`api/schemas.py`; actual T03 models are `contracts/v1.py`. Installed API probe `DoclingPdfParser.unload` raised `AttributeError`; corrected to returned `PdfDocument.unload()`. Initial Ruff exit1 for imports/class mutable defaults, mypy exit1 for python-docx Path argument; fixed imports/frozensets/str(path). First fixture-run command had Ruff exit1 for12 nonraw pytest regex literals (PowerShell continued to pytest); fixed literals, no initial lint PASS claim. Actual first tests: `15 passed in 12.27s`; expanded `19 passed in 14.18s`. Apply-patch context mismatches made no changes, corrected after reading formatted lines. Review added worker temp environment/caller-exception kill/cleanup, Setext/fence handling and HTML-as-data in Markdown code; final tests below.

**DoD mapping:** DoD-1 expected real EN/VI format fixtures, multi-page PDF/DOCX page break/tables, source locator round-trip, corrupt/AES encrypted errors; actual19PASS/no skips below. PDF physical1/2 and printed i/ii separate, native offsets/bbox and table/header/unit text; DOCX heading/paragraph/table/XPath/nested/header/footer/no page; TXT/MD BOM/CRLF/Unicode positions; HTML entities/headings/table/raw span. DoD-2 expected MIME/size/deadline/temp gates, inert script/external refs; actual8PASS/no skips below: loopback canary0requests, real ZIP bombs/traversal/VBA/entities refused without extraction, process killed/reaped, original source unchanged and sandbox empty on every parse, concurrent real execution bounded. PDF missing-text detection is OCR-required/partial, not scan/OCR verification.

### DoD-1 — Real parsers and source provenance

Cwd repository root; host/config below; exit **0**.

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv run --no-sync pytest tests/integration/test_text_parsers.py -v -s --tb=short --basetemp=.local/t13-final-dod1 -o cache_dir=.local/t13-cache-final-dod1
```

```text
============================= test session starts =============================
platform win32 -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\Admin\Documents\GitHub\rag-core\.venv\Scripts\python.exe
cachedir: .local\t13-cache-final-dod1
rootdir: C:\Users\Admin\Documents\GitHub\rag-core
configfile: pyproject.toml
plugins: anyio-4.15.1, asyncio-1.4.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 19 items

tests/integration/test_text_parsers.py::test_pdf_physical_pages_unicode_and_table_source PASS real Docling PDF: 2 physical pages, EN/VI, table headers/units, native offsets/bbox, printed i/ii
PASSED
tests/integration/test_text_parsers.py::test_docx_paragraph_table_heading_headers_and_no_fake_pages PASS real python-docx: page break, EN/VI paragraphs, table/unit, heading path, header/footer XML round-trip; no page
PASSED
tests/integration/test_text_parsers.py::test_unicode_text_line_and_source_offset_round_trip[txt] PASS real txt: exact UTF-8/BOM/CRLF Unicode offsets and one-based lines, EN/VI
PASSED
tests/integration/test_text_parsers.py::test_unicode_text_line_and_source_offset_round_trip[md] PASS real md: exact UTF-8/BOM/CRLF Unicode offsets and one-based lines, EN/VI
PASSED
tests/integration/test_text_parsers.py::test_html_heading_table_entities_and_raw_source_spans PASS real HTML parser: EN/VI, entities, headings, table/unit and original HTML spans
PASSED
tests/integration/test_text_parsers.py::test_corrupt_files_are_errors[pdf] PASSED
tests/integration/test_text_parsers.py::test_corrupt_files_are_errors[docx] PASSED
tests/integration/test_text_parsers.py::test_real_encrypted_pdf_is_error PASS real corrupt PDF/DOCX and AES-256 encrypted PDF: safe explicit errors; sources unchanged, temp empty
PASSED
tests/integration/test_text_parsers.py::test_safety_mime_size_hash_output_and_page_limits PASS MIME signature/type/extension, byte/page/block/text/result limits, SHA mismatch, cleanup
PASSED
tests/integration/test_text_parsers.py::test_safety_timeout_kills_real_parser_and_cleans_temp PASS real subprocess deadline: killed/reaped, sandbox removed, subsequent real parse succeeds
PASSED
tests/integration/test_text_parsers.py::test_safety_html_never_executes_or_fetches_external_refs PASS actual HTTP canary: zero requests from script/style/image/iframe/link/event refs; hidden text excluded
PASSED
tests/integration/test_text_parsers.py::test_safety_docx_archive_limits_traversal_macros_entities PASS real ZIP preflight: entry/expanded/ratio limits, traversal, VBA, XML entity rejected without extraction
PASSED
tests/integration/test_text_parsers.py::test_safety_empty_and_mixed_pdf_require_explicit_ocr PASS empty extraction errors; native PDF missing text -> OCR required/partial page 2, no scan verification claimed
PASSED
tests/integration/test_text_parsers.py::test_safety_docx_external_relationships_are_data_only PASSED
tests/integration/test_text_parsers.py::test_markdown_code_and_table_are_preserved_as_source_data PASSED
tests/integration/test_text_parsers.py::test_markdown_setext_and_fenced_delimiters_keep_heading_context PASSED
tests/integration/test_text_parsers.py::test_safety_actual_format_encoding_and_docx_package_validation PASSED
tests/integration/test_text_parsers.py::test_docx_nested_table_and_blank_paragraph_source_paths PASSED
tests/integration/test_text_parsers.py::test_safety_registry_bounds_concurrent_real_execution PASSED

============================= 19 passed in 14.52s =============================
```

### DoD-2 — Bounds, cleanup and inert external content

Cwd repository root; host/config below; exit **0**.

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv run --no-sync pytest tests/integration/test_text_parsers.py -k safety -v -s --tb=short --basetemp=.local/t13-final-dod2 -o cache_dir=.local/t13-cache-final-dod2
```

```text
============================= test session starts =============================
platform win32 -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\Admin\Documents\GitHub\rag-core\.venv\Scripts\python.exe
cachedir: .local\t13-cache-final-dod2
rootdir: C:\Users\Admin\Documents\GitHub\rag-core
configfile: pyproject.toml
plugins: anyio-4.15.1, asyncio-1.4.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 19 items / 11 deselected / 8 selected

tests/integration/test_text_parsers.py::test_safety_mime_size_hash_output_and_page_limits PASS MIME signature/type/extension, byte/page/block/text/result limits, SHA mismatch, cleanup
PASSED
tests/integration/test_text_parsers.py::test_safety_timeout_kills_real_parser_and_cleans_temp PASS real subprocess deadline: killed/reaped, sandbox removed, subsequent real parse succeeds
PASSED
tests/integration/test_text_parsers.py::test_safety_html_never_executes_or_fetches_external_refs PASS actual HTTP canary: zero requests from script/style/image/iframe/link/event refs; hidden text excluded
PASSED
tests/integration/test_text_parsers.py::test_safety_docx_archive_limits_traversal_macros_entities PASS real ZIP preflight: entry/expanded/ratio limits, traversal, VBA, XML entity rejected without extraction
PASSED
tests/integration/test_text_parsers.py::test_safety_empty_and_mixed_pdf_require_explicit_ocr PASS empty extraction errors; native PDF missing text -> OCR required/partial page 2, no scan verification claimed
PASSED
tests/integration/test_text_parsers.py::test_safety_docx_external_relationships_are_data_only PASSED
tests/integration/test_text_parsers.py::test_safety_actual_format_encoding_and_docx_package_validation PASSED
tests/integration/test_text_parsers.py::test_safety_registry_bounds_concurrent_real_execution PASSED

====================== 8 passed, 11 deselected in 9.00s =======================
```

### D2 — Locked offline environment

Cwd repository root; host/config below; exit **0**.

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv sync --locked --offline --group dev --group api --group ingestion; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; uv lock --check --offline
```

```text
Resolved 101 packages in 1ms
   Building rag-core @ file:///C:/Users/Admin/Documents/GitHub/rag-core
      Built rag-core @ file:///C:/Users/Admin/Documents/GitHub/rag-core
Prepared 1 package in 629ms
Uninstalled 1 package in 1ms
Installed 1 package in 8ms
 ~ rag-core==0.1.0 (from file:///C:/Users/Admin/Documents/GitHub/rag-core)
Resolved 101 packages in 1ms
```

### D2 — Ruff and strict mypy

Cwd repository root; host/config below; exit **0**.

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv run --no-sync ruff check .; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; uv run --no-sync mypy src
```

```text
warning: Encountered error: Access is denied. (os error 5)
warning: Encountered error: Access is denied. (os error 5)
warning: Encountered error: Access is denied. (os error 5)
All checks passed!
Success: no issues found in 38 source files
```

### D2 — Unit/contract/security regression

Cwd repository root; host/config below; exit **0**.

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv run --no-sync pytest -q tests/unit tests/contract tests/security --tb=short --basetemp=.t13r -o cache_dir=.local/t13-cache-regression
```

```text
........................................................................ [ 22%]
........................................................................ [ 44%]
........................................................................ [ 66%]
........................................................................ [ 88%]
.....................................                                    [100%]
325 passed in 100.64s (0:01:40)
```

### D4 — Unchanged API export

Cwd repository root; host/config below; exit **0**.

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv run --no-sync python scripts/export_openapi.py --check
```

```text
PASS checked docs/api/openapi-v1.designed.json
PASS checked docs/api/openapi.served.json
PASS checked docs/api/examples-v1.json
PASS designed_operations=13 served_health_routes=2 synthetic_examples=37
PASS OpenAPI model + Draft2020-12 schemas=48; examples JSON Schema + Pydantic
CONTRACT EXPORT: PASS (business endpoints unmounted; no runtime query/stream verification)
```

### D1–D6 completion review

- **D1:** dependencies/P01/baseline/task scope reviewed; `git diff --check` exit0/no output. T13-only code/tests/dependency/docs; original prompt/corpus/auth/session/storage/job/retrieval semantics unchanged. Historical scratch retained.
- **D2:** checks above plus final Ruff/mypy after review fix below. Regression325 includes T09 real loopback security/HTTP; no PG/MinIO/Redis rerun claimed because adapters unchanged.
- **D3:** each DoD separately executed above on actual parsers, no mock substitute; T13 has no external-provider/service credential gate.
- **D4:** README/RUNBOOK status/format matrix/operator limits/errors/offset contract/install/tests/unverified OCR/worker boundaries, task notes/handoff/phase summary updated; final docs check follows.
- **D5:** intermediate schema1 is new, no DB/index/API migration; T03 locators/OpenAPI unchanged. No source execution/network, credentials/corpus/weights/cache/scratch staged. Native PDF retains table textline/header/unit/geometry, does not infer semantic cell structure. No general layout/corpus RAM/latency/Docker worker/OCR claim.
- **D6:** completion subject `feat(T13): parse text documents with source provenance`; COMPLETE effective only after successful inspected scoped14-file commit. User authorizes origin/main push; actual hash/remote equality returned post-commit, never embedded into its own commit. T14 depends only on T13 and ready after closure; **STOP AFTER T13**.

Final lint/type verification after Markdown review (cwd above):

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv run --no-sync ruff format src/rag_core/adapters/parsers/worker.py tests/integration/test_text_parsers.py; uv run --no-sync ruff check .; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; uv run --no-sync mypy src
```

Exit0, actual `1 file reformatted, 1 file left unchanged`, inherited three Access-denied scratch warnings, `All checks passed!`, `Success: no issues found in 38 source files`. Final DoD1/2 commands above were repeated after that source change.

Regression used short `.t13r` to avoid known Windows corpus path limit; not ignored. After PASS only this self-created directory was removed with checked absolute target:

```powershell
$taskWorkspace = [IO.Path]::GetFullPath((Get-Location).Path); $taskScratch = [IO.Path]::GetFullPath((Join-Path $taskWorkspace '.t13r')); if ($taskScratch -ne (Join-Path $taskWorkspace '.t13r') -or -not $taskScratch.StartsWith($taskWorkspace + '\')) { throw 'Scratch outside workspace' }; Remove-Item -LiteralPath $taskScratch -Recurse -Force; Write-Output 'Removed only own verified .t13r test temp'; git diff --check
```

Exit0, `Removed only own verified .t13r test temp`; whitespace output empty. Historical T07 scratch untouched.

### Final D1/D4/D5/D6 closure

Review found that defusedxml's default allows entity-free DTDs; set explicit forbid_dtd/forbid_entities/forbid_external and added a standalone external-DTD fixture to existing ZIP safety test. No source/QA/gate altered. Final code after this fix:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv run --no-sync ruff format src/rag_core/adapters/parsers/worker.py tests/integration/test_text_parsers.py; uv run --no-sync ruff check .; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; uv run --no-sync mypy src
```

Exit0; actual `1 file reformatted, 1 file left unchanged`, three inherited scratch Access-denied warnings, `All checks passed!`, `Success: no issues found in 38 source files`.

Separate final DoD-1/2 invocations on that reviewed code, cwd/config as above, both exit0:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv run --no-sync pytest tests/integration/test_text_parsers.py -v -s --tb=short --basetemp=.local/t13-reviewed-dod1 -o cache_dir=.local/t13-cache-reviewed-dod1
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv run --no-sync pytest tests/integration/test_text_parsers.py -k safety -v -s --tb=short --basetemp=.local/t13-reviewed-dod2 -o cache_dir=.local/t13-cache-reviewed-dod2
```

Actual excerpts (full successful test diagnostics equal preceding runs):

```text
============================= 19 passed in 14.31s =============================
collecting ... collected 19 items / 11 deselected / 8 selected
PASS real ZIP preflight: entry/expanded/ratio limits, traversal, VBA, XML entity rejected without extraction
PASS actual HTTP canary: zero requests from script/style/image/iframe/link/event refs; hidden text excluded
====================== 8 passed, 11 deselected in 9.11s =======================
```

**D1/D5 dependency/scope review** command, exit0:

```powershell
$taskReview = @'
import pathlib, subprocess, tomllib
prior = tomllib.loads(subprocess.check_output(['git', 'show', 'HEAD:uv.lock'], text=True, encoding='utf-8'))
current = tomllib.loads(pathlib.Path('uv.lock').read_text(encoding='utf-8'))
old = {p['name']: p for p in prior['package']}
new = {p['name']: p for p in current['package']}
assert all(new[name]['version'] == item['version'] for name, item in old.items())
assert old['rag-core']['dev-dependencies']['api'] == new['rag-core']['dev-dependencies']['api']
assert not {'torch', 'transformers', 'docling-ibm-models'} & new.keys()
print(f'PASS prior {len(old)} package pins unchanged; {len(new)-len(old)} added parser dependencies; API group unchanged; no model runtime')
paths = ['README.md', 'RUNBOOK.md', 'docs/tasks.md', 'docs/handoffs.md', 'docs/implementation-summary.md', 'pyproject.toml', 'uv.lock', 'src/rag_core/domain/documents.py', 'src/rag_core/ports/parsers.py', 'src/rag_core/adapters/parsers/__init__.py', 'src/rag_core/adapters/parsers/registry.py', 'src/rag_core/adapters/parsers/text.py', 'src/rag_core/adapters/parsers/worker.py', 'tests/integration/test_text_parsers.py']
for name in paths:
    raw = pathlib.Path(name).read_bytes()
    raw.decode('utf-8')
    assert len(raw) < 1024*1024, name
tracked = subprocess.check_output(['git', 'diff', '--name-only'], text=True).splitlines()
assert set(tracked) <= set(paths), tracked
assert not subprocess.check_output(['git', 'diff', '--', 'corpus-documents'], text=True)
print('PASS exact14 candidate UTF-8/size/scope; prompt/corpus untouched; no raw binaries/credentials/cache/weights in candidate paths')
'@
$taskReview | .venv/Scripts/python.exe -
git diff --check
```

```text
PASS prior 83 package pins unchanged; 18 added parser dependencies; API group unchanged; no model runtime
PASS exact14 candidate UTF-8/size/scope; prompt/corpus untouched; no raw binaries/credentials/cache/weights in candidate paths
```

**D4 actual documentation check:** command `$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv run --no-sync python scripts/check_docs.py; git diff --check`, cwd above, exit0:

```text
PASS UTF-8/nonempty Markdown: 14 files
PASS internal links/anchors: 285
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```

**D6 explicit stage**, approved Git write, cwd above, exit0/no stdout:

```powershell
git add -- README.md RUNBOOK.md docs/tasks.md docs/handoffs.md docs/implementation-summary.md pyproject.toml uv.lock src/rag_core/domain/documents.py src/rag_core/ports/parsers.py src/rag_core/adapters/parsers/__init__.py src/rag_core/adapters/parsers/registry.py src/rag_core/adapters/parsers/text.py src/rag_core/adapters/parsers/worker.py tests/integration/test_text_parsers.py
```

**D5/D6 cached review and secrets check**, exit0 (actual local values compared in memory only):

```powershell
git diff --cached --check; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; git diff --cached --name-only; git diff --cached --stat; $taskStagedPatch = git diff --cached; foreach ($taskSecretName in @('postgres_password','minio_root_password','t10_postgres_password','minio_reader_password','minio_uploader_password')) { $taskSecretPath = Join-Path '.local/secrets' $taskSecretName; if (Test-Path -LiteralPath $taskSecretPath) { $taskSecretValue = [IO.File]::ReadAllText((Join-Path (Get-Location) $taskSecretPath)).Trim(); if ($taskSecretValue.Length -gt 0 -and ($taskStagedPatch -join "`n").Contains($taskSecretValue)) { throw 'Local secret matched staged diff' } } }; $taskAddedLines = ($taskStagedPatch | Where-Object { $_.StartsWith('+') -and -not $_.StartsWith('+++') }) -join "`n"; if ($taskAddedLines -match '-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----|eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.') { throw 'Credential material matched new staged lines' }; Write-Output 'PASS staged exact task files; compared local secret values absent; no private keys/JWT literals in new lines'
```

```text
warning: unable to access 'C:\Users\Admin/.config/git/ignore': Permission denied
warning: unable to access 'C:\Users\Admin/.config/git/ignore': Permission denied
README.md
RUNBOOK.md
docs/handoffs.md
docs/implementation-summary.md
docs/tasks.md
pyproject.toml
src/rag_core/adapters/parsers/__init__.py
src/rag_core/adapters/parsers/registry.py
src/rag_core/adapters/parsers/text.py
src/rag_core/adapters/parsers/worker.py
src/rag_core/domain/documents.py
src/rag_core/ports/parsers.py
tests/integration/test_text_parsers.py
uv.lock
warning: unable to access 'C:\Users\Admin/.config/git/ignore': Permission denied
 README.md                                 |  31 +-
 RUNBOOK.md                                |  89 +++++-
 docs/handoffs.md                          | 232 ++++++++++++++
 docs/implementation-summary.md            |  12 +
 docs/tasks.md                             |   6 +-
 pyproject.toml                            |   4 +
 src/rag_core/adapters/parsers/__init__.py |   5 +
 src/rag_core/adapters/parsers/registry.py | 124 ++++++++
 src/rag_core/adapters/parsers/text.py     | 253 +++++++++++++++
 src/rag_core/adapters/parsers/worker.py   | 331 +++++++++++++++++++
 src/rag_core/domain/documents.py          |  82 +++++
 src/rag_core/ports/parsers.py             |  12 +
 tests/integration/test_text_parsers.py    | 508 ++++++++++++++++++++++++++++++
 uv.lock                                   | 298 ++++++++++++++++++
 14 files changed, 1971 insertions(+), 16 deletions(-)
warning: unable to access 'C:\Users\Admin/.config/git/ignore': Permission denied
PASS staged exact task files; compared local secret values absent; no private keys/JWT literals in new lines
```

D1–D5 PASS. D6 scope/cached review PASS; final docs restage, cached/docs validation and commit are last atomic completion steps. COMPLETE field is effective only with successful inspected completion commit; resolve actual hash via `git log -1 --format=%H --grep="^feat(T13):"`. Actual commit and remote equality reported post-push. No unresolved T13 blocker; T14 ready after closure; stop here.


<a id="h-t14-a01"></a>
## H-T14-A01 — Phase 3 / XLSX, CSV, PPTX và bảng, 2026-10-01

**Runtime/baseline/scope:** direct Codex agent, exact model/effort not exposed, no subagents.
Cwd for all commands below `C:\Users\Admin\Documents\GitHub\rag-core`, PowerShell,
Windows/Python3.12.4/pytest9.1.1/uv0.11.16; `UV_CACHE_DIR=<repo>\.uv-cache`.
No services/provider/model/OCR/weights required, only synthetic Office/CSV fixtures.
T13 COMPLETE and its notes/evidence/summary, AGENTS/task-session-prompt, P01/P02/P06/P07/P13,
living docs/current checkpoint read before code. No unfinished T14 work existed.
User explicitly authorizes scoped commit/push origin/current branch, no force/merge/deploy.

Baseline command `git status --short; git branch --show-current; git rev-parse HEAD;
git remote -v; rg --files -g AGENTS.md -g task-session-prompt.md -g tasks.md -g plan.md
-g handoffs.md -g implementation-summary.md -g README.md -g RUNBOOK.md` overall exit1
because rg hit inherited inaccessible scratch. Git baseline output:

```text
?? .ptmp-t07-a02/
?? .tmp-t07-a02/
main
d3e57b29de892ff360e2e255e9d1680bf179faaf
origin https://github.com/admininistrator/rag-core.git (fetch)
origin https://github.com/admininistrator/rag-core.git (push)
```

Inherited scratch/global Git-ignore ACL warnings unchanged, no files touched there.
`git log -1 --format='%H%n%s'` exit0: same hash / `feat(T13): parse text documents with source provenance`.
`git ls-remote origin refs/heads/main` sandbox exit128:
`fatal: unable to access 'https://github.com/admininistrator/rag-core.git/': Failed to connect to github.com port 443 after 22 ms: Could not connect to server`.
Authorized network escalation of same command exit0:

```text
d3e57b29de892ff360e2e255e9d1680bf179faaf refs/heads/main
```

`git var GIT_AUTHOR_IDENT | Out-Null; if ($LASTEXITCODE -eq 0) { Write-Output 'Git author configured' }`
exit0, actual `Git author configured`; identity neither printed nor changed.

**Implementation/official APIs:** [openpyxl load_workbook](https://openpyxl.readthedocs.io/en/stable/api/openpyxl.reader.excel.html)
data_only controls formula vs stored cache; keep_vba/keep_links disabled, no recalculation.
[python-pptx shapes](https://python-pptx.readthedocs.io/en/latest/api/shapes.html) supplies text,
tables/groups/z-order, never Office execution. Release artifacts verified on official PyPI
[openpyxl3.1.5](https://pypi.org/project/openpyxl/3.1.5/) / [python-pptx1.0.2](https://pypi.org/project/python-pptx/1.0.2/).
Interfaces/policies/files/revisions in [S-T14-A01](implementation-summary.md#s-t14-a01).
Allowed exact15 files: README/RUNBOOK, tasks/handoffs/implementation-summary,
pyproject/uv.lock, domain/documents, parser registry/worker/text/archive/office/tables,
real integration test_office_tables. No API/DB/index/corpus/session semantics change.

Dependency command, authorized network escalation, exit0:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv add --group ingestion 'openpyxl==3.1.5' 'python-pptx==1.0.2' --no-sync; if ($LASTEXITCODE -eq 0) { uv sync --locked --group dev --group api --group ingestion }
```

Actual excerpt (upstream invalid version normalization WARNs retained in tool output):

```text
Resolved 105 packages in 1.28s
Resolved 105 packages in 1ms
Prepared 5 packages in 1.75s
Uninstalled 1 package in 7ms
Installed 5 packages in 145ms
+ et-xmlfile==2.0.0
+ openpyxl==3.1.5
+ python-pptx==1.0.2
~ rag-core==0.1.0 (from file:///C:/Users/Admin/Documents/GitHub/rag-core)
+ xlsxwriter==3.2.9
```

**Diagnostics/fixes retained, no lowered gate:** initial integration collection exit1
`ModuleNotFoundError: No module named 'tests'` from cross-test helper import; replaced
with local real registry/source-hash/cleanup helper. Initial Ruff RUF001 dash/import
and later UP012 encode argument fixed. Second run exit1 `1 failed, 18 passed in14.69s`:
XPath lacked namespace mapping; namespace provided. Third combined run exit1
`1 failed, 37 passed in32.64s`: python-pptx custom XML text properties repeated itertext;
independent XML-from-original-package resolver used instead; exact source text assert
unchanged, focused real PPTX run1PASS. Review made group blocks unique, retained
numeric year headers/full merged bounds/blank regions, pre-load combined area limits,
and actual hyperlink/WEBSERVICE execution canaries. Three focused review tests PASS.
First DoD invocation in `.local/t14-dod1.log` exit1 `1 failed, 21 passed in15.67s`:
Windows fixture write_text inserted CRLF, parser correctly preserved it; fixture now
writes exact intended LF bytes. CSV field-size error maps to extraction_limit; focused
single-column/empty/budget test1PASS. Context-mismatched apply_patch calls made no
changes and were corrected after reading actual formatted lines. Final full gates below.

### DoD-1 — Actual Office/CSV parsing and source round-trip

Expected multi-sheet/merged/numeric headers/units/formula-cache distinction, PPTX slides,
CSV quoting/delimiters/Unicode, source cell/slide/logical record round-trip; actual22PASS,
no skips. Original source bytes unchanged and private parser sandbox empty asserted on
every parse, including errors. Full synthetic-only log `.local/t14-dod1-final.log`.
Exit **0**, exact command:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv run --no-sync pytest tests/integration/test_office_tables.py -v -s --tb=short --basetemp=.local/t14-accept-dod1 -o cache_dir=.local/t14-cache-accept-dod1 2>&1 | Tee-Object -FilePath .local/t14-dod1-final.log; exit $LASTEXITCODE
```

```text
============================= test session starts =============================
platform win32 -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\Admin\Documents\GitHub\rag-core\.venv\Scripts\python.exe
cachedir: .local\t14-cache-accept-dod1
rootdir: C:\Users\Admin\Documents\GitHub\rag-core
configfile: pyproject.toml
plugins: anyio-4.15.1, asyncio-1.4.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 22 items

tests/integration/test_office_tables.py::test_xlsx_multisheet_merged_headers_units_and_cell_round_trip PASS actual XLSX: 2 sheets, merged A1:C1, headers/units/percent format, every cell/range round-trip; no PDF page
PASSED
tests/integration/test_office_tables.py::test_xlsx_formula_cache_policy_never_recalculates PASS formula policy: stored cache240 retained, missing cache not inferred as0.5; formulas separate and inert
PASSED
tests/integration/test_office_tables.py::test_xlsx_numeric_headers_merged_extent_blank_regions_and_false_dimension PASS numeric year headers/units, full merged extent, blank-region reset; forged dimension ignored
PASSED
tests/integration/test_office_tables.py::test_common_table_normalization_preserves_empty_cells_multiline_headers_units PASS shared DOCX/HTML/MD table rows/header/units/empty cells; CSV HTML/formula-looking fields remain inert data
PASSED
tests/integration/test_office_tables.py::test_csv_unicode_quoting_multiline_delimiters_record_round_trip[,] PASS actual CSV delimiter',': Unicode/BOM/CRLF/escaped quotes/multiline; logical records1-3, formula text unchanged
PASSED
tests/integration/test_office_tables.py::test_csv_unicode_quoting_multiline_delimiters_record_round_trip[;] PASS actual CSV delimiter';': Unicode/BOM/CRLF/escaped quotes/multiline; logical records1-3, formula text unchanged
PASSED
tests/integration/test_office_tables.py::test_csv_unicode_quoting_multiline_delimiters_record_round_trip[\t] PASS actual CSV delimiter'\t': Unicode/BOM/CRLF/escaped quotes/multiline; logical records1-3, formula text unchanged
PASSED
tests/integration/test_office_tables.py::test_csv_unicode_quoting_multiline_delimiters_record_round_trip[|] PASS actual CSV delimiter'|': Unicode/BOM/CRLF/escaped quotes/multiline; logical records1-3, formula text unchanged
PASSED
tests/integration/test_office_tables.py::test_pptx_multislide_table_group_xml_locator_round_trip PASS actual PPTX: slides1/2, blank paragraph indices, tables/units, group paths and original XML round-trip
PASSED
tests/integration/test_office_tables.py::test_csv_invalid_encoding_shape_or_quotes_are_explicit_errors[a,b\n1,2,3\n] PASSED
tests/integration/test_office_tables.py::test_csv_invalid_encoding_shape_or_quotes_are_explicit_errors[a,b\n1,"unterminated] PASSED
tests/integration/test_office_tables.py::test_csv_invalid_encoding_shape_or_quotes_are_explicit_errors[\xff\xfe\x00] PASSED
tests/integration/test_office_tables.py::test_csv_invalid_encoding_shape_or_quotes_are_explicit_errors[a,b\n\n] PASSED
tests/integration/test_office_tables.py::test_safety_office_archive_bombs_macros_traversal_entities[xlsx] PASS xlsx actual ZIP entry/expanded/ratio bombs, traversal, VBA and XML entities refused; no extraction, source preserved
PASSED
tests/integration/test_office_tables.py::test_safety_office_archive_bombs_macros_traversal_entities[pptx] PASS pptx actual ZIP entry/expanded/ratio bombs, traversal, VBA and XML entities refused; no extraction, source preserved
PASSED
tests/integration/test_office_tables.py::test_safety_external_relationships_never_fetch_or_execute[xlsx] PASS xlsx actual loopback HTTP execution canary:0 requests; external relations inert
PASSED
tests/integration/test_office_tables.py::test_safety_external_relationships_never_fetch_or_execute[pptx] PASS pptx actual loopback HTTP execution canary:0 requests; external relations inert
PASSED
tests/integration/test_office_tables.py::test_safety_csv_single_column_empty_and_cell_text_limits PASSED
tests/integration/test_office_tables.py::test_safety_xlsx_sparse_dimension_merged_and_cell_sheet_budgets PASS XLSX pre-load sparse/merge area and sheet/cell budgets; huge merge never materialized
PASSED
tests/integration/test_office_tables.py::test_safety_pptx_slide_table_and_result_budgets PASSED
tests/integration/test_office_tables.py::test_safety_office_mime_package_corrupt_encrypted_and_legacy[xlsx] PASSED
tests/integration/test_office_tables.py::test_safety_office_mime_package_corrupt_encrypted_and_legacy[pptx] PASSED

============================= 22 passed in 15.43s =============================
```

### DoD-2 — Archives/macros/links inert, legacy/chart limits documented

Expected unsafe Office packages refused, no external/formula/macro execution and honest
format limits in README/RUNBOOK. Actual9PASS in separate safety run,0loopback requests
from real hyperlink refs/WEBSERVICE formula; VBA/entity/bomb rejected before backend,
no package extraction. `.doc/.xls/.ppt` unsupported, charts/images not promised; format
matrix/policy checked in both docs. Full log `.local/t14-dod2-final.log`, exit **0**:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv run --no-sync pytest tests/integration/test_office_tables.py -k safety -v -s --tb=short --basetemp=.local/t14-accept-dod2 -o cache_dir=.local/t14-cache-accept-dod2 2>&1 | Tee-Object -FilePath .local/t14-dod2-final.log; exit $LASTEXITCODE
```

```text
============================= test session starts =============================
platform win32 -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\Admin\Documents\GitHub\rag-core\.venv\Scripts\python.exe
cachedir: .local\t14-cache-accept-dod2
rootdir: C:\Users\Admin\Documents\GitHub\rag-core
configfile: pyproject.toml
plugins: anyio-4.15.1, asyncio-1.4.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 22 items / 13 deselected / 9 selected

tests/integration/test_office_tables.py::test_safety_office_archive_bombs_macros_traversal_entities[xlsx] PASS xlsx actual ZIP entry/expanded/ratio bombs, traversal, VBA and XML entities refused; no extraction, source preserved
PASSED
tests/integration/test_office_tables.py::test_safety_office_archive_bombs_macros_traversal_entities[pptx] PASS pptx actual ZIP entry/expanded/ratio bombs, traversal, VBA and XML entities refused; no extraction, source preserved
PASSED
tests/integration/test_office_tables.py::test_safety_external_relationships_never_fetch_or_execute[xlsx] PASS xlsx actual loopback HTTP execution canary:0 requests; external relations inert
PASSED
tests/integration/test_office_tables.py::test_safety_external_relationships_never_fetch_or_execute[pptx] PASS pptx actual loopback HTTP execution canary:0 requests; external relations inert
PASSED
tests/integration/test_office_tables.py::test_safety_csv_single_column_empty_and_cell_text_limits PASSED
tests/integration/test_office_tables.py::test_safety_xlsx_sparse_dimension_merged_and_cell_sheet_budgets PASS XLSX pre-load sparse/merge area and sheet/cell budgets; huge merge never materialized
PASSED
tests/integration/test_office_tables.py::test_safety_pptx_slide_table_and_result_budgets PASSED
tests/integration/test_office_tables.py::test_safety_office_mime_package_corrupt_encrypted_and_legacy[xlsx] PASSED
tests/integration/test_office_tables.py::test_safety_office_mime_package_corrupt_encrypted_and_legacy[pptx] PASSED

====================== 9 passed, 13 deselected in 10.42s ======================
```

### D2 — Quality, regression, reproducible dependencies and contracts

Regression on current T14 source, expected T13 native text/parser safety and full
unit/contract/security remain correct. Actual344PASS (325 prior suite+19T13), no skips,
exit **0**, `.local/t14-regression.log`:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv run --no-sync pytest tests/unit tests/contract tests/security tests/integration/test_text_parsers.py -q --tb=short --basetemp=.local/t14-reg -o cache_dir=.local/t14-cache-reg 2>&1 | Tee-Object -FilePath .local/t14-regression.log; exit $LASTEXITCODE
```

```text
........................................................................ [ 20%]
........................................................................ [ 41%]
........................................................................ [ 62%]
........................................................................ [ 83%]
........................................................                 [100%]
344 passed in 118.27s (0:01:58)
```

Final quality command, exit0:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv run --no-sync ruff check .; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; uv run --no-sync mypy src; git diff --check; git diff --exit-code -- corpus-documents docs/api; git status --short
```

Actual quality excerpt:

```text
warning: Encountered error: Access is denied. (os error 5)
warning: Encountered error: Access is denied. (os error 5)
warning: Encountered error: Access is denied. (os error 5)
All checks passed!
Success: no issues found in 41 source files
```

Three warnings refer to inherited scratch; all changed files checked. Git diff checks
no stdout, no corpus/prompt/API snapshot edits; status only allowed candidate + two
baseline T07 scratch directories. No scope loosening or storage operations introduced.

Locked offline sync/OpenAPI check command, exit0:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv sync --offline --locked --group dev --group api --group ingestion; uv run --no-sync python scripts/export_openapi.py --check; git var GIT_AUTHOR_IDENT | Out-Null; if ($LASTEXITCODE -eq 0) { Write-Output 'Git author configured' }
```

```text
Resolved 105 packages in 34ms
Checked 104 packages in 14ms
PASS checked docs/api/openapi-v1.designed.json
PASS checked docs/api/openapi.served.json
PASS checked docs/api/examples-v1.json
PASS designed_operations=13 served_health_routes=2 synthetic_examples=37
PASS OpenAPI model + Draft2020-12 schemas=48; examples JSON Schema + Pydantic
CONTRACT EXPORT: PASS (business endpoints unmounted; no runtime query/stream verification)
Git author configured
```

### D1/D5 — Scope, source and dependency review

Read/reviewed all new/modified source/tests/lock/docs. Read-only inline Python review
(`$reviewScript | .venv/Scripts/python.exe -`, script shown below) exit0, expected no
old lock upgrades or dependency spill, actual:

```text
PASS existing lock versions unchanged; 4 Office packages added; other dependency groups unchanged
PASS corpus/prompt and API snapshots unchanged; no schema/DB/index migration
```

```python
import subprocess,tomllib
from pathlib import Path
old=tomllib.loads(subprocess.check_output(['git','show','HEAD:uv.lock'],text=True,encoding='utf-8'))
new=tomllib.loads(Path('uv.lock').read_text(encoding='utf-8'))
before={p['name']:p['version'] for p in old['package']}
after={p['name']:p['version'] for p in new['package']}
assert all(after[k]==v for k,v in before.items())
assert set(after)-set(before)=={'openpyxl','python-pptx','et-xmlfile','xlsxwriter'}
assert subprocess.run(['git','diff','--exit-code','--','corpus-documents','docs/api']).returncode==0
cfg=tomllib.loads(Path('pyproject.toml').read_text(encoding='utf-8'))
prior=tomllib.loads(subprocess.check_output(['git','show','HEAD:pyproject.toml'],text=True,encoding='utf-8'))
for name in cfg['dependency-groups']:
 if name!='ingestion': assert cfg['dependency-groups'][name]==prior['dependency-groups'][name]
print('PASS existing lock versions unchanged; 4 Office packages added; other dependency groups unchanged')
print('PASS corpus/prompt and API snapshots unchanged; no schema/DB/index migration')
```

Source schema1 fields additive with defaults, parser revisions updated where table
metadata changed; future T16/T19 fingerprint obligation documented, no migration needed
before those tasks exist. Existing T03 locators and page policy reused, session/auth/
retention/storage contracts untouched. Only generated synthetic fixtures in ignored
`.local`, no raw corpus/weights/.env/cache/logs/source binaries included in completion.
README/RUNBOOK both explain working commands, source context convention, missing/stale
formula cache, numeric formats, UTF-8/CSV record semantics, PPTX groups and bounds;
no worker/index/OCR/chart/legacy support claimed.

### D4/D6 — Closure boundary

README/RUNBOOK + tasks/handoffs/summary updated; final docs check, exact scope/secrets
scan/stage evidence appended below. Completion subject/Task-ID
`feat(T14): preserve spreadsheet and table evidence`; actual hash, inspected commit
and origin/main equality returned after execution, never self-reference/amend.
COMPLETE only after all gates and successful inspected commit; failed commit/push must
report actual error/checkpoint. T15 depends on T14/T13, ready after successful closure;
stop T14, no T15 code/worker/OCR/deployment/Scarlet changes.


### Final review correction and separate DoD reruns

Final source review found two T14-only edge cases: all-empty single-column CSV header
was valid context followed by actual data but Pydantic rejected its empty text;
merged formula header must reuse normalized cache/missing value, not expression text.
Preserved raw rows/formula metadata, explicit empty-field marker and all-empty-file
`empty_extraction`; normalized anchor value now supplies merged context. Added one
real regression test (23total). Shared T13 parser/worker/domain/contract regression
paths unchanged by this Office-only fix, so344PASS evidence above still applies;
final T14 DoD reruns and Ruff/mypy below cover final changed paths. No tests/gold/gates
removed. Focused `-k empty_csv_header` exit0 `1 passed, 22 deselected in1.78s`.

Final DoD-1, exit0, `.local/t14-dod1-close.log`:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv run --no-sync pytest tests/integration/test_office_tables.py -v -s --tb=short --basetemp=.local/t14-close-dod1 -o cache_dir=.local/t14-cache-close-dod1 2>&1 | Tee-Object -FilePath .local/t14-dod1-close.log; exit $LASTEXITCODE
```

```text
============================= test session starts =============================
platform win32 -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\Admin\Documents\GitHub\rag-core\.venv\Scripts\python.exe
cachedir: .local\t14-cache-close-dod1
rootdir: C:\Users\Admin\Documents\GitHub\rag-core
configfile: pyproject.toml
plugins: anyio-4.15.1, asyncio-1.4.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 23 items

tests/integration/test_office_tables.py::test_xlsx_multisheet_merged_headers_units_and_cell_round_trip PASS actual XLSX: 2 sheets, merged A1:C1, headers/units/percent format, every cell/range round-trip; no PDF page
PASSED
tests/integration/test_office_tables.py::test_xlsx_formula_cache_policy_never_recalculates PASS formula policy: stored cache240 retained, missing cache not inferred as0.5; formulas separate and inert
PASSED
tests/integration/test_office_tables.py::test_xlsx_numeric_headers_merged_extent_blank_regions_and_false_dimension PASS numeric year headers/units, full merged extent, blank-region reset; forged dimension ignored
PASSED
tests/integration/test_office_tables.py::test_common_table_normalization_preserves_empty_cells_multiline_headers_units PASS shared DOCX/HTML/MD table rows/header/units/empty cells; CSV HTML/formula-looking fields remain inert data
PASSED
tests/integration/test_office_tables.py::test_csv_unicode_quoting_multiline_delimiters_record_round_trip[,] PASS actual CSV delimiter',': Unicode/BOM/CRLF/escaped quotes/multiline; logical records1-3, formula text unchanged
PASSED
tests/integration/test_office_tables.py::test_csv_unicode_quoting_multiline_delimiters_record_round_trip[;] PASS actual CSV delimiter';': Unicode/BOM/CRLF/escaped quotes/multiline; logical records1-3, formula text unchanged
PASSED
tests/integration/test_office_tables.py::test_csv_unicode_quoting_multiline_delimiters_record_round_trip[\t] PASS actual CSV delimiter'\t': Unicode/BOM/CRLF/escaped quotes/multiline; logical records1-3, formula text unchanged
PASSED
tests/integration/test_office_tables.py::test_csv_unicode_quoting_multiline_delimiters_record_round_trip[|] PASS actual CSV delimiter'|': Unicode/BOM/CRLF/escaped quotes/multiline; logical records1-3, formula text unchanged
PASSED
tests/integration/test_office_tables.py::test_pptx_multislide_table_group_xml_locator_round_trip PASS actual PPTX: slides1/2, blank paragraph indices, tables/units, group paths and original XML round-trip
PASSED
tests/integration/test_office_tables.py::test_csv_invalid_encoding_shape_or_quotes_are_explicit_errors[a,b\n1,2,3\n] PASSED
tests/integration/test_office_tables.py::test_csv_invalid_encoding_shape_or_quotes_are_explicit_errors[a,b\n1,"unterminated] PASSED
tests/integration/test_office_tables.py::test_csv_invalid_encoding_shape_or_quotes_are_explicit_errors[\xff\xfe\x00] PASSED
tests/integration/test_office_tables.py::test_csv_invalid_encoding_shape_or_quotes_are_explicit_errors[a,b\n\n] PASSED
tests/integration/test_office_tables.py::test_safety_office_archive_bombs_macros_traversal_entities[xlsx] PASS xlsx actual ZIP entry/expanded/ratio bombs, traversal, VBA and XML entities refused; no extraction, source preserved
PASSED
tests/integration/test_office_tables.py::test_safety_office_archive_bombs_macros_traversal_entities[pptx] PASS pptx actual ZIP entry/expanded/ratio bombs, traversal, VBA and XML entities refused; no extraction, source preserved
PASSED
tests/integration/test_office_tables.py::test_safety_external_relationships_never_fetch_or_execute[xlsx] PASS xlsx actual loopback HTTP execution canary:0 requests; external relations inert
PASSED
tests/integration/test_office_tables.py::test_safety_external_relationships_never_fetch_or_execute[pptx] PASS pptx actual loopback HTTP execution canary:0 requests; external relations inert
PASSED
tests/integration/test_office_tables.py::test_safety_csv_single_column_empty_and_cell_text_limits PASSED
tests/integration/test_office_tables.py::test_empty_csv_header_and_merged_formula_header_keep_source_data_distinct PASSED
tests/integration/test_office_tables.py::test_safety_xlsx_sparse_dimension_merged_and_cell_sheet_budgets PASS XLSX pre-load sparse/merge area and sheet/cell budgets; huge merge never materialized
PASSED
tests/integration/test_office_tables.py::test_safety_pptx_slide_table_and_result_budgets PASSED
tests/integration/test_office_tables.py::test_safety_office_mime_package_corrupt_encrypted_and_legacy[xlsx] PASSED
tests/integration/test_office_tables.py::test_safety_office_mime_package_corrupt_encrypted_and_legacy[pptx] PASSED

============================= 23 passed in 16.60s =============================
```

Final separate DoD-2, exit0, `.local/t14-dod2-close.log`:

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv run --no-sync pytest tests/integration/test_office_tables.py -k safety -v -s --tb=short --basetemp=.local/t14-close-dod2 -o cache_dir=.local/t14-cache-close-dod2 2>&1 | Tee-Object -FilePath .local/t14-dod2-close.log; exit $LASTEXITCODE
```

```text
============================= test session starts =============================
platform win32 -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\Admin\Documents\GitHub\rag-core\.venv\Scripts\python.exe
cachedir: .local\t14-cache-close-dod2
rootdir: C:\Users\Admin\Documents\GitHub\rag-core
configfile: pyproject.toml
plugins: anyio-4.15.1, asyncio-1.4.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 23 items / 14 deselected / 9 selected

tests/integration/test_office_tables.py::test_safety_office_archive_bombs_macros_traversal_entities[xlsx] PASS xlsx actual ZIP entry/expanded/ratio bombs, traversal, VBA and XML entities refused; no extraction, source preserved
PASSED
tests/integration/test_office_tables.py::test_safety_office_archive_bombs_macros_traversal_entities[pptx] PASS pptx actual ZIP entry/expanded/ratio bombs, traversal, VBA and XML entities refused; no extraction, source preserved
PASSED
tests/integration/test_office_tables.py::test_safety_external_relationships_never_fetch_or_execute[xlsx] PASS xlsx actual loopback HTTP execution canary:0 requests; external relations inert
PASSED
tests/integration/test_office_tables.py::test_safety_external_relationships_never_fetch_or_execute[pptx] PASS pptx actual loopback HTTP execution canary:0 requests; external relations inert
PASSED
tests/integration/test_office_tables.py::test_safety_csv_single_column_empty_and_cell_text_limits PASSED
tests/integration/test_office_tables.py::test_safety_xlsx_sparse_dimension_merged_and_cell_sheet_budgets PASS XLSX pre-load sparse/merge area and sheet/cell budgets; huge merge never materialized
PASSED
tests/integration/test_office_tables.py::test_safety_pptx_slide_table_and_result_budgets PASSED
tests/integration/test_office_tables.py::test_safety_office_mime_package_corrupt_encrypted_and_legacy[xlsx] PASSED
tests/integration/test_office_tables.py::test_safety_office_mime_package_corrupt_encrypted_and_legacy[pptx] PASSED

====================== 9 passed, 14 deselected in 10.43s ======================
```

Final `uv run --no-sync ruff check .; uv run --no-sync mypy src; git diff --check`,
same UV_CACHE_DIR/cwd, exit0 (after Office edge fix):

```text
warning: Encountered error: Access is denied. (os error 5)
warning: Encountered error: Access is denied. (os error 5)
warning: Encountered error: Access is denied. (os error 5)
All checks passed!
Success: no issues found in 41 source files
```

D4 docs check command `$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'; uv run --no-sync python scripts/check_docs.py; git diff --check`, exit0:

```text
PASS UTF-8/nonempty Markdown: 14 files
PASS internal links/anchors: 291
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```

Read-only scope/secret review `$scopeScript | .venv/Scripts/python.exe -`, exit0,
script enforces exact15 candidate allowlist, unchanged-source/new files within list,
all text/no NUL/<1MiB, high-confidence AWS/Anthropic/GitHub/private-key marker absence
in added diff/new sources (never prints matched values), manual legacy/chart docs
and artifact-ignore assertions. Actual output:

```text
.local/t14-dod1-close.log
.local/t14-dod2-close.log
.local/t14-regression.log
PASS exact15 allowed files; source/new-file scope; text/size and added credential-marker scan
PASS README/RUNBOOK legacy/chart limits; generated fixtures and evidence logs ignored
PASS D5 manual review: no secrets/raw corpus/binaries/weights; API/DB/index unchanged; retained session policy
```

D1 PASS dependencies/allowed scope/diff, D2 PASS quality/regression/lock, D3 PASS
individual actual DoD1/2, D4 PASS docs/evidence/summary, D5 PASS code/contract/secrets/
source review. D6 completion candidate staged exactly15 paths and inspected below;
status COMPLETE is effective only when actual completion commit succeeds and is
inspected. Authorized remote push/hash equality reported post-execution; no self-hash
inside completion commit, no amend/rewrite/force push. T15 TODO and technically ready
once T14 closes; no next-task work or server deployment performed.

### D6 — Explicit staging and inspected completion candidate

Authorized Git mutation, exact command, exit0/no stdout:

```powershell
git add -- README.md RUNBOOK.md docs/tasks.md docs/handoffs.md docs/implementation-summary.md pyproject.toml uv.lock src/rag_core/domain/documents.py src/rag_core/adapters/parsers/registry.py src/rag_core/adapters/parsers/worker.py src/rag_core/adapters/parsers/text.py src/rag_core/adapters/parsers/archive.py src/rag_core/adapters/parsers/office.py src/rag_core/adapters/parsers/tables.py tests/integration/test_office_tables.py
```

`git diff --cached --check; git diff --cached --stat; git diff --cached --name-only;
git diff --cached -- src/rag_core/adapters/parsers/archive.py src/rag_core/adapters/parsers/office.py src/rag_core/adapters/parsers/tables.py`
exit0, full source diff inspected. Actual stat at that boundary:

```text
15 files changed, 1640 insertions(+), 75 deletions(-)
```

Read-only `$stagedScript | .venv/Scripts/python.exe -` compares exact15-path stage
against allowed list, requires no unstaged paths, cached whitespace/added credential
markers clean and baseline main/T13 HEAD unchanged. Exit0, actual:

```text
PASS staged exact15 T14 code/tests/docs; no unstaged changes; whitespace/credential-marker checks
PASS branch main and baseline T13 HEAD unchanged; baseline T07 scratch excluded
```

Latest docs check after final task notes, same command/cwd/config, exit0:

```text
PASS UTF-8/nonempty Markdown: 14 files
PASS internal links/anchors: 293
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```

Only this evidence append is restaged; repeat cached scope/whitespace/docs checks,
then `git commit -m "feat(T14): preserve spreadsheet and table evidence"` and inspect
actual commit before authorized `git push origin main`. Actual commit/output/remote
hash equality returned directly post-execution, not inserted into its own commit.
If commit/push fails, report actual failure/checkpoint instead of claiming closure.

### Post-completion inspection and heading encoding correction

Source completion command `git commit -m "feat(T14): preserve spreadsheet and table evidence"`
exit0, actual:

```text
[main f7c8acd] feat(T14): preserve spreadsheet and table evidence
15 files changed, 1680 insertions(+), 75 deletions(-)
```

`git show --check --oneline HEAD; git rev-parse HEAD; git rev-parse HEAD^;
git branch --show-current; git remote get-url origin; git show --format= --name-only HEAD;
git status --short` exit0: commit whitespace clean, exact15files, parentT13 unchanged,
only two inherited scratch directories untracked. Actual identities:

```text
f7c8acd04eb8282d520ad68f2ba572e16be77bdb
d3e57b29de892ff360e2e255e9d1680bf179faaf
main
https://github.com/admininistrator/rag-core.git
```

Authorized `git push origin main` exit0:

```text
To https://github.com/admininistrator/rag-core.git
   d3e57b2..f7c8acd  main -> main
```

Remote comparison `git rev-parse HEAD` + `git ls-remote origin refs/heads/main`,
with unequal-hash guard, exit0:

```text
PASS HEAD equals origin/main: f7c8acd04eb8282d520ad68f2ba572e16be77bdb
```

Final read inspection found six handoff headings had Unicode replaced by `?` in the
PowerShell-to-Python stdin write; `$OutputEncoding.WebName` returned `us-ascii`.
Raw log decoding and source/tests were unaffected. Headings repaired using UTF-8
apply_patch; separate docs-only corrective commit preserves the successful completion
commit/history and records its actual closure evidence here. No source/tests/DoD change;
only docs validator/diff checks apply to this correction. Corrective commit subject
`docs(T14): repair handoff heading encoding`; actual hash/remote equality reported
after that commit/push, not self-referenced. T15 ready; stop after T14.

<a id="h-t15-a01"></a>
## H-T15-A01 — Phase 3 / OCR EN/VI, 2026-10-01

Direct Codex agent (GPT-6 family; exact model/effort not exposed), no subagents.
All host commands cwd `C:\Users\Admin\Documents\GitHub\rag-core`, Windows PowerShell.
Baseline `main`/`cc6345dfb4b957a8f57d0ff6b3e9d31a016e606c`; read AGENTS/session
prompt/T13+T14 notes/evidence/summary, P01/P02/P07/P13 and living docs before code.
`git status --short` exit0 listed only inherited `?? .ptmp-t07-a02/` and
`?? .tmp-t07-a02/`; access warnings for historical T07 scratch/user Git ignore.
Initial combined rg enumeration exit1 from inherited inaccessible directory, targeted
reads succeeded. No T15 unfinished source/checkpoint; baseline scratch untouched.
`git branch --show-current`, `git rev-parse HEAD`, `git remote -v` exit0:

```text
main
cc6345dfb4b957a8f57d0ff6b3e9d31a016e606c
origin https://github.com/admininistrator/rag-core.git (fetch)
origin https://github.com/admininistrator/rag-core.git (push)
```

Initial sandbox `docker version --format '{{.Client.Version}} {{.Server.Version}}'`
exit1: config/npipe permission denied. Approved read check exit0 `29.5.2 29.5.2`;
approved `git ls-remote origin refs/heads/main` exit0:
`cc6345dfb4b957a8f57d0ff6b3e9d31a016e606c refs/heads/main` (matches baseline).
No credential/provider requirement, no external document upload or deployment.
Docker tests CPU2/memory2GiB/network none/init, uid10001, Python3.12.13;
Tesseract5.3.0/Leptonica1.82.0, eng/vie/osd Debian1:4.1.0-2, Docling slim2.132.0
OCR-only stage, Docling Parse7.22.1, PDFium5.13.0, pandas3.0.6; no Torch/weights.
Only original synthetic raster/PDF fixtures, never corpus QA or user documents.

### Preparation and retained failures

`$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; uv lock; uv sync --locked
--group dev --group api --group ingestion` (each command run, exit0): final lock112
packages; added slim/filetype/langcodes/PDFium/rtree/scipy/tqdm. An initial pandas
pin3.0.3 caused a downgrade; corrected to existing3.0.6 before implementation gates,
final existing package versions unchanged. Actual import command
`uv run --no-sync python -c "from docling.models.stages.ocr.tesseract_ocr_cli_model import TesseractOcrCliModel; print('OCR stage import OK')"`
exit0 `OCR stage import OK`; no models required.

Initial source Ruff/mypy exit1 found import/style, Windows POSIX typing, external
pandas stubs and union/backend annotations; fixed without global relaxations.
Exact external pandas import/untyped upstream unload and POSIX-only killpg annotations
are local and documented; final strict check42 source files passes below.

Build command (each exit0):
`docker build --progress=plain --target ocr-test -f docker/worker.Dockerfile -t rag-core-ocr-test:t15 .`;
logs `.local/t15-build.log`, `t15-build2.log` through `t15-build5.log`, no secrets.
Initial default `docker run --rm --init --network none --memory=2g --cpus=2 rag-core-ocr-test:t15`
exit2 `.local/t15-ocr-initial.log`: `Failed to initialize cache at /home/ragcore/.cache/uv`.
Set runtime UV_CACHE_DIR=/tmp/uv-cache; initial2 run with
`-e UV_CACHE_DIR=/tmp/uv-cache` exit1, `.local/t15-ocr-initial2.log`:

```text
AssertionError: assert 'Doanh thu quý một đạt 120 triệu đồng.' in 'Doanh thu quý một dat 120 triệu đồng.'
AssertionError: Real Tesseract child must start before interruption
3 failed, 16 passed in 80.84s (0:01:20)
```

PNG lost dấu with eng+vie, searchable scan inherited that actual upstream text.
Cancellation observer initially selected TSV only, missing live Tesseract OSD phase.
Kept source phrase/gold/fixtures unchanged; observed actual recognition (`stdout`,
OSD or TSV), not startup list-langs. Actual isolated CPU/network-none probe on same
PNG, `tesseract <fixture> stdout -l <order> --psm <mode>`, exit0:

```text
eng+vie 3 'Doanh thu quý một dat 120 triệu đồng.'
eng+vie 6 'Doanh thu quý một dat 120 triệu đồng.'
vie+eng 3 'Doanh thu quý một đạt 120 triệu đồng.'
vie+eng 6 'Doanh thu quý một đạt 120 triệu đồng.'
```

Production OCR/config and searchable fixture CLI now vie+eng/PSM3; no spelling
repair or expected phrase reduction. A later default run `.local/t15-dod1.log`
exit2 found root-owned `/tmp/uv-cache/sdists-v9/.git` baked by build-time sync.
Build cache explicitly `/root/.cache/uv` mounted in both RUNs; runtime `/tmp/uv-cache`
created by non-root. Final build5 exit0; default runner now works without extra env.

### DoD-1 — Actual worker OCR, source phrase and locator

Expected: real scan EN/VI có dấu, PNG/JPG/JPEG, mixed PDF, searchable scan native
layer once; original page/image locators/offset/bboxes; no skipped test or mock.
Command (approved Docker access), host cwd above; container cwd `/app`:

```powershell
docker run --rm --init --network none --memory=2g --cpus=2 rag-core-ocr-test:t15
```

Exit **0**, full real output `.local/t15-dod1-final.log`. Image CMD executes
`uv run --no-sync pytest tests/integration/test_ocr.py -v -s --tb=short --basetemp=/tmp/ocr-tests -o cache_dir=/tmp/pytest-cache`.
Actual excerpts (not inferred/rounded outputs):

```text
platform linux -- Python 3.12.13, pytest-9.1.1, pluggy-1.6.0 -- /app/.venv/bin/python3
collected 19 items
{"page_count": null, "quality": "ocr", "ocr": {"engine": "tesseract", "engine_version": "5.3.0", "languages": ["vie", "eng"], "attempted_pages": [1], "completed_pages": [1], "elapsed_seconds": 0.47932633999880636, "parser_peak_rss_mib": 147.421875, "child_peak_rss_mib": 146.921875}, "excerpt": "Doanh thu quý một đạt 120 triệu đồng."}
{"page_count": 2, "quality": "ocr", "ocr": {"engine": "tesseract", "engine_version": "5.3.0", "languages": ["vie", "eng"], "attempted_pages": [1, 2], "completed_pages": [1, 2], "elapsed_seconds": 2.5078987150009198, "parser_peak_rss_mib": 182.28125, "child_peak_rss_mib": 182.28125}, "excerpt": "First quarter revenue was 120 million VND. Doanh thu quý một đạt 120 triệu đồng."}
{"page_count": 3, "quality": "ocr", "ocr": {"engine": "tesseract", "engine_version": "5.3.0", "languages": ["vie", "eng"], "attempted_pages": [2], "completed_pages": [2], "elapsed_seconds": 1.2101823769990006, "parser_peak_rss_mib": 181.73828125, "child_peak_rss_mib": 181.73828125}, "excerpt": "First quarter revenue was 120 million VND. Doanh thu quý một đạt 120 triệu đồng. First quarter revenue was 120 million VND."}
PASS actual searchable scan image + Tesseract text layer: no OCR retry, phrase once
PASS cancel: observed actual Tesseract children=1, killed process group; cleanup; elapsed=3.625s
PASS timeout: observed actual Tesseract children=1, killed process group; cleanup; elapsed=8.015s
ACTUAL worker acceptance wall=74.189s container_memory_peak_mib=536.254
19 passed in 74.83s (0:01:14)
```

DoD-1 **PASS**. PDF physical2pages with distinct EN/VI source phrases, printed i/ii,
canonical OCR offsets/page bbox; images SHA256 ID/zero-based word bbox validated by
cropping original source pixels. Mixed3pages OCR only2; actual searchable OCR text
layer native-only/no duplicate. Source bytes and temp-empty asserted on every parse.
Stage elapsed excludes import/copy/native pass; RSS high-water/inherited fork memory
not sum or whole-machine budget. cgroup peak is whole test-container measurement,
not full corpus/other containers/Windows or promised production throughput.

### DoD-2 — Separate status/error/resource gate

Initial separate command below exit1, full `.local/t15-dod2.log`:

```powershell
docker run --rm --init --network none --memory=2g --cpus=2 rag-core-ocr-test:t15 uv run --no-sync pytest tests/integration/test_ocr.py -k status -v -s --tb=short --basetemp=/tmp/ocr-status -o cache_dir=/tmp/pytest-cache
```

```text
collected 19 items / 6 deselected / 13 selected
PASS cancel: observed actual Tesseract children=1, killed process group; cleanup; elapsed=3.340s
Failed: DID NOT RAISE ParseError
ACTUAL worker acceptance wall=42.961s container_memory_peak_mib=508.035
1 failed, 12 passed, 6 deselected in 43.66s
```

Real9.6MP stress fixture sometimes completed before8s deadline. Increased only
stress canvas/line count to21.6MP (<25MP cap), kept actual engine/recognition observer,
deadline/assertions/phrases unchanged. No sleeps/stubs in OCR, no gate reduction.
Final test image rebuilt via same build command, log `.local/t15-build6.log`.
Append final two DoD reruns below before completion.

Final review found Pillow conversion can carry EXIF metadata through PNG saving;
explicitly cleared copied image metadata before saving. Added independent original
JPEG EXIF orientation6/DPI600 phrase/source-pixel crop check (20 full OCR tests now).
No change to source input/expected EN/VI phrases. Rebuilt `.local/t15-build7.log`;
both final DoD runs must cover this current source/test revision.

### D2 — Host native/regression/locked quality and unchanged contracts

Host cwd above, `$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'`.
Actual commands and outputs:

```powershell
uv run --no-sync pytest tests/integration/test_text_parsers.py tests/integration/test_office_tables.py -q --tb=short --basetemp=.local/t15-native -o cache_dir=.local/t15-native-cache
```

Exit0, `.local/t15-native.log`: `42 passed in 36.41s`. Tests actual native parsers;
OCR disabled T13/14 paths unchanged by later OCR-only order/metadata fixes.

```powershell
uv run --no-sync pytest tests/unit tests/contract tests/security -q --tb=short --basetemp=.t15a -o cache_dir=.local/t15-regression-cache
```

Exit0, `.local/t15-regression.log`:

```text
........................................................................ [ 22%]
........................................................................ [ 44%]
........................................................................ [ 66%]
........................................................................ [ 88%]
.....................................                                    [100%]
325 passed in 125.03s (0:02:05)
```

Removed only own `.t15a` after verifying resolved absolute path equals workspace
direct child and stays inside root; native `.local` artifacts retained; historical
T07 scratch untouched. Output `PASS removed only self-created T15 regression basetemp inside workspace`.
Source paths exercised above unaffected by later OCR-only fixes; actual final OCR
gates exercise changed OCR branches separately. No service/provider mocks as OCR proof.

```powershell
uv sync --locked --offline --group dev --group api --group ingestion
uv run --no-sync python scripts/export_openapi.py --check
uv run --no-sync ruff check .
uv run --no-sync mypy src
git diff --check
```

Each exit0, actual output (locked112, existing package revisions unchanged):

```text
Resolved 112 packages in 56ms
PASS checked docs/api/openapi-v1.designed.json
PASS checked docs/api/openapi.served.json
PASS checked docs/api/examples-v1.json
PASS designed_operations=13 served_health_routes=2 synthetic_examples=37
PASS OpenAPI model + Draft2020-12 schemas=48; examples JSON Schema + Pydantic
CONTRACT EXPORT: PASS (business endpoints unmounted; no runtime query/stream verification)
All checks passed!
Success: no issues found in 42 source files
```

Ruff inherited three inaccessible scratch warnings; no lint errors. Final OCR metadata
review check `uv run --no-sync ruff check src tests/integration/test_ocr.py` and
`uv run --no-sync mypy src` repeated exit0, same success outputs.
`uv run --no-sync python scripts/check_docs.py` at interim docs exit0:

```text
PASS UTF-8/nonempty Markdown: 14 files
PASS internal links/anchors: 298
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```

Final docs validation will be repeated after final gate results/status.

### Final DoD-2 rerun — current source/test image

Same separate `docker run ... uv run --no-sync pytest ... -k status ...` command
above, host cwd unchanged/container `/app`, CPU2/RAM2GiB/init/network none.
Exit **0**, full `.local/t15-dod2-final.log`; expected explicit non-success errors,
partial page detection, real engine cancellation and measurements, actual:

```text
collected 20 items / 7 deselected / 13 selected
PASS .png blank/unreadable -> ocr_empty; source unchanged; sandbox empty
PASS .pdf blank/unreadable -> ocr_empty; source unchanged; sandbox empty
{"page_count": 2, "quality": "partial", "ocr": {"engine": "tesseract", "engine_version": "5.3.0", "languages": ["vie", "eng"], "attempted_pages": [1, 2], "completed_pages": [1], "elapsed_seconds": 0.6312517539990949, "parser_peak_rss_mib": 182.4296875, "child_peak_rss_mib": 182.4296875}, "excerpt": "Doanh thu quý một đạt 120 triệu đồng."}
PASS real Tesseract with empty tessdata -> ocr_tessdata_missing; cleanup
PASS missing vie -> ocr_tessdata_missing; corrupt eng/vie -> technical ocr_failed
PASS actual unavailable CLI -> ocr_engine_missing
PASS corrupt/image signature mismatch explicit errors; cleanup
PASS .png pixel allocation bounded before render/decode
PASS .pdf pixel allocation bounded before render/decode
PASS cancel: observed actual Tesseract children=1, killed process group; cleanup; elapsed=4.999s
PASS timeout: observed actual Tesseract children=1, killed process group; cleanup; elapsed=8.024s
ACTUAL worker acceptance wall=49.403s container_memory_peak_mib=867.703
13 passed, 7 deselected in 50.62s
```

DoD-2 **PASS**, not skip: deselected7 are phrase/provenance checks in separate full
DoD-1. Actual source unchanged + temp cleanup assert on every case. RUNBOOK
diagnostic/error/quality policy documented. Current 21.6MP stress measured peak above;
not full-stack budget or model inference benchmark.

### Final DoD-1 rerun — final OCR code and all20 tests

Same default `docker run --rm --init --network none --memory=2g --cpus=2 rag-core-ocr-test:t15`
command above, exit **0**, `.local/t15-dod1-final2.log`; engine/config/cwd unchanged.
Includes EXIF/DPI fix and larger actual stress input. Actual excerpts:

```text
collected 20 items
{"page_count": null, "quality": "ocr", "ocr": {"engine": "tesseract", "engine_version": "5.3.0", "languages": ["vie", "eng"], "attempted_pages": [1], "completed_pages": [1], "elapsed_seconds": 0.34707980299936025, "parser_peak_rss_mib": 147.25, "child_peak_rss_mib": 146.875}, "excerpt": "Doanh thu quý một đạt 120 triệu đồng."}
{"page_count": 2, "quality": "ocr", "ocr": {"engine": "tesseract", "engine_version": "5.3.0", "languages": ["vie", "eng"], "attempted_pages": [1, 2], "completed_pages": [1, 2], "elapsed_seconds": 0.7161576729995431, "parser_peak_rss_mib": 182.390625, "child_peak_rss_mib": 182.390625}, "excerpt": "First quarter revenue was 120 million VND. Doanh thu quý một đạt 120 triệu đồng."}
PASS EXIF orientation6/DPI600: phrase + bboxes retain original raw source pixels
{"page_count": 3, "quality": "ocr", "ocr": {"engine": "tesseract", "engine_version": "5.3.0", "languages": ["vie", "eng"], "attempted_pages": [2], "completed_pages": [2], "elapsed_seconds": 0.3648834400009946, "parser_peak_rss_mib": 181.8671875, "child_peak_rss_mib": 181.8671875}, "excerpt": "First quarter revenue was 120 million VND. Doanh thu quý một đạt 120 triệu đồng. First quarter revenue was 120 million VND."}
PASS actual searchable scan image + Tesseract text layer: no OCR retry, phrase once
PASS cancel: observed actual Tesseract children=1, killed process group; cleanup; elapsed=4.012s
PASS timeout: observed actual Tesseract children=1, killed process group; cleanup; elapsed=8.024s
ACTUAL worker acceptance wall=68.447s container_memory_peak_mib=810.703
20 passed in 69.10s (0:01:09)
```

Final DoD-1 **PASS**, DoD-2 **PASS** separately above; no pending OCR acceptance.

### D1/D4/D5 review and closure preparation

Final source reviewed for per-page selection/no native text duplication, raw image
EXIF/DPI provenance, cumulative pixel/text/process bounds, safe error/quality and
no source mutation/auth/storage scope changes. T03 API/PG/index schemas unchanged;
intermediate schema1 additive fields/config/revisions need T16/T19 fingerprints.
No prompt corpus/gold edits, provider/model/Scarlet/deploy/merge/force push.
README/RUNBOOK working build/test/diagnostic commands and unsupported cases updated,
task notes/summary/evidence cover separate gates, limits and readiness. No N/A.

An initial ad-hoc scope helper's Python command exit1 (combined shell continued)
matched a literal private-key marker in historical T10 review code at handoffs line4277,
not a real credential. Corrected to compare task added diff and actual local secret
values in memory; historical evidence kept unchanged. Reproduction helper retained
at ignored `.local/t15_review.py`; actual command/cwd as above:

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'
uv run --no-sync python .local/t15_review.py
```

Exit0:

```text
PASS existing lock package versions unchanged; added=docling-slim,filetype,langcodes,pypdfium2,rtree,scipy,tqdm; total=112
PASS API/metadata/inference/dev dependency groups unchanged
PASS exact15 task paths UTF-8/scope; original prompt/corpus/plan/API/Compose unchanged
PASS added diff credential markers/local secret comparisons; no values printed
```

`git var GIT_AUTHOR_IDENT > $null` exit0, `PASS Git author identity already configured; no identity change`.
Final worker target build `docker build --progress=plain --target worker -f docker/worker.Dockerfile -t rag-core-worker:t15 .`
log `.local/t15-worker-build-final.log`; final image/source/diagnostic check follows.

Final production target build exit0; diagnostics/image SHA command:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .local/t15_images.ps1
```

Exit0, full `.local/t15-images-final.log`, actual excerpt (helper contains exact
Docker commands; compares installed source42 + copied test2 to worktree SHA256,
queries UID/packages/no Torch, CLI version/list-langs/config/data SHA):

```text
PASS rag-core-worker:t15: uid=10001 source_sha256_equal=42 test_sha256_equal=0 docling-slim=2.132.0 docling-parse=7.22.1 pdfium=5.13.0 torch_installed=False
sha256:54294ef6d35ae5c76a5967b224ca8de12b2a0bc7cc5ecb1bc313f7d26158f9c4 10001:10001
PASS rag-core-ocr-test:t15: uid=10001 source_sha256_equal=42 test_sha256_equal=2 docling-slim=2.132.0 docling-parse=7.22.1 pdfium=5.13.0 torch_installed=False
sha256:593c7d5abe847efd733d64b1bbe58e8531eb6839df1a76bfbf093fae84f9c455 10001:10001
tesseract 5.3.0
 leptonica-1.82.0
List of available languages in "/usr/share/tesseract-ocr/5/tessdata/" (3):
eng
osd
vie
uid 10001 docling-slim 2.132.0
tessdata system default
{"eng.traineddata": "7d4322bd2a7749724879683fc3912cb542f19906c83bcc1a52132556427170b2", "osd.traineddata": "9cf5d576fcc47564f11265841e5ca839001e7e6f38ff7f7aacf46d15a96b00ff", "vie.traineddata": "79df64caf7bcfb2a27df5042ecb6121e196eada34da774956995747636d5bfa1"}
```

D1 scope/dependency/diff PASS, D2 quality/native/regression/lock PASS, D3 each real
DoD PASS, D4 living docs/notes/summary/evidence updated, D5 source/contract/pins/secrets
review PASS. D6 subject `feat(T15): support Vietnamese and English OCR`; explicit15file
stage/inspection and commit follow. COMPLETE candidate fields only effective with
successful inspected completion commit; actual hash/remote equality returned after
push, no self-referenced hash/amend. If commit/push fails, report actual checkpoint.
T16 deps T15/T13/T14 ready after closure; no next-task implementation started.

### Final D4/D5/D6 — Explicit staged completion candidate

`uv run --no-sync python scripts/check_docs.py` exit0 on final living docs:

```text
PASS UTF-8/nonempty Markdown: 14 files
PASS internal links/anchors: 301
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```

`git diff --check` exit0/no output. Approved Git staging, host cwd above:

```powershell
git add -- README.md RUNBOOK.md docs/tasks.md docs/handoffs.md docs/implementation-summary.md pyproject.toml uv.lock docker/worker.Dockerfile docker/worker.Dockerfile.dockerignore src/rag_core/domain/documents.py src/rag_core/ports/parsers.py src/rag_core/adapters/parsers/registry.py src/rag_core/adapters/parsers/worker.py src/rag_core/adapters/parsers/ocr.py tests/integration/test_ocr.py
git diff --cached --check
uv run --no-sync python .local/t15_review.py --staged
git diff --cached --stat
git status --short
```

Each exit0; cached whitespace clean, exact15 paths above, actual review output:

```text
PASS existing lock package versions unchanged; added=docling-slim,filetype,langcodes,pypdfium2,rtree,scipy,tqdm; total=112
PASS API/metadata/inference/dev dependency groups unchanged
PASS exact15 task paths UTF-8/scope; original prompt/corpus/plan/API/Compose unchanged
PASS exact15 staged paths; staged content equals reviewed worktree
PASS added diff credential markers/local secret comparisons; no values printed
15 files changed, 1372 insertions(+), 33 deletions(-)
```

Final docs-only evidence append changes that insertion count; restage handoffs and
repeat cached/docs review before commit. Escalated Git status can enumerate two
extra historical directories previously only present as Access-denied warnings:
`.pytmp-t07-a02/` and `UsersAdminAppDataLocalTempt07a03/`. Together with baseline
`.ptmp-t07-a02/`/`.tmp-t07-a02/`, all four remain untracked, untouched and unstaged.
Ignored `.local` logs/helpers/temp stay outside commit. No secret/model/cache/raw
source/pdf/dataset, or unexpected source/test/contract path in stage.

D1–D5 **PASS**. D6 candidate exact scoped15-file commit reviewed; command
`git commit -m "feat(T15): support Vietnamese and English OCR"` followed by
`git show --stat --oneline HEAD`, `git rev-parse HEAD`, authorized normal
`git push origin main` and remote hash equality. Actual post-commit/remote output
reported to user; not written into this same commit, no amend/rewrite. T15 COMPLETE
only with successful inspected completion commit; T16 then ready, **STOP AFTER T15**.

<a id="h-t16-a01"></a>
## H-T16-A01 — Phase 3 / Structural chunks and source locators, 2026-10-01

Direct Codex agent (GPT-6 family; exact model/effort not exposed), no subagents.
All host commands cwd `C:\Users\Admin\Documents\GitHub\rag-core`, Windows PowerShell,
Python3.12.4/uv0.11.16/pytest9.1.1; `UV_CACHE_DIR=<repo>\.uv-cache`.
AGENTS/session prompt, T13/T14/T15 COMPLETE notes/interfaces/evidence, P01/P03/P04/P07/P13,
README/RUNBOOK/current checkpoint read before code. No unfinished T16 source.
User authorizes scoped commit and normal push origin/current branch; no force/merge/deploy.

`git status --short; git branch --show-current; git rev-parse HEAD; git remote -v`
exit0, baseline output:

```text
?? .ptmp-t07-a02/
?? .tmp-t07-a02/
main
e1e348d45b7a83872c420f5b6f647551db21e751
origin https://github.com/admininistrator/rag-core.git (fetch)
origin https://github.com/admininistrator/rag-core.git (push)
```

Inherited scratch/global-ignore ACL warnings retained; no paths there touched.
Initial sandbox `git ls-remote origin refs/heads/main` exit128, connection refused.
Same approved network command exit0:

```text
e1e348d45b7a83872c420f5b6f647551db21e751 refs/heads/main
```

`git var GIT_AUTHOR_IDENT | Out-Null; if ($LASTEXITCODE -eq 0) { Write-Output 'Git author configured' }`
exit0, `Git author configured`; no identity changed or printed.
Exact13 allowed paths: README/RUNBOOK/tasks/handoffs/implementation-summary,
pyproject/uv.lock, scripts/setup_tokenizer.py, adapters/tokenizer.py,
domain/chunking.py, ports/tokenizer.py, tests/unit/test_chunking.py,
tests/integration/test_source_locators.py. No existing parser/OCR/API/DB/Compose/corpus change.

### Dependencies and real tokenizer artifact

Verified official [BGE-M3 model revision](https://huggingface.co/BAAI/bge-m3/tree/5617a9f61b028005a4858fdac845db406aefb181)
and [tokenizer config](https://huggingface.co/BAAI/bge-m3/raw/5617a9f61b028005a4858fdac845db406aefb181/tokenizer_config.json).
Installed tokenizers0.22.2 API supplies encoding offsets/counts; local adapter disables
truncation/padding and slices original Unicode, not normalized decode. No model weights,
inference/provider/service/credentials needed; source fixtures synthetic EN/VI.

Approved dependency command, exit0:

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; uv add --group ingestion 'tokenizers==0.22.2' --no-sync; if ($LASTEXITCODE -eq 0) { uv sync --locked --group dev --group api --group ingestion }
```

```text
Resolved 117 packages in 1.60s
Resolved 117 packages in 1ms
Prepared 6 packages in 1.43s
Uninstalled 1 package in 3ms
Installed 6 packages in 268ms
+ filelock==4.0.8
+ fsspec==2026.9.0
+ hf-xet==1.6.0
+ huggingface-hub==1.33.0
+ tokenizers==0.22.2
```

Initial explicit download used stdlib `urllib.request.urlopen` on exact pinned
`https://huggingface.co/BAAI/bge-m3/resolve/5617a9f61b028005a4858fdac845db406aefb181/tokenizer.json`,
timeout60s/read<=32MiB, ignored local path `.local/tokenizers/bge-m3/tokenizer.json`.
Exit0, actual output:

```text
tokenizer.json bytes 17098108 sha256 21106b6d7dab2952c1d496fb21d5dc9db75c28ed361a05f5020bbba27810dd08
```

`uv run --no-sync python scripts/setup_tokenizer.py` exit0, existing real artifact
verified and local manifest written; no claim of a second cold download:

```text
VERIFIED BAAI/bge-m3@5617a9f61b028005a4858fdac845db406aefb181/21106b6d7dab2952c1d496fb21d5dc9db75c28ed361a05f5020bbba27810dd08/tokenizers-0.22.2; bytes=17098108
```

Tests never download/skip/fake tokenization. Missing/corrupt runtime artifacts fail.

### Retained diagnostics and scope decisions

Initial PowerShell ASCII-to-Python task-heading lookup failed `ValueError: substring not found`
without edits; applied UTF-8 patch and used `$OutputEncoding=[System.Text.UTF8Encoding]::new($false)`
for subsequent non-ASCII stdin. First source lint exit1 `E741 Ambiguous variable name: l`;
mypy exit1 role typing/list annotation/locator union, corrected locally, no strictness reduction.
Initial unit14PASS, expanded unit16PASS; final extra >8192-token input check17PASS below.
First actual source integration `.local/t16-source1.log` exit1:

```text
E   rag_core.domain.chunking.ChunkingError: unmapped_table_header
1 failed, 8 passed in 6.85s
```

CSV emits separate records with header context; added original-first-record header mapping
and adjacent record groups. Same original fixture/parser/source assertions retained.
Combined unit/source `.local/t16-source2.log` exit0 `25 passed in 7.39s`.
Reviewed merged XLSX header-only rows to avoid duplicating their raw cells in context/body.
Whole row/header >budget returns safe explicit error, preserving the no-cell-split DoD;
no silent truncation/oversized success. Empty separators/policy annotations have no source quote.

### DoD-1 — Actual tokenizer budgets/Unicode/long blocks/tables/overlap/stable identity

Expected512total embedding tokens including special tokens, <=64content-token overlap,
Unicode/combining/emoji/unbroken/special-token-text exact source coverage, long table
whole-row groups with repeated source headers, rerun stable IDs, new version/different
parser/tokenizer/config/generation fingerprint changes. Real BGE-M3 artifact above;
no provider/model weights/services. Initial official16PASS command exit0:

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; $env:UV_NO_SYNC='1'; $env:PYTEST_ADDOPTS='--basetemp=.local/t16-dod1 -o cache_dir=.local/t16-dod1-cache'; uv run pytest tests/unit/test_chunking.py -v --tb=short *> .local/t16-dod1.log
```

Final17PASS adds >8192tokens original input without tokenizer truncation, same512budget.
Command/exit0, `.local/t16-unitfinal.log`:

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; uv run --no-sync pytest tests/unit/test_chunking.py -q --tb=short --basetemp=.local/t16-unitfinal -o cache_dir=.local/t16-unitfinal-cache *> .local/t16-unitfinal.log
```

```text
.................                                                        [100%]
17 passed in 2.35s
```

All17 unskipped tests are actual tokenizer-backed, including artifact checksum refusal,
source quote identity/ranges/output bounds, trusted custom profile/unknown-domain failure
and refusal to chunk partial PDF. Source tests independently validate original bytes.

### DoD-2 — Actual parsers and independently reopened PDF/DOCX/XLSX/PPTX source

Expected chunk maps stay within physical PDF pages/table/units/sheet/PPTX shape,
real originals and source XML/cells independently reopened; no PDF off-by-one and no
fabricated Office pages. Also CSV/TXT/MD/HTML quote-normalization/original raw spans.
Command exit0, `.local/t16-dod2.log`:

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; $env:UV_NO_SYNC='1'; $env:PYTEST_ADDOPTS='--basetemp=.local/t16-dod2 -o cache_dir=.local/t16-dod2-cache'; uv run pytest tests/integration/test_source_locators.py -v -s --tb=short *> .local/t16-dod2.log
```

```text
collecting ... collected 9 items
PDF: physical pages=[1, 2, 3], chunks=6, printed=i/ii/iii
DOCX: tables=[0, 1], chunks=15, no invented pages
XLSX: chunks=8, mapped cells=104, merged/header/units retained
PPTX: slides=[1, 2], chunks=18, shape/table boundaries preserved
test_other_text_and_table_formats_keep_normalized_quote_and_original_span[txt] PASSED
test_other_text_and_table_formats_keep_normalized_quote_and_original_span[md] PASSED
test_other_text_and_table_formats_keep_normalized_quote_and_original_span[html] PASSED
test_other_text_and_table_formats_keep_normalized_quote_and_original_span[csv] PASSED
test_original_table_unit_too_large_explicit_error PASSED
9 passed in 6.23s
```

Actual test-only profile96/12 forces repeated table/paragraph splits, and unit gate
uses baseline512/64; budget measured including header/policy metadata. XLSX fixtures
use merged header,30data rows,0% formats, blank-region currency switch and missing
formula cache. DOCX2tables/VND-USD, PPTX2slides and source XPath, PDF3physical pages
vs printed Roman labels. Original binary unchanged and parser sandbox empty asserted.
RUNBOOK T16 documents config/error/reindex implications; HTTP resolver remains T24.

### Additional actual OCR word regrouping/source mapping

Existing verified T15 Linux worker image `rag-core-ocr-test:t15`, Python3.12.13,
Tesseract5.3.0/Docling slim2.132.0, CPU2/2GiB/network-none/non-root/init. No image/source
deployment. Ignored `.local/t16-ocr/export_ocr.py` reuses actual T15 fixture generators,
ParserRegistry OCR engine, asserts unchanged input/sandbox cleanup, exports original
ParsedDocument JSON and traineddata hashes. Host parses UTF-8 JSON, actual T16 tokenizer
maps every word back to original block/locator/bbox and checks required extraction config.

```powershell
$taskEvidence=(Resolve-Path -LiteralPath .local/t16-ocr).Path; docker run --rm --init --network none --memory=2g --cpus=2 --mount "type=bind,source=$taskEvidence,target=/evidence" rag-core-ocr-test:t15 python /evidence/export_ocr.py
uv run --no-sync python .local/t16-ocr/verify_chunks.py *> .local/t16-ocr-verify.log
```

Both exit0 after correcting host JSON locale decoding (`read_text(encoding='utf-8')`).
Initial host helper phrase assertion exit1 from cp1252 mojibake, output itself was
UTF-8/correct; original phrase/gold/engine/source unchanged. Actual output:

```text
png actual OCR blocks 8 engine 5.3.0
pdf actual OCR blocks 15 engine 5.3.0
png actual OCR word mapping PASS; blocks 8 chunks 1 mapped 8 tokens [11] excerpt Doanh thu quý một đạt 120 triệu đồng.
pdf actual OCR word mapping PASS; blocks 15 chunks 2 mapped 15 tokens [11, 11] excerpt Doanh thu quý một đạt 120 triệu đồng.
```

Actual eng SHA `7d4322bd2a7749724879683fc3912cb542f19906c83bcc1a52132556427170b2`,
vie SHA `79df64caf7bcfb2a27df5042ecb6121e196eada34da774956995747636d5bfa1`,
OSD SHA `9cf5d576fcc47564f11265841e5ca839001e7e6f38ff7f7aacf46d15a96b00ff`.
Extractor config digest additionally includes5.3.0/vie+eng/216dpi/Docling2.132.0/PSM3;
same OCR text/provenance with changed elapsed/RSS gives same chunk IDs.
These are synthetic fixtures and reused real OCR runtime, not new OCR quality/full-stack
RAM/latency acceptance, model inference, source storage, corpus benchmark or ingestion.

### D1–D6 quality, review and closure

D1 scope/dependency review and `git diff --check` exit0/no stdout; baseline scratch preserved.
D2 commands each exit0, exact output/logs:

```powershell
uv run --no-sync ruff check src tests scripts corpus-documents/scripts
uv run --no-sync mypy src
uv lock --check --offline
uv sync --locked --offline --group dev --group api --group ingestion
uv run --no-sync pytest tests/integration/test_text_parsers.py tests/integration/test_office_tables.py -q --tb=short --basetemp=.local/t16-native -o cache_dir=.local/t16-native-cache
uv run --no-sync python scripts/export_openapi.py --check
```

```text
All checks passed!
Success: no issues found in 45 source files
Resolved 117 packages in 38ms
Resolved 117 packages in 1ms
Checked 116 packages in 27ms
42 passed in 33.72s
PASS designed_operations=13 served_health_routes=2 synthetic_examples=37
PASS OpenAPI model + Draft2020-12 schemas=48; examples JSON Schema + Pydantic
CONTRACT EXPORT: PASS (business endpoints unmounted; no runtime query/stream verification)
```

Full logs `.local/t16-ruff.log`, `t16-mypy.log`, `t16-native.log`, `t16-openapi.log`.
Initial full regression exit1 `.local/t16-regression.log`:

```powershell
uv run --no-sync pytest tests/unit tests/contract tests/security -q --tb=short --basetemp=.local/t16-regression -o cache_dir=.local/t16-regression-cache
```

```text
E   FileNotFoundError: [Errno 2] No such file or directory: 'C:\\Users\\Admin\\Documents\\GitHub\\rag-core\\.local\\t16-regression\\test_prepare_and_rerun_preserv0\\.downloads\\default-stage-dfcd6a16e273434b9a414fc6cd134ffe\\default\\documents\\.hotpot_9dbd5ec2781ec2df0e16c49e80e045fbaaa9ae12ac61765348937d72a88b3648.md.6ajljkzo.part'
10 failed, 331 passed in 88.33s (0:01:28)
```

Windows path-length failure in existing corpus temporary stage writer, reproduced and
retained. No corpus/test/gold/security change. Same suite rerun with fresh shorter
basetemp `.local/u16`; outcome and final docs/scope/commit steps appended below.
D3 individual real DoDs PASS as above. D4 README/RUNBOOK/notes/summary/evidence updated;
new internal source maps, tokenizer setup/pins, mandatory OCR config, reindex/generation
and limits explicitly described. D5/D6 review/staging/commit/push remain pending here.

No DB/API/index migration. T17/T19 must include chunk pipeline fingerprint plus model/index
revision, mount verified tokenizer offline and authorize source/generation separately.
T24 must enforce active session before resolving maps. No full corpus chunk tuning,
weights/inference/retrieval/LLM, worker T16 deployment or full-stack resource measurement.
Chunk/table source precision is measured on fixtures, not a general layout/accuracy claim.
Completion subject `feat(T16): chunk documents with stable source mappings`; actual hash
and origin/main equality reported after successful inspected commit/push; no self-reference.
**STOP AFTER T16**, do not start T17.

### Final regression and review fixes

Same full suite, shorter **fresh** basetemp, cwd/config as above; exit0,
`.local/t16-regression-short.log`:

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; uv run --no-sync pytest tests/unit tests/contract tests/security -q --tb=short --basetemp=.local/u16 -o cache_dir=.local/c16 *> .local/t16-regression-short.log
```

```text
........................................................................ [ 21%]
........................................................................ [ 42%]
........................................................................ [ 63%]
........................................................................ [ 84%]
.....................................................                    [100%]
341 passed in 108.10s (0:01:48)
```

Collected before the final extra >8192-token unit case; final17-unit gate independently
covers that new case. No older test/gold/schema changed or skipped. No scratch deleted.
Review found header-only numeric Excel cells also need number-format/cell metadata.
Header policy now retained with source cells, synthetic policy text explicitly unquotable;
new original-XLSX integration test guards percent-header units. Combined real gates
`.local/t16-review-tests.log` exit0 `27 passed in 12.11s`.
Ruff/mypy rerun after source correction exit0:
`All checks passed!` / `Success: no issues found in 45 source files`.

Final **separate** DoD gates on reviewed source, each exit0:

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; $env:UV_NO_SYNC='1'; $env:PYTEST_ADDOPTS='--basetemp=.local/t16-close-unit -o cache_dir=.local/t16-close-unit-cache'; uv run pytest tests/unit/test_chunking.py -q --tb=short *> .local/t16-close-unit.log
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; $env:UV_NO_SYNC='1'; $env:PYTEST_ADDOPTS='--basetemp=.local/t16-close-source -o cache_dir=.local/t16-close-source-cache'; uv run pytest tests/integration/test_source_locators.py -v -s --tb=short *> .local/t16-close-source.log
```

```text
17 passed in 2.51s
collecting ... collected 10 items
PDF: physical pages=[1, 2, 3], chunks=6, printed=i/ii/iii
DOCX: tables=[0, 1], chunks=15, no invented pages
XLSX: chunks=8, mapped cells=104, merged/header/units retained
PPTX: slides=[1, 2], chunks=18, shape/table boundaries preserved
test_xlsx_header_number_format_metadata_is_preserved_and_not_a_quote PASSED
10 passed in 7.53s
```

Final OCR helper rerun initially failed solely printing Unicode to default cp1252
(`UnicodeEncodeError`), not mapping/assertions; setting UTF-8 stdout, same sources/engine/
phrase/assertions, command exit0 `.local/t16-ocr-close.log`:

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; $env:PYTHONIOENCODING='utf-8'; uv run --no-sync python .local/t16-ocr/verify_chunks.py *> .local/t16-ocr-close.log
```

```text
png actual OCR word mapping PASS; blocks 8 chunks 1 mapped 8 tokens [11] excerpt Doanh thu quý một đạt 120 triệu đồng.
pdf actual OCR word mapping PASS; blocks 15 chunks 2 mapped 15 tokens [11, 11] excerpt Doanh thu quý một đạt 120 triệu đồng.
```

D4 `uv run --no-sync python scripts/check_docs.py` exit0 before final result-note additions:

```text
PASS UTF-8/nonempty Markdown: 14 files
PASS internal links/anchors: 306
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```

D5 reviewed all13task paths/source/diff; ignored review helper checks existing lock versions,
unchanged API/dev/metadata/inference/OCR groups, UTF-8/path allowlist and added-text
private-key/JWT markers + local credential exact-value comparisons without printing values.
`uv run --no-sync python .local/t16-review.py` exit0:

```text
PASS existing lock versions unchanged; five added tokenizer packages; total 117
PASS API/dev/metadata/inference/OCR groups unchanged; ingestion adds only tokenizers pin
PASS exact13 task paths UTF-8; added text has no credential markers/local secret values; corpus/plan/API/Compose/parsers untouched
```

D1-D5 PASS. D6 explicit13-file staging/inspection, final docs check and completion commit
are final closure steps. COMPLETE fields are conditional on successful inspected commit.
Actual commit/output/authorized origin-main push/equality reported after execution,
without adding self-hash to this commit or amending. T17 T16/T02 dependencies ready only
with T16 inspected completion; **STOP AFTER T16**.

### D6 staged review

`git add -- README.md RUNBOOK.md docs/tasks.md docs/handoffs.md docs/implementation-summary.md pyproject.toml uv.lock scripts/setup_tokenizer.py src/rag_core/adapters/tokenizer.py src/rag_core/domain/chunking.py src/rag_core/ports/tokenizer.py tests/unit/test_chunking.py tests/integration/test_source_locators.py`
approved repository Git write, exit0. Expected Git CRLF-to-LF warnings for three
Python-written docs; staged content has UTF-8/LF. Initial ignored review helper exact
worktree-byte comparison failed `AssertionError` solely from that Git newline conversion.
Correct comparison uses Git's own `hash-object --path <path> <path>` vs `rev-parse :<path>`
to apply the declared Git text filters, while exact13path/UTF-8/secrets/lock checks remain.
No source/test/gate changed. Cached whitespace check exit0/no output.

Final docs validation after results notes exit0:

```text
PASS UTF-8/nonempty Markdown: 14 files
PASS internal links/anchors: 308
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```

Staged scope before this append:13files/1791insertions/12deletions; source/corpus/model
artifacts/scratch all excluded except the13 explicitly listed task files. Review outputs
and final commit/push/hash equality are returned directly after execution. No amend,
force push/merge/deploy. Final evidence-only append is restaged before commit.

<a id="h-t17-a01"></a>
## Phase 3 / T17 / T17-A01 — Shared model inference

Direct Codex agent, exact runtime model/effort not exposed, no subagents; started2026-10-01
(Asia/Bangkok). CWD for all commands below:
`C:/Users/Admin/Documents/GitHub/rag-core`. Baseline main/`9633cfcb872a89ccb1f472e6361c201e94d83588`
equals live origin/main; T16/T02 COMPLETE notes/interfaces/evidence read. Only inherited
untracked `.ptmp-t07-a02/` and `.tmp-t07-a02/`, with historical inaccessible T07 scratch
warnings, preserved. No prior T17 implementation. User authorizes scoped commit/push;
no subagent/drain/merge/deploy/Scarlet edits or unrelated service mutation.

### Environment, pins and actual failures

Initial unprivileged `docker info --format '{{.OSType}} {{.MemTotal}}'` failed with
`permission denied while trying to connect to the docker API at npipe:////./pipe/docker_engine`;
initial `git ls-remote origin refs/heads/main` exit128 connection failed. Approved escalation
ran the same read-only checks exit0:

```text
linux 8325890048
9633cfcb872a89ccb1f472e6361c201e94d83588 refs/heads/main
```

Host and Docker GPU checks each exit0:
`nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader`
and `docker run --rm --gpus all python:3.12.13-slim-bookworm nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader`:

```text
NVIDIA GeForce RTX 4060 Laptop GPU, 8188 MiB, 576.88
```

Thus GPU capability AVAILABLE, GPU smoke required; NOT_AVAILABLE not used. First official
PyPI metadata probe assumed FlagEmbedding wheel and exited1 `StopIteration`: upstream1.3.5
is sdist-only. Corrected official sdist API inspection succeeded, no vendor source copied
to repo; helper source only ignored `.local`. First Ruff failed3style findings; first mypy
failed2missing list annotations; corrected, no test/gate change. Optional Windows OS memory
CIM inspection denied access, no host total-RAM measurement claimed. Docker actual capacity
above and process RSS used instead. Logs are local/ignored, no private source text/keys.

`$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; uv lock *> .local/t17-lock.log`
exit0, `Resolved 169 packages in 8.42s`. Lock has166unique package names/169entries including
CPU/CUDA alternatives. Existing117packages retained except required compatibility downgrades
`huggingface-hub1.33.0 ->0.36.2` (transformers4.57 requires<1) and `fsspec2026.9.0 ->2026.6.0`
(datasets dependency). No other existing version changed. API/ingestion remain without
Torch/FlagEmbedding model imports/runtime groups. Real parser/source/chunk regressions below.

`$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; uv sync --locked --group dev --group api --group ingestion --group inference *> .local/t17-sync.log`
exit0; actual CPython3.12.4 host, torch2.9.1+cpu, FlagEmbedding1.3.5, transformers4.57.6,
tokenizers0.22.2, sentence-transformers5.1.2, peft0.17.1. GPU group mutually exclusive,
locked2.9.1+cu128 from official PyTorch index. Python/uv Docker base digests unchanged.
Immutable official HF API pins/checksums captured in `configs/model-artifacts.json`:
embedding5617a9f61b028005a4858fdac845db406aefb181 (T16tokenizer unchanged),
reranker953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e. URLs:
[BGE-M3](https://huggingface.co/BAAI/bge-m3),
[reranker](https://huggingface.co/BAAI/bge-reranker-v2-m3),
[FlagEmbedding](https://github.com/FlagOpen/FlagEmbedding).

`.venv/Scripts/python.exe scripts/setup_models.py *> .local/t17-download.log` exit0;
expected4,588,661,382total artifact bytes including tokenizer/config/heads, actual checksum/
size verification PASS; exact real excerpt:

```text
DOWNLOADED embedding/pytorch_model.bin 2271145830B
DOWNLOADED embedding/sparse_linear.pt 3516B
DOWNLOADED embedding/colbert_linear.pt 2100674B
DOWNLOADED reranker/model.safetensors 2271071852B
MODEL CACHE VERIFIED
```

### DoD-1 actual CPU weights

First command exit0 `.local/t17-real1.log`:
`$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; uv run --no-sync pytest tests/integration/test_model_inference.py -v -s --tb=short --basetemp=.local/t17-real1 -o cache_dir=.local/t17-c1 *> .local/t17-real1.log`.
Real final scheduler/token-ID provenance command exit0 `.local/t17-real2.log`:

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; $env:UV_NO_SYNC='1'; $env:PYTEST_ADDOPTS='--basetemp=.local/t17-real2 -o cache_dir=.local/t17-cr2'; uv run pytest tests/integration/test_model_inference.py -v -s --tb=short *> .local/t17-real2.log
```

```text
REAL RERANK elapsed=17.469s raw_scores=(5.891203880310059, -11.034421920776367)
test_actual_tokenizer_refuses_silent_truncation[embed] PASSED
test_actual_tokenizer_refuses_silent_truncation[rerank] PASSED
REAL CANCEL/TIMEOUT/RECOVERY PASS; shared native executor slots=1
6 passed in 145.91s (0:02:25)
```

First6passed82.42s; second under concurrent Docker-build/regression contention, latency
not advertised as isolated SLA. Both use actual offline weights, no skip/fake vectors.
Dense1024/unit norm/finite vectors, sparse sorted unique positive weights with actual token
IDs, EN/VI cross-language relevant cosine >distractor, two real raw rerank relevance checks,
embed/pair token-limit rejection, native cancel/deadline/slot/recovery checked. Dedicated
final Linux image gate and resource smoke append below.

### D2 quality/regression and retained failure

First full command exit1, `.local/t17-regression.log`:
`$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; uv run --no-sync pytest tests/unit tests/contract tests/security -q --tb=short --basetemp=.local/u17 -o cache_dir=.local/c17 *> .local/t17-regression.log`:

```text
FAILED tests/security/test_auth.py::test_service_key_and_app_binding_even_with_shared_jwks
E rag_core.auth.AuthUnavailable
1 failed, 354 passed in 286.66s (0:04:46)
```

Observed during concurrent real host model/build, inferred timing contention, not proven
root cause. No auth code/threshold/test relaxed. Same failed test plus new19tests command
exit0 `.local/t17-target3.log`:
`$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; uv run --no-sync pytest tests/security/test_auth.py::test_service_key_and_app_binding_even_with_shared_jwks tests/unit/test_model_client.py tests/unit/test_inference_scheduler.py -q --tb=short --basetemp=.local/t17-target3 -o cache_dir=.local/t17-ct3 *> .local/t17-target3.log`:
`20 passed in 2.92s`.

Full final rerun exit0 `.local/t17-regression2.log`:
`$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; uv run --no-sync pytest tests/unit tests/contract tests/security -q --tb=short --basetemp=.local/v17 -o cache_dir=.local/d17 *> .local/t17-regression2.log`:
`361 passed in 151.97s (0:02:31)`.

Relevant real parsers/source mappings after shared-dependency changes exit0 `.local/t17-parsers.log`:
`$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; uv run --no-sync pytest tests/integration/test_source_locators.py tests/integration/test_text_parsers.py -q --tb=short --basetemp=.local/t17-parsers -o cache_dir=.local/t17-cp *> .local/t17-parsers.log`:
`29 passed in 39.59s`.

Final current source checks each exit0: `uv run --no-sync ruff check .` →`All checks passed!`
(inherited inaccessible scratch warnings); `uv run --no-sync mypy src` →
`Success: no issues found in 55 source files`; `uv run --no-sync python scripts/export_openapi.py --check` →
`PASS designed_operations=13 served_health_routes=2 synthetic_examples=37` /48schemas /
`CONTRACT EXPORT: PASS (business endpoints unmounted; no runtime query/stream verification)`.
`git diff --check` exit0/no whitespace error; expected Git CRLF→LF warnings for Python-written
files. New19tests prove queue32/reserved query admission, query preemption between batches,
single executor thread, running timeout slot ownership, queued cancellation, safe failure/
recovery/duplicate/shutdown/bounds and HTTP client revision/result/error/cancel protocol.
Synthetic unit transport is not real model/HTTP acceptance; DoD weights and smoke separate.

### DoD-2 CPU Docker HTTP/resource smoke

Final CPU test image build exit0, `.local/t17-build-cpu-final.log`:
`docker build --target inference-test -f docker/inference.Dockerfile -t rag-core-inference-test:t17-cpu . *> .local/t17-build-cpu-final.log`.
Actual image manifest `sha256:566b9caa5f3c28224f08ae67337453664f689347d4a70e6604ea8d0191886c16`,
Python3.12.13, non-root10001, locked CPU group, no model files in image.
Seed command created `rag-core_model_cache` then copied from bind-read-only workspace
`.local/models` using Python3.12.13 helper in new empty volume, refusing nonempty target,
exit0 `MODEL CACHE COPIED; verification remains required in runtime`. No source/other volume
deleted. Runtime full cache checksum verified, model volume read-only.

CPU command exit0, `.local/t17-cpu-smoke1.log`:

```powershell
docker run --rm --init --network none --memory=7g --cpus=2 --mount type=volume,source=rag-core_model_cache,target=/models,readonly rag-core-inference-test:t17-cpu python scripts/smoke_inference.py --spawn *> .local/t17-cpu-smoke1.log
```

Actual excerpt (ready JSON abbreviated to fields actually emitted):

```text
device=cpu pid=8 active_jobs=0 capacity=32 model_instances=2 inference_processes=1
fingerprint=f25d7370e6e501a36aaba4da5c487ea790909d1a400d410e01f32348c34f534b
load_seconds=28.59250352300296 warmup_seconds=2.3855132530006813 startup_seconds=30.97802516900265
HTTP embed latency_seconds=0.363
HTTP rerank latency_seconds=0.398
FOUR_CLIENT_SHARED_PID [8, 8, 8, 8]
FINAL_RESOURCES {"vram_allocated_bytes": 0, "vram_peak_reserved_bytes": 0}
SMOKE PASS elapsed_seconds=34.946 peak_process_tree_rss_bytes=3572674560 final_rss_bytes=3572674560
```

Expected: actual HTTP vectors/raw relevant scores, four independent HTTP clients share PID,
cancel then recovery/zero outstanding jobs, actual tokenizer limit422, validation does not
echo input, >1MiB body413, finite operation outcome. Actual all PASS. Peak3.327GiB RSS
is sampled50ms model process tree, not Docker cache/cgroup/full-stack10GiB/load20users gate.
One CPU owner with two fixed models, native slot1/batch2; no per-client model copy.
GPU smoke/final Compose/source-image/scope/docs/commit evidence follow below.

### Final acceptance / resume 2026-10-03 — DoD-1 CPU and GPU

Continued the same T17-A01 candidate/checkpoint, no code discarded, no new task/agent.
CPU final image CMD (exact command in `docker/inference.Dockerfile`):

```text
uv run --no-sync pytest tests/integration/test_model_inference.py -v -s --tb=short --basetemp=/tmp/models -o cache_dir=/tmp/pytest-cache
```

Executed in final CPU test image, actual real offline model volume `/models` read-only,
`MODEL_DEVICE=cpu`, Python3.12.13/Torch2.9.1+cpu/Flag1.3.5, memory7GiB/2CPU,
network none; exit0 `.local/t17-dod1-cpu-final.log`:

```text
REAL FULL BUDGET embed tokens=512 elapsed=3.944s PASS
REAL FULL BUDGET rerank tokens=768 elapsed=6.282s PASS
REAL CANCEL/TIMEOUT/RECOVERY PASS; shared native executor slots=1
REAL MODEL RESOURCES {'vram_allocated_bytes': 0, 'vram_peak_reserved_bytes': 0}
8 passed in 76.88s (0:01:16)
```

Additional first full-budget fixture check exit1 `.local/t17-full-budget.log` retained:
`AssertionError: assert 1019 == 512`, `assert 1528 == 768`, `2 failed, 6 deselected in 21.16s`.
Incorrect assumption that repeating `hello ` gives linear token count was corrected by
selecting fixture repetitions using actual pinned tokenizer lengths; exact512/768 and
limit+1 refusal remain enforced. No production truncation/token limit/gold relaxed.
Corrected host focused gate exit0 `.local/t17-full-budget2.log` `2 passed in 42.98s`;
final Linux CPU8/GPU8 gates include both cases.

GPU final command, exit0 `.local/t17-dod1-gpu-acceptance.log`:

```powershell
docker run --rm --network none --gpus all --memory 7g --cpus 2 -v rag-core_model_cache:/models:ro -e MODEL_CACHE=/models -e MODEL_DEVICE=cuda:0 rag-core-inference-test:t17-gpu uv run --no-sync pytest tests/integration/test_model_inference.py -v -s --tb=short --basetemp=/tmp/models -o cache_dir=/tmp/pytest-cache *> .local/t17-dod1-gpu-acceptance.log
```

```text
REAL MODEL LOAD seconds=22.792 device=cuda:0
runtime={'FlagEmbedding': '1.3.5', 'torch': '2.9.1+cu128', 'transformers': '4.57.6', 'tokenizers': '0.22.2', 'sentence-transformers': '5.1.2', 'peft': '0.17.1'}
fingerprint=e48fa22cdf955a46390b9fb1aa33a947d1d327d86bbc3fde618a1b9eee99c6b1
REAL EMBED elapsed=2.979s dense=1024 sparse_counts=[8, 9, 9] cross_language=0.7212 distractor=0.3706
REAL RERANK elapsed=3.622s raw_scores=(4.15234375, -11.03125)
REAL RERANK elapsed=0.041s raw_scores=(5.88671875, -11.03125)
REAL FULL BUDGET embed tokens=512 elapsed=0.053s PASS
REAL FULL BUDGET rerank tokens=768 elapsed=0.061s PASS
REAL CANCEL/TIMEOUT/RECOVERY PASS; shared native executor slots=1
REAL MODEL RESOURCES {'vram_allocated_bytes': 2292524032, 'vram_peak_reserved_bytes': 2334130176}
8 passed in 30.23s
```

Expected dense1024/unit norm/finite values, sparse actual token IDs/positive weights,
EN/VI relevant>irrelevant, raw rerank ordering, no silent truncation, actual native
cancel/timeout/slot/recovery and configured budgets. Actual all PASS, no fake/skip.

Resume initially found previous `.local/t17-dod1-gpu-final.log` empty; no success claimed.
One newly launched invocation accidentally used `RAG_MODEL_CACHE`/`RAG_INFERENCE_DEVICE`
instead of the implemented `MODEL_CACHE`/`MODEL_DEVICE`:

```powershell
docker run --rm --network none --gpus all --memory 7g --cpus 2 -v rag-core_model_cache:/models:ro -e RAG_MODEL_CACHE=/models -e RAG_INFERENCE_DEVICE=cuda:0 -e UV_NO_SYNC=1 rag-core-inference-test:t17-gpu python -m pytest -q -s tests/integration/test_model_inference.py *> .local/t17-dod1-gpu-final.log
```

Default CPU confirmed with `docker exec suspicious_kalam printenv MODEL_DEVICE` →`cpu`.
Stopped only this owned T17 container via `docker stop --time 10 suspicious_kalam`
exit0 `suspicious_kalam`; test exit137 from explicit stop, log retained, not GPU PASS.
Correct invocation above is the GPU acceptance. Docker startup was slow after resume;
no Docker daemon restart, prune or unrelated container/volume mutation performed.
Automatic approval review rejected a proposed full-container-environment print due to
possible credential exposure; no environment printed. Safer single `MODEL_DEVICE`
inspection succeeded. A Go-template attempt to select that one variable failed1
`template parsing error: ... bad character U+003D '='`; corrected with `printenv MODEL_DEVICE`.
No blocked approval remains.

### Final DoD-2 CPU/GPU HTTP, resources and shared ownership

CPU final smoke command exit0 `.local/t17-cpu-smoke-close.log`:

```powershell
docker run --rm --init --network none --memory=7g --cpus=2 --mount type=volume,source=rag-core_model_cache,target=/models,readonly rag-core-inference-test:t17-cpu python scripts/smoke_inference.py --spawn *> .local/t17-cpu-smoke-close.log
```

Actual ready fields and output:

```text
device=cpu pid=8 active_jobs=0 capacity=32 model_instances=2 inference_processes=1
fingerprint=f25d7370e6e501a36aaba4da5c487ea790909d1a400d410e01f32348c34f534b
load_seconds=23.5780972270004 warmup_seconds=1.4956517460013856 startup_seconds=25.073754554003244
HTTP embed latency_seconds=0.504
HTTP rerank latency_seconds=0.434
FOUR_CLIENT_SHARED_PID [8, 8, 8, 8]
FINAL_RESOURCES {"vram_allocated_bytes": 0, "vram_peak_reserved_bytes": 0}
SMOKE PASS elapsed_seconds=28.850 peak_process_tree_rss_bytes=3568619520 final_rss_bytes=3569012736
```

Peak is model-process-tree RSS sampled50ms; final RSS may exceed sampled peak slightly.
GPU final smoke command exit0 `.local/t17-gpu-smoke-close.log`:

```powershell
docker run --rm --init --gpus all --network none --memory=7g --cpus=2 -e MODEL_DEVICE=cuda:0 --mount type=volume,source=rag-core_model_cache,target=/models,readonly rag-core-inference-test:t17-gpu python scripts/smoke_inference.py --spawn *> .local/t17-gpu-smoke-close.log
```

```text
device=cuda:0 pid=8 active_jobs=0 capacity=32 model_instances=2 inference_processes=1
fingerprint=e48fa22cdf955a46390b9fb1aa33a947d1d327d86bbc3fde618a1b9eee99c6b1
load_seconds=26.77680169999985 warmup_seconds=8.533143319999908 startup_seconds=35.310270283000136
HTTP embed latency_seconds=0.160
HTTP rerank latency_seconds=0.034
FOUR_CLIENT_SHARED_PID [8, 8, 8, 8]
GPU_VRAM_USED_MIB 3782 CUDA 12.8
FINAL_RESOURCES {"vram_allocated_bytes": 2282955776, "vram_peak_reserved_bytes": 2306867200}
SMOKE PASS elapsed_seconds=43.789 peak_process_tree_rss_bytes=4664487936 final_rss_bytes=1922301952
```

Expected/actual PASS: real HTTP2text embedding/2pair raw rerank, four independent clients
same model PID, remote cancel/recovery/zero outstanding jobs, overlimit422, sanitized422
without caller text and body413. Both model revisions/cache verified on every startup;
CPU/GPU fingerprints differ deliberately for precision/runtime/device. No model copy per
client/API worker. Native slot1/model batch2; priority/reserved queue behavior separately
verified by scheduler tests. GPU peak reserved2.148GiB; nvidia-smi total3.693GiB includes
other host GPU users. Synthetic tiny-fixture latency/resources are not full-stack/corpus/
20user/p95/SLA evidence. Native kernels only cooperatively cancel between batches.

### Compose/profile and exact image proof

Each configuration check exit0/no output:

```powershell
docker compose --profile inference config --quiet
docker compose -f compose.yaml -f compose.gpu.yaml --profile inference config --quiet
```

CPU up command exit0 `.local/t17-compose-cpu.log`:
`docker compose --profile inference up -d --no-build --wait --wait-timeout 180 inference`.
Actual `rag-core-inference-1` healthy, no host port; readyPID7/CPU fingerprint above,
load23.181791537994286/warmup3.7952118709945353/startup26.97701052499906,
RSS3562618880B. Inspect actual
`10001:10001 | {} | 7516192768 | 2000000000 | rag-core_model_cache RW=false`.
`docker compose --profile inference stop inference` exit0. CPU then GPU, no dual owners.

GPU up command exit0 `.local/t17-compose-gpu.log`:

```powershell
docker compose -f compose.yaml -f compose.gpu.yaml --profile inference up -d --no-build --wait --wait-timeout 180 inference *> .local/t17-compose-gpu.log
docker compose -f compose.yaml -f compose.gpu.yaml --profile inference ps inference
docker compose -f compose.yaml -f compose.gpu.yaml exec -T inference python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8080/health/ready').read().decode())"
docker inspect rag-core-inference-1 --format '{{.Config.User}} | {{json .HostConfig.PortBindings}} | {{.HostConfig.Memory}} | {{.HostConfig.NanoCpus}} | {{json .HostConfig.DeviceRequests}} | {{range .Mounts}}{{.Name}} RW={{.RW}}{{end}}'
docker compose -f compose.yaml -f compose.gpu.yaml --profile inference stop inference
```

All exit0; actual output excerpts, ready metadata fields abbreviated:

```text
Container rag-core-inference-1 Healthy
rag-core-inference-1 rag-core-inference:t17-gpu inference Up About a minute (healthy) PORTS=<empty>
status=ready pid=7 model_instances=2 inference_processes=1 active_jobs=0 capacity=32 device=cuda:0
fingerprint=e48fa22cdf955a46390b9fb1aa33a947d1d327d86bbc3fde618a1b9eee99c6b1
startup_seconds=30.246293197999876 load_seconds=23.01318720800009 warmup_seconds=7.23309678700025
resources={"vram_allocated_bytes":2282955776,"vram_peak_reserved_bytes":2306867200} rss_bytes=2806624256
10001:10001 | {} | 7516192768 | 2000000000 | [{"Capabilities":[["gpu"]],"Count":1,"DeviceIDs":null,"Driver":"nvidia","Options":null}] | rag-core_model_cache RW=false
Container rag-core-inference-1 Stopped
```

Compose warning retained: `volume "rag-core_model_cache" already exists but was not created
by Docker Compose. Use external: true to use an existing volume`. Acceptance manually
seeded this named volume once with verified host artifacts; missing Compose creation labels
does not change the mounted read-only volume. No volume deleted/recreated to suppress it.
Other services/Scarlet untouched, no server deployment.

Four final image IDs inspected/actually executed:

| Image | Manifest SHA-256 |
| --- | --- |
| rag-core-inference-test:t17-cpu | 644e23e5e27c4ec917fa106a785561e19fa621828990f8928c7ee7c579920317 |
| rag-core-inference:t17-cpu | 4b79b3c9e877d07eebef37c0d1e580f3a23708dad0e4380cfdba4f877cd6e2ac |
| rag-core-inference-test:t17-gpu | 8090758b3c63188644a9daaaaf0a5b0f6b66a671e2bc712b6a357a42f4b48856 |
| rag-core-inference:t17-gpu | 633de2ab095ea01199ad01152cc4a69e0e5b641812aca38e35e54e632b1ece59 |

GPU build logs `.local/t17-accept-gpu-build.log` / `.local/t17-gpu-runtime-build.log`
end at unpacking after manifest/tag publication; session transition lost final build exit.
Do not infer build exit0 from truncated logs. Final tag availability is proven by actual
GPU8tests/HTTP smoke/runtime Compose startup and content-hash comparison, no stale source.
CPU final build logs `.local/t17-accept-cpu-build.log` and runtime image verified likewise.

D5 current command exit0 `.local/t17-review-close.log`:
`$env:PYTHONIOENCODING='utf-8'; .venv/Scripts/python.exe .local/t17-review.py`.
Helper compares every55installed Python source against workspace SHA-256 in all four
offline containers; compares config/setup plus tests/smoke in test images; UTF-8/size/
27path scope/new private-key markers/local exact-secret-value checks without printing secrets.

```text
SOURCE_IMAGE_SHA256_EQUAL rag-core-inference-test:t17-cpu 55 Python files
CONFIG_SETUP_TEST_SMOKE_SHA256_EQUAL rag-core-inference-test:t17-cpu 4 files
SOURCE_IMAGE_SHA256_EQUAL rag-core-inference:t17-cpu 55 Python files
CONFIG_SETUP_TEST_SMOKE_SHA256_EQUAL rag-core-inference:t17-cpu 2 files
SOURCE_IMAGE_SHA256_EQUAL rag-core-inference-test:t17-gpu 55 Python files
CONFIG_SETUP_TEST_SMOKE_SHA256_EQUAL rag-core-inference-test:t17-gpu 4 files
SOURCE_IMAGE_SHA256_EQUAL rag-core-inference:t17-gpu 55 Python files
CONFIG_SETUP_TEST_SMOKE_SHA256_EQUAL rag-core-inference:t17-gpu 2 files
PASS exact27files UTF8/size/no private-key markers/local secret values; models/cache/logs absent
```

Existing historical key-marker quotations are compared with HEAD counts, not deleted;
no new marker or exact local credential value found. Model weights/cache/logs/corpus/
scratch are ignored and not task candidates. No public API/DB schema migration; next
T18/T19 must use model fingerprint as index revision/new generation, never silent overwrite.
Internal callers must authorize current-session scope before supplying model text.

### Final D1–D6 closure

D1 PASS: read dependency notes and plan, preserved baseline scratch, reviewed exact27paths,
`git diff --check` exit0. No prompt/AGENTS/plan/Scarlet/history rewrite.
D2 PASS: full361regression and29real parser/source tests above; final21scheduler/client
cases include malformed non-dict/non-string remote errors. Final Ruff/mypy commands each
exit0 `.local/t17-ruff-close.log` / `.local/t17-mypy-close.log`:

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; uv run --no-sync ruff check . *> .local/t17-ruff-close.log
uv run --no-sync mypy src *> .local/t17-mypy-close.log
uv lock --check --offline
uv run --no-sync python scripts/export_openapi.py --check
```

```text
All checks passed!
Success: no issues found in 55 source files
Resolved 169 packages in 45ms
PASS designed_operations=13 served_health_routes=2 synthetic_examples=37
PASS OpenAPI model + Draft2020-12 schemas=48; examples JSON Schema + Pydantic
CONTRACT EXPORT: PASS (business endpoints unmounted; no runtime query/stream verification)
```

Ruff has inherited inaccessible scratch warnings. An ignored helper edit initially failed
Python quoting (`SyntaxError: unexpected character after line continuation character`),
corrected via direct file patch; source/test/gates unaffected. Optional isolated uv dry-run
failed a user-level Python lock permission; actual locked sync and offline lock check PASS,
no runtime/package change based on the diagnostic failure.
D3 PASS: separate real CPU/GPU DoD-1 and CPU/GPU HTTP/resource DoD-2 above.
D4: README/RUNBOOK/task/handoffs/summary updated, docs validator output appended at staging.
D5 PASS: manual code/tests/transport/scheduler/cache/lock/Compose review and exact hashes/
secrets checks above. Safe internal errors/no text cache or unscoped retrieval path;
compatible HF/fsspec changes covered by real source regressions.
D6: explicit27task paths staging/cached inspection, completion commit
`feat(T17): add bounded multilingual model inference`, actual hash/commit paths/push/remote
equality reported after execution. COMPLETE only with successful inspected commit; if
commit fails task must remain unfinished. No self-hash/amend/force/merge/deploy.
No unresolved T17 blocker. T18 T17/T10 dependencies ready after inspected commit, T18 TODO;
**STOP AFTER T17**. Model/cache named volume retained, inference stopped.

### D4/D6 final documentation and stage boundary

Final focused unit command exit0 `.local/t17-closure-unit.log`:

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; uv run --no-sync pytest tests/unit/test_inference_scheduler.py tests/unit/test_model_client.py -q --tb=short --basetemp=.local/t17-closure-unit -o cache_dir=.local/t17-closure-cache *> .local/t17-closure-unit.log
```

Actual `21 passed in 0.40s`. No changed old test/gold/auth semantics.
First final docs invocation omitted the repository UV_CACHE_DIR and failed user cache
permission: `failed to open file ... uv/cache/sdists-v9/.git: Access is denied. (os error 5)`.
Correct cache setting, same docs validator command, exit0 `.local/t17-docs-close.log`:

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; uv run --no-sync python scripts/check_docs.py *> .local/t17-docs-close.log
```

```text
PASS UTF-8/nonempty Markdown: 14 files
PASS internal links/anchors: 314
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```

Exact27paths staged with structured argv (no wildcard); initial index must be empty.
Command: `.venv/Scripts/python.exe .local/t17-stage.py`. It runs
`git add -- <the27 explicit task paths>` and `git diff --cached --check`, verifies cached
path set equals the documented task set, then compares Git-filtered worktree object IDs
with each index blob (`git hash-object --path <path> <path>` vs `git rev-parse :<path>`).
Expected Git CRLF-to-LF warnings are not missing source; filters applied to comparison.
Actual scope/hash/whitespace results are reported before completion commit and actual
commit/push/hash verification after execution; no fabricated self-referential hash.

Completion task paths:

```text
README.md
RUNBOOK.md
docs/tasks.md
docs/handoffs.md
docs/implementation-summary.md
compose.yaml
compose.gpu.yaml
configs/model-artifacts.json
docker/inference.Dockerfile
docker/inference.Dockerfile.dockerignore
pyproject.toml
uv.lock
scripts/setup_models.py
scripts/smoke_inference.py
src/rag_core/adapters/models/__init__.py
src/rag_core/adapters/models/artifacts.py
src/rag_core/adapters/models/flag.py
src/rag_core/adapters/models/http.py
src/rag_core/domain/models.py
src/rag_core/ports/models.py
src/rag_core/inference/__init__.py
src/rag_core/inference/__main__.py
src/rag_core/inference/app.py
src/rag_core/inference/scheduler.py
tests/integration/test_model_inference.py
tests/unit/test_inference_scheduler.py
tests/unit/test_model_client.py
```

Final stage helper exit0 `.local/t17-stage.log`, actual output:

```text
27 files changed, 2896 insertions(+), 47 deletions(-)
PASS staged exact27 task paths / Git-filtered worktree=index / cached whitespace
```

After staging, `uv run --no-sync python scripts/check_docs.py` with workspace UV_CACHE_DIR
exit0, actual14files/314links/37tasks/81edges/acyclic PASS; `git diff --cached --check`
exit0/no output and `git diff --name-only` exit0/empty. Final source/image/secrets helper
same command exit0 `.local/t17-review-final.log`, all four source55/config/setup/test/smoke
hash comparisons and exact27scope/no new credential markers/local secret values PASS.
This evidence-only append is restaged and Git-filtered hashes/cached whitespace rechecked
before the completion commit. Actual commit/remote hashes returned post-commit; historical
scratch/cache/weights/logs remain outside staged scope. No unresolved T17 blocker.


<a id="h-t18-a01"></a>
## H-T18-A01 — Phase 3 / Scoped Qdrant repository, 2026-10-03

Direct Codex agent (GPT-6 family; exact model/effort unavailable), no subagents.
Every command CWD: `C:\Users\Admin\Documents\GitHub\rag-core`.
Baseline main/HEAD `919d4e43ab58158f1421982ae9dee6b95809396c`; authorized
`git ls-remote origin refs/heads/main` exit0 returned the same hash.
Read AGENTS/task-session prompt, T17/T10 COMPLETE notes and dependency interfaces/evidence,
P01/P04/P08/P13, checkpoint/implementation-summary/README/RUNBOOK. No prior T18 candidate.
Baseline untracked `.ptmp-t07-a02/`, `.tmp-t07-a02/` and permission warnings on inherited
`.pytmp-t07-a02/`, nested temp, `UsersAdminAppDataLocalTempt07a03/`, global Git ignore
preserved; no user scratch touched. Allowed12paths listed at D6 below.
T17 actual completion commit verified by HEAD/git log; older checkpoint's conditional
commit language is historical, not missing current T17 completion. User authorizes
scoped commit and origin/main push, no force/merge/deploy/Scarlet/task drain.

### Environment, retained diagnostics and real service setup

Host Python3.12.4, pytest9.1.1, qdrant-client1.19.0 already installed/locked; no new
dependency. PG17.11 and Qdrant1.19.1-unprivileged pinned digests from repo. No provider
or inference model called in T18; synthetic vectors are fixtures for real server isolation.
Full model CPU/GPU evidence remains T17, not claimed newly verified here.

All test/quality commands set `$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'`.
Real integration commands additionally set:

```powershell
$env:RAG_TEST_DATABASE_URL='postgresql://rag_core_test@127.0.0.1:55432/t10_acceptance'
$env:DATABASE_PASSWORD_FILE='.local/secrets/t10_postgres_password'
$env:RAG_TEST_QDRANT_URL='http://127.0.0.1:56333'
```

Existing T10 test secret retained, never printed. Fixtures create/drop only UUID-named
own test DBs and random-profile Qdrant collections. No existing data/volume deleted.
Initial sandbox `docker ps --format '{{.Names}} {{.Image}} {{.Ports}}'` could not access
Docker config/daemon pipe; scoped escalation succeeded, showed only other existing stacks,
which were untouched. No approval rejection or unresolved permission remains.

`docker compose -f compose.metadata-test.yaml -f compose.qdrant-test.yaml config --quiet`
exit0, no output. Initial `... up -d --wait postgres qdrant` exit1:

```text
container rag-core-metadata-test-qdrant-1 exited (1)
```

`docker compose -f compose.metadata-test.yaml -f compose.qdrant-test.yaml logs --no-color --tail 30 qdrant`
exit0, actual excerpt:

```text
Version: 1.19.1
Unable to check mmap functionality for storage path ./storage. Details: Data will be lost on system restart - tmpfs is memory-based, error: failed to open file `./storage/.qdrant_fs_check.tmp`: Permission denied (os error 13)
Error: Service internal error: Failed to write file: Permission denied (os error 13) at path "/qdrant/./storage/.atomicwriteBdqC02"
```

`docker image inspect qdrant/qdrant:v1.19.1-unprivileged --format '{{.Config.User}}'`
initially reported no tag (digest-pinned image already used); `docker run --rm --network none --entrypoint id qdrant/qdrant:v1.19.1-unprivileged`
exit0 after tag resolution to same digest, actual `uid=1000(qdrant) gid=1000(qdrant) groups=1000(qdrant)`.
Fixed only test tmpfs uid1000/gid1000/mode0700, kept non-root and no host-mounted data.
Corrected `docker compose -f compose.metadata-test.yaml -f compose.qdrant-test.yaml up -d --wait postgres qdrant`
exit0, actual `Container rag-core-metadata-test-postgres-1 Healthy` and
`Container rag-core-metadata-test-qdrant-1 Healthy`. Compose orphan warning for stopped
inherited registration-test Redis retained; no `--remove-orphans`/prune/delete used.

Initial focused Ruff found unsorted UUID import and unused UUID in new test (exit1),
fixed by focused `ruff check ... --fix` and format; initial mypy60PASS. Initial DoD17not
yet present: `.local/t18-dod1-initial.log` recorded13PASS11.97s. Added real detach tests
for fetch/anchor/neighbor expansion, actual PG lock-waiter proof and malformed/404 error
checks; `.local/t18-dod1.log` then17PASS11.93s. Review added rejection of quantized dense
and nonconfigured sparse index; final gates below apply to final source.
Intermediate docs command failed1 `Missing anchor ... docs/handoffs.md#h-t18-a01`
while evidence was pending; final docs check follows after this actual evidence append.
Read-only exploratory file/path searches returned missing paths before rg inventory;
no code/test input overwritten based on those diagnostics.

### DoD-1 — Real scoped dense/sparse/neighbor access

Expected: network Qdrant/PG, every candidate branch filtered before top-k, current
session-only exact pairs, empty scope no calls, stale/forged/raced scope rejected.
Actual command exit0; full final output `.local/t18-dod1-final.log`:

```powershell
uv run --no-sync pytest tests/integration/test_qdrant_scope.py -v -s --tb=short --basetemp=.local/18d -o cache_dir=.local/18cache *> .local/t18-dod1-final.log
```

```text
============================= test session starts =============================
platform win32 -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\Admin\Documents\GitHub\rag-core\.venv\Scripts\python.exe
cachedir: .local\18cache
rootdir: C:\Users\Admin\Documents\GitHub\rag-core
configfile: pyproject.toml
plugins: anyio-4.15.1, asyncio-1.4.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 17 items

tests/integration/test_qdrant_scope.py::test_isolation_every_branch_and_exact_pairs[dense] Real PostgreSQL: separate database t10_test_fd5cb9e989a74f79826f4cca73868011, public tables before migration=0
Real PostgreSQL: migrated separate database t10_test_fd5cb9e989a74f79826f4cca73868011
PASS dense: 2apps/2users/same-owner 2sessions, stale/crossed pairs, prefiltered top1/subset
PASSED
tests/integration/test_qdrant_scope.py::test_isolation_every_branch_and_exact_pairs[sparse] PASS sparse: 2apps/2users/same-owner 2sessions, stale/crossed pairs, prefiltered top1/subset
PASSED
tests/integration/test_qdrant_scope.py::test_isolation_every_branch_and_exact_pairs[hybrid] PASS hybrid: 2apps/2users/same-owner 2sessions, stale/crossed pairs, prefiltered top1/subset
PASSED
tests/integration/test_qdrant_scope.py::test_fetch_neighbors_and_languages PASS fetch/neighbor: scoped anchor + unit/ordinal/language; foreign chunk IDs return empty
PASSED
tests/integration/test_qdrant_scope.py::test_empty_scope_no_qdrant_request PASS empty allowed set: zero Qdrant query/scroll calls across all read methods
PASSED
tests/integration/test_qdrant_scope.py::test_pg_snapshot_is_authority[detach] PASS PG detach: stale/forged snapshot rejected before Qdrant; retained4vectors
PASSED
tests/integration/test_qdrant_scope.py::test_pg_snapshot_is_authority[delete] PASS PG delete: stale/forged snapshot rejected before Qdrant; retained4vectors
PASSED
tests/integration/test_qdrant_scope.py::test_pg_snapshot_is_authority[reindex] PASS PG reindex: stale/forged snapshot rejected before Qdrant; retained4vectors
PASSED
tests/integration/test_qdrant_scope.py::test_pg_snapshot_is_authority[forged] PASS PG forged: stale/forged snapshot rejected before Qdrant; retained4vectors
PASSED
tests/integration/test_qdrant_scope.py::test_detach_after_actual_query_rejects_result[query] PASS actual query completed then PG detach committed: no stale result returned
PASSED
tests/integration/test_qdrant_scope.py::test_detach_after_actual_query_rejects_result[fetch] PASS actual fetch completed then PG detach committed: no stale result returned
PASSED
tests/integration/test_qdrant_scope.py::test_detach_after_actual_query_rejects_result[neighbor-anchor] PASS actual neighbor-anchor completed then PG detach committed: no stale result returned
PASSED
tests/integration/test_qdrant_scope.py::test_detach_after_actual_query_rejects_result[neighbor-expansion] PASS actual neighbor-expansion completed then PG detach committed: no stale result returned
PASSED
tests/integration/test_qdrant_scope.py::test_idempotent_update_cleanup_and_retention PASS update/retry stableIDs count4; exact cleanup0; active/other owner retained4; new session empty
PASSED
tests/integration/test_qdrant_scope.py::test_publication_waits_for_acknowledged_write PASS PG publication blocked by generation write lock until actual Qdrant wait=true ack
PASSED
tests/integration/test_qdrant_scope.py::test_payload_corruption_and_real_dependency_failure PASS actual corrupted payload rejected; actual missing collection -> sanitized technical error
PASSED
tests/integration/test_qdrant_scope.py::test_collection_config_and_invalid_requests PASS dense1024 Cosine/sparse/noIDF/9payload indexes/versioned fingerprint; incompatible rejected
PASSED

============================= 17 passed in 10.38s =============================
```

### DoD-2 — Empty scope/idempotency/cleanup/collection semantics

Expected/actual PASS: zero empty-scope network reads, stable retry/update IDs and count4, cleanup only target inactive generation; active/other owner retained4; PG UPDATE blocked until actual ack, config validation and RUNBOOK reindex/retention documented.
Command exit0; actual output `.local/t18-dod2-final.log`:

```powershell
uv run --no-sync pytest tests/integration/test_qdrant_scope.py -k 'empty_scope or idempotent_update or publication_waits or collection_config' -v -s --tb=short --basetemp=.local/18e -o cache_dir=.local/18cache *> .local/t18-dod2-final.log
```

```text
============================= test session starts =============================
platform win32 -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\Admin\Documents\GitHub\rag-core\.venv\Scripts\python.exe
cachedir: .local\18cache
rootdir: C:\Users\Admin\Documents\GitHub\rag-core
configfile: pyproject.toml
plugins: anyio-4.15.1, asyncio-1.4.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 17 items / 13 deselected / 4 selected

tests/integration/test_qdrant_scope.py::test_empty_scope_no_qdrant_request Real PostgreSQL: separate database t10_test_724c95272c7b437f8dc5083cb92c24b0, public tables before migration=0
Real PostgreSQL: migrated separate database t10_test_724c95272c7b437f8dc5083cb92c24b0
PASS empty allowed set: zero Qdrant query/scroll calls across all read methods
PASSED
tests/integration/test_qdrant_scope.py::test_idempotent_update_cleanup_and_retention PASS update/retry stableIDs count4; exact cleanup0; active/other owner retained4; new session empty
PASSED
tests/integration/test_qdrant_scope.py::test_publication_waits_for_acknowledged_write PASS PG publication blocked by generation write lock until actual Qdrant wait=true ack
PASSED
tests/integration/test_qdrant_scope.py::test_collection_config_and_invalid_requests PASS dense1024 Cosine/sparse/noIDF/9payload indexes/versioned fingerprint; incompatible rejected
PASSED

====================== 4 passed, 13 deselected in 3.95s =======================
```

### D2 — Real dependency PG regression

Expected/actual PASS: existing scope/retention/concurrency and isolated empty migration reproduction remain intact;19tests.
Command exit0; actual output `.local/t18-pg-regression.log`:

```powershell
uv run --no-sync pytest tests/integration/test_session_scope.py tests/integration/test_metadata_migrations.py -q -s --tb=short --basetemp=.local/18p -o cache_dir=.local/18pcache *> .local/t18-pg-regression.log
```

```text
Real PostgreSQL: separate database t10_test_d4ee7d22263e4538b2d52c45924b5793, public tables before migration=0
Real PostgreSQL: migrated separate database t10_test_d4ee7d22263e4538b2d52c45924b5793
PASS isolation: app/user/current-session, explicit new registration, independent detach
...........PASS repeated/concurrent delete: one revision, retained rows byte-equivalent, no resurrection
.PASS real lock race: old coherent snapshot then revision invalidation; replay stays detached
......Real PostgreSQL: separate database t10_test_b53aef68b5714826a81bd8c5a433f9ba, public tables before migration=0
Real PostgreSQL: migrated separate database t10_test_b53aef68b5714826a81bd8c5a433f9ba
PASS separate empty PG migration -> repeat head -> downgrade base -> upgrade head: identical schema
.
19 passed in 5.56s
```

### D2 — Unit/contract/security regression

Expected/actual PASS363tests, no skipped tests or relaxed gate/gold/auth semantics.
Command exit0; actual output `.local/t18-regression.log`:

```powershell
uv run --no-sync pytest tests/unit tests/contract tests/security -q --tb=short --basetemp=.local/18r -o cache_dir=.local/18rcache *> .local/t18-regression.log
```

```text
........................................................................ [ 19%]
........................................................................ [ 39%]
........................................................................ [ 59%]
........................................................................ [ 79%]
........................................................................ [ 99%]
...                                                                      [100%]
363 passed in 112.65s (0:01:52)
```

### D2 — Quality, environment and unchanged API contracts

Each command below exit0; Ruff has inherited inaccessible-scratch warnings, not findings.
Mypy final source60PASS and Ruff rechecked after collection-validation review. Actual
sync included host CPU inference group to preserve the existing installed T17 environment;
an earlier **dry-run** without inference proposed uninstalling33model packages, no mutation
occurred from that diagnostic. Actual sync below kept current148installed packages.

```powershell
uv run --no-sync ruff check . *> .local/t18-ruff.log
uv run --no-sync mypy src *> .local/t18-mypy.log
uv sync --locked --offline --group dev --group api --group ingestion --group inference *> .local/t18-sync.log
uv lock --check --offline
uv run --no-sync python scripts/export_openapi.py --check
```

```text
All checks passed!
Success: no issues found in 60 source files
Resolved 169 packages in 1ms
Checked 148 packages in 60ms
Resolved 169 packages in 1ms
PASS checked docs/api/openapi-v1.designed.json
PASS checked docs/api/openapi.served.json
PASS checked docs/api/examples-v1.json
PASS designed_operations=13 served_health_routes=2 synthetic_examples=37
PASS OpenAPI model + Draft2020-12 schemas=48; examples JSON Schema + Pydantic
CONTRACT EXPORT: PASS (business endpoints unmounted; no runtime query/stream verification)
```

### D1/D4/D5 — Scope, docs, review and limitations

D1 PASS: reviewed task/dependencies and exact12paths; `git diff --check` exit0/no output.
No AGENTS/plan/prompt/corpus/Scarlet/default Compose/dependency/DB/public schema changes.
D3 PASS: individual DoD-1/DoD-2 actual gates above; no mock substitution/provider requirement.
D4: five living docs updated with verified/designed boundaries, README commands, RUNBOOK
profile/collection/payload/index/interfaces/budgets/reindex/retention/ack/cleanup/race rules.
D5 review: all new source/tests read; exact prefilters and PG revalidation on every read;
private SDK handle, no raw/unscoped search port; async SDK/PG, bounded I/O; no text in
payload/error logs. Scoped generation cleanup holds PG row locks and rejects active;
generation publication remains T19, no distributed atomicity claim. Pipeline must supply
stable T16 hard-boundary unit IDs and persist original chunks, revalidate again before
prompt/final. Fingerprint/model mismatches/config/errors fail technically, not insufficient.
No model quality/corpus/end-to-end ingestion/public query/provider/load claim from T18.
Future publication UPDATE locks same PG rows; do not hold own locking transaction while
calling adapter on another connection. Migration N/A: no schema change; index migration
uses new collection/generation, old active retained until validated publication.

Final actual service inspection before stopping, all exit0:

```powershell
docker compose -f compose.metadata-test.yaml -f compose.qdrant-test.yaml config --quiet
docker compose -f compose.metadata-test.yaml -f compose.qdrant-test.yaml ps postgres qdrant
docker inspect rag-core-metadata-test-qdrant-1 --format '{{.Config.User}} | {{json .HostConfig.Tmpfs}} | {{json .HostConfig.PortBindings}}'
docker compose -f compose.metadata-test.yaml -f compose.qdrant-test.yaml stop postgres qdrant
```

```text
rag-core-metadata-test-postgres-1 postgres:17.11-bookworm@sha256:051f7b7b3abdd564d5d1bd1e8c4b9c1b6e77087d1dd22020ede611c096a272e0 ... Up 8 minutes (healthy) 127.0.0.1:55432->5432/tcp
rag-core-metadata-test-qdrant-1 qdrant/qdrant:v1.19.1-unprivileged@sha256:801777072776dc81b2a9dd2007b2ed487571f21ecd30efffd15ddb1671f2193d ... Up 8 minutes (healthy) 127.0.0.1:56333->6333/tcp
1000:1000 | {"/qdrant/storage":"uid=1000,gid=1000,mode=0700"} | {"6333/tcp":[{"HostIp":"127.0.0.1","HostPort":"56333"}]}
Container rag-core-metadata-test-qdrant-1 Stopped
Container rag-core-metadata-test-postgres-1 Stopped
```

Whitespace formatting/columns elided in service table above; values are actual.
Test services stopped, inherited containers/network/volumes/sources untouched.
Exact12completion paths:

```text
README.md
RUNBOOK.md
docs/tasks.md
docs/handoffs.md
docs/implementation-summary.md
compose.qdrant-test.yaml
src/rag_core/domain/vectors.py
src/rag_core/ports/vectors.py
src/rag_core/adapters/persistence/vector_generations.py
src/rag_core/adapters/vectors/__init__.py
src/rag_core/adapters/vectors/qdrant.py
tests/integration/test_qdrant_scope.py
```

D6 completion subject `feat(T18): enforce scoped Qdrant access`; actual scoped staging,
secret/artifact/hash/docs checks below, inspected commit and authorized origin/main
push/equality reported after execution, no self-hash/amend/force/merge/deploy.
COMPLETE effective only after successful inspected commit. T19 dependencies T18/T12/T15/T16
ready after closure; STOP AFTER T18. No unresolved T18 blocker.

### Final D4/D5/D6 — Docs and exact staged candidate

Final docs command `uv run --no-sync python scripts/check_docs.py` with workspace
UV_CACHE_DIR exit0; actual output:

```text
PASS UTF-8/nonempty Markdown: 14 files
PASS internal links/anchors: 323
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```

The first whitespace check after append caught an accidental whitespace-only line2
in implementation-summary; removed it, `git diff --check` exit0 thereafter. This was
documentation whitespace only; final code/DoD tests unchanged. Git warns CRLF will
be normalized to LF for handoffs; content reviewed with Git filters, no encoding loss.

Explicit staging/review command `.venv/Scripts/python.exe .local/t18-stage.py` exit0.
Helper invokes `git add -- <the exact12paths listed above>` (no wildcard), checks
cached path equality/whitespace/UTF8, compares Git-filtered worktree blob hashes to
index blobs, scans exact local secret bytes without printing them and rejects new
private-key markers relative to HEAD. Actual output before this evidence-only append:

```text
12 files changed, 1637 insertions(+), 8 deletions(-)
PASS exact12 task paths / UTF8 / no local secret values or new private-key markers / Git-filtered worktree=index / cached whitespace
PASS no tracked unstaged changes; inherited scratch/cache/logs/secrets absent from index
```

Read/reviewed all12task files and staged changes. Git author already configured and
unchanged. New source/config/test/README/RUNBOOK and dependency scope reviewed; no
secrets/raw licensed data/model weights/cache/scratch or .local helper/logs included.
D1–D5 PASS with individual evidence above. Restage this append, rerun docs and exact
stage/hash/whitespace check, then D6 create `feat(T18): enforce scoped Qdrant access`,
inspect actual commit12paths with `git show --check`, and authorized `git push origin main`.
Compare actual HEAD against `git ls-remote origin refs/heads/main`; post-execution hash
and outcome go in direct user report, not fabricated self-hash inside this commit.


<a id="h-t19-a01"></a>
## H-T19-A01 — Phase 3 / durable ingestion and atomic publication

- Started 2026-10-03 Asia/Bangkok. Direct Codex agent, exact model/effort unavailable;
  no subagents. Cwd for every command: `C:/Users/Admin/Documents/GitHub/rag-core`.
  Baseline main/969b402e9f21e4ca38bea4f37f7c23839078eeec; origin/main same. User
  authorizes scoped commit/push, no merge/deploy/drain. Inherited T07 scratch retained.
- Read AGENTS/session prompt/T19/dependency execution notes T18/T12/T15/T16 and
  interfaces T10/T11/T13/T14/T17, P01/P04/P07/P12/P13, living docs/checkpoint before code.
- Initial sandbox Docker pipe access denied and git remote could not connect.
  Scoped escalation succeeded: remote output
  `969b402e9f21e4ca38bea4f37f7c23839078eeec refs/heads/main`. Unrelated Scarlet running;
  no operation against it. Real acceptance uses separate rag-core-ingestion-test project.
- `uv lock --offline` + locked sync dev/api/ingestion: PASS169packages. Initial mypy
  without inference group failed3existing Torch/Flag imports. Restored locked inference
  group; no source gate reduction. `uv run --no-sync mypy src` exit0:
  `Success: no issues found in 68 source files`. Ruff exit0 `All checks passed!`
  with inherited scratch ACL warnings. OpenAPI --check exit0 unchanged13designed/
  2served/37examples/48schemas. Windows inline documentation append quoting failed
  SyntaxError exit1 (no file mutation); switched to local UTF-8 script.
- `uv run --no-sync pytest tests/unit tests/contract tests/security -q --tb=short
  --basetemp=.local/19r1 -o cache_dir=.local/19rc1` exit0:
  `363 passed in 130.90s (0:02:10)`. Full synthetic log `.local/t19-regression.log`.
- Docker config/up started separate PG17.11/Redis8.10.1/Qdrant1.19.1/pinned MinIO/
  CPU BGE-M3 service, MinIO provisioner exit0. One concurrent build failed exit1:
  `ERROR: failed to build: failed to solve: frontend grpc server closed unexpectedly`
  (`.local/t19-build-current.log`). Sequential second/third builds exit0; own inference
  temporarily stopped while building, then healthy. Removed recursive chown /app;
  UID10001 runtime uses readable root-owned install and temp-only writes. No volume deletion.
- DoD-1 initial run in progress: actual scan PDF/XLSX/TXT Celery prefork ingestion
  ready with1chunk each, Vietnamese OCR phrase preserved, original object/file SHA
  unchanged, real source locators; case20.489s / peak1240.090MiB / shared model PID7.
  Remaining gates and final D1–D6 pending; no completion commit yet.

### Failure correction and final acceptance — DoD-1

The first actual run `docker compose -f compose.ingestion-test.yaml run --rm ingestion-tests`
ended exit2 after SIGINT of the task's test container: `.local/t19-dod1-initial.log`.
The scan/XLSX/text case passed; duplicate claim waited behind Qdrant's generation/version
lock until the intentionally held HTTP ACK timed out. Actual failure excerpt:

```text
test_duplicate_pending_generation_invisible
assert await task == "ready"
E AssertionError: assert 'vector_depen...y_unavailable' == 'ready'
1 failed, 1 passed in 316.85s (0:05:16)
```

Fixed fast queued-state claim check (locked recheck still arbitrates races) and moved
heartbeat to session/job locks so slow bounded Qdrant I/O does not block lease renewal.
Replaced the CPU-heavy long text multi-batch fixture with34 XLSX sheets producing34
actual structural chunks; same batch32/partial ACK/failure/reindex gate, no model fake
or scope/gate reduction. The interrupted third case is not a PASS. Second real suite
exit0 `.local/t19-dod1-second.log`: `12 passed in 112.39s (0:01:52)`.

**Final DoD-1 command**, cwd `C:/Users/Admin/Documents/GitHub/rag-core`:

```powershell
docker compose -f compose.ingestion-test.yaml run --rm ingestion-tests
```

Container command: `uv run --no-sync pytest tests/integration/test_ingestion_pipeline.py
-v -s --tb=short --basetemp=/tmp/ingestion-tests -o cache_dir=/tmp/pytest-cache`.
Exit0; full synthetic log `.local/t19-dod1-final.log`. Expected: all named real
ingestion/fault/retry/retention/publication gates pass, no service/model success mock.
Actual output excerpts:

```text
Real PostgreSQL: migrated separate database t10_test_4ceff503043141819b7a161ccb78d9f2
{"job": "280506d0-1a2e-47cc-8a11-f3a50a28d06a", "state": "ready", "chunks": 1, "locator": {"kind": "pdf", "page": 1, "block": 0, "offsets": {"end": 5, "start": 0}, "printed_page_label": "1"}, "excerpt": "Doanh thu quý một đạt 120 triệu đồng."}
REAL reindex: initial multi-batch source ingestion
REAL reindex: acknowledged first batch, next write forced HTTP503
REAL reindex: retry new generation with retained old publication
{"job": "88284cf6-ebf5-4328-bd93-96c5feafae61", "state": "ready", "chunks": 34, "locator": {"kind": "xlsx", "unit": null, "sheet": "Quarter 0", "headers": ["Quarter\tRevenue (million VND)"], "cell_range": "A1"}, "excerpt": "Quarter\tRevenue (million VND)\n0\t120"}
REAL detach during indexing: cancelled, attached_links=0, chunks retained
REAL delete during indexing: cancelled, attached_links=0, chunks retained
REAL Celery worker killed exit=-9; expired lease fenced, resume attempts=2
PASSEDREAL ingestion case elapsed=27.105s test_container_peak_mib=1342.242 shared_model_pid=7
REAL retry budget: attempts=3, failed, durable events=3, further retry denied
12 passed in 106.74s (0:01:46)
```

All12actual tests include VI scanned PDF, XLSX cell B2/source segments, TXT/real Celery
prefork, duplicate/staging invisibility + live lease renewal during gated ACK, acknowledged
first32points + HTTP503 on second batch + failed scoped generation cleanup32→0 while
old ready34 retained + successful retry34, checksum-only changed source refusal,
detach/delete retention/no resurrection, actual process group SIGKILL/recovery through
Redis/outbox, missing acknowledged vector rejection, partial OCR refusal before model,
max3retry/outbox enforcement, and staged PG text/source-map tamper rejection. Source
file/object SHA checks and direct actual retained vector count checks pass. All random
fixture databases created/migrated and dropped separately from application DB.

Actual services: PG17.11, Redis8.10.1, Qdrant1.19.1, MinIO RELEASE.2025-07-23T15-54-02Z,
pinned images in compose.ingestion-test.yaml; real BGE-M3+multilingual reranker CPU
T17 image, one model process PID7/two fixed models. Actual model fingerprint
`f25d7370e6e501a36aaba4da5c487ea790909d1a400d410e01f32348c34f534b`;
FlagEmbedding1.3.5/Torch2.9.1+cpu/Transformers4.57.6/tokenizers0.22.2,
sentence-transformers5.1.2/peft0.17.1; actual Tesseract5.3.0 with eng/vie/osd.
Real test config: lease10s/heartbeat1s, CPU model cache mounted read-only, worker2GiB/2CPU,
inference7GiB/2CPU. Test-container peak1342.242MiB includes parser subprocesses;
this is fixture observation, not20user/full-stack SLA or corpus-quality benchmark.
MinIO reader IAM is separate from fixture uploader; core does only HEAD/GET.

### Separate DoD-2 — visibility, source/retention and reports

Command from same cwd, exit0, `.local/t19-dod2-final.log`:

```powershell
docker compose -f compose.ingestion-test.yaml run --rm ingestion-tests uv run --no-sync pytest tests/integration/test_ingestion_pipeline.py -k 'scan_xlsx or visibility or duplicate_pending' -v -s --tb=short --basetemp=/tmp/ingestion-visibility -o cache_dir=/tmp/pytest-cache
```

Expected: ready-only scoped repository visibility; unchanged source SHA, no delete/detach
link resurrection, actual retained PG chunks/Qdrant vectors; ready job/count/locator
reports and README/RUNBOOK real flow. Actual output excerpts:

```text
collecting ... collected 12 items / 8 deselected / 4 selected
{"job": "455f0c21-e728-4b0a-a3c5-b8bb0eef7e26", "state": "ready", "chunks": 1, "locator": {"kind": "pdf", "page": 1, "block": 0, "offsets": {"end": 5, "start": 0}, "printed_page_label": "1"}, "excerpt": "Doanh thu quý một đạt 120 triệu đồng."}
{"job": "abeea78c-12f5-4a9f-ba47-0e648a68f5f2", "state": "ready", "chunks": 1, "locator": {"kind": "xlsx", "unit": null, "sheet": "Revenue VND", "headers": ["Quarter\tRevenue (million VND)"], "cell_range": "A1"}, "excerpt": "Quarter\tRevenue (million VND)\nQ1\t120\nQ2\t150"}
REAL detach during indexing: cancelled, attached_links=0, chunks retained
REAL delete during indexing: cancelled, attached_links=0, chunks retained
PASSEDREAL ingestion case elapsed=3.032s test_container_peak_mib=1182.871 shared_model_pid=7
4 passed, 8 deselected in 39.02s
```

Visibility through actual T18 scoped vector/PG repositories, public HTTP/query still
unmounted. Source hashes/counts/cell B2/source maps are asserted against actual source;
logs show synthetic excerpts only. Documentation now VERIFIED with acceptance commands,
operators' config/cache/IAM/migration prerequisites, fences/backoff/cleanup/retention.

### D1/D2/D3 — scope, quality and dependency services

All commands cwd repo above; host UV_CACHE_DIR set to absolute workspace `.uv-cache`.

```powershell
uv run --no-sync pytest tests/unit tests/contract tests/security -q --tb=short --basetemp=.local/19r1 -o cache_dir=.local/19rc1
```

Exit0 `.local/t19-regression.log`: `363 passed in 130.90s (0:02:10)`.
Separate real dependency services started with
`docker compose -f compose.metadata-test.yaml -f compose.qdrant-test.yaml up -d --wait postgres qdrant`
exit0. RAG_TEST_DATABASE_URL=`postgresql://rag_core_test@127.0.0.1:55432/t10_acceptance`,
DATABASE_PASSWORD_FILE workspace `.local/secrets/t10_postgres_password` (value never printed),
RAG_TEST_QDRANT_URL=`http://127.0.0.1:56333`. Command:

```powershell
uv run --no-sync pytest tests/integration/test_session_scope.py tests/integration/test_metadata_migrations.py tests/integration/test_qdrant_scope.py -v -s --tb=short --basetemp=.local/19p1 -o cache_dir=.local/19pc1
```

Exit0 `.local/t19-dependency-services.log` actual excerpts:

```text
PASS update/retry stableIDs count4; exact cleanup0; active/other owner retained4; new session empty
PASS PG publication blocked by generation write lock until actual Qdrant wait=true ack
PASS dense1024 Cosine/sparse/noIDF/9payload indexes/versioned fingerprint; incompatible rejected
36 passed in 20.52s
```

Migration test includes clean upgrade/repeat/downgrade/reupgrade with identical actual
schema/FKs/checks/indexes, including chunks/fencing migration0003. Existing protected
AGENTS/plan/corpus check `git diff --quiet -- AGENTS.md docs/plan.md corpus-documents` exit0.
`git diff --check` exit0 after doc edits, inherited T07 ACL warnings/scratch untouched.

Quality commands all exit0 (logs `.local/t19-{ruff,mypy,lock,openapi}-final.log`):

```text
uv run --no-sync ruff check .
All checks passed!
uv run --no-sync mypy src
Success: no issues found in 68 source files
uv lock --check --offline
Resolved 169 packages in 31ms
uv run --no-sync python scripts/export_openapi.py --check
PASS designed_operations=13 served_health_routes=2 synthetic_examples=37
PASS OpenAPI model + Draft2020-12 schemas=48; examples JSON Schema + Pydantic
CONTRACT EXPORT: PASS (business endpoints unmounted; no runtime query/stream verification)
```

PowerShell redirection wraps native stderr progress/warnings in NativeCommandError
decorations in some logs; recorded native exit codes are0, these are not test failures.
Initial Ruff test style/duplicate import findings fixed; final gate unchanged.

### D4/D5 — living docs, reproducible runtime, reviewed boundaries

README/RUNBOOK/tasks/handoffs/implementation-summary updated together. Closure doc
helper initially hit an overlapping replacement assertion after updating README/RUNBOOK;
fixed ordering and reran successfully (no code/test/gate changes). Fixed an accidental
single-backtick RUNBOOK fence to proper Markdown. Final docs/explicit review output
appended below. Historical attempt evidence retained.

`docker compose config --quiet` and
`docker compose -f compose.ingestion-test.yaml config --quiet` exit0.
Sequential final test image build exit0 `.local/t19-build-final.log`;
`docker compose build worker dispatcher` exit0 `.local/t19-runtime-build.log`:
`Image rag-core-dispatcher:t19 Built`, `Image rag-core-worker:t19 Built`.
`.venv/Scripts/python.exe .local/t19-image-check.py` exit0,
full output `.local/t19-image-proof.log`:

```text
PASS rag-core-worker:t19: 68 installed source hashes equal, uid10001, Python3.12.13, no Torch
PASS rag-core-dispatcher:t19: 68 installed source hashes equal, uid10001, Python3.12.13, no Torch
PASS rag-core-ingestion-test:t19: 68 installed source hashes equal, uid10001, Python3.12.13, no Torch
PASS worker packaged migration0003
```

New schema additive; operator backups/manual upgrade documented. No API contract
changes. Dependencies'169locked versions unchanged; HTTPX already present, uv lock
normalized NVIDIA extras markers. Worker no inference group/weights. Config examples
are trusted operator data, no credentials. Language und until trusted annotation;
no cross-registration computation reuse, conservative neighbor unit; no public route,
corpus benchmark/LLM provider/Scarlet/server deployment claim. No unresolved T19 blocker.

Task services stopped, both commands exit0:

```powershell
docker compose -f compose.ingestion-test.yaml stop
docker compose -f compose.metadata-test.yaml -f compose.qdrant-test.yaml stop postgres qdrant
```

Actual output `.local/t19-stop-ingestion.log` / `.local/t19-stop-metadata.log`:
`rag-core-ingestion-test-inference-1 Stopped`, postgres/redis/qdrant/minio/storage-fixture
Stopped; `rag-core-metadata-test-postgres-1 Stopped`, qdrant Stopped. No down-v,
no application/source/model cache volume deletion, unrelated Scarlet untouched.

### D6 — completion boundary

Completion subject `feat(T19): complete durable document ingestion`. Exact scoped
stage/scope/secret/hash/whitespace/docs review below; COMPLETE is effective only after
successful inspected commit. Actual hash and user-authorized `git push origin main`
plus HEAD/remote equality returned after execution, no fabricated self-hash/amend.
T20 dependencies T19/T03/T10 ready after closure; T20 remains TODO. STOP AFTER T19.

### Final D4/D5/D6 review and exact task paths

Final docs check `uv run --no-sync python scripts/check_docs.py` exit0
(`.local/t19-docs-final.log`, before removing one duplicate sentence):

```text
PASS UTF-8/nonempty Markdown: 14 files
PASS internal links/anchors: 336
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```

Initial explicit31path stage/review helper exit0 `.local/t19-stage-final.log`:

```text
PASS exact31 task files UTF8/size/no local secret values/JWT/new key markers; 169 locked versions unchanged; AGENTS/plan/corpus unchanged
PASS staged exactly31paths, cached whitespace, Git-filtered worktree=index; no tracked unstaged changes; scratch/logs/secrets/cache absent from index
```

Final staged document review removed a duplicated README evidence sentence and
remaining T19 in-progress wording. Review identified the new Compose development
HTTP flag lacked negative config tests. Added one task security test file (final32
paths) proving only explicitly opted-in minio:9000 origin is allowed, arbitrary
host/port/metadata IP/credentials/path/query/fragment rejected, and production denies
both development flags even on HTTPS. No runtime source/config/model changes.
Separate command exit0 `.local/t19-storage-security.log`:

```powershell
uv run --no-sync pytest tests/security/test_ingestion_storage_config.py -v --tb=short --basetemp=.local/19s1 -o cache_dir=.local/19sc1
```

Actual `12 passed in 0.67s`; preceding363regression remain a separate run, no fabricated
375count. `uv run --no-sync ruff check .` exit0 `.local/t19-ruff-review.log`:
`All checks passed!` (inherited scratch ACL warnings only). Mypy68/images/real DoD
code unchanged. Final docs + exact32stage helper rerun after this append.

Exact authorized task paths, no broad git add:

```text
.env.example
README.md
RUNBOOK.md
compose.yaml
compose.ingestion-test.yaml
configs/storage.compose.example.json
configs/worker.example.json
docker/worker.Dockerfile
docker/worker.Dockerfile.dockerignore
docs/handoffs.md
docs/implementation-summary.md
docs/tasks.md
migrations/versions/0003_ingestion_publication.py
pyproject.toml
uv.lock
src/rag_core/adapters/broker/dispatcher.py
src/rag_core/adapters/persistence/ingestion.py
src/rag_core/adapters/persistence/vector_generations.py
src/rag_core/adapters/storage/s3.py
src/rag_core/adapters/vectors/qdrant.py
src/rag_core/application/__init__.py
src/rag_core/application/ingestion.py
src/rag_core/domain/ingestion.py
src/rag_core/ports/ingestion.py
src/rag_core/ports/vectors.py
src/rag_core/workers/__init__.py
src/rag_core/workers/celery.py
src/rag_core/workers/runtime.py
tests/integration/conftest.py
tests/integration/test_ingestion_pipeline.py
tests/integration/test_metadata_migrations.py
tests/security/test_ingestion_storage_config.py
```

Read/reviewed code/tests/diffs, additive migration/FKs/legacy compatibility, async
offload/cancel/lease locks, actual vector reconciliation, shared model/Compose boundaries,
operator examples and docs. Git author already configured, unchanged. Stage helper
compares exact local credential bytes without printing them, rejects JWT/new private
key markers and oversized artifacts, checks169locked versions unchanged, protected
AGENTS/plan/corpus unchanged, then exact32path cached set/whitespace/UTF8/filtered blob
equality and no tracked unstaged changes. No raw restricted corpus/models/weights/logs/
secrets/ignored helpers/T07 scratch in index. Completion subject and inspected commit
are D6; actual commit/hash and authorized remote equality reported after execution.

Final closure docs command above exit0 `.local/t19-docs-closure.log`:

```text
PASS UTF-8/nonempty Markdown: 14 files
PASS internal links/anchors: 335
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```

Final `.venv/Scripts/python.exe .local/t19-stage.py` exit0,
`.local/t19-stage-closure.log`, actual output before this evidence-only append:

```text
PASS exact32 task files UTF8/size/no local secret values/JWT/new key markers; 169 locked versions unchanged; AGENTS/plan/corpus unchanged
32 files changed, 2144 insertions(+), 77 deletions(-)
PASS staged exactly32paths, cached whitespace, Git-filtered worktree=index; no tracked unstaged changes; scratch/logs/secrets/cache absent from index
```

Restage this evidence-only append with same exact32path checks, run docs/whitespace
again, create inspected completion commit, push origin/main and compare remote hash.
All D1–D5 and individual DoD gates PASS; D6 depends on actual successful commit.

<a id="h-t20-a01"></a>
## H-T20-A01 — Phase 4 / domain registry, scoped preparation and conversation

Runtime: direct Codex agent/no subagents; exact model/effort unavailable. Date2026-10-03
Asia/Bangkok. All commands cwd `C:\Users\Admin\Documents\GitHub\rag-core`.
Baseline `git status --short` exit0: only inherited untracked `.ptmp-t07-a02/`,
`.tmp-t07-a02/`; inaccessible T07 scratch/global ignore warnings retained. Branch
`main`, HEAD/initial authorized `git ls-remote origin refs/heads/main` both
`0b3d6f40dfc85034788c3dd9a3c285749cd19449`. Origin verified
`https://github.com/admininistrator/rag-core.git`; existing Git identity configured.
Read AGENTS/task-session-prompt, T20+T19/T03/T10 complete notes, P01/P03/P08/P13,
checkpoint/summary/README/RUNBOOK before source edits. No prior T20 candidate.

Scope13files: README/RUNBOOK, docs tasks/handoffs/implementation-summary,
pyproject pytest-local-pythonpath only, src domain/query/application/query/ports/rewrite,
tests contract/test_domain_registry/security/test_history_scope/fixtures/query_support,
security/conftest selector-loop hook. No dependency/lock/API/migration/index changes.

### Environment and service evidence

Initial sandbox Docker read failed (permission denied on Docker named pipe), and
initial sandbox `git ls-remote` could not connect443. Authorized elevated commands
then succeeded; no approval rejection or unresolved credential blocker. Only the
dedicated T20 test project was started/stopped; application/Scarlet services unchanged.

Command exit0:

```powershell
docker compose -p rag-core-t20-test -f compose.metadata-test.yaml -f compose.qdrant-test.yaml up -d --wait
```

Actual output excerpt:

```text
Network rag-core-t20-test_default Created
Container rag-core-t20-test-postgres-1 Healthy
Container rag-core-t20-test-qdrant-1 Healthy
```

Post-tests `docker compose ... ps` and
`docker inspect --format '{{.Name}} {{.Config.Image}} {{.State.Health.Status}}' rag-core-t20-test-postgres-1 rag-core-t20-test-qdrant-1`
each exit0, actual:

```text
/rag-core-t20-test-postgres-1 postgres:17.11-bookworm@sha256:051f7b7b3abdd564d5d1bd1e8c4b9c1b6e77087d1dd22020ede611c096a272e0 healthy
/rag-core-t20-test-qdrant-1 qdrant/qdrant:v1.19.1-unprivileged@sha256:801777072776dc81b2a9dd2007b2ed487571f21ecd30efffd15ddb1671f2193d healthy
```

Loopback55432/56333; PG/Qdrant tmpfs, random isolated DBs/collections cleaned by
existing fixtures. Tokenizer actual offline BGE-M3, not a count mock or model inference.
Rewrite provider `tests.fixtures.query_support.TestRewriter`, explicit schema-bound
synthetic protocol per T20 DoD; no LLM provider/model/credential or live claim.
Synthetic1024D vectors are authorization fixtures, not retrieval/model quality.

Common test environment (no secret values printed):

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'
$env:RAG_TEST_DATABASE_URL='postgresql://rag_core_test@127.0.0.1:55432/t10_acceptance'
$env:DATABASE_PASSWORD_FILE=Join-Path (Get-Location) '.local/secrets/t10_postgres_password'
$env:RAG_TEST_QDRANT_URL='http://127.0.0.1:56333'
```

### DoD-1 — PASS (separate final command)

```powershell
uv run --no-sync pytest tests/contract/test_domain_registry.py tests/security/test_history_scope.py -q -s --tb=short --basetemp=.local/t20-f1 -o cache_dir=.local/t20-fc1 *> .local/t20-dod1-final.log
```

Exit0; expected all unknown/subset/config/history/rewrite/custom-scope boundaries pass
with actual services/tokenizer; actual excerpt:

```text
Real PostgreSQL: separate database t10_test_7360c37b12a94a38a5a250b41b4fb347, public tables before migration=0
Real PostgreSQL: migrated separate database t10_test_7360c37b12a94a38a5a250b41b4fb347
T20 real PG/Qdrant: custom hook dense top1/fetch/neighbor current-session en only
T20 real PG/Qdrant: custom hook sparse top1/fetch/neighbor current-session en only
T20 real PG/Qdrant: custom hook hybrid top1/fetch/neighbor current-session en only
T20 real PG/Qdrant: custom hook dense top1/fetch/neighbor current-session vi only
T20 real PG/Qdrant: custom hook sparse top1/fetch/neighbor current-session vi only
T20 real PG/Qdrant: custom hook hybrid top1/fetch/neighbor current-session vi only
T20 real PG: detach during provider-test rewrite -> session_scope_changed
T20 real PG: delete during provider-test rewrite -> session_scope_changed
T20 real PG: generation during provider-test rewrite -> session_scope_changed
56 passed in 30.56s
```

Also proves foreign subset/identity rejected before provider/hook, context cannot be
used after detach, detach during custom hook aborts, every hybrid prefetch carries
same exact-pair/language filter. History old assistant citation/foreign chunk IDs
remain untrusted rewrite data only; no history/citations/evidence member in retrieval
context, no structured citation/system/developer/tool role accepted. Injected text
cannot select scope/config or obtain SDK/write/cleanup through the hook interface.
Trusted Python is not sandboxed; production repository independently enforces scope.

### DoD-2 — PASS (separate provider-test/language matrix)

```powershell
uv run --no-sync pytest tests/contract/test_domain_registry.py::test_followup_rewrite_schema_session_and_language_defaults -v --tb=short --basetemp=.local/t20-f2 -o cache_dir=.local/t20-fc2 *> .local/t20-dod2-final.log
```

Exit0, expected follow-up standalone-question schema, same session, original-question
language default/explicit overrides and unchanged opposite corpus filter in all3domains.
Actual excerpt (all12 combinations in local log):

```text
collecting ... collected 12 items
test_followup_rewrite_schema_session_and_language_defaults[en-None-default] PASSED
test_followup_rewrite_schema_session_and_language_defaults[vi-None-multilingual] PASSED
test_followup_rewrite_schema_session_and_language_defaults[en-vi-document] PASSED
test_followup_rewrite_schema_session_and_language_defaults[vi-en-multilingual] PASSED
============================= 12 passed in 7.53s ==============================
```

README/RUNBOOK domain matrix and port/system-data separation updated. Real provider
adapters T23 and live T26 are unchanged requirements, not skipped T20 gates.

### D1–D5 quality, review and failure history

Regression command common environment above, exit0 `.local/t20-regression.log`:

```powershell
uv run --no-sync pytest tests/unit tests/contract tests/security -q --tb=short --basetemp=.local/r20 -o cache_dir=.local/c20 *> .local/t20-regression.log
```

```text
431 passed in 146.59s (0:02:26)
```

Quality commands/outputs each exit0 unless initial format failure noted below:

```powershell
uv run --no-sync ruff check . *> .local/t20-ruff.log
uv run --no-sync mypy src *> .local/t20-mypy.log
uv lock --check --offline *> .local/t20-lock.log
uv run --no-sync python scripts/export_openapi.py --check *> .local/t20-openapi.log
```

```text
All checks passed!
Success: no issues found in 71 source files
Resolved 169 packages in 36ms
PASS checked docs/api/openapi-v1.designed.json
PASS checked docs/api/openapi.served.json
PASS checked docs/api/examples-v1.json
PASS designed_operations=13 served_health_routes=2 synthetic_examples=37
PASS OpenAPI model + Draft2020-12 schemas=48; examples JSON Schema + Pydantic
CONTRACT EXPORT: PASS (business endpoints unmounted; no runtime query/stream verification)
```

Ruff root traversal emits3inherited Access-is-denied warnings, not task errors; changed
paths also explicitly checked. Initial mypy1domain override error resolved with a documented
internal-only widening suppression; public QueryRequest still closed. Initial RUF005/F811
fixed (tuple unpack, fixture module imports). First pytest collection exit2 `No module named
'tests'` in `.local/t20-dod1-first.log`; minimal pytest pythonpath fixes shared test namespace,
second full51PASS27.39s in `.local/t20-dod1-second.log`. No gate removed. Later strict-result
revalidation/error-redaction and EN/VI real filter cases expand final gate to56PASS.
Format check initially1file failed after EN/VI print edit; only formatting changed and final
same7paths format check exit0 `7 files already formatted`.

After acceptance, `uv sync --locked --group dev --group api --group ingestion --offline`
exit0 resolved169packages/build local package; removed34unrequested inference-only installed
extras from host `.venv`, no lock changes. Tests above used inherited locked dev/api/ingestion
plus inference extras; relevant tokenizer/provider/persistence versions unchanged after sync.
Runtime inspection exit0 actual:

```text
3.12.4
{'pydantic': '2.13.5', 'tokenizers': '0.22.2', 'psycopg': '3.3.5', 'qdrant-client': '1.19.0', 'pytest': '9.1.1', 'pytest-asyncio': '1.4.0'}
BAAI/bge-m3@5617a9f61b028005a4858fdac845db406aefb181/21106b6d7dab2952c1d496fb21d5dc9db75c28ed361a05f5020bbba27810dd08/tokenizers-0.22.2
```

`docker compose -p rag-core-t20-test -f compose.metadata-test.yaml -f compose.qdrant-test.yaml stop`
exit0: both own test containers Stopped; no volume/source/cache deletion.

D1 dependency+exact task scope/whitespace review; D2 separate checks+critical behavior;
D3 both above gates; D4 README/RUNBOOK +task/handoff/summary; D5 source/config/contracts
review (no API/migration/index change, no secret/raw corpus/cache staging). Final docs/scope/
secrets/cached checks appended at closure. D6 is actual inspected scoped completion commit
`feat(T20): compose extensible session-scoped domains`; hash/push equality returned after
execution, never self-hash/amend. T21 dependencies ready only after closure, stays TODO.

### Final environment/docs/format checks

After reducing host extras, focused contract command exit0:

```powershell
uv run --no-sync pytest tests/contract/test_domain_registry.py -q --tb=short --basetemp=.local/t20-post -o cache_dir=.local/t20-postc *> .local/t20-postsync.log
```

Actual `40 passed in 13.85s` proves T20 does not require Torch/FlagEmbedding inference.
Whole-source mypy immediately after that reduced sync exited1 (`.local/t20-mypy-close.log`):

```text
Cannot find implementation or library stub for module named "torch" [import-not-found]
Unused "type: ignore" comment [unused-ignore]
Cannot find implementation or library stub for module named "FlagEmbedding" [import-not-found]
Found 3 errors in 1 file (checked 71 source files)
```

These are T17 adapter environment imports, not T20 source/type failures. Restored
existing locked inference group offline, no code/typing-gate/lock modification:

```powershell
uv sync --locked --group dev --group api --group ingestion --group inference --offline *> .local/t20-sync-close.log
uv run --no-sync mypy src *> .local/t20-mypy-final.log
uv run --no-sync ruff check src/rag_core/domain/query.py src/rag_core/application/query.py src/rag_core/ports/rewrite.py tests/contract/test_domain_registry.py tests/security/test_history_scope.py tests/fixtures/query_support.py tests/security/conftest.py *> .local/t20-ruff-final.log
uv run --no-sync ruff format --check src/rag_core/domain/query.py src/rag_core/application/query.py src/rag_core/ports/rewrite.py tests/contract/test_domain_registry.py tests/security/test_history_scope.py tests/fixtures/query_support.py tests/security/conftest.py *> .local/t20-format-final.log
uv run --no-sync python scripts/check_docs.py *> .local/t20-docs-final.log
```

Each exit0; actual:

```text
Resolved 169 packages in 1ms
Installed 33 packages in 5.59s
Success: no issues found in 71 source files
All checks passed!
7 files already formatted
PASS UTF-8/nonempty Markdown: 14 files
PASS internal links/anchors: 340
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```

Docs check count above was before final task result/closure additions, rerun at staging.

### Scoped staging and closure review

Exact staging command (exit0):

```powershell
git add -- README.md RUNBOOK.md docs/tasks.md docs/handoffs.md docs/implementation-summary.md pyproject.toml src/rag_core/domain/query.py src/rag_core/application/query.py src/rag_core/ports/rewrite.py tests/contract/test_domain_registry.py tests/security/test_history_scope.py tests/fixtures/query_support.py tests/security/conftest.py
git diff --cached --check
git diff --cached --stat
git diff --cached -- pyproject.toml tests/security/conftest.py
git diff --cached --name-only
uv run --no-sync python .local/t20_review.py *> .local/t20-review-close.log
uv run --no-sync python scripts/check_docs.py *> .local/t20-docs-close.log
```

Each exit0; actual before this evidence-only append:

```text
13 files changed, 1241 insertions(+), 6 deletions(-)
Existing marker metadata only: docs/handoffs.md current=(1, 0, 0) HEAD=(1, 0, 0)
PASS exact13 staged paths; new credential markers/local-secret/size/UTF8 checks; AGENTS/plan/lock/corpus unchanged; worktree=index and whitespace clean
PASS UTF-8/nonempty Markdown: 14 files
PASS internal links/anchors: 342
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```

Initial entire-history marker scan exited1 (`credential marker in task file`), because
one pre-existing key-marker occurrence already exists in HEAD handoff history. It prints
no key value and no content. Review checks unchanged baseline marker counts and **all
added diff lines**, plus absence of actual own local credential across all13files; no
new key/JWT/AWS marker added. Historical evidence preserved. Local review helper/logs
ignored, never staged; no corpus/cache/weights/source/storage credentials in index.

Restage this evidence-only append and repeat same exact13path review/docs/whitespace,
then execute completion commit and authorized push. D1–D5/individual DoD all PASS;
D6 becomes PASS only when inspected completion commit succeeds. Actual commit hash/
remote equality reported outside its own commit; no amend/merge/deploy/task drain.

<a id="h-t21-a01"></a>
## H-T21-A01 — Phase 4 / dense/sparse hybrid retrieval

Runtime direct Codex agent, exact model/effort unavailable, no subagents; date2026-10-03
Asia/Bangkok. All commands cwd `C:\Users\Admin\Documents\GitHub\rag-core`.
Baseline `git status --short; git branch --show-current; git rev-parse HEAD; git remote -v`
exit0, actual:

```text
?? .ptmp-t07-a02/
?? .tmp-t07-a02/
main
938bee71ac537e386e8472efc6f9eed7951026d1
origin https://github.com/admininistrator/rag-core.git (fetch)
origin https://github.com/admininistrator/rag-core.git (push)
```

Inherited global-ignore/inaccessible T07 scratch warnings retained, files untouched.
Authorized `git ls-remote origin refs/heads/main` exit0:
`938bee71ac537e386e8472efc6f9eed7951026d1 refs/heads/main`.
Read AGENTS/session prompt/fullT20/T18/T17 notes/interfaces/evidence, P01/P03/P08/P11/P13,
checkpoint/summary/README/RUNBOOK before implementation; no prior T21 candidate.
Scope11paths: five living docs, application query/retrieval +domain retrieval,
compose.retrieval-test.yaml, actual integration suite and supplemental policy unit suite.
No dependency/lock/model/publicAPI/index/DB migration/corpus change.

### Environment and retained diagnostics

Initial sandbox `docker ps --format '{{.Names}} {{.Status}}'; git ls-remote origin refs/heads/main`
exit1, actual `permission denied while trying to connect to the docker API at npipe:////./pipe/docker_engine`
and `Failed to connect to github.com port 443`. Scoped elevated calls succeeded; no
approval rejection/credential blocker. Existing model cache/image reused read-only.
First attempt to write task metadata through `uv run --no-sync python -` exit1:
`Failed to initialize cache at C:\Users\Admin\AppData\Local\uv\cache` / `Access is denied`.
Set repo UV_CACHE_DIR. Subsequent PowerShell-piped non-ASCII replacements did not match
Vietnamese task labels (only line endings changed); caught on actual diff/read, corrected
with UTF-8 patch. Task is T21-A01; no gate/semantics changed to hide either diagnostic.

Actual service command (elevated) exit0:

```powershell
docker compose -p rag-core-t21-test -f compose.metadata-test.yaml -f compose.qdrant-test.yaml -f compose.retrieval-test.yaml up -d --wait
```

Actual output:

```text
Network rag-core-t21-test_default Created
Container rag-core-t21-test-qdrant-1 Healthy
Container rag-core-t21-test-postgres-1 Healthy
Container rag-core-t21-test-inference-1 Healthy
```

Only own dedicated test project; no application/Scarlet mutation. PG17.11 and
Qdrant1.19.1 pinned digests from T18, loopback55432/56333 tmpfs. Inference loopback58080,
T17 CPU image and read-only `rag-core_model_cache`. Host uses existing locked groups;
no host model execution. Model BGE-M3 revision5617a9f61b028005a4858fdac845db406aefb181;
full CPU runtime fingerprint f25d7370e6e501a36aaba4da5c487ea790909d1a400d410e01f32348c34f534b.
Reranker revision953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e loaded once by shared T17
service, not invoked by retrieval. No LLM provider/key/live-generation claim.

Commands each exit0:

```powershell
docker compose -p rag-core-t21-test -f compose.metadata-test.yaml -f compose.qdrant-test.yaml -f compose.retrieval-test.yaml config --quiet
docker inspect --format '{{.Name}} {{.Config.Image}} {{.Image}} {{.State.Health.Status}}' rag-core-t21-test-postgres-1 rag-core-t21-test-qdrant-1 rag-core-t21-test-inference-1
docker stats --no-stream --format '{{.Name}} {{.MemUsage}} {{.CPUPerc}}' rag-core-t21-test-inference-1
```

Actual output excerpt (config command no output):

```text
/rag-core-t21-test-postgres-1 postgres:17.11-bookworm@sha256:051f7b7b3abdd564d5d1bd1e8c4b9c1b6e77087d1dd22020ede611c096a272e0 sha256:051f7b7b3abdd564d5d1bd1e8c4b9c1b6e77087d1dd22020ede611c096a272e0 healthy
/rag-core-t21-test-qdrant-1 qdrant/qdrant:v1.19.1-unprivileged@sha256:801777072776dc81b2a9dd2007b2ed487571f21ecd30efffd15ddb1671f2193d sha256:801777072776dc81b2a9dd2007b2ed487571f21ecd30efffd15ddb1671f2193d healthy
/rag-core-t21-test-inference-1 rag-core-inference:t17-cpu sha256:4b79b3c9e877d07eebef37c0d1e580f3a23708dad0e4380cfdba4f877cd6e2ac healthy
rag-core-t21-test-inference-1 2.196GiB / 7GiB 0.11%
```

Tests observed one PID8/two model instances, CPU load66.551s. Snapshot memory is not
peak/load/full-stack SLA. Inference image is existing T17 artifact; new retrieval code
runs from current host source via HTTP client, no claim new source packaged in that image.
Official Qdrant hybrid reference confirms default equal-weight RRF k2; pinned T18
FusionQuery used, no raw-score sum/cosine threshold/algorithm migration.

Common test environment, credential only loaded from file, never printed:

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'
$env:RAG_TEST_DATABASE_URL='postgresql://rag_core_test@127.0.0.1:55432/t10_acceptance'
$env:DATABASE_PASSWORD_FILE=Join-Path (Get-Location) '.local/secrets/t10_postgres_password'
$env:RAG_TEST_QDRANT_URL='http://127.0.0.1:56333'
$env:RAG_TEST_INFERENCE_URL='http://127.0.0.1:58080'
```

First DoD-1 command exit1, full local log ignored `.local/t21-dod1-first.log`:

```powershell
uv run --no-sync pytest tests/integration/test_retrieval.py -q -s --tb=short --basetemp=.local/t21-a1 -o cache_dir=.local/t21-c1 *> .local/t21-dod1-first.log
```

Actual failure excerpt:

```text
E AttributeError: 'Session' object has no attribute 'revision'
1 failed, 13 passed in 37.01s
```

Corrected test uses real `scope_revision` and retains T10 empty-session
`no_session_documents`/snapshot rejection; no change to persistence semantics.
Added actual neighbor-return EN/VI assertions and unrelated appendix embeddings,
not merely vacuous iteration over empty expanded set. Initial Ruff unused imports
fixed and formatting applied; no skipped/relaxed tests.

### DoD-1 — PASS, separate real-service command

```powershell
uv run --no-sync pytest tests/integration/test_retrieval.py -q -s --tb=short --basetemp=.local/t21-a2 -o cache_dir=.local/t21-c2 *> .local/t21-dod1-second.log
```

Exit0; expected actual multi-doc/keyword/numeric/EN->VI/VI->EN/distractor/no-match,
language filter at each branch, same-scope bounded neighbors and invalidation.
Actual output excerpts, complete local log above (synthetic IDs only, no secrets):

```text
T21 REAL MODEL device=cpu pid=8 fingerprint=f25d7370e6e501a36aaba4da5c487ea790909d1a400d410e01f32348c34f534b runtime={'FlagEmbedding': '1.3.5', 'torch': '2.9.1+cpu', 'transformers': '4.57.6', 'tokenizers': '0.22.2', 'sentence-transformers': '5.1.2', 'peft': '0.17.1'} load=66.551s
T21 REAL dense corpus=vi top1=capital-vi scope/filter/trace PASS
T21 REAL hybrid corpus=vi top1=capital-vi scope/filter/trace PASS
T21 REAL dense corpus=en top1=capital-en scope/filter/trace PASS
T21 REAL hybrid corpus=en top1=capital-en scope/filter/trace PASS
T21 REAL dense corpus=en top1=finance-en scope/filter/trace PASS
T21 REAL hybrid corpus=en top1=finance-en scope/filter/trace PASS
T21 REAL dense corpus=vi top1=finance-vi scope/filter/trace PASS
T21 REAL hybrid corpus=vi top1=finance-vi scope/filter/trace PASS
T21 REAL multi-doc labels=['capital-en', 'finance-en'] candidates=4 neighbor_calls=2
T21 REAL no-match language -> zero candidates; empty session rejected before model/vector
T21 REAL neighbor corpus=en adds1 same-page/pair/filter; detach on scroll aborts
T21 REAL neighbor corpus=vi adds1 same-page/pair/filter; detach on scroll aborts
T21 REAL sparse absent lexical tokens -> zero candidates
T21 REAL detach after model / Qdrant -> abort, no stale candidates
T21 REAL reproducible dense/hybrid, prefetch100/candidate20/anchors20 boundaries PASS
16 passed in 42.50s
```

Actual model token-budget rejection also passes without vector search. Both prefetch
filters observed on real requests; owner/exact pairs/language checked before top-k,
foreign2apps/2users/same-owner-other-session actual embeddings retained but excluded.
All six synthetic documents plus distractors/appendices indexed, no QA/gold/doc selection
for relevance. Negative no-match uses user-selected EN source +valid VI filter; no
ground-truth narrowing. No factual answer/held-out corpus quality measurement claimed.

### DoD-2 — PASS, separate reproducibility/boundary command

```powershell
uv run --no-sync pytest tests/unit/test_retrieval_policy.py tests/integration/test_retrieval.py::test_real_dense_hybrid_toggle_reproducible_and_max_budget -q -s --tb=short --basetemp=.local/t21-d2 -o cache_dir=.local/t21-dc2 *> .local/t21-dod2.log
```

Exit0; expected JSON config roundtrip/hash, dense/hybrid repeat same scored candidates,
actual prefetch100/candidate20/anchors20, min/max/invalid budgets, immutable profile,
unknown/stale/empty/cancel/deadline/revision/shape failure boundaries. Actual:

```text
T21 REAL reproducible dense/hybrid, prefetch100/candidate20/anchors20 boundaries PASS
29 passed in 6.83s
```

Supplemental28unit cases use explicitly synthetic stalled/error protocol collaborators
for cancellation/deadline/config, not model/retrieval success. RUNBOOK tunables, score
semantics, revalidation, trace vs private candidates, no QA/gold API and limitations
updated. No pipeline corpus file access or gold filter; source metadata from scoped
repository only. Trace has no question/history/identity/IDs/vectors/storage key.

### D2 — Quality, regression and dependency gates

Each command exit0, logs at the exact ignored local paths shown:

```powershell
uv run --no-sync ruff check . *> .local/t21-ruff.log
uv run --no-sync mypy src *> .local/t21-mypy.log
uv lock --check --offline *> .local/t21-lock.log
uv run --no-sync python scripts/export_openapi.py --check *> .local/t21-openapi.log
uv run --no-sync pytest tests/unit tests/contract tests/security -q --tb=short --basetemp=.local/r21 -o cache_dir=.local/c21 *> .local/t21-regression.log
uv run --no-sync pytest tests/integration/test_qdrant_scope.py tests/integration/test_session_scope.py -q --tb=short --basetemp=.local/t21-dep -o cache_dir=.local/t21-depc *> .local/t21-dependencies.log
```

Actual output excerpts:

```text
All checks passed!
Success: no issues found in 73 source files
Resolved 169 packages in 35ms
PASS checked docs/api/openapi-v1.designed.json
PASS checked docs/api/openapi.served.json
PASS checked docs/api/examples-v1.json
PASS designed_operations=13 served_health_routes=2 synthetic_examples=37
PASS OpenAPI model + Draft2020-12 schemas=48; examples JSON Schema + Pydantic
CONTRACT EXPORT: PASS (business endpoints unmounted; no runtime query/stream verification)
459 passed in 135.41s (0:02:15)
35 passed in 13.79s
```

Ruff root traversal warns three inherited inaccessible directories, no task errors;
explicit changed-path checks/format also run at closure. Existing environment keeps
inference group installed for whole-source T17 imports in mypy; no uv.lock change.

### D1/D3/D4/D5/D6 — Closure review boundary

D1: read dependencies/P01, preserve baseline scratch, review exact11paths and whitespace.
D2: quality/regression/actual dependency gates above. D3: two DoD commands individually.
D4: README/RUNBOOK updated together with status/DI/tunables/commands/errors/limits;
task notes/summary/checkpoint/evidence added, docs validator run at closure.
D5: review no secrets/rawQA/weights/cache/logs/prompt changes; additive validation method,
no dependency/API/DB/index migration, no source deletion. D6: explicit scoped stage and
completion subject `feat(T21): add scoped hybrid multilingual retrieval`; COMPLETE only
after successful inspected commit. Actual hash/authorized origin/main push equality
reported after execution, no self-hash/amend/force/merge/deploy.
T22 dependencies T21/T17 ready after closure; leave TODO and STOP AFTER T21.

### Final reviewed fixture — actual cap20, min1 and accurate language metadata

Review found intermediate fixture had18current-session chunks, so the max20 test
had not exercised overflow. Final fixture has24actual embedded chunks (6sources ×4),
with EN/VI appendix texts matching each language annotation, plus actual retained
foreign/same-owner-other-session vectors. Final max test requires **exactly20** candidates
and zero neighbor calls when budget full, and minimum prefetch/top_k/total1 requires
exactly1 candidate. Same-scope neighbor gate still requires actual additional1point.
No model/pipeline/scope/gold/DoD change; both DoD commands rerun after test changes.

Same scoped Compose `up -d --wait` and final `stop` commands above exit0; inference
restarted as PID7 with same full CPU model/runtime fingerprint and loaded two fixed
models, load33.590s. No application services/volumes/cache/source deletion.

Final DoD-1 command exit0:

```powershell
uv run --no-sync pytest tests/integration/test_retrieval.py -q -s --tb=short --basetemp=.local/t21-fin1 -o cache_dir=.local/t21-fc1 *> .local/t21-dod1-final.log
```

Final actual excerpt:

```text
T21 REAL MODEL device=cpu pid=7 fingerprint=f25d7370e6e501a36aaba4da5c487ea790909d1a400d410e01f32348c34f534b runtime={'FlagEmbedding': '1.3.5', 'torch': '2.9.1+cpu', 'transformers': '4.57.6', 'tokenizers': '0.22.2', 'sentence-transformers': '5.1.2', 'peft': '0.17.1'} load=33.590s
T21 REAL neighbor corpus=en adds1 same-page/pair/filter; detach on scroll aborts
T21 REAL neighbor corpus=vi adds1 same-page/pair/filter; detach on scroll aborts
T21 REAL sparse absent lexical tokens -> zero candidates
T21 REAL detach after model / Qdrant -> abort, no stale candidates
T21 REAL reproducible dense/hybrid, prefetch100/candidate20/anchors20 boundaries PASS
16 passed in 42.73s
```

Final DoD-2 command exit0:

```powershell
uv run --no-sync pytest tests/unit/test_retrieval_policy.py tests/integration/test_retrieval.py::test_real_dense_hybrid_toggle_reproducible_and_max_budget -q -s --tb=short --basetemp=.local/t21-fin2 -o cache_dir=.local/t21-fc2 *> .local/t21-dod2-final.log
```

```text
T21 REAL reproducible dense/hybrid, prefetch100/candidate20/anchors20 boundaries PASS
29 passed in 5.25s
```

Actual final D2/D4 commands each exit0:

```powershell
uv run --no-sync ruff check src/rag_core/domain/retrieval.py src/rag_core/application/retrieval.py src/rag_core/application/query.py tests/integration/test_retrieval.py tests/unit/test_retrieval_policy.py
uv run --no-sync ruff format --check src/rag_core/domain/retrieval.py src/rag_core/application/retrieval.py tests/integration/test_retrieval.py tests/unit/test_retrieval_policy.py
uv run --no-sync python scripts/check_docs.py
```

```text
All checks passed!
4 files already formatted
PASS UTF-8/nonempty Markdown: 14 files
PASS internal links/anchors: 351
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```

Initial D4 checker exit1 `Missing anchor ... #h-t21-a01`; added exact explicit anchor,
fixed current README/RUNBOOK/summary stale retrieval status; same validator PASS above.
Earlier passing459unit/contract/security and35dependency checks still apply to identical
production/unit source; final changes only strengthen T21 integration fixtures and docs.

Final service commands exit0:

```powershell
docker compose -p rag-core-t21-test -f compose.metadata-test.yaml -f compose.qdrant-test.yaml -f compose.retrieval-test.yaml stop
docker compose -p rag-core-t21-test -f compose.metadata-test.yaml -f compose.qdrant-test.yaml -f compose.retrieval-test.yaml ps --all --format '{{.Name}} {{.State}}'
```

```text
Container rag-core-t21-test-qdrant-1 Stopped
Container rag-core-t21-test-postgres-1 Stopped
Container rag-core-t21-test-inference-1 Stopped
rag-core-t21-test-inference-1 exited
rag-core-t21-test-postgres-1 exited
rag-core-t21-test-qdrant-1 exited
```

### Final D1/D4/D5/D6 — exact staged candidate review

Explicit stage/inspection commands each exit0:

```powershell
git add -- README.md RUNBOOK.md docs/tasks.md docs/handoffs.md docs/implementation-summary.md src/rag_core/application/query.py src/rag_core/application/retrieval.py src/rag_core/domain/retrieval.py compose.retrieval-test.yaml tests/integration/test_retrieval.py tests/unit/test_retrieval_policy.py
git diff --cached --check
git diff --cached --stat
uv run --no-sync python .local/t21_review.py
uv run --no-sync python scripts/check_docs.py
git diff --cached --name-only
```

Actual output excerpt before this evidence/status-only append:

```text
11 files changed, 1299 insertions(+), 15 deletions(-)
Existing marker metadata only: docs/handoffs.md current=(1, 0, 0) HEAD=(1, 0, 0)
PASS exact11 staged paths; added credential markers/local-secret/size/UTF8 checks; AGENTS/plan/lock/dependency/corpus unchanged; worktree=index and whitespace clean
PASS UTF-8/nonempty Markdown: 14 files
PASS internal links/anchors: 351
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```

Actual index lists exactly README/RUNBOOK, three ledgers, three source modules,
one test Compose and two test suites. Existing Git identity configured, no fake
author/global settings. Source/diff independently read/reviewed, no raw licensed
data/QA/weights/cache/local helper/logs/credentials staged; inherited historical
private-key-marker count unchanged and every added line checked. Local review helper
does not print secret values, UTF-8/stat/markers only; ignored and not staged.

Restage this evidence/status-only append, repeat same scope/whitespace/docs audit,
then completion commit. All task DoD/D1–D5 PASS; D6/COMPLETE effective only with
successful inspected `feat(T21): add scoped hybrid multilingual retrieval` commit.
Actual hash/authorized origin/main equality reported outside its own commit; no
amend/force/merge/deploy, T22 remains TODO and STOP AFTER T21.


<a id="h-t22-a01"></a>
## H-T22-A01 - Phase 4 / partial reranking checkpoint, NOT COMPLETE

Direct Codex agent; exact runtime model/effort unavailable; no subagents. Date
2026-10-06 Asia/Bangkok. Every command cwd
`C:\Users\Admin\Documents\GitHub\rag-core`. This is a partial checkpoint,
**not task acceptance**. Required conflicting-evidence decision/test is outstanding.

### Baseline, authorization and services

`git status --short; git branch --show-current; git rev-parse HEAD; git remote -v`
exit0, actual:

```text
?? .ptmp-t07-a02/
?? .tmp-t07-a02/
main
2c84157ba5bcac83560191573d8a26fa944bb1cf
origin https://github.com/admininistrator/rag-core.git (fetch)
origin https://github.com/admininistrator/rag-core.git (push)
```

Existing global-ignore and inaccessible T07 scratch warnings retained; no cleanup.
T21/T17 COMPLETE notes/interfaces/evidence and AGENTS/session prompt,
P01/P08/P09/P11/P13, checkpoint/summary/README/RUNBOOK read before code.
No partial tracked T22 candidate. User explicitly authorizes scoped commit/push,
no force/merge/deploy/drain. No subagents/old Orchestrator/Worker/Kanban used.

Initial sandbox command `docker ps --format '{{.Names}} {{.Status}}'; git ls-remote origin refs/heads/main`
exit1: `permission denied while trying to connect to the docker API at npipe:////./pipe/docker_engine`
and `Failed to connect to github.com port 443`. Same scoped elevated read succeeded
exit0; remote actual `2c84157ba5bcac83560191573d8a26fa944bb1cf refs/heads/main`.
Existing Scarlet/sub2api services observed healthy and preserved. No automatic
approval rejection or credential blocker. `git var GIT_AUTHOR_IDENT | Out-Null`
exit0, `Git author configured`; no identity values printed or config changed.

Elevated actual command exit0:

```powershell
docker compose -p rag-core-t22-test -f compose.metadata-test.yaml -f compose.qdrant-test.yaml -f compose.retrieval-test.yaml up -d --wait
```

Actual output: `Network rag-core-t22-test_default Created`, containers
`rag-core-t22-test-postgres-1 Healthy`, `rag-core-t22-test-qdrant-1 Healthy`,
`rag-core-t22-test-inference-1 Healthy`. Isolated tmpfs PG/Qdrant, external model
cache read-only, opt-in loopback55432/56333/58080; no source/application volumes changed.

Actual elevated inspection commands each exit0:

```powershell
docker inspect --format '{{.Name}} {{.Config.Image}} {{.Image}} {{.State.Health.Status}}' rag-core-t22-test-postgres-1 rag-core-t22-test-qdrant-1 rag-core-t22-test-inference-1
docker stats --no-stream --format '{{.Name}} {{.MemUsage}} {{.CPUPerc}}' rag-core-t22-test-inference-1
```

Output excerpt:

```text
/rag-core-t22-test-postgres-1 postgres:17.11-bookworm@sha256:051f7b7b3abdd564d5d1bd1e8c4b9c1b6e77087d1dd22020ede611c096a272e0 sha256:051f7b7b3abdd564d5d1bd1e8c4b9c1b6e77087d1dd22020ede611c096a272e0 healthy
/rag-core-t22-test-qdrant-1 qdrant/qdrant:v1.19.1-unprivileged@sha256:801777072776dc81b2a9dd2007b2ed487571f21ecd30efffd15ddb1671f2193d sha256:801777072776dc81b2a9dd2007b2ed487571f21ecd30efffd15ddb1671f2193d healthy
/rag-core-t22-test-inference-1 rag-core-inference:t17-cpu sha256:4b79b3c9e877d07eebef37c0d1e580f3a23708dad0e4380cfdba4f877cd6e2ac healthy
rag-core-t22-test-inference-1 2.453GiB / 7GiB 0.12%
```

Model actual CPU fingerprint
`f25d7370e6e501a36aaba4da5c487ea790909d1a400d410e01f32348c34f534b`,
one PID7/two fixed models/load29.193s. BGE-M3 revision
5617a9f61b028005a4858fdac845db406aefb181 and reranker953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e
from verified T17 read-only cache/image. FlagEmbedding1.3.5, Torch2.9.1+cpu,
Transformers4.57.6, tokenizers0.22.2, sentence-transformers5.1.2, peft0.17.1.
Image remains original shared T17 model service; T22 host source calls real HTTP.
Memory is an idle snapshot, not peak/SLA/load/full-stack/calibration measurement.
No DeepSeek/Anthropic/LLM/provider credential or live-generation claim in T22.

### Common host configuration and partial gates

Actual common environment, secret value only loaded from file:

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'
$env:RAG_TEST_DATABASE_URL='postgresql://rag_core_test@127.0.0.1:55432/t10_acceptance'
$env:DATABASE_PASSWORD_FILE=Join-Path (Get-Location) '.local/secrets/t10_postgres_password'
$env:RAG_TEST_QDRANT_URL='http://127.0.0.1:56333'
$env:RAG_TEST_INFERENCE_URL='http://127.0.0.1:58080'
```

No uv sync/dependency changes; existing .venv reused with --no-sync and locked
groups. All tests use serial suites on dedicated server; own random PG databases
and fixture collections removed by existing test lifecycle, source/cache retained.
Synthetic source fixtures are tagged explicitly; actual model/server acceptance
does not consume official QA/gold/answer/document IDs as retrieval hints.

DoD-1 is **BLOCKED** overall, even though implemented cases pass: required
conflicting-evidence behavior and real acceptance case missing. Nearest neighbor
irrelevant, EN->VI/VI->EN support, multi-source/number/unit/table headers/full maps,
whole-passage budget boundary/no match, actual HTTP cancel/recovery and pair
overlimit/deadline are already tested. Max20 real candidates/8passages checked.
No mock score substitutes for these real gates. Raw floor0.0 is versioned baseline
pending T31, never factual-confidence probability or tuned multi-hop completeness.

Required clarification asked asynchronously: plan/task requires conflicting reason
but does not define pre-LLM mechanism; choose numeric same-label/unit baseline or
semantic contradiction coverage. No reply at checkpoint. Per AGENTS section2,
do not guess product semantics, weaken DoD or silently defer required conflict gate.
Reason enum exists, but current selector does not detect conflicts. Preserve work;
resume conflict implementation and each original gate after decision.

DoD-2 checks bound app/owner/current session/ready pair/subset/language before
rerank/context; stale/detached/deleted scope, forged vector metadata/generation,
foreign retained sources, forged history/passages and tampered source text/map
fail closed. RUNBOOK now explicitly records pending T31 thresholds/non-probability
and partial status. No LLM context/provider invocation claim: context gate for T24
is checked directly with actual scoped durable passage inputs.

### Initial implemented DoD-1 cases

Command exact (exit0), expected/actual implemented checks PASS:

```powershell
uv run --no-sync pytest tests/integration/test_evidence_selection.py -q -s --tb=short --basetemp=.local/22d1 -o cache_dir=.local/22c1 *> .local/t22-dod1-initial.log
```

Actual excerpt; full ignored log `.local/t22-dod1-initial.log`:

```text
T22 REAL cross-language en supported raw=4.9300
.T21 REAL MODEL device=cpu pid=7 fingerprint=f25d7370e6e501a36aaba4da5c487ea790909d1a400d410e01f32348c34f534b runtime={'FlagEmbedding': '1.3.5', 'torch': '2.9.1+cpu', 'transformers': '4.57.6', 'tokenizers': '0.22.2', 'sentence-transformers': '5.1.2', 'peft': '0.17.1'} load=29.193s
T22 REAL irrelevant nearest neighbor -> insufficient / zero context
.T21 REAL MODEL device=cpu pid=7 fingerprint=f25d7370e6e501a36aaba4da5c487ea790909d1a400d410e01f32348c34f534b runtime={'FlagEmbedding': '1.3.5', 'torch': '2.9.1+cpu', 'transformers': '4.57.6', 'tokenizers': '0.22.2', 'sentence-transformers': '5.1.2', 'peft': '0.17.1'} load=29.193s
T22 REAL multi-evidence=3 numeric/unit/header/source-map PASS
.T21 REAL MODEL device=cpu pid=7 fingerprint=f25d7370e6e501a36aaba4da5c487ea790909d1a400d410e01f32348c34f534b runtime={'FlagEmbedding': '1.3.5', 'torch': '2.9.1+cpu', 'transformers': '4.57.6', 'tokenizers': '0.22.2', 'sentence-transformers': '5.1.2', 'peft': '0.17.1'} load=29.193s
.T21 REAL MODEL device=cpu pid=7 fingerprint=f25d7370e6e501a36aaba4da5c487ea790909d1a400d410e01f32348c34f534b runtime={'FlagEmbedding': '1.3.5', 'torch': '2.9.1+cpu', 'transformers': '4.57.6', 'tokenizers': '0.22.2', 'sentence-transformers': '5.1.2', 'peft': '0.17.1'} load=29.193s
T22 REAL HTTP rerank cancelled; subsequent real rerank supported
.T21 REAL MODEL device=cpu pid=7 fingerprint=f25d7370e6e501a36aaba4da5c487ea790909d1a400d410e01f32348c34f534b runtime={'FlagEmbedding': '1.3.5', 'torch': '2.9.1+cpu', 'transformers': '4.57.6', 'tokenizers': '0.22.2', 'sentence-transformers': '5.1.2', 'peft': '0.17.1'} load=29.193s
.T21 REAL MODEL device=cpu pid=7 fingerprint=f25d7370e6e501a36aaba4da5c487ea790909d1a400d410e01f32348c34f534b runtime={'FlagEmbedding': '1.3.5', 'torch': '2.9.1+cpu', 'transformers': '4.57.6', 'tokenizers': '0.22.2', 'sentence-transformers': '5.1.2', 'peft': '0.17.1'} load=29.193s
.
8 passed in 50.92s
```

### Initial DoD-2 security gate

Command exact (exit0), expected/actual implemented checks PASS:

```powershell
uv run --no-sync pytest tests/security/test_evidence_scope.py -q -s --tb=short --basetemp=.local/22d2 -o cache_dir=.local/22c2 *> .local/t22-dod2-initial.log
```

Actual excerpt; full ignored log `.local/t22-dod2-initial.log`:

```text
.T21 REAL MODEL device=cpu pid=7 fingerprint=f25d7370e6e501a36aaba4da5c487ea790909d1a400d410e01f32348c34f534b runtime={'FlagEmbedding': '1.3.5', 'torch': '2.9.1+cpu', 'transformers': '4.57.6', 'tokenizers': '0.22.2', 'sentence-transformers': '5.1.2', 'peft': '0.17.1'} load=29.193s
.T21 REAL MODEL device=cpu pid=7 fingerprint=f25d7370e6e501a36aaba4da5c487ea790909d1a400d410e01f32348c34f534b runtime={'FlagEmbedding': '1.3.5', 'torch': '2.9.1+cpu', 'transformers': '4.57.6', 'tokenizers': '0.22.2', 'sentence-transformers': '5.1.2', 'peft': '0.17.1'} load=29.193s
.T21 REAL MODEL device=cpu pid=7 fingerprint=f25d7370e6e501a36aaba4da5c487ea790909d1a400d410e01f32348c34f534b runtime={'FlagEmbedding': '1.3.5', 'torch': '2.9.1+cpu', 'transformers': '4.57.6', 'tokenizers': '0.22.2', 'sentence-transformers': '5.1.2', 'peft': '0.17.1'} load=29.193s
.T21 REAL MODEL device=cpu pid=7 fingerprint=f25d7370e6e501a36aaba4da5c487ea790909d1a400d410e01f32348c34f534b runtime={'FlagEmbedding': '1.3.5', 'torch': '2.9.1+cpu', 'transformers': '4.57.6', 'tokenizers': '0.22.2', 'sentence-transformers': '5.1.2', 'peft': '0.17.1'} load=29.193s
.T21 REAL MODEL device=cpu pid=7 fingerprint=f25d7370e6e501a36aaba4da5c487ea790909d1a400d410e01f32348c34f534b runtime={'FlagEmbedding': '1.3.5', 'torch': '2.9.1+cpu', 'transformers': '4.57.6', 'tokenizers': '0.22.2', 'sentence-transformers': '5.1.2', 'peft': '0.17.1'} load=29.193s
T22 REAL history/foreign/text/allowlist generation-context guards PASS; no LLM invoked
.
12 passed in 61.48s (0:01:01)
```

### Actual max budget and T21/T18/T10 dependency regression

Command exact (exit0), expected/actual implemented checks PASS:

```powershell
uv run --no-sync pytest tests/integration/test_evidence_selection.py::test_actual_twenty_candidates_eight_passages_and_reproducible_threshold tests/integration/test_retrieval.py tests/integration/test_qdrant_scope.py tests/integration/test_session_scope.py -q -s --tb=short --basetemp=.local/22dep -o cache_dir=.local/22depc *> .local/t22-dependencies.log
```

Actual excerpt; full ignored log `.local/t22-dependencies.log`:

```text
.PASS PG publication blocked by generation write lock until actual Qdrant wait=true ack
.PASS actual corrupted payload rejected; actual missing collection -> sanitized technical error
.PASS dense1024 Cosine/sparse/noIDF/9payload indexes/versioned fingerprint; incompatible rejected
.Real PostgreSQL: separate database t10_test_d463721e0b2a4282b6f50afa2d342278, public tables before migration=0
Real PostgreSQL: migrated separate database t10_test_d463721e0b2a4282b6f50afa2d342278
PASS isolation: app/user/current-session, explicit new registration, independent detach
...........PASS repeated/concurrent delete: one revision, retained rows byte-equivalent, no resurrection
.PASS real lock race: old coherent snapshot then revision invalidation; replay stays detached
......
52 passed in 76.89s (0:01:16)
```

### Full regression before final empty-map guard case

Command exact (exit0), expected/actual implemented checks PASS:

```powershell
uv run --no-sync pytest tests/unit tests/contract tests/security -q --tb=short --basetemp=.local/r22 -o cache_dir=.local/c22 *> .local/t22-regression.log
```

Actual excerpt; full ignored log `.local/t22-regression.log`:

```text
........................................................................ [ 14%]
........................................................................ [ 29%]
........................................................................ [ 43%]
........................................................................ [ 58%]
........................................................................ [ 72%]
........................................................................ [ 87%]
................................................................         [100%]
496 passed in 224.23s (0:03:44)
```

### Supplemental quality/review diagnostics

Actual supplemental command exit0:
`uv run --no-sync pytest tests/unit/test_evidence_policy.py -q --tb=short --basetemp=.local/22u1 -o cache_dir=.local/22uc1`
output `25 passed in 0.30s`. Synthetic protocol collaborators test config/response
failure boundaries only, never replace real success gates.

`uv run --no-sync ruff check . *> .local/t22-ruff-final.log` exit0,
`All checks passed!`; existing inaccessible scratch traversal warnings retained,
explicit eight changed Python files also format checked below. Initial import
format/annotation diagnostics fixed, initial mypy3errors invalid dynamic type alias
replaced with explicit EvidenceReason; no gate/semantics changed to hide failure.
Review found empty segments could raise IndexError before safe map validation;
reordered guard and added real durable empty-map corruption case. Initial docs
patch failed on wrong summary header anchor (atomic no file change), corrected.

Final quality commands each exit0:

```powershell
uv run --no-sync ruff format --check src/rag_core/domain/evidence.py src/rag_core/application/evidence.py src/rag_core/adapters/persistence/evidence.py src/rag_core/ports/evidence.py tests/fixtures/evidence_support.py tests/integration/test_evidence_selection.py tests/security/test_evidence_scope.py tests/unit/test_evidence_policy.py
uv run --no-sync mypy src
uv run --no-sync python scripts/export_openapi.py --check
uv lock --check --offline
git diff --check
```

Actual `8 files already formatted`; `Success: no issues found in 77 source files`;
`PASS designed_operations=13 served_health_routes=2 synthetic_examples=37`,
`PASS OpenAPI model + Draft2020-12 schemas=48; examples JSON Schema + Pydantic`,
`CONTRACT EXPORT: PASS (business endpoints unmounted; no runtime query/stream verification)`;
`Resolved 169 packages in 32ms`; git diff whitespace only preexisting CRLF warnings.
No public API/schema/model/index/DB/dependency migration, prompt corpus untouched.
`git check-ignore .local/t22-dod1-checkpoint.log .local/t22-regression.log` exit0
printed both paths: logs/helpers remain local/ignored and do not enter commit.

D1 PASS scoped13paths/dependency/whitespace/scratch preservation; D2 partial source
quality/regression above PASS, final source-map security recheck recorded below;
D3 BLOCKED missing conflict semantics/test, no task acceptance; D4 five living docs
partial interfaces/commands/status/limitations/ledgers updated; D5 scoped code/tests/
config-secrets/artifact review; D6 checkpoint only, **no completion commit**.
Checkpoint subject `docs(T22): checkpoint reranking pending conflict policy`;
actual hash/authorized push equality returned after execution, not inserted into
its own commit. T23 not dependency-ready; do not start next task.

### Final checkpoint rechecks (still NOT COMPLETE)

Implemented DoD-1 cases; required conflict gate still BLOCKED; actual command exit0:

```powershell
uv run --no-sync pytest tests/integration/test_evidence_selection.py -q -s --tb=short --basetemp=.local/22f1 -o cache_dir=.local/22fc1 *> .local/t22-dod1-checkpoint.log
```

Actual excerpt, full ignored `.local/t22-dod1-checkpoint.log`:

```text
.T21 REAL MODEL device=cpu pid=7 fingerprint=f25d7370e6e501a36aaba4da5c487ea790909d1a400d410e01f32348c34f534b runtime={'FlagEmbedding': '1.3.5', 'torch': '2.9.1+cpu', 'transformers': '4.57.6', 'tokenizers': '0.22.2', 'sentence-transformers': '5.1.2', 'peft': '0.17.1'} load=29.193s
T22 REAL20 rerank candidates ->8 passages; stable config/raw ranking, calibration pending
.
9 passed in 70.67s (0:01:10)
```

DoD-2 PASS including real empty-map tamper recheck; actual command exit0:

```powershell
uv run --no-sync pytest tests/security/test_evidence_scope.py -q -s --tb=short --basetemp=.local/22f2 -o cache_dir=.local/22fc2 *> .local/t22-dod2-checkpoint.log
```

Actual excerpt, full ignored `.local/t22-dod2-checkpoint.log`:

```text
.T21 REAL MODEL device=cpu pid=7 fingerprint=f25d7370e6e501a36aaba4da5c487ea790909d1a400d410e01f32348c34f534b runtime={'FlagEmbedding': '1.3.5', 'torch': '2.9.1+cpu', 'transformers': '4.57.6', 'tokenizers': '0.22.2', 'sentence-transformers': '5.1.2', 'peft': '0.17.1'} load=29.193s
T22 REAL history/foreign/text/allowlist generation-context guards PASS; no LLM invoked
.
13 passed in 89.62s (0:01:29)
```

D2 final source quality PASS as above;496full regression pre-empty-map case plus
13final real security89.62s includes the new safe-error case.52dependency76.89s,
25unit0.30s retained. D3 overall BLOCKED only mandatory conflict decision/test.
D4 command `uv run --no-sync python scripts/check_docs.py` exit0:

```text
PASS UTF-8/nonempty Markdown: 14 files
PASS internal links/anchors: 360
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```

Initial sandbox stage command `git add -- README.md RUNBOOK.md docs/tasks.md docs/handoffs.md docs/implementation-summary.md src/rag_core/domain/evidence.py src/rag_core/application/evidence.py src/rag_core/ports/evidence.py src/rag_core/adapters/persistence/evidence.py tests/fixtures/evidence_support.py tests/integration/test_evidence_selection.py tests/security/test_evidence_scope.py tests/unit/test_evidence_policy.py`
failed `fatal: Unable to create 'C:/Users/Admin/Documents/GitHub/rag-core/.git/index.lock': Permission denied`.
Compound read-check command overall exit0 masked this stage failure; nothing staged
until same exact scoped elevated stage succeeded exit0. No approval rejection or
request to bypass hook/history/security. Subsequent cached path/stat review exit0,
13task files/1464insertions/3deletions before final evidence append; no scratch staged.
Explicit D5 review of four source and four test/helper files, five living docs:
scope before rerank, exact source-map/text, language/subset/history boundary,
timeouts/cancel/error shape, partial status/calibration honesty. Empty-map issue
corrected with real guard regression, no schema/contract migration.

Actual `uv run --no-sync python .local/t22_review.py *> .local/t22-review.log`
exit0 (safe ignored local checker comparing exact path set/staged Git-filtered
hashes and added-line private-key/AWS/key markers plus cached whitespace):

```text
PASS exact13 T22 paths, staged/worktree filtered hashes, added-line key scan, whitespace
PASS no corpus/prompt/AGENTS/lock/migration/API/secrets/raw data/cache/scratch paths staged
T22 incomplete: checkpoint only; conflict DoD remains BLOCKED
```

Restage only task notes/handoffs evidence, repeat exact13hashes/docs/whitespace,
then checkpoint command `git commit -m "docs(T22): checkpoint reranking pending conflict policy"`.
Inspect actual commit parent/files/hash and push `git push origin main`, verify
`git ls-remote origin refs/heads/main` equals HEAD. Actual outputs returned after
execution (cannot record own hash in same commit). D6 checkpoint preservation
only, not COMPLETE; T23 cannot start. No amend/rewrite/force/merge/deploy.

Actual test cleanup command (elevated) exit0:

```powershell
docker compose -p rag-core-t22-test -f compose.metadata-test.yaml -f compose.qdrant-test.yaml -f compose.retrieval-test.yaml stop; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; docker compose -p rag-core-t22-test -f compose.metadata-test.yaml -f compose.qdrant-test.yaml -f compose.retrieval-test.yaml ps --all --format '{{.Name}} {{.State}}'
```

Actual output excerpt:

```text
Container rag-core-t22-test-qdrant-1 Stopped
Container rag-core-t22-test-postgres-1 Stopped
Container rag-core-t22-test-inference-1 Stopped
rag-core-t22-test-inference-1 exited
rag-core-t22-test-postgres-1 exited
rag-core-t22-test-qdrant-1 exited
```

No down/delete-volume/source/model-cache/scratch cleanup; existing application
services not operated on. Final docs checker exit0:14files/360links/37tasks/81edges,
`DOCUMENTATION CHECK: PASS`; final whitespace check exit0.


<a id="h-t22-a02"></a>
## H-T22-A02 - Phase 4 / ranked evidence and conservative numeric conflicts

Runtime direct Codex agent, exact model/effort unavailable; no subagents. Date
2026-10-06 Asia/Bangkok. Every command cwd
`C:\Users\Admin\Documents\GitHub\rag-core`. User delegated choice of best
conflict policy; selected conservative `numeric-claim-v1` to complete T22 without
adding semantic/NLI/LLM dependencies ahead of T23. This resolves A01 decision
blocker; historical A01 incomplete results remain untouched above. Original
DoD1/2 and D1-D6 kept; numeric baseline scope/limits documented, no lowered gate.

### Baseline/decision/source scope

Actual baseline command `git status --short; git branch --show-current; git rev-parse HEAD; git remote -v`
exit0:

```text
?? .ptmp-t07-a02/
?? .tmp-t07-a02/
main
74bb13019410bc2baf1fe911a2183ff5933716ea
origin https://github.com/admininistrator/rag-core.git (fetch)
origin https://github.com/admininistrator/rag-core.git (push)
```

Known global-ignore/inaccessible scratch warnings retained, no cleanup.
Read AGENTS/session prompt, T22 checkpoint/source and complete T21/T17 dependency
notes/interfaces/evidence, plan P01/P08/P09/P11/P13, README/RUNBOOK and ledgers.
Kept existing hydration/rerank/context implementation from inspected A01 checkpoint.
Mark IN_PROGRESS T22-A02 before code. User commit/push authorization persists.
One task only, no subagents, old worker/kanban, force/merge/deploy/Scarlet mutation.

Actual elevated resume command exit0:

```powershell
docker compose -p rag-core-t22-test -f compose.metadata-test.yaml -f compose.qdrant-test.yaml -f compose.retrieval-test.yaml up -d --wait; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; git ls-remote origin refs/heads/main
```

Output `Container rag-core-t22-test-postgres-1 Healthy`,
`Container rag-core-t22-test-qdrant-1 Healthy`,
`Container rag-core-t22-test-inference-1 Healthy`, and
`74bb13019410bc2baf1fe911a2183ff5933716ea refs/heads/main`.
Same pinned PG17.11/Qdrant1.19.1 tmpfs/loopback55432/56333 and read-only model cache,
T17 CPU image (unchanged); new code runs host source through real model HTTP58080.
Actual CPU fingerprint
`f25d7370e6e501a36aaba4da5c487ea790909d1a400d410e01f32348c34f534b`, PID7/two models,
load58.325s, FlagEmbedding1.3.5/Torch2.9.1+cpu/Transformers4.57.6/tokenizers0.22.2/
sentence-transformers5.1.2/peft0.17.1. BGE-M3 pin5617a9f61b028005a4858fdac845db406aefb181
and reranker pin953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e inherited verified T17
cache. No new weights/dependencies/model/provider change, GPU/LLM/corpus/load claim.

Common actual host environment, secret only read from file and never printed:

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'
$env:RAG_TEST_DATABASE_URL='postgresql://rag_core_test@127.0.0.1:55432/t10_acceptance'
$env:DATABASE_PASSWORD_FILE=Join-Path (Get-Location) '.local/secrets/t10_postgres_password'
$env:RAG_TEST_QDRANT_URL='http://127.0.0.1:56333'
$env:RAG_TEST_INFERENCE_URL='http://127.0.0.1:58080'
```

### Decision and behavior reviewed

Exact normalized statement/heading skeleton retains label/entity/period/qualifiers,
explicit units; mapped table headers + numeric-column unit + other row dimensions
retain entity/year. Decimal compares unambiguous values exactly. No unit/currency
scale conversion, translation, semantic entailment, grouped/ambiguous-number guess,
formula recalculation/cache certainty, unmapped metadata/history input. Numeric
helper runs off event loop, bounded <=20 authorized relevant candidates.
Conflict scan precedes passage/token budget, so reason conflicting_evidence wins
even when one passage or zero tokens fit; answerability insufficient_evidence.
First opposing pair prioritized if budget permits, preserving whole chunks/maps.
Same amount/different entity/metric/year/unit/qualifier tests avoid conflation;
foreign same-owner retained contradiction cannot influence current state.

Policy fingerprint includes literal conflict_policy numeric-claim-v1 and pending-T31
calibration, raw floor0.0 is not factual confidence. Trace schema1 adds count only,
no claim text/identity/IDs. Internal additive fields, public schema/API/DB/index/
dependency/model unchanged. Code/test total15task paths across A01+A02; A02 delta13
paths (five living docs +eight Python source/test paths). No raw corpus/gold changes.
Baseline is intentionally bounded: general semantic/paraphrase/cross-language,
text-table equivalent and un-retrieved-document contradictions are not measured
or advertised; supported is not proof of complete multi-hop/claim coverage.

### DoD-1 PASS - real reranker, vectors and durable source maps

Exact command exit0; expected/actual all cases PASS:

```powershell
uv run --no-sync pytest tests/integration/test_evidence_selection.py -q -s --tb=short --basetemp=.local/22a2d1 -o cache_dir=.local/22a2c1 *> .local/t22-a02-dod1.log
```

Actual excerpt, full ignored log `.local/t22-a02-dod1.log`:

```text
T22 REAL cross-language vi supported raw=2.8313
T22 REAL cross-language en supported raw=4.9300
T22 REAL irrelevant nearest neighbor -> insufficient / zero context
T22 REAL conflicting12.5/14.5 million USD ->insufficient/conflicting passage_limit=8 tokens=8000
T22 REAL conflicting12.5/14.5 million USD ->insufficient/conflicting passage_limit=1 tokens=8000
T22 REAL conflicting12.5/14.5 million USD ->insufficient/conflicting passage_limit=8 tokens=1
T22 REAL conflicting XLSX14.5/12.5 ->insufficient/conflicting; both headers/maps retained
T22 REAL multi-evidence=3 numeric/unit/header/source-map PASS
T22 REAL HTTP rerank cancelled; subsequent real rerank supported
T22 REAL20 rerank candidates ->8 passages; stable config/raw ranking, calibration pending
14 passed in 103.34s (0:01:43)
```

### DoD-2 PASS - real scope/history/context gate and threshold docs

Exact command exit0; expected/actual all cases PASS:

```powershell
uv run --no-sync pytest tests/security/test_evidence_scope.py -q -s --tb=short --basetemp=.local/22a2d2 -o cache_dir=.local/22a2c2 *> .local/t22-a02-dod2.log
```

Actual excerpt, full ignored log `.local/t22-a02-dod2.log`:

```text
T22 REAL history/foreign/text/allowlist generation-context guards PASS; no LLM invoked
14 passed in 65.89s (0:01:05)
```

### Focused policy and numeric ambiguity/source-role risk tests PASS

Exact command exit0; expected/actual all cases PASS:

```powershell
uv run --no-sync pytest tests/unit/test_evidence_policy.py tests/unit/test_evidence_conflicts.py -q --tb=short --basetemp=.local/22a2u2 -o cache_dir=.local/22a2uc2 *> .local/t22-a02-unit.log
```

Actual excerpt, full ignored log `.local/t22-a02-unit.log`:

```text
45 passed in 0.32s
```

DoD1 includes all original real cases plus text conflicting12.5/14.5 million USD,
conflict under passage_limit1/context_tokens1, different-period supported and XLSX
opposing numeric values with headers/maps retained. Actual CPU model required,
no synthetic/fake score fallback. DoD2 includes foreign app/user/retained same-owner
session, subset/language/forged metadata/generation/history/text/maps, detach/delete
at hydrate/rerank/context stages, durable empty-map tamper and outside-session
contradiction excluded. No LLM call claim; context_for_generation boundary is T22
output for T24's later provider/system-policy framing. RUNBOOK pending-T31/non-
probability/limitations updated with implementation.

### D2 quality and retained diagnostics

Actual commands each exit0:

```powershell
uv run --no-sync ruff check src/rag_core/domain/evidence.py src/rag_core/domain/evidence_conflicts.py src/rag_core/application/evidence.py tests/unit/test_evidence_policy.py tests/unit/test_evidence_conflicts.py tests/fixtures/evidence_support.py tests/integration/test_evidence_selection.py tests/security/test_evidence_scope.py
uv run --no-sync mypy src
uv lock --check --offline
uv run --no-sync python scripts/export_openapi.py --check
```

Actual outputs `All checks passed!`, `Success: no issues found in 78 source files`,
`Resolved 169 packages in 39ms`,
`PASS designed_operations=13 served_health_routes=2 synthetic_examples=37`,
`PASS OpenAPI model + Draft2020-12 schemas=48; examples JSON Schema + Pydantic`,
`CONTRACT EXPORT: PASS (business endpoints unmounted; no runtime query/stream verification)`.
Whole `uv run --no-sync ruff check . *> .local/t22-a02-ruff.log` also exit0,
`All checks passed!`, known old scratch traversal permission warnings retained.
Initial scoped Ruff import formatting fixed automatically and focused43test initial
run PASS0.35s; final45test run adds unknown detector rejection/table cache/dimension
guards, no skipped/removed test or changed gold. Failed text patch on formatted
unit-test anchor made no edits (atomic), corrected; not a test failure or gate change.


### D1-D6 closure evidence

Actual regression command exit0:

```powershell
uv run --no-sync pytest tests/unit tests/contract tests/security -q --tb=short --basetemp=.local/r22a2 -o cache_dir=.local/c22a2 *> .local/t22-a02-regression.log
```

Expected/actual all unit/contract/security PASS, no skip/mock substitute for real
model gates. Actual excerpt; full ignored log `.local/t22-a02-regression.log`:

```text
........................................................................ [ 97%]
..............                                                           [100%]
518 passed in 202.67s (0:03:22)
```

Final quality commands each exit0:

```powershell
uv run --no-sync ruff check . *> .local/t22-a02-ruff-final.log
uv run --no-sync ruff format --check src/rag_core/domain/evidence.py src/rag_core/domain/evidence_conflicts.py src/rag_core/application/evidence.py tests/fixtures/evidence_support.py tests/integration/test_evidence_selection.py tests/security/test_evidence_scope.py tests/unit/test_evidence_policy.py tests/unit/test_evidence_conflicts.py
uv run --no-sync python scripts/check_docs.py
git diff --check
```

Actual `All checks passed!` (known old scratch traversal permission warnings),
`8 files already formatted`, docs:

```text
PASS UTF-8/nonempty Markdown: 14 files
PASS internal links/anchors: 365
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```

Whitespace check exit0, only existing CRLF normalization warnings. D1 PASS scope/
dependency notes/checkpoint/tombstone source ownership/scratch preservation;
D2 PASS45focused unit0.32s,518regression202.67s, final Ruff/mypy78/locked169 and
unchanged structural OpenAPI. D3 PASS separate original real DoD1/2 above.
D4 PASS five living docs status/contracts/DI/profiles/errors/budgets/conflict
semantics/thresholds/tests/migration-N/A/limits and ledger/checkpoint updated.
No API/index/DB/dependency/model migration because changes are internal evidence
policy/helper and additive private trace field; public query/generation remains future.

Actual elevated own test project stop/state command exit0:

```powershell
docker compose -p rag-core-t22-test -f compose.metadata-test.yaml -f compose.qdrant-test.yaml -f compose.retrieval-test.yaml stop; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; docker compose -p rag-core-t22-test -f compose.metadata-test.yaml -f compose.qdrant-test.yaml -f compose.retrieval-test.yaml ps --all --format '{{.Name}} {{.State}}'
```

Actual output:

```text
Container rag-core-t22-test-qdrant-1 Stopped
Container rag-core-t22-test-postgres-1 Stopped
Container rag-core-t22-test-inference-1 Stopped
rag-core-t22-test-inference-1 exited
rag-core-t22-test-postgres-1 exited
rag-core-t22-test-qdrant-1 exited
```

No down/delete volumes/source/cache/scratch. Existing applications/Scarlet untouched.
D5 source/test review includes mapped-only numeric comparison, exact time/unit/
qualifiers, table entity dimensions, formula-cache ambiguity, full relevant scan
before budget, ordered opposing pair, no foreign effects, safe trace and post-stage
scope revalidation. Unit text-patch diagnostics retained above; no gate lowered.
Review/stage exact13paths and filtered hashes/secrets below. D6 subject
`feat(T22): select ranked evidence with answerability state` (completion), actual
commit/parent/files/hash/push/remote equality returned after execution, not embedded
in its own commit. A01 checkpoint74bb130 remains immutable history. No amend/
force/merge/deploy. T23 dependencies T22/T20 ready after inspected completion,
stays TODO; STOP T22.

Final A02 scoped stage command (elevated) exit0:

```powershell
git add -- README.md RUNBOOK.md docs/tasks.md docs/handoffs.md docs/implementation-summary.md src/rag_core/domain/evidence.py src/rag_core/domain/evidence_conflicts.py src/rag_core/application/evidence.py tests/fixtures/evidence_support.py tests/integration/test_evidence_selection.py tests/security/test_evidence_scope.py tests/unit/test_evidence_policy.py tests/unit/test_evidence_conflicts.py
uv run --no-sync python .local/t22_a02_review.py *> .local/t22-a02-review.log
uv run --no-sync python scripts/check_docs.py
git diff --cached --stat
git status --short
git ls-remote origin refs/heads/main
```

Each read/review command exit0, actual output excerpt before evidence-only restage:

```text
PASS A02 exact13paths; checkpoint parent; staged/worktree filtered hashes; added-line key scan; whitespace
PASS no corpus/prompt/AGENTS/lock/migration/API/raw data/secrets/cache/scratch staged
PASS completion subject feat(T22): select ranked evidence with answerability state
PASS UTF-8/nonempty Markdown: 14 files
PASS internal links/anchors: 365
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
13 files changed, 677 insertions(+), 28 deletions(-)
74bb13019410bc2baf1fe911a2183ff5933716ea refs/heads/main
```

Only13T22 paths staged, inherited two scratch directories untracked unchanged.
D5 PASS exact source/test/docs paths, code/behavior/secret/artifact review; local
checker/logs ignored. Restage only this evidence append and repeat same exact13
filtered hashes/docs/whitespace before completion commit. D1-D5 PASS, D6 actual
commit inspection/push/hash equality returned after execution. No unresolved blocker,
raw threshold pending T31 and conservative semantic limits documented. STOP T22.


<a id="h-t23-a01"></a>
## H-T23-A01 - Phase 5 / provider adapters / 2026-10-06

### Identity, scope, baseline and official references

Direct Codex agent, exact model/effort unavailable, no subagents. Cwd for every
command in this entry: `C:/Users/Admin/Documents/GitHub/rag-core`. Client date/timezone:
2026-10-06 Asia/Bangkok. Assigned T23 only; user authorizes scoped commit and
origin/current branch push, no force/merge/deploy/drain. Initial main HEAD
`3e6821b814282ef0a6859a9414ecf8f8d29fdf72` (T22 completion), T22/T20 COMPLETE notes,
interfaces, P01/P02/P05/P09/P13, AGENTS/session prompt and living docs read.
No partial tracked T23 source. Initial `git status --short` exit0:

```text
?? .ptmp-t07-a02/
?? .tmp-t07-a02/
```

Known inaccessible legacy scratch warnings retained, no cleanup. `git branch --show-current`
exit0 `main`; `git rev-parse HEAD` exit0 hash above; `git remote -v` exit0 origin fetch/push
`https://github.com/admininistrator/rag-core.git`. Initial sandbox
`git ls-remote origin refs/heads/main` exit128:

```text
fatal: unable to access 'https://github.com/admininistrator/rag-core.git/': Failed to connect to github.com port 443 after 38 ms: Could not connect to server
```

Same read-only command with network escalation exit0:

```text
3e6821b814282ef0a6859a9414ecf8f8d29fdf72	refs/heads/main
```

No permission rejection or user approval blocker. Secrets never printed. Initial
PowerShell-to-Python document update did not match Vietnamese text due to console
encoding; detected with Git diff and corrected via UTF-8 apply_patch. Task status/
notes are now explicit T23-A01; no fabricated prior mutation/verification claim.

Official sources checked with web tool before adapter code, not copied into corpus:
[DeepSeek Chat Completions](https://api-docs.deepseek.com/api/create-chat-completion/),
[DeepSeek JSON mode](https://api-docs.deepseek.com/guides/json_mode/),
[Anthropic Messages](https://platform.claude.com/docs/en/api/messages/create),
[Anthropic streaming](https://platform.claude.com/docs/en/build-with-claude/streaming),
[Anthropic Python SDK](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python).
Direct DeepSeek opens timed out; official indexed reference content retrieved by
search contains native request/finish/SSE/usage schema. Current DeepSeek final
finish chunk carries usage; legacy usage-only chunk remains explicitly tested.
Anthropic native top-level system, message/block stream flow/cumulative usage,
SDK retries/timeout/raw response and distinct HTTPX2 behavior checked. No default
model ID inferred from examples or hardcoded. Live-provider verification belongs
T26 per original T23 DoD, no missing keys used to bypass a gate.

### Environment and SDK pin

Actual setup command (network escalation; workspace cache/interpreter paths):

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; $env:UV_PYTHON_INSTALL_DIR=Join-Path (Get-Location) '.uv-python'; uv add --group api anthropic
```

Exit0 actual output excerpt:

```text
Resolved 177 packages in 11.21s
Prepared 8 packages in 6.10s
Installed 8 packages in 910ms
 + anthropic==1.11.0
 + docstring-parser==0.18.0
 + httpcore2==2.13.1
 + httpx2==2.13.1
 + jiter==0.17.0
 + sniffio==1.3.1
 + truststore==0.10.4
```

Changed API specifier to exact `anthropic==1.11.0`; `uv lock --offline` exit0
`Resolved 177 packages in 115ms`. Lock additionally includes platform-conditional
httpx2-jsfetch1.0;169existing package versions unchanged, official PyPI URLs/hashes.
Initial unconfigured `uv pip show anthropic` failed opening global user cache
(Access denied); subsequent commands use workspace UV_CACHE_DIR, no bypass.

Actual commands each exit0:

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; uv sync --locked --offline --group dev --group api --group ingestion --group inference
uv run --no-sync python -c "import sys, anthropic, httpx, httpx2; print(sys.version); print('anthropic='+anthropic.__version__+' httpx='+httpx.__version__+' httpx2='+httpx2.__version__)"
uv lock --check --offline
```

Output excerpts:

```text
Resolved 177 packages in 1ms
3.12.4 | packaged by Anaconda, Inc. | (main, Jun 18 2024, 15:03:56) [MSC v.1929 64 bit (AMD64)]
anthropic=1.11.0 httpx=0.28.1 httpx2=2.13.1
Resolved 177 packages in 36ms
```

### DoD-1 PASS - distinct protocol fixtures, native SDK and transport lifecycle

Actual command exit0 (UV_CACHE_DIR workspace as above):

```powershell
uv run --no-sync pytest tests/contract/test_llm_providers.py -q --tb=short --basetemp=.local/23-dod1 *> .local/t23-a01-dod1.log
```

Expected native request/JSON/SSE schema, missing usage, split UTF-8 frames,
429/5xx/retry bounds, malformed event, timeout/disconnect/cancel all PASS, no
retry after emitted delta. Actual full ignored log `.local/t23-a01-dod1.log`:

```text
........................................................................ [ 56%]
.......................................................                  [100%]
127 passed in 4.63s
```

Synthetic fixtures, real HTTPX0.28.1 / HTTPX2 2.13.1 MockTransport and actual
Anthropic1.11.0 SDK request/error/raw-response API; no live model/keys/network.
T23 specifically requires recorded/synthetic protocols, not live substitution.
Covers JSON/native headers/model/output budgets, single-byte split multibyte EN/VI
SSE, comments/multiline/CR-LF-CRLF, missing/cache/cumulative usage, current/legacy
DeepSeek finish usage, native Anthropic block/message order/future event handling,
HTTP/in-band transient retry, permanent errors, exact exhausted attempt count,
pre-delta disconnect/timeout retry, post-delta disconnect/EOF/timeout/truncation
without retry/completed, malformed/oversized/tool events and JSON, request/context/
output bounds and constructed copies, cancellation/consumer-close/paused-caller
cleanup, strict EN/VI question-only rewrite, untrusted history kept out of policy.
No factual-answer/citation/prompt-injection-compliance model claim.

### DoD-2 PASS - independent config/secrets and documented live boundary

Actual separate command exit0:

```powershell
uv run --no-sync pytest tests/contract/test_llm_providers.py -k 'config or redirect_following' -q --tb=short --basetemp=.local/23-dod2 *> .local/t23-a01-dod2.log
```

Expected both providers configure independently, no other-provider key requirement
or fallback, redaction survives malformed config/upstream errors; README/RUNBOOK
explain T26 live gates. Actual log `.local/t23-a01-dod2.log`:

```text
..................                                                       [100%]
18 passed, 109 deselected in 2.22s
```

Deselection is intentional separate configuration subset, not skipped acceptance;
all127tests ran in DoD-1. Two independently configured profiles tested together,
selected-provider missing key fails despite other valid key/model, safe repr/JSON/
traceback, env field names and invalid constructed config, HTTPS/key/model/retry/
timeout bounds, redirect-following Anthropic pool rejection. No plaintext key value
committed. All key-shaped fixtures are explicit non-credential synthetic strings.
README/RUNBOOK/.env.example enumerate selected-provider config and no model default.
Planned T26 commands `uv run python scripts/smoke_llm.py --provider deepseek` and
`uv run python scripts/smoke_llm.py --provider anthropic` remain planned: public routes
and smoke script do not yet exist. No live PASS recorded, no DoD lowered.

### Retained diagnostics and corrections

Initial scoped Ruff found4import/unused-import findings; auto-fixed in task files.
Initial mypy found2iterator `aclose` typing errors; corrected private `_stream` return
to AsyncGenerator. Final whole-source type check below PASS85sources, no ignores added.
Initial89protocol tests PASS2.65s. Expanded test run:

```powershell
uv run --no-sync pytest tests/contract/test_llm_providers.py -q --tb=short --basetemp=.local/23-second
```

Exit1 actual excerpts:

```text
E   TypeError: rag_core.adapters.llm.config.DeepSeekSettings() got multiple values for keyword argument 'retry_base_seconds'
E   assert (0 == 1)
5 failed, 119 passed in 3.96s
```

One fixture helper passed both default and explicit retry_base_seconds; corrected
using settings.pop. SDK lazy request setup could consume the test-only10/30ms
whole-operation deadlines before request, so deadlines now200ms and deterministic
retry-base1s > remaining deadline. Same total-deadline/no-retry/cleanup behavior
asserted, no provider acceptance gate removed. Failed correction command exited1:
`UnicodeDecodeError: 'charmap' codec can't decode byte 0x81 in position 17023`;
explicit UTF-8 read/write corrected it. Another patch failed atomically on formatted
line context; corrected against actual file. No partial edits or evidence fabricated.

Intermediate logs retained `.local/t23-a01-protocol-initial.log` (4failed120passed3.40s),
`.local/t23-a01-protocol-final.log` (2failed122passed5.31s),
`.local/t23-a01-protocol-final2.log` (2failed122passed4.66s).
Final pre-closure127PASS log is DoD-1 above. First broad regression started before
helper fix finished collecting, so used the old helper (all4failures from helper):

```powershell
uv run --no-sync pytest tests/unit tests/contract tests/security -q --tb=short --basetemp=.local/r23a1 -o cache_dir=.local/c23a1 *> .local/t23-a01-regression.log
```

Exit1 actual tail, `.local/t23-a01-regression.log`:

```text
4 failed, 638 passed in 210.15s (0:03:30)
```

Full rerun after all source/test fixes passes below. Intermediate documentation
check failed because newly referenced `#h-t23-a01` evidence was not yet appended;
this entry closes the anchor. No dependency/model/gold changes to mask failures.

### D2/D3 - final regression and real dependency boundaries

Test project is isolated loopback PG/Qdrant/tmpfs + existing read-only shared model
cache, same pinned T17 CPU service image as T20/T22 acceptance. No provider credentials,
application volumes, source writes or Scarlet changes. Real integration/security
fixtures use PG/Qdrant/CPU inference; provider protocol tests remain synthetic.
Actual service preparation (network/Docker escalation) exit0:

```powershell
docker compose -p rag-core-t23-test -f compose.metadata-test.yaml -f compose.qdrant-test.yaml -f compose.retrieval-test.yaml up -d --wait
```

Actual output includes all3services Healthy. Regression command (escalation) exit0:

```powershell
$env:UV_CACHE_DIR=Join-Path (Get-Location) '.uv-cache'; $env:RAG_TEST_DATABASE_URL='postgresql://rag_core_test@127.0.0.1:55432/t10_acceptance'; $env:DATABASE_PASSWORD_FILE=Join-Path (Get-Location) '.local/secrets/t10_postgres_password'; $env:RAG_TEST_QDRANT_URL='http://127.0.0.1:56333'; $env:RAG_TEST_INFERENCE_URL='http://127.0.0.1:58080'; uv run --no-sync pytest tests/unit tests/contract tests/security -q --tb=short --basetemp=.local/r23a1f -o cache_dir=.local/c23a1f *> .local/t23-a01-regression-final.log
```

Expected all prior518tests+127T23 tests PASS, no skip. Actual output excerpt from
`.local/t23-a01-regression-final.log`:

```text
........................................................................ [ 89%]
.....................................................................    [100%]
645 passed in 200.23s (0:03:20)
```

Quality commands each exit0:

```powershell
uv run --no-sync ruff check . *> .local/t23-a01-ruff.log
uv run --no-sync ruff format --check src/rag_core/adapters/llm src/rag_core/domain/llm.py src/rag_core/ports/llm.py tests/contract/test_llm_providers.py
uv run --no-sync mypy src
uv run --no-sync python scripts/export_openapi.py --check
git diff --check
```

Actual outputs:

```text
All checks passed!
8 files already formatted
Success: no issues found in 85 source files
PASS checked docs/api/openapi-v1.designed.json
PASS checked docs/api/openapi.served.json
PASS checked docs/api/examples-v1.json
PASS designed_operations=13 served_health_routes=2 synthetic_examples=37
PASS OpenAPI model + Draft2020-12 schemas=48; examples JSON Schema + Pydantic
CONTRACT EXPORT: PASS (business endpoints unmounted; no runtime query/stream verification)
```

Ruff retains3known legacy scratch Access denied warnings; exit0. Git whitespace
exit0 with existing CRLF-to-LF normalization warnings; no content issue. Actual
post-regression service state/stop command (escalation) exit0:

```powershell
docker compose -p rag-core-t23-test -f compose.metadata-test.yaml -f compose.qdrant-test.yaml -f compose.retrieval-test.yaml ps --all --format '{{.Name}} {{.State}} {{.Health}}'; docker compose -p rag-core-t23-test -f compose.metadata-test.yaml -f compose.qdrant-test.yaml -f compose.retrieval-test.yaml stop; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; docker compose -p rag-core-t23-test -f compose.metadata-test.yaml -f compose.qdrant-test.yaml -f compose.retrieval-test.yaml ps --all --format '{{.Name}} {{.State}}'
```

Actual excerpts:

```text
rag-core-t23-test-inference-1 running healthy
rag-core-t23-test-postgres-1 running healthy
rag-core-t23-test-qdrant-1 running healthy
rag-core-t23-test-inference-1 exited
rag-core-t23-test-postgres-1 exited
rag-core-t23-test-qdrant-1 exited
```

No down -v, no deletion/move of source/cache/scratch/original data.

### D1/D4/D5/D6 - review and completion boundary

All16task paths:7private domain/port/adapter source files,1contract suite, API
pyproject/lock, env example, README/RUNBOOK and3ledgers. No public contract/route,
DB/index/parser/model/Compose migration. Native SDK success JSON/SSE bodies bounded;
SDK itself handles HTTP error body decoding. Input charge is conservative UTF-8
processing units, not provider billing; T24 must enforce assembled prompt and scope.
Live smoke/model behavior/factual quality/citations/public endpoints remain T24-T26;
no deployment/Scarlet/server integration claim. T24 dependencies T23/T22/T16 ready
only after successful inspected completion commit; remains TODO, STOP T23.

Actual review helper command exit0:

```powershell
uv run --no-sync python .local/t23_a01_review.py
```

Actual output:

```text
PASS tracked changes within16T23allowed paths; new files explicitly reviewed
PASS UTF8/size/new-source and added-line private-key/API-key-pattern scan (synthetic fixtures reviewed)
PASS domain/port no transport/framework SDK imports; no public schema/migration change
PASS169existing locked versions unchanged;8new SDK packages use official PyPI
PASS prompt corpus unchanged; no raw sources/secrets/weights/cache/scratch staged
PASS configured Git author; identity value not printed
```

Helper is ignored runtime evidence only, not source to commit. Final docs/staged
checks and inspected completion commit/push boundary append below. Completion
subject `feat(T23): support DeepSeek and Anthropic generation`; actual hash/remote
equality reported post-execution, never self-hash/amend. COMPLETE effective only
once inspected commit succeeds; push authorized origin/main, no force/merge/deploy.


### Final D1-D6 documentation and review closure

Initial full-history secret-pattern scan exited1 at `AssertionError: docs/handoffs.md`:
historical evidence includes key marker text outside T23 changes. Review helper now
scans complete new source/test/env and added lines in existing docs/config/lock, while
retaining UTF-8/size checks on every file; no old evidence altered or credential
printed. Final helper PASS above is actual corrected output, not initial failure.

Actual final documentation/whitespace commands each exit0:

```powershell
uv run --no-sync python scripts/check_docs.py
git diff --check
```

Output:

```text
PASS UTF-8/nonempty Markdown: 14 files
PASS internal links/anchors: 371
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```

D1 PASS dependency/checkpoint/scope/whitespace; D2 PASS127protocol+645regression,
Ruff/format/mypy85/locked177/OpenAPI; D3 PASS original separate DoD1/2;
D4 PASS README/RUNBOOK/env/notes/checkpoint/summary and documentation validator;
D5 PASS native schemas/retry/emitted-token guard/usage/null/cancel/deadline/prompt
data separation, new-source/added-line secrets/artifacts, all169prior locked versions
unchanged/8new SDK packages, no public/API/DB/index/model/corpus migration.
D6 scoped16path stage/filtered hash/cached whitespace review and completion subject
`feat(T23): support DeepSeek and Anthropic generation`; actual inspected commit hash
and authorized origin/main equality returned after execution. No self-hash/amend.
No unresolved T23 blocker. Live availability/model compliance/public query/generation/
citations remain T24-T26. T24 dependencies T23/T22/T16 ready after inspected successful
completion commit; remains TODO. Own services stopped, sources/cache/old scratch
unchanged; STOP T23.


### D6 actual staged candidate

Actual explicit stage command (Git escalation) exit0:

```powershell
git add -- .env.example README.md RUNBOOK.md docs/tasks.md docs/handoffs.md docs/implementation-summary.md pyproject.toml uv.lock src/rag_core/domain/llm.py src/rag_core/ports/llm.py src/rag_core/adapters/llm/__init__.py src/rag_core/adapters/llm/config.py src/rag_core/adapters/llm/common.py src/rag_core/adapters/llm/deepseek.py src/rag_core/adapters/llm/anthropic.py tests/contract/test_llm_providers.py
```

Actual `uv run --no-sync python .local/t23_a01_review.py --staged` exit0:

```text
PASS exact16T23staged paths and filtered worktree/index hashes
PASS UTF8/size/new-source and added-line private-key/API-key-pattern scan (synthetic fixtures reviewed)
PASS domain/port no transport/framework SDK imports; no public schema/migration change
PASS169existing locked versions unchanged;8new SDK packages use official PyPI
PASS prompt corpus unchanged; no raw sources/secrets/weights/cache/scratch staged
PASS configured Git author; identity value not printed
```

`git diff --cached --check` exit0, no output; `git diff --cached --stat` confirms16files
including7source/1test/3env-dependency files/5living docs. `git status --short` shows
only16staged task paths plus inherited `.ptmp-t07-a02/`, `.tmp-t07-a02/` untracked.
Final docs command after task/summary closure exit0:

```text
PASS UTF-8/nonempty Markdown: 14 files
PASS internal links/anchors: 373
PASS task fields/status/dependencies: 37 tasks, 81 edges, acyclic
DOCUMENTATION CHECK: PASS
```

This evidence append is restaged and reviewed with the same helper/whitespace/docs
commands before `git commit -m "feat(T23): support DeepSeek and Anthropic generation"`.
Then inspect commit/parent/exact16files, `git push origin main` without force and
`git ls-remote origin refs/heads/main`; actual outputs/hash/equality reported directly
to user after execution. No commit hash written into its own commit. COMPLETE only
with successful inspected completion commit, STOP T23, T24 remains TODO.
