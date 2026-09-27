# F7Hub Current State

Last verified: 2026-09-27 (America/Toronto).

Current candidate: **Slice 030 — Edit a Saved Ticket Subject**, on `feature/ticket-subject-edit-s030` in `C:\Dev\F7Hub`. Approved base and branch HEAD are `cdd49fac734d6bedfecf58aacfea4846b8a6e79d`, equal to fetched `origin/main` at the implementation baseline gate. The checkout, index and untracked set were initially clean. The protected `recovery/pre-s024-protected-work` branch remains at `002a494735f30e1488f61e21ea98740ae6371d4d` and was not modified.

Status: **PASS — READY_FOR_REVIEW after correction**, with independent read-only rereview pending. The first independent review found a post-commit queue-refresh feedback defect; the previous review decision is invalidated by this correction. Authorization covered the bounded correction, testing and documentation only. The candidate remains unstaged and uncommitted; no push, PR or integration was performed. The prior Slice 029 Todo/current-state claim that rereview was pending is **STALE HANDOFF METADATA**: live `main` includes its PR #30 merge at `cdd49fa`. The previous report below is retained as a historical handoff snapshot.

## Slice 030 Result and Scope

`TicketService.update_ticket_subject(ticket_id, *, expected_subject, expected_updated_at, subject)` validates the loaded subject and exact update timestamp inside the existing repository writer transaction before deciding no-op. A real change trims required text, uses a bound guarded UPDATE for only subject and a strictly later UTC activity timestamp, creates exactly one `SUBJECT_CHANGED` timeline event without either subject value, and reloads the authoritative row before commit. Missing/stale state and invalid input create no event; update, event or reload failure rolls back. The correction is permitted in every ticket status. The Save dialog is prefilled, keeps entered text on failure, blocks duplicate submission and close during a write, and asks for a reload after conflict. Successful commit reuses the existing detail and queue reload path. The review correction preserves **Subject saved** and Refresh retry guidance for every post-commit queue failure, including `TicketValidationError`, without changing ordinary queue-read feedback; a later detail read failure still acknowledges the save and offers Reload ticket. Notes/status drafts remain intact. No schema, migration, index, dependency, description edit, other ticket edit, search or Knowledge change is included.

## Slice 030 Fresh Validation

Environment: repository `.venv\Scripts\python.exe -B`, `PYTHONPATH=$PWD\Python;$PWD` from `C:\Dev\F7Hub`. Automated GUI/Integration ran with `QT_QPA_PLATFORM=offscreen`; native validation used `windows` with isolated synthetic SQLite.

| Suite | Command | Final-candidate result |
|---|---|---|
| Focused ticket reads/workspace | `python -B -m unittest Tests.Database.test_ticket_reads Tests.Integration.test_ticket_workspace_flow` | PASS — 34 tests, exit 0 |
| Affected ticket set | `python -B -m unittest Tests.Database.test_ticket_reads Tests.Database.test_ticket_service Tests.Database.test_ticket_repository Tests.GUI.test_main_window Tests.Integration.test_ticket_workspace_flow` | PASS — 50 tests, exit 0 |
| Database | `python -B -m unittest discover -s Tests\Database -p 'test_*.py'` | PASS — 345 tests, exit 0 |
| GUI | `python -B -m unittest discover -s Tests\GUI -p 'test_*.py'` | PASS — 153 tests, exit 0 |
| Integration | `python -B -m unittest discover -s Tests\Integration -p 'test_*.py'` | PASS — 107 tests, exit 0 |

Full regression: **605 PASS**, zero failures/errors; focused and affected tests overlap the full suites. Real SQLite tests cover normalization, no-op and stale-before-no-op validation, missing ticket, closed-ticket correction, same-millisecond timestamp advancement, one text-free event, rollback for update/event/reload failure, unrelated field/note/relationship preservation, `integrity_check = ok` and zero foreign-key violations. Integration covers Cancel, retained input, stale feedback, duplicate/busy protection, detail and queue refresh, and committed-save feedback after either later read fails. The corrected test covers RuntimeError, TicketValidationError and TicketReadError queue failures after commit, verifies one update per edit and no duplicate on Refresh, and checks that an ordinary queue validation error keeps its prior behavior. Expected error-path log messages had successful unittest outcomes and exit 0.

Native Windows: PASS — actual `windows` Qt platform with the MainWindow at 1000×700, after observable worker idle. A persisted ticket was opened and its prefilled subject corrected. A simulated validation failure after commit left the new detail visible and the old queue row available. The [post-commit failure capture](C:/Users/Jo/AppData/Local/Temp/f7-s030-correction-refresh-failed.png) and [recovered queue capture](C:/Users/Jo/AppData/Local/Temp/f7-s030-correction-refresh-recovered.png) were opened and inspected: saved acknowledgment, refresh failure, retry guidance and controls were readable without observed overlap. Refresh then loaded the committed subject into the queue. This verifies the tested Windows environment, not every display scale.

## Slice 030 Delivery Gate

The independent review's one blocking post-commit feedback finding has been corrected and self-validated; independent rereview remains required. Production scope is the ticket repository, service, saved-ticket workspace and one focused dialog; tests are the ticket read and workspace flow files. Affected canonical owners are Features, User Workflows, GUI, Database architecture, Python architecture, Roadmap, Todo, ChangeLog and this status report. Product requirement FR-TICKET-003 remains broader than this first edit slice. Physical SQL Schema, ERD, system architecture, AHK and PowerShell owners have no behavioral change. No independent approval has been granted. The next gate is independent read-only rereview of the exact unstaged candidate; implementation evidence does not authorize staging or integration.

Exact candidate scope: modified `Python/f7hub/repositories/ticket_repository.py`, `Python/f7hub/services/ticket_service.py`, `Python/f7hub/gui/ticket_workspace.py`, `Tests/Database/test_ticket_reads.py`, `Tests/Integration/test_ticket_workspace_flow.py`, `Docs/03_Features.md`, `Docs/04_UserWorkflows.md`, `Docs/05_GUI.md`, `Docs/07_Database.md`, `Docs/13_PythonArchitecture.md`, `Docs/16_Roadmap.md`, `Docs/17_Todo.md`, `Docs/18_ChangeLog.md` and this file; created untracked `Python/f7hub/gui/edit_ticket_subject_dialog.py`. No staged or deleted paths. The bounded review correction changed only the workspace callback, integration coverage, Todo, ChangeLog and this status report. Focused and affected tests were run before the three full suites; documentation changed afterward without changes to code, tests, schema, configuration or dependencies. Native captures were taken after the final code and test bytes stabilized.

---

## Prior Slice 029 handoff snapshot (historical; Slice 029 later merged through PR #30)

Last verified: 2026-09-27 (America/Toronto).

Current candidate: **Slice 029 — Filter Saved Tickets by Type**, `feature/ticket-type-filter-s029` in `C:\Dev\F7Hub`. Approved base and branch HEAD: `1b66f3e888ab24eb1b1fefde2d74e3f60ebba84b`, equal to freshly fetched `origin/main` at the implementation baseline gate. Tracked, staged and untracked state was initially clean. The protected `recovery/pre-s024-protected-work` branch remains at `002a494735f30e1488f61e21ea98740ae6371d4d` and was not modified.

Status: **PASS — READY_FOR_REVIEW after correction**. The first independent review required removing the Type selector's duplicated ticket-type list. That review decision no longer applies to the corrected candidate; independent rereview is pending. Authorization covers correction, testing and documentation only. Candidate changes remain unstaged and uncommitted. No push, PR or integration was performed for Slice 029. Earlier text below describing Slice 028 as awaiting review is **STALE HANDOFF METADATA**: live Git shows Slice 028 merged through PR #29 at `1b66f3e`; that text is retained as a historical candidate snapshot.

## Slice 029 Result and Scope

Saved Tickets adds Type below Priority: All types, Incident, Service request, Problem and Task. All types passes `ticket_type=None`. After review correction, the selector iterates the existing `TICKET_TYPES` vocabulary directly in its established display order; labels are presentation-only. `TicketService.list_tickets` rejects invalid non-None types before querying; `TicketRepository.list_tickets` adds a bound Type predicate alongside Status and Priority in one SQL query. Newest-updated ordering and bounded paging are unchanged. Any filter change requests page 1; Refresh, paging and exact-number opening retain all three selections. The shared worker disables all three selectors while busy. A failed queue read retains prior rows, detail, drafts and selections and records the requested page for Refresh retry. This slice adds no database write, schema, migration, index, dependency, category reference, ticket editing, search or Knowledge change.

## Slice 029 Fresh Validation

Environment: repository `.venv\Scripts\python.exe -B`, `PYTHONPATH=$PWD\Python;$PWD` from `C:\Dev\F7Hub`. Automated GUI/Integration used `QT_QPA_PLATFORM=offscreen`; native validation used `windows` against isolated synthetic SQLite.

| Suite | Command | Fresh final-candidate result |
|---|---|---|
| Focused ticket reads/workspace | `python -B -m unittest Tests.Database.test_ticket_reads Tests.Integration.test_ticket_workspace_flow` | PASS — 25 tests, exit 0 |
| Affected ticket set | `python -B -m unittest Tests.Database.test_ticket_reads Tests.Database.test_ticket_service Tests.Database.test_ticket_repository Tests.GUI.test_main_window Tests.Integration.test_ticket_workspace_flow` | PASS — 41 tests, exit 0 |
| Database | `python -B -m unittest discover -s Tests\Database -p 'test_*.py'` | PASS — 341 tests, exit 0 |
| GUI | `python -B -m unittest discover -s Tests\GUI -p 'test_*.py'` | PASS — 153 tests, exit 0 |
| Integration | `python -B -m unittest discover -s Tests\Integration -p 'test_*.py'` | PASS — 102 tests, exit 0 |

Full regression: **596 PASS**, zero failures or errors. Focused and affected results overlap the full suites. Real-SQLite tests cover all four valid types, invalid and SQL-like values, service rejection before repository querying, three-filter composition, stable paging/order, unchanged before/after database dump, `integrity_check = ok` and zero foreign-key violations. Integration tests cover selector order/accessibility, page-1 reset, Refresh/page/Open number retention, busy-state disabling, failure preservation and requested-page retry. Expected error-path log messages in GUI/Integration had successful unittest results and exit 0.

Native Windows after correction: PASS — actual `windows` Qt platform with MainWindow at 1000×700, Open + High + Service request selected, one matching synthetic ticket and current detail loaded after observable worker idle. The [corrected-candidate capture](C:/Users/Jo/AppData/Local/Temp/f7-s029-correction-native.png) was opened and inspected: all three selectors, queue, detail and activity controls were readable without observed overlap or clipped controls. The native harness also checked that the options equal `TICKET_TYPES` once each and that All types carries `None`. This verifies the tested Windows environment, not every display scale.

## Slice 029 Delivery Gate

The review finding was corrected by making the service's single authoritative `TICKET_TYPES` sequence ordered and having the workspace iterate it directly. `_choice` now accepts that collection type; validation behavior is unchanged. The integration test checks each authoritative type exactly once and All types as `None`. Focused, affected and full regression counts above were rerun on the correction and all passed. Scope remains the same 13 tracked paths: the ticket repository/service/workspace, two focused test files and affected documentation. Database architecture and SQL Schema need no edit because the physical schema and indexes are unchanged. AHK, PowerShell and Knowledge owners are unaffected. The next gate is independent read-only rereview of the new unstaged candidate; this self-review grants no integration approval.

---

## Prior Slice 028 handoff snapshot (historical; Slice 028 later merged through PR #29)

Last verified: 2026-09-27 (America/Toronto).

Current candidate: **Slice 028 — Filter Saved Tickets by Priority**, `feature/ticket-priority-filter-s028` in `C:\Dev\F7Hub`. Approved base and current branch HEAD: `ce55c5a355bbc8434b3b536001e3dd393147821d`, equal to freshly fetched `origin/main` at the implementation baseline gate. The initial tracked, staged and untracked state was clean. Slice 027 was merged through PR #28. The protected `recovery/pre-s024-protected-work` branch remains at `002a494735f30e1488f61e21ea98740ae6371d4d` and was not modified.

Status: **PASS — READY_FOR_REVIEW**. Authorization covers IMPLEMENT → TEST → DOCUMENT only. Candidate files are unstaged and uncommitted; independent review is pending. No push, PR or integration was performed for Slice 028.

## Slice 028 Result and Scope

Saved Tickets adds a Priority selector below Status/Refresh. All priorities passes `None`; Critical, High, Medium and Low reuse the existing priority vocabulary. `TicketService.list_tickets` validates the optional priority, and `TicketRepository.list_tickets` composes it with Status using bound SQL values while preserving `updated_at DESC, ticket_id DESC` and bounded paging. Both filter changes reset to page 1. Refresh, page navigation and exact-number opening preserve both selections and the applicable page. Reads remain on the shared worker; both filter controls disable while it is busy. A failed replacement keeps the last successful rows, current detail, activity drafts and selected filters; Refresh retries the requested page, including page 1 after a failed filter change. The feature makes no database write and adds no schema, migration, index, dependency, ticket-text search or unrelated Knowledge change.

## Slice 028 Fresh Validation

Environment: repository `.venv\Scripts\python.exe -B`, `PYTHONPATH=$PWD\Python;$PWD` from `C:\Dev\F7Hub`. Automated GUI/Integration tests used `QT_QPA_PLATFORM=offscreen`; native validation used `windows` against isolated synthetic SQLite.

| Suite | Command | Fresh final-candidate result |
|---|---|---|
| Focused ticket reads/workspace | `python -B -m unittest Tests.Database.test_ticket_reads Tests.Integration.test_ticket_workspace_flow` | PASS — 22 tests, exit 0 |
| Affected ticket set | `python -B -m unittest Tests.Database.test_ticket_reads Tests.Database.test_ticket_service Tests.Database.test_ticket_repository Tests.GUI.test_main_window Tests.Integration.test_ticket_workspace_flow` | PASS — 38 tests, exit 0 |
| Database | `python -B -m unittest discover -s Tests\Database -p 'test_*.py'` | PASS — 340 tests, exit 0 |
| GUI | `python -B -m unittest discover -s Tests\GUI -p 'test_*.py'` | PASS — 153 tests, exit 0 |
| Integration | `python -B -m unittest discover -s Tests\Integration -p 'test_*.py'` | PASS — 100 tests, exit 0 |

Full regression: **593 PASS**, zero failures or errors. Focused and affected results overlap the full suites. Real-SQLite checks cover all priority modes, priority/status composition, stable ordering, paging, invalid values, SQL-like input, unchanged before/after database dump, `integrity_check = ok` and zero foreign-key violations. Integration tests cover filter choice order/accessibility, page/Refresh/direct-open preservation, disabled selectors during a delayed read, failure preservation and retry from page 2 to the requested page 1. The initial full GUI run failed three 1000×700 layout checks because placing Priority in the Status row raised the window minimum width to 1176px. Moving Priority to its own row fixed the layout. A later self-review found the failed-filter page retry edge and added a pending requested offset; focused, affected and all three full suites passed after that final production change.

Native Windows: PASS — actual `windows` Qt platform with MainWindow at 1000×700, High and Open selected, one matching synthetic ticket and current detail loaded after observable worker idle. A first harness attempt checked workspace visibility before navigating away from New Ticket and stopped before validating the feature; the corrected harness passed. The [final post-fix capture](C:/Users/Jo/AppData/Local/Temp/f7-s028-native-final-d40ee4e8bcd94da8bea2371029ca0f02.png) was opened and inspected: both filter controls, queue, ticket detail and activity controls were readable without observed overlap or clipped controls. This verifies the tested Windows environment, not every display scale.

## Slice 028 Delivery Gate

Implementation self-review found no remaining blocking defect. Only the approved ticket repository/service/workspace, focused tests and affected documentation changed. Documentation owners affected: Features, User Workflows, GUI, Python Architecture, Roadmap, Todo, ChangeLog and this report. Database architecture and SQL Schema were inspected but require no edit because physical schema, migrations and indexes did not change. AHK, PowerShell and Knowledge owners are unaffected. The next gate is independent read-only review of the exact unstaged candidate; this self-review grants no integration approval.

---

## Prior Slice 027 handoff snapshot (historical; Slice 027 later merged through PR #28)

Last verified: 2026-09-26 (America/Toronto).

Current candidate: **Slice 027 — Open a saved ticket by number**, `feature/ticket-number-open-s027` in `C:\Dev\F7Hub`. Base and current HEAD: `db81aff585d309e7db605d667fbd8332d0d1863a`, equal to freshly fetched `origin/main` at the implementation baseline gate. The initial tracked, staged and untracked scope was clean. Slice 026 is merged through PR #26; the preserved `recovery/pre-s024-protected-work` branch remains read-only at `002a494735f30e1488f61e21ea98740ae6371d4d`.

Status: **PASS — READY_FOR_REVIEW**. The user authorized IMPLEMENT → TEST → DOCUMENT only. The Slice 027 changes are unstaged and uncommitted; independent review is pending. No push, PR or integration occurred.

## Slice 027 Result and Scope

Saved Tickets adds an exact Ticket number field and Open number action. Enter and the button use the same `TicketService.get_ticket_details_by_number` call through the existing runner. The service trims input, reuses the case-insensitive repository lookup, and reloads current details through `get_ticket_details`. Blank GUI input makes no query. A successful open can display a ticket outside the visible status-filtered page without changing the filter or page. The entered number remains for retry. Missing/read-failure/disappearing-ticket paths and Cancel on the existing draft-discard confirmation preserve current detail and activity drafts. No repository query, database write, schema, migration, dependency or new exception hierarchy was added.

## Slice 027 Fresh Validation

Environment: repository `.venv\Scripts\python.exe -B`, `PYTHONPATH=$PWD\Python;$PWD` from `C:\Dev\F7Hub`. Automated GUI/Integration tests used `QT_QPA_PLATFORM=offscreen`; native validation used `windows`.

| Suite | Command | Fresh result |
|---|---|---|
| Focused ticket reads/workspace | `python -B -m unittest Tests.Database.test_ticket_reads Tests.Integration.test_ticket_workspace_flow` | PASS — 19 tests, exit 0, 25.138s |
| Affected ticket set | `python -B -m unittest Tests.Database.test_ticket_reads Tests.Database.test_ticket_service Tests.Database.test_ticket_repository Tests.GUI.test_main_window Tests.Integration.test_ticket_workspace_flow` | PASS — 35 tests, exit 0, 26.322s |
| Database | `python -B -m unittest discover -s Tests\Database -p 'test_*.py'` | PASS — 339 tests, exit 0, 24.343s |
| GUI | `python -B -m unittest discover -s Tests\GUI -p 'test_*.py'` | PASS — 153 tests, exit 0, 158.378s |
| Integration | `python -B -m unittest discover -s Tests\Integration -p 'test_*.py'` | PASS — 98 tests, exit 0, 267.124s |

Full regression: **590 PASS**, zero failures or errors. Focused/affected results overlap the full suites. Real-SQLite tests verify exact/case-insensitive match, complete current details, no match for a prefix, unchanged before/after database dump, validation, missing/disappearing-ticket and safe read-error handling. UI/integration tests verify Enter/button, preservation of Page 2, out-of-filter opening, blank input without a service call, busy duplicate prevention, retained input, cancellation and draft/detail preservation. The first focused attempt failed because test setup left a SQLite handle open and placed the target on page one; both fixtures were corrected before the passing reruns. Candidate implementation did not change to resolve those fixture failures.

Native Windows: PASS — actual 1000×700 MainWindow with isolated synthetic SQLite, `QT_QPA_PLATFORM=windows`. The harness waited for visible/enabled/idle MainWindow and Saved Tickets states before interaction. Button lookup opened a ticket outside an empty Closed queue while preserving the filter and input; Enter opened another. The [final MainWindow capture](C:/Users/Jo/AppData/Local/Temp/f7-s027-native-final-1000x700.png) was opened and inspected after the final test change: the number controls, queue, detail and status actions were readable with no observed clipping or overlap. This verifies the tested Windows environment, not every display scale.

## Slice 027 Delivery Gate

Self-review found no blocking defect. Only the approved service, GUI, focused tests and affected canonical documents changed. Ticket text/prefix/universal search, migrations, repository redesign and the protected recovery branch remain outside scope. The next gate is independent read-only review of the exact unstaged candidate.

---

## Prior Slice 026 handoff snapshot (historical; Slice 026 later merged into `main`)

Last verified: 2026-09-26 (America/Toronto).

Current candidate: **Slice 026 — Show current Knowledge article dates**, `feature/knowledge-article-dates-s026` in `C:\Dev\F7Hub`. Base and current HEAD: `c9a1a85a3b04afbf4a856379f3f0485dbf5d4351`, equal to live `origin/main` at the implementation baseline gate. Initial tree, index and untracked scope were clean. Slice 025 is CLOSED on this base. The preserved `recovery/pre-s024-protected-work` branch remains read-only at `002a494735f30e1488f61e21ea98740ae6371d4d`.

Status: **PASS — READY_FOR_REVIEW**. The user authorized IMPLEMENT → TEST → DOCUMENT only. No staging, commit, push, PR or integration occurred; independent Slice 026 review is pending.

## Slice 026 Result and Scope

KnowledgeWorkspace shows one wrapping plain-text line below Version: `Created: <created_at> · Last updated: <updated_at>`. The values come directly from the existing authoritative current-article record and are cleared with empty, missing or failed detail. They are displayed exactly as persisted, with no timezone conversion or timestamp semantics change. Selection, search and Ticket Open Article use the existing detail path. Production changes are confined to `Python/f7hub/gui/knowledge_workspace.py`; focused GUI and real-SQLite integration tests changed. No repository query, service API, database write, schema change, migration or dependency was added. Author, publication date, history comparison, restore/revert, date filters and relationship work remain outside this slice.

## Slice 026 Fresh Validation

Environment: repository `.venv\Scripts\python.exe -B`, `PYTHONPATH=$PWD\Python;$PWD` from `C:\Dev\F7Hub`. Automated GUI/Integration tests used `QT_QPA_PLATFORM=offscreen`; native validation used `windows`.

| Suite | Command | Fresh result |
|---|---|---|
| Focused GUI | `python -B -m unittest Tests.GUI.test_knowledge_workspace.KnowledgeWorkspaceTests.test_current_article_dates_follow_selection_without_extra_read Tests.GUI.test_knowledge_workspace.KnowledgeWorkspaceTests.test_current_article_dates_clear_on_missing_failed_and_empty_detail` | PASS — 2 tests, exit 0 |
| Focused real SQLite | `python -B -m unittest Tests.Integration.test_knowledge_base_flow.KnowledgeBaseFlowTests.test_current_dates_match_persisted_article_through_updates_and_search Tests.Integration.test_ticket_knowledge_flow.TicketKnowledgeFlowTests.test_link_read_and_second_article_navigation` | PASS — 2 tests, exit 0 |
| Database | `python -B -m unittest discover -s Tests\Database -p 'test_*.py'` | PASS — 336 tests, exit 0, 22.152s |
| GUI | `python -B -m unittest discover -s Tests\GUI -p 'test_*.py'` | PASS — 153 tests, exit 0, 158.013s |
| Integration | `python -B -m unittest discover -s Tests\Integration -p 'test_*.py'` | PASS — 95 tests, exit 0, 244.387s |

Full regression: **584 PASS**, zero failures. Focused results overlap the full suites. Real-SQLite checks compare the displayed values with `knowledge_articles` after creation, content revision, category assignment and publication, then reopen through FTS and compare before/after database dumps for viewing. The existing Ticket Open Article workflow now asserts the displayed current values. GUI checks cover selection changes, exact plain text, no extra detail read, and empty/missing/failed clearing.

Native Windows: PASS — actual 1000×700 MainWindow with a persisted and revised synthetic article, `QT_QPA_PLATFORM=windows`. The [MainWindow capture](C:/Users/Jo/AppData/Local/Temp/f7-s026-native-kavuy1ap/main-dates.png) was opened and inspected. The added line is readable, there is no observed clipping or overlap around it, and the body remains visible at 272 px high. This verifies the tested Windows environment, not every display scale. The first temporary harness attempt called `show_knowledge` while the initial main-window load was busy and failed before selecting an article; waiting for that load fixed the harness, with no candidate change.

## Slice 026 Delivery Gate and Skill v0.1 Observations

Self-review found no blocking defect; the next gate is independent read-only review of the exact unstaged candidate. The v0.1 baseline and scope gates prevented starting from stale handoff prose: live Git verification established the approved Slice 025 merged base while the old CURRENT_STATE/Todo still described its pre-review candidate. Its phase examples still name Slice 024. Focused and full tests remained separate, and native inspection caught a harness sequencing assumption before validating layout. Across Slices 024–026, full regressions took several minutes each; a v0.2 skill evaluation should consider this runtime and the value of native evidence. No skill change or Slice 027 work is part of this candidate.

---

## Prior Slice 025 handoff snapshot (historical; Slice 025 later closed on `main`)

Last verified: 2026-09-26 (America/Toronto).

Current candidate: **Slice 025 — All of selected Knowledge tags**, `feature/knowledge-all-selected-tags-s025` in `C:\Dev\F7Hub`. Base and current HEAD: `1c684a38d6b50a040f31c4b420e0bab9152d8c66`, equal to freshly fetched `origin/main` at the implementation baseline gate. Initial tree/index/untracked scope was clean. The preserved `recovery/pre-s024-protected-work` branch at `002a494735f30e1488f61e21ea98740ae6371d4d` was read-only evidence and remains untouched.

Status: **PASS — READY_FOR_REVIEW**. The user approved the Slice 025 plan and IMPLEMENT → TEST → DOCUMENT only. No staging, commit, push, PR or integration occurred. Independent review is pending.

## Slice 025 Result and Scope

The existing cached tag dialog now offers **Match any selected tag** and **Match all selected tags**. Two or more IDs use the chosen mode; zero and one collapse to All tags or the specific tag. `KnowledgeService.list_articles/search_articles` and `KnowledgeRepository` add `match_all_tags: bool = False`. True requires at least two distinct positive IDs in `tag_ids`, with contradictory modes rejected before querying. The All predicate counts only bridge rows for the bound selected IDs and compares that count with the selection size; the bridge primary key prevents duplicate relationships. Normal list order, current FTS MATCH/bm25 ranking and one row per article remain intact.

The workspace retains All mode through valid reference renames and partial deletion while at least two IDs survive, collapses to specific/All when fewer remain, and preserves cached choices after a failed tag read. Switching Any/All reruns the current list or last executed search without submitting unsubmitted input. Category/Status, Clear Search, tag mutation reconciliation and Ticket Open Article reset use existing paths. No migration, schema, FTS object, tag write, dependency or new service/repository layer was added. Custom tag expressions and revision restore/revert remain deferred.

Production changes are limited to `Python/f7hub/{gui/knowledge_tag_filter_dialog.py,gui/knowledge_workspace.py,repositories/knowledge_repository.py,services/knowledge_service.py}`. Focused tests changed `Tests/Database/test_knowledge_tag_filter.py`, `Tests/GUI/{test_knowledge_tag_filter.py,test_knowledge_tag_filter_dialog.py}` and `Tests/Integration/test_ticket_knowledge_flow.py`. No files were created or deleted. Documentation owners updated: Features, User Workflows, GUI, Database, Python Architecture, Roadmap, Todo, ChangeLog and this report. `Docs/09_SQLSchema.md`, ERD, AHK and PowerShell owners are unaffected.

## Slice 025 Validation

Environment: repository `.venv\Scripts\python.exe -B`, `PYTHONPATH=$PWD\Python;$PWD` from `C:\Dev\F7Hub`. Automated GUI/Integration suites used `QT_QPA_PLATFORM=offscreen`; the native check used `windows`.

| Suite | Command | Fresh result |
|---|---|---|
| Database | `python -B -m unittest discover -s Tests\Database -p 'test_*.py'` | PASS — 336 tests, exit 0, 28.247s |
| GUI | `python -B -m unittest discover -s Tests\GUI -p 'test_*.py'` | PASS — 151 tests, exit 0, 160.494s |
| Integration | `python -B -m unittest discover -s Tests\Integration -p 'test_*.py'` | PASS — 94 tests, exit 0, 247.539s |

Total full regression: **581 PASS**, zero failures. Focused new-path checks also passed: Database tag-filter module 9 tests, GUI tag-dialog module 3, workspace tag-filter module 17, new ticket-open test 1, and later callback-order/mutation tests 2; these overlap the full suites. Database tests cover partial/full/no intersections, Category/Status composition, FTS relative ranking, direct/service validation, query-only reads, unchanged dumps, `integrity_check = ok` and zero foreign-key violations. GUI/Integration tests cover mode switching, Cancel/unchanged Apply, zero/one collapse, keyboard controls, both refresh callback orders, partial failure/retry, tag mutation and Ticket Open Article reset.

Native Windows: PASS — actual 1000×700 MainWindow, All of 2 tags, one matching synthetic article and visible dialog actions. The [dialog capture](C:/Users/Jo/AppData/Local/Temp/f7-s025-native-ad8r8erf/dialog-all.png) and [MainWindow capture](C:/Users/Jo/AppData/Local/Temp/f7-s025-native-ad8r8erf/main-all.png) were opened and visually inspected. The filter row, list/detail, radio choices, check list and Cancel/Apply fit without observed clipping or overlap. This verifies the tested Windows environment, not every DPI configuration. The first native harness attempt lacked `PYTHONPATH` and exited before app construction; the corrected harness passed without a production change.

## Slice 025 Delivery Gate and Skill v0.1 Observations

Self-review found no remaining blocking defect. The final candidate must still be audited against the exact unstaged diff and reviewed independently; this report does not grant approval. The next gate is an independent read-only review of this candidate. The recovery branch is excluded from candidate scope.

The v0.1 baseline gate caught no drift: fresh origin, branch, HEAD, index and untracked checks matched the approved plan before branch creation. The explicit test gate kept focused and full results separate; full suite runtime was about 436 seconds across three suites. The native gate required actual Windows captures after offscreen tests. The stale pre-review Slice 024 wording in this file and Todo needed direct correction in the current handoff, while historical changelog evidence stayed labeled by its date. One harness setup failure exposed a missing `PYTHONPATH`, then passed after correction. Propose a v0.2 skill review after Slices 024–026 as the skill requests; do not change the skill or begin Slice 026 here.

---

## Prior Slice 024 handoff snapshot (historical; Slice 024 later merged into `main` through PR #24)

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
