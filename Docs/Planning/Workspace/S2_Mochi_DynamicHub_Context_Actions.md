# F7Hub Workspace Planning S2
# Mochi, DynamicHub & Context-Aware Technician Actions Architecture Planning Contract

**Status:** `NOT_STARTED`  
**Mode:** `@ARCHITECT @PLAN`  
**Future repository path:** `Docs/Planning/Workspace/S2_Mochi_DynamicHub_Context_Actions.md`  
**Implementation authorization:** NONE

---

## 1. Purpose

Define how F7Hub combines:

```text
Mochi
DynamicHub
local IT AI
Active Technician Context
approved actions
Diagnostics
RMM integrations
Microsoft 365 integrations
future provider integrations
Ticket observations/evidence
context-aware follow-up suggestions
```

without giving AI unrestricted execution authority.

Target experience:

```text
technician context
-> Mochi receives a bounded projection
-> DynamicHub suggests useful approved actions
-> technician explicitly chooses an action
-> owning service/provider performs it
-> structured result returns
-> Mochi acknowledges briefly
-> eligible result is recorded through owning F7Hub services
-> DynamicHub suggests sensible next actions
```

---

## 2. Dependency Gate

Required approved inputs should include:

```text
Foundation 0A-0E CLOSED
S1 Main Shell / Technician Workspace APPROVED
relevant Diagnostics architecture APPROVED before execution design
provider/integration architecture APPROVED where required
```

Preserve Foundation ownership:

```text
DynamicHub may coordinate interactive troubleshooting through owning services/gateways.
Diagnostics retains diagnostic definitions, execution and result authority.
DynamicHub does not become competing persistence, Ticket, Clipboard, Knowledge, Analytics or AI authority.
```

If the proposed Mochi/DynamicHub specialization conflicts with that rule:

```text
FOUNDATION_OWNER_REVIEW_REQUIRED
```

---

## 3. User Experience Goal

Example context:

```text
Ticket: INC-10452
User: jane@contoso.com
Device: CONTOSO-LT042
Issue: intermittent connectivity
```

DynamicHub may offer:

```text
[Get network snapshot]
[Check DNS]
[Check device uptime]
[Check M365 licenses]
[Check mailbox]
[Search similar tickets]
```

After a successful action:

```text
Mochi overlay:
"Network snapshot collected.
Saved to INC-10452."
```

DynamicHub may then show:

```text
Gateway reachable
DNS: 10.0.0.10
Wi-Fi signal weak

[Test DNS]
[Check Wi-Fi adapter]
[Search similar tickets]
```

---

## 4. Core Ownership

### Mochi

Mochi is:

```text
personalized technician-assistant presentation
local/contextual AI-facing UX
brief acknowledgement/suggestion surface
```

Mochi is not:

```text
database owner
Ticket owner
PowerShell executor
RMM client
Graph client
authorization authority
secret store
```

### Local IT AI Sublayer

May:

```text
interpret bounded approved context
summarize structured results
rank approved actions
explain diagnostics
suggest searches
draft human-readable notes
```

May not grant itself execution authority.

### DynamicHub

DynamicHub is Mochi's contextual quick-action surface/coordinator.

May:

```text
show context-aware actions
show result summaries
show follow-up choices
route explicit action requests
```

Must not:

```text
execute arbitrary commands
own Diagnostics
write SQLite directly
become AI authority
bypass Action Catalog validation
```

### Owning Services

Effects remain with:

```text
DiagnosticService
TicketService
KnowledgeService
Script/Automation services
provider gateways
future Microsoft services
```

---

## 5. Mode and Prohibitions

Do not:

- implement RMM APIs
- implement Graph
- implement Adobe integrations
- execute PowerShell
- modify Ticket notes
- create credentials/secrets
- create migrations
- modify Mochi runtime
- modify a DynamicHub prototype
- enable unrestricted AI tool calling
- permit free-form AI-generated PowerShell execution
- automatically remediate customer systems
- make external AI/internet required for local technician workflows

---

## 6. Mandatory Current-State Inspection

Inspect:

```text
Mochi architecture
Mochi protocol/channel
Mochi runtime controls
MainWindow integration
Foundation DynamicHub decisions
Diagnostic service / PowerShell boundary
Script registry
TicketService note/activity behavior
Knowledge services
current provider/integration code
M365/Graph placeholders
RMM placeholders
Settings architecture
logging/security guidance
tests
```

Use:

```text
FACT
ASSUMPTION
INFERENCE
RECOMMENDATION
NOT VERIFIED
```

---

## 7. Context Projection

Consume S1 `ActiveTechnicianContext`.

Potential references:

```text
Company
User
Device
Ticket
Tenant
Session
selected Clipboard Item
selected Entity
selected Diagnostic result
current module
```

Mochi receives bounded projections, not unrestricted database/object access.

Conceptual projection:

```text
context_id
revision
ticket_ref?
company_ref?
user_ref?
device_ref?
tenant_ref?
selected_entity?
selected_result_ref?
module_key
privacy_class
capabilities
```

Do not include secrets by default.

---

## 8. Context Freshness

Every action must revalidate current context.

Examples of invalidation:

```text
Ticket changed
Device changed
User changed
Tenant changed
selection changed
provider capability changed
permission changed
```

AI must never silently retarget an action.

---

## 9. DynamicHub Trigger Policy

DynamicHub may appear when:

```text
technician opens Mochi
significant context changes
a diagnostic completes
a useful Entity is selected
a result has clear next actions
a recoverable failure occurs
```

Define:

```text
cooldown
repeated-suggestion suppression
one active DynamicHub surface
non-modal behavior
focus preservation
dismiss behavior
optional stay-open behavior
```

Avoid popup fatigue.

---

## 10. Mochi Acknowledgement Overlay

Plan a short overlay near Mochi.

Examples:

```text
"Network snapshot collected."
"Saved to INC-10452."
"M365 license checked."
"RMM unavailable."
```

Rules:

```text
brief
non-modal
no focus theft
privacy-safe
bounded lifetime
accessible text alternative
```

The overlay is presentation, not the sole record of failure/success.

---

## 11. Approved Action Catalog

This is a critical security boundary.

Mochi/DynamicHub should select approved action identifiers such as:

```text
network.snapshot
network.dns_check
device.uptime
device.disk_free
m365.user_summary
m365.license_summary
m365.mailbox_summary
knowledge.search_similar
ticket.add_observation
```

Catalog mapping:

```text
action_id
-> owner service
-> provider
-> approved implementation
-> parameter schema
-> required context
-> permission/capability
-> risk level
-> result schema
```

No AI-generated executable string becomes an action.

---

## 12. No Free-Form Remote PowerShell

Prohibited:

```text
AI
-> arbitrary generated PowerShell
-> RMM
-> customer endpoint
```

Required:

```text
AI/DynamicHub
-> approved action_id
-> Action Catalog
-> owning service
-> approved script/version
-> validated parameters
-> provider gateway
-> target
```

Any future free-form execution requires separate explicit architecture/security review.

---

## 13. Action Risk Classes

### SAFE_READ_ONLY

Candidates to evaluate:

```text
IP configuration
DNS configuration
gateway reachability
adapter state
Wi-Fi details
uptime
disk free
memory summary
OS/version
installed application version
M365 license summary
mailbox summary
```

Default UX:

```text
one explicit technician action
```

### CONFIRM_REQUIRED

Examples:

```text
restart service
flush DNS
restart adapter
refresh policy
```

Requires confirmation.

### MUTATING_HIGH_RISK

Examples:

```text
remove software
change account state
change security policy
modify mailbox
disable user
delete data
```

These belong in dedicated reviewed workflows, not lightweight one-click DynamicHub actions.

---

## 14. Future Automatic Safe Read-Only

Evaluate but do not implement:

```text
AUTO_SAFE_READ_ONLY
```

Only if:

```text
action explicitly whitelisted
provider capability verified
target unambiguous
privacy policy allows
rate limits allow
technician enabled it
```

Default architecture remains technician-controlled.

---

## 15. Provider Ownership

Use the correct provider instead of routing everything through RMM/PowerShell.

### Device / Windows

```text
approved Device/Diagnostic action
-> RMM Gateway
-> approved PowerShell or provider-native query
-> structured result
```

### Microsoft 365

```text
approved Microsoft action
-> Microsoft service/gateway
-> Graph / Exchange / required endpoint
-> structured result
```

### Adobe

Treat actual Adobe entitlement/license API access as:

```text
NOT VERIFIED
```

Distinguish:

```text
installed Adobe software -> local/RMM device fact
assigned Adobe entitlement -> Adobe/provider API if authorized
```

Do not promise entitlement visibility before provider/API verification.

---

## 16. Provider Capability Model

DynamicHub must only offer actions supported by current capabilities.

Potential capabilities:

```text
rmm.connected
rmm.device.read
m365.graph.read
m365.exchange.read
adobe.license.read
ticket.note.write
diagnostic.network.read
```

UI visibility is not authorization.

---

## 17. Structured Action Request

Conceptual request:

```text
action_id
request_id
context_revision
target_ref
parameters
initiator
confirmation_state
```

No arbitrary command field.

---

## 18. Structured Action Result

Conceptual result:

```text
request_id
action_id
status
target_ref
started_at
completed_at
provider
observations
safe_summary
evidence_refs
safe_followup_keys
error
```

Raw provider output must not automatically become Ticket content.

---

## 19. Structured Observations

Prefer facts before prose.

Example:

```text
action_id: network.snapshot

ipv4: 192.168.10.42
gateway: 192.168.10.1
dns_servers:
  - 10.0.0.10
  - 10.0.0.11
adapter: Intel Wi-Fi
gateway_reachable: true
wifi_signal: weak
```

Presentation may then derive:

```text
Mochi summary
DynamicHub result summary
Ticket observation
follow-up suggestions
```

The structured result remains authoritative.

---

## 20. Ticket Recording

Do not silently mix machine-generated output with technician-authored prose.

Prefer an existing Ticket activity/evidence mechanism or a clearly identified system-generated observation through `TicketService`.

Example rendered observation:

```text
[Network Snapshot]
Device: CONTOSO-LT042
IPv4: 192.168.10.42
Gateway: 192.168.10.1
DNS: 10.0.0.10, 10.0.0.11
Adapter: Intel Wi-Fi
Result: Gateway reachable
Source: RMM / network.snapshot
Time: ...
```

Do not invent a second Ticket-note store.

---

## 21. Local Ticket vs External PSA

Keep distinct:

```text
F7Hub local Ticket observation
```

and:

```text
external PSA synchronization
```

Do not assume every local observation is automatically published externally.

---

## 22. Ticketless Work

If no active Ticket exists:

```text
Diagnostic result / Case Journal
-> preserve locally according to owning architecture
-> associate with Ticket later if needed
```

Do not force Ticket creation merely to run a safe diagnostic.

---

## 23. Follow-Up Suggestions

Mochi may rank only approved follow-up action IDs using:

```text
active context
structured result
capabilities
privacy policy
recent action history
failure state
```

It must not fabricate unsupported actions.

Example:

```text
gateway reachable = true
dns = 10.0.0.10
wifi signal = weak

-> network.dns_check
-> network.wifi_details
-> ticket.search_similar
-> knowledge.search_network_issue
```

---

## 24. Failure and Partial Results

Plan for:

```text
provider offline
timeout
target offline
permission denied
capability unavailable
unsupported action
stale context
ambiguous target
partial result
parse failure
Ticket save failure
AI unavailable
rate limit
```

Distinguish truthful states such as:

```text
SUCCESS
PARTIAL
BLOCKED
UNAVAILABLE
ERROR
```

Do not show fake success.

---

## 25. AI-Unavailable Behavior

Deterministic approved actions should still work where possible.

AI may enhance:

```text
ranking
summaries
explanations
```

but must not be required for:

```text
permission validation
diagnostic execution
Ticket evidence persistence
```

---

## 26. Offline Classification

Classify actions as:

```text
LOCAL_REQUIRED
PROVIDER_REQUIRED
AI_OPTIONAL
```

Examples:

```text
local navigation -> LOCAL_REQUIRED
local KB search -> LOCAL_REQUIRED
RMM query -> PROVIDER_REQUIRED
Graph license check -> PROVIDER_REQUIRED
AI summarization -> AI_OPTIONAL where deterministic presentation exists
```

---

## 27. Privacy and Secrets

Do not automatically send:

```text
raw Clipboard history
full Ticket transcript
passwords
API keys
MFA codes
credential fields
customer secrets
```

to AI/providers.

No:

```text
hard-coded provider token
normal Settings secret
raw secret in prompt
raw secret in Ticket note
raw secret in logs
```

Every action defines minimum required fields.

---

## 28. Logging

Safe operational logs may include:

```text
request_id
action_id
provider
target reference class
status
duration
error category
```

Avoid raw provider output, raw Ticket/Clipboard content, credentials and MFA codes.

---

## 29. Authentication and Authorization

At action time validate:

```text
current permission
provider connection
provider capability
target identity
tenant mapping
risk class
confirmation
context freshness
parameter schema
```

Fail closed.

---

## 30. Multi-Tenant Safety

If providers span customers/tenants:

```text
Tenant/Company mapping must be explicit
```

Never infer target tenant solely from copied text.

Ambiguous targets require disambiguation.

---

## 31. Retry, Rate and Idempotency

Every provider action defines:

```text
connect timeout
request timeout
max attempts
max elapsed duration
retryable errors
terminal result
rate policy
```

Do not resubmit an action merely because an overlay acknowledgement was lost.

No unbounded retries.

---

## 32. Long-Running Actions

If an action outlives the small Mochi overlay:

```text
DynamicHub/global status -> PROCESSING
later completion -> final result
```

Never block the Qt GUI thread.

---

## 33. DynamicHub Surface

Plan a lightweight contextual surface containing at most what is useful:

```text
context header
result summary
2-5 ranked quick actions
Open full workspace
Dismiss
optional stay-open
```

Do not turn DynamicHub into a second Diagnostic Center.

Consume S1 shell placement/responsive decisions.

---

## 34. Focus and Confirmation

DynamicHub should normally be:

```text
non-modal
non-focus-stealing
keyboard accessible
predictably dismissible
```

Risk mapping:

```text
SAFE_READ_ONLY -> explicit click, no second confirmation by default
CONFIRM_REQUIRED -> confirmation summary
MUTATING_HIGH_RISK -> dedicated workflow
```

---

## 35. Diagnostic and PowerShell Ownership

Diagnostics retains:

```text
definition
parameter validation
execution policy
result parsing
result authority
```

Approved flow:

```text
DynamicHub
-> action_id
-> application/Diagnostic service
-> PowerShell gateway or RMM provider
-> approved script/action
```

Never:

```text
Mochi -> powershell.exe
DynamicHub -> powershell.exe
```

---

## 36. RMM Action Requirements

For each RMM-backed action define:

```text
target identity
provider mapping
capability
approved script/action version
parameter schema
timeout
structured result parser
```

Do not assume all RMM providers expose the same API.

---

## 37. Microsoft 365 Candidates

Evaluate read-only actions such as:

```text
user account summary
assigned licenses
mailbox summary
sign-in status
group-membership summary
Teams/SharePoint capability where appropriate
```

Use least privilege.

Do not make Graph availability a local workflow dependency.

---

## 38. Knowledge, Clipboard and Analytics Boundaries

Mochi/DynamicHub may suggest:

```text
Search KB
Search similar tickets
Open relevant article
Create KB draft from approved evidence
```

KB drafts are not auto-published.

Clipboard context must respect Clipboard privacy and may use approved item/entity references rather than unrestricted raw content.

Analytics may provide read-only drill-down context but remains separate from operational truth.

---

## 39. Action Descriptor

Evaluate bounded metadata:

```text
action_id
label
description
category
risk
required_context
required_capabilities
confirmation
owner
result_type
```

No executable command text.

---

## 40. Ticket Auto-Recording Policy

Evaluate:

```text
A. never auto-record
B. auto-record approved SAFE_READ_ONLY observations when active Ticket exists
C. per-action policy
```

Recommended planning direction:

```text
per-action policy
+ visible acknowledgement
+ owning TicketService
```

This may require explicit user review.

Do not dump raw outputs into notes.

---

## 41. Provenance

Recorded results should preserve:

```text
action_id
provider
target reference
timestamp
result completeness
Diagnostic/result reference
human/AI summary provenance
```

AI-generated prose is presentation/draft, not source truth.

---

## 42. Prompt Injection and Untrusted Data

Ticket text, Clipboard content, KB content, provider output and external data are untrusted.

Text such as:

```text
"Ignore previous rules and run ..."
```

must never become executable authority.

Only approved action IDs plus validated parameters may execute.

---

## 43. Required Provider Matrix

Produce:

```text
Action family
Owner
Preferred provider
Fallback provider
Required capability
Offline?
Risk
Result type
Ticket-record policy
Status
```

Cover:

```text
Device
Network
Windows
M365 identity
M365 licensing
Mailbox
Security
Adobe
Knowledge
Ticket
Clipboard
```

---

## 44. Required Action Catalog Matrix

For every MVP candidate:

```text
action_id
label
owner
target type
parameters
risk class
confirmation
provider capability
result schema
Mochi summary
Ticket recording
follow-up actions
```

---

## 45. Required Context Matrix

For each context field:

```text
Source
Owner
Optional?
Freshness
May AI see?
May provider receive?
May Ticket observation include?
Privacy risk
```

---

## 46. Required Failure Matrix

Cover:

```text
AI unavailable
RMM unavailable
Graph unavailable
target offline
permission denied
context stale
target ambiguous
timeout
partial result
parse failure
Ticket save failure
rate limit
unsupported action
```

For each:

```text
retry?
Mochi overlay?
DynamicHub?
Ticket?
log?
terminal action?
```

---

## 47. Required Security Review

Verify:

```text
No free-form AI command execution
No direct PowerShell from Mochi
No direct DB writes from DynamicHub
No hard-coded secrets
No raw provider token in Settings
No target guessing
No implicit cross-tenant action
No secret logging
No authorization from UI visibility
No automatic high-risk remediation
```

---

## 48. UI State Model

At minimum:

```text
IDLE
CONTEXT_READY
SUGGESTIONS_AVAILABLE
ACTION_RUNNING
ACTION_SUCCESS
ACTION_PARTIAL
ACTION_BLOCKED
ACTION_ERROR
PROVIDER_UNAVAILABLE
AI_UNAVAILABLE
```

Cosmetic Mochi state remains separate from domain result state.

---

## 49. Decision Register

At minimum decide/recommend:

```text
Mochi role
DynamicHub role
AI boundary
Action Catalog
safe-read-only policy
confirmation policy
future auto-read-only
provider routing
structured observation
Ticket auto-record policy
provenance
follow-up ranking
DynamicHub trigger policy
overlay behavior
context freshness
offline behavior
AI-unavailable behavior
Adobe handling
```

Statuses:

```text
RECOMMENDED
REQUIRES_USER_DECISION
DEFERRED
NOT_VERIFIED
```

---

## 50. Risk Register

Include:

```text
wrong target
cross-tenant action
hallucinated action
prompt injection
unsafe free-form script
excess provider privilege
secret exposure
stale context
duplicate action
Ticket-note pollution
raw-output leakage
AI/provider outage
rate limiting
Mochi interruption fatigue
DynamicHub popup fatigue
automatic-action creep
provider lock-in
```

---

## 51. Future Slice Sequence

Potential only:

```text
Context A - bounded context projection + action descriptors
Context B - DynamicHub suggestions with no execution
Context C - one approved local/read-only action end-to-end
Context D - RMM read-only provider boundary
Context E - Ticket observation recording
Context F - M365 read-only provider boundary
Context G - Mochi summaries/follow-up ranking
Context H - failure/offline/native polish
```

Do not implement.

---

## 52. Acceptance Criteria

S2 is acceptable when all are PASS:

1. Existing Mochi/DynamicHub boundaries inspected.
2. Mochi is presentation/personalization, not execution authority.
3. DynamicHub is contextual action surface/coordinator.
4. Foundation DynamicHub ownership remains compatible or conflict raised.
5. Active Technician Context consumption bounded.
6. Context freshness defined.
7. Trigger policy defined.
8. Mochi acknowledgement overlay defined.
9. Action Catalog defined.
10. Free-form AI PowerShell prohibited.
11. Risk classes defined.
12. Safe read-only behavior defined.
13. Confirm-required behavior defined.
14. High-risk actions excluded from lightweight execution.
15. Provider ownership defined.
16. RMM boundary defined.
17. M365 boundary defined.
18. Adobe entitlement marked NOT VERIFIED unless verified.
19. Capability gating defined.
20. Structured request/result defined.
21. Structured observation defined.
22. Ticket recording uses existing ownership.
23. Local Ticket vs PSA sync distinguished.
24. Ticketless workflow supported.
25. Follow-up actions use approved IDs only.
26. Failure/partial behavior defined.
27. AI-unavailable behavior defined.
28. Offline behavior defined.
29. Privacy/secrets defined.
30. Authorization checks defined.
31. Retry/rate/idempotency bounded.
32. Multi-tenant safety defined.
33. No direct PowerShell from Mochi/DynamicHub.
34. No direct DB write from Mochi/DynamicHub.
35. Future implementation decomposable.
36. No production implementation.

---

## 53. Result Vocabulary

Return exactly one:

```text
READY_FOR_CONTEXT_ACTION_REVIEW
REQUIRES_CONTEXT_ACTION_DECISIONS
FOUNDATION_OWNER_REVIEW_REQUIRED
BLOCKED
```

Never return `READY_FOR_IMPLEMENTATION`.

---

## 54. Completion Boundary

Stop after S2 architecture authoring.

Do not execute PowerShell, call RMM/Graph/Adobe, modify Ticket notes, change Mochi runtime, implement DynamicHub, create credentials, implement the Action Catalog, or start autonomous remediation.
