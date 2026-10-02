# Mochi Luna Light agent instructions

## Scope and authority

These instructions specialize work under `Mochi/**` and work elsewhere that
directly affects Mochi. Read them explicitly from repository-root sessions.
Follow [root AGENTS.md](../AGENTS.md), the [documentation index](../Docs/19_DocumentationIndex.md)
and applicable [vertical-slice-delivery gates](../.agents/skills/vertical-slice-delivery/SKILL.md).
They retain ownership of repository safety, lifecycle, approval and integration.
This file grants no implementation, capture, API, execution or Git authority.

Mochi belongs to the F7Hub repository at `C:\Dev\F7Hub\Mochi`. Its companion
window is a proposed feature within the modular monolith, not a separate
repository, application data store or automation authority. Runtime paths must
eventually be resolved from configuration or an explicit project root rather
than permanently depending on this development path.

## Read and inspect before changing

1. Read [README](README.md) and the [MVP specification](docs/Mochi_Luna_Light_MVP_Specification.md).
2. Select relevant [Architecture](docs/Architecture.md), [Roadmap](docs/Roadmap.md)
   and [File organization](docs/FileOrganization.md) sections.
3. Inspect actual source, settings, assets and tests; search existing F7Hub
   services and adapters before creating anything.
4. For F7Hub GUI, services or integration, consult canonical Docs 04, 05, 06 and
   13 as applicable. For Windows/AHK behavior, also consult Docs 10 and 11.
5. Before reading, analyzing, testing, changing or documenting AltF7Hub, read
   [its AGENTS.md](../AutoHotkey/Troubleshooting_Sections/AGENTS.md) and
   [README](../AutoHotkey/Troubleshooting_Sections/README.md).

The initial imported baseline had artwork, settings, a print-only `src/main.py`,
empty packages/tests and an empty `config/guide.json`. Slice 001 now implements
the standalone Python/PySide6 pet, settings validation, idle playback, dragging,
Pause/Resume/Exit and logging under `src/mochi`; see [README](README.md) for current
evidence and limitations. Slice 002 adds approved local startup/controls IPC as an implementation candidate. Screen recognition, hints, business-context adapters and Luna remain
**PLANNED**. Artwork QA remains historical evidence, separate from runtime
validation. Verify the live baseline again before future work.

The MVP is an accepted planning baseline. Its proposals are not implemented
contracts or authorization to start the next feature. If it conflicts with a
canonical architectural or security owner, report the conflict before deciding.

## Ownership and integration boundaries

Python/PySide6 retains F7Hub GUI, orchestration, application services and normal
SQLite access. Keep presentation → services → core → interfaces/adapters.
Core logic must not import GUI widgets, SQLite, Windows APIs, AHK or provider SDKs.
Services own validation, context selection and use cases; adapters own platform
or provider details. Reuse existing boundaries before adding new abstractions.

Mochi must not query SQLite from its UI, access the database directly to bypass
F7Hub services, or duplicate ticket, company, contact, knowledge, taxonomy or
technician-note state. A future F7Hub context adapter is read-only and disabled
by default. Write workflows require a separately approved slice, an existing
service boundary, validation, audit requirements, tests and independent review.

Slice 001 uses the explicitly approved standalone Python/PySide6 renderer.
Distribution packaging remains undecided. F7Hub's primary GUI remains PySide6.
Any further framework, process or IPC contract needs root architecture review
before implementation; this file does not approve it.

AHK v2 may own narrowly scoped desktop input and approved window metadata.
Preserve `AutoHotkey/F7Hub.ahk` as the F7/Alt+F7 shared host. Do not duplicate
AltF7Hub hosts, repurpose its fixed show/focus request for context transport,
or add hotkeys without inspecting existing bindings and focus/modifier scope.
The MVP's pet movement is cosmetic: no automatic clicks, typing, navigation,
PowerShell, browser control or administrative actions.

## MVP context and privacy

The MVP recognizes only explicitly supported F7Hub/AltF7Hub windows and resolves
reviewed local guide entries. Window Spy is a development inspection tool, not
a runtime navigation engine. Prefer stable, verified identifiers; process names
such as `python.exe` or `AutoHotkey64.exe` alone do not identify this checkout or
its screen. Inspect real launchers, host/window identities and controls before
writing recognition rules. Unknown or ambiguous screens must return safe manual
help instead of guessed instructions. Coordinates and titles are fallback
signals; titles may contain customer data and are not inherently safe to send.

Keep sensitive capabilities off. The MVP excludes screenshots, OCR, recording,
clipboard monitoring, keyboard/mouse logging, browser-history collection,
arbitrary window-content capture and background ticket extraction. Existing
privacy flags are initial data, not proof that enforcement is implemented.
Do not implement excluded features merely because a flag exists.

Future selected-text, clipboard or ticket-note assistance needs separate scope:
user-triggered collection, minimal context, local filtering, payload preview,
explicit Send and an approved data-handling policy. Secret-pattern detection
is an additional safeguard; it cannot guarantee that content is safe.
Do not collect or transmit passwords, tokens, keys or recovery codes.

## Local guide and development generator

Keep local guidance usable offline and independent of Luna availability.
Guide entries must come from verified workflows and identifiers, not inferred
screen names or invented shortcuts. The guide schema and loader are planned;
the empty `config/guide.json` is not a valid populated guide.

The [guide generator](tools/guide_generator/README.md) is also planned. It may
eventually read an explicit allowlist of source/documentation files and write
reviewable output only within approved Mochi paths. Exclude databases, live
topics/settings, ticket/customer data, clipboard data, credentials and unrelated
files. Record source revision, dirty-input identity when applicable, generator
version and selected sources. Generated output remains untrusted until reviewed.
Development-time repository analysis does not authorize runtime scanning.

## Luna and advisory output

Luna's provider, endpoint, authentication and data-retention terms are unresolved.
Keep provider details behind an adapter. Confirm those details and approved
credential storage before API implementation; do not invent an endpoint or
silently select a provider. Never persist plaintext credentials in normal
configuration, SQLite, `.env` files, logs or Git. Use the approved secure-storage
architecture when persistence is required.

No request occurs automatically. The technician invokes Ask Mochi, reviews the
exact minimal payload, and explicitly selects Send. The default proposed payload
contains an app identifier, known screen identifier, reviewed guide text and the
question. Exclude screenshots, raw screen text, clipboard, tickets and customer
data. Failed or unavailable requests must leave local guidance usable.

Separate instructions, approved guide context, user question and tool results
when constructing requests. Ticket text, clipboard, files, webpages and AI output
are untrusted data. AI may explain, suggest or draft; it cannot authorize or
execute actions. Any later action still requires normal F7Hub boundaries and
explicit technician control.

## Assets, configuration and local state

Follow [File organization](docs/FileOrganization.md). Preserve atlases and final
frames, previews, references, original decoded artwork, the workflow ZIP, prompts
and historical QA. Do not regenerate, delete, deduplicate, rename or rewrite their
provenance during unrelated development. Historical `/workspace/...` paths are
not runtime paths. Keep new validation separate from historical artwork evidence.

Animation states must be explicit and centralized; inventory real frames and
metadata before choosing mappings, rates or transitions. Do not embed binary
assets in source or assume artwork state names already define runtime behavior.
Future settings loading must validate types, bounds and malformed input, provide
safe defaults and preserve unrelated user settings. Configuration is not secret
storage. Do not run `tools/Initialize-Mochi.ps1` as a read-only check: inspect its
fixed root and filesystem writes first.

## Failure, performance and validation

Mochi failure must preserve F7Hub work and return to a stable state with useful
feedback. Log through existing application conventions without ticket bodies,
clipboard contents, screenshots, secrets or unnecessary personal data. Report
configuration, recognition, animation and provider failures honestly.

Keep GUI work on the GUI thread and slow work off its event loop. Prefer bounded,
event-driven behavior; avoid busy loops, unbounded history, repeated scans and
unsolicited API requests. Cancellation must distinguish completed actions from
unconfirmed or best-effort requests.

For an implemented slice, test applicable success/failure paths: deterministic
state transitions, animation selection, invalid settings, privacy disabled,
allowlist and unknown-screen recognition, offline hints, explicit payload/send,
adapter failures and preservation of F7Hub state. Use synthetic fixtures only.
Guide-generator tests must verify read/write containment, input exclusion,
provenance and safe replacement behavior. Do not add tests that merely restate
documentation or report historical artwork checks as fresh runtime results.

Native GUI changes need applicable Windows checks for transparency, topmost
behavior, focus/input interference, DPI, monitor bounds, animation, hide/exit,
and click-through if introduced. A screenshot from an isolated fixture does not
establish production privacy or physical input acceptance. Follow AltF7Hub's
bounded automation and process-recovery rules when touching its host: finite
inputs, external whole-run timeout, key release and test-owned process cleanup.

Report PASS / FAIL / NOT RUN / BLOCKED per required suite, with FRESH / RETAINED
provenance separately. Do not claim runtime verification without execution.

## Delivery and documentation

Inspect Git status, branch, HEAD, index and all untracked files before edits.
Preserve unrelated work, settings, authored topics, backups and evidence.
Define the smallest slice with objective, scope, exclusions, constraints,
acceptance criteria, validation and deliverables. Planning and documentation
tasks do not authorize source implementation. A roadmap does not start a slice.

Update affected owner documents only, after behavior is understood and validated.
Use the MVP for product scope, Architecture for proposed responsibilities,
Roadmap for future sequence, File organization for provenance and README for
entry points/current capability. Cross-subsystem behavior also needs applicable
canonical owner updates. Keep planned, implemented and verified labels separate.

Finish implementation with required evidence, affected documentation and an exact
candidate manifest at READY_FOR_REVIEW. Self-checks are not independent review;
approval is not integration authorization. Leave changes unstaged/uncommitted
unless the user explicitly authorizes staging or committing. No destructive Git
recovery or cleanup is implied.

Mochi should increase technician productivity while preserving technician control.
