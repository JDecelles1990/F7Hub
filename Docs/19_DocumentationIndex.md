# F7Hub Documentation Index

> Document: `Docs/19_DocumentationIndex.md`  
> Project: F7Hub  
> Purpose: Provide the canonical navigation, governance, ownership, status, dependency, task-routing, review-gate, and documentation-impact map for the F7Hub documentation system.  
> Related Project Files: `AGENTS.md`, `ROOT.md`, `Docs/00_ProjectVision.md` through `Docs/18_ChangeLog.md`

---

# 1. Purpose

This file is the navigation index for the F7Hub documentation system.

It does not replace:

```text
AGENTS.md
ROOT.md
or
any individual canonical documentation file
```

Its purpose is to provide:

- documentation inventory
- document status
- authority categories
- document ownership
- dependency relationships
- recommended reading order
- task-to-document routing
- documentation impact guidance
- review gates
- agent navigation rules
- documentation conflict handling
- implementation-readiness guidance
- quick navigation for developers and coding agents

The central question is:

> Which F7Hub documents should be read for a particular task, and which document owns the relevant decision?

---

# 2. Documentation Hierarchy

The F7Hub documentation system follows this hierarchy:

```text
AGENTS.md
    │
    │ Defines HOW coding agents must work
    ▼
ROOT.md
    │
    │ Provides the project entry point
    │ and explains WHAT F7Hub is
    ▼
Docs/19_DocumentationIndex.md
    │
    │ Defines WHICH canonical documents to consult
    ▼
Relevant Canonical Docs
    │
    ├── Product Definition
    ├── Requirements
    ├── Workflows
    ├── GUI
    ├── System Architecture
    ├── Database
    ├── Technology Architecture
    ├── Design Standards
    └── Planning / History
    │
    ▼
Implementation Inspection
    │
    ▼
Plan
    │
    ▼
Implementation
    │
    ▼
Tests
    │
    ▼
Review
    │
    ▼
Documentation Synchronization
```

Documentation defines intended behavior.

Repository inspection determines what actually exists.

Tests determine what has been verified.

---

# 3. Source-of-Truth Priority

When information conflicts, use:

```text
1. Explicit user requirement
2. Approved architecture
3. Canonical project documentation
4. Validated implementation
5. Tests
6. Established project conventions
7. Engineering inference
```

Do not silently choose whichever source is easiest to implement.

If canonical documents conflict, resolve the conflict before significant implementation.

---

# 4. Documentation Status

Canonical documents may use:

```text
DRAFT
REVIEW
APPROVED
DEPRECATED
ARCHIVED
```

## DRAFT

The document is incomplete or actively being designed.

Its content should not automatically be treated as final architectural authority.

## REVIEW

The document is sufficiently developed for formal review but has not yet been accepted as current authoritative guidance.

## APPROVED

The document has been reviewed and accepted as the current specification for its subject.

Approval does not prove implementation exists.

## DEPRECATED

The document has been superseded but remains temporarily available for transition or reference.

## ARCHIVED

The document is historical only and must not be used as current source of truth.

---

# 5. Implementation Status Is Separate

Documentation status and implementation status are different concepts.

```text
APPROVED DOCUMENT
≠
IMPLEMENTED FEATURE

IMPLEMENTED FEATURE
≠
VERIFIED FEATURE
```

For product or implementation status, use applicable terms such as:

```text
PLANNED
IN PROGRESS
IMPLEMENTED
VERIFIED
DEFERRED
REJECTED
NOT VERIFIED
```

For test execution, use:

```text
PASS
FAIL
NOT RUN
BLOCKED
```

Never infer working implementation from documentation alone.

---

# 6. Authority Categories

Canonical documents may be grouped by primary authority:

```text
PRODUCT
REQUIREMENTS
WORKFLOW
GUI
ARCHITECTURE
DATABASE
TECHNOLOGY
DESIGN
PLANNING
HISTORY
INDEX
```

Authority means:

> This document is the primary owner of this kind of decision.

It does not override higher-priority explicit requirements.

---

# 7. Canonical Documentation Inventory

| ID | File | Primary Responsibility | Authority | Current Status |
|---|---|---|---|---|
| DOC-00 | `00_ProjectVision.md` | Long-term vision and purpose | PRODUCT | REVIEW |
| DOC-01 | `01_Project.md` | Project identity, scope, technology context | PRODUCT | REVIEW |
| DOC-02 | `02_ProductRequirements.md` | Functional and non-functional requirements | REQUIREMENTS | REVIEW |
| DOC-03 | `03_Features.md` | Feature and capability catalogue | PRODUCT | REVIEW |
| DOC-04 | `04_UserWorkflows.md` | Technician workflows and journeys | WORKFLOW | REVIEW |
| DOC-05 | `05_GUI.md` | GUI structure, presentation, UX behavior | GUI | REVIEW |
| DOC-06 | `06_SystemArchitecture.md` | Overall subsystem architecture and boundaries | ARCHITECTURE | REVIEW |
| DOC-07 | `07_Database.md` | SQLite architecture, integrity, migration strategy | DATABASE | REVIEW |
| DOC-08 | `08_ERD.md` | Conceptual entities and relationships | DATABASE | REVIEW |
| DOC-09 | `09_SQLSchema.md` | Exact SQLite schema definition | DATABASE | REVIEW |
| DOC-10 | `10_FolderStructure.md` | Canonical repository/filesystem organization | ARCHITECTURE | REVIEW |
| DOC-11 | `11_AHKArchitecture.md` | AutoHotkey v2 architecture | TECHNOLOGY | REVIEW |
| DOC-12 | `12_PowerShellArchitecture.md` | PowerShell architecture | TECHNOLOGY | REVIEW |
| DOC-13 | `13_PythonArchitecture.md` | Python/PyQt6 architecture | TECHNOLOGY | REVIEW |
| DOC-14 | `14_DesignPrinciples.md` | Engineering and design principles | DESIGN | REVIEW |
| DOC-15 | `15_NamingConventions.md` | Cross-technology naming standards | DESIGN | REVIEW |
| DOC-16 | `16_Roadmap.md` | Development phases and milestones | PLANNING | REVIEW |
| DOC-17 | `17_Todo.md` | Current actionable work | PLANNING | REVIEW |
| DOC-18 | `18_ChangeLog.md` | Meaningful historical changes | HISTORY | REVIEW |
| DOC-19 | `19_DocumentationIndex.md` | Documentation navigation and governance | INDEX | REVIEW |

These statuses should be updated after the planned cross-document review.

Do not mark documents `APPROVED` merely because they contain substantial text.

---

# 8. Canonical Document Ownership

Each important concept should have one primary documentation owner.

```text
Project vision
→ 00_ProjectVision.md

Project definition and scope
→ 01_Project.md

Requirements
→ 02_ProductRequirements.md

Features
→ 03_Features.md

User workflows
→ 04_UserWorkflows.md

GUI behavior
→ 05_GUI.md

Overall system architecture
→ 06_SystemArchitecture.md

Database architecture
→ 07_Database.md

Entity relationships
→ 08_ERD.md

Exact SQL schema
→ 09_SQLSchema.md

Folder structure
→ 10_FolderStructure.md

AutoHotkey v2 architecture
→ 11_AHKArchitecture.md

PowerShell architecture
→ 12_PowerShellArchitecture.md

Python/PyQt6 architecture
→ 13_PythonArchitecture.md

Design principles
→ 14_DesignPrinciples.md

Naming rules
→ 15_NamingConventions.md

Roadmap
→ 16_Roadmap.md

Current tasks
→ 17_Todo.md

Historical changes
→ 18_ChangeLog.md

Documentation routing
→ 19_DocumentationIndex.md
```

Avoid duplicating authoritative specifications across several documents.

References are preferable to repetition.

---

# 9. Recommended Full Reading Order

For a developer learning F7Hub from the beginning:

```text
00 Project Vision
      ↓
01 Project
      ↓
02 Product Requirements
      ↓
03 Features
      ↓
04 User Workflows
      ↓
05 GUI
      ↓
06 System Architecture
      ↓
07 Database
      ↓
08 ERD
      ↓
09 SQL Schema
      ↓
10 Folder Structure
      ↓
11 AutoHotkey v2 Architecture
      ↓
12 PowerShell Architecture
      ↓
13 Python/PyQt6 Architecture
      ↓
14 Design Principles
      ↓
15 Naming Conventions
      ↓
16 Roadmap
      ↓
17 Todo
      ↓
18 ChangeLog
      ↓
19 Documentation Index
```

This is a learning order.

It is not the required reading set for every coding task.

---

# 10. Minimum-Sufficient Reading Rule

For most focused tasks, read:

```text
2 to 5 directly relevant canonical docs
```

in addition to:

```text
AGENTS.md
Docs/19_DocumentationIndex.md
```

Read additional documents when a task crosses subsystem boundaries.

The objective is:

```text
enough context
without unnecessary context loading
```

---

# 11. Product Dependency Graph

```text
00_ProjectVision.md
        ↓
01_Project.md
        ↓
02_ProductRequirements.md
        ↓
03_Features.md
        ↓
04_UserWorkflows.md
```

These answer:

```text
Why does F7Hub exist?
What is F7Hub?
What must F7Hub do?
What capabilities provide that behavior?
How does a technician use those capabilities?
```

---

# 12. Architecture Dependency Graph

```text
02_ProductRequirements.md
        ↓
03_Features.md
        ↓
04_UserWorkflows.md
        ↓
06_SystemArchitecture.md
```

`06_SystemArchitecture.md` converts product behavior into subsystem boundaries.

---

# 13. GUI Dependency Graph

```text
02_ProductRequirements.md
        ↓
03_Features.md
        ↓
04_UserWorkflows.md
        ↓
05_GUI.md
        ↓
06_SystemArchitecture.md
        ↓
13_PythonArchitecture.md
```

---

# 14. Database Dependency Graph

```text
02_ProductRequirements.md
        ↓
03_Features.md
        ↓
04_UserWorkflows.md
        ↓
06_SystemArchitecture.md
        ↓
07_Database.md
        ↓
08_ERD.md
        ↓
09_SQLSchema.md
```

The three database documents have distinct responsibilities and must remain synchronized.

---

# 15. Technology Dependency Graph

```text
                    06_SystemArchitecture.md
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
11_AHKArchitecture  12_PowerShell   13_PythonArchitecture
                         Architecture
```

Technology architecture must not contradict overall system architecture.

---

# 16. Design Standards Dependency

```text
06_SystemArchitecture.md
        ↓
14_DesignPrinciples.md
        ↓
15_NamingConventions.md
```

These standards apply across implementation work.

---

# 17. Planning Dependency Graph

```text
02_ProductRequirements.md
        ↓
03_Features.md
        ↓
16_Roadmap.md
        ↓
17_Todo.md
        ↓
Implementation
        ↓
18_ChangeLog.md
```

---

# 18. Database Documentation Relationship

## `07_Database.md`

Owns database architecture and rules.

Examples:

- SQLite role
- normalization
- persistence principles
- foreign-key policy
- migrations
- transactions
- indexing strategy
- FTS5 strategy
- backups
- repository boundary
- integrity rules

## `08_ERD.md`

Owns conceptual and logical relationships.

Examples:

- entities
- relationships
- cardinality
- ownership
- many-to-many relationships
- conceptual domain separation

## `09_SQLSchema.md`

Owns exact physical schema.

Examples:

- tables
- columns
- SQLite data types
- primary keys
- foreign keys
- defaults
- constraints
- indexes
- FTS objects
- views
- triggers where justified

The relationship is:

```text
07
Database rules
   ↓
08
Entities and relationships
   ↓
09
Exact SQLite implementation
```

Do not modify `09_SQLSchema.md` in isolation from 07 and 08 when structural changes are involved.

---

# 19. GUI Documentation Relationship

## `05_GUI.md`

Owns user-facing presentation and interaction.

Examples:

- windows
- navigation
- workspaces
- docks
- forms
- dialogs
- menus
- toolbars
- status feedback
- keyboard interaction

## `06_SystemArchitecture.md`

Owns technical boundaries between:

```text
GUI
Services
Domain
Repositories
Infrastructure
```

## `13_PythonArchitecture.md`

Owns the implementation architecture for PyQt6 and Python.

Detailed Python implementation should not be placed in `05_GUI.md`.

---

# 20. Technology Documentation Relationship

## `11_AHKArchitecture.md`

Owns:

```text
AutoHotkey v2
global hotkeys
hotstrings
clipboard automation
launchers
lightweight quick menus
window focus
desktop integration
AHK-to-F7Hub command forwarding
```

It does not own the primary application GUI.

---

## `12_PowerShellArchitecture.md`

Owns:

```text
PowerShell 7
Windows administration
Microsoft administration
diagnostics
remediation boundaries
structured results
script registry behavior
PowerShell execution rules
```

---

## `13_PythonArchitecture.md`

Owns:

```text
Python package architecture
PyQt6 application
services
domain
repositories
infrastructure
integrations
search
diagnostics
background execution
application lifecycle
```

---

# 21. Design Standards Relationship

## `14_DesignPrinciples.md`

Owns decision principles such as:

```text
simplicity
least privilege
vertical slices
inspect-before-create
deterministic core behavior
controlled AI
data integrity
scope control
```

## `15_NamingConventions.md`

Owns naming conventions for:

```text
Python
PowerShell
AutoHotkey
SQLite
folders
files
commands
tests
migrations
logs
integrations
```

---

# 22. Task Routing: Project Scope

For:

- project direction
- whether a capability belongs in F7Hub
- major scope decisions
- strategic priorities

Read:

```text
00_ProjectVision.md
01_Project.md
02_ProductRequirements.md
14_DesignPrinciples.md
```

---

# 23. Task Routing: Requirements

For:

- new requirements
- changed requirements
- functional behavior
- non-functional behavior
- acceptance criteria

Read:

```text
01_Project.md
02_ProductRequirements.md
03_Features.md
04_UserWorkflows.md
```

---

# 24. Task Routing: Feature Planning

For:

- new feature
- feature split
- capability inventory
- prioritization

Read:

```text
02_ProductRequirements.md
03_Features.md
04_UserWorkflows.md
16_Roadmap.md
17_Todo.md
```

---

# 25. Task Routing: User Workflows

For:

- technician flows
- ticket resolution
- escalation
- KB workflow
- diagnostics
- clipboard workflow
- administration workflow

Read:

```text
03_Features.md
04_UserWorkflows.md
```

Then read the architecture document for the affected subsystem.

---

# 26. Task Routing: GUI

For general PyQt6 GUI work:

```text
04_UserWorkflows.md
05_GUI.md
06_SystemArchitecture.md
13_PythonArchitecture.md
15_NamingConventions.md
```

If folders change:

```text
10_FolderStructure.md
```

---

# 27. Task Routing: Main Window

For:

- `QMainWindow`
- menu bar
- toolbar
- status bar
- central workspace
- docks
- window state

Read:

```text
05_GUI.md
06_SystemArchitecture.md
13_PythonArchitecture.md
```

---

# 28. Task Routing: Command Palette

For:

- `Ctrl+Shift+P`
- command registry
- stable command IDs
- command routing
- AHK command forwarding

Read:

```text
05_GUI.md
06_SystemArchitecture.md
11_AHKArchitecture.md
13_PythonArchitecture.md
15_NamingConventions.md
```

---

# 29. Task Routing: Workspaces

For:

- workspace profiles
- dock layouts
- panel state
- layout persistence

Read:

```text
05_GUI.md
06_SystemArchitecture.md
13_PythonArchitecture.md
08_ERD.md
```

Read `09_SQLSchema.md` only if workspace persistence is actually being implemented.

---

# 30. Task Routing: Python General

For general Python/PyQt6 implementation:

```text
06_SystemArchitecture.md
10_FolderStructure.md
13_PythonArchitecture.md
14_DesignPrinciples.md
15_NamingConventions.md
```

Add feature-specific requirements/workflow docs.

---

# 31. Task Routing: Python Bootstrap

For:

- entry point
- configuration
- logging
- service construction
- startup
- database initialization
- shutdown

Read:

```text
06_SystemArchitecture.md
07_Database.md
10_FolderStructure.md
13_PythonArchitecture.md
```

---

# 32. Task Routing: Python Services

For application services:

```text
02_ProductRequirements.md
04_UserWorkflows.md
06_SystemArchitecture.md
13_PythonArchitecture.md
14_DesignPrinciples.md
15_NamingConventions.md
```

---

# 33. Task Routing: Domain Logic

For:

- entities
- validation
- enums
- state transitions
- domain rules

Read:

```text
02_ProductRequirements.md
04_UserWorkflows.md
06_SystemArchitecture.md
13_PythonArchitecture.md
15_NamingConventions.md
```

Add DB docs if persistence structure is affected.

---

# 34. Task Routing: Repositories

For repository creation or changes:

```text
06_SystemArchitecture.md
07_Database.md
08_ERD.md
09_SQLSchema.md
13_PythonArchitecture.md
15_NamingConventions.md
```

---

# 35. Task Routing: SQLite General

For any SQLite implementation:

```text
07_Database.md
08_ERD.md
09_SQLSchema.md
13_PythonArchitecture.md
15_NamingConventions.md
```

If repository paths or DB location are involved:

```text
10_FolderStructure.md
```

---

# 36. Task Routing: New Database Entity

Before creating a table:

```text
02_ProductRequirements.md
04_UserWorkflows.md
07_Database.md
08_ERD.md
09_SQLSchema.md
15_NamingConventions.md
```

Then:

```text
SEARCH
→ IDENTIFY
→ REUSE / EXTEND
→ CREATE ONLY IF NECESSARY
```

---

# 37. Task Routing: Migrations

For migration infrastructure or schema changes:

```text
07_Database.md
09_SQLSchema.md
10_FolderStructure.md
13_PythonArchitecture.md
15_NamingConventions.md
```

After implementation, review:

```text
18_ChangeLog.md
```

---

# 38. Task Routing: ERD

For relationship design:

```text
02_ProductRequirements.md
04_UserWorkflows.md
07_Database.md
08_ERD.md
```

Use `09_SQLSchema.md` only when converting the approved model into exact SQL.

---

# 39. Task Routing: Exact SQL Schema

For:

- `CREATE TABLE`
- PK/FK
- defaults
- constraints
- exact indexes
- FTS objects
- views/triggers

Read:

```text
07_Database.md
08_ERD.md
09_SQLSchema.md
15_NamingConventions.md
```

Also inspect relevant requirements/workflows.

---

# 40. Task Routing: Indexes

For index changes:

```text
04_UserWorkflows.md
07_Database.md
09_SQLSchema.md
```

Use real query patterns and:

```text
EXPLAIN QUERY PLAN
```

Do not add speculative indexes.

---

# 41. Task Routing: FTS5

For full-text search:

```text
06_SystemArchitecture.md
07_Database.md
09_SQLSchema.md
13_PythonArchitecture.md
```

If user-facing search behavior changes:

```text
03_Features.md
04_UserWorkflows.md
```

---

# 42. Task Routing: Tickets

For ticket implementation:

```text
02_ProductRequirements.md
03_Features.md
04_UserWorkflows.md
07_Database.md
08_ERD.md
09_SQLSchema.md
13_PythonArchitecture.md
```

For GUI:

```text
05_GUI.md
```

---

# 43. Task Routing: Ticket Creation

Recommended focused reading:

```text
02_ProductRequirements.md
04_UserWorkflows.md
07_Database.md
09_SQLSchema.md
13_PythonArchitecture.md
15_NamingConventions.md
```

For UI:

```text
05_GUI.md
```

---

# 44. Task Routing: Ticket Notes

Read:

```text
02_ProductRequirements.md
04_UserWorkflows.md
08_ERD.md
09_SQLSchema.md
13_PythonArchitecture.md
```

---

# 45. Task Routing: Ticket Status

For lifecycle/state changes:

```text
02_ProductRequirements.md
04_UserWorkflows.md
08_ERD.md
09_SQLSchema.md
13_PythonArchitecture.md
```

---

# 46. Task Routing: Companies

Read:

```text
02_ProductRequirements.md
03_Features.md
04_UserWorkflows.md
08_ERD.md
09_SQLSchema.md
13_PythonArchitecture.md
```

---

# 47. Task Routing: Contacts

Read:

```text
02_ProductRequirements.md
03_Features.md
04_UserWorkflows.md
08_ERD.md
09_SQLSchema.md
13_PythonArchitecture.md
```

---

# 48. Task Routing: Knowledge Base

Read:

```text
02_ProductRequirements.md
03_Features.md
04_UserWorkflows.md
07_Database.md
08_ERD.md
09_SQLSchema.md
13_PythonArchitecture.md
```

For interface:

```text
05_GUI.md
```

---

# 49. Task Routing: Universal Search

Read:

```text
02_ProductRequirements.md
03_Features.md
04_UserWorkflows.md
06_SystemArchitecture.md
07_Database.md
13_PythonArchitecture.md
```

If exact FTS tables/indexes are involved:

```text
09_SQLSchema.md
```

---

# 50. Task Routing: Search Ranking

Read:

```text
03_Features.md
04_UserWorkflows.md
13_PythonArchitecture.md
14_DesignPrinciples.md
```

Initial search ranking should remain deterministic.

---

# 51. Task Routing: Diagnostics

For Diagnostic Engine work:

```text
02_ProductRequirements.md
03_Features.md
04_UserWorkflows.md
06_SystemArchitecture.md
08_ERD.md
13_PythonArchitecture.md
```

For persistence:

```text
09_SQLSchema.md
```

For PowerShell execution steps:

```text
12_PowerShellArchitecture.md
```

---

# 52. Task Routing: Dynamic Diagnostic Forms

Read:

```text
04_UserWorkflows.md
05_GUI.md
08_ERD.md
13_PythonArchitecture.md
```

---

# 53. Task Routing: PowerShell General

For PowerShell work:

```text
06_SystemArchitecture.md
10_FolderStructure.md
12_PowerShellArchitecture.md
14_DesignPrinciples.md
15_NamingConventions.md
```

Add the affected feature/workflow docs.

---

# 54. Task Routing: New PowerShell Script

Before creating a script:

```text
04_UserWorkflows.md
10_FolderStructure.md
12_PowerShellArchitecture.md
15_NamingConventions.md
```

Then inspect:

```text
PowerShell\
Tests\
```

Search for existing functionality first.

---

# 55. Task Routing: PowerShell Gateway

For Python-to-PowerShell execution:

```text
06_SystemArchitecture.md
12_PowerShellArchitecture.md
13_PythonArchitecture.md
14_DesignPrinciples.md
```

---

# 56. Task Routing: Structured PowerShell Output

Read:

```text
06_SystemArchitecture.md
12_PowerShellArchitecture.md
13_PythonArchitecture.md
```

Changes to a stable result contract should be versioned and recorded in `18_ChangeLog.md`.

---

# 57. Task Routing: PowerShell Remediation

For modifying system or tenant state:

```text
02_ProductRequirements.md
04_UserWorkflows.md
06_SystemArchitecture.md
12_PowerShellArchitecture.md
14_DesignPrinciples.md
```

Security review is required.

Read-only diagnostics should usually exist first.

---

# 58. Task Routing: Microsoft Graph

Read:

```text
02_ProductRequirements.md
06_SystemArchitecture.md
12_PowerShellArchitecture.md
13_PythonArchitecture.md
14_DesignPrinciples.md
```

Current official Microsoft documentation must be checked before implementation.

---

# 59. Task Routing: Exchange Online

Read:

```text
02_ProductRequirements.md
04_UserWorkflows.md
06_SystemArchitecture.md
12_PowerShellArchitecture.md
```

Verify currently supported modules/authentication.

---

# 60. Task Routing: Entra ID

Read:

```text
02_ProductRequirements.md
04_UserWorkflows.md
06_SystemArchitecture.md
12_PowerShellArchitecture.md
```

Use current Microsoft Entra terminology.

---

# 61. Task Routing: Intune

Read:

```text
02_ProductRequirements.md
04_UserWorkflows.md
06_SystemArchitecture.md
12_PowerShellArchitecture.md
```

---

# 62. Task Routing: Defender

Read:

```text
02_ProductRequirements.md
04_UserWorkflows.md
12_PowerShellArchitecture.md
14_DesignPrinciples.md
```

Security-sensitive operations require additional review.

---

# 63. Task Routing: Teams / SharePoint

Read:

```text
02_ProductRequirements.md
04_UserWorkflows.md
06_SystemArchitecture.md
12_PowerShellArchitecture.md
```

---

# 64. Task Routing: AutoHotkey v2 General

For AutoHotkey work:

```text
06_SystemArchitecture.md
10_FolderStructure.md
11_AHKArchitecture.md
14_DesignPrinciples.md
15_NamingConventions.md
```

F7Hub uses:

```text
AutoHotkey v2
```

Do not introduce AHK v1 syntax.

---

# 65. Task Routing: Hotkeys

Read:

```text
05_GUI.md
11_AHKArchitecture.md
15_NamingConventions.md
```

If forwarding actions into Python:

```text
06_SystemArchitecture.md
13_PythonArchitecture.md
```

---

# 66. Task Routing: Hotstrings

Read:

```text
11_AHKArchitecture.md
15_NamingConventions.md
```

Only read DB docs if persistence is genuinely required.

---

# 67. Task Routing: Clipboard

For AHK clipboard automation:

```text
11_AHKArchitecture.md
14_DesignPrinciples.md
```

For persistent snippets/history:

```text
02_ProductRequirements.md
08_ERD.md
09_SQLSchema.md
13_PythonArchitecture.md
```

---

# 68. Task Routing: Launchers

For:

- application launching
- window focus
- Windows tools
- portal launching

Read:

```text
10_FolderStructure.md
11_AHKArchitecture.md
15_NamingConventions.md
```

---

# 69. Task Routing: AI

For AI implementation:

```text
02_ProductRequirements.md
03_Features.md
04_UserWorkflows.md
06_SystemArchitecture.md
13_PythonArchitecture.md
14_DesignPrinciples.md
```

If persistence is involved:

```text
08_ERD.md
09_SQLSchema.md
```

---

# 70. Task Routing: AI Provider

Read:

```text
06_SystemArchitecture.md
13_PythonArchitecture.md
14_DesignPrinciples.md
```

Provider-specific details should remain behind an adapter/gateway boundary.

---

# 71. Task Routing: AI Context

For:

- context builder
- privacy filtering
- ticket context
- KB context
- prompt context

Read:

```text
02_ProductRequirements.md
04_UserWorkflows.md
13_PythonArchitecture.md
14_DesignPrinciples.md
```

---

# 72. Task Routing: AI-Generated Commands

Read:

```text
12_PowerShellArchitecture.md
13_PythonArchitecture.md
14_DesignPrinciples.md
```

AI output must never directly execute shell commands.

---

# 73. Task Routing: Prompt Library

Read:

```text
02_ProductRequirements.md
03_Features.md
04_UserWorkflows.md
08_ERD.md
13_PythonArchitecture.md
```

Exact schema:

```text
09_SQLSchema.md
```

---

# 74. Task Routing: Reporting

Read:

```text
02_ProductRequirements.md
03_Features.md
04_UserWorkflows.md
12_PowerShellArchitecture.md
13_PythonArchitecture.md
```

Reports should derive from structured data.

---

# 75. Task Routing: Settings

Read:

```text
02_ProductRequirements.md
05_GUI.md
06_SystemArchitecture.md
10_FolderStructure.md
13_PythonArchitecture.md
```

Secrets must not be stored as normal settings.

---

# 76. Task Routing: Logging

Read:

```text
06_SystemArchitecture.md
10_FolderStructure.md
12_PowerShellArchitecture.md
13_PythonArchitecture.md
14_DesignPrinciples.md
```

Technical logs and audit records are separate concepts.

---

# 77. Task Routing: Security

For security-sensitive work:

```text
02_ProductRequirements.md
06_SystemArchitecture.md
12_PowerShellArchitecture.md
13_PythonArchitecture.md
14_DesignPrinciples.md
```

Also read affected subsystem docs.

---

# 78. Task Routing: Authentication

For:

- Microsoft authentication
- Graph scopes
- credentials
- tokens
- privilege boundaries

Read:

```text
02_ProductRequirements.md
06_SystemArchitecture.md
12_PowerShellArchitecture.md
13_PythonArchitecture.md
14_DesignPrinciples.md
```

Use current official provider documentation.

---

# 79. Task Routing: Filesystem

For:

- attachments
- exports
- temp files
- runtime directories
- path safety

Read:

```text
07_Database.md
10_FolderStructure.md
13_PythonArchitecture.md
14_DesignPrinciples.md
```

---

# 80. Task Routing: Attachments

Read:

```text
02_ProductRequirements.md
04_UserWorkflows.md
07_Database.md
08_ERD.md
09_SQLSchema.md
13_PythonArchitecture.md
```

---

# 81. Task Routing: Folder Structure

For creating or moving architectural folders:

```text
06_SystemArchitecture.md
10_FolderStructure.md
14_DesignPrinciples.md
```

Then read the relevant technology architecture file.

---

# 82. Task Routing: Repository Restructuring

Read:

```text
01_Project.md
06_SystemArchitecture.md
10_FolderStructure.md
14_DesignPrinciples.md
15_NamingConventions.md
```

Major restructuring requires explicit review.

---

# 83. Task Routing: Naming

Primary source:

```text
15_NamingConventions.md
```

Then read the relevant technology-specific architecture file.

---

# 84. Task Routing: Testing

For general test design:

```text
02_ProductRequirements.md
13_PythonArchitecture.md
14_DesignPrinciples.md
17_Todo.md
```

Then add affected subsystem docs.

---

# 85. Task Routing: Database Testing

Read:

```text
07_Database.md
09_SQLSchema.md
13_PythonArchitecture.md
14_DesignPrinciples.md
```

Test:

```text
foreign keys
constraints
migrations
transactions
repositories
failure paths
```

---

# 86. Task Routing: GUI Testing

Read:

```text
05_GUI.md
13_PythonArchitecture.md
14_DesignPrinciples.md
```

---

# 87. Task Routing: PowerShell Testing

Read:

```text
12_PowerShellArchitecture.md
13_PythonArchitecture.md
14_DesignPrinciples.md
```

Potential tools:

```text
Pester
pytest integration tests
```

---

# 88. Task Routing: AutoHotkey Testing

Read:

```text
11_AHKArchitecture.md
14_DesignPrinciples.md
```

Some AHK workflows may require documented manual testing.

---

# 89. Task Routing: Code Review

Read:

```text
06_SystemArchitecture.md
14_DesignPrinciples.md
15_NamingConventions.md
```

Then add the relevant subsystem architecture.

Review:

```text
correctness
architecture
security
error handling
duplication
database integrity
tests
documentation
```

---

# 90. Task Routing: Architecture Review

Read:

```text
00_ProjectVision.md
02_ProductRequirements.md
06_SystemArchitecture.md
10_FolderStructure.md
14_DesignPrinciples.md
16_Roadmap.md
```

Add affected subsystem documents.

---

# 91. Task Routing: Roadmap

Read:

```text
02_ProductRequirements.md
03_Features.md
16_Roadmap.md
17_Todo.md
```

---

# 92. Task Routing: Todo

Read:

```text
16_Roadmap.md
17_Todo.md
18_ChangeLog.md
```

Todo owns current actionable work.

---

# 93. Task Routing: ChangeLog

Read:

```text
16_Roadmap.md
17_Todo.md
18_ChangeLog.md
```

ChangeLog owns meaningful historical changes.

---

# 94. Task Routing: Mermaid Diagrams

For organizing or generating Mermaid diagrams:

```text
10_FolderStructure.md
17_Todo.md
19_DocumentationIndex.md
```

Then read the canonical owner for the diagram.

Examples:

```text
System architecture
→ 06_SystemArchitecture.md

GUI
→ 05_GUI.md

Database
→ 07_Database.md + 08_ERD.md + 09_SQLSchema.md

PowerShell
→ 12_PowerShellArchitecture.md

AutoHotkey
→ 11_AHKArchitecture.md

Python
→ 13_PythonArchitecture.md
```

Diagrams visualize approved architecture.

They must not silently redefine it.

---

# 95. Task Routing: Sequence Diagrams

Use:

```text
04_UserWorkflows.md
06_SystemArchitecture.md
```

Then add subsystem docs.

Example:

```text
Open Ticket Sequence
→ 04
→ 05
→ 06
→ 13
```

---

# 96. Task Routing: State Diagrams

Examples:

```text
Ticket Lifecycle
→ 04_UserWorkflows.md
→ 08_ERD.md
→ 09_SQLSchema.md

Diagnostic Session Lifecycle
→ 04_UserWorkflows.md
→ 08_ERD.md
→ 13_PythonArchitecture.md
```

---

# 97. Task Routing: Component Diagrams

Read:

```text
06_SystemArchitecture.md
10_FolderStructure.md
```

Then inspect relevant technology architecture docs.

---

# 98. Task Routing: Deployment Diagrams

Read:

```text
01_Project.md
06_SystemArchitecture.md
10_FolderStructure.md
13_PythonArchitecture.md
16_Roadmap.md
```

Do not present unapproved deployment assumptions as current architecture.

---

# 99. Task Routing: Class Diagrams

Class diagrams should primarily reflect implementation.

Read:

```text
13_PythonArchitecture.md
15_NamingConventions.md
```

Then inspect current source.

Avoid speculative dozens-of-class diagrams.

---

# 100. Task Routing: Git

For:

- branches
- baseline commit
- repository conventions
- release history

Read:

```text
01_Project.md
14_DesignPrinciples.md
15_NamingConventions.md
16_Roadmap.md
17_Todo.md
```

---

# 101. Task Routing: Packaging

Read:

```text
01_Project.md
06_SystemArchitecture.md
10_FolderStructure.md
13_PythonArchitecture.md
16_Roadmap.md
```

If packaging PowerShell/AHK components:

```text
12_PowerShellArchitecture.md
11_AHKArchitecture.md
```

---

# 102. Task Routing: Installer

Read:

```text
10_FolderStructure.md
13_PythonArchitecture.md
14_DesignPrinciples.md
16_Roadmap.md
```

Installed F7Hub must not permanently depend on:

```text
C:\Dev\F7Hub\
```

---

# 103. Task Routing: Plugins

Plugins are later scope.

Before plugin work:

```text
02_ProductRequirements.md
03_Features.md
06_SystemArchitecture.md
10_FolderStructure.md
13_PythonArchitecture.md
14_DesignPrinciples.md
16_Roadmap.md
```

Do not build the loader until concrete extension points exist.

---

# 104. Task Routing: HaloPSA

Before HaloPSA work:

```text
02_ProductRequirements.md
04_UserWorkflows.md
06_SystemArchitecture.md
13_PythonArchitecture.md
14_DesignPrinciples.md
```

Verify current provider documentation before implementation.

---

# 105. Task Routing: NinjaOne

Before NinjaOne integration:

```text
02_ProductRequirements.md
04_UserWorkflows.md
06_SystemArchitecture.md
13_PythonArchitecture.md
14_DesignPrinciples.md
```

---

# 106. Documentation Impact Matrix

| Change | Documents to Review |
|---|---|
| New requirement | 02, 03, 04 |
| New feature | 02, 03, 04, 16, 17 |
| Workflow change | 03, 04, 05 |
| GUI change | 04, 05, 06, 13 |
| Architecture change | 06 + affected subsystem docs |
| New database entity | 02/04 as needed, 07, 08, 09, 15 |
| Database relationship change | 07, 08, 09 |
| Database migration | 07, 09, 13, tests, 18 |
| Index change | 07, 09, query tests |
| Folder structure change | 10 + affected architecture doc |
| AHK architecture change | 11, possibly 06/10/13 |
| PowerShell architecture change | 12, possibly 06/10/13 |
| Python architecture change | 13, 06, possibly 10 |
| Naming standard change | 15 + affected docs/code |
| Design principle change | 14 + affected docs |
| Major milestone | 16, 17, possibly 18 |
| Current task status | 17 |
| Significant completed change | 18 |
| Cross-language interface | 06 + affected technology docs |
| Authentication/security boundary | 06, 12/13, 14 |
| Plugin architecture | 06, 10, 13, 16 |
| Diagram architecture change | owner doc first, then diagram |

---

# 107. Documentation Synchronization Rule

When implementation changes project behavior:

```text
IMPLEMENTATION CHANGE
        ↓
DOCUMENTATION IMPACT ANALYSIS
        ↓
Identify owning documents
        ↓
Validate implementation
        ↓
Update canonical docs
        ↓
Update ChangeLog if meaningful
```

Never modify documentation merely to make incorrect implementation appear correct.

---

# 108. Documentation Conflict Procedure

If canonical documents conflict:

```text
STOP
  ↓
Identify exact conflicting statements
  ↓
Apply source-of-truth priority
  ↓
Determine intended architecture
  ↓
Update all affected canonical docs
  ↓
Review
  ↓
Resume implementation
```

Do not silently choose one interpretation.

---

# 109. Documentation Gap Procedure

If an implementation requirement is missing:

```text
Identify missing decision
        ↓
Identify owning canonical document
        ↓
Document the decision
        ↓
Review architectural impact
        ↓
Implement
```

Trivial local implementation details do not require documentation expansion.

---

# 110. New Feature Decision Tree

```text
Does a requirement exist?
        │
    ┌───┴───┐
   No      Yes
    │        │
Update      Is feature documented?
02 first        │
            ┌───┴───┐
           No      Yes
            │        │
       Update 03    Is workflow clear?
                         │
                     ┌───┴───┐
                    No      Yes
                     │        │
                Update 04    Identify owner
                                  ↓
                           Read architecture docs
                                  ↓
                           Inspect implementation
                                  ↓
                           Plan small slice
```

---

# 111. New Database Entity Decision Tree

```text
Does the workflow require persistent data?
              │
          ┌───┴───┐
         No      Yes
          │        │
     No table     Existing entity fits?
                    │
                ┌───┴───┐
               Yes      No
                │        │
             Reuse     Define entity
                          ↓
                    Define relationships
                          ↓
                       Normalize
                          ↓
                     Update 08
                          ↓
                     Update 09
                          ↓
                      Migration
                          ↓
                       Tests
```

---

# 112. New Python Component Decision Tree

```text
What responsibility is required?
            ↓
Does an existing component own it?
        ┌───┴───┐
       Yes      No
        │        │
     Extend    Identify layer
                 ↓
        GUI / Service / Domain /
        Repository / Infrastructure
                 ↓
          Create only if necessary
```

---

# 113. New PowerShell Script Decision Tree

```text
Administrative or diagnostic need?
             ↓
Existing script?
       ┌─────┴─────┐
      Yes          No
       │            │
    Reuse /      Define narrow operation
    extend              ↓
                Diagnostic or remediation?
                        ↓
                  Define parameters
                        ↓
                Define structured result
                        ↓
                Define risk / privilege
                        ↓
                     Implement
                        ↓
                       Test
```

---

# 114. New AutoHotkey Component Decision Tree

```text
Is this primarily desktop automation?
             │
         ┌───┴───┐
        No      Yes
         │        │
Use Python/   Existing AHK component?
PowerShell          │
                ┌───┴───┐
               Yes      No
                │        │
             Extend   Create minimal component
```

---

# 115. New AI Feature Decision Tree

```text
Can deterministic logic solve it?
            │
        ┌───┴───┐
       Yes      No
        │        │
Use normal    Does AI provide clear benefit?
logic              │
               ┌────┴────┐
              No         Yes
               │          │
           Do not add   Define context
             AI             ↓
                       Privacy review
                            ↓
                        AIProvider
                            ↓
                      Validate output
                            ↓
                    Technician review
```

---

# 116. What Each Document Should NOT Become

## `00_ProjectVision.md`

Do not turn it into a technical implementation manual.

## `01_Project.md`

Do not duplicate all architecture documents.

## `02_ProductRequirements.md`

Do not contain detailed SQL.

## `03_Features.md`

Do not become implementation documentation.

## `04_UserWorkflows.md`

Do not become a schema definition.

## `05_GUI.md`

Do not contain raw persistence or business logic.

## `06_SystemArchitecture.md`

Do not contain every class and implementation detail.

## `07_Database.md`

Do not duplicate the exact SQL schema.

## `08_ERD.md`

Do not become migration history.

## `09_SQLSchema.md`

Do not define user-facing workflows.

## `10_FolderStructure.md`

Do not become a duplicate of system architecture.

## `11_AHKArchitecture.md`

Do not become a second GUI architecture or PowerShell specification.

## `12_PowerShellArchitecture.md`

Do not become the overall F7Hub architecture.

## `13_PythonArchitecture.md`

Do not become the product requirements document.

## `14_DesignPrinciples.md`

Do not become a second architecture specification.

## `15_NamingConventions.md`

Do not become source-code documentation.

## `16_Roadmap.md`

Do not become a task-by-task implementation backlog.

## `17_Todo.md`

Do not become another roadmap or architecture essay.

## `18_ChangeLog.md`

Do not become a duplicate of Git history or current architecture.

## `19_DocumentationIndex.md`

Do not become another requirements or architecture specification.

Its primary role is navigation and governance.

---

# 117. AGENTS.md Role

`AGENTS.md` defines how coding agents operate inside F7Hub.

It should include or reference:

```text
development process
source-of-truth hierarchy
inspect-before-create
scope control
testing expectations
security rules
documentation synchronization
agent-task format
```

A coding agent should read it before significant work.

---

# 118. ROOT.md Role

`ROOT.md` should act as a concise project entry point.

It should answer:

```text
What is F7Hub?
Where is the project?
What are the major technologies?
What should I read next?
```

It should point to:

```text
AGENTS.md
Docs/19_DocumentationIndex.md
```

instead of duplicating all canonical documentation.

---

# 119. Skills Role

Project-local `.agents/skills/` may contain reusable technical procedures when the project actually needs them. Repository inspection on 2026-09-02 found no project-local `.agents` directory; this is not a blocker for the first implementation slice.

Expected skills include:

```text
architecture
sqlite-database
autohotkey-v2
powershell
pyqt6
testing
documentation
codex-orchestration
code-review
security
```

Skills answer:

> How should this kind of technical task be performed?

Canonical F7Hub docs answer:

> What does F7Hub require and how is F7Hub designed?

---

# 120. Skills vs Canonical Docs

Example:

```text
sqlite-database skill
→ procedure for normalization, migrations, indexes, review

07_Database.md
→ F7Hub-specific database rules

08_ERD.md
→ F7Hub entities and relationships

09_SQLSchema.md
→ exact F7Hub schema
```

Both may be needed.

---

# 121. Archived Documentation

Archived documents may live under:

```text
Docs\Archive\
```

or:

```text
Docs\Archive\PreviousVersions\
```

Archived content may provide historical context.

It must not be treated as current architecture.

---

# 122. Research Documents

Supporting research may live under:

```text
Docs\Research\
```

Research is evidence and reference material.

It is not automatically approved architecture.

Relevant conclusions should be incorporated into the canonical owner document.

---

# 123. Diagrams

Recommended location:

```text
Docs\Assets\Diagrams\
```

Potential categories:

```text
Architecture
Sequence
State
Component
Deployment
Database
Class
Activity
```

Canonical Markdown remains the textual source of truth.

---

# 124. Mockups

Recommended location:

```text
Docs\Assets\Mockups\
```

Mockups illustrate desired UX.

They do not prove implementation.

---

# 125. Screenshots

Recommended location:

```text
Docs\Assets\Screenshots\
```

Screenshots may provide evidence of implemented behavior but can become stale.

Use them carefully.

---

# 126. Current Official Documentation Rule

For technologies and APIs that change over time, verify current official documentation before implementation.

Examples:

```text
Microsoft Graph
Exchange Online
Intune
Defender
OpenAI APIs
PyQt6
Python
SQLite
GitHub
```

F7Hub documentation defines project intent.

It does not freeze external technology behavior indefinitely.

---

# 127. Documentation Metadata

A future optional metadata format may resemble:

```yaml
---
document_id: DOC-07
title: Database Architecture
status: REVIEW
authority: DATABASE
version: 0.1
last_reviewed: 2026-09-02
depends_on:
  - DOC-02
  - DOC-06
  - DOC-08
  - DOC-09
---
```

Do not mechanically add metadata to all files until the schema is explicitly approved.

---

# 128. Documentation Readiness

Before a major implementation area begins, assess:

```text
READY
PARTIALLY READY
NOT READY
```

Example:

```text
Database implementation readiness

02 Product Requirements     READY
04 User Workflows           READY
06 System Architecture      READY
07 Database                 READY
08 ERD                      READY
09 SQL Schema               REVIEW REQUIRED
13 Python Architecture      READY
15 Naming Conventions       READY
```

Readiness should reflect content quality, not file existence.

---

# 129. Review Gate 1: Product

Review:

```text
00
01
02
03
04
```

Question:

> Do we know what F7Hub is supposed to accomplish?

---

# 130. Review Gate 2: Architecture

Review:

```text
05
06
10
14
15
```

Question:

> Do the application boundaries, interface direction, folder organization, and design standards agree?

---

# 131. Review Gate 3: Database

Review:

```text
07
08
09
```

Question:

> Are persistence rules, relationships, and exact schema consistent?

This gate must be completed before the first production-oriented schema migration is implemented.

---

# 132. Review Gate 4: Technology Ownership

Review:

```text
11
12
13
```

Question:

> Is responsibility clearly separated between AutoHotkey v2, PowerShell, and Python/PyQt6?

---

# 133. Review Gate 5: Planning

Review:

```text
16
17
18
19
```

Question:

> Do we know what comes next, what is actionable now, what changed, and where to find the relevant docs?

---

# 134. Agent Navigation Protocol

When a coding agent receives a significant task:

```text
1. Read AGENTS.md.
2. Read ROOT.md if project orientation is needed.
3. Read Docs/19_DocumentationIndex.md.
4. Identify the task category.
5. Select the minimum sufficient canonical docs.
6. Read related dependency references only as necessary.
7. Inspect the actual implementation.
8. Search for existing functionality.
9. Inspect relevant tests.
10. Distinguish FACT / ASSUMPTION / INFERENCE / RECOMMENDATION.
11. Create a focused plan.
12. Implement only the approved scope.
13. Run appropriate tests.
14. Review architecture, security, and duplication.
15. Perform documentation impact analysis.
16. Synchronize affected canonical docs.
17. Update 17_Todo.md and 18_ChangeLog.md when appropriate.
18. Report result using PASS / FAIL / NOT RUN / BLOCKED.
```

Agents should not blindly load all 20 documents.

---

# 135. Agent Scope Rule

Reading a related document does not authorize unrelated refactoring.

Example:

A ticket repository task should not automatically redesign:

```text
GUI
PowerShell
AutoHotkey
AI
Plugins
```

unless the requested scope requires it.

---

# 136. Repository Inspection Rule

Documentation defines intended architecture.

Inspection verifies actual repository state.

Always combine:

```text
Documentation
+
Repository Inspection
```

before implementation.

If something has not been inspected:

```text
Not verified.
```

---

# 137. First Programming Reading Set

For the recommended first implementation task:

```text
SQLite bootstrap and migration infrastructure
```

Read:

```text
AGENTS.md
ROOT.md
Docs/19_DocumentationIndex.md
Docs/07_Database.md
Docs/09_SQLSchema.md
Docs/10_FolderStructure.md
Docs/13_PythonArchitecture.md
Docs/15_NamingConventions.md
```

Then inspect:

```text
Database\
Python\
Tests\
Tools\
```

---

# 138. Second Programming Reading Set

For:

```text
Taxonomy, Companies and Contacts persistence
```

Read:

```text
02_ProductRequirements.md
04_UserWorkflows.md
07_Database.md
08_ERD.md
09_SQLSchema.md
13_PythonArchitecture.md
15_NamingConventions.md
```

---

# 139. Third Programming Reading Set

For:

```text
Ticket creation persistence
```

Read:

```text
02_ProductRequirements.md
04_UserWorkflows.md
07_Database.md
08_ERD.md
09_SQLSchema.md
13_PythonArchitecture.md
15_NamingConventions.md
```

---

# 140. First GUI Reading Set

For:

```text
Minimal ticket creation UI
```

Read:

```text
04_UserWorkflows.md
05_GUI.md
06_SystemArchitecture.md
13_PythonArchitecture.md
15_NamingConventions.md
```

---

# 141. First PowerShell Reading Set

For:

```text
PowerShell result contract and first diagnostic
```

Read:

```text
06_SystemArchitecture.md
10_FolderStructure.md
12_PowerShellArchitecture.md
13_PythonArchitecture.md
15_NamingConventions.md
```

---

# 142. First AutoHotkey Reading Set

For:

```text
F7 launch/focus
```

Read:

```text
06_SystemArchitecture.md
10_FolderStructure.md
11_AHKArchitecture.md
15_NamingConventions.md
```

---

# 143. Documentation Maintenance Rules

Update `19_DocumentationIndex.md` when:

- a canonical document is added
- a canonical document is removed
- a canonical document is renamed
- ownership changes
- major task-routing changes
- a new major subsystem gets canonical documentation
- agents repeatedly struggle to locate the correct source of truth

Do not update this index for every minor text change.

---

# 144. Index Accuracy Rule

If a canonical document is renamed, moved, or replaced:

```text
update 19_DocumentationIndex.md immediately
```

This file must not point to stale filenames.

---

# 145. Documentation Anti-Patterns

Avoid:

```text
duplicated authoritative rules
obsolete routing
unreviewed archived docs treated as current
every doc repeating the full architecture
planning docs defining exact schema
GUI docs defining database constraints
technology docs contradicting system architecture
```

Documentation should reduce ambiguity, not multiply it.

---

# 146. Pre-Programming Documentation Checklist

Before substantial implementation begins:

```text
[x] Canonical 00–19 files created
[x] Cross-document consistency review
[x] 09_SQLSchema.md detailed review
[x] ROOT.md final review
[x] AGENTS.md final review
[ ] Mermaid diagram organization
[x] Repository inspection
[x] Git baseline
[x] Existing Python runtime located and used for isolated infrastructure tests
```

Consistency review work is complete. Document acceptance remains `REVIEW` pending user approval. The local Git baseline, migration infrastructure, migrations through the ticket-core schema in `0004_tickets.sql`, and company/contact repositories are verified. Publication of local `main` to an upstream branch remains pending.

The next implementation target is:

```text
Ticket creation persistence through a tested `TicketRepository` boundary, followed by `TicketService` validation and transaction coordination
```

---

# 147. Final Documentation Map

```text
                    AGENTS.md
                        │
                        ▼
                     ROOT.md
                        │
                        ▼
          19_DocumentationIndex.md
                        │
        ┌───────────────┼────────────────┐
        │               │                │
        ▼               ▼                ▼
    PRODUCT          ARCHITECTURE      PLANNING
  00–04              05–15             16–18
        │               │                │
        └───────────────┼────────────────┘
                        ▼
               Relevant Specification
                        │
                        ▼
               Repository Inspection
                        │
                        ▼
                      Plan
                        │
                        ▼
                  Implementation
                        │
                        ▼
                      Tests
                        │
                        ▼
                     Review
                        │
                        ▼
             Documentation Sync
```

Conceptually:

```text
AGENTS.md
→ HOW agents work

ROOT.md
→ WHAT F7Hub is and where to begin

19_DocumentationIndex.md
→ WHICH documentation to consult

00–18 canonical docs
→ WHAT F7Hub specifies, plans, and records

Source code
→ WHAT F7Hub implements

Tests
→ WHAT F7Hub verifies

18_ChangeLog.md
→ WHAT meaningfully changed
```

---

# 148. Final Principle

The documentation system is successful when a new developer or coding agent can determine:

1. What F7Hub is.
2. Why it exists.
3. What it must do.
4. How technicians use it.
5. How it is architected.
6. Which technology owns each responsibility.
7. Where a specific decision is documented.
8. Which implementation should be inspected.
9. Which tests validate that implementation.
10. What should be built next.
11. What has already changed.
12. Which documents must be synchronized after a change.

The guiding principle is:

> F7Hub documentation should function as a navigable system of authority, not a pile of Markdown files. A developer or coding agent should be able to locate the correct source of truth quickly, inspect reality, make a focused change, validate it, and leave the project easier to understand than before.
