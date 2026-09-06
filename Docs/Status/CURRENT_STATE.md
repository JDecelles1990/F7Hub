# F7Hub Current State

Last verified: 2026-09-05

Branch: `feat/ticket-category-reference`

Base HEAD: `66c370e9ca67527a01e30c57d34766fde7e6fc1f`; Slice 007 changes are uncommitted for independent review.

## Working

- SQLite bootstrap, migrations through `0005_knowledge.sql`, and integrity checks
- Company and contact repositories
- Ticket creation and Saved Tickets reopening
- Ticket notes, status history, timeline, resolution, closure and reopening
- Company-aware and contact-aware ticket creation with active, company-filtered choices
- Optional active TICKET category selection, category-only refresh/retry and category ID persistence
- Reference refresh/retry, draft preservation and transactional reference validation
- Saved-ticket company/contact names, including inactive references and safe null/deletion handling
- Saved-ticket current category names, including inactive categories and safe null/deletion handling
- AutoHotkey v2 F7 launch/focus/restore (previously verified; not rerun in Slice 007)

## Partial

- Company/contact/category management GUI is not implemented; selectors use existing database records
- Category hierarchy formatting is deferred; the selector displays category names directly
- AutoHotkey login startup is not configured

## Not Started

- Knowledge repositories and knowledge GUI
- PowerShell integration

## Current Milestone

Ticket Creation References Complete

## Validation

Database: PASS — 152 tests

GUI: PASS — 22 tests

Integration: PASS — 27 tests

Total regression: PASS — 201 tests

Native Windows visual/input checks: PASS — synthetic category population/filtering, failure/retry, draft and company/contact preservation, save/reopen, optional category, notes and status lifecycle. Corrected form and saved-ticket layout verified at 1000×700. Agent checks, not user acceptance testing.

AutoHotkey: NOT RUN in this slice

Migration: NONE — five unchanged migrations; isolated integrity_check = ok and foreign_key_check = zero violations.

## Recommended Next Slice

Create an active company from New Ticket and select it immediately, using a small service-backed form and the existing CompanyRepository. Not implemented. Complete the independent Slice 007 review before starting another feature.
