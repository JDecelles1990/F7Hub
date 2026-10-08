# F7Hub priority RCA curation v0.1.0 (PLANNING ONLY)

Source: `F7Hub_Synthetic_Troubleshooting_Starter_v0_1/data/coverage_candidates.json` previously generated in this conversation. Additional symptom anchors come from the user's stated MSP priorities. Original source items are UNREVIEWED candidates. This is NOT a KB, approved SOP, proven cause map, or live database state.

## Counts

- 31 bilingual draft symptom anchors in 6 high-priority domains.
- 68 reusable proposed cause concepts, 68 proposed diagnostic checks, 68 reusable proposed findings, 68 proposed action descriptions.
- 68 proposed alternative diagnostic branches.
- 36 original candidates in the priority domain scope, including retained deferrals and cause/finding types.
- Reconciliation dispositions: {'SELECTED_SYMPTOM_ANCHOR': 27, 'POSSIBLE_FINDING': 3, 'POSSIBLE_CAUSE': 4, 'DEFERRED_NEXT_COHORT': 1, 'UNSCOPED_POTENTIAL_ISSUE': 1}.
- No calibrated probabilities, no source-backed remedies, no verified SQLite identities, no live F7Hub modifications.

## Document roles

- `priority_rca_graph.proposed.json`: one typed PROPOSAL graph with separate nodes and references. Draft IDs must never be treated as canonical identity.
- `symptom_anchors_review.csv`: bilingual review worksheet with current candidate mappings.
- `candidate_reconciliation.csv`: every original intake candidate in these domains, including deferred or retyped items. No silent dropping.
- `PRIORITY_COVERAGE_GAP_REPORT.md`: gap and review recommendations.
- `CODEX_REVIEW_BRIEF.md`: bounded planning and validation instructions.
- `validate_proposals.py`: offline read-only structural/referential validation for this artifact; not the final Foundation 0B-conformant JSON Schema.

## Safety & architecture

- Approved Foundation 0A–0E remain authoritative. Existing `categories`, `tags` and feature owner services are reused; no second catalog or database is introduced.
- Proposed cause association does NOT assert a root cause. A check observation does NOT prove resolution. Technician-authorized remediation and user verification are required.
- Synthetic information is not suitable for unchecked production troubleshooting.
- Treat potential remedies as review hints only. Do not run, authorize or automate changes based on this artifact.
- Before production use, review Microsoft/vendor references, release versions, privacy gates, privileges, prerequisites, backups, rollback, escalation, bilingual translations and negative tests.
- This is a planning representation, not a final JSON Schema or SQL migration.
