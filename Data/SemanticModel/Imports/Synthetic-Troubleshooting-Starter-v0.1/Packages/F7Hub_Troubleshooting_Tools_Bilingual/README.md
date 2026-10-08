# F7Hub bilingual troubleshooting & tool catalog (planning draft)

This package normalizes the user-supplied OneNote troubleshooting notes and HiloTech MSP analyst narrative with the previously prepared 46-item issue catalog.

Files:
- `issues_bilingual.csv`: one canonical troubleshooting issue per record; `|` separates multiple associations.
- `tools.csv`: concrete platforms, applications, portals, and named utilities; entries marked learning are not claims of daily practical use.
- `procedures.csv`: procedures separated from actual incidents.
- `catalog.json`: the corresponding JSON source of truth with arrays for relationships.

Counts: 46 canonical issue types, 26 tools/platforms, 12 procedures.

Normalization rules:
1. Issue identifiers are stable within this planning draft. Never silently reassign them once referenced.
2. Symptom category, root cause, affected product, KB article and remediation procedure are separate concepts.
3. Edge/Chrome/Firefox share browser issue IDs; their product names identify the affected application.
4. OST corruption and Outlook profile issues are grouped under EXO-003. MFA set-up and challenge failures are separated.
5. This dataset is intended for review. Do not import to production SQLite without mapping and migration review against Foundation 0A/0B/0C/0D, existing taxonomy and DB constraints.
6. Free-text possible causes are hypotheses, not verified diagnoses. Source notes describe user-provided materials, not independently verified facts.
7. Source materials name SharePoint, Intune, DNS and related areas as study or tool topics without enumerating specific incidents. No new incident types were fabricated for those topics.
8. Product names, knowledge topics and MSP operations are not treated as standalone failures.

Suggested future relational model (not executable schema): issue_type; issue_alias; issue_product; tool; issue_tool; procedure; issue_procedure; diagnostic_check; kb_issue_link. Resolve bilingual strings and aliases into language-specific records when final schema is chosen.
