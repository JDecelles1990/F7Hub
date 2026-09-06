# F7Hub Current State

Last verified: 2026-09-06

Branch: `feat/quick-company-create`

Base HEAD: `d9a25c8f2739d3d252a8749ebd1be5ed031d83d5`; Slice 008 changes are uncommitted for independent review.

## Working

- SQLite bootstrap, migrations through `0005_knowledge.sql`, and integrity checks
- Company and contact repositories
- Ticket creation and Saved Tickets reopening
- Ticket notes, status history, timeline, resolution, closure and reopening
- Company-aware and contact-aware ticket creation with active, company-filtered choices
- Optional active TICKET category selection, category-only refresh/retry and category ID persistence
- Reference refresh/retry, draft preservation and transactional reference validation
- Quick active-company creation from New Ticket, automatic selection and contact reset
- Name validation, background creation, duplicate-submit protection and post-commit refresh recovery
- Saved-ticket company/contact names, including inactive references and safe null/deletion handling
- Saved-ticket current category names, including inactive categories and safe null/deletion handling
- AutoHotkey v2 F7 launch/focus/restore (previously verified; not rerun in Slice 008)

## Partial

- Company creation is name-only; company code and full company management are not exposed
- Contact creation and contact/category management GUI are not implemented
- Category hierarchy formatting is deferred; the selector displays category names directly
- AutoHotkey login startup is not configured

## Not Started

- Knowledge repositories and knowledge GUI
- PowerShell integration

## Current Milestone

QUICK COMPANY CREATION IN TICKET WORKFLOW

## Validation

Database: PASS — 161 tests

GUI: PASS — 30 tests

Integration: PASS — 32 tests

Total regression: PASS — 223 tests

Native Windows visual/input checks: PASS — validation, cancel, company creation, automatic selection, contact reset, complete draft preservation, post-commit refresh recovery, save/reopen, notes and Resolve → Close → Reopen. Form, dialog and saved-ticket layout inspected at 1000×700. Success feedback was moved beside Create Ticket to prevent window growth. Agent checks, not user acceptance testing.

AutoHotkey: NOT RUN in this slice

Migration: NONE — five unchanged migrations; isolated integrity_check = ok and foreign_key_check = zero violations.

## Recommended Next Slice

Create, list and reopen a minimal knowledge article using the existing relational schema and Python service/repository boundaries. Not implemented; editing, search/FTS and ticket linking remain excluded. Complete independent Slice 008 review before starting another feature.
