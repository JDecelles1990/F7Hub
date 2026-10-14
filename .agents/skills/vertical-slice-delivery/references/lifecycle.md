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

Testing is its own semantic state: generated code is untrusted. Determine applicable unit, database, service, GUI, integration, native Windows, and regression coverage using specialized guidance and the selection procedure below. Runtime alone never waives a required suite. Cover success, failure, cancellation, state recovery, and data integrity where applicable. Record why a category is inapplicable; never relabel an unexecuted required test as inapplicable to pass a gate.

### Mandatory selection before execution

Before running any suite, classify its relationship to the candidate and record its evidence or execution disposition. Selection categories are neither lifecycle states nor PASS / FAIL outcomes.

| Selection category | Relationship and required disposition |
|---|---|
| DIRECTLY AFFECTED | Changed functionality or acceptance contract; fresh focused validation required. |
| TRANSITIVELY AFFECTED | A shared service, dependency, API, state, security or execution boundary could affect it; fresh relevant regression required. |
| UNCHANGED / EVIDENCE APPLICABLE | No relevant input change and independently verified prior evidence meets provenance requirements; RETAINED PASS permitted. |
| NOT APPLICABLE | No technical relationship to the change; record the rationale and do not execute automatically. |
| REQUIRED BY GATE | Explicit project, safety, security, user or review requirement; must run unless valid retained evidence satisfies that specific gate. |

REQUIRED BY GATE also applies alongside an impact category; record the requirement source and whether it demands fresh execution. It cannot be displaced by NOT APPLICABLE, and retained evidence cannot replace a gate that explicitly requires a fresh run. Unchanged behavior without applicable prior evidence does not qualify for UNCHANGED / EVIDENCE APPLICABLE; record unchanged inputs and missing evidence, then execute validation if required.

Use a compact matrix in the existing implementation/review evidence rather than introducing another framework:

| Suite / criterion | Impact category and dependency rationale | Mandatory gate / source, or none | Relevant input identities / prior evidence | Planned execution or reuse and rationale |
|---|---|---|---|---|
| | | | | |

Apply this order:

1. Inspect the candidate diff and dependencies, including transitive inputs.
2. Build the compact test-impact matrix.
3. Identify explicit mandatory validation gates.
4. Run focused tests of changed behavior.
5. Run affected integration and regression tests.
6. Reuse independently verified applicable evidence for unchanged suites under [retained evidence](review-gates.md#retained-evidence).
7. Run broader regression only for an actual gate, unresolved risk, relevant input drift, or concrete failure; record the reason and affected scope.

Never rerun a full suite simply because a previous slice ran it. Required unavailable evidence remains NOT RUN or BLOCKED and must be resolved through necessary validation before approval; it cannot support READY_FOR_REVIEW.

### Cross-language impact

For a Python -> AHK UI integration change, validate the changed integration contract with fresh evidence; do not automatically rerun the entire AHK feature suite. If the change affects the shared host, input routing, IPC acknowledgments, editor persistence, security or process lifecycle, include focused tests of those affected boundaries. Broaden coverage only when dependency impact or an explicit gate justifies it. Native Windows validation remains required where applicable; mocked or offscreen checks do not establish native behavior.

### Bounded execution and correction

- Failure circuit breaker: after any execution that fails, hangs, times out, terminates inconclusively, or leaves potentially surviving test-owned processes or uncertain state, Codex MUST stop automatic retries of that execution. Preserve failure/completion status, command, environment, candidate and relevant input evidence; safely inspect the failure and surviving state; determine whether an implementation, harness, fixture or environment cause is identifiable; record the diagnosis and next corrective action. Resume affected testing only when the conditions below and safe process/fixture/state preconditions are satisfied.
- Verified relevant correction: rerun failed or inconclusive execution only after verifying and recording a change that plausibly addresses the observed failure, such as corrected production implementation, harness or fixture, a repaired environment dependency, or a resolved process, lock or resource condition. Merely increasing the timeout, restarting an unchanged harness or modifying a retry counter is not sufficient.
- Materially different diagnostic probe: a separate bounded diagnostic may investigate a specific failure hypothesis without changing production code, but MUST differ meaningfully in purpose, execution path, instrumentation or controlled conditions. Record the hypothesis and changed probe; do not disguise the original failing execution as another attempt. The diagnostic does not authorize rerunning the unchanged failing harness afterward; that rerun still requires a verified relevant correction and safe state.
- No unchanged automatic retries merely because the failure is described as flaky, a rationale was documented, the retry count is finite, more time or tokens are available, full regression or independent review remains required, a passing result is desired, or the unchanged test previously passed. Required fresh independent checks are not an exception to the failure circuit breaker. If a mandatory check cannot safely complete, report FAIL for an established failure or BLOCKED for unresolved safe execution/completion, preserve evidence and stop; never manufacture completion through repeated unchanged execution.
- Do not restart an entire regression suite after every unrelated documentation correction. Corrections trigger testing of affected behavior and dependencies, not automatic repetition of every historical suite.
- Use bounded execution time and deterministic cleanup of test-owned processes/fixtures; preserve unrelated processes and user state. Apply scoped native safeguards, including external termination where in-process timers cannot stop a blocked callback.
- Preserve failed or incomplete execution evidence under [long-test continuity](token-continuity.md#long-tests-and-incremental-evidence). A timeout is not PASS.
- Define bounded attempts before execution and honor user/scoped retry limits. An attempt limit does not authorize an unchanged retry after the failure circuit breaker applies. Verify surviving-process ownership, cleanup and fixture/state safety before any permitted execution; preserve unrelated processes and user state.

### Selection examples

These examples illustrate dependency analysis, not automatic waivers or instructions to run against an in-progress candidate.

| Change | Fresh validation | Retained evidence / broader coverage |
|---|---|---|
| A: Rename AHK Guide window | Exact title; Python -> AHK open/focus; window identity and acknowledgment; Alt+F7 toggle; negative confirmation path. | Topic navigation, formatting, archive, opacity, and unchanged GUI/Integration regressions may remain RETAINED only when their relevant inputs and environment are verified unchanged. Shared-host/routing/persistence/security/process changes require affected focused regressions; broaden for demonstrated dependency impact or mandatory gates. |
| B: New SQLite migration | Migration, constraints, foreign keys, transactions, affected queries/services, failure and recovery paths; applicable integrity_check must return ok and foreign_key_check zero violations on isolated validation data. | Shared-schema changes may require broader database regression. Prior evidence cannot validate changed schema or affected dependencies. |
| C: Documentation-only correction | Documentation accuracy, references, manifest/aggregate and unchanged relevant input verification. | Do not rerun application suites solely because Markdown changed. Changed acceptance contracts, dependencies or explicit gates still require applicable validation. |

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
