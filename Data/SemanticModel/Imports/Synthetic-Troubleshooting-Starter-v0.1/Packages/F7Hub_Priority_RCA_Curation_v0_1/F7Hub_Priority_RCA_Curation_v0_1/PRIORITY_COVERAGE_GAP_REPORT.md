# Priority coverage-gap and root-cause review

**31 curated draft anchors, 6 priority domains, 68 alternative branches.** All are unverified suggestions.

## Domain summary

| Domain | Anchor count | Review focus |
|---|---:|---|
| `identity_entra` | 6 | Separate symptom from cause, test and remediation |
| `outlook_exchange` | 7 | Separate symptom from cause, test and remediation |
| `onedrive` | 5 | Separate symptom from cause, test and remediation |
| `windows` | 5 | Separate symptom from cause, test and remediation |
| `vpn_remote` | 4 | Separate symptom from cause, test and remediation |
| `network` | 4 | Separate symptom from cause, test and remediation |

## Original candidate reconciliation

Priority-scope original candidates: **36**.

| Classification | Count |
|---|---:|
| `SELECTED_SYMPTOM_ANCHOR` | 27 |
| `POSSIBLE_FINDING` | 3 |
| `POSSIBLE_CAUSE` | 4 |
| `DEFERRED_NEXT_COHORT` | 1 |
| `UNSCOPED_POTENTIAL_ISSUE` | 1 |

### Specific deferred or retyped source items

- **CAND-EXCHANGE-ONLINE-004**: Message quarantined by policy → `POSSIBLE_FINDING`. Quarantine is a policy outcome, not necessarily a failure.
- **CAND-EXCHANGE-ONLINE-005**: Mailbox exceeds storage quota → `POSSIBLE_CAUSE`. Quota reached is a possible explanation for failed mail receipt; do not encode the cause into the symptom anchor.
- **CAND-OUTLOOK-003**: OST data cache corruption → `POSSIBLE_CAUSE`. OST cache corruption is not a user-reported symptom; investigate condition.
- **CAND-OUTLOOK-005**: Calendar events not synchronized → `DEFERRED_NEXT_COHORT`. Calendar synchronization symptom not covered in this set.
- **CAND-OUTLOOK-006**: Outlook add-in blocks startup → `UNSCOPED_POTENTIAL_ISSUE`. Add-in blocks startup, not equivalent to connection failure.
- **CAND-NETWORK-001**: DNS lookup fails on one device → `POSSIBLE_FINDING`. DNS lookup failure is a diagnostic observation; user-visible website loading has a separate anchor.
- **CAND-NETWORK-004**: Gateway unreachable → `POSSIBLE_FINDING`. Gateway unreachable is a diagnostic observation; user-visible LAN access failure has a separate anchor.
- **CAND-NETWORK-005**: Proxy misconfiguration → `POSSIBLE_CAUSE`. Proxy misconfiguration may affect web access.
- **CAND-VPN-REMOTE-004**: Split-tunnel route missing → `POSSIBLE_CAUSE`. Missing split-tunnel route may cause inaccessible internal resources.

## Gaps blocking diagnostic automation

1. No branch has a verified product/version-specific source, validated method, prerequisites, permission scope, rollback, or safe execution contract.
2. No authoritative F7Hub SQLite catalog identities have been reconciled.
3. The branch graph lists plausible alternatives but lacks empirically assessed likelihoods, falsification tests, and contradiction rules.
4. Security/privacy admissibility and tenant policy must be enforced before note ingestion.
5. Bilingual labels require technician review; French and English terms should share the reviewed identity.
6. The rest of the 24-domain corpus remains future coverage; do not treat these 6 domains as exhaustive.
7. Need negative, unresolved, intermittently reproducible and escalated synthetic cases, not just successes.

## Suggested acceptance order

A. Reconcile existing published KB/Tag/Category identities (read-only).
B. Select 10 most common symptoms based on actual authorized triage frequency or a clearly declared expert estimate.
C. For each, review alternate causes, read-only checks, discriminating findings, negative results, and escalation gates.
D. Add vendor citations and test fixtures; separate evidence from unproven hypotheses.
E. Approve bounded, typed relationship vocabulary under Foundation 0C ownership.
F. Only later design importer/SQLite mapping via approved feature slices.
