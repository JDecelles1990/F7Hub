# Root AGENTS.md refactor traceability — 2026-10-07

Review evidence for the instruction-only candidate in `C:\Dev\F7Hub-Agents-Cleanup`.
This is a historical migration audit, not a new policy authority or independent approval.
The full section classification was completed and this table was saved before replacing root.
The artifact is the one review file allowed by the user; 95 dispositions need durable inspection.

## Objective, scope and baseline

- Refactor root into a durable agent entry point; preserve global invariants and route details.
- Allowed changes: root `AGENTS.md` plus this single review artifact.
- No production code, migrations, tests, canonical numbered docs, ROOT or scoped instructions changed.
- Canonical checkout: `C:\Dev\F7Hub`, branch `feature/disk-space-assessment`,
  HEAD `aea520323cce4d38cf1d7ebff3da28810f3bb4cf`; dirty unrelated state is protected.
- Remote: `origin` = `https://github.com/JDecelles1990/F7Hub.git`.
- Current remote main independently verified with `git ls-remote origin refs/heads/main`:
  `adb0189304d547387f27c71dcb77bf09175c6df3`, matching local `origin/main`.
- Candidate branch: `docs/lean-root-agents`; isolated worktree HEAD/base is that main SHA.
- Old root: 2,624 lines, 42,798 raw bytes, UTF-8 without BOM, CRLF.
- Old Git blob: `dd3624d43d50191568eef86881583740fbf4220b`.
- Old raw SHA-256: `e3a65220e6c948be0c7f31cb0d299b9f7194bbbfde352f5a92c6c9e65dc3525c`.
- Canonical root and isolated old root were raw-byte identical before editing.
- Required instruction chain read; scoped PowerShell and AltF7Hub guidance also inspected.
- Repository `.agents/skills/` contains only `vertical-slice-delivery`.
  Architecture, sqlite-database, autohotkey-v2, powershell, pyqt6, testing, documentation,
  codex-orchestration, code-review and security skills were not found there.
  Existing canonical/scoped owners supply the necessary detail; no skill was invented.
- The delivery skill was inspected as an existing procedural/reporting owner.
  No slice implementation, independent approval or integration lifecycle was executed.

## Authority key

Paths are relative to the candidate repository. Section numbers identify inspected existing owners.
For a compressed rule, Root remains the always-visible obligation and the named owner supplies detail.
MOVE means removal of root duplication and routing to existing content; no destination was edited.

| Key | Existing authority |
|---|---|
| Root | `AGENTS.md`, candidate headings named in the table |
| ROOT | `ROOT.md`, project orientation, architecture, security, evidence and completion |
| INDEX | `Docs/19_DocumentationIndex.md`, canonical routing and documentation governance |
| PLAN | `Docs/Planning/AGENTS.md`, scoped planning, decisions, handoff and reports |
| FND | `Docs/Planning/Foundation/AGENTS.md`, phase ownership, approved-contract routing and safeguards |
| D06 | `Docs/06_SystemArchitecture.md`, overall layer/subsystem boundaries |
| D07 | `Docs/07_Database.md`, database strategy, migrations, transactions, indexes, FTS and tests |
| D09 | `Docs/09_SQLSchema.md`, physical schema and connection PRAGMAs |
| D11 | `Docs/11_AHKArchitecture.md`, AHK v2, clipboard and desktop automation |
| D12 | `Docs/12_PowerShellArchitecture.md`, execution/result contracts and validation |
| D13 | `Docs/13_PythonArchitecture.md`, GUI/services/domain/repositories, workers, errors and tests |
| D14 | `Docs/14_DesignPrinciples.md`, review, dependencies, least privilege and engineering principles |
| D15 | `Docs/15_NamingConventions.md`, migration and branch naming |
| D18 | `Docs/18_ChangeLog.md`, historical changes; old root remains recoverable from Git |
| PS | `PowerShell/AGENTS.md`, scoped runtime, execution, validation and security procedures |
| VSD | `.agents/skills/vertical-slice-delivery/SKILL.md` and its existing references/templates |

VSD resources cited below: `references/lifecycle.md`, `references/git-safety.md`,
`templates/slice-plan.md`, `templates/implementation-report.md`, `templates/review-report.md`.
Canonical sections were inspected progressively for the delegated subjects, rather than loading all 20 documents.
The unnumbered old Project Entry Point is KEEP_COMPRESS under Root entry point/progressive context.
The four obsolete sections are historical prompts, not instructions to implement them now.
Their technical invariants remain in Root/database owners; original wording remains in the recorded base Git blob.

## Complete numbered-section audit

| Old Section | Current Purpose | Disposition | New Authority | Reason | Risk if Removed |
|---|---|---|---|---|---|
| 0. Foundation Architecture Bridge | Cross-cutting owners and safeguards | KEEP_COMPRESS | Root: Foundation; FND | Keep phase routing, escalation, offline/data reminders; delegate topic lists | Parallel contracts or lost safety boundaries |
| 1. Purpose | Project objective and lifecycle | KEEP_COMPRESS | Root: purpose and workflow | Keep universal behavior without examples | Uncontrolled whole-system work |
| 2. Golden Rule | Small, clear, reversible engineering | MERGE | Root: purpose; D14 | Merge into purpose and scope principles | Complexity without justification |
| 3. Repository Root | Canonical root and existence checks | KEEP_COMPRESS | Root: purpose and evidence; ROOT | Keep path and inspection truth; folder inventory belongs to ROOT | Invented repository state |
| 4. Project Technology Ownership | Technology responsibilities | KEEP_COMPRESS | Root: technology ownership; D06 | Keep ownership table; route details | Responsibility transfer |
| 5. Primary Application Architecture | Layer direction | KEEP_COMPRESS | Root: architecture; D06 | Keep direction and boundary reminders; remove examples | GUI/persistence/execution bypass |
| 6. Architecture Style | Modular monolith and complexity restraint | KEEP_COMPRESS | Root: architecture; D06 | Keep style and speculative-infrastructure prohibition | Unnecessary distributed infrastructure |
| 7. Canonical Documentation | Canonical inventory and archive/research authority | MOVE | INDEX sections 7-8, 121-122 | Delegate inventory; keep root authority reminder | Stale competing inventory |
| 8. Documentation Navigation | Task entry reading sequence | KEEP_COMPRESS | Root: progressive context; INDEX section 134 | Keep progressive loading and minimal reading | Missed guidance or excessive context |
| 9. Documentation Authority | Authority order and conflict handling | KEEP_COMPRESS | Root: source of truth | Preserve exact source priority and escalation | Convenient lower-priority source wins |
| 10. Fact Discipline | Fact discipline | KEEP_COMPRESS | Root: evidence; PLAN evidence classification | Retain all labels and no invented facts | Unsupported claims |
| 11. Documentation Status vs Implementation Status | Approval/implementation/test distinction | KEEP_COMPRESS | Root: evidence; INDEX sections 4-5 | Keep distinction and test truth; delegate vocabularies | Approval mistaken for verification |
| 12. Documentation Routing | Canonical task router | MERGE | Root: progressive context; INDEX | Combine duplicate router rules into entry section | Competing reading maps |
| 13. Product / Requirements Tasks | Product requirements reading list | MOVE | INDEX sections 22-25 | Use existing task router | Missed requirement owners |
| 14. GUI Tasks | GUI reading lists | MOVE | INDEX sections 26-29, 86 | Use router; primary GUI ownership stays explicit | Wrong presentation/architecture owner |
| 15. Overall Architecture Tasks | Overall architecture reading list | MOVE | INDEX sections 12, 90 | Use existing router | Missing system boundaries |
| 16. Database Tasks | Database reading list | MOVE | INDEX sections 34-41, 85 | Delegate routing; retain direct schema safeguards | Wrong physical schema authority |
| 17. AutoHotkey Tasks | AHK v2 and mandatory AltF7Hub guidance | KEEP_COMPRESS | Root: scoped guidance and technology; INDEX section 20 | Preserve mandatory explicit scoped read; delegate general reading list | Protected state/native safeguards skipped |
| 18. PowerShell Tasks | PowerShell reading list and runtime | MOVE | INDEX sections 53-63; PS; D12 | Delegate list; keep PowerShell 7 and execution reminder | Wrong execution authority |
| 19. Python / PySide6 Tasks | Python/PySide6 reading list | MOVE | INDEX sections 30-34; D13 | Use router and architectural summary | Reverse dependencies |
| 20. Planning Tasks | Planning reading list | MOVE | INDEX sections 24, 91-93; PLAN | Use existing planning owner and router | Plan treated as implementation |
| 21. Inspect Before Creating | Search before creating | KEEP_COMPRESS | Root: workflow | Retain search/reuse sequence and evidence areas | Duplicate infrastructure |
| 22. Scope Control | Authorized scope and follow-ups | KEEP_COMPRESS | Root: workflow | Retain exclusions and follow-up rule | Unrelated changes |
| 23. Vertical Slice Rule | Bounded vertical slices | MERGE | Root: workflow; VSD | Merge with workflow; examples are unnecessary | Oversized delivery |
| 24. Implementation Process | Understand/inspect/plan/test/review/document | KEEP_COMPRESS | Root: workflow; VSD lifecycle reference | Keep lifecycle and task fields; delegate phase mechanics | Skipped evidence gates |
| 25. Coding-Agent Task Contract | Agent-task fields and sample | MOVE | PLAN Implementation Handoff; VSD slice-plan template | Existing handoff/template owns details; root retains fields | Ambiguous task authorization |
| 26. Python Architecture Rules | Python layer direction | MERGE | Root: architecture; D13 sections 4, 112-115 | Merge with architecture summary | Reverse dependencies |
| 27. GUI Rules | GUI responsibilities | MERGE | Root: architecture; D13 sections 14-15, 115 | Keep short prohibition on SQL/domain/credentials/commands | Business/execution rules in widgets |
| 28. Service Rules | Service use-case coordination | MOVE | D13 services package; D06 | Delegate detail; root retains service ownership | Presentation logic in services |
| 29. Domain Rules | Domain independence | KEEP_COMPRESS | Root: architecture; D13 sections 31-33, 113 | Keep framework/provider independence | Domain coupled to infrastructure |
| 30. Repository Rules | Persistence responsibility and structured returns | MOVE | D13 repositories package, sections 42, 114 | Delegate mechanics; root retains persistence/SQL boundary | Raw persistence leaking into GUI |
| 31. SQLite Rules | SQLite integrity and connection PRAGMAs | KEEP_COMPRESS | Root: SQLite; D07; D09 sections 18-19 | Keep keys/constraints/foreign keys/busy timeout | Silent relational corruption |
| 32. SQL Parameterization | Parameterized SQL | KEEP_COMPRESS | Root: SQLite; D07 section 36 | Keep prohibition and remove code examples | SQL injection |
| 33. Database Schema Authority | Physical schema authority | KEEP_COMPRESS | Root: SQLite; D09 | Keep exact owner and distinguish ERD | Schema invented from conceptual diagram |
| 34. No Arbitrary Table Targets | No arbitrary table counts | MERGE | Root: inspect-before-create; D14 | Keep requirement-driven creation through reuse rule | Speculative schema |
| 35. Database Change Procedure | Database change sequence | MOVE | D07 sections 47-50; INDEX sections 35-39 | Delegate procedure; root requires schema/relationship inspection | Unreviewed destructive change |
| 36. Migration Rules | Migration naming/tracking | MOVE | D07 sections 47-49; D15 migration naming | Delegate mechanics; root retains versioning/history authority | Competing migration state |
| 37. Migration Immutability | Released migration immutability | KEEP_COMPRESS | Root: SQLite; D07 section 47 | Keep revision exception and forward-only requirement | History altered silently |
| 38. Migration Safety | Destructive migration safeguards | KEEP_COMPRESS | Root: SQLite and escalation; D07 section 50 | Keep explicit approval and foreign-key safeguard | Data loss |
| 39. Database Transactions | Atomic units and external waits | KEEP_COMPRESS | Root: SQLite; D07 sections 34-35 | Keep atomicity and no long external waits | Partial writes/locks during external work |
| 40. Index Rules | Index justification and query plans | MOVE | D07 sections 38-41; D09 | Existing database owner covers procedure | Speculative indexing cost |
| 41. FTS5 Rules | FTS as derived infrastructure | MOVE | D07 sections 42-44; D09 | Delegate details; root keeps relational authority | Search index treated as source data |
| 42. Trigger Rules | Triggers versus business logic | KEEP_COMPRESS | Root: SQLite; D07 section 45 | Keep service ownership; route synchronization mechanics | Hidden business/execution workflows |
| 43. SQLite Integrity Testing | Executed SQLite integrity checks | MOVE | D07 section 74, sections 78-79 | Delegate test mechanics; root keeps required results/truth | Unsubstantiated integrity claim |
| 44. PowerShell Architecture Rules | PowerShell ownership and runtime | KEEP_COMPRESS | Root: technology and scoped guidance; PS | Keep PowerShell 7/ownership; route runtime procedures | Parallel runtime or persistence layer |
| 45. PowerShell Execution Boundary | Service/gateway execution boundary | KEEP_COMPRESS | Root: AI and automation; PS execution boundary; D12 | Keep chain/direct-launch guard; private-copy verification, containment, time/output bounds and cleanup remain scoped to PS/D12 | Uncontrolled process execution |
| 46. PowerShell Safety | Parameters, privilege, failure, preview | MOVE | PS Security, diagnostics and Microsoft administration; D12 | Delegate procedures; root retains least privilege/controlled mutation | Diagnostics silently become remediation |
| 47. PowerShell Structured Output | Machine-readable result example | MOVE | PS Machine results, streams and errors; D12 | Use approved result owner rather than generic JSON example | New incompatible result contract |
| 48. PowerShell Command Injection | Injection and shell argument safety | KEEP_COMPRESS | Root: AI and automation; PS Security | Keep untrusted dynamic execution ban; route argument procedures | Command injection |
| 49. AutoHotkey v2 Rules | AHK v2 desktop layer and syntax | KEEP_COMPRESS | Root: technology ownership; D11 | Keep desktop ownership and explicit v2-only syntax invariant; delegate procedures | AHK v1 syntax or parallel primary application |
| 50. AutoHotkey Database Boundary | AHK core-database boundary | KEEP_COMPRESS | Root: architecture; D07 AHK database boundary | Keep normal writes in Python repositories | Direct uncontrolled persistence |
| 51. Clipboard Safety | Clipboard preservation/privacy | KEEP_COMPRESS | Root: AI and automation; D11 clipboard architecture | Keep restoration reminder and explicit optional, privacy-aware persistent-history invariant | Loss or unwanted persistence of user content |
| 52. UI Automation Rule | API/CLI before UI automation | KEEP_COMPRESS | Root: AI and automation; D11 UI automation | Keep integration preference; route state-wait mechanics | Fragile desktop automation |
| 53. AI Rules | AI advisory role | KEEP_COMPRESS | Root: AI and automation; D14 section 26 | Keep technician/service authorization boundary | AI acquires execution authority |
| 54. AI Output Is Untrusted | Untrusted generated text/code/commands | MERGE | Root: security and AI | Merge input validation and AI review rules | Generated content treated as trusted |
| 55. AI-Generated Code Review | AI-code review matrix | MOVE | D14 section 108; INDEX section 89 | Existing review owners cover criteria; root requires validation | Unsafe generated code accepted |
| 56. Security Rules | Least privilege and secrets | KEEP_COMPRESS | Root: security; D14 | Retain explicit non-disclosure/non-commit rule | Credential disclosure |
| 57. Untrusted Inputs | Untrusted input classes | KEEP_COMPRESS | Root: security | Keep broad boundary validation rule | Unchecked external data |
| 58. Filesystem Safety | Traversal, filenames, overwrite and metadata | KEEP_COMPRESS | Root: security; D13 File Security; INDEX sections 79-80 | Retain path/user-file safeguards; delegate attachments strategy | Traversal or user-file loss |
| 59. Secrets and Configuration | Secrets versus configuration | MERGE | Root: security; FND Secrets Boundary | Merge with secrets reminder and approved broker boundary | Plaintext secret storage |
| 60. Testing Requirements | Appropriate success/failure checks | KEEP_COMPRESS | Root: validation; D13 section 127; D14 sections 85-87 | Keep required checks; delegate full category lists | Success-only validation |
| 61. Test Reporting | Truthful test statuses | KEEP_COMPRESS | Root: validation | Keep exact PASS/FAIL/NOT RUN/BLOCKED and execution requirement | Invented PASS |
| 62. Database Testing Requirements | Database test matrix | MOVE | D07 sections 78-80; D13 sections 130-131 | Delegate existing test procedures; root retains integrity truth | Untested migrations/rollback |
| 63. GUI Testing Requirements | GUI test matrix | MOVE | D13 section 132; INDEX section 86 | Delegate construction/signals/navigation/workflow coverage | Broken GUI lifecycle |
| 64. PowerShell Testing Requirements | PowerShell test matrix | MOVE | PS Validation, documentation and completion; D12 sections 98-101 | Delegate syntax/output/failure/cleanup coverage | Unsafe execution failure paths |
| 65. Failure Is Part of the Design | Failure assumptions | MERGE | Root: validation; D14 Design for Failure | Merge with failure/cancellation/recovery requirement | Success-only error design |
| 66. Error Handling | Meaningful exception handling | KEEP_COMPRESS | Root: validation; D13 Error Architecture | Keep no suppression rule; delegate translation mechanics | Failures hidden |
| 67. Logging | Centralized safe logging | KEEP_COMPRESS | Root: security; D13 sections 89-92 | Keep central logging and sensitive-content exclusions | Secondary uncontrolled data store |
| 68. Audit vs Logs | Audit versus technical logs | MOVE | D13 section 93; D07 section 54 | Delegate conceptual detail; root retains separation | Audit/log confusion |
| 69. Background Work | Responsive GUI and thread ownership | KEEP_COMPRESS | Root: architecture; D13 sections 56-58 | Keep event-loop and GUI-thread invariants | UI hangs or thread violations |
| 70. Cancellation | Truthful cancellation statuses | KEEP_COMPRESS | Root: validation; D13 section 59 | Keep completion truth; delegate status definitions | Committed operation reported cancelled |
| 71. Dependencies | Dependency evaluation procedure | MOVE | D14 sections 110-112; D13 sections 122-123 | Delegate costs/compatibility; root retains justification | Unnecessary unsafe dependencies |
| 72. Current Official Documentation | Current official external documentation | KEEP_COMPRESS | Root: evidence; INDEX section 126; D14 section 109 | Keep freshness verification rule | Stale API/framework assumptions |
| 73. Project Skills | Skills discovery and architecture precedence | KEEP_COMPRESS | Root: scoped guidance; ROOT section 19 | Keep discovery/fallback/precedence; remove expected inventory | Absent skill assumed authoritative |
| 74. Git Safety | Protect unrelated user work and control integration | KEEP_COMPRESS | Root: Git; VSD Git safety reference | Keep baseline/preservation; integration task-authorization rule is intentional safety hardening | User edits lost or unauthorized integration |
| 75. Branch Strategy | Focused branch conventions | MOVE | D15 sections 152-153 | Existing naming owner; root retains focused worktree safety | Inconsistent branches |
| 76. Destructive Git Operations | Explicit destructive Git approval | KEEP_COMPRESS | Root: Git; VSD Git safety reference | Retain authorization and impact review | History/data loss |
| 77. Documentation Synchronization | Affected canonical docs updated after change | KEEP_COMPRESS | Root: documentation; INDEX sections 106-107 | Keep living-doc rule; delegate mapping matrix | Obsolete current specification |
| 78. Documentation Impact Analysis | Documentation impact report | MERGE | Root: documentation; INDEX section 106 | Merge impact requirement; existing router owns matrix | Unrelated documentation churn |
| 79. Documentation Accuracy | Plan/implementation/verification truth | KEEP_COMPRESS | Root: evidence and documentation | Retain no legitimizing incorrect implementation | False implementation claims |
| 80. Architecture Escalation | Major architecture review gates | KEEP_COMPRESS | Root: Foundation and escalation | Retain all major-risk categories | Silent boundary redesign |
| 81. Architecture Change Procedure | Architecture change proposal fields | MOVE | PLAN Decision Register and User-Review Decisions; VSD | Delegate procedure; root retains impacts/alternatives/approval | Major decision without evidence |
| 82. Plugins | Validated plugin need and isolation | KEEP_COMPRESS | Root: architecture; INDEX section 103; D13 sections 148-149 | Keep approved use case and database-access limit | Unrestricted speculative plugins |
| 83. Integrations | Read-first integrations and system-of-record responsibility | KEEP_COMPRESS | Root: offline and integrations; D13 integration boundary | Keep read-first/no automatic bidirectional sync | External data overwritten |
| 84. Microsoft Integration Safety | Permissions/authentication/least privilege | KEEP_COMPRESS | Root: offline and integrations; PS Microsoft administration | Keep verification and no broad scopes for convenience | Excess tenant permissions |
| 85. Implementation Completeness | Behavior/security/data/test/documentation completeness | KEEP_COMPRESS | Root: completion; ROOT section 24 | Keep completion obligations | Premature completion claim |
| 86. Completion Checklist | Completion checklist | MERGE | Root: completion; VSD implementation-report template | Merge duplicate checklist into completion rule | Unverified completion |
| 87. Standard Implementation Report | Implementation report fields | MOVE | VSD implementation-report template | Use existing template; root retains result/impact/risks summary | Missing evidence and risks |
| 88. Planning Report | Planning report fields | MOVE | PLAN Planning Document Structure; VSD slice-plan template | Existing scoped owner/templates cover fields | Unclear plan/approval state |
| 89. Code Review Report | Code-review report fields | MOVE | VSD review-report template; INDEX section 89 | Existing review owners/templates; root retains concrete-defect priority | Review without severity/evidence |
| 90. First Implementation Phase | First bootstrap implementation objective | DELETE_OBSOLETE | Git baseline AGENTS.md sections 90-93; D18 historical owner | Remove fixed early task; durable lifecycle remains | No invariant lost; old task could misdirect agents |
| 91. First Codex Slice | First SQLite bootstrap slice prompt | DELETE_OBSOLETE | Git baseline AGENTS.md sections 90-93; D18 historical owner | Remove stale task; database safeguards remain above | No invariant lost; duplicate bootstrap work |
| 92. Subsequent Development Sequence | Old subsequent development order | DELETE_OBSOLETE | Git baseline AGENTS.md sections 90-93; D18 historical owner | Use router/Roadmap for current planning; preserve history in Git | No invariant lost; obsolete priorities |
| 93. What Not to Build First | What not to build first | DELETE_OBSOLETE | Git baseline AGENTS.md sections 90-93; D18 historical owner | Remove early-phase premise; keep enduring scope/AI/plugin/data safeguards | No invariant lost; stale missing-foundations claim |
| 94. Final Development Principle | Small tested secure reversible development | MERGE | Root: purpose, workflow and completion | Merge concluding repetition with universal rules | No invariant lost through deduplication |

## Disposition totals

- KEEP: 0.
- KEEP_COMPRESS: 50.
- MOVE: 29.
- MERGE: 12.
- DELETE_OBSOLETE: 4.
- REQUIRES_DECISION: 0.
- Total numbered sections: 95 (0 through 94), each classified exactly once.

## Invariant preservation and review scope

Always-visible root rules cover user-work preservation, secrets, employer/customer minimization,
least privilege, untrusted inputs, technician-controlled AI/automation, offline classifications,
scope, inspect-before-create, data integrity, test truth, authority, progressive loading,
scoped precedence and architecture escalation.
Additional short reminders retain parameterization, migration immutability, foreign-key enforcement,
transaction boundaries, truthful cancellation, AHK v2-only syntax, optional/privacy-aware persistent
clipboard history, clipboard restoration, GUI-thread ownership,
read-first integrations, plugin restrictions and controlled PowerShell execution.
Foundation routes 0A-0E through the scoped owner; 0E is conditional on existence/review.
No Foundation phase was executed, created, approved or redesigned.
No current implementation inventory or early implementation order remains in the candidate root.
No blocking conflict or guidance without an owner was identified.
This is implementation self-review and documentation validation; independent rereview remains pending.

## Independent-review corrections and intentional hardening

The independent review requested four narrow root corrections, now applied:

- Remove the added `AGENTS.override.md` precedence sentence; it was absent from the original root.
- Remove the private-copy verification, containment, time/output bounds and cleanup sentence from root;
  those implementation details remain with existing PowerShell authorities, reached by unchanged links.
- Restore: "AutoHotkey work uses v2 syntax; do not introduce AHK v1 syntax."
- Restore: "Persistent clipboard history must remain optional and privacy-aware."

The Git integration-authorization rule is an intentional safety-hardening addition, not a verbatim
preservation of an old root rule: commit, push, PR creation and merge require task authorization;
review approval alone does not authorize integration. The root sentence remains unchanged in this correction.
No other root rule was changed.

Correction baseline: root raw SHA-256 `e5531fd5f1a6e2e204168f1fa2cf4cd63eec64ae84442da93d60a834f68c0eed`;
audit raw SHA-256 `133e479c2d05efad83183ffd4109e7ca4f31cd58455b854ee27c62e2ff0a2f91`.
Section 49 changes from MERGE to KEEP_COMPRESS; sections 45, 51 and 74 retain their dispositions
with corrected ownership/preservation/hardening explanations. All other section classifications remain unchanged.

## Validation record

Fresh static validation used PowerShell inspection and an in-memory Python check; no test/helper file was created.

- New root: 219 lines, 17,558 raw bytes, UTF-8 without BOM, CRLF retained.
- Reduction: 2,405 lines (91.65%) and 25,240 bytes (58.97%).
- Candidate raw SHA-256: `5111890c751123fdd41ca3b2b7ddfe18865718b0f0026c6ee90a966fc68c6d26`.
- Candidate Git-normalized blob: `04667d3e0fbb2c8cd9496eafdc0d4960d3105627`.
- Complete tracked diff: one whole-file hunk, `@@ -1,2624 +1,219 @@`.
  Old/new contents were reconstructed from every diff line and matched against base/candidate.
  The old section content and complete candidate were inspected for semantics and safety.
- Traceability: all 95 old numbered sections appear exactly once; totals reconcile.
- Critical-rule check: 21 explicit invariant/authority/context checks PASS, plus all five Foundation routes.
- Destination check: 22 existing owner/resource paths PASS; delegated topic content inspected progressively.
- Markdown: headings, tables, balanced fences, all relative links, final newline and whitespace PASS.
- `git diff --check`: PASS. The untracked audit artifact was additionally checked for Markdown/whitespace.
- Authorized scope: only root tracked modification plus this single untracked review artifact; index empty.
- Canonical preservation (retained initial evidence): PASS for branch, HEAD, status, index, root hash and all 75 protected path identities.
  This includes two absent deleted paths and expanded untracked file inventories.
- Documentation validation: PASS.
- Application tests: NOT RUN — documentation-only; no runtime behavior was changed.
- Architecture impact: instruction routing with intentional Git-authorization safety hardening; ownership, Foundation semantics and layer contracts preserved.
- Security impact: safeguards remain explicit and detailed authorities remain reachable.
- Conflicts / requires decision: none identified.
- Risk: detailed guidance now depends on routed owners staying discoverable; all candidate links resolve.
- Next gate: independent rereview of the corrected unstaged candidate and this traceability record.
- No commit, push, PR or merge was performed; both files remain unstaged.
- Result: READY_FOR_REVIEW.
