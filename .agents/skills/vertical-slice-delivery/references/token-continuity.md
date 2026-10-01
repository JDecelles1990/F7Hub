# Token-Aware Continuity and Recovery

TOKEN PRESSURE NEVER ADVANCES A LIFECYCLE GATE. Strategy may change; correctness requirements do not. Seek maximum safe progress, not maximum token consumption.

## Assess pressure

Distinguish design-tested/simulated recovery from operationally exercised recovery. MUST label the evidence category, originating interruption, recovered artifacts, and observed outcome when claiming recovery validation. A simulation does not establish real exhaustion recovery, and one successful operational recovery does not guarantee persistence after every host failure. The recovery procedure below remains generic.

Use a reliable host-provided remaining-context/token indicator conservatively if exposed. Otherwise never invent an exact count. Observe explicit user notice, host/tool/session warnings, truncation warnings, inability to recall inspected details reliably, unusually large accumulated state, or an imminent context limit. Absence of a counter alone is not exhaustion; inability to trust continuity is UNKNOWN and follows RED.

| Level | Allowed strategy |
|---|---|
| GREEN | Normal bounded work; may start one small atomic operation. Preserve evidence at gates. |
| AMBER | No scope expansion, large refactor, optional work, or new unrelated test suite. Finish the current small file edit, focused test, or inspection unit; prioritize required work and persist evidence. Prepare a checkpoint. |
| RED | Start no substantive new work or long regression. No new architecture/migration/schema work, broad refactor, staging, commit, push, PR creation, merge, branch/worktree deletion, stash manipulation, or destructive/recovery Git action. Finish only an already-started operation whose interruption would leave unsafe partial state; checkpoint and stop. |
| UNKNOWN/EXHAUSTION | When continuity cannot be trusted, behave as RED. |

An atomic operation is bounded but may still fail or have an uncertain outcome: one migration-file write, transaction-sensitive edit, explicit staging operation, commit, push, PR creation, merge action, or worktree operation. Before starting under pressure ask: can it be completed, verified, and recorded within available context? If no, do not begin. RED prohibitions take precedence over this assessment. Do not chain remote mutations into one presumed atomic unit.

## Phase-specific RED behavior

| Phase | Safe stop |
|---|---|
| PLAN | Finish the current inspection unit only if safe; checkpoint findings. Do not select a slice without sufficient evidence. |
| IMPLEMENT | Finish only an in-flight small edit if interruption would leave unsafe partial state; if possible perform the smallest syntax/focused check needed to assess it. No staging. |
| TEST | Record completed tests exactly; remaining tests are NOT RUN — token/context safety stop. No validation-complete claim. |
| DOCUMENT | Finish only the current small edit if safe; otherwise record pending documentation. |
| REVIEW | No APPROVE without all required independent evidence. If incomplete, record decision BLOCKED and lifecycle CHECKPOINTED when stopping for continuity. |
| INTEGRATE | Record the exact milestone below; do not initiate the next mutation. |
| VERIFY/CLOSE | Record verified facts and pending verification; do not claim CLOSED without its gates. |

Integration milestones:

- Nothing staged: record status, checkpoint, stop.
- Exact staging complete, no commit: record staged paths, cached diff identity/check, checkpoint, stop.
- Commit created, no push: record commit SHA and ancestry, checkpoint, stop.
- Pushed, no PR: record verified remote branch SHA or label NOT VERIFIED, checkpoint, stop.
- PR created, not merged: record PR number, base/head and state, checkpoint, stop.
- Merge completed: verify remote main if reasonably possible; otherwise record MERGE_COMPLETED_VERIFICATION_PENDING. Never infer merge failure from session loss.

## Long tests and incremental evidence

With healthy context run required full regression normally. Under AMBER complete focused checks first; start required long regression only if capacity remains to capture the command, result/counts, and report/checkpoint. Under RED do not start it.

For long-running or expensive suites, MUST create/identify a durable log before execution and persist execution identity: command, working directory, candidate manifest/aggregate, relevant non-secret environment/platform, start time, and process/tool-session identifier when available. Arrange completion recording independently of the originating chat session where supported; a supervisor/wrapper may write it. Fast focused checks MAY use ordinary command/result records.

On completion MUST persist a small machine-readable `<suite>.result.json` (or an established equivalent) with schema version, candidate aggregate identity and manifest location, command, working directory, relevant environment/platform, started_at, finished_at, exit_code, discovered/executed test counts when available, failures, errors, skips, result, log path, and optional notes. Use timezone-qualified timestamps and null plus an explanation for unavailable fields; never invent counts or exit codes. Result vocabulary is PASS / FAIL / BLOCKED / INCOMPLETE; these are execution outcomes, not lifecycle states or provenance. Record INCOMPLETE while running or when completion cannot be established. PASS requires verified completion, successful suite outcome and exit code, and satisfaction of required assertions/counts/skip policy. Write completion records safely and read them back; retain earlier attempt records rather than overwriting failure history.

On recovery MUST inspect durable result artifacts and logs BEFORE rerunning an expensive suite, then check whether its identified process is still running or completed. MUST NOT assume an interrupted command failed because the originating agent session ended. An absent result record or partial log is uncertain/incomplete evidence, never automatic FAIL or PASS. Reconstruct a completion record only from independently recovered completion/exit/result evidence, naming its sources. If completion cannot be established, report execution INCOMPLETE and evidence NOT VERIFIED; mark the required criterion NOT RUN or BLOCKED with the recovery limitation, and safely rerun when appropriate. Do not launch a duplicate while the same validation is still running or terminate unrelated processes.

Reuse completed results only after candidate/transitive-input and environment applicability checks under [review gates](review-gates.md), labeling them RETAINED. Prior verified tests need not be repeated unless changed inputs, environment, or missing evidence require it.

Abrupt termination may prevent a final checkpoint. Recover from the latest incremental evidence plus live state; absence of a final report does not prove an action failed. A skill cannot guarantee persistence after host termination.

## Durable checkpoint creation

Preferred root: resolve LOCALAPPDATA from the environment, then use F7Hub\CodexCheckpoints\Slice-NNN beneath it. Do not hard-code a user profile. Conceptual example:

```powershell
$checkpointRoot = Join-Path $env:LOCALAPPDATA 'F7Hub\CodexCheckpoints'
$sliceCheckpointDirectory = Join-Path $checkpointRoot 'Slice-NNN'
```

Before writing, confirm LOCALAPPDATA is available and the resolved destination is outside the repository and its worktrees. Validate the slice directory name; never interpolate arbitrary slice text into a path. Use latest.md as the clearly identifiable latest checkpoint and timestamped checkpoint-YYYYMMDD-HHMMSS.md snapshots where useful. Avoid collisions and preserve a prior valid snapshot until the new file is written and read back successfully; never overwrite an unrelated file. Record the actual path and persistence verification. Do not modify .gitignore or repository files for checkpointing.

Use [recovery checkpoint](../templates/recovery-checkpoint.md). Inspect Git state; record interrupted phase/state, completed/incomplete work, all test statuses, changed/staged/untracked files, branch/HEAD/origin/main, documentation/review status, exact Git milestones, risks, existing authorization, pending operations, evidence and one next safe action. Save incremental evidence before pressure becomes RED where possible.

Read back the checkpoint and verify completeness and redaction. If external writing or verification is unavailable, emit the complete checkpoint in the session response and explicitly state: durable external persistence NOT VERIFIED. Read-only review permits only external evidence/checkpoint artifacts, never candidate edits. Enter CHECKPOINTED and stop; do not rush to finish the slice.

## Checkpoint security

Persist only evidence necessary for safe resumption. Never persist passwords, API keys, access/refresh tokens, private keys, authentication cookies, secret-bearing connection strings, unnecessary personal information, sensitive clipboard contents, raw credentials from logs, or secret environment-variable values. Do not dump the environment or copy raw logs wholesale into checkpoints.

Redact sensitive values in commands/errors while preserving non-secret structure needed to resume. SHAs, necessary paths, branch names, PR numbers, test counts, states and non-secret commands are acceptable. Paths and URLs must still be checked for embedded secrets or unnecessary personal information. Record redaction status; never include the original secret beside its replacement.

## RECOVERING audit

RESUME means RECOVER -> VERIFY -> IDENTIFY CURRENT STATE -> CONTINUE SAME PHASE. CHECKPOINTED -> RECOVERING -> original interrupted phase; never restart or advance solely because a session changed. If no final checkpoint exists, enter RECOVERING from the last known state.

Before implementation or any new Git mutation:

1. Verify root, branch and HEAD.
2. Fetch/verify origin/main when relevant; distinguish a stale local remote-tracking ref from a live remote check. Failed required freshness verification blocks integration.
3. Inspect working tree, staged diff, and all untracked files.
4. Inspect the durable lifecycle/checkpoint, candidate manifest if present, per-path and aggregate identities, long-test result artifacts/logs and pending/running identifiers before any expensive rerun. Verify known commit existence, parentage and content. Reconstruct from durable repository/external evidence, never model memory alone.
5. Verify remote feature SHA, existing PR base/head/state, and merge state where applicable using [Git idempotency](git-safety.md).
6. Inspect review/integration/closure reports and unresolved carry-forward notes. Compare evidence and checkpoint claims: CONFIRMED, STALE, CONFLICTING, or NOT VERIFIED. Apply [handoff authority](lifecycle.md): actual repository/remote state overrides Git prose, verified completion artifacts establish lifecycle facts, and stale metadata does not authorize repair.
7. Reconcile completed/incomplete actions and authorization. Existing approval/authorization is bounded to the same slice, scope, reviewed candidate and operation; new session alone does not require renewed permission.
8. Resume the original interrupted phase only when sufficiently reconciled. Record any subsequently justified normal transition separately. Material conflicts enter BLOCKED or INTEGRATION_BLOCKED; uncertain remote outcomes never justify automatic retry.

Examples: recover a staged candidate into INTEGRATING before deciding whether the authorized commit remains safe; recover a completed test into TESTING before recording its gate; recover an observed merge into the interrupted integration phase, then record MERGED only with verified evidence. Changed approved content requires renewed review. One unknown untracked file is inspected and classified, never automatically staged, deleted or ignored.
