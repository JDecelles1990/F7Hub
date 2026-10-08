# F7Hub Workspace Planning S1
# Main Shell, Technician Workspace & Navigation Architecture

> **Planning status:** `NOT_STARTED`
>
> **Mode:** `@ARCHITECT @PLAN`
>
> **Proposed repository path:** `Docs/Planning/Workspace/S1_Main_Shell_Technician_Workspace_Navigation.md`
>
> **Purpose:** Freeze the F7Hub application shell, Technician Workspace, global working context, navigation-flyout and Quick Ticket architecture before additional module-specific GUI work makes shell changes expensive.

---

## 1. Why This Planning Phase Exists

F7Hub is becoming a dense technician application. A button, pane, route, flyout or workspace integration can require hours of implementation, native validation, screenshots, regression testing, review and Git integration.

The shell therefore needs one reusable architecture before each module independently invents navigation, hover flyouts, side panes, active-ticket handling, quick actions, secondary navigation, workspace tabs, right-side panels, status surfaces or module activation behavior.

The goal is to make future module UI work primarily a matter of supplying module content to reusable shell primitives rather than repeatedly building another popup/navigation framework.

---

## 2. Dependency Gate

Before executing this plan, verify:

```text
Foundation 0A–0E  CLOSED
Clipboard 1A      CLOSED
Clipboard 1B      CLOSED
```

Clipboard 1C is not authoritative input unless separately reviewed, USER-approved and integrated.

If repository state differs:

```text
RESULT = BLOCKED
```

Do not compensate by inventing replacement architecture.

---

## 3. Approved Architectural Anchor

The root architecture already allows a first-class `Technician Workspace` inside the primary PySide6 application. It may host substantial technician tools, internal tabs, activation, layout, split views, context propagation, restoration and tool lifecycle.

It remains a presentation/application-shell concept and must not own unrelated business logic.

A future Active Technician Context may connect Company, User, Device, Ticket, Tenant and other working references without transferring domain ownership to the Workspace.

This plan specializes that approved direction. It must not silently redefine Foundation ownership.

---

## 4. Explicit USER Requirements

1. Avoid unnecessary independent desktop popup windows.
2. Prefer substantial tools living inside the primary F7Hub PySide6 app.
3. Tickets must remain quickly accessible from every major workspace.
4. Provide a Quick Ticket surface for rapid note/evidence entry without navigation ping-pong.
5. Main navigation buttons may expose temporary semi-transparent hover/click flyouts.
6. Flyouts must use reusable shell mechanics, not one custom popup implementation per module.
7. Plan every primary navigation button's flyout content before implementing those buttons.
8. Reserve DynamicHub for Mochi/contextual assistance, not main navigation.
9. Reserve future Mochi/DynamicHub space so module layouts do not consume it accidentally.
10. Reduce future GUI implementation cost through stable shell contracts.

---

## 5. Scope

Design:

```text
MainWindow shell
Technician Workspace
module hosting
main navigation
navigation flyouts
flyout content contract
Active Technician Context
Active Ticket Context
Quick Ticket Drawer
global search placement
global status placement
workspace tabs / activation
internal panel hosting
responsive behavior
focus behavior
keyboard behavior
accessibility
opacity / translucency policy
module-content descriptors
draft-preserving navigation
Mochi/DynamicHub reserved region
native validation strategy
future vertical-slice decomposition
```

---

## 6. Out of Scope

Do not implement:

```text
PySide6 production classes
MainWindow changes
flyout widgets
Quick Ticket UI
workspace tabs
database migrations
Settings implementation
RMM / Graph / Adobe integration
DynamicHub runtime
Mochi AI behavior
Clipboard Center
new Ticket business rules
PowerShell execution behavior
```

Do not create a general plugin framework unless repository inspection proves one is already appropriate.

---

## 7. Required Inspection

Before recommendations, inspect at minimum:

```text
ROOT.md
AGENTS.md
Docs/19_DocumentationIndex.md
Docs/05_GUI.md
Docs/06_SystemArchitecture.md
Docs/13_PythonArchitecture.md
Docs/14_DesignPrinciples.md
Docs/Planning/AGENTS.md
Docs/Planning/Foundation/0E_Foundation_Architecture_Reconciliation.md

Python/f7hub/gui/main_window.py
Python/f7hub/gui/ticket_workspace.py
Python/f7hub/gui/knowledge_workspace.py
Python/f7hub/gui/script_workspace.py
Python/f7hub/gui/service_task_runner.py
application bootstrap
current navigation/menu/toolbar code
current dialogs/status surfaces
current GUI tests
```

Inspect relevant Clipboard 1A/1B contracts and Mochi scoped guidance.

Use:

```text
SEARCH → IDENTIFY → REUSE / EXTEND → CREATE ONLY IF NECESSARY
```

Classify findings:

```text
FACT
ASSUMPTION
INFERENCE
RECOMMENDATION
NOT VERIFIED
```

---

## 8. Primary Shell Model

Evaluate this conceptual shell against the real MainWindow:

```text
┌───────────────────────────────────────────────────────────────────────┐
│ Main Toolbar / Search / Active Context / Global Actions              │
├───────────────┬───────────────────────────────────────────────────────┤
│ Main          │ Technician Workspace                                  │
│ Navigation    │                                                       │
│               │ Ticket | Clipboard | Diagnostics | Knowledge | ...   │
│ Dashboard     │                                                       │
│ Tickets       │ Current embedded workspace                            │
│ Clipboard     │                                                       │
│ Knowledge     │ Optional internal split panes / inspector             │
│ Diagnostics   │                                                       │
│ Scripts       │                                                       │
│ ...           │                                                       │
├───────────────┴───────────────────────────────────────────────────────┤
│ Status / Background Activity                                         │
└───────────────────────────────────────────────────────────────────────┘
```

The conceptual drawing is not an implementation mandate.

---

## 9. Technician Workspace Role

Potential shell responsibilities:

```text
module hosting
workspace tabs
tool activation
selection/context propagation
split panes
workspace restoration
focus routing
unsaved-draft protection
navigation requests
```

It must not own:

```text
Ticket rules
Clipboard lifecycle
Diagnostic execution
Knowledge persistence
PowerShell policy
Analytics calculations
Mochi reasoning
provider authorization
```

---

## 10. Workspace Hosting Decision

Evaluate:

```text
QStackedWidget / existing equivalent
QTabWidget / custom workspace tabs
QSplitter
non-floatable QDockWidget
slide-over/drawer panels
QMdiArea / QMdiSubWindow
```

Classic free-floating MDI should normally be rejected unless evidence justifies it because it increases z-order, overlap, focus, restoration, screenshot and small-screen complexity.

Prefer embedded/docked/tabbed tools inside the primary application.

---

## 11. Interaction Depth Model

### Level 1: Navigation Flyout

Fast navigation/glance/resume. No destructive action and no remote execution on hover.

### Level 2: Quick Internal Panel

Small task without leaving current workspace, e.g. Quick Ticket.

### Level 3: Full Technician Workspace

Substantial Ticket, Clipboard, Diagnostic, Knowledge, Script or other work.

Do not force every action into the same surface.

---

## 12. Active Technician Context

Design a shell/application context holding references such as:

```text
company_id
contact/user_id
device_id
ticket_id
tenant_id
session/case reference
```

Rules:

1. References, not duplicate domain records.
2. Owning domains revalidate references before use.
3. Context is not permission.
4. Context changes must not silently discard dirty drafts.
5. Stale references fail safely.
6. Context may be partially populated.
7. Context does not authorize remote execution.
8. Context supports navigation/deep-link use cases.

Search for existing `ApplicationContext`, navigation context or equivalent before creating anything new.

---

## 13. Active Ticket Context

Plan persistent compact Ticket visibility such as:

```text
INC-10452 | Contoso | Jane Smith | LT-042
[Quick Note] [Open Ticket]
```

Exact visuals are deferred.

The shell may expose:

```text
active ticket reference
safe short label
Quick Note
Open Full Ticket Workspace
Attach Current Result / Evidence entry points
```

All mutations route through Ticket application/services.

---

## 14. Quick Ticket Drawer

Plan an internal, non-modal drawer accessible from every major workspace.

Candidate contents:

```text
ticket identity
company/user/device summary
status
Quick Note
recent F7Hub-generated observations
attach current Clipboard item
attach current diagnostic result
attach KB reference
Open Full Ticket Workspace
```

Rules:

- inside MainWindow
- no separate app window
- never opens merely from hover
- dirty note drafts are protected
- failed saves retain draft
- ticket target is revalidated
- it does not become a second Ticket implementation

---

## 15. Main Navigation Contract

For every primary module define:

```text
module key
display label
icon
primary route
availability
badge/count policy
flyout availability
keyboard activation
capability dependency
```

One coherent main-navigation system owns mechanics.

---

## 16. Reusable Navigation Flyout Host

Design one reusable shell primitive, conceptually `NavigationFlyoutHost` or repository-conventional equivalent.

Shell owns:

```text
open/close mechanics
placement
focus behavior
opacity/theme
screen clamping
keyboard accessibility
one-flyout-at-a-time policy
```

Modules own:

```text
meaning of destinations
action availability
recent/pinned records
badges/status
```

Support sidebar flyout-right and top-navigation flyout-down through one placement policy where practical.

---

## 17. Flyout Interaction Rules

### Hover

Bounded open delay, recommended planning range:

```text
200–350 ms
```

### Pointer transfer

`trigger → flyout` must keep it open.

### Leave grace

Recommended planning range:

```text
300–500 ms
```

### Click

Primary button click should retain the module's primary navigation role unless a deliberate chevron/secondary affordance is approved.

### Keyboard / touch

All flyout contents must be reachable without hover.

### Focus

Hover-open should normally not steal keyboard focus. Escape closes. Only one navigation flyout at a time.

---

## 18. Flyout Appearance

The USER wants a temporary semi-transparent pane.

Recommended architecture target:

```text
background opacity approximately 85–95%
```

subject to theme, contrast, Windows composition, accessibility and native testing.

Text/icons remain readable. Blur/acrylic is optional polish, not a functional dependency.

Do not inherit AltF7Hub opacity policy automatically.

---

## 19. Standard Flyout Anatomy

```text
┌──────────────────────────────┐
│ CONTEXT                      │
│ current/active information   │
├──────────────────────────────┤
│ QUICK ACTIONS                │
│ 2–5 frequent operations      │
├──────────────────────────────┤
│ NAVIGATION / RECENT          │
│ destinations/items           │
├──────────────────────────────┤
│ OPEN FULL WORKSPACE          │
└──────────────────────────────┘
```

Sections may be omitted when irrelevant.

---

## 20. Flyout Content Item Contract

Conceptually define:

```text
item key
label
icon
item type
route/action key
owner subsystem
availability
enabled state
disabled reason
badge
safe summary
keyboard behavior
privacy classification
```

Possible item types:

```text
NAVIGATION
QUICK_ACTION
RECENT_RECORD
PINNED_RECORD
STATUS
SEPARATOR
OPEN_WORKSPACE
```

Never put arbitrary executable command strings in shell descriptors.

---

## 21. Candidate Main Sections

Verify actual inventory before finalizing:

```text
Dashboard
Tickets
Companies / Users / Devices
Clipboard
Knowledge
Diagnostics
Scripts / Automation
Applications / Websites
Search
Analytics / Reports
Settings
Mochi / AI
```

Unavailable/future modules must be marked honestly.

---

## 22. Dashboard Flyout

Candidate context:

```text
active Ticket
active user/device
important current status
```

Quick actions:

```text
Resume Active Ticket
Quick Note
Global Search
```

Dynamic content:

```text
Today
Recent Activity
Recent Tickets
Important Alerts
```

Do not create a second Analytics dashboard.

---

## 23. Tickets Flyout

Context:

```text
Active Ticket
status
company/user/device
```

Quick actions:

```text
Quick Note
New Ticket
Open Active Ticket
Attach Current Context
```

Navigation candidates:

```text
Active
Waiting Customer
Waiting Vendor
Recent
History
```

Use actual Ticket states from the domain.

---

## 24. Companies / Users / Devices Flyout

Candidate context:

```text
active company
active user
active device
tenant
```

Quick actions:

```text
Open Active Record
Search User
Search Device
Copy approved identity field
```

Dynamic content:

```text
recent companies
recent users
recent devices
```

Respect privacy.

---

## 25. Clipboard Flyout

Consume approved Clipboard architecture.

Context:

```text
last/current capture result
active Clipboard item
```

Quick actions:

```text
Capture Current
Save
Pin
Open Clipboard Center
```

Navigation candidates:

```text
Recent
Saved
Pinned
URLs
Ticket Evidence
Diagnostic Evidence
```

Do not duplicate Clipboard lifecycle logic.

---

## 26. Knowledge Flyout

Context:

```text
current article
current query
```

Quick actions:

```text
Search
Create Draft
Open Current Article
```

Dynamic content:

```text
Recent
Favorites
Drafts
Categories
```

---

## 27. Diagnostics Flyout

Context:

```text
active target
latest diagnostic/result
```

Potential categories:

```text
Network
Device
Microsoft 365
Security
```

Quick actions must come from approved diagnostics/action catalogs.

Hover never executes remote or PowerShell work.

---

## 28. Scripts / Automation Flyout

Context:

```text
active target
capability/availability
```

Dynamic content:

```text
approved favorites
recent safe actions
Open Scripts Workspace
```

No raw script text as an executable flyout payload.

---

## 29. Applications / Websites Flyout

Candidate contents:

```text
Favorites
Recent
Categories
Launch/Open
```

Reuse approved records. Do not hard-code a parallel registry in shell code.

---

## 30. Search Flyout

Candidate contents:

```text
Global Search
recent queries
scoped searches
```

Do not persist search history without privacy/Settings approval.

---

## 31. Analytics / Reports Flyout

Context:

```text
active Ticket / Company
```

Quick actions:

```text
Open relevant report
Open drill-down
```

Dynamic content:

```text
Recent Reports
Pinned Reports
```

No Analytics calculation in shell code.

---

## 32. Settings Flyout

Candidate navigation:

```text
General
Appearance
Hotkeys
Clipboard
Integrations
Mochi / AI
Privacy
```

Final sections follow approved Settings definitions. Avoid fake Settings behavior before the shared Settings service exists.

---

## 33. Mochi / AI Flyout

Keep this minimal because DynamicHub is the richer contextual action surface.

Candidate items:

```text
Show Mochi
Hide Mochi
Pause / Resume
Open Context Surface
Settings
```

Do not duplicate DynamicHub action recommendations in a navigation flyout.

---

## 34. F7Hub Navigation Surface Matrix

The final plan MUST contain one authoritative row per primary main-navigation button.

Required columns:

```text
Module
Primary route
Context header
Quick actions
Navigation items
Recent/pinned provider
Badge/count
Empty state
Unavailable state
Hover behavior
Click behavior
Keyboard behavior
Privacy considerations
Capability dependencies
Owning service(s)
MVP / Later
```

No later main-navigation button should be implemented without a row here or a reviewed update.

---

## 35. Module Descriptor Concept

Evaluate a lightweight presentation descriptor such as:

```text
ModuleNavigationDescriptor
```

Potential metadata:

```text
module_key
label
icon_key
primary_route
flyout_groups
badge_provider
availability_provider
```

This is not automatically a plugin system. Search for an existing navigation/module registry first.

---

## 36. Workspace Tabs

Evaluate internal tabs for substantial tools:

```text
Ticket
Clipboard
Diagnostics
Knowledge
Scripts
```

Decide:

```text
one instance per module?
multiple Ticket tabs?
draft protection?
tab restoration?
close rules?
context synchronization?
```

Do not default to unlimited browser-like tabs without evidence.

---

## 37. Full Ticket Workspace

Ticket Workspace remains the deep-work Ticket surface.

Shell provides activation/routing/Active Ticket/Quick Ticket only.

It does not duplicate status rules, note persistence, history, relationships or validation.

---

## 38. Global Search

Define one shell-level Global Search entry point and how it routes into module-specific results.

Do not make every flyout another full search engine.

---

## 39. Status / Background Activity

Plan one coherent non-modal shell surface for:

```text
background loads
completed actions
recoverable failures
provider unavailable states
```

DynamicHub/Mochi acknowledgements remain a separate contextual-assistant presentation concern.

---

## 40. Draft Preservation

Navigation, flyouts, workspace tabs and Quick Ticket must respect dirty-draft protection.

Required scenarios include:

```text
Ticket note draft
Ticket field draft
Knowledge draft
future Clipboard interaction state
pending write/dialog
```

Never silently discard user work.

---

## 41. Responsive Shell

Document:

```text
WIDE
MEDIUM
MINIMUM SUPPORTED
```

For each define behavior of:

```text
main navigation
workspace tabs
Active Context
Quick Ticket Drawer
Mochi reserved region
Inspector/right-side regions
flyouts
```

Flyouts clamp inside available screen/application bounds.

---

## 42. Multi-Monitor / DPI

Future native validation must cover:

```text
100%
125%
150%
high DPI where practical
monitor-edge placement
negative coordinates
mixed-DPI transitions where supported
taskbar boundaries
```

---

## 43. Keyboard Model

Inventory existing bindings first.

Plan shell behavior for:

```text
main navigation
global search
Quick Ticket
workspace cycling
closing transient panels
flyout keyboard access
```

Do not steal normal editable-widget shortcuts.

`Win+Alt+C` remains Clipboard capture authority from Clipboard 1B.

---

## 44. Accessibility

Require:

```text
non-hover access
visible focus
logical Tab order
accessible names
non-color-only status
sufficient contrast
keyboard-close behavior
disabled-state explanation
```

Semi-transparency must not reduce readability below acceptable contrast.

---

## 45. Security / Authority

Shell UI never grants authority merely by showing an action.

Shell must not:

```text
write SQLite directly
run PowerShell directly
call RMM directly from widgets
store secrets
infer permission from visibility
trust stale context blindly
```

Meaningful actions route through owning application/service boundaries.

---

## 46. Settings Inputs

Evaluate future shared Settings needs:

```text
navigation style
flyout enabled
hover delay
flyout opacity
Quick Ticket preference
workspace restoration
panel-collapse preferences
```

Classify:

```text
CORE
LIKELY
FUTURE
NOT NEEDED
```

Do not turn all transient UI state into persistent Settings.

---

## 47. Performance

Opening/hovering a flyout must not trigger:

```text
RMM request
Graph request
heavy database aggregation
AI inference
large record load
```

Flyout data should be already available, cached/bounded or asynchronously loaded.

Remote/provider work requires explicit action.

---

## 48. Error / Unavailable States

Every flyout needs truthful states for:

```text
module unavailable
service unavailable
no active context
no recent records
loading
partial data
permission denied
```

No fake enabled actions.

---

## 49. Required Diagrams

Produce Mermaid source for:

1. Main shell ownership.
2. Technician Workspace hosting.
3. Active Technician Context propagation.
4. Main navigation → flyout → route/action flow.
5. Quick Ticket Drawer → TicketService flow.
6. Responsive shell variants.

---

## 50. Required Reuse Assessment

Classify actual components:

```text
MainWindow
QStackedWidget/workspace host
toolbar
menus
navigation
ServiceTaskRunner
status surface
TicketWorkspace
KnowledgeWorkspace
ScriptWorkspace
dialogs
splitters
navigation helpers
draft protection
Mochi integration
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

## 51. Decision Register

At minimum decide:

```text
primary workspace-host pattern
MDI rejection/acceptance
workspace tabs
Active Technician Context ownership
Active Ticket visibility
Quick Ticket Drawer
main-navigation placement
flyout trigger behavior
flyout focus policy
flyout opacity policy
flyout anatomy
module-descriptor approach
global search placement
status surface
right-side/Mochi reservation
responsive collapse
workspace restoration
```

Record:

```text
Decision
Options
Recommendation
Evidence
Rationale
Consequences
Planning depth
Status
```

Allowed statuses:

```text
RECOMMENDED
REQUIRES_USER_DECISION
DEFERRED
NOT_VERIFIED
```

---

## 52. Risk Register

At minimum include:

```text
nested navigation
excess horizontal width
flyout flicker
hover-only accessibility
focus theft
draft loss
module-specific duplication
stale Active Context
wrong Ticket target
too many actions
provider calls on hover
semi-transparent readability
DPI popup placement
multi-monitor placement
Mochi/right-panel competition
workspace-tab sprawl
slow startup
over-engineered plugin/descriptor model
testing loops
```

Record Risk, Likelihood, Impact, Mitigation, Residual Risk, Owner and Status.

---

## 53. Future Implementation Slice Strategy

May recommend, but not implement, small slices such as:

```text
SHELL-01 navigation descriptor + tests
SHELL-02 reusable flyout mechanics
SHELL-03 one low-risk flyout vertical slice
SHELL-04 Active Technician Context
SHELL-05 Active Ticket shell indicator
SHELL-06 Quick Ticket Drawer
SHELL-07 workspace-tab host
SHELL-08 responsive/panel restoration
SHELL-09 remaining module flyout content
SHELL-10 native accessibility/DPI/focus hardening
```

Actual numbering follows repository governance.

Never implement every flyout in one giant slice.

---

## 54. Acceptance Criteria

S1 is acceptable when:

1. Existing MainWindow/navigation architecture inspected.
2. Existing workspaces inspected.
3. Existing draft-protection patterns inspected.
4. Technician Workspace role explicit.
5. Workspace ownership does not absorb domains.
6. Primary workspace-host pattern recommended.
7. Classic MDI explicitly evaluated.
8. Main navigation architecture defined.
9. Reusable flyout mechanics defined.
10. Hover is not the only access method.
11. Flyout focus behavior defined.
12. Flyout opacity/readability defined.
13. Flyout timing bounded.
14. Flyout content anatomy defined.
15. Navigation Surface Matrix complete.
16. Tickets flyout defined.
17. Clipboard flyout defined.
18. Knowledge flyout defined.
19. Diagnostics flyout defined.
20. Scripts/Automation flyout defined.
21. Settings flyout defined.
22. Mochi flyout boundary defined.
23. Active Technician Context defined.
24. Active Ticket Context defined.
25. Quick Ticket Drawer defined.
26. Ticket mutations remain Ticket-owned.
27. Global Search placement defined.
28. Workspace tab strategy defined.
29. Responsive shell behavior defined.
30. Mochi/DynamicHub space reserved.
31. Keyboard model defined.
32. Accessibility requirements defined.
33. DPI/multi-monitor validation planned.
34. Settings inputs classified.
35. Hover does not trigger provider work.
36. Security/authority preserved.
37. Reuse assessment complete.
38. Decision register complete.
39. Risk register complete.
40. Future slices small/reviewable.
41. No production implementation occurred.
42. No database change occurred.
43. Foundation ownership not silently redefined.
44. Clipboard 1C can consume S1 without inventing shell behavior.

For a positive result:

```text
44/44 PASS
```

at architecture-planning depth.

---

## 55. Required Validation Summary

```text
Current shell inspection                 PASS / FAIL / BLOCKED
Technician Workspace architecture        PASS / FAIL / BLOCKED
Workspace hosting                        PASS / FAIL / BLOCKED
Main navigation                          PASS / FAIL / BLOCKED
Flyout mechanics                         PASS / FAIL / BLOCKED
Flyout content matrix                    PASS / FAIL / BLOCKED
Active Technician Context                PASS / FAIL / BLOCKED
Active Ticket Context                    PASS / FAIL / BLOCKED
Quick Ticket Drawer                      PASS / FAIL / BLOCKED
Draft preservation                       PASS / FAIL / BLOCKED
Responsive layout                        PASS / FAIL / BLOCKED
Keyboard/accessibility                   PASS / FAIL / BLOCKED
DPI/multi-monitor plan                   PASS / FAIL / BLOCKED
Mochi/DynamicHub coexistence             PASS / FAIL / BLOCKED
Settings boundary                        PASS / FAIL / BLOCKED
Security/authority                       PASS / FAIL / BLOCKED
Reuse assessment                         PASS / FAIL / BLOCKED
Scope control                            PASS / FAIL / BLOCKED
Production changes                       MUST BE NONE
Database changes                         MUST BE NONE
```

---

## 56. Required Execution Report

When executed, append `# EXECUTION REPORT` with at minimum:

```text
Summary
Baseline / Candidate Identity
Approved Inputs
Repository Areas Inspected
Verified Current Shell
Reuse Assessment
Technician Workspace
MainWindow Integration
Workspace Hosting
Active Technician Context
Active Ticket Context
Quick Ticket Drawer
Main Navigation
Flyout Mechanics
Flyout Content Contract
F7Hub Navigation Surface Matrix
Workspace Tabs
Global Search
Status / Background Activity
Draft Preservation
Responsive Layout
Keyboard & Accessibility
DPI / Multi-Monitor
Mochi / DynamicHub Reserved Region
Settings Inputs
Security / Authority
Required Diagrams
Decision Register
Requires User Decision
Assumptions
Not Verified
Risk Register
Recommended Vertical Slices
Downstream Clipboard 1C Inputs
Acceptance Criteria
Validation
Result
```

---

## 57. Result Vocabulary

Return exactly one:

```text
READY_FOR_WORKSPACE_REVIEW
REQUIRES_WORKSPACE_DECISIONS
BLOCKED
```

Never return `READY_FOR_IMPLEMENTATION`.

---

## 58. Completion Boundary

STOP after producing the exact planning candidate.

Do not stage, commit, push, merge, implement MainWindow, create flyout widgets, create Quick Ticket, create Active Context services, start S2 automatically, start Clipboard 1C automatically or create Workspace AGENTS.md automatically.

Next gate:

```text
INDEPENDENT S1 ARCHITECTURE REVIEW
→ explicit USER approval
→ controlled integration
```
