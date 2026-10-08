# F7Hub Clipboard Agent Guidance

This file governs Clipboard feature planning, implementation, testing, review
and documentation across F7Hub.

It specializes, but does not replace:

- [repository-root AGENTS.md](../../../AGENTS.md)
- [ROOT.md](../../../ROOT.md)
- [Planning AGENTS.md](../AGENTS.md)
- approved Foundation contracts, routed through
  [Foundation AGENTS.md](../Foundation/AGENTS.md)
- applicable technology-specific `AGENTS.md`
- applicable project skills

Explicit user requirements and approved architecture remain authoritative.

If this file conflicts with an approved owning architecture contract, stop and
identify the conflict rather than silently overriding it.


## Scope

Read this file before substantial work involving any Clipboard feature,
including work under:

- `Docs/Planning/Clipboard/`
- `Database/`
- `Python/`
- `Tests/`
- `AutoHotkey/`
- `Config/`
- Clipboard-related Settings
- Clipboard-to-Ticket/Evidence integrations
- Clipboard-to-Diagnostics integrations
- Clipboard-to-DynamicHub/Mochi integrations

The repository-root AGENTS.md explicitly routes Clipboard tasks to this file,
including tasks outside this directory. Read it for every Clipboard Center
task, including planning, implementation, testing, review and documentation.
More-specific technology guidance still applies to the files being worked on.

Reading this file grants no implementation, capture, execution or Git
integration authority. Apply the current task scope and requested lifecycle
gate. Planning and independent review remain read-only for production.

The physical file location does not determine architectural ownership.

A Clipboard change in `Database/` is still Clipboard feature work.

A Clipboard change in `Python/f7hub/gui/` is still Clipboard feature work.


## Authoritative Clipboard Contracts

Clipboard work must consume the approved contracts rather than recreate them.
Verify the current approval, review and integration evidence for each required
input before relying on it. File existence, dependency lists and historical
author-side readiness statements do not establish current approval or runtime
availability. This guidance does not approve an architecture phase or slice.
Load only the owner sections and dependency contracts needed for the task.

### Clipboard 1A

[1A_Clipboard_Domain_Data_Lifecycle.md](1A_Clipboard_Domain_Data_Lifecycle.md)

Owns:

- Clipboard Item semantics
- Capture Event semantics
- content identity
- genuine capture semantics
- replay/idempotency principles
- sensitivity/privacy lifecycle
- retention
- saved/pinned state
- Evidence/hold relationships
- Clipboard domain/data ownership

### Clipboard 1B

[1B_AHK_Python_Clipboard_Capture_IPC_Quick_HUD_Architecture.md](1B_AHK_Python_Clipboard_Capture_IPC_Quick_HUD_Architecture.md)

Owns:

- AHK/manual capture boundary
- Python capture adapter boundary
- IPC
- Quick HUD
- capture acknowledgements
- host/hotkey behavior
- capture transport behavior

### Clipboard 1C

[1C_PySide6_Clipboard_Center.md](1C_PySide6_Clipboard_Center.md)

Owns:

- Clipboard Center presentation
- workspace behavior
- views
- read models
- search/filter presentation
- Inspector presentation
- async/stale GUI behavior
- paging presentation
- navigation/flyout integration
- responsive/accessibility behavior

### Workspace S1

[S1 Main Shell / Technician Workspace / Navigation](../Workspace/S1_Main_Shell_Technician_Workspace_Navigation.md)

Owns:

- MainWindow shell
- workspace hosting
- navigation
- reusable flyout mechanics
- Active Technician Context
- Active Ticket access
- Quick Ticket shell behavior
- shared auxiliary-region mechanics

### Workspace S2

[S2 Mochi / DynamicHub / Context Actions](../Workspace/S2_Mochi_DynamicHub_Context_Actions.md)

Owns:

- DynamicHub
- Mochi presentation boundary
- context-aware action routing
- invocation-time operation binding
- provider-safe action architecture

### Foundation

Foundation remains authoritative for:

- layer ownership
- interoperability
- taxonomy
- Settings
- secrets
- security
- shared context
- integration boundaries
- provenance


## Core Clipboard Invariants

The following are architectural invariants unless an owning contract is
explicitly reviewed and changed.

### Item and Event are different concepts

A Clipboard Item represents eligible content identity.

A Capture Event represents a genuine capture occurrence.

Repeated capture of identical content may reuse one Item.

A genuine new capture may create a new Event.

Transport retry or replay must not manufacture another Event.

Do not collapse Item and Event merely to simplify a table, query or GUI.


### Capture does not imply persistence

Reading the OS Clipboard or receiving an IPC message does not automatically
authorize persistence.

Privacy/sensitivity admission remains an owning Clipboard responsibility.

Do not infer that because storage tables exist, capture may write to them.


### Persistence does not imply capture readiness

A database migration, repository or service does not activate:

- OS Clipboard monitoring
- manual capture
- AHK hotkeys
- IPC
- Quick HUD
- background capture

Those require separately authorized delivery.


### GUI does not own persistence

Preserve:

`PySide6 GUI → ClipboardService → ClipboardRepository → SQLite`

The GUI must not:

- execute SQL
- open the Clipboard database directly
- own domain validation
- implement capture semantics
- infer persistence rules from visible widgets


### Services own use cases

ClipboardService owns application-level Clipboard workflows.

ClipboardRepository owns persistence and queries.

Infrastructure owns connection mechanics.

Domain types remain independent of Qt and SQLite implementation details.


## Slice Families

Use these planning labels to keep responsibilities clear.

### `Dxx`

Clipboard data/domain/service prerequisites.

Examples:

- migrations
- domain/read types
- repositories
- services
- query sources

A D slice must not silently implement GUI or capture behavior.


### `CC-xx`

Clipboard Center GUI vertical slices.

Examples:

- workspace
- Recent view
- search/filter UI
- Inspector
- safe actions

A CC slice may depend on a D slice.

A CC slice must not implement missing data/domain capability inside the GUI
merely to unblock itself.


### Capture / IPC slices

Capture, AHK, IPC and Quick HUD delivery must remain explicitly scoped and
consume 1B.

Do not place capture behavior inside Dxx or CC-xx merely because those layers
need Clipboard data.


## Inspect Before Creating

Before adding any Clipboard:

- table
- migration
- domain type
- repository
- service
- adapter
- IPC message
- GUI component
- Settings key
- action
- relationship

perform:

`SEARCH → IDENTIFY → REUSE / EXTEND → CREATE ONLY IF NECESSARY`

Inspect current implementation, migrations, tests and approved contracts.

Do not infer absence from memory or older planning reports.


## SQLite and Persistence

Clipboard persistence must use normal F7Hub SQLite infrastructure.

Requirements include:

- versioned migrations
- primary keys
- foreign keys
- constraints
- justified indexes
- parameterized SQL
- transactions for logical writes
- migration checksum preservation
- `PRAGMA foreign_keys = ON`
- the documented `busy_timeout` default (5000 ms), unless approved configuration
  changes it
- integrity validation where persistence changes
- isolated synthetic test databases

Do not:

- modify released migrations
- disable foreign keys to force success
- access operational data during tests
- create JSON blobs to avoid stable relational structure without justification
- introduce FTS before a slice actually requires search


## Recent Query Rules

The user-provided initial D01 Recent query scope is intentionally bounded.
When that slice is explicitly authorized, use the limits below; these limits
do not themselves authorize delivery or establish that D01 is implemented.

Initial Recent delivery:

- first page only
- default limit 50
- hard maximum 100
- `has_more`
- deterministic ordering
- deterministic unique tie-breaker
- query at most `limit + 1`
- return at most `limit`
- no OFFSET pagination
- no cursor contract yet

This first-page scope does not replace 1C's eventual keyset paging
architecture. Before a later slice changes the query contract, verify its
approved owning requirements; do not treat these initial limits as permanent
restrictions on separately authorized extensions.

Keyset Next/Previous, typed cursors and stale-traversal behavior require a
separately authorized extension.

Do not make paging state a GUI-owned substitute for the owner query contract.


## Privacy and Sensitive Content

Clipboard content is untrusted.

Persistence and presentation must use the sensitivity/privacy rules owned by
1A.

Secrets must not enter ordinary Clipboard history.

Do not create:

- secret override settings
- hidden persistence bypasses
- automatic external transmission
- logging of unrestricted raw Clipboard content

Local visibility does not equal consent to send content externally.

DynamicHub, Mochi, AI and providers receive only explicitly approved,
purpose-filtered projections.


## Raw Content

Raw Clipboard text must not become an execution channel.

Never implement:

`Clipboard text → shell`

or:

`Clipboard text → PowerShell`

or:

`Clipboard text → arbitrary process`

or equivalent indirect execution.

Clipboard content may become validated input to an approved operation only
through the owning service/action contract.


## Entity and Tag Boundaries

Detected Clipboard Entity occurrences are not automatically authoritative
records.

Do not automatically create:

- Companies
- Users
- Devices
- Tickets
- Tenants

from Clipboard content.

Use approved taxonomy/provenance semantics.

Tags are global F7Hub Tags.

Do not create a competing Clipboard-only Tag catalog.


## Ticket and Evidence Boundary

Clipboard Center does not own Ticket lifecycle.

Ticket association must route through the owning Ticket/association service.

Changing Active Ticket must not retarget an already accepted operation.

Evidence and protection holds must prevent unsafe deletion/expiration where
required by the owning lifecycle contract.

Do not silently release a hold because a related target is temporarily
unavailable.


## Diagnostics Boundary

Clipboard content must not bypass Diagnostics ownership.

Opening or proposing a diagnostic is different from executing it.

Only approved registered operations with validated typed inputs may execute.

No arbitrary copied-command execution.


## DynamicHub and Mochi Boundary

Clipboard may expose an approved privacy-filtered context projection.

DynamicHub remains a workflow/action surface, not Clipboard persistence owner.

Mochi remains presentation/advisory.

Do not:

- create a competing AI panel inside Clipboard Center
- send raw history automatically
- treat selection as execution permission
- retarget accepted work when current selection changes


## Invocation-Time Binding

Accepted operations must retain their invocation-time binding.

Where relevant capture:

- source Clipboard Item
- target
- Ticket association or explicit none
- context revision
- provider/tenant scope
- validated parameters

A later GUI selection or Active Ticket change affects future actions only.

Late results remain associated with the original accepted operation.


## Async and Stale Results

GUI reads must be bounded and must not block the Qt event loop.

Where asynchronous reads are used:

- identify requests
- track relevant generations/revisions
- reject stale success
- reject stale failure
- preserve current selection safely
- do not overwrite a newer query with an older result

Worker threads must not directly mutate Qt models/widgets.


## Testing

Clipboard slices require tests appropriate to their actual scope.

Data slices normally require:

- migration tests
- constraint tests
- repository tests
- service tests
- integrity checks
- foreign-key checks
- success and failure paths
- empty-state behavior
- deterministic ordering
- no unintended writes

GUI slices normally require:

- focused GUI tests
- navigation/state tests
- async/stale-result tests where applicable
- regression tests
- Windows-native validation for visible/native behavior

Capture/IPC slices require their own bounded native/contract validation.

For persistence checks, `PRAGMA integrity_check` must return `ok` and
`PRAGMA foreign_key_check` must return zero violations. Select checks for the
actual change; documentation-only guidance does not require runtime tests.

Report fresh, retained and historical evidence separately, using `PASS`,
`FAIL`, `NOT RUN` or `BLOCKED` and an environment qualifier. A
`CLOUD_PORTABLE` PASS does not establish `WINDOWS_NATIVE` behavior. Apply the
root native-validation gate before integration of Windows-dependent changes.

Never claim a test passed unless it actually ran and passed.


## Test Data

Use synthetic Clipboard data only.

Do not place real employer/customer Clipboard contents in:

- tests
- fixtures
- seed data
- documentation
- screenshots committed to Git
- logs

Production modules must never import test fixture helpers.


## Loop Guard

Do not repeat the same failed test, screenshot check, launch, focus attempt or
IPC validation more than twice with:

- unchanged candidate
- unchanged environment/state
- unchanged hypothesis

After two identical unchanged failures:

`STOP → DIAGNOSE → REPORT`

Do not enter retry spirals.


## Documentation Routing

Use [Docs/19_DocumentationIndex.md](../../19_DocumentationIndex.md) to route
the minimum relevant canonical documentation. Assess impact and update only
affected owners; proposed capabilities must remain identified as planned.

Clipboard persistence/schema changes require review of:

- [07_Database.md](../../07_Database.md)
- [08_ERD.md](../../08_ERD.md)
- [09_SQLSchema.md](../../09_SQLSchema.md)

Python/service/repository changes require review of:

- [13_PythonArchitecture.md](../../13_PythonArchitecture.md)

Visible GUI changes require review of:

- [05_GUI.md](../../05_GUI.md)
- [06_SystemArchitecture.md](../../06_SystemArchitecture.md) only when architecture actually changes

AHK/capture host changes require review of:

- [11_AHKArchitecture.md](../../11_AHKArchitecture.md)

PowerShell execution-boundary changes require review of:

- [12_PowerShellArchitecture.md](../../12_PowerShellArchitecture.md)

Meaningful delivery status/history should update the applicable:

- [17_Todo.md](../../17_Todo.md)
- [18_ChangeLog.md](../../18_ChangeLog.md)
- [CURRENT_STATE.md](../../Status/CURRENT_STATE.md)

Do not document planned capabilities as implemented.


## Worktree and Git Safety

Apply the existing
[vertical-slice-delivery skill](../../../.agents/skills/vertical-slice-delivery/SKILL.md)
when delivering or reviewing a Clipboard slice. Its lifecycle/evidence
procedures do not expand the current authorization.

Production Clipboard slices should normally use isolated worktrees.

Do not stage unrelated work.

Never use:

`git add .`

Use explicit candidate path allowlists.

Review approval does not authorize integration.

Commit, push, PR creation and merge each require task authorization.
Integration requires explicit user authorization.


## Completion Gate

Before declaring a Clipboard slice complete, verify:

- requested outcome delivered
- owner boundaries preserved
- privacy/security considered
- Item/Event semantics preserved where relevant
- no unauthorized capture or execution path introduced
- database integrity preserved where applicable
- success and failure paths tested
- required native validation completed where applicable
- documentation synchronized
- unrelated changes excluded
- remaining limitations recorded
- next slice not started automatically


## Guiding Rule

Build only the Clipboard capability required by the current slice.

Do not solve a missing dependency in the wrong layer.

A missing D capability blocks or precedes a CC feature.

A missing capture capability belongs to the 1B/capture owner.

A missing shared shell/context capability belongs to S1/S2.

Prefer small, independently testable, reversible delivery over feature
accumulation.
