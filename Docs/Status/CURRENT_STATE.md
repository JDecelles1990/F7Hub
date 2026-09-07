# F7Hub Current State

Last verified: 2026-09-07

Branch: `feat/ticket-knowledge-unlink`

Base HEAD: `68aefb157c7351aa47e5f11ffd4c94cdbb8cf0ae` (Slice 012 integrated through PR #7).

Status: Slice 013 implemented, uncommitted, ready for independent review. Starting main/HEAD matched with only the separate user-confirmed deletion of Docs/Archive/DocsOLD/00_Vision.md. Nothing staged; no commit, push or merge. ROOT.md, physical schema docs and five historical migrations are unchanged.

## Current Milestone

TICKET ↔ KNOWLEDGE RELATED LINKS MANAGEABLE

## Working

- SQLite bootstrap, five migrations through 0005_knowledge.sql, integrity and FK checks
- New Ticket with company/contact/category references and transactional validation
- Quick Company / Quick Contact creation with safe reference refresh/recovery and draft preservation
- Saved Tickets, current reference names, notes, history/timeline, Resolve → Close → Reopen
- Knowledge create/list/read and DRAFT editing with immutable code, current version and atomic historical snapshots
- Stale-edit protection, safe errors, preserved input and no-change saves without extra revisions
- Plain-text article metadata and read-only Markdown source
- RELATED Link Article, lightweight current code/title/status/version, Open Article and Refresh
- RELATED Unlink Article for one selected association, with explicit confirmation and Cancel as default/escape
- Exact relationship-only deletion preserving both entities, other RELATED and APPLIED/RESOLUTION_SOURCE rows
- Safe ticket-missing, article-missing and not-linked feedback; concurrent unlink yields one success and one not-linked result
- Async linking/unlinking, duplicate/conflicting-action protection, confirmation/context guards and safe obsolete callbacks
- Failed unlink preserves selection; committed unlink plus failed refresh retains success and recovers through Refresh without another DELETE
- Unlinked articles reappear in Link Article candidates; normal relink persists one association with a fresh linked_at timestamp
- MainWindow-mediated exact article navigation and persisted link/unlink state after application reconstruction
- AutoHotkey F7 launch/focus: VERIFIED; manual Windows verification: PASS — 2026-09-07. Detailed launcher architecture: `Docs/11_AHKArchitecture.md`.

## Deferred / Limitations

- Bulk linking/unlinking, APPLIED/RESOLUTION_SOURCE workflows, relationship-type editing, relationship history/undo and generic relationship management
- History viewer/restore, search/FTS, tags/categories, recommendations and AI
- Article publishing/archiving/deletion and ticket-driven article creation/editing
- Full company/contact/category management and category hierarchy formatting
- KnowledgeWorkspace's existing list still loads bodies; relationship lists remain lightweight. No pagination or large-library validation. Real content volume is NOT VERIFIED; validation is synthetic only.
- PowerShell integration; AutoHotkey login startup

## Validation

| Suite | Result |
|---|---|
| Database | 244 PASS |
| GUI | 74 PASS |
| Integration | 66 PASS |
| Total | 384 PASS |

Pre-slice: 347 (226 / 64 / 57). Increase: 37 tests (18 Database, 10 GUI, 9 Integration); no suite decreased.

Focused: repository/service 42 PASS; combined Ticket/Knowledge GUI 34 PASS; cross-module Integration 16 PASS.

All full suites ran after final implementation/test changes and exited 0. Only documentation changed afterward; focused/full evidence is retained during completion, with no additional application test run required.

Native Windows: PASS — windows Qt platform, 1000×700, isolated synthetic SQLite. Mouse/keyboard checks created a ticket and KB0001/KB0002, linked both, cancelled then confirmed unlink of KB0001, preserved the ticket/articles/KB0002 link, opened exact KB0002, found KB0001 in candidates and relinked it. Notes and Resolve → Close → Reopen also passed. Captured windows were visually inspected: the new control and confirmation were readable with no clipping/overlap in tested layouts. Agent verification, not user acceptance testing. Evidence retained during documentation completion; no additional native run. Harness/screenshots/databases/logs stayed outside the repository.

Existing New Ticket, Quick Company, Quick Contact, references, Saved Tickets, notes/status, Knowledge create/read/edit/version snapshots and Link/Open are covered by the passing full suites. Integration also verifies persisted unlink after reconstruction and opening the remaining article's current version.

AutoHotkey Slice 013 execution: NOT RUN — launcher unchanged. F7 launch/focus remains VERIFIED; the recent isolated automated recheck was BLOCKED — shell wait timeout.

## Database / Activity

Migration count: 5. New migration: NO. Schema changes: NONE. Historical migrations unchanged. Isolated integrity_check = ok; foreign_key_check = zero violations.

Unlink uses one BEGIN IMMEDIATE transaction with ticket, article and exact RELATED checks before DELETE and a one-row requirement before commit. Tests cover rowcount failures, rollback after DELETE/at commit, parent and other-type preservation, concurrent unlink, candidate/relink and reconstruction.

ACTIVITY WRITE: NONE — link/unlink changes only ticket_knowledge_articles. Ticket updated_at, notes, status history and timeline remain unchanged. Existing widget → service → repository → SQLite ownership and shared ServiceTaskRunner are preserved.

## Next Gate / Candidate

Independent Slice 013 review is the next gate. Do not stage, commit, push or merge during this completion task.

Recommended next slice: a read-only Knowledge version-history viewer using existing snapshots. See 16_Roadmap.md for the six-option comparison. No Slice 014 implementation.
