# F7Hub Roadmap

> Document: `Docs/16_Roadmap.md`  
> Project: F7Hub  
> Purpose: Define the recommended development sequence for F7Hub from documentation and database foundation through a useful technician application, automation, diagnostics, Microsoft integrations, AI assistance, packaging, and later extensibility.  
> Related Documents: `00_ProjectVision.md`, `01_Project.md`, `02_ProductRequirements.md`, `03_Features.md`, `04_UserWorkflows.md`, `06_SystemArchitecture.md`, `07_Database.md`, `08_ERD.md`, `09_SQLSchema.md`, `10_FolderStructure.md`, `11_AHKArchitecture.md`, `12_PowerShellArchitecture.md`, `13_PythonArchitecture.md`, `14_DesignPrinciples.md`, `15_NamingConventions.md`, `17_Todo.md`, `18_ChangeLog.md`

---

# 1. Purpose

This document defines the development roadmap for F7Hub.

It answers:

> In what order should F7Hub be built so that each stage produces a useful, testable, understandable system?

The roadmap is deliberately incremental.

F7Hub should not be built in one giant implementation.

Preferred progression:

```text
Documentation
    ↓
Database Foundation
    ↓
Application Shell
    ↓
Tickets
    ↓
Knowledge
    ↓
Search
    ↓
Scripts / PowerShell
    ↓
Diagnostics
    ↓
AutoHotkey Productivity
    ↓
Microsoft Integrations
    ↓
AI Assistance
    ↓
Reporting / Packaging
    ↓
Plugins / Advanced Integrations
```

---

# 2. Roadmap Philosophy

The roadmap follows these principles:

```text
small slices
→ working capability
→ tests
→ review
→ documentation
→ next slice
```

Each phase should create a usable or architecturally meaningful result.

Avoid phases that produce large amounts of unconnected infrastructure with no demonstrated workflow.

---

# 3. Roadmap Status Vocabulary

Use:

```text
PLANNED
IN PROGRESS
IMPLEMENTED
VERIFIED
DEFERRED
REJECTED
NOT VERIFIED
```

A phase is not `VERIFIED` until its required validation has actually been executed.

Validation and test results use `PASS`, `FAIL`, `NOT RUN`, or `BLOCKED`.

---

# 4. Current Project Status

Repository inspection and tests through 2026-09-09 verify the Python SQLite foundation, migrations through `0006_knowledge_search.sql`, the company/contact and ticket workflows, and Knowledge create/read/edit/history/link/unlink/search. PowerShell integration remains unimplemented.

```text
Documentation consistency review: IN PROGRESS
Phase 1A migration infrastructure: VERIFIED
Phase 1B taxonomy and company/contact persistence: VERIFIED
Phase 1C ticket-core schema migration: VERIFIED
Ticket creation repository/service boundary: VERIFIED
Ticket notes/status/resolution/reopening repository and service boundary: VERIFIED
Minimal ticket creation GUI: VERIFIED
Minimal application bootstrap and MainWindow: VERIFIED
Saved-ticket workspace and background service runner: VERIFIED
Reference-aware company/contact ticket creation: VERIFIED
Ticket category selection, persistence and reopened label: VERIFIED
Quick active-company creation from New Ticket: VERIFIED
AutoHotkey F7 launch/focus shortcut: VERIFIED
Relational knowledge schema migration: VERIFIED
Knowledge current-article FTS5 migration and search: VERIFIED
Remaining application implementation: PLANNED
```

---

# 5. Roadmap Layers

After Slice 015, the verified milestone is **CURRENT KNOWLEDGE ARTICLES ARE SEARCHABLE AND OPEN AUTHORITATIVELY**. Migration 0006 indexes current article code/title/summary/body, backfills existing rows and synchronizes insert/update/delete. Plain input is safely tokenized, lightweight ranked results open through the existing current-detail boundary, and history remains separately readable. Fresh sequential regression on 2026-09-09: Database 262, GUI 85, Integration 77 = 424 PASS. Native Windows workflow and all nine post-fix captures passed at 1000×700 against isolated SQLite.

Recommended next bounded slice: **Slice 016 — publish a DRAFT Knowledge article**. Add one explicit DRAFT → PUBLISHED transition through the existing GUI/service/repository boundary, set `published_at` atomically, preserve current content/history and verify search/list/link behavior afterward. Archiving, unpublishing, restore/revert, categories/tags and broader lifecycle management remain outside that slice. Recommendation only; do not implement Slice 016 here.

The F7Hub roadmap is organized into:

```text
Phase 0
→ Documentation Foundation

Phase 1
→ Database Foundation

Phase 2
→ Python Application Foundation

Phase 3
→ First Useful Vertical Slice

Phase 4
→ Company and Contact Context

Phase 5
→ Knowledge Base

Phase 6
→ Universal Search

Phase 7
→ Script Registry

Phase 8
→ PowerShell Execution Foundation

Phase 9
→ Diagnostic Engine

Phase 10
→ AutoHotkey v2 Productivity Layer

Phase 11
→ Microsoft 365 Foundation

Phase 12
→ Controlled Remediation

Phase 13
→ AI Assistance

Phase 14
→ Clipboard and Prompt Library

Phase 15
→ Reporting

Phase 16
→ Workspace and GUI Refinement

Phase 17
→ External PSA and RMM Integrations

Phase 18
→ Plugin Architecture

Phase 19
→ Packaging

Phase 20
→ Release Process
```

Phases may overlap slightly when dependencies are clear, but the architecture should not skip foundational work.

---

# 6. Phase 0: Documentation Foundation

## Objective

Establish reliable project rules before major implementation.

## Scope

Complete and align the canonical documentation set:

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

Also establish:

```text
AGENTS.md
ROOT.md
.agents\skills\
```

where appropriate.

---

# 7. Phase 0 Acceptance Criteria

Phase 0 is complete when:

```text
[ ] Canonical documentation set exists
[ ] Document responsibilities do not significantly overlap
[ ] Architecture boundaries are consistent
[ ] Technology ownership is explicit
[ ] Folder structure is defined
[ ] Database design process is defined
[ ] Coding-agent guidance is defined
[ ] Documentation index maps tasks to docs
```

---

# 8. Phase 0 Result

Expected result:

```text
F7Hub has a reliable design specification
before implementation begins.
```

Status:

```text
IN PROGRESS
```

---

# 9. Phase 1: Database Foundation

## Objective

Build the SQLite foundation safely and incrementally.

Do not attempt to implement every conceptual entity at once.

---

# 10. Phase 1A: Migration Infrastructure

Implement:

```text
database creation
migration discovery
migration ordering
schema_migrations tracking
migration checksum validation
foreign key enforcement
busy timeout configuration
transactional migration execution
migration failure handling
```

First versioned application-schema migration:

```text
0001_core.sql
→ application_metadata
```

`schema_migrations` remains bootstrap-owned migration-engine infrastructure and is not duplicated in `0001_core.sql`. The exact migration strategy belongs in `07_Database.md` and `09_SQLSchema.md`.

```text
0001_core.sql: VERIFIED — 2026-09-03 — full database suite PASS, 40 tests
```

---

# 11. Phase 1A Acceptance Criteria

```text
[x] Empty database can be created
[x] PRAGMA foreign_keys = ON is verified
[x] Migration state is recorded
[x] Migrations execute in order
[x] Failed migration does not silently corrupt schema
[x] Migration tests exist
```

Status:

```text
VERIFIED — 2026-09-03 — 28 isolated database infrastructure tests passed
```

---

# 12. Phase 1B: Taxonomy, Company and Contact Model

Implement shared taxonomy and the first core context entities:

```text
categories
tags
companies
contacts
```

Implement this phase as separate vertical slices:

```text
0002_taxonomy.sql
→ categories
→ tags

0003_companies_contacts.sql
→ companies
→ company_notes
→ company_links
→ contacts
```

Implementation status:

```text
0002_taxonomy.sql: VERIFIED — 2026-09-03 — full database suite PASS, 49 tests
0003_companies_contacts.sql: VERIFIED — 2026-09-03 — full database suite PASS, 59 tests
CompanyRepository and ContactRepository: VERIFIED — 2026-09-03 — 10 focused repository tests; 69 full database tests
```

Include:

- primary keys
- required constraints
- foreign keys
- indexes justified by expected queries
- repository tests

---

# 13. Phase 1C: Ticket Core

Implement:

```text
tickets
ticket_notes
ticket_status_history
```

Potential additional table only if required by the first workflow:

```text
ticket_timeline_events
```

Do not build attachments, relationships, advanced taxonomy, and external sync prematurely.

```text
0004_tickets.sql: VERIFIED — 2026-09-03 — 10 focused tests; 79 full database tests
TicketRepository and TicketService creation boundary: VERIFIED — 2026-09-04 — 11 focused tests; 101 full database tests
```

---

# 14. Phase 1 Acceptance Criteria

Database foundation is ready when:

```text
[x] Companies persist correctly
[x] Contacts persist correctly
[x] Tickets persist correctly
[ ] Ticket notes persist correctly
[x] Ticket status history is preserved for creation
[x] FK failures are tested
[x] Required indexes exist
[x] Ticket creation transactions are tested
[ ] Schema docs match implementation
```

---

# 15. Phase 1 Deliverable

A tested SQLite database capable of supporting the first useful ticket workflow.

Expected dependency chain:

```text
Migration
→ Schema
→ Repository
→ Tests
```

---

# 16. Phase 2: Python Application Foundation

## Objective

Create the smallest working PySide6 application architecture.

---

# 17. Phase 2A: Python Environment

Establish:

```text
supported Python version
virtual environment
dependency definition
PySide6 dependency
test framework
package entry point
```

Do not add a large dependency list.

```text
Python 3.14.6 development environment: VERIFIED
PySide6 6.11.2 dependency: VERIFIED
unittest-based test framework: VERIFIED
Package entry point: VERIFIED
```

---

# 18. Phase 2B: Application Bootstrap

Implement:

```text
application startup
configuration loading
logging initialization
database initialization
migration check
service construction
QApplication
MainWindow
shutdown flow
```

---

# 19. Phase 2C: Main Application Shell

Initial GUI:

```text
Menu Bar
Toolbar / Command Area
Navigation
Main Workspace
Status Bar
```

Dockable panels may begin minimally.

Do not implement every future dock at once.

---

# 20. Phase 2 Acceptance Criteria

```text
[x] F7Hub starts successfully
[x] Main window opens
[x] SQLite initializes
[x] Migrations execute safely
[ ] Logging initializes
[x] Application closes cleanly
[x] Startup failure produces useful error
[x] Basic application startup test exists
```

---

# 21. Phase 2 Result

At this stage, F7Hub becomes a real application rather than only architecture and database files.

The GUI may still be sparse.

That is acceptable.

---

# 22. Phase 3: First Useful Vertical Slice

## Objective

Implement ticket creation end-to-end.

This is the first major proof of the application architecture.

---

# 23. Phase 3A: Ticket Creation

Build:

```text
Ticket Form
    ↓
TicketService
    ↓
TicketRepository
    ↓
SQLite
```

Required behavior:

- create ticket
- validate required fields
- optionally associate company/contact
- record initial status
- display successful result

---

# 24. Phase 3B: Ticket List

Implement:

```text
ticket list
basic filters
open ticket
refresh
```

Use a Qt model/view implementation where appropriate.

---

# 25. Phase 3C: Ticket Detail

Implement:

```text
subject
description
status
company
contact
created time
notes
status history
```

---

# 26. Phase 3D: Ticket Notes

Add:

```text
new note
note history
timestamps
```

This is a high-value technician workflow.

Repository and service operations were verified on 2026-09-04: note creation/reload, metadata, timeline references, ticket activity timestamps and atomic rollback. The notes editor/history GUI remains planned.

---

# 27. Phase 3E: Ticket Status

Implement controlled status changes.

Example:

```text
OPEN
→ IN_PROGRESS
→ RESOLVED
→ CLOSED
```

Exact statuses should be defined in the schema and requirements.

The initial service transition policy is implemented and verified on 2026-09-04, including required resolution summaries, closure and the approved reopening of RESOLVED/CLOSED tickets to OPEN. Status/history/timeline writes are atomic; prior resolutions survive reopening. Saved-ticket GUI controls and the create/note/resolve/close/reopen flow are verified by automated tests on 2026-09-05. Native Windows visual/input checks passed on 2026-09-05 at the initial size and 1000×700. See `13_PythonArchitecture.md` for the exact service policy.

---

# 28. Phase 3 Acceptance Criteria

```text
[ ] Ticket can be created
[ ] Ticket appears in list
[ ] Ticket can be opened
[ ] Notes can be added
[ ] Status can be changed
[ ] History is preserved
[ ] Invalid data is rejected
[ ] Persistence survives application restart
[ ] Success and failure tests exist
```

---

# 29. Phase 3 Result

F7Hub now has its first genuinely useful workflow.

```text
Receive issue
→ create ticket
→ work ticket
→ add notes
→ change status
```

This should be considered a major architectural checkpoint.

---

# 30. Phase 4: Company and Contact Context

## Objective

Make ticket work contextual.

Add:

```text
company detail
contact detail
ticket relationships
recent tickets by company
recent tickets by contact
```

---

# 31. Phase 4 Acceptance Criteria

```text
[x] Ticket can reference company
[x] Ticket can reference contact
[ ] Company view lists relevant tickets
[ ] Contact view lists relevant tickets
[ ] Relationships preserve integrity
```

---

# 32. Phase 5: Knowledge Base

## Objective

Create reusable technician knowledge.

---

# 33. Phase 5A: Knowledge Articles

Relational schema foundation:

```text
knowledge_articles
knowledge_article_versions
knowledge_article_links
knowledge_article_relationships
ticket_knowledge_articles
knowledge_article_tags
```

```text
0005_knowledge.sql: VERIFIED — 2026-09-04 — 11 focused tests; 90 full database tests
KnowledgeRepository/Service and create/list/read workspace: VERIFIED — Slice 010
DRAFT editing with atomic snapshots and stale-edit protection: VERIFIED — Slice 011
RELATED ticket/article link/list/open: VERIFIED — Slice 012
Confirmed RELATED unlink and normal relink: VERIFIED — Slice 013
Read-only history viewer: VERIFIED — Slice 014
Current-article FTS5 search/result/open: VERIFIED — Slice 015
Restore/revert, publishing/archiving and richer relationship workflows: PLANNED
```

Initial capabilities:

- create
- edit
- view
- archive
- search
- metadata

---

# 34. Phase 5B: Knowledge Relationships

Use the verified relationship tables only through explicit application workflows:

```text
ticket_knowledge_articles
knowledge_article_tags
```

Potential later, after the scripts schema exists:

```text
knowledge_article_scripts
```

---

# 35. Phase 5C: Knowledge Workflow

Support:

```text
Ticket
→ Find KB
→ Apply KB
→ Link KB to Ticket
```

Later:

```text
Resolved Ticket
→ Draft KB Article
```

---

# 36. Phase 5 Acceptance Criteria

```text
[x] KB article can be created
[x] KB article can be edited
[x] KB article can be searched (current article content, Slice 015)
[x] Ticket can link to KB article (RELATED only, Slice 012)
[ ] Tags work if implemented
[ ] Archived articles behave correctly
```

---

# 37. Phase 6: Universal Search

## Objective

Make F7Hub information quickly discoverable.

---

# 38. Phase 6A: Search Foundation

Initial providers:

```text
tickets
companies
contacts
knowledge
```

Potential later providers:

```text
scripts
prompts
diagnostics
```

---

# 39. Phase 6B: FTS5

Implement FTS5 where justified for:

```text
knowledge article current code/title/summary/body — VERIFIED, Slice 015
ticket text
```

Potential later:

```text
script descriptions
prompts
```

Relational data remains source of truth.

---

# 40. Phase 6C: Unified Search Result

Conceptual result:

```text
type
id
title
summary
score
action
```

---

# 41. Phase 6D: Command Palette

Once search/action infrastructure is stable, introduce:

```text
command palette
```

Potential commands:

```text
ticket.new
search.open
knowledge.new
script.library
diagnostic.start
```

---

# 42. Phase 6 Acceptance Criteria

```text
[ ] Search finds tickets
[ ] Search finds companies
[ ] Search finds contacts
[ ] Search finds KB articles
[ ] Ranking is deterministic
[ ] Search works without AI
[ ] Empty and invalid queries behave safely
```

---

# 43. Phase 7: Script Registry

## Objective

Make PowerShell automation discoverable before making it powerful.

---

# 44. Phase 7A: Script Metadata

Implement script registry entities.

Potential fields:

```text
script_id
name
description
relative_path
type
runtime
risk
privilege
enabled
```

---

# 45. Phase 7B: Script Parameters

Implement metadata for required parameters.

Example:

```text
Hostname
UserPrincipalName
ComputerName
```

---

# 46. Phase 7C: Script Library GUI

Create a view where technicians can:

```text
search scripts
filter scripts
inspect description
inspect risk
inspect required parameters
```

Do not begin with arbitrary script execution.

---

# 47. Phase 7 Acceptance Criteria

```text
[ ] Script files remain source files
[ ] Metadata is persisted
[ ] Registry resolves valid relative paths
[ ] Missing script files are detected
[ ] Script search works
[ ] No arbitrary shell command execution exists
```

---

# 48. Phase 8: PowerShell Execution Foundation

## Objective

Execute approved PowerShell scripts safely.

---

# 49. Phase 8A: PowerShell Result Contract

Standardize machine-readable results.

Example:

```json
{
  "schemaVersion": 1,
  "operation": "Test-DnsHealth",
  "success": true,
  "status": "PASS",
  "message": "DNS resolution succeeded.",
  "data": {},
  "warnings": [],
  "errors": []
}
```

---

# 50. Phase 8B: PowerShell Gateway

Implement:

```text
pwsh discovery
safe argument arrays
-NoProfile
stdout capture
stderr capture
exit code
timeout
structured parsing
```

---

# 51. Phase 8C: First Diagnostic Script

Choose one narrow read-only Windows or networking diagnostic.

Recommended example:

```text
Test-DnsHealth.ps1
```

or:

```text
Get-SystemInformation.ps1
```

---

# 52. Phase 8D: Execution History

Persist useful execution metadata.

Potential:

```text
script
timestamp
duration
status
related ticket
sanitized parameters
```

---

# 53. Phase 8 Acceptance Criteria

```text
[ ] Registered script executes through gateway
[ ] shell=False or equivalent safe execution is used
[ ] Timeout is handled
[ ] stdout is parsed
[ ] invalid JSON is handled
[ ] stderr is captured
[ ] non-zero exit is handled
[ ] execution history is persisted
[ ] success and failure tests exist
```

---

# 54. Phase 9: Diagnostic Engine

## Objective

Turn individual diagnostic capabilities into structured troubleshooting workflows.

---

# 55. Phase 9A: Diagnostic Workflow Data

Implement:

```text
diagnostic_workflows
diagnostic_steps
diagnostic_conditions
diagnostic_sessions
diagnostic_responses
diagnostic_results
```

Do not implement every future workflow feature simultaneously.

---

# 56. Phase 9B: Deterministic Workflow Engine

Support initial step types:

```text
QUESTION
INSTRUCTION
CONDITION
SCRIPT
RESULT
```

---

# 57. Phase 9C: Dynamic Forms

PySide6 should render form controls based on workflow step definition.

Examples:

```text
text
boolean
selection
instruction
```

---

# 58. Phase 9D: PowerShell Integration

Workflow script step:

```text
Diagnostic Step
→ Script Registry
→ PowerShellService
→ Structured Result
→ Condition Evaluation
```

---

# 59. Phase 9E: Ticket Integration

Diagnostic sessions should optionally link to tickets.

Results may support:

- ticket timeline
- notes
- resolution evidence
- escalation evidence

---

# 60. Phase 9 Acceptance Criteria

```text
[ ] Diagnostic session can start
[ ] Step sequence is deterministic
[ ] Responses persist
[ ] Conditions choose correct next step
[ ] Registered script can run from workflow
[ ] Results persist
[ ] Session can complete
[ ] Failure can be recovered or reported
```

---

# 61. Phase 10: AutoHotkey v2 Productivity Layer

## Objective

Add high-value desktop productivity features without duplicating the Python application.

---

# 62. Phase 10A: F7 Launch / Focus

Implement the core F7 behavior:

```text
Press F7
  ↓
F7Hub running?
  ├── Yes → activate
  └── No  → launch
```

---

# 63. Phase 10B: Quick Menu

Potential:

```text
Open F7Hub
New Ticket
Search
Clipboard
Windows Tools
```

Actions should delegate to stable F7Hub command IDs where possible.

---

# 64. Phase 10C: Hotstrings

Add a small useful collection of technician text expansions.

Avoid building hundreds before observing actual use.

---

# 65. Phase 10D: Clipboard Helpers

Initial safe capabilities:

```text
paste plain text
trim text
normalize line breaks
ticket-note formatting
```

Persistent clipboard history belongs to Python/SQLite if later implemented.

---

# 66. Phase 10 Acceptance Criteria

```text
[ ] AutoHotkey v2 only
[x] F7 launches/focuses reliably (live Windows checks, 2026-09-05)
[ ] No duplicate app launch under normal test
[ ] Clipboard is preserved where required
[ ] Hotkeys avoid known conflicts
[ ] No direct core SQLite writes from AHK
```

---

# 67. Phase 11: Microsoft 365 Foundation

## Objective

Introduce Microsoft integrations after local architecture and PowerShell execution are stable.

Start read-only.

---

# 68. Phase 11A: Microsoft Graph Authentication

Implement one controlled authentication path.

Prefer:

```text
least privilege
+
interactive technician authentication
```

Exact approach must follow current Microsoft-supported guidance.

---

# 69. Phase 11B: First Graph Queries

Recommended read-only capabilities:

```text
user lookup
license information
group membership
device context
```

Choose one focused vertical slice first.

---

# 70. Phase 11C: Exchange Online

Add read-only Exchange diagnostics.

Examples:

```text
mailbox information
permissions
recipient state
```

---

# 71. Phase 11D: Entra ID

Add focused administrative diagnostics.

Examples:

```text
user state
group membership
object lookup
```

---

# 72. Phase 11E: Intune / Defender / Teams / SharePoint

Add these one at a time only after foundational authentication and gateway conventions are stable.

Recommended order should follow actual technician needs rather than technology prestige.

---

# 73. Phase 11 Acceptance Criteria

For each Microsoft integration:

```text
[ ] Current supported API/module verified
[ ] Permissions documented
[ ] Authentication tested
[ ] Read-only workflow works
[ ] Failure is isolated
[ ] Secrets are not logged
[ ] Integration can be unavailable without breaking local F7Hub
```

---

# 74. Phase 12: Controlled Remediation

## Objective

Introduce safe administrative changes only after read-only operations are proven.

---

# 75. Phase 12A: Risk and Privilege Model

Scripts should identify:

```text
risk
required privilege
target
expected impact
```

---

# 76. Phase 12B: Confirmation Workflow

Preferred:

```text
Technician chooses remediation
        ↓
F7Hub displays target + impact
        ↓
Technician confirms
        ↓
PowerShell executes
        ↓
Verification diagnostic
        ↓
Result recorded
```

---

# 77. Phase 12C: First Remediation

Choose one low-risk, reversible operation.

Do not begin with broad tenant changes.

---

# 78. Phase 12 Acceptance Criteria

```text
[ ] Target is explicit
[ ] Risk is visible
[ ] Privilege is visible
[ ] Technician confirmation occurs
[ ] Result is structured
[ ] Verification follows change
[ ] Failure does not silently hide partial completion
```

---

# 79. Phase 13: AI Assistance

## Objective

Add AI where it improves technician work without making AI part of the trusted execution path.

---

# 80. Phase 13A: AI Provider Boundary

Implement:

```text
AIService
→ AIProvider
→ provider adapter
```

Provider-specific code should remain isolated.

---

# 81. Phase 13B: First AI Use Cases

Recommended low-risk starting capabilities:

```text
ticket summary
ticket note cleanup
KB suggestion
diagnostic explanation
```

---

# 82. Phase 13C: Context Builder

Create a controlled method for selecting relevant context.

Avoid sending entire ticket databases or unrelated sensitive information.

---

# 83. Phase 13D: AI Review UX

AI output should clearly appear as:

```text
suggestion
draft
recommendation
```

not verified truth.

---

# 84. Phase 13 Acceptance Criteria

```text
[ ] AI is optional
[ ] Local features work when AI is unavailable
[ ] Context is intentionally selected
[ ] Sensitive data handling is reviewed
[ ] Responses are treated as untrusted
[ ] AI cannot directly execute PowerShell
[ ] Technician review occurs before impactful use
```

---

# 85. Phase 14: Clipboard and Prompt Library

## Objective

Expand technician productivity after the core workflows are stable.

Potential capabilities:

```text
saved snippets
clipboard transformations
prompt templates
prompt variables
contextual prompt rendering
```

Do not persist every copied clipboard item by default.

---

# 86. Phase 14 Acceptance Criteria

```text
[ ] Saved snippets are searchable
[ ] Sensitive clipboard behavior is configurable
[ ] Prompt variables validate
[ ] Prompt rendering is deterministic
[ ] AI integration remains optional
```

---

# 87. Phase 15: Reporting

## Objective

Turn structured application and administrative data into useful technician reports.

Potential reports:

```text
ticket activity
script executions
diagnostic outcomes
KB usage
administrative data exports
```

---

# 88. Reporting Architecture

Preferred:

```text
Repository / Integration / PowerShell
              ↓
       Structured Data
              ↓
        ReportService
              ↓
       Export Formatter
              ↓
        Data\Exports\
```

---

# 89. Phase 15 Acceptance Criteria

```text
[ ] Reports are derived from structured data
[ ] Exports do not become source of truth
[ ] Output filenames are predictable
[ ] Sensitive data is reviewed
[ ] Large reports do not freeze GUI
```

---

# 90. Phase 16: Workspace and GUI Refinement

## Objective

Improve productivity after the underlying modules are useful.

Potential:

```text
dockable layouts
workspace profiles
context panel
PowerShell output panel
activity panel
keyboard navigation
saved layouts
```

---

# 91. Workspace Profiles

Potential profiles:

```text
Helpdesk
Microsoft 365
Networking
Knowledge
Automation
AI
```

Only create profiles that have real workflow value.

---

# 92. Phase 16 Acceptance Criteria

```text
[ ] Layout persists
[ ] Layout restores safely
[ ] Missing panel does not corrupt workspace
[ ] Keyboard navigation remains functional
[ ] User can reset layout
```

---

# 93. Phase 17: External PSA and RMM Integrations

## Objective

Integrate F7Hub with external operational platforms.

Possible future providers:

```text
HaloPSA
NinjaOne
```

These should be introduced only after local ticket context and external gateway conventions are proven.

---

# 94. Initial Integration Strategy

Prefer:

```text
read
→ link
→ refresh
```

before:

```text
bidirectional automatic synchronization
```

---

# 95. External Mapping

Use F7Hub internal IDs separately from provider IDs.

Example:

```text
ticket_id
+
provider
+
external_ticket_id
```

Avoid making an external provider's ID the core F7Hub primary key.

---

# 96. Phase 17 Acceptance Criteria

```text
[ ] Provider API is supported
[ ] Authentication model is documented
[ ] External IDs are mapped cleanly
[ ] Provider failure is isolated
[ ] Conflict behavior is defined
[ ] Sync does not silently overwrite newer data
```

---

# 97. Phase 18: Plugin Architecture

## Objective

Introduce plugins only after concrete extension requirements exist.

Do not build the plugin system merely because future integrations are imaginable.

---

# 98. Plugin Architecture Questions

Before implementation, define:

```text
What is extensible?
How are plugins discovered?
How are they enabled?
What permissions do they receive?
What version contracts exist?
How are failures isolated?
What APIs are exposed?
```

---

# 99. Phase 18 Acceptance Criteria

```text
[ ] At least one real plugin use case exists
[ ] Extension points are explicit
[ ] Plugins do not receive unrestricted database access by default
[ ] Plugin compatibility is versioned
[ ] Plugin failure does not crash core app where practical
```

---

# 100. Phase 19: Packaging

## Objective

Turn the development project into a reproducible Windows application package.

Potential work:

```text
Python packaging
application executable
PyQt resources
PowerShell inclusion
AHK inclusion
configuration defaults
runtime directory creation
```

---

# 101. Runtime Separation

Installed application should not require:

```text
C:\Dev\F7Hub\
```

Potential application data location:

```text
%LOCALAPPDATA%\F7Hub\
```

Potential runtime data:

```text
Data
Logs
Database
Cache
Attachments
```

---

# 102. Phase 19 Acceptance Criteria

```text
[ ] Application installs on clean supported Windows environment
[ ] Development paths are not required
[ ] Runtime DB is created correctly
[ ] Migrations run
[ ] Required PowerShell scripts are available
[ ] AutoHotkey integration works if included
[ ] Upgrade preserves user data
[ ] Uninstall behavior is defined
```

---

# 103. Phase 20: Release Process

## Objective

Create controlled versioned releases.

Use semantic versioning.

Examples:

```text
0.1.0-alpha
0.2.0
0.5.0-beta
1.0.0
```

---

# 104. Release Requirements

A release should include:

```text
version
change summary
known issues
migration information
test status
release artifacts
```

---

# 105. Alpha Milestone

A practical alpha should probably include:

```text
Application shell
SQLite
Tickets
Companies
Contacts
Ticket notes
Basic KB
Basic search
Settings
Logging
```

This is already useful without AI or Microsoft cloud integration.

---

# 106. Automation Alpha Milestone

A later milestone may add:

```text
Script registry
PowerShell gateway
basic Windows diagnostics
execution history
AutoHotkey launch/focus
```

---

# 107. Diagnostic Beta Milestone

Potential:

```text
Diagnostic Engine
dynamic forms
workflow persistence
PowerShell diagnostic steps
ticket-linked results
```

---

# 108. Microsoft Beta Milestone

Potential:

```text
Graph read-only integration
Exchange diagnostics
Entra queries
selected Microsoft administration workflows
```

---

# 109. AI Beta Milestone

Potential:

```text
ticket summaries
KB suggestions
diagnostic explanation
prompt library
```

AI should remain optional.

---

# 110. 1.0 Direction

A reasonable F7Hub 1.0 should represent:

```text
a stable technician productivity platform
```

rather than:

```text
every imagined F7Hub feature
```

Potential 1.0 capability set:

```text
tickets
companies
contacts
knowledge
search
PowerShell script library
diagnostics
AHK productivity
selected Microsoft administration
settings
logging
reporting
stable packaging
```

Plugins and broad third-party integrations do not need to block 1.0.

---

# 111. Roadmap Dependency Graph

Simplified:

```text
Documentation
     ↓
SQLite Foundation
     ↓
Python Application
     ↓
Ticket Workflow
     ↓
Knowledge
     ↓
Search
     ↓
Script Registry
     ↓
PowerShell Execution
     ↓
Diagnostics
     ↓
Microsoft Integration
     ↓
Controlled Remediation
     ↓
AI Assistance
```

AHK productivity can begin after the Python application has a stable launch/command boundary.

---

# 112. What Should Not Be Built First

Do not begin implementation with:

```text
AI assistant
plugin marketplace
100-table database
HaloPSA synchronization
NinjaOne synchronization
complex dock layouts
tenant-wide remediation
large reporting system
```

These depend on simpler foundations.

---

# 113. Database Roadmap Rule

Do not create every conceptual table from `08_ERD.md` in one migration.

Implement database domains as required by vertical slices.

Preferred progression:

```text
Migration Infrastructure
↓
Companies / Contacts
↓
Tickets / Notes / Status
↓
Knowledge
↓
Tags
↓
Scripts
↓
Diagnostics
↓
Prompts / Clipboard / Workspaces
↓
Integrations / Audit as required
```

---

# 114. GUI Roadmap Rule

Do not build every GUI module before backend behavior exists.

Preferred:

```text
feature requirement
↓
service/repository behavior
↓
minimal GUI
↓
test workflow
↓
refine GUI
```

---

# 115. PowerShell Roadmap Rule

PowerShell implementation progression:

```text
Result Contract
↓
Gateway
↓
Read-Only Windows Diagnostic
↓
Networking
↓
Execution History
↓
Graph Read-Only
↓
Exchange Read-Only
↓
Other Microsoft Services
↓
Controlled Remediation
```

---

# 116. AutoHotkey Roadmap Rule

AHK progression:

```text
Launch / Focus F7Hub
↓
Quick Menu
↓
Hotstrings
↓
Clipboard Helpers
↓
Command Forwarding
↓
Context-Aware Automation
```

Avoid large AHK GUIs.

---

# 117. AI Roadmap Rule

AI progression:

```text
Summarize
↓
Explain
↓
Suggest
↓
Draft
```

before considering any workflow that could affect execution.

AI should never bypass application safety boundaries.

---

# 118. Integration Roadmap Rule

External integrations should evolve:

```text
Connect
↓
Read
↓
Display
↓
Link
↓
Controlled Update
↓
Synchronization
```

Do not start with automatic bidirectional sync.

---

# 119. Testing Roadmap

Testing should grow with the system.

Early:

```text
database
repository
service
```

Then:

```text
GUI
PowerShell
integration
diagnostic workflow
```

Later:

```text
end-to-end
packaging
upgrade
release
```

---

# 120. Documentation Roadmap

Documentation should be updated continuously.

Do not wait until the project is “finished.”

For each slice:

```text
Implement
→ Test
→ Review
→ Update affected docs
```

---

# 121. Security Roadmap

Security should not be a final phase.

Security review occurs throughout.

However, deeper security work will become especially important before:

```text
Microsoft authentication
remediation
AI data transmission
external integrations
plugins
packaging
```

---

# 122. Performance Roadmap

Do not optimize prematurely.

Potential performance work should follow measured needs in:

```text
search
ticket lists
database queries
PowerShell startup
cloud requests
AI requests
large exports
```

---

# 123. Deferred Ideas

Ideas should be marked `DEFERRED` when they are useful but not appropriate for the current stage.

Potential examples:

```text
plugin marketplace
persistent PowerShell runspace
bidirectional PSA sync
advanced AI agents
complex scheduling engine
multi-user server architecture
cross-platform support
```

Deferred does not mean rejected.

---

# 124. Rejected Ideas

Ideas should be marked `REJECTED` when they conflict with the approved architecture.

Examples may include:

```text
AutoHotkey as primary application GUI
PowerShell directly owning core SQLite persistence
AI executing arbitrary shell commands
arbitrary target of 100 database tables
```

---

# 125. Roadmap and Todo Difference

`16_Roadmap.md` answers:

> What major capability should come next, and in what order?

`17_Todo.md` answers:

> What specific actionable tasks are currently pending?

Roadmap items should remain relatively stable.

Todo items should change frequently.

---

# 126. Roadmap and ChangeLog Difference

`16_Roadmap.md` is forward-looking.

`18_ChangeLog.md` is historical.

Do not use the roadmap as a record of every completed code change.

---

# 127. Phase Completion Rule

A phase should not be marked complete solely because code exists.

Completion requires applicable:

```text
implementation
tests
review
documentation
```

---

# 128. Roadmap Review Rule

Review this roadmap when:

- major architecture changes
- priorities change
- new external dependencies appear
- an assumption proves incorrect
- a milestone is completed
- a major feature is deferred or rejected

Do not rewrite the roadmap after every small commit.

---

# 129. Initial Implementation Recommendation

The recommended first coding objective was completed and verified on 2026-09-03:

```text
Implement SQLite bootstrap and migration infrastructure.
```

No business-domain migration was included. Continue with independently tested persistence slices rather than building the entire database at once.

---

# 130. First Coding-Agent Task

A good first Codex task should resemble:

```text
OBJECTIVE

Implement F7Hub SQLite bootstrap and migration infrastructure.

CONTEXT

Read:
- AGENTS.md
- ROOT.md
- Docs/19_DocumentationIndex.md
- Docs/07_Database.md
- Docs/09_SQLSchema.md
- Docs/10_FolderStructure.md
- Docs/13_PythonArchitecture.md
- Docs/15_NamingConventions.md

SCOPE

- Database connection initialization
- PRAGMA foreign_keys = ON
- migration discovery
- ordered migration execution
- schema version tracking
- isolated database tests

OUT OF SCOPE

- ticket GUI
- PowerShell
- AI
- plugins
- Microsoft integrations

ACCEPTANCE CRITERIA

- empty test DB migrates successfully
- migrations run in order
- migrations are not rerun incorrectly
- foreign keys are enabled
- failure path is tested

VALIDATION

Run database test suite.

DELIVERABLES

Implementation
Tests
Documentation updates
```

This is preferable to:

```text
Build F7Hub.
```

---

# 131. Second Coding Slice

After migration infrastructure:

```text
Implement companies and contacts persistence,
including migrations, repositories,
validation, and tests.
```

---

# 132. Third Coding Slice

Then:

```text
Implement ticket creation persistence,
including ticket migration,
TicketRepository,
TicketService,
validation,
and tests.
```

---

# 133. Fourth Coding Slice

Then:

```text
Implement minimal PySide6 ticket creation GUI
using the existing TicketService.
```

```text
Status: VERIFIED — 2026-09-04 — 5 GUI tests; 1 GUI-to-database integration test
```

This completes the first ticket-creation vertical slice.

The minimal application-shell follow-up was completed and verified on 2026-09-04:

```text
Status: VERIFIED — 7 GUI tests; 5 application and GUI integration tests
```

Full navigation, toolbar and logging work remain planned within Phase 2.

---

# 134. Development Milestone Model

A practical milestone pattern:

```text
Architecture
    ↓
Persistence
    ↓
Service
    ↓
GUI
    ↓
Test
    ↓
Documentation
```

Repeat for each major capability.

---

# 135. Recommended Early Milestones

```text
M0
Documentation Foundation

M1
SQLite Bootstrap

M2
Taxonomy / Company / Contact Persistence

M3
Ticket Persistence

M4
PySide6 Application Shell

M5
Ticket Creation Workflow

M6
Ticket Notes / Status

M7
Knowledge Base

M8
Universal Search

M9
Script Registry

M10
PowerShell Execution

M11
Diagnostic Engine

M12
AutoHotkey Productivity

M13
Microsoft Read-Only Integration

M14
Controlled Remediation

M15
AI Assistance

M16
Packaging / Alpha Release
```

Exact milestone numbering may evolve.

---

# 136. Milestone Definition of Done

Each milestone should answer:

```text
What was built?
What was tested?
What failed?
What documentation changed?
What remains?
```

---

# 137. Roadmap Risk: Overengineering

Primary risk:

```text
building too much architecture before enough real workflow exists
```

Mitigation:

```text
small vertical slices
+
inspect-before-create
+
review before major architectural additions
```

---

# 138. Roadmap Risk: Documentation Drift

Risk:

```text
code evolves but canonical docs remain old
```

Mitigation:

```text
documentation update as part of completion
```

---

# 139. Roadmap Risk: Database Overdesign

Risk:

```text
building many speculative entities
before queries and workflows are understood
```

Mitigation:

```text
schema by vertical slice
```

---

# 140. Roadmap Risk: AI Too Early

Risk:

```text
AI hides incomplete deterministic application architecture
```

Mitigation:

```text
build tickets, KB, search, scripts,
and diagnostics first
```

---

# 141. Roadmap Risk: Microsoft Complexity

Risk:

```text
cloud authentication and permissions
consume development effort too early
```

Mitigation:

```text
prove local architecture first
then add one read-only integration at a time
```

---

# 142. Roadmap Risk: Cross-Language Duplication

Risk:

```text
Python, PowerShell, and AHK
all begin implementing the same responsibilities
```

Mitigation:

```text
respect technology ownership
```

---

# 143. Roadmap Risk: Giant Agent Prompts

Risk:

```text
coding agent makes unrelated changes
across the entire repository
```

Mitigation:

```text
small task
clear scope
explicit out-of-scope
validation
review
```

---

# 144. Roadmap Risk: Untested Claims

Risk:

```text
features are called complete
because code was generated
```

Mitigation:

Use:

```text
PASS
FAIL
NOT RUN
BLOCKED
```

and distinguish:

```text
IMPLEMENTED
```

from:

```text
VERIFIED
```

---

# 145. Current Near-Term Sequence

The recommended immediate sequence is:

```text
1. Establish and review the Git baseline
2. Implement the taxonomy required by the next persistence slice
3. Implement companies and contacts persistence
4. Add focused migration, repository, validation and failure-path tests
5. Synchronize the affected database documentation
```

---

# 146. Roadmap Golden Rules

1. Do not build F7Hub in one prompt.
2. Build vertical slices.
3. Prove architecture early.
4. Build useful local features before cloud complexity.
5. Build read-only administration before remediation.
6. Build deterministic workflows before AI enhancement.
7. Implement database tables when workflows require them.
8. Keep Python as the primary application.
9. Keep PowerShell focused on administration and diagnostics.
10. Keep AutoHotkey v2 focused on desktop productivity.
11. Keep SQLite behind Python repositories.
12. Test failure paths.
13. Document completed architectural changes.
14. Avoid arbitrary complexity targets.
15. Do not mark work verified unless validation actually ran.

---

# 147. Final Roadmap Summary

The F7Hub development journey should look like:

```text
Documentation
      ↓
Database Foundation
      ↓
Python / PySide6 Shell
      ↓
Tickets
      ↓
Companies / Contacts
      ↓
Knowledge Base
      ↓
Universal Search
      ↓
Script Registry
      ↓
PowerShell
      ↓
Diagnostic Engine
      ↓
AutoHotkey v2 Productivity
      ↓
Microsoft 365
      ↓
Controlled Remediation
      ↓
AI Assistance
      ↓
Reporting
      ↓
Packaging
      ↓
External Integrations / Plugins
```

The most important principle is:

> F7Hub should grow through small, tested, useful capabilities where each new layer builds on a foundation that has already been understood and validated.
