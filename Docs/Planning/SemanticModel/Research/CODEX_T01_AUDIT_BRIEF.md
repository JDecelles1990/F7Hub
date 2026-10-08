# Codex brief: T01-A 24-domain taxonomy coverage and RCA audit

MODE: AUDIT / READ-ONLY / NO IMPLEMENTATION.

### Inputs

- Foundation 0A–0E approved contracts and scoped AGENTS.md guidance.
- Current repository taxonomy migration, Tag/Category repositories, KB, diagnostic and Clipboard plans.
- Read-only user supplied `coverage_candidates.json`, `synthetic_cases.jsonl`, and this generated `COVERAGE_GAP_AUDIT.json`.
- If provided, approved human-reviewed prior issue/alias catalogs. Treat prior exported lists as candidates unless imported/verified.

### Mandatory rules

- 0A–0E are authoritative; do not rewrite their architecture.
- No SQLite writes, seeds, migrations, schema edits, commits, branch changes, real ticket exports or unapproved network/provider access.
- Inspect the **existing** Tag and Category authority; do not invent a parallel global catalog.
- Classify candidate names by their *semantic role*, not their original `issue_label_en` field. Some labels are findings or causes, not issues.
- A repeated symptom is not necessarily one root cause. Multiple verified conditional pathways must be supported.
- Aliases are equivalent terms only; similarity or relatedness is not identity.
- An ordered diagnostic check cannot automatically execute a remediation. Security/access changes require separate authorization.
- Synthetic success is not evidence of real-world effectiveness; never use synthetic text alone to calibrate diagnostic probability.
- Preserve source references and unresolved ambiguity. No fabricated numeric confidence.

### Required deliverables

1. A complete actual catalog inventory: current installed Categories/Tags and relevant service-owned Types/KB IDs, with facts vs unknowns.
2. 24-domain coverage-gap matrix reconciling all 106 intake candidates and 24 case seeds to canonical identities when *verified*, else null.
3. Semantic role suggestions: `issue`, `symptom`, `cause_hypothesis`, `diagnostic_check`, `finding`, `remediation`, `verification`, `procedure`, `tag`, `category`, `alias`, `other`.
4. Root-cause graph predicate draft with typed allowed endpoints, directionality, evidence origins, lifecycle, cardinality, no-invalid-cycles rules.
5. Prioritized shortlist of first 20–30 high-value **symptom anchors**, and the minimum discriminating checks for each.
6. Diversity matrix: positive/negative/inconclusive, success/failure, escalated, intermittent, bilingual, version/product and single/multi-user scenarios.
7. Duplicate/collision report with `REUSE`, `ALIAS_CANDIDATE`, `RELATED_DISTINCT`, `NEW_CANDIDATE`, `AMBIGUOUS`, `REJECT` outcomes.
8. Gap register for vendor documentation, safe diagnostics and privacy policy; no source is invented.
9. Proposed read-only Knowledge Concept Explorer and reconciliation workflow consistent with Foundation 0C.
10. A bounded next slice proposal and validation/test matrix. STOP AT READY_FOR_REVIEW.

### Acceptance

- All 24 source domains accounted for; all 106 candidate IDs and all 24 case IDs preserved exactly in audit coverage.
- Candidate counts reflect unreviewed source labels, not verified unique issues.
- No accepted new canonical concept solely by an embedding/fuzzy match.
- No synthetic data enters production KB or operational F7Hub SQLite.
- Every proposed relation has a clear endpoint type and a review/authority status.
- Output explicitly distinguishes existing implementation, approved Foundation, unapproved planning candidates and unknowns.
