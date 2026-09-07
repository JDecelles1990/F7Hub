# F7Hub GUI Design

> Document: `Docs/05_GUI.md`  
> Project: F7Hub  
> Purpose: Define the intended graphical user interface, navigation model, workspace structure, panel behavior and interaction principles for F7Hub.  
> Scope: Product-level GUI behavior and layout.  
> Related Documents: `03_Features.md`, `04_UserWorkflows.md`, `06_SystemArchitecture.md`, `13_PythonArchitecture.md`

---

# 1. Purpose

This document defines how F7Hub should present its features to the technician.

It answers:

> How should F7Hub look, behave and organize technician workflows?

This document defines:

- main window structure
- navigation
- workspaces
- panels
- module layouts
- command palette
- toolbar behavior
- status areas
- keyboard interaction
- forms
- dialogs
- feedback
- accessibility
- error presentation

Implementation details such as PySide6 classes, signal wiring and threading belong in:

`13_PythonArchitecture.md`

---

# 2. GUI Goals

The interface should optimize for:

1. fast access to support context
2. minimal application switching
3. high information density without clutter
4. keyboard productivity
5. clear current context
6. predictable navigation
7. safe administrative actions
8. strong search
9. resizable workspaces
10. useful multi-monitor behavior

The GUI should feel like a technician workspace rather than a generic database application.

---

# 3. GUI Philosophy

F7Hub should combine useful interaction concepts from:

- VS Code
- ticketing systems
- OneNote
- PowerShell terminals
- command palettes
- knowledge bases
- clipboard managers
- Microsoft administration tools

It should not visually or functionally clone any of them.

The primary interaction principle is:

> Keep the current support context visible while making related actions easy to reach.

---

# 4. Current Implementation Status

Repository inspection and tests through 2026-09-06 verified ticket creation, quick company/contact creation, the saved-ticket workspace and Knowledge Base create/list/read plus DRAFT editing with version history in the application shell.

```text
TicketCreateWidget: VERIFIED
Application entry point, bootstrap and MainWindow: VERIFIED
Saved-ticket list, details, notes and status controls: VERIFIED
Remaining navigation and GUI modules: PLANNED
Knowledge Base create/list/read: VERIFIED
Knowledge DRAFT editing, current version and stale-edit feedback: VERIFIED
GUI tests: PASS — 52 tests (fresh Slice 011 final regression)
Application and GUI integration tests: PASS — 50 tests (fresh Slice 011 final regression)
```

`TicketCreateWidget` provides the minimum ticket input form, inline required-field feedback, safe persistence-error presentation, input preservation, keyboard save action, service delegation and a successful-ticket signal. The main window provides New ticket and Saved tickets navigation. Successful creation opens the saved ticket. The queue supports status filtering and pages of 100 tickets; details show notes, lifecycle history and timeline events. Technicians can add notes, resolve with a summary, close and reopen using service-provided status choices.

Failed saves preserve drafts. Switching tickets or leaving activity drafts prompts before discarding them; failed loads preserve existing details and drafts. A committed save followed by a failed reload remains reported as saved. If the initial detail load fails after creation, the queue refreshes so the saved ticket can be opened again. Operations disable conflicting actions while running; closing waits for the operation to finish. Automated GUI checks run offscreen; native Windows visual inspection and input-event checks are PASS on 2026-09-05 at the default size and 1000×700. Initial window sizing now leaves space for Windows borders and the taskbar. Reference-data loading is verified: New Ticket loads active companies and company-filtered active contacts through a background service call. Changing company clears the old contact. Refresh references supports retry and preserves draft text and valid selections. Saved ticket details display company/contact names, including inactive references; null or deleted references show Not selected. Native Windows Slice 006 visual/input checks passed at the initial size and 1000×700, including error feedback. The AutoHotkey F7 shortcut launches, focuses or restores the application while its script is active.

Slice 007 category integration is verified on 2026-09-05. New Ticket loads active TICKET category names through the existing background runner, with independent ID values, Not selected, empty feedback and a Refresh categories retry action. Category failures preserve text and company/contact/category selections; category-only retry does not query companies or contacts. Saved details show current category names, including inactive references, and Not selected after null/deletion. The description minimum height is 100 pixels so the added feedback row fits at 1000×700. Native Windows renders and input checks passed for the category workflow and failure feedback; these are agent checks, not user acceptance testing.

Slice 008 adds a secondary **Add Company** action beside the company selector and a bounded **Quick Add Company** dialog with required name, Cancel and Create Company. It opens asynchronously, uses ServiceTaskRunner for persistence, prevents repeated submission and preserves input after errors. Successful creation refreshes only companies and contacts, selects the new company and preserves all unrelated ticket fields. A committed creation with failed refresh is reported distinctly and recovered through Refresh references without another insertion. Company code and broader company/contact management are not exposed.

Native Windows Slice 008 visual/input checks passed on 2026-09-06 for validation, cancel, creation, selection, draft preservation, refresh recovery and saved-ticket reopening at 1000×700. Success feedback shares the Create Ticket action row so it does not force the window above that size. These are agent checks, not user acceptance testing.

Slice 009 adds **Add Contact** beside Contact and a **Quick Add Contact** dialog containing required contact name, optional email, Cancel and Create Contact. It follows the existing asynchronous dialog/worker conventions, retains input on failure and prevents duplicate submission and unsafe close/cancel during writes. Add Contact requires a selected company and an idle runner with no pending company/contact reconciliation.

Contact success refreshes only the selected company's contacts and selects the created ID without changing any other ticket draft field. After a committed write with failed refresh, the form retains contact/company identity, locks company switching and creation actions, blocks ticket submission and offers contact-only retry through Refresh references. Missing contacts after a successful authoritative reload clear pending auto-selection with explicit feedback. If an authoritative read finds the company inactive or deleted, one **Continue without this contact** button appears beside Refresh references. It releases pending auto-selection, clears company/contact choices and refreshes companies without reloading categories or changing the remaining draft. The committed contact stays stored; transient failures remain retryable. Recovery is disabled while a worker is busy, and obsolete contact-load callbacks are ignored. Native Windows input checks and visual inspection passed at 1000×700 on 2026-09-06, including combined Add Company → Add Contact → save/reopen and subsequent deactivation/deletion recovery checks. These are agent checks, not user acceptance testing.

The layouts in this document represent intended product behavior.

---

# 5. Primary GUI Technology

Primary framework:

```text
Python
+
PySide6
```

PySide6 owns:

- main application window
- navigation
- panels
- views
- forms
- dialogs
- workspaces
- command palette
- status displays
- application-level visual state

AutoHotkey v2 may supplement the main GUI with:

- global hotkeys
- quick menus
- lightweight popups
- clipboard actions

AHK should not become a second competing full GUI architecture.

---

# 6. Main Window Concept

The preferred main-window structure is:

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Menu Bar                                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ Toolbar / Command Area                                                       │
├───────────────┬───────────────────────────────────────┬──────────────────────┤
│ Navigation    │ Main Workspace                        │ Context / Assistant  │
│               │                                       │                      │
│ Dashboard     │ Active Module                         │ Ticket Context       │
│ Tickets       │                                       │ Related KB           │
│ Companies     │                                       │ AI Assistant         │
│ Contacts      │                                       │ Diagnostics          │
│ KB            │                                       │                      │
│ Search        │                                       │                      │
│ Scripts       │                                       │                      │
│ Diagnostics   │                                       │                      │
│ Clipboard     │                                       │                      │
│ Prompts       │                                       │                      │
│ Reports       │                                       │                      │
├───────────────┴───────────────────────────────────────┴──────────────────────┤
│ Output / PowerShell / Logs / Activity                                        │
├──────────────────────────────────────────────────────────────────────────────┤
│ Status Bar                                                                   │
└──────────────────────────────────────────────────────────────────────────────┘
```

Not every panel must always be visible.

---

# 7. Main Window Regions

The primary window may contain:

## Menu Bar

Application-wide commands.

## Toolbar

Frequently used actions and context controls.

## Navigation Sidebar

Primary module navigation.

## Main Workspace

The currently active module or workflow.

## Context Panel

Information related to the current ticket, company, contact or diagnostic session.

## Bottom Panel

Output, terminal, logs, diagnostics or activity.

## Status Bar

Application and integration status.

---

# 8. Menu Bar

Suggested top-level structure:

```text
File
Edit
View
Navigate
Ticket
Automation
Database
AI
Tools
Window
Help
```

The menu bar should expose application-level actions rather than every possible feature.

Frequently used actions should also be available through:

- keyboard shortcuts
- toolbar
- command palette
- context menus

---

# 9. Toolbar

The main toolbar may provide:

- back
- forward
- search
- command palette
- new ticket
- active ticket
- active company
- workspace selector
- run diagnostic
- open PowerShell
- quick actions

The toolbar should remain compact.

---

# 10. Navigation Sidebar

The sidebar should provide stable access to major modules.

Suggested structure:

```text
WORKSPACE
├── Dashboard
├── Tickets
├── Companies
└── Contacts

KNOWLEDGE
├── Knowledge Base
├── Search
└── Prompts

AUTOMATION
├── Scripts
├── Diagnostics
├── Clipboard
└── PowerShell

ADMINISTRATION
├── Microsoft 365
├── Reports
└── Plugins

SYSTEM
├── Logs
└── Settings
```

The exact grouping may evolve as features mature.

---

# 11. Navigation Principles

Navigation should:

- preserve module state where appropriate
- make the active module obvious
- support keyboard access
- avoid opening excessive windows
- permit opening related objects from context
- maintain useful navigation history

Example:

```text
Ticket
→ Company
→ Previous Ticket
→ Back
→ Ticket
```

---

# 12. Active Context Display

The GUI should make active support context visible.

Potential display:

```text
Ticket: INC-10254
Company: Contoso
Contact: Alex Martin
Workspace: Helpdesk
```

This context may appear in:

- toolbar
- title area
- context panel
- breadcrumb

The same information should not be redundantly repeated everywhere.

---

# 13. Dashboard

The Dashboard is the technician landing area.

Potential sections:

```text
┌───────────────────────────────────────────────────────────────┐
│ Dashboard                                                     │
├──────────────────────────────┬────────────────────────────────┤
│ Active / Recent Tickets      │ Quick Actions                  │
│                              │                                │
│ INC-10254 Outlook issue      │ + New Ticket                   │
│ INC-10251 VPN issue          │ Search                         │
│ INC-10247 MFA                │ Run Diagnostic                 │
│                              │ Open PowerShell                │
├──────────────────────────────┼────────────────────────────────┤
│ Recent Knowledge             │ Recent Activity                │
│                              │                                │
│ Outlook Profile Repair       │ DNS diagnostic                │
│ Teams Camera Troubleshooting │ KB article updated             │
└──────────────────────────────┴────────────────────────────────┘
```

The dashboard should provide shortcuts rather than duplicate every module.

---

# 14. Ticket Center

The Ticket Center should be one of the primary F7Hub workspaces.

Suggested layout:

```text
┌─────────────────────────────────────────────────────────────────────────┐
│ Tickets                                                                 │
├──────────────────────┬──────────────────────────────────────────────────┤
│ Ticket Queue         │ Ticket Workspace                                 │
│                      │                                                  │
│ Search               │ INC-10254                                        │
│ Filters              │ Outlook cannot connect                           │
│                      │                                                  │
│ INC-10254            │ Details | Notes | Timeline | Attachments         │
│ INC-10253            │                                                  │
│ INC-10252            │ Main ticket content                              │
│ INC-10251            │                                                  │
├──────────────────────┴──────────────────────────────────────┬───────────┤
│                                                           │ Context   │
│                                                           │ KB        │
│                                                           │ Scripts   │
│                                                           │ AI        │
└───────────────────────────────────────────────────────────┴───────────┘
```

---

# 15. Ticket Queue

The ticket list should support:

- search
- filtering
- sorting
- status indicators
- company
- ticket number
- title
- priority
- update date

The list should avoid displaying too many columns by default.

Columns may be configurable later.

---

# 16. Ticket Details

Ticket details may include:

- ticket number
- title
- description
- status
- priority
- company
- contact
- category
- timestamps
- assigned technician where applicable
- external PSA identifier

Editable and read-only information should be visually distinguishable.

---

# 17. Ticket Workspace Tabs

Potential tabs include:

```text
Details
Notes
Timeline
Attachments
Diagnostics
Related
```

Not every related feature must become a tab.

Contextual panels may be better for:

- related KB
- scripts
- AI
- company context

---

# 18. Ticket Notes

The notes interface should support:

- chronological display
- note type
- timestamp
- author/context where applicable
- add note
- copy
- search
- filtering

When writing a note, the technician may access:

- snippets
- clipboard tools
- AI formatting
- templates

---

# 19. Ticket Timeline

Timeline entries may visually distinguish:

- ticket creation
- notes
- status changes
- diagnostics
- scripts
- KB relationships
- attachments
- resolution
- escalation

The timeline should provide concise summaries with expandable details.

---

# 20. Ticket Context Panel

The right-side context panel may contain switchable sections:

```text
Context
KB Matches
Diagnostics
Scripts
AI
Company
Contact
```

This preserves the central ticket workspace while providing related tools.

---

# 21. Company Center

Suggested structure:

```text
┌──────────────────────┬─────────────────────────────────────────────┐
│ Companies            │ Company Details                             │
│                      │                                             │
│ Search               │ Contoso                                     │
│ Contoso              │ Domains                                     │
│ Fabrikam             │ Environment                                 │
│ Northwind            │ Contacts                                    │
│                      │ Tickets                                     │
│                      │ Notes                                       │
│                      │ Links                                       │
└──────────────────────┴─────────────────────────────────────────────┘
```

Company context should emphasize support information rather than CRM-style complexity.

---

# 22. Contact Center

Contacts should display:

- name
- company
- email
- phone
- department
- title
- relevant notes
- ticket history

The interface should make it easy to move between:

```text
Contact
↔ Company
↔ Tickets
```

---

# 23. Knowledge Base

Slice 010 adds Knowledge Base beside New ticket and Saved tickets in the existing toolbar/menu and stacked application shell. The workspace has New Article, a code/title/status table, a clear empty state and a read view with code, title, status, summary and read-only Markdown source. Metadata is explicitly plain text so HTML-like input remains literal.

New Article collects required article code/title/body and optional summary. Creation, list refresh and detail reads use the existing background runner; conflicting pages/navigation are disabled while busy. Duplicate submission is prevented, errors preserve input and detail callbacks check the current selection.

Slice 011 adds Edit Article for a loaded DRAFT and a read-only Version N detail label. Edit is unavailable without loaded details, during reload or for PUBLISHED/ARCHIVED articles. A separate EditArticleDialog keeps creation and revision responsibilities explicit: code and the originally opened version are plain-text labels; title/summary/body are prefilled editable fields; actions are Cancel and Save Revision.

Save uses ServiceTaskRunner, blocks duplicate submission and close/cancel during the write, and closes on success. The list refreshes, reselects the same article ID and reloads current details. Failures preserve entered text. Stale/missing/non-DRAFT conflicts disable further saves in that editor; a new editor must be opened explicitly. Workspace refreshes cannot replace its expected-version token. No-change feedback leaves the editor open and creates no revision after authoritative version checks.

Native Windows input and visual verification at 1000×700 passed for edit prefill, stable code, Version 1 → 2, updated content, navigation/reopen and existing New Article. No clipping/overlap was observed in the synthetic examples; this is agent verification, not user acceptance testing. There is no rendered Markdown, history browser, historical viewer, restore/revert, publishing/archiving, search/FTS, categories/tags, article-to-article relationships, external links or AI.

Slice 012 adds a Knowledge tab to the existing saved-ticket detail tabs. TicketKnowledgeWidget shows a lightweight code/title/status/version table, empty state, Link Article, Open Article and Refresh. Identity columns are sized immediately after loading so the initial article code is readable. Controls are unavailable without a ticket or while the shared runner is busy. LinkArticleDialog provides existing article identities, Cancel and Link Article, plus retry after candidate-load failure; there is no search, filter, preview or relationship-type selector.

List/candidate/link calls use ServiceTaskRunner. Cancel during a candidate read ignores its eventual result; closing during a link waits for completion. Failures retain selection and show safe plain-text feedback. Success selects the new link and refreshes current metadata. TicketWorkspace emits an article-ID signal; MainWindow handles draft-discard protection, switches pages and calls KnowledgeWorkspace.open_article_by_id. A missing target is reported without selecting a different article.

Slice 012 native Windows input checks and visual inspection passed at 1000×700 with isolated synthetic SQLite: empty state, candidate selection, link, current metadata, Open Article, edit/create, notes/status lifecycle and reopening after reconstruction. The initial code-column clipping found during inspection was corrected and the native flow rerun. These are agent checks, not user acceptance testing.

Native Windows agent input checks and visual inspection passed on 2026-09-06 at 1000×700 for the empty state, creation of KB0001 and KB0002, list/detail switching and return through New ticket/Saved tickets. Both articles survived application reconstruction against isolated synthetic SQLite. No clipping/overlap was observed for these inputs. These are agent checks, not user acceptance testing. The broader layouts below remain planned.

Suggested layout:

```text
┌──────────────────────┬─────────────────────────────────────────────┐
│ KB Navigation        │ Article                                    │
│                      │                                             │
│ Search               │ Outlook Cached Credentials                  │
│ Categories           │                                             │
│ Tags                 │ Symptoms                                    │
│ Technologies         │ Cause                                       │
│                      │ Resolution                                  │
│ Results              │ Verification                                │
│                      │ Escalation                                  │
└──────────────────────┴─────────────────────────────────────────────┘
```

---

# 24. Knowledge Article Structure

The GUI should support structured article sections where useful.

Examples:

```text
Overview
Symptoms
Environment
Cause
Resolution
Verification
Commands
Scripts
Escalation
References
```

Article type may determine which sections are shown.

---

# 25. Knowledge Editor

The knowledge editor should support:

- title
- article type
- metadata
- tags
- structured content
- related scripts
- related tickets
- preview
- save
- lifecycle state

Markdown support may be used if approved by implementation architecture.

---

# 26. Universal Search

Search should be accessible globally.

Potential layout:

```text
Search: outlook cached credentials

[All] [Tickets] [KB] [Scripts] [Companies] [Contacts]

KB
────────────────────────────────────────
Outlook Cached Credentials
Repairing an Outlook profile

Tickets
────────────────────────────────────────
INC-10254 Outlook sign-in issue

Scripts
────────────────────────────────────────
Reset-OutlookProfile.ps1
```

Search results should clearly indicate their source type.

---

# 27. Search Result Actions

Results should support direct actions where safe.

Examples:

```text
Ticket
→ Open

KB
→ Open

Company
→ Open Context

Script
→ Review

Command
→ Run Registered Action
```

Search should support the pattern:

```text
Search → Find → Open → Act
```

---

# 28. Script Library

Suggested layout:

```text
┌──────────────────────────┬──────────────────────────────────────────┐
│ Script Library           │ Script Details                           │
│                          │                                          │
│ Search                   │ Test-DnsHealth.ps1                       │
│ Categories               │ Description                              │
│ Tags                     │ Risk: Low                                │
│                          │ Privilege: User                           │
│ DNS                      │ Parameters                               │
│ Exchange                 │                                          │
│ Intune                   │ [Review Script] [Run]                    │
└──────────────────────────┴──────────────────────────────────────────┘
```

---

# 29. Script Execution Dialog

Before execution, display:

- script name
- purpose
- target
- parameters
- privilege requirement
- risk level
- related ticket if applicable

Example:

```text
Run Script

Script:
Test-DnsHealth.ps1

Target:
PC-1042

Privilege:
Standard User

Parameters:
Hostname: example.com

[Cancel] [Run]
```

Privileged or destructive actions require stronger confirmation.

---

# 30. PowerShell Output

PowerShell output may appear in a bottom panel.

Possible tabs:

```text
PowerShell
Output
Errors
Activity
```

The panel should distinguish:

- running
- successful
- failed
- cancelled

Structured results may be rendered in a more readable form than raw JSON.

---

# 31. Diagnostic Center

Suggested layout:

```text
┌─────────────────────────┬───────────────────────────────────────────┐
│ Diagnostic Workflows    │ Current Diagnostic                        │
│                         │                                           │
│ Outlook                 │ Outlook Cannot Connect                    │
│ MFA                     │                                           │
│ VPN                     │ Step 3 of 7                               │
│ DNS                     │                                           │
│ Teams                   │ Can the user access Outlook Web?          │
│ Intune                  │                                           │
│                         │ ( ) Yes                                    │
│                         │ ( ) No                                     │
│                         │                                           │
│                         │ [Back] [Next]                              │
└─────────────────────────┴───────────────────────────────────────────┘
```

---

# 32. Diagnostic Workflow UI

The diagnostic interface should show:

- workflow title
- purpose
- progress
- current step
- inputs
- automated result where applicable
- previous answers
- next action

The technician should be able to understand why the workflow is progressing to the next step.

---

# 33. Diagnostic Result

At completion, display:

```text
Diagnostic Complete

Status:
Issue Identified

Finding:
DNS resolution is failing.

Evidence:
Server lookup failed.
Gateway reachable.

Recommended Next Step:
Reset DNS configuration.

Related KB:
DNS Resolution Troubleshooting

Approved Script:
Reset-NetworkDns.ps1
```

The result should be easy to attach or summarize into a ticket.

---

# 34. Clipboard Center

Potential layout:

```text
┌───────────────────────┬────────────────────────────────────────────┐
│ Clipboard History     │ Preview / Actions                          │
│                       │                                            │
│ Search                │ Selected clipboard content                 │
│                       │                                            │
│ Recent                │ Copy                                       │
│ Snippets              │ Insert                                     │
│ Templates             │ Transform                                  │
│                       │ Save as Snippet                            │
└───────────────────────┴────────────────────────────────────────────┘
```

Sensitive-content controls should remain visible and easy to access.

---

# 35. Clipboard Actions

Potential transformations:

- plain text
- remove extra whitespace
- uppercase
- lowercase
- extract URLs
- extract email addresses
- extract IP addresses
- format ticket note

The technician should be able to preview potentially destructive transformations before replacing existing content.

---

# 36. Prompt Library

Suggested structure:

```text
┌───────────────────────┬────────────────────────────────────────────┐
│ Prompts               │ Prompt Details                             │
│                       │                                            │
│ Search                │ Ticket Escalation Summary                  │
│ Categories            │                                            │
│                       │ Variables                                  │
│ Ticketing             │ {{ticket_title}}                           │
│ Knowledge             │ {{diagnostic_results}}                     │
│ PowerShell            │                                            │
│                       │ [Preview] [Use]                             │
└───────────────────────┴────────────────────────────────────────────┘
```

---

# 37. AI Assistant Panel

The AI Assistant may appear as a dockable contextual panel.

Potential functions:

- summarize ticket
- suggest troubleshooting
- improve notes
- explain script
- suggest KB
- interpret diagnostic results

The panel should clearly distinguish:

```text
F7Hub Data
AI Suggestion
Technician Decision
```

AI suggestions must not visually masquerade as verified system facts.

---

# 38. AI Safety UI

Before sending potentially sensitive context externally, F7Hub should provide appropriate transparency.

Possible controls:

- context preview
- included sources
- excluded sensitive fields
- provider
- submit/cancel

For administrative actions:

```text
AI Suggestion
    ↓
Technician Review
    ↓
Explicit Action
```

Never:

```text
AI Suggestion
    ↓
Automatic Destructive Execution
```

---

# 39. Microsoft Administration Center

Suggested function:

- portal launcher
- administrative shortcuts
- diagnostic actions
- supported Graph/PowerShell operations

Potential navigation:

```text
Microsoft 365
├── M365 Admin
├── Entra
├── Exchange
├── Intune
├── Defender
├── Teams
└── SharePoint
```

F7Hub should not attempt to replicate entire Microsoft portals.

---

# 40. Reports

The Reports module may include:

- report type
- filters
- preview
- export

Examples:

- diagnostic report
- script execution report
- ticket activity
- troubleshooting summary

---

# 41. Settings

Settings should be categorized.

Possible sections:

```text
General
Appearance
Paths
Database
PowerShell
AutoHotkey
Clipboard
AI
Microsoft
Integrations
Plugins
Logging
Advanced
```

Secrets should not be exposed as ordinary plaintext settings.

---

# 42. Settings Validation

When configuration is invalid:

- identify the affected field
- explain the issue
- preserve other valid changes
- avoid corrupting the entire configuration

A reset mechanism should exist for recoverable settings.

---

# 43. Logs and Activity

The Logs module may support:

- severity filtering
- subsystem filtering
- date filtering
- search
- details

Example:

```text
12:04:33 INFO    Database initialized
12:04:34 INFO    Workspace restored
12:04:39 WARNING Microsoft Graph unavailable
12:05:03 ERROR   Diagnostic script failed
```

Sensitive information must be sanitized.

---

# 44. Dockable Panels

Potential dockable panels include:

- Ticket Queue
- Ticket Details
- Notes
- Timeline
- Company Context
- Contact Context
- Knowledge Matches
- Search
- AI Assistant
- PowerShell
- Script Library
- Clipboard
- Output
- Activity
- Logs

Not every module should become a dock.

Docking should be used where persistent simultaneous context is valuable.

---

# 45. Panel Behavior

Where appropriate, panels may support:

- dock
- undock
- float
- resize
- hide
- restore
- move to another monitor

Panel configuration may be persisted as part of a workspace.

---

# 46. Workspace Profiles

Potential predefined workspaces:

## Helpdesk

Emphasis:

- Tickets
- Notes
- KB
- Diagnostics
- AI

## Microsoft 365

Emphasis:

- ticket context
- PowerShell
- Microsoft administration
- output

## Networking

Emphasis:

- diagnostics
- scripts
- PowerShell
- technical notes

## Automation

Emphasis:

- script library
- parameters
- PowerShell
- output
- logs

## Knowledge Authoring

Emphasis:

- KB editor
- source ticket
- search
- AI assistance

## AI

Emphasis:

- AI panel
- ticket context
- knowledge
- prompt library

---

# 47. Workspace Persistence

Workspace state may include:

- visible panels
- docking locations
- panel sizes
- active module
- selected workspace profile

Sensitive operational content should not necessarily be restored automatically.

Example:

Restoring panel layout is acceptable.

Automatically rerunning a privileged diagnostic is not.

---

# 48. Command Palette

The command palette should provide fast keyboard navigation.

Example:

```text
> open ticket 10254

Open Ticket INC-10254
```

Other examples:

```text
> dns
Run DNS Diagnostic
Search KB: DNS
Open Networking Workspace

> exchange
Open Exchange Admin Center
Search Exchange Scripts
Search Exchange KB
```

---

# 49. Command Palette Categories

Potential command categories:

- navigation
- tickets
- search
- knowledge
- scripts
- diagnostics
- workspaces
- tools
- Microsoft
- settings

Command search should prioritize useful actions rather than exposing internal implementation names.

---

# 50. Keyboard Productivity

Common tasks should eventually have keyboard shortcuts.

Potential examples:

```text
Ctrl+K
→ Command Palette

Ctrl+F
→ Contextual Search

Ctrl+S
→ Save

Ctrl+Shift+F
→ Universal Search

Ctrl+N
→ New Item in Current Context
```

Exact shortcut assignments must avoid conflicts and belong in approved GUI conventions.

---

# 51. Context Menus

Context menus should expose actions appropriate to the selected object.

Example ticket context menu:

```text
Open
Add Note
Run Diagnostic
Search Related KB
Copy Ticket Number
Open Company
```

Avoid excessively long context menus.

---

# 52. Forms

Forms should:

- group related information
- clearly identify required fields
- provide inline validation
- preserve entered information after recoverable errors
- support keyboard navigation
- avoid excessive modal dialogs

---

# 53. Validation Feedback

Invalid input should be shown near the relevant control where possible.

Example:

```text
Company Name
[                       ]

⚠ Company name is required.
```

A single generic error dialog should not replace useful field-level validation.

---

# 54. Dialog Philosophy

Use modal dialogs for actions requiring focused decisions.

Appropriate examples:

- privileged script confirmation
- destructive action
- unsaved changes
- authentication flow
- migration failure requiring intervention

Routine navigation should not depend heavily on modal dialogs.

---

# 55. Destructive Action Confirmation

Destructive actions should clearly identify:

```text
Action
Target
Impact
```

Example:

```text
Disable User Account

Target:
alex@contoso.com

Impact:
The user may immediately lose access to Microsoft 365 services.

[Cancel] [Disable Account]
```

Generic dialogs such as:

```text
Are you sure?
```

should be avoided for high-impact actions.

---

# 56. Feedback States

Operations should clearly communicate:

```text
IDLE
RUNNING
SUCCESS
WARNING
FAILED
CANCELLED
```

Examples:

- progress indicator
- status message
- result panel
- error indicator

The GUI should not falsely indicate completion while a background operation is still running.

---

# 57. Long-Running Operations

For operations such as:

- PowerShell scripts
- Graph requests
- AI calls
- report generation
- search indexing

the GUI should:

- remain responsive
- show operation status
- support cancellation where safe
- prevent accidental duplicate execution where appropriate

---

# 58. Error Presentation

Technical errors should be translated into useful technician-facing messages.

Example:

Instead of only:

```text
sqlite3.OperationalError
```

show:

```text
F7Hub could not save the ticket because the database operation failed.

Your entered information has been preserved.

View technical details
```

Technical details may remain available for troubleshooting.

---

# 59. Empty States

Empty states should explain what the user can do.

Example:

```text
No knowledge articles found.

Try another search or create a new KB article.
```

Avoid large blank panes with no explanation.

---

# 60. Loading States

When data retrieval is not immediate, show a visible loading state.

The technician should be able to distinguish:

- no data
- loading
- failed retrieval

---

# 61. Integration Status

Connected services may display status such as:

```text
SQLite          Connected
PowerShell      Available
Microsoft Graph Not Connected
AI              Available
HaloPSA         Not Configured
```

Status must reflect real application state.

---

# 62. Status Bar

Possible status-bar information:

```text
DB ✓ | PowerShell ✓ | Graph ○ | AI ✓ | Workspace: Helpdesk | F7Hub 0.1.0
```

The status bar should remain concise.

Detailed diagnostics belong elsewhere.

---

# 63. Theme

F7Hub should eventually support:

- dark mode
- light mode

Visual design should prioritize readability over decorative effects.

A modern Windows appearance is appropriate, but visual effects should not interfere with:

- contrast
- text clarity
- performance
- accessibility

---

# 64. Visual Hierarchy

Use visual emphasis deliberately.

Most prominent:

- active task
- ticket title
- critical warning
- primary action

Less prominent:

- metadata
- timestamps
- secondary links

The application should avoid making every control equally visually loud.

---

# 65. Color Usage

Color should communicate state rather than decorate randomly.

Examples:

- error
- warning
- success
- running
- inactive
- selected

Important state must not rely solely on color.

Icons and text should reinforce meaning.

---

# 66. Icons

Icons may improve navigation and recognition.

Use consistent icon families where licensing permits.

Icons should not replace labels for unfamiliar or critical actions.

---

# 67. Typography

Typography should prioritize:

- readability
- hierarchy
- consistency
- Windows scaling compatibility

Monospace fonts may be appropriate for:

- PowerShell
- command output
- code
- SQL
- logs

Normal interface text should use the application UI font.

---

# 68. Scaling

The GUI should behave correctly with common Windows display scaling settings.

Important target scenarios:

- 100%
- 125%
- 150%

Hard-coded pixel assumptions should be minimized.

---

# 69. Minimum Window Behavior

When the window becomes smaller:

- core content remains usable
- secondary panels may collapse
- scrolling is preferable to overlapping controls
- critical buttons remain accessible

---

# 70. Multi-Monitor Support

Dockable or floating panels may eventually support placement on secondary monitors.

Example:

```text
Monitor 1
→ Ticket Workspace

Monitor 2
→ PowerShell + KB + AI
```

Saved layout behavior across changing monitor configurations must fail gracefully.

---

# 71. Accessibility

The GUI should support:

- keyboard navigation
- focus indication
- readable text
- scalable interface
- meaningful labels
- sufficient contrast

Core workflows should not require precise mouse-only interactions.

---

# 72. Keyboard Focus

Focus behavior should be predictable.

Examples:

Opening universal search should place focus directly in the search box.

Opening a new ticket should focus the first required field.

Unexpected focus jumps should be avoided.

---

# 73. Data Tables

Tables should support appropriate:

- sorting
- filtering
- column sizing
- selection
- context actions

Large tables should use pagination or incremental loading where appropriate.

---

# 74. Read vs Edit Modes

Complex records should not always appear permanently editable.

Where appropriate:

```text
View
→ Edit
→ Save / Cancel
```

This reduces accidental changes.

---

# 75. Save Behavior

Save actions should:

- validate
- persist
- clearly report success/failure
- preserve data on recoverable failure

The application should not silently discard unsaved changes.

---

# 76. Unsaved Changes

When navigating away from meaningful unsaved changes:

```text
Save
Discard
Cancel Navigation
```

should be available where appropriate.

---

# 77. Notifications

Notifications should be used sparingly.

Appropriate examples:

- script completed
- diagnostic failed
- integration disconnected
- export completed

Routine successful actions should not produce disruptive popups unnecessarily.

---

# 78. Search Everywhere Principle

Where practical, lists should support search.

Examples:

- tickets
- companies
- contacts
- KB
- scripts
- prompts
- logs

Search behavior should remain consistent.

---

# 79. Context Preservation

Moving between related views should preserve active context.

Example:

```text
Open Ticket
    ↓
Open Related Company
    ↓
Review Company
    ↓
Back
    ↓
Same Ticket
```

This is preferable to making the technician reconstruct the workflow manually.

---

# 80. F7Hub vs External Applications

When an external tool is better suited to the task, F7Hub should launch or integrate with it.

Examples:

```text
VS Code
→ edit scripts

Microsoft Admin Center
→ complex portal administration

Keeper
→ credential management

NinjaOne
→ RMM functions

HaloPSA
→ PSA-specific workflows
```

F7Hub should act as the coordinating workspace.

---

# 81. Initial GUI Scope

The first useful GUI should remain limited.

Recommended initial modules:

```text
Main Application Shell
Dashboard
Tickets
Companies
Contacts
Knowledge Base
Search
Script Library
Settings
Logs
```

This is enough to validate:

- navigation
- persistence
- repositories
- services
- workflows
- search
- state management

---

# 82. Second GUI Stage

After the initial core is stable:

```text
Diagnostics
PowerShell Panel
Clipboard Center
Command Palette
Workspace Profiles
Reporting
```

---

# 83. Later GUI Stage

Future additions:

```text
AI Center
Microsoft Administration
Plugins
HaloPSA Integration
NinjaOne Integration
Advanced Reporting
```

These should not overload the initial application shell.

---

# 84. GUI Architecture Boundary

The GUI must call application services.

Preferred:

```text
Button
  ↓
GUI Controller / View Logic
  ↓
Application Service
  ↓
Repository / Gateway
```

Avoid:

```text
Button
  ↓
SQL Query
```

or:

```text
Button
  ↓
Construct Arbitrary PowerShell
```

---

# 85. GUI State Boundary

Widgets should not become the sole source of application state.

Persistent or shared state should live in appropriate services/models.

Example:

```text
Active ticket
→ application context

Text currently typed into a note editor
→ widget state
```

---

# 86. GUI Testing Priorities

High-priority GUI workflows should include:

1. application startup
2. module navigation
3. create ticket
4. open ticket
5. edit ticket
6. add note
7. ticket search
8. KB search
9. create KB article
10. script review/execution workflow
11. error presentation
12. unsaved changes

---

# 87. GUI Acceptance Criteria

A GUI feature should normally satisfy:

```text
[ ] Clear entry point
[ ] Correct context displayed
[ ] Keyboard navigation considered
[ ] Input validation visible
[ ] Loading state handled
[ ] Empty state handled
[ ] Error state handled
[ ] Success state handled
[ ] Unsaved data protected
[ ] Long-running tasks do not freeze GUI
[ ] Architecture boundary preserved
```

---

# 88. GUI Anti-Patterns

Avoid:

## Giant Main Window

Every feature displayed simultaneously.

## Modal Overload

Routine tasks require repeated popups.

## Hidden Context

Technician cannot tell which ticket or company is active.

## Raw Technical Errors Only

Low-level exceptions are shown with no useful explanation.

## GUI-Owned SQL

Widgets directly query the database.

## GUI-Owned PowerShell

Buttons construct arbitrary shell commands.

## Excessive Tabs

Every piece of information becomes another tab.

## Decorative Density

Too many colors, borders, icons and visual effects reduce readability.

## Mouse-Only Navigation

Important actions cannot be reached efficiently from the keyboard.

---

# 89. GUI Design Decision Rule

For each new interface element, ask:

1. What technician task does it support?
2. Does it belong in the current context?
3. Does an existing panel already provide this function?
4. Should it be persistent or temporary?
5. Is a panel, page, dialog or command more appropriate?
6. Does it reduce or increase context switching?
7. Can the technician understand its state?
8. Is the operation safe?

---

# 90. Core F7Hub Workspace

The intended experience is:

```text
┌───────────────────────────────────────────────────────────────────────────┐
│ F7Hub                                                                     │
├───────────────────────────────────────────────────────────────────────────┤
│ Search / Commands / Active Ticket / Workspace                             │
├───────────────┬───────────────────────────────────────┬───────────────────┤
│ Navigation    │ Current Work                          │ Context           │
│               │                                       │                   │
│ Dashboard     │ Ticket / KB / Script / Diagnostic    │ Company           │
│ Tickets       │                                       │ Related KB        │
│ KB            │                                       │ Diagnostics       │
│ Search        │                                       │ AI                │
│ Scripts       │                                       │                   │
├───────────────┴───────────────────────────────────────┴───────────────────┤
│ PowerShell / Output / Activity / Logs                                     │
├───────────────────────────────────────────────────────────────────────────┤
│ DB ✓ | PS ✓ | Graph ○ | AI ✓ | Workspace: Helpdesk                        │
└───────────────────────────────────────────────────────────────────────────┘
```

This layout is conceptual rather than a fixed pixel specification.

---

# 91. Relationship to Other Documents

## `03_Features.md`

Defines:

> What capabilities exist?

## `04_UserWorkflows.md`

Defines:

> How does the technician use them?

## `05_GUI.md`

Defines:

> How are those capabilities presented and interacted with?

## `06_SystemArchitecture.md`

Defines:

> How do the underlying components cooperate?

## `13_PythonArchitecture.md`

Defines:

> How is the PySide6 implementation structured internally?

---

# 92. Final GUI Principles

The F7Hub interface should:

- keep technician context visible
- reduce unnecessary application switching
- make search central
- expose related knowledge quickly
- integrate diagnostics and automation safely
- remain keyboard-friendly
- support dockable workflows where useful
- remain responsive during long operations
- provide clear states and errors
- preserve unsaved technician work
- avoid duplicating external applications
- remain understandable as features grow

The core GUI principle is:

> Show the technician what matters for the current task, keep related tools nearby, and hide complexity that is not currently useful.

F7Hub should feel like one coherent workspace, not twenty utilities taped together.
