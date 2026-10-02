# AltF7Hub directory-specific agent instructions

## Scope and governing guidance

These instructions apply to `AutoHotkey/Troubleshooting_Sections/**` and tasks
elsewhere that directly affect AltF7Hub integration, including the shared host,
Python launch boundary and tests. Read this file explicitly from repository-root
sessions as well as sessions within the directory.

Follow [root AGENTS.md](../../AGENTS.md), its documentation authority order, and
the applicable [vertical-slice-delivery](../../.agents/skills/vertical-slice-delivery/SKILL.md)
gates. Repository-wide Git, lifecycle, security and authorization policies remain
with those owners. This file specializes subsystem obligations; it MUST NOT
weaken higher-level safety or review requirements and grants no execution,
staging, commit or integration authority. Consult task-relevant canonical
documentation using the routing below before changing behavior.

## Shared host and request boundary

Preserve the existing ownership:

- `AutoHotkey/F7Hub.ahk` owns the persistent shared host and F7, Alt+F7 and scoped
  hotkey integration.
- `GuideHost.ahk` initializes the explicit guide data directory, settings, topics,
  native callbacks, readiness endpoint and pending preference flush.
- `GuideCore.ahk` owns guide/editor GUI, topic handling, navigation, Rich Edit
  formatting, preferences and file-save/recovery behavior.
- `GuideRequest.ahk` and `Troubleshooting_Quick_Guide.ahk` implement the bounded,
  checkout-specific request bridge and short-lived standalone client.

Keep `MainWindow → ServiceTaskRunner → AltF7HubService → WindowsAltF7HubGateway
→ fixed request client → shared AHK host`. Preserve show/focus semantics and
workspace, ticket and editor drafts. Do not duplicate host/launch ownership,
create a second persistent guide, or broaden IPC without approved scope. The
guide displays reference notes; ticket-to-topic automation remains deferred.

A host may survive or complete presentation after client timeout. Preserve
unconfirmed-request reporting and visible-target confirmation; a dispatched
request MUST NOT trigger an automatic second send or toggle. Retain the guarded
pre-dispatch keyboard fallback and held-modifier exclusions.

## Local, protected and generated state

Before modifying, cleaning or staging, classify actual paths by tracking,
provenance, paired content and authorized scope. Tracking alone does not make
authored data disposable; generated origin alone does not authorize deletion.

- `GuideSettings.ini` is optional user preference/protected local state because
  built-in defaults exist. Preserve existing bytes by default; do not reset or
  commit it merely to reproduce local appearance.
- Topic `.txt` files may be versioned authored content and may change during
  ordinary guide use. Preserve unrelated user edits.
- `*.styles.ini` is context-dependent: versioned metadata or generated/user
  state. Inspect each sidecar with its topic; never apply a blanket stage/delete
  rule or regenerate it merely for a clean worktree.
- Preserve `Backups/**`; replacement or deletion requires task authorization.
- Preserve existing `Tests/Evidence/**` as historical evidence, not a disposable
  output directory. Prior captures do not establish current validation.
- Inspect `.tmp`, `.rollback` and formatting recovery copies before cleanup;
  they may contain the only usable data.

Read maintenance utilities and test harnesses for their actual writes and
process behavior before running them. Backups and evidence are not topic inputs.

## Topic text and metadata

When editing existing topics, preserve UTF-8 encoding, the existing BOM and
newline convention per file, authored blank lines, and first-line title/body
structure. Do not impose a universal line-width limit. Retain keyword-reminder
style and personal-note meaning without inventing interview achievements.

Preserve stable IDs, legacy filename/English-content mappings, optional
shortcuts, reserved letters and collision handling across active and archived
topics. Keep applicable identity/formatting sidecars paired when copying or
moving topics. Scan only direct topic files and `Archive` for the library.

Distinguish semantic content changes from byte-only formatting changes; either
can matter to candidate identity. Do not normalize unrelated files opportunistically.

## Formatting and save safety

Preserve settings/sidecar UTF-16 INI compatibility, format-version handling,
normalized-body fingerprints, and Rich Edit UTF-16 range coordinates with one
character per normalized line break. Incompatible fingerprints invalidate
personal ranges on load while automatic headings remain available.

Retain stale-editor and stale-selection guards, preparation of both topic and
metadata files before replacement, paired replacement and rollback behavior.
Keep unsaved editor content available after save failure and identify retained
recovery copies when rollback fails. Preserve native text undo and formatting
precedence. Do not rewrite these mechanisms unnecessarily; consult the README
and relevant `GuideCore.ahk` functions first.

## Navigation, hotkeys and appearance

Preserve intended notes/list focus scope, modifier exclusions, native editor
input, topic/title/body synchronization, and documented wrap, filter and archive
semantics. Search, sliders, buttons and dialogs must retain intended native input.

Accepted legitimate arrow-repeat input MUST remain accounted for; do not discard
it through arbitrary debounce. Logical navigation may be separated from
expensive rendering, with redundant painting coalesced, without queuing future
moves. Validate key release and absence of trailing navigation when relevant.

Preserve shared guide/editor opacity, preference bounds, pending-save behavior
and exit-time flushing of pending changes only. Include affected F7 regressions
when shared-host behavior changes.

## Native validation safety

Before authorized native AHK automation involving repeated input, held keys,
timers, loops, dialogs or persistent processes, agents MUST define:

1. Finite event/work limits and bounded cadence where relevant.
2. A whole-run timeout and deterministic termination.
3. Release of every injected key/modifier, including failure paths.
4. Identification and cleanup of test-owned processes and fixtures.
5. Recovery if normal termination fails.

A potentially blocking native operation MUST NOT rely solely on an in-process
AHK timer. Use an external supervisor or another termination mechanism effective
when callbacks block. On timeout or suspected looping, STOP and inspect surviving
processes/state before retrying; do not repeatedly relaunch a stuck harness.

Identify host/client PIDs and checkout paths, including recovery when startup
fails before normal PID capture. Do not terminate installed/Startup guides or
unrelated AHK processes. Confirm children exited before deleting fixtures.
Prefer isolated copies of mutable topics, `Archive`, settings and sidecars;
exclude backups/historical evidence unless explicitly needed as fixtures.
Generate fresh captures/logs outside historical evidence locations unless
specifically authorized otherwise.

Keep parser/static validation, mocked Python integration, injected native input
and physical/manual acceptance claims distinct. Direct function calls alone do
not establish behavior through hotkey or native-message paths.

## Candidate versus runtime drift

Compare candidate identity using authorized path inventory, base, relevant Git
identities and raw hashes where byte preservation matters, following the delivery
skill. Separately compare local/user settings, generated sidecars, backups,
historical evidence and authored topic changes outside candidate scope.

The cause of a change does not determine drift classification. Runtime/manual
edits to a candidate topic remain candidate drift; generated files outside its
inventory may instead be local state. Establish origin from evidence and status
from scope and actual bytes, never filename guesses.

## Documentation routing

Use [Docs/19_DocumentationIndex.md](../../Docs/19_DocumentationIndex.md) and the
minimum relevant owners; update only documentation affected by authorized changes.

- Guide behavior/content: [local README](README.md).
- Keyboard workflows: [Docs/04_UserWorkflows.md](../../Docs/04_UserWorkflows.md).
- Shared host/messages/F7: [Docs/11_AHKArchitecture.md](../../Docs/11_AHKArchitecture.md).
- Library/settings/evidence: [Docs/10_FolderStructure.md](../../Docs/10_FolderStructure.md).
- Python action/service/gateway: [Docs/05_GUI.md](../../Docs/05_GUI.md),
  [Docs/06_SystemArchitecture.md](../../Docs/06_SystemArchitecture.md) and
  [Docs/13_PythonArchitecture.md](../../Docs/13_PythonArchitecture.md).
