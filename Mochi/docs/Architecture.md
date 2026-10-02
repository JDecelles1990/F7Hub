# Mochi architecture

**Status:** Proposed design derived from the [accepted MVP baseline](Mochi_Luna_Light_MVP_Specification.md). No pet runtime or integration is implemented.

Read [Mochi AGENTS.md](../AGENTS.md) and [F7Hub's system architecture](../../Docs/06_SystemArchitecture.md) before implementation. This document organizes existing intent; it does not approve a renderer, provider or IPC contract.

## Existing implementation

`src/main.py` prints a message. The `core`, `services`, `integrations`, `ui` and test packages are empty. Initial settings exist, but there is no loader. `config/guide.json` is empty. Imported artwork is available through the [existing asset layout](FileOrganization.md); generation reports are historical evidence.

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

- Pet renderer and packaging, while retaining PySide6 as F7Hub's primary GUI. Any additional framework/process requires architectural review.
- Exact supported checkout/window/control identities, recognition confidence and a non-conflicting invocation mechanism.
- Guide schema, settings validation and actual frame/state mapping.
- Whether a new communication boundary is needed; define and review it before implementation.
- Luna provider/API, authentication, credential storage, retention terms and permitted payload policy.

These remain unresolved. No code, settings, source files or deployed behavior are changed by this design. Use the [Roadmap](Roadmap.md) to scope and validate each separately authorized step.
