# Lifecycle and Evidence Gates

## Engineering principle and delivery order

Preserve F7Hub's engineering principle: UNDERSTAND -> INSPECT -> PLAN -> IMPLEMENT -> TEST -> REVIEW -> DOCUMENT. Implementation self-review informs documentation. Delivery then requires PLAN -> IMPLEMENT -> TEST -> DOCUMENT -> INDEPENDENT REVIEW -> INTEGRATE -> CLOSE. Documentation precedes independent review so the reviewer verifies both behavior and its synchronized description.

Maintain a compact record: slice identity, state, interrupted phase if any, baseline, approved scope, authorization, last completed gate, next gate, and evidence locations. Record transitions as from/to, reason, evidence, and authorization where needed. Reports describe actual state, not intended completion. READY is a plan result; APPROVE is a review decision; neither is an extra lifecycle state.

## Normal transitions

| From | To | Evidence required |
|---|---|---|
| UNPLANNED | PLANNED | Inspection sufficient for a bounded READY plan; approval recorded separately. |
| PLANNED | IMPLEMENTING | Approved plan, current baseline gate, branch and exact scope. |
| IMPLEMENTING | TESTING | Bounded implementation and self-review complete enough to validate; exact candidate recorded. |
| TESTING | DOCUMENTING | All required tests PASS for the candidate; commands/results and applicability recorded. |
| DOCUMENTING | READY_FOR_REVIEW | Affected docs synchronized, required evidence complete, scope audited. |
| READY_FOR_REVIEW | REVIEWING | Independent reviewer and exact reviewed candidate identified. |
| REVIEWING | CHANGES_REQUIRED | Review decision CHANGES REQUIRED with actionable findings. |
| CHANGES_REQUIRED | IMPLEMENTING | Findings mapped to bounded fixes within approved scope; escalation resolved if needed. |
| REVIEWING | APPROVED | APPROVE or APPROVE WITH NOTES, with no blocking findings or missing required evidence. |
| APPROVED | INTEGRATING | Integration authorization plus reviewed content, scope, and remote freshness gates. |
| INTEGRATING | MERGED | Actual merge verified against approved commit and PR. |
| MERGED | CLOSED | Remote/local main, merge ancestry, content and preservation verified; closure report. |

No other forward transition is implicit. A code/test change during documentation returns to IMPLEMENTING and TESTING before review readiness. Post-review changes invalidate affected approval: return to CHANGES_REQUIRED with the changed scope recorded, then implement/test/document/review again. Prior unaffected evidence may be retained under [review gates](review-gates.md), never assumed to validate changed content.

## Exceptions and recovery

| State | Entry evidence | Permitted exit |
|---|---|---|
| FAILED_VALIDATION | Required test failure, including focused checks during implementation. | IMPLEMENTING for fixes; TESTING if only an environmental cause was resolved and candidate is unchanged. Record resolution and rerun required checks. |
| BLOCKED | Concrete missing evidence, authorization, technical dependency, or architecture decision; save interrupted phase. | Return to interrupted phase only after resolution and applicable gate checks; RECOVERING first after a continuity break. |
| INTEGRATION_BLOCKED | Main advanced, scope/content mismatch, conflict, or unresolved Git/remote state. | INTEGRATING only after compatibility, review, validation, and authorization gates are restored; CHANGES_REQUIRED if candidate changes are needed. RECOVERING first after a continuity break. |
| CHECKPOINTED | Safe-stop checkpoint records interrupted state/phase and completed/incomplete operations. | RECOVERING only. |
| RECOVERING | RESUME or uncertain continuity, with or without a final checkpoint. | Original interrupted phase after sufficient reconciliation; BLOCKED or INTEGRATION_BLOCKED for material conflicts. |

Any active phase may enter BLOCKED, CHECKPOINTED, or RECOVERING when supported by evidence; integration-specific blockers use INTEGRATION_BLOCKED. Checkpoint an existing blocker without erasing it. After recovery, independently verified completed operations may support ordinary transitions, recorded individually; recovery itself supplies no approval. An uncertain completed merge is recorded as MERGE_COMPLETED_VERIFICATION_PENDING, an operation marker, not an eighteenth state.

## PLAN: inspection only

1. Verify root, branch/main, HEAD, index, tracked and untracked state; fetch origin and verify origin/main under [Git safety](git-safety.md). Fetch is the permitted metadata refresh, not permission to switch branches or edit.
2. Read actual current Roadmap, Todo, CURRENT_STATE, ChangeLog, relevant canonical owners, source/tests, and deferred adjacent work. Reconcile dated prose with live evidence; do not invent a slice from old suggestions.
3. SEARCH -> IDENTIFY -> REUSE -> EXTEND -> CREATE ONLY IF NECESSARY. Compare candidate slices and select the smallest correct bounded one supported by current evidence.
4. Produce [slice plan](../templates/slice-plan.md): READY or BLOCKED, objective, baseline, scope/exclusions, acceptance criteria, validation, likely files, architecture/database impact, branch and risks. Do not implement or automatically treat READY as approval.

## IMPLEMENT

Require approved plan; recheck baseline before edits. Establish one feature branch only after gates pass, normally in C:\Dev\F7Hub. Extra worktrees require an explicit recovery, integration, isolation, or parallel-development reason; record it. Keep the approved objective bounded, preserve unrelated work, and avoid unrelated refactors. Unexpected architectural expansion enters BLOCKED for explicit review.

## TEST

Testing is its own semantic state: generated code is untrusted. Determine applicable unit, database, service, GUI, integration, native Windows, and regression coverage using specialized guidance. Cover success, failure, state recovery, and data integrity where applicable. Record why a category is inapplicable; never relabel an unexecuted required test as inapplicable to pass a gate.

Record exact command, candidate identity, environment, result, counts, exit status and evidence location per suite. Required FAIL enters FAILED_VALIDATION; required NOT RUN or BLOCKED prevents readiness. A focused pass does not replace required regression. Follow [continuity](token-continuity.md) for long tests and lost output.

## DOCUMENT

Identify affected, potentially affected, and unaffected owner documents with reasons. Synchronize only affected documentation with verified behavior and honest limitations. Do not present intended/untested behavior as implemented or verified. No broad retrospective cleanup. Record a no-change rationale if no owner requires edits. Complete the [implementation report](../templates/implementation-report.md) before independent review.

## REVIEW and correction loop

Apply [review gates](review-gates.md). Review is independent and read-only. CHANGES REQUIRED returns through IMPLEMENT -> TEST -> DOCUMENT -> REVIEW AGAIN; corrections do not inherit blanket approval. APPROVE WITH NOTES can contain only nonblocking follow-ups, not required fixes disguised as notes.

## INTEGRATE, VERIFY, CLOSE

Only APPROVED work, explicitly authorized for integration, enters [controlled Git integration](git-safety.md). Use the [integration report](../templates/integration-report.md). Confirm merge and feature ancestry, origin/main, safe local-main synchronization, final scope and preserved unrelated work. Normally finish on main with HEAD == origin/main and a clean tree. If unrelated work prevents cleanliness, preserve it and report the verified exception; never clean to satisfy a target. Unresolved synchronization or content verification prevents CLOSED.

Closure records actual validation, remaining limitations and deferred work. A newly requested next-slice plan begins from current repository evidence; never automatically start its planning or implementation.
