# Lifecycle and Evidence Gates

## Engineering principle and delivery order

Preserve F7Hub's engineering principle: UNDERSTAND -> INSPECT -> PLAN -> IMPLEMENT -> TEST -> REVIEW -> DOCUMENT. Implementation self-review informs documentation. Delivery then requires PLAN -> IMPLEMENT -> TEST -> DOCUMENT -> INDEPENDENT REVIEW -> INTEGRATE -> CLOSE. Documentation precedes independent review so the reviewer verifies both behavior and its synchronized description.

Maintain a compact record: slice identity, state, interrupted phase if any, baseline, approved scope, authorization, last completed gate, next gate, and evidence locations. Record transitions as from/to, reason, evidence, and authorization where needed. Reports describe actual state, not intended completion. READY is a design-plan result; current implementation-baseline readiness is a separate gate. APPROVE is a review decision; none is an extra lifecycle state.

## Normal transitions

| From | To | Evidence required |
|---|---|---|
| UNPLANNED | PLANNED | Inspection sufficient for a bounded READY plan; approval recorded separately. |
| PLANNED | IMPLEMENTING | Approved plan, current baseline gate, branch and exact scope. |
| IMPLEMENTING | TESTING | Bounded implementation and self-review complete enough to validate; exact candidate recorded. |
| TESTING | DOCUMENTING | All required tests PASS for the candidate; commands/results and applicability recorded. |
| DOCUMENTING | READY_FOR_REVIEW | Affected docs synchronized, required evidence complete, scope audited, reproducible candidate manifest recorded. |
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
2. Read actual current Roadmap, Todo, CURRENT_STATE/checkpoint, ChangeLog, relevant canonical owners, source/tests, and deferred adjacent work. Where available, MUST inspect the immediately preceding integration/closure report and unresolved carry-forward notes before defining scope. Notes are planning inputs, not automatic scope; explicitly select, defer, or escalate each relevant note with rationale.
3. SEARCH -> IDENTIFY -> REUSE -> EXTEND -> CREATE ONLY IF NECESSARY. Compare candidate slices and select the smallest correct bounded one supported by current evidence.
4. Produce [slice plan](../templates/slice-plan.md): report design readiness and current implementation-baseline readiness separately, with objective, scope/exclusions, acceptance criteria, validation, likely files, architecture/database impact, branch and risks. A READY design may have a BLOCKED FOR IMPLEMENTATION checkout. Do not implement or treat design readiness as approval.

## IMPLEMENT

Require approved plan; recheck baseline before edits. Establish one feature branch only after gates pass, normally in C:\Dev\F7Hub. Extra worktrees require an explicit recovery, integration, isolation, or parallel-development reason; record it. Keep the approved objective bounded, preserve unrelated work, and avoid unrelated refactors. Unexpected architectural expansion enters BLOCKED for explicit review.

### Authoritative mutation and subsequent refresh

For database write -> GUI refresh, filesystem write -> reconstruction, or API mutation -> local re-query, MUST record OPERATION OUTCOME (authoritative mutation succeeded, failed, or remains uncertain) separately from POST-OPERATION OUTCOME (refresh/reconstruction/display succeeded, failed, or was not attempted). A committed mutation followed by failed refresh MUST NOT be reported as a failed mutation. Define transaction/commit boundaries, accurate user/report messaging, and a safe refresh-only recovery path. SHOULD assess idempotency and duplicate prevention before retrying. When mutation outcome is uncertain, verify authoritative state before repeating it; refreshing does not authorize a second write.

Implementation reports MUST identify new/changed trust boundaries and invariants, including applicable concurrency/transaction, filesystem/process/security, and data-integrity risks. Record unaffected or inapplicable surfaces with rationale so review can target changed and transitively affected behavior.

## TEST

Testing is its own semantic state: generated code is untrusted. Determine applicable unit, database, service, GUI, integration, native Windows, and regression coverage using specialized guidance. Prefer focused tests, then affected suites, then full required regression; runtime alone never waives a required suite. Cover success, failure, state recovery, and data integrity where applicable. Record why a category is inapplicable; never relabel an unexecuted required test as inapplicable to pass a gate.

Record exact command, candidate identity, environment, result, counts, exit status and evidence location per suite. For native GUI checks, use the observable readiness gate in [review gates](review-gates.md). Required FAIL enters FAILED_VALIDATION; required NOT RUN or BLOCKED prevents readiness. A focused pass does not replace required regression. Follow [continuity](token-continuity.md) for long tests and lost output.

## DOCUMENT

Identify affected, potentially affected, and unaffected owner documents with reasons. Synchronize only affected documentation with verified behavior and honest limitations. Do not present intended/untested behavior as implemented or verified. No broad retrospective cleanup. Record a no-change rationale if no owner requires edits. Complete the [implementation report](../templates/implementation-report.md) before independent review.

## REVIEW and correction loop

Apply [review gates](review-gates.md). Review is independent and read-only. CHANGES REQUIRED returns through IMPLEMENT -> TEST -> DOCUMENT -> REVIEW AGAIN; corrections do not inherit blanket approval. APPROVE WITH NOTES can contain only nonblocking follow-ups, not required fixes disguised as notes.

## INTEGRATE, VERIFY, CLOSE

Only APPROVED work, explicitly authorized for integration, enters [controlled Git integration](git-safety.md). Use the [integration report](../templates/integration-report.md). Confirm merge and feature ancestry, origin/main, safe local-main synchronization, final scope and preserved unrelated work. Normally finish on main with HEAD == origin/main and a clean tree. If unrelated work prevents cleanliness, preserve it and report the verified exception; never clean to satisfy a target. Unresolved synchronization or content verification prevents CLOSED.

Closure records actual validation, remaining limitations and deferred work. A newly requested next-slice plan begins from current repository evidence; never automatically start its planning or implementation.

## Handoff authority and carry-forward notes

Live verified Git state MUST govern branch/HEAD/index/worktree facts. Verified review/integration/closure artifacts may establish completed lifecycle facts; check their candidate/base and actual completion evidence before accepting them. If CURRENT_STATE, Todo, checkpoints or similar metadata disagree, label STALE HANDOFF METADATA with claim, verified fact, and source. MUST NOT roll back live state to make old prose true, or synchronize stale metadata unless the current task authorizes that edit. After closure, the verified closure report may temporarily be the authoritative lifecycle handoff until canonical documentation is synchronized.

Review and integration/closure reports MUST contain `Carry-forward notes`, explicitly `None` if empty. Each note records blocking/nonblocking, rationale, code/test/documentation/architecture/cleanup work type, owner/future phase if known (otherwise unknown), and resolution status/evidence. A blocking note prevents its applicable gate; deferral cannot disguise a required correction. Preserve unresolved notes and their source across correction, integration, closure, and recovery; resolve explicitly rather than silently dropping them. Next-slice PLAN inspects them without automatically adopting them.
