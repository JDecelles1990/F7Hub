# Mochi local control protocol v1

Slice 002 implementation candidate, independent review pending. The protocol carries only runtime control metadata; it never carries business/database data, secrets, paths, executable text or PowerShell. Same-user processes are inside this local control boundary; endpoint naming is not authentication.

## Identity and lifetime

Normalize and resolve the checkout root, applying Windows case normalization, then SHA-256 its UTF-8 path to form a 64-character checkout ID. Use it consistently in endpoint and lock names and every request/snapshot. Lock storage is the current user's Qt GenericCacheLocation/F7Hub/Mochi directory; endpoint names also include a digest of that user cache location. Configure QLocalServer.UserAccessOption before listen. Every renderer route retains the same QLockFile, setStaleLockTime(0), tryLock(0), before endpoint creation or display. A failed acquisition returns unavailable (exit 2), never removes a contended lock or displays another pet.

F7Hub owns the persistent gateway/controller, session ID, greeting-consumed flag and automatic-start gate. Settings owns only a removable UI subscription. Detached launch success is not readiness; validated ATTACHED is readiness. Closing F7Hub closes its connection and leaves the pet running.

## Framing and limits

One strict UTF-8 JSON object per LF-terminated message. The 4096-byte serialized limit includes LF. CRLF input is accepted as JSON whitespace within the same limit. Duplicate JSON keys and nonfinite numeric constants are rejected.

| Resource | Limit |
|---|---:|
| Serialized message, including LF | 4096 bytes |
| Qt socket read buffer | 8192 bytes |
| Qt pending accepted connections | 8 |
| Application accepted sockets, validated or not | 8 |
| Complete requests queued per connection | 8 |
| Simultaneous runtime mutations | 1 |
| Incomplete-message deadline | 2 seconds from first partial byte; dribbled bytes do not extend it |
| Initial validated-attach deadline | 2 seconds |
| Command/queued-request deadline | 2 seconds |
| Overall startup/readiness attempt | 5 seconds |
| Outbound queued bytes per channel | 4096 × 8 |

The OS backlog is not a validated connection. Enforce accepted count separately. Overflow, invalid framing/schema or incomplete/initial-attach timeout closes that connection with no invalid request dispatch. Server queues have monotonic expiries checked before dispatch; disconnected or expired queued requests cannot mutate. No nested event loop or external work runs inside a mutation.

## Request

Exactly these fields:

```json
{"version":1,"request_id":"unique_id","controller_id":"controller_id","session_id":"session_id","checkout_id":"checkout_digest","command":"attach","payload":{"greeting_requested":true,"connection_generation":1}}
```

IDs are 1–64 ASCII letters, digits, underscores or hyphens. Version is integer 1 (booleans are rejected). Checkout must match the runtime. Commands are attach, status, show, hide, idle, wave, pause, resume and exit. Attach payload contains exactly the strict boolean greeting_requested and integer connection_generation in 1..2^53. Every other payload is an empty object. Missing/extra fields, wrong types, unknown commands and wrong identity are rejected before dispatch.

Successful attach binds controller/session IDs and generation to that connection. Other commands require the same registration. Unvalidated/transient sockets do not count as controllers. Each reconnect increments the gateway generation. Repeated greeting-bearing attaches are runtime-deduplicated before animation; ordinary attach never greets.

## Response

Exactly version, request_id, runtime_id, connection_generation, ok, outcome and snapshot. Snapshot contains exactly checkout_id, behavior, selected_animation, frame, visibility and paused. Behavior is STARTING/IDLE/WAVE/PAUSED/EXITING; selected animation IDLE/WAVE; visibility VISIBLE/HIDDEN; frame is an integer 0..127. No raw exceptions are returned.

Outcomes are ATTACHED, STATUS, STATE, CHANGED, UNCHANGED, INVALID_TRANSITION, NO_CONTROLLER and EXITING. `ok` is false for the final three. Unsolicited coherent state updates use request_id `event` and outcome STATE after validated registration. A gateway accepts them only on its current attached runtime/generation. Ordinary replies must match the pending request ID and current runtime/generation. Invalid input closes the channel rather than echoing untrusted identifiers or diagnostics.

## Greeting, recovery and uncertainty

The application atomically consumes greeting eligibility before transmitting the first eligible attach request and never resets it within that F7Hub process. Missed delivery/acknowledgement, runtime restart, Settings reopening and runtime LRU eviction cannot renew it. A new F7Hub process gets a fresh session. The runtime records up to 16 consumed sessions before attempting animation, including ineligible greetings. It only greets visible IDLE pets, completing on actual WAVE frame wrap. User interruption invalidates its token. Manual Wave ignores application greeting consumption and loops indefinitely.

Hide requires a validated connected controller at execution. Final-controller loss restores hidden pets unless EXITING, preserving animation, frame and Pause and recovering position before display.

Lost mutation acknowledgement produces UNCERTAIN, never automatic replay. Gateway reconnects/attaches without launching and requests status. That observation does not replace the earlier uncertain mutation outcome. Exit acknowledgement means the runtime accepted the transition, not that process termination was independently proven. Endpoint disappearance alone never proves clean exit; inconclusive Exit remains UNCERTAIN. Native validation combines test-owned process handles and released lock evidence for terminal assertions.

Automatic startup occurs only once after first display and is recorded before async scheduling. Every startup/retry is attach-first; each attempt launches at most once, with concurrent requests coalesced. Readiness timeout does not trigger another automatic launch. Explicit Start/Show may retry and clears obsolete reconciliation intent. A late/detached contender cannot render until it acquires the shared runtime lock. Manual exit does not reset the automatic-attempt gate.
