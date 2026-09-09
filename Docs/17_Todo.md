# F7Hub Todo

> Document: `Docs/17_Todo.md`  
> Project: F7Hub  
> Purpose: Maintain the current actionable work queue for F7Hub.  
> Related Documents: `16_Roadmap.md`, `18_ChangeLog.md`, `19_DocumentationIndex.md`

---

# 1. Purpose

This file answers:

> What concrete work should happen next?

It does not own long-term sequencing, technical specifications or historical changes.

```text
16_Roadmap.md
→ long-term sequence

17_Todo.md
→ current actionable work

18_ChangeLog.md
→ meaningful completed changes
```

---

# 2. Current Project State

Repository inspection and tests through 2026-09-05 confirmed:

```text
Documentation consistency review: IN PROGRESS
SQLite migration infrastructure: VERIFIED
Core application migration — 0001_core.sql: VERIFIED
Taxonomy migration — 0002_taxonomy.sql: VERIFIED
Company/contact migration — 0003_companies_contacts.sql: VERIFIED
Ticket-core migration — 0004_tickets.sql: VERIFIED
Knowledge migration — 0005_knowledge.sql: VERIFIED
CompanyRepository and ContactRepository: VERIFIED
TicketRepository and TicketService creation boundary: VERIFIED
Ticket notes, status changes, resolution and reopening service boundary: VERIFIED
PySide6 ticket creation widget and vertical integration: VERIFIED
PySide6 application bootstrap and minimal MainWindow: VERIFIED
Remaining business-domain migrations: PLANNED
Saved-ticket workspace and background service runner: VERIFIED
AutoHotkey F7 launch/focus shortcut: VERIFIED
Permanent isolated database tests: PASS — 133 tests
GUI tests: PASS — 10 tests
Application and GUI integration tests: PASS — 14 tests
Local Git repository and recovery baseline: PRESENT
Remote origin: CONFIGURED
GitHub synchronization: BLOCKED — SSH public-key authentication
```

The explicit 2026-09-03 implementation task authorized the SQLite infrastructure slice before a Git baseline was established. The local baseline now exists, but publishing `main` to `origin/main` remains pending.

---

# 3. P0 — Complete Documentation Review

- [x] Inspect `AGENTS.md` and `ROOT.md`.
- [x] Inspect all canonical `Docs/00` through `Docs/19` Markdown files.
- [x] Review architecture and technology boundaries.
- [x] Review database entity, naming and migration consistency.
- [x] Review Roadmap, Todo and ChangeLog role separation.
- [x] Inspect repository state needed to validate implementation claims.
- [x] Run Markdown, reference and stale-term validation.
- [x] Run the documented SQL DDL in a fresh in-memory SQLite database.
- [ ] Obtain user acceptance of the corrected documentation baseline.

Documentation remains in `REVIEW` until accepted; review completion does not imply implementation.

---

# 4. P0 — Publish Git Baseline

`C:\Dev\F7Hub\` is a local Git repository on `main`. The local baseline exists, `origin` is configured, and two local commits were present when the Slice 001 follow-up was verified. No pre-Slice-001 focused diff is available because the initial baseline commit was created after the implementation.

Current actions:

- [x] Initialize this directory as the canonical local Git repository.
- [x] Establish the local `main` branch and baseline commit.
- [x] Configure `origin` as `git@github.com:JDecelles1990/F7Hub.git`.
- [x] Review and populate `.gitignore` before remote publication.
- [x] Exclude runtime databases, logs, secrets, caches and generated artifacts as appropriate.
- [x] Review the local baseline file set for sensitive or obsolete content before publication.
- [ ] Publish local `main` to `origin/main` only with explicit user authorization.

Remote publication remains pending until GitHub authentication succeeds and remote history can be inspected safely.

---

# 5. P0 — First Implementation Task

## Objective

Implement F7Hub SQLite bootstrap and migration infrastructure.

## Scope

- database connection creation
- `PRAGMA foreign_keys = ON`
- busy-timeout configuration
- `schema_migrations` tracking
- migration discovery
- migration ordering
- checksum validation
- transactional migration execution
- isolated database tests

## Out of Scope

- taxonomy or business-domain tables
- company, contact or ticket repositories
- PySide6 GUI
- PowerShell execution
- AutoHotkey
- diagnostics
- AI
- plugins
- Microsoft integrations

## Acceptance Criteria

- [x] An empty temporary database can be initialized.
- [x] Foreign-key enforcement is verified for each application connection.
- [x] Migrations execute once and in order.
- [x] Applied migration checksums are validated.
- [x] Failed migrations roll back and are not marked applied.
- [x] Database integrity and foreign-key checks pass.
- [x] Success and failure paths are covered by tests.

## Validation

Run the isolated database test suite and report only `PASS`, `FAIL`, `NOT RUN`, or `BLOCKED`.

```text
Status: PASS — 28 tests — 2026-09-03
```

## Permanent Regression Follow-Up

- [x] Reject renamed applied migrations.
- [x] Parse semicolons in quoted values, line comments and block comments.
- [x] Reject migration-authored `BEGIN`, `COMMIT`, `ROLLBACK` and `SAVEPOINT`.
- [x] Reject migration-authored `ATTACH` and `DETACH`.
- [x] Verify rollback, absent history records and usable connections after rejection.
- [x] Verify the approved `schema_migrations` structure and constraints.
- [x] Verify negative migration execution times are rejected.

```text
Status: PASS — 35 tests — 2026-09-03
```

---

# 6. P1 — Second Persistence Slice: Taxonomy

Completed and verified on 2026-09-03:

- [x] Create `Database\Migrations\0002_taxonomy.sql`.
- [x] Implement only `categories` and `tags` from the approved physical schema.
- [x] Add focused constraint, rollback, checksum, idempotency and integrity tests.
- [x] Do not begin company, contact, ticket or GUI work in this slice.

```text
Status: PASS — 9 focused taxonomy tests; 49 full database tests
```

---

# 7. P1 — Third Persistence Slice: Companies and Contacts

Completed and verified on 2026-09-03:

- [x] Create `Database\Migrations\0003_companies_contacts.sql`.
- [x] Implement `companies`, `company_notes`, `company_links` and `contacts`.
- [x] Add focused migration, constraint, relationship and failure-path tests.

```text
Status: PASS — 10 focused company/contact tests; 59 full database tests
```

---

# 8. P1 — Company and Contact Repository Slice

Before beginning ticket persistence, the company/contact repository follow-up was completed and verified on 2026-09-03:

- [x] Add `CompanyRepository` with structured company records and parameterized create, read, list, update and activation operations.
- [x] Add `ContactRepository` with structured contact records, company filtering and parameterized create, read, list, update and activation operations.
- [x] Preserve database constraints, `ON DELETE SET NULL` contact behavior and SQL-injection resistance.
- [x] Keep services, GUI, tickets, dependencies and production schema out of this repository-only slice.

```text
Status: PASS — 5 CompanyRepository tests; 5 ContactRepository tests; 69 full database tests
```

---

# 9. P1 — Fourth Persistence Slice: Tickets

The schema-only ticket slice was completed and verified on 2026-09-03:

- [x] Create `Database\Migrations\0004_tickets.sql`.
- [x] Implement `tickets`, `ticket_notes`, `ticket_status_history` and `ticket_timeline_events` from the approved physical schema.
- [x] Add the nine documented ticket-core indexes.
- [x] Test migration ordering, checksum validation, idempotency, constraints, foreign keys, delete behavior, rollback and integrity.

```text
Status: PASS — 10 focused ticket migration tests; 79 full database tests
```

The ticket repository/service creation boundary was completed and verified on 2026-09-04:

- [x] Implement `TicketRepository` creation and reload behavior with focused persistence and rollback tests.
- [x] Implement `TicketService` validation and transaction coordination as a separate application layer.
- [x] Create initial status history and timeline records transactionally with the ticket.

```text
Status: PASS — 6 focused TicketRepository tests; 5 focused TicketService tests; 101 full database tests
```

The minimal PySide6 ticket workflow was completed and verified as a separate GUI slice using the tested service boundary:

- [x] Adopt PySide6 6.11.2 and update the current canonical framework references from PyQt6.
- [x] Add `TicketCreateWidget` with required fields, optional references, inline feedback, safe persistence errors and keyboard save behavior.
- [x] Keep workflow validation and persistence in `TicketService`; the widget contains no SQL.
- [x] Add isolated GUI tests and a complete GUI-to-service-to-repository-to-SQLite integration test.

```text
Status: PASS — 5 focused GUI tests; 1 vertical integration test; 101 database tests
```

Application-shell follow-up:

- [x] Add application bootstrap and a minimal `QMainWindow` that composes the tested ticket form.
- [x] Add the `python -m f7hub` development entry point and safe startup failure feedback.
- [x] Keep F7 launch/focus behavior outside this Python slice.

```text
Status: PASS — 7 GUI tests; 5 application and GUI integration tests; 101 database tests
```

Ticket activity persistence/service slice — verified 2026-09-04:

- [x] Implement ticket notes and status transitions through repository and service boundaries before adding their GUI workflow.
- [x] Persist notes, timeline references and ticket activity timestamps atomically.
- [x] Validate status transitions and atomically update lifecycle fields, status history and timeline.
- [x] Require a resolution summary and preserve it as a resolution note.
- [x] Support the approved reopening of resolved/closed tickets to Open, preserving older resolution text.
- [x] Verify validation, writer serialization, missing records, reload and failure rollback.

```text
Status: PASS — 11 activity repository tests; 17 activity service tests; 129 full database tests
GUI regression: PASS — 7 tests; application/integration regression: PASS — 5 tests
```

Saved-ticket workspace slice — verified 2026-09-05:

- [x] Add list/reload service operations and a minimal ticket list/detail GUI for saved tickets, notes, history and status actions.
- [x] Connect successful ticket creation to its saved detail view and verify the complete create/open/work/reopen workflow.
- [x] Verify draft preservation, failed saves, committed saves with failed reloads, paging and status filtering.
- [x] Run service calls in a worker while disabling conflicting GUI actions.
- [x] Perform a native Windows visual/input check of the saved-ticket workspace (agent visual inspection and Qt input events, default size and 1000×700; 2026-09-05).

Validation: PASS — 133 database tests, 10 GUI tests, 14 application/integration tests, including nine saved-ticket GUI flows against isolated SQLite. Integrity and foreign-key checks: PASS. Native Windows visual/input check: PASS at the initial size and 1000×700.

F7 launch/focus slice — verified 2026-09-05:

- [x] Add the AutoHotkey v2 entry point and project-relative Python launcher.
- [x] Focus/restore existing windows and guard repeated startup attempts.
- [x] Check missing runtime, timeout/retry, cold launch, actual global F7 focus/restore and duplicate shortcut startup.
- [x] Keep normal startup unelevated and leave login-startup registration unchanged.

Slice 006 — reference-aware ticket creation, verified 2026-09-05:

- [x] Load active company choices and filter active contacts by the selected company through the service boundary.
- [x] Clear incompatible contact selections and preserve drafts on query/save failures.
- [x] Revalidate active references and membership in the creation transaction.
- [x] Display company/contact names when reopening saved tickets; handle null, inactive and deleted references safely.
- [x] Verify 142 database, 16 GUI and 21 integration tests, plus native Windows visual/input checks using isolated synthetic data. No migration.

Slice 007 — ticket category references, verified 2026-09-05:

- [x] Load active TICKET categories through CategoryRepository and TicketReferenceService; order by sort order, name and ID.
- [x] Preserve optional selection, draft text and company/contact choices through category failure and independent retry.
- [x] Reuse transactional save-time validation; reject inactive, missing and wrong-scope categories without partial activity writes.
- [x] Display current category names for saved tickets, including inactive categories and safe null/deletion handling.
- [x] Verify focused automated tests and native Windows selection, persistence, reopening, failure/retry and 1000×700 layout with synthetic data.
- [ ] Consider hierarchical selector labels in a later slice; current names are displayed directly.

Slice 008 — quick company creation, verified 2026-09-06:

- [x] Add a name-only Quick Add Company dialog and narrow CompanyService using CompanyRepository.
- [x] Run creation in the existing worker, prevent duplicate submissions and preserve input after failure.
- [x] Select the new active company, clear incompatible contacts and preserve the complete ticket draft without category reload.
- [x] Retain committed identity through failed selector refresh and recover without duplicate insertion.
- [x] Make repository insert/reload atomic and verify rollback before retry.
- [x] Verify native Windows validation, cancel, create, refresh recovery, save/reopen and 1000×700 layout with synthetic data.
- [x] Complete regression: 161 database, 30 GUI and 32 integration tests (223 total); integrity_check = ok, foreign_key_check = zero violations, five unchanged migrations.

Slice 009 — quick contact creation, verified 2026-09-06:

- [x] Add company-scoped ContactService and Quick Add Contact with required name and optional email.
- [x] Validate the active company and insert/reload within one transaction; prove rollback and single-row retry.
- [x] Reuse ServiceTaskRunner, prevent duplicate submission and unsafe close/cancel, retain inputs on failure.
- [x] Automatically select the created contact and preserve every unrelated ticket draft field.
- [x] Retain committed contact/company identity during failed refresh; lock company switching and recover with contact-only reads.
- [x] Verify existing-company and combined quick-company/contact creation, ticket persistence and reopening.
- [x] Pass 21 focused database, 10 GUI and 8 integration tests; native Windows rerun of 18 GUI/integration tests and visual inspection at 1000×700.
- [x] Remediate post-commit company deactivation/deletion: typed unavailable-company feedback and explicit abandonment restore reference selection and ticket save, preserve the committed contact/draft, and ignore stale callbacks without duplicate insertion.
- [x] Remediation validation: 44 focused tests; three native Windows recovery/normal-flow checks and recovery layout inspection at 1000×700.
- [x] Complete post-remediation regression: 178 database, 40 GUI, 44 integration (262 total); integrity_check = ok, foreign_key_check = zero violations, five unchanged migrations.
- Historical Slice 009 re-review checkpoint: superseded by the integrated baseline at 8c2ef7f (merge PR #4); this continuation did not repeat that independent review.

The subsequent Slice 010 create/list/read implementation is recorded below; the Slice 009 checks above are historical evidence.

---

# 10. P1 — Fifth Persistence Slice: Knowledge

Slice 010 — first usable Knowledge Base, verified 2026-09-06:

- [x] Preserve and complete the existing create/list/read implementation on feat/knowledge-base-first-slice.
- [x] Required user-entered article code/title/body, optional summary, safe validation and duplicate-code feedback.
- [x] DRAFT/version 1, atomic article plus initial version snapshot, rollback before commit on failure.
- [x] Persistent deterministic list/reopen, asynchronous dialog/workspace, plain/read-only Markdown source.
- [x] Force untrusted metadata to plain text and cover HTML-like input with a GUI regression.
- [x] Retain supplied Database evidence: 11 focused and 189 full tests; rerun GUI 45 and Integration 46 after the display fix (280 total regression evidence).
- [x] Native Windows synthetic create/list/read, two articles, reconstruction and ticket navigation at 1000×700; visual layout inspected.
- [x] Five unchanged migrations, integrity_check = ok, zero foreign-key violations; rollback/retry and one successful commit independently checked.
- Historical checkpoint: Slice 010 is now integrated through PR #5 at main HEAD 04466c3c549bc809a7314c136e1d512ba403ae98.

Slice 011 — DRAFT editing with version history, verified 2026-09-06:

- [x] Preserve the existing implementation on feat/knowledge-article-editing; no continuation refactor or behavior rewrite.
- [x] Read-only article code/version; editable title/summary/body; current Version N in details.
- [x] Validate positive ID/version (reject bool), normalize title/summary and preserve valid body content.
- [x] BEGIN IMMEDIATE, authoritative existence/DRAFT/version checks, conditional UPDATE, immutable new snapshot, reload and one commit.
- [x] Preserve snapshots 1/2/3, reject stale overwrites even after workspace refresh, roll back snapshot/reload failures and retry without skipped/duplicate revisions.
- [x] No-change detection only after authoritative version checks; safe missing/non-DRAFT/persistence errors and retained editor input.
- [x] Async save, duplicate/close protection, same-ID list/detail reconciliation and unchanged creation workflow.
- [x] Focused tests: repository/service 24 PASS, GUI 12 PASS, Integration 6 PASS.
- [x] Fresh full regression: Database 202 PASS, GUI 52 PASS, Integration 50 PASS; total 304, up from 280.
- [x] Native Windows input/visual checks at 1000×700, isolated synthetic SQLite; retained on continuation because GUI/persistence code did not change.
- [x] Five unchanged migrations; integrity_check = ok, foreign_key_check = zero violations; ROOT.md and separate archive deletion untouched.
- Historical Slice 011 review checkpoint is superseded by integration through PR #6 at 13fc1bcae44f4e36c6e6dd2fcf382874ec121508.

Slice 012 — RELATED ticket/article linking, verified 2026-09-07:

- [x] Add narrow TicketKnowledgeService/Repository using the existing junction and lightweight joined current metadata.
- [x] Atomically verify entities/duplicate state, insert RELATED and reload; safe typed errors, rollback and concurrent duplicate protection.
- [x] Saved-ticket Knowledge tab, async candidate selector, Link Article, Refresh and Open Article; selection retention and duplicate/close protection.
- [x] MainWindow-mediated article-ID navigation, current detail selection, missing-target feedback and persisted reconstruction.
- [x] Focused repository/service 24 PASS, combined ticket/knowledge GUI 24 PASS (12 new), cross-module Integration 7 PASS.
- [x] Full regression: Database 226 PASS, GUI 64 PASS, Integration 57 PASS; total 347, up 43 from 304.
- [x] Native Windows 1000×700 input/visual checks for link/list/open, article create/edit, notes/status lifecycle and reconstruction. Initial code sizing corrected and rerun.
- [x] Only junction writes; five unchanged migrations, integrity_check = ok, zero FK violations and both deletion cascades tested.
- [x] Independent Slice 012 review approved with no defects/cleanup; integrated through PR #7 at 68aefb157c7351aa47e5f11ffd4c94cdbb8cf0ae.

Slice 013 — RELATED ticket/article unlink, verified 2026-09-07:

- [x] Extend the existing relationship repository/service/widget; no new infrastructure or migration.
- [x] BEGIN IMMEDIATE before ticket/article/RELATED existence checks, exact parameterized DELETE and one-row requirement; rollback on delete/commit failure.
- [x] Preserve ticket, article, other RELATED, APPLIED and RESOLUTION_SOURCE rows; no ticket updated_at, notes, history or timeline writes.
- [x] Safe missing-ticket, missing-article and not-linked errors; concurrent independent services produce one success and one not-linked result.
- [x] Unlink Article with explicit plain-text confirmation, Cancel as default/escape, no write on Cancel, async execution and duplicate/context protection.
- [x] Preserve failed selection; preserve committed-success feedback after refresh failure and recover with Refresh without repeating DELETE.
- [x] Candidate reappearance, normal relink with a new timestamp, persisted reconstruction and exact remaining-article navigation.
- [x] Focused tests: repository/service 42 PASS, combined Ticket/Knowledge GUI 34 PASS, Integration 16 PASS.
- [x] Full regression: Database 244 PASS, GUI 74 PASS, Integration 66 PASS; total 384, up 37 from 347. Evidence retained during documentation-only completion.
- [x] Native Windows 1000×700 synthetic input/visual checks: Cancel, Unlink, parent/other-link preservation, candidate/relink, exact Open Article, notes and Resolve → Close → Reopen.
- [x] Five unchanged migrations; integrity_check = ok, foreign_key_check = zero violations; ROOT.md and separate archive deletion preserved.
- Historical Slice 013 review checkpoint; the current Slice 014 review gate is recorded below.

Slice 014 — read-only version-history viewer, remediation verified 2026-09-09:

- [x] Resume and inspect all nine existing implementation/test paths; preserve correct work.
- [x] Lightweight newest-first metadata and exact selected snapshot, with no migration or data writes.
- [x] Safe positive-ID validation, missing article/revision and empty-history handling.
- [x] History for DRAFT/PUBLISHED/ARCHIVED, service/busy guards, plain text and read-only body.
- [x] Serialized detail selection; fresh real-MainWindow and native PASS for pending list + Close, list + Escape, detail + Close and detail + Escape, with late callbacks ignored.
- [x] Scroll to both ends of a 6,132-character historical summary at 900×620; literal metadata and read-only body remain accessible, with 356-pixel native body height.
- [x] Exact V1/V2/V3 and immutable current/history/full database state across viewing and reconstruction.
- [x] Focused Integration fresh 29 PASS, exit 0; retained post-fix focused GUI log confirms 19 PASS. Earlier focused repository/service 31 PASS remains historical.
- [x] Fresh sequential full regression: Database 251, GUI 81, Integration 73 = 405 PASS, all exit 0; no suite decreased.
- [x] Fresh native Windows Qt input and inspection of all six captures, 1000×700 main / 900×620 dialog; read-only database, five migrations, integrity ok, zero FK violations.
- [x] Preserve Docs/10 modification, archive deletion and ROOT.md; evidence remains outside repository.
- [ ] Independent Slice 014 re-review after remediation; keep changes unstaged/uncommitted.

Recommended next slice only: Knowledge Search / FTS5 for current articles. See 16_Roadmap.md for the six-option comparison. Do not begin Slice 015. Restore/revert, historical editing/deletion, compare/apply, historical status, search/AI, pagination, category/tag management, publishing/archiving and richer ticket relationship workflows remain deferred.

The schema-only relational knowledge slice was completed and verified on 2026-09-04:

- [x] Create `Database\Migrations\0005_knowledge.sql`.
- [x] Implement knowledge articles, versions, links, article relationships, ticket/article links and article/tag links from the approved physical schema.
- [x] Add the seven documented relational knowledge indexes.
- [x] Test ordering, checksums, idempotency, constraints, foreign keys, cascades, rollback and integrity.
- [x] Keep `knowledge_article_scripts` deferred until the scripts schema exists and keep all FTS objects in the later FTS migration.

```text
Status: PASS — 11 focused knowledge migration tests; 90 full database tests
```

---

# 11. Repository Follow-Ups

These are real repository issues found during documentation review but are not part of the documentation-only edit scope:

- [ ] Decide whether to remove, archive or update `.Create-F7HubStructure.ps1`, which contains the obsolete OneDrive root and old folder model.
- [ ] Decide whether to update `Generate-F7FolderInventory.ps1`, which contains the obsolete OneDrive root.
- [ ] Decide whether the zero-byte `Database\SQLite\F7Hub.db` scaffold artifact should be retained.
- [ ] Decide whether the empty noncanonical `zip\` directory should be removed or assigned an approved purpose.
- [ ] Decide whether empty root support files such as `README.md`, `CHANGELOG.md`, `.gitignore`, `.editorconfig`, `LICENSE` and `Project.json` should be populated or removed during repository initialization.
- [ ] Add project-local `.agents/skills\` only when a concrete reusable procedure justifies them.
- [ ] Organize legacy diagrams under `Docs\Assets\Diagrams\` without treating them as current architecture until reviewed.
- [ ] Add reviewed local Mermaid source under `Docs\Assets\Diagrams\` when canonical diagrams are next revised; do not recover source from deleted browser exports.

---

# 12. Deferred Work

The following remain `DEFERRED` until earlier foundations and real requirements justify them:

- plugin loader or marketplace
- persistent PowerShell runspace
- automatic bidirectional PSA/RMM synchronization
- autonomous AI administration
- multi-user server architecture
- microservices
- advanced workspace persistence

Long-term placement belongs in `16_Roadmap.md`.

---

# 13. Rejected Directions

The following remain `REJECTED` unless an explicitly approved architecture change revisits them:

- AutoHotkey as the primary GUI
- PowerShell as the primary application layer
- direct PowerShell or AutoHotkey ownership of core SQLite persistence
- arbitrary 100-table or 120-table targets
- AI directly executing arbitrary commands
- building the entire application in one coding task

---

# 14. Maintenance Rule

Keep this file short and actionable.

When work is completed:

1. remove it from the active queue or mark the checklist item complete
2. record meaningful completed changes in `18_ChangeLog.md`
3. update `16_Roadmap.md` only when milestone sequencing changes
4. keep implementation and test status truthful

> The Todo should make the next useful task obvious without reproducing the Roadmap.
