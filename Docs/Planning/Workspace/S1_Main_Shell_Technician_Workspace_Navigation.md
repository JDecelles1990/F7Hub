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

# EXECUTION REPORT

## Summary

RECOMMENDATION: extend the existing MainWindow and QStackedWidget into a bounded Technician Workspace shell. Retain one instance per module, use a left navigation rail with one shared flyout host, keep a compact Active Ticket control reachable in every major workspace, and offer a Ticket-owned Quick Note through one internal Quick Ticket Drawer. A single mutually exclusive auxiliary region accommodates module inspectors, Quick Ticket and future Mochi/DynamicHub content. No classic MDI, unlimited document tabs, plugin loader, global event bus or second domain implementation is required.

Planning status: READY_FOR_REVIEW. Result: READY_FOR_WORKSPACE_REVIEW. These are author-side architecture conclusions, not independent approval, integration, implementation or runtime verification. The original NOT_STARTED contract above is preserved historical input; this appended report records its execution on 2026-10-07, America/Toronto.

FACT: only the allowlisted S1 document is changed. Production source, database, tests, configuration, S2 and Clipboard 1C are unchanged. This report offers recommendations for subsequent review; none is implemented by this task.

## Baseline / Candidate Identity

| Field | Inspected identity / boundary |
| --- | --- |
| Canonical workspace | C:\Dev\F7Hub |
| Initial branch | main |
| Initial HEAD / main / origin/main / live remote main | f005949dbeaaf6a17029a8c1d4d74c0adb9b62c0, all equal; verified with rev-parse and ls-remote, then fetch before branch creation |
| Execution branch | docs/workspace-s1-execution-20261007; absent at inspection, created from verified main |
| Target | Docs/Planning/Workspace/S1_Main_Shell_Technician_Workspace_Navigation.md |
| Target baseline Git blob | 3ffb0f5ac3b5fe2e8d2ecd1455f72bd66870d15f |
| Original raw checkout | 29,694 bytes; SHA256 af005c7ebc5c86a6cccf854e80f839e37fd56895a8b42adc3443f4b460b6094d; UTF-8 without BOM; CRLF; final newline present |
| Baseline safety | No tracked or staged changes; sole untracked pathname AutoHotkey/Troubleshooting_Sections/GuideSettings.ini |
| Protected path handling | Observed only in ordinary Git pathname inventory; no open/read/hash/metadata/edit/cleanup/staging |
| Candidate lifecycle | UNAPPROVED / UNSTAGED / UNCOMMITTED / UNPUSHED / NOT INTEGRATED |
| Final identity location | Final response after the last edit: raw SHA256, Git-normalized blob, byte count, newline/final-newline state and diff counts; no self-referential final hash in this document |

Original contract preservation is tested two ways: exact raw prefix length/hash against the initial checkout and LF-normalized prefix comparison against the integrated baseline Git blob. Different CRLF checkout and LF Git bytes are distinguished.

## Approved Inputs

FACT: current dependency closure is established from Git ancestry and fresh read-only GitHub merged-PR records, not historical author-side wording. PR bodies are integration records reporting independent review and explicit USER approval; no separate chat-history audit is claimed.

| Input | Reverified review / integration evidence | Status for S1 |
| --- | --- | --- |
| Foundation 0A | [PR 66](https://github.com/JDecelles1990/F7Hub/pull/66); merge 1a7015b500fc0eccbab749e82585c7936d5cb478; explicit USER approval including 0A-D1/0A-D2 ownership and exact-candidate integration review recorded | CLOSED |
| Foundation 0B | [PR 67](https://github.com/JDecelles1990/F7Hub/pull/67); merge 41d49d6644727cb324be24e05fda6738cd782eb6; APPROVE and USER integration approval recorded | CLOSED |
| Foundation 0C | [PR 68](https://github.com/JDecelles1990/F7Hub/pull/68); merge 3d0dd673798852941b6fd690cd290dd2ba8c61de; corrected rereview APPROVE and USER approval recorded | CLOSED |
| Foundation 0D | [PR 70](https://github.com/JDecelles1990/F7Hub/pull/70); merge 4c4ecb19022bb2906b56d15f15316f6594bcabcf; APPROVE_WITH_NOTES and USER approval recorded | CLOSED |
| Foundation 0E | [PR 71](https://github.com/JDecelles1990/F7Hub/pull/71); merge 69176c2801329fef2f107a35129337c9394b2aa4; reconciliation APPROVE_WITH_NOTES, 20/20 and USER approval recorded; closes 0A-0E | CLOSED |
| Clipboard 1A | [PR 72](https://github.com/JDecelles1990/F7Hub/pull/72); merge db7b7b387806fce786a05ee3f9bc14ee29cdbd60; APPROVE, 30/30 and explicit USER approval recorded | CLOSED |
| Clipboard 1B | [PR 73](https://github.com/JDecelles1990/F7Hub/pull/73); merge d22b001aea9957dd28bfc1af6450934a110aa0e6; approved exact candidate, independent APPROVE_WITH_NOTES, 23/23 recorded; subsequent authorized S1 contract names 1B CLOSED | CLOSED |
| S1/S2 contracts | [PR 75](https://github.com/JDecelles1990/F7Hub/pull/75); merge f005949dbeaaf6a17029a8c1d4d74c0adb9b62c0; planning contracts integrated, executions explicitly not completed | S1 execution authorized by this task; S2 NOT EXECUTED |

All listed merge commits are present in current main ancestry. Fresh records match the user's expected dependency history. Historical UNAPPROVED / NOT INTEGRATED / next independent review text in upstream execution reports describes those authors' original candidates; it does not undo later integration. Dependency gate: PASS.

Authoritative architectural inputs are [0A](../Foundation/0A_Master_Foundation_Architectural_Contract.md), [0B](../Foundation/0B_Global_JSON_Contract_Interoperability_Grammar.md), [0C](../Foundation/0C_Taxonomy_Information_Vocabulary.md), [0D](../Foundation/0D_Settings_Architecture.md) and [0E](../Foundation/0E_Foundation_Architecture_Reconciliation.md). S1 specializes presentation/activation and application-selected context. Source domains retain records, relationships, evidence and execution authority; 0D separates runtime selection from preferences. [Clipboard 1A](../Clipboard/1A_Clipboard_Domain_Data_Lifecycle.md) owns Item/Event/Save/Pin/Evidence/privacy; [Clipboard 1B](../Clipboard/1B_AHK_Python_Clipboard_Capture_IPC_Quick_HUD_Architecture.md) owns capture/IPC/HUD and Win+Alt+C. The [S2 contract](S2_Mochi_DynamicHub_Context_Actions.md) is read only for its reserved-region and invocation-context compatibility requirements, not executed or adopted as approved action semantics.

## Repository Areas Inspected

Inspected source establishes FACT about code, not verified runtime behavior. Evidence keys below keep recommendations traceable without reproducing entire owner documents.

| Key | Area / inspected content | Evidence use |
| --- | --- | --- |
| G | [AGENTS](../../../AGENTS.md), [ROOT](../../../ROOT.md), [router](../../19_DocumentationIndex.md), [Planning guidance](../AGENTS.md), [Foundation guidance](../Foundation/AGENTS.md) | Scope, routing, labels, ownership and lifecycle |
| C | [GUI](../../05_GUI.md), [System architecture](../../06_SystemArchitecture.md), [Python architecture](../../13_PythonArchitecture.md), [Design principles](../../14_DesignPrinciples.md) | Current slice notes; intended controlled stack/tab model; shell/service boundaries; reuse, responsiveness and explicit composition |
| F | Foundation inputs linked above, especially 0E Shared Context / Authority Matrix / Downstream Contract and 0D runtime-state distinction | No duplicate identity, taxonomy, configuration or context authority |
| B | Clipboard 1A lifecycle/privacy/service/downstream sections; 1B Quick HUD / Action Routing / Availability / native requirements / 1C inputs | Typed refs, safe projections, source eligibility, explicit target, no command-derived execution |
| E-M | [MainWindow](../../../Python/f7hub/gui/main_window.py), construction through closeEvent | Actual stack, menus/toolbar, routes, busy protection, startup, status and closing |
| E-T | [TicketWorkspace](../../../Python/f7hub/gui/ticket_workspace.py), layout, has_draft/confirm_discard/open_ticket/add_note/_reload_after_save; [creation widget](../../../Python/f7hub/gui/ticket_create_widget.py), draft and shortcut boundaries | Ticket split host, detail tabs, note editor, context/creation transitions and pending ownership |
| E-K | [KnowledgeWorkspace](../../../Python/f7hub/gui/knowledge_workspace.py), construction, filters, search, dialogs and article routing; [new article dialog](../../../Python/f7hub/gui/new_article_dialog.py), [edit article dialog](../../../Python/f7hub/gui/edit_article_dialog.py) | Independent filter runners; input preservation and conflict token; no common shell draft participant |
| E-S | [ScriptWorkspace](../../../Python/f7hub/gui/script_workspace.py), catalog/search/copy/run/pack/result/pending paths | Existing diagnostic home, immutable run identity, current results in memory |
| E-R | [ServiceTaskRunner](../../../Python/f7hub/gui/service_task_runner.py), all source | Single-task QThread dispatch; GUI-thread callbacks; busy false before callback |
| E-A | [bootstrap](../../../Python/f7hub/app/bootstrap.py), [app main](../../../Python/f7hub/app/main.py) | Explicit dependency composition; frozen ApplicationContext holds services, not selected records |
| E-D | [TicketService](../../../Python/f7hub/services/ticket_service.py), read/note/classification/status methods; [TicketKnowledgeService](../../../Python/f7hub/services/ticket_knowledge_service.py), link/read methods | Owner validation, transactions, real status vocabulary; RELATED KB link is not generic evidence |
| E-P | [PowerShell guidance](../../../PowerShell/AGENTS.md), [execution architecture](../../12_PowerShellArchitecture.md), E-S/service call sites | Preserve registered/sealed bounded execution through owning service/gateway |
| E-O | [Mochi guidance](../../../Mochi/AGENTS.md), [README](../../../Mochi/README.md), MVP headings/scope; [MochiService](../../../Python/f7hub/services/mochi_service.py), [Mochi controls](../../../Python/f7hub/gui/mochi_settings_dialog.py) | Current cosmetic/control boundary, no business context/AI assumed |
| E-H | [AltF7Hub guidance](../../../AutoHotkey/Troubleshooting_Sections/AGENTS.md), [README entry/keyboard rules](../../../AutoHotkey/Troubleshooting_Sections/README.md), E-M fixed service route | Preserve independent guide's show/focus boundary; no guide runtime redesign or settings inspection |
| T | [MainWindow tests](../../../Tests/GUI/test_main_window.py), [script execution tests](../../../Tests/GUI/test_script_execution.py), [Ticket creation integration](../../../Tests/Integration/test_ticket_workspace_creation.py), Ticket flow and Knowledge GUI test inventory | Existing source assertions for 1000x700, failed-save drafts, callback gaps, stale completion and close guards; inspected, NOT RUN |
| Q | Official Qt for Python 6 references, checked read-only during task | Stack/MDI/geometry/translucency constraints; not proof of installed-version/native behavior |

Searches covered Python GUI/app/services, relevant domain/schema filenames, Tests GUI/Integration, tracked native/smoke filenames and required planning owners before proposing shared context, descriptors, flyouts or Quick Ticket. FACT: inspected MainWindow and Mochi GUI tests default QT_QPA_PLATFORM to offscreen; their source assertions do not constitute native Windows GUI evidence. Native QTest/96-DPI findings in current canonical slice notes are historical, not retained S1 runtime results; new-shell native validation remains NOT RUN. No operational database, provider session, external DynamicHub prototype or protected INI was inspected. No extra project architecture skill was found in .agents/skills; the existing delivery skill's Git-safety reference was used narrowly, not as implementation authority.

## Verified Current Shell

| Current-state statement | Classification / evidence |
| --- | --- |
| MainWindow is a QMainWindow whose central widget is QStackedWidget; retained TicketWorkspace plus optional KnowledgeWorkspace and ScriptWorkspace are constructed once | FACT, E-M / E-A |
| File menu and Tickets-named toolbar contain Tickets, Knowledge Base, Scripts, AltF7Hub Guide and database backup; Settings menu exposes Mochi; Exit uses Qt StandardKey.Quit | FACT, E-M; these are the actual menu/toolbar inventory, not an implemented 12-module sidebar |
| Initial Tickets load is scheduled after show; Knowledge/Scripts activation refreshes their lists; Ticket-linked article navigation calls MainWindow.open_knowledge_article and KnowledgeWorkspace.open_article_by_id | FACT, E-M / E-K |
| Ticket uses a queue/detail splitter, an internal detail/creation stack and five detail tabs: Details, Notes, History & timeline, Knowledge, Company; Quick Note remains in saved Ticket detail | FACT, E-T; these record-detail tabs are not shell workspace tabs |
| Knowledge and Scripts use internal splitters; Scripts currently includes reviewed diagnostic Run, baseline pack and plain-text memory-only results | FACT, E-K / E-S; a separate Diagnostics workspace is not implemented in this composition |
| MainWindow's shared runner globally disables pages/navigation for work; note/creation/status/classification and diagnostic pending flags span completion gaps; Knowledge also has separate filter/tag runners | FACT, E-M / E-R / E-K; replacing runner.busy with a simplistic global ready flag would regress protection |
| Ticket departure to Knowledge/Scripts asks Discard/Cancel, then clears drafts; opening a different Ticket guards draft replacement; close also protects the creation form and pending work | FACT, E-M / E-T; retained no-discard module switching is a proposed improvement, not current behavior |
| Knowledge create/edit dialogs preserve fields on save failure and block close while submitting; idle reject/close does not provide a common dirty-discard prompt | FACT, inspected dialog reject/closeEvent; a universal draft coordinator does not exist here |
| ApplicationContext is frozen dependency composition; inspected searches found no shared mutable Active Technician Context, navigation descriptor/flyout host or shell Quick Ticket Drawer | FACT within searched tracked areas, E-A plus source searches; no claim about external prototypes |
| Status bar currently shows Ready/Working and completion messages; workspace labels carry local feedback | FACT, E-M / E-T / E-K / E-S |
| Mochi has application-session control/state and a modeless control dialog; context-aware suggestions, DynamicHub and external AI are not current shell capabilities | FACT for inspected integration; future capability/runtime NOT VERIFIED, E-O / F |
| Native suitability, screen-reader behavior, DPI transitions, transparency performance and physical keyboard interaction of this proposed shell | NOT VERIFIED; current tests/docs are evidence of source/prior work only |

## Reuse Assessment

| Component | Current responsibility / layer and dependencies | Consumers / inspected tests | Treatment and architectural fitness |
| --- | --- | --- | --- |
| MainWindow | GUI composition/menus/status/navigation; injected services, no Ticket rules | All hosted tools; T | EXTEND: retain QMainWindow and its integration routes; delegate growing mechanics to small presentation helpers |
| QStackedWidget host | Central singleton page visibility | Ticket/Knowledge/Script, MainWindow tests | REUSE: suitable primary host; wrap with shell chrome rather than replace tools |
| Toolbar | Current module and utility QAction entry points | MainWindow tests | EXTEND: compact global search/context/tool commands; one underlying action per route; rail becomes primary module selector |
| Menus | Accessible application actions and Exit/Mochi | MainWindow/Mochi tests | REUSE / EXTEND: alternate keyboard access, preserve backup and guide actions; avoid duplicate action state |
| Main navigation | Hard-coded show_tickets/show_knowledge/show_scripts | T plus Ticket-linked KB flow | EXTEND: typed guarded route adapter over existing methods, not a new plugin router |
| Status bar / workspace feedback | Ready/Working/completion plus per-tool details | MainWindow and save-failure tests | EXTEND: operation-keyed safe summaries; owning tool retains detailed errors/outcomes |
| ServiceTaskRunner | One asynchronous service call; GUI-thread completion | Every main tool; pending-gap tests | REUSE: keep ownership guards through callbacks; no new global scheduler or unbounded queue |
| TicketWorkspace | Ticket deep-work presentation via TicketService/link service | Ticket GUI/integration tests | EXTEND: draft/activation adapter and shared note presentation; preserve field/status/race logic |
| KnowledgeWorkspace | KB queries, filters, article detail/dialogs via KnowledgeService | Knowledge GUI/flow tests | EXTEND: draft/dialog participant and guarded route adapter; keep independent filter runners visible to lifecycle checks |
| ScriptWorkspace | Registry/copy/diagnostics via ScriptService/PowerShellService | Scripts/run tests | REUSE / EXTEND: read-only cached flyout projection and route adapter; result target remains run-owned |
| Dialogs | Ticket fields, Knowledge drafts/filtering, script management, Mochi controls | Relevant GUI tests | REUSE / EXTEND: retain focused editors; require dirty/pending registration before shell close/hide/replacement; do not move every dialog into a new framework |
| Internal QSplitter | Queue/detail and list/detail sizing | Current 1000x700 assertions | REUSE / EXTEND: module owns splitter and compact fallback; shell owns outer width budget |
| Navigation helpers | MainWindow methods and Ticket-to-KB signal | Existing cross-module tests | EXTEND: validated intent plus draft guard; no arbitrary callback or shell command in route data |
| Draft protection | Ticket has_draft/confirm_discard, creation has_draft and pending flags; dialog-local tokens | Save-failure/close tests | EXTEND: small participant contract; no new persisted draft database implied |
| Mochi integration | Session service/gateway and single modeless dialog | Mochi controls tests | REUSE: cosmetic v1 unchanged; S2 owns later context/actions |
| Active Technician Context | No equivalent selected-reference owner found; ApplicationContext only composes dependencies | New future focused tests required | NEW: minimal application-owned selected-reference state, explicitly injected; do not repurpose frozen composition as global mutable state |
| Flyout host / descriptors / Quick Ticket shell container | No shared equivalent found in searched GUI | Future pure/GUI/native tests | NEW: bounded presentation mechanics; owning services reused for content/effects |
| General plugin loader, event bus, command executor, generic job registry, new settings store | No demonstrated shell requirement | None required for S1 | NOT NEEDED: adds authority/cost without current use case |
| Device/Tenant/recent/favorite/global search APIs, new diagnostic history/evidence associations | No implemented shell consumer/service established in inspected inventory | Future feature-specific inspection | NOT VERIFIED as runtime capabilities; unavailable until owner implementation exists |

## Technician Workspace

RECOMMENDATION: Technician Workspace names the substantial central application work host, not a dashboard, domain service or additional desktop window. MainWindow owns its lifetime; a small presentation coordinator owns activation/layout/focus/participant negotiation. Feature widgets retain their services and draft owners. Exact class filenames are implementation detail, not required production changes.

Activation uses module key plus an optional typed record/filter route. Each module has one retained widget instance and one remembered valid focus target. A module change hides, rather than reconstructs, the old tool; safe retention must first be implemented and tested through its draft adapter. Existing destructive show_knowledge/show_scripts behavior cannot be called unchanged to claim retained-draft navigation. Existing ticket/article/service entry points remain the adapter destinations after their guards are reconciled.

Tool lifecycle is bounded: compose existing services centrally, construct existing pages as today, activate only after availability/guard checks, perform a bounded explicit local read when necessary, suspend timers/subscriptions that are irrelevant while hidden, and dispose on approved close. Later heavy tools can be lazily constructed after review without delaying basic Tickets startup. Hidden tools still report pending writes/dirty state. Shutdown never destroys a worker or silently abandons a committed operation.

Selection propagation is deliberate. Browsing a row is local preview; explicit successful Open/Use as active publishes selected context. Module activation alone does not replace the active Ticket or reinterpret the last diagnostic target. Split panes remain module-owned; the shell permits one auxiliary region and no second simultaneous main-module instance. Navigation history, if introduced, stores bounded in-memory typed routes only and revalidates availability/record identity on traversal.

Restoration has two boundaries: session retention of instantiated tools is CORE; cross-process layout preference restoration is FUTURE through 0D. No draft text, Ticket/customer identity, queries, clipboard refs, provider handles or pending writes are restored automatically after process restart. Startup retains today's Tickets destination until a separately approved nonsensitive module preference is supported.

## MainWindow Integration

RECOMMENDATION: retain menu/status/native window ownership and service injection. Extend central composition to a horizontal layout of navigation rail, Technician Workspace stack, and optional auxiliary region; add a compact top search/context row. Reuse QAction route identities between menu, rail, toolbar and flyout. Utilities such as local backup, existing AltF7Hub Guide and Mochi controls remain reachable through their existing owning services; they do not become new independent main workspaces.

The integration seam is a conceptual request_navigation(module_key, route_key, typed_reference, focus_intent) presentation API. It rejects unknown keys/unsafe arguments, checks composed capability, negotiates all affected participants, resolves the owner record, then commits activation/context together. No model key is interpreted as a Python import, arbitrary callback, executable path, URL or command string. Source services do not import the shell to navigate; modules signal an intent and the application adapts it on the GUI thread.

Read/navigation outcome differs from mutation outcome: refused route preserves page/context/focus; a read failure preserves existing drafts and shows safe feedback; a committed write followed by failed refresh says Saved; refresh unavailable and retries only the read. Future routing from authenticated Clipboard 1B ingress reaches this same guard on the GUI thread. A navigation acknowledgement is not proof of capture, save or evidence attachment, and no IPC contract is redesigned here.

## Workspace Hosting

| Pattern evaluated | Focus / restoration / overlap / sizing / testing implications | Recommendation |
| --- | --- | --- |
| Existing QStackedWidget | One visible module, stable retained identity, simple route/focus restoration, no internal window z-order; module minimum size still needs compact layouts | PRIMARY REUSE; best fit for inspected singleton tools |
| QTabWidget / custom workspace tabs | Extra second navigation row and close/dirty/record lifecycle; existing Ticket detail tabs remain legitimate | No shell tab row in MVP; optional bounded singleton selector later if real workflow proves benefit |
| QSplitter | Predictable resize and no floating windows; simultaneous panes consume central width | REUSE inside tools and optional outer wide auxiliary split; not a competing module host |
| Non-floatable QDockWidget | Supports controlled ancillary areas; docking/reordering/state restoration still adds complexity | Valid later ancillary implementation option, no primary tool docks/rearrangement in MVP |
| Internal drawer | Non-modal focused quick task; occlusion and draft/focus management must be explicit | NEW Quick Ticket/shared auxiliary surface; narrow full-width internal panel if necessary |
| QMdiArea / QMdiSubWindow, including tabbed mode | Classic child windows add activation, overlap, z-order, geometry/DPI and screenshot combinations; tabbed MDI still adds unnecessary document lifecycle | REJECT classic/free-floating MDI and tabbed MDI for S1; no current multi-document workflow justifies either |

INFERENCE: the current stack and record-level detail tabs already supply deep work without recreating tools. S1's recommendations preserve those responsibilities. The stack is not a complete draft/restoration policy: those policies must be added explicitly at the application/shell seam.

Official Qt confirms [QStackedWidget](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QStackedWidget.html) as a one-visible-page container and [QMdiArea](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QMdiArea.html) as an MDI child-window manager. The preference above is an inference from F7Hub workflows, not a Qt mandate. Installed-version behavior and actual focus/DPI remain NOT VERIFIED.

## Active Technician Context

RECOMMENDATION: one explicitly constructed, application-owned selected-context holder per main application session, injected into shell and interested presentation adapters. Its lifetime is the application session; it owns selected references and revisions, not records/authorization/persistence. Preserve ApplicationContext as dependency composition. No global mutable singleton, generic context database or shared JSON channel is proposed.

Conceptual state has a monotonically increasing local selection revision; optional owner-qualified references for company, contact, user, device, Ticket, tenant and case/session; and per-reference freshness/availability. Contact and provider User are separate roles, not interchangeable contact/user_id aliases. A remote identity requires source/provider/tenant namespace and the owner's accepted mapping; a hostname, literal Entity, credential token or row label is never fabricated into device_id or tenant_id. Current local Company/Contact/Ticket IDs can be supplied by existing source services; unavailable owner types remain absent. Case Journal remains Ticket-optional and no universal session record is invented.

Mutation concept: propose_selection(expected_revision, explicit_intent, typed_refs), validate known roles/owner identity and domain existence asynchronously, negotiate affected drafts/pending operations, then atomically publish the new immutable snapshot on the GUI thread. Cancel/failed resolution changes nothing. clear_selection is explicit and uses the same guard. Complete snapshots, not a succession of partially applied fields, prevent mixed-company/wrong-Ticket states. If an unrelated Company is selected while a Ticket is active, offer the guarded change that clears the incompatible Ticket and its derived links, or cancel; never silently combine them. Optional refs may be omitted; a Ticket without Company/Contact remains valid.

A successfully opened Ticket may contribute its authoritative linked Company/Contact. Changing preview selection, a search query, a flyout hover or the current workspace does not implicitly select a different global record. New Ticket mode has no actionable saved Ticket target: clear its active Ticket after guard while retaining a separate presentation return reference; Cancel may revalidate/restore that saved reference, and successful creation selects the newly authoritative saved Ticket.

Consumers receive only the fields relevant to their purpose. The shell requests a compact safe label from the owner; Diagnostics receives an explicitly accepted target; Mochi/S2 receives only an approved minimized projection later. Context-change notification is a typed in-process observation of snapshot/revision, not permission for providers to execute. No source domain depends back on Mochi, Analytics or the workspace.

Freshness is explicit: VALIDATED, STALE, MISSING or UNAVAILABLE per source role, plus owner revision/last-validated information when available. A read failure is UNAVAILABLE, not proof of deletion. Known deletion clears actionable reference and dependent projection after safe draft handling; stale references disable effects until owner revalidation. Notification invalidates projections promptly; operation-time validation is always required even without a notification. Labels/cache do not certify record validity. Bounded asynchronous revalidation occurs on deliberate open/use or relevant owner invalidation, never expensive work on hover.

Pending work freezes initiating references, context revision and owner concurrency tokens. Later selection cannot retarget it. Completion still records its original owner result, but applies visual selection updates only if the consumer generation matches. The shell does not add a context token to existing TicketService signatures and pretend it is transaction protection; service-owned current-record/race checks remain authoritative. Context is not permission and never authorizes remote actions.

Persistence: NONE for active selected context in S1. Layout preferences are distinct optional 0D settings; domain records stay in their repositories. Cross-process representation, if later justified, specializes 0B owner-qualified references rather than exposing this internal object or creating a second envelope.

## Active Ticket Context

RECOMMENDATION: one compact shell control derives from the selected context's Ticket reference, visible in all major modules and compact layouts. Default label is Ticket number plus plain status, with an explicit empty No active ticket state. Company/Contact/Device summaries are secondary, purpose-eligible, bounded and concealed by default in glance/flyout surfaces; no subject, note body, customer email, hostname or tenant token in application title/logs. Ticket number itself can be sensitive; conceal labels on lock/privacy suppression and retain neutral navigation affordances.

Open Ticket routes to the singleton TicketWorkspace and uses TicketService.get_ticket_details; Quick Note deliberately opens the drawer and focuses the shared Ticket-owned note draft. Evidence actions identify both selected source and exact saved Ticket, show a target preview, and dispatch only through the appropriate owning association use case. No active target means Quick Note/Attach disabled with an explanation; Open Tickets remains available.

Active Ticket survives unrelated module changes. Opening a different Ticket, new-ticket mode, clearing selection or changing incompatible Company context requires the draft/pending guard. Its saved identity and display projection are separate: a failed refresh marks unavailable/stale without sending notes to another Ticket. Known deletion invalidates actions, protects any unsaved original-target draft and offers Return to Tickets / copy or explicitly discard permitted local draft; it never picks a replacement automatically. A restored return reference is revalidated before it becomes actionable.

## Quick Ticket Drawer

RECOMMENDATION: a MainWindow-owned internal non-modal container with Ticket-owned content/presenter. It works from every major module and occupies the shared auxiliary region. It never opens on hover, performs no direct persistence and does not mirror a second full Ticket editor.

| Candidate content | S1 treatment / owner boundary |
| --- | --- |
| Ticket identity and status | MVP read-only compact projection through TicketService; current record revalidated when opening |
| Company/User/Device summary | Optional safe owner projection; current Company/Contact only when actually linked; no invented Device/User mapping |
| Quick Note | MVP existing TicketService.add_note; preserve note type/optional author semantics, default INTERNAL; no implicit publication to PSA |
| Recent F7Hub observations | LATER bounded Ticket-owned activity/read projection; no generic observation table or raw diagnostic/clipboard stream |
| Attach Clipboard evidence | LATER 1A/1B source plus explicitly accepted Ticket association, currently NOT IMPLEMENTED; disabled until both owners provide capability |
| Attach Diagnostic result | LATER result-owned exact run identity/completeness plus reviewed Ticket association; current memory result is not durable attachment capability |
| Attach KB reference | REUSE TicketKnowledgeService.link_related_article in a separately tested presentation adapter; label Link KB reference, retain RELATED semantics, never claim copied Evidence |
| Open Full Ticket Workspace | MVP guarded route to singleton detail; preserve original draft and focus its note editor on request |

One Ticket-owned in-memory note draft is bound to one saved Ticket and shared between full detail and drawer. Two simultaneous writable editors are prohibited: switch the active presentation binding, preserve the same values, and make the inactive presentation read-only/unbound. Field/status/creation drafts remain existing Ticket presentation owners. This shared draft adapter is NEW future presentation work; the current direct widget buffer is not yet that adapter. No generic persistence or new business rules follow.

Opening captures target/ref/revision and focus origin, revalidates through TicketService, then activates the matching editor. Repeated open focuses the existing drawer. The owning full-note editor cannot race a second drawer submit. Close/Escape while idle hides the drawer while retaining its session draft and a visible draft indicator; explicit Discard is separate. Outside-click never silently discards or retargets. App close, target change or disposal offers Save / Discard / Cancel where the owning operation is supported; Cancel is default. Save success is required before completing a queued target-changing intent; failure retains the draft/target and cancels that intent.

While pending, a Ticket-owned guard blocks duplicate writes and conflicting target changes through runner idle-before-callback and result presentation. Drawer close may hide only if the stable presenter and draft remain retained; it cannot imply cancellation, disposal or rollback. App shutdown follows the existing wait/retry-close rule. Rejected dispatch, validation error or pre-commit failure retains values. Authoritative note success clears only the submitted draft generation; failed reload displays Note saved; refresh unavailable and never resubmits the note. Unknown post-dispatch outcome is unconfirmed until owner reconciliation, never Failed therefore retry blindly. The current in-process add_note returns after transaction; no new retry/idempotency service is claimed.

Context change while drawer is dirty negotiates with its Ticket owner; it cannot relabel unsaved text as a different Ticket. Ticket deletion/unavailability disables save and retains the original local draft without raw fallback. Source evidence gets independent freshness/privacy/target checks at invocation; source selection changes do not replace an attachment intent already under review.

Wide layout places drawer beside the workspace only if the minimum central budget survives. Medium uses a temporary internal slide-over. Minimum uses a full available-width internal task panel with a visible return control; host widget stays alive beneath it. This is non-modal ownership, not permission for unsafe interaction behind it. Replace another auxiliary surface only after its dirty/pending guard; restore it on return if still valid. Opening takes focus only on explicit click/keyboard intent; closing restores the recorded live origin if the user has not intentionally moved elsewhere. Quick Note errors/status are announced locally and summarized in shell status without note text.

## Main Navigation

RECOMMENDATION: left navigation rail is primary; wide offers labels and medium/minimum use icons plus accessible labels/tooltips. One stable destination per module; no nested permanent navigation tree in shell MVP. Modules own their in-workspace filters/detail tabs. Search is the single top-row entry with an optional rail shortcut to that entry; Mochi and Settings are utility/footer destinations using the same mechanics, not new domain workspaces. A rail can scroll/overflow without losing Tickets/Search/Quick Ticket access. Top-navigation placement is a later variant supported by the same flyout placement contract, not a second required navigation implementation.

Navigation metadata below is RECOMMENDATION, including keys/icons/routes. CURRENT means the destination or underlying service exists, not that this proposed rail/flyout exists. PLANNED means architectural slot/content defined but not implemented. DEFERRED means richer behavior requires a later approved owner. NOT VERIFIED describes runtime capability/provider evidence not established. Icon keys are semantic references; asset choice is implementation detail, with readable text fallback and no new icon dependency.

| module_key | Display label / icon_key | Primary route | Current destination / availability | Badge/flyout/keyboard/privacy/dependency/owner | MVP / Later |
| --- | --- | --- | --- | --- | --- |
| dashboard | Dashboard / dashboard | dashboard.overview | PLANNED, no composed Dashboard | Cached safe summary only; shared flyout H/C/K; local shell projections; no global Analytics owner invented | Later tool; shell slot now |
| tickets | Tickets / ticket | tickets.list | CURRENT TicketWorkspace when TicketService composed | Bounded loaded-item count only, no total inferred; shared H/C/K; local TicketService; identity concealment | MVP |
| records | Companies / Users / Devices / records | records.overview | PLANNED record host; Company/Contact services CURRENT; generalized User/Device/Tenant NOT VERIFIED | No aggregate badge; H/C/K once available; owner-qualified private refs; CompanyService/ContactService and future source owners | Later host |
| clipboard | Clipboard / clipboard | clipboard.center | PLANNED, Center/Clipboard services not current shell | No raw preview/count retention implied; H/C/K after availability; 1A ClipboardService plus 1B adapter/1C view, all future | Later 1C delivery |
| knowledge | Knowledge Base / knowledge | knowledge.list | CURRENT optional KnowledgeWorkspace | Loaded-list count qualified, not whole library; H/C/K; local KnowledgeService, bounded safe metadata | MVP |
| diagnostics | Diagnostics / diagnostic | diagnostics.overview | PLANNED standalone tool; CURRENT read-only local diagnostics in Scripts | MVP route alias scripts.diagnostics_panel with Open in Scripts label; no second tool; cached readiness, never hover Run; PowerShellService | MVP alias / Later tool |
| scripts | Scripts / script | scripts.catalog | CURRENT optional ScriptWorkspace | Loaded catalog availability/approval counts distinct; H/C/K; ScriptService, PowerShellService for explicit reviewed Run only | MVP |
| applications | Applications / Websites / application | applications.catalog | PLANNED; launcher/catalog capability NOT VERIFIED in shell | No badge; H/C/K later; source-owner URL/path validation, no executable descriptors | Later |
| search | Search / search | search.focus | PLANNED global entry; current scoped queries CURRENT | No badge; focus one top search; H/C/K without history persistence; existing query services plus future application coordinator | MVP entry/adapters / Later aggregate |
| reports | Analytics / Reports / report | reports.overview | PLANNED report host/provider NOT VERIFIED | No calculations/count aggregation here; H/C/K later; future report/analytics owner, safe scopes | Later |
| settings | Settings / settings | settings.overview | PLANNED general view; CURRENT Mochi dialog only | No badge; route fallback explains unavailable general service and exposes existing Mochi controls, not fake saved preferences; future SettingsService | MVP existing controls / Later shared UI |
| mochi | Mochi / AI / mochi | mochi.controls | CURRENT local controls with composed MochiService; AI/DynamicHub DEFERRED | Cached control status, shared H/C/K; no inference/context scrape; future S2 capability remains separate | MVP cosmetic controls / Later S2 |

H/C/K is precisely defined in Flyout Mechanics below. Every new main-navigation button must consume this inventory and the matrix, or receive a reviewed row update. Planned modules do not ship as fake enabled destinations: omit unimplemented primary buttons from normal MVP navigation or show them disabled with an accessible Not available yet reason; a direct stale route returns that same safe state. Diagnostics' explicit current alias is the only named temporary module alias. Current File/toolbar utilities are preserved and are not counted as twelve implemented modules. Prompts, standalone PowerShell, Plugins, Logs and provider administration in canonical conceptual inventories remain DEFERRED outside S1's primary set; no arbitrary shell endpoint or provider module is introduced.

## Flyout Mechanics

RECOMMENDATION: one shell-owned NavigationFlyoutHost concept supports every available descriptor. It owns one current trigger/content generation, a placement strategy and finite timers. Modules provide bounded safe content snapshots and domain availability, never popup windows or execution code. Flyouts are internal MainWindow child surfaces over the workspace, not independent persistent desktop windows, always-on-top panels or main navigation in DynamicHub.

| Interaction / code | Exact proposed behavior |
| --- | --- |
| H: hover | After 275 ms stable pointer dwell within the trigger, open available cached flyout with no keyboard focus change. No automatic read, provider work, capture, execution or inference. Cancel timer on leaving/replacement/close. Moving over another trigger starts its own dwell; exactly one flyout ever visible. |
| C: primary click | Navigate the module's primary route through draft guard; do not toggle flyout instead. Search focuses global entry; Mochi opens existing controls; unavailable destinations explain refusal without mutation. |
| C: chevron / touch | Separate accessible secondary control opens/focuses the flyout; repeated activation closes that flyout. Touch has the same two explicit targets, no long-press/hover requirement. One combined accessible control may expose a secondary action if tested, but not ambiguous primary-click semantics. |
| K: keyboard | Tab reaches trigger; Enter/Space invokes primary route. Alt+Down on the focused trigger or Enter/Space on its chevron opens flyout and focuses first enabled item (or empty-state explanation). Arrows navigate selectable content; Home/End first/last; Tab/Shift+Tab traverse controls; Enter/Space activates one allowed item. No letter keys intercepted in an editor. |
| Escape | Flyout owns scoped Escape while keyboard focus is inside; closes and returns to trigger. Hover-open does not steal an editor's Escape. Deliberate shell Close transient action can also dismiss unfocused hover flyout without consuming unrelated text-widget input. |
| Trigger to flyout transfer | Trigger + short geometric bridge + flyout form one pointer-transfer region. Moving across its bridge suspends leaving until the 400 ms grace expires; entering flyout cancels the close timer. No giant invisible hit region or intercepting workspace clicks. |
| Leave grace | 400 ms after pointer leaves the combined region closes only a hover-mode flyout with no focus within. Keyboard/click-focused flyout stays open until explicit dismissal/focus departure; a pointer departure cannot close under keyboard use. Timers are cancelled on owner destruction. |
| Focus departure / outside click | Close when a click or deliberate focus move goes outside trigger/flyout; never force focus back over the user's new destination. A navigation/action first captures its typed intent, closes the flyout, and enters the guard. Click causing dismissal is not also interpreted as another flyout action. |
| Panel/module/modal changes | Close flyout and invalidate content callbacks on module activation, window deactivation/minimize, application close, modal editor, privacy suppression or incompatible panel replacement. It has no writable draft to lose. |
| Placement | Prefer beside rail; support below top navigation later. Clamp inside the intersection of MainWindow's usable client area and the trigger screen's available work area; flip side if necessary. Reduce/scroll content if it cannot fit; never position partly offscreen or across a nonexistent monitor gap. |

Numbers are planning recommendations, not immutable code constants. Hover 275 ms (within 200-350) and leave 400 ms (within 300-500) are RECOMMENDED defaults. Hover enablement/delay are LIKELY USER-CONFIGURABLE through future 0D definitions with finite validated bounds; leave grace is an IMPLEMENTATION DETAIL unless usability proves a setting need. Pointer bridge, animation and exact dimensions are IMPLEMENTATION DETAIL and NATIVE-VALIDATION DEPENDENT. If a feature setting is missing, use a safe static default; no separate settings file.

Background alpha 90% within approximately 85-95% is RECOMMENDED, optionally USER-CONFIGURABLE once 0D supports it. Text/icons remain opaque. Reduced-transparency/high-contrast or poor measured contrast forces opaque background (100%) regardless of cosmetic preference. Whole-window opacity that fades text is not the chosen architecture; QWidget.windowOpacity is a window property, so an internal child flyout uses a themed background with alpha, subject to native validation. Blur/acrylic is optional, never an availability dependency. Qt's [QWidget reference](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QWidget.html) is checked for this distinction; S1 does not inherit the guide's separate opacity policy.

Reopening flyout consumes already available, purpose-filtered snapshots, not work. On explicit click/keyboard opening, an owner MAY request one small asynchronous local projection if its capability exists; present Loading and retain stale/nonactionable cache identity. Suggested bound: at most five combined recent/pinned items and two to five quick actions (three typical), no raw record bodies and no unbounded aggregation. Coalesce duplicate reads, reject stale consumer generations and offer explicit Retry on failure. Do not create a prefetch scheduler or poll providers to decorate badges.

## Flyout Content Contract

RECOMMENDATION: NEW small immutable ModuleNavigationDescriptor built by explicit application composition, not a dynamic plugin registry. No shared descriptor implementation was found. Extract existing route/action metadata rather than author a competing executable action catalog. Module-owned pure contributions define meaning; existing owner-service adapters supply availability/projections. The shell does not introspect imports or discover executable commands.

| Descriptor property | Conceptual constraint |
| --- | --- |
| module_key / display_label / icon_key / primary_route | Stable known identity; bounded plain label; semantic icon fallback; closed allowlisted route |
| flyout_groups | Ordered Context, Quick actions, Navigation/Recent, Open full workspace; omit irrelevant groups; no empty decorative sections |
| availability_provider / badge_provider | Explicit injected bounded projection interface; no callable text in serialized descriptor; source/cache availability and freshness independent of enabled |
| item_key / item_type | Unique within module; NAVIGATION, QUICK_ACTION, RECENT_RECORD, PINNED_RECORD, STATUS, SEPARATOR or OPEN_WORKSPACE |
| label / icon / safe_summary | Bounded owner-approved plain text; summary optional/concealed by default; no raw Clipboard, note, credential, command or HTML rendering |
| route_key or action_key | Exactly one meaningful allowlisted destination/action; separators/status nonactivatable; route keys cannot authorize business effects |
| owner_subsystem / typed_reference | Known owning domain and qualified source identity, optional revision/generation; never guessed from visible text |
| availability / enabled / disabled_reason | Distinguish unimplemented/service unavailable/loading/partial/stale/no context/permission denied; show bounded safe explanation; no default true for missing capability |
| badge | Optional source-qualified loaded count/status plus freshness; unknown is unknown, not zero; no sensitive global totals |
| keyboard_behavior / privacy_classification | Uses H/C/K, focus order and explicit activation; conceal potentially identifying rows by default, allow only purpose-eligible minimized disclosure |

Availability is presentation truth, not authorization. Every activated quick action revalidates source/target/policy and operation permissions through its owning service. Descriptors never contain SQL, shell snippets, script bodies, Graph/RMM endpoints, credentials, untrusted URLs as commands or arbitrary executable callbacks. A compiled adapter resolves known key to a reviewed owner method. A provider cannot register itself by supplying arbitrary data; capability flags and settings cannot grant permission.

Error anatomy is stable across modules: unavailable module reason + reachable safe alternative; no active context + Open workspace; empty provider + No recent items; loading + nonduplicating feedback; partial/stale + nonactionable data and explicit Refresh where available; permission denied + owner-safe explanation, no expanded scope request. Disabled explanations are readable/focusable as adjacent status even if their button is not Tab-focusable. Hover never retries.

## F7Hub Navigation Surface Matrix

RECOMMENDATION: this is the single authoritative S1 content matrix at planning depth. H/C/K refers to the complete shared mechanics above, not unimplemented per-module behavior. MVP means later bounded shell delivery using existing capability; it is not an implemented label. PLANNED/DEFERRED content remains unavailable until its owner passes separate delivery gates. Pinned/recent interfaces are source-owned future reads unless a bounded loaded projection is expressly identified; no global favorites/history table is invented.

| Module | Primary route | Context header | Quick actions | Navigation items | Recent/pinned provider | Badge/count | Empty state | Unavailable state | Hover behavior | Click behavior | Keyboard behavior | Privacy considerations | Capability dependencies | Owning service(s) | MVP / Later |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Dashboard — PLANNED | dashboard.overview | Safe active Ticket presence / local status, identifying labels concealed | Resume Active Ticket; Quick Note; focus Search | Overview; Today/Activity later, no duplicated report engine | Session visited route refs only; durable activity/recent Ticket feed DEFERRED | Cached safe status, no calculated totals | No active work; Open Tickets | Dashboard unavailable; Tickets/Search remain reachable | H cached only when host exists | C guarded Overview | K; action refs revalidated | No activity text/customer previews | Local shell host/projections; no provider prerequisite | Shell coordinator consuming TicketService; future dashboard reads | Later tool; no fake MVP dashboard |
| Tickets — CURRENT destination, PLANNED flyout | tickets.list | Active Ticket number/status or No active ticket | Quick Note; New Ticket; Open Active Ticket; Attach source only when association exists | All; NEW; OPEN; IN_PROGRESS; WAITING; RESOLVED/CLOSED history views; Recent later | Existing loaded Ticket queue bounded to five eligible refs; pins/recent store DEFERRED | Loaded page count explicitly qualified; no Waiting Customer/Vendor invented | No tickets on current page / no active target; New Ticket | Service unavailable; read-only safe explanation; no write | H snapshot only | C list; chevron content actions separately guarded | K; Ctrl+Alt+T planned Quick Note | Number may be private; no subject/body by default | TicketService; note/creation idle; association separately required | TicketService, TicketKnowledgeService for RELATED link; future source association owner | MVP routes/note; attachments later |
| Companies / Users / Devices — PLANNED host, partial CURRENT services | records.overview | Selected Company/Contact; Device/User/Tenant absent if not resolved | Open active record; Search Contact; Search Device later; copy approved identity only if owner allows | Companies; Contacts; Users/Devices/Tenants later with truthful unavailable labels | Future source-qualified recent provider; no global browsing-history persistence | None | No selected record; search available owner | General host unavailable; existing ticket-linked Company view remains available | H only available safe snapshot | C record host when delivered | K; owner-qualified record activation | Names/email/device/tenant identifiers concealed in glance surfaces | CompanyService/ContactService current; other owners NOT VERIFIED | CompanyService, ContactService; future device/user/integration owners | Later host; current Company tab not a substitute universal directory |
| Clipboard — PLANNED | clipboard.center | Generic last capture disposition/storage state; selected safe Item ref, no raw preview | Capture Current deliberately; Save; Pin; Open Center; no more than five available actions | Recent; Saved; Pinned; URLs by owner Kind; Ticket Evidence / Diagnostic Evidence only if associations exist | Future ClipboardService bounded eligible Item views; no AHK history provider | No default count; owner-approved cached eligible count later | No eligible items / not saved / expired ref; capture manual | Center/service unavailable, blocked/error/unconfirmed safe status; no raw fallback | H generic cache, no OS read or capture | C Center; Capture is separate explicit 1B-owned workflow | K; Win+Alt+C stays 1B ownership, no duplicate global binding | No secrets/title/raw content/history; Save/Pin/hold semantics remain 1A | 1A service, 1B authentic ingress, 1C Center, source policy and rev; all future | ClipboardService and association owners, proposed/not implemented | Later 1C; slot and content frozen now |
| Knowledge — CURRENT destination, PLANNED flyout | knowledge.list | Current article code/state, identifying title/query hidden by default | Focus KB Search; Create Draft; Open current article | All; Drafts; Categories through existing filters; Favorites later | Bounded eligible loaded article refs; favorites/pins provider DEFERRED | Loaded results qualified; no total inferred | No current article / no matching results; search/create | KnowledgeService unavailable; existing drafts retained | H no search/filter load | C list; secondary explicit scoped filter/action | K; normal query Enter remains scoped | Query/body/title may be sensitive; no raw KB body on hover | KnowledgeService and filter option readiness; draft dialog guard | KnowledgeService; TicketKnowledgeService only accepted Ticket relationship | MVP; Favorites later |
| Diagnostics — CURRENT in Scripts, PLANNED standalone | diagnostics.overview; MVP alias scripts.diagnostics_panel | Local target / latest run identity and safe outcome, not current row guessed as target | Open approved diagnostic details; View current result; no Run in hover flyout | Current local System/Network/Services and baseline pack via Scripts; M365/Security categories later | Existing in-memory last-result projection only; pinned/history provider DEFERRED | Cached ready/unavailable status; collection ERROR distinct from execution failure | No result; Open in Scripts | Execution boundary unavailable; local catalog still accessible; no run fallback | H no PowerShell/provider work | C MVP Open in Scripts alias; full future route unavailable | K activates presentation only; Run stays explicit full tool | No raw diagnostic data/user/device info by default | Existing ScriptService/PowerShellService manifest/runtime availability; remote inputs unsupported | PowerShellService -> approved gateway; future Diagnostic presentation owner | MVP alias; later dedicated tool/associations |
| Scripts / Automation — CURRENT destination, PLANNED flyout | scripts.catalog | Safe selected registration name/policy availability; target only if owner supports it | Focus script Search; Open selected metadata; Open management through existing dialog; no direct Run/copy body on hover | Catalog; approved metadata views later; approved favorites later | Bounded loaded catalog metadata; favorites/persisted recents DEFERRED | Shown/Available/Execution approved distinct cached counts | No scripts / no match; Refresh explicitly | ScriptService unavailable or file/runtime missing; no arbitrary path execution | H cached metadata only | C catalog; actions route existing guarded view/dialog | K; editable search preserved | No script body, paths with personal data or executable payload in descriptor | ScriptService; PowerShellService only actual reviewed execution | ScriptService, PowerShellService | MVP browse; richer favorites later |
| Applications / Websites — PLANNED | applications.catalog | Approved category/selection, no raw URL/title | Open catalog; deliberately Launch/Open selected approved record only after owner capability exists | Favorites; Recent; Categories | Source-owned approved records; provider/API NOT VERIFIED; no shell list of executable paths | None | No approved entries | Catalog/launch boundary unavailable; no unchecked URL/path open | H no launch, URL resolution or history scan | C catalog when available | K explicit launch intent via owner | URLs/path/title can be private; no browser history import | Approved catalog/launch validation, scheme/path policy required | Future application/website catalog and launch service; names not implemented claims | Later |
| Search — PLANNED global entry, CURRENT scoped queries | search.focus | Scope + no active query preview | Focus Global Search; choose Tickets/Knowledge/Scripts scope | Scoped destinations; combined results later | None MVP; opt-in reviewed query-history provider DEFERRED | None | Enter a query; local scope chooser | Unsupported scope clearly unavailable; existing scoped queries usable | H static scope choices, no query execution | C focus single top entry | K; Ctrl+K proposed focus; Enter explicit submit | In-memory query only; no persisted history, logs or AI by default | Existing Ticket subject search/Knowledge search/Script text query; aggregation future | TicketService, KnowledgeService, ScriptService; future application search coordinator | MVP focus/adapters; later combined search |
| Analytics / Reports — PLANNED | reports.overview | Optional validated Ticket/Company scope, concealed label | Open report; Open drill-down, both later | Reports; Analytics views by approved owner | Future owner recent/pinned reports; no shell aggregation | None until owner cached safe projection exists | No reports in scope | Reporting unavailable; no fake zero/remote fallback | H cached safe metadata only | C report host when delivered | K typed drill-down route and owner scope | No telemetry bodies/customer totals in glance; disclosure source-owned | Reviewed report/analytics definitions/read APIs; external provider optional per use case | Future reporting/Analytics services, NOT VERIFIED runtime | Later |
| Settings — CURRENT Mochi control entry only, PLANNED shared Settings | settings.overview | Availability/effective state only, never credential values | Open current Mochi controls; general preference editors later | General; Appearance; Hotkeys; Clipboard; Integrations; Mochi/AI; Privacy only when definitions/consumers exist | None | None; desired/applied warning later from owner | No shared Settings UI yet | General Settings unavailable; existing Mochi control route offered; no pretend Save | H static approved section map, no config/secret read | C later general view; current controls via explicit alternative | K accessible navigation; no new global hotkey | Secrets excluded; privacy opt-in not blanket permission | 0D definitions/shared service implementation; current MochiService separately available | Future SettingsService; MochiService for current controls | MVP truthful alternative; later shared UI |
| Mochi / AI — CURRENT cosmetic controls, DEFERRED contextual actions | mochi.controls | Cached running/paused/unconfirmed status; no business-context dump | Show/Hide; Pause/Resume; Open controls; Open Context Surface later | Current controls; Settings entry; future S2 context surface | No recommendation/recent conversation provider in navigation flyout | Cosmetic availability only, never implied AI ready | Mochi not running; deliberate Start/Show | Cosmetic service unavailable / unconfirmed; AI not configured, no inference | H cached control status, no start/IPC/inference | C existing controls; future context route separately available | K explicit cosmetic action; local controls cannot authorize business action | No screenshots/raw screen/Clipboard/Ticket payload; no automatic Send | Current MochiService/gateway; future S2 adapter/provider separately reviewed | MochiService; S2 coordinator consumes source services later | MVP cosmetics; Later S2/AI |

Ticket filter labels come from E-D: WAITING is one current status, not distinct Waiting Customer/Vendor states; those labels are rejected until Ticket domain changes independently. Diagnostic categories shown in the original contract are candidate future groupings, not proof of Graph/RMM/M365 capability. Clipboard Capture Current refers to a deliberately invoked reviewed capture workflow, not reading OS Clipboard at hover or inventing a duplicate AHK trigger. No surface manufactures favorites, evidence association, shared Settings or provider capabilities merely because a candidate row mentions them.

## Workspace Tabs

RECOMMENDATION: no shell workspace tab strip in MVP. Main rail + retained singleton stack supply module switching. Ticket's existing record-detail tabs remain unchanged in meaning. This avoids two competing navigation hierarchies and a new close/restore model before multi-record workflows are demonstrated.

One Ticket module with one active saved detail and one guarded creation mode; one Knowledge module with owner dialogs; one Scripts module with its run/result ownership. Multiple Ticket/record instances, unlimited browser-like tabs, pinned workspace tabs and temporary preview tabs are NOT NEEDED for this S1 architecture. Later proven multi-record requirements require a reviewed extension including draft budgets, target tokens, close semantics and native tests, not silent tab proliferation.

If a later bounded singleton workspace selector is added, it is a view over the same module keys/stack, not a second host. Its close action hides a clean module, leaves dirty/pending participants intact or negotiates explicitly, and never destroys a pending write. No automatic record/context persistence. Module switching uses the same context and draft rules in all entry points.

## Global Search

RECOMMENDATION: one compact top-row search affordance, always keyboard reachable; narrow mode collapses it to a button that opens/focuses an internal search row/panel. The optional Search rail entry and flyout scope choices focus this same entry. Ctrl+K is a proposed application-window shortcut, not a registered global hotkey. Ctrl+F remains the focused tool's local search where provided; no editable shortcuts are intercepted.

MVP delegates explicit submitted queries to existing Ticket subject, Knowledge and Scripts search adapters. A scope chooser makes the target clear; Enter submits, typing does not start provider work, and result activation issues a guarded typed record route. Combined results are a later application use case; no new full search engine is hidden in flyouts. Ticket number lookup remains its existing owner method. Source search/filter semantics and literal escaping remain owning service responsibilities.

Async read uses existing runners/available owner read paths and request generation. One outstanding search per consumer; stale results cannot replace a newer query or select another record. Closing a search surface invalidates its callback/focus generation without falsely cancelling committed work. Loading/no matches/partial/unavailable distinguish module results. Result opening preserves drafts via the same guard. Queries/results live only for the application session, bounded and cleared on privacy/session transitions; no durable history/telemetry/query text logging or default external search/AI.

## Status / Background Activity

RECOMMENDATION: retain QStatusBar as the global non-modal summary and module feedback as the detailed owner presentation. A small application-session activity view, if delivered, holds bounded operation identity, owning module, safe state and retry-read route only. No global job table, logging replacement, Ticket history replacement or unsolicited provider watcher is required.

States distinguish loading, writing, completed, completed with refresh unavailable, recoverable failure, unavailable and unconfirmed. An unknown badge is not zero; partial availability is not success for missing components. Explicit action routes to its owning workspace to view detail/retry; status never contains note text, raw Clipboard, diagnostic payload or credential data. Success announcements are transient but recoverable failures remain reachable. Include accessible announcements and textual state, not color alone.

Runner busy is not the entire lifecycle: per-owner pending flags remain active through service completion, callback gap and owned refresh. Preserve current conservative blocking for writes/diagnostic runs until a separately tested slice proves safe scoped independence. Small independent read-only navigation may eventually remain responsive; no promise of parallel Ticket writes or new cancellation. Existing diagnostics are not cancellable; hiding a panel does not cancel them. Mochi acknowledgement overlays and DynamicHub advice remain separate contextual surfaces, and Ticket timeline remains domain evidence.

## Draft Preservation

RECOMMENDATION: extend existing local guards with a minimal presentation participant protocol: report dirty owner/ref, pending operation identity, can retain while hidden, safe focus target, and prepare_navigation/prepare_close result. This is not a new domain service or persistence system. Shell coordinates; each feature detects dirty values, validates/saves and determines meaningful failure.

| Scenario | Detection owner | Shell behavior / safe outcome |
| --- | --- | --- |
| Saved Ticket note draft | Ticket-owned shared note model | Switching unrelated retained modules preserves buffer/target; drawer/detail shares one editor; changing Ticket negotiates Save/Discard/Cancel |
| Ticket field/status/classification drafts | TicketWorkspace and edit dialogs, original owner tokens | Keep on hide if adapter guarantees retention; affected record replacement/reload uses owner guard; no rewriting concurrency baseline |
| New Ticket form | TicketCreateWidget/creation presenter | Preserve form on unrelated module hide once adapter supported; no actionable saved Ticket during creation; closing/replacement prompts, Cancel default |
| Knowledge create/edit draft | Knowledge dialog/presenter bound to article/version | Register all open editors; preserve on background navigation or refuse if modal; idle close/destruction gains dirty confirmation before new shell behavior ships; conflict retains original draft/token |
| Script management / modal editors | Owning dialog and change/pending state | Keep current modal/lifecycle conventions; do not close or refresh behind a pending write |
| Future Clipboard selection/annotation/association intent | Future 1C owning presenter | Retain permitted session state; source expiry invalidates effects without silently retargeting; raw persistence is not a shell decision |
| Pending write/run | Owning participant, not runner.busy alone | Refuse conflicting target changes/disposal/app exit; safe hide only with retained presenter; truthful wait/status, no fake cancellation |
| App close / restart | All participants, including hidden tools/dialogs | Collect affected dirty/pending owners; pending blocks close; negotiate supported saves serially; any Cancel/failure keeps window/state. No claim of crash recovery or durable draft restore |

Retained hide avoids discard prompts only after owner adapters prove drafts/dialogs survive and remain bound. Until then, preserve existing conservative Discard/Cancel behavior or refuse navigation; do not bypass confirm_discard because this plan describes future retention. Explicit destructive discard has Cancel default and identifies original record; no automatic save on module activation. Save unsupported means only Discard/Cancel offered, never a fake Save button. A failed save leaves every affected draft intact and cancels queued navigation. Once a write commits, its acknowledgement cannot be downgraded to failure/cancellation by a later read, context change or panel close.

Escape ownership must be reconciled deliberately: Ticket's current note editor consumes Escape. S1 does not silently override that behavior. In a future Quick Ticket binding the Ticket presenter must explicitly grant scoped drawer-close behavior or provide the visible close action; an inner editor/modal guard gets first refusal. Changing the existing editor Escape contract requires focused regression/native validation. This resolves shell close without global interception.

## Responsive Layout

RECOMMENDATION: fit measured usable client width and owner minimum sizes, not physical display pixels. Planning bands below are initial logical-pixel targets, NATIVE-VALIDATION DEPENDENT; they are not immutable settings. Reserve central working width of approximately 700 logical px for existing tool adaptation; if real minima/large fonts demand more, collapse ancillary regions sooner. Existing 1000x700 source assertions inform the minimum target but do not certify new layout.

| Region | WIDE: usable width >=1440, height >=700 | MEDIUM: 1180-1439, height >=700 | MINIMUM SUPPORTED: 1000-1179, height >=700 |
| --- | --- | --- | --- |
| Main navigation | Labeled rail about 176 px; bounded scroll/overflow | Icon rail about 56 px with accessible labels | Icon rail about 48-56 px; overflow navigation fully keyboard reachable |
| Workspace tabs | No shell tab row; module detail tabs remain | Same; no second permanent row | Same; module tabs/content may scroll, never hide required save/close |
| Active Technician Context | Compact top row optional secondary refs | Selected context summary collapsed to button; explicit details panel | One compact Context button; no permanent context sidebar |
| Active Ticket | Number/status + Quick Note/Open Ticket | Compact number/status and explicit actions | Compact Ticket button/status; Quick Note/Open available in button/menu; no offscreen target |
| Quick Ticket | Shared auxiliary split roughly 320-400 px only if central >=700 remains | Temporary internal right slide-over; do not shrink workspace below minimum | Full available-width internal Quick Ticket task panel, visible Back/Close, underlying module retained |
| Main content | Singleton stack with module-owned splitters | Stack retains width; collapse secondary module pane as needed | Module compact mode/list-detail toggle/scroll; no simultaneous permanent queue+inspector+drawer burden |
| Inspector / right panel | At most one auxiliary occupant beside content | Temporary surface; mutually exclusive with Quick Ticket/S2 | Internal task panel; owner state retained during replacement |
| Mochi/DynamicHub reserve | Same shell-owned auxiliary slot; not permanently assigned to modules | Collapsed explicit affordance, temporary side surface later | Collapsed explicit affordance, internal panel later; no reserved empty width |
| Flyout | Internal rail-right, clamp/flip/scroll | Same, smaller width/height if needed | Compact internal overlay with scroll and keyboard Close; can use explicit internal menu sheet |

Height under 700 or width under 1000 is BELOW the proposed supported baseline, not silently considered validated. Future implementation must enforce/report reachable minimum or deliver an accessibility-safe compact fallback if font/DPI/work-area prevents it; no cropping controls to fake support. At each band, only one permanent secondary region exists. Collapse before central minima fail, preserve dirty/pending state, and never use desktop overflow windows as automatic fallback. User-resized splitter preference cannot force an unusable central layout. Active Ticket/Search remain reachable even with long labels; cap/ellipsize labels with safe accessible equivalents, not raw content tooltips.

## Keyboard & Accessibility

FACT current inventory: MainWindow uses Qt StandardKey.Quit; Ticket note editor uses Ctrl+Enter only while focused and consumes scoped Escape; visible Ticket creation form uses StandardKey.Save (Ctrl+S) with visibility/pending guards. Queries use their local Enter/button behavior. Menu mnemonics include File/Settings/Exit. Existing guide keyboard scope remains independent; approved Clipboard 1B reserves Win+Alt+C capture. No dedicated current global search, Quick Ticket, rail or workspace cycling shortcut was found in inspected Python source.

| Shell action | Proposed binding / scope | Editable-widget and conflict rule |
| --- | --- | --- |
| Focus navigation rail | Ctrl+Alt+N, application window only | Candidate, future native keyboard/AltGr audit required; accessible Navigate menu/Tab fallback always works |
| Activate main navigation | Tab/arrows within rail, Enter/Space | No global bare letters/numbers; focus stays logical; unavailable reason reachable |
| Global Search | Ctrl+K, application window only | Opens/focuses single entry; no Ctrl+F override; resolve installed shortcut collision before enabling |
| Quick Ticket / Quick Note | Ctrl+Alt+T, application window only | Explicit drawer open/focus, original Ticket target revalidated; AltGr/layout audit and menu fallback |
| Cycle workspace | Ctrl+PageUp/PageDown only with focus on rail/workspace selector shell control | Do not intercept Ticket detail tabs, editors, lists or guide's own bindings; Navigate menu lists alternatives |
| Flyout access | Alt+Down on focused trigger / chevron Enter/Space | Opens focusable content; standard editable combo/list behavior untouched elsewhere |
| Close transient panel | Scoped Escape after inner owner guard, or visible Close | Dirty panels hide/retain or negotiate; editor/modal consumes first; no global capture of Escape |
| Focus return | Origin widget if live/enabled and no newer intentional focus | Otherwise active module heading/trigger; never repeated focus attempts into another application |

Proposed chords are RECOMMENDED, NATIVE-VALIDATION DEPENDENT and not claimed registered/collision-free. No new global hotkey, AHK binding or keyboard hook. Clipboard 1B retains Win+Alt+C; no reuse of F7/Alt+F7 or Ctrl+C/Ctrl+V/Ctrl+X/Ctrl+Z/Ctrl+Y/Ctrl+S for shell navigation. Standard text editing and accessibility technologies must remain usable.

Every hover item is available through click/chevron/menu/keyboard and touch. Require visible focus, named icons and expand/collapse state, logical Tab order (global row, rail, active content, active auxiliary surface, status detail), plain textual disabled explanations and non-color-only badges. Use sufficient measured contrast over worst-case background; opaque fallback when translucency fails. Do not announce entire sensitive context through screen reader status; accessible labels follow the same minimization policy. Narrator/tab traversal/high contrast/large font and keyboard-only task completion need separate future Windows evidence.

## DPI / Multi-Monitor

RECOMMENDATION: use Qt logical coordinates consistently, map trigger geometry through the shell once, and choose the trigger's actual screen rather than assume primary/positive coordinates. Recompute geometry on screen/DPI/window movement and work-area change. Clamp to current application's usable area intersected with that screen's work area; never apply a devicePixelRatio twice. If origin screen disappears, close transient surface and reopen safely on explicit action with a valid current screen.

Official [QScreen availableGeometry](https://doc.qt.io/qtforpython-6/PySide6/QtGui/QScreen.html) excludes reserved areas such as taskbars; actual Windows/mixed-DPI behavior is still an implementation validation requirement. Existing MainWindow initial resize uses available screen geometry, but that is not proof of future flyout placement.

| Future WINDOWS_NATIVE case | Required observation | Current S1 result |
| --- | --- | --- |
| 100%, 125%, 150%; higher DPI where practical | Readable labels/icons, no clipped controls, one coordinate scale, reachable min-size behavior | NOT RUN |
| Screen edges / taskbar top/right/bottom/left | Flyout flips/clamps/scrolls within available application/screen region | NOT RUN |
| Negative-coordinate secondary monitor | Correct placement/focus with no assumption x/y >=0 | NOT RUN |
| Mixed-DPI crossing and maximize/restore | Recompute bounds and preserve draft/focus; no stale placement cache | NOT RUN |
| Disconnect / work-area change / session transition | Dismiss/recalculate safely; no offscreen restoration or sensitive stale projection | NOT RUN |
| 1000x700; larger fonts/high contrast; reduced transparency | Quick Note/Close/Search/Ticket accessible without overlap; opaque fallback | NOT RUN |
| Keyboard / pointer / touch / Narrator | All routes/flyout items reachable, no focus theft, no hover-only task | NOT RUN |

Future native harnesses use synthetic records, observable readiness, finite input/assertions, whole-run timeout and owned-process cleanup. Two identical failures without changed state/hypothesis stop the loop. QTest-native input, physical hardware input and headless/offscreen evidence must be reported separately. CLOUD_PORTABLE success cannot satisfy these Windows gates. No runtime/screenshots were produced in S1.

## Mochi / DynamicHub Reserved Region

RECOMMENDATION: the shell owns one optional right auxiliary region. Modules receive a temporary lease for inspector/Quick Ticket; they cannot permanently consume it or create their own rival right dock. Future S2 receives the same presentation slot, with a collapsed Mochi/context affordance reachable at all layout sizes. No blank permanent column is required while S2 is absent.

At most one of inspector, Quick Ticket or DynamicHub is expanded at once. Replacement negotiates affected drafts/pending operations; dirty Quick Ticket can remain retained while hidden or refuse unsafe replacement. Explicit Open Full Workspace releases the slot and uses the stack. A meaningful later S2 result cannot silently replace an active dirty editor or steal focus; it may expose a safe indicator and require deliberate opening. S2 owns triggering/action/observation semantics after its separate execution/review/approval.

Navigation flyouts are transient above ordinary shell content and close when another focused auxiliary panel is activated. They do not cover modal dialogs or force topmost desktop behavior. Auxiliary panels remain MainWindow children; focus precedence is active modal owner, deliberately focused internal task surface, then active workspace. Mochi's current cosmetic companion/controls remain their approved separate lifecycle; S1 adds no AI/context transport. S2's invocation-time target binding remains compatible: surface replacement/active-context changes cannot change the target of already initiated work.

## Settings Inputs

RECOMMENDATION: future definitions are pure module contributions to the shared 0D mechanism, not UI-state persistence by default. Classification says whether a input is justified, not that its key/service/value has been implemented or approved for activation. Validate before consumer application; sensitive optional behavior fails closed; desired/saved state differs from applied native state.

| Input | Classification | Proposed default / admissible treatment | Runtime / persistence boundary |
| --- | --- | --- | --- |
| Navigation style | FUTURE | Adaptive left rail is static MVP; top-navigation/dense style only after workflow/native evidence | Appearance preference later; not module routing/authority |
| Flyout enabled / hover enabled | LIKELY | Hover on by recommendation; disabling hover keeps explicit click/keyboard access | Future USER-CONFIGURABLE preference; no disclosure permission |
| Hover delay | LIKELY | 275 ms; future finite bounded range validated through 0D; initial planning 200-350 ms | Next open; grace/bridge remain implementation detail |
| Flyout background opacity | LIKELY | 90% target; approximately 85-95% design range, opaque 100% mandatory fallback | Theme consumer, accessibility overrides; no guide INI reuse |
| Quick Ticket preference | LIKELY | Explicit open, no automatic popup; optional default collapsed | Presentation only; target/draft never preference |
| Workspace restoration | FUTURE | No cross-process record/query/draft restore by default; optional nonsensitive module/geometry later | 0D-owned storage, versioned allowlist and clamp; no restore of operations |
| Panel-collapse preference | LIKELY | Adaptive safe collapse, optional preferred width/state later | Apply only if central min survives; no context/customer persistence |
| Session workspace/draft retention | CORE behavior, NOT a new persistent Setting | Retain safe participant state while process lives | Source-owned runtime buffers, privacy policy/lock handling |
| Leave grace / pointer bridge | NOT NEEDED as settings initially | 400 ms default plus tested bridge | IMPLEMENTATION DETAIL / NATIVE-VALIDATION DEPENDENT |

No Settings class/store/schema/key file is created. Cosmetic preferences cannot disable domain validation, secret gates, explicit target confirmation, execution policy or access checks. Open menu section does not imply a configurable setting exists. Follow 0D per-key admitted scope/precedence and desired/applied lifecycle when a later implementation actually adds a consumer.

## Security / Authority

RECOMMENDATION: shell widgets collect intent and present minimized owner projections. Ticket mutations remain TicketService/TicketKnowledgeService or reviewed association-use-case owned; repositories transact. Diagnostics retains result/execution semantics and uses the existing PowerShellService -> PowerShellGateway -> approved registered operation. Shell does not write SQLite, open arbitrary shell processes, invoke Graph/RMM/AI directly, broker credentials or elevate.

Context, selected row, visible action, enabled preference and cached capability each fail to grant permission. Owning services validate current target/source, policy, concurrency and supported operation at invocation. Clipboard contents/Entity detection cannot select an authoritative Ticket or execution target. No action runs on hover or mere context-change notification; even an approved diagnostic requires explicit reviewed Run intent. Imported/provider/AI text and descriptors are untrusted; render plain text, bound labels/rows, validate route keys and source IDs, and never interpolate executable fragments.

No secrets in context/settings/descriptors/logs/history/activity. No raw Clipboard/Ticket/diagnostic body in flyouts, titles or status by default; approved full workspace read is separately owner-authorized and does not imply external disclosure. Recent/pinned counts/projections follow source privacy and retention, not global lifetime invented by shell. Employer/provider policy and actual screen-sharing acceptance are NOT VERIFIED. External AI needs its separately reviewed credential/provider/minimal-payload preview and explicit Send boundary; S1 selects none.

Local-required shell navigation, Ticket note drafts and existing local queries remain useful offline. Clipboard domain/Center activation follows 1A/1B safety prerequisites, not remote providers. External reporting/Graph/RMM/AI operations are separately ONLINE_OPTIONAL/ONLINE_REQUIRED by owning use case; their failure cannot disable unrelated local tools. Existing guide/Mochi routes retain their narrow services and unconfirmed-result truth.

Database impact: NONE. No migrations, relationships, Settings rows, global context store, generic evidence table or operational data writes/reads are introduced. integrity_check/foreign_key_check are NOT RUN; S1 makes no claim of operational database validity. Any future persistence slice must inspect Docs07/08/09 and existing owner tables before proposing schema.

Documentation impact: only S1 appended. Future approved synchronization may affect Docs05/06/13 and actual current-state/history owners, but this task changes none of them or S2/1C/Roadmap/Todo/ChangeLog/ROOT/Workspace AGENTS. No historical claim is rewritten as though the proposed shell already exists.

## Required Diagrams

RECOMMENDATION: arrows below mean owns/contains or invokes/consumes as labeled. Return projections/notifications are data flow, not reverse service construction. Six diagrams checked conceptually for domain/service/gateway ownership; Mermaid compilation/rendering NOT RUN.

### 1. Main shell ownership

~~~mermaid
flowchart TD
  App[Application composition] -->|constructs| MW[MainWindow shell]
  MW -->|contains| Top[Search and compact Active Context]
  MW -->|contains| Nav[Primary navigation and one flyout host]
  MW -->|contains| TW[Technician Workspace presentation host]
  MW -->|contains| Aux[One optional auxiliary region]
  MW -->|contains| Status[Status and safe activity]
  TW -->|invokes| Services[Owning application services]
  Aux -->|invokes through presenters| Services
  Services -->|owns effects through| RG[Repositories and Gateways]
~~~

### 2. Technician Workspace hosting

~~~mermaid
flowchart TD
  Guard[Guarded navigation intent] -->|activates| Host[Retained QStackedWidget]
  Host -->|one instance| T[TicketWorkspace]
  Host -->|one instance| K[KnowledgeWorkspace]
  Host -->|one instance| S[ScriptWorkspace]
  Host -->|future available singleton| C[Clipboard Center]
  T -->|presentation only| Split[Queue detail and record tabs]
  K -->|presentation only| KB[Article list detail and owner dialogs]
  S -->|presentation only| SR[Catalog and current diagnostic results]
  T --> TS[TicketService and TicketKnowledgeService]
  K --> KS[KnowledgeService]
  S --> SS[ScriptService and PowerShellService]
~~~

### 3. Active Technician Context propagation

~~~mermaid
flowchart LR
  Intent[Explicit record selection] --> Guard[Draft and pending guard]
  Guard --> Validate[Application resolver invokes source services]
  Validate -->|valid refs then atomic publish| Context[Application selected refs and revision]
  Context -->|purpose projection| Shell[Safe shell header]
  Context -->|frozen request snapshot| Tool[Owning tool use case]
  Context -->|future minimized projection| S2[Future S2 consumer]
  Tool -->|revalidate and authorize independently| Domain[Source application service]
~~~

### 4. Navigation to flyout to route or action

~~~mermaid
flowchart TD
  Trigger[Primary navigation trigger] -->|hover cached only| Fly[Single shell flyout]
  Trigger -->|chevron or keyboard focus| Fly
  Trigger -->|primary click| Route[Typed navigation request]
  Fly -->|explicit selected route| Route
  Fly -->|explicit action key and bound refs| Action[Owning use case adapter]
  Route --> Guard[Availability and draft guard]
  Guard --> Host[Activate retained workspace]
  Action --> Validate[Owner source target and policy checks]
  Validate --> Service[Owning application service]
~~~

### 5. Quick Ticket Drawer to TicketService

~~~mermaid
sequenceDiagram
  actor U as Technician
  participant D as Internal Quick Ticket Drawer
  participant P as Ticket-owned draft presenter
  participant R as ServiceTaskRunner
  participant T as TicketService
  participant DB as TicketRepository transaction
  U->>D: Explicit Quick Note
  D->>P: Bind original saved Ticket reference
  P->>R: Async owner revalidation
  R->>T: get_ticket_details(original target)
  T-->>P: Authoritative projection or unavailable
  U->>P: Explicit Save note
  P->>P: Freeze target draft and pending generation
  P->>R: Submit once
  R->>T: add_note(original target and values)
  T->>DB: Validate target and transact note/activity
  DB-->>T: Committed note
  T-->>P: Authoritative success via runner GUI callback
  P-->>D: Saved; refresh read only, retain pending through presentation
~~~

### 6. Responsive shell variants

~~~mermaid
flowchart TD
  Size[Measured usable client size and tool minimums] --> W[WIDE]
  Size --> M[MEDIUM]
  Size --> N[MINIMUM SUPPORTED]
  W --> WR[Labeled rail and singleton stack plus one optional side region]
  M --> MR[Icon rail and stack plus temporary internal slide-over]
  N --> NR[Icon rail and retained stack plus full-width internal task panel]
  WR --> A[Active Ticket Search and keyboard access remain reachable]
  MR --> A
  NR --> A
  W --> Policy[One auxiliary occupant and shared draft guard]
  M --> Policy
  N --> Policy
~~~

## Decision Register

Every row is a reviewable RECOMMENDATION, not recorded USER approval. DECIDE NOW means fixed enough at architecture depth for downstream planning after S1's approval; DESIGN NEXT means implementation/native detail; DEFER means no capability implied.

| Decision | Options | Recommendation | Evidence | Rationale | Consequences | Planning depth | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S1-D01 Primary host | Stack / tabs / MDI / docks | Existing retained singleton stack | E-M/E-T/E-K/E-S; C | Minimal compatible tool host | New shell chrome/guard, not replacement tools | DECIDE NOW | RECOMMENDED |
| S1-D02 MDI | Classic / tabbed / none | Reject both MDI forms | E-M; Q; host evaluation | No evidenced multi-document need; avoid overlap/focus/DPI state | Multi-record workflow must reopen host decision explicitly | DECIDE NOW | RECOMMENDED |
| S1-D03 Workspace tabs | Unlimited / bounded singleton / no row | No shell row MVP | Existing rail routes and Ticket detail tabs | One navigation hierarchy | Multiple records/pinned/temporary tabs absent | DECIDE NOW | RECOMMENDED |
| S1-D04 Active context owner | Widget / mutable composition / application refs | New explicit session selected-reference holder | E-A/F context | App selection, domains own records | Typed optional refs, atomic revision, no global DB | DECIDE NOW | RECOMMENDED |
| S1-D05 Active Ticket visibility | Ticket-only / permanent sidebar / compact global | Compact top-row control with narrow collapse | USER requirement; E-T | Always reachable without width loss | Safe labels and explicit target revalidation | DECIDE NOW | RECOMMENDED |
| S1-D06 Quick Ticket | Desktop popup / second editor / internal shared draft | Internal auxiliary drawer with one Ticket-owned note draft | E-T/E-D | Fast task, existing Ticket use cases | New presenter seam; preserve original target/pending ownership | DECIDE NOW | RECOMMENDED |
| S1-D07 Navigation placement | Left rail / top / both permanent | Adaptive left rail; top variant later | C/E-M; matrix | Stable primary destinations | Existing actions reused, no nested permanent tree | DECIDE NOW | RECOMMENDED |
| S1-D08 Flyout trigger | Hover only / primary click toggles / separate secondary | Hover plus chevron/keyboard; primary click navigates | Original S1; accessibility | Preserve navigation intent and touch access | Shared H/C/K policy; defaults 275/400 ms | DECIDE NOW; timing DESIGN NEXT | RECOMMENDED |
| S1-D09 Flyout focus | Always focus / no focus / explicit mode | Hover no focus; deliberate open focuses | Editor behavior E-T; original S1 | Avoid stealing typing | Scoped Escape/return; inner editor priority | DECIDE NOW | RECOMMENDED |
| S1-D10 Opacity | Whole-window fade / background alpha / opaque only | Background 90%, opaque text and accessibility fallback | USER request; Q/C | Temporary transparency with readability | Alpha/native contrast not certified | DECIDE NOW; actual rendering DESIGN NEXT | RECOMMENDED |
| S1-D11 Flyout anatomy | Module-specific layouts / common four groups | Context, quick actions, navigation/recent, full workspace | Original contract; matrix | Content once, shell mechanics once | Bounded items, omit irrelevant groups | DECIDE NOW | RECOMMENDED |
| S1-D12 Descriptors | Hard-code each popup / light static descriptors / plugins | New small pure descriptors, injected owner adapters | Searches; E-M; 0D composition principle | Three existing hard-coded routes need shared metadata | No arbitrary callbacks/text execution, no plugin loader | DECIDE NOW | RECOMMENDED |
| S1-D13 Search | Per-flyout engine / toolbar entry / provider-first global | One top entry routing existing local scopes | E-T/E-K/E-S; C | Explicit query, no provider prerequisite | Combined search later, no durable history | DECIDE NOW | RECOMMENDED |
| S1-D14 Status | Modal alerts / assistant overlay / status plus owner feedback | Existing status bar + bounded safe activity | E-M/E-R | Coherent async truth, no new history authority | Owner pending/commit state retained | DECIDE NOW | RECOMMENDED |
| S1-D15 Right region | Permanent competing sidebars / shared lease | One optional mutually exclusive auxiliary slot | Original S1/S2; width budget | Reserve S2 without empty permanent width | Dirty/pending negotiation before replacement | DECIDE NOW | RECOMMENDED |
| S1-D16 Responsive collapse | Fixed columns / breakpoints only / measured budgets | Initial bands plus real tool-minimum collapse | E-M/T 1000x700; C | Keep central work usable | Native/large-font fit required; thresholds adjustable | DECIDE NOW; dimensions DESIGN NEXT | RECOMMENDED |
| S1-D17 Restoration | Everything durable / none / session plus optional safe preferences | Session retention only MVP | E-M/F/0D | Avoid stale targets/privacy and speculative store | Cross-process record/query/draft restore absent | DECIDE NOW | RECOMMENDED |
| S1-D18 Durable geometry/module preference | New file / shared 0D / ignore | Later reviewed 0D-owned nonsensitive preference | 0D | One setting architecture | Not prerequisite for shell/1C planning | DEFER | DEFERRED |
| S1-D19 Native constants/chords | Freeze now / tune with bounded native evidence | Validate contrast, focus, bands, bridge, AltGr/chords before activation | T/Q/native plan | Architecture is stable without invented physical acceptance | Menus/buttons always fallback; no native PASS here | DESIGN NEXT | NOT_VERIFIED |

## Requires User Decision

NONE at S1 architecture-planning depth. Existing ownership and conservative bounded recommendations resolve the requested shell without authentication redesign, framework replacement, new persistence or provider selection. Pixel dimensions, artwork, alpha implementation and shortcut collision checks are native implementation detail, not manufactured architectural blockers. Independent review and explicit USER approval of this exact candidate remain mandatory; that lifecycle approval is not an unresolved design choice. If a later real multi-record/workspace requirement or owner conflict emerges, reopen its owning decision before implementation.

## Assumptions

| Assumption | Basis / explicit safe failure |
| --- | --- |
| One retained major tool instance is sufficient for first shell delivery | Inspected tools and USER workflow; INFERENCE, not usage telemetry. New multi-record demand requires reviewed extension, no silent MDI/tabs |
| 1000x700 logical window is an appropriate initial minimum target | Existing test assertions and canonical slice notes; actual new layout NOT VERIFIED. Collapse earlier or report unsupported, never clip controls |
| Private labels should be minimized in glance surfaces | Foundation/Clipboard privacy; employer policy NOT VERIFIED. Conceal identifying summaries by default and disable unavailable disclosure |
| Cached safe small projections can avoid hover work | Current loaded tools already retain records/status; providers/new recent APIs not established. Empty/stale safe status when projection absent |
| New draft/navigation adapters can safely retain existing tools | Same widget instances currently exist; adaptation is future implementation. Until validated, retain current conservative guards |

## Not Verified

Installed Qt/Python/native runtime versions; actual proposed GUI rendering, translucency/compositor performance, physical input, Narrator/high contrast/large font, shortcut conflicts/AltGr/RDP, mixed DPI/multi-monitor placement, startup/latency/memory distributions, operational database contents/integrity, real provider/account/permissions/credential terms or employer policy, future Clipboard/Settings/context/evidence/history/Device/Tenant APIs, untracked external DynamicHub prototypes, crash recovery or durable draft restoration. No proposed service/class is made current by this report. Current source-test inspection and historical doc PASS claims are not fresh or retained runtime evidence for S1.

## Risk Register

Likelihood UNKNOWN means no runtime/workflow measurement was made. Residual native/privacy limitations stay explicit; ownership assignments below are proposed responsibility within existing architecture.

| Risk | Likelihood | Impact | Mitigation | Residual Risk | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Nested navigation | MEDIUM | MEDIUM | Rail primary; no shell tab row; module-local detail tabs | Later content could add a second route hierarchy | Shell/module reviewers | OPEN |
| Excess horizontal width | HIGH | HIGH | One auxiliary region, central budget, compact bands | Large fonts/real tool minima unmeasured | Shell/module GUI | OPEN |
| Flyout flicker | UNKNOWN | MEDIUM | Stable dwell, pointer bridge, finite grace, generation | Native pointer/touch behavior untested | Shell flyout owner | NOT_VERIFIED |
| Hover-only accessibility | MEDIUM | HIGH | Chevron/menu/keyboard/touch same content | Narrator/actual focus order untested | Shell/accessibility | OPEN |
| Focus theft | UNKNOWN | HIGH | Hover no focus; explicit mode; do not restore over newer focus | Windows activation and keyboard routing need evidence | Shell/native GUI | NOT_VERIFIED |
| Draft loss | HIGH | HIGH | All hidden owners registered, retain-safe adapter, Cancel-default guard | Existing dialogs require adaptation; crash recovery excluded | Ticket/Knowledge/Clipboard presenters | OPEN |
| Module-specific duplicate popups | MEDIUM | MEDIUM | One descriptor and host; reviewed matrix | Future button-specific shortcuts may bypass contracts | Shell/review | OPEN |
| Stale Active Context | HIGH | HIGH | Typed refs/revision, owner invalidation and action-time revalidation | Notification lag/read failure still possible | App context/source owners | OPEN |
| Wrong Ticket target | HIGH | HIGH | Freeze source/target, atomic selection, shared note model, no inference from Clipboard | Owner validation must remain transactional where needed | Ticket/association owner | OPEN |
| Too many quick actions | MEDIUM | MEDIUM | Two-five actions, five recents maximum; full workspace escape | Module additions need matrix review | Module descriptor owners | OPEN |
| Provider calls on hover | MEDIUM | HIGH | Hover cached only; no prefetch/poll/provider call side effects | Hidden provider adapters need future inspection/tests | Module/application owners | OPEN |
| Semi-transparent readability | UNKNOWN | HIGH | Opaque text, measured contrast, 100% fallback | Composition/background variance unmeasured | Theme/accessibility | NOT_VERIFIED |
| DPI popup placement | UNKNOWN | HIGH | Logical coordinates, screen work area, clamp/flip/scroll | Mixed-scale transitions untested | Shell/native GUI | NOT_VERIFIED |
| Multi-monitor placement | UNKNOWN | HIGH | Actual trigger screen, negative coordinates, disconnect policy | Display topology/session changes untested | Shell/native GUI | NOT_VERIFIED |
| Mochi/right-panel competition | HIGH | MEDIUM | One lease, negotiate draft before replacement, collapsed affordance | Future S2 triggers must honor focused editor | Shell/S2 | OPEN |
| Workspace-tab sprawl | MEDIUM | MEDIUM | No shell tabs/multi-record MVP; explicit extension gate | Later workload may justify bounded expansion | Workspace/review | OPEN |
| Slow startup | UNKNOWN | MEDIUM | Reuse current tools, lazy future heavy modules, no provider prefetch | Existing optional filter/startup costs not measured | Bootstrap/module owners | NOT_VERIFIED |
| Over-engineered descriptor/plugins | MEDIUM | HIGH | Small pure static contributions and allowlisted route adapter | Metadata may grow; review necessity before abstraction | Python/shell architecture | OPEN |
| Testing loops | MEDIUM | HIGH | Finite native assertions/deadline; two identical failures stop | New harnesses need ownership/cleanup proof | Validation owner | OPEN |
| Callback gap / duplicate submit | HIGH | HIGH | Preserve owner pending through callback/refresh; draft generation | Runner.busy alone remains insufficient | Owning presenters | OPEN |
| False future capability | MEDIUM | HIGH | CURRENT/PLANNED/DEFERRED/NOT VERIFIED; explicit disabled reasons | Descriptors must bind actual composed capability | Composition/module owners | OPEN |
| Disclosure from labels/history | UNKNOWN | HIGH | Concealed safe summaries, no durable query/recent store by default | Ticket number/status still sensitive; real policy unknown | Source/privacy owners | NOT_VERIFIED |

## Recommended Vertical Slices

RECOMMENDATION: labels SHELL-01 etc. are planning decomposition only; assign actual repository slice numbers through the delivery skill when separately authorized. None is implemented. Each requires its own objective, exact scope/exclusions, acceptance criteria, required tests, independent review and integration authority. Windows-dependent work cannot integrate on headless evidence alone.

| Proposed slice | Bounded objective / output | Validation and dependencies / exclusion |
| --- | --- | --- |
| SHELL-01 | Pure navigation descriptors + adapter for existing Knowledge route; preserve menus and availability | Focused route/invalid-key/unavailable/draft-cancel tests; no flyout/provider/plugin framework |
| SHELL-02 | One reusable internal flyout mechanics host using static safe fixture content | Native hover/chevron/keyboard/touch-alternative/Escape/clamp/focus tests; no business actions, no provider data |
| SHELL-03 | Knowledge flyout end-to-end browse/search-focus only, real guarded route | Bounded local cached projection + empty/unavailable/stale tests; no favorites/history or create mutation in first slice |
| SHELL-04 | Minimal app selected-context holder for existing local Ticket/Company/Contact refs | Pure atomic revision/conflicting refs/cancel/stale projection tests plus Qt notifications; no Device/Tenant mapping/store |
| SHELL-05 | Active Ticket compact indicator + guarded Open Ticket from Knowledge | Wrong/missing target, creation no-target, stale read, draft/close/native minimum tests; no drawer write |
| SHELL-06a | Ticket-owned single note draft/pending adapter reused by full workspace | Existing note/status/classification/creation regression; save failure/committed reload/callback gap tests; no new domain rules |
| SHELL-06b | Internal Quick Ticket drawer + existing note save only | Native shared-editor binding, target change/cancel, failure and all-module reachability; depends 06a; no attachments |
| SHELL-06c | One KB RELATED-link entry through existing TicketKnowledgeService | Explicit source/target/revalidation/duplicate/missing/failed-link evidence; no generic Evidence claim |
| SHELL-07 | Other owner draft adapters (one dialog/workspace per slice) and retained navigation | Dirty close/hidden editor/conflict/failed-save tests; workspace tab host NOT NEEDED; no unlimited tabs |
| SHELL-08 | Shared auxiliary lease and compact responsive layout | Native 1000x700/wide/medium/large-font replacement/focus/draft checks; durable restoration split into later 0D consumer work |
| SHELL-09 | One remaining module's flyout per slice once owner capabilities exist | Matrix conformity, cache/privacy, no hover effects; Clipboard deferred until approved 1C/owner prerequisites; no giant all-module change |
| SHELL-10 | Native accessibility/DPI/focus hardening for exact bounded implemented shell | 100/125/150%, mixed screens/negative coords/taskbar/Narrator/high contrast; no new feature/API |
| LATER-SEARCH | One shell search entry and one existing scoped adapter at a time | Explicit submission/stale/cancel/route/empty/unavailable; aggregate engine not bundled |
| LATER-STATUS | Safe status/activity projection for one existing operation | Commit versus failed read, pending-gap/unconfirmed/accessibility; no new audit/job DB |
| LATER-SETTINGS | Only justified layout/hover preferences through separately implemented approved 0D service | Validation/desired-applied/default/privacy and native consumers; no parallel store; prerequisite shared Settings delivery |

No shell-tab implementation slice is recommended without a new justified workflow. Clipboard/Diagnostic evidence attachments, Applications launch, Reports and S2 actions need their own owning feature contracts/capabilities; do not bundle them into Quick Ticket or shell mechanics. Do not renumber existing repository slices or execute any recommendation here.

## Downstream Clipboard 1C Inputs

Conditional on independent S1 review, explicit USER approval and controlled integration, then separately authorized 1C planning. Clipboard 1C remains additionally dependent on S2's required closure; S1 alone does not waive that gate or start 1C. The existing 1C document is not authoritative GUI input to S1.

| 1C MAY consume later | Fixed S1 shell contract / 1C-owned specialization |
| --- | --- |
| MainWindow integration | Existing QMainWindow ownership; centrally composed services; typed guarded navigation on GUI thread, no direct domain effects |
| Technician Workspace host | One retained Clipboard Center singleton in stack; module-local list/Inspector/split layout belongs to 1C; no independent desktop history window |
| Navigation/flyout mechanics | Shared H/C/K/timing/focus/clamp/anatomy; explicit click primary route; cached safe hover only |
| Clipboard slot/content | clipboard.center route and matrix content; Capture/Save/Pin/Evidence semantics from 1A, capability truth/action routing from 1B; missing actions unavailable |
| Active Technician Context | Optional owner-qualified refs/immutable revision; explicitly accepted selections, no clipboard-derived Ticket/Device/Tenant guesses |
| Active Ticket Context | Reachable compact control, explicit original saved target; absent Ticket valid for Clipboard work |
| Quick Ticket | Internal shared auxiliary region; Ticket-owned note draft; source+target confirmation and owning association use case for future Attach, not existing capability claim |
| Global Search | One entry and local scoped adapter; 1C designs approved own filters/query/paging, no flyout engine or durable history default |
| Responsive shell | Wide/medium/minimum central budgets; 1C collapses its Inspector; no permanent competing right sidebar |
| Mochi/DynamicHub reservation | Same temporary auxiliary lease, no stolen width/focus; S2 owns later context/actions |
| Keyboard/accessibility | All hover content reachable otherwise; editor shortcuts preserved; Win+Alt+C remains 1B; explicit scoped activation/close/focus return |
| Async/status conventions | Existing dispatch/GUI callbacks with source/request generation and pending owner guards; capture/save committed vs refresh failure/unconfirmed distinction |
| Privacy/restoration | Concealed minimized flyout/status; no raw persistent context/query/draft history imposed by shell; source expiry and safety remain 1A/1B |

1C must still design Clipboard Center columns/history/filtering/Inspector/actions, raw access eligibility, completeness/retention display, drafts/selection adapter and owned native tests. It may not silently change S1 hosting/focus/auxiliary rules, 1A Item/Event/Save/Pin/Evidence/privacy, 1B capture/IPC/HUD or Foundation owners. Missing source capability is unavailable rather than implemented by shell. Any owning-contract conflict stops that local decision and goes to the owner.

## Acceptance Criteria

The exact original S1 criteria are reproduced below without substitution. PASS is an author-side architecture-depth coverage assessment backed by named report sections/source evidence; it is not executable test PASS or independent approval.

| ID | Original criterion | Result | Evidence / section |
| --- | --- | --- | --- |
| AC-01 | Existing MainWindow/navigation architecture inspected. | PASS | E-M; Verified Current Shell |
| AC-02 | Existing workspaces inspected. | PASS | E-T/E-K/E-S; inspected layouts/routes/lifecycle |
| AC-03 | Existing draft-protection patterns inspected. | PASS | E-T, creation/new/edit dialogs; current gaps explicitly recorded |
| AC-04 | Technician Workspace role explicit. | PASS | Technician Workspace |
| AC-05 | Workspace ownership does not absorb domains. | PASS | Technician Workspace; MainWindow Integration; Security |
| AC-06 | Primary workspace-host pattern recommended. | PASS | Workspace Hosting: retained singleton stack |
| AC-07 | Classic MDI explicitly evaluated. | PASS | Workspace Hosting: classic/tabbed MDI rejection |
| AC-08 | Main navigation architecture defined. | PASS | Main Navigation inventory and guard |
| AC-09 | Reusable flyout mechanics defined. | PASS | Flyout Mechanics: single host/H/C/K/placement |
| AC-10 | Hover is not the only access method. | PASS | Chevron/keyboard/touch/menu alternatives |
| AC-11 | Flyout focus behavior defined. | PASS | Hover no focus, explicit focus, scoped close/return |
| AC-12 | Flyout opacity/readability defined. | PASS | Background alpha/opaque text/accessibility fallback |
| AC-13 | Flyout timing bounded. | PASS | 275/400 ms recommendations, finite cancellable timers |
| AC-14 | Flyout content anatomy defined. | PASS | Flyout Content Contract: four optional ordered groups |
| AC-15 | Navigation Surface Matrix complete. | PASS | Twelve rows and all sixteen required columns |
| AC-16 | Tickets flyout defined. | PASS | Matrix Tickets; actual Ticket status vocabulary |
| AC-17 | Clipboard flyout defined. | PASS | Matrix Clipboard; 1A/1B source/action boundaries |
| AC-18 | Knowledge flyout defined. | PASS | Matrix Knowledge; existing scope/search/dialog capabilities |
| AC-19 | Diagnostics flyout defined. | PASS | Matrix Diagnostics; existing Scripts alias versus future host |
| AC-20 | Scripts/Automation flyout defined. | PASS | Matrix Scripts; no direct executable payload |
| AC-21 | Settings flyout defined. | PASS | Matrix Settings; truthful current Mochi versus future shared service |
| AC-22 | Mochi flyout boundary defined. | PASS | Matrix Mochi; cosmetic controls separate from S2 |
| AC-23 | Active Technician Context defined. | PASS | Application lifetime, typed refs, atomic revision/freshness/guard |
| AC-24 | Active Ticket Context defined. | PASS | Compact visibility; no-target/create/stale/deleted handling |
| AC-25 | Quick Ticket Drawer defined. | PASS | Internal surface/shared draft/async/context/responsive behavior |
| AC-26 | Ticket mutations remain Ticket-owned. | PASS | TicketService and RELATED link/association owners; diagram 5 |
| AC-27 | Global Search placement defined. | PASS | One top entry/narrow affordance/scoped adapters |
| AC-28 | Workspace tab strategy defined. | PASS | No shell row/multi-record/pinned/temporary tabs MVP |
| AC-29 | Responsive shell behavior defined. | PASS | Three band matrix and measured central minima |
| AC-30 | Mochi/DynamicHub space reserved. | PASS | One auxiliary region with replacement guards/collapse |
| AC-31 | Keyboard model defined. | PASS | Current inventory + proposed scoped bindings/collision gates |
| AC-32 | Accessibility requirements defined. | PASS | Non-hover access/visible focus/plain reasons/contrast/order |
| AC-33 | DPI/multi-monitor validation planned. | PASS | Future native matrix, all runtime cases NOT RUN |
| AC-34 | Settings inputs classified. | PASS | CORE/LIKELY/FUTURE/NOT NEEDED inventory; no store |
| AC-35 | Hover does not trigger provider work. | PASS | Cached-only hover; no capture/read/run/inference/provider work |
| AC-36 | Security/authority preserved. | PASS | No direct SQL/process/provider/credential effects; owner revalidation |
| AC-37 | Reuse assessment complete. | PASS | Required components plus new/not-needed/unverified concepts |
| AC-38 | Decision register complete. | PASS | S1-D01..D19; all required fields/status/depth |
| AC-39 | Risk register complete. | PASS | Nineteen mandatory concerns plus lifecycle/privacy risks |
| AC-40 | Future slices small/reviewable. | PASS | Separate mechanics/one-module/one-write slices and dependencies |
| AC-41 | No production implementation occurred. | PASS | Git allowed-path diff; only S1 append |
| AC-42 | No database change occurred. | PASS | No runtime/DB invocation or schema change; Git scope |
| AC-43 | Foundation ownership not silently redefined. | PASS | Approved Inputs/F authority, application refs not records/permissions |
| AC-44 | Clipboard 1C can consume S1 without inventing shell behavior. | PASS | Explicit conditional downstream matrix; S2 gate retained |

Architecture coverage: 44/44 PASS. No replacement criteria and no claims of new functionality. Runtime obligations are listed separately below.

## Validation

Environment: WINDOWS_NATIVE workstation, read-only repository/GitHub/source inspection and documentation static checks. FRESH means executed for this candidate; source/test inspection is not runtime evidence. No runtime suite result is retained as S1 PASS.

| Required architecture validation | Result | Evidence / limit |
| --- | --- | --- |
| Dependency gate | PASS | main/live-remote equality; merged records 66/67/68/70/71/72/73/75 and ancestry |
| Current shell inspection | PASS | E-M/E-T/E-K/E-S/E-R/E-A and inspected T sources |
| Technician Workspace architecture | PASS | Responsibilities/activation/lifecycle/focus/guards/restoration explicit |
| Workspace hosting | PASS | Six options evaluated, retained stack recommended, MDI rejected |
| Main navigation | PASS | Actual menu inventory versus twelve proposed module metadata rows |
| Flyout mechanics | PASS | Shared bounded H/C/K/timers/clamp/focus/opacity, no hover effects |
| Flyout content matrix | PASS | Twelve modules, sixteen columns, honest capability/content states |
| Active Technician Context | PASS | Separate app-selected typed refs, revision/freshness/atomic guard |
| Active Ticket Context | PASS | Global minimized projection and original-target safety |
| Quick Ticket Drawer | PASS | One Ticket-owned draft; service-only effects, failure/close/context behavior |
| Draft preservation | PASS | Detection per owner, hidden participants, save/failed-read/pending separation |
| Responsive layout | PASS | Three variants/central budget/one auxiliary occupant; runtime fit NOT VERIFIED |
| Keyboard/accessibility | PASS | Inventory and non-hover/focus/contrast/editor-safe contract; runtime NOT VERIFIED |
| DPI/multi-monitor plan | PASS | Explicit future native conditions, no current native GUI PASS |
| Mochi/DynamicHub coexistence | PASS | Slot lease/guard/focus/collapse, S2 not executed |
| Settings boundary | PASS | Classified prospective inputs, no implementation/runtime selection persistence |
| Security/authority | PASS | Source/service/gateway owners unchanged; privacy/offline/explicit intent |
| Reuse assessment | PASS | Required actual components and no duplicate infrastructure |
| Scope control | PASS | S1 only, no downstream or canonical edits, index empty |
| Production changes | NONE | Entire tracked diff confined to S1 |
| Database changes | NONE | No migrations/runtime data access |
| Original contract prefix | PASS | Exact original raw prefix and integrated Git-normalized prefix comparison |
| Required report/matrix/register/diagram structure | PASS | Deterministic heading, row/column, ID, criterion and fence checks |
| Relative Markdown link destinations | PASS | Static existence checks for appended local links; no protected file target |
| Git diff whitespace / allowed paths / index | PASS | diff --check, diff/status/index final inspection |
| Diagrams conceptual ownership | PASS | Six source diagrams checked for shell/domain/service boundaries |
| Mermaid compilation/rendering | NOT RUN | No renderer installed or invoked; source presence is not rendering evidence |
| Independent architecture review | NOT RUN | Required NEXT gate; self-check cannot grant approval |
| Application runtime | NOT RUN | Architecture planning only |
| Database tests/integrity checks | NOT RUN | No schema/data/runtime scope |
| GUI tests | NOT RUN | Test source inspected only |
| Integration tests | NOT RUN | Test source inspected only |
| AHK tests | NOT RUN | No host/runtime changes |
| PowerShell tests | NOT RUN | Execution boundary unchanged |
| Mochi runtime tests | NOT RUN | Cosmetic/context runtime not started |
| Native Windows GUI tests | NOT RUN | No proposed shell exists; no screenshots/physical-input claim |

Static PASS is bounded to document structure, deterministic preservation and inspected architecture coverage. It cannot certify rendering, execution, data integrity, provider permission or native product usability. No dependency/tool installation, operational DB access or retry loop was used. Final immutable candidate identity is recorded outside this document after validations close.

## Result

READY_FOR_WORKSPACE_REVIEW

Author-side execution is complete at architecture-planning depth: dependency gate PASS, current shell/reuse assessed, requested shell/context/navigation/flyout/Quick Ticket/responsive/security boundaries defined, six conceptual diagrams, decision/risk registers, explicit downstream inputs and 44/44 criteria covered. Requires User Decision: NONE at this depth. Candidate remains unapproved, unstaged, uncommitted, unpushed and not integrated; native/runtime behavior NOT RUN / NOT VERIFIED.

Next gate: INDEPENDENT S1 ARCHITECTURE REVIEW -> explicit USER approval -> controlled S1 integration. STOP. S2, Clipboard 1C, implementation, canonical synchronization, Workspace AGENTS creation and Git publication are not authorized by this result.
