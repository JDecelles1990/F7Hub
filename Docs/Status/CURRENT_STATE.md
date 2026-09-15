# F7Hub Current State

Last verified: 2026-09-15 (America/Toronto)

Branch: `feat/knowledge-status-filter`

Base and current HEAD: `0d650062066fa563c9c4d02a4afdd9c94c352065`

Status: PASS — READY FOR INDEPENDENT REVIEW. Slice 020 implementation, focused tests, full regression and native verification are complete. Work remains unstaged and uncommitted. Independent review is NOT complete; Slice 021 has NOT started.

## Current Milestone

READ-ONLY KNOWLEDGE STATUS FILTERING COMPOSES WITH CATEGORY AND CURRENT FTS SEARCH

## Working Behavior and Boundaries

All statuses, DRAFT, PUBLISHED and ARCHIVED filtering: IMPLEMENTED for normal Knowledge lists and current-article FTS results.

- Status and category are orthogonal. All/specific/Not selected category modes compose with all four status modes.
- Changing either filter during search reruns the last executed query, not unsubmitted text. Clear Search clears text/mode and preserves both filters.
- Replacement requests clear rows and all details before dispatch. Empty/failure states are truthful and retain filters for retry.
- New DRAFT articles reset status/category only when needed to reveal the authoritative uncategorized result.
- Publishing under DRAFT and archiving under PUBLISHED reset Status to All statuses, preserve a compatible category, and reveal the authoritative new state.
- Category mutation and content editing preserve status. Version History remains available for selected DRAFT/PUBLISHED/ARCHIVED records.
- Ticket Open Article clears search and resets Category/Status to All before explicit ID reveal; existing relationships remain unchanged.

Saved filters, tag/date filtering, multi-select/custom statuses, pagination, advanced search, Unpublish and Unarchive: NOT IMPLEMENTED. No migration, schema, index, ranking or lifecycle mutation change.

## Architecture and Queries

KnowledgeRepository.list_articles/search_articles and KnowledgeService now accept keyword-only `status=None`. The service accepts only None, DRAFT, PUBLISHED or ARCHIVED; lowercase, empty, unknown, integer and bool inputs are rejected before repository access. Existing category validation remains unchanged.

Repository reads build a small list of internal static predicate fragments and bind every external value. Normal list order remains updated_at DESC / knowledge_article_id DESC. Search keeps literal MATCH generation and bm25 / updated_at DESC / ID DESC, with category/status applied as relational predicates on the authoritative current row. FTS indexed columns, triggers and lightweight result records are unchanged.

KnowledgeWorkspace adds one static Status combo using item data rather than display text. It reuses the existing filter-state method and shared ServiceTaskRunner. No status reference load, new runner, filter service, dependency or MainWindow change exists. The Slice 019 category-reference runner and failure behavior are unchanged.

## Focused Validation

Environment: existing `.venv/Scripts/python.exe`, PYTHONPATH=Python plus repository root, PYTHONDONTWRITEBYTECODE=1; GUI/Integration use QT_QPA_PLATFORM=offscreen.

| Command after `python.exe -B -m unittest` | Result | Duration |
|---|---:|---:|
| `Tests.Database.test_knowledge_status_filter Tests.Database.test_knowledge_category_filter Tests.Database.test_knowledge_search Tests.Database.test_knowledge_service -v` | 42 PASS | 7.369s |
| `Tests.GUI.test_knowledge_status_filter Tests.GUI.test_knowledge_category_filter Tests.GUI.test_knowledge_workspace -v` | 48 PASS | 52.117s |
| Matrix + lifecycle/Ticket targeted Integration tests | 2 PASS | 27.898s |

An initial combined pre-test run exposed one legacy mock expecting no explicit `status=None`; production forwarding retained the existing call shape when All statuses is selected, and the complete focused/full runs then passed. This was a test-detected compatibility correction, not a final-suite failure.

## Full Sequential Regression

Commands, each run sequentially with the prescribed environment:

```powershell
.venv\Scripts\python.exe -B -m unittest discover -s Tests/Database -p "test_*.py" -v
.venv\Scripts\python.exe -B -m unittest discover -s Tests/GUI -p "test_*.py" -v
.venv\Scripts\python.exe -B -m unittest discover -s Tests/Integration -p "test_*.py" -v
```

| Suite | Result | Duration |
|---|---:|---:|
| Database | 311 PASS | 15.878s |
| GUI | 119 PASS | 67.037s |
| Integration | 89 PASS | 392.148s |

User-supplied baseline: 304 Database / 113 GUI / 88 Integration = 505. Slice 020 adds 7 Database, 6 GUI and 1 Integration test. Final total: **519 PASS**, zero failures/errors/skips, all three process exits 0, and no suite decreased.

Logs outside the repository:

- `C:\Users\Jo\AppData\Local\Temp\f7-s020-full-Database.log`
- `C:\Users\Jo\AppData\Local\Temp\f7-s020-full-GUI.log`
- `C:\Users\Jo\AppData\Local\Temp\f7-s020-full-Integration.log`

## Native Windows Evidence

PASS: QT_QPA_PLATFORM=windows, actual MainWindow at 1000×700, isolated synthetic SQLite. Verified static All/Draft/Published/Archived options, each lifecycle filter, category/status composition, FTS with both filters, Clear Search preservation, publish/archive reconciliation, new-DRAFT reveal, Version History and actual Ticket panel Open Article reset/reveal.

Six captures were opened and inspected: 01-all-statuses, 02-draft, 03-archived, 04-networking-published-search, 05-lifecycle-reconciled and 06-ticket-open-revealed. Search, Category and Status fit on one row; labels/options/status columns are readable; no horizontal clipping or important overlap was observed. This is agent verification, not independent review or user acceptance.

Evidence outside the repository:

- `C:\Users\Jo\AppData\Local\Temp\f7-s020-native-akrkf8hx`: six screenshots and synthetic.db.
- `C:\Users\Jo\AppData\Local\Temp\f7-s020-native.py`: native harness.

## Database and Preservation

Six migration files and six records. Database/Migrations/0001–0006, schema owners Docs/08_ERD.md and Docs/09_SQLSchema.md, and ROOT.md have no diff. Native synthetic integrity_check=ok, foreign_key_check=zero rows and external-content FTS integrity-check PASS. Focused query-only tests observed SELECT-only repository reads; complete database dumps before/after status-filter operations were identical in Database and Integration coverage.

Protected `Docs/10_FolderStructure.md` SHA256 remains `7DE1EAACB0F833AF5B26A29D8DF163E48F3D10765DD4471E325EC54224B9D258`. `Docs/Archive/DocsOLD/00_Vision.md` remains deleted. Neither protected path was edited, staged, restored, stashed or committed. No validation artifacts are in the repository.

## Documentation Impact and Self-Review

Affected owners: 03 Features, 04 User Workflows, 05 GUI, 06 System Architecture, 07 Database, 13 Python Architecture, 16 Roadmap, 17 Todo, 18 ChangeLog and this current-state report. Requirements remain valid; ERD, physical schema, folder structure and ROOT require no Slice 020 change.

Self-review: PASS for exact domain validation, bound SELECT predicates, category/status/FTS composition, unchanged MATCH/ranking, no duplicate rows or filtering writes, asynchronous busy/failure behavior, selection/detail reconciliation, create/edit/category/publish/archive continuity, Ticket navigation, native layout, migration preservation and scope control.

Verified limitations: status choices are intentionally fixed to the existing lifecycle domain and are not persisted between launches. Category choices retain the Slice 019 workspace-lifetime cache. Native evidence covers the tested 1000×700 environment and synthetic text, not every DPI/display configuration.

Next gate: independent review of Slice 020. Of the narrow candidates, tag filtering needs explicit multi-tag semantics but fits the established read-only composition path; saved filters additionally require persistence and UX design, and date filtering requires boundary/time-zone decisions. Recommend **specify and implement read-only tag filtering as one later bounded slice**, only after Slice 020 review. No next slice is implemented.

Final Git verification is recorded in the completion report. Work must remain unstaged/uncommitted.
