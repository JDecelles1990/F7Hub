# AGENTS.md

## Scope

This file applies to:

```text
Docs/Planning/
```

and all descendant directories unless a more-specific `AGENTS.md` exists below this directory.

This guidance supplements the repository root `AGENTS.md`.

If instructions conflict, use the normal F7Hub source-of-truth hierarchy and the most specific applicable `AGENTS.md`.

---

# Purpose

`Docs/Planning/` contains architecture investigation, design, decision, and implementation-planning artifacts for future F7Hub development.

These documents are not proof that functionality has been implemented.

Planning exists to reduce uncertainty before implementation and to make later vertical slices smaller, safer, testable, reviewable, and reversible.

The planning workflow is:

```text
UNDERSTAND
    ↓
INSPECT
    ↓
PLAN
    ↓
REVIEW
    ↓
APPROVE
    ↓
SLICE PLANNING
    ↓
IMPLEMENT
```

Implementation does not occur inside an architecture-planning phase unless the user explicitly changes the task scope.

---

# Primary Rule

When working under `Docs/Planning/`:

> Investigate and design the correct architecture. Do not silently implement it.

Planning work must preserve the distinction between:

```text
what currently exists
what has been verified
what is proposed
what has been approved
what has been implemented
```

---

# Planning Documents

Current planning areas may include:

```text
Foundation/
Clipboard/
Diagnostics/
Analytics/
Mochi/
Archive/
```

Planning documents may contain:

```text
architecture contracts
planning instructions
current-state findings
reuse assessments
decision registers
risk registers
dependency maps
security analysis
database-impact analysis
testing implications
documentation implications
downstream contracts
review records
approval records
```

---

# Canonical Documentation Boundary

The numbered documentation under:

```text
Docs/
```

remains the canonical project documentation.

Examples include:

```text
00_ProjectVision.md
01_Project.md
02_ProductRequirements.md
03_Features.md
04_UserWorkflows.md
05_GUI.md
06_SystemArchitecture.md
07_Database.md
08_ERD.md
09_SQLSchema.md
10_FolderStructure.md
11_AHKArchitecture.md
12_PowerShellArchitecture.md
13_PythonArchitecture.md
14_DesignPrinciples.md
15_NamingConventions.md
16_Roadmap.md
17_Todo.md
18_ChangeLog.md
19_DocumentationIndex.md
```

Planning documents may propose changes to canonical documentation.

Planning documents must not present proposed behavior as implemented fact.

Do not update canonical documentation merely because an architectural idea was proposed.

Canonical documentation should be synchronized when decisions are approved and implementation or verified architecture state justifies the update.

---

# Planning Status

Use the following planning statuses:

```text
NOT_STARTED
IN_PROGRESS
REQUIRES_DECISION
BLOCKED
READY_FOR_REVIEW
APPROVED
SUPERSEDED
ARCHIVED
```

Do not use:

```text
IMPLEMENTED
```

as the status of an architecture-planning document.

Implementation status belongs to implementation records, canonical documentation, current-state documentation, tests, and Git history.

---

# Approval Authority

Codex may determine that a planning phase is:

```text
READY_FOR_REVIEW
REQUIRES_DECISION
BLOCKED
```

Codex must not independently mark an architecture phase:

```text
APPROVED
```

unless the user explicitly instructs it to record a previously completed approval.

Architecture approval is a review decision, not an automatic consequence of finishing a planning report.

---

# Dependency Gates

Planning phases may depend on earlier approved phases.

Example:

```text
0A Foundation
    ↓
0B Interoperability
    ↓
0C Taxonomy
    ↓
0D Settings
    ↓
1A Clipboard Domain
    ↓
1B Clipboard Integration
    ↓
1C Clipboard GUI
```

Before executing a phase:

1. Identify its declared dependencies.
2. Verify their current status.
3. Read their approved decisions and downstream contracts.
4. Do not silently redefine decisions owned by earlier phases.

If a required dependency is not sufficiently resolved, report:

```text
BLOCKED
```

or:

```text
REQUIRES_DECISION
```

as appropriate.

Do not compensate for missing architecture by inventing local replacements.

---

# Inspect Before Designing

Before proposing any new:

```text
table
migration
class
service
repository
gateway
protocol
JSON envelope
taxonomy
tag system
Entity model
configuration mechanism
GUI component
worker
event system
action registry
IPC transport
```

perform:

```text
SEARCH
    ↓
IDENTIFY
    ↓
REUSE / EXTEND
    ↓
CREATE ONLY IF NECESSARY
```

Search both implementation and documentation.

Relevant existing architecture may live in:

```text
Python/
AutoHotkey/
PowerShell/
Database/
Config/
Docs/
Tests/
Mochi/
.agents/
```

Do not assume a capability is absent because it has not yet appeared in the current planning document.

---

# Current-State Evidence

Planning must inspect actual repository state before making significant architectural recommendations.

Evidence may include:

```text
source code
migrations
SQLite schema
repositories
services
domain models
gateways
configuration
tests
canonical documentation
current-state documentation
Git history when relevant
```

Never invent project state.

If something has not been inspected, say:

```text
NOT VERIFIED
```

---

# Evidence Classification

Use these labels consistently:

```text
FACT
ASSUMPTION
INFERENCE
RECOMMENDATION
NOT VERIFIED
```

Definitions:

## FACT

Directly supported by inspected project evidence.

## ASSUMPTION

A temporary premise required to continue planning but not yet verified.

## INFERENCE

A conclusion reasonably derived from inspected evidence but not explicitly stated by the project.

## RECOMMENDATION

A proposed architectural choice.

## NOT VERIFIED

A statement or project area that has not been inspected sufficiently.

Do not convert assumptions or recommendations into facts through repetition.

---

# Existing Architecture First

F7Hub already contains implemented architecture.

A planning phase must identify existing components before proposing replacements.

For each relevant component, evaluate:

```text
Component
Current responsibility
Layer
Consumers
Dependencies
Tests
Documentation
Architectural fitness
Recommended treatment
```

Recommended treatment values:

```text
REUSE
EXTEND
REPLACE
DEPRECATE
NOT RELATED
NOT VERIFIED
```

Replacement requires justification.

---

# Architecture Boundaries

Prefer:

```text
GUI
 ↓
Application / Services
 ↓
Domain Logic
 ↓
Repositories
 ↓
Database / Infrastructure
```

Do not move business rules into GUI code for convenience.

Do not place SQL in GUI widgets.

Do not allow AutoHotkey to become a database/business-logic layer.

Do not allow PowerShell to become application orchestration.

Do not allow Mochi to bypass application services.

Do not let SQLite define application behavior that belongs in services or domain rules.

---

# Technology Responsibilities

Unless approved architecture says otherwise:

## AutoHotkey v2

Primary responsibilities:

```text
Windows interaction
global hotkeys
desktop automation
lightweight HUDs
clipboard integration
window interaction
launching
```

## Python / PySide6

Primary responsibilities:

```text
application orchestration
advanced GUI
domain/application services
classification
integration coordination
search
business workflows
```

## PowerShell

Primary responsibilities:

```text
Windows administration
Microsoft administration
diagnostics
approved remediation
technical data collection
reporting
```

## SQLite

Primary responsibilities:

```text
durable relational state
data integrity
relationships
search indexes
audit/persistence structures
```

## Mochi

Primary responsibilities:

```text
presentation
contextual assistance
approved interaction
communication
```

Mochi must not become an unrestricted execution or database layer.

---

# Database Planning

SQLite changes are foundational and require special care.

Architecture planning must consider:

```text
normalization
primary keys
foreign keys
constraints
indexes
transactions
migrations
views
FTS5
query patterns
retention
audit
data integrity
```

Do not create migrations during architecture-planning phases unless the user explicitly changes scope.

Do not silently propose duplicate tables without inspecting existing schema and migrations.

Do not use JSON columns to avoid designing stable relational data when stable queryable structure is warranted.

---

# Contract Planning

When designing JSON or interoperability contracts:

```text
separate contract semantics from transport
use stable machine-readable keys
validate all boundaries
version breaking contracts
define error semantics
define idempotency where required
treat local processes as untrusted boundaries
avoid arbitrary command execution
```

Do not create a second interoperability grammar if a suitable existing contract can be extended.

---

# Taxonomy Planning

Do not confuse:

```text
Category
Type / Kind
Entity
Entity Type
Tag
Status
Priority
Relationship
Metric
Insight
```

Reuse existing taxonomy infrastructure where possible.

Detected literal values such as:

```text
IP addresses
email addresses
hostnames
error codes
GUIDs
ticket IDs
```

are generally Entities, not Tags.

Flexible reusable concepts such as:

```text
PowerShell
Networking
Outlook
Troubleshooting
```

may be Tags where approved by taxonomy architecture.

---

# Settings Planning

Settings configure behavior.

Settings must not become a miscellaneous storage mechanism for domain definitions.

Examples of things that are generally not Settings:

```text
Tag Catalog
Entity Type Catalog
Diagnostic Registry
Script Registry
JSON Schema
Ticket Status Semantics
Security Invariants
```

Separate:

```text
setting definition
setting value
default
stored override
effective value
```

Secrets do not belong in ordinary application settings.

---

# Security

Planning must explicitly consider:

```text
least privilege
untrusted input
clipboard privacy
file input
URLs
commands
AI output
IPC boundaries
PowerShell execution
sensitive data
secret handling
logging
audit
local process impersonation
```

Never recommend an unrestricted endpoint such as:

```text
run_any_command
```

AI-generated commands must not execute automatically.

---

# Privacy

Clipboard, logs, window titles, source URLs, ticket information, diagnostic data, and assistant context may contain sensitive information.

Architecture planning must identify:

```text
what is captured
what is transmitted
what is persisted
what is logged
what is searchable
what is sent to Mochi
what is eligible for analytics
what is deleted
```

Raw sensitive content should not enter normal logs.

---

# Planning vs Implementation

Unless explicitly authorized, architecture-planning work must not:

```text
modify production Python
modify production AHK
modify production PowerShell
create migrations
alter the SQLite database
register hotkeys
start persistent services
change IPC endpoints
install dependencies
refactor unrelated code
implement GUI features
```

Allowed planning changes are normally limited to:

```text
Docs/Planning/
```

and only the specific planning documents in scope.

---

# Preserve Planning Contracts

When executing a phase document:

1. Preserve the existing planning instructions.
2. Do not rewrite the prompt into a different architecture question.
3. Populate or append the Execution Report sections.
4. Preserve unresolved decisions.
5. Record what was inspected.
6. Record what was not verified.
7. Record evidence supporting architectural conclusions.
8. Record downstream assumptions explicitly.

Do not erase the original planning contract after execution.

---

# Planning Document Structure

Planning documents should normally contain:

```text
Document Control
Purpose
Scope
Out of Scope
Dependencies
Planning Instructions

Execution Report
Verified Current State
Reuse Assessment
Architecture Recommendation
Decision Register
Requires User Decision
Assumptions
Not Verified
Risk Register
Security / Privacy Impact
Database Impact
Testing Implications
Documentation Impact
Downstream Contract
Validation
Final Result
Review Record
Approval Record
Change History
```

Not every document needs identical prose, but the lifecycle information should remain recognizable.

---

# Decision Register

Significant architecture decisions should record:

```text
Decision
Options considered
Recommendation
Evidence
Rationale
Consequences
Status
```

Allowed decision statuses:

```text
RECOMMENDED
REQUIRES_USER_DECISION
DEFERRED
NOT_VERIFIED
APPROVED
SUPERSEDED
```

Do not silently make major architectural decisions.

---

# User-Review Decisions

Explicit user review is required before recommending implementation of major changes involving:

```text
destructive migrations
core database relationship changes
authentication boundaries
security boundaries
major dependency changes
major framework changes
repository restructuring
plugin architecture
IPC contract redesign
cross-language architecture
persistent background services
```

Record these as review gates.

---

# Risk Register

Planning must identify relevant risks.

For each material risk record:

```text
Risk
Likelihood
Impact
Mitigation
Residual risk
Status
```

Do not hide unresolved architecture uncertainty in general prose.

---

# Testing Implications

Architecture planning should identify tests required by future implementation.

Possible categories:

```text
unit
database
contract
integration
GUI
native Windows
security
performance
regression
end-to-end
```

Do not claim tests passed during a planning phase unless they were actually executed for inspection purposes.

Use:

```text
PASS
FAIL
NOT RUN
BLOCKED
```

---

# Native Test Loop Safety

Automated validation must be bounded.

Every retrying action should define:

```text
trigger
maximum retry count
maximum elapsed time
success condition
failure condition
```

If the same native, GUI, integration, or screenshot validation fails twice with:

```text
the same failure
+
no relevant code/configuration/state change
```

then:

```text
STOP
DIAGNOSE
REPORT BLOCKED
```

Do not continue repeating the same test.

No infinite:

```text
polling
retries
relaunches
screenshots
focus attempts
GUI checks
IPC reconnect loops
```

---

# Scope Control

During one planning phase:

```text
solve the requested architectural question
```

Do not redesign unrelated subsystems.

If unrelated improvements are discovered:

```text
record them as follow-up work
```

Do not expand scope automatically.

---

# Downstream Contracts

Every completed phase should state what downstream phases may now rely upon.

Example:

```text
Phase 1A defines Clipboard Item and Capture Event.

Phase 1B may consume those definitions.

Phase 1B may not redefine them silently.
```

If a downstream phase discovers a conflict with an approved upstream decision:

```text
STOP
record conflict
identify owning phase
request architecture review
```

Do not patch around the conflict locally.

---

# Canonical Documentation Synchronization

Planning may identify future documentation impact.

Common mappings:

```text
Database
→ 07_Database.md
→ 08_ERD.md
→ 09_SQLSchema.md

GUI
→ 05_GUI.md
→ 06_SystemArchitecture.md

AHK
→ 11_AHKArchitecture.md

PowerShell
→ 12_PowerShellArchitecture.md

Python
→ 13_PythonArchitecture.md

Major feature/workflow
→ 03_Features.md
→ 04_UserWorkflows.md
→ 16_Roadmap.md
→ 17_Todo.md
→ 18_ChangeLog.md
→ Status/CURRENT_STATE.md
```

Do not synchronize proposed functionality as implemented functionality.

---

# Archive Rules

Use:

```text
Docs/Planning/Archive/
```

for planning artifacts that are:

```text
SUPERSEDED
ARCHIVED
```

Do not archive a still-authoritative approved plan merely because implementation has begun.

---

# Phase Completion

Before declaring a planning phase complete, verify:

```text
required repository areas inspected
dependencies respected
existing architecture considered
reuse opportunities identified
architecture recommendation explicit
security considered
privacy considered
database impact considered
testing implications identified
canonical documentation impact identified
decision register complete
risk register complete
unverified items explicit
downstream contract written
no unauthorized implementation occurred
```

---

# Final Result

A planning phase must end with only one phase-specific state such as:

```text
READY_FOR_REVIEW
REQUIRES_DECISION
BLOCKED
```

or the exact result token required by that phase document.

Do not return:

```text
READY_FOR_IMPLEMENTATION
```

unless the relevant planning sequence explicitly defines that state and all required architecture approvals have already occurred.

---

# Implementation Handoff

When architecture is approved, implementation should proceed through small vertical slices.

Each implementation slice should define:

```text
OBJECTIVE
CONTEXT
SCOPE
OUT OF SCOPE
CONSTRAINTS
ACCEPTANCE CRITERIA
VALIDATION
DELIVERABLES
```

Do not convert an approved architecture document into one giant implementation task.

---

# Guiding Principle

The purpose of architecture planning is not to maximize documentation.

The purpose is to reduce ambiguity before code changes.

Prefer:

```text
small
verified
explicit
reusable
testable
reviewable
reversible
```

decisions.

F7Hub should become more understandable after every development cycle.


---

# Cross-Subsystem Contract Ownership

A subsystem planning document may specialize a global contract, but may not silently redefine it.

For example:
Foundation defines:
Event

Diagnostics specializes:
Diagnostic Event

DynamicHub specializes:
Troubleshooting Action Event

Analytics consumes:
Event

DynamicHub should not invent an incompatible second definition of Event.

When a subsystem plan introduces a concept that affects two or more
subsystems, determine whether the concept belongs in Foundation before
making it subsystem-local authority.

