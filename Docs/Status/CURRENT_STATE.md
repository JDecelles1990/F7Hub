# F7Hub Current State

Last verified: 2026-09-06

Branch: `feat/quick-contact-create`

Base HEAD: `30cf7f616bb67bbe92209042bf91e3e919e44c3b`; Slice 009 and unavailable-company recovery remediation are uncommitted for independent re-review.

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
- AutoHotkey v2 F7 launch/focus/restore (previously verified; not rerun in Slice 009)

## Partial

- Company creation is name-only; company code and full company management are not exposed
- Contact creation is limited to selected companies; contact editing/deletion and contact/category management GUI are not implemented
- Category hierarchy formatting is deferred; the selector displays category names directly
- AutoHotkey login startup is not configured

## Not Started

- Knowledge repositories and knowledge GUI
- PowerShell integration

## Current Milestone

QUICK COMPANY AND CONTACT CREATION IN TICKET WORKFLOW

## Validation

Database: PASS — 178 tests

GUI: PASS — 40 tests

Integration: PASS — 44 tests

Total regression: PASS — 262 tests

Remediation focused tests: PASS — 12 quick-contact integration, 10 database reference, 12 reference-widget and 10 quick-contact dialog tests (44 total).

Native Windows remediation checks: PASS — three synthetic integration tests using the windows platform at 1000×700: company deactivation recovery, company deletion recovery and normal contact create/auto-select/save/reopen. Draft preservation, responsiveness, company reselection and ticket save after recovery passed; recovery feedback/action layout visually inspected. Earlier Slice 009 checks covered 18 GUI/integration tests and combined Add Company → Add Contact. Existing notes and status lifecycle passed the post-remediation automated regression. Agent checks, not user acceptance testing.

AutoHotkey: NOT RUN in this slice

Migration: NONE — five unchanged migrations; isolated integrity_check = ok and foreign_key_check = zero violations.

## Recommended Next Slice

Create, list and reopen a minimal knowledge article using the existing relational schema and Python service/repository boundaries. Not implemented; editing, search/FTS and ticket linking remain excluded. Complete independent Slice 009 review before starting another feature.
