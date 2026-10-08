# Codex instruction: Priority MSP Symptom/RCA Curation T01a

MODE: READ_ONLY ARCHITECTURE RECONCILIATION. Do not write production data, modify migrations, run remediation, or stage/commit code.

1. Read AGENTS.md and approved Foundation 0A–0E. Existing taxonomy/category/Tag sources are authoritative; this package is unreviewed intake ONLY.
2. Inspect current category and tag repositories, Knowledge, Diagnostics, and Clipboard D01 status read-only. Do not assume a historical report is current.
3. Load `priority_rca_graph.proposed.json`, `candidate_reconciliation.csv`, and prior source `coverage_candidates.json` in isolated read-only planning context.
4. Classify each original candidate as symptom, issue, cause, finding, check, action, alias, unrelated, or deferred; preserve source provenance and uncertain labels.
5. Identify existing canonical identities for candidates; never assign novel SQLite identity from draft IDs or title similarity.
6. For every branch, review clinical-style diagnostic logic as IT investigation: which observation supports the cause, what would disconfirm it, and when to stop/escalate. No evidence means no confirmed root cause.
7. Separate factual checks from write actions; require signed-off permission, safety, privacy and user verification for future actions.
8. Reconcile French/English labels, exact aliases versus search-related phrases, and duplicate anchors without destructive merges.
9. Produce approval-ready decisions: REUSE_IDENTITY / ALIAS / RELATED / NEW_DRAFT / DEFER / REJECT, with evidence and owner.
10. Specify JSON Schema 2020-12 and semantic-validation rules as design candidates consistent with 0B; do not finalize before review.
11. Identify coverage gaps, negative test cases, weak branch evidence, tool choices, and versioned corpus splits for later calibration.
12. STOP at READY_FOR_REVIEW, no changes to official Foundation, database, local F7Hub or user's protected worktree.

Outputs: Read-only inventory, source-to-canonical mapping (unknowns explicit), candidate semantic conflict register, relationship validation matrix, coverage gaps, vendor citation backlog, and next independently reviewable slice proposal.
