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

# 3. 2026-09-03 — Company and Contact Repositories

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

# 4. 2026-09-03 — Company and Contact Schema Migration

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

# 5. 2026-09-03 — Taxonomy Schema Migration

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

# 6. 2026-09-03 — First Versioned Core Migration

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

# 7. 2026-09-03 — Slice 001 Verification Follow-Ups

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

# 8. 2026-09-03 — SQLite Bootstrap and Migration Infrastructure

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

# 9. 2026-09-02 — Documentation Consistency Review

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

# 10. 2026-09-02 — Canonical Architecture Baseline

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

# 11. Superseded Directions

The following earlier directions were replaced by the canonical architecture:

| Earlier direction | Current decision |
|---|---|
| OneDrive-based development root | `C:\Dev\F7Hub\` |
| PySide6 | PyQt6 |
| AutoHotkey as the primary GUI | AutoHotkey v2 as desktop productivity support |
| PowerShell as the primary application layer | PowerShell 7 as controlled administration and diagnostics |
| Direct PowerShell/AHK core database ownership | Python repository ownership |
| Arbitrary 100-table or 120-table target | Requirement-driven normalized schema |
| Early unrestricted plugin framework | Deferred until validated requirements |
| AI-controlled administration | Technician-controlled execution boundaries |
| One large implementation task | Small independently tested slices |

Archived documents and legacy diagrams do not override these decisions.

---

# 12. Maintenance Rule

Record only meaningful completed changes here.

For each entry:

1. state what changed
2. distinguish documentation from implementation
3. report actual validation using `PASS`, `FAIL`, `NOT RUN`, or `BLOCKED`
4. reference migrations for physical schema changes
5. leave future work in `16_Roadmap.md` or `17_Todo.md`

> The ChangeLog records what F7Hub became, not what it might become next.
