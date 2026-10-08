# Diversified technical case collection and synthetic data quality

## What "exhaustive" means

Aim for **coverage completeness against a versioned scope matrix**, not literally every IT problem. Track each domain, issue family, supported platform/version, severity/impact, diagnostic alternatives and lifecycle stage. Report absent coverage as gaps. Initial seed = 24 cases, 24 domains, 106 unreviewed issue-family prompts. Not exhaustive and not verified against production taxonomy.

## Source channels (distinct provenance labels)

1. `AUTHOR_ORIGINAL_SYNTHETIC`: technician-created fictional case narratives, manually checked.
2. `GENERATED_SYNTHETIC_DRAFT`: model-generated synthetic cases, untrusted until factual and coherence review.
3. `PUBLIC_DATASET_IMPORT`: external licensed dataset with attribution, source snapshot hash and source-specific transformation policy.
4. `VENDOR_DOCUMENTATION_EXTRACT`: version-specific symptom/check candidates extracted from official vendor docs, with precise URL/version/date, not copied wholesale or asserted as proven case histories.
5. `AUTHORIZED_SANITIZED_CASE`: real case only with employer authorization, limited purpose, complete privacy handling and explicit approval. Not required for the prototype.
6. `TECHNICIAN_CONCEPT_PROPOSAL`: manually entered candidate in read-only KB Concept Explorer, not published.

Keep all source types distinct. Do not launder synthetic/generated language into real-world success evidence.

## Diversity axes: deliberately vary with controls

- Domain / product / platform version / environment (Windows 10 vs 11, desktop vs web)
- Scope: one user vs team vs tenant-wide; single device vs service-wide
- Language: EN, FR, bilingual mixed; informal vs formal wording, typo, abbreviation
- State: unresolved, mitigated, resolved, escalated, intermittent, not reproducible
- Cause: credentials, service outage, client state, permissions, routing, policy, dependency, hardware
- Contradictions: similar symptoms with distinct verified causes; same cause with different reported symptoms
- Safety: read-only diagnosis, authorized configuration change, admin-only escalation, security-sensitive triage
- Evidence: strong distinguishing check vs insufficient evidence vs contradictory findings
- Failure modes: denied permission, unavailable tool, stale documentation, unexpected result, partial processing
- Time: before/after restart, sign-in token expiry, policy propagation, intermittent failure

For a given issue, generate a **bounded family of genuinely different scenarios**, not dozens of superficial paraphrases labeled as independent ground truth.

## Acceptance and review workflow

`INTAKE → PRIVACY_GATE → STRUCTURAL_CHECK → CANONICAL_LOOKUP → SEMANTIC_REVIEW → VENDOR_REFERENCE_CHECK → HUMAN_TECHNICAL_REVIEW → APPROVED_CANDIDATE → DOMAIN_OWNED_PUBLICATION`

The final publication transition is NOT implemented by this package.

QA requires each draft to include (at minimum) bilingual titles/reports, environment, impact, symptoms, three diagnostic actions and fictional observations, cause and discriminating evidence, safe resolution, verification, rollback/escalation considerations, explicit source/provenance, and flags that prevent unreviewed data from being used as production KB. The exact future approved case schema must be determined by domain owners and Foundation rules, not this seed.

## Data leakage / confidence safeguards

- Test corpus must be distinct from generated training phrases and near-duplicate cases; split by canonical issue and/or scenario family, not just random rows.
- Maintain hard negatives and OOD/no-answer examples. A success-only corpus causes systematic overconfidence and anchoring.
- Evaluate **coverage, precision, recall, false-match rate, abstention rate, calibration**, bilingual performance, and safety violations separately.
- Keep embedding scores separate from probabilities. No fabricated confidence thresholds.
- Change to lexicon, source version or model requires same frozen evaluation suite and a regression report.
- Avoid introducing the answer in input text or explanation templates in ways that create artificial model performance.
- Test on independent real-world, appropriately authorized and curated examples before drawing conclusions about helpdesk performance.

## Handling new data later

- Manual: KB Concept Explorer entry, raw technical term, attachments with source provenance, technician resolution record after permission check.
- Automated (offline): periodic import of explicitly selected local sanitized files, rules/NER, fuzzy candidates, optional batch embeddings, near-duplicate grouping, nightly or on-demand review queue.
- Automated (online research, opt-in only): collect official documentation pages with attribution, version and publication date, isolate from client notes, queue proposals for review; no silent bulk insert.
- No background clipboard harvesting, unlimited ticket ingestion or production database write during this planning stage.

## Recommended staged adoption

Stage A: deterministic filters + alias proposal, 24 synthetic golden-format checks.
Stage B: manually reviewed diverse expanded corpus with genuine negatives and ambiguous cases.
Stage C: optional multilingual embeddings on held-out corpus; compare to Stage A.
Stage D: guarded F7Hub feature integration, after independently reviewed slices; then evaluate against authorized cases.
