# F7Hub Product Requirements

> Document: `Docs/02_ProductRequirements.md`  
> Project: F7Hub  
> Purpose: Define what F7Hub must accomplish as a product.  
> Scope: Functional and non-functional product requirements.  
> Related Documents: `00_ProjectVision.md`, `01_Project.md`, `03_Features.md`, `04_UserWorkflows.md`, `06_SystemArchitecture.md`

---

# 1. Purpose

This document defines the product requirements for F7Hub.

It specifies:

- required system behavior
- functional capabilities
- quality requirements
- security requirements
- data requirements
- usability requirements
- integration requirements
- testing expectations
- acceptance criteria
- scope boundaries

This document answers:

> What must F7Hub accomplish?

It does not define the complete technical implementation.

Technical implementation belongs primarily in:

- `05_GUI.md`
- `06_SystemArchitecture.md`
- `07_Database.md`
- `08_ERD.md`
- `09_SQLSchema.md`
- `11_AHKArchitecture.md`
- `12_PowerShellArchitecture.md`
- `13_PythonArchitecture.md`

---

# 2. Requirements Philosophy

Requirements should describe required outcomes rather than prematurely forcing implementation details.

Prefer:

> The system shall preserve ticket notes after application restart.

Instead of:

> The ticket form shall call `TicketRepository.SaveTicket()` when the Save button is clicked.

Implementation details may change.

Required product behavior should remain stable.

---

# 3. Requirement Status

Each requirement may use one of the following statuses:

| Status | Meaning |
|---|---|
| PLANNED | Requirement is accepted but not yet implemented |
| IN PROGRESS | Implementation has started |
| IMPLEMENTED | Requirement has been implemented |
| VERIFIED | Requirement has been tested and confirmed |
| DEFERRED | Requirement is intentionally postponed |
| REJECTED | Requirement is no longer part of the product |
| NOT VERIFIED | Implementation state has not been inspected |

Unless explicitly updated elsewhere, requirements in this document should be treated as:

`PLANNED`

---

# 4. Requirement Priority

Requirements use four priority levels.

| Priority | Meaning |
|---|---|
| P0 | Essential foundation. Product cannot function correctly without it. |
| P1 | Core product capability. Required for useful early versions. |
| P2 | Important enhancement. Valuable after core capabilities are stable. |
| P3 | Future or optional capability. |

Priority describes implementation importance, not implementation order by itself.

Dependencies must also be considered.

---

# 5. Requirement Identifier Format

Requirement IDs follow this pattern:

```text
CATEGORY-SUBSYSTEM-NUMBER
```

Examples:

```text
FR-TICKET-001
FR-KB-002
NFR-SEC-001
NFR-PERF-001
INT-M365-001
DATA-DB-001
```

Prefixes:

| Prefix | Meaning |
|---|---|
| FR | Functional Requirement |
| NFR | Non-Functional Requirement |
| DATA | Data / Database Requirement |
| INT | Integration Requirement |
| SEC | Security Requirement |
| TEST | Testing Requirement |
| DOC | Documentation Requirement |

---

# 6. Product Goals

F7Hub must help an IT technician:

1. centralize support context
2. retrieve technical information quickly
3. organize tickets and troubleshooting information
4. reuse technical knowledge
5. execute approved automation safely
6. reduce repetitive typing
7. preserve troubleshooting history
8. structure diagnostic workflows
9. interact with Microsoft administration tools
10. search across multiple information domains
11. use AI assistance without surrendering technical control
12. preserve clear architecture and documentation

---

# 7. Core User

The primary user is an IT support technician working on Windows in a Microsoft-centric support environment.

Typical responsibilities include:

- Windows support
- Microsoft 365 support
- Outlook troubleshooting
- Exchange Online
- Entra ID
- Intune
- Microsoft Defender
- network diagnostics
- account support
- ticket documentation
- script execution
- remote troubleshooting
- knowledge management

---

# 8. Core Product Domains

F7Hub is divided conceptually into the following product domains:

```text
F7Hub
│
├── Application Shell
├── Dashboard
├── Tickets
├── Companies
├── Contacts
├── Knowledge Base
├── Search
├── Diagnostics
├── Scripts
├── PowerShell
├── AutoHotkey
├── Clipboard
├── Prompts
├── AI
├── Plugins
├── Reports
├── Assets
├── Settings
├── Logs
└── External Integrations
```

Each domain should remain sufficiently independent to preserve modularity.

---

# 9. Application Shell Requirements

## FR-APP-001 — Application Startup

Priority: P0

The application shall start without requiring external cloud services to be available.

Acceptance Criteria:

- local application shell can launch
- unavailable integrations do not prevent startup
- initialization errors are reported
- startup failure does not silently terminate where recoverable
- local database initialization is validated

---

## FR-APP-002 — Main Navigation

Priority: P1

The application shall provide navigation between major F7Hub modules.

Expected modules may include:

- Dashboard
- Tickets
- Companies
- Contacts
- Knowledge Base
- Scripts
- Clipboard
- Prompts
- AI
- Database
- Plugins
- Reports
- Logs
- Settings

Acceptance Criteria:

- navigation can switch modules
- active module is visually identifiable
- switching modules does not corrupt unsaved state
- unavailable modules fail gracefully

---

## FR-APP-003 — Workspace Persistence

Priority: P2

The application shall support persistent workspace layouts.

Acceptance Criteria:

- panel layout can be saved
- saved layout can be restored
- invalid saved layouts do not prevent application startup
- workspace configuration can be reset

---

## FR-APP-004 — Dockable Panels

Priority: P2

The application should support dockable interface panels where appropriate.

Potential panel states:

- docked
- floating
- hidden
- resized
- repositioned

Acceptance Criteria:

- supported panels can change position
- layout remains usable after restart
- hidden panels can be restored

---

## FR-APP-005 — Status Information

Priority: P2

The application should display relevant application status.

Potential indicators include:

- SQLite
- PowerShell
- AI
- integrations
- active company
- active ticket
- plugin state
- application version
- current workspace

Status indicators must reflect real state rather than decorative assumptions.

---

# 10. Dashboard Requirements

## FR-DASH-001 — Dashboard Overview

Priority: P1

The system shall provide an overview of useful technician information.

Possible dashboard information:

- active tickets
- recent tickets
- recent KB articles
- frequently used scripts
- recent actions
- saved workspaces
- alerts
- shortcuts
- system status

Acceptance Criteria:

- dashboard loads without requiring all external integrations
- dashboard data is derived from available sources
- unavailable information is clearly identified

---

## FR-DASH-002 — Quick Actions

Priority: P1

The dashboard should provide configurable quick actions.

Examples:

- new ticket
- search
- open PowerShell
- run diagnostic
- open KB
- open Microsoft admin portal
- open clipboard manager

---

# 11. Ticket Requirements

## FR-TICKET-001 — Create Ticket Record

Priority: P0

The system shall support creation of a local ticket record.

Required minimum fields shall be determined by the database and workflow design.

Acceptance Criteria:

- ticket can be created
- required fields are validated
- invalid records are rejected
- ticket receives a unique identifier
- record persists after restart

---

## FR-TICKET-002 — View Ticket

Priority: P0

The system shall allow a technician to open and inspect an existing ticket.

Acceptance Criteria:

- ticket information is retrieved from persistent storage
- related information can be accessed
- missing ticket IDs are handled gracefully

---

## FR-TICKET-003 — Edit Ticket

Priority: P0

The system shall allow editable ticket information to be updated.

Acceptance Criteria:

- valid edits persist
- invalid data is rejected
- unrelated ticket data is not overwritten
- changes can be verified after reload

---

## FR-TICKET-004 — Ticket Notes

Priority: P1

The system shall support multiple notes associated with a ticket.

Potential note types:

- technician note
- troubleshooting note
- customer communication
- internal note
- resolution note
- escalation note

Acceptance Criteria:

- multiple notes can exist per ticket
- notes preserve timestamps
- notes preserve ticket relationship
- notes remain searchable where applicable

---

## FR-TICKET-005 — Ticket Timeline

Priority: P1

The system should present significant ticket-related activity chronologically.

Potential events:

- ticket created
- note added
- status changed
- diagnostic executed
- script executed
- attachment added
- KB linked
- escalation recorded
- resolution recorded

---

## FR-TICKET-006 — Ticket Attachments

Priority: P2

The system should support references to ticket-related attachments.

Attachment storage design must be explicitly defined before implementation.

The database should not automatically be used to store arbitrary large binary files.

---

## FR-TICKET-007 — Ticket Relationships

Priority: P2

Tickets should be capable of relationships with:

- companies
- contacts
- KB articles
- scripts
- diagnostic sessions
- attachments
- tags
- related tickets

---

## FR-TICKET-008 — Ticket Search

Priority: P1

The user shall be able to search ticket records.

Searchable information may include:

- ticket number
- title
- description
- notes
- company
- contact
- tags

---

## FR-TICKET-009 — Ticket Resolution

Priority: P1

The system should support recording a resolution.

Resolution data should remain distinct from arbitrary troubleshooting notes where appropriate.

---

## FR-TICKET-010 — Ticket Escalation Information

Priority: P2

The system should support structured escalation information.

Possible information:

- escalation reason
- troubleshooting performed
- diagnostic results
- relevant logs
- attempted remediation
- recommended next step

---

# 12. Company Requirements

## FR-COMPANY-001 — Company Records

Priority: P1

The system shall support company records.

Possible company information:

- company name
- aliases
- notes
- technical environment
- links
- domains
- escalation information
- administrative references

---

## FR-COMPANY-002 — Company Context

Priority: P1

When a ticket is associated with a company, relevant company context should be accessible from the ticket workspace.

---

## FR-COMPANY-003 — Company Relationships

Priority: P1

Companies should be capable of relationships with:

- contacts
- tickets
- KB articles
- bookmarks
- technical assets
- notes
- scripts
- external systems

---

# 13. Contact Requirements

## FR-CONTACT-001 — Contact Records

Priority: P1

The system shall support contact records.

Possible information:

- name
- company
- email
- phone
- title
- department
- notes
- technical context

---

## FR-CONTACT-002 — Ticket Contact Relationship

Priority: P1

Tickets should support association with one or more relevant contacts where required by the domain model.

---

## FR-CONTACT-003 — Contact History

Priority: P2

The system should allow related ticket history to be accessed from contact context.

---

# 14. Knowledge Base Requirements

## FR-KB-001 — Create Knowledge Article

Priority: P1

The user shall be able to create structured knowledge articles.

Potential article types:

- troubleshooting guide
- SOP
- known error
- command reference
- PowerShell reference
- Microsoft 365 procedure
- network procedure
- escalation guide

---

## FR-KB-002 — Edit Knowledge Article

Priority: P1

Knowledge articles shall be editable.

Acceptance Criteria:

- content changes persist
- metadata changes persist
- invalid data is rejected
- updates do not silently destroy existing content

---

## FR-KB-003 — Search Knowledge Base

Priority: P1

The system shall support fast knowledge-base search.

Search should eventually support:

- titles
- article content
- tags
- keywords
- categories
- technologies

SQLite FTS5 should be considered where appropriate.

---

## FR-KB-004 — Article Metadata

Priority: P1

Knowledge articles should support structured metadata.

Potential metadata includes:

- title
- article type
- category
- tags
- technology
- status
- creation date
- modification date
- author
- review status

---

## FR-KB-005 — Ticket-to-KB Relationship

Priority: P1

Tickets should be linkable to relevant KB articles.

---

## FR-KB-006 — Related Knowledge

Priority: P2

The system should be able to identify related KB articles using deterministic search and optionally AI-assisted ranking.

---

## FR-KB-007 — Knowledge Lifecycle

Priority: P2

Knowledge articles should eventually support lifecycle states such as:

- draft
- active
- review required
- deprecated
- archived

---

# 15. Search Requirements

## FR-SEARCH-001 — Universal Search

Priority: P1

The application shall eventually provide a unified search interface across supported F7Hub domains.

Potential sources:

- tickets
- companies
- contacts
- KB
- scripts
- prompts
- clipboard items
- bookmarks
- documentation
- commands
- plugins

---

## FR-SEARCH-002 — Search Filtering

Priority: P2

Users should be able to filter results by information domain.

Examples:

```text
Tickets
KB
Scripts
Companies
Contacts
Prompts
Clipboard
```

---

## FR-SEARCH-003 — Search Ranking

Priority: P2

Search results should be ranked by relevance.

Ranking should remain explainable enough to troubleshoot unexpected search behavior.

---

## FR-SEARCH-004 — Full-Text Search

Priority: P1

F7Hub should support full-text search for high-value textual domains where appropriate.

SQLite FTS5 is the preferred local candidate unless architecture review identifies a better justified solution.

---

## FR-SEARCH-005 — Query Normalization

Priority: P2

Search may normalize user queries to improve retrieval.

Possible normalization:

- whitespace
- capitalization
- punctuation
- abbreviations
- aliases
- technology synonyms

AI must not be required for basic search functionality.

---

# 16. Script Library Requirements

## FR-SCRIPT-001 — Script Registry

Priority: P1

F7Hub shall maintain a registry of scripts available to the technician.

Possible script types:

- PowerShell
- AutoHotkey
- Python
- command line
- approved external utility invocation

---

## FR-SCRIPT-002 — Script Metadata

Priority: P1

Each registered script should support metadata such as:

- name
- description
- language
- category
- file path
- version
- required privilege
- risk level
- parameters
- supported environment
- tags

---

## FR-SCRIPT-003 — File-Based Source

Priority: P1

Script source code should normally remain in version-controlled files.

SQLite should store metadata and execution records rather than becoming the default source-code repository.

---

## FR-SCRIPT-004 — Script Search

Priority: P1

Scripts shall be searchable.

Search criteria may include:

- name
- category
- technology
- tags
- purpose
- privilege requirement

---

## FR-SCRIPT-005 — Parameter Collection

Priority: P1

The application should provide structured parameter collection before script execution.

Acceptance Criteria:

- required parameters are identified
- input is validated
- unsafe input is rejected where applicable
- parameter values are passed without unsafe command construction

---

## FR-SCRIPT-006 — Script Execution History

Priority: P1

The system should preserve script execution history.

Possible information:

- script
- timestamp
- parameters
- ticket
- result status
- exit code
- execution duration
- operator
- sanitized output

Sensitive data must not be stored unnecessarily.

---

# 17. PowerShell Requirements

## FR-PS-001 — PowerShell Execution

Priority: P1

F7Hub shall be capable of invoking approved PowerShell scripts through a controlled execution layer.

---

## FR-PS-002 — PowerShell 7

Priority: P1

PowerShell 7 should be the preferred runtime where supported.

Windows PowerShell 5.1 may only be used when required by a specific compatibility constraint.

---

## FR-PS-003 — Structured Results

Priority: P1

Diagnostic and administrative scripts should return structured output where practical.

Preferred interchange format:

```json
{
  "success": true,
  "status": "PASS",
  "message": "Diagnostic completed",
  "data": {},
  "warnings": [],
  "errors": []
}
```

Exact contracts belong in `12_PowerShellArchitecture.md`.

---

## FR-PS-004 — Error Capture

Priority: P1

PowerShell failures shall be captured and displayed meaningfully.

Errors should not be silently discarded.

---

## FR-PS-005 — Privilege Awareness

Priority: P1

The system should identify whether a PowerShell operation requires elevated or privileged access.

F7Hub must not silently elevate administrative permissions.

---

## FR-PS-006 — Microsoft Administration

Priority: P2

PowerShell integration may support administration through approved modules for:

- Microsoft Graph
- Exchange Online
- Microsoft 365
- Entra-related administration
- Microsoft Teams
- supported Microsoft services

---

# 18. AutoHotkey Requirements

## FR-AHK-001 — Global Hotkeys

Priority: P2

AutoHotkey v2 may provide global keyboard shortcuts for approved F7Hub actions.

---

## FR-AHK-002 — Hotstrings

Priority: P2

The application may support reusable text expansion through AutoHotkey v2.

---

## FR-AHK-003 — Clipboard Automation

Priority: P1

AutoHotkey may support clipboard-centric workflows such as:

- capture
- formatting
- transformation
- insertion
- templates

---

## FR-AHK-004 — Application Launching

Priority: P2

AHK may provide fast launching or focusing of external technician tools.

---

## FR-AHK-005 — Safe Automation

Priority: P1

AHK automation must avoid destructive actions without explicit intent.

---

# 19. Clipboard Requirements

## FR-CLIP-001 — Clipboard History

Priority: P1

The system should support controlled clipboard history.

---

## FR-CLIP-002 — Clipboard Snippets

Priority: P1

Users should be able to save reusable snippets.

Examples:

- ticket responses
- troubleshooting text
- commands
- escalation templates
- standard customer communication

---

## FR-CLIP-003 — Clipboard Transformation

Priority: P2

The system may provide transformations such as:

- remove formatting
- normalize whitespace
- convert to lowercase
- convert to uppercase
- format ticket notes
- extract URLs
- extract email addresses
- extract IP addresses

---

## FR-CLIP-004 — Sensitive Clipboard Handling

Priority: P0

Clipboard history must account for potentially sensitive content.

Requirements include:

- ability to exclude sensitive entries
- ability to clear history
- configurable persistence
- no assumption that all clipboard content is safe to store

---

# 20. Diagnostic Engine Requirements

## FR-DIAG-001 — Diagnostic Workflow Definitions

Priority: P1

F7Hub shall support structured diagnostic workflows.

A workflow may contain:

- questions
- conditions
- steps
- scripts
- expected results
- decision branches
- resolutions
- escalation paths

---

## FR-DIAG-002 — Dynamic Diagnostic Forms

Priority: P2

The GUI should eventually generate diagnostic forms from workflow definitions.

---

## FR-DIAG-003 — Conditional Steps

Priority: P1

Diagnostic workflows shall support conditional progression.

Example:

```text
Is Outlook opening?
│
├── Yes
│   └── Check connectivity
│
└── No
    └── Check process and profile state
```

---

## FR-DIAG-004 — Script Integration

Priority: P1

Diagnostic steps may invoke approved PowerShell scripts.

---

## FR-DIAG-005 — Structured Results

Priority: P1

Diagnostic execution should produce structured results.

Results may include:

- status
- observations
- values
- warnings
- errors
- recommended next step

---

## FR-DIAG-006 — Diagnostic Sessions

Priority: P1

Each diagnostic session should preserve relevant execution history.

A session may be associated with:

- ticket
- workflow
- technician
- start time
- end time
- answers
- script results
- final status

---

## FR-DIAG-007 — Deterministic Core

Priority: P1

Core diagnostic flow should remain deterministic where practical.

AI may assist but should not be the only mechanism deciding critical troubleshooting progression.

---

# 21. Prompt Library Requirements

## FR-PROMPT-001 — Prompt Storage

Priority: P2

The system should support reusable structured AI prompts.

---

## FR-PROMPT-002 — Prompt Metadata

Priority: P2

Prompts may include:

- title
- category
- purpose
- model/provider compatibility
- variables
- tags
- version
- description

---

## FR-PROMPT-003 — Prompt Variables

Priority: P2

Prompts should support controlled placeholders.

Example:

```text
{{ticket_title}}
{{ticket_description}}
{{company_name}}
{{diagnostic_results}}
```

---

## FR-PROMPT-004 — Prompt Preview

Priority: P2

The user should be able to inspect the final generated prompt before submission where appropriate.

---

# 22. AI Requirements

## FR-AI-001 — AI Assistance

Priority: P2

F7Hub may provide AI-assisted functionality.

Potential uses:

- summarization
- troubleshooting suggestions
- prompt generation
- note cleanup
- KB suggestions
- search assistance
- script explanation
- structured extraction

---

## FR-AI-002 — Human Review

Priority: P0

AI-generated administrative actions shall require technician review before execution.

---

## FR-AI-003 — No Automatic Destructive Execution

Priority: P0

AI shall not directly execute destructive system or administrative commands without explicit technician-controlled safeguards.

---

## FR-AI-004 — Context Control

Priority: P1

The system should control what information is sent to external AI providers.

Sensitive ticket or customer data should not automatically be transmitted.

---

## FR-AI-005 — Provider Independence

Priority: P3

AI architecture should avoid unnecessary dependency on a single provider where practical.

---

## FR-AI-006 — AI Failure Tolerance

Priority: P1

Core F7Hub functionality shall not depend on AI availability.

The application should remain useful if AI services are unavailable.

---

# 23. Plugin Requirements

## FR-PLUGIN-001 — Plugin Discovery

Priority: P3

F7Hub may eventually support plugin discovery.

---

## FR-PLUGIN-002 — Plugin Metadata

Priority: P3

Plugins should define metadata such as:

- name
- version
- author
- description
- compatibility
- dependencies
- permissions

---

## FR-PLUGIN-003 — Plugin Lifecycle

Priority: P3

Plugin lifecycle may include:

```text
Discover
→ Validate
→ Load
→ Initialize
→ Run
→ Disable
→ Unload
```

---

## FR-PLUGIN-004 — Plugin Isolation

Priority: P3

Plugins should not receive unrestricted access to every application subsystem by default.

---

## FR-PLUGIN-005 — Plugin Failure Isolation

Priority: P3

A failing optional plugin should not normally crash the entire application.

---

# 24. Reports Requirements

## FR-REPORT-001 — Report Generation

Priority: P2

F7Hub should support reports generated from structured application data.

Potential reports:

- diagnostic sessions
- script execution
- ticket activity
- knowledge usage
- technician activity
- troubleshooting summaries

---

## FR-REPORT-002 — Export

Priority: P2

Reports may support export to appropriate formats such as:

- CSV
- JSON
- HTML
- Markdown

Additional formats should only be added when justified.

---

# 25. Settings Requirements

## FR-SETTINGS-001 — Application Settings

Priority: P1

F7Hub shall provide persistent application settings.

Possible settings:

- theme
- paths
- feature preferences
- default workspace
- clipboard behavior
- logging
- integrations
- terminal settings

---

## FR-SETTINGS-002 — Settings Validation

Priority: P1

Invalid configuration should not silently break the application.

---

## FR-SETTINGS-003 — Reset Capability

Priority: P2

The application should provide a way to recover from invalid user settings.

---

# 26. Logging Requirements

## FR-LOG-001 — Application Logging

Priority: P1

F7Hub shall produce useful operational logs.

Logs may capture:

- application errors
- module initialization
- integration failures
- database errors
- script execution metadata
- plugin failures

---

## FR-LOG-002 — Sensitive Data Protection

Priority: P0

Logs must avoid exposing:

- passwords
- access tokens
- refresh tokens
- private keys
- authentication secrets
- unnecessary personal information

---

## FR-LOG-003 — Log Levels

Priority: P2

Logging should support levels such as:

```text
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

---

# 27. Database Requirements

## DATA-DB-001 — SQLite

Priority: P0

SQLite shall be the primary local relational database unless an approved architectural change replaces it.

---

## DATA-DB-002 — Foreign Keys

Priority: P0

SQLite foreign key enforcement shall be enabled.

---

## DATA-DB-003 — Primary Keys

Priority: P0

Persistent entities shall have stable primary keys.

---

## DATA-DB-004 — Referential Integrity

Priority: P0

Relationships between database entities shall preserve referential integrity.

---

## DATA-DB-005 — Constraints

Priority: P0

Database constraints shall enforce important invariants where appropriate.

---

## DATA-DB-006 — Parameterized Queries

Priority: P0

SQL queries containing external input shall use parameterized queries.

String concatenation shall not be used to construct SQL from untrusted input.

---

## DATA-DB-007 — Transactions

Priority: P0

Multi-step operations requiring atomicity shall use transactions.

---

## DATA-DB-008 — Migrations

Priority: P0

Database schema evolution shall use versioned migrations.

---

## DATA-DB-009 — No Silent Destructive Migration

Priority: P0

Migrations shall not silently destroy user data.

Destructive migrations require explicit review.

---

## DATA-DB-010 — Normalization

Priority: P1

Database design should normally target third normal form where practical.

Denormalization requires a documented reason.

---

## DATA-DB-011 — Indexing

Priority: P1

Indexes shall be added based on query requirements, relationships and measured performance needs.

Indexes should not be created blindly on every column.

---

## DATA-DB-012 — Full-Text Search

Priority: P1

SQLite FTS5 should be used where justified for searchable textual content.

---

## DATA-DB-013 — Backups

Priority: P1

The system should eventually provide or document safe backup procedures for persistent data.

---

## DATA-DB-014 — Database Recovery

Priority: P2

The project should define recovery procedures for corrupted or incompatible databases.

---

# 28. Integration Requirements

## INT-M365-001 — Microsoft 365 Integration

Priority: P2

F7Hub may integrate with Microsoft 365 services using approved APIs and PowerShell modules.

---

## INT-GRAPH-001 — Microsoft Graph

Priority: P2

Microsoft Graph should be the preferred modern API where appropriate for supported Microsoft cloud operations.

---

## INT-EXO-001 — Exchange Online

Priority: P2

F7Hub may support Exchange Online administration through supported Microsoft tooling.

---

## INT-ENTRA-001 — Entra ID

Priority: P2

F7Hub may support Entra ID administration and diagnostics.

---

## INT-INTUNE-001 — Microsoft Intune

Priority: P2

F7Hub may support Intune administration and diagnostics.

---

## INT-DEFENDER-001 — Microsoft Defender

Priority: P2

F7Hub may support Microsoft Defender-related workflows where supported by APIs or approved tooling.

---

## INT-PSA-001 — PSA Integration

Priority: P3

F7Hub may integrate with PSA systems such as HaloPSA.

Initial F7Hub versions shall not depend on PSA integration.

---

## INT-RMM-001 — RMM Integration

Priority: P3

F7Hub may provide integrations or launch workflows for RMM systems such as NinjaOne/NinjaRMM.

---

## INT-EXTERNAL-001 — Graceful External Failure

Priority: P1

Failure of an external integration shall not corrupt local application state.

---

# 29. Security Requirements

## SEC-001 — Least Privilege

Priority: P0

F7Hub shall follow least-privilege principles.

---

## SEC-002 — No Hard-Coded Secrets

Priority: P0

F7Hub source code and configuration shall not hard-code:

- passwords
- API keys
- tokens
- private keys
- customer credentials

---

## SEC-003 — Untrusted Input

Priority: P0

The following shall be treated as untrusted:

- clipboard data
- files
- URLs
- user input
- ticket data
- external APIs
- AI output
- plugin data
- command output

---

## SEC-004 — Command Injection Protection

Priority: P0

External input shall not be inserted directly into shell command strings without validation and safe argument handling.

---

## SEC-005 — SQL Injection Protection

Priority: P0

All externally influenced SQL values shall use parameterization.

---

## SEC-006 — AI Command Safety

Priority: P0

AI-generated commands shall not bypass execution review controls.

---

## SEC-007 — Secret Storage

Priority: P1

If F7Hub requires stored credentials, a secure credential mechanism must be explicitly designed before implementation.

Plaintext credential storage is not acceptable.

---

## SEC-008 — Sensitive Logging

Priority: P0

Secrets and unnecessary confidential data shall not be written to logs.

---

## SEC-009 — External Content Validation

Priority: P1

External files, API responses and plugin content should be validated before use.

---

## SEC-010 — Administrative Action Awareness

Priority: P1

Administrative operations should provide sufficient context for the technician to understand:

- target
- operation
- privilege level
- potential impact

before execution.

---

# 30. Performance Requirements

## NFR-PERF-001 — Startup Performance

Priority: P2

The application should start promptly under normal workstation conditions.

Slow cloud services shall not unnecessarily block local startup.

---

## NFR-PERF-002 — Search Performance

Priority: P1

Local search should return useful results quickly for expected personal-workstation dataset sizes.

---

## NFR-PERF-003 — UI Responsiveness

Priority: P1

Long-running database, PowerShell, network or AI operations should not freeze the primary GUI.

---

## NFR-PERF-004 — Database Query Efficiency

Priority: P1

Frequently used queries should be monitored for unnecessary full-table scans and poor query plans.

---

# 31. Reliability Requirements

## NFR-REL-001 — Graceful Failure

Priority: P0

Recoverable failures should not terminate the entire application.

---

## NFR-REL-002 — Error Visibility

Priority: P1

Errors should provide useful diagnostic information without exposing sensitive data.

---

## NFR-REL-003 — Data Preservation

Priority: P0

Unexpected application errors should not unnecessarily destroy persistent data.

---

## NFR-REL-004 — Transaction Safety

Priority: P0

Database operations requiring multiple dependent writes shall use transactions.

---

## NFR-REL-005 — External Dependency Isolation

Priority: P1

Failure of AI, Microsoft APIs, PSA platforms or other integrations should remain isolated where possible.

---

# 32. Usability Requirements

## NFR-UX-001 — Technician-Oriented Design

Priority: P1

The interface shall prioritize technician workflows rather than generic application patterns.

---

## NFR-UX-002 — Keyboard Productivity

Priority: P2

Frequently used actions should support keyboard access.

Examples:

- universal search
- command palette
- open ticket
- new ticket
- run command
- save
- switch workspace

---

## NFR-UX-003 — Consistent Navigation

Priority: P1

Navigation conventions should remain consistent across modules.

---

## NFR-UX-004 — Clear Status

Priority: P1

Users should be able to understand whether an operation:

- succeeded
- failed
- is running
- was cancelled
- requires attention

---

## NFR-UX-005 — Recoverable Mistakes

Priority: P2

Where practical, destructive or irreversible actions should require deliberate confirmation or provide recovery mechanisms.

---

# 33. Accessibility Requirements

## NFR-ACCESS-001 — Keyboard Accessibility

Priority: P2

Core application functionality should be accessible without requiring exclusive mouse interaction.

---

## NFR-ACCESS-002 — Readability

Priority: P1

Text and controls should remain readable at standard Windows scaling configurations.

---

## NFR-ACCESS-003 — Theme Support

Priority: P2

The interface should eventually support appropriate light and dark visual configurations.

---

# 34. Maintainability Requirements

## NFR-MAINT-001 — Modular Architecture

Priority: P0

Subsystem responsibilities shall remain explicit.

---

## NFR-MAINT-002 — Separation of Concerns

Priority: P0

GUI, business logic, repositories and infrastructure should not be unnecessarily coupled.

Preferred direction:

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

---

## NFR-MAINT-003 — Reuse Before Creation

Priority: P0

Existing functionality shall be searched before new architectural components are introduced.

---

## NFR-MAINT-004 — Dependency Control

Priority: P1

Dependencies should be added only when they provide justified value.

---

## NFR-MAINT-005 — No Unrelated Refactoring

Priority: P1

Focused implementation tasks should avoid unrelated architectural changes.

---

# 35. Portability Requirements

## NFR-PORT-001 — Windows First

Priority: P0

F7Hub is a Windows-first application.

Cross-platform support is not a core initial requirement.

---

## NFR-PORT-002 — Reproducible Setup

Priority: P2

Development and runtime dependencies should eventually be documented sufficiently to reproduce the environment.

---

## NFR-PORT-003 — Configurable Paths

Priority: P2

Environment-specific paths should not be unnecessarily hard-coded.

---

# 36. Local-First Requirements

## NFR-LOCAL-001 — Local Core Functionality

Priority: P1

Core local features should remain usable when internet connectivity is unavailable.

Examples:

- local tickets
- KB
- scripts
- clipboard
- notes
- local search
- settings

---

## NFR-LOCAL-002 — Connected Features

Priority: P1

Cloud-dependent features may require connectivity.

Examples:

- Microsoft Graph
- Exchange Online
- Intune
- Defender
- cloud AI
- HaloPSA

The application must distinguish local failure from remote service failure.

---

# 37. Auditability Requirements

## NFR-AUDIT-001 — Significant Actions

Priority: P2

Important administrative or automation actions should be traceable.

Potential information:

- action
- timestamp
- target
- technician
- result
- related ticket

---

## NFR-AUDIT-002 — Sensitive Audit Data

Priority: P1

Audit records must not unnecessarily preserve secrets.

---

# 38. Testing Requirements

## TEST-001 — Unit Testing

Priority: P1

Important domain logic should receive unit tests.

---

## TEST-002 — Database Testing

Priority: P0

Database behavior shall be tested.

Testing should include:

- migrations
- constraints
- foreign keys
- repository behavior
- transactions
- failure paths

---

## TEST-003 — Migration Testing

Priority: P0

Database migrations must be tested against representative prior schema versions before production use.

---

## TEST-004 — PowerShell Testing

Priority: P1

Important PowerShell scripts should include validation appropriate to their risk.

---

## TEST-005 — Integration Testing

Priority: P1

Subsystem boundaries should receive integration testing where practical.

---

## TEST-006 — GUI Testing

Priority: P2

Important GUI workflows should eventually receive automated or documented manual validation.

---

## TEST-007 — Failure Path Testing

Priority: P1

Testing shall include expected failure conditions.

Examples:

- database unavailable
- malformed input
- missing script
- PowerShell failure
- external API failure
- invalid configuration

---

## TEST-008 — Test Status

Priority: P0

Test results shall use:

```text
PASS
FAIL
NOT RUN
BLOCKED
```

Tests shall never be described as passing unless they were executed.

---

# 39. Documentation Requirements

## DOC-001 — Documentation Synchronization

Priority: P0

Significant implementation changes shall update relevant project documentation.

---

## DOC-002 — Database Documentation

Priority: P0

Database changes may require updates to:

- `07_Database.md`
- `08_ERD.md`
- `09_SQLSchema.md`

---

## DOC-003 — GUI Documentation

Priority: P1

Significant GUI changes may require updates to:

- `05_GUI.md`
- `06_SystemArchitecture.md`
- `13_PythonArchitecture.md`

---

## DOC-004 — AutoHotkey Documentation

Priority: P1

AHK architecture changes shall update:

`11_AHKArchitecture.md`

---

## DOC-005 — PowerShell Documentation

Priority: P1

PowerShell architecture changes shall update:

`12_PowerShellArchitecture.md`

---

## DOC-006 — Python Documentation

Priority: P1

Python/PyQt6 architecture changes shall update:

`13_PythonArchitecture.md`

---

## DOC-007 — Repository Documentation

Priority: P1

Repository structure changes shall update:

`10_FolderStructure.md`

---

## DOC-008 — Change History

Priority: P1

Verified significant project changes shall be recorded in:

`18_ChangeLog.md`

---

# 40. Data Privacy Requirements

## NFR-PRIV-001 — Minimize Sensitive Data

Priority: P0

F7Hub should store only data required for its intended workflows.

---

## NFR-PRIV-002 — Customer Information Awareness

Priority: P0

Ticket, contact and company records may contain confidential information and must be handled accordingly.

---

## NFR-PRIV-003 — External AI Transmission

Priority: P0

Sensitive support data shall not automatically be sent to external AI services.

---

## NFR-PRIV-004 — Export Awareness

Priority: P1

Exports should clearly indicate when potentially sensitive support information is included.

---

# 41. Backup and Recovery Requirements

## NFR-BACKUP-001 — Database Backup

Priority: P1

A reliable SQLite backup procedure shall be defined before F7Hub stores irreplaceable operational data.

---

## NFR-BACKUP-002 — Configuration Backup

Priority: P2

Important user configuration should be exportable or recoverable.

---

## NFR-BACKUP-003 — Restore Validation

Priority: P2

Backup procedures should eventually include restore testing.

A backup is not considered reliable merely because a file was copied.

---

# 42. Versioning Requirements

## NFR-VERSION-001 — Application Version

Priority: P1

F7Hub shall maintain an identifiable application version.

---

## NFR-VERSION-002 — Semantic Versioning

Priority: P2

Versions should generally follow semantic versioning:

```text
MAJOR.MINOR.PATCH
```

with pre-release identifiers where appropriate.

---

## NFR-VERSION-003 — Schema Version

Priority: P0

The database schema shall maintain an identifiable migration/schema version.

---

# 43. Initial Release Scope

The earliest useful F7Hub version should focus on a small reliable core.

Recommended foundational capabilities:

```text
Application shell
    +
SQLite database
    +
Basic ticket records
    +
Knowledge base
    +
Search
    +
Script registry
    +
PowerShell execution foundation
    +
Settings
    +
Logging
```

Advanced functionality should be layered on after these foundations are reliable.

---

# 44. Initial Release Exclusions

Early releases do not need:

- enterprise multi-user collaboration
- SaaS backend
- mobile client
- full HaloPSA synchronization
- full NinjaOne integration
- autonomous Microsoft 365 administration
- advanced AI orchestration
- complex plugin marketplace
- distributed database
- cloud synchronization platform
- full multi-tenant MSP backend
- cross-platform desktop support

These capabilities may be revisited later.

---

# 45. Future Product Requirements

Potential future requirements include:

## Collaboration

- multiple technicians
- role-based permissions
- shared KB
- shared ticket context

## Cloud Synchronization

- secure multi-device synchronization
- centrally managed configuration

## Advanced AI

- retrieval-augmented troubleshooting
- ticket pattern recognition
- knowledge-gap detection
- controlled agent workflows

## Advanced Reporting

- SLA analytics
- diagnostic trends
- ticket category trends
- script effectiveness
- knowledge reuse metrics

## Advanced Integrations

- PSA synchronization
- RMM integration
- Microsoft Graph expansion
- external knowledge providers

These remain future requirements until explicitly approved.

---

# 46. Product Constraints

F7Hub must operate within several important constraints.

## Technical Constraints

- Windows-first
- local SQLite database
- multiple implementation languages
- Microsoft service authentication requirements
- external API availability
- PowerShell module compatibility

## Security Constraints

- least privilege
- no plaintext secrets
- no blind AI command execution
- customer data confidentiality

## Development Constraints

- primarily individual development
- AI-assisted implementation
- architecture must remain understandable
- development must occur incrementally

---

# 47. Requirement Conflicts

When two requirements conflict, resolution should consider:

1. explicit user requirement
2. security
3. data integrity
4. approved architecture
5. product requirements
6. usability
7. performance
8. implementation convenience

Implementation convenience must not override security or data integrity.

---

# 48. Definition of Done

A product requirement should not be considered fully satisfied merely because code exists.

A requirement may be considered complete when applicable conditions are met:

```text
[ ] Requirement implemented
[ ] Acceptance criteria satisfied
[ ] Input validation implemented
[ ] Error handling implemented
[ ] Security reviewed
[ ] Database integrity preserved
[ ] Tests executed
[ ] Failure paths tested
[ ] Documentation synchronized
[ ] No unrelated architectural changes introduced
```

---

# 49. Requirement Traceability

Requirements should eventually be traceable through:

```text
Requirement
   ↓
Feature
   ↓
Workflow
   ↓
Architecture
   ↓
Implementation
   ↓
Test
```

Example:

```text
FR-TICKET-001
Create Ticket Record
        ↓
03_Features.md
Ticket Management
        ↓
04_UserWorkflows.md
Create Ticket Workflow
        ↓
06_SystemArchitecture.md
Ticket Service Architecture
        ↓
Python / Database Implementation
        ↓
Tests
```

This traceability is especially important when coding agents are used.

---

# 50. Relationship to Other Documents

## `00_ProjectVision.md`

Defines:

> Why does F7Hub exist?

---

## `01_Project.md`

Defines:

> What is F7Hub as a software project?

---

## `02_ProductRequirements.md`

Defines:

> What must F7Hub accomplish?

---

## `03_Features.md`

Defines:

> What product capabilities satisfy these requirements?

---

## `04_UserWorkflows.md`

Defines:

> How does the user interact with those capabilities?

---

## `05_GUI.md`

Defines:

> How are those workflows presented in the interface?

---

## `06_SystemArchitecture.md`

Defines:

> How do the internal components implement those workflows?

---

# 51. Requirement Development Rule

New requirements should not be added casually during implementation.

When a substantial new requirement appears:

```text
Identify Requirement
        ↓
Determine Scope
        ↓
Assign Requirement ID
        ↓
Assign Priority
        ↓
Define Acceptance Criteria
        ↓
Analyze Architecture Impact
        ↓
Update Related Documentation
        ↓
Implement
        ↓
Test
```

This prevents implementation from silently becoming the product specification.

---

# 52. Product Success Criteria

F7Hub will be considered successful when it demonstrably helps an IT technician:

- access ticket context faster
- retrieve relevant technical knowledge faster
- perform structured troubleshooting
- reuse scripts safely
- reduce repetitive manual tasks
- reduce repetitive typing
- preserve diagnostic results
- document work consistently
- navigate Microsoft administrative systems efficiently
- search across technical information
- maintain useful local functionality
- retain control over automation and AI
- understand what the application is doing
- extend functionality without destabilizing the core

---

# 53. Core Product Requirement Summary

The essential F7Hub product can be summarized as:

```text
                    F7Hub
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
     Context       Knowledge     Automation
        │             │             │
        ▼             ▼             ▼
     Tickets         KB          PowerShell
     Company        Search       AutoHotkey
     Contacts       Prompts      Diagnostics
        │             │             │
        └─────────────┼─────────────┘
                      │
                      ▼
                   SQLite
                      │
                      ▼
              Persistent History
                      │
                      ▼
                Technician
                  Control
```

F7Hub must remain:

- modular
- understandable
- secure
- testable
- searchable
- maintainable
- technician-centered

The product should grow by satisfying verified requirements, not by accumulating disconnected features.

> Every major feature should answer a documented requirement.  
> Every requirement should have a reason to exist.  
> Every implementation should remain inspectable, testable and understandable.