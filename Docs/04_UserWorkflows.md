# F7Hub User Workflows

> Document: `Docs/04_UserWorkflows.md`  
> Project: F7Hub  
> Purpose: Define how technicians interact with F7Hub to complete common IT support tasks.  
> Scope: User journeys, workflow sequences, decision points and expected outcomes.  
> Related Documents: `02_ProductRequirements.md`, `03_Features.md`, `05_GUI.md`, `06_SystemArchitecture.md`, `07_Database.md`

---

# 1. Purpose

This document defines the principal user workflows of F7Hub.

It answers:

> How does the technician use F7Hub to accomplish real support work?

This document focuses on:

- technician actions
- workflow sequences
- decision points
- expected results
- feature interactions
- failure and escalation paths

It does not define:

- exact GUI layouts
- database tables
- Python classes
- PowerShell implementation details
- SQL schemas

Those belong in architecture-specific documents.

---

# 2. Workflow Philosophy

F7Hub should guide technicians through useful workflows without forcing unnecessary steps.

The primary support lifecycle is:

```text
Receive Work
    ↓
Understand Context
    ↓
Search Existing Knowledge
    ↓
Troubleshoot
    ↓
Run Diagnostics
    ↓
Use Approved Automation
    ↓
Evaluate Results
    ↓
Resolve or Escalate
    ↓
Document Work
    ↓
Preserve Knowledge
```

The technician remains in control throughout the workflow.

---

# 3. Workflow Principles

All workflows should follow these principles:

1. preserve context
2. minimize repetitive navigation
3. reuse existing information
4. expose relevant knowledge early
5. prefer deterministic troubleshooting where possible
6. preserve technician control
7. validate before privileged actions
8. preserve useful history
9. support failure and escalation paths
10. avoid unnecessary duplication of work

---

# 4. Primary User Context

F7Hub may maintain an active support context containing:

```text
Active Context
│
├── Ticket
├── Company
├── Contact
├── Diagnostic Session
└── Workspace
```

When practical, related modules should use this context.

Example:

Opening a ticket may automatically make its:

- company
- contact
- related knowledge
- diagnostics
- scripts
- timeline

available to other modules.

---

# 5. Workflow Status

The workflows in this document represent intended product behavior.

Repository inspection determines whether individual workflows exist:

```text
Workflow implementation status: MIXED
```

The 2026-09-02 inspection is historical and does not describe every current
implementation. Individual sections identify verified behavior where it is
material to the technician workflow.

A documented workflow does not prove that the corresponding functionality currently exists.

---

# 6. Application Startup Workflow

Related Features:

- `FEAT-APP-001`
- `FEAT-APP-002`
- `FEAT-DASH-001`

## Goal

Start F7Hub and reach a usable technician workspace.

## Workflow

```text
Launch F7Hub
    ↓
Load Configuration
    ↓
Initialize Logging
    ↓
Validate Environment
    ↓
Open SQLite Database
    ↓
Check Migrations
    ↓
Initialize Core Services
    ↓
Attempt Optional Integrations
    ↓
Restore Workspace
    ↓
Display Main Window
    ↓
Ready
```

## Expected Outcome

The technician reaches the main application even if optional services such as AI or Microsoft Graph are unavailable.

## F7 Launch / Focus Shortcut

When the AutoHotkey v2 shortcut script is active, the technician can press
global `F7` to reach F7Hub. If the exact F7Hub window is already running, the
shortcut restores it when minimized and focuses it. Otherwise, it starts the
project-local Python application. The shortcut provides Windows launch/focus
integration only; the PySide6 application remains the GUI owner. Detailed
behavior and validation status belong in `11_AHKArchitecture.md`.

## Failure Paths

### Database Failure

```text
Database initialization fails
    ↓
Prevent unsafe writes
    ↓
Display meaningful error
    ↓
Provide recovery information
```

### Optional Integration Failure

```text
Microsoft Graph unavailable
    ↓
Mark integration unavailable
    ↓
Continue local application startup
```

---

# 7. Open Existing Ticket Workflow

Related Features:

- `FEAT-TICKET-001`
- `FEAT-TICKET-002`
- `FEAT-TICKET-004`

## Goal

Open an existing ticket and establish support context.

## Workflow

```text
Open Tickets
    ↓
Search or Select Ticket
    ↓
Load Ticket
    ↓
Load Company
    ↓
Load Contact
    ↓
Load Notes
    ↓
Load Timeline
    ↓
Load Related Resources
    ↓
Set Active Ticket Context
    ↓
Display Ticket Workspace
```

## Related Resources May Include

- related tickets
- knowledge articles
- diagnostic workflows
- script recommendations
- attachments
- company context
- previous activity

## Expected Outcome

The technician can understand the case without manually reopening information across unrelated tools.

---

# 8. Create Ticket Workflow

Related Requirements:

- `FR-TICKET-001`

Related Feature:

- `FEAT-TICKET-001`

## Goal

Create a local F7Hub ticket record.

## Workflow

```text
New Ticket
    ↓
Enter Required Information
    ↓
Select Company
    ↓
Select Contact
    ↓
Enter Description
    ↓
Validate
    ↓
Save
    ↓
Create Ticket Record
    ↓
Create Initial Timeline Event
    ↓
Open Ticket Workspace
```

## Implemented Reference Selection — Slices 006–007

New Ticket loads active company names. Selecting a company loads only its active contacts; changing or clearing the company clears the previous contact. Both selections remain optional. Refresh references retries failed loads without clearing ticket text or valid selections. Creation revalidates active references and company/contact membership inside its existing transaction.

Successful creation opens Saved Tickets. Reopening displays company and contact names, including names of subsequently inactive rows. Null references show Not selected. Existing foreign keys clear references on deletion; deleted names are not retained as historical snapshots.

Validation on 2026-09-05: automated integration and native Windows visual/input checks with isolated synthetic data are PASS, including empty choices, query failure, stale selections, draft preservation and create/reopen.

Slice 007 adds optional active TICKET category choices, ordered by sort order, name and category ID. New Ticket displays category names and saves the separate ID through the existing creation service. Refresh categories retries just that list without reloading companies or contacts; a failed load preserves the draft and selected references. No active categories leaves Not selected available. Full reference refresh also loads categories, and company switching preserves the category selection.

Saved Tickets displays the current category name, including subsequently inactive categories. Null or deleted references display Not selected. Creation rejects inactive, wrong-scope or missing categories without partial ticket/history/timeline writes. Native Windows category selection, failure/retry, optional creation and reopening were verified with synthetic data on 2026-09-05.

## Quick Company Creation — Slice 008

From New Ticket, choose **Add Company**, enter the required company name and choose **Create Company**. The service trims the name and creates an active company. Company code is not exposed. Duplicate names remain allowed. Cancel, Escape and closing the dialog before submission perform no write and preserve the ticket draft. During creation, duplicate submission and closing are blocked until the worker finishes.

After creation, the company list refreshes in its existing stable order, the new company is selected and the previous contact is cleared. Contacts load for the new company; categories are not reloaded. Ticket number, subject, type, priority, category and description remain intact. Saving still uses TicketService, and reopening displays the new company name.

A failed write retains dialog input for retry. If creation commits but the company refresh fails, the dialog completes and the form explicitly reports successful creation with a refresh problem. The committed ID is retained for **Refresh references** recovery; Add Company and ticket submission cannot repeat or bypass the pending recovery. Choosing another company explicitly replaces that pending selection. A contact-load failure retains the newly selected company and permits reference retry.

Native Windows synthetic-data checks on 2026-09-06 passed for validation, cancel, creation, refresh recovery, draft preservation and save/reopen at 1000×700. Full company management and contact creation remain outside this slice.

## Quick Contact Creation — Slice 009

From New Ticket, select an active company (including one just created through Add Company), choose **Add Contact**, enter the required contact name and optional email, and choose **Create Contact**. Add Contact is unavailable without a selected company or during background work/pending reference reconciliation. The service validates the current company, trims name/email, stores blank email as NULL and creates an active contact; duplicate names/emails remain allowed.

Success closes the dialog, reloads only that company's contacts and selects the new contact. Ticket number, subject, type, priority, company, category and description remain intact. Save and reopen through the existing ticket workflow displays the correct company/contact labels. Cancel before submission performs no write; validation/write failures retain dialog inputs, and submission blocks duplicate writes and unsafe close/cancel actions while the worker finishes.

If contact creation commits but selector refresh fails, the form reports successful creation and retains the contact and company IDs. Company switching, Add Company, Add Contact and ticket submission are blocked until **Refresh references** reconciles the contact; retry reads only contacts and never repeats the insertion. If a successful later read no longer includes the contact, auto-selection is abandoned with explicit feedback and the technician can choose another contact or continue without one. TicketService remains the authoritative save-time integrity boundary.

If the company is deactivated or deleted after the contact commits, the form explains that the saved contact could not be selected and offers **Continue without this contact**. This explicitly abandons auto-selection, clears the pending lock and company/contact selections, and refreshes active companies without reloading categories. All non-reference ticket fields remain intact. The technician can select another active company/contact or save without references. The contact is never inserted again or deleted by recovery; company deletion retains the contact with a NULL company ID under the existing foreign key rule. Transient read failures retain the ordinary retry path.

Native Windows synthetic-data checks on 2026-09-06 passed for validation, cancel, create, auto-selection, every draft field, post-commit recovery, combined company/contact creation and save/reopen. Form/dialog/saved-ticket layout was inspected at 1000×700. Contact editing/deletion and full management remain deferred.

## Validation Examples

- required fields present
- company reference valid
- contact reference valid
- values within expected limits

## Failure Path

```text
Validation Fails
    ↓
Highlight Invalid Data
    ↓
Preserve Entered Information
    ↓
Allow Correction
```

---

# 9. Ticket Investigation Workflow

Related Features:

- Ticket Center
- Company Center
- Contact Center
- Knowledge Base
- Search
- Diagnostics

## Goal

Understand the issue before attempting remediation.

## Workflow

```text
Open Ticket
    ↓
Read Description
    ↓
Review Existing Notes
    ↓
Review Company Context
    ↓
Review Contact History
    ↓
Check Related Tickets
    ↓
Search Knowledge
    ↓
Identify Likely Issue Category
    ↓
Choose Troubleshooting Path
```

## Technician Questions

The workflow should help answer:

- What is failing?
- Who is affected?
- When did it start?
- What changed?
- Is this isolated or widespread?
- Has this happened before?
- What troubleshooting has already been performed?
- Is there an existing KB article?
- Is there an approved diagnostic workflow?

---

# 10. Add Ticket Note Workflow

Related Feature:

- `FEAT-TICKET-003`

## Goal

Record meaningful support activity.

## Workflow

```text
Open Ticket
    ↓
Select Add Note
    ↓
Choose Note Type
    ↓
Enter / Paste Content
    ↓
Optionally Format or Improve
    ↓
Review
    ↓
Save
    ↓
Add Timeline Event
```

## Possible Note Types

- troubleshooting
- internal
- customer communication
- escalation
- resolution

## Expected Outcome

The note becomes part of the persistent ticket history.

---

# 11. Ticket Resolution Workflow

Related Feature:

- `FEAT-TICKET-008`

## Goal

Record a successful resolution clearly.

## Workflow

```text
Issue Resolved
    ↓
Review Troubleshooting Performed
    ↓
Record Root Cause if Known
    ↓
Record Resolution
    ↓
Record Verification
    ↓
Link Relevant KB if Applicable
    ↓
Update Ticket Status
    ↓
Save
```

## Resolution Content Should Ideally Include

- issue
- root cause
- actions performed
- final resolution
- verification
- relevant commands or scripts
- KB reference

---

# 12. Ticket Escalation Workflow

Related Feature:

- `FEAT-TICKET-008`

## Goal

Escalate a ticket with sufficient technical context.

## Workflow

```text
Unable to Resolve
    ↓
Review Troubleshooting History
    ↓
Collect Diagnostic Results
    ↓
Collect Relevant Logs
    ↓
Record Attempts
    ↓
Describe Current State
    ↓
Specify Escalation Reason
    ↓
Recommend Next Step
    ↓
Create Escalation Summary
```

## Escalation Summary Should Include

- issue
- affected user/system
- troubleshooting performed
- results
- failed remediation
- relevant logs
- diagnostic evidence
- suspected cause
- next recommended action

---

# 13. Company Context Workflow

Related Features:

- `FEAT-COMPANY-001`
- `FEAT-COMPANY-002`

## Goal

Access company-specific support information while troubleshooting.

## Workflow

```text
Open Ticket
    ↓
Resolve Associated Company
    ↓
Open Company Context
    ↓
Review Technical Information
    ↓
Review Known Issues
    ↓
Review Relevant Links
    ↓
Return to Ticket
```

## Possible Company Context

- tenant information
- domains
- network notes
- supported applications
- environment notes
- escalation information
- KB links
- admin portals

---

# 14. Contact History Workflow

Related Feature:

- `FEAT-CONTACT-002`

## Goal

Understand whether the user has experienced related problems previously.

## Workflow

```text
Open Contact
    ↓
View Contact Details
    ↓
Load Related Tickets
    ↓
Filter Relevant History
    ↓
Open Previous Case if Needed
```

This may reveal:

- recurring issues
- previous resolutions
- device/user history
- known environmental patterns

---

# 15. Knowledge Search Workflow

Related Features:

- `FEAT-KB-003`
- `FEAT-SEARCH-001`

## Goal

Find relevant existing knowledge before reinventing troubleshooting steps.

## Workflow

```text
Enter Search Query
    ↓
Normalize Query
    ↓
Search Relevant Sources
    ↓
Rank Results
    ↓
Filter if Needed
    ↓
Open Result
    ↓
Use Knowledge
```

## Search Examples

```text
Outlook cached credentials
Teams camera not detected
VPN DNS issue
Exchange shared mailbox permissions
Intune device not compliant
```

## Implemented current-article search — Slice 015

Open Knowledge Base → enter plain text → Search (or press Enter) → select a lightweight match → read the authoritative current article. The search covers current article code, title, summary and Markdown body for DRAFT, PUBLISHED and ARCHIVED articles. Multiple letter/number tokens use implicit AND; case, Unicode text, punctuation, quotes, parentheses and operator-looking words are accepted as ordinary input rather than raw FTS syntax.

Search runs through the existing background runner. While it is pending, Search, Clear Search, list interaction, New Article, Edit Article and Version History are disabled. No matches show an explicit empty result without changing the query. A safe failure keeps the query for retry. Clear Search empties the query and restores the complete deterministic article list.

Selecting a result reuses the existing `get_article` path, so a changed article opens its latest persisted content and an article deleted after the search receives safe missing-article feedback. Search indexes current rows only; an earlier revision's obsolete text is not returned, while Version History remains separately available after opening a result.

---

# 16. Contextual KB Workflow

## Goal

Find knowledge related to the current ticket automatically or semi-automatically.

## Workflow

```text
Open Ticket
    ↓
Extract Ticket Context
    ↓
Search KB
    ↓
Rank Matches
    ↓
Display Related Knowledge
    ↓
Technician Selects Article
```

Relevant context may include:

- title
- description
- category
- technology
- company
- previous diagnostics

AI may assist ranking later, but local deterministic search should remain available.

---

# 17. Create Knowledge Article Workflow

## Implemented workflow — Slice 010

Open Knowledge Base → New Article → enter article code, title, optional summary and body → Create Article → select the saved article in the list → read its details. Empty databases show “No knowledge articles yet.” Both list and details reload from SQLite; articles remain available after reconstructing the application against the same database.

Code and title are trimmed and required. Summary is trimmed, with blank input stored as NULL. Whitespace-only body input is rejected; valid body text is preserved exactly by the service. Duplicate codes use the existing case-insensitive schema constraint and receive safe feedback. Failed creation preserves entered values; Cancel closes an idle form without saving, and repeated submission/cancellation is blocked during a write.

Creation stores a DRAFT article and its version-1 snapshot atomically. Category and published_at remain NULL. The read view shows code, title, status, current Version N, summary and plain, read-only Markdown source.

## Implemented draft editing — Slice 011

Open an existing DRAFT article → Edit Article → change title, summary or body → Save Revision → the same article remains selected with updated content and Version N+1 → reopen/read the saved revision. Article code and the editor's originally opened version are read-only. Title and summary are normalized as for creation; valid body content is preserved by the service.

The current article update and new revision snapshot commit together. Version 1 preserves the original content; subsequent snapshots preserve each new revision without changing earlier rows. Saving identical normalized content reports “No changes to save.” and leaves the current version and timestamp unchanged, only after the database confirms the expected version is still current.

If another editor saves first, the stale editor cannot overwrite it or add a snapshot. Its text remains available to copy, with clear feedback and Save disabled. Close the old editor, reopen the latest article, and start a new edit explicitly; a workspace refresh never replaces an open editor's original token. External changes to PUBLISHED/ARCHIVED status or deletion receive safe specific feedback with input retained. Generic persistence failures preserve input and permit retry. Cancel writes nothing; save runs in the background and blocks duplicate saves and closing during the write.

Restore/revert, deletion, publishing/archiving, category/tag assignment, article-to-article relationships, external links and AI remain deferred. The broader workflow below remains a product target.

## Implemented read-only version history — Slice 014

Slice 014 implements read-only version history: Knowledge Base → open an article → Version History → select a persisted revision → read its exact snapshot. History is available for loaded DRAFT, PUBLISHED and ARCHIVED articles with an available service and idle runner. The list is newest-first and excludes bodies; only the selected revision loads its summary/body. Historical version, title, summary, body, change summary, created by and stored timestamp come from knowledge_article_versions. Missing optional metadata displays Not provided. Status, category, updated_by and published_at are not snapshotted and are not presented as historical data. Article code is current immutable identity. Viewing does not change the current article, history rows, timestamps or ticket activity.

The current persisted revision is selected by version identity, with the newest returned revision as fallback. Select another row to load its exact historical content asynchronously. The body is read-only Markdown source and all metadata is plain text. Close or Escape dismisses the viewer while either the history list or selected revision read is pending; the read finishes safely without changing or reopening the dismissed viewer. All four combinations passed fresh MainWindow integration and native Windows input checks on 2026-09-09. Long metadata scrolls independently of the read-only body: the beginning and end of a 6,132-character historical summary were accessible at 900×620, with useful body space retained. Empty history and missing article/revision states receive safe feedback without substituting current content. Ticket Open Article continues to navigate to the current article; history requires a separate action.

Restore/revert, historical editing/deletion, comparison/apply and AI remain deferred. There is no historical status snapshot and no pagination for large revision or search-result lists.

## Implemented ticket/article linking — Slice 012

Saved tickets → open a ticket → Knowledge → Link Article → select an existing article → Link Article. The ticket shows the linked code, current title, status and version. Open Article switches to Knowledge Base, selects that article and reads its current details. Refresh, Reload ticket or returning through Saved tickets refreshes linked metadata after an article edit. Relationships survive application reconstruction against the same database.

An empty ticket shows “No knowledge articles linked.” The selector loads lightweight identities for DRAFT, PUBLISHED and ARCHIVED articles, excluding existing RELATED links. Cancel before saving writes nothing. Link runs in the background, blocks duplicate submission/closing during the write, and preserves selection on failure. Missing tickets/articles and duplicate links have clear feedback; an article disappearing before Open Article produces a safe missing-article message. A committed link followed by a failed list refresh remains explicitly reported as linked; use Refresh to recover.

Only RELATED is supported. Linking writes the relationship alone: no ticket updated_at, timeline, status or resolution change. Relationship-type changes, APPLIED/RESOLUTION_SOURCE, search/filtering, recommendations and ticket-driven article creation/editing are deferred.

## Implemented RELATED unlink — Slice 013

Saved tickets → open a ticket → Knowledge → select KB0001 → Unlink Article → confirm Unlink. The confirmation identifies KB0001 and explains that the ticket and knowledge article remain; Cancel, Enter with the default focus and Escape cancel without a service call or write, preserving selection. On success, only KB0001's RELATED association disappears. Other linked articles remain, and Open Article still opens the exact selected current article. KB0001 reappears in Link Article candidates and can be linked again with a fresh relationship timestamp.

Unlink reserves the writer before checking ticket, article and exact RELATED existence. A missing ticket takes precedence; otherwise a missing article is reported, then an already-removed relationship. Concurrent unlink produces one success and one safe not-linked result. Use Refresh to reconcile stale lists. Failed persistence preserves the displayed selection and permits retry; successful persistence followed by failed list refresh remains reported as “Article unlinked.” and Refresh retries only the read. Obsolete callbacks do not update another ticket.

ACTIVITY WRITE: NONE. Unlink changes only the chosen RELATED junction row, preserving the ticket, article, other relationships, ticket updated_at, notes, status history and timeline. There is no bulk unlink, other-type unlink, undo/history or parent deletion workflow.

Related Features:

- `FEAT-KB-001`
- `FEAT-KB-002`

## Goal

Preserve reusable technical knowledge.

## Workflow

```text
New KB Article
    ↓
Choose Article Type
    ↓
Enter Title
    ↓
Enter Procedure / Content
    ↓
Assign Category
    ↓
Assign Tags
    ↓
Add Related Scripts / Tickets
    ↓
Review
    ↓
Save as Draft or Active
```

---

# 18. Create KB from Resolved Ticket Workflow

## Goal

Convert solved support work into reusable knowledge.

## Workflow

```text
Resolve Ticket
    ↓
Identify Reusable Solution
    ↓
Select Create KB from Ticket
    ↓
Extract Relevant Information
    ↓
Remove Ticket-Specific Noise
    ↓
Structure Procedure
    ↓
Add Metadata
    ↓
Review
    ↓
Save KB Article
    ↓
Link Article to Ticket
```

This workflow supports knowledge reuse rather than repeated rediscovery.

---

# 19. Script Discovery Workflow

Related Features:

- `FEAT-SCRIPT-001`
- `FEAT-SCRIPT-004`

## Goal

Find an existing approved script.

## Workflow

```text
Open Script Library
    ↓
Search by Purpose / Technology
    ↓
Filter Results
    ↓
Select Script
    ↓
Review Description
    ↓
Review Risk / Privilege
    ↓
Review Parameters
```

Possible searches:

```text
DNS
Exchange mailbox
M365 license
Intune device
Windows network reset
```

---

# 20. Script Execution Workflow

Related Features:

- `FEAT-SCRIPT-005`
- `FEAT-SCRIPT-006`
- `FEAT-PS-001`

## Goal

Run an approved automation safely.

## Workflow

```text
Select Script
    ↓
Review Purpose
    ↓
Review Privilege Requirement
    ↓
Enter Parameters
    ↓
Validate Parameters
    ↓
Review Target
    ↓
Execute
    ↓
Capture Output
    ↓
Parse Structured Result
    ↓
Display Result
    ↓
Record Execution History
```

## Safety Boundary

The system should never treat arbitrary text from:

- AI
- ticket descriptions
- clipboard
- external APIs

as executable command input without validation.

---

# 21. Privileged Script Workflow

## Goal

Prevent accidental administrative action.

## Workflow

```text
Select Privileged Script
    ↓
Display Target
    ↓
Display Operation
    ↓
Display Required Privilege
    ↓
Validate Parameters
    ↓
Technician Confirms
    ↓
Execute Through Controlled Gateway
    ↓
Capture Result
```

F7Hub should not silently elevate privilege.

---

# 22. Diagnostic Workflow Selection

Related Feature:

- `FEAT-DIAG-001`

## Goal

Select an appropriate diagnostic procedure.

## Workflow

```text
Open Ticket
    ↓
Identify Issue Category
    ↓
Display Matching Diagnostic Workflows
    ↓
Technician Selects Workflow
    ↓
Start Diagnostic Session
```

Possible diagnostic workflows:

- Outlook cannot open
- Microsoft 365 authentication
- MFA failure
- VPN connectivity
- DNS resolution
- Teams camera
- OneDrive synchronization
- printer failure
- Windows performance
- Intune compliance

---

# 23. Guided Diagnostic Workflow

Related Features:

- `FEAT-DIAG-001`
- `FEAT-DIAG-002`
- `FEAT-DIAG-003`

## Goal

Guide the technician through structured troubleshooting.

## Workflow

```text
Start Diagnostic Session
    ↓
Load Workflow
    ↓
Display Current Step
    ↓
Collect Technician Input
    ↓
Evaluate Condition
    ↓
Determine Next Step
    ↓
Continue Until Outcome
```

Example:

```text
Can the user sign in?
│
├── Yes
│   ↓
│ Check application-specific issue
│
└── No
    ↓
Check authentication / account state
```

---

# 24. Automated Diagnostic Step Workflow

Related Feature:

- `FEAT-DIAG-004`

## Goal

Collect technical evidence automatically.

## Workflow

```text
Diagnostic Step Requires Script
    ↓
Load Approved Script Reference
    ↓
Build Validated Parameters
    ↓
Execute PowerShell
    ↓
Receive Structured Result
    ↓
Store Result
    ↓
Evaluate Result
    ↓
Continue Workflow
```

---

# 25. Diagnostic Completion Workflow

Related Feature:

- `FEAT-DIAG-005`

## Workflow

```text
Final Diagnostic Step
    ↓
Evaluate Session
    ↓
Produce Outcome
    ↓
Suggest Resolution / Escalation
    ↓
Save Session
    ↓
Link to Ticket
    ↓
Add Timeline Entry
```

---

# 26. Diagnostic Failure Workflow

## Goal

Handle failed automation without losing troubleshooting progress.

## Workflow

```text
Diagnostic Script Fails
    ↓
Capture Error
    ↓
Preserve Existing Session
    ↓
Display Failure
    ↓
Offer Manual Path / Retry if Safe
    ↓
Continue or Escalate
```

A failed diagnostic script should not erase previous answers.

---

# 27. Clipboard Snippet Workflow

Related Feature:

- `FEAT-CLIP-002`

## Goal

Reuse frequently typed support text.

## Workflow

```text
Open Clipboard / Snippets
    ↓
Search Snippet
    ↓
Select Snippet
    ↓
Preview
    ↓
Copy or Insert
```

Possible snippets:

- customer greetings
- escalation text
- troubleshooting steps
- standard responses
- ticket-note templates

---

# 28. Clipboard Capture Workflow

Related Feature:

- `FEAT-CLIP-001`

## Workflow

```text
Copy Text
    ↓
Clipboard Handler Receives Content
    ↓
Check Persistence Rules
    ↓
Check Exclusion / Sensitivity Rules
    ↓
Store if Allowed
    ↓
Make Available in History
```

Sensitive clipboard content must not automatically be assumed safe to persist.

---

# 29. Clipboard Transformation Workflow

Related Feature:

- `FEAT-CLIP-003`

## Workflow

```text
Select Clipboard Content
    ↓
Choose Transformation
    ↓
Transform
    ↓
Preview
    ↓
Copy / Insert
```

Examples:

- clean whitespace
- remove formatting
- extract URLs
- extract email addresses
- extract IP addresses
- format ticket notes

---

# 30. AutoHotkey Quick Action Workflow

Related Features:

- `FEAT-AHK-001`
- `FEAT-AHK-003`

## Goal

Trigger common actions without navigating manually.

## Workflow

```text
Press Hotkey
    ↓
AHK Detects Shortcut
    ↓
Resolve Registered Action
    ↓
Launch / Focus / Send Request
    ↓
F7Hub or External Tool Responds
```

AHK should remain a lightweight automation layer.

---

# 31. Command Palette Workflow

Related Feature:

- `FEAT-APP-003`

## Goal

Execute common F7Hub actions from the keyboard.

## Workflow

```text
Open Command Palette
    ↓
Type Search Text
    ↓
Filter Registered Commands
    ↓
Select Command
    ↓
Validate Availability
    ↓
Execute Registered Action
```

Examples:

```text
Open ticket INC-10254
Search KB Outlook
Run DNS diagnostics
Switch workspace
Open Exchange Admin Center
```

---

# 32. Universal Search Workflow

Related Feature:

- `FEAT-SEARCH-001`

## Workflow

```text
Open Search
    ↓
Enter Query
    ↓
Normalize Query
    ↓
Search Providers
    ↓
Combine Results
    ↓
Rank
    ↓
Display Unified Results
    ↓
Open Selected Result
```

Supported result types may include:

- tickets
- companies
- contacts
- KB
- scripts
- prompts
- clipboard
- commands

---

# 33. Microsoft Admin Portal Workflow

Related Feature:

- `FEAT-M365-001`

## Goal

Open the appropriate Microsoft administration environment quickly.

## Workflow

```text
Open Microsoft Administration
    ↓
Select Service
    ↓
Launch Approved Portal
```

Possible targets:

- Microsoft 365 Admin
- Entra
- Exchange
- Intune
- Defender
- Teams
- SharePoint

---

# 34. Microsoft Graph Read Workflow

Related Feature:

- `FEAT-M365-002`

## Goal

Retrieve supported Microsoft cloud information.

## Workflow

```text
Technician Requests Information
    ↓
Validate Request
    ↓
Check Authentication
    ↓
Call Microsoft Graph Gateway
    ↓
Receive Response
    ↓
Validate / Parse
    ↓
Display Result
```

External failures should not corrupt local data.

---

# 35. Microsoft Administrative Change Workflow

## Goal

Perform an approved cloud administrative action safely.

## Workflow

```text
Select Administrative Action
    ↓
Identify Target
    ↓
Enter Parameters
    ↓
Validate
    ↓
Display Impact
    ↓
Check Privilege
    ↓
Technician Confirms
    ↓
Execute
    ↓
Capture Result
    ↓
Record Appropriate Audit Information
```

Examples may eventually include:

- account actions
- mailbox operations
- group membership
- license operations
- device diagnostics

Each operation requires separate security and implementation review.

---

# 36. AI Ticket Summary Workflow

Related Feature:

- `FEAT-AI-001`

## Workflow

```text
Open Ticket
    ↓
Select Summarize
    ↓
Build Approved Context
    ↓
Apply Privacy Rules
    ↓
Send to AI Provider
    ↓
Receive Summary
    ↓
Display as Suggestion
    ↓
Technician Reviews
```

AI output must not silently overwrite ticket information.

---

# 37. AI Troubleshooting Workflow

Related Feature:

- `FEAT-AI-002`

## Workflow

```text
Ticket / Diagnostic Context
    ↓
Technician Requests Assistance
    ↓
Build Context
    ↓
Retrieve Relevant KB if Available
    ↓
Send Approved Context
    ↓
Receive Suggestions
    ↓
Display Hypotheses / Next Steps
    ↓
Technician Decides
```

AI remains advisory.

---

# 38. AI Note Improvement Workflow

Related Feature:

- `FEAT-AI-003`

## Workflow

```text
Technician Writes Rough Note
    ↓
Select Improve / Structure
    ↓
AI Generates Draft
    ↓
Technician Reviews
    ↓
Edit if Required
    ↓
Save
```

The original ticket data should not be overwritten without explicit action.

---

# 39. AI Script Assistance Workflow

Related Feature:

- `FEAT-AI-004`

## Workflow

```text
Select Script
    ↓
Ask AI to Explain / Review
    ↓
AI Produces Analysis
    ↓
Technician Reviews
    ↓
No Automatic Execution
```

If AI suggests modifications, they remain untrusted until reviewed and tested.

---

# 40. Prompt Library Workflow

Related Features:

- `FEAT-PROMPT-001`
- `FEAT-PROMPT-002`
- `FEAT-PROMPT-003`

## Workflow

```text
Open Prompt Library
    ↓
Search Prompt
    ↓
Select Template
    ↓
Populate Variables
    ↓
Preview Final Prompt
    ↓
Review Context
    ↓
Submit if Desired
```

---

# 41. Workspace Switching Workflow

Related Feature:

- `FEAT-WORKSPACE-002`

## Goal

Reconfigure the interface for different support tasks.

## Workflow

```text
Open Workspace Selector
    ↓
Choose Profile
    ↓
Save Current State if Needed
    ↓
Load Selected Layout
    ↓
Restore Panels
```

Potential workspaces:

- Helpdesk
- Microsoft 365
- Networking
- Automation
- Knowledge Authoring
- AI

---

# 42. Save Workspace Workflow

## Workflow

```text
Arrange Panels
    ↓
Select Save Workspace
    ↓
Name / Update Profile
    ↓
Persist Layout
    ↓
Confirm Save
```

Invalid layouts should be recoverable.

---

# 43. Reporting Workflow

Related Features:

- `FEAT-REPORT-001`
- `FEAT-REPORT-002`
- `FEAT-REPORT-003`

## Workflow

```text
Open Reports
    ↓
Select Report Type
    ↓
Choose Filters
    ↓
Generate Structured Report
    ↓
Review
    ↓
Export if Needed
```

Possible report types:

- diagnostic session
- script execution
- ticket activity
- troubleshooting summary

---

# 44. Settings Workflow

Related Feature:

- `FEAT-SETTINGS-001`

## Workflow

```text
Open Settings
    ↓
Select Category
    ↓
Modify Setting
    ↓
Validate
    ↓
Save
    ↓
Apply Immediately or on Restart
```

Sensitive credentials must not be treated as ordinary plaintext settings.

---

# 45. Integration Configuration Workflow

## Workflow

```text
Open Settings
    ↓
Select Integration
    ↓
Configure Required Information
    ↓
Authenticate if Required
    ↓
Test Connection
    ↓
Display Status
    ↓
Save Non-Secret Configuration
```

Possible integration states:

```text
NOT_CONFIGURED
AVAILABLE
AUTHENTICATING
CONNECTED
DEGRADED
UNAVAILABLE
ERROR
```

---

# 46. Plugin Enable Workflow

Related Features:

- `FEAT-PLUGIN-001`
- `FEAT-PLUGIN-002`
- `FEAT-PLUGIN-003`

## Workflow

```text
Discover Plugin
    ↓
Validate Metadata
    ↓
Check Compatibility
    ↓
Review Permissions
    ↓
Enable Plugin
    ↓
Initialize
    ↓
Expose Approved Extension Points
```

A plugin must not receive unrestricted access to core F7Hub internals.

---

# 47. Plugin Failure Workflow

## Workflow

```text
Plugin Error
    ↓
Capture Error
    ↓
Disable / Isolate Plugin if Required
    ↓
Log Failure
    ↓
Notify Technician
    ↓
Continue Core Application
```

---

# 48. Search-to-Action Workflow

One important F7Hub design pattern is:

```text
Search
   ↓
Find
   ↓
Open
   ↓
Act
```

Examples:

```text
Search ticket
→ Open ticket

Search KB
→ Open procedure

Search script
→ Review / Execute

Search company
→ Open company context

Search command
→ Execute registered application action
```

Search should be actionable, not merely a list of results.

---

# 49. Ticket-to-Diagnostic-to-KB Workflow

This is one of the most important integrated workflows in F7Hub.

```text
Open Ticket
    ↓
Understand Context
    ↓
Search KB
    ↓
Start Diagnostic Workflow
    ↓
Collect Answers
    ↓
Run Approved Diagnostics
    ↓
Evaluate Results
    ↓
Find Relevant KB
    ↓
Perform Resolution
    ↓
Document Ticket
```

---

# 50. Ticket-to-Escalation Workflow

```text
Open Ticket
    ↓
Troubleshoot
    ↓
Run Diagnostics
    ↓
Resolution Unsuccessful
    ↓
Compile Evidence
    ↓
Generate Escalation Summary
    ↓
Technician Reviews
    ↓
Escalate
```

---

# 51. Ticket-to-Knowledge Workflow

```text
Resolve Ticket
    ↓
Identify Reusable Information
    ↓
Create KB Draft
    ↓
Generalize Procedure
    ↓
Review
    ↓
Publish / Activate
    ↓
Future Tickets Can Retrieve It
```

This creates a continuous knowledge loop.

---

# 52. Knowledge Improvement Loop

```text
Ticket
  ↓
Troubleshooting
  ↓
Resolution
  ↓
Knowledge Article
  ↓
Future Search
  ↓
Faster Resolution
  ↓
Updated Knowledge
```

This loop is central to the long-term value of F7Hub.

---

# 53. Failure Handling Pattern

Most workflows should follow a consistent failure model:

```text
Operation
    ↓
Failure
    ↓
Capture Technical Error
    ↓
Preserve User State
    ↓
Display Understandable Message
    ↓
Offer Safe Recovery / Retry
```

Failures should not silently destroy technician work.

---

# 54. Cancellation Pattern

For cancellable long-running operations:

```text
Operation Running
    ↓
Technician Requests Cancel
    ↓
Check Whether Safe to Cancel
    │
    ├── Yes → Cancel → Report Cancelled
    │
    └── No  → Explain Operation Must Complete
```

The GUI must not claim an action was cancelled if the underlying administrative operation continued.

---

# 55. Offline Workflow

F7Hub should remain useful without cloud access.

```text
Internet / Cloud Unavailable
    ↓
Continue Local Features
    │
    ├── Tickets
    ├── KB
    ├── Search
    ├── Scripts
    ├── Clipboard
    ├── Prompts
    └── Settings
```

Connected features should clearly indicate unavailable status.

---

# 56. Application Shutdown Workflow

```text
Close F7Hub
    ↓
Check Running Operations
    ↓
Handle Safe Cancellation
    ↓
Save Workspace State
    ↓
Complete / Roll Back Pending DB Work
    ↓
Close Database
    ↓
Flush Logs
    ↓
Stop Managed Child Processes
    ↓
Exit
```

Shutdown must preserve data integrity.

---

# 57. Keyboard-First Workflow

Frequently used actions should eventually be reachable without extensive mouse navigation.

Examples:

```text
Open Command Palette
Search
Open Ticket
Save
Switch Workspace
Run Diagnostic
Open KB
```

Exact shortcuts belong in `05_GUI.md`.

---

# 58. Workflow Composition

F7Hub workflows should be composable.

Example:

```text
Ticket Workflow
    │
    ├── Company Workflow
    ├── Contact Workflow
    ├── Search Workflow
    ├── Knowledge Workflow
    ├── Diagnostic Workflow
    ├── Script Workflow
    ├── AI Workflow
    └── Resolution Workflow
```

Modules should cooperate through shared context rather than duplicate the same data.

---

# 59. Workflow Traceability

User workflows should trace to features and requirements.

Preferred chain:

```text
Requirement
    ↓
Feature
    ↓
Workflow
    ↓
GUI
    ↓
Architecture
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
    ↓
Guided Diagnostic Workflow
    ↓
05_GUI.md
    ↓
06_SystemArchitecture.md
    ↓
Implementation
    ↓
Tests
```

---

# 60. Workflow Acceptance Rule

A workflow is not complete merely because individual buttons exist.

A completed workflow should normally satisfy:

```text
[ ] Entry point exists
[ ] Required data can be loaded
[ ] User can complete primary path
[ ] Input is validated
[ ] Failure path exists
[ ] User state is preserved appropriately
[ ] Database state remains valid
[ ] Security boundaries are respected
[ ] Result is clearly communicated
[ ] Tests cover critical behavior
```

---

# 61. High-Priority End-to-End Workflows

The following workflows should receive early end-to-end validation:

1. application startup
2. create ticket
3. open ticket
4. add ticket note
5. search tickets
6. create KB article
7. search KB
8. find script
9. execute safe PowerShell script
10. run diagnostic workflow
11. record diagnostic session
12. resolve ticket

These prove that the core architecture works across multiple layers.

---

# 62. Future Workflow Candidates

Later workflows may include:

- HaloPSA synchronization
- NinjaOne device context
- Microsoft Graph administration
- Intune diagnostics
- Exchange administration
- Defender investigation
- plugin installation
- AI-assisted knowledge creation
- multi-technician collaboration
- advanced reporting
- cloud synchronization

These should not be implemented until their requirements and architecture are approved.

---

# 63. Workflow Anti-Patterns

Avoid:

## Duplicate Data Entry

Technician repeatedly enters information already available in active ticket context.

---

## Hidden Automation

Administrative action occurs without technician understanding what is being executed.

---

## Dead-End Errors

Workflow fails and discards technician progress.

---

## AI-Controlled Administration

AI independently decides and executes privileged operations.

---

## Workflow Explosion

Every minor variation becomes a completely separate workflow when existing workflows can be reused or parameterized.

---

## GUI-Defined Business Rules

Important workflow rules exist only inside button handlers.

---

# 64. Workflow Design Rule

When adding a new workflow:

```text
Identify User Goal
    ↓
Identify Existing Features
    ↓
Define Entry Point
    ↓
Define Required Context
    ↓
Define Happy Path
    ↓
Define Decision Points
    ↓
Define Failure Paths
    ↓
Define Result
    ↓
Map Requirements
    ↓
Define Tests
```

---

# 65. Core F7Hub Technician Workflow

The central F7Hub experience is:

```text
                Incoming Support Issue
                         │
                         ▼
                    Open Ticket
                         │
                         ▼
                 Understand Context
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
       Search Knowledge       Review History
              │                     │
              └──────────┬──────────┘
                         ▼
                   Troubleshoot
                         │
                         ▼
                 Run Diagnostics
                         │
                         ▼
               Use Approved Scripts
                         │
                         ▼
                 Evaluate Results
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
           Resolve               Escalate
              │                     │
              └──────────┬──────────┘
                         ▼
                     Document
                         │
                         ▼
               Preserve Knowledge
```

---

# 66. Final Workflow Principles

F7Hub workflows should:

- start from the technician's real task
- preserve active context
- surface relevant knowledge
- reuse existing automation
- provide deterministic diagnostic guidance
- allow safe PowerShell execution
- record useful history
- support escalation
- integrate AI as assistance
- remain usable when cloud services fail
- reduce duplicate technician effort

The core interaction model is:

> Understand → Search → Troubleshoot → Diagnose → Automate → Resolve → Document → Reuse

F7Hub should make each transition easier without hiding the technical work from the technician.
