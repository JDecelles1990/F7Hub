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

Repository inspection and tests on 2026-09-03 confirmed:

```text
Documentation consistency review: IN PROGRESS
SQLite migration infrastructure: VERIFIED
Core application migration — 0001_core.sql: VERIFIED
Taxonomy migration — 0002_taxonomy.sql: VERIFIED
Company/contact migration — 0003_companies_contacts.sql: VERIFIED
Remaining business-domain migrations: PLANNED
Permanent isolated database tests: PASS — 59 tests
Local Git repository and baseline: PRESENT
Remote origin: CONFIGURED
origin/main publication: PENDING
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
- [ ] Review and populate `.gitignore` before remote publication.
- [ ] Exclude runtime databases, logs, secrets, caches and generated artifacts as appropriate.
- [ ] Review the local baseline file set for sensitive or obsolete content before publication.
- [ ] Publish local `main` to `origin/main` only with explicit user authorization.

This task must not commit or push.

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
- PyQt6 GUI
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

# 8. P1 — Fourth Persistence Slice: Tickets

After taxonomy, companies and contacts are tested:

- [ ] Implement ticket creation persistence.
- [ ] Implement `TicketRepository` and `TicketService` validation.
- [ ] Create initial status history transactionally with the ticket where required.
- [ ] Test constraints, foreign keys, rollback and reload behavior.

The minimal PyQt6 ticket workflow follows as a separate slice using the tested service boundary.

---

# 9. Repository Follow-Ups

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

# 10. Deferred Work

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

# 11. Rejected Directions

The following remain `REJECTED` unless an explicitly approved architecture change revisits them:

- AutoHotkey as the primary GUI
- PowerShell as the primary application layer
- direct PowerShell or AutoHotkey ownership of core SQLite persistence
- arbitrary 100-table or 120-table targets
- AI directly executing arbitrary commands
- building the entire application in one coding task

---

# 12. Maintenance Rule

Keep this file short and actionable.

When work is completed:

1. remove it from the active queue or mark the checklist item complete
2. record meaningful completed changes in `18_ChangeLog.md`
3. update `16_Roadmap.md` only when milestone sequencing changes
4. keep implementation and test status truthful

> The Todo should make the next useful task obvious without reproducing the Roadmap.
