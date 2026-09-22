# F7Hub Current State

Last verified: 2026-09-22 (America/Toronto)

Branch: `feat/knowledge-filter-reference-refresh`

Base and current HEAD: `d98e12a3faa722ad380c8e426c51def50892a273`

Status: PASS — READY FOR INDEPENDENT SLICE 023 REVIEW. Implementation, focused tests, full regression, database validation and native Windows verification are complete. Work remains unstaged and uncommitted. Independent review is NOT complete.

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

Next gate: independent review of Slice 023. Do not stage, commit, push, merge or begin Slice 024 from this worktree.
