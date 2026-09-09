# F7Hub Current State

Last verified: 2026-09-09

Branch: `feat/knowledge-search-fts5`

Base HEAD: `d584fd10902b0a3c361208412130462499c0a27b`

Status: Slice 015 implemented and verified, unstaged and uncommitted, ready for independent review. No commit, push or merge. Protected `Docs/10_FolderStructure.md` modification and `Docs/Archive/DocsOLD/00_Vision.md` deletion remain preserved; `ROOT.md` is unchanged.

## Current Milestone

CURRENT KNOWLEDGE ARTICLES ARE SEARCHABLE AND OPEN AUTHORITATIVELY

## Working

- SQLite bootstrap and six ordered migrations through `0006_knowledge_search.sql`
- Existing New Ticket, Saved Tickets, Quick Company/Contact, notes/status and reference workflows
- Knowledge create/list/read, DRAFT revision editing and immutable Version History
- RELATED ticket/article Link, Open, Unlink and Relink
- Current Knowledge search across article code, title, summary and Markdown body
- DRAFT, PUBLISHED and ARCHIVED current rows are searchable; historical version rows are not indexed
- Lightweight ranked results expose ID/code/title/status/current version/updated timestamp, then reload authoritative current detail
- Search button and Enter submission, result count, no-result state, safe failure with retained query and Clear Search to the full list
- Search/list/New/Edit/Version History actions are serialized through the existing `ServiceTaskRunner`
- Insert, repeated searchable-field update and delete synchronize FTS automatically; existing rows are backfilled during migration

## Search Contract

`KnowledgeWorkspace → KnowledgeService.search_articles → KnowledgeRepository.search_articles → SQLite FTS5` preserves the GUI/service/repository boundary. The service converts plain text into quoted `unicode61` letter/number/private-use tokens joined by implicit AND. Empty or punctuation-only input performs no MATCH. Quotes, parentheses, asterisks and operator-looking text do not expose raw FTS syntax.

The repository executes a parameterized MATCH, joins `knowledge_articles_fts.rowid` to the authoritative `knowledge_articles` row and orders by `bm25`, `updated_at DESC`, then `knowledge_article_id DESC`. Selection uses the existing `get_article` path, so an edited result opens current persisted content and a result deleted before opening receives safe missing-article feedback.

Migration 0006 owns only derived search infrastructure: the external-content virtual table, its four shadow tables, three triggers and initial `rebuild`. Relational Knowledge rows and immutable history remain owned by migration 0005.

## Deferred / Limitations

- Historical-revision search, historical status snapshots, restore/revert, historical editing/deletion and compare/apply
- Search filters, result snippets/highlighting, pagination, saved searches, advanced query syntax and large-library performance claims
- Unified search, ticket search, provider abstraction, recommendations and AI ranking
- Article publishing/archiving/deletion, categories/tags and ticket-driven article creation/editing
- Bulk relationship operations, APPLIED/RESOLUTION_SOURCE workflows and relationship history/undo
- Full company/contact/category management, PowerShell integration and AutoHotkey login startup
- Actual user library volume, other screen sizes, DPI modes and assistive-technology coverage are NOT VERIFIED

## Validation

Fresh focused evidence during Slice 015:

| Scope | Result |
|---|---:|
| New migration + search Database tests | 11 PASS |
| Relevant repository/service/migration tests | 42 PASS |
| Knowledge GUI module | 23 PASS |
| Targeted new Integration cases | 4 PASS |
| Post-visual-fix GUI sizing case | 1 PASS |

Fresh final suite evidence after the native visual correction and strengthened migration rollback/retry assertion:

| Suite | Count | Test duration | Exit |
|---|---:|---:|---:|
| Database | 262 PASS | 14.345s | 0 |
| GUI | 85 PASS | 10.560s | 0 |
| Integration | 77 PASS | 313.633s | 0 |

Total: **424 PASS**. Database → GUI → Integration ran sequentially after the final product-code correction. The later Database-only test strengthening was rerun independently; no product, GUI or Integration code changed afterward. Commands used `.venv\Scripts\python.exe`, `PYTHONPATH=$PWD\Python;$PWD`, `-B`, and offscreen Qt for GUI/Integration automation.

```powershell
.venv\Scripts\python.exe -B -m unittest discover -s Tests/Database -p "test_*.py" -v
.venv\Scripts\python.exe -B -m unittest discover -s Tests/GUI -p "test_*.py" -v
.venv\Scripts\python.exe -B -m unittest discover -s Tests/Integration -p "test_*.py" -v
```

FTS5 runtime probe: PASS with SQLite 3.50.4; `ENABLE_FTS5` is present and a temporary FTS5 virtual table was created successfully.

## Native Windows Evidence

PASS — fresh after the final code change on 2026-09-09 with Qt platform `windows`, isolated `slice015-native-postfix.db` and a 1000×700 main window. Ten deterministic checks covered pending async state and competing-action blocking; title/body/code/mixed-case/punctuation/C++ searches; every current lifecycle status; no results; safe failure/query retention; Clear Search; edit synchronization/current-only indexing; exact immutable V1 history; New Article; ticket Open Article; and database/FTS integrity.

All nine final captures were inspected. Controls, result counts, empty/failure states, current article details, history and regression workflows were readable without overlap. Initial inspection found full-list PUBLISHED/ARCHIVED status elision after a longer New Article title; identity columns now recalculate after each population, and the final capture shows complete values. Agent verification, not user acceptance testing.

Evidence folder: `C:\Users\Jo\AppData\Local\Temp\f7hub-slice015-native-051ce7bd8ade436399219a33358a1983`

## Database Evidence

- Migration history: six ordered entries, ending in logical name `knowledge_search`
- FTS objects: `knowledge_articles_fts`, four standard shadow tables and triggers `knowledge_articles_ai`, `knowledge_articles_ad`, `knowledge_articles_au`
- Query plan: `SCAN knowledge_articles_fts VIRTUAL TABLE INDEX 0:M4`, followed by the relational integer-primary-key lookup
- `PRAGMA integrity_check`: `ok`
- `PRAGMA foreign_key_check`: zero violations
- Failed migration 0006: virtual table, shadow tables, triggers and history record all roll back; retry applies once
- Migration hashes:
  - 0001: `84596d21bbae32c05cf92cb3512674eb5e598d3400210af6b67871aac71931da`
  - 0002: `46d3f6383e0463ee4130449d23ee87144012e972ac7c6c55c65018e2f5ac1864`
  - 0003: `6a6b01f2cc0be0855e6ae1794ee4db8a1518c0fb6d0cdeb40b7a3c51a2d16a24`
  - 0004: `7168f94abe6fd03429475f87c4851344653bb917a7b5838cabbcc3a9acf282d9`
  - 0005: `7e976210c37c7c6d46b1dae24c88e578b259449a02d1c58e48f9e9b53c354572`
  - 0006: `7d1488daa57ece75d1faa3ac87f455f099a82e94aa558f0b6fb055c6e7d2841d`

## Next Gate / Candidate

Independent Slice 015 review is next. Keep changes unstaged and uncommitted; do not push or merge.

Recommend exactly one next bounded slice: **Slice 016 — publish one DRAFT Knowledge article** through an explicit DRAFT → PUBLISHED transition that atomically sets `published_at`, preserves current content/history and verifies search/list/link behavior. Recommendation only; Slice 016 is not implemented.
