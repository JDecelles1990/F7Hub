# F7Hub Current State

Last verified: 2026-09-05

Branch: `feat/ticket-reference-data`

Base HEAD: `3e99db6f35ddf5d23a2d22905a92a40c3d0425c2`; Slice 006 changes are uncommitted for review.

## Working

- SQLite bootstrap, migrations through `0005_knowledge.sql`, and integrity checks
- Company and contact repositories
- Ticket creation and Saved Tickets reopening
- Ticket notes, status history, timeline, resolution, closure and reopening
- Company-aware and contact-aware ticket creation with active, company-filtered choices
- Reference refresh/retry, draft preservation and transactional reference validation
- Saved-ticket company/contact names, including inactive references and safe null/deletion handling
- AutoHotkey v2 F7 launch/focus/restore (previously verified; not rerun in Slice 006)

## Partial

- Category choices are not loaded into New Ticket
- Company/contact management GUI is not implemented; selectors use existing database records
- AutoHotkey login startup is not configured

## Not Started

- Knowledge repositories and knowledge GUI
- PowerShell integration

## Current Milestone

Reference-Aware Ticket Creation

## Validation

Database: PASS — 142 tests

GUI: PASS — 16 tests

Integration: PASS — 21 tests

Native Windows visual/input checks: PASS — synthetic reference selection, switching, save/reopen, empty states, query/stale-reference errors and draft preservation; initial size and 1000×700. Agent checks, not user acceptance testing.

AutoHotkey: NOT RUN in this slice

Migration: NONE

## Recommended Next Slice

KnowledgeRepository article creation/reload with isolated repository tests using the existing `0005_knowledge.sql` schema. Not implemented.
