# F7Hub Current State

Last verified: 2026-09-06

Branch: `feat/knowledge-base-first-slice`

Base HEAD: `8c2ef7f0aeecfa6b0d65c9e731de8eef3f399efc`; Slice 010 is uncommitted and ready for independent review. Existing partial implementation was preserved on resume. Nothing is staged. ROOT.md is unchanged; the separate user-confirmed deletion of Docs/Archive/DocsOLD/00_Vision.md remains untouched.

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
- AutoHotkey v2 F7 launch/focus/restore (previously verified; not rerun in Slice 010)

## Partial

- Company creation is name-only; company code and full company management are not exposed
- Contact creation is limited to selected companies; contact editing/deletion and contact/category management GUI are not implemented
- Category hierarchy formatting is deferred; the selector displays category names directly
- AutoHotkey login startup is not configured
- Knowledge articles cannot yet be edited, deleted, published or archived through the application
- Knowledge search/FTS, categories/tags, relationships, links, ticket linking and AI remain unimplemented
- Knowledge listing currently loads all article records, including bodies; no pagination or large-library performance validation

## Not Started

- PowerShell integration

## Current Milestone

FIRST USABLE KNOWLEDGE BASE — CREATE → LIST → REOPEN / READ

## Validation

Database: PASS — 189 tests (supplied prior-session evidence retained; persistence implementation unchanged during continuation)

GUI: PASS — 45 tests (fresh continuation run after the metadata plain-text fix)

Integration: PASS — 46 tests (fresh complete run and post-fix rerun; baseline was 44)

Total regression evidence: PASS — 280 tests (189 retained + 45 fresh + 46 fresh)

Slice 010 focused tests: repository/service 11 PASS retained; original GUI 4 PASS and Integration 2 PASS retained. Fresh affected tests: GUI 5 PASS (including one added untrusted-metadata regression), Integration 2 PASS.

Native Windows Slice 010: PASS — native windows Qt platform, 1000×700, isolated synthetic SQLite. Input-event checks created KB0001 (print spooler) and KB0002 (Microsoft 365 sign-in), selected both and verified correct details, switched through New ticket/Saved tickets/Knowledge Base and reopened both articles after application reconstruction. Empty state, dialog and both article views were visually inspected; no clipping/overlap observed for the supplied examples. Agent checks, not user acceptance testing.

Existing New Ticket, Quick Company, Quick Contact, company/contact/category references, Saved Tickets, notes and Resolve → Close → Reopen are covered by the freshly passing full GUI/Integration suites.

AutoHotkey: NOT RUN in this slice

Migration: NONE — five unchanged migrations; isolated integrity_check = ok and foreign_key_check = zero violations.

Database continuation check: two article rows and two version-1 rows, one snapshot per article. A separate isolated trace proved failed reload rolls back, retry leaves one article/one snapshot and successful creation commits exactly once. Whitespace-only body with newline/tab was rejected and meaningful body whitespace survived storage unchanged.

## Recommended Next Slice

Knowledge article editing with version history: correct an existing draft's title, summary and body, preserve prior revisions atomically and reject stale overwrites, keeping its article code stable. This fixes the immediate inability to correct reusable procedures and reuses the current Knowledge boundaries. See 16_Roadmap.md for the comparison with search/FTS, categories/tags, ticket linking, company/contact management and dashboard/navigation. Recommendation only; no Slice 011 work. Independent Slice 010 review remains the next gate.
