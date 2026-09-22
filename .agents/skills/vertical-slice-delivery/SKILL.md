---
name: vertical-slice-delivery
description: Plan, implement, test, document, independently review, integrate, or resume a bounded F7Hub vertical slice with evidence gates and safe context continuity. Use for slice delivery and status requests.
---

# F7Hub Vertical Slice Delivery

Version: 0.1

Own slice state, scope, transitions, evidence, continuity, recovery, reporting, and Git/GitHub safety. Preserve explicit user scope and authorization. This skill does not authorize external actions merely by being loaded.

## Select the phase

| Intent | Entry behavior |
|---|---|
| Plan Slice 024 | Inspection-only PLAN; propose READY or BLOCKED. |
| Implement approved Slice 024 | Verify approved plan and baseline before editing. |
| Review Slice 024 | Independent read-only REVIEW. |
| Integrate approved Slice 024 | Verify review approval, integration authorization, and Git gates. |
| Resume Slice 024 / RESUME | RECOVERING audit, then continue the interrupted phase. |
| What's the state of Slice 024? | Read-only reconciliation of live evidence and reports. |
| Continue | Identify current state, last verified gate, and existing authorization; choose the safest action within the same phase. |

Ambiguous continuation never automatically means implement, commit, push, merge, or start another slice. If mutation authorization is unclear, remain in read-only status/recovery. Already-granted authorization persists across sessions only for the same slice, scope, reviewed candidate, and operation; expansion requires new authorization.

## Lifecycle states and gates

The complete 17-state vocabulary is:

```text
UNPLANNED
PLANNED
IMPLEMENTING
TESTING
DOCUMENTING
READY_FOR_REVIEW
REVIEWING
CHANGES_REQUIRED
APPROVED
INTEGRATING
MERGED
CLOSED
BLOCKED
FAILED_VALIDATION
INTEGRATION_BLOCKED
CHECKPOINTED
RECOVERING
```

Normal delivery: PLAN -> IMPLEMENT -> TEST -> DOCUMENT -> INDEPENDENT REVIEW -> INTEGRATE -> VERIFY -> CLOSE. Corrections repeat implementation, testing, documentation, and independent review. Planning the next slice requires a new user instruction.

Every transition needs recorded evidence. Read [lifecycle](references/lifecycle.md) for the transition table and phase procedures. No shortcut from implementation to review readiness; all required tests and affected documentation must be complete. Only approved content may integrate. MERGED is not CLOSED until remote and local main are verified.

## Continuity first

Before a substantive operation, assess GREEN / AMBER / RED / UNKNOWN using reliable host capacity if available, otherwise observable pressure signals without invented counts. TOKEN PRESSURE NEVER ADVANCES A LIFECYCLE GATE.

Read [token continuity](references/token-continuity.md) at task entry and whenever pressure or session continuity changes. RED or untrustworthy continuity means checkpoint and stop, with no new substantive work or Git/GitHub mutations. RESUME means CHECKPOINTED -> RECOVERING -> original interrupted phase, after reconciliation; it never means start over or advance automatically.

## Ownership and escalation

Read root AGENTS.md, ROOT.md, and Docs/19_DocumentationIndex.md; resolve actual current filenames. Discover relevant available subsystem skills rather than assuming they exist: architecture, SQLite, AutoHotkey v2, PowerShell, PySide6/pyqt6, testing, documentation, code-review, and security. Use only guidance compatible with F7Hub ownership; a skill named pyqt6 does not authorize replacing PySide6.

Technical procedures belong to subsystem skills and canonical documents. If an optional skill is absent, use canonical F7Hub documentation and verified implementation. If required guidance is missing and proceeding would require guessing, enter BLOCKED.

Unexpected destructive migration, core relationship change, authentication/security-boundary change, major dependency, repository restructuring, plugin architecture change, IPC contract change, framework change, cross-language ownership change, or destructive Git recovery requires explicit review before action. Stop, record impact and alternatives, and request the missing decision. Pressure makes these gates stricter, never weaker.

## Phase resources

- All delivery phases: [lifecycle](references/lifecycle.md).
- Checkpoint, pressure, or RESUME: [token continuity](references/token-continuity.md).
- Baseline, integration, or uncertain Git action: [Git safety](references/git-safety.md).
- Review readiness, independent review, or changed approved content: [review gates](references/review-gates.md).

Use the relevant report template; do not load every template by default:

- [Slice plan](templates/slice-plan.md)
- [Implementation report](templates/implementation-report.md)
- [Review report](templates/review-report.md)
- [Integration report](templates/integration-report.md)
- [Recovery checkpoint](templates/recovery-checkpoint.md)

Reports distinguish PASS, FAIL, NOT RUN, BLOCKED, and CHECKPOINTED. Test results use PASS / FAIL / NOT RUN / BLOCKED; CHECKPOINTED describes execution continuity, not a passing test. Uninspected facts are NOT VERIFIED.

## Evolution

After approximately Slices 024–026, propose a v0.2 review of useful/ignored gates, exhaustion behavior, repeated prompts, defects caught, Git mistakes prevented, test/runtime costs, and documentation accuracy. Do not automatically revise the skill or start the next slice.
