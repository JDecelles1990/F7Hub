# F7Hub Project Information

> Document: `Docs/01_Project.md`  
> Project: F7Hub  
> Purpose: Define what F7Hub is as a software project, including its scope, technology stack, development environment, repository conventions, versioning and project-level success criteria.  
> Related Vision: `Docs/00_ProjectVision.md`

---

# 1. Project Identity

| Property | Value |
|---|---|
| Project Name | F7Hub |
| Project Type | Modular Windows IT Support and Technician Productivity Platform |
| Primary Platform | Windows 11 |
| Primary GUI Framework | Python / PyQt6 |
| Automation Technologies | PowerShell 7 and AutoHotkey v2 |
| Database | SQLite |
| Primary Domain | IT Support, Helpdesk, MSP Operations and Microsoft 365 Administration |
| Development Model | Documentation-driven, modular and iterative |
| Repository Type | Local development directory; Git baseline is not currently present |
| Project Root | `C:\Dev\F7Hub\` |
| Author | Jonathan Decelles |
| Current Phase | Documentation consistency review before initial implementation |
| Current Stability | Pre-release / development |

This document describes the F7Hub project itself.

The broader reason F7Hub exists and what it should ultimately become are defined in:

`Docs/00_ProjectVision.md`

---

# 2. Project Description

F7Hub is a modular Windows desktop application designed to centralize common IT support workflows within a single technician-oriented workspace.

It is intended to connect and organize functions such as:

- ticket context
- troubleshooting workflows
- knowledge management
- PowerShell automation
- Windows desktop automation
- script management
- diagnostics
- clipboard utilities
- search
- Microsoft 365 administration
- documentation
- company and contact context
- AI-assisted support
- reporting
- plugins
- technical utilities

F7Hub is not intended to replace every external support platform.

Instead, it provides a central command environment that helps technicians interact with those platforms efficiently.

---

# 3. Project Mission

The project's mission is to build a maintainable technician workspace that reduces fragmentation during IT support work.

F7Hub should help a technician move through the following lifecycle:

```text
Ticket / Request
      │
      ▼
Understand Context
      │
      ▼
Search Knowledge
      │
      ▼
Troubleshoot
      │
      ▼
Run Diagnostics
      │
      ▼
Use Automation
      │
      ▼
Resolve or Escalate
      │
      ▼
Document
      │
      ▼
Preserve Knowledge
```

The application should make these transitions faster without obscuring what the system is doing.

---

# 4. Technology Stack

F7Hub intentionally uses multiple technologies.

Each technology should remain focused on the tasks for which it is best suited.

## 4.1 Primary Technologies

### Python

Primary application language for the advanced desktop application layer.

Typical responsibilities:

- application startup
- application services
- domain coordination
- repositories
- database access
- search orchestration
- plugin management
- state management
- GUI integration
- reporting
- cross-module coordination

---

### PyQt6

Primary graphical user interface framework.

Typical responsibilities:

- main application window
- navigation
- dockable panels
- dialogs
- forms
- data views
- workspaces
- context panels
- editors
- command palette
- terminal/output interfaces
- GUI state management

Detailed architecture:

`Docs/13_PythonArchitecture.md`

---

### SQLite

Primary persistent relational database.

Typical responsibilities:

- application data
- ticket-related records
- companies
- contacts
- knowledge metadata
- script metadata
- diagnostic definitions
- diagnostic results
- prompts
- application settings
- bookmarks
- workspace definitions
- execution history
- searchable content
- audit information

Detailed architecture:

- `Docs/07_Database.md`
- `Docs/08_ERD.md`
- `Docs/09_SQLSchema.md`

---

### PowerShell 7

Primary Windows and Microsoft administration automation technology.

Typical responsibilities:

- Windows diagnostics
- Microsoft 365 administration
- Exchange Online
- Microsoft Graph
- Entra ID
- Intune
- Microsoft Defender
- networking diagnostics
- system information
- reporting
- structured diagnostic scripts
- administrative automation

Detailed architecture:

`Docs/12_PowerShellArchitecture.md`

---

### AutoHotkey v2

Primary Windows desktop automation technology.

Typical responsibilities:

- global hotkeys
- hotstrings
- clipboard automation
- text insertion
- application launching
- popup menus
- quick commands
- lightweight Windows interaction
- productivity shortcuts

Detailed architecture:

`Docs/11_AHKArchitecture.md`

---

# 5. Supporting Technologies

F7Hub may use additional technologies where justified.

These may include:

- JSON
- YAML
- Markdown
- Mermaid
- SQL
- HTML
- CSS
- REST APIs
- Microsoft Graph
- Git
- GitHub
- Python virtual environments
- PowerShell modules
- Qt Designer
- SQLite FTS5

The presence of a technology in this document does not automatically mean it is currently implemented.

---

# 6. External Platforms

F7Hub may integrate with or provide shortcuts to external platforms such as:

## Microsoft

- Microsoft 365
- Microsoft Entra ID
- Exchange Online
- Microsoft Graph
- Microsoft Intune
- Microsoft Defender
- Microsoft Teams
- SharePoint Online
- OneDrive
- Microsoft Learn

## MSP / IT Operations

- HaloPSA
- NinjaOne / NinjaRMM
- Keeper

## Productivity and Development

- Visual Studio Code
- OneNote
- Microsoft Edge
- Windows Terminal
- PowerShell
- File Explorer
- Windows administrative tools

External platform integrations require their own implementation and security review.

Their presence here represents project scope, not verified integration status.

---

# 7. Development Environment

## Operating System

Primary development operating system:

```text
Windows 11
```

F7Hub is currently a Windows-first project.

Cross-platform compatibility is not a primary requirement because significant functionality depends on Windows-specific technologies such as:

- AutoHotkey
- PowerShell
- Windows administration
- Microsoft desktop environments
- Windows APIs
- Windows-specific utilities

---

# 8. Development Tools

Primary development tools may include:

```text
Visual Studio Code
PowerShell 7
Python
PyQt6
Qt Designer
SQLite
DB Browser for SQLite
Git
GitHub
Windows Terminal
Markdown
Mermaid
OpenAI Codex
ChatGPT
```

Additional tools may be introduced when justified by a documented requirement.

Major framework or dependency changes require architectural review.

---

# 9. Development Methodology

F7Hub follows an incremental engineering workflow.

```text
UNDERSTAND
    ↓
INSPECT
    ↓
PLAN
    ↓
IMPLEMENT
    ↓
TEST
    ↓
REVIEW
    ↓
DOCUMENT
```

The project should be built through small, independently testable slices.

Large prompts such as:

> Build F7Hub.

should not be used as the normal implementation strategy.

Prefer focused tasks such as:

> Implement SQLite persistence for ticket creation, including migration, repository, validation and tests.

---

# 10. Inspect Before Creating

Before introducing a new:

- table
- entity
- class
- service
- repository
- utility
- module
- API
- configuration system
- script registry
- plugin
- abstraction

development should first determine whether an equivalent component already exists.

The required process is:

```text
SEARCH
   ↓
IDENTIFY
   ↓
REUSE OR EXTEND
   ↓
CREATE ONLY IF NECESSARY
```

This rule helps control architectural duplication.

---

# 11. Repository Root

Canonical project root:

```text
C:\Dev\F7Hub\
```

The project root should remain stable unless repository restructuring is explicitly approved.

---

# 12. Top-Level Repository Structure

The canonical top-level structure is:

```text
F7Hub\
│
├── AutoHotkey\
├── PowerShell\
├── Python\
├── Database\
├── Config\
├── Data\
├── Docs\
├── Plugins\
├── Tests\
├── Assets\
├── Build\
├── Installer\
├── Logs\
├── Releases\
└── Tools\
```

Detailed folder organization belongs in:

`Docs/10_FolderStructure.md`

This file should not duplicate the complete repository tree.

---

# 13. Repository Philosophy

The repository should remain understandable from its structure.

Source code, documentation, generated files, user data and build artifacts should not be mixed without reason.

General responsibilities:

```text
AutoHotkey\
→ AHK v2 source and desktop automation

PowerShell\
→ PowerShell automation and administration scripts

Python\
→ Python application and PyQt6 source

Database\
→ SQLite schema, migrations and database tooling

Config\
→ Application configuration

Data\
→ Application data, import and export content

Docs\
→ Project documentation and diagrams

Plugins\
→ Plugin implementations and plugin metadata

Tests\
→ Automated tests and validation resources

Assets\
→ Icons, graphics, templates and application resources

Build\
→ Intermediate build artifacts

Installer\
→ Installer definitions and packaging

Logs\
→ Development/runtime logs where applicable

Releases\
→ Release packages and release records

Tools\
→ Development and maintenance utilities
```

Generated data should not be confused with source files.

---

# 14. Source Control

Git should be used to preserve project history.

Source control should support:

- incremental development
- rollback
- code review
- experimentation
- branching
- release tracking
- documentation history
- migration history

The repository should avoid committing:

- passwords
- API keys
- authentication tokens
- refresh tokens
- private keys
- customer credentials
- sensitive ticket data
- temporary build files
- unnecessary logs
- local caches
- virtual environments

A suitable `.gitignore` should be maintained.

---

# 15. Branching Strategy

F7Hub should initially use a simple branching model.

Recommended branches:

```text
main
│
├── feature/*
├── fix/*
├── docs/*
├── refactor/*
└── experiment/*
```

## `main`

Represents the latest reviewed project state considered sufficiently stable for the current development phase.

## `feature/*`

Used for focused new functionality.

Example:

```text
feature/ticket-persistence
feature/sqlite-migrations
feature/diagnostic-workflows
```

## `fix/*`

Used for focused bug fixes.

Example:

```text
fix/database-foreign-keys
```

## `docs/*`

Used for significant documentation work where separate review is useful.

## `experiment/*`

Used for prototypes that may never become part of the production architecture.

The branching strategy should remain simple until project complexity actually requires something more sophisticated.

---

# 16. Versioning

F7Hub should use Semantic Versioning where practical.

Format:

```text
MAJOR.MINOR.PATCH
```

Example:

```text
0.1.0
```

Meaning:

```text
MAJOR
→ incompatible architectural or product changes

MINOR
→ backward-compatible features or substantial capability additions

PATCH
→ backward-compatible fixes
```

---

# 17. Pre-Release Versioning

During early development, versions may use pre-release labels.

Examples:

```text
0.1.0-alpha
0.1.0-alpha.1
0.2.0-alpha
0.5.0-beta
1.0.0-rc.1
1.0.0
```

Approximate interpretation:

```text
alpha
→ architecture and features are still changing substantially

beta
→ primary capabilities exist but require broader validation

rc
→ release candidate

1.0.0
→ first stable production-quality release
```

Version numbers must reflect actual project maturity rather than desired maturity.

---

# 18. Release Management

Releases should eventually record:

- version
- release date
- significant features
- fixes
- migrations
- compatibility requirements
- known issues
- installation requirements
- upgrade instructions

Release information should remain synchronized with:

- `Docs/16_Roadmap.md`
- `Docs/17_Todo.md`
- `Docs/18_ChangeLog.md`

Release packages belong under:

```text
Releases\
```

Packaging and installer files belong under:

```text
Build\
Installer\
```

---

# 19. License

Current license status:

```text
PLANNED
```

A license should be selected before public distribution of F7Hub source code or packaged releases.

Possible considerations include:

- private/proprietary development
- open-source distribution
- third-party library licenses
- PyQt6 licensing requirements
- bundled tool licenses
- icons and visual asset licenses
- Microsoft API terms
- external platform terms

The selected license must be documented before F7Hub is publicly released.

---

# 20. Author Information

```text
Project Author:
Jonathan Decelles

Role:
Project creator, designer and primary developer

Project:
F7Hub
```

Additional contributors may be documented in the future.

AI coding tools should not be treated as human project authors.

They may be documented separately as development tools where appropriate.

---

# 21. Development Roles

During development, responsibilities may conceptually be separated into:

```text
Product Owner
→ Defines requirements and priorities

Software Architecture
→ Defines system boundaries and technical decisions

Implementation
→ Builds approved vertical slices

Testing
→ Validates behavior and failure paths

Review
→ Examines correctness, security and maintainability

Documentation
→ Synchronizes architecture and implementation knowledge
```

Initially, several or all of these responsibilities may be performed by the same developer with AI assistance.

The separation still matters because each development activity requires different reasoning.

---

# 22. AI-Assisted Development

F7Hub may be developed with assistance from coding agents and LLMs such as:

- OpenAI Codex
- ChatGPT
- other approved development assistants

AI-generated code is not automatically trusted.

AI output must be reviewed for:

- correctness
- architectural consistency
- security
- duplication
- error handling
- database integrity
- test coverage
- documentation impact

Coding agents should receive focused tasks containing:

```text
OBJECTIVE
CONTEXT
SCOPE
OUT OF SCOPE
CONSTRAINTS
ACCEPTANCE CRITERIA
VALIDATION
DELIVERABLES
```

Agents should inspect relevant project documentation before significant implementation work.

---

# 23. Project Documentation

F7Hub uses Markdown as the primary documentation format.

Architecture and workflow diagrams may use Mermaid.

The canonical documentation directory is:

```text
Docs\
```

The documentation set includes:

```text
00_ProjectVision.md
01_Project.md
02_ProductRequirements.md
03_Features.md
04_UserWorkflows.md
05_GUI.md
06_SystemArchitecture.md
07_Database.md
08_ERD.md
09_SQLSchema.md
10_FolderStructure.md
11_AHKArchitecture.md
12_PowerShellArchitecture.md
13_PythonArchitecture.md
14_DesignPrinciples.md
15_NamingConventions.md
16_Roadmap.md
17_Todo.md
18_ChangeLog.md
19_DocumentationIndex.md
```

`19_DocumentationIndex.md` should help humans and coding agents determine which documents must be inspected for a given type of task.

---

# 24. Documentation Hierarchy

The project documents answer different questions.

```text
00_ProjectVision.md
→ Why does F7Hub exist?

01_Project.md
→ What is the project?

02_ProductRequirements.md
→ What must it accomplish?

03_Features.md
→ What capabilities should exist?

04_UserWorkflows.md
→ How does the technician use it?

05_GUI.md
→ How should the interface behave?

06_SystemArchitecture.md
→ How do components interact?

07_Database.md
→ How is persistent information designed?

08_ERD.md
→ How are database entities related?

09_SQLSchema.md
→ How is the SQLite schema implemented?

10_FolderStructure.md
→ How is the repository organized?

11_AHKArchitecture.md
→ What belongs to AutoHotkey?

12_PowerShellArchitecture.md
→ What belongs to PowerShell?

13_PythonArchitecture.md
→ What belongs to Python / PyQt6?

14_DesignPrinciples.md
→ What engineering principles apply?

15_NamingConventions.md
→ How should things be named?

16_Roadmap.md
→ What should be developed and in what sequence?

17_Todo.md
→ What work remains active?

18_ChangeLog.md
→ What verified changes occurred?

19_DocumentationIndex.md
→ Which documents should be consulted for each task?
```

---

# 25. Development Source of Truth

When project information conflicts, use the following priority:

1. Explicit user requirement
2. Approved architecture
3. Project documentation
4. Validated implementation
5. Tests
6. Established conventions
7. Engineering inference

Unknown state must remain explicitly unknown.

Do not silently convert assumptions into project facts.

---

# 26. Scope

F7Hub has a broad long-term vision, but implementation must remain incremental.

---

# 27. In Scope

Core project scope includes:

## Desktop Application

- Python desktop application
- PyQt6 GUI
- navigation
- workspaces
- dockable panels
- settings
- context panels

## Ticket Support

- ticket workspace
- ticket notes
- ticket timelines
- ticket-related data
- ticket context
- ticket search
- integration opportunities with external PSA systems

## Companies and Contacts

- company information
- contacts
- contextual support information
- relationships to tickets and technical resources

## Knowledge Management

- KB articles
- troubleshooting procedures
- SOPs
- known errors
- tags
- categories
- searchable technical information

## Database

- SQLite
- relational data
- migrations
- normalization
- indexing
- constraints
- transactions
- FTS5 where appropriate

## Automation

- PowerShell scripts
- AutoHotkey v2
- script metadata
- script execution
- structured diagnostics
- parameter collection

## Microsoft Administration

Potential integration with:

- Microsoft 365
- Microsoft Graph
- Exchange Online
- Entra ID
- Intune
- Defender
- Teams
- SharePoint

## Clipboard

- clipboard history
- snippets
- templates
- transformations
- ticket-note assistance

## Search

- universal F7Hub search
- local content search
- structured filtering
- full-text search

## AI Assistance

- ticket summarization
- troubleshooting suggestions
- prompt generation
- KB assistance
- script explanation
- script review
- structured extraction

## Plugins

- controlled extensibility
- future module integration

## Reporting

- diagnostic reports
- execution reports
- support-related reports
- application metrics where appropriate

## Documentation

- Markdown documentation
- Mermaid diagrams
- architecture documentation
- developer instructions

---

# 28. Out of Scope for Initial Releases

The following are not primary requirements for early F7Hub releases:

- replacement of HaloPSA
- replacement of NinjaRMM/NinjaOne
- replacement of Microsoft admin portals
- replacement of Microsoft Entra ID
- replacement of Exchange Online
- replacement of Intune
- replacement of Microsoft Defender
- enterprise-scale multi-tenant backend infrastructure
- public SaaS hosting
- mobile applications
- macOS support
- Linux desktop support
- unattended autonomous administration
- automatic execution of destructive AI-generated commands
- enterprise identity provider implementation
- custom remote desktop platform
- full password manager replacement
- recreation of existing mature external tools

Integration is preferred over unnecessary reimplementation.

---

# 29. Offline and Online Capabilities

F7Hub should provide useful local functionality even when external systems are unavailable.

Potential offline capabilities include:

- local SQLite data
- local KB search
- script library access
- prompt library access
- clipboard tools
- notes
- application configuration
- local documentation
- workspace management

Some functionality inherently requires connectivity.

Examples:

- Microsoft Graph
- Exchange Online
- Entra ID
- Intune
- Defender
- HaloPSA
- cloud AI providers
- external KB sources
- remote administration

Therefore F7Hub is better described as:

> Local-first where practical, connected where required.

rather than strictly offline-first.

---

# 30. Configuration Philosophy

Configuration should be preferred over hard-coded environment-specific behavior.

Configuration may include:

- file paths
- feature flags
- URLs
- application preferences
- workspace settings
- module settings
- integration settings
- logging settings
- theme settings

Configuration files must not contain sensitive secrets unless an approved secure storage mechanism is explicitly designed.

---

# 31. Data Ownership

Local F7Hub data should remain understandable and accessible.

Where appropriate:

- structured data belongs in SQLite
- configuration belongs in configuration files
- source code belongs in the repository
- scripts remain version-controlled files
- logs belong in logs
- exports belong in data/export locations
- documentation belongs in Docs

The database should not be used merely as a container for every file type.

For example, full PowerShell source scripts should generally remain stored as files while SQLite stores metadata and execution records.

---

# 32. Modularity

F7Hub should maintain clear subsystem boundaries.

Preferred conceptual structure:

```text
GUI
 ↓
Application / Services
 ↓
Domain Logic
 ↓
Repositories / Gateways
 ↓
Infrastructure
```

Infrastructure may include:

```text
SQLite
PowerShell
AutoHotkey
Files
Microsoft Graph
External APIs
Plugins
```

GUI code should not become the location where business rules, SQL queries and PowerShell orchestration are all mixed together.

---

# 33. Security Principles

F7Hub may execute administrative tasks.

Security requirements therefore include:

- least privilege
- secure defaults
- input validation
- parameterized SQL
- safe subprocess handling
- restricted secrets storage
- controlled script execution
- sanitization of sensitive logs
- explicit authorization
- review of AI-generated commands
- dependency review
- plugin boundaries

Inputs from external systems must be treated as untrusted.

---

# 34. Database Principles

SQLite is foundational to F7Hub.

Database development should preserve:

- primary keys
- foreign keys
- constraints
- normalization
- indexes
- transactions
- migrations
- query performance
- referential integrity
- parameterized queries
- appropriate auditability

Database schema changes should be implemented through migrations rather than manual destructive modification.

---

# 35. Testing Requirements

Code is not considered complete solely because it executes.

Testing may include:

- unit tests
- integration tests
- SQLite tests
- migration tests
- repository tests
- PowerShell tests
- GUI tests
- regression tests
- end-to-end workflow tests
- security-oriented tests

Test reporting should use:

```text
PASS
FAIL
NOT RUN
BLOCKED
```

No automated test should be described as passing unless it was actually executed.

---

# 36. Success Criteria

F7Hub is successful when it improves real technician workflows.

Success should be evaluated by practical outcomes rather than total feature count.

Key criteria include:

## Productivity

- reduces unnecessary application switching
- reduces repetitive typing
- reduces repeated searches
- improves access to scripts and commands
- makes common actions faster

## Troubleshooting

- encourages consistent diagnostic workflows
- preserves troubleshooting history
- improves access to relevant knowledge
- helps technicians understand ticket context
- supports structured escalation

## Knowledge

- makes KB content easier to create
- makes existing knowledge easier to retrieve
- connects knowledge with tickets and diagnostics
- reduces rediscovery of solved problems

## Automation

- makes approved automation easy to discover
- captures script parameters and output
- reduces repetitive manual administration
- maintains technician control

## Architecture

- remains modular
- remains testable
- avoids unnecessary duplication
- supports future extension
- preserves clear subsystem responsibilities

## Reliability

- protects database integrity
- handles errors predictably
- maintains logs where useful
- supports safe migrations
- avoids silent failures

## Security

- does not expose credentials
- uses least privilege
- validates external data
- does not blindly execute AI output

## Documentation

- keeps implementation and documentation synchronized
- allows new contributors or coding agents to understand the project
- records architectural decisions and verified changes

---

# 37. Project Quality Goals

F7Hub should progressively improve in the following areas:

```text
Correctness
Maintainability
Security
Testability
Usability
Performance
Observability
Extensibility
Documentation
Recoverability
```

These goals should be balanced rather than optimized independently.

For example:

- maximum abstraction may harm understandability
- excessive optimization may harm maintainability
- excessive configurability may create unnecessary complexity
- excessive automation may reduce safety

---

# 38. Guiding Principles

The project's core guiding principles are:

1. Build the correct system, not the most code.
2. Inspect existing functionality before creating new functionality.
3. Prefer simple architecture over speculative complexity.
4. Maintain explicit subsystem boundaries.
5. Use configuration instead of environment-specific hardcoding.
6. Keep data ownership clear.
7. Keep automation reviewable.
8. Treat AI-generated output as untrusted.
9. Use least privilege.
10. Preserve database integrity.
11. Implement database changes through migrations.
12. Build features as small testable vertical slices.
13. Test success and failure paths.
14. Keep documentation synchronized.
15. Avoid unnecessary dependency growth.
16. Reuse existing mature external platforms rather than recreating them.
17. Preserve reversibility where practical.
18. Keep F7Hub understandable.

---

# 39. Major Architectural Boundaries

Changes affecting the following areas require additional review:

- destructive database migrations
- core database relationships
- primary GUI framework
- authentication architecture
- security boundaries
- repository restructuring
- plugin architecture
- major dependencies
- inter-process communication contracts
- cross-language architecture
- secrets management
- external administrative integrations

These areas can create long-term project constraints and should not be modified casually.

---

# 40. Project Completion Philosophy

A task should only be considered complete when applicable requirements have been checked.

Typical completion checklist:

```text
[ ] Requested behavior implemented
[ ] Existing architecture inspected
[ ] Duplicate functionality avoided
[ ] Architecture preserved
[ ] Database integrity preserved
[ ] Security considered
[ ] Error handling implemented
[ ] Tests executed
[ ] Test status recorded
[ ] Documentation updated
[ ] Unrelated changes avoided
[ ] Known limitations documented
[ ] Remaining risks identified
```

Not every task requires every item, but omitted checks should be intentional.

---

# 41. Relationship to Project Vision

`00_ProjectVision.md` defines:

> Why does F7Hub exist and what should it become?

This document defines:

> What is F7Hub as an actual software project?

The distinction is intentional.

For example:

```text
00_ProjectVision.md
→ F7Hub should become a technician command center.

01_Project.md
→ F7Hub is designed as a Windows-first modular application using Python, PyQt6, PowerShell, AutoHotkey and SQLite.
```

---

# 42. Related Documents

## Product

- `00_ProjectVision.md`
- `02_ProductRequirements.md`
- `03_Features.md`
- `04_UserWorkflows.md`

## Interface and Architecture

- `05_GUI.md`
- `06_SystemArchitecture.md`

## Database

- `07_Database.md`
- `08_ERD.md`
- `09_SQLSchema.md`

## Repository and Technology

- `10_FolderStructure.md`
- `11_AHKArchitecture.md`
- `12_PowerShellArchitecture.md`
- `13_PythonArchitecture.md`

## Standards

- `14_DesignPrinciples.md`
- `15_NamingConventions.md`

## Project Management

- `16_Roadmap.md`
- `17_Todo.md`
- `18_ChangeLog.md`

## Documentation Navigation

- `19_DocumentationIndex.md`

---

# 43. Project Summary

F7Hub is a Windows-first modular IT support platform centered around a Python/PyQt6 desktop application.

Its architecture combines:

```text
PyQt6
→ User interface

Python
→ Application coordination and domain services

SQLite
→ Persistent relational data

PowerShell
→ Windows and Microsoft administration

AutoHotkey v2
→ Desktop automation and productivity

Markdown + Mermaid
→ Documentation and architecture visualization

Git
→ Source control and project history

AI
→ Assisted development and technician support
```

F7Hub is intended to centralize technician context without unnecessarily reproducing mature external systems.

The project should evolve through small, documented, tested and reversible changes.

Its success depends not on how many features it contains, but on whether it makes IT support work faster, more consistent, safer and easier to understand.
