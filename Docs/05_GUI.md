# F7Hub GUI Design

## CP02-S4 candidate — Recent multi-select and Copy Selected (2026-10-29)

Unintegrated candidate from merged PR #121 base `8150dc7e139fee62a7121b3fd449d3e3c9d7de4d`.
Recent adds Select All Visible, Clear Selection, Copy Selected (N), a passive
selected-count label and model check state. Logical columns remain Time, Preview,
Source App, Retention, Pinned, then Select; Select is moved to the first visual
section. All text columns remain read-only; no native row-selection or sorting
contract is added. Source App values and underlying field indices are preserved.

The stable registry rows below describe the candidate where marked. Its three
new action buttons do not rewrite pinned historical registry audit totals.
`clipboardSelectedCount` is a plain accessible QLabel, not another action.
Checks use Item ID/revision and CheckStateRole, never per-row checkbox widgets.
The table's Space event toggles one current row without autorepeat; normal arrows,
Tab/Shift+Tab and accessible check state remain available. Copy feedback reuses the
existing status label. Selection and pending lifecycle are owned by
[1C](Planning/Clipboard/1C_PySide6_Clipboard_Center.md#cp02-s4-selection-contract);
[CURRENT_STATE](Status/CURRENT_STATE.md#cp02-s4-current-state) owns evidence.

## CP02-S3 — Source App in Recent candidate (2026-10-29)

Candidate only in `C:/Dev/F7Hub-Clipboard-SourceAppProvenance-20261029`, branch
`feature/clipboard-source-app-provenance-20261029`, base/HEAD
`b049a56a88305d48cf64d813065efa5a9b96f3e5`. Unstaged and uncommitted;
independent review and user-owned physical acceptance remain pending.

The candidate's existing Recent QTableView/model has exactly **Time | Preview |
Source App | Retention | Pinned**. Source App is the latest committed Event's
permitted executable basename (`notepad.exe`, `msedge.exe`) or **Not recorded**
when NULL/unavailable; an older Event's name is never substituted. Plain display
and AccessibleTextRole use the same bounded value. Preview stretches; fixed widths
for Time/Source App/Retention/Pinned are 230/170/105/70. Refresh, navigation,
read-only behavior and NoSelection remain unchanged. No sorting/filtering/actions
or title presentation are added. Stable registry IDs are retained below.

Setup now describes the integrated Win+Alt+C/V behavior and the false-default
source-process option for new eligible captures, including preservation of prior
names when disabled. Automatic capture and window-title collection remain unavailable.
The baseline includes PR120; earlier integration-pending snapshots below remain
historical. Author offscreen model/accessibility/refresh/navigation checks PASS;
physical layout, Narrator/high contrast and alternate DPI remain NOT RUN.

## Python Clipboard shortcut status — accepted candidate, integration pending (2026-10-29)

Win+Alt+C is integrated through PR #119. The Python/Qt Win+Alt+V Paste Latest
action is implemented in the isolated feature candidate; final code-review
disposition is **APPROVED WITH NOTES**, with A/B/C, stale-history rejection and
compatibility **USER-REPORTED PHYSICAL PASS**. It remains uncommitted and
unmerged. See the [single shortcut entry](#gui-registry-shortcuts),
[1B current contract](Planning/Clipboard/1B_AHK_Python_Clipboard_Capture_IPC_Quick_HUD_Architecture.md#python-paste-latest-current)
and [current status](Status/CURRENT_STATE.md#python-paste-latest-current-state).
This documentation delta awaits focused review. Older dated GUI/registry
snapshots retain their original evidence; no unrelated shortcut is reassigned.

## F7 restore correction — candidate (2026-10-26)

The first exposure-only white-window correction FAILED physical acceptance:
X/F7 remained white, while tray Open restored the GUI. Tray Open followed by
guarded Exit physically PASS, as clarified by the user. The replacement candidate
uses the existing Qt recovery timer and a read-only HWND visibility query to
restore widgets without relying on Expose notifications or altering AHK TAP/HOLD.
Corrected automated fixtures pass; replacement physical acceptance and
independent review remain pending. No integration readiness is claimed.
See [Python architecture](13_PythonArchitecture.md#f7-restore-presentation-correction--candidate-2026-10-26).
The integrated LIFE-01 history below is preserved.

## LIFE-01 — system tray lifecycle (2026-10-25 integrated)

**INTEGRATED / PASS** through [PR #112](https://github.com/JDecelles1990/F7Hub/pull/112).
Independent implementation review: **APPROVED WITH NOTES**. Implementation
`a89fde20d5da281dd0109a4ed1a6868ed570db30` was merged as
`041246b288c584f807dd849e450e3ad025f5a93d`. See
[current state](Status/CURRENT_STATE.md) for evidence provenance and all three
retained P3 findings.

The composed Python application retains its existing MainWindow when X is used.
X hides without draft confirmation, Clipboard leave/discard, or Mochi cleanup.
The retained tray icon offers **Open F7Hub** and **Exit F7Hub**; single/double
activation and Open restore the same window, page, drafts and usable editor focus.
Windows may place the icon behind the notification-area overflow arrow.

Before hiding, the application checks tray availability, installed nonempty icon
geometry and the retained enabled Open menu route. If those checks fail, the
window remains visible with recovery guidance. A one-second Qt timer restores a
hidden window when that route disappears. These runtime checks complement native
validation; availability alone does not prove the actual Open path works.

The existing Settings utility Exit command, Quit shortcut and tray Exit share one
guarded coordinator. Exit presents the retained window, applies existing pending
operation and Ticket/Clipboard draft checks, and preserves state on Cancel.
Accepted Exit releases existing resources once and quits the application, even
with last-window automatic quitting disabled. Windows may refuse foreground
activation; a visible restored window/taskbar remains available in that case.

LIFE-01 adds no automatic Clipboard monitoring or persistence; RAM-01B is NOT
STARTED. Retained Windows smoke evidence uses synthetic data and OS-injected input
at 1000×700, 96 DPI, covering hide/Open restoration and lost-tray recovery.

Historical hidden-window tray Exit attempts failed to observe accepted shutdown;
those failures and their undetermined root cause remain preserved. The later
physical attempt's original adjudication also remains **FAIL / EVENT_ORDER**.
Its saved physical evidence subsequently received a separate **PASS** through
independently approved offline reassessment of the corrected adjudicator. That
reassessment established physical selection, accepted guarded cleanup, non-forced
quit, natural exit 0 and no owned survivors without another physical attempt.
Physical acceptance is therefore satisfied for this bounded lifecycle gate.
The origins of `0x8001010D` and the earlier abnormal `0xC000041D` termination remain
NOT VERIFIED; crash-free stability and alternate DPI are not established.

## S05 Clipboard Setup consent status (2026-10-15 candidate)

The existing retained Setup surface distinguishes saved workflow preference from
eligible manual-history consent. Explicit enable+Apply records consent through the
Clipboard service. Saved true without evidence requires deliberate reaffirmation;
no-op Apply or Reload does not grant. Cancel, stale-draft conflict and pending-work
guards remain. The visible workflow opt-in and its accessible description explain
that TEMPORARY Clipboard content is retained locally for 7 days by default,
detected sensitive content is rejected, and detection cannot guarantee that all
secrets are identified; an approved preservation action may use a different policy.
An uncertain save preserves the draft and requires Reload, with no
false “nothing saved” claim. No second dialog or native capture/paste action is
added. Runtime capture/Active Paste remain unavailable; automatic monitoring is
not authorized by this manual-purpose consent. The owner is
[Clipboard 1C](Planning/Clipboard/1C_PySide6_Clipboard_Center.md).

## Clipboard Phase 2A — retained source composition (2026-10-14 candidate)

The retained Clipboard Center has a labelled, noneditable **Clipboard source** selector below its heading. Its only choices are **F7Hub Clipboard** (default on new construction) and **Windows Clipboard**. Stable local keys `f7hub` and `windows` select two retained QStackedWidget children. The original Recent table/model, optional Recent/Setup stack, ClipboardSetup, services and runners are composed once and reused. This presentation candidate awaits independent review; dated predecessor entries below preserve their historical scope/evidence.

F7Hub keeps its bounded read-only Recent query, initial accepted activation, explicit Refresh/Retry, safe Item projections and Settings editor. Switching source calls no service operation, refresh, capture, persistence or native path. Windows presents plain accessible **Windows Clipboard snapshot is not available yet.** feedback and disabled Refresh with an unavailable description; there is no acquisition callback, fabricated content or effect command. Saved preferences cannot enable Windows access. Native snapshot/IPC/privacy admission, capture, outbound domain Copy, Active Paste, monitoring, History import and Ctrl+Alt+C/V remain separate future delivery.

Explicit combo activation enters one guarded transition. QSignalBlocker restores the committed selector value before a modal question; only accepted departure commits selector and source page together. Dirty Setup uses existing Discard/Cancel: Cancel preserves draft/revision/section/source and restores valid prior focus; Discard follows existing session cleanup once and returns the F7Hub section to Recent. Pending Recent/Setup work, including idle-before-callback and completing intervals, refuses switching without queued navigation or duplicate work. Existing hidden-Recent completion and hidden-pending close guards remain. Recent success/error callbacks are request-generation bound and update only their own child, without selecting a source or taking focus.

Each source retains safe child state and in-memory shell scroll offsets. MainWindow supplies narrow capture/restore callbacks for the existing viewport: restoration is synchronous, range-clamped and skipped while another module is visible. Keeping focus reachable takes precedence over an off-screen offset; no delayed restoration can override newer scrolling. Module changes retain the existing shell reset. No source Settings key, query/filter/selection contract, new service/runner or schema is introduced.

Tab/Shift+Tab traverse the selector and enabled active-section controls; Tab now leaves the Recent table rather than navigating cells. Native combo arrows/type-ahead and popup Escape remain. The plain Source label has no mnemonic competing with Alt+S. Accepted switching keeps selector focus; repeated Center activation preserves valid intentional focus, active-section/selector activation chooses a usable control, and the S005 rail fallback remains when none is usable. Standard text-widget Ctrl+C remains distinct from Clipboard-domain commands.

FRESH WINDOWS_NATIVE workstation validation: **124 focused GUI PASS**, **15 affected Integration/two exact bootstrap checks PASS**, Qt offscreen, exit 0/no skips; separate Qt `windows` **202 observations PASS** at exact 660×592, 1000×700 and 1180×850 client sizes, 96 DPI, with **18 opened/inspected captures**. Input was Qt-synthesized; physical keyboard/mouse, Narrator, actual High Contrast, alternate/mixed DPI, RDP and AltGr remain NOT RUN. Existing compact Setup explanatory horizontal overflow remains nonblocking with required controls/text reachable after actual scrolling. Initial GUI/native assertion/readiness/reachability/post-modal failures remain FAIL; diagnosed relevant corrections and distinct diagnostics preceded fresh executions under RT-R01.

Exact commands/results/input identities, corrections, native observations and manifest are external under `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Clipboard-Phase2/implementation-20261014T193711Z`. Candidate stops READY_FOR_REVIEW, unstaged/uncommitted; independent approval/integration and later phases remain pending.

## GUI Shell S005 — Clipboard return control retirement (2026-10-14 candidate)

ClipboardWorkspace no longer contains the lower Back to Tickets button. MainWindow's existing Tickets rail QAction and guarded `show_tickets()` route remain the return path; `_leave_clipboard()` still owns Setup confirmation and accepted-session cleanup. No return control or shortcut was added to Clipboard Center. The retained Recent and Setup sections, read-only history, lazy construction, safe close and pending/draft guards remain.

On an accepted Clipboard page change, focus goes to enabled visible Refresh/Retry in Recent; while Refresh is disabled for loading, it goes to the Recent section selector when Settings exists, otherwise the Clipboard rail button. Setup's first enabled checkbox is preferred when editing is available; its enabled Reload/Cancel or section selector are fallbacks. Pending Setup uses its section selector, with the rail as fallback. When both optional services are absent, the rail is the only interactive landing point. Repeated activation preserves an existing valid user focus, section and scroll state. Async completion does not later steal focus. Qt native validation and exact limits are recorded in [CURRENT_STATE](Status/CURRENT_STATE.md#gui-shell-s005--clipboard-return-control-retirement-candidate-2026-10-14). Earlier S004/CC-01 descriptions of the button are historical.

## GUI Shell S004 — menu and toolbar retirement (2026-10-14 candidate)

The existing 52px rail is the sole primary navigation surface for Tickets, Knowledge Base, Scripts and Clipboard Center. MainWindow no longer constructs the redundant File/Settings menu bar or Tickets toolbar. The four rail buttons retain their shared QActions and guarded routes; native window controls, the status bar and workspace-local controls remain. Clipboard stays lazy and retained, including its Back to Tickets button.

The Settings gear retains Mochi, Back up database and Exit and now contains **Knowledge Base tools → Guide**. The submenu uses the same MainWindow-owned Guide action as the KB header, independently of KnowledgeService availability, workspace construction or article loading. Missing Guide service disables Guide truthfully; busy/pending guards remain authoritative. The unavailable KB tooltip identifies the surviving gear fallback.

**Alt+S** opens utilities. **Alt+F** focuses the selected enabled rail destination, then the first enabled destination in rail order, then the enabled gear when every destination is disabled. It never activates a route or discards drafts. Separate editor dialogs retain mnemonic priority; popups retain native input. Escape dismisses the root menu back to its invocation focus, returns from the tools submenu to its parent, or returns from Alt+F navigation focus to its still-valid workspace invocation control. Tab/Shift+Tab, Space/Return, accessible names, visible focus and current-workspace descriptions remain. Utility-popup lifetime temporarily suspends the two shell shortcuts to prevent another activation during native Alt dismissal.

Ctrl+Q remains on the existing Exit action registered with MainWindow; keyboard, menu and native close retain pending-operation and draft confirmation protections. No service, worker, IPC, database or global hotkey contract changes. S001–S003 sections below preserve historical candidate evidence and access locations superseded here. See [CURRENT_STATE](Status/CURRENT_STATE.md#gui-shell-s004--menu-and-toolbar-retirement-candidate-2026-10-14) for exact validation and physical accessibility limits.

## GUI Shell S003 — Guide access (2026-10-14 candidate)

The Knowledge Base header contains one keyboard-accessible **Guide** button. It uses the existing MainWindow `altF7HubGuideAction`, now labeled **Guide**, through `QToolButton.setDefaultAction`. **File → Knowledge Base tools → Guide** exposes the same action independently of KnowledgeService composition or successful article loading. Its direct File-menu and top-toolbar positions are removed. A KnowledgeWorkspace construction failure leaves the article action unavailable with explanatory feedback while the shell and Guide fallback remain available. There is no new Guide page, service or command.

Guide opens or focuses the retained AHK Guide/editor without navigating the stack or changing the current article, search, filters, selected record, Ticket drafts or unsaved AHK editor content. Existing shared-runner, pending-operation and close protections remain authoritative; unconfirmed requests produce safe feedback without automatic retry. Availability depends on the Guide service and existing busy/pending guards. Compact layouts retain the shell scrollbars for control reachability. Candidate validation and limitations are in [CURRENT_STATE](Status/CURRENT_STATE.md#gui-shell-s003--guide-relocation-and-window-title-candidate-2026-10-14).


## GUI Shell S002 — Settings utility menu (2026-10-14 candidate)

The 52px navigation rail has a bottom-aligned, icon-only **Settings and utilities** button with a tooltip, accessible name and visible keyboard focus. Click, Space or Enter opens a compact Qt menu; Escape dismisses it without changing the selected workspace or invoking a command. Its three entries use the existing **Mochi…**, **Back up database** and **E&xit** QAction instances, so their enabled states match the retained Settings and File menus. Mochi opens the existing modeless dialog, backup uses the existing asynchronous guarded service, and Exit uses the normal protected close path. Opening the menu does not change drafts, pages or scroll position. The gear is not a workspace or Settings Center, and no Appearance control is present.

The button joins ordinary Tab traversal after Clipboard and before the Tickets workspace. The shared Exit action preserves a valid native Quit shortcut and falls back to Ctrl+Q on Windows when Qt supplies none; keyboard activation follows the same draft and pending-operation guards as menu Exit. Existing `&File` and `&Settings` menu mnemonics remain; the proposed Alt+F and Alt+S rail bindings conflict with them and are deferred to the menu/toolbar retirement slice. The S001 section below records its earlier candidate and validation history; S001 later merged through PR #96 at `76bd643c8b44e13f4967f2fad5c736bcabc8ecde`. S002 remains an uncommitted implementation candidate pending independent rereview of the Quit correction.

## GUI Shell S001 — four-module navigation rail (2026-10-13)

The implementation candidate adds a 52-logical-pixel left rail for **Tickets**, **Knowledge Base**, **Scripts** and **Clipboard Center**. Four 44×44 icon-only Qt controls reuse the existing File-menu/toolbar QAction objects and guarded handlers. Original Qt-painted outline icons, tooltips, accessible names, a textual current-workspace description, visible selection/focus indicators, hover feedback and action-matched disabled states are confined to the rail. Existing menus, toolbar, Guide route, status bar, native title bar and Clipboard return remain.

Selection follows the actual QStackedWidget page, including menu/toolbar, New Ticket, article opening and Clipboard Back to Tickets transitions. The selected workspace remains visibly identifiable, including while its navigation control is disabled. Accepted changes to a different page reset both shell scrollbars to their origin; refused or cancelled routes and repeated activation preserve their scroll positions. Refused departures preserve the displayed page and drafts. Mouse activation keeps editor focus; rail-local synchronous Cancel restoration returns to the prior enabled workspace control. Keyboard Space on Scripts activates the workspace once. If asynchronous work displaces that rail focus, queued reconciliation restores it after callback completion, subject to current page, active window, enabled state and activation generation; a later deliberate user action cancels restoration. Clipboard remains lazy and retained; existing optional-service, shared-worker, pending-operation, draft and close protections remain guarded.

The read-only Ticket queue uses arrow keys for records and lets Tab/Shift+Tab leave the table without trapping traversal. Scripts toolbar Tab relationships follow the displayed **Run diagnostic → Copy Script → Manage scripts → Refresh** order, with naturally disabled controls skipped. Automated and visible native Qt traversal evidence is separate from physical keyboard acceptance.

A shell QScrollArea hosts the existing stack so workspace minimum sizes remain intact. At compact sizes or expanded forms, horizontal/vertical overflow is reachable through workspace scrollbars while the rail stays fixed; all workspace controls need not appear simultaneously. Earlier slice fit statements and native Qt size, 150% scale and 15-point font checks retain their historical validation meaning. Current candidate identity, retained regression evidence and manual acceptance are in [CURRENT_STATE](Status/CURRENT_STATE.md#gui-shell-s001--implementation-candidate-2026-10-13).

**Accepted physical keyboard limitation:** following refresh, focus was visibly restored, but three physical forward Tab presses reached Search where the native Qt test expected Refresh. Reverse navigation and general keyboard access remained available. The exact skipped or reordered stop is **NOT VERIFIED**; the user accepted the discrepancy and independent review classified it as nonblocking for S001. The complete physical forward sequence is **NOT PASS**. Refinement belongs to the [future Scripts Workspace redesign follow-up](17_Todo.md#gui-shell-s001--scripts-keyboard-follow-up-2026-10-14). Narrator, physical High Contrast and actual alternate-monitor DPI remain **NOT RUN**.

## CP-02 Stage 2 — Clipboard Setup editor

Clipboard Center now retains one **Clipboard Setup** page beside **Recent** when the shared SettingsService is composed. Existing Recent presentation and Back to Tickets remain. Setup loads a coherent authoritative snapshot asynchronously each time a new editing session begins. Exactly three independently editable checkboxes expose workflow/local-history opt-in, optional source executable basename and optional source window title. Values/defaults come from SettingsSnapshot; no GUI defaults or SQL are introduced.

Workflow enablement explains eligible future durable manual captures with normal TEMPORARY retention unless an independently approved preservation action applies. Master disable preserves both optional source preferences and existing history. Titles are explicitly described as potentially sensitive. Saved preferences never assert active capability: production capture, Active Paste and Ctrl+Alt+C/V remain unavailable.

Apply validates changed Booleans through existing definitions and makes one async SettingsService.apply call with the original expected revision. No-op Apply performs no write. Cancel discards only uncommitted edits and restores the latest known saved values. Conflict preserves the complete draft, disables Apply and requires explicit Reload, Discard/Cancel confirmation and deliberate review of the refreshed snapshot. Leaving Setup, changing shell workspace, reopening/reloading and main-window close protect unsaved edits. Pending reads/writes refuse overlapping operations, navigation and close, including the runner completion gap.

Storage-unavailable snapshots show effective safe-disabled values and disable persistence until Reload succeeds. Invalid stored sensitive values show the backend's false fallback with safe feedback. Validation, contention and persistence errors preserve drafts; raw exceptions are never shown/logged. Successful commits update the saved baseline before presentation; observer or display failures remain acknowledged as saved with a separate downstream warning and reload-only recovery for display failure.

Candidate **READY_FOR_REVIEW**, unstaged/uncommitted. FRESH WINDOWS_NATIVE host, noninteractive Qt offscreen: focused 73, GUI 251, Integration 219, Database 520 PASS. Separate user-authorized native Qt run: 74 assertions PASS, exit 0, zero owned survivors; seven captures inspected at 1000×700 and 1180×850/96 DPI. QTest input is synthesized; physical input, alternate DPI, Narrator/high contrast remain NOT RUN. See [current state](Status/CURRENT_STATE.md#cp-02-stage-2--clipboard-setup-editor-2026-10-12) for evidence and limitations.

## CC-02 — Bounded read-only Clipboard Recent page

Production Clipboard Center now consumes the merged D01 service. Accepted navigation lazily constructs and retains one workspace, starts one asynchronous `get_recent()` read with the default 50-item limit, and reuses that page on reopening. An optional absent service retains CC-01's truthful unavailable state. The CC-01 record below describes its original shell delivery; CC-02 supersedes its production no-service/no-worker state.

The integrated CC-02 baseline has four columns. The CP02-S3 candidate extends the same read-only model/view to exactly **Time**, **Preview**, **Source App**, **Retention**, and **Pinned**. Time is the validated latest receipt instant displayed explicitly in UTC with milliseconds. Preview is only D01's bounded safe plain text, with a textual truncation suffix when flagged; long cells use normal Qt elision in the stretching Preview column. Retention reads Temporary/Saved and pin state Yes/No. Source App follows the nullable Event attribution contract above. There are no fabricated Kind/Entity/Tag/relationship columns, sorting controls, stable Item selection, Inspector or mutations.

**Refresh** performs one new first-page read. Loading shows **Loading Clipboard history…**, clears old rows/count (including the accessibility label), and disables only Refresh. Empty success shows **No recent Clipboard history is available.** Failure clears rows and shows only **Clipboard history could not be loaded.**, with explicit **Retry**. Successful feedback is **Showing N recent items.**, adding **More items are available.** only for `has_more`. There is no Next/Previous, cursor, polling, capture or automatic retry.

Clipboard owns an independent existing ServiceTaskRunner. Tickets, Knowledge and Scripts remain usable during Clipboard-only loading; completion does not change the current route or focus. Existing navigation, Ticket Discard/Cancel and Back to Tickets behavior remain. Close is refused while the owned Clipboard worker/callback is finishing, including when the page is hidden. No OS Clipboard access, raw body, SQL, URL/markup interpretation, logging of previews or external handoff is added.

CC-02 validation: focused 50, full GUI 232 and full Integration 209 PASS on a Windows host with Qt offscreen, zero failures/errors/skips, exit 0 and zero owned survivors. Separate WINDOWS_NATIVE validation passed 96 assertions at 1000×700/96 DPI, exit 0, zero survivors. Populated, empty, failure/Retry and loading captures were all inspected without observed control clipping/overlap. QTest input was synthesized; physical input, additional DPI, Narrator and CC-13 refinement remain NOT RUN. Candidate is READY_FOR_REVIEW, unstaged/uncommitted; evidence is external under `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Clipboard-CC02`. Independent review is next.

## CC-01 — Clipboard Center workspace shell

The File menu and existing toolbar share one **Clipboard Center** action immediately after Scripts. Its stable action identity is `clipboard.center`. Explicit activation lazily creates one retained read-only page in MainWindow's existing stack. Repeated activation and navigation away/back reuse that page. Startup remains Tickets.

The page displays **Clipboard Center**, **Clipboard history is not available yet.**, and **Back to Tickets**. The return button uses the existing Tickets navigation and receives focus on accepted Clipboard activation. Labels are plain text with accessible names; the unavailable message wraps. Standard Qt palette, font and keyboard button behavior apply. The menu mnemonic adds no dedicated/global shortcut.

Existing shared-runner and Ticket/Script owner-pending guards refuse navigation, including idle-before-callback gaps. Existing Ticket activity Discard/Cancel protection runs before first construction or a page transition; Cancel preserves page, values and focus. Accepted discard uses the existing cleanup. Idle new-ticket creation fields remain retained while hidden, and application close still prompts for the unsaved form. Clipboard adds no draft, timer or worker.

No Clipboard query/history service, persistence, capture, monitoring, IPC, search or Inspector is delivered. The shell does not read the OS Clipboard or display sample history.

Validation on Windows: 221 GUI and 204 integration tests PASS, exit 0, using Qt offscreen; this establishes automated behavior, not native rendering. One separate Windows-native QTest smoke passed 28 assertions at 1000×700/96 DPI, exit 0 and zero owned survivors. Its single client screenshot was inspected without observed clipping/overlap. Physical hardware input, alternate DPI and Narrator remain NOT RUN. CC-01 is an unstaged implementation candidate; independent review is pending.

## Slice 053 — Local Baseline Diagnostics

Scripts shows **Name | Type | Category | File status | Execution**. Code, Version and current metadata policy are in plain-text details. File availability and execution approval are separate; an approved missing file cannot Run. Shown/available/approved counts describe the filtered rows. Pack readiness checks its three registrations independently of search, remains advisory, and execution rechecks bytes/runtime. The pack panel names member order, local read-only scope, memory-only results and per-member limits: up to 60 seconds execution plus 5 seconds cleanup; preparation adds time. Runs cannot be cancelled. Shared pending ownership spans dispatch, runner idle-before-callback and result presentation, including stale-callback, failure, navigation and close guards.

Ordered plain-text pack results include execution outcome, collection outcome or unavailable aggregate on abort, whole and member durations, exit codes, cleanup verification, safe warnings/errors/data and skipped members. Previous result identity remains independent of later row selection. A presentation failure releases only the matching owner and preserves the in-memory result and cleanup quarantine.

Validation: Database 438, PowerShell 72, GUI 210, Integration 203 PASS (196 RETAINED methods plus 7 FRESH corrected bootstrap methods; original full exit 1, correction exit 0). Other final suites exit 0, and all supervisors report zero owned survivors. Native Windows 104 assertions PASS at 1000×700/96 DPI, QTest input; real pack and individual Network, synthetic valid ERROR, invalid middle output, actual synthetic timeout containment and cleanup-quarantine scenarios. All 6 captures inspected. Physical hardware input and alternate DPI NOT RUN. Earlier failed fixture/harness/migration-count attempts remain historical evidence with bounded correction records. `native-v5-retry.md` records one accidental unchanged launch and loss of the original v3 JSON; the later v4 duplicate artifact is preserved separately. Final applicability checks bind tested inputs to the documented candidate.

## Scripts diagnostic Run and result panel — Slice 052 historical candidate

Historical Slice 052 scope, closed through PR #58 and superseded by Slice 053 above.

The existing Scripts page adds an explicit **Run diagnostic** button and a read-only plain-text result panel beside the catalog. Only an available selected **Windows System Snapshot** with the composed execution service enables Run; service policy performs the authoritative eligibility check. The selection shows purpose, local target, Standard User privilege, time limit and memory-only result handling before execution. The shared background runner keeps the GUI responsive. Workspace-owned pending state spans the idle-before-callback gap, suppresses duplicate and conflicting actions, and blocks navigation/close until result presentation and cleanup complete. Completed diagnostic ERROR and execution failure have distinct status text. Native Windows 1000×700/96 DPI captures of ready, completed and timeout states were inspected without observed overlap; input used QTest events. Physical manual input and other DPI are NOT RUN.

## Inline classification layout — Slice 051

Saved-ticket detail has one compact row: **Priority [dropdown] Type [dropdown] [Apply changes]**. Accessible names are Ticket priority, Ticket type and Apply ticket changes. Choices come directly from the existing domain collections. The remaining compact action row contains Edit subject, Edit description and Reload ticket; Edit priority/Edit type are removed.

Authoritative loaded values are distinct from dropdown drafts. Apply is enabled only for an idle, loaded saved ticket with a changed choice, and disabled in New Ticket mode or while Subject/Description editing is active. Classification pending state spans the write and owned detail/queue reads, keeping navigation, close and conflicting activity protected across the runner callback gap. Failure preserves choices; success updates the baseline and disables Apply. Dirty choices survive unrelated activity refreshes with their original concurrency token.

The existing scrollable detail tabs may shrink to 100 pixels to accommodate expanded Resolution at 1000×700. Status controls, Quick Note and the embedded creation form retain their workflows. Native Windows 1000×700/96 DPI validation passed after correcting vertical sizing; all nine final captures were inspected without observed clipping or overlap. Input used QTest on the Windows backend; physical manual input and additional DPI were NOT RUN. Historical Slice 031/033 modal descriptions below are superseded for normal ticket use.

## Tickets and embedded New Ticket — Slice 050

**Tickets** is the single ticket navigation destination in the File menu and toolbar, and the initial application page loads its queue. The heading and keyboard-accessible **+ New Ticket** button remain above the queue/detail splitter without scrolling. There is no separate New Ticket page/action/keyboard shortcut.

The right pane switches between saved detail and the reused creation form. A scroll area keeps the full existing form reachable at 1000×700, with Cancel pinned beneath it; the queue, search/filter controls and pagination remain visible. Small spacing/margin adjustments accommodate the new heading without a broader layout redesign. The form focuses Subject after initial reference reads. Ctrl+S is scoped to the visible form. New Ticket is disabled while already creating or during pending operations.

Saved activity drafts require explicit discard before entry. Quick Note is hidden/disabled and the active saved identity is cleared during creation; Cancel restores the prior detail/tab. Confirmed creation opens saved detail and selects a matching queue row without resetting filters/search/page. Failure preserves form values; committed read failure has truthful feedback and a visible read-only reopen action. Old detail text is cleared while there is no active saved identity. Native Windows 1000×700/96 DPI agent validation passed with inspected captures. Input used QTest events on the native Windows Qt backend; physical input and other DPI configurations were not run.

## Persistent Quick Note — Slice 049

Saved-ticket detail retains its five existing tabs and optional Author field. A compact **Quick Note** row contains note type and **Add note** above the existing multiline plain-text editor. The button tooltip exposes Ctrl+Enter; the shortcut applies only in that editor. Blank/unloaded/busy states disable submission. Navigation, tab names, property editing and status layout are unchanged.

The note's local pending state keeps note controls and MainWindow navigation/close protection active across the shared runner's idle-before-callback boundary. Success clears only note text and restores focus after the owned refresh completes; errors preserve the draft and distinguish committed writes from failed refreshes. Native Windows 1000×700/96 DPI checks passed across all tabs and expanded resolution; all six captures were inspected without observed control overlap or clipping. Physical manual input and other DPI environments remain NOT RUN.


## Mochi Settings — Slice 002 candidate

Settings → Mochi… opens a single parent-owned modeless `MochiSettingsDialog`. Repeated opening raises the existing dialog. Status and controls observe the application-owned MochiService; closing unsubscribes the dialog without closing the connection or storing preferences. Pending commands disable only conflicting Mochi controls. Close, F7Hub navigation and ticket work remain usable. Detached/obsolete dialog callbacks are ignored, and replacement dialogs subscribe to current service state.

Controls are Start/Show, Hide, Idle, Wave, Pause/Resume and Exit. Animation switching is disabled while paused. Unconfirmed commands retain UNCERTAIN feedback separately from subsequently observed runtime state. The first display schedules one automatic attempt after recording its application-session gate, rather than launching during bootstrap.

> Document: `Docs/05_GUI.md`  
> Project: F7Hub  
> Purpose: Define the intended graphical user interface, navigation model, workspace structure, panel behavior and interaction principles for F7Hub.  
> Scope: Product-level GUI behavior and layout.  
> Related Documents: `03_Features.md`, `04_UserWorkflows.md`, `06_SystemArchitecture.md`, `13_PythonArchitecture.md`

---

## AltF7Hub Guide — Slice 046

At original Slice 046 delivery, MainWindow added **AltF7Hub Guide** to its toolbar and direct File menu; S003 above supersedes those entry positions and labels. The action is enabled when its service is composed and the shared runner is idle; launch work runs through ServiceTaskRunner and preserves page selection and drafts. Completion distinguishes guide opening from editor focusing. Safe failures offer installation/file checks or retry without exposing internal diagnostics.

The reference overlay retains its AHK GUI ownership and existing controls. Opening focuses notes while preserving selection and scroll position. Arrow navigation is scoped to notes/list and wraps visible topics; opacity keys support repeat and share the slider, label, native alpha and saved preference. Native Python action, overlay and editor captures were inspected at 96 DPI after observable worker/callback readiness; no new controls were clipped. Transparency naturally reveals the underlying window.

---

## Manual Scripts search controls — Slice 045

Scripts adds a dedicated accessible search row: one field, **Search** and **Clear**. Enter applies the field. Draft text and the applied query remain separate; Refresh/navigation/management reload preserve both their meanings. Query state is local to the current workspace and resets on reconstruction. The table, details and existing heading actions are reused.

Search, Clear and Refresh are guarded during shared-runner activity and local loading/copying, including idle-before-callback completion. Each request captures its applied query. Loading/failure clears stale rows and details; validation feedback offers edited Search/Clear, read failure offers Refresh. Filtered/unfiltered empty messages differ; the manager stays accessible with no matches. Selection reconciliation and late-copy rejection are preserved. Fresh native Windows validation passed at 1000×700 after observable idle; six captures showed readable controls, feedback and metadata without observed control clipping or overlap. The long query scrolls inside its field.

---

## Local script management — Slice 044

The Scripts heading row adds **Manage scripts…**, opening a modal owned by MainWindow outside its disabled pages hierarchy. Its table shows Name, Code, Enabled and File status for scoped registrations, with a scrollable plain-text metadata panel and Register script…, Refresh, Enable/Disable and Close actions. Selection and successful refresh retain stable script IDs. Registration uses a separate form requiring code, name, relative path, type, risk and privilege; description/version are optional. Classification choices require an explicit selection. Cancel is the default action and writes nothing.

Reads and writes use the shared ServiceTaskRunner. Writes disable conflicting actions and dismissal; dismissed reads ignore late callbacks. Enabling requires explicit confirmation with Cancel as default. Errors preserve registration input, stale update conflicts clear actionable rows for Refresh, and a committed write with failed reload keeps its success notice and offers read-only retry. Closing a changed manager refreshes the catalog, waiting for a pending management read if necessary. Copy Script retains Slice 043's existing availability gating and service checksum check. Native Windows keyboard, busy/error/retry and clipboard workflows at 1000×700 passed; six captures were inspected without observed control overlap or clipping. This is implementation validation, not independent approval.

---

## Copy Script control — Slice 043

The Scripts heading row includes an accessible **Copy Script** button. It requires a selected entry last observed as AVAILABLE and is disabled during shared-worker activity. Clicking starts fresh verification in ServiceTaskRunner; success sets the Qt clipboard to raw source text and shows a short confirmation. A selection change or page departure while verification runs discards the stale result. Missing approval, mismatch, unavailable file and read failures show bounded plain-text feedback without paths, source or exception details. The GUI neither opens `.ps1` files nor executes PowerShell.

---

## Scripts workspace — Slice 041

The existing File menu and toolbar add one **Scripts** action that opens a page in MainWindow's stacked navigation. The page has a four-column enabled-script table (Name, Code, Category, File status), a read-only scrollable plain-text metadata panel, an intentional empty message, and a manual **Refresh** button. Row selection, including keyboard selection, updates details from the loaded entry without another service read. Refresh preserves the selected script code when present, otherwise selects the first row. Loading and failure clear stale content; Refresh is disabled while the shared worker is busy. Status remains readable as text, with unknown values shown as Unknown. There is no clickable script path or execution control.

---

## Manual database backup action — Slice 038

The existing File menu contains **Back up database**. The shared worker keeps the window responsive and disables the action and conflicting navigation while backup runs. The success dialog shows the actual published path and brief local-only protection guidance; failure shows bounded feedback without a raw exception message. Closing during work follows the existing busy guard. Native Windows inspection at 1000×700 found the menu item and both dialogs readable; the isolated snapshot reopened and passed integrity and foreign-key checks.

---

## Saved-ticket Company tab — Slice 036

Saved-ticket detail includes a Company tab with the authoritative company name, **Load recent tickets**, a separate ticket table, and **Open selected ticket**. The read is asynchronous through the shared worker and capped at 20 newest tickets. No-company and read-failure states are explicit; a failed refresh keeps earlier rows only for the same loaded ticket/company. Opening a result uses existing draft-discard confirmation and detail loading. Native Windows inspection at 1000×700 found the Company tab and existing queue/detail controls accessible without observed clipping or overlap.

## Saved-ticket note search — Slice 039

The existing queue search field now displays and exposes the accessible name **Search subjects, descriptions and notes**. Enter or Search submits one literal phrase; note-only matches appear as ordinary ticket rows without note excerpts. A successful note save uses the existing detail and queue refresh, preserving an applied phrase and any later unsubmitted draft. Failed reads keep the prior rows and detail for Refresh retry. Native Windows inspection at 1000×700 confirmed the empty, matched, failed, recovered and cleared states with the Saved Tickets page visible and no observed control overlap.

---

## All-selected-tag filter selection — Slice 025

The existing Choose tags… dialog adds keyboard-usable Any/All radio choices above its check list. With two or more selected IDs, the Tag combo displays **All of N tags** or **Any of N tags** and lists the selected names in its tooltip. Zero and one selections collapse to All tags and the existing specific-tag item. Cancel and unchanged Apply submit no result request. The tested native Windows 1000×700 MainWindow and dialog kept the filter row, detail, check list and actions visible; evidence is in `Status/CURRENT_STATE.md`.

---

## Any-tag filter selection — Slice 024

The existing Tag combo adds Choose tags… and shows Any of N tags when two or more cached global tags are selected. The small selection dialog has a keyboard-usable check list and Cancel/Apply; it performs no reference query or write. Zero/one selections collapse to the existing All/specific modes. The workspace disables conflicting actions while the dialog is open, applies changed choices through its shared asynchronous list/search runner, and keeps current search input distinct from the last executed query. Stable IDs drive reference and article reconciliation. Native Windows 1000×700 MainWindow and dialog captures were inspected; evidence is in Status/CURRENT_STATE.md.

---

## Implemented manual Knowledge filter-reference refresh — Slice 023

The compact Category/Status/Tag row includes a keyboard-reachable **Refresh filters** tool button with the accessible name “Refresh knowledge filter choices”. It remains visible at 1000×700 and is disabled while the manual cycle or another filter-reference read is active. The existing `filter_loading` close guard remains authoritative.

Category and tag reads continue through their existing independent `ServiceTaskRunner` instances. Each successful callback replaces only that source's dynamic options under signal blocking and restores static mode or stable ID; a failed callback leaves its combo untouched and shows safe source-specific feedback. Minimal cycle state waits for both callbacks, coalesces one or two missing selections into one list/search reload, and issues no result request when both selections remain valid. During active search the stored executed query is submitted directly without replacing unsubmitted field text. No GUI SQL, new dialog or MainWindow change is introduced.

---

## Implemented Knowledge tag filter — Slice 022

Search remains on its own row. A compact filter row contains Category, Status and Tag so the actual MainWindow remains usable at 1000×700. Tag defaults to All tags, includes static Untagged, and appends every existing global tag in deterministic name/ID order. Item data carries explicit modes and IDs; display labels are not parsed.

Category and tag references use independent workspace-owned `ServiceTaskRunner` instances. Each selector remains independently usable after the other reference source fails, while `filter_loading` covers either runner for existing MainWindow close protection. Signal-blocked population does not issue article requests. List/search replacement, selection/detail reconciliation, Clear Search, tag mutation, create/lifecycle reveal and Ticket Open Article follow the same authoritative reload path. No GUI SQL or MainWindow modification is introduced.

---

## Implemented Knowledge status filter — Slice 020

A compact Status: combo sits beside the existing Search and Category controls. Its accessible name is “Filter knowledge articles by status”; item data is None, DRAFT, PUBLISHED or ARCHIVED, independent of display text. All statuses is the default. Choices are populated synchronously from the fixed lifecycle domain, so no database query or additional ServiceTaskRunner is used.

Article list/search continues through the shared ServiceTaskRunner and disables Status while the request is busy. Status remains usable while only the category-reference worker is pending. Category loading/failure behavior and MainWindow close protection are unchanged.

Replacement list/search requests clear old rows and details before dispatch. Compatible selection remains a preference. Clear Search retains category and status; explicit Ticket Open Article resets search and both filters before reveal. Create/Publish/Archive reset only incompatible dimensions and show the authoritative result. Category mutation and content edit preserve status. Native Windows 1000×700 evidence is recorded in Status/CURRENT_STATE.md.

---

# 1. Purpose

This document defines how F7Hub should present its features to the technician.

It answers:

> How should F7Hub look, behave and organize technician workflows?

This document defines:

- main window structure
- navigation
- workspaces
- panels
- module layouts
- command palette
- toolbar behavior
- status areas
- keyboard interaction
- forms
- dialogs
- feedback
- accessibility
- error presentation

Implementation details such as PySide6 classes, signal wiring and threading belong in:

`13_PythonArchitecture.md`

---

# 2. GUI Goals

The interface should optimize for:

1. fast access to support context
2. minimal application switching
3. high information density without clutter
4. keyboard productivity
5. clear current context
6. predictable navigation
7. safe administrative actions
8. strong search
9. resizable workspaces
10. useful multi-monitor behavior

The GUI should feel like a technician workspace rather than a generic database application.

---

# 3. GUI Philosophy

F7Hub should combine useful interaction concepts from:

- VS Code
- ticketing systems
- OneNote
- PowerShell terminals
- command palettes
- knowledge bases
- clipboard managers
- Microsoft administration tools

It should not visually or functionally clone any of them.

The primary interaction principle is:

> Keep the current support context visible while making related actions easy to reach.

---

# 4. Current Implementation Status

Repository inspection and tests through 2026-09-06 verified ticket creation, quick company/contact creation, the saved-ticket workspace and Knowledge Base create/list/read plus DRAFT editing with version history in the application shell.

```text
TicketCreateWidget: VERIFIED
Application entry point, bootstrap and MainWindow: VERIFIED
Saved-ticket list, details, notes and status controls: VERIFIED
Remaining navigation and GUI modules: PLANNED
Knowledge Base create/list/read: VERIFIED
Knowledge DRAFT editing, current version and stale-edit feedback: VERIFIED
GUI tests: PASS — 52 tests (fresh Slice 011 final regression)
Application and GUI integration tests: PASS — 50 tests (fresh Slice 011 final regression)
```

`TicketCreateWidget` provides the minimum ticket input form, inline required-field feedback, safe persistence-error presentation, input preservation, keyboard save action, service delegation and a successful-ticket signal. The main window provides Tickets (including + New Ticket) navigation. Successful creation opens the saved ticket. The queue supports status filtering and pages of 100 tickets; details show notes, lifecycle history and timeline events. Technicians can add notes, resolve with a summary, close and reopen using service-provided status choices.

Slice 027 adds one Ticket number field and Open number button beneath the Saved Tickets status/refresh row. Enter and the button perform the same exact-number read through the shared service runner. The number is retained for retry; a successful direct open leaves the queue page and status filter unchanged. Native Windows verification at 1000×700 found the controls and detail readable after the workspace reached idle.

Slice 028 adds a Priority selector on its own row below Status and Refresh so the MainWindow still fits at 1000×700. It offers All priorities, Critical, High, Medium and Low. Priority and Status compose for queue reads; either change resets paging, while Refresh, paging and exact-number opening retain filter state. Both selectors disable during shared-runner work, and replacement rows appear only after a successful read. A failed read leaves prior rows, detail, drafts and selections available for retry. Native Windows validation used the `windows` Qt platform with one selected High/Open ticket and an inspected 1000×700 capture.

Slice 029 adds an accessible Type selector on its own row below Priority, with All types, Incident, Service request, Problem and Task. It uses stored type values through the existing queue worker, disables with Status and Priority during worker activity, and preserves all selected filters and the prior rows/detail/drafts after a failed read. The final native Windows 1000×700 capture was inspected with an Open, High Service request ticket selected; the filter rows, queue and detail controls were readable without observed clipping or overlap.

Slice 030 places **Edit subject** beside Reload ticket in saved-ticket details. Its compact dialog prefills the loaded subject and keeps entered text after validation or save failure. While a write runs, Save and Cancel are unavailable and the dialog cannot close. Stale-edit feedback asks the technician to reload. A committed edit is acknowledged even when the later detail or queue refresh fails. Native Windows verification at 1000×700 inspected the dialog and post-save workspace after observable idle; the controls and feedback were readable without overlap.

Historical Slice 031 introduced the separate priority dialog. Slice 051 supersedes that normal UI with inline Priority and explicit atomic Apply; its individual guarded service/repository API remains supported.

Slice 032 adds **Edit description** with a plain-text multiline editor. The four detail actions now use a two-row grid so the main window retains its 1000×700 size. The dialog preserves typed text on failure and prevents duplicate submission or unsafe close during a write. Native Windows captures after observable idle show the dialog, saved detail, post-commit refresh-failure acknowledgment and recovered queue at 1000×700 without observed clipping or overlap.

Historical Slice 033 introduced the separate type dialog. Slice 051 supersedes that normal UI with inline Type and explicit atomic Apply; its individual guarded service/repository API remains supported.

Failed saves preserve drafts. Switching tickets or leaving activity drafts prompts before discarding them; failed loads preserve existing details and drafts. A committed save followed by a failed reload remains reported as saved. If the initial detail load fails after creation, the queue refreshes so the saved ticket can be opened again. Operations disable conflicting actions while running; closing waits for the operation to finish. Automated GUI checks run offscreen; native Windows visual inspection and input-event checks are PASS on 2026-09-05 at the default size and 1000×700. Initial window sizing now leaves space for Windows borders and the taskbar. Reference-data loading is verified: New Ticket loads active companies and company-filtered active contacts through a background service call. Changing company clears the old contact. Refresh references supports retry and preserves draft text and valid selections. Saved ticket details display company/contact names, including inactive references; null or deleted references show Not selected. Native Windows Slice 006 visual/input checks passed at the initial size and 1000×700, including error feedback. The AutoHotkey F7 shortcut launches, focuses or restores the application while its script is active.

Slice 007 category integration is verified on 2026-09-05. New Ticket loads active TICKET category names through the existing background runner, with independent ID values, Not selected, empty feedback and a Refresh categories retry action. Category failures preserve text and company/contact/category selections; category-only retry does not query companies or contacts. Saved details show current category names, including inactive references, and Not selected after null/deletion. The description minimum height is 100 pixels so the added feedback row fits at 1000×700. Native Windows renders and input checks passed for the category workflow and failure feedback; these are agent checks, not user acceptance testing.

Slice 008 adds a secondary **Add Company** action beside the company selector and a bounded **Quick Add Company** dialog with required name, Cancel and Create Company. It opens asynchronously, uses ServiceTaskRunner for persistence, prevents repeated submission and preserves input after errors. Successful creation refreshes only companies and contacts, selects the new company and preserves all unrelated ticket fields. A committed creation with failed refresh is reported distinctly and recovered through Refresh references without another insertion. Company code and broader company/contact management are not exposed.

Native Windows Slice 008 visual/input checks passed on 2026-09-06 for validation, cancel, creation, selection, draft preservation, refresh recovery and saved-ticket reopening at 1000×700. Success feedback shares the Create Ticket action row so it does not force the window above that size. These are agent checks, not user acceptance testing.

Slice 009 adds **Add Contact** beside Contact and a **Quick Add Contact** dialog containing required contact name, optional email, Cancel and Create Contact. It follows the existing asynchronous dialog/worker conventions, retains input on failure and prevents duplicate submission and unsafe close/cancel during writes. Add Contact requires a selected company and an idle runner with no pending company/contact reconciliation.

Contact success refreshes only the selected company's contacts and selects the created ID without changing any other ticket draft field. After a committed write with failed refresh, the form retains contact/company identity, locks company switching and creation actions, blocks ticket submission and offers contact-only retry through Refresh references. Missing contacts after a successful authoritative reload clear pending auto-selection with explicit feedback. If an authoritative read finds the company inactive or deleted, one **Continue without this contact** button appears beside Refresh references. It releases pending auto-selection, clears company/contact choices and refreshes companies without reloading categories or changing the remaining draft. The committed contact stays stored; transient failures remain retryable. Recovery is disabled while a worker is busy, and obsolete contact-load callbacks are ignored. Native Windows input checks and visual inspection passed at 1000×700 on 2026-09-06, including combined Add Company → Add Contact → save/reopen and subsequent deactivation/deletion recovery checks. These are agent checks, not user acceptance testing.

The layouts in this document represent intended product behavior.

---

# 5. Primary GUI Technology

Primary framework:

```text
Python
+
PySide6
```

PySide6 owns:

- main application window
- navigation
- panels
- views
- forms
- dialogs
- workspaces
- command palette
- status displays
- application-level visual state

AutoHotkey v2 may supplement the main GUI with:

- global hotkeys
- quick menus
- lightweight popups
- clipboard actions

AHK should not become a second competing full GUI architecture.

---

# 6. Main Window Concept

The preferred main-window structure is:

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Menu Bar                                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│ Toolbar / Command Area                                                       │
├───────────────┬───────────────────────────────────────┬──────────────────────┤
│ Navigation    │ Main Workspace                        │ Context / Assistant  │
│               │                                       │                      │
│ Dashboard     │ Active Module                         │ Ticket Context       │
│ Tickets       │                                       │ Related KB           │
│ Companies     │                                       │ AI Assistant         │
│ Contacts      │                                       │ Diagnostics          │
│ KB            │                                       │                      │
│ Search        │                                       │                      │
│ Scripts       │                                       │                      │
│ Diagnostics   │                                       │                      │
│ Clipboard     │                                       │                      │
│ Prompts       │                                       │                      │
│ Reports       │                                       │                      │
├───────────────┴───────────────────────────────────────┴──────────────────────┤
│ Output / PowerShell / Logs / Activity                                        │
├──────────────────────────────────────────────────────────────────────────────┤
│ Status Bar                                                                   │
└──────────────────────────────────────────────────────────────────────────────┘
```

Not every panel must always be visible.

---

# 7. Main Window Regions

The primary window may contain:

## Menu Bar

Application-wide commands.

## Toolbar

Frequently used actions and context controls.

## Navigation Sidebar

Primary module navigation.

## Main Workspace

The currently active module or workflow.

## Context Panel

Information related to the current ticket, company, contact or diagnostic session.

## Bottom Panel

Output, terminal, logs, diagnostics or activity.

## Status Bar

Application and integration status.

---

# 8. Menu Bar

Suggested top-level structure:

```text
File
Edit
View
Navigate
Ticket
Automation
Database
AI
Tools
Window
Help
```

The menu bar should expose application-level actions rather than every possible feature.

Frequently used actions should also be available through:

- keyboard shortcuts
- toolbar
- command palette
- context menus

---

# 9. Toolbar

The main toolbar may provide:

- back
- forward
- search
- command palette
- new ticket
- active ticket
- active company
- workspace selector
- run diagnostic
- open PowerShell
- quick actions

The toolbar should remain compact.

---

# 10. Navigation Sidebar

The sidebar should provide stable access to major modules.

Suggested structure:

```text
WORKSPACE
├── Dashboard
├── Tickets
├── Companies
└── Contacts

KNOWLEDGE
├── Knowledge Base
├── Search
└── Prompts

AUTOMATION
├── Scripts
├── Diagnostics
├── Clipboard
└── PowerShell

ADMINISTRATION
├── Microsoft 365
├── Reports
└── Plugins

SYSTEM
├── Logs
└── Settings
```

The exact grouping may evolve as features mature.

---

# 11. Navigation Principles

Navigation should:

- preserve module state where appropriate
- make the active module obvious
- support keyboard access
- avoid opening excessive windows
- permit opening related objects from context
- maintain useful navigation history

Example:

```text
Ticket
→ Company
→ Previous Ticket
→ Back
→ Ticket
```

---

# 12. Active Context Display

The GUI should make active support context visible.

Potential display:

```text
Ticket: INC-10254
Company: Contoso
Contact: Alex Martin
Workspace: Helpdesk
```

This context may appear in:

- toolbar
- title area
- context panel
- breadcrumb

The same information should not be redundantly repeated everywhere.

---

# 13. Dashboard

The Dashboard is the technician landing area.

Potential sections:

```text
┌───────────────────────────────────────────────────────────────┐
│ Dashboard                                                     │
├──────────────────────────────┬────────────────────────────────┤
│ Active / Recent Tickets      │ Quick Actions                  │
│                              │                                │
│ INC-10254 Outlook issue      │ + New Ticket                   │
│ INC-10251 VPN issue          │ Search                         │
│ INC-10247 MFA                │ Run Diagnostic                 │
│                              │ Open PowerShell                │
├──────────────────────────────┼────────────────────────────────┤
│ Recent Knowledge             │ Recent Activity                │
│                              │                                │
│ Outlook Profile Repair       │ DNS diagnostic                 │
│ Teams Camera Troubleshooting │ KB article updated             │
└──────────────────────────────┴────────────────────────────────┘
```

The dashboard should provide shortcuts rather than duplicate every module.

---

# 14. Ticket Center

The Ticket Center should be one of the primary F7Hub workspaces.

Suggested layout:

```text
┌─────────────────────────────────────────────────────────────────────────┐
│ Tickets                                                                 │
├──────────────────────┬──────────────────────────────────────────────────┤
│ Ticket Queue         │ Ticket Workspace                                 │
│                      │                                                  │
│ Search               │ INC-10254                                        │
│ Filters              │ Outlook cannot connect                           │
│                      │                                                  │
│ INC-10254            │ Details | Notes | Timeline | Attachments         │
│ INC-10253            │                                                  │
│ INC-10252            │ Main ticket content                              │
│ INC-10251            │                                                  │
├──────────────────────┴──────────────────────────────────────┬───────────┤
│                                                           │ Context   │
│                                                           │ KB        │
│                                                           │ Scripts   │
│                                                           │ AI        │
└───────────────────────────────────────────────────────────┴───────────┘
```

---

# 15. Ticket Queue

Slice 034 adds a Search subjects row with a text field, Search and Clear buttons. The field accepts Enter. The submitted query is separate from unsubmitted input, composes with Status/Priority/Type and uses the existing asynchronous queue replacement, paging and Refresh path. Clear removes only subject search. During a queue worker operation the search controls are disabled; failed reads keep the previous rows, current detail and drafts with retry feedback. A subject edit can remove the row from the active search without closing the updated detail. Native Windows 1000×700 evidence is recorded in Status/CURRENT_STATE.md.

Slice 035 keeps that row and relabels its input Search subjects and descriptions. The same submitted phrase searches either field through the queue worker, with all three filters and page recovery intact. A description edit can remove a result without closing its saved, updated detail or clearing activity drafts. Native Windows inspection at 1000×700 found the full placeholder, Search, Clear, filters and detail actions accessible without observed clipping or overlap.

The ticket list should support:

- search
- filtering
- sorting
- status indicators
- company
- ticket number
- title
- priority
- update date

The list should avoid displaying too many columns by default.

Columns may be configurable later.

---

# 16. Ticket Details

Ticket details may include:

- ticket number
- title
- description
- status
- priority
- company
- contact
- category
- timestamps
- assigned technician where applicable
- external PSA identifier

Editable and read-only information should be visually distinguishable.

---

# 17. Ticket Workspace Tabs

Potential tabs include:

```text
Details
Notes
Timeline
Attachments
Diagnostics
Related
```

Not every related feature must become a tab.

Contextual panels may be better for:

- related KB
- scripts
- AI
- company context

---

# 18. Ticket Notes

The notes interface should support:

- chronological display
- note type
- timestamp
- author/context where applicable
- add note
- copy
- search
- filtering

When writing a note, the technician may access:

- snippets
- clipboard tools
- AI formatting
- templates

---

# 19. Ticket Timeline

Timeline entries may visually distinguish:

- ticket creation
- notes
- status changes
- diagnostics
- scripts
- KB relationships
- attachments
- resolution
- escalation

The timeline should provide concise summaries with expandable details.

---

# 20. Ticket Context Panel

The right-side context panel may contain switchable sections:

```text
Context
KB Matches
Diagnostics
Scripts
AI
Company
Contact
```

This preserves the central ticket workspace while providing related tools.

---

# 21. Company Center

Suggested structure:

```text
┌──────────────────────┬─────────────────────────────────────────────┐
│ Companies            │ Company Details                             │
│                      │                                             │
│ Search               │ Contoso                                     │
│ Contoso              │ Domains                                     │
│ Fabrikam             │ Environment                                 │
│ Northwind            │ Contacts                                    │
│                      │ Tickets                                     │
│                      │ Notes                                       │
│                      │ Links                                       │
└──────────────────────┴─────────────────────────────────────────────┘
```

Company context should emphasize support information rather than CRM-style complexity.

---

# 22. Contact Center

Contacts should display:

- name
- company
- email
- phone
- department
- title
- relevant notes
- ticket history

The interface should make it easy to move between:

```text
Contact
↔ Company
↔ Tickets
```

---

# 23. Knowledge Base

Slice 018 adds Category… beside the plain-text Category name in current details. Keeping this action out of the top toolbar preserves the 1000×700 window minimum across tested styles. The action requires a service, idle runner and loaded DRAFT. ArticleCategoryDialog contains Not selected, active KNOWLEDGE names, current-category context, Refresh categories, Cancel and Save. Active current selection is prefilled; inactive assigned names stay visible but are excluded from choices. PUBLISHED/ARCHIVED category editing and category administration remain unimplemented; read-only category filtering is implemented in Slice 019.

Slice 021 adds a plain-text Tags detail and adjacent Tags… action for an idle loaded DRAFT. ArticleTagsDialog asynchronously loads every existing global tag and the current article set, presents a simple checkable list, supports zero/one/multiple selections and keeps Cancel as the default/Escape action. Save submits the complete set once and updates detail only from the authoritative committed record. Reference/save failures retain truthful article detail; stale context cannot submit. PUBLISHED and ARCHIVED articles retain visible tags with Tags… disabled. Tag creation/admin are not part of this dialog; read-only tag filtering is a separate Slice 022 control.

Slice 023 adds Refresh filters to the existing compact filter row. It preserves static modes and stable-ID selections, displays renamed choices, retains cached options on source-specific failure, and coalesces unavailable category/tag resets into one authoritative result reload. Automated and native Windows 1000×700 evidence is recorded in Status/CURRENT_STATE.md.

The main window owns this modal outside the disabled pages hierarchy. Reference reads remain dismissible; late callbacks after dismissal are ignored. Save retains the original version/updated_at tokens and rejects changed workspace context. Competing actions and repeat submits are disabled. After the repository reloads and commits, the returned authoritative record updates the displayed category with safe success feedback. Failure preserves current detail and permits retry or reopening as appropriate. Native 1000×700 workflow and captures are recorded in Status/CURRENT_STATE.md.

Slice 010 adds Knowledge Base beside New ticket and Saved tickets in the existing toolbar/menu and stacked application shell. The workspace has New Article, a code/title/status table, a clear empty state and a read view with code, title, status, summary and read-only Markdown source. Metadata is explicitly plain text so HTML-like input remains literal.

New Article collects required article code/title/body and optional summary. Creation, list refresh and detail reads use the existing background runner; conflicting pages/navigation are disabled while busy. Duplicate submission is prevented, errors preserve input and detail callbacks check the current selection.

Slice 011 adds Edit Article for a loaded DRAFT and a read-only Version N detail label. Edit is unavailable without loaded details, during reload or for PUBLISHED/ARCHIVED articles. A separate EditArticleDialog keeps creation and revision responsibilities explicit: code and the originally opened version are plain-text labels; title/summary/body are prefilled editable fields; actions are Cancel and Save Revision.

Slice 026 adds a wrapping, plain-text Created / Last updated line directly below current Version N. It uses the existing loaded current-article record and clears with the rest of detail. The values are displayed exactly as persisted, without timezone conversion. Native Windows inspection at 1000×700 found the line readable and the article body usable.

Save uses ServiceTaskRunner, blocks duplicate submission and close/cancel during the write, and closes on success. The list refreshes, reselects the same article ID and reloads current details. Failures preserve entered text. Stale/missing/non-DRAFT conflicts disable further saves in that editor; a new editor must be opened explicitly. Workspace refreshes cannot replace its expected-version token. No-change feedback leaves the editor open and creates no revision after authoritative version checks.

Native Windows input and visual verification at 1000×700 passed through Slice 021 for zero/multiple tag display and selection, edit, filters/search, publish/archive, Version History and Ticket Open Article. Six captures were inspected with no horizontal clipping or important overlap. Slice 022 separately implements read-only single-tag filtering; Slice 024 adds Any and Slice 025 adds All-selected matching with separate native evidence above. This is agent verification, not user acceptance testing. There is no rendered Markdown, restore/revert, unpublishing/unarchiving, category/tag administration, custom tag expression filtering, article-to-article relationships, external links or AI.

Slice 015 adds a single-line Search field, Search button and Clear Search button beside the Knowledge list. Enter submits. Search reuses the article table and current-detail read path; result rows retain stable article IDs rather than display text as identity. Empty and failed searches have distinct feedback, failures retain the query, and Clear Search restores the full list. The shared ServiceTaskRunner keeps MATCH work off the GUI thread and disables search/list/create/edit/history actions while any Knowledge operation is active. Search results remain usable with Edit Article and Version History after authoritative detail has loaded.

The initial search UI intentionally has no filters, result snippets/highlighting, advanced syntax, pagination or universal-search navigation.

Fresh native Windows input and captured-window inspection passed on 2026-09-09 at 1000×700 for pending/disabled search, DRAFT/PUBLISHED/ARCHIVED results, no-result and safe-failure states, Clear Search, current content after edit, immutable Version 1 history, New Article and ticket Open Article. Inspection found status elision after a longer full-list refresh; the identity columns are now recalculated after each population, and the post-fix capture shows complete status values. All nine final captures were inspected. This is agent verification, not user acceptance testing.

Slice 014 adds Version History beside New Article and Edit Article. A separate VersionHistoryDialog lists Version, Title, Created and Created by, with read-only historical detail alongside it. ServiceTaskRunner loads list and selected body asynchronously; row interaction is disabled while busy. Version identities and callback generations guard results, and dismissal invalidates pending callbacks. All strings use plain text; the body uses read-only QPlainTextEdit. There are no mutation controls or historical status field. The top-level window owns the history dialog outside the disabled page hierarchy, leaving Close/Escape available during reads while workspace actions remain disabled. Historical metadata uses a resizable scroll area; the body retains its own useful space. Fresh remediation validation on 2026-09-09 passed all four list/detail × Close/Escape combinations. Native captures at 900×620 showed both ends of a 6,132-character plain-text summary through scrolling, with no overlap and a 356-pixel body height.

Fresh native Windows Qt mouse/keyboard checks and captured-window visual inspection passed on 2026-09-08 with a 1000×700 main window and 900×620 history dialog: exact V1/V2/V3, newest-first selection, unchanged current article, reopen, New/Edit and non-DRAFT history. Body and controls were readable without overlap for tested synthetic inputs. Table titles may use ellipsis; selected detail shows the full title. These are agent checks, not user acceptance testing.

Slice 012 adds a Knowledge tab to the existing saved-ticket detail tabs. TicketKnowledgeWidget shows a lightweight code/title/status/version table, empty state, Link Article, Open Article and Refresh. Identity columns are sized immediately after loading so the initial article code is readable. Controls are unavailable without a ticket or while the shared runner is busy. LinkArticleDialog provides existing article identities, Cancel and Link Article, plus retry after candidate-load failure; there is no search, filter, preview or relationship-type selector.

List/candidate/link calls use ServiceTaskRunner. Cancel during a candidate read ignores its eventual result; closing during a link waits for completion. Failures retain selection and show safe plain-text feedback. Success selects the new link and refreshes current metadata. TicketWorkspace emits an article-ID signal; MainWindow handles draft-discard protection, switches pages and calls KnowledgeWorkspace.open_article_by_id. A missing target is reported without selecting a different article.

Slice 012 native Windows input checks and visual inspection passed at 1000×700 with isolated synthetic SQLite: empty state, candidate selection, link, current metadata, Open Article, edit/create, notes/status lifecycle and reopening after reconstruction. The initial code-column clipping found during inspection was corrected and the native flow rerun. These are agent checks, not user acceptance testing.

Slice 013 adds Unlink Article beside the existing Link Article and Open Article buttons. It is enabled only with a saved ticket, service, selected linked article and idle runner. A small plain-text confirmation identifies the article and states that both entities remain; Cancel is the default and Escape action. Confirmation cannot be reentered, and changes to ticket context or selection during confirmation prevent submission. The confirmed unlink uses the shared worker, blocks conflicting actions and ignores callbacks for another ticket. Failed persistence preserves the row/selection. Success refreshes the list; if refresh fails, “Article unlinked.” remains visible, stale rows are cleared and Refresh provides recovery without repeating the deletion.

Slice 013 native Windows input checks and captured-window visual inspection passed at 1000×700: confirmation Cancel and Unlink, selected-row removal, preservation of the other link, exact KB0002 navigation, KB0001 candidate reappearance/relink, notes and Resolve → Close → Reopen. The new button and confirmation were readable with no clipping/overlap in the synthetic layouts. These are agent checks, not user acceptance testing.

Native Windows agent input checks and visual inspection passed on 2026-09-06 at 1000×700 for the empty state, creation of KB0001 and KB0002, list/detail switching and return through New ticket/Saved tickets. Both articles survived application reconstruction against isolated synthetic SQLite. No clipping/overlap was observed for these inputs. These are agent checks, not user acceptance testing. The broader layouts below remain planned.

Suggested layout:

```text
┌──────────────────────┬─────────────────────────────────────────────┐
│ KB Navigation        │ Article                                    │
│                      │                                             │
│ Search               │ Outlook Cached Credentials                  │
│ Categories           │                                             │
│ Tags                 │ Symptoms                                    │
│ Technologies         │ Cause                                       │
│                      │ Resolution                                  │
│ Results              │ Verification                                │
│                      │ Escalation                                  │
└──────────────────────┴─────────────────────────────────────────────┘
```

---

## Implemented Archive action — Slice 017

Action order: New Article, Edit Article, Publish, Archive, Version History. Archive requires an available service, idle runner and loaded PUBLISHED article. The PlainText Archive Article confirmation identifies code/title, explains ARCHIVED status and preserved content/history/ticket links, and states that Unarchive is unavailable. Archive/Cancel buttons use Cancel as default and Escape; Enter respects the default. Confirmation disables workspace actions and retains the reviewed article token.

ServiceTaskRunner performs the write asynchronously. Busy state disables competing actions in the containing MainWindow. Success refreshes/reselects/reloads authoritative ARCHIVED details without changing content/version; Edit/Publish/Archive disable and Version History remains enabled. Safe failure preserves the displayed article without an optimistic status mutation. Archive from search returns to the normal list; a new search finds the ARCHIVED current row. Native windows verification and visual inspection at 1000×700 passed; see Status/CURRENT_STATE.md for evidence and limits.

## Implemented Publish action — Slice 016

The action order is New Article, Edit Article, Publish, Archive, Version History (Archive added in Slice 017). Publish requires an available service, idle runner and loaded DRAFT. A QMessageBox displays code/title with PlainText and explains the PUBLISHED transition, preserved content/history and unavailable editing afterward. Its buttons are Publish and Cancel; default/Enter and Escape select Cancel. Confirmation reentry and changed article context cannot submit.

Confirmed publication uses ServiceTaskRunner and the loaded expected_version_number. Busy policy disables competing actions; no status is mutated optimistically. Success returns to the normal list, reselects the article and reloads authoritative PUBLISHED details. Edit/Publish become unavailable; Version History stays available. Safe failure feedback preserves the visible article; stale feedback requires reopening and reviewing the latest version. Cancel calls no service and performs no refresh.

Fresh native Windows verification at 1000×700 passed; all nine captures were inspected for button fit, plain confirmation readability, status, history, search and ticket Open Article. No overlap or clipped action/status labels was observed with the synthetic inputs; table titles retain established ellipsis behavior. Evidence and validation counts are in Status/CURRENT_STATE.md.

# 24. Knowledge Article Structure

The GUI should support structured article sections where useful.

Examples:

```text
Overview
Symptoms
Environment
Cause
Resolution
Verification
Commands
Scripts
Escalation
References
```

Article type may determine which sections are shown.

---

# 25. Knowledge Editor

The knowledge editor should support:

- title
- article type
- metadata
- tags
- structured content
- related scripts
- related tickets
- preview
- save
- lifecycle state

Markdown support may be used if approved by implementation architecture.

---

# 26. Universal Search

Search should be accessible globally.

Potential layout:

```text
Search: outlook cached credentials

[All] [Tickets] [KB] [Scripts] [Companies] [Contacts]

KB
────────────────────────────────────────
Outlook Cached Credentials
Repairing an Outlook profile

Tickets
────────────────────────────────────────
INC-10254 Outlook sign-in issue

Scripts
────────────────────────────────────────
Reset-OutlookProfile.ps1
```

Search results should clearly indicate their source type.

---

# 27. Search Result Actions

Results should support direct actions where safe.

Examples:

```text
Ticket
→ Open

KB
→ Open

Company
→ Open Context

Script
→ Review

Command
→ Run Registered Action
```

Search should support the pattern:

```text
Search → Find → Open → Act
```

---

# 28. Script Library

Suggested layout:

```text
┌──────────────────────────┬──────────────────────────────────────────┐
│ Script Library           │ Script Details                           │
│                          │                                          │
│ Search                   │ Test-DnsHealth.ps1                       │
│ Categories               │ Description                              │
│ Tags                     │ Risk: Low                                │
│                          │ Privilege: User                          │
│ DNS                      │ Parameters                               │
│ Exchange                 │                                          │
│ Intune                   │ [Review Script] [Run]                    │
└──────────────────────────┴──────────────────────────────────────────┘
```

---

# 29. Script Execution Dialog

Before execution, display:

- script name
- purpose
- target
- parameters
- privilege requirement
- risk level
- related ticket if applicable

Example:

```text
Run Script

Script:
Test-DnsHealth.ps1

Target:
PC-1042

Privilege:
Standard User

Parameters:
Hostname: example.com

[Cancel] [Run]
```

Privileged or destructive actions require stronger confirmation.

---

# 30. PowerShell Output

PowerShell output may appear in a bottom panel.

Possible tabs:

```text
PowerShell
Output
Errors
Activity
```

The panel should distinguish:

- running
- successful
- failed
- cancelled

Structured results may be rendered in a more readable form than raw JSON.

---

# 31. Diagnostic Center

Suggested layout:

```text
┌─────────────────────────┬───────────────────────────────────────────┐
│ Diagnostic Workflows    │ Current Diagnostic                        │
│                         │                                           │
│ Outlook                 │ Outlook Cannot Connect                    │
│ MFA                     │                                           │
│ VPN                     │ Step 3 of 7                               │
│ DNS                     │                                           │
│ Teams                   │ Can the user access Outlook Web?          │
│ Intune                  │                                           │
│                         │ ( ) Yes                                   │
│                         │ ( ) No                                    │
│                         │                                           │
│                         │ [Back] [Next]                             │
└─────────────────────────┴───────────────────────────────────────────┘
```

---

# 32. Diagnostic Workflow UI

The diagnostic interface should show:

- workflow title
- purpose
- progress
- current step
- inputs
- automated result where applicable
- previous answers
- next action

The technician should be able to understand why the workflow is progressing to the next step.

---

# 33. Diagnostic Result

At completion, display:

```text
Diagnostic Complete

Status:
Issue Identified

Finding:
DNS resolution is failing.

Evidence:
Server lookup failed.
Gateway reachable.

Recommended Next Step:
Reset DNS configuration.

Related KB:
DNS Resolution Troubleshooting

Approved Script:
Reset-NetworkDns.ps1
```

The result should be easy to attach or summarize into a ticket.

---

# 34. Clipboard Center

Potential layout:

```text
┌───────────────────────┬────────────────────────────────────────────┐
│ Clipboard History     │ Preview / Actions                          │
│                       │                                            │
│ Search                │ Selected clipboard content                 │
│                       │                                            │
│ Recent                │ Copy                                       │
│ Snippets              │ Insert                                     │
│ Templates             │ Transform                                  │
│                       │ Save as Snippet                            │
└───────────────────────┴────────────────────────────────────────────┘
```

Sensitive-content controls should remain visible and easy to access.

---

# 35. Clipboard Actions

Potential transformations:

- plain text
- remove extra whitespace
- uppercase
- lowercase
- extract URLs
- extract email addresses
- extract IP addresses
- format ticket note

The technician should be able to preview potentially destructive transformations before replacing existing content.

---

# 36. Prompt Library

Suggested structure:

```text
┌───────────────────────┬────────────────────────────────────────────┐
│ Prompts               │ Prompt Details                             │
│                       │                                            │
│ Search                │ Ticket Escalation Summary                  │
│ Categories            │                                            │
│                       │ Variables                                  │
│ Ticketing             │ {{ticket_title}}                           │
│ Knowledge             │ {{diagnostic_results}}                     │
│ PowerShell            │                                            │
│                       │ [Preview] [Use]                            │
└───────────────────────┴────────────────────────────────────────────┘
```

---

# 37. AI Assistant Panel

The AI Assistant may appear as a dockable contextual panel.

Potential functions:

- summarize ticket
- suggest troubleshooting
- improve notes
- explain script
- suggest KB
- interpret diagnostic results

The panel should clearly distinguish:

```text
F7Hub Data
AI Suggestion
Technician Decision
```

AI suggestions must not visually masquerade as verified system facts.

---

# 38. AI Safety UI

Before sending potentially sensitive context externally, F7Hub should provide appropriate transparency.

Possible controls:

- context preview
- included sources
- excluded sensitive fields
- provider
- submit/cancel

For administrative actions:

```text
AI Suggestion
    ↓
Technician Review
    ↓
Explicit Action
```

Never:

```text
AI Suggestion
    ↓
Automatic Destructive Execution
```

---

# 39. Microsoft Administration Center

Suggested function:

- portal launcher
- administrative shortcuts
- diagnostic actions
- supported Graph/PowerShell operations

Potential navigation:

```text
Microsoft 365
├── M365 Admin
├── Entra
├── Exchange
├── Intune
├── Defender
├── Teams
└── SharePoint
```

F7Hub should not attempt to replicate entire Microsoft portals.

---

# 40. Reports

The Reports module may include:

- report type
- filters
- preview
- export

Examples:

- diagnostic report
- script execution report
- ticket activity
- troubleshooting summary

---

# 41. Settings

Settings should be categorized.

Possible sections:

```text
General
Appearance
Paths
Database
PowerShell
AutoHotkey
Clipboard
AI
Microsoft
Integrations
Plugins
Logging
Advanced
```

Secrets should not be exposed as ordinary plaintext settings.

---

# 42. Settings Validation

When configuration is invalid:

- identify the affected field
- explain the issue
- preserve other valid changes
- avoid corrupting the entire configuration

A reset mechanism should exist for recoverable settings.

---

# 43. Logs and Activity

The Logs module may support:

- severity filtering
- subsystem filtering
- date filtering
- search
- details

Example:

```text
12:04:33 INFO    Database initialized
12:04:34 INFO    Workspace restored
12:04:39 WARNING Microsoft Graph unavailable
12:05:03 ERROR   Diagnostic script failed
```

Sensitive information must be sanitized.

---

# 44. Dockable Panels

Potential dockable panels include:

- Ticket Queue
- Ticket Details
- Notes
- Timeline
- Company Context
- Contact Context
- Knowledge Matches
- Search
- AI Assistant
- PowerShell
- Script Library
- Clipboard
- Output
- Activity
- Logs

Not every module should become a dock.

Docking should be used where persistent simultaneous context is valuable.

---

# 45. Panel Behavior

Where appropriate, panels may support:

- dock
- undock
- float
- resize
- hide
- restore
- move to another monitor

Panel configuration may be persisted as part of a workspace.

---

# 46. Workspace Profiles

Potential predefined workspaces:

## Helpdesk

Emphasis:

- Tickets
- Notes
- KB
- Diagnostics
- AI

## Microsoft 365

Emphasis:

- ticket context
- PowerShell
- Microsoft administration
- output

## Networking

Emphasis:

- diagnostics
- scripts
- PowerShell
- technical notes

## Automation

Emphasis:

- script library
- parameters
- PowerShell
- output
- logs

## Knowledge Authoring

Emphasis:

- KB editor
- source ticket
- search
- AI assistance

## AI

Emphasis:

- AI panel
- ticket context
- knowledge
- prompt library

---

# 47. Workspace Persistence

Workspace state may include:

- visible panels
- docking locations
- panel sizes
- active module
- selected workspace profile

Sensitive operational content should not necessarily be restored automatically.

Example:

Restoring panel layout is acceptable.

Automatically rerunning a privileged diagnostic is not.

---

# 48. Command Palette

The command palette should provide fast keyboard navigation.

Example:

```text
> open ticket 10254

Open Ticket INC-10254
```

Other examples:

```text
> dns
Run DNS Diagnostic
Search KB: DNS
Open Networking Workspace

> exchange
Open Exchange Admin Center
Search Exchange Scripts
Search Exchange KB
```

---

# 49. Command Palette Categories

Potential command categories:

- navigation
- tickets
- search
- knowledge
- scripts
- diagnostics
- workspaces
- tools
- Microsoft
- settings

Command search should prioritize useful actions rather than exposing internal implementation names.

---

# 50. Keyboard Productivity

Common tasks should eventually have keyboard shortcuts.

Potential examples:

```text
Ctrl+K
→ Command Palette

Ctrl+F
→ Contextual Search

Ctrl+S
→ Save

Ctrl+Shift+F
→ Universal Search

Ctrl+N
→ New Item in Current Context
```

Exact shortcut assignments must avoid conflicts and belong in approved GUI conventions.

---

# 51. Context Menus

Context menus should expose actions appropriate to the selected object.

Example ticket context menu:

```text
Open
Add Note
Run Diagnostic
Search Related KB
Copy Ticket Number
Open Company
```

Avoid excessively long context menus.

---

# 52. Forms

Forms should:

- group related information
- clearly identify required fields
- provide inline validation
- preserve entered information after recoverable errors
- support keyboard navigation
- avoid excessive modal dialogs

---

# 53. Validation Feedback

Invalid input should be shown near the relevant control where possible.

Example:

```text
Company Name
[                       ]

⚠ Company name is required.
```

A single generic error dialog should not replace useful field-level validation.

---

# 54. Dialog Philosophy

Use modal dialogs for actions requiring focused decisions.

Appropriate examples:

- privileged script confirmation
- destructive action
- unsaved changes
- authentication flow
- migration failure requiring intervention

Routine navigation should not depend heavily on modal dialogs.

---

# 55. Destructive Action Confirmation

Destructive actions should clearly identify:

```text
Action
Target
Impact
```

Example:

```text
Disable User Account

Target:
alex@contoso.com

Impact:
The user may immediately lose access to Microsoft 365 services.

[Cancel] [Disable Account]
```

Generic dialogs such as:

```text
Are you sure?
```

should be avoided for high-impact actions.

---

# 56. Feedback States

Operations should clearly communicate:

```text
IDLE
RUNNING
SUCCESS
WARNING
FAILED
CANCELLED
```

Examples:

- progress indicator
- status message
- result panel
- error indicator

The GUI should not falsely indicate completion while a background operation is still running.

---

# 57. Long-Running Operations

For operations such as:

- PowerShell scripts
- Graph requests
- AI calls
- report generation
- search indexing

the GUI should:

- remain responsive
- show operation status
- support cancellation where safe
- prevent accidental duplicate execution where appropriate

---

# 58. Error Presentation

Technical errors should be translated into useful technician-facing messages.

Example:

Instead of only:

```text
sqlite3.OperationalError
```

show:

```text
F7Hub could not save the ticket because the database operation failed.

Your entered information has been preserved.

View technical details
```

Technical details may remain available for troubleshooting.

---

# 59. Empty States

Empty states should explain what the user can do.

Example:

```text
No knowledge articles found.

Try another search or create a new KB article.
```

Avoid large blank panes with no explanation.

---

# 60. Loading States

When data retrieval is not immediate, show a visible loading state.

The technician should be able to distinguish:

- no data
- loading
- failed retrieval

---

# 61. Integration Status

Connected services may display status such as:

```text
SQLite          Connected
PowerShell      Available
Microsoft Graph Not Connected
AI              Available
HaloPSA         Not Configured
```

Status must reflect real application state.

---

# 62. Status Bar

Possible status-bar information:

```text
DB ✓ | PowerShell ✓ | Graph ○ | AI ✓ | Workspace: Helpdesk | F7Hub 0.1.0
```

The status bar should remain concise.

Detailed diagnostics belong elsewhere.

---

# 63. Theme

F7Hub should eventually support:

- dark mode
- light mode

Visual design should prioritize readability over decorative effects.

A modern Windows appearance is appropriate, but visual effects should not interfere with:

- contrast
- text clarity
- performance
- accessibility

---

# 64. Visual Hierarchy

Use visual emphasis deliberately.

Most prominent:

- active task
- ticket title
- critical warning
- primary action

Less prominent:

- metadata
- timestamps
- secondary links

The application should avoid making every control equally visually loud.

---

# 65. Color Usage

Color should communicate state rather than decorate randomly.

Examples:

- error
- warning
- success
- running
- inactive
- selected

Important state must not rely solely on color.

Icons and text should reinforce meaning.

---

# 66. Icons

Icons may improve navigation and recognition.

Use consistent icon families where licensing permits.

Icons should not replace labels for unfamiliar or critical actions.

---

# 67. Typography

Typography should prioritize:

- readability
- hierarchy
- consistency
- Windows scaling compatibility

Monospace fonts may be appropriate for:

- PowerShell
- command output
- code
- SQL
- logs

Normal interface text should use the application UI font.

---

# 68. Scaling

The GUI should behave correctly with common Windows display scaling settings.

Important target scenarios:

- 100%
- 125%
- 150%

Hard-coded pixel assumptions should be minimized.

---

# 69. Minimum Window Behavior

When the window becomes smaller:

- core content remains usable
- secondary panels may collapse
- scrolling is preferable to overlapping controls
- critical buttons remain accessible

---

# 70. Multi-Monitor Support

Dockable or floating panels may eventually support placement on secondary monitors.

Example:

```text
Monitor 1
→ Ticket Workspace

Monitor 2
→ PowerShell + KB + AI
```

Saved layout behavior across changing monitor configurations must fail gracefully.

---

# 71. Accessibility

The GUI should support:

- keyboard navigation
- focus indication
- readable text
- scalable interface
- meaningful labels
- sufficient contrast

Core workflows should not require precise mouse-only interactions.

---

# 72. Keyboard Focus

Focus behavior should be predictable.

Examples:

Opening universal search should place focus directly in the search box.

Opening a new ticket should focus the first required field.

Unexpected focus jumps should be avoided.

---

# 73. Data Tables

Tables should support appropriate:

- sorting
- filtering
- column sizing
- selection
- context actions

Large tables should use pagination or incremental loading where appropriate.

---

# 74. Read vs Edit Modes

Complex records should not always appear permanently editable.

Where appropriate:

```text
View
→ Edit
→ Save / Cancel
```

This reduces accidental changes.

---

# 75. Save Behavior

Save actions should:

- validate
- persist
- clearly report success/failure
- preserve data on recoverable failure

The application should not silently discard unsaved changes.

---

# 76. Unsaved Changes

When navigating away from meaningful unsaved changes:

```text
Save
Discard
Cancel Navigation
```

should be available where appropriate.

---

# 77. Notifications

Notifications should be used sparingly.

Appropriate examples:

- script completed
- diagnostic failed
- integration disconnected
- export completed

Routine successful actions should not produce disruptive popups unnecessarily.

---

# 78. Search Everywhere Principle

Where practical, lists should support search.

Examples:

- tickets
- companies
- contacts
- KB
- scripts
- prompts
- logs

Search behavior should remain consistent.

---

# 79. Context Preservation

Moving between related views should preserve active context.

Example:

```text
Open Ticket
    ↓
Open Related Company
    ↓
Review Company
    ↓
Back
    ↓
Same Ticket
```

This is preferable to making the technician reconstruct the workflow manually.

---

# 80. F7Hub vs External Applications

When an external tool is better suited to the task, F7Hub should launch or integrate with it.

Examples:

```text
VS Code
→ edit scripts

Microsoft Admin Center
→ complex portal administration

Keeper
→ credential management

NinjaOne
→ RMM functions

HaloPSA
→ PSA-specific workflows
```

F7Hub should act as the coordinating workspace.

---

# 81. Initial GUI Scope

The first useful GUI should remain limited.

Recommended initial modules:

```text
Main Application Shell
Dashboard
Tickets
Companies
Contacts
Knowledge Base
Search
Script Library
Settings
Logs
```

This is enough to validate:

- navigation
- persistence
- repositories
- services
- workflows
- search
- state management

---

# 82. Second GUI Stage

After the initial core is stable:

```text
Diagnostics
PowerShell Panel
Clipboard Center
Command Palette
Workspace Profiles
Reporting
```

---

# 83. Later GUI Stage

Future additions:

```text
AI Center
Microsoft Administration
Plugins
HaloPSA Integration
NinjaOne Integration
Advanced Reporting
```

These should not overload the initial application shell.

---

# 84. GUI Architecture Boundary

The GUI must call application services.

Preferred:

```text
Button
  ↓
GUI Controller / View Logic
  ↓
Application Service
  ↓
Repository / Gateway
```

Avoid:

```text
Button
  ↓
SQL Query
```

or:

```text
Button
  ↓
Construct Arbitrary PowerShell
```

---

# 85. GUI State Boundary

Widgets should not become the sole source of application state.

Persistent or shared state should live in appropriate services/models.

Example:

```text
Active ticket
→ application context

Text currently typed into a note editor
→ widget state
```

---

# 86. GUI Testing Priorities

High-priority GUI workflows should include:

1. application startup
2. module navigation
3. create ticket
4. open ticket
5. edit ticket
6. add note
7. ticket search
8. KB search
9. create KB article
10. script review/execution workflow
11. error presentation
12. unsaved changes

---

# 87. GUI Acceptance Criteria

A GUI feature should normally satisfy:

```text
[ ] Clear entry point
[ ] Correct context displayed
[ ] Keyboard navigation considered
[ ] Input validation visible
[ ] Loading state handled
[ ] Empty state handled
[ ] Error state handled
[ ] Success state handled
[ ] Unsaved data protected
[ ] Long-running tasks do not freeze GUI
[ ] Architecture boundary preserved
```

---

# 88. GUI Anti-Patterns

Avoid:

## Giant Main Window

Every feature displayed simultaneously.

## Modal Overload

Routine tasks require repeated popups.

## Hidden Context

Technician cannot tell which ticket or company is active.

## Raw Technical Errors Only

Low-level exceptions are shown with no useful explanation.

## GUI-Owned SQL

Widgets directly query the database.

## GUI-Owned PowerShell

Buttons construct arbitrary shell commands.

## Excessive Tabs

Every piece of information becomes another tab.

## Decorative Density

Too many colors, borders, icons and visual effects reduce readability.

## Mouse-Only Navigation

Important actions cannot be reached efficiently from the keyboard.

---

# 89. GUI Design Decision Rule

For each new interface element, ask:

1. What technician task does it support?
2. Does it belong in the current context?
3. Does an existing panel already provide this function?
4. Should it be persistent or temporary?
5. Is a panel, page, dialog or command more appropriate?
6. Does it reduce or increase context switching?
7. Can the technician understand its state?
8. Is the operation safe?

---

# 90. Core F7Hub Workspace

The intended experience is:

```text
┌───────────────────────────────────────────────────────────────────────────┐
│ F7Hub                                                                     │
├───────────────────────────────────────────────────────────────────────────┤
│ Search / Commands / Active Ticket / Workspace                             │
├───────────────┬───────────────────────────────────────┬───────────────────┤
│ Navigation    │ Current Work                          │ Context           │
│               │                                       │                   │
│ Dashboard     │ Ticket / KB / Script / Diagnostic     │ Company           │
│ Tickets       │                                       │ Related KB        │
│ KB            │                                       │ Diagnostics       │
│ Search        │                                       │ AI                │
│ Scripts       │                                       │                   │
├───────────────┴───────────────────────────────────────┴───────────────────┤
│ PowerShell / Output / Activity / Logs                                     │
├───────────────────────────────────────────────────────────────────────────┤
│ DB ✓ | PS ✓ | Graph ○ | AI ✓ | Workspace: Helpdesk                       │
└───────────────────────────────────────────────────────────────────────────┘
```

This layout is conceptual rather than a fixed pixel specification.

---

# 91. Relationship to Other Documents

## `03_Features.md`

Defines:

> What capabilities exist?

## `04_UserWorkflows.md`

Defines:

> How does the technician use them?

## `05_GUI.md`

Defines:

> How are those capabilities presented and interacted with?

## `06_SystemArchitecture.md`

Defines:

> How do the underlying components cooperate?

## `13_PythonArchitecture.md`

Defines:

> How is the PySide6 implementation structured internally?

---

# 92. Final GUI Principles

The F7Hub interface should:

- keep technician context visible
- reduce unnecessary application switching
- make search central
- expose related knowledge quickly
- integrate diagnostics and automation safely
- remain keyboard-friendly
- support dockable workflows where useful
- remain responsive during long operations
- provide clear states and errors
- preserve unsaved technician work
- avoid duplicating external applications
- remain understandable as features grow

The core GUI principle is:

> Show the technician what matters for the current task, keep related tools nearby, and hide complexity that is not currently useful.

F7Hub should feel like one coherent workspace, not twenty utilities taped together.


# 93. GUI Control & Action Registry

Current extension (2026-10-29): the existing shortcut matrix adds exactly one
Win+Alt+V record for the isolated accepted feature candidate. It is a native
action/event entry, not a new visual control or a second registry. The earlier
Pass 5 presentation counts remain the pinned audit totals. No fresh physical
acceptance is performed by this documentation change.

### Historical registry audit status — pinned 2026-10-27 baseline

**GUI_REGISTRY_READY_FOR_INDEPENDENT_REVIEW — author-side documentation gate.**
Pass 5 reconciles the source-defined GUI construction scope below. This is not
independent approval, runtime validation or integration authority. Stable control
IDs are documentation identifiers only; source and approved architecture govern.
The Pass 1–4 completion/remaining-work paragraphs retain their historical
progression meaning. The Pass 5 counts, coverage, findings and status are current
for this pinned candidate; older partial-readiness statements are not its status.

Pinned integrated-source baseline:
`62f95f185cd5abfefbfbc16822d12dc30144ed79`. A fresh read-only ls-remote query
on 2026-10-27 confirmed remote main at the same SHA; no baseline movement or
merge was performed. The documentation candidate is an uncommitted diff on this
base. `—` means not
applicable; `NOT VERIFIED` means the relationship has not been established.
Integrated means present in the inspected source, not physically tested here.

Navigate: [Shell/Guide/Mochi](#gui-registry-shell),
[Clipboard](#gui-registry-clipboard), [Tickets](#gui-registry-tickets),
[Knowledge](#gui-registry-knowledge), [Scripts](#gui-registry-scripts),
[final coverage/counts](#gui-registry-coverage),
[shortcuts](#gui-registry-shortcuts), [findings](#gui-registry-findings).

<a id="gui-registry-shell"></a>

## Shell, utilities, lifecycle, Mochi and Guide — Pass 4

Inspected integrated source: `62f95f185cd5abfefbfbc16822d12dc30144ed79`.
Entries inherit **Integrated / static inspection**, with runtime/native execution
**NOT RUN**. Source locators are not invented Qt objectNames. `—` means no
source-assigned name or explicit custom shortcut, as applicable. AHK equivalents
use native control/function names, never Qt metadata. Physical rendering,
keyboard acceptance and platform standard-key/mnemonic resolution are
**NOT VERIFIED** here.

Control rows count constructed interactive presentations and transient dialog
choices. `ACTION.*` records name reusable explicit QAction identities; `BIND.*`
records name keyboard/window/native events. Those records are separate from
control counts and are not extra visual buttons. Reused actions/handlers do not
add identities; distinct presentations are identified explicitly. Containers,
passive feedback, native scrolling and repeated topic/data rows are excluded.
Pass 5 still owns final application-wide identity/presentation reconciliation.

### A. Shell and navigation

Owner: [main_window.py](../Python/f7hub/gui/main_window.py), MainWindow and
`_build_navigation_rail`. **MW** =
[MainWindow tests](../Tests/GUI/test_main_window.py), including surviving command
identities, retired containers, rail focus, retained pages and refused routes.
These are test references, not fresh runtime results. MainWindow builds no menu
bar, toolbar, dock or shell splitter; the old menu/toolbar are retired. Its
QHBoxLayout (`navigationShell`) contains the rail (`navigationRail`) then
`workspaceViewport` (resizable QScrollArea hosting the retained `pages` stack).
Source calls statusBar().showMessage; no application-defined interactive status
control is constructed. Native frame/size-grip behavior is inherited and is not
an additional source-defined control mapping.
Module-owned splitters and forms remain in their existing inventory sections.

`Shell-busy` is `_set_busy`'s union of supplied/shared-runner busy, Script run
ownership and Ticket note/creation/status/classification pending flags. It
disables pages and the four module actions; optional Knowledge/Scripts also
require their workspaces. Clipboard Recent/Setup use their separate guards,
not a new global shell-busy owner. Individual route methods retain draft and
pending guards; an enabled presentation alone does not prove dispatch.

| Stable ID | Label / type / objectName | Logical location | Action/event → owner/handler | Availability / accessibility / keyboard | Tests |
|---|---|---|---|---|---|
| SHELL.NAV.TICKETS | Tickets; QToolButton; `ticketsNavigationButton` | Rail QVBoxLayout first module button | setDefaultAction(tickets_action) → show_tickets; local page route | Not Shell-busy; accessible Tickets, TabFocus; native Space; no custom shortcut on button | MW |
| SHELL.NAV.KNOWLEDGE | Knowledge Base; QToolButton; `knowledgeNavigationButton` | Rail second module button | setDefaultAction(knowledge_action) → show_knowledge | Not Shell-busy and workspace supplied/constructed; unavailable tooltip points to utility Guide; accessible Knowledge Base, TabFocus | MW |
| SHELL.NAV.SCRIPTS | Scripts; QToolButton; `scriptsNavigationButton` | Rail third module button | setDefaultAction(scripts_action) → show_scripts | Not Shell-busy and workspace supplied; accessible Scripts, TabFocus | MW |
| SHELL.NAV.CLIPBOARD | Clipboard Center; QToolButton; `clipboardNavigationButton` | Rail fourth module button | setDefaultAction(clipboard_action) → show_clipboard; retained lazy page | Not Shell-busy; accessible Clipboard Center, TabFocus; workspace details remain in Pass 3 | MW |
| SHELL.UTILITIES.SETTINGS | Settings and utilities; QToolButton; `settingsUtilityButton` | Rail after module buttons and stretch, bottom | clicked → _show_utility_menu; same popup handler as Alt+S | No local busy disabling; popup/modal guard in handler; accessible Settings and utilities, description Alt+S opens Settings and utilities; TabFocus | MW |

| Action identity (not extra control) | Source member / objectName / data | Signal → handler | Presentations |
|---|---|---|---|
| ACTION.NAV.TICKETS | MainWindow.tickets_action; — | triggered → show_tickets | SHELL.NAV.TICKETS |
| ACTION.NAV.KNOWLEDGE | MainWindow.knowledge_action; — | triggered → show_knowledge | SHELL.NAV.KNOWLEDGE |
| ACTION.NAV.SCRIPTS | MainWindow.scripts_action; — | triggered → show_scripts | SHELL.NAV.SCRIPTS |
| ACTION.NAV.CLIPBOARD | MainWindow.clipboard_action; clipboardCenterAction; data clipboard.center | triggered → show_clipboard | SHELL.NAV.CLIPBOARD |

| Binding identity (not extra control) | Definition / scope | Handler / guarded effect | Tests |
|---|---|---|---|
| BIND.SHELL.NAVIGATION | QShortcut Alt+F; WidgetWithChildrenShortcut; auto-repeat false | activated → _focus_navigation; selected enabled/visible rail button, else first eligible module, else gear; no page change; refuses active popup/modal | MW |

`pages.currentChanged` → `_sync_navigation_rail` derives active icon/property and
accessible description Current workspace from actual page identity, without
making QActions checkable. Accepted page changes synchronously reset shell
scrollbars; same-page/refused routes do not. Explicit Tab links place viewport
→ Tickets → Knowledge → Scripts → Clipboard → gear → New Ticket; disabled
controls are handled by Qt. The shell event filter handles rail return/escape
and generation-guarded focus reconciliation; later deliberate focus/scroll or
deactivation defeats obsolete restoration. Actual physical traversal remains
unverified. Utility-popup show/hide temporarily suspends both shell shortcuts,
resuming on a later event turn; separate windows retain their own shortcuts.

### B. Settings and utility menus

Owner: MainWindow `_build_navigation_rail`, `_show_utility_menu`,
show_mochi_settings, back_up_database and show_altf7hub. The gear is the existing
SHELL.UTILITIES.SETTINGS presentation, not another Settings Center. Its popup
(`settingsUtilityMenu`) inserts Mochi…, Back up database, E&xit, then Knowledge
Base tools (`knowledgeBaseToolsMenu`) → Guide. The submenu is one navigable menu
entry; its Qt-generated menu action is not an extra explicit application QAction.
The popup is anchored to the gear's right/top and clamped to available screen
geometry; active popup/modal prevents a second popup. No source-defined separator
or menu-bar/toolbar duplicate remains. **GR** =
[Guide relocation tests](../Tests/GUI/test_guide_relocation.py); MW covers utility
shortcuts, backup outcomes and command survival.

| Stable ID | Label / type / objectName | Logical location | Signal → handler / dependency | Availability / accessibility / keyboard | Tests |
|---|---|---|---|---|---|
| SHELL.UTILITIES.MOCHI | Mochi…; QAction menu presentation; mochiSettingsAction | Utility popup first | triggered → show_mochi_settings → retained MochiSettingsDialog/MochiService | Requires mochi_service; no shell-busy disable in _set_busy; dialog is shown/raised/activated, never launches on menu construction; no custom shortcut | MW, MC |
| SHELL.UTILITIES.BACKUP | Back up database; QAction menu presentation; backupDatabaseAction | Popup second | triggered → back_up_database → shared ServiceTaskRunner → DatabaseBackupService.create_backup | Requires backup_service and not Shell-busy; handler rechecks pending owners; no custom shortcut | MW |
| SHELL.UTILITIES.EXIT | E&xit; QAction menu presentation; exitAction | Popup third | triggered → request_exit → lifecycle.request_exit, or standalone close | Not disabled by _set_busy; accepted Exit still needs shared guards and draft confirmation; mnemonic &x; StandardKey.Quit binding below | MW, LC |
| SHELL.UTILITIES.KNOWLEDGE_TOOLS | Knowledge Base tools; QMenu submenu; knowledgeBaseToolsMenu | Popup fourth/last | Native submenu open → Guide entry | No custom availability/shortcut assigned; independent of Knowledge workspace construction | GR |
| SHELL.UTILITIES.GUIDE | Guide; QAction menu presentation; altF7HubGuideAction | Knowledge Base tools submenu, only child | triggered → show_altf7hub → shared runner → AltF7HubService.show_guide | Requires altf7hub_service and not Shell-busy; same QAction as KNOWLEDGE.GUIDE, even if Knowledge unavailable; no custom shortcut on QAction | GR, MW |
| SHELL.FEEDBACK.BACKUP.SUCCESS | OK; standard QMessageBox choice; — | Database backup completed information dialog | back_up_database.completed → information; acknowledgement dismisses feedback | Only successful backup completion; no second backup dispatch; native Qt default acknowledgement, no custom button label/slot | MW |
| SHELL.FEEDBACK.BACKUP.FAILURE | OK; standard QMessageBox choice; — | Database backup failed warning dialog | back_up_database.failed → warning | Safe fixed failure text; no completed backup claimed; native acknowledgement | MW |
| SHELL.FEEDBACK.GUIDE.FAILURE | OK; standard QMessageBox choice; — | Guide could not open warning dialog | show_altf7hub.failed → warning | Unconfirmed request; safe AltF7HubOpenError or fixed fallback; no automatic second request; native acknowledgement | MW, GR |
| SHELL.FEEDBACK.STARTUP.FAILURE | OK; standard QMessageBox critical choice; — | App entry point, F7Hub could not start; parent None, before MainWindow is shown | [app.main.main](../Python/f7hub/app/main.py): bootstrap exception → critical → return 1 after acknowledgement | Fixed service-initialization feedback; no retry or new service operation; native acknowledgement/focus not exercised | [startup failure test](../Tests/Integration/test_application_bootstrap.py) |

| Action identity (not extra control) | Source member / objectName | Signal → handler | Presentations |
|---|---|---|---|
| ACTION.UTILITIES.MOCHI | MainWindow.mochi_action; mochiSettingsAction | triggered → show_mochi_settings | SHELL.UTILITIES.MOCHI |
| ACTION.UTILITIES.BACKUP | MainWindow.backup_action; backupDatabaseAction | triggered → back_up_database | SHELL.UTILITIES.BACKUP |
| ACTION.UTILITIES.EXIT | MainWindow.exit_action; exitAction | triggered → request_exit | SHELL.UTILITIES.EXIT; MainWindow.addAction also registers its shortcut, not another visual control |
| ACTION.UTILITIES.GUIDE | MainWindow.altf7hub_action; altF7HubGuideAction | triggered → show_altf7hub | SHELL.UTILITIES.GUIDE and existing KNOWLEDGE.GUIDE button share one identity |

| Binding identity (not extra control) | Definition / scope | Handler / effect | Tests |
|---|---|---|---|
| BIND.SHELL.UTILITIES | QShortcut Alt+S; WidgetWithChildrenShortcut, no auto-repeat | activated → _show_utility_menu; popup-local suspension described above | MW |
| BIND.SHELL.QUIT | QKeySequence.StandardKey.Quit on exit_action; Ctrl+Q fallback only if standard sequence empty on win32 | QAction triggered → request_exit; registered on MainWindow independent of popup visibility | MW, LC |

[DatabaseBackupService](../Python/f7hub/services/database_backup_service.py)
owns explicit local snapshot creation via existing create_database_snapshot
infrastructure, publishing a unique backup beneath LOCALAPPDATA/F7Hub/Backups.
GUI owns no SQL/path picker and supplies no arbitrary command. A successful path
is reported only by the completion callback; error feedback does not expose raw
exceptions. [AltF7HubService](../Python/f7hub/services/altf7hub_service.py) delegates
the fixed Guide request boundary described in E. Utility operations reuse their
existing services rather than adding a general Settings service or new router.

### C. Tray and lifecycle

Owner: [application_lifecycle.py](../Python/f7hub/gui/application_lifecycle.py),
ApplicationLifecycle; **LC** =
[lifecycle tests](../Tests/GUI/test_application_lifecycle.py). One retained
MainWindow gets one lifecycle owner. start shows the icon, starts the recovery
timer and disables last-window automatic quitting; repeated start is a no-op.
Tray geometry/overflow and actual Windows interaction are not verified here.

| Stable ID | Label / type / objectName | Logical location | Signal/event → handler | Availability / focus / keyboard | Tests |
|---|---|---|---|---|---|
| LIFECYCLE.TRAY.ICON | F7Hub tooltip; QSystemTrayIcon; — | Windows notification area, platform-selected position; attached QMenu | activated(reason) → _activated → restore for Trigger/DoubleClick; native context menu exposes two actions | Constructed once; shown by start, hidden on accepted exit/aboutToQuit; no custom shortcut/accessibility name assigned | LC |
| LIFECYCLE.TRAY.OPEN | Open F7Hub; QAction menu presentation; — | Tray context menu first | open_action.triggered → restore | No explicit disable; restore refuses accepted exit, clears minimized state, restores retained window and usable remembered focus; no custom shortcut | LC |
| LIFECYCLE.TRAY.EXIT | Exit F7Hub; QAction menu presentation; — | Tray context menu second/last | exit_action.triggered → request_exit → restore → MainWindow.confirm_exit → cleanup_shutdown/quit | Reentrant/accepted exit refused; pending work or draft Cancel keeps application; no custom shortcut | LC |
| LIFECYCLE.CONFIRM.NEW_TICKET.DISCARD | Discard; QMessageBox standard choice; — | MainWindow.confirm_exit → Unsaved new ticket modal action area | Question result Discard permits remaining Clipboard guard, then accepted exit | Only outstanding creation draft after Ticket activity guard; caller-specific Exit prompt, not an extra Ticket creation button | LC, MW |
| LIFECYCLE.CONFIRM.NEW_TICKET.CANCEL | Cancel; QMessageBox standard choice; — | Same modal action area | Non-Discard result refuses shutdown | Explicit default Cancel; preserves draft; native resolution NOT VERIFIED | LC, MW |

| Action identity (not extra control) | Source member | Signal → handler | Relationship |
|---|---|---|---|
| ACTION.TRAY.OPEN | ApplicationLifecycle.open_action; no objectName | triggered → restore | LIFECYCLE.TRAY.OPEN; icon activation also invokes restore without another QAction |
| ACTION.TRAY.EXIT | ApplicationLifecycle.exit_action; no objectName | triggered → request_exit | LIFECYCLE.TRAY.EXIT; distinct from ACTION.UTILITIES.EXIT, same coordinator |

| Binding identity (not extra control) | Definition / scope | Handler / effect | Tests |
|---|---|---|---|
| BIND.LIFECYCLE.CLOSE | MainWindow closeEvent, including native window X | With unaccepted composed lifecycle: ignore close and lifecycle.hide; standalone host uses confirm_exit; accepted lifecycle permits close | LC |
| BIND.LIFECYCLE.ACTIVATE | QSystemTrayIcon.activated Trigger/DoubleClick | _activated → restore; other reasons do not trigger this restore branch; one icon, not two buttons | LC |

hide preserves work without invoking draft guards or Clipboard leave. It hides
only when the started, visible non-null icon has nonempty geometry, an enabled
retained Open menu route and a system tray; otherwise the window remains/restores
visible with recovery feedback. Hidden recovery timer cadence is 100 ms; normal
cadence is 1000 ms. The timer itself is not an interactive control.

PR #114 is included in the pinned source: check_recovery reconciles an owned
hidden window through the read-only
[Windows visibility adapter](../Python/f7hub/infrastructure/windows_window_visibility.py).
A native-visible HWND restores Qt presentation with activate=False/normalize=True;
lost tray recovery also restores. The accepted/exiting guards prevent reentry.
restore otherwise preserves maximized state as appropriate and retains editor
focus when usable; a refused OS foreground activation is not forced success.
This source trace preserves the earlier exposure-only white-window failure
record at the document start and does not establish a new physical result.

request_exit restores a visible owner before confirmation. MainWindow rejects
shared/Ticket/Script/Knowledge-filter/Clipboard pending work, then applies Ticket
activity, new-ticket and Clipboard draft guards. Existing Ticket activity and
Clipboard confirmation choices remain in their owning module inventories.
Cancel never authorizes cleanup. Accepted exit cleans once, stops timer, hides
tray, closes the retained window and quits. aboutToQuit uses the same idempotent
cleanup. No Clipboard acquisition or persistence operation is added by lifecycle.

### D. Mochi entry, control dialog and module-owned pet menu

The shell entry is SHELL.UTILITIES.MOCHI; do not count it again. Owner:
[mochi_settings_dialog.py](../Python/f7hub/gui/mochi_settings_dialog.py),
MochiSettingsDialog (`mochiSettingsDialog`), parented to MainWindow, modeless,
WA_DeleteOnClose. Its VBox contains passive mochiStatus, a two-column QGridLayout,
then Close. MainWindow retains/raises one dialog and clears its reference on
finished. **MC** = [F7Hub Mochi controls tests](../Tests/GUI/test_mochi_controls.py).
All seven buttons have source objectNames but no explicit accessibleName,
custom shortcut, mnemonic or Tab-order assignment; native button text/focus
behavior is not a new accessibility-validation claim.

`M-usable` means availability AVAILABLE, snapshot present and behavior not
EXITING. render disables command buttons while service.busy; Start/Show only
requires not busy. Idle/Wave additionally require not paused. Status is plain
text and distinguishes connecting/unavailable/timeout/disconnected/uncertain;
an unconfirmed command is not reported as success.

| Stable ID | Label / member; type; objectName | Grid/parent position | Signal → handler / backend | Availability / keyboard | Tests |
|---|---|---|---|---|---|
| MOCHI.DIALOG.START | Start/Show / buttons[start]; QPushButton; mochi_start | Grid row 0 column 0 | clicked closure → invoke(start) → MochiService.start_show | Not service.busy; explicit retry/start/show | MC |
| MOCHI.DIALOG.HIDE | Hide / buttons[hide]; QPushButton; mochi_hide | Row 0 column 1 | invoke(hide) → service.command(hide) | Not busy and M-usable; no F7Hub window hide | MC |
| MOCHI.DIALOG.IDLE | Idle / buttons[idle]; QPushButton; mochi_idle | Row 1 column 0 | invoke(idle) → service.command(idle) | Not busy, M-usable, not paused | MC |
| MOCHI.DIALOG.WAVE | Wave / buttons[wave]; QPushButton; mochi_wave | Row 1 column 1 | invoke(wave) → service.command(wave) | Not busy, M-usable, not paused; existing delivered animation command only | MC |
| MOCHI.DIALOG.PAUSE | Pause / Resume / buttons[pause]; QPushButton; mochi_pause | Row 2 column 0 | invoke(pause) resolves snapshot.paused to command resume or pause | Not busy and M-usable; one button, changing label | MC |
| MOCHI.DIALOG.EXIT | Exit / buttons[exit]; QPushButton; mochi_exit | Row 2 column 1 | invoke(exit) → service.command(exit) | Not busy and M-usable; stops Mochi, not F7Hub | MC |
| MOCHI.DIALOG.CLOSE | Close / local close; QPushButton; mochi_close | VBox below grid | clicked → close → closeEvent → unsubscribe(render) | No explicit busy disable; closing dialog does not send Mochi Exit | MC |

[MochiService](../Python/f7hub/services/mochi_service.py) validates its finite
command set and tracks availability/snapshot/outcome; start_show requests the
existing [MochiGateway](../Python/f7hub/infrastructure/mochi_gateway.py) start with
show=True. Commands use the reviewed local companion channel, not SQL or an
arbitrary process/AI command. subscribe/render updates this UI; Close removes
only the subscription. MainWindow shutdown owns the separate service cleanup.

The integrated module's separate
[PetWindow](../Mochi/src/mochi/ui/pet_window.py) owns its own QMenu and local
runtime, not MainWindow actions. **MP** =
[pet-window tests](../Mochi/tests/test_pet_window.py), **MT** =
[runtime-control tests](../Mochi/tests/test_controls.py). These references are
inspected, not executed. The frameless tool window is translucent, optionally
topmost from settings, NoFocus/ShowWithoutActivating at construction; native
click/menu behavior remains unverified here. No in-window Settings form is
constructed; file settings are not new GUI controls. Context menu order:

| Stable ID | Label / type / objectName | Position / event | Owner/handler / backend | Enabled condition | Tests |
|---|---|---|---|---|---|
| MOCHI.PET.SURFACE | Configured pet name; PetWindow(QWidget) painted input surface; — | Separate frameless top-level pet canvas; constructed by [Mochi app](../Mochi/src/mochi/app.py) | mousePressEvent/mouseMoveEvent/mouseReleaseEvent → retained drag offset/move; contextMenuEvent → local menu | NoFocus/ShowWithoutActivating construction; left drag and native context event are explicitly handled; actual configured caption/native behavior NOT VERIFIED | MP, MT |
| MOCHI.PET.PAUSE | Pause; QAction menu presentation; — | Pet context menu first; triggered | PetWindow.pause → apply(pause) → local PetRuntime | State IDLE or WAVE | MP, MT |
| MOCHI.PET.RESUME | Resume; QAction menu presentation; — | Context menu second; triggered | PetWindow.resume → apply(resume) | State PAUSED | MP, MT |
| MOCHI.PET.EXIT | Exit; QAction menu presentation; — | Context menu third; triggered | PetWindow.close → closeEvent/shutdown | State not EXITING | MP, MT |

These three explicit QActions are distinct module-local identities
ACTION.MOCHI.PAUSE (pause_action), ACTION.MOCHI.RESUME (resume_action) and
ACTION.MOCHI.EXIT (exit_action). They have no explicit custom shortcut/name and
are not the seven F7Hub dialog buttons. BIND.MOCHI.PET.MENU maps contextMenuEvent
to _sync_actions/menu.popup(globalPos); BIND.MOCHI.PET.DRAG maps left press/move/
release to retained offset/move/clear. They are event bindings on the existing
pet surface MOCHI.PET.SURFACE, not extra buttons. Animation timers/state changes add no controls.
Recognition, screen-context guidance, Luna/provider actions and unrelated
planned animation behaviors are not delivered controls in these sources.

### E. Guide and AutoHotkey v2

Integrated host: [F7Hub.ahk](../AutoHotkey/F7Hub.ahk), #Requires AutoHotkey v2,
#SingleInstance Ignore, #MaxThreadsPerHotkey 1. It owns F7 and Alt+F7, and
includes [GuideHost](../AutoHotkey/Troubleshooting_Sections/GuideHost.ahk),
[GuideCore](../AutoHotkey/Troubleshooting_Sections/GuideCore.ahk) and the request
bridge. **AT** = [toggle tests](../Tests/AutoHotkey/test_altf7hub_toggle.ahk),
**AH** = [host tests](../Tests/AutoHotkey/test_altf7hub_host.ahk), **AN** =
[navigation tests](../Tests/AutoHotkey/test_altf7hub_navigation.ahk), **AR** =
[request-failure tests](../Tests/AutoHotkey/test_altf7hub_request_failure.ahk),
**AL** = [launcher tests](../Tests/AutoHotkey/test_f7hub_launcher.ahk), **AF** =
[F7 restore tests](../Tests/AutoHotkey/test_f7hub_restore.ahk), **AM** =
[magnetic follower tests](../Tests/AutoHotkey/test_magnetic_window_follower.ahk),
**AP** = [Python launch integration](../Tests/Integration/test_altf7hub_launch.py).
**GF** = [Guide formatting safety](../AutoHotkey/Troubleshooting_Sections/Tests/guide_formatting_safety.ahk),
**GT** = [topic routing contract](../AutoHotkey/Troubleshooting_Sections/Tests/topic_contract.ahk).
Test source references do not establish fresh native/physical acceptance.
GuideCore includes [TopicRouting](../AutoHotkey/Troubleshooting_Sections/TopicRouting.ahk):
BuildShortcuts, TopicShortcutEnabled and ShortcutTarget own catalog shortcut
resolution (GT). GF checks selected-text formatting and stale-source save safety;
native button/acknowledgement acceptance remains NOT VERIFIED. These test sources
were inspected without running them or opening their topic/preference inputs.

The Python Guide entry uses MainWindow → ServiceTaskRunner → AltF7HubService →
[WindowsAltF7HubGateway](../Python/f7hub/infrastructure/altf7hub_gateway.py) → fixed
[short-lived request client](../AutoHotkey/Troubleshooting_Sections/Troubleshooting_Quick_Guide.ahk)
with --show → [GuideRequest](../AutoHotkey/Troubleshooting_Sections/GuideRequest.ahk)
→ shared host. Gateway validates Windows, standard 64-bit AHK v2 and required
files, starts no shell, and accepts only successful SHOWN/FOCUSED_EDITOR output.
The checkout-derived endpoint's fixed F7Hub.AltF7Hub.Show.v1 request calls
ShowGuide, not ToggleGuide. An existing editor is focused with its draft intact.
Dispatched timeout remains unconfirmed, not permission to send a second toggle;
pre-dispatch keyboard fallback has readiness/dispatch/held-modifier guards.
Double-click client without --show starts/reuses the host without presenting
Guide; errors can show the client warning listed below. There is no second
persistent Guide or topic-to-ticket automation.

#### Guide-owned controls

Owner for the next tables: GuideCore CreateGuide, AddFormattingToolbar,
ShowEditor and named handlers. AHK controls have native HWNDs/member locators,
not Qt objectNames; no explicit custom accessible names or global shortcuts are
assigned to these controls. Native captions/cues and keyboard routing below are
source facts, not a screen-reader result. Initial logical positions use source
rows/relative coordinates; ResizeGuide/ResizeEditor reposition controls, so no
physical pixel claim is made. Passive Opacity/percentage/topic title/status,
editor labels and Selected words labels are excluded.

Guide is a resizable window titled Guide. Top row is opacity, pin, sidebar,
heading color and bold headings. Sidebar has search, Create/Edit/Script row,
Archive/View row and topic list. Notes area is to the right, below title and
formatting/Auto-fit row. Sidebar controls become hidden with SidebarHidden.
ShowGuide focuses the notes control and preserves its selection/scroll; an
existing editor takes priority. No authored topic is counted separately.

| Stable ID | Label / native type / locator | Position / owner | Event → handler / backend | Availability / keyboard / tests |
|---|---|---|---|---|
| GUIDE.OPACITY | Opacity; Slider; OpacitySlider | CreateGuide top row x74, range 60–100 | Change → ChangeOpacity → SetGuideOpacity / deferred preferences | Native slider/tooltip; shared Guide/editor opacity; AH, AT |
| GUIDE.PIN | Always on top; Checkbox; PinCheck | Top row after opacity/percentage | Click → ChangePin → ApplyPin / preferences | Reflects Pinned; native checkbox; AH |
| GUIDE.SIDEBAR | Show topics / Hide topics; Button; SidebarButton | Top row after pin | Click → ToggleSidebar → ApplySidebar | One changing-label control; no custom shortcut; AH |
| GUIDE.HEADING.COLOR | Heading color; Button; colorButton | Top row after sidebar | Click → ChangeHeadingColor → PickColor / formatting preferences | Native color picker; Cancel returns without chosen color; AH |
| GUIDE.HEADING.BOLD | Bold headings; Checkbox; HeadingBoldCheck | Top row after Heading color | Click → ChangeHeadingBold → RefreshFormatting / preferences | Reflects HeadingBold; native checkbox; AH |
| GUIDE.SEARCH | Search topics... cue; Edit; SearchBox | Sidebar first, y52 | Change → FilterTopics → RebuildTopicList | Filters title/body/id/shortcut locally; Ctrl+F focuses; AN, AH |
| GUIDE.CREATE | C - Create; Button; CreateButton | Sidebar action row first, y90 | Click closure → ShowEditor(create) | Disabled in archive; focused notes/list C route also invokes; AH |
| GUIDE.EDIT | E - Edit; Button; EditButton | Same row second | Click closure → ShowEditor(edit) | Active topic required and not archive; focused notes/list E route; AH |
| GUIDE.SCRIPT | Script; Button; scriptButton | Same row third | Click → OpenScript → fixed notepad.exe with local request-client source path | Opens AHK source for editing; not Scripts workspace or diagnostic execution; AH |
| GUIDE.ARCHIVE | Archive topic / Restore topic; Button; ArchiveButton | Sidebar next row first, y130 | Click → ArchiveOrRestore → MoveTopic / paired topic files | Current displayed topic required; source invokes no confirmation; errors retain feedback path; AH |
| GUIDE.ARCHIVE.VIEW | View archive / Back to guide; Button; ArchiveViewButton | Same row second | Click → ToggleArchiveView → FilterTopics | Changes library mode and clears search; disables create/edit in archive; AH |
| GUIDE.TOPICS | Topic list; ListBox; TopicList | Sidebar below action rows, y170 | Change → SelectTopic; scoped navigation → NavigateTopic/ShowTopic | Dynamic rows from displayed library, owner-drawn titles; repeated rows not controls; AN, AH |
| GUIDE.FORMAT.COLOR | Text color; Button; toolbar color | Notes toolbar after Selected words label, y90 | Click closure → FormatSelection(false, color) → PickColor / WriteTopic | Requires current topic and selected range; failure has acknowledgement below; AH; direct formatting acceptance NOT VERIFIED |
| GUIDE.FORMAT.BOLD | Bold; Button; toolbar bold | Same toolbar after Text color | Click closure → FormatSelection(false, bold) | Same selected-range guard; saves local formatting sidecar/topic pair; AH |
| GUIDE.FORMAT.RESET | Reset formatting; Button; toolbar reset | Same toolbar after Bold | Click closure → FormatSelection(false, reset) | Removes selected-range personal formatting; same guards; AH |
| GUIDE.AUTOFIT | Auto-fit text; Checkbox; AutoFitCheck | Right of formatting toolbar, y90 | Click → ChangeAutoFit → FitNotes / preferences | Reflects AutoFit; fits notes with bounded font search; AH |
| GUIDE.NOTES | Topic notes; Custom RICHEDIT50W; NotesBox | Notes area below toolbar, x296/y128 initially | CreateRichControl(..., true); selection/focus/native read-only text; HandleGuideKeys when scoped | Read-only text; native selection/scroll/copy; no command execution; AN, AH |

ShowEditor creates one owned Create topic/Edit topic window, disables Guide
while open, and reuses an already-open editor. ID/shortcut are on the first row,
Title next, then formatting toolbar/body and bottom Save/Cancel. It focuses ID
for create, Title for edit. Cancel/X/Escape use CloseEditor, destroy the editor
and re-enable/activate Guide; no unsaved-editor confirmation is constructed.
Failure to save preserves the editor. These controls are distinct instances of
the shared toolbar factory, not duplicate function implementations.

| Stable ID | Label / native type / locator | Position | Event → handler / backend | Availability / keyboard / tests |
|---|---|---|---|---|
| GUIDE.EDITOR.ID | ID; Edit; EditorId | First row left, x50/y12 | Read by SaveEditor(mode) | Read-only for edit, editable for create; AH |
| GUIDE.EDITOR.SHORTCUT | Shortcut; Edit; EditorShortcut | First row after ID, x374/y12 | Read by SaveEditor; Uppercase Limit1 | Optional; displayed reserved-letter guidance and SaveEditor validation govern; no global hotkey registration; AH |
| GUIDE.EDITOR.TITLE | Title; Edit; EditorTitle | Second row x66/y50 | Read by SaveEditor | Single-line title required; first edit-mode focus; AH |
| GUIDE.EDITOR.FORMAT.COLOR | Text color; Button; toolbar color | Editor toolbar after Selected words, x16/y88 row | Click → FormatSelection(true, color) | Selected editor range required; native picker; changes EditorRuns pending Save; AH |
| GUIDE.EDITOR.FORMAT.BOLD | Bold; Button; toolbar bold | Same toolbar second button | Click → FormatSelection(true, bold) | Selected editor range; no immediate library write; AH |
| GUIDE.EDITOR.FORMAT.RESET | Reset formatting; Button; toolbar reset | Same toolbar third button | Click → FormatSelection(true, reset) | Removes selected editor formatting; no immediate library write; AH |
| GUIDE.EDITOR.BODY | Topic body; Custom RICHEDIT50W; EditorBody | Below toolbar x16/y130; resized with window | HandleEditorChange WM_COMMAND/EN_CHANGE and SyncEditorText timer; SaveEditor reads text/runs | Editable native text/undo; plain topic content, not shell input; AH |
| GUIDE.EDITOR.SAVE | Save; Button; EditorSave | Bottom row before Cancel | Click closure → SaveEditor(mode) → WriteTopic, update library and CloseEditor | Validates ID/uniqueness/shortcut/title/body; preserves draft on failure; no custom save shortcut installed; AH |
| GUIDE.EDITOR.CANCEL | Cancel; Button; EditorCancel | Bottom right after Save | Click → CloseEditor; same as editor Close/Escape events | Discards uncommitted editor session without library save; AH |

Guide topic edits/formatting/archive use GuideCore's local paired text/style
file owner, not core SQLite. Preference handlers use existing bounded/deferred
settings functions. This inventory reads source only: no topics, preference
contents or protected GuideSettings.ini metadata were opened. PickColor invokes
the OS ChooseColorW dialog; inherited native picker internals are not separately
constructed application controls and are excluded like inherited editor menus.

#### Native feedback choices

Each row is one standard OK acknowledgement at a source call site, not another
domain operation. Native button focus/ordering and physical acceptance are
NOT VERIFIED. There is no retry/save permission implied by acknowledgement.

| Stable ID | Dialog title / native choice | Source caller / trigger | Result / tests |
|---|---|---|---|
| GUIDE.FEEDBACK.SELECTION | Text formatting / OK | GuideCore.FormatSelection: no selected range | Returns false; AH; direct assertion not identified |
| GUIDE.FEEDBACK.FORMAT.SAVE | Save failed / OK | FormatSelection: WriteTopic fails/stale text | Retains operation failure; AH; direct assertion not identified |
| GUIDE.FEEDBACK.ID.INVALID | Invalid ID / OK | SaveEditor: ID syntax/length invalid | Editor retained; AH |
| GUIDE.FEEDBACK.ID.DUPLICATE | ID already used / OK | SaveEditor: active/archive ID collision | No save; AH |
| GUIDE.FEEDBACK.SHORTCUT.INVALID | Invalid shortcut / OK | SaveEditor: fixed/reserved shortcut invalid | No save; AH |
| GUIDE.FEEDBACK.SHORTCUT.RESERVED | Shortcut already used / OK | SaveEditor: built-in shortcut collision | No save; AH |
| GUIDE.FEEDBACK.SHORTCUT.DUPLICATE | Shortcut already used / OK | SaveEditor: other custom shortcut collision | No save; AH |
| GUIDE.FEEDBACK.CONTENT | Missing content / OK | SaveEditor: title/body invalid | Editor retained; AH |
| GUIDE.FEEDBACK.EDITOR.SAVE | Save failed / OK | SaveEditor: WriteTopic failure | Draft remains in editor; AH |
| GUIDE.FEEDBACK.MOVE | Topic not moved / OK | ArchiveOrRestore: MoveTopic error | No success claim; AH |
| AHK.FEEDBACK.LAUNCHER | F7Hub launcher / OK | F7HotkeyController.ReportError after TAP/HOLD error | Current press consumed; no automatic retry while held; AL, AM |
| AHK.FEEDBACK.CLIENT | Guide could not start / OK | Troubleshooting_Quick_Guide catch without --show | Native warning then failure exit; --show instead reports stderr; AR, AP |

#### Hotkeys, event scope and launcher ownership

[F7HotkeyController](../AutoHotkey/Hotkeys/F7HotkeyController.ahk) and
[F7HubLauncher](../AutoHotkey/Launchers/F7HubLauncher.ahk) are the existing owners;
[MagneticWindowFollower](../AutoHotkey/Helpers/MagneticWindowFollower.ahk) owns
cursor-follow movement. No new hotkeys are registered by this documentation.

| Binding identity (not extra control) | Definition / source scope | Handler / target / condition | Tests |
|---|---|---|---|
| BIND.AHK.F7.DOWN | F7:: in F7Hub.ahk | f7Controller.OnDown → PENDING, one 180-ms hold timer; repeated presses ignored outside IDLE | AL, AM |
| BIND.AHK.F7.UP | F7 up:: | OnUp: PENDING → RunTap → LaunchOrFocus; HOLD_STARTING/HOLDING/WAIT_RELEASE → Stop and IDLE | AL, AM, AF |
| BIND.AHK.F7.HOLD | BeginHold timer while physical F7 remains down | LaunchOrFind visible validated HWND → follower.Start; no foreground-focus requirement; release/failure stops, failure consumes press | AM, AF |
| BIND.AHK.GUIDE.TOGGLE | $!F7::, shared-host global Alt+F7 | ToggleGuide: hide active Guide only without editor; otherwise ShowGuide; editor/draft takes priority | AT, AH |
| BIND.AHK.GUIDE.SEARCH | $^f:: under Guide active HWND #HotIf | FocusSearch; show sidebar and focus search | AH, AN |
| BIND.AHK.GUIDE.SIDEBAR | ^l:: under same Guide active scope | ShowSidebar | AH |
| BIND.AHK.GUIDE.PREVIOUS | ^PgUp:: under Guide active scope | NavigateTopic(-1) | AN |
| BIND.AHK.GUIDE.NEXT | ^PgDn:: under Guide active scope | NavigateTopic(1) | AN |
| BIND.AHK.GUIDE.HIDE | Esc:: under Guide active scope; Guide Close event | Guide.Hide; leaves shared host running | AT, AH |
| BIND.AHK.GUIDE.ARROWS | Up/Down/Left/Right #HotIf GuideNavigationFocused(); WM_KEYDOWN HandleGuideKeys | NotesBox/TopicList focus, active Guide and no Ctrl/Alt/Shift/Win; Up/Down navigate with repeat, Left/Right change opacity ±1; other controls keep native input | AN |
| BIND.AHK.GUIDE.LETTERS | GuideHost OnMessage(0x100, HandleGuideKeys), notes/list scope | Non-repeat C/E create/edit outside archive; valid ShortcutTarget letters/1–5 open topics; no per-topic inventory or new global hotkeys | AH, AN |
| BIND.AHK.EDITOR.CLOSE | EditorGui Close/Escape events | CloseEditor; separate from Guide-hide Escape scope | AH |

Launcher finds hidden/existing windows before launching the checkout's pythonw
module entry. IsF7HubWindow checks exact F7Hub title, Qt window class and Python
process-name pattern; it does **not** check the target process command line or
project root. Cross-checkout disambiguation is therefore NOT VERIFIED, a
source-grounded follow-up rather than an invented identity guarantee. PendingPid
prevents repeated launches after readiness timeout. EnsureVisible uses native
show without activation; Focus separately activates and checks foreground within
two seconds, reporting refusal rather than forcing focus. These AHK operations
remain distinct from PR #114's Python timer/Qt restoration.

GuideHost installs keyboard/editor/native draw callbacks and the hidden request
endpoint; that endpoint and passive owner-draw/resize/timer state are not extra
controls. Default AutoHotkey host-tray commands and native editor menus are
framework-owned, not custom F7Hub menu construction. Native hotkey precedence,
modifier/input acceptance, file-save recovery and window presentation were not
executed here. No current topic contents, protected preferences or native
Clipboard data were inspected.

### Shell-family current coverage and Pass 4 historical validation

| Pass 4 presentation group | Control rows |
|---|---:|
| A: navigation rail and gear | 5 |
| B: utility/menu presentations and feedback choices | 9 |
| C: tray icon/menu and new-ticket Exit confirmation | 5 |
| D: Mochi dialog, interactive pet surface and module pet menu | 11 |
| E: Guide window/editor controls and native feedback choices | 38 |
| **Current shell-family total after Pass 5 corrections** | **68** |

The seven preliminary IDs are preserved. The original Pass 4 checkpoint had
66 rows and added 59; Pass 5 adds the startup acknowledgement and custom pet
input surface, yielding 68 current rows. Guide has 17 main-window and nine editor controls plus ten Guide feedback
choices; two AHK launcher/client acknowledgements complete E. A single Guide
QAction is presented here and by the existing Knowledge button; final distinct
action and full-application presentation totals remain Pass 5 work. ACTION/BIND
records and implicit containers/events are excluded from these control rows.

**GUI_REGISTRY_PASS4_COMPLETE — READY_FOR_FINAL_AUDIT.** Fresh author-side
focused static validation: **PASS**. Checks cover 66 scoped control/presentation
rows, seven preserved preliminary IDs, factory/loop expansion, named actions and
handlers, Qt signals and AHK bindings, objectNames/labels, selected layout/state/
shortcut invariants, source/test identities, unique row IDs, Markdown/counts,
unchanged bytes outside this section and both AGENTS additions, exact three-path
candidate scope, empty index and git diff --check. Source inspection supplements
automated checks for semantic availability/focus/backend relationships.

The original audit FAIL is retained: ShortcutTarget was checked against the
caller instead of its included TopicRouting owner, and tuple/list JSON read-back
equality failed. The validator/owner reference were corrected with separate
failure/correction records before the successful execution; failure history is
not rewritten as success. No source correction or runtime retry occurred.

A–E subsection checkpoints and final static evidence are external. Runtime GUI,
AHK/hotkeys, Clipboard, database, PowerShell and full regression execution were
NOT RUN. Physical/native behavior and the explicitly listed source/test
limitations remain NOT VERIFIED. Pass 5 comprehensive consistency/coverage/
shortcut/presentation audit has not begun. Earlier Pass 1–3 checkpoint summaries
retain their historical remaining-work statements. No independent-review
request or Git integration is authorized.

<a id="gui-registry-clipboard"></a>

## Clipboard Center — Pass 3 source-verified inventory

Inspected integrated source: `62f95f185cd5abfefbfbc16822d12dc30144ed79`.
All entries inherit **Integrated / static inspection**; runtime/native tests
are **NOT RUN** here. The nine preliminary IDs are retained and expanded; five
rows are added. This section uses the existing control-counting convention:
one constructed interactive/data-view widget or transient confirmation choice
per row. Combo-box choices, stacked containers, passive labels, repeated history
rows, headers and native scrollbars/editor commands are not extra controls.
`—` for objectName means no source assignment; member names are source locators.
`—` for shortcut means no explicit custom binding, not absence of native input.

Test keys: **CW** = [workspace tests](../Tests/GUI/test_clipboard_workspace.py)
(safe table roles, loading/Retry, source switching, callback gaps, scroll and
keyboard); **CS** = [Setup GUI tests](../Tests/GUI/test_clipboard_setup.py)
(draft/pending/conflict, dynamic checkboxes, consent, source/shell guards and
accessible keyboard input); **CR** =
[Recent integration](../Tests/Integration/test_clipboard_recent_flow.py)
(bounded service/repository reads and composition); **CI** =
[Setup integration](../Tests/Integration/test_clipboard_setup_flow.py)
(revision-checked preferences, restart/database scope and history preservation).
These are inspected existing references, not fresh execution results.

### Workspace, Recent and unavailable Windows source

Owner: [clipboard_workspace.py](../Python/f7hub/gui/clipboard_workspace.py),
`ClipboardWorkspace.__init__`. The outer QVBoxLayout contains heading, Source
QHBoxLayout (label, selector, stretch), hidden-until-needed source feedback, then
`source_pages` (QStackedWidget, `clipboardSourcePages`, stretch 1). Its first
page is `f7hub_page` (`f7hubClipboardSourcePage`); second is `windows_page`
(`windowsClipboardSourcePage`). The workspace is `clipboardWorkspace`, accessible
Clipboard Center. These containers describe ownership, not extra tab controls.

With SettingsService supplied, the F7Hub page contains Recent/Clipboard Setup
navigation then `sections` (QStackedWidget: `recent_page`, then one retained
ClipboardSetup). Without SettingsService, no section buttons or Setup are
constructed and Recent content goes directly in the F7Hub page VBox. Recent's
VBox contains status, optional Refresh, candidate selection actions/count, table (stretch 1), then page summary.
Without ClipboardService, Refresh/table/model/summary are absent and the
truthful unavailable status remains; Setup can still exist independently.

| Stable ID | Label / member; widget; objectName | Logical position / parent | Signal or event → handler / backend | Availability / focus / accessibility | Shortcut | Tests |
|---|---|---|---|---|---|---|
| CLIPBOARD.SOURCE | F7Hub Clipboard / Windows Clipboard / `source_selector`; QComboBox; `clipboardSourceSelector` | Source row after Source: label; outside both source pages | activated(index) → `_source_activated` → `select_source(itemData(index))`; presentation only, no acquisition/service call | Always constructed; choices f7hub then windows, default f7hub; accessible Clipboard source with source-choice description; label buddy, no label mnemonic; transition refuses Recent loading or settings_pending and negotiates dirty Setup | Native combo input; no custom shortcut | CW, CS, CI |
| CLIPBOARD.RECENT | Recent / `recent_button`; QPushButton; — | F7Hub navigation row first, before Setup and stretch | clicked → `show_recent` → `confirm_leave` / `leave`; no automatic query from this handler | Only with SettingsService; source must be f7hub and Setup departure accepted; local button is not disabled for Recent reads; focuses Refresh when present; accessible Recent Clipboard history | — | CW, CS |
| CLIPBOARD.SETUP | Clipboard Setup / `setup_button`; QPushButton; — | Same navigation row second | clicked → `show_setup` → setup.reload; selects Setup only if accepted | Only with SettingsService and f7hub source; reload guards pending/dirty state; Recent loading remains independent; pending Copy Selected blocks section entry in the candidate; requests focus on Reload; accessible Clipboard Setup | — | CS, CI |
| CLIPBOARD.RECENT.REFRESH | Refresh / Retry / `refresh_button`; QPushButton; `clipboardRefreshButton` | Recent VBox below status, left-aligned, before table | clicked → `refresh` → own ServiceTaskRunner.submit(ClipboardService.get_recent); generation-bound `_recent_completed` → `_loaded` / `_failed` → `_finish` | Only with ClipboardService; handler requires f7hub and not loading; disabled during request; _finish restores enabled state and label/accessibility Refresh or Retry; one button, same handler | — | CW, CR |
| CLIPBOARD.RECENT.TABLE | `table`; QTableView; `clipboardRecentTable` | Recent after selection actions, before summary | CP02-S4 candidate: immutable safe rows plus CheckStateRole and accessible check state; setData updates transient Item/revision selection; no full text in model | Read-only text, NoSelection, no sorting; checking disabled during work; Select logical column is visually first | Space toggles current row once; native arrows, Tab escape and scroll | CW; selected-copy GUI/integration |
| CLIPBOARD.RECENT.SELECT_ALL | Select All Visible; QPushButton; `clipboardSelectAllVisibleButton` | Candidate selection row, first | clicked → model.select_all_visible → selection_changed | Loaded visible F7Hub rows only, max 100; disabled during work or when all checked | Tab/Space | selected-copy GUI |
| CLIPBOARD.RECENT.CLEAR | Clear Selection; QPushButton; `clipboardClearSelectionButton` | Candidate selection row, second | clicked → model.clear_checks | Transient only; disabled empty/pending | Tab/Space | selected-copy GUI |
| CLIPBOARD.RECENT.COPY_SELECTED | Copy Selected (N); QPushButton; `clipboardCopySelectedButton` | Candidate selection row, third, before passive `clipboardSelectedCount` label | clicked → copy_selected → own ServiceTaskRunner → ClipboardService.copy_selected → native delivery adapter → guarded completion | Positive count, F7Hub source, owner available and no pending work; all-or-nothing fresh authorization; generation-bound safe feedback | Tab/Space; no global hotkey | selected-copy GUI/integration/native |
| CLIPBOARD.WINDOWS.REFRESH | Refresh / `windows_refresh_button`; QPushButton; `windowsClipboardRefreshButton` | Windows page VBox after heading, unavailable message and help; before stretch | No connected handler; no native acquisition or snapshot backend | Always constructed, disabled; visible on Windows page; accessible Refresh Windows Clipboard; description says refresh unavailable | — | CW |

Historical CP02-S3 column snapshot: Time, Preview, Source App, Retention, Pinned.
CP02-S4 adds logical Select and moves it visually first, as described above.
Time displays explicit UTC, previews remain plain text with a truncation suffix
when indicated, Source App displays a permitted basename or Not recorded, retention displays Temporary/Saved and pinned displays Yes/No.
No raw text or tooltip is exposed by the model. The preview column stretches;
other widths are 230/170/105/70, headers cannot sort, the vertical header is hidden,
and word wrap is disabled. Native scrolling is not a separate history paging
contract. `has_more` adds feedback only: no Next/Previous or load-more control.

Recent uses its own [ServiceTaskRunner](../Python/f7hub/gui/service_task_runner.py),
separate from MainWindow's shared runner and Setup's runner. First accepted
`activate` while on f7hub calls `refresh` once; `_started` prevents repeated
navigation from re-reading. Refresh clears rows/summary before dispatch.
`loading` includes `_loading`, runner.busy and runner.completing; generation
checks reject obsolete success/failure. Completion does not force focus.
Success distinguishes populated/empty pages; errors use fixed safe feedback and
relabel the same button Retry without exposing exception details or previews.
The backend path is GUI →
[ClipboardService](../Python/f7hub/services/clipboard_service.py).get_recent
(default limit 50) →
[ClipboardRepository](../Python/f7hub/repositories/clipboard_repository.py) →
read-only SQLite first-page projection. It is durable F7Hub Recent, not RAM-01A
history or the current Windows Clipboard. No GUI SQL or native Clipboard read.

Source switching restores the committed combo index before modal guards, refuses
unknown keys, and treats the current source as a no-op. It preserves the retained
pages/model/runners and per-source shell-scroll positions. Cancel retains the
Setup section/draft and restores a usable remembered F7Hub child focus; accepted
departure ends that editing session, resets the section to Recent and focuses
the source selector. Scroll restoration is synchronous through the supplied
shell callbacks. Selecting either source does not itself dispatch Recent,
Settings or Windows acquisition. Source and section changes are different paths.

The explicit local Tab chain with sections is selector → Recent → Setup →
Refresh → table when those widgets exist; without sections, selector → Refresh
→ table. Setup has its separate chain below. `activation_focus_target` picks a
usable section control, falling back to the selector; Windows always proposes
the selector. Source-label buddy assignment has no `&` mnemonic. No custom
QShortcut, QAction or context menu is installed in these two Clipboard classes.
Physical focus traversal and platform mnemonic behavior are **NOT VERIFIED**.

### Clipboard Setup, preferences and unsaved-draft confirmation

Owner: [clipboard_setup.py](../Python/f7hub/gui/clipboard_setup.py), ClipboardSetup
(`clipboardSetup`, accessible Clipboard Setup). Its QVBoxLayout contains heading,
runtime and consent messages, then each checkbox followed by its explanatory
label; draft/status feedback follows; bottom action row is Apply, Cancel, Reload,
stretch, followed by outer stretch. The three checkbox instances come from the
ordered `fields` tuple, stored in `checkboxes[key]`; their objectNames are the
exact keys in [clipboard_settings.py](../Python/f7hub/domain/clipboard_settings.py).
All three definitions default false. Callback `lambda value, key=key:
self._edited(key, value)` captures the definition key per instance; value/key
are callback arguments, not handler names. `_present_values` blocks signals while
restoring values, so reading/reloading does not affirm workflow consent.

`E-editable` means a loaded snapshot with storage_available and not pending.
`pending` includes the local accepted-operation flag and its runner.busy; the
workspace's settings_pending additionally includes runner.completing. `_submit`
holds the local flag through completion presentation and generation checks.
Enabled state is local; ordinary parent-page state can also disable a control.

| Stable ID | Label / member; widget; objectName | Logical position / parent | Signal or event → handler / backend | Availability / accessibility / keyboard | Tests |
|---|---|---|---|---|---|
| CLIPBOARD.SETUP.WORKFLOW | &Enable Clipboard workflow and local history / `checkboxes[WORKFLOW_ENABLED]`; QCheckBox; `clipboard.workflow_enabled` | Setup first checkbox, below consent message, before its explanation | toggled(value) → `_edited(WORKFLOW_ENABLED, value)`; local draft, sets _affirmed on true; Apply owns any save/grant | E-editable; accessible Enable Clipboard workflow and local history; description discloses future eligible durable manual capture, 7-day TEMPORARY default, sensitivity-detection limits and no history deletion on disable; &E mnemonic / native Space | CS, CI |
| CLIPBOARD.SETUP.SOURCE.PROCESS | Store source &application executable name / `checkboxes[SOURCE_PROCESS_ENABLED]`; QCheckBox; `clipboard.source_process_persistence_enabled` | Second checkbox after workflow explanation, before its own explanation | toggled(value) → `_edited(SOURCE_PROCESS_ENABLED, value)`; Apply reads draft for Settings | E-editable independently of workflow value; accessible Store source application executable name; CP02-S3 description limits new eligible Win+Alt+C metadata to executable basename, excludes paths/command lines/titles, defaults off and preserves prior names when disabled; &a mnemonic / native Space | CS, CI |
| CLIPBOARD.SETUP.SOURCE.TITLE | Store source window &title / `checkboxes[SOURCE_TITLE_ENABLED]`; QCheckBox; `clipboard.source_window_title_persistence_enabled` | Third checkbox after process explanation, before its own explanation and draft/status labels | toggled(value) → `_edited(SOURCE_TITLE_ENABLED, value)`; Apply reads draft for Settings | E-editable independently of workflow/process values; accessible Store source window title; description warns titles may be sensitive and collection is independent; &t mnemonic / native Space | CS, CI |
| CLIPBOARD.SETUP.APPLY | &Apply / `apply_button`; QPushButton; — | Setup action QHBoxLayout first | clicked → `apply` → changed-key validation → `_submit`; ordinary SettingsService.apply or explicit ClipboardService.enable_history_from_setup; `_saved` handles committed result | E-editable plus _save_available and no conflict; no dirty-only enable gate; accessible Apply Clipboard preferences; no-change path avoids write; &A mnemonic | CS, CI |
| CLIPBOARD.SETUP.CANCEL | &Cancel / `cancel_button`; QPushButton; — | Action row second | clicked → `cancel` → restore latest loaded draft, clear _affirmed; no service call/write | Loaded snapshot and not pending, even when storage unavailable/conflicted; conflict remains until Reload; accessible Cancel Clipboard preference edits; &C mnemonic | CS, CI |
| CLIPBOARD.SETUP.RELOAD | &Reload / `reload_button`; QPushButton; — | Action row third, before stretch | clicked → `reload` → confirm_discard → `_submit`; ClipboardService.refresh_setup if supplied, otherwise SettingsService.refresh | Not pending; dirty draft needs Discard; reload never grants consent; accessible Reload Clipboard preferences; &R mnemonic | CS, CI |
| CLIPBOARD.SETUP.CONFIRM.DISCARD | Discard; QMessageBox standard button | Unsaved Clipboard preferences → native modal action area; source does not specify physical button order | `confirm_discard` compares question result to Discard, allowing the caller's departure/reload/close | Only when draft dirty and not pending; caller performs session reset or authoritative reload; no save/grant from confirmation | CS |
| CLIPBOARD.SETUP.CONFIRM.CANCEL | Cancel; QMessageBox standard button | Same modal action area | Any result other than Discard refuses the caller's transition and preserves draft | Explicit default Cancel; pending refuses before opening dialog; native dialog behavior, platform resolution NOT VERIFIED | CS |

The Setup Tab chain follows checkbox insertion order: workflow → process → title
→ Apply → Cancel → Reload. Source label mnemonic markers above are not new
global shortcuts. The process checkbox (&a) and Apply (&A) share the letter A
in source; platform dispatch/cycling for that mnemonic is **NOT VERIFIED**.
No default/auto-default QPushButton policy or custom shortcut is assigned here.

Settings are mediated by [SettingsService](../Python/f7hub/services/settings_service.py)
and [SettingsRepository](../Python/f7hub/repositories/settings_repository.py).
Setup receives the composed Clipboard owner only when its supports_setup property
is true. `refresh_setup` reads coherent preference/consent state; ordinary edits
use SettingsService.apply with the captured loaded revision. A deliberate
workflow affirmation plus Apply can call ClipboardService.enable_history_from_setup
with both revision and consent epoch; imported true values require deliberate
uncheck/recheck. The owner delegates the trusted Setup transaction through the
existing Settings service/repository. No-op Apply, Cancel and Reload do not grant.
Source-process/title preferences remain independent, and disabling workflow does
not delete existing history. Manual consent is not passive-monitoring authority.

Conflict preserves the draft and blocks Apply until Reload. Uncertain save says
it may have committed, disables saving and requires read-only reconciliation;
contention preserves a retryable draft, while persistence/unknown failure blocks
saving until reload. The saved baseline is accepted before rendering; notification
or presentation failure is reported separately from commit, preventing a replayed
write. Invalid/unavailable sensitive settings fail closed; Reload remains the
recovery route. `end_session` cancels local edits and advances generation only
when not pending. No content capture or native paste is dispatched by Setup.

Passive indicators are QLabels: workspace heading (`clipboardHeading`),
status/unavailable alias (`clipboardUnavailableMessage`), Source: label,
source_message, page_message, windows_heading, windows_unavailable_message
(`windowsClipboardUnavailableMessage`), windows_help; Setup heading,
runtime_message, consent_message, one explanation per checkbox, draft_message
and status_message. They use plain text and accessible feedback; they are not
additional actions. Windows says snapshot unavailable and retains a constructed
disabled Refresh. Setup runtime text still advertises unavailable Ctrl+Alt+C/V;
this wording is not a registered shortcut or evidence of acquisition capability.

### Clipboard-owned shell boundaries and implementation status

[MainWindow](../Python/f7hub/gui/main_window.py) owns the existing shared
clipboard_action (`clipboardCenterAction`, data clipboard.center) →
show_clipboard; its rail presentation is already SHELL.NAV.CLIPBOARD and is not
counted again here. show_clipboard guards shared/Ticket/Script pending work and
Ticket draft departure, constructs one retained ClipboardWorkspace with the exact
composed services and scroll callbacks, adds it to pages and calls activate.
Same-page activation preserves usable editor/rail focus; other accepted entry
uses activation_focus_target. `_leave_clipboard` negotiates Setup departure.
Explicit Exit's confirm_exit refuses Recent/settings pending work and negotiates
drafts; composed X-to-tray does not call that departure path and retains the
workspace. No shell/Tray control inventory is added by this pass.

Current native-action extension: Python/Qt owns the integrated Win+Alt+C route
and the isolated Win+Alt+V candidate through the same SelectionCapture lifecycle
and worker. ClipboardService remains the consent/privacy/source authority.
There is no Windows Clipboard history integration or additional Recent/Setup
control. The Win+Alt+V shortcut row below maps the candidate without claiming
it is on main.

Pinned audit record (2026-10-27; the native-action availability statement is
historical and superseded by the current extension):

Recent reads route through the existing Clipboard service/repository; Setup
preferences and consent route through their Settings/Clipboard owners. Qt event
routing creates no native reader. [Bootstrap](../Python/f7hub/app/bootstrap.py)
supplies the selected-database services. Integrated
[RAM-01A volatile history](../Python/f7hub/domain/clipboard_history.py) has no
automatic Windows observation or GUI wiring in these classes. RAM-01B passive
monitoring is not implemented, and Win+Alt+C HybridB-01 remains an unintegrated,
blocked development candidate, not an available control. There are no delivered
monitoring Enable/Pause/Resume/Clear/Save controls here. The
[RAM-01 successor contract](Planning/Clipboard/RAM01_Volatile_History_And_Promotion_Contract.md)
describes later native/history/explicit-promotion stages; it does not activate
them. Preserve the [1A manual-consent](Planning/Clipboard/1A_Clipboard_Domain_Data_Lifecycle.md),
[1B acquisition](Planning/Clipboard/1B_AHK_Python_Clipboard_Capture_IPC_Quick_HUD_Architecture.md)
and [1C presentation](Planning/Clipboard/1C_PySide6_Clipboard_Center.md) owners.

Documentation finding: historical CP-02/CC-01 descriptions in
[Python architecture](13_PythonArchitecture.md) describe an earlier read-only
ClipboardService/return-button stage. Current source and the later S05 owner
contract include Setup consent and omit the retired return button. Those dated
records remain unchanged; they are not current-control evidence or new authority.

### Pass 3 coverage and validation status — historical checkpoint

| Clipboard inventory group | Control rows |
|---|---:|
| Source selector and Recent/Setup navigation | 3 |
| Recent Refresh/Retry and read-only table | 2 |
| Constructed, disabled Windows Refresh | 1 |
| Setup preferences and Apply/Cancel/Reload | 6 |
| Unsaved-draft Discard/Cancel choices | 2 |
| **Clipboard total** | **14** |

All 14 rows are source-mapped: 12 widget instances and two confirmation choices.
The nine prior IDs are preserved; three checkbox IDs and two confirmation IDs
are new. Refresh/Retry and source combo choices are not double-counted. Passive
labels and stacked/page containers add no control rows.

**GUI_REGISTRY_PASS3_COMPLETE — READY_FOR_CONTINUATION.** Fresh author-side
focused static validation: **PASS**. Checks cover all 12 widget mappings, dynamic
definition keys/objectNames/labels and loop-captured callbacks, ten logical
control connections, the two confirmation choices, source/class/service APIs,
selected layout/Tab/state invariants, linked source/test/contract identities,
unique IDs, tables/counts, byte preservation outside this section and of both
AGENTS additions, exact three-path candidate scope, empty index and
`git diff --check`. Logical state/backend/focus semantics were also inspected
in source. These checks establish no runtime/native behavior; referenced tests
were inspected, not executed. No GUI runtime, Clipboard access, PowerShell,
database modification, native Windows test or full regression suite was run.
Physical focus/rendering, DPI and native mnemonic/default-button resolution
remain **NOT VERIFIED**, including the documented A/a mnemonic overlap.

Passes 1 and 2 below retain their dated completion/remaining-work snapshots.
The full application registry remains
INCOMPLETE: remaining work is Shell/Settings utilities, Tray, Mochi, Guide/AHK
and the final comprehensive action/presentation/shortcut audit. No independent
review readiness or Git integration eligibility is claimed.

## Pass 1 conventions and coverage

Pass 1 inspects Tickets and Knowledge Base at the source SHA above on
2026-10-26. The following tables inherit **Integrated / static inspection**;
runtime tests are **NOT RUN**. Each subsection names the exact source/class,
parent and test owners. A row's member name is a source locator, never an
invented objectName. ObjectName is `—` unless explicitly shown. Widget type,
label, relative position, container, event/handler, backend, state and keyboard
behavior are recorded per row or inherited from the subsection. Ordinary input
fields have no separate activation handler: the named submit handler reads them.
`—` in the shortcut column means no explicit custom shortcut; normal Qt input
and dialog behavior remains. Mnemonics are shown as source label `&` markers;
their native resolution has not been exercised here.

Count one row for each input, button, data view, splitter, tab target or transient
dialog choice. Repeated data rows, table headers, native editor context commands,
scrollbars and decorative labels are not separate controls. A tab target counts
once; its read-only editor is recorded in that row. Passive feedback labels are
listed below each group, outside these control counts. QAction identity is
separate from its presentations. Child dialogs are counted with the module that
opens them; TicketKnowledgeWidget belongs to Tickets. These rules apply to the
new Pass 1 tables; the earlier partial tables await the later audit.

<a id="gui-registry-tickets"></a>

## Tickets — queue and saved-ticket detail

Owner: [ticket_workspace.py](../Python/f7hub/gui/ticket_workspace.py),
`TicketWorkspace._build_ui`. MainWindow's Tickets page contains a QVBoxLayout
with a header, feedback and a horizontal QSplitter. The queue is its first
child; the second is `detail_stack` (QStackedWidget: detail, creation). The
detail panel is disabled until a ticket is loaded. `T-idle` means no runner
busy, note, creation, status or classification operation pending. Individual
handlers retain their own guards; enabled appearance alone does not prove an
operation will dispatch. Service reads/writes use ServiceTaskRunner and
[TicketService](../Python/f7hub/services/ticket_service.py) → TicketRepository
→ SQLite. TicketService owns validation, allowed status transitions, stale-edit
checks and transactional writes; GUI selections alone do not write.

Test keys: **TW** = [workspace flow](../Tests/Integration/test_ticket_workspace_flow.py),
**TC** = [workspace creation](../Tests/Integration/test_ticket_workspace_creation.py),
**TI** = [inline classification](../Tests/Integration/test_ticket_inline_classification.py),
**CO** = [company context](../Tests/Integration/test_ticket_company_context_flow.py),
**MW** = [main window](../Tests/GUI/test_main_window.py). These are inspected
existing test references, not fresh test outcomes. In particular TW covers
search/paging, note keyboard input, status failures and post-commit recovery;
TC covers creation/cancellation and callback gaps; TI covers field edits and
classification; MW covers queue traversal and compact layout reachability.

| Stable ID | Label / member; widget; objectName | Logical position / container and order | Event → handler / dependency | Availability / focus | Shortcut | Tests |
|---|---|---|---|---|---|---|
| TICKETS.NEW | + New Ticket / `new_ticket_button`; QPushButton; `newTicketButton` | Header QHBoxLayout, after recovery button | clicked → `begin_creation`; local mode change | T-idle, not creating, create widget supplied; accessible New Ticket; focuses Subject | — | TC, MW |
| TICKETS.RECOVER | Open created ticket / `retry_created_button`; QPushButton; — | Header, before New Ticket | clicked → `_open_created_ticket` → `open_ticket`; TicketService read | Hidden initially; shown for retained created identity; enabled T-idle and not creating | — | TC |
| TICKETS.SPLIT | Queue/detail divider; QSplitter; — | Below feedback; queue first, detail stack second; initial sizes 460/620 | Native splitter movement; presentation only | Native splitter behavior; screen geometry NOT VERIFIED | — | MW (compact layout; no direct drag assertion identified) |
| TICKETS.FILTER.STATUS | All statuses / `status_filter`; QComboBox; — | Queue `filters` QHBoxLayout, first | currentIndexChanged → `refresh_list(offset=0)` → `list_tickets` | Not runner busy; accessible Filter tickets by status | — | TW |
| TICKETS.REFRESH | Refresh / `refresh_button`; QPushButton; — | Same filter row, second | clicked lambda → `refresh_list` → `list_tickets` | No explicit button disabling; handler rejects busy/pending; preserves page/retry offset | — | TW, TC |
| TICKETS.FILTER.PRIORITY | All priorities / `priority_filter`; QComboBox; — | Queue QVBoxLayout, below status row | currentIndexChanged → `refresh_list(offset=0)` → `list_tickets` | Not runner busy; accessible Filter tickets by priority | — | TW |
| TICKETS.FILTER.TYPE | All types / `type_filter`; QComboBox; — | Below priority | currentIndexChanged → `refresh_list(offset=0)` → `list_tickets` | Not runner busy; accessible Filter tickets by type | — | TW |
| TICKETS.SEARCH.INPUT | Search subjects, descriptions and notes / `subject_search_input`; QLineEdit; — | Queue `search_row`, first, stretch 1 | returnPressed → `search_subjects` → `refresh_list` → `list_tickets` | Not runner busy; accessible name equals placeholder | Return | TW |
| TICKETS.SEARCH.SUBMIT | Search / `search_subjects_button`; QPushButton; — | Search row, second | clicked → `search_subjects`; same path as input | Not runner busy | — | TW |
| TICKETS.SEARCH.CLEAR | Clear / `clear_subject_search_button`; QPushButton; — | Search row, third | clicked → `clear_subject_search` → `refresh_list(offset=0)` | Not runner busy | — | TW |
| TICKETS.NUMBER.INPUT | Ticket number / `ticket_number_input`; QLineEdit; — | Queue `number_row`, first, stretch 1 | returnPressed → `open_ticket_by_number` → `get_ticket_details_by_number` | Not runner busy; accessible Open saved ticket by number | Return | TW |
| TICKETS.NUMBER.OPEN | Open number / `open_number_button`; QPushButton; — | Number row, second | clicked → `open_ticket_by_number`; same read as input | Not runner busy; handler also guards mode/pending and drafts | — | TW |
| TICKETS.QUEUE | `table`; QTableView; — | Queue below number row | activated → `_activate_row` → `open_ticket` → `get_ticket_details` | Single read-only row selection; accessible Tickets; activate a row to open; Tab leaves table | Native row activation | TW, MW |
| TICKETS.QUEUE.OPEN | Open selected ticket / local `open_button`; QPushButton; — | Queue below table | clicked lambda → `_activate_row(currentIndex)` | No explicit enable condition; invalid selection is ignored | — | TW, MW |
| TICKETS.PAGE.PREVIOUS | Previous / `previous_button`; QPushButton; — | Bottom `pages` QHBoxLayout, before page label | clicked → `refresh_list(offset - PAGE_SIZE)` | Initially disabled; successful read enables if offset > 0; handler guards pending | — | TW |
| TICKETS.PAGE.NEXT | Next / `next_button`; QPushButton; — | Bottom page row, after page label | clicked → `refresh_list(offset + PAGE_SIZE)` | Initially disabled; successful read enables if more than PAGE_SIZE results | — | TW |
| TICKETS.TAB.DETAILS | Details / `summary`; QTextEdit | Detail `tabs` QTabWidget, first tab | Native tab change; `_display_details` presents TicketService result | Read-only, plain text; detail parent enabled only after load | — | TW |
| TICKETS.TAB.NOTES | Notes / `notes_history`; QTextEdit | Detail tabs, second | Native tab change; `_display_details` | Read-only plain text | — | TW |
| TICKETS.TAB.HISTORY | History & timeline / `timeline`; QTextEdit | Detail tabs, third | Native tab change; `_display_details` | Read-only plain text | — | TW |
| TICKETS.TAB.KNOWLEDGE | Knowledge / `knowledge_tab`; TicketKnowledgeWidget | Detail tabs, fourth | Native tab change; knowledge_article_requested relays to workspace signal; child mappings below | Detail parent gate; child service/selection gates | — | TK |
| TICKETS.TAB.COMPANY | Company / local `company_tab`; QWidget | Detail tabs, fifth | Native tab change; controls below | Detail parent gate | — | CO |
| TICKETS.COMPANY.LOAD | Load recent tickets / `company_load_button`; QPushButton | Company tab QVBoxLayout, after heading/feedback | clicked → `load_company_tickets` → `list_tickets(company_id, limit=20, offset=0)` | Not runner busy, retained non-null company context; handler also guards mode/pending | — | CO |
| TICKETS.COMPANY.TABLE | `company_table`; QTableView | Company tab, below Load | activated → `_activate_company_row` → `open_ticket`; currentChanged → `_set_company_controls_idle` | Single read-only row selection; accessible Recent tickets for this company | Native row activation | CO |
| TICKETS.COMPANY.OPEN | Open selected ticket / `company_open_button`; QPushButton | Company tab, below table | clicked lambda → `_activate_company_row(currentIndex)` | Not runner busy and valid current index | — | CO |
| TICKETS.AUTHOR | Your name (optional) / `author_input`; QLineEdit | Detail QVBoxLayout, immediately below tabs | Read by `add_note` and `change_status` → TicketService | Loaded ticket, not creating, T-idle; accessible Activity author | — | TW |
| TICKETS.NOTE.TYPE | `note_type`; QComboBox | Quick Note QHBoxLayout, after label, before stretch | Read by `add_note` → `add_note` service | Same note gate; default INTERNAL; accessible Note type | — | TW |
| TICKETS.NOTE.ADD | Add note / `add_note_button`; QPushButton | Quick Note row, after stretch | clicked → `add_note` → TicketService.add_note | Note gate plus nonblank note; tooltip documents shortcut | Ctrl+Enter in editor also calls handler | TW, MW |
| TICKETS.NOTE.INPUT | Add a support note… / `note_input`; QTextEdit | Below Quick Note row | textChanged → `_update_note_controls`; eventFilter → `add_note` | Plain text; note gate; accessible New note; focus restored after owned completion; Escape consumed | Ctrl+Return/Enter with no other modifier, no auto-repeat | TW |
| TICKETS.STATUS.SELECT | Change status / `status_input`; QComboBox | Detail QFormLayout, first row | currentIndexChanged → resolution visibility; read by `change_status` | Loaded-ticket parent gate; choices from `allowed_statuses`; accessible New ticket status | — | TW |
| TICKETS.STATUS.REASON | Reason / `reason_input`; QLineEdit | Same form, second row | Read by `change_status` | Loaded-ticket parent gate; accessible Status change reason | — | TW |
| TICKETS.STATUS.RESOLUTION | Resolution summary / `resolution_input`; QTextEdit | Below status form | Read by `change_status` for RESOLVED | Plain text; visible only for RESOLVED; accessible Resolution summary | — | TW |
| TICKETS.STATUS.APPLY | Apply status / `change_status_button`; QPushButton | Below resolution | clicked → `change_status` → TicketService.change_status | Enabled when status count > 1 at detail load; handler rejects mode/pending/busy | — | TW, TC |
| TICKETS.CLASSIFY.PRIORITY | Priority / `priority_input`; QComboBox | `properties` QHBoxLayout, before Type | currentIndexChanged → `_update_classification_controls`; read by `apply_classification` | Loaded, T-idle, not creating, no edit dialog; accessible Ticket priority | — | TI |
| TICKETS.CLASSIFY.TYPE | Type / `type_input`; QComboBox | Properties row, after Priority | currentIndexChanged → `_update_classification_controls`; read by `apply_classification` | Same classification gate; accessible Ticket type | — | TI |
| TICKETS.CLASSIFY.APPLY | Apply changes / `apply_properties_button`; QPushButton | Properties row, last | clicked → `apply_classification` → `update_ticket_classification` | Classification gate plus dirty baseline; accessible Apply ticket changes | — | TI |
| TICKETS.EDIT.SUBJECT | Edit subject / `edit_subject_button`; QPushButton | Bottom `detail_actions` QHBoxLayout, first | clicked → `open_edit_subject`; dialog below | Parent gate; handler requires T-idle and no other edit dialog | — | TI, TW |
| TICKETS.EDIT.DESCRIPTION | Edit description / `edit_description_button`; QPushButton | Detail action row, second | clicked → `open_edit_description`; dialog below | Same handler guard as subject | — | TI, TW |
| TICKETS.RELOAD | Reload ticket / `reload_button`; QPushButton | Detail action row, third | clicked lambda → `open_ticket(current id)` → `get_ticket_details` | Parent gate; normal read/pending/discard guards apply | — | TI, TW |
| TICKETS.CREATE.CANCEL | Cancel / `cancel_create_button`; QPushButton | Creation panel QVBoxLayout, below scroll area holding creation widget | clicked → `cancel_creation`; local reset and previous detail restore | Creation panel visible; T-idle; accessible Cancel New Ticket | — | TC |
| TICKETS.CONFIRM.CREATE.DISCARD | Discard; QMessageBox standard button | Unsaved new ticket dialog in `cancel_creation` | Question result Discard → reset form and leave creation | Only when a creation draft exists; Cancel is default | — | TC |
| TICKETS.CONFIRM.CREATE.CANCEL | Cancel; QMessageBox standard button | Same confirmation | Question result Cancel → retain draft | Default; native dialog dismissal | Native dialog Cancel | TC |
| TICKETS.CONFIRM.ACTIVITY.DISCARD | Discard; QMessageBox standard button | Unsaved ticket activity dialog in `confirm_discard` | Question result Discard → caller may navigate/reload | Draft predicate includes note, status, reason, resolution, classification; pending note/classification refuses | — | TI, TW |
| TICKETS.CONFIRM.ACTIVITY.CANCEL | Cancel; QMessageBox standard button | Same confirmation | Question result Cancel → caller preserves current context | Default | Native dialog Cancel | TI, TW |

Passive indicators: `workspace_heading`, `feedback`, `page_label`, detail
`heading`, `company_heading`, `company_feedback`, and the Quick Note/Priority/
Type labels are QLabels. They present mode, read/write/recovery outcome and
selection context; they are not extra activation actions. Layout positions above
follow source insertion order; native pixel rendering/DPI is NOT VERIFIED.

### Ticket creation form and quick reference dialogs

Owner: [ticket_create_widget.py](../Python/f7hub/gui/ticket_create_widget.py),
`TicketCreateWidget._build_ui`, objectName `ticketCreateWidget`; hosted inside
the creation panel's resizable QScrollArea. Unless shown otherwise, fields are
read by `submit` → TicketService.create_ticket. In MainWindow it runs through
ServiceTaskRunner; the standalone widget also has a synchronous fallback.
The form has a QFormLayout, then an action QHBoxLayout with status/stretch/Create.
`StandardKey.Save` is scoped to WidgetWithChildrenShortcut → `submit`; actual
platform key resolution is NOT VERIFIED here. No explicit Tab order is set in
this form. Creation entry focuses Subject; failures preserve input and target
the invalid field.

**TF** = [creation widget tests](../Tests/GUI/test_ticket_create_widget.py),
**TR** = [reference widget tests](../Tests/GUI/test_ticket_reference_widget.py),
**QC** = [quick company tests](../Tests/GUI/test_quick_company_dialog.py),
**QN** = [quick contact tests](../Tests/GUI/test_quick_contact_dialog.py).
TicketReferenceService → CompanyRepository / ContactRepository /
CategoryRepository supplies choices; CompanyService and ContactService own
quick creation through their respective repositories. No GUI SQL is involved.

| Stable ID | Label / member; widget; objectName | Position / container | Event → handler / backend | Availability / accessibility | Shortcut | Tests |
|---|---|---|---|---|---|---|
| TICKETS.CREATE.NUMBER | Ticket number / `ticket_number_input`; QLineEdit; `ticketNumberInput` | Form row 1 | Read by `submit` | Optional; blank generates number; accessible Ticket number | Save action reads field | TF |
| TICKETS.CREATE.SUBJECT | Subject * / `subject_input`; QLineEdit; `ticketSubjectInput` | Form after number error row | Read by `submit` | Required; accessible Subject, required | Save action reads field | TF, TC |
| TICKETS.CREATE.TYPE | Type / `ticket_type_input`; QComboBox; `ticketTypeInput` | Below subject error | Read by `submit` | Incident default; accessible Ticket type | — | TF |
| TICKETS.CREATE.PRIORITY | Priority / `priority_input`; QComboBox; `ticketPriorityInput` | Below Type | Read by `submit` | Medium default; accessible Priority | — | TF |
| TICKETS.CREATE.COMPANY | Company / `company_input`; QComboBox; `ticketCompanyInput` | Company form row, first, stretch 1 | currentIndexChanged → `_company_changed` → `_load_contacts`; submit reads id | Not busy and no pending contact; Not selected allowed; accessible Company | — | TR, QC, QN |
| TICKETS.CREATE.COMPANY.ADD | Add Company / `add_company_button`; QPushButton; `addCompanyButton` | Company row, second | clicked → `open_company_dialog` | Visible with company/reference services and runner; disabled busy/pending contact/company | — | QC |
| TICKETS.CREATE.CONTACT | Contact / `contact_input`; QComboBox; `ticketContactInput` | Contact row, first, stretch 1 | Submit reads id; `_load_contacts` updates choices | Async company-dependent loading; disabled while loading/no available contacts; accessible Contact | — | TR, QN |
| TICKETS.CREATE.CONTACT.ADD | Add Contact / `add_contact_button`; QPushButton; `addContactButton` | Contact row, second | clicked → `open_contact_dialog` | Visible with contact/reference services and runner; enabled valid company id, idle and no pending recovery | — | QN |
| TICKETS.CREATE.REFERENCES | Refresh references / `refresh_references_button`; QPushButton | Below Contact in `reference_actions` QHBoxLayout, first | clicked → `refresh_references` → category/company/contact reference reads | Visible with reference service; handlers guard runner; preserves drafts | — | TR, QC, QN |
| TICKETS.CREATE.CONTACT.ABANDON | Continue without this contact / `abandon_contact_button`; QPushButton; `abandonPendingContactButton` | Reference actions, second | clicked → `abandon_pending_contact`; local recovery release | Only visible for pending contact with unavailable company; not runner busy | — | QN |
| TICKETS.CREATE.CATEGORY | Category / `category_input`; QComboBox; `ticketCategoryInput` | Form below reference actions | Submit reads id | Optional, Not selected; accessible Category | — | TF, TR |
| TICKETS.CREATE.CATEGORY.REFRESH | Refresh categories / `refresh_categories_button`; QPushButton | Category feedback row, after stretchable feedback | clicked → `refresh_categories` → `list_active_ticket_categories` | Visible with reference service; guard prevents busy dispatch | — | TR |
| TICKETS.CREATE.DESCRIPTION | Description / `description_input`; QTextEdit; `ticketDescriptionInput` | Last form field | Submit reads plain text | Rich text disabled; accessible Description | — | TF |
| TICKETS.CREATE.SAVE | Create Ticket / `save_button`; QPushButton; `createTicketButton` | Bottom action row, after stretch | clicked / Save shortcut → `submit` → create_ticket; emits ticket_created | Default button; disabled submitting; handler rejects busy/pending reference recovery/blank subject | StandardKey.Save | TF, TC, MW |

Passive creation labels: heading `ticketCreateHeading`, `ticketNumberError`,
`ticketSubjectError`, `ticketFormError`, `ticketStatusLabel`,
`reference_feedback`, `category_feedback` and generated form labels. Validation
and recovery feedback does not constitute another save operation.

Quick dialogs are parented to TicketCreateWidget. Each uses QFormLayout then
feedback then a QHBoxLayout with stretch, Cancel, default Create. No objectNames
are assigned. While submitting, fields and buttons are disabled and reject/X
is refused. Names are required; failures preserve input and focus Name. Creating
a company/contact does not itself create a ticket; committed reference-refresh
recovery is retained by the form.

| Stable ID | Owner/source | Label / member; widget | Position | Event → handler / backend | Shortcut / state | Tests |
|---|---|---|---|---|---|---|
| TICKETS.COMPANY.NEW.NAME | [QuickCompanyDialog](../Python/f7hub/gui/quick_company_dialog.py) | Company &name * / `name_input`; QLineEdit | Only form field | `submit` reads name → CompanyService.create_company | Label mnemonic; accessible Company name, required; disabled submitting | QC |
| TICKETS.COMPANY.NEW.CANCEL | QuickCompanyDialog | Cancel / `cancel_button`; QPushButton | Action row, first button | clicked → `reject` | Not auto-default; blocked submitting | QC |
| TICKETS.COMPANY.NEW.SAVE | QuickCompanyDialog | Create Company / `create_button`; QPushButton | Action row, second | clicked → `submit` | Default/Enter; handler guards submitted/created/busy | QC |
| TICKETS.CONTACT.NEW.NAME | [QuickContactDialog](../Python/f7hub/gui/quick_contact_dialog.py) | Contact &name * / `name_input`; QLineEdit | Form first | `submit` → ContactService.create_contact(company_id, display_name, email) | Label mnemonic; accessible Contact name, required | QN |
| TICKETS.CONTACT.NEW.EMAIL | QuickContactDialog | &Email / `email_input`; QLineEdit | Form second | Read by `submit` | Label mnemonic; accessible Email, optional | QN |
| TICKETS.CONTACT.NEW.CANCEL | QuickContactDialog | Cancel / `cancel_button`; QPushButton | Action row, first button | clicked → `reject` | Blocked submitting | QN |
| TICKETS.CONTACT.NEW.SAVE | QuickContactDialog | Create Contact / `create_button`; QPushButton | Action row, second | clicked → `submit` | Default/Enter; guards submitted/created/busy | QN |

### Ticket subject and description editors

Owners: [EditTicketSubjectDialog](../Python/f7hub/gui/edit_ticket_subject_dialog.py)
and [EditTicketDescriptionDialog](../Python/f7hub/gui/edit_ticket_description_dialog.py),
opened modelessly by TicketWorkspace. Each form shows ticket number then the
editable field, feedback, and stretch/Cancel/Save QHBoxLayout. No objectNames
are assigned. Fields/Cancel are disabled submitting; Save additionally remains
disabled after a conflict or successful save. Reject and X are refused during
submission. Saves use ServiceTaskRunner → TicketService → TicketRepository,
with expected content/timestamp guards. Successful signals return to the owning
workspace for read-only reload. Test owner TI covers dialog completion,
classification blocking, cancellation and failed saves; TW covers edited search
results. No separate custom save shortcut is installed.

| Stable ID | Owner | Label / member; widget | Event → handler / backend | Focus / keyboard | Tests |
|---|---|---|---|---|---|
| TICKETS.SUBJECT.INPUT | EditTicketSubjectDialog | &Subject * / `subject_input`; QLineEdit | Read by `submit` → update_ticket_subject | Accessible Ticket subject, required; label mnemonic; refocused on failure | TI, TW |
| TICKETS.SUBJECT.CANCEL | EditTicketSubjectDialog | Cancel / `cancel_button`; QPushButton | clicked → `reject` | Not auto-default | TI |
| TICKETS.SUBJECT.SAVE | EditTicketSubjectDialog | Save subject / `save_button`; QPushButton | clicked → `submit` → update_ticket_subject | Default/Enter | TI, TW |
| TICKETS.DESCRIPTION.INPUT | EditTicketDescriptionDialog | &Description / `description_input`; QPlainTextEdit | Read by `submit` → update_ticket_description | Accessible Ticket description, optional; label mnemonic; refocused on failure | TI, TW |
| TICKETS.DESCRIPTION.CANCEL | EditTicketDescriptionDialog | Cancel / `cancel_button`; QPushButton | clicked → `reject` | Not auto-default | TI |
| TICKETS.DESCRIPTION.SAVE | EditTicketDescriptionDialog | Save description / `save_button`; QPushButton | clicked → `submit` → update_ticket_description | Default button; multiline input keeps native editing | TI, TW |

### Ticket Knowledge links and selector

Owner: [ticket_knowledge_widget.py](../Python/f7hub/gui/ticket_knowledge_widget.py),
`TicketKnowledgeWidget`, its `LinkArticleDialog` and `_ArticleIdentityTable`.
No objectNames are assigned. **TK** =
[ticket Knowledge GUI tests](../Tests/GUI/test_ticket_knowledge_widget.py),
including candidate retry, confirmation safety, selection identity, pending
writes and stale contexts. **TKI** =
[link integration tests](../Tests/Integration/test_ticket_knowledge_flow.py).
ServiceTaskRunner → TicketKnowledgeService → TicketKnowledgeRepository → SQLite
owns list/link/unlink; opening an article emits knowledge_article_requested →
TicketWorkspace signal → MainWindow.open_knowledge_article →
KnowledgeWorkspace.open_article_by_id, subject to shell pending/discard guards.

| Stable ID | Parent / label / member; widget | Logical layout position | Event → handler / service method | State / focus / shortcut | Tests |
|---|---|---|---|---|---|
| TICKETS.KNOWLEDGE.TABLE | Knowledge tab / `table`; _ArticleIdentityTable (QTableView) | VBox below Linked articles heading | selectionChanged → `_update_controls` | Single read-only row; accessible Linked knowledge articles; native selection; — | TK, TKI |
| TICKETS.KNOWLEDGE.LINK | Knowledge tab / Link Article / `link_button`; QPushButton | Bottom actions QHBoxLayout, first | clicked → `open_link_dialog` | Loaded ticket, service, not runner busy or confirming unlink | TK |
| TICKETS.KNOWLEDGE.OPEN | Knowledge tab / Open Article / `open_button`; QPushButton | Actions second | clicked → `open_selected_article` → request signal | Same gate plus selected article id | TK |
| TICKETS.KNOWLEDGE.UNLINK | Knowledge tab / Unlink Article / `unlink_button`; QPushButton | Actions third | clicked → `unlink_selected_article` → confirmation → unlink_related_article | Same gate plus selection; rechecks context after modal loop | TK, TKI |
| TICKETS.KNOWLEDGE.REFRESH | Knowledge tab / Refresh / `refresh_button`; QPushButton | Actions after stretch, last | clicked lambda → `refresh_links` → list_linked_articles | Loaded ticket, service, idle, not confirming | TK |
| TICKETS.KNOWLEDGE.SELECT.TABLE | Link Knowledge Article dialog / `table`; _ArticleIdentityTable | VBox first, before feedback | selectionChanged → `_update_link_button` | Accessible Existing knowledge articles available to link; disabled submitting | TK |
| TICKETS.KNOWLEDGE.SELECT.RETRY | Selector / Retry loading articles / `retry_button`; QPushButton | Actions first, before stretch | clicked → `load_candidates` → list_link_candidates | Hidden until load failure; handler guards busy/dismissed/completed | TK |
| TICKETS.KNOWLEDGE.SELECT.CANCEL | Selector / Cancel / `cancel_button`; QPushButton | After stretch | clicked → `reject` | Not auto-default; disabled submitting; dismissal ignores late read | TK |
| TICKETS.KNOWLEDGE.SELECT.LINK | Selector / Link Article / `link_button`; QPushButton | Actions last | clicked → `submit` → link_related_article | Idle, selected id, not submitting/completed; handler also guards dismissed | TK, TKI |
| TICKETS.KNOWLEDGE.CONFIRM.UNLINK | Unlink Article QMessageBox / Unlink; destructive-role button | Modal confirmation | clicked result → `_confirm_unlink` returns true | Exact retained selection/context rechecked before dispatch | TK |
| TICKETS.KNOWLEDGE.CONFIRM.CANCEL | Same dialog / Cancel; standard button | Modal confirmation | clicked result → no unlink | Explicit default and Escape button; Enter cancels | TK |

Both article tables reuse the same identity-view class, not duplicate link
implementations. Their selection callbacks update action state; no separate row
activation shortcut opens an article. Feedback labels report loading, safe
failure and saved outcomes. No custom context-menu actions are defined in the
inspected Tickets classes; native Qt text-edit menus are inherited behavior.

<a id="gui-registry-knowledge"></a>

## Knowledge Base — workspace

Owner: [knowledge_workspace.py](../Python/f7hub/gui/knowledge_workspace.py),
`KnowledgeWorkspace.__init__`, hosted as MainWindow's Knowledge page. Its
QVBoxLayout contains top actions, search, filters, feedback labels, then a
horizontal QSplitter (list first, article detail second, initial 420/620).
`K-idle` means `_update_actions`' effective busy flag is false: no shared runner
busy, tag-filter dialog, manual filter refresh, publish/archive confirmation,
category dialog or tags dialog. MainWindow's page enable state also applies.
Filter loading has additional independent runners and gates described below.
All rows inherit objectName `—` unless specified. Native widget focus/input is
retained; explicit custom focus policies are listed where set.

Backend: ServiceTaskRunner →
[KnowledgeService](../Python/f7hub/services/knowledge_service.py) →
KnowledgeRepository → SQLite for articles, versions, search and guarded writes.
CategoryRepository supplies active KNOWLEDGE categories; TagRepository supplies
available/article tags. KnowledgeService owns validation and delegates guarded
draft category/tag writes to KnowledgeRepository. Category/tag filter option
reads have separate ServiceTaskRunners; selection changes remain presentation
state until an explicit operation accepts the values.

Test keys: **KW** = [workspace tests](../Tests/GUI/test_knowledge_workspace.py),
**KF-C** = [category filter](../Tests/GUI/test_knowledge_category_filter.py),
**KF-S** = [status filter](../Tests/GUI/test_knowledge_status_filter.py),
**KF-T** = [tag filter](../Tests/GUI/test_knowledge_tag_filter.py),
**GR** = [Guide relocation](../Tests/GUI/test_guide_relocation.py),
**KI** = [Knowledge flow](../Tests/Integration/test_knowledge_base_flow.py).
KW includes actual input/selection assertions for search, guarded publication,
editor drafts/conflicts and history; the filter suites cover composition,
cached choices and retry. References identify coverage to inspect, not freshly
executed results.

| Stable ID | Label / member; widget; objectName if assigned | Logical position / container | Event → handler / dependency | Availability / focus | Shortcut | Tests |
|---|---|---|---|---|---|---|
| KNOWLEDGE.GUIDE | Guide / `guide_button`; QToolButton; `knowledgeGuideButton` | Top QHBoxLayout after heading, before stretch | setDefaultAction(guide_action); shared MainWindow.altf7hub_action.triggered → show_altf7hub → ServiceTaskRunner → AltF7HubService.show_guide | Disabled if no supplied action; otherwise action state, shell busy/service gate; accessible Guide, StrongFocus | No custom binding assigned to button | GR |
| KNOWLEDGE.NEW | New Article / `new_button`; QPushButton | Top after stretch, first action | clicked → `open_new_article` | K-idle; opens NewArticleDialog | — | KW, KI |
| KNOWLEDGE.EDIT | Edit Article / `edit_button`; QPushButton | Top second action | clicked → `open_edit_article` | K-idle and loaded DRAFT; opens EditArticleDialog | — | KW, KI |
| KNOWLEDGE.PUBLISH | Publish / `publish_button`; QPushButton | Top third action | clicked → `publish_article` → confirmation → KnowledgeService.publish_article | Service, K-idle, loaded DRAFT; rechecks article identity after confirmation | — | KW |
| KNOWLEDGE.ARCHIVE | Archive / `archive_button`; QPushButton | Top fourth action | clicked → `archive_article` → confirmation → KnowledgeService.archive_article | Service, K-idle, loaded PUBLISHED; rechecks article identity | — | KW |
| KNOWLEDGE.HISTORY | Version History / `version_history_button`; QPushButton | Top fifth action, last | clicked → `open_version_history` | Service, K-idle, any loaded article status | — | KW |
| KNOWLEDGE.SEARCH.INPUT | Search current articles / `search_input`; QLineEdit | Search QHBoxLayout first, stretch 1 | returnPressed → `search_articles` → search_articles service; textChanged → `_search_text_changed` updates actions | K-idle; accessible Search current knowledge articles | Return | KW, KF-C, KF-S, KF-T |
| KNOWLEDGE.SEARCH.SUBMIT | Search / `search_button`; QPushButton | Search row second | clicked → `search_articles`; same search as Return | K-idle; blank query clears search | — | KW |
| KNOWLEDGE.SEARCH.CLEAR | Clear Search / `clear_search_button`; QPushButton | Search row third | clicked → `clear_search` → refresh_list → list_articles | K-idle and active search or nonempty input; retains filters | — | KW, KF-C, KF-S, KF-T |
| KNOWLEDGE.FILTER.CATEGORY | Category: / `category_filter`; QComboBox | Filter QHBoxLayout, first selector | currentIndexChanged → `_filter_changed` → list/search with category args | K-idle, options ready, category runner idle; accessible Filter knowledge articles by category; All categories / Not selected / active choices | — | KF-C |
| KNOWLEDGE.FILTER.STATUS | Status: / `status_filter`; QComboBox | Filter row second selector | currentIndexChanged → `_filter_changed` → list/search with status | K-idle; All statuses / Draft / Published / Archived; accessible Filter knowledge articles by status | — | KF-S |
| KNOWLEDGE.FILTER.TAG | Tag: / `tag_filter`; QComboBox | Filter row third selector | currentIndexChanged → `_tag_filter_changed` → `_filter_changed` or open_tag_filter | K-idle, options ready, tag runner idle; All tags / Untagged / existing tags / multi-tag selector; accessible Filter knowledge articles by tag | — | KF-T |
| KNOWLEDGE.FILTER.REFRESH | Refresh filters / `refresh_filters_button`; QToolButton | Filter row last | clicked → `refresh_filter_options` → list_active_knowledge_categories and list_available_tags; reconciles results when needed | Service, K-idle, not filter_loading; accessible Refresh knowledge filter choices; StrongFocus | — | KF-C, KF-T |
| KNOWLEDGE.ARTICLES | `table`; QTableView | Splitter first child → list_panel QVBoxLayout, before empty state | selectionChanged → `_selection_changed` → open_article → get_article | K-idle; single read-only row; accessible Knowledge articles; select a row to read | Native row selection | KW, KI |
| KNOWLEDGE.SPLIT | List/detail divider; QSplitter | Below feedback, horizontal | Native splitter movement; presentation only | Pixel geometry NOT VERIFIED | — | KF-S (layout; no direct drag assertion identified) |
| KNOWLEDGE.CATEGORY | Category… / `category_button`; QPushButton | Detail VBox category row QHBoxLayout, after stretchable category QLabel | clicked → `open_category` | Service, K-idle, loaded DRAFT | — | KA-C |
| KNOWLEDGE.TAGS | Tags… / `tags_button`; QPushButton | Detail VBox tags row, after stretchable tags QLabel | clicked → `open_tags` | Service, K-idle, loaded DRAFT | — | KA-T |
| KNOWLEDGE.BODY | `detail_body`; QPlainTextEdit | Detail VBox last, below summary, stretch 1 | `_show_article` sets plain text from authoritative loaded article | Read-only; accessible Knowledge article body, read only; no execution/rendered Markdown action | Native text selection/copy | KW |
| KNOWLEDGE.CONFIRM.PUBLISH.ACCEPT | Publish; QMessageBox AcceptRole button | Publish Article modal confirmation | Result compared by `_confirm_publish`; accepted retained token dispatched by publish_article | DRAFT only; preserves content/version history | — | KW |
| KNOWLEDGE.CONFIRM.PUBLISH.CANCEL | Cancel; QMessageBox standard button | Same confirmation | Result → no publish | Explicit default and Escape button | Enter/Escape cancel | KW |
| KNOWLEDGE.CONFIRM.ARCHIVE.ACCEPT | Archive; QMessageBox AcceptRole button | Archive Article modal confirmation | Result compared by `_confirm_archive`; retained token dispatched by archive_article | PUBLISHED only; preserves content/history/relationships; no Unarchive control | — | KW |
| KNOWLEDGE.CONFIRM.ARCHIVE.CANCEL | Cancel; QMessageBox standard button | Same confirmation | Result → no archive | Explicit default and Escape button | Enter/Escape cancel | KW |

The Guide button and utility submenu present one QAction; they do not duplicate
the Guide implementation. This pass traces the F7Hub-owned entry point only;
the delegated AHK host/editor and native launch/focus acceptance remain outside
Pass 1. No AltF7Hub configuration content was accessed for this mapping.

Passive Knowledge indicators are QLabels: heading `knowledgeHeading`,
`filter_feedback`, `tag_filter_feedback`, `feedback`, `empty_state`, then detail
metadata in order `detail_code` (objectName `articleCode`), `detail_title`,
`detail_status`, `detail_version`, `detail_dates`, `detail_category`,
`detail_tags`, `detail_summary`. The date label uses the current article's
created/updated timestamps. Labels are plain text; metadata and body clear when
selection is unavailable. These labels do not add separate action counts.

### New Article and Edit Article dialogs

Owners: [NewArticleDialog](../Python/f7hub/gui/new_article_dialog.py) and
[EditArticleDialog](../Python/f7hub/gui/edit_article_dialog.py), parented to
KnowledgeWorkspace and opened modelessly. No objectNames are assigned. Each
QVBoxLayout contains a QFormLayout, feedback, then stretch/Cancel/default Save
in a QHBoxLayout. All editable fields and Cancel are disabled submitting;
reject/X is blocked during a write. Edit Save is additionally disabled after
conflict/success. No explicit custom QShortcut is installed. Labels use the
source mnemonic markers below; bodies preserve native multiline editing.
Backend writes use ServiceTaskRunner → KnowledgeService; success signals
article_created/article_updated return to KnowledgeWorkspace._article_created
for authoritative list/detail refresh. Test owner KW covers fields, cancellation,
duplicate dispatch, failures, stale versions and successful revisions; KI covers
the integrated Knowledge workflow.

| Stable ID | Owner / label / member; widget | Form or action position | Event → handler / service | Focus / shortcut | Tests |
|---|---|---|---|---|---|
| KNOWLEDGE.NEW.CODE | NewArticleDialog / Article &code * / `code_input`; QLineEdit | Form first | submit reads → create_article | Accessible Article code, required; KB0001 placeholder; label mnemonic | KW |
| KNOWLEDGE.NEW.TITLE | NewArticleDialog / &Title * / `title_input`; QLineEdit | Form second | submit reads → create_article | Accessible Article title, required; label mnemonic | KW |
| KNOWLEDGE.NEW.SUMMARY | NewArticleDialog / &Summary / `summary_input`; QLineEdit | Form third | submit reads → create_article | Accessible Article summary, optional; label mnemonic | KW |
| KNOWLEDGE.NEW.BODY | NewArticleDialog / &Body * / `body_input`; QPlainTextEdit | Form fourth | submit reads plain text → create_article | Accessible Article body, required, Markdown source; label mnemonic | KW |
| KNOWLEDGE.NEW.CANCEL | NewArticleDialog / Cancel / `cancel_button`; QPushButton | Action row first button | clicked → reject | Not auto-default; blocked submitting | KW |
| KNOWLEDGE.NEW.SAVE | NewArticleDialog / Create Article / `create_button`; QPushButton | Action row second | clicked → submit → create_article | Default/Enter; guards submitting/created/runner busy; validates nonblank code/title/body | KW, KI |
| KNOWLEDGE.EDIT.TITLE | EditArticleDialog / &Title * / `title_input`; QLineEdit | Form after read-only code/current version | submit reads → update_article | Accessible Article title, required; label mnemonic | KW |
| KNOWLEDGE.EDIT.SUMMARY | EditArticleDialog / &Summary / `summary_input`; QLineEdit | Next form row | submit reads → update_article | Accessible Article summary, optional; label mnemonic | KW |
| KNOWLEDGE.EDIT.BODY | EditArticleDialog / &Body * / `body_input`; QPlainTextEdit | Last form row | submit reads → update_article | Accessible Article body, required, Markdown source; label mnemonic | KW |
| KNOWLEDGE.EDIT.CANCEL | EditArticleDialog / Cancel / `cancel_button`; QPushButton | Action row first button | clicked → reject | Not auto-default; blocked submitting | KW |
| KNOWLEDGE.EDIT.SAVE | EditArticleDialog / Save Revision / `save_button`; QPushButton | Action row second | clicked → submit → update_article(expected_version_number) | Default; guarded submitting/saved/conflicted/busy; draft-only service guard | KW, KI |

New feedback and Edit `code_label`, `version_label`, `feedback` are passive
QLabels; Edit's identity/version labels allow mouse text selection and do not
permit identity changes. Missing required New inputs receive focus; failed
writes retain drafts. Published/archived articles are not editable here.

### Article Category and Article Tags dialogs

Owners: [ArticleCategoryDialog](../Python/f7hub/gui/article_category_dialog.py)
and [ArticleTagsDialog](../Python/f7hub/gui/article_tags_dialog.py), parented to
the window by KnowledgeWorkspace. No objectNames are assigned. QVBoxLayout:
current article label, selector (Tags additionally has an instruction label),
feedback, actions QHBoxLayout: Refresh, stretch, default Cancel, Save.
`A-idle` means active, runner idle and not submitting. Selector/Save additionally
require loaded choices and no conflict; Refresh requires no conflict. Cancel
remains enabled during reference reads, but Cancel/X/done refuse during writes.
There is no additional custom shortcut. **KA-C** =
[category dialog tests](../Tests/GUI/test_article_category_dialog.py),
**KA-T** = [tags dialog tests](../Tests/GUI/test_article_tags_dialog.py).

| Stable ID | Owner / label / member; widget | Position | Event → handler / KnowledgeService method | State / focus / shortcut | Tests |
|---|---|---|---|---|---|
| KNOWLEDGE.CATEGORY.INPUT | ArticleCategoryDialog / `category_input`; QComboBox | Below current article/category label | submit reads category id → set_article_category | A-idle, loaded, no conflict; accessible Active Knowledge category; Not selected clears category | KA-C |
| KNOWLEDGE.CATEGORY.REFRESH | ArticleCategoryDialog / Refresh categories / `refresh_button`; QPushButton | Actions first | clicked → load_categories → list_active_knowledge_categories | A-idle, no conflict | KA-C |
| KNOWLEDGE.CATEGORY.CANCEL | ArticleCategoryDialog / Cancel / `cancel_button`; QPushButton | Actions after stretch | clicked → reject | Default/Enter; not submitting | KA-C |
| KNOWLEDGE.CATEGORY.SAVE | ArticleCategoryDialog / Save / `save_button`; QPushButton | Actions last | clicked → submit → set_article_category(id, version, timestamp, category) | A-idle, loaded, no conflict; current-context guard; not auto-default | KA-C |
| KNOWLEDGE.TAGS.INPUT | ArticleTagsDialog / `tag_list`; QListWidget | Below Select zero or more existing tags | Checked UserRole ids read by submit → set_article_tags | A-idle, loaded, no conflict; accessible Existing global tags; checkable items; zero clears all | KA-T |
| KNOWLEDGE.TAGS.REFRESH | ArticleTagsDialog / Refresh tags / `refresh_button`; QPushButton | Actions first | clicked → load_tags → list_available_tags and list_article_tags | A-idle, no conflict | KA-T |
| KNOWLEDGE.TAGS.CANCEL | ArticleTagsDialog / Cancel / `cancel_button`; QPushButton | Actions after stretch | clicked → reject | Default/Enter; not submitting | KA-T |
| KNOWLEDGE.TAGS.SAVE | ArticleTagsDialog / Save / `save_button`; QPushButton | Actions last | clicked → submit → set_article_tags(id, version, timestamp, ids) | A-idle, loaded, no conflict; current-context guard; not auto-default | KA-T |

The current labels and feedback are passive plain-text QLabels. A stale loaded
context requires reopening; saved associations are not inferred from a checked
item. Tag catalog creation is not offered by this dialog.

### Multi-tag filter dialog

Owner: [KnowledgeTagFilterDialog](../Python/f7hub/gui/knowledge_tag_filter_dialog.py),
window-parented by KnowledgeWorkspace.open_tag_filter. No objectNames or custom
shortcuts are assigned. The dialog consumes cached available tags and changes
read-filter state only; it does not call a persistence service. After accept,
KnowledgeWorkspace._tag_filter_closed reads selected_ids/matches_all, updates
the filter and reloads list/search if changed. Opening requires idle shared and
filter runners, ready tag options, and no conflicting dialog/confirmation.
All controls use native input behavior. **KFD** =
[tag-filter dialog tests](../Tests/GUI/test_knowledge_tag_filter_dialog.py);
KF-T covers owner-level query composition and cancellation.

| Stable ID | Label / member; widget | QVBoxLayout / action row order | Event → handler / owner | State / shortcut | Tests |
|---|---|---|---|---|---|
| KNOWLEDGE.TAGFILTER.ANY | Match any selected tag / `any_button`; QRadioButton | After instruction, before All | Native exclusive state, read by matches_all | Any default unless supplied all-mode; Space tested | KFD, KF-T |
| KNOWLEDGE.TAGFILTER.ALL | Match all selected tags / `all_button`; QRadioButton | Below Any | Native exclusive state, read by matches_all | Space tested | KFD, KF-T |
| KNOWLEDGE.TAGFILTER.TAGS | `tag_list`; QListWidget | Below radio buttons, stretch 1 | Native item checks; selected_ids reads sorted ids | Accessible Tags to match; Space toggles; none = All tags, one = specific tag | KFD, KF-T |
| KNOWLEDGE.TAGFILTER.CANCEL | Cancel / `cancel_button`; QPushButton | Bottom QHBoxLayout after stretch, first | clicked → reject | Default/Enter; native Escape dismissal | KFD, KF-T |
| KNOWLEDGE.TAGFILTER.APPLY | Apply / `apply_button`; QPushButton | Bottom last | clicked → accept → owner _tag_filter_closed | Not auto-default; no write | KFD, KF-T |

### Version history viewer

Owner: [VersionHistoryDialog](../Python/f7hub/gui/version_history_dialog.py),
window-parented by KnowledgeWorkspace.open_version_history. No objectNames or
custom shortcuts are assigned. QVBoxLayout: feedback, horizontal splitter,
Close action row. Splitter contains the list then detail panel (390/500 initial
sizes). Detail panel contains a resizable metadata QScrollArea then body.
ServiceTaskRunner → KnowledgeService.list_article_versions/get_article_version
→ KnowledgeRepository supplies immutable revision projections. The viewer can
close while a read is pending; active/generation guards ignore late callbacks.
KW tests history availability, exact plain-text content, failures and dismissal.

| Stable ID | Label / member; widget | Position / container | Event → handler / backend | State / accessibility / shortcut | Tests |
|---|---|---|---|---|---|
| KNOWLEDGE.HISTORY.TABLE | `table`; QTableView | Splitter first → list_panel QVBoxLayout | selectionChanged → _selection_changed → _load_version → get_article_version | Single read-only row; disabled runner busy; accessible Knowledge article version history | KW |
| KNOWLEDGE.HISTORY.SPLIT | List/revision divider; QSplitter | Main VBox below feedback | Native movement; no service | Horizontal; no direct drag test identified | KW (layout/content only) |
| KNOWLEDGE.HISTORY.BODY | `detail_body`; QPlainTextEdit | Detail VBox below metadata_scroll, stretch 1 | _show_version sets plain text | Read-only; accessible Historical knowledge article body, read only; native selection/copy | KW |
| KNOWLEDGE.HISTORY.CLOSE | Close / `close_button`; QPushButton | Bottom QHBoxLayout after stretch | clicked → reject | Remains available during reads; late completion ignored | KW |

Metadata scroll accessible name is Historical revision metadata, read only.
Its labels `detail_version`, `detail_title`, `detail_summary`,
`detail_created_at`, `detail_created_by`, `detail_change_summary` wrap plain text
and allow mouse selection. These passive labels and the scroll container are
excluded from control counts under the Pass 1 rule. No restore/revert, delete,
Unarchive or historical edit action is defined in these inspected classes.

## Pass 1 result and outstanding coverage — historical checkpoint

**GUI_REGISTRY_PASS1_COMPLETE — READY_FOR_CONTINUATION.** Tickets and Knowledge
Base construction, child dialogs, signal routing, logical layout, explicit
shortcuts, state gates, service owners and existing test references have been
inspected at the pinned source revision. This is author-side static evidence;
independent review and runtime validation are separate gates.

| Pass 1 inventory group | Control rows |
|---|---:|
| Tickets queue/detail, tabs, creation-mode Cancel and draft confirmations | 43 |
| Ticket creation form | 14 |
| Quick company/contact dialogs | 7 |
| Ticket subject/description dialogs | 6 |
| Ticket Knowledge links, selector and unlink confirmation | 11 |
| **Tickets total** | **81** |
| Knowledge workspace and publish/archive confirmations | 22 |
| New/Edit Article dialogs | 11 |
| Article Category/Tags dialogs | 8 |
| Multi-tag filter dialog | 5 |
| Version history viewer | 4 |
| **Knowledge Base total** | **50** |
| **Pass 1 total** | **131** |

Focused static validation: **PASS**, including 117 constructed widget-member
mappings plus 14 structural/confirmation entries, unique IDs, 36 source/test
links, assigned objectNames, direct control-to-method connection names, table
column consistency and preservation of the pre-registry document. Logical
layout, state and backend semantics were manually traced; these automated checks
are not a semantic or runtime proof. The external audit's original failed result
is retained alongside the corrected successful result: the first check treated
callback arguments as handler names and prompted clearer connection wording.
No runtime, database, native GUI or regression suite was executed.

Limits: native pixel placement, platform shortcut resolution and physical input
acceptance are **NOT VERIFIED**. The splitter rows have layout/content test
references but no direct drag assertion was identified. Passive labels and
inherited Qt editor menus are described under the stated counting rule rather
than assigned separate control IDs. No unresolved source handler is claimed in
the new tables; future independent review may identify corrections.

**Full registry INCOMPLETE:** next module is Scripts/Diagnostics. Remaining work
also includes the Clipboard partial table and setup/state transitions, shell/
utility/lifecycle completion, AHK hotkeys and delegated Guide boundary, and the
final comprehensive consistency/coverage audit. Those areas were not extended
by Pass 1. No full-application total, shortcut count, shared-action count or
independent-review readiness is claimed.

Maintain stable IDs and update affected entries after approved changes are
validated. Distinguish a shared QAction from its multiple visual presentations;
record unresolved relationships as `NOT VERIFIED` and never infer runtime
behavior or authorization from an entry.

<a id="gui-registry-scripts"></a>

## Pass 2 — Scripts and Diagnostics

This section extends the existing registry at the same inspected source
`62f95f185cd5abfefbfbc16822d12dc30144ed79`. All entries inherit **Integrated /
static inspection**; runtime/native validation is **NOT RUN** in this pass.
The Pass 1 counting convention applies: one row per control, splitter or
transient dialog choice; passive labels, repeated data rows and native editor
menus are excluded. Member names are source locators. ObjectName is `—` for
every counted control below: none is assigned in these three GUI classes.
`—` for a shortcut means no explicit custom binding; native Qt behavior remains.

### Scripts workspace and implemented diagnostic execution

Owner: [script_workspace.py](../Python/f7hub/gui/script_workspace.py),
`ScriptWorkspace.__init__`, hosted as MainWindow's Scripts page. Its QVBoxLayout
contains: heading/action row; pack heading; pack notice; pack action/readiness
row; search row; summary; feedback; horizontal splitter. The splitter contains
the list panel (table, empty-state label) then the result panel (metadata,
run notice, result editor), initially 560/440. These are logical insertion
positions, not verified screen geometry.

`S-idle` means `_update_actions` has no supplied runner-busy flag or
`run_pending`, and neither `_loading` nor `_copying` is true. MainWindow's
parent-page enable state additionally applies: the shared runner and accepted
diagnostic ownership can disable the page. Enabled appearance is not dispatch
authority; `_can_run`, `copy_script`, search and refresh retain their own guards.
The explicit local Tab chain is Run diagnostic → Copy Script → Manage scripts…
→ Refresh. No other local setTabOrder, custom QShortcut or QAction is installed
in these three GUI classes. Native/editor and shell focus behavior still apply;
full physical traversal is **NOT VERIFIED**.

Test keys: **SW** = [workspace tests](../Tests/GUI/test_script_workspace.py)
(construction, button order/keyboard, metadata, copy/stale selection, search and
read recovery); **SE** = [execution GUI tests](../Tests/GUI/test_script_execution.py)
(explicit dispatch, callback gaps, run ownership, readiness and cleanup latch);
**SC** = [catalog integration](../Tests/Integration/test_script_catalog_flow.py)
(registration/visibility, copy, search and retained metadata);
**SX** = [execution integration](../Tests/Integration/test_script_execution_workflow.py);
**DP** = [pack service tests](../Tests/PowerShell/test_diagnostic_pack.py).
These are existing source references, not newly executed results; SX includes
Windows-native execution tests that this documentation pass does not run.

Catalog reads and management use ServiceTaskRunner →
[ScriptService](../Python/f7hub/services/script_service.py) →
[ScriptRepository](../Python/f7hub/repositories/script_repository.py) → SQLite.
Copy uses `read_verified_script` to validate current approved source, then the
GUI completion sets the clipboard only if selection generation, script code and
page visibility still match. A prior AVAILABLE observation alone does not grant
copy approval. Copying neither launches PowerShell nor pastes into another app.

Explicit execution uses ServiceTaskRunner →
[PowerShellService](../Python/f7hub/services/powershell_service.py) →
[PowerShellGateway](../Python/f7hub/infrastructure/powershell_gateway.py), with
ScriptService supplying verified source. [Bootstrap](../Python/f7hub/app/bootstrap.py)
composes these shared owners. The literal policy permits the reviewed System,
Network and Services snapshots; the fixed
[Local Baseline Diagnostics definition](../Python/f7hub/domain/diagnostic_results.py)
orders System → Network → Services. Service/gateway boundaries recheck identity,
metadata, source bytes, runtime and process/result contracts; registration or
availability does not authorize arbitrary execution. See the current Slice 053
contract in [PowerShell architecture](12_PowerShellArchitecture.md).

| Stable ID | Label / member; widget | Logical position / parent | Event → handler / backend | Availability / accessibility / focus | Shortcut | Tests |
|---|---|---|---|---|---|---|
| SCRIPTS.RUN.DIAGNOSTIC | Run diagnostic / `run_button`; QPushButton | Header after stretch, first action | clicked → `run_diagnostic` → `_start_run` → PowerShellService.execute_diagnostic(selected code) | S-idle, AVAILABLE selected entry with execution-approved metadata, no management dialog, execution service supplied, no local cleanup block; accessible Run the selected reviewed diagnostic | — | SE, SW, SX |
| SCRIPTS.COPY | Copy Script / `copy_button`; QPushButton | Header second action | clicked → `copy_script` → ScriptService.read_verified_script → guarded clipboard completion | S-idle and AVAILABLE selection; service may still reject checksum/eligibility; accessible Copy Script | — | SW, SC |
| SCRIPTS.MANAGE | Manage scripts… / `manage_button`; QPushButton | Header third action | clicked → `open_management` → ScriptManagementDialog | S-idle, no existing manager; parented to `self.window()` outside the disabled page stack | — | SW, SM, SC |
| SCRIPTS.REFRESH | Refresh / `refresh_button`; QPushButton | Header fourth action, last | clicked → `refresh_list` → ScriptService.list_scripts(text_query), optional PowerShellService.pack_readiness | S-idle; refresh uses last submitted query, preserves selected code after success | — | SW, SE, SC |
| SCRIPTS.RUN.BASELINE | Run baseline diagnostics / `pack_button`; QPushButton | Pack QHBoxLayout first, before stretchable readiness label; above search | clicked → `run_pack` → `_start_run` → execute_diagnostic_pack(LOCAL_BASELINE_PACK.code) | S-idle, `_pack_ready`, service supplied, no manager or local cleanup block; readiness is independent of filtered catalog rows; accessible Run baseline diagnostics | — | SE, DP, SX |
| SCRIPTS.SEARCH.INPUT | Search names, codes and descriptions / `search_input`; QLineEdit | Search QHBoxLayout first, stretch 1 | returnPressed → `search_scripts` → trim query → `refresh_list` | S-idle; text editing alone does not submit; accessible Search script names, codes and descriptions | Return | SW, SC |
| SCRIPTS.SEARCH.SUBMIT | Search / `search_button`; QPushButton | Search row second | clicked → `search_scripts` → same list query as Return | S-idle; blank submitted text selects unfiltered catalog | — | SW, SC |
| SCRIPTS.SEARCH.CLEAR | Clear / `clear_search_button`; QPushButton | Search row third | clicked → `clear_search` → clear input/query → `refresh_list` | S-idle; clears submitted filter and current draft | — | SW, SC |
| SCRIPTS.TABLE | `table`; QTableView | Splitter first child → list panel VBox before empty-state label | selectionChanged → `_selection_changed` → `_show_entry`, update action state | Single read-only row selection; locally disabled during run_pending; accessible Enabled scripts; select a row to read metadata; selection does not execute | Native selection | SW, SE |
| SCRIPTS.DETAILS | `details`; QPlainTextEdit | Splitter second child → result panel VBox first, stretch 1 | `_show_entry` presents selected service metadata; cleared on missing selection/read reset | Read-only; accessible Script metadata, read only; reference shown as plain text, not a launch control | Native selection/copy | SW |
| SCRIPTS.RESULTS | `results`; QPlainTextEdit | Result panel below run-notice label, last, stretch 1 | `_present_result` / `_attempt_lines` render single or pack results after accepted completion | Read-only; accessible Diagnostic result, read only; kept in memory only; a run attempt reaching `_start_run` clears the display, including subsequent dispatch rejection | Native selection/copy | SE, SX |
| SCRIPTS.SPLIT | Catalog/result divider; local `splitter`; QSplitter | Main VBox last; horizontal, list then result panel | Native movement; no backend call | Initial 560/440 sizes; runtime geometry and direct drag acceptance NOT VERIFIED | — | SW (construction; no direct drag assertion identified) |

Passive QLabels: `heading` (objectName `scriptsHeading`), `pack_heading`,
`pack_notice`, `pack_readiness`, `summary`, `feedback`, `empty_state` and
`run_notice`. Summary reports shown/available/execution-approved counts; it does
not authorize a run. Feedback distinguishes loading, invalid search, read/copy
failure, execution failure and completed results. Empty state distinguishes no
scripts from no search matches. The run notice describes the selected reviewed
diagnostic; it is not an additional Run control.

`_run_identity` holds ownership through callback presentation, including the
runner-idle gap; stale completions cannot release another run. Failed dispatch
and worker/presentation errors release that ownership with safe feedback.
Unverified cleanup latches `_execution_blocked`, clears pack readiness and blocks
both run modes. Results remain in memory; valid collection ERROR is distinct
from execution failure, and an aborted pack retains attempted results and skipped
members. Execution has no confirmation dialog or Cancel control here. There is
no custom Scripts context menu; inherited text-editor selection/copy commands
are native behavior, excluded from counts. Search is manual text matching over
names/codes/descriptions; no separate category/type/status filter is constructed.
The broader planned Diagnostic Center, parameter forms, arbitrary script runs,
execution history, ticket linkage, remediation and user-defined packs are not
implemented controls in these classes.

### Script management and enable confirmation

Owner: [script_management_dialog.py](../Python/f7hub/gui/script_management_dialog.py),
`ScriptManagementDialog`, opened by ScriptWorkspace.open_management using
`dialog.open()` then `refresh_list`. It is parented to the top-level window,
outside MainWindow.pages, so the shared worker's page disabling does not disable
its controls indiscriminately. `M-idle` is `_update_actions`' predicate: runner
idle, not loading/writing/confirming, no registration child and not closed.
The QVBoxLayout contains an explanatory note, feedback, table (stretch 1),
metadata editor, then the action row. **SM** =
[management/registration GUI tests](../Tests/GUI/test_script_management_dialog.py)
(selection, enable confirmation, write guards, preserved drafts, committed-write
refresh failure and dismissed late reads). SC additionally covers real catalog
reconciliation with isolated test data; no such tests run in this pass.

| Stable ID | Label / member; widget | Logical position / parent | Event → handler / backend | Availability / accessibility / keyboard | Tests |
|---|---|---|---|---|---|
| SCRIPTS.MANAGER.TABLE | `table`; QTableView | Management VBox below feedback, above details | selectionChanged → `_selection_changed` → `_selected` metadata / `_update_actions` | M-idle; single read-only row selection; accessible Script registrations, including disabled; columns Name, Code, Enabled, File status; native selection | SM, SC |
| SCRIPTS.MANAGER.DETAILS | `details`; QPlainTextEdit | Below table, maximum height 150; above actions | `_selection_changed` presents selected registration, including stored checksum; no write | Read-only; accessible Registration metadata, read only; no local enable override; native selection/copy | SM |
| SCRIPTS.MANAGER.REGISTER | Register script… / `register_button`; QPushButton | Bottom QHBoxLayout first | clicked → `open_registration` → RegisterScriptDialog; finished → `_registration_closed`, script_registered → `_registered` | M-idle; not auto-default; no custom shortcut; one child at a time | SM, SC |
| SCRIPTS.MANAGER.REFRESH | Refresh / `refresh_button`; QPushButton | Actions second | clicked → `refresh_list` → ScriptService.list_registered_scripts | M-idle; includes disabled records; preserves preferred id after successful reload; not auto-default | SM, SC |
| SCRIPTS.MANAGER.TOGGLE | Enable / Disable / `toggle_button`; QPushButton | Actions third, before stretch | clicked → `toggle_selected` → optional enable confirmation → ScriptService.set_script_enabled(id, enabled, expected_updated_at) | M-idle and selected record; label reflects retained enabled state; enable rechecks readable source; disable has no confirmation; not auto-default, Space activation tested | SM, SC |
| SCRIPTS.MANAGER.CLOSE | Close / `close_button`; QPushButton | Actions after stretch, last | clicked → inherited reject → guarded `done`; owner `_management_closed` reconciles changed catalog | Button enabled when not writing and no registration child; done/X additionally refuse during confirmation; can dismiss reads, ignoring late callbacks; default button, no custom shortcut | SM, SC |
| SCRIPTS.MANAGER.CONFIRM.ENABLE | Yes; QMessageBox standard button | Enable script modal confirmation → native action area; no source-defined button ordering claimed | `toggle_selected` compares exec result to Yes, rechecks exact selected record identity and closed state, then dispatches write | Only enabling opens confirmation; catalog visibility only, no content/copy/execution approval; native dialog activation | SM |
| SCRIPTS.MANAGER.CONFIRM.CANCEL | Cancel; QMessageBox standard button | Same modal action area | exec result other than Yes → no visibility write | Explicit default Cancel; native standard-button behavior, physical resolution NOT VERIFIED | SM |

No custom shortcuts, explicit Tab order or context menus are installed here.
The note and `feedback` are passive QLabels. The table/model and selected record
are the retained operation context; a stale write reports conflict and clears
the obsolete selection. Successful registration/toggle sets `changed`, retains
the saved identity and committed notice, then refreshes. Failed refresh does not
repeat or relabel the committed write. On manager dismissal, the workspace queues
its changed-catalog refresh until the shared runner is idle.

### Register Script dialog

Owner: [register_script_dialog.py](../Python/f7hub/gui/register_script_dialog.py),
`RegisterScriptDialog`, parented to the manager and opened by `open_registration`.
Its QVBoxLayout contains a QFormLayout, note, feedback and an action QHBoxLayout:
stretch, default Cancel, Register script. `_choices` constructs the three
QComboBoxes, each starting with Select…/None; these are three control instances,
not extra rows for the reusable helper. The exact form order is shown below.
All ten controls are disabled by `_set_submitting(True)`; done/X refuse during
submission. `submit` also rejects an already-created result or busy runner.
Failures preserve input and display safe feedback; no explicit field-focus
restoration, custom shortcut or local Tab order is installed. Form `&` markers
are source mnemonics; native resolution is **NOT VERIFIED**.

| Stable ID | Label / member; widget | Form or action order | Event → handler / ScriptService dependency | Accessibility / keyboard | Tests |
|---|---|---|---|---|---|
| SCRIPTS.REGISTER.CODE | Script &code * / `code_input`; QLineEdit | Form first | `submit` reads text → register_script(script_code) | Accessible Script code, required; label mnemonic | SM, SC |
| SCRIPTS.REGISTER.NAME | &Name * / `name_input`; QLineEdit | Form second | `submit` reads text → register_script(name) | Accessible Script name, required; label mnemonic | SM, SC |
| SCRIPTS.REGISTER.PATH | Relative &path * / `path_input`; QLineEdit | Form third | `submit` reads text → register_script(relative_path); service validates approved relative reference | Accessible Relative script path, required; PowerShell/Diagnostics/Example.ps1 placeholder; label mnemonic | SM, SC |
| SCRIPTS.REGISTER.TYPE | &Type * / `type_input`; QComboBox via `_choices(SCRIPT_TYPES)` | Form fourth | `submit` reads currentData → register_script(script_type) | Accessible Script type, required; Select… then service-defined types; label mnemonic | SM, SC |
| SCRIPTS.REGISTER.RISK | &Risk * / `risk_input`; QComboBox via `_choices(RISK_LEVELS)` | Form fifth | `submit` reads currentData → register_script(risk_level) | Accessible Script risk, required; Select… then service-defined risk levels; label mnemonic | SM, SC |
| SCRIPTS.REGISTER.PRIVILEGE | &Privilege * / `privilege_input`; QComboBox via `_choices(PRIVILEGE_LEVELS)` | Form sixth | `submit` reads currentData → register_script(privilege_level) | Accessible Script privilege, required; Select… then service-defined privilege levels; label mnemonic | SM, SC |
| SCRIPTS.REGISTER.DESCRIPTION | &Description / `description_input`; QPlainTextEdit | Form seventh, maximum height 80 | `submit` reads plain text → register_script(description) | Accessible Description, optional; multiline native editing; label mnemonic | SM, SC |
| SCRIPTS.REGISTER.VERSION | &Version / `version_input`; QLineEdit | Form eighth, last | `submit` reads text → register_script(version) | Accessible Version, optional; label mnemonic | SM, SC |
| SCRIPTS.REGISTER.CANCEL | Cancel / `cancel_button`; QPushButton | Bottom actions first button, after stretch | clicked → inherited reject → guarded `done` | Default button; disabled during submission; no custom shortcut | SM |
| SCRIPTS.REGISTER.SAVE | Register script / `register_button`; QPushButton | Bottom actions last | clicked → `submit` → ServiceTaskRunner → ScriptService.register_script → ScriptRepository; `_succeeded` accepts and emits script_registered | Not auto-default; duplicate/completed/busy guards; no custom shortcut | SM, SC |

`note` and `feedback` are passive plain-text QLabels. The note describes metadata
registration of an already-existing readable .ps1 under PowerShell/Diagnostics,
Reports or Modules, disabled with no approved checksum, and defaults of
PowerShell 7, 120 seconds and structured output. The form offers no file creation,
content editing, approval, category picker, runtime/timeout editor, file browser
or Run action. ScriptService validates choices and references; repository methods
own the transactional metadata writes and stale-token protection. This is not a
second execution pathway. No GUI code directly writes SQL.

### Pass 2 coverage and validation status — historical checkpoint

| Scripts/Diagnostics inventory group | Control rows |
|---|---:|
| Workspace, single diagnostic, fixed baseline pack, search, views and splitter | 12 |
| Management dialog and enable confirmation choices | 8 |
| Registration form and actions | 10 |
| **Pass 2 total** | **30** |

Counts include 27 constructed widget instances, one splitter and two standard
confirmation choices. Enable/Disable is one button with two labels; its Yes and
Cancel confirmation choices are separate transient controls. Run diagnostic and
Run baseline diagnostics are separate buttons that reuse `_start_run` and the
same service/gateway; neither creates a duplicate QAction. Their shared result
editor counts once. Passive status/error feedback adds no action rows.

**GUI_REGISTRY_PASS2_COMPLETE — READY_FOR_CONTINUATION.** Fresh focused
author-side static validation: **PASS**. Checks cover all 27 widget mappings,
the splitter and two confirmation choices, 16 direct control connections,
source/class/API and assigned-name checks, accessibility labels, selected layout
and state invariants, linked source/test identities, unique IDs, table columns,
counts, prior-document/AGENTS byte preservation, three-path scope and empty
index. Logical layout, availability and backend semantics were also inspected
in source; static checks are not runtime proof. Existing test references were
inspected, not executed. No runtime GUI, PowerShell execution, Clipboard,
database or full regression operation was performed. Splitter dragging, native
rendering/DPI, physical input and platform mnemonic/default-key resolution remain
**NOT VERIFIED**; no direct splitter-drag assertion was identified.

Full registry remains INCOMPLETE;
the next unfinished inventory is Clipboard Center, followed by shell/utilities/
lifecycle completion, AHK/delegated Guide mapping and the final consistency audit.
Those sections have not been extended by this pass. No full-application control,
presentation or shortcut total, independent-review readiness or integration
eligibility is claimed.

## Pass 5 — final source reconciliation and review preparation

<a id="gui-registry-coverage"></a>

### Coverage and counting units

The author-side audit covers Python/f7hub and Mochi/src Python construction
sites, their custom QWidget subclasses/factories, the integrated F7Hub.ahk include
closure and the fixed Guide request client. Each applicable discovered input,
view, action, confirmation or binding is mapped or explicitly excluded. Detailed
per-site construction/signal ledgers and five batch records are external in the
final review package. No unexplained construction or ownership gap remains in
this inspected source scope. Unrelated standalone AHK experiments, test fixtures,
authored topic rows and future features are not production GUI constructions.

| Module family | Current control/presentation rows |
|---|---:|
| Tickets and owned dialogs | 81 |
| Knowledge Base and owned dialogs | 50 |
| Scripts / Diagnostics and owned dialogs | 30 |
| Clipboard Center / Setup | 14 |
| Shell / lifecycle / Mochi / Guide / AHK | 68 |
| **Final documented total** | **243** |

The recovered Pass 4 total was 241. Two verified omissions were added in Pass 5:
SHELL.FEEDBACK.STARTUP.FAILURE and MOCHI.PET.SURFACE. This is a source-driven
correction, not an expected-count target. All prior control IDs remain present.

Construction totals use a union of one instance of each documented source class
or factory output, including conditional service branches. They do not describe
simultaneous visibility, repeated dialog openings or platform-private objects.
Read-only focusable data/text views count as interactive views. Pure composite
containers do not; the pet's custom mouse-input canvas does.

| Unit | Verified source count / interpretation |
|---|---|
| Constructed interactive widgets | 198: 172 Qt widgets and 26 AHK native controls |
| Interactive splitters | 4, already included in the 172 Qt widgets; not added again |
| Pure tab-target rows | 2: Knowledge and Company; the other three Ticket tab rows also describe their read-only content editors, counted once per row |
| Menu-entry presentations | 10: nine explicit QAction menu presentations and one inserted submenu entry |
| Tray icon | 1 QSystemTrayIcon; QObject surface, outside QWidget total |
| Confirmation/acknowledgement choices | 32: 20 Qt choices and 12 AHK standard acknowledgements |
| Presentation-row reconciliation | 198 widgets + 2 tab targets + 10 menu entries + 1 tray icon + 32 choices = 243 |
| Explicit QAction identities | 13 source-constructed objects: MainWindow 8, lifecycle 2, pet 3; implicit framework actions excluded |
| Explicit QAction presentations | 14: nine menu entries plus four rail buttons and the Knowledge Guide button; one Guide action has two presentations |
| QShortcut instances | 3: shell Alt+F / Alt+S and Ticket creation StandardKey.Save; Quit is an action shortcut, not a fourth QShortcut |
| Registered AHK hotkey definitions | 12 in the integrated host; F7 down/up are two definitions, TAP/HOLD are routing outcomes, topic keys use message dispatch |
| Passive source templates excluded | 78 QLabel constructor sites and 9 AHK AddText sites; 87 source templates, not a runtime instance count |
| Unresolved source/handler/action ownership mappings | 0; explicitly unverified runtime/identity/test matters are listed below |

Passive factories may produce multiple labels, and native form labels, headers,
scrollbars, picker internals, default editor menus and repeated data/topic rows
are excluded. QTabWidget/QStackedWidget/QScrollArea and ordinary dialog/page
containers are structural; their represented targets or child controls remain
covered. TicketKnowledgeWidget's tab row is a target/composite, not a second
count of its link controls. Factory declarations are not additional instances.

| Inspected class/source owner | Coverage / explicit exclusion |
|---|---|
| TicketWorkspace | 43 rows: queue/detail/actions, read-only tab content, Company target and draft choices; one structural QTabWidget represented by its five targets |
| TicketCreateWidget | 14 rows; three reference-combo outputs mapped individually; helper constructor/error-label templates excluded |
| QuickCompanyDialog / QuickContactDialog | 3 / 4 rows; dialog containers and generated form labels excluded |
| EditTicketSubjectDialog / EditTicketDescriptionDialog | 3 / 3 rows; inherited reject/default input semantics distinguished from custom shortcuts |
| TicketKnowledgeWidget / LinkArticleDialog | 7 / 4 rows; two _ArticleIdentityTable instances covered at their call sites; composite container not extra widget |
| KnowledgeWorkspace | 22 rows, including shared Guide presentation, splitter and publish/archive choices; passive metadata excluded |
| NewArticleDialog / EditArticleDialog | 6 / 5 rows; identity/version labels excluded |
| ArticleCategoryDialog / ArticleTagsDialog | 4 / 4 rows; generated category/tag choices are data, not extra controls |
| KnowledgeTagFilterDialog / VersionHistoryDialog | 5 / 4 rows; metadata scroll container and labels excluded |
| ScriptWorkspace / ScriptManagementDialog / RegisterScriptDialog | 12 / 8 / 10 rows; fixed diagnostic pack and manual search covered; three _choices outputs counted, template excluded |
| ClipboardWorkspace / ClipboardSetup | 6 / 8 rows; two source choices in one selector, conditional section stacks, three checkbox outputs and two draft choices; disabled Windows Refresh is not acquisition |
| MainWindow / app.main.main | 13 shell/utility/feedback rows plus one startup acknowledgement; named actions and event bindings separate; no active menu bar/toolbar/dock |
| ApplicationLifecycle / Windows visibility adapter | 5 presentation/choice rows plus close/activation bindings; recovery timer/query/state transitions excluded from control count |
| MochiSettingsDialog / PetWindow / Mochi app | 7 / 4 rows, including custom pet input surface; app constructs the pet once; timers/animation frames are not controls |
| GuideCore / TopicRouting / GuideHost | 26 native controls and 10 Guide acknowledgements; shared toolbar has two sets of three buttons; topic catalog, hidden endpoint, draw/resize callbacks excluded |
| F7HotkeyController / F7HubLauncher / MagneticWindowFollower | 12 host hotkey definitions and one launcher acknowledgement; state/timer/movement bindings are not extra buttons |
| GuideRequest / Troubleshooting_Quick_Guide | Fixed delegated show/focus route and one client acknowledgement; no second persistent GUI or per-request control count |
| Table models / ServiceTaskRunner / transport services | Projection, background completion or relay infrastructure, not additional user controls; owning views/actions are mapped above |

### Legitimate action and handler reuse

| Reuse | Source-grounded relationship |
|---|---|
| Guide button and utility Guide | Same MainWindow.altf7hub_action, one triggered connection to show_altf7hub; two presentations |
| Rail navigation and routing | Four QToolButtons use their existing QActions; active marker is derived from pages, not a second action |
| Shell Exit and tray Exit | Different QActions, same ApplicationLifecycle.request_exit coordinator through MainWindow; shared guards, no duplicate shutdown owner |
| Tray icon and Open menu | Native Trigger/DoubleClick and open_action both invoke restore; one icon, not one control per activation reason |
| Single diagnostic and baseline pack | Different buttons/use cases reuse ScriptWorkspace._start_run and the shared PowerShell service/gateway |
| Refresh/Retry and Pause/Resume | One changing-label button in each applicable owner; labels do not create extra instances |
| Guide/editor formatting | AddFormattingToolbar constructs three buttons in each of two windows; six instances, one implementation |
| Source and section navigation | Clipboard source selector changes presentation; its two options and stacked pages are not new capture actions |

<a id="gui-registry-shortcuts"></a>

### Static shortcut ownership matrix

Every row below is source verification, not physical keyboard acceptance. Normal
native input and platform-generated menus remain available within their owner
scope; no shortcut was executed or reassigned by this audit.

The Win+Alt+V row is the 2026-10-29 candidate extension; its physical status is
explicitly USER-REPORTED. The earlier rows retain their pinned-audit status.
Static source search found one Python paste RegisterHotKey route and no active
AHK Win+Alt+V registration. Installed-application conflicts cannot be excluded
by source inspection: registration refusal leaves that operation unavailable.

| Shortcut / input | Owner and context | Effect / source | Potential conflict or limitation | Static status |
|---|---|---|---|---|
| Win+Alt+V | Python/Qt SelectionCapture; global native RegisterHotKey with MOD_NOREPEAT; existing safety/target restrictions | Paste Latest authorized F7Hub Clipboard capture: trigger(action='paste') → ClipboardService.paste_latest → native paste_latest / WindowsPasteAPI; latest eligible persisted source; one attempt per eligible press/release cycle | Existing ClipboardService consent/privacy and one-use authorization; original non-elevated target, release/cancellation/lease guards; no stale-history fallback or Windows Clipboard history integration; registration can collide with another app; Windows paste is non-atomic | Candidate source verified; code review APPROVED WITH NOTES; A/B/C USER-REPORTED PHYSICAL PASS; integration PENDING; documentation-delta review pending |
| Alt+F | MainWindow QShortcut, WidgetWithChildrenShortcut, no repeat | _focus_navigation; main_window.py | Active popup/modal refused; separate dialog windows keep local mnemonic handling | PASS; physical NOT VERIFIED |
| Alt+S | Same owner/context | _show_utility_menu; main_window.py | Popup show suspends both shortcuts; next-turn guarded resume after hide | PASS; physical NOT VERIFIED |
| Alt+F / Alt+S while popup active | MainWindow ShortcutOverride event filter | Consumes shell override so popup keeps native handling | Native menu dismissal/dispatch remains untested | PASS / NOT VERIFIED runtime |
| StandardKey.Quit | MainWindow.exit_action, associated with MainWindow | request_exit; Ctrl+Q fallback only if standard sequence empty on win32 | Exact platform standard sequence unresolved by static source | PASS definition; resolution NOT VERIFIED |
| StandardKey.Save | TicketCreateWidget QShortcut, WidgetWithChildrenShortcut | submit; ticket_create_widget.py | Scoped to creation widget descendants; no global Save action or assumed physical Ctrl+S result | PASS definition; resolution NOT VERIFIED |
| Ctrl+Return / Ctrl+Enter | TicketWorkspace note_input focus, no other modifier except keypad bit; no repeat | add_note; ticket_workspace.py eventFilter | Other editors/scopes do not acquire this submission action | PASS; physical NOT VERIFIED |
| Escape in Quick Note | Focused note_input | Consumed by TicketWorkspace | Preserves editor/draft rather than shell departure | PASS; physical NOT VERIFIED |
| Escape on rail/gear | Focused rail/gear, no popup, retained same-page editor | MainWindow eventFilter restores usable invoking editor | Popup Escape and dialog Escape remain their own paths | PASS; physical NOT VERIFIED |
| Enter/Return on gear; Space/Enter rail input | Focused shell controls | Gear explicitly click()s; rail records keyboard intent while default action owns activation | Actual native QToolButton key acceptance not inferred from intent tracking | PASS source; physical NOT VERIFIED |
| E&xit; &Clipboard Center | MainWindow action text | Source mnemonic markers on action labels | No invented global Alt+C shortcut; platform mnemonic resolution NOT VERIFIED | PASS marker definitions |
| Setup &E / &a / &t / &A / &C / &R | ClipboardSetup controls | Workflow/process/title/Apply/Cancel/Reload | Process &a and Apply &A overlap; physical dispatch/cycling explicitly NOT VERIFIED | PASS source; conflict resolution NOT VERIFIED |
| Dialog label & markers / default buttons | Owning Ticket/Knowledge/registration dialogs | Source form labels and setDefault/setDefaultButton/setEscapeButton calls | Default Enter or inherited Escape remain guarded by owning submit/done/reject methods; source defaults are not new QShortcuts | PASS definitions; physical NOT VERIFIED |
| F7 down / F7 up | Shared F7Hub.ahk host | F7HotkeyController.OnDown/OnUp | Two registered definitions; no repeat-created parallel hold timer | PASS; native NOT VERIFIED |
| F7 TAP / HOLD / release | Same controller, 180 ms source threshold | TAP LaunchOrFocus; HOLD LaunchOrFind + follower.Start; release Stop | HOLD timer is not another hotkey; physical timing/focus not exercised | PASS; native NOT VERIFIED |
| Alt+F7 ($!F7) | Shared host global binding | ToggleGuide; editor priority and active-Guide hide/show behavior | Separate from Python show/focus request; no automatic second toggle after dispatch | PASS; native NOT VERIFIED |
| Ctrl+F / Ctrl+L | Guide active HWND #HotIf | FocusSearch / ShowSidebar | Scoped to Guide window; editor is separate owned window | PASS; native NOT VERIFIED |
| Ctrl+PgUp / Ctrl+PgDn | Guide active HWND #HotIf | NavigateTopic(-1/+1) | Scope is window-level; notes/list-only scope applies to unmodified arrows instead | PASS; native NOT VERIFIED |
| Guide Escape / editor Escape | Guide host binding / EditorGui Escape event | Guide.Hide / CloseEditor | Different window scopes; editor Cancel discards uncommitted editor session, no invented confirmation | PASS; native NOT VERIFIED |
| Up/Down / Left/Right | GuideNavigationFocused, notes/list, active Guide, no Ctrl/Alt/Shift/Win | Repeated topic navigation / opacity ±1 | Other controls retain native input; no arbitrary debounce inferred | PASS; native NOT VERIFIED |
| C / E / valid topic keys | GuideHost WM_KEYDOWN callback, same notes/list/modifier scope; non-repeat | Create/edit or TopicRouting.ShortcutTarget | Data-driven topic targets are not extra registered hotkeys; archive guards apply | PASS; native NOT VERIFIED |

Source default-button audit covers the named dialog groups, not an assumed
universal Save key: quick company/contact and new/edit article/subject dialogs
use their source defaults; category/tags/multi-tag, script registration/manager
and destructive confirmations prefer Cancel/Close as recorded in their rows.
Inherited editor copy/undo/context commands and OS color-picker internals are
excluded from custom shortcut totals.

<a id="gui-registry-findings"></a>

### Findings, architecture and readiness

| Finding | Type / severity | Verification and disposition |
|---|---|---|
| P5-D01: startup acknowledgement missing | Documentation defect / P2 | RESOLVED: SHELL.FEEDBACK.STARTUP.FAILURE maps app.main.main and its existing startup-failure test |
| P5-D02: custom pet input surface missing | Documentation defect / P2 | RESOLVED: MOCHI.PET.SURFACE maps PetWindow construction and mouse/context events; event records are not extra buttons |
| P5-D03: obsolete partial status / missing reconciled units | Documentation defect / P2 | RESOLVED: current status, navigation, coverage, unit counts and shortcut ownership added; earlier pass outcomes retained as historical progression |
| P5-S01: F7 target identity predicate | Potential source limitation / P3 | OPEN, nonblocking for documentation: title/Qt class/Python name checks have no command-line/project-root comparison; cross-checkout protection NOT VERIFIED; source unchanged |
| P5-S02: Clipboard A/a mnemonic overlap | Potential source/platform behavior / P3 | OPEN, nonblocking for documentation: source markers verified; physical dispatch/cycling NOT VERIFIED; no reassignment |
| P5-E01: physical/native UI acceptance | Runtime-unverified behavior / P3 | NOT RUN by this gate; includes rendering, DPI, tray, hotkey timing, foreground focus and default-key resolution; no fresh physical PASS claimed |
| P5-T01: control-specific native assertions | Test coverage limitation / P3 | Existing source tests identified; direct formatting functions/fixtures do not establish every button, acknowledgement or physical route; unverified areas remain explicit |
| P5-H01: earlier GUI/Clipboard/Mochi prose | Historical issue / informational | Earlier delivery snapshots and original failed restoration/adjudication records preserved; they do not override this pinned-source inventory |

The registry preserves GUI → application/service → domain → repository/gateway
ownership. Recent is a durable read-only projection; Setup's trusted S05 manual
consent is separate from generic settings and RAM monitoring. Windows Refresh
has no acquisition connection; RAM-01A domain integration is not automatic
observation; RAM-01B and HybridB-01 are not delivered GUI capture controls.
Scripts separates catalog visibility, verified Copy and fixed execution policy;
single/pack execution does not imply a general Diagnostic Center. PR #114's
Python restoration is integrated at this source revision without rewriting
the failed Expose-only history or manufacturing fresh native acceptance.
Guide owns local topic files, not core SQLite; Mochi Close/Exit and delegated
local control remain distinct from planned recognition/provider features.

Governance audit: root AGENTS.md and Clipboard AGENTS.md retain their exact
recovered bytes. Their concise additions require registry consultation, actual
source inspection/reuse and synchronization after validated authorized changes,
while preserving source-of-truth precedence, Clipboard consent/privacy and
planned/candidate distinctions. The detailed inventory remains only here; no
duplicate maintenance policy or independent implementation authority was added.

All five author-side audit batches and the construction/action census pass.
Final fresh source/link/handler/objectName/connection/layout/shortcut/status/ID/
table/governance/history/scope checks are recorded in the external frozen review
package, bound to raw and Git-normalized file hashes and the exact saved patch.
No unresolved source coverage gap or blocking documentation finding remains.
Runtime GUI, AHK/native, Clipboard, PowerShell, database operations and full
regressions were NOT RUN as required by this documentation-only gate.

**GUI_REGISTRY_READY_FOR_INDEPENDENT_REVIEW.** This is an author readiness
statement only. Independent review has not been requested or performed, no
approval is inherited, and staging/commit/push/merge remain unauthorized.
