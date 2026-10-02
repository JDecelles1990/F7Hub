# Mochi architecture

**Status:** Slice 001 integrated and closed with nonblocking notes. Slice 002 local control implementation candidate is pending independent review. Broader MVP integrations remain proposed.

Read [Mochi AGENTS.md](../AGENTS.md) and [F7Hub's system architecture](../../Docs/06_SystemArchitecture.md) before changes. Slice 001 selects PySide6 Widgets and a
standalone entry point through its approved task; this document grants no provider
or IPC authority.

## Existing implementation

`src/main.py` is a thin launcher for the named `src/mochi` package. Initial empty
packages are preserved. `config/guide.json` remains empty. Imported artwork and
historical generation reports are preserved through the [existing layout](FileOrganization.md).

## Slice 001 runtime

| Component | Responsibility |
|---|---|
| `app.py`, `__main__.py` | Resolve installation root; configure logging; load settings/images before the event loop; compose and clean up the standalone Qt app |
| `core/config.py`, `core/logging.py` | Read-only type/bounds/path validation and safe defaults; one bounded process-local Mochi log handler |
| `pet/animation.py`, `pet/pet_state.py` | UI-independent immutable animation metadata and explicit state enum |
| `pet/animation_loader.py` | One directory discovery and one decode per frame through QtGui; typed safe failures; no presentation widgets |
| `services/pet_runtime.py` | STARTING → IDLE, IDLE ↔ PAUSED, active → EXITING; idempotent actions and frame wrap; no Qt dependency |
| `ui/pet_window.py` | Draw preloaded pixmaps; GUI-thread timer; dragging and Pause/Resume/Exit menu; no filesystem or configuration parsing |

Window construction selects Tool, FramelessWindowHint and configured
WindowStaysOnTopHint, with WA_TranslucentBackground. WA_ShowWithoutActivating avoids
startup focus theft; direct interaction can activate the window/menu. The
WindowDoesNotAcceptFocus flag is deliberately omitted because native Windows
validation showed it swallowed mouse input. No click-through or global input
hooks are present. The process owns no F7Hub business state, workers or subprocesses. Slice 002 adds only the reviewed local control IPC below.

The runtime loads only configured local PNG frames. It never interprets historical
artwork metadata as executable configuration. No screenshots, OS input injection,
capture or observation exist in runtime code; the external native validation
harness is test-only. Settings and artwork are never written by the runtime.
Runtime writes are limited to ignored Mochi logs.

## Proposed responsibilities

| Component | Responsibility | Boundary |
|---|---|---|
| Pet shell / UI | Display frames, cosmetic movement, hints, question/preview/send, hide and exit | No SQL, provider calls, capture or command execution |
| Behavior core | Explicit states, transitions and animation selection | Independent of UI, AHK, SQLite and provider SDKs |
| Context / guide service | Select supported identifiers and resolve reviewed local hints | Unknown/ambiguous screen returns manual help |
| Windows / AHK observer adapter | Approved active-window metadata for supported apps | No raw text, screenshot, clipboard or ticket collection |
| Optional F7Hub adapter | Approved read-only service interface if separately implemented | No direct database access or duplicated records |
| Luna adapter | Explicit approved payload request and bounded failure translation | No unsolicited requests or execution authority |
| Development guide generator | Allowlisted source/docs to reviewable guide output | Separate from runtime observation; writes only to approved Mochi paths |

Dependency direction remains UI → services → core → interfaces/adapters. Reuse F7Hub's current services and worker conventions where applicable. F7Hub retains primary PySide6 GUI, repositories and SQLite ownership; AHK v2 retains desktop integration. Slow observation/provider work must not block the GUI event loop.

## Proposed context flow

1. Identify an explicitly supported app/window locally through verified metadata.
2. Match stable identifiers against reviewed guide entries.
3. Show local guidance when requested, or a safe unknown-screen message.
4. For Ask Mochi only, assemble app ID, known screen ID, relevant guide text and the user's question.
5. Show the exact payload and wait for explicit Send before invoking the optional provider.
6. Present advisory output. If the provider fails, keep local hints and the technician's work available.

The MVP excludes screenshots, OCR, clipboard monitoring, ticket/customer-data extraction and automated input/actions. Window titles may contain sensitive text; prefer a known screen ID over transmitting observed titles. Provider output and external text remain untrusted data.

## F7Hub and AltF7Hub boundaries

AltF7Hub is hosted by the existing `AutoHotkey/F7Hub.ahk` process. Its Python action uses `MainWindow → ServiceTaskRunner → AltF7HubService → WindowsAltF7HubGateway → fixed request client → shared host`. This contract shows/focuses the guide; it does not expose ticket data, topic selection or a Mochi context endpoint.

Read [AltF7Hub AGENTS.md](../../AutoHotkey/Troubleshooting_Sections/AGENTS.md) and [README](../../AutoHotkey/Troubleshooting_Sections/README.md) before integration work. Preserve unsaved editors, workspace/ticket drafts, F7/Alt+F7 bindings, local topics, settings, sidecars and the existing host. Do not assume `python.exe` or `AutoHotkey64.exe` alone identifies F7Hub or AltF7Hub.

## Decisions required before the affected slice

- Distribution packaging beyond the approved standalone Python/PySide6 renderer.
  F7Hub remains the primary GUI; future framework/process/IPC changes require review.
- Exact supported checkout/window/control identities, recognition confidence and a non-conflicting invocation mechanism.
- Guide schema and context recognition. Settings and IDLE/WAVE playback are implemented for the approved local slices.
- Any communication boundary beyond Slice 002's reviewed local controls requires separate review.
- Luna provider/API, authentication, credential storage, retention terms and permitted payload policy.

These later decisions remain unresolved. Use the [Roadmap](Roadmap.md) to scope
and validate each separately authorized step; Slice 001 implements only its
approved local desktop runtime.

## Slice 002 local controls

F7Hub owns MochiService → MochiGateway and its persistent asynchronous local socket for its application session. Settings only subscribes. The renderer's LocalController validates and registers controllers before dispatching commands through PetRuntime and PetWindow. Same-user local-server ACLs and a per-user/per-checkout lifetime QLockFile protect startup. Every script/module route uses the same lock. Singletons are rendered only after lock acquisition; contention exits unavailable without stealing the lock.

Application session greeting consumption happens atomically before the first greeting-bearing attach. Failure may miss a greeting, never renew it. Runtime eligibility requires visible Idle; its consumed-session LRU is defense-in-depth. Greeting runs one actual four-frame WAVE cycle and returns to IDLE, unless interrupted. Manual WAVE loops indefinitely. Pause/Hide/Idle/Wave/Exit invalidate obsolete completion tokens; paused animation switching is rejected. Visibility does not replace behavior state. Show and final-controller recovery preserve state/frame and recover inaccessible positions against individual available screen rectangles.

`Python/f7hub/domain/mochi_protocol.py` is the shared pure wire schema; `infrastructure/mochi_channel.py` contains shared Qt channel/checkout identity primitives. Standalone Mochi resolves this checkout's Python directory without importing application bootstrap or database code. See [IPC protocol](IPC.md) for schemas, limits and failure handling. No ReactionController, preferences, AI, AHK or PowerShell action is included.
