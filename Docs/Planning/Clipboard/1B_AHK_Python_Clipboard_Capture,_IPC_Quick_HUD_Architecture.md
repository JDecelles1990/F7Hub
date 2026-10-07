# F7Hub Phase 1B
# AHK ↔ Python Clipboard Capture, IPC & Quick HUD Architecture Planning Instructions
Existing AHK/hotkey/AltF7Hub integration inventory; manual capture semantics; Clipboard snapshot behavior; source process/window metadata; privacy policy; hotkey ownership and conflicts; AHK/Python responsibility matrix; actual IPC transport recommendation; authentication; endpoint discovery; timeout/retry policy; transport idempotency vs content deduplication; F7Hub-running/not-running behavior; Quick HUD states; HUD action routing; native Windows validation; explicit loop/retry guard.

## Retry and Loop Safety Contract

Every retrying operation must define:

- triggering failure
- maximum retry count
- maximum elapsed duration
- state change required before another validation attempt
- failure result after exhaustion

The agent must not repeat the same native or integration test
more than twice when:

1. the failure is identical, and
2. no relevant code/configuration/state changed.

In that case:

STOP
DIAGNOSE
REPORT BLOCKED

Do not continue automated retries.


## Mode

`@ARCHITECT @PLAN`

Architecture and integration planning only.

Do not implement production code.

Do not register hotkeys.

Do not create an IPC server.

Do not modify AHK scripts.

Do not create Python services.

Do not create SQLite migrations.

Do not modify Clipboard persistence.

Do not create the full Clipboard Center GUI.

Do not implement PowerShell diagnostics.

Do not implement Mochi.

---

# 1. Objective

Design the Windows integration boundary for F7Hub Clipboard capture.

This phase must define:

- how AutoHotkey v2 initiates Clipboard capture
- how Windows Clipboard content is obtained safely
- how source application/window context is collected
- how AHK packages a Phase 0B contract
- how AHK communicates with Python
- how Python validates and accepts the request
- how duplicate transport requests are handled
- how unavailable services and timeouts behave
- how privacy protection begins at the capture boundary
- how the Quick HUD displays results
- how HUD actions are routed back through F7Hub
- how hotkeys are configured safely
- how the AHK layer remains lightweight
- how manual capture differs from future automatic monitoring

The result must allow implementation slices to build the AHK ↔ Python integration without redefining the Clipboard domain from Phase 1A.

---

# 2. Required Foundation Inputs

Before planning:

```text
Phase 0A
Master Foundation Architecture

Phase 0B
Global JSON / Interoperability Contract

Phase 0C
Classification / Taxonomy / Entities / Tags

Phase 0D
Settings / Configuration Architecture

Phase 1A
Clipboard Domain & Data Lifecycle
```

Treat approved decisions from those phases as constraints.

Do not silently redesign:

```text
Clipboard Item
Capture Event
Entity
Tag
Retention
Sensitivity
JSON envelope
Settings ownership
```

inside Phase 1B.

---

# 3. Mandatory Current-State Inspection

Inspect relevant existing F7Hub and AltF7Hub implementation for:

```text
AHK application architecture
existing global hotkeys
hotkey registry/configuration
clipboard hooks
OnClipboardChange usage
AHK GUIs / HUDs
AltF7Hub launcher patterns
Python process startup
F7Hub bootstrap
existing localhost IPC
existing named-pipe code
JSON serialization
HTTP client usage
process communication
logging
single-instance enforcement
Windows focus/window inspection
tests
```

Also inspect documentation covering:

```text
AHK Architecture
Python Architecture
System Architecture
GUI
Security
Folder Structure
```

Do not assume no reusable integration infrastructure exists.

Use:

```text
FACT
ASSUMPTION
INFERENCE
RECOMMENDATION
NOT VERIFIED
```

---

# 4. Core Responsibility Boundary

Use the foundation principle:

```text
AHK senses and interacts.

Python understands and orchestrates.

SQLite remembers.

PowerShell performs approved technical work.

Mochi communicates.
```

For Phase 1B specifically:

```text
Windows
   ↓
AHK
   ↓
Interoperability Boundary
   ↓
Python
   ↓
Clipboard Domain
```

---

# 5. AHK Responsibilities

AHK may own:

```text
global hotkey registration
manual capture trigger
Windows Clipboard access
foreground process discovery
window title discovery
lightweight source metadata
sending a structured request
receiving a structured result
Quick HUD presentation
user selection of HUD action
opening F7Hub Clipboard Center
```

---

# 6. AHK Must Not Own

AHK must not own:

```text
SQLite access
Clipboard Item persistence
deduplication truth
entity extraction rules
tag taxonomy
retention decisions
ticket validation
diagnostic logic
analytics
Mochi reasoning
PowerShell execution policy
```

AHK is the Windows interaction adapter.

---

# 7. Python Responsibilities

Python should own the trusted F7Hub boundary after transport.

Likely responsibilities:

```text
authenticate local request
validate contract
validate size
validate operation
sanitize metadata
apply privacy rules
invoke ClipboardService
return structured response
route approved action requests
```

The Python IPC adapter should not itself become Clipboard business logic.

---

# 8. Primary Manual Workflow

Target conceptual flow:

```text
Technician copies text
        ↓
Windows Clipboard
        ↓
Ctrl+Alt+C
        ↓
AHK collects:
  clipboard text
  foreground process
  window title
  capture method
        ↓
AHK builds clipboard.process request
        ↓
Local IPC
        ↓
Python contract adapter
        ↓
ClipboardService
        ↓
Classification / persistence
        ↓
clipboard.result
        ↓
AHK Quick HUD
```

---

# 9. Preserve Native Copy Behavior

Do not redefine normal:

```text
Ctrl+C
```

as F7Hub capture.

Windows/application copy behavior must remain native.

Recommended conceptual sequence:

```text
Ctrl+C
→ normal Windows copy

Ctrl+Alt+C
→ send current Clipboard contents to F7Hub
```

The exact default shortcut must be validated against existing F7Hub/AltF7Hub shortcuts.

---

# 10. Ctrl+Shift+C Conflict

Explicitly inspect whether:

```text
Ctrl+Shift+C
```

is already used by:

```text
File Explorer
Terminal
Windows applications
F7Hub
AltF7Hub
```

A global AHK override should not unintentionally suppress native behavior.

Candidate default:

```text
Ctrl+Alt+C
```

remains a recommendation, not an implementation decision until inspection.

---

# 11. Configurable Hotkeys

Phase 1B should define how Clipboard hotkeys depend on Phase 0D Settings.

Potential actions:

```text
clipboard.capture_current
clipboard.open_hud
clipboard.open_center
clipboard.pin_selected
```

Do not create separate AHK-owned configuration truth.

---

# 12. Hotkey Registry

Evaluate whether F7Hub should maintain a structured hotkey registry.

Conceptually:

```text
action_key
default_binding
effective_binding
scope
owner
global?
enabled?
```

Clipboard integration should consume the approved hotkey configuration mechanism.

---

# 13. Hotkey Validation

Plan validation for:

```text
duplicate F7Hub shortcut
duplicate AltF7Hub shortcut
Windows reserved shortcut
known application conflict
unsupported key combination
empty binding
```

Exact collision detection capabilities must be assessed.

---

# 14. Hotkey Failure Behavior

If a configured global hotkey cannot be registered:

```text
do not silently fail
```

Provide a recoverable state such as:

```text
Hotkey unavailable
```

with the binding visible in Settings or diagnostics.

---

# 15. Clipboard Read Timing

A manual F7Hub capture hotkey should normally read:

```text
the Clipboard content that already exists
```

rather than synthesize:

```text
Ctrl+C
```

automatically.

This avoids changing the active application's selection or state.

---

# 16. Optional Copy-and-Capture Action

A future separate action could perform:

```text
copy current selection
wait for clipboard update
capture
```

but this is a different workflow.

Do not merge it with:

```text
Send current Clipboard to F7Hub
```

without explicit design.

---

# 17. Clipboard Race Conditions

Windows Clipboard ownership can change rapidly.

Plan handling for:

```text
clipboard becomes empty
clipboard changes while being read
another application updates content
clipboard temporarily locked
large content delays
```

AHK should avoid assuming every Clipboard access succeeds immediately.

---

# 18. Clipboard Access Retry

Evaluate a small bounded retry strategy for transient Windows Clipboard lock failures.

Example concept:

```text
attempt
short delay
retry
```

with:

```text
strict maximum attempts
short total duration
```

Do not create indefinite loops.

---

# 19. No Testing Loops

Explicit rule:

```text
No unbounded polling.
No infinite clipboard retry.
No indefinite IPC retry.
No repeated GUI validation without state change.
```

Every retry must have:

```text
maximum count
maximum duration
observable failure result
```

This is particularly important given previous coding-agent looping problems.

---

# 20. Clipboard Sequence Number

Evaluate use of Windows Clipboard sequence information where available to determine:

```text
whether Clipboard changed during capture
```

Do not add platform complexity unless it materially improves reliability.

---

# 21. Clipboard Content Snapshot

Once the manual hotkey fires, create a stable in-memory snapshot.

Conceptually:

```text
capture_time
clipboard_text
source_context
```

The later Python request should use that snapshot.

Do not re-read Clipboard after the request begins unless explicitly retrying the capture.

---

# 22. Empty Clipboard

If Clipboard contains no supported text:

```text
return a lightweight HUD message
```

such as:

```text
No supported text in Clipboard
```

Do not send meaningless empty payloads into persistence.

---

# 23. Supported Format MVP

Phase 1B should assume Phase 1A MVP:

```text
text/plain
```

AHK may detect that other clipboard formats exist but should not attempt to serialize images, files, or RTF into this contract.

---

# 24. Unicode

AHK ↔ Python transport must preserve:

```text
French accents
Unicode paths
smart punctuation
technical symbols
emoji
```

Require:

```text
UTF-8
```

or the Phase 0B approved encoding.

---

# 25. Source Context

AHK can provide useful Windows context.

Potential:

```text
process executable
process PID
window title
window handle
capture timestamp
capture method
```

Do not persist everything simply because it can be collected.

---

# 26. Foreground Process

Preferred source identity may include:

```text
process_name
```

Example:

```text
OUTLOOK.EXE
powershell.exe
msedge.exe
```

Determine whether:

```text
PID
```

needs to cross the contract or is only temporary diagnostic metadata.

---

# 27. Window Title

Window title may be useful for context but may contain sensitive information.

Examples:

```text
customer name
email subject
ticket title
document name
```

Plan:

```text
maximum length
sanitization
persistence policy
Mochi eligibility
logging prohibition
```

---

# 28. Source Window Handle

A Windows HWND may be useful temporarily for:

```text
returning focus
positioning HUD
context validation
```

It should not automatically become durable domain data.

Evaluate whether HWND belongs only inside AHK runtime state.

---

# 29. Source URL

Do not assume AHK can reliably retrieve browser URL from every application.

Phase 1B must mark:

```text
browser source URL
```

as:

```text
optional
future
application-specific
```

unless existing F7Hub architecture already provides a safe mechanism.

---

# 30. Capture Method

Use Phase 1A/0B canonical values.

Potential:

```text
AHK_MANUAL
AHK_AUTOMATIC
F7HUB
IMPORT
```

Phase 1B focuses primarily on:

```text
AHK_MANUAL
```

---

# 31. Requested Action

AHK may optionally tell Python why capture occurred.

Example:

```text
PROCESS
OPEN_CENTER
ATTACH_TO_ACTIVE_TICKET
```

Only support actions explicitly designed and validated.

Do not make free-form action strings executable.

---

# 32. AHK → Python Contract

Phase 1B should define the Clipboard-specific payload within the approved Phase 0B envelope.

Conceptually:

```json
{
  "contract_version": "1.0",
  "message_id": "uuid",
  "message_type": "command",
  "operation": "clipboard.process",
  "timestamp": "...",
  "source": {
    "component": "altf7hub",
    "technology": "ahk_v2",
    "application": "powershell.exe",
    "window_title": "Administrator: PowerShell"
  },
  "payload": {
    "capture_method": "AHK_MANUAL",
    "content": {
      "format": "text/plain",
      "value": "Get-Service Spooler"
    }
  }
}
```

This is conceptual.

Use the approved Phase 0B schema rather than creating a parallel envelope.

---

# 33. Contract Size

AHK should enforce an initial sanity check before transmitting extreme content.

Python remains authoritative for maximum-size validation.

This gives:

```text
AHK
→ early UX protection

Python
→ authoritative security rule
```

---

# 34. Do Not Trust AHK Metadata

Python must validate:

```text
operation
format
payload size
enums
context IDs
source metadata shape
```

AHK is local but still outside the trusted application-service boundary.

---

# 35. Transport Decision

Phase 1B is the correct place to recommend the actual AHK ↔ Python transport.

Evaluate at minimum:

```text
localhost HTTP
Windows Named Pipes
local socket if applicable
stdin/stdout helper process
```

Do not select purely on novelty.

---

# 36. Transport Evaluation Criteria

Compare:

```text
implementation complexity
AHK v2 support
Python support
security
authentication
latency
debuggability
testability
single-instance behavior
message framing
timeouts
error handling
Windows compatibility
deployment complexity
```

---

# 37. Localhost HTTP

Evaluate advantages:

```text
AHK WinHttp support
simple request/response
easy JSON
easy testing
debuggable
```

Risks:

```text
local listener
port management
authentication
firewall/security perception
accidental broader binding
```

If used:

```text
127.0.0.1 only
```

must be considered mandatory.

---

# 38. Named Pipes

Evaluate advantages:

```text
Windows-native local IPC
no TCP port
local security boundary
```

Costs:

```text
more AHK complexity
message framing
testing complexity
reconnection behavior
```

Do not choose Named Pipes automatically merely because they are Windows-native.

---

# 39. stdin/stdout Helper

Evaluate whether AHK spawning Python per capture is acceptable.

Likely drawbacks:

```text
startup latency
process churn
state loss
harder context continuity
```

A persistent F7Hub Python application/service is likely preferable if already available.

Verify.

---

# 40. Recommended Transport Output

Phase 1B must produce:

```text
Primary recommendation
Secondary fallback
Rejected options
Reason
```

If transport cannot yet be safely selected:

```text
REQUIRES_USER_DECISION
```

---

# 41. Persistent Python Endpoint

Evaluate whether Clipboard integration talks to:

```text
running F7Hub process
```

or:

```text
dedicated local bridge/service
```

Prefer the simplest architecture consistent with F7Hub lifecycle.

Do not introduce a new Windows service unless clearly justified.

---

# 42. F7Hub Not Running

Define behavior when the capture hotkey fires and Python is unavailable.

Possible approaches:

```text
show F7Hub unavailable
offer Open F7Hub
optionally launch F7Hub
```

Do not silently drop the request.

---

# 43. Auto-Launch

Determine whether AHK is allowed to start F7Hub when required.

Potential benefits:

```text
better UX
```

Potential issues:

```text
unexpected startup
multiple instances
startup latency
race with IPC readiness
```

Recommend explicitly.

---

# 44. Startup Handshake

If F7Hub auto-launch is supported:

```text
AHK
→ launch F7Hub
→ wait bounded time for readiness
→ send request
```

Never:

```text
while not ready:
    retry forever
```

---

# 45. Singleton Requirement

Inspect current F7Hub single-instance behavior.

Clipboard IPC must not accidentally create:

```text
multiple Python F7Hub processes
```

to process one capture.

---

# 46. IPC Authentication

If transport permits other local processes to connect, define an authentication mechanism.

For localhost HTTP, evaluate:

```text
per-session token
installation token
random runtime secret
```

Do not hard-code credentials into source.

---

# 47. Authentication Token Storage

If a local IPC token is required, determine how AHK obtains it safely.

Possible:

```text
restricted runtime file
environment inherited from launcher
handshake
Windows IPC ACL
```

Do not put long-lived secrets into normal Settings.

---

# 48. Endpoint Allowlist

The local bridge should expose only approved operations.

Good:

```text
clipboard.process
clipboard.action
application.status
```

Bad:

```text
/run_any_command
```

No generic arbitrary-command endpoint.

---

# 49. Rate Limiting

Even local manual capture can accidentally repeat.

Plan simple rate protection.

Potential:

```text
maximum requests per short interval
```

Automatic capture later will need stricter controls.

Do not reject legitimate manual captures merely due to aggressive throttling.

---

# 50. Timeouts

Define separate timeout concepts:

```text
connection timeout
request timeout
processing timeout
HUD timeout
```

Do not use one magic number everywhere.

---

# 51. Manual Capture Processing Timeout

A manual small-text request should have a short bounded timeout.

If Python continues processing beyond the interactive window, evaluate whether AHK should receive:

```text
accepted / processing
```

rather than waiting indefinitely.

---

# 52. Synchronous vs Asynchronous

For initial manual text capture, evaluate:

```text
synchronous request/response
```

because processing should usually be fast.

For future large content:

```text
asynchronous result
```

may become appropriate.

Do not complicate MVP prematurely.

---

# 53. Transport Retry

A retry due to network/pipe failure must reuse:

```text
message_id
```

so Python can distinguish:

```text
same transport request
```

from:

```text
new user capture
```

---

# 54. Transport Retry vs Capture Event

Important invariant:

```text
retrying delivery
```

must not create:

```text
another Capture Event
```

for the same manual capture.

A second actual hotkey press may create another Capture Event.

---

# 55. Idempotency

Phase 1B should define:

```text
message_id
```

as the transport idempotency identity.

Phase 1A:

```text
content_hash
```

remains the content deduplication identity.

Do not confuse them.

---

# 56. Response Contract

The Python response should use Phase 0B conventions.

Possible payload:

```json
{
  "clipboard_item_id": 901,
  "duplicate": false,
  "primary_kind": "powershell_command",
  "sensitivity": "normal",
  "entities": [
    {
      "entity_type_key": "powershell_command",
      "display_value": "Get-Service Spooler"
    }
  ],
  "tags": [
    {
      "tag_key": "powershell",
      "display_name": "PowerShell"
    }
  ],
  "available_actions": [
    "clipboard.open_center",
    "script.search",
    "kb.search"
  ]
}
```

Exact vocabulary must come from approved phases.

---

# 57. Response Should Be HUD-Friendly

AHK should not need to understand complex domain structures.

Response should provide enough presentation-ready summary for the HUD.

Potential:

```text
primary label
secondary summary
top entities
available action keys
status
clipboard_item_id
```

---

# 58. AHK Does Not Reclassify

AHK should not inspect the result and decide:

```text
IP address means Networking
```

Python already owns classification.

AHK may map:

```text
action_key
```

to a HUD button.

---

# 59. Quick HUD Purpose

The AHK HUD should answer:

```text
Was it captured?

What did F7Hub recognize?

What are the most useful next actions?
```

It should not become a second Clipboard Center.

---

# 60. HUD Example

Conceptual:

```text
┌──────────────────────────────┐
│ F7Hub Clipboard             │
│                              │
│ IPv4 detected                │
│ 10.0.0.87                    │
│                              │
│ [Ping] [DNS Lookup]          │
│ [Attach to Ticket]           │
│ [Open Clipboard Center]      │
└──────────────────────────────┘
```

---

# 61. HUD Information Limit

Show only:

```text
primary result
small preview
important entity
2 to 4 top actions
```

Avoid rendering:

```text
full logs
dozens of entities
all tags
relationship history
```

That belongs in PySide6 Clipboard Center.

---

# 62. HUD Position

Evaluate placement:

```text
near mouse
near active window
fixed screen corner
```

Reuse existing AltF7Hub HUD conventions if available.

Do not create a new positioning system unnecessarily.

---

# 63. HUD Transparency

If AltF7Hub already supports transparent GUIs, reuse those conventions.

Ensure:

```text
text readability
screenshot testability
Windows scaling
```

remain acceptable.

---

# 64. HUD Lifetime

Potential:

```text
auto-dismiss after configurable interval
```

unless user interacts.

HUD timeout belongs to Settings.

Do not auto-dismiss while a menu/dialog is actively being used.

---

# 65. HUD Keyboard Navigation

Plan support for:

```text
Escape → close
Enter → primary action
arrow/tab → navigate actions
```

only if consistent with AltF7Hub accessibility conventions.

---

# 66. HUD Mouse Interaction

All actions must be clickable.

Do not rely solely on keyboard shortcuts.

---

# 67. HUD Focus Behavior

Avoid stealing focus from the technician unnecessarily.

Evaluate:

```text
non-activating HUD
```

where technically appropriate.

But if keyboard interaction requires focus, behavior must be explicit.

---

# 68. Source Application Focus

After HUD closes or action completes, determine whether focus returns to the source application.

Do not implement fragile forced-focus behavior without justification.

---

# 69. HUD Error State

Examples:

```text
F7Hub unavailable
Unsupported content
Sensitive content blocked
Clipboard too large
Capture failed
```

Messages should be concise.

Detailed error belongs in logs/F7Hub.

---

# 70. HUD Partial Success

Example:

```text
Captured
Classification incomplete
```

HUD should indicate capture succeeded even if optional enrichment failed.

---

# 71. HUD Duplicate State

Potential:

```text
Already known
Seen 8 times
```

This can be useful.

Do not make duplicate captures look like failures.

---

# 72. HUD Action Keys

The HUD should receive stable machine action keys.

Potential:

```text
clipboard.open_center
ticket.attach
diagnostic.run_network
dns.lookup
script.search
kb.search
mochi.ask
```

Do not hard-code business meaning into button labels only.

---

# 73. Action Execution Boundary

When technician clicks HUD:

```text
Ping
```

AHK should not necessarily run:

```text
ping.exe
```

directly.

Preferred conceptual route:

```text
HUD action
   ↓
structured action request
   ↓
Python
   ↓
approved F7Hub service
```

This preserves security and auditability.

---

# 74. Pure UI Actions

Some actions may safely remain local.

Example:

```text
Open Clipboard Center
Close HUD
Copy processed value
```

Classify which actions:

```text
LOCAL_UI
APPLICATION_COMMAND
DIAGNOSTIC_COMMAND
```

---

# 75. Diagnostic Actions

Example:

```text
Run Network Diagnostic
```

must route into the Diagnostic Service.

AHK must not execute diagnostic PowerShell directly.

---

# 76. Ticket Actions

Example:

```text
Attach to Ticket
```

must use Python/Ticket service validation.

AHK must not write ticket relationships.

---

# 77. KB Actions

Example:

```text
Search KB
```

may open F7Hub with a structured search context.

The search term should come from the validated result/entity rather than arbitrary HUD reconstruction.

---

# 78. Mochi Action

A future:

```text
Ask Mochi
```

should send:

```text
clipboard_item_id
```

or approved context reference to Python.

AHK should not assemble AI prompts.

---

# 79. Open Clipboard Center

Plan a navigation request such as:

```text
open Clipboard Center
select item 901
```

rather than launching a duplicate standalone clipboard window if the main F7Hub GUI already owns the full interface.

---

# 80. Main App Already Open

If F7Hub is running:

```text
bring appropriate window/module forward
```

through existing application navigation mechanisms.

Inspect current bootstrap/navigation design.

---

# 81. Main App Closed

If allowed:

```text
launch F7Hub
wait for readiness
navigate to Clipboard Center
select captured item
```

This should be bounded and deterministic.

---

# 82. Capture Without Main GUI

Evaluate whether Clipboard capture can work when:

```text
F7Hub GUI is closed
```

but a Python bridge is running.

This has significant architecture implications.

Do not introduce a resident background service casually.

---

# 83. Recommended MVP Lifecycle

Likely simplest MVP:

```text
F7Hub running
→ Clipboard capture available

F7Hub not running
→ HUD offers Open F7Hub
```

unless current AltF7Hub architecture already supports safely launching/communicating with F7Hub.

---

# 84. Future Background Bridge

A future persistent local bridge may support:

```text
clipboard capture without visible F7Hub
Mochi
launcher commands
```

but this should be a separate architectural decision.

---

# 85. Manual vs Automatic Capture

Phase 1B should design manual capture completely.

Automatic capture should remain:

```text
FUTURE
```

unless user requirements explicitly change.

---

# 86. Why Automatic Capture Is Different

`OnClipboardChange` can observe:

```text
passwords
MFA codes
customer data
private URLs
personal text
large logs
rapid repeated copies
```

Therefore automatic mode requires:

```text
application exclusions
secret filtering
rate limiting
temporary processing
retention rules
pause control
```

---

# 87. Automatic Capture Architecture Placeholder

Future conceptual flow:

```text
Windows ClipboardChanged
      ↓
AHK policy gate
      ↓
local sensitivity precheck
      ↓
Python authoritative check
```

Do not implement in initial Clipboard integration.

---

# 88. Application Exclusions

Future auto-capture should likely support exclusions such as:

```text
password managers
credential dialogs
private applications
```

Exact list requires careful design.

Manual capture remains safer initially.

---

# 89. Privacy Precheck in AHK

Evaluate whether AHK should perform only minimal obvious protection before transport.

Example:

```text
content exceeds enormous size
unsupported format
```

Avoid duplicating Python secret-detection logic in AHK.

Python remains authoritative.

---

# 90. Sensitive Result

If Python identifies:

```text
SECRET_POSSIBLE
```

AHK HUD should not echo the full secret back visibly.

Show:

```text
Sensitive content detected
Not saved
```

or equivalent.

---

# 91. HUD Privacy

Do not display complete sensitive Clipboard content on top of other windows.

For potentially sensitive data:

```text
redacted preview
```

should be used.

---

# 92. Logging Boundary

AHK logs may include:

```text
message_id
operation
response status
duration
error code
```

Do not log raw Clipboard text.

---

# 93. Python Logs

Same principle.

Operational logs should prefer:

```text
clipboard_item_id
size
kind
status
counts
```

over raw payload.

---

# 94. Contract Debugging

If developer/debug mode allows payload inspection:

```text
explicitly gated
redacted where possible
disabled by default
```

Do not normalize raw Clipboard logging into standard troubleshooting.

---

# 95. Error Categories

Phase 1B should map Phase 0B errors into user-relevant states.

Examples:

```text
IPC_UNAVAILABLE
IPC_AUTH_FAILED
CONTRACT_INVALID
EMPTY_CLIPBOARD
UNSUPPORTED_FORMAT
PAYLOAD_TOO_LARGE
SENSITIVE_CONTENT_BLOCKED
PROCESSING_TIMEOUT
PROCESSING_ERROR
```

Use approved naming conventions.

---

# 96. AHK Error Handling

AHK should:

```text
display concise result
retain normal Clipboard
not crash
not enter retry loop
```

Errors should not alter Clipboard content unless explicitly required.

---

# 97. Clipboard Mutation

Default capture should be:

```text
READ ONLY
```

with respect to Windows Clipboard.

Do not replace Clipboard text with normalized/classified values automatically.

---

# 98. Future Transform Actions

Potential actions:

```text
Normalize text
Format PowerShell error
Normalize ticket data
```

may intentionally replace Clipboard content.

Those should be explicit separate commands.

---

# 99. AHK ↔ Python Health Check

Evaluate a lightweight:

```text
application.status
```

or equivalent readiness check.

Avoid polling continuously.

Only use when needed:

```text
startup
capture after connection failure
explicit diagnostics
```

---

# 100. Connection Reuse

If using HTTP or pipe, evaluate persistent vs per-request connections.

Prefer simplicity unless connection overhead becomes material.

---

# 101. Port Selection

If localhost HTTP is selected:

```text
do not hard-code an arbitrary public port without design
```

Evaluate:

```text
fixed documented loopback port
dynamic port + discovery
runtime endpoint file
```

Each has tradeoffs.

---

# 102. Endpoint Discovery

If dynamic:

```text
AHK needs a trusted way to discover the endpoint
```

Potential:

```text
runtime file in user profile
```

with:

```text
endpoint
token
process id
```

Security and cleanup must be reviewed.

---

# 103. Named Pipe Naming

If Named Pipes:

```text
pipe name
user/session scope
access control
single-instance behavior
```

must be explicitly defined.

---

# 104. Session Scope

The integration should generally communicate inside:

```text
current Windows user session
```

Do not unintentionally make F7Hub IPC machine-wide.

---

# 105. Multi-User Windows

If multiple users are logged in:

```text
one user's AltF7Hub
```

must not communicate with:

```text
another user's F7Hub
```

where avoidable.

---

# 106. Privilege Boundary

Avoid requiring:

```text
Run as Administrator
```

for normal Clipboard capture.

If AHK and F7Hub run at different integrity levels, Windows interaction may differ.

Document expected privilege level.

---

# 107. Elevated Applications

AHK may have difficulty interacting with elevated windows if it is not elevated.

Determine whether manual Clipboard reading still works because content is already in Windows Clipboard.

Do not elevate the entire architecture merely for window metadata.

---

# 108. UIPI Considerations

Inspect whether current AHK integration already handles Windows User Interface Privilege Isolation.

Mark limitations rather than introducing unsafe elevation.

---

# 109. Source Metadata Failure

If process/window metadata cannot be obtained:

```text
capture should still proceed
```

where safe.

Source context is enrichment.

Clipboard content is primary.

---

# 110. Metadata Truncation

Set limits for:

```text
window title
application string
optional URLs
```

to prevent enormous or malicious metadata fields.

---

# 111. Input Sanitization

Do not treat:

```text
window title
application name
clipboard text
```

as executable input.

All remain data.

---

# 112. No Shell Construction

Never generate shell commands by concatenating Clipboard text.

Any later diagnostic/action must use:

```text
approved action key
validated parameter
```

---

# 113. Test Architecture

Phase 1B must plan tests for:

```text
AHK contract construction
Python contract validation
transport
idempotency
timeouts
source metadata
Unicode
empty Clipboard
large Clipboard
service unavailable
sensitive content
HUD behavior
hotkey conflict
main app unavailable
```

---

# 114. Contract Tests

Create future fixtures for:

```text
valid manual capture
missing content
unknown capture method
invalid message version
oversize content
Unicode
malformed JSON
duplicate message ID
```

---

# 115. Transport Tests

Future tests:

```text
connect
send
receive
timeout
authentication failure
server unavailable
server restart
malformed response
duplicate delivery
```

---

# 116. Native Windows Tests

Required eventual tests should include actual Windows behavior for:

```text
hotkey
Clipboard read
source application
window title
HUD placement
focus behavior
F7Hub launch/navigation
```

Do not rely solely on mocked unit tests.

---

# 117. GUI Screenshot Validation

AHK HUD native validation should include screenshots.

Screenshots should verify:

```text
legibility
transparency
DPI
no clipping
buttons visible
sensitive preview redaction
```

This should remain compatible with Codex visual review.

---

# 118. DPI Testing

At minimum consider:

```text
96 DPI
125%
150%
```

depending on existing test conventions.

Do not require exhaustive matrices in every slice.

---

# 119. Multi-Monitor

Evaluate future tests for:

```text
primary monitor
secondary monitor
different DPI
negative coordinates
```

HUD should remain on-screen.

---

# 120. Hotkey Tests

Future validation:

```text
register
trigger
unregister
conflict
settings change
restart
```

No global hotkeys should be left registered after tests.

---

# 121. Process Cleanup

Testing must verify:

```text
no orphan Python bridge
no orphan AHK process
no stale test HUD
no stale IPC endpoint
```

---

# 122. Retry Tests

Explicitly test bounded behavior.

Example:

```text
Python unavailable

AHK attempts:
N bounded attempts

Result:
fails visibly
stops retrying
```

This guards against the testing-loop failure mode.

---

# 123. Performance Targets

Recommend measurable targets, not claims.

For small manual text:

```text
hotkey → request dispatch
very fast

round-trip processing
interactive

HUD appearance
near-immediate
```

Suggested numerical targets may be proposed after inspection.

---

# 124. Startup Performance

If capture can launch F7Hub, measure separately.

Do not treat application startup latency as normal Clipboard processing latency.

---

# 125. Quick HUD Action Latency

Opening Clipboard Center may be slower than:

```text
Close
Pin
```

HUD should provide appropriate state.

Avoid freezing AHK while waiting for heavy application work.

---

# 126. Async HUD Actions

Longer action:

```text
Run Diagnostic
```

may return:

```text
Diagnostic started
```

rather than keeping the HUD blocked until the diagnostic finishes.

---

# 127. Quick HUD State Machine

Evaluate a simple state model:

```text
CAPTURING
PROCESSING
SUCCESS
PARTIAL
BLOCKED
ERROR
```

Do not create excessive UI state complexity.

---

# 128. Processing Indicator

If processing takes more than a brief threshold, show:

```text
Processing…
```

Avoid flashing a spinner for instantaneous captures.

---

# 129. Cancel

For a small synchronous manual capture, cancellation may not be necessary.

Do not add Cancel unless processing can meaningfully be stopped.

---

# 130. Clipboard Result Cache in AHK

Avoid durable AHK caching.

AHK may retain temporary runtime state such as:

```text
current clipboard_item_id
available actions
HUD data
```

until HUD closes.

Canonical state stays in F7Hub.

---

# 131. Restart Behavior

After AHK restart:

```text
previous HUD context may disappear
```

That is acceptable.

Durable Clipboard Items remain in SQLite.

---

# 132. Action After HUD Close

If the user later wants the item:

```text
Clipboard Center
```

is the durable management surface.

Do not try to make the HUD maintain history.

---

# 133. Quick HUD vs Clipboard Center Boundary

Quick HUD:

```text
fast
small
contextual
temporary
action-oriented
```

Clipboard Center:

```text
searchable
persistent
inspectable
filterable
relationship-aware
retention-aware
```

Keep this distinction explicit.

---

# 134. Quick HUD vs Mochi Sidebar

HUD:

```text
immediate Windows interaction
```

Mochi sidebar:

```text
deeper contextual assistance
```

Do not place a full conversational assistant inside the AHK HUD.

---

# 135. Settings Dependencies

Phase 1B should consume settings for:

```text
capture hotkey
HUD enabled
HUD duration
HUD position strategy
auto-launch F7Hub
transport timeout
```

Possible future:

```text
automatic capture
```

Do not create duplicate config files unless Phase 0D explicitly requires them.

---

# 136. Runtime Infrastructure Settings

Transport endpoint or runtime token may be:

```text
runtime infrastructure
```

not normal user settings.

Do not expose sensitive internals in the Settings GUI unnecessarily.

---

# 137. Security Decision

The transport must preserve:

```text
least privilege
local-only communication
schema validation
operation allowlist
bounded payload size
authentication where necessary
```

---

# 138. Threat Model

At minimum consider:

```text
malicious local process sending requests
crafted Clipboard payload
huge payload
replay
duplicate request
fake source metadata
injection through action parameters
stale IPC token
port exposure
```

---

# 139. Replay Handling

If message IDs are retained briefly, repeated identical transport requests can be detected.

Do not create an unbounded replay database solely for local Clipboard IPC.

Recommend reasonable scope.

---

# 140. Transport Authentication Failure

Must produce:

```text
SECURITY_ERROR
```

or approved equivalent.

Do not fall back to unauthenticated mode.

---

# 141. IPC Version Mismatch

If AHK speaks an unsupported major contract version:

```text
reject clearly
```

and advise update/restart.

Do not guess the payload semantics.

---

# 142. Update Compatibility

AHK and Python may eventually update independently.

Phase 1B must use Phase 0B compatibility rules to tolerate:

```text
new optional fields
```

while rejecting:

```text
breaking major-version mismatch
```

---

# 143. Installation Packaging Impact

Identify future installer considerations:

```text
AHK script/application startup
Python/F7Hub endpoint startup
firewall behavior if localhost HTTP
runtime config location
single-instance startup
```

Do not modify Installer during planning.

---

# 144. Development Mode

Developer environments may need:

```text
verbose IPC diagnostics
mock server
test port/pipe
```

Keep them separated from production behavior.

---

# 145. Mock Python Endpoint

For AHK tests, a test endpoint may return deterministic fixture responses.

This enables testing without:

```text
database
full F7Hub startup
```

but integration tests must still cover the real boundary.

---

# 146. Mock AHK Producer

Python contract tests should also generate AHK-equivalent fixture payloads without needing live AHK.

Both sides need independent testability.

---

# 147. Contract Golden Fixtures

Maintain shared valid fixture(s) that both AHK and Python tests use conceptually.

This prevents schema drift.

---

# 148. Documentation Impact

Future implementation will likely affect:

```text
11_AHKArchitecture.md
13_PythonArchitecture.md
06_SystemArchitecture.md
04_UserWorkflows.md
05_GUI.md
```

Possibly:

```text
02_ProductRequirements.md
03_Features.md
```

depending on final feature scope.

---

# 149. Required Transport Comparison

Produce a formal table covering at least:

| Criterion | Localhost HTTP | Named Pipe | Per-call Process |
|---|---:|---:|---:|
| AHK simplicity | | | |
| Python simplicity | | | |
| Security | | | |
| Testing | | | |
| Deployment | | | |
| Latency | | | |
| Debugging | | | |
| Recommendation | | | |

Use repository evidence where relevant.

---

# 150. Required Sequence Diagram

Produce:

```text
User
 ↓
Windows Clipboard
 ↓
AHK Hotkey
 ↓
Capture Snapshot
 ↓
JSON Contract
 ↓
Transport
 ↓
Python Adapter
 ↓
ClipboardService
 ↓
ClipboardRepository
 ↓
Response
 ↓
AHK HUD
```

---

# 151. Required Failure Sequence

Show:

```text
AHK
 ↓
Python unavailable
 ↓
bounded retry / readiness check
 ↓
failure
 ↓
HUD:
F7Hub unavailable
```

No background retry loop.

---

# 152. Required Idempotency Diagram

Show distinction between:

```text
same message retransmitted
```

and:

```text
same Clipboard content captured again later
```

This is a mandatory output.

---

# 153. Required Responsibility Matrix

Include:

| Responsibility | AHK | Python IPC | Clipboard Service | SQLite |
|---|---:|---:|---:|---:|
| Read Clipboard | OWN | No | No | No |
| Validate contract | No | OWN | No | No |
| Classify | No | No | OWN | No |
| Deduplicate | No | No | OWN | Support |
| Persist | No | No | Orchestrate | OWN data |
| HUD | OWN | No | No | No |

Refine based on existing architecture.

---

# 154. Required Hotkey Inventory

Inspect all current global/application shortcuts and produce:

```text
existing binding
owner
scope
conflict?
recommended Clipboard binding
```

Do not register anything.

---

# 155. Required Source Metadata Matrix

Evaluate:

| Metadata | Capture | Transmit | Persist | Log | Mochi |
|---|---:|---:|---:|---:|---:|
| Process name | | | | | |
| PID | | | | | |
| Window title | | | | | |
| HWND | | | | | |
| Source URL | | | | | |

Privacy must drive recommendations.

---

# 156. Required Error Matrix

For:

```text
AHK hotkey conflict
Clipboard locked
Clipboard empty
unsupported format
service unavailable
authentication failure
timeout
invalid JSON
unsupported version
payload too large
secret blocked
partial processing
```

define:

```text
AHK response
retry?
HUD?
log?
user action?
```

---

# 157. Required HUD State Matrix

At minimum:

```text
SUCCESS
DUPLICATE
PARTIAL
BLOCKED
ERROR
```

For each define:

```text
title
preview policy
actions
auto-dismiss?
```

---

# 158. Required Action Matrix

For candidate HUD actions identify:

```text
action key
local or Python-routed
required entity/context
security level
sync/async
```

Examples:

```text
Open Clipboard Center
Pin
Attach to Ticket
Search KB
Run Diagnostic
Ask Mochi
```

---

# 159. Required Privacy Matrix

Cover:

```text
normal text
email
window title with customer name
password-like text
API key
MFA code
large log
URL
```

For each:

```text
AHK display?
transmit?
Python persist?
HUD preview?
log?
```

---

# 160. Required Settings Inputs

List all settings Phase 1B requires from Phase 0D.

Mark:

```text
CORE
LIKELY
FUTURE
NOT NEEDED
```

---

# 161. Required Existing-Code Impact Assessment

Identify likely components as:

```text
REUSE
EXTEND
NEW
NOT NEEDED
NOT VERIFIED
```

for:

```text
AHK hotkey manager
AHK HTTP/IPC helper
AHK HUD base
Python IPC adapter
application singleton
navigation service
settings service
logging
```

No implementation.

---

# 162. Required Security Review

Explicitly validate:

```text
No arbitrary command endpoint
No direct AHK DB access
No hard-coded secret
No broad network binding
No unbounded payload
No unbounded retry
No raw Clipboard logging
No automatic PowerShell execution
```

---

# 163. Planning Depth

Classify topics:

```text
DECIDE NOW
DESIGN NEXT
DEFER
```

Likely `DECIDE NOW`:

```text
transport
manual capture semantics
idempotency
source metadata
hotkey ownership
HUD boundary
service-unavailable behavior
security model
```

Likely `DESIGN NEXT`:

```text
exact HUD geometry
exact icons
animations
```

Likely `DEFER`:

```text
automatic capture
browser URL extraction
binary formats
OCR
background resident bridge
```

unless existing architecture changes the recommendation.

---

# 164. Acceptance Criteria

Phase 1B is acceptable when:

1. Existing AHK integration architecture has been inspected.
2. Existing hotkeys have been inventoried.
3. Manual capture semantics are defined.
4. AHK/Python responsibilities are explicit.
5. AHK does not own persistence or business rules.
6. Transport options have been compared.
7. A transport recommendation or explicit decision gate exists.
8. Local IPC security requirements are defined.
9. Contract usage matches Phase 0B.
10. Transport retry and content deduplication are clearly distinguished.
11. Bounded retry behavior is defined.
12. F7Hub-unavailable behavior is defined.
13. Source metadata is defined with privacy rules.
14. Quick HUD scope is defined.
15. HUD action routing is defined.
16. Clipboard content remains read-only by default.
17. Sensitive HUD behavior is defined.
18. Hotkey configuration integrates with Settings.
19. Native Windows validation requirements are defined.
20. Automatic capture remains clearly separated from manual capture.
21. No production implementation has occurred.
22. Phase 1C can design the full PySide6 Clipboard Center independently.
23. Future implementation can be decomposed into small vertical slices.

---

# 165. Validation

Return:

```text
Current AHK inspection              PASS / FAIL / BLOCKED
Hotkey inventory                    PASS / FAIL / BLOCKED
Manual capture model                PASS / FAIL / BLOCKED
Transport evaluation                PASS / FAIL / BLOCKED
Contract integration                PASS / FAIL / BLOCKED
Idempotency model                   PASS / FAIL / BLOCKED
Retry/timeout model                 PASS / FAIL / BLOCKED
Source metadata model               PASS / FAIL / BLOCKED
Privacy review                      PASS / FAIL / BLOCKED
Security review                     PASS / FAIL / BLOCKED
HUD architecture                    PASS / FAIL / BLOCKED
Action-routing model                PASS / FAIL / BLOCKED
Settings integration                PASS / FAIL / BLOCKED
Testing strategy                    PASS / FAIL / BLOCKED
Scope control                       PASS / FAIL / BLOCKED
Production changes                  MUST BE NONE
Database changes                    MUST BE NONE
```

---

# 166. Required Final Report

Return in this order:

## Summary

Recommended Windows Clipboard integration architecture.

## Current State

Existing AHK, Python, hotkey and IPC capabilities.

## Responsibility Boundary

AHK vs Python vs Clipboard domain.

## Manual Capture Workflow

Exact conceptual behavior.

## Hotkey Architecture

Inventory, conflicts and recommended binding strategy.

## Source Context

Process/window/context metadata and privacy.

## Contract Usage

Phase 0B request/result usage.

## Transport Evaluation

HTTP vs Named Pipes vs alternatives.

## Transport Recommendation

Recommended option and fallback.

## Security Architecture

Authentication, allowlists, binding, trust boundaries.

## Idempotency & Retry

Transport retries vs real capture events.

## F7Hub Availability

Running/not-running/startup behavior.

## Quick HUD

Purpose, states, actions and limits.

## Action Routing

Local UI vs Python/application commands.

## Privacy

Sensitive content and display restrictions.

## Settings Inputs

Required Phase 0D settings.

## Testing Strategy

Unit, contract, integration and native Windows validation.

## Existing-Code Impact

REUSE / EXTEND / NEW / NOT VERIFIED.

## Decision Register

Resolved, deferred and user-review decisions.

## Risk Register

Integration-specific risks.

## Recommended Implementation Slices

Only identify small future slices.

Do not implement them.

## Phase 1C Inputs

Explicit assumptions the PySide6 Clipboard Center plan may rely on.

## Result

Return exactly one:

```text
READY_FOR_CLIPBOARD_GUI_DESIGN
REQUIRES_CLIPBOARD_INTEGRATION_DECISIONS
BLOCKED
```

Do not return:

```text
READY_FOR_IMPLEMENTATION
```

Phase 1B remains architecture planning.