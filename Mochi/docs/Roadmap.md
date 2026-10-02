# Mochi roadmap

**Status:** Proposed sequence from the [MVP specification](Mochi_Luna_Light_MVP_Specification.md). No feature slice is started or authorized by this page.

Existing work consists of a scaffold, initial settings and imported artwork. The print-only entry point is not a pet runtime. Read [AGENTS.md](../AGENTS.md), [Architecture](Architecture.md) and the relevant F7Hub owner documents before choosing the smallest next slice.

| Step | Bounded outcome | Prerequisites / acceptance focus |
|---|---|---|
| 1. Asset and renderer decision | Inventory current frames and propose a rendering/packaging approach | Preserve originals; review framework/process implications; verify state/frame mapping |
| 2. Local pet shell | Display one animation, move cosmetically, show a short bubble, hide and exit | Validate settings/defaults and deterministic states; Windows checks for DPI, monitor bounds, focus and input interference |
| 3. Supported-window recognition | Identify only configured F7Hub/AltF7Hub windows locally | Verify actual host/control identities and shortcut conflicts; reject unknown/ambiguous screens; no capture or content extraction |
| 4. Reviewed offline hints | Hand-author a few guide entries and resolve them locally | Define/version schema; handle malformed/missing guide; offline and unknown-screen tests |
| 5. Optional development generator | Produce reviewable guide data from allowlisted source/docs | Prove containment, exclusions and provenance; no database/customer data; no automatic runtime activation |
| 6. Optional Luna question flow | Question → exact payload preview → explicit Send → advisory response | Confirm provider, API, secure credentials and permitted context; test no-send, timeout, failure and offline hints |
| 7. Affected workflow acceptance | Validate the implemented subset across supported apps | Isolated Windows evidence, privacy checks and applicable F7Hub/AltF7Hub regressions; independent review before integration |

This sequence does not assign slice numbers, dates, hotkeys, a renderer or a provider. State/configuration tests accompany the behavior they protect; validation and independent review apply to every implemented slice, not only the last row. Leave source and integration work pending until explicitly requested.

## Deferred beyond the MVP

- Selected-text, clipboard or ticket-note assistance: separate capture/filter/preview/send and data-policy design.
- F7Hub writes, automated input, troubleshooting execution or administration: separately approved service boundaries and technician control.
- AltF7Hub ticket-to-topic automation: already deferred by its owning subsystem; Mochi does not implement or authorize it.

Screenshots, OCR, background monitoring and arbitrary-app recognition are excluded from this MVP. A privacy flag or artwork state is not approval to add a capability.
