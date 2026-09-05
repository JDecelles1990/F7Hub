# F7Hub Design Principles

> Document: `Docs/14_DesignPrinciples.md`  
> Project: F7Hub  
> Purpose: Define the architectural, product, UX, data, automation, security, testing, and maintainability principles that guide F7Hub design decisions.  
> Related Documents: `00_ProjectVision.md`, `01_Project.md`, `02_ProductRequirements.md`, `05_GUI.md`, `06_SystemArchitecture.md`, `07_Database.md`, `10_FolderStructure.md`, `11_AHKArchitecture.md`, `12_PowerShellArchitecture.md`, `13_PythonArchitecture.md`

---

# 1. Purpose

This document defines the design principles for F7Hub.

It answers:

> What rules should guide decisions when several technically valid solutions are possible?

Design principles are not detailed implementation instructions.

They are decision filters.

When choosing between approaches, prefer the one that best preserves:

- clarity
- maintainability
- safety
- simplicity
- testability
- technician usefulness
- architectural consistency

---

# 2. Core Philosophy

F7Hub should become more understandable after every development cycle.

The project should prefer:

```text
small
tested
documented
reversible
understandable
```

changes over large uncontrolled implementations.

The objective is not to maximize the amount of code.

The objective is to build the correct system.

---

# 3. Build the Correct System, Not the Most Code

More code does not automatically mean more functionality or better architecture.

Prefer:

```text
clear requirement
→ small design
→ small implementation
→ test
→ review
```

over:

```text
large prompt
→ hundreds of files
→ unclear architecture
→ difficult validation
```

Code volume is not a success metric.

---

# 4. Technician Value First

Every feature should answer:

> How does this help an IT technician perform work more effectively?

Useful outcomes include:

- faster information retrieval
- fewer repetitive actions
- safer administration
- clearer troubleshooting
- better ticket documentation
- easier knowledge reuse
- reduced context switching

Features that do not improve a real workflow should not be prioritized merely because they are technically interesting.

---

# 5. Practical Before Impressive

F7Hub is not designed around architectural spectacle.

Avoid implementing complexity merely to resemble a large enterprise platform.

Examples of unnecessary early complexity may include:

- microservices
- distributed message brokers
- excessive abstraction layers
- huge plugin frameworks
- dozens of empty modules
- arbitrary numbers of database tables

Use sophisticated architecture only when the problem requires it.

---

# 6. Learn Through Real Architecture

F7Hub should remain a useful learning project.

Where practical, architecture should expose important engineering concepts clearly:

```text
SQL
repositories
transactions
foreign keys
services
APIs
PowerShell
GUI events
testing
logging
security
```

Do not hide useful concepts behind frameworks before understanding the underlying mechanism.

---

# 7. Understand Before Implementing

The development process is:

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

Skipping earlier stages usually creates cleanup work later.

---

# 8. Inspect Before Creating

Before creating a new:

- module
- class
- service
- repository
- database table
- helper
- configuration file
- PowerShell script
- AHK component
- plugin

follow:

```text
SEARCH
  ↓
IDENTIFY
  ↓
REUSE / EXTEND
  ↓
CREATE ONLY IF NECESSARY
```

This reduces duplication and architectural drift.

---

# 9. One Responsibility per Component

A component should have one clear primary responsibility.

Examples:

```text
TicketRepository
→ ticket persistence

TicketService
→ ticket application workflows

TicketView
→ ticket presentation

PowerShellGateway
→ PowerShell process execution
```

Avoid components whose responsibility can only be described as:

> handles everything related to...

---

# 10. Clear Technology Ownership

Technology responsibilities should remain explicit.

```text
Python / PySide6
→ primary application and GUI

PowerShell
→ Windows and Microsoft administration

AutoHotkey v2
→ desktop automation

SQLite
→ persistent relational data
```

A technology should not absorb another subsystem without a clear reason.

---

# 11. Layered Responsibility

Preferred application direction:

```text
GUI
 ↓
Application Services
 ↓
Domain Logic
 ↓
Repositories / Gateways
 ↓
Infrastructure
```

Dependencies should generally move downward.

Avoid shortcuts such as:

```text
GUI
→ raw SQL
```

or:

```text
GUI
→ raw shell command
```

---

# 12. GUI Is Presentation

The GUI should primarily handle:

- presentation
- navigation
- input collection
- user feedback
- view state

It should not become the home of:

- SQL
- business rules
- authentication logic
- migration logic
- PowerShell command construction

---

# 13. Services Own Use Cases

Application services represent what the application does.

Examples:

```text
Create Ticket
Add Ticket Note
Search Knowledge
Run Diagnostic
Execute Registered Script
```

Services coordinate the components needed to perform those workflows.

---

# 14. Domain Logic Should Remain Independent

Core business rules should not require:

- PySide6
- SQLite
- PowerShell
- external APIs

This improves:

- testing
- reuse
- clarity
- maintainability

---

# 15. Persistence Through Repositories

SQLite access should normally pass through repositories.

Preferred:

```text
Service
 ↓
Repository
 ↓
SQLite
```

This centralizes:

- SQL
- parameterization
- mapping
- persistence behavior
- schema coupling

---

# 16. External Systems Through Gateways

External platforms should be accessed through controlled adapters or gateways.

Examples:

```text
PowerShellGateway
GraphGateway
AIProvider
FileSystemGateway
```

The rest of the application should not depend everywhere on provider-specific details.

---

# 17. Prefer a Modular Monolith

F7Hub should begin as a modular monolith.

This means:

```text
one application
+
clear internal modules
+
clear boundaries
```

This is preferable to early distributed architecture because F7Hub is primarily a desktop application.

---

# 18. Avoid Premature Microservices

Do not introduce microservices simply because they are common in large systems.

Microservices introduce:

- deployment complexity
- network boundaries
- authentication complexity
- observability requirements
- failure modes
- versioning complexity

Use them only if a future requirement clearly justifies them.

---

# 19. Prefer Explicitness

Code should make important behavior visible.

Prefer:

```text
explicit dependencies
explicit parameters
explicit transactions
explicit permissions
explicit risk
explicit errors
```

over hidden framework behavior.

Explicit systems are easier to learn, debug, and trust.

---

# 20. Avoid Magic

Avoid architectures that depend heavily on implicit behavior.

Examples:

- hidden global state
- automatic module discovery without need
- implicit database writes
- reflection-heavy wiring
- action names constructed dynamically
- silent privilege escalation

A technician/developer should be able to trace what happens.

---

# 21. Simplicity Is a Feature

When two solutions satisfy the same requirement, prefer the simpler one unless the more complex option provides a measurable benefit.

Simple does not mean careless.

Simple means:

```text
few moving parts
clear ownership
predictable behavior
easy testing
```

---

# 22. Complexity Must Earn Its Place

Every abstraction introduces cost.

Examples:

- interfaces
- base classes
- event buses
- dependency injection frameworks
- plugin systems
- caches
- background schedulers

Before adding one, ask:

> What concrete problem does this solve today?

---

# 23. Avoid Premature Abstraction

Do not create abstractions because similar code might exist someday.

Start with clear concrete code.

Refactor when duplication or variation becomes real.

---

# 24. Avoid Premature Optimization

Do not optimize based on imagined bottlenecks.

First:

```text
implement
→ measure
→ identify bottleneck
→ optimize
```

Potential performance techniques should be justified by observed need.

---

# 25. Prefer Deterministic Core Behavior

Core application behavior should be deterministic wherever practical.

Examples:

- ticket validation
- diagnostic branching
- SQL constraints
- script risk classification
- search filters
- permissions

AI should enhance workflows rather than become a hidden decision engine for basic application behavior.

---

# 26. AI Is an Assistant, Not an Authority

AI may assist with:

- summarization
- explanation
- search suggestions
- draft responses
- KB recommendations
- troubleshooting suggestions

AI should not silently determine:

- destructive actions
- tenant administration
- database deletion
- privileged commands
- final technician decisions

---

# 27. AI Output Is Untrusted

AI-generated content should be treated like any other external input.

Validate before:

```text
executing
saving
parsing
displaying as trusted fact
```

AI-generated commands should never bypass normal application controls.

---

# 28. Human Review Before Impactful Actions

Actions that may affect:

- users
- devices
- tenant configuration
- files
- persistent data
- permissions

should require appropriate review or confirmation.

The technician should understand:

```text
target
action
risk
expected effect
```

before execution.

---

# 29. Read-Only Before Write

When implementing administrative features, prefer read-only capability first.

Example:

```text
inspect mailbox permissions
```

before:

```text
modify mailbox permissions
```

This allows architecture and authentication to be validated with lower risk.

---

# 30. Diagnose Before Remediate

Troubleshooting should generally follow:

```text
observe
→ measure
→ interpret
→ remediate
→ verify
```

Avoid jumping immediately from symptom to destructive action.

---

# 31. Separate Diagnosis and Remediation

Where practical:

```text
Test-X
```

and:

```text
Repair-X
```

should be separate operations.

This improves:

- safety
- reuse
- auditability
- testing
- technician understanding

---

# 32. Verify After Change

A remediation is not complete simply because a command executed successfully.

Preferred:

```text
change
→ verification check
→ result
```

Example:

```text
reset network configuration
→ test connectivity
```

---

# 33. Least Privilege

Every operation should use the minimum privilege required.

Avoid:

- running F7Hub permanently elevated
- requesting broad Graph permissions
- using global administrator credentials for routine queries
- silent elevation

Privilege should be explicit.

---

# 34. Secure Defaults

Default behavior should favor safety.

Examples:

```text
read-only before modify
no automatic clipboard persistence
no automatic AI execution
no silent elevation
no destructive migration
no automatic module installation
```

Unsafe behavior should never be the easiest accidental path.

---

# 35. Treat External Input as Untrusted

Untrusted input includes:

```text
user input
clipboard data
ticket text
files
URLs
API responses
PowerShell results
AI output
external identifiers
```

Validate at appropriate boundaries.

---

# 36. Protect Secrets

Secrets must not be stored in:

- source code
- Markdown docs
- Git history
- ordinary configuration
- logs
- normal database settings

Examples:

```text
passwords
API keys
tokens
private keys
client secrets
```

Use an approved secret-storage mechanism when needed.

---

# 37. Avoid Command Injection

External input must never be blindly converted into shell commands.

Prefer:

```text
known executable
+
known script
+
validated arguments
```

Avoid arbitrary command strings.

---

# 38. Avoid SQL Injection

All dynamic SQL input must use parameterized queries.

Never rely on escaping manually constructed SQL strings.

---

# 39. Protect the Filesystem

User-provided paths should be validated.

Consider:

- path traversal
- unexpected network paths
- invalid filenames
- unsafe file types
- overwriting existing files

---

# 40. Preserve Data

F7Hub should never silently destroy persistent data.

Potentially destructive actions require deliberate handling.

Examples:

```text
record deletion
migration
file overwrite
bulk change
```

Use transactions and backups where appropriate.

---

# 41. Database Integrity Is Foundational

SQLite design should preserve:

- primary keys
- foreign keys
- constraints
- normalization
- transactions
- indexes
- migrations

Application convenience should not bypass integrity.

---

# 42. Foreign Keys Must Be Enforced

Every SQLite connection should enable:

```sql
PRAGMA foreign_keys = ON;
```

Relationships should be enforced in the database where appropriate, not only in Python.

---

# 43. Normalize Before Denormalizing

Target approximately third normal form where appropriate.

Denormalization should only occur when:

- a concrete query need exists
- performance is measured
- synchronization rules are understood

---

# 44. Avoid Arbitrary Table Counts

Database quality is not measured by the number of tables.

Do not design toward:

```text
100 tables
```

or any other arbitrary number.

Use the number of entities required by the domain.

---

# 45. Use Junction Tables for Real Many-to-Many Relationships

Many-to-many relationships should generally be explicit.

Example:

```text
tickets
 ↕
ticket_tags
 ↕
tags
```

Avoid comma-separated relationship IDs inside text fields.

---

# 46. JSON Is Not a Replacement for Relational Design

Use JSON when data is:

- variable
- opaque
- external
- not meaningfully relational

Do not place normal relational entities into large JSON blobs merely to reduce schema work.

---

# 47. Filesystem and Database Have Different Roles

Store structured metadata in SQLite.

Store large files on disk when appropriate.

Example:

```text
SQLite
→ attachment metadata

Filesystem
→ actual attachment
```

---

# 48. Migrations Are Required

Schema changes should be represented through versioned migrations.

Avoid manually modifying production database structure without a migration path.

---

# 49. Migrations Should Be Reversible Where Practical

Not every migration can be perfectly reversible.

However changes should be designed so rollback or recovery is possible where practical.

Destructive migrations require review.

---

# 50. Database Changes Require Tests

Schema work should test:

- migration success
- foreign keys
- constraints
- transactions
- indexes where relevant
- existing data preservation

---

# 51. Search Should Work Without AI

Universal search should remain functional without AI.

Preferred initial foundation:

```text
SQLite
+
FTS5
+
deterministic ranking
```

AI may later improve discovery but should not be mandatory for basic search.

---

# 52. Search Results Should Be Explainable

Where practical, users should understand why a result appeared.

Ranking should initially rely on understandable signals such as:

- exact match
- prefix match
- relevance
- recency
- type

---

# 53. Local-First Where Practical

F7Hub should remain useful locally when external services are unavailable.

Examples:

```text
tickets
KB
local search
scripts
diagnostics
settings
```

should not unnecessarily depend on cloud connectivity.

---

# 54. Connected Where Required

Local-first does not mean pretending cloud services are local.

Features requiring:

- Microsoft Graph
- Exchange Online
- Intune
- Defender
- HaloPSA
- NinjaOne
- AI providers

should use supported connections when necessary.

---

# 55. Graceful Degradation

External failure should reduce functionality rather than collapse the entire application.

Example:

```text
AI unavailable
→ local search continues

Graph unavailable
→ local ticket notes continue

PowerShell unavailable
→ KB continues
```

---

# 56. Avoid Startup Dependency on Every Integration

F7Hub should not need to connect to every external service before the GUI becomes usable.

Prefer lazy connection when the relevant feature is used.

---

# 57. Fast Startup Matters

Startup should perform only essential initialization.

Essential examples may include:

```text
configuration
logging
database
migrations
core services
main GUI
```

Cloud authentication and heavy indexing should not unnecessarily block startup.

---

# 58. Keep the GUI Responsive

Blocking operations must not freeze the PySide6 event loop.

Potential blocking work includes:

- PowerShell
- network requests
- Graph
- AI
- large exports
- filesystem scanning

Run them through appropriate background execution.

---

# 59. User Feedback During Work

Long operations should communicate state.

Possible states:

```text
starting
running
waiting
completed
failed
cancelled
```

Avoid leaving the technician wondering whether the application froze.

---

# 60. Cancellation Must Be Truthful

Not every operation can be cancelled safely.

The application should distinguish:

```text
cancellable
best effort
not cancellable
```

Never claim a remote operation was cancelled if it already completed.

---

# 61. Keyboard-First Productivity

F7Hub is designed for technician productivity.

Common actions should support keyboard use where practical.

Examples:

- command palette
- navigation
- search
- hotkeys
- quick actions
- forms

Mouse access should remain available.

---

# 62. AutoHotkey Should Stay Lightweight

AutoHotkey v2 should specialize in:

- hotkeys
- hotstrings
- clipboard
- launchers
- lightweight menus

It should not become a second F7Hub application.

---

# 63. PowerShell Should Stay Administrative

PowerShell should specialize in:

- administration
- diagnostics
- reporting
- automation

It should not own the GUI or core SQLite persistence.

---

# 64. Python Should Coordinate, Not Absorb Everything

Python is the architectural center but should not replace PowerShell or AutoHotkey merely because it could.

Use the best tool for the responsibility.

---

# 65. Prefer Stable Interfaces Between Technologies

Cross-language communication should use explicit contracts.

Examples:

```text
known action IDs
command-line parameters
structured JSON
stable file paths
result schemas
```

Avoid fragile assumptions.

---

# 66. Version Cross-Language Contracts

Structured contracts should include versions where future evolution is likely.

Example:

```json
{
  "schemaVersion": 1
}
```

This helps safely evolve PowerShell-to-Python communication.

---

# 67. UI Automation Is a Last Resort

Preferred integration order:

```text
API
 ↓
PowerShell / CLI
 ↓
supported application interface
 ↓
UI automation
```

UI automation is fragile and should be used when better interfaces do not exist.

---

# 68. Prefer State-Based Waiting

For desktop automation, prefer:

```text
wait until expected condition
```

instead of:

```text
sleep arbitrary number of seconds
```

Fixed delays may still be used where unavoidable.

---

# 69. Preserve User Clipboard State

Clipboard automation should not unexpectedly destroy user data.

Temporary clipboard replacement should preserve and restore previous contents where practical.

---

# 70. Logging Should Be Useful

Log events that help:

- diagnose failures
- understand lifecycle
- troubleshoot integrations
- verify important operations

Avoid logging everything merely because it is possible.

---

# 71. Logging Is Not a Data Warehouse

Do not duplicate entire tickets, API responses, or clipboard contents into logs unnecessarily.

Logs should be targeted.

---

# 72. Audit and Logging Are Different

```text
Logging
→ technical behavior

Audit
→ meaningful user or administrative action
```

Keep them conceptually separate.

---

# 73. Errors Should Be Visible

Avoid silent failures.

The application should:

```text
detect
→ log
→ report appropriately
```

The amount of detail shown to the technician depends on context.

---

# 74. Technical Details Should Be Available

Normal users may see:

```text
Unable to save the ticket.
```

Developers or troubleshooting views may expose:

```text
SQLite constraint error...
```

User-facing simplicity should not eliminate diagnostic visibility.

---

# 75. Fail Safely

Failure should preserve as much valid state as possible.

Examples:

- rollback transactions
- preserve unsaved form data
- retain original files
- avoid partial multi-step operations

---

# 76. Transactions Define Units of Work

Multiple database actions that logically belong together should use one transaction.

Example:

```text
Create Ticket
+
Initial Status
+
Timeline Event
```

Either all should succeed or the operation should fail cleanly.

---

# 77. Idempotency Is Valuable

Operations should be safe to repeat where practical.

Especially useful for:

- initialization
- configuration checks
- module checks
- migrations
- administrative scripts

---

# 78. Avoid Hidden Side Effects

A method named:

```text
get_ticket()
```

should not unexpectedly modify unrelated data.

Names and behavior should align.

---

# 79. Naming Should Reveal Intent

Prefer:

```text
TicketRepository
PowerShellGateway
DiagnosticSession
```

over vague names such as:

```text
Manager
Handler
Thing
Helper2
```

Naming conventions are defined further in `15_NamingConventions.md`.

---

# 80. Avoid Generic Manager Classes

`Manager` may be appropriate occasionally, but it often hides unclear responsibilities.

Prefer specific terms:

```text
Service
Repository
Gateway
Registry
Controller
Builder
Validator
```

when they accurately describe the role.

---

# 81. Avoid Giant Utility Modules

A large:

```text
utils.py
```

often indicates missing ownership.

Place code with the subsystem that owns the behavior whenever possible.

---

# 82. Avoid God Objects

No object should become the universal owner of:

- settings
- DB
- GUI
- integrations
- PowerShell
- search
- AI
- tickets

Large objects make dependencies invisible and testing difficult.

---

# 83. Avoid Global Mutable State

Global state makes behavior harder to:

- reason about
- test
- reset
- parallelize

Use explicit ownership.

---

# 84. Explicit Dependency Construction

Initially prefer explicit object construction over a heavy dependency-injection framework.

Example:

```text
database
 ↓
repository
 ↓
service
 ↓
view
```

This makes architecture visible.

---

# 85. Testability Is a Design Requirement

Code should be structured so important behavior can be tested without launching the entire application.

Examples:

- domain rules
- services
- repositories
- search ranking
- diagnostics
- PowerShell result parsing

---

# 86. Test the Correct Layer

Use:

```text
unit tests
→ small logic

database tests
→ SQL and constraints

integration tests
→ subsystem boundaries

GUI tests
→ user interaction

end-to-end tests
→ complete workflows
```

Do not force every scenario into one test type.

---

# 87. Test Success and Failure

Testing should include both:

```text
expected success
```

and:

```text
expected failure
```

Examples:

- valid ticket / invalid ticket
- successful script / timeout
- valid migration / constraint conflict

---

# 88. Never Claim Untested Results

Use:

```text
PASS
FAIL
NOT RUN
BLOCKED
```

Do not write:

> Everything works.

unless relevant tests were actually executed.

---

# 89. Regression Protection Matters

When fixing a bug, add a regression test where practical.

A bug fix without protection may quietly return later.

---

# 90. Synthetic Test Data

Committed tests should use safe synthetic data.

Do not use actual:

- customers
- passwords
- tenant data
- tickets
- personal information

---

# 91. Documentation Is Part of the System

Documentation is not an afterthought.

F7Hub architecture depends on docs as a source of truth for humans and coding agents.

Implementation and documentation must remain synchronized.

---

# 92. Document Decisions, Not Every Line of Code

Documentation should explain:

- architecture
- responsibilities
- constraints
- workflows
- important decisions

Avoid duplicating implementation details that are obvious from clean code and likely to change frequently.

---

# 93. One Source of Truth per Topic

Avoid describing the same specification differently across several documents.

Examples:

```text
07_Database.md
→ database rules

08_ERD.md
→ relationships

09_SQLSchema.md
→ exact schema
```

References are better than duplication.

---

# 94. Documentation Must Reflect Verified Reality

Do not document planned functionality as implemented.

Use status vocabulary such as:

```text
PLANNED
IN PROGRESS
IMPLEMENTED
VERIFIED
NOT VERIFIED
```

as appropriate.

---

# 95. Architecture Changes Require Documentation Review

When changing a major boundary, inspect affected docs.

Examples:

```text
GUI change
→ 05 + 06 + 13

database change
→ 07 + 08 + 09

PowerShell change
→ 12

AHK change
→ 11
```

---

# 96. Avoid Documentation Theater

Large documentation volume is not inherently useful.

Documentation should help:

- make decisions
- navigate the project
- implement safely
- explain architecture
- onboard a developer or coding agent

If a section does none of these, reconsider it.

---

# 97. Keep Folder Structure Intentional

Do not create empty directories for every imagined future subsystem.

Create folders when:

- required by the approved architecture
- implementation needs them
- organization materially improves clarity

---

# 98. Source and Runtime Data Should Be Separated

Repository source should not become the permanent home for runtime state.

Examples of runtime state:

- user DB
- logs
- cache
- temp files
- production attachments

Installed application data may live under user application-data locations.

---

# 99. Git Should Track Source, Not Noise

Generally avoid committing:

```text
logs
cache
temporary files
compiled Python files
virtual environments
local databases
secrets
```

Version-controlled migrations and source remain tracked.

---

# 100. Reversible Changes Are Preferred

Development changes should be easy to inspect and undo.

Prefer:

- focused commits
- migrations
- small branches
- narrow scope
- documented changes

Avoid huge unrelated refactors mixed with feature work.

---

# 101. Scope Control

A focused task should not redesign unrelated systems.

If an unrelated improvement is discovered:

```text
record it
→ defer it
→ review later
```

Do not silently expand scope.

---

# 102. Major Decisions Require Review

Require deliberate review before:

- destructive migrations
- major database relationship changes
- framework replacement
- authentication redesign
- plugin architecture changes
- major dependency changes
- cross-language IPC changes
- repository restructuring

---

# 103. Prefer Vertical Slices

A vertical slice implements one useful capability through the relevant layers.

Example:

```text
Create Ticket
↓
GUI form
↓
TicketService
↓
TicketRepository
↓
SQLite
↓
Tests
```

This proves architecture more effectively than building all repositories first and all GUI later.

---

# 104. Keep Slices Small

Good:

```text
Implement ticket creation persistence and tests.
```

Less useful:

```text
Build Ticket Center.
```

Small slices have clearer acceptance criteria.

---

# 105. Acceptance Criteria Before Coding

Before significant implementation, define what success means.

Example:

```text
Given valid ticket data,
when ticket creation is submitted,
then one ticket is persisted,
its required relations are valid,
and the created ticket is returned.
```

This focuses implementation and testing.

---

# 106. Do Not Optimize for Coding Agents

Architecture should be good for humans first.

Documentation may help coding agents navigate it, but the system should not become artificially fragmented solely to accommodate AI.

---

# 107. Coding Agents Need Boundaries

Agent prompts should specify:

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

This reduces uncontrolled changes.

---

# 108. AI-Generated Code Requires Review

Generated code must be evaluated for:

- correctness
- architecture
- security
- error handling
- duplication
- data integrity
- tests
- documentation

AI output is a draft until validated.

---

# 109. Prefer Official Sources for Changing Technologies

For rapidly changing technologies, verify current official documentation before implementation.

Examples:

- Microsoft Graph
- Exchange Online
- Intune
- PySide6
- OpenAI APIs
- Python
- SQLite
- GitHub

Old tutorials may contain deprecated practices.

---

# 110. Dependencies Must Be Justified

Every third-party dependency adds:

- updates
- vulnerabilities
- compatibility concerns
- packaging cost
- learning cost

Use the standard library or existing dependency when sufficient.

---

# 111. Avoid Duplicate Libraries

Do not add several libraries solving the same problem without a strong reason.

Example:

Avoid using three different HTTP clients in one desktop application.

---

# 112. Version Dependencies Deliberately

Dependencies important to application behavior should eventually be pinned or constrained appropriately.

Upgrades should be tested.

---

# 113. Accessibility Is Part of Usability

The GUI should support:

- keyboard navigation
- visible focus
- clear labels
- high DPI
- scalable layouts
- readable text
- status cues beyond color alone

Accessibility should not be bolted on at the end.

---

# 114. Consistency Beats Novelty

Common actions should behave consistently across modules.

Examples:

```text
Save
Cancel
Delete
Search
Filter
Run
Confirm
```

A technician should not have to relearn interaction patterns in every screen.

---

# 115. Destructive Actions Should Look Destructive

Actions such as:

```text
Delete
Reset
Remove
Disable
Revoke
```

should be visually and behaviorally distinct from normal navigation.

---

# 116. Avoid Confirmation Fatigue

Do not ask confirmation for harmless routine actions.

Require confirmation where the operation has meaningful impact.

Too many confirmations train users to ignore them.

---

# 117. Preserve User Work

When practical, protect unsaved:

- notes
- ticket edits
- diagnostic responses
- drafts

Unexpected navigation or application shutdown should not casually destroy substantial work.

---

# 118. Error Messages Should Help

A useful error explains:

```text
what failed
what the user can do
where more detail exists
```

Avoid errors that only say:

```text
Error 500
```

or:

```text
Something went wrong
```

when more useful information is available.

---

# 119. Empty States Should Guide

When a module contains no data, the interface should explain the next useful action.

Example:

```text
No knowledge articles yet.
Create the first article or import one.
```

---

# 120. Defaults Should Reduce Work

Good defaults reduce repeated configuration.

Examples may include:

- default workspace
- common ticket status
- default search scope
- common export location

Defaults should remain changeable where appropriate.

---

# 121. Configuration Should Be Centralized

Avoid scattering configurable values across code.

Examples:

- paths
- URLs
- feature toggles
- UI preferences
- timeouts

Use a controlled configuration architecture.

---

# 122. Configuration Should Not Contain Secrets by Default

Ordinary settings and secrets have different security requirements.

Keep them separate.

---

# 123. Cache Is Disposable

Anything considered cache should be safely regenerable.

If losing it would destroy important information, it is not cache.

---

# 124. Source of Truth Must Be Clear

For each important concept, know which system owns the authoritative value.

Examples:

```text
ticket record
→ SQLite

PowerShell source
→ .ps1 file

script metadata
→ F7Hub database

external tenant user
→ Microsoft service

FTS index
→ derived from relational source
```

---

# 125. Avoid Dual Write Paths

Do not allow several technologies to independently modify the same persistent state unless explicitly coordinated.

Example to avoid:

```text
Python writes tickets
+
PowerShell writes tickets
+
AHK writes tickets
```

Prefer one persistence path.

---

# 126. Use Stable IDs

Application entities should use stable identifiers.

Display names and titles may change.

Relationships should not depend on mutable human-readable strings.

---

# 127. External IDs Are Not Internal Primary Keys

Provider identifiers should usually remain separate from F7Hub internal IDs.

This reduces coupling to external systems.

---

# 128. Design for Failure

Assume that:

- network requests fail
- PowerShell scripts error
- modules are missing
- APIs change
- files disappear
- users cancel
- SQLite operations can fail

Architecture should define failure behavior.

---

# 129. Recovery Matters

For important workflows, consider:

- retries
- rollback
- backup
- restart
- resuming state
- clear error records

Not every feature needs all of them.

---

# 130. Retry Carefully

Retries are useful for transient failures.

Do not automatically retry:

- destructive commands
- non-idempotent remote operations

unless duplicate execution is safe.

---

# 131. Timeouts Should Exist

External operations should not wait forever.

Timeouts may apply to:

- PowerShell
- Graph
- HTTP
- AI
- external applications

Timeout values should be configurable where appropriate.

---

# 132. Observability Should Match Risk

The more impactful an operation, the more important it is to know:

- who initiated it
- what target was used
- when it occurred
- whether it succeeded

Routine UI navigation does not require the same audit level.

---

# 133. Avoid Over-Auditing

Recording every click as an audit event creates noise.

Audit meaningful state changes and administrative actions.

---

# 134. Performance Should Follow Query Design

For SQLite:

```text
requirements
→ query patterns
→ indexes
→ query plan
```

Do not create hundreds of speculative indexes.

Indexes have storage and write costs.

---

# 135. FTS for Text Search, Not Everything

FTS5 is useful for natural text search.

Do not use FTS where normal indexed relational queries are more appropriate.

---

# 136. Pagination Is Better Than Loading Everything

Large result sets should eventually use:

- pagination
- filtering
- lazy loading

rather than always loading every row into the GUI.

Use this when actual data volume justifies it.

---

# 137. Separate Presentation From Data

A formatted string should not become the primary data representation if structured data exists.

Examples:

```text
PowerShell object
→ structured JSON
→ Python object
→ GUI formatting
```

not:

```text
formatted console table
→ screen scraping
```

---

# 138. Preserve Structured Data as Long as Possible

Delay presentation formatting until the presentation layer.

This improves:

- reuse
- export
- testing
- search
- reporting

---

# 139. Business Rules Should Not Depend on UI Text

Avoid logic such as:

```text
if button.text() == "Closed"
```

Use stable internal states or enums instead.

---

# 140. UX Labels and Internal IDs Are Different

A visible label may change for usability or localization.

Internal identifiers should remain stable.

---

# 141. Bilingual Capability Should Remain Possible

F7Hub may later support English and French UI/content.

Architecture should avoid unnecessary dependence on literal English UI strings as internal identifiers.

Full internationalization should still be added only when required.

---

# 142. Use Standard Conventions

Prefer established conventions for:

- Python
- PowerShell
- AutoHotkey v2
- SQL
- Qt

unless F7Hub has a documented reason to differ.

---

# 143. Avoid Clever Code

Code that is slightly longer but obvious is often preferable to a dense clever solution.

Maintenance happens more often than initial writing.

---

# 144. Comments Explain Why

Comments should explain:

- non-obvious intent
- constraints
- trade-offs
- safety requirements

Avoid comments that merely repeat the code.

---

# 145. Documentation Comments Should Stay Current

Incorrect comments are worse than absent comments.

When behavior changes, related comments should be reviewed.

---

# 146. Names Are Better Than Comments

Prefer:

```text
validate_ticket_status_transition()
```

over:

```text
do_it()
# validates status
```

Clear naming reduces explanation burden.

---

# 147. Keep Functions Focused

A function should usually perform one understandable task.

Very long functions may indicate that responsibilities should be separated.

Do not split functions solely to satisfy arbitrary line counts.

---

# 148. Keep Modules Cohesive

A module should group closely related behavior.

Avoid modules that collect unrelated code merely because it was created at the same time.

---

# 149. Design for Replacement at External Boundaries

External providers may change.

Keep provider-specific behavior behind boundaries when practical.

Examples:

```text
AI provider
PSA provider
RMM provider
Microsoft API
```

Internal business logic should not require major rewriting simply because a provider changes.

---

# 150. Do Not Abstract Stable Internal Code Prematurely

Replaceability is most valuable at external boundaries.

Not every internal class needs an interface.

---

# 151. Plugins Are Future Capability

Do not build a broad plugin framework until concrete extension needs are understood.

When plugins are introduced, they must respect:

- security
- versioning
- permissions
- failure isolation
- defined extension points

---

# 152. Prefer Feature Flags Over Dead Half-Built Features

When incomplete functionality must exist in the codebase, keep it clearly disabled rather than exposing broken behavior.

Avoid long-lived dead branches.

---

# 153. Status Must Be Honest

Use accurate implementation status.

Examples:

```text
PLANNED
IMPLEMENTED
VERIFIED
NOT VERIFIED
```

Do not present mockups or architecture documents as working functionality.

---

# 154. Source of Truth Priority

When information conflicts, use:

```text
1. Explicit user requirement
2. Approved architecture
3. Project documentation
4. Validated implementation
5. Tests
6. Established conventions
7. Engineering inference
```

Do not silently choose the easiest interpretation.

---

# 155. Distinguish Fact From Assumption

During analysis, use concepts such as:

```text
FACT
ASSUMPTION
INFERENCE
RECOMMENDATION
```

If implementation was not inspected:

```text
Not verified.
```

---

# 156. Do Not Invent Project State

Never claim:

```text
the class already exists
the migration has run
tests pass
the API is connected
```

without evidence.

This applies equally to humans and coding agents.

---

# 157. Review Before Large Structural Change

Architecture should evolve deliberately.

Examples requiring review:

- moving entire subsystems
- changing GUI framework
- replacing SQLite
- changing Python ownership
- introducing service processes
- changing authentication model

---

# 158. Prefer Evolution Over Rewrite

When possible:

```text
extend
refactor
migrate
```

rather than replacing functioning subsystems wholesale.

Rewrites should solve a real structural problem.

---

# 159. Backward Compatibility Has a Cost

Do not preserve old interfaces indefinitely merely because they once existed.

However, migrations and user data should be protected deliberately.

Compatibility decisions should be explicit.

---

# 160. Use Versioning Where Contracts Matter

Version:

- database schema
- migrations
- PowerShell result contracts
- plugin interfaces if introduced
- exported formats where compatibility matters

---

# 161. Development Should Be Reproducible

A new development environment should eventually be reconstructable from:

- repository
- dependency definitions
- configuration templates
- setup instructions
- migrations

Avoid relying on undocumented machine-specific state.

---

# 162. Tooling Should Be Non-Destructive by Default

Development scripts should generally:

```text
create missing
validate existing
report differences
```

rather than delete or overwrite.

Destructive tooling should require explicit intent.

---

# 163. Generated Artifacts Should Be Distinguishable

Build outputs and generated files should not be confused with source.

Keep generated content under appropriate folders such as:

```text
Build\
Releases\
Data\Exports\
```

---

# 164. Development and Production Paths Should Differ Cleanly

Development may use:

```text
C:\Dev\F7Hub\
```

Installed runtime should resolve its own appropriate data directories.

Do not hard-code development paths into production logic.

---

# 165. No OneDrive Dependency

The project architecture should not depend on OneDrive synchronization for runtime behavior.

SQLite and frequently modified runtime state should avoid cloud-sync conflicts.

---

# 166. Design for Windows First

F7Hub is a Windows IT support application.

Windows-first behavior is acceptable and expected.

Cross-platform abstractions should not be introduced unless they provide actual value.

---

# 167. Windows Integration Should Still Be Modular

Windows-first does not mean mixing Windows-specific code everywhere.

Keep platform interaction in appropriate gateways, PowerShell scripts, or AHK modules.

---

# 168. Keep the Technician in Context

Whenever possible, tools should preserve the currently relevant context.

Examples:

```text
active ticket
active company
active user
active diagnostic session
```

This reduces repeated searching and copy/paste.

---

# 169. Context Should Be Explicit

Do not let actions silently infer sensitive targets from uncertain UI state.

For impactful operations, display or validate the target.

---

# 170. Reduce Context Switching

A core F7Hub goal is reducing unnecessary transitions between:

- ticket system
- KB
- PowerShell
- browser portals
- notes
- clipboard
- diagnostics

Integrate information where practical without rebuilding every external platform.

---

# 171. Do Not Replace Mature External Products Without Reason

F7Hub should integrate with tools such as:

- Microsoft admin portals
- HaloPSA
- NinjaOne
- Keeper
- VS Code

where appropriate.

It does not need to recreate every function they provide.

---

# 172. Build Bridges, Not Copies

A useful integration may be:

```text
open correct external portal
with current context
```

rather than implementing a complete local clone.

---

# 173. Capture Knowledge From Work

Resolved tickets and diagnostics should make it easy to preserve reusable knowledge.

Potential evolution:

```text
incident
→ troubleshooting
→ resolution
→ KB article
```

Knowledge capture should support technician learning.

---

# 174. Knowledge Should Be Searchable

Knowledge is valuable only if it can be found later.

Design metadata, tags, relationships, and FTS to support retrieval.

---

# 175. Avoid Excessive Taxonomy

Tags and categories should help retrieval.

Do not create dozens of overlapping classification systems that technicians cannot use consistently.

---

# 176. Automation Should Be Discoverable

Scripts should have metadata such as:

```text
name
description
category
risk
parameters
requirements
```

A folder full of unexplained `.ps1` files is not sufficient.

---

# 177. Automation Should Be Explainable

Before running a script, F7Hub should eventually make it possible to understand:

- what it does
- what it targets
- what it requires
- what risk it carries

---

# 178. Safe Automation Beats Fast Automation

A one-click operation that can cause unexpected tenant changes is not good productivity.

Productivity must include reliability and control.

---

# 179. Verification Should Be Visible

When a workflow verifies a fix, show the result clearly.

Examples:

```text
DNS resolution: PASS
Mailbox permission: PASS
Device compliance: WARNING
```

---

# 180. Reports Should Be Derived From Structured Data

Prefer:

```text
structured data
→ report
```

rather than storing formatted reports as the only representation of information.

---

# 181. Export Is Not Source of Truth

CSV, HTML, Markdown, or PDF exports are outputs.

They should not become the canonical application database.

---

# 182. Keep Business Data Separate From Presentation Preferences

Example:

```text
ticket status
→ business data

column width
→ GUI preference
```

Do not mix them.

---

# 183. Prefer Configuration Over Forked Code

If behavior differs because of environment or preference, configuration may be better than maintaining separate code paths.

Do not make every behavior configurable, however.

---

# 184. Avoid Configuration Explosion

Configuration itself creates complexity.

Only expose settings that users or deployments reasonably need to change.

---

# 185. Defaults Must Be Valid

The application should be able to run with documented defaults where external integrations are not configured.

---

# 186. External Integrations Should Be Optional Where Possible

Missing AI, PSA, RMM, or cloud integrations should not prevent unrelated local modules from working.

---

# 187. Respect Provider Boundaries

Do not assume one provider's identifiers, terminology, or permissions apply universally.

Translate provider data into F7Hub concepts where appropriate.

---

# 188. Keep Integration Data Traceable

When storing external references, preserve enough metadata to identify the originating provider and external object.

---

# 189. Avoid Silent Synchronization Conflicts

If F7Hub later synchronizes with external systems, conflict behavior must be defined explicitly.

Do not silently overwrite newer data.

---

# 190. Be Conservative With Automatic Synchronization

Start with:

```text
manual refresh
```

or controlled synchronization before adding complex background bidirectional sync.

---

# 191. Background Work Should Be Observable

If a background task runs, F7Hub should be able to show or log meaningful state.

Avoid invisible work that changes important data.

---

# 192. Scheduler Complexity Should Be Earned

Do not build a full internal scheduling engine before real recurring-job requirements exist.

Use simpler mechanisms first.

---

# 193. Feature Boundaries Should Match User Workflows

Modules should be organized around meaningful technician capabilities, not arbitrary technical divisions.

Examples:

```text
Tickets
Knowledge
Diagnostics
Scripts
Search
```

---

# 194. Architecture Boundaries Should Match Responsibilities

Technical packages may differ from GUI modules.

For example:

```text
TicketService
TicketRepository
TicketView
```

belong to different layers while supporting one feature.

---

# 195. Avoid Copy-Paste Architecture

Do not create identical service/repository/controller structures for every feature unless the responsibilities actually require them.

Consistency is useful, but mechanical duplication is not.

---

# 196. Refactor From Evidence

Refactor when you observe:

- duplication
- unclear ownership
- difficult testing
- repeated bugs
- hard-to-change code

Do not refactor only to match a theoretical pattern.

---

# 197. Technical Debt Should Be Visible

If a temporary compromise is accepted, document it as follow-up work where appropriate.

Do not allow temporary hacks to become invisible permanent architecture.

---

# 198. Comments Are Not a Substitute for Design

If code requires a long warning explaining why touching it is dangerous, consider whether the structure should be improved.

---

# 199. Use Data Constraints as Defense in Depth

Application validation and database constraints should complement one another.

Example:

```text
GUI
→ prevents invalid input

Service
→ enforces workflow

SQLite
→ prevents invalid persistent state
```

---

# 200. Completion Means More Than Code Running

A feature is complete when applicable:

```text
requested behavior implemented
architecture preserved
security considered
data integrity preserved
tests executed
documentation synchronized
remaining risks identified
```

---

# 201. Design Review Questions

Before approving a design, ask:

1. What user problem does this solve?
2. Is this the simplest maintainable solution?
3. Which subsystem owns it?
4. Does something similar already exist?
5. Does it preserve architectural dependency direction?
6. What data does it read or modify?
7. What can fail?
8. What privileges does it require?
9. How will it be tested?
10. What documentation changes?
11. Can the change be reversed?
12. Are we adding complexity before it is needed?

---

# 202. Current Implementation Status

This document defines F7Hub design principles. Code review and isolated tests on 2026-09-03 verified compliance for the SQLite connection and migration infrastructure slice only.

```text
SQLite infrastructure design compliance: PASS
Remaining system design compliance: NOT VERIFIED
```

Future slices require their own code review, tests and documentation inspection.

---

# 203. F7Hub Design Principles Summary

F7Hub should be:

```text
useful
understandable
modular
safe
testable
documented
maintainable
reversible
```

It should avoid becoming:

```text
overengineered
duplicated
opaque
unsafe
AI-controlled
framework-driven
unnecessarily distributed
```

The core decision model is:

```text
Requirement
    ↓
Understand
    ↓
Inspect
    ↓
Choose Simplest Correct Architecture
    ↓
Implement Small Slice
    ↓
Test
    ↓
Review
    ↓
Document
```

The guiding principle is:

> Build F7Hub as a practical technician tool with clear boundaries, strong data integrity, controlled automation, and architecture that remains understandable as the project grows.
