# F7Hub Slice Recovery Checkpoint

Use [token continuity](../references/token-continuity.md). Save under the environment-resolved LOCALAPPDATA\F7Hub\CodexCheckpoints\Slice-NNN, outside the repository. This template's relative link refers to the source skill; when copying externally, record its resolved source path below. No secrets or unnecessary personal information. Redact sensitive commands/errors before writing.

## Slice

- Number:
- Name:
- Checkpoint timestamp / timezone:
- Source skill path:
- External latest checkpoint path / timestamped snapshot path:
- Durable external persistence: VERIFIED / NOT VERIFIED

## Lifecycle State

- Current state:
- Original interrupted phase/state:
- Last completed gate and evidence:
- Next required gate:
- Token pressure level and observed reason (no invented count):

## Repository

- Root:
- Branch:
- HEAD:
- origin/main / last fetch or live verification time:
- Working tree / changed files:
- Staged files / cached diff identity:
- Untracked files:
- Protected unrelated paths and preservation evidence:

## Approved Scope

- Production:
- Tests:
- Documentation:
- Out of scope:
- Approved plan / reviewed candidate identity:
- Authorization already granted, source and exact operation limits:
- Architectural decisions and evidence:

## Work Completed

- Exact completed items and evidence:

## Work Incomplete

- Exact remaining items and required gates:

## Tests

- PASS:
- FAIL:
- NOT RUN:
- BLOCKED:
- Commands / environment / candidate identity / counts / exit status:
- Fresh versus retained evidence:

## Documentation

- Completed:
- Pending:

## Review

- Status / decision / reviewer:
- Findings:
- Approved base / scope / content binding, if applicable:

## Git / GitHub

- Feature commit / parent / tree:
- Remote feature branch / verified SHA:
- PR number / URL / base / head / state:
- All same-repository/head PRs discovered across bases and states; discovery completeness:
- Each discovered PR: number / URL / state / actual base / expected base / head / remote head SHA:
- Conflicting PR evidence / classification / explicit disposition or pending decision:
- Merge commit / parents / ancestry / verification status:
- Actions definitely completed (including remote actions):
- Actions definitely NOT completed:
- Uncertain actions requiring verification:
- Pending/running operations / process or tool-session identifiers:
- Evidence locations:

## Risks / Blockers

- Concrete items only:

## Security

- Sensitive-data redaction status:
- Commands/errors sanitized; no credential, secret environment value, or sensitive clipboard material persisted:

## Next Safe Action

One explicit action, within existing authorization and the interrupted phase:

## Resume Instructions

Enter RECOVERING before dependent work:

1. Verify root, branch and HEAD.
2. Fetch/verify origin/main when relevant; inspect status, staged diff and untracked files.
3. Verify known commits and pending/running operations.
4. Verify remote branch, existing PR and merge state where applicable before any repeated mutation.
5. Compare actual evidence with this checkpoint; classify each material claim below.
6. Reconcile scope, reviewed content and existing authorization. Material conflicts mean BLOCKED or INTEGRATION_BLOCKED.
7. Resume the SAME interrupted phase only after reconciliation. Record any subsequent justified lifecycle transition separately.

| Claim | CONFIRMED / STALE / CONFLICTING / NOT VERIFIED | Actual evidence / disposition |
|---|---|---|
| | | |

Never assume an action failed merely because the prior session ended. If external persistence is unavailable, emit this complete checkpoint in the response and state: durable external persistence NOT VERIFIED.
