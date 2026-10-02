# AltF7Hub built-in topic catalog

This catalog documents all 34 built-in IDs. [README.md](README.md) owns technician keyboard use. `TopicRouting.ahk` owns runtime shortcut/color policy; `GuideCore.ahk` owns loading and selection. This Markdown catalog is documentation, never runtime configuration. Aliases and ticket keywords below are reference metadata; no classifier or ticket integration is implemented.

Stable ID is semantic/programmatic identity. Display title, filename, key, cycle position, list position, color and aliases are separate concerns. `LegacyIds()` supplies historical filename/content compatibility only, and must never drive future automation. Topic files or compatible identity sidecars establish the loaded ID; archive/restore writes that ID to paired metadata and may change the filename without changing identity. Editor IDs are immutable; all built-in IDs remain reserved even if their files are missing. Imported duplicate IDs are reported; within each collection the duplicate is rejected, and existing archive precedence across collections is retained.

New user topics require a valid unused ID and may omit shortcuts. They receive a deterministic readable ID-derived fallback color; colors may coincide and never establish identity. Unknown topics do not inherit shortcuts from title or initial filename letter. User shortcuts cannot reuse built-in keys or C/E. Imported accidental key collisions disable that key with a warning; they never extend intentional groups. Built-in routing overrides historical saved shortcut metadata without rewriting sidecars.

## Keyboard, search and archive contract

A: applications → azure-vm. S: sharepoint → phishing. H: hardware → power. W: windows-365 → services → windows. These arrays are explicit runtime policy, independent of filesystem enumeration, Map iteration, alphabetic list sorting and search results. Windows participates only when present in the displayed collection; it is archived by default, so the default active W cycle contains Windows 365 and Services. An absent member is skipped; no members means no action. From outside a group, its first available member is selected; otherwise advance from the currently selected member and wrap. One available member selects itself. Held letter/number repeats are ignored.

Shortcut selection clears search and can reach a filter-excluded member in the current view. Active navigation excludes archived members; in the explicitly selected Archive view only archived members participate, without restoring them. Archive/restore retains ID, effective color and semantic identity. Missing/archived topics must never be silently restored by future automation. Numeric shortcuts are 1 technical, 2 behavioral, 3 STAR, 4 personal and 5 questions; all share #C792EA.

Bare letters/numbers act only with notes or topic list focused and without Ctrl/Alt/Shift/Win. C/E remain create/edit. A is now the Applications/Azure VM group; Script is a button. Search, buttons, sliders, editor fields and dialogs retain native input. Ctrl+F is scoped to the main guide, restores a hidden sidebar, focuses Search and places a collapsed caret at the end of its existing query. Editor/dialog Ctrl+F is unaffected.

The table colors apply to the list label, large title and automatic troubleshooting headings. Explicit personal word formatting still takes precedence, and heading boldness remains a preference. Built-in colors cannot be changed by the shared Heading color preference; that preference remains a fallback when topic color metadata is unavailable. A visual color change does not change the stable ID.

## Future controlled integration (not implemented)

The conceptual flow is ticket subject/context → future controlled classifier or explicit mapping → stable topic ID → separately approved topic-aware request boundary → show/focus the existing shared host → select exact ID → render reference notes → technician remains in control. Preferred semantic intent: “Show AltF7Hub at topic ID”, for example `outlook` or `azure-vm`. No IPC wire format is defined here and the current show/focus protocol is unchanged. A later reviewed slice must design any cross-component extension.

Never simulate A/A or S key presses for programmatic integration. Selection depends on focus, current topic, groups, search and archive state. Automation must target an exact ID rather than title, filename, shortcut count, list order or color.

Future classification should prefer specific validated product evidence: “Outlook cannot send email” → `outlook`; “Teams camera doesn't work” → `teams`; “OneDrive red X on files” → `onedrive-sync`; “Azure VM RDP unavailable” → `azure-vm`. Generic parent topics must not outrank that evidence. “Microsoft application not working” remains ambiguous; do not force it into `applications`. Resolve through explicit administrator/technician mapping, exact product evidence, validated deterministic keyword/context mapping, then technician selection if ambiguity remains. Aliases are hints, never authoritative identity.

A later classifier may consider subject/title, category, subcategory, description, technician tags, product/application fields and error keywords. This slice reads none of those. AI/fuzzy classification, ticket reads, automatic launching/restoring, database/Python changes, keyboard simulation, troubleshooting execution, topic-aware IPC and ticket payloads remain out of scope.

## Complete built-in catalog

Default state below describes the supplied library, not a forced setting. Local archive choices and title edits may differ. Source filenames are compatibility references, not automation targets.

## `accounts`

| Field | Value |
| --- | --- |
| Stable topic ID | `accounts` |
| Display title | ACCOUNT ACCESS / LOCKOUT |
| Category / family | Identity / Access |
| Shortcut key | K |
| Shortcut group | Direct K |
| Deterministic group order | Direct |
| Topic color | #F7DC6F |
| Default state | Active |
| Aliases | account; lockout; password; reset |
| Common ticket-subject keywords | locked account; password expired; cannot sign in |
| Related technologies/products | Windows accounts; directory services |
| Source topic filename | `accounts.txt` |
| Ambiguity notes | Separate account lockout from Microsoft 365 identity or network errors. |
| Collision/group behavior | Unexpected duplicate shortcut disables the key. |
| Automation target | `accounts` |

## `applications`

| Field | Value |
| --- | --- |
| Stable topic ID | `applications` |
| Display title | APPLICATIONS / CRASHES |
| Category / family | Applications |
| Shortcut key | A |
| Shortcut group | A |
| Deterministic group order | 1 of 2 |
| Topic color | #7BC96F |
| Default state | Active |
| Aliases | application; app; software; program |
| Common ticket-subject keywords | application crash; app crash; software crash; program not responding; application error; software will not open |
| Related technologies/products | Desktop applications |
| Source topic filename | `applications.txt` |
| Ambiguity notes | A specific product takes precedence; generic Microsoft application reports remain ambiguous. |
| Collision/group behavior | Only the explicit A membership is intentional; unexpected members disable the key. |
| Automation target | `applications` |

## `azure-vm`

| Field | Value |
| --- | --- |
| Stable topic ID | `azure-vm` |
| Display title | AZURE VM |
| Category / family | Azure / Compute |
| Shortcut key | A |
| Shortcut group | A |
| Deterministic group order | 2 of 2 |
| Topic color | #0089D6 |
| Default state | Active |
| Aliases | Azure VM; Azure virtual machine; Azure server; virtual machine |
| Common ticket-subject keywords | RDP Azure; VM unavailable; VM stopped; boot diagnostics; NSG; Azure RDP |
| Related technologies/products | Microsoft Azure; virtual machines; RDP; SSH |
| Source topic filename | `azure-vm.txt` |
| Ambiguity notes | Require Azure evidence; distinguish Cloud PC, generic VM and VPN connectivity. |
| Collision/group behavior | Only the explicit A membership is intentional; unexpected members disable the key. |
| Automation target | `azure-vm` |

## `customer-communication`

| Field | Value |
| --- | --- |
| Stable topic ID | `customer-communication` |
| Display title | CUSTOMER COMMUNICATION |
| Category / family | Support / Communication |
| Shortcut key | None |
| Shortcut group | None |
| Deterministic group order | None |
| Topic color | #F8B195 |
| Default state | Active |
| Aliases | customer communication; user update; expectation setting |
| Common ticket-subject keywords | status update; customer callback; explain outage |
| Related technologies/products | Help desk; customer support |
| Source topic filename | `customer-communication.txt` |
| Ambiguity notes | Communication requests do not identify the failing technical product. |
| Collision/group behavior | Search/list selection; no shortcut. |
| Automation target | `customer-communication` |

## `dns`

| Field | Value |
| --- | --- |
| Stable topic ID | `dns` |
| Display title | DNS / INTERNET |
| Category / family | Network / Internet |
| Shortcut key | G |
| Shortcut group | Direct G |
| Deterministic group order | Direct |
| Topic color | #4DD0E1 |
| Default state | Active |
| Aliases | internet; DNS; name resolution; gateway; hostname |
| Common ticket-subject keywords | no internet; website unavailable; DNS resolution; cannot browse |
| Related technologies/products | DNS; browsers; TCP/IP |
| Source topic filename | `dns.txt` |
| Ambiguity notes | Separate name resolution from VPN, firewall policy and application outages. |
| Collision/group behavior | Unexpected duplicate shortcut disables the key. |
| Automation target | `dns` |

## `fortigate`

| Field | Value |
| --- | --- |
| Stable topic ID | `fortigate` |
| Display title | FORTINET / FORTIGATE |
| Category / family | Network / Firewall |
| Shortcut key | Y |
| Shortcut group | Direct Y |
| Deterministic group order | Direct |
| Topic color | #EE3124 |
| Default state | Active |
| Aliases | FortiGate; Fortinet; FortiOS; firewall |
| Common ticket-subject keywords | FortiGate firewall; firewall policy; FortiView |
| Related technologies/products | Fortinet FortiGate; FortiOS |
| Source topic filename | `Y.txt` |
| Ambiguity notes | A FortiClient endpoint VPN report belongs to vpn unless appliance evidence points here. |
| Collision/group behavior | Unexpected duplicate shortcut disables the key. |
| Automation target | `fortigate` |

## `hardware`

| Field | Value |
| --- | --- |
| Stable topic ID | `hardware` |
| Display title | HARDWARE / PERIPHERALS |
| Category / family | Devices / Peripherals |
| Shortcut key | H |
| Shortcut group | H |
| Deterministic group order | 1 of 2 |
| Topic color | #FF9F43 |
| Default state | Active |
| Aliases | hardware; peripheral; device; keyboard; mouse; monitor |
| Common ticket-subject keywords | USB device; device not detected; peripheral failure |
| Related technologies/products | Windows devices; USB; displays |
| Source topic filename | `hardware.txt` |
| Ambiguity notes | Teams-specific camera/audio evidence selects teams; startup/display power issues select power. |
| Collision/group behavior | Only the explicit H membership is intentional; unexpected members disable the key. |
| Automation target | `hardware` |

## `identity`

| Field | Value |
| --- | --- |
| Stable topic ID | `identity` |
| Display title | IDENTITY / MICROSOFT 365 |
| Category / family | Microsoft 365 / Identity |
| Shortcut key | I |
| Shortcut group | Direct I |
| Deterministic group order | Direct |
| Topic color | #B39DDB |
| Default state | Active |
| Aliases | identity; Microsoft 365 sign-in; Entra ID; MFA |
| Common ticket-subject keywords | authentication failed; MFA prompt; token; conditional access |
| Related technologies/products | Microsoft Entra ID; Microsoft 365 |
| Source topic filename | `identity.txt` |
| Ambiguity notes | Product-specific errors and ordinary local account lockouts need separate evidence. |
| Collision/group behavior | Unexpected duplicate shortcut disables the key. |
| Automation target | `identity` |

## `interview-behavioral`

| Field | Value |
| --- | --- |
| Stable topic ID | `interview-behavioral` |
| Display title | INTERVIEW / BEHAVIORAL ANSWERS |
| Category / family | Interview preparation |
| Shortcut key | 2 |
| Shortcut group | Direct 2 |
| Deterministic group order | Direct |
| Topic color | #C792EA |
| Default state | Active |
| Aliases | behavioral interview; interview preparation |
| Common ticket-subject keywords | behavioral answer; interview prompt |
| Related technologies/products | Interview practice |
| Source topic filename | `interview-behavioral.txt` |
| Ambiguity notes | Personal preparation reference; do not infer a technical ticket topic or invent achievements. |
| Collision/group behavior | Unexpected duplicate shortcut disables the key. |
| Automation target | `interview-behavioral` |

## `interview-personal`

| Field | Value |
| --- | --- |
| Stable topic ID | `interview-personal` |
| Display title | INTERVIEW / PERSONAL MOTIVATION |
| Category / family | Interview preparation |
| Shortcut key | 4 |
| Shortcut group | Direct 4 |
| Deterministic group order | Direct |
| Topic color | #C792EA |
| Default state | Active |
| Aliases | personal interview; interview preparation |
| Common ticket-subject keywords | personal answer; interview prompt |
| Related technologies/products | Interview practice |
| Source topic filename | `Z.txt` |
| Ambiguity notes | Personal preparation reference; do not infer a technical ticket topic or invent achievements. |
| Collision/group behavior | Unexpected duplicate shortcut disables the key. |
| Automation target | `interview-personal` |

## `interview-questions`

| Field | Value |
| --- | --- |
| Stable topic ID | `interview-questions` |
| Display title | INTERVIEW / QUESTIONS TO ASK |
| Category / family | Interview preparation |
| Shortcut key | 5 |
| Shortcut group | Direct 5 |
| Deterministic group order | Direct |
| Topic color | #C792EA |
| Default state | Active |
| Aliases | questions interview; interview preparation |
| Common ticket-subject keywords | questions answer; interview prompt |
| Related technologies/products | Interview practice |
| Source topic filename | `Q.txt` |
| Ambiguity notes | Personal preparation reference; do not infer a technical ticket topic or invent achievements. |
| Collision/group behavior | Unexpected duplicate shortcut disables the key. |
| Automation target | `interview-questions` |

## `interview-star`

| Field | Value |
| --- | --- |
| Stable topic ID | `interview-star` |
| Display title | INTERVIEW / STAR STORY PROMPTS |
| Category / family | Interview preparation |
| Shortcut key | 3 |
| Shortcut group | Direct 3 |
| Deterministic group order | Direct |
| Topic color | #C792EA |
| Default state | Active |
| Aliases | star interview; interview preparation |
| Common ticket-subject keywords | star answer; interview prompt |
| Related technologies/products | Interview practice |
| Source topic filename | `interview-star.txt` |
| Ambiguity notes | Personal preparation reference; do not infer a technical ticket topic or invent achievements. |
| Collision/group behavior | Unexpected duplicate shortcut disables the key. |
| Automation target | `interview-star` |

## `interview-technical`

| Field | Value |
| --- | --- |
| Stable topic ID | `interview-technical` |
| Display title | INTERVIEW / TECHNICAL ANSWERS |
| Category / family | Interview preparation |
| Shortcut key | 1 |
| Shortcut group | Direct 1 |
| Deterministic group order | Direct |
| Topic color | #C792EA |
| Default state | Active |
| Aliases | technical interview; interview preparation |
| Common ticket-subject keywords | technical answer; interview prompt |
| Related technologies/products | Interview practice |
| Source topic filename | `interview-technical.txt` |
| Ambiguity notes | Personal preparation reference; do not infer a technical ticket topic or invent achievements. |
| Collision/group behavior | Unexpected duplicate shortcut disables the key. |
| Automation target | `interview-technical` |

## `linux`

| Field | Value |
| --- | --- |
| Stable topic ID | `linux` |
| Display title | LINUX |
| Category / family | Operating systems / Linux |
| Shortcut key | B |
| Shortcut group | Direct B |
| Deterministic group order | Direct |
| Topic color | #FCC624 |
| Default state | Active |
| Aliases | Linux; Ubuntu; Debian; Red Hat; RHEL |
| Common ticket-subject keywords | SSH; systemctl; Linux server |
| Related technologies/products | Linux; SSH; systemd |
| Source topic filename | `linux.txt` |
| Ambiguity notes | SSH alone does not establish Linux; identify the platform. |
| Collision/group behavior | Unexpected duplicate shortcut disables the key. |
| Automation target | `linux` |

## `macos`

| Field | Value |
| --- | --- |
| Stable topic ID | `macos` |
| Display title | MACOS |
| Category / family | Operating systems / Apple |
| Shortcut key | U |
| Shortcut group | Direct U |
| Deterministic group order | Direct |
| Topic color | #B0BEC5 |
| Default state | Active |
| Aliases | Mac; macOS; MacBook; MacBook Pro; MacBook Air; iMac; Apple computer; Apple Silicon |
| Common ticket-subject keywords | Mac sign-in; macOS application; Mac storage |
| Related technologies/products | Apple macOS; Mac hardware |
| Source topic filename | `macos.txt` |
| Ambiguity notes | Identify Apple platform; distinguish hardware symptoms from macOS software behavior. |
| Collision/group behavior | Unexpected duplicate shortcut disables the key. |
| Automation target | `macos` |

## `mapped-drives`

| Field | Value |
| --- | --- |
| Stable topic ID | `mapped-drives` |
| Display title | MAPPED DRIVES / SMB |
| Category / family | Network / File shares |
| Shortcut key | X |
| Shortcut group | Direct X |
| Deterministic group order | Direct |
| Topic color | #81D4FA |
| Default state | Active |
| Aliases | mapped drive; SMB; file share; network drive |
| Common ticket-subject keywords | drive disconnected; share unavailable; UNC path |
| Related technologies/products | SMB; Windows file shares |
| Source topic filename | `mapped-drives.txt` |
| Ambiguity notes | Distinguish SharePoint/OneDrive cloud libraries from SMB shares. |
| Collision/group behavior | Unexpected duplicate shortcut disables the key. |
| Automation target | `mapped-drives` |

## `methodology`

| Field | Value |
| --- | --- |
| Stable topic ID | `methodology` |
| Display title | TROUBLESHOOTING METHODOLOGY |
| Category / family | Support / Troubleshooting |
| Shortcut key | M |
| Shortcut group | Direct M |
| Deterministic group order | Direct |
| Topic color | #6BCB77 |
| Default state | Active |
| Aliases | troubleshooting; diagnostic method; problem isolation |
| Common ticket-subject keywords | scope issue; reproduce error; known-good comparison |
| Related technologies/products | Help desk diagnostics |
| Source topic filename | `methodology.txt` |
| Ambiguity notes | General workflow reference; specific product evidence takes precedence. |
| Collision/group behavior | Unexpected duplicate shortcut disables the key. |
| Automation target | `methodology` |

## `network`

| Field | Value |
| --- | --- |
| Stable topic ID | `network` |
| Display title | NETWORK |
| Category / family | Network / Connectivity |
| Shortcut key | N |
| Shortcut group | Direct N |
| Deterministic group order | Direct |
| Topic color | #45B7D1 |
| Default state | Active |
| Aliases | network; Ethernet; Wi-Fi; connectivity |
| Common ticket-subject keywords | packet loss; network outage; adapter; DHCP |
| Related technologies/products | TCP/IP; Ethernet; Wi-Fi |
| Source topic filename | `network.txt` |
| Ambiguity notes | Identify DNS, VPN or firewall-specific evidence before choosing a general network topic. |
| Collision/group behavior | Unexpected duplicate shortcut disables the key. |
| Automation target | `network` |

## `onedrive-sync`

| Field | Value |
| --- | --- |
| Stable topic ID | `onedrive-sync` |
| Display title | ONEDRIVE SYNC |
| Category / family | Microsoft 365 / Storage |
| Shortcut key | D |
| Shortcut group | Direct D |
| Deterministic group order | Direct |
| Topic color | #0078D4 |
| Default state | Active |
| Aliases | OneDrive; sync; syncing; cloud files |
| Common ticket-subject keywords | red X; pending sync; Files On-Demand; OneDrive sign-in; file conflict |
| Related technologies/products | Microsoft OneDrive; Microsoft 365 |
| Source topic filename | `onedrive-sync.txt` |
| Ambiguity notes | Generic sync does not establish OneDrive; distinguish SharePoint permissions and library access. |
| Collision/group behavior | Unexpected duplicate shortcut disables the key. |
| Automation target | `onedrive-sync` |

## `outlook`

| Field | Value |
| --- | --- |
| Stable topic ID | `outlook` |
| Display title | OUTLOOK / EMAIL |
| Category / family | Microsoft 365 / Messaging |
| Shortcut key | O |
| Shortcut group | Direct O |
| Deterministic group order | Direct |
| Topic color | #2B88D8 |
| Default state | Active |
| Aliases | Outlook; email; mail; mailbox; Exchange; OWA |
| Common ticket-subject keywords | send email; receive email; outbox; NDR; OST; Outlook profile; disconnected; Work Offline; cannot send email; cannot receive email; mailbox full; Outlook disconnected |
| Related technologies/products | Microsoft Outlook; Exchange Online; Microsoft 365; Outlook on the web |
| Source topic filename | `outlook.txt` |
| Ambiguity notes | Generic Microsoft application reports need Outlook/mail-specific evidence; suspicious email may instead require phishing triage. |
| Collision/group behavior | Unexpected duplicate shortcut disables the key. |
| Automation target | `outlook` |

## `performance`

| Field | Value |
| --- | --- |
| Stable topic ID | `performance` |
| Display title | PERFORMANCE / DISK SPACE |
| Category / family | Devices / Performance |
| Shortcut key | L |
| Shortcut group | Direct L |
| Deterministic group order | Direct |
| Topic color | #FFD93D |
| Default state | Active |
| Aliases | performance; slow computer; disk space; storage |
| Common ticket-subject keywords | low disk space; high CPU; high memory; slow startup |
| Related technologies/products | Windows; storage; Task Manager |
| Source topic filename | `performance.txt` |
| Ambiguity notes | Separate resource symptoms from a named application failure. |
| Collision/group behavior | Unexpected duplicate shortcut disables the key. |
| Automation target | `performance` |

## `phishing`

| Field | Value |
| --- | --- |
| Stable topic ID | `phishing` |
| Display title | PHISHING / SECURITY TRIAGE |
| Category / family | Security / Incident triage |
| Shortcut key | S |
| Shortcut group | S |
| Deterministic group order | 2 of 2 |
| Topic color | #FF5A5F |
| Default state | Active |
| Aliases | phishing; suspicious email; malicious email; security incident |
| Common ticket-subject keywords | compromised account; suspicious link; credential phishing; user clicked link; suspicious attachment |
| Related technologies/products | Email security; identity security |
| Source topic filename | `phishing.txt` |
| Ambiguity notes | Email delivery faults select outlook; suspicious content needs security evidence and technician control. |
| Collision/group behavior | Only the explicit S membership is intentional; unexpected members disable the key. |
| Automation target | `phishing` |

## `placeholder-active`

| Field | Value |
| --- | --- |
| Stable topic ID | `placeholder-active` |
| Display title | XXX |
| Category / family | Compatibility / Placeholder |
| Shortcut key | None |
| Shortcut group | None |
| Deterministic group order | None |
| Topic color | #90A4AE |
| Default state | Archived |
| Aliases | legacy placeholder; XXX |
| Common ticket-subject keywords | placeholder notes |
| Related technologies/products | Historical guide compatibility |
| Source topic filename | `Archive/placeholder-active.txt` |
| Ambiguity notes | No technical classification meaning; never automatically select from XXX or generic text. |
| Collision/group behavior | Search/list selection; no shortcut. |
| Automation target | `placeholder-active` |

## `placeholder-archived`

| Field | Value |
| --- | --- |
| Stable topic ID | `placeholder-archived` |
| Display title | XXX |
| Category / family | Compatibility / Placeholder |
| Shortcut key | None |
| Shortcut group | None |
| Deterministic group order | None |
| Topic color | #78909C |
| Default state | Archived |
| Aliases | legacy placeholder; XXX |
| Common ticket-subject keywords | placeholder notes |
| Related technologies/products | Historical guide compatibility |
| Source topic filename | `Archive/X.txt` |
| Ambiguity notes | No technical classification meaning; never automatically select from XXX or generic text. |
| Collision/group behavior | Search/list selection; no shortcut. |
| Automation target | `placeholder-archived` |

## `power`

| Field | Value |
| --- | --- |
| Stable topic ID | `power` |
| Display title | POWER / STARTUP / DISPLAY |
| Category / family | Devices / Startup and display |
| Shortcut key | H |
| Shortcut group | H |
| Deterministic group order | 2 of 2 |
| Topic color | #FF9F43 |
| Default state | Active |
| Aliases | power; startup; display; boot |
| Common ticket-subject keywords | no power; black screen; will not start; no display |
| Related technologies/products | Windows startup; displays; hardware |
| Source topic filename | `P.txt` |
| Ambiguity notes | Distinguish USB/peripheral faults from startup/power/display symptoms. |
| Collision/group behavior | Only the explicit H membership is intentional; unexpected members disable the key. |
| Automation target | `power` |

## `printing`

| Field | Value |
| --- | --- |
| Stable topic ID | `printing` |
| Display title | PRINTING |
| Category / family | Devices / Printing |
| Shortcut key | R |
| Shortcut group | Direct R |
| Deterministic group order | Direct |
| Topic color | #A8DADC |
| Default state | Active |
| Aliases | printer; printing; spooler; print queue; print server; toner |
| Common ticket-subject keywords | stuck print job; cannot print |
| Related technologies/products | Windows printing; printers |
| Source topic filename | `printing.txt` |
| Ambiguity notes | Distinguish document/application problems from print-system faults. |
| Collision/group behavior | Unexpected duplicate shortcut disables the key. |
| Automation target | `printing` |

## `prioritization`

| Field | Value |
| --- | --- |
| Stable topic ID | `prioritization` |
| Display title | PRIORITIZATION / ESCALATION |
| Category / family | Support / Escalation |
| Shortcut key | None |
| Shortcut group | None |
| Deterministic group order | None |
| Topic color | #FFB4A2 |
| Default state | Active |
| Aliases | priority; prioritization; escalation; impact; urgency |
| Common ticket-subject keywords | major incident; escalate ticket; service impact |
| Related technologies/products | Help desk; incident management |
| Source topic filename | `prioritization.txt` |
| Ambiguity notes | Process metadata does not itself classify a technical product. |
| Collision/group behavior | Search/list selection; no shortcut. |
| Automation target | `prioritization` |

## `services`

| Field | Value |
| --- | --- |
| Stable topic ID | `services` |
| Display title | WINDOWS SERVICES |
| Category / family | Windows / Services |
| Shortcut key | W |
| Shortcut group | W |
| Deterministic group order | 2 of 3 |
| Topic color | #00A4EF |
| Default state | Active |
| Aliases | Windows service; service control; service manager |
| Common ticket-subject keywords | service stopped; service will not start; dependency failure; services.msc |
| Related technologies/products | Windows Service Control Manager |
| Source topic filename | `services.txt` |
| Ambiguity notes | A cloud service or generic service outage does not establish a Windows service issue. |
| Collision/group behavior | Only the explicit W membership is intentional; unexpected members disable the key. |
| Automation target | `services` |

## `sharepoint`

| Field | Value |
| --- | --- |
| Stable topic ID | `sharepoint` |
| Display title | SHAREPOINT / FILE ACCESS |
| Category / family | Microsoft 365 / Collaboration |
| Shortcut key | S |
| Shortcut group | S |
| Deterministic group order | 1 of 2 |
| Topic color | #1AA3A3 |
| Default state | Active |
| Aliases | SharePoint; SharePoint Online; document library |
| Common ticket-subject keywords | site access; file access; sharing link; library permissions; SharePoint file |
| Related technologies/products | Microsoft SharePoint Online; Microsoft 365 |
| Source topic filename | `sharepoint.txt` |
| Ambiguity notes | OneDrive sync-specific evidence selects onedrive-sync; SMB shares select mapped-drives. |
| Collision/group behavior | Only the explicit S membership is intentional; unexpected members disable the key. |
| Automation target | `sharepoint` |

## `teams`

| Field | Value |
| --- | --- |
| Stable topic ID | `teams` |
| Display title | TEAMS / AUDIO / VIDEO |
| Category / family | Microsoft 365 / Meetings |
| Shortcut key | T |
| Shortcut group | Direct T |
| Deterministic group order | Direct |
| Topic color | #6264A7 |
| Default state | Active |
| Aliases | Teams; Microsoft Teams; meeting; headset; speaker |
| Common ticket-subject keywords | microphone; camera; audio; video; Teams call |
| Related technologies/products | Microsoft Teams; cameras; audio devices |
| Source topic filename | `teams.txt` |
| Ambiguity notes | Teams-specific camera/audio evidence selects teams; generic hardware reports need device context. |
| Collision/group behavior | Unexpected duplicate shortcut disables the key. |
| Automation target | `teams` |

## `ticketing`

| Field | Value |
| --- | --- |
| Stable topic ID | `ticketing` |
| Display title | TICKETING / DOCUMENTATION |
| Category / family | Support / Documentation |
| Shortcut key | None |
| Shortcut group | None |
| Deterministic group order | None |
| Topic color | #80CBC4 |
| Default state | Active |
| Aliases | ticket; ticketing; incident record; documentation |
| Common ticket-subject keywords | ticket notes; document resolution; handoff |
| Related technologies/products | Help desk; ticket systems |
| Source topic filename | `ticketing.txt` |
| Ambiguity notes | This guide topic provides reference notes and does not read F7Hub ticket data. |
| Collision/group behavior | Search/list selection; no shortcut. |
| Automation target | `ticketing` |

## `vpn`

| Field | Value |
| --- | --- |
| Stable topic ID | `vpn` |
| Display title | VPN |
| Category / family | Network / Remote access |
| Shortcut key | V |
| Shortcut group | Direct V |
| Deterministic group order | Direct |
| Topic color | #26A69A |
| Default state | Active |
| Aliases | VPN; tunnel; remote access; FortiClient VPN |
| Common ticket-subject keywords | VPN connection failed; VPN disconnected; internal resource through VPN |
| Related technologies/products | VPN clients; FortiClient; remote networks |
| Source topic filename | `vpn.txt` |
| Ambiguity notes | Distinguish endpoint tunnel failure from FortiGate appliance policy and Azure VM connectivity. |
| Collision/group behavior | Unexpected duplicate shortcut disables the key. |
| Automation target | `vpn` |

## `windows`

| Field | Value |
| --- | --- |
| Stable topic ID | `windows` |
| Display title | WINDOWS |
| Category / family | Operating systems / Windows |
| Shortcut key | W |
| Shortcut group | W |
| Deterministic group order | 3 of 3 |
| Topic color | #00A4EF |
| Default state | Archived |
| Aliases | Windows; operating system; Windows desktop |
| Common ticket-subject keywords | Windows update; OS error; desktop problem |
| Related technologies/products | Microsoft Windows |
| Source topic filename | `Archive/W.txt` |
| Ambiguity notes | Archived by default; distinguish Cloud PC, Windows services and product-specific faults. |
| Collision/group behavior | Only the explicit W membership is intentional; unexpected members disable the key. |
| Automation target | `windows` |

## `windows-365`

| Field | Value |
| --- | --- |
| Stable topic ID | `windows-365` |
| Display title | WINDOWS 365 / CLOUD PC |
| Category / family | Microsoft cloud / Cloud PC |
| Shortcut key | W |
| Shortcut group | W |
| Deterministic group order | 1 of 3 |
| Topic color | #00A4EF |
| Default state | Active |
| Aliases | Windows 365; Cloud PC; cloud desktop; Windows 365 app |
| Common ticket-subject keywords | Cloud PC unavailable; Cloud PC provisioning; Windows 365 connection |
| Related technologies/products | Microsoft Windows 365; Cloud PC |
| Source topic filename | `windows-365.txt` |
| Ambiguity notes | Require Windows 365 evidence; distinguish Azure VM, local Windows and generic VPN problems. |
| Collision/group behavior | Only the explicit W membership is intentional; unexpected members disable the key. |
| Automation target | `windows-365` |
