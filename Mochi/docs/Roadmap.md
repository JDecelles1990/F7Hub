# Mochi roadmap

**Status:** Slice 001 desktop runtime implemented; independent review pending.
The broader sequence comes from the [MVP specification](Mochi_Luna_Light_MVP_Specification.md).
This page authorizes no next slice or integration.

Slice 001 implements settings/defaults, the existing six-frame idle loop,
transparent frameless/topmost rendering, dragging, Pause/Resume/Exit, explicit
states and bounded logging. The source baseline and imported artwork are preserved.
41 focused tests and native Windows checks pass; physical-user inputs and DPI
scales above 100% remain unverified. Read [AGENTS.md](../AGENTS.md),
[Architecture](Architecture.md) and relevant F7Hub owners before further work.

Recommended Slice 002 scope is only hide/show controls and one additional
reviewed animation. This recommendation is deferred; Slice 002 has not started.

| Step | Bounded outcome | Prerequisites / acceptance focus |
|---|---|---|
| 1. Asset and renderer decision | Slice 001 selects existing idle row 0 and PySide6 Widgets | Asset bytes preserved; source/module launch available; distribution packaging deferred |
| 2. Local pet shell | Slice 001 implements idle, drag, pause/resume and exit; hide/bubbles remain deferred | Settings/state tests and native 96-DPI checks pass; wider DPI/physical acceptance remain future validation |
| 3. Supported-window recognition | Identify only configured F7Hub/AltF7Hub windows locally | Verify actual host/control identities and shortcut conflicts; reject unknown/ambiguous screens; no capture or content extraction |
| 4. Reviewed offline hints | Hand-author a few guide entries and resolve them locally | Define/version schema; handle malformed/missing guide; offline and unknown-screen tests |
| 5. Optional development generator | Produce reviewable guide data from allowlisted source/docs | Prove containment, exclusions and provenance; no database/customer data; no automatic runtime activation |
| 6. Optional Luna question flow | Question → exact payload preview → explicit Send → advisory response | Confirm provider, API, secure credentials and permitted context; test no-send, timeout, failure and offline hints |
| 7. Affected workflow acceptance | Validate the implemented subset across supported apps | Isolated Windows evidence, privacy checks and applicable F7Hub/AltF7Hub regressions; independent review before integration |

Only the explicitly requested Slice 001 is implemented. Remaining rows assign
no slice numbers, dates, hotkeys or provider. Tests and independent review apply
to every slice; leave future source and integration work pending until requested.

## Deferred beyond the MVP

- Selected-text, clipboard or ticket-note assistance: separate capture/filter/preview/send and data-policy design.
- F7Hub writes, automated input, troubleshooting execution or administration: separately approved service boundaries and technician control.
- AltF7Hub ticket-to-topic automation: already deferred by its owning subsystem; Mochi does not implement or authorize it.

Screenshots, OCR, background monitoring and arbitrary-app recognition are excluded from this MVP. A privacy flag or artwork state is not approval to add a capability.
