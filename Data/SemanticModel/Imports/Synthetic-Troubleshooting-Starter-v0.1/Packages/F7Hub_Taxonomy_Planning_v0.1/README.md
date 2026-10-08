# F7Hub Taxonomy Registry, planning proposal v0.1.0

**Status:** Planning-only, not approved as final schema and NOT import-ready. No F7Hub repository or database files were changed.

## Purpose
Organize existing supplied issue/tool/SOP labels and search phrases by semantic type. Preserve the original 46 issue IDs, 26 tool IDs, and 12 SOP IDs. Reuse F7Hub's existing global Tags and scoped Categories. Do not create a competing Tag catalog.

## Inventory
- **46** distinct issue-type definitions with bilingual labels, unreviewed search phrases, hypotheses, tool links and SOP links.
- **26** tool/platform entries, with alias hints pending semantic review.
- **12** procedures with issue references.
- **277** unique lookup phrases, deduplicated by (language, NFKC + casefold + whitespace), with a full list of source uses. These are NOT all canonical tags, concepts, or validated aliases.
- **29** suggested global Tag *candidates*, no auto-create, no assignments.
- **9** domain-to-existing-category mapping placeholders, NOT category IDs.
- **23** proposed entity-type recognition profiles from Foundation 0C, no actual entities or persistent occurrences.
- **9** broad tool name/alias ambiguity review entries.

## Boundaries already established by F7Hub Foundation
- **0A:** Own services remain authoritative; SQLite domain stores remain authoritative for operational business data.
- **0B:** JSON is for serialization and data contract interfaces. A seed/plan registry is not an IPC envelope and should not be confused with runtime state authority.
- **0C:** Reuse existing Categories/Tags; system Tags are global, Categories scoped; entity occurrences feature-owned; aliases and acceptance do not create identities.
- **0E:** Existing categories/global tags/Knowledge assignments are implemented. Families/aliases/lifecycle and additional relationships need feature-owned design and review.

## Fields and semantics
- `issue_id`: stable ID from previous working catalog, not SQLite primary key.
- `proposed_key`: readable lowercase snake_case display-independent key, NOT approved as canonical yet.
- `labels.en` / `labels.fr`: same concept identity, translated display labels.
- `search_phrases`: **search cues** from issue aliases, not semantic equivalence proof.
- `possible_causes`: unverified hypotheses, never confirmed diagnoses.
- `tag_keys`: intentionally empty; no mapping to existing global Tags was verified.
- `category_mapping`: intentionally null; existing scoped category record identities must be inspected first.
- `entity_occurrences`: intentionally empty; never extract user/client data into seed dictionaries.
- `lookup_form`: a term-lookup aid only; never use this generic folding to normalize IPs, file paths, email, error codes, PowerShell commands or external IDs.
- `record_ref` in `search_terms`: original source catalog ID; not an authorized relationship to a canonical DB record.

## Suggested Codex review order
1. Inventory current SQLite `categories`, global `tags`, existing Knowledge assignments and migration history. Read 0A/0B/0C/0E + Foundation AGENTS.md.
2. Reconcile domain groupings against module Category scopes; do NOT map by display name alone.
3. Search existing Tag identities and alias information; classify tag candidates REUSE / ALIAS / PROPOSE NEW / AMBIGUOUS / REJECT.
4. Review all tool search-hint ambiguities. E.g., 'MFA' is **not** equivalent to the Microsoft Authenticator app.
5. Refine synonym, abbreviation, symptom, related phrase, product label and cause roles separately.
6. Approve core semantic registry and localizations; then write approved Feature specification and physical mapping proposal.
7. Only in a separately authorized implementation slice, design bounded SQLite migrations/import tooling and tests. Keep normal service ownership and existing migration rules.

## Validation
- JSON Schema Draft 2020-12 for issue_types and search_terms; other collections have manifest/version wrappers awaiting specialized schemas.
- Cross-reference checks: issue/SOP/tool identifiers, uniqueness, term deduplication, and JSON serialization.
- Semantic correctness and DB/category/tag identity match **NOT VERIFIED**.

## Not a troubleshooting engine
Issue and keyword definitions are documentation data. Neither JSON Schema validity nor parser or AI confidence authorizes remote execution, privileged account changes, or incident closure.
