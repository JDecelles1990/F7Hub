# Decisions requiring approval (planning draft)

| Decision | Suggested default | Status |
|---|---|---|
| Canonical runtime authority | Existing F7Hub services/SQLite | Retain Foundation 0A |
| Draft dictionary representation | JSON seed files in Git | Proposed |
| Category vs Tag vs Issue Type | Separate semantics, map to existing records | Retain Foundation 0C |
| Canonical Tag identity | Reuse existing global Tags | Retain Foundation 0C |
| Tag families/hierarchy | Governed flat families, not tree tags | Review feature detail |
| Alias vs symptom phrase | Mark every imported alias as unreviewed search phrase | Needs semantic review |
| Language | Same identity, EN/FR labels/phrases | Proposed |
| Unscoped alias conflicts | Report ambiguity; never force one winner | Proposed |
| Causes | Hypotheses linked to issues | Proposed |
| Entity profile | Defined type, no automatic persistent occurrences | Retain Foundation 0C |
| Provenance | Keep source field and owner; acceptance separate | Proposed extension |
| Status | Document catalog proposal separately from ticket status | Proposed |
| SQL table strategy | Extend current schema after inventory | Not designed |

## Anti-patterns
- Do not add `tags`, `categories` or `entities` as a second global set of SQLite tables without identifying existing ownership.
- Do not convert all search keywords into Tags.
- Do not collapse an issue into a product label, or a cause into a confirmed diagnosis.
- Do not equate a detection or recognition profile with a concrete company/user/device.
- Do not edit Foundation documents, run migrations, or seed data as part of this planning artifact.
