# F7Hub Current State

Last verified: 2026-09-26 (America/Toronto)

Current candidate: Slice 024, `feature/knowledge-any-tag-filter-s024` in isolated `C:\Dev\F7Hub-S024`.

Base and current HEAD: `02733c29f1b9d960383e00844aa8535c830efb52` (`origin/main` at the implementation baseline check).

Status: PASS — READY FOR INDEPENDENT SLICE 024 REVIEW. Implementation, all required automated suites, database read-only/integrity checks and native Windows inspection are complete. The candidate remains unstaged and uncommitted; independent review and integration are NOT complete.

## Slice 024 Result and Scope

Any of two or more selected existing global tags now filters current Knowledge lists and FTS results. The existing All, Untagged and single-tag modes remain. `KnowledgeService.list_articles` and `search_articles` accept an optional `tag_ids` tuple, validate distinct positive non-bool IDs and mutually exclusive tag modes, then pass bound values to the repository's correlated `EXISTS` predicate. Current article reads return both display names and stable tag IDs. Zero selected tags mean All; one uses the prior specific-tag mode. No database write, schema, migration, index, FTS object, tag mutation or dependency was added.

The cached-choice dialog is opened from the existing Tag filter. Cancel or unchanged Apply requests no result. Changed choices use the existing asynchronous article runner. Category/Status composition, last executed search query, unsubmitted input, Clear Search, explicit Ticket Open Article reset and authoritative article/tag reconciliation remain intact. Successful reference refresh retains surviving selected IDs across renames/deletions and coalesces one final reload; failed tag refresh preserves cached choices for retry. Multi-tag AND/expression filtering and restore/revert remain deferred.

## Slice 024 Validation

Environment: `C:\Dev\F7Hub\.venv\Scripts\python.exe`; `PYTHONPATH=$PWD\Python;$PWD` from the isolated worktree. GUI/Integration regression used `QT_QPA_PLATFORM=offscreen`; the native check used `windows`.

| Suite | Command | Result |
|---|---|---|
| Database | `python -m unittest discover -s Tests/Database -p 'test_*.py'` | PASS — 334 tests, exit 0, 22.970s |
| GUI | `python -m unittest discover -s Tests/GUI -p 'test_*.py'` | PASS — 146 tests, exit 0, 132.120s |
| Integration | `python -m unittest discover -s Tests/Integration -p 'test_*.py'` | PASS — 93 tests, exit 0, 239.095s |

Total full regression: **573 PASS**, zero failures. Focused Database, GUI and ticket-flow checks preceded the full suites. The Database tests exercise query-only connections and identical before/after dumps, `PRAGMA integrity_check = ok`, zero foreign-key violations, list/search composition, FTS order and no duplicate rows. GUI/Integration tests exercise Cancel/no-op, zero/one/multiple selection, keyboard input, reference rename/deletion/failure/retry, executed-query preservation, tag mutation and Ticket Open Article reveal. An initial GUI failure exposed tuple lookup through Qt `findData`; matching explicit item data fixed it before the passing full runs. A first native harness attempt lacked a `QApplication` before constructing widgets; the corrected harness passed without a production-code change.

Native Windows: PASS — actual 1000×700 MainWindow, Any of 2 tags, one matching synthetic article, visible Cancel/Apply controls. The [MainWindow capture](C:/Users/Jo/AppData/Local/Temp/f7-s024-native-xoyfxyey/main-any.png) and [dialog capture](C:/Users/Jo/AppData/Local/Temp/f7-s024-native-xoyfxyey/dialog-any.png) were opened and visually inspected: no forced oversize, clipping, overlap, hidden filter control or broken detail view was observed. This verifies the tested Windows environment, not every DPI configuration.

## Slice 024 Delivery Gate

The approved plan was implemented in an isolated worktree because the root checkout was already dirty on `feature/knowledge-any-tag-filter`. That root work is protected and was not copied, edited or staged. Production changes are confined to Knowledge repository/service/workspace and one filter dialog; tests cover Database, GUI and ticket-flow Integration. Affected canonical docs and this report are synchronized; `Docs/09_SQLSchema.md`, ERD, AHK, PowerShell and dependency files are unaffected. Self-review found no remaining blocking defect. The next gate is an independent read-only review of this exact unstaged candidate. No staging, commit, push or integration has begun.

Exact candidate scope: modified `Python/f7hub/{repositories/knowledge_repository.py,services/knowledge_service.py,gui/knowledge_workspace.py}`, `Tests/Database/test_knowledge_tag_filter.py`, `Tests/GUI/test_knowledge_tag_filter.py`, `Tests/Integration/test_ticket_knowledge_flow.py`, `Docs/{03_Features.md,04_UserWorkflows.md,05_GUI.md,07_Database.md,13_PythonArchitecture.md,16_Roadmap.md,17_Todo.md,18_ChangeLog.md,Status/CURRENT_STATE.md}`; new `Python/f7hub/gui/knowledge_tag_filter_dialog.py` and `Tests/GUI/test_knowledge_tag_filter_dialog.py`. No deletions; index empty. The root checkout retains its seven modified and two untracked protected paths.

For the v0.2 skill evaluation after Slices 024–026: the PLAN baseline gate caught the dirty root, live Git history resolved stale status prose, and this full regression cost about 394 seconds of suite runtime. Distinguish a READY design from an implementation baseline blocker in future templates.

---

## Prior Slice 023 handoff snapshot (historical, superseded by the merged baseline)

Last verified: 2026-09-22 (America/Toronto)

Branch: `feat/knowledge-filter-reference-refresh`

Base and current HEAD at that handoff: `d98e12a3faa722ad380c8e426c51def50892a273`

At that handoff: PASS — READY FOR INDEPENDENT SLICE 023 REVIEW. This prior status is retained as historical test evidence. Slice 023 later merged into `main` through PR #22 (`2f3368db45c3067ccfac2fc5c76b41ab9dc8a4c9`).

## Current Milestone

KNOWLEDGE FILTER REFERENCES CAN BE REFRESHED MANUALLY WITHOUT RECONSTRUCTING THE WORKSPACE

## Slice 023 Working Behavior and Boundaries

The compact Knowledge filter row includes an accessible **Refresh filters** control. One activation requests active KNOWLEDGE categories once and global tags once through the existing independent runners. Duplicate activation is disabled until both reads settle, and `filter_loading` keeps existing MainWindow close protection truthful.

Successful sources replace their dynamic choices. Failed sources keep the last successfully loaded options and selection, show safe source-specific feedback and allow retry; one failure does not block the other source. All categories, Not selected, All tags and Untagged remain stable modes. Specific selections reconcile by ID, so renames stay selected with updated labels. Inactive/deleted category selections reset Category only; deleted tag selections reset Tag only.

After both callbacks settle, valid selections cause no article request. One or two unavailable selections cause exactly one authoritative result request using the final controls. Normal mode reloads the filtered list. Active search reruns its last executed query while leaving unsubmitted input untouched. Status and compatible filter dimensions remain selected. No polling, watchers, administration, saved/date filters or multi-tag expressions are implemented.

## Architecture and Database Safety

`KnowledgeWorkspace` reuses `KnowledgeService.list_active_knowledge_categories()`, `KnowledgeService.list_available_tags()`, `_filter_runner`, `_tag_filter_runner`, source feedback labels and the shared list/search runner. `CategoryRepository.list_categories(scope="KNOWLEDGE", active_only=True)` and `TagRepository.list_tags()` remain the only reference queries. MainWindow, services, repositories, domain, AHK and PowerShell are unchanged; no component, dependency, migration, schema, index or FTS change was added.

The refresh path is read-only. An isolated real-SQLite integration test compared complete `iterdump()` output immediately before and after successful, mixed-failure and reset/reload refreshes; every pair was identical. Representative final state returned `PRAGMA integrity_check = ok` and zero `PRAGMA foreign_key_check` rows.

## Validation

Environment: repository `.venv\Scripts\python.exe`, `PYTHONPATH=$PWD\Python;$PWD`; focused/full GUI and Integration automation used `QT_QPA_PLATFORM=offscreen` except the explicit native run.

- Focused Slice 023: **27 PASS** in 132.760s.
- Database regression: **332 PASS** in 17.875s.
- GUI regression: **140 PASS** in 177.985s.
- Integration regression: **92 PASS** in 451.618s.
- Total full regression: **564 PASS**; zero failures, errors or skips; no suite decreased from the supplied 332/128/91 baseline.

Coverage includes control/accessibility/layout, exact service-call counts, both completion orders, additions/renames/deactivation/deletion, all static modes, source-specific and dual failure, cached choices, retry, duplicate prevention, close protection, zero/one final result request, Category/Status/Tag preservation, normal list, last-executed FTS query, unsubmitted text, real external SQLite changes, read-only dumps, integrity and foreign keys. Existing full regression covers Category+Status+Tag filtering, FTS, Clear Search and Ticket Open Article.

## Native Windows Verification

`QT_QPA_PLATFORM=windows`: **6 PASS** in 20.386s using real MainWindow hierarchies and isolated SQLite.

After making the tool button's strong keyboard-focus policy explicit, the two native control/accessibility/layout tests re-passed in 2.914s; the focus-only change did not alter geometry.

An actual MainWindow remained exactly 1000×700 for all six captures in `C:\Users\Jo\AppData\Local\Temp\f7-s023-validation-codex`: idle, busy/disabled, successful updated choices, one-source failure, unavailable category/tag reset, and active-search reconciliation. All captures were opened and manually inspected. The filter row, feedback, table, detail and actions were readable with no forced oversize, clipping, overlap, hidden control, misleading stale filter/result or broken detail view. The search capture and runtime evidence showed `search_active=True`, executed query `DNS`, visible input `unsubmitted text`, reset All category/tag and one matching result. This is agent verification, not user acceptance testing.

## Documentation and Git Safety

Updated owners: 03 Features, 04 User Workflows, 05 GUI, 13 Python Architecture, 16 Roadmap, 17 Todo, 18 ChangeLog and this current-state report. Database architecture, ERD, SQL schema, folder structure, AHK and PowerShell docs are unchanged because their owned behavior did not change. No validation/native artifact is stored in the repository.

## Risks and Next Gate

Verified remaining limitation: choices update only on initial load or explicit Refresh filters; there is no polling/watcher. Native evidence covers the tested 1000×700 Windows environment and synthetic text, not every DPI/display configuration.

At this historical handoff, the next gate was independent review of Slice 023. That candidate was later merged into `main`; the current Slice 024 gate is stated above.
