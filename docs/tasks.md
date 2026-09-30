# RAG Core — Phases và tasks

> Trạng thái khởi tạo: T00 COMPLETE khi completion commit tồn tại; T01–T36 TODO. Chưa có code ứng dụng.
> Workflow hiện hành: **một task được chỉ định trong mỗi session**, agent trực tiếp thực hiện rồi dừng theo [AGENTS.md](../AGENTS.md) và [P14](plan.md#p14). Ghi chú Codex/Hermes trước đây là lịch sử.

## Quy ước bắt buộc

- Trạng thái: `TODO` (chưa làm), `IN_PROGRESS` (đang dở), `BLOCKED` (có trở ngại), `COMPLETE` (đã nghiệm thu + commit).
- Thứ tự T00 đến T36 là thứ tự drain. Mỗi task phụ thuộc task liền trước; dependency bổ sung nhắc các phần cần đọc lại. Không chạy song song dù dependency kỹ thuật có thể cho phép.
- Mọi task kế thừa [DoD D1–D6](plan.md#p13), gồm cập nhật README/RUNBOOK, nhật ký và Git commit. DoD bên dưới bổ sung, không thay thế D1–D6.
- Lệnh ở task TODO là hợp đồng nghiệm thu **cần được task tạo và chạy**, chưa phải command hiện đang hoạt động. Không tạo test rỗng để command exit 0. `pytest` không được skip/no-tests thay PASS.
- Integration nghĩa chạy dependency thật; live nghĩa gọi provider thật có chủ đích. Output mock chỉ chứng minh test mock.
- Sau mỗi attempt ghi **dưới đúng task**: agent/model/effort, start/end, files, việc thực hiện, DoD IDs + evidence links, README/RUNBOOK changes hoặc lý do N/A, commit subject/hash resolver, blockers/next action. Chi tiết dài ở handoffs/summary.
- Không sửa DoD/mark COMPLETE để vượt blocker. Xem [handoffs.md](handoffs.md) để biết worktree/attempt hiện tại.

## Human Task — Hermes Git author identity (2026-09-26)

- **T-H1 — cấu hình Git author cho repo:** COMPLETE theo người dùng xác nhận và Orchestrator kiểm `git var GIT_AUTHOR_IDENT` exit 0 (không in identity). Trước đó exit 128: `Author identity unknown`; không tạo danh tính giả hoặc thay đổi Git config bằng agent. Completion commits T07 trở đi không còn bị chặn bởi identity. Giữ T00–T36 và các trạng thái task chuẩn nguyên vẹn.
- **T-H2 — phê duyệt phép đọc kiểm hash/mtime T07:** HUMAN APPROVAL RECEIVED ngày 2026-09-26: người dùng xác nhận nguyên văn “Tôi phê duyệt riêng phép kiểm hash/mtime bị từ chối ở card t_88f601c9.” Phê duyệt chỉ cho đúng Python read-only snapshot toàn `corpus-documents/bilingual/` đã ghi trong board log A04 (tree SHA256, mtime-map SHA256, QA-slice SHA256, source receipts/counts), không blanket bypass, không xóa scratch, không hạ/skip DoD. A04 trước đó bị `Timeout — denying command` ~60.4s nên lệnh chưa chạy. Worker A05 mới có thể thử đúng phép kiểm đã được người dùng phê duyệt; nếu terminal vẫn từ chối, dừng ngay, không rephrase/route quanh. T-H2 hoàn tất về mặt quyết định của người dùng; technical gate và T07 DoD vẫn phải chứng minh bằng output thật.

## Phase 0 — Hồ sơ và nền tảng

<a id="t00"></a>
### T00 — Khởi tạo bộ hồ sơ dự án

- **Trạng thái:** COMPLETE
- **Phụ thuộc:** Không.
- **Tham chiếu kế hoạch:** [P00](plan.md#p00), [P14](plan.md#p14), [P15](plan.md#p15).
- **Công việc:** Tạo plan/tasks/AGENTS/handoffs/implementation-summary; điền skeleton README/RUNBOOK đang rỗng; chốt các quyết định người dùng, chuẩn bị prompt Orchestrator. Không viết ứng dụng hoặc chạy corpus.
- **Xong khi thỏa mãn DoD:**
  1. Bảy file có nội dung UTF-8, link/anchor nội bộ hợp lệ; đủ task fields và dependency graph không có chu trình.
  2. Scope session, worker model/effort/context mới, tuần tự, commit và docs đồng thời nhất quán giữa các file; chỉ T00 có thể COMPLETE.
  3. Kiểm tra staged diff và tạo `docs(T00): establish RAG core implementation blueprint`; lưu output thật ở handoff. Prompt Orchestrator được gửi cho người dùng.
- **Cạm bẫy:** Không coi kế hoạch là code đã chạy; không đưa T01 trở đi vào COMPLETE; không sửa prompt corpus gốc hay commit file người dùng ngoài scope.
- **Ghi chú thực thi:** Initial planning session, 2026-09-15; bảy file Markdown, 37 tasks/10 phases. DoD-1/2 PASS (136 internal links/anchors, fields/dependencies/UTF-8); DoD-3 staged check PASS, completion commit theo subject ở trên là điều kiện đóng T00. README/RUNBOOK đã có skeleton và contract DESIGNED. Không có app/corpus implementation. Evidence [H-T00](handoffs.md#h-t00), decisions [S-T00](implementation-summary.md#s-t00). Task tiếp theo T01; giữ prompt corpus untracked cho T01 stage nguyên bản.

<a id="t01"></a>
### T01 — Python project, cấu trúc và quality commands

- **Trạng thái:** COMPLETE
- **Phụ thuộc:** T00.
- **Tham chiếu kế hoạch:** [P02](plan.md#p02), [P13](plan.md#p13), [P15](plan.md#p15).
- **Công việc:** Tạo src layout, Python 3.12/uv lock, dependency groups, typed settings, Ruff/mypy/pytest markers, .gitignore/.env.example/.gitattributes (UTF-8, LF); script `scripts/check_docs.py` kiểm links/anchors/task fields/deps. Đưa prompt corpus nguyên bản vào Git ở task này sau kiểm nội dung. README có prerequisites; RUNBOOK có bảng env chưa chứa secret.
- **Xong khi thỏa mãn DoD:**
  1. `uv sync --locked --group dev`, `uv run ruff check .`, `uv run mypy src`, `uv run pytest tests/unit/test_settings.py` PASS; settings thiếu secret/config cần thiết báo lỗi có ý nghĩa.
  2. `uv run python scripts/check_docs.py` PASS; raw corpus, .env, model weights và runtime files được ignore; lock thực sự tái tạo env.
- **Cạm bẫy:** Máy đang có Python 3.13 không thay baseline 3.12 âm thầm; không gom heavyweight ML dependencies vào API; không commit secret; không ghi command Docker đã hoạt động.
- **Ghi chú thực thi:** Attempt `T01-A01` | worker/model/effort/context `gpt-5.6-sol`/`xhigh`/fresh (`fork_turns="none"`) | 2026-09-15 22:16–22:35 +07:00. Implemented: Python `3.12.*` src package + `py.typed`, uv lock/groups base/api/ingestion/inference/dev, typed safe settings, Ruff/mypy/pytest markers, docs validator, ignore/UTF-8-LF/env policy; prompt corpus stage nguyên byte. Files: `.python-version`, `.gitattributes`, `.gitignore`, `.env.example`, `pyproject.toml`, `uv.lock`, `src/rag_core/**`, `scripts/check_docs.py`, `tests/unit/test_settings.py`, README/RUNBOOK và ba sổ docs, prompt gốc. DoD-1 PASS: locked sync CPython 3.12.4, Ruff, mypy, 3 settings tests; missing `DATABASE_URL`/`REDIS_URL` báo tên rõ, malformed DSN không lộ input trong repr/traceback. DoD-2 PASS: docs links/anchors/37-task graph; raw/generated corpus, `.env`, root model/runtime artifacts ignored trong khi source model adapter/corpus scripts/prompt vẫn trackable; lock check/Python proof. D1–D5 PASS theo [H-T01-A01](handoffs.md#h-t01-a01); D6 subject `feat(T01): scaffold Python project and quality checks`, COMPLETE hợp lệ sau completion commit thành công và Orchestrator review; hash trả ngoài commit. README/RUNBOOK cập nhật prerequisites, commands, env table và trạng thái VERIFIED/DESIGNED. Giới hạn: chưa có service/Docker/provider/model/corpus data; inference group dành T17 và đang rỗng có chủ đích.

<a id="t02"></a>
### T02 — Docker Compose nền tảng

- **Trạng thái:** COMPLETE
- **Phụ thuộc:** T01.
- **Tham chiếu kế hoạch:** [P02](plan.md#p02), [P12](plan.md#p12).
- **Công việc:** Dockerfiles/stages, Compose PG/Qdrant/Redis/API health skeleton; profile local-storage MinIO; named volumes, loopback ports, healthcheck và secret references. Worker/inference chưa triển khai không được báo ready giả. Pin images; viết prerequisites Docker Windows trong README/RUNBOOK.
- **Xong khi thỏa mãn DoD:**
  1. `docker compose config --quiet` và `docker compose --profile local-storage up -d --build` PASS với chỉ services thực sự đã có; health routes phản ánh dependency thực.
  2. `docker compose ps` cho trạng thái thật; restart giữ fixture PG/Qdrant/MinIO, không publish DB/broker ra host; lưu lệnh inspect đã redacted.
- **Cạm bẫy:** Không `down -v`; không bind database files NTFS; không ghi plaintext secrets vào output compose config; không đưa GPU vào điều kiện để API khởi động.
- **Ghi chú thực thi:** Attempt `T02-A01` dừng trước mọi repo mutation do runtime quota; event nguyên văn và việc không có repo checks/logs nằm tại [H-T02-A01](handoffs.md#h-t02-a01). Attempt `T02-A02` | worker/model/effort/context `gpt-5.6-sol`/`xhigh`/fresh (`fork_turns="none"`) | 2026-09-16 10:08–10:30 +07:00. Implemented/files: Compose PG17/Qdrant/Redis/health-only API + MinIO profile/bootstrap, pinned tags+digests, multi-stage non-root API image, named volumes/internal ports/loopback, ignored secret bootstrap, typed Qdrant/health/password-file settings, unit + local smoke/persistence helpers; `compose.yaml`, `docker/**`, `.dockerignore`, config/dependency/lock, `src/rag_core/api/**`, tests/scripts, README/RUNBOOK và ba sổ docs. DoD-1 PASS: config/build/up/wait/health, real Redis outage giữ live 200 và đưa ready 503 rồi phục hồi 200. DoD-2 PASS: ps/inspect chứng minh ports/volumes/images/health; restart giữ PG/Qdrant marker và MinIO timestamp/size/ETag. D1–D5 PASS; Ruff/mypy/7 unit/docs/lock checks PASS, secrets/cache/corpus/scope review PASS theo [H-T02-A02](handoffs.md#h-t02-a02). D6 stage explicit paths + commit subject `feat(T02): add local Docker infrastructure`; COMPLETE có hiệu lực sau commit thành công và Orchestrator review, actual hash trả ngoài commit. README/RUNBOOK cập nhật Docker prerequisites/bootstrap/start/wait/stop/health/troubleshooting, phân biệt health VERIFIED với business API DESIGNED. Giới hạn: không business schema/routes/auth, worker/dispatcher/inference/provider/GPU/cloud/Scarlet; MinIO chưa thuộc API readiness trước T11. Next: Orchestrator nghiệm thu rồi worker mới T03, không reuse attempt này.

- **Phục hồi / T02-A03:** completion candidate | worker `/root/t02_a03`, runtime `gpt-5.6-sol`/`xhigh`/fresh (`fork_turns="none"`), thread `01a0a9a0-7c47-7b43-bd6c-09b38a8303a8`, turn `01a0a9a0-7cc9-7031-adb0-83aed0d1bcdf` | Started 2026-09-16 16:51 +07:00; kết thúc sau completion commit, timestamp báo cáo post-commit. A02 chưa COMPLETE: không có T02 commit tại HEAD T01, và khi resume Orchestrator chỉ thấy root, không có worker A02 active; nguyên nhân chưa xác định. Implemented/files: giữ nguyên 16 source/test/config/helper candidate A02, chỉ cập nhật README/RUNBOOK + `docs/{tasks,handoffs,implementation-summary}.md`; tổng completion scope đúng 21 file T02 baseline, không AGENTS/plan/corpus/T03. DoD-1 PASS: config/up-build/wait/HTTP smoke hiện tại thật, final image SHA-256 all 6 Python source equal và container/tag image match, Python 3.12.13/non-root; outage live 200/ready 503/recovery 200 kế thừa A02 vì source không đổi. DoD-2 PASS: current ps/inspect ports/volumes/images/health thật, PG/Qdrant marker và MinIO timestamp/size/ETag còn nguyên; controlled restart kế thừa A02, A03 không reseed PG/Qdrant. D1 PASS diff/scope/dependency/prompt; D2 PASS locked sync/Ruff/mypy/7 unit/Powershell parse; D3 PASS từng DoD + inherited boundary; D4 PASS docs/notes/evidence/summary/check; D5 PASS secret/ignore/size/lock source/corpus/scope; D6 explicit stage/cached review + subject `feat(T02): add local Docker infrastructure`, COMPLETE chỉ hợp lệ khi commit thành công và Orchestrator review. Evidence [H-T02-A03](handoffs.md#h-t02-a03), decisions [S-T02-A03](implementation-summary.md#s-t02-a03); actual hash trả post-commit. README/RUNBOOK: giữ quickstart T02 VERIFIED/business DESIGNED và bổ sung recovery/check-current/source-image/inherited evidence links. Giới hạn/blocker: không blocker T02 cần user input; nguyên nhân lifecycle A02 chưa xác định, API chỉ health/MinIO chưa readiness trước T11; không schema/auth/business/worker/model/GPU/load/cloud/Scarlet. Next: root nghiệm thu completion commit, worker/context mới T03; A03 kết thúc, không reuse.

<a id="t03"></a>
### T03 — Schemas và hợp đồng API

- **Trạng thái:** COMPLETE
- **Phụ thuộc:** T02, T01.
- **Tham chiếu kế hoạch:** [P01](plan.md#p01), [P05](plan.md#p05), [P06](plan.md#p06), [P09](plan.md#p09).
- **Công việc:** Pydantic schemas/domain types, error envelope, request/response/SSE contracts, endpoint inventory/schema snapshot. Endpoint chưa implement trả lỗi rõ hoặc chưa mount; không stub response success. Cập nhật API matrix trong RUNBOOK với DESIGNED.
- **Xong khi thỏa mãn DoD:**
  1. `uv run pytest tests/contract/test_api_schema.py` PASS cho domain/subset/history/language/limits/citation locator/error/event validation; không cho client override identity/system prompt.
  2. Export schema bằng `uv run python scripts/export_openapi.py`; snapshot và JSON examples validate được; phân biệt API design với routes đang phục vụ.
- **Cạm bẫy:** Default không tìm kho user ngoài session; `document_ids=[]` không đồng nghĩa all; không đóng response usage thiếu thành số giả.
- **Ghi chú thực thi:** Attempt `T03-A01` | worker `/root/t03_a01`, runtime `gpt-5.6-sol`/`xhigh`, fresh `fork_turns="none"`, turn `01a0a9ad-1977-7a52-a89d-5c49faa92f74` | Started 2026-09-16 17:05 +07:00. Baseline `main`/`851ff1d10b49b6a4d7ae7e1756f2c2a1b8562e96`, worktree CLEAN; T01/T02 đã COMPLETE và được Orchestrator nghiệm thu, notes/dependencies đã đọc. Allowed files: schema/domain/API contract modules, contract tests, export script, snapshots/JSON examples, README/RUNBOOK và ba sổ docs; app/config/dependency chỉ khi thiết yếu. Plan: strict Pydantic requests/responses, discriminated citation/SSE contracts và sequence validation; export designed OpenAPI tách served health, validate snapshots/examples, chạy từng DoD và D1–D6, commit explicit. Không business/auth/ingestion/retrieval/provider/streaming runtime/T04. Commit dự kiến `feat(T03): define versioned API contracts`; results bổ sung sau kiểm chứng.

- **Phục hồi / T03-A02:** IN_PROGRESS | worker `/root/t03_a02`, `gpt-5.6-sol`/`xhigh`, context mới `fork_turns="none"` theo spawn/runtime verification của Orchestrator | Started 2026-09-17 11:51 +07:00. A01 đã kết thúc do runtime quota, chưa commit; không reuse agent. Baseline `main`/`851ff1d10b49b6a4d7ae7e1756f2c2a1b8562e96`, đúng 16 files candidate T03 dirty/untracked; T01/T02 COMPLETE đã đọc notes/evidence. Allowed exact scope: `README.md`, `RUNBOOK.md`, `docs/{tasks,handoffs,implementation-summary}.md`, `pyproject.toml`, `uv.lock`, `docs/api/{examples-v1,openapi-v1.designed,openapi.served}.json`, `scripts/export_openapi.py`, `src/rag_core/contracts/{__init__,examples,openapi,sse,v1}.py`, `tests/contract/test_api_schema.py` (17 completion files). Plan: review candidate giữ nguyên phần đúng, chạy riêng từng DoD/quality, sửa checkpoint/evidence/summary/links, kiểm scope/secrets và commit explicit `feat(T03): define versioned API contracts`; không code task sau. Recovery [H-T03-A01](handoffs.md#h-t03-a01), actual evidence A02 bổ sung sau checks.

- **Kết quả / T03-A02:** implemented giữ source/test/config candidate A01, bổ sung recovery và actual evidence/summary/docs; completion scope đúng 17 files ở brief trên. DoD-1 **PASS** — 83 contract tests, domain/subset/history/EN-VI/limits/locators/evidence/error/SSE validation và identity/system override refusal, không skip: [H-T03-A02 DoD-1](handoffs.md#h-t03-a02-dod1). DoD-2 **PASS** — export + `--check`, 13 designed ops/2 served health/48 schemas/37 synthetic examples qua OpenAPI model + Draft2020-12/format checker + Pydantic/roundtrip: [H-T03-A02 DoD-2](handoffs.md#h-t03-a02-dod2). **D1 PASS:** dependency notes/review/diff/scope/prompt unchanged; **D2 PASS:** locked dev/api sync, Ruff, strict mypy 11 source, 7 unit và 83 contract; **D3 PASS:** từng DoD command/cwd/exit/expected/actual; **D4 PASS:** README/RUNBOOK + tasks/handoffs/summary và UTF-8/docs links/task graph check; **D5 PASS:** manual diff/sensitive-name/credential-marker/size/ignore/lock source/prompt review; **D6:** explicit stage 17 paths/cached review + completion commit, có hiệu lực sau commit thành công và Orchestrator review. Full evidence [H-T03-A02](handoffs.md#h-t03-a02), interfaces/decisions [S-T03-A02](implementation-summary.md#s-t03-a02). README/RUNBOOK: quality/export commands, API design/served matrix và synthetic artifacts links, history/tokenizer boundary, format locators/opaque storage version vs core UUID, error envelope/framework404 và logical SSE/runtime limitations; actual evidence links A02 + A01 recovery. Không DB/index migration, initial v1 design chưa có business client; runtime auth/scope/readiness/factual/tokenizer/provider/SSE transport chưa implement hoặc verify. Không blocker cần user input; không chạy lại T02 integration vì source/config T02 không đổi. Commit subject/Task-ID `feat(T03): define versioned API contracts`; resolver `git log -1 --format=%H --grep="^feat(T03):"`, actual hash/end/output trả sau commit, không nhét hash vào chính commit. Next: completion commit/root review rồi worker/context mới T04; A02 không tự làm task tiếp.

- **Completion boundary / T03-A02:** `COMPLETE` trong completion candidate chỉ có hiệu lực sau actual completion commit thành công và Orchestrator review; staged exact 17-file scope/cached whitespace PASS, không unstaged/untracked file lạ. D6 actual hash/exit/output và ended timestamp trả root post-commit; không self-reference hoặc amend. Nếu commit fail, chưa COMPLETE và phải ghi reproduction/checkpoint trước trả root.

## Phase 1 — Evaluation corpus

<a id="t04"></a>
### T04 — Hạ tầng tải/manifest/validation corpus

- **Trạng thái:** COMPLETE
- **Phụ thuộc:** T03, T01.
- **Tham chiếu kế hoạch:** [P11](plan.md#p11); prompt corpus §§4–9.
- **Công việc:** Đọc toàn bộ prompt corpus. Tạo shared download/checksum/pin/atomic write utilities, setup CLI, validators schema, manifest/license policy; mọi script/data dưới corpus-documents. Xác minh nguồn/license thực, chỉ ignore dữ liệu nặng. Chưa tải toàn bộ hoặc đổi pipeline.
- **Xong khi thỏa mãn DoD:**
  1. `uv run python corpus-documents/scripts/setup_corpus.py --help` và `uv run pytest tests/unit/test_corpus_common.py` PASS: corrupt download, interrupted write, retry, idempotency, invalid reference đều được kiểm.
  2. Có source/license inventory với URL/version thật; manifest chưa tải ghi trạng thái chưa có, không bịa checksum/count; README/RUNBOOK giải thích command sẽ đầy đủ ở T08.
- **Cạm bẫy:** Script setup không được PASS `--all` khi domain chưa có; không chạy legacy model setup; không dùng mirror lạ; không mirror upstream license suy từ code license mà bỏ dataset terms.
- **Ghi chú thực thi:** Attempt `T04-A01` | worker `/root/t04_a01`, `gpt-5.6-sol`/`xhigh`, fresh context `fork_turns="none"` theo spawn, runtime sẽ được Orchestrator đối chiếu | Started 2026-09-17 12:03 +07:00. Baseline `main`/`e4db5e3203b6c7052caa8943118b1999d84f51d8`, CLEAN (global ignore permission warning có sẵn); T03/T01 COMPLETE đã đọc toàn bộ notes cùng P01/P11/P13/P14, handoffs/summary/README/RUNBOOK và prompt gốc. Allowed: corpus scripts/schemas/manifests/source-license-inventory/README/licenses, `tests/unit/test_corpus_common.py`, ignore/dependency chỉ nếu thiết yếu, README/RUNBOOK và ba sổ docs. Plan: xác minh official revisions/terms; stdlib bounded download/hash/atomic publication/path safety; shared QA/manifest validation và honest CLI unavailable gates; synthetic fault tests, từng DoD/D1–D6, explicit commit `feat(T04): add reproducible corpus tooling`. Không download full corpus, implement T05–T07, đổi API/models/retrieval hoặc ingest.

- **Kết quả / T04-A01:** 19 completion files: root README/RUNBOOK +docs tasks/handoffs/summary; corpus README/source-license-inventory/root+3domain manifests/3schemas/3scripts/licenseREADME; `tests/unit/test_corpus_common.py`. Shared stdlib download/hash/Git-blob/atomic/strictJSON/path/QA utilities, metadata validation và honest unavailable setup/full-validation gates implemented. DoD-1 **PASS** — separate help exit0 và 80 meaningful synthetic unit tests/no skip: [H-T04-A01 DoD-1](handoffs.md#h-t04-a01-dod1). DoD-2 **PASS** — official source revisions/blob IDs/README terms/publisher card verified live, actual GitHub HEAD200/CMU timeouts recorded, no downloaded bytes or fabricatedcounts/hash/timestamps, manifest not_downloaded+null values; full setup pendingT08 documented: [H-T04-A01 sources](handoffs.md#h-t04-a01-sources). D1 scope/dependency/diff/prompt PASS; D2 locked77/44 sync/Ruff/strictmypy14/commonunit80 PASS; D3 each requestedDoD actual commands/exit/expected/actual PASS; D4 README/RUNBOOK/task/handoff/summary/docscheck; D5 secrets/artifacts/prompt/initialschema compatibility review; D6 explicit19stage/cachedreview +commit `feat(T04): add reproducible corpus tooling`, results evidenced at [H-T04-A01 review](handoffs.md#h-t04-a01-review). README/RUNBOOK: T04 tooling VERIFIED vs data/setupT05–T08 PLANNED, commands/conventions/source-license/state/risks/troubleshooting; new corpus README/license notices. Interfaces/limits [S-T04-A01](implementation-summary.md#s-t04-a01). No new dependency/ignore/DB/index/API migration or model/retrieval change. No T04 code blocker; Hotpot HTTP20s/HTTPS15s HEAD timeout requires actual access check/blocker atT05, FinanceBench GitHub/PDF license unresolved requires user decision/upstreamgrant beforeT06. Runtime model/effort metadata verification by root remains acceptance boundary. Commit actualhash/end returned post-commit; resolver `git log -1 --format=%H --grep="^feat(T04):"`. COMPLETE proposal has effect only after successful completion commit/root review; no T05 work by this worker.

- **Completion boundary / T04-A01:** D1–D5 PASS; D4 docscheck UTF-8/nonempty10/internal186/task37/dependency81 acyclic PASS, D5 exact19file/size/secret/prompt/ignore review PASS. D6 initial stage/cached scope PASS, last finite-JSON guard passed80 tests/Ruff/strictmypy14; explicit restage/final docs/cached checks và actual completion commit là bước cuối. COMPLETE trong candidate chỉ có hiệu lực sau commit thành công và Orchestrator runtime/diff/DoD/hash review; actual hash/end/status báo ngoài commit, không amend/self-reference. No T05 implementation.

<a id="t05"></a>
### T05 — HotpotQA Default corpus

- **Trạng thái:** COMPLETE
- **Phụ thuộc:** T04.
- **Tham chiếu kế hoạch:** [P11](plan.md#p11); prompt corpus §1 và §§6–7.
- **Công việc:** Tải official dev distractor JSON, deterministic stratified seed 42 subset 100 QA, materialize paragraphs+distractors/dedup, gold docs từ supporting_facts; ghi original answer/type/level, actual distribution và provenance.
- **Xong khi thỏa mãn DoD:**
  1. `uv run python corpus-documents/scripts/setup_corpus.py --domain default` và `uv run python corpus-documents/scripts/validate_corpus.py --domain default` PASS với nguồn thật.
  2. Chạy lại setup: IDs/content hashes ổn định và không duplicates; `uv run pytest tests/unit/test_corpus_default.py` kiểm supporting-vs-distractor mapping, title collisions, sampling reproducibility; report có 100 QA hoặc blocker có chứng cứ upstream.
- **Cạm bẫy:** Không đưa answers/supporting flags vào document text; không dùng tất cả context làm expected docs; title giống nhau chưa chắc paragraph giống nhau.
- **Ghi chú thực thi:** `T05-A01` worker `/root/t05_a01` kết thúc ngay bởi runtime usage-limit, không shell execution/repo changes/commit; recovery event [H-T05-A01](handoffs.md#h-t05-a01). Attempt `T05-A02` | worker `/root/t05_a02`, requested `gpt-5.6-sol`/`xhigh`, fresh `fork_turns="none"`; actual runtime do root đối chiếu | Started 2026-09-17 23:22 +07:00. Baseline CLEAN `main`/accepted T04 `ad49ecc53a1998758f419e00ac5d03bf468ba989`; dependency notes/P01/P11/P13/full prompt/README/RUNBOOK/handoffs/summary đọc trước edits. Allowed: default preparation/shared CLI+validator, default data/QA/manifests/reports, necessary inventory/schema metadata, corpus README/licenses, default/common unit tests, root README/RUNBOOK/three execution docs; no other domains/API/model/pipeline. Plan: bounded real official GET and publisher source inspection; deterministic seed42 stratification, paragraph-content dedup/supporting-only mapping, safe publication; each DoD/quality/docs/artifact checks and explicit completion commit `feat(T05): prepare HotpotQA evaluation corpus` only if all acceptance passes. No mirror substitution or fabricated gold/counts/hash.

- **Kết quả / T05-A02:** completion candidate, hiệu lực COMPLETE chỉ sau successful commit và root runtime/DoD/diff review; end/hash trả post-commit. User phê duyệt nguồn HF community derivative cụ thể sau canonical CMU GET HTTP/HTTPS timeout20s; P11 có exception riêng, prompt nguyên byte. Actual source Parquet revision `1908d6afbbead072334abe2965f91bd2709910ab`, SHA256 `c20b638ca82b21d04fe12e14ff417ad05153d4d215a65de54497fca4e972f7c6`, 27452575B/7405rows; semantic conversion giữ id/question/answer/type/level/context/facts, chưa đối chiếu byteCMU. Actual 100QA/986documents,996contextinstances/10dedup,50bridge/50comparison/allhard (source5918bridge/1487comparison/allhard). One upstream annotation anomaly ngoài unchangedsample được report, sampled ranges/title/mapping enforce; không edit/drop/resample gold. Files22: root README/RUNBOOK/docs tasks/handoffs/summary/authorizedplanexception; corpus README/licenses/inventory/root+defaultmanifest/4scripts/3QAmetadata; default+commontests; dev-only pyarrow25.0.1/uvlock78. DoD-1 **PASS** — separate real setup và default validator exit0 [H-T05-A02 DoD-1](handoffs.md#h-t05-a02-dod1). DoD-2 **PASS** — setup rerun exit0, all993hashes/mtimes/100IDs/downloadtimestamp unchanged/no duplicates;37 meaningful syntheticdefaulttests/no skip [H-T05-A02 DoD-2](handoffs.md#h-t05-a02-dod2). D1 dependency/scope/diff/prompt PASS; D2 locked78sync/Ruff/strictmypy15/82commontests/37defaulttests PASS; D3 actualcommand/cwd/exit/config/expected/actual for each DoD PASS; D4 README/RUNBOOK/task/handoff/summary/docscheck; D5 code/secrets/license/ignoredraw+docs/cache review/noAPIorDBmigration; D6 explicit22file stage/cachedcheck/commit `feat(T05): prepare HotpotQA evaluation corpus` at [H-T05-A02 review](handoffs.md#h-t05-a02-review). README/RUNBOOK: approved-source commands/realcounts/license/conversion/anomaly/rollback/cache/readerlimits versus pendingotherdomains/T08. Interfaces [S-T05-A02](implementation-summary.md#s-t05-a02). No T05 blocker after user source decision; no official-author mirror or CMU-byte-equivalence claim, full7405annotations not allclean, CPU/runtime/provider/benchmark unchanged. Next rootacceptance then freshT06, rightsdecision still needed before FinanceBench downloads. Commit resolver `git log -1 --format=%H --grep="^feat(T05):"`; actualhash outside owncommit.

<a id="t06"></a>
### T06 — FinanceBench Document corpus

- **Trạng thái:** COMPLETE
- **Phụ thuộc:** T05, T04.
- **Tham chiếu kế hoạch:** [P07](plan.md#p07), [P11](plan.md#p11); prompt corpus §2 và §§6–7.
- **Công việc:** Resolve QA->metadata->PDF official; tải đúng PDF được reference, normalize toàn bộ open-source QA, giữ gold/evidence/justification và page indexing gốc; không chạy benchmark tài chính ở task này.
- **Xong khi thỏa mãn DoD:**
  1. `uv run python corpus-documents/scripts/setup_corpus.py --domain document` và `uv run python corpus-documents/scripts/validate_corpus.py --domain document` PASS với PDF thật, page trong range, evidence/answer không thay đổi.
  2. `uv run pytest tests/unit/test_corpus_document.py` kiểm tên file/mapping/page zero-based; manifest/README in số QA/PDF/hash/license thực, rerun không tải trùng.
- **Cạm bẫy:** Không đổi page convention trực tiếp trong gold; không tải tất cả PDF không liên quan; không lấy closed dataset; lỗi download/auth không thay bằng PDF giả.
- **Ghi chú thực thi:** `T06-A01` worker `/root/t06_a01` kết thúc ngay bởi runtime usage-limit, không shell execution/repo changes/commit; exact event được lưu tại [H-T06-A01](handoffs.md#h-t06-a01). Attempt `T06-A02` | worker `/root/t06_a02`, requested `gpt-5.6-sol`/`xhigh`, fresh `fork_turns="none"`; actual runtime do Orchestrator đối chiếu | Started 2026-09-19 16:52 +07:00. Baseline CLEAN `main`/accepted T05 `a2a94fbba00ee8c2f6462134af03035a86f524e3`; T05/T04 dependency notes, P01/P07/P11/P13/P14, full original corpus prompt, handoffs/summary/README/RUNBOOK và corpus interfaces được đọc trước code. Allowed: document preparation/minimal shared setup+validation, document manifests/local normalized QA policy/inventory/license docs, document unit tests, dependency/ignore chỉ khi thiết yếu, root README/RUNBOOK và ba execution docs. Plan: verify pinned official QA+metadata bytes and current notices; resolve exact referenced company PDFs, bounded download/cache, preserve source gold/evidence/justification/metadata and zero-based pages; validate real PDF page ranges and deterministic rerun; run each DoD plus D1–D6, then explicit completion commit `feat(T06): prepare FinanceBench evaluation corpus`. Local-use authorization is inherited from the approved plan; raw/PDF and, while redistribution rights remain unresolved, normalized FinanceBench QA stay ignored/local. No T07, benchmark, production ingestion, API/model/retrieval or Scarlet work.

- **Kết quả / T06-A02:** completion candidate có hiệu lực sau successful commit và root runtime/diff/DoD review; actual hash/end trả post-commit. Exact18 tracked files: root README/RUNBOOK/.gitignore/pyproject/lock; corpus README/licenses/inventory/root+document manifests/3 scripts; document+common tests; tasks/handoff/summary. Official commit/main `cc39aeb4afdf33909ee1412188bf89035950c2eb`, QA SHA256 `a5a2aa673e573e55675fc3c0f9aa38c1cf59d2abc91edb077534f71f10a71877`, metadata SHA256 `1c69127783879de8cdadb159d2181f39bc3123b8e0ebf74031c3969d69189575`; all150 `OPEN_SOURCE` QA map to84/368 official repository PDFs, 189 evidence, no unrelated PDF. Actual PDFs165,527,662B/12,013pages; gold pages0–303 and 0 out-of-range. Answers/evidence/full-page text/justification/metadata/order unchanged; page gold remains zero-based and eval adapter owns future one-based conversion. 50 null justification/reasoning preserved; unreferenced conflicting metadata pair `FOOTLOCKER_2023_annualreport` reported, referenced ambiguity fails. Raw/PDF/normalizedQA stay local ignored; manifest non-content receipts tracked. DoD-1 **PASS** — separate real setup/validator exit0 [H-T06-A02 DoD-1](handoffs.md#h-t06-a02-dod1). DoD-2 **PASS** — 19 meaningful document tests/no skip, real rerun keeps91published+84cache hashes/mtimes,150IDs/downloadtimestamp and no PDF redownload [H-T06-A02 DoD-2](handoffs.md#h-t06-a02-dod2). D1 dependency/scope/diff/prompt PASS; D2 locked82/49 sync, Ruff, strictmypy16,81common/37default/19document tests PASS; D3 separate commands/cwd/exit/config/expected/actual; D4 README/RUNBOOK/corpus docs/task/handoff/summary + docscheck; D5 official source/license/current pin, secrets/artifact/ignore/schema review; D6 explicit18-stage/cached review + commit `feat(T06): prepare FinanceBench evaluation corpus` at [H-T06-A02 review](handoffs.md#h-t06-a02-review). README/RUNBOOK: working commands/counts/hashes/page policy/cache/rollback/rights/anomalies/troubleshooting. No DB/index/API/model/provider/Scarlet migration or benchmark. Known boundary: ready manifest is tracked while raw/PDF/QA are ignored, so fresh-clone recovery is T08; hard crash requires operator lock/stage review. No blocker for T06; publisher card CC-BY-NC4.0 does not resolve GitHub/PDF redistribution/company rights and local-use authorization is not a commercial/redistribution grant. Commit hash outside own commit; resolver `git log -1 --format=%H --grep="^feat(T06):"`. Next root review then fresh T07; A02 does not start it.

- **T06-A03 — acceptance evidence closure (started IN_PROGRESS):** Worker `/root/t06_a03`, `gpt-5.6-sol`/`xhigh`, fresh `fork_turns="none"`; started 2026-09-22 08:43 +07:00 at CLEAN `main`/T06 implementation commit `6863abf221db2d387e141656610c710ceac14dff`. Root has reviewed A02 technical DoD and actual Sol/xhigh runtime (thread `01a0b914-5327-7d20-866b-6f60b4f65bed`, ended 2026-09-19 17:25:14 +07:00); two closure gaps remained: exact historical rerun/source/staging command provenance and stale README/RUNBOOK top statuses. Allowed files: README, RUNBOOK, tasks, handoffs, implementation-summary only. Plan: recover original public A02 invocations/output from runtime record without rerunning corpus downloads/tests; align current status and user-paused checkpoint; run docs check and D1–D6 review; commit `docs(T06): finalize acceptance evidence and paused checkpoint`. No code/data/config/test changes or T07 work.

- **Kết quả đề nghị / T06-A03:** exact A02 rerun/source/staging/cache-assertion commands copied verbatim from original public runtime and checked byte-for-byte against [H-T06-A03](handoffs.md#h-t06-a03); original A02 outputs/failed attempts retained, no historical rerun claimed. DoD-1 **PASS (REUSED A02, 2026-09-19 / `6863abf`)** — real separate setup and validator output [H-T06-A02 DoD-1](handoffs.md#h-t06-a02-dod1). DoD-2 **PASS (REUSED A02)** — actual rerun91published/84cache unchanged and19 Document tests [H-T06-A02 DoD-2](handoffs.md#h-t06-a02-dod2), recovered exact rerun command [H-T06-A03](handoffs.md#h-t06-a03). D1 exact five allowed documentation files, clean baseline and diff check; D2 A03 documentation quality check only, with A02 locked sync/Ruff/mypy/tests retained as reused evidence; D3 recovered commands/outputs map each DoD; D4 README/RUNBOOK current summaries, task/handoff/Phase1-T06-A03 summary and docs check; D5 no source/test/config/manifest/prompt/payload/secret change, no migrations; D6 explicit five-file stage/cached review and `docs(T06): finalize acceptance evidence and paused checkpoint` commit, all at [H-T06-A03](handoffs.md#h-t06-a03). README/RUNBOOK now state T06 Document VERIFIED local and user-requested pause. Limitations unchanged: source/PDF redistribution rights and T08 clean-clone recovery unresolved; no benchmark or provider result claimed. Formal COMPLETE requires successful A03 docs commit plus root review; actual hash/end returned after commit. **USER-PAUSED AFTER T06**; T07–T36 remain TODO and T07 starts only after a new user request.

<a id="t07"></a>
### T07 — XQuAD EN/VI và bốn cross-lingual slices

- **Trạng thái:** COMPLETE
- **Phụ thuộc:** T06, T04.
- **Tham chiếu kế hoạch:** [P03](plan.md#p03), [P11](plan.md#p11); prompt corpus §3 và §§6–7.
- **Công việc:** Tải official EN/VI, kiểm QA/title/paragraph alignment, materialize toàn bộ paragraph instances, stable parallel_group_id, giữ full QA và optional small subset; tạo en_en, vi_vi, vi_en, en_vi.
- **Xong khi thỏa mãn DoD:**
  1. `uv run python corpus-documents/scripts/setup_corpus.py --domain bilingual` và `uv run python corpus-documents/scripts/validate_corpus.py --domain bilingual` PASS với dữ liệu thật.
  2. `uv run pytest tests/unit/test_corpus_bilingual.py` chứng minh counterpart bằng IDs/structure, expected answer/evidence đúng language của từng slice; actual counts và hashes ghi manifest, rerun ổn định.
- **Cạm bẫy:** Không assume array position trước validate; không dịch gold bằng LLM; không dùng corpus cùng ngôn ngữ câu hỏi trong slice chéo; không thay full QA bằng quick subset.
- **Ghi chú thực thi:** `T07-A01` khởi tạo bởi Orchestrator Hermes ngày 2026-09-26 01:21:49 SEAST; profile `worker`, config model `gpt-6-luna`/provider `openai-codex`, reasoning effort giữ cấu hình profile, chưa có xác nhận runtime effort; card `t_2a19f514`, run 2, fresh session, dispatch tại 01:23 SEAST. Baseline CLEAN `main`/`7696f83fa2d718bcad3ca6d69f627ff886f2d10d` (bootstrap/review docs commit); T06/T04 COMPLETE. Allowed ngoài docs: bilingual preparation + minimal shared corpus CLI/validator, bilingual manifest/root manifest/inventory/licenses/corpus README và bilingual/common tests; README.md/RUNBOOK.md phải sửa status `USER-PAUSED` hết hiệu lực và tài liệu chức năng T07. Không sửa `docs/`, không tạo commit: Worker trả structured handoff/commands/cwd/exit/output/diff; Orchestrator kiểm, ghi docs và tạo completion commit `feat(T07): prepare XQuAD bilingual evaluation slices`. P01/P03/P11/P13, prompt §§3,6–7, dependency notes T04/T06, handoffs/summary/README/RUNBOOK và protocol là prerequisites. Plan: official pinned EN/VI Git blobs; alignment IDs/structure; full paragraph/QA + bốn slices counterpart gold; setup/validator/test riêng, rerun hash/mtime, D1–D5; D6 do Orchestrator sau handoff. Không sửa một byte prompt corpus, API/retrieval/model/Scarlet, gold-based prefilter, hoặc ingest qa/. T08 clean-clone reproduction vẫn riêng.
- **T07-A01 BLOCKED / human safety gate (resolved for A02 dispatch):** run kết thúc `blocked` sau ~23 phút; terminal từ chối lệnh xóa ba repo-local pytest scratch dirs `.t`, `.tmp-test`, `.verify-temp` và yêu cầu dừng. Worker không trả structured DoD handoff; chưa kiểm DoD hoặc commit, không claim PASS. Không retry/route vòng trước khi hỏi. Người dùng sau đó **cho phép dọn đúng ba thư mục** sau khi kiểm nằm trong repo; Orchestrator kiểm read-only `pwd`, `realpath`, `stat`: cả ba là directory và resolved path lần lượt dưới repo root. Chưa kiểm từng nested reparse point và chưa xóa. A02 phải kiểm nested links/junctions + absolute targets trước thao tác và chỉ dọn các path được chấp thuận; nếu safety gate tiếp tục từ chối thì stop, không bypass. A01 terminal không resume; A02 là fresh Worker/card, giữ code dở và mọi file ngoài đúng ba target. Evidence [Hermes T07-A01 blocker](handoffs.md#hermes-t07-a01-blocker).
- **T07-A02 BLOCKED / user decision for A03:** card `t_b2a34702`, fresh Worker configured `gpt-6-luna`/`openai-codex`, run 3; HEAD unchanged `7696f83`. Sau kiểm absolute targets/nested reparse trên Windows, dọn chính ba scratch dirs đã được user cho phép bằng PowerShell `Remove-Item -LiteralPath`, verified removed; no other deletion. Separate real setup và validator exit 0, 240 parallel groups/240 EN+240 VI docs/1,190 QA mỗi slice. Bilingual pytest exit 1: initial 4 pass/1 Windows temp setup error; repo-local temp reruns 4 pass/1 fail `FileNotFoundError` sâu trong stage; patch parent mkdir trong `prepare_bilingual.py` chưa chứng minh sửa lỗi. Một read-only `python -c` path-length diagnostic bị terminal timeout/deny 60.5s; Worker dừng theo safety gate, không retry. Người dùng sau đó **chỉ đạo bỏ riêng phép đo tùy chọn bị từ chối**; không cho phép đổi test/DoD hay dùng công cụ khác để chạy lại phép đo đó. DoD-2 FAIL/chưa hoàn tất, D1–D5 chưa hoàn tất, D6 không thực hiện; partial code/scratch giữ nguyên. Board summary + structured comment [Hermes T07-A02 handoff](handoffs.md#hermes-t07-a02-handoff). Fresh Worker A03 điều tra từ traceback/source/tests, không hạ gate.
- **T07-A03 stale / recovery:** card `t_9bc95bc3`, run 4, profile `worker` configured `gpt-6-luna`/`openai-codex`; no handoff. Sau hơn 12h, claim expired, PID 34724 absent (`MSYS_NO_PATHCONV=1 tasklist.exe /FI 'PID eq 34724'` → no tasks), board log ngừng sau 3 lần pytest với cấu hình temp (hai lần exit1, lần ba log không ghi exit) và patch bỏ `output_path.parent.mkdir` trong `prepare_bilingual.py`. Không suy ra pytest PASS từ preview không có exit. Orchestrator `reclaim` rồi `block` card cũ; giữ partial edits + scratch, không resume; không có DoD accepted/commit, T07 còn IN_PROGRESS. Evidence [Hermes T07-A03 stale recovery](handoffs.md#hermes-t07-a03-stale). A04 Worker/card/session mới `t_88f601c9` đã dispatch để điều tra; không chuyển T08.
- **T07-A04 BLOCKED / safety decision (authorization subsequently received):** card `t_88f601c9` run 6 kết thúc với structured handoff [Hermes T07-A04](handoffs.md#hermes-t07-a04). Setup/validator trên XQuAD thật exit0 (240 EN +240 VI paragraphs, 240 groups, 1190 QA mỗi slice); test thường lỗi temp permission, test với fresh short Windows basetemp exit0, **5 passed**. Lệnh đọc snapshot hash/mtime và source receipts để kiểm rerun bị terminal timeout/deny sau 60.4s; Worker dừng, không chạy lại hay lách bằng lệnh khác. Không có deterministic rerun/quality regressions/D1–D5 closure hoặc D6 commit. Không coi T07 COMPLETE. Người dùng sau đó phê duyệt **riêng đúng phép kiểm read-only bị từ chối** ở card A04; không phê duyệt bỏ DoD, xóa scratch, blanket bypass hay đo path-length tùy chọn từng bị từ chối. A05 fresh Worker/card/session được dispatch.
- **T07-A05 BLOCKED / runtime safety gate persists:** card `t_90838461` run 7 fresh Worker; user approval T-H2 được đọc nhưng chính xác read-only inspection vẫn bị terminal từ chối exit -1 (`BLOCKED: User denied this command... Do NOT retry...`). Worker dừng ngay, không thực hiện setup rerun, không sửa file/test/docs, không thử tool/command khác. Handoff [Hermes T07-A05](handoffs.md#hermes-t07-a05). Không có bằng chứng hash/mtime trước-sau hoặc D1–D5 closure; D6 chưa commit. T07 BLOCKED, T08–T36 gated. Cần người dùng giải quyết **quyền runtime của terminal cho đúng inspection**, hoặc quyết định cách xử lý blocker có thể kiểm chứng; chat approval đã được ghi nhưng không làm runtime gate cho phép. Không spawn A06 tự động hay vòng qua gate.


- **T07-A06 / IN_PROGRESS:** User yêu cầu hoàn thiện riêng T07, commit/push GitHub và dừng; xác nhận agent trực tiếp sửa code/tests/docs theo chế độ một task/session ngày 2026-09-26. Runtime Codex `gpt-6-sol`/`xhigh`, không subagent. Tiếp quản candidate A01–A05 tại HEAD `7696f83`, giữ scratch và lịch sử; sửa unit test gọi dữ liệu live, bổ sung corruption/rollback checks, kiểm XQuAD thật và rerun, đóng D1–D6. Allowed: candidate T07, docs nghiệm thu và cập nhật workflow AGENTS/P14/state theo phê duyệt. Không triển khai T08.

- **Kết quả T07-A06:** COMPLETE có hiệu lực khi completion commit thành công và được kiểm. DoD-1 **PASS**, setup và validator riêng trên official XQuAD thật; DoD-2 **PASS**, 21 bilingual tests và rerun giữ491published+3cache hashes/mtimes/IDs/downloaded_at.240aligned groups/240EN+240VI docs/1190QA mỗi slice, không dịch/đổi gold. D1 scope/dependencies/prompt hash/diff; D2 Ruff/mypy17 và138regression PASS; D3 actual commands/output; D4 README/RUNBOOK/corpus/license/task/summary/handoffs/state/workflow/prompt session; D5 explicit27files review không secrets/raw/scratch; D6 subject `feat(T07): prepare XQuAD bilingual evaluation slices`, actual hash trả post-commit, resolver `git log -1 --format=%H --grep="^feat(T07):"`. Evidence [H-T07-A06](handoffs.md#h-t07-a06), interfaces [S-T07-A06](implementation-summary.md#s-t07-a06). Known limits: fresh-clone/all-domain download thuộc T08; XQuAD không có unanswerable; legacy scratch giữ local; optional broad mypy export script có lỗi stub cũ ghi rõ trong evidence. User cho phép push origin/main, không merge/deploy. **Dừng sau T07**; T08 TODO, dependencies đã sẵn sàng sau commit, người dùng chủ động mở session mới.

<a id="t08"></a>
### T08 — Nghiệm thu corpus có thể tái tạo

- **Trạng thái:** COMPLETE
- **Phụ thuộc:** T07, T05, T06.
- **Tham chiếu kế hoạch:** [P11](plan.md#p11); toàn bộ acceptance §11 của prompt corpus.
- **Công việc:** Hoàn thiện root setup/manifest/README/licenses; CLI hỗ trợ `--output-root` nằm dưới corpus-documents để kiểm clean reproduction trong thư mục tạm đã ignore; strict missing/error nonzero.
- **Xong khi thỏa mãn DoD:**
  1. `uv run python corpus-documents/scripts/setup_corpus.py --all`, `uv run python corpus-documents/scripts/validate_corpus.py --all` PASS; kiểm đủ từng dòng acceptance prompt, lưu actual summary.
  2. Setup vào clean output root rồi rerun: content/IDs/counts giống corpus chuẩn, timestamps tách khỏi content hash; validator cố tình thiếu file trả nonzero. README/RUNBOOK có command reproduce đã thử, giới hạn XQuAD và license rõ.
- **Cạm bẫy:** Không xóa nguồn người dùng để tạo clean state; output path phải kiểm nằm trong workspace; network blocked là BLOCKED, không coi cache-only là clean download proof.
- **Ghi chú thực thi:** T08-A01, direct Codex agent; model/effort not exposed by this runtime, no subagents. Started 2026-09-26; baseline `main`/`1d36c0906c918106eafaecc42e457c1a1ae3827b`, remote matches. T07/T05/T06 COMPLETE; dependency notes, P01/P11/P13, full corpus prompt and execution docs read. Existing T07 scratch retained. Allowed: corpus setup/validation/shared preparation glue, reproduction tests/helper, manifests/ignore, README/RUNBOOK/corpus notices and task/handoffs/summary. Plan: safe isolated output root and metadata-only clone recovery, all-domain summary/validation, real clean downloads + rerun/comparison + missing-file rejection, each DoD and D1–D6; commit/push current branch then stop. Commit dự kiến `test(T08): verify complete corpus reproduction`.

- **T08-A01 results:** COMPLETE effective after the inspected completion commit. DoD-1 **PASS**: separate real canonical setup/validator plus all12 original acceptance rows [H-T08-A01 DoD-1](handoffs.md#h-t08-a01-dod1). DoD-2 **PASS**: final cold download `.repro/a2` with own cache, separate validator,1574published/92cache fingerprints equal to standard corpus, stable rerun and deliberate missing QA exit1 with exact restoration [H-T08-A01 DoD-2](handoffs.md#h-t08-a01-dod2). D1 scope/dependencies/diff/prompt PASS; D2 locked82/49,268unit+contract then21focused tests, Ruff/mypy19 PASS; D3 actual commands/output PASS; D4 README/RUNBOOK/corpus/licenses/tasks/handoffs/summary and docs check PASS; D5 exact20file review/no secrets/raw/scratch/schema/API migration PASS; D6 explicit stage/commit with subject `test(T08): verify complete corpus reproduction`, actual hash returned post-commit and verified against origin/main after authorized push. Interfaces/files [S-T08-A01](implementation-summary.md#s-t08-a01). Counts remain986Default/100QA,84PDF/150QA,240EN+240VI/1190QA per four slices. README/RUNBOOK now document working all-domain/isolated reproduction, strict paths/metadata-only checkout recovery, fingerprints/locks/error handling and inherited licensing/XQuAD limits. No blocker remains; no benchmark/provider/production/Scarlet work. T09 depends on T08/T03 and is ready after completion; **STOP after T08**, do not start T09.

## Phase 2 — Identity, metadata và vòng đời tài liệu

<a id="t09"></a>
### T09 — JWT, service identity và local issuer

- **Trạng thái:** COMPLETE
- **Phụ thuộc:** T08, T03.
- **Tham chiếu kế hoạch:** [P01](plan.md#p01), [P05](plan.md#p05), [P06](plan.md#p06).
- **Công việc:** Principal injection, app config/service-key mapping, JWT verify/JWKS rotation/cache, dev key/token CLI; không tích hợp Scarlet. Document auth flow/secret generation trong RUNBOOK.
- **Xong khi thỏa mãn DoD:**
  1. `uv run pytest tests/security/test_auth.py` PASS cho sai chữ ký/alg/iss/aud/exp/nbf, key rotation, app mismatch, forged user_id/JWKS URL; missing config fail closed.
  2. Local issuer tạo JWT dùng thực qua HTTP protected test endpoint; không default bypass hoặc commit key; README/RUNBOOK có ví dụ redacted, key revocation/cache semantics.
- **Cạm bẫy:** JWT decode không là validation; không tin subject từ body; service key không gửi browser; không lộ token trong handoff.
- **Ghi chú thực thi:** T09-A01 | Direct Codex agent; model/effort not exposed, no subagents | Started 2026-09-27. Baseline main/5f851c38ede7430a2dd41f32beed2108ad7d3e64; inherited T07 scratch retained, no T09 partial code. T08/T03 COMPLETE; dependency notes/P01/P05/P06/P13/handoffs/summary/README/RUNBOOK read. Allowed: auth/principal/config/API guard, local issuer CLI, security/HTTP tests, dependency lock/env and README/RUNBOOK/tasks/handoffs/summary. Plan: fail-closed service identity + RS256 validation, bounded JWKS rotation/cache, generated local credentials and real loopback HTTP acceptance; individual DoD + D1–D6, scoped commit/push then stop. Commit dự kiến `feat(T09): implement authenticated application principals`.

- **T09-A01 results (completion effective only after successful inspected commit):** DoD-1 **PASS**,51security tests with real RSA/JWKS; [H-T09-A01 DoD-1](handoffs.md#h-t09-a01-dod1). DoD-2 **PASS**, CLI-generated JWT through real loopback JWKS/Uvicorn HTTP, safe failure/revocation/private-file/exclusive-output checks; [H-T09-A01 DoD-2](handoffs.md#h-t09-a01-dod2). D1 scope/dependencies/diff PASS; D2 Ruff/mypy16/locked83packages50installed,269unit+contract PASS; D3 separate actual evidence PASS; D4 README/RUNBOOK/env/task/handoffs/summary/docs links PASS; D5 explicit19files/secret+scope review PASS; D6 scoped completion subject `feat(T09): implement authenticated application principals`, actual hash/commit inspection and authorized origin/main push equality returned post-execution, no self-reference hash. README/RUNBOOK now cover AUTH_CONFIG_FILE, required JWT claims, app binding, fail-closed errors, TTL/rotation/revocation/restart and local CLI/HTTP commands. Interfaces/files/limits [S-T09-A01](implementation-summary.md#s-t09-a01). Initial regression failures (10long Windows temp paths +1old pre-auth404 assertion) resolved with short fresh basetemp and contract assertion matching new guard; no corpus/gold changes. No blocker remains; Docker issuer wiring/production JWKS/session authorization/business API/provider/Scarlet not claimed. Ended2026-09-27; T10 dependencies T09/T02 ready after completion; **STOP AFTER T09**.

<a id="t10"></a>
### T10 — Schema metadata và session scope resolver

- **Trạng thái:** COMPLETE
- **Phụ thuộc:** T09, T02.
- **Tham chiếu kế hoạch:** [P01](plan.md#p01), [P04](plan.md#p04), [P06](plan.md#p06).
- **Công việc:** Alembic migrations/core repositories; sessions, document versions, links, jobs/outbox types; create/get/delete session và scoped link resolver, tombstone/revision. Không public route liệt kê kho ngoài session.
- **Xong khi thỏa mãn DoD:**
  1. `uv run alembic upgrade head` trên DB trống; `uv run pytest tests/integration/test_session_scope.py` chạy PG thật, kiểm app/user/session isolation, same-owner different sessions, uniqueness, empty/deleted scope.
  2. Session delete lặp lại đúng semantics, không đụng source/index; concurrent detach/query snapshot có revision; migrations tái tạo trên DB riêng. RUNBOOK có schema ownership và session mapping.
- **Cạm bẫy:** Foreign keys thiếu owner checks; external_session_id không unique toàn hệ thống; không tự inherit user documents vào session mới.
- **Ghi chú thực thi:** T10-A01 | Direct Codex agent; exact model/effort unavailable, no subagents | Started 2026-09-27. Baseline main/9e67d5d513c751930e4548ae9c292501444963a4 equals origin/main; inherited T07 scratch preserved. T09/T02 COMPLETE notes, P01/P04/P06/P13, handoffs/summary/README/RUNBOOK read. Allowed: metadata domain/port/SQLAlchemy adapter, Alembic migrations, real PG integration tests/test service, dependency groups/lock and task docs. Plan: owner-enforced schema, transactional tombstone/detach/revision and exact-pair resolver; two isolated PG databases for migration/reproduction and concurrent lifecycle evidence. Business HTTP mounting remains T26 per R05; no T11/T12 registration/storage implementation. Commit dự kiến `feat(T10): add session-scoped metadata persistence`.

- **T10-A01 results (COMPLETE effective only after successful inspected commit):** DoD-1 **PASS**: empty PG17.11 `alembic upgrade head/current`,18real scope tests for app/user/same-owner-session isolation, concurrent uniqueness, empty/deleted/subset/readiness and owner constraints. DoD-2 **PASS**: real lock/connection detach-query race, idempotent/concurrent delete, retained metadata unchanged, no worker/replay resurrection; separate empty DB migration repeat/downgrade/re-upgrade with identical columns/defaults/constraints/indexes. Evidence [H-T10-A01](handoffs.md#h-t10-a01). D1 scope/dependency/diff PASS; D2 Ruff/mypy24/locked83resolved55installed/325regression PASS; D3 individual real gates PASS; D4 README/RUNBOOK/schema mapping/migration/transaction/snapshot/test instructions and notes/summary/evidence PASS; D5 scoped review/no secrets in Git/first-schema recovery PASS; D6 completion subject `feat(T10): add session-scoped metadata persistence`, actual commit/push/remote equality returned post-execution. Interfaces/files/limits [S-T10-A01](implementation-summary.md#s-t10-a01). Initial Windows Proactor failure fixed with SelectorEventLoop; traceback exposed old local PG credential, redacted from evidence and switched to own ignored T10 test credential; original credential needs operator rotation (not changed silently). HTTP business routes remain unmounted per T26; no storage/vector/provider/worker verification claimed. Ended2026-09-27; T11 dependencies T10/T02 ready after closure; **STOP AFTER T10**.

<a id="t11"></a>
### T11 — S3/MinIO read adapter và nguồn bất biến

- **Trạng thái:** COMPLETE
- **Phụ thuộc:** T10, T02.
- **Tham chiếu kế hoạch:** [P04](plan.md#p04), [P05](plan.md#p05), [P07](plan.md#p07).
- **Công việc:** StorageReader HEAD/GET, app-config endpoint/bucket/prefix, bounded streaming/temp cleanup, source version/checksum, MinIO dev read-only policy. Fixture uploader riêng mô phỏng app dùng credential riêng.
- **Xong khi thỏa mãn DoD:**
  1. `uv run pytest tests/integration/test_storage_reader.py` PASS trên MinIO thật: đọc đúng file, denied prefix, source change, oversized body và interrupted download.
  2. Credential core không PUT/DELETE được; endpoint tùy ý/path traversal/URL redirects bị chặn; source hash trước/sau còn nguyên. README/RUNBOOK có storage trust contract.
- **Cạm bẫy:** S3 key không là chứng minh ownership; ETag không luôn là content SHA-256; không dùng cùng admin credential cho app uploader và reader.
- **Ghi chú thực thi:** T11-A01 | direct Codex agent, exact model/effort unavailable; started 2026-09-30. Baseline `main`/`2a67f8b53b65371a71ca72719cd6d0cd5025b899`, T10/T02 COMPLETE; inherited `.ptmp-t07-a02/` and `.tmp-t07-a02/` scratch retained untouched. Read AGENTS, task session prompt, dependency notes, P01/P04/P05/P07/P13, handoffs/summary/README/RUNBOOK. Allowed: storage port/domain/config/adapter, local MinIO read-only fixture policy/setup, integration/security tests, relevant dependency/env and README/RUNBOOK/task/handoff/summary. Plan: bound configured alias/prefix, immutable HEAD/GET with bounded temp cleanup; test against real isolated MinIO with separate uploader and reader principals, each DoD and D1–D6; scoped commit/push then stop. Commit subject `feat(T11): add read-only application storage adapter`.

- **T11-A01 results (COMPLETE effective only after successful inspected commit):** Implemented storage protocol, operator registry and read-only boto3 adapter, dedicated versioned MinIO test bucket with separate IAM reader/uploader and live security tests; files [S-T11-A01](implementation-summary.md#s-t11-a01). DoD-1 **PASS**: real MinIO `test_storage_reader.py` 5 passed; separate 3-test read/version/change/size/interruption run [H-T11-A01](handoffs.md#h-t11-a01). DoD-2 **PASS**: actual reader PUT/DELETE and outside-prefix GET denied, source bytes hash unchanged; separate 2-test unsafe endpoint/path and live redirect check pass. D1 scope/dependencies/diff PASS; D2 Ruff/mypy27/325 regression PASS; D3 individual real gates PASS; D4 README/RUNBOOK/env/tasks/handoffs/summary/docs check PASS; D5 reviewed scoped code/policies/no secrets/raw data/schema/API change; D6 explicit stage and subject `feat(T11): add read-only application storage adapter`, actual hash/remote equality reported after commit/push. README/RUNBOOK record working reader/config/test command and designed registration boundary. Limits: local MinIO only, synchronous boto3 adapter not yet called by API/worker, no S3 ACL ownership inference, no registration/ingestion/provider. Initial redirect recursion fixed without relaxing gate. T12 dependencies T11/T10 ready only after commit; **STOP AFTER T11**.

<a id="t12"></a>
### T12 — Upload registration, idempotency và outbox

- **Trạng thái:** TODO
- **Phụ thuộc:** T11, T10.
- **Tham chiếu kế hoạch:** [P04](plan.md#p04), [P06](plan.md#p06), [P12](plan.md#p12).
- **Công việc:** Register upload, list/detach session documents, SessionDocument, job status/retry API, transactional outbox dispatcher, lifecycle transitions, dedup phạm vi owner; worker parsing sẽ nối ở T19.
- **Xong khi thỏa mãn DoD:**
  1. `uv run pytest tests/integration/test_registration_jobs.py` với PG/Redis/MinIO: same-key same-body, same-key different-body 409, concurrent duplicate, broker unavailable/recovered, owner checks đều PASS.
  2. Outbox event không mất khi crash giữa DB commit và publish; consumer redelivery không nhân link/job; session deleted trước publish không được hồi sinh. RUNBOOK ghi 202/polling/retry/error examples.
- **Cạm bẫy:** DB commit rồi publish không transaction gây mất job; worker retry không được gắn lại tài liệu; chưa ingestion thì không báo document ready.
- **Ghi chú thực thi:** Chưa có attempt. Commit dự kiến `feat(T12): register uploads with durable ingestion jobs`.

## Phase 3 — Ingestion và index

<a id="t13"></a>
### T13 — Intermediate document model và text parsers

- **Trạng thái:** TODO
- **Phụ thuộc:** T12, T03.
- **Tham chiếu kế hoạch:** [P07](plan.md#p07), [P02](plan.md#p02).
- **Công việc:** ParsedDocument/Block/Locator, registry, PDF text/DOCX/TXT/MD/HTML parsers; giữ page/paragraph/table/source offsets; HTML không fetch network. OCR dành T15.
- **Xong khi thỏa mãn DoD:**
  1. `uv run pytest tests/integration/test_text_parsers.py` dùng parser thật trên fixtures EN/VI và PDF/DOCX nhiều trang/bảng, locator trỏ đúng nguồn, corrupt/encrypted file trả lỗi rõ.
  2. Giới hạn MIME/size/timeouts và safe temp cleanup hoạt động; HTML script/external refs không chạy. README/RUNBOOK format matrix đánh dấu đúng phần text, scan chưa verified.
- **Cạm bẫy:** Không bịa page DOCX; không coi empty extraction là thành công; không làm mất dấu hoặc headers; không dùng QA file làm nguồn parse.
- **Ghi chú thực thi:** Chưa có attempt. Commit dự kiến `feat(T13): parse text documents with source provenance`.

<a id="t14"></a>
### T14 — XLSX, CSV, PPTX và bảng

- **Trạng thái:** TODO
- **Phụ thuộc:** T13.
- **Tham chiếu kế hoạch:** [P07](plan.md#p07), [P06](plan.md#p06).
- **Công việc:** XLSX sheet/cell locators, CSV rows/header, PPTX slide/block, table normalization chung; formula/cached value policy, archive limits.
- **Xong khi thỏa mãn DoD:**
  1. `uv run pytest tests/integration/test_office_tables.py` PASS trên multi-sheet, merged header, units, missing cached formula, multi-slide, CSV quoting/delimiter/Unicode; locator round-trip đúng ô/slide/row.
  2. Archive bomb/external links/macros không được thực thi; README/RUNBOOK nêu `.doc/.xls/.ppt` chưa hỗ trợ và không cam kết suy luận biểu đồ.
- **Cạm bẫy:** Sheet không là trang PDF; không tính lại công thức; không bỏ đơn vị/tiêu đề cột rồi khiến số liệu sai.
- **Ghi chú thực thi:** Chưa có attempt. Commit dự kiến `feat(T14): preserve spreadsheet and table evidence`.

<a id="t15"></a>
### T15 — OCR EN/VI có kiểm chứng

- **Trạng thái:** TODO
- **Phụ thuộc:** T14, T13.
- **Tham chiếu kế hoạch:** [P07](plan.md#p07), [P02](plan.md#p02).
- **Công việc:** Tesseract CLI eng/vie trong worker Docker, Docling OCR config, scan/mixed PDF và PNG/JPEG, quality status, per-page fallback và cancellation/time limits.
- **Xong khi thỏa mãn DoD:**
  1. `uv run pytest tests/integration/test_ocr.py` trong worker image PASS với scan EN/VI có dấu, ảnh và mixed PDF; kiểm phrase/locator gốc thật và không nhân đôi text layer.
  2. Thiếu tessdata/ảnh trắng/không đọc được có trạng thái rõ; ghi command, OCR engine/version, page count, elapsed/RAM và actual output excerpt. RUNBOOK có bước chẩn đoán OCR.
- **Cạm bẫy:** Không mock OCR để nghiệm thu; không OCR lại mọi trang mặc định; không nhầm language code của engine; không thêm VLM lớn làm vượt máy local.
- **Ghi chú thực thi:** Chưa có attempt. Commit dự kiến `feat(T15): support Vietnamese and English OCR`.

<a id="t16"></a>
### T16 — Chunking theo cấu trúc và source locators

- **Trạng thái:** TODO
- **Phụ thuộc:** T15, T13, T14.
- **Tham chiếu kế hoạch:** [P03](plan.md#p03), [P07](plan.md#p07), [P04](plan.md#p04).
- **Công việc:** Token-aware chunks 512/64 baseline, table row groups/context, stable IDs/versioned fingerprints, citation source maps, domain chunk profile hooks.
- **Xong khi thỏa mãn DoD:**
  1. `uv run pytest tests/unit/test_chunking.py` PASS với tokenizer thật: token budgets, Unicode, long block/table, overlap, stable rerun IDs, different source version tạo ID khác.
  2. `uv run pytest tests/integration/test_source_locators.py` chứng minh chunk->PDF/DOCX/XLSX/PPTX source đúng, không vượt bảng/đơn vị và không off-by-one trang; config/reindex implications trong RUNBOOK.
- **Cạm bẫy:** Không cắt token theo ký tự; không để overlap biến citation quote sai vị trí; không thay tokenizer mà giữ fingerprint cũ.
- **Ghi chú thực thi:** Chưa có attempt. Commit dự kiến `feat(T16): chunk documents with stable source mappings`.

<a id="t17"></a>
### T17 — Embedding/reranker inference service

- **Trạng thái:** TODO
- **Phụ thuộc:** T16, T02.
- **Tham chiếu kế hoạch:** [P02](plan.md#p02), [P08](plan.md#p08), [P12](plan.md#p12).
- **Công việc:** Ports và service nội bộ chạy BGE-M3 dense+sparse, reranker v2 M3, model revision/cache manifest, batching/queue/semaphore/cancel, CPU path và GPU override. Ưu tiên query hơn indexing.
- **Xong khi thỏa mãn DoD:**
  1. `uv run pytest tests/integration/test_model_inference.py` với weights thật PASS: dense dimension/normalization, sparse indices, EN/VI, rerank score, limits/cancel; không chỉ kiểm fake vectors.
  2. CPU smoke bắt buộc, pin revisions, ghi RAM/warmup/latency thật và chứng minh không nhân model mỗi API worker. Kiểm GPU capability; nếu runtime khả dụng chạy Docker GPU smoke và ghi VRAM. Nếu không khả dụng, ghi output capability check + GPU profile NOT_AVAILABLE (tùy chọn), không claim GPU verified; vẫn nghiệm thu CPU path.
- **Cạm bẫy:** Không coi sigmoid score là probability correctness; không load hết models trong từng process; không đổi embedding revision trong cùng collection ngầm.
- **Ghi chú thực thi:** Chưa có attempt. Commit dự kiến `feat(T17): add bounded multilingual model inference`.

<a id="t18"></a>
### T18 — Qdrant repository bắt buộc scope

- **Trạng thái:** TODO
- **Phụ thuộc:** T17, T10.
- **Tham chiếu kế hoạch:** [P01](plan.md#p01), [P04](plan.md#p04), [P08](plan.md#p08).
- **Công việc:** Collection versioned named dense/sparse vectors, payload indexes, scoped upsert/search/fetch-neighbors/generation cleanup; không public unscoped search. PG allowed version/generation set là authority.
- **Xong khi thỏa mãn DoD:**
  1. `uv run pytest tests/integration/test_qdrant_scope.py` PASS trên Qdrant thật: 2 apps/2 users/2 sessions cùng owner, stale generations, empty allowed set, dense/sparse branches và neighbor expansion.
  2. Empty scope không phát search all; update/retry point IDs idempotent; collection config/reindex/retained-index semantics được ghi RUNBOOK.
- **Cạm bẫy:** Filter sau retrieval là chưa đủ; chỉ lọc owner vẫn lộ session khác; mỗi branch prefetch phải có filter; vector retained không tự có quyền query.
- **Ghi chú thực thi:** Chưa có attempt. Commit dự kiến `feat(T18): enforce scoped Qdrant access`.

<a id="t19"></a>
### T19 — Ingestion worker end-to-end và atomic index publication

- **Trạng thái:** TODO
- **Phụ thuộc:** T18, T12, T15, T16.
- **Tham chiếu kế hoạch:** [P04](plan.md#p04), [P07](plan.md#p07), [P12](plan.md#p12).
- **Công việc:** Nối storage->parse/OCR->chunk->embed->Qdrant->PG publication, Celery lease/retry/redelivery/cancel/progress; generation cleanup có scope. Bật worker/dispatcher/inference trong Compose chuẩn.
- **Xong khi thỏa mãn DoD:**
  1. `uv run pytest tests/integration/test_ingestion_pipeline.py` với MinIO/PG/Redis/Qdrant/model thật: ingest PDF scan+XLSX+text, retry duplicate, partial Qdrant failure, source changed, worker kill/resume đều PASS.
  2. Query visibility chỉ generation ready; delete/detach trong job không hồi sinh link; source hash không đổi; report job/count/locator và README/RUNBOOK luồng ingest thật.
- **Cạm bẫy:** Celery redelivery có thể lặp; PG và Qdrant không cùng transaction; không báo ready trước đủ chunks; không xóa generation đang phục vụ khi reindex thất bại.
- **Ghi chú thực thi:** Chưa có attempt. Commit dự kiến `feat(T19): complete durable document ingestion`.

## Phase 4 — Retrieval và domains

<a id="t20"></a>
### T20 — Domain registry, scope policies và hội thoại

- **Trạng thái:** TODO
- **Phụ thuộc:** T19, T03, T10.
- **Tham chiếu kế hoạch:** [P01](plan.md#p01), [P03](plan.md#p03), [P08](plan.md#p08).
- **Công việc:** Register default/document/multilingual, ScopedRetrievalContext, config validation, history budgeting và rewrite port; provider thật nối T23. Custom test domain chứng minh extension không sửa router.
- **Xong khi thỏa mãn DoD:**
  1. `uv run pytest tests/contract/test_domain_registry.py tests/security/test_history_scope.py` PASS: unknown domain, empty subset, ID ngoài session, history stale citations/system injection, custom hook không bypass repository scope.
  2. Follow-up query rewrite dùng provider test có schema rõ và giữ session; API language defaults/overrides nhất quán. README/RUNBOOK domain matrix cập nhật.
- **Cạm bẫy:** History chỉ hỗ trợ hiểu câu hỏi, không là factual evidence; không biến bilingual dataset thành runtime domain thứ tư; không cho registry chạy code từ request.
- **Ghi chú thực thi:** Chưa có attempt. Commit dự kiến `feat(T20): compose extensible session-scoped domains`.

<a id="t21"></a>
### T21 — Dense/sparse hybrid retrieval

- **Trạng thái:** TODO
- **Phụ thuộc:** T20, T18, T17.
- **Tham chiếu kế hoạch:** [P08](plan.md#p08), [P03](plan.md#p03), [P11](plan.md#p11).
- **Công việc:** Dense baseline, sparse lexical BGE-M3, RRF, bounded candidates, language filters, same-scope neighbors; retrieval trace đã redacted cho eval.
- **Xong khi thỏa mãn DoD:**
  1. `uv run pytest tests/integration/test_retrieval.py` trên vector/model thật PASS với multi-doc, keyword/numeric, EN->VI/VI->EN, distractor và empty/no-match; xác minh language filter trong mỗi branch.
  2. Dense/hybrid toggle cấu hình tái tạo được, top-k/budget có boundary tests; retrieved chunks không lấy từ QA ground truth; RUNBOOK mô tả tunables và giới hạn.
- **Cạm bẫy:** RRF scores không so trực tiếp cosine threshold; sparse branch không được quên auth; không dùng query gold document IDs để làm đẹp recall.
- **Ghi chú thực thi:** Chưa có attempt. Commit dự kiến `feat(T21): add scoped hybrid multilingual retrieval`.

<a id="t22"></a>
### T22 — Reranking và đánh giá đủ bằng chứng

- **Trạng thái:** TODO
- **Phụ thuộc:** T21, T17.
- **Tham chiếu kế hoạch:** [P08](plan.md#p08), [P09](plan.md#p09), [P11](plan.md#p11).
- **Công việc:** Rerank top candidates, passage/token budget, evidence policy trả supported/insufficient/conflicting reason, model thresholds versioned; baseline thresholds chưa là calibration kết thúc.
- **Xong khi thỏa mãn DoD:**
  1. `uv run pytest tests/integration/test_evidence_selection.py` dùng reranker thật PASS: relevant/irrelevant/conflicting, multi-evidence, number/unit/table headers, budget/cancellation.
  2. `uv run pytest tests/security/test_evidence_scope.py` không cho passages/history ngoài scope vào LLM context; RUNBOOK ghi threshold pending calibration T31, không quảng cáo confidence xác suất.
- **Cạm bẫy:** Có nearest neighbor không nghĩa có đáp án; không bỏ citation provenance khi rerank; không đưa hết document vào prompt để vượt thiếu evidence.
- **Ghi chú thực thi:** Chưa có attempt. Commit dự kiến `feat(T22): select ranked evidence with answerability state`.

## Phase 5 — Generation, citations và streaming

<a id="t23"></a>
### T23 — DeepSeek và Anthropic provider adapters

- **Trạng thái:** TODO
- **Phụ thuộc:** T22, T20.
- **Tham chiếu kế hoạch:** [P02](plan.md#p02), [P09](plan.md#p09), [P05](plan.md#p05).
- **Công việc:** generate/stream/rewrite implementations, provider-specific request schema, model/env, token budgets, timeout/cancel/retry/usage. Kiểm official SDK/API docs khi code; không đòi provider keys trong unit tests.
- **Xong khi thỏa mãn DoD:**
  1. `uv run pytest tests/contract/test_llm_providers.py` PASS với recorded/synthetic protocol fixtures: usage missing, SSE split frame, 429, 5xx, malformed event, timeout/disconnect; không retry sau emitted token.
  2. Cấu hình hai provider độc lập và secret redaction có test; README/RUNBOOK ghi bước live verification ở T26, không đánh dấu live PASS tại đây.
- **Cạm bẫy:** Anthropic không phải OpenAI-compatible endpoint; không hardcode model ID lỗi thời; không lộ key; không tự fallback đổi provider trong stream.
- **Ghi chú thực thi:** Chưa có attempt. Commit dự kiến `feat(T23): support DeepSeek and Anthropic generation`.

<a id="t24"></a>
### T24 — Answer assembly và citation validation

- **Trạng thái:** TODO
- **Phụ thuộc:** T23, T22, T16.
- **Tham chiếu kế hoạch:** [P06](plan.md#p06), [P09](plan.md#p09), [P08](plan.md#p08).
- **Công việc:** Prompt templates, evidence allowlist IDs, answerability, bounded citation repair, response contexts/usage/timing, scoped citation resolver. Revalidate scope trước prompt/final.
- **Xong khi thỏa mãn DoD:**
  1. `uv run pytest tests/integration/test_answer_pipeline.py tests/security/test_citations.py` PASS: supported có evidence, insufficient vẫn gọi LLM để diễn đạt, invalid ID/quote bị reject/repair hữu hạn, provider fail không thành insufficient giả.
  2. Citation round-trip PDF page/DOCX paragraph/XLSX cell và stale/detached chunk bị chặn; RUNBOOK JSON/error examples validate với schema.
- **Cạm bẫy:** Không tự tạo sources cho model claim; không coi history là evidence; không đồng nhất missing provider với thiếu bằng chứng tài liệu.
- **Ghi chú thực thi:** Chưa có attempt. Commit dự kiến `feat(T24): return grounded answers and verified citations`.

<a id="t25"></a>
### T25 — SSE, backpressure và cancellation

- **Trạng thái:** TODO
- **Phụ thuộc:** T24, T23.
- **Tham chiếu kế hoạch:** [P09](plan.md#p09), [P06](plan.md#p06), [P12](plan.md#p12).
- **Công việc:** POST SSE events, heartbeat, bounded buffers, sentence citation ID checking, final authoritative JSON, disconnect/upstream cancel, per-event scope revision validation; document client parser semantics.
- **Xong khi thỏa mãn DoD:**
  1. `uv run pytest tests/e2e/test_streaming.py` với real HTTP server PASS: event order, UTF-8 tiếng Việt split frames, exactly one done/error, heartbeat, partial provider failure, client disconnect không leak slots.
  2. Detach/delete giữa stream dừng với scope_changed, không phát done success; JSON và SSE final schema tương đương. RUNBOOK có parser pseudocode/HTTPX example và delta provisional rule.
- **Cạm bẫy:** SSE HTTP 200 ban đầu không có nghĩa request thành công; EventSource không phù hợp POST auth; bytes đã gửi không thu hồi được; không retry lặp answer.
- **Ghi chú thực thi:** Chưa có attempt. Commit dự kiến `feat(T25): stream scoped answers with cancellation`.

<a id="t26"></a>
### T26 — API end-to-end và provider smoke thật

- **Trạng thái:** TODO
- **Phụ thuộc:** T25, T19, T09.
- **Tham chiếu kế hoạch:** [P06](plan.md#p06), [P09](plan.md#p09), [P13](plan.md#p13).
- **Công việc:** Nối toàn bộ public routes/schema, CLI demo app độc lập, ingestion/status/query/history/detach/delete flow. Chạy LLM thật cho mỗi provider đã yêu cầu.
- **Xong khi thỏa mãn DoD:**
  1. `uv run pytest tests/e2e/test_public_api.py` PASS với local Docker dependencies; fixture app upload S3 rồi register, poll, hỏi nối tiếp, nhận citations/stream, delete chat và kiểm source/index còn nguyên.
  2. `uv run python scripts/smoke_llm.py --provider deepseek` và `uv run python scripts/smoke_llm.py --provider anthropic` PASS live cho JSON/SSE/insufficient, lưu model IDs/usage/output redacted; thiếu key phải BLOCKED, không skip rồi COMPLETE.
- **Cạm bẫy:** Không sửa repo Scarlet; không gọi credential từ frontend; không vô tình benchmark hàng nghìn QA bằng LLM trong smoke; không upload tài liệu người dùng ngoài fixtures đã chọn.
- **Ghi chú thực thi:** Chưa có attempt. Commit dự kiến `test(T26): verify public RAG API with live providers`.

## Phase 6 — UI quản trị

<a id="t27"></a>
### T27 — Admin auth, metadata API và audit

- **Trạng thái:** TODO
- **Phụ thuộc:** T26, T10.
- **Tham chiếu kế hoạch:** [P05](plan.md#p05), [P10](plan.md#p10), [P12](plan.md#p12).
- **Công việc:** Admin login session/password hash/logout/CSRF, metadata endpoints phân trang, counts/health, job retry/cancel, session detach/tombstone và reindex qua job có audit; không raw content viewer.
- **Xong khi thỏa mãn DoD:**
  1. `uv run pytest tests/security/test_admin_auth.py tests/integration/test_admin_operations.py` PASS: unauthorized, CSRF, session expiry, escaped metadata, audited actions, illegal transition và no-source-delete.
  2. Admin response/log không có text chunks/answers/secrets; app credential không tự có admin role. RUNBOOK admin setup/permission matrix rõ.
- **Cạm bẫy:** Admin metadata access không đồng nghĩa quyền đọc mọi tài liệu; không cấp SQL/vector console; không cancel job bằng cách xóa bản gốc.
- **Ghi chú thực thi:** Chưa có attempt. Commit dự kiến `feat(T27): add audited administration APIs`.

<a id="t28"></a>
### T28 — Admin UI local

- **Trạng thái:** TODO
- **Phụ thuộc:** T27.
- **Tham chiếu kế hoạch:** [P10](plan.md#p10), [P02](plan.md#p02).
- **Công việc:** Jinja2/CSS/JS local assets cho login/overview/documents/jobs/sessions/index/evaluation reports; forms/polling/pagination/filter; loading/empty/error states; keyboard/responsive, no CDN dependency.
- **Xong khi thỏa mãn DoD:**
  1. `uv run pytest tests/integration/test_admin_views.py` PASS, UI đọc dữ liệu thật từ admin API; action gửi CSRF, phản hồi trạng thái lỗi; không hardcode dashboard numbers.
  2. Mở UI local và kiểm trực quan desktop/mobile width, keyboard focus, table overflow, labels; lưu evidence quan sát thật; README/RUNBOOK có URL/login/use cases đúng.
- **Cạm bẫy:** Không xây UI chat hoặc tính năng nguồn ngoài scope; không nhúng secrets trong HTML/JS; không tạo hosting/cloud deployment vì yêu cầu local.
- **Ghi chú thực thi:** Chưa có attempt. Commit dự kiến `feat(T28): build the local administration interface`.

<a id="t29"></a>
### T29 — Browser acceptance của admin

- **Trạng thái:** TODO
- **Phụ thuộc:** T28, T27.
- **Tham chiếu kế hoạch:** [P10](plan.md#p10), [P13](plan.md#p13).
- **Công việc:** Playwright flows có backend thật cho login/logout/list/filter/retry/detach/reindex và evaluation empty state; fix lỗi trong scope UI, không thêm chức năng.
- **Xong khi thỏa mãn DoD:**
  1. `uv run pytest tests/e2e/test_admin_browser.py` PASS với Docker backend và browser thật; đánh giá loading/error, session expiry, CSRF/XSS metadata, responsive/keyboard.
  2. Retry/reindex có job/audit thật, UI session deletion không đổi source hash; screenshots/logs không chứa secrets, paths ghi handoff. RUNBOOK troubleshooting UI đã thử.
- **Cạm bẫy:** HTTP template 200 chưa chứng minh UI dùng được; không dùng ảnh/mock data thay backend thật; không để browser session admin credentials vào Git.
- **Ghi chú thực thi:** Chưa có attempt. Commit dự kiến `test(T29): verify administration browser workflows`.

## Phase 7 — Đánh giá chất lượng

<a id="t30"></a>
### T30 — Evaluation harness và protocol chống leakage

- **Trạng thái:** TODO
- **Phụ thuộc:** T29, T08, T26.
- **Tham chiếu kế hoạch:** [P11](plan.md#p11), [P01](plan.md#p01).
- **Công việc:** CLI eval ingest/retrieval/generation/report, isolated eval app/user/session/index; gold adapter FinanceBench pages và bilingual languages; document/parallel-group splits, deterministic samples, metrics/manifest schema.
- **Xong khi thỏa mãn DoD:**
  1. `uv run pytest tests/contract/test_eval_protocol.py tests/security/test_eval_leakage.py` PASS: answer/QA không ingest, baseline/tuned same scope, cross-lingual filters thật, correct zero->one based conversion, numeric scoring/Unicode.
  2. `uv run python scripts/evaluate.py --help` và fixture benchmark chạy thật; config/splits/gates được commit trước tuning T31. README/RUNBOOK giải thích full retrieval và generation sample, metric limitations.
- **Cạm bẫy:** Không lọc gold page trước retrieve; không tune held-out; không coi XQuAD là unanswerable benchmark; không trộn eval namespace với user data.
- **Ghi chú thực thi:** Chưa có attempt. Commit dự kiến `feat(T30): add reproducible RAG evaluation harness`.

<a id="t31"></a>
### T31 — Benchmark thật, calibration và báo cáo chất lượng

- **Trạng thái:** TODO
- **Phụ thuộc:** T30, T21, T22.
- **Tham chiếu kế hoạch:** [P11](plan.md#p11), [P08](plan.md#p08), [P13](plan.md#p13).
- **Công việc:** Ingest corpus documents thật, dense/hybrid/hybrid+rerank trên full retrieval QA; tune theo frozen tuning split, freeze config rồi held-out. Generation >=130 câu theo protocol, một provider đã verified là benchmark mặc định; provider còn lại đã smoke T26.
- **Xong khi thỏa mãn DoD:**
  1. `uv run python scripts/evaluate.py --config configs/evaluation.yaml --stage retrieval` và `--stage generation` hoàn tất; lưu IDs/counts/model/index/corpus revisions, timings/usage và metrics từng domain/slice thật.
  2. Gates P11 đạt; report chỉ rõ so baseline, citation validity/faithfulness, lỗi số/trang/EN-VI, unanswerable riêng; nếu không đạt sửa trong tuning split hoặc BLOCKED, không đổi held-out/gold. README/RUNBOOK và admin report dùng report thật.
- **Cạm bẫy:** Không hardcode score/count; không xem synthetic fixture như official corpus; không tune theo đáp án held-out; model judge không thay gold; không giấu degraded slice trong trung bình.
- **Ghi chú thực thi:** Chưa có attempt. Commit dự kiến `test(T31): record measured RAG quality baselines`.

## Phase 8 — Reliability, an toàn dữ liệu và vận hành

<a id="t32"></a>
### T32 — Session isolation và kiểm thử lỗi có chủ đích

- **Trạng thái:** TODO
- **Phụ thuộc:** T31, T25, T27.
- **Tham chiếu kế hoạch:** [P01](plan.md#p01), [P04](plan.md#p04), [P05](plan.md#p05), [P09](plan.md#p09).
- **Công việc:** Cross-cutting regression/fault suite: cùng owner khác session, stale history/citations, delete/detach race, reindex race, prompt injection, SSRF/ZIP limits, rate-limit, log redaction, upstream/broker/vector failure.
- **Xong khi thỏa mãn DoD:**
  1. `uv run pytest tests/security tests/integration/test_failure_recovery.py` PASS với dependencies thật cho các đường cần DB/Qdrant; không có content/citation leakage ở bất kỳ branch/history/admin/stream nào.
  2. Detach/delete dưới tải và worker kill không hồi sinh scope, partial index không phục vụ, source không thay; RUNBOOK có incident diagnosis/recovery đã thử, gate fixtures 100%.
- **Cạm bẫy:** Unit mocked filter không chứng minh Qdrant thực có scope; đừng chỉ test khác user mà quên cùng user khác session; không đổi retention để che lỗi.
- **Ghi chú thực thi:** Chưa có attempt. Commit dự kiến `test(T32): harden isolation and failure recovery`.

<a id="t33"></a>
### T33 — Tải 15–20 người dùng và ngân sách local

- **Trạng thái:** TODO
- **Phụ thuộc:** T32, T17, T26.
- **Tham chiếu kế hoạch:** [P02](plan.md#p02), [P12](plan.md#p12), [P13](plan.md#p13).
- **Công việc:** Async load driver, 15/20 virtual users nhiều owner/session, streaming/nonstream + ingestion nền; hai chế độ provider giả có latency để tách core và provider thật với batch hữu hạn; resource telemetry, backpressure/tuning within scope.
- **Xong khi thỏa mãn DoD:**
  1. `uv run python scripts/load_test.py --users 15 --duration 120 --mode stub` và `--users 20 --duration 120 --mode stub` PASS; thêm `--users 20 --requests 40 --mode live` với provider thật. Mỗi chế độ báo riêng, không gộp số đo.
  2. Không OOM/unbounded queue/process crash/resource leak hoặc cross-session evidence; tất cả request có terminal outcome; ở tải mục tiêu stub admission >=95% và accepted requests thành công >=99%, 429 ghi riêng (không loại để che từ chối hàng loạt); report p50/p95 TTFT/total, admission/rejections/5xx, RAM/VRAM và mức vượt ngân sách nếu có. Sửa để đạt budgets P02 hoặc báo blocker, không tự hứa SLA.
- **Cạm bẫy:** 20 users không là 20 model copies; TTFT không tính heartbeat/meta; không tắt auth/rerank lén để làm đẹp số; không dùng corpus 1 GB như kích thước RAM/index.
- **Ghi chú thực thi:** Chưa có attempt. Commit dự kiến `perf(T33): validate bounded local concurrency`.

<a id="t34"></a>
### T34 — Backup, restore, restart và index migration rehearsal

- **Trạng thái:** TODO
- **Phụ thuộc:** T33, T19.
- **Tham chiếu kế hoạch:** [P04](plan.md#p04), [P12](plan.md#p12), [P15](plan.md#p15).
- **Công việc:** Scripts/quy trình maintenance snapshot PG+Qdrant+config, restore môi trường tách biệt, restart persistence, model/index revision migration rollback không mất nguồn; redacted diagnostics và disk growth notes.
- **Xong khi thỏa mãn DoD:**
  1. `uv run python scripts/backup.py --output <workspace-backup-dir>` tạo manifest thật; `uv run python scripts/restore_check.py --backup <workspace-backup-dir> --project rag-restore-check` restore vào volumes riêng, kiểm counts/query/citations/session restrictions sau restore.
  2. Worker/API/Redis restart vẫn reconcile jobs, source hashes không đổi; RUNBOOK chứa commands đã chạy và recovery boundaries; không ghi backup/secret dumps vào Git.
- **Cạm bẫy:** PG/Qdrant snapshots khác thời điểm có thể lệch generation; không restore đè môi trường đang chạy; không dùng recursive delete hoặc `down -v` để tiện rehearsal.
- **Ghi chú thực thi:** Chưa có attempt. Commit dự kiến `chore(T34): verify backup and recovery procedures`.

## Phase 9 — Bàn giao

<a id="t35"></a>
### T35 — RUNBOOK tích hợp và client app độc lập

- **Trạng thái:** TODO
- **Phụ thuộc:** T34, T26, T29.
- **Tham chiếu kế hoạch:** [P06](plan.md#p06), [P09](plan.md#p09), [P15](plan.md#p15).
- **Công việc:** Hoàn thiện README/RUNBOOK tất cả mục; client FastAPI/HTTPX mẫu dưới examples chứng minh app upload/registration/history/SSE/citation/delete mapping. Tài liệu cho agent tích hợp Scarlet, không sửa Scarlet.
- **Xong khi thỏa mãn DoD:**
  1. `uv run pytest tests/e2e/test_reference_client.py` PASS qua HTTP thật: app/user auth, source upload, session-only queries, history, JSON/SSE, cancel/errors, deleted session và source/index retention; không import private core services.
  2. `uv run python scripts/check_docs.py` PASS; mọi public route/error/env trong RUNBOOK đối chiếu OpenAPI/code; fresh operator đi theo quickstart thực, placeholder cần secret được ghi rõ. Checklist Scarlet không còn quyết định kiến trúc ngầm.
- **Cạm bẫy:** README/RUNBOOK phải đã được cập nhật từng task, không dồn lần đầu ở đây; không ghi “Scarlet đã tích hợp”; app rewrite không được tuyên bố citation được core xác thực lại.
- **Ghi chú thực thi:** Chưa có attempt. Commit dự kiến `docs(T35): deliver verified application integration runbook`.

<a id="t36"></a>
### T36 — Nghiệm thu cuối và handoff sẵn sàng tích hợp

- **Trạng thái:** TODO
- **Phụ thuộc:** T35 và toàn bộ T00–T34 COMPLETE.
- **Tham chiếu kế hoạch:** [P13](plan.md#p13), [P14](plan.md#p14), [P16](plan.md#p16).
- **Công việc:** Fresh worker audit toàn bộ required features/gates/commit evidence; chạy clean-environment final smoke và checks, sửa lỗi nghiệm thu đúng phạm vi qua attempt mới nếu cần; đóng docs/summary/handoff.
- **Xong khi thỏa mãn DoD:**
  1. `uv run ruff check .`, `uv run mypy src`, `uv run pytest -m "not live and not slow"`, `uv run python scripts/check_docs.py`, `docker compose config --quiet` PASS; integration tests cần service phải thực sự chạy hoặc chạy nhóm riêng có output, không skip.
  2. Môi trường Compose project mới từ lock/images + env documented chạy sample ingestion/OCR/query/stream/admin; verify evidence T08/T26/T29/T31/T32/T33/T34 vẫn ứng với cấu hình cuối, rerun phần đã bị thay đổi. Không cần lặp full benchmark nếu config không đổi.
  3. Tất cả task COMPLETE với DoD/commit xác minh; README/RUNBOOK không claim chưa chứng minh; handoff ghi next work là tích hợp app, limitations và exact commands; final task commit thành công.
- **Cạm bẫy:** Không gọi complete vì hết context/budget; task BLOCKED không là hoàn thành; không xóa local volumes để có “clean”; không triển khai server hoặc push Git ngoài yêu cầu.
- **Ghi chú thực thi:** Chưa có attempt. Commit dự kiến `chore(T36): complete local RAG core acceptance`.
