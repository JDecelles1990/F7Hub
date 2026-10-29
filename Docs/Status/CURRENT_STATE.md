# F7Hub Current State

<a id="cp02-s4-current-state"></a>

## CP02-S4 — R1 focused clock/expiry correction (2026-10-29)

**READY_FOR_REREVIEW — implementer correction complete; independent rereview pending.**
This is the user-requested correction handoff, not independent approval or Git
integration. The original independent review remains **CHANGES_REQUIRED** for
aggregate `a9c66a8fa4a486955e6e1e1219e53c5cbba1fb2ec89fca5b396e4f0afa7dfa60`;
its R1 reproduction and report are preserved unchanged.

`ClipboardService.copy_selected` now compares each wall-clock sample with the
immediately preceding accepted sample throughout service, native-wait and
readback guards. Equal timestamps are valid; any backward movement fails closed
without a new tolerance. Existing monotonic lifetime/drift protections remain.
Each guard uses one validated post-read timestamp for every selected Item expiry;
exact expiry rejects. No database transaction spans native Clipboard operations.
Pre-replacement rejection leaves Clipboard unchanged; post-replacement rejection
retains the existing WRITTEN effect state and never retries.

Fresh implementer validation: six deterministic R1 tests PASS, including the
original .800/.900/.300 expiry reproduction, 13 rollback sampling boundaries,
equal/increasing clocks, native-wait expiry, different Item expiries and exact
expiry. A separate relevant service/repository/consent/GUI/capture/Paste Latest
regression campaign PASS 246/246; the six new cases are excluded from that count.
Native regression PASS 1/1 with actual Unicode Clipboard readback and QTest paste.
All processes exit 0 with zero failures/errors/skips. Synthetic fixtures and
native injected input are distinct from physical user acceptance, which remains
NOT RUN. Prior Clipboard MIME representations were restored from RAM under the
existing newer-sequence guard; no prior content was persisted.

Only the service, selected-copy database tests, this current-state record and
ChangeLog differ from the reviewed candidate. All other candidate paths retain
their reviewed bytes. The new manifest, full old/new drift matrix, test commands,
logs, input identities, preservation audit and independent rereview handoff are
outside the worktree under
`%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Clipboard-CP02-S4/r1-correction-20261029T1810Z`.
Rereview must rerun an independently controlled clock-regression probe against
the new manifest; implementer results do not close the independent R1 finding.

Carry forward N1: actual native test-host captures remain 1000x700 and 660x612,
DPR 1.0. The extra paste editor is part of that fixture; no production 500-pixel
fit is established. Physical keyboard/Narrator/alternate DPI/RDP remain NOT RUN.
SQLite/native atomicity and interruptible native-call budgets are not promised.
Candidate remains unstaged/uncommitted at the same approved base; no push, PR,
merge, canonical synchronization or adjacent slice is authorized here.

## CP02-S4 — original author implementation record (2026-10-29)

The following preserves the initial author readiness record. The independent
review subsequently required R1 changes; the correction status above is current.

**READY_FOR_REVIEW — author candidate, independent review pending.**
Explicit implementation authorization follows the completed read-only plan and
preflight. PR #121 is confirmed merged by regular merge at approved base
`8150dc7e139fee62a7121b3fd449d3e3c9d7de4d`. Its tree matches the inspected Source App
candidate; no architecture reinvestigation was needed. Earlier CP02-S3 and Paste
Latest candidate sections below remain historical snapshots.

Worktree: `C:/Dev/F7Hub-Clipboard-CP02-S4`; branch
`feature/clipboard-cp02-s4-copy-selected`; HEAD/base remain the approved merge.
Changes are unstaged and uncommitted. No push, PR or merge is authorized here.
The dirty canonical checkout, protected settings, existing worktrees/databases
and review checkpoints are preserved; no canonical synchronization was performed.

Implemented: stable Item/revision check state, Select All Visible, Clear Selection,
selected count, Copy Selected (N), asynchronous complete-text retrieval, fresh
all-or-nothing consent/privacy/retention validation and existing-writer output.
Logical Select column is visually first. Output follows displayed Item order,
uses exactly two newline characters between complete texts and excludes metadata.
Limits: 100 distinct Items and 65,536 combined UTF-8 bytes including separators.
Selection clears on refresh/replacement and accepted source/section/module
navigation; pending copy freezes checks and guards departure. Settings-only
composition and Setup navigation during ordinary Recent reads are preserved.

| Author evidence | Result / environment / provenance |
|---|---|
| Selected focused + affected regressions, final-01 | PASS 245/245; exit 0; no failures/errors/skips; FRESH Windows-host SYNTHETIC, Qt offscreen, isolated SQLite |
| Final GUI scope-preservation correction, final-gui-01 | PASS 63/63; exit 0; no skips; FRESH Windows-host SYNTHETIC; overlaps prior GUI cases |
| Native final, native-02 | PASS 1/1; exit 0; actual Windows Clipboard write/readback, native Qt editor paste via QTest Ctrl+V; deletion rejection leaves native sequence unchanged |
| Isolated database integrity | PASS: integrity_check = ok; foreign_key_check = zero; configured foreign_keys ON / busy_timeout 5000; no data/schema mutations from copying |
| Native visual inspection | Two captures inspected at actual 1000x700 and 660x612, DPR 1.0; leading checkboxes and action/count feedback visible; normal horizontal overflow for other fields at compact width |
| Physical user input / Narrator / alternate DPI / RDP | NOT RUN; native QTest evidence does not establish physical user acceptance |
| Independent review / integration | NOT RUN / PENDING separate gates |

Counts overlap and must not be added. The final GUI-only change preserves normal
Setup entry during read-only Recent loading; final-01's service/writer/capture
behavior is unchanged and final-gui-01 refreshes affected GUI/composition evidence.
Native test preservation restored prior MIME representations from RAM; prior
content never entered logs, screenshots or evidence files. This is observed
semantic restoration, not a claim of identical original native format ownership.

External evidence root: `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Clipboard-CP02-S4/implementation-20261029T170910Z`.
It contains the reproducible candidate manifest, input identities, per-attempt
logs/results, self-review, preservation checks and independent review handoff.
Original FAIL records remain intact: focused-01 (assessor caller + button inventory),
focused-02 (verified fixture polling starvation), regression-01 (Settings-only
model absence). Corrections and successful subsequent evidence are separate.

Remaining limits: no atomic transaction spans SQLite and Windows Clipboard;
changes after the final check remain possible. Native calls have soft budgets,
not enforced interruption. Partial/uncertain writes can change the Clipboard;
feedback preserves effect state and never retries automatically. Normal Clipboard
consumers/history/sync policy remain relevant despite retained exclusion markers.
[1B](../Planning/Clipboard/1B_AHK_Python_Clipboard_Capture_IPC_Quick_HUD_Architecture.md#cp02-s4-copy-selected-contract)
owns the narrow output contract; Win+Alt+C and Win+Alt+V retain their independent
existing contracts and byte-identical implementation files.

## CP02-S3 — Source App Provenance author handoff (2026-10-29)

**SOURCE_APP_PROVENANCE_READY_FOR_REVIEW** — lifecycle READY_FOR_REVIEW. Author
implementation, validation, documentation and final preservation reconciliation
are complete. Independent review and user-owned physical acceptance remain pending.

Candidate only in `C:/Dev/F7Hub-Clipboard-SourceAppProvenance-20261029`, branch
`feature/clipboard-source-app-provenance-20261029`, base/HEAD
`b049a56a88305d48cf64d813065efa5a9b96f3e5`. Unstaged and uncommitted;
independent review and user-owned physical acceptance remain pending.

FACT baseline: fresh remote main is `b049a56a88305d48cf64d813065efa5a9b96f3e5`,
the PR120 merge with the existing Win+Alt+C/V implementation. The older
Paste Latest integration-pending sections below are historical snapshots.
CP02-S3 is the documented unstarted successor to closed CP02-S1/S2; only this
request's bounded source-process path is implemented. CC-03 search is untouched.

The candidate carries a strictly bounded optional original-target basename from
the existing native safety query through ClipboardService and the authorized Event
transaction to Recent's new Source App column. The existing independent preference
defaults False; pre-acquisition preference and final consent/revision/field checks
prevent retroactive or late authorization. No title/full path/PID/HWND/URL/command
line is persisted. Existing exact-text deduplication, replay, append head and
latest-paste mechanics are preserved. Latest Event ID selects source, including NULL.

| Author evidence | Result / provenance |
|---|---|
| Focused provenance + offscreen GUI | FRESH PASS 74, exit0; Database fixture batching later verified by full Database suite |
| Full Database regression | FRESH PASS 664, exit0; fresh/upgraded SQLite integrity_check=ok; zero foreign-key violations |
| Synthetic capture/paste and release-cycle regression | FRESH PASS 198, exit0 after two existing synthetic adapters were updated for the typed acquisition |
| Affected integration selection | 70 distinct methods covered: 60 unchanged non-bootstrap passing executions plus fresh corrected bootstrap module10 PASS, exit0; separate hash-bound derived applicability record |
| Physical Windows acceptance and native layout | NOT RUN; user-owned single controlled session prepared externally |
| Independent review | NOT RUN; exact candidate handoff pending |

Initial focused run FAIL (missing PySide6 under default interpreter), initial
capture/paste regression FAIL (old synthetic adapters), and original integration
run FAIL (69/70 passed; one stale migration-count assertion) remain preserved.
The corrected environment reuses the existing F7Hub virtualenv, PySide6 6.11.2.
No unchanged full integration rerun was performed. Results identify tested candidate
aggregates, with later documentation changes separated from code/test inputs.

External evidence/checkpoint/manifest and physical procedure:
`%LOCALAPPDATA%/F7Hub/CodexCheckpoints/SourceAppProvenance-20261029/`.
The final candidate manifest is authoritative for exact path/content identity.
The canonical dirty checkout branch/HEAD/index/status and ordinary local file hashes
match the starting preservation record. Protected GuideSettings.ini/desktop.ini
remain pathname-only opaque state. Five pre-existing worktree directories changed
from available to missing during the task: ActiveSelectionCopy-20261028, HBR01,
HBR01N, NativeIPC-20261027 and PythonPasteLatest-20261028 (all under the
C:/Dev/F7Hub-Clipboard- prefix). Their registrations retain branch/HEAD but are now
prunable. The user subsequently confirmed, "Yes, I intentionally removed them."
The user further clarified that the folders were moved to another disk to free
space. This is USER-REPORTED INTENTIONAL RELOCATION and resolves the earlier unexplained
availability blocker; no move timestamp, destination or missing-folder byte preservation
is inferred. The original BLOCKED finding remains in the external historical
evidence. Fresh checks confirm canonical status/ordinary bytes and candidate
identity; this task did not remove, restore or prune those worktrees.
All candidate changes remain unstaged/uncommitted. Next gate: independent
read-only review. User-owned physical acceptance remains required before any
later integration; no staging, commit, publication or merge is authorized.

<a id="python-paste-latest-current-state"></a>

## Python Paste Latest — accepted feature candidate; integration pending (2026-10-29)

**Win+Alt+C is integrated through [PR #119](https://github.com/JDecelles1990/F7Hub/pull/119).
Win+Alt+V is implemented and functionally accepted in the isolated feature
worktree; it is not available on main through this candidate.** Worktree:
C:\Dev\F7Hub-Clipboard-PythonPasteLatest-20261028; branch:
feature/clipboard-python-paste-latest; base/HEAD:
2a659f351df764ddf7681781b2b647665ffb1035. The worktree remains unstaged and
uncommitted. Candidate integration is **PENDING**; a feature commit, push,
Draft PR and GitHub merge have **NOT BEEN PERFORMED**.

| Evidence / gate | Current result and provenance |
| --- | --- |
| Final independent code-review disposition | **APPROVED WITH NOTES**; final targeted write-cleanup review after the preceding source/correction reviews |
| Physical Test A — actual text insertion | **USER-REPORTED PHYSICAL PASS** |
| Physical Test B — Windows Clipboard independence | **USER-REPORTED PHYSICAL PASS** |
| Physical Test C — held-key duplicate prevention | **USER-REPORTED PHYSICAL PASS** |
| No stale-history fallback | **USER-REPORTED PHYSICAL PASS** |
| Existing Win+Alt+C, F7, Alt+F7 and Exit compatibility | **USER-REPORTED PHYSICAL PASS** |
| This five-document reconciliation | **READY FOR FOCUSED DOCUMENTATION REVIEW**; it is not additional code-review approval or integration authority |

The physical results are the user's reported outcomes. No execution timestamps,
screenshots, process-exit result or unreported sub-observations are inferred.
Earlier FAIL, CHANGES REQUIRED and NOT RUN records remain historical evidence.
The accepted 19-path candidate before this documentation delta was bound to
aggregate 1ac5b58ce9420e45a1211d211a776635b22950c80f24cc5c68a7b1ecb6fd0091;
the new documentation manifest must preserve all production/test identities.

The [1B current contract](../Planning/Clipboard/1B_AHK_Python_Clipboard_Capture_IPC_Quick_HUD_Architecture.md#python-paste-latest-current)
owns Python/ClipboardService responsibilities. The
[Python owner](../13_PythonArchitecture.md#python-paste-latest-accepted-candidate)
describes post-close verification, native cleanup and the observed-state,
non-atomic Windows paste limits. The existing
[GUI shortcut registry](../05_GUI.md#gui-registry-shortcuts) records the single
Win+Alt+V action. Functional evidence is retained externally under
%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Python-Paste-Latest/, notably
final-independent-review-20261029T033628Z and
write-cleanup-physical-retest-20261029T034801Z. The latest physical PASS reports
come from the user's controlled-integration/documentation requests.

**Historical checkpoint boundary:** the earlier Paste Latest sections dated
2026-10-28 below preserve their original status and outcomes. Their uses of
"Current disposition", review pending, physical NOT RUN or blocked describe
those earlier checkpoints and are superseded for current status by this section.

## Paste Latest exceptional readback cleanup - ready for targeted rereview (2026-10-28)

The latest independent outcome-propagation rereview returned CHANGES REQUIRED
for a raised read-lock CloseClipboard followed by target cleanup failure falsely
reporting UNCHANGED after the authorized write. The post-close verifier now
normalizes that exception into CLEANUP_FAILED / WRITTEN / NOT_SENT and retains
the original close exception as cause. Target cleanup preserves this typed
outcome and causal chain. False-close rejection and one close attempt remain.
Only the native effect source, its focused test module and affected owner docs
changed; no service, coordinator, Win+Alt+C, schema, AHK or IPC change.

Regression-first: FAIL 1/1, exit 1. Corrected native writer/exception checks:
PASS 59/59; affected diagnostic/GUI checks: PASS 31/31; both exit 0, zero
failures/errors/skips. These are author synthetic checks on Windows with
offscreen Qt and isolated SQLite, without real Clipboard writes or input.
Previous failures and review dispositions remain historical; earlier sections
retain their snapshot status. The existing Python heading links resolve through
an explicit compatibility anchor in the Python owner.

Current disposition: EXCEPTIONAL_CLEANUP_CORRECTED_READY_FOR_REREVIEW.
Independent targeted rereview is required; physical insertion is NOT RUN.
Candidate remains unstaged/uncommitted; no push, PR or merge.
Evidence: external Python-Paste-Latest/20261028T235514Z-post-close-verification/
exceptional-cleanup-correction-20261029T030411Z.

## Paste Latest outcome propagation correction - ready for targeted rereview (2026-10-28)

The prior post-close candidate received independent CHANGES REQUIRED for a
combined verification and target-cleanup failure reporting UNCHANGED after an
authorized write. The Python owner now propagates the existing PasteEffectError
Clipboard and dispatch outcomes before cleanup and retains the first fixed-code
error as safe cause when cleanup fails. No policy, coordinator, Win+Alt+C,
schema, AHK or IPC change was made. Regression-first FAIL 1/1 is preserved;
fresh focused synthetic validation PASS 76/76, exit 0, zero failures/errors/
skips, and a separate combined-failure probe PASSed with WRITTEN / NOT_SENT.
The superseded review records and user-reported physical failure remain intact.
Current disposition: OUTCOME_PROPAGATION_CORRECTED_READY_FOR_REREVIEW.
Independent targeted rereview and user-owned Notepad insertion are NOT RUN.
No staging, commit, push, PR or merge. Evidence: external
Python-Paste-Latest/20261028T235514Z-post-close-verification/
outcome-propagation-correction-20261028.

## Post-close Paste Latest correction — pre-rereview snapshot (2026-10-28)

The [Python owner](../13_PythonArchitecture.md#post-close-paste-latest-verification-correction--candidate-2026-10-28)
describes verified post-close exact Unicode/privacy-marker/owner checks before
establishing a stable dispatch baseline. Source policy, service, coordinator and
Win+Alt+C remain unchanged. There is no operation-specific marker; identical
same-owner semantic state cannot establish producer identity. Existing non-atomic
Windows limits remain explicit. Pre-fix FAIL 1/1 and the initial focused fixture
FAIL are preserved; corrected affected runs PASS 21 and 27 (overlapping), exit 0,
zero skips, with unchanged selected checks carried by a source-bound audit.
Independent targeted rereview and normal physical insertion were NOT RUN at this snapshot;
no integration. Evidence: Python-Paste-Latest/20261028T235514Z-post-close-verification.

## Native Clipboard sequence diagnostic — development candidate (2026-10-28)

Added the explicitly enabled, one-attempt S1/S2/S3 diagnostic described in
[Python architecture](../13_PythonArchitecture.md#native-clipboard-sequence-diagnostic--development-candidate-2026-10-28).
It reuses normal consent/source authorization and the actual writer, preserves
rejection, and always stops before Ctrl+V. No normal-mode correction was made.
Initial focused checks PASS 125/125; final affected diagnostic checks PASS 21/21
after a reporting-only refinement. Both exit 0, zero skips; overlapping counts.
The physical sequence diagnostic is NOT RUN / USER OWNED; Test A's original
CLIPBOARD_CHANGED failure and stopped B/C remain preserved. Integration blocked.
External manifest/results/handoff: Python-Paste-Latest/20261028T232238Z-native-sequence-diagnostic.

## C-to-V physical release regression — BLOCKED (2026-10-28)

Disposition `RELEASE_REGRESSION_BLOCKED`. The user reports that candidate
20db710ddec0089c8408db82e6feaa0bc20ab08f1046d48826023997a3c89e7b
still returned ADMISSION_RELEASE_REQUIRED after a successful C capture. The
previous 119 synthetic PASS results did not establish physical resolution.
Prior readiness below is historical and superseded by this failure.

Fresh import-only provenance matches the expected interpreter, checkout and
release-callback code; process metadata shows one matching runtime family
(the Windows venv launcher and its child). Past live imported module state is
NOT VERIFIED. No new failing production transition was reproduced, so no
additional state-machine workaround was made. Exact physical latch/event
states and first divergence remain NOT VERIFIED.

Necessary diagnostic instrumentation now retains one bounded C state record
in RAM and reports fixed state flags with V results, distinguishing an
unsignaled release, a signaled/unreconciled event, another pending operation,
completed worker awaiting drain, and sampled key state. A same-process launcher
pins imports and verifies loaded code against the manifest before application
startup. It writes content-free provenance metadata only; release state stays
in RAM. No Clipboard/input effect is added to diagnostic V.

FRESH WINDOWS_NATIVE / SYNTHETIC offscreen evidence: 111 focused tests PASS,
zero skips, exit 0, including timing permutations and consecutive C/V cycles.
This is diagnostic/invariant validation, not a reproduced fix or physical PASS.
New diagnostic physical execution is NOT RUN / USER OWNED. General paste and
integration remain blocked. External checkpoint:
`%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Python-Paste-Latest/20261028T220103Z-release-regression`.

## ADMISSION_RELEASE_REQUIRED correction — awaiting diagnostic retest (2026-10-28)

Disposition: `ADMISSION_RELEASE_CORRECTED_READY_FOR_RETEST`. General Paste
Latest remains CHANGES_REQUIRED; this is not review approval or physical paste
acceptance. User evidence against the previous diagnostic candidate: V after
C returned ADMISSION_RELEASE_REQUIRED, while V alone returned
TARGET_VALIDATED_AFTER_RELEASE, with Clipboard UNCHANGED, Ctrl+V NOT_SENT and
authorization NOT_REQUESTED. Exact physical timings were not supplied.

Confirmed synthetic defect: C worker observes full release between GUI timer
samples; V is down when the next GUI sample drains C completion, leaving the
old shared latch true. The correction preserves a per-press worker release
observation and reconciles it in poll/admission. Each accepted press reserves a
fresh Event; busy, actual-release and duplicate guards remain. No change to
target policy, authorization, source/consent/privacy rules or native effects.

FRESH author WINDOWS_NATIVE / SYNTHETIC offscreen evidence: pre-fix regression
FAIL 1/1 preserved; after relevant source correction, 119 focused checks PASS,
zero skips, exit 0. This covers both action orders, held repeats, new cycles,
cancellation/start failures/Exit, diagnostic no-effects, target policy and
existing authorization/latest-source fences. No automated native input or
physical retest. External checkpoint:
`%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Python-Paste-Latest/20261028T214052Z-release-correction`.
Next is one diagnostic V press after a user C capture in the isolated launcher;
normal paste physical testing follows only if target diagnosis succeeds. Prior
TARGET_UNAVAILABLE and original 4 PASS / 4 FAIL physical evidence remain open.
No staging, commit, push, PR or merge authority.

## Win+Alt+V target diagnostic — prepared for one physical test (2026-10-28)

Disposition: `TARGET_DIAGNOSTIC_READY_FOR_PHYSICAL_TEST` for the bounded
development diagnostic only. General Paste Latest remains CHANGES_REQUIRED
with the original user-reported physical 4 PASS / 4 FAIL preserved below.
The exact rejecting guard from the failed press remains NOT VERIFIED.

Source-checkout opt-in `F7HUB_DEV_PASTE_TARGET_DIAGNOSTIC=1` routes the same
Win+Alt+V event, foreground binding and worker through the existing target pin
and modifier-release checks. It reports fixed allowlisted branch/phase codes
and stops before service authorization, history retrieval, Windows Clipboard
access or Ctrl+V. Status contains no target identifiers, process details,
window titles, Clipboard text or tokens and is not persisted. Normal target
policy and Win+Alt+C behavior are preserved; no workaround is implemented.

FRESH author `WINDOWS_NATIVE / SYNTHETIC` offscreen checks: 90/90 PASS; after
adding two composed Qt/native-mock cases, 26/26 diagnostic checks PASS, zero
skips (overlapping suites). No automated real keyboard injection, native
physical press or general paste acceptance was run. A separate external
checkpoint provides a manifest-verified launcher using a new isolated acceptance
database and a single user-owned diagnostic procedure. Stop after that result;
no automatic retry. Candidate remains unstaged/uncommitted, without approval
or integration authority. Source and exact evidence are in the diagnostic
checkpoint under `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Python-Paste-Latest/20261028T211933Z-target-diagnostic`.

## Python Win+Alt+V Paste Latest — physical acceptance failed; changes required (2026-10-28)

User-approved Python implementation is present in isolated worktree
`C:\Dev\F7Hub-Clipboard-PythonPasteLatest-20261028`, branch
`feature/clipboard-python-paste-latest`, base/HEAD
`2a659f351df764ddf7681781b2b647665ffb1035` (merged PR #119).
Canonical checkout was safely fast-forwarded from PR #118 with external
before/after preservation checks; all pre-existing local state was preserved.
The candidate remains unstaged/uncommitted; no PR or integration is authorized.

Current [1B](../Planning/Clipboard/1B_AHK_Python_Clipboard_Capture_IPC_Quick_HUD_Architecture.md#python-paste-latest-current)
resolves Paste Latest ownership and supersedes historical AHK/Ctrl+Alt+V
recommendations for this operation. Existing append-head prepare/consume APIs
supply consent/privacy/source/replay authority. One Python worker owns capture
or paste, requires key release, binds/rechecks the original target and effects
one Clipboard write plus one Ctrl+V dispatch. Any unsaved/unavailable latest
session capture prevents fallback to an older saved Item. Output status is
content-free and distinguishes Clipboard mutation from dispatch. No AHK/IPC,
monitoring, migration, Quick Picker, GUI Registry or 1A/1C edits.

FRESH author validation on Windows with synthetic native effects / offscreen Qt:
**48/48 focused PASS**, exit 0; **193/193 affected regression PASS**, exit 0;
zero skips. After a narrow safe-feedback self-review correction, **45/45 affected
GUI/flow checks PASS**, exit 0, zero skips. These overlap and must not be added.
Unchanged service/gateway/database/lifecycle regression inputs are hash-compared
in the external applicability record. Regression includes a real
bootstrapped F7Hub owner/service with fake Clipboard/input and isolated SQLite;
source/consent/replay races, capture compatibility, lifecycle and integrity checks.
Isolated integrity_check=ok; foreign_key_check=zero violations. Full regression
and unrelated native campaigns NOT RUN.

The first run remains FAIL: default interpreter lacked PySide6 and an expiry
fixture violated a CHECK. The existing project venv and valid synthetic clock
advance corrected those causes before the successful run. Native-01 remains
**FAIL (2/2)**: Win+Alt+C registration collision prevented native routing checks.
After the user closed the conflicting applications, a fresh process inventory
found no matching runtime processes; native-02 **2/2 PASS**, exit 0. Following
the feedback correction, native-final **2/2 PASS**, exit 0, zero skips, on final
Python inputs. Those checks register both real hotkeys, route posted WM_HOTKEY
through Qt and unregister/re-register; no real Clipboard read/write or keyboard
injection. This is native registration evidence, not actual paste acceptance.
Physical Win+Alt+V Notepad acceptance is now **USER-REPORTED PHYSICAL FAIL**: four checks PASS and four FAIL. The first failed paste reported `TARGET_UNAVAILABLE`, `Clipboard: UNCHANGED`, and `Ctrl+V: NOT_SENT` while Notepad B was visibly active. The exact symptoms of the other three failed checks were not supplied; they may depend on the first failure. A read-only native pin against the currently running Notepad process passed from both main and worker threads, so the failing target gate within the original press remains **NOT VERIFIED**. No product correction or native physical retest has occurred. The original acceptance placeholder and author test reports remain preserved in the external checkpoint.

External evidence, test-impact matrix, failed/successful logs, candidate manifest,
implementation report and independent-review handoff are under
`%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Python-Paste-Latest/20261028T175234Z`.
Disposition: `PASTE_LATEST_BLOCKED` / `CHANGES_REQUIRED`. The original candidate aggregate `b01a0787604f122ad62bb0e090e416c164636178ab0bb92d7cdbe475f06b5835` remains historical author evidence; it is not ready for independent review or integration. The user-reported physical failure and this status correction require a new manifest. No staging, commit, PR or integration is authorized.

## Win+Alt+C integration and physical acceptance reconciliation (2026-10-28)

Current FACT: PR #119 is merged at the baseline above and live GitHub main was
verified at that SHA. Current user evidence: **USER-REPORTED PHYSICAL PASS 8/8**
for Python Win+Alt+C. No timestamps or individual observations were supplied here.
The earlier candidate section below is preserved as HISTORICAL author evidence;
its not-integrated / physical-pending statements describe that earlier point.
They do not negate current integration or user-reported acceptance.

## Python Win+Alt+C active selection capture — candidate (2026-10-28)

**Contract correction: PASS.** Python ownership is explicitly USER APPROVED in
[current 1B](../Planning/Clipboard/1B_AHK_Python_Clipboard_Capture_IPC_Quick_HUD_Architecture.md#python-selection-current).
The current contract supersedes conflicting Sections 15/16, AHK snapshot/selection
ownership, no-synthesis and capture-current hotkey recommendations. Earlier blocked
candidate text remains labelled historical; its bytes and checkpoints are preserved.
Capture Current remains separate. No unresolved ownership decision remains.

Candidate worktree: `C:\Dev\F7Hub-Clipboard-ActiveSelectionCopy-20261028`;
branch `feature/clipboard-active-selection-copy`; base/HEAD
`c3db85fb2e1d72cc3dd3baed7cf48a7443a74cd1`. Unstaged/uncommitted; not integrated.
The canonical checkout and unrelated worktrees are preserved.

Python registers the hotkey in the existing lifecycle, actively copies the
selection off the GUI thread, requires a fresh stable eligible Unicode result,
and routes it through ClipboardService. No prior manual Ctrl+C or old-content
fallback. Existing consent gates allow durable Recent only when affirmative
consent existed before copying and still matches at admission/commit. Otherwise
eligible text is shown transiently in the existing status bar with a not-saved
label. Failed acquisition and rejected privacy create no successful capture record.
Existing Item/Event/receipt and SQLite integrity rules remain unchanged.

FRESH author evidence: first focused run **83 PASS**, exit 0. After narrow
self-review changes, affected checks **41 PASS**, exit 0; these overlap the first
run and are not additive. The first run's 24 lifecycle and 23 consent checks remain
applicable after input verification. Bounded native hotkey registration, posted
WM_HOTKEY dispatch through Qt and unregister/re-registration **1 PASS**, exit 0
against the updated adapter. This native check performed no SendInput or real
Clipboard read. Synthetic full F7Hub bootstrap receives the expected fresh-text
projection using a fake native adapter. Real service tests use isolated SQLite;
integrity_check=ok, foreign_key_check=zero violations.

Focused Setup GUI/integration checks after passive-feedback correction: **34 PASS**,
exit 0. No interactive controls or audited registry rows changed.

The user's earlier standalone proof is USER-REPORTED PHYSICAL PASS only.
In-F7Hub physical Notepad acceptance, actual Ctrl+C/read compatibility and physical
F7/Alt+F7 regression are NOT RUN / user-owned. In-process delayed native rendering
has no hard external deadline; Exit waits for actual drain and late results are
rejected. Full regression, historical native campaigns and independent review
are NOT RUN. See [Python architecture](../13_PythonArchitecture.md) for limits.

Evidence/checkpoint/manifest:
`%LOCALAPPDATA%/F7Hub/CodexCheckpoints/PythonActiveCopy/20261028T165348Z`.
Final handoff validation and exact path identity are in `implementation-report.md`
and `candidate-manifest.json`; this section does not self-approve the candidate.

## Native IPC — retained-process context candidate (2026-10-27)

Implementation disposition: **READY_FOR_REVIEW**, awaiting independent review.

Base: PR #117 merge `d4762afe003f353946c520ad746185c981d4b5df`.
Candidate: `C:\Dev\F7Hub-Clipboard-NativeIPC-20261027`, branch
`feature/clipboard-native-ipc-prerequisite-20261027`; unstaged/uncommitted.
Canonical synchronization was not repeated. Approval reconciliation freshly
verified both HBR-01/HBR-01N independent **APPROVED WITH NOTES** dispositions,
their exact PR integration identities and absence of blocking findings. PR #117's
reviewed eight-line sole-I/O-owner retention addition explains the session blob
change from PR #116. Final integrated source matches the authorized PR #117 blobs.

The selected prerequisite observes the adopted 112-byte process context from
original retained Windows process handles, as described in
[Python architecture](../13_PythonArchitecture.md). It verifies PID/creation,
liveness, same token session/user/logon SID and exact medium integrity, closes
only temporary token handles and fails closed on incomplete or mismatched data.
It does not establish trusted launch/enrollment or pipe authentication, and has
no production importer. No connected status exchange is delivered.

FRESH author validation: **20 PASS**, WINDOWS_PYTHON_SYNTHETIC; **3 PASS**,
WINDOWS_NATIVE process/token APIs with short-lived test-owned Python children.
Both commands exited 0, with zero failures/errors/skips. Native tests cover exact
context, wrong creation identity and exited retained process; they do not exercise
AHK, enrollment, IPC, handle transfer, native I/O or 500-ms feasibility. Historical
security campaigns and full application regression were NOT RUN. Production/test
identities and completion logs are bound in the external checkpoint:
`%LOCALAPPDATA%/F7Hub/CodexCheckpoints/NativeIPC/implementation-20261027T2303450737851Z`.
Independent review is NOT RUN. Host launch, pipe peer checks, control/data I/O,
status delivery, lifecycle composition and all Clipboard effects remain deferred.
No GUI Registry, AHK, schema, consent, hotkey or tray/Exit change is included.

## HBR-01 / HBR-01N — integrated dormant prerequisites (2026-10-27)

PR #116 merged the independently approved two-file HBR-01 policy core at
`63de01184d084d17556435ab888c587f6fdcf0ca`. PR #117 merged the independently
approved six-file HBR-01N I/O gate at `d4762afe003f353946c520ad746185c981d4b5df`.
These are integrated dormant prerequisites; neither activates native IPC or
Clipboard behavior. The previously recorded pre-review/pre-merge candidate
status is historical. The new checkpoint contains the verified approval and
integration evidence references; the old campaigns were not rerun.

Historical HBR-01N validation remains separate: 26 final gate tests, 56 session
and six codec tests across author executions, and 33 independent synthetic
checks (26 gate plus seven probes). Its original 86-test wrapper FAIL remains
preserved beside the separate hash-bound derived assessment; no original result
is rewritten. Native interoperability and full 500-ms feasibility remain
NOT RUN / NOT VERIFIED. Retain the authoritative policy and sole I/O gate for
their entire fixed-offer lifetime, including replay/resend state and quarantine.

## F7 physical-failure replacement — READY_FOR_USER_SMOKE_TEST (2026-10-26)

Current uncommitted replacement on `fix/canonical-install-20261026`, HEAD/base
`c77bc5511887545a26974dfe2fedd86c069b7581`. The first candidate FAILED physical
X/F7 restoration. Tray Open repairs the white window; the user clarified that
tray Open followed by guarded Exit physically PASS. No general Exit defect is
inferred. Exact event/callback timing in the physical failure remains NOT VERIFIED.

The replacement removes incidental Expose notification eligibility. The existing
Qt timer checks the retained HWND's native visibility every 100 ms while hidden
and restores through Qt without foreground activation, returning to 1000 ms when
restored. Native queries are read-only, with no new message, IPC endpoint or
window-command contract. AHK production sources and the database are unchanged.

Fresh validation: 24 lifecycle, three native-query and four startup tests PASS;
34 native fixture stages PASS, including native X/F7/X/F7/tray Open, true widget
and child visibility with repair notifications suppressed, retained drafts
without text logging, HOLD focus/release, no duplicate and real guard cancellation
followed by natural accepted exit 0. A corrected regression first FAILS the old
candidate with responsive Qt heartbeat and no repair callback. A registered-host
synthetic diagnostic did not reproduce the physical failure; that does not erase
the user's physical FAIL. Replacement physical acceptance and independent review
remain NOT RUN. No commit, push, merge or integration readiness is claimed.

Evidence and prior candidate/physical failure records:
`%LOCALAPPDATA%/F7Hub/CodexCheckpoints/F7-Restore-Physical-Correction-20261027T000152Z`
(directory timestamp is UTC). All worktrees, unrelated files and protected settings
are preserved. Restart through normal Exit before the one new physical smoke test.

## Historical first F7 correction — physical FAIL (2026-10-26)

The earlier readiness and automated results below are preserved as history. The
later physical X/F7 failure supersedes its user-smoke readiness disposition.

Local candidate on `fix/canonical-install-20261026`, HEAD/base
`c77bc5511887545a26974dfe2fedd86c069b7581`. The integrated installation and all
Clipboard worktrees are preserved. The production correction is confined to
`ApplicationLifecycle`; AHK launcher/controller/follower, database and migration
inputs are unchanged. No new IPC contract is introduced.

An isolated Windows fixture demonstrated a fully white native client area with
Qt and child visibility still false after the existing native show operation;
tray Open restored Qt state and rendering. Fresh validation of the correction:
23 lifecycle tests and four startup tests PASS; 25 native synthetic fixture
stages PASS, including cold TAP, X-hide, tray Open, repeated TAP/HOLD restore,
maximized-hidden and minimized HOLD, no duplicate window, cancelled Exit and
accepted natural exit 0. The existing six-geometry/3600-tick follower regression
also PASS. These are synthetic/automated native results, not physical acceptance.

Physical user smoke and independent review are pending. An already running
application must exit normally and restart to load the local Python correction;
the unchanged AHK host needs no reload. No commit, push or merge was performed.
Evidence, original failed attempts, candidate identity and review handoff are in
`%LOCALAPPDATA%/F7Hub/CodexCheckpoints/F7-Restore-White-20261026T233806Z`.

## LIFE-01 — INTEGRATED / PASS (2026-10-25)

This is the authoritative current LIFE-01 summary. The recovery and candidate
sections below are historical snapshots; their blocked states and failed attempts
remain evidence of those executions, not the current integration disposition.

[PR #112](https://github.com/JDecelles1990/F7Hub/pull/112) integrated the exact
independently reviewed implementation with disposition **APPROVED WITH NOTES**:

- Implementation commit: `a89fde20d5da281dd0109a4ed1a6868ed570db30`.
- Merge commit and verified remote main: `041246b288c584f807dd849e450e3ad025f5a93d`.
- Reviewed implementation base: `b779d0bb0589b569b1d75a0bcb445dfaee967243`.
- Reviewed 18-path aggregate SHA-256:
  `4ffe3d053bc321f27f48b59eb3f50a87a38c802bd529754e8c5ee17be3673c59`.

The validated lifecycle retains the same MainWindow and drafts on X; tray Open
restores it. Unavailable or lost tray recovery keeps or restores a visible window.
Main-window Exit, tray Exit and Quit share pending-operation and draft guards.
Cancel preserves drafts and state; accepted Exit performs idempotent existing
cleanup and normal Qt termination. One Python-owned coordinator runs in the
existing process. No automatic Clipboard monitoring or acquisition is activated;
RAM-01B is **NOT STARTED** and requires separate authorization and validation.

| Evidence | Provenance and result |
| --- | --- |
| Independent lifecycle tests | FRESH in the independent implementation review: **20 PASS**, exit 0 |
| Independent selected integration tests | FRESH in that review: **10 PASS**, exit 0 |
| Cumulative affected-method coverage | Independently verified RETAINED **149/149** passing methods; not a single suite PASS |
| Historical 149-method suite | **INCOMPLETE**; original supervised execution preserved |
| Historical 577-method suite | **FAIL**; original 11 failures and exit 1 preserved |
| Completed 578-method full-suite PASS | **NOT VERIFIED**; no such completed PASS established |
| Native physical acceptance | **PASS** through independently approved offline reassessment of RETAINED physical execution |
| Original physical adjudication | **FAIL / EVENT_ORDER**, preserved unchanged as a separate record |
| Origins of `0x8001010D` and `0xC000041D` | **NOT VERIFIED**; neither exception is characterized as harmless or resolved |
| GitHub CI | **NO CHECKS REPORTED**; no CI PASS claimed |

The offline reassessment used the saved physical selection, unique action
dispatch, accepted guard, completed cleanup, non-forced quit, natural process
exit 0 and no-survivor evidence. Independent approval of the corrected adjudicator
preceded reassessment. It did not repeat physical input or overwrite the original
EVENT_ORDER verdict. Earlier failed hidden-window tray Exit attempts also remain
failed records. Retained native Open/restore and lost-tray recovery evidence is
separate from physical Exit acceptance. Alternate DPI remains NOT RUN. The review
tests and native executions are retained evidence for this documentation update;
no application tests or physical attempts were rerun for the synchronization.

All three original P3/nonblocking findings are retained:

- **P3-N1 — stale handoff metadata:** addressed by this four-owner documentation
  candidate; documentation review/publication remain separate from the completed
  implementation integration. The original finding and historical labels remain.
- **P3-N2 — native reliability, OPEN:** the origins, faulting module and relationship
  of `0x8001010D` and the earlier abnormal `0xC000041D` termination remain NOT VERIFIED.
  Further investigation needs separate native-diagnostic authorization.
- **P3-N3 — long-suite interaction, OPEN:** cumulative coverage does not establish
  monolithic suite behavior or explain the historical stall. Any bounded diagnostic
  requires separate authorization; old results must retain their original outcomes.

Source reports are retained under `%LOCALAPPDATA%/F7Hub/CodexCheckpoints`:
`LIFE-01-review-20261025/independent-review.md` and its bound
`review-decision.json`, plus
`LIFE-01-20261025/adjudicator-correction-20261025T230000Z/final-handoff.md` and
`offline-reassessment.result.json`. The integration handoff is retained in Codex
session `01a17558-cc39-74f3-9475-8abd76103e47`; PR #112 and current Git parent/tree
verification corroborate its merge facts. Approved architecture contracts remain
unchanged. Unrelated older subsystem statuses below have not been reconciled.

## Historical LIFE-01 recovery — IMPLEMENTATION_BLOCKED (2026-10-25)

Historical snapshot: the following recovery record is preserved as written.
The current integration and native-acceptance disposition is recorded above.

The existing unstaged, uncommitted candidate remains in
`C:\Dev\F7Hub-Clipboard-LIFE01` on
`feature/clipboard-life01-tray-lifecycle`, with HEAD/base
`b779d0bb0589b569b1d75a0bcb445dfaee967243`. Recovery reused this worktree and
preserved the canonical checkout and all original protected registrations.

The candidate adds one Python-owned tray coordinator, retained-window hide/Open,
shared guarded explicit Exit and idempotent existing shutdown cleanup. It adds
no Clipboard acquisition, monitoring, privacy rule, persistence or migration.

The required native gate remains incomplete. The latest retained
`native-tray-keyboard.result.json` reports FAIL waiting for accepted Exit from
the tray while the main window is hidden. The menu was observed visible and
owned foreground input; accepted shutdown and the tray Exit action signal were
not observed. Root cause is NOT VERIFIED. Earlier native successes do not fill
that gap. Recovery does not repeat native input without a demonstrated
correction. Physical hardware input and alternate DPI remain NOT RUN.

Recovery verifies saved focused/broad results and validates only the affected
fixtures once. That fresh regression reached its 480-second supervision limit
before completion; its suite outcome is INCOMPLETE / BLOCKED, not PASS, and no
retry was made. Shutdown-intended fixture calls use explicit Exit, unrelated
integration fixtures suppress Mochi startup, and six migration-count assertions
match the unchanged 17-migration baseline. The speculative Script Catalog
worker-yield addition is excluded because a LIFE-01 scheduling requirement was
not demonstrated. Exact commands, final results, candidate manifest, ignored
path inventory and preservation comparison are in the external checkpoint
directory `LIFE-01-20261025/recovery-20261025T111350Z` under
`%LOCALAPPDATA%/F7Hub/CodexCheckpoints`.

Delivery lifecycle: BLOCKED with TESTING interrupted by the native acceptance
gap. Independent review and all Git integration operations remain pending.
The dated RAM-01A candidate records below are retained historical snapshots.

## Clipboard RAM-01A R1 — READY_FOR_INDEPENDENT_REREVIEW (2026-10-25)

RAM-01A is an unstaged, uncommitted implementation candidate on
`feature/clipboard-ram01a-volatile-history` in
`C:\Dev\F7Hub-Clipboard-RAM01A`, based on integrated RAM-00 merge
`56ef70e8122a79c3aa816383b6485320dd3a6405`. Independent rereview is pending;
no implementation approval, integration or production activation is claimed.

Independent review required R1: recoverable allocation failures during admission
construction escaped. The bounded correction catches only `MemoryError`, returns
`CAPACITY_OR_CLOCK_CHANGED` and prepares the result/replacement rows before
publication. Failed construction preserves live history and accounting; expiry,
generation fencing, cancellation and non-memory error propagation remain intact.
Fresh correction validation: **43 focused tests**, **41 affected regressions**
and **14 original reviewer probes PASS**, each exit 0, on the Windows host with
synthetic data. Reexecuted probes are implementation evidence, not independent
rereview. The original review artifacts remain unchanged.

The new pure Python `VolatileClipboardHistory` domain provides exact UTF-8
history, 100-entry/256-MiB accounted limits, 4-MiB per entry, 12-hour dual-clock
expiry, exact consecutive duplicate suppression, bounded previews and stale
reference/admission invalidation after Clear or disable. The default privacy
boundary denies admission; no production assessor or consumer is supplied.
Details and accounting ownership are in
[Python architecture](../13_PythonArchitecture.md#clipboard-ram-01a--volatile-history-domain-candidate-2026-10-25).

Initial author Windows-host synthetic validation: **32 RAM-01A Unit tests PASS** and
**41 existing privacy/manual-contract/database-boundary regressions PASS**,
Python 3.14.6, exit 0. The initial focused dependency failure was diagnosed:
the services package eagerly imports Ticket/SQLite. Consolidating RAM-01A in
the domain removed that dependency without changing existing exports. Failed
and corrected artifacts are retained externally. Portable domain evidence does
not establish native Clipboard or physical keyboard behavior; those tests are
NOT RUN and excluded from this slice.

The approved RAM-00 contract and protected historical evidence remain intact.
Hybrid B-01 remains IMPLEMENTATION_BLOCKED, integration deferred, physical
campaign closed and `NATIVE_ACCEPTANCE_VERIFIED=False`. LIFE-01, RAM-01B,
monitoring consent/observer/tray/GUI, durable Save and integrations are not
started. Next gate: independent rereview of the exact corrected candidate and
external manifest/evidence; no staging, publication or integration authorized.

## H01-B security corrections F1/F2 — ready for independent rereview (2026-10-15)

**CORRECTIONS IMPLEMENTED, READY_FOR_INDEPENDENT_REREVIEW.** The independent review
of aggregate `0c4eb557d5f924d55034c1ccd841023fd49c85c51a3f7364d0b37feaeb27a210`
required changes for an unrestricted public exact-source getter and time checks
preceding response construction. The original 24-path candidate and review are
preserved byte-for-byte in the external correction checkpoint. The original author
handoff below is historical; its passing suites did not establish these invariants.

The public plaintext getter is removed. Its internal replacement rechecks the
existing S05 consent snapshot against current scoped database evidence before
loading exact source in the same read snapshot. Service-only supported source
delivery still requires one-use consume and current full-source assessment.
Response/state construction now precedes the final SQLite authorization fence;
final generation/request/Item-expiry checks precede release. Expired preparation
does not publish a ticket; consume remains spent on failure. Post-fence invalidation
ordering and future consumers' duty to honor expiry remain unchanged. Scheduling
or delivery timing after return is not guaranteed by an in-process check.

Fresh Windows-host synthetic checks: **16 security regressions PASS**, existing
**50 H01-B PASS**, S05 consent/privacy/receipt/service **75 PASS**, isolated
persistence/Recent Integration **5/5 PASS**, all exit 0 with zero skips. Qt checks
are offscreen. The first new regression attempt had one incorrect expected denial
ordering; RT-R01 diagnosis preceded a test-only ordering correction and fresh PASS.
All prior failure evidence remains preserved. No full Database/protocol rerun is
claimed for this correction; migration/schema/protocol bytes are unchanged.

Five existing candidate paths are corrected: repository, service, H01-B test file,
Python architecture and this status document. No new candidate path, migration,
domain DTO, H01-A contract/hotkey, native effect or IPC change. Exact correction
diff, per-path CHANGED/UNCHANGED identities, complete corrected 24-path manifest,
validation and rereview handoff are under
`%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Clipboard-H01/H01-B/security-correction-20261016T021154Z/`.
The branch/worktree/base remain those below; the index is empty and the candidate
is uncommitted. Independent rereview is NOT RUN. No Git integration or H01-C work.

## H01-B — SQLite append head and internal paste authorization (2026-10-15 candidate)

**READY_FOR_INDEPENDENT_REVIEW.** H01-B implementation candidate is in
`C:/Dev/F7Hub-Clipboard-H01-B`, branch
`feature/clipboard-h01-append-head`, based on H01-A merge
`31301634c9e40c4a1f34523bd790974a38b07296`. Live local/fetched/remote main matched
that base at implementation preflight. H01-A is CLOSED by PR #108; its feature
commit is `1edf510b0fbca1411ade7ebb2724a16fcf9df596`. The older H01-A candidate
section below retains its historical meaning. H01 architecture D1–D12 is approved
for plan SHA-256 `c690e10017019da92ddef5cb6f7a3ffad21f3360a8f546507db3aba7d98ee9a2`.

Migration 0017, atomic genuine-append head updates, exact no-fallback source reads,
and internal one-use prepare/consume are implemented. S05 consent/assessment and
existing receipt recovery remain authoritative. Deleted/expired/replaced/invalid
heads deny. Consume rechecks the assessed exact source under an immediate writer
reservation and releases it before delivery; its ticket is retired even on failure.
The effect lease is request-start bounded and never promises OS paste success.
No H01-C–F runtime, native effect or production registration is delivered.

Fresh final checks on the Windows host: full Database **633 PASS** (including
**50 H01-B** cases); S01/H01-A/capture/privacy Unit regression **68 PASS**;
isolated persistence/Recent/Setup/bootstrap Integration **5/5/8/10 PASS**;
Settings cross-process **1 PASS**. All completed with exit 0 and no skips. Qt
Integration used offscreen presentation. Synthetic databases require
integrity_check=ok and zero foreign-key violations.
An initial bootstrap run failed on a second stale migration-count literal (16);
RT-R01 diagnosis and an expectation-only correction preceded the fresh 10-test
PASS. That failed attempt is preserved externally and is not relabeled PASS.
Full affected-suite results and exact commands are recorded with per-run candidate
identities under `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Clipboard-H01/H01-B/`.
The final external manifest/handoff owns the exact review candidate identity.
No operational database or live Clipboard was used. Native paste, physical keyboard,
modern Notepad acceptance and cross-process IPC security validation are NOT RUN.

Candidate remains unstaged/uncommitted; separate independent review and any future
Git integration require their own gates. Canonical unrelated work and all prior
worktrees/checkpoints are preserved. H01-C has not begun.

## H01-A — native Clipboard contracts and dormant chord adaptation (2026-10-15 candidate)

**READY_FOR_INDEPENDENT_REVIEW** in isolated
`C:/Dev/F7Hub-Clipboard-H01-A`, branch `feature/clipboard-h01-contract-cycle`,
based on `97593f1e14d6b5efd75303886fdac3d592be71a1`. The user approved H01
D1–D12 and corrected F1/F2 for the exact external plan SHA-256
`c690e10017019da92ddef5cb6f7a3ffad21f3360a8f546507db3aba7d98ee9a2`.
H01-A adds closed inert native DTO/schema/framing profiles and extends the
existing CP-01 policy/controller with independent latest-paste exclusions,
Win+Alt chord recognition, process creation identity and async completion.

FRESH `WINDOWS_NATIVE` checks: Python native-protocol unit tests **6 PASS**;
externally supervised AHK Policy **255 assertions PASS**, Harness **57 PASS**,
and CP-01 Native hook/foreground fixture **123 PASS**, each exit 0 with zero
owned survivors. The native fixture used injected Ctrl+Alt+F23/F24 events;
Win+Alt+C/V were checked through deterministic injected key-state providers,
not physical keyboard or production hook registration. Physical keyboard,
installed Notepad, AltGr layout, accessibility/display variants and actual
Clipboard effects are NOT RUN in H01-A. An initial malformed-vector unit-test
failure was corrected and the final six tests passed; the failed attempt is
preserved in external evidence. Candidate manifest, test results and handoff
are under `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Clipboard-H01/H01-A/`.

No production hotkey, authenticated IPC, session, worker, Clipboard capture or
paste, SQLite change, S01 semantic change, or F7/Alt+F7 host change is delivered.
H01-B through H01-F remain separate increments. The candidate is unstaged and
uncommitted; independent review and Git integration are pending separate gates.
Older candidate sections below retain their historical wording.

## S05 Checkpoint B — READY_FOR_INDEPENDENT_REVIEW (2026-10-15 candidate)

Candidate in `C:/Dev/F7Hub-Clipboard-Phase2B-S05`, branch
`feature/clipboard-s05-privacy-admission`, base/HEAD
`8edb7a2b056d2ff605f84b7e8473cf44c5b437b1`. User R1–R6 approval authorizes
implementation/testing/documentation only. Lifecycle READY_FOR_REVIEW; requested
handoff disposition READY_FOR_INDEPENDENT_REVIEW. No independent review, staging,
commit, push, PR or merge has occurred. The earlier B-blocked and D02 candidate
passages below retain their historical meaning; Git establishes D02 merged via PR106.

Implemented: additive empty consent migration 0016, trusted retained Setup
enable/reaffirm, atomic preference/evidence grant and workflow revocation, real
exact-source pure assessment composition, pre-assessment consent binding and final
writer-transaction authorization. Missing/stale/revoked/incompatible evidence denies.
Checkpoint A's implementation and tests remain unchanged. No native producer,
hotkey, paste, automatic monitor, popup, IPC or semantic feature is activated.

FRESH final affected run: **184 methods PASS**, zero failures/errors/skips, exit 0,
covering Settings, consent, profile paths, A assessment/boundaries, D02 contracts/
persistence, Setup GUI/flow, bootstrap and separate-process Settings/consent races.
Broader Database run: **582 methods PASS**, exit 0, before the final preparation-read
ordering correction and one added targeted test. That exact delta is documented;
all affected modules were rerun in the final 184-method PASS. The 582-method result
is RETAINED where unchanged/applicable, not a fresh whole-suite claim for the final
candidate. Earlier A 117-method evidence is historical, not combined S05 validation.

WINDOWS_NATIVE separate-process writer-order/interruption assertions passed in the
focused run. Native Qt windows-backend Setup check PASS at actual 1000x760: exposed/
idle readiness, keyboard reaffirmation, reload and visible controls; screenshots
inspected. Its Setup-path evidence remains applicable after a capture-only ordering
change. Synthetic input does not certify physical input, Narrator, High Contrast,
DPI, RDP or compact-layout accessibility. Offscreen checks are identified separately.
Temporary fixtures assert integrity_check=ok, zero FK violations, FK ON and 5000-ms
busy timeout. No operational DB/customer data or native Clipboard was accessed.

Evidence, failed attempts/diagnoses, exact candidate manifest/input hashes and
independent-review handoff are under
`%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Clipboard-Phase2B/S05/B-implementation/`.
Protected canonical state/worktrees and the opaque INI are preserved. Full A+B
independent review remains NOT RUN.

Approved transfer policy is preserved: complete backups may contain historical
consent; future managed restore/import must invalidate before admission and require
explicit Setup. Restore/replacement, snapshot sanitization, lifecycle coordination
and MT01–MT18 remain DEFERRED / NOT RUN. Arbitrary external same-path/profile DB
replacement is outside the detection guarantee; normal unchanged-DB restart keeps
valid consent. Finite-rule false negatives/positives and composed-code trust remain
explicit limits, with no external authority or malicious same-process resistance claim.

## Clipboard Phase 2B S05 — Checkpoint A implemented, Checkpoint B BLOCKED (2026-10-15)

**BLOCKED**, with an independently testable Checkpoint A candidate. Isolated
worktree `C:/Dev/F7Hub-Clipboard-Phase2B-S05`, branch
`feature/clipboard-s05-privacy-admission`, base/HEAD
`8edb7a2b056d2ff605f84b7e8473cf44c5b437b1`. Fresh remote main matched that
expected reviewed baseline before isolation. D02 is integrated through PR #106;
its candidate-era paragraphs below retain their historical meaning.

Checkpoint A adds a deterministic bounded offline assessment in the existing
Clipboard domain. Fixed content-free findings preserve PERMITTED, NEEDS_REVIEW,
POSSIBLE_SECRET and failed/incomplete distinctions. The module does not change
original Unicode or return/persist source, previews, hashes or match spans.
Finite local rules cannot detect every secret; ambiguity, recognized risks and
failed assessment deny automatic eligibility. The module is uncomposed.

Checkpoint B stopped before implementation: current Settings revision/USER source
cannot prove explicit Setup consent across restart or distinguish imported and
programmatic enablement. A new persistent consent representation/security review
is needed, including scope/restore and atomic revocation/commit ordering. No
migration, extra Boolean, in-memory bypass or real authority was implemented.
Positive consent-authorized capture and revocation/commit race tests remain
BLOCKED / NOT RUN. Default bootstrap remains unable to capture. Disabling
preferences leaves existing committed historical Items/Events unchanged.

FRESH Windows-host synthetic checks: privacy/negative boundaries 24, D02
contract/persistence/receipt migration regressions 49, Settings definition/backend
regressions 39 and isolated D02 integration 5: **117 PASS**, exit 0 per group,
zero failures/errors/skips. Pure Python/SQLite and offscreen Qt evidence does not
certify native Clipboard, hotkeys, IPC, physical input, DPI or accessibility. Two
unchanged D02 integration methods explicitly exercise Windows separate-process
locking/races. Temporary fixtures verify integrity_check=ok, zero FK violations,
foreign keys ON and 5000-ms busy timeout. Whole-repository regression and S05
independent review are NOT RUN. The tested and final manifests differ only by the
four affected owner/status/history documents; external verification compares the
unchanged production/test inputs.

Exactly seven unstaged/uncommitted paths: one new domain module, two new test
modules, and `13_PythonArchitecture.md`, Clipboard 1A, this status document and
`18_ChangeLog.md`. External evidence under
`%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Clipboard-Phase2B/S05/` includes the consent
assessment, test selection/results/logs, reproducible manifest and implementation
report. Canonical unrelated work and existing worktrees are preserved;
GuideSettings.ini remains opaque pathname-only state. Next required gate is
separate approval of the B consent mechanism. The combined slice is not
READY_FOR_INDEPENDENT_REVIEW; nothing is staged, committed or published.

User-intended future workflow: Win+Alt+C copies to F7Hub Clipboard; Win+Alt+V
pastes its last appended item. S05 excludes registration, native acquisition/
paste, IPC, monitoring and any runtime producer activation.

## Clipboard D02 — dormant atomic persistence candidate (2026-10-15)

Implementation candidate in `C:/Dev/F7Hub-Clipboard-D02`, branch `feature/clipboard-d02-atomic-persistence`, base/HEAD `cc0c3839e2500b3c9fe68545e8f899b718e6734e`. Remote main was freshly fetched and equal before isolation. This baseline includes S01 via merge PR #105; earlier S01 rereview/candidate text below is historical metadata and does not override that Git fact. Canonical unrelated work and worktree registrations are preserved; the protected INI is observed only by pathname inventory.

Checkpoint A implements additive receipt migration 0015 and immutable original-outcome contracts. Checkpoint B implements trusted source/operation/database/policy admission (default unavailable), service-issued generation and operation identities, monotonic fencing, binary-exact deduplication, one atomic Item/Event/receipt core, original-outcome replay, deleted-source receipt survival and bounded explicit maintenance. Same-operation changed semantics conflict; missing source yields known completion without equality verification or recreation; unknown/expired receipts never initiate capture. UNCERTAIN remains separate from confirmed rollback and requires receipt lookup.

**READY_FOR_INDEPENDENT_REVIEW** (delivery lifecycle READY_FOR_REVIEW), unstaged/uncommitted. Checkpoint A focused 6, domain/admission 17, persistence 26, D02 integration 5, full Database regression 552 and seven affected Integration modules 91 PASS, exit 0 for each completed group/module, no skips. Total distinct passing methods: 665 (focused Database methods are included in 552). Executions were FRESH on the Windows host and are RETAINED on resumption after relevant-input/log/exit verification; no suite was repeated for resumption. D02 includes real separate-process Windows locking/races; other Qt evidence is offscreen. Initial discovery FAIL, grouped Integration timeout and stale migration-count FAIL remain preserved. The recovery selector mistakenly repeated that known failed count check before correction; this RT-R01 procedural error is explicitly recorded in correction-03.md. The assertion was then corrected 14 to 15 before successful bootstrap and final isolated module executions. No independent review or approval has occurred.

No bootstrap, connection infrastructure, S01 protocol/schema, AHK, GUI, native Clipboard or Settings production files changed. Default bootstrap remains unable to persist text even after saved Settings are enabled. The injected test authority is test-only; a future real privacy authority/transport composition requires separate review. Local Python/SQLite validation does not certify native Clipboard, AHK/hotkeys, IPC authentication, accessibility/DPI or actual secret detection. No operational DB or real Clipboard contents are used.

Candidate manifest, input hashes, reproducible aggregate, commands/full logs/exit statuses, implementation report and architecture/security limitations are external under `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Clipboard-D02/`. Nothing is staged, committed or published. Next gate: separate independent read-only D02 review of the external candidate manifest; no automatic review or integration cycle.

## Clipboard Phase 2B S01 — inert snapshot protocol candidate (2026-10-15)

**READY_FOR_INDEPENDENT_REREVIEW**, unstaged/uncommitted in
`C:/Dev/F7Hub-Clipboard-Phase2B-S01-Reconciled`, branch
`feature/clipboard-phase2b-s01-reconciled`, base/HEAD
`4250f5f326ca1b8c0c867aed056fa6724882ed81`. The original seven-path
aggregate `43676fbda41096b936484f55194ec7b9cfea18c078c8d6d6e5ea504f3a2e1f01`
at base `418e3bfa3a01e27351e756befdab61d1d4bb9c4c` received independent
APPROVED_WITH_NOTES. Scope here remains exactly seven files:
infrastructure protocol module, local schema, focused unit tests and four owner/
status/history documents. The provisional domain module was replaced by a module
inside the existing infrastructure package under the explicit S01 placement gate.

Delivered: strict immutable inert 1.0 request/result/error DTOs, Foundation 0B
envelope, closed/status-body validation, bounded UTF-8/Unicode/JSON parsing and
serialization, caller-supplied operation/generation/producer-binding consistency,
safe content-free exceptions and hidden result text representations. Structural
schema fixture parity is checked; no full JSON Schema engine is claimed.

Original reviewed execution: 28 focused synthetic unit tests PASS, exit 0, zero
skips, 2026-10-14 Windows workstation, portable inert Python behavior only.
FRESH Windows-host focused run on the reconciled base: 28 PASS, exit 0, zero
skips, portable inert Python behavior. All five tested inputs match the original.
The new seven-path manifest and fresh result are external under
`%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Clipboard-Phase2B/S01/reconciliation-20261015/`;
original review evidence is in its parent directory.

Native Clipboard capability remains NOT IMPLEMENTED. Runtime auth/enrollment,
transport, worker, privacy assessment, replay tables, service/GUI connection,
60-second expiry enforcement and capture persistence remain separate S02–S07 or
owning capture slices. Native Clipboard tests are NOT APPLICABLE to this inert
module; unrelated GUI/AHK/PowerShell/Mochi/database suites are NOT RUN.

Fresh fetch and live remote query match canonical main at the integrated
Documentation Reconciliation 01 merge `4250f5f326ca1b8c0c867aed056fa6724882ed81`
(PR #104). Its newer Foundation/Clipboard planning remains in this candidate.
The original approved implementation bytes are preserved. This combined
documentation/base requires independent rereview; integration is separate.
Canonical user files, opaque GuideSettings.ini and existing worktrees remain
untouched.

## Documentation Reconciliation 01 — current boundary (2026-10-15)

**INTEGRATED** through PR #104 at `4250f5f326ca1b8c0c867aed056fa6724882ed81`
on canonical and live remote main. The earlier review-candidate wording below
is a dated planning snapshot. The [DR01 register](../Planning/Foundation/0A_Master_Foundation_Architectural_Contract.md#documentation-reconciliation-01--decision-register-2026-10-15)
routes approved functional requirements; no application capability is delivered
by this reconciliation. The former review gate is historical.

FACT from local ancestry: shell S001–S005 and Clipboard Phase 2A are merged through
PR #103 (`418e3bf`). Their candidate-stage passages below are historical, including
then-pending integration statements. Source inspection confirms retained rail/
utility routes and two Clipboard source children: F7Hub Recent/Setup plus Windows
unavailable feedback/disabled Refresh. No fresh runtime or native acceptance is
claimed. Existing Shared Settings stores only its admitted Boolean preferences.

Automatic capture, seven-day cleanup execution, recognition, Quick Picker,
authenticated Clipboard bridge, durable workspace recovery, contextual Mochi
forms/reminders and manual Prompt Builder remain future delivery. Approved intent
does not activate them. The nine placed Workspace/DataReadiness candidate files
remain unreviewed and unadopted. Synthetic data is not production-ready evidence.
Validation here is documentation/static only; no production or database change,
seeding, hotkey registration, dependency installation or Git integration occurs.

## Clipboard Phase 2A — two-source composition candidate (2026-10-14)

**READY_FOR_REVIEW**, unstaged/uncommitted in `C:/Dev/F7Hub-Clipboard-Phase2A`, branch `feature/clipboard-phase2a-two-source-composition`, base/HEAD `01900ab420e5cf2f316b7039319b3d9171c58e7f`. Local/fetched/live main and PR #102 integration matched before isolation. Phase 1 is CLOSED_WITH_NON_BLOCKING_NOTES through #102; its author-stage readiness passages and dated predecessor candidate sections below remain historical. Independent approval and integration are pending.

Implemented: one labelled source combo/two retained children in the existing Center; F7Hub default and original Recent/model/Setup/services/runners reused. Windows has accessible unavailable feedback and disabled Refresh, with no native read/callback. Switching reuses Setup Cancel/Discard, refuses pending/completing work, retains safe independent state/synchronous shell-owned offsets, and performs no service read/write/effect. Same-source selection is a no-op. Active-section/selector focus, S005 rail fallback, hidden-read/close guards and generation-bound own-child Recent completion remain. No backend/bootstrap/schema/AHK/IPC/dependency change.

FRESH WINDOWS_NATIVE host: **124 focused GUI PASS**, **15 affected Integration/two bootstrap checks PASS**, Qt offscreen, exit 0/no skips; synthetic DB byte/logical/revision/trace/integrity assertions pass. Separate Qt `windows`: **202 observations PASS**, exact 660×592, 1000×700, 1180×850 at 96 DPI; **18 captures opened/inspected**. Initial GUI/native attempts remain FAIL; assertion/readiness/reachability/post-modal corrections and distinct diagnostics are preserved under RT-R01. Diagnostic completion is separate from native acceptance; no unchanged automatic retry or timeout-only correction.

Physical keyboard/mouse, Narrator, actual High Contrast, alternate/mixed DPI, RDP and AltGr remain NOT RUN. Existing compact Setup explanatory horizontal overflow remains nonblocking with required reachability checked. Operational DB/integrity/live Clipboard are NOT RUN. Unrelated full AHK/PowerShell/Mochi/database/GUI/Integration suites were not automatically rerun. Unchanged backend evidence is historical; no blanket current RETAINED full-suite PASS.

Exact eleven-file candidate, command/log/result/input records, corrections, native captures/observations, raw/Git-normalized manifest and preservation audit are external under `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Clipboard-Phase2/implementation-20261014T193711Z`; continuity checkpoint is `Clipboard-Phase2/latest.md`. Canonical main/topic/sidecar/media state and existing registrations remain preserved. GuideSettings.ini remains opaque pathname-only inventory. S005 prunable registration is untouched, cause NOT VERIFIED.

Windows acquisition/authenticated IPC/privacy service, History/monitoring, capture, outbound domain Copy, Active Paste, Ctrl+Alt+C/V, HUD, new Settings/migrations and Phase 2B–2D remain unstarted here. Exactly one next action: independent read-only review of the bound Phase 2A candidate. No staging/commit/push/PR/merge/canonical synchronization/self-approval is authorized by readiness.

## GUI Shell S005 — Clipboard return control retirement candidate (2026-10-14)

S005 is **READY_FOR_REVIEW** in isolated `C:/Dev/F7Hub-GUI-Shell-S005`, branch `feature/gui-shell-s005-clipboard-return-retirement`, based on `05c3405d1ebf342ba37d5ec7c222993d6c54bb24`. The candidate remains unstaged/uncommitted; independent review, publication and integration are pending. The lower Back to Tickets button, `tickets_requested` signal, MainWindow connection and unconditional old-button focus are removed. The existing 52px rail Tickets QAction and guarded `show_tickets() → _leave_clipboard()` route remain. Clipboard Recent/Setup, lazy retained identity, reads, preferences, draft confirmation, pending refusal, Retry and close behavior are preserved. Accepted Clipboard activation chooses an enabled visible control in the active section or the Clipboard rail; repeated activation retains valid user focus.

FRESH WINDOWS_NATIVE host, Qt offscreen: affected GUI modules `test_clipboard_workspace`, `test_clipboard_setup`, `test_main_window` **111 PASS**, exit 0; selected Clipboard Recent/Setup and bootstrap Integration **22 PASS**, exit 0. The added Recent-with-Settings loading/focus method also passed separately under native Qt `windows` before the final 111-method offscreen execution. FRESH WINDOWS_NATIVE Qt `windows` synthetic-service harness at 660×592, 1000×700 and 1180×850 completed exit 0 with assertions for actual dimensions, missing return control, visible remaining controls, Tickets rail keyboard focus/Space route, and Tab/Shift+Tab traversal. Nine screenshots were saved and representative compact/standard captures visually inspected; compact Setup retains horizontal overflow for long explanatory text. This is Qt-injected keyboard/mouse evidence, not physical-device or screen-reader evidence. Native records and screenshots are under `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/GUI-Shell-S005/implementation-20261014`.

Historical S005 failed executions remain FAIL: initial affected GUI 107 tests/1 failure; corrected 110/2; selected readiness checks 2/2 and 2/1 before fixture event-order correction. Their preserved notes/logs explain missing window show, owner-specific readiness and deferred startup events; corrected checks passed after relevant fixture changes. No failed execution is relabeled PASS. Unchanged AHK Guide, PowerShell, Mochi, database and unrelated full suites were NOT RUN for S005; prior S004 evidence is context, not a fresh S005 pass. Physical keyboard/mouse, Narrator, real High Contrast, alternate or mixed-monitor DPI, RDP and AltGr remain NOT RUN. The accepted Scripts physical forward-Tab issue remains NOT PASS with exact stop NOT VERIFIED; the unrelated Mochi deleted-QTimer diagnostic remains unresolved.

Canonical `C:/Dev/F7Hub` stayed at `05c3405` with its unrelated modified AHK topic and untracked media/sidecar/protected settings pathname. `GuideSettings.ini` received Git pathname inventory only, with contents/metadata NOT VERIFIED. Earlier S004 candidate-status text below is a historical snapshot superseded by its external PR #100 closure record and live main.

## GUI Shell S004 — menu and toolbar retirement candidate (2026-10-14)

S004 is **READY_FOR_REVIEW**, unstaged/uncommitted in `C:/Dev/F7Hub-GUI-Shell-S004`, branch `feature/gui-shell-s004-menu-toolbar-retirement`, base/HEAD `0f970ca30cb88702a71ff0013ff2ce405002b885`. The user approved the external plan and authorized IMPLEMENT/TEST/DOCUMENT only through this gate. Independent review and integration remain separate and pending; no PR/publication, merge, canonical synchronization or S005 work occurred. S001/S002/S003 previously integrated via PRs #96/#97/#98 at `76bd643c8b44e13f4967f2fad5c736bcabc8ecde`, `54c48f1e1aca97f9450fe51a90bdbfc2e85ec1f4` and `f9bb6606389d1236c58d65f01e858d44bcc2544e`. Their earlier candidate snapshots below remain historical; live history and external closure records supersede old pending gates.

Delivered: MainWindow omits the redundant File/Settings menu bar and Tickets toolbar, retaining the 52px rail, four shared navigation QActions, native controls/status bar and existing workspace/service/draft/pending protections. The utility menu retains Mochi/Backup/Exit and owns Knowledge Base tools → Guide, using the same Guide action as the KB header independently of KnowledgeService composition/loading. Exit's existing Ctrl+Q action is registered with MainWindow. Alt+S opens utilities; Alt+F focuses the selected enabled destination, then the first enabled rail destination, then the gear when all destinations are disabled, without routing or discarding. Separate editor dialogs retain mnemonics, popups retain native input, and bounded local Escape restoration preserves current-page/control validity. Clipboard stays lazy/retained and keeps Back to Tickets.

FRESH validation on WINDOWS_NATIVE host: selected affected GUI regression **69 PASS**, selected affected Integration **193 PASS**, both Qt offscreen, exit 0 and no skips. Focused coverage reconciles **88 distinct MainWindow/Guide methods PASS across completed executions**, with explicit per-method provenance; this is not a claim that the original combined focused suite passed. Native Qt `windows`: **25 cases PASS** including eight shell-key/focus cases, six Quit cases, ten Guide cases and a real keyboard-selected gear → Python gateway → isolated AHK cold/warm/editor smoke with KnowledgeService absent. A separate **one-case PASS** verifies actual article Summary and modeless Mochi dialog priority. Native layout **2 cases PASS** at 660×592, 1000×700 and 1180×850 with a 15-point font fixture; fitting 150% Qt scale **2 cases PASS** at 660×500. All completed native executions exit 0. **27 current captures inspected**: rail/gear, root/submenu text, focus, KB controls and synthetic Guide/editor content. At compact sizes, existing workspace overflow remains accessible through shell scrollbars. Requested client rendering and keyboard/menu reachability do not establish physical whole-window fit on every screen; the host's available geometry limits tall desktop/scale fixtures.

RETAINED after source/transitive-input and completed-log verification: unchanged AHK Guide smoke **168**, host **70**, navigation **77** assertions PASS. No complete AHK, database, PowerShell, Mochi or full GUI/Integration suite rerun. Operational database checks **NOT RUN**; selected flow tests use isolated existing fixtures. Physical keyboard/mouse, Narrator, actual Windows High Contrast, alternate/mixed-monitor DPI, OS-font settings, RDP and AltGr **NOT RUN**. Qt scaling/font fixtures and synthesized keys are narrower evidence. The accepted Scripts physical forward-Tab discrepancy remains **NOT PASS**, exact stop **NOT VERIFIED**, deferred to its owner.

Historical failed runs remain FAIL: initial focused 87 tests/3 failures, corrected failfast 42/1, later 74/1, one popup fixture check 1/1, and initial native 5/1. Corrections preserved deliberate-input semantics, flushed queued creation focus in the actual helper, suspended shell shortcuts during utility-menu lifetime and waited for observable native combo popup exposure. One patch initially targeted the Quit helper rather than the new shell helper; that failed attempt is disclosed and retained. Corrected native/selected completion proves the affected criteria; no failed suite is relabeled PASS. No unchanged automatic retry is justified by these outcomes.

Integration logs retain expected temporary-fixture Mochi launcher missing-entry diagnostics while unittest completed OK/exit 0. The historical Mochi deleted-QTimer diagnostic remains an unrelated unresolved follow-up; it was not repaired or established as caused by S004. No service/worker/IPC/database/global-hotkey/security boundary change, new dependency, media feature or Settings mechanism was introduced.

Exact candidate manifest, per-run manifests/results/logs, focused-method coverage, retained-input verification, native observations/captures, correction history and implementation report are external under `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/GUI-Shell-S004/implementation-20261014-130648`. Later documentation/test-only additions are explicitly reconciled with the original tested identities. Canonical main remains on its verified base; unrelated topic, sidecar and media bytes are preserved. GuideSettings.ini is pathname-only opaque state with no individual read/stat/hash/copy/modification. Candidate scope is one production file, two existing GUI test files and nine narrowly affected documentation files.

## GUI Shell S003 — Guide relocation and window title candidate (2026-10-14)

S003 is **READY_FOR_REVIEW**, in isolated `C:/Dev/F7Hub-GUI-Shell-S003`, branch `feature/gui-shell-s003-guide-relocation`, base/HEAD `54c48f1e1aca97f9450fe51a90bdbfc2e85ec1f4`. Canonical main and the live remote were verified at that S002 PR #97 merge before worktree creation. S001/S002 sections below retain their original evidence and lifecycle snapshots; S002 is integrated in this baseline. S003 is unstaged/uncommitted; independent review and integration are separate gates.

Implemented: one **Guide** button in the Knowledge Base header and independent **File → Knowledge Base tools → Guide** fallback share `altF7HubGuideAction` and the existing async service/gateway handler. Its toolbar/direct File positions are removed. The AHK main title is exactly **Guide**; tray and Python feedback use the new display name. Visible ACK confirmation and guarded fallback require exact Guide/editor titles in the identified host PID/class. The existing Alt+F7 toggle, shared host, F7 launcher, editor drafts, message identities and payload remain unchanged.

FRESH WINDOWS_NATIVE validation: focused S003 10, full GUI 305 (Qt offscreen), full Integration 219 in three disjoint 73-test partitions (Qt offscreen), and native Qt/real Python-to-AHK 11 cases PASS. Six native fallback menu assertions PASS; five app/Guide/editor captures plus one submenu capture were opened and inspected. Compact 660×592, standard 1000×700 and desktop 1180×850 Qt client sizes, Guide reachability, keyboard focus/Tab/Space, availability/fallback, one dispatch, draft/state preservation and actual editor focusing were verified. Native AHK request-failure 20, host 70, navigation 77, toggle 9, Guide smoke 168, entry smoke 16 and standalone failure-caption 3 checks PASS; F7 launcher and magnetic follower regressions PASS. All accepted processes exited 0, with no test-owned AHK survivor and the three baseline AHK PIDs preserved. Native input is synthesized, at 96 DPI; physical keyboard/mouse, Narrator/high contrast, alternate DPI, RDP and AltGr are NOT RUN.

Prior failed/incomplete attempts remain archived: test-fixture pending-state mistakes, host readiness race, exact-title startup-wait mismatch, external discovery/multiprocessing runner errors, combined Integration supervision timeout, a GUI 30-ms scheduling assertion under parallel load, and legacy entry assumptions/foreground-readiness failures. The GUI timing test passed alone and the complete serial 305-test run passed; exact earlier timing/foreground causes are NOT VERIFIED. The entry harness now follows current Slice 047 bounds and notes/list focus scope, uses bounded observable readiness, and preserves the cursor around owned-window input. Production opacity/navigation were unchanged. Integration partition 2 reports a Mochi deleted-QTimer traceback after OK/exit 0. That owner is unchanged from base; causality to S003 is NOT VERIFIED, and no out-of-scope repair was made.

The final manifest, aggregate, exact commands/results, transitive-input applicability, inspected captures and implementation report are external in `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/GUI-Shell-S003/implementation-20261014`. Final documentation and test-only changes after earlier executions are explicitly reconciled there; failed results are not relabeled PASS. Independent review is pending. No commit, push, PR, merge, canonical-main synchronization or S004 work was authorized or performed. Canonical unrelated topic/sidecar/media changes are preserved. GuideSettings.ini receives Git pathname inventory only, with no individual read/stat/hash/copy/modification. S004, topics, formatting, databases, Settings and unrelated Mochi/Scripts corrections remain outside scope.


## GUI Shell S002 — Settings gear and utility menu candidate (2026-10-14)

S001 is CLOSED_WITH_NON_BLOCKING_NOTES through merged PR #96; canonical `main` and `origin/main` were at `76bd643c8b44e13f4967f2fad5c736bcabc8ecde` when S002 work began. The S001 section below is historical lifecycle evidence and its earlier OPEN wording is superseded by this current status.

S002 adds one bottom-aligned rail Settings gear and a Qt menu reusing the existing Mochi, backup and Exit actions and handlers. File and Settings menus remain. The gear is reachable through Tab, click, Space and Enter; Escape closes the menu. The existing action availability, asynchronous backup and protected close behavior remain the authority. No Alt+S or Alt+F rail shortcut is assigned because `&Settings` and `&File` already own those mnemonics. Appearance, Guide relocation, menu/toolbar retirement, Settings Center, media and S003 are not part of S002. This uncommitted S002 candidate is **READY_FOR_INDEPENDENT_REREVIEW** after the authorized P2 Quit shortcut correction; independent approval and integration remain separate gates.

Pre-correction Windows-host validation: Qt offscreen MainWindow **63 PASS**, full GUI **289 PASS**, and relevant Integration **79 PASS**, all with exit 0. Native Qt `windows` probes passed **33 assertions** at 660×592, 1000×700, 1180×850 and 15-point font, plus **25 assertions** in a bounded 150% Qt scale fixture; captured menus and focus were inspected. A first native run exposed a desktop-edge popup placement defect at 1180×850; clamping the popup to available screen geometry resolved it, and the failed evidence is retained. Native probes used synthesized Qt input. Physical keyboard, Narrator, physical High Contrast and actual mixed-monitor DPI remain NOT RUN. No database schema, migration, AHK, PowerShell or service change occurred. The original candidate and validation records are under `%LOCALAPPDATA%\F7Hub\CodexCheckpoints\GUI-Shell-S002`.

The independent review required correction because Qt's Windows `StandardKey.Quit` resolved to an empty shortcut. The existing Exit QAction now falls back to Ctrl+Q only when the native mapping is empty on Windows, preserving valid platform mappings and the existing close handler. No current Ctrl+Q collision was found. FRESH correction validation: **6 PASS** on native Qt `windows` with synthesized keyboard events, **69 PASS** in the Qt offscreen MainWindow regression and **1 PASS** in application-bootstrap Integration, each with exit 0. Draft Cancel preserves the focused Ticket note, pending backup refuses closing without duplication and recovers, idle Ctrl+Q closes once, and File/utility-menu Exit reuse the same action. Full GUI/Integration suites were not repeated for this focused correction; their earlier results describe the original candidate. Correction evidence, original/new manifests and the path drift matrix are under `%LOCALAPPDATA%\F7Hub\CodexCheckpoints\GUI-Shell-S002-Quit-Correction-20261014`. This is implementation validation, not independent approval.

## GUI Shell S001 — implementation candidate (2026-10-13)

**2026-10-14 pre-merge lifecycle snapshot:** The six-file implementation/test correction received independent **APPROVED_WITH_NOTES** at its reviewed candidate; its unchanged aggregate is `7c33a6c3629f2d361682d895101dc521865a7fd4d3c40e2d99a6ce1e931a1931`. The initial four-document review was CHANGES_REQUIRED for the Todo visual-order acceptance criterion; a later focused independent review approved that Todo correction before publication, while the other three documents retained their prior PASS findings. The complete approved 11-path S001 candidate is published at PR #96 head `c19490287ad5ae21586eacf17b1228a26af17a6a` on `feature/gui-shell-s001-navigation-rail`, based on `main` at `8e6e7bb3a2127d3fe9e54a7fe65c106cd3f9a807`; the original scroll correction and subsequent palette/focus corrections are included. The independent final published-head review identified stale lifecycle wording as the blocking documentation issue; no blocking implementation defect was reported. This targeted three-document correction is prepared for independent focused rereview. PR #96 remains **OPEN and UNMERGED**. Required GitHub review-thread reconciliation, approval to merge, PR merge, canonical `main` synchronization, final integration/launcher verification and S001 closure remain pending. S001 is not merged, integrated or CLOSED; S002 has not started. The approved S1 design-adoption history remains unchanged.

Delivered: a 52-logical-pixel rail routes through existing QAction handlers between Tickets, Knowledge Base, Scripts and Clipboard Center, with actual-page selection, visible selected state, accessible names/tooltips and action-matched availability. Scripts keyboard Space activation opens the workspace once. Rail-local Cancel focus restoration is synchronous; queued focus reconciliation after asynchronous completion waits for the outermost callback and checks activation generation, displayed page, active window and enabled/idle state without overriding later deliberate input. Busy and owner-pending guards, Ticket/Clipboard drafts, Back to Tickets and close protections remain. The Ticket queue permits Tab/Shift+Tab exit while retaining row navigation/Enter. Scripts toolbar has explicit visual-order Tab relationships with naturally disabled controls skipped. Accepted page changes reset both shell scrollbars synchronously; refusals and same-page activation retain position. Compact overflow remains reachable by scrolling. The verified stock Windows dark palette retains the adopted dark/cyan rail colors; other effective Qt palettes provide rail colors through their roles, including runtime palette changes. Physical High Contrast remains NOT RUN.

**Implementation evidence:** Retained Windows-native focused Qt windows **57 PASS**, full GUI **286 PASS**, and visible native traversal probe **PASS** remain bound to the six implementation/test blobs in the approved correction aggregate; independent rereview also executed **57 PASS**. The full Integration suite was rerun against published head `c19490287ad5ae21586eacf17b1228a26af17a6a`: **219 PASS**, exit 0, Windows host/Qt offscreen, with `PYTHONPATH` set to this worktree's `Python` directory. After the unittest summary and successful exit, the process emitted a Mochi deleted-QTimer traceback; its S001 causality remains **NOT VERIFIED**. The Integration result record and full log are in `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/GUI-Shell-S001/final-lifecycle-reconciliation-20261014/`. The six implementation/test files remain byte-identical to the published head and approved aggregate. The targeted documentation edits do not alter those test inputs. Synthesized QTest input does not establish a physical sequence PASS.

**S001 — Final Physical Keyboard Acceptance Evidence: USER_ACCEPTED_WITH_KNOWN_DEVIATION. MANUAL_ACCEPTANCE: ACCEPTED_WITH_KNOWN_DEVIATION.** User-reported manual validation covered sidebar/selected marker, Scripts Space activation, visible focus after refresh, reverse traversal, Ticket queue navigation, Clipboard Back and Ticket draft protection. Three physical forward Tab presses after refresh reached the Scripts Search field, whereas the native Qt test expected Refresh at the third press. Search remained keyboard-accessible; reverse navigation and general access remained available. The exact skipped or reordered focus stop is **NOT VERIFIED**. The user accepts this discrepancy for now; independent review classified it as **NONBLOCKING** for S001. The complete physical forward Tab sequence is **NOT PASS**. The reviewer did not directly inspect the physical screenshots. The [canonical Todo follow-up](../17_Todo.md#gui-shell-s001--scripts-keyboard-follow-up-2026-10-14) assigns refinement and physical destination-by-destination acceptance to the future Scripts Workspace redesign. Narrator, physical High Contrast, actual alternate-monitor DPI, OS font settings, RDP and AltGr remain NOT RUN.

Historical S001-R01 correction-cycle Windows host / Qt offscreen: focused MainWindow **42 PASS**, full GUI **267 PASS**, full Integration **219/219 PASS**, exits 0 with zero failures/errors/skips. Integration covers three disjoint 73-test partitions; its tested production and Integration inputs remain unchanged through the later GUI-test-only geometry correction and documentation updates. The new regression reproduced the original defect before the production fix. The first corrected full GUI run failed six new geometry assertions; an offscreen diagnostic exposed a text-bounds origin of `(100000,100000)` and an editor wider than the compact viewport. Corrected tests measure text dimensions and visible selection endpoints while retaining exact scrollbar checks; focused and full GUI then passed. All original and correction-cycle failures/incomplete attempts remain external historical evidence, including the original 600-second serial Integration timeout.

Historical S001-R01 corrected foreground Qt `windows` validation: **16 rail cases / 32 additional capture assertions PASS** at exact 660×592 / 1000×700 / 1180×850 and DPR 1.0 / 96 logical DPI, with 14 inspected destination captures. Bounded 150% Qt scale: **14 cases / 23 additional assertions PASS**, 10 inspected captures at 660×500 and 1000×500; the two suites requiring all three original sizes were excluded because those heights exceed the scaled available area. A 15-point application-font fixture passed four module routes / nine assertions at 660×592, with four inspected captures. All exits 0. Total final correction captures inspected: **28**. At that historical gate, physical input, Narrator, high contrast, actual alternate-monitor DPI, OS font settings, RDP and AltGr remained NOT RUN; the prior 35-image implementation record is preserved as historical evidence.

Historical S001-R01 and final 219-test Integration runs emitted the post-summary MochiGateway deleted-QTimer traceback despite successful test summaries and process exits 0. The concern remains **UNRESOLVED**, with S001 causality **NOT VERIFIED** and no Mochi repair. Preexisting worktree companions identified by review were preserved; their original ownership and complete cleanup remain NOT VERIFIED. Bounded correction supervisors observed zero surviving correction-owned companions. This is not a claim that all preexisting Mochi processes were cleaned up.

Current evidence: `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/GUI-Shell-S001/toolbar-keyboard-20261014/candidate-manifest.json`, its durable suite/native results and logs, and `final-independent-rereview-20261014/review-report.md`. Earlier reports/manifests under the parent checkpoint and `correction-20261013-115618` retain their historical candidate identities and failures/incomplete attempts. The new documentation manifest/inventory is external under the same S001 checkpoint root. The complete candidate includes the existing PR commits, the approved six-file correction and four changed owner documents. No staging, commit, push, merge or canonical synchronization occurred in this documentation task. Protected GuideSettings.ini remains pathname-only opaque; bytes/metadata are NOT VERIFIED. No database, AHK, PowerShell, dependency, media, utility relocation or broader GUI work was introduced. Older delivery sections below retain their historical meaning.

## Clipboard CP-02 lifecycle status (2026-10-12)

**CP02-S1: MERGED — closure pending. CP02-S2: MERGED — closure pending.** Both independently approved implementation slices are merged to `main`; the initial canonical synchronization is verified at `828507f952919662e518b1dd5cfbffdd21ecc5b4`, equal to `origin/main`. PR #91 merged as `8717e99f4cc77fc723497376dd858d22b8d6f18f`; PR #92 merged as `828507f952919662e518b1dd5cfbffdd21ecc5b4`. The Stage 1 and Stage 2 external integration reports record their review approvals, exact scopes, test provenance, and merged trees.

Initial closure verification: FRESH Git verification confirmed both PRs MERGED, both merge commits and feature commits in main ancestry, and canonical HEAD equal to live remote main. Fast-forward synchronization began from `8b92fd13dfe340563044acd41ef15c0b905243db`; the protected untracked `AutoHotkey/Troubleshooting_Sections/GuideSettings.ini` pathname was absent from the target tree and remains untracked. Its contents and metadata were not inspected. The Stage 1 and Stage 2 reviewed implementation trees are unchanged at their merge commits. The documentation reconciliation changes no production or test files. Documentation candidate review, integration, and final canonical synchronization remain pending; see the external closure report.

Evidence provenance: implementation and native evidence remain RETAINED from the independently reviewed reports; this closure pass added FRESH Git/ancestry/state checks only. GitHub reports **NO CHECKS CONFIGURED**, not a CI PASS. Stage 2 stale shell refusal feedback remains a nonblocking focused GUI follow-up. Physical input, alternate DPI, Narrator and high-contrast validation remain NOT RUN. CP-01 historical WINWORD2 failure root cause remains NOT VERIFIED; the subsequent post-merge diagnostic closed without reproducing it. Production Clipboard capture, Active Paste, native Ctrl+Alt+C/V bindings and authenticated Clipboard IPC remain unavailable. CP02-S3 remains unstarted and requires a new task.

Older CP02 implementation-candidate sections below are historical snapshots. They do not override these verified merge/synchronization facts or prior delivery evidence.

## CP-02 Stage 2 — Clipboard Setup editor (2026-10-12)

**READY_FOR_REVIEW**, isolated worktree `C:/Dev/F7Hub-Clipboard-CP02-S2`, branch `feature/clipboard-cp02-s2-setup-ui`, verified base/HEAD `8717e99f4cc77fc723497376dd858d22b8d6f18f`. Implementation/tests/docs are unstaged/uncommitted. Independent Stage 2 review is the next gate; no staging, commit, push, PR or integration is authorized here. Canonical main remains at `8b92fd13dfe340563044acd41ef15c0b905243db`; its protected untracked GuideSettings.ini was observed only through Git pathname inventory.

Implemented: one retained Clipboard Setup editor with the three existing independently editable Boolean preferences, explicit future durable-history opt-in/TEMPORARY wording, truthful unavailable runtime status, async coherent snapshots, atomic changed-key Apply with original revision, no-op without write, Cancel, dirty departure/reload/close protection, pending/callback-gap guards, safe errors and explicit stale-conflict Reload/review. Known commits remain saved through observer/display failure. Definitions, backend/schema/migrations and read-only Recent are unchanged; history and selected-database boundaries are preserved.

FRESH WINDOWS_NATIVE host noninteractive Qt offscreen: focused **73**, full GUI **251**, full Integration **219**, full Database **520** PASS, all exit 0/no failures/errors/skips. Full Integration freshly executes Stage 1 AC-15; a separate RETAINED applicability assessment checks 27 unchanged backend/schema/package/test inputs and accessible prior review result/log. Separate user-authorized foreground Qt run: **74 assertions PASS**, exit 0, zero owned survivors; seven captures opened/inspected after observable state at 1000×700 and 1180×850/96 DPI with no observed clipping/overlap. Input is QTest synthesized. Loading/unavailable/confirmation boundaries use explicit fixtures; CAS/SQLite and observer failure are real. Isolated integrity_check=ok and foreign_key_check=zero PASS. Evidence: `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Clipboard-CP02-S2/implementation-20261012` contains implementation-report.md, candidate-manifest.json, reproduction script, durable suite results/logs, native record, screenshots and visual inspection.

NOT RUN: physical input, alternate DPI, Narrator/high contrast, RDP/AltGr and actual capture/hotkey/Clipboard behavior. Capture ingestion, Ctrl+Alt+C/V production bindings, IPC, Active Paste, source acquisition/storage extension, retention execution and CP02-S3 are unavailable/unstarted. No operational/customer data was used. Existing companion-launch diagnostics and Mochi teardown follow-up are unrelated; no repair occurred. Native shell status-bar navigation/close-refusal feedback can remain after completion until another shell message replaces it; editor feedback/state is current (nonblocking shell follow-up).

Stage 1: **MERGED, closure pending**, verified PR #91 and external integration-20261012 report. Local-main synchronization is prohibited by this task, so Stage 1 is not CLOSED. CP-01 PR #90 and its diagnostic are CLOSED per current directive/verified integration handoff; historical WINWORD2 root cause remains **NOT VERIFIED**, nonblocking carry-forward. Older candidate paragraphs below describe their original delivery snapshots and do not override current verified lifecycle state. Stage 2 does not rewrite historical reports or close Stage 1.

## CP-02 Stage 1 — Shared Settings backend candidate (2026-10-12)

**READY_FOR_REVIEW**, branch `feature/clipboard-cp02-settings-backend`, isolated worktree `C:/Dev/F7Hub-Clipboard-CP02-S1`, base/HEAD `09bef3e8b4e55ed34b63a062d7b14a9d0b3f92af`. This candidate is unstaged/uncommitted and not integrated. Canonical checkout remains intentionally behind remote main and is preserved. Independent CP-02 Stage 1 review is the next gate.

Implemented/verified: pure Boolean USER definitions and exactly three false-default Clipboard preferences, safe immutable effective snapshots, SQLite overrides/revision, atomic Apply/Reset, stale-write CAS including absent-key/two-process races, explicit coherent refresh, classified failures and bootstrap composition. Disabling master preserves optional process/title preferences. Invalid/unknown rows remain retained; invalid/unavailable sensitive values resolve false. No runtime activation/capability is reported from a saved preference.

WINDOWS_NATIVE noninteractive validation: FRESH final Database **520**, mandatory AC-15 **1**, impacted bootstrap **10** PASS; RETAINED compatible full Integration **211**, GUI **232**, PowerShell **72** PASS, exit 0/no skips. AC-15 uses deterministic pipes/barrier synchronization, 250-ms fixture SQLite busy deadline, finite process/IPC budgets and verified child exit/cleanup. Independently repeat AC-15 during review; repeat on persistence/revision/group/reset/transaction changes. A read-only GUI change alone does not mandate whole concurrency repetition. Qt offscreen; no foreground/manual/DPI/native Clipboard acceptance claim. Isolated SQLite integrity_check=ok / zero foreign_key_check violations PASS. Focused new definition/backend checks also PASS. Evidence, test-input applicability, path hashes and reproducible final manifest: `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Clipboard-CP02-S1/implementation-20261012`.

Unavailable: Stage 2 setup/consent UI, capture/history ingestion, Ctrl+Alt+C/V production binding, authenticated IPC, source process/title acquisition/fields, active paste and retention execution. Existing ClipboardService remains read-only; AHK, Mochi and AltF7Hub behavior/configuration are unchanged. Operational/customer data and employer policy NOT VERIFIED. No user-owned process was restarted and no foreground native harness was run.

The supplied current handoff identifies CP-00/CP-01 approved, integrated and closed; live remote main is PR #90's CP-01 merge at the stated base. Older CP-01 pending-review paragraphs below are historical candidate metadata, not a rollback target or authority to repeat native automation.

## CP-01 — Clipboard hotkey policy and press-cycle candidate

**READY_FOR_REVIEW** on 2026-10-08 (America/Toronto). Worktree
`C:/Dev/F7Hub-Clipboard-CP01`, branch `feature/clipboard-cp01-hotkey-policy`,
base/HEAD `988c982f3abbdc1749cf1720dc487941f42899b7` (CP-00 merge PR #89).
Unstaged/uncommitted, not integrated. Canonical checkout remains on its earlier
HEAD with protected untracked GuideSettings.ini preserved through pathname-only
Git observation; no synchronization performed.

The dormant AHK foundation provides independent capture-selection/paste-active
exclusion maps, the centralized five Office basenames, exact case-insensitive
matching and unknown fail-closed resolution. Every observed trigger press is
latched, including rejection; trigger/Ctrl/Alt release permits rearm. Fixture
dispatch rechecks current action policy and original HWND/PID/executable.
Exceptions/cancellation cannot replay a held cycle or strand busy state.
No host inclusion/production binding, Ctrl+C/V synthesis, Clipboard content,
Python/IPC/Settings/database/GUI change or CP-02 is delivered.

FRESH WINDOWS_NATIVE focused AHK **147 assertions PASS**, native hook/foreground
**123 assertions PASS**, existing F7 launcher/tap/hold and follower **PASS**,
focused actual Alt+F7 toggle/reuse **9 assertions PASS**; exits 0 and zero owned
survivors. Native keyboard events are injected with test-only logical key-state
observation; physical/manual hardware, AltGr/RDP/extra layouts NOT RUN. Word and
New Outlook foreground identity/both-action rejection PASS without keys/content;
installed Excel/classic Outlook/PowerPoint acceptance NOT RUN (no safe existing
window). Broader Python/GUI/database suites NOT RUN because their owner code and
composition are unchanged and CP-01 is dormant.

One broader unchanged baseline host harness **FAIL** at SharePoint-topic
rendering/readiness, before its Alt+F7 section; preserved as a separate unrelated
follow-up, with cause NOT VERIFIED. Native fixture parsing/cleanup failures and
the zero-app initial Office probe are preserved; corrected required validation
completed. External evidence, exact candidate manifest and report:
`%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Clipboard-CP01/implementation-20261008`.
Next gate: **INDEPENDENT CP-01 REVIEW**. No staging, commit, push, PR or merge.

## CC-02 — Bounded read-only Clipboard Recent page candidate

**READY_FOR_REVIEW** on 2026-10-08 (America/Toronto), worktree `C:/Dev/F7Hub-Clipboard-CC02`, branch `feat/clipboard-cc02-recent-page`, baseline/HEAD `1991263db17c1a60b37808ab05a82741a0cd7b4d`. Recovery audit preserved the seven original modified implementation/test files and verified unchanged remote main; final candidate adds only the five affected owner docs. Empty index, unstaged/uncommitted/unpushed. Preceding D01/CC-01 records below describe their original candidate snapshots; their implementations are in the required merged baseline.

Production bootstrap now composes the merged Clipboard repository/service at the resolved database and injects the exact optional service into the lazy retained workspace. One independent existing runner reads the default first page; model/view shows only Time, Preview, Retention and Pinned. Refresh/Retry are explicit, empty success differs from safe failure, has_more is feedback only, duplicate reads are refused and close protects the owned worker/callback gap. Unrelated navigation and prior Ticket Discard/Cancel/Back semantics remain usable. No raw body, GUI SQL, OS Clipboard, capture, selection/Inspector, search, paging controls, mutations or external handoff.

Final FRESH evidence: focused 50 PASS; full GUI 232 PASS; full Integration 209 PASS on Windows host with Qt offscreen, zero failures/errors/skips, exit 0 and zero owned survivors. Separate WINDOWS_NATIVE: 96 assertions PASS at 1000×700/96 DPI, exit 0, zero survivors; four populated/empty/failure/Retry/loading captures opened and inspected without observed control clipping/overlap. QTest input is synthesized. Physical hardware input, alternate DPI, Narrator/high contrast and CC-13 work NOT RUN.

Historical focused 48/49 timeout and failed original zero-test diagnostic remain preserved externally. A bounded corrected diagnostic established cold Python-worker URI imports and Qt-only wait scheduling starvation; a 1 ms scheduling yield fixed the test helper without extending its five-second deadline or modifying D01. Full Database regression: **NOT RUN — NOT REQUIRED FOR UNCHANGED D01 DATA LAYER**. Prior D01 481 PASS is RETAINED separately with 83 relevant inputs verified unchanged; fresh CC-02 isolated integration checks preserve database bytes/logical state and pass integrity/FK checks.

External evidence: `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Clipboard-CC02/implementation-report.md`, `candidate-manifest.json`, suite logs/results, `native-validation.result.json`, four screenshots, visual inspection, recovery diagnosis and evidence-applicability records. Final documentation-only additions are bound to unchanged tested production/test identities. Independent review pending; next gate **INDEPENDENT CC-02 REVIEW**. No staging/commit/push/PR/merge or next slice performed.

## D01 — Clipboard persistence and Recent query source candidate

**READY_FOR_REVIEW** on 2026-10-08 (America/Toronto). Candidate worktree `C:/Dev/F7Hub-Clipboard-D01`, branch `feat/clipboard-d01-recent-query-source`, repaired-main baseline/HEAD `df2d91fdcd1abc3c04f921cf47483ecb004bb7d1`; 30 candidate paths before this documentation correction, with exact final count recorded in the external manifest. The fast-forward reconciliation succeeded and preserved the D01 candidate implementation/test bytes. Candidate remains unstaged, uncommitted and unpushed; it is not approved, merged, integrated or closed.

Migration 0013 adds exactly eligible Clipboard Items and distinct Item-owned Capture Events. The owner service/repository returns immutable PERMITTED/complete SAVED-or-unexpired Item projections ordered by lifetime last_received_at and Item ID descending, using read-only SQLite, a limit+1 sentinel, default 50/max 100 and a safe 240-scalar preview. Kind is unavailable; full raw bodies, hashes and child collections are absent. No production writer, capture/privacy detector, complete replay handling, GUI/bootstrap composition, cursor/navigation, search, Inspector, associations or lifecycle mutations are delivered.

Fresh WINDOWS_NATIVE evidence after reconciliation: System Snapshot checksum module 4 PASS and full Database regression 481 PASS, zero failures/errors/skips, exit 0. RETAINED applicable evidence: focused Clipboard 49 PASS; Integration 206 PASS (Qt offscreen), exit 0; integrity_check = ok, foreign_key_check = zero violations; 1,000/10,000-item Recent checks use `idx_clipboard_items_recent` and preserve fixture database bytes. The completed Integration supervisor cleaned three owned companion descendants with zero survivors. The initial 180-second Integration attempt was incomplete; the corrected 600-second rerun completed on unchanged production/test inputs. Separate physical GUI validation is inapplicable to D01, which changes no GUI behavior.

Historical blocker: before reconciliation, the Database regression ran 481 tests with 480 passing and one pre-existing System Snapshot checksum-test failure (exit 1); an exact baseline-source probe reproduced it. The baseline defect was repaired separately and merged through PR #81. D01 then fast-forward reconciled to repaired main; no D01 candidate implementation/test bytes changed. The fresh post-reconciliation Database run passed all 481 tests.

The exact final manifest, implementation report, suite logs/results, baseline probe, reconciliation report and input-applicability mapping are external under `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Clipboard-D01`. Database integrity/query-plan evidence uses isolated synthetic fixtures. Runtime tests for this documentation-only reconciliation correction: NOT RUN; retained evidence remains applicable because no production or test input changed. Next gate: **INDEPENDENT D01 REVIEW**. Integration and CC-02 remain separately authorized work.

## CC-01 — Clipboard workspace shell

**READY_FOR_REVIEW** on 2026-10-08 (America/Toronto), pending independent implementation review. Candidate worktree `C:/Dev/F7Hub-Clipboard-CC01`, branch `feat/clipboard-cc01-workspace-shell`, base/HEAD `2af22c24b188e040080d1a7e3effd24ecf6613ca`; unstaged/uncommitted. This candidate is not integrated into canonical main.

File menu and toolbar share `clipboard.center`, immediately after Scripts. Accepted guarded activation creates one retained read-only ClipboardWorkspace in the existing stack. It displays **Clipboard Center**, **Clipboard history is not available yet.**, and **Back to Tickets**. The return signal uses existing Tickets navigation. Focus, singleton reuse, existing routes, callback-gap refusal, Discard/Cancel and hidden new-ticket close protection are covered. Clipboard query/history service, persistence, capture, monitoring, OS Clipboard access and IPC remain absent; no later Clipboard functionality is delivered.

Fresh validation against the implemented source/test candidate: workspace 3, MainWindow 23, corrected bootstrap 8, full GUI 221 and full integration 204 tests PASS, exits 0. Automated GUI tests use Qt offscreen on Windows; the integration suite also contains existing real Windows PowerShell execution cases. Separate WINDOWS_NATIVE Qt smoke: 28 assertions PASS at 1000×700/96 DPI, exit 0, one inspected screenshot, clean close and zero owned survivors. Input was synthesized by QTest; physical hardware input, alternate DPI and Narrator NOT RUN.

External evidence: `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Clipboard-CC01/implementation-report.md`, `candidate-manifest.json`, suite logs/results, `evidence-applicability.json` and `native-validation.result.json`. Final documentation-only additions are bound to unchanged tested production/test identities. Historical fixture/harness failures and the initial incomplete integration run are retained in the report; the corrected full run completed. Its supervisor terminated three owned companion descendants and verified zero survivors. Existing fixture companion-launch diagnostics are a nonblocking future harness/lifecycle concern, not changed by CC-01.

Canonical checkout remains on main at the approved base, with only protected `AutoHotkey/Troubleshooting_Sections/GuideSettings.ini` observed by pathname. Its contents/metadata were not inspected. No staging, commit, push, PR, merge or CC-02 work occurred.

## PowerShell diagnostic compliance candidate

The unstaged, uncommitted `feature/powershell-diagnostic-compliance` candidate adds strict mode and concise help to the three existing registered diagnostics. A guarded forward-only data migration refreshes their exact SHA-256 registrations, with matching literal execution-policy digests. The structured result and Local Baseline pack contracts remain unchanged. Validation and exact candidate identity are in the external implementation report; independent read-only review is the next gate.

## Slice 053 — Local Baseline Diagnostics

**READY_FOR_REVIEW** on 2026-10-03 (America/Toronto). Isolated `C:/Dev/F7Hub-S053`, branch `feature/diagnostic-baseline-pack-s053`, base/HEAD `642db59e6883c7d2e0a6dc4bb081f22ff2739ac2`. The candidate is unstaged/uncommitted; independent read-only review is next. System → Network → Services is the fixed, code-defined **Local Baseline Diagnostics** pack (`diagnostic.pack.local_baseline`). The technician explicitly runs the pack or one approved member. Results remain in memory. Script Type describes the script; the literal execution policy grants permission. Exactly the three reviewed DIAGNOSTIC identities may execute; unknown diagnostics and all five other types are rejected.

The existing shared PowerShellService, PowerShellGateway and ServiceTaskRunner serve both run modes. A service reservation spans the entire sequential pack. Every member repeats current registration lookup, exact-byte verification, sealed preparation, immediate revalidation, trusted 64-bit PowerShell 7/token checks, separate owned job, bounded capture, contract validation and verified cleanup. Valid collection ERROR/exit 1 continues; a boundary failure aborts with partial attempted results, failure position and skipped remainder, and no aggregate collection status. Cleanup uncertainty latches both run modes blocked.

Validation: Database 438, PowerShell 72, GUI 210, Integration 203 PASS (196 RETAINED methods plus 7 FRESH corrected bootstrap methods; original full exit 1, correction exit 0). Other final suites exit 0, and all supervisors report zero owned survivors. Native Windows 104 assertions PASS at 1000×700/96 DPI, QTest input; real pack and individual Network, synthetic valid ERROR, invalid middle output, actual synthetic timeout containment and cleanup-quarantine scenarios. All 6 captures inspected. Physical hardware input and alternate DPI NOT RUN. Earlier failed fixture/harness/migration-count attempts remain historical evidence with bounded correction records. `native-v5-retry.md` records one accidental unchanged launch and loss of the original v3 JSON; the later v4 duplicate artifact is preserved separately. Final applicability checks bind tested inputs to the documented candidate.

External evidence: `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Slice-053/implementation-report.md`, `candidate-manifest.json`, suite result/log files and `native-validation.result.json`. Canonical protected AltF7Hub YAML remains outside this candidate and preserved. No parameters, generic execution, elevation, remote targets, service control, health baseline, persistence/history, ticket linkage, AI execution or user-defined packs are included.

## Slice 052 — Controlled System Snapshot execution historical candidate

Historical Slice 052 scope, closed through PR #58 and superseded by Slice 053 above.

**CLOSED** through PR #58 at Slice 053 base `642db59e6883c7d2e0a6dc4bb081f22ff2739ac2`. The following records its original implementation scope and evidence. Original isolated worktree `C:/Dev/F7Hub-S052`, branch `feature/powershell-execution-s052`, base/HEAD `2730047e83387a042b9e89378ea4beca6cef4b45`; the original candidate was unstaged/uncommitted. Scripts now explicitly runs only the reviewed read-only Windows System Snapshot under non-elevated PowerShell 7 and displays validated in-memory results. The source is exact-byte verified and executed through a private sealed artifact and owned finite job. Diagnostic ERROR differs from execution failure. No pack, parameter, history, ticket linkage, remediation, AI execution or schema migration.

Resumed GUI **206 PASS FRESH**, exit 0. Database **433**, PowerShell **51** and Integration **201 PASS RETAINED** from durable results with unchanged relevant inputs. Corrected native Windows validation **43 assertions PASS**, process exit 0, zero owned survivors; ready, real result and synthetic timeout captures inspected at 1000×700/96 DPI. Physical manual input and other DPI NOT RUN. The earlier native failures and incomplete GUI run remain historical evidence. Exact manifest, logs, results, captures and implementation report are external under `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Slice-052`. Prior Slice 051 historical candidate status below is historical handoff prose; its closure through current main was verified in the external Slice 051 integration report.

## Slice 051 — Bounded correction R1

The independent review of aggregate `258d08f48869162960401c782bf056240f32d5afa1f7ff1ba815f38c30847ef5` returned **CHANGES REQUIRED**: an unchanged Subject/Description save or failed save followed by Cancel could leave inline Priority/Type/Apply disabled. Its original fresh reviewer result remains **30 PASS / 4 FAIL**.

Both dialog paths now recalculate availability through the existing classification helper on open and completion. Completion clears the dialog reference before recalculation; pending/busy guards and dirty-state Apply remain authoritative. Regression tests preserve clean/dirty classification values and baseline without test-side control repair. The four exact regression methods failed before the production correction and now **4 PASS**. Fresh affected validation: **67 inline/dialog, 199 GUI and 197 Integration PASS**, all child exits 0 with no failures/errors/skips. The focused tests overlap regression. Database **433 PASS RETAINED** after 81-input comparison; native 1000×700/96 DPI layout evidence is RETAINED from the prior 185-assertion execution because layout/focus-order inputs did not change. New native execution, physical input and extra DPI are NOT RUN.

**READY_FOR_REREVIEW**, not approved or integrated. One newly added Description test fixture initially expected leading whitespace to persist; its input was corrected and the one justified focused rerun passed. The previous review/fixture/layout/watchdog evidence is preserved. The unchanged Mochi post-summary QTimer diagnostic and temporary fixture-launch messages recur in the successful Integration log; they remain a nonblocking lifecycle/test-harness follow-up. Two regression-owned Mochi descendants were terminated, with zero owned survivors. No Mochi correction or Slice 052 work is included.

Correction manifests, before/after evidence, retained-input comparisons and the correction report are external under `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Slice-051/correction-20261003`. The section below records the pre-correction candidate and its historical validation; its aggregate and GUI/Integration runs do not identify or validate changed correction bytes.

## Slice 051 — Pre-correction Inline Priority and Type candidate

Verified 2026-10-03 (America/Toronto). Entry fetch and final remote verification match main `9111c9d87162d9f5f15a11c05b06495f9c86c328`, the Slice 050 merge PR #55. Slice 050 is CLOSED according to its external integration report; its pending-review prose below is **STALE HANDOFF METADATA** retained as history. Isolated candidate `C:/Dev/F7Hub-S051`, branch `feature/tickets-inline-classification-s051`, base/HEAD above. The dirty canonical checkout and all prior worktrees are protected.

**PASS — READY_FOR_REVIEW**. Tickets directly exposes domain-backed Priority and Type dropdowns and one explicit Apply changes action. Selection alone writes nothing; the normal Edit priority/Edit type dialog paths and unused modules are removed. A combined guarded transaction updates only changed classification fields and strictly later activity time, creates the existing conditional history events and reloads before commit; both fields commit or neither does. Individual APIs remain supported. No schema/migration, direct GUI SQL, dependency, Status/Subject/Description/Notes/Knowledge redesign or Slice 052 work.

Authoritative baseline and drafts are separate. Existing discard protection includes inline choices across ticket/number/queue/Company switches, New Ticket, reload, navigation and close. Dirty choices retain their original token across unrelated activity refreshes, so stale Apply fails closed. Pending ownership spans write/detail/queue callbacks including dispatch errors and obsolete completions. Failed saves retain drafts; committed saves become clean before read recovery and remain truthfully acknowledged if detail/queue refresh fails. Existing search/filter/page and filter exit, Quick Note, Status and New Ticket remain intact.

Regression **822 PASS**: 433 Database RETAINED with unchanged applicable inputs; 199 GUI and 190 Integration FRESH, all exit 0 and zero test failures/errors/skips. Focused tests overlap. Native Windows **185 assertions PASS**, exit 0, at 1000×700/96 DPI; all nine final captures inspected, including expanded Resolution, without observed clipping or overlap. Physical manual input and other DPI are NOT RUN; failures use injected fixtures. Earlier fixture failures, progressing-suite watchdog timeout, native height and offscreen width failures are retained with corrections. The final Integration log also contains an unchanged MochiGateway shutdown QTimer-already-deleted diagnostic after its successful unittest summary; this is an explicit nonblocking follow-up outside Slice 051, not a suppressed test failure. Two owned detached Mochi descendants from regression were terminated; final owned-process inspection reports zero survivors and the native fixture was removed.

Twenty candidate paths: 16 tracked modifications, two tracked deletions, two untracked test additions; index empty, nothing staged/committed/pushed and no PR/merge. Exact external manifest, normalized/raw identities, applicability records, logs/results, native captures, self-review and implementation report reside under `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Slice-051`. Next gate is independent read-only review; no approval/integration is claimed.

## Slice 050 — Tickets workspace creation candidate

Baseline verified 2026-10-02 (America/Toronto): live remote and clean local main `fbb3340b3454db65a7b8b14e7cd3733ff3dc860c`. Slice 049 is **CLOSED** through PR #54 and its inspected external integration/closure report. Its pending-review prose below is **STALE HANDOFF METADATA**. Candidate `C:/Dev/F7Hub-S050`, branch `feature/tickets-workspace-create-s050`, base/HEAD above; canonical dirty checkout and unrelated worktrees are protected.

Implemented: **Tickets** replaces the visible Saved Tickets label; separate New Ticket primary menu/toolbar/page/Ctrl+N is removed. **+ New Ticket** hosts the existing creation widget in the right pane with queue visible and pinned Cancel. Activity draft discard confirmation protects entry; cancel restores prior detail/tab without ticket writes. Search, filters and page persist. Successful creation reopens authoritative saved detail and selects a matching queue row; excluding views retain their filters while detail opens independently. Save failure preserves form data; committed creation plus failed reads has read-only reopen/Refresh recovery. Quick Note is hidden/disabled with no active saved identity during creation, and restored for loaded tickets. Creation and status pending/generation guards cover callback gaps, duplicates, close and stale detail/queue/number callbacks. No service/repository/schema/migration/bootstrap composition or unrelated redesign.

Native Windows 1000×700/96 DPI validation passed using QTest events on the Windows Qt backend and isolated synthetic SQLite; captures are inspected. Earlier failed layout/foreground/focus attempts are preserved. Physical manual input and additional DPI are NOT RUN; failure fixtures are injected. Recovery verified 2026-10-03: **READY_FOR_REVIEW**. FRESH 10 focused boundaries and 177 Integration tests PASS; RETAINED 199 GUI, 423 Database and corrected native evidence PASS with unchanged relevant inputs. Durable artifacts proved the status guard was already validated before exhaustion; this recovery additionally covers post-commit failure/dispatch release and normal creation afterward. Exact candidate manifest and implementation report are external. Owned historical Mochi descendants were removed; no owned test/native process or Slice 050 native fixture remains. Work is unstaged/uncommitted; independent review/integration remain pending; Slice 050 is not CLOSED. External evidence: `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Slice-050`. Inline property editing and Knowledge Base redesign remain deferred.

## Slice 049 — Quick Note

Verified 2026-10-02 (America/Toronto). Candidate `C:/Dev/F7Hub-S049`, branch `feature/tickets-quick-note-s049`, base/HEAD `9f66c9a51f2adb3fe6fbcd21bb65a09b69303957`. Entry fetch and live remote main matched this approved base. Slice 048 is CLOSED through PR #53 and its external integration/closure report; its candidate prose below is STALE HANDOFF METADATA. The dirty canonical checkout, 405 protected changed/untracked files, protected recovery ref and every prior worktree were preserved.

Status **PASS — READY_FOR_REVIEW**. Scope is the first increment only: compact always-visible Quick Note, editor-scoped Ctrl+Enter, multiline/Escape behavior, Internal default, retained type/author, captured values, pending ownership through write/detail/queue callbacks, draft/error safety and same-ticket focus recovery. MainWindow guards navigation/close during callback gaps. No service/repository/schema, lifecycle, naming, preference, retrieval, property-edit, creation or Knowledge Base change.

FRESH focused GUI **15 PASS**, ticket Integration **49 PASS**; full GUI **199 PASS**, Integration **163 PASS**, all exit 0, no failures/errors/skips. Database **423 PASS RETAINED**, after independently matching 82 relevant inputs, original logs/results and environment. Full regression total **785 PASS** comprises 362 fresh and 423 retained tests; focused counts overlap. Native Windows **90 assertions PASS**, process exit 0, at 1000×700/96 DPI; all six final captures inspected. Physical manual input and other DPI are NOT RUN. Earlier harness failures and liveness-report correction remain recorded; product tests were not rerun for unchanged inputs.

Approved scope, manifests, suite results/logs, native procedure/result/captures, applicability and preservation records, implementation report and latest checkpoint reside under `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Slice-049`. All candidate files are unstaged/uncommitted and the index is empty. Next gate: independent read-only review; no commit/push/PR/merge performed. Follow-ups B–G are not started. One synthetic temporary fixture remains outside repositories after recursive cleanup was rejected by command policy; this is a nonblocking cleanup note, not user data.


## Slice 048 — Network Configuration Snapshot

Verified 2026-10-02 (America/Toronto). Candidate workspace `C:/Dev/F7Hub-S048`, branch `feature/network-snapshot-s048`, base/HEAD `dab8f25d65a505c6a7943b15335c9fb1c7984c92`. Slice 047 is CLOSED through PR #52, corroborated by its external closure state and live local/remote main. The dirty canonical workspace on the older Slice 047 branch is protected and preserved from recovery entry. GuideSettings.ini already differed from the original implementation checkpoint; its current bytes are retained. Predecessor pending-review prose below is historical STALE HANDOFF METADATA.

Status **PASS — READY_FOR_REVIEW**: one core configuration diagnostic, one guarded data migration with exact CRLF checksum, targeted attribute rule and existing Scripts/copy/management behavior reused. No production Python/GUI/schema/execution changes. Catalog remains metadata plus manually verified source copy; enablement is visibility only.

Powershell 19 PASS (RETAINED), Database 423 PASS (RETAINED), Gui 197 PASS (RETAINED), Integration 157 PASS (FRESH); exit 0, no failures/errors/skips. Focused suites overlap full results. RETAINED non-elevated native diagnostic and isolated Windows catalog workflow PASS at 1000×700/96 DPI, observable runner/loading/copying idle, screenshot inspected and all previous clipboard MIME formats restored. Native data values are excluded from durable logs. Other Windows versions/DPI and PowerShell 5.1 are NOT RUN; AHK/Mochi behavior is outside Slice 048 scope.

Exact candidate manifest, tested manifests, suite logs/results, native record/capture, protected-work verification and implementation report reside under `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Slice-048/implementation-20261002`. Candidate is unstaged/uncommitted, index empty. Next gate: independent read-only review; no commit/push/PR/merge is authorized.


## Slice 046 — AltF7Hub integration and keyboard navigation

Last verified: 2026-10-01 (America/Toronto). Candidate branch `feature/altf7hub-integration-s046`; HEAD/base `15c61b5c410d0d5dffe5ac6c5ac01a4b6dd960f7`. Status: **PASS — READY_FOR_REVIEW after correction of R046-01**. Index empty; candidate unstaged/uncommitted. Independent rereview is the next gate; integration is pending.

Shared AHK v2 host, standalone client and Python toolbar/File action are implemented. Scoped topic arrows wrap; repeated opacity arrows share controls and persistence. R046-01 previously reproduced seven Down inputs advancing only three topics. The corrected input callback commits logical navigation immediately and defers native selection/formatting to an interruptible serialized painter. FRESH correction validation: navigation 77 checks, guide 162, shared-host 29, native Python/guide/editor 14, supplemental native 35, three original reproductions (9 checks each), F7 launcher and parser validation of 19 AHK files PASS. Seven rapid/held/native Down and Up inputs now each produce seven transitions, with synchronized final topic/title/body and no post-release movement. GUI 181, Integration 156, request-failure 7 and magnetic-follower PASS remain RETAINED after transitive-input/environment verification. Prior affected evidence was invalidated and freshly rerun. Exact results, attempts, native captures, corrected manifest and drift/applicability matrices are under `%LOCALAPPDATA%\F7Hub\CodexCheckpoints\Slice-046\correction`; `correction-report.md` in the parent folder is the current handoff. Native validation uses isolated data at 96 DPI; physical hardware, other DPI and live Teams/camera acceptance remain NOT RUN.

Supplied topics, format metadata, settings, backups and older evidence are preserved. Other worktrees and protected refs are unchanged. The corrected candidate has 68 paths; its previous 67-path manifest and review decision are preserved as historical evidence. Ticket-to-topic automation remains deferred. No database, dependency, script execution or Windows Startup changes.

## Slice 045 — verified closure

Slice 045 is **CLOSED** through PR #46 at `15c61b5c410d0d5dffe5ac6c5ac01a4b6dd960f7`. Its external integration/closure report was inspected and its merge was reconfirmed before Slice 046. The earlier pending-review snapshot below is historical and superseded; its validation counts are retained history, not fresh Slice 046 evidence.

### Historical implementation handoff


### Slice 045 — historical candidate snapshot

Last verified: 2026-10-01 (America/Toronto). Current candidate on `feature/script-catalog-search-s045`; HEAD/base `66f6a3d3da3c08242fcf698707bd233ff12e84f6`. Local main includes the approved v0.3 maintenance commit; remote main remained at Slice 044 closure `5fe1ed73d9c65c4d1b88defd0f43a3d1b91b94c0` at implementation entry. No remote mutation was authorized/performed for this slice.

Status: **PASS — READY_FOR_REVIEW**. Manual Search/Enter/Clear matches enabled scoped name/code/description metadata by escaped bound literal substring. Query validation rejects type/NUL before database access. Draft/applied state, refresh/navigation/management reload, selection, worker/callback guards, safe failures and existing verified-copy behavior are covered. No schema, migration, source-content search, execution, approval or dependency change.

Fresh Database **418 PASS**, GUI **178 PASS**, Integration **148 PASS** (744 full regression total), all exit 0 with no failures, errors or skips. Focused **32 PASS** and affected **46 PASS** overlap the full suites. Native Windows **PASS** at 1000×700 with observable worker/callback idle; six captures inspected. Search query-only/dump and integrity/FK evidence passed on isolated data. Native delay/refresh-failure fixtures were injected service failures, not native ACL evidence; the Windows GUI, keyboard and clipboard workflow was real. Prior clipboard MIME data was restored and temporary fixtures removed. Independent implementation review is pending.

Approved plan recovered from this conversation and durably saved as `%LOCALAPPDATA%\F7Hub\CodexCheckpoints\Slice-045\approved-plan.md`. Candidate manifests, suite results/logs, native harness/result and six inspected captures are in the same external directory. Final manifest/report identify exact candidate content; test-era manifests differ only by documented owner-document edits with unchanged relevant runtime inputs. All candidate files are unstaged/uncommitted; index empty. Protected recovery ref and four unrelated worktrees are preserved. Next gate: independent read-only review.

### Prior Slice 044 handoff snapshot (historical)

The verified closure report establishes Slice 044 CLOSED through PR #45. Its retained pending-review prose below is STALE HANDOFF METADATA. Broad historical synchronization remains DEFERRED.

Last verified: 2026-10-01 (America/Toronto).

Current candidate: **Slice 044 — Script registration and local management**, on `feature/script-registration-admin-s044` from `b4d46ef7af6936c5ef3c34686040691222115f31`. Freshly fetched origin/main and clean local main matched this approved base before branching, with an empty index and no untracked files. Protected recovery ref `recovery/pre-s024-protected-work` remained `002a494735f30e1488f61e21ea98740ae6371d4d`; four unrelated worktree HEADs were preserved. Slice 043 is merged through PR #44; its pending-review text below is **STALE HANDOFF METADATA**, retained as a historical snapshot.

Status: **PASS — READY_FOR_REVIEW after correction**. The initial independent review required actual Windows read-access proof before registration/enabling; the shared service guard now resolves the approved path, opens it in binary mode, reads one byte and closes it before writing. Denied open/read leaves persisted state unchanged; empty readable files are valid and Disable requires no read. ScriptService reuses scoped disabled-row inspection and existing path validation; ScriptRepository adds atomic default-disabled registration and token-guarded visibility writes, reloading before commit and returning the persisted record after success. New rows use PowerShell 7, 120 seconds, structured output required, disabled state and null category/checksum. Management/registration dialogs use the shared runner, preserve failed input, block duplicate writes/dismissal, discard late dismissed reads and report saved changes truthfully when refresh fails. Enabling is catalog visibility only; Copy Script retains its existing checksum verification. No schema/migration/dependency, PowerShell source or execution change. The corrected candidate is unstaged and uncommitted; independent read-only rereview is the next gate. The pre-correction aggregate and initial review remain historical evidence.

## Slice 044 Validation

Environment: repository `.venv\Scripts\python.exe -B`, Python 3.14.6, PySide6 6.11.2, SQLite 3.50.4, `PYTHONPATH=$PWD\Python;$PWD`. Automated GUI/Integration used `QT_QPA_PLATFORM=offscreen`; native used `windows`. Fresh corrected-candidate focused **46 PASS** (21.143s); full Database **414 PASS** (34.451s), GUI **174 PASS** (120.437s), Integration **146 PASS** (301.520s) = **734 full regression PASS**, all exit 0 with no failures, errors or skips. Database tests additionally force actual open/read failures and assert no registration, unchanged enable metadata/token/checksum, unreadable-file disable with stale protection, empty-file acceptance and recovery. Integration verifies real service read rejection preserves form input/database state and permits corrected retries. Existing defaults, uniqueness, scope, rollback, copy rejection and integrity/foreign-key coverage remain passing.

Fresh native Windows checks used isolated databases and synthetic scripts, waited for observable worker/callback idle, and passed keyboard input, registration validation, busy/dismissal protection, enable confirmation, disable, saved-write/failed-refresh retry and unchanged clipboard after null-checksum rejection. Existing approved source copied exactly; prior clipboard MIME data was restored. A fresh NTFS probe first established actual PermissionError, then verified rejected registration/no row and rejected enable/all metadata unchanged, recovery after restoring access, and successful unreadable-file disable. All three fixture DACLs were restored byte-for-byte, read access restored and temporary data removed. Eight captures were inspected with no observed control overlap or clipping at a 1000×700 MainWindow. Fresh correction logs/harness/captures are under `%LOCALAPPDATA%\F7Hub\CodexCheckpoints\Slice-044\correction-20261001\`; the new exact manifest, implementation report and latest checkpoint remain at the Slice-044 root. This is implementation validation, not independent approval. Prior PowerShell **6 PASS**, exit 0, is retained after unchanged standalone source/test inputs were verified; no PowerShell was executed during correction. AHK/API execution is outside this scope.

---

## Prior Slice 043 handoff snapshot (historical; Slice 043 merged through PR #44)

Last verified: 2026-09-30 (America/Toronto).

Current candidate: **Slice 043 — Secure Script Copy to Clipboard**, on `feature/secure-script-copy-s043` from `4d6901c01064af143abcca6292ff4abbea77129f`. Before branching, fresh local and live remote `main` matched this base with a clean tree and index; the protected recovery ref and four unrelated worktree HEADs matched the requested baseline. Slice 042 is CLOSED through PR #43. The Slice 042 pending-review text below is a historical handoff snapshot.

Status: **PASS — READY_FOR_REVIEW**. Root `.gitattributes` pins CRLF checkout for only `Get-SystemSnapshot.ps1`; migration 0009 guards the reviewed SHA-256 update without changing the `scripts` schema. `ScriptService` uses enabled-only lookup, current path validation, one binary read, exact-byte SHA-256 comparison and strict UTF-8 decoding. ScriptWorkspace submits the read through ServiceTaskRunner and copies raw source through Qt only if selection remains current. No PowerShell execution, automatic paste or remote integration was added. The candidate remains unstaged and uncommitted; independent read-only review of this exact candidate is the next gate.

## Slice 043 Validation

Focused exact-byte/migration **4 PASS**, service **6 PASS**, Scripts GUI **8 PASS**, and catalog integration **3 PASS** were rerun during recovery, each exit 0. Fresh full Database **398 PASS**, PowerShell **6 PASS**, and Integration **143 PASS** each exited 0; the prior full GUI **166 PASS**, exit 0, is retained because its production, GUI-test, migration and configuration inputs did not change. The first full Integration run found one stale eight-migration assertion; its narrow correction passed in the final complete rerun. Native Windows validation at 1000×700 is retained because production GUI/service and native-harness inputs did not change: after observable worker idle, real clipboard text matched the approved source, a local editor paste reproduced its text after editor newline normalization, and mismatch/missing-file fixtures preserved prior clipboard text. Keyboard Space activated Copy Script. Three screenshots under `%LOCALAPPDATA%\F7Hub\CodexCheckpoints\Slice-043\` were inspected; the visible controls and feedback had no observed overlap or clipping. This is candidate validation, not independent approval.

---

## Prior Slice 042 handoff snapshot (historical; Slice 042 later closed on main)

Last verified: 2026-09-30 (America/Toronto).

Current candidate: **Slice 042 — First Production PowerShell Diagnostic Script**, on `feature/system-snapshot-script-s042` in `C:\Dev\F7Hub`. A fresh `git fetch origin --prune` confirmed clean local `main` and fetched `origin/main` at approved base `c4c87ded5e7e8b66ded4f844c1715567760c730b` before branching, with an empty index and no untracked files. The protected `recovery/pre-s024-protected-work` ref was `002a494735f30e1488f61e21ea98740ae6371d4d`; four unrelated linked worktrees were left untouched. Slice 041 is CLOSED on the fetched base. The Slice 041 candidate wording below is **STALE HANDOFF METADATA**, retained as a prior snapshot.

Status: **PASS — READY_FOR_REREVIEW** after narrow corrections to the independently reviewed candidate. Migration 0008 installs one enabled Windows System Snapshot registry row without changing the schema or default-disabled table behavior. `Get-SystemSnapshot.ps1` collects a local read-only Windows snapshot as one JSON result when run standalone by test tooling. Returned drives retain null for unavailable Size or FreeSpace, preserve real zero, and make the result WARNING without discarding available measurements. The existing Scripts workspace displays the row as AVAILABLE when the file is present. F7Hub has no PowerShell execution path; production Python and GUI code are unchanged. Independent read-only rereview of the exact corrected, unstaged candidate is the next gate.

## Slice 042 Validation

Environment: repository `.venv\Scripts\python.exe -B`, `PYTHONPATH=$PWD\Python;$PWD`; automated GUI/Integration use `QT_QPA_PLATFORM=offscreen`. On the corrected candidate, focused PowerShell parser/normal/OS-failure/no-OS-result/drive-failure/partial-measurement **6 PASS**, migration **3 PASS**, affected registry/bootstrap/catalog **19 PASS**, and full Database **388 PASS** all exited 0 with zero failures, errors or skips. The isolated full GUI **163 PASS** and Integration **142 PASS** results from independent review are retained: production Python/GUI, migrations, GUI/Integration tests, configuration and dependencies are unchanged; the catalog flow copies the changed `.ps1` but checks its presence and metadata without reading or executing its content. Native Windows 1000×700 screenshots and idle-state harness evidence are also retained because GUI layout, registry metadata, path and passive file inspection are unchanged. They are not newly captured evidence. The external corrected manifest and checkpoint bind the exact candidate for rereview.

---

## Prior Slice 041 handoff snapshot (historical; Slice 041 later closed on main)

## Slice 041 Validation

Environment: repository `.venv\Scripts\python.exe -B`, `PYTHONPATH=$PWD\Python;$PWD`; automated GUI/Integration use `QT_QPA_PLATFORM=offscreen`. Final focused ScriptWorkspace **5 PASS**, MainWindow **10 PASS**, application bootstrap **6 PASS**, existing Script Registry **8 PASS**, and Script Catalog flow **1 PASS**. Fresh full Database **385 PASS** (25.824s), GUI **163 PASS** (262.096s), and Integration **141 PASS** (772.647s) = **689 full regression PASS**. Every final run exited 0 with zero unittest failures, errors or skips. The initial affected-test failure assumed Knowledge Base was always present in a MainWindow test; it was corrected to the actual optional-page index. The first integration attempt opened Scripts during an existing startup load; the test now waits for observable idle. Both corrected suites passed. Expected injected failure-path log lines did not indicate unittest failures. Full-suite logs are under `%LOCALAPPDATA%\F7Hub\CodexCheckpoints\Slice-041\`.

Native Windows Qt validation used a temporary project root, copied migrations and isolated SQLite; no production registry data changed. At 1000×700, the empty, populated, keyboard-selection, long-scroll and failed-load screenshots were captured and inspected. AVAILABLE, MISSING and INVALID_REFERENCE came from the real service/fixture. INACCESSIBLE was injected at the service inspection boundary solely for visual presentation. Manual refresh preserved selection; failed load cleared rows/details and successful retry restored them. Shutdown after workspace use succeeded. The first long-metadata fixture did not require vertical scroll; the fixture was extended and the final native run passed. No PowerShell process was launched. The external manifest and checkpoint bind the exact candidate for review.

---

## Prior Slice 040 handoff snapshot (historical; Slice 040 later closed on main)

Current candidate: **Slice 040 — PowerShell Script Registry Foundation**, on `feature/powershell-script-registry-s040` in `C:\Dev\F7Hub`. Fetched local `main` and `origin/main` equal the approved base `5072ae20cb912f25cd721bd6c18e5bf23a816eb0`, with a clean checkout and empty index before branching. The protected `recovery/pre-s024-protected-work` ref was `002a494735f30e1488f61e21ea98740ae6371d4d`; four unrelated linked worktrees were untouched. The development database had migrations 0001–0006 and no `scripts` table; the runtime database was absent and the legacy file zero bytes. None was migrated for validation.

Status: **PASS — READY_FOR_REVIEW**. Migration 0007, read-only repository and service, path validation, isolated tests and owner-document updates are in the unstaged, uncommitted candidate. Focused, affected and full regression passed on the final executable inputs. Independent read-only review remains the next gate. Slice 039's pending-review wording below is **STALE HANDOFF METADATA**: fetched main contains its PR #40 merge at the approved Slice 040 base. Its 673-test result is prior baseline evidence.

## Slice 040 Scope and Validation

Migration 0007 adds a metadata-only `scripts` table with default-disabled records and no production seed. The shared category foreign key checks identity; repository reads require `SCRIPT` scope and suppress an invalid-scope association. The service returns enabled metadata and a separate point-in-time file-reference status under approved PowerShell directories. It does not read or execute scripts. Disabled inspection is explicit repository maintenance access, not authorization. File availability does not establish later execution permission and must be revalidated by a future execution subsystem.

Validation environment: repository `.venv\Scripts\python.exe -B`, `PYTHONPATH=$PWD\Python;$PWD`; GUI and Integration used `QT_QPA_PLATFORM=offscreen`. Focused script-registry **8 PASS**; affected category-reference **10 PASS** and application-bootstrap **6 PASS**. Fresh full Database **385 PASS**, GUI **156 PASS**, Integration **140 PASS** = **681 full regression PASS**. Every run exited 0, with zero failures, errors or skips. The full Integration run completed after the earlier interrupted run's result could not be recovered. Expected injected failure-path log messages did not indicate unittest failures. Test logs are under `%LOCALAPPDATA%\F7Hub\CodexCheckpoints\Slice-040\`. Native Windows GUI inspection and PowerShell execution testing are not applicable to this backend-only slice. Independent read-only review is the next gate; this implementation is not an approval to stage or integrate.

---

Current candidate: **Slice 039 — Search Saved Tickets by Note Text**, on `feature/ticket-note-search-s039` in `C:\Dev\F7Hub`. The user approved the Slice 039 plan and explicitly authorized implementation, testing and documentation through `READY_FOR_REVIEW`. A fresh `git fetch origin --prune` confirmed clean canonical `main`, empty index/untracked set and HEAD = `origin/main` = `17e8a0c03a8e027cc044b09a83ebd0646e5409e0` before branching. The protected `recovery/pre-s024-protected-work` ref remained `002a494735f30e1488f61e21ea98740ae6371d4d`, and the four unrelated linked worktrees were left untouched.

Status: **PASS — READY_FOR_REVIEW** after bounded implementation, focused/affected/full regression, native Windows validation, documentation and self-review. Slice 038's pending rereview/integration wording below and in Todo is **STALE HANDOFF METADATA**: fetched local and remote `main` include its PR #39 merge at `17e8a0c03a8e027cc044b09a83ebd0646e5409e0`. Its 667-test result is prior baseline evidence, not Slice 039 validation. Slice 039 remains unstaged and uncommitted; independent read-only review is the next gate.

## Slice 039 Result and Scope

TicketService and TicketRepository now accept optional `include_notes: bool = False` on the existing list path. The service validates the flag before repository access; default callers remain subject-only. Saved Tickets opts into both description and note matching. The repository binds one escaped literal pattern into grouped subject, description and correlated note alternatives, preserving Status/Priority/Type/company constraints, ordering, paging and one result row per ticket. The existing worker, submitted-versus-draft search state, failure retry, exact-number opening and post-save detail/queue refresh remain in use. A new committed note can add a ticket to the applied results. Note text is not included in queue rows, preview snippets, logs or error feedback. No schema, migration, index, dependency, FTS or new search subsystem was added.

## Slice 039 Validation

Environment: repository `.venv\Scripts\python.exe -B`, `PYTHONPATH=$PWD\Python;$PWD`; automated GUI/Integration used `QT_QPA_PLATFORM=offscreen`. Focused ticket reads **33 PASS** and ticket workspace **43 PASS**. Affected note-service **17 PASS**, company-context **5 PASS** and MainWindow **8 PASS**. Fresh Database **377 PASS**, GUI **156 PASS**, Integration **140 PASS** = **673 full regression PASS**, each suite exit 0. Read tests cover all four text-field flag combinations, literal metacharacters, note-only/overlap/multiple-note matches, grouping with all queue and company filters, ordering, paging, unchanged SQLite contents, integrity, foreign keys and an `EXPLAIN QUERY PLAN` lookup using the existing note ticket-ID index. Integration covers search state, note-save membership, drafts, later-page retry, safe failures and exact-number opening. Injected negative-path log lines were expected; unittest summaries and exits were clean.

Native Windows: **PASS** on actual `windows` Qt at 1000×700 with an isolated populated database. After observable worker-idle readiness and explicit navigation to Saved Tickets, Enter search, combined filters, note-save membership, failed-read feedback, retry and Clear passed. All five final captures under `%LOCALAPPDATA%\F7Hub\CodexEvidence\Slice-039\native-hhc3zegc` were opened and inspected; the search placeholder and queue/detail controls were readable without observed overlap. An initial harness run timed out before inspection, and a later run captured the hidden New Ticket page; those were corrected in the external harness and are not counted as native visual evidence.

## Slice 039 Delivery Gate

Production scope is the ticket repository, ticket service and Saved Tickets workspace; focused tests are ticket reads and ticket workspace flow. Affected canonical owners are Features, User Workflows, GUI, Database Architecture, Python Architecture, Roadmap, Todo, ChangeLog and this report. Product Requirements already states the search need. System Architecture, physical SQL Schema, ERD, AHK and PowerShell have no change. Independent read-only review of the exact unstaged candidate is required; implementation self-review does not authorize staging or integration.

---

## Prior Slice 038 handoff snapshot (historical; Slice 038 later merged through PR #39)

Current candidate: **Slice 038 — Manual SQLite Database Backup**, on `feature/manual-database-backup-s038` in `C:\Dev\F7Hub`. The user approved the Slice 038 plan and authorized IMPLEMENT → TEST → DOCUMENT, then explicitly authorized the bounded Slice 038 correction after independent review. A fresh `git fetch origin` before branching confirmed a clean canonical `main`, empty index/untracked set, and HEAD = `origin/main` = `61a5ecb8f1607dc0e5da19cbacc9a0248c62fffb`. The protected `recovery/pre-s024-protected-work` ref remained `002a494735f30e1488f61e21ea98740ae6371d4d`. The four other linked worktrees were inspected and not changed; one already had unrelated documentation deletion/untracked archive work.

Status: **PASS — READY_FOR_REREVIEW** after the bounded 2026-09-30 correction, fresh focused/affected/full regression, native Windows validation, documentation and self-review. Slice 037's pre-review/pre-integration wording below and in Todo is **STALE HANDOFF METADATA**: live `main` includes its PR #38 merge at `61a5ecb8`. Slice 038 remains unstaged and uncommitted. Independent read-only rereview is the next gate; no push, PR or integration was performed.

## Slice 038 Result and Scope

The File menu adds **Back up database**. Bootstrap passes the active resolved SQLite path to a narrow service; the existing ServiceTaskRunner keeps the GUI responsive and prevents overlapping backup actions. A dedicated read-only source connection uses SQLite online backup into a temporary file under `%LOCALAPPDATA%\F7Hub\Backups`. The destination is closed, independently reopened and checked with `integrity_check = ok` and zero foreign-key violations before publication through a no-overwrite rename. All three backup connections enable foreign keys. A source write racing the backup snapshot boundary may or may not appear in the snapshot; successfully committed writes remain in the source. A unique filename avoids same-second collision assumptions. Failures remove the temporary file when possible and preserve completed backups. Success displays the actual path and explains that the file contains local SQLite data only and needs another location for protection from local-drive loss. Failure feedback does not expose raw exception text. No schema, migration, dependency, restore, schedule, retention, attachment/configuration/log backup or external transfer was added.

## Slice 038 Validation

Environment: repository `.venv\Scripts\python.exe -B`, `PYTHONPATH=$PWD\Python;$PWD`; automated GUI/Integration used `QT_QPA_PLATFORM=offscreen`. Corrected focused backup/MainWindow/bootstrap **26 PASS**, affected database connection/integrity/path/MainWindow/bootstrap **39 PASS**. Fresh Database **374 PASS**, GUI **156 PASS**, Integration **137 PASS** = **667 full regression PASS**, each suite exit 0. The initial focused run exposed Windows test-connection leaks and a false assertion requiring a racing write in the snapshot. The corrected fixture closes connections deterministically; the test now verifies a coherent SQLite snapshot and the committed source write while accepting either valid snapshot boundary. A focused test observes `PRAGMA foreign_keys = 1` on the source, temporary destination and independent validation connections. Existing focused tests still cover populated source, missing source/LOCALAPPDATA, destination failure, failed-backup and validation cleanup, foreign-key rejection, collision preservation, WAL concurrency and source non-modification. Expected injected negative-path logs occurred with clean unittest summaries. Integration confirms the composed service backs up the initialized six-migration database without changing migration history.

Native Windows: **PASS** on actual `windows` Qt at 1000×700 using an isolated populated database. After observable idle, the File menu action was accessible and the backup ran through the worker. The published snapshot reopened with `integrity_check = ok`, zero foreign-key violations and the fixture company present. Success showed the final path and local-only guidance; a synthetic failure showed no secret text or false success, left the completed backup intact and restored the action. All four captures under `%LOCALAPPDATA%\F7Hub\CodexEvidence\Slice-038\corrected-native-jovxkx9r` were opened and inspected. This verifies the tested Windows environment, not every display scale.

## Slice 038 Delivery Gate

Production scope is the database infrastructure, one backup service, bootstrap composition and MainWindow action; focused tests are the new database backup module and existing MainWindow/bootstrap tests. Affected owner documents are Features, User Workflows, GUI, System Architecture, Database Architecture, Folder Structure, Python Architecture, Roadmap, Todo, ChangeLog and this report. Product requirements already state the backup need and require no rewrite. Physical SQL Schema, ERD, AHK and PowerShell are unaffected. Independent read-only rereview of the exact corrected unstaged candidate is required; self-review grants no integration approval.

---

## Prior Slice 037 handoff snapshot (historical; Slice 037 later merged through PR #38)

Last verified: 2026-09-29 (America/Toronto).

Current candidate: **Slice 037 — Safe Application Logging at Startup**, on `feature/safe-startup-logging-s037` in `C:\Dev\F7Hub`. The approved plan authorized implementation only. Before branching, a fresh `git fetch origin` confirmed clean `main`, an empty index/untracked set, and both HEAD and `origin/main` at `95744e36d34238f7223660392db9e38ecb8a94ac`. The protected `recovery/pre-s024-protected-work` ref remained `002a494735f30e1488f61e21ea98740ae6371d4d`; other worktrees were not changed.

Status: **PASS — READY_FOR_REVIEW** after bounded implementation, focused/affected/full regression, native Windows inspection, documentation and self-review. The Slice 036 pre-review/pre-integration request below and in Todo is **STALE HANDOFF METADATA**: live `main` contains PR #37 at `95744e3`. Slice 037 remains unstaged and uncommitted; independent review is the next gate. No push, PR or integration was performed.

## Slice 037 Result and Scope

`app.main` configures the `f7hub` logger before application bootstrap. One application-owned UTF-8 `RotatingFileHandler` writes `%LOCALAPPDATA%\F7Hub\Logs\Application\f7hub.log` with a 1 MiB limit and two backups. If path creation or handler initialization fails, a fixed warning with setup exception type only goes to stderr and an owned stderr `StreamHandler` carries subsequent application records. The process root logger is not configured and `f7hub` propagation is disabled while active. Reconfiguration replaces/closes only a prior owned handler; application exit closes the active handler and restores prior level/propagation where still controlled by the helper. Current startup success records fixed text; a bootstrap failure records fixed text and exception type only, keeping the existing safe dialog and exit code. This does not sanitize arbitrary future log calls. No database schema, migration, dependency, repository, or startup workflow expansion was added.

## Slice 037 Validation

Environment: repository `.venv\Scripts\python.exe -B`, `PYTHONPATH=$PWD\Python;$PWD`; automated GUI/Integration used `QT_QPA_PLATFORM=offscreen`. Focused logging/bootstrap **9 PASS**, affected logging/bootstrap/MainWindow **15 PASS**. Fresh Database **362 PASS**, GUI **154 PASS**, Integration **136 PASS** = **652 full regression PASS**, each suite exit 0. Expected injected negative-path logs occurred with clean unittest summaries. Isolated checks cover exact log path, UTF-8, rotation settings and rollover, root isolation, owned-handler lifecycle, safe synthetic-secret startup failure, and deterministic stderr fallback. Existing database/migration tests passed without production database changes.

Native Windows: **PASS** on the actual `windows` Qt platform. Isolated startup reached observable idle with `Ready` status at 1000×700; the log had exactly one success record. An isolated synthetic bootstrap failure displayed the unchanged safe dialog and returned exit code 1; its log contained only the fixed failure text and exception type, without the synthetic secret or traceback. Both external captures under `LOCALAPPDATA/F7Hub/CodexEvidence/Slice-037` were opened and inspected. The tested 1000×700 main window showed no observed clipping or inaccessible controls, and the failure dialog showed no secret text.

## Slice 037 Delivery Gate

Production scope is `app/main.py` and one small application logging helper; tests are isolated logging/bootstrap and existing MainWindow coverage. Updated owner documents are Features, User Workflows, System Architecture, Folder Structure, Python Architecture, Roadmap, Todo, ChangeLog and this report. GUI layout, physical SQL Schema, ERD, Database architecture, AHK and PowerShell are unaffected. The next gate is independent read-only review of the exact unstaged candidate. Self-review is not independent approval.

---

## Prior Slice 036 handoff snapshot (historical; Slice 036 later merged through PR #37)

Last verified: 2026-09-29 (America/Toronto).

Current candidate: **Slice 036 — Recent Tickets for a Saved Ticket's Company**, on `feature/company-ticket-context-s036` in `C:\Dev\F7Hub`. A fresh `git fetch origin` before editing confirmed clean `main`, HEAD and `origin/main` at `112d51cff17582756625af86f69817ccec761ef2`. The feature branch starts at that exact base. The protected `recovery/pre-s024-protected-work` ref remained `002a494735f30e1488f61e21ea98740ae6371d4d`; other worktrees were not changed.

Status: **PASS — READY_FOR_REVIEW** after implementation, focused/affected/full regression, native Windows inspection, documentation and self-review. The Slice 035 pre-review/pre-integration request below and in Todo was **STALE HANDOFF METADATA**: live `main` includes its PR #36 merge at `112d51cf`. The prior candidate report remains historical evidence. Slice 036 changes remain unstaged and uncommitted; no push, PR or integration was performed.

## Slice 036 Result and Scope

`TicketService.list_tickets` and `TicketRepository.list_tickets` accept optional `company_id`. The service rejects bool, zero, negative, non-integer and out-of-range IDs before querying; None preserves existing calls. The repository binds `company_id = ?` into the existing SELECT with Status/Priority/Type/text predicates, newest-updated/ID ordering and paging. Saved Tickets adds a Company tab with the authoritative company name and a separate `TicketTableModel`. **Load recent tickets** requests only 20 first-page tickets for the stored company ID using the shared worker. Context identity and generation guard completion after ticket/company changes. Switching tickets clears old company results; a no-company ticket disables loading. A same-context failed refresh retains previous company rows and offers retry. Opening a result uses the existing ticket-open path and unsaved-draft confirmation, without changing the main queue. No schema, migration, index, new service or dependency was added.

## Slice 036 Validation

Environment: `.venv\Scripts\python.exe -B`, `PYTHONPATH=$PWD\Python;$PWD`; automated GUI/Integration used `QT_QPA_PLATFORM=offscreen`. Focused ticket reads/company context: **35 PASS**, exit 0. Affected ticket/database/GUI/integration set: **105 PASS**, exit 0. Full Database **362 PASS**, GUI **154 PASS**, Integration **131 PASS** = **647 PASS**, all exit 0. Expected injected failure-path logs accompanied clean unittest summaries. Isolated SQLite verifies SELECT-only contents, `integrity_check = ok` and zero foreign-key violations.

Native Windows: **PASS** on the actual `windows` Qt platform at 1000×700 after observable shared-worker idle. Eight captures under `LOCALAPPDATA/F7Hub/CodexEvidence/Slice-036` were opened and inspected: initial Company tab, loaded rows, failed refresh, retry, canceled draft discard, related-ticket open, inactive company and no-company state. The visible Company tab and existing queue/detail actions showed no observed clipping, overlap or inaccessible controls in this tested environment. The main queue rows, filters, page and search draft/applied state remained coherent throughout.

## Slice 036 Delivery Gate

Production scope is the ticket repository, service and Saved Tickets workspace; tests are ticket reads and Company-context flow. Affected canonical owners are Features, User Workflows, GUI, Database architecture, Python architecture, Roadmap, Todo, ChangeLog and this report. The physical SQL Schema, ERD, system architecture, AHK and PowerShell are unaffected. The next gate is independent read-only review of the exact unstaged candidate; self-review grants no integration approval.

---

## Prior Slice 035 handoff snapshot (historical; Slice 035 later merged through PR #36)

Current candidate: **Slice 035 — Search Saved Tickets by Subject or Description**, on `feature/ticket-text-search-s035` in `C:\Dev\F7Hub`. Before editing, `git fetch origin` confirmed clean `main` with HEAD and origin/main at `f235cfde50d4e728527706440bc3c4abb56bd8c6`. The feature branch starts at that exact base. The protected `recovery/pre-s024-protected-work` ref remains `002a494735f30e1488f61e21ea98740ae6371d4d`; other worktrees were not changed.

Status: **PASS — READY_FOR_REVIEW** after implementation, validation, native Windows inspection, documentation and self-review. The Slice 034 review/integration request in the prior snapshot and Todo was **STALE HANDOFF METADATA**: live `main` includes its PR #35 merge at `f235cfde`. The prior report is historical evidence. Candidate changes remain unstaged and uncommitted; no push, PR or integration was performed for Slice 035.

## Slice 035 Result and Scope

`TicketService.list_tickets` and `TicketRepository.list_tickets` accept `include_description: bool = False`. The service rejects non-booleans before querying and keeps None/blank queries unconstrained. Default callers retain Slice 034 subject-only behavior. Saved Tickets passes True, so one submitted literal phrase matches subject or description inside a parenthesized, bound SQL predicate. NULL descriptions do not match and both-field matches return one ticket. Status/Priority/Type filters, newest-updated/ID order and bounded paging are unchanged. The existing field is labeled Search subjects and descriptions; Enter/Search/Clear, draft and applied text, worker busy state, exact-number opening and failed-read retry remain on the same path. A successful description edit may remove the queue row while its authoritative updated detail stays open, activity draft and filters remain, and the save stays acknowledged. No schema, migration, index, FTS object, dependency or new search service was added.

## Slice 035 Validation

Environment: repository `.venv\Scripts\python.exe -B`, `PYTHONPATH=$PWD\Python;$PWD` from `C:\Dev\F7Hub`. Automated GUI/Integration used `QT_QPA_PLATFORM=offscreen`; native validation used the Windows Qt platform and isolated synthetic SQLite.

| Suite | Result |
|---|---|
| Focused ticket reads/workspace | PASS — 68 tests, exit 0 |
| Affected ticket reads/service/repository/MainWindow/workspace | PASS — 85 tests, exit 0 |
| Database | PASS — 360 tests, exit 0 |
| GUI | PASS — 154 tests, exit 0 |
| Integration | PASS — 126 tests, exit 0 |

Full regression: **640 PASS**, zero failures/errors on completed suites. Expected injected error-path logs had successful unittest counts and exit 0. Isolated tests cover subject-only compatibility, description-only/both-field/NULL matches, literal `%`, `_` and backslash, filters and OR precedence, order/paging, no duplicate rows, unchanged database dump, integrity_check=ok and zero foreign-key violations. Worker-backed tests cover description search, draft/applied state, Enter/Search/Clear, filters, paging, exact-number opening, failed Search/Refresh and retry, busy protection and description-edit result exit with one write.

Native Windows: PASS — actual `windows` Qt platform at 1000×700 after observable worker idle. Eight captures under the external `f7-s035-native-captures` directory were opened and inspected. The complete Search subjects and descriptions placeholder, Search/Clear, filters, queue, detail and action controls were accessible without observed clipping or overlap. The synthetic workflow covered description-only Enter search, page 2, failed Search and Refresh with recovery, and a description edit that removed the row but retained authoritative updated detail, applied query, unsubmitted draft, note draft and truthful save feedback. This validates the tested Windows environment, not every display scale.

## Slice 035 Delivery Gate

Production scope is the ticket repository, service and Saved Tickets workspace; tests are ticket reads and workspace flow. Affected canonical owners are Features, User Workflows, GUI, Database architecture, Python architecture, Roadmap, Todo, ChangeLog and this report. The physical SQL Schema, ERD, system architecture, AHK and PowerShell are unaffected. The next gate is independent read-only review of the exact unstaged candidate; self-review grants no integration approval.

---

## Prior Slice 034 handoff snapshot (historical; Slice 034 later merged through PR #35)

Last verified: 2026-09-27 (America/Toronto).

Current candidate: **Slice 034 — Search Saved Tickets by Subject**, on feature/ticket-subject-search-s034 in C:\Dev\F7Hub. Before editing, a fresh fetch confirmed clean main with HEAD and origin/main at 6041bae3eba521cd92c2a4bcf535e541ec15b40d. The feature branch starts at that exact base. The protected recovery/pre-s024-protected-work ref remains 002a494735f30e1488f61e21ea98740ae6371d4d; other worktrees were not changed.

Status: **PASS — READY_FOR_REVIEW** after implementation, testing, native Windows inspection, documentation and self-review. All candidate changes remain unstaged and uncommitted; no push, PR or integration was performed. The Slice 033 review/integration request retained in the prior snapshot is **STALE HANDOFF METADATA**: live main contains its PR #34 merge at 6041bae. That report is historical evidence.

## Slice 034 Result and Scope

TicketService.list_tickets accepts optional subject_query, rejects non-text before repository access, trims surrounding whitespace and maps blank text to no constraint. TicketRepository adds a bound literal-substring LIKE predicate with an explicit escape clause for percent signs, underscores and backslashes. Search composes with Status, Priority and Type in the same SELECT, retaining updated-time/ID order and bounded paging. TicketWorkspace provides Search subjects, Search and Clear; Enter submits. It keeps draft text separate from the submitted query. Search and Clear start at page 1; Refresh, paging and filter changes reuse the submitted query. Failed reads retain previous rows, detail, activity drafts and requested query/page for retry. Exact-number opening preserves search and queue state. A committed subject edit may remove the row from the active search while the updated detail stays open. No database write, schema, migration, index, FTS, dependency or other ticket editor was added.

## Slice 034 Validation

Environment: repository .venv\Scripts\python.exe -B, PYTHONPATH=$PWD\Python;$PWD from C:\Dev\F7Hub. Automated GUI/Integration used QT_QPA_PLATFORM=offscreen; native validation used windows and isolated synthetic SQLite.

| Suite | Command | Final-candidate result |
|---|---|---|
| Focused ticket reads/workspace | python -B -m unittest Tests.Database.test_ticket_reads Tests.Integration.test_ticket_workspace_flow -q | PASS — 65 tests, exit 0; original fixture |
| Affected ticket set | python -B -m unittest Tests.Database.test_ticket_reads Tests.Database.test_ticket_service Tests.Database.test_ticket_repository Tests.GUI.test_main_window Tests.Integration.test_ticket_workspace_flow -q | PASS — 82 tests, exit 0; original fixture |
| Final focused ticket reads | python -B -m unittest Tests.Database.test_ticket_reads -q | PASS — 26 tests, exit 0; wildcard lookalike fixture added |
| Database | python -B -m unittest discover -s Tests\Database -p 'test_*.py' -q | PASS — 358 tests, exit 0; final fixture |
| GUI | python -B -m unittest discover -s Tests\GUI -p 'test_*.py' -q | PASS — 154 tests, exit 0; executable inputs unchanged after final Database-only test refinement |
| Integration | python -B -m unittest discover -s Tests\Integration -p 'test_*.py' -q | PASS — 125 tests, exit 0; executable inputs unchanged after final Database-only test refinement |

Full regression: **637 PASS**, zero failures/errors on completed suites. The Database suite was rerun after the final Database-only fixture refinement; GUI and Integration results remain applicable because their production code, own tests, configuration, dependencies and schema did not change. Expected injected error-path logs had successful unittest counts and exit 0. Isolated SQLite checks cover None/blank/invalid queries, literal percent/underscore/backslash and combined input, lookalike exclusions, case-insensitive ASCII matching, filter composition, ordering, paging/lookahead, unchanged database dump, integrity_check = ok and zero foreign-key violations. Worker-backed integration covers draft versus submitted input, Enter/Search/Clear, filter and page retention, exact-number opening, failed search/Refresh/paging and retry, busy protection, subject-edit result exit and one subject write.

Native Windows: PASS — actual windows Qt platform at 1000×700 after observable worker idle. Isolated synthetic tickets exercised Enter search, Clear, injected failed search, Refresh retry and subject editing out of active results with its updated detail and note draft retained. The initial, Enter search, Clear, failure, recovery and subject-exit captures under the external f7-s034-native-captures directory were opened and inspected without observed clipping, overlap or inaccessible search, queue or detail controls. This validates the tested Windows environment, not every display scale.

## Slice 034 Delivery Gate

Production scope is the ticket repository, service and Saved Tickets workspace; tests are ticket reads and workspace flow. Affected canonical owners are Features, User Workflows, GUI, Database architecture, Python architecture, Roadmap, Todo, ChangeLog and this report. Physical SQL Schema, ERD, system architecture, AHK and PowerShell remain unaffected. The next gate is independent read-only review of the exact unstaged candidate; self-review does not grant integration approval.

---

## Prior Slice 033 handoff snapshot (historical; Slice 033 later merged through PR #34)

Current candidate: **Slice 033 — Edit a Saved Ticket Type**, on `feature/ticket-type-edit-s033` in `C:\Dev\F7Hub`. Before editing, a fresh fetch confirmed clean `main`, HEAD and `origin/main` at `9f3ddab19ba4d54d619d9ce21c2887beae6558db`. The feature branch starts at that exact base. The protected `recovery/pre-s024-protected-work` ref remains `002a494735f30e1488f61e21ea98740ae6371d4d`; other worktrees were not changed.

Status: **PASS — READY_FOR_REVIEW** after implementation, testing, native Windows inspection, documentation and self-review. All candidate changes remain unstaged and uncommitted; no push, PR or integration was performed. The earlier Slice 032 review/integration request, retained in the prior snapshot below, is **STALE HANDOFF METADATA**: live `main` contains its PR #33 merge at `9f3ddab`; the prior report remains historical evidence.

## Slice 033 Result and Scope

`TicketService.update_ticket_type(ticket_id, *, expected_ticket_type, expected_updated_at, ticket_type)` validates the existing ordered type domain and loaded tokens. Within `TicketRepository.transaction()`, it rejects stale state before no-op; a real change uses a bound guarded UPDATE of only type and strictly later activity time, adds one value-free `TYPE_CHANGED` event and reloads before commit. Invalid, missing, stale and no-op requests write nothing; failed update, event or reload rolls back. `EditTicketTypeDialog` derives its choices directly from `TICKET_TYPES`, preserves selection after failure, gives stale reload guidance and blocks duplicate submission/unsafe closing during a write. Saved details show the authoritative current type. The shared worker retains committed-save acknowledgment after later reads fail; changing type can remove a row from the selected Type queue while keeping its updated detail open. No schema, migration, index, dependency, generic editor, search or Knowledge change was included.

## Slice 033 Validation

Environment: repository `.venv\Scripts\python.exe -B`, `PYTHONPATH=$PWD\Python;$PWD` from `C:\Dev\F7Hub`. Automated GUI/Integration used `QT_QPA_PLATFORM=offscreen`; native validation used `windows` and isolated synthetic SQLite.

| Suite | Command | Final-candidate result |
|---|---|---|
| Focused ticket reads/workspace/MainWindow | `python -B -m unittest Tests.Database.test_ticket_reads Tests.Integration.test_ticket_workspace_flow Tests.GUI.test_main_window` | PASS — 65 tests, exit 0 |
| Affected ticket set | `python -B -m unittest Tests.Database.test_ticket_reads Tests.Database.test_ticket_service Tests.Database.test_ticket_repository Tests.GUI.test_main_window Tests.Integration.test_ticket_workspace_flow` | PASS — 76 tests, exit 0 |
| Database | `python -B -m unittest discover -s Tests\Database -p 'test_*.py'` | PASS — 356 tests, exit 0 |
| GUI | `python -B -m unittest discover -s Tests\GUI -p 'test_*.py'` | PASS — 154 tests, exit 0 |
| Integration | `python -B -m unittest discover -s Tests\Integration -p 'test_*.py'` | PASS — 121 tests, exit 0 |

Full regression: **631 PASS**, zero failures/errors on the final completed suites. The initial focused run failed because new test methods split an existing priority test; its boundary was restored, two affected post-commit tests passed, and the entire focused, affected and full sequence passed on rerun. Expected injected error-path logs had successful unittest counts and exit 0. SQLite checks cover every type, all valid transitions, invalid/missing/stale/no-op cases, same-millisecond advancement, value-free event, update/event/reload rollback, unrelated ticket fields and links, `integrity_check = ok` and zero foreign-key violations. Integration covers Cancel, preselection, choice order, busy/stale/error behavior, detail and queue failures after commit, retry without another update, page/filter/draft retention and Type-filter exit.

Native Windows: PASS — the actual `windows` Qt platform with MainWindow at 1000×700 after observable worker idle. An isolated Incident ticket was changed to Task under the Incident filter; its row disappeared, the Task detail stayed open, Status/Priority/Type selections and note draft remained, and save feedback stayed truthful. A later type change with injected post-commit queue validation failure retained **Type saved**, refresh failure and retry guidance; Refresh recovered the queue without another type event. The [five actions](C:/Users/Jo/AppData/Local/Temp/f7-s033-native-captures/initial-actions.png), [dialog](C:/Users/Jo/AppData/Local/Temp/f7-s033-native-captures/edit-type-dialog.png), [filter exit](C:/Users/Jo/AppData/Local/Temp/f7-s033-native-captures/filter-exit.png), [failure](C:/Users/Jo/AppData/Local/Temp/f7-s033-native-captures/post-commit-failure.png) and [recovery](C:/Users/Jo/AppData/Local/Temp/f7-s033-native-captures/refresh-recovered.png) captures were opened and inspected without observed clipping, overlap or unusable controls. This validates the tested Windows environment, not every display scale.

## Slice 033 Delivery Gate

Production scope is the ticket repository, service, Saved Tickets workspace and one focused dialog; tests are ticket reads, workspace flow and MainWindow. Affected canonical owners are Features, User Workflows, GUI, Database architecture, Python architecture, Roadmap, Todo, ChangeLog and this report. Physical SQL Schema, ERD, system architecture, AHK and PowerShell remain unaffected. The next gate is independent read-only review of the exact unstaged candidate; self-review does not grant integration approval.

---

## Prior Slice 032 handoff snapshot (historical; Slice 032 later merged through PR #33)

Current candidate: **Slice 032 — Edit a Saved Ticket Description**, on `feature/ticket-description-edit-s032` in `C:\Dev\F7Hub`. Fresh fetch confirmed the approved base, branch starting HEAD and live `origin/main` at `8ff62f902aecbab8c30338c0988a7ec5032b4319` before editing; the checkout, index and untracked set were clean. The protected `recovery/pre-s024-protected-work` branch remains at `002a494735f30e1488f61e21ea98740ae6371d4d` and was not modified.

Status: **PASS — READY_FOR_REVIEW** after implementation, testing, documentation and self-review. Changes are unstaged and uncommitted; no push, PR or integration was performed. The Slice 031 claim below that review is pending is **STALE HANDOFF METADATA**: live `main` includes its PR #32 merge at `8ff62f9`. That report is retained below as a historical candidate snapshot.

## Slice 032 Result and Scope

`TicketService.update_ticket_description(ticket_id, *, expected_description, expected_updated_at, description)` validates the ID, preserves the exact nullable expected value, and normalizes submitted optional plain text using the existing creation rule. Inside `TicketRepository.transaction()`, it checks the authoritative description and timestamp before no-op. A real edit uses a bound NULL-safe guarded UPDATE of only description and strictly later activity time, adds one `DESCRIPTION_CHANGED` event without description text, and reloads before commit. Validation, missing, stale and no-op requests write nothing; update, event or reload failure rolls back. `EditTicketDescriptionDialog` preloads multiline text or an empty editor for NULL, retains drafts after failure, blocks duplicate submission and close during a write, and gives stale reload guidance. `TicketWorkspace` reuses shared worker and post-save detail/queue refresh, preserving save acknowledgment after later read failure. Filters, page, open detail and activity drafts remain; the four detail actions use a two-row grid. No schema, migration, index, dependency, other ticket edit, search or Knowledge change was included.

## Slice 032 Validation

Environment: repository `.venv\Scripts\python.exe -B`, `PYTHONPATH=$PWD\Python;$PWD` from `C:\Dev\F7Hub`. Automated GUI/Integration ran with `QT_QPA_PLATFORM=offscreen`; native validation used `windows` and isolated synthetic SQLite.

| Suite | Command | Candidate result |
|---|---|---|
| Focused ticket reads/workspace | `python -B -m unittest Tests.Database.test_ticket_reads Tests.Integration.test_ticket_workspace_flow` | PASS — 50 tests, exit 0 |
| Affected ticket set | `python -B -m unittest Tests.Database.test_ticket_reads Tests.Database.test_ticket_service Tests.Database.test_ticket_repository Tests.GUI.test_main_window Tests.Integration.test_ticket_workspace_flow` | PASS — 66 tests, exit 0 |
| Database | `python -B -m unittest discover -s Tests\Database -p 'test_*.py'` | RETAINED PASS — 352 tests, exit 0; inputs unchanged by later GUI-only layout correction |
| GUI | `python -B -m unittest discover -s Tests\GUI -p 'test_*.py'` | PASS — 153 tests, exit 0 after two-row layout correction |
| Integration | `python -B -m unittest discover -s Tests\Integration -p 'test_*.py'` | PASS — 116 tests, exit 0 after two-row layout correction |

Full regression: **621 PASS**, zero failures or errors on the completed suite runs. The Database result is retained after the GUI-only layout correction because its service, repository, tests, schema and other relevant inputs stayed unchanged; focused, affected, GUI and Integration checks passed after that correction. Isolated SQLite tests cover add/change/clear of multiline description, exact NULL/stale checks before no-op, same-millisecond timestamp advancement, one text-free event, update/event/reload rollback, unrelated data and relationship preservation, integrity and foreign keys. Integration covers Cancel, prefill, draft retention, busy protection, committed-save read failures and retry without duplicate write, filter/draft/page retention. Expected negative-path logs had successful unittest results and exit 0. The initial full GUI run had three 1000×700 width failures because four detail buttons occupied one row; a two-row grid fixed the cause, the three focused layout checks passed, and the entire GUI suite passed on rerun.

Native Windows: PASS — actual `windows` Qt platform with MainWindow at 1000×700 after observable worker idle. A synthetic ticket description was changed to multiline text; an injected post-commit queue validation failure kept **Description saved**, refresh failure and retry guidance visible. Refresh recovered the queue without a second description update. The [dialog](C:/Users/Jo/AppData/Local/Temp/f7-s032-description-dialog.png), [saved detail](C:/Users/Jo/AppData/Local/Temp/f7-s032-description-saved.png), [post-commit failure](C:/Users/Jo/AppData/Local/Temp/f7-s032-description-refresh-failed.png), and [recovery](C:/Users/Jo/AppData/Local/Temp/f7-s032-description-recovered.png) captures were opened and inspected without observed clipping or overlap. This validates the tested Windows environment, not every display scale.

## Slice 032 Delivery Gate

Production scope is the ticket repository, service, Saved Tickets workspace and one focused dialog; tests are the ticket read and workspace flow files. Affected canonical owners are Features, User Workflows, GUI, Database architecture, Python architecture, Roadmap, Todo, ChangeLog and this report. Physical SQL Schema, ERD, system architecture, AHK and PowerShell remain unaffected by this no-schema/no-dependency edit. The next gate is independent read-only review of the exact unstaged candidate; self-review does not grant integration approval.

---

## Prior Slice 031 handoff snapshot (historical; Slice 031 later merged through PR #32)

Current candidate: **Slice 031 — Edit a Saved Ticket Priority**, on `feature/ticket-priority-edit-s031` in `C:\Dev\F7Hub`. The approved base and branch HEAD are `32970e06ca9c5ca481d06cd4833e383b51f01ee3`, equal to freshly fetched `origin/main` at the implementation baseline gate. The initial checkout, index and untracked set were clean. The protected `recovery/pre-s024-protected-work` branch remains at `002a494735f30e1488f61e21ea98740ae6371d4d` and was not modified.

Status: **PASS — READY_FOR_REVIEW** after implementation, testing, documentation and self-review. Changes are unstaged and uncommitted; no push, PR or integration was performed. The prior Slice 030 claim below that rereview is pending is **STALE HANDOFF METADATA**: live `main` includes its PR #31 merge at `32970e0`. The prior report is retained below as a historical candidate snapshot.

## Slice 031 Result and Scope

`TicketService.update_ticket_priority(ticket_id, *, expected_priority, expected_updated_at, priority)` validates the positive ID and existing `TICKET_PRIORITIES` domain. Inside `TicketRepository.transaction()`, it compares authoritative priority and exact update time before no-op; a real edit uses a bound guarded UPDATE of only priority and a strictly later UTC `updated_at`, adds one `PRIORITY_CHANGED` event without priority values, and reloads before commit. Missing/stale/invalid/no-op requests write nothing; failed update, event or reload rolls back. Corrections are allowed in every ticket status. `EditTicketPriorityDialog` preselects the loaded value, retains selection after failed save, blocks duplicate submission and unsafe close during a write, and gives reload guidance for stale state. `TicketWorkspace` reuses the shared worker and post-save detail/queue refresh. A failed later read retains saved acknowledgment and retry guidance. If the new priority excludes the ticket from the current queue filter, the row disappears while saved detail and Status/Priority/Type filters remain. No schema, migration, index, dependency, other ticket edit, search or Knowledge change was included.

## Slice 031 Fresh Validation

Environment: repository `.venv\Scripts\python.exe -B`, `PYTHONPATH=$PWD\Python;$PWD` from `C:\Dev\F7Hub`. Automated GUI/Integration ran with `QT_QPA_PLATFORM=offscreen`; native validation used the `windows` platform and isolated synthetic SQLite.

| Suite | Command | Final-candidate result |
|---|---|---|
| Focused ticket reads/workspace | `python -B -m unittest Tests.Database.test_ticket_reads Tests.Integration.test_ticket_workspace_flow` | PASS — 42 tests, exit 0 |
| Affected ticket set | `python -B -m unittest Tests.Database.test_ticket_reads Tests.Database.test_ticket_service Tests.Database.test_ticket_repository Tests.GUI.test_main_window Tests.Integration.test_ticket_workspace_flow` | PASS — 58 tests, exit 0 |
| Database | `python -B -m unittest discover -s Tests\Database -p 'test_*.py'` | PASS — 349 tests, exit 0 |
| GUI | `python -B -m unittest discover -s Tests\GUI -p 'test_*.py'` | PASS — 153 tests, exit 0 |
| Integration | `python -B -m unittest discover -s Tests\Integration -p 'test_*.py'` | PASS — 111 tests, exit 0 |

Full regression: **613 PASS**, zero failures or errors; focused and affected results overlap the full suites. Real SQLite checks cover every valid priority pair, invalid and missing requests, stale priority/time before no-op, same-millisecond advancement, one value-free event, rollback after update/event/reload failure, unrelated fields/notes/status history/Knowledge link preservation, `integrity_check = ok` and zero foreign-key violations. Integration covers Cancel, authoritative choices, retained selection, stale/busy feedback, committed-save feedback after detail and three queue error categories, retry without duplicate write, and filter exit with open detail retained. Expected negative-path logs had successful unittest results and exit 0.

Native Windows: PASS — actual `windows` Qt platform with MainWindow at 1000×700 after observable worker idle. An isolated saved ticket was edited from Medium to High; an injected post-commit queue validation failure left **Priority saved**, refresh failure and retry guidance readable. Refresh recovered the queue. Changing High to Low under the selected High filter removed its row and kept Low detail open. The [dialog](C:/Users/Jo/AppData/Local/Temp/f7-s031-priority-dialog.png), [post-commit failure](C:/Users/Jo/AppData/Local/Temp/f7-s031-priority-refresh-failed.png) and [filter exit](C:/Users/Jo/AppData/Local/Temp/f7-s031-priority-filter-exit.png) captures were opened and inspected without observed clipping or overlap. This validates the tested Windows environment, not every display scale.

## Slice 031 Delivery Gate

Implementation self-review found no blocking defect. Production scope is the ticket repository, service, Saved Tickets workspace and one focused dialog; tests are the ticket read and workspace flow files. Affected canonical owners are Features, User Workflows, GUI, Database architecture, Python architecture, Roadmap, Todo, ChangeLog and this report. Product requirement FR-TICKET-003 remains broader than these two edit slices. Physical SQL Schema, ERD, system architecture, AHK and PowerShell owners were inspected or considered but have no behavior change. The next gate is independent read-only review of the exact unstaged candidate; self-review does not grant integration approval.

Exact candidate scope: modified `Python/f7hub/repositories/ticket_repository.py`, `Python/f7hub/services/ticket_service.py`, `Python/f7hub/gui/ticket_workspace.py`, `Tests/Database/test_ticket_reads.py`, `Tests/Integration/test_ticket_workspace_flow.py`, `Docs/03_Features.md`, `Docs/04_UserWorkflows.md`, `Docs/05_GUI.md`, `Docs/07_Database.md`, `Docs/13_PythonArchitecture.md`, `Docs/16_Roadmap.md`, `Docs/17_Todo.md`, `Docs/18_ChangeLog.md` and this file; created untracked `Python/f7hub/gui/edit_ticket_priority_dialog.py`. No staged or deleted paths. Native captures were taken after final production and test bytes stabilized.

---

## Prior Slice 030 handoff snapshot (historical; Slice 030 later merged through PR #31)

Current candidate: **Slice 030 — Edit a Saved Ticket Subject**, on `feature/ticket-subject-edit-s030` in `C:\Dev\F7Hub`. Approved base and branch HEAD are `cdd49fac734d6bedfecf58aacfea4846b8a6e79d`, equal to fetched `origin/main` at the implementation baseline gate. The checkout, index and untracked set were initially clean. The protected `recovery/pre-s024-protected-work` branch remains at `002a494735f30e1488f61e21ea98740ae6371d4d` and was not modified.

Status: **PASS — READY_FOR_REVIEW after correction**, with independent read-only rereview pending. The first independent review found a post-commit queue-refresh feedback defect; the previous review decision is invalidated by this correction. Authorization covered the bounded correction, testing and documentation only. The candidate remains unstaged and uncommitted; no push, PR or integration was performed. The prior Slice 029 Todo/current-state claim that rereview was pending is **STALE HANDOFF METADATA**: live `main` includes its PR #30 merge at `cdd49fa`. The previous report below is retained as a historical handoff snapshot.

## Slice 030 Result and Scope

`TicketService.update_ticket_subject(ticket_id, *, expected_subject, expected_updated_at, subject)` validates the loaded subject and exact update timestamp inside the existing repository writer transaction before deciding no-op. A real change trims required text, uses a bound guarded UPDATE for only subject and a strictly later UTC activity timestamp, creates exactly one `SUBJECT_CHANGED` timeline event without either subject value, and reloads the authoritative row before commit. Missing/stale state and invalid input create no event; update, event or reload failure rolls back. The correction is permitted in every ticket status. The Save dialog is prefilled, keeps entered text on failure, blocks duplicate submission and close during a write, and asks for a reload after conflict. Successful commit reuses the existing detail and queue reload path. The review correction preserves **Subject saved** and Refresh retry guidance for every post-commit queue failure, including `TicketValidationError`, without changing ordinary queue-read feedback; a later detail read failure still acknowledges the save and offers Reload ticket. Notes/status drafts remain intact. No schema, migration, index, dependency, description edit, other ticket edit, search or Knowledge change is included.

## Slice 030 Fresh Validation

Environment: repository `.venv\Scripts\python.exe -B`, `PYTHONPATH=$PWD\Python;$PWD` from `C:\Dev\F7Hub`. Automated GUI/Integration ran with `QT_QPA_PLATFORM=offscreen`; native validation used `windows` with isolated synthetic SQLite.

| Suite | Command | Final-candidate result |
|---|---|---|
| Focused ticket reads/workspace | `python -B -m unittest Tests.Database.test_ticket_reads Tests.Integration.test_ticket_workspace_flow` | PASS — 34 tests, exit 0 |
| Affected ticket set | `python -B -m unittest Tests.Database.test_ticket_reads Tests.Database.test_ticket_service Tests.Database.test_ticket_repository Tests.GUI.test_main_window Tests.Integration.test_ticket_workspace_flow` | PASS — 50 tests, exit 0 |
| Database | `python -B -m unittest discover -s Tests\Database -p 'test_*.py'` | PASS — 345 tests, exit 0 |
| GUI | `python -B -m unittest discover -s Tests\GUI -p 'test_*.py'` | PASS — 153 tests, exit 0 |
| Integration | `python -B -m unittest discover -s Tests\Integration -p 'test_*.py'` | PASS — 107 tests, exit 0 |

Full regression: **605 PASS**, zero failures/errors; focused and affected tests overlap the full suites. Real SQLite tests cover normalization, no-op and stale-before-no-op validation, missing ticket, closed-ticket correction, same-millisecond timestamp advancement, one text-free event, rollback for update/event/reload failure, unrelated field/note/relationship preservation, `integrity_check = ok` and zero foreign-key violations. Integration covers Cancel, retained input, stale feedback, duplicate/busy protection, detail and queue refresh, and committed-save feedback after either later read fails. The corrected test covers RuntimeError, TicketValidationError and TicketReadError queue failures after commit, verifies one update per edit and no duplicate on Refresh, and checks that an ordinary queue validation error keeps its prior behavior. Expected error-path log messages had successful unittest outcomes and exit 0.

Native Windows: PASS — actual `windows` Qt platform with the MainWindow at 1000×700, after observable worker idle. A persisted ticket was opened and its prefilled subject corrected. A simulated validation failure after commit left the new detail visible and the old queue row available. The [post-commit failure capture](C:/Users/Jo/AppData/Local/Temp/f7-s030-correction-refresh-failed.png) and [recovered queue capture](C:/Users/Jo/AppData/Local/Temp/f7-s030-correction-refresh-recovered.png) were opened and inspected: saved acknowledgment, refresh failure, retry guidance and controls were readable without observed overlap. Refresh then loaded the committed subject into the queue. This verifies the tested Windows environment, not every display scale.

## Slice 030 Delivery Gate

The independent review's one blocking post-commit feedback finding has been corrected and self-validated; independent rereview remains required. Production scope is the ticket repository, service, saved-ticket workspace and one focused dialog; tests are the ticket read and workspace flow files. Affected canonical owners are Features, User Workflows, GUI, Database architecture, Python architecture, Roadmap, Todo, ChangeLog and this status report. Product requirement FR-TICKET-003 remains broader than this first edit slice. Physical SQL Schema, ERD, system architecture, AHK and PowerShell owners have no behavioral change. No independent approval has been granted. The next gate is independent read-only rereview of the exact unstaged candidate; implementation evidence does not authorize staging or integration.

Exact candidate scope: modified `Python/f7hub/repositories/ticket_repository.py`, `Python/f7hub/services/ticket_service.py`, `Python/f7hub/gui/ticket_workspace.py`, `Tests/Database/test_ticket_reads.py`, `Tests/Integration/test_ticket_workspace_flow.py`, `Docs/03_Features.md`, `Docs/04_UserWorkflows.md`, `Docs/05_GUI.md`, `Docs/07_Database.md`, `Docs/13_PythonArchitecture.md`, `Docs/16_Roadmap.md`, `Docs/17_Todo.md`, `Docs/18_ChangeLog.md` and this file; created untracked `Python/f7hub/gui/edit_ticket_subject_dialog.py`. No staged or deleted paths. The bounded review correction changed only the workspace callback, integration coverage, Todo, ChangeLog and this status report. Focused and affected tests were run before the three full suites; documentation changed afterward without changes to code, tests, schema, configuration or dependencies. Native captures were taken after the final code and test bytes stabilized.

---

## Prior Slice 029 handoff snapshot (historical; Slice 029 later merged through PR #30)

Last verified: 2026-09-27 (America/Toronto).

Current candidate: **Slice 029 — Filter Saved Tickets by Type**, `feature/ticket-type-filter-s029` in `C:\Dev\F7Hub`. Approved base and branch HEAD: `1b66f3e888ab24eb1b1fefde2d74e3f60ebba84b`, equal to freshly fetched `origin/main` at the implementation baseline gate. Tracked, staged and untracked state was initially clean. The protected `recovery/pre-s024-protected-work` branch remains at `002a494735f30e1488f61e21ea98740ae6371d4d` and was not modified.

Status: **PASS — READY_FOR_REVIEW after correction**. The first independent review required removing the Type selector's duplicated ticket-type list. That review decision no longer applies to the corrected candidate; independent rereview is pending. Authorization covers correction, testing and documentation only. Candidate changes remain unstaged and uncommitted. No push, PR or integration was performed for Slice 029. Earlier text below describing Slice 028 as awaiting review is **STALE HANDOFF METADATA**: live Git shows Slice 028 merged through PR #29 at `1b66f3e`; that text is retained as a historical candidate snapshot.

## Slice 029 Result and Scope

Saved Tickets adds Type below Priority: All types, Incident, Service request, Problem and Task. All types passes `ticket_type=None`. After review correction, the selector iterates the existing `TICKET_TYPES` vocabulary directly in its established display order; labels are presentation-only. `TicketService.list_tickets` rejects invalid non-None types before querying; `TicketRepository.list_tickets` adds a bound Type predicate alongside Status and Priority in one SQL query. Newest-updated ordering and bounded paging are unchanged. Any filter change requests page 1; Refresh, paging and exact-number opening retain all three selections. The shared worker disables all three selectors while busy. A failed queue read retains prior rows, detail, drafts and selections and records the requested page for Refresh retry. This slice adds no database write, schema, migration, index, dependency, category reference, ticket editing, search or Knowledge change.

## Slice 029 Fresh Validation

Environment: repository `.venv\Scripts\python.exe -B`, `PYTHONPATH=$PWD\Python;$PWD` from `C:\Dev\F7Hub`. Automated GUI/Integration used `QT_QPA_PLATFORM=offscreen`; native validation used `windows` against isolated synthetic SQLite.

| Suite | Command | Fresh final-candidate result |
|---|---|---|
| Focused ticket reads/workspace | `python -B -m unittest Tests.Database.test_ticket_reads Tests.Integration.test_ticket_workspace_flow` | PASS — 25 tests, exit 0 |
| Affected ticket set | `python -B -m unittest Tests.Database.test_ticket_reads Tests.Database.test_ticket_service Tests.Database.test_ticket_repository Tests.GUI.test_main_window Tests.Integration.test_ticket_workspace_flow` | PASS — 41 tests, exit 0 |
| Database | `python -B -m unittest discover -s Tests\Database -p 'test_*.py'` | PASS — 341 tests, exit 0 |
| GUI | `python -B -m unittest discover -s Tests\GUI -p 'test_*.py'` | PASS — 153 tests, exit 0 |
| Integration | `python -B -m unittest discover -s Tests\Integration -p 'test_*.py'` | PASS — 102 tests, exit 0 |

Full regression: **596 PASS**, zero failures or errors. Focused and affected results overlap the full suites. Real-SQLite tests cover all four valid types, invalid and SQL-like values, service rejection before repository querying, three-filter composition, stable paging/order, unchanged before/after database dump, `integrity_check = ok` and zero foreign-key violations. Integration tests cover selector order/accessibility, page-1 reset, Refresh/page/Open number retention, busy-state disabling, failure preservation and requested-page retry. Expected error-path log messages in GUI/Integration had successful unittest results and exit 0.

Native Windows after correction: PASS — actual `windows` Qt platform with MainWindow at 1000×700, Open + High + Service request selected, one matching synthetic ticket and current detail loaded after observable worker idle. The [corrected-candidate capture](C:/Users/Jo/AppData/Local/Temp/f7-s029-correction-native.png) was opened and inspected: all three selectors, queue, detail and activity controls were readable without observed overlap or clipped controls. The native harness also checked that the options equal `TICKET_TYPES` once each and that All types carries `None`. This verifies the tested Windows environment, not every display scale.

## Slice 029 Delivery Gate

The review finding was corrected by making the service's single authoritative `TICKET_TYPES` sequence ordered and having the workspace iterate it directly. `_choice` now accepts that collection type; validation behavior is unchanged. The integration test checks each authoritative type exactly once and All types as `None`. Focused, affected and full regression counts above were rerun on the correction and all passed. Scope remains the same 13 tracked paths: the ticket repository/service/workspace, two focused test files and affected documentation. Database architecture and SQL Schema need no edit because the physical schema and indexes are unchanged. AHK, PowerShell and Knowledge owners are unaffected. The next gate is independent read-only rereview of the new unstaged candidate; this self-review grants no integration approval.

---

## Prior Slice 028 handoff snapshot (historical; Slice 028 later merged through PR #29)

Last verified: 2026-09-27 (America/Toronto).

Current candidate: **Slice 028 — Filter Saved Tickets by Priority**, `feature/ticket-priority-filter-s028` in `C:\Dev\F7Hub`. Approved base and current branch HEAD: `ce55c5a355bbc8434b3b536001e3dd393147821d`, equal to freshly fetched `origin/main` at the implementation baseline gate. The initial tracked, staged and untracked state was clean. Slice 027 was merged through PR #28. The protected `recovery/pre-s024-protected-work` branch remains at `002a494735f30e1488f61e21ea98740ae6371d4d` and was not modified.

Status: **PASS — READY_FOR_REVIEW**. Authorization covers IMPLEMENT → TEST → DOCUMENT only. Candidate files are unstaged and uncommitted; independent review is pending. No push, PR or integration was performed for Slice 028.

## Slice 028 Result and Scope

Saved Tickets adds a Priority selector below Status/Refresh. All priorities passes `None`; Critical, High, Medium and Low reuse the existing priority vocabulary. `TicketService.list_tickets` validates the optional priority, and `TicketRepository.list_tickets` composes it with Status using bound SQL values while preserving `updated_at DESC, ticket_id DESC` and bounded paging. Both filter changes reset to page 1. Refresh, page navigation and exact-number opening preserve both selections and the applicable page. Reads remain on the shared worker; both filter controls disable while it is busy. A failed replacement keeps the last successful rows, current detail, activity drafts and selected filters; Refresh retries the requested page, including page 1 after a failed filter change. The feature makes no database write and adds no schema, migration, index, dependency, ticket-text search or unrelated Knowledge change.

## Slice 028 Fresh Validation

Environment: repository `.venv\Scripts\python.exe -B`, `PYTHONPATH=$PWD\Python;$PWD` from `C:\Dev\F7Hub`. Automated GUI/Integration tests used `QT_QPA_PLATFORM=offscreen`; native validation used `windows` against isolated synthetic SQLite.

| Suite | Command | Fresh final-candidate result |
|---|---|---|
| Focused ticket reads/workspace | `python -B -m unittest Tests.Database.test_ticket_reads Tests.Integration.test_ticket_workspace_flow` | PASS — 22 tests, exit 0 |
| Affected ticket set | `python -B -m unittest Tests.Database.test_ticket_reads Tests.Database.test_ticket_service Tests.Database.test_ticket_repository Tests.GUI.test_main_window Tests.Integration.test_ticket_workspace_flow` | PASS — 38 tests, exit 0 |
| Database | `python -B -m unittest discover -s Tests\Database -p 'test_*.py'` | PASS — 340 tests, exit 0 |
| GUI | `python -B -m unittest discover -s Tests\GUI -p 'test_*.py'` | PASS — 153 tests, exit 0 |
| Integration | `python -B -m unittest discover -s Tests\Integration -p 'test_*.py'` | PASS — 100 tests, exit 0 |

Full regression: **593 PASS**, zero failures or errors. Focused and affected results overlap the full suites. Real-SQLite checks cover all priority modes, priority/status composition, stable ordering, paging, invalid values, SQL-like input, unchanged before/after database dump, `integrity_check = ok` and zero foreign-key violations. Integration tests cover filter choice order/accessibility, page/Refresh/direct-open preservation, disabled selectors during a delayed read, failure preservation and retry from page 2 to the requested page 1. The initial full GUI run failed three 1000×700 layout checks because placing Priority in the Status row raised the window minimum width to 1176px. Moving Priority to its own row fixed the layout. A later self-review found the failed-filter page retry edge and added a pending requested offset; focused, affected and all three full suites passed after that final production change.

Native Windows: PASS — actual `windows` Qt platform with MainWindow at 1000×700, High and Open selected, one matching synthetic ticket and current detail loaded after observable worker idle. A first harness attempt checked workspace visibility before navigating away from New Ticket and stopped before validating the feature; the corrected harness passed. The [final post-fix capture](C:/Users/Jo/AppData/Local/Temp/f7-s028-native-final-d40ee4e8bcd94da8bea2371029ca0f02.png) was opened and inspected: both filter controls, queue, ticket detail and activity controls were readable without observed overlap or clipped controls. This verifies the tested Windows environment, not every display scale.

## Slice 028 Delivery Gate

Implementation self-review found no remaining blocking defect. Only the approved ticket repository/service/workspace, focused tests and affected documentation changed. Documentation owners affected: Features, User Workflows, GUI, Python Architecture, Roadmap, Todo, ChangeLog and this report. Database architecture and SQL Schema were inspected but require no edit because physical schema, migrations and indexes did not change. AHK, PowerShell and Knowledge owners are unaffected. The next gate is independent read-only review of the exact unstaged candidate; this self-review grants no integration approval.

---

## Prior Slice 027 handoff snapshot (historical; Slice 027 later merged through PR #28)

Last verified: 2026-09-26 (America/Toronto).

Current candidate: **Slice 027 — Open a saved ticket by number**, `feature/ticket-number-open-s027` in `C:\Dev\F7Hub`. Base and current HEAD: `db81aff585d309e7db605d667fbd8332d0d1863a`, equal to freshly fetched `origin/main` at the implementation baseline gate. The initial tracked, staged and untracked scope was clean. Slice 026 is merged through PR #26; the preserved `recovery/pre-s024-protected-work` branch remains read-only at `002a494735f30e1488f61e21ea98740ae6371d4d`.

Status: **PASS — READY_FOR_REVIEW**. The user authorized IMPLEMENT → TEST → DOCUMENT only. The Slice 027 changes are unstaged and uncommitted; independent review is pending. No push, PR or integration occurred.

## Slice 027 Result and Scope

Saved Tickets adds an exact Ticket number field and Open number action. Enter and the button use the same `TicketService.get_ticket_details_by_number` call through the existing runner. The service trims input, reuses the case-insensitive repository lookup, and reloads current details through `get_ticket_details`. Blank GUI input makes no query. A successful open can display a ticket outside the visible status-filtered page without changing the filter or page. The entered number remains for retry. Missing/read-failure/disappearing-ticket paths and Cancel on the existing draft-discard confirmation preserve current detail and activity drafts. No repository query, database write, schema, migration, dependency or new exception hierarchy was added.

## Slice 027 Fresh Validation

Environment: repository `.venv\Scripts\python.exe -B`, `PYTHONPATH=$PWD\Python;$PWD` from `C:\Dev\F7Hub`. Automated GUI/Integration tests used `QT_QPA_PLATFORM=offscreen`; native validation used `windows`.

| Suite | Command | Fresh result |
|---|---|---|
| Focused ticket reads/workspace | `python -B -m unittest Tests.Database.test_ticket_reads Tests.Integration.test_ticket_workspace_flow` | PASS — 19 tests, exit 0, 25.138s |
| Affected ticket set | `python -B -m unittest Tests.Database.test_ticket_reads Tests.Database.test_ticket_service Tests.Database.test_ticket_repository Tests.GUI.test_main_window Tests.Integration.test_ticket_workspace_flow` | PASS — 35 tests, exit 0, 26.322s |
| Database | `python -B -m unittest discover -s Tests\Database -p 'test_*.py'` | PASS — 339 tests, exit 0, 24.343s |
| GUI | `python -B -m unittest discover -s Tests\GUI -p 'test_*.py'` | PASS — 153 tests, exit 0, 158.378s |
| Integration | `python -B -m unittest discover -s Tests\Integration -p 'test_*.py'` | PASS — 98 tests, exit 0, 267.124s |

Full regression: **590 PASS**, zero failures or errors. Focused/affected results overlap the full suites. Real-SQLite tests verify exact/case-insensitive match, complete current details, no match for a prefix, unchanged before/after database dump, validation, missing/disappearing-ticket and safe read-error handling. UI/integration tests verify Enter/button, preservation of Page 2, out-of-filter opening, blank input without a service call, busy duplicate prevention, retained input, cancellation and draft/detail preservation. The first focused attempt failed because test setup left a SQLite handle open and placed the target on page one; both fixtures were corrected before the passing reruns. Candidate implementation did not change to resolve those fixture failures.

Native Windows: PASS — actual 1000×700 MainWindow with isolated synthetic SQLite, `QT_QPA_PLATFORM=windows`. The harness waited for visible/enabled/idle MainWindow and Saved Tickets states before interaction. Button lookup opened a ticket outside an empty Closed queue while preserving the filter and input; Enter opened another. The [final MainWindow capture](C:/Users/Jo/AppData/Local/Temp/f7-s027-native-final-1000x700.png) was opened and inspected after the final test change: the number controls, queue, detail and status actions were readable with no observed clipping or overlap. This verifies the tested Windows environment, not every display scale.

## Slice 027 Delivery Gate

Self-review found no blocking defect. Only the approved service, GUI, focused tests and affected canonical documents changed. Ticket text/prefix/universal search, migrations, repository redesign and the protected recovery branch remain outside scope. The next gate is independent read-only review of the exact unstaged candidate.

---

## Prior Slice 026 handoff snapshot (historical; Slice 026 later merged into `main`)

Last verified: 2026-09-26 (America/Toronto).

Current candidate: **Slice 026 — Show current Knowledge article dates**, `feature/knowledge-article-dates-s026` in `C:\Dev\F7Hub`. Base and current HEAD: `c9a1a85a3b04afbf4a856379f3f0485dbf5d4351`, equal to live `origin/main` at the implementation baseline gate. Initial tree, index and untracked scope were clean. Slice 025 is CLOSED on this base. The preserved `recovery/pre-s024-protected-work` branch remains read-only at `002a494735f30e1488f61e21ea98740ae6371d4d`.

Status: **PASS — READY_FOR_REVIEW**. The user authorized IMPLEMENT → TEST → DOCUMENT only. No staging, commit, push, PR or integration occurred; independent Slice 026 review is pending.

## Slice 026 Result and Scope

KnowledgeWorkspace shows one wrapping plain-text line below Version: `Created: <created_at> · Last updated: <updated_at>`. The values come directly from the existing authoritative current-article record and are cleared with empty, missing or failed detail. They are displayed exactly as persisted, with no timezone conversion or timestamp semantics change. Selection, search and Ticket Open Article use the existing detail path. Production changes are confined to `Python/f7hub/gui/knowledge_workspace.py`; focused GUI and real-SQLite integration tests changed. No repository query, service API, database write, schema change, migration or dependency was added. Author, publication date, history comparison, restore/revert, date filters and relationship work remain outside this slice.

## Slice 026 Fresh Validation

Environment: repository `.venv\Scripts\python.exe -B`, `PYTHONPATH=$PWD\Python;$PWD` from `C:\Dev\F7Hub`. Automated GUI/Integration tests used `QT_QPA_PLATFORM=offscreen`; native validation used `windows`.

| Suite | Command | Fresh result |
|---|---|---|
| Focused GUI | `python -B -m unittest Tests.GUI.test_knowledge_workspace.KnowledgeWorkspaceTests.test_current_article_dates_follow_selection_without_extra_read Tests.GUI.test_knowledge_workspace.KnowledgeWorkspaceTests.test_current_article_dates_clear_on_missing_failed_and_empty_detail` | PASS — 2 tests, exit 0 |
| Focused real SQLite | `python -B -m unittest Tests.Integration.test_knowledge_base_flow.KnowledgeBaseFlowTests.test_current_dates_match_persisted_article_through_updates_and_search Tests.Integration.test_ticket_knowledge_flow.TicketKnowledgeFlowTests.test_link_read_and_second_article_navigation` | PASS — 2 tests, exit 0 |
| Database | `python -B -m unittest discover -s Tests\Database -p 'test_*.py'` | PASS — 336 tests, exit 0, 22.152s |
| GUI | `python -B -m unittest discover -s Tests\GUI -p 'test_*.py'` | PASS — 153 tests, exit 0, 158.013s |
| Integration | `python -B -m unittest discover -s Tests\Integration -p 'test_*.py'` | PASS — 95 tests, exit 0, 244.387s |

Full regression: **584 PASS**, zero failures. Focused results overlap the full suites. Real-SQLite checks compare the displayed values with `knowledge_articles` after creation, content revision, category assignment and publication, then reopen through FTS and compare before/after database dumps for viewing. The existing Ticket Open Article workflow now asserts the displayed current values. GUI checks cover selection changes, exact plain text, no extra detail read, and empty/missing/failed clearing.

Native Windows: PASS — actual 1000×700 MainWindow with a persisted and revised synthetic article, `QT_QPA_PLATFORM=windows`. The [MainWindow capture](C:/Users/Jo/AppData/Local/Temp/f7-s026-native-kavuy1ap/main-dates.png) was opened and inspected. The added line is readable, there is no observed clipping or overlap around it, and the body remains visible at 272 px high. This verifies the tested Windows environment, not every display scale. The first temporary harness attempt called `show_knowledge` while the initial main-window load was busy and failed before selecting an article; waiting for that load fixed the harness, with no candidate change.

## Slice 026 Delivery Gate and Skill v0.1 Observations

Self-review found no blocking defect; the next gate is independent read-only review of the exact unstaged candidate. The v0.1 baseline and scope gates prevented starting from stale handoff prose: live Git verification established the approved Slice 025 merged base while the old CURRENT_STATE/Todo still described its pre-review candidate. Its phase examples still name Slice 024. Focused and full tests remained separate, and native inspection caught a harness sequencing assumption before validating layout. Across Slices 024–026, full regressions took several minutes each; a v0.2 skill evaluation should consider this runtime and the value of native evidence. No skill change or Slice 027 work is part of this candidate.

---

## Prior Slice 025 handoff snapshot (historical; Slice 025 later closed on `main`)

Last verified: 2026-09-26 (America/Toronto).

Current candidate: **Slice 025 — All of selected Knowledge tags**, `feature/knowledge-all-selected-tags-s025` in `C:\Dev\F7Hub`. Base and current HEAD: `1c684a38d6b50a040f31c4b420e0bab9152d8c66`, equal to freshly fetched `origin/main` at the implementation baseline gate. Initial tree/index/untracked scope was clean. The preserved `recovery/pre-s024-protected-work` branch at `002a494735f30e1488f61e21ea98740ae6371d4d` was read-only evidence and remains untouched.

Status: **PASS — READY_FOR_REVIEW**. The user approved the Slice 025 plan and IMPLEMENT → TEST → DOCUMENT only. No staging, commit, push, PR or integration occurred. Independent review is pending.

## Slice 025 Result and Scope

The existing cached tag dialog now offers **Match any selected tag** and **Match all selected tags**. Two or more IDs use the chosen mode; zero and one collapse to All tags or the specific tag. `KnowledgeService.list_articles/search_articles` and `KnowledgeRepository` add `match_all_tags: bool = False`. True requires at least two distinct positive IDs in `tag_ids`, with contradictory modes rejected before querying. The All predicate counts only bridge rows for the bound selected IDs and compares that count with the selection size; the bridge primary key prevents duplicate relationships. Normal list order, current FTS MATCH/bm25 ranking and one row per article remain intact.

The workspace retains All mode through valid reference renames and partial deletion while at least two IDs survive, collapses to specific/All when fewer remain, and preserves cached choices after a failed tag read. Switching Any/All reruns the current list or last executed search without submitting unsubmitted input. Category/Status, Clear Search, tag mutation reconciliation and Ticket Open Article reset use existing paths. No migration, schema, FTS object, tag write, dependency or new service/repository layer was added. Custom tag expressions and revision restore/revert remain deferred.

Production changes are limited to `Python/f7hub/{gui/knowledge_tag_filter_dialog.py,gui/knowledge_workspace.py,repositories/knowledge_repository.py,services/knowledge_service.py}`. Focused tests changed `Tests/Database/test_knowledge_tag_filter.py`, `Tests/GUI/{test_knowledge_tag_filter.py,test_knowledge_tag_filter_dialog.py}` and `Tests/Integration/test_ticket_knowledge_flow.py`. No files were created or deleted. Documentation owners updated: Features, User Workflows, GUI, Database, Python Architecture, Roadmap, Todo, ChangeLog and this report. `Docs/09_SQLSchema.md`, ERD, AHK and PowerShell owners are unaffected.

## Slice 025 Validation

Environment: repository `.venv\Scripts\python.exe -B`, `PYTHONPATH=$PWD\Python;$PWD` from `C:\Dev\F7Hub`. Automated GUI/Integration suites used `QT_QPA_PLATFORM=offscreen`; the native check used `windows`.

| Suite | Command | Fresh result |
|---|---|---|
| Database | `python -B -m unittest discover -s Tests\Database -p 'test_*.py'` | PASS — 336 tests, exit 0, 28.247s |
| GUI | `python -B -m unittest discover -s Tests\GUI -p 'test_*.py'` | PASS — 151 tests, exit 0, 160.494s |
| Integration | `python -B -m unittest discover -s Tests\Integration -p 'test_*.py'` | PASS — 94 tests, exit 0, 247.539s |

Total full regression: **581 PASS**, zero failures. Focused new-path checks also passed: Database tag-filter module 9 tests, GUI tag-dialog module 3, workspace tag-filter module 17, new ticket-open test 1, and later callback-order/mutation tests 2; these overlap the full suites. Database tests cover partial/full/no intersections, Category/Status composition, FTS relative ranking, direct/service validation, query-only reads, unchanged dumps, `integrity_check = ok` and zero foreign-key violations. GUI/Integration tests cover mode switching, Cancel/unchanged Apply, zero/one collapse, keyboard controls, both refresh callback orders, partial failure/retry, tag mutation and Ticket Open Article reset.

Native Windows: PASS — actual 1000×700 MainWindow, All of 2 tags, one matching synthetic article and visible dialog actions. The [dialog capture](C:/Users/Jo/AppData/Local/Temp/f7-s025-native-ad8r8erf/dialog-all.png) and [MainWindow capture](C:/Users/Jo/AppData/Local/Temp/f7-s025-native-ad8r8erf/main-all.png) were opened and visually inspected. The filter row, list/detail, radio choices, check list and Cancel/Apply fit without observed clipping or overlap. This verifies the tested Windows environment, not every DPI configuration. The first native harness attempt lacked `PYTHONPATH` and exited before app construction; the corrected harness passed without a production change.

## Slice 025 Delivery Gate and Skill v0.1 Observations

Self-review found no remaining blocking defect. The final candidate must still be audited against the exact unstaged diff and reviewed independently; this report does not grant approval. The next gate is an independent read-only review of this candidate. The recovery branch is excluded from candidate scope.

The v0.1 baseline gate caught no drift: fresh origin, branch, HEAD, index and untracked checks matched the approved plan before branch creation. The explicit test gate kept focused and full results separate; full suite runtime was about 436 seconds across three suites. The native gate required actual Windows captures after offscreen tests. The stale pre-review Slice 024 wording in this file and Todo needed direct correction in the current handoff, while historical changelog evidence stayed labeled by its date. One harness setup failure exposed a missing `PYTHONPATH`, then passed after correction. Propose a v0.2 skill review after Slices 024–026 as the skill requests; do not change the skill or begin Slice 026 here.

---

## Prior Slice 024 handoff snapshot (historical; Slice 024 later merged into `main` through PR #24)

Last verified: 2026-09-26 (America/Toronto)

Current candidate: Slice 024, `feature/knowledge-any-tag-filter-s024` in isolated `C:\Dev\F7Hub-S024`.

Base and current HEAD: `02733c29f1b9d960383e00844aa8535c830efb52` (`origin/main` at the implementation baseline check).

Status: PASS — READY FOR INDEPENDENT SLICE 024 REVIEW. Implementation, all required automated suites, database read-only/integrity checks and native Windows inspection are complete. The candidate remains unstaged and uncommitted; independent review and integration are NOT complete.

## Slice 024 Result and Scope

Any of two or more selected existing global tags now filters current Knowledge lists and FTS results. The existing All, Untagged and single-tag modes remain. `KnowledgeService.list_articles` and `search_articles` accept an optional `tag_ids` tuple, validate distinct positive non-bool IDs and mutually exclusive tag modes, then pass bound values to the repository's correlated `EXISTS` predicate. Current article reads return both display names and stable tag IDs. Zero selected tags mean All; one uses the prior specific-tag mode. No database write, schema, migration, index, FTS object, tag mutation or dependency was added.

The cached-choice dialog is opened from the existing Tag filter. Cancel or unchanged Apply requests no result. Changed choices use the existing asynchronous article runner. Category/Status composition, last executed search query, unsubmitted input, Clear Search, explicit Ticket Open Article reset and authoritative article/tag reconciliation remain intact. Successful reference refresh retains surviving selected IDs across renames/deletions and coalesces one final reload; failed tag refresh preserves cached choices for retry. Multi-tag AND/expression filtering and restore/revert remain deferred.

## Slice 024 Validation

Environment: `C:\Dev\F7Hub\.venv\Scripts\python.exe`; `PYTHONPATH=$PWD\Python;$PWD` from the isolated worktree. GUI/Integration regression used `QT_QPA_PLATFORM=offscreen`; the native check used `windows`.

| Suite | Command | Result |
|---|---|---|
| Database | `python -m unittest discover -s Tests/Database -p 'test_*.py'` | PASS — 334 tests, exit 0, 22.970s |
| GUI | `python -m unittest discover -s Tests/GUI -p 'test_*.py'` | PASS — 146 tests, exit 0, 132.120s |
| Integration | `python -m unittest discover -s Tests/Integration -p 'test_*.py'` | PASS — 93 tests, exit 0, 239.095s |

Total full regression: **573 PASS**, zero failures. Focused Database, GUI and ticket-flow checks preceded the full suites. The Database tests exercise query-only connections and identical before/after dumps, `PRAGMA integrity_check = ok`, zero foreign-key violations, list/search composition, FTS order and no duplicate rows. GUI/Integration tests exercise Cancel/no-op, zero/one/multiple selection, keyboard input, reference rename/deletion/failure/retry, executed-query preservation, tag mutation and Ticket Open Article reveal. An initial GUI failure exposed tuple lookup through Qt `findData`; matching explicit item data fixed it before the passing full runs. A first native harness attempt lacked a `QApplication` before constructing widgets; the corrected harness passed without a production-code change.

Native Windows: PASS — actual 1000×700 MainWindow, Any of 2 tags, one matching synthetic article, visible Cancel/Apply controls. The [MainWindow capture](C:/Users/Jo/AppData/Local/Temp/f7-s024-native-xoyfxyey/main-any.png) and [dialog capture](C:/Users/Jo/AppData/Local/Temp/f7-s024-native-xoyfxyey/dialog-any.png) were opened and visually inspected: no forced oversize, clipping, overlap, hidden filter control or broken detail view was observed. This verifies the tested Windows environment, not every DPI configuration.

## Slice 024 Delivery Gate

The approved plan was implemented in an isolated worktree because the root checkout was already dirty on `feature/knowledge-any-tag-filter`. That root work is protected and was not copied, edited or staged. Production changes are confined to Knowledge repository/service/workspace and one filter dialog; tests cover Database, GUI and ticket-flow Integration. Affected canonical docs and this report are synchronized; `Docs/09_SQLSchema.md`, ERD, AHK, PowerShell and dependency files are unaffected. Self-review found no remaining blocking defect. The next gate is an independent read-only review of this exact unstaged candidate. No staging, commit, push or integration has begun.

Exact candidate scope: modified `Python/f7hub/{repositories/knowledge_repository.py,services/knowledge_service.py,gui/knowledge_workspace.py}`, `Tests/Database/test_knowledge_tag_filter.py`, `Tests/GUI/test_knowledge_tag_filter.py`, `Tests/Integration/test_ticket_knowledge_flow.py`, `Docs/{03_Features.md,04_UserWorkflows.md,05_GUI.md,07_Database.md,13_PythonArchitecture.md,16_Roadmap.md,17_Todo.md,18_ChangeLog.md,Status/CURRENT_STATE.md}`; new `Python/f7hub/gui/knowledge_tag_filter_dialog.py` and `Tests/GUI/test_knowledge_tag_filter_dialog.py`. No deletions; index empty. The root checkout retains its seven modified and two untracked protected paths.

For the v0.2 skill evaluation after Slices 024–026: the PLAN baseline gate caught the dirty root, live Git history resolved stale status prose, and this full regression cost about 394 seconds of suite runtime. Distinguish a READY design from an implementation baseline blocker in future templates.

---

## Prior Slice 023 handoff snapshot (historical, superseded by the merged baseline)

Last verified: 2026-09-22 (America/Toronto)

Branch: `feat/knowledge-filter-reference-refresh`

Base and current HEAD at that handoff: `d98e12a3faa722ad380c8e426c51def50892a273`

At that handoff: PASS — READY FOR INDEPENDENT SLICE 023 REVIEW. This prior status is retained as historical test evidence. Slice 023 later merged into `main` through PR #22 (`2f3368db45c3067ccfac2fc5c76b41ab9dc8a4c9`).

## Current Milestone

KNOWLEDGE FILTER REFERENCES CAN BE REFRESHED MANUALLY WITHOUT RECONSTRUCTING THE WORKSPACE

## Slice 023 Working Behavior and Boundaries

The compact Knowledge filter row includes an accessible **Refresh filters** control. One activation requests active KNOWLEDGE categories once and global tags once through the existing independent runners. Duplicate activation is disabled until both reads settle, and `filter_loading` keeps existing MainWindow close protection truthful.

Successful sources replace their dynamic choices. Failed sources keep the last successfully loaded options and selection, show safe source-specific feedback and allow retry; one failure does not block the other source. All categories, Not selected, All tags and Untagged remain stable modes. Specific selections reconcile by ID, so renames stay selected with updated labels. Inactive/deleted category selections reset Category only; deleted tag selections reset Tag only.

After both callbacks settle, valid selections cause no article request. One or two unavailable selections cause exactly one authoritative result request using the final controls. Normal mode reloads the filtered list. Active search reruns its last executed query while leaving unsubmitted input untouched. Status and compatible filter dimensions remain selected. No polling, watchers, administration, saved/date filters or multi-tag expressions are implemented.

## Architecture and Database Safety

`KnowledgeWorkspace` reuses `KnowledgeService.list_active_knowledge_categories()`, `KnowledgeService.list_available_tags()`, `_filter_runner`, `_tag_filter_runner`, source feedback labels and the shared list/search runner. `CategoryRepository.list_categories(scope="KNOWLEDGE", active_only=True)` and `TagRepository.list_tags()` remain the only reference queries. MainWindow, services, repositories, domain, AHK and PowerShell are unchanged; no component, dependency, migration, schema, index or FTS change was added.

The refresh path is read-only. An isolated real-SQLite integration test compared complete `iterdump()` output immediately before and after successful, mixed-failure and reset/reload refreshes; every pair was identical. Representative final state returned `PRAGMA integrity_check = ok` and zero `PRAGMA foreign_key_check` rows.

## Validation

Environment: repository `.venv\Scripts\python.exe`, `PYTHONPATH=$PWD\Python;$PWD`; focused/full GUI and Integration automation used `QT_QPA_PLATFORM=offscreen` except the explicit native run.

- Focused Slice 023: **27 PASS** in 132.760s.
- Database regression: **332 PASS** in 17.875s.
- GUI regression: **140 PASS** in 177.985s.
- Integration regression: **92 PASS** in 451.618s.
- Total full regression: **564 PASS**; zero failures, errors or skips; no suite decreased from the supplied 332/128/91 baseline.

Coverage includes control/accessibility/layout, exact service-call counts, both completion orders, additions/renames/deactivation/deletion, all static modes, source-specific and dual failure, cached choices, retry, duplicate prevention, close protection, zero/one final result request, Category/Status/Tag preservation, normal list, last-executed FTS query, unsubmitted text, real external SQLite changes, read-only dumps, integrity and foreign keys. Existing full regression covers Category+Status+Tag filtering, FTS, Clear Search and Ticket Open Article.

## Native Windows Verification

`QT_QPA_PLATFORM=windows`: **6 PASS** in 20.386s using real MainWindow hierarchies and isolated SQLite.

After making the tool button's strong keyboard-focus policy explicit, the two native control/accessibility/layout tests re-passed in 2.914s; the focus-only change did not alter geometry.

An actual MainWindow remained exactly 1000×700 for all six captures in `C:\Users\Jo\AppData\Local\Temp\f7-s023-validation-codex`: idle, busy/disabled, successful updated choices, one-source failure, unavailable category/tag reset, and active-search reconciliation. All captures were opened and manually inspected. The filter row, feedback, table, detail and actions were readable with no forced oversize, clipping, overlap, hidden control, misleading stale filter/result or broken detail view. The search capture and runtime evidence showed `search_active=True`, executed query `DNS`, visible input `unsubmitted text`, reset All category/tag and one matching result. This is agent verification, not user acceptance testing.

## Documentation and Git Safety

Updated owners: 03 Features, 04 User Workflows, 05 GUI, 13 Python Architecture, 16 Roadmap, 17 Todo, 18 ChangeLog and this current-state report. Database architecture, ERD, SQL schema, folder structure, AHK and PowerShell docs are unchanged because their owned behavior did not change. No validation/native artifact is stored in the repository.

## Risks and Next Gate

Verified remaining limitation: choices update only on initial load or explicit Refresh filters; there is no polling/watcher. Native evidence covers the tested 1000×700 Windows environment and synthetic text, not every DPI/display configuration.

At this historical handoff, the next gate was independent review of Slice 023. That candidate was later merged into `main`; the current Slice 024 gate is stated above.
