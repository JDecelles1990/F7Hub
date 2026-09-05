# F7Hub Current State

Last verified: 2026-09-05

Branch: `main` and `recovery/2026-09-05-first-usable-ticket-workflow`

HEAD after commit: this recovery checkpoint commit (`git rev-parse HEAD`)

## Working

- SQLite bootstrap, migrations through `0005_knowledge.sql`, and integrity checks
- Company and contact repositories
- Ticket creation, reload, notes, status history, timeline, resolution, closure, and reopening
- PySide6 New Ticket and Saved Tickets workflows with background service execution
- AutoHotkey v2 F7 launch, focus, restore, and duplicate-launch protection

## Partial

- Company, contact, and category fields exist in ticket creation, but reference choices are not loaded into the GUI
- AutoHotkey is a development-session launcher; login startup is not configured

## Not Started

- Reference-aware company/contact ticket creation
- Knowledge repositories and knowledge GUI
- PowerShell integration

## Current Milestone

First Useful Local Ticket Workflow

## Baseline Tests

Database: PASS — 133 tests

GUI: PASS — 10 tests

Integration: PASS — 14 tests

AutoHotkey: PASS — live launcher verification

## Next Approved Slice

Reference-aware company/contact ticket creation

## Next User-Visible Target

```text
Launch F7Hub
→ New Ticket
→ select company
→ select matching contact
→ Save
→ reopen ticket
→ correct company/contact displayed
```
