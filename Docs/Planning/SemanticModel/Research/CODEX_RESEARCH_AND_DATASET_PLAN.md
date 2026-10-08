# Codex brief: F7Hub Open-Source Reuse Audit & Synthetic Case Pipeline

## Execution mode / hard stops

`ARCHITECT / RESEARCH / READ_ONLY` — do not install third-party packages into canonical F7Hub virtualenv; do not execute untrusted scripts or serialized model artifacts; do not alter 0A–0E, Clipboard D01, live SQLite, schema/migrations, protected paths, branch state, or user data. Do not stage, commit, or integrate. If the current baseline/worktree is not what the router expects, STOP and report, preserving the original 30-file candidate.

## Mandatory authoritative sources

- Root and scoped `AGENTS.md` routing.
- `Docs/Planning/Foundation/0A` through `0E` (approved architectural decisions, execution reports).
- `Docs/Planning/Clipboard/1A` to `1C` and current D01 candidate/worktree identity.
- `Database/Migrations/0002_taxonomy.sql`, `0005_knowledge.sql`, `0006_knowledge_search.sql`, owning repositories/services and import/test conventions.
- This package is UNAPPROVED input only. Do not treat its proposed keys/domains as authoritative.

## A. Seven-project audit

Examine the seven links in `OPEN_SOURCE_REUSE_ASSESSMENT.md`. For each, capture pinned commit SHA/tag, LICENSE and dependency tree, active maintenance/issue patterns, security and supply-chain risks, model-artifact/license implications, Python/Windows compatibility, CPU/offline footprint, English/French behavior, available tests, API shape, data export, privacy handling and risk of taxonomy collision. Check code license separately from datasets. Include reproducible benchmark plan, not invented numbers. Prefer source inspection and isolated experiments after approval.

## B. Corpus design

Use the starter's 24 fictional cases and 106 unreviewed candidates as examples, not approved labels. Design a full scoped coverage matrix: domain → issue family → symptom variants → differential diagnoses → diagnostic checks → possible causes → verified decision → safe resolution → verification → escalation. Each must link to canonical identity ONLY after an authoritative lookup. Define versioned typed JSON Schema per entity type with 0B-compatible contracts and 0C meanings; reuse existing Tag and Category IDs.

Add controlled diverse intake streams for manual technician contributions, synthetic drafts, approved vendor docs, independently licensed datasets and (later, with authorization only) sanitized real cases.

## C. Evaluation plan

Define frozen bilingual positive, hard-negative, ambiguous, contradictory and OOD fixtures. Compare exact/approved aliases vs RapidFuzz vs spaCy vs TF-IDF vs optional embeddings and BERTopic. Report precision, recall, F1, confusion, false merges, human review burden, CPU/memory/latency, and selective risk/abstention. Distinguish ranking from probability. Prevent near-duplicate train/test leakage. Include provenance and licensing validation. No bulk pseudo-label-to-training shortcut.

## D. Expected deliverables

1. OSS Reuse Matrix, pinned revisions, license/compatibility report.
2. Existing F7Hub taxonomy-owner inventory (current code and read-only catalogs; no user data exfiltration).
3. Corpus provenance, identity/graph mapping and review workflow design.
4. Candidate dataset JSON Schema and validator assessment; proposed future migration mapping only.
5. Synthetic case coverage/gap/dedup report, with negative and incomplete outcomes prioritized.
6. Minimal safe read-only Python prototype plan (future separate approval).
7. Risk register, tests, explicit unknowns, independently reviewable feature slices.

Stop at `READY_FOR_REVIEW`, no execution/import into production. Cite source paths, commits and upstream project documentation for every factual claim.
