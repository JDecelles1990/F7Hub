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

Repository inspection and isolated database tests through 2026-09-05 found:

```text
Canonical Docs/00–19 files: PRESENT
Canonical top-level directories: PRESENT
Python SQLite infrastructure: VERIFIED
Company/contact repositories: VERIFIED
TicketRepository and TicketService creation boundary: VERIFIED
Ticket notes, status changes, resolution and reopening service boundary: VERIFIED
PySide6 ticket creation widget and vertical integration: VERIFIED
PySide6 application entry point, bootstrap and minimal main window: VERIFIED
Saved-ticket workspace and background service runner: VERIFIED
Remaining Python application implementation: PLANNED
PowerShell implementation: PLANNED
AutoHotkey F7 launch/focus shortcut: VERIFIED
Remaining AutoHotkey implementation: PLANNED
Migration infrastructure: VERIFIED
Business-domain migrations through 0005: VERIFIED
Remaining business-domain migrations and repositories: PLANNED
Isolated database tests: PASS — 133 tests
GUI tests: PASS — 10 tests
Application and GUI integration tests: PASS — 14 tests
Git baseline: PRESENT — local main; origin configured
Project-local .agents/skills/: NOT PRESENT
```

The existing `Database\SQLite\F7Hub.db` file is zero bytes and does not verify a database implementation.

`Tools\Scripts\Initialize-F7HubStructure.ps1` is present. Two older root-level PowerShell scripts still reference the former OneDrive location; they are legacy repository artifacts, not canonical architecture. An empty noncanonical `zip\` directory is also present and requires a repository-cleanup decision.

Documentation describes the target system. It does not prove that application behavior is implemented or verified.

---

# 4. Development Launch

From the project root, start the current development application with:

```powershell
$env:PYTHONPATH = "$PWD\Python"
.\.venv\Scripts\python.exe -m f7hub
```

This initializes `Database\Dev\f7hub_dev.db`, applies the available migrations and opens the application with New ticket and Saved tickets workflows. Open `AutoHotkey/F7Hub.ahk` with AutoHotkey v2 to enable F7. F7 launches F7Hub or focuses/restores its existing window. Exit or reload the shortcut from its tray icon. It runs only while that script is active; automatic login startup is not configured.

---

# 5. Technology Ownership

| Technology | Primary responsibility |
|---|---|
| Python / PySide6 | Primary desktop application, GUI, orchestration, services, repositories and integrations |
| SQLite | Primary persistent relational data store |
| PowerShell 7 | Windows and Microsoft administration, diagnostics, reporting and controlled automation |
| AutoHotkey v2 | Global hotkeys, hotstrings, clipboard helpers, launch/focus behavior and lightweight quick menus |

PySide6 is the primary GUI. AutoHotkey is not a second application framework.

Normal core SQLite writes flow through Python repositories. PowerShell and AutoHotkey do not independently own core application persistence.

---

# 6. Primary Architecture

F7Hub begins as a modular monolith with this dependency direction:

```text
PySide6 GUI
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
- Domain logic does not depend on PySide6, SQLite details or provider SDKs.
- Repositories own normal SQLite persistence.
- Gateways isolate PowerShell, files and external APIs.
- PowerShell returns structured results to Python.
- AI output is untrusted and cannot bypass technician-controlled execution.
- Plugin architecture remains deferred until validated extension requirements exist.

Detailed ownership belongs to the canonical architecture documents, not this file.

---

# 7. Source-of-Truth Priority

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

# 8. Project Navigation

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

# 9. Canonical Documentation

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

# 10. Repository Structure

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

# 11. Status Discipline

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

# 12. Implementation Sequence

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

Subsequent verified slices added taxonomy, company/contact schema and repositories, the ticket-core schema through `0004_tickets.sql`, the relational knowledge schema through `0005_knowledge.sql`, the ticket creation persistence/service boundary, the first PySide6 ticket creation form, and a thin application bootstrap with a minimal `QMainWindow`. The repository/service layer also supports ticket notes, status changes, resolution, closure and reopening with atomic history and timeline writes. These activity operations are exposed in the saved-ticket workspace and verified by automated GUI integration tests. The AutoHotkey F7 launch/focus shortcut is also verified. Knowledge repositories, PowerShell, remaining AutoHotkey features, AI, diagnostics and plugins remain planned.

The saved-ticket workspace now lets technicians open saved tickets, review history, add notes, resolve, close and reopen tickets. Failed saves preserve drafts; committed saves remain clearly reported when reload fails. Native Windows visual inspection and Qt input-event checks are PASS at the default size and 1000×700. F7 launch/focus is verified. The next approved slice is reference-aware company/contact ticket creation.

The exact task contract is defined in `AGENTS.md`; the wider sequence belongs to `Docs/16_Roadmap.md`.

---

# 13. Final Principle

F7Hub should become more understandable after every development cycle.

> Build the correct system, not the most code.
