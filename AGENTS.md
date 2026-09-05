# F7Hub Codex Development Instructions

> File: `AGENTS.md`  
> Project: F7Hub  
> Project Root: `C:\Dev\F7Hub\`  
> Purpose: Define mandatory development behavior for Codex and other coding agents working in the F7Hub repository.

---

# 1. Purpose

F7Hub is a modular Windows IT Support and technician-productivity platform.

The primary objective is:

> Build the correct system, not the most code.

All significant work should follow:

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

For complex work, decompose the task into small, independently testable vertical slices.

Do not attempt to build the entire application, subsystem, or database in one uncontrolled operation.

---

# 2. Golden Rule

F7Hub should become more understandable after every development cycle.

Prefer:

```text
small
tested
documented
reversible
maintainable
explicit
```

over:

```text
large
clever
speculative
unverified
coupled
difficult to understand
```

Architecture should reduce uncertainty rather than create more of it.

---

# 3. Repository Root

The canonical development root is:

```text
C:\Dev\F7Hub\
```

Expected major directories:

```text
AutoHotkey\
PowerShell\
Python\
Database\
Config\
Data\
Docs\
Plugins\
Tests\
Assets\
Build\
Installer\
Logs\
Releases\
Tools\
```

Do not assume every documented file, folder, class, table, script, migration, or feature currently exists.

Inspect the repository first.

If something has not been inspected, state:

```text
NOT VERIFIED
```

---

# 4. Project Technology Ownership

The canonical technology responsibilities are:

```text
Python / PySide6
→ primary desktop application
→ GUI
→ application orchestration
→ application services
→ domain coordination
→ repositories
→ integrations

SQLite
→ primary persistent relational data store

PowerShell 7
→ Windows administration
→ Microsoft administration
→ diagnostics
→ reporting
→ controlled automation

AutoHotkey v2
→ global hotkeys
→ hotstrings
→ clipboard automation
→ launchers
→ lightweight quick menus
→ desktop interaction
```

Technology boundaries must remain explicit.

Do not move functionality between technologies merely because another implementation would be convenient.

---

# 5. Primary Application Architecture

The preferred architecture is:

```text
PySide6 GUI
    ↓
Application Services
    ↓
Domain Logic
    ↓
Repositories / Gateways
    ↓
Infrastructure
```

Examples:

```text
TicketView
    ↓
TicketService
    ↓
TicketRepository
    ↓
SQLite
```

and:

```text
DiagnosticService
    ↓
PowerShellService
    ↓
PowerShellGateway
    ↓
pwsh.exe
```

Do not bypass architectural layers without explicit justification.

---

# 6. Architecture Style

F7Hub should initially remain a:

```text
MODULAR MONOLITH
```

Do not introduce:

- microservices
- distributed message brokers
- unnecessary service processes
- complex plugin frameworks
- heavyweight dependency injection
- event-bus infrastructure

unless a validated requirement demonstrates the need.

Complexity must earn its place.

---

# 7. Canonical Documentation

Primary project documentation is located under:

```text
Docs\
```

The canonical documentation set is:

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

Archived documents are not current source of truth.

Research documents are supporting material, not automatically approved architecture.

---

# 8. Documentation Navigation

Before significant implementation work:

```text
1. Read AGENTS.md.
2. Read ROOT.md when project orientation is needed.
3. Read Docs/19_DocumentationIndex.md.
4. Identify the task category.
5. Select the minimum sufficient canonical documents.
6. Inspect the implementation.
7. Search for existing functionality.
8. Inspect relevant tests.
9. Plan the smallest appropriate implementation.
```

Do not automatically read all 20 canonical documents for every task.

Use progressive documentation loading.

---

# 9. Documentation Authority

When information conflicts, use:

```text
1. Explicit user requirement
2. Explicitly approved architectural decision
3. Current canonical project documentation
4. Validated implementation
5. Passing tests
6. Established project conventions
7. Engineering inference
```

If a conflict affects:

- architecture
- security
- authentication
- database integrity
- data relationships
- external APIs
- repository structure
- plugins
- cross-language interfaces
- major dependencies

stop and report the conflict before making a major architectural decision.

Do not silently rewrite documentation to legitimize incorrect implementation.

---

# 10. Fact Discipline

Never invent project state.

During analysis distinguish:

```text
FACT
ASSUMPTION
INFERENCE
RECOMMENDATION
```

Examples:

```text
FACT
09_SQLSchema.md defines tickets.status as a constrained TEXT value.

ASSUMPTION
The migration implementing tickets has not yet been created.

INFERENCE
TicketRepository will probably require transactional status updates.

RECOMMENDATION
Implement ticket status persistence after migration infrastructure is tested.
```

If something was not inspected:

```text
Not verified.
```

---

# 11. Documentation Status vs Implementation Status

These concepts are separate.

Documentation statuses may include:

```text
DRAFT
REVIEW
APPROVED
DEPRECATED
ARCHIVED
```

Implementation/product statuses may include:

```text
PLANNED
IN PROGRESS
IMPLEMENTED
VERIFIED
DEFERRED
REJECTED
NOT VERIFIED
```

Test statuses are:

```text
PASS
FAIL
NOT RUN
BLOCKED
```

Do not confuse:

```text
APPROVED
```

with:

```text
IMPLEMENTED
```

or:

```text
VERIFIED
```

---

# 12. Documentation Routing

Use:

```text
Docs/19_DocumentationIndex.md
```

as the canonical task-to-document routing guide.

Typical examples follow.

---

# 13. Product / Requirements Tasks

Read:

```text
00_ProjectVision.md
01_Project.md
02_ProductRequirements.md
03_Features.md
04_UserWorkflows.md
```

Use for:

- scope
- requirements
- capabilities
- user workflows
- functional behavior
- non-functional requirements

---

# 14. GUI Tasks

Read the relevant subset of:

```text
04_UserWorkflows.md
05_GUI.md
06_SystemArchitecture.md
13_PythonArchitecture.md
15_NamingConventions.md
```

Then inspect:

```text
Python\
Tests\
```

PySide6 is the primary GUI framework.

Do not move primary GUI ownership into AutoHotkey.

---

# 15. Overall Architecture Tasks

Read:

```text
01_Project.md
06_SystemArchitecture.md
10_FolderStructure.md
14_DesignPrinciples.md
```

Then inspect the relevant technology architecture document.

---

# 16. Database Tasks

Read the relevant subset of:

```text
02_ProductRequirements.md
04_UserWorkflows.md
06_SystemArchitecture.md
07_Database.md
08_ERD.md
09_SQLSchema.md
13_PythonArchitecture.md
15_NamingConventions.md
```

Inspect:

```text
Database\
Python\
Tests\
```

before modifying persistence.

---

# 17. AutoHotkey Tasks

Read:

```text
06_SystemArchitecture.md
10_FolderStructure.md
11_AHKArchitecture.md
14_DesignPrinciples.md
15_NamingConventions.md
```

Inspect:

```text
AutoHotkey\
Tests\
```

F7Hub uses:

```text
AutoHotkey v2
```

Do not introduce AutoHotkey v1 syntax.

---

# 18. PowerShell Tasks

Read:

```text
04_UserWorkflows.md
06_SystemArchitecture.md
10_FolderStructure.md
12_PowerShellArchitecture.md
14_DesignPrinciples.md
15_NamingConventions.md
```

Inspect:

```text
PowerShell\
Tests\
```

Use PowerShell 7 by default unless a verified compatibility requirement requires Windows PowerShell 5.1.

---

# 19. Python / PySide6 Tasks

Read:

```text
05_GUI.md
06_SystemArchitecture.md
10_FolderStructure.md
13_PythonArchitecture.md
14_DesignPrinciples.md
15_NamingConventions.md
```

Inspect:

```text
Python\
Tests\
```

---

# 20. Planning Tasks

Read:

```text
16_Roadmap.md
17_Todo.md
18_ChangeLog.md
```

Planning documents are not substitutes for technical specifications.

---

# 21. Inspect Before Creating

Before creating any:

- database table
- column
- relationship
- migration
- index
- view
- trigger
- class
- service
- repository
- utility
- configuration system
- external adapter
- plugin
- PowerShell script
- AutoHotkey module
- Python module
- GUI component
- diagnostic
- workflow
- command
- API abstraction

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

Search:

- filenames
- classes
- functions
- database entities
- services
- repositories
- commands
- migrations
- tests
- documentation

Avoid duplicate functionality.

---

# 22. Scope Control

For focused tasks:

- implement only requested scope
- avoid unrelated refactoring
- avoid unrelated renaming
- avoid repository-wide cleanup
- avoid speculative abstractions
- avoid unnecessary dependencies
- avoid changing APIs without need
- avoid altering neighboring subsystems
- avoid changing unrelated documentation

If unrelated improvement is discovered:

```text
record follow-up
→ continue current scope
```

Do not silently expand the task.

---

# 23. Vertical Slice Rule

Prefer small vertical slices.

Good:

```text
Implement ticket creation persistence,
including migration,
repository,
service validation,
and tests.
```

Avoid:

```text
Build Ticket Center.
```

Prefer:

```text
Implement PowerShell structured execution
for one registered read-only diagnostic.
```

Avoid:

```text
Build the PowerShell subsystem.
```

---

# 24. Implementation Process

For non-trivial work use the following lifecycle.

## UNDERSTAND

Determine:

- objective
- user need
- affected subsystem
- expected behavior
- dependencies
- constraints
- acceptance criteria
- documentation impact

## INSPECT

Inspect:

- relevant docs
- repository structure
- existing code
- migrations
- schema
- configuration
- tests
- dependencies
- related implementations

## PLAN

Create the smallest coherent implementation sequence.

Identify:

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

## IMPLEMENT

Implement only the approved slice.

## TEST

Execute applicable tests.

## REVIEW

Review architecture, correctness, security, duplication, integrity, maintainability, and failure paths.

## DOCUMENT

Update affected canonical documentation only after behavior is understood and appropriately validated.

---

# 25. Coding-Agent Task Contract

When creating work for Codex or another coding agent, define:

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

Example:

```text
OBJECTIVE

Implement SQLite migration bootstrap.

SCOPE

- connection initialization
- foreign key enforcement
- migration discovery
- migration ordering
- migration tracking
- checksum validation
- tests

OUT OF SCOPE

- GUI
- ticket implementation
- PowerShell
- AI
- plugins
```

---

# 26. Python Architecture Rules

Python/PySide6 is the architectural center of F7Hub.

Preferred dependency direction:

```text
gui
 ↓
services
 ↓
domain
 ↓
repositories / gateways
 ↓
infrastructure
```

Do not create reverse dependencies such as:

```text
domain
→ PySide6
```

or:

```text
repository
→ GUI widget
```

---

# 27. GUI Rules

PySide6 GUI components primarily own:

- rendering
- input collection
- navigation
- GUI state
- visual feedback
- signal/slot interaction

They do not own:

- raw SQL
- migration logic
- PowerShell command construction
- Microsoft authentication
- domain rules
- external credential handling

Preferred:

```text
GUI
→ Service
```

not:

```text
GUI
→ SQLite
```

---

# 28. Service Rules

Application services own use cases.

Examples:

```text
TicketService
KnowledgeService
SearchService
DiagnosticService
ScriptService
PowerShellService
```

Services may:

- validate workflows
- coordinate repositories
- coordinate gateways
- manage transaction boundaries
- enforce application rules

Services should not contain PySide6-specific presentation logic.

---

# 29. Domain Rules

Domain logic should remain independent from:

- PySide6
- SQLite implementation details
- PowerShell
- external provider SDKs
- AI provider SDKs

Domain concepts should be modeled only when they improve clarity or correctness.

Do not create a domain object for every database table mechanically.

---

# 30. Repository Rules

Repositories own normal SQLite persistence.

Preferred:

```text
Service
 ↓
Repository
 ↓
SQLite
```

Repositories should:

- use parameterized SQL
- map results into structured values
- handle persistence-specific concerns
- avoid business workflow decisions
- avoid GUI dependencies

Do not return raw cursors to the GUI.

---

# 31. SQLite Rules

SQLite is foundational.

Preserve:

- normalization
- primary keys
- foreign keys
- constraints
- transactions
- migrations
- intentional indexes
- FTS5 where justified
- data integrity

Every application connection must enable:

```sql
PRAGMA foreign_keys = ON;
```

The current schema also recommends:

```sql
PRAGMA busy_timeout = 5000;
```

unless configuration later changes that value.

---

# 32. SQL Parameterization

Always parameterize dynamic values.

Correct:

```python
cursor.execute(
    "SELECT * FROM tickets WHERE ticket_id = ?",
    (ticket_id,),
)
```

Incorrect:

```python
cursor.execute(
    f"SELECT * FROM tickets WHERE ticket_id = {ticket_id}"
)
```

Never concatenate untrusted input into SQL.

---

# 33. Database Schema Authority

The exact physical SQLite schema belongs to:

```text
Docs/09_SQLSchema.md
```

It includes:

- tables
- columns
- exact data types
- constraints
- exact foreign keys
- indexes
- views
- FTS objects
- approved triggers

Do not create a table solely from memory or from `08_ERD.md`.

The ERD is conceptual.

The SQL Schema is physical.

---

# 34. No Arbitrary Table Targets

F7Hub does not target:

```text
100 tables
120 tables
or any arbitrary number
```

Create a table only because a requirement and persistent domain relationship justify it.

---

# 35. Database Change Procedure

Before changing the schema:

```text
Requirement
    ↓
Inspect Current Schema
    ↓
Review 07_Database.md
    ↓
Review 08_ERD.md
    ↓
Review 09_SQLSchema.md
    ↓
Design Migration
    ↓
Implement
    ↓
Repository Changes
    ↓
Tests
    ↓
Documentation
```

---

# 36. Migration Rules

Schema changes require versioned migrations.

Current migration naming convention:

```text
NNNN_description.sql
```

Example:

```text
0001_core.sql
0002_taxonomy.sql
0003_companies_contacts.sql
0004_tickets.sql
```

Migration history is authoritative through:

```text
schema_migrations
```

not through competing manual version tracking.

---

# 37. Migration Immutability

Applied released migrations are historical records.

Do not silently edit them.

Migration tooling should validate recorded checksums where implemented.

If an applied migration must be changed:

```text
create a new migration
```

unless the migration is provably unreleased and the task explicitly permits revision.

---

# 38. Migration Safety

Never:

- casually drop tables
- casually remove columns
- silently destroy data
- disable foreign keys to force success
- change PKs casually
- alter core relationships without review
- mark failed migrations as applied

Potentially destructive migration changes require explicit approval.

---

# 39. Database Transactions

Use transactions for logical units of work.

Example:

```text
Create Ticket
+
Initial Status History
+
Timeline Event
```

should succeed or fail together where required.

Do not hold SQLite transactions open while waiting on:

- PowerShell
- network calls
- Microsoft Graph
- AI
- external applications

Commit local state, perform external work, then use a short transaction to record results.

---

# 40. Index Rules

Indexes must follow real query patterns.

Do not:

```text
index every column
```

Use:

```sql
EXPLAIN QUERY PLAN
```

where relevant.

An index must justify its read-performance benefit against:

- storage
- write cost
- maintenance

---

# 41. FTS5 Rules

FTS5 is intended for natural text search such as:

- knowledge articles
- tickets
- scripts
- prompts

FTS tables are derived search infrastructure.

They are not authoritative application data.

Relational source tables remain source of truth.

FTS synchronization triggers are a justified trigger use.

---

# 42. Trigger Rules

Avoid ordinary business logic in SQLite triggers.

Do not implement triggers that:

- run scripts
- branch diagnostics
- create AI actions
- determine ticket workflow
- enforce user permissions
- initiate external calls

Application services own such behavior.

Triggers should be used only where database-local infrastructure behavior clearly benefits.

---

# 43. SQLite Integrity Testing

Database work should eventually validate:

```sql
PRAGMA integrity_check;
```

Expected:

```text
ok
```

and:

```sql
PRAGMA foreign_key_check;
```

Expected:

```text
zero violations
```

Do not claim database validity without executing appropriate checks.

---

# 44. PowerShell Architecture Rules

PowerShell 7 is the preferred runtime.

Default executable:

```text
pwsh.exe
```

Use Windows PowerShell 5.1 only for a verified compatibility requirement.

PowerShell primarily owns:

- Windows administration
- Microsoft administration
- diagnostics
- remediation scripts
- reporting
- automation

PowerShell does not own core application persistence.

---

# 45. PowerShell Execution Boundary

Preferred flow:

```text
GUI
 ↓
ScriptService / DiagnosticService
 ↓
PowerShellService
 ↓
PowerShellGateway
 ↓
pwsh.exe
 ↓
Registered Script
 ↓
Structured Result
 ↓
Python
```

Do not let arbitrary widgets launch raw shell commands.

---

# 46. PowerShell Safety

PowerShell code must:

- validate parameters
- use clear error handling
- avoid unnecessary elevation
- avoid destructive defaults
- protect secrets
- expose predictable results
- clearly report failure

Where applicable, support:

```text
-WhatIf
```

or equivalent preview/dry-run behavior.

---

# 47. PowerShell Structured Output

Scripts integrated with F7Hub should return structured machine-readable output.

Preferred form:

```json
{
  "schemaVersion": 1,
  "operation": "Test-DnsHealth",
  "success": true,
  "status": "PASS",
  "message": "DNS resolution succeeded.",
  "data": {},
  "warnings": [],
  "errors": []
}
```

Do not force Python to parse decorative `Format-Table` output.

---

# 48. PowerShell Command Injection

Avoid:

```powershell
Invoke-Expression
```

for user-controlled execution.

Python should invoke:

```text
known executable
+
known script
+
validated arguments
```

using argument arrays.

Avoid unnecessary:

```text
shell=True
```

---

# 49. AutoHotkey v2 Rules

AutoHotkey is a lightweight desktop productivity layer.

Use primarily for:

- hotkeys
- hotstrings
- clipboard helpers
- launch/focus behavior
- Windows tools
- quick menus

Do not build a parallel full F7Hub application in AHK.

Do not use AHK v1 syntax.

---

# 50. AutoHotkey Database Boundary

AutoHotkey should not normally modify core SQLite state directly.

Preferred:

```text
AHK Action
    ↓
F7Hub Command
    ↓
Python
    ↓
Service
    ↓
Repository
```

---

# 51. Clipboard Safety

Clipboard automation must treat clipboard content as untrusted.

Where temporary replacement occurs, preserve and restore user clipboard state when appropriate.

Persistent clipboard history must remain optional and privacy-aware.

---

# 52. UI Automation Rule

Preferred integration order:

```text
API
 ↓
PowerShell / supported CLI
 ↓
documented application integration
 ↓
UI automation
```

Use UI automation only when better interfaces do not exist.

Prefer state-based waits over arbitrary sleeps where possible.

---

# 53. AI Rules

AI is an assistant, not an execution authority.

AI may:

- summarize
- explain
- suggest
- draft
- recommend
- help search

AI must not directly:

- execute PowerShell
- run shell commands
- modify tenant configuration
- delete database records
- perform destructive administration

without normal F7Hub service boundaries and explicit technician control.

---

# 54. AI Output Is Untrusted

Treat AI-generated:

- text
- JSON
- SQL
- Python
- PowerShell
- AutoHotkey
- recommendations

as untrusted until reviewed and validated.

Never assume generated output is correct because it appears plausible.

---

# 55. AI-Generated Code Review

Review AI-generated code for:

- correctness
- architecture
- security
- injection risk
- error handling
- data integrity
- performance
- duplication
- maintainability
- tests
- documentation impact

---

# 56. Security Rules

Use:

```text
least privilege
+
secure defaults
+
explicit user intent
```

Never hard-code or expose:

- passwords
- API keys
- access tokens
- refresh tokens
- private keys
- client secrets

---

# 57. Untrusted Inputs

Treat as untrusted:

- user input
- ticket text
- clipboard content
- files
- file paths
- URLs
- API responses
- external identifiers
- PowerShell output
- AI output
- imported data
- configuration supplied externally

Validate at the correct boundary.

---

# 58. Filesystem Safety

When handling paths:

- prevent traversal
- sanitize generated filenames
- preserve original file metadata where useful
- avoid silent overwrite
- validate expected locations
- treat executable/imported content as untrusted

Attachments normally remain filesystem files with SQLite metadata.

---

# 59. Secrets and Configuration

Ordinary configuration must not become secret storage.

Do not store plaintext credentials in:

```text
Python source
PowerShell source
AHK source
Markdown docs
Git
normal JSON/YAML/INI config
normal SQLite settings
logs
```

If persistent credentials become required, use an explicitly approved secure secret-storage architecture.

---

# 60. Testing Requirements

Code is not complete merely because it runs.

Use appropriate:

- unit tests
- repository tests
- database tests
- migration tests
- integration tests
- GUI tests
- PowerShell tests
- regression tests
- end-to-end tests

Test both:

```text
success
```

and:

```text
failure
```

paths.

---

# 61. Test Reporting

Never write:

```text
Tests passed.
```

unless those tests were actually executed.

Use:

```text
PASS
FAIL
NOT RUN
BLOCKED
```

Report exactly what was executed.

Example:

```text
Database migration tests: PASS
GUI tests: NOT RUN
Microsoft Graph live test: BLOCKED
```

---

# 62. Database Testing Requirements

Database work should test where applicable:

- fresh database migration
- incremental migration
- migration ordering
- migration checksum handling
- foreign keys
- constraints
- transactions
- repository behavior
- failed migration rollback
- query plans
- FTS synchronization
- integrity checks

---

# 63. GUI Testing Requirements

GUI work should test appropriate:

- widget construction
- navigation
- validation
- signals
- state transitions
- worker completion
- error presentation
- core workflows

Avoid unnecessary pixel-perfect tests.

---

# 64. PowerShell Testing Requirements

PowerShell work should test where appropriate:

- syntax
- parameters
- invalid input
- structured JSON output
- non-zero exit
- missing dependency
- timeout
- privilege failure
- Python integration

Pester may be used where appropriate.

---

# 65. Failure Is Part of the Design

Assume:

```text
database calls fail
PowerShell scripts fail
network requests fail
APIs change
modules are missing
files disappear
users cancel
AI providers fail
```

Define failure behavior.

Do not implement success paths only.

---

# 66. Error Handling

Do not suppress unexpected errors.

Avoid:

```python
try:
    ...
except Exception:
    pass
```

Catch errors where a layer can:

- handle them
- translate them
- log useful detail
- return safe user feedback

---

# 67. Logging

Use centralized application logging.

Do not log:

- secrets
- tokens
- passwords
- unrestricted clipboard contents
- entire API responses without need
- sensitive AI context without review

Logs are not a secondary database.

---

# 68. Audit vs Logs

Keep separate:

```text
Application Logs
→ technical behavior

Audit Events
→ meaningful user/system actions
```

Do not audit every click.

---

# 69. Background Work

Never block the PySide6 event loop with:

- PowerShell
- network calls
- AI
- large exports
- long DB operations
- filesystem scans

Use an appropriate worker model.

GUI widgets must be updated from the GUI thread.

---

# 70. Cancellation

Cancellation semantics must be truthful.

Distinguish:

```text
CANCELLABLE
BEST_EFFORT
NOT_CANCELLABLE
```

Never report a remote action as cancelled if it already completed.

---

# 71. Dependencies

Before adding a third-party dependency:

1. identify the requirement
2. inspect existing dependencies
3. determine whether the standard library/current dependency solves it
4. assess maintenance/security cost
5. document major dependency changes
6. test compatibility

Avoid overlapping libraries solving the same problem.

---

# 72. Current Official Documentation

For changing technologies and APIs, verify current official documentation where appropriate.

Especially:

- Python
- PySide6
- SQLite
- Microsoft Graph
- Exchange Online
- Intune
- Defender
- GitHub
- OpenAI APIs

Do not rely blindly on outdated tutorials.

---

# 73. Project Skills

Specialized procedures may exist under:

```text
.agents\skills\
```

Expected areas include:

```text
architecture
sqlite-database
autohotkey-v2
powershell
pyqt6
testing
documentation
codex-orchestration
code-review
security
```

Use relevant skills when appropriate.

Canonical project documentation defines F7Hub-specific requirements.

Skills define technical procedures.

If a skill conflicts with explicit F7Hub architecture:

```text
F7Hub canonical architecture wins
```

unless an explicitly approved change supersedes it.

---

# 74. Git Safety

Before substantial modifications:

```text
inspect Git status
inspect current branch
understand unrelated local changes
```

Do not:

- discard user changes
- reset unrelated work
- force-clean files
- rewrite history
- overwrite unrelated modifications
- commit secrets

without explicit authorization.

---

# 75. Branch Strategy

Preferred patterns:

```text
main
feature/*
fix/*
docs/*
refactor/*
experiment/*
```

Use focused branches where appropriate.

Do not create unnecessary branch complexity.

---

# 76. Destructive Git Operations

Operations such as:

```text
git reset --hard
git clean -fd
force push
history rewrite
```

must never be used casually.

If required, explain impact and obtain explicit approval.

---

# 77. Documentation Synchronization

After a meaningful implementation change, identify the canonical owner documents.

Database:

```text
07_Database.md
08_ERD.md
09_SQLSchema.md
```

GUI:

```text
05_GUI.md
06_SystemArchitecture.md
13_PythonArchitecture.md
```

AutoHotkey:

```text
11_AHKArchitecture.md
```

PowerShell:

```text
12_PowerShellArchitecture.md
```

Python architecture:

```text
13_PythonArchitecture.md
```

Naming:

```text
15_NamingConventions.md
```

Planning/history where appropriate:

```text
16_Roadmap.md
17_Todo.md
18_ChangeLog.md
```

---

# 78. Documentation Impact Analysis

Before finishing significant work, determine:

```text
DOCUMENTATION IMPACT

Affected:
- ...

Potentially affected:
- ...

Not affected:
- ...

Reason:
- ...
```

Only update documentation actually affected.

Avoid documentation churn.

---

# 79. Documentation Accuracy

Do not document a planned feature as implemented.

Do not document an implemented feature as verified unless validation was performed.

Do not rewrite requirements merely because implementation differs.

Incorrect implementation should be corrected rather than legitimized through documentation.

---

# 80. Architecture Escalation

Explicit review is required before:

- destructive migrations
- core database relationship changes
- authentication redesign
- security-boundary changes
- major dependency changes
- framework changes
- repository restructuring
- plugin architecture changes
- IPC/cross-language contract changes
- replacement of SQLite
- replacement of PySide6
- change to Python ownership
- major PowerShell/AHK ownership change

---

# 81. Architecture Change Procedure

For a major proposed change:

```text
1. Describe current architecture.
2. Identify the limitation.
3. Describe proposed architecture.
4. Explain why change is necessary.
5. Describe simpler alternatives.
6. Identify migration cost.
7. Identify risks.
8. Identify affected docs/tests.
9. Request approval if not already explicitly authorized.
```

Do not silently make major architectural decisions.

---

# 82. Plugins

Plugin architecture is deferred until real extension requirements exist.

Do not build:

- generic plugin loader
- plugin marketplace
- unrestricted plugin API
- provider-specific plugin directories

without an approved use case.

Future plugins should not receive unrestricted database access by default.

---

# 83. Integrations

External integrations should generally evolve:

```text
Connect
   ↓
Read
   ↓
Display
   ↓
Link
   ↓
Controlled Update
   ↓
Synchronization
```

Do not begin with automatic bidirectional synchronization.

External systems remain authoritative for their own data unless explicitly designed otherwise.

---

# 84. Microsoft Integration Safety

Begin with read-only operations where possible.

Before implementation verify:

- supported module/API
- required permissions
- authentication model
- least privilege
- failure behavior
- token handling

Do not request broad tenant permissions merely for convenience.

---

# 85. Implementation Completeness

A feature is complete only when applicable:

```text
requested behavior implemented
architecture preserved
security considered
data integrity preserved
errors handled
tests executed
test results reported
documentation synchronized
risks identified
scope respected
```

---

# 86. Completion Checklist

Before declaring work complete:

```text
[ ] Requested behavior implemented
[ ] Relevant documentation inspected
[ ] Existing implementation inspected
[ ] Existing functionality searched
[ ] Duplicate functionality avoided
[ ] Correct architectural layer used
[ ] Scope remained controlled
[ ] Security considered
[ ] Database integrity preserved
[ ] Input validation implemented
[ ] Error handling implemented
[ ] Success path tested
[ ] Failure path tested
[ ] Test results reported accurately
[ ] Documentation impact analyzed
[ ] Affected docs synchronized
[ ] Unrelated work preserved
[ ] Remaining risks identified
[ ] Follow-up work recorded if needed
```

---

# 87. Standard Implementation Report

For implementation work, report:

```text
Summary

Files Changed

Tests

Result

Architecture Impact

Security Impact

Risks

Documentation

Next Step
```

Do not hide failures.

---

# 88. Planning Report

For planning work include:

```text
Objective

Current Verified State

Implementation Sequence

Files / Subsystems Affected

Acceptance Criteria

Validation

Risks

Documentation Impact
```

Do not generate substantial implementation before the plan is understood for complex tasks.

---

# 89. Code Review Report

For code review include:

```text
Summary

Findings

Severity

Architecture

Security

Database Integrity

Tests

Documentation

Recommendation
```

Prioritize concrete defects over stylistic preferences.

---

# 90. First Implementation Phase

After documentation review is complete, the first major implementation objective is:

```text
SQLite bootstrap and migration infrastructure
```

The first task should not be:

```text
Build F7Hub.
```

---

# 91. First Codex Slice

Initial recommended scope:

```text
OBJECTIVE

Implement F7Hub SQLite bootstrap and migration infrastructure.

CONTEXT

Read:
- AGENTS.md
- ROOT.md
- Docs/19_DocumentationIndex.md
- Docs/07_Database.md
- Docs/09_SQLSchema.md
- Docs/10_FolderStructure.md
- Docs/13_PythonArchitecture.md
- Docs/15_NamingConventions.md

SCOPE

- database connection creation
- PRAGMA foreign_keys = ON
- PRAGMA busy_timeout
- migration discovery
- migration ordering
- schema_migrations tracking
- migration checksum validation
- transactional migration execution
- database tests

OUT OF SCOPE

- ticket GUI
- ticket persistence
- PowerShell
- AutoHotkey
- AI
- diagnostics
- plugins
- Microsoft integrations

VALIDATION

Run isolated database tests.

DELIVERABLES

- implementation
- tests
- applicable documentation updates
```

---

# 92. Subsequent Development Sequence

After migration infrastructure:

```text
Taxonomy / Companies / Contacts
        ↓
Ticket Persistence
        ↓
Ticket Service
        ↓
PySide6 Application Shell
        ↓
Ticket Creation UI
        ↓
Ticket Notes / Status
        ↓
Knowledge Base
        ↓
Search
        ↓
Script Registry
        ↓
PowerShell
        ↓
Diagnostics
```

Follow `16_Roadmap.md` for the wider sequence.

---

# 93. What Not to Build First

Do not begin with:

```text
AI assistant
plugin loader
plugin marketplace
full Microsoft integration
bidirectional PSA sync
complex workspace manager
100-table database
persistent PowerShell runspace
autonomous administration
```

These depend on foundations that do not yet exist.

---

# 94. Final Development Principle

F7Hub development should repeatedly follow:

```text
Requirement
    ↓
Relevant Documentation
    ↓
Repository Inspection
    ↓
Small Plan
    ↓
Focused Implementation
    ↓
Tests
    ↓
Review
    ↓
Documentation
    ↓
Next Slice
```

The final rule is:

> Build F7Hub through small, tested, documented, secure, and reversible changes. Respect technology ownership, protect SQLite integrity, treat automation and AI as controlled capabilities, and never trade architectural clarity for code volume.
