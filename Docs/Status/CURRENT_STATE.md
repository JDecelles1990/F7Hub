# F7Hub Current State

Last verified: 2026-09-09

Branch: `feat/knowledge-version-history-viewer`

Base HEAD: `4871fd4a1b1ceec8d99dca4247d1407d3e95dc44`

Status: Slice 014 remediation verified, uncommitted, ready for independent re-review. Resumed and preserved the two interrupted GUI fixes and five added integration tests. Fresh verification required no further implementation/test changes. No accidental source duplication or unexpected unrelated paths. Nothing staged; no commit, push or merge. Protected Docs/10 modification and archive deletion remain exactly preserved; ROOT.md, physical schema docs and five historical migrations are unchanged.

## Current Milestone

KNOWLEDGE ARTICLES HAVE READABLE IMMUTABLE HISTORY

## Working

- SQLite bootstrap, five migrations through 0005_knowledge.sql, integrity and FK checks
- New Ticket with company/contact/category references and transactional validation
- Quick Company / Quick Contact creation with safe reference refresh/recovery and draft preservation
- Saved Tickets, current reference names, notes, history/timeline, Resolve → Close → Reopen
- Knowledge create/list/read and DRAFT editing with immutable code, current version and atomic historical snapshots
- Stale-edit protection, safe errors, preserved input and no-change saves without extra revisions
- Plain-text article metadata and read-only Markdown source
- Read-only Version History: newest-first metadata, exact selected immutable snapshot, safe missing/empty states and dismissal
- RELATED Link Article, lightweight current code/title/status/version, Open Article and Refresh
- RELATED Unlink Article for one selected association, with explicit confirmation and Cancel as default/escape
- Exact relationship-only deletion preserving both entities, other RELATED and APPLIED/RESOLUTION_SOURCE rows
- Safe ticket-missing, article-missing and not-linked feedback; concurrent unlink yields one success and one not-linked result
- Async linking/unlinking, duplicate/conflicting-action protection, confirmation/context guards and safe obsolete callbacks
- Failed unlink preserves selection; committed unlink plus failed refresh retains success and recovers through Refresh without another DELETE
- Unlinked articles reappear in Link Article candidates; normal relink persists one association with a fresh linked_at timestamp
- MainWindow-mediated exact article navigation and persisted link/unlink state after application reconstruction
- AutoHotkey F7 launch/focus: VERIFIED; manual Windows verification: PASS — 2026-09-07. Detailed launcher architecture: `Docs/11_AHKArchitecture.md`.

## Historical Data Contract

Knowledge Base → open current article → Version History → select a revision → read its stored snapshot. DRAFT/PUBLISHED/ARCHIVED are all eligible when a service and loaded article are available and the runner is idle. List metadata excludes summary/body; selected detail loads one version using article ID plus version number. Version, title, summary, body, change summary, created by and created at come only from knowledge_article_versions. NULL metadata displays Not provided; timestamps remain as stored. Article code is current immutable identity, not a versioned field. Status, category, updated_by and published_at are not historical snapshots.

VersionHistoryDialog renders plain text, disables row interaction during async reads, checks revision identity/generation and ignores callbacks after dismissal. Top-level window ownership keeps Close/Escape enabled outside the disabled page hierarchy, with Qt cleanup on window destruction. Metadata scrolls independently while reserving useful read-only body space. Current article content is never substituted. Missing article, missing revision and empty history have safe distinct feedback. Ticket Open Article still opens the current article; history is an explicit separate action.

## Deferred / Limitations

- Restore/revert, historical editing/deletion, compare/apply, historical status snapshots, search/FTS and AI.
- No pagination or large-history performance validation; actual user library volume is NOT VERIFIED.
- Table titles may use ellipsis; the selected detail displays the complete title.
- Bulk linking/unlinking, APPLIED/RESOLUTION_SOURCE workflows, relationship-type editing and relationship history/undo.
- Article publishing/archiving/deletion, categories/tags and ticket-driven article creation/editing.
- Full company/contact/category management, PowerShell integration and AutoHotkey login startup.
- Existing current-article list still loads bodies; history and relationship lists are lightweight.

## Validation

Fresh results after the preserved remediation, 2026-09-09:

| Scope | Count | Test duration | Process elapsed | Exit |
|---|---:|---:|---:|---:|
| Focused Integration | 29 PASS | 118.030s | 120.656s | 0 |
| Full Database | 251 PASS | 10.345s | 10.587s | 0 |
| Full GUI | 81 PASS | 9.678s | 10.105s | 0 |
| Full Integration | 73 PASS | 273.218s | 273.625s | 0 |

Full suites ran sequentially: **405 PASS**, five above the 400 pre-remediation total (251 / 81 / 68). No suite decreased. The five additions cover the four pending-read dismissal combinations through the real MainWindow hierarchy and long-summary accessibility. Full regression covers New Ticket, Quick Company/Contact, saved tickets, notes/status, Knowledge create/read/edit and RELATED Link/Open/Unlink/Relink. GUI/Integration suites used offscreen Qt.

Retained evidence: post-fix focused GUI log on 2026-09-09 confirms 19 PASS in 3.871s, exit 0; GUI implementation was unchanged during this resume and is also covered by the fresh full GUI suite. Earlier focused repository/service 31 PASS is historical, not rerun as a separate focused command. Explicit py_compile and AST duplicate import/function checks passed. A separate real-MainWindow ownership check verified the workspace reference, dismissal guard and Qt cleanup on window destruction. Only documentation changed after validation.

Fresh focused Integration and full regression commands used the existing `.venv\Scripts\python.exe`, with `PYTHONPATH=$PWD\Python;$PWD`, `PYTHONDONTWRITEBYTECODE=1`, and `QT_QPA_PLATFORM=offscreen`:

```powershell
.venv\Scripts\python.exe -B -m unittest Tests.Integration.test_knowledge_base_flow Tests.Integration.test_ticket_knowledge_flow -v
.venv\Scripts\python.exe -B -m unittest discover -s Tests/Database -p "test_*.py" -v
.venv\Scripts\python.exe -B -m unittest discover -s Tests/GUI -p "test_*.py" -v
.venv\Scripts\python.exe -B -m unittest discover -s Tests/Integration -p "test_*.py" -v
```

Native Windows remediation: PASS — fresh on 2026-09-09 using the existing TEMP native.py, windows Qt, isolated synthetic SQLite, 1000×700 main window and 900×620 history dialog. Pending list + Close, list + Escape, detail + Close and detail + Escape all passed before reads completed; competing actions stayed blocked, late callbacks did not mutate/resurrect dismissed state and current article/database remained unchanged. A 6,132-character summary displayed literal tag/Markdown-like text; scrolling via keyboard reached END-OF-LONG-SUMMARY, with a 356-pixel read-only body. All six captures were inspected: four pending states plus summary start/end, with accessible markers and no overlap. Trace contained 18 SELECTs with nine BEGIN/ROLLBACK pairs; no data writes. Agent verification, not user acceptance testing. Evidence folder: `C:\Users\Jo\AppData\Local\Temp\f7hub-slice014-remediation-f3870f277a904aa4b26fd1c639ec1e23`.

Historical native validation recorded on 2026-09-08 (not a fresh repetition of those broader checks): Created KB0001 V1 → V2 → V3, checked initial V3/newest-first 3/2/1, exact V1/V2/V3 title/summary/body, close with current V3 unchanged, and reopened history. Created KB0002 and saved another edit; PUBLISHED/ARCHIVED history remained available with Edit disabled. Captured windows were visually inspected: selected detail/body and controls readable without overlap in tested layouts; table titles use ellipsis as needed. Agent verification, not user acceptance testing. Harnesses, captures, SQL trace, databases and logs stayed outside the repository.

AutoHotkey: NOT RUN during Slice 014 — unchanged. The earlier manual launcher PASS of 2026-09-07 remains historical evidence, not a fresh check.

## Database / No-write Evidence

Migration count: 5. New migration: NO. Schema changes: NONE. Historical migrations unchanged. Isolated integrity_check = ok; foreign_key_check = zero violations.

History list/detail SQL trace: BEGIN → SELECT article existence → SELECT requested history metadata/detail → ROLLBACK on connection cleanup. SELECT-only data access; no INSERT/UPDATE/DELETE. The list query excludes body_markdown and selected detail includes exactly one body. Existing idx_knowledge_versions_article_version supports newest-first reads; no redundant index added. Full logical database dump, current row and history rows are unchanged across opening, selecting and closing the viewer. Prior V1 remains exact after V2/V3 edits and application reconstruction.

## Next Gate / Candidate

Independent Slice 014 re-review is next. Keep changes unstaged and uncommitted; do not push or merge.

Recommend exactly one next slice: Knowledge Search / FTS5 for current articles only, with result → open through existing navigation. See 16_Roadmap.md for the six-option assessment and scope limits. Recommendation only; no Slice 015 implementation.
