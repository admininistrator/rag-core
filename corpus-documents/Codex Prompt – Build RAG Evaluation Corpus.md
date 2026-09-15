Bạn đang làm việc trong repository `rag-core`.

## Mục tiêu

Thiết lập một bộ corpus + ground-truth question/answer dùng để đánh giá chất lượng RAG cho 3 custom domain:

1. `default`
2. `document`
3. `bilingual`

Toàn bộ dữ liệu, script tải dữ liệu, dữ liệu đã normalize và tài liệu hướng dẫn phải nằm dưới:

`rag-core/corpus-documents`

Mục tiêu của task này KHÔNG phải train model và KHÔNG phải thay đổi pipeline RAG hiện tại.

Mục tiêu là tạo một bộ evaluation corpus có thể tái sử dụng để sau này benchmark:

- dense retrieval
- hybrid retrieval
- reranker
- chunking strategy
- answer correctness
- retrieval recall
- faithfulness
- citation accuracy
- cross-document retrieval
- cross-lingual retrieval

Hãy tự inspect repository `rag-core` trước khi triển khai để tuân theo conventions, Python environment và project structure hiện có.

---

# 1. DOMAIN: DEFAULT

## Dataset chính

Sử dụng official HotpotQA dataset:

Repository:

`hotpotqa/hotpot`

File ưu tiên:

`hotpot_dev_distractor_v1.json`

Không cần train hoặc cài baseline model của HotpotQA.

Không chạy toàn bộ legacy training setup của repository nếu không cần thiết.

Chúng ta chỉ cần dataset JSON.

HotpotQA mỗi example đã cung cấp:

- `_id`
- `question`
- `answer`
- `supporting_facts`
- `context`
- `type`
- `level`

## Mục tiêu evaluation

Default domain đại diện cho RAG kiến thức tổng quát.

Phải kiểm tra được:

- factual retrieval
- semantic retrieval
- multi-hop retrieval
- comparison questions
- bridge questions
- distractor/noise robustness
- supporting-document retrieval

## Dataset subset

Tạo một deterministic subset từ `hotpot_dev_distractor_v1.json`.

Target ban đầu:

`100 QA`

Ưu tiên cân bằng:

- bridge
- comparison
- medium
- hard

Nếu dataset distribution không cho phép chia hoàn toàn cân bằng thì ghi lại distribution thực tế.

Subset phải reproducible.

Sử dụng fixed random seed, ví dụ:

`seed = 42`

Không chọn subset bằng index thủ công tùy ý.

## Materialize corpus

Không để hệ thống evaluation dựa trực tiếp vào `context` nằm bên trong QA JSON.

Từ HotpotQA context, materialize các paragraph thành document độc lập để RAG thực sự phải ingest và retrieve chúng.

Ví dụ:

`corpus-documents/default/documents/*.md`

Mỗi document nên chứa metadata tối thiểu:

- document_id
- title
- source_dataset
- source_question_ids nếu applicable

Deduplicate paragraph/document nếu cùng một Wikipedia paragraph xuất hiện ở nhiều QA.

## Ground truth

Normalize QA thành JSONL:

`corpus-documents/default/qa/eval.jsonl`

Schema tối thiểu:

```json
{
  "id": "default_xxx",
  "domain": "default",
  "question": "...",
  "expected_answers": ["..."],
  "expected_documents": ["..."],
  "supporting_facts": [],
  "category": "bridge|comparison",
  "difficulty": "medium|hard",
  "language": "en",
  "answerable": true,
  "source_dataset": "hotpotqa"
}
```

`expected_documents` phải được suy ra từ `supporting_facts`, không phải từ toàn bộ distractor context.

---

# 2. DOMAIN: DOCUMENT

## Dataset chính

Sử dụng official open-source FinanceBench:

Repository:

`patronus-ai/financebench`

FinanceBench open-source sample cung cấp:

- khoảng 150 QA examples
- human-annotated gold answer
- evidence
- justification
- source document
- evidence page number
- source PDF documents

Các file quan trọng gồm:

`data/financebench_open_source.jsonl`

`data/financebench_document_information.jsonl`

và thư mục:

`pdfs/`

Không cần full proprietary/closed FinanceBench dataset.

Chỉ sử dụng phần được công khai trong official repository.

## Vì sao FinanceBench được chọn

Document domain phải kiểm tra RAG trên tài liệu thực tế dài, đặc biệt:

- PDF ingestion
- page-aware retrieval
- document metadata
- numerical answers
- financial tables/text
- cross-page context
- citation accuracy
- evidence retrieval
- reasoning trên tài liệu

FinanceBench phù hợp vì gold data đã chứa cả answer và evidence location.

## Corpus

Copy/download các PDF được reference bởi 150 open-source questions vào:

`corpus-documents/document/documents/`

Không download PDF không liên quan nếu không cần.

Nếu repository chứa nhiều PDF hơn số tài liệu thực sự referenced bởi open-source QA thì hãy resolve danh sách PDF từ metadata/QA trước và chỉ materialize tập cần thiết.

Preserve original filenames nếu có thể.

## QA normalization

Tạo:

`corpus-documents/document/qa/eval.jsonl`

Schema đề xuất:

```json
{
  "id": "document_xxx",
  "domain": "document",
  "question": "...",
  "expected_answers": ["..."],
  "expected_documents": ["..."],
  "evidence": [
    {
      "document": "...",
      "page": 0,
      "text": "..."
    }
  ],
  "justification": "...",
  "question_type": "...",
  "reasoning_type": "...",
  "language": "en",
  "answerable": true,
  "source_dataset": "financebench"
}
```

Quan trọng:

FinanceBench evidence page number có thể dùng zero-based indexing.

Không tự ý chuyển page number sang one-based mà không lưu rõ convention.

Trong manifest phải ghi:

`page_indexing: zero_based`

Nếu RAG của project sử dụng page number one-based cho citation thì conversion phải diễn ra tại evaluation adapter, không làm mất ground truth gốc.

---

# 3. DOMAIN: BILINGUAL

## Dataset chính

Sử dụng official XQuAD:

Repository:

`google-deepmind/xquad`

Hai file chính:

`xquad.en.json`

`xquad.vi.json`

XQuAD là dataset parallel.

English và Vietnamese chứa các paragraph/question/answer tương ứng.

Mục tiêu là test cả multilingual lẫn cross-lingual retrieval.

## Corpus

Materialize toàn bộ 240 parallel paragraph instances cho cả hai ngôn ngữ.

Cấu trúc:

`corpus-documents/bilingual/documents/en/`

`corpus-documents/bilingual/documents/vi/`

Mỗi document phải có một `parallel_group_id` để xác định paragraph English và Vietnamese tương ứng.

Ví dụ metadata:

```json
{
  "document_id": "xquad_en_001",
  "parallel_group_id": "xquad_parallel_001",
  "language": "en",
  "source_dataset": "xquad"
}
```

và:

```json
{
  "document_id": "xquad_vi_001",
  "parallel_group_id": "xquad_parallel_001",
  "language": "vi",
  "source_dataset": "xquad"
}
```

Không assume alignment chỉ dựa trên array position mà không validate.

Hãy inspect IDs / titles / QA structure và viết validation để chắc chắn EN-VI pair tương ứng.

Nếu official files không cung cấp một universal explicit parallel ID thì tạo deterministic `parallel_group_id` sau khi xác minh alignment.

## Evaluation slices

Phải tạo 4 loại test:

### A. EN → EN

English question.

Retrieve English corpus.

Expected answer bằng English.

### B. VI → VI

Vietnamese question.

Retrieve Vietnamese corpus.

Expected answer bằng Vietnamese.

### C. VI → EN

Vietnamese question.

Chỉ retrieve English corpus.

Expected answer phải lấy từ English counterpart của cùng parallel QA.

### D. EN → VI

English question.

Chỉ retrieve Vietnamese corpus.

Expected answer phải lấy từ Vietnamese counterpart của cùng parallel QA.

Đây là phần quan trọng nhất để phân biệt:

`multilingual RAG`

với:

`cross-lingual RAG`

## QA output

Tạo:

`corpus-documents/bilingual/qa/en_en.jsonl`

`corpus-documents/bilingual/qa/vi_vi.jsonl`

`corpus-documents/bilingual/qa/vi_en.jsonl`

`corpus-documents/bilingual/qa/en_vi.jsonl`

và optionally:

`corpus-documents/bilingual/qa/eval.jsonl`

là merged version của cả bốn.

Schema:

```json
{
  "id": "bilingual_xxx",
  "domain": "bilingual",
  "question": "...",
  "question_language": "vi",
  "corpus_language": "en",
  "answer_language": "en",
  "expected_answers": ["..."],
  "expected_documents": ["..."],
  "parallel_group_id": "...",
  "evaluation_slice": "vi_en",
  "answerable": true,
  "source_dataset": "xquad"
}
```

Có thể sử dụng toàn bộ 1190 QA nếu mapping sạch và kích thước hợp lý.

Nếu cần subset cho quick benchmark thì tạo thêm:

`eval_small.jsonl`

với deterministic sampling.

Không thay thế full normalized dataset bằng subset.

---

# 4. DIRECTORY STRUCTURE

Target cuối cùng nên gần với:

```text
rag-core/
└── corpus-documents/
    ├── README.md
    ├── manifest.json
    ├── scripts/
    │   ├── setup_corpus.py
    │   ├── prepare_default.py
    │   ├── prepare_document.py
    │   ├── prepare_bilingual.py
    │   └── validate_corpus.py
    │
    ├── default/
    │   ├── raw/
    │   ├── documents/
    │   ├── qa/
    │   │   └── eval.jsonl
    │   └── manifest.json
    │
    ├── document/
    │   ├── raw/
    │   ├── documents/
    │   ├── qa/
    │   │   └── eval.jsonl
    │   └── manifest.json
    │
    ├── bilingual/
    │   ├── raw/
    │   ├── documents/
    │   │   ├── en/
    │   │   └── vi/
    │   ├── qa/
    │   │   ├── en_en.jsonl
    │   │   ├── vi_vi.jsonl
    │   │   ├── vi_en.jsonl
    │   │   ├── en_vi.jsonl
    │   │   └── eval.jsonl
    │   └── manifest.json
    │
    └── licenses/
```

Có thể điều chỉnh nhẹ structure nếu conventions hiện tại của `rag-core` yêu cầu, nhưng phải giữ separation rõ ràng giữa:

- raw source
- ingestable documents
- evaluation QA

---

# 5. SETUP SCRIPT

Tạo một command duy nhất để setup corpus.

Ví dụ:

```bash
python corpus-documents/scripts/setup_corpus.py --all
```

và cho phép riêng từng domain:

```bash
python corpus-documents/scripts/setup_corpus.py --domain default
python corpus-documents/scripts/setup_corpus.py --domain document
python corpus-documents/scripts/setup_corpus.py --domain bilingual
```

Script phải:

1. download/clone nguồn cần thiết;
2. verify download;
3. normalize dataset;
4. materialize documents;
5. generate QA JSONL;
6. generate/update manifests;
7. run validation;
8. print summary.

Phải idempotent.

Chạy lại không được tạo duplicate data hoặc phá data đã chuẩn hóa.

Không yêu cầu user cài các model/baseline dependencies của HotpotQA, FinanceBench hoặc XQuAD.

Chỉ thêm Python packages thực sự cần cho việc tải, parse và normalize dataset.

Ưu tiên Python standard library nếu đủ.

---

# 6. MANIFEST

Mỗi domain cần `manifest.json`.

Thông tin tối thiểu:

```json
{
  "domain": "default",
  "dataset": "HotpotQA",
  "source_repository": "hotpotqa/hotpot",
  "dataset_version": "...",
  "downloaded_at": "...",
  "license": "...",
  "document_count": 0,
  "qa_count": 0,
  "languages": ["en"],
  "checksum": {},
  "notes": ""
}
```

Root:

`corpus-documents/manifest.json`

phải aggregate cả 3 domain.

Ghi lại commit hash/tag của upstream repository nếu clone từ Git.

Mục tiêu là corpus reproducible.

---

# 7. VALIDATION

`validate_corpus.py` phải fail với exit code khác 0 khi phát hiện lỗi nghiêm trọng.

Kiểm tra tối thiểu:

### Common

- file tồn tại
- JSON/JSONL parse được
- ID unique
- question không rỗng
- expected answer không rỗng
- referenced document tồn tại

### Default

- supporting document tồn tại trong materialized corpus
- selected HotpotQA QA vẫn giữ đúng original answer
- deterministic sampling reproducible

### Document

- source PDF tồn tại
- QA map được tới đúng PDF
- evidence page hợp lệ
- evidence text không bị mất
- gold answer không bị thay đổi

### Bilingual

- EN/VI parallel mapping hợp lệ
- question pair đúng counterpart
- answer pair đúng counterpart
- `vi_en` thực sự dùng VI question + EN expected evidence/answer
- `en_vi` thực sự dùng EN question + VI expected evidence/answer
- không vô tình retrieve corpus cùng language trong cross-lingual slice

---

# 8. README

Tạo:

`rag-core/corpus-documents/README.md`

README phải giải thích:

- mục tiêu của bộ corpus;
- ý nghĩa 3 domains;
- upstream datasets;
- licensing;
- setup commands;
- directory structure;
- QA schema;
- số lượng documents/questions thực tế;
- cách chạy validation;
- cách dùng các JSONL này cho RAG eval;
- bilingual evaluation matrix;
- limitations.

Phải nêu rõ:

### HotpotQA

Default benchmark chủ yếu kiểm tra generic multi-hop retrieval.

### FinanceBench

Document benchmark tập trung vào long-form PDF, evidence và page-aware citation.

### XQuAD

Bilingual benchmark tập trung vào EN/VI parallel QA.

XQuAD không có unanswerable questions, vì vậy không được diễn giải kết quả XQuAD như benchmark hallucination/rejection hoàn chỉnh.

---

# 9. LICENSING / DATA HYGIENE

Không commit dữ liệu nếu upstream license hoặc repository policy không cho phép.

Kiểm tra license trước khi quyết định commit raw datasets/PDFs.

Nếu raw corpus lớn hoặc không phù hợp để commit:

- thêm vào `.gitignore`;
- commit setup scripts;
- commit normalized lightweight metadata nếu license cho phép;
- document cách reproduce.

Không remove attribution.

Không mirror dataset sang một nguồn không chính thức khi official upstream vẫn khả dụng.

---

# 10. KHÔNG LÀM

Không:

- train HotpotQA baseline;
- train FinanceBench model;
- train XQuAD model;
- thay embedding model;
- thay retrieval pipeline;
- thay RAG APIs;
- ingest vào production vector database;
- benchmark model ngay trong task này;
- generate synthetic gold answers để thay cho official answers.

Task hiện tại chỉ chuẩn bị **evaluation corpus + QA ground truth**.

---

# 11. ACCEPTANCE CRITERIA

Task chỉ hoàn thành khi:

1. `rag-core/corpus-documents` tồn tại với đủ 3 domains.
2. Một setup command có thể reproduce corpus từ clean state.
3. Default có HotpotQA documents + normalized QA.
4. Document có FinanceBench PDFs + normalized human-annotated QA/evidence.
5. Bilingual có XQuAD EN + VI corpus.
6. Bilingual có đủ 4 slices:
   - EN→EN
   - VI→VI
   - VI→EN
   - EN→VI
7. Mọi QA reference tới document hợp lệ.
8. Validation script PASS.
9. README ghi source, license, counts và cách sử dụng.
10. Không có hidden manual steps ngoài những trường hợp upstream thực sự yêu cầu authentication.
11. Chạy lại setup không tạo duplicate.
12. In ra final summary tương tự:

```text
RAG Evaluation Corpus

Default
  dataset: HotpotQA
  documents: X
  QA: 100

Document
  dataset: FinanceBench
  PDFs: X
  QA: 150

Bilingual
  dataset: XQuAD
  EN documents: 240
  VI documents: 240
  EN→EN QA: 1190
  VI→VI QA: 1190
  VI→EN QA: 1190
  EN→VI QA: 1190

Validation: PASS
```

Không hardcode những count cuối cùng nếu upstream data thực tế khác; summary phải lấy từ data đã download và validate.

Sau khi hoàn thành, báo cáo:

- files đã tạo/thay đổi;
- upstream sources/version;
- actual corpus counts;
- validation result;
- bất kỳ limitation/blocker nào;
- command chính xác để reproduce setup từ đầu.