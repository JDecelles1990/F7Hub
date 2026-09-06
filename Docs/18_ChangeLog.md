# F7Hub ChangeLog

> Document: `Docs/18_ChangeLog.md`  
> Project: F7Hub  
> Purpose: Record meaningful completed changes to F7Hub architecture, documentation, schema, behavior, tooling and releases.
> Related Documents: `16_Roadmap.md`, `17_Todo.md`, `19_DocumentationIndex.md`

---

# 1. Purpose

This file answers:

> What meaningfully changed, when did it change, and what was validated?

It is historical. It is not a roadmap, todo list, requirements document or substitute for source-control history.

```text
16_Roadmap.md
→ future direction

17_Todo.md
→ current actionable work

18_ChangeLog.md
→ meaningful completed changes
```

---

# 2. Status Discipline

Documentation changes, implementation and validation are reported separately.

```text
Documentation status
→ DRAFT / REVIEW / APPROVED / DEPRECATED / ARCHIVED

Implementation status
→ PLANNED / IN PROGRESS / IMPLEMENTED / VERIFIED / DEFERRED / REJECTED / NOT VERIFIED

Test or validation status
→ PASS / FAIL / NOT RUN / BLOCKED
```

No entry may imply that documented target architecture is implemented or verified without repository and test evidence.

---

# 2026-09-06 — Slice 008: Quick Company Creation from New Ticket

- Added a name-only Quick Add Company dialog and narrow CompanyService. Creation trims and validates text, supplies matching UTC timestamps and persists an active company through CompanyRepository.
- Reused ServiceTaskRunner for responsive background creation, guarded repeated submissions and blocked cancellation/closing while the write finishes. Cancel before submission performs no write; failures retain input and show safe messages.
- Successful creation refreshes companies and contacts, selects the new company and clears incompatible contact selection without reloading categories or resetting any unrelated ticket field. The existing TicketService save/reopen path is unchanged.
- Retained committed company identity after failed selector refresh. Recovery through Refresh references selects the existing record without another insertion; committed creation remains explicitly reported as successful.
- Made CompanyRepository INSERT and returned-record reload one transaction. Reload failure rolls back the insert, eliminating ambiguous retry after a partial repository operation. Other repository behavior and all five migrations are unchanged.
- Native Windows inspection found that a separate success-message row expanded the window above 1000×700. Moved success feedback beside Create Ticket and verified the corrected size during success and refresh failure.
- Focused checks: PASS — 14 service/repository, 8 GUI and 5 integration tests; all 27 rerun after the final service-error and layout adjustments. Full regression: PASS — 161 database, 30 GUI and 32 integration tests (223 total). Isolated integrity_check = ok, foreign_key_check = zero violations, migration count = 5.
- Native Windows visual/input checks: PASS — validation, cancel, create, automatic selection, draft preservation, contact reset, post-commit refresh recovery, save/reopen, notes and Resolve → Close → Reopen at 1000×700. Agent verification, not user acceptance testing. AutoHotkey: NOT RUN; launcher contract unchanged.
- No schema, dependency or ROOT.md changes. The archived user modification was preserved exactly. Synthetic databases, screenshots and the native verification script remain outside the repository. No staging, commit, push or merge performed.

---

# 2026-09-05 — Slice 007: Ticket Category Reference Integration

- Added a small read-only CategoryRepository for scoped category facts, with deterministic sort-order/name/ID ordering. TicketReferenceService supplies active TICKET options with separate IDs and labels.
- New Ticket loads categories through the existing ServiceTaskRunner. Category-only refresh/retry avoids company/contact queries and preserves the draft and reference selections on failure. Empty lists retain optional Not selected.
- Reused existing TicketService validation and atomic ticket/history/timeline persistence unchanged. Saved-ticket details resolve current category names, including inactive categories, and handle null/deleted references through the existing SET NULL relationship.
- Reduced the description minimum height to 100 pixels after native inspection found the additional feedback row exceeded the 1000×700 target. Corrected an existing GUI test double to include category reference fields.
- Validation: PASS — 152 database, 22 GUI and 27 integration tests (201 total). Focused runs: 10 database tests, 24 GUI/integration tests and one additional category-worker responsiveness test. Integrity check returned ok; foreign-key check returned zero violations; migration count remains five.
- Native Windows visual/input verification: PASS — category population/filtering, retry, draft and company/contact preservation, create/reopen, optional category, notes and Resolve → Close → Reopen. The corrected form and saved-ticket workspace fit 1000×700. Agent verification, not user acceptance testing. AutoHotkey: NOT RUN — launch contract unchanged.
- No schema, historical migration or dependency changes. ROOT.md and the unrelated archived modification were preserved. Slice changes remain uncommitted for independent review.

---

# 2026-09-05 — Slice 006: Reference-Aware Ticket Creation

- Added active company selection and company-filtered active contacts to New Ticket through a narrow TicketReferenceService and the existing background runner. IDs remain separate from canonical display labels.
- Company switching clears the old contact. Empty choices and reference-query failures have inline feedback and retry; draft text and valid reference selections survive refresh failures.
- Creation rechecks active state and company/contact membership in its existing transaction. Ticket details resolve names from the same SQLite snapshot, including inactive rows; deletion retains the existing SET NULL behavior.
- Fixed deferred initial reference loading so widget destruction cancels its callback. Adjusted description minimum height to fit the added controls and error feedback at 1000×700.
- Validation: PASS — 142 database, 16 GUI and 21 integration tests. Native Windows visual inspection and Qt input-event checks: PASS for company loading, contact filtering, switching, persistence/reopening, empty choices, query errors and stale references. These are agent checks, not user acceptance testing. AutoHotkey was not rerun in this slice.
- No schema, migration or production dependency changes. Synthetic databases and screenshots remain outside the repository. Changes remain uncommitted for independent review.

---

# 2026-09-05 — Windows Usability Check and F7 Shortcut

- Inspected native Windows renders at the initial size and 1000×700, with an available screen of 1600×852. Exercised creation, notes, resolution and Enter-to-open using Qt input events against an isolated database. Native visual/interaction check: PASS; this is agent inspection, not user acceptance testing.
- Adjusted the initial window size to leave room for Windows borders and the taskbar.
- Added the AutoHotkey v2 entry point and F7 launcher: focus/restore an existing window, otherwise start the project Python application. Repeated presses and pending startup retries avoid duplicate launches; startup/focus failures provide feedback.
- Live AutoHotkey checks: PASS, including cold launch, actual global F7 focus/restore, single shortcut instance, missing runtime and timeout/retry handling. GUI regression: PASS — 10 tests. Application/integration regression: PASS — 14 tests.
- No schema, service workflow, production dependency or login-startup changes.

---

# 2026-09-05 — Saved-Ticket Workspace Verification

- Completed verification of the saved-ticket queue, status filtering, paging, detail display, notes, history, resolution, closure and reopening through the application window and real service workers.
- Confirmed failed saves preserve drafts and failed detail loads preserve existing information. Committed writes retain success feedback when subsequent reads fail.
- Fixed creation recovery: if the first detail load fails after a successful save, the workspace explicitly reports creation and refreshes the queue for retry.
- Added nine integration tests using isolated SQLite databases, including integrity and foreign-key checks. Corrected a test-only connection cleanup issue found during the first run.
- Validation: PASS — 133 database tests, 10 GUI tests and 14 application/integration tests. Native Windows smoke validation: PASS.
- Preserved service-owned validation and transactions; no schema or dependency changes. F7 launch/focus is verified separately.

---

# 3. 2026-09-04 — Ticket Notes and Status Service Boundary

## Implementation

- Extended `TicketRepository` with frozen `TicketNoteRecord` results, note creation/reload/list operations, transaction-scoped current-ticket reads and narrow activity/lifecycle updates.
- Reserved repository writes with `BEGIN IMMEDIATE` before reading current ticket state, preserving configured busy-timeout and foreign-key behavior.
- Added `TicketService.add_note()` validation and atomic persistence of the note, a `NOTE_ADDED` event referencing its ID and the ticket activity timestamp. Notes preserve author, source and AI-origin metadata and can be added to closed or cancelled tickets.
- Added `TicketService.change_status()` to validate lifecycle transitions and atomically persist the ticket, status history and `STATUS_CHANGED` timeline event. `NEW` remains creation-only, resolved and closed tickets may reopen to `OPEN`, and `CANCELLED` is terminal.
- Required resolution text when resolving and saved a `RESOLUTION` note plus its timeline reference in the same transaction. Closing retains the resolution; reopening clears current lifecycle fields while preserving resolution notes, including a legacy-resolution snapshot when needed.
- Added missing-ticket validation and safe `TicketUpdateError` feedback for persistence failures. A resolution-typed note alone does not transition the ticket.
- Preserved the existing schema and kept notes/status GUI controls as the next interface slice.

## Validation

```text
Ticket activity repository tests: PASS — 11 tests
Ticket activity service tests: PASS — 17 tests
Full database suite: PASS — 129 tests
Existing GUI regression tests: PASS — 7 tests
Application and GUI integration tests: PASS — 5 tests
Notes/status GUI: NOT RUN — implementation remains planned
```

---

# 4. 2026-09-04 — PySide6 Application Shell and Ticket Creation GUI

## Architecture Decision

- Replaced PyQt6 with the explicitly approved PySide6 framework for the primary Python GUI.
- Pinned `PySide6==6.11.2`, verified it with Python 3.14.6, and installed it into the ignored project `.venv`.
- Selected the community distribution under its available LGPLv3/GPL licensing terms; packaging must preserve applicable notices and LGPL compliance.

## Implementation

- Added `TicketCreateWidget` with ticket number, subject, type, priority, optional company/contact/category references and description input.
- Added inline required-field feedback, safe persistence-error presentation, input preservation, `Ctrl+S`, duplicate-submit protection and created/failed signals.
- Kept the GUI dependent on `TicketService`; no SQL or workflow validation moved into the widget.
- Added service-level translation of SQLite failures into `TicketCreationError` so the GUI does not expose database details.
- Added the thin `python -m f7hub` entry point, central application bootstrap and minimal `QMainWindow` that composes `TicketRepository`, `TicketService` and `TicketCreateWidget`.
- Added a File/Exit action, ready/created status feedback, explicit development-database override and safe fatal-startup feedback.
- Kept the global F7 launch/focus hotkey in the later AutoHotkey slice.

## Validation

```text
Focused GUI tests: PASS — 7 tests
Application and GUI integration tests: PASS — 5 tests
Full database suite: PASS — 101 tests
Package entry point and startup failure path: PASS
Windows-platform visual render review: PASS
Development database isolation: PASS
```

---

# 5. 2026-09-04 — Ticket Persistence and Creation Service

## Implementation

- Added `TicketRepository` with frozen ticket, status-history and timeline records, parameterized ticket creation/reload, case-insensitive number lookup and stable activity retrieval.
- Added a repository transaction session so one service workflow can reuse a private configured SQLite connection without exposing SQL to the service or GUI.
- Added `TicketService` separately to validate ticket fields and references, generate ticket numbers when needed, and atomically create the ticket, initial `NEW` status history and `TICKET_CREATED` timeline event.
- Kept GUI, ticket editing, notes, status transitions and unrelated repositories outside this slice.

## Validation

```text
TicketRepository tests: PASS — 6 tests
TicketService tests: PASS — 5 tests
Full database suite: PASS — 101 tests
Ticket creation and reload: PASS
Required-field, enum and relationship validation: PASS
Parameterized SQL and database constraints: PASS
Transaction commit and forced-failure rollback: PASS
Development database isolation: PASS
```

---

# 6. 2026-09-04 — Knowledge Schema Migration

## Implementation

- Added `Database\Migrations\0005_knowledge.sql` with the canonical relational knowledge tables: articles, versions, links, article relationships, ticket/article links and article/tag links.
- Added the seven documented knowledge indexes and preserved canonical constraints and foreign-key delete behavior.
- Kept `knowledge_article_scripts` deferred until the scripts schema exists and kept FTS tables and synchronization triggers in the later FTS migration.
- Preserved the slice as schema-only: no repository, service, GUI, script schema or FTS implementation was added.

## Validation

```text
Focused knowledge migration tests: PASS — 11 tests
Full database suite: PASS — 90 tests
Migration ordering, checksum and idempotency: PASS
Knowledge constraints, defaults and foreign-key behavior: PASS
Owned-row cascades and category nullification: PASS
Failed knowledge migration rollback: PASS
PRAGMA integrity_check: PASS
PRAGMA foreign_key_check: PASS
Development database isolation: PASS
```

---

# 7. 2026-09-03 — Ticket Core Schema Migration

## Implementation

- Added `Database\Migrations\0004_tickets.sql` with the canonical `tickets`, `ticket_notes`, `ticket_status_history` and `ticket_timeline_events` tables.
- Added the nine documented ticket and ticket-detail indexes.
- Preserved nullable company, contact and category relationships through `ON DELETE SET NULL` and owned ticket-detail rows through `ON DELETE CASCADE`.
- Preserved the slice as schema-only: no repository, service, GUI, attachment, relationship, tagging or FTS implementation was added.

## Validation

```text
Focused ticket migration tests: PASS — 10 tests
Full database suite: PASS — 79 tests
Migration ordering, checksum and idempotency: PASS
Ticket constraints, defaults and foreign-key behavior: PASS
Owned-row cascade and nullable-reference delete behavior: PASS
Failed ticket migration rollback: PASS
PRAGMA integrity_check: PASS
PRAGMA foreign_key_check: PASS
Development database isolation: PASS
```

---

# 8. 2026-09-03 — Company and Contact Repositories

## Implementation

- Added `Python\f7hub\repositories\` with explicit `CompanyRepository` and `ContactRepository` persistence boundaries.
- Added frozen `CompanyRecord` and `ContactRecord` return values rather than exposing SQLite rows or cursors.
- Implemented parameterized create, read, stable list, update and activation-state operations, plus company-code lookup and contact filtering by company.
- Preserved the slice as repository-only: no production schema, migration, service, GUI, ticket or dependency change was added.

## Validation

```text
CompanyRepository tests: PASS — 5 tests
ContactRepository tests: PASS — 5 tests
Full database suite: PASS — 69 tests
Constraint and foreign-key behavior: PASS
Stable ordering and active filtering: PASS
SQL-looking input treated as data: PASS
Company deletion preserves contacts with a null company reference: PASS
```

---

# 9. 2026-09-03 — Company and Contact Schema Migration

## Implementation

- Added `Database\Migrations\0003_companies_contacts.sql` with the canonical `companies`, `company_notes`, `company_links` and `contacts` tables.
- Added the six documented company/contact indexes, including case-insensitive name/email lookup and descending company-note chronology.
- Implemented owned-row cascades for company notes and links while preserving contacts through `ON DELETE SET NULL`.
- Preserved the slice as schema-only: no seed data, repository, service, trigger, GUI or ticket table was added.
- Changed no production Python because the existing migration engine applied the new migration correctly.

## Validation

```text
Focused company/contact migration tests: PASS — 10 tests
Full database suite: PASS — 59 tests
Migration ordering, checksum and idempotency: PASS
Company/contact constraints and foreign-key behavior: PASS
Failed company/contact migration rollback: PASS
PRAGMA integrity_check: PASS
PRAGMA foreign_key_check: PASS
Development database isolation: PASS
```

---

# 10. 2026-09-03 — Taxonomy Schema Migration

## Implementation

- Added `Database\Migrations\0002_taxonomy.sql` with the canonical `categories` and `tags` tables.
- Added the documented parent-category and scope/active/sort indexes without adding redundant tag indexes.
- Preserved taxonomy as a schema-only slice: no seed data, repository, service, trigger, GUI or dependent business-domain table was added.
- Changed no production Python because the existing migration engine applied the new migration correctly.

## Validation

```text
Focused taxonomy migration tests: PASS — 9 tests
Full database suite: PASS — 49 tests
Migration ordering, checksum and idempotency: PASS
Taxonomy constraints and foreign-key behavior: PASS
Failed taxonomy migration rollback: PASS
PRAGMA integrity_check: PASS
PRAGMA foreign_key_check: PASS
Development database isolation: PASS
```

---

# 11. 2026-09-03 — First Versioned Core Migration

## Architecture Decision

- Established `schema_migrations` as bootstrap-owned migration-engine infrastructure created before versioned migrations run.
- Kept `schema_migrations` out of `0001_core.sql`, avoiding duplicate and circular ownership.

## Implementation

- Added `Database\Migrations\0001_core.sql` as the first versioned application-schema migration.
- Added only the canonical `application_metadata` table; no business-domain table, seed data, repository, service or GUI was added.
- Corrected the unreleased migration so `metadata_key TEXT NOT NULL PRIMARY KEY` enforces the documented required-key contract in SQLite.
- Added isolated permanent tests for fresh application, history recording, checksum validation, idempotency, exact structure, constraints, rollback and integrity.
- Changed no production Python infrastructure because the existing bootstrap behavior already implemented the correct ownership model.

## Validation

```text
Focused core-migration tests: PASS — 5 tests
Full database suite: PASS — 40 tests
PRAGMA integrity_check: PASS
PRAGMA foreign_key_check: PASS
NULL metadata_key rejection: PASS
Development database isolation: PASS
```

---

# 12. 2026-09-03 — Slice 001 Verification Follow-Ups

## Git State

- Confirmed the local Git repository is present on `main`.
- Confirmed the local baseline exists and two local commits were present at verification time.
- Confirmed `origin` is configured as `git@github.com:JDecelles1990/F7Hub.git`.
- Confirmed `origin/main` is not yet present; remote publication remains pending.
- Recorded that a focused pre-Slice-001 Git diff is unavailable because no earlier baseline commit exists.

## Regression Coverage

- Promoted seven independently verified SQLite migration behaviors into permanent `unittest` coverage.
- Added coverage for renamed migrations, quoted/comment semicolons, transaction-control denial, `ATTACH`/`DETACH` denial, rollback state, the exact migration-history structure, and its nonnegative execution-time constraint.
- Changed no production SQLite implementation because the permanent tests confirmed the existing behavior.

## Documentation

- Updated current Git status in `ROOT.md` and current Git/test readiness in `17_Todo.md`.
- Preserved earlier ChangeLog statements as historical observations rather than rewriting them as current state.

## Validation

```text
Permanent database infrastructure tests: PASS — 35 tests
Focused new regression tests: PASS — 7 tests
Production SQLite source changes: NONE
origin/main publication: PENDING
```

---

# 13. 2026-09-03 — SQLite Bootstrap and Migration Infrastructure

## Security Cleanup

- Removed the legacy raw ChatGPT browser export `Docs\Assets\ChatGPT - Scripting AHK V.2, PowerShell and PyQt6 F7Hub.html`.
- Removed its complete companion `Docs\Assets\ChatGPT - Scripting AHK V.2, PowerShell and PyQt6 F7Hub_files\` directory.
- Preserved standalone diagram PNG and SVG assets.
- A path-only high-confidence plaintext credential scan returned no remaining file paths.

## Implementation

- Added environment-independent development and installed-runtime database path resolution.
- Added controlled SQLite connection creation with mandatory foreign-key enforcement, configurable busy timeout and clean lifecycle handling.
- Added strict `NNNN_description.sql` discovery, numeric ordering and duplicate-version rejection.
- Added canonical `schema_migrations` initialization and SHA-256 history validation.
- Added atomic statement-by-statement migration execution without `executescript()`, including denial of migration-authored transaction control.
- Added idempotent bootstrap plus `integrity_check` and `foreign_key_check` helpers.
- Added no business-domain migration, repository, GUI or external integration.

## Validation

```text
Isolated database infrastructure tests: PASS — 28 tests
Connection PRAGMAs: PASS
Migration ordering and history validation: PASS
Checksum immutability: PASS
DDL/DML failure rollback: PASS
Integrity and foreign-key checks: PASS
Development database isolation: PASS
Mermaid visual validation: NOT RUN — not required by this slice
Git diff: BLOCKED — Git metadata is not present
```

The tests used temporary file-backed databases and did not create or modify `Database\Dev\f7hub_dev.db` or the legacy `Database\SQLite\F7Hub.db` scaffold.

---

# 14. 2026-09-02 — Documentation Consistency Review

## Scope

- Reviewed `AGENTS.md`, `ROOT.md`, and all canonical `Docs/00` through `Docs/19` Markdown files.
- Inspected repository structure only as needed to validate documentation claims.
- Made documentation-only corrections; no application code, migrations, dependencies or commits were created.

## Documentation Navigation

- Replaced the conversational, duplicated `ROOT.md` draft with a concise project entry point.
- Preserved the separate roles of `AGENTS.md`, `ROOT.md`, and `19_DocumentationIndex.md`.
- Added `ROOT.md` to the first-programming reading path.
- Recorded that project-local `.agents/skills\` are not currently present and are optional until justified.

## Architecture

- Preserved Python/PyQt6 as the primary application and GUI architecture.
- Preserved SQLite as the primary relational persistence layer.
- Preserved PowerShell 7 as the Windows and Microsoft administration, diagnostics and reporting layer.
- Preserved AutoHotkey v2 as the lightweight desktop-productivity layer.
- Aligned the early architecture sequence with the approved first task: SQLite bootstrap and migration infrastructure.
- Corrected target-tense wording that previously implied an application implementation already existed.

## Database

- Aligned `07_Database.md`, `08_ERD.md`, and `09_SQLSchema.md` around `schema_migrations` as the sole migration-state authority.
- Replaced stale potential entity lists in `07_Database.md` with references to the exact physical inventory owned by `09_SQLSchema.md`.
- Added missing `application_metadata` and `categories` entries to the ERD inventory.
- Marked `workspace_panels` and generic `external_entity_mappings` as deferred rather than baseline tables.
- Aligned ticket status examples with the schema values: `NEW`, `OPEN`, `IN_PROGRESS`, `WAITING`, `RESOLVED`, `CLOSED`, and `CANCELLED`.
- Removed a duplicate definition of `ux_diagnostic_steps_one_entry` from the documented DDL.
- Clarified that the first coding task does not include taxonomy, companies, contacts, tickets, repositories or GUI work.

## Naming and Structure

- Corrected the canonical project root in `01_Project.md` from the former OneDrive path to `C:\Dev\F7Hub\`.
- Documented the FTS5 trigger-name exception to the general trigger naming convention.
- Aligned migration filename examples with `0001_core.sql`, `0002_taxonomy.sql`, and `0003_companies_contacts.sql`.
- Corrected PowerShell test ownership from `PowerShell\Tests\` to `Tests\PowerShell\`.
- Removed ChatGPT drafting prefaces, outer Markdown fences and conversational postambles from canonical documents.
- Converted `06_SystemArchitecture.md` top-level numbered sections into navigable Markdown headings without changing its substantive body.

## Planning

- Corrected the Roadmap summary to match its actual Phase 0 through Phase 20 body.
- Aligned the first implementation recommendation throughout the documentation set.
- Replaced the duplicated 2,000-line Todo with a focused current action queue.
- Removed future implementation templates and plans from this ChangeLog.

## Verified Repository State

Repository inspection found:

```text
Python application implementation: PLANNED
PowerShell implementation: PLANNED
AutoHotkey implementation: PLANNED
Database migrations and repositories: PLANNED
Automated application tests: NOT RUN — no test implementation is present
Git baseline: NOT PRESENT
```

The existing `Database\SQLite\F7Hub.db` file is zero bytes and does not verify a database implementation.

`Tools\Scripts\Initialize-F7HubStructure.ps1` exists at the canonical location. Two older root-level PowerShell scripts still contain the obsolete OneDrive path and remain follow-up source-cleanup items. An empty noncanonical `zip\` directory is also present and remains a repository-cleanup decision.

## Validation

```text
Canonical file inventory: PASS
Markdown fence balance: PASS
Canonical cross-reference check: PASS
Stale canonical Markdown term/path scan: PASS
Database inventory alignment: PASS
Documented SQLite DDL execution: PASS
PRAGMA integrity_check on fresh in-memory schema: PASS
PRAGMA foreign_key_check on fresh in-memory schema: PASS
Application tests: NOT RUN
Git diff: BLOCKED — Git metadata is not present
No-index baseline diff review: PASS
```

The SQLite checks validate the documented DDL, not migrations or runtime application behavior.

---

# 15. 2026-09-02 — Canonical Architecture Baseline

The documentation baseline established these project decisions:

- F7Hub is a modular Windows IT Support and technician-productivity platform.
- The project begins as a modular monolith.
- Python/PyQt6 owns the primary desktop application, GUI and orchestration.
- SQLite owns application relational persistence through Python repositories.
- PowerShell 7 owns controlled Windows and Microsoft administration and diagnostics.
- AutoHotkey v2 owns hotkeys, hotstrings, clipboard helpers, launch/focus behavior and lightweight menus.
- AI is an optional assistant and not a privileged execution authority.
- External integrations begin with connect/read/display behavior before controlled updates or synchronization.
- Plugin architecture is deferred until real extension requirements exist.
- The canonical documentation set contains 20 files numbered `00` through `19`.
- `09_SQLSchema.md` owns the exact physical schema; `08_ERD.md` is conceptual and `07_Database.md` owns database design rules.
- The first implementation task is SQLite bootstrap and migration infrastructure.

---

# 16. Superseded Directions

The following earlier directions were replaced by the canonical architecture:

| Earlier direction | Current decision |
|---|---|
| OneDrive-based development root | `C:\Dev\F7Hub\` |
| PyQt6 | PySide6 |
| AutoHotkey as the primary GUI | AutoHotkey v2 as desktop productivity support |
| PowerShell as the primary application layer | PowerShell 7 as controlled administration and diagnostics |
| Direct PowerShell/AHK core database ownership | Python repository ownership |
| Arbitrary 100-table or 120-table target | Requirement-driven normalized schema |
| Early unrestricted plugin framework | Deferred until validated requirements |
| AI-controlled administration | Technician-controlled execution boundaries |
| One large implementation task | Small independently tested slices |

Archived documents and legacy diagrams do not override these decisions.

---

# 17. Maintenance Rule

Record only meaningful completed changes here.

For each entry:

1. state what changed
2. distinguish documentation from implementation
3. report actual validation using `PASS`, `FAIL`, `NOT RUN`, or `BLOCKED`
4. reference migrations for physical schema changes
5. leave future work in `16_Roadmap.md` or `17_Todo.md`

> The ChangeLog records what F7Hub became, not what it might become next.
