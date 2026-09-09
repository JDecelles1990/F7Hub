# F7Hub Features

> Document: `Docs/03_Features.md`  
> Project: F7Hub  
> Purpose: Define the planned product capabilities of F7Hub and map them to approved product requirements.  
> Scope: Feature inventory and feature-level behavior.  
> Related Documents: `00_ProjectVision.md`, `01_Project.md`, `02_ProductRequirements.md`, `04_UserWorkflows.md`, `05_GUI.md`, `06_SystemArchitecture.md`

---

# 1. Purpose

This document defines the major features planned for F7Hub.

It answers:

> What capabilities should F7Hub provide?

This document does not define:

- exact GUI layouts
- SQL tables
- Python classes
- PowerShell implementation
- database schema
- detailed user workflows

Those belong in later architecture and implementation documents.

---

# 2. Feature Status

Each feature may use the following status values:

| Status | Meaning |
|---|---|
| PLANNED | Approved but not yet implemented |
| IN PROGRESS | Implementation has started |
| IMPLEMENTED | Feature exists |
| VERIFIED | Feature has been tested and confirmed |
| DEFERRED | Intentionally postponed |
| REJECTED | Removed from product scope |
| NOT VERIFIED | Current implementation state has not been inspected |

Unless explicitly updated:

```text
Status: PLANNED
```

---

# 3. Feature Priority

| Priority | Meaning |
|---|---|
| P0 | Foundational |
| P1 | Core capability |
| P2 | Important enhancement |
| P3 | Future capability |

---

# 4. Feature Organization

F7Hub features are grouped into major product areas:

```text
F7Hub
│
├── Application Platform
├── Dashboard
├── Tickets
├── Companies
├── Contacts
├── Knowledge Base
├── Search
├── Scripts
├── PowerShell
├── Diagnostics
├── AutoHotkey
├── Clipboard
├── Prompts
├── AI
├── Microsoft Administration
├── Reporting
├── Workspaces
├── Settings
├── Logging
├── Plugins
└── Utilities
```

---

# 5. Application Platform

## FEAT-APP-001 — Main Desktop Application

Priority: P0  
Requirements: `FR-APP-001`, `FR-APP-002`

F7Hub shall provide a primary Windows desktop application built with Python and PySide6.

The application shell provides:

- main window
- module navigation
- status information
- menu system
- toolbar
- workspace hosting
- service initialization

---

## FEAT-APP-002 — Modular Navigation

Priority: P1  
Requirements: `FR-APP-002`

The application shall provide navigation between major F7Hub modules.

Potential modules include:

- Dashboard
- Tickets
- Companies
- Contacts
- Knowledge Base
- Search
- Scripts
- Diagnostics
- Clipboard
- Prompts
- AI
- Reports
- Plugins
- Settings
- Logs

---

## FEAT-APP-003 — Command Palette

Priority: P2  
Requirements: `NFR-UX-002`

F7Hub should provide a universal command palette.

Possible commands:

```text
Open ticket INC-10254
Search KB Outlook profile
Run DNS diagnostics
Open Exchange Admin Center
Open PowerShell
New KB article
Open company Contoso
Show clipboard history
Switch workspace
```

Commands should invoke registered application actions rather than arbitrary code.

---

# 6. Dashboard

## FEAT-DASH-001 — Technician Dashboard

Priority: P1  
Requirements: `FR-DASH-001`

The dashboard provides a technician-oriented overview.

Potential content:

- recent tickets
- active tickets
- recent KB articles
- frequent scripts
- diagnostic history
- shortcuts
- integration status
- recent activity

---

## FEAT-DASH-002 — Quick Actions

Priority: P1  
Requirements: `FR-DASH-002`

The dashboard should provide shortcuts to frequently used actions.

Examples:

- create ticket
- search F7Hub
- open KB
- run diagnostic
- open PowerShell
- open clipboard tools
- launch Microsoft portals

---

# 7. Ticket Center

## FEAT-TICKET-001 — Ticket Records

Priority: P0  
Requirements: `FR-TICKET-001` through `FR-TICKET-003`

F7Hub shall support local ticket records.

Core capabilities:

- create
- view
- edit
- persist
- validate

---

## FEAT-TICKET-002 — Ticket Workspace

Priority: P1  
Requirements: `FR-TICKET-002`, `FR-TICKET-007`

Opening a ticket should provide a contextual workspace containing relevant support information.

Potential panels:

- ticket details
- notes
- company
- contact
- timeline
- attachments
- related KB
- scripts
- diagnostics
- AI assistance

---

## FEAT-TICKET-003 — Ticket Notes

Priority: P1  
Requirements: `FR-TICKET-004`

Tickets shall support multiple structured notes.

Possible note types:

- troubleshooting
- internal
- customer communication
- escalation
- resolution

---

## FEAT-TICKET-004 — Ticket Timeline

Priority: P1  
Requirements: `FR-TICKET-005`

The application should provide a chronological ticket timeline.

Potential events:

- ticket creation
- note creation
- status change
- script execution
- diagnostic execution
- KB relationship
- escalation
- resolution

---

## FEAT-TICKET-005 — Ticket Attachments

Priority: P2  
Requirements: `FR-TICKET-006`

Tickets may reference related files such as:

- screenshots
- logs
- exports
- documents

Large files should remain outside the SQLite database by default.

---

## FEAT-TICKET-006 — Related Tickets

Priority: P2  
Requirements: `FR-TICKET-007`

F7Hub should support relationships between tickets.

Possible uses:

- repeated incident
- parent/child case
- known recurring issue
- similar historical issue

---

## FEAT-TICKET-007 — Ticket Search

Priority: P1  
Requirements: `FR-TICKET-008`

Tickets shall be searchable by relevant fields and associated content.

---

## FEAT-TICKET-008 — Resolution and Escalation

Priority: P1  
Requirements: `FR-TICKET-009`, `FR-TICKET-010`

The ticket workspace should support structured:

- resolution notes
- escalation summaries
- troubleshooting performed
- diagnostic evidence
- recommended next steps

---

# 8. Company Center

## FEAT-COMPANY-001 — Company Records

Priority: P1  
Requirements: `FR-COMPANY-001`

F7Hub shall support company records.

Potential information:

- company name
- domains
- notes
- links
- environment information
- escalation context

---

## FEAT-COMPANY-002 — Company Technical Context

Priority: P1  
Requirements: `FR-COMPANY-002`

Technicians should be able to access company-specific technical information while working on a ticket.

Examples:

- Microsoft tenant information
- network notes
- common applications
- support procedures
- known issues
- useful administrative links

---

## FEAT-COMPANY-003 — Company Relationships

Priority: P1  
Requirements: `FR-COMPANY-003`

Companies may relate to:

- contacts
- tickets
- knowledge articles
- scripts
- bookmarks
- technical assets

---

# 9. Contact Center

## FEAT-CONTACT-001 — Contact Records

Priority: P1  
Requirements: `FR-CONTACT-001`

F7Hub shall support contact records associated with companies.

---

## FEAT-CONTACT-002 — Contact Ticket History

Priority: P2  
Requirements: `FR-CONTACT-003`

Technicians should be able to review relevant previous ticket activity for a contact.

---

# 10. Knowledge Base

## FEAT-KB-001 — Knowledge Articles

Priority: P1  
Requirements: `FR-KB-001`, `FR-KB-002`

F7Hub shall support creation and editing of structured KB articles.

Slices 010–011 implement creation, deterministic listing, reopening/reading and DRAFT article editing through Knowledge Base navigation. Creation requires a user-entered article code, title and Markdown body; summary is optional. New articles are DRAFT, version 1, with an atomic initial history snapshot. Edit Article changes title/summary/body while keeping the article code immutable. Save Revision atomically increments the current version and appends its new snapshot; earlier snapshots remain unchanged. An expected-version token rejects stale overwrites. The read view displays Version N and read-only Markdown source.

Only DRAFT articles are editable; PUBLISHED/ARCHIVED articles remain readable. Failed saves preserve input. No-change saves create no revision after authoritative status/version checks. Restore/revert, deletion, publishing/archiving workflows, categories/tags, article-to-article relationships, external links and AI remain unimplemented.

Slice 012 adds RELATED ticket/article linking: open a saved ticket → Knowledge → Link Article → select an existing article → link → Open Article to read its current content in Knowledge Base. The linked list displays current code/title/status/version. All existing article statuses are eligible; already RELATED articles are excluded from candidates, and concurrent duplicate attempts receive safe feedback.

Slice 013 adds Unlink Article for one selected RELATED association. Confirmation identifies the article and explains that both the ticket and article remain; Cancel is the default. Confirmed unlink removes only the exact association and refreshes the list. The article becomes a link candidate again and can be linked normally with a new linked_at timestamp. Missing entities and already-removed links produce safe feedback; a committed unlink remains reported as successful even if refresh fails. Bulk unlink, APPLIED/RESOLUTION_SOURCE workflows, relationship-type editing, history/undo, recommendations and creating/editing articles from the ticket remain deferred.

Slice 014 implements read-only version history: Knowledge Base → open an article → Version History → select a persisted revision → read its exact snapshot. History is available for loaded DRAFT, PUBLISHED and ARCHIVED articles with an available service and idle runner. The list is newest-first and excludes bodies; only the selected revision loads its summary/body. Historical version, title, summary, body, change summary, created by and stored timestamp come from knowledge_article_versions. Missing optional metadata displays Not provided. Status, category, updated_by and published_at are not snapshotted and are not presented as historical data. Article code is current immutable identity. Viewing does not change the current article, history rows, timestamps or ticket activity.

Slice 015 adds current-article Knowledge search through SQLite FTS5. Search covers article code, title, summary and current Markdown body for DRAFT, PUBLISHED and ARCHIVED articles. Plain input is converted into quoted Unicode letter/number tokens joined by implicit AND, so punctuation and operator-looking text do not expose raw FTS syntax. Results are lightweight current identities ranked by bm25 with deterministic recency/ID tie-breaking; selecting one reloads authoritative current detail through the existing read path. Historical revisions are not indexed.

Restore/revert, historical editing/deletion, comparison/apply and AI remain deferred. There is no historical status snapshot and no pagination for large revision or search-result lists.

Possible article types:

- troubleshooting guide
- SOP
- known error
- command reference
- PowerShell reference
- Microsoft 365 procedure
- escalation guide

---

## FEAT-KB-002 — KB Metadata

Priority: P1  
Requirements: `FR-KB-004`

Knowledge articles may include:

- title
- article type
- category
- technology
- tags
- status
- creation date
- modification date

---

## FEAT-KB-003 — KB Search

Priority: P1  
Requirements: `FR-KB-003`

Knowledge content shall support fast local search.

Slice 015 implements this for current Knowledge articles with an external-content `knowledge_articles_fts` index synchronized by insert/update/delete triggers. Existing rows are backfilled during migration 0006. The relational `knowledge_articles` row remains authoritative; search results expose only article ID, code, title, status, current version and updated timestamp before the normal detail read.

This slice does not implement unified search, ticket search, filters, snippets/highlighting, advanced query syntax, pagination, saved searches, recommendations or AI ranking.

---

## FEAT-KB-004 — Related Knowledge

Priority: P2  
Requirements: `FR-KB-005`, `FR-KB-006`

Knowledge articles may be linked to:

- tickets
- diagnostics
- scripts
- companies
- technologies
- other articles

---

## FEAT-KB-005 — Knowledge Lifecycle

Priority: P2  
Requirements: `FR-KB-007`

Knowledge articles may use states such as:

```text
DRAFT
ACTIVE
REVIEW_REQUIRED
DEPRECATED
ARCHIVED
```

---

# 11. Universal Search

## FEAT-SEARCH-001 — Unified Search

Priority: P1  
Requirements: `FR-SEARCH-001`

F7Hub should provide a shared search experience across supported domains.

Potential sources:

- tickets
- companies
- contacts
- KB
- scripts
- prompts
- clipboard
- commands
- documentation

---

## FEAT-SEARCH-002 — Search Filters

Priority: P2  
Requirements: `FR-SEARCH-002`

Search results may be filtered by:

- domain
- category
- technology
- date
- company
- status

---

## FEAT-SEARCH-003 — Full-Text Search

Priority: P1  
Requirements: `FR-SEARCH-004`

High-value textual content should support SQLite FTS5 where appropriate.

---

## FEAT-SEARCH-004 — Search Ranking

Priority: P2  
Requirements: `FR-SEARCH-003`

Search results should prioritize relevance.

Ranking may consider:

- textual relevance
- recency
- tags
- relationships
- active ticket context

---

## FEAT-SEARCH-005 — Query Normalization

Priority: P2  
Requirements: `FR-SEARCH-005`

Search should support basic normalization and aliases.

AI must not be required for core local search.

---

# 12. Script Library

## FEAT-SCRIPT-001 — Script Registry

Priority: P1  
Requirements: `FR-SCRIPT-001`, `FR-SCRIPT-002`

F7Hub shall provide a searchable catalog of automation scripts.

Potential languages:

- PowerShell
- AutoHotkey v2
- Python
- approved command-line utilities

---

## FEAT-SCRIPT-002 — Script Metadata

Priority: P1  
Requirements: `FR-SCRIPT-002`

Metadata may include:

- name
- description
- path
- language
- category
- tags
- version
- required privilege
- risk level
- parameters

---

## FEAT-SCRIPT-003 — File-Based Script Source

Priority: P1  
Requirements: `FR-SCRIPT-003`

Scripts should normally remain version-controlled files.

SQLite stores metadata and execution history.

---

## FEAT-SCRIPT-004 — Script Search

Priority: P1  
Requirements: `FR-SCRIPT-004`

Users should be able to find scripts by:

- purpose
- technology
- category
- tags
- privilege
- language

---

## FEAT-SCRIPT-005 — Parameter Forms

Priority: P1  
Requirements: `FR-SCRIPT-005`

F7Hub should generate validated parameter inputs for registered scripts.

---

## FEAT-SCRIPT-006 — Execution History

Priority: P1  
Requirements: `FR-SCRIPT-006`

Executed scripts should produce useful execution records.

---

# 13. PowerShell Center

## FEAT-PS-001 — Controlled PowerShell Execution

Priority: P1  
Requirements: `FR-PS-001`

F7Hub shall invoke approved PowerShell scripts through a controlled execution layer.

---

## FEAT-PS-002 — PowerShell 7 Runtime

Priority: P1  
Requirements: `FR-PS-002`

PowerShell 7 should be preferred unless compatibility requires Windows PowerShell 5.1.

---

## FEAT-PS-003 — Structured Results

Priority: P1  
Requirements: `FR-PS-003`

PowerShell diagnostic scripts should return structured results where practical.

Preferred interchange format:

```text
JSON
```

---

## FEAT-PS-004 — Terminal / Output Panel

Priority: P2

F7Hub may provide an embedded or integrated PowerShell-oriented output panel.

It may display:

- command output
- errors
- diagnostic results
- execution status

The exact terminal architecture belongs in `05_GUI.md` and `12_PowerShellArchitecture.md`.

---

## FEAT-PS-005 — Privilege Awareness

Priority: P1  
Requirements: `FR-PS-005`

F7Hub should identify operations requiring administrative or cloud privileges before execution.

---

# 14. Diagnostic Engine

## FEAT-DIAG-001 — Diagnostic Workflows

Priority: P1  
Requirements: `FR-DIAG-001`

F7Hub shall support reusable troubleshooting workflows.

A workflow may contain:

- questions
- checks
- conditions
- script steps
- decisions
- resolutions
- escalation paths

---

## FEAT-DIAG-002 — Dynamic Diagnostic Forms

Priority: P2  
Requirements: `FR-DIAG-002`

Diagnostic questions may dynamically generate PySide6 form controls.

---

## FEAT-DIAG-003 — Conditional Branching

Priority: P1  
Requirements: `FR-DIAG-003`

Workflows shall support branching based on:

- technician answers
- existing ticket data
- diagnostic values
- script results

---

## FEAT-DIAG-004 — Automated Diagnostic Steps

Priority: P1  
Requirements: `FR-DIAG-004`

Approved diagnostic workflows may invoke PowerShell scripts.

---

## FEAT-DIAG-005 — Diagnostic Session History

Priority: P1  
Requirements: `FR-DIAG-005`, `FR-DIAG-006`

Diagnostic sessions should preserve:

- workflow
- ticket
- answers
- script results
- warnings
- errors
- outcome

---

## FEAT-DIAG-006 — Suggested Next Steps

Priority: P2

Based on deterministic workflow rules, F7Hub may suggest:

- another diagnostic step
- a KB article
- an approved script
- likely resolution
- escalation

AI assistance may supplement these suggestions.

---

# 15. AutoHotkey Features

## FEAT-AHK-001 — Global Hotkeys

Priority: P2  
Requirements: `FR-AHK-001`

AutoHotkey v2 provides the verified global `F7` launch/focus shortcut. While
the shortcut script is active, F7 restores and focuses an existing F7Hub
window or launches the project-local Python application when no matching
window exists. Other global shortcuts remain planned. Detailed launcher
behavior and boundaries belong in `11_AHKArchitecture.md`.

---

## FEAT-AHK-002 — Hotstrings

Priority: P2  
Requirements: `FR-AHK-002`

Reusable text may be inserted through configured hotstrings.

---

## FEAT-AHK-003 — Quick Menus

Priority: P2

AHK may provide lightweight popup menus for common technician actions.

---

## FEAT-AHK-004 — Application Launcher

Priority: P2  
Requirements: `FR-AHK-004`

AHK may launch or focus commonly used applications and portals.

---

# 16. Clipboard Center

## FEAT-CLIP-001 — Clipboard History

Priority: P1  
Requirements: `FR-CLIP-001`

F7Hub should provide controlled clipboard history.

Persistence must be configurable.

---

## FEAT-CLIP-002 — Snippet Library

Priority: P1  
Requirements: `FR-CLIP-002`

Technicians should be able to save reusable text snippets.

---

## FEAT-CLIP-003 — Text Transformations

Priority: P2  
Requirements: `FR-CLIP-003`

Potential transformations:

- plain text conversion
- whitespace cleanup
- case conversion
- ticket-note formatting
- URL extraction
- email extraction
- IP address extraction

---

## FEAT-CLIP-004 — Sensitive Content Controls

Priority: P0  
Requirements: `FR-CLIP-004`

Clipboard features must support privacy controls such as:

- clear history
- disable persistence
- exclusion
- retention limits

---

# 17. Prompt Library

## FEAT-PROMPT-001 — Prompt Templates

Priority: P2  
Requirements: `FR-PROMPT-001`

F7Hub may store reusable AI prompt templates.

---

## FEAT-PROMPT-002 — Prompt Variables

Priority: P2  
Requirements: `FR-PROMPT-003`

Templates may use variables such as:

```text
{{ticket_title}}
{{company_name}}
{{ticket_description}}
{{diagnostic_results}}
```

---

## FEAT-PROMPT-003 — Prompt Preview

Priority: P2  
Requirements: `FR-PROMPT-004`

The user should be able to inspect generated prompts before submission where appropriate.

---

# 18. AI Center

## FEAT-AI-001 — Ticket Summarization

Priority: P2  
Requirements: `FR-AI-001`

AI may summarize:

- ticket description
- ticket notes
- troubleshooting performed
- diagnostic results

---

## FEAT-AI-002 — Troubleshooting Assistance

Priority: P2

AI may suggest:

- troubleshooting hypotheses
- questions
- relevant KB content
- possible next steps

AI suggestions remain advisory.

---

## FEAT-AI-003 — Note Improvement

Priority: P2

AI may help transform rough technician notes into structured:

- internal notes
- escalation summaries
- resolution notes
- customer-facing summaries

---

## FEAT-AI-004 — Script Explanation

Priority: P2

AI may explain PowerShell, AutoHotkey or Python code.

Generated changes require review.

---

## FEAT-AI-005 — AI Context Builder

Priority: P2  
Requirements: `FR-AI-004`

F7Hub should control which ticket, KB, diagnostic and script context is supplied to AI.

---

## FEAT-AI-006 — Human-Controlled Execution

Priority: P0  
Requirements: `FR-AI-002`, `FR-AI-003`

AI shall not directly execute destructive administrative actions.

---

# 19. Microsoft Administration Center

## FEAT-M365-001 — Microsoft Admin Launchpad

Priority: P2

F7Hub may provide quick access to Microsoft administrative services.

Examples:

- Microsoft 365 Admin Center
- Entra Admin Center
- Exchange Admin Center
- Intune Admin Center
- Defender
- Teams Admin Center
- SharePoint Admin Center

---

## FEAT-M365-002 — Microsoft Graph Integration

Priority: P2  
Requirements: `INT-GRAPH-001`

F7Hub may use Microsoft Graph for supported administrative and diagnostic workflows.

---

## FEAT-M365-003 — Exchange Online Integration

Priority: P2  
Requirements: `INT-EXO-001`

F7Hub may expose approved Exchange Online operations through PowerShell and/or supported APIs.

---

## FEAT-M365-004 — Entra Integration

Priority: P2  
Requirements: `INT-ENTRA-001`

Potential capabilities include approved account and identity diagnostics.

---

## FEAT-M365-005 — Intune Integration

Priority: P2  
Requirements: `INT-INTUNE-001`

Potential capabilities include device and policy diagnostics.

---

## FEAT-M365-006 — Defender Integration

Priority: P2  
Requirements: `INT-DEFENDER-001`

Potential capabilities include security-related diagnostic workflows.

---

# 20. External Integration Features

## FEAT-INT-001 — HaloPSA Integration

Priority: P3  
Requirements: `INT-PSA-001`

Potential future integration may provide:

- ticket lookup
- ticket linking
- ticket context
- note export
- status synchronization

F7Hub is not intended to replace HaloPSA.

---

## FEAT-INT-002 — NinjaOne / RMM Integration

Priority: P3  
Requirements: `INT-RMM-001`

Potential integration may provide:

- device context
- launch shortcuts
- diagnostic workflow integration
- remote-management references

---

# 21. Workspace Features

## FEAT-WORKSPACE-001 — Dockable Panels

Priority: P2  
Requirements: `FR-APP-004`

Supported modules may appear in movable dock panels.

Potential panels:

- Ticket Details
- Notes
- Timeline
- KB Matches
- AI Assistant
- PowerShell
- Search
- Clipboard
- Output

---

## FEAT-WORKSPACE-002 — Saved Workspace Profiles

Priority: P2  
Requirements: `FR-APP-003`

Potential workspace profiles include:

- Helpdesk
- Microsoft 365
- Networking
- Automation
- Knowledge Authoring
- AI

---

# 22. Reporting

## FEAT-REPORT-001 — Diagnostic Reports

Priority: P2  
Requirements: `FR-REPORT-001`

Diagnostic session information may be rendered into structured reports.

---

## FEAT-REPORT-002 — Script Execution Reports

Priority: P2

F7Hub may produce reports describing:

- scripts executed
- result
- time
- ticket
- errors

---

## FEAT-REPORT-003 — Export

Priority: P2  
Requirements: `FR-REPORT-002`

Potential export formats include:

- CSV
- JSON
- HTML
- Markdown

---

# 23. Settings

## FEAT-SETTINGS-001 — Application Preferences

Priority: P1  
Requirements: `FR-SETTINGS-001`

Settings may include:

- theme
- paths
- default workspace
- logging preferences
- clipboard behavior
- feature preferences
- integration configuration

---

## FEAT-SETTINGS-002 — Recovery / Reset

Priority: P2  
Requirements: `FR-SETTINGS-003`

Invalid configuration should be recoverable through safe reset mechanisms.

---

# 24. Logging and Activity

## FEAT-LOG-001 — Application Logs

Priority: P1  
Requirements: `FR-LOG-001`

F7Hub should capture useful operational information.

---

## FEAT-LOG-002 — Execution Activity

Priority: P1

Relevant actions may be visible through execution or activity history.

Examples:

- scripts
- diagnostics
- errors
- integrations
- administrative operations

---

# 25. Plugin Platform

## FEAT-PLUGIN-001 — Plugin Discovery

Priority: P3  
Requirements: `FR-PLUGIN-001`

F7Hub may discover approved plugins from defined locations.

---

## FEAT-PLUGIN-002 — Plugin Metadata

Priority: P3  
Requirements: `FR-PLUGIN-002`

Plugins should declare:

- identity
- version
- compatibility
- dependencies
- permissions

---

## FEAT-PLUGIN-003 — Controlled Extension Points

Priority: P3

Potential extension points include:

- GUI panels
- search providers
- diagnostic providers
- integrations
- reports
- utility commands

---

# 26. Technician Utility Features

F7Hub may provide or launch lightweight utilities useful during support work.

Potential capabilities include:

- network tools
- Windows administrative tools
- system information
- path and file utilities
- browser shortcuts
- remote support launchers
- PowerShell tools
- command references

F7Hub should reuse mature operating-system utilities rather than recreating them unnecessarily.

---

# 27. Feature Relationships

Features should cooperate rather than exist as isolated tools.

Example:

```text
Ticket
   │
   ├── Company
   ├── Contact
   ├── KB
   ├── Diagnostic Session
   ├── Script Execution
   ├── AI Context
   └── Timeline
```

This contextual integration is one of the primary advantages of F7Hub.

---

# 28. Example Integrated Ticket Experience

A technician opens a ticket.

F7Hub may provide:

```text
Ticket Details
      │
      ├── Company Context
      ├── Contact History
      ├── Related Tickets
      ├── KB Matches
      ├── Diagnostic Workflows
      ├── Approved Scripts
      ├── AI Suggestions
      └── Ticket Timeline
```

The objective is not merely to display data.

The objective is to provide relevant context for the current support task.

---

# 29. Feature Dependency Principles

Features may depend on platform capabilities.

Examples:

```text
Ticket Search
→ requires ticket persistence

KB Search
→ requires KB persistence

Diagnostic Execution
→ requires diagnostic engine + PowerShell execution

AI Ticket Summary
→ requires ticket context + AI service

Saved Workspaces
→ requires settings/state persistence
```

Dependencies should influence implementation order.

---

# 30. Initial Feature Set

The first useful F7Hub release should remain intentionally limited.

Recommended core:

```text
Application Shell
        │
        ├── Dashboard
        ├── Tickets
        ├── Companies
        ├── Contacts
        ├── Knowledge Base
        ├── Search
        ├── Script Library
        ├── PowerShell Foundation
        ├── Settings
        └── Logging
```

Advanced capabilities should build on this foundation.

---

# 31. Second-Stage Features

After the core platform is reliable:

```text
Diagnostic Engine
Clipboard Center
AutoHotkey Integration
Workspace Profiles
Reporting
Command Palette
Microsoft Administration
```

---

# 32. Later Features

Future phases may introduce:

```text
Advanced AI
HaloPSA Integration
NinjaOne Integration
Plugin Framework
Advanced Analytics
Multi-user Capabilities
Cloud Synchronization
```

These should not complicate the initial architecture prematurely.

---

# 33. Feature Acceptance Rule

A feature should not be considered complete simply because its GUI exists.

Feature completion may require:

```text
[ ] Requirement satisfied
[ ] Data model implemented
[ ] Service behavior implemented
[ ] Validation implemented
[ ] Error handling implemented
[ ] Security reviewed
[ ] Tests executed
[ ] Failure paths tested
[ ] Documentation synchronized
```

---

# 34. Feature Traceability

Each significant feature should trace back to one or more product requirements.

Preferred chain:

```text
Product Requirement
       ↓
Feature
       ↓
User Workflow
       ↓
GUI / Architecture
       ↓
Implementation
       ↓
Test
```

Example:

```text
FR-DIAG-001
    ↓
FEAT-DIAG-001
Diagnostic Workflows
    ↓
04_UserWorkflows.md
Run Diagnostic Workflow
    ↓
06_SystemArchitecture.md
Diagnostic Engine
    ↓
Implementation
    ↓
Tests
```

---

# 35. Feature Change Rule

Before adding a major feature:

1. identify the user problem
2. identify the requirement
3. determine whether an existing feature already addresses it
4. define scope
5. identify dependencies
6. identify architecture impact
7. define acceptance criteria
8. update documentation
9. implement incrementally

Avoid creating features simply because they are technically interesting.

---

# 36. Features That Should Not Become Duplicates

F7Hub should integrate with or complement external tools rather than reproduce them unnecessarily.

Examples:

```text
HaloPSA
→ F7Hub provides technician context and integration
→ not a complete PSA replacement

NinjaOne
→ F7Hub provides workflows and access
→ not a complete RMM replacement

Microsoft Admin Centers
→ F7Hub provides shortcuts, diagnostics and automation
→ not complete portal replacements

Keeper
→ F7Hub may launch or reference credential workflows
→ not a password-manager replacement

VS Code
→ F7Hub manages script discovery and execution
→ not a full development IDE
```

---

# 37. Feature Design Principles

Every F7Hub feature should aim to be:

- useful
- discoverable
- contextual
- modular
- testable
- secure
- keyboard-friendly where appropriate
- consistent with other modules

Features should reduce technician friction rather than simply increase application size.

---

# 38. Current Feature Status

The implementation was inspected during the 2026-09-02 consistency review.

Therefore:

```text
Current implementation status: PLANNED
```

Repository inspection on 2026-09-02 found no feature implementation in the canonical application source trees. This document represents planned F7Hub capabilities.

It does not prove that any listed feature currently exists.

---

# 39. Relationship to Other Documents

## `02_ProductRequirements.md`

Defines:

> What must F7Hub accomplish?

## `03_Features.md`

Defines:

> What capabilities provide those outcomes?

## `04_UserWorkflows.md`

Defines:

> How does the technician use those capabilities?

## `05_GUI.md`

Defines:

> How are features presented visually?

## `06_SystemArchitecture.md`

Defines:

> How do the underlying components cooperate?

---

# 40. Feature Summary

The major F7Hub capability groups are:

```text
                       F7Hub
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
     Support          Knowledge       Automation
        │                │                │
     Tickets             KB            Scripts
    Companies           Search       PowerShell
    Contacts           Prompts       Diagnostics
        │                │             AutoHotkey
        └────────────────┼────────────────┘
                         │
                         ▼
                    Productivity
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
    Clipboard           AI           Workspaces
      Reports         M365             Plugins
                         │
                         ▼
                      SQLite
```

F7Hub should not be measured by how many features it accumulates.

It should be measured by how well those features cooperate to help a technician:

```text
Understand
   ↓
Search
   ↓
Troubleshoot
   ↓
Automate
   ↓
Resolve
   ↓
Document
   ↓
Reuse Knowledge
```

The best F7Hub features are the ones that reduce context switching while preserving technician control.
