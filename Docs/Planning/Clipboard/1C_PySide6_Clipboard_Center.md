# F7Hub Phase 1C
# PySide6 Clipboard Center Architecture Planning Instructions
Existing MainWindow/workspace/navigation conventions; reusable Qt components; Clipboard Center shell integration; internal views; query semantics; search/filter model; list/read models; table columns; pagination; Inspector architecture; Entities, Tags, Capture History, Relationships, Retention/Privacy and Actions tabs; deep links; keyboard/accessibility; async loading; stale-result handling; error/empty states; large-dataset strategy; responsive layout; future Mochi-sidebar coexistence; vertical-slice implementation decomposition.

## Dependency Gate

Required approved architecture:

- Phase 0A: APPROVED
- Phase 0B: APPROVED
- Phase 0C: APPROVED
- Phase 0D: APPROVED
- Phase 1A: APPROVED
- Phase 1B: APPROVED

If any required dependency is not approved:

RESULT = BLOCKED

Do not compensate by inventing missing architecture locally.


## GUI Ownership

Clipboard Center owns:

- Clipboard navigation
- Clipboard list presentation
- Clipboard item inspection
- Clipboard filters
- Clipboard contextual actions presentation

Clipboard Center does NOT own:

- Tag Catalog
- Ticket business logic
- Diagnostic execution
- Knowledge Base persistence
- Mochi reasoning
- PowerShell invocation
- Analytics calculations
- AHK capture

## Must remain visible

GUI
 ↓
Application Service
 ↓
Domain
 ↓
Repository
 ↓
SQLite


## Mode

`@ARCHITECT @PLAN`

GUI architecture and interaction planning only.

Do not implement production code.

Do not create PySide6 classes.

Do not create `.ui` files.

Do not modify `MainWindow`.

Do not create SQLite migrations.

Do not modify repositories or services.

Do not modify AHK integration.

Do not implement IPC.

Do not implement Diagnostics.

Do not implement Statistical Analytics.

Do not implement Mochi.

Do not perform unrelated GUI redesign.

---

# 1. Objective

Design the complete PySide6 Clipboard Center architecture for F7Hub.

The Clipboard Center must become the primary persistent operational interface for captured Clipboard intelligence.

It must allow the technician to:

```text
find
filter
inspect
understand
tag
save
pin
link
search
launch approved actions
manage retention
review privacy state
```

for Clipboard Items already processed by the Clipboard domain.

This phase must define the complete GUI architecture without reimplementing Clipboard business rules inside PySide6.

---

# 2. Required Foundation Inputs

Before planning the GUI, read the approved outputs from:

```text
Phase 0A
Master Foundation Architecture

Phase 0B
Global JSON / Interoperability Contract

Phase 0C
Classification / Taxonomy / Entities / Tags

Phase 0D
Settings / Configuration Architecture

Phase 1A
Clipboard Domain & Data Lifecycle

Phase 1B
AHK ↔ Python Clipboard Capture / IPC / Quick HUD
```

These plans establish:

```text
domain semantics
contract semantics
taxonomy
retention
privacy
settings
AHK responsibilities
transport boundary
```

Phase 1C must not redefine them silently.

---

# 3. Mandatory Existing GUI Inspection

Inspect the current PySide6 F7Hub implementation before recommending the Clipboard GUI.

At minimum inspect:

```text
MainWindow
navigation
toolbars
menus
workspace layout
ticket workspace
Knowledge Base workspace
dialog conventions
table models
proxy models
selection behavior
async/background-loading patterns
error presentation
retry behavior
empty states
keyboard shortcuts
status bar
theme
icons
spacing
font usage
window geometry
DPI handling
testing conventions
```

Identify reusable components.

Use:

```text
SEARCH
  ↓
IDENTIFY
  ↓
REUSE / EXTEND
  ↓
CREATE ONLY IF NECESSARY
```

Do not introduce an independent Clipboard visual framework if F7Hub already has usable patterns.

---

# 4. Current State Classification

For every relevant GUI capability classify it as:

```text
FACT
ASSUMPTION
INFERENCE
RECOMMENDATION
NOT VERIFIED
```

Do not invent current widgets, services, models, or navigation APIs.

---

# 5. Clipboard Center Responsibility

Clipboard Center should answer:

```text
What have I captured?

What kind of information is it?

What Entities were detected?

What Tags apply?

Where did it come from?

How often was it captured?

What is it linked to?

How long will it remain?

What safe actions are available?
```

---

# 6. Clipboard Center Must Not Become

Clipboard Center must not become:

```text
a second Statistical Analytics dashboard
a PowerShell console
a ticket editor
a Knowledge Base editor
a diagnostic implementation layer
a Mochi conversation engine
an AHK configuration screen
```

It may navigate to or invoke those systems through approved services.

---

# 7. Main Workspace Concept

Preferred high-level composition:

```text
┌──────────────────────────────────────────────────────────────┐
│ Toolbar                                                      │
├───────────────┬─────────────────────────────┬────────────────┤
│ Navigation    │ Clipboard Items             │ Inspector      │
│ / Views       │                             │                │
│               │ Search + Filters            │ Summary        │
│ Recent        │                             │ Entities       │
│ Saved         │ Table                       │ Tags           │
│ Pinned        │                             │ History        │
│ URLs          │                             │ Relationships  │
│ Commands      │                             │ Retention      │
│ Errors        │                             │ Actions        │
│ Networking    │                             │                │
├───────────────┴─────────────────────────────┴────────────────┤
│ Status / result summary                                      │
└──────────────────────────────────────────────────────────────┘
```

The plan must validate this against current F7Hub GUI architecture.

---

# 8. Three-Pane Model

Evaluate a three-pane model:

```text
LEFT
Navigation / saved views

CENTER
Clipboard operational list

RIGHT
Selected-item inspector
```

Benefits:

```text
high information density
fast keyboard workflow
persistent context
minimal dialog hopping
consistent technician workflow
```

---

# 9. Responsive Collapse

The design must support smaller application widths.

Potential behavior:

```text
Wide
Left + Center + Inspector

Medium
Center + Inspector
Navigation collapsible

Narrow
Center
Inspector opens drawer/panel
```

Exact breakpoints must follow current F7Hub resizing conventions.

---

# 10. Navigation Views

Proposed primary views:

```text
Recent
Saved
Pinned
URLs
Commands
PowerShell
Errors & Logs
Networking
Ticket Evidence
Diagnostic Evidence
Mixed Content
```

These are primarily filtered views.

They must not represent duplicate storage tables.

---

# 11. Recent

Default operational view.

Potential semantics:

```text
active Clipboard Items
sorted by most recent capture
```

Exact retention and state definitions come from Phase 1A.

---

# 12. Saved

Shows items explicitly preserved by the user.

Do not interpret every Ticket-linked item as manually Saved unless Phase 1A defines that behavior.

---

# 13. Pinned

Shows items with:

```text
is_pinned = true
```

or the approved equivalent.

Pinning is a presentation/importance dimension, not necessarily a separate persistence model.

---

# 14. URLs

Filter based on canonical Kind / Entity taxonomy.

Potential:

```text
primary_kind = url
OR
contains URL entity
```

The plan must decide exact query semantics.

---

# 15. Commands

Potential filter for:

```text
PowerShell commands
CMD commands
other recognized command lines
```

Do not conflate Commands and approved Scripts.

---

# 16. PowerShell View

Potential:

```text
PowerShell Kind
OR
PowerShell Tag
OR
PowerShell-specific Entities
```

Use canonical taxonomy rather than raw string matching.

---

# 17. Errors & Logs

Potential:

```text
error Kind
log Kind
error-code Entity
event Entity
```

Exact semantics must be documented.

---

# 18. Networking

Potential:

```text
Networking Tag
OR
network Entity Types
```

Examples:

```text
IPv4
IPv6
CIDR
MAC
FQDN
domain
port
```

---

# 19. Ticket Evidence

Shows Clipboard Items with explicit Ticket relationships.

Do not infer evidence merely because text contains a ticket number.

---

# 20. Diagnostic Evidence

Shows Clipboard Items explicitly related to Diagnostic Sessions.

---

# 21. Mixed Content

Items whose primary Kind is:

```text
mixed_text
```

or approved equivalent.

Useful for complex copied troubleshooting notes.

---

# 22. Smart Filters

Consider secondary smart filters:

```text
Sensitive
Large Items
Unlinked
This Week
Recently Used
Duplicate-heavy
```

Only include filters with operational value.

Avoid visual clutter.

---

# 23. Navigation Counts

Evaluate optional counts:

```text
Recent            836
Pinned             14
URLs               92
Ticket Evidence    47
```

Counts must be efficient.

Do not execute expensive full-table counts every repaint.

---

# 24. Navigation Selection

Selecting a view should update:

```text
filter state
table query
status text
```

without losing unrelated selected context unnecessarily.

---

# 25. Toolbar

Recommended top-level actions:

```text
Capture
Save
Pin
Delete
Attach to Ticket
Search KB
Run Diagnostic
Ask Mochi
```

Do not expose actions that are not implemented by their owning subsystem.

Unavailable future actions should not appear as fake working controls.

---

# 26. Capture Button

Potential behavior:

```text
Process current Windows Clipboard
```

through the same Clipboard application service as AHK capture.

Do not duplicate processing logic inside PySide6.

---

# 27. Save

Explicitly preserves the selected Clipboard Item according to Phase 1A retention semantics.

---

# 28. Pin

Toggles selected item's pinned state.

The plan should define:

```text
single-selection behavior
multi-selection behavior
visual feedback
```

---

# 29. Delete

Delete semantics must follow Phase 1A.

The GUI must clearly differentiate:

```text
remove temporary item
unlink evidence
delete preserved item
```

when behavior differs.

---

# 30. Attach to Ticket

Must invoke the approved Ticket relationship workflow.

The GUI must not write relationship rows directly.

---

# 31. Search KB

Should derive a meaningful search query from:

```text
selected item
selected entity
selected error
selected tags
```

depending on context.

---

# 32. Run Diagnostic

Must route through DiagnosticService.

Clipboard Center only supplies validated context.

---

# 33. Ask Mochi

Future behavior should route selected-item context through the approved ContextService.

The Clipboard Center should not build its own conversational prompt.

---

# 34. Toolbar Context Sensitivity

Actions should enable/disable according to selection.

Example:

```text
Nothing selected
Save              disabled
Pin               disabled
Attach to Ticket  disabled

IPv4 selected
Run Diagnostic    enabled
Search KB         enabled
```

Disabled states should include useful tooltip explanations where appropriate.

---

# 35. Global Search Field

Clipboard Center should have fast search.

Potential search domains:

```text
content
preview
Tags
Entities
source application
relationships
```

Search architecture should reuse existing F7Hub search conventions where possible.

---

# 36. Search Semantics

Evaluate:

```text
free-text search
structured filters
combined search
```

Example:

```text
0x80070005
```

may match:

```text
content
Error Code Entity
```

---

# 37. Search Should Not Replace Structured Filters

Use:

```text
text search
+
Type filter
+
Application filter
+
Sensitivity filter
+
Relationship filter
+
Date filter
```

rather than forcing everything into one query language initially.

---

# 38. Filter Bar

Recommended filters:

```text
Kind / Type
Source Application
Sensitivity
Relationship
Date Range
Tag
Entity Type
```

Avoid exposing all advanced filters simultaneously if space becomes crowded.

---

# 39. Filter Chips

Applied filters may appear as removable chips:

```text
[PowerShell ×]
[Last 7 Days ×]
[Unlinked ×]
```

Evaluate consistency with existing F7Hub UI.

---

# 40. Clear Filters

Provide one clear action:

```text
Clear Filters
```

to return to current navigation view defaults.

---

# 41. Filter Persistence

Decide whether filter selections survive:

```text
view changes
module changes
application restart
```

Recommended initial behavior:

```text
session-local
```

unless Settings architecture indicates otherwise.

---

# 42. Center Table

Clipboard Center's operational table should be optimized for scanning.

Candidate columns:

```text
Time
Preview
Kind
Entities
Tags
Source
Seen
Linked
Pinned
```

The plan must recommend final default columns.

---

# 43. Time Column

Likely:

```text
last_seen_at
```

for the Recent view.

Tooltip/detail may show:

```text
first_seen
last_seen
```

---

# 44. Preview Column

Display a short one-line or two-line preview.

Must:

```text
truncate safely
support Unicode
avoid exposing secret content
```

Sensitive items may show:

```text
[Redacted]
```

instead.

---

# 45. Kind Column

Show canonical display name:

```text
PowerShell Command
URL
Mixed Text
Error Message
```

not raw internal key unless developer mode.

---

# 46. Entities Column

Do not render all Entities inline.

Potential:

```text
6
```

or:

```text
IPv4 +5
```

with detailed inspection in Inspector.

---

# 47. Tags Column

Potentially show:

```text
DNS · PowerShell +2
```

or small chips.

Avoid excessively widening the table.

---

# 48. Source Column

Potential:

```text
PowerShell
Outlook
Edge
Notepad
```

Source display must respect privacy decisions from Phase 1B.

---

# 49. Seen Column

Represents capture frequency.

Example:

```text
8×
```

If count is derived rather than persisted, model design must remain efficient.

---

# 50. Linked Column

Potential summary:

```text
Ticket
Diagnostic
KB
2 links
```

Avoid listing full relationships in the table.

---

# 51. Pinned Column

Use a compact icon or boolean marker.

Must be keyboard-accessible.

---

# 52. Hidden / Optional Columns

Potential optional columns:

```text
Sensitivity
Size
First Seen
Last Seen
Retention
```

Do not make the default table too wide.

---

# 53. Column Configuration

Evaluate whether users should be able to:

```text
show/hide columns
resize columns
reorder columns
```

If existing F7Hub tables support this, reuse it.

Otherwise defer customizable layout until needed.

---

# 54. Table Model Architecture

Prefer Qt model/view architecture.

Potential:

```text
QTableView
+
custom QAbstractTableModel
+
QSortFilterProxyModel
```

or existing project equivalents.

Do not populate large datasets using ad-hoc widget-per-row approaches.

---

# 55. Repository Pagination

If Clipboard history may become large, avoid loading all items at startup.

Evaluate:

```text
database pagination
incremental loading
query limits
```

rather than only client-side filtering.

---

# 56. Sorting

Common sorting:

```text
Last Seen
First Seen
Kind
Source
Capture Count
```

Default:

```text
Last Seen descending
```

for Recent.

---

# 57. Stable Selection

When rows refresh, preserve selection by:

```text
clipboard_item_id
```

not row number.

---

# 58. Refresh Behavior

After:

```text
new capture
tag update
pin
link
retention change
```

refresh affected data without unnecessarily resetting:

```text
scroll
filters
selection
inspector tab
```

---

# 59. Auto-Refresh

If AHK captures new content while Clipboard Center is open, evaluate:

```text
automatic update
```

through existing application signals/events.

Do not use aggressive polling.

---

# 60. New Item Visibility

If current view includes the new item:

```text
insert/update row
```

without forcibly stealing current selection.

Potential subtle indication:

```text
New item captured
```

---

# 61. Table Row Selection

Recommended:

```text
single selection
```

for initial Clipboard inspection.

Evaluate whether multi-select is genuinely needed for:

```text
bulk delete
bulk tag
bulk save
```

Do not add complexity prematurely.

---

# 62. Multi-Select

Likely defer until:

```text
bulk workflows
```

have concrete requirements.

---

# 63. Double Click

Potential behavior:

```text
open/focus Inspector
```

or:

```text
open detailed item dialog
```

Prefer keeping inspection in the right panel.

---

# 64. Enter Key

With row selected:

```text
Enter
→ focus/open Inspector
```

or primary item action.

Define consistently.

---

# 65. Context Menu

Right-click row may expose:

```text
Save
Pin
Attach to Ticket
Run Diagnostic
Search KB
Copy
Delete
```

Only show valid actions.

Do not duplicate every toolbar action mechanically if menu becomes too large.

---

# 66. Inspector Purpose

The Inspector provides full operational details for one selected Clipboard Item.

Recommended tabs:

```text
Summary
Entities
Tags
Capture History
Relationships
Retention & Privacy
Actions
```

Potential optional:

```text
Raw
```

only if needed.

---

# 67. Summary Tab

Show:

```text
content preview
primary Kind
source
first seen
last seen
capture count
size
sensitivity
retention
saved/pinned state
```

Avoid overwhelming detail.

---

# 68. Full Content

The Summary or dedicated content area should allow:

```text
view full text
select text
copy text
```

subject to privacy restrictions.

Do not make raw content editable by default.

---

# 69. Content Viewer

Prefer:

```text
read-only text widget
```

with:

```text
monospace option for technical content
line wrapping
find within content
```

where justified.

---

# 70. Syntax Highlighting

Potential future highlighting for:

```text
JSON
PowerShell
logs
```

but do not require it for initial implementation.

Entity highlighting is more important.

---

# 71. Entity Highlighting

The content viewer should eventually highlight detected Entity ranges.

Example:

```text
john@contoso.com
PC-1042
10.0.0.87
0x80070005
```

Use offsets defined in Phase 1A.

---

# 72. Overlapping Entities

The GUI architecture must anticipate overlapping Entity occurrences.

Example:

```text
https://10.0.0.87:443
```

contains:

```text
URL
IPv4
Port
```

Do not assume every character can have only one Entity classification.

---

# 73. Entity Highlight Interaction

Clicking highlighted Entity could:

```text
select Entity in Entities tab
```

or open context actions.

Avoid hidden hover-only functionality.

---

# 74. Entities Tab

Display structured Entity occurrences.

Candidate columns/cards:

```text
Type
Raw Value
Normalized Value
Confidence
Provenance
Occurrence Count
```

Do not expose internal metadata unnecessarily.

---

# 75. Entity Actions

Context-sensitive actions:

### IPv4

```text
Ping
DNS Lookup
Search Tickets
Run Network Diagnostic
```

### Error Code

```text
Search Tickets
Search KB
Run relevant diagnostic
```

### Ticket ID

```text
Open Ticket
Link Item
```

### PowerShell Command

```text
Search Script Registry
Save Snippet
Search KB
```

---

# 76. Entities Are Not Editable Taxonomy

Users may correct a detection later if designed, but the Entities tab should not become Entity Type administration.

Entity taxonomy belongs to global architecture/Settings read-only management if supported.

---

# 77. Tags Tab

Show assigned Tags with provenance.

Example:

```text
PowerShell
RULE

Networking
RULE

Needs Review
USER
```

Potential visual distinction:

```text
manual
automatic
suggested
```

without relying only on color.

---

# 78. Add Tag

Reuse the global Tag Selector architecture from Phase 0C.

Potential:

```text
[PowerShell ×]
[DNS ×]

+ Add Tag
```

---

# 79. Suggested Tags

Potential section:

```text
Suggested
+ Networking
+ Troubleshooting
```

Only if Tag suggestion infrastructure exists.

Do not fake AI suggestions.

---

# 80. Remove Tag

Manual/user-removable Tags may support:

```text
×
```

System-required classifications may be protected according to taxonomy rules.

---

# 81. Tag Management Link

Potential:

```text
Manage Tags…
```

should navigate to:

```text
Settings → Tags & Taxonomy
```

not open a duplicate tag-management implementation.

---

# 82. Capture History Tab

Show Capture Events.

Candidate fields:

```text
Captured At
Source Application
Capture Method
Source Context
```

Potential:

```text
14:31 PowerShell   Manual
14:42 PowerShell   Manual
15:05 Outlook      Manual
```

---

# 83. Capture History Privacy

Window titles and source metadata should obey Phase 1B privacy policy.

Potential:

```text
redacted
truncated
not persisted
```

must display accordingly.

---

# 84. Capture Event Pagination

A repeatedly copied item may have many events.

Do not render thousands of capture events in one widget.

Use:

```text
limited recent events
Load More
pagination
```

if needed.

---

# 85. Relationships Tab

Show explicit relationships.

Potential sections:

```text
Tickets
Diagnostics
Knowledge Base
Scripts
Automation
```

Only display relationship types actually implemented.

---

# 86. Ticket Relationship

Example:

```text
Ticket #41872
EVIDENCE_FOR
Outlook cannot send
```

Possible actions:

```text
Open Ticket
Unlink
View relationship details
```

based on permissions/retention semantics.

---

# 87. Diagnostic Relationship

Example:

```text
Diagnostic Session #55
INPUT_TO

Network Diagnostic
WARNING
```

Possible:

```text
Open Diagnostic
```

---

# 88. KB Relationship

Example:

```text
KB-NET-014
RELATED_TO
DNS Troubleshooting
```

or:

```text
SOURCE_FOR
Draft #17
```

Use semantic relation labels.

---

# 89. Relationship Creation

Clipboard Center may provide:

```text
Attach to Ticket
Create KB Draft
```

through services.

It should not allow arbitrary relationship types unless explicitly supported.

---

# 90. Retention & Privacy Tab

Show:

```text
Sensitivity
Retention state
Expiration
Saved
Pinned
Evidence preservation
Content size
Privacy restrictions
```

This tab should explain *why* an item is retained.

---

# 91. Retention Explanation

Example:

```text
Temporary item

Scheduled expiry:
Oct 7, 2026

Preserved because:
Linked to Ticket #41872
```

This makes retention behavior understandable.

---

# 92. Save Action

Potential:

```text
Save Item
```

should visibly update:

```text
retention state
status
toolbar
navigation counts
```

---

# 93. Pin Action

Potential:

```text
Pin
Unpin
```

with immediate feedback.

---

# 94. Expiry

If item is eligible for automatic cleanup:

```text
Expires in 18 hours
```

may be useful.

Avoid countdown timers continuously repainting the UI.

Display coarse relative time.

---

# 95. Sensitive Content

If content is:

```text
SECRET_POSSIBLE
BLOCKED
```

the GUI may display:

```text
Sensitive content was not persisted.
```

rather than raw value.

---

# 96. Privacy Override

If architecture permits manual override:

```text
Save Anyway
```

must require deliberate confirmation and audit.

Do not assume such override should exist.

Phase 1A decision is authoritative.

---

# 97. Actions Tab

Actions should be generated from:

```text
Kind
Entities
Tags
Relationships
available subsystem capabilities
```

not hard-coded solely by GUI.

---

# 98. Candidate Actions

Potential:

```text
Ping IP
DNS Lookup
Search Tickets
Search KB
Run Diagnostic
Save Snippet
Attach as Evidence
Create KB Draft
Ask Mochi
```

Only expose actions supported by actual services.

---

# 99. Action Availability

Example:

```text
IPv4 detected
→ Ping / DNS Lookup available

Error Code detected
→ Search KB available

No ticket selected
→ Attach to Active Ticket unavailable
```

---

# 100. Primary Action

The GUI may emphasize one recommended safe action.

Example:

```text
Run DNS Diagnostic
```

but should not execute it automatically.

---

# 101. Action Confirmation

Potentially low-risk:

```text
Search KB
Open Ticket
```

may not need confirmation.

Potentially state-changing:

```text
Create KB Draft
Attach Evidence
Delete
```

may need explicit action/confirmation.

Diagnostics should follow Diagnostic architecture.

---

# 102. No Arbitrary Command Execution

Clipboard Center must never expose:

```text
Run copied command
```

as a generic unrestricted action.

Copied commands remain untrusted.

---

# 103. Clipboard Copy Actions

Allow:

```text
Copy raw text
Copy normalized text
Copy Entity value
```

where safe.

Do not replace Windows Clipboard automatically unless user chooses the action.

---

# 104. Keyboard Shortcuts

Plan an initial shortcut map.

Potential:

```text
Ctrl+F
Focus Clipboard search

Ctrl+P
Pin / Unpin selected item

Ctrl+S
Save selected item

Ctrl+L
Link selected item to Ticket

Delete
Delete selected item

Enter
Inspect selected item

Ctrl+M
Ask Mochi

Escape
Close secondary interaction / clear focus
```

Must be checked against existing F7Hub shortcuts.

---

# 105. Global vs Module Shortcut

Clipboard Center shortcuts should usually apply only when:

```text
Clipboard Center has focus
```

Do not register these as global AHK hotkeys.

Global hotkeys belong to Phase 1B.

---

# 106. Shortcut Discoverability

Expose shortcuts via:

```text
tooltips
menus
context menu
optional shortcut legend
```

Do not make essential functionality keyboard-secret.

---

# 107. Keyboard Navigation

Technician should be able to:

```text
focus search
move through rows
open Inspector
move between Inspector tabs
activate actions
return to table
```

without a mouse.

---

# 108. Accessibility

Plan:

```text
accessible names
logical tab order
visible focus
non-color-only states
keyboard activation
tooltips
readable contrast
```

Follow Qt accessibility conventions.

---

# 109. Empty State

Example:

```text
No Clipboard items yet.

Use Ctrl+Alt+C to send the current Clipboard
to F7Hub.
```

Only mention the actual approved hotkey.

Potential button:

```text
Capture Current Clipboard
```

---

# 110. Filter Empty State

Different from no-data state.

Example:

```text
No Clipboard items match these filters.

[Clear Filters]
```

---

# 111. Loading State

Loading should not block the entire application.

Potential:

```text
skeleton/placeholder
progress indicator
disabled list
```

Reuse existing F7Hub conventions.

---

# 112. Error State

Example:

```text
Clipboard history could not be loaded.

[Retry]
```

The draft/filter state should remain where possible.

---

# 113. Independent Retry

If:

```text
Items load
Tags fail
```

avoid blocking the entire Clipboard Center.

Use independent recoverable components where appropriate.

This follows the successful pattern used elsewhere in F7Hub.

---

# 114. Refresh

Provide explicit:

```text
Refresh
```

only if auto-refresh is insufficient.

Do not rely on constant polling.

---

# 115. Background Queries

Potential heavier operations:

```text
FTS search
relationship counts
large history
```

should not freeze the GUI.

Reuse existing async worker infrastructure if available.

---

# 116. Stale Results

If search/filter query changes while background work is running:

```text
discard stale result
```

rather than replacing newer UI state.

---

# 117. Retry Loop Guard

Explicit rule:

```text
No automatic infinite retries.
```

A failed GUI load may:

```text
retry once automatically if transient
```

only if established project conventions support it.

Otherwise expose:

```text
Retry
```

to user.

---

# 118. Search Debounce

For text search, evaluate a short debounce.

Example target:

```text
150 to 300 ms
```

Avoid SQL/FTS query on every keystroke instantaneously if unnecessary.

Exact value can be implementation-specific.

---

# 119. Database Query Responsibility

GUI should request data through:

```text
ClipboardService / Query Service
```

or approved architecture.

No SQL inside widgets.

---

# 120. Read Models

Evaluate whether Clipboard Center needs GUI-specific read models.

Example:

```text
ClipboardListItem
ClipboardInspectorDetail
CaptureHistoryEntry
RelationshipSummary
```

These may improve separation from domain entities.

Do not create DTO proliferation without need.

---

# 121. List Query

Potential conceptual request:

```text
ClipboardListQuery
  view
  search
  filters
  sort
  page
  page_size
```

This allows efficient database-backed lists.

---

# 122. Pagination

Potential:

```text
50
100
```

items per page or incremental chunk.

Recommend based on existing F7Hub table conventions.

---

# 123. Infinite Scroll

Do not introduce infinite scroll if F7Hub already uses explicit pagination.

Consistency matters more than novelty.

---

# 124. Selection Detail Loading

List result should not need to carry:

```text
full raw content
all entities
all events
all relationships
```

for every row.

Potential:

```text
list summary query
```

then:

```text
selected-item detail query
```

This is more scalable.

---

# 125. Inspector Lazy Loading

Potentially load:

```text
Capture History
Relationships
```

when corresponding tab is first opened.

Evaluate complexity vs actual expected data size.

---

# 126. Search Result Highlighting

Search matches may highlight:

```text
matching preview text
matching Entity
matching Tag
```

but avoid expensive rich rendering initially.

---

# 127. FTS Search Result Context

If FTS returns a snippet:

```text
use it as temporary search-result preview
```

without overwriting stored `preview_text`.

---

# 128. Tag Filtering

Tag selector should query canonical Tag Catalog.

Do not create free-text tags inside the filter box unless explicitly creating a User Tag through the Tag workflow.

---

# 129. Entity Type Filter

Potential:

```text
IPv4
Error Code
URL
PowerShell Command
```

from canonical Entity Type definitions.

---

# 130. Entity Value Filter

Potential advanced filter:

```text
Entity Type = IPv4
Value = 10.0.0.87
```

Likely useful for investigation.

May be deferred from MVP GUI.

---

# 131. Source Application Filter

Source applications should be derived from stored capture metadata.

Avoid requiring a separate global application taxonomy initially.

---

# 132. Date Filter

Potential presets:

```text
Today
Last 7 Days
Last 30 Days
Custom
```

Use local display while preserving canonical timestamp semantics.

---

# 133. Sensitivity Filter

Potential:

```text
Normal
Personal
Confidential
Sensitive/Blocked
```

Use Phase 1A canonical vocabulary.

---

# 134. Relationship Filter

Potential:

```text
Any
Linked
Unlinked
Ticket
Diagnostic
KB
```

---

# 135. Saved / Pinned Filter

These may remain navigation views rather than filter controls to reduce duplication.

---

# 136. Filter State Model

Recommend one central immutable or explicit state representation.

Conceptually:

```text
ClipboardViewState
```

containing:

```text
view
search
filters
sort
page
selected_item_id
```

Exact implementation follows current PySide6 architecture.

---

# 137. Navigation State

When user leaves Clipboard Center and returns, evaluate preserving:

```text
current view
filters
search
selected item
```

for the current application session.

This would improve workflow continuity.

---

# 138. Deep Linking

Other modules may navigate into Clipboard Center with context.

Examples:

```text
Open Clipboard Item #901

Open Clipboard Center filtered by:
Tag = DNS

Open Ticket Evidence for Ticket #41872
```

Plan navigation parameters.

---

# 139. Analytics Drill-Down

Future Statistical Analytics should be able to open:

```text
Clipboard Center
with filters already applied
```

Example:

```text
Tag = PowerShell
Date = Last 30 Days
```

Clipboard Center remains the evidence/detail surface.

---

# 140. Mochi Deep Link

Mochi may say:

```text
I found 8 related Clipboard Items.
```

Action:

```text
View Items
```

should open Clipboard Center with the appropriate filter/query.

---

# 141. Ticket Deep Link

Ticket workspace could open:

```text
Clipboard Center
Ticket Evidence
ticket_id = 41872
```

---

# 142. Diagnostic Deep Link

Diagnostic Center could open:

```text
Clipboard Center
Diagnostic Evidence
diagnostic_session_id = 55
```

---

# 143. Navigation Contract

Use existing application navigation mechanisms.

Do not implement module-to-module widget coupling.

Avoid:

```text
TicketWidget directly manipulating ClipboardWidget
```

Prefer:

```text
NavigationService / MainWindow routing
```

or current equivalent.

---

# 144. Status Bar

Clipboard module may expose concise status:

```text
Items: 836
View: Recent
Selected: 1
Search indexed
```

Avoid showing too many transient metrics.

---

# 145. Capture Notification

When AHK captures while Clipboard Center is visible:

```text
New Clipboard item captured
```

may appear briefly in status.

No modal dialog.

---

# 146. Duplicate Capture Feedback

If item already exists:

```text
Existing item updated
Seen 9 times
```

could be surfaced unobtrusively.

---

# 147. Delete Confirmation

Potential rules:

### Temporary unlinked item

```text
simple confirmation or immediate delete
```

depending on project convention.

### Saved / pinned item

```text
confirmation
```

### Evidence-linked item

```text
stronger explanation
```

Example:

```text
This item is linked to Ticket #41872.
Remove the relationship first?
```

Final behavior must follow Phase 1A.

---

# 148. Undo

Evaluate whether immediate Delete needs Undo.

Potential value:

```text
accidental user deletion
```

Potential issue:

```text
privacy-sensitive content should disappear immediately
```

Do not add soft-delete/Undo if domain architecture rejected it.

---

# 149. Export

Clipboard export should be deferred unless requirement exists.

Potential risks:

```text
sensitive content
customer data
large histories
```

Do not create CSV export automatically just because Analytics exists.

---

# 150. Drag and Drop

Likely not required in MVP.

Do not add drag-to-ticket or drag-to-KB until explicit workflow benefits are proven.

---

# 151. Visual Language

Clipboard Center should reuse:

```text
F7Hub spacing
buttons
toolbar patterns
table styling
dialog styling
icons
theme
status colors
```

Do not create an isolated neon Clipboard application inside F7Hub.

---

# 152. Semantic Color

Use color carefully for:

```text
warning
error
selected
sensitive
```

Do not encode Kind solely by color.

---

# 153. Tag Chips

Tags may use restrained chips.

Avoid assigning arbitrary permanent colors to hundreds of Tags unless taxonomy architecture defines them.

---

# 154. Entity Chips

Likewise:

```text
IPv4
ERROR CODE
URL
```

can use consistent visual tokens.

Avoid rainbow overload.

---

# 155. Sensitive Indicator

Use:

```text
icon + text
```

not red alone.

Example:

```text
🔒 Confidential
```

according to actual icon conventions.

---

# 156. Tooltips

Useful for:

```text
truncated preview
disabled action
retention explanation
source application
tag provenance
```

Do not hide essential information only in tooltips.

---

# 157. Contextual Action Density

Limit the main Inspector to a small set of highest-value actions.

Potential:

```text
4 to 8
```

depending on context.

Additional actions may live in:

```text
More…
```

if necessary.

---

# 158. Action Ranking

Potential prioritization:

```text
1. highly relevant deterministic action
2. search/investigation action
3. relationship action
4. assistant action
```

Do not use opaque AI ranking initially.

---

# 159. Action Provenance

If an action is suggested because of an Entity:

```text
Ping
Because IPv4 10.0.0.87 was detected
```

may improve explainability.

---

# 160. No Auto-Execution

The UI must never automatically execute technical actions merely because an Entity is selected.

All execution requires user action.

---

# 161. Clipboard Center + Right Mochi Sidebar

If F7Hub later has a global Mochi sidebar:

```text
Clipboard Center Inspector
```

must not become a duplicate assistant sidebar.

Potential layout:

```text
Main Navigation
Clipboard Workspace
Clipboard Inspector
Global Mochi Sidebar
```

Four columns may be too dense.

Phase 1C should note that when Mochi sidebar is introduced, the Clipboard Inspector may need responsive/collapsible behavior.

Do not redesign Mochi here.

---

# 162. Inspector Collapse

Consider:

```text
Ctrl+I
```

or toolbar toggle to collapse Inspector.

Exact shortcut should be checked globally.

This may help future Mochi-sidebar coexistence.

---

# 163. Persistence of Panel Sizes

Consider preserving:

```text
navigation width
inspector width
```

in UI settings if current F7Hub does this.

Do not make it required for MVP.

---

# 164. Large Dataset Target

Plan usability for at least:

```text
10,000 Clipboard Items
100,000 Capture Events
```

without loading all records.

These are planning targets, not measured claims.

---

# 165. Table Performance

Avoid:

```text
one QWidget per table cell
```

where model/delegate rendering can suffice.

Use Qt's model/view system.

---

# 166. Inspector Performance

Only selected item should load full content.

Do not pre-load all raw Clipboard contents into memory.

---

# 167. Search Performance

Plan indexes/FTS capable of interactive search.

Performance goals should be measurable later.

Candidate UX target:

```text
common filtered query < 250 ms
```

subject to dataset/test environment.

---

# 168. Entity Highlight Performance

For huge content:

```text
do not highlight thousands of Entities synchronously
```

Potential:

```text
limit highlights
lazy render
large-content mode
```

---

# 169. Large Item UX

For large content:

```text
show preview first

[Load Full Content]
```

if Phase 1A permits persisted full content.

Avoid freezing UI.

---

# 170. Read-Only Content Safety

Use a read-only viewer that does not accidentally mutate Clipboard Item content.

If future editing is desired, create a separate explicit transformation workflow.

---

# 171. Copy Selection

Standard:

```text
Ctrl+C
```

inside read-only content viewer should preserve normal copy behavior.

Do not globally hijack it.

---

# 172. Global Clipboard Capture Shortcut

Phase 1B owns:

```text
Ctrl+Alt+C
```

or final chosen hotkey.

Phase 1C should only display/help document the current configured binding.

---

# 173. Search Shortcut

`Ctrl+F` within Clipboard Center should focus local Clipboard search.

This is consistent with standard desktop expectations, subject to existing F7Hub behavior.

---

# 174. Delete Shortcut

`Delete` should only act when Clipboard table/Inspector selection context is appropriate.

It must not trigger while typing in:

```text
search
tag input
other editable fields
```

---

# 175. Escape Behavior

Potential priority:

```text
close popup
clear context menu
cancel inline editing
return focus
```

Avoid Escape unexpectedly closing the entire F7Hub application.

---

# 176. Focus Management

After:

```text
save
pin
tag assignment
link
```

preserve selected item and sensible focus.

Do not force mouse re-navigation.

---

# 177. Dialog Usage

Prefer inline panels for lightweight tasks.

Dialogs may be appropriate for:

```text
Attach to Ticket
Delete evidence confirmation
Manage retention override
```

Reuse existing F7Hub dialogs when possible.

---

# 178. Attach to Ticket Dialog

Potential content:

```text
Search Ticket
Recent Tickets
Current Ticket
relationship note optional
```

But TicketService owns validation.

Do not implement full ticket search inside Clipboard module if reusable selector exists.

---

# 179. Tag Selector Popup

Reuse global TagSelector.

Do not create Clipboard-only Tag management.

---

# 180. Diagnostic Selector

If multiple Diagnostics apply:

```text
Run Diagnostic…
```

may open a chooser.

If exactly one obvious approved diagnostic applies:

```text
Run DNS Diagnostic
```

could be direct.

Final behavior belongs partly to Diagnostic architecture.

---

# 181. Search KB Action

Potential flow:

```text
selected Entity/Tag
   ↓
Knowledge Search
   ↓
KB results
```

Clipboard Center should not embed an entire duplicate KB browser unless current F7Hub architecture supports integrated results.

---

# 182. Create KB Draft

Potential future action.

Must create:

```text
DRAFT
```

through KB service.

Never auto-publish.

---

# 183. Save Snippet

If F7Hub has a Snippet/Hotstring feature:

```text
Save Snippet
```

must route through that subsystem.

Do not duplicate snippet storage in Clipboard tables.

---

# 184. Copy Normalized Value

For certain Entities:

```text
email
IPv4
GUID
MAC
```

copy normalized representation may be useful.

Make it explicit.

---

# 185. Context Menu on Entity

Possible:

```text
Copy
Copy Normalized
Search Tickets
Search KB
Run Diagnostic
Add Tag
```

depending on Entity Type.

---

# 186. Context Menu on Tag

Potential:

```text
Filter by this Tag
Search F7Hub for Tag
View Tag Details
Remove Tag
```

---

# 187. Tag Detail Navigation

Future global Tag detail could open from Clipboard Center.

Phase 0C owns that eventual architecture.

---

# 188. Source Application Action

Potential future:

```text
Filter by PowerShell
```

when clicking source.

Useful, low-risk.

---

# 189. Capture History Action

Potential:

```text
Filter by source application
```

from a capture event.

No need for complex editing.

---

# 190. Table Row Badges

Avoid excessive visual noise.

Recommended visible semantic indicators:

```text
Pinned
Sensitive
Linked
```

only when useful.

---

# 191. Selection Summary

When an item is selected, Inspector header may show:

```text
Mixed Text
Normal
Recent
```

or:

```text
PowerShell Command
Saved
Pinned
```

---

# 192. Item ID

Internal IDs should normally remain hidden.

Developer/details mode may expose:

```text
clipboard_item_id
content_hash
```

if needed for troubleshooting.

---

# 193. Content Hash

Do not display hash prominently in normal GUI.

Useful only in:

```text
Advanced Details
```

or diagnostics.

---

# 194. Advanced Details

Potential expandable section:

```text
Item ID
Content Hash
Contract Version
Processing Status
Created At
Updated At
```

Only if useful for support/development.

---

# 195. GUI Error Boundaries

A failure loading:

```text
Capture History
```

should not erase:

```text
Summary
Entities
Tags
```

where independent loading is possible.

---

# 196. Draft Preservation

If user is:

```text
adding tags
choosing ticket
changing retention
```

and background refresh occurs, preserve the in-progress interaction.

---

# 197. Optimistic Updates

Evaluate whether:

```text
Pin
Save
```

should update visually before persistence completes.

Given F7Hub's emphasis on integrity, conservative approach may be:

```text
perform service operation
then update UI on success
```

while showing brief progress.

---

# 198. Failed Save/Pin

On failure:

```text
retain selection
show error
do not pretend state changed
```

---

# 199. Notifications

Use non-modal notification/toast/status where appropriate.

Examples:

```text
Pinned
Saved
Linked to Ticket #41872
```

Do not show confirmation dialogs for every successful action.

---

# 200. Confirmation Threshold

Reserve modal confirmations for:

```text
destructive actions
sensitive overrides
meaningful state changes with risk
```

---

# 201. Statistical Analytics Link

Potential toolbar/menu action:

```text
View Statistics
```

could later navigate to Analytics scoped by:

```text
selected Kind
Tag
Entity Type
```

Do not embed charts inside Clipboard Center.

---

# 202. Operational vs Statistical Boundary

Clipboard Center may show:

```text
Seen 47×
```

because this directly describes the selected item.

It should not show full historical dashboards such as:

```text
PowerShell captures increased 37% this quarter.
```

That belongs in Statistical Analytics.

---

# 203. Local Item Statistics

Allowed operational summaries may include:

```text
first seen
last seen
capture count
relationship count
```

because they help understand the current item.

---

# 204. Analytics Deep Link

Potential:

```text
View Statistics for PowerShell
```

opens Statistical Analytics.

---

# 205. Mochi Integration Placeholder

When available:

```text
Ask Mochi
```

may request:

```text
Explain this item
Suggest next troubleshooting step
Summarize related evidence
```

through approved context/action contracts.

---

# 206. Mochi Privacy

If item sensitivity forbids assistant context:

```text
Ask Mochi
```

should be disabled with explanation.

---

# 207. Right Sidebar Future Compatibility

The Clipboard workspace must remain usable if F7Hub later adds:

```text
global Mochi right sidebar
```

Plan:

```text
collapsible Clipboard Inspector
minimum center-table width
responsive panel sizing
```

---

# 208. Settings Integration

Clipboard Center may consume Settings such as:

```text
default view
page size
retention display
hotkey display
HUD settings reference
sensitive preview behavior
```

Avoid module-specific GUI settings unless they add real value.

---

# 209. Appearance Settings

Respect global:

```text
theme
font scaling
accent
```

where F7Hub supports them.

Clipboard Center should not introduce its own theme system.

---

# 210. Privacy Settings

Potential behavior affected by:

```text
show sensitive previews
source-window persistence
```

subject to approved policy.

Settings may tighten behavior.

They must not violate hard privacy invariants.

---

# 211. Status Messages

Standardize messages:

```text
Item saved.
Item pinned.
Tag added.
Linked to Ticket #41872.
Clipboard history refreshed.
```

Failures:

```text
Could not save item.
Could not load Tags.
```

Keep details in logs where appropriate.

---

# 212. Error Detail

User-facing errors should be concise.

Optional:

```text
Show Details
```

may reveal safe technical information.

Do not expose sensitive raw payloads.

---

# 213. Search Failure

If FTS/search subsystem fails:

```text
table browsing should remain available
```

where possible.

Graceful degradation.

---

# 214. Tag Service Failure

If Tag service is unavailable:

```text
Clipboard content remains inspectable
```

Tag editing can display:

```text
Tags unavailable
Retry
```

---

# 215. Diagnostic Service Unavailable

Disable:

```text
Run Diagnostic
```

with explanation.

Clipboard module should remain functional.

---

# 216. Mochi Unavailable

Hide or disable:

```text
Ask Mochi
```

according to overall product convention.

Do not treat it as Clipboard failure.

---

# 217. Relationship Service Failure

Existing links may remain visible from loaded detail.

Creation/removal actions should fail safely.

---

# 218. Database Failure

If core Clipboard data cannot load:

```text
show module-level error state
```

with:

```text
Retry
```

and do not crash MainWindow.

---

# 219. Threading

GUI thread must not perform long-running:

```text
SQL searches
FTS queries
entity-detail loads
diagnostics
```

if they can block responsiveness.

Reuse existing worker/task abstractions.

---

# 220. Cancellation of Background Queries

When new search replaces an old one:

```text
cancel if supported
or
ignore stale completion
```

No queue buildup.

---

# 221. Query Generation

Search/filter requests should be parameterized through repository/service code.

No dynamic SQL concatenation inside GUI.

---

# 222. Pagination State

Pagination should reset appropriately when:

```text
view changes
search changes
filter changes
```

but not when:

```text
Inspector tab changes
Pin state changes
```

unless row ordering changes.

---

# 223. Result Count

If total count is expensive:

```text
show loaded count
```

or defer full count.

Do not degrade search responsiveness solely to compute exact totals.

---

# 224. Table Empty Preview

Long content should not expand row height wildly.

Use:

```text
fixed/default row height
elided text
```

with full content in Inspector.

---

# 225. Monospace Content

Technical content viewer should use the existing approved monospace font strategy.

Do not bundle new fonts unnecessarily.

---

# 226. Clipboard Item Kinds in GUI

Display labels should come from taxonomy/reference layer.

Do not hard-code dozens of Kind names into widget code where avoidable.

---

# 227. Entity Type Labels

Likewise use canonical display metadata.

---

# 228. Tags

Use TagService / shared selectors.

---

# 229. Relationship Names

Use semantic labels defined by relationship architecture.

---

# 230. Retention Labels

Use domain-approved labels.

Do not invent GUI-only meanings.

---

# 231. GUI View Configuration

Navigation definitions may be declarative.

Conceptually:

```text
Recent:
query definition

URLs:
Kind/entity filter

Ticket Evidence:
relationship filter
```

Do not create one repository method per sidebar button if a reusable query model works better.

---

# 232. Saved Views Future

User-defined saved filters could be a future feature.

Do not implement in MVP unless explicitly required.

---

# 233. Search History

Likely defer.

---

# 234. Recent Filters

Potential future convenience.

Not necessary for first Clipboard Center.

---

# 235. Favorites

Use:

```text
Pinned
```

rather than introducing another "Favorite" concept.

Avoid semantic duplication.

---

# 236. Archive

Clipboard history should use retention/lifecycle semantics.

Do not introduce:

```text
Archived
```

unless Phase 1A requires it.

---

# 237. Trash

Likewise do not automatically create a Trash system.

Privacy-sensitive deletion may favor hard deletion.

---

# 238. Batch Actions

Likely defer:

```text
bulk tag
bulk delete
bulk pin
bulk link
```

until actual use justifies multi-selection.

---

# 239. Dragging Items

Defer.

Keyboard and explicit buttons provide clearer, testable flows.

---

# 240. Visual Density

Clipboard Center is technician software.

Prefer:

```text
compact
readable
information-dense
```

over oversized consumer-style cards.

Use cards selectively in Inspector.

---

# 241. Window Size Validation

Native Windows testing should include the project's supported minimum size.

Previous F7Hub testing often uses:

```text
1000 × 700
```

Verify current requirement before adopting it.

---

# 242. DPI Validation

Test at least project-standard Windows DPI settings.

Potential:

```text
96 DPI
125%
```

and others where established.

---

# 243. Inspector Minimum Width

Ensure:

```text
Entity values
URLs
file paths
```

remain usable through wrapping/elision.

---

# 244. Horizontal Table Scrolling

Avoid if possible for default columns.

If unavoidable, keep:

```text
Time
Preview
```

visible/usable.

---

# 245. Column Stretch Strategy

Likely:

```text
Preview → stretch
Time → fixed/compact
Kind → content
Entities → compact
Source → content
Seen → compact
Linked → compact
Pinned → compact
```

Final widths should be validated natively.

---

# 246. Table Header

Allow sorting where meaningful.

Do not expose sorting on columns with undefined semantics.

---

# 247. Row Tooltips

Preview tooltip may show more text for normal items.

Sensitive items must remain redacted.

---

# 248. Selection Highlight

Use theme-aware selection.

Do not rely on custom colors that break dark/light themes.

---

# 249. Loading Indicator

Avoid blocking modal spinner for table refresh.

Use inline progress.

---

# 250. Initial Module Load

Potential flow:

```text
Open Clipboard Center
    ↓
Restore session view/filter
    ↓
Load first page
    ↓
Display
```

Inspector remains blank until selection.

---

# 251. Default Selection

Evaluate:

```text
auto-select first row
```

versus:

```text
no selection until user chooses
```

A default first-row selection may improve information density.

Inspect current F7Hub conventions.

---

# 252. Inspector Empty State

If nothing selected:

```text
Select a Clipboard item to inspect its
Entities, Tags, relationships and actions.
```

---

# 253. Navigation Keyboard

Potential:

```text
Alt+1 etc.
```

likely unnecessary initially.

Prefer standard tab/focus navigation.

---

# 254. Main F7Hub Module Shortcut

If F7Hub has module navigation shortcuts, Clipboard Center should integrate into the same system.

Do not invent a global shortcut without inspecting existing mappings.

---

# 255. Menus

Potential main menu integration:

```text
View → Clipboard Center
Clipboard → Capture Current
Clipboard → Search
```

only if consistent with current MainWindow.

---

# 256. Toolbar Integration

Main F7Hub toolbar may have:

```text
Clipboard
```

module button.

Phase 1C should recommend integration point after inspection.

---

# 257. Navigation Sidebar Integration

If F7Hub already has left main-navigation:

```text
Dashboard
Tickets
Knowledge Base
...
```

Clipboard becomes a first-class module there.

Do not confuse application navigation with Clipboard's internal view navigation.

---

# 258. Two Navigation Levels

Conceptually:

```text
F7Hub Main Navigation
    ↓
Clipboard Center

Clipboard Internal Navigation
    ├── Recent
    ├── Saved
    └── ...
```

These must be visually distinguishable.

---

# 259. Nested Sidebar Risk

If F7Hub already uses a persistent sidebar, adding another full sidebar may consume excessive width.

Phase 1C must evaluate alternatives:

```text
compact internal rail
dropdown view selector
collapsible secondary sidebar
```

based on inspected current GUI.

This is an important architecture decision.

---

# 260. Recommended Decision Criterion

If current MainWindow already permanently consumes left-side navigation width:

```text
prefer compact Clipboard internal navigation
```

rather than another wide sidebar.

---

# 261. Inspector vs Existing Right Pane

If F7Hub already has a global right-side Assistant area, inspect whether:

```text
Clipboard Inspector
```

should use:

```text
central split pane
bottom detail panel
tabbed right region
```

instead of assuming a third permanent pane.

---

# 262. GUI Must Follow Existing Shell

The visualization created during brainstorming is conceptual.

Do not force the repository to match the mockup if current F7Hub architecture provides a better consistent pattern.

---

# 263. Loading Relationships

Relationship counts in table should preferably use efficient summary queries.

Full relationship records belong in Inspector.

---

# 264. Tags in List Queries

Avoid joining huge Tag strings into every row if it causes query duplication/performance issues.

Possible:

```text
top tag summary
count
```

or secondary lookup.

Plan based on SQLite query architecture.

---

# 265. Entity Counts

Likewise:

```text
entity_count
```

may be derived efficiently through aggregate query/view.

---

# 266. Capture Count

Should reflect true Capture Events, not arbitrary GUI access.

---

# 267. Seen

The label:

```text
Seen
```

must be defined as:

```text
number of captured occurrences
```

if that is the approved semantic.

Avoid ambiguous "Views."

---

# 268. Search Indexing Status

Developer/status UI may show:

```text
Search indexed
```

only if meaningful.

Not required for normal user UI.

---

# 269. Refresh After Capture

New capture of existing item may update:

```text
Last Seen
Seen count
source history
```

without creating new table row.

GUI should animate/update subtly if useful but not required.

---

# 270. Table Ordering After Update

If sorted by Last Seen, duplicate recapture may move existing row to top.

Preserve selection where practical.

---

# 271. Inspector Update

If selected item's count changes due to a new capture:

```text
update inspector
```

without resetting active tab.

---

# 272. Concurrency

Possible simultaneous changes:

```text
AHK capture
user pins item
background cleanup
```

GUI must tolerate records changing underneath it.

---

# 273. Optimistic Concurrency

Inspect existing repository/service patterns.

If records include:

```text
updated_at
version
```

reuse stale-write protections.

Do not introduce a new concurrency mechanism solely for Clipboard without need.

---

# 274. Deleted Item While Selected

If cleanup removes a temporary selected item:

```text
clear Inspector
refresh list
show concise status
```

---

# 275. Evidence Protection

Cleanup should not remove preserved evidence according to Phase 1A.

GUI should not need to fight cleanup logic.

Domain owns that invariant.

---

# 276. Query Service

Evaluate whether read-heavy Clipboard GUI benefits from:

```text
ClipboardQueryService
```

separate from command-oriented ClipboardService.

Only recommend if consistent with current architecture and complexity.

---

# 277. CQRS

Do not introduce formal CQRS framework merely because reads and writes differ.

Use lightweight separation if useful.

---

# 278. GUI Presentation Models

Potential models:

```text
ClipboardListRow
ClipboardInspectorModel
ClipboardEntityRow
ClipboardCaptureEventRow
ClipboardRelationshipRow
```

Keep them read-focused and immutable where practical.

---

# 279. Testability

GUI presentation logic should be independently testable from actual Windows Clipboard and IPC.

Phase 1C tests use persisted/service data.

Phase 1B tests Windows capture.

---

# 280. Unit Tests

Future tests should cover:

```text
view-state changes
filter construction
action enablement
selection handling
retention labels
sensitivity display
shortcut routing
```

---

# 281. GUI Tests

Future Qt tests should cover:

```text
module navigation
default view
row selection
Inspector updates
search
filters
Tag selector
Pin
Save
Delete confirmation
relationship dialog
error states
retry
```

---

# 282. Integration Tests

Future integration tests should cover:

```text
database → service → GUI
new capture appears
duplicate capture updates row
Tag assignment persists
Ticket link appears
retention state changes
search returns expected item
```

---

# 283. Native Windows Validation

Validate real F7Hub window for:

```text
layout
DPI
resizing
keyboard navigation
context menus
dialogs
focus
table scrolling
Inspector
```

---

# 284. Screenshot Validation

Codex should inspect screenshots for:

```text
clipping
overlap
truncation
bad contrast
empty space
incorrect alignment
incorrect disabled states
unreadable tags/entities
```

---

# 285. Screenshot Test Loop Guard

Explicitly prevent repeated validation loops.

Rule:

```text
If the same native test fails twice without
a code/state change, STOP and diagnose.
```

Future implementation agent should produce:

```text
BLOCKED
```

rather than rerunning indefinitely.

---

# 286. Performance Tests

Future performance validation should include:

```text
10k Clipboard Items
search
filter
sort
select
Inspector load
```

and, where practical:

```text
100k Capture Events
```

---

# 287. Search Performance

Measure:

```text
first search
warm search
rapid query changes
```

No claims without actual test results.

---

# 288. Memory Usage

Ensure list loading does not retain:

```text
full raw text for thousands of rows
```

in memory unnecessarily.

---

# 289. Privacy Tests

Future GUI tests should confirm:

```text
sensitive preview redacted
secret-like content not surfaced
Mochi disabled where prohibited
logs do not contain raw content
```

---

# 290. Accessibility Tests

Validate:

```text
Tab order
keyboard actions
accessible labels
focus visibility
screen scaling
non-color-only status
```

---

# 291. Error-Handling Tests

Cover:

```text
list load failure
Inspector load failure
Tag load failure
relationship failure
Pin failure
Save failure
Delete failure
search failure
```

---

# 292. No Fake Success

If persistence fails:

```text
do not update UI to successful state
```

unless using a fully managed optimistic pattern with rollback.

---

# 293. Documentation Impact

Future implementation likely updates:

```text
04_UserWorkflows.md
05_GUI.md
06_SystemArchitecture.md
13_PythonArchitecture.md
03_Features.md
```

Database changes from earlier Clipboard slices may additionally affect:

```text
07_Database.md
08_ERD.md
09_SQLSchema.md
```

Do not update them during Phase 1C planning unless explicitly requested.

---

# 294. Required GUI Architecture Diagram

Produce a Mermaid diagram representing:

```text
MainWindow
   ↓
ClipboardWorkspace
   ├── View Navigation
   ├── Search / Filters
   ├── Clipboard Table
   └── Inspector
          ├── Summary
          ├── Entities
          ├── Tags
          ├── Capture History
          ├── Relationships
          ├── Retention
          └── Actions
```

Adapt names to existing architecture.

---

# 295. Required Interaction Diagram

Produce:

```text
User selects row
   ↓
Clipboard Workspace
   ↓
Clipboard Query/Service
   ↓
Load selected detail
   ↓
Inspector renders
```

---

# 296. Required Action Diagram

Example:

```text
User selects IPv4 Entity
   ↓
Actions
   ↓
Run Network Diagnostic
   ↓
DiagnosticService
   ↓
Diagnostic Center
```

Clipboard GUI must not call PowerShell directly.

---

# 297. Required Deep-Link Diagram

Show:

```text
Analytics
Ticket
Diagnostic
Mochi
      ↓
Navigation Service
      ↓
Clipboard Center
      ↓
View / Filter / Selected Item
```

---

# 298. Required Layout Variants

Document:

```text
wide
medium
minimum supported
```

with recommendations for:

```text
navigation
center table
Inspector
```

No pixel-perfect mockup required unless helpful.

---

# 299. Required Navigation Inventory

For every Clipboard view provide:

```text
display name
purpose
query semantics
default sort
empty state
```

---

# 300. Required Table Column Matrix

For every candidate column provide:

```text
column
meaning
source
sortable?
default visible?
width strategy
privacy risk
```

---

# 301. Required Filter Matrix

For:

```text
search
Kind
Tag
Entity Type
Source
Sensitivity
Relationship
Date
```

define:

```text
query semantics
combinability
default
clear behavior
```

---

# 302. Required Inspector Tab Matrix

For each tab:

```text
purpose
data required
load strategy
actions
error state
empty state
```

---

# 303. Required Action Matrix

For each action define:

```text
action key
owner subsystem
required selection
required Entity/Tag
confirmation?
sync/async?
available in toolbar?
available in Inspector?
available in context menu?
```

---

# 304. Required Keyboard Shortcut Matrix

For each shortcut:

```text
binding
scope
action
conflicts
editable-widget behavior
```

Do not approve conflicts silently.

---

# 305. Required Privacy Matrix

For GUI surfaces:

```text
table preview
full content
Entity tab
Capture History
status messages
tooltips
Mochi action
```

define behavior for each sensitivity class.

---

# 306. Required Loading/Error Matrix

For:

```text
list
search
Inspector
Tags
Entities
Capture History
Relationships
Actions
```

define:

```text
loading
empty
partial
failure
retry
```

---

# 307. Required Performance Strategy

Document:

```text
pagination
lazy detail loading
FTS search
structured filtering
async query execution
stale-result rejection
large-content handling
```

---

# 308. Required Reuse Assessment

Identify current GUI elements as:

```text
REUSE
EXTEND
NEW
NOT NEEDED
NOT VERIFIED
```

Potential:

```text
main navigation
table model
filter widgets
async worker
Tag selector
Ticket selector
status notification
dialogs
splitters
search box
```

---

# 309. Required Settings Inputs

List settings used directly by Clipboard Center.

Mark:

```text
CORE
LIKELY
FUTURE
NOT NEEDED
```

Avoid turning layout details into excessive settings.

---

# 310. Required Integration Inputs

Document dependencies on:

```text
ClipboardService
TagService
TicketService
DiagnosticService
Knowledge Base Service
Navigation Service
SettingsService
ContextService / Mochi future
```

Mark unavailable systems as future/deferred.

---

# 311. Required Dependency Rules

Clipboard GUI may depend on:

```text
application/query services
shared GUI components
navigation
settings
```

It must not depend on:

```text
AHK internals
PowerShell process details
analytics implementation
raw database connection
```

---

# 312. Required Decision Register

At minimum evaluate:

```text
three-pane vs existing F7Hub shell adaptation
secondary navigation style
default view
default columns
single vs multi-select
pagination model
Inspector tab set
full-content viewer
Entity highlighting
Tag editing
relationship UI
retention UI
search/filter interaction
keyboard shortcuts
deep-link model
async loading
panel-collapse behavior
future Mochi sidebar coexistence
```

For each:

```text
Decision
Options
Recommendation
Reason
Consequences
Status
```

Statuses:

```text
RECOMMENDED
REQUIRES_USER_DECISION
DEFERRED
NOT_VERIFIED
```

---

# 313. Required Risk Register

Include:

```text
GUI density
nested navigation
too many actions
slow search
loading full content
FTS latency
stale async results
sensitive content exposure
Tag clutter
Entity clutter
relationship coupling
keyboard conflicts
Mochi sidebar width conflict
large-data table performance
testing loops
```

Provide mitigation.

---

# 314. Planning Depth

Classify:

```text
DECIDE NOW
DESIGN DURING SLICE
DEFER
```

Likely `DECIDE NOW`:

```text
workspace composition
navigation semantics
table/read-model structure
Inspector architecture
search/filter behavior
privacy presentation
deep-link behavior
service boundaries
```

Likely `DESIGN DURING SLICE`:

```text
exact icon
column pixel width
minor spacing
tooltip wording
```

Likely `DEFER`:

```text
bulk actions
drag/drop
user-created views
search history
advanced syntax highlighting
custom column layouts
```

---

# 315. MVP Clipboard Center Boundary

Recommended first useful Clipboard Center should include:

```text
module navigation entry

Recent
Saved
Pinned
URLs

search

basic filters:
Kind
Source
Date
Tag

table:
Time
Preview
Kind
Entities
Source
Seen
Linked
Pinned

Inspector:
Summary
Entities
Tags
Capture History
Relationships
Retention & Privacy
Actions

Save
Pin
Delete
Attach to Ticket
Search KB
Open related record
```

Actions depending on unfinished subsystems should be introduced only when their owning feature exists.

---

# 316. Later Clipboard GUI Features

Defer:

```text
bulk editing
drag/drop
custom saved views
advanced column customization
complex syntax highlighting
AI-generated actions
binary/image previews
OCR
full analytics widgets
automatic remediation
```

---

# 317. Recommended Implementation Sequence After Approval

Phase 1C may recommend implementation slices, but must not implement them.

Potential sequence:

```text
Clipboard GUI Slice A
Module shell + Recent list

Clipboard GUI Slice B
Selection + Summary Inspector

Clipboard GUI Slice C
Search + filters

Clipboard GUI Slice D
Entities Inspector

Clipboard GUI Slice E
Tags integration

Clipboard GUI Slice F
Capture History

Clipboard GUI Slice G
Ticket relationships

Clipboard GUI Slice H
Retention / Save / Pin / Delete

Clipboard GUI Slice I
Contextual actions

Clipboard GUI Slice J
Deep links + native polish
```

Final slicing must be based on actual repository inspection and current Slice numbering.

---

# 318. Do Not Bundle the Whole GUI

Explicit prohibition:

```text
Do not implement Clipboard Center in one giant slice.
```

Each implementation slice must:

```text
have one user-visible vertical outcome
have bounded files
have focused tests
have regression tests
be independently reviewable
be reversible
```

---

# 319. Completion Gate Before Implementation

After Phase 1C, verify all Clipboard architecture documents agree:

```text
1A
Domain / lifecycle

1B
Windows capture / IPC / HUD

1C
PySide6 operational GUI
```

If they conflict, resolve architecture before implementation.

---

# 320. Phase 1C Acceptance Criteria

Phase 1C is acceptable when:

1. Existing PySide6 shell and GUI conventions have been inspected.
2. Reusable GUI components are identified.
3. Clipboard Center has a clear place in MainWindow.
4. Internal navigation semantics are defined.
5. Default Clipboard views are defined.
6. Search semantics are defined.
7. Filter architecture is defined.
8. Table columns are defined conceptually.
9. Large-data table strategy is defined.
10. Selection behavior is defined.
11. Inspector architecture is defined.
12. Summary content is defined.
13. Entity presentation is defined.
14. Entity actions are bounded.
15. Tag integration uses global Tag architecture.
16. Capture History behavior is defined.
17. Relationship display and actions are defined.
18. Retention/privacy display is defined.
19. Contextual actions route through owning services.
20. No arbitrary command execution is possible.
21. Keyboard behavior is defined.
22. Accessibility requirements are defined.
23. Sensitive-content presentation is defined.
24. Loading/error/partial states are defined.
25. Async stale-result handling is defined.
26. Deep-link architecture is defined.
27. Analytics drill-down compatibility is defined.
28. Mochi sidebar compatibility is considered.
29. Native Windows validation is planned.
30. Testing-loop guard is explicit.
31. No production implementation occurred.
32. Clipboard feature architecture is complete enough to begin vertical implementation planning.

---

# 321. Validation

Return:

```text
Current GUI inspection                 PASS / FAIL / BLOCKED
MainWindow integration                 PASS / FAIL / BLOCKED
Workspace composition                  PASS / FAIL / BLOCKED
Navigation model                       PASS / FAIL / BLOCKED
Search/filter architecture             PASS / FAIL / BLOCKED
Table architecture                     PASS / FAIL / BLOCKED
Inspector architecture                 PASS / FAIL / BLOCKED
Entity presentation                    PASS / FAIL / BLOCKED
Tag integration                        PASS / FAIL / BLOCKED
Relationship UX                        PASS / FAIL / BLOCKED
Retention/privacy UX                   PASS / FAIL / BLOCKED
Contextual actions                     PASS / FAIL / BLOCKED
Keyboard/accessibility                 PASS / FAIL / BLOCKED
Async/error handling                   PASS / FAIL / BLOCKED
Large-data strategy                    PASS / FAIL / BLOCKED
Deep-link architecture                 PASS / FAIL / BLOCKED
Native validation plan                 PASS / FAIL / BLOCKED
Scope control                          PASS / FAIL / BLOCKED
Production changes                     MUST BE NONE
Database changes                       MUST BE NONE
```

---

# 322. Required Final Report

Return the report in this order:

## Summary

Recommended Clipboard Center GUI architecture.

## Inspected Current GUI

Existing F7Hub patterns and components.

## MainWindow Integration

Where Clipboard Center belongs in the application shell.

## Workspace Composition

Navigation, center list and Inspector arrangement.

## Navigation Views

Purpose and query semantics for every view.

## Toolbar

Available actions and ownership.

## Search & Filters

Search behavior, filter model and state.

## Clipboard Table

Columns, sorting, pagination and selection.

## Inspector

Tabs and data ownership.

## Entities

Presentation, highlighting and actions.

## Tags

Global Tag integration and selector behavior.

## Capture History

Capture-event UX and privacy.

## Relationships

Ticket, Diagnostic, KB and other links.

## Retention & Privacy

Save, Pin, Evidence, expiry and sensitive content.

## Contextual Actions

Action-generation and routing.

## Keyboard & Accessibility

Shortcut and navigation model.

## Loading / Empty / Error States

Independent failure behavior.

## Async Architecture

Background loading, stale-result rejection and GUI responsiveness.

## Large Dataset Strategy

Pagination, read models and performance.

## Deep Links

Ticket, Diagnostic, Analytics and Mochi navigation.

## Future Mochi Sidebar Compatibility

Panel-layout implications.

## Settings Inputs

Phase 0D configuration used by the GUI.

## Reuse Assessment

REUSE / EXTEND / NEW / NOT VERIFIED.

## Testing Strategy

Unit, GUI, integration, regression and native Windows validation.

## Decision Register

Resolved, deferred and user-review decisions.

## Risk Register

Clipboard GUI architectural risks.

## Recommended Vertical Implementation Slices

Small sequential slices only.

## Clipboard Architecture Closure

Explicitly confirm whether Phases 1A, 1B and 1C form a coherent implementation-ready feature architecture.

## Result

Return exactly one:

```text
READY_FOR_CLIPBOARD_SLICE_PLANNING
REQUIRES_CLIPBOARD_GUI_DECISIONS
BLOCKED
```

Do not return:

```text
READY_FOR_IMPLEMENTATION
```

Phase 1C closes Clipboard architecture planning, not implementation.