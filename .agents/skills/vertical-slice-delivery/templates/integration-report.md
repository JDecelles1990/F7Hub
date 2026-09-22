# F7Hub Slice Integration and Closure Report

Use with [Git safety](../references/git-safety.md). Report verified actions only. Lost output is not proof of failure; never repeat a mutation before checking actual state.

## Baseline and Authorization

- Slice number / name:
- Result: PASS / FAIL / BLOCKED / CHECKPOINTED
- Lifecycle state / interrupted phase:
- Root / branch / HEAD:
- Reviewed base / candidate identity / review decision and source:
- Exact approved paths / protected paths:
- Integration authorization source and operation limits:
- Initial tracked / staged / untracked status:

## Integration Evidence

| Gate / action | Actual result / identity | Fresh evidence / time | Remaining requirement |
|---|---|---|---|
| Fetch and origin/main freshness before staging | | | |
| Candidate identity and approval binding | | | |
| Main advancement compatibility disposition, if needed | | | |
| Explicit staged allowlist | | | |
| Full cached diff / path / whitespace audit | | | |
| Atomic feature commit SHA / parent / tree / scope | | | |
| Normal push and live remote SHA | | | |
| Complete same-repository/head PR discovery across all bases and states | | | |
| Each discovered PR: number / URL / state / actual base / expected base / head SHA | | | |
| Conflicting or multiple PRs / evidence classification / explicit disposition | | | |
| PR base / head / commits / exact file scope | | | |
| Required checks / conflicts / mergeability | | | |
| Main freshness and expected head before merge | | | |
| Normal merge / merge SHA / parents | | | |
| Feature ancestry / resulting content identity | | | |
| Renewed validation/review for resolution changes, if needed | | | |
| origin/main contains verified merge | | | |
| Safe local main switch / pull --ff-only | | | |
| Local HEAD == origin/main | | | |
| Final status / protected content preservation | | | |

## Validation and Recovery

- Retained test/review evidence and unchanged-content justification:
- Fresh validation required and executed:
- Definitely completed actions:
- Definitely not completed actions:
- Uncertain actions and read-only verification needed:
- Pending/running operation identifiers:
- Checkpoint location / persistence / redaction status:

## Closure

- State transitions and evidence:
- Final branch / HEAD / origin/main:
- Staged / unstaged / untracked:
- Concrete risks / blockers:
- Verified cleanliness exception, if protected unrelated work remains:
- CLOSED gate satisfied or outstanding checks:
- Next safe action:
- Deferred next-slice candidates (planning requires a new instruction):
