# F7Hub

> Windows IT Support Technician Workspace

F7Hub is an actively developed modular Windows desktop application for MSP/helpdesk technicians. It brings ticket context, troubleshooting knowledge, controlled diagnostics, and technician productivity tools into one workspace.

This is my current flagship software-engineering project. It is developed with AI-assisted coding agents under explicit architecture rules, scoped feature slices, automated regression testing, documented review gates, and Git-based change control.

## What F7Hub solves

IT support work often requires technicians to jump between ticketing systems, notes, knowledge articles, diagnostic scripts, administrative tools, and reference material. F7Hub explores a local technician command center that keeps those workflows organized without trying to replace every external IT platform.

Current implemented areas include:

- Ticket creation and saved-ticket workflows
- Company, contact, category, priority, and type reference data
- Ticket notes, status transitions, resolution, closure, and reopening
- Searchable Knowledge content and technician reference material
- Controlled PowerShell diagnostic execution
- Local System, Network, and Windows Services diagnostic snapshots
- AltF7Hub troubleshooting guide integration
- AutoHotkey launch/focus and technician productivity shortcuts
- SQLite migrations, repositories, service boundaries, and history tracking
- Automated database, GUI, PowerShell, and integration testing
- Native Windows validation for supported GUI workflows

F7Hub remains under active development. Planned functionality is documented separately and is not presented here as completed functionality.

## Technology stack

| Technology | Role |
|---|---|
| Python | Core application logic and orchestration |
| PySide6 / Qt | Primary Windows desktop interface |
| SQLite | Relational persistence and local application data |
| PowerShell 7 | Windows diagnostics, administration, and controlled automation |
| AutoHotkey v2 | Global shortcuts, launch/focus behavior, and lightweight desktop automation |
| YAML / JSON | Structured reference data and interoperability contracts |
| Git / GitHub | Feature branches, pull requests, review, and integration history |

## Architecture

F7Hub is being developed as a modular monolith with explicit responsibility boundaries.

```text
PySide6 GUI
    ↓
Application Services
    ↓
Domain Logic
    ↓
Repositories / Gateways
    ↓
SQLite / PowerShell / External Boundaries
```

Key architectural rules include:

- GUI components do not own raw SQL or shell-command construction.
- Core SQLite writes flow through Python repositories.
- PowerShell execution is mediated through controlled service/gateway boundaries.
- AutoHotkey handles desktop automation rather than core application persistence.
- AI-generated output is treated as untrusted and cannot bypass technician-controlled execution.
- Documentation, implementation, and verification status are tracked separately.

See [ROOT.md](ROOT.md) for the project definition and [Docs/19_DocumentationIndex.md](Docs/19_DocumentationIndex.md) for the canonical documentation map.

## Engineering workflow

Development is organized around small, reviewable vertical slices rather than large one-shot implementations.

Typical workflow:

```text
Requirement
    ↓
Architecture / documentation check
    ↓
Focused implementation slice
    ↓
Automated tests
    ↓
Native validation when applicable
    ↓
Independent review
    ↓
Pull request
    ↓
Integration
    ↓
Documentation synchronization
```

The repository history intentionally preserves implementation reports, review evidence, regressions, corrections, and architectural decisions. The objective is not merely to generate code, but to keep changes inspectable and reproducible.

## AI-assisted development

F7Hub uses AI coding agents as part of the development workflow.

The agents operate within documented constraints covering:

- scope control
- architecture boundaries
- source-of-truth hierarchy
- test expectations
- security rules
- documentation synchronization
- independent review
- Git branch and pull-request discipline

AI assistance is therefore part of the implementation process, not a substitute for architecture, validation, or review.

## Current diagnostic capabilities

The current diagnostic framework includes a reviewed Local Baseline Diagnostics pack containing:

1. Windows System Snapshot
2. Network Snapshot
3. Windows Services Snapshot

Diagnostic execution uses PowerShell 7 through controlled Python boundaries with registration checks, exact-file verification, bounded execution, structured-result validation, and cleanup handling.

See [Docs/18_ChangeLog.md](Docs/18_ChangeLog.md) for implementation and validation history.

## AltF7Hub

F7Hub also integrates the AltF7Hub technician troubleshooting guide.

With AutoHotkey v2 running:

- `F7` launches or focuses F7Hub.
- `Alt+F7` opens the Help Desk & Interview Guide.
- The guide provides keyboard-driven access to troubleshooting reference material.

Detailed guide behavior is documented in [AutoHotkey/Troubleshooting_Sections/README.md](AutoHotkey/Troubleshooting_Sections/README.md).

## Project documentation

F7Hub uses a structured documentation system rather than a single oversized specification.

Useful starting points:

- [ROOT.md](ROOT.md) - project definition, architecture overview, and local launch information
- [AGENTS.md](AGENTS.md) - coding-agent operating rules
- [Docs/19_DocumentationIndex.md](Docs/19_DocumentationIndex.md) - canonical documentation map
- [Docs/06_SystemArchitecture.md](Docs/06_SystemArchitecture.md) - system architecture
- [Docs/07_Database.md](Docs/07_Database.md) - SQLite architecture
- [Docs/12_PowerShellArchitecture.md](Docs/12_PowerShellArchitecture.md) - PowerShell boundaries
- [Docs/13_PythonArchitecture.md](Docs/13_PythonArchitecture.md) - Python/PySide6 architecture
- [Docs/18_ChangeLog.md](Docs/18_ChangeLog.md) - implemented changes and validation history

## Development launch

From the repository root:

```powershell
$env:PYTHONPATH = "$PWD\Python"
.\.venv\Scripts\python.exe -m f7hub
```

To enable the global F7/Alt+F7 behaviors, run:

```text
AutoHotkey/F7Hub.ahk
```

with AutoHotkey v2.

For fuller setup and repository guidance, use [ROOT.md](ROOT.md).

## Project status

F7Hub is an active personal engineering and IT-support productivity project. It is not presented as finished enterprise production software.

The repository deliberately distinguishes:

```text
documented
implemented
verified
planned
```

so that future functionality is not confused with completed functionality.

## Author

Jonathan Decelles  
Bilingual IT Support Helpdesk Technical Analyst  
Québec, Canada

- [LinkedIn](https://www.linkedin.com/in/JonathanDecelles)
- [GitHub](https://github.com/JDecelles1990)
