# KB-SG03 — reviewed implementation contract

Date: 2026-11-01, America/Toronto. Architecture:
**KB_SG03_ARCHITECTURE_APPROVED_WITH_NOTES**. Stage A implementation:
**READY_FOR_REVIEW**, independent correction approval PENDING (initial review CHANGES_REQUIRED).
Stage B: **NOT IMPLEMENTED / NOT RUN / NOT AUTHORIZED by A**.

## Authority and baseline

The owner explicitly authorized Stage A implementation, tests and a separate
independent review of exactly thirteen paths, with no Git integration.
The authoritative v2 architecture review is external at
`%LOCALAPPDATA%/F7Hub/CodexCheckpoints/KB-SG03/independent-embedded-architecture-review-20261101/independent-embedded-architecture-review-v2.md`.
It binds the original architecture plan SHA-256
`383ab981d2eb07de0ab860600a9a80aa0c015d219459943fe8dcc339f1af7592`.
Its stage scopes and mandatory clarifications prevail over incomplete plan detail.

Baseline: integrated KB-SG02 PR #127,
`f9954998866f22a3521c83b2e748877d1565bc94`; verified live remote main before
implementation. Dedicated candidate: `C:/Dev/F7Hub-KB-SG03A`,
`feature/kb-sg03a-shared-editor`. Preserve dirty canonical, unrelated worktrees
and excluded superseded subprocess candidate. No staging/commit/push/PR/merge.

## Exact A allowlist

| Kind | Path |
|---|---|
| ADD | Python/f7hub/gui/kb_preview_editor.py |
| MODIFY | Python/f7hub/gui/kb_preview_dialog.py |
| ADD | Python/f7hub/services/kb_lab_session.py |
| MODIFY | Tools/Knowledge/kb_sg02_lab.py |
| ADD | Tests/GUI/test_kb_preview_editor.py |
| MODIFY | Tests/GUI/test_kb_preview_dialog.py |
| MODIFY | Tests/Integration/test_kb_sg02_lab.py |
| MODIFY | Docs/05_GUI.md |
| MODIFY | Docs/06_SystemArchitecture.md |
| MODIFY | Docs/13_PythonArchitecture.md |
| MODIFY | Docs/18_ChangeLog.md |
| MODIFY | Docs/Status/CURRENT_STATE.md |
| ADD | Docs/Planning/DataReadiness/KB_SG03_Implementation_Contract.md |

Tests/Unit/test_kb_preview.py is an unchanged required regression.

## Implemented A contract

One `KBPreviewEditor(QWidget)` owns all existing notice/selector/source/proposal/
title/summary/body/annotation widgets and draft behavior. No database/repository
capability enters it. Its close signal carries intent; confirmation is nonterminal.
The thin standalone QDialog retains modal title/geometry, guarded Escape/reject/
accept/done/X routes and no stronger accepted meaning. Terminal commit clears and
freezes view content/undo; only the resource owner invalidates service lifetime.

Fixed loader/manifest/source pins, six immutable fixture identities F01-F06,
NEW tickets, DRAFT reference, English/French, fictional qualifications and
unresolved canonical proposals are unchanged. Explicit fixture selection is
required. Titles/summaries use 200/1000 Unicode scalar limits; body/annotations
use 64/16 KiB UTF-8. Invalid edits restore the last admitted value.
Replacement generation precedes discard confirmation; failure asks no discard
question. Cancel preserves source identity, every field, selection and undo.

The one-shot `SyntheticLabSession(project_root)` exists before preparation,
admits before allocation and creates only its own temp SQLite target. Fresh
existing repositories/services stage six NEW tickets and one DRAFT reference
with zero promoted links. All connections close before immutable snapshots and
the existing preview-only service reach the GUI. No production database path,
repositories, credentials, Settings or ApplicationContext are accepted.

AC1 outcomes are distinct: admission failure allocates nothing; setup failure
with successful cleanup reports removed storage; setup-plus-cleanup failure keeps
the exact owner/root with `setup_failed=True`, `cleanup_failed=True` and
`cleanup_complete=False`. Safe exceptions carry `owner`, without raw feedback.
Invalidation and successful cleanup are individually idempotent. Failure retains
diagnostic identity; no automatic cleanup retry or broad parent deletion occurs.
Directory identity, temp-parent, path and reparse/symlink checks precede exact-root
removal. Explicit later cleanup must revalidate ownership. Context exit and dialog
use the same owner, avoiding duplicate invalidation or successful deletion.
This is application capability separation, not OS sandboxing or crash-proof erasure.

After setup, generation, edits, fixture switches and close confirmation use no
SQLite/source-file/network/repository/production-service I/O. Terminal filesystem
cleanup is measured separately. The CLI retains fixed no-override arguments.

## Validation and limits

Focused changed GUI/integration suites and unchanged preview regression are
required fresh checks. Real-service integration guards exact SQLite targets,
closed setup connections, immutable snapshot identity, failure ownership, exactly
once terminal behavior, no production capability use and zero preview-time I/O.
Disposable logical dumps must match, integrity_check must return ok and
foreign_key_check must return zero rows. No real operational DB is opened/copied/
hashed as an isolation probe.

A fresh bounded WINDOWS_NATIVE retained-CLI run is required: visible ready editor,
all six choices, readable notice/source, keyboard/focus, dirty Cancel/Discard,
normal dialog/process exit and exact owned-root removal, with dimensions/DPI and
inspected screenshots. Corrected author run PASS 39 assertions at 1080x780/96 DPI/DPR 1.0,
three inspected captures, exit 0 and removed owned storage. Qt-injected input is
distinct from physical acceptance. Physical input, alternate DPI, AT/high contrast
and other newline profiles remain NOT RUN. Initial focused author tests PASS
50/50; a test-only production guard addition led to integration17/17.
Independent focused51 PASS did not cover the later diagnosed keyboard failure.
R1 restores the baseline no-default Close policy; R2 restores existing doc tails.
Corrected author tests PASS fresh38 (editor9/dialog12/integration17) plus
RETAINED unchanged preview14, giving52 unique covered tests. Clean/dirty title
and summary Return preserve session without question; Close/Space and Escape
retain their guarded semantics. Original review/failure evidence is preserved. Current counts/manifest and review disposition belong to the external
implementation/review records and CURRENT_STATE, without rewriting test history.

Retain KB-SG02 B01 closure and N01-N03: note tuple revisions are not displayed;
six manual fixtures do not establish extraction or technical/canonical acceptance;
physical/accessibility and non-Windows raw-byte profiles are unverified. Original
historical KB-SG01 approval remains NOT VERIFIED. No source/fixture/service/
migration changes expand that authority.

First failed/inconclusive execution stops automatic retries. Preserve evidence,
diagnose and verify a relevant correction or a materially different diagnostic
purpose before any further affected probe. No unchanged retry.

## Stage B dependency and exclusions

B requires a separately reviewed/authorized A identity plus explicit B authority.
Its embedded Articles/Lab tabs, toolbar, worker/owner generation/latch, page-aware
actions and deferred application close/Exit remain planned, not implemented here.
Reviewed AC2-AC4 apply to B's host/lifecycle/context implementation; A contributes
the shared editor and AC1 resource contract only. B may not silently fix A runtime
outside its allowlist.

No MainWindow/ApplicationLifecycle/bootstrap/KnowledgeWorkspace changes, live or
RESOLVED ticket admission, semantic activation/publication, migrations, Clipboard,
installer or unrelated refactoring are included. No subprocess launcher, native
reparenting or second editor is introduced.

## Evidence and next gate

External author evidence:
`%LOCALAPPDATA%/F7Hub/CodexCheckpoints/KB-SG03A/correction-r1-r2-20261101/`.
Original author and initial independent-review directories remain preserved.
Candidate manifest records all thirteen paths, base, branch/HEAD, raw SHA-256,
Git-normalized blobs and reproducible aggregate. Tested-to-final applicability
must distinguish documentation/test-only changes from runtime drift.

Completion requires a separate independent reviewer/session and an exact
APPROVED, APPROVED_WITH_NOTES, CHANGES_REQUIRED or REVIEW_BLOCKED disposition.
Stop at that review gate. Approval does not authorize B or integration.
