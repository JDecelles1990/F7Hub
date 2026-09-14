# F7Hub Current State

Last verified: 2026-09-14 (America/Toronto)

Branch: `feat/knowledge-archive-published`

Base and current HEAD: `1f8b418d8a4718ddfe56b0aefcda23e05689ed17`

Status: PASS — Slice 017 implemented and validated; ready for independent review. Work remains unstaged and uncommitted. Independent Slice 017 review is NOT complete. Slice 018 was NOT started.

## Current Milestone

ONE PUBLISHED ARTICLE CAN BE ARCHIVED WITH PUBLICATION AND CONTENT HISTORY PRESERVED

## Working Behavior and Boundaries

Knowledge Base → open PUBLISHED article → Archive → explicit confirmation → ARCHIVED. Archive is enabled only with an available service, idle runner and loaded PUBLISHED article. PlainText confirmation identifies code/title and explains preserved content, Version History and existing ticket links, and unavailable Unarchive. Cancel is default and Escape; Enter respects the default. All three cancellation paths were verified with zero archive calls/writes.

KnowledgeWorkspace retains the reviewed article/version across the modal event loop. Reentry, changed article context and busy state cannot submit an unintended archive. ServiceTaskRunner executes asynchronously; real MainWindow coverage verifies competing controls are disabled. Success refreshes the normal list, reselects the same article and reloads authoritative ARCHIVED details. Edit/Publish/Archive disable; Version History remains enabled. Failures preserve the displayed article without a false ARCHIVED mutation; stale feedback requires reopening the latest version.

Publish and DRAFT → PUBLISHED: IMPLEMENTED. Archive PUBLISHED and PUBLISHED → ARCHIVED: IMPLEMENTED. DRAFT → ARCHIVED, Unarchive and Unpublish: NOT IMPLEMENTED.

## Archive Persistence Contract

`KnowledgeWorkspace → KnowledgeService.archive_article → KnowledgeRepository.archive_published_article → SQLite` reuses the existing layers. The service validates positive integer ID/version values, rejects bool, generates one UTC timestamp and translates missing/non-PUBLISHED/stale/persistence errors into safe messages.

One BEGIN IMMEDIATE transaction loads authoritative state, validates existence/PUBLISHED/expected version, executes a parameterized conditional UPDATE by ID/PUBLISHED/version, requires rowcount==1, reloads and commits. Only status and updated_at change. published_at is never assigned during archive. Post-update reload failure rolls back; zero-row updates reject safely. Tests compare complete database dumps on rollback, including existing ticket links.

| Field or relationship | Archive result |
|---|---|
| status | PUBLISHED → ARCHIVED |
| updated_at | One archive UTC timestamp |
| published_at | Original publication timestamp preserved |
| version_number | Unchanged; V2 stays V2 |
| Content, identity, category, created_at | Unchanged |
| Version History | V2/V1 unchanged; no V3 or new snapshot |
| Ticket RELATED row | Preserved exactly |

Native example: published_at before and after = `2026-09-14T18:50:51.061Z`; archived updated_at = `2026-09-14T18:50:52.926Z`. Version remained 2. Existing published-at and archived state survived application reconstruction.

## Search, History and Ticket Continuity

Migration 0006 indexes content fields only. Archive makes no explicit FTS update or reindex; search joins authoritative relational status and returns one ARCHIVED result for the same content. Historical snapshots are unchanged. Ticket metadata shows ARCHIVED; Open Article loads the authoritative archived current article. Version History stays available after archive and search.

## Validation Executed in This Session

Environment:

```powershell
$env:PYTHONPATH="$PWD\Python;$PWD"
$env:PYTHONDONTWRITEBYTECODE='1'
$env:QT_QPA_PLATFORM='offscreen'
```

Completed focused runs (their complete summaries were rechecked after the continuation request):

```powershell
.\.venv\Scripts\python.exe -B -m unittest Tests.Database.test_knowledge_repository Tests.Database.test_knowledge_service Tests.GUI.test_knowledge_workspace -v
.\.venv\Scripts\python.exe -B -m unittest Tests.Integration.test_knowledge_base_flow -v
.\.venv\Scripts\python.exe -B -c "import faulthandler, unittest; faulthandler.dump_traceback_later(45); unittest.main(module=None, argv=['unittest', 'Tests.Integration.test_ticket_knowledge_flow', '-v'])"
.\.venv\Scripts\python.exe -B -m unittest Tests.Integration.test_ticket_knowledge_flow.TicketKnowledgeFlowTests.test_archive_busy_in_real_main_window_blocks_competing_actions Tests.Integration.test_ticket_knowledge_flow.TicketKnowledgeFlowTests.test_archive_v2_preserves_publication_history_search_link_and_reconstruction -v
```

- Repository: 31 PASS; service: 18 PASS; Knowledge GUI: 33 PASS — combined 82, 13.625s.
- Knowledge Base integration: 16 PASS, 99.168s.
- Ticket-Knowledge integration: 23 PASS, 80.258s, before adding the final busy-state test.
- Final real-window busy-state and deterministic V2 archive flow: 2 PASS, 14.190s. The V2 flow is repeated coverage, not two additional unique tests.
- Initial focused run: 81 PASS/1 FAIL; the new confirmation-copy test caught a missing explanation. Corrected before the completed focused and full runs.
- Initial combined integration run was interrupted without a complete summary and is not counted as PASS. Separate completed runs supersede it. The diagnostic 45-second traceback in the ticket run was a progress snapshot, not a test failure; the run completed with OK.

Full regression executed sequentially (Database → GUI → Integration), using the actual existing `.venv` interpreter:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s Tests/Database -p "test_*.py" -v
.\.venv\Scripts\python.exe -B -m unittest discover -s Tests/GUI -p "test_*.py" -v
.\.venv\Scripts\python.exe -B -m unittest discover -s Tests/Integration -p "test_*.py" -v
```

| Suite | Result | Duration | Failures | Errors | Skips | Exit |
|---|---:|---:|---:|---:|---:|---:|
| Database | 280 PASS | 40.521s | 0 | 0 | 0 | 0 |
| GUI | 95 PASS | 11.590s | 0 | 0 | 0 | 0 |
| Integration | 84 PASS | 358.649s | 0 | 0 | 0 | 0 |

Total: **459 PASS**. User-specified baseline: 441 (271/90/80). Increase: 18 tests (9/5/4); no suite decreased. All three final summaries and successful sequential-process completion were captured. Product/test code was unchanged after this full regression; subsequent edits only complete documentation.

## Native Windows Evidence

PASS in this session with Qt platform `windows`, isolated synthetic SQLite and MainWindow 1000×700. The script exercised create DRAFT, edit V2, publish, Archive enablement, Cancel/default Enter/Escape with zero archive calls/writes, confirm archive, disabled Edit/Publish/Archive, enabled Version History, V2/V1 contents, search, linked-ticket status/Open Article and application reconstruction.

All 14 PNG captures were actually inspected: draft, publication confirmation, published details, three archive cancellation confirmations, cancelled published state, accepted archive confirmation, archived details, history, search, ticket relationship, ticket Open Article and reconstructed application. Action/status text fits without overlap or clipping; HTML-like title text remains literal. Existing table-title ellipsis remains. This is native Qt input and visual agent verification, not independent review or user acceptance testing.

Evidence folder: `C:\Users\Jo\AppData\Local\Temp\f7hub-slice017-validation`. It contains focused/full logs, native.py, native.log, the isolated native database and 14 screenshots. These are outside the repository.

## Database and Preservation Checks

- Exactly six migration files; 0001–0006 match HEAD using Git-normalized blob hashes. No 0007 or schema modification.
- Synthetic schema object identity unchanged; no archived_at field, audit table, content snapshot or FTS rewrite.
- PRAGMA integrity_check: ok; PRAGMA foreign_key_check: zero rows; external-content FTS integrity-check with rank=1: PASS.
- Docs/08_ERD.md, Docs/09_SQLSchema.md and ROOT.md unchanged.
- Protected Docs/10 SHA256 remains `7DE1EAACB0F833AF5B26A29D8DF163E48F3D10765DD4471E325EC54224B9D258`.
- ROOT SHA256 remains `1E7E493B7C66BFE90D132EE972726FE77A4F4D6B1C2F75B2D10FF888250969F3`.
- Protected `Docs/Archive/DocsOLD/00_Vision.md` deletion remains untouched.
- No untracked validation artifacts. Existing ignored __pycache__ directories predate this work; no new bytecode was generated by these runs.
- git diff --check: PASS. No staging, commit, push, merge or dependency changes.

## Documentation Impact

Updated: Docs/03 Features, 04 Workflows, 05 GUI, 06 System Architecture, 07 Database, 13 Python Architecture, 16 Roadmap, 17 Todo, 18 ChangeLog and this status file. Requirements (02) already cover lifecycle/archive intent and need no rewrite. Documentation Index (19) routing is unchanged. ERD (08), SQL Schema (09) and ROOT need no change because structure/schema/launch behavior is unchanged.

## Limitations and Next Gate

Unarchive, Unpublish, DRAFT archive, restore/revert, historical editing/deletion, archive reasons, actors, bulk/scheduled lifecycle, permissions and AI are outside this slice. Archive records current lifecycle metadata without a lifecycle audit history. Archiving from search returns to the normal list; search-state preservation is not implemented. Other screen sizes/DPI, assistive technology and user-library scale are NOT VERIFIED.

Stop for independent Slice 017 review. Do not stage, commit, push or merge. Slice 018 is NOT started. Recommendation only: Unarchive one ARCHIVED article to PUBLISHED with explicit confirmation and preserved content/history, a narrower metadata operation than reopening editing through Unpublish or adding content revisions through restore/revert.
