# F7Hub Current State

Last verified: 2026-09-15 (America/Toronto)

Branch: `feat/knowledge-tag-filter`

Base and current HEAD: `7cc6fe06e854c93d95b8b801c547c2a59c876f11`

Status: PASS — READY FOR INDEPENDENT REVIEW. Slice 022 implementation, focused tests, full regression, database validation and native Windows verification are complete. Work remains unstaged and uncommitted. Independent review is NOT complete.

## Current Milestone

CURRENT KNOWLEDGE ARTICLES SUPPORT READ-ONLY SINGLE-TAG FILTERING

## Slice 022 Working Behavior and Boundaries

Tag filter modes: All tags, Untagged and one specific existing global tag are IMPLEMENTED for normal current-article lists and FTS results. All tags adds no tag predicate. Untagged means zero `knowledge_article_tags` relationships. A specific tag matches any article related to that tag even when other tags are also assigned.

Category, Status and Tag compose independently. Active-search filter changes rerun the last executed query, not unsubmitted input. Clear Search clears text/mode and preserves all three filters. Default All tags behavior equals the prior list/search behavior. Filtering is SELECT-only.

Multi-tag AND/OR, negation, tag expressions, saved/date filters, tag counts, tag FTS indexing, historical tag filtering and tag administration: NOT IMPLEMENTED. PUBLISHED/ARCHIVED tag mutation remains unavailable. Migration: NONE.

## Architecture and Queries

`TagRepository.list_tags()` remains the single global option source in deterministic case-insensitive name/ID order. `KnowledgeService.list_available_tags()` is reused; no filter repository/service or duplicate tag query exists. Service list/search accepts `tag_id` or `untagged_only`, validates positive non-bool IDs, requires a boolean flag and rejects contradictory modes before repository access.

`KnowledgeRepository.list_articles()` and `search_articles()` use correlated `EXISTS` for a specific tag and `NOT EXISTS` for Untagged. The FTS predicate correlates on authoritative `ka.knowledge_article_id`. Multi-tag articles appear once; no direct many-to-many join, `DISTINCT` or `GROUP BY` is used. Normal order remains updated-at descending then ID descending. FTS remains MATCH then bm25, updated-at descending and ID descending. Tags are not added to MATCH or indexed content.

`KnowledgeWorkspace` adds explicit-mode item data for All/Untagged/specific choices and a compact Category/Status/Tag row. Category and tag choices load through independent workspace-owned `ServiceTaskRunner` instances. `filter_loading` reflects either runner so existing MainWindow close protection remains sufficient; MainWindow is unchanged. Static All/Untagged and All/Not selected modes remain usable after their respective reference failure, and the other reference source continues independently.

## State Reconciliation

Normal list and active search replacement clear stale rows/details before dispatch and preserve the current article only as a preference. A tag write that removes active-filter membership reloads the authoritative result set; retaining the selected tag keeps the article eligible. Untagged-to-tagged mutation removes the row truthfully.

New DRAFT articles reset only incompatible Category/Status/Tag dimensions. Untagged is retained for a new untagged article; a specific tag resets to All tags. Content/category mutation preserves a compatible tag filter. Publish and Archive preserve tag relationships and the compatible Tag selection while existing Status reconciliation reveals the new lifecycle state. Ticket Open Article clears search and resets Category, Status and Tag to All before explicit ID reveal; ticket relationships remain unchanged.

Successfully loaded category/tag options are cached for the workspace lifetime. External taxonomy changes require workspace reconstruction/reopen; no polling or live-refresh control is implemented.

## Focused Validation

Environment: existing `.venv\Scripts\python.exe`, `PYTHONPATH=$PWD\Python;$PWD`, `PYTHONDONTWRITEBYTECODE=1`, with GUI/Integration focused tests using `QT_QPA_PLATFORM=offscreen`.

Fresh focused affected set: **158 PASS** in 357.432s. Coverage includes list/FTS matrices, service validation/forwarding, query-only/dump equality, deterministic global options, independent reference failures, busy/close safety, last-executed search, Clear Search, selection/detail reconciliation, tag mutation removal/retention, Untagged mutation, compatible/incompatible creation, lifecycle preservation, Version History, Ticket Open Article and reconstruction.

## Full Sequential Regression

- Database: **323 PASS** in 18.216s.
- GUI: **128 PASS** in 107.371s.
- Integration: **91 PASS** in 429.931s.
- Total: **542 PASS** versus the supplied 532 baseline; zero failures/errors/skips and no suite decrease.

## Native Windows Verification

`QT_QPA_PLATFORM=windows`: **6 PASS** in 35.761s using real MainWindow hierarchies. Covered all/specific/Untagged, Category/Status/Tag composition, FTS and Clear Search, tag mutation removal/retention, new-article reveal, Publish/Archive preservation, Version History, Ticket Open Article reset/reconstruction, independent reference failure and close protection.

An actual MainWindow at exactly 1000×700 used isolated synthetic SQLite. Five captures in `C:\Users\Jo\AppData\Local\Temp\f7-s022-validation-codex` were opened and inspected: All tags, Untagged, VPN, Category+Status+Tag+FTS and Clear Search preserving filters. Controls, table, details and actions were readable with no forced oversize, horizontal clipping, important overlap or status elision. This is agent verification, not user acceptance testing.

## Database Validation

Six migration files and six applied records. `Database/Migrations/0001–0006`, schema owners `Docs/08_ERD.md` and `Docs/09_SQLSchema.md`, and `ROOT.md` have no Slice 022 diff. Fresh isolated validation: `integrity_check=ok`, zero foreign-key violations, FTS integrity PASS, zero duplicate article/tag pairs and zero orphan article/tag bridge references. Query-only trace plus before/after dump equality proves tag-filter list/search operations write nothing.

## Documentation and Git Safety

Updated owners: 03 Features, 04 User Workflows, 05 GUI, 06 System Architecture, 07 Database, 13 Python Architecture, 16 Roadmap, 17 Todo, 18 ChangeLog and this current-state report. Product requirements already authorize tag filtering and need no behavioral change. ERD, physical schema, folder-structure owner and ROOT require no Slice 022 update.

Protected user work remains present and unstaged: modified `Docs/10_FolderStructure.md` (SHA-256 `7DE1EAACB0F833AF5B26A29D8DF163E48F3D10765DD4471E325EC54224B9D258`) and deleted `Docs/Archive/DocsOLD/00_Vision.md`. Neither was edited, restored, staged, stashed, reset, cleaned or committed. ROOT working hash matches HEAD blob `77e6b012d15e30e05cd4148cce15dbf6bea6fc54`. No validation/native artifact is stored in the repository.

## Risks and Next Gate

Verified limitation: filter option lists are workspace-lifetime snapshots, so external category/tag additions or deletions do not appear until reconstruction/reopen. Native evidence covers the tested 1000×700 Windows environment and synthetic text, not every DPI/display configuration.

Next gate: independent review of Slice 022. Recommended next candidate only: **manual Knowledge filter-reference refresh**, independently reloading category and tag choices while preserving valid selections and resetting only unavailable selections. Do not add polling, administration, saved filters or multi-tag expressions in that slice.
