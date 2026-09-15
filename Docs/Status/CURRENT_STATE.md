# F7Hub Current State

Last verified: 2026-09-15 (America/Toronto)

Branch: `feat/knowledge-tag-assignment`

Base and current HEAD: `5256b6625940e60dbf0641c824ffca48fc99cc62`

Status: PASS — READY FOR INDEPENDENT REVIEW. Slice 021 implementation, focused tests, full regression, database validation and native verification are complete. Work remains unstaged and uncommitted. Independent review is NOT complete; Slice 022 has NOT started.

## Current Milestone

EXISTING GLOBAL TAGS CAN BE MANAGED ATOMICALLY ON DRAFT KNOWLEDGE ARTICLES

## Slice 021 Working Behavior and Boundaries

DRAFT existing-tag assignment/replacement/removal: IMPLEMENTED. Zero, one and multiple global tags are valid; empty removes all. Tags… loads choices/current checks asynchronously, defaults to Cancel, and Escape writes nothing. PUBLISHED and ARCHIVED articles retain readable tags but cannot mutate them.

Tag changes update only `knowledge_article_tags` and `knowledge_articles.updated_at`. Version/content/history, category/status, created/published timestamps, ticket relationships and FTS remain unchanged. Both expected version and expected updated-at tokens reject tag, category and content races. No-op saves write nothing; bridge or token-update failures roll back completely.

Tag creation/admin, PUBLISHED/ARCHIVED tag editing, tag filtering and historical tag reconstruction: NOT IMPLEMENTED. Tags are global under the unchanged current schema. Migration: NONE.

Fresh validation: focused 13 PASS; Database 318 PASS; GUI 123 PASS; Integration 91 PASS; total 532 PASS versus 519 baseline. Native Windows actual MainWindow 1000×700: PASS; six screenshots in `C:\Users\Jo\AppData\Local\Temp\f7-s021-native-12c5730cbfb747f6aaf65e2d3a6c78c5` were opened and inspected. No clipping/important overlap. Migration count 6, integrity_check=ok, zero foreign-key violations, FTS integrity PASS and zero duplicate article/tag pairs.

## Existing Filter Behavior

All statuses, DRAFT, PUBLISHED and ARCHIVED filtering: IMPLEMENTED for normal Knowledge lists and current-article FTS results.

- Status and category are orthogonal. All/specific/Not selected category modes compose with all four status modes.
- Changing either filter during search reruns the last executed query, not unsubmitted text. Clear Search clears text/mode and preserves both filters.
- Replacement requests clear rows and all details before dispatch. Empty/failure states are truthful and retain filters for retry.
- New DRAFT articles reset status/category only when needed to reveal the authoritative uncategorized result.
- Publishing under DRAFT and archiving under PUBLISHED reset Status to All statuses, preserve a compatible category, and reveal the authoritative new state.
- Category mutation and content editing preserve status. Version History remains available for selected DRAFT/PUBLISHED/ARCHIVED records.
- Ticket Open Article clears search and resets Category/Status to All before explicit ID reveal; existing relationships remain unchanged.

Saved filters, tag/date filtering, multi-select/custom statuses, pagination, advanced search, Unpublish and Unarchive: NOT IMPLEMENTED. Existing-tag assignment is implemented but tags are not search or filter input. No migration, schema, index, ranking or lifecycle mutation change.

## Architecture and Queries

TagRepository reads global choices and per-article relationships in case-insensitive name/ID order. KnowledgeService requires explicit KnowledgeRepository, CategoryRepository and TagRepository dependencies; every Python/Test constructor was updated. The service validates positive non-bool IDs, rejects duplicate IDs, produces one strictly advancing UTC metadata token and translates failures safely.

KnowledgeRepository.set_draft_tags owns one BEGIN IMMEDIATE transaction: authoritative article load, DRAFT/version/updated-at validation, submitted-tag existence validation, current-set read, no-op check, differential DELETE/INSERT, conditional updated-at UPDATE by ID/DRAFT/version/token, exact row-count check, authoritative reload and commit. Current record reads resolve tag names exactly without delimiter encoding. ArticleTagsDialog and KnowledgeWorkspace use ServiceTaskRunner and contain no SQL.

## Focused Validation

Environment: existing `.venv/Scripts/python.exe`, PYTHONPATH=Python plus repository root, PYTHONDONTWRITEBYTECODE=1; GUI/Integration use QT_QPA_PLATFORM=offscreen.

Fresh focused Slice 021 run: 13 PASS in 18.842s. It covers global/reference reads, exact replacement and remove-all, duplicate/missing/non-DRAFT validation, no-op, strictly advancing timestamps, tag/content/category races, rollback after bridge and token-update failures, async dialog behavior, stale-detail clearing, filters, lifecycle, ticket navigation and reconstruction.

## Full Sequential Regression

Commands, each run sequentially with the prescribed environment:

```powershell
.venv\Scripts\python.exe -B -m unittest discover -s Tests/Database -p "test_*.py" -v
.venv\Scripts\python.exe -B -m unittest discover -s Tests/GUI -p "test_*.py" -v
.venv\Scripts\python.exe -B -m unittest discover -s Tests/Integration -p "test_*.py" -v
```

| Suite | Result | Duration |
|---|---:|---:|
| Database | 318 PASS | 17.828s |
| GUI | 123 PASS | 80.947s |
| Integration | 91 PASS | 432.985s |

Slice 021 baseline: 311 Database / 119 GUI / 89 Integration = 519. Final total: **532 PASS**, an increase of 13, with zero failures/errors/skips and all three process exits 0.

## Native Windows Evidence

PASS: QT_QPA_PLATFORM=windows, actual MainWindow at 1000×700, isolated synthetic SQLite. Verified zero/one/multiple tags, current preselection, Cancel/Escape, replace/remove/remove-all/final set, Category/Status filters, FTS search, edit persistence, Publish/Archive preservation and disabled mutation, Version History, Ticket Open Article and reconstruction.

Six captures were opened and inspected: zero tags, zero-current selector, multiple preselected, filtered/searched DRAFT V2, PUBLISHED and ticket-open ARCHIVED. The dialog checklist and MainWindow details/actions are readable; no horizontal clipping or important overlap was observed. This is agent verification, not independent review or user acceptance.

Evidence outside the repository:

- `C:\Users\Jo\AppData\Local\Temp\f7-s021-native-12c5730cbfb747f6aaf65e2d3a6c78c5`: six screenshots and synthetic.db.
- `C:\Users\Jo\AppData\Local\Temp\f7-s021-native.py`: native harness.

## Database and Preservation

Six migration files and six records. Database/Migrations/0001–0006, schema owners Docs/08_ERD.md and Docs/09_SQLSchema.md, and ROOT.md have no Slice 021 diff. Native synthetic integrity_check=ok, foreign_key_check=zero rows, external-content FTS integrity-check PASS and zero duplicate article/tag pairs. Foreign keys prove all bridge references valid.

Protected `Docs/10_FolderStructure.md` SHA256 remains `7DE1EAACB0F833AF5B26A29D8DF163E48F3D10765DD4471E325EC54224B9D258`. `Docs/Archive/DocsOLD/00_Vision.md` remains deleted. Neither protected path was edited, staged, restored, stashed or committed. No validation artifacts are in the repository.

## Documentation Impact and Self-Review

Affected owners: 03 Features, 04 User Workflows, 05 GUI, 06 System Architecture, 07 Database, 13 Python Architecture, 16 Roadmap, 17 Todo, 18 ChangeLog and this current-state report. ERD, physical schema and ROOT require no Slice 021 change because the existing global tags and bridge are reused.

Self-review: PASS for global taxonomy semantics, DRAFT-only exact-set mutation, validation/no-op, dual concurrency tokens, tag/category/content races, rollback, timestamp advancement, unchanged version/history/category/status/ticket links/FTS, filter preservation, async GUI, Cancel/Escape, authoritative display, native layout, migration preservation and scope control.

Verified limitations: tag creation/admin, PUBLISHED/ARCHIVED tag editing, tag filtering and historical tag reconstruction are not implemented. Native evidence covers the tested 1000×700 environment and synthetic text, not every DPI/display configuration.

Next gate: independent review of Slice 021. Recommend one next candidate only: **Slice 022 — read-only Knowledge tag filtering**, after precise single-tag/Untagged semantics are approved. Slice 022 is not implemented.

Final Git verification is recorded in the completion report. Work must remain unstaged/uncommitted.
