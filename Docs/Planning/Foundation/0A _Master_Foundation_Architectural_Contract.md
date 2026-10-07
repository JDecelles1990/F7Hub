# F7Hub Phase 0A

## Cross-Subsystem Planning Note

Register DynamicHub as a subsystem; establish authoritative selected-ticket context as a shared application concept; define one authority per business concept; add evidence-flow boundaries; show DynamicHub ↔ Diagnostics ↔ Analytics ↔ Clipboard ↔ Mochi dependencies

# Master Foundation Architecture Planning Instructions
Current subsystem inventory; existing application/service/domain/repository/infrastructure boundaries; technology ownership matrix for Python/PySide6, AHK, PowerShell, SQLite and Mochi; dependency graph; permitted and prohibited dependency directions; existing cross-language infrastructure; trust/security boundaries; data-ownership matrix; application module map; architectural decision register; circular-dependency risks; canonical source-of-truth rules; explicit foundation handoff to 0B/0C/0D.

I want Codex to inspect existing:
taxonomy migration
categories
tags
tag repository
category repository
Knowledge Base tags/categories
Ticket categories
existing constraints
existing scopes

Then produce:
## Existing Taxonomy Reuse Matrix

Concept | Existing Mechanism | Used By | Reuse? | Required Change

The desired outcome is not necessarily “build Global Tags.”
It may instead be:
Existing tag system
        ↓
extend carefully
        ↓
becomes Global Tag Catalog


## Existing Foundation Components

For each potentially reusable foundation component:

Component:
Current responsibility:
Layer:
Consumers:
Dependencies:
Public API:
Tests:
Documentation:
Architectural fitness:
Recommendation:
  REUSE
  EXTEND
  REPLACE
  DEPRECATE
  NOT RELATED
  NOT VERIFIED


## Mode

`@ARCHITECT @PLAN`

Planning and architecture analysis only.

Do not implement features.

Do not create migrations.

Do not modify production code.

Do not perform unrelated refactoring.

Do not make irreversible architectural decisions silently.

---

# 1. Objective

Produce a comprehensive but implementation-neutral Master Foundation Architecture Plan for the next major F7Hub development cycle.

The purpose of this plan is to give future Codex sessions and feature plans a shared architectural model before implementation begins.

The plan must establish:

- subsystem boundaries
- responsibility ownership
- shared terminology
- cross-module relationships
- cross-language communication boundaries
- data ownership
- persistence ownership
- configuration ownership
- taxonomy responsibilities
- event and contract boundaries
- dependency order
- security boundaries
- testing boundaries
- implementation sequencing constraints

The plan must reduce the risk that future features:

- duplicate functionality
- create competing taxonomies
- create incompatible JSON schemas
- bypass service boundaries
- duplicate persistent data
- mix analytics with operational workflows
- allow AHK, PowerShell, Python, PySide6, Mochi, or SQLite to absorb responsibilities belonging to another subsystem

This is a foundation-planning exercise.

It is not an instruction to build the features.

---

# 2. Planned Feature Domains

The Master Plan must account for these upcoming areas:

1. Cross-language JSON / interoperability contracts
2. F7Hub Settings architecture
3. Global Tags and taxonomy
4. Entity classification and extraction
5. Clipboard Center
6. Diagnostic Engine
7. Diagnostic Center GUI
8. Statistical Analytics
9. Mochi Python Automation Assistant
10. Optional Mochi right sidebar
11. AHK integration
12. PowerShell integration
13. SQLite persistence
14. Cross-module search and relationships

These are related systems.

Do not plan them as isolated applications.

---

# 3. Existing Architecture Is Authoritative

Before proposing architecture:

```text
UNDERSTAND
    ↓
INSPECT
    ↓
MAP EXISTING CAPABILITIES
    ↓
IDENTIFY GAPS
    ↓
PLAN
```

Do not invent current project state.

For every relevant capability classify it as:

```text
FACT
ASSUMPTION
INFERENCE
RECOMMENDATION
NOT VERIFIED
```

When something has not been inspected, explicitly state:

```text
Not verified.
```

---

# 4. Mandatory Repository Inspection

Inspect relevant current F7Hub implementation and documentation before proposing new foundational components.

At minimum inspect relevant material covering:

```text
Project Vision
Project Requirements
Features
User Workflows
GUI
System Architecture
Database
ERD
SQL Schema
Folder Structure
AHK Architecture
PowerShell Architecture
Python Architecture
Roadmap
Todo
ChangeLog
```

Also inspect existing implementation for:

```text
Database migrations
Repositories
Application services
Domain models
Settings/configuration
Categories/taxonomy
Tags, if any
Ticket references
Knowledge Base relationships
PowerShell script registry
Diagnostic infrastructure
JSON result structures
FTS5/search
Application bootstrap
Event handling
Cross-language integration
```

Do not create a proposed subsystem until the repository has been searched for something that can be reused or extended.

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

---

# 5. Primary Architecture Principle

Preserve F7Hub's modular-monolith architecture.

Preferred application direction:

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

External integration layers may communicate with Application Services through explicit contracts.

Do not allow GUI components to become business-logic owners.

Do not allow AHK to become a database client.

Do not allow PowerShell to become a business-domain layer.

Do not allow Mochi to become a second system of record.

Do not allow Statistical Analytics to mutate operational data.

---

# 6. Technology Responsibilities

The Master Plan must explicitly define and preserve technology ownership.

## Python / PySide6

Primary responsibilities:

- main F7Hub application
- business/application orchestration
- parsing
- classification
- entity extraction
- data normalization
- analytics
- diagnostic orchestration
- context aggregation
- validation
- service layer
- GUI
- optional offline assistant behavior

## SQLite

Primary responsibilities:

- canonical relational persistence
- relationships
- integrity
- historical operational records
- FTS5 where justified
- analytical source data
- durable settings where appropriate

## AutoHotkey v2

Primary responsibilities:

- global hotkeys
- lightweight desktop interaction
- Windows clipboard triggers
- quick HUDs
- focused window context
- paste/injection actions
- launcher-like interaction

AHK must not directly modify F7Hub database state.

## PowerShell

Primary responsibilities:

- Windows administration
- Microsoft administration
- diagnostics
- system inspection
- approved automation
- structured evidence collection

PowerShell must not define F7Hub domain rules.

## Mochi

Primary responsibilities:

- context presentation
- explanations
- recommendations
- deterministic offline assistant output
- optional speech
- future AI-enhanced assistance

Mochi must consume approved F7Hub context through services/contracts.

Mochi must not independently bypass business or security boundaries.

## JSON

Primary responsibilities:

- language-neutral contracts
- structured IPC payloads
- diagnostic results
- automation results
- assistant context payloads

JSON is a communication format, not the system of record.

---

# 7. Required Conceptual Separation

The Master Plan must formally distinguish the following concepts.

## Category

Formal structured classification.

Example:

```text
Microsoft 365 → Outlook
```

## Type / Kind

Describes what a record fundamentally is.

Example:

```text
powershell_error
url
mixed_text
```

## Entity

A specific object/value discovered in content.

Example:

```text
10.0.0.87
john@contoso.com
PC-1042
0x80070005
```

## Tag

Flexible reusable concept associated with records across F7Hub.

Example:

```text
DNS
Outlook
Authentication
Networking
PowerShell
```

## Status

Workflow state.

Example:

```text
OPEN
RESOLVED
PUBLISHED
ARCHIVED
```

## Relationship

Explicit connection between records.

Example:

```text
Clipboard Item
    ↓ EVIDENCE_FOR
Ticket
```

## Metric

Calculated measurement.

Example:

```text
31 DNS-related tickets in the last 30 days
```

## Insight

Derived interpretation of metrics.

Example:

```text
DNS-related activity increased significantly this month.
```

These concepts must not be collapsed into one generic taxonomy mechanism.

---

# 8. Global Tag Architecture Principle

The Master Plan should evaluate a single global F7Hub Tag Catalog.

Target conceptual model:

```text
Global Tags
    │
    ├── Tickets
    ├── Knowledge Base
    ├── Clipboard
    ├── Diagnostics
    ├── Scripts
    ├── Automation
    └── Other eligible modules
```

The same canonical `DNS` tag should be reusable across modules.

The Master Plan must determine whether existing F7Hub taxonomy infrastructure can support or be extended for this purpose.

Do not automatically create a parallel taxonomy engine.

---

# 9. Entity Architecture Principle

Entities are different from Tags.

Example clipboard content:

```text
User: john@contoso.com
Device: PC-1042
IP: 10.0.0.87
Error: 0x80070005
```

Possible extracted entities:

```text
EMAIL
HOSTNAME
IPV4
ERROR_CODE
```

Possible tags:

```text
Networking
Windows
Troubleshooting
```

The Master Plan must define:

- ownership of entity taxonomy
- entity normalization
- source/provenance
- confidence
- offsets in source content
- optional metadata
- entity reuse across modules
- whether entities should be global concepts or module-owned records
- how entity values should relate to future structured F7Hub records such as devices, contacts, companies, tickets, or diagnostics

Do not assume every detected entity becomes a permanent business entity.

---

# 10. Cross-Language Contract Boundary

The Master Plan must reserve a dedicated follow-up architecture phase for the Global F7Hub JSON Contract.

Do not fully design the JSON contract during this Master Plan.

Instead identify:

- contract families required
- producers
- consumers
- trust boundaries
- validation points
- payload-size considerations
- versioning requirements
- error-handling needs
- asynchronous vs synchronous usage
- security requirements

Expected contract families may include:

```text
clipboard.capture
clipboard.process
clipboard.result

diagnostic.request
diagnostic.result

automation.request
automation.result

mochi.context
mochi.message

application.event
```

These are conceptual names only.

The detailed contract should be designed in Phase 0B after this Master Plan is approved.

---

# 11. Do Not Confuse Contract With Transport

The Master Plan must explicitly separate:

```text
CONTRACT
```

from:

```text
TRANSPORT
```

For example:

```text
JSON Contract
```

may later travel over:

```text
Named Pipe
localhost HTTP
local socket
process stdin/stdout
```

Transport decisions should not leak into domain models unnecessarily.

The Master Plan should identify which transport decisions must be made now and which can safely be deferred.

---

# 12. Settings Architecture

The Master Plan must identify Settings as shared infrastructure.

Expected future consumers include:

```text
Clipboard
Tags
Diagnostics
PowerShell
Automation
Analytics
Mochi
Appearance
Privacy
```

Plan responsibility boundaries for:

```text
Settings GUI
SettingsService
SettingsRepository
configuration defaults
validation
persistence
```

Determine conceptually which settings belong in:

```text
SQLite
```

versus configuration files or runtime configuration.

Do not design every individual setting yet.

---

# 13. Clipboard Domain Boundary

Clipboard Center should be treated as an operational module.

Conceptual responsibilities:

```text
capture
classification
entity extraction
normalization
sensitivity handling
deduplication
retention
search
pin/save
relationships
actions
```

Clipboard Center should answer:

```text
What information did I capture?
What does it contain?
What can I do with it?
```

Clipboard Center should not own historical statistical analysis.

---

# 14. Diagnostic Domain Boundary

Diagnostic Engine should transform technical context into structured technical evidence.

Conceptual model:

```text
DiagnosticSession
    ↓
DiagnosticExecution
    ├── Findings
    ├── Evidence
    └── Recommendations
```

The Master Plan must inspect existing F7Hub diagnostic and PowerShell infrastructure before proposing additions.

Diagnostics should initially favor:

```text
READ-ONLY
DETERMINISTIC
APPROVED
STRUCTURED
```

operations.

---

# 15. Statistical Analytics Boundary

Statistical Analytics is a read-oriented subsystem.

It should consume operational facts from modules such as:

```text
Tickets
Clipboard
Diagnostics
Knowledge Base
Tags
Automation
Scripts
Companies
Devices
```

Conceptual rule:

```text
Operational modules WRITE facts.

Analytics READS facts
and derives measurements.
```

Analytics should not become another source of operational truth.

Plan eventual layering:

```text
SQLite operational data
        ↓
SQLite views
        ↓
Python aggregation
        ↓
optional persisted aggregates
        ↓
Statistical Analytics GUI
```

---

# 16. Mochi Boundary

Mochi should sit above structured F7Hub context.

Conceptually:

```text
                 Mochi
                   │
             Context Service
                   │
        ┌──────────┼──────────┐
        │          │          │
    Clipboard  Diagnostics  Analytics
        │          │          │
      Tickets      KB        Tags
```

Mochi should not become:

- a second database owner
- an unrestricted PowerShell executor
- a direct SQLite client
- an independent ticket workflow engine
- an autonomous remediation engine

The Master Plan must distinguish:

```text
Mochi UI shell
```

from:

```text
Mochi assistant behavior
```

The right-sidebar shell may be planned earlier than advanced assistant functionality.

---

# 17. Data Ownership Matrix

The Master Plan must produce a data ownership matrix.

At minimum include:

| Data | Canonical Owner | Writers | Readers | Persistence |
|---|---|---|---|---|
| Clipboard item | TBD | TBD | TBD | TBD |
| Clipboard entity | TBD | TBD | TBD | TBD |
| Tag | TBD | TBD | TBD | TBD |
| Diagnostic session | TBD | TBD | TBD | TBD |
| Finding | TBD | TBD | TBD | TBD |
| Evidence | TBD | TBD | TBD | TBD |
| Recommendation | TBD | TBD | TBD | TBD |
| Metric | TBD | TBD | TBD | TBD |
| Mochi context | TBD | TBD | TBD | TBD |
| Settings | TBD | TBD | TBD | TBD |

Do not fill this from assumptions alone.

Ground it in inspected architecture and clearly mark recommendations.

---

# 18. Responsibility Matrix

Produce a matrix for:

```text
PySide6
Python Services
AHK
PowerShell
SQLite
JSON Contracts
Mochi
Statistical Analytics
```

For each major responsibility classify:

```text
OWNS
MAY USE
MUST NOT OWN
```

Example:

```text
SQLite Persistence

Python Repository Layer     OWNS ACCESS
SQLite                     OWNS DATA
PySide6                     MAY USE THROUGH SERVICES
AHK                         MUST NOT OWN
Mochi                       MUST NOT OWN
PowerShell                  MUST NOT OWN
```

---

# 19. Cross-Module Relationship Map

Produce a conceptual relationship map covering at least:

```text
Tickets
Companies
Contacts
Knowledge Base
Clipboard
Entities
Tags
Diagnostics
Scripts
Automation
Analytics
Mochi
```

Identify relationships such as:

```text
Clipboard → Ticket Evidence
Clipboard → Diagnostic Input
Diagnostic → Ticket
Diagnostic → KB
Script → Diagnostic
Tag → Clipboard
Tag → Ticket
Tag → KB
Tag → Diagnostic
Analytics → reads all eligible modules
Mochi → reads approved context
```

Do not create database schemas yet.

The purpose is to establish semantics.

---

# 20. Events and State Changes

Identify which future interactions are:

```text
COMMAND
EVENT
QUERY
```

Examples:

```text
COMMAND:
Run diagnostic.

EVENT:
Clipboard item captured.

QUERY:
Find KB articles tagged DNS.
```

This distinction should help prevent inappropriate coupling.

Do not implement an event bus unless inspection proves one is needed.

---

# 21. Security Boundaries

The Master Plan must explicitly identify trust boundaries.

Treat as untrusted:

```text
Clipboard content
AHK payloads
PowerShell output
URLs
Files
External APIs
User-entered text
AI output
Imported content
```

Define architectural safeguards for:

- schema validation
- payload size limits
- parameterized SQL
- command allowlists
- PowerShell script registry
- no arbitrary execution endpoint
- secret detection
- sensitive clipboard handling
- localhost IPC exposure
- auditability
- least privilege

No destructive action should be executed solely because clipboard or AI text requests it.

---

# 22. Privacy Boundaries

The Master Plan must identify privacy-sensitive data flows involving:

```text
Clipboard
Tickets
Contacts
Diagnostic evidence
Mochi
Analytics
```

Determine which systems:

- persist raw content
- persist normalized content
- persist only aggregates
- receive redacted context
- may receive AI context in the future
- must never receive secrets automatically

---

# 23. Analytics Vocabulary Must Be Stable

Before Statistical Analytics implementation, define the difference between:

```text
Raw Data
Event
Metric
Dimension
Insight
Recommendation
```

Example:

```text
Raw:
Get-Service Spooler

Event:
Clipboard captured at 14:31

Metric:
47 PowerShell commands captured this week

Insight:
PowerShell commands increased 18%

Recommendation:
Consider creating a reusable automation
```

The Master Plan should ensure that operational modules do not prematurely store derived insights as facts.

---

# 24. Shared Vocabulary Document

Produce a proposed glossary covering at least:

```text
Category
Type
Kind
Entity
Tag
Status
Priority
Relationship
Evidence
Finding
Recommendation
Diagnostic
Automation
Event
Command
Query
Metric
Dimension
Insight
Context
Contract
Payload
Transport
```

Every later architecture plan should reuse these meanings.

---

# 25. Dependency Graph

Produce a dependency graph for the planned systems.

Expected high-level direction should be evaluated against the repository:

```text
Existing F7Hub
      ↓
Shared Foundation Decisions
      ↓
JSON Contract
      ↓
Settings + Taxonomy
      ↓
Clipboard
      ↓
Diagnostics
      ↓
Analytics
      ↓
Mochi
```

Identify where dependencies may run in parallel.

Identify prohibited circular dependencies.

---

# 26. Prohibited Dependency Examples

Evaluate and explicitly guard against structures such as:

```text
ClipboardService
    ↓
MochiService
    ↓
ClipboardService
```

or:

```text
Analytics
    ↓ writes into
TicketRepository
```

or:

```text
AHK
    ↓
SQLite
```

or:

```text
PowerShell
    ↓
business workflow decisions
```

or:

```text
Mochi
    ↓
arbitrary PowerShell execution
```

---

# 27. Planning Depth Classification

For every architectural topic classify it as one of:

```text
DECIDE NOW
DESIGN NEXT
DEFER UNTIL FEATURE PLAN
DEFER UNTIL IMPLEMENTATION
```

Examples:

Potential `DECIDE NOW`:

```text
Module responsibility boundaries
Canonical data ownership
Tags vs Entities distinction
Analytics read-only rule
Mochi security boundary
```

Potential `DESIGN NEXT`:

```text
JSON Contract details
Entity taxonomy
Tag taxonomy
Settings persistence
```

Potential `DEFER`:

```text
Exact GUI pixel dimensions
Every diagnostic type
Every analytics KPI
Every classifier
Every Mochi phrase
```

This is important.

Do not over-design details whose requirements are not yet stable.

---

# 28. Required Master Plan Deliverables

Produce the following deliverables.

## A. Executive Architecture Summary

Explain the intended system in plain language.

## B. Verified Current-State Inventory

Show what already exists and what was inspected.

Use:

```text
FACT
NOT VERIFIED
```

appropriately.

## C. Proposed Domain Map

Show major F7Hub domains.

## D. Dependency Graph

Show foundational and feature dependencies.

## E. Data Ownership Matrix

Identify canonical owners.

## F. Technology Responsibility Matrix

Define Python, PySide6, SQLite, AHK, PowerShell, JSON, Analytics, and Mochi responsibilities.

## G. Classification Vocabulary

Define:

```text
Categories
Types
Entities
Tags
Statuses
Relationships
Metrics
```

## H. Cross-Module Relationship Map

Describe semantic relationships.

## I. Security / Trust Boundary Map

Identify untrusted data and execution boundaries.

## J. Configuration Ownership Model

Describe Settings responsibilities.

## K. Contract Inventory

List required JSON contract families without designing their full schemas.

## L. Decision Register

For every major choice include:

```text
Decision
Reason
Alternatives considered
Consequences
Status
```

Use statuses:

```text
PROPOSED
RECOMMENDED
REQUIRES USER DECISION
DEFERRED
```

## M. Open Questions

Only include questions that materially affect architecture.

Do not ask questions whose answer can be obtained by repository inspection.

## N. Risk Register

Identify:

```text
duplication risk
coupling risk
migration risk
security risk
privacy risk
performance risk
schema-growth risk
taxonomy drift
contract drift
analytics inconsistency
```

## O. Recommended Planning Sequence

Recommend the order of the next detailed planning exercises.

---

# 29. Expected Next Planning Sequence

The Master Plan should evaluate this proposed sequence:

```text
Phase 0A
Master Foundation Architecture

Phase 0B
Global JSON / Interoperability Contract

Phase 0C
Classification & Taxonomy Architecture
- Categories
- Types / Kinds
- Entities
- Tags
- Relationships

Phase 0D
Settings Architecture

Phase 1
Clipboard Architecture

Phase 2
Diagnostic Architecture

Phase 3
Statistical Analytics Architecture

Phase 4
Mochi Context & Assistant Architecture
```

Do not treat these phase numbers as implementation slice numbers.

They are architecture/planning phases.

---

# 30. No Implementation Slices Yet

The Master Plan may identify probable future implementation slices.

However, do not create detailed implementation slice instructions until the corresponding architecture plan is approved.

Use:

```text
MASTER ARCHITECTURE
        ↓
DETAILED DOMAIN PLAN
        ↓
IMPLEMENTATION SLICES
```

not:

```text
MASTER ARCHITECTURE
        ↓
100 files changed at once
```

---

# 31. Architecture Decision Gates

Identify decisions that require explicit review before proceeding.

At minimum flag:

- new global taxonomy architecture
- new IPC transport
- major settings persistence design
- new cross-module foreign-key patterns
- major diagnostic execution boundary
- new background service
- new authentication/security mechanism
- destructive migrations
- plugin architecture changes
- major repository restructuring
- new cross-language dependency direction

---

# 32. Documentation Impact Plan

Identify which existing documentation will eventually require synchronization.

Examples:

```text
GUI changes
→ GUI + System Architecture docs

Database changes
→ Database + ERD + SQL Schema docs

Python architecture changes
→ Python Architecture

AHK integration
→ AHK Architecture

PowerShell contracts
→ PowerShell Architecture

Major feature sequencing
→ Roadmap + Todo + ChangeLog
```

Do not update documentation during this planning task unless explicitly requested.

Only identify expected impact.

---

# 33. Testing Strategy at Architecture Level

Do not write detailed tests yet.

Define required future validation categories:

```text
unit
repository
database migration
contract/schema
integration
cross-language
GUI
security
privacy
regression
native Windows
performance
retention/cleanup
analytics correctness
```

Map test categories to future domains.

---

# 34. Performance Considerations

Identify likely performance-sensitive areas:

```text
clipboard capture frequency
large clipboard payloads
FTS indexing
entity extraction
tagging rules
diagnostic subprocess execution
analytics aggregation
large historical datasets
GUI filtering
Mochi context assembly
```

Do not prematurely optimize.

Identify where measurement will be required.

---

# 35. Acceptance Criteria

The Master Foundation Architecture Plan is acceptable when:

1. Existing relevant architecture has been inspected.
2. Existing reusable capabilities have been identified.
3. No project state has been invented.
4. Major domains have explicit responsibilities.
5. Canonical data ownership is clear.
6. Tags, Entities, Categories, Types, and Statuses are clearly distinguished.
7. Analytics is separated from operational ownership.
8. Mochi's boundary is explicit.
9. AHK and PowerShell responsibilities are constrained.
10. Required JSON contract families are identified.
11. Settings dependencies are identified.
12. Cross-module relationships are mapped.
13. Security and privacy boundaries are documented.
14. Dependency direction is clear.
15. Circular dependencies are identified and prevented.
16. Decisions that require user review are flagged.
17. Deferred decisions are explicitly documented.
18. The next architecture-planning sequence is clear.
19. No implementation is performed.
20. F7Hub is easier to reason about after the plan than before it.

---

# 36. Validation

Before declaring the plan complete:

```text
Architecture inspection       PASS / FAIL / BLOCKED
Existing capability mapping   PASS / FAIL / BLOCKED
Dependency analysis           PASS / FAIL / BLOCKED
Data ownership analysis       PASS / FAIL / BLOCKED
Security review               PASS / FAIL / BLOCKED
Taxonomy boundary review      PASS / FAIL / BLOCKED
Contract inventory            PASS / FAIL / BLOCKED
Scope control                 PASS / FAIL / BLOCKED
Implementation changes        MUST BE NONE
```

---

# 37. Final Report Format

Return:

## Summary

What was inspected and the recommended architecture direction.

## Current-State Findings

Verified existing capabilities relevant to the plan.

## Domain Map

Major subsystem boundaries.

## Dependency Map

Direction of dependencies.

## Data Ownership

Canonical ownership matrix.

## Classification Model

Categories vs Types vs Entities vs Tags vs Statuses vs Relationships.

## Communication Boundaries

Required contract families and producers/consumers.

## Settings Architecture

Shared configuration responsibility.

## Security & Privacy

Trust and execution boundaries.

## Decision Register

Recommended, deferred, and user-review decisions.

## Risks

Architectural risks and mitigations.

## Recommended Planning Sequence

Exact recommended order for subsequent detailed architecture plans.

## Result

Use one:

```text
READY_FOR_FOUNDATION_DESIGN
BLOCKED
REQUIRES_ARCHITECTURE_DECISIONS
```

Do not return `READY_FOR_IMPLEMENTATION`.

This Phase 0 task is intentionally upstream of implementation.

# Cross-subsystem context and evidence map
Ticket Workspace
      │
      │ authoritative ticket selection
      ▼
Application Context
      │
      ├──────────────► DynamicHub
      │                    │
      │                    ├── actions
      │                    ├── observations
      │                    └── workflow state
      │
      ├──────────────► Diagnostics
      │                    │
      │                    └── structured results
      │
      ├──────────────► Clipboard
      │                    │
      │                    └── optional technician input
      │
      └──────────────► Mochi
                           │
                           └── advisory context

Actions + Results + Observations
              │
              ▼
        Evidence Model
              │
              ├── Case Notes
              ├── Closure
              └── Analytics

F7Hub owns ticket identity.
Diagnostics own diagnostic execution.
DynamicHub owns interactive workflow presentation.
Analytics owns derived measurement.
Clipboard owns clipboard lifecycle.
Mochi owns advisory pet interaction.

None of them become alternative ticket authorities.

---

## Additional Mandatory Cross-Cutting Architecture Questions

During repository inspection, determine whether F7Hub requires shared
architectural concepts for the following.

Do not assume that each item requires a new service, table, registry,
module or abstraction.

For each item:

1. search for existing implementation;
2. identify current ownership;
3. classify as REUSE / EXTEND / NEW / FEATURE-OWNED / NOT NEEDED /
   NOT VERIFIED;
4. identify the appropriate architectural layer;
5. identify downstream Foundation impact.

Evaluate:

- Technician Workspace
- Active Technician Context
- Case Journal / Case Activity
- offline Case Note generation
- Evidence
- Attachments / binary content
- Audit / Application Events
- Approved Actions / Remediation
- Background Jobs
- External Systems of Record
- Integration Gateway / Adapter boundaries
- Integration Capability / Permission model
- Credential Broker boundary
- Synchronization Outbox
- Remote Identity Mapping
- Connectivity state
- Privacy / redaction
- provenance of externally sourced information

### Offline-First Requirement

Determine which architectural capabilities must be:

- LOCAL_REQUIRED
- ONLINE_OPTIONAL
- ONLINE_REQUIRED

F7Hub must support core local technician workflows without requiring an
external API or AI provider.

In particular, Case Journal storage, Case Note draft creation and Case
Note editing must remain possible offline.

External synchronization may be unavailable while those local workflows
continue.

### Vendor-Neutral Integration Requirement

Foundation architecture must allow future employer-approved APIs without
making any current vendor mandatory.

Potential providers may include PSA, RMM, Microsoft administration,
credential-management and AI systems.

Do not design Foundation architecture around a specific vendor unless
the current repository already contains an approved vendor-specific
integration.

Vendor-specific behavior should normally terminate at an integration
gateway or adapter boundary.

### External System-of-Record Boundary

Determine how F7Hub distinguishes:

- local working state;
- locally generated drafts;
- synchronized external state;
- authoritative external records.

Example architectural question:

F7Hub may own a local Case Journal and offline Case Note draft while a
future PSA owns the official published ticket note.

The specific PSA must remain replaceable.

### Sensitive Information and Secrets

Determine trust and data-handling boundaries without requiring real
employer or customer information.

Planning examples and test data must be synthetic.

Secrets must not become ordinary domain data, taxonomy data, application
settings, logs, analytics input or assistant context.

Any future credential integration must have a clearly defined security
boundary and least-privilege model.