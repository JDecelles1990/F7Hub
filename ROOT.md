# F7Hub Root Project Definition

> File: `ROOT.md`  
> Project: F7Hub  
> Project Root: `C:\Dev\F7Hub\`  
> Purpose: Provide the concise, stable project entry point for humans and coding agents.
> Status: `REVIEW`

---

# 1. Role of This File

`ROOT.md` explains:

```text
WHAT F7Hub is
WHERE the project begins
HOW the major technologies relate
WHERE authoritative information lives
HOW to navigate the repository
```

It is intentionally more stable than implementation-status documents.

`ROOT.md` is not:

```text
a running development log
a complete architecture specification
a test report
a replacement for AGENTS.md
a replacement for the canonical Docs/ set
a replacement for feature planning documents
```

Detailed current implementation state belongs in:

```text
Docs/Status/CURRENT_STATE.md
```

where available, together with actual repository state, Git history and executed test evidence.

Historical development changes belong primarily in:

```text
Docs/18_ChangeLog.md
Git history
review records
integration records
archived planning artifacts
```

---

# 2. When Coding Agents Should Read ROOT.md

Coding agents should read `ROOT.md` when:

```text
starting substantial work in F7Hub
orienting to the repository
starting a new feature or architecture phase
determining technology ownership
determining documentation routing
resolving uncertainty about project-wide boundaries
performing a major review
```

Agents do not need to reread `ROOT.md` for every trivial edit when the applicable project context is already established.

`AGENTS.md` remains the authoritative mechanism for agent behavior.

Recommended project-entry sequence:

```text
AGENTS.md
    ↓
ROOT.md
    ↓
Docs/19_DocumentationIndex.md
    ↓
Relevant scoped AGENTS.md
    ↓
Relevant canonical or planning documents
    ↓
Relevant project skills
    ↓
Repository inspection
    ↓
Relevant tests
```

---

# 3. What F7Hub Is

F7Hub is a modular Windows IT Support and technician-productivity platform.

Its purpose is to reduce fragmentation during technical-support work by bringing relevant technician workflows into one controlled application.

Potential and existing areas include:

```text
Tickets and case context
Companies and contacts
Knowledge retrieval
Clipboard productivity
Troubleshooting and diagnostics
Controlled PowerShell automation
Windows administration
Microsoft administration
Search
Technician Workspace
Case Journal and case-note assistance
Evidence
Reporting
Analytics
AI-assisted support
External integrations
Desktop automation
```

F7Hub is a technician command center.

It is not intended to replace every external IT platform.

External PSA, RMM, identity, credential, AI, security or Microsoft administration systems may remain systems of record or execution providers while F7Hub coordinates technician workflows around them.

---

# 4. Canonical Project Root

The canonical development root is:

```text
C:\Dev\F7Hub\
```

Production/runtime behavior must not depend permanently on this development path.

Paths used by production behavior must be resolved through approved configuration, application paths or runtime discovery rather than hard-coded development-machine assumptions.

---

# 5. Core Product Principles

F7Hub should remain:

```text
modular
understandable
offline-capable
extensible
vendor-neutral where practical
secure by default
technician-controlled
testable
reviewable
reversible
```

## 5.1 Build the Correct System

Prefer:

```text
small
verified
documented
reusable
independently testable
```

changes over large uncontrolled implementations.

Use:

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

---

## 5.2 Inspect Before Creating

Before creating a new:

```text
table
migration
class
service
repository
gateway
utility
configuration mechanism
protocol
registry
catalog
plugin
integration abstraction
```

use:

```text
SEARCH
    ↓
IDENTIFY
    ↓
REUSE / EXTEND
    ↓
CREATE ONLY IF NECESSARY
```

F7Hub is not a greenfield project.

---

## 5.3 Offline First

Offline behavior is a project priority.

Core local technician workflows should continue to function without requiring:

```text
internet access
external PSA
external RMM
external AI
external credential manager
Microsoft cloud API
other remote provider
```

where those workflows are classified as locally required.

Architecture should distinguish:

```text
LOCAL_REQUIRED
ONLINE_OPTIONAL
ONLINE_REQUIRED
```

External integrations enhance F7Hub.

They must not accidentally become dependencies of unrelated local functionality.

Case Journal storage, local case-note drafting and editing must remain architecturally capable of operating offline.

External AI may enhance locally generated content but must not be required for core offline note generation.

---

# 6. Technician Workspace Principle

F7Hub may provide a first-class:

```text
Technician Workspace
```

inside the primary PySide6 application.

Its purpose is to host substantial technician tools inside the main application rather than opening unnecessary independent desktop windows.

Potential responsibilities include:

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

The Technician Workspace is a presentation/application-shell concept.

It must not become the owner of unrelated business logic.

Examples:

```text
Ticket behavior
→ Ticket services/domain

Clipboard behavior
→ Clipboard services/domain

Diagnostics
→ Diagnostic services/domain

Knowledge
→ Knowledge services/domain

PowerShell execution
→ approved PowerShell/application boundary

Analytics
→ Analytics domain/services

Mochi reasoning
→ approved Mochi/application boundary
```

A future `Active Technician Context` may connect Company, User, Device, Ticket, Tenant and other working context across Workspace tools without transferring domain ownership to the Workspace itself.

Detailed Workspace architecture belongs to its feature planning documents.

---

# 7. Technology Ownership

| Technology | Primary responsibility |
|---|---|
| Python / PySide6 | Primary desktop application, GUI, orchestration, application services, domain coordination, repositories and integration coordination |
| SQLite | Primary persistent relational data store |
| PowerShell 7 | Windows and Microsoft administration, diagnostics, reporting and approved automation |
| AutoHotkey v2 | Global hotkeys, hotstrings, clipboard helpers, Windows interaction, launch/focus behavior and lightweight quick interfaces |
| Mochi | Contextual assistant/presentation capability operating through approved F7Hub boundaries |

PySide6 is the primary F7Hub application GUI.

AutoHotkey is not a second business-application framework.

Normal core SQLite writes flow through the approved Python repository/application architecture.

PowerShell and AutoHotkey do not independently own core application persistence.

Mochi must not bypass approved application-service, security, persistence or execution boundaries.

Detailed ownership is defined by approved architecture rather than this summary.

---

# 8. Primary Architecture

F7Hub begins as a modular monolith.

Preferred dependency direction:

```text
PySide6 GUI
    ↓
Application / Services
    ↓
Domain Logic
    ↓
Repositories / Gateways
    ↓
Infrastructure
```

Key principles:

```text
GUI does not own raw SQL.

GUI does not construct arbitrary shell commands.

Domain logic does not depend directly on PySide6.

Domain logic should not depend on SQLite implementation details.

Repositories own normal relational persistence.

Gateways isolate external processes, APIs and provider-specific behavior.

PowerShell should return structured results where practical.

External provider DTOs should normally stop at integration boundaries.

AI output is untrusted.

Destructive or security-sensitive AI-generated actions require explicit approved execution paths.

Plugin architecture remains governed by validated extension requirements rather than speculative abstraction.
```

---

# 9. Foundation Architecture

Cross-cutting architecture planning is maintained under:

```text
Docs/Planning/Foundation/
```

The Foundation sequence is:

```text
0A  Master Foundation Architecture
0B  Global JSON / Interoperability Contract
0C  Taxonomy / Information Vocabulary
0D  Settings / Configuration Architecture
0E  Foundation Architecture Reconciliation
```

Conceptual ownership:

```text
0A
→ Who owns what?

0B
→ How do components communicate?

0C
→ What does information mean?

0D
→ What can be configured and how?

0E
→ Do 0A–0D form one coherent Foundation?
```

Foundation-specific agent guidance belongs in:

```text
Docs/Planning/Foundation/AGENTS.md
```

Planning documents are not automatically proof of implemented behavior.

Unapproved Foundation recommendations must not be treated as implemented architecture.

After Foundation architecture is reviewed and approved, future feature planning should consume it rather than independently inventing parallel:

```text
ownership rules
interoperability grammars
taxonomy systems
Settings systems
security boundaries
secret-handling rules
integration boundaries
offline semantics
```

---

# 10. Source-of-Truth Priority

When project information conflicts, use:

```text
1. Explicit user requirement
2. Explicitly approved architectural decision
3. Current canonical project documentation
4. Validated implementation
5. Executed passing tests
6. Established project conventions
7. Engineering inference
```

Material conflicts must be surfaced.

Do not silently resolve significant architectural contradictions.

If something has not been inspected, say:

```text
NOT VERIFIED
```

---

# 11. Documentation Model

F7Hub documentation serves different purposes.

## 11.1 Canonical Documentation

The numbered Markdown files under:

```text
Docs/
```

describe current approved project requirements, architecture and behavior.

They are living documentation.

They are not immutable historical snapshots.

When approved implementation changes current behavior, update the relevant canonical documentation.

---

## 11.2 Planning Documentation

Architecture and feature planning lives under:

```text
Docs/Planning/
```

Planning documents may contain:

```text
architecture contracts
investigation instructions
decision records
risk registers
execution reports
reconciliation reports
downstream contracts
```

Planning documentation does not prove implementation.

---

## 11.3 Current-State Documentation

Verified current implementation state should be recorded in:

```text
Docs/Status/CURRENT_STATE.md
```

or another explicitly approved current-state artifact.

Current-state claims must be supported by actual repository inspection and validation.

---

## 11.4 Historical Documentation

Historical information belongs primarily in:

```text
Docs/18_ChangeLog.md
Git history
review reports
integration reports
archived planning artifacts
```

Do not preserve obsolete current-state descriptions merely to keep history.

Do not rewrite historical records to make later designs appear as though they always existed.

---

# 12. Canonical Documentation Routing

F7Hub maintains 20 numbered canonical Markdown documents, `00` through `19`, directly under `Docs\`.

Document ownership and routing are defined by:

```text
Docs/19_DocumentationIndex.md
```

Important database responsibility is separated:

```text
Docs/07_Database.md
→ database rules and strategy

Docs/08_ERD.md
→ conceptual entities and relationships

Docs/09_SQLSchema.md
→ exact physical SQLite schema
```

Planning and development tracking are separated:

```text
Docs/16_Roadmap.md
→ long-term sequence

Docs/17_Todo.md
→ actionable work

Docs/18_ChangeLog.md
→ meaningful completed changes
```

Do not read every canonical document for every task.

Use `Docs/19_DocumentationIndex.md` and applicable agent guidance to select the minimum sufficient documentation set.

---

# 13. Canonical Documentation Is Updated With the Product

When application behavior changes, agents must assess documentation impact.

Examples:

```text
GUI behavior changes
→ inspect 05_GUI.md
→ inspect 06_SystemArchitecture.md when architecture is affected

Database structure changes
→ inspect 07_Database.md
→ inspect 08_ERD.md
→ inspect 09_SQLSchema.md

AutoHotkey behavior changes
→ inspect 11_AHKArchitecture.md

PowerShell behavior changes
→ inspect 12_PowerShellArchitecture.md

Python architecture changes
→ inspect 13_PythonArchitecture.md

Feature/workflow changes
→ inspect relevant Feature and Workflow documents

Meaningful completed change
→ inspect 18_ChangeLog.md
```

Documentation impact must be determined from the actual change.

Do not mechanically edit unrelated documents.

---

# 14. External Integrations

F7Hub must support future employer-approved integrations without making a specific vendor foundational unless explicitly approved.

Potential categories include:

```text
PSA
RMM
Microsoft administration
identity
credential management
security
monitoring
documentation
AI
other employer-approved APIs
```

Potential providers such as HaloPSA, NinjaOne, CIPP, Keeper, Microsoft Graph or a company AI are examples only.

Do not assume a particular provider is available.

Prefer:

```text
F7Hub Domain
    ↓
Application Service
    ↓
Integration Gateway / Adapter
    ↓
External Provider
```

Provider-specific DTOs, authentication models and API details should normally remain at the integration boundary.

A configured provider does not imply every provider capability or permission is available.

Future integrations should support capability-aware behavior where appropriate.

---

# 15. External Systems of Record

F7Hub may maintain local working state while another system remains authoritative for an official record.

Architecture must be capable of distinguishing:

```text
local working state
local draft
local evidence
pending synchronization
confirmed synchronized state
authoritative external record
```

For example, a future ticketing integration may allow:

```text
F7Hub
→ owns local Case Journal and draft note

External PSA
→ owns official published ticket note
```

The exact provider remains integration-specific.

Local workflows must not become unusable merely because the external system is temporarily unavailable.

---

# 16. Security and Data Boundary

F7Hub must use least privilege and secure defaults.

Treat as untrusted where applicable:

```text
user input
clipboard data
files
URLs
commands
external API responses
AI output
imported data
IPC messages
```

Do not hard-code:

```text
passwords
API keys
access tokens
refresh tokens
private keys
authentication secrets
```

Secrets are not ordinary:

```text
application data
Settings
Clipboard history
Case Journal content
Analytics input
Mochi context
documentation
test fixtures
normal logs
```

Future credential integrations should prefer secure references, transient access, least privilege and approved credential-broker behavior.

F7Hub must not become an accidental password manager.

---

# 17. Employer and Customer Data

F7Hub architecture, source code, documentation and tests should not require real employer or customer operational data.

Use synthetic examples wherever practical.

Do not intentionally commit real:

```text
credentials
customer secrets
access tokens
private identifiers
production ticket content
customer device inventory
tenant data
confidential logs
```

into:

```text
source code
planning documents
canonical examples
Git history
test fixtures
seed data
sample JSON
committed screenshots
AI prompt fixtures
```

unless explicitly authorized and necessary.

Runtime processing of employer-authorized operational data is different from storing that information in the F7Hub development repository.

When employer policy is unknown:

```text
minimize collection
minimize persistence
avoid unnecessary external transmission
do not invent policy
mark uncertainty NOT VERIFIED
```

---

# 18. Repository Structure

Core project areas include:

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
Mochi\
```

Exact folder ownership and canonical structure belong to:

```text
Docs/10_FolderStructure.md
```

Do not create speculative directory trees merely because they are conceivable.

---

# 19. Skills

Project-local agent skills may exist under:

```text
.agents/skills/
```

Use specialized skills when they are relevant to the task.

A skill does not override:

```text
explicit user requirements
approved architecture
AGENTS.md
applicable scoped AGENTS.md
```

Do not invoke implementation-oriented lifecycle machinery mechanically for documentation-only architecture work unless the skill is actually appropriate.

---

# 20. Status Discipline

Documentation status and implementation status are separate.

Documentation statuses may include:

```text
DRAFT
REVIEW
APPROVED
DEPRECATED
ARCHIVED
```

Planning documentation may additionally use statuses defined by:

```text
Docs/Planning/AGENTS.md
```

Implementation statuses include:

```text
PLANNED
IN PROGRESS
IMPLEMENTED
VERIFIED
DEFERRED
REJECTED
NOT VERIFIED
```

Test and validation statuses are:

```text
PASS
FAIL
NOT RUN
BLOCKED
```

Do not equate:

```text
documented
approved
implemented
verified
```

These are different states.

---

# 21. Current Implementation State

`ROOT.md` deliberately does not maintain a detailed implementation inventory.

Before making claims about current behavior:

```text
inspect repository
inspect current-state documentation
inspect relevant Git state when required
inspect relevant tests
execute validation when the task requires it
```

Never use an old implementation summary in `ROOT.md` as proof that current behavior still exists.

---

# 22. Development and Validation

Code is not complete merely because it runs.

Use appropriate:

```text
unit tests
database tests
contract tests
integration tests
GUI tests
native Windows validation
security validation
regression tests
end-to-end tests
offline-behavior tests
```

depending on the change.

Never claim a test passed unless it actually ran and passed.

Use:

```text
PASS
FAIL
NOT RUN
BLOCKED
```

AI-generated code remains untrusted until reviewed and validated.

---

# 23. Scope Control

During focused work:

```text
solve the requested problem
preserve architectural boundaries
avoid unrelated refactoring
record unrelated improvements as follow-up work
```

Explicit review is required before major changes involving:

```text
destructive migrations
core database relationships
authentication/security boundaries
major framework changes
major dependency changes
repository restructuring
plugin architecture
IPC contracts
cross-language architecture
persistent background services
secret-management boundaries
external system-of-record ownership
```

---

# 24. Completion Principle

Before declaring substantial implementation complete, verify:

```text
requested behavior implemented
architecture preserved
database integrity preserved
security considered
offline behavior considered where applicable
tests actually executed
documentation synchronized
unrelated changes avoided
remaining risks identified
```

If something is unknown:

```text
say so
```

---

# 25. Final Principle

F7Hub should become more understandable after every development cycle.

> Build the correct system, not the most code.