# F7Hub Current State

Last verified: 2026-09-15 (America/Toronto)

Branch: `feat/knowledge-category-filter`

Base and current HEAD: `223b54ab1658a448dea37dcb3d9c88987aa8ca28`

Status: PASS — READY FOR INDEPENDENT REVIEW. Slice 019 implementation, focused tests, full regression and native verification are complete. Work remains unstaged and uncommitted. Independent review is NOT complete. Slice 020 has NOT started.

## Current Milestone

READ-ONLY KNOWLEDGE CATEGORY FILTERING FOR CURRENT LISTS AND FTS SEARCH

## Working Behavior and Boundaries

Category filtering, All categories, Not selected, active KNOWLEDGE category filter, category + FTS search, and Clear Search preserving category: IMPLEMENTED.

- All categories imposes no category restriction: categorized, uncategorized and inactive assigned categories remain visible across DRAFT/PUBLISHED/ARCHIVED.
- Not selected means category_id IS NULL.
- A specific category means exact category_id equality. Selector options come only from active KNOWLEDGE rows in existing CategoryRepository order.
- Search and category are independent. Changing category in search mode reruns the executed query. Clear Search clears text/mode and reloads the same category's normal list.
- Category names remain readable in details, including inactive assignments. Inactive categories are omitted from filter choices.

Category administration, status filtering, tags/filtering, saved filters, hierarchy browsing, pagination and PUBLISHED/ARCHIVED category mutation: NOT IMPLEMENTED. No migration, schema change, category indexing or ranking redesign.

## Architecture and Queries

KnowledgeRepository.list_articles/search_articles and KnowledgeService expose keyword-only category_id=None and uncategorized_only=False. Service validation rejects bool/noninteger/nonpositive IDs, nonboolean flags and contradictory modes. Category values stay parameterized. Only internal constant SQL predicates are composed.

List ordering remains updated_at DESC / knowledge_article_id DESC. Search adds the relational predicate on ka.category_id alongside MATCH and retains bm25 / updated_at DESC / ID DESC. Literal query generation, indexed fields, search result records and FTS triggers are unchanged. Filtering performs SELECT only; full database dump comparison and query_only connections verify no stored changes.

CategoryRepository remains the shared reference reader via KnowledgeService.list_active_knowledge_categories. No new repository/service/subsystem/dependency is introduced. Normal operations use the shared ServiceTaskRunner. A separate workspace-owned ServiceTaskRunner reads filter options without blocking article browsing; MainWindow also checks this worker before closing.

## State and Failure Reconciliation

- Default All list loads independently of category choices. Signal-blocked population issues no duplicate article request.
- Reference failure keeps All list/search and current detail usable, disables the selector and shows separate safe feedback. Later list refresh or reopening Knowledge Base retries. Successfully loaded choices are retained for the workspace lifetime.
- List/search replacement clears old rows and all details before dispatch. Failed requests preserve category/query and safe feedback without stale results.
- Filter changes preserve the selected article when present, otherwise select the first result or show a truthful empty state. Selection preference does not generate a false missing-article message.
- Successful Category… writes reconcile filtered list/search; a moved article disappears without optimistic mutation. The selected filter remains unchanged.
- New articles outside a specific filter reveal under All. Edit/Publish/Archive preserve a compatible category filter and use the existing return-to-normal-list behavior.
- Ticket Open Article clears search and resets All before explicit ID reveal. Existing relationships are unchanged.

## Focused Validation

Environment: existing `.venv/Scripts/python.exe`, PYTHONPATH=Python plus repository root, PYTHONDONTWRITEBYTECODE=1; GUI/Integration use QT_QPA_PLATFORM=offscreen.

| Command after `python.exe -B -m unittest` | Result | Duration |
|---|---:|---:|
| `Tests.Database.test_knowledge_category_filter Tests.Database.test_knowledge_search Tests.Database.test_knowledge_service -q` | 35 PASS | 2.923s |
| `Tests.Database.test_knowledge_repository Tests.Database.test_knowledge_categories -q` | 45 PASS | 2.919s |
| `Tests.GUI.test_knowledge_category_filter Tests.GUI.test_knowledge_workspace Tests.GUI.test_article_category_dialog Tests.GUI.test_ticket_knowledge_widget -q` | 73 PASS | 46.262s |
| `Tests.GUI.test_knowledge_category_filter -q` after selection-preference cleanup | 9 PASS | 33.632s |
| `Tests.Integration.test_knowledge_base_flow Tests.Integration.test_ticket_knowledge_flow -q` | 44 PASS | 232.539s |

Focused runs passed with no failures/errors/skips. An auxiliary schema-comparison command initially failed to import f7hub because PYTHONPATH was set inside a pipeline; setting the environment before launching Python corrected that command, and the comparison passed. This was not a test-suite failure. Repeated GUI tests are not additional unique tests.

## Full Sequential Regression

Commands, each in a separate sequential process:

```powershell
$env:PYTHONPATH="$PWD\Python;$PWD"
$env:PYTHONDONTWRITEBYTECODE='1'
$env:QT_QPA_PLATFORM='offscreen'
.venv\Scripts\python.exe -B -m unittest discover -s Tests/Database -p "test_*.py" -v
.venv\Scripts\python.exe -B -m unittest discover -s Tests/GUI -p "test_*.py" -v
.venv\Scripts\python.exe -B -m unittest discover -s Tests/Integration -p "test_*.py" -v
```

| Suite | Result | Duration |
|---|---:|---:|
| Database | 304 PASS | 15.064s |
| GUI | 113 PASS | 47.018s |
| Integration | 88 PASS | 400.029s |

Baseline supplied by user: 294 Database / 104 GUI / 86 Integration = 484. New tests: 10 Database, 9 GUI, 2 Integration. Final total: **505 PASS**, zero failures/errors/skips, all three process exits 0. Increase: 21 tests; no suite decreased. No production/test changes during the full regression run; only documentation edits follow.

## Native Windows Evidence

PASS: QT_QPA_PLATFORM=windows, actual MainWindow at 1000×700, isolated synthetic SQLite. Networking, Microsoft 365 and uncategorized articles share searchable DNS text. Verified All, Not selected, specific list, search within category, Clear Search preserving category, filter change during search, current detail/category display, Category… move reconciliation, edit, Publish, Archive, Version History and actual Ticket panel Open Article reset/reveal.

Six captures were opened and inspected: 01-all, 02-not-selected, 03-networking-search, 04-category-reconciled, 05-archived-filter-search and 06-ticket-open-revealed. No horizontal control clipping or important overlap observed. Native function checks used Qt input events and programmatic selector values; this is agent verification, not independent review or user acceptance.

Evidence outside repository:

- `C:\Users\Jo\AppData\Local\Temp\f7-s019-native-9lqs2105`: six screenshots, synthetic.db and integrity-preservation.json.
- `C:\Users\Jo\AppData\Local\Temp\f7-s019-native.py`: native harness.
- `C:\Users\Jo\AppData\Local\Temp\f7-s019-focused-gui.log` and `f7-s019-focused-integration.log`.
- `C:\Users\Jo\AppData\Local\Temp\f7-s019-full-Database.log`, `f7-s019-full-GUI.log`, `f7-s019-full-Integration.log`.

## Database and Preservation

Six migration files and records; Git-normalized 0001–0006 blobs match HEAD. No 0007 or schema change; schema also matches a freshly bootstrapped six-migration reference. Native synthetic integrity_check=ok; foreign_key_check=zero rows; external-content FTS integrity-check with rank=1 passes. Filtering preserves complete database dumps and succeeds under query_only protection.

Docs/10_FolderStructure.md SHA256 remains 7DE1EAACB0F833AF5B26A29D8DF163E48F3D10765DD4471E325EC54224B9D258. Docs/Archive/DocsOLD/00_Vision.md remains deleted. Neither protected path was edited/staged/restored/stashed/committed. ROOT.md, Docs/08_ERD.md and Docs/09_SQLSchema.md have no diff. No validation artifacts are in the repository.

## Documentation Impact and Self-Review

Affected owners: 03 Features, 04 User Workflows, 05 GUI, 06 System Architecture, 07 Database, 13 Python Architecture, 16 Roadmap, 17 Todo, 18 ChangeLog and this current-state report. Requirements remain valid; ERD, physical schema and ROOT require no change.

Self-review: PASS for three-mode validation, parameterized SELECTs, no lifecycle restrictions, unchanged FTS ranking/content, independent references and safe retry, selection/detail reconciliation, new-article reveal, category mutation, lifecycle continuity, Ticket navigation, native layout and scope preservation.

Limitations: successful filter choices are cached for the workspace lifetime; external taxonomy changes require reconstructing the workspace. Native evidence covers the tested 1000×700 environment and synthetic text, not every DPI or display configuration.

Next gate: independent review of Slice 019. Compare one narrow candidate, read-only status filtering, with saved filters requiring persistence/UX design. Recommend status filtering only after review. It is NOT IMPLEMENTED; no Slice 020 work is started.

Final Git verification: feature branch and baseline HEAD retained; no staged paths or commit. git diff --check: PASS (exit 0). Nineteen Slice paths: four production files, five test files and ten documentation files. Two new test files; no Slice deletions. The two protected changes are excluded from these totals.
