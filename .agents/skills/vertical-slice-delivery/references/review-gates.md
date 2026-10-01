# Independent Review Gates

## Readiness and independence

Required tests and affected documentation must be complete before READY_FOR_REVIEW. Identify exact candidate/base, scope, exclusions and evidence in the [implementation report](../templates/implementation-report.md).

## Candidate manifest contract

READY_FOR_REVIEW MUST include `candidate-manifest.json` or an established repository equivalent stored outside the candidate/worktree with the evidence. Record schema/version, root, branch, HEAD, reviewed base, creation time, exact candidate path inventory, and aggregate identity. Each path MUST identify tracked/untracked status, change kind (including deletion), Git-normalized identity where applicable, and working-byte hash when byte preservation/behavior matters. Record modes/symlink targets where applicable; represent deletions explicitly rather than hashing a missing file. Classify protected/unrelated paths separately; audit both tracked diffs and untracked additions against the allowlist.

Document algorithms, Git normalization/filter context, path ordering, encoding, delimiters/newlines, base contribution, and exclusions sufficiently to reproduce the aggregate. Preserve an existing reliable recipe rather than silently substituting one. For example, an existing UTF-8/LF recipe may hash `base<TAB>SHA<LF>` followed by sorted `path<TAB>git_blob<LF>` records; this is an example, not a mandated new algorithm. Status/mode metadata not included in a legacy aggregate MUST be verified separately. Compare Git-normalized identities for reviewed commit content and raw hashes for exact-byte requirements. A filename list, branch, or raw Windows hash alone is insufficient.

Preserve prior manifests when candidates change; provide per-path comparison as well as aggregate comparison so a reviewer can locate drift, evaluate retained evidence, and bind integration to reviewed bytes. Evidence produced before final documentation edits MUST name its tested candidate and justify any later candidate difference through transitive inputs. Do not circularly include a manifest/report in its own candidate aggregate.

## Evidence provenance

Provenance MUST be recorded separately from PASS / FAIL / NOT RUN / BLOCKED outcomes and from lifecycle state:

| Provenance | Definition |
|---|---|
| FRESH | Executed against the current candidate during the current validation/review cycle. If the final aggregate later changes, record the original tested identity and verified unchanged relevant inputs explicitly. |
| RETAINED | Executed previously and independently established as still valid for the current candidate. |
| NOT RUN | Not executed and not claimed as validation evidence. |
| BLOCKED | Required or desired validation could not execute because of a documented blocker. |

RETAINED MUST name the originating command/suite, accessible result artifact/log and completion evidence, original candidate identity, current candidate/transitive-input applicability, relevant environment applicability, and reuse rationale. `Previously passed` alone never qualifies. An inspected screenshot or inspected old log does not turn a prior execution into FRESH execution; distinguish fresh artifact inspection from retained execution. These four provenance values add no lifecycle states.

Use a separate reviewer/agent/session from the implementer. Do not label implementer self-checks independent review. If an independent reviewer is unavailable, report BLOCKED and leave approval pending. Supply raw candidate/source/tests and evidence locations; implementation reports are claims to verify, not authority.

Review is READ ONLY with respect to the candidate and user state. Do not edit, repair, stage, commit, push, merge, restore, reset, or clean. Run applicable tests only with isolated test data and external artifacts where necessary; inspect status before/after. External review reports/checkpoints must follow [checkpoint security](token-continuity.md). A review discovering a defect reports it rather than fixing it.

## Fresh evidence

Independently verify:

- Root, branch, HEAD, base, tracked plus untracked scope, staged state, protected paths and candidate content identity.
- Implementation against approved objective, acceptance criteria, exclusions and architecture.
- Relevant tests, actual commands/results, success/failure/recovery coverage, and missing validation.
- Security and failure paths using appropriate specialized guidance.
- Database state, constraints, transaction/integrity evidence where relevant; no destructive live-data checks.
- Native Windows behavior and inspected evidence for physical/layout claims; wait for observable usable/idle/loading-complete state before judging the GUI. If readiness times out, record failure or a blocker, not PASS. Avoid arbitrary long sleeps when observable state exists; offscreen tests alone do not establish native behavior.
- Synchronized documentation against verified behavior; no planned capability presented as verified.
- Final candidate/status identity after review to detect drift or test artifacts.

Run required independent checks and inspect actual outputs/artifacts. Record reviewer identity, environment, candidate, commands/results, finding severity/location and limitations in the [review report](../templates/review-report.md).

Review MUST use the implementation report's new/changed trust boundaries, invariants and risk surfaces as inspection inputs, verifying the claims independently. Focus fresh evidence on changed concurrency/transaction, filesystem/process/security and data-integrity boundaries while still verifying scope, candidate identity, baseline compatibility, regression evidence and lifecycle compliance. Include unchanged but transitively affected areas; risk focus does not waive applicable gates.

## Native GUI record

Native/manual GUI validation MUST persist `native-validation.result.json` (or an established equivalent) with candidate identity/manifest, command or manual procedure/harness identity, process exit code, platform/relevant environment, actual window dimensions, observable-ready condition and its observed outcome, assertions performed and results, overall PASS/FAIL (or BLOCKED/INCOMPLETE when no conclusion is possible), screenshot inventory/paths, timezone-qualified timestamps, and visual/manual observations. Record null and `not captured` if exit status is unavailable; never imply process success from screenshots. Distinguish simulated/injected boundary fixtures from native OS behavior.

Screenshots alone do not prove process success; exit 0 alone does not prove visual correctness. Inspect captures after observable usable/idle/loading-complete readiness and record what was checked. Missing exit evidence is a stated limitation, not an invented 0; a required process-success criterion without independently recoverable evidence blocks the gate. Separate assertion results, process outcome, and visual observations.

## Retained evidence

Retained evidence requires an accessible prior command/result, applicable environment, and verified unchanged relevant inputs: production code, tests, schema, configuration, dependencies, and other transitive inputs that could affect that suite. An identical whole-candidate content identity suffices for input comparison; otherwise justify the unchanged relevant inputs explicitly. If any relevant input changed, rerun the affected suite. Label retained evidence and record its applicability rationale, not a fresh PASS. Missing results, an inaccessible artifact, or an implementation report saying PASS is not proof. Required unavailable evidence blocks approval; do not waive it merely for runtime or token savings.

## Correction and candidate drift matrix

After CHANGES_REQUIRED and corrections, MUST preserve old/new manifests and classify every reviewed path CHANGED or UNCHANGED using relevant normalized/raw identities; additions/deletions are CHANGED. Include changes to baseline, modes, configuration, dependencies, harnesses and other inputs, even outside the reviewed path inventory. Explain each correction against its finding and approved scope.

| Reviewed path / input | Before / after identity | CHANGED / UNCHANGED | Finding / reason |
|---|---|---|---|
| | | | |

Map each previously executed suite to its transitive inputs, not just its test filenames:

| Suite / prior artifact | Transitive inputs and drift | Disposition | Candidate / environment justification | New evidence |
|---|---|---|---|---|
| | | FRESH rerun required / RETAINED evidence valid / evidence invalidated / not applicable | | |

Changed inputs that can affect tested behavior invalidate prior evidence and require a FRESH affected rerun; mark missing reruns explicitly. Not applicable requires a scope/behavior rationale, never an expedient waiver. Unchanged relevant inputs with verified provenance permit RETAINED evidence even if unrelated documentation changed. Do not mechanically rerun expensive unaffected suites or retain affected results merely to save time. Independent correction review verifies this matrix and fresh risk evidence before binding a new approval; unchanged approval is not inherited automatically.

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
