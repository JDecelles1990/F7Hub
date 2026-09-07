# F7Hub Current State

Last verified: 2026-09-07

Branch: `feat/ticket-knowledge-linking`

Base HEAD: `13fc1bcae44f4e36c6e6dd2fcf382874ec121508` (integrated Slice 011, PR #6). Starting main/HEAD matched, with nothing staged and only the separate deletion of Docs/Archive/DocsOLD/00_Vision.md. Slice 012 is implemented and ready for independent review. Nothing is staged or committed; no push or merge. ROOT.md, physical schema docs and historical migrations are unchanged. The user-confirmed archive deletion remains untouched.

## Working

- SQLite bootstrap, five migrations through `0005_knowledge.sql`, integrity and FK checks
- Company/contact repositories and quick active-company/contact creation from New Ticket
- Company/contact/category-aware ticket creation, transactional reference validation and safe refresh/recovery with draft preservation
- Saved-ticket reopening, current reference names, notes, status history/timeline, resolution, closure and reopening
- Knowledge Base navigation and asynchronous article create/list/read
- DRAFT/version 1 creation with atomic initial snapshot; required code/title/body and optional summary
- Plain-text metadata and read-only Markdown source, with valid body whitespace preserved
- DRAFT editing with immutable code, current Version N, expected-version conflict protection and atomic sequential snapshots
- Safe stale/non-DRAFT/missing errors, retained editor input and no-change saves without revision/timestamp updates
- RELATED ticket/article linking through TicketKnowledgeService/Repository using the existing junction
- Saved-ticket Knowledge tab with current code/title/status/version, Link Article, Open Article and Refresh
- Lightweight candidates for all existing statuses, excluding already RELATED articles; safe duplicate/missing-entity feedback
- Atomic existence/duplicate checks, insert and joined reload; rollback and concurrent duplicate protection
- Async list/candidate/link calls, duplicate-submit/active-write close protection and retained selection on failure
- Explicit committed-link feedback after failed list refresh and safe Refresh recovery
- MainWindow-mediated article-ID navigation into Knowledge Base, including vanished-target feedback
- Current linked metadata after article edits/status changes, FK cascades and persistence after reconstruction
- AutoHotkey v2 F7 launch/focus/restore (previously verified; not rerun in Slice 012)

## Partial

- Company creation is name-only; full company/contact/category management remains unimplemented
- Category hierarchy formatting is deferred; selectors display names directly
- AutoHotkey login startup is not configured
- Only DRAFT articles are editable; article deletion/publishing/archiving workflows are not implemented
- Historical snapshots persist; no history viewer or restore/revert UI
- RELATED only: no unlink, APPLIED/RESOLUTION_SOURCE workflow, type changes, link notes or bulk linking
- No selector search/filter, FTS, tags/categories, recommendations, AI or article creation/editing from tickets
- KnowledgeWorkspace's existing list still loads bodies; new relationship lists do not. No pagination or large-library performance validation. Real user-library volume is NOT VERIFIED; only synthetic data was used.

## Not Started

- PowerShell integration

## Current Milestone

TICKETS ↔ KNOWLEDGE BASE CONNECTED

## Validation

Database: PASS — 226 tests, fresh full discovery, exit code 0

GUI: PASS — 64 tests, fresh full discovery after final sizing fix, exit code 0

Integration: PASS — 57 tests, fresh full discovery after final sizing fix, exit code 0

Total: PASS — 347 (226 + 64 + 57), up 43 from pre-slice 304 (202 + 52 + 50). No suite count decreased.

Focused Slice 012: repository/service 24 PASS; combined Ticket/Knowledge GUI 24 PASS (12 new plus 12 existing Knowledge tests); cross-module Integration 7 PASS. Full suites include these tests.

Native Windows Slice 012: PASS — windows Qt platform, 1000×700, isolated synthetic SQLite. QTest mouse/keyboard checks created a ticket and KB0001, opened the empty Knowledge tab, selected/linked KB0001, opened its current details, edited it to Version 2, created KB0002, returned to the ticket, added a note and ran Resolve → Close → Reopen. Reconstructing the application against the same database preserved the link and opened Version 2. Empty, selector, linked, read and revised/activity screenshots were visually inspected. Initial code clipping was corrected and the native flow rerun; final identity columns were readable with no clipping/overlap in tested layouts. Agent verification, not user acceptance testing. Harnesses/screenshots/databases stayed outside the repository.

Existing New Ticket, Quick Company, Quick Contact, company/contact/category references, Saved Tickets, notes/status lifecycle and Knowledge create/read/edit/version snapshots are covered by the full regression suites. Native checks additionally exercised ticket creation, notes/status and Knowledge create/edit alongside linking.

AutoHotkey: NOT RUN in this slice; launcher unchanged.

Database validation: integrity_check = ok; foreign_key_check = zero violations; migration count = 5. New migration: NO. Schema changes: NONE. Tests cover both deletion cascades, deletion after candidate/list reads, concurrent duplicate linking, insert/reload rollback/retry, current joined title/status/version and immutable lightweight records. Native SQLite contains the verified ticket_id/article_id/RELATED/UTC linked_at row.

## Architecture / Activity Decision

TicketWorkspace / TicketKnowledgeWidget / LinkArticleDialog → TicketKnowledgeService → TicketKnowledgeRepository → SQLite. MainWindow mediates the article-ID signal and public KnowledgeWorkspace.open_article_by_id operation. Workspaces do not access each other's internals; no GUI SQL or repository calls.

ACTIVITY WRITE: NONE. Linking writes only ticket_knowledge_articles; current requirements do not mandate ticket updated_at or timeline events for this use case. Tests verify existing ticket details/activity remain unchanged by linking.

## Recommended Next Slice

Unlink one RELATED article from a saved ticket, retaining both entities. This corrects accidental links through the existing narrow boundary without requiring more content, new schema or richer types. See 16_Roadmap.md for the six-option comparison. Recommendation only; independent Slice 012 review is the next gate. Do not begin Slice 013.
