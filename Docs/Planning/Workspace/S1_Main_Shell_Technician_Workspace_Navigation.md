# F7Hub Workspace Planning S1
# Main Shell, Technician Workspace & Navigation Architecture Planning Contract

**Status:** `NOT_STARTED`  
**Mode:** `@ARCHITECT @PLAN`  
**Future repository path:** `Docs/Planning/Workspace/S1_Main_Shell_Technician_Workspace_Navigation.md`  
**Implementation authorization:** NONE

---

## 1. Purpose

Define the F7Hub application shell before more module-specific GUI work is implemented.

This plan must establish one coherent architecture for:

- `MainWindow`
- Technician Workspace
- module hosting
- main navigation
- reusable navigation flyouts
- Active Technician Context
- Active Ticket access
- Quick Ticket Drawer
- global search and global status
- responsive internal panels
- keyboard/accessibility behavior
- future Mochi/DynamicHub coexistence
- reusable module navigation metadata

The objective is to avoid implementing every button, flyout, panel, and workspace as a one-off GUI.

---

## 2. Dependency Gate

Required approved inputs:

```text
Foundation 0A-0E CLOSED
Clipboard 1A CLOSED
Clipboard 1B CLOSED
```

If this S1 plan is approved before Clipboard 1C, Clipboard 1C should consume S1 rather than independently inventing shell behavior.

If an approved upstream contract conflicts with S1:

```text
RECORD CONFLICT
IDENTIFY OWNER
REQUEST OWNER REVIEW
DO NOT PATCH AROUND IT
```

---

## 3. Approved Technician Workspace Principle

F7Hub may provide a first-class `Technician Workspace` inside the primary PySide6 application.

The Technician Workspace may coordinate:

```text
embedded tool hosting
internal tabs
navigation
activation
layout
split views
context propagation
workspace restoration
tool lifecycle
```

It remains a presentation/application-shell concept.

Domain ownership remains outside the Workspace:

```text
Tickets      -> Ticket services/domain
Clipboard    -> Clipboard services/domain
Diagnostics  -> Diagnostic services/domain
Knowledge    -> Knowledge services/domain
PowerShell   -> approved execution boundary
Analytics    -> Analytics services/domain
Mochi        -> approved Mochi/application boundary
```

---

## 4. Mode and Prohibitions

This phase is architecture planning only.

Do not:

- modify `MainWindow`
- create PySide6 production classes
- create `.ui` files
- create migrations
- implement Settings
- implement flyouts
- implement Quick Ticket
- implement Active Technician Context
- implement Mochi/DynamicHub
- register new global hotkeys
- redesign business services
- introduce a plugin framework only to host shell metadata
- adopt `QMdiArea` as the primary workspace without explicit review
- create unnecessary external popup windows

---

## 5. Mandatory Current-State Inspection

Before recommending shell architecture, inspect:

```text
Python/f7hub/gui/main_window.py
application bootstrap
current QStackedWidget/workspace hosting
TicketWorkspace
KnowledgeWorkspace
ScriptWorkspace
existing dialogs and splitters
menus and toolbars
status bar
navigation shortcuts
ServiceTaskRunner
navigation helpers/services
Mochi runtime/settings controls
AltF7Hub launch/focus integration
GUI tests
native screenshot-validation patterns
Docs/05_GUI.md
Docs/06_SystemArchitecture.md
Docs/13_PythonArchitecture.md
ROOT.md
```

Classify findings as:

```text
FACT
ASSUMPTION
INFERENCE
RECOMMENDATION
NOT VERIFIED
```

Use:

```text
SEARCH -> IDENTIFY -> REUSE/EXTEND -> CREATE ONLY IF NECESSARY
```

---

## 6. Target Shell Model

Evaluate this conceptual structure against the actual current shell:

```text
+-------------------------------------------------------------------+
| F7Hub MAIN SHELL                                                  |
| Main Navigation | Active Technician Context | Global Search/Status|
+-------------------------------------------------------------------+
| TECHNICIAN WORKSPACE                                              |
| Tickets | Clipboard | Diagnostics | Knowledge | Scripts | ...    |
| Active module workspace                                           |
+------------------------------------------+------------------------+
| Optional Quick Ticket / utility panel    | Mochi reserved region |
+------------------------------------------+------------------------+
```

Do not force the diagram if current repository conventions support a simpler equivalent.

---

## 7. Three Interaction Depths

### Level 1 - Navigation Flyout

Use for:

```text
fast navigation
lightweight context
recent/pinned destinations
small explicit quick actions
```

Hover alone must never execute a business action.

### Level 2 - Quick Internal Panel

Use for a bounded task without leaving the current workspace.

Primary candidate:

```text
Quick Ticket Drawer
```

### Level 3 - Full Workspace

Use for substantial work:

```text
Ticket Workspace
Clipboard Center
Diagnostic Center
Knowledge Workspace
Script Workspace
```

---

## 8. Technician Workspace Host

Evaluate reuse/extension of:

```text
QStackedWidget
QTabWidget or project-equivalent tabs
QSplitter
QDockWidget with floating disabled
shared workspace host
```

### QMdiArea decision

`QMdiArea/QMdiSubWindow` must be explicitly evaluated, but default recommendation should be `NOT RECOMMENDED AS PRIMARY MODEL` unless workflow evidence justifies overlapping internal windows.

Assess:

```text
z-order
focus complexity
overlap
restoration
small-screen usability
keyboard navigation
native-test burden
```

Prefer structured stacked/tabbed/split/docked-without-floating layouts.

---

## 9. Active Technician Context

Plan a shared application-level context containing references such as:

```text
Company
User
Device
Ticket
Tenant
Session
```

Conceptual model:

```text
ActiveTechnicianContext
  company_ref?
  user_ref?
  device_ref?
  ticket_ref?
  tenant_ref?
  session_ref?
  revision
```

The shell owns the current selection reference, not domain truth.

Owning services must revalidate references before mutation or execution.

---

## 10. Active Ticket Everywhere

Ticket access must not require switching to the full Tickets module for every small action.

Plan three distinct concepts:

```text
Active Ticket Context
Quick Ticket Drawer
Full Ticket Workspace
```

Potential shell summary:

```text
INC-10452 | Contoso | Jane Smith | PC-042
[Quick Note] [Open Ticket]
```

The full Ticket Workspace remains the deep-work interface.

---

## 11. Quick Ticket Drawer

Plan an internal MainWindow panel, not another desktop window.

Potential contents:

```text
Ticket summary
Quick Note
Status summary
Recent diagnostic result
Current Clipboard evidence
KB reference
Open Full Ticket Workspace
```

Rules:

- all mutations route through Ticket services
- no direct SQLite
- no duplicate Ticket validation
- no silent destruction of TicketWorkspace drafts
- fail truthfully if Ticket state changed

---

## 12. Reusable Main Navigation

Each main module button should provide shell metadata conceptually equivalent to:

```text
module_key
display_name
icon_key
primary_route
active_state
optional_badge
optional_flyout_descriptor
keyboard/accessibility metadata
```

Do not hand-code a unique navigation mechanism for each module.

---

## 13. Reusable Navigation Flyout

Plan one shared flyout host.

Conceptual placement modes:

```text
RIGHT_OF_TRIGGER
BELOW_TRIGGER
AUTO
```

This should support both sidebar and possible future top navigation.

### Trigger rules

```text
hover after bounded delay -> open
pointer moves trigger -> flyout -> remain open
leave trigger + flyout -> bounded close grace
keyboard focus -> can open
click/touch -> valid non-hover path
Escape -> close
```

Hover alone must never execute.

### Planning timing ranges

```text
open delay: ~200-350 ms
close grace: ~300-500 ms
animation: brief/subtle/optional
```

Exact timing belongs to later native tuning.

### Focus

Hover normally must not steal keyboard focus.

### Transparency

Evaluate readable semi-transparency, approximately:

```text
85-95% opacity
```

Requirements:

```text
accessible contrast
theme compatibility
DPI safety
no privacy leak
```

Blur/acrylic is optional, not architectural.

---

## 14. Standard Flyout Anatomy

Prefer a consistent structure:

```text
+------------------------------+
| CONTEXT                      |
+------------------------------+
| QUICK ACTIONS                |
+------------------------------+
| NAVIGATION / RECENT          |
+------------------------------+
| Open full workspace          |
+------------------------------+
```

Zones may be omitted when irrelevant.

Flyouts must not become mini full workspaces.

---

## 15. Flyout Safety Rules

A flyout must not:

```text
call RMM/Graph merely because of hover
run PowerShell on hover
mutate Tickets on hover
eagerly load large datasets
display secrets in previews
steal focus unexpectedly
open nested cascading flyout chains for MVP
```

Every side effect requires explicit user action.

---

## 16. Navigation Surface Matrix

S1 must produce a complete matrix for every primary module.

Required columns:

```text
Button
Primary route
Context header
Quick actions
Navigation items
Recent/pinned items
Badge/status
Empty state
Unavailable state
Keyboard access
Hover behavior
Click behavior
Capability dependency
Owning service
MVP/Later
```

This matrix should be detailed enough that later implementation of a button does not require redesigning its flyout content.

---

## 17. Initial Flyout Content Inventory

This is a planning seed, not approved implementation.

| Module | Context | Quick actions | Navigation / dynamic content |
|---|---|---|---|
| Dashboard | Active Ticket/User/Device | Resume work, Quick Note, Global Search | Today, recent activity, attention items |
| Tickets | Active Ticket, Company, User, Device | Quick Note, New Ticket, Open Active Ticket | Active, Waiting Customer, Waiting Vendor, Recent, History |
| Companies/Users/Devices | Active identity context | Search, open user/device, copy approved identity | Recent companies/users/devices |
| Clipboard | Current/last capture state | Capture Current, Save, Pin, Attach to Active Ticket | Recent, Saved, Pinned, URLs, Evidence, Open Center |
| Knowledge | Current query/article | Search, Create Draft, Open Article | Recent, Drafts, Published, Categories |
| Diagnostics | Active target/recent result | Approved read-only checks | Network, Device, M365, Security, Recent Results |
| Scripts/Automation | Active target/capabilities | Approved catalog actions only | Favorites, Approved Scripts, Recent Runs |
| Applications/Websites | Optional context | Launch pinned resource | Favorites, Recent, Categories |
| Search | Current scope/query | Global Search, clear scope | Scoped searches, recent queries if later approved |
| Analytics/Reports | Active Ticket/Company | Open relevant report | Recent reports, dashboards, drill-downs |
| Settings | Current profile/pending state | Usually none | Appearance, Hotkeys, Clipboard, Integrations, Mochi |
| Mochi/AI | Active technician context | Explain, Summarize, Suggest next approved action | Context actions, Open Mochi surface |

The final matrix must be based on actual current module inventory.

---

## 18. Capability Gating

Every quick action must define:

```text
action_key
owner_service
required_context
required_capability
required_permission
risk_class
confirmation
offline behavior
unavailable reason
```

UI visibility does not grant authorization.

---

## 19. Global Search and Global Status

Plan shell-level entry points for:

```text
Global Search
Background/operation status
```

Do not duplicate every module's search engine.

Do not turn status into a raw log viewer.

---

## 20. Module Internal Navigation

Distinguish:

```text
F7Hub Main Navigation
```

from:

```text
Module Internal Navigation
```

Avoid permanent nested wide sidebars.

Evaluate compact rail, dropdown, tabs, collapsible internal nav, or flyout based on actual shell evidence.

---

## 21. Responsive Shell

Define behavior for:

```text
WIDE
MEDIUM
MINIMUM SUPPORTED
```

for:

```text
main navigation
active context
global search
workspace
Quick Ticket
module Inspector
Mochi region
```

Avoid multiple permanent sidebars competing for width.

---

## 22. Draft Preservation and Context Switching

Navigation must not silently destroy unsaved drafts.

Use owning workspace draft guards.

Switching Company/User/Device/Ticket must advance a context revision and prevent stale background results from silently applying to the new context.

---

## 23. Deep Links

Plan typed validated navigation requests, for example:

```text
open_module("clipboard")
open_ticket(ticket_id)
open_clipboard_item(item_id)
open_diagnostic_result(result_id)
```

No arbitrary SQL, code, or unvalidated widget names.

---

## 24. Settings Boundary

Potential durable preferences:

```text
flyout enabled
flyout opacity
hover delay
close grace
default workspace
panel restoration policy
```

Do not automatically persist:

```text
current hover
current flyout
temporary selection
transient context
every splitter pixel
every filter
```

Runtime state is not Settings.

---

## 25. Privacy, Security and Offline Rules

Shell/flyouts must not:

```text
grant provider permissions
execute PowerShell directly
bypass service validation
store provider secrets
accept arbitrary action strings
treat selection as authorization
```

Flyouts are ambient surfaces, so customer/Ticket/Clipboard/diagnostic previews require explicit privacy rules.

Local navigation must continue when external providers are unavailable.

---

## 26. Keyboard and Accessibility

Plan keyboard access for:

```text
main navigation
flyout open/close
flyout items
module switching
Quick Ticket
Global Search
Escape
workspace tabs if approved
```

Require:

```text
accessible names
visible focus
logical Tab order
keyboard-only operation
non-color-only status
high-DPI/scaling
sufficient contrast
```

Hover cannot be the sole access path.

---

## 27. Native Validation Plan

Future implementation must validate:

```text
hover timing
pointer transfer trigger -> flyout
leave grace
keyboard open
Escape
focus retention
click/touch fallback
screen-edge clamping
multi-monitor
DPI
theme
opacity/contrast
rapid movement across buttons
app deactivation
modal coexistence
```

Loop guard:

```text
same failure twice
+ no relevant code/state change
= STOP, DIAGNOSE, BLOCKED
```

---

## 28. Required Diagrams

Produce:

1. Main Shell architecture
2. Navigation flyout sequence
3. Active Ticket / Quick Ticket flow

---

## 29. Required Reuse Assessment

Classify at minimum:

```text
MainWindow
QStackedWidget/current workspace host
existing navigation actions
toolbar/menu actions
ServiceTaskRunner
navigation helpers
TicketWorkspace
KnowledgeWorkspace
ScriptWorkspace
status bar
dialogs
splitters
Mochi settings/runtime surface
```

as:

```text
REUSE
EXTEND
NEW
NOT NEEDED
NOT VERIFIED
```

---

## 30. Decision Register

At minimum decide/recommend:

```text
Technician Workspace host
QMdiArea acceptance/rejection
Active Technician Context
Quick Ticket Drawer
main navigation style
reusable flyout host
hover/click behavior
flyout opacity
module descriptor model
workspace tabs
internal docks
responsive shell
module-internal navigation
Mochi reserved region
global search/status
workspace restoration
```

Statuses:

```text
RECOMMENDED
REQUIRES_USER_DECISION
DEFERRED
NOT_VERIFIED
```

---

## 31. Risk Register

Include:

```text
shell over-complexity
nested sidebars
too many persistent panels
accidental flyout activation
hover-only accessibility
focus stealing
privacy leakage
provider calls on hover
duplicate navigation logic
duplicate context ownership
Ticket draft loss
stale context actions
tab explosion
DPI/multi-monitor defects
opacity readability
Mochi/Inspector width conflict
testing loops
```

---

## 32. Future Slice Decomposition

Potential sequence only:

```text
Shell A - navigation descriptor foundation
Shell B - flyout host + one pilot module
Shell C - Active Technician Context
Shell D - Quick Ticket Drawer
Shell E - remaining module flyouts
Shell F - responsive/keyboard/accessibility
Shell G - restoration/native polish
```

Do not implement.

---

## 33. Acceptance Criteria

S1 is acceptable when all are PASS:

1. Current MainWindow/workspace host inspected.
2. Existing workspace/navigation patterns inspected.
3. Technician Workspace ownership explicit.
4. QMdiArea versus structured hosting decided/recommended.
5. Active Technician Context defined without stealing domain ownership.
6. Active Ticket globally reachable.
7. Quick Ticket scope defined.
8. Main navigation ownership defined.
9. Reusable flyout mechanics defined.
10. Hover/click/keyboard/touch behavior defined.
11. Flyout focus behavior defined.
12. Flyout opacity/privacy requirements defined.
13. Standard flyout anatomy defined.
14. Every primary module represented in Navigation Surface Matrix.
15. Hover never executes business actions.
16. Descriptor concept does not become business plugin framework.
17. Responsive shell behavior defined.
18. Main versus internal navigation distinguished.
19. Draft preservation defined.
20. Context switching/stale handling defined.
21. Deep links bounded.
22. Settings versus runtime state defined.
23. Keyboard/accessibility defined.
24. Offline degradation defined.
25. Native validation planned.
26. Test-loop guard explicit.
27. Mochi/DynamicHub region reserved without implementation.
28. No production implementation.
29. No database change.
30. Future shell implementation decomposable into small slices.

---

## 34. Result Vocabulary

Return exactly one:

```text
READY_FOR_SHELL_REVIEW
REQUIRES_SHELL_DECISIONS
BLOCKED
```

Never return `READY_FOR_IMPLEMENTATION`.

---

## 35. Completion Boundary

Stop after the S1 architecture candidate.

Do not implement the shell, flyouts, Quick Ticket, Active Technician Context, Mochi/DynamicHub, Settings, or Clipboard Center.
