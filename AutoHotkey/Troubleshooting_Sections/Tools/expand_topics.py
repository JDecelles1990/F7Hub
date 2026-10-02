"""Append keyword-only depth cues once; preserve existing text and matching styles.

Maintenance utility, not an application dependency. Run from the guide folder.
"""
from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parent.parent
EXTRA = {
    "methodology.txt": """INTAKE — caller identity · contact · asset · location · ticket
IMPACT — blocked task · affected users · critical function · workaround
BASELINE — normal behavior · frequency · duration · last success
CHANGE HISTORY — updates · moves · permissions · hardware · policy
ERROR CAPTURE — verbatim text · code · screen · timestamp · time zone
DEPENDENCY MAP — client · identity · DNS · transport · service · data
REPRODUCTION — smallest input · original context · consistent sequence
COMPARISON MATRIX — same user / other device · other user / same device
LAYER ISOLATION — local / remote · application / OS · site / tenant
HYPOTHESIS — supporting evidence · counterexample · discriminating test
TEST ORDER — observation · reversible comparison · targeted remediation
ONE CHANGE — single variable · baseline · measurable result
INTERMITTENT — frequency · workload · network · environmental pattern
TIMELINE CORRELATION — logs · service events · updates · error onset
NEGATIVE RESULTS — excluded layers · remaining hypotheses · next test
KNOWLEDGE — approved article · vendor documentation · known incident
ACCESS BOUNDARY — help desk authority · service owner · change approval
DATA PROTECTION — unsaved work · synchronization · backup · recovery
ROLLBACK PLAN — original setting · recovery route · validation criteria
WORKAROUND — continuity · limitations · duration · owner
ESCALATION TRIGGER — SLA risk · security event · shared infrastructure
HANDOFF PACKAGE — scope · timeline · errors · tests · results · logs
ROOT CAUSE — confirmed evidence · contributing factors · uncertainty
CLOSURE — user validation · ticket completeness · prevention · follow-up""",
    "outlook.txt": """CLIENT IDENTITY — classic Outlook · new Outlook · web · exact build
ACCOUNT CONTEXT — work / school · personal · shared mailbox · delegate
SCOPE MATRIX — self / internal / external · recipient / all · device / all
WEB CONTROL — same account · same recipient · same message · private browser
TRANSPORT STATE — Connected · Disconnected · Work Offline · Need Password
OUTBOX CONTROL — stuck message · offline move to Drafts · new minimal message
RECIPIENT CONTROL — typed SMTP · AutoComplete bypass · group restrictions
NDR EVIDENCE — complete 4.x.x / 5.x.x · diagnostic text · generating server
TRACE CONTEXT — sender · recipient · Message-ID · time zone · reporting delay
TRACE INTERPRETATION — submitted · deferred · delivered · failed · recipient-side location
HEADERS — Received chain · Message-ID · duplicate submission · transport delay
MAILBOX HEALTH — provisioning · service plan · quota · send restriction
DELEGATION — Full Access · Send As · Send on Behalf · propagation
GROUP DELIVERY — sender restrictions · moderation · membership · external policy
MESSAGE CONTENT — size · MIME overhead · signature · sensitivity label
PROTECTION — quarantine · anti-spam · anti-phishing · DLP · encryption
ROUTING — transport rule · connector · accepted domain · mail-flow owner
CLIENT ISOLATION — add-ins · integrations · profile · known-good user
CLASSIC TOOLS — outlook.exe /safe · COM add-ins · new profile · indexing
CLASSIC CACHE — OST · cache range · Exchange confirmation · local-only data
NEW OUTLOOK — web comparison · account state · app update / repair
SEARCH — web result · folder scope · cache duration · indexing
CALENDAR — web permissions · delegate rights · direct / group Full Access
IDENTITY DETAIL — token prompts · sign-ins · MFA · compliance · policy
CONNECTIVITY DETAIL — outlook.office.com · DNS · TCP 443 · proxy · TLS inspection
REPAIR ORDER — approved update · Quick Repair · Online Repair · rollback
VALIDATION MATRIX — original send · delivery · replies · attachment · delegation""",
    "P.txt": """POWER CLASSIFICATION — no LEDs / fans · powered / blank screen · POST / boot
POWER SOURCE — known-good outlet · power-strip bypass · UPS status
CABLE PATH — wall / adapter · adapter / device · both ends · damage
DESKTOP PSU — I / O switch · external indicators · no PSU opening
LAPTOP ADAPTER — OEM compatibility · rated wattage · charging LED
USB-C POWER — charging port · PD support · cable capability · dock supply
BATTERY STATE — charge indication · removable battery · vendor reset
DOCK ISOLATION — direct charger · direct monitor · known-good cable
PERIPHERAL ISOLATION — storage · USB hub · webcam · printer · network
POWER BUTTON — response · stuck button · indicators · timing
POST EVIDENCE — beep count · LED pattern · vendor diagnostics
DISPLAY PATH — correct GPU output · monitor source · cable standard
MONITOR CONTROL — on-screen menu · known-good cable · known-good monitor
LAPTOP SCREEN — brightness · external display · lid / dock state
BOOT TRANSITION — vendor logo · firmware · disk detection · boot device
RECOVERY BOUNDARY — BitLocker key source · data protection · authorization
ENVIRONMENT — heat · liquid · surge · physical damage · transport
SAFETY TRIGGER — smoke · smell · swelling · sparks · excessive heat
HARDWARE ACCESS — warranty · trained technician · electrostatic precautions
SERVICE HANDOFF — asset · model · charger · diagnostic code · comparisons
FINAL CONTROL — stable power · display · boot · peripheral reconnection""",
    "onedrive-sync.txt": """ACCOUNT SPLIT — Personal · Work / School · tenant · sign-in address
PATH MAP — local root · cloud location · SharePoint library · shortcut
SYNC DIRECTION — upload · download · both · one file · all files
STATUS DETAIL — processing · pending · paused · signing in · sync error
WEB BASELINE — tenant · latest item · test upload · test download
FILE LOCKS — open app · coauthoring · checkout · stale lock
FILE VALIDITY — characters · reserved names · long path · file size
CAPACITY — cloud quota · local space · Files On-Demand state
ACCESS DETAIL — file permissions · library membership · sharing changes
CONFLICT DETAIL — duplicate names · conflicted copies · version history
LOCAL DATA — unsynced changes · local-only files · protected backup
LIBRARY DETAIL — folder selection · sync relationship · shortcut overlap
FOLDER BACKUP — Desktop · Documents · Pictures · redirection · policy
NETWORK DETAIL — proxy · TLS inspection · VPN · required endpoints
SECURITY DETAIL — ransomware indicators · mass deletion · escalation
CLIENT DETAIL — version · accounts · startup · authentication prompts
ISOLATION MATRIX — item / other item · web / local · known-good device
TEST FILE — small neutral file · noncritical folder · timestamps
SERVICE COMPARISON — tenant health · SharePoint · account health
RESET BOUNDARY — unsynced-file backup · cloud confirmation · approved reset
RELINK BOUNDARY — correct account · correct root · duplicate-folder avoidance
RESTORE BOUNDARY — recycle bin · version history · retention owner
FINAL CHECK — upload / download · latest content · path · conflicts""",
    "phishing.txt": """MESSAGE ORIGIN — display name · actual address · reply-to · domain
AUTHENTICATION — SPF · DKIM · DMARC · header evidence
LINK REVIEW — visible text · target domain · lookalike · approved analysis
ATTACHMENT REVIEW — type · unexpected archive · macro request · verdict
SOCIAL ENGINEERING — urgency · authority · secrecy · payment change
USER TIMELINE — receipt · open · click · download · credential submission
CREDENTIAL EXPOSURE — password · MFA approval · session token · accounts
DEVICE EXPOSURE — executed file · download · endpoint alert
MAILBOX EVIDENCE — original email · headers · Message-ID · recipients
ACCOUNT EVIDENCE — sign-in location · device · time · unfamiliar activity
PERSISTENCE REVIEW — forwarding · inbox rules · delegated access
SCOPE REVIEW — related messages · recipients · shared mailbox
CONTAINMENT OWNER — security operations · incident lead · approved procedure
ACCOUNT CONTAINMENT — authorized session revocation · credentials · MFA
DEVICE CONTAINMENT — authorized isolation · endpoint tooling · evidence
EMAIL CONTAINMENT — reporting · quarantine · mail security owner
FINANCIAL REQUEST — independently verified contact · approved process
HANDLING LIMITS — no live links · no attachment execution · evidence retention
REPORT PACKAGE — action timeline · indicators · user · device · logs
COMMUNICATION — neutral facts · reassurance · security updates
FOLLOW-UP — recovery · security clearance · awareness reminders""",
    "identity.txt": """IDENTITY MAP — UPN · email alias · tenant · domain · guest / member
AUTHORITY MAP — cloud-only · AD-synced · federated · managed domain
SIGN-IN CONTEXT — application · browser · device · network
ERROR EVIDENCE — full code · correlation ID · timestamp · request
SIGN-IN LOGS — failure reason · resource · policy evaluation
ACCOUNT DETAIL — enabled · locked · expired · deleted · risky
LICENSE DETAIL — assignment · service plan · provisioning · group delay
AUTHENTICATION DETAIL — password · MFA · passwordless · federation
MFA DETAIL — method · registered device · notification · time
MFA BOUNDARY — verified identity · approved reset · no bypass
POLICY DETAIL — Conditional Access · location · compliance · session
DEVICE DETAIL — registration · join type · primary user · compliance
TOKEN DETAIL — prompts · private browser · mismatch · cached session
HYBRID DETAIL — reset authority · password synchronization · replication
DOMAIN DETAIL — DNS · time skew · controller reachability
KERBEROS DETAIL — tickets · service access · SPN · identity owner
ACCESS DETAIL — membership · role · resource permission · propagation
GUEST DETAIL — home / resource tenant · invitation · account selection
SERVICE DETAIL — tenant health · application · federation availability
ISOLATION MATRIX — user / alternate device · alternate user / device
RECOVERY ORDER — identity verification · targeted correction · validation
ESCALATION PACKAGE — sign-in event · policy result · join state · scope
FINAL CHECK — authentication · target resource · MFA · confirmation""",
    "Archive/W.txt": """BOOT STAGE — firmware · POST · boot loader · Windows · sign-in
RECENT CHANGE — update · driver · firmware · hardware · power loss
RECOVERY ENVIRONMENT — authorized WinRE · startup repair · restore
BITLOCKER DETAIL — asset match · recovery key ID · authorized source
DISK VISIBILITY — firmware detection · controller · diagnostics
PROFILE DETAIL — temporary profile · profile events · disk · permissions
KNOWN-GOOD PROFILE — app behavior · per-user configuration · policy
UPDATE DETAIL — KB · hexadecimal error · servicing · pending restart
UPDATE LOGS — Event Viewer · CBS.log · DISM.log · update evidence
UPDATE ENVIRONMENT — space · proxy · metered network · management policy
INTEGRITY TOOLS — approved DISM · SFC · results · reboot requirement
DRIVER DETAIL — hardware ID · version · recent update · rollback
CRASH DETAIL — stop code · dump · module · Reliability Monitor
CRASH PATTERN — load · sleep / wake · heat · device · frequency
PERFORMANCE DETAIL — CPU · memory pressure · disk latency · startup
STORAGE DETAIL — free space · vendor diagnostics · I/O events
TIME DETAIL — time zone · clock skew · domain time source
DOMAIN DETAIL — IP · DNS · VPN · trust · authentication
POLICY DETAIL — Group Policy · MDM · compliance · owner
TOOLS — msinfo32 · Event Viewer · Reliability Monitor · Device Manager
RECOVERY ORDER — backup · recovery key · authorization · rollback
ESCALATION PACKAGE — build · asset · error · logs · dump · test matrix
FINAL CHECK — restart · sign-in · original workflow · stability""",
    "network.txt": """LAYER ORDER — physical · link · IP · routing · DNS · transport · application
ADAPTER DETAIL — enabled · driver · speed · error counters
WIRED DETAIL — port · cable · VLAN · duplex · switch owner
WIRELESS DETAIL — SSID · band · signal · roaming · channel contention
ADDRESS DETAIL — subnet · APIPA · DHCP lease · duplicate address
DHCP DETAIL — lease · scope · reservation · relay · server owner
GATEWAY DETAIL — reachability · ARP / neighbor · route · VLAN
ROUTE DETAIL — default / specific route · VPN route · metric
DNS DETAIL — resolver · suffix · internal / external · IPv4 / IPv6
TRANSPORT DETAIL — required port · listener · firewall · timeout / refusal
APPLICATION DETAIL — endpoint · TLS · authentication · proxy
COMPARISON MATRIX — site / other site · wired / wireless · device / user
PATH TOOLS — ipconfig /all · route print · arp -a · tracert
PORT TOOLS — Test-NetConnection · listener · destination service
DNS TOOLS — Resolve-DnsName · nslookup · resolver comparison
QUALITY METRICS — latency · loss · jitter · utilization · retransmissions
INTERMITTENT — time · location · roaming · VPN · peak load
PROXY DETAIL — system / browser · PAC · authentication · bypass policy
TLS DETAIL — chain · hostname · clock · inspection
CAPTURE BOUNDARY — authorization · targeted filter · privacy · owner
SHARED INFRASTRUCTURE — switch · router · firewall · ISP · service owner
CHANGE BOUNDARY — approval · baseline · rollback
FINAL MATRIX — IP · name · port · app · original workflow""",
    "sharepoint.txt": """RESOURCE MAP — tenant · site URL · library · folder · file
ACCOUNT MAP — member · guest · organization · browser session
ACCESS MATRIX — site / library / item · web / sync · user / group
PERMISSION DETAIL — inheritance · unique rights · membership
SHARING DETAIL — link scope · expiration · guest restriction · owner
MEMBERSHIP DETAIL — M365 group · SharePoint group · propagation
FILE DETAIL — lock · checkout · coauthoring · sensitivity label
VERSION DETAIL — modification · history · author · conflict
LIBRARY DETAIL — metadata · required columns · content type · approval
SYNC DETAIL — account · folders · shortcut overlap
PATH DETAIL — item name · length · invalid characters
DATA LOSS DETAIL — deletion time · recycle bins · retention · restore owner
MASS CHANGE — unexpected deletes · propagation · security escalation
FOLDER LOCATION — redirection · local-only copies · correct library
POLICY DETAIL — Conditional Access · device restriction · sharing
SERVICE DETAIL — tenant health · site availability · storage quota
ISOLATION MATRIX — fresh browser · second item · known-good user / device
EVIDENCE PACKAGE — URL · exact error · request time · correlation ID
RECOVERY ORDER — backup · version / recycle-bin review · approved restore
FINAL CHECK — web · synchronization · edit / save · sharing""",
    "performance.txt": """ONSET DETAIL — sudden / gradual · update · uptime · workload
MEASUREMENT WINDOW — idle baseline · active workload · sustained use
CPU DETAIL — top process · service host · updates · security scan
MEMORY DETAIL — committed memory · paging · tabs · application leak
DISK DETAIL — active time · latency · queue · top I/O process
CAPACITY DETAIL — system volume · profile · temporary data · cloud cache
STORAGE HEALTH — I/O errors · diagnostics · disk type · failure signs
STARTUP DETAIL — approved startup list · login duration · management agents
PROFILE DETAIL — known-good user · redirected folders · sync backlog
BROWSER DETAIL — extensions · tabs · profile · hardware acceleration
THERMAL DETAIL — temperature · fan · vents · power · throttling
POWER DETAIL — charger wattage · dock · battery saver · OEM profile
NETWORK DETAIL — local / remote task · backend response · VPN
INDEXING DETAIL — search index · large changes · workload timing
SECURITY DETAIL — scan schedule · detections · endpoint health
TOOLS — Task Manager · Resource Monitor · Performance Monitor
CLEANUP BOUNDARY — approved tools · retention · user confirmation
CACHE BOUNDARY — application cache · unsynced work · backup
HARDWARE BOUNDARY — diagnostics · warranty · authorized upgrade
CHANGE CONTROL — one adjustment · before / after timing · rollback
FINAL CHECK — repeat workload · response time · baseline · recurrence""",
    "dns.txt": """CLIENT CONFIG — resolvers · DHCP source · interface order
QUERY MATRIX — short name · FQDN · IP · same resolver
RECORD DETAIL — A · AAAA · CNAME · SRV · PTR · expected value
ANSWER DETAIL — authoritative / cached · TTL · NXDOMAIN · SERVFAIL · timeout
SERVER COMPARISON — configured resolver · authorized alternate
CACHE DETAIL — client · negative cache · server · TTL
LOCAL OVERRIDES — hosts file · suffix search · application cache
DOMAIN DETAIL — AD DNS · SRV records · controller discovery
VPN DETAIL — split DNS · NRPT · pushed resolver · routes
NETWORK DETAIL — UDP / TCP 53 · routing · firewall · loss
RECURSION DETAIL — forwarders · conditional forwarders · upstream
ZONE DETAIL — authority · delegation · dynamic registration
IPv6 DETAIL — AAAA · reachable route · address preference
BROWSER DETAIL — secure DNS policy · proxy resolution · cache
APPLICATION DETAIL — DNS success / TCP failure · port · TLS · backend
PUBLIC RECORDS — propagation · authoritative answer · expiry · owner
TOOLS — Resolve-DnsName · nslookup · ipconfig /displaydns
SERVER TOOLS — DNS logs · service state · server-team authorization
CHANGE BOUNDARY — captured answer · TTL · approved correction · rollback
FINAL CHECK — expected answer · required port · application task""",
    "vpn.txt": """CLIENT DETAIL — product · version · profile · OS · service state
ENDPOINT DETAIL — gateway · DNS · port · certificate hostname
TRANSPORT DETAIL — internet · captive portal · proxy · firewall
CERTIFICATE DETAIL — expiry · chain · client certificate · clock
AUTHENTICATION DETAIL — authority · username · password · MFA
POLICY DETAIL — compliance · membership · restrictions
ERROR DETAIL — exact message · stage · timestamp · client logs
TUNNEL DETAIL — status · assigned address · negotiation · reconnect
ROUTE DETAIL — subnet · split tunnel · default route · overlap
DNS DETAIL — resolver · suffix · split DNS · name / IP comparison
RESOURCE DETAIL — service availability · required port · permission
OVERLAPPING SUBNETS — home LAN · corporate LAN · route preference
QUALITY DETAIL — Wi-Fi · loss · latency · mobile network
SESSION DETAIL — timeout · sleep / wake · roaming
ISOLATION MATRIX — user / device / network · known-good profile
CLIENT SERVICE — dependency · driver · endpoint security
LOG CORRELATION — client · gateway · authentication · policy owner
CHANGE BOUNDARY — approved profile · driver update · rollback
SECURITY BOUNDARY — MFA verification · no policy bypass · approved reset
FINAL MATRIX — tunnel · internal DNS · port · business app""",
    "printing.txt": """SCOPE MATRIX — app / all apps · user / all users · printer / all printers
DEVICE DETAIL — power · consumables · paper path · display
CONNECTION DETAIL — USB · direct IP · shared queue · Wi-Fi
ADDRESS DETAIL — printer IP · reservation · old port address
NETWORK DETAIL — DNS · reachability · print protocol · server
QUEUE DETAIL — paused · offline · stuck job · owner
JOB DETAIL — document type · size · corruption · user context
CONTROL OUTPUT — printer self-test · Windows test page · minimal document
APP COMPARISON — PDF · browser · Office · alternate device
DRIVER DETAIL — model · architecture · package · version
PORT DETAIL — TCP/IP · WSD · server share · expected address
SETTINGS DETAIL — tray · paper size · duplex · color · finishing
SPOOLER DETAIL — service · dependencies · crash events · timing
SERVER DETAIL — shared impact · server queue · deployment policy
ACCESS DETAIL — printer rights · membership · driver policy
PATTERN DETAIL — document · driver · repeated spooler failure
LOGS — PrintService Operational · Application · System · device logs
REMEDIATION ORDER — individual job · targeted queue · approved driver repair
SHARED IMPACT — other users · server owner · restart authorization
FINAL CHECK — original document · correct printer · settings""",
    "teams.txt": """CLIENT MATRIX — desktop / web · same account · same meeting
INPUT CHAIN — microphone · OS input · Teams device · meeting mute
OUTPUT CHAIN — Teams speaker · OS output · mixer · device
CAMERA CHAIN — shutter · privacy · OS Camera · Teams selection
USB DETAIL — port · dock · hub · bandwidth · power
BLUETOOTH DETAIL — profile · pairing · battery · competing device
PERMISSION DETAIL — camera · microphone · browser · organization policy
EXCLUSIVE USE — meeting app · recording app · device lock
AUDIO LEVEL — input meter · gain · noise suppression · volume
ECHO DETAIL — duplicate devices · speaker pickup · joined endpoints
WEB BASELINE — supported browser · permissions · same device
MEETING DETAIL — tenant · device · meeting ID · timestamp
NETWORK DETAIL — latency · jitter · loss · Wi-Fi · VPN
QUALITY DETAIL — call-health metrics · bandwidth · CPU · load
CLIENT DETAIL — build · update · cached account · policy · health
SCREEN SHARING — display selection · OS permission · graphics · policy
IDENTITY DETAIL — prompts · guest tenant · MFA · license
HARDWARE MATRIX — headset · camera · direct USB · another app
LOG PACKAGE — app logs · call time · devices · comparisons
REPAIR BOUNDARY — version-specific procedure · saved work · authorization
FINAL MATRIX — preview · test call · audio · video · sharing""",
    "services.txt": """SERVICE INVENTORY — system name · display name · role · owner
STATE DETAIL — stopped · starting · running · stopping · recovery
STARTUP DETAIL — automatic · delayed · manual · disabled · trigger start
ERROR DETAIL — Win32 code · service-specific code · timestamp
DEPENDENCY DETAIL — service · driver · backend · network
LOGON DETAIL — local · domain · managed service account
ACCOUNT DETAIL — password · logon-as-service right · policy
BINARY DETAIL — path · existence · permissions · version · signature
CONFIGURATION DETAIL — arguments · working directory · file · environment
RESOURCE DETAIL — disk · memory · port conflict · certificate
EVENTS — Service Control Manager · Application · vendor logs
PROCESS DETAIL — PID · crash · timeout · exit code
RECOVERY DETAIL — restart policy · restart loop · failure timing
POLICY DETAIL — Group Policy · baseline · endpoint controls
COMPARISON — matching known-good host · expected startup
TOOLS — services.msc · Get-Service · sc.exe query · Win32_Service
SHARED IMPACT — dependencies · other users · service owner
CHANGE BOUNDARY — approved restart · expected configuration · rollback
ACCOUNT BOUNDARY — credential owner · no generic account replacement
FINAL CHECK — successful start · stable process · dependent workflow""",
    "accounts.txt": """DIRECTORY MAP — AD · Entra · managed domain · hybrid authority
USER MAP — UPN · SAM account · domain · email alias
STATE DETAIL — disabled · locked · account expiry · password expiry
VERIFICATION DETAIL — approved proof · authorized contact
LOG DETAIL — source host · time · failure reason · repeated pattern
AD EVENTS — 4740 · 4625 · 4771 · 4776 · authorized audit access
CLOUD LOGS — sign-in failure · MFA · risk · policy evaluation
PASSWORD TIMELINE — last change · authority · sync · replication
RETRY SOURCES — mobile mail · VPN · Wi-Fi · RDP · browser
BACKGROUND SOURCES — services · scheduled tasks · mapped drives
CREDENTIAL STORES — exact target · Credential Manager · app session
OLD SESSION DETAIL — disconnected session · unattended app · stale token
HYBRID DETAIL — on-premises reset · cloud propagation · sign-in method
DOMAIN DETAIL — controller · site · DNS · time skew
MFA DETAIL — method · new phone · prompt · approved recovery
POLICY DETAIL — Conditional Access · compliance · risk · location
LOCKOUT SCOPE — device · app · repeated interval · recent change
ROOT-CAUSE ORDER — source identification · targeted correction · controlled unlock
BOUNDARY — no blanket credential deletion · no lockout-policy weakening
ESCALATION PACKAGE — events · source · time · tests · authority
FINAL CHECK — authentication · resource · recurrence window""",
    "mapped-drives.txt": """RESOURCE MAP — letter · UNC · server · share · subfolder
USER CONTEXT — interactive · elevated · application identity
PATH MATRIX — letter / UNC · hostname / FQDN · known-good resource
TRANSPORT DETAIL — TCP 445 · route · VPN · server
DNS DETAIL — expected address · suffix · split DNS
AUTHENTICATION DETAIL — domain · account · saved credentials
KERBEROS DETAIL — tickets · time · SPN · identity owner
PERMISSION DETAIL — share · NTFS · effective access
MEMBERSHIP DETAIL — nested group · replication · refreshed logon
MAPPING DETAIL — persistence · net use · SMB state
DEPLOYMENT DETAIL — Group Policy · targeting · logon script
POLICY TOOLS — gpresult · management logs · processing time
TIMING DETAIL — sign-in network · VPN · delayed reconnect
CLIENT DETAIL — offline files · cache · credential target
SERVER DETAIL — share · storage · SMB service · capacity
FILE DETAIL — path length · locks · open handles · read-only
ERROR DETAIL — exact code · timestamp · access / path
CHANGE BOUNDARY — targeted mapping · credential owner · rollback
SECURITY BOUNDARY — no SMB1 enablement · approved policy
FINAL MATRIX — read · write · open · save · reconnect · sign-in""",
    "applications.txt": """FAILURE MAP — launch · startup · action · file · backend · shutdown
VERSION MAP — app · OS · architecture · plugins
ERROR DETAIL — code · module · exception · time
REPRODUCTION DETAIL — minimal input · safe copy · consistent action
PROFILE MATRIX — user / other host · other user / host
DATA MATRIX — file / new file · local / network path
PROCESS DETAIL — launch · hang · exit code · resource use
EVENTS — Application Error · Windows Error Reporting · vendor logs
RELIABILITY — install timeline · repeated failure · update correlation
DUMP BOUNDARY — authorization · app data · sensitive content
DEPENDENCY DETAIL — .NET · Visual C++ · runtime · driver · service
CONFIGURATION DETAIL — user settings · environment · cache · rights
EXTENSION DETAIL — safe mode · approved add-in · version · load order
BACKEND DETAIL — endpoint · DNS · port · authentication · health
SECURITY DETAIL — app control · alert · permitted execution
STORAGE DETAIL — free space · temp path · locks · corrupt input
UPDATE DETAIL — vendor known issue · compatibility · rollback
REPAIR ORDER — targeted setting · update · repair · reinstall last
DATA BOUNDARY — backup · export · local-only data · license
FINAL MATRIX — original action · original data · repeat · stability""",
    "Y.txt": """CONTEXT — FortiOS version · VDOM · HA member · role
FLOW ID — source IP · destination IP · protocol · ports
TIME CONTEXT — timestamp · time zone · log window · reproduction
INGRESS — interface · VLAN · subnet · VDOM
EGRESS — route lookup · policy route · SD-WAN rule · next hop
RETURN PATH — reverse route · asymmetric flow · upstream route
POLICY MATCH — rule order · interface pair · address object · service
POLICY DETAIL — schedule · identity group · implicit deny · logging
TRAFFIC LOGS — forward traffic · action · policy ID · session ID · bytes
SESSION DETAIL — state · NAT mapping · timeout · hardware offload
NAT DETAIL — SNAT · central NAT · VIP / DNAT · expected source
DNS DETAIL — resolver · FortiGate DNS · domain filter · resolution
AUTH DETAIL — LDAP / RADIUS · group match · certificate · MFA
VPN DETAIL — IPsec phase state · selectors · route · auth logs
SD-WAN DETAIL — health check · latency · loss · member selection
SECURITY PROFILE — IPS · antivirus · web filter · app control
TLS INSPECTION — trust · profile · handshake · exemption owner
FORTIGUARD — license · reachability · signatures · category result
SYSTEM HEALTH — CPU · memory · conserve mode · counters
EVENT LOGS — system · admin change · HA · link · VPN
HA DETAIL — active member · sync · failover time · session pickup
CAPTURE PLAN — source / destination filter · interfaces · privacy
DEBUG FLOW — authorization · narrow filters · short capture · debug stop
DEBUG LIMITS — version-specific syntax · offload visibility · performance
LOG COMPARISON — permitted flow · denied flow · known-good device
CHANGE PLAN — firewall owner · config backup · approved window · rollback
FINAL MATRIX — route · policy · session · app · return traffic""",
    "linux.txt": """HOST INVENTORY — distribution · release · kernel · architecture · role
SYSTEM BASELINE — uptime · load average · CPU · memory · swap
STORAGE CAPACITY — df -h · df -i · disk / inode exhaustion
STORAGE MAP — lsblk · mount · findmnt · filesystem · path
STORAGE HEALTH — kernel I/O · read-only mount · diagnostics
FILE ACCESS — owner · group · mode · ACL · parent directories
SECURITY CONTEXT — SELinux / AppArmor · audit evidence · approved policy
PROCESS DETAIL — ps · top · PID · resource pattern · open descriptors
SERVICE DETAIL — systemctl status · unit · dependencies · exit code
STARTUP DETAIL — enabled state · overrides · directory · environment
JOURNAL DETAIL — journalctl · unit · boot · priority · timestamp
KERNEL DETAIL — dmesg · driver · device · OOM event
NETWORK ADDRESS — ip addr · link · DHCP · subnet
NETWORK PATH — ip route · gateway · VPN · port
LISTENERS — ss · bind address · port · process
DNS DETAIL — resolver · resolvectl · hostname / IP comparison
SSH DETAIL — user · key · authorized_keys · rights · host key · logs
ACCOUNT DETAIL — lock · shell · expiry · sudo authorization
PACKAGE DETAIL — distribution package manager · version · repository
CERTIFICATE DETAIL — trust store · expiry · hostname · time
SCHEDULE DETAIL — cron · systemd timer · user context · output
LOG ROTATION — disk growth · retention · service logs · ownership
CONTAINER BOUNDARY — host / container · volume · namespace · owner
RECOVERY ORDER — backup · approved service action · targeted change · rollback
FINAL CHECK — process · service · access · original task · persistence""",
    "hardware.txt": """INVENTORY — model · serial · firmware · warranty · compatibility
SIGNAL PATH — host · port · cable · dock / hub · peripheral
POWER DETAIL — adapter rating · USB power · powered hub · dock
USB DETAIL — connector · alternate port · direct host
DOCK DETAIL — model · firmware · charger · display support
DEVICE MANAGER — hardware ID · status code · driver · event history
DRIVER DETAIL — OEM source · exact device · architecture · update
DISPLAY DETAIL — HDMI / DisplayPort / USB-C · source · mode
MULTI-DISPLAY — arrangement · scaling · resolution · refresh · bandwidth
KEYBOARD / MOUSE — batteries · pairing · receiver · accessibility
AUDIO DETAIL — routing · jack detection · microphone / output
STORAGE DETAIL — detection · connector · encryption · data protection
THERMAL DETAIL — ventilation · fan · temperature · workload
DIAGNOSTICS — vendor test · error code · reproducible pattern
INTERMITTENT — cable movement · sleep / wake · dock reconnect · heat
COMPARISON MATRIX — known-good device · cable · port · model
FIRMWARE BOUNDARY — stable power · approved package · recovery key
PHYSICAL BOUNDARY — warranty · trained technician · safe access
REPLACEMENT DETAIL — compatibility · asset tracking · loaner · impact
FINAL CHECK — peripheral workflow · reconnect · restart · stability""",
    "customer-communication.txt": """CALL CONTEXT — callback · location · urgency · user needs
ACTIVE LISTENING — uninterrupted description · user wording · clarification
FACT / ASSUMPTION — observed symptom · hypothesis · evidence
EXPECTATION SETTING — next test · disruption · checkpoint
PLAIN LANGUAGE — familiar terms · concise explanation · confirmation
REMOTE SESSION — identity check · consent · visible actions
USER ACTION — one instruction · confirmation · observed result
FRUSTRATION — acknowledgement · calm pace · business impact
ACCESSIBILITY — pace · landmarks · alternative channel
UNCERTAINTY — finding · remaining hypothesis · escalation plan
TIME MANAGEMENT — progress summary · pause point · callback
HANDOFF — owner · reason · findings · next checkpoint
WORKAROUND — benefit · limitation · temporary duration
PRIVACY — sensitive screens · necessary data · approved handling
CLOSURE CHECK — user task · outcome · remaining impact
FOLLOW-UP — ticket · contact route · timeframe""",
    "ticketing.txt": """INCIDENT QUALITY — title · service · observable symptom
REQUEST QUALITY — desired access / service · approval · owner
ENVIRONMENT — OS · app build · tenant · site · device
TIMELINE — onset · last success · change · timestamps
IMPACT DETAIL — users · blocked activity · workaround
PRIORITY JUSTIFICATION — impact · urgency · SLA · business context
REPRODUCTION DETAIL — workflow · input · comparison · result
TEST RECORD — hypothesis · action · observation · interpretation
CHANGE RECORD — approval · original / new setting · rollback
ATTACHMENTS — logs · sanitized screenshots · exact error
DATA BOUNDARY — no passwords · no secrets · minimum personal data
ESCALATION QUALITY — focused question · missing authority · evidence
OWNERSHIP QUALITY — team · next action · checkpoint
RESOLUTION QUALITY — cause / uncertainty · fix · validation
KNOWLEDGE QUALITY — reusable cues · scope · applicability · version
CLOSURE QUALITY — agreement · outcome · reopen route · follow-up""",
    "prioritization.txt": """BUSINESS CONTEXT — revenue · operations · critical deadline
AFFECTED SCOPE — user · team · site · organization
SERVICE CRITICALITY — application · identity · network · data loss
URGENCY DETAIL — blocked / degraded work · acceptable delay
SECURITY PRIORITY — compromise · exposed data · security owner
MAJOR INCIDENT — pattern · dependency · incident lead
SLA DETAIL — response · resolution · escalation threshold
WORKAROUND DETAIL — availability · effectiveness · temporary risk
QUEUE REVIEW — age · impact · ownership · dependency
PARALLEL WORK — independent tests · specialist · coordinated changes
ESCALATION LEVEL — expertise · approval · vendor · management
VENDOR PACKAGE — contract · asset · version · evidence
COMMUNICATION CADENCE — user · stakeholders · next checkpoint
DEPENDENCY TRACKING — approval · external team · promised response
RECURRENCE — related tickets · problem record · known error
CLOSURE PRIORITY — restoration · backlog · follow-up""",
    "Q.txt": """ONBOARDING — first weeks · shadowing · knowledge base · access
TEAM STRUCTURE — tiers · specialists · service owners
ESCALATION CULTURE — difficult issues · consultation · feedback
QUALITY MEASURES — satisfaction · ticket quality · effectiveness
LEARNING SUPPORT — training · certifications · mentoring
SERVICE ENVIRONMENT — remote / on-site · locations · platforms
BUSINESS CONTEXT — critical services · peak periods · users
WORKLOAD — tickets · calls · backlog · prioritization
TECHNICAL DEPTH — challenges · complex incidents · improvement
KNOWLEDGE PRACTICE — ownership · review · sharing
COMMUNICATION — meetings · handoff · incident updates
ROLE FIT — expectations · support style · long-term growth
INTERVIEW CLOSING — skill clarification · concerns · next stage""",
    "Z.txt": """ROLE CONNECTION — users · infrastructure interest · reliable service
LONG-TERM FIT — stability · development · responsibility
LEARNING STYLE — questions · documentation · safe testing · feedback
ENVIRONMENT FIT — approachable colleagues · cooperation · expectations
TRANSITION FRAMING — gratitude · positive growth · future goals
LINUX EXAMPLES — actual distributions · actual tasks · honest scope
DATA CENTER INTEREST — hardware · availability · structured operations
EMPLOYER RESEARCH — role description · values · responsibilities
PERSONAL EVIDENCE — real task · contribution · verified result
SKILL BOUNDARIES — familiar tools · learning areas · escalation judgment
ANSWER SHAPE — motivation · example · role connection
CUSTOMIZATION — employer · vacancy · authentic interest""",
    "interview-star.txt": """STORY INVENTORY — support · difficult diagnosis · collaboration
SITUATION DETAIL — user · service · impact · context
TASK DETAIL — assignment · ownership · deadline · constraints
ACTION DETAIL — decisions · diagnosis · communication
RESULT DETAIL — actual improvement · confirmation · outcome
TECHNICAL STORY — scope · hypothesis · comparison · cause
CUSTOMER STORY — listening · de-escalation · explanation · resolution
TEAM STORY — evidence · handoff · specialist collaboration
PRIORITY STORY — impact · urgency · competing tasks · updates
MISTAKE STORY — acknowledgement · correction · prevention
LEARNING STORY — unfamiliar tool · source · safe test · feedback
SECURITY STORY — verification · evidence · approved escalation
BOUNDARIES — personal / team contribution · honest uncertainty
DELIVERY — concise context · strongest actions · actual result
FOLLOW-UP PROMPTS — alternatives · tradeoff · lesson · next-time change""",
    "interview-technical.txt": """OPENING CUES — expected behavior · symptom · scope · changes
DIAGNOSTIC ORDER — observations · working comparison · one variable
DNS ANSWER — address · resolver · record · cache · route · app
AUTHENTICATION ANSWER — identity · authority · credentials · MFA · policy
PERMISSIONS ANSWER — authentication / authorization · group · rights
EMAIL ANSWER — web comparison · account · mailbox · transport · client
SYNC ANSWER — cloud copy · local changes · quota · locks · rights
PERFORMANCE ANSWER — measured process · resource · baseline · change
POWER ANSWER — state · outlet · charger · dock · indicators · safety
PRINTER ANSWER — device · queue · driver · spooler · comparison
VPN ANSWER — transport · identity · tunnel · route · DNS · resource
LINUX ANSWER — system · storage · service · journal · rights · network
FIREWALL ANSWER — flow · route · policy · NAT · return path
COMPLEX ISSUE — dependencies · timeline · discriminating test
SAFE CHANGE — approval · backup · rollback · validation
UNKNOWN ANSWER — honest boundary · source · safe test · escalation
CLOSING CUES — original task · confirmation · ticket · prevention""",
    "interview-behavioral.txt": """CUSTOMER EMPATHY — impact · listening · calm explanation · confirmation
OWNERSHIP — follow-through · updates · next action
TEAM CONTRIBUTION — evidence · consultation · handoff
CONFLICT — facts · shared goal · communication · escalation
PRIORITIZATION — impact · urgency · SLA · workaround
PRESSURE — triage · calm pace · communication · boundaries
FEEDBACK — specific input · adjustment · improvement
LEARNING — gap · research · practice · reflection
MISTAKE — accountability · correction · prevention
ETHICS — verification · least privilege · confidential data
INITIATIVE — real improvement · scope · collaboration · outcome
STRENGTH EVIDENCE — relevant trait · example · value
DEVELOPMENT EVIDENCE — real gap · action · progress
ROLE MOTIVATION — user impact · problem solving · infrastructure · growth
ANSWER CONTROL — concise STAR · honest experience · contribution""",
}

def main():
    total = 0
    for name, additions in EXTRA.items():
        path = ROOT / name
        raw = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
        title, body = raw.split("\n", 1)
        if body.endswith("\n"):
            body = body[:-1]
        existing = set(body.splitlines())
        missing = [line for line in additions.splitlines() if line not in existing]
        if not missing:
            continue
        new_body = body + "\n" + "\n".join(missing)
        path.write_text(title + "\n" + new_body + "\n", encoding="utf-8-sig")
        sidecar = Path(str(path) + ".styles.ini")
        if sidecar.exists():
            metadata = sidecar.read_text(encoding="utf-16")
            old_hash = hashlib.sha256(body.encode("utf-16-le")).hexdigest().upper()
            if "fingerprint=" + old_hash in metadata:
                new_hash = hashlib.sha256(new_body.encode("utf-16-le")).hexdigest().upper()
                sidecar.write_text(metadata.replace("fingerprint=" + old_hash, "fingerprint=" + new_hash), encoding="utf-16")
        total += len(missing)
    print(f"Appended {total} keyword reminder lines across {len(EXTRA)} subjects; placeholders untouched.")

if __name__ == "__main__":
    main()
