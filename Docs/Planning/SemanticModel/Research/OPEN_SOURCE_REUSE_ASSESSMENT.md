# Preliminary open-source reuse review

**Status: DESK_RESEARCH_ONLY.** Public project documentation/repository trees were examined. No third-party source downloaded, installed, executed, security-scanned, or benchmarked in the F7Hub Windows environment. Codex must complete a detailed independent audit before approving dependencies.

| Project | Documented role | Apparent license of code | Recommended treatment | Key unresolved checks |
|---|---|---|---|---|
| `rapidfuzz/RapidFuzz` | Fuzzy matching, comparison, ranking | MIT | High-priority lightweight read-only candidate | Python >=3.11; Windows VC++ 2019 redistributable, package/version compatibility, locale/abbreviation collision tests |
| `explosion/spaCy` | Language processing, token matching, entity/pattern extraction | MIT | High-priority rule/phrase recognizer candidate | French model accuracy, dependency footprint, input offsets and false positives |
| `MaartenGr/KeyBERT` | Embedding-based keyphrase extraction | MIT | Optional research candidate | CPU resources, model selection, phrase relevance vs canonical identity, local model download/license |
| `huggingface/sentence-transformers` (formerly UKPLab) | Embeddings, semantic similarity and reranking | Apache-2.0 | Optional multilingual semantic layer | Separate model license, offline model packaging, inference speed, hallucinated equivalence risk |
| `MaartenGr/BERTopic` | Unsupervised / guided topic discovery | MIT | Optional batch discovery experiment, not runtime baseline | UMAP/HDBSCAN/transformer dependencies, low-frequency topics, reproducibility, CPU memory, cluster review |
| `AnikMallick/ticket-nlp-classification` | Ticket classification and retrieval experiments | MIT listed in repo | Study methodology and evaluation; avoid copying model artifacts by default | Dataset rights, code safety, claimed scores reproduction, training/test leakage |
| `Afrin1012/it-support-ticket-classification` | Small Streamlit ticket category/priority sample | Code license **NOT VERIFIED**; linked dataset licensing separate | Read example only until code license clarified | Single-commit repository includes virtualenv/cache/model files, missing code LICENSE in inspected top-level inventory, model safety, data-origin verification |

Sources inspected (2026-10-08):

- https://github.com/rapidfuzz/RapidFuzz
- https://github.com/explosion/spaCy
- https://github.com/MaartenGr/KeyBERT
- https://github.com/huggingface/sentence-transformers
- https://github.com/MaartenGr/BERTopic
- https://github.com/AnikMallick/ticket-nlp-classification
- https://github.com/Afrin1012/it-support-ticket-classification
- https://zenodo.org/records/7648117

**Interesting external dataset to audit separately:**

- https://huggingface.co/datasets/ameau01/synthetic-it-support-tickets  (dataset card advertises 745 synthetic incidents with structured root causes and resolution plus redaction/retention sidecars; license MIT according to card; synthetic PII included intentionally; do not import unreviewed).

**Strong caution:** AnikMallick's own reported experiment found that simple retrieval-augmented neural classification degraded macro-F1 compared with other evaluated baselines. See project README. Retrieval ranking does not equal calibrated causal diagnostic probability.

**Recommended minimal stack:** built-in Python `json` / `re` / `sqlite3` and the existing SQLite FTS5 + optional `jsonschema` + `RapidFuzz` first. spaCy if rule/entity breadth justifies it. Embedding and clustering models after measured benefit on representative bilingual fixtures.
