# F7Hub Workspace Planning S2
# Mochi, DynamicHub & Context-Aware Action Architecture

> **Planning status:** `NOT_STARTED`
>
> **Mode:** `@ARCHITECT @PLAN`
>
> **Proposed repository path:** `Docs/Planning/Workspace/S2_Mochi_DynamicHub_Context_Actions.md`
>
> **Purpose:** Define Mochi as the personalized presentation of F7Hub's local IT AI sublayer and DynamicHub as its contextual action surface, while execution, persistence, security and provider authority remain behind approved F7Hub services/gateways.

---

## 1. Why This Phase Exists

F7Hub should help a technician move from current context to a safe next action quickly.

Conceptual flow:

```text
Active Ticket
+ User
+ Device
+ Clipboard / Diagnostic context
        ↓
Mochi
        ↓
DynamicHub suggestions
        ↓
approved action
        ↓
RMM / Microsoft / other provider
        ↓
structured result
        ↓
F7Hub observation / Ticket association
        ↓
Mochi acknowledgement
        ↓
next suggested actions
```

The experience may feel intelligent and immediate, but the architecture must remain deterministic about who authorizes, who executes, what data is sent, what may be automated, where results are stored and what requires confirmation.

AI-generated text is never execution authority.

---

## 2. Dependency Gate

Before execution verify:

```text
Foundation 0A–0E  CLOSED
Workspace S1       APPROVED / CLOSED
```

Also consume approved feature architecture relevant to the action:

```text
Clipboard
Diagnostics when approved
Tickets
Knowledge
Scripts / PowerShell
Settings architecture
```

If S1 is not approved:

```text
RESULT = BLOCKED
```

because DynamicHub placement, Active Technician Context and shell ownership remain unstable.

---

## 3. Foundation Compatibility

Approved Foundation 0A-D1 establishes that DynamicHub may coordinate interactive troubleshooting through owning services/gateways while Diagnostics retains diagnostic definition, execution and result authority.

This plan specializes the UX role:

```text
DynamicHub
= contextual action/presentation surface

Mochi
= personalized assistant presentation

Local IT AI sublayer
= context analysis / ranking / explanation

Owning application services
= authorization and domain behavior

Gateways/providers
= external execution/integration
```

This must not transfer business, security, persistence or execution authority to Mochi/DynamicHub.

If a real conflict with approved Foundation exists, record `FOUNDATION_CONFLICT` and route it to the owner.

---

## 4. Explicit USER Requirements

1. Mochi is personalization/presentation of the local IT AI sublayer, not a separate business authority.
2. DynamicHub becomes Mochi's contextual popup/action surface.
3. DynamicHub should appear conveniently when context makes useful next actions obvious.
4. Mochi may acknowledge completed work with a short nearby text overlay.
5. Future provider access may include an RMM API.
6. F7Hub should support lightweight remote Windows/PowerShell information gathering through approved providers.
7. Microsoft 365 facts should use appropriate approved Microsoft boundaries.
8. Adobe license capability may be supported if a safe authorized API/provider exists.
9. Useful results may be recorded in F7Hub Ticket notes/timeline/observations.
10. DynamicHub should suggest useful follow-up actions from structured results.
11. AI must not send arbitrary invented PowerShell directly to managed endpoints.
12. Mutating/high-risk actions remain explicit, technician-controlled workflows.

---

## 5. Scope

Design:

```text
Mochi role
local IT AI sublayer role
DynamicHub role
context projection
context freshness
Action Catalog
action ranking
action safety classes
provider capability model
RMM action routing
Microsoft 365 action routing
future Adobe capability
PowerShell action boundary
structured results
Ticket observation/note behavior
Case Journal fallback
short Mochi overlays
DynamicHub trigger rules
cooldowns
focus behavior
privacy
security
provider failure
idempotency / reconciliation
audit / provenance
offline behavior
confirmation policy
future bounded automation
testing strategy
future vertical slices
```

---

## 6. Out of Scope

Do not implement:

```text
AI model/provider
RMM API
Microsoft Graph
Exchange API
Adobe API
PowerShell scripts
DynamicHub popup
Mochi AI logic
Ticket note automation
database migrations
Action Catalog
Settings
provider credentials
automatic remediation
```

Do not choose a specific RMM vendor unless separately scoped and inspected.

Do not assume Adobe entitlement APIs are available.

---

## 7. Required Inspection

Inspect at minimum:

```text
ROOT.md
Foundation 0A / 0B / 0C / 0D / 0E
Docs/Planning/AGENTS.md
Workspace S1

Mochi/AGENTS.md
Mochi/README.md
Mochi/docs/Architecture.md
current Mochi protocol/channel/gateway/service

TicketService
Ticket notes/timeline/associations
Case Journal planning if present

PowerShellService
script registry
diagnostic registry/pack architecture
approved PowerShell execution boundary

current gateway/provider patterns
current logging/security patterns
```

Inspect Diagnostics architecture if approved.

Use:

```text
SEARCH → IDENTIFY → REUSE / EXTEND → CREATE ONLY IF NECESSARY
```

Classify findings:

```text
FACT
ASSUMPTION
INFERENCE
RECOMMENDATION
NOT VERIFIED
```

---

## 8. Role Model

### Local IT AI Sublayer

May:

```text
interpret eligible current context
summarize
rank approved actions
explain structured results
suggest next steps
form bounded action requests
```

Must not:

```text
own Ticket state
own provider credentials
write database directly
run arbitrary PowerShell
grant permissions
invent provider capabilities
bypass confirmation policy
```

### Mochi

Provides:

```text
personality
visual presence
short acknowledgements
contextual prompts
attention cues
```

Mochi remains optional.

### DynamicHub

Provides:

```text
context summary
ranked approved actions
action state
result summary
follow-up actions
```

DynamicHub is bounded and non-modal.

### Owning Services

Examples:

```text
TicketService
DiagnosticService
KnowledgeService
ClipboardService
future Action/Automation service
provider gateways
```

These remain authoritative.

---

## 9. Context Input Model

DynamicHub/Mochi may receive approved projections of:

```text
Active Company
Active User
Active Device
Active Ticket
selected Clipboard Item
selected Entity
selected Diagnostic result
selected KB article
selected Script metadata
current workspace/module
recent approved observations
```

Rules:

1. References/projections, not copied domain records.
2. Include freshness/version where necessary.
3. Revalidate before execution/mutation.
4. Context is not permission.
5. No automatic raw secret exposure.
6. Context may be incomplete.
7. Provider actions bind explicitly to target.
8. Stale Ticket/device targeting fails closed.
9. AI cannot retarget solely from prose.

---

## 10. Context Projection

Consume S1 Active Technician Context instead of creating a competing global context system.

A safe projection may contain:

```text
context_id
revision
active references
safe display labels
capability summary
selected evidence references
privacy flags
```

DynamicHub consumes this projection.

---

## 11. Context Freshness

Every action with an external effect should bind to:

```text
context revision
target reference
action key
provider capability state
```

Before execution, owning services revalidate:

```text
target exists
target still matches intended user/device/tenant
capability available
permission valid
confirmation current
```

Do not execute against stale UI context.

### Invocation-Time Operation Binding

**The action's invocation context is immutable for that operation.** When an
approved action is invoked, the owning service captures the authoritative
references and decision inputs for its lifetime, including:

```text
operation_id
action_key
invocation-time context revision
invocation-time target reference(s)
tenant / provider scope where applicable
optional Ticket association choice and exact Ticket reference
capability and safety decision inputs
requesting technician and required provenance
```

Changing the current Active Technician Context or Active Ticket Context after
invocation is navigation/presentation state only. It MUST NOT retarget an
in-flight operation or rewrite its Ticket association. The current selection
is never completion-time authority.

A result that completes after the technician has changed context remains a
valid late result when its execution outcome is valid. Keep it bound to the
invocation-time target and any invocation-time Ticket association; preserve
provenance; do not switch the technician's current context or overwrite the
new context's UI as though the result belongs to it. Surface that the result
belongs to a different/stale displayed context, allow explicit navigation to
its originating target or Ticket, and permit viewing the result without
implying it belongs to the currently active context. Exact visual treatment is
deferred to S1/S2 execution and UI design.

If an invocation-time target, tenant/provider scope, or captured Ticket
reference becomes unavailable or invalid, fail or reconcile truthfully through
the owning service. Never substitute whatever target or Ticket is currently
active.

---

## 12. Action Catalog

The primary safety mechanism is an approved Action Catalog.

Conceptual metadata:

```text
action key
display name
description
owner subsystem
safety class
target types
input schema
capability requirements
provider strategy
result schema
timeout
confirmation policy
audit policy
Ticket-recording policy
follow-up rules
```

Example stable action keys:

```text
network.snapshot
network.ping_gateway
network.dns_configuration
device.uptime
device.disk_free
device.services_summary
m365.user_summary
m365.license_summary
m365.mailbox_summary
security.signin_summary
```

AI selects approved action keys, not executable strings.

---

## 13. No Arbitrary AI PowerShell

Hard invariant:

```text
AI-generated PowerShell text
≠
authorized execution
```

Forbidden:

```text
Mochi / LLM
→ generated script string
→ RMM
→ customer device
```

Approved pattern:

```text
Mochi / DynamicHub
→ action key + validated parameters
→ owning application service
→ approved Action/Diagnostic Catalog
→ approved versioned implementation
→ provider gateway
→ structured result
```

---

## 14. Action Safety Classes

### SAFE_READ_ONLY

Examples:

```text
IP configuration
DNS configuration
uptime
disk free space
memory summary
adapter status
installed application version
license-read query
mailbox-read query
sign-in-read query
```

No mutation intended.

### CONFIRM_REQUIRED

Examples:

```text
restart approved service
flush DNS
renew approved network operation
start/stop approved process/service
```

Technician confirmation required.

### HIGH_RISK / MUTATING

Examples:

```text
uninstall software
change policy
disable account
remove license
modify mailbox settings
device reset
security-policy mutation
```

Requires separately reviewed workflow and explicit confirmation.

---

## 15. Default Automation Level

Initial recommendation:

```text
SUGGEST_ONLY
or
ONE_CLICK_SAFE_READ_ONLY
```

Do not start with autonomous remote execution.

A future opt-in level may be considered:

```text
AUTO_SAFE_READ_ONLY
```

only with:

```text
allowlisted actions
allowlisted contexts
fresh target binding
capability verification
strict timeout
structured result
audit trail
rate limit
clear USER opt-in
```

Mutating actions never inherit automation automatically.

---

## 16. Provider Capability Model

DynamicHub must not assume every provider supports every action.

Conceptually model:

```text
provider_id
provider_type
tenant/customer scope
supported action keys
read/write classification
permission state
health/availability
freshness
```

Capabilities are checked near execution.

A stale capability flag is not permanent authority.

---

## 17. RMM Gateway

Future flow:

```text
DynamicHub action
→ application service
→ capability check
→ RMM gateway
→ approved remote action/script
→ structured result
```

RMM is an execution provider, not domain authority.

Vendor-specific responses should normalize into F7Hub DTOs.

No RMM API details in GUI/Mochi.

---

## 18. Lightweight PowerShell via RMM

If an RMM uses PowerShell for read-only diagnostics:

1. Action/script predefined and reviewed.
2. Parameters schema-validated.
3. No shell-string concatenation from AI output.
4. Least privilege.
5. Bounded timeout.
6. Bounded output size.
7. Structured parsing.
8. Raw output handled according to privacy policy.
9. Explicit exit/error state.
10. Provider execution ID retained where useful.
11. Retries cannot duplicate unsafe effects.
12. Action/script version/provenance retained.

---

## 19. Microsoft 365 Boundary

Use the most appropriate approved Microsoft gateway rather than routing everything through endpoint PowerShell.

Potential providers:

```text
Microsoft Graph
Exchange Online
Entra ID
other approved Microsoft APIs
```

Examples:

```text
user existence/status
assigned licenses
mailbox summary
sign-in summary
group membership summary
device registration summary
```

Respect least privilege, tenant identity, scopes, rate limits, privacy and provider freshness.

---

## 20. Adobe License Capability

Treat Adobe entitlement/license information as:

```text
NOT VERIFIED
```

until an authorized API/provider and permission model are inspected.

Important distinction:

```text
Adobe application installed
≠
Adobe entitlement/license assigned
```

RMM installed-software inventory must not be treated as authoritative licensing evidence.

Only expose Adobe license actions when verified capability exists.

---

## 21. Provider-Neutral Actions

Prefer:

```text
device.network_snapshot
```

over vendor-specific UI/domain keys such as:

```text
VendorXRunScript17
```

Provider adapters translate approved actions.

---

## 22. Action Request Contract

Conceptual request:

```text
operation_id
action_key
context_revision
target_ref
tenant / provider scope where applicable
optional invocation-time Ticket association choice/reference
validated parameters
requested_by
confirmation state
capability snapshot reference
```

Do not include raw credentials, arbitrary executable strings or unbounded raw Clipboard content.

Consume the global interoperability grammar.

---

## 23. Action Result Contract

Conceptual result:

```text
operation_id
action_key
target_ref
invocation context revision and binding correlation
captured tenant / provider scope where applicable
status
started_at
completed_at
provider
provider_execution_ref
structured observations
safe summary
warnings
partial/completeness state
provenance
```

Distinguish:

```text
success
partial
blocked
failed
timeout
uncertain
unsupported
unauthorized
```

Provider dispatch alone is not success.

---

## 24. Result Normalization

Each action defines a result schema.

Example network snapshot:

```text
hostname
interfaces[]
ipv4[]
ipv6[]
gateways[]
dns_servers[]
link_state
wifi_signal if available
warnings[]
```

Mochi should summarize normalized data rather than treating arbitrary console text as the primary result.

---

## 25. Ticket Recording Model

Do not silently append raw command output into a technician-authored note.

Prefer a distinguishable system-generated observation/event, for example:

```text
[Network Snapshot]
Device: CONTOSO-LT042
IPv4: 192.168.10.42
Gateway: 192.168.10.1
DNS: 10.0.0.10, 10.0.0.11
Adapter: Intel Wi-Fi
Result: Gateway reachable
Source: RMM / network.snapshot
Time: 19:43
```

Reuse current Ticket note/timeline/evidence architecture before creating new persistence.

---

## 26. Note vs Observation vs Evidence

Distinguish:

### Technician Note
Human-authored content.

### System Observation
Structured/generated result summary.

### Evidence
Accepted relationship/provenance with retention meaning.

They may appear in one Ticket timeline without becoming the same semantic thing.

---

## 27. Ticket Association

If an Active Ticket exists and the technician intentionally runs an action in that context, the result may associate through Ticket/association services.

That choice and the exact Ticket reference are captured at invocation. On
completion, association is permitted only with that captured reference; never
infer a Ticket from the then-current Active Ticket Context. If no Ticket
association was selected at invocation, do not silently associate with a
Ticket that becomes active later. Any later association is a separate,
explicit user/service operation with normal validation.

If no Ticket exists:

```text
result remains in owning domain / Case Journal / Diagnostic result
```

and may be associated later.

Ticket association is optional to local troubleshooting.

---

## 28. Automatic Ticket Recording Policy

Initial recommendation:

```text
explicit or policy-controlled recording
```

A future policy may auto-record concise safe read-only observations only after:

```text
USER opt-in
clear source labeling
context freshness
successful target validation
confirmed result
privacy policy
Settings implementation
```

External PSA publication remains a separate decision.

---

## 29. Short Mochi Acknowledgement

Mochi may show a compact non-modal overlay, e.g.:

```text
Network snapshot collected.
Saved to INC-10452.

M365 license check complete.
2 assigned licenses found.

Device query failed.
RMM is unavailable.
```

Rules:

```text
short
truthful
privacy-safe
no raw secrets
no focus theft
bounded lifetime
accessible equivalent
```

Detailed results belong in DynamicHub/workspace/Ticket.

---

## 30. DynamicHub Surface

DynamicHub is a contextual action surface, not a full independent business module by default.

Candidate sections:

```text
Context
What happened
Suggested next actions
Recent result
Warnings / unavailable capabilities
Open full tool
```

Consume the region reserved by S1.

---

## 31. DynamicHub Trigger Rules

Potential triggers:

```text
USER explicitly opens Mochi/DynamicHub
important active-context change
selected actionable Entity
diagnostic/action completes
provider failure needs recovery
new result yields obvious next steps
```

Do not trigger on:

```text
every hover
every keystroke
every Clipboard change
every timer tick
```

---

## 32. Trigger Restraint / Cooldown

Plan:

```text
one DynamicHub surface at a time
deduplicate repeated suggestions
cooldown repeated informational prompts
respect explicit dismissal
do not steal keyboard focus
```

Exact timing may be later Settings/slice detail.

---

## 33. Suggestion Ranking

AI may rank only approved available actions.

Possible ranking inputs:

```text
current issue
selected Entity
recent structured results
active target
action prerequisites
provider availability
past action outcome in current case
privacy/safety class
```

Ranking never overrides permissions, capability or confirmation policy.

---

## 34. Follow-Up Rules

Action definitions may declare safe semantic follow-ups.

Example:

```text
network.snapshot
→ DNS servers present: suggest network.test_dns
→ gateway missing: suggest adapter/status checks
→ Wi-Fi weak: suggest wifi.details
```

AI may rank/explain, but follow-ups still resolve to approved action keys.

---

## 35. No Hidden Execution

DynamicHub appearance, hover and Mochi animation do not execute actions.

Execution begins only via:

```text
explicit USER action
or
future separately approved AUTO_SAFE_READ_ONLY policy
```

---

## 36. Mutating Confirmation

For side-effect actions show:

```text
action
target
effect
safety class
provider
confirmation requirement
```

Confirmation binds to the same validated target/action revision.

Stale confirmation cannot be replayed against another target.

---

## 37. Secrets

Never expose through Mochi/DynamicHub:

```text
API keys
tokens
passwords
private keys
RMM secrets
Graph client secrets
refresh tokens
provider credentials
```

Mochi consumes capability/result projections, not credentials.

---

## 38. Privacy

Use bounded projections.

Do not send entire Ticket histories, full logs, raw secret Clipboard content or unnecessary customer data where a smaller projection suffices.

External AI/provider processing requires approved privacy rules.

Local F7Hub workflows remain useful offline where possible.

---

## 39. Logging

Safe operational logs may include:

```text
operation_id
action_key
target reference
provider category
duration
status
error category
```

Do not log credentials, raw secrets, unbounded command output or private Ticket note text by default.

---

## 40. Offline Behavior

When remote providers are unavailable, local capabilities such as Ticket work, Clipboard, Knowledge, local notes and approved local diagnostics should continue where architecture permits.

DynamicHub marks remote actions `UNAVAILABLE` rather than failing the whole application.

---

## 41. Provider Failure States

Plan:

```text
provider unavailable
authentication expired
permission denied
target offline
timeout
partial result
malformed result
unsupported action
rate limited
uncertain execution
```

For each define retry, user message, Ticket behavior, DynamicHub recovery and audit/log behavior.

No infinite retries.

---

## 42. Idempotency / Reconciliation

Every external action has an operation identity.

Do not equate same action key with same operation.

If provider accepts an action but response is lost:

```text
do not blindly rerun a mutating action
```

Use provider execution reference/status reconciliation where possible or report `UNCERTAIN`.

Mochi must not say "Done" without confirmation.

---

## 43. Facts vs Interpretation

Structured provider result is factual input.

Mochi explanation is derived interpretation.

Presentation should distinguish:

```text
Observed
Inferred
Suggested
```

Generated prose never overwrites the structured result.

---

## 44. Action Provenance

Retain enough provenance for support/audit:

```text
action key
action version
provider
target
requesting user/context
timestamps
result status
provider execution reference
script/action version where relevant
```

Exact persistence belongs to owning feature design.

---

## 45. Least Privilege / Cross-Tenant Safety

Provider access must use least privilege.

DynamicHub availability must consider:

```text
provider connected?
scope sufficient?
target eligible?
action allowed?
tenant/customer boundary valid?
```

Do not infer tenant/device/user IDs from display names or prose when authoritative mappings exist.

Target mismatch blocks execution. Invocation-time target and tenant/provider
scope remain authoritative for the operation even if the technician changes
context while it runs. A context switch cannot transform an in-flight
operation into another tenant or provider target.

---

## 46. Provider Identifier Resolution

External IDs are resolved through approved mappings/adapters.

AI must not fabricate:

```text
device ID
tenant ID
user ID
mailbox ID
```

Provider parameters come from validated identifiers.

---

## 47. RMM Result to Ticket Flow

Required conceptual flow:

```text
DynamicHub
→ approved action request
→ Action/Application Service
→ capability + target validation
→ RMM Gateway
→ approved remote action
→ normalized result
→ owning result/observation service
→ optional Ticket association
→ Mochi acknowledgement
→ follow-up suggestions
```

No direct `DynamicHub → RMM` path.

---

## 48. M365 Result to Ticket Flow

```text
DynamicHub
→ approved M365 action key
→ Microsoft application/integration service
→ Graph/Exchange/etc gateway
→ normalized result
→ optional Ticket observation
→ Mochi acknowledgement
→ follow-up suggestions
```

No raw Microsoft API calls from GUI/Mochi.

---

## 49. Adobe Flow

Until verified:

```text
Adobe license query = FUTURE / NOT VERIFIED
```

If later supported:

```text
DynamicHub
→ adobe.license_summary
→ capability check
→ Adobe/integration gateway
→ structured entitlement result
```

Installed-product inventory is not entitlement authority.

---

## 50. DynamicHub Action Cards

Each suggested action should conceptually expose:

```text
label
why suggested
target
safety indicator
provider/source
availability
confirmation state
```

Prefer a small ranked set such as top 3–5 actions plus `More` rather than a wall of buttons.

---

## 51. Action Feedback States

Define:

```text
READY
RUNNING
SUCCEEDED
PARTIAL
FAILED
BLOCKED
UNAVAILABLE
UNCERTAIN
```

Long actions must not freeze MainWindow.

---

## 52. Ticket Write Failure Is Separate

If remote action succeeds but Ticket recording fails:

```text
Action result = SUCCEEDED
Ticket recording = FAILED
```

Offer recovery such as:

```text
Retry Ticket recording
Open Result
Copy Safe Summary
```

Retrying Ticket write must not rerun the remote action. Retry only the
recording/association step, using the original invocation-time Ticket
reference and normal existence, authorization and freshness validation. Never
use the Ticket currently active at retry time; if the captured reference is no
longer valid, report that failure without retargeting.

---

## 53. Mochi / DynamicHub Optionality

If Mochi renderer is unavailable, F7Hub actions should still work through owning services where possible.

If DynamicHub UI is unavailable, the Action Catalog/services remain independent.

Do not implement provider execution only inside a widget.

---

## 54. Settings Inputs

Potential future Settings:

```text
Mochi enabled
DynamicHub enabled
suggestion verbosity
acknowledgement duration
auto-open on important result
provider feature flags
AUTO_SAFE_READ_ONLY opt-in
automatic local Ticket observation policy
```

Do not store secrets/tokens/runtime handles/provider credentials as ordinary Settings.

Settings can affect presentation/enablement, not redefine action meaning, permission or provider security.

---

## 55. UI Placement

Consume S1 shell architecture.

DynamicHub should use the approved contextual region/temporary side surface.

Mochi short overlays may appear near the pet but remain tiny/non-modal.

Avoid proliferating independent desktop windows.

---

## 56. Accessibility

Require:

```text
keyboard access
visible focus
non-color-only safety state
accessible action labels
equivalent text for Mochi overlay
reasonable interaction time
dismiss without losing work
```

Animation is never the sole success/failure indicator.

---

## 57. Performance / Rate Control

Opening DynamicHub should not itself require provider calls.

Use local bounded context/capability state for initial suggestions.

Provider calls occur only on explicit action or separately approved automation.

AI inference must not block MainWindow navigation.

Provider actions need bounded rate/retry behavior. Suggestion UI needs deduplication/cooldown and dismissal respect.

---

## 58. Required Capability Matrix

For every action category provide:

```text
Action key
Purpose
Target type
Safety class
Owning service
Potential provider
Capability required
Confirmation
Result schema
Ticket-recording policy
Offline?
MVP / Later / Not Verified
```

Include representative Network, Device, Microsoft 365, Security and Adobe rows.

---

## 59. Required Provider Matrix

For:

```text
RMM
Microsoft Graph
Exchange Online
local PowerShell/Diagnostics
Adobe/licensing provider
```

define:

```text
authority
credentials owner
capability discovery
target mapping
request boundary
result normalization
rate/failure behavior
offline behavior
NOT VERIFIED items
```

---

## 60. Required Action Safety Matrix

For representative actions define:

```text
action
read-only?
side effects?
safety class
confirmation
auto-safe eligible?
Ticket record?
audit?
```

No auto-safe eligibility merely because an action sounds harmless.

---

## 61. Required Ticket Recording Matrix

For:

```text
successful read-only action
partial action
failed action
uncertain action
mutating action
provider unavailable
```

define:

```text
local result record
Ticket observation
technician note
evidence
external PSA sync
Mochi acknowledgement
```

External PSA sync should normally remain separate/deferred.

---

## 62. Required DynamicHub Trigger Matrix

For each trigger define:

```text
trigger
opens automatically?
suggestion only?
focus?
cooldown?
dismissal behavior?
privacy risk?
```

Cover context change, Entity selection, action completion/failure, provider unavailable, USER open and USER dismiss.

---

## 63. Required Context Matrix

For:

```text
Company
User
Device
Ticket
Tenant
Clipboard Item
Entity
Diagnostic result
Knowledge article
Script
```

define:

```text
reference source
safe projection
freshness
required validation
AI exposure
provider exposure
Ticket use
```

---

## 64. Required Security Review

Explicitly confirm:

```text
No arbitrary AI-generated PowerShell execution
No direct DynamicHub provider calls
No direct GUI database writes
No provider credentials exposed to Mochi
No permission inferred from visibility
No stale-target execution
No autonomous mutating actions
No raw secret logging
No blind retry of uncertain mutation
No cross-tenant inference
```

Any violation blocks approval.

---

## 65. Required Failure Matrix

Cover:

```text
no active target
stale context
provider disconnected
provider auth expired
provider permission denied
target offline
timeout
partial result
malformed result
Ticket write failure
Mochi unavailable
DynamicHub unavailable
AI unavailable
rate limit
uncertain provider execution
```

For each define action status, retry, Ticket behavior, Mochi message, DynamicHub behavior and log/audit policy.

---

## 66. Required Diagrams

Produce Mermaid source for:

1. Context → Mochi → DynamicHub suggestion flow.
2. DynamicHub → Action Catalog → provider execution flow.
3. RMM PowerShell read-only flow.
4. Microsoft 365 query flow.
5. Result → Ticket observation → Mochi acknowledgement.
6. Failure/uncertain-outcome reconciliation.
7. Capability → action availability relationship.

---

## 67. Decision Register

At minimum decide:

```text
Mochi role
DynamicHub role
Action Catalog ownership
context projection ownership
suggestion ranking
default automation level
safe-read-only class
confirmation classes
provider capability model
RMM routing
M365 routing
Adobe deferral
Ticket recording default
short acknowledgement
auto-open trigger policy
cooldowns
uncertain-outcome behavior
AI-unavailable behavior
```

Record Decision, Options, Recommendation, Evidence, Rationale, Consequences, Planning Depth and Status.

Allowed statuses:

```text
RECOMMENDED
REQUIRES_USER_DECISION
DEFERRED
NOT_VERIFIED
```

---

## 68. Risk Register

Include:

```text
AI hallucinated action
arbitrary script execution
wrong target
wrong tenant
stale context
provider over-privilege
credential leakage
privacy leakage
duplicate remote execution
uncertain mutation
Ticket note spam
incorrect Ticket association
provider rate limit
slow provider response
DynamicHub nagging
Mochi focus theft
too many suggested actions
unsafe future autonomy
provider-specific coupling
Adobe license misinterpretation
AI/provider offline dependency
testing loops
```

---

## 69. Future Vertical Slices

May recommend but not implement small slices such as:

```text
CTX-01 context projection
ACT-01 Action Catalog metadata/read path
ACT-02 DynamicHub static action cards
ACT-03 safe local diagnostic action
ACT-04 structured result + acknowledgement
ACT-05 Ticket observation association
RMM-01 provider capability adapter
RMM-02 one approved read-only device action
M365-01 one approved read-only identity/license query
DH-01 context-aware ranking
DH-02 follow-up suggestion rules
AI-01 optional local AI explanation
AUTO-01 future opt-in AUTO_SAFE_READ_ONLY experiment
```

Actual numbering follows repository governance.

Never bundle Mochi + RMM + Graph + Ticket writing + AI automation into one slice.

---

## 70. Acceptance Criteria

S2 is acceptable when:

1. Mochi role explicit.
2. Local IT AI role explicit.
3. DynamicHub role explicit.
4. DynamicHub is not execution authority.
5. Foundation 0A-D1 ownership preserved.
6. S1 shell consumed.
7. Active Technician Context consumed, not duplicated.
8. Context freshness defined.
9. Target validation defined.
10. Action Catalog defined.
11. Arbitrary AI PowerShell prohibited.
12. Safety classes defined.
13. Default automation level defined.
14. Future auto-safe path bounded.
15. Provider capability model defined.
16. RMM gateway role defined.
17. Approved PowerShell-via-RMM path defined.
18. M365 provider boundary defined.
19. Adobe remains NOT VERIFIED unless proven.
20. Provider-neutral action keys defined.
21. Action request contract defined.
22. Action result contract defined.
23. Structured normalization defined.
24. Ticket recording semantics defined.
25. Note vs observation vs evidence distinguished.
26. Ticketless behavior defined.
27. Mochi acknowledgement defined.
28. DynamicHub trigger policy defined.
29. Cooldown/dismissal behavior defined.
30. Suggestions bounded to approved actions.
31. Follow-ups use approved action keys.
32. Mutating confirmation defined.
33. Secrets boundary explicit.
34. Privacy projection explicit.
35. Logging restrictions explicit.
36. Offline behavior defined.
37. Provider failure behavior defined.
38. Idempotency/reconciliation defined.
39. Uncertain outcomes cannot fake success.
40. Provenance defined.
41. Least privilege required.
42. Cross-tenant safety defined.
43. Provider ID resolution validated.
44. Ticket write retry does not rerun remote action.
45. Mochi optional.
46. DynamicHub UI optional to action services.
47. Settings inputs classified.
48. Required matrices complete.
49. Security review passes.
50. Risk register complete.
51. Future slices small.
52. No production implementation occurred.
53. No credentials/secrets added.
54. No database migration occurred.
55. No provider falsely claimed available.

For a positive result:

```text
55/55 PASS
```

at architecture-planning depth.

---

## 71. Validation Summary

```text
Current Mochi inspection                 PASS / FAIL / BLOCKED
Foundation compatibility                 PASS / FAIL / BLOCKED
S1 shell compatibility                   PASS / FAIL / BLOCKED
Context architecture                     PASS / FAIL / BLOCKED
Action Catalog                           PASS / FAIL / BLOCKED
Safety classes                           PASS / FAIL / BLOCKED
RMM boundary                             PASS / FAIL / BLOCKED
PowerShell safety                        PASS / FAIL / BLOCKED
M365 boundary                            PASS / FAIL / BLOCKED
Adobe boundary                           PASS / FAIL / BLOCKED
Ticket recording                         PASS / FAIL / BLOCKED
DynamicHub UX                            PASS / FAIL / BLOCKED
Mochi acknowledgement                    PASS / FAIL / BLOCKED
Provider failure/reconciliation          PASS / FAIL / BLOCKED
Privacy/security                         PASS / FAIL / BLOCKED
Offline behavior                         PASS / FAIL / BLOCKED
Settings boundary                        PASS / FAIL / BLOCKED
Testing strategy                         PASS / FAIL / BLOCKED
Scope control                            PASS / FAIL / BLOCKED
Production changes                       MUST BE NONE
Database changes                         MUST BE NONE
Credential changes                       MUST BE NONE
```

---

## 72. Required Execution Report

When executed, append `# EXECUTION REPORT` containing at minimum:

```text
Summary
Baseline / Candidate Identity
Approved Inputs
Repository Areas Inspected
Verified Current Mochi / AI State
Foundation Compatibility
S1 Shell Compatibility
Role Model
Context Architecture
Context Freshness
Action Catalog
Action Safety Classes
Automation Levels
Provider Capability Model
RMM Architecture
PowerShell-via-RMM Boundary
Microsoft 365 Architecture
Adobe Capability Assessment
Action Request / Result Contracts
Result Normalization
Ticket Recording
Case Journal / Ticketless Behavior
Mochi Acknowledgement
DynamicHub Surface
Trigger / Cooldown Model
Suggestion Ranking
Follow-Up Actions
Security
Privacy
Offline Behavior
Provider Failures
Idempotency / Reconciliation
Settings Inputs
Required Matrices
Required Diagrams
Decision Register
Requires User Decision
Assumptions
Not Verified
Risk Register
Recommended Vertical Slices
Downstream Architecture Inputs
Acceptance Criteria
Validation
Result
```

---

## 73. Result Vocabulary

Return exactly one:

```text
READY_FOR_DYNAMIC_CONTEXT_REVIEW
REQUIRES_DYNAMIC_CONTEXT_DECISIONS
BLOCKED
```

Never return `READY_FOR_IMPLEMENTATION`.

---

## 74. Completion Boundary

STOP after producing the exact planning candidate.

Do not stage, commit, push, merge, implement DynamicHub, change Mochi runtime, connect RMM/Graph/Adobe, write PowerShell, write Ticket observations automatically, enable autonomous actions, create credentials or start implementation slices.

Next gate:

```text
INDEPENDENT S2 ARCHITECTURE REVIEW
→ explicit USER approval
→ controlled integration
```


---

# EXECUTION REPORT

## Summary

The S2 architecture execution is complete on 2026-10-08, America/Toronto. Planning status: READY_FOR_REVIEW. Result: READY_FOR_DYNAMIC_CONTEXT_REVIEW. The original NOT_STARTED header remains historical contract state. This is an author-side architecture candidate, not independent approval, implementation, provider availability or runtime verification.

FACT: the complete integrated S1 execution report was inspected, from Summary through Result, including reuse, diagrams, decision/risk registers, downstream Clipboard 1C inputs and validation. The USER identifies S1 as executed, independently reviewed, USER-approved and integrated. Fresh Git ancestry and the merged [S1 PR 76](https://github.com/JDecelles1990/F7Hub/pull/76) corroborate integration and its recorded APPROVED_WITH_NOTES review. S1's historical author-side unapproved/next-review wording describes its original candidate; it does not undo subsequent closure. PR 76 records a non-blocking P3 inventory wording note. No S1 change is made here.

S1's executed architecture is authoritative for shell/presentation concerns. Its previously completed 25/25 reconciliation remains preserved below without redesign. S2 recommends deterministic local suggestions by default, explicit invocation of available approved read-only actions, immutable service-validated target/Ticket bindings, and optional, separate recording. AI remains advisory/optional; remote providers, sensitive Mochi transport, observation persistence and automation require their own reviewed delivery. Seven required matrices, eight Mermaid sources, decision/risk registers, Clipboard 1C handoff and all 55 original criteria are completed at architecture-planning depth. Runtime and Mermaid rendering remain NOT RUN.

## Baseline / Candidate Identity

| Field | Inspected boundary |
| --- | --- |
| Workspace / branch | C:\Dev\F7Hub / main |
| HEAD / local origin/main | 7c99b4b1326cf52ca565f51258fc6332040b6a29, equal at inspection; fresh remote-ref equality NOT VERIFIED |
| Integrated S1 | PR 76, merge 7c99b4b1326cf52ca565f51258fc6332040b6a29; architecture integration, no shell implementation |
| S1 raw input | 149,444 bytes; SHA256 d7319c11832e6efab042a67ed963592123057c7589fe7ed65d5d7e191dfcfa22; CRLF; unchanged input |
| S2 pre-task raw input | 37,294 bytes; SHA256 198ac6225f729997c3ff626f727e2be4e2a9fffae795c97a056433ca99409db5; UTF-8 without BOM, LF, final newline |
| Initial status / index | S2 marked modified; protected unrelated GuideSettings.ini pathname untracked; no staged paths |
| Authorized write | Append to this S2 report only; preserve the entire pre-task file as an exact raw prefix, including existing local state |
| Worktree choice | Bounded append to the explicitly named existing S2 file in place; no branch movement or integration, no edits to any other path |
| Protected handling | AHK settings pathname observed only in Git inventory; not opened, read, hashed, statted, edited or staged |
| Candidate lifecycle | S2 supplement unapproved, unstaged, uncommitted, unpushed; independent review NOT RUN |

Continuation identity: the USER named docs/workspace-s2-execution-20261007; fresh inspection found main instead and no such branch. The named branch was created at unchanged HEAD 7c99b4b1326cf52ca565f51258fc6332040b6a29, preserving the existing S2 candidate and protected pathname. Baseline main SHA is that same commit; baseline S2 Git blob is e28f31c2a05a0ab4ea98f724db1e53f35c001cbe. Retained reconciliation input was 78,014 bytes, raw SHA256 676467e5a5ac5ec0149499d83b1737833b683f81bd7b7942deaca01c1d04cd5d. Final immutable identity is reported outside this document after validation; no self-referential final hash is embedded. Historical baseline rows describe the prerequisite turn; current candidate remains unapproved, unstaged, uncommitted and unpushed.

## Approved Inputs

FACT: fresh read-only merged-PR records and merge ancestry corroborate the approved inputs already identified by S1. Approval evidence is the USER's explicit S1 closure plus recorded review/approval/integration descriptions; no separate chat-history audit is claimed. Old author-side next-review wording is historical. All merges below are ancestors of current HEAD.

| Owner input | Integration record / merge | Consumed contract / gate |
| --- | --- | --- |
| Foundation 0A | [PR 66](https://github.com/JDecelles1990/F7Hub/pull/66), 1a7015b500fc0eccbab749e82585c7936d5cb478 | CLOSED; approved 0A-D1 troubleshooting coordination and 0A-D2 ticket-optional Journal |
| Foundation 0B | [PR 67](https://github.com/JDecelles1990/F7Hub/pull/67), 41d49d6644727cb324be24e05fda6738cd782eb6 | CLOSED; envelope, identity/correlation, outcome axes and retained legacy adapters |
| Foundation 0C | [PR 68](https://github.com/JDecelles1990/F7Hub/pull/68), 3d0dd673798852941b6fd690cd290dd2ba8c61de | CLOSED; Observation/Evidence/Action/Result, provenance and accepted relationships |
| Foundation 0D | [PR 70](https://github.com/JDecelles1990/F7Hub/pull/70), 4c4ecb19022bb2906b56d15f15316f6594bcabcf | CLOSED; pure definitions, shared resolution, runtime/secret/capability distinction |
| Foundation 0E | [PR 71](https://github.com/JDecelles1990/F7Hub/pull/71), 69176c2801329fef2f107a35129337c9394b2aa4 | CLOSED; reconciled ownership, no parallel shared infrastructure |
| Clipboard 1A | [PR 72](https://github.com/JDecelles1990/F7Hub/pull/72), db7b7b387806fce786a05ee3f9bc14ee29cdbd60 | CLOSED; Item/Event, mandatory sensitivity, Save/Pin/Evidence and safe context |
| Clipboard 1B | [PR 73](https://github.com/JDecelles1990/F7Hub/pull/73), d22b001aea9957dd28bfc1af6450934a110aa0e6 | CLOSED architecture input; typed actions/authenticated ingress, source references and unavailable capabilities |
| Workspace S1 | [PR 76](https://github.com/JDecelles1990/F7Hub/pull/76), 7c99b4b1326cf52ca565f51258fc6332040b6a29 | CLOSED by USER direction; shell authority, retained compatibility PASS |
| Diagnostics 2A | Planning file inspected; no executed/approved report found in it | NOT VERIFIED as approved; not an authority input. Existing PowerShell implementation/canonical boundary and Foundation D1 constrain S2 |

Dependency gate: PASS for architecture planning. Ticket/Knowledge/Script services and local diagnostic boundaries are inspected implementation inputs; proposed generic providers/result associations do not acquire availability from this table.

## Repository Areas Inspected

| Evidence key | Source / inspection | Use and limit |
| --- | --- | --- |
| S1 | [Complete S1 execution report](S1_Main_Shell_Technician_Workspace_Navigation.md#execution-report) | Authoritative architecture input; not proof that its proposed shell is implemented |
| S2 | Original sections 1-74 of this file, including invocation binding in 11, 22-23, 27, 45 and 52 | Consumer contract; original planning instructions preserved |
| F | [0E Shared Context](../Foundation/0E_Foundation_Architecture_Reconciliation.md#shared-context-reconciliation), [0E DynamicHub](../Foundation/0E_Foundation_Architecture_Reconciliation.md#dynamichub-reconciliation), [0D Settings / Non-Settings](../Foundation/0D_Settings_Architecture.md#settings--non-settings-classification) | Source ownership, workflow coordination, immutable initiating refs and runtime/preference separation |
| M | [MainWindow](../../../Python/f7hub/gui/main_window.py), construction, routes, busy and close paths | Fresh source inspection: QMainWindow, retained QStackedWidget pages, status bar and conservative guards |
| T | [TicketWorkspace](../../../Python/f7hub/gui/ticket_workspace.py), has_draft, confirm_discard, add_note and _reload_after_save; [TicketService.add_note](../../../Python/f7hub/services/ticket_service.py) | Existing Ticket-owned draft, frozen ticket_id/values, transactional notes and committed-write/read-failure distinction |
| R | [ServiceTaskRunner](../../../Python/f7hub/gui/service_task_runner.py), complete source | Existing asynchronous dispatch and GUI-thread completion; busy clears before callback, so owner pending guards remain necessary |
| O | [Mochi guidance](../../../Mochi/AGENTS.md), [README](../../../Mochi/README.md), MVP and Architecture relevant sections | Cosmetic companion/current controls versus planned context/acknowledgement; no new transport or pet lifecycle assumed |
| V | [MainWindow tests](../../../Tests/GUI/test_main_window.py), relevant draft/pending/minimum-size assertions inspected | Source evidence only; tests NOT RUN for this document-only supplement |
| G | Root/Planning/Foundation guidance, ROOT, documentation router, Git state and PR 76 | Scope, authority, lifecycle and preservation |

FACT M/T/R: the existing host and service boundaries can be reused. The S1 shared auxiliary lease, application selected-context holder and shared Quick Note presenter are approved architectural targets; this inspection does not establish that they exist at runtime. REUSE / EXTEND those S1 seams when separately implemented; do not create a competing host, context store, Ticket editor, scheduler, Settings store or domain owner. No operational database, provider account, external prototype or sensitive runtime data was inspected.

### Continuation evidence

| Key | Newly inspected material | Evidence / limit |
| --- | --- | --- |
| F-A | [0A decisions D1/D2](../Foundation/0A_Master_Foundation_Architectural_Contract.md#approved-decision-0a-d1--dynamichub-ownership) | DynamicHub workflow coordination, Diagnostics execution/result authority, Journal independence |
| F-B | [0B execution report](../Foundation/0B_Global_JSON_Contract_Interoperability_Grammar.md#execution-report), Common Envelope through provider/offline and legacy contracts | Closed message grammar, request correlation versus operation identity, uncertainty, cosmetic v1 preservation |
| F-C | [0C Shared Operational Vocabulary](../Foundation/0C_Taxonomy_Information_Vocabulary.md#shared-operational-vocabulary), Provenance & Confidence | Domain semantic distinctions; no fabricated scores or global ledger |
| F-D | [0D Recommended Configuration Architecture](../Foundation/0D_Settings_Architecture.md#recommended-configuration-architecture), Settings Ownership / non-settings | Definitions/services composed explicitly; selected workflow state not preference |
| B-A | [Clipboard 1A](../Clipboard/1A_Clipboard_Domain_Data_Lifecycle.md#sensitivity--privacy), privacy/Mochi boundary and source retention | No raw secret/hash/history sharing, fresh selected source and redaction limits |
| B-B | [Clipboard 1B](../Clipboard/1B_AHK_Python_Clipboard_Capture_IPC_Quick_HUD_Architecture.md#action-routing), action/privacy/1C handoff | Diagnostic open-request never copied-command execution; cosmetic Mochi cannot carry advisory payload |
| O-C | [MochiService](../../../Python/f7hub/services/mochi_service.py), [MochiGateway](../../../Python/f7hub/infrastructure/mochi_gateway.py), [channel](../../../Python/f7hub/infrastructure/mochi_channel.py), [protocol](../../../Python/f7hub/domain/mochi_protocol.py), complete source | Session control, generation/correlation, limits/timeouts, mutation uncertainty; no business context/actions |
| P | [PowerShellService](../../../Python/f7hub/services/powershell_service.py), approved specs/execute/pack/result validators; [gateway](../../../Python/f7hub/infrastructure/powershell_gateway.py), preparation/runtime/process/capture-cleanup paths; [result types](../../../Python/f7hub/domain/diagnostic_results.py) | Three fixed local operations, sealed non-elevated execution, strict validation, memory results and one fixed sequential pack |
| S | [ScriptService](../../../Python/f7hub/services/script_service.py), verified read/preparation/path admission; [ScriptRepository](../../../Python/f7hub/repositories/script_repository.py), record/list/get | Existing registry/verified bytes reused; catalog availability is not execution permission |
| A-L | [bootstrap](../../../Python/f7hub/app/bootstrap.py), [logging](../../../Python/f7hub/app/logging_config.py); PowerShell guidance and Docs12 relevant current sections | Composition/session versus selection; centralized safe logging; established execution architecture |
| DB | [ticket migration 0004](../../../Database/Migrations/0004_tickets.sql), notes/timeline schema; Docs07/08/09 relevant ownership/schema sections | Existing note metadata/transactions do not establish generic Observation/Evidence APIs; no database opened |
| SEARCH | Tracked filename/symbol searches in Python/f7hub, Mochi/src, Tests and planning owners | No current Action Catalog/DynamicHub/RMM/Graph/Adobe/Journal/observation association implementation established in searched scope; external/untracked prototypes excluded |
| Q | Official Microsoft user/licenseDetails/Get-EXOMailbox docs, checked 2026-10-08 | Supported read-operation examples, not configured provider/account/permission evidence; links in Microsoft 365 Architecture |

Test filenames and relevant existing source assertions were inspected, including Mochi controls, PowerShell service/pack and Script/Ticket GUI flows; none was executed. No additional project architecture skill was found; implementation slice lifecycle machinery is not applied to this documentation-only phase. No protected guide settings/content or external DynamicHub files were inspected.

The following reconciliation block is the retained prerequisite snapshot. Its statements that full S2 work remained outstanding describe that earlier checkpoint and are superseded by the completed sections and final Validation/Result below. Its compatibility matrix and architecture rules are unchanged.

## S1 → S2 Architecture Reconciliation

### Authority and compatibility assessment

All 17 mandatory executed S1 decisions are consumed by the matrix and lifecycle rules below. S1 owns MainWindow, Technician Workspace hosting/navigation, selected-context presentation and coordinated auxiliary layout. The application owns Active Technician Context references/revisions; source services own records and effect validation. Ticket owns its draft/content and writes. S2 consumes those seams for contextual assistance, approved action presentation and result follow-up.

Conflict classifications: S2_SPECIALIZATION means a consumer detail compatible with S1; S2_CORRECTION_REQUIRED means an S2 assertion must be corrected within S1's existing authority; S1_CONFLICT means an approved S1 decision would have to change; NOT_VERIFIED means insufficient evidence. Matrix PASS assesses architecture only. Runtime unknowns are listed separately and cannot be converted to runtime PASS.

### S1 → S2 Compatibility Matrix

| S1 Decision | S1 Owner | S2 Consumer | Required S2 Behavior | Conflict? | Resolution / Specialization | Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MainWindow ownership | MainWindow / application composition | DynamicHub presenter | Remain an internal MainWindow child; request shell placement and guarded routes | No | S2_SPECIALIZATION: no second primary window or rival shell | S1 MainWindow Integration; S2 30, 55; M | PASS |
| Technician Workspace | S1 shell presentation coordinator | Contextual assistance | Consume hosting/context; owning services retain domain rules | No | S2_SPECIALIZATION: coordination does not transfer records, execution or persistence ownership | S1 Technician Workspace; S2 3, 8; F | PASS |
| Workspace hosting | S1 retained QStackedWidget | Open Full Tool | Route to existing owning singleton; DynamicHub remains an auxiliary surface | No | S2_SPECIALIZATION: no replacement host or popup full business module | S1 Workspace Hosting; S2 30, 55; M | PASS |
| Singleton workspace lifecycle | S1 and module participants | Result detail / tool routes | Preserve owner instance, draft and pending state on hide/return | No | S2_SPECIALIZATION: panels bind to retained owner projections; no duplicate tool per result | S1 Technician Workspace; S2 23, 53 | PASS |
| MDI rejection | S1-D02 | DynamicHub / full results | Introduce no classic or tabbed MDI | No | Consume rejection without exception; internal temporary panels suffice | S1 Workspace Hosting, Decision Register | PASS |
| Workspace tabs | S1-D03 | Multiple results / follow-ups | No unlimited browser tabs, multi-record shell instances or new MVP tab row | No | S2_SPECIALIZATION: bounded result cards are views of operation identities, not shell documents | S1 Workspace Tabs; S2 30, 50 | PASS |
| Active Technician Context | Application selection owner, S1-D04 | Context projection / ranking | Consume minimal owner-qualified refs and revision; never copy records or grant permission | No | S2_SPECIALIZATION: distinguish current display snapshot from immutable operation binding | S1 Active Technician Context; S2 9-11, 22; F | PASS |
| Active Ticket Context | S1 compact shell control / application selection | Optional Ticket association | Keep globally reachable across major workspaces and narrow panels; absence is valid | No | S2_SPECIALIZATION: association captures exact invocation-time Ticket; current display is not completion authority | S1 Active Ticket Context; S2 27, 52 | PASS |
| Quick Ticket | S1 container / Ticket-owned presenter | Ticket-related result follow-up | Reuse one Quick Note draft and explicit Open Ticket; no separate editor or generated Quick Note | No | S2_SPECIALIZATION: dirty/pending guard before occupancy; observations use their owning service | S1 Quick Ticket Drawer; S2 25-28; T | PASS |
| Navigation flyouts | S1 shared host / descriptors | Mochi navigation entry | Shared navigation mechanics stay separate from DynamicHub cards/results | No | S2_SPECIALIZATION: an explicit context-surface route requests the auxiliary slot | S1 Flyout Mechanics, Navigation Surface Matrix; S2 30, 55 | PASS |
| Flyout hover/provider prohibition | S1-D08 / descriptor adapters | Capabilities / suggestions | Hover/open performs no AI, RMM, Graph, PowerShell, remote capability refresh or DynamicHub remote action | No | No indirect prefetch via S2 subscriptions; available cache or unavailable state only | S1 Flyout Mechanics; S2 16, 35, 57 | PASS |
| Global status/background surface | MainWindow status / operation owner | Action feedback | Generic progress/outcome remains shell status; detailed result belongs to its owner/S2 | No | S2_SPECIALIZATION: project safe state without replacing status with Mochi or Ticket Timeline | S1 Status / Background Activity, S1-D14; S2 29, 51-52; M/R | PASS |
| Auxiliary region | S1 shell coordinator, S1-D15 | DynamicHub placement | Use the single coordinated region; one expanded occupant; no permanent second right sidebar | No | S2_SPECIALIZATION: guarded temporary occupancy, release and return rules below | S1 Mochi / DynamicHub Reserved Region; S2 30, 55 | PASS |
| Module inspector coexistence | S1 coordinator / inspector owner | DynamicHub takeover/return | Preserve owning module selection/draft and refuse unsafe displacement | No | S2_SPECIALIZATION: one bounded return descriptor; no stack of layered inspectors | S1 Quick Ticket Drawer, Reserved Region | PASS |
| DynamicHub placement | S1 region/layout | Contextual action surface | Use split, temporary slide-over or internal task panel by shell budget | No | S2_SPECIALIZATION: collapsed affordance has no reserved blank column | S1 Responsive Layout, Reserved Region; S2 30, 55 | PASS |
| Mochi overlay placement | Existing companion lifecycle / S1 focus constraints | Tiny acknowledgement | Optional, nonactivating, bounded and separate from auxiliary occupancy | No | S2_SPECIALIZATION: tiny text is outside the lease; no cards/editor/sidebar there; accessible app equivalent | S1 Reserved Region, Keyboard & Accessibility; S2 29, 55-56; O | PASS |
| Focus behavior | S1 shell / modal and draft participants | Opening/dismissal/completion | Only explicit open takes focus; results do not steal focus; inner/modal owner has priority | No | S2_SPECIALIZATION: generation-aware focus return, no activation of another application | S1 Flyout Mechanics, Keyboard & Accessibility; S2 29, 32 | PASS |
| Keyboard behavior | S1 scoped application actions | Cards / Close / Open Full Tool | Preserve editor shortcuts; scoped Escape after inner owner guard; visible alternatives | No | S2_SPECIALIZATION: no new global hotkey or override of S1 candidate chords | S1 Keyboard & Accessibility; S2 56 | PASS |
| Accessibility | S1 shell / theme constraints | Cards / result / acknowledgement | Named controls, visible focus, textual state, keyboard access and nonanimated equivalent | No | S2_SPECIALIZATION: optional acknowledgement expiry does not remove recoverable errors/results | S1 Keyboard & Accessibility, DPI; S2 29, 56 | PASS |
| Responsive layout | S1-D16 / measured central minimum | Every S2 surface | Consume WIDE / MEDIUM / MINIMUM; primary working width has priority | No | S2_SPECIALIZATION: collapse first; explicit narrow task panel with Back/Close, not a permanent column | S1 Responsive Layout; S2 55; responsive matrix below | PASS |
| Draft preservation | Feature draft owner / S1 coordinator | Occupancy and navigation | Retain valid hidden drafts or refuse; never save, clear or retarget them itself | No | S2_SPECIALIZATION: unchanged Cancel-default guard and owner pending-through-callback semantics | S1 Draft Preservation; S2 11, 52; T/R | PASS |
| Workspace restoration | S1-D17 / future 0D preference owner | Dismiss/return / application restart | Session retention only initially; revalidate returned refs; no persisted operations/context/drafts | No | S2_SPECIALIZATION: discard S2 presentation/lease return state at shutdown; owner result persistence is separate | S1 Technician Workspace, Settings Inputs; S2 44, 54; F | PASS |
| Async/background work | Owning service/runner / S1 activity | Action execution / late completion | Keep work off GUI loop; retain bound operation and truth through callback/refresh | No | S2_SPECIALIZATION: hiding is not cancellation; late result indicator does not overwrite new-context UI | S1 Status / Background Activity; S2 11, 23, 51-52; R | PASS |
| Settings boundary | Foundation 0D / S1 consumer | Verbosity, acknowledgement and trigger preferences | Contribute validated definitions through 0D; no selection/lease/operation/credentials in preferences | No | S2_SPECIALIZATION: defaults work without shared Settings delivery; preferences never grant permissions or bypass draft guards | S1 Settings Inputs; S2 54; F | PASS |
| Clipboard 1C downstream use | S1 shell; Clipboard 1A/1B; future 1C owner | Clipboard context / action entry | Same singleton host, inspector lease and explicit validated source/target; no Clipboard-derived authority | No | S2_SPECIALIZATION: 1C consumes this coexistence contract only after full S2 closure; cross-check alone does not start 1C | S1 Downstream Clipboard 1C Inputs; S2 9-11, 27 | PASS |

Compatibility coverage: 25/25 PASS at architecture-planning depth. No inspected S2 assertion requires changing S1. Remaining ambiguity is resolved by explicit consumer specialization, not by rewriting the approved shell.

### Auxiliary-region reconciliation

RECOMMENDATION: extend the presentation lease already defined by S1. MainWindow's shell coordinator is the sole occupancy arbiter. Module-inspector presenters, the Ticket-owned Quick Ticket presenter and the S2 DynamicHub presenter request occupancy with a known surface kind, explicit-versus-informational intent, owner reference/generation and safe return/focus information. Requests are in-process presentation intent, not domain commands. S2 never grants itself a lease or invokes a domain effect through occupancy.

Only one inspector, Quick Ticket or DynamicHub is expanded. WIDE renders it beside the stack if measured central space remains usable; MEDIUM/MINIMUM use the temporary surface described below. Hidden retained presenters are not layered expanded occupants. A modal dialog retains precedence; no request opens behind/above it.

| Transition / concern | Shell arbitration | S2 / owning-presenter behavior |
| --- | --- | --- |
| Explicit DynamicHub open, empty slot | Validate presentation generation/availability, close navigation flyout, grant slot | Present bounded local eligible data; focus first meaningful control on successful explicit open only |
| Existing DynamicHub, repeated open | Reuse same surface and lease | Focus existing view on explicit request; do not create another instance or duplicate work |
| Automatic context/result/recovery cue | Do not displace any expanded occupant or active editor; default to collapsed safe indicator | May refresh eligible local presentation without focus; cue does not execute, infer remotely or consume the slot |
| Explicit replacement of clean inspector / clean Quick Ticket | Ask displaced owner to prepare safe hide; grant only after acceptance | Preserve owner selection/state and original-target draft model; retain one return descriptor for the displaced valid surface |
| Dirty Quick Ticket | Never replace automatically. On explicit request, owner may confirm safe retained hide; otherwise refuse or negotiate supported Save / Discard / Cancel, Cancel default | S2 cannot clear/save/discard the draft. Failed save/Cancel cancels replacement. Retained hidden draft keeps its exact Ticket and visible draft indicator |
| Dirty inspector | Same owner guard; preserve permitted draft/token on safe hide or refuse | Inspector stays its module's presentation/domain responsibility; no S2 copy of its editable state |
| Pending owner write/run | Respect pending through callback/owned refresh; safe hide only with a proven retained presenter, otherwise refuse | Existing conservative blocking remains until tested adapters exist; no fake cancellation or automatic replay |
| Explicit Quick Ticket/inspector request while DynamicHub expanded | Release DynamicHub after any owning action-input guard; apply incoming owner guards | Hide S2 without cancelling operation; original result remains reachable by operation identity |
| DynamicHub Close / Back / scoped Escape | Release slot, revalidate remembered displaced surface and restore without overriding a newer explicit surface/focus intent | Discard transient suggestion view, retain bounded eligible owner-backed result access; do not mutate active context |
| Context change | S1 negotiates affected dirty/pending owners before publishing its context revision | Reproject current suggestions; disable obsolete actions/confirmation. Running operation cards retain original binding; incompatible inspector is not restored under a new record |
| Responsive collapse | Remove auxiliary width before central minima fail; retain safe owner state or apply owner guard | No discard, retarget or cancellation; collapsed affordance/owner draft indicator remains reachable |
| Focus return | Prefer recorded live/enabled origin only if no newer intentional focus; otherwise current module/trigger | No repeated focus attempts, no application activation on completion or automatic restoration |

The return descriptor is bounded to one displaced owner and its presentation generation. A new explicit replacement supersedes it; no unbounded surface history or restoration stack. It carries no copied records, draft text or execution authority. If the origin is disposed, its reference expires, its module/context no longer matches, or it cannot rebind safely, restore the central workspace/collapsed affordance instead and preserve any still-valid owner draft separately. Restoring a surface must not change global context to satisfy an obsolete descriptor.

Dirty Quick Ticket can be hidden only through the owner-approved S1 retention path. Until that adapter exists and is validated, keep the existing conservative guard or refuse. Completion/resize/auto-open preference is never permission to bypass that condition.

Mochi's tiny acknowledgement is outside the auxiliary-region lease and outside primary tool hosting. It is optional output on the companion's approved presentation lifecycle, with bounded lifetime, no focus acquisition, no editable content and no interactive action-card collection. It cannot occupy a second right sidebar. Suppress it when hidden/unavailable, privacy-suppressed, another application is active or safe geometry cannot be established; use a minimized accessible application equivalent. It must not obscure input, confirmation, navigation or required Close/Back controls. No new IPC command, payload transport, desktop window or current companion capability is implemented or approved here. A future renderer extension needs its own approved boundary; core results remain available without it.

### Active Technician Context reconciliation

CURRENT UI SELECTION means the application-owned selected refs/revision and the consumer's present display generation. It may change only through S1's guarded selection pathway. It is neither authorization nor a durable domain snapshot.

INVOCATION-TIME OPERATION BINDING means the owning service's immutable operation identity and initiating references/decision inputs. S2 supplies a proposal; the service validates and establishes the binding. S2's optional context_id is correlation metadata when supported, not a new global identity store or mandatory fabricated ID.

Required flow:

```text
S1 application-owned Active Technician Context (selected refs + revision)
  -> purpose-filtered, bounded safe projection
  -> explicit action intent with proposed invocation snapshot
  -> owning service validates action, refs, scope, freshness, permissions,
     capability, confirmation and optional exact Ticket association
  -> accepted immutable operation binding + operation_id
  -> owning operation / normalized original-target result
```

Changing context before acceptance invalidates a stale request/confirmation; return for explicit revalidation instead of dispatching against a replacement target. Once accepted, later S1 revisions affect future actions and current presentation only. Services may fail/reconcile if the original target, authorization or captured scope becomes invalid; they cannot substitute new current refs. Missing optional refs stay absent; missing required refs disable the action. Display names, clipboard Entities and prose cannot establish Device/User/Tenant IDs.

A current-context projection contains only approved fields required for this use case: optional owner-qualified refs, selection revision, source freshness, safe labels and privacy-filtered available-capability/result references. Do not copy full Ticket, user, device, Clipboard or provider records. No new global context database, cross-process representation or source-service dependency on S2.

Completion always retains operation_id, action/version, original target/provider/tenant and invocation-time Ticket choice. GUI callbacks update a displayed card only if its view/operation generation matches. After selection A -> B, current suggestions may describe B; an operation for A remains identified as an earlier-context result for A. Expose a safe pending/result indicator and explicit View Result / Open originating tool route. Do not select A automatically, relabel it B, replace B's result or lose the authoritative A outcome just because its original panel is hidden. Privacy/expiry can remove a presentation projection without changing authoritative owner retention.

### Active Ticket / Quick Ticket reconciliation

S1 owns the global Active Ticket presentation and Quick Ticket shell access. Ticket owns one saved-Ticket-bound, human-authored Quick Note draft shared with the full Ticket presentation, with only one writable binding. S2 owns none of these mechanisms.

| Concept | Authority / permitted S2 use | Prohibited conflation |
| --- | --- | --- |
| Technician Quick Note | Ticket-owned draft and TicketService workflow; explicit human input/save | Injecting generated observation text or saving it automatically as technician-authored content |
| System Observation / structured result | Producing action/result owner; optional reviewed Ticket recording/association service | Calling current add_note and claiming that establishes distinct observation semantics or provider authority |
| Evidence | Source eligibility, accepted relationship/provenance and owner retention contract | Treating every result/Quick Note/KB reference as accepted Evidence |
| Ticket Timeline | Ticket-owned history presentation of authoritative records | Using it as generic shell progress or declaring a write saved before owner confirmation |
| Later Ticket association | Separate explicit target/source intent with owning-service validation | Retargeting or rewriting the original operation's captured association |

FACT T: TicketService.add_note has source/is_ai_generated metadata and transactional persistence; this alone does not verify a System Observation API, generic Evidence association or duplicate-safe recording retry. A future owner capability must be inspected/designed before S2 enables recording; unavailable means disabled, not a fallback write into Quick Note.

Concrete binding case: operation O starts for Device A with explicit Ticket A association. The technician later selects Ticket B and opens B's Quick Ticket. O may finish and remain a valid result for Device A. Only the captured Ticket A can receive O's originally requested recording after current owner validation. B's display/draft is untouched; feedback clearly identifies recording state separately from provider state. No invocation-time Ticket choice means no automatic association when B becomes active.

If O succeeds and Ticket A recording fails, O remains SUCCEEDED (or its actual partial/uncertain state). Retry Ticket recording invokes only the association/recording step using O's existing authoritative result and captured Ticket A, with current existence/authorization/freshness and duplicate-prevention/reconciliation checks. No provider rerun. An unknown recording outcome is reconciled before retry; no assumed exactly-once API. If A is deleted/unavailable, retain truthful owner result access and explain the recording failure; do not use B. A later explicit association to B is a new service operation with its own identity/validation, not a mutation of O's binding.

Opening Quick Ticket / Open Full Ticket always uses S1's guarded access and Ticket's draft presenter. A current dirty B draft can refuse switching to originating A. An accepted observation never clears B's human draft, and a failed refresh never changes a committed recording into failure or triggers another write.

### Navigation flyout versus DynamicHub

Navigation Flyout = fast navigation / cached glance / safe quick entry using S1's shared mechanics.

DynamicHub = contextual recommendations / explicit action presentation / result follow-up using the auxiliary region.

These surfaces stay separate even when transient. A Mochi navigation entry can expose cached cosmetic status and an explicit Open Context Surface route; that route closes the flyout, requests the auxiliary slot and shows locally available context. Neither hovering nor opening any navigation flyout triggers AI inference, RMM, Graph, PowerShell, remote capability refresh or DynamicHub remote actions, including indirect subscription/prefetch effects.

A missing/stale capability projection displays unknown/unavailable and an explicit owning-tool recovery route. Remote refresh, provider execution or external AI Send requires its separately approved explicit intent and owner boundary. Opening DynamicHub itself needs no provider call; animations, context notifications and suggestion cues do not execute actions. Any later auto-safe operation policy remains separately reviewed and cannot be inferred from a presentation auto-open preference.

### Status versus acknowledgement

| Surface | Owner / meaning | Permitted feedback |
| --- | --- | --- |
| Shell Status / Background Activity | S1 generic application async state | Safe owner/operation status, progress and route to details; no raw payload/history authority |
| DynamicHub | S2 contextual action/result presentation | Action target/safety/availability, structured summary, separate execution/recording outcomes, approved follow-up |
| Mochi acknowledgement | Optional personalized presentation | Tiny truthful privacy-filtered acknowledgement with accessible app equivalent; no progress dashboard or mandatory action controls |
| Ticket Timeline | Ticket domain/history presentation | Authoritative committed notes, observations/relationships when implemented, each preserving its meaning |

A remote result can produce shell completion feedback and a DynamicHub card without a Ticket write. Only confirmed recording permits a Saved to Ticket statement. Partial/failed/uncertain execution or recording is stated accurately; neither cosmetic wave nor dispatch implies success. Important failures/recovery remain reachable after transient acknowledgement expiry. Suppressing Mochi does not remove shell status, owning results or Ticket history.

### Responsive coexistence

Consume S1's initial logical-client-size bands: WIDE >=1440, MEDIUM 1180-1439, MINIMUM SUPPORTED 1000-1179, height >=700. These are S1 planning targets, NATIVE-VALIDATION DEPENDENT; actual owner minimum sizes/large fonts can require earlier collapse. The approximately 700 logical-pixel central budget is S1's initial target, not a certified minimum or fixed setting. Below-baseline fit remains NOT VERIFIED and must not be represented as supported by clipping.

| Concern | WIDE | MEDIUM | MINIMUM SUPPORTED |
| --- | --- | --- | --- |
| DynamicHub auxiliary occupancy | Optional ~320-400 side split only if central owner minimum survives; one occupant | Collapsed affordance; explicit temporary internal slide-over; no permanently reserved width | Collapsed affordance by default; explicit full available-width internal task panel with visible Back/Close; central singleton retained |
| Mochi acknowledgement | Tiny optional nearby text only if safe geometry; accessible app equivalent | Suppress if it competes with input/slide-over or safe space; app equivalent remains | Prefer app equivalent; pet bubble only if it fits without covering task/Close/navigation; never reserve workspace width |
| Action cards | Small ranked 3-5 set, plain target/safety/reason and explicit controls; More/Open Full Tool | Compact vertically scrollable cards; preserve labels and disabled reasons | Single-column scrollable set; no horizontally crowded button wall; required controls reachable with large font |
| Result details | Safe summary inline; explicit details in owning tool, bounded in-panel detail if it fits | Compact summary; deliberate bounded detail within same surface or guarded full-tool route | Summary first; detail replaces content within same internal task panel with Back, or owning full tool; no new dock/window |
| Quick Ticket conflict | Negotiate same single slot; no automatic replacement; dirty/pending owner retains/refuses | Same guard before slide-over change; retained draft indicator accessible | Same guard before task-panel change; never auto-cover dirty editor; preserve exact Ticket binding |
| Inspector conflict | Owner-preserved hide/rebind and one return descriptor | Same owner guard; no stacked inspector plus S2 slide-over | Same guard; inspector and DynamicHub alternate explicit task presentation, no concurrent sidebars |
| Focus | Explicit open only; focus origin/generation recorded | Explicit opening closes flyout; modal/inner owner precedence; completion no focus | Focus contained in current internal task controls while displayed; accessible Back/Close and global Ticket/navigation routes; no Qt modal domain ownership implied |
| Dismissal | Close/scoped Escape releases lease; restore valid prior owner, else central workspace | Same; outside-click may hide only when owner retention is safe and never discards work | Visible Back/Close plus scoped Escape after inner guard; retained central focus/selection restored without retargeting |
| Open Full Tool fallback | Guarded route to existing owning singleton; release slot after successful navigation | Same full tool uses central width; refused navigation keeps current surface | Primary fallback for deep work; central full tool replaces temporary view after guards; no automatic desktop overflow window |

At minimum width, primary technician work takes priority over persistent DynamicHub visibility. A safe collapsed indicator and guarded explicit opening satisfy discoverability. Resize does not clear drafts, rerun actions or change a running binding. If navigation to a full tool fails/cancels, preserve current panel, draft and context. When the route succeeds, return-descriptor state cannot resurrect an incompatible inspector into the newly selected module.

DPI/multi-monitor constraints remain S1-owned: use the valid current shell/screen geometry; clamp transient content, preserve reachable controls, recalculate on work-area changes, dismiss safely on screen removal, and never force focus to another application. Exact geometry, translucency, screen-reader behavior and installed-runtime acceptance are NOT_VERIFIED until separate bounded WINDOWS_NATIVE checks.

### Conflicts found and specializations made

| Finding | Classification | Resolution / owner | Disposition |
| --- | --- | --- | --- |
| S2 30/55 names a reserved temporary region without occupancy arbitration | S2_SPECIALIZATION | S1-D15 consumed through one arbiter, one occupant, guarded replacement and bounded return descriptor | RESOLVED at architecture depth |
| S2 31/54 allows important-context/result auto-open without detailed coexistence rules | S2_SPECIALIZATION | Default indicator-only automatic cue; no displacement/focus. A future auto-open preference can act only on a clean vacant region, no editor/modal interaction and permitted privacy state; otherwise cue only | RESOLVED; preference cannot bypass S1 |
| S2 10/11 distinguishes projection/binding but leaves late-result visuals deferred | S2_SPECIALIZATION | Current suggestion generation separate from original-operation card; earlier-context label and deliberate owner navigation | RESOLVED at architecture depth |
| S2 29/55 tiny overlay could be mistaken for auxiliary occupant or second context surface | S2_SPECIALIZATION | Outside lease, optional tiny output only; safe app equivalent and existing companion lifecycle; no new action surface/transport | RESOLVED at architecture depth |
| S2 54 preferences could be used to persist current context/workflow state | S2_SPECIALIZATION | Consume 0D classification; selection, lease, bindings and drafts remain runtime/owner state | RESOLVED at architecture depth |
| S2 cannot change a retained-stack/no-tab/no-MDI or single-region S1 decision locally | S1_CONFLICT if later proposed; none found now | STOP local design, identify exact S1 decision and return REQUIRES_DYNAMIC_CONTEXT_DECISIONS for owner review | Gate preserved; no current conflict |
| Concrete S2 assertion requiring correction to fit S1 | S2_CORRECTION_REQUIRED | None found in the inspected original contract; ambiguities are specializations above | NONE |
| Actual shell/overlay geometry, focus, accessibility and provider/recording capabilities | NOT_VERIFIED | Future owner implementation and native validation; no fabricated runtime PASS | Open verification obligations |

No unresolved material S1/S2 architecture conflict remains for this prerequisite. S1 was not rewritten. No Foundation meaning, Ticket authority, Notes/Observation/Evidence semantics, Settings architecture or execution boundary is redefined.

### Unresolved items and downstream limits

NOT VERIFIED: actual DynamicHub/auxiliary/shared-draft/selected-context implementation; acknowledgement delivery through a reviewed renderer boundary; exact native focus/DPI/monitor/large-font behavior; provider capabilities/permissions; System Observation/Evidence recording API and retry reconciliation; employer privacy policy. These are future implementation/verification obligations, not evidence that S1 requires changing.

This supplement does not execute the remaining S2 architecture requirements: full Mochi/protocol/gateway inspection, action/provider/context/trigger/recording/safety/failure matrices, complete Foundation comparison, seven required diagrams, whole-phase decision/risk registers and 55/55 assessment. Do not use compatibility PASS to mark the full S2 phase READY_FOR_DYNAMIC_CONTEXT_REVIEW. That result requires this compatibility PASS plus all remaining S2 gates and no unresolved material architecture conflict.

Clipboard 1C may later consume the single-slot rules, context/binding distinction and responsive/focus contract after full S2 review, explicit USER approval and controlled integration. Its own Clipboard source/Inspector/privacy/retention requirements remain owned by 1A/1B/1C. No 1C execution or implementation starts here.

### Required future verification scenarios

These are future tests, NOT RUN. Use synthetic inputs, bounded workers/automation and separate portable from WINDOWS_NATIVE evidence.

| Scenario | Required observation |
| --- | --- |
| Dirty Quick Ticket B + automatic completion for A | B remains visible/bound; A indicator/result preserved; no focus theft or draft change |
| Dirty Quick Ticket + explicit DynamicHub request | Safe owner-retained hide or guard/refusal; Cancel/save failure leaves original surface/draft |
| Inspector -> DynamicHub -> dismiss | Valid owner state returns once; context/module drift invalidates return, never forces old selection |
| Context/tenant A -> B during O | O target/scope/Ticket immutable; B suggestions update; result A correctly correlated |
| No Ticket at invocation; Ticket B selected before completion | No implicit B write; later association separate and explicit |
| Provider succeeded; Ticket recording failed/uncertain | Recording-only retry/reconciliation on captured Ticket; provider invocation count remains one |
| Hover/open every navigation flyout | Zero AI/RMM/Graph/PowerShell/remote capability/S2 execution side effects |
| Panel hide, callback gap, refresh failure and app close | Owner pending/draft/commit truth preserved; hiding is not cancellation |
| All three bands with long labels/large font, DPI/monitor change | Central budget, one occupant, reachable global Ticket/Back/Close/full-tool route; no clipped input |
| Keyboard-only, Narrator/high contrast, acknowledgement suppression | Editor shortcuts and modal precedence retained; accessible equivalent/recovery survives bubble expiry |

## Verified Current Mochi / AI State

FACT O-C: MochiService owns application-session greeting/control intent and subscribes to gateway cosmetic snapshots. MochiGateway performs bounded asynchronous attach/start/status/control, matches request/runtime/connection generations, and reports UNCERTAIN on lost mutation acknowledgement without replay. The channel bounds framing/read/write queues and partial-frame deadlines. Cosmetic v1 admits attach/status/show/hide/idle/wave/pause/resume/exit only, with 4,096-byte complete messages and no arbitrary payload on ordinary controls.

FACT M/A-L: application composition injects MochiService and existing owner services; ApplicationContext is frozen dependency composition. It is not Active Technician Context. Current controls are cosmetic; no business projection, DynamicHub, action-ranking AI, provider execution, acknowledgement-text command or general observation store was established by inspected source/searches. README/MVP proposals and historical native evidence do not implement them.

NOT VERIFIED: installed runtime/renderer health, packaged distributions, external providers, licenses/permissions, employer policy and any external prototype. No existing cosmetic IPC identifier, checkout digest or same-user socket is promoted to a sensitive/admin trust boundary.

## Foundation Compatibility

| Owner | Consumed decision | S2 specialization / prohibited redefinition | Assessment |
| --- | --- | --- | --- |
| 0A-D1 | DynamicHub coordinates interactive troubleshooting | Application workflow presenter/coordinator consumes services; Diagnostics keeps definition/run/result; no alternate executor/persistence | PASS |
| 0A-D2 | Journal supports pre-ticket/ticketless work | Source-owned results can remain ticketless; future local Journal/drafts independent of PSA/AI; no second Ticket Timeline | PASS |
| 0B | Envelope/classes, correlation, conditional refs, legacy adapters | Proposed action DTO profile below; operation_id distinct from message_id; cosmetic/PowerShell v1 unchanged | PASS |
| 0C | Entity resolution, Observation/Result/Evidence, provenance | Selected literals are advisory occurrences; source IDs validated; interpretation separate from observed data/acceptance | PASS |
| 0D | Settings definitions/resolution and runtime exclusion | Pure contributions only; workflow/target/lease/binding are session state, capabilities discovered, secrets excluded | PASS |
| 0E | Coherent owners and extension rules | Reuse source services and approved seams; no global context/event/job/secret/Settings store | PASS |

No material FOUNDATION_CONFLICT found at this planning depth. Missing concrete provider, association and Journal implementations are feature delivery prerequisites, not permission to invent shared replacements. Authentication/credential or sensitive cross-process changes require separate owner review before implementation; S2 specifies no such mechanism.

## S1 Shell Compatibility

RETAINED: 25/25 architecture compatibility PASS in the unchanged reconciliation block. Full S2 consumes its singleton stack, guarded auxiliary occupancy, draft/focus/accessibility and responsive rules. No new S1 conflict is introduced: suggestions/results never become primary navigation, competing sidebars, shell tabs or completion-time selected-context authority. The retained native obligations remain NOT RUN.

## Reuse Assessment

| Component / layer | Current responsibility / dependencies | Consumers / inspected tests | Treatment / reason |
| --- | --- | --- | --- |
| MainWindow, stack, owner presenters / GUI | Composition/routes/status/draft guards via injected services | Ticket/Knowledge/Scripts; existing GUI tests | EXTEND only through approved S1 seams; no new primary host |
| S1 context/auxiliary/shared draft contracts / application presentation | Approved targets, runtime implementation not established | Future S2 and 1C tests | CONSUME / EXTEND when delivered; no duplicate context or editor |
| MochiService/Gateway/channel/protocol / application/infrastructure | Cosmetic session controls, bounded local IPC | Mochi control/protocol tests | REUSE unchanged; sensitive context/text needs separately reviewed adapter, not v1 payload stretching |
| ServiceTaskRunner / GUI adapter | One asynchronous call and GUI-thread callbacks | Existing GUI/integration tests | REUSE; owner pending spans callback/refresh; no speculative parallel scheduler |
| ScriptService/Repository / application/persistence | Approved metadata and same-byte verified preparation | Script registry/copy tests | REUSE existing code/identity; registry is not the S2 catalog or authorization by itself |
| PowerShellService/Gateway / application/infrastructure | Literal local execution policy, sealed process, validation/cleanup, fixed pack | PowerShell/pack tests | REUSE; local targets/parameters cannot be generalized by S2 |
| DiagnosticResult/run/pack / domain | Execution versus collection data and attempted/skipped members | Contract/pack tests | ADAPT after owner validation; retain completeness and collection ERROR semantics |
| TicketService/Repository / application/persistence | Notes/activity/timeline transactions | Ticket tests | REUSE normal Ticket boundary; EXTEND only after explicit observation/association/retry design |
| KnowledgeService/TicketKnowledgeService / application | Local search and RELATED links | Knowledge/link tests | REUSE existing semantics; KB reference is not copied Evidence |
| Shared Settings architecture / Foundation | Pure definitions, validated resolution/overrides | Implementation not established | CONSUME later approved service; no local preference file/store |
| Action Catalog / pure application definitions | No equivalent complete metadata found; source registries/policy do exist | Future pure catalog/dispatch tests | NEW bounded static contribution profile justified for cross-owner discoverability; references existing operations, no duplicate diagnostic registry |
| DynamicHub workflow state / application coordination | No implementation established | Future binding/late-result tests | NEW minimal session coordinator/presenter seam within 0A-D1; existing dispatch/services reused, not global jobs |
| RMM/Microsoft/Adobe / integration | No adapter or account capability established | Future adapter contract tests | DEFER provider implementation; reuse gateway pattern, no SDK dependency chosen |
| Case Journal / domain | Approved ticketless concept, no concrete service/store established | Future owner tests | DEFER physical design; source result retained for current session meanwhile |
| Logging / infrastructure | F7Hub rotating application handler, safe exception-type fallback | Existing logging tests/inventory | REUSE; technical logs distinct from audit/observations |
| Generic executor/event bus/plugin loader/global ledger | No demonstrated S2 need | None required | NOT NEEDED; increases authority and duplicates owners |

No table, migration, production class, IPC endpoint, dependency or service is created by this report. Proposed catalog/coordinator names are conceptual responsibilities; future implementation searches again before choosing filenames/classes.

## Role Model

RECOMMENDATION: Local IT AI sublayer names optional eligible-context interpretation/ranking/explanation, not a required hosted model. Deterministic local rules are the initial suggestion path. Mochi is optional personality/presentation. DynamicHub is the application-level interactive troubleshooting surface/coordinator under 0A-D1, handling suggestion/step presentation and explicit intent through source services. It owns bounded session workflow presentation, not domain records, credentials or execution policy.

An owning application service validates intent/source/target/policy and performs its use case through repositories/gateways. Diagnostics owns diagnostics/results; Ticket owns notes/history and accepted Ticket association; Clipboard owns Item lifecycle/privacy; Knowledge owns articles; provider adapters own external translation. AI may propose only known action keys/typed values and explain validated observations. Its proposal is untrusted until catalog/type/identity validation and technician adoption; no confidence score or generated command grants authority.

## Context Architecture

Consume S1's application-owned selected refs/revision. An application projection adapter reads approved source services and supplies only purpose-eligible fields to the DynamicHub workflow presenter. It does not mutate selection to satisfy a suggestion. A display projection, selected source refs and invocation binding have distinct lifetimes; no copied domain objects or universal context/session store.

Optional Company/User/Device/Ticket/Tenant refs remain absent until their owners resolve them. Contact is not automatically a Microsoft User. A hostname/email/Clipboard Entity is not a canonical provider mapping. The Context Matrix fixes freshness/exposure/association for each source. Current shell selection does not authorize outbound AI/provider exposure; source references are not bearer permissions.

Bound presentation memory: one DynamicHub surface, at most five displayed suggestions, a bounded session list of operation-card references (initial recommendation ten, no raw bodies). Owner result retention/limits remain authoritative. Evicted/expired refs become unavailable; no secretly persisted cache or promised recovery after app restart. A result in memory only is labelled as such.

## Context Freshness

Source services supply available revision/observation time and VALIDATED/STALE/MISSING/UNAVAILABLE meaning. Failed read means unavailable, not deleted. Projection generation rejects obsolete UI callbacks; owner invalidation immediately disables affected actions. Revalidate before action acceptance even without a notification.

Owning services validate source eligibility, exact target/mapping, company/customer/tenant relationship, current capability/permission/policy and required confirmation. A selection revision is a staleness precondition, not domain transaction protection. Existing transactional/concurrency tokens remain owner authority. Confirmation binds action version, parameters and exact scope/target; any changed request needs fresh confirmation. No stale queued/destructive replay.

## Invocation-Time Operation Binding

Consume the immutable binding established in original S2 section 11 and retained reconciliation. Capture after owner validation: operation_id, action key/definition version, invocation selection revision, exact owner-qualified target(s), tenant/customer/provider scope, validated parameters, technician attribution, capability/policy/confirmation inputs and optional exact Ticket recording choice. Freeze the binding for that operation; do not read current Active Ticket during completion/retry.

If context changes before service acceptance, reject the stale proposal rather than choose new refs. Once accepted, later UI selection affects future suggestions only. Revalidate original authorization/scope at dispatch and any later association; revoked/invalid original refs fail/reconcile without substitution. Results retain the binding and their source operation identity even if the consumer generation changes.

Late results are valid when their execution outcome is valid. Present an earlier-context label and deliberate Open originating tool/Ticket route; preserve owner result, no automatic navigation/focus or mutation of new-context widgets. A recording retry is a distinct operation over the original result and captured Ticket. A later association to a new Ticket is separately explicit and does not rewrite the original binding.

## Action Catalog

RECOMMENDATION: application-owned, statically composed, pure Action Catalog metadata for DynamicHub's approved action discovery. Each source module contributes definitions that reference its owning use case and existing registry/policy identity. Diagnostics retains definitions/run/result authority; catalog membership alone is not execution permission. Avoid runtime import/plugin discovery or a second diagnostic/script registration store.

Each admitted definition includes stable provider-neutral key, definition revision, plain label/purpose, owner, allowed target/input schema, safety class, current capability prerequisites, reviewed adapter strategy, result schema/limits, finite deadline, confirmation/disclosure policy, provenance/audit, recording eligibility and bounded semantic follow-ups. Dispatch is a compiled allowlist from key to owning-service method, never callable names, paths, shell fragments or endpoints supplied by AI/provider/UI metadata.

Reject duplicate keys/incompatible owner definitions, unknown parameters/fields, unsupported versions, nonexistent adapters and unsupported target types. Reuse diagnostic.windows.system_snapshot/network_snapshot/services_snapshot and diagnostic.pack.local_baseline for current local definitions. Future device.network_snapshot is a separate remote-target use case; it cannot relabel current parameterless local execution as remote. Original example aliases are illustrative, not registrations; resolve through reviewed metadata before enabling them.

## Action Safety Classes

SAFE_READ_ONLY: reviewed operation intends no operational/domain mutation on the queried target, uses an eligible bounded source/target and least privilege; incidental provider audit/counters may still exist and confidentiality remains a risk. Read-only classification does not authorize disclosure, replay or automatic remote work. Catalog entries declare read effects and sensitive-data requirements.

CONFIRM_REQUIRED: known effects requiring an explicit target/effect/provider preview and current confirmation, e.g. service restart or DNS flush; these are mutating despite familiar names. HIGH_RISK / MUTATING: policy/account/license/software/device changes require a separately reviewed domain workflow, least privilege, pre/postconditions, truthful audit, recovery/rollback where possible and dedicated tests. Both remain unavailable in initial S2 execution delivery unless independently approved and implemented.

Confirmation defaults to Cancel; displays exact validated target/scope/action/version/effect, not a vague Continue. A changed input/capability/target invalidates it. Safety classification is owned metadata/policy and rechecked by services, never inferred by AI wording.

## Automation Levels

Initial behavior combines SUGGEST_ONLY recommendations with ONE_CLICK_SAFE_READ_ONLY invocation only for explicitly available approved read-only operations: one deliberate click after target/scope preview, fresh owner checks and any required privacy/disclosure consent. Begin delivery with existing local diagnostics; remote cards stay unavailable until reviewed provider delivery. Explicit one-click is not autonomous execution.

AUTO_SAFE_READ_ONLY is DEFERRED, default off and not activated by this plan. Any experiment needs separate USER-approved action/context allowlists, fresh binding, least privilege/capability checks, explicit consent, finite budget/time/output, operation provenance/audit, bounded rate/cooldown, visible activity, stop/pause and failure/reconciliation. A preference cannot permit unsupported operations. Mutating actions never inherit auto-safe eligibility; context change/hover/appearance/animation is not an execution trigger.

## Provider Capability Model

Capability truth is an owner/provider observation: supported action/version/target type, actual composed adapter, scope/mapping, permission/health, observed time/revision and availability reason. Separate supported, configured, authorized, currently reachable and action-ready. Unknown is not false success or a fabricated zero; a cache may advertise only what it actually observed.

Composition determines initial local capability. Remote discovery occurs on explicit owner connect/refresh/use, with finite timeout/rate/negative-cache policy, never flyout hover or DynamicHub opening. Services check current permissions/scope and target again at dispatch. UI visibility/feature flags can suppress capability, never create permission. Do not persist credentials/handles with capability metadata or treat stale read/write flags as permanent consent.

## RMM Architecture

Future flow: DynamicHub intent -> owning application/Diagnostic use case -> catalog/target/capability/security validation -> provider gateway -> reviewed remote operation -> validated normalized owner result. Vendor selection, supported authentication, secure credential references, target/customer mapping, API/license/roles and output/execution-status support remain NOT_VERIFIED. No default tenant-wide grant or RMM account is configured.

Remote device identity is a qualified provider/customer device reference from authoritative mapping and explicit technician acceptance. Never choose the first hostname match or inferred device from copied prose. Gateway accepts typed reviewed operations, not arbitrary code. Provider dispatch acknowledgement establishes acceptance only; store provider execution reference where available, reconcile to confirmed completion or UNCERTAIN. One operation per owning use case initially; no hidden batching, offscreen queue, autonomous remediation or vendor response directly in GUI/domain.

## PowerShell-via-RMM Boundary

A remote read-only operation, if its provider supports it after review, uses a predefined/versioned/digest-bound script or approved provider-native operation. The owner validates declared typed parameters, target/scope, finite deadline/output, least privilege, provenance and exact approved implementation. The gateway handles execution reference/status, bounded parsing and confirmed cleanup/cancellation semantics supported by that provider. AI cannot supply PowerShell bodies, command-line fragments, script paths or replacement implementations.

Current local PowerShellService -> ScriptService -> PowerShellGateway is unchanged: three literal parameterless approved diagnostics, trusted 64-bit PowerShell 7, non-elevated token, sealed exact bytes, owned Job Object, concurrent bounded output, revalidation and strict result validation. The fixed pack remains application-composed, sequential. Valid collection ERROR is a completed collection result; boundary/timeout/cleanup failure has no fabricated diagnostic. Cleanup uncertainty remains latched blocked.

Remote execution is a distinct provider boundary; local Job Object proof is not remote process containment. Review remote runtime/version/modules, least privilege, output/status/cancellation and uncertain-outcome behavior before activation. Missing guarantees disable the remote action; do not add a remote parameter or arbitrary command path to today's local gateway. No script/registry/digest/migration is modified here.

## Microsoft 365 Architecture

Use a Microsoft-owned integration service/gateway for tenant-qualified identity/license/mailbox/security facts. Choose the supported API for the actual fact and authentication model; do not route cloud facts through endpoint RMM PowerShell or assume a generic Graph connection supports Exchange/security data. Map authoritative tenant/user/mailbox IDs; reject ambiguous/cross-tenant mapping. Minimize requested properties and returned pages; credentials/tokens remain integration-private.

FACT Q: Microsoft's [Get user](https://learn.microsoft.com/en-us/graph/api/user-get?view=graph-rest-1.0) documents an explicit property selection and scenario-dependent permissions. Its [List licenseDetails](https://learn.microsoft.com/en-us/graph/api/user-list-licensedetails?view=graph-rest-1.0) currently documents delegated work-account access with permission/role conditions and application access as unsupported. Therefore a generic app-only credential cannot be assumed to enable this candidate action.

Microsoft's [Get-EXOMailbox](https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/get-exomailbox?view=exchange-ps) documents mailbox property retrieval, including targeted identity/property selection; default broad enumeration is inappropriate for a selected-mailbox card. INFERENCE/RECOMMENDATION: use a separately approved bounded Microsoft/Exchange adapter when that fact requires it, with operation-specific RBAC/auth review. No module/auth/session/scopes are installed or granted.

Directory/license read, mailbox read and sign-in read are separate capabilities, each ONLINE_REQUIRED when invoked. Concrete sign-in scope/licensing/retention and actual tenant/account authorization remain NOT_VERIFIED. No exact permission bundle is selected for S2. Verified public docs establish candidate read boundaries, not local/employer provider availability.

## Adobe Capability Assessment

Adobe entitlement query remains FUTURE / NOT_VERIFIED and disabled. No supported authorized API/provider, enterprise account terms, authentication or least-privilege capability was inspected/selected. A catalog slot is not availability. Installed software, running process or RMM inventory can establish only those observations, never entitlement/license assignment. Enable an Adobe license action only after an approved provider/identity/permission/result/failure contract; otherwise offer an existing approved full-tool/manual workflow without a fabricated result.

## Action Request / Result Contracts

Proposed internal DTOs are immutable typed application objects. If a future approved wire boundary needs them, specialize 0B's composite envelope; no new transport is selected and no existing v1 is rewritten.

| Contract aspect | Required semantics |
| --- | --- |
| New wire header | contract, schema_version string MAJOR.MINOR, message_class, message_id, created_at UTC milliseconds, producer.component, payload; conditional context/correlation under 0B |
| Request payload | operation_id, known action_key/definition_version, invocation context revision, exact typed target/provider/tenant scope, schema-validated parameters, requested_by safe attribution, confirmation/policy/capability decision refs and optional Ticket association choice/reference |
| Result payload | Same operation/action/version/binding correlation, target/scope, owner execution and collection outcome axes, start/finish observation times, provider_execution_ref if known, bounded structured observations, safe summary, warnings/completeness/provenance |
| Correlation | RESULT/ERROR gets new message_id, correlation_id equals request message_id; operation_id identifies business invocation, never overloaded as communication identity |
| Outcome | 0B terminal COMPLETED / proven CANCELLED / caller-facing UNCERTAIN or classified ERROR; completed RESULT may contain failed/partial diagnostic collection. S2 view states map without losing owner axes |
| Rejection | Parse/schema/unknown key/version/ID/scope/authorization errors before effect; return safe typed classification, no rejected payload echo or fabricated owner result |
| Bounds/version | Closed action/security fields, strict types/no bool-as-int/NaN, bounded strings/arrays/depth/UTF-8 document; retain existing stricter PS/Mochi limits and 0B caps; profile fixes exact ceilings before delivery |
| Identity/absence | Owner-qualified refs, optional omission means not supplied; null only when declared. New local SQLite wire IDs use canonical positive decimal strings under 0B; in-process ints unchanged; provider IDs opaque and scoped |
| Not carried | Credentials, raw customer histories, arbitrary commands/paths/endpoints/SQL, renderer handles or unbounded source bodies |

No sensitive/admin context is sent through cosmetic Mochi v1. Future acknowledgement/advisory projection profile is bounded (0B initial <=16 KiB), read-only and privacy-reviewed; source minimization precedes serialization. The mechanism/peer-security review is a later separate gate, not a reason to introduce another grammar here. This plan does not claim an executable JSON schema or endpoint exists.

## Result Normalization

Validate provider types/identity/status/errors at its gateway, then translate to a source-owned F7Hub result; GUI consumes safe projections. Retain original target/scope, timestamps, implementation/provider provenance and collection method. Bound arrays/fields, declare units, preserve false/zero/null/empty and distinguish not-collected/redacted/unsupported from actual empty data. Never parse arbitrary console text as authoritative structured health.

Examples: network addresses/DNS/link state are observations, not a verified connectivity/root-cause conclusion; uptime has explicit unit/time; disk free is measured bytes/availability, not remediation; installed app version is inventory, not license; license summary reports confirmed source assignments and completeness, not inferred entitlement from inventory. Keep warnings/partial/failed components visible; no silent truncation or assumed total from one page.

Generated explanation uses Observed / Inferred / Suggested labels with traceable source refs. Store/display structured result independently of prose; AI text cannot overwrite it, mark a Ticket resolved or promote evidence. Current local run/pack types are adapted after their validators without changing collection ERROR, ABORTED/attempted/skipped or cleanup semantics.

## Ticket Recording

Initial default is explicit recording to local Ticket through an implemented approved owner association use case; automatic recording is off/deferred. A confirmed source result plus an explicit invocation-time Ticket choice is eligible for recording only when the required observation API, source privacy/retention and retry/audit path exist. Current add_note/source/is_ai_generated fields are reuse evidence, not a ready System Observation API or universal Evidence table.

Human Quick Note remains human-authored, Ticket-owned and never filled/submitted by S2. Generated/structured observation carries source/time/method/completeness and is distinctly labelled; failed/uncertain outcomes are not successful observations. Evidence is separately accepted source/claim relationship with retention/provenance. A KB RELATED link keeps its current meaning. Ticket Timeline renders confirmed domain/history, not transient shell progress.

Preserve provider outcome independently of recording outcome: SUCCEEDED + recording FAILED/UNAVAILABLE/UNCERTAIN remains that pair. Retry only recording/reconcile original result/captured Ticket, with duplicate-safe owner behavior; post-commit refresh failure says recorded, refresh unavailable. External PSA publication is a separately reviewed use case/default off, never implied by a local note or PUBLIC type.

## Ticket Association

Exact source/result revision and saved Ticket are previewed and validated; source content cannot choose a Ticket. Capture the explicit choice at invocation, including no association. Recheck original Ticket existence/permission/relationship and source eligibility before the recording transaction. No database transaction remains open across provider/AI execution. Unknown commit outcome requires query/reconciliation before another insert.

Later explicit association is its own validated operation, not a change to the original invocation binding. Missing/deleted/unavailable captured Ticket produces truthful recording failure; never substitute current Ticket B. Existing association cardinality, Evidence hold/release and duplicate semantics require the owning feature's inspected contract before activation; no relationship/schema is invented locally.

## Case Journal / Ticketless Behavior

Ticket is optional to troubleshooting. Initial source-owned results may stay in bounded session memory with explicit memory-only/no-restart-recovery status; losing/evicting an in-memory result is not durable Journal storage. Local diagnostics/Knowledge remain usable without a Ticket. No fabricated ticket/session identity or automatic Ticket creation.

Approved 0A-D2 permits future local Journal storage, deterministic case-note drafting/editing before/without a Ticket. That domain owns physical persistence/retention/association and its future service; S2 can consume it when delivered. Journal never becomes a competing Ticket Timeline. Select/reuse existing source/activity/relationship facilities before a dedicated persistence plan; no table decision here. Optional later Ticket association preserves original source/provenance. Journal/draft baseline cannot require PSA, internet or AI.

## Mochi Acknowledgement

Use the retained separate optional tiny overlay lifecycle and accessible application equivalent. Only owner-confirmed completion can say collected/completed; only confirmed recording can say saved to the captured Ticket. Partial, unavailable, failed and uncertain states get truthful concise text, no raw result/customer/credential body. Do not show an identifying Ticket/device label when privacy policy/suppression excludes it.

Current cosmetic v1 has no text delivery. Initial S2 delivery can use existing shell/app feedback while a separately reviewed read-only presentation adapter is deferred. Pet absence/paused/hidden/provider failure cannot remove operation results or block services. Overlay never takes focus, becomes a mandatory button panel or expires the only recovery route; duration/geometry are bounded native detail.

## DynamicHub Surface

Consume the retained single-region contract: Context, What happened, a small approved action set, Recent result/warnings and Open Full Tool. Show actual availability and why suggested, exact eligible target/safety/provider and confirmation state. Initial cached/local bounded projection only; opening costs no provider call/inference. Render untrusted text plain/bounded with no executable link or HTML shortcut.

One expanded occupant; dirty Quick Ticket/inspector and modal/pending guards prevail. Explicit close hides/relinquishes presentation, never cancels a provider run, discards an owner draft or authorizes recording. Results for another context carry original identity and deliberate navigation. No primary navigation, second Ticket editor or independent permanent right dock.

## Trigger / Cooldown Model

Initial automatic triggers produce only a minimized indicator and deterministic local suggestion refresh; explicit USER open requests the slot/focus after guards. Future preference-driven expansion requires vacant clean slot, no editing/modal interaction, current eligible context/privacy and no dismissal suppression; otherwise indicator only. Result success/failure is not permission to displace a dirty surface.

Deduplicate by source owner/ref/revision, current projection generation, action/result identity and trigger reason, not raw content hash or customer label. Initial informational cue cooldown recommendation 30 seconds, at most one pending coalesced cue; exact finite timing is implementation detail. Explicit dismiss suppresses that trigger/context-result generation until deliberate reopen or a genuinely new eligible source/operation event. No immediate reopen loop on the same event; no every-keystroke/capture/timer/hover trigger, provider polling or forced focus.

The Trigger Matrix controls each stimulus. Privacy/lock/app-inactive state hides identifying cues and transient overlays; returning focus does not automatically restore raw context or replay work. An important failure remains reachable in owner result/status, not repeated animations.

## Suggestion Ranking

Default deterministic rules filter by supported catalog/version, resolved target/input, source eligibility, scope/permission availability, safety and actual composed capability before ranking. Rank current explicit need, relevant source finding, prerequisite satisfaction and recent confirmed owner outcome; stable tie-break by approved priority/key. Limit to 3-5 cards; More opens a bounded local list/full owning tool.

Optional AI may explain/reorder only the eligible keys, using reviewed minimized inputs; validate output against the same closed candidate set and typed schema. Reject invented key/target/ID/capability/unsafe parameter, disclose advisory origin and fall back to deterministic ranking. No dependency on model/provider availability, no inferred permission from AI confidence and no provider refresh to decorate a card.

## Follow-Up Actions

Definitions declare reviewed semantic rules over normalized structured observations and eligibility; outcome/version/source refs bind each candidate. Examples: missing gateway can suggest approved adapter/configuration review; weak signal can suggest approved Wi-Fi details; a license-read result can suggest opening the relevant full tool, not automatic license mutation. Suggestions remain unexecuted until explicit intent and fresh validation.

No follow-up creates a recursive execution chain. Bound displayed rules/candidates, track per-operation presentation generation and suppress duplicate suggestions. Uncertain operation suggests status reconciliation, never rerun mutation. Partial data does not satisfy missing prerequisites. No AI-generated script or free-form command enters dispatch.

## Security

Security final architecture check: 13/13 PASS in the explicit matrix below, with no production trust-boundary changes. Fail closed on missing owner capability, target/mapping, required consent, current permission or valid result. Least privilege and source purpose apply to read-only operations as well as mutation. GUI/pet/cached metadata only present intent/state; they cannot authorize effects or access records directly.

Sensitive transport, provider authentication/secure credential references and mutating workflows require separate reviewed boundaries before delivery. Existing same-user cosmetic channel is not a privileged authenticated ingress. Producer component/checkout digest/window title/feature flag is not identity/permission proof. No credential setup, arbitrary endpoint, elevation, ambient broad account grant or test customer data.

## Privacy

Minimize capture -> projection -> outbound preview -> result -> recording independently. Clipboard's complete mandatory assessment precedes derivation/disclosure; POSSIBLE_SECRET/assessment failure is blocked, no raw override/hash/secret quarantine. NEEDS_REVIEW sensitive content is not default Mochi/AI/provider material. Redacted derivative gets new identity, full reassessment and provenance without original secret offsets/hash/value.

Initial DynamicHub uses owner refs and safe coarse facts, with identifying labels concealed by policy. No background clipboard monitoring, screenshots/OCR/window text/customer history extraction or automatic provider/AI feed. Explicit raw Inspector access, Save/Pin or Ticket association does not authorize onward AI transmission. External AI needs exact minimal payload preview + explicit Send and verified employer/provider/credential policy; unavailable policy disables Send. Diagnostic summaries/Entities remain source/purpose-gated.

Bounded session projections clear on privacy/session transitions and expiry; owner persistence/deletion remains source-owned. Log validated operation/message IDs, action/source category, duration and safe error code only when purpose-eligible; no raw Clipboard/Ticket/diagnostic body, credential, rejected payload, URL/path/Entity literal or provider exception dump. Existing technical logger is not audit evidence; meaningful audit/retention requirements must exist before sensitive action activation. No physical zeroization or perfect secret-detector claim.

## Offline Behavior

LOCAL_REQUIRED: navigation, context availability explanation, deterministic suggestions over eligible local facts, existing Ticket drafts/Knowledge queries/local diagnostics when their local requirements exist. Future local Clipboard/Journal storage/drafts follow their owners and do not require cloud AI/PSA. Some source refs may be absent without disabling unrelated tools.

ONLINE_OPTIONAL: external AI explanation/optional provider-enriched suggestions; failure falls back to local deterministic suggestions/results and drafts. ONLINE_REQUIRED: invoked RMM/Graph/Exchange/licensing reads; absent connectivity shows UNAVAILABLE for that action, no fake local substitution. A remote operation cannot be silently queued for later execution against stale selection. PSA publication and future outbox are separate, explicitly approved domains.

## Provider Failures

Classify before-dispatch rejection versus accepted/in-flight unknown versus confirmed owner outcome. The Failure Matrix fixes retry/recording/UI/log behavior for all required cases. Bound each admitted action's finite timeout/output and provider request rate; preserve original refs through timeout, cancellation inquiry and late confirmation. Credential/permission/target/schema failure is not transient retry advice.

Initial policy: no automatic provider operation retry. Explicit retry before proven dispatch may request a new fresh operation; after ambiguous dispatch reconcile by provider execution ref/status where supported, otherwise UNCERTAIN. An idempotent safe-read retry must be explicitly declared by its reviewed owner and still not imply mutation replay. Proposed status-query budget: at most two attempts and ten elapsed seconds total, honoring provider delay/timeout; beyond budget leave reachable UNCERTAIN, no blocking sleep/loop. Per-operation adapter may require stricter limits before delivery; unsupported reconciliation never invents an API.

## Idempotency / Reconciliation

0B message_id identifies communication; operation_id identifies accepted business intent. Same logical message redelivery retains ID/content identity; same ID with different validated content is conflict. Same action_key is not the same operation. New intent has new identity and fresh checks. Source result/provenance correlates both.

Owning adapter uses provider execution/status reference and declared deduplication only when supported. A local UI click guard or caller message cache is not exactly-once provider execution. Accepted response lost means UNCERTAIN, not FAILED so retry. Confirmed completion may arrive after caller timeout; record original-target outcome once and update only matching view generation. Preserve uncertain cleanup separately from timeout/health.

Ticket association retry uses a separate owner recording identity keyed to the original authoritative result/captured Ticket and intent revision, with transactional duplicate protection/reconciliation before activation. No provider rerun, no generic outbox mandated, no replay across app restart. Declared cancellation needs owner confirmation; hiding/Exit request/timeout cannot turn completed effects into cancelled. Future mutating action cannot activate without its dedicated reconcile/audit/recovery contract.

## Settings Inputs

Consume 0D shared definitions/snapshots, not a new JSON/INI/SQLite store. Proposed names below are semantic candidates, not registered keys. Safe static defaults apply until the shared consumer exists.

| Input | Classification / proposed default | Application / limit |
| --- | --- | --- |
| Mochi / DynamicHub presentation enabled | LIKELY preference; optional, context sharing off | Presentation consumer; unavailable renderer cannot disable services |
| Suggestion count/verbosity | LIKELY bounded preference; compact 3-5 | Next projection; hard source/cap bounds retained |
| Acknowledgement duration | LIKELY finite preference; short, native tuned | Next acknowledgement; accessible durable recovery remains |
| Important-result auto-open | FUTURE preference; off | Only clean vacant slot/no editing/modal/privacy conflict; never focus/displacement authority |
| Informational cooldown | LIKELY bounded preference; initial 30 s recommendation | Next cue; dismissal/generation rule not disableable |
| Provider feature flag | LIKELY enablement preference; off until reviewed capability | Can suppress; cannot invent support/auth/scopes |
| AUTO_SAFE_READ_ONLY | DEFERRED opt-in; off | Separate approved experiment; not shipped/autonomous by this plan |
| Automatic local Ticket observation | FUTURE opt-in; off | Explicit recording baseline; owner privacy/confirmed outcome/duplicate safety required |
| External AI/context sharing | FUTURE consent/presentation input; off | Exact preview/Send and policy gate independent of toggle |
| Current context/lease/draft/binding/result refs | RUNTIME STATE / NOT SETTINGS | Owner session lifetime; no restart replay or durable restoration |
| Provider discovered permission/health | DERIVED CAPABILITY / NOT SETTINGS | Integration observation with freshness, not user-granted authority |
| Credential/token/runtime handle | SECRET/private runtime / NOT SETTINGS | Approved future integration-private reference/transient retrieval |
| Catalog/safety/validation/secret exclusion | CONTRACT / SECURITY INVARIANT / NOT SETTINGS | Cannot be overridden by convenience preference |

Definitions belong to each module but admission/resolution/persistence to shared 0D owner. Apply presentation changes safely on the next consumer event; operation-bound policy/target remains frozen, while current authorization still revalidates at effect boundaries. Saved preference differs from applied renderer/provider state; report unavailable/unconfirmed rather than claiming a toggle worked.


## Required Matrices

These are RECOMMENDATION matrices at architecture depth. CURRENT_BOUNDARY means inspected source exists, not fresh runtime PASS; FUTURE means capability unavailable until separately delivered/reviewed. Initial action/card support also depends on the future S1/S2 presenter/catalog adapters.

### Context Matrix

| Context | Reference source | Safe projection | Freshness | Required validation | AI exposure | Provider exposure | Ticket use |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Company | Company service / explicit S1 selection | Optional qualified ID and concealed safe label | Owner revision/availability | Exists/allowed; compatible Ticket/contact scope | No customer label by default; purpose review | Only necessary confirmed customer mapping | Relationship validated, no inferred Ticket |
| User | Future identity/Microsoft/provider owner, distinct from Contact | Optional scoped ID/type, label concealed | Mapping/observation time | Tenant/account/object match and permissions | Coarse type initially, no email/history | Exact approved query identity only | Optional captured association; user does not choose Ticket |
| Device | Future Device/RMM mapping owner; local operation scope separate | Scoped device ref, no hostname invention | Owner mapping/capability revision | Exact customer/tenant target; ambiguity blocks | No raw device inventory initially | Validated approved target only | Original binding; source/device relation verified |
| Ticket | TicketService, saved Ticket explicitly selected | Qualified ID, minimized number/status when eligible | Owner validation plus invocation snapshot | Existence/permission/relation/draft guard | No subject/notes/history; raw excluded default | Omitted unless use case requires approved metadata | Optional exact invocation choice; no current-at-completion lookup |
| Tenant | Microsoft/provider mapping owner | Optional qualified tenant ref, no token | Mapping/auth scope observation | Exact tenant/customer/account scope | Omit identifiers by default | Required authorized tenant routing, not prose | Captured relationship only, never cross-tenant substitution |
| Clipboard Item | Clipboard owner, explicit eligible selected ref/revision | Kind/coarse facts, approved derivative preview only | Availability/expiry/sensitivity/revision | Complete gate, purpose/retention, ref not permission | Default off; selected safe projection only after review; external preview/Send | No raw/default forwarding; schema-approved necessary safe values only | Explicit source+captured Ticket; separate accepted Evidence |
| Entity | Source occurrence/0C resolver | Type, approved safe literal/ref only when needed | Source and resolver generation | Occurrence is not canonical ID; explicit authoritative resolution | Sensitive literal omitted; confidence advisory | Validated mapped typed value, never executable fragments | Cannot infer Ticket/provider target |
| Diagnostic result | PowerShell/Diagnostics owner exact run/result | Status/completeness/safe observations, no full raw payload | Operation/source version and observation time | Owner outcome/schema/cleanup, target and purpose | Optional reviewed summary, not health assertion | Follow-up parameters validated separately | Source result preserved; optional captured Ticket recording |
| Knowledge article | KnowledgeService selected article/version | Article ref/state, bounded eligible title concealed default | Owner current version/availability | Read permission/lifecycle; original revision retained | No whole article dump; explicit permitted excerpt review | None for default local KB | RELATED link stays that meaning; no automatic Evidence |
| Script | ScriptService registration | Key/version/policy readiness, no body/path by default | Current metadata/verified source at execution | Literal eligibility, exact bytes/runtime; no context-derived parameters | Metadata explanations only, no body-to-executor | Remote implementation only by reviewed independent adapter | Execution result only, no automatic note from copied script |

### Capability Matrix

| Action key | Purpose | Target type | Safety class | Owning service | Potential provider | Capability required | Confirmation | Result schema | Ticket-recording policy | Offline? | MVP / Later / Not Verified |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| diagnostic.windows.system_snapshot | Local OS/uptime/memory/drives | Explicit this-PC local scope | SAFE_READ_ONLY | Existing PowerShellService / Diagnostics ownership | Local PowerShell 7 | Literal current registry/policy/bytes/runtime/cleanup | Explicit Run/target preview; no new target params | Existing validated System v1 adapted | Off default; future approved observation API | LOCAL_REQUIRED, runtime prerequisites | CURRENT_BOUNDARY; S2 adapter later |
| diagnostic.windows.network_snapshot | Local interface configuration | This PC | SAFE_READ_ONLY | PowerShellService | Local PowerShell 7 | Same; no invented ping/DNS testing | Explicit Run | Network v1; configuration not connectivity | Same | LOCAL_REQUIRED | CURRENT_BOUNDARY; adapter later |
| diagnostic.windows.services_snapshot | Local service state/startup info | This PC | SAFE_READ_ONLY | PowerShellService | Local PowerShell 7 | Same; no restart/stop capability | Explicit Run | Services v1; stopped not fault | Same | LOCAL_REQUIRED | CURRENT_BOUNDARY; adapter later |
| diagnostic.pack.local_baseline | Sequential local baseline | This PC | SAFE_READ_ONLY | PowerShellService pack use case | Local PowerShell 7 | All three current identities; reservation/cleanup | Explicit pack Run | Existing pack attempted/skipped/collection axes | Same, no member spam | LOCAL_REQUIRED | CURRENT_BOUNDARY; adapter later |
| device.network_snapshot | Approved remote network observations | Validated scoped Device | SAFE_READ_ONLY after review | Future Diagnostic/application use case | RMM | Reviewed script/provider, mapping, permissions/status/output | Explicit target/scope and any disclosure consent | Versioned bounded network observations | Explicit optional original-Ticket recording | ONLINE_REQUIRED | FUTURE / provider NOT_VERIFIED |
| device.uptime | Remote uptime read | Scoped Device | SAFE_READ_ONLY after review | Future Diagnostic use case | RMM/native approved read | Actual reviewed operation and least privilege | Explicit target/scope | Duration/unit/time/completeness | Same | ONLINE_REQUIRED | FUTURE |
| device.disk_free | Remote free-space read | Scoped Device | SAFE_READ_ONLY after review | Future Diagnostic use case | RMM/native approved read | Actual reviewed operation, size/output limits | Explicit target/scope | Drives/bytes/availability/time | Same; not remediation | ONLINE_REQUIRED | FUTURE |
| m365.user_summary | Minimized directory facts | Tenant-qualified User | SAFE_READ_ONLY after review | Future Microsoft integration service | Graph | Correct auth/operation/properties/permissions | Explicit target/tenant; privacy gate | Confirmed selected properties/time | Explicit eligible safe observation only | ONLINE_REQUIRED | FUTURE; docs verified, account NOT_VERIFIED |
| m365.license_summary | Confirmed assigned license details | Tenant-qualified User | SAFE_READ_ONLY after review | Microsoft integration service | Graph operation supported by actual auth | Delegated supported permission/role for candidate licenseDetails; not assumed app-only | Explicit target/tenant | Assignment/source/completeness, not software inventory | Same | ONLINE_REQUIRED | FUTURE / permissions NOT_VERIFIED |
| m365.mailbox_summary | Approved mailbox properties | Scoped Mailbox/User mapping | SAFE_READ_ONLY after review | Microsoft/Exchange integration service | Exchange or verified suitable Microsoft API | Operation-specific auth/RBAC and bounded property selection | Explicit mailbox/tenant | Safe mailbox property DTO | Same; no raw mail content | ONLINE_REQUIRED | FUTURE / operation delivery deferred |
| security.signin_summary | Eligible sign-in observations | Scoped Tenant/User | Sensitive SAFE_READ_ONLY only after review | Microsoft/security owner | Approved Microsoft API | Specific scopes/license/retention/purpose NOT_VERIFIED | Explicit target/disclosure; sensitive review | Bounded observation/window/completeness | Off; explicit reviewed eligible summary | ONLINE_REQUIRED | FUTURE / NOT_VERIFIED |
| adobe.license_summary | Authoritative entitlement read | Qualified Adobe account/user | Class NOT_VERIFIED until operation inspected | Future licensing integration owner | Adobe/authorized licensing source | Authorized supported API/account/permissions | Unavailable; define after provider review | Entitlement source/time, no inventory inference | None until approved source semantics | ONLINE_REQUIRED if supported | NOT_VERIFIED / disabled |

Future keys are candidates, not registered operations. No remote target is passed into today's local parameterless definitions. Readiness for all actions is recomputed at invocation.

### Provider Matrix

| Provider | Authority | Credentials owner | Capability discovery | Target mapping | Request boundary | Result normalization | Rate/failure behavior | Offline behavior | NOT VERIFIED items |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Local PowerShell/Diagnostics | Fixed local collection/result, not workflow/Ticket | No provider credentials; current standard-user token check | Composed literal policy/current registration; Run rechecks | Explicit this PC only, no generalized Device ID | PowerShellService -> verified candidate -> sealed gateway | Existing strict per-operation validators; execution/collection separate | Single reservation; <=60 s registry policy; 1 MiB stdout/64 KiB stderr gateway; cleanup latch | Local prerequisites only | Installed runtime/native/operational registry health not tested here |
| RMM | Remote execution/status provider, not domain owner | Future approved integration/secure reference boundary | Explicit owner connect/refresh; finite observations, no hover poll | Confirmed provider/customer/device IDs | Owner use case -> approved typed gateway operation | Validate vendor DTO then owner schema/provenance | No automatic run retry; explicit status reconcile when supported; finite budgets | Remote unavailable only; local work preserved | Vendor/API/auth/license/mapping/permissions/status/remote containment |
| Graph | Microsoft directory/license/security provider | Future Microsoft integration-private auth | Per-operation actual auth/scope/role/health check | Tenant + authoritative object ID | Microsoft service -> typed operation adapter | Minimized versioned properties; no GUI vendor JSON | Bounded pages/output; classified rate/auth/partial/uncertain; no consent escalation | Invoked remote reads unavailable | App/tenant credentials/permissions/license; sign-in specifics |
| Exchange Online | Mailbox property provider | Microsoft/Exchange integration-private auth/RBAC | Explicit operation/role/module/API readiness | Validated mailbox-to-tenant/user mapping | Reviewed Microsoft service/gateway; no free-form cmdlet text | Selected bounded properties, safe absence/partial states | Finite request/deadline; no unlimited enumeration or install/auth fallback | Remote read unavailable | Actual module/session/RBAC/fact-specific operation support |
| Adobe/licensing | Entitlement only if supported source verified | Future approved licensing integration | No discovery assumed; disabled slot | Authorized account/product/user mapping required | Future reviewed owner/gateway only | Confirmed entitlement DTO; inventory kept separate | Unknown until inspected; no fake fallback/retry | Local inventory is a separate observation | All provider/account/API/permission/terms/retention |
| Optional AI | Advisory derivation/ranking, no action/result authority | Reviewed AI integration-private boundary | Explicit configured supported model/provider, policy and input/output limits | Safe context projection, never account/device ID resolution | Reviewed minimal preview/Send for external requests | Validate candidate keys/plain explanation; reject executable/invented outputs | Finite timeout; deterministic fallback; no automatic Send/retry loop | Local guidance/suggestions survive | Model/provider/auth/retention/employer policy; no provider chosen |

### Action Safety Matrix

| Action | Read-only? | Side effects? | Safety class | Confirmation | Auto-safe eligible? | Ticket record? | Audit? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Approved local snapshot/pack | Intended target read | Process/resource usage; separate optional recording | SAFE_READ_ONLY | Explicit Run and local target | DEFERRED; no automatic eligibility now | Explicit future approved observation | Existing safe run feedback; future association audit required |
| Reviewed RMM network/uptime/disk read | Intended read if reviewed | Provider execution/audit/load and data disclosure | SAFE_READ_ONLY after review | Explicit target/scope/disclosure | DEFERRED; separate experiment only | Explicit eligible summary | Source/version/actor/target/outcome safe provenance |
| Microsoft user/license read | Intended read | Sensitive identity/license disclosure, provider logs | SAFE_READ_ONLY after review | Explicit validated tenant/user/purpose | DEFERRED, sensitive policy required | Explicit safe observation | Owner/integration audit requirements before activation |
| Sign-in read | Intended read | Sensitive security/privacy exposure | Sensitive read, separate review | Explicit target/window/disclosure | Not baseline eligible | Off until reviewed purpose | Required sensitive access evidence |
| Restart service / flush DNS | No | Operational/network change | CONFIRM_REQUIRED | Target/effect/version, Cancel default | NO | Dedicated approved mutation record | Required pre/post/outcome/recovery |
| Stop process / renew networking | No | Session loss/connectivity change | CONFIRM_REQUIRED or higher by reviewed effects | Dedicated validated workflow | NO | Dedicated approved record | Required; uncertainty/recovery |
| Remove license / disable account / uninstall | No | Access/data/software disruption | HIGH_RISK / MUTATING | Separate reviewed permissions/preconditions/recovery | NO | Authoritative mutation outcome | Required, no AI-only approval |
| Adobe entitlement read | NOT_VERIFIED | NOT_VERIFIED | NOT_VERIFIED | Disabled pending review | NO | None pending verification | Define through licensing owner |
| Ticket recording/association | No, local domain write | History/relationship/retention change | Owner-reviewed local write, separate from provider safety | Explicit source + original saved Ticket | Auto-record DEFERRED/off | This is the recording step | Required truthful commit/idempotency evidence |

Read-only provider action and its optional Ticket write are different safety/effect boundaries. Neither adopts arbitrary PowerShell because a pasted string looks diagnostic.

### Ticket Recording Matrix

| Action outcome | Local result record | Ticket observation | Technician note | Evidence | External PSA sync | Mochi acknowledgement |
| --- | --- | --- | --- | --- | --- | --- |
| Successful read-only | Source-owned confirmed result; initially memory-only | Explicit original-choice recording if owner API/policy exists | No automatic draft/create | Only separately accepted eligible relationship | Off/deferred | Collected; Saved only after confirmed local recording |
| Partial action | Partial result with missing/warnings/source/time | Explicit partial-labelled safe summary; no omitted-component success | No automatic note | Explicit eligible partial source with completeness | Off/deferred | Partial result, details/recovery available |
| Failed action | Classified execution failure; no fabricated observations | Off by default; optional owner-defined failure event, not successful Observation | No automatic note | No invented evidence; actual failure artifacts only if reviewed | Off/deferred | Failed truthfully, safe reason |
| Uncertain action | Pending/uncertain owner evidence and original binding | No success recording; optional explicitly labelled uncertain activity only if owner supports it | No automatic note | No completed-evidence assertion | Off/deferred | Outcome unconfirmed; Reconcile |
| Mutating action | Dedicated reviewed mutation result/pre-post facts; not baseline enabled | Separate mutation-owned history after confirmation | No automatic Quick Note | Reviewed accepted provenance only | Separately approved publication | Confirmed change or uncertain/failed; never dispatch=Done |
| Provider unavailable | Local classified not-started outcome/status | No observation spam; no invented source result | No automatic note | None | Off/deferred | Unavailable, local alternatives |
| Provider success + recording failed | Original provider result unchanged | FAILED/UNAVAILABLE/UNCERTAIN independent; original-Ticket-only recording retry | Human draft untouched | Relationship not accepted until owner confirms | Off/deferred | Collected; recording failed/unconfirmed, not Saved |

Recording disabled/missing is UNAVAILABLE, not an attempted failed write. No-Ticket/no-association stays valid; later association is explicit. Cards/history do not create durable persistence by themselves.

### DynamicHub Trigger Matrix

| Trigger | Opens automatically? | Suggestion only? | Focus? | Cooldown? | Dismissal behavior? | Privacy risk? |
| --- | --- | --- | --- | --- | --- | --- |
| USER explicit open | Not automatic; guarded slot request | Local approved set, no execution | Explicit successful open only | No artificial delay; deduplicate repeated open | USER close suppresses same generation cues | Safe selected projection; identifying defaults concealed |
| Active-context change | Default NO; indicator/local reprojection | YES | Never | Coalesce revision; initial 30 s info budget | Dismissed same generation not reopened | No copied records or automatic disclosure/provider refresh |
| Selected actionable Entity | Default NO; eligible local cue | YES, after source/resolution eligibility | Never | Source/ref/revision keyed | Respect dismissal; unresolved IDs remain unavailable | Literal sensitive; no canonical target inferred |
| Selected eligible Clipboard Item | Explicit selection cue only, not capture stream | YES after complete privacy gate | Never | Source revision, one coalesced cue | Same-generation suppression | No raw/secret auto feed, expiry invalidates |
| Confirmed action completion/new useful result | Default indicator; optional future clean-vacant safe expansion | YES; original operation binding retained | Never automatically | Operation result once + dedup follow-ups | Viewed/dismissed event does not retrigger on repaint | Earlier-context labels concealed as required |
| Action failure / partial / uncertain | Default indicator + reachable owner recovery | YES; reconcile/full-tool routes | Never automatically | No repeated nagging; one event-specific cue | Recovery remains reachable after dismissal | Classified reason, no payload/exception body |
| Provider unavailable/recovery required | Default indicator on explicit attempted use/result | Safe alternative/reconnect route | Never automatically | Finite negative state; no timer polling | Dismissed state only new evidence/explicit open changes it | No token/tenant/customer details in cue |
| USER dismiss / privacy suppression | NO | No renewed cue for same generation | Return under S1 guard only | Suppress until explicit reopen/new eligible event | Retain owner draft/results, release slot | Clear projections/overlay, no persistence/export |

Future auto-open remains a presentation option only; it cannot invoke AI/provider/actions or replace an inspector/dirty Quick Ticket.

### Failure Matrix

| Failure case | Action status | Retry | Ticket behavior | Mochi message | DynamicHub behavior | Log/audit policy |
| --- | --- | --- | --- | --- | --- | --- |
| No active required target | BLOCKED, not dispatched | Explicit select/resolve then new intent | No association; ticketless reads that do not require it still allowed | Select an eligible target | Disabled reason/Open Full Tool | Safe code; no guessed ID |
| Stale context | BLOCKED before acceptance | Fresh owner validation/new confirmation; no substitution | Captured ongoing writes unaffected | Context needs refresh | Disable stale cards, preserve original results | Revision/category only if safe |
| Provider disconnected | UNAVAILABLE, no proven start | Explicit reconnect through owner/new validated intent | No result write/spam | Provider unavailable | Local alternatives; no app-wide failure | Safe provider category/code |
| Provider auth expired | UNAVAILABLE/UNAUTHORIZED | Approved auth owner recovery, no silent login/escalation | No new write | Provider sign-in required | Disabled action/recovery route | Never token/response credentials |
| Provider permission denied | BLOCKED/UNAUTHORIZED | No automatic retry; approved permission review | No write/target fallback | Action not permitted | Explain safe reason; no broad-scope request | Safe denied code; required access audit |
| Target offline | UNAVAILABLE or owner-declared failed/uncertain if dispatched | New explicit attempt only when safe; reconcile accepted work | No success observation | Target unavailable/unconfirmed | Status/full-tool route; original scope kept | Safe code/operation ref |
| Timeout | UNCERTAIN if acceptance/effects unknown; confirmed local termination retains actual timeout/cleanup | Reconcile, never blind replay | No successful recording until confirmed | Outcome unconfirmed / timed out as proven | Original card, status inquiry if supported | Timeout/cleanup axes, no raw stderr |
| Partial result | PARTIAL view over owner COMPLETED partial result | Explicit missing-component action, new identity | Explicit partial-labelled summary if eligible | Partial information collected | Warnings/completeness, no false total | Safe completeness/outcome |
| Malformed result | FAILED contract validation; dispatch may remain uncertain | No arbitrary parse fallback; owner reconcile if needed | No fabricated observation | Result could not be verified | Nonactionable data, owning recovery | Safe validation code; no offending payload |
| Ticket write failure | Provider outcome unchanged; recording FAILED/UNAVAILABLE/UNCERTAIN | Recording-only retry/reconcile, original captured Ticket | No other Ticket; no duplicate unknown commit | Collected; recording failed/unconfirmed | Separate badges and Retry recording | Source/recording IDs/commit truth, no note body |
| Mochi unavailable | Action outcome unchanged | Explicit renderer recovery optional | Normal association behavior unchanged | No pet output; accessible app feedback | Existing panel/owner result still works | Cosmetic unavailable safely; no run retry |
| DynamicHub unavailable | Owner operation outcome unchanged | Guarded Open Full Tool / UI recovery | Owner recording lifecycle independent | Optional safe app/pet cue | No widget-dependent execution; no lost result | Safe surface error; no provider replay |
| AI unavailable | Deterministic suggestions; no execution failure fabricated | Explicit future AI request after recovery/policy; no automatic Send | Structured result/recording unchanged | Local guidance available | Approved deterministic cards/structured facts | Safe AI status, no prompt content |
| Rate limit | UNAVAILABLE/not started or UNCERTAIN by dispatch evidence | Honor provider delay; explicit bounded retry/status, no tight loop | No spam or duplicate recording | Provider busy, try later | Disabled until permitted owner freshness; local alternatives | Safe category/retry timing, no raw reply |
| Uncertain provider execution | UNCERTAIN caller observation, owner operation may continue | At most bounded status reconcile; no mutation replay | No success assertion; late original-result association when confirmed | Outcome unconfirmed | Original operation remains reachable across context switch | Dispatch/ref/time/classification; meaningful uncertainty evidence |

## Security Final Check

PASS below means the design explicitly preserves each invariant and the candidate introduces no production enforcement bypass. It is not proof of future deployed enforcement.

| ID | Required invariant | Evidence / design check | Result |
| --- | --- | --- | --- |
| SEC-01 | No arbitrary AI-generated PowerShell execution | Catalog closed keys/typed input; reviewed exact implementation only; P/Action Catalog | PASS |
| SEC-02 | No direct DynamicHub -> provider execution | Owning service validation -> gateway in all action/provider flows | PASS |
| SEC-03 | No direct GUI -> SQLite writes | Ticket/source repositories own persistence; no production edits/schema invocation | PASS |
| SEC-04 | No credentials exposed to Mochi | Cosmetic v1 unchanged; future read-only projection excludes secrets, integration-private auth | PASS |
| SEC-05 | No permission inferred from UI visibility | Capability display distinct from current owner authorization/consent | PASS |
| SEC-06 | No stale-target execution | Revision/mapping/source/permission checks at acceptance/dispatch; no substituted target | PASS |
| SEC-07 | No completion-time operation retargeting | Frozen binding/card correlation, captured Ticket-only recording/retry | PASS |
| SEC-08 | No autonomous mutating actions | Initial explicit reads; mutating workflows separate, auto-safe deferred and read-only | PASS |
| SEC-09 | No raw secret logging | Privacy/source preflight/gates; classified IDs/codes only; no raw exceptions/payload | PASS |
| SEC-10 | No blind retry of uncertain mutation | Provider/recording reconcile before retry; no exactly-once assumption | PASS |
| SEC-11 | No cross-tenant inference | Scoped authoritative mapping; mismatch/ambiguity blocks | PASS |
| SEC-12 | No fabricated provider IDs | Entity/label/prose never canonical ID; absence valid or action blocked | PASS |
| SEC-13 | No installed-software -> license-entitlement assumption | Adobe deferral, normalized inventory/entitlement separation | PASS |

Security architecture check: 13/13 PASS. No secret material was added; no provider credential was accessed or configured.


## Required Diagrams

RECOMMENDATION: eight Mermaid sources describe architecture/data flow, not existing endpoint/classes. Future gateways/presentation adapters remain unavailable until separately approved delivery. Ownership arrows do not reverse service construction. Static structure/manual boundary review is separate from compilation/rendering, which is NOT RUN; no renderer is installed.

### 1. Context -> Mochi -> DynamicHub suggestion flow

~~~mermaid
flowchart LR
  S1[Application selected refs and revision] --> P[Owner validated minimized projection]
  P --> Rules[Local deterministic candidate rules]
  P -->|optional separately reviewed input| AI[Advisory AI sublayer]
  AI -->|untrusted known keys only| Validate[Catalog and output validation]
  Rules --> Validate
  Validate --> DH[DynamicHub approved suggestion cards]
  Validate -->|optional safe presentation only| M[Mochi cue]
  M -->|explicit open request| DH
~~~

### 2. DynamicHub -> Action Catalog -> provider execution

~~~mermaid
flowchart TD
  U[Explicit technician intent] --> DH[DynamicHub presenter]
  DH --> C[Static catalog key and typed proposal]
  C --> S[Owning application service]
  S --> V[Current target scope policy permission confirmation checks]
  V --> B[Accepted immutable operation binding]
  B --> G[Reviewed operation gateway]
  G --> Provider[Approved local or external provider]
  Provider --> N[Validate and normalize source result]
  N --> Owner[Owning result authority]
  Owner -->|safe projection| DH
~~~

### 3. RMM -> approved PowerShell read-only flow

~~~mermaid
flowchart TD
  I[Explicit bound remote read intent] --> S[Diagnostic application use case]
  S --> Check[Validated device customer scope and actual RMM capability]
  Check --> Def[Reviewed versioned script and declared typed parameters]
  Def --> R[RMM gateway]
  R -->|approved operation only| PS[Provider controlled remote PowerShell]
  PS --> Status[Provider execution ref and bounded structured output]
  Status --> V[Gateway and owner schema validation]
  V --> Result[Original target result or uncertain outcome]
  Local[Existing sealed local gateway] -.->|separate boundary no remote target extension| S
~~~

### 4. Microsoft 365 query flow

~~~mermaid
flowchart TD
  DH[Explicit M365 action key] --> S[Microsoft integration service]
  S --> Scope[Tenant object mapping auth permissions and purpose]
  Scope --> Choose[Reviewed fact specific adapter]
  Choose --> Graph[Graph supported user or license read]
  Choose --> Ex[Exchange supported mailbox read]
  Choose --> Sec[Separately reviewed security read]
  Graph --> N[Validate bounded DTO and normalize]
  Ex --> N
  Sec --> N
  N --> R[Owner result with original tenant and target]
  R --> View[Safe DynamicHub projection]
~~~

### 5. Result -> Ticket observation -> Mochi acknowledgement

~~~mermaid
flowchart TD
  Result[Confirmed source result and original binding] --> Choice{Captured Ticket recording choice}
  Choice -->|none| Keep[Source owned ticketless result]
  Choice -->|explicit exact Ticket| Validate[Ticket and source privacy eligibility checks]
  Validate --> API{Reviewed association API available}
  API -->|no| Unavail[Recording unavailable result unchanged]
  API -->|yes| Write[Ticket owner transaction and duplicate guard]
  Write --> Outcome[Confirmed recording or separate failure uncertainty]
  Outcome --> Timeline[Ticket history only when committed]
  Result --> Feedback[Safe app status and result card]
  Outcome --> Feedback
  Feedback -->|optional truthful bounded output| Mochi[Mochi acknowledgement via future reviewed adapter]
~~~

### 6. Failure / uncertain-outcome reconciliation

~~~mermaid
flowchart TD
  Intent[Bound accepted operation] --> Dispatch[Owner dispatch evidence]
  Dispatch --> Known{Confirmed outcome}
  Known -->|yes| R[Owner normalized result]
  Known -->|no after possible dispatch| U[Uncertain caller observation]
  U --> Query{Provider status inquiry supported}
  Query -->|yes explicit bounded inquiry| S[Original execution ref inquiry]
  S --> KnownLater{Now confirmed}
  KnownLater -->|yes| R
  KnownLater -->|no budget exhausted| Hold[Reachable uncertain state no replay]
  Query -->|no| Hold
  R --> Record[Optional original Ticket recording]
  Record --> Fail[Recording failure or unknown commit]
  Fail --> Reconcile[Recording owner query or safe retry only]
  Reconcile --> Record
~~~

### 7. Capability -> action availability

~~~mermaid
flowchart TD
  Def[Known catalog and source definition] --> Filter[Presentation eligibility filter]
  Adapter[Actual composed supported adapter] --> Filter
  Cap[Fresh owner capability health and scope] --> Filter
  Context[Validated required refs and privacy] --> Filter
  Filter --> UI[Enabled card or safe disabled reason]
  UI -->|explicit intent visibility grants no permission| S[Owning service]
  S --> Checks[Fresh target policy permissions confirmation and implementation checks]
  Checks -->|valid| Dispatch[Approved dispatch]
  Checks -->|invalid| Block[Classified blocked unavailable state]
~~~

### 8. Invocation-time binding -> late-result correlation

~~~mermaid
sequenceDiagram
  actor U as Technician
  participant C as S1 selected context
  participant D as DynamicHub
  participant S as Owning service
  participant P as Provider gateway
  participant T as Ticket recording owner
  U->>D: Invoke for target A with explicit Ticket A choice
  D->>S: Proposed refs and selection revision
  S->>S: Validate and freeze operation O binding A
  S->>P: Dispatch approved operation O for A
  U->>C: Guarded selection change to B
  C-->>D: New current projection revision for future actions
  P-->>S: Authoritative O result for A
  S-->>D: O original binding and late result
  D->>D: Earlier context card A no focus or selection change
  S->>T: Optional recording of O to captured Ticket A
  T-->>D: Recording outcome separate from provider outcome
  U->>T: Explicit recording only retry if safe after reconciliation
~~~

Diagram 6's return edge means an explicit recording recovery request after owner reconciliation, not an automatic retry loop. Inquiry/retry remains bounded by the failure contract. None of the diagrams creates direct GUI/provider/SQLite execution, copies selected records or uses current context as completion authority.

## Decision Register

DECIDE NOW means resolved enough for review/downstream architecture; DESIGN NEXT means bounded implementation/native detail; DEFER means not enabled by this plan. Every status is an author recommendation, never recorded USER approval.

| Decision | Options | Recommendation | Evidence | Rationale | Consequences | Planning Depth | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S2-D01 Mochi role | Domain executor / optional presentation | Optional personalized cues/explanation presentation | O-C; S2 8/29 | Preserve primary app/services | Renderer failure cannot block work | DECIDE NOW | RECOMMENDED |
| S2-D02 DynamicHub role | Full domain module / workflow surface | Application troubleshooting coordinator and single auxiliary presenter | F-A; retained S1 | 0A-D1 authority | No competing persistence/run/Ticket owner | DECIDE NOW | RECOMMENDED |
| S2-D03 AI role | Mandatory inference / deterministic plus advisory | Deterministic default, optional reviewed AI explanation/ranking | F-B; Role Model | Offline and no AI authority | Validate known candidates, explicit outbound gate | DECIDE NOW | RECOMMENDED |
| S2-D04 Catalog ownership | New diagnostic DB / static application metadata | Pure static owner contributions referencing existing operations | S/P; Action Catalog | Cross-owner discovery without duplicate registry | Compiled allowlisted dispatch; no plugins | DECIDE NOW | RECOMMENDED |
| S2-D05 Projection ownership | Widget records / application adapter | S1 selected refs plus source-approved minimal projection | F-A/B-A; Context Matrix | No parallel context/identity | Source eligibility and consumer generation | DECIDE NOW | RECOMMENDED |
| S2-D06 Invocation binding | Current-at-completion / service frozen intent | Immutable accepted operation refs/scope/Ticket/version | Original 11; retained reconciliation | Wrong target/Ticket prevention | Later selection only future actions | DECIDE NOW | RECOMMENDED |
| S2-D07 Ranking | Arbitrary LLM buttons / filtered known set | Eligibility filter then deterministic priority; optional validated reorder | Suggestion Ranking | Safety before relevance | 3-5 cards, stable keys, AI fallback | DECIDE NOW | RECOMMENDED |
| S2-D08 Default automation | Autonomous / suggestions and explicit reads | SUGGEST_ONLY + deliberate available ONE_CLICK_SAFE_READ_ONLY | Automation Levels; P | Explicit intent preserved | Remote actions unavailable until delivered | DECIDE NOW | RECOMMENDED |
| S2-D09 Safe read definition | Name-based / reviewed effect classification | No intended target mutation, bounded purpose/disclosure risks | Safety Matrix | Reads still privacy/security relevant | No automatic eligibility | DECIDE NOW | RECOMMENDED |
| S2-D10 Confirmation classes | Generic Continue / bound effect workflow | Cancel-default exact target/action/version/scope; mutations separately reviewed | F-B; Action Safety Classes | No stale confirmation | No initial autonomous mutation | DECIDE NOW | RECOMMENDED |
| S2-D11 Capability model | Flag=permission / owner observations | Composed support plus fresh scope/permission/health | P; Provider Matrix | Configured does not mean supported | Dispatch rechecks; no hover remote discovery | DECIDE NOW | RECOMMENDED |
| S2-D12 RMM routing | Widget API / owning service gateway | Qualified device/customer mapping, reviewed provider adapter | F-A/B; RMM Architecture | Provider execution is not domain authority | Vendor/auth/terms must be verified before delivery | DECIDE NOW | RECOMMENDED |
| S2-D13 PowerShell via RMM | Generated script / predefined reviewed operation | Approved versioned implementation with typed inputs | P; PowerShell boundary | No arbitrary AI/customer endpoint code | Remote safety distinct from local Job Object | DECIDE NOW | RECOMMENDED |
| S2-D14 M365 routing | Endpoint RMM / fact-specific Microsoft adapter | Graph or Exchange supported read by actual auth/capability | Q; Microsoft 365 Architecture | Correct provider/fact/least privilege | No assumed app-only licenseDetails | DECIDE NOW | RECOMMENDED |
| S2-D15 Adobe | Installed software inference / authoritative API | Keep entitlement unavailable until provider proven | Adobe Capability Assessment | Avoid invented entitlement | No enabled card/result without inspection | DEFER | NOT_VERIFIED |
| S2-D16 Ticket recording default | Auto Quick Note / explicit observation | Explicit owner-recorded generated observation, default auto off | T/DB/F-C; Recording Matrix | Human versus system semantics | Recording API/duplicate safety prerequisite | DECIDE NOW | RECOMMENDED |
| S2-D17 Ticketless fallback | Require/create Ticket / owner result | Source-owned session result now; optional future local Journal | F-A D2; Case Journal | Ticket optional, no false durability | Physical Journal storage/drafts separate owner design | DECIDE NOW | RECOMMENDED |
| S2-D18 Acknowledgement | Mandatory text IPC / optional output | Safe app equivalent first; tiny pet output through later reviewed adapter | O-C; retained S1 | Current cosmetic wire cannot carry text | No sensitive channel upgrade assumed | DECIDE NOW; adapter DESIGN NEXT | RECOMMENDED |
| S2-D19 Trigger policy | Auto replace / cue then guarded open | Explicit open; default automatic indicator; safe-vacant future preference only | Trigger Matrix; retained S1 | Avoid focus/draft theft | No provider/AI work on appearance | DECIDE NOW | RECOMMENDED |
| S2-D20 Cooldowns | Timer nagging / generation suppression | Bounded dedup/cooldown, explicit dismiss respected | Trigger / Cooldown Model | No repeat unchanged event | Finite initial timings tuned natively | DECIDE NOW; timing DESIGN NEXT | RECOMMENDED |
| S2-D21 Uncertain outcome | Timeout=failed / reconcile original operation | Preserve UNCERTAIN; explicit bounded status/recording reconciliation | F-B; Failure Matrix | Acceptance is not completion | No blind replay; late result remains correlated | DECIDE NOW | RECOMMENDED |
| S2-D22 AI unavailable | Disable tool / deterministic fallback | Preserve local rules/results/drafts | B-A; Offline / Failure Matrix | Optional AI | No automatic retry/Send | DECIDE NOW | RECOMMENDED |
| S2-D23 Offline | Provider-required app / classify use cases | Local-required work independent; remote operation unavailable individually | F-A/B; Offline Behavior | Avoid integration prerequisites | No stale execution outbox | DECIDE NOW | RECOMMENDED |
| S2-D24 Cross-tenant | Guess ID / authoritative qualified mapping | Explicit validated provider/tenant/customer/object refs | Context Matrix; SEC-11/12 | No label/prose authority | Reject ambiguity, no fallback tenant/device | DECIDE NOW | RECOMMENDED |
| S2-D25 Auto-safe experiment | Ship now / separately scoped opt-in | Default off; separate read-only experiment contract | Automation Levels | Current task cannot grant autonomy | No mutant inheritance or security-toggle bypass | DEFER | DEFERRED |
| S2-D26 Durable observations/Journal/Evidence | New tables now / later owner reuse | Inspect/reuse/extend under separate domain/persistence plan | DB; F-A/C | Existing timeline not universal ledger | No migration or false implemented association | DEFER | DEFERRED |

## Requires User Decision

NONE at S2 architecture-planning depth. The conservative defaults, fixed upstream ownership and explicit unavailability/deferred delivery resolve the requested design without choosing a provider, authentication mechanism, persistent schema or IPC redesign. Those implementation activation gates are not manufactured USER choices to finish this architecture report. Visual timings/pixel constants are native implementation detail.

A future requirement that changes S1 hosting/region/context ownership, Foundation meaning, authentication/security or a domain relationship must stop at that owner and return REQUIRES_DYNAMIC_CONTEXT_DECISIONS for a material S2 architectural choice. This author-side candidate still requires independent review and explicit USER approval; NONE is not approval.

## Assumptions

| Assumption | Basis / safe failure |
| --- | --- |
| Deterministic local rules are useful before AI/provider delivery | INFERENCE from existing local tools; no usage/quality measurement. If no eligible action, show safe empty state/Open Full Tool |
| A small catalog and session coordinator can reuse existing composition/runner | Source fit, not runtime proof. Keep current conservative single-operation guards until adapters tested |
| Safe result summaries can be provided without copying raw records | Owner contract requirement, privacy policy not verified. Missing approved projection disables sharing |
| Source-owned in-memory result is adequate for first action presentation | Current diagnostics behave this way; explicit no-durable-recovery label. Durable work requires owner persistence plan |
| Optional future provider can satisfy bounded read/status contracts | NOT VERIFIED. Unsupported auth/mapping/output/status keeps action disabled; no unsafe local substitute |
| Exact cue/card constants can be tuned without altering authority | S1 native constraints retained; collapse sooner and preserve accessible controls if fit fails |

## Not Verified

Provider vendor/API/account/credentials/permissions/license/retention/employer policy; actual Graph/Exchange sessions; Adobe entitlement source; local native runtime/renderer/operational database health; DynamicHub/catalog/context/auxiliary/shared-draft implementation; future observation/association/idempotent recording/Journal/Settings service availability; sensitive presentation transport and authenticated peer mechanism; external DynamicHub prototype; memory/performance/ranking usability; physical input, Narrator/high contrast/large font, DPI/multi-monitor/focus/overlay geometry; crash recovery or durable results; Mermaid rendering.

Public Microsoft docs were checked for candidate read boundaries, not actual access. Existing source/tests and historical documents are not fresh runtime evidence. Deferred providers/transport/persistence are unavailable until separately reviewed; no material unresolved upstream architecture conflict was found.

## Risk Register

Likelihood is UNKNOWN throughout because no provider/native workflow measurements were made. Status OPEN means architecture mitigation specified with implementation/runtime residuals; no risk is claimed eliminated.

| Risk | Likelihood | Impact | Mitigation | Residual Risk | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| AI hallucinated action | UNKNOWN | HIGH | Closed catalog/output validation; deterministic fallback | Explanation may still mislead; source labels/review | AI/application use case | OPEN |
| Arbitrary script execution | UNKNOWN | CRITICAL | Typed key-only dispatch and versioned approved implementation | Future adapter can regress; negative contract tests | Execution/security owner | OPEN |
| Wrong target | UNKNOWN | CRITICAL | Qualified refs and owner mapping/dispatch revalidation | Mapping can stale; no ambiguous fallback | Source/integration owner | OPEN |
| Wrong Ticket | UNKNOWN | HIGH | Exact captured optional Ticket and separate recording | Original Ticket can become invalid | Ticket association owner | OPEN |
| Wrong tenant | UNKNOWN | CRITICAL | Tenant/customer/provider-qualified identity, permission scope | Misconfiguration/remote mapping drift | Integration/security | OPEN |
| Stale context | UNKNOWN | HIGH | Generation/freshness/source tokens, immutable binding | Notification lag; service must recheck | Application/source owners | OPEN |
| Provider over-privilege | UNKNOWN | CRITICAL | Fact-specific least privilege and reviewed auth | Actual provider grants not verified | Integration/security | OPEN |
| Credential leakage | UNKNOWN | CRITICAL | Private auth refs, no context/log/ordinary Settings secret | Provider/runtime memory and unsafe exceptions | Integration/security | OPEN |
| Privacy leakage | UNKNOWN | HIGH | Mandatory source gate, minimal projections, preview/Send | Detector false negatives and unknown employer policy | Source/privacy owner | OPEN |
| Duplicate remote execution | UNKNOWN | CRITICAL | Operation identity, single-submit guard, reconcile unknown dispatch | Provider idempotency/status may not exist | Execution/integration | OPEN |
| Uncertain mutation | UNKNOWN | CRITICAL | Mutations disabled baseline; dedicated reconcile/recovery | Later provider cannot prove cancellation | Mutation/security owner | OPEN |
| Ticket spam | UNKNOWN | MEDIUM | Recording explicit/off default; bounded one result summary | Poor future policy could over-record | Ticket/workflow owner | OPEN |
| Incorrect Ticket association | UNKNOWN | HIGH | Source revision/privacy/target relationship validation | Retention/cardinality needs later owner contract | Ticket/source association | OPEN |
| Provider rate limit | UNKNOWN | MEDIUM | No hover poll; finite rate/deadline/status budget | Vendor delay/burst requirements unknown | Integration | OPEN |
| Slow provider response | UNKNOWN | MEDIUM | Async owner dispatch, explicit status/full-tool path | Long remote lifecycle despite UI timeout | Application/integration | OPEN |
| DynamicHub nagging | UNKNOWN | MEDIUM | Generation dedup, finite cooldown, dismissal, cues | Real workflow relevance not measured | DynamicHub presentation | OPEN |
| Mochi focus theft | UNKNOWN | HIGH | Optional nonactivating output, S1 focus/modal guard | Desktop/native behavior untested | Shell/Mochi presentation | OPEN |
| Too many suggested actions | UNKNOWN | MEDIUM | 3-5 set; bounded More/full-tool | Ranking may hide useful action | Workflow/UX | OPEN |
| Unsafe future autonomy | UNKNOWN | CRITICAL | Off/deferred, separate explicit allowlisted experiment | Policy expansion needs independent review | Automation/security | OPEN |
| Provider-specific coupling | UNKNOWN | HIGH | Typed owner DTOs and gateway adapters, neutral keys | Actual SDK/errors/version constraints | Integration/application | OPEN |
| Adobe license misinterpretation | UNKNOWN | HIGH | Entitlement disabled; inventory distinction | Manual unsupported claim still possible | Licensing owner | OPEN |
| AI/provider offline dependency | UNKNOWN | HIGH | Local rules/results/drafts survive; per-action unavailable | Future feature composition could add dependency | Application/source owners | OPEN |
| Completion-time retargeting | UNKNOWN | CRITICAL | Frozen operation/Ticket refs; late view correlation | Future callback can misuse current selection | Application/recording owners | OPEN |
| Testing loops | UNKNOWN | MEDIUM | Finite checks; no repeated unchanged check >2; native deadlines/owned cleanup | New harnesses need explicit budgets | Validation owner | OPEN |
| Dirty auxiliary displacement | UNKNOWN | HIGH | S1 one-slot owner retention/refusal; Cancel default | Required draft adapters not delivered | Shell/Ticket/inspector owners | OPEN |
| False persistence / audit claim | UNKNOWN | HIGH | Memory-only labels; no generic ledger; capability gates | Future recording store/retry semantics unknown | Result/Ticket/Journal owners | OPEN |


## Recommended Vertical Slices

Planning identifiers below are decomposition only; actual repository slice numbering is assigned through governance when authorized. Every slice needs its own explicit objective/manifest/exclusions, required validation, independent review and integration authority. No slice is executed here.

| Proposed slice | Bounded objective | Validation / dependency / exclusion |
| --- | --- | --- |
| CTX-01 | One read-only local Ticket-context projection using S1 holder and one source | Pure optional/missing/stale/privacy/ref tests; no AI/provider/IPC/persistence; depends delivered S1 seam |
| ACT-01 | Pure catalog metadata for one existing local snapshot, compiled owner adapter | Unknown/duplicate key/version/type/availability negative tests; no generic execution/registry replacement |
| ACT-02 | DynamicHub static local cards in S1 shared region | Native dirty Quick Ticket/inspector/modal/Close/focus/responsive tests; no provider or action run |
| ACT-03 | One explicit existing local diagnostic end-to-end | Reuse current sealed boundary; failure/cleanup/duplicate-submit/late-result tests; no parameters or remote target |
| ACT-04 | Original-operation result card and safe app acknowledgement | Execution/collection/recording axes, context A -> B, hidden panel/callback/expiry tests; no pet protocol change |
| ACT-05A | Ticket owner observation/association reuse assessment and one exact approved recording API | Source semantics, transaction/duplicate/unknown-commit/failure tests; separately approve physical schema if needed; no provider rerun |
| ACT-05B | One explicit result-to-captured-Ticket UI flow through that API | No-Ticket/A->B/wrong/deleted Ticket/recording-only retry/human-draft tests; no PSA auto-publication |
| DH-01 | Deterministic ranking/trigger dedup over eligible local source | Empty/disabled/partial/stale/dismissed/cooldown bounds; no AI/remote discovery |
| DH-02 | One definition-owned local structured-result follow-up | Key/type/prerequisite/provenance/duplicate tests; no auto chain |
| MOCHI-ACK | Optional minimized acknowledgement presentation adapter | Separate transport/security review first; compatibility/privacy/native focus/DPI/suppression tests; keep cosmetic v1 |
| RMM-01 | Provider-specific read-only capability/mapping adapter after verified vendor/auth scope | Synthetic DTO/auth/permission/tenant/rate/malformed tests; no endpoint scripts/credential values in fixtures |
| RMM-02 | One reviewed remote read operation through that adapter | Script/native-operation identity/output/deadline/status/uncertain tests; no Graph/Ticket writing/AI |
| M365-01 | One supported read on a validated tenant-qualified user after auth review | Operation-specific permissions/auth, property/page bounds/partial/rate/cross-tenant tests; no RMM/Exchange bundle |
| M365-02 | One separate mailbox fact if justified after Exchange boundary review | RBAC/identity/bounded property/deadline/error tests; no free-form cmdlet endpoint |
| JOURNAL-LATER | Feature-owned ticketless local storage/draft design and one bounded use case | Reuse/schema/retention/optional association/offline tests; no competing timeline or remote prerequisites |
| AI-01 | Optional reviewed explanation for one eligible local projection | Prompt/output/adversarial invented-ID/key/privacy/offline tests; external preview/Send if used; no execution |
| AUTO-LATER | Separately authorized opt-in read-only experiment only if justified | Explicit action/context/rate/timeout/audit/stop/reconcile tests; not initial delivery; no mutation |

Native-dependent changes require separate WINDOWS_NATIVE evidence before integration. Headless/cloud checks cannot satisfy focus/desktop/DPI acceptance. Provider contract tests with synthetic fixtures do not prove real employer authorization. Shared Settings implementation is a separate dependency for actual preference consumers; static defaults avoid bundling it into each slice.

## Downstream Clipboard 1C Inputs

After full S2 independent review -> explicit USER approval -> controlled integration, Clipboard 1C may consume these inputs along with closed S1/1A/1B. READY_FOR_DYNAMIC_CONTEXT_REVIEW is not that closure and does not execute 1C.

| 1C concern | Authoritative input / permitted consumption |
| --- | --- |
| MainWindow / Technician Workspace placement | S1 primary MainWindow, one retained Clipboard singleton in stack, guarded typed GUI-thread routes; module list/detail belongs to 1C |
| DynamicHub auxiliary-region behavior | Same single coordinated inspector/Quick Ticket/DynamicHub slot; one occupant, owner retained hide/refusal, no second permanent sidebar |
| Safe Active Technician Context projection | S1 refs/revision plus source-approved purpose projection; 1C supplies eligible selected Clipboard ref, no copied records or universal context store |
| Clipboard Item privacy/sensitivity | 1A mandatory complete gate before derivation/disclosure, secret blocked/no raw override, sensitive review, expiry and reassessed derivative; 1B authenticated bounded ingress remains unchanged |
| Active Ticket context | Optional globally reachable saved target via S1; absence valid for Clipboard/Journal/local work; Clipboard content cannot pick Ticket |
| Invocation-time Ticket binding | Explicit source+exact Ticket choice captured by owning service at invocation, including none; no current-at-completion lookup |
| Late-result semantics | Original operation/result/ref preserved; current view generation may change, earlier-context indicator/explicit navigation, no focus/selection overwrite |
| Ticket association | Separate owner API, source eligibility/provenance/Evidence hold semantics and original target validated; no duplicate editor or generated human Quick Note |
| Action Catalog routing | Typed allowlisted key and schema through owning service; UI availability not permission; 1B diagnostic.open_request stays a planning/confirmation route |
| No arbitrary copied-command execution | Copied PowerShell/text/URL/Entity/AI output is data, never dispatch string/path or new local target parameter; unknown operations unavailable |
| Mochi acknowledgement | Optional tiny truthful output/app equivalent; cosmetic v1 unchanged; source result versus recording status separate |
| AI exposure rules | Sharing off by default; eligible selected minimized projection only; raw Inspector read or Save is not outbound consent; external exact preview/Send and verified policy |
| Offline behavior | Clipboard/Knowledge/Ticket local-required paths stay useful; optional AI absence falls back locally; owner prerequisites/capabilities explicit |
| Provider-unavailable behavior | Disable affected online action, preserve Item/draft/local result and safe full-tool route; no stale delayed execution queue |
| Keyboard/accessibility shell rules | S1 modal/editor/scoped Escape/focus-return/contrast/DPI bands; 1B Win+Alt+C retained; all cues/actions reachable without hover/animation |

1C still owns Center columns/filters/search/history/Inspector, raw-read eligibility, Save/Pin/Evidence presentation, source expiry, session drafts and its native tests. It cannot relax 1A retention/secret invariants, repurpose 1B cosmetic/guide/ingress boundaries, infer provider IDs, create a rival sidebar or silently change S1/S2 semantics. Missing owner capability stays unavailable; a genuine owning-contract conflict stops that local decision and goes to its owner.

## Testing Implications

Future pure/contract tests cover catalog admission, typed inputs, mapping/scope, binding immutability, optional context, closed outputs, axes/null/empty/completeness and malicious AI/provider proposals. Service integration tests prove permission/confirmation revalidation, provider uncertainty, original-Ticket-only record/retry, duplicate-safe unknown commit, no direct SQL/process shortcuts and local offline independence. Database tests apply only when a separately reviewed persistence slice actually changes records/schema, including integrity_check=ok and zero foreign_key_check violations on isolated fixtures.

GUI tests cover draft/pending gaps, stale callbacks, one occupant, earlier-context results, confirmation Cancel and safe full-tool navigation. Native tests separately cover keyboard/Narrator/high contrast/large fonts/minimum size, DPI/monitor changes, focus/geometry and pet acknowledgement suppression, with finite total deadline/input count and owned-process cleanup. No physical/native claim follows from offscreen tests. Repeat unchanged checks no more than twice; a third attempt needs changed input/hypothesis/new evidence, otherwise STOP and classify.

## Documentation Impact

Only S2 is modified. Foundation/S1/Clipboard contracts, ROOT, numbered canonical docs, CURRENT_STATE and ChangeLog remain unchanged. This architecture report is not implemented functionality. After separately approved/validated delivery, assess Docs05/04 for surfaces/workflow; Docs06/13 for composition/services; Docs12 only for actually approved execution changes; Docs07/08/09 for real persistence; source privacy/Settings/Mochi owners for their actual changes. Synchronize implemented status/history only with evidence, never to legitimize a speculative provider.

## Acceptance Criteria

Each original S2 criterion is evaluated separately against the completed report and inspected source/scope evidence. PASS is author-side architecture-depth assessment, not independent architecture review or test execution. The exact original wording is preserved in the table; no substituted criteria or invented runtime results.

| ID | Original criterion | Result | Evidence / section |
| --- | --- | --- | --- |
| AC-01 | Mochi role explicit. | PASS | Role Model; O-C |
| AC-02 | Local IT AI role explicit. | PASS | Role Model; Suggestion Ranking |
| AC-03 | DynamicHub role explicit. | PASS | Role Model; DynamicHub Surface |
| AC-04 | DynamicHub is not execution authority. | PASS | Foundation Compatibility; SEC-02/03 |
| AC-05 | Foundation 0A-D1 ownership preserved. | PASS | Foundation Compatibility; F-A approved D1 |
| AC-06 | S1 shell consumed. | PASS | Retained S1 reconciliation, 25/25; S1 Shell Compatibility |
| AC-07 | Active Technician Context consumed, not duplicated. | PASS | Context Architecture/Matrix; S2-D05 |
| AC-08 | Context freshness defined. | PASS | Context Freshness; Context Matrix |
| AC-09 | Target validation defined. | PASS | Invocation-Time Operation Binding; SEC-06/11/12 |
| AC-10 | Action Catalog defined. | PASS | Action Catalog; Capability Matrix; S2-D04 |
| AC-11 | Arbitrary AI PowerShell prohibited. | PASS | PowerShell-via-RMM Boundary; SEC-01 |
| AC-12 | Safety classes defined. | PASS | Action Safety Classes; Safety Matrix |
| AC-13 | Default automation level defined. | PASS | Automation Levels; S2-D08 |
| AC-14 | Future auto-safe path bounded. | PASS | Automation Levels; S2-D25; off/deferred |
| AC-15 | Provider capability model defined. | PASS | Provider Capability Model; Provider Matrix |
| AC-16 | RMM gateway role defined. | PASS | RMM Architecture; S2-D12 |
| AC-17 | Approved PowerShell-via-RMM path defined. | PASS | PowerShell-via-RMM Boundary; diagram 3 |
| AC-18 | M365 provider boundary defined. | PASS | Microsoft 365 Architecture; Q; diagram 4 |
| AC-19 | Adobe remains NOT VERIFIED unless proven. | PASS | Adobe Capability Assessment; SEC-13 |
| AC-20 | Provider-neutral action keys defined. | PASS | Action Catalog; Capability Matrix neutral keys |
| AC-21 | Action request contract defined. | PASS | Action Request / Result Contracts; F-B |
| AC-22 | Action result contract defined. | PASS | Action Request / Result Contracts; diagram 8 |
| AC-23 | Structured normalization defined. | PASS | Result Normalization; P/source validators |
| AC-24 | Ticket recording semantics defined. | PASS | Ticket Recording; Recording Matrix; T/DB |
| AC-25 | Note vs observation vs evidence distinguished. | PASS | Ticket Recording; retained Ticket reconciliation; F-C |
| AC-26 | Ticketless behavior defined. | PASS | Case Journal / Ticketless Behavior; F-A D2 |
| AC-27 | Mochi acknowledgement defined. | PASS | Mochi Acknowledgement; separate app equivalent |
| AC-28 | DynamicHub trigger policy defined. | PASS | Trigger / Cooldown Model; Trigger Matrix |
| AC-29 | Cooldown/dismissal behavior defined. | PASS | Trigger Matrix; explicit generation suppression |
| AC-30 | Suggestions bounded to approved actions. | PASS | Suggestion Ranking; SEC-01/05/12 |
| AC-31 | Follow-ups use approved action keys. | PASS | Follow-Up Actions; definition-owned key-only proposals |
| AC-32 | Mutating confirmation defined. | PASS | Action Safety Classes; Safety Matrix; S2-D10 |
| AC-33 | Secrets boundary explicit. | PASS | Security; Privacy; SEC-04/09 |
| AC-34 | Privacy projection explicit. | PASS | Privacy; Context Matrix; B-A/B-B |
| AC-35 | Logging restrictions explicit. | PASS | Privacy; Failure Matrix; A-L logging |
| AC-36 | Offline behavior defined. | PASS | Offline Behavior; Provider Matrix; S2-D23 |
| AC-37 | Provider failure behavior defined. | PASS | Provider Failures; Failure Matrix, 15 cases |
| AC-38 | Idempotency/reconciliation defined. | PASS | Idempotency / Reconciliation; F-B |
| AC-39 | Uncertain outcomes cannot fake success. | PASS | Failure Matrix; diagrams 5/6; UNCERTAIN separate |
| AC-40 | Provenance defined. | PASS | Result Normalization; immutable request/result source provenance |
| AC-41 | Least privilege required. | PASS | Security; Provider Matrix; operation-specific review |
| AC-42 | Cross-tenant safety defined. | PASS | RMM/Microsoft architectures; SEC-11 |
| AC-43 | Provider ID resolution validated. | PASS | Context Matrix; SEC-12; exact scoped mappings |
| AC-44 | Ticket write retry does not rerun remote action. | PASS | Ticket Association; Failure Matrix; diagram 6 |
| AC-45 | Mochi optional. | PASS | Mochi Acknowledgement; S2-D01/18 |
| AC-46 | DynamicHub UI optional to action services. | PASS | Role Model; Failure Matrix; owner services independent |
| AC-47 | Settings inputs classified. | PASS | Settings Inputs; F-D; no runtime/secret overrides |
| AC-48 | Required matrices complete. | PASS | Seven matrices; retained compatibility matrix; exact row/column checks |
| AC-49 | Security review passes. | PASS | Security Final Check; 13/13 architecture PASS |
| AC-50 | Risk register complete. | PASS | Risk Register; 26 risks with all seven fields |
| AC-51 | Future slices small. | PASS | Recommended Vertical Slices; separate local/provider/Ticket/AI scopes |
| AC-52 | No production implementation occurred. | PASS | Allowed-path Git diff/index checks; production untouched |
| AC-53 | No credentials/secrets added. | PASS | Security/Privacy; no credential access/setup or candidate secret material |
| AC-54 | No database migration occurred. | PASS | No schema/data/runtime invocation; only S2 modified |
| AC-55 | No provider falsely claimed available. | PASS | Verified Current State; Provider/Capability matrices; actual access NOT_VERIFIED |

Architecture acceptance: 55/55 PASS. S1/S2 compatibility: retained 25/25 PASS. No material unresolved architectural decision or authority conflict. Independent S2 review has not run.

## Validation

Environment: WINDOWS_NATIVE workstation. FRESH documentation/static checks and read-only source/GitHub/official-doc inspection are distinguished from RETAINED reconciliation findings and NOT RUN runtime suites. No executed runtime result is reused as S2 PASS.

| Required architecture validation | Result | Evidence / provenance |
| --- | --- | --- |
| Current Mochi inspection | PASS | FRESH complete O-C sources and current/MVP distinction; no AI/text capability fabricated |
| Foundation compatibility | PASS | FRESH approved D1/D2/envelope/vocabulary/settings input inspection, merged records/ancestry; no parallel authority |
| S1 shell compatibility | PASS | RETAINED 25/25 reconciliation, exact block preservation; current S2 creates no conflict |
| Context architecture | PASS | Optional source refs/projection/freshness/immutable binding and late correlation |
| Action Catalog | PASS | Static owner contributions/compiled dispatch/version/input limits; no duplicate registry |
| Safety classes | PASS | Read disclosure risks, explicit confirmation, mutations separately gated |
| RMM boundary | PASS | Owner service/gateway and mapping/status review; provider not claimed available |
| PowerShell safety | PASS | Existing fixed local policy/sealed boundary retained; future remote approved versioned operation only |
| M365 boundary | PASS | Official operation docs checked; actual auth/scope/tenant remains NOT_VERIFIED |
| Adobe boundary | PASS | Entitlement disabled/NOT_VERIFIED; inventory distinct |
| Ticket recording | PASS | Distinct human/generated/Evidence semantics; original-choice write/retry; API unavailable until delivered |
| DynamicHub UX | PASS | Single S1 slot/cues/guards/three bands, small cards, full-tool fallback |
| Mochi acknowledgement | PASS | Optional truthful tiny output/app equivalent; no cosmetic v1 expansion |
| Provider failure/reconciliation | PASS | 15-case matrix, original-operation uncertainty/status/recording-only retry |
| Privacy/security | PASS | 13-invariant final check; complete source gates and explicit outbound review |
| Offline behavior | PASS | Local-required independence, optional AI fallback, per-action remote unavailable |
| Settings boundary | PASS | 0D definitions only, runtime/capability/secret/security distinctions |
| Testing strategy | PASS | Future meaningful pure/contract/owner/native cases; bounded retry/harness stop rules |
| Scope control | PASS | One allowlisted tracked file; only permitted protected untracked pathname; empty index |
| Required headings/matrices/registers/diagrams | PASS | FRESH static structure/column/ID/fence checks; 7 matrices, 8 diagram sources, 26 decisions/26 risks |
| Acceptance criteria | PASS | Exact 55 original wordings, individually assessed and traced |
| Original integrated contract prefix | PASS | FRESH raw prefix SHA256 plus Git-normalized equality; NOT_STARTED and integrated invocation binding retained |
| Previous reconciliation | PASS | FRESH byte identity comparison of retained block; no re-execution/redesign |
| Relative local links / anchors | PASS | FRESH appended-report destination/anchor checks; no protected target |
| git diff --check | PASS | FRESH final whitespace check |
| git status --short / diff --name-status / cached paths | PASS | FRESH only S2 modified; no staged path; branch/HEAD checked |
| Production implementation | NONE | No production source, runtime, dependencies or endpoints changed |
| Database / credentials | NONE | No migration/operational data/credential configuration/read/write |
| Independent S2 architecture review | NOT RUN | Mandatory NEXT gate, not supplied by author acceptance checks |

| Runtime / rendering area | Result |
| --- | --- |
| Application runtime | NOT RUN |
| Database tests | NOT RUN |
| GUI tests | NOT RUN |
| Integration tests | NOT RUN |
| AHK tests | NOT RUN |
| PowerShell runtime tests | NOT RUN |
| Mochi runtime tests | NOT RUN |
| Provider/API tests | NOT RUN |
| Native Windows GUI tests | NOT RUN |
| Mermaid rendering | NOT RUN |

Static source/diagram boundary inspection is not compiled diagram or deployed enforcement evidence. No rendering tooling/dependency was installed. Two unchanged repetitions do not justify another; this continuation used new scope/evidence and performed final checks against changed candidate bytes. No unbounded native/provider loop or persistent service was started.

ORIGINAL CONTRACT PREFIX = PASS.

## Result

READY_FOR_DYNAMIC_CONTEXT_REVIEW

S2 execution is complete at architecture-planning depth: retained S1 reconciliation PASS, all required architecture sections/matrices/eight diagram sources/registers/handoff complete, 55/55 original criteria PASS, Requires User Decision NONE, no unresolved material architecture conflict. Candidate unapproved, unstaged, uncommitted and unpushed; exactly one tracked file modified. Runtime and Mermaid rendering NOT RUN.

Next gate: INDEPENDENT S2 ARCHITECTURE REVIEW. STOP. No staging, commit, push, PR, merge, Clipboard 1C execution, production Action Catalog, DynamicHub/Mochi change, provider connection, PowerShell writing, credentials or autonomous action is authorized.
