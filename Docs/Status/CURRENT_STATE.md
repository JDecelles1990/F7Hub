# F7Hub Current State

Last verified: 2026-09-06

Branch: `feat/knowledge-article-editing`

Base HEAD: `04466c3c549bc809a7314c136e1d512ba403ae98` (integrated Slice 010, PR #5). Slice 011 is uncommitted and ready for independent review. Existing implementation was preserved during continuation; only documentation was changed after the resumed-state review. Nothing is staged. ROOT.md is unchanged; the separate user-confirmed deletion of Docs/Archive/DocsOLD/00_Vision.md remains untouched.

## Working

- SQLite bootstrap, migrations through `0005_knowledge.sql`, and integrity checks
- Company and contact repositories
- Ticket creation and Saved Tickets reopening
- Ticket notes, status history, timeline, resolution, closure and reopening
- Company-aware and contact-aware ticket creation with active, company-filtered choices
- Optional active TICKET category selection, category-only refresh/retry and category ID persistence
- Reference refresh/retry, draft preservation and transactional reference validation
- Quick active-company creation from New Ticket, automatic selection and contact reset
- Quick company-scoped active-contact creation with required name and optional email, automatic selection and complete draft preservation
- Name validation, background creation, duplicate-submit protection and post-commit company/contact refresh recovery
- Explicit pending-contact abandonment after company deactivation/deletion, preserving the committed contact and draft, restoring reference selection/save, and ignoring obsolete callbacks without duplicate insertion
- Atomic company validation/contact creation and repository insert/reload rollback
- Saved-ticket company/contact names, including inactive references and safe null/deletion handling
- Saved-ticket current category names, including inactive categories and safe null/deletion handling
- Knowledge Base navigation in the existing application shell
- Asynchronous article create/list/reopen/read with required code/title/body and optional summary
- DRAFT/version 1 creation with an atomic initial version snapshot, safe errors and duplicate-submit protection
- Deterministic SQLite-backed article listing and persisted details after application reconstruction
- Read-only Markdown source with valid body whitespace preserved; metadata displayed literally as plain text
- DRAFT article title/summary/body editing with immutable article code and read-only current Version N
- Fixed expected-version token, authoritative stale-edit protection and conditional ID/version/DRAFT update
- Atomic current-row update plus new immutable revision snapshot; sequential 1/2/3 history, complete snapshot/reload rollback and safe retry
- Specific safe stale/non-DRAFT/missing errors, retained editor input, no raw database details and explicit reopening after conflict
- No-change saves detected after authoritative status/version checks; no revision or timestamp change
- Async Save Revision, duplicate-save/close protection and same-article list/detail reconciliation
- AutoHotkey v2 F7 launch/focus/restore (previously verified; not rerun in Slice 011)

## Partial

- Company creation is name-only; company code and full company management are not exposed
- Contact creation is limited to selected companies; contact editing/deletion and contact/category management GUI are not implemented
- Category hierarchy formatting is deferred; the selector displays category names directly
- AutoHotkey login startup is not configured
- Only DRAFT articles can be edited; deletion, publishing and archiving workflows are not implemented
- Historical snapshots persist in SQLite; no history browser, historical viewer or restore/revert UI
- Knowledge search/FTS, categories/tags, relationships, links, ticket linking and AI remain unimplemented
- Knowledge listing currently loads all article records, including bodies; no pagination or large-library performance validation

## Not Started

- PowerShell integration

## Current Milestone

KNOWLEDGE BASE CREATE → READ → EDIT WITH VERSION HISTORY

## Validation

Database: PASS — 202 tests, fresh final discovery, exit code 0

GUI: PASS — 52 tests, fresh final discovery, exit code 0

Integration: PASS — 50 tests, fresh final discovery, exit code 0

Total: PASS — 304 tests (202 + 52 + 50), up 24 from the pre-slice 280 (189 + 45 + 46). No suite count decreased.

Slice 011 focused tests: repository/service 24 PASS, GUI 12 PASS, Integration 6 PASS. Evidence retained on continuation because implementation/tests remained unchanged; the fresh full suites also include these tests.

Native Windows Slice 011: PASS — native windows Qt platform, 1000×700, isolated synthetic SQLite. Input-event checks created KB0001 version 1, opened Edit Article, verified read-only code/version and prefilled title/summary/body, saved revised title/body and displayed Version 2 with the same selection. Switching through New ticket/Saved tickets/Knowledge Base preserved the revised content. Creating KB0002 verified New Article still works. Editor and saved Version 2 views were visually inspected; no clipping/overlap observed for the supplied examples. Agent checks, not user acceptance testing. Evidence retained on continuation; no additional native run because GUI implementation stayed unchanged. Harness/captures were outside the repository.

Existing New Ticket, Quick Company, Quick Contact, company/contact/category references, Saved Tickets, notes and Resolve → Close → Reopen are covered by the freshly passing full GUI/Integration suites.

AutoHotkey: NOT RUN in this slice

Migration: NONE — five unchanged migrations; isolated integrity_check = ok and foreign_key_check = zero violations.

Database/native evidence: KB0001 snapshots 1/2 plus KB0002 version 1; integrity_check = ok, foreign_key_check = zero violations and five migrations. Repository tests additionally verify complete historical rows remain unchanged through versions 1/2/3, snapshot/reload failure rollback, unchanged timestamps on no-change saves, and retry producing exactly the next version. Real SQLite integration proves two editors conflict correctly after workspace refresh, no extra snapshot, status/deletion protection, input retention and latest content/history surviving application reconstruction.

## Recommended Next Slice

Ticket ↔ Knowledge linking: attach an existing article to a saved ticket with a RELATED link and reopen it through the current read view. This reuses the existing junction schema and gives immediate cross-workflow context without depending on a large library. Current real article volume is NOT VERIFIED; validation used synthetic data only. See 16_Roadmap.md for the comparison of search/FTS, history viewer/restore, categories/tags, ticket linking, company/contact management and dashboard/navigation. Recommendation only; no Slice 012 work. Independent Slice 011 review remains the next gate.
