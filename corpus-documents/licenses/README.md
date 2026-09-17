# Dataset attribution and license notices

These notices describe inspected upstream statements; they do not relicense company
reports or replace upstream legal terms. Actual pinned statements and metadata are
listed in [source-license-inventory.json](../source-license-inventory.json).

- **HotpotQA:** Yang et al. (2018), *HotpotQA: A Dataset for Diverse, Explainable
  Multi-hop Question Answering*, [paper](https://arxiv.org/abs/1809.09600).
  [Pinned README license](https://github.com/hotpotqa/hotpot/blob/3635853403a8735609ee997664e1528f4480762a/README.md#license)
  explicitly separates CC BY-SA 4.0 dataset terms from Apache 2.0 code terms.
  Retain original Wikipedia titles, dataset origin and description of normalization
  changes with permitted materializations.
  T05 uses the user-approved community/HF-maintained
  [pinned derivative](https://huggingface.co/datasets/hotpotqa/hotpot_qa/blob/1908d6afbbead072334abe2965f91bd2709910ab/README.md),
  whose card also declares CC BY-SA 4.0. Normalized QA/index/report adaptations remain
  under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/): Parquet semantic
  fields converted to legacy JSON, deterministic100QA subset, content-derived paragraph
  IDs and separated provenance. Original source answers/type/level/facts/text are
  preserved. Raw files/documents are local and ignored; no CMU byte-equivalence claim.
- **FinanceBench:** Islam et al. (2023), *FinanceBench: A New Benchmark for Financial
  Question Answering*, [paper](https://arxiv.org/abs/2311.11944).
  [Pinned GitHub README](https://github.com/patronus-ai/financebench/blob/cc39aeb4afdf33909ee1412188bf89035950c2eb/README.md)
  asks users to cite the work but supplies no explicit license in the inspected
  tree/README. The [publisher card](https://huggingface.co/datasets/PatronusAI/financebench/blob/e04404e3a97f69f79c14d42f24981a1c9c3bcd18/README.md)
  declares CC BY-NC 4.0 for its dataset; GitHub/PDF rights remain unresolved.
  Financial PDFs retain company rights and source attribution. No PDFs/raw gold
  are redistributed or committed; T06 needs a user decision or upstream grant.
- **XQuAD:** Artetxe, Ruder and Yogatama (2019), *On the Cross-lingual Transferability
  of Monolingual Representations*, [paper](https://arxiv.org/abs/1910.11856).
  [Pinned README license](https://github.com/google-deepmind/xquad/blob/7d30520c717524000f0d9d2f9c10a069acd9d285/README.md#license)
  explicitly states CC BY-SA 4.0 for the dataset. Retain SQuAD v1.1 origin,
  professional translation provenance and descriptions of normalization changes.

For datasets with an explicit applicable CC BY-SA 4.0 grant, preserve attribution,
the [license link](https://creativecommons.org/licenses/by-sa/4.0/) and changes;
adaptations retain ShareAlike terms. No dataset/PDF license is inferred from code
licenses. T04 downloaded only official README/metadata; T05 downloaded the specifically
approved pinned HF Parquet. No third-party company copyright notice was removed.
