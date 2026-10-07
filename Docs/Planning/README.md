# F7Hub Architecture Planning

## Purpose

This directory contains architecture, design, and implementation-planning documents for future F7Hub development.

These documents are **planning artifacts**, not proof that functionality has been implemented.

The canonical numbered documentation under `Docs/` remains the authoritative description of approved and implemented F7Hub architecture and behavior.

Planning documents may contain:

- verified current-state observations
- architectural recommendations
- decision registers
- risk registers
- proposed domain models
- proposed contracts
- proposed GUI architecture
- implementation sequencing
- future vertical-slice recommendations

Approved planning decisions should be synchronized into the appropriate canonical documentation when implementation occurs.

---

# Planning Rules

All planning work follows:

```text
UNDERSTAND
    ↓
INSPECT
    ↓
PLAN
    ↓
IMPLEMENT
    ↓
TEST
    ↓
REVIEW
    ↓
DOCUMENT
```

Before creating a new service, repository, table, taxonomy, contract, configuration mechanism, GUI component, or integration:

```text
SEARCH
    ↓
IDENTIFY
    ↓
REUSE / EXTEND
    ↓
CREATE ONLY IF NECESSARY
```

Planning must distinguish:

```text
FACT
ASSUMPTION
INFERENCE
RECOMMENDATION
NOT VERIFIED
```

A planning document must never describe proposed behavior as already implemented.

---

# Source of Truth

When information conflicts, use this priority:

1. Explicit user requirement
2. Approved architecture
3. Canonical F7Hub documentation
4. Validated implementation
5. Tests
6. Established project conventions
7. Engineering inference
8. Unapproved planning proposal

Planning documents do not override implemented or approved architecture merely because they are newer.

---

# Planning Status Vocabulary

Use these statuses consistently.

| Status | Meaning |
|---|---|
| `NOT_STARTED` | Planning has not yet been executed against the repository. |
| `IN_PROGRESS` | Codex is currently investigating or preparing the plan. |
| `REQUIRES_DECISION` | One or more architectural decisions require review. |
| `BLOCKED` | Planning cannot safely continue. |
| `READY_FOR_REVIEW` | Planning report is complete and awaiting review. |
| `APPROVED` | Architecture has been reviewed and accepted. |
| `SUPERSEDED` | Replaced by a newer approved planning document. |
| `ARCHIVED` | Retained for historical reference only. |

Do not use `IMPLEMENTED` for planning documents.

Implementation status belongs in the canonical documentation, current-state documentation, feature-slice records, and Git history.

---

# Planning Sequence

The current architecture-planning program is intentionally dependency ordered.

```text
FOUNDATION
────────────────────────────────────

0A  Master Foundation Architecture
 ↓
0B  Global JSON / Interoperability Contract
 ↓
0C  Classification / Taxonomy Architecture
 ↓
0D  Settings / Configuration Architecture


CLIPBOARD
────────────────────────────────────

1A  Clipboard Domain & Data Lifecycle
 ↓
1B  AHK ↔ Python Clipboard Integration
 ↓
1C  PySide6 Clipboard Center


FUTURE
────────────────────────────────────

2   Diagnostic Architecture
 ↓
3   Statistical Analytics
 ↓
4   Mochi Assistant Architecture
```

Later phases must consume approved decisions from earlier phases rather than redefining them independently.

---

# Phase 0: Foundation Architecture

Directory:

```text
Docs/Planning/Foundation/
```

## Phase 0A: Master Foundation Architecture

**Status:** `NOT_STARTED`

**Purpose:**

Establish the global architecture map before designing individual features.

Primary questions:

- Which subsystem owns which responsibility?
- Which technology owns which responsibility?
- What are the allowed dependency directions?
- Where are the security boundaries?
- Which existing F7Hub capabilities should be reused?
- Which architectural decisions must be made before feature planning?

Expected result:

```text
READY_FOR_FOUNDATION_DESIGN
```

---

## Phase 0B: Global JSON / Interoperability Contract

**Status:** `NOT_STARTED`

**Depends on:**

```text
Phase 0A APPROVED
```

**Purpose:**

Define how F7Hub components exchange structured information.

Primary areas:

- common contract conventions
- message identity
- commands
- queries
- events
- results
- errors
- versioning
- compatibility
- validation
- AHK ↔ Python communication
- Python ↔ PowerShell communication
- Mochi context and actions
- security boundaries
- transport independence

Expected result:

```text
READY_FOR_TAXONOMY_DESIGN
```

---

## Phase 0C: Classification & Taxonomy Architecture

**Status:** `NOT_STARTED`

**Depends on:**

```text
Phase 0A APPROVED
Phase 0B APPROVED
```

**Purpose:**

Define what F7Hub information means.

The architecture must clearly separate:

```text
Category
Type / Kind
Entity
Entity Type
Tag
Tag Family
Status
Priority
Relationship
Metric
Insight
Provenance
Confidence
```

Primary areas:

- existing taxonomy reuse
- global Tag Catalog
- Tag Families
- aliases
- module scopes
- Entity taxonomy
- Entity normalization
- relationship semantics
- classification provenance
- bilingual labels
- search implications
- analytics implications

Expected result:

```text
READY_FOR_SETTINGS_ARCHITECTURE
```

---

## Phase 0D: Settings & Configuration Architecture

**Status:** `NOT_STARTED`

**Depends on:**

```text
Phase 0A APPROVED
Phase 0B APPROVED
Phase 0C APPROVED
```

**Purpose:**

Define what F7Hub behavior may be configured and where configuration belongs.

Primary areas:

- SettingsService ownership
- SQLite vs configuration files
- defaults
- persisted overrides
- effective values
- validation
- configuration precedence
- module settings
- privacy settings
- security-sensitive settings
- secret boundary
- AHK configuration
- PowerShell configuration
- Mochi configuration

Expected result:

```text
READY_FOR_FEATURE_ARCHITECTURE
```

---

# Phase 1: Clipboard Architecture

Directory:

```text
Docs/Planning/Clipboard/
```

---

## Phase 1A: Clipboard Domain & Data Lifecycle

**File:**

```text
Docs/Planning/Clipboard/1A_Clipboard_Domain_Data_Lifecycle.md
```

**Status:** `NOT_STARTED`

**Depends on:**

```text
Phase 0A APPROVED
Phase 0B APPROVED
Phase 0C APPROVED
Phase 0D APPROVED
```

**Purpose:**

Define the Clipboard domain independently of its Windows integration and GUI.

Primary areas:

- Clipboard Item
- Capture Event
- raw vs normalized content
- deduplication
- content hashing
- primary Kind
- Entity extraction
- Tags
- sensitivity
- secret handling
- Save
- Pin
- Evidence
- retention
- expiration
- cleanup
- Ticket relationships
- Diagnostic relationships
- search
- FTS5
- Analytics boundary
- Mochi boundary

Expected result:

```text
READY_FOR_CLIPBOARD_INTEGRATION_DESIGN
```

---

## Phase 1B: AHK ↔ Python Clipboard Capture, IPC & Quick HUD

**File:**

```text
Docs/Planning/Clipboard/1B_AHK_Python_Clipboard_Capture,_IPC_Quick_HUD_Architecture.md
```

**Status:** `NOT_STARTED`

**Depends on:**

```text
Phase 1A APPROVED
```

**Purpose:**

Define the Windows-facing Clipboard integration.

Primary areas:

- manual capture hotkey
- Windows Clipboard access
- source application context
- AHK responsibilities
- Python responsibilities
- interoperability contract
- IPC transport
- timeouts
- retries
- idempotency
- security
- F7Hub availability
- Quick HUD
- contextual action routing
- native Windows testing

Expected result:

```text
READY_FOR_CLIPBOARD_GUI_DESIGN
```

---

## Phase 1C: PySide6 Clipboard Center

**File:**

```text
Docs/Planning/Clipboard/1C_PySide6_Clipboard_Center.md
```

**Status:** `NOT_STARTED`

**Depends on:**

```text
Phase 1A APPROVED
Phase 1B APPROVED
```

**Purpose:**

Define the complete persistent Clipboard Center user interface.

Primary areas:

- MainWindow integration
- Clipboard internal navigation
- Recent
- Saved
- Pinned
- URLs
- Commands
- PowerShell
- Errors & Logs
- Networking
- Ticket Evidence
- Diagnostic Evidence
- search
- filtering
- table model
- Inspector
- Entities
- Tags
- Capture History
- Relationships
- Retention & Privacy
- contextual actions
- deep links
- keyboard navigation
- accessibility
- async loading
- native Windows validation

Expected result:

```text
READY_FOR_CLIPBOARD_SLICE_PLANNING
```

---

# Phase 2: Diagnostic Architecture

Directory:

```text
Docs/Planning/Diagnostics/
```

**Status:** `FUTURE`

Likely planning areas:

```text
2A  Diagnostic Domain & Registry
2B  Diagnostic Execution & PowerShell Contract
2C  PySide6 Diagnostic Center
```

Exact phases should be determined after Foundation and Clipboard planning are reviewed.

---

# Phase 3: Statistical Analytics

Directory:

```text
Docs/Planning/Analytics/
```

**Status:** `FUTURE`

Likely planning areas:

```text
3A  Analytics Data Architecture
3B  Metrics / Aggregation Architecture
3C  PySide6 Statistical Analytics Center
```

Analytics must read operational facts.

It must not become a competing system of record.

---

# Phase 4: Mochi Assistant

Directory:

```text
Docs/Planning/Mochi/
```

**Status:** `FUTURE`

Likely planning areas:

```text
4A  Mochi Context Architecture
4B  F7Hub Right Sidebar Integration
4C  Offline Automation Assistant
```

Mochi must operate through approved F7Hub services and contracts.

Mochi must not directly bypass:

```text
repositories
database
PowerShell safety
Ticket services
Diagnostic services
Automation policy
```

---

# Planning vs Canonical Documentation

Planning documents describe:

```text
possible future architecture
recommended decisions
implementation options
risks
dependency sequencing
```

Canonical documentation describes:

```text
approved architecture
implemented behavior
verified project state
```

Examples:

```text
Planning decision:
Docs/Planning/Foundation/0C_...

After approval and implementation:
Docs/06_SystemArchitecture.md
Docs/07_Database.md
Docs/08_ERD.md
Docs/09_SQLSchema.md
```

Planning files must not silently rewrite canonical documentation.

---

# Documentation Synchronization

When a planned feature is eventually implemented, update the appropriate canonical documentation.

## Database changes

```text
Docs/07_Database.md
Docs/08_ERD.md
Docs/09_SQLSchema.md
```

## GUI changes

```text
Docs/05_GUI.md
Docs/06_SystemArchitecture.md
```

## AutoHotkey changes

```text
Docs/11_AHKArchitecture.md
```

## PowerShell changes

```text
Docs/12_PowerShellArchitecture.md
```

## Python changes

```text
Docs/13_PythonArchitecture.md
```

## Major feature changes

```text
Docs/03_Features.md
Docs/04_UserWorkflows.md
Docs/16_Roadmap.md
Docs/17_Todo.md
Docs/18_ChangeLog.md
Docs/Status/CURRENT_STATE.md
```

Only document functionality as implemented after it has actually been validated.

---

# Planning Document Lifecycle

Each planning document should move through:

```text
NOT_STARTED
    ↓
IN_PROGRESS
    ↓
READY_FOR_REVIEW
    ↓
APPROVED
```

If unresolved:

```text
READY_FOR_REVIEW
    ↓
REQUIRES_DECISION
    ↓
revised
    ↓
READY_FOR_REVIEW
```

If replaced:

```text
APPROVED
    ↓
SUPERSEDED
    ↓
Archive if appropriate
```

---

# Implementation Gate

Architecture approval does not mean:

```text
build the whole subsystem
```

After architecture approval:

```text
Architecture
    ↓
Vertical Slice Planning
    ↓
Small Implementation Slice
    ↓
Focused Tests
    ↓
Regression Tests
    ↓
Independent Review
    ↓
Integration
    ↓
Documentation
```

Each implementation slice should have:

- one bounded objective
- explicit scope
- explicit out-of-scope items
- acceptance criteria
- validation requirements
- limited architectural impact
- independently reviewable changes

---

# Architecture Review Gate

Before implementation begins for a major planned subsystem, verify:

```text
architecture internally consistent
dependencies approved
database impact understood
security reviewed
cross-language contracts stable
taxonomy stable enough
configuration ownership clear
testing approach defined
documentation impact identified
```

If not:

```text
DO NOT IMPLEMENT
```

Resolve architecture first.

---

# Archive

Directory:

```text
Docs/Planning/Archive/
```

Use this directory for planning artifacts that are:

```text
SUPERSEDED
ARCHIVED
```

Do not archive currently approved architecture merely because implementation has begun.

The approved plan remains useful historical context until deliberately superseded.

---

# Guiding Principle

Planning exists to make implementation smaller and safer.

The purpose of these documents is not to predict every future class or database column.

Their purpose is to establish enough shared architecture that future F7Hub features can be implemented without:

```text
duplicating systems
breaking boundaries
inventing incompatible terminology
inventing incompatible JSON
bypassing security
mixing GUI and domain logic
creating parallel sources of truth
```

The final goal is:

> F7Hub should become more understandable after every development cycle.

---

# Cross-Subsystem Planning Notes

These notes identify dependencies that later planning must reconcile. They are planning guidance, not proof of implementation.

| Area | Priority | Planning requirement |
|---|---|---|
| Diagnostics | MUST | DynamicHub may request diagnostics and consume structured results, while PowerShell execution remains behind the established diagnostic/service/gateway architecture. Stable diagnostic/action identifiers should bridge the systems. |
| Analytics | MUST | Distinguish ticket evidence, workflow telemetry and derived analytics. Analytics should consume structured events/results rather than generated case-note prose. |
| Clipboard | MUST | Clipboard content may assist a ticket workflow but must never establish ticket identity. Clipboard events are not troubleshooting evidence unless explicitly attached to the active session. |
| Mochi | SHOULD | Mochi is an advisory consumer of selected-ticket/session context. It must not silently write diagnostic results, claim resolution or change ticket binding. |
| Archive | MINIMAL | Archived planning is historical and cannot override current Foundation or approved cross-subsystem contracts. |

Conceptual dependency sketch:

```text
                Foundation
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
    Clipboard   Diagnostics    Mochi
                    │
                    ▼
                DynamicHub
                    │
             ┌──────┴──────┐
             ▼             ▼
        Case Notes       Analytics
        / Closure
```
