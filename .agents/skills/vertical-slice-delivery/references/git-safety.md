# Controlled Git and GitHub Integration

## Baseline and preservation

Verify the canonical root C:\Dev\F7Hub (or an explicitly justified checkout), branch, HEAD, remote identity, status including every untracked path, and staged diff before edits or branch movement. For new-slice planning, verify main and fetch origin; establish whether HEAD == origin/main. Do not switch, pull, or repair during inspection-only PLAN. Record mismatches and their impact.

Before implementation, recheck the approved baseline. Normally begin from clean main and create one feature branch. If baseline changed, inspect the delta and obtain any necessary plan revision before editing. Do not assume a previous fetch is current. Preserve unrelated changes; document protected paths and content identity where needed. Unknown untracked files require inspection/classification; never include them by default. Unexpected pre-staged content blocks staging until an explicitly authorized resolution exists.

Never use destructive recovery to simplify state. Do not automatically use git reset --hard, git clean, git rebase, force push, stash apply/pop, branch deletion, or worktree deletion. These need specific task authorization after inspection. No reset, clean, restore, or stash operation merely to obtain cleanliness. Do not alter Git configuration or line-ending policy to bypass a gate.

## Bind approval and authorization

Independent approval records reviewed base SHA, branch/HEAD, exact allowed paths, tracked diff and untracked additions, plus content identity sufficient to compare the candidate later. Use normalized Git content identities for commit comparisons; record raw hashes where byte preservation matters. A branch name or path list alone does not bind approval to content.

Integration authorization is distinct from review approval. Respect authorization already granted, but keep it bounded to the same slice/scope/candidate/operation. Post-review candidate changes invalidate approval for affected content; do not integrate them without renewed review and relevant validation. Even documentation-only changes require review of the delta; unchanged implementation evidence may be retained under [review gates](review-gates.md).

## Integration sequence

Check [token pressure](token-continuity.md) before each atomic operation. Only APPROVED and authorized work may proceed.

1. Fetch origin. Verify reviewed base against origin/main, candidate identity, branch, scope, protected files, and empty/unexpected index state. If main advanced since review, enter INTEGRATION_BLOCKED, even if changes appear compatible. Inspect compatibility; no silent rebase or merge of main. Proceed only after an explicit compatibility disposition with required validation/review against the new base. A changed candidate follows the correction loop.
2. Stage exact approved paths using git add -- followed by the explicit allowlist. Never default to git add ., git add -A, or git add --all. Approving a path does not authorize unrelated hunks inside it; resolve mixed ownership before staging.
3. Audit git diff --cached --name-status, the full cached diff, git diff --cached --check, and status. Confirm exact expected path/content identity, protected exclusions, and no omitted intended changes. Stop on mismatch; do not automatically unstage user content.
4. Create one atomic feature commit containing the approved production/tests/docs scope. Verify commit SHA, parent, tree and changed files. If a commit may already exist, use the recovery procedure below before creating another.
5. Push normally to the intended remote feature branch. Verify the live remote SHA equals the feature commit. No force push.
6. Apply the PR discovery and disposition rules below before creating or reusing a PR: discover the same repository/feature head across all bases and states first, then validate the base. Verify PR target main, head SHA, commits and exact changed-file/content scope. Check applicable required checks, conflicts and mergeability; do not bypass project protection rules.
7. Fetch origin and recheck main freshness and PR head immediately before merging. Main advancement enters INTEGRATION_BLOCKED. Default is NORMAL MERGE COMMIT, never squash/rebase unless project policy explicitly changes. Use an available expected-head guard; do not assume a precheck eliminates races. Verify the actual result.
8. Verify PR is merged and identify merge SHA. Fetch origin; verify the merge exists, its parents and approved feature-commit ancestry, and its presence in origin/main. Check resulting content against the reviewed candidate and approved base. A clean merge with unchanged reviewed content and base may retain prior test evidence; Git verification remains fresh.
9. Conflict resolution or changed resulting content requires renewed affected validation and independent review; do not resolve it silently in the integration phase. If discovered after merge, do not claim CLOSED: enter INTEGRATION_BLOCKED, record actual merged state, and seek an authorized correction without destructive rollback. A main race or other unexpected parent/content also requires reconciliation before closure.
10. When safe, return the local workspace to main, use git pull --ff-only, and verify HEAD == freshly verified origin/main. Verify merge/feature ancestry and final preservation/status. Do not delete branches/worktrees as implicit cleanup. Normally end clean; protected unrelated work is preserved and any verified exception is reported. Unresolved synchronization prevents CLOSED.

Use [integration report](../templates/integration-report.md). If network/auth/required evidence is unavailable, report BLOCKED/INTEGRATION_BLOCKED, never infer success.

## PR discovery and disposition

HEAD DISCOVERY FIRST -> BASE VALIDATION SECOND. Before PR creation, determine whether the feature head already participates in ANY PR in the repository. Discover same-repository/head PRs across all base branches and OPEN, CLOSED and MERGED states; do not initially filter by the expected base. Verify exact head identity, including the source repository where relevant, and complete any pagination. Incomplete discovery or unavailable remote evidence means INTEGRATION_BLOCKED, not permission to create.

After discovery, inspect every result's number, URL if available, state, actual base, head identity and remote head SHA against the approved candidate. Record the approved integration base separately. Apply these rules to the complete result set; finding one reusable PR does not hide another conflicting result.

| Discovered result | Required disposition |
|---|---|
| ANY wrong-base PR, in ANY state | Classify the evidence CONFLICTING and enter INTEGRATION_BLOCKED. Report number, state, actual base, expected base and URL if available. Do not automatically create another PR, reuse the wrong-base PR, change its base, close, merge or supersede it. Require explicit disposition; even a closed wrong-base PR must be surfaced. If merged into the wrong base, verify resulting repository state before any further integration action. |
| Expected-base OPEN PR, with no conflicting result | Reuse the existing PR after verifying head SHA, base, changed-file scope and reviewed candidate identity. Do not create a duplicate. |
| Expected-base MERGED PR, with no conflicting result | Do not create another PR. Enter recovery/verification; verify merge commit, feature ancestry, origin/main and reviewed candidate identity before continuing. |
| Expected-base CLOSED, not merged | Record the existing PR and its state; do not blindly recreate. Require an explicit replacement disposition. If replacement creation is not already authorized by the current workflow, obtain that authorization; prefer INTEGRATION_BLOCKED over guessing. |
| Multiple same-head PRs | Inspect all results. Any wrong-base result blocks as above, even alongside a correct-base OPEN PR. If the remaining state cannot be unambiguously reconciled, enter INTEGRATION_BLOCKED rather than guessing which PR represents the approved integration. |

PR creation is permitted only after complete discovery and reconciliation establish no conflicting same-head PR, no reusable expected-base PR, and no existing merge requiring recovery verification; current authorization must permit creation and reviewed content identity must remain valid. A prior closed expected-base PR additionally requires the explicit replacement disposition above. Record discovered PRs and any conflict/disposition in the integration report and recovery checkpoint. Explicit disposition is a decision gate, not blanket permission to mutate an existing PR or bypass content/review gates.

## Idempotent recovery from uncertain actions

Never repeat a remote mutation until current remote state is checked. Read-only checks are safe to repeat; mutations are not presumed to have failed because output or context was lost.

| Uncertain action | Verify before deciding next action |
|---|---|
| Commit | Inspect HEAD, relevant log/reflog, parent, tree, message and exact scope. Reuse the verified intended commit; do not create another merely because its result was lost. Unexpected commit/content is a blocker. |
| Push | Inspect the live remote feature ref (for example git ls-remote --heads origin with the exact branch) and compare SHA. Equal means already pushed. Missing/older state requires ancestry and authorization checks before normal push; divergent/unexpected state blocks. |
| PR creation | Apply PR discovery and disposition above: query all same-repository/head PRs across bases and states, never only the expected head + base. Reconcile number, state, base, head, remote head SHA and reviewed candidate before any retry. Classify evidence CONFIRMED / STALE / CONFLICTING / NOT VERIFIED; wrong-base evidence is CONFLICTING and causes INTEGRATION_BLOCKED pending explicit disposition. |
| Merge | Check PR state and merge SHA, fetch origin/main, verify parents, feature ancestry and resulting content. If already merged, continue verification. If remote state cannot be determined, block rather than merge again. |

Record definitely completed, definitely not completed, and uncertain actions separately. Never infer success from a local remote-tracking ref alone. See [continuity recovery](token-continuity.md) before continuing the interrupted phase.
