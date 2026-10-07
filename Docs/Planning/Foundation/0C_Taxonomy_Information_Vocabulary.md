# F7Hub Phase 0C

## Cross-Subsystem Planning Note

Define shared terms such as action, event, result, observation, validation, evidence, session, resolution, selected context so Diagnostics, Analytics and DynamicHub do not invent competing meanings

# Classification, Taxonomy, Entities, Tags & Relationships Architecture
Existing taxonomy/category/tag inventory; exact distinction between Category, Type/Kind, Entity, Entity Type, Tag, Status, Priority, Relationship, Metric and Insight; initial Entity taxonomy; normalization rules; Entity occurrence vs canonical domain record; Tag Families; canonical Tags and aliases; tag scope; provenance; confidence; relationship vocabulary; multilingual-label strategy; search semantics; analytics dimensions; privacy rules; taxonomy governance and lifecycle.

I want Codex to inspect existing:
taxonomy migration
categories
tags
tag repository
category repository
Knowledge Base tags/categories
Ticket categories
existing constraints
existing scopes

Then produce:
## Existing Taxonomy Reuse Matrix

Concept | Existing Mechanism | Used By | Reuse? | Required Change

The desired outcome is not necessarily “build Global Tags.”
It may instead be:
Existing tag system
        ↓
extend carefully
        ↓
becomes Global Tag Catalog


## Mode

`@ARCHITECT @PLAN`

Architecture and taxonomy planning only.

Do not implement production code.

Do not create SQLite migrations.

Do not modify existing taxonomy tables.

Do not create repositories or services.

Do not seed taxonomy data.

Do not create GUI components.

Do not refactor unrelated F7Hub modules.

Do not make irreversible taxonomy decisions silently.

---

# 1. Objective

Design the global F7Hub Classification and Taxonomy Architecture.

This phase must establish a shared information vocabulary that future F7Hub modules can rely on consistently.

The design must clearly define and separate:

```text
Categories
Types / Kinds
Entities
Entity Types
Tags
Tag Families
Statuses
Priorities
Relationships
Classification Confidence
Provenance
Normalization
Aliases
Scopes
```

The architecture must prevent these concepts from becoming interchangeable.

The result should give future modules a stable vocabulary for:

```text
Clipboard
Tickets
Knowledge Base
Diagnostics
PowerShell Scripts
Automation
Statistical Analytics
Mochi
Search
Companies
Contacts
Devices
Websites
Prompts
```

---

# 2. Relationship to Earlier Foundation Phases

Phase 0C depends on:

```text
Phase 0A
Master Foundation Architecture

Phase 0B
Global JSON / Interoperability Contract
```

Before taxonomy design:

1. Read the approved Phase 0A architecture plan.
2. Read the approved Phase 0B interoperability plan.
3. Inspect current F7Hub taxonomy/category implementation.
4. Inspect existing database tables.
5. Inspect existing repositories/services.
6. Inspect existing ticket category behavior.
7. Inspect existing KB taxonomy behavior.
8. Inspect current search/filter conventions.
9. Identify any existing tags or tag-like structures.
10. Identify any existing entity/reference tables.

Do not create a competing taxonomy system if existing structures can be extended.

---

# 3. Existing F7Hub Taxonomy Is Authoritative

F7Hub already has implemented shared taxonomy/category concepts.

Their exact current scope must be inspected.

Do not assume:

```text
existing categories are insufficient
```

and do not assume:

```text
existing categories can serve every future taxonomy need
```

Determine both from evidence.

Classify findings as:

```text
FACT
ASSUMPTION
INFERENCE
RECOMMENDATION
NOT VERIFIED
```

---

# 4. Primary Principle

The architecture must answer:

```text
WHAT IS THIS RECORD?
WHAT FORMAL CLASSIFICATION DOES IT BELONG TO?
WHAT SPECIFIC OBJECTS DOES IT CONTAIN?
WHAT TOPICS IS IT ABOUT?
WHAT IS ITS WORKFLOW STATE?
HOW IS IT RELATED TO OTHER RECORDS?
```

These are different questions.

They require different data concepts.

---

# 5. Core Vocabulary

The following definitions are the initial conceptual baseline.

Phase 0C must verify, refine, and formalize them.

---

# 6. Category

A Category is a controlled formal classification used by a specific domain.

Example:

```text
Ticket Category:
Microsoft 365
```

or potentially:

```text
Knowledge Category:
Troubleshooting
```

Categories typically support:

```text
controlled classification
workflow
reporting
filtering
business rules
```

Categories may be scoped to particular modules.

They should not automatically become global Tags.

---

# 7. Type / Kind

Type or Kind describes what a record fundamentally is.

Examples:

```text
clipboard:
powershell_error
url
mixed_text

ticket:
incident
service_request

knowledge:
how_to
troubleshooting_article
reference
```

Type should answer:

```text
What kind of object is this?
```

It should not answer:

```text
What topic is this about?
```

---

# 8. Entity

An Entity is a specific identifiable value or object found in content or context.

Examples:

```text
10.0.0.87
john@contoso.com
PC-1042
outlook.office.com
0x80070005
INC0045211
C:\Windows\Temp\support.log
```

Entities are concrete.

Tags are conceptual.

---

# 9. Entity Type

Entity Type describes the class of detected entity.

Examples:

```text
ipv4
ipv6
email
upn
hostname
fqdn
url
file_path
registry_path
error_code
event_id
ticket_id
powershell_command
service_name
```

Example:

```text
Entity Type:
ipv4

Entity Value:
10.0.0.87
```

---

# 10. Tag

A Tag is a flexible reusable cross-module concept.

Examples:

```text
DNS
Outlook
Authentication
Networking
PowerShell
Security
VPN
Printer
Microsoft 365
```

Tags answer:

```text
What is this about?
```

Tags should be reusable across eligible F7Hub modules.

---

# 11. Status

Status represents workflow state.

Examples:

```text
OPEN
WAITING_CUSTOMER
RESOLVED

DRAFT
PUBLISHED
ARCHIVED

ACTIVE
DISABLED
```

Status is not a Tag.

Do not model workflow states as tags.

---

# 12. Priority

Priority represents urgency or operational importance.

Examples:

```text
P1
P2
P3
P4
```

Priority must remain separate from Tags and Categories.

---

# 13. Relationship

A Relationship explicitly connects two records.

Examples:

```text
Clipboard Item
    EVIDENCE_FOR
Ticket

Diagnostic Session
    RUN_FOR
Ticket

KB Article
    RESOLVES
Issue Pattern

Script
    USED_BY
Diagnostic
```

Relationships describe structure between records.

Tags describe shared concepts.

---

# 14. Metric

Metric is a calculated measurement.

Example:

```text
31 DNS-related tickets in the last 30 days.
```

Metrics must not become Tags.

---

# 15. Insight

Insight is a derived interpretation of data.

Example:

```text
DNS-related activity increased 42% this month.
```

Insights should not silently modify classification.

---

# 16. Classification Hierarchy

The plan should establish a conceptual classification stack such as:

```text
Record
│
├── Domain
├── Type / Kind
├── Formal Category
├── Status
├── Priority
│
├── Entities [0..many]
├── Tags [0..many]
└── Relationships [0..many]
```

Example:

```text
Ticket #41872

Domain:
Ticket

Type:
Incident

Category:
Microsoft 365

Status:
Open

Priority:
P2

Entities:
john@contoso.com
OUTLOOK.EXE
0x8004010F

Tags:
Outlook
Authentication
Microsoft 365
Recurring Issue

Relationships:
Clipboard Item #901
Diagnostic Session #55
KB Article #17
```

---

# 17. Master Taxonomy Inventory

Before designing schemas, produce a proposed master inventory of classifications needed across F7Hub.

The inventory must be organized by concept.

Example:

```text
Categories
Types
Entity Types
Tag Families
Tags
Statuses
Priorities
Relationship Types
```

Do not mix these lists.

---

# 18. Existing Category Inventory

Inspect all current category/taxonomy records.

Produce:

```text
Current category key
Display name
Scope
Active state
Used by
Repository/service owner
Current relationships
```

Identify:

```text
usable as-is
extendable
duplicate
legacy
unclear
```

Do not modify them during this phase.

---

# 19. Category Scope

Determine whether categories are currently:

```text
global
module-scoped
domain-scoped
hierarchical
flat
```

Recommend the future model.

Possible scopes may include:

```text
TICKET
KNOWLEDGE
SCRIPT
DIAGNOSTIC
```

Do not create duplicate category values solely because they are used in multiple modules unless semantic meaning actually differs.

---

# 20. Categories vs Tags Decision Rules

Create explicit rules.

Example:

Use a Category when:

```text
the classification is formal
the value set is controlled
the module relies on it operationally
workflow/reporting depends on it
one primary classification is expected
```

Use a Tag when:

```text
multiple labels may apply
cross-module discovery is useful
classification is topical
classification is flexible
workflow does not depend on it
```

---

# 21. Example

Ticket:

```text
Category:
Networking

Tags:
VPN
DNS
Fortinet
Remote Access
Recurring Issue
```

Do not create:

```text
Category:
Networking / VPN / DNS / Fortinet / Remote Access
```

unless there is a genuine business need for such hierarchy.

---

# 22. Type / Kind Inventory

Produce proposed type inventories per major domain.

At minimum evaluate:

```text
Clipboard
Ticket
Knowledge
Diagnostic
Script
Automation
Website
Prompt
```

Example Clipboard types:

```text
plain_text
mixed_text
url
powershell_command
powershell_output
powershell_error
log
json
xml
yaml
csv
markdown
ticket_data
error_message
unknown
```

Do not treat this example list as final.

Phase 0C must refine it.

---

# 23. Type Governance

Determine whether Types are:

```text
hard-coded enums
reference-table records
configuration
taxonomy records
```

Different domains may require different approaches.

The plan must recommend consistency without forcing unrelated domains into one generic Type table.

---

# 24. Global Entity Taxonomy

Design a proposed master inventory of Entity Types.

This should be comprehensive enough to support upcoming Clipboard and Diagnostic planning.

Organize by family.

---

# 25. Network Entity Types

Evaluate:

```text
ipv4
ipv6
cidr
mac_address
hostname
fqdn
domain
url
port
protocol
socket_endpoint
```

---

# 26. Identity Entity Types

Evaluate:

```text
email
upn
username
sid
guid
display_name
entra_object_id
tenant_id
```

Be careful with ambiguous natural-language names.

---

# 27. Windows Entity Types

Evaluate:

```text
file_path
directory_path
unc_path
registry_path
process_name
process_id
service_name
device_name
computer_name
event_id
windows_build
```

---

# 28. PowerShell / Command Entity Types

Evaluate:

```text
powershell_command
powershell_cmdlet
powershell_parameter
powershell_module
cmd_command
command_line
script_path
```

---

# 29. Error / Diagnostic Entity Types

Evaluate:

```text
error_code
hresult
win32_error
powershell_error_id
exception_type
stack_trace
smtp_status
ndr_code
http_status
event_id
```

Determine overlaps carefully.

Example:

```text
event_id
```

should not accidentally be defined in multiple incompatible families.

---

# 30. Ticketing Entity Types

Evaluate:

```text
ticket_id
incident_id
request_id
problem_id
change_id
task_id
```

Determine whether these should be generic or platform-specific.

---

# 31. Microsoft Entity Types

Evaluate:

```text
tenant_id
entra_object_id
intune_device_id
exchange_guid
message_id
mailbox_guid
azure_resource_id
subscription_id
```

Only include entities with realistic F7Hub use cases.

---

# 32. Security Entity Types

Evaluate:

```text
cve_id
md5
sha1
sha256
certificate_thumbprint
security_alert_id
```

Sensitive values such as passwords and tokens should not necessarily become normal Entities.

---

# 33. Structured Data Entity Types

Evaluate whether:

```text
json_object
xml_fragment
yaml_fragment
csv_data
key_value
```

are actually Entity Types or better represented as content Types.

Do not classify container formats as Entities unless justified.

---

# 34. Temporal Entity Types

Evaluate:

```text
date
time
datetime
timestamp
duration
```

Decide whether generic time values should normally become stored Entities.

Avoid clutter.

---

# 35. Software Entity Types

Evaluate:

```text
software_name
product_name
version
semantic_version
package_name
```

Define normalization expectations.

---

# 36. Entity Persistence Strategy

Not every detected entity must become a permanent database record.

Distinguish:

```text
detected entity occurrence
```

from:

```text
canonical domain entity
```

Example:

```text
Clipboard detects:
PC-1042
```

This does not automatically mean:

```text
create Device record PC-1042
```

Instead:

```text
Detected Entity
     ↓
Optional Resolver
     ↓
Existing Device Match?
```

Only explicit workflow should create or link a canonical Device.

---

# 37. Entity Occurrence Model

Evaluate an occurrence model containing:

```text
source_record
entity_type
raw_value
normalized_value
confidence
start_offset
end_offset
metadata
provenance
```

This is particularly relevant for Clipboard.

---

# 38. Canonical Entity Resolution

Plan for optional future entity resolution.

Concept:

```text
Detected:
john@contoso.com

        ↓

Resolver

        ↓

Contact #88
```

or:

```text
Detected:
PC-1042

        ↓

No canonical device exists

        ↓

Keep as detected entity only
```

Do not force resolution.

---

# 39. Entity Normalization

Each Entity Type may need normalization.

Examples:

```text
Email
JOHN@CONTOSO.COM
→ john@contoso.com
```

```text
IPv4
010.000.000.001
→ validated normalized representation
```

```text
URL
HTTP://EXAMPLE.COM
→ canonicalized where safe
```

```text
MAC
00-11-22-AA-BB-CC
→ normalized format
```

The plan must define:

```text
raw_value
normalized_value
```

semantics.

---

# 40. Never Normalize Away Meaning

Normalization must not silently change semantic content.

Example:

URL query strings may contain meaningful values.

File paths may be case-insensitive but still should retain original text for evidence.

Therefore preserve:

```text
raw_value
```

and separately store:

```text
normalized_value
```

when justified.

---

# 41. Classification Confidence

Automated classifications need confidence.

Conceptual model:

```text
0.0 → 1.0
```

Examples:

```text
IPv4 validated by ipaddress:
1.0

Probable hostname:
0.82

AI-suggested product:
0.65
```

Define which classifications are deterministic and do not need probabilistic semantics.

---

# 42. Provenance

Every automated classification should be able to answer:

```text
Where did this classification come from?
```

Proposed provenance values:

```text
USER
RULE
PARSER
IMPORT
SYSTEM
AI_SUGGESTED
RESOLVER
```

Do not treat AI suggestions as equivalent to deterministic parser results.

---

# 43. Provenance vs Assignment Source

Determine whether one common provenance vocabulary can cover:

```text
Entity extraction
Tag assignment
Category assignment
Relationship creation
```

or whether each domain requires its own constrained values.

Avoid one overly generic field whose semantics become unclear.

---

# 44. Tag Architecture

Evaluate a global shared Tag Catalog.

Conceptual:

```text
tags
tag_families
tag_aliases
tag_module_scopes
```

Do not finalize SQL yet.

---

# 45. Tag Families

Produce a proposed master Tag Family inventory.

At minimum evaluate:

```text
technology
product
platform
issue
networking
identity
security
workflow
knowledge
automation
protocol
hardware
custom
```

Determine whether some should be merged.

---

# 46. Proposed Technology Tags

Evaluate:

```text
PowerShell
Python
AutoHotkey
Microsoft Graph
SQLite
Windows
```

Only include tags relevant to F7Hub usage.

---

# 47. Product Tags

Evaluate:

```text
Outlook
Teams
OneDrive
SharePoint
Exchange Online
Intune
Entra ID
Defender
Purview
Fortinet
Windows 11
```

---

# 48. Networking Tags

Evaluate:

```text
DNS
DHCP
VPN
Wi-Fi
TCP/IP
Routing
Firewall
Proxy
Connectivity
```

---

# 49. Identity Tags

Evaluate:

```text
Authentication
Authorization
MFA
Password
Account Lockout
Conditional Access
SSO
```

---

# 50. Security Tags

Evaluate:

```text
Phishing
Malware
Spam
Safe Links
Safe Attachments
Endpoint Security
Email Security
```

Avoid duplicating Product Tags.

For example:

```text
Defender
```

may be Product.

```text
Malware
```

may be Security.

---

# 51. Workflow Tags

Evaluate:

```text
Needs Review
Follow-up
Escalation
Recurring Issue
Training
Documentation Needed
Automation Candidate
Knowledge Gap
```

These may be especially useful for Tickets, Clipboard, and Analytics.

---

# 52. Knowledge Tags

Evaluate:

```text
Troubleshooting
How-To
Reference
FAQ
Known Issue
Workaround
Best Practice
```

Determine whether these are better as KB Types instead.

Do not duplicate Type concepts as Tags unnecessarily.

---

# 53. Tag Aliases

Plan canonical aliases.

Example:

```text
PowerShell
Aliases:
PS
pwsh
Power Shell
```

Example:

```text
Microsoft 365
Aliases:
M365
Office 365
O365
```

Aliases should support:

```text
search
import cleanup
auto-tag resolution
```

but should not appear as separate analytics dimensions.

---

# 54. Tag Module Scopes

Tags should be global, but suggestion scope may differ.

Example:

```text
Tag:
PowerShell

Recommended for:
Clipboard
Diagnostics
Scripts
KB
Automation
Tickets

Not usually suggested for:
Contacts
Companies
```

Scope affects suggestion behavior.

Scope must not create duplicate Tags.

---

# 55. System Tags vs User Tags

Plan:

```text
SYSTEM
USER
```

System Tags:

```text
controlled
stable
possibly non-editable
used by rules
```

User Tags:

```text
flexible
user-created
editable
```

Determine how user-created tags interact with aliases and families.

---

# 56. Tag Lifecycle

Plan states such as:

```text
ACTIVE
INACTIVE
MERGED
```

Do not casually physically delete Tags used historically.

Preserve analytics integrity.

---

# 57. Tag Merge

Design the semantic behavior.

Example:

```text
Power Shell
PS
PowerShell
```

merge into:

```text
PowerShell
```

Required future behavior:

```text
reassign relationships
preserve aliases
prevent duplicate links
retain historical trace if needed
transactional change
```

Do not implement yet.

---

# 58. Tag Assignment

Tag assignment may be:

```text
manual
rule-based
imported
system-generated
AI-suggested
```

Determine which may auto-assign and which require approval.

---

# 59. Auto-Tag Rules

Do not design full implementation yet.

Define rule classes.

Possible:

```text
ENTITY_PRESENT
PRIMARY_KIND
KEYWORD
REGEX
SOURCE_APPLICATION
RELATIONSHIP
CATEGORY
COMPOSITE
```

Examples:

```text
Entity ipv4
→ Networking
```

```text
PowerShell cmdlet Resolve-DnsName
→ PowerShell
→ DNS
→ Networking
```

---

# 60. Auto-Tag Confidence

Create policy recommendations.

Potential:

```text
deterministic rule
→ auto-assign

strong heuristic
→ auto-assign or suggest

weak heuristic
→ suggest only

AI
→ suggest unless specifically trusted
```

Do not hard-code thresholds without evidence.

---

# 61. Categories vs Tags Examples

Produce a large comparison matrix.

Examples:

```text
Outlook
could be:
Category? Possibly in some module.
Tag? Yes, likely global product tag.

DNS
Category? Possibly diagnostic category.
Tag? Yes.
Entity? No.

10.0.0.87
Entity? Yes.
Tag? No.

P2
Priority? Yes.
Tag? No.

Resolved
Status? Yes.
Tag? No.

powershell_error
Kind? Yes.
Tag? No.

Recurring Issue
Tag? Yes.
Status? No.
```

This matrix should become a reference for future Codex work.

---

# 62. Relationship Architecture

Produce a master relationship vocabulary.

Relationships should be semantic.

Examples:

```text
EVIDENCE_FOR
RELATED_TO
RUN_FOR
GENERATED_FROM
USES
REFERENCES
RESOLVES
SUGGESTS
DERIVED_FROM
```

Do not create dozens prematurely.

---

# 63. Relationship Direction

Determine whether relationships are directional.

Example:

```text
Clipboard Item
EVIDENCE_FOR
Ticket
```

is not semantically identical to:

```text
Ticket
EVIDENCE_FOR
Clipboard Item
```

Plan directionality explicitly.

---

# 64. Explicit Link Tables vs Generic Relationships

Evaluate where F7Hub should use:

```text
dedicated foreign-key relationship tables
```

versus:

```text
generic relationship infrastructure
```

Default principle:

Use explicit relational tables when strong referential integrity is available.

Example:

```text
clipboard_ticket_links
```

may be better than:

```text
relationships(
    source_type,
    source_id,
    target_type,
    target_id
)
```

But inspect existing architecture before deciding.

---

# 65. Cross-Module Relationship Map

Produce a conceptual map including:

```text
Tickets
Companies
Contacts
Devices
KB
Clipboard
Diagnostics
Scripts
Automation
Tags
Entities
Analytics
Mochi
```

Example:

```text
Company
   ↓
Contact

Ticket
   ├── Company
   ├── Contact
   ├── Clipboard Evidence
   ├── Diagnostics
   └── KB Articles

Diagnostic
   ├── Script
   ├── Findings
   ├── Evidence
   └── Tags

Clipboard
   ├── Entities
   ├── Tags
   ├── Ticket Links
   └── Diagnostic Links
```

---

# 66. Relationship Provenance

Determine whether cross-module links should track:

```text
USER
SYSTEM
RULE
IMPORT
AI_SUGGESTED
```

Example:

```text
Clipboard linked to Ticket
```

may be:

```text
USER
```

while:

```text
Diagnostic linked to Ticket
```

may be:

```text
SYSTEM
```

because it was launched from that ticket.

---

# 67. Search Architecture Impact

Taxonomy must support future Global Search.

Examples:

```text
tag:DNS
entity:10.0.0.87
kind:powershell_error
category:Networking
status:Open
```

The plan should define canonical search semantics.

Do not implement search syntax yet.

---

# 68. Statistical Analytics Impact

Taxonomy becomes a dimension source.

Analytics should be able to measure:

```text
tickets by tag
clipboard entities by type
diagnostics by category
tag co-occurrence
category distribution
entity frequency
automation coverage by tag
KB coverage by tag
```

Stable taxonomy is necessary for reliable analytics.

---

# 69. Tag Analytics

Potential metrics:

```text
top tags
tag growth
tag co-occurrence
tag-module usage
tag-to-ticket resolution time
tag-to-diagnostic usage
tag-to-KB coverage
```

Do not store these metrics in the Tag catalog.

Analytics owns derived metrics.

---

# 70. Entity Analytics

Potential measurements:

```text
most frequent error codes
most frequent domains
most frequent PowerShell cmdlets
most frequent event IDs
```

Be careful with privacy.

Avoid analytics that expose unnecessary personal identifiers.

---

# 71. Privacy Rules for Entities

Certain Entity Types may contain sensitive data.

Examples:

```text
email
username
device_name
file_path
URL
```

Determine:

```text
which may be persisted
which may be normalized
which may appear in analytics
which should be aggregated only
which require redaction
```

---

# 72. Secret Detection

Secrets should generally not become ordinary Entities.

Examples:

```text
password
MFA code
API key
Bearer token
private key
connection string
```

Instead classify sensitivity.

Possible behavior:

```text
SECRET_POSSIBLE
```

then block or quarantine persistence.

---

# 73. Taxonomy and Mochi

Mochi should consume canonical classifications.

Example context:

```text
Tags:
DNS
Networking

Entities:
IPv4 10.0.0.87
FQDN outlook.office.com
```

This is much more reliable than giving Mochi only raw text.

Mochi should not create canonical Tags or Categories independently.

---

# 74. Taxonomy and JSON Contract

Phase 0B defines how taxonomy references travel.

Phase 0C defines what those references mean.

Example:

```json
{
  "entity_type_key": "ipv4",
  "normalized_value": "10.0.0.87",
  "confidence": 1.0,
  "provenance": "PARSER"
}
```

and:

```json
{
  "tag_key": "networking",
  "confidence": 1.0,
  "assignment_source": "RULE"
}
```

Contract schemas must refer to canonical taxonomy keys.

---

# 75. Naming Convention

Recommend naming rules for taxonomy keys.

Potential:

```text
lower_snake_case
```

Examples:

```text
microsoft_365
conditional_access
powershell_command
knowledge_gap
```

Display labels remain independent:

```text
Microsoft 365
Conditional Access
PowerShell Command
Knowledge Gap
```

---

# 76. Stable Machine Keys

Machine keys should not change casually.

Example:

```text
tag_key:
microsoft_365
```

Display:

```text
Microsoft 365
```

may evolve without breaking relationships.

---

# 77. Case Normalization

Define case behavior.

Examples:

```text
Tag keys:
lowercase normalized

Emails:
lowercase where appropriate

PowerShell cmdlets:
canonical display casing preserved

File paths:
raw casing preserved
```

Do not apply one global lowercasing rule to all entity values.

---

# 78. Duplicate Detection

Plan duplicate rules.

Tags:

```text
PowerShell
powershell
Power Shell
PS
```

should resolve appropriately.

Entities:

```text
10.0.0.87
```

may be identical after normalization.

But:

```text
URL
```

duplicate semantics may depend on fragment/query rules.

Entity-specific normalization is required.

---

# 79. Taxonomy Governance

Define who may create:

```text
system categories
user categories
system tags
user tags
entity types
relationship types
```

Likely:

```text
Entity Types:
system-controlled

Core Tags:
system-controlled

User Tags:
user-created

Relationship Types:
system-controlled

Statuses:
system-controlled

Categories:
module-governed
```

Phase 0C should recommend exact governance.

---

# 80. User-Editable Taxonomy

Avoid letting users modify structural concepts such as:

```text
entity_type = ipv4
```

into:

```text
entity_type = cat_picture
```

unless custom entity types are intentionally supported later.

Tags are the natural flexible extension mechanism.

---

# 81. Taxonomy Management GUI Scope

Plan eventual Settings UI:

```text
Settings
└── Tags & Taxonomy
```

Potential sections:

```text
Tag Families
Tags
Aliases
Module Scope
Categories
Auto-tag Rules
```

Entity Type management should probably be read-only initially.

---

# 82. Tag Management GUI

Future interface should support:

```text
search
family filter
active/inactive
system/user
aliases
module scopes
usage counts
rename
deactivate
merge
```

Do not implement in Phase 0C.

---

# 83. Module Tag Selector

Plan reusable component:

```text
[Outlook ×]
[Authentication ×]
[Microsoft 365 ×]

+ Add Tag
```

This component should eventually be shared across:

```text
Tickets
KB
Clipboard
Diagnostics
Scripts
Automation
```

---

# 84. Tag Suggestions

Future UI could show:

```text
Suggested
+ PowerShell
+ DNS
+ Networking
```

but preserve provenance and confidence.

User should be able to:

```text
accept
dismiss
```

where appropriate.

---

# 85. Classification Pipeline

Recommend general layering:

```text
Raw Content
    ↓
Content Type Detection
    ↓
Entity Extraction
    ↓
Entity Normalization
    ↓
Formal Classification
    ↓
Tag Rules
    ↓
Relationship Resolution
    ↓
Persistence
```

Not every module needs every step.

---

# 86. Deterministic Before AI

Prefer:

```text
parser
regex
validation library
rule
resolver
```

before:

```text
AI
```

AI may suggest uncertain classifications later.

---

# 87. Entity Extraction Example

Input:

```text
User john@contoso.com
PC-1042
10.0.0.87
Get-Service Spooler
0x80070005
```

Possible result:

```text
Primary Kind:
mixed_text

Entities:
EMAIL
john@contoso.com

HOSTNAME
PC-1042

IPV4
10.0.0.87

POWERSHELL_COMMAND
Get-Service Spooler

SERVICE_NAME
Spooler

ERROR_CODE
0x80070005
```

---

# 88. Tagging Example

From the same item:

```text
Tags:
PowerShell
Windows
Networking
Troubleshooting
```

If active ticket context indicates printer issue:

```text
Suggested:
Printing
```

Do not infer unrelated Tags merely from weak context.

---

# 89. Category Example

The active Ticket might have:

```text
Category:
Hardware / Printing
```

or whatever the existing F7Hub category model supports.

That Category is independent from the Clipboard Item's primary Kind.

---

# 90. Relationship Example

The system may create:

```text
Clipboard Item #901
    EVIDENCE_FOR
Ticket #41872
```

That relationship is separate from:

```text
Tags:
Printing
PowerShell
```

---

# 91. Classification Confidence Matrix

Produce a matrix.

Example:

| Classification | Method | Confidence |
|---|---|---:|
| IPv4 | strict parser | deterministic |
| Email | syntax parser | high |
| PowerShell command | parser/heuristic | high |
| Hostname | heuristic | medium |
| Outlook relevance | context/rule | medium |
| Root cause | not taxonomy | N/A |

Do not assign numerical confidence where deterministic true/false is more appropriate unless a unified API requires it.

---

# 92. Provenance Matrix

Produce a similar matrix:

| Item | Possible provenance |
|---|---|
| Entity | PARSER / USER / IMPORT |
| Tag | USER / RULE / AI_SUGGESTED |
| Category | USER / SYSTEM / IMPORT |
| Relationship | USER / SYSTEM / RULE |
| Normalized value | NORMALIZER |

---

# 93. Taxonomy Drift Risks

Identify risks such as:

```text
duplicate tags
near-synonyms
module-specific variants
uncontrolled custom tags
aliases treated as separate tags
categories reused as tags
statuses copied into tags
entities turned into tags
```

Define mitigations.

---

# 94. Example Drift Problem

Avoid:

```text
M365
Microsoft 365
Office 365
O365
Microsoft365
```

as separate analytics dimensions.

Use:

```text
Canonical:
Microsoft 365

Aliases:
M365
Office 365
O365
Microsoft365
```

---

# 95. Relationship Drift

Avoid:

```text
related
linked
associated
connects_to
has_relation
```

all meaning effectively the same thing.

Relationship vocabulary should be controlled.

---

# 96. Category Drift

Avoid creating categories just because a Tag exists.

Example:

```text
DNS
```

may be:

```text
Tag globally
Diagnostic category locally
```

This can be valid if semantics differ.

Document those differences explicitly.

---

# 97. Master Classification Decision Table

Produce a decision guide such as:

```text
Does this describe workflow state?
→ Status

Does this describe urgency?
→ Priority

Does this identify what kind of record it is?
→ Type / Kind

Does this represent a formal module classification?
→ Category

Is this a specific detected value?
→ Entity

Is this a reusable cross-module topic?
→ Tag

Does this connect two records?
→ Relationship

Is this calculated?
→ Metric / Insight
```

This should become one of the main outputs of Phase 0C.

---

# 98. Module-by-Module Classification Matrix

For each major module, identify which classification concepts apply.

Example:

| Module | Category | Type | Entity | Tag | Status | Relationship |
|---|---|---|---|---|---|---|
| Tickets | Yes | Yes | Yes | Yes | Yes | Yes |
| Clipboard | Maybe | Yes | Yes | Yes | Yes/retention state | Yes |
| KB | Yes | Yes | Yes | Yes | Yes | Yes |
| Diagnostics | Yes | Yes | Yes | Yes | Yes | Yes |
| Scripts | Maybe | Yes | Yes | Yes | Yes | Yes |
| Analytics | No | Metric type | Reads only | Reads only | N/A | Reads |
| Mochi | No | Message type | Reads | Reads | Interaction state | Reads |

Refine after inspection.

---

# 99. Database Impact Assessment

Do not design final SQL yet.

Instead identify likely structures required.

Potential:

```text
tag_families
tags
tag_aliases
tag_module_scopes

entity_types
entity_occurrences

module-specific tag link tables

relationship tables
```

Compare with existing schema.

Mark:

```text
REUSE
EXTEND
NEW
NOT NEEDED
NOT VERIFIED
```

---

# 100. Migration Principles

Future migrations must preserve:

```text
existing categories
existing ticket references
existing KB relationships
existing data integrity
existing analytics semantics
```

Do not silently convert existing categories to Tags.

Do not destroy historical taxonomy records.

---

# 101. Search Impact Assessment

Plan future query patterns.

Examples:

```text
Find everything tagged DNS.

Find clipboard items containing IPv4 entity 10.0.0.87.

Find open tickets tagged Outlook.

Find diagnostics with ERROR_CODE entity 0x80070005.

Find KB articles related to VPN.
```

The taxonomy architecture should support these without denormalized duplication.

---

# 102. Analytics Impact Assessment

Ensure future queries can answer:

```text
Top Tags
Top Entity Types
Top Error Codes
Tag Co-occurrence
Tags per Module
Diagnostic Coverage by Tag
KB Coverage by Tag
Ticket Resolution by Tag
```

Taxonomy storage should not be optimized solely for GUI display.

---

# 103. Mochi Context Impact

Mochi should receive:

```text
canonical keys
display labels where useful
normalized entity values
confidence
provenance where relevant
```

Mochi should not be required to reverse-engineer taxonomy from raw strings.

---

# 104. Settings Impact

Phase 0C must identify taxonomy-related settings that Phase 0D needs to support.

Examples:

```text
Enable automatic tag suggestions
Auto-assign deterministic tags
Show AI tag suggestions
User tag creation enabled
Maximum suggestions displayed
Sensitive entity redaction
```

Do not implement Settings here.

---

# 105. Required Diagrams

Produce conceptual Mermaid diagrams for:

## Classification Model

```text
Record
├── Type
├── Category
├── Status
├── Entities
├── Tags
└── Relationships
```

## Tag Architecture

```text
Tag Catalog
→ Modules
→ Analytics
```

## Entity Flow

```text
Raw Text
→ Parser
→ Entity Occurrence
→ Optional Canonical Resolver
```

## Cross-Module Relationships

Show Tickets, Clipboard, Diagnostics, KB, Scripts, Tags.

---

# 106. Required Taxonomy Inventory Deliverable

Produce a structured master inventory with sections:

```text
A. Category Scopes
B. Type / Kind Inventories
C. Entity Families
D. Entity Types
E. Tag Families
F. Initial System Tags
G. Statuses
H. Priorities
I. Relationship Types
J. Provenance Values
K. Confidence Rules
L. Alias Rules
M. Normalization Rules
```

Do not treat the inventory as final database seed data.

Mark entries:

```text
CORE
LIKELY
FUTURE
REJECTED
NEEDS REVIEW
```

---

# 107. Initial System Tag Inventory

Produce a proposed first-pass global System Tag catalog.

Keep it intentionally smaller than the universe of possible tags.

Prefer useful reusable concepts.

Potential domains:

```text
Microsoft 365
Outlook
Teams
Exchange Online
SharePoint
OneDrive
Entra ID
Intune
Defender
Purview

Windows
PowerShell
Active Directory
Group Policy
Windows Server

Networking
DNS
DHCP
VPN
Wi-Fi
Firewall
Proxy

Authentication
MFA
Password
Account Lockout
Conditional Access

Printing
Remote Desktop
Performance
Storage
Updates

Security
Phishing
Malware
Spam

Troubleshooting
Automation Candidate
Knowledge Gap
Recurring Issue
Training
Needs Review
```

Phase 0C should refine and reduce this list.

---

# 108. Avoid Over-Tagging

Do not create Tags for every noun.

Bad:

```text
Computer
User
Ticket
Error
Problem
Issue
Text
Command
```

unless they have a meaningful discovery or analytics use.

A Tag should earn its existence.

---

# 109. Tag Creation Criteria

A proposed system Tag should ideally satisfy one or more:

```text
useful across modules
useful for search
useful for filtering
useful for analytics
useful for automation rules
useful for knowledge discovery
```

Reject decorative Tags.

---

# 110. Entity Type Creation Criteria

An Entity Type should have:

```text
recognizable semantics
reliable detection or manual assignment
normalization rules
search value
workflow value
or analytics value
```

Avoid hyper-specific entity types with no practical use.

---

# 111. Relationship Type Creation Criteria

A relationship type should represent a meaningful semantic connection.

Not merely:

```text
RELATED
```

when a stronger term exists.

But also avoid creating dozens of overly narrow relationship types.

Balance semantic clarity and maintainability.

---

# 112. Open Questions

Only include architectural questions that inspection cannot answer.

Examples might include:

```text
Should global tags support hierarchy?
Should user-defined tag families be allowed?
Should detected entities persist by default?
Should Tags be attached to Companies/Contacts?
Should canonical entity resolution exist in MVP?
Should Tags support aliases across languages?
Should Categories remain completely separate from Tag catalog?
```

Do not ask questions merely because repository inspection was skipped.

---

# 113. Multilingual Consideration

F7Hub may eventually display taxonomy labels in English and French.

The plan should evaluate whether canonical keys should remain language-neutral:

```text
tag_key = account_lockout
```

while display labels may later support:

```text
English:
Account Lockout

French:
Verrouillage de compte
```

Do not implement localization yet.

Avoid encoding English display names as structural identifiers.

---

# 114. Bilingual Aliases

Evaluate whether search aliases may support:

```text
Account Lockout
Verrouillage de compte
```

without creating two canonical Tags.

This could become valuable for bilingual technician workflows.

---

# 115. Performance Considerations

Identify expected high-volume structures:

```text
entity occurrences
clipboard tags
capture relationships
search indexes
analytics queries
```

Plan indexing concepts without premature optimization.

---

# 116. Data Volume Considerations

Tags:

```text
low-volume catalog
```

Tag assignments:

```text
medium/high volume
```

Entity occurrences:

```text
potentially high volume
```

Analytics should not require scanning raw content unnecessarily.

---

# 117. Privacy and Analytics

Entity frequency analytics should prefer aggregation.

For example:

Useful:

```text
Error code 0x80070005 occurred 31 times.
```

Potentially inappropriate:

```text
john@contoso.com appeared 94 times.
```

unless specifically necessary.

The plan must distinguish operational search from analytics eligibility.

---

# 118. Retention Interaction

Detected entity occurrences tied to temporary Clipboard items may expire with the item.

Tags on durable records remain durable.

Analytics aggregates may outlive raw entity occurrences.

Document these lifecycle relationships.

---

# 119. Taxonomy Deactivation

When a Tag or classification becomes obsolete:

```text
deactivate
```

rather than deleting historical meaning.

Preserve existing relationships where appropriate.

---

# 120. Taxonomy Evolution

Define future process:

```text
Need identified
   ↓
Search existing taxonomy
   ↓
Alias existing concept?
   ↓
Extend existing?
   ↓
Create only if necessary
   ↓
Review analytics impact
   ↓
Document
```

Apply:

```text
SEARCH
IDENTIFY
REUSE / EXTEND
CREATE ONLY IF NECESSARY
```

---

# 121. Required Decision Register

At minimum decide or evaluate:

```text
Global Tags?
Tag Families?
Tag hierarchy?
User Tags?
Aliases?
Module scopes?
System vs User?
Entity type ownership?
Entity occurrence persistence?
Canonical entity resolution?
Confidence representation?
Provenance vocabulary?
Relationship architecture?
Category/Tag separation?
Type governance?
Multilingual labels?
```

For each provide:

```text
Decision
Options
Recommendation
Reason
Consequences
Status
```

Status:

```text
RECOMMENDED
REQUIRES_USER_DECISION
DEFERRED
NOT_VERIFIED
```

---

# 122. Required Risk Register

Include:

```text
taxonomy duplication
taxonomy drift
tag explosion
over-tagging
entity explosion
privacy leakage
ambiguous categories
relationship ambiguity
migration incompatibility
analytics fragmentation
bilingual synonym duplication
AI-generated taxonomy noise
weak normalization
cross-module coupling
```

Provide mitigation for each.

---

# 123. Planning Depth Classification

For every topic classify:

```text
DECIDE NOW
DESIGN NEXT
DEFER UNTIL FEATURE PLAN
DEFER UNTIL IMPLEMENTATION
```

Likely `DECIDE NOW`:

```text
Category vs Tag semantics
Entity vs Tag semantics
Global Tag catalog direction
Canonical key convention
Provenance concept
Relationship principles
```

Likely `DESIGN NEXT`:

```text
exact initial system tag inventory
entity taxonomy
tag aliases
normalization rules
```

Likely `DEFER`:

```text
every possible tag
every entity parser
AI auto-tagging
advanced graph visualization
```

---

# 124. Acceptance Criteria

Phase 0C is acceptable when:

1. Existing taxonomy architecture has been inspected.
2. Current categories have been inventoried.
3. Category, Type, Entity, Tag, Status, Priority, Relationship, Metric, and Insight are clearly distinguished.
4. A proposed global Entity Type inventory exists.
5. A proposed global Tag Family inventory exists.
6. A proposed initial System Tag inventory exists.
7. Tag aliases are defined conceptually.
8. Module scopes are defined conceptually.
9. System vs User Tags are defined.
10. Entity occurrence and canonical entity concepts are separated.
11. Normalization rules are defined conceptually.
12. Confidence rules are defined.
13. Provenance rules are defined.
14. Relationship semantics are defined.
15. Cross-module taxonomy use is mapped.
16. Search implications are mapped.
17. Analytics implications are mapped.
18. Privacy risks are addressed.
19. Mochi consumption rules are identified.
20. Settings requirements for Phase 0D are identified.
21. Database impact is assessed without implementing migrations.
22. Taxonomy drift risks have mitigations.
23. No production implementation has occurred.
24. Future Clipboard and Diagnostic plans can use this vocabulary without redefining it.

---

# 125. Validation

Return:

```text
Current taxonomy inspection          PASS / FAIL / BLOCKED
Existing category inventory          PASS / FAIL / BLOCKED
Classification vocabulary            PASS / FAIL / BLOCKED
Entity taxonomy                      PASS / FAIL / BLOCKED
Tag taxonomy                         PASS / FAIL / BLOCKED
Relationship model                   PASS / FAIL / BLOCKED
Normalization model                  PASS / FAIL / BLOCKED
Confidence/provenance model          PASS / FAIL / BLOCKED
Search impact review                 PASS / FAIL / BLOCKED
Analytics impact review              PASS / FAIL / BLOCKED
Privacy review                       PASS / FAIL / BLOCKED
Cross-module consistency review      PASS / FAIL / BLOCKED
Scope control                        PASS / FAIL / BLOCKED
Production changes                   MUST BE NONE
Database changes                     MUST BE NONE
```

---

# 126. Required Final Report

Return in this order:

## Summary

Recommended information architecture.

## Current-State Taxonomy

What already exists and how it currently works.

## Classification Vocabulary

Formal definitions.

## Classification Decision Tree

When to use Category, Type, Entity, Tag, Status, Priority, Relationship, Metric, or Insight.

## Category Architecture

Existing and recommended scope.

## Type / Kind Architecture

Per-domain type strategy.

## Entity Architecture

Families, types, normalization, occurrence model, resolution.

## Tag Architecture

Families, catalog, aliases, scopes, lifecycle, assignment.

## Relationship Architecture

Cross-module semantic links.

## Provenance & Confidence

Rules and ownership.

## Master Taxonomy Inventory

Categorized list marked CORE / LIKELY / FUTURE / NEEDS REVIEW.

## Module Classification Matrix

Which concepts each module uses.

## Search Impact

Expected query semantics.

## Analytics Impact

Dimensions and aggregation implications.

## Mochi Impact

How taxonomy becomes context.

## Settings Inputs

What Phase 0D must support.

## Database Impact Assessment

REUSE / EXTEND / NEW / NOT VERIFIED.

## Decision Register

Architectural decisions and unresolved choices.

## Risk Register

Taxonomy and data-quality risks.

## Recommended Next Planning Steps

Explicit downstream sequence.

## Result

Return exactly one:

```text
READY_FOR_SETTINGS_ARCHITECTURE
REQUIRES_TAXONOMY_DECISIONS
BLOCKED
```

Do not return:

```text
READY_FOR_IMPLEMENTATION
```

Phase 0C is still foundation architecture planning.

# Shared operational vocabulary

Context
Session
Action
Event
Result
Observation
Evidence
Diagnostic
Remediation
Validation
Resolution
Recommendation
Telemetry
Generated Output

The particularly valuable distinctions are:
Recommendation
≠ Action

Action
≠ Result

Result
≠ Resolution

Resolution
≠ Validation

Validation
≠ User Confirmation

Telemetry
≠ Ticket Evidence

The exact enum values such as:
pass
fail
partial

do not necessarily all belong globally yet.
The meaning of the concepts does.

---

# 127. Extension and sensitivity rules

## Extensible Vocabulary Requirement

0C must define the rules for extending F7Hub vocabulary without requiring
every future Tag, Entity Type, Category or Relationship Type to be known
before feature implementation.

Prefer:

stable vocabulary architecture
+
initial CORE vocabulary
+
controlled extension mechanism

over an exhaustive speculative dictionary.

Evaluate useful vocabulary classifications such as:

- CORE
- MODULE
- USER

Do not adopt these classifications without verifying that they fit the
existing taxonomy implementation.

Adding a new approved vocabulary entry through the established extension
mechanism is not automatically a Foundation architecture change.

Changing the meaning, identity, ownership or governance of a Foundation
taxonomy concept is a Foundation architecture change.

### Sensitive Values Are Not Tags

Do not use Tags as a convenient storage mechanism for:

- passwords
- tokens
- customer secrets
- credentials
- confidential free-form values

Named customers, users, devices, addresses and other concrete detected
values should be modeled according to Entity/reference-data rules rather
than converted into reusable Tags merely for convenience.

### Sensitivity Vocabulary

0C may define generic F7Hub sensitivity semantics where needed.

Do not invent or claim employer-specific legal, security or information
classification policy.

Future employer policy may be mapped onto F7Hub handling rules only when
that policy is actually known and authorized.

### Provenance

Taxonomy and Entity architecture should be capable of distinguishing
where information originated, such as:

- technician input
- local rule/parser
- F7Hub subsystem
- imported data
- external integration
- AI suggestion

Provider-specific provenance must not require Foundation taxonomy to be
redesigned every time a new integration is added.