# AGENTS.md

## Scope

This file applies to:

```text
Docs/Planning/Foundation/
```

and all descendant files unless a more-specific `AGENTS.md` exists.

This guidance governs the Foundation architecture planning sequence:

```text
0A
0B
0C
0D
0E
```

It supplements broader repository and Planning guidance.

---

## Instruction Chain

This file supplements:

- [Repository AGENTS.md](../../../AGENTS.md)
- [Planning AGENTS.md](../AGENTS.md)

All applicable instructions remain in force.

For files under `Docs/Planning/Foundation/`, this Foundation guidance adds
more-specific rules but does not replace repository-wide safety,
architecture, security or documentation requirements.

---

# Purpose

The Foundation planning documents establish the shared architectural rules that future F7Hub features must consume.

Foundation planning exists to answer cross-cutting questions before individual features create incompatible solutions.

The Foundation must establish enough architecture that future feature planning can reuse shared rules for:

```text
ownership
dependency direction
interoperability
taxonomy
settings
security
offline behavior
integration boundaries
external systems
synchronization
provenance
capabilities
shared context
evidence
```

The Foundation does not implement product features.

The Foundation must not attempt to predict every future class, table, Tag, Entity Type, workflow, API, provider or GUI screen.

---

# Primary Foundation Principle

The Foundation defines:

```text
HOW F7Hub grows
```

not:

```text
EVERYTHING F7Hub will ever contain
```

Prefer stable architectural rules and controlled extension mechanisms over exhaustive speculative design.

---

# Foundation Phases

The Foundation architecture sequence is:

```text
0A  Master Foundation Architecture
0B  Global JSON / Interoperability Contract
0C  Taxonomy / Information Vocabulary
0D  Settings / Configuration Architecture
0E  Foundation Architecture Reconciliation
```

Each phase owns a distinct architectural concern.

---

# 0A Authority

0A owns cross-cutting architectural responsibility and system boundaries.

0A answers:

> Who owns what?

Primary concerns include:

```text
subsystem ownership
layer ownership
technology responsibilities
dependency direction
application/service/domain/repository boundaries
infrastructure boundaries
database responsibility
GUI responsibility
AutoHotkey responsibility
PowerShell responsibility
Python responsibility
Mochi responsibility
trust boundaries
security boundaries
integration ownership
external-system boundaries
offline/local responsibility
background-work ownership
shared-context ownership
```

0A may identify shared architectural primitives.

0A must not create them simply because they appear useful.

Before introducing a shared primitive:

```text
SEARCH
→ IDENTIFY
→ REUSE / EXTEND
→ CREATE ONLY IF NECESSARY
```

---

# 0B Authority

0B owns interoperability and machine-readable communication rules.

0B answers:

> How do F7Hub components communicate?

Primary concerns include:

```text
message envelopes
commands
queries
events
results
errors
serialization
versioning
correlation
causation where justified
idempotency
timeouts
cancellation
retry semantics
cross-language communication
validation boundaries
operation identity
```

0B must distinguish:

```text
WHAT information means
```

from:

```text
HOW information is transported
```

0B must not redefine domain semantics owned by 0C.

0B must not redefine subsystem ownership established by 0A.

---

# 0C Authority

0C owns F7Hub information vocabulary and taxonomy semantics.

0C answers:

> What does information mean?

Primary concepts include:

```text
Category
Type
Kind
Entity
Entity Type
Tag
Tag Family
Status
Priority
Relationship
Provenance
Confidence
Normalization
Alias
Scope
```

0C must establish stable meaning and extension rules.

0C must not require every future:

```text
Tag
Entity Type
Category
Relationship Type
```

to be known before feature implementation begins.

Prefer:

```text
stable vocabulary framework
+
initial CORE vocabulary
+
controlled extension process
```

over an exhaustive speculative dictionary.

---

# 0D Authority

0D owns Settings and configuration architecture.

0D answers:

> What can be configured, where does it live, and how is its effective value determined?

Primary concerns include:

```text
setting definitions
stored values
defaults
overrides
precedence
effective values
validation
scope
runtime changes
restart requirements
module configuration
integration configuration
privacy-related configuration
configuration persistence
secret references
```

0D must distinguish:

```text
SETTING
```

from:

```text
DOMAIN DATA
REFERENCE DATA
REGISTRY
CATALOG
SECURITY INVARIANT
SECRET
DISCOVERED CAPABILITY
```

0D must not turn unrelated domain concepts into generic Settings.

---

# 0E Authority

0E owns Foundation reconciliation.

0E answers:

> Do 0A, 0B, 0C and 0D form one coherent architecture?

0E may:

```text
cross-reference
compare
identify conflicts
identify duplication
identify missing architecture
record authority ownership
record terminology alignment
record downstream assumptions
evaluate feature-planning readiness
```

0E must not become a second copy of 0A-0D.

0E must not replace the authority of 0A-0D.

0E must link to the authoritative Foundation documents rather than concatenating their contents.

---

# Required Execution Order

The normal execution order is:

```text
0A
 ↓
Review
 ↓
Approval

0B
 ↓
Review
 ↓
Approval

0C
 ↓
Review
 ↓
Approval

0D
 ↓
Review
 ↓
Approval

0E
 ↓
Reconciliation Review
 ↓
Foundation Ready for Feature Planning
```

A downstream phase may be pre-written before its dependencies are approved.

It must not be executed as authoritative architecture until required upstream dependencies are sufficiently resolved.

---

# Dependency Rule

A downstream Foundation phase may:

```text
consume
reference
clarify
extend within its own authority
```

approved upstream architecture.

It may not silently:

```text
override
rename
reinterpret
duplicate
replace
```

an upstream decision.

If a conflict is discovered:

```text
STOP
IDENTIFY OWNING PHASE
RECORD CONFLICT
RETURN REQUIRES_DECISION OR BLOCKED
```

Do not patch around Foundation conflicts inside a downstream phase.

---

# Approval Authority

Codex may conclude that a Foundation phase is:

```text
READY_FOR_REVIEW
REQUIRES_DECISION
BLOCKED
```

or another exact phase-specific result token defined by the planning document.

Codex must not independently mark a Foundation phase:

```text
APPROVED
```

unless explicitly instructed to record an approval that has already occurred.

Architecture approval requires explicit review.

---

# Repository Inspection Requirement

F7Hub is not greenfield.

Before making significant architectural recommendations, inspect relevant implementation and documentation.

Potential evidence includes:

```text
source code
domain models
services
repositories
gateways
database migrations
SQLite schema
configuration
tests
canonical documentation
current-state documentation
existing protocols
existing JSON/result structures
existing taxonomy
existing integration code
```

Do not invent project state.

If something was not inspected, say:

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

## FACT

Directly supported by inspected repository evidence.

## ASSUMPTION

A temporary premise required for planning but not yet verified.

## INFERENCE

A reasonable conclusion derived from inspected evidence but not explicitly stated.

## RECOMMENDATION

A proposed architectural choice.

## NOT VERIFIED

A relevant area that was not sufficiently inspected.

Do not convert recommendations or assumptions into facts through repetition.

---

# Reuse First

Before proposing a new:

```text
table
migration
class
service
repository
gateway
protocol
JSON envelope
taxonomy system
Tag system
Entity system
Settings provider
configuration store
event system
workspace host
job system
integration abstraction
credential mechanism
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

Relevant existing architecture should be classified as:

```text
REUSE
EXTEND
REPLACE
DEPRECATE
NOT RELATED
NOT VERIFIED
```

Replacement requires architectural justification.

---

# Existing Architecture of Interest

Foundation planning should inspect relevant existing components before proposing replacements.

Examples may include:

```text
altf7hub_gateway
altf7hub_service

mochi_channel
mochi_gateway
mochi_service
mochi_protocol

powershell_gateway
powershell_service

diagnostic_results

category_repository
tag_repository

existing database migrations
existing configuration mechanisms
existing GUI workspace patterns
existing application services
existing integration tests
```

This list is illustrative.

Repository inspection remains authoritative.

---

# Architecture Layering

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

Do not move business logic into GUI code for convenience.

Do not place SQL directly in GUI widgets.

Do not allow AutoHotkey to become the primary business or persistence layer.

Do not allow PowerShell to become general application orchestration.

Do not allow Mochi to bypass application-service boundaries.

Do not allow external integrations to write directly into unrelated domain structures.

---

# Technology Responsibilities

Unless repository evidence and approved architecture establish otherwise:

## AutoHotkey v2

Primary responsibility:

```text
Windows interaction
hotkeys
desktop automation
lightweight HUDs
clipboard integration
window interaction
launching
```

## Python / PySide6

Primary responsibility:

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

Primary responsibility:

```text
Windows administration
Microsoft administration
diagnostics
approved remediation
technical collection
reporting
```

## SQLite

Primary responsibility:

```text
durable relational state
data integrity
relationships
search indexes
persistence
```

## Mochi

Primary responsibility:

```text
presentation
contextual assistance
approved interaction
communication
```

Mochi must not become an unrestricted execution, secret-storage or database-access layer.

---

# Mandatory Cross-Cutting Investigation

0A must investigate whether F7Hub requires shared architectural concepts for the following.

Do not assume that each item requires a new service, table, registry or subsystem.

For each:

1. search existing implementation;
2. determine whether something equivalent already exists;
3. identify current owner;
4. classify the concept;
5. identify downstream Foundation dependencies.

Evaluate:

```text
Technician Workspace
Active Technician Context
Case Journal / Case Activity
Offline Case Note Generation
Evidence
Attachments / Binary Content
Audit / Application Events
Approved Actions / Remediation
Background Jobs
External Systems of Record
Integration Gateway / Adapter boundaries
Integration Capability / Permission model
Credential Broker boundary
Synchronization Outbox
Remote Identity Mapping
Connectivity State
Privacy / Redaction
Provenance of external information
```

Possible classifications include:

```text
SHARED FOUNDATION CONCEPT
FEATURE-OWNED CONCEPT
EXISTING CAPABILITY TO REUSE
EXTENSION OF EXISTING CAPABILITY
NOT NEEDED
NOT VERIFIED
```

---

# Technician Workspace Boundary

Foundation planning must investigate whether F7Hub requires a first-class:

```text
Technician Workspace
```

and:

```text
Active Technician Context
```

These are separate concepts.

The Technician Workspace may potentially own:

```text
tool hosting
navigation
activation
layout
internal tabs
split views
restoration
context propagation
workspace lifecycle
```

It must not automatically become the owner of:

```text
Ticket business logic
Clipboard business logic
Diagnostic execution
Knowledge persistence
PowerShell execution
Analytics calculations
Mochi reasoning
```

Embedded tools should continue to use the application services of their owning modules.

Do not commit to a specific Qt implementation such as `QMdiArea` unless later GUI architecture justifies it.

---

# Active Technician Context

Foundation planning should investigate how F7Hub may represent the technician's current working context.

Potential contextual concepts may include:

```text
Company
User
Device
Ticket
Tenant
Diagnostic Session
Clipboard evidence
Knowledge Article
```

Do not assume all context values exist or must be persisted.

Context propagation must not create circular dependencies between modules.

---

# Offline-First Architecture

Offline behavior is a Foundation priority.

F7Hub must remain useful without:

```text
internet connectivity
external PSA
external RMM
external AI
credential-management API
Microsoft cloud API
other remote integration
```

where the capability is classified as locally required.

Foundation and feature architecture should classify workflows as:

```text
LOCAL_REQUIRED
ONLINE_OPTIONAL
ONLINE_REQUIRED
```

Examples expected to be evaluated include:

```text
Case Journal storage
Case Note draft generation
Case Note editing
Clipboard access
local Knowledge Base
local Diagnostics
external ticket synchronization
remote device information
external AI enhancement
```

Do not finalize a classification without phase-specific architectural review.

---

# Offline Case Note Requirement

Case Journal and Case Note architecture must support offline operation.

At minimum, Foundation planning must preserve the possibility that:

```text
Case Journal
        ↓
Local structured activities
        ↓
Local deterministic note generation
        ↓
Editable draft
```

works without:

```text
external PSA
cloud AI
internet access
```

External AI may enhance or rewrite a note later.

It must not become a required dependency for core Case Note generation.

---

# External Systems of Record

Foundation planning must distinguish:

```text
local working state
local drafts
locally generated evidence
synchronized external state
authoritative external records
```

A future external PSA may own the official published ticket note while F7Hub owns:

```text
working journal
structured case activities
draft notes
synchronization metadata
```

Do not assume a specific PSA provider.

The architecture must allow provider replacement.

---

# Vendor-Neutral Integration Architecture

Future employers may use different combinations of:

```text
PSA
RMM
password manager
Microsoft administration tooling
AI provider
monitoring platform
security platform
documentation platform
other APIs
```

Foundation architecture must not require a specific vendor unless the repository already contains an approved vendor-specific integration.

Potential providers such as:

```text
HaloPSA
NinjaOne
CIPP
Keeper
Microsoft Graph
company AI
```

are examples, not Foundation requirements.

Prefer:

```text
F7Hub Domain
      ↓
Application Service
      ↓
Integration Gateway / Adapter
      ↓
Provider
```

Vendor-specific DTOs should normally terminate at the integration boundary.

Do not allow vendor-specific payloads to become the global F7Hub domain model.

---

# Integration Capability Model

Foundation planning should preserve the possibility that integrations expose capabilities dynamically.

Examples might include:

```text
READ_TICKET
WRITE_TICKET_NOTE
CHANGE_TICKET_STATUS
READ_DEVICE
READ_ALERTS
RUN_APPROVED_AUTOMATION
READ_TENANT
USE_CREDENTIAL
AI_SUMMARIZE
AI_CLASSIFY
```

Do not finalize this vocabulary prematurely.

A configured integration does not imply every possible capability is available.

Capability availability may depend on:

```text
provider
permissions
license
tenant configuration
runtime state
connectivity
```

Discovered capabilities are not ordinary user preferences.

---

# Synchronization and Outbox Architecture

Foundation planning must consider future delayed synchronization.

Potentially queueable operations may include:

```text
ticket note publication
evidence metadata upload
non-destructive synchronization
```

Potentially unsafe delayed operations may include:

```text
restart device
disable account
reset password
terminate process
run remediation
```

Do not assume technical actions are safe to replay later.

State-changing actions should normally require:

```text
fresh context
current authorization
appropriate confirmation
```

Synchronization architecture must consider:

```text
operation identity
correlation
idempotency
duplicate prevention
remote confirmation
retryability
stale-state detection
conflict detection
```

---

# Retry and Loop Safety

All retrying operations must be bounded.

Every retry mechanism should define:

```text
trigger
maximum retry count
maximum elapsed time
success condition
failure condition
```

If the same validation, native test, integration test or screenshot check fails twice with:

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

Do not enter unbounded:

```text
retries
polling
relaunches
screenshots
focus attempts
IPC reconnect loops
review loops
```

---

# Employer and Customer Data Boundary

Foundation planning must be safe without requiring real employer or customer operational data.

Architecture documentation, tests and examples should use synthetic data wherever possible.

Do not require production data to prove architectural concepts.

Examples of safe synthetic values include:

```text
Contoso Ltd.
Jane Technician
USER-001
PC-042
INC-1001
example.com
192.0.2.10
```

Runtime processing of employer-authorized operational data is separate from committing that data into the F7Hub repository.

Do not intentionally place real employer/customer data into:

```text
source code
planning documentation
canonical documentation examples
Git history
test fixtures
seed data
screenshots committed to the repository
sample JSON
AI prompt fixtures
```

unless explicitly authorized and necessary.

---

# Secrets Boundary

Secrets are not ordinary F7Hub domain data.

Examples include:

```text
passwords
API keys
access tokens
refresh tokens
private keys
session cookies
recovery codes
authentication secrets
```

Secrets must not normally be stored in:

```text
SQLite application tables
ordinary Settings
Clipboard history
Case Journal
Analytics
Mochi context
documentation
test fixtures
normal logs
diagnostic evidence
```

Future credential integrations should prefer:

```text
secure reference
transient retrieval
least privilege
use without unnecessary reveal
explicit authorization
```

F7Hub must not become an accidental password manager.

---

# Sensitive Information

Not all sensitive information is a secret.

Foundation planning must distinguish credentials from potentially sensitive operational information.

Potentially sensitive information may include:

```text
customer names
user identities
device names
tenant identifiers
ticket contents
email addresses
network details
diagnostic evidence
URLs
window titles
logs
screenshots
```

Handling rules must be based on:

```text
data minimization
purpose limitation
least persistence
approved employer policy when known
```

Do not invent employer-specific classification policy.

If policy is unknown:

```text
minimize collection
minimize persistence
avoid unnecessary external transmission
record NOT VERIFIED where appropriate
```

---

# Privacy and Redaction

Foundation planning should preserve architecture for:

```text
sensitivity detection
redaction
controlled external transmission
AI context filtering
log filtering
evidence handling
```

Raw sensitive information should not automatically enter normal application logs.

External AI integration must remain optional.

Information sent to any AI provider must follow approved privacy and authorization rules.

---

# Internal Contract vs External Vendor Contract

The F7Hub interoperability contract is an internal architectural contract.

Do not treat external vendor JSON as F7Hub's internal model.

Preferred boundary:

```text
External API
   ↓
Provider Gateway / Adapter
   ↓
Validated Provider DTO
   ↓
F7Hub Application / Domain Representation
```

Provider-specific fields should not leak unnecessarily into:

```text
GUI
SQLite schema
taxonomy
diagnostic domain
case journal
unrelated services
```

---

# JSON and Interoperability Safety

Cross-boundary communication must be validated.

Conceptual processing:

```text
Receive
 ↓
Parse
 ↓
Validate envelope
 ↓
Validate version
 ↓
Validate operation
 ↓
Validate payload
 ↓
Check capability / authorization
 ↓
Convert to application/domain object
 ↓
Application Service
```

Do not expose unrestricted operations such as:

```text
run_any_command
```

Use approved operations with validated parameters.

Do not put secrets into:

```text
normal JSON examples
logs
error details
correlation metadata
test fixtures
```

---

# Taxonomy Extensibility

0C must make vocabulary extension normal and controlled.

Adding a new approved entry through the existing extension mechanism should not automatically require Foundation redesign.

Example normal extension:

```text
new Tag
new Entity Type
new module-specific vocabulary entry
```

Potential Foundation change:

```text
changing what Tag means
changing Entity identity
creating a second taxonomy system
changing provenance semantics
changing taxonomy ownership
```

The latter requires architecture review.

---

# Sensitive Values Are Not Tags

Do not use Tags to store arbitrary sensitive or identity-bearing values.

Do not treat:

```text
password
access token
customer secret
credential
private free-form value
```

as Tags.

Concrete detected values such as:

```text
IP address
email address
hostname
GUID
ticket ID
device identifier
```

should follow Entity/reference-data semantics where applicable rather than being converted to flexible Tags for convenience.

---

# Provenance

Foundation architecture should preserve the ability to identify where information originated.

Possible provenance classes may include:

```text
technician input
local rule/parser
F7Hub subsystem
import
external integration
AI suggestion
resolver
```

Do not finalize the taxonomy before 0C review.

Adding a new external provider must not require redesigning provenance semantics.

---

# Settings and Secrets

Secrets are not normal settings.

A Setting may potentially hold:

```text
secure reference
provider identifier
feature preference
timeout
display preference
integration enablement
```

but the secret itself belongs to the approved secret-management boundary.

---

# Capabilities Are Not Settings

A discovered provider capability is not equivalent to a user preference.

Example:

```text
Provider supports WRITE_TICKET_NOTE
= discovered capability

Preferred Case Note formatting
= setting
```

Do not allow a Settings toggle to claim a capability that the underlying integration does not possess.

---

# Safety Invariants Are Not Settings

Hard security invariants must not become casual Settings.

Examples include:

```text
do not log credentials
do not persist secrets in Clipboard history
do not send secrets to Mochi
do not automatically replay stale destructive actions
do not bypass required authorization
```

A preference must not override a Foundation safety invariant.

---

# Database Planning

SQLite remains foundational.

Any future database architecture must consider:

```text
normalization
primary keys
foreign keys
constraints
indexes
transactions
migrations
views
FTS5 where appropriate
query performance
data integrity
retention
audit requirements
```

Do not create migrations during Foundation planning unless explicitly authorized.

Do not silently duplicate existing tables or registries.

Do not use JSON columns merely to avoid designing stable relational structures when stable queryable data is warranted.

---

# Foundation Planning Is Read-Only for Production

Unless explicitly authorized, 0A-0E planning must not modify:

```text
Python/
AutoHotkey/
PowerShell/
Database/
Config/
Tests/
Mochi/
```

Do not create production:

```text
code
migrations
dependencies
services
endpoints
runtime configuration
```

during Foundation planning.

---

# Allowed Writes

Normal Foundation-planning writes are limited to:

```text
Docs/Planning/Foundation/
```

When explicitly required, also allow:

```text
Docs/Planning/README.md
```

for:

```text
status
index
relative links
phase tracking
```

Do not modify canonical numbered documentation during Foundation planning unless explicitly authorized.

---

# Preserve Planning Contracts

Each Foundation Markdown file may contain:

```text
planning instructions
execution report
decision register
risk register
review record
approval record
change history
```

When executing a phase:

1. preserve the planning instructions;
2. inspect the required repository evidence;
3. populate the Execution Report;
4. record actual findings;
5. record unresolved decisions;
6. record assumptions;
7. record `NOT VERIFIED` items;
8. record risks;
9. record downstream contracts;
10. preserve review history.

Do not erase the original planning contract after execution.

---

# Decision Register

Significant architectural decisions should record:

```text
Decision
Options considered
Evidence
Recommendation
Rationale
Consequences
Status
```

Possible statuses include:

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

# Decisions Requiring Explicit Review

Explicit review is required before recommending implementation of major changes involving:

```text
destructive migrations
core database relationships
authentication boundaries
security boundaries
major dependency changes
major framework changes
repository restructuring
plugin architecture
IPC redesign
cross-language architecture changes
persistent background services
secret-management boundaries
external-system ownership changes
```

---

# Canonical Documentation Is Living Documentation

The numbered files under:

```text
Docs/
```

describe the current approved F7Hub architecture, behavior and requirements.

They are living documentation.

They are not immutable historical snapshots.

When approved implementation changes current behavior, update the relevant canonical documentation.

Examples:

```text
GUI change
→ 05_GUI.md
→ 06_SystemArchitecture.md where appropriate

Database change
→ 07_Database.md
→ 08_ERD.md
→ 09_SQLSchema.md

AHK change
→ 11_AHKArchitecture.md

PowerShell change
→ 12_PowerShellArchitecture.md

Python change
→ 13_PythonArchitecture.md

Feature/workflow change
→ relevant Feature / Workflow documentation
```

Historical records belong primarily in:

```text
18_ChangeLog.md
Git history
review records
integration records
archived or superseded planning artifacts
```

Do not preserve obsolete current-state documentation merely to retain history.

Do not rewrite historical records to make later architecture appear as though it always existed.

---

# Canonical Documentation During Foundation Planning

During 0A-0E:

```text
Canonical Docs
= evidence input

Planning Docs
= architecture output
```

After architecture is approved and implementation changes current state:

```text
Approved implementation
        ↓
Relevant canonical Docs
```

Do not automatically add backlinks to all canonical documentation.

Only relevant documentation should be synchronized.

---

# Cross-Document Links

Foundation files should use relative Markdown links to related Foundation documents when useful.

Prefer:

```text
link to owning document
```

over:

```text
copying the same architecture into multiple files
```

Avoid circular duplicated architecture.

---

# 0E Reconciliation Requirements

0E must reconcile the approved Foundation architecture.

It should include, where supported by actual findings:

```text
Foundation source links
architecture authority matrix
dependency reconciliation
responsibility reconciliation
interoperability reconciliation
taxonomy reconciliation
settings reconciliation
persistence reconciliation
security reconciliation
offline-behavior reconciliation
integration-boundary reconciliation
terminology matrix
existing architecture reuse matrix
cross-document conflict register
duplicate-concept register
missing-architecture register
downstream Foundation contract
feature-planning readiness
risk register
validation
final result
```

0E must not concatenate 0A-0D.

---

# Foundation Readiness

0E should determine whether future feature architecture can proceed without independently inventing shared infrastructure.

Evaluate whether the Foundation provides sufficient guidance for:

```text
ownership
communication
taxonomy
settings
security
offline behavior
integration boundaries
external-system ownership
synchronization
capabilities
shared context
evidence
provenance
```

The Foundation does not need complete implementation designs for these.

It needs enough architectural ownership and rules that downstream features know where their decisions belong.

---

# Downstream Feature Rule

Once 0E passes, feature architecture may rely on the reconciled Foundation contract.

Future feature planning should not independently reinvent:

```text
layer ownership
interoperability grammar
taxonomy semantics
Settings architecture
secret handling
offline principles
integration boundaries
system-of-record rules
security boundaries
```

If a feature discovers a genuine Foundation gap:

```text
RECORD GAP
IDENTIFY FOUNDATION OWNER
REQUEST FOUNDATION REVIEW IF REQUIRED
```

Do not create parallel infrastructure locally.

---

# Feature Extension vs Foundation Change

Normal feature extension may include:

```text
adding a Tag
adding an Entity Type
adding a setting
adding a registered diagnostic
adding a provider adapter
adding a Workspace tool
```

when performed through an approved extension mechanism.

Foundation review is required when changing:

```text
what a Tag means
what an Entity means
global JSON semantics
layer ownership
Settings ownership
security invariants
secret handling
offline guarantees
integration boundaries
external-system ownership
```

---

# Testing Implications

Foundation planning may inspect existing tests.

Planning should identify future testing requirements but must not claim implementation validation that did not occur.

Possible categories include:

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
offline behavior
synchronization
```

Use:

```text
PASS
FAIL
NOT RUN
BLOCKED
```

Never claim a test passed unless it actually ran and passed.

---

# Scope Control

During one Foundation phase:

```text
solve the requested architectural question
```

Do not redesign unrelated systems.

If unrelated improvements are discovered:

```text
record as follow-up work
```

Do not expand scope automatically.

---

# Foundation Completion Check

Before declaring a Foundation phase ready for review, verify:

```text
required repository areas inspected
dependencies respected
existing architecture considered
reuse opportunities identified
architecture recommendation explicit
security considered
offline behavior considered
integration impact considered
sensitive-data impact considered
database impact considered
testing implications identified
canonical documentation impact identified
decision register complete
risk register complete
NOT VERIFIED items explicit
downstream contract written
no unauthorized implementation occurred
```

---

# Guiding Principle

Foundation architecture should make future F7Hub development:

```text
predictable
extensible
offline-capable
vendor-neutral
secure
reviewable
testable
reversible
```

without freezing the product into today's assumptions.

Prefer:

```text
small
verified
explicit
reusable
controlled
```

architectural decisions.

F7Hub should become more understandable after every development cycle.