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

Target mismatch blocks execution.

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

Retrying Ticket write must not rerun the remote action.

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
