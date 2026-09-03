# F7Hub Root Project Definition

> File: `ROOT.md`  
> Project: F7Hub  
> Project Root: `C:\Dev\F7Hub\`  
> Purpose: Provide the concise project entry point for humans and coding agents.
> Status: `REVIEW`

---

# 1. What F7Hub Is

F7Hub is a modular Windows IT Support and technician-productivity platform.

Its purpose is to centralize technician context and make common support work easier to understand and control, including:

- tickets and company/contact context
- knowledge retrieval and reuse
- troubleshooting and diagnostics
- controlled PowerShell automation
- Microsoft administration
- search, clipboard and prompt productivity
- reporting and AI-assisted support

F7Hub is a technician command center. It is not intended to replace every external IT platform.

---

# 2. Canonical Project Root

The canonical development root is:

```text
C:\Dev\F7Hub\
```

Production runtime behavior must not depend permanently on this development path.

---

# 3. Verified Current State

Repository inspection performed on 2026-09-03 found:

```text
Canonical Docs/00–19 files: PRESENT
Canonical top-level directories: PRESENT
Python SQLite infrastructure: VERIFIED
Remaining Python application implementation: PLANNED
PowerShell implementation: PLANNED
AutoHotkey implementation: PLANNED
Migration infrastructure: VERIFIED
Business-domain migrations and repositories: PLANNED
Isolated database tests: PASS — 28 tests
Git baseline: PRESENT — local main; origin configured
Project-local .agents/skills/: NOT PRESENT
```

The existing `Database\SQLite\F7Hub.db` file is zero bytes and does not verify a database implementation.

`Tools\Scripts\Initialize-F7HubStructure.ps1` is present. Two older root-level PowerShell scripts still reference the former OneDrive location; they are legacy repository artifacts, not canonical architecture. An empty noncanonical `zip\` directory is also present and requires a repository-cleanup decision.

Documentation describes the target system. It does not prove that application behavior is implemented or verified.

---

# 4. Technology Ownership

| Technology | Primary responsibility |
|---|---|
| Python / PyQt6 | Primary desktop application, GUI, orchestration, services, repositories and integrations |
| SQLite | Primary persistent relational data store |
| PowerShell 7 | Windows and Microsoft administration, diagnostics, reporting and controlled automation |
| AutoHotkey v2 | Global hotkeys, hotstrings, clipboard helpers, launch/focus behavior and lightweight quick menus |

PyQt6 is the primary GUI. AutoHotkey is not a second application framework.

Normal core SQLite writes flow through Python repositories. PowerShell and AutoHotkey do not independently own core application persistence.

---

# 5. Primary Architecture

F7Hub begins as a modular monolith with this dependency direction:

```text
PyQt6 GUI
    ↓
Application Services
    ↓
Domain Logic
    ↓
Repositories / Gateways
    ↓
Infrastructure
```

Key boundaries:

- GUI components do not own raw SQL, migrations or shell-command construction.
- Domain logic does not depend on PyQt6, SQLite details or provider SDKs.
- Repositories own normal SQLite persistence.
- Gateways isolate PowerShell, files and external APIs.
- PowerShell returns structured results to Python.
- AI output is untrusted and cannot bypass technician-controlled execution.
- Plugin architecture remains deferred until validated extension requirements exist.

Detailed ownership belongs to the canonical architecture documents, not this file.

---

# 6. Source-of-Truth Priority

When project information conflicts, use:

```text
1. Explicit user requirement
2. Explicitly approved architectural decision
3. Current canonical project documentation
4. Validated implementation
5. Passing tests
6. Established project conventions
7. Engineering inference
```

Surface material conflicts rather than resolving them silently.

---

# 7. Project Navigation

For significant work, follow:

```text
AGENTS.md
    ↓
ROOT.md
    ↓
Docs/19_DocumentationIndex.md
    ↓
Relevant canonical documents
    ↓
Relevant project-local skills, if present
    ↓
Repository inspection
    ↓
Relevant tests
```

The roles are intentionally separate:

```text
AGENTS.md
→ HOW coding agents work

ROOT.md
→ WHAT F7Hub is and where to begin

Docs/19_DocumentationIndex.md
→ WHICH documents apply to a task and which document owns a decision
```

Do not read all canonical documents for every task. Use the index to select the minimum sufficient set.

---

# 8. Canonical Documentation

F7Hub has 20 canonical Markdown documents numbered `00` through `19`, stored directly under `Docs\`.

Their ownership and routing are authoritative in:

```text
Docs/19_DocumentationIndex.md
```

Important database authority is deliberately split:

```text
Docs/07_Database.md
→ database rules and strategy

Docs/08_ERD.md
→ conceptual entities and relationships

Docs/09_SQLSchema.md
→ exact physical SQLite schema
```

Planning authority is also separated:

```text
Docs/16_Roadmap.md
→ long-term sequence

Docs/17_Todo.md
→ current actionable work

Docs/18_ChangeLog.md
→ meaningful completed changes
```

---

# 9. Repository Structure

Canonical top-level directories are:

```text
AutoHotkey\
PowerShell\
Python\
Database\
Config\
Data\
Docs\
Plugins\
Tests\
Assets\
Build\
Installer\
Logs\
Releases\
Tools\
```

Exact folder ownership belongs to `Docs/10_FolderStructure.md`. Do not create speculative folder trees merely because they are conceivable.

---

# 10. Status Discipline

Documentation status and implementation status are separate.

Documentation statuses:

```text
DRAFT
REVIEW
APPROVED
DEPRECATED
ARCHIVED
```

Product or implementation statuses:

```text
PLANNED
IN PROGRESS
IMPLEMENTED
VERIFIED
DEFERRED
REJECTED
NOT VERIFIED
```

Test and validation statuses:

```text
PASS
FAIL
NOT RUN
BLOCKED
```

Do not equate documented or approved architecture with implemented or verified behavior.

---

# 11. Implementation Sequence

The first coding task was completed and verified on 2026-09-03:

```text
SQLite bootstrap and migration infrastructure
```

Verified scope:

- database connection creation
- `PRAGMA foreign_keys = ON`
- busy-timeout configuration
- `schema_migrations` tracking
- migration discovery and ordering
- checksum validation
- transactional migration execution
- isolated database tests

No business-domain migration was added. Taxonomy, companies, contacts, tickets, GUI, PowerShell, AutoHotkey, AI, diagnostics and plugins remain outside the completed first task.

The next independently reviewed implementation slice is taxonomy, companies and contacts persistence with its focused migrations, repositories, validation and tests.

The exact task contract is defined in `AGENTS.md`; the wider sequence belongs to `Docs/16_Roadmap.md`.

---

# 12. Final Principle

F7Hub should become more understandable after every development cycle.

> Build the correct system, not the most code.
