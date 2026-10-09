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


---

# EXECUTION REPORT

## Summary

Date: 2026-10-07, America/Toronto. Mode: ARCHITECT / PLAN. Planning status: READY_FOR_REVIEW. New decisions: RECOMMENDED, never independently APPROVED. This report consumes approved Phase 1A and executes the preserved 166-section Phase 1B contract. The user's current hotkey priority is Win+Alt+C, then Win+Alt+V, then Win+Alt+B; historical Ctrl+Alt+C examples above remain unchanged.

Recommend manual text/plain capture through the existing shared AHK host, an immutable snapshot, authenticated Windows Named Pipes terminating in the running F7Hub application, and a small privacy-safe AHK Quick HUD. Python admission invokes ClipboardService; repositories retain persistence ownership. Normal copy and the Windows Clipboard remain untouched. Capture is LOCAL_REQUIRED; Mochi, Analytics, external providers and automatic capture are not prerequisites.

A short-lived AHK snapshot worker is recommended solely to contain potentially blocking native Clipboard reads; it is not a second Clipboard application, persistent bridge, or per-capture Python domain processor. A sensitive channel needs new authenticated bootstrap and singleton safeguards; the existing cosmetic and guide protocols cannot supply them unchanged.

Author-side outcome: 23/23 PASS at architecture-planning depth. No blocking Foundation/Phase 1A conflict or unresolved material user choice identified. This is an UNAPPROVED candidate for independent architecture review, not closure, runtime acceptance, implementation authority or permission to start 1C.

## Baseline / Candidate Identity

| Item | FRESH evidence |
| --- | --- |
| Repository / initial branch | C:/Dev/F7Hub / main |
| HEAD / origin/main / live remote main | db7b7b387806fce786a05ee3f9bc14ee29cdbd60, all equal |
| Origin | https://github.com/JDecelles1990/F7Hub.git |
| Initial tracked/index | No changes / empty |
| Initial untracked inventory | Only AutoHotkey/Troubleshooting_Sections/GuideSettings.ini; Git pathname inventory only |
| Original target Git blob / bytes | 1b22658e671246f7a90c1565d137886c2b7b0ff9 / 47,479 |
| Original checkout SHA-256 | ae5391ab305f1bb99ae27258372744d533468e92454e898fee76e73a8e07a64e |
| Original checkout bytes / lines | 50,774 bytes; 3,295 LF terminators; 3,296 logical lines; CRLF representation |
| Original final newline | NONE; append supplies a separator after the complete original bytes |
| Candidate branch | docs/clipboard-1b-execution-20261007 |
| Candidate final identity | Computed outside this document after all edits; no self-changing hash |
| Candidate state | UNSTAGED / UNCOMMITTED / UNPUBLISHED / UNAPPROVED / NOT INTEGRATED |

Executed initial commands: git branch --show-current; rev-parse HEAD and origin/main; status --short; diff --name-only; diff --cached --name-only; ls-files --others --exclude-standard; diff --check; ls-remote origin refs/heads/main; remote -v; input rev-parse and target cat-file -s; raw checkout identity. Branch created only after the required baseline and blob gates passed. Final scope, exact raw/filtered prefix, document structure and identity checks follow authoring. No protected-file content or metadata operation occurred.

## Approved Inputs

Current Git identities were verified; user-supplied CLOSED status supplies approval authority. First-parent history corroborates normal PR #72 and #71 merges. Historical candidate labels inside upstream reports remain historical, not current refusal of the user's explicit closure record.

| Owner | Verified current Git blob | Consumed constraint |
| --- | --- | --- |
| [1A](1A_Clipboard_Domain_Data_Lifecycle.md#execution-report) | 3de37546de73e4243bcc361cd42847aa7d218833 | Item/Event/operation distinction; exact identity versus search normalization; secret exclusion; off-default history; typed transient references; atomic acceptance; producer/generation leases; source minimization; downstream contract |
| [0A](<../Foundation/0A_Master_Foundation_Architectural_Contract.md#execution-report>) | b2bfc2f330ea582a224cd6d2c72eb899160725e2 | Technology/layer/trust ownership; local-required behavior; services own actions |
| [0B](<../Foundation/0B_Global_JSON_Contract_Interoperability_Grammar.md#execution-report>) | e290ba6c9c8cf570f380a10575cb219bdfadfbf4 | Seven-field envelope; composite versions; classes/correlation; strict JSON; limits; authenticated sensitive IPC; uncertain dispatch |
| [0C](../Foundation/0C_Taxonomy_Information_Vocabulary.md#execution-report) | 8e6fcbfc24b486c92983b13c2488f57a3a0dd2f4 | Feature-owned Kind/Entity occurrences/provenance; global Tag identities; no inference of business identity or permission |
| [0D](../Foundation/0D_Settings_Architecture.md#execution-report) | 26c8ec6e399f7c206717dd156eb4e23b5a73454b | Central definitions/resolution; immutable desired/applied snapshots; cross-process activation; credentials and invariants are not Settings |
| [0E](../Foundation/0E_Foundation_Architecture_Reconciliation.md#execution-report) | d9d0b995c9f6f1a82a22428b15a2aa9aeab036d7 | Reconciled ownership/extension/downstream boundaries; missing implementation is not a Foundation gap |
| Root AGENTS.md | 714ff3cc2bed24bc246bfd803a0b20d4db1101e4 | Single authorized planning write; explicit lifecycle and scoped guidance |

Read the full original 1B contract once, then targeted ranges. Consumed the 1A Execution Report's invariants, identity, privacy, retention, bounds, contract, transaction, failure and downstream sections. No 1A semantic change is proposed. A genuine conflict must record PHASE_1A_CONFLICT, exact owning decision and downstream effect, stop that thread and request owner review; a Foundation conflict follows its named owner. NONE identified. Settings/Clipboard implementation remains NOT AUTHORIZED.

## Repository Areas Inspected

Environment: WINDOWS_NATIVE host; evidence: FRESH static inspection, not runtime acceptance. Tracked-file searches used git ls-files/git grep, plus explicit source/document paths with rg and bounded reads. Untracked runtime state, live Clipboard, operational DB and customer content were excluded.

| Evidence key | Actual sources / inspected questions |
| --- | --- |
| E-HOST | [F7Hub.ahk](../../../AutoHotkey/F7Hub.ahk), [F7 controller](../../../AutoHotkey/Hotkeys/F7HotkeyController.ahk), [launcher](../../../AutoHotkey/Launchers/F7HubLauncher.ahk), helper inventory; all tracked *.ahk binding declarations, Hotkey calls, clipboard/hook/IPC searches |
| E-GUIDE | Scoped AGENTS and [README](../../../AutoHotkey/Troubleshooting_Sections/README.md) read; GuideHost, GuideRequest, GuideCore HandleGuideKeys/GUI/settings symbols, TopicRouting explicit keys/groups; no live INI read |
| E-APP | [main](../../../Python/f7hub/app/main.py), [bootstrap](../../../Python/f7hub/app/bootstrap.py), __main__, [MainWindow](../../../Python/f7hub/gui/main_window.py), ticket-create shortcut, [ServiceTaskRunner](../../../Python/f7hub/gui/service_task_runner.py); process lifecycle, navigation, pending and GUI-thread boundaries |
| E-IPC | [Mochi channel](../../../Python/f7hub/infrastructure/mochi_channel.py), [protocol](../../../Python/f7hub/domain/mochi_protocol.py), gateway symbols, [local server](../../../Mochi/src/mochi/integrations/local_server.py), app singleton symbols; JSON/framing/queues/deadlines and limitations |
| E-MOCHI | Scoped AGENTS, README, MVP privacy/exclusions and Architecture; tracked source shortcut search; current cosmetic capability versus planned context |
| E-SERVICE | PowerShell scoped guidance and canonical boundary; PowerShellService fixed diagnostic API; TicketService note/association authority, KnowledgeService search API; no copied-command execution or existing Clipboard attach API assumed |
| E-LOG | [logging_config](../../../Python/f7hub/app/logging_config.py), canonical logging owner; safe type-only startup errors, process-local rotating logger |
| E-TEST | Bootstrap/logging/Alt launch test source, F7 launcher native harness source, Mochi protocol/server and test inventory; isolated fixtures, bounded launch, uncertainty and cleanup patterns; tests NOT RUN |
| E-DOC | Root/ROOT/router/Planning/Foundation guidance; Docs05 GUI Clipboard/focus/scaling, Docs06 layers/current integration/security, Docs10 source/runtime and subsystem layout, Docs11 hotkeys/Clipboard/IPC/security, Docs13 bootstrap/workers/Settings/logging; targeted 0A-0E owners |
| E-EXT | Official sources below, consulted 2026-10-07; documented mechanisms, not installed-version or runtime observations |

Only vertical-slice-delivery exists in the inspected project skill inventory. Implementation/integration machinery is not mechanically applied to architecture authoring; scoped planning governs. No sub-agent or independent review was run.

## Verified Current State

| Classification | Finding | Architecture consequence |
| --- | --- | --- |
| FACT | E-HOST: one persistent AHK v2 entry, #SingleInstance Ignore, F7 tap/hold controller and Alt+F7 guide toggle | EXTEND the same host; preserve its drafts, key ownership and timing |
| FACT | E-GUIDE: scoped hotkeys plus native WM_KEYDOWN routing; modifier exclusions protect Win/Alt/Ctrl/Shift input; large resizable guide/editor GUIs | REUSE safe interaction precedents; no reusable small Clipboard HUD base established |
| FACT | E-HOST: launcher validates exact F7Hub title/Qt class/Python executable name, retains PendingPid after timeout, waits at most 15 seconds, focus wait 2 seconds | Useful launch/focus coordination; title/executable name is not authenticated identity or system-wide singleton enforcement |
| FACT | E-APP: every main invocation constructs QApplication and bootstrap; no F7Hub-wide lock/endpoint owner gate found in inspected startup | NEW application singleton before enabling endpoint or launch-on-capture |
| FACT | E-IPC: Mochi uses QLocalServer/QLocalSocket, UserAccessOption, newline-framed v1 JSON, 4096-byte frame cap, bounded queues/deadlines, renderer QLockFile | REUSE design/tests as patterns; unchanged cosmetic wire must not carry Clipboard data or new 0B contracts |
| FACT | E-GUIDE: fixed checkout-specific Windows-message bridge shows/focuses guide only | Keep unchanged; no Clipboard payload over it |
| INFERENCE | Tracked AHK searches found no OnClipboardChange/A_Clipboard/ClipboardAll capture hook, HTTP helper, Named Pipe adapter, shared configurable global hotkey manager or small HUD base | NEW narrowly scoped adapter/helpers justified; absence claim limited to audited tracked source |
| INFERENCE | E-APP plus tracked Python searches found no ClipboardService/IPC ingress, HTTP listener or shared SettingsService implementation | Approved architecture exists; implementation is future, not reusable API |
| FACT | E-APP: QStackedWidget navigation exists for Tickets/Knowledge/Scripts, not Clipboard Center; Settings menu controls Mochi runtime only | EXTEND application navigation later, no invented existing Center |
| FACT | E-LOG: bounded Python standard logging is available; E-TEST supplies fixture/timeout patterns | REUSE without payload/credential logs |
| NOT VERIFIED | Installed applications/custom mappings, active registrations, source permission/elevation, native locks/races/DPI, actual transport performance/packaging | Future native gates; no runtime PASS |

## Responsibility Boundary

| Responsibility | AHK adapter | Python IPC adapter | ClipboardService/domain | Repository / SQLite |
| --- | --- | --- | --- | --- |
| Manual hotkey, Windows interaction | OWN shared host | No | No | No |
| Snapshot/source observation | OWN bounded worker + host | Validate claims | Privacy policy | No |
| Request identity/serialization | Construct immutable request | Validate/bind generation | Own operation semantics | Receipt support |
| Peer authentication/framing/limits | Validate server; producer safeguards | OWN admission/authorization | Authoritative content/privacy limits | No |
| Sensitivity, Kind, Entities, Tags | Minimal credential preflight only | Invoke service | OWN semantic truth | Persist eligible prepared data |
| Deduplication / retention / holds | No | No | OWN policy | Full comparison/atomic integrity |
| Persistence / promotion / pin | No | No direct SQL | Orchestrate approved use case | OWN normal data writes |
| Result projection | Validate/render | Correlate/encode | Truthful disposition/completeness/action availability | Committed receipt outcome |
| Quick HUD | OWN | No | Supply safe projection | No |
| Actions/navigation | Collect intent; local close | Allowlist/route | Owning service revalidates | Owner-approved mutation only |

SQLite does not classify or authorize; PowerShell performs only approved technical operations through its existing boundary. Mochi is optional/advisory through reviewed application context. The adapter does not become a general action, authentication, Settings or domain platform.

## Manual Capture Workflow

1. Technician copies using native application behavior; one fresh capture key press reads CURRENT Clipboard, with no synthesized Ctrl+C.
2. Host captures trigger time and an ephemeral foreground HWND; starts one bounded snapshot worker. No preview or persistent queue.
3. Worker obtains a stable permitted text/plain snapshot, enforces early limits and the narrow producer secret preflight, releases Windows handles, and returns eligible data through a private parent-child pipe.
4. Host freezes text, allowed metadata, capture method, explicit intent, operation_id/message_id and current admission generation. Default history is off; no implicit Save/Attach/Run.
5. Host authenticates the current endpoint before sending any content. Adapter validates strict 0B profile and references; ClipboardService repeats complete authoritative sensitivity assessment before hashing/classification/persistence/exposure.
6. Service returns explicit MEMORY_ONLY or committed PERSISTED/REDACTED_PERSISTED outcome, or safe ERROR. Optional enrichment failures may be PARTIAL; core failure cannot be labeled captured/saved.
7. Host validates correlated result, renders only service-approved summary/actions and releases raw request buffers promptly. Reconciliation retains identities, not a background payload backlog.
8. A new later press is a new operation and genuine occurrence even with unchanged text; a delivery retry retains the same immutable operation and snapshot.

At most one pending capture per host. A fresh press while busy shows Capture in progress without reading another snapshot or queueing it; holding the key is one press, not many captures. A deliberate later press after release/completion is not suppressed by content-based debounce. Clipboard mutations/transforms/copy-and-capture remain separate deferred workflows.

## Clipboard Snapshot Model

RECOMMENDATION: capture the first stable supported snapshot obtained within the bounded read window, not an unverifiable promise of contents at the exact key-down nanosecond. Record observed_at when that snapshot completes. Do not infer that the foreground application originally copied it: foreground context is only context at capture; clipboard owner can differ, exit or represent delayed rendering.

Use a narrowly scoped fixed AHK v2 snapshot-worker mode under the shared host's ownership. It registers no hotkey, creates no HUD/server/database, and exits after one request. The parent starts only reviewed fixed script/interpreter bytes with handle-scoped anonymous pipe inheritance, no shell or payload/token arguments/environment/files. Parent retains the worker process handle/creation identity, enforces a 2-second whole-worker deadline including startup/read/output, terminates only this worker on exhaustion and confirms exit within 1 additional second. Failed cleanup disables further capture until repaired; never kill the shared host or another application. No automatic worker restart after timeout. This is a proposed target, not measured AHK startup performance.

Worker model: bounded OpenClipboard attempts; select CF_UNICODETEXT; GetClipboardData; bound GlobalSize before copying; GlobalLock; validate bounded NUL-terminated UTF-16 text; copy to private memory; GlobalUnlock and CloseClipboard on every path. No SetClipboardData/EmptyClipboard. Enumerate formats sufficiently to distinguish empty versus unsupported; choose available plain Unicode text even if RTF/HTML also exists, without serializing richer formats or treating CF_HDROP filenames as a text capture. Reject invalid surrogate/NUL-in-content or ambiguous malformed storage; the required Windows terminator is not content. No automatic ANSI fallback, line-ending translation, trim, NFC or replacement decoding.

Initial worker allocation ceiling: 128 KiB + 2 bytes for UTF-16 including terminator; authoritative decoded text must still fit 64 KiB strict UTF-8. Large padded allocations are safely refused, even if their visible text might be shorter; do not allocate/copy arbitrary-sized buffers. Host measures complete serialized request <=128 KiB, including escaping and envelope. Python independently enforces both limits. No prefix-only successful capture or arbitrary file-path workaround.

OpenClipboard locks stabilize the read while open. Compare sequence after rendering with sequence after copying while still open, along with owner stability; sample before opening only as a race diagnostic, not an immutable content ID. Delayed rendering may itself change sequence, so do not reject solely because pre-open and post-render numbers differ. A change after successful close does not invalidate the copied snapshot. Unknown/zero sequence, unavailable handle, owner inconsistency or inability to establish a valid stable read yields safe failure. Sequence is ephemeral and never the idempotency key.

External documented FACT: [OpenClipboard](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-openclipboard) can fail when another window holds it. [GetClipboardSequenceNumber](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getclipboardsequencenumber) is window-station scoped and delayed rendering affects when it changes. Microsoft documents a much longer system wait for [delayed rendering](https://devblogs.microsoft.com/oldnewthing/20220609-00/?p=106731); a host timer cannot bound a blocking native call. INFERENCE: worker containment is justified independently of normal lock retries. Exact API/format behavior, kill/handle cleanup and rare race handling remain native implementation tests, not current verification.

| Case | Required outcome |
| --- | --- |
| Empty / whitespace-only | EMPTY_CLIPBOARD local result, no IPC/domain occurrence |
| Unsupported-only formats | UNSUPPORTED_CONTENT_TYPE, no conversion/OCR/files |
| Temporary lock | At most 3 attempts / 2 retries within 300 ms and overall worker deadline |
| Change before stable acquisition | First stable current snapshot; timestamp honestly reflects read time |
| Change during copy / inconsistent owner | Discard candidate; at most one reacquisition within same deadline, then CLIPBOARD_SNAPSHOT_UNSTABLE |
| Blocking delayed render / worker timeout | CLIPBOARD_READ_TIMEOUT; terminate owned worker; no request; visible failure |
| Oversize / invalid Unicode | PAYLOAD_LIMIT_EXCEEDED / CONTRACT_VALIDATION_FAILED; no persistence or echo |
| Clipboard changes after read / during transport | Keep the immutable original snapshot; never reread under old IDs |
| Recognized/suspected secret | Producer blocks before ordinary IPC, generic status only; leave OS Clipboard untouched |
| Metadata unavailable / elevated source | Capture without optional source enrichment; do not elevate or guess origin |

## Hotkey Inventory

Bounded inventory: all tracked AHK files (production and fixture declarations), dynamic Hotkey/OnMessage/OnClipboardChange patterns, launcher/controller/TopicRouting, tracked Python/Mochi shortcut definitions and Config inventory. No separate hotstring/global-binding registry was found in this scope. Imported topics/documented examples are not live global bindings. No installed Startup scripts, third-party remaps, live INI, host registration table or comprehensive installed-app inventory was inspected.

| Binding | Owner / scope / global? | Source | Candidate conflict / native concern / status |
| --- | --- | --- | --- |
| F7 down/up; tap/hold | Shared AHK host, global YES | F7Hub.ahk:16-23; F7HotkeyController | No Win+Alt candidate overlap; owns native F7 behavior intentionally; existing binding FACT |
| Alt+F7 ($!F7) | Shared host/guide, global YES | F7Hub.ahk:28 | No candidate overlap; preserve toggle/editor focus; FACT |
| Ctrl+F, Ctrl+L | Guide-active scope, global NO | F7Hub.ahk:29-34 | No overlap; native search/list elsewhere retained; FACT |
| Ctrl+Page Up/Down, Esc | Guide-active scope, global NO | Same host lines | No overlap; Esc hides guide; FACT |
| Up/Down, Left/Right | Guide notes/list focus, global NO | Host:40-43; GuideCore HandleGuideKeys | No overlap; all modifiers excluded; native editor/other controls preserved; FACT |
| A/S/H/W grouped topic keys | Guide notes/list, unmodified, global NO | TopicRouting ConfiguredShortcutGroups | No overlap; foreground/focus/modifier guards; FACT |
| B/D/G/I/K/L/M/N/O/R/T/U/V/X/Y; 1-5 | Direct topics/interview keys, global NO | TopicRouting BuiltInTopics | No overlap; B/V alone are not Win+Alt+B/V; FACT |
| C/E | Guide create/edit, unmodified, global NO | GuideCore:953-958 | C excluded when Win/Alt held; no candidate conflict; FACT |
| Ctrl+Z/Ctrl+Y, Page Up/Down, wheel, native edit/copy keys | Native controls/guide/editor, global NO | Guide README; native control behavior | Not global replacements; preserve; native behavior NOT VERIFIED this turn |
| QKeySequence.StandardKey.Save (normally Ctrl+S on Windows) | TicketCreateWidget visible-form scope, global NO | ticket_create_widget.py:631 and existing visibility guard | No overlap; platform mapping not registered/tested here; FACT source |
| QKeySequence.StandardKey.Quit | MainWindow QAction, global NO | main_window.py:120 | No overlap; exact native mapping NOT VERIFIED |
| Alt+F7 in guide fixture | Test-only host, global while harness running | Tests/AutoHotkey/fixtures/guide_request_host.ahk:11 | Existing integration-test collision, not a production extra binding; harness NOT RUN |
| Mochi global shortcut | NONE found in tracked source; README says no global hotkeys | E-MOCHI/E-IPC | No repository candidate conflict; installed/custom behavior NOT_VERIFIED |
| Other Ctrl/Shift/Alt/Win global combinations | No other declaration/dynamic registration found in tracked audit | E-HOST tracked-file searches | Bounded negative finding, no universal absence claim |

## Hotkey Recommendation

| Priority / binding | Repository | Windows / known applications | AHK / usability | Recommendation |
| --- | --- | --- | --- | --- |
| 1. Win+Alt+C | NO_KNOWN_CONFLICT in E-HOST/GUIDE/APP/MOCHI | No exact default found in consulted Microsoft Windows list or bounded official technician-application references; NO_KNOWN_CONFLICT, installed/custom mappings NOT_VERIFIED | #!c is expressible in v2; Win/Alt ergonomics, remote forwarding, AltGr/layout and menu masking require native acceptance | FIRST suitable candidate: RECOMMENDED |
| 2. Win+Alt+V | NO_KNOWN_CONFLICT | No exact default found in bounded references; native Win+V is distinct; custom clipboard utilities NOT_VERIFIED | #!v expressible; same native risks | Audited fallback, not selected because C survives |
| 3. Win+Alt+B | NO_KNOWN_CONFLICT | WINDOWS_CONFLICT: documented Windows HDR toggle | Registering an override could suppress display behavior | Unsuitable default; no silent override |

The result is bounded suitability, not a claim every installed application was checked. Native registration success cannot itself prove absence of hooks or application collisions. Later activation fails visibly rather than using a stronger hook to steal an occupied/system binding. Do not automatically fall through from a user-configured binding to another; user priority informs this recommendation, not silent runtime remapping.

Native Ctrl+C remains native, including terminal interrupt/copy semantics. Ctrl+Shift+C has KNOWN_APPLICATION_CONFLICT for Windows Terminal copy and developer/browser workflows; File Explorer version-specific path behavior is NOT_VERIFIED. Ctrl+Alt+C is an older candidate only, with KNOWN_APPLICATION_CONFLICT in Word formatting and possible AltGr layouts; neither is recommended. Official [Windows shortcuts](https://support.microsoft.com/en-us/accessibility/windows/keyboard-shortcuts-in-windows), [Terminal actions](https://learn.microsoft.com/en-us/windows/terminal/customize-settings/actions) and [Word shortcuts](https://support.microsoft.com/en-us/accessibility/word/keyboard-shortcuts-in-word) support this bounded review. Installed custom Teams/Office/browser/RMM mappings are NOT_VERIFIED.

Official [AHK v2 Hotkeys source](https://github.com/AutoHotkey/AutoHotkeyDocs/blob/v2/docs/Hotkeys.htm) documents consecutive # and ! modifiers, extra-modifier/wildcard behavior and Win/Alt menu masking; [Hotkey source](https://github.com/AutoHotkey/AutoHotkeyDocs/blob/v2/docs/lib/Hotkey.htm) supplies runtime failure handling. Recommend ordinary non-wildcard registration, one physical press/release cycle, no Ctrl+C interception, no Send-based selection copying and no blanket hook override. Accessibility includes clickable Open/Close controls and an equivalent application capture route; exact layout/keyboard interaction is validated later. No hotkey registered here.

Settings owns one desired binding for stable action clipboard.capture_current. Host owns OS activation and applied revision. Validate canonical binding/owner scope/repository/system conflicts before persistence; register new binding after commit while keeping old safe binding until success, then unregister old. On failure retain old applied binding and show saved-but-inactive desired state. Lost activation ACK is UNCERTAIN, reconciled by query of applied revision, never blind toggling/restart. One bounded activation attempt per explicit Apply; no DB transaction waits for IPC. Actual binding validator is a purpose-specific extension, not a new universal registry.

## Source Context

Consume 1A D25/source policy: source context OFF by default; optional allowlisted coarse class terminal/browser/editor/unknown only. Foreground observation is not original-copy attribution.

| Metadata | Capture? | Transmit? | Persist? | Log? | HUD? | Mochi? |
| --- | --- | --- | --- | --- | --- | --- |
| Process name | Only optional transient basename to map allowlisted coarse class; no full path/command line | Coarse class only, enabled policy required | Optional coarse class in eligible Event per 1A | No observed basename/class unless justified safe telemetry | Optional approved coarse label | No automatic source feed |
| PID | Runtime only for foreground/process validity; not authoritative source | NO | NO | NO | NO | NO |
| Window title | NO MVP | NO | NO | NO | NO | NO |
| HWND | Host runtime only for positioning/identity checks | NO | NO | NO | NO | NO |
| Browser source URL | NO; DEFER application-specific extraction | NO | NO | NO | NO | NO |
| Capture timestamp | YES snapshot observed_at, unavailable reason if unknown | YES under bounded profile | Eligible accepted occurrence provenance | No unnecessary observed-time detail | Optional relative time | No automatic feed |
| Capture method | AHK_MANUAL | YES closed enum | Accepted occurrence | Safe code only if useful | Manual label optional | Only later safe selected projection |

Minimize metadata before transport; no universal browser retrieval, window text scraping or UIA fallback. A content URL is content subject to sensitivity, not browser-source metadata. Source enrichment failure never blocks an otherwise safe capture. No title hashing substitute. Future title collection would require a newly reviewed purpose and cannot silently override 1A.

## Contract Usage

Use the unchanged 0B seven required fields: contract, schema_version, message_class, message_id, created_at, producer, payload. Responses have their own UUID v4 plus correlation_id equal to request message_id. Names are dotted lower_snake_case, classes uppercase, version canonical string 1.0 for exact initially supported composite profiles. Producer.component is f7hub.ahk; it is validated against authenticated enrollment, never authority by assertion. No top-level operation/message_type/contract_version or arbitrary metadata envelope from historical examples.

| Contract / class | Proposed profile |
| --- | --- |
| clipboard.capture / COMMAND | Explicit manual immutable snapshot, not reprocessing or an EVENT |
| clipboard.result / RESULT | COMPLETED accepted outcome, with truthful memory/durable disposition and completeness |
| clipboard.lookup / QUERY | Recovery lookup of original operation receipt/current source; no capture effects |
| clipboard.lookup_result / RESULT | Known completion, source unavailable, or defined UNKNOWN/IN_PROGRESS observation, not acceptance of a second capture |
| clipboard.action_request / COMMAND; clipboard.action_result / RESULT | Allowlisted explicit UI/use-case intent; no arbitrary execution |
| application.status / QUERY; application.status_result / RESULT | Authenticated minimum readiness/version/applied binding observation only |
| clipboard.bridge_attach / COMMAND; clipboard.bridge_attach_result / RESULT | Content-free enrollment/lease/settings projection after OS bootstrap checks |
| contract.error / ERROR | Pinned 0B safe code/message/optional retryable, bounded known-path violations only |
| clipboard.captured / EVENT | NOT NEEDED for MVP IPC; future eligible committed fact distinct from result |

These are feature profile recommendations requiring review, not implemented/registered contracts. Bootstrap/framing credentials are transport metadata, not a second JSON envelope or ordinary Settings fields.

Required capture payload: operation_id UUID; admission_generation UUID; producer_binding opaque issued ID; observed_at UTC milliseconds or explicitly allowed null plus observation_unavailable_reason; capture_method=AHK_MANUAL; content={format:"text/plain",text:<exact immutable scalar text>}; persistence_intent=POLICY_DEFAULT for MVP; optional allowlisted source_class when enabled. No raw titles, PID/HWND, URL context, arbitrary intent, client-selected Ticket or requested command. Server determines policy from its start-bound 0D snapshot. Enforce exact safety fields; separate future Save/Pin/Attach action. Generation/binding are feature freshness references, not new mandatory global headers.

Required accepted result payload: outcome=COMPLETED; disposition=MEMORY_ONLY/PERSISTED/REDACTED_PERSISTED; duplicate Boolean when resolution occurred; capture_event_created Boolean; replayed Boolean; typed item_ref/event_ref; processing_completeness=COMPLETE/PARTIAL; bounded component issue codes; effective preservation summary. Reference is explicitly durable {kind:"DURABLE",id:<canonical positive signed-64-bit decimal string>} or transient {kind:"TRANSIENT",handle:<opaque owner handle>}; never infer mode from formatting. Replay preserves original Event/refs and original acceptance disposition; current source availability can be queried separately. A later promotion does not rewrite the original MEMORY_ONLY acknowledgement.

Optional primary_kind, sensitivity-safe summary, preview <=240 Unicode scalars from eligible retained content, <=4 action keys, and safe counts. NEEDS_REVIEW/blocked/error has no literal preview. No full content/Entity values/occurrence/history arrays returned to HUD. Whole result/error <=16 KiB. Optional detail exceeding cap is omitted with explicit completeness/detail availability, never truncated JSON.

Admission: <=64 KiB UTF-8 content; <=128 KiB complete capture document; <=16 KiB attach/query/action/result/error documents; nesting <=16, <=128 members/object and <=1024 array entries under 0B, stricter profile counts where declared. Reject duplicate JSON keys, invalid UTF-8/BOM, invalid scalar escapes/NUL, nonfinite numeric values, trailing garbage, unknown closed fields/classes/actions and unsafe references. No enum/number/string guessing. Integer DB IDs are canonical strings; UUIDs/time units/booleans follow 0B.

Initial profiles accept exact 1.0; advertise supported versions on authenticated attach/status. Unsupported major/minor rejects before interpretation; no silent downgrade or assumption any 1.x is compatible. Future optional evolution is compatible only in predeclared extensible observation slots and cannot expand actions/security meaning. Schema/fixture tooling is future implementation; no schema files created here.

## Transport Evaluation

FACT means inspected source or linked official documentation; INFERENCE is engineering comparison; actual latency, registration, packaging and platform behavior remain NOT VERIFIED. No benchmark/server experiment was run.

| Criterion | Localhost HTTP | Named Pipe | Per-call Process | Existing Qt local channel |
| --- | --- | --- | --- | --- |
| AHK simplicity | INFERENCE: WinHttpRequest COM is relatively simple; no tracked helper | INFERENCE: DllCall, handles, overlapped I/O/security need a narrow new adapter | INFERENCE: spawning is simple; handles/deadlines/singleton routing are not | INFERENCE: AHK cannot directly consume Python Qt API; native pipe client needed |
| Python simplicity | INFERENCE: stdlib parsing/server possible; production hardening still new | INFERENCE: standard-library ctypes Win32 adapter; PySide6 already available for dispatch | INFERENCE: easy isolated helper, difficult reuse of running service/context | FACT: existing PySide6 QLocalServer/Socket and Channel |
| Security | Loopback alone insufficient; protected token and authenticated bootstrap needed; peer process binding extra work | Documented ACL, remote rejection and peer PID APIs; still requires enrollment/token, not same-user trust alone | Private inherited handles can bind parent/child; command-line secrets forbidden; helper must not become DB authority | FACT: same-user cosmetic ACL/checkout IDs; 0B explicitly rejects using these as sensitive authentication |
| Message framing | HTTP Content-Length plus strict JSON; cap headers/body, no arbitrary routes/redirects | Explicit bounded length-prefixed UTF-8 frame and authenticated transport metadata | Bounded streams, exact one terminal document; stdout contamination risk | FACT: newline framing, 4096 bytes incl LF, strict v1 shapes |
| Latency | INFERENCE: existing application owner avoids cold Python start | INFERENCE: same; no achieved latency claim | INFERENCE: repeated interpreter/bootstrap cost and process churn; no measured number | INFERENCE: existing persistent connection helpful, only cosmetic state |
| Debugging | INFERENCE: familiar tools; dangerous body/header traces must be disabled | INFERENCE: fixture clients/codes/frame counters; less generic tooling | INFERENCE: easy process fixtures; accidental stdout/payload logging risk | FACT: tests/pure encode/decode/Channel patterns already exist |
| Testing | Portable protocol/server logic; native COM/firewall/end-to-end tests | Portable framing/contract models plus native ACL/peer/I/O/crash tests | Portable mock subprocess; native handles/packaging/lifecycle | Portable pure logic/headless eligible tests; native windows pipe/ACL tests |
| Singleton / lifecycle | NEW F7Hub singleton/readiness ownership needed | Same; first-instance ownership plus mutex, no second resident bridge | NEW singleton handoff needed or duplicate application authority | FACT: renderer singleton only; not F7Hub singleton |
| Timeout / reconnection | Documented WinHTTP phase timeouts plus whole-operation supervisor; reconnect not replay permission | Overlapped I/O/deadlines plus bounded generation reconnect/query | Supervisor owns finite process; result-loss uncertainty remains | FACT: bounded incomplete/command timeout/generation patterns, not durable replay |
| Discovery | Dynamic port descriptor plus secure token delivery; stale endpoint/port reuse risk | Scoped pipe + non-secret runtime descriptor; peer validation and generation fence | Fixed trusted launch path/handles; must still find running owner | FACT: checkout/cache-derived endpoint; identity digest is not secret |
| Windows / firewall | TCP listener; bind 127.0.0.1 only; policy/security products NOT VERIFIED | No TCP listener/firewall rule proposed; reject remote SMB pipe clients; endpoint policy still NOT VERIFIED | No listener; packaging process/security policy still matters | Documented Windows named-pipe implementation; cannot assume strong ACL/exclusive ownership |
| Deployment | Listener/router/header/proxy/browser protections, discovery/token lifecycle; no web framework justified | More native code, fewer HTTP/network policy surfaces; fixed tested Windows wrapper | Helper executable/runtime distribution and repeated startup; owner context/upgrade split | Existing dependency, but new security/raw-handle requirements not met by unchanged Channel |
| Recommendation | Secondary reviewed fallback, disabled by default | PRIMARY RECOMMENDED | Rejected as domain transport | REUSE patterns, not endpoint/wire or raw-content trust |

Documented FACT: [WinHTTP SetTimeouts](https://learn.microsoft.com/en-us/windows/win32/winhttp/iwinhttprequest-settimeouts) exposes separate phase controls; these do not replace a whole-call budget. [QLocalServer](https://doc.qt.io/qt-6/qlocalserver.html) supplies platform local sockets but same-user options are not process authentication. Repository Mochi code is not a safe drop-in sensitive bridge.

## Transport Recommendation

Primary: application-owned authenticated local Windows Named Pipes with a narrow AHK v2 client and Python Win32 infrastructure adapter. Reason: sensitive untrusted local ingress needs peer/process identity, per-logon access and explicit endpoint ownership; native pipe facilities offer these controls without a TCP/web surface. Existing Mochi code gives useful bounded-channel precedents, not approved reuse of its cosmetic endpoint/schema.

Secondary fallback: localhost HTTP only after separately reviewed equivalent bootstrap/token/producer binding and native evidence. It is not an automatic fallback after pipe authentication failure. If later evidence shows the native adapter burden disproportionate, review this fallback rather than silently switching. No new web framework/dependency is selected.

HTTP fallback design constraints: app binds 127.0.0.1 with OS-assigned port 0 after acquiring singleton; non-secret bounded descriptor records port/PID/creation/generation. Runtime credential stays in memory through authenticated owned-process handoff, never in descriptor/Settings/argv/URL. Allow only exact POST bridge route carrying allowlisted 0B profiles; authenticate before accepting body, cap headers 8 KiB/body 128 KiB/response 16 KiB, reject transfer-encoding ambiguity, redirects, unexpected Host/Origin/browser cookies/CORS and content types. Client uses numeric loopback, direct/no-proxy mode and explicit phase/whole-call deadlines. Same limits/rates/replay fences apply. No LAN/0.0.0.0/IPv6 broad listener, firewall exception, URL reservation, unauthenticated health route or arbitrary shell endpoint. Installed firewall/EDR behavior is NOT VERIFIED.

Rejected: per-capture Python domain helper (repeated bootstrap, unsafe duplicate authority, transient/receipt/context discontinuity); broad WM_COPYDATA/general Windows-message payloads (existing guide profile is fixed show/focus); file spool (raw data lifetime/stale replay/secret leakage); raw Mochi channel/endpoint (different security/data/size/class semantics); machine service/resident daemon (unjustified lifecycle/authority). The snapshot worker has a different, necessary purpose: supervised isolation of a native read that cannot be reliably interrupted in the shared host. It never calls ClipboardService or writes SQLite.

Deployment: use approved configured install/runtime paths, not permanent C:/Dev/F7Hub. Need trusted AHK runtime + fixed worker mode, Python Win32 API wrapper, singleton/bootstrap enrollment and protected runtime-directory creation. No installer/source/dependency changes here. ctypes/no new package is a RECOMMENDATION; native ABI/handle correctness must be reviewed/tested before delivery.

## Endpoint Lifecycle

Endpoint belongs to the running F7Hub modular-monolith process; no separate bridge/service. Acquire a per-installation, per-logon/session application singleton before DB bootstrap or endpoint creation. Second invocation performs a bounded content-free owner status/focus handoff and exits; it does not bootstrap a second database/service stack. Mutex ownership is coordination, not peer authentication; don't delete/steal live locks or kill competing processes. Endpoint conflict fails capture availability while unrelated local app work remains usable.

After service readiness, create pipe with explicit security, establish bootstrap enrollment, then publish discovery. App process exists, window visible, endpoint listening, authenticated ready and capture accepted are distinct. Hiding/minimizing an existing main window can leave its app-owned endpoint alive; closing the app stops admission, resolves admitted work truthfully, removes only its matching discovery generation, closes handles and clears tokens. No new tray/close-to-background behavior.

I/O/framing runs through overlapped native I/O in a bounded application-owned infrastructure worker, not blocking Qt or shared AHK GUI callbacks. Service work remains outside GUI thread, marshalled completion/navigation on Qt GUI thread. REUSE finite worker conventions; do not put persistent listener lifetime into ServiceTaskRunner or block its existing ticket workflows. At most one active capture and two pending read-only queries globally for MVP; overload returns safe BUSY before mutation.

## Endpoint Discovery

Proposed pipe spelling: \\.\pipe\F7Hub.Clipboard.<install_digest>.<logon_digest>.<session_id>.<runtime_uuid>, <=256 UTF-16 code units. Digests namespace distinct installations/logons; they are non-secret routing labels, not authentication. Exact install namespace is derived by approved path configuration, never arbitrary caller root. Each runtime has a fresh cryptographic random UUID.

One non-secret discovery descriptor in the approved per-user runtime root (conceptually LOCALAPPDATA/F7Hub/Runtime/Clipboard/<installation>/<logon-session>/endpoint.json), maximum 4 KiB. Fixed schema: discovery_version, pipe_name, server_pid, process_creation_time, runtime_generation, supported_contract_versions; no content, user title/path dump, token or bearer reference. Python is sole writer; do not create another Settings authority.

Validate location/containment, parent and file ownership/DACL, no permissive inheritance/reparse escape, complete size/schema and expected namespace. Writer creates a protected same-directory temporary file, flushes/closes and atomically replaces its owned descriptor, never follows an arbitrary requested path. Native replace/sharing/security correctness remains unverified. Descriptor is a hint; authenticated live pipe and retained process identity determine readiness.

Stale/missing/invalid descriptor: one reread after an observed application startup/generation change within the readiness budget; otherwise unavailable. AHK does not delete/repair it. On app exit, writer removes only descriptor matching its own generation; a new app publishes a new generation. PID reuse is rejected using process handle/creation identity, not PID alone. No infinite port/pipe scanning.

## Security Architecture

Security invariants: no command endpoint, AHK DB access, hard-coded secret, broad network binding, unbounded payload/retry, raw Clipboard logging or automatic PowerShell execution. Each is satisfied by the recommended boundaries; this is a design assessment, not deployed security certification.

Pipe: explicit logon-SID DACL, deny anonymous/Everyone/network and unintended logons; local-only PIPE_REJECT_REMOTE_CLIENTS; first owner uses FILE_FLAG_FIRST_PIPE_INSTANCE and retains its ownership handle; bounded instances, not PIPE_UNLIMITED_INSTANCES. Client permission grants only necessary individual read/write/synchronize rights, not blanket FILE_GENERIC_WRITE/create-instance permission. Secure noninherited handles and correct medium-integrity/logon checks are part of the native wrapper.

External documented FACT: [Named Pipe Security](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-security-and-access-rights) explains default ACL exposure, logon SID isolation and the generic-write/create-instance overlap. [CreateNamedPipeW](https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-createnamedpipew) documents first-instance, overlapped I/O and remote-client rejection controls. The controls need deliberate implementation; a default pipe or UserAccessOption is insufficient.

Wire framing: 4-byte unsigned network-order JSON length, 8-byte transport sequence, 32-byte HMAC-SHA256 over direction/runtime/connection generation/sequence/length/exact UTF-8 document, then exactly that document. Fixed 44-byte framing allowance separate from the <=128-KiB document cap. Reject declared length before allocation; partial header/body deadline 1 second; per-connection buffer <=128 KiB+44; output <=16 KiB+44. Reject sequence reuse/out-of-order/auth failure before parsing. One logical request per connection at a time; close invalid/trailing frames, no raw dumps. Crypto framing is transport integrity/authentication, not a new JSON grammar.

Maximum 4 established connections, 2 concurrent bootstrap attempts, 2 queued read-only queries, one capture in flight. Proposed admitted-command limit 10 per second per binding (burst 10), global 20 per second; excess visibly BUSY, never silently drops accepted occurrences or queues indefinitely. Unauthenticated attempts bounded before JSON/body admission. These are proposed limits requiring load tests; no claim to stop all local denial of service. Auth/size/shape/privacy gates are independent, not permissive alternatives.

Authenticate and bind sender before body -> validate 0B/composite size/shape/version -> validate operation/source/context -> complete service sensitivity -> execute approved use case -> safe outcome. Copied commands, URLs, titles and action parameters never become shell construction, interpreter code or delegated permissions. No browser auto-open/file access. Developer mocks isolated to explicit fixture namespaces; no production raw payload debugging exception.

## Threat Model

| Threat | Trust/control | Residual / rejection |
| --- | --- | --- |
| Unrelated malicious local process | Logon ACL plus enrolled OS peer identity and per-runtime token/MAC; no content before server proof | Same-account code injection/token theft/admin compromise cannot be made impossible by IPC; fail on unverified identity |
| Fake/squatted endpoint | First-instance ownership, independent process pin, token challenge; descriptor never establishes trust | Denial possible; no deletion/unauthenticated downgrade |
| Crafted Clipboard / forged source | Strict format/size/scalars; producer preflight + complete service privacy; source is untrusted enrichment | Detectors imperfect; no literal logs/default sharing |
| Oversized/slow input | Length-before-allocation, partial deadline, connection/queue/rate ceilings | Local resource interference still possible |
| Replay / duplicate / changed operation | Authenticated frame sequence, admission generation/lease, exact semantic comparison and atomic receipt | Old generations rejected; uncertain completion reconciled |
| Action injection/stale refs | Closed action keys, typed refs/revision, current owner policy/context and explicit intent | Missing source/owner capability makes action unavailable |
| Token leak / stale token | Memory-only bootstrap, no argv/env/descriptor/log/Settings, fresh generation on app/host change | No physical memory/paging/dump erasure guarantee |
| Version skew/malformed result | Exact supported composite version, strict correlated safe result | Fail clearly, advise update/restart; no guess/downgrade |
| Cross-user/session/elevation | Logon/session + token integrity checks; ordinary unelevated pair | Elevation/UIPI behavior NOT VERIFIED; refuse mixed-integrity IPC |
| Screen sharing/HUD | Generic/concealed previews, no raw title/secret, user hide/status mode | Screen recording outside app control; even safe snippets may identify work |

Same-user access is not strong producer authentication. Trusted-code/install integrity plus explicit live process enrollment is the chosen additional boundary. It is not a sandbox against arbitrary code already executing inside enrolled processes or an administrator. If deployment requires that stronger adversary isolation, stop activation and seek security-owner review rather than pretending a token or path hash supplies it.

## Authentication

Per-runtime CSPRNG 256-bit token, scoped to the enrolled producer process handle/creation identity, user logon SID, Windows session, approved medium integrity, install identity and ingress generation. Separate connection nonces and transport sequence/MAC bind replies as well as requests. Wrong/missing/stale proof yields AUTHORIZATION_DENIED under 0B (local IPC_AUTH_FAILED observation if no valid remote response); never unauthenticated fallback. Unknown peer receives safe close, no reflected bytes.

Bootstrap is content-free and tied to an actual trusted owned launch, not claimant-supplied PID/path. Two supported future paths: (a) F7Hub launches/enrolls the one shared AHK host through its approved launcher and retains process handles; (b) that reviewed shared host launches F7Hub, retaining child handle and explicit inherited bootstrap channel, with Python verifying the actual direct parent/launch context. Token is exchanged through private inherited anonymous handles only after reciprocal process checks, not through public descriptor, arguments or broadly inherited environment. Exact inheritance allowlist, fixed script/includes integrity and cancellation/cleanup require a dedicated native security slice.

Use [GetNamedPipeClientProcessId](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-getnamedpipeclientprocessid) and [GetNamedPipeServerProcessId](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-getnamedpipeserverprocessid) from connected handles, then retained process handles/creation/token/session identity. Executable name, window title, checkout digest, claimed script path and producer.component alone cannot authenticate a process. General interpreters do not attest script identity; deployment/bootstrap must verify the fixed loaded-code launch path under the stated trusted-code assumption. No impersonation/elevation of clients.

An already running legacy host without authenticated launch/enrollment is not silently trusted or terminated. Capture remains unavailable; explicit application/host enrollment recovery must preserve guide/editor drafts, and may require the technician to close/restart that host after preserving work. This is an implementation activation prerequisite, not permission to restart it in this task. No persistent enrollment secret or unrestricted registration endpoint.

Compare options: hard-coded/install-long-lived secret REJECTED; normal INI/JSON/SQLite Settings secret REJECTED; ACL-protected runtime token file alone REJECTED as sensitive producer authentication because same-logon readers may obtain it; inherited environment less restrictive than handle handoff and NOT NEEDED; narrow owned-process inherited handles + OS peer pin + rotating runtime token RECOMMENDED. No external credential provider/broker selected.

Host or app restart revokes token/binding/admission generation; pending operations recover only by authenticated receipt query. Missing OS identity/security metadata fails closed; no broad compatibility exception. Multiple users/logons have distinct descriptor/pipe/lock scopes; mixed elevated/non-elevated pair refuses capture without auto-elevation. Reading already-present Clipboard text from an elevated source may work without interaction, but source metadata/focus/UIPI is NOT VERIFIED and safely omitted.

## Idempotency & Replay

Consume 1A's three identities unchanged: Item content equality, genuine Capture Event occurrence, and producer/generation-bound operation_id plus logical message_id. The capture command initially maps one operation to one logical communication; neither content hash nor Windows sequence substitutes for it.

| Situation | Required behavior |
| --- | --- |
| Identical request retransmitted while admitted | Same immutable text/source/intent/profile/IDs; return original outcome/refs with replayed=true; no new Event, count, last-seen or expiry update |
| Same IDs but different validated semantic request | CLIPBOARD_OPERATION_CONFLICT, no effects; a fingerprint is only an accelerator, full eligible source/metadata comparison required |
| Fresh later hotkey press, same eligible content | New operation/message/Event; service may reuse existing exact Item; duplicate=true is valid capture success |
| Lost reply after durable commit | Atomic receipt proves original Event/outcome; authenticated lookup, never invent failure/rollback/new capture |
| In-flight concurrent duplicate | One operation reservation; BUSY/in-progress observation or prior terminal result; never two transactions creating Events |
| Restart / lease expiry / evicted comparison data | Old admission generation cannot accept new effects; lookup receipt only; source unavailable/unknown is truthful, not permission to replay |
| Deleted Item / expired transient source | Safe known-completed/source-unavailable receipt observation; cannot reconstruct from preview/hash |
| Explicit Save/Pin/Attach of transient source | New preservation action identity, promote selected occurrence at most once under 1A; not another capture |

Admission generation issued only after authentication; maximum new-operation admission lease 5 minutes, measured by service monotonic deadline. Producer timestamps are not freshness proof. Every operation is bound to issued producer_binding and generation; changed parent/child/connection enrollment requires new binding. Initial memory replay budget: 512 safe outcomes/reservations or 4 MiB metadata per binding, whichever first; no raw secret rejection value/fingerprint retained. Saturation closes new admission and rotates/fences generation before evicting any admissible operation knowledge. Existing in-flight reservations remain until their bounded final state/reconciliation; no eviction that could readmit the same operation.

Durable acceptance includes operation receipt atomically with Event/core, as 1A requires. Retain proposed 14-day receipt/Event horizon under 1A ceilings; physical schema/CAS is a future reviewed persistence slice, not a new generic replay database. Known-committed result can survive source deletion with safe receipt IDs/outcome but source/fingerprint removed. If exact comparison material is gone, refuse capture redispatch. Memory-only results/reservations expire with bounded transient store/session; restart does not recover lost transient content or certify that it was never accepted.

After app restart, old generation is absent/retired and mutation is rejected even if receipt has expired. Newly authenticated lookup may reference original operation/generation under same authorized data scope; response can report known completion, unavailable source or UNKNOWN. UNKNOWN after dispatch is UNCERTAIN for the caller; never automatically issue a fresh capture. A technician may choose a genuinely new capture with visible warning that earlier outcome remains unconfirmed. This is new intent, not recovery labeled exactly-once success.

Lookup is a new QUERY/message_id referencing the original operation; response correlation matches the lookup. Retransmission uses same original capture message/operation IDs, while connection frame sequence/MAC changes on a new authenticated connection. Byte framing is not semantic identity. No unbounded poll, permanent retired-generation registry, secret fingerprint or raw wire receipt.

## Retry & Timeout Model

Targets are RECOMMENDATION and NOT VERIFIED measurements. Each operation has an independent budget plus an outer deadline; no timer silently restarts that deadline. Initial cold/large/unhealthy behavior fails visibly rather than widening bounds.

| Operation / triggering failure | Max attempts / retries | Max elapsed | Required state before retry | Exhaustion / terminal result |
| --- | --- | --- | --- | --- |
| OpenClipboard transient lock | 3 / 2 | 300 ms within worker 2 s | Lock attempt released, finite 50/100 ms delay, deadline remains | CLIPBOARD_LOCKED |
| Inconsistent native read | 2 acquisitions / 1 | Same worker 2 s | Close/unlock/discard invalid snapshot; new stable acquisition | CLIPBOARD_SNAPSHOT_UNSTABLE |
| Snapshot worker startup/block/output | 1 / 0 automatic | 2 s plus 1 s owned cleanup confirmation | Explicit later user capture after confirmed cleanup; timeout disables until recovery if cleanup uncertain | CLIPBOARD_READ_TIMEOUT / cleanup BLOCKED |
| Pipe connection before dispatch | 2 / 1 | 500 ms total | Observed fresh descriptor/readiness generation or cleared transient busy condition | IPC_UNAVAILABLE, no domain effect |
| Bootstrap/auth attach | 1 / 0 | 1 s | Explicit valid re-enrollment after cause/version repair | IPC_AUTH_FAILED/AUTHORIZATION_DENIED; no content |
| Capture processing + reply | 1 send initially | 3 s; standard overall capture target <=6 s incl snapshot/connect | No blind automatic resend after any dispatch uncertainty | Local UNCERTAIN; lookup only |
| Capture delivery retry with proof no admission | At most 1 additional send | Same 3-s request/6-s outer budget | Authoritative no-admission rejection or verified no bytes dispatched; still-live same lease/binding and immutable snapshot | Unavailable/ERROR; never new IDs |
| Receipt reconciliation / lost reply | 2 QUERY attempts / 1 | 2 s total, starts after original timeout; one outer capture+reconciliation <=8 s | Authenticated endpoint ready or authoritative generation transition; no periodic background poll | UNCONFIRMED/UNCERTAIN, recover in app |
| Explicit Open F7Hub or opt-in auto-launch | 1 launch / 0 relaunch | 15 s readiness total, <=30 spaced status probes | Owned child or existing singleton starting; each probe after >=500 ms and not-ready observation | F7Hub unavailable; keep pending launch handle to avoid duplicate |
| Fresh descriptor reread | 2 reads / 1 | Within 500-ms connect or 15-s launch budget | Observed app startup or generation change | Unavailable; client never deletes descriptor |
| User HUD navigation/action | 1 send / 0 automatic mutation retry | 2 s acknowledgement | Explicit current intent/revision; dispatched uncertainty reconciled, not replayed | Action unconfirmed; capture remains acknowledged |
| Settings binding activation | 1 / 0 per Apply | 2 s ACK | Explicit Apply/repair, validated desired revision, registration outcome known | Failed/uncertain applied state, retain safe old binding |
| Partial frame / idle connection | 1 read sequence / 0 restart | 1 s incomplete; 30 s idle close | Explicit fresh authenticated interaction later | Close handles; no auto-reconnect |
| HUD display | One timer / no loop | 5 s default; user preference 3-15 s; interaction pauses display timer | Explicit user focus/hover may pause; does not extend RPC budgets | Close presentation; no mutation/cancellation claim |

Counts share outer deadlines: lock/reacquisition never imply six fresh 2-second workers. OpenClipboard total attempts capped at three across acquisitions. Readiness probes are content-free and begin only after explicit launch, not resident polling. No retry for validation, unsupported version/format, authorization, privacy or operation conflict. A service-declared retryable error is advice; it does not establish safe replay or a repaired cause. Deterministic pipeline/database failures require diagnosis/repair plus still-admissible same-operation recovery, not automatic looping.

Synchronous domain request/terminal result is sufficient for bounded MVP text; native I/O and service dispatch are asynchronous to the GUI event loops. No new ACCEPTED/PROCESSING global result or queued long-running capture protocol. A transient local PROCESSING indicator is presentation only; accepted transport delivery is not completion. If owner work outlives the observation timeout, it may still commit and be reconciled. No Cancel button promising rollback; closing HUD dismisses UI only. Shutdown must drain or establish owner-confirmed pre-commit abort under bounded cleanup, with commit uncertainty retained.

## F7Hub Availability

| Observed state | Behavior |
| --- | --- |
| Authenticated endpoint ready, GUI visible | Normal manual capture; no focus change merely for capture |
| GUI hidden/minimized, same live owner ready | Normal capture, user action may show/focus through existing shell; no new resident mode |
| Not running / endpoint absent | Generic unavailable HUD; release unsent raw snapshot; offer Open F7Hub and a new manual capture once ready |
| Process starting / window visible but services not ready | Bounded content-free readiness, no guessed endpoint/acceptance |
| Endpoint unhealthy / conflicting owner | Capture unavailable, preserve other local work, no takeover/extra process |
| Version mismatch | Safe error/update/restart guidance, no fallback profile |
| Authentication failure / legacy unenrolled host | No content dispatch; explicit enrollment recovery, no elevation/unauthenticated mode |
| App exits after dispatch | Caller UNCERTAIN; new authenticated owner may query safe receipt, not resend capture |
| Worker/host restart | Pending host state may be lost; no durable AHK backlog; eligible durable Items remain Python-owned |

Default auto-launch=false; explicit Open F7Hub is enough for MVP. REUSE launcher intent and PendingPid behavior but EXTEND singleton/enrollment/readiness proof before this feature activates. Current title-based launcher is not that proof. Neither unavailable HUD nor Open F7Hub claims original capture saved.

Optional later auto-launch setting=true: one explicit manual press triggers one coalesced approved launch; retain exactly the same eligible snapshot for at most the 15-second readiness budget; at ready authenticate and send once with newly issued binding/generation but original capture operation/message identity. If no dispatch has occurred, acquiring initial admission does not change its content/intent. Total cold workflow <=20 seconds plus 1-second cleanup target; expiry releases snapshot and requires fresh capture. If generation changes after dispatch, lookup only; never relabel/rebind and resend. Default-off policy avoids unexpected starts; native bootstrap/race tests are activation prerequisites.

## Quick HUD

AHK acknowledgement/action surface only: one active HUD, primary status/storage mode, optional safe preview and at most four owner-offered actions. No Item history, raw inspector, domain editor, ticket workspace, diagnostic workspace or Mochi conversation. MEMORY_ONLY visibly says Not saved; duplicate content is success, whereas transport replay is the same prior capture. Don't manufacture seen-count information from AHK cache.

Default preview is generic/type-only to reduce screen-share exposure; allow bounded literal preview only if Python marks it privacy-eligible and an explicit HUD preference permits it. Maximum 240 Unicode scalars, plain escaped text, controls/bidi presentation made safe, truncation visibly marked. No raw request fallback; blocked/error/unconfirmed displays none. No source window title. Python's disposition/completeness drives UX; AHK does not reclassify content or infer save/duplicate state.

Recommend non-activating display, conservative high-contrast appearance, restrained topmost lifetime, monitor work-area clamping using source HWND/mouse monitor with primary fallback. No borrowing the guide's user opacity as Clipboard preference. Existing guide GUI/focus patterns can be reused, not its settings truth or large editor layout. Exact geometry/icons/animations DESIGN NEXT.

Mouse actions clickable. Keyboard interaction begins only when the technician deliberately focuses HUD (click or standard window navigation); Tab/arrows move action focus, Enter/Space invoke selected enabled action, Esc closes in HUD scope. Capture hotkey does not steal typing focus; global Escape/Enter are never captured just because HUD is visible. No mandatory new global open_hud binding. Closing nonactivated HUD leaves source focus alone; don't forcibly restore stale HWND or steal newer intentional focus. User-requested Open Center may intentionally focus app; Windows denial yields visible taskbar fallback rather than repeated WinActivate.

Display timer pauses while hovered/focused or an action dialog is active; RPC/work deadlines remain finite. Default dismiss 5 seconds; errors with user interaction remain accessible, and app status carries recoverable diagnostics. Bound raw/transient context lifetime under 1A even if HUD stays open: expired ref disables source actions, leaving generic status/Open Center. On session lock/switch or policy escalation clear previews/HUD and revoke access. No synthetic captures/screenshots for this planning task.

## HUD State Matrix

Presentation vocabulary is separate from 0B/domain outcomes. SUCCESS/DUPLICATE/PARTIAL require authoritative COMPLETED result, never mere HTTP/pipe delivery.

| State | Title / storage truth | Preview | Offered actions | Auto-dismiss / focus |
| --- | --- | --- | --- | --- |
| CAPTURING / PROCESSING | Capturing / Processing; no saved claim | NONE | Close only; no fake Cancel | Delay processing indicator ~150 ms target; nonactivating; bounded operation |
| SUCCESS | Captured - Not saved, or Captured - Saved from disposition | Generic default; <=240 scalars only eligible opt-in | Open Center; eligible Pin; additional owner offers <=4 | 5 s default, pause interaction; no focus steal |
| DUPLICATE | Captured again - Already known; current storage mode | Same safe policy | Same owner-validated actions | Same; genuine new Event distinct from replay |
| PARTIAL | Captured - Some processing unavailable; explicit storage mode | Eligible approved summary only | Open Center; only actions whose prerequisites completed | Same, safe component issue summary |
| BLOCKED | Sensitive content blocked / Unsupported text / Too large | NONE | Close; Open F7Hub if useful; no persist-anyway | Generic accessible status; no activation/secret echo |
| ERROR | Capture failed / F7Hub unavailable / Capture unconfirmed | NONE | Open F7Hub or recovery read; no automatic retry mutation | No forced focus; timer pauses on interaction; unconfirmed never labeled cancelled |

Replay may render the original success state with Already acknowledged rather than Captured again; duplicate Boolean and replayed Boolean represent different facts. Invalid correlation/schema/MAC yields local ERROR with no remote result claimed.

## Action Routing

All keys below are proposed allowlisted profiles, not currently implemented capabilities. Server recomputes eligible actions from current Item/source/policy/owner state at invocation; a button is not authorization. HUD sends typed ref, expected revision where needed and explicit action intent, never arbitrary text/command/URL reconstructed from preview. At most one pending action; post-capture action failure cannot undo acknowledged capture.

| Action / key | Route / required context | Owning boundary | Security / sync-async / availability |
| --- | --- | --- | --- |
| Close / clipboard.close_hud | LOCAL_UI; current HUD only | AHK | No domain effect; immediate; always |
| Open F7Hub | LOCAL_UI convenience, fixed approved launcher | AHK launcher + Python singleton | No capture payload argv; bounded async startup/focus; only explicit intent/default-off auto-launch policy |
| Open Clipboard Center / clipboard.open_center | Python-routed navigation with typed Item/ref optional | Application navigation -> future Clipboard presentation | Validate source and preserve Ticket/editor drafts; async GUI-thread navigate/2-s ACK; unavailable until 1C component exists |
| Pin / clipboard.pin_selected | APPLICATION_COMMAND; eligible current durable/transient ref and revision | ClipboardService/repository | 1A Pin implies Save; promotion once, audit/eligibility needed; bounded service work/terminal action result; absent/expired/sensitive source unavailable |
| Attach to Ticket / clipboard.attach_to_ticket | APPLICATION_COMMAND; source + explicit validated Ticket ref/revision | Owning Ticket/Clipboard association use case | Python binds technician-selected target; content cannot select it; accepted evidence hold; no direct AHK mutation; async draft/confirmation then separate transaction; current API NOT IMPLEMENTED |
| Search KB / kb.search | APPLICATION_COMMAND to read/navigation; eligible result ref/entity selection | KnowledgeService + application navigation | Python resolves safe bounded search text, no raw HUD reconstruction; async read; current Knowledge search reusable, new routing/privacy integration future |
| Run Diagnostic / diagnostic.open_request | DIAGNOSTIC_COMMAND planning/confirmation route; approved diagnostic key/context only | Diagnostic ownership via existing PowerShellService -> PowerShellGateway | Open approved run UI/revalidate explicit run intent; never execute copied command; current parameterless registered diagnostics do not support Clipboard target inputs; input-derived run unavailable, separately reviewed future |
| Ask Mochi / mochi.ask | APPLICATION_COMMAND opening optional advisory flow; safe selected context ref | Application context/Clipboard projection -> MochiService future adapter | No raw history/secret or prompt built by AHK; provider preview + explicit Send separately required; async optional; current cosmetic v1 cannot carry it, unavailable MVP |

No inferred active Ticket from Clipboard text. A source ref is revalidated through owner and never a bearer permission. Unknown/offered-but-now-stale actions return classified error/unavailable; update buttons safely without retargeting current draft. Action COMMANDs get new message/operation IDs; uncertain mutations are queried, not blindly retried. Long diagnostics/provider calls belong to their existing approved lifecycle after interactive acknowledgement, not an unbounded HUD RPC.

## Privacy

Two gates: narrow AHK producer preflight blocks recognizable credentials/authentication-context suspicion before ordinary transport; ClipboardService repeats full authoritative assessment. AHK preflight uses reviewed bounded credential indicators from the Clipboard owner (API/Bearer/private-key/password/MFA-context examples), no Kind/Entity/Tag/retention truth or general duplicate classification engine. If preflight is missing, version-incompatible, fails or cannot complete under bound, do not send. Literal detector values never enter responses/logs; no user disable or send-secret override. False negatives remain a residual explicitly carried from 1A; neither detector nor local authentication certifies content safe.

Snapshot worker filters before private output; eligible text travels only private parent-child handles and authenticated application pipe. Raw buffers promptly released after send/completion/deadline; no AHK disk history/spool/clipboard reset. Physical zeroization, paging/dump/OS clipboard erase is not promised. Tightly bounded transient content and complete authoritative gate precede hash/dedup/persistence/derived exposure.

| Content | AHK display? | Transmit? | Python persist? | HUD preview? | Log? |
| --- | --- | --- | --- | --- | --- |
| Ordinary text | No raw pre-result display | Eligible manual snapshot after preflight/auth | Default MEMORY_ONLY; explicit eligible Save or enabled history per 1A | Generic default, bounded eligible opt-in | IDs/code/size class only; no text/preview/hash |
| Email | No raw pre-result display | Bounded explicit manual non-secret; service assessment | NEEDS_REVIEW memory-only; reviewed purpose/intent required for durable use | Concealed/type-only by default | No address/Entity value |
| Window title with customer name | Not collected | NO | NO | NONE | NONE |
| Password-like text | Generic blocked | NO when recognized/suspected; false negatives not ruled out | BLOCKED; no raw/hash/Event/quarantine | NONE | Generic content-free code only |
| API key / bearer / private key | Generic blocked | Same producer block | BLOCKED, no ordinary storage or onward context | NONE | No token/fingerprint |
| MFA / recovery code | Generic blocked on auth suspicion; numeric ambiguity acknowledged | NO when suspected; no universal numeric-secret claim | BLOCKED when suspected; mandatory assessment | NONE | No code/span/context |
| Large log | No raw preview | Only within both caps and complete preflight; oversize NO | Eligible rules; customer-sensitive MEMORY_ONLY/review; no silent truncation | Type/size only by default | Coarse size/code only |
| URL content | No raw pre-result display | Non-secret inline eligible; signed/credential-bearing blocked when recognized | Privacy/purpose-gated per 1A | Generic; strip risky query/userinfo only in independently assessed projection, not mutate Item | No URL/title/path |
| Known secret sanitized by user | No original retained or echoed | Separately submitted sanitized new snapshot only | Re-assess new identity/derivative under 1A | Eligible derivative only | No original hash/value |

No automatic Analytics/Mochi/external feed. Enablement flags do not constitute disclosure consent. Saving/pinning/evidence preserves only eligible content; source values never grant execution. Sensitive persistence/audit/association activation waits until the required owner implementation exists. Employer/customer policy and external provider data terms remain NOT VERIFIED.

## Settings Inputs

0D central service/definitions own allowed durable USER preferences and effective source-aware resolution. Clipboard contributes pure key definitions; adapter consumes a bounded authenticated immutable projection at attach/status and start of operation. No AHK DB read/write, new INI truth or independent default authority. Existing guide-local preferences remain local and unchanged.

| Input / proposed key | Class | Proposed default/bounds | Update / owner |
| --- | --- | --- | --- |
| Capture binding / clipboard.capture_hotkey | CORE | Win+Alt+C recommendation; canonical validated modifier/key value, not arbitrary AHK expression | Desired/applied revision ACK after explicit Apply; Settings+host |
| Capture enabled / clipboard.manual_capture_enabled | CORE | Disabled until authenticated implementation ready; explicit feature activation | Next operation; registration truth separate; no sensitivity bypass |
| HUD enabled / clipboard.hud_enabled | CORE | true when feature activated; disabling previews does not suppress mandatory safe failure/status feedback | Next presentation; AHK consumer |
| HUD duration / clipboard.hud_duration_ms | LIKELY | 5000 proposed, 3000-15000 validated | Next HUD; no RPC deadline extension |
| HUD position / clipboard.hud_position_strategy | LIKELY | source_monitor_corner, safe work-area clamp | Next HUD; geometry DESIGN NEXT |
| Literal preview / clipboard.hud_preview_enabled | LIKELY | false; service eligibility independently required | Next HUD; privacy-sensitive bad value disables preview |
| Auto-launch / clipboard.auto_launch_f7hub | LIKELY | false; opt-in only after singleton/bootstrap implementation | Next operation; one launch/no relaunch |
| Transport timeout / clipboard.request_timeout_ms | LIKELY | 3000; preference may lower within admitted 1000-3000 range, never raise safety ceiling | Next operation immutable snapshot; timing owner |
| Source context / clipboard.source_context_enabled | LIKELY | false; only allowlisted coarse class | Next capture; bad sensitive value excludes enrichment |
| Automatic capture / clipboard.auto_capture_enabled | FUTURE | false, no consumer/hook in MVP | Separate future privacy/rate/retention review |
| Open HUD / open Center / pin selected global bindings | NOT NEEDED MVP | No extra global hotkeys; local buttons/app routing sufficient | Revisit only demonstrated use case |
| History/persistence/retention/action/privacy inputs | CORE dependency on approved 1A | Off-default persistence; 1A lifecycle/holds/caps unchanged | ClipboardService start-bound 0D snapshot, not AHK authority |
| Pipe name, runtime token, generation, enrollment, process handle, discovery path | NOT NEEDED as user Settings | Runtime infrastructure/credentials, no ordinary stored preference | Bootstrap/infrastructure owner |
| Payload/connection/rate/security ceilings / detector bypass | NOT NEEDED as editable Settings | Enforced invariants; no permissive toggle | Security/contract owner |

If shared Settings is not implemented, later feature delivery must integrate the approved minimal slice or stay capture-disabled; no ad hoc INI/JSON or permanently hard-coded binding workaround. Unknown settings are inert; sensitive invalid resolution fails closed. 0D precedence/defaults/reset semantics are unchanged. New operations use a snapshot; in-flight capture/action cannot retarget when settings or selected Ticket changes.

## Existing-Code Impact

SEARCH -> IDENTIFY -> REUSE / EXTEND -> NEW only when needed; current presence is not approved feature implementation.

| Component | Treatment | Actual evidence / why / future boundary |
| --- | --- | --- |
| AHK hotkey manager/registry | EXTEND shared host; new narrow binding activation helper | E-HOST controller handles F7 only, not generic configurable manager; no global registry found; keep one Clipboard action definition, no universal registry |
| AHK HTTP/IPC helper | NEW Named Pipe/security helper; HTTP NOT NEEDED primary | Tracked searches no helper; GuideRequest fixed message cannot carry content; Win32 client explicitly required |
| AHK HUD base | NEW small presentation; REUSE guide safety patterns | GuideCore large guide/editor, no reusable Clipboard HUD found; no cloning domain UI |
| AHK snapshot producer/worker | NEW fixed short-lived adapter mode | No capture hook found; documented blocking read justifies containment; not resident process/new app authority |
| Python IPC adapter | NEW application-owned native ingress | Mochi server cosmetic, no Clipboard listener; reuse framing/backpressure/test ideas without changing v1 |
| Application singleton | NEW F7Hub enforcement; REUSE conceptual QLockFile/owned-launch patterns | main/bootstrap lacks gate; Mochi lock applies renderer only; PendingPid not complete singleton |
| Navigation service | EXTEND MainWindow routes through narrow application adapter | Existing QStackedWidget/methods and pending guards; no generic navigation service or Clipboard Center established |
| Settings service | NEW under approved 0D, injected minimal projection | No shared SettingsService found; current Mochi dialog is runtime controls; no AHK INI substitute |
| Logging | REUSE bounded Python application logger | logging_config owns hierarchy/rotation/safe setup errors; AHK sends bounded safe codes, no parallel content logger |
| JSON validation | REUSE standard library/PySide6 dependency and strict DTO patterns; NEW composite profile | Mochi decoder demonstrates duplicate-key/type validation; no raw schema/wire expansion |
| Receipt / Clipboard persistence | EXTEND future 1A implementation, not current generic table | Consume atomic receipt/Item/Event/holds; schema belongs authorized 1A delivery, no migration here |
| Resident bridge / Windows service / automatic capture hook | NOT NEEDED / DEFERRED | No availability requirement justifying second application owner |
| Secure packaging/process-attestation mechanism | NOT VERIFIED actual deployed integrity | Narrow bootstrap trust contract specified; Windows-native negative and installer verification needed before activation |

## Error Matrix

The first twelve rows cover every original required error case. Codes are proposed feature errors/local typed observations under pinned 0B ERROR grammar, not an arbitrary string protocol. Logs: safe validated IDs/code/duration/size class only; never content, token, title, offending value, raw exceptions or untrusted reflected IDs.

| Case | AHK response / HUD | Retry? | Safe log | User action |
| --- | --- | --- | --- | --- |
| AHK hotkey conflict | Binding unavailable; retain known applied binding; ERROR | None automatic; one explicit Apply after repaired conflict | HOTKEY_UNAVAILABLE plus safe action ID, no raw setting value | Repair desired binding; no silent fourth shortcut |
| Clipboard locked | CLIPBOARD_LOCKED / ERROR, unchanged OS Clipboard | Lock row of bounded model only | Generic code | New capture after lock owner releases |
| Clipboard empty | EMPTY_CLIPBOARD / BLOCKED, no dispatch | NO | Code only | Copy supported text, new press |
| Unsupported format | UNSUPPORTED_CONTENT_TYPE / BLOCKED | NO | Safe format class if justified | Copy plain text; no files/OCR conversion |
| Service unavailable | IPC_UNAVAILABLE / ERROR; original unsent capture not saved | Predispatch connection budget only | Code/elapsed | Open F7Hub, then new capture |
| Authentication failure | Local IPC_AUTH_FAILED or safe AUTHORIZATION_DENIED / ERROR; no raw send | NO; never downgrade | Generic security code | Explicit trusted enrollment/repair |
| Timeout | Predispatch TIMEOUT known no effects; postdispatch local UNCERTAIN / ERROR | Receipt QUERY only after dispatch uncertainty | Valid ID/phase/elapsed | Bounded reconciliation or app recovery |
| Invalid JSON | CONTRACT_VALIDATION_FAILED or safe close / ERROR; no content echo | NO | Code/schema-known path only | Repair/update producer |
| Unsupported version | UNSUPPORTED_VERSION / ERROR | NO | Safe profile/version class | Update/restart matched components |
| Payload too large | PAYLOAD_LIMIT_EXCEEDED / BLOCKED before domain | NO; no truncation/repeated send | Size class/code | New smaller supported snapshot |
| Secret blocked | CLIPBOARD_SECRET_BLOCKED / BLOCKED; no Item/Event/hash/persist override | NO | Content-free generic block | Separately sanitize and capture new text |
| Partial processing | COMPLETED + PARTIAL / PARTIAL, truthful disposition | No automatic recapture; explicit owner reprocess later | Safe component code/count | Open Center; only prerequisite-safe actions |
| Snapshot instability / delayed render | Local CLIPBOARD_SNAPSHOT_UNSTABLE/READ_TIMEOUT / ERROR | Acquisition budget only; no auto worker restart | Code | Wait/fix source, new user capture |
| Privacy assessment failed/incomplete | CLIPBOARD_PRIVACY_CHECK_FAILED / BLOCKED | After component repair only, no permissive fallback | Generic component code | Repair detector/policy; no raw send override |
| Persistence/receipt/core FTS failure | CLIPBOARD_PERSISTENCE_FAILED / ERROR; no saved claim | Known rollback needs repair/still-live lease; uncertain commit lookup only | Safe code/type only | Repair/reconcile |
| Operation payload conflict / stale generation | CLIPBOARD_OPERATION_CONFLICT/STALE / ERROR | No mutation retry; lookup known outcome | Valid bound ID/code | Reconcile; genuine new intent distinct |
| Invalid response / bad correlation / bad MAC | Local CONTRACT_INVALID/IPC_AUTH_FAILED / ERROR; no remote outcome invented | Lookup only if original was dispatched | Generic code | Update/repair/reconcile |
| Capacity/rate/queue saturation | CLIPBOARD_CAPACITY_EXCEEDED or BUSY / ERROR; truthful memory-only alternative only if service expressly accepts | No background backlog; explicit fresh intent | Coarse class/code | Free eligible capacity without evicting holds, or later capture |
| Action target missing/stale/unavailable | Action ERROR; capture status remains intact | No automatic mutation retry | Safe key/ref class/code | Reopen/choose current authorized target |

## Testing Strategy

Planning source/document checks are distinct from future tests. No feature fixture/runtime suite exists by writing this report. Future tests use synthetic data, isolated namespaces/databases and no protected live guide preferences.

| Layer | Required meaningful assertion | Environment |
| --- | --- | --- |
| Unit / policy | Exact text/profile preservation, UTF-16/scalar/UTF-8 conversion, no NUL/surrogate replacement, closed action/metadata validation | CLOUD_PORTABLE for pure logic; native reads separate |
| Shared contract/golden fixtures | Valid AHK_MANUAL, missing text, unknown method/version, malformed UTF-8/JSON/duplicate keys/booleans/IDs, escaped-size boundaries, safe correlated RESULT/ERROR | CLOUD_PORTABLE models; AHK real serializer WINDOWS_NATIVE |
| Transport framing/auth models | Length/auth direction/nonce/sequence tamper, partial/coalesced frames, timeout/backpressure, no content before server proof, invalid/no credential | Portable model plus native actual pipe security |
| Producer mock / endpoint mock | Deterministic safe success/duplicate/partial/block/error, fake/stale/bad-correlated responses, busy and action expiry | Portable Python equivalent + native AHK/mock pipe |
| Integration / atomicity | Same-op retry one Event; new press same content new Event; full comparison conflict; no receipt outside core; restart/deletion/cache saturation fencing | CLOUD_PORTABLE isolated SQLite/domain plus WINDOWS_NATIVE cross-process |
| Recovery / uncertainty | Drop reply before/after commit, restart before/after receipt, lease/clock/host change, deleted source, query UNKNOWN; no fresh capture disguised as retry | Both; physical process/handle faults native |
| Privacy / security | Known/suspected secrets producer-blocked and authoritative-blocked; detector failure closes; no payload/token/title/hash in every log/error/HUD/descriptor; no raw action escalation | Both; native adversarial peer/worker fixtures mandatory |
| Service/navigation | Off-event-loop capture, GUI-thread completion, pending generation through callback gap, preserve Ticket/guide drafts, stale action revision/ref denied | Portable eligible Qt plus native focus integration |
| Native snapshot/hotkey/HUD | Actual physical/injected distinction, lock/race/delayed rendering, owner/source mismatch, Unicode, focus, DPI, cleanup and collisions | WINDOWS_NATIVE mandatory |
| Packaging / upgrade | Configured install paths, trusted AHK/runtime mode, no TCP/firewall exception, descriptors/ACL/token lifecycle, version mismatch, distinct checkout/session | WINDOWS_NATIVE; installed/EDR policy NOT VERIFIED |
| Performance / resource bounds | Measure small/medium p95/p99, worker startup, processing, cold launch, bounded allocations/queues; 1A targets retained, not claimed met | Declared reference hardware; native end-to-end |

1A small-text end-to-end p95 <250 ms and preparation p95 <100 ms remain aspirational targets, not this plan's achieved result. Worker isolation/startup may affect them; measure, optimize within boundaries or report a revised feature-owned target for review. Hard safety ceilings are not latency promises. A slow test never justifies disabling privacy/authentication or freezing GUI callbacks.

Future database fixtures require integrity_check=ok and zero foreign_key_check violations after relevant changes; no operational DB opened here. Native wrappers tests need invalid handles, races, partial I/O and supervised cleanup. No production dependencies/fixture files/tests were added.

## Native Windows Validation Requirements

Every native harness declares finite events/work, external whole-run timeout <=60 seconds for a focused scenario, owned PIDs/handles/files, key release on every path and deterministic cleanup. Stop after two identical failures without relevant state/content/config change; diagnose, don't relaunch an unchanged stuck worker/harness. No process-name termination or live endpoint/settings cleanup.

| Native gate | Required acceptance / actual current status |
| --- | --- |
| Win+Alt+C registration/trigger/unregister | Exact candidate, repeated fresh vs held press, Ctrl+C/Win+C/Win+V/native menu behavior, existing F7 tap/hold and Alt+F7; cleanup unregisters only test binding; NOT RUN |
| Collision/accessibility/keyboard layout | Existing external hooks, native registration failure, left/right modifiers, French/English/AltGr, Sticky Keys where enabled, RDP Windows-key routing; no universal app guarantee; NOT RUN |
| Clipboard locks/races | Owned locker/change producer, rapid owner change, foreground differs original source, empty/unsupported/rich+plain/CF_HDROP, stability and no mutation; NOT RUN |
| Delayed rendering / worker containment | Unresponsive synthetic owner, worker whole deadline, no frozen shared host, exit/handle/job cleanup and failed-cleanup quarantine; NOT RUN |
| Unicode / limits | Accents/emoji/combining/bidi/CRLF/LF/quotes/control escaping, surrogate/NUL/terminator errors, UTF-8 and whole-frame caps; NOT RUN |
| Auth/ACL/impersonation negatives | Other logon/user/session, same-user unrelated executable/interpreter, fake descriptor/pipe owner, missing/wrong/stale MAC/token, PID reuse, parent/child spoof, no content before server proof; NOT RUN |
| Singleton/startup/recovery | Concurrent F7/start/capture/direct launch, endpoint-not-ready, persistent PendingPid, app/host crash/version skew/re-enrollment, no duplicated DB bootstrap or worker/bridge; NOT RUN |
| Elevation/UIPI | Normal unelevated pair; elevated source without elevation; mixed-integrity pair refuses; source metadata/focus fail safely; NOT RUN |
| HUD / navigation / privacy | Nonactivated typing, deliberate focus/Tab/Enter/Esc, no global key interception, sensitive generic states, source/action expiry, no raw screen-share preview, intentional Open Center focus and denial fallback; NOT RUN |
| DPI / monitors / screenshots | 100%/125%/150%, primary/secondary mixed DPI/negative coordinates, work-area/taskbar clamp, changed/disconnected monitor, legibility/contrast/no clipped actions; isolated synthetic screenshots, no customer data; NOT RUN |
| Timeout/replay/rate/cleanup | Finite query/probe/capture counts and elapsed ceilings, no automatic mutation replay, retired generation rejection, bounded memory, exit cleanup and no stale test pipe/descriptor/HUD/modifiers/process; NOT RUN |

WINDOWS_NATIVE implementation acceptance is NOT RUN for every row. A planning PASS cannot satisfy these future integration gates; CLOUD_PORTABLE tests cannot replace native behavior.

## Required Diagrams

Conceptual Mermaid source only; rendering NOT RUN.

### Manual capture sequence

~~~mermaid
sequenceDiagram
    actor U as Technician
    participant W as Windows Clipboard
    participant A as Shared AHK host
    participant X as Owned snapshot worker
    participant T as Authenticated Named Pipe
    participant P as Python adapter
    participant S as ClipboardService
    participant R as ClipboardRepository
    participant D as SQLite
    participant H as Quick HUD
    U->>W: Native application copy
    U->>A: Win+Alt+C fresh manual press
    A->>X: One bounded native snapshot
    X->>W: Open/read/copy/unlock/close
    X-->>A: Stable eligible immutable text or local failure
    A->>A: Freeze IDs/snapshot and validate trusted server
    A->>T: Bounded authenticated 0B clipboard.capture
    T->>P: Authorized peer and valid frame
    P->>S: Validated request and policy snapshot
    S->>S: Complete privacy then eligible derivation
    alt Eligible durable capture
        S->>R: Prepared core
        R->>D: Atomic Item/Event/receipt/eligible children
        D-->>R: Commit
        R-->>S: Authoritative outcome
    else Eligible memory only
        S->>S: Bounded transient Item and occurrence
    else Rejection
        S->>S: No accepted core
    end
    S-->>P: Safe terminal outcome
    P-->>T: Correlated RESULT or ERROR
    T-->>A: Authenticated bounded response
    A->>H: Storage truth and privacy-safe actions
~~~

### Failure sequence

~~~mermaid
sequenceDiagram
    participant A as AHK host
    participant E as Endpoint
    participant H as Quick HUD
    participant L as Approved launcher
    A->>E: One bounded content-free authenticated connect
    E--xA: Absent or not ready
    opt Observed readiness change within connect budget
        A->>E: One connection retry
        E--xA: Still unavailable
    end
    A->>A: Release unsent raw snapshot
    A->>H: F7Hub unavailable - not saved
    Note over A,H: No background retry or automatic default launch
    opt Explicit Open F7Hub
        H->>L: One coalesced launch
        L->>E: Bounded readiness probes within 15 seconds
        alt Authenticated ready
            L-->>H: Ready - press capture again
        else Deadline/auth failure
            L-->>H: Unavailable / enrollment repair required
        end
    end
~~~

### Idempotency distinction

~~~mermaid
flowchart TD
    A[First genuine capture O1 M1 text T] --> B[Resolve Item I and create Event E1]
    B --> C[Commit receipt with core or bounded transient outcome]
    C --> R[Same immutable O1 M1 retransmitted]
    R --> K[Return original E1 outcome - replayed]
    K --> N[No new occurrence count or expiry update]
    C --> U[New later user press O2 M2 same T]
    U --> V[Resolve same Item I - duplicate content]
    V --> W[Create genuine Event E2]
    C --> X[Restart or retired admission generation]
    X --> Y[Receipt query only - no capture redispatch]
~~~

### HUD states

~~~mermaid
stateDiagram-v2
    [*] --> CAPTURING
    CAPTURING --> PROCESSING: eligible snapshot and authenticated dispatch
    CAPTURING --> BLOCKED: empty unsupported secret or size
    CAPTURING --> ERROR: read or availability failure
    PROCESSING --> SUCCESS: completed new Item
    PROCESSING --> DUPLICATE: completed existing Item
    PROCESSING --> PARTIAL: completed incomplete enrichment
    PROCESSING --> BLOCKED: authoritative privacy rejection
    PROCESSING --> ERROR: rejected invalid or unconfirmed
    SUCCESS --> [*]: dismiss UI only
    DUPLICATE --> [*]: dismiss UI only
    PARTIAL --> [*]: dismiss UI only
    BLOCKED --> [*]: dismiss UI only
    ERROR --> [*]: dismiss UI only
~~~

## Decision Register

All current choices remain RECOMMENDED until independent review, explicit USER approval and controlled integration. No new 1B decision is APPROVED. E-keys refer to Repository Areas Inspected; external links identify documented facts, not tested runtime.

| Decision | Options considered | Recommendation | Evidence | Rationale | Consequences | Depth | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D01 Capture hotkey | User ordered C/V/B; historical Ctrl+Alt+C | Win+Alt+C first suitable | E-HOST/GUIDE/APP; official Windows/AHK | Bounded audit passes C; B conflicts HDR | Native collision/registration gate; no current binding | DECIDE NOW | RECOMMENDED |
| D02 Manual workflow | Current Clipboard; copy selection; auto monitor | Current immutable text snapshot, no copy synthesis | 1A; E-HOST; Windows clipboard docs | Preserve native application/clipboard behavior | Separate future copy-and-capture | DECIDE NOW | RECOMMENDED |
| D03 Blocking read | Host call; worker thread; isolated worker | One owned short-lived AHK worker | Delayed rendering docs; E-HOST | Hard deadline cannot rely on host timer in blocked call | Narrow handle/process containment; startup measured later | DECIDE NOW | RECOMMENDED |
| D04 Transport | HTTP; pipes; per-call Python; cosmetic Qt | Authenticated native Named Pipe | E-IPC; Win32 security/PID docs | Sensitive peer binding/local session and no TCP | Native wrapper/security tests; HTTP reviewed fallback only | DECIDE NOW | RECOMMENDED |
| D05 Endpoint owner | App process; resident bridge; service | Running F7Hub application | E-APP/1A/0A | One application/domain/data authority | Closed app means unavailable; no tray invention | DECIDE NOW | RECOMMENDED |
| D06 Authentication | Hard-coded/install/file token; implicit same-user; owned bootstrap | Memory-only runtime token, owned handle handoff and OS peer pin/MAC | 0B sensitive boundary; Win32; E-IPC limitations | Path/producer/cache digest alone insufficient | Unenrolled legacy host fails closed; explicit safe recovery | DECIDE NOW | RECOMMENDED |
| D07 Discovery | Fixed name; secret file; random scoped descriptor | Non-secret protected descriptor + authenticated random pipe | 0B file boundary; E-IPC | Separate routing from authority/Settings | Native ACL/replace/stale-generation tests | DECIDE NOW | RECOMMENDED |
| D08 Singleton | PendingPid/window search; app lock+owner handoff | Application singleton before bootstrap, retained owner handle | E-HOST/APP | Current launcher cannot enforce all entry paths | NEW enforcement, no takeover/duplicate launch | DECIDE NOW | RECOMMENDED |
| D09 Auto-launch | Always; opt-in; explicit Open only | Off default; explicit Open; later bounded opt-in | E-HOST/0D | Predictable starts/minimized retention | One launch/15-s readiness; no relaunch loop | DECIDE NOW | RECOMMENDED |
| D10 Request mode | Blocking GUI; synchronous semantic reply; queued async capture | Synchronous terminal domain reply through asynchronous bounded adapters | 0B/1A; E-APP/IPC | No unnecessary global status/queue protocol | Postdispatch timeout UNCERTAIN; owner can still finish | DECIDE NOW | RECOMMENDED |
| D11 Retry/timeouts | One magic deadline; unbounded; phase budgets | Separate finite budgets, state-change gates, no blind dispatched resend | 0B/1A; original loop rule | Avoid double effects/frozen host | Explicit exhaustion matrix | DECIDE NOW | RECOMMENDED |
| D12 Replay scope | Hash key; RAM only; generic replay DB | Bound operation/message/generation, atomic 1A receipt, fenced bounded caches | 1A identity/failure; E-IPC last-request limitation | Distinguish content equality from occurrence | Restart query-only; unknown source cannot redispatch | DECIDE NOW | RECOMMENDED |
| D13 Source context | Full process/PID/title/URL; coarse/off | Off default, optional coarse class; runtime HWND only | 1A D25/0C privacy/E-GUIDE | Minimize sensitive attribution claims | No title/browser-source capture | DECIDE NOW | RECOMMENDED |
| D14 HUD focus/privacy | Activating raw popup; nonactivated safe status | Nonactivating generic default; deliberate focused interaction | E-GUIDE; 1A; Docs05 | Preserve typing and screen privacy | Scoped Esc/Enter; no automatic stale focus restore | DECIDE NOW | RECOMMENDED |
| D15 HUD timeout | Always permanent; short noninteractive; paused display timer | 5-s default/3-15-s preference, pause active interaction | 0D; Docs05/11 | Accessible interaction without unbounded RPC | Ref expiry independent; geometry later | DECIDE NOW | RECOMMENDED |
| D16 Actions | AHK business/command execution; owner routes | Closed keys + typed refs/fresh owner checks, diagnostic UI intent only | 0A/1A; E-SERVICE/APP | Presentation offer never authority | Absent attach/Mochi/input capability unavailable | DECIDE NOW | RECOMMENDED |
| D17 Hotkey Settings | Permanent static binding; new INI; central shared key | 0D definition/snapshot and desired/applied activation ACK | 0D hotkey boundary/E-HOST | One truth, failures visible | Minimal Settings slice prerequisite, no universal registry | DECIDE NOW | RECOMMENDED |
| D18 Automatic capture/binary/URL extraction | Early monitor/conversion; defer | Separate future policy/format review | 1A/0B/Mochi exclusions | Manual MVP sufficient | No OnClipboardChange/OCR/files/resident bridge now | DEFER | DEFERRED |
| D19 HUD appearance | Pixel-perfect now; stable boundary then design | Exact geometry/icons/animations later | Docs05/1C separation | Boundary resolved without speculative cosmetics | Future native visual review | DESIGN NEXT | DEFERRED |
| D20 Deployed trust/performance/policy | Assume tested; verify native/employer environment | Activation/release evidence required | E-EXT/E-TEST only source facts | No runtime/credential/provider facts invented | Fail closed if boundary unavailable | DESIGN NEXT | NOT_VERIFIED |

## Requires User Decision

NONE at architecture-planning depth. The first preferred hotkey survives the bounded audit; authenticated transport/lifecycle/privacy recommendations are sufficiently defined. Alternatives alone are not unresolved user choices. A future failure to meet native trust/containment requirements must stop the affected activation and return to its owner, not silently weaken the recommendation.

The exact candidate still requires INDEPENDENT PHASE 1B ARCHITECTURE REVIEW -> explicit USER approval -> controlled integration before Phase 1B closes or becomes authoritative input for 1C. This lifecycle approval requirement is separate from a material design question; no implementation authority follows from the result.

## Assumptions

| ID / classification | Premise / safe failure / verification |
| --- | --- |
| A01 ASSUMPTION | One technician data scope, Windows desktop medium-integrity app/host, per-logon session. Cross-user/elevation denied; deployment tests verify actual scope. |
| A02 ASSUMPTION | Trusted installation/loaded code and owned-launch relationship can establish the enrolled live processes. Arbitrary same-user code injection/admin compromise is outside this IPC isolation promise; deployment/security owner must verify or keep capture disabled. |
| A03 ASSUMPTION | AHK native worker startup/read/cleanup can meet proposed deadline without weakening privacy. If not, narrow/optimize under review; no in-host blocking fallback. |
| A04 ASSUMPTION | Future 1A ClipboardService/atomic receipt and minimal 0D Settings implementation will be available before feature activation. Missing dependency leaves feature unavailable, not duplicate local truth. |
| A05 ASSUMPTION | Expected manual text fits approved inline caps; no production size/latency distribution observed. Oversize refuses without partial evidence or file bypass. |

No assumption supplies approval, emitter identity, employer permission, native PASS, current singleton capability or implemented API.

## Not Verified

Actual AHK/Python/Windows/Qt installed versions; live host/process/input state; installed Windows/application/custom shortcut collisions; actual native hotkey registration/menu masking/accessibility/RDP; worker startup and delayed-render cleanup; pipe ABI/overlapped cancellation/security descriptors/peer identity proof/inheritance; Windows discovery ACL/reparse/atomic replace behavior; authenticated bootstrap/enrollment, app singleton, generation/cache/replay/restart implementation; native elevation/UIPI/session behavior; HUD/focus/DPI/multi-monitor screenshots; throughput/p95/EDR/packaged installation/firewall policy; shared Settings/Clipboard persistence/action APIs; operational database integrity/rows/backups; employer/customer policy; provider authentication/data terms/permissions; physical memory/paging/dump erase. These are explicit future verification/activation gates, not evidence of current implementation.

No live Clipboard, customer content, protected INI, operational database, external prototype or unrelated runtime was read or managed. Historical upstream PASS/candidate labels are not fresh runtime evidence. Tests were inspected, not executed.

## Risk Register

Likelihood UNKNOWN throughout: source/design evidence supplies mechanisms, not operational probability. Impacts qualitative. Mitigations are proposed; residual native/security effectiveness is NOT_VERIFIED, not claimed deployed.

| Risk | Likelihood | Impact | Mitigation | Residual risk | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Hotkey collision | UNKNOWN | MEDIUM | Bounded inventory, configurable desired/applied binding, native registration failure visible | External hooks/custom maps unknown | AHK/Settings | NOT_VERIFIED |
| Native behavior suppression | UNKNOWN | MEDIUM | C first suitable; B rejected HDR; no copy override/wildcard/forced hook | Menu/layout/RDP effects pending | AHK | NOT_VERIFIED |
| Clipboard lock/race/delayed rendering | UNKNOWN | HIGH | Stable open/read/private copy, finite attempts and supervised worker | Native cleanup/deadline accuracy unknown | Windows adapter | NOT_VERIFIED |
| Worker/process proliferation | UNKNOWN | HIGH | One worker per pending capture, exact ownership, hard deadline, failed-cleanup disable | Startup/job/handle races pending | AHK infrastructure | NOT_VERIFIED |
| Source metadata privacy | UNKNOWN | HIGH | Off default/coarse optional; no title/source URL/PID wire | Coarse class/time can identify behavior | Clipboard/security | RECOMMENDED |
| Raw Clipboard leakage | UNKNOWN | HIGH | Producer gate, complete authoritative gate, authenticated channel, no raw logs/descriptor/default preview | False negatives/paging/OS clipboard remain | Clipboard/security | NOT_VERIFIED |
| Malicious local process | UNKNOWN | HIGH | Owned bootstrap, peer pin, session token/MAC, closed operations | Same-account injection/admin/DoS beyond guarantee | Security/bootstrap | NOT_VERIFIED |
| IPC exposure/squatting | UNKNOWN | HIGH | Logon DACL, remote refusal, first ownership, random name, no TCP | Namespace denial/deployment policy possible | Infrastructure | NOT_VERIFIED |
| Authentication/token leakage | UNKNOWN | HIGH | Memory-only private handoff, no file/env/argv/Settings, revocation | Memory inspection/inherited-handle bugs pending | Security | NOT_VERIFIED |
| Replay | UNKNOWN | HIGH | Frame sequence, five-minute admission, fenced generations, receipt | Reconciliation may remain uncertain after expiry | Clipboard/IPC | NOT_VERIFIED |
| Duplicate Capture Events | UNKNOWN | HIGH | Bound immutable operation, exact comparison, atomic receipt, no blind resend | Cross-process concurrency tests pending | Clipboard/repository | NOT_VERIFIED |
| Discovery staleness/PID reuse | UNKNOWN | HIGH | Protected non-secret descriptor, live process handle/creation check | Native file/identity races pending | Infrastructure | NOT_VERIFIED |
| Version skew | UNKNOWN | MEDIUM | Exact supported profile, reject closed unknown semantics | Upgrade coordination still required | Contract owner | RECOMMENDED |
| Unbounded retry/polling | UNKNOWN | HIGH | Separate attempts/outer deadlines/state-change/exhaustion model | Implementation can violate unless tested | Adapter/testing | NOT_VERIFIED |
| Startup race | UNKNOWN | HIGH | Endpoint after services, bounded status, one launch/PendingPid | Cold-start timing unknown | Bootstrap | NOT_VERIFIED |
| Multiple instances | UNKNOWN | HIGH | New singleton before DB/endpoint; owner handoff | Current main lacks complete enforcement | Bootstrap | NOT_VERIFIED |
| Elevation/UIPI | UNKNOWN | HIGH | Medium pair only, no elevation for metadata, mixed pair refusal | Elevated-source focus/access pending | Windows/security | NOT_VERIFIED |
| HUD privacy/screen-share | UNKNOWN | HIGH | Generic/concealed default, service-approved opt-in, no title/secret | Even eligible preview/context can be sensitive | Presentation/privacy | NOT_VERIFIED |
| Focus stealing | UNKNOWN | MEDIUM | Nonactivating capture HUD, explicit actions, no stale forced restore | Windows activation policy/accessibility unknown | AHK/navigation | NOT_VERIFIED |
| Multi-monitor/DPI | UNKNOWN | MEDIUM | Work-area clamp, mixed-DPI/disconnect/native visual matrix | Geometry/readability untested | Presentation | NOT_VERIFIED |
| Action-routing escalation | UNKNOWN | HIGH | Closed keys, typed refs/current owner checks, no AHK domain executor | Missing APIs remain unavailable | Owning services/security | NOT_VERIFIED |
| Copied-command execution confusion | UNKNOWN | HIGH | Capture is data; diagnostic opens reviewed run UI, never copied shell | User misunderstanding still possible | Diagnostics/presentation | RECOMMENDED |
| Packaging/firewall/EDR friction | UNKNOWN | MEDIUM | No TCP/exception primary; trusted fixed paths/runtime, native deployment test | Actual policy/package restrictions unknown | Installer/infrastructure | NOT_VERIFIED |
| Architecture PASS mistaken for runtime | UNKNOWN | HIGH | Explicit NOT RUN matrices and review/approval/integration gates | Downstream must preserve distinctions | Author/reviewer | RECOMMENDED |

## Recommended Implementation Slices

Future slices only, each separately authorized after this architecture is independently reviewed, USER approved and integrated. Dependencies are explicit; a skeleton/mock slice cannot activate capture against missing security/persistence/Settings.

| Slice | Bounded objective / prerequisites | Independent validation / deliverable |
| --- | --- | --- |
| S1 Composite contract fixtures | Pure 0B capture/result/error/lookup/action schemas and safe fixtures; fixed 1A semantics | Strict valid/invalid/Unicode/escape/cap/correlation tests; no listener or hotkey |
| S2 F7Hub singleton lifecycle | One per-logon/install owner before bootstrap; content-free second-invocation handoff | Concurrent cold launch/exit/crash/owner denial; isolated app fixtures, no Clipboard feature |
| S3 Authenticated bootstrap/discovery | Narrow owned-process enrollment, memory token, protected non-secret descriptor, peer identity | Spoof/wrong-session/PID reuse/token/version/ACL/reparse negative native tests; no raw Clipboard traffic |
| S4 Named Pipe transport adapter | Bounded frame/MAC/overlapped I/O/read/write/connection/rate behavior atop S3 | Mock producer/endpoint, split frames/deadline/backpressure/cleanup; no arbitrary action or business persistence |
| S5 AHK snapshot worker | One fixed mode reading text/plain, producer preflight, private handles and external deadline | Native lock/race/delayed-render/Unicode/size/secret/cleanup tests; no production hotkey |
| S6 Python capture adapter | Validate accepted profile and invoke separately implemented 1A service plus minimal 0D snapshot | Service stubs then isolated integration; fail closed missing dependencies; no alternate DB path |
| S7 Receipt/replay integration | Atomic 1A receipt plumbing, lease/generation/cache saturation/restart query semantics | Commit/lost reply/delete/concurrent/restart fault injection; new schema only separately authorized under 1A |
| S8 Basic Quick HUD | Safe states/storage truth/ref expiry/nonactivating focus, fixture results | Native synthetic visual/focus/accessibility/DPI checks; no unapproved business actions |
| S9 Settings binding activation | Minimal approved 0D key/projection/desired-applied ACK and Win+Alt+C activation | Collision/apply/ACK-loss/restart/register/unregister plus F7/Alt+F7/native copy regression |
| S10 Unavailable/startup UX | Explicit Open app; bounded optional auto-launch only after S2/S3 | Readiness race/deadline/same-snapshot/nonduplication/recovery; default off |
| S11 Action routing | Open Center after 1C; one eligible owner action per slice, Pin/Attach separately | Revision/source/target/privacy/promotion/audit/uncertainty tests; absent diagnostic/Mochi APIs remain unavailable |
| S12 Native end-to-end acceptance | Reviewed exact candidate with all prior gates, declared hardware/session | Hotkey -> snapshot -> authentic ingress -> receipt -> HUD; physical input, focus/DPI/multi-monitor and test-owned cleanup |

No giant Implement Clipboard IPC slice, migration number, production source edit or independently authorized downstream work is created by this list. Automatic monitoring, browser source retrieval, binary/OCR, resident bridge and external Mochi context remain DEFERRED.

## Phase 1C Inputs

After independent review -> explicit USER approval -> controlled integration of 1B, 1C may rely on manual current-Clipboard text/plain workflow; Python domain/persistence authority; typed durable/transient Item/Event refs; three identity/replay rules; explicit storage/disposition/completeness; safe result/action availability; unavailable/unconfirmed/error states; off-default minimized source/history/sharing; 0D desired/applied/start-bound settings; separate authenticated app-owned integration/HUD boundary.

1C designs the full PySide6 Clipboard Center history/search/views/Inspector/actions/accessibility/geometry independently. It may consume open_center typed navigation and future component capability without inventing AHK history/domain truth, altering 1A preservation/Entity/Tag/privacy rules or changing 1B ingress/security/replay. Raw Inspector access is separately owner-authorized; HUD preview is not whole evidence. Missing/expired source and post-commit read failure are honest UX states. Center layout is not fixed by AHK HUD geometry.

No 1C execution occurred. 1B is not CLOSED until its lifecycle gates finish. Clipboard and Settings implementation remain NOT AUTHORIZED.

## Documentation Impact

Only this target receives an append. After separately authorized approval/delivery, assess affected Docs05 Center/HUD accessibility; Docs06/13 bootstrap/ingress/layers/navigation; Docs11 host/manual snapshot/hotkeys/IPC/HUD; Docs10 runtime descriptor/worker placement; Docs04 technician workflow; actual Status/CURRENT_STATE/ChangeLog. 1A persistence delivery owns any Docs07/08/09 synchronization, not this report. Docs12 only for a separately approved diagnostic-input change, never because copied content resembles commands. Foundation unchanged; consume/link owners rather than duplicating or redefining policy. No canonical document is rewritten to present proposals as implemented.

## Phase 1B Acceptance Criteria

FRESH author-side architecture-planning assessment, not independent review, approval, implementation or runtime verification. Exact original section 164 criteria independently mapped.

| # | Criterion | Result | Supporting section / evidence |
| --- | --- | --- | --- |
| 1 | Existing AHK integration architecture has been inspected. | PASS | Repository Areas / Verified Current State; E-HOST/GUIDE |
| 2 | Existing hotkeys have been inventoried. | PASS | Hotkey Inventory / Recommendation; tracked global/scoped/fixture/application bindings |
| 3 | Manual capture semantics are defined. | PASS | Manual Capture Workflow / Snapshot; no copy synthesis, immutable request |
| 4 | AHK/Python responsibilities are explicit. | PASS | Responsibility Boundary / adapter-service ownership |
| 5 | AHK does not own persistence or business rules. | PASS | Responsibility / Action Routing / 1A constraints |
| 6 | Transport options have been compared. | PASS | Formal four-option Transport Evaluation |
| 7 | A transport recommendation or explicit decision gate exists. | PASS | Named Pipes primary, reviewed HTTP fallback, no automatic downgrade |
| 8 | Local IPC security requirements are defined. | PASS | Security / Threat / Authentication / Discovery / native negative gates |
| 9 | Contract usage matches Phase 0B. | PASS | Seven fields/classes/composite versions/correlation/strict bounds; legacy protocols unchanged |
| 10 | Transport retry and content deduplication are clearly distinguished. | PASS | Idempotency & Replay / required diagram / 1A identities |
| 11 | Bounded retry behavior is defined. | PASS | Retry table includes trigger/count/elapsed/state/exhaustion; no unbounded polling |
| 12 | F7Hub-unavailable behavior is defined. | PASS | Availability / lifecycle / failure diagram / default-off launch |
| 13 | Source metadata is defined with privacy rules. | PASS | Source Context matrix; off/coarse, no title/source URL |
| 14 | Quick HUD scope is defined. | PASS | Quick HUD / five terminal state matrix / Center separation |
| 15 | HUD action routing is defined. | PASS | Action Routing matrix; owning capability/intent/ref validation |
| 16 | Clipboard content remains read-only by default. | PASS | Snapshot/Manual; no mutation API/normalization or copied-command execution |
| 17 | Sensitive HUD behavior is defined. | PASS | Privacy / HUD safe preview and generic blocked/error |
| 18 | Hotkey configuration integrates with Settings. | PASS | 0D central key, immutable projection, desired/applied ACK, no new INI truth |
| 19 | Native Windows validation requirements are defined. | PASS | Explicit Windows matrix and finite supervised native safety; actual NOT RUN |
| 20 | Automatic capture remains clearly separated from manual capture. | PASS | Manual scope / deferred decision and no OnClipboardChange |
| 21 | No production implementation has occurred. | PASS | One tracked documentation append; final scope/index/prefix gate |
| 22 | Phase 1C can design the full PySide6 Clipboard Center independently. | PASS | Conditional Phase 1C Inputs; no presentation/domain redefinition |
| 23 | Future implementation can be decomposed into small vertical slices. | PASS | Twelve bounded dependency/validation slices, no implementation |

23/23 PASS at architecture-planning depth only. No runtime acceptance or implementation-readiness token.

## Validation

Environment: WINDOWS_NATIVE host. Provenance: FRESH author-side static source/document/Git assessment. A PASS below means planning completeness or the specified static check, never native feature execution.

| Required category | Result | Evidence / limit |
| --- | --- | --- |
| Current AHK inspection | PASS | Tracked host/launcher/controller/guide/hooks/IPC/GUI/source search |
| Hotkey inventory | PASS | All tracked AHK and application bindings, strict C/V/B priority, official risks |
| Manual capture model | PASS | Immutable read-only current text, worker/snapshot/source/secret/size gates |
| Transport evaluation | PASS | Formal matrix/primary/fallback/rejections/deployment |
| Contract integration | PASS | 0B envelope and feature profiles, strict versions/errors/sizes/classes |
| Idempotency model | PASS | Bound operations, atomic 1A receipt, cache fence, restart/deletion query-only |
| Retry/timeout model | PASS | Trigger/count/duration/state/exhaustion and outer deadlines |
| Source metadata model | PASS | Required capture/transmit/persist/log/HUD/Mochi matrix |
| Privacy review | PASS | Eight requested content cases plus derivative, two gates, no default sharing |
| Security review | PASS | Eight mandatory invariants plus threat/auth/discovery/peer/rate model |
| HUD architecture | PASS | States/focus/accessibility/preview/timer/privacy/Center boundary |
| Action-routing model | PASS | Six requested actions and local actions, availability/owner/security |
| Settings integration | PASS | 0D input classes, defaults/bounds/projection/activation distinction |
| Testing strategy | PASS | Future portable/native/contract/security/recovery/cleanup matrices |
| Scope control | PASS | Sole tracked append, empty index, protected path observed through Git only |
| Baseline / all upstream input identities | PASS | Required live/local Git commands and exact blobs |
| Original raw/filtered contract prefix | PASS | Byte-oriented comparison against full original checkout-filtered HEAD and original raw SHA-256; historical examples preserved |
| Report sections / criteria / matrices / diagrams | PASS | Static extraction verifies required report headings, exact 23 original criteria with PASS, balanced fences, three required conceptual diagrams |
| Whitespace / candidate identity / final scope | PASS | git diff --check, status/name/index/untracked gates; external digest/blob/bytes/line/numstat computation |
| Application runtime | NOT RUN | No F7Hub app/bootstrap launched |
| Database runtime/integrity | NOT RUN | No operational or fixture DB opened |
| GUI | NOT RUN | No Qt/Windows HUD launched |
| AHK runtime | NOT RUN | No interpreter/host/snapshot worker/capture invoked |
| PowerShell runtime | NOT RUN | No F7Hub diagnostic/admin operation executed; shell used for static file/Git work only |
| Mochi runtime | NOT RUN | No renderer/provider/context invocation |
| Actual IPC | NOT RUN | No server/client/listener created or tested |
| Hotkey registration | NOT RUN | None registered |
| Mermaid rendering | NOT RUN | Source checked only; visual rendering not established |
| Independent architecture review | NOT RUN | Next lifecycle gate |
| Staging/commit/push/PR/merge | NOT RUN | Explicitly prohibited |

Production changes: NONE. Database changes: NONE. Test-source inspection is not test execution. No full regression suite run for architecture authoring. Original final line lacks newline; Git may count its unchanged text as one deleted/readded line when the append introduces a terminator. Exact original raw bytes and normalized Git content remain the complete prefix; numstat is reported honestly outside the document.

During this authoring task, no native/GUI/server/hotkey test loops occurred. A long shell append was rejected before process creation by tool policy with no substantive reason; that route stopped and an external continuity checkpoint/draft was used with a short byte-append command. One checkpoint patch had an incorrect exact-line context; correcting to the actual line resolved it, not an unchanged retry loop.

Review Record: NOT RUN. Approval Record: NONE for this candidate. Change History: 2026-10-07, preserved full original contract, appended architecture Execution Report, author-side static scope/identity/completeness checks. Protected unrelated state has no read/hash/metadata certificate because those operations are expressly forbidden.

## Result

READY_FOR_CLIPBOARD_GUI_DESIGN

All 23 criteria PASS at architecture-planning depth; approved 1A semantics and Foundation boundaries preserved; bounded hotkey and actual transport/security/authentication recommendations established; no unresolved material user choice blocks the conditional 1C integration/design contract.

Candidate remains UNAPPROVED / UNSTAGED / UNCOMMITTED / UNPUBLISHED / NOT INTEGRATED. Next gate: INDEPENDENT PHASE 1B ARCHITECTURE REVIEW. Only after independent review, explicit USER approval and controlled integration may Phase 1B be CLOSED and 1C architecture planning become the next Clipboard phase. STOP: no independent approval/integration/1C/Clipboard/Settings/AHK/IPC/HUD/Python/migration/PowerShell/Diagnostics/Analytics/Mochi implementation authorized or performed.

---

# CP-00 Current Reconciliation

## Control and authoritative current direction

Date: 2026-10-08 (America/Toronto). Architecture/documentation only; author
result READY_FOR_REVIEW. Independent review, CP-00 approval and integration are
pending. The user's explicit decisions supersede conflicting recommendations;
the reconciliation candidate itself is not APPROVED, INTEGRATED or CLOSED.
Baseline: `9dc7409e51a8023ba0f0c287e3e840f81bebac66`.

Consume [1A CP-00 lifecycle/provenance](1A_Clipboard_Domain_Data_Lifecycle.md#cp-00-current-reconciliation)
and [1C CP-00 intent/presentation](1C_PySide6_Clipboard_Center.md#cp-00-current-reconciliation).
The entire preceding report remains historical evidence. In particular, the
Win+Alt+C capture-current recommendation, Win+Alt+V fallback, no-selection-copy
MVP and coarse-only source policy describe earlier decisions. They must not be
used to negate the current successor rules below. Current-Clipboard capture
itself remains a distinct supported architectural use case, with no automatic
shortcut reassignment or assumed third production binding.

## Action and technology ownership

| Stable action | USER current semantics | Desired future default |
| --- | --- | --- |
| clipboard.capture_selection | COPY_SELECTION: native Ctrl+C request, then newly copied eligible text; fresh update required | Ctrl+Alt+C |
| clipboard.capture_current | CAPTURE_CURRENT_CLIPBOARD: bounded read of existing Windows Clipboard, no Ctrl+C synthesis | Explicit future UI action; no new global binding selected by CP-00 |
| clipboard.paste_active | Exact explicitly armed Item/revision; Python authorizes full text, AHK writes it to normal Windows Clipboard and requests native Ctrl+V | Ctrl+Alt+V |

These are future action semantics and desired defaults, not registered hotkeys
or implemented capabilities. Native Ctrl+C/Ctrl+V outside an explicitly invoked
eligible F7Hub action remain ordinary application behavior. No Ctrl+C hook or
global Office exclusion is introduced by this plan.

AHK v2 owns shortcuts, cheap foreground awareness, bounded native copy/paste,
Windows Clipboard acquisition/write and transient Windows context. It stays a
narrow adapter in the existing shared host, with contained worker mechanics
where native blocking requires them. Python retains trusted contract/service/
domain validation, privacy/sensitivity, deduplication, retention, persistence,
SQLite, exact active-paste authorization and higher-level automation. Neither
GUI, AHK, JSON validity nor foreground labels grant domain/effect authority.

## Action-specific exclusions and press-cycle seam

USER DECISION: both selection capture and active paste initially exclude the
following exact executable basenames:

| Initial canonical exclusion | Coverage |
| --- | --- |
| WINWORD.EXE | Word |
| EXCEL.EXE | Excel |
| OUTLOOK.EXE | Outlook |
| OLK.EXE | New Outlook, explicitly included |
| POWERPNT.EXE | PowerPoint |

Use one small Clipboard-specific policy helper after SEARCH -> IDENTIFY ->
REUSE/EXTEND -> CREATE ONLY IF NECESSARY. Centralize these literals; capture and
paste retain independent action-owned exclusion sets/preferences even when
their initial values match. No universal hotkey framework or refactoring of
F7HotkeyController is justified. F7 tap/hold and Alt+F7 guide behavior remain
independent and unchanged. These exclusions do not create a content ban on
manually invoking capture_current from the future Windows snapshot view.

Resolve reliable foreground executable identity, derive its basename once if
the native provider supplied a full path, validate it, and normalize case once
before exact equality. Folder/path spelling never controls membership. Unknown,
empty, malformed or unresolved identity fails closed: no Clipboard dispatch and
no native shortcut interception. Reject ambiguous basename inputs rather than
guessing. Prefix, suffix, substring, regex similarity and title matching are not
exclusion rules. Input fixtures `winword.exe`, `WINWORD.EXE`, `WinWord.Exe`,
`olk.exe`, `OLK.EXE`, `PowerPnt.exe` match; `WINWORD2.EXE`, `MYOUTLOOK.EXE`,
`OUTLOOK.EXE.BAK`, `OLKHELPER.EXE`, `POWERPNT2.EXE` do not.

The hotkey eligibility predicate only checks action policy against cheap
foreground identity. It reads/writes no Clipboard, waits/sleeps on nothing,
performs no IPC/SQLite/Settings mutation/logging/launch/focus change, and uses
no title collection, UI Automation, browser URL discovery, PowerShell or
provider calls. Workflow applied enablement is supplied by its owner outside
the predicate. Excluded/unknown contexts preserve native chord behavior through
contextual eligibility; silently consuming and then forwarding a substitute
Send is not native-shortcut preservation.

Required seam: trigger eligibility -> latch physical press cycle and bind
transient target -> recheck immediately before dispatch/native input. Recheck
both action eligibility and the originally bound foreground window/process
identity; an allowed app B cannot replace allowed app A. No attempt to refocus
the original target. Change, exclusion or unknown identity aborts the F7Hub
effect. These checks reduce races; they cannot promise atomicity across OS
focus changes and input delivery.

One physical shortcut press/release cycle permits at most one operation, even
after rejection/error/interruption or foreground change. Held autorepeat and
modifier release/repress cannot create another cycle while the trigger key
remains physically down. Rearm only after release of the trigger and participating
modifiers; a new completed cycle may act again. Track/observe release even when
the contextual action becomes ineligible; entering a permitted app while keys
are held cannot manufacture a fresh press. Execution/busy cleanup and physical
rearm are separate: a callback exception must not leave busy state stuck or
reset a held press to invocable. CP-01 native fixtures must prove this seam,
including modifier release ordering and an initially excluded/unknown held chord
moving into an allowed context. Registration alone or direct callbacks are
insufficient evidence of physical hotkey behavior.

## Selection-copy acquisition contract for later delivery

Check prerequisites and foreground eligibility before any native copy effect.
Bind original foreground identity and read a transient pre-copy sequence marker;
recheck before requesting exactly one native Ctrl+C. Use bounded physical
modifier handling so the emitted action is Ctrl+C, not another Ctrl+Alt+C
trigger. No user-process elevation, arbitrary application activation or title/
URL/UIA inspection is a fallback. Input injection is later native validation,
not CP-00 execution.

Require a fresh supported Clipboard update after that request, then a stable,
bounded text/plain snapshot under existing worker/size/Unicode/privacy rules.
No update, timeout, unknown sequence, malformed/unsupported content or ambiguous
target/race produces safe failure; never read old/current contents as successful
selection capture. Do not empty the Clipboard to simulate freshness or preserve
old raw contents merely to restore them. Identical newly copied text is valid
freshness if change detection succeeds: content equality and update identity
are different questions.

Microsoft documents sequence as window-station change detection, including
emptying and delayed-rendering behavior, not source attribution. INFERENCE:
sequence change alone cannot prove the intended Ctrl+C produced the content;
retain cheap target/owner stability checks and refuse detected unrelated updates
or unresolved acquisition ambiguity. Concrete application compatibility and
residual races need a bounded acquisition slice. No absolute source-attribution
claim follows from process/title. See [sequence documentation](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getclipboardsequencenumber)
and [Clipboard operations/ownership](https://learn.microsoft.com/en-us/windows/win32/dataxchg/clipboard-operations).

Keep existing containment: finite attempts and an external whole-worker/native
run deadline effective during blocking APIs. Reuse 1B's proposed read ceiling,
worker ownership and cleanup; exact copy-wait/write/input sub-budgets must be
reviewed and measured in their delivery slices. No infinite polling, automatic
second copy or relaunch. Failed native copying creates no Item/Event. Once an
eligible immutable snapshot is accepted, transport retry retains original
operation/message/source/mode; it cannot recopy or capture a later Clipboard.

## Active paste authorization and native effect

USER DECISION: Set for Paste explicitly arms an exact Item/revision in the
current F7Hub application session; row selection does not arm. Python owns the
reference and revalidates it on every paste. Bind operation, armed generation,
exact source revision and original transient target at invocation. Later row,
Ticket or active-paste changes cannot retarget accepted work; pre-effect
source/privacy invalidation or Clear revokes pending unused authorization.

Python checks current source/revision, complete privacy admission, workflow
availability and full-text eligibility before returning a purpose-bound,
single-operation authorization to the authenticated AHK adapter. Missing/stale/
deleted/expired/ineligible source returns no raw text; confirmed invalidation
or stale exact-reference failure clears arming. Temporary owner unavailability
is no proof of deletion: deny paste and display unavailable rather than silently
substituting a cached body or newer revision. No reusable hidden raw-text cache
in GUI, service, AHK, logs or files; a narrowly lived authorized delivery buffer
for one operation is released promptly.

AHK independently verifies response correlation, bound operation/source/arming
generation and target context; rechecks foreground/policy immediately before
Clipboard write and before native Ctrl+V. Source authorization must still be
valid at the effect boundary, using a reviewed one-use freshness/revocation
mechanism in the future paste slice. An old response is not a transferable
paste permission. This is a requirement, not a new token API selected in CP-00.

Write authorized full text to the normal Windows Clipboard, then request native
Ctrl+V once. USER DECISION: leave pasted text on Windows Clipboard afterward;
do not automatically restore previous contents in MVP. ClipboardAll preservation/
restoration is deferred to separately reviewed work. If writing succeeded but
input was subsequently blocked/failed, report that distinction truthfully:
Clipboard may already contain authorized text, with no fake rollback or paste
success. A newer user Clipboard change prevents sending a substituted value;
do not overwrite it again or restore an older snapshot. Input dispatch is not
proof the target application inserted text; uncertain delivery must not trigger
automatic repeat or replay.

## Feature profile extension and future Settings contributions

Reuse 0B envelope, classes, correlation, strict bounded serialization, safe
errors and compatibility rules and 1B's authenticated, application-owned IPC.
Retain producer/generation/operation binding, immutable-request replay checks,
receipt recovery and content-before-authentication prohibition. No new global
grammar, endpoint or general native-input/shell RPC.

Capture feature profiles must distinguish selection-copy versus current capture
mode and allow only 1A's admitted bounded source fields. Active-paste profiles
need exact source/ref revision, arming generation, operation correlation and
purpose-bound full-text response plus truthful authorization/write/input outcomes.
PID/HWND/sequence stay local transient Windows context, not ordinary durable
payload fields. Wire spelling/schema versions/closed enums and native revocation
mechanics are DESIGN NEXT in separately reviewed contract/security slices.
Never silently add these semantics to a closed released v1 profile: use 0B's
breaking-change review and explicit supported-version rules. Existing capture
result output ceiling cannot be assumed to carry full paste text; the paste
profile must establish a reviewed bounded response budget within approved
document/content maxima. No full text in receipts, generic status or logs.

0D future contributions: master workflow/history enablement, separately owned
selection/paste bindings and action exclusions, independent process/title
collection, and normal retention. No actual new Settings keys/storage are
defined here. Use typed definitions and authenticated immutable desired/applied
projections; persisted desired bindings do not mean active registration.
Setup opt-in and eligible provenance use 1A CP-00; neither an imported preference
nor saved boolean grants new permission. Missing secure Settings/IPC/native
prerequisites keeps production capture/paste unavailable. No CP-00 production
Ctrl+Alt+C/V registration, OS Clipboard access, copy/paste, ingress or database
change occurs.

## Performance, CP-01 prerequisite and validation gates

The synchronous native path contains cheap Windows facts and bounded input/
Clipboard mechanics only. Python validation/interpretation/persistence runs
outside the GUI thread with GUI-thread presentation. No synchronous OCR, UIA,
source URL discovery, executable signature inspection, network enrichment or
ML/AI analysis on the hotkey path. Metadata failure may safely omit enrichment;
unknown foreground identity cannot bypass the action guard. Normal logs exclude
raw content and titles; no cloud/provider transmission or semantic acceptance.

CP-00 review/approval/integration is a prerequisite to CP-01, not completed by
this author report. CP-01 is limited to action-specific policy and press-cycle
mechanics, using fixture bindings/counters, no Clipboard content/native Ctrl+C/V,
production bindings, Settings, IPC, migrations or persistence. Native Windows
validation is mandatory for CP-01, including allowed/excluded/unknown and exact
mixed-case/prefix/suffix cases; repeat/release/context/recheck/failure cleanup;
native shortcut preservation; unchanged F7 tap/hold and Alt+F7; bounded owned
process/key/hotkey cleanup. Later production activation additionally needs
separately delivered Settings, secure capture, authenticated IPC, domain write
admission/persistence and native acquisition/paste authorization.

CP-00 author checks cover all A-O decisions and the requested 20 consistency
criteria through 1A lifecycle/provenance, this action/native contract and 1C
presentation. Reproducible external evidence records exact raw and Git-normalized
prefix preservation, unchanged Foundation/Semantic authorities, the five-path
allowlist, empty index, links/anchors/fences, decision coverage and no runtime
diff. Evidence: FRESH documentation/static checks on a WINDOWS_NATIVE host;
not native behavior acceptance or independent review. Runtime/AHK/native/GUI/
database suites are NOT RUN because CP-00 changes documentation only. No
operational database validity claim. Remaining acquisition races, native layout/
AltGr/RDP/app collisions, metadata policy and secure profile delivery remain
explicit later validation gates. Stop at READY_FOR_REVIEW; no integration or CP-01.
