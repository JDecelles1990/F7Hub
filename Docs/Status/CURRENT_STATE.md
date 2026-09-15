# F7Hub Current State

Last verified: 2026-09-15 (America/Toronto)

Branch: `feat/knowledge-category-assignment`

Base and current HEAD: `67dbe5269d1ba4b22f246333ec79782076ad7840`

Status: PASS — Slice 018 implemented and validated; ready for independent review. Work remains unstaged and uncommitted. Independent review is NOT complete. Slice 019 has NOT started.

## Current Milestone

ONE DRAFT KNOWLEDGE ARTICLE CAN ASSIGN, CHANGE OR REMOVE ITS CATEGORY

## Working Behavior and Boundaries

Knowledge Base → open DRAFT → Category… beside the current category name → select an active KNOWLEDGE category or Not selected → Save → authoritative category displays. Assign, change and remove: IMPLEMENTED FOR DRAFT. Active KNOWLEDGE selector: IMPLEMENTED. Inactive/wrong-scope/missing assignment: REJECTED. NULL removes the category. Inactive assigned names remain readable and can be replaced or cleared.

PUBLISHED/ARCHIVED category mutation, category history, category filtering, tags and category administration: NOT IMPLEMENTED. Published and archived articles still display their category. Existing draft editing, publish, archive, version history, search and ticket Open Article continue to work.

ArticleCategoryDialog uses ServiceTaskRunner for independent category reads and writes. Cancel/default Enter/Escape cause no mutation or refresh. Cancel/Escape also work during reference reads because the main window owns the modal outside disabled pages. Dismissed callbacks are ignored. Failed reference loading leaves article reads usable and supports Refresh categories. Writes disable duplicate submission and dismissal until completion. Reviewed-record identity prevents stale modal submission after workspace context changes. Failure preserves truthful current detail and permits retry or reopening. Success uses the repository's authoritative reload before commit; no optimistic category update occurs.

## Persistence and Concurrency

Bootstrap explicitly shares CategoryRepository between KnowledgeService and TicketReferenceService. CategoryRepository owns scoped taxonomy reads. KnowledgeService maps active KNOWLEDGE rows to category_id/name options, validates inputs, supplies one new UTC timestamp and sanitizes errors. All real KnowledgeService construction sites under Python/Tests supply the required category dependency; test doubles retain their own explicit contracts.

KnowledgeRepository.set_draft_category uses BEGIN IMMEDIATE, authoritative existence/DRAFT/version/updated_at checks, in-transaction category eligibility, then no-op detection. The conditional parameterized UPDATE requires ID/DRAFT/version/updated_at and exactly one affected row. Reload precedes COMMIT; failure rolls back. The service advances timestamps at microsecond precision even when the clock repeats or moves backward; the repository rejects reuse of the current token.

| Field or relationship | Category operation |
|---|---|
| category_id | Active KNOWLEDGE ID or NULL |
| updated_at | New UTC metadata/concurrency token |
| version_number | Unchanged |
| Title, summary, body, code | Unchanged |
| Status, published_at | Unchanged |
| Immutable version history | Unchanged; no new row |
| Ticket RELATED row | Unchanged |
| FTS content/schema | Unchanged |

A separate service changed DRAFT V2 from T1 to T2; the modal's subsequent V2/T1 submission was rejected. The external category stayed authoritative, V2 stayed V2 and the entire post-external-write database dump remained unchanged after rejection. No-op cannot bypass stale checks.

Current record reads resolve category_name by a nullable scalar lookup of categories' primary key, including inactive references. No GUI SQL, duplicate taxonomy reader, new schema object or migration is introduced.

## Validation

Retained focused result: **117 PASS**, completed before interruption. Fresh resumed focused result: **82 PASS**, covering Knowledge search (7), service (18), category repository/service (14), Knowledge GUI (33), real-window category GUI (9) and the affected quick-company size regression (1).

The earlier full Database attempt FAILED with seven NameError errors in the search fixture: a mechanically inserted Mock was undefined. The corrected fixture supplies CategoryRepository(self.database_path); search behavior and assertions are unchanged. Constructor/search verification passed (7 tests), and the resumed focused run includes those tests. The first completed Integration run FAILED nine 1000×700 assertions because the added top-toolbar action forced 1038 pixels under its style. Moving Category… to the current category detail row corrected that layout without changing the write workflow. Initial failures remain recorded in external evidence.

Final sequential regression uses the existing `.venv` interpreter, PYTHONPATH=Python plus repository root, PYTHONDONTWRITEBYTECODE=1 and QT_QPA_PLATFORM=offscreen:

| Suite | Result | Duration |
|---|---:|---:|
| Database | 294 PASS | 14.860s |
| GUI | 104 PASS | 19.331s |
| Integration | 86 PASS | 373.145s |

Final total: **484 PASS**, zero failures/errors/skips, sequential process exit 0. Pre-slice baseline: 280 Database / 95 GUI / 84 Integration = 459. Increase: 14 Database + 9 GUI + 2 Integration = 25 tests; no suite decreased. Production/test code did not change during the final full run; subsequent edits only completed documentation.

## Native Windows Evidence

Retained native workflow: PASS, Qt windows, isolated synthetic SQLite, MainWindow 1000×700. Selector; Cancel/Enter/Escape; assign/change/remove/final assignment; edit; publish; archive; history; search; ticket link/Open Article and reconstruction all passed. The 21 prior captures were inspected. Repository/service/dialog behavior is unchanged since that workflow; the category action placement alone changed during resumption.

Fresh bounded native layout verification: PASS at 1000×700, Category… beside current name, visible active-choice popup, Escape without mutation, keyboard selection, asynchronous assignment and disabled published action. All four new captures were inspected. They supersede the earlier toolbar layout images. Total inspected captures: 25. These are agent checks, not independent review or user acceptance testing.

Evidence: `C:\Users\Jo\AppData\Local\Temp\f7hub-slice018-validation` contains focused-resumed.log, final suite logs, retained focused/native logs, native-layout-resumed.py/log, screenshots and isolated databases. No evidence artifacts are stored in the repository.

## Database and Preservation

Fresh isolated checks: six migration files and records; 0001–0006 Git-normalized blobs unchanged; schema identical to a freshly bootstrapped reference; integrity_check=ok; foreign_key_check=zero rows; FTS integrity=PASS and one expected content match. No 0007 migration. These results are captured in integrity-preservation.json.

Docs/10_FolderStructure.md SHA256 still matches the initial protected work. Docs/Archive/DocsOLD/00_Vision.md remains deleted. ROOT.md SHA256 is unchanged. Docs/08_ERD.md and Docs/09_SQLSchema.md remain unchanged. No staged changes or commits.

## Documentation Impact and Next Gate

Updated owners: 03 Features, 04 User Workflows, 05 GUI, 06 System Architecture, 07 Database, 13 Python Architecture, 16 Roadmap, 17 Todo, 18 ChangeLog and this current-state report. Requirements remain valid; schema/ERD/ROOT need no change. Category metadata is explicitly current-only.

Self-review: PASS for shared taxonomy reuse, explicit injection, DRAFT/active-scope/NULL policy, dual concurrency checks, immutable history, lifecycle/search/link continuity, parameterized writes, safe errors, PlainText rendering and absence of GUI SQL.

Next gate: independent review of Slice 018. One future candidate: read-only Knowledge category filtering. It is not implemented or started here.
