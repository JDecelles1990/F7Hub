# F7Hub 24-Domain Coverage & Root-Cause Modeling Audit (Draft v0.1)

> READ-ONLY planning artifact. Not an approved taxonomy, case library, or implementation authorization.

## Verified inventory from starter files

- **24** distinct domain keys; **106** unreviewed candidate labels; **24** synthetic cases (one per domain).
- All 24 cases have `canonical_issue_ref = null`, `review_status = UNREVIEWED`, outcome `SIMULATED_RESOLVED`, and simulated success.
- All 24 cases require official source verification and currently have **no vendor reference URLs**.
- Therefore: **validated candidate coverage is unknown**, not 24/106 or 106/106. Individual candidate-to-case semantic links have not been reviewed.
- All 106 labels have `canonical_id = null`; do not import them as existing F7Hub identities.

## Domain-level coverage matrix

Priority is an **editorial proposal**, not measured ticket frequency. Each line shows the existing single synthetic example and three *candidates for first review*; their assignment is not verified.

| Domain | Candidates | Cases | Priority | Sample case | First-review candidates |
|---|---:|---:|---|---|---|
| Identity Entra | 6 | 1 | A | MFA registration fails after phone replacement | MFA enrollment fails after phone replacement; Unexpected conditional access denial; Password change not synchronized |
| Exchange Online | 5 | 1 | A | Shared mailbox cannot be opened | Shared mailbox access denied; Inbound message rejected by mail flow; Distribution group delivery issue |
| Outlook | 6 | 1 | A | Outlook repeatedly prompts for credentials | Repeated password prompts; Outlook cannot connect; OST data cache corruption |
| Microsoft Teams | 5 | 1 | A | Teams meeting microphone not detected | Meeting microphone not detected; User cannot join meeting; Teams login loop |
| Onedrive | 5 | 1 | A | OneDrive file remains unsynchronized | Known Folder Move conflict; File sync stalled; Storage quota reached |
| Sharepoint | 4 | 1 | A | SharePoint document library access denied | SharePoint document access denied; Document library fails to load; Guest access denied |
| M365 Apps | 4 | 1 | A | Word reports an activation problem | Office activation fails; Word cannot save to cloud location; Excel add-in prevents startup |
| Windows | 5 | 1 | A | Windows Update repeatedly requests installation | Windows update stuck pending restart; User profile fails to load; Workstation starts slowly |
| Hardware | 4 | 1 | B | External monitor is blank through dock | Docking station monitor not detected; Laptop battery not charging; USB keyboard stops responding |
| Network | 5 | 1 | A | Websites fail by hostname on one PC | DNS lookup fails on one device; DHCP address missing; Wi-Fi connected without Internet |
| VPN Remote | 4 | 1 | A | VPN connects but internal file share is unreachable | VPN connects but internal share inaccessible; VPN MFA authentication fails; RDP cannot reach permitted host |
| Browsers | 5 | 1 | A | Web portal fails only in Chrome profile | Chrome extension blocks web portal; Edge profile sync fails; Firefox user profile corruption |
| Printing | 4 | 1 | A | Printer queue stalls on one workstation | Print queue blocked by stalled job; Printer mapping fails; Printer driver conflict |
| Security Defender | 4 | 1 | A | Defender alert blocks approved utility | False-positive malware detection review; Suspicious login investigation; Reported phishing email triage |
| Intune | 4 | 1 | B | Device compliance does not refresh | Compliance policy fails to refresh; Enrollment blocked by device restriction; Required app install remains pending |
| Azure | 4 | 1 | C | Azure VM operator cannot start a VM | Azure VM access denied by role; VM private DNS resolution fails; Storage account network access blocked |
| Active Directory | 4 | 1 | B | GPO network drive mapping missing | GPO drive mapping not applied; Domain join fails; Group membership not reflected |
| File Storage | 4 | 1 | B | Network share denies read permission | Mapped drive permission denied; File share offline; Disk volume nearly full |
| Software | 4 | 1 | B | Line-of-business app installer fails | MSI installation blocked by prerequisite; Application crashes on launch; Software updater fails |
| Certificates | 4 | 1 | C | Internal HTTPS portal reports expired certificate | Expired TLS certificate warning; Certificate chain not trusted; VPN device certificate missing |
| VoIP | 4 | 1 | C | Softphone rings but has no sound | Softphone has no audio output; VoIP phone fails registration; Intermittent call quality |
| Backup | 4 | 1 | C | Scheduled backup reports insufficient capacity | Scheduled backup job fails; Restore job reports missing file; Backup agent is offline |
| MSP Tools | 4 | 1 | B | RMM agent shows offline while PC is online | Remote monitoring agent offline; Remote assistance session blocked; RMM policy application delayed |
| Powershell Automation | 4 | 1 | B | PowerShell cmdlet is not recognized | PowerShell module missing; Execution policy prevents local script; Graph API command returns insufficient privileges |

## Gap classes that must be resolved before production taxonomy seeding

1. **Identity gap:** No case has an accepted canonical issue link; no verified links to existing F7Hub taxonomy rows.
2. **Ontology gap:** Labels mix issue, symptom, cause, finding, and investigation task (see role-hint examples below).
3. **Evidence gap:** All case observations are fictional and no cases have official source URLs; do not infer general technical correctness.
4. **Outcome gap:** All cases are simulated resolved/pass; add ambiguous, unresolved, failed-remediation, escalated, recurring, and negative scenarios.
5. **Differential-diagnosis gap:** One case per domain cannot adequately compare alternative causes for the same symptom.
6. **Bilingual detail gap:** Case titles/reports are bilingual, but diagnostic detail is not yet uniformly bilingual.
7. **Provenance gap:** No confidence calibration or evidence from independently labeled real-world outcome samples.
8. **Research coverage gap:** Additional issues should be sourced from official/vendor docs only through reviewed, licensed intake, not guessed as established facts.

## Examples of candidate terminology needing type review

| Domain | Candidate label | Proposed role hint (not approved) |
|---|---|---|
| outlook | OST data cache corruption | `possible_cause_or_condition` |
| outlook | Outlook add-in blocks startup | `issue_or_cause_requires_review` |
| network | DNS lookup fails on one device | `symptom_or_diagnostic_finding` |
| network | Gateway unreachable | `diagnostic_finding_or_issue_requires_context` |
| network | Proxy misconfiguration | `possible_cause` |
| exchange_online | Message quarantined by policy | `observed_state_or_incident` |
| backup | Backup storage capacity exceeded | `condition_or_possible_cause` |
| security_defender | False-positive malware detection review | `investigation_task_or_finding` |
| outlook | Repeated password prompts | `user_visible_symptom` |
| onedrive | File sync stalled | `user_visible_symptom` |
| vpn_remote | VPN connects but internal share inaccessible | `user_visible_symptom` |
| powershell_automation | PowerShell module missing | `possible_cause_or_prerequisite` |

## Complete candidate inventory by domain

Every following entry is an **unreviewed candidate**, not a canonical issue. The source file supplies no accepted entity/type/relationship mapping.

### Identity Entra (6 candidates / 1 synthetic case)
Illustrative synthetic case: SYN-IT-0001 · MFA registration fails after phone replacement. No validated case-to-candidate mapping.
- `CAND-IDENTITY-ENTRA-001`: MFA enrollment fails after phone replacement
- `CAND-IDENTITY-ENTRA-002`: Unexpected conditional access denial
- `CAND-IDENTITY-ENTRA-003`: Password change not synchronized
- `CAND-IDENTITY-ENTRA-004`: Account locked after repeated attempts
- `CAND-IDENTITY-ENTRA-005`: User missing required group access
- `CAND-IDENTITY-ENTRA-006`: Provisioned user cannot access licensed service

### Exchange Online (5 candidates / 1 synthetic case)
Illustrative synthetic case: SYN-IT-0002 · Shared mailbox cannot be opened. No validated case-to-candidate mapping.
- `CAND-EXCHANGE-ONLINE-001`: Shared mailbox access denied
- `CAND-EXCHANGE-ONLINE-002`: Inbound message rejected by mail flow
- `CAND-EXCHANGE-ONLINE-003`: Distribution group delivery issue
- `CAND-EXCHANGE-ONLINE-004`: Message quarantined by policy (type review: observed_state_or_incident)
- `CAND-EXCHANGE-ONLINE-005`: Mailbox exceeds storage quota

### Outlook (6 candidates / 1 synthetic case)
Illustrative synthetic case: SYN-IT-0003 · Outlook repeatedly prompts for credentials. No validated case-to-candidate mapping.
- `CAND-OUTLOOK-001`: Repeated password prompts (type review: user_visible_symptom)
- `CAND-OUTLOOK-002`: Outlook cannot connect
- `CAND-OUTLOOK-003`: OST data cache corruption (type review: possible_cause_or_condition)
- `CAND-OUTLOOK-004`: Outlook search returns incomplete results
- `CAND-OUTLOOK-005`: Calendar events not synchronized
- `CAND-OUTLOOK-006`: Outlook add-in blocks startup (type review: issue_or_cause_requires_review)

### Microsoft Teams (5 candidates / 1 synthetic case)
Illustrative synthetic case: SYN-IT-0004 · Teams meeting microphone not detected. No validated case-to-candidate mapping.
- `CAND-MICROSOFT-TEAMS-001`: Meeting microphone not detected
- `CAND-MICROSOFT-TEAMS-002`: User cannot join meeting
- `CAND-MICROSOFT-TEAMS-003`: Teams login loop
- `CAND-MICROSOFT-TEAMS-004`: Screen sharing unavailable
- `CAND-MICROSOFT-TEAMS-005`: Notifications missing

### Onedrive (5 candidates / 1 synthetic case)
Illustrative synthetic case: SYN-IT-0005 · OneDrive file remains unsynchronized. No validated case-to-candidate mapping.
- `CAND-ONEDRIVE-001`: Known Folder Move conflict
- `CAND-ONEDRIVE-002`: File sync stalled (type review: user_visible_symptom)
- `CAND-ONEDRIVE-003`: Storage quota reached
- `CAND-ONEDRIVE-004`: File name unsupported
- `CAND-ONEDRIVE-005`: OneDrive sign-in failure

### Sharepoint (4 candidates / 1 synthetic case)
Illustrative synthetic case: SYN-IT-0006 · SharePoint document library access denied. No validated case-to-candidate mapping.
- `CAND-SHAREPOINT-001`: SharePoint document access denied
- `CAND-SHAREPOINT-002`: Document library fails to load
- `CAND-SHAREPOINT-003`: Guest access denied
- `CAND-SHAREPOINT-004`: Office file checked out and locked

### M365 Apps (4 candidates / 1 synthetic case)
Illustrative synthetic case: SYN-IT-0007 · Word reports an activation problem. No validated case-to-candidate mapping.
- `CAND-M365-APPS-001`: Office activation fails
- `CAND-M365-APPS-002`: Word cannot save to cloud location
- `CAND-M365-APPS-003`: Excel add-in prevents startup
- `CAND-M365-APPS-004`: Office app update fails

### Windows (5 candidates / 1 synthetic case)
Illustrative synthetic case: SYN-IT-0008 · Windows Update repeatedly requests installation. No validated case-to-candidate mapping.
- `CAND-WINDOWS-001`: Windows update stuck pending restart
- `CAND-WINDOWS-002`: User profile fails to load
- `CAND-WINDOWS-003`: Workstation starts slowly
- `CAND-WINDOWS-004`: Unexpected BSOD
- `CAND-WINDOWS-005`: Startup repair loop

### Hardware (4 candidates / 1 synthetic case)
Illustrative synthetic case: SYN-IT-0009 · External monitor is blank through dock. No validated case-to-candidate mapping.
- `CAND-HARDWARE-001`: Docking station monitor not detected
- `CAND-HARDWARE-002`: Laptop battery not charging
- `CAND-HARDWARE-003`: USB keyboard stops responding
- `CAND-HARDWARE-004`: Storage device not detected

### Network (5 candidates / 1 synthetic case)
Illustrative synthetic case: SYN-IT-0010 · Websites fail by hostname on one PC. No validated case-to-candidate mapping.
- `CAND-NETWORK-001`: DNS lookup fails on one device (type review: symptom_or_diagnostic_finding)
- `CAND-NETWORK-002`: DHCP address missing
- `CAND-NETWORK-003`: Wi-Fi connected without Internet
- `CAND-NETWORK-004`: Gateway unreachable (type review: diagnostic_finding_or_issue_requires_context)
- `CAND-NETWORK-005`: Proxy misconfiguration (type review: possible_cause)

### VPN Remote (4 candidates / 1 synthetic case)
Illustrative synthetic case: SYN-IT-0011 · VPN connects but internal file share is unreachable. No validated case-to-candidate mapping.
- `CAND-VPN-REMOTE-001`: VPN connects but internal share inaccessible (type review: user_visible_symptom)
- `CAND-VPN-REMOTE-002`: VPN MFA authentication fails
- `CAND-VPN-REMOTE-003`: RDP cannot reach permitted host
- `CAND-VPN-REMOTE-004`: Split-tunnel route missing

### Browsers (5 candidates / 1 synthetic case)
Illustrative synthetic case: SYN-IT-0012 · Web portal fails only in Chrome profile. No validated case-to-candidate mapping.
- `CAND-BROWSERS-001`: Chrome extension blocks web portal
- `CAND-BROWSERS-002`: Edge profile sync fails
- `CAND-BROWSERS-003`: Firefox user profile corruption
- `CAND-BROWSERS-004`: Web app certificate warning
- `CAND-BROWSERS-005`: Browser freezes after update

### Printing (4 candidates / 1 synthetic case)
Illustrative synthetic case: SYN-IT-0013 · Printer queue stalls on one workstation. No validated case-to-candidate mapping.
- `CAND-PRINTING-001`: Print queue blocked by stalled job
- `CAND-PRINTING-002`: Printer mapping fails
- `CAND-PRINTING-003`: Printer driver conflict
- `CAND-PRINTING-004`: Printer is offline

### Security Defender (4 candidates / 1 synthetic case)
Illustrative synthetic case: SYN-IT-0014 · Defender alert blocks approved utility. No validated case-to-candidate mapping.
- `CAND-SECURITY-DEFENDER-001`: False-positive malware detection review (type review: investigation_task_or_finding)
- `CAND-SECURITY-DEFENDER-002`: Suspicious login investigation
- `CAND-SECURITY-DEFENDER-003`: Reported phishing email triage
- `CAND-SECURITY-DEFENDER-004`: Endpoint protection not reporting

### Intune (4 candidates / 1 synthetic case)
Illustrative synthetic case: SYN-IT-0015 · Device compliance does not refresh. No validated case-to-candidate mapping.
- `CAND-INTUNE-001`: Compliance policy fails to refresh
- `CAND-INTUNE-002`: Enrollment blocked by device restriction
- `CAND-INTUNE-003`: Required app install remains pending
- `CAND-INTUNE-004`: Configuration profile conflict

### Azure (4 candidates / 1 synthetic case)
Illustrative synthetic case: SYN-IT-0016 · Azure VM operator cannot start a VM. No validated case-to-candidate mapping.
- `CAND-AZURE-001`: Azure VM access denied by role
- `CAND-AZURE-002`: VM private DNS resolution fails
- `CAND-AZURE-003`: Storage account network access blocked
- `CAND-AZURE-004`: Virtual machine unavailable

### Active Directory (4 candidates / 1 synthetic case)
Illustrative synthetic case: SYN-IT-0017 · GPO network drive mapping missing. No validated case-to-candidate mapping.
- `CAND-ACTIVE-DIRECTORY-001`: GPO drive mapping not applied
- `CAND-ACTIVE-DIRECTORY-002`: Domain join fails
- `CAND-ACTIVE-DIRECTORY-003`: Group membership not reflected
- `CAND-ACTIVE-DIRECTORY-004`: Computer account trust relationship fails

### File Storage (4 candidates / 1 synthetic case)
Illustrative synthetic case: SYN-IT-0018 · Network share denies read permission. No validated case-to-candidate mapping.
- `CAND-FILE-STORAGE-001`: Mapped drive permission denied
- `CAND-FILE-STORAGE-002`: File share offline
- `CAND-FILE-STORAGE-003`: Disk volume nearly full
- `CAND-FILE-STORAGE-004`: File locked by another user

### Software (4 candidates / 1 synthetic case)
Illustrative synthetic case: SYN-IT-0019 · Line-of-business app installer fails. No validated case-to-candidate mapping.
- `CAND-SOFTWARE-001`: MSI installation blocked by prerequisite
- `CAND-SOFTWARE-002`: Application crashes on launch
- `CAND-SOFTWARE-003`: Software updater fails
- `CAND-SOFTWARE-004`: Application license not detected

### Certificates (4 candidates / 1 synthetic case)
Illustrative synthetic case: SYN-IT-0020 · Internal HTTPS portal reports expired certificate. No validated case-to-candidate mapping.
- `CAND-CERTIFICATES-001`: Expired TLS certificate warning
- `CAND-CERTIFICATES-002`: Certificate chain not trusted
- `CAND-CERTIFICATES-003`: VPN device certificate missing
- `CAND-CERTIFICATES-004`: Certificate enrollment failure

### VoIP (4 candidates / 1 synthetic case)
Illustrative synthetic case: SYN-IT-0021 · Softphone rings but has no sound. No validated case-to-candidate mapping.
- `CAND-VOIP-001`: Softphone has no audio output
- `CAND-VOIP-002`: VoIP phone fails registration
- `CAND-VOIP-003`: Intermittent call quality
- `CAND-VOIP-004`: USB headset microphone muted

### Backup (4 candidates / 1 synthetic case)
Illustrative synthetic case: SYN-IT-0022 · Scheduled backup reports insufficient capacity. No validated case-to-candidate mapping.
- `CAND-BACKUP-001`: Scheduled backup job fails
- `CAND-BACKUP-002`: Restore job reports missing file
- `CAND-BACKUP-003`: Backup agent is offline
- `CAND-BACKUP-004`: Backup storage capacity exceeded (type review: condition_or_possible_cause)

### MSP Tools (4 candidates / 1 synthetic case)
Illustrative synthetic case: SYN-IT-0023 · RMM agent shows offline while PC is online. No validated case-to-candidate mapping.
- `CAND-MSP-TOOLS-001`: Remote monitoring agent offline
- `CAND-MSP-TOOLS-002`: Remote assistance session blocked
- `CAND-MSP-TOOLS-003`: RMM policy application delayed
- `CAND-MSP-TOOLS-004`: Ticket notification automation not triggered

### Powershell Automation (4 candidates / 1 synthetic case)
Illustrative synthetic case: SYN-IT-0024 · PowerShell cmdlet is not recognized. No validated case-to-candidate mapping.
- `CAND-POWERSHELL-AUTOMATION-001`: PowerShell module missing (type review: possible_cause_or_prerequisite)
- `CAND-POWERSHELL-AUTOMATION-002`: Execution policy prevents local script
- `CAND-POWERSHELL-AUTOMATION-003`: Graph API command returns insufficient privileges
- `CAND-POWERSHELL-AUTOMATION-004`: Scheduled task returns nonzero exit code

## Proposed next data cycle

1. Inspect **real existing** shared Categories/Tags/KB and migrate **no data** during the audit.
2. Classify *each* candidate label into issue/symptom/cause/finding/check/action/other, with an owning domain.
3. Review canonical identity reuse, aliases (equivalence only), topical Tags and scoped Categories separately.
4. For each high-priority symptom, define at least two plausible root-cause branches and one or more **discriminating read-only tests**.
5. Define test outcome semantics, including `not_run`, `unknown`, `inconclusive`, positive, negative, and failure-to-collect.
6. Review hypothesis links, findings and safe remediation separately with provenance; no one-step automatic resolution.
7. Author negative, inconclusive, unresolved, escalated and failed-action synthetic cases to counter success-only bias.
8. Regress prior approved identities and known examples after each vocabulary update. Similarity scores are not diagnostic probabilities.

## Existing architectural authority

- Foundation **0A–0E** stays locked-in; taxonomy meaning is 0C and JSON interoperability is 0B.
- Existing `tags`/`categories` remain authoritative. New source JSON is unapproved intake, not a competing database.
- Domain-owned explicit relationships and service-layer writes only after a separate approval and migration plan.
- Keep the optional offline retrieval/vector index derived and regenerable, never authoritative.

