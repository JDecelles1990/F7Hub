# F7Hub ChangeLog

## 2026-10-03 — AltF7Hub Knowledge corpus import

Imported the supplied 31-topic YAML corpus as separate DRAFT/version-1 Knowledge articles in the local development database, preserving all 841 ordered sections and 3,089 prompts. Each article has an initial version snapshot, source metadata and a searchable FTS entry. The original article, unrelated tables and source YAML were preserved. The technician confirmed successful use in the application.

Rehearsal/live article, history, search, duplicate-prevention and integrity checks passed; malformed/duplicate-key/conflict rejection and injected snapshot-write rollback were validated on an isolated copy. This evidence is RETAINED for the source/documentation integration after unchanged-input verification. No new automated native UI or full regression run is claimed. A validated backup preceded live writes. [Data/README.md](../Data/README.md) owns the import record and limitations: local database content is not committed or automatically seeded elsewhere; no schema, application dependency or synchronization change was added.

## Slice 053 — Local Baseline Diagnostics

System → Network → Services is the fixed, code-defined **Local Baseline Diagnostics** pack (`diagnostic.pack.local_baseline`). The technician explicitly runs the pack or one approved member. Results remain in memory. Script Type describes the script; the literal execution policy grants permission. Exactly the three reviewed DIAGNOSTIC identities may execute; unknown diagnostics and all five other types are rejected.

The existing shared PowerShellService, PowerShellGateway and ServiceTaskRunner serve both run modes. A service reservation spans the entire sequential pack. Every member repeats current registration lookup, exact-byte verification, sealed preparation, immediate revalidation, trusted 64-bit PowerShell 7/token checks, separate owned job, bounded capture, contract validation and verified cleanup. Valid collection ERROR/exit 1 continues; a boundary failure aborts with partial attempted results, failure position and skipped remainder, and no aggregate collection status. Cleanup uncertainty latches both run modes blocked.

Scripts shows **Name | Type | Category | File status | Execution**. Code, Version and current metadata policy are in plain-text details. File availability and execution approval are separate; an approved missing file cannot Run. Shown/available/approved counts describe the filtered rows. Pack readiness checks its three registrations independently of search, remains advisory, and execution rechecks bytes/runtime. The pack panel names member order, local read-only scope, memory-only results and per-member limits: up to 60 seconds execution plus 5 seconds cleanup; preparation adds time. Runs cannot be cancelled. Shared pending ownership spans dispatch, runner idle-before-callback and result presentation, including stale-callback, failure, navigation and close guards.

Forward-only data migration `0011_services_snapshot_script.sql` adds exactly one enabled, uncategorized Windows Services Snapshot registration: code `diagnostic.windows.services_snapshot`, description `Collects a local read-only Windows services snapshot.`, path `PowerShell/Diagnostics/Get-ServicesSnapshot.ps1`, DIAGNOSTIC / POWERSHELL_7 / LOW / STANDARD_USER, version 1.0.0, timeout 60, structured output 1 and timestamps `2026-10-03T00:00:00.000Z`. Exact UTF-8 no-BOM CRLF SHA-256: `8a48321800e4d8147f2dd94a9d83eebedace6ac4e45b3e38c00f74d280abc347`. Case-insensitive code and separator-normalized/case-insensitive path conflicts abort atomically without version 11 recorded. Migrations 0001–0010 and the physical schema, six type enum, defaults, relationships and indexes are unchanged. No pack or result rows are created.

Validation: Database 438, PowerShell 72, GUI 210, Integration 203 PASS (196 RETAINED methods plus 7 FRESH corrected bootstrap methods; original full exit 1, correction exit 0). Other final suites exit 0, and all supervisors report zero owned survivors. Native Windows 104 assertions PASS at 1000×700/96 DPI, QTest input; real pack and individual Network, synthetic valid ERROR, invalid middle output, actual synthetic timeout containment and cleanup-quarantine scenarios. All 6 captures inspected. Physical hardware input and alternate DPI NOT RUN. Earlier failed fixture/harness/migration-count attempts remain historical evidence with bounded correction records. `native-v5-retry.md` records one accidental unchanged launch and loss of the original v3 JSON; the later v4 duplicate artifact is preserved separately. Final applicability checks bind tested inputs to the documented candidate.

The reviewed candidate received **APPROVE_WITH_NOTES**. This normal integration closes Slice 053 after post-merge verification; the historical full Integration exit 1 and native evidence limitations remain recorded above.

## 2026-10-03 — Slice 052: Controlled System Snapshot execution historical candidate

Historical Slice 052 scope, closed through PR #58 and superseded by Slice 053 above.

Added explicit execution of the reviewed Windows System Snapshot from Scripts, through a fixed non-elevated PowerShell 7 gateway with exact-byte verification, private sealed artifact, finite owned job, bounded output and strict structured-result validation. Added memory-only result presentation and callback-spanning pending guards. No migration, source diagnostic change, pack, parameter, history, ticket write or remediation. Resumed from the preserved checkpoint without restarting implementation. The historical native harness failure and polling starvation remain recorded; corrected polling completed the real diagnostic plus injected invalid-output and timeout paths. Native **43 assertions PASS**, exit 0, zero owned survivors; three 1000×700/96 DPI captures inspected. GUI **206 PASS FRESH**; Database **433**, PowerShell **51** and Integration **201 PASS RETAINED** after relevant-input comparison. Physical input and other DPI NOT RUN. Slice 052 is CLOSED through PR #58; original test evidence remains historical. Evidence is external under `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Slice-052`.

## 2026-10-03 — Slice 051: Bounded dialog completion correction

Corrected blocking review finding R1 by recalculating inline classification availability with the existing helper when Subject/Description editing opens or finishes. Completion clears its dialog reference first; there is no force-enable bypass, draft reset, layout change or service/repository change. Added clean/dirty no-op and failure/Cancel regressions, adjacent success/direct Cancel/window-close checks and checks that other blockers still disable the controls. Removed the test-side private refresh that masked the missing production transition.

The original independent review remains **30 PASS / 4 FAIL**. The four exact regression methods failed before the production change and now **4 PASS**. Fresh affected validation: **67 inline/dialog, 199 GUI and 197 Integration PASS**, exits 0 without failures/errors/skips; focused tests overlap. Database **433 PASS RETAINED** after unchanged transitive-input verification; native 1000×700/96 DPI layout evidence is RETAINED from the prior 185-assertion execution. No new native execution, physical input or extra DPI was performed. A new Description fixture expectation was corrected before one justified focused rerun; the failed attempt and prior review/fixture/layout/watchdog evidence remain historical. Unchanged Mochi shutdown/fixture-launch diagnostics remain a nonblocking follow-up; owned-process cleanup is complete. **READY_FOR_REREVIEW**, with approval/integration pending. Durable corrected manifest and report are under `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Slice-051/correction-20261003`. The original candidate entry below is historical.

## 2026-10-03 — Slice 051: Inline Priority and Type candidate

Implemented inline Priority/Type dropdowns and one explicit Apply changes action in Tickets; selection alone writes nothing. Removed the normal Edit priority/Edit type buttons and unused dialog modules, replacing their obsolete GUI integration tests while preserving individual service/repository coverage. Added one atomic classification operation with loaded priority/type/timestamp guards, strict activity advancement, conditional existing change events and authoritative reload before commit. Failure at any stage rolls back both fields.

Inline choices now use existing draft protection. Failed saves retain drafts; unrelated activity refreshes retain dirty choices and their original token. Classification pending protects duplicate submission, navigation/New Ticket/close and callback completion; committed save plus failed reads has truthful read-only recovery. Queue filters/search/page and filter exit remain intact. Compact controls and shrinkable scrollable detail tabs preserve 1000×700, including expanded Resolution. Quick Note, Status, Subject/Description and embedded New Ticket remain separate; no schema/migration change.

Native Windows validation passed with 185 assertions, exit 0 and nine inspected captures after preserved harness readiness and layout failures. Physical manual input/other DPI are NOT RUN. Final regression is 822 tests: 433 Database RETAINED after input comparison, 199 GUI and 190 Integration FRESH, all exit 0 without test failures/errors/skips. Earlier test-fixture, timeout and native/offscreen layout failures are preserved. An unchanged MochiGateway shutdown diagnostic after Integration completion is recorded as an out-of-scope nonblocking follow-up. **READY_FOR_REVIEW**, not integrated or CLOSED. Regression evidence and candidate manifest are external under `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Slice-051`; independent review and integration remain pending.

## 2026-10-02 — Slice 050: Consolidate creation into Tickets

Renamed the user-visible Saved Tickets workspace to Tickets and removed the separate New Ticket primary navigation/menu/toolbar action and Ctrl+N. + New Ticket now hosts the existing TicketCreateWidget inside the right pane with a visible queue and pinned Cancel. Existing activity-draft confirmation protects entry; cancellation writes no ticket and restores prior detail/tab and queue state.

Creation reuses the unchanged service/repository and initial activity transaction. Success reopens authoritative saved detail and refreshes/selects in the retained queue view. Save failures preserve the form; committed creation plus failed reads remains acknowledged with read-only reopen/Refresh recovery. Local pending/generation guards cover callback gaps, duplicates, stale reads and unsafe close. Quick Note has no active old-ticket identity during creation and is restored for saved detail. Native Windows 1000×700/96 DPI validation passed; captures were inspected, using native Qt QTest events and injected service failures. Physical input/additional DPI were not run.

No schema, migration, service/repository, Knowledge Base or inline-edit redesign. Recovered and finalized on 2026-10-03 at **READY_FOR_REVIEW**: FRESH 10 boundary tests and 177 Integration tests PASS; RETAINED 199 GUI, 423 Database and corrected native evidence PASS after input verification. Historical failures remain preserved. Candidate remains unstaged/uncommitted; independent review and integration are pending. Slice 049 closure is established by its external report and PR #54 at fbb3340; earlier dated candidate entries remain historical.

## 2026-10-02 — Slice 049: Quick Note

Implemented the first bounded Tickets UX increment: compact persistent Quick Note, editor-scoped Ctrl+Enter, explicit Internal default, blank/unloaded guards, captured submission values, pending protection across worker callbacks and focus recovery. Note type and the existing optional Author remain retained in session. Save failures preserve inputs; committed notes remain acknowledged if subsequent detail/queue reads fail, with read-only retry.

FRESH focused GUI 15 PASS and ticket Integration 49 PASS overlap the full suites. FRESH full GUI **199 PASS** and Integration **163 PASS**, exit 0, no failures/errors/skips. Database **423 PASS RETAINED**, with accessible completion evidence and 82 unchanged relevant inputs independently verified. Native Windows 1000×700/96 DPI: **90 assertions PASS**, process exit 0, six captures inspected. Initial native harness dispatch/connection-cleanup errors and a process-liveness reporting correction are retained externally; candidate code did not change during those corrections. Physical manual input and additional DPI are NOT RUN.

No service/repository/schema, lifecycle, navigation rename, author persistence, note retrieval or Knowledge Base change. Work remains unstaged/uncommitted at **READY_FOR_REVIEW**. Evidence is under `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Slice-049`; independent review is pending. One policy-rejected synthetic temporary-fixture cleanup is a nonblocking external note. Slice 048 closure is established by PR #53 and its verified external closure report; older pending-review prose is historical.


## 2026-10-02 — Slice 048 implementation candidate

Implemented **Windows Network Configuration Snapshot** as one local, read-only, parameterless PowerShell 7 script and one enabled registry/checksum row in migration 0010. Added its targeted CRLF rule and deterministic contract, rollback, byte-integrity and existing catalog/management integration coverage. Production Python/GUI/service/repository behavior and physical schema remain unchanged; F7Hub cannot execute PowerShell.

Full regression: Powershell 19 PASS (RETAINED), Database 423 PASS (RETAINED), Gui 197 PASS (RETAINED), Integration 157 PASS (FRESH), all exit 0 with no failures/errors/skips. RETAINED standard-user standalone collection and native Windows Scripts search/select/details/exact-copy passed at 1000×700, 96 DPI, with observable idle, one inspected capture and clipboard restoration. The table elides the long name; the full details name/metadata remain visible. Recovery found a completed 157-test Integration failure from one stale nine-migration assertion; that test-only correction required one supervised full Integration rerun. The earlier incomplete confirmation-dialog attempt and all failure records are preserved; no identical unchanged native rerun was performed.

Candidate is READY_FOR_REVIEW on `feature/network-snapshot-s048` from `dab8f25d65a505c6a7943b15335c9fb1c7984c92`, unstaged/uncommitted. External manifest/results/report are under `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/Slice-048/implementation-20261002`. Independent approval and integration remain pending. Historical predecessor wording below retains its dated meaning; verified Slice 047 closure supplies the baseline.


## 2026-10-02 — Mochi Slice 002 implementation candidate

Implemented the approved F7Hub startup, modeless Mochi controls, persistent local controller, bounded IPC, singleton runtime, Wave/greeting and visibility/controller-loss recovery contracts in an isolated feature worktree. Candidate remains unstaged/uncommitted pending independent review. No merge, Slice 003, schema, AHK launcher, PowerShell execution, capture product feature or persisted preferences are included. Exact tests, native evidence and limitations are recorded in the external Slice 002 implementation report; this entry grants no integration authorization.

> Document: `Docs/18_ChangeLog.md`  
> Project: F7Hub  
> Purpose: Record meaningful completed changes to F7Hub architecture, documentation, schema, behavior, tooling and releases.
> Related Documents: `16_Roadmap.md`, `17_Todo.md`, `19_DocumentationIndex.md`

---

## AltF7Hub topic contract — Slice 047 candidate

**2026-10-02 — Slice 047: stable topic documentation and Ctrl+F.** Added a complete 34-topic [catalog](../AutoHotkey/Troubleshooting_Sections/TopicCatalog.md), explicit A/S/H/W cycle order, interview keys 1–5, curated list/title/automatic-heading colors and keyword references for macOS, Azure VM and Windows 365. Main-guide Ctrl+F focuses Search with its caret after the current query; opacity now supports 60–100%. Runtime routing policy is separate from historical filename compatibility. Future classification aliases remain documentation only; the current show/focus IPC is unchanged.

Slice 046 is CLOSED; PR #47 merged into authoritative main `bb81a2c2dd9851c2c80d42549fc078309e02be72`. Slice 047 was reconstructed from that base using only its authorized changes after CHANGES_REQUIRED for mixed-file scope. The corrected candidate is READY_FOR_REVIEW, unstaged and uncommitted; independent review and integration remain pending. Slice 047 is neither integrated nor closed. Historical ChangeLog entries retain their dated meaning.

Validation, the new exact manifest and implementation handoff are external under `%LOCALAPPDATA%\F7Hub\CodexCheckpoints\Slice-047`. The previous 17-path aggregate `b9e08c6bacc6b4819a72e873eb2c29385b9e88de0dcb9da850d4fbf0dd51e925` is historical rejected evidence only and supplies no integration approval. The user's successful native acceptance is RETAINED after input comparison; it is not fresh automated validation.

## AltF7Hub Guide — Slice 046

**2026-10-01 — Slice 046: AltF7Hub integration and keyboard navigation.** Integrated the supplied reference guide under the shared AHK v2 entry, retained standalone access through a bounded request wrapper, and added the Python toolbar/File action through the existing worker/service boundary. Topics wrap with Up/Down; Left/Right change opacity by 1% and support repeat, with focus exclusions, bounds and saved settings. Show/focus preserves editor content, ticket drafts and topic selection/scroll. Concurrent clients are serialized; unconfirmed dispatched requests do not trigger a keyboard toggle.

Validation executed on 2026-10-01: GUI 181 PASS, Integration 156 PASS, isolated guide 162 checks PASS, native shared-host 29 checks PASS, request-failure 7 checks PASS, native Python/guide/editor 13 checks PASS, and existing F7 launcher and magnetic-follower suites PASS. On resume, GUI/Integration and AHK regression evidence is retained after verifying unchanged relevant inputs; native Python/guide/editor checks were freshly rerun and all 18 current AHK files passed fresh v2.0.26 parser validation. Commands, candidate identities, result files and inspected native captures are under `%LOCALAPPDATA%\F7Hub\CodexCheckpoints\Slice-046`. Native checks use isolated data at 96 DPI; repeated-key messages are automated evidence, not a claim of physical hardware acceptance or a live Teams/camera test.

Status: **READY_FOR_REVIEW**, unstaged/uncommitted. Existing topics, backups, settings and prior evidence are preserved. Ticket-driven topic selection remains deferred. No schema, dependency, PowerShell execution or Startup-entry change.

**Slice 045 closure reconciliation:** its reviewed candidate subsequently integrated through PR #46 at `15c61b5`; prior pending-review wording is superseded by its verified external closure report.

---

# 1. Purpose

This file answers:

> What meaningfully changed, when did it change, and what was validated?

It is historical. It is not a roadmap, todo list, requirements document or substitute for source-control history.

```text
16_Roadmap.md
→ future direction

17_Todo.md
→ current actionable work

18_ChangeLog.md
→ meaningful completed changes
```

---

# 2. Status Discipline

Documentation changes, implementation and validation are reported separately.

```text
Documentation status
→ DRAFT / REVIEW / APPROVED / DEPRECATED / ARCHIVED

Implementation status
→ PLANNED / IN PROGRESS / IMPLEMENTED / VERIFIED / DEFERRED / REJECTED / NOT VERIFIED

Test or validation status
→ PASS / FAIL / NOT RUN / BLOCKED
```

No entry may imply that documented target architecture is implemented or verified without repository and test evidence.

---

# 2026-10-01 — Slice 045: Manual Scripts Catalog Text Search

Added optional bound literal-substring catalog search across name, code and description, retaining enabled/category predicates and deterministic unique results. Type/NUL validation occurs before database access. Scripts adds Search/Enter/Clear, separate draft/applied state, request query capture, loading/copy guards, selection reconciliation, distinct empty messages and recoverable failure feedback. Navigation and filtered management reload preserve the applied query; committed management writes are not repeated after refresh failure. Existing verified-copy and registration/visibility behavior remain intact. No schema, migration, dependency or PowerShell source changes.

Fresh Database **418 PASS**, GUI **178 PASS**, Integration **148 PASS** (744 full regression total), all exit 0 with no failures, errors or skips. Focused **32 PASS** and affected **46 PASS** overlap the full suites. Native Windows **PASS** at 1000×700 with observable worker/callback idle; six captures inspected. Durable suite/native records and manifests are outside the repository under `%LOCALAPPDATA%\F7Hub\CodexCheckpoints\Slice-045\`. This records historical implementation validation. Slice 045 subsequently passed independent review and closed through PR #46 at `15c61b5c410d0d5dffe5ac6c5ac01a4b6dd960f7`; its verified external integration/closure report establishes the completed lifecycle.

---

# 2026-10-01 — Vertical-slice-delivery skill v0.3

Updated the existing delivery skill and report templates with reproducible candidate manifests, durable long-suite and native GUI result records, explicit evidence provenance, correction drift matrices, carry-forward notes, stale handoff authority, compact prompts, risk-focused review, and separate authoritative-mutation versus refresh outcomes. Recovery now checks durable results and running operations before repeating expensive validation; PLAN consumes the preceding integration/closure report and unresolved notes without adopting them automatically. The 17 lifecycle states and readiness/approval/integration/closure distinctions are preserved. This is skill maintenance; Slice 045 and application behavior are unchanged. Structural and behavioral validation evidence is recorded in the external Skill-v0.3 delivery reports; this entry does not claim integration or real token-exhaustion testing.

---

# 2026-10-01 — Slice 044: Script registration and local management

Added **Manage scripts…** with scoped disabled-row inspection, registration of existing readable approved-folder `.ps1` references and guarded enable/disable. New rows retain table defaults and null category/checksum; writes reload before commit, reject stale state and preserve integrity approval metadata. Shared-runner dialogs prevent duplicate writes, retain failed registration input, ignore dismissed reads and distinguish saved changes from failed refreshes. Copy Script keeps its existing service integrity boundary and clipboard protection. No schema, migration, dependency or PowerShell source change was added. Clarified reviewed checksum metadata versus approval UI/workflow in Database architecture.

Fresh focused **40 PASS**; full Database **409 PASS**, GUI **174 PASS**, Integration **145 PASS** (728 total), all exit 0. Native Windows at 1000×700 passed keyboard registration/toggling, busy and dismissal guards, error/retry, truthful post-save refresh failure and clipboard protection; six captures were inspected. The candidate remains unstaged and uncommitted for independent read-only review.

The initial independent review subsequently required a Windows readability correction: metadata inspection could report AVAILABLE when NTFS denied an actual read. Registration and Enable now prove read access with a binary open and one-byte read before writing; empty readable files remain valid, denied access leaves the database unchanged, and Disable still works while unreadable. Source and checksum/copy semantics are unchanged. The corrected candidate passed fresh focused **46**, Database **414**, GUI **174** and Integration **146** tests (734 full regression total), all exit 0. Fresh native NTFS rejection/recovery and the full native workflow passed; eight captures were inspected, fixture ACLs restored exactly and temporary data removed. It is READY_FOR_REVIEW for independent rereview, without staging or integration.

---

# 2026-09-30 — Slice 043: Secure Script Copy to Clipboard

Added a targeted CRLF checkout rule and guarded data migration 0009 with the reviewed exact-byte SHA-256 for Windows System Snapshot. ScriptService now reads one current byte buffer after enabled lookup and approved-path validation, checks the registry hash, and strictly decodes only matching bytes. ScriptWorkspace adds asynchronous **Copy Script**, current-selection protection and safe feedback; only the GUI writes raw source to the Qt clipboard. Full Database 398, Integration 143 and PowerShell 6 passed during recovery; full GUI 166 and native Windows evidence were retained after unchanged relevant inputs were verified. Slice 043 subsequently merged through PR #44 at `b4d46ef7af6936c5ef3c34686040691222115f31`; its prior pending-review wording is historical. F7Hub does not execute, paste or transmit PowerShell.

---

# 2026-09-30 — Slice 042: First Production PowerShell Diagnostic Script

Added one PowerShell 7 diagnostic, `Get-SystemSnapshot.ps1`, for a local read-only Windows OS, uptime, memory and fixed-drive snapshot. It emits one structured JSON result, with safe ERROR and partial WARNING paths. Data migration `0008_system_snapshot_script.sql` installs exactly one enabled, uncategorized `Windows System Snapshot` registry row; the table's default remains disabled and its checksum was initially null. The existing Scripts workspace displays the file as AVAILABLE when present, with no application execution control or production Python change. Standalone PowerShell validation runs only in test tooling. Slice 042 was subsequently reviewed and merged through PR #43; its initial pending-review wording is historical. Slice 043 adds the separate checksum approval for copying.

---

# 2026-09-30 — Slice 041: Read-Only Scripts Catalog UI

Application bootstrap now composes the existing ScriptRepository and ScriptService with the resolved database path and project root. The existing MainWindow stack, File menu and toolbar expose **Scripts**. ScriptWorkspace loads enabled entries through ServiceTaskRunner, shows an intentional empty state, four text file statuses and plain-text metadata, and supports selection-preserving manual Refresh and safe retry after a failed read. The shared runner and close guard prevent concurrent loads and page destruction during work. The GUI does not query SQLite, validate paths, read `.ps1` contents or execute PowerShell. No schema, migration, production seed, registry management or execution control was added.

Focused, full regression and native Windows evidence were recorded in the Slice 041 handoff. Slice 041 was subsequently reviewed and merged through PR #42; its original candidate-state wording is historical.

---

# 2026-09-30 — Slice 040: PowerShell Script Registry Foundation

Migration `0007_script_registry.sql` adds the metadata-only `scripts` table with unique case-insensitive code and relative path, constrained documented metadata, nullable shared-category foreign key, `is_enabled DEFAULT 0`, and enabled/name plus category indexes. The production registry is empty. `ScriptRepository` offers enabled-only list and code lookup; explicit disabled inspection is internal. Catalog reads exclude rows linked to categories outside `SCRIPT` scope. `ScriptService` returns metadata with a separate `AVAILABLE`, `MISSING`, `INACCESSIBLE` or `INVALID_REFERENCE` file status. Path inspection limits `.ps1` references to Diagnostics, Reports and Modules beneath the supplied project root and rejects Windows path escapes and symlink escapes. It reads no script contents and launches no PowerShell process. Approval, registration, execution, parameters, history and GUI remain future work.

Validation details and candidate identity are recorded in `Status/CURRENT_STATE.md`. The candidate remains unstaged and uncommitted for independent read-only review.

---

# 2026-09-30 — Slice 039: Search Saved Tickets by Note Text

Saved Tickets now submits its existing literal query against subject, description and note text. TicketService and TicketRepository add an optional boolean `include_notes` that defaults to false, retaining subject-only behavior for existing callers. The repository uses a bound correlated `EXISTS` so multiple matching notes still return one ticket and all existing filters, newest-updated ordering and paging remain intact. The workspace uses its existing worker and post-save refresh: a committed note can add its ticket to applied results without submitting later draft search text. No note snippet, schema, migration, index, dependency or new search subsystem was added.

Focused ticket-read **33 PASS** and ticket-workspace **43 PASS**; affected note-service **17 PASS**, company-context **5 PASS** and MainWindow **8 PASS**. Fresh Database **377** + GUI **156** + Integration **140** = **673 full regression PASS**, all exit 0. Read tests include literal metacharacters, all four flag combinations, filter grouping, ordering, paging, no duplicate rows, unchanged SQLite content, integrity, foreign keys and an index-backed correlated query plan. Native Windows Qt at 1000×700 passed Enter search, combined filters, note-save membership, safe failure, retry and Clear on an isolated database; all five final Saved Tickets captures were inspected. The candidate remains unstaged and uncommitted for independent review.

---

# 2026-09-29 — Slice 038: Manual SQLite Database Backup

The File menu now offers **Back up database**. Bootstrap supplies the active database path to DatabaseBackupService; the shared worker keeps the GUI responsive. A dedicated read-only SQLite connection copies the live source with the online backup API to a temporary file under `%LOCALAPPDATA%\F7Hub\Backups`. An independent reopen must pass integrity and foreign-key checks before a no-overwrite rename publishes a unique `.db` file. Success shows the path and local-drive limitation; failure shows bounded feedback and leaves existing backups intact. The backup contains SQLite data only; no restore, scheduling, retention, schema, migration, dependency or external transfer was added.

The initial pre-review candidate passed 666 full tests but independent review found a false concurrent-snapshot assertion and missing foreign-key connection configuration. The 2026-09-30 correction enables foreign keys on the source, destination and validation connections and verifies a coherent snapshot while allowing either inclusion or exclusion of a racing committed write. Corrected focused **26 PASS**, affected **39 PASS**, and fresh Database **374** + GUI **156** + Integration **137** = **667 full regression PASS**, all exit 0. Focused tests cover the three connection settings, source-write preservation, missing source, destination and validation failures, foreign-key rejection, collision preservation and WAL concurrency. Native Windows 1000×700 success and synthetic-failure workflows passed again on an isolated populated database; four corrected-candidate captures were inspected. The published snapshot reopened with `integrity_check = ok`, zero foreign-key violations and the fixture company present. The candidate remains unstaged and uncommitted for independent rereview.

---

# 2026-09-29 — Slice 037: Safe Application Logging at Startup

The application entry point now configures one `f7hub` logger handler before bootstrap. A UTF-8 rotating file at `%LOCALAPPDATA%\F7Hub\Logs\Application\f7hub.log` is capped at 1 MiB with two backups. If file setup fails, a fixed type-only stderr warning precedes an application-owned stderr handler and startup continues. The process root logger is unchanged and F7Hub records do not propagate to it while configured. Reconfiguration replaces and closes only the prior F7Hub-owned handler; exit closes the active handler and restores prior level/propagation where still owned. Successful startup records fixed text. Bootstrap failure records fixed text and exception type only, retaining the existing safe dialog and exit code. This protects the current approved startup messages; future callers remain responsible for safe content.

Focused **9 PASS**, affected **15 PASS**, and fresh Database **362** + GUI **154** + Integration **136** = **652 full regression PASS**, all exit 0. Isolated tests cover path, UTF-8, 1 MiB/two-backup rotation, root isolation, owned-handler replacement/closure, safe synthetic-secret failure content and deterministic stderr fallback. Native Windows startup reached observable idle at 1000×700 and the failure dialog preserved its safe text; both external captures were inspected. No SQLite schema, migration, dependency, repository behavior or database content changed. The candidate remains unstaged and uncommitted for independent review.

---

# 2026-09-29 — Slice 036: Recent Tickets for a Saved Ticket's Company

Saved Tickets now has a Company tab for the loaded ticket. **Load recent tickets** reads up to 20 most recently updated tickets using the persisted company ID and the existing ticket list service/repository. The query binds an optional company predicate and retains existing filters, ordering and paging. The tab has its own ticket model, uses the shared worker, rejects stale async results after context changes, and opens a result through the existing draft-confirmed ticket path. No-company and read-failure states are explicit; same-context results survive failed refresh. Inactive company names remain readable. The main queue and its page, filters and search state are unchanged. No schema, migration, index, dependency or new service was added.

Focused **35 PASS**, affected **105 PASS**, and Database **362** + GUI **154** + Integration **131** = **647 full regression PASS**, all exit 0. Isolated SQLite checks cover validation, binding, predicate composition, ordering, top-20 bounds, paging, unchanged data, integrity and foreign keys. Native Windows Qt at 1000×700 passed Company-tab load, failure/retry, draft-discard Cancel, related-ticket opening, inactive and no-company states; all eight external captures under `LOCALAPPDATA/F7Hub/CodexEvidence/Slice-036` were inspected. The candidate remains unstaged and uncommitted for independent review.

---

# 2026-09-28 — Slice 035: Search Saved Tickets by Subject or Description

Saved Tickets now searches a submitted literal phrase in either the subject or optional description using the existing paged SELECT. `include_description=False` preserves the subject-only service/repository contract for default callers; the workspace opts in. The same escaped pattern is bound to both columns inside a parenthesized OR predicate, combined with Status, Priority and Type. Search/Enter/Clear, draft and applied text, paging, exact-number opening, busy protection and failed-read retry continue through the existing worker. A description edit can remove a matching row while the updated detail stays open and the save remains acknowledged. No schema, migration, index, FTS object or dependency changed.

Focused **68 PASS**, affected **85 PASS**, and Database **360** + GUI **154** + Integration **126** = **640 full regression PASS**, all exit 0. Isolated SQLite checks cover default compatibility, optional description matches, NULL, literal metacharacters, combined filters, ordering, paging, one row per ticket, unchanged data, integrity and foreign keys. Native Windows Qt at 1000×700 passed description-only search, Enter, paging, failed Search/Refresh recovery and description-edit result exit; all eight external captures were inspected. The candidate remains unstaged and uncommitted for independent review.

---

# 2026-09-27 — Slice 034: Search Saved Tickets by Subject

Saved Tickets now accepts a submitted literal subject substring. TicketService validates and trims optional text; TicketRepository binds a LIKE predicate with an explicit escape character so percent signs, underscores and backslashes remain literal. Search composes with Status, Priority and Type in the existing ordered, paged SELECT. The workspace separates draft text from the submitted query, offers Enter/Search/Clear, retains previous results and open detail on failed reads, and retries the requested query/page through Refresh. A committed subject edit can remove its row from active search while its new detail remains open. No schema, migration, index, FTS, dependency or other subsystem changed.

Focused ticket tests passed 65, affected tests 82, and full Database 358 + GUI 154 + Integration 125 = 637 regression tests passed, all exit 0. Database coverage includes literal wildcard and escape-character matches, lookalike exclusions, filter composition, stable paging, no writes and integrity. Worker-backed GUI coverage includes draft/submitted state, Enter/Search/Clear, filters, paging, exact-number opening, failure/retry, busy protection and subject-edit search exit. Native Windows passed at 1000×700 using isolated SQLite; six captures were inspected for input/action fit, usable queue/detail, failure recovery and the updated detail after result exit. The candidate remains unstaged and uncommitted for independent review.

---

# 2026-09-27 — Slice 033: Edit a Saved Ticket Type

Saved Tickets now shows the loaded ticket type and offers Edit type using the ordered `TICKET_TYPES` domain. Exact loaded type and update time are checked before no-op. A real edit atomically changes only type and a strictly later activity timestamp, writes one `TYPE_CHANGED` event without type values, and reloads before commit. Failed update, event or reload rolls back. A changed ticket may leave the active Type queue while its updated detail stays visible. Later read failures retain the committed-save acknowledgment and retry path without another update. The five detail actions remain usable in a two-row grid at 1000×700.

The focused ticket/MainWindow set passed **65**, affected set **76**, and full Database **356**, GUI **154**, Integration **121** = **631 full regression PASS**, all exit 0. Isolated SQLite tests cover all type values and transitions, invalid/missing/stale/no-op requests, same-millisecond advancement, rollback, unrelated data and links, integrity and foreign keys. Worker-backed integration covers dialog state, committed-save read failures and retry, filters, page and draft retention, and Type-filter exit. Native Windows `windows` platform reached observable idle at 1000×700; five captures of actions, dialog, filter exit, post-commit failure and recovery were inspected without observed clipping or overlap. No schema, migration, index, dependency, generic editor or unrelated subsystem changed. The candidate remains unstaged and uncommitted for independent review.

---

# 2026-09-27 — Slice 032: Edit a Saved Ticket Description

Saved Tickets now offers Edit description for a loaded ticket. The multiline plain-text dialog starts with the loaded value or empty for NULL, retains draft text after failed saves, and blocks duplicate writes and unsafe close during a write. The service reuses creation's optional-text normalization: surrounding whitespace is trimmed, internal line breaks remain, and blank input clears to NULL. Exact loaded description and update time are checked before no-op. A real edit atomically updates only description and a strictly later `updated_at`, adds one `DESCRIPTION_CHANGED` event without description text, and reloads before commit. Failed update/event/reload rolls back. Later detail or queue read failures retain the saved acknowledgment and retry path without another write.

Focused **50 PASS**, affected **66 PASS**, Database **352 PASS**, GUI **153 PASS**, Integration **116 PASS** = **621 full regression PASS**, all exit 0 on their completed runs. Database evidence was retained after a GUI-only layout correction because its service, repository, tests, schema and other Database inputs were unchanged; focused, affected, GUI and Integration checks passed after that correction. The initial GUI run found that four detail actions in one row forced the main window to 1058 pixels wide; a two-row grid restored the 1000×700 layout. The three failing layout checks and the complete GUI suite passed after that correction. Native Windows `windows` platform reached observable idle at 1000×700; the multiline dialog, successful save, post-commit validation-error feedback and retry captures were opened and inspected without observed clipping or overlap. No migration, schema, index, dependency or other ticket edit changed. The candidate remains unstaged and uncommitted for independent review.

---

# 2026-09-27 — Slice 031: Edit a Saved Ticket Priority

Saved Tickets now offers Edit priority for a loaded ticket using the existing four-value priority domain. A valid change compares the loaded priority and exact update time before no-op, atomically updates only priority and a strictly later `updated_at`, adds one `PRIORITY_CHANGED` event without priority values, and reloads before commit. Missing/stale/invalid/no-op requests write nothing; update, event and reload failures roll back. The dialog retains selection after failure and blocks duplicate writes and close during a write. After commit, detail and queue refresh keep the save acknowledged if a later read fails; a ticket may leave the selected priority-filtered queue while its saved detail remains open. No schema, migration, index, dependency or other ticket edit changed.

Final-candidate focused **42 PASS**, affected **58 PASS**, full Database **349 PASS**, GUI **153 PASS**, Integration **111 PASS** = **613 PASS**, all exit 0. Isolated SQLite checks cover every valid priority pair, stale-before-no-op, same-millisecond advancement, rollback, unrelated data/relationship preservation, integrity and foreign keys. Integration covers Cancel, selection retention, busy protection, committed-save read failures and retry without a second write, and active-filter exit. Native Windows at 1000×700 reached observable idle; dialog, post-commit failure and filtered-detail captures were opened and inspected without observed overlap. The candidate remains unstaged and uncommitted for independent review.

---

# 2026-09-27 — Slice 030: Edit a Saved Ticket Subject

Saved Tickets now offers Edit subject beside Reload ticket. The dialog prefills the loaded subject, preserves entered text on validation or save failure, blocks duplicate writes and closing during a write, and instructs a stale editor to reload. The service validates the exact loaded subject and update timestamp before a no-op decision. A real edit atomically changes only subject and a strictly later UTC `updated_at`, adds one `SUBJECT_CHANGED` event without subject text, and reloads before commit. The dialog closes only after committed success; later detail or queue read failures still acknowledge the save and give a retry path. No schema, migration, index, dependency or other editable field changed.

Initial-candidate validation before the first independent review: focused **33 PASS**, affected **49 PASS**, full Database **345 PASS**, GUI **153 PASS**, Integration **106 PASS** = **604 PASS**, all exit 0. Isolated SQLite tests cover normalization, no-op, missing/stale state, same-millisecond advancement, rollback of update/event/reload failures, preservation of unrelated fields and relationships, integrity check and foreign-key check. Native Windows `windows` platform reached observable idle at 1000×700; dialog and post-save captures were opened and inspected with readable controls and feedback. Changes were unstaged and uncommitted.

Independent review found that a `TicketValidationError` during post-commit queue refresh could replace the committed-save acknowledgment. The queue failure callback now preserves caller-supplied success context and Refresh guidance for every error category, while still showing safe validation detail; ordinary queue-read error feedback is unchanged. Corrected-candidate validation: focused **34 PASS**, affected **50 PASS**, full Database **345 PASS**, GUI **153 PASS**, Integration **107 PASS** = **605 PASS**, all exit 0. Integration tests cover RuntimeError, TicketValidationError and TicketReadError after commit, one write per edit, retry without a second write, pre-commit save failure and ordinary queue validation failure. Fresh native Windows 1000×700 captures show the saved acknowledgment, refresh failure and retry text together, then the recovered queue after Refresh. Independent rereview remains pending; the 15-path candidate is unstaged and uncommitted.

---

# 2026-09-27 — Slice 029: Saved Tickets Type Filter

Saved Tickets now filters its read-only queue by All types, Incident, Service request, Problem or Task. The service validates the canonical stored type before querying; the repository binds Type with Status and Priority in one query while preserving ordering and paging. Filter changes start at page 1. Refresh, paging and exact-number opening retain all three selections; failed reads keep prior rows, detail and drafts for requested-page retry. No schema, migration, index, write or dependency changed.

Fresh candidate validation: focused **25 PASS**, affected **41 PASS**, full Database **341 PASS**, GUI **153 PASS**, Integration **102 PASS** = **596 PASS**, all exit 0. Real SQLite content was unchanged by filtered reads, with integrity and foreign-key checks passing. Native Windows reached idle with one Open, High Service request ticket at 1000×700; the capture was opened and inspected without observed clipping or overlap. The candidate remains unstaged and uncommitted for independent review.

After independent review requested a correction, the Type selector now iterates the single ordered `TICKET_TYPES` vocabulary instead of enumerating a local copy. The integration test verifies every authoritative type appears once and All types maps to `None`. Focused **25**, affected **41**, Database **341**, GUI **153**, and Integration **102** all passed again on the corrected candidate. A fresh native Windows 1000×700 capture was inspected after observable idle. Independent rereview was pending at that handoff; Slice 029 was subsequently merged through PR #30 at `cdd49fa`.

---

# 2026-09-27 — Slice 028: Saved Tickets Priority Filter

Saved Tickets now filters its read-only queue by All priorities, Critical, High, Medium or Low, composed with Status. The optional service argument reuses the existing priority vocabulary; the repository binds both values and preserves newest-updated ordering and paging. Filter changes start at page 1; Refresh, paging and exact-number opening retain selections. Failed reads keep prior rows, detail and drafts for retry. No schema, migration, index, write or dependency changed.

Fresh final-candidate validation: focused **22 PASS**, affected **38 PASS**, full Database **340 PASS**, GUI **153 PASS**, Integration **100 PASS** = **593 PASS**, all exit 0. An isolated SQLite dump was unchanged across filtered reads, integrity and foreign-key checks passed, and a native Windows 1000×700 High/Open capture was opened and inspected. An initial full GUI run found the added selector widened the window to 1176px; placing Priority on its own row resolved this, and the affected layout checks and full GUI suite passed on the corrected candidate. This candidate remains unstaged and uncommitted for independent review.

---

# 2026-09-26 — Slice 027: Open a Saved Ticket by Number

Saved Tickets now opens an exact ticket number through the existing case-insensitive repository lookup and authoritative detail read. Enter and Open number share one asynchronous action. Blank input issues no query; missing/read-failure/disappearing-ticket and cancelled draft-discard paths preserve current detail and activity drafts. The entered number, queue page and status filter remain in place. Lookup is read-only. No new exception hierarchy, repository query, schema, migration or dependency was added.

Candidate validation: focused 19 PASS; affected ticket set 35 PASS; full Database **339 PASS**, GUI **153 PASS**, Integration **98 PASS** = **590 PASS**, all exit 0. A real SQLite dump was unchanged across lookup. Native Windows MainWindow reached idle and passed button/Enter lookup at 1000×700; its capture was opened and inspected. Candidate remains unstaged and uncommitted for independent review.

---

# 2026-09-26 — Slice 026: Current Knowledge Article Dates

The Knowledge detail now shows the current article's persisted Created and Last updated values below Version, using the existing authoritative record. Values are displayed exactly without timezone conversion. Empty, missing and failed detail clears the line. No query, service API, database write, schema change, migration or dependency was added.

Fresh candidate validation: focused GUI and real-SQLite checks passed; Database **336 PASS**, GUI **153 PASS**, Integration **95 PASS** = **584 PASS**, all exit 0. A native Windows 1000×700 MainWindow capture was opened and inspected; the date line and body were readable. The candidate remains unstaged and uncommitted for independent review.

---

# 2026-09-26 — Slice 025: Read-only All Selected Knowledge Tags

The existing tag choice dialog now offers Any or All for two or more selected global tags. All mode requires every selected current tag relationship in both normal lists and FTS results; zero/one choices collapse to the existing modes. Service and repository validation reject invalid modes before reads. Category/Status composition, ordering, MATCH/bm25 ranking, one row per article, executed-query state, refresh reconciliation and Ticket Open Article reset remain intact. No schema, migration, index, FTS object, tag write or dependency changed.

Fresh candidate validation: Database **336 PASS**, GUI **151 PASS**, Integration **94 PASS** = **581 PASS**, all exit 0. Query-only and unchanged-dump checks, integrity and foreign-key checks passed. Native Windows 1000×700 MainWindow and dialog captures were opened and inspected after applying All of two tags; controls and detail remained visible. Candidate is unstaged/uncommitted for independent review. Custom expressions and restore/revert remain deferred.

---

# 2026-09-26 — Slice 024: Read-only Any Selected Knowledge Tags

Added a cached-choice Tag filter dialog for Any of selected global tags. Zero and one choices use existing All/specific modes; multiple choices filter current Knowledge lists and FTS results through validated, bound IDs in a correlated `EXISTS`. Category/Status composition, list order, MATCH/bm25 ranking, one-row-per-article behavior, Clear Search, Ticket Open Article and authoritative refresh are preserved. Current article records include stable tag IDs for reconciliation. No schema, migration, index, FTS object, tag mutation or dependency changed.

Validation on the isolated Slice 024 candidate: Database **334 PASS**, GUI **146 PASS**, Integration **93 PASS**, total **573 PASS** with zero failures. Native Windows MainWindow 1000×700 and selection dialog captures were inspected after applying two tags; controls and detail remained visible without clipping. The branch remains unstaged and uncommitted for independent review. AND/expression filtering and restore/revert remain deferred.

---

# 2026-09-22 — Slice 023: Manual Knowledge Filter-Reference Refresh

Added one compact, accessible **Refresh filters** control to the existing Knowledge Category/Status/Tag row. One activation submits exactly one active-category read and one global-tag read through the existing independent runners. Successful sources replace dynamic choices; failed sources keep their cached options and selection with safe, retryable source-specific feedback. Duplicate activation is blocked and existing `filter_loading` close protection remains sufficient.

Static modes and valid specific IDs survive refresh; renamed choices display their new labels. An inactive/deleted selected category resets only Category, and a deleted selected tag resets only Tag. Coordination waits for both reads and issues no article query when selections remain valid or exactly one authoritative list/search request when either/both reset. Active search reuses the last executed query while preserving unsubmitted input. No repository, service, database, migration, schema, FTS, AHK, PowerShell or dependency change was made.

Validation: focused Slice 023 set 27 PASS; full Database 332, GUI 140 and Integration 92 = **564 PASS**, zero failures/errors/skips. Isolated real-SQLite before/after dumps proved refresh and reconciliation reads write nothing; `integrity_check=ok` and foreign-key violations=0. Native Windows representative set: 6 PASS. Six actual 1000×700 MainWindow captures covering idle, busy, updated options, partial failure, unavailable reset and active-search reconciliation were manually inspected with no clipping, forced oversize, overlap, hidden control or broken detail view. Work remains unstaged/uncommitted for independent review.

---

# 2026-09-22 — Migration Checksum Portability

Corrected raw-byte checksum failures across LF/CRLF checkouts. Discovery now hashes canonical bytes formed by replacing only CRLF pairs with LF and executes pending SQL decoded from those same bytes. New history records use the canonical hash. Existing records accept only canonical LF, reconstructed CRLF, or exact-raw hashes derived from the current migration source; no global allowlist or historical-row rewrite is used.

Preserved strict UTF-8 decoding, BOM checksum identity, lone CR, all other whitespace/content, version/name/order validation, and per-migration transaction/rollback behavior. Unknown checksums still fail before pending execution. All six migration SQL files remain byte-for-byte unchanged. No schema, migration, dependency, Git configuration, attributes, AHK, or GUI behavior change was made.

Validation: 9 focused portability tests PASS; 80 migration tests PASS; full Database 332 PASS (17.912s), GUI 128 PASS (119.560s), Integration 91 PASS (451.043s). Full regression totals 551 tests with zero failures, errors, or skips; focused runs overlap the full Database suite. Tests used `C:/Dev/F7Hub/.venv/Scripts/python.exe -B` with PYTHONPATH pointing to this worktree because this checkout has no local virtual environment. The existing development database was opened read-only/query-only: LF and CRLF fixtures both validated all six mixed-history rows, with zero changes and identical before/after database file hashes.

Legacy hash constants were retained as historical evidence and are exercised separately from new canonical-record expectations. Unsupported historical mixed-ending digests still fail unless the exact raw source is present; old raw-byte runners retain their downgrade/checkout limitation. Independent review is pending; this entry does not claim integration or release.

---

# 2026-09-21 — Magnetic Follow Review Corrections

- Corrected destination-boundary snapping that bypassed the per-tick speed cap. Only the target is clamped to the cursor monitor; intermediate movement remains bounded and cannot overshoot the target. A short approach outside the destination finishes before dead-zone settling. Oversized axes align to the destination start edge without resizing.
- Corrected same-press HOLD restart after follower self-stop or startup failure. `WAIT_RELEASE` consumes the attempt until key-up; repeats schedule no new hold timer or launch. TAP and the 180 ms threshold are retained.
- Follower regression: PASS, exit 0, console-independent temporary result file. Six geometries exercise 600 actual native movement ticks each. The review's approximately 1733.18 px first step is now 32.557641 px, below 32 + 0.707107 px rounding tolerance. All geometries settle within normal bounds or the oversized start-edge fallback.
- Controller regressions: PASS for self-stop, launcher/lookup failure and follower-start rejection. Self-stop keeps counts at one launch/one start until release; the next press advances both to two. Full live launcher regression: PASS, exit 0, with app/shortcut/database cleanup verified. The corrected test fixture keeps its focus-check decoy under the cursor; Windows settings and production focus behavior are unchanged. Subsequent fresh user physical validation of the unchanged corrected implementation: PASS for magnetic follow, cross-monitor smoothness and multi-monitor movement. No other-PC compatibility is claimed.
- `Docs/11_AHKArchitecture.md` remains canonical; this supplemental note does not replace it. No integration was performed in the feature worktree.

---

# 2026-09-16 — F7 Tap/Hold Magnetic Window Follow

Implemented an explicit 180 ms F7 tap/hold state machine in the AutoHotkey v2 integration layer. TAP retains launch/restore/focus behavior. HOLD now uses a separate find/launch/show path, validates the exact F7Hub Qt/Python window, restores without activation, and starts one 16 ms magnetic movement timer. Physical F7 release, invalid identity, window disappearance and movement errors stop the timer and reset HWND/velocity state.

The follower accelerates and damps toward a cursor-offset target, clamps maximum vector speed, applies a dead zone, suppresses unchanged integer-pixel `WinMove` calls and clamps to the cursor monitor's work area, including negative multi-monitor coordinates. Normal TAP focus errors remain visible; HOLD no longer requires `WinActivate` or `WinWaitActive`. The minimized HOLD path uses `ShowWindow(SW_SHOWNOACTIVATE)` to avoid the activation caused by `WinRestore`.

Both focused AutoHotkey tests use console-independent result files. Live automated Windows validation passed cold launch, controller TAP focus, non-focusing HOLD, release stop, minimized restore, rapid reuse, decoy rejection, cleanup and three-monitor work-area movement; the follower lifecycle/helper suite also passed. User-reported physical Windows acceptance on 2026-09-21 passed all eight required scenarios: tap while closed, tap while existing, hold/follow/release, focus separation, minimized HOLD, rapid use, multi-monitor movement and interactive visual/flicker validation. The dedicated release-stop and dead-zone stability checks also passed.

No Python, PowerShell, database, migration, Slice 022 or primary-recovery-repository file was changed by the magnetic feature.

---

# 2026-09-15 — Slice 022: Read-only Knowledge Tag Filtering

Implemented All tags, Untagged and one-specific-global-tag filtering for current Knowledge lists and FTS search. Tag composes with Category and Status, active changes reuse the last executed query, Clear Search preserves all three filters, and explicit Ticket Open Article resets all filters before reveal. Tag mutation, new article, edit, Publish and Archive reconcile against authoritative current state.

KnowledgeRepository uses correlated `EXISTS`/`NOT EXISTS` predicates on `knowledge_article_tags`, preventing duplicate rows for multi-tag articles while preserving normal ordering and FTS MATCH/bm25 ordering. KnowledgeService validates the single-tag contract. KnowledgeWorkspace reuses global TagRepository options through an independent asynchronous reference runner; MainWindow is unchanged. Filtering is SELECT-only. Six migrations, schema, indexed FTS content and triggers are unchanged. Multi-tag AND/OR, tag administration, saved/date filters and historical tag filtering remain unimplemented.

Validation evidence and actual regression/native results are recorded in `Status/CURRENT_STATE.md`. Work remains unstaged/uncommitted for independent review.

# 2026-09-15 — Slice 021: Existing Global Tags on DRAFT Knowledge Articles

Implemented Tags… for an idle loaded DRAFT article using existing rows from the global `tags` table. The checkable selector supports zero, one or multiple tags, preselects the authoritative current set, and treats Save as exact replacement. Cancel/Escape make no mutation; reference and persistence failures remain safe and truthful. Current tag names remain visible after edit, publish, archive, reconstruction and Ticket Open Article, while PUBLISHED/ARCHIVED mutation is unavailable.

Added explicit TagRepository injection and `KnowledgeRepository.set_draft_tags`. The write transaction uses BEGIN IMMEDIATE, authoritative DRAFT/version/updated-at checks, submitted-tag validation, differential bridge changes, a conditional metadata-token update, exact row-count verification and authoritative reload before commit. No-op sets write nothing. Only `knowledge_article_tags` and `knowledge_articles.updated_at` may change; content version/history, category/status, published_at, ticket links and FTS remain unchanged. No migration or schema change.

Validation: focused Slice 021 set 13 PASS; full Database 318, GUI 123 and Integration 91 = **532 PASS**, zero failures/errors/skips. Native Windows MainWindow 1000×700 passed the zero/one/multiple/replace/remove/remove-all workflow, filters/search, edit, publish/archive, Version History, Ticket Open Article and reconstruction; six external captures were inspected with no horizontal clipping or important overlap. Six unchanged migrations, integrity_check=ok, zero foreign-key violations, FTS integrity PASS and no duplicate bridge pairs. Work remains unstaged/uncommitted for independent review; protected Docs/10 modification and archived-vision deletion remain untouched. Tag creation/admin, tag filtering and historical tag reconstruction remain unimplemented.

---

# 2026-09-15 — Slice 020: Read-only Knowledge Status Filtering

Implemented static All statuses, Draft, Published and Archived filtering for current Knowledge lists and FTS search. Status composes with All/specific/Not selected category modes. Filter changes during search reuse the executed query; Clear Search preserves both filters. Replacement failures clear stale rows/details while retaining selections.

Extended existing KnowledgeRepository/KnowledgeService reads with optional validated status. Repository queries bind external values and compose only static predicate fragments; MATCH, indexed columns, bm25/list ordering and current-result records are unchanged. Filtering is SELECT-only. No migration, schema, index, worker, service layer, MainWindow change or dependency was added.

Create, Publish and Archive reset only incompatible filter dimensions and reveal authoritative results. Category mutation and content edit preserve status. Explicit Ticket Open Article clears search and resets both filters before revealing linked articles regardless of lifecycle/category. Focused/full/native validation and exact evidence are recorded in Status/CURRENT_STATE.md. Work remains unstaged/uncommitted for independent review; saved/tag/date filters, pagination, advanced search and Slice 021 remain unimplemented.

---

# 2026-09-15 — Slice 019: Read-only Knowledge Category Filtering

Implemented All categories, Not selected and active KNOWLEDGE category filtering for current article lists and FTS search. Clear Search retains category; filter changes rerun the executed search. Explicit Ticket Open Article clears search and resets All. Successful category moves reconcile filtered rows/details; new articles outside the filter reveal under All, while edit/publish/archive preserve compatible categories.

Extended existing repository/service read APIs with validated category_id and uncategorized_only arguments. Parameters remain bound; list ordering, literal MATCH generation, bm25 ranking, indexed fields and search records are unchanged. Filtering performs SELECT only. CategoryRepository supplies active Knowledge options through the existing service method. A separate ServiceTaskRunner loads choices without blocking article reads; MainWindow close protection covers its lifetime. Reference failures retain All-category browsing and permit retry; stale list/search results clear before replacement requests.

Focused validation: 35 + 45 Database repository/service tests, 73 GUI tests, 9 repeated focused filter GUI tests after selection cleanup, and 44 Integration tests: PASS. Final sequential regression: Database 304 PASS (15.064s), GUI 113 PASS (47.018s), Integration 88 PASS (400.029s), total **505 PASS** versus 484 baseline. No failures/errors/skips and no suite decrease.

Native Windows MainWindow 1000×700 on isolated synthetic SQLite: All/Not selected/specific category, search/filter/clear, detail/category display, Category… reconciliation, edit, Publish, Archive, Version History and Ticket Open Article: PASS. Six captures were actually opened and inspected; no horizontal control clipping or important overlap observed. Full evidence paths and exact commands are in Status/CURRENT_STATE.md.

Six unchanged migrations, unchanged schema, integrity_check=ok, zero foreign-key violations and FTS integrity PASS. Query-only reads and complete dump comparison confirm no filtering writes. Protected local document modification/deletion are preserved; ROOT, ERD and physical schema documentation are unchanged. Work is unstaged/uncommitted on feat/knowledge-category-filter at 223b54ab. Independent review remains pending. Status filtering, tags, category administration and saved filters remain NOT IMPLEMENTED; Slice 020 was not started.

---

# 2026-09-15 — Slice 018: DRAFT Knowledge Category Metadata

Implemented assign/change/remove for one DRAFT article using active KNOWLEDGE reference data or NULL. Bootstrap explicitly shares CategoryRepository with KnowledgeService and TicketReferenceService. Current article reads resolve category names including inactive assigned references. The small asynchronous ArticleCategoryDialog offers Not selected, active choices, independent reference retry and safe cancellation. Category… sits beside the current category name; keeping it out of the top toolbar preserves the 1000×700 window under the tested styles.

KnowledgeRepository.set_draft_category uses BEGIN IMMEDIATE, authoritative DRAFT/version/updated_at checks, category eligibility in the same transaction, no-op detection and a parameterized conditional UPDATE with exactly-one-row validation. Only category_id/updated_at change; reload precedes commit. Metadata races with unchanged content version reject safely. Timestamp generation reads UTC once and advances beyond a repeated/backward clock token. Version/content/history, publication state/time, FTS and ticket links remain unchanged. No schema or migration change.

Retained focused validation: 117 PASS. Fresh resumed focused validation: 82 PASS (search 7, service 18, category repository/service 14, Knowledge GUI 33, category GUI 9, affected quick-company integration 1). The original full Database attempt failed seven tests due to an undefined Mock in the search constructor fixture; it now explicitly supplies CategoryRepository(self.database_path), with no search behavior or assertion change. The first completed Integration run failed nine 1000×700 checks because the added toolbar action forced a 1038-pixel minimum; relocating that action corrected the production layout. Final sequential regression: Database 294 PASS (14.860s), GUI 104 PASS (19.331s), Integration 86 PASS (373.145s): **484 PASS**, up 25 from the 459 baseline, zero failures/errors/skips. Detailed evidence is recorded in Status/CURRENT_STATE.md.

Native validation: retained complete workflow PASS with 21 inspected captures; fresh bounded layout/selector/assignment/published-state verification PASS with four inspected captures. The fresh captures supersede the old toolbar placement; category/persistence behavior is unchanged. Six migration blobs remain unchanged, schema matches a fresh reference, integrity=ok, foreign-key violations=0 and FTS integrity=PASS. Agent validation only; independent review remains pending.

Updated the affected feature/workflow/GUI/architecture/database/planning owners and CURRENT_STATE. ERD, physical schema and ROOT remain unchanged. Protected Docs/10 content and archived-vision deletion are preserved. All evidence is outside the repository at `C:\Users\Jo\AppData\Local\Temp\f7hub-slice018-validation`. Work remains unstaged and uncommitted. PUBLISHED/ARCHIVED category mutation, tags, category history/filtering/administration and Slice 019 are not implemented here.

---

# 2026-09-14 — Slice 017: Archive One Published Knowledge Article

Implemented PUBLISHED → ARCHIVED through the existing KnowledgeWorkspace, KnowledgeService and KnowledgeRepository. Archive requires explicit PlainText confirmation identifying code/title and preserved content/history/ticket relationships, with Cancel as default and Escape. Enter respects the safe default; cancellation performs zero service calls or writes. Unarchive is explicitly unavailable.

The service validates positive integer article/version inputs (rejecting bool), generates one UTC timestamp and sanitizes missing/non-PUBLISHED/stale/persistence failures. One BEGIN IMMEDIATE transaction loads authoritative state, checks status/version, conditionally updates only status and updated_at, requires exactly one affected row, reloads and commits. Original published_at, content/version/history and ticket links remain unchanged. Injected post-update reload failure rolls back the complete database state. No migration, schema object, FTS rewrite or dependency is added.

ServiceTaskRunner performs the archive asynchronously, blocks competing actions in the real MainWindow and retains the reviewed token across confirmation. Success refreshes/reselects/reloads the authoritative ARCHIVED current article. Edit/Publish/Archive disable; Version History, search and linked-ticket Open Article remain usable. No optimistic status mutation occurs.

Validation: focused repository/service/GUI 82 PASS (31/18/33); Knowledge Base integration 16 PASS; ticket-Knowledge integration 23 PASS, followed by two final focused checks covering real-window busy state and deterministic V2 timestamps. Full sequential regression: Database 280 PASS, GUI 95 PASS, Integration 84 PASS; **459 total**, up 18 from 441, with zero failures/errors/skips. An initial confirmation-copy assertion was corrected before the successful focused and full runs. An incomplete combined integration attempt was superseded by completed separate runs; a diagnostic timer in the ticket run captured slow progress, and that run completed successfully.

Native Windows: PASS with Qt windows, isolated synthetic SQLite and MainWindow 1000×700. Creation/edit/publication, Archive Cancel/default Enter/Escape, confirmed archive, unchanged V2/V1 history, archived search, ticket link/Open Article and reconstruction passed. All 14 captures were visually inspected. SQLite integrity=ok, foreign-key violations=0, FTS integrity=PASS and schema identity were verified. Agent validation, not independent review or user acceptance testing.

Updated affected owner documents and CURRENT_STATE; requirements, documentation routing, ERD, SQL schema and ROOT require no changes. Six migration blobs and protected ROOT/Docs/10 hashes match their baselines; the protected archived-vision deletion remains. Evidence is outside the repository at `C:\Users\Jo\AppData\Local\Temp\f7hub-slice017-validation`. Work remains unstaged/uncommitted for independent Slice 017 review. Slice 018 was not started; Unarchive and Unpublish remain NOT IMPLEMENTED.

---

# 2026-09-09 — Slice 016: Publish One Draft Knowledge Article

Implemented Publish for one loaded DRAFT with explicit Cancel-default plain-text confirmation. The existing service generates one UTC timestamp and rejects invalid ID/version inputs. The existing repository checks authoritative existence/DRAFT/version inside BEGIN IMMEDIATE, conditionally updates lifecycle metadata, verifies one affected row, reloads and commits. Missing, stale, non-DRAFT and persistence failures receive safe feedback; injected post-update reload failure rolls back.

Successful publication sets PUBLISHED and matching published_at/updated_at. It leaves content, version number, immutable history and relationships unchanged; no new snapshot or migration. ServiceTaskRunner serializes the write, then the normal list/detail reload reselects the current PUBLISHED article. Edit/Publish are disabled; Version History, search and ticket Open Article remain usable. Unpublish and Archive remain NOT IMPLEMENTED.

Focused repository/service/GUI: 68 PASS. Focused Knowledge and ticket-link Integration: 36 PASS. Fresh native Windows 1000×700 workflow passed and all nine captures were inspected. Six migrations, unchanged schema, SQLite/FTS integrity and zero foreign-key violations were verified. Final sequential regression: Database 271, GUI 90, Integration 80 = 441 PASS (baseline 424); all exit 0. Commands and evidence are recorded in Status/CURRENT_STATE.md. Work remains unstaged/uncommitted for independent review; protected Docs/10 modification and archive deletion remain intact, with ROOT unchanged.

# 2026-09-09 — Slice 015: Current Knowledge Search / FTS5

- Added `0006_knowledge_search.sql`: an external-content `knowledge_articles_fts` index over current article code/title/summary/body, `unicode61`, insert/update/delete synchronization triggers and migration-time rebuild for existing rows. Historical revisions remain outside FTS. Migrations 0001–0005 remain byte-for-byte unchanged.
- Extended KnowledgeRepository/KnowledgeService with parameterized MATCH, lightweight current result records, bm25 plus deterministic tie-breaking, safe error translation and literal Unicode letter/number token construction with implicit AND. DRAFT/PUBLISHED/ARCHIVED are searchable; empty/punctuation-only queries perform no MATCH and operator-looking input stays plain.
- Added asynchronous Search/Enter/Clear Search to KnowledgeWorkspace using the existing ServiceTaskRunner and current-detail navigation. Explicit loading/count/no-result/failure states, stable IDs, re-entry/competing-action guards, failure query preservation and Clear-to-full-list behavior are covered. New/Edit/History and ticket Open Article remain intact.
- Added migration, repository/service, GUI and Integration coverage for FTS5 availability, backfill, synchronization, complete schema/trigger rollback plus clean retry, current-versus-history semantics, punctuation/Unicode/case/C++, all statuses, deterministic ordering/query plan, deletion races and application reconstruction. Fresh sequential regression: Database 262, GUI 85, Integration 77 = 424 PASS; Database remained 262 PASS after the rollback/retry assertion was strengthened.
- Native Windows 1000×700 workflow passed 10 checks against fresh isolated SQLite. Visual inspection found and corrected full-list status elision by recalculating identity column widths; all nine post-fix captures were then inspected with readable controls/states and no remaining overlap. Six migrations, eight expected FTS objects, virtual-table MATCH plan, integrity ok and zero FK violations.
- Updated only canonical owners for search/schema/workflow/status. Protected Docs/10 and archive deletion remain exactly preserved; ROOT.md is unchanged. Evidence is outside the repository. Work remains unstaged/uncommitted; no commit, push or merge.

# 2026-09-09 — Slice 014 remediation resumed and verified

- Preserved the interrupted remediation in KnowledgeWorkspace, VersionHistoryDialog and test_knowledge_base_flow.py; no further implementation/test correction was needed. Real source had no duplicate imports or function declarations; explicit py_compile passed.
- Top-level window ownership keeps Close/Escape interactive while MainWindow pages remain disabled. All four pending list/detail × Close/Escape cases passed, with competing reads blocked, dismissed callbacks ignored and current article/database unchanged. Qt parent-destruction cleanup was separately verified.
- Scrollable historical metadata exposes both markers of a 6,132-character literal summary at 900×620. Fresh Windows captures showed no overlap and a usable read-only body 356 pixels high.
- Fresh focused Integration: 29 PASS (118.030s test time; 120.656s process elapsed), exit 0. Retained post-fix focused GUI log: 19 PASS. Fresh sequential regression: Database 251, GUI 81, Integration 73 = 405 PASS, all exit 0; five more than pre-remediation, no suite decreased.
- Existing TEMP native harness reused: all four dismissal combinations, long summary and read-only checks PASS. All six screenshots inspected. SQL trace: 18 SELECT, nine BEGIN and nine ROLLBACK statements; full database dump unchanged; five migrations, integrity ok, zero FK violations.
- Corrected workflow and current validation claims only after fresh validation. Protected Docs/10 bytes match the saved pre-remediation hash; archive deletion remains unstaged; ROOT.md, schema, migrations, MainWindow, ServiceTaskRunner and repository/service implementation were untouched by remediation. Evidence remains outside the repository. Unstaged/uncommitted; ready for independent re-review, no Slice 015 work.

# 2026-09-08 — Slice 014: Read-only Knowledge Version History

- Resumed all nine existing Slice 014 implementation/test paths at 4871fd4a1b1ceec8d99dca4247d1407d3e95dc44 on feat/knowledge-version-history-viewer. Preserved correct implementation; added the missing History service-availability guard and strengthened repository/GUI/integration coverage.
- Extended existing KnowledgeService/Repository with lightweight newest-first metadata and one exact selected snapshot. Parameterized SELECTs run in read transactions; trace contains only BEGIN/SELECT/ROLLBACK. No current article, snapshot, timestamp or activity changes; full database-state comparison passes.
- VersionHistoryDialog uses ServiceTaskRunner, stable revision identities, safe dismissal/callback handling and plain-text read-only content. History is available for every loaded status. Missing article/revision and empty history are handled without substituting current content. Historical status/category/updated_by/published_at are not snapshotted.
- Fresh focused: repository/service 31, GUI 19, Integration 24 PASS. Sequential full regression: Database 251, GUI 81, Integration 68 = 400 PASS, up 16 from 384 (7 Database, 7 GUI, 2 Integration). All exit 0; commands use the existing .venv because the supplied ..venv path does not exist.
- Fresh native windows Qt mouse/keyboard workflow and captured-window visual inspection PASS at 1000×700: creation through V3, exact V1/V2/V3, newest-first/current initial selection, unchanged current content, reopen, New/Edit and PUBLISHED/ARCHIVED history. Table titles can elide; full selected titles, body and controls were readable. Agent verification, not user acceptance testing.
- No migration/schema/dependency change. Five historical migrations unchanged; isolated integrity_check = ok and zero foreign-key violations. ROOT.md, physical schema docs, protected Docs/10 modification and archive deletion remain untouched. Harnesses, synthetic databases, captures and logs remain outside the repository.
- Restore/revert, historical editing/deletion, comparison/apply, search/FTS, AI and large-history pagination remain deferred. Unstaged/uncommitted for independent review; recommendation only: current-article Knowledge Search / FTS5. No Slice 015 implementation.

# 2026-09-07 — Slice 013: RELATED Ticket/Knowledge Unlink

- Extended TicketKnowledgeRepository/Service/Widget with one selected RELATED unlink, reusing the existing junction, lightweight identities and ServiceTaskRunner.
- BEGIN IMMEDIATE → ticket/article/exact RELATED checks → parameterized DELETE by both IDs and fixed RELATED → require rowcount == 1 → COMMIT. Zero rows yields typed not-linked; unexpected rowcount and delete/commit failures roll back. Existing missing-entity errors are reused and persistence details remain hidden.
- Added Unlink Article and a plain-text confirmation identifying the article and retaining both entities. Cancel is the default/escape action; cancellation makes no service call. Confirmed unlink is async, blocks duplicate/conflicting operations, guards confirmation reentry/context changes and ignores callbacks for another ticket.
- Failed unlink preserves the selected row. Committed unlink followed by refresh failure remains acknowledged as “Article unlinked.”; Refresh retries only the read. The article reappears in candidates and normal relinking creates one new RELATED row with a fresh timestamp.
- ACTIVITY WRITE: NONE. Only the exact RELATED row is removed. Ticket, article, other RELATED and synthetic APPLIED/RESOLUTION_SOURCE rows survive; ticket updated_at, notes, history and timeline remain unchanged. No schema/dependency change; five historical migrations unchanged, isolated integrity_check = ok and zero FK violations.
- Focused validation: 42 repository/service (18 new), 34 combined Ticket/Knowledge GUI (10 new), 16 Integration (9 new), all PASS. Full regression: 244 Database, 74 GUI, 66 Integration = 384 PASS, up 37 from 347, all exit codes 0. These runs followed final code/test changes; evidence was retained during documentation-only completion.
- Native Windows Qt input and captured-window visual inspection passed at 1000×700 with isolated synthetic SQLite: Cancel, confirmed unlink, parent/other-link preservation, exact KB0002 navigation, KB0001 candidate reappearance/relink, notes and Resolve → Close → Reopen. New control/confirmation readable with no clipping or overlap in tested layouts. Agent verification, not user acceptance testing; harness/captures/logs remained outside the repository.
- Work remains unstaged/uncommitted on feat/ticket-knowledge-unlink for independent review. ROOT.md, physical schema docs and separate archive deletion remain untouched. Next recommendation: read-only Knowledge version-history viewer; no Slice 014 work.

# 2026-09-07 — Slice 012: Ticket/Knowledge Linking

- Added TicketKnowledgeService/Repository for RELATED-only links through existing ticket_knowledge_articles. Frozen lightweight identities exclude bodies; joined title/status/version reflect current article metadata.
- BEGIN IMMEDIATE → entity/duplicate checks → RELATED insert → joined reload → commit. Typed missing/duplicate errors are safe for display; insert/reload failure rolls back. Concurrent duplicates produce one winner; all existing article statuses are eligible and FK cascades remain intact.
- Added the saved-ticket Knowledge tab and LinkArticleDialog with async load/link, retained selection, duplicate-submit/active-close protection, and explicit saved-link feedback if refresh fails. Fixed initial code-column clipping found during native inspection.
- TicketWorkspace emits an article-ID request. MainWindow protects unsaved ticket activity, switches pages and calls KnowledgeWorkspace.open_article_by_id using existing list/detail logic. Missing targets receive safe feedback without opening another article.
- ACTIVITY WRITE: NONE. Only the junction is written; ticket timestamps, timeline, status and resolution are unchanged by linking. No new migration, schema or dependency change; five historical migrations are unchanged.
- Focused validation: 24 repository/service, 24 combined Ticket/Knowledge GUI (12 new) and 7 cross-module Integration tests PASS. Full regression: 226 Database, 64 GUI, 57 Integration, 347 total (43 above baseline), exit codes 0. GUI/Integration rerun after the sizing fix.
- Native Windows agent input and visual checks passed at 1000×700 with synthetic SQLite: empty/link/list/open, article create/edit, notes, Resolve → Close → Reopen and reconstruction. Initial code clipping was fixed and the native flow rerun. Integrity_check = ok, zero FK violations, five migrations. Evidence stayed outside the repository; agent verification, not user acceptance testing.
- ROOT.md and the separate archive deletion remain untouched. Work remains unstaged/uncommitted for independent review. Unlink, other relationship types, search, recommendations and full relationship management are deferred. Next recommendation: RELATED unlink only; no Slice 013 work.

# 2026-09-06 — Slice 011: Draft Editing with Version History

- Added EditArticleDialog and extended KnowledgeWorkspace/Service/Repository for DRAFT title/summary/body revisions. Article code is immutable; current Version N is displayed. The existing implementation was preserved during completion review without refactoring passing code.
- Expected version_number is fixed when editing begins. BEGIN IMMEDIATE → load → existence/DRAFT/version checks → no-change check → conditional UPDATE → new snapshot → reload → COMMIT uses one connection. Snapshot/reload failures roll back; retry creates exactly one next revision. Historical snapshots are never changed by editing.
- Stale editors cannot overwrite newer content or create an extra snapshot, including after the same workspace refreshes. PUBLISHED/ARCHIVED and deleted articles receive safe errors. Failed input is retained; conflicts require reopening. No-change saves leave version/timestamp/history unchanged after authoritative checks.
- Save Revision reuses ServiceTaskRunner, blocks duplicate saves and close/cancel during writes, then refreshes/reselects/reloads the same article. Creation and ticket workflows remain functional.
- Focused tests: repository/service 24 PASS, GUI 12 PASS, Integration 6 PASS. Fresh final discovery: Database 202 PASS, GUI 52 PASS, Integration 50 PASS; 304 total versus 280 before Slice 011. All three commands completed with exit code 0.
- Native Windows input/visual checks: PASS at 1000×700 with isolated synthetic SQLite, edit prefill and read-only identity, Version 1 → 2, updated content, ticket navigation/reopen and another New Article. No observed clipping/overlap. Evidence retained during continuation; no duplicate native run. Harness/captures stayed outside the repository.
- Isolated integrity_check = ok, foreign_key_check = zero violations, migration count = 5. No schema/migration changes. ROOT.md unchanged; unrelated archive deletion preserved separately. Security/integrity review found no blocking defect in the Slice 011 diff.
- Scope excludes history browsing/viewing, restore/revert, publishing/archiving, deletion, search/FTS, categories/tags, relationships, links, ticket linking and AI. Ticket ↔ Knowledge linking is the single recommended next slice, not implemented.
- Branch feat/knowledge-article-editing, base HEAD 04466c3c549bc809a7314c136e1d512ba403ae98. Ready for independent review; no staging, commit, push or merge performed.

# 2026-09-06 — Slice 010: First Usable Knowledge Base

- Resumed existing uncommitted work on feat/knowledge-base-first-slice at 8c2ef7f0aeecfa6b0d65c9e731de8eef3f399efc. Preserved the implementation, ROOT.md and the separate user-confirmed archive deletion.
- KnowledgeRepository/Service, NewArticleDialog and KnowledgeWorkspace provide create → list → reopen/read through existing bootstrap/MainWindow navigation and ServiceTaskRunner. Code/title/body are required; summary is optional. Valid body whitespace is preserved, duplicate codes receive safe feedback and creation prevents duplicate submission.
- DRAFT/version 1 article and initial snapshot use one transaction, reloading before commit and rolling back on version/reload failure. Category and published_at remain NULL. Five existing migrations are unchanged; no schema change.
- Continuation review fixed one defect: metadata QLabels could interpret HTML-like text automatically. Explicit PlainText now matches the read-only Markdown-source body, covered by an added GUI regression test. No passing persistence implementation was rewritten.
- Retained supplied prior-session evidence: 11 repository/service focused, 189 full Database, 4 original GUI focused and 2 original Integration focused tests. Fresh continuation: 5 GUI + 2 Integration focused PASS; full GUI 45 PASS; full Integration 46 PASS after the display fix. Combined regression evidence: 280 PASS (Database retained, GUI/Integration freshly run).
- Native Windows platform: synthetic KB0001/KB0002 creation, list/read switching, application reconstruction and existing ticket navigation PASS at 1000×700. Empty/form/article captures visually inspected without clipping/overlap for these inputs. Agent checks, not user acceptance testing. Isolated integrity_check = ok; zero foreign-key violations; five migrations; one version-1 row per article. A separate trace verified rollback/retry and exactly one successful commit.
- Synchronized features, workflows, GUI/system/Python architecture, roadmap, todo and current state. Editing, deletion, publishing/archiving, search/FTS, categories/tags, relationships, links, ticket linking and AI are not implemented. AutoHotkey NOT RUN; launcher unchanged. Independent review pending; nothing staged or committed.

---

# 2026-09-06 — Slice 009 remediation: unavailable-company recovery

- Fixed the reviewed P2 where a company deactivated or deleted after contact commit left pending contact reconciliation permanently locked. TicketReferenceService now distinguishes authoritative company unavailability with CompanyReferenceUnavailableError; transient read failures retain retry and automatic selection.
- Added one explicit **Continue without this contact** action. It releases pending auto-selection, clears unsafe references and refreshes active companies without reloading categories. The committed contact and remaining ticket draft are preserved; recovery never repeats insertion. Contact-load generations ignore stale success/failure callbacks, including returning to the same company. TicketService and repository transaction code are unchanged by remediation.
- Focused validation: PASS — `.venv\Scripts\python.exe -B -m unittest Tests.Integration.test_quick_contact_flow Tests.Database.test_ticket_references -v` (22 tests: 12 integration, 10 reference); `.venv\Scripts\python.exe -B -m unittest Tests.GUI.test_ticket_reference_widget Tests.GUI.test_quick_contact_dialog -v` (22 tests). Commands used `PYTHONPATH` containing the project Python directory and root, with bytecode disabled.
- Post-remediation regression: PASS — 178 database, 40 GUI, 44 integration (262 total). Isolated integrity_check = ok, foreign_key_check = zero violations, migration count = 5. Schema and historical migrations unchanged.
- Native Windows: PASS — three synthetic integration checks for deactivation recovery, deletion recovery and normal create/auto-select/save/reopen, using the windows Qt platform at 1000×700. Recovery layout visually inspected; draft preservation, responsiveness, company reselection and save after both recovery variants passed. Agent checks, not user acceptance testing.
- Updated workflow, GUI, Python architecture, todo, changelog and current state. ROOT.md, roadmap and the separate archive deletion were preserved. No staging, commit, push, merge or Slice 010 work.

---

# 2026-09-06 — Slice 009: Quick Contact Creation from New Ticket

- Added Quick Add Contact beside the selected company's Contact selector, exposing only required contact name and optional email. ContactService validates company identity/activity, trims text, normalizes empty email to NULL, assigns matching UTC timestamps and creates an active contact. Duplicate names/emails remain valid.
- Reused ServiceTaskRunner for asynchronous writes, cancellation/close protection and duplicate-submit prevention. Failures retain input and expose safe messages; success reloads only contacts, selects the new ID and preserves ticket number, subject, type, priority, company, category and description.
- Retained committed contact/company identity through failed selector refresh. Company switching, Add Company, Add Contact and ticket submission wait for contact-only reconciliation through Refresh references, without another insertion. A successful read excluding a later-unavailable contact releases pending selection with explicit feedback.
- ContactRepository transaction review: SAME RISK — ALIGNED. Creation previously autocommitted before record reload; it now commits only after a successful reload and rolls back failed/missing reloads. A narrow transaction context and optional connection arguments on contact creation/company lookup allow service validation and insertion under the same BEGIN IMMEDIATE lock. Other contact methods and TicketService remain unchanged.
- Focused tests: PASS — 21 database (15 service + 6 repository), 10 GUI, 8 integration. Final regression: PASS — 177 database, 40 GUI, 40 integration (257 total, up from 223). Isolated integrity_check = ok, foreign_key_check = zero violations, migration count = 5; no migration added or modified.
- Native Windows: PASS — 18 GUI/integration tests with the windows platform plus visual inspection of New Ticket, Quick Add Contact and saved details at 1000×700. Verified validation, cancellation, creation, automatic selection, complete draft preservation, busy responsiveness, recovery, combined Add Company → Add Contact, persistence and reopening. Agent checks, not user acceptance testing. Existing notes/lifecycle regression passed; AutoHotkey NOT RUN, launcher unchanged.
- Updated only affected workflow, GUI, Python architecture, roadmap, todo, changelog and current-state documentation. ROOT.md and dependencies are unchanged. During the run, the user deleted the previously modified archived vision document and explicitly instructed preserving that deletion; it was left untouched. No staging, commit, push, merge or next-slice implementation.

---

# 2026-09-06 — Slice 008: Quick Company Creation from New Ticket

- Added a name-only Quick Add Company dialog and narrow CompanyService. Creation trims and validates text, supplies matching UTC timestamps and persists an active company through CompanyRepository.
- Reused ServiceTaskRunner for responsive background creation, guarded repeated submissions and blocked cancellation/closing while the write finishes. Cancel before submission performs no write; failures retain input and show safe messages.
- Successful creation refreshes companies and contacts, selects the new company and clears incompatible contact selection without reloading categories or resetting any unrelated ticket field. The existing TicketService save/reopen path is unchanged.
- Retained committed company identity after failed selector refresh. Recovery through Refresh references selects the existing record without another insertion; committed creation remains explicitly reported as successful.
- Made CompanyRepository INSERT and returned-record reload one transaction. Reload failure rolls back the insert, eliminating ambiguous retry after a partial repository operation. Other repository behavior and all five migrations are unchanged.
- Native Windows inspection found that a separate success-message row expanded the window above 1000×700. Moved success feedback beside Create Ticket and verified the corrected size during success and refresh failure.
- Focused checks: PASS — 14 service/repository, 8 GUI and 5 integration tests; all 27 rerun after the final service-error and layout adjustments. Full regression: PASS — 161 database, 30 GUI and 32 integration tests (223 total). Isolated integrity_check = ok, foreign_key_check = zero violations, migration count = 5.
- Native Windows visual/input checks: PASS — validation, cancel, create, automatic selection, draft preservation, contact reset, post-commit refresh recovery, save/reopen, notes and Resolve → Close → Reopen at 1000×700. Agent verification, not user acceptance testing. AutoHotkey: NOT RUN; launcher contract unchanged.
- No schema, dependency or ROOT.md changes. The archived user modification was preserved exactly. Synthetic databases, screenshots and the native verification script remain outside the repository. No staging, commit, push or merge performed.

---

# 2026-09-05 — Slice 007: Ticket Category Reference Integration

- Added a small read-only CategoryRepository for scoped category facts, with deterministic sort-order/name/ID ordering. TicketReferenceService supplies active TICKET options with separate IDs and labels.
- New Ticket loads categories through the existing ServiceTaskRunner. Category-only refresh/retry avoids company/contact queries and preserves the draft and reference selections on failure. Empty lists retain optional Not selected.
- Reused existing TicketService validation and atomic ticket/history/timeline persistence unchanged. Saved-ticket details resolve current category names, including inactive categories, and handle null/deleted references through the existing SET NULL relationship.
- Reduced the description minimum height to 100 pixels after native inspection found the additional feedback row exceeded the 1000×700 target. Corrected an existing GUI test double to include category reference fields.
- Validation: PASS — 152 database, 22 GUI and 27 integration tests (201 total). Focused runs: 10 database tests, 24 GUI/integration tests and one additional category-worker responsiveness test. Integrity check returned ok; foreign-key check returned zero violations; migration count remains five.
- Native Windows visual/input verification: PASS — category population/filtering, retry, draft and company/contact preservation, create/reopen, optional category, notes and Resolve → Close → Reopen. The corrected form and saved-ticket workspace fit 1000×700. Agent verification, not user acceptance testing. AutoHotkey: NOT RUN — launch contract unchanged.
- No schema, historical migration or dependency changes. ROOT.md and the unrelated archived modification were preserved. Slice changes remain uncommitted for independent review.

---

# 2026-09-05 — Slice 006: Reference-Aware Ticket Creation

- Added active company selection and company-filtered active contacts to New Ticket through a narrow TicketReferenceService and the existing background runner. IDs remain separate from canonical display labels.
- Company switching clears the old contact. Empty choices and reference-query failures have inline feedback and retry; draft text and valid reference selections survive refresh failures.
- Creation rechecks active state and company/contact membership in its existing transaction. Ticket details resolve names from the same SQLite snapshot, including inactive rows; deletion retains the existing SET NULL behavior.
- Fixed deferred initial reference loading so widget destruction cancels its callback. Adjusted description minimum height to fit the added controls and error feedback at 1000×700.
- Validation: PASS — 142 database, 16 GUI and 21 integration tests. Native Windows visual inspection and Qt input-event checks: PASS for company loading, contact filtering, switching, persistence/reopening, empty choices, query errors and stale references. These are agent checks, not user acceptance testing. AutoHotkey was not rerun in this slice.
- No schema, migration or production dependency changes. Synthetic databases and screenshots remain outside the repository. Changes remain uncommitted for independent review.

---

# 2026-09-05 — Windows Usability Check and F7 Shortcut

- Inspected native Windows renders at the initial size and 1000×700, with an available screen of 1600×852. Exercised creation, notes, resolution and Enter-to-open using Qt input events against an isolated database. Native visual/interaction check: PASS; this is agent inspection, not user acceptance testing.
- Adjusted the initial window size to leave room for Windows borders and the taskbar.
- Added the AutoHotkey v2 entry point and F7 launcher: focus/restore an existing window, otherwise start the project Python application. Repeated presses and pending startup retries avoid duplicate launches; startup/focus failures provide feedback.
- Live AutoHotkey checks: PASS, including cold launch, actual global F7 focus/restore, single shortcut instance, missing runtime and timeout/retry handling. GUI regression: PASS — 10 tests. Application/integration regression: PASS — 14 tests.
- No schema, service workflow, production dependency or login-startup changes.

---

# 2026-09-05 — Saved-Ticket Workspace Verification

- Completed verification of the saved-ticket queue, status filtering, paging, detail display, notes, history, resolution, closure and reopening through the application window and real service workers.
- Confirmed failed saves preserve drafts and failed detail loads preserve existing information. Committed writes retain success feedback when subsequent reads fail.
- Fixed creation recovery: if the first detail load fails after a successful save, the workspace explicitly reports creation and refreshes the queue for retry.
- Added nine integration tests using isolated SQLite databases, including integrity and foreign-key checks. Corrected a test-only connection cleanup issue found during the first run.
- Validation: PASS — 133 database tests, 10 GUI tests and 14 application/integration tests. Native Windows smoke validation: PASS.
- Preserved service-owned validation and transactions; no schema or dependency changes. F7 launch/focus is verified separately.

---

# 3. 2026-09-04 — Ticket Notes and Status Service Boundary

## Implementation

- Extended `TicketRepository` with frozen `TicketNoteRecord` results, note creation/reload/list operations, transaction-scoped current-ticket reads and narrow activity/lifecycle updates.
- Reserved repository writes with `BEGIN IMMEDIATE` before reading current ticket state, preserving configured busy-timeout and foreign-key behavior.
- Added `TicketService.add_note()` validation and atomic persistence of the note, a `NOTE_ADDED` event referencing its ID and the ticket activity timestamp. Notes preserve author, source and AI-origin metadata and can be added to closed or cancelled tickets.
- Added `TicketService.change_status()` to validate lifecycle transitions and atomically persist the ticket, status history and `STATUS_CHANGED` timeline event. `NEW` remains creation-only, resolved and closed tickets may reopen to `OPEN`, and `CANCELLED` is terminal.
- Required resolution text when resolving and saved a `RESOLUTION` note plus its timeline reference in the same transaction. Closing retains the resolution; reopening clears current lifecycle fields while preserving resolution notes, including a legacy-resolution snapshot when needed.
- Added missing-ticket validation and safe `TicketUpdateError` feedback for persistence failures. A resolution-typed note alone does not transition the ticket.
- Preserved the existing schema and kept notes/status GUI controls as the next interface slice.

## Validation

```text
Ticket activity repository tests: PASS — 11 tests
Ticket activity service tests: PASS — 17 tests
Full database suite: PASS — 129 tests
Existing GUI regression tests: PASS — 7 tests
Application and GUI integration tests: PASS — 5 tests
Notes/status GUI: NOT RUN — implementation remains planned
```

---

# 4. 2026-09-04 — PySide6 Application Shell and Ticket Creation GUI

## Architecture Decision

- Replaced PyQt6 with the explicitly approved PySide6 framework for the primary Python GUI.
- Pinned `PySide6==6.11.2`, verified it with Python 3.14.6, and installed it into the ignored project `.venv`.
- Selected the community distribution under its available LGPLv3/GPL licensing terms; packaging must preserve applicable notices and LGPL compliance.

## Implementation

- Added `TicketCreateWidget` with ticket number, subject, type, priority, optional company/contact/category references and description input.
- Added inline required-field feedback, safe persistence-error presentation, input preservation, `Ctrl+S`, duplicate-submit protection and created/failed signals.
- Kept the GUI dependent on `TicketService`; no SQL or workflow validation moved into the widget.
- Added service-level translation of SQLite failures into `TicketCreationError` so the GUI does not expose database details.
- Added the thin `python -m f7hub` entry point, central application bootstrap and minimal `QMainWindow` that composes `TicketRepository`, `TicketService` and `TicketCreateWidget`.
- Added a File/Exit action, ready/created status feedback, explicit development-database override and safe fatal-startup feedback.
- Kept the global F7 launch/focus hotkey in the later AutoHotkey slice.

## Validation

```text
Focused GUI tests: PASS — 7 tests
Application and GUI integration tests: PASS — 5 tests
Full database suite: PASS — 101 tests
Package entry point and startup failure path: PASS
Windows-platform visual render review: PASS
Development database isolation: PASS
```

---

# 5. 2026-09-04 — Ticket Persistence and Creation Service

## Implementation

- Added `TicketRepository` with frozen ticket, status-history and timeline records, parameterized ticket creation/reload, case-insensitive number lookup and stable activity retrieval.
- Added a repository transaction session so one service workflow can reuse a private configured SQLite connection without exposing SQL to the service or GUI.
- Added `TicketService` separately to validate ticket fields and references, generate ticket numbers when needed, and atomically create the ticket, initial `NEW` status history and `TICKET_CREATED` timeline event.
- Kept GUI, ticket editing, notes, status transitions and unrelated repositories outside this slice.

## Validation

```text
TicketRepository tests: PASS — 6 tests
TicketService tests: PASS — 5 tests
Full database suite: PASS — 101 tests
Ticket creation and reload: PASS
Required-field, enum and relationship validation: PASS
Parameterized SQL and database constraints: PASS
Transaction commit and forced-failure rollback: PASS
Development database isolation: PASS
```

---

# 6. 2026-09-04 — Knowledge Schema Migration

## Implementation

- Added `Database\Migrations\0005_knowledge.sql` with the canonical relational knowledge tables: articles, versions, links, article relationships, ticket/article links and article/tag links.
- Added the seven documented knowledge indexes and preserved canonical constraints and foreign-key delete behavior.
- Kept `knowledge_article_scripts` deferred until the scripts schema exists and kept FTS tables and synchronization triggers in the later FTS migration.
- Preserved the slice as schema-only: no repository, service, GUI, script schema or FTS implementation was added.

## Validation

```text
Focused knowledge migration tests: PASS — 11 tests
Full database suite: PASS — 90 tests
Migration ordering, checksum and idempotency: PASS
Knowledge constraints, defaults and foreign-key behavior: PASS
Owned-row cascades and category nullification: PASS
Failed knowledge migration rollback: PASS
PRAGMA integrity_check: PASS
PRAGMA foreign_key_check: PASS
Development database isolation: PASS
```

---

# 7. 2026-09-03 — Ticket Core Schema Migration

## Implementation

- Added `Database\Migrations\0004_tickets.sql` with the canonical `tickets`, `ticket_notes`, `ticket_status_history` and `ticket_timeline_events` tables.
- Added the nine documented ticket and ticket-detail indexes.
- Preserved nullable company, contact and category relationships through `ON DELETE SET NULL` and owned ticket-detail rows through `ON DELETE CASCADE`.
- Preserved the slice as schema-only: no repository, service, GUI, attachment, relationship, tagging or FTS implementation was added.

## Validation

```text
Focused ticket migration tests: PASS — 10 tests
Full database suite: PASS — 79 tests
Migration ordering, checksum and idempotency: PASS
Ticket constraints, defaults and foreign-key behavior: PASS
Owned-row cascade and nullable-reference delete behavior: PASS
Failed ticket migration rollback: PASS
PRAGMA integrity_check: PASS
PRAGMA foreign_key_check: PASS
Development database isolation: PASS
```

---

# 8. 2026-09-03 — Company and Contact Repositories

## Implementation

- Added `Python\f7hub\repositories\` with explicit `CompanyRepository` and `ContactRepository` persistence boundaries.
- Added frozen `CompanyRecord` and `ContactRecord` return values rather than exposing SQLite rows or cursors.
- Implemented parameterized create, read, stable list, update and activation-state operations, plus company-code lookup and contact filtering by company.
- Preserved the slice as repository-only: no production schema, migration, service, GUI, ticket or dependency change was added.

## Validation

```text
CompanyRepository tests: PASS — 5 tests
ContactRepository tests: PASS — 5 tests
Full database suite: PASS — 69 tests
Constraint and foreign-key behavior: PASS
Stable ordering and active filtering: PASS
SQL-looking input treated as data: PASS
Company deletion preserves contacts with a null company reference: PASS
```

---

# 9. 2026-09-03 — Company and Contact Schema Migration

## Implementation

- Added `Database\Migrations\0003_companies_contacts.sql` with the canonical `companies`, `company_notes`, `company_links` and `contacts` tables.
- Added the six documented company/contact indexes, including case-insensitive name/email lookup and descending company-note chronology.
- Implemented owned-row cascades for company notes and links while preserving contacts through `ON DELETE SET NULL`.
- Preserved the slice as schema-only: no seed data, repository, service, trigger, GUI or ticket table was added.
- Changed no production Python because the existing migration engine applied the new migration correctly.

## Validation

```text
Focused company/contact migration tests: PASS — 10 tests
Full database suite: PASS — 59 tests
Migration ordering, checksum and idempotency: PASS
Company/contact constraints and foreign-key behavior: PASS
Failed company/contact migration rollback: PASS
PRAGMA integrity_check: PASS
PRAGMA foreign_key_check: PASS
Development database isolation: PASS
```

---

# 10. 2026-09-03 — Taxonomy Schema Migration

## Implementation

- Added `Database\Migrations\0002_taxonomy.sql` with the canonical `categories` and `tags` tables.
- Added the documented parent-category and scope/active/sort indexes without adding redundant tag indexes.
- Preserved taxonomy as a schema-only slice: no seed data, repository, service, trigger, GUI or dependent business-domain table was added.
- Changed no production Python because the existing migration engine applied the new migration correctly.

## Validation

```text
Focused taxonomy migration tests: PASS — 9 tests
Full database suite: PASS — 49 tests
Migration ordering, checksum and idempotency: PASS
Taxonomy constraints and foreign-key behavior: PASS
Failed taxonomy migration rollback: PASS
PRAGMA integrity_check: PASS
PRAGMA foreign_key_check: PASS
Development database isolation: PASS
```

---

# 11. 2026-09-03 — First Versioned Core Migration

## Architecture Decision

- Established `schema_migrations` as bootstrap-owned migration-engine infrastructure created before versioned migrations run.
- Kept `schema_migrations` out of `0001_core.sql`, avoiding duplicate and circular ownership.

## Implementation

- Added `Database\Migrations\0001_core.sql` as the first versioned application-schema migration.
- Added only the canonical `application_metadata` table; no business-domain table, seed data, repository, service or GUI was added.
- Corrected the unreleased migration so `metadata_key TEXT NOT NULL PRIMARY KEY` enforces the documented required-key contract in SQLite.
- Added isolated permanent tests for fresh application, history recording, checksum validation, idempotency, exact structure, constraints, rollback and integrity.
- Changed no production Python infrastructure because the existing bootstrap behavior already implemented the correct ownership model.

## Validation

```text
Focused core-migration tests: PASS — 5 tests
Full database suite: PASS — 40 tests
PRAGMA integrity_check: PASS
PRAGMA foreign_key_check: PASS
NULL metadata_key rejection: PASS
Development database isolation: PASS
```

---

# 12. 2026-09-03 — Slice 001 Verification Follow-Ups

## Git State

- Confirmed the local Git repository is present on `main`.
- Confirmed the local baseline exists and two local commits were present at verification time.
- Confirmed `origin` is configured as `git@github.com:JDecelles1990/F7Hub.git`.
- Confirmed `origin/main` is not yet present; remote publication remains pending.
- Recorded that a focused pre-Slice-001 Git diff is unavailable because no earlier baseline commit exists.

## Regression Coverage

- Promoted seven independently verified SQLite migration behaviors into permanent `unittest` coverage.
- Added coverage for renamed migrations, quoted/comment semicolons, transaction-control denial, `ATTACH`/`DETACH` denial, rollback state, the exact migration-history structure, and its nonnegative execution-time constraint.
- Changed no production SQLite implementation because the permanent tests confirmed the existing behavior.

## Documentation

- Updated current Git status in `ROOT.md` and current Git/test readiness in `17_Todo.md`.
- Preserved earlier ChangeLog statements as historical observations rather than rewriting them as current state.

## Validation

```text
Permanent database infrastructure tests: PASS — 35 tests
Focused new regression tests: PASS — 7 tests
Production SQLite source changes: NONE
origin/main publication: PENDING
```

---

# 13. 2026-09-03 — SQLite Bootstrap and Migration Infrastructure

## Security Cleanup

- Removed the legacy raw ChatGPT browser export `Docs\Assets\ChatGPT - Scripting AHK V.2, PowerShell and PyQt6 F7Hub.html`.
- Removed its complete companion `Docs\Assets\ChatGPT - Scripting AHK V.2, PowerShell and PyQt6 F7Hub_files\` directory.
- Preserved standalone diagram PNG and SVG assets.
- A path-only high-confidence plaintext credential scan returned no remaining file paths.

## Implementation

- Added environment-independent development and installed-runtime database path resolution.
- Added controlled SQLite connection creation with mandatory foreign-key enforcement, configurable busy timeout and clean lifecycle handling.
- Added strict `NNNN_description.sql` discovery, numeric ordering and duplicate-version rejection.
- Added canonical `schema_migrations` initialization and SHA-256 history validation.
- Added atomic statement-by-statement migration execution without `executescript()`, including denial of migration-authored transaction control.
- Added idempotent bootstrap plus `integrity_check` and `foreign_key_check` helpers.
- Added no business-domain migration, repository, GUI or external integration.

## Validation

```text
Isolated database infrastructure tests: PASS — 28 tests
Connection PRAGMAs: PASS
Migration ordering and history validation: PASS
Checksum immutability: PASS
DDL/DML failure rollback: PASS
Integrity and foreign-key checks: PASS
Development database isolation: PASS
Mermaid visual validation: NOT RUN — not required by this slice
Git diff: BLOCKED — Git metadata is not present
```

The tests used temporary file-backed databases and did not create or modify `Database\Dev\f7hub_dev.db` or the legacy `Database\SQLite\F7Hub.db` scaffold.

---

# 14. 2026-09-02 — Documentation Consistency Review

## Scope

- Reviewed `AGENTS.md`, `ROOT.md`, and all canonical `Docs/00` through `Docs/19` Markdown files.
- Inspected repository structure only as needed to validate documentation claims.
- Made documentation-only corrections; no application code, migrations, dependencies or commits were created.

## Documentation Navigation

- Replaced the conversational, duplicated `ROOT.md` draft with a concise project entry point.
- Preserved the separate roles of `AGENTS.md`, `ROOT.md`, and `19_DocumentationIndex.md`.
- Added `ROOT.md` to the first-programming reading path.
- Recorded that project-local `.agents/skills\` are not currently present and are optional until justified.

## Architecture

- Preserved Python/PyQt6 as the primary application and GUI architecture.
- Preserved SQLite as the primary relational persistence layer.
- Preserved PowerShell 7 as the Windows and Microsoft administration, diagnostics and reporting layer.
- Preserved AutoHotkey v2 as the lightweight desktop-productivity layer.
- Aligned the early architecture sequence with the approved first task: SQLite bootstrap and migration infrastructure.
- Corrected target-tense wording that previously implied an application implementation already existed.

## Database

- Aligned `07_Database.md`, `08_ERD.md`, and `09_SQLSchema.md` around `schema_migrations` as the sole migration-state authority.
- Replaced stale potential entity lists in `07_Database.md` with references to the exact physical inventory owned by `09_SQLSchema.md`.
- Added missing `application_metadata` and `categories` entries to the ERD inventory.
- Marked `workspace_panels` and generic `external_entity_mappings` as deferred rather than baseline tables.
- Aligned ticket status examples with the schema values: `NEW`, `OPEN`, `IN_PROGRESS`, `WAITING`, `RESOLVED`, `CLOSED`, and `CANCELLED`.
- Removed a duplicate definition of `ux_diagnostic_steps_one_entry` from the documented DDL.
- Clarified that the first coding task does not include taxonomy, companies, contacts, tickets, repositories or GUI work.

## Naming and Structure

- Corrected the canonical project root in `01_Project.md` from the former OneDrive path to `C:\Dev\F7Hub\`.
- Documented the FTS5 trigger-name exception to the general trigger naming convention.
- Aligned migration filename examples with `0001_core.sql`, `0002_taxonomy.sql`, and `0003_companies_contacts.sql`.
- Corrected PowerShell test ownership from `PowerShell\Tests\` to `Tests\PowerShell\`.
- Removed ChatGPT drafting prefaces, outer Markdown fences and conversational postambles from canonical documents.
- Converted `06_SystemArchitecture.md` top-level numbered sections into navigable Markdown headings without changing its substantive body.

## Planning

- Corrected the Roadmap summary to match its actual Phase 0 through Phase 20 body.
- Aligned the first implementation recommendation throughout the documentation set.
- Replaced the duplicated 2,000-line Todo with a focused current action queue.
- Removed future implementation templates and plans from this ChangeLog.

## Verified Repository State

Repository inspection found:

```text
Python application implementation: PLANNED
PowerShell implementation: PLANNED
AutoHotkey implementation: PLANNED
Database migrations and repositories: PLANNED
Automated application tests: NOT RUN — no test implementation is present
Git baseline: NOT PRESENT
```

The existing `Database\SQLite\F7Hub.db` file is zero bytes and does not verify a database implementation.

`Tools\Scripts\Initialize-F7HubStructure.ps1` exists at the canonical location. Two older root-level PowerShell scripts still contain the obsolete OneDrive path and remain follow-up source-cleanup items. An empty noncanonical `zip\` directory is also present and remains a repository-cleanup decision.

## Validation

```text
Canonical file inventory: PASS
Markdown fence balance: PASS
Canonical cross-reference check: PASS
Stale canonical Markdown term/path scan: PASS
Database inventory alignment: PASS
Documented SQLite DDL execution: PASS
PRAGMA integrity_check on fresh in-memory schema: PASS
PRAGMA foreign_key_check on fresh in-memory schema: PASS
Application tests: NOT RUN
Git diff: BLOCKED — Git metadata is not present
No-index baseline diff review: PASS
```

The SQLite checks validate the documented DDL, not migrations or runtime application behavior.

---

# 15. 2026-09-02 — Canonical Architecture Baseline

The documentation baseline established these project decisions:

- F7Hub is a modular Windows IT Support and technician-productivity platform.
- The project begins as a modular monolith.
- Python/PyQt6 owns the primary desktop application, GUI and orchestration.
- SQLite owns application relational persistence through Python repositories.
- PowerShell 7 owns controlled Windows and Microsoft administration and diagnostics.
- AutoHotkey v2 owns hotkeys, hotstrings, clipboard helpers, launch/focus behavior and lightweight menus.
- AI is an optional assistant and not a privileged execution authority.
- External integrations begin with connect/read/display behavior before controlled updates or synchronization.
- Plugin architecture is deferred until real extension requirements exist.
- The canonical documentation set contains 20 files numbered `00` through `19`.
- `09_SQLSchema.md` owns the exact physical schema; `08_ERD.md` is conceptual and `07_Database.md` owns database design rules.
- The first implementation task is SQLite bootstrap and migration infrastructure.

---

# 16. Superseded Directions

The following earlier directions were replaced by the canonical architecture:

| Earlier direction | Current decision |
|---|---|
| OneDrive-based development root | `C:\Dev\F7Hub\` |
| PyQt6 | PySide6 |
| AutoHotkey as the primary GUI | AutoHotkey v2 as desktop productivity support |
| PowerShell as the primary application layer | PowerShell 7 as controlled administration and diagnostics |
| Direct PowerShell/AHK core database ownership | Python repository ownership |
| Arbitrary 100-table or 120-table target | Requirement-driven normalized schema |
| Early unrestricted plugin framework | Deferred until validated requirements |
| AI-controlled administration | Technician-controlled execution boundaries |
| One large implementation task | Small independently tested slices |

Archived documents and legacy diagrams do not override these decisions.

---

# 17. Maintenance Rule

Record only meaningful completed changes here.

For each entry:

1. state what changed
2. distinguish documentation from implementation
3. report actual validation using `PASS`, `FAIL`, `NOT RUN`, or `BLOCKED`
4. reference migrations for physical schema changes
5. leave future work in `16_Roadmap.md` or `17_Todo.md`

> The ChangeLog records what F7Hub became, not what it might become next.
