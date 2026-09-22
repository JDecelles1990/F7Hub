# Independent Review Gates

## Readiness and independence

Required tests and affected documentation must be complete before READY_FOR_REVIEW. Identify exact candidate/base, scope, exclusions and evidence in the [implementation report](../templates/implementation-report.md).

Use a separate reviewer/agent/session from the implementer. Do not label implementer self-checks independent review. If an independent reviewer is unavailable, report BLOCKED and leave approval pending. Supply raw candidate/source/tests and evidence locations; implementation reports are claims to verify, not authority.

Review is READ ONLY with respect to the candidate and user state. Do not edit, repair, stage, commit, push, merge, restore, reset, or clean. Run applicable tests only with isolated test data and external artifacts where necessary; inspect status before/after. External review reports/checkpoints must follow [checkpoint security](token-continuity.md). A review discovering a defect reports it rather than fixing it.

## Fresh evidence

Independently verify:

- Root, branch, HEAD, base, tracked plus untracked scope, staged state, protected paths and candidate content identity.
- Implementation against approved objective, acceptance criteria, exclusions and architecture.
- Relevant tests, actual commands/results, success/failure/recovery coverage, and missing validation.
- Security and failure paths using appropriate specialized guidance.
- Database state, constraints, transaction/integrity evidence where relevant; no destructive live-data checks.
- Native Windows behavior and inspected evidence for physical/layout claims; offscreen tests alone do not establish native behavior.
- Synchronized documentation against verified behavior; no planned capability presented as verified.
- Final candidate/status identity after review to detect drift or test artifacts.

Run required independent checks and inspect actual outputs/artifacts. Record reviewer identity, environment, candidate, commands/results, finding severity/location and limitations in the [review report](../templates/review-report.md).

## Retained evidence

Retained evidence is usable only when its provenance, command/result, environment applicability and candidate binding can be verified independently. Label it retained, not freshly run. Changed implementation/test content requires affected reruns; unchanged evidence may be reused when the reviewer explicitly justifies applicability. Missing results, an inaccessible artifact, or an implementation report saying PASS is not proof. Required unavailable evidence blocks approval; do not waive it merely for runtime or token savings.

## Decisions and approval binding

The decision is exactly one of:

| Decision | Lifecycle consequence |
|---|---|
| APPROVE | APPROVED; required evidence complete, no blocking findings. |
| APPROVE WITH NOTES | APPROVED; only nonblocking follow-ups, explicitly identified. |
| CHANGES REQUIRED | CHANGES_REQUIRED; bounded fixes then implementation/testing/documentation/review again. |
| BLOCKED | BLOCKED; identify missing required evidence or review prerequisite. Under context stop, checkpoint the interrupted REVIEWING phase. |

No approval under RED unless all required independent evidence already exists. Incomplete review cannot become APPROVED through exhaustion.

Bind approval to base SHA, exact candidate content, approved file list and review evidence. Post-review candidate changes invalidate affected approval and require renewed review. A change of base also requires compatibility evaluation under [Git safety](git-safety.md). Neither a conflict-free merge nor an unchanged filename list alone proves content identity. Conflict resolution requires renewed validation/review. Approval never itself authorizes staging, commit, push or merge.
