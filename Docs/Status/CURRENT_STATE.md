# F7Hub Current State

Last verified: 2026-09-09 (America/Toronto)

Branch: `feat/knowledge-publish-draft`

Base HEAD: `426341c5d82a0ccc0bcc060829096cfc0294e8af`

Status: PASS — Slice 016 implemented and verified, ready for independent review. Work is unstaged and uncommitted. Protected `Docs/10_FolderStructure.md` modification and `Docs/Archive/DocsOLD/00_Vision.md` deletion remain preserved; `ROOT.md` is unchanged.

## Current Milestone

ONE REVIEWED DRAFT CAN BE PUBLISHED WITHOUT CHANGING CONTENT HISTORY

## Working

- SQLite bootstrap and six ordered migrations through `0006_knowledge_search.sql`
- Existing ticket creation, quick company/contact, saved tickets, notes/status and reference workflows
- Knowledge create/list/read, DRAFT content editing, immutable Version History and current-article FTS5 search
- RELATED ticket/article Link, Open, Unlink and Relink
- Publish one loaded DRAFT through explicit plain-text confirmation identifying article code/title
- Cancel as default, Enter without changed selection and Escape; zero service calls, writes or refresh on Cancel
- Async Publish with the loaded expected-version token; busy policy blocks duplicate and competing actions
- DRAFT → PUBLISHED with matching UTC published_at/updated_at; authoritative current/list refresh and same-article selection
- Edit/Publish disabled after publication; Version History, current-content search and ticket Open Article remain available

## Publish Contract

`KnowledgeWorkspace → KnowledgeService.publish_article → KnowledgeRepository.publish_draft_article → SQLite` reuses the existing layers and ServiceTaskRunner. The service validates positive integer ID/version inputs (rejecting bool), generates one UTC timestamp and translates typed missing/non-DRAFT/stale errors plus persistence failures into safe feedback.

One BEGIN IMMEDIATE transaction loads authoritative state, checks existence/DRAFT/expected version, conditionally updates by article ID/DRAFT/version, checks exactly one affected row, reloads and commits. Only status, published_at and updated_at change. Content/version/category/identity/creation metadata/history/relationships remain unchanged. Injected post-update reload failure rolls back; a zero-row update rejects safely.

Publish: IMPLEMENTED. DRAFT → PUBLISHED: IMPLEMENTED. published_at: IMPLEMENTED. Content revision on publish: NO. Version increment on publish: NO. Unpublish: NOT IMPLEMENTED. Archive: NOT IMPLEMENTED.

Publication of a stale V1 after another editor creates V2 is rejected; current state remains DRAFT V2 with NULL published_at and exactly V2/V1 history. Already-PUBLISHED and ARCHIVED articles reject publication without timestamp overwrite. No optimistic GUI status change occurs before success.

## Search / History / Relationships

Migration 0006 is unchanged. Its FTS update trigger covers only article_code/title/summary/body_markdown, so lifecycle metadata does not require reindexing. Search joins the relational row for current status; the same query returns one PUBLISHED result after publication. Historical snapshots remain separate and unchanged. Ticket RELATED rows survive exact value comparison, linked metadata shows PUBLISHED, and Open Article navigates to the current article. Application reconstruction preserves published_at and PUBLISHED status.

## Validation

Fresh focused commands, with `PYTHONPATH=$PWD\Python;$PWD`, `PYTHONDONTWRITEBYTECODE=1` and `QT_QPA_PLATFORM=offscreen`:

```powershell
.\.venv\Scripts\python.exe -B -m unittest Tests.Database.test_knowledge_repository Tests.Database.test_knowledge_service Tests.GUI.test_knowledge_workspace -v
.\.venv\Scripts\python.exe -B -m unittest Tests.Integration.test_ticket_knowledge_flow Tests.Integration.test_knowledge_base_flow -v
```

- Repository 25, service 15 and Knowledge GUI 28: combined 68 PASS, 7.378s.
- Knowledge Integration 16 and ticket-link Integration 20: combined 36 PASS, 170.012s.
- Initial new integration assertion used `status` instead of the existing `article_status`; corrected test and final focused rerun passed.

Final regression runs sequentially, using the same environment:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s Tests/Database -p "test_*.py" -v
.\.venv\Scripts\python.exe -B -m unittest discover -s Tests/GUI -p "test_*.py" -v
.\.venv\Scripts\python.exe -B -m unittest discover -s Tests/Integration -p "test_*.py" -v
```

| Suite | Result | Duration | Exit |
|---|---:|---:|---:|
| Database | 271 PASS | 13.481s | 0 |
| GUI | 90 PASS | 10.849s | 0 |
| Integration | 80 PASS | 314.166s | 0 |

Pre-slice baseline: 424 (262 Database, 85 GUI, 77 Integration). Final total: **441 PASS**, an increase of 17 tests (9 Database, 5 GUI, 3 Integration); no suite decreased. Product and test code did not change after the focused runs and before/after final regression.

## Native Windows Evidence

PASS with Qt platform `windows`, isolated synthetic SQLite and MainWindow 1000×700. Native Qt input checks covered creation/load, Publish enabled, explicit confirmation, Cancel with unchanged DRAFT/NULL published_at, V2 publication, PUBLISHED status, Edit/Publish disabled, history V2/V1, search/current PUBLISHED result, ticket link/Open Article and application reconstruction. SQLite and FTS integrity, six migrations and unchanged schema objects also passed.

All nine captured images were actually inspected: draft, Cancel confirmation, cancelled draft, Publish confirmation, PUBLISHED details, history, published search, linked ticket and ticket Open Article. Actions and lifecycle status fit without clipping/overlap; confirmation is readable and HTML-like article text remains literal. Existing table-title ellipsis remains. This is agent verification, not user acceptance testing.

Evidence folder: `C:\Users\Jo\AppData\Local\Temp\f7hub-slice016-validation`. It contains native.py, native.log, native-synthetic.db, nine PNG captures and focused/full regression logs. No evidence artifacts are placed in the repository.

## Database Evidence

- Migration count: 6; no 0007, no schema objects added or changed by publication.
- Historical migrations 0001–0006 unchanged; compare against base HEAD and initial file hashes.
- PRAGMA integrity_check: ok.
- PRAGMA foreign_key_check: zero rows.
- FTS external-content integrity-check with rank=1: PASS.
- Publication preserves both current content revisions and exact RELATED rows; rollback preserves the full synthetic database dump.

## Limitations / Deferred

- Unpublish, Archive, bulk/scheduled publish, approvals, permissions, publication actors/notes and notifications are NOT IMPLEMENTED.
- Publication is lifecycle metadata, with no historical status reconstruction, new content version or audit subsystem.
- Published articles cannot be edited in the current workflow.
- Publishing from search returns to the normal list; search-state preservation is intentionally outside this slice.
- Historical search, restore/revert, categories/tags, richer relationships, unified search and AI remain deferred.
- Actual user-library scale, other screen sizes/DPI and assistive-technology coverage are NOT VERIFIED.

## Documentation / Protected Work

Updated owner documents: 03 Features, 04 Workflows, 05 GUI, 06 System Architecture, 07 Database, 13 Python Architecture, 16 Roadmap, 17 Todo, 18 ChangeLog and this status file. Product requirements were inspected; the bounded user-approved publication contract needs no requirements rewrite. 08 ERD, 09 SQL Schema and ROOT remain unchanged. Protected Docs/10 content and the archive deletion are retained exactly.

## Next Gate / Candidate

Stop for independent Slice 016 review. Final sequential regression, native capture inspection, self-review and Git preservation checks passed. Do not stage, commit, push or merge.

Recommend one next bounded candidate: archive one PUBLISHED Knowledge article with explicit confirmation and preserved content/history/links. Compared with unpublish (which reopens editing) and restore/revert (which creates a content revision), this can remain a narrow lifecycle-metadata transition. Recommendation only; Slice 017 is not started.
