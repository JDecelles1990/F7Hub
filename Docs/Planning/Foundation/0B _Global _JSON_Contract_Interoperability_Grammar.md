# F7Hub Phase 0B

## Cross-Subsystem Planning Note

Add shared rules for schema_version, producer/consumer ownership, correlation IDs, ticket_id, session_id, atomic replacement, explicit null/unknown semantics, stale-state detection, and event/result separation

# Global JSON & Interoperability Contract Planning Instructions
Inventory of existing JSON, DTO, protocol and IPC structures; producer/consumer matrix; common envelope; command/query/event/result/error semantics; message IDs and correlation; timestamp rules; naming and serialization rules; versioning and backwards compatibility; common error/status vocabulary; PowerShell structured-output contract; AHK/Python contract boundary; Mochi context/action contracts; transport comparison; local IPC security; contract test strategy; schema/fixture strategy.

## Existing Interoperability Inventory

### AltF7Hub
Current transport:
Current message format:
Current producer:
Current consumer:
Validation:
Error behavior:
Versioning:
Tests:

### Mochi
Current transport:
Current protocol:
Current producer:
Current consumer:
Validation:
Versioning:
Tests:

### PowerShell
Invocation mechanism:
Input model:
stdout model:
stderr model:
exit-code semantics:
structured result model:
tests:

### Other Existing Contracts
...


## Mode

`@ARCHITECT @PLAN`

Architecture and contract design only.

Do not implement production code.

Do not create IPC servers.

Do not create PowerShell scripts.

Do not create AHK transport code.

Do not create SQLite migrations.

Do not refactor unrelated components.

Do not select a major transport mechanism without documenting alternatives and consequences.

---

# 1. Objective

Design the Global F7Hub Interoperability Contract Architecture.

The purpose is to define how structured information is exchanged safely and consistently between:

```text
Python
PySide6
AutoHotkey v2
PowerShell
Mochi
Clipboard
Diagnostic Engine
Automation
future F7Hub integrations
```

The result must establish a common communication language before individual feature contracts are implemented.

The architecture must prevent every subsystem from inventing its own incompatible JSON conventions.

---

# 2. Relationship to Phase 0A

Phase 0A established the Master Foundation Architecture.

Phase 0B must operate inside those approved boundaries.

Before designing contracts:

1. Read the approved Phase 0A Master Foundation Architecture.
2. Inspect relevant current F7Hub code and documentation.
3. Identify any existing JSON conventions.
4. Identify existing PowerShell result formats.
5. Identify existing Python models or DTOs.
6. Identify existing IPC mechanisms.
7. Identify existing script-registry conventions.
8. Identify current error-handling patterns.
9. Reuse existing conventions when they remain suitable.

Do not assume that F7Hub currently has no interoperability conventions.

If something was not inspected, state:

```text
NOT VERIFIED
```

---

# 3. Primary Contract Principle

Separate:

```text
WHAT IS COMMUNICATED
```

from:

```text
HOW IT IS TRANSPORTED
```

The JSON contract defines:

```text
structure
meaning
validation
version
identity
context
errors
results
security expectations
```

The transport defines:

```text
how bytes move
```

Possible transports may eventually include:

```text
localhost HTTP
Named Pipes
local sockets
stdin/stdout
process execution
file exchange
```

A contract should not be redesigned merely because transport changes.

---

# 4. Contract Architecture Goal

Preferred conceptual structure:

```text
F7Hub Interoperability Contract
│
├── Common Envelope
│
├── Common Metadata
│
├── Common Context
│
├── Common Error Model
│
├── Common Status Model
│
├── Common Execution Metadata
│
│
├── Clipboard Contracts
├── Diagnostic Contracts
├── Automation Contracts
├── PowerShell Result Contracts
├── Mochi Context Contracts
└── Application/Event Contracts
```

Feature-specific payloads should reuse the common foundation.

---

# 5. Do Not Create One Giant Universal Payload

Avoid:

```json
{
  "clipboard": {},
  "ticket": {},
  "diagnostic": {},
  "powershell": {},
  "analytics": {},
  "mochi": {},
  "automation": {},
  "everything_else": {}
}
```

Instead use:

```text
Common Envelope
       +
Domain-Specific Payload
```

For example:

```text
Envelope
    ↓
clipboard.capture payload
```

or:

```text
Envelope
    ↓
diagnostic.result payload
```

This preserves strong boundaries.

---

# 6. Contract Families to Design

Phase 0B must define the architecture for at least these contract families.

## Clipboard

```text
clipboard.capture
clipboard.process
clipboard.result
clipboard.action_request
clipboard.action_result
```

## Diagnostics

```text
diagnostic.request
diagnostic.started
diagnostic.result
diagnostic.failed
diagnostic.cancelled
```

## PowerShell

```text
powershell.execution_request
powershell.execution_result
```

PowerShell should preferably sit behind approved diagnostic or automation abstractions rather than become a public arbitrary-command interface.

## Automation

```text
automation.request
automation.started
automation.result
automation.failed
```

## Mochi

```text
mochi.context
mochi.message
mochi.action_request
mochi.action_result
```

## General Application Events

Potential examples:

```text
application.event
context.updated
ticket.selected
clipboard.selected
diagnostic.selected
```

The final naming convention must be recommended during this planning phase.

---

# 7. Message Classes

Classify every contract as one of:

```text
COMMAND
QUERY
EVENT
RESULT
ERROR
```

## Command

Requests an intentional action.

Example:

```text
diagnostic.run
```

## Query

Requests information without changing operational state.

Example:

```text
clipboard.lookup
```

## Event

Reports something that already occurred.

Example:

```text
clipboard.captured
```

## Result

Returns the outcome of an earlier request.

Example:

```text
diagnostic.result
```

## Error

Communicates contract or execution failure.

Example:

```text
contract.validation_failed
```

The plan must define which classes require responses.

---

# 8. Recommended Common Envelope

Evaluate an envelope concept similar to:

```json
{
  "contract_version": "1.0",
  "message_id": "uuid",
  "message_type": "command",
  "event": "clipboard.process",
  "timestamp": "2026-10-04T23:30:00-04:00",
  "source": {},
  "context": {},
  "payload": {}
}
```

Do not treat this exact shape as approved automatically.

Phase 0B must evaluate and refine it.

---

# 9. Required Common Envelope Fields

Determine whether every message requires:

```text
contract_version
message_id
message_type
event / operation
timestamp
source
payload
```

Determine which fields are optional:

```text
correlation_id
causation_id
context
target
metadata
trace
```

Avoid adding fields without a clear purpose.

---

# 10. Message Identity

Every message should have a unique identifier.

Recommended concept:

```text
message_id
```

Likely format:

```text
UUID
```

Example:

```text
f43cf246-5e9b-42a2-a867-b31db09c44dc
```

Use cases:

- logging
- troubleshooting
- duplicate detection
- response matching
- auditing

---

# 11. Correlation ID

For workflows involving multiple messages, define:

```text
correlation_id
```

Example:

```text
AHK capture
    ↓
Python classification
    ↓
Diagnostic request
    ↓
PowerShell result
    ↓
Mochi explanation
```

All may belong to one:

```text
correlation_id
```

This allows F7Hub to reconstruct the workflow.

---

# 12. Causation ID

Consider:

```text
causation_id
```

Example:

```text
Message A
clipboard.captured

causes

Message B
clipboard.process
```

Then:

```text
Message B.causation_id
=
Message A.message_id
```

This is especially useful for:

```text
debugging
automation tracing
audit
event-chain reconstruction
```

Phase 0B should determine whether F7Hub needs this now or should reserve it for later.

---

# 13. Timestamp Standard

All interoperable contracts should use one timestamp standard.

Recommended:

```text
ISO 8601
```

Example:

```text
2026-10-04T23:30:00-04:00
```

The plan must decide:

- whether messages preserve local timezone offsets
- whether persistence normalizes to UTC
- precision requirements
- whether durations use milliseconds

Avoid ambiguous timestamps such as:

```text
10/04/26 11:30
```

---

# 14. Source Metadata

Design a common `source` structure.

Potential fields:

```json
{
  "component": "altf7hub",
  "technology": "ahk_v2",
  "application": "OUTLOOK.EXE",
  "window_title": "Inbox - Outlook"
}
```

Different contracts may populate different fields.

Do not require source metadata that cannot reliably be obtained.

---

# 15. F7Hub Context

Contracts should be able to carry optional contextual identifiers without embedding entire domain records.

Possible context:

```json
{
  "ticket_id": 41872,
  "company_id": 42,
  "contact_id": 88,
  "device_id": 103,
  "clipboard_item_id": 901,
  "diagnostic_session_id": 55
}
```

Important rule:

```text
Context references identifiers.

Context should not become a copy
of the entire F7Hub database record.
```

This reduces payload size and stale duplicated state.

---

# 16. Context Ownership

Determine:

```text
who may add context
who may modify context
who validates context
```

Example:

AHK may provide:

```text
source application
active window
clipboard content
```

But should not be trusted to assert:

```text
company_id = 42
```

without Python validating that reference.

---

# 17. Payload Design

Each contract must define a specific payload schema.

Example conceptual clipboard payload:

```json
{
  "content": {
    "format": "text/plain",
    "value": "0x8004010F",
    "size_bytes": 10
  }
}
```

Example diagnostic request payload:

```json
{
  "diagnostic_key": "network.dns",
  "parameters": {
    "hostname": "microsoft.com"
  }
}
```

Different domain payloads should not share fields merely because they happen to be JSON.

---

# 18. Contract Naming Convention

Define one naming system.

Recommended candidate:

```text
domain.action
```

Examples:

```text
clipboard.capture
clipboard.classify
diagnostic.run
diagnostic.result
automation.run
mochi.context
```

Alternative:

```text
domain.resource.action
```

Example:

```text
diagnostic.dns.run
```

Phase 0B must evaluate the naming depth that best balances clarity and stability.

---

# 19. Versioning Strategy

Contract versioning must be planned before implementation.

Determine whether version lives:

```text
globally
per contract family
per schema
```

Candidate:

```json
{
  "contract_version": "1.0"
}
```

Versioning rules should define:

```text
PATCH
non-semantic documentation clarification

MINOR
backward-compatible optional additions

MAJOR
breaking structural/semantic change
```

Do not casually bump versions for every internal code change.

---

# 20. Backward Compatibility

Plan how older components behave when receiving:

```text
new optional fields
unknown fields
new enum values
unsupported major versions
```

Recommended principle:

```text
Unknown optional fields:
ignore safely where permitted.

Unsupported major version:
reject explicitly.
```

Do not silently interpret incompatible contracts.

---

# 21. Schema Validation

Every external or cross-language payload must be validated before domain use.

Conceptual boundary:

```text
AHK / PowerShell / external process
             ↓
        JSON payload
             ↓
       Schema Validation
             ↓
      Application Service
```

Not:

```text
External JSON
     ↓
Repository
```

Phase 0B should recommend the Python validation strategy.

Potential options include:

```text
dataclasses
Pydantic
JSON Schema
custom validation
```

Do not add a dependency without evaluating current F7Hub conventions.

---

# 22. JSON Schema

Evaluate whether formal JSON Schema definitions should become the language-neutral source of contract documentation.

Possible advantages:

```text
cross-language validation
documentation
test fixture generation
contract versioning
PowerShell validation
AHK interoperability reference
```

Potential cost:

```text
additional tooling
duplication with Python models
maintenance burden
```

Recommend whether F7Hub should use:

```text
JSON Schema
Python models only
hybrid approach
```

and explain why.

---

# 23. Serialization Rules

Define global serialization rules.

At minimum determine:

```text
UTF-8
null handling
empty strings
booleans
numbers
timestamps
enum casing
property naming
line endings
Unicode
```

Recommended property convention:

```text
snake_case
```

because Python and current database naming are likely to align naturally.

Do not mix:

```text
sourceApp
source_app
SourceApplication
```

without a deliberate boundary adapter.

---

# 24. Enum Conventions

Define consistent enum representation.

Recommended:

```text
UPPER_SNAKE_CASE
```

or:

```text
lower_snake_case
```

Choose one.

Example:

```text
SUCCESS
WARNING
FAILURE
```

or:

```text
success
warning
failure
```

Consistency matters more than the exact choice.

---

# 25. Status Model

Define whether all contract families share a minimal common status vocabulary.

Possible base:

```text
success
warning
failure
error
cancelled
timeout
```

Be careful:

```text
failure
```

may mean a valid diagnostic finding,

while:

```text
error
```

may mean the diagnostic itself could not execute.

Example:

```text
DNS Diagnostic

status = failure
```

could mean:

```text
DNS genuinely failed.
```

Whereas:

```text
status = error
```

could mean:

```text
PowerShell crashed before DNS could be tested.
```

This semantic distinction should be explicit.

---

# 26. Common Error Model

Design a standard error structure.

Conceptual example:

```json
{
  "error": {
    "code": "CONTRACT_VALIDATION_FAILED",
    "message": "Required property 'payload' is missing.",
    "details": {},
    "retryable": false
  }
}
```

Potential fields:

```text
code
message
details
retryable
origin
```

Do not expose:

```text
secrets
stack traces
full internal paths
credentials
```

to consumers unnecessarily.

---

# 27. Error Categories

Consider a stable set such as:

```text
CONTRACT_ERROR
VALIDATION_ERROR
SECURITY_ERROR
NOT_FOUND
CONFLICT
TIMEOUT
EXECUTION_ERROR
UNSUPPORTED_VERSION
PERMISSION_ERROR
INTERNAL_ERROR
```

Feature domains may define additional specific codes.

Avoid using free-form text as the only machine-readable failure indication.

---

# 28. PowerShell Result Contract

This deserves special care.

PowerShell scripts should ideally return machine-readable structured output.

Conceptual architecture:

```text
Python
  ↓
Approved Script Registry
  ↓
PowerShell
  ↓
JSON Result
  ↓
Schema Validator
  ↓
Diagnostic / Automation Service
```

The result should distinguish:

```text
execution metadata
status
findings
evidence
recommendations
warnings
errors
```

---

# 29. Diagnostic Findings

A Finding answers:

```text
What was discovered?
```

Conceptual structure:

```json
{
  "code": "DNS_RESOLUTION_FAILED",
  "severity": "warning",
  "title": "DNS resolution failed",
  "message": "The requested hostname could not be resolved."
}
```

Findings should be structured enough to:

```text
display
search
persist
aggregate
tag
analyze
```

---

# 30. Evidence

Evidence answers:

```text
What facts support the finding?
```

Example:

```json
{
  "query": "microsoft.com",
  "dns_server": "192.168.1.1",
  "response": null,
  "timeout_ms": 5000
}
```

Evidence should preserve factual output without mixing interpretation into it.

---

# 31. Recommendations

Recommendations answer:

```text
What might the technician consider next?
```

Example:

```json
{
  "priority": 1,
  "action_key": "compare_dns_configuration",
  "message": "Compare configured DNS servers with a working device."
}
```

Recommendations are not findings.

They must remain semantically separate.

---

# 32. Execution Metadata

Potential common execution structure:

```json
{
  "execution_id": "uuid",
  "started_at": "...",
  "completed_at": "...",
  "duration_ms": 742
}
```

Additional fields may include:

```text
script_id
script_version
runtime
host
exit_code
```

Only include fields relevant to the contract.

---

# 33. PowerShell stdout / stderr

Plan strict handling.

Preferred:

```text
structured JSON
```

should be distinct from:

```text
human-readable console output
debug output
stderr
```

A script writing decorative text around JSON can corrupt machine parsing.

The planning document must define conventions such as:

```text
stdout = contract JSON only
stderr = diagnostic/process errors
```

if compatible with current architecture.

---

# 34. Clipboard Contract

Clipboard contracts should support:

```text
raw clipboard text
source metadata
capture method
requested action
context
```

Example conceptual request:

```json
{
  "contract_version": "1.0",
  "message_id": "uuid",
  "message_type": "command",
  "operation": "clipboard.process",
  "timestamp": "...",
  "source": {
    "component": "altf7hub",
    "application": "powershell.exe"
  },
  "payload": {
    "content": {
      "format": "text/plain",
      "value": "Get-Service Spooler"
    }
  }
}
```

The detailed Clipboard schema can later be refined during Clipboard architecture planning.

---

# 35. Clipboard Result

Conceptually:

```json
{
  "classification": {
    "primary_kind": "powershell_command",
    "confidence": 1.0
  },
  "entities": [],
  "suggested_tags": [],
  "available_actions": []
}
```

Phase 0B should define the boundary, not the entire future taxonomy.

Entity and Tag vocabularies belong primarily to Phase 0C.

---

# 36. Avoid Contract/Taxonomy Coupling

The contract should be able to carry:

```text
entity_type_key
tag_key
primary_kind
```

without embedding the complete taxonomy definition.

Example:

```json
{
  "entity_type_key": "ipv4",
  "value": "10.0.0.87"
}
```

not:

```json
{
  "entity_type": {
    "key": "ipv4",
    "display_name": "IPv4 Address",
    "family": "network",
    "description": "...",
    "all_related_tags": []
  }
}
```

Contracts should transmit references and required facts, not duplicate catalog data.

---

# 37. Mochi Context Contract

Mochi should receive a curated context object.

Avoid:

```text
dump entire database record
dump entire Clipboard history
dump full raw logs
```

Prefer:

```json
{
  "ticket": {
    "ticket_id": 41872,
    "summary": "Outlook cannot send"
  },
  "clipboard": {
    "kind": "smtp_error",
    "entities": []
  },
  "diagnostic": {
    "status": "warning",
    "findings": []
  }
}
```

The plan must define:

```text
what Mochi may receive
what must be redacted
what is optional
what has size limits
```

---

# 38. Mochi Action Contract

Mochi should request actions through structured contracts.

Example:

```json
{
  "operation": "diagnostic.run",
  "payload": {
    "diagnostic_key": "network.dns"
  }
}
```

Mochi should not produce:

```text
"Run this arbitrary PowerShell command..."
```

that is automatically executed.

All actions must pass normal F7Hub service/security boundaries.

---

# 39. Automation Contract

Automation requests need clear ownership.

Conceptually:

```text
automation.request
```

may specify:

```text
automation_key
approved parameters
context
```

It must never become:

```text
arbitrary executable content
```

Avoid:

```json
{
  "command": "whatever the caller wants"
}
```

Prefer:

```json
{
  "automation_key": "network.flush_dns",
  "parameters": {}
}
```

where the key maps to an approved registry entry.

---

# 40. Request / Response Pattern

Define how synchronous requests correlate with results.

Example:

```text
Request:
message_id = A

Response:
correlation_id = A
```

or another clearly documented convention.

Do not make each integration invent response matching.

---

# 41. Event Pattern

Events should describe completed facts.

Example:

```text
clipboard.captured
```

means:

```text
the capture happened
```

not:

```text
please capture something
```

That would instead be a command.

This distinction should be enforced in naming conventions.

---

# 42. Asynchronous Operations

Some operations may take longer:

```text
diagnostics
PowerShell
automation
large parsing tasks
```

The contract architecture should support:

```text
request
started
progress optional
completed
failed
cancelled
```

without requiring progress messages for every operation.

---

# 43. Cancellation

Determine how cancellable operations are represented.

Potential command:

```text
diagnostic.cancel
```

with:

```text
execution_id
```

Define what cancellation means:

```text
requested
acknowledged
completed
```

Do not assume process termination equals safe cancellation.

---

# 44. Idempotency

Consider which commands should be safe against accidental duplicates.

For example:

```text
clipboard.process
```

may be naturally idempotent if keyed by:

```text
content_hash
```

But:

```text
automation.execute
```

may not be.

Determine whether certain requests need:

```text
idempotency_key
```

or whether message IDs plus service-level protections are sufficient.

---

# 45. Duplicate Message Handling

AHK or IPC retries could result in duplicate messages.

Plan how F7Hub detects:

```text
same message_id received twice
```

Possible behavior:

```text
return original result
ignore duplicate event
reject duplicate
```

depending on message class.

---

# 46. Payload Size Limits

Define architectural limits.

Especially relevant for:

```text
Clipboard
logs
PowerShell output
diagnostic evidence
Mochi context
```

Phase 0B should recommend:

```text
global maximum
contract-specific maximum
large-content strategy
```

For example:

```text
inline content
preview only
external managed file reference
```

Do not pass unbounded multi-megabyte content through every layer.

---

# 47. Large Content References

Future contracts may need to reference rather than embed large content.

Conceptual structure:

```json
{
  "content_reference": {
    "type": "managed_file",
    "id": "..."
  }
}
```

Do not design the entire file-storage system here.

Identify the boundary and defer implementation.

---

# 48. Sensitive Content

Contracts must support privacy handling.

Clipboard and Mochi flows especially may encounter:

```text
passwords
tokens
MFA codes
API keys
private keys
connection strings
PII
customer data
```

Plan:

```text
sensitivity classification
redaction indicators
blocked payload behavior
audit behavior
```

Never automatically route secrets to Mochi or future cloud AI.

---

# 49. Trust Boundary

Treat these producers as untrusted until validated:

```text
AHK
PowerShell
clipboard content
external APIs
imported files
future plugins
AI output
```

Even localhost traffic must be validated.

Local does not equal trusted.

---

# 50. Local IPC Security

If a localhost bridge is later selected, the contract plan should identify security requirements such as:

```text
bind only to loopback
authentication token
action allowlist
payload limits
rate limits
schema validation
no arbitrary execution endpoint
audit logging
```

Do not implement the transport in this phase.

---

# 51. Contract Registry

Consider a central contract inventory.

Conceptually:

```text
Contracts/
├── common/
├── clipboard/
├── diagnostics/
├── automation/
└── mochi/
```

or whatever location matches the inspected architecture.

Possible contents:

```text
schema
examples
version history
documentation
```

Exact repository location must follow current conventions.

---

# 52. Contract Documentation

Every contract should eventually document:

```text
name
purpose
producer
consumer
message class
schema version
required fields
optional fields
validation
size limits
security classification
expected responses
error codes
example payload
```

This prevents hidden assumptions.

---

# 53. Contract Test Fixtures

Plan reusable fixtures.

Example:

```text
valid/
clipboard_capture_basic.json

invalid/
clipboard_capture_missing_payload.json

compatibility/
clipboard_capture_v1_optional_field.json
```

These can later be consumed by:

```text
Python tests
PowerShell tests
AHK integration tests
```

---

# 54. Cross-Language Contract Tests

Future validation should confirm:

```text
AHK produces valid contract
Python consumes it

Python produces valid result
AHK consumes it

Python launches PowerShell
PowerShell returns valid result
Python validates it
```

Contract compatibility should become independently testable.

---

# 55. PowerShell Contract Tests

Future tests should cover:

```text
valid result
warning result
diagnostic failure
execution error
timeout
invalid JSON
missing field
wrong contract version
extra optional field
Unicode content
large evidence payload
```

---

# 56. Clipboard Contract Tests

Future tests should cover:

```text
plain text
URL
PowerShell command
large content
Unicode
empty clipboard
invalid encoding
secret-like content
duplicate message
unknown optional field
unsupported major version
```

---

# 57. Logging

Determine what contract metadata is appropriate for logs.

Safe candidates:

```text
message_id
correlation_id
contract name
version
status
duration
source component
```

Avoid blindly logging:

```text
clipboard payload
tokens
customer data
PowerShell evidence
Mochi context
```

Logging policy must respect sensitivity.

---

# 58. Observability

The contract architecture should make future troubleshooting possible.

A diagnostic flow might be traceable:

```text
Clipboard Capture
message_id A
        ↓
Classification
message_id B
correlation A
        ↓
Diagnostic
message_id C
correlation A
        ↓
PowerShell
execution X
        ↓
Result
message_id D
correlation A
```

This is especially useful when diagnosing cross-language failures.

---

# 59. Persistence Boundary

Do not automatically persist every contract.

Contracts are communication objects.

Domain repositories decide what becomes durable.

Example:

```text
clipboard.capture contract
        ↓
ClipboardService
        ↓
validation
        ↓
Clipboard domain model
        ↓
Repository
```

Do not store raw interchange messages as the primary domain model unless explicitly justified.

---

# 60. Domain Model ≠ Transport DTO

The plan must explicitly distinguish:

```text
Transport DTO
```

from:

```text
Domain Model
```

For example:

```text
ClipboardCaptureRequest
```

is not automatically the same object as:

```text
ClipboardItem
```

This prevents transport concerns from leaking into the domain.

---

# 61. Analytics Boundary

Statistical Analytics should consume persisted domain facts.

Avoid making analytics depend directly on transient IPC payloads.

Preferred:

```text
JSON
 ↓
Application Service
 ↓
Domain
 ↓
SQLite
 ↓
Analytics
```

Not:

```text
JSON event
 ↓
Analytics calculates permanent truth immediately
```

unless a future event architecture explicitly requires it.

---

# 62. Tag and Entity Boundary

Phase 0B should only define how contracts carry taxonomy references.

Example:

```json
{
  "entity_type_key": "ipv4",
  "normalized_value": "10.0.0.87",
  "confidence": 1.0
}
```

and:

```json
{
  "tag_key": "networking",
  "confidence": 0.97,
  "source": "RULE"
}
```

The authoritative catalog definitions belong to Phase 0C.

---

# 63. Settings Boundary

Some contract behavior may depend on Settings.

Examples:

```text
payload size limits
clipboard capture enabled
Mochi enabled
diagnostic timeout
```

Contract schemas should not embed configuration values unnecessarily.

Services resolve current settings.

---

# 64. AHK Responsibilities

AHK should generally:

```text
capture
package
send
receive
display quick result
perform allowed UI actions
```

AHK should not:

```text
perform domain validation
write SQLite
decide taxonomy truth
interpret complex diagnostic evidence
```

The contract design should keep AHK payload generation reasonably simple.

---

# 65. Python Responsibilities

Python should generally:

```text
validate
normalize
authorize
route
orchestrate
convert DTO → domain
convert domain result → response DTO
```

Python becomes the primary contract boundary inside F7Hub.

---

# 66. PowerShell Responsibilities

PowerShell should:

```text
receive approved parameters
execute approved task
return structured results
```

PowerShell should not:

```text
invent ticket workflow
write arbitrary F7Hub DB records
control Mochi
define global taxonomy
```

---

# 67. Mochi Responsibilities

Mochi should consume:

```text
curated context
structured findings
approved recommendations
historical insights
```

and produce:

```text
messages
explanations
optional action requests
```

not unrestricted executable instructions.

---

# 68. Transport Evaluation

Phase 0B should compare likely transport mechanisms.

At minimum evaluate:

| Transport | Strengths | Weaknesses | Likely Use |
|---|---|---|---|
| localhost HTTP | simple/debuggable | listener/security overhead | AHK ↔ Python |
| Named Pipes | Windows-native/local | more implementation complexity | local IPC |
| stdin/stdout | simple process boundary | request-oriented only | Python ↔ PowerShell |
| file exchange | easy prototype | latency/race/cleanup problems | generally avoid for live IPC |

Do not select a transport solely because one snippet is easy to write.

---

# 69. Likely Transport Direction

Evaluate whether F7Hub should eventually use different transports for different boundaries.

Example:

```text
AHK ↔ Python
Named Pipe or localhost service

Python → PowerShell
process invocation + structured stdout

PySide6 ↔ Python
in-process service calls
```

A single transport is not required everywhere.

The contract conventions can remain shared.

---

# 70. Contract Evolution

Define how contract changes are proposed.

Recommended process:

```text
Need identified
    ↓
Contract change proposed
    ↓
Compatibility reviewed
    ↓
Schema updated
    ↓
Fixtures updated
    ↓
Producer tests
    ↓
Consumer tests
    ↓
Documentation updated
```

Do not allow silent schema drift.

---

# 71. Contract Ownership

Recommend an owner for global interoperability conventions.

Conceptually:

```text
F7Hub Application / Infrastructure Boundary
```

Individual modules own their payload semantics.

Example:

```text
Clipboard module owns clipboard payload fields.

Global contract architecture owns:
versioning
envelope
errors
timestamps
identity
common conventions
```

---

# 72. Contract Registry Table?

Evaluate whether contract definitions need SQLite persistence.

Default recommendation should probably be:

```text
No.
```

Contract schemas are application/versioned source artifacts, not user data.

Only choose database persistence if a concrete requirement exists.

---

# 73. Contract Security Classification

Consider documenting contract sensitivity:

```text
PUBLIC_LOCAL
INTERNAL
SENSITIVE
SECRET_POSSIBLE
```

or a simpler model.

This could influence:

```text
logging
persistence
Mochi eligibility
analytics eligibility
```

Do not over-engineer if sensitivity is already governed elsewhere.

---

# 74. Required Contract Matrix

Produce a matrix like:

| Contract | Class | Producer | Consumer | Sync/Async | Sensitive? |
|---|---|---|---|---|---|
| clipboard.capture | Event | AHK | Python | Async | Possible |
| clipboard.process | Command | AHK/PySide6 | Python | Request | Possible |
| diagnostic.run | Command | Python/UI | Diagnostic Service | Async | Contextual |
| diagnostic.result | Result | Diagnostic Service | UI/Ticket/Mochi | Async | Possible |
| powershell.result | Result | PowerShell | Python | Request | Possible |
| mochi.context | Context | Python | Mochi | Request | Yes |

Do not populate unverified producers/consumers as FACT.

Use recommendations where appropriate.

---

# 75. Required Sequence Diagrams

Produce conceptual sequence diagrams for at least:

## AHK Clipboard Flow

```text
Windows
→ AHK
→ Python
→ ClipboardService
→ response
→ AHK HUD
```

## Clipboard → Diagnostic Flow

```text
Clipboard Center
→ DiagnosticService
→ PowerShell
→ DiagnosticService
→ SQLite
→ Diagnostic Center
```

## Diagnostic → Mochi Flow

```text
Diagnostic Center
→ ContextService
→ Mochi
→ message
```

## Contract Failure Flow

```text
Producer
→ Validator
→ rejection
→ structured error
```

Use Mermaid if existing project documentation supports it.

---

# 76. Required Trust Diagram

Map:

```text
Windows Clipboard
AHK
Python boundary
PowerShell subprocess
SQLite
Mochi
future AI
```

Mark where:

```text
validation
authorization
redaction
persistence
```

occur.

---

# 77. Required Decision Register

At minimum evaluate these decisions:

```text
Common envelope?
Version format?
Naming convention?
Timestamp convention?
Enum convention?
Formal JSON Schema?
Validation library?
Correlation IDs?
Causation IDs?
Idempotency support?
Large-payload handling?
PowerShell stdout convention?
Local IPC transport?
Mochi context limits?
Error taxonomy?
```

For each:

```text
Decision
Status
Options
Recommendation
Reason
Consequences
Deferred work
```

Statuses:

```text
RECOMMENDED
REQUIRES USER DECISION
DEFERRED
NOT VERIFIED
```

---

# 78. Decisions That Should Likely Be Made Now

Phase 0B should aim to settle:

```text
contract naming convention
common envelope
message identity
timestamps
versioning model
error structure
status semantics
serialization conventions
validation boundary
PowerShell structured-output rule
contract/domain separation
security principles
```

---

# 79. Decisions That May Be Deferred

Likely candidates:

```text
final AHK ↔ Python transport
progress-message protocol
large-file reference implementation
future plugin contract
remote/cloud transport
AI provider contracts
binary clipboard contract
```

The report should confirm whether these can safely remain deferred.

---

# 80. Acceptance Criteria

The Phase 0B plan is acceptable when:

1. Existing interoperability mechanisms have been inspected.
2. Existing JSON structures have been inventoried.
3. Contract and transport are clearly separated.
4. A common envelope has been recommended or explicitly rejected with rationale.
5. Contract naming conventions are defined.
6. Versioning rules are defined.
7. Message identity rules are defined.
8. Request/result correlation is defined.
9. Error semantics are defined.
10. Status semantics are defined.
11. Serialization conventions are defined.
12. Validation ownership is defined.
13. PowerShell result requirements are defined.
14. AHK responsibilities are constrained.
15. Mochi action boundaries are constrained.
16. Clipboard contract boundaries are defined.
17. Large and sensitive payload handling is addressed.
18. Security/trust boundaries are mapped.
19. Contract families are inventoried.
20. Future compatibility strategy is documented.
21. Contract tests are planned.
22. No implementation has occurred.
23. Phase 0C can safely build taxonomy contracts on top of this architecture.

---

# 81. Validation Status

Final validation must include:

```text
Repository inspection                PASS / FAIL / BLOCKED
Existing contract inventory          PASS / FAIL / BLOCKED
Envelope architecture                PASS / FAIL / BLOCKED
Versioning model                     PASS / FAIL / BLOCKED
Error/status semantics               PASS / FAIL / BLOCKED
PowerShell contract boundary         PASS / FAIL / BLOCKED
AHK contract boundary                PASS / FAIL / BLOCKED
Mochi security boundary              PASS / FAIL / BLOCKED
Payload/privacy review               PASS / FAIL / BLOCKED
Compatibility review                 PASS / FAIL / BLOCKED
Scope control                        PASS / FAIL / BLOCKED
Production code modifications        MUST BE NONE
Database modifications               MUST BE NONE
```

---

# 82. Required Final Report

Return the report in this order:

## Summary

Overall recommended interoperability architecture.

## Inspected Current State

Existing mechanisms and conventions found in F7Hub.

## Contract Principles

Global invariants.

## Common Envelope

Recommended common fields and responsibilities.

## Message Classes

Commands, queries, events, results, errors.

## Contract Families

Clipboard, Diagnostics, PowerShell, Automation, Mochi, Application.

## Status and Error Model

Shared semantics.

## Versioning & Compatibility

Evolution rules.

## Serialization Rules

JSON conventions.

## Security & Privacy

Trust boundaries and sensitive content handling.

## PowerShell Contract

Structured result requirements.

## AHK Contract

Producer/consumer responsibilities.

## Mochi Contract

Context and action boundaries.

## Contract Matrix

Producer/consumer mapping.

## Transport Evaluation

Options and deferred decisions.

## Sequence Diagrams

Primary interoperability workflows.

## Testing Strategy

Contract validation and cross-language compatibility.

## Decision Register

Approved recommendations, unresolved decisions, deferred choices.

## Risks

Contract drift, coupling, security, incompatible producers, large payloads, schema duplication.

## Phase 0C Inputs

Explicitly list what the Classification & Taxonomy architecture may now rely on.

## Result

Return exactly one:

```text
READY_FOR_TAXONOMY_DESIGN
REQUIRES_CONTRACT_DECISIONS
BLOCKED
```

Do not return:

```text
READY_FOR_IMPLEMENTATION
```

Phase 0B remains a foundation architecture task.

                 F7Hub Contract Layer
                        │
       ┌────────────────┼────────────────┐
       │                │                │
      AHK             Python         PowerShell
       │                │                │
       └──────── structured JSON ────────┘
                        │
                 Application Services
                        │
          ┌─────────────┼─────────────┐
          │             │             │
      Clipboard     Diagnostics     Automation
                                      │
                                   Mochi

I would not require every F7Hub JSON document to have ticket_id or session_id.
Instead, the grammar should say:
When a JSON contract is ticket-bound, the stable F7Hub ticket ID must be explicit.

And:
When a contract is session-bound, the stable session ID must be explicit.

Other global concepts worth moving upward:
schema versioning
UTF-8
producer ownership
consumer ownership
atomic file replacement
unsupported-version behavior
nullable vs missing fields
timestamps
stable identifiers
correlation
stale-state handling
temporary vs durable state

Particularly important
DynamicHub also revealed:
event ≠ result

That distinction should probably become global.
Diagnostics, Analytics, DynamicHub and Mochi could all eventually produce events.

---

## External Integration and Offline Interoperability Constraints

### Internal Contract vs Vendor Contract

The F7Hub interoperability grammar is an internal architectural contract.

Do not treat an external vendor's JSON schema as the F7Hub domain model.

Preferred conceptual boundary:

External API
→ Provider Gateway / Adapter
→ validated provider DTO
→ F7Hub application/domain representation

Vendor-specific payloads must not leak unnecessarily into GUI, domain,
database or unrelated modules.

### Vendor Neutrality

The global interoperability contract must not require any specific:

- PSA
- RMM
- credential manager
- Microsoft administration platform
- AI provider

Provider-specific adapters may be added later.

### Offline Behavior

Interoperability planning must distinguish operations that:

- execute locally;
- may be delayed until connectivity returns;
- require current online state and must not be replayed later.

Delayed synchronization must consider:

- message identity;
- correlation;
- idempotency;
- confirmation of remote success;
- retryability;
- stale-state detection;
- duplicate prevention.

Do not assume that state-changing technical actions are safe to queue.

Examples such as device restart, account disablement, password reset or
remediation execution should normally require fresh context and renewed
authorization rather than automatic delayed replay.

### Secret Handling

Global JSON envelopes, diagnostic results, errors and logs must not
contain credential material unless a narrowly scoped approved contract
explicitly requires secure handling.

Do not place authentication secrets in:

- ordinary payload examples;
- schema fixtures;
- debug logs;
- error details;
- correlation metadata.

Use synthetic values in architecture documentation and tests.

### Capability Discovery

Where appropriate, integrations should expose approved capabilities
rather than forcing callers to assume provider permissions.

Examples:

- READ_TICKET
- WRITE_TICKET_NOTE
- READ_DEVICE
- RUN_APPROVED_AUTOMATION
- READ_TENANT
- USE_CREDENTIAL
- AI_SUMMARIZE

Exact capability vocabulary remains subject to architecture review.

A configured provider does not imply that every capability is available.