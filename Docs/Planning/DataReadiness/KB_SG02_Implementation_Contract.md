# KB-SG02 — Isolated Synthetic Proposal and Temporary KB Preview Lab

Date: 2026-11-01, America/Toronto. Candidate state: **READY_FOR_REVIEW**.
Independent review, technical-claim approval and Git integration: **PENDING**.

## Authorization and reconciliation

The user's explicit "PLEASE IMPLEMENT THIS PLAN" request authorizes the exact
standalone lab and twelve-path allowlist below. It supplies the bounded replacement
basis selected during planning: isolated lab, authored semantic proposals, unresolved
canonical identities, temporary editor and no operational data access. It supersedes
the prior planning stop for implementation of this scope only.

The completed KB-SG01 record was not located. Its contents and independent approval
remain **NOT VERIFIED**. This contract does not claim to recover that record, adopt
all of SemanticModel 2E/2F, approve vocabulary/mappings or certify the authored
fixture expectations independently. Those expectations are explicitly marked
`AUTHOR_PROPOSED_INDEPENDENT_REVIEW_PENDING` for the next review gate.

Clipboard recovery remains **USER CONFIRMED**, identifier
`F7HUB_CLIPBOARD_CENTER_RECOVERED_NO_CODE_CHANGE`. No Clipboard investigation,
modification or validation campaign forms part of this slice.

## Baseline and ownership

Candidate: `C:/Dev/F7Hub-KB-SG02`, branch `feature/kb-sg02-synthetic-preview`,
base/HEAD `b5ef6e6b49899cb249617e39de553c720e6c0556`. Live `origin/main`
was verified with `git ls-remote` before worktree creation. The initial sandbox
network attempt failed; reviewed escalation succeeded. No fetch, commit, push or
PR was performed. The canonical dirty checkout remains on
`fix/canonical-install-20261026` at `e72c390a57ac73fb64b5afd3c8dd852516494366`.

The GUI renders and edits temporary state; the preview service validates admitted
snapshots and composes text. The lab launcher alone owns disposable database setup.
Ticket/Knowledge services and repositories retain their existing responsibilities.
[SemanticModel 2D](../SemanticModel/2D_Case_Note_Semantic_Extraction_Pipeline.md),
[2B](../SemanticModel/2B_Troubleshooting_Concept_Relationship_Model.md) and
[2C](../SemanticModel/2C_Troubleshooting_Lexical_Model.md) retain semantic authority.
This is a local research profile, not a shared schema, engine or acceptance system.

## Fixed source profile and fixtures

Profile: `KB-SG02-LAB-v1`, package revision `1`. Only the fixed repository-relative
fixture and manifest paths are loaded. The launcher exposes no input/root/database
override, directory scanning or network source. Admission precedes storage setup.

| Case | Lineage and admitted fields | Authored expectations |
|---|---|---|
| F01 | SYN-IT-0004, `customer_report.en` | Reported symptom, unverified and unresolved |
| F02 | SYN-IT-0009, `customer_report.fr` | Preserve French accents/wording; no translation mapping |
| F03 | SYN-IT-0010, EN/FR reports and `root_cause.hypothesis` | Distinguish reports and fictional hypothesis; bilingual copies are not independent corroboration |
| F04 | Newly authored Teams variant, `variant.note` | Negated current failure, conditional planned check; no attempt/result |
| F05 | Newly authored monitor variant, `variant.note` | Reported contradiction and unverified input; no inherited cause/resolution |
| F06 | Newly authored unrelated note, `variant.note` | No authored proposals; no extractor success/abstention claim |

The original 24-case corpus is unchanged. All its outcomes are fictional resolved /
simulated PASS; this is not real-world technical validation or broad negative-case
coverage. F04–F06 do not inherit those outcomes.

Pinned SHA-256 inputs:

- Corpus: `612e115caeabb000ab5e19e6782168d43f0bc1149b9ae725c93a143cf2790eeb`.
- Original schema: `b024f4182c66a0d9280279ebfe4d1572fff228e01db8b04a26155da4575ac871`.

The manifest binds exact fixture bytes and the two original inputs. Admission rejects
hash changes, duplicate keys/IDs, unknown fields, invalid types/flags, unsupported
roles/methods, canonical targets, broken references and altered original excerpts.
It enforces six cases, 128 KiB package, 16 KiB per serialized case/admitted source
and at most eight proposals per case. The original schema is pinned evidence;
this slice does not claim a full JSON Schema validator.

The fixture file uses CRLF physical line endings, matching the existing Windows
`core.autocrlf=true` checkout policy and both pinned original inputs. Its byte hash
survives a normal checkout under that policy; no Git configuration or attributes
were changed. Other newline policies require a separately reviewed byte-identity
disposition rather than silent normalization of source evidence.

Only local display, temporary staging and manual review are admitted. Indexing,
Analytics, training, export, outbound disclosure, durable preview retention and
promotion are excluded. Synthetic source ownership is explicitly fictional; no
operational Ticket identity is created or inferred. No vendor URL is fetched and
technical correctness remains **NOT VERIFIED**.

## Service and preview contract

The launcher creates an owned OS temporary directory and initializes the existing
migration chain only inside it. Existing TicketService creates six **NEW** lab
tickets and INTERNAL notes; KnowledgeService creates one clearly marked synthetic
**DRAFT** reference. NEW preserves the service's initial status; no resolution or
OPEN transition is fabricated. No new migration or table is introduced.

Six actual `get_ticket_details` reads and six actual `get_article` reads supply
minimized immutable snapshots before the dialog opens. Setup writes are deliberate
lab staging, distinct from preview generation. TicketKnowledge's RELATED link
mutations are unused; no semantic relationship follows from a link.

`KBPreviewService.bind_sources` verifies the fixture-to-lab records and binds owner
references/revisions to package hash/revision, projection, synthetic provenance and
session. `build_preview` accepts only the exact currently admitted snapshot from
that session and returns immutable title/summary/body/provenance. Copies with
changed revisions, foreign snapshots and invalidated sessions cannot generate.
The session uses frozen startup snapshots, with no live database/file watching or
operational-source freshness claim. A new source requires a new admitted session.

Authored proposals retain existing role keys, bounded field references,
qualifications, `manual_fixture_authoring` and a null canonical target. They confer
no accepted cause, Entity, Tag, mapping, execution, Ticket transition or publication
authority. `accepted_cause_of` remains owner controlled. There is no extraction
algorithm, confidence score, precision/recall or evaluation-success metric.

The dialog receives only the preview service and immutable snapshots. It has no
database, repository, main-application context or publication capability. The
persistent synthetic notice and read-only provenance sit outside editable text.
Title (200 Unicode scalars), summary (1,000 scalars), body (64 KiB UTF-8) and review
annotations (16 KiB UTF-8) reject excessive edits visibly and preserve prior text.
Source/draft content uses plain-text widgets. No character-span highlighting,
external resources or command execution is implemented. The implementation uses
Qt's documented [QPlainTextEdit](https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QPlainTextEdit.html)
plain-text API and text-change signals.

Dirty fixture switches and all normal close/accept/reject routes require
Discard/Cancel, defaulting to Cancel. A failed replacement preserves the prior
edited draft before any discard question. Reentrant transitions cannot bypass the
guard. Accepted close erases editor state and invalidates the session. A new lab
session never restores prior preview edits. There are no Save, Publish, Export,
Accept Cause or Approve Mapping actions.

## Exact change inventory

| Action | Path |
|---|---|
| Add | `Python/f7hub/services/kb_preview_service.py` |
| Add | `Python/f7hub/gui/kb_preview_dialog.py` |
| Add | `Tools/Knowledge/kb_sg02_lab.py` |
| Add | `Tests/Fixtures/kb_sg02/review_cases.json` |
| Add | `Tests/Fixtures/kb_sg02/manifest.json` |
| Add | `Tests/Unit/test_kb_preview.py` |
| Add | `Tests/GUI/test_kb_preview_dialog.py` |
| Add | `Tests/Integration/test_kb_sg02_lab.py` |
| Add | `Docs/Planning/DataReadiness/KB_SG02_Implementation_Contract.md` |
| Modify | `Docs/05_GUI.md` |
| Modify | `Docs/Status/CURRENT_STATE.md` |
| Modify | `Docs/18_ChangeLog.md` |

The GUI registry and [current-state entry](../../Status/CURRENT_STATE.md#kb-sg02-current-state)
identify the lab separately from integrated application controls. Database schema,
production Python/GUI composition, AHK, PowerShell, Clipboard, configuration,
dependencies and existing datasets are unchanged. The canonical documentation
index requires no new subsystem/owner routing for this bounded candidate.

## Acceptance and fresh validation

Evidence root: `%LOCALAPPDATA%/F7Hub/CodexCheckpoints/KB-SG02/implementation-20261101/`.
Use its final candidate manifest, implementation report, test-impact record, suite
logs and `native-validation.result.json`; author statements do not replace review.

| Checks | Environment / result | Evidence |
|---|---|---|
| New admission/authority/preview unit checks | Windows host / Windows byte-identity profile: PASS 14/14 | `unit-final.log` |
| New GUI checks | Windows Qt offscreen: PASS 9/9 | `gui-final.log` |
| New real-service isolation/integration checks | Windows Qt offscreen / disposable SQLite: PASS 8/8 | `integration-final.log` |
| Existing Ticket/Knowledge service regression | Windows host / disposable SQLite: PASS 23/23 | `existing-service-regression.log` |
| Native Qt smoke | WINDOWS_NATIVE, injected Qt input: PASS 20 assertions, exit 0 | `native-validation.result.json`, three inspected captures |

The integration gate guards every setup database connection to the exact owned
target. After setup it forbids any database connection and all Ticket/Knowledge/
link mutations while generating, editing, switching and closing previews. Before/
after logical database dumps match, `integrity_check` returns `ok` and
`foreign_key_check` returns zero violations. These checks concern disposable
fixtures only; production SQLite was not opened, hashed, copied or validated.

Native evidence covers a visible 1080x780 client at the recorded DPI, observable
exposure, French text, unresolved proposal provenance, title editing/Tab focus,
real Discard/Cancel questions, guarded close, normal exit and removed owned storage.
All three captures were inspected for readable source/proposal/editor separation,
persistent notice and visible controls. Physical input, alternate DPI, Narrator and
high-contrast acceptance: **NOT RUN**.

Exact PowerShell test commands use the existing canonical virtual environment,
`PYTHONPATH=<candidate>/Python`, `QT_QPA_PLATFORM=offscreen`, and:

```powershell
& C:\Dev\F7Hub\.venv\Scripts\python.exe -B -m unittest discover -s Tests/Unit -p test_kb_preview.py -v
& C:\Dev\F7Hub\.venv\Scripts\python.exe -B -m unittest discover -s Tests/GUI -p test_kb_preview_dialog.py -v
& C:\Dev\F7Hub\.venv\Scripts\python.exe -B -m unittest discover -s Tests/Integration -p test_kb_sg02_lab.py -v
# Also add <candidate>/Tests/Database to PYTHONPATH for this command:
& C:\Dev\F7Hub\.venv\Scripts\python.exe -B -m unittest test_ticket_service test_knowledge_service -v
```

Initial integration failures remain in separate logs: incorrect NEW/OPEN assumption;
test-owned connections not closed and wrong test link-table name. The source/test
corrections precede the passing final checks. Exactly three failed-test temporary
directories were separately identified, absolute-parent/name checked and removed.
No repeated unchanged native failure or broad cleanup was performed.

## Launch, rollback and next gate

```powershell
& C:\Dev\F7Hub\.venv\Scripts\python.exe -B C:\Dev\F7Hub-KB-SG02\Tools\Knowledge\kb_sg02_lab.py
```

The tool has only the standard `--help` option. Normal shutdown invalidates the
session and removes only its exact owned temporary directory after parent/path
checks. Cleanup failure reports failure without broad deletion or unbounded retry;
an interruption can leave synthetic staging files in an OS temporary directory.
No secure-erasure guarantee is made. Verify the exact directory's ownership before
any later cleanup. Lab setup failure and post-UI cleanup failure remain distinct
from publication: no production action is attempted in either case.

Rollback is retirement of the standalone launcher and a separately authorized
reversion of only the candidate allowlist. No production migration, restore or
database repair is necessary. Canonical unrelated work and protected opaque paths
remain untouched.

Next gate: **independent candidate and fixture-expectation review**. Review the
replacement KB-SG01 basis, bounded source/privacy permissions, role qualifications,
Ticket/Knowledge staging and applicable 2E/2F limits as separate owner concerns.
The current implementation instruction does not constitute independent approval.
Technical claims, automatic matching/extraction, production ingestion, publication
and Git integration require separate authorization.

Carry-forward notes: **NONBLOCKING for author review readiness, BLOCKING for later
approval/integration** — original KB-SG01 record unavailable; authored fixture
expectations not independently approved; owner reconciliation belongs to the next
review. No upstream semantic approval or technical correctness is inferred.
