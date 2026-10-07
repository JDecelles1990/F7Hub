# F7Hub Phase 1A
# Clipboard Domain & Data Lifecycle Architecture Planning Instructions
Clipboard Item vs Capture Event; raw/normalized content; hash/deduplication semantics; primary Kind; Entity occurrences; Tag assignments; sensitivity handling; secret detection; persistence boundaries; temporary/saved/pinned/evidence semantics; retention and expiration; cleanup rules; large-content policy; Ticket/Diagnostic/KB relationships; FTS/search requirements; Analytics facts; Mochi-safe context; transaction boundaries; failure/partial-processing rules.

Clipboard Invariants section
Before database design, I want explicit rules such as:
## Clipboard Domain Invariants

1. Repeated capture of identical content does not necessarily
   create another Clipboard Item.

2. Every genuine capture occurrence may create a Capture Event.

3. Transport retry must not create a second Capture Event.

4. Clipboard content remains untrusted.

5. Sensitive content is evaluated before normal persistence.

6. Entities do not automatically create canonical Companies,
   Contacts, Devices or Tickets.

7. Tags reference the global Tag Catalog.

8. Ticket evidence cannot disappear through ordinary temporary
   Clipboard cleanup.

9. Clipboard contextual actions do not execute arbitrary copied
   commands.

10. Analytics derives metrics from Clipboard facts rather than
    becoming Clipboard's source of truth.

These invariants become guardrails for every later Clipboard slice.


## Mode

`@ARCHITECT @PLAN`

Architecture and feature-domain planning only.

Do not implement production code.

Do not create SQLite migrations.

Do not create PySide6 screens.

Do not create AHK hotkeys.

Do not create IPC endpoints.

Do not create repositories or services.

Do not modify existing code.

Do not create PowerShell automation.

Do not implement Mochi behavior.

---

# 1. Objective

Design the F7Hub Clipboard Domain and complete Clipboard data lifecycle.

The result must define:

- what a Clipboard Item represents
- how captures differ from unique content
- what data is persisted
- how duplicate content is handled
- how content is classified
- how Entities are extracted
- how Tags are assigned
- how privacy/sensitivity is handled
- how retention works
- how temporary vs saved/pinned/evidence content differs
- how Clipboard records relate to Tickets, Diagnostics, KB, Scripts, Search, Analytics, and Mochi
- how large or unsupported clipboard content is handled
- how lifecycle transitions occur
- which data is operational vs analytical

The plan must be detailed enough that later implementation slices do not need to redefine the Clipboard domain.

---

# 2. Required Foundation Inputs

Before planning Clipboard, read the approved results from:

```text
Phase 0A
Master Foundation Architecture

Phase 0B
Global JSON / Interoperability Contract

Phase 0C
Classification / Taxonomy / Entity / Tag Architecture

Phase 0D
Settings / Configuration Architecture
```

Do not contradict approved foundation decisions silently.

If a contradiction is discovered:

```text
STOP THAT DESIGN THREAD
DOCUMENT THE CONFLICT
IDENTIFY REQUIRED ARCHITECTURE DECISION
```

Do not work around it.

---

# 3. Inspect Existing F7Hub Before Designing Clipboard

Inspect current implementation for:

```text
clipboard functionality
AHK clipboard hooks
hotkeys
search infrastructure
FTS5
ticket relationships
KB relationships
diagnostics
settings
taxonomy
tags
entities
repositories
services
database migrations
application bootstrap
logging
audit
background processing
```

Also inspect relevant documentation.

Classify findings as:

```text
FACT
ASSUMPTION
INFERENCE
RECOMMENDATION
NOT VERIFIED
```

---

# 4. Primary Clipboard Responsibility

Clipboard Center should answer:

```text
What did I capture?

What does it contain?

Where did it come from?

How often have I seen it?

What is it related to?

What can I safely do with it?

How long should it remain?
```

Clipboard Center is primarily an operational module.

It is not the Statistical Analytics module.

---

# 5. Clipboard Architecture Boundary

Preferred conceptual flow:

```text
Windows Clipboard
      ↓
Capture Adapter
      ↓
Interoperability Contract
      ↓
Clipboard Application Service
      ↓
Validation
      ↓
Sensitivity Check
      ↓
Normalization
      ↓
Classification
      ↓
Entity Extraction
      ↓
Deduplication
      ↓
Tagging
      ↓
Persistence
      ↓
Relationships / Actions
```

Each step must have a clear owner.

---

# 6. AHK Boundary

AHK may be responsible for:

```text
manual capture trigger
optional future automatic trigger
source application context
source window title
quick HUD interaction
sending clipboard content to F7Hub
receiving safe action results
```

AHK must not own:

```text
SQLite persistence
entity taxonomy
tag rules
retention logic
deduplication truth
ticket relationships
diagnostic business logic
```

---

# 7. Python Boundary

Python should likely own:

```text
contract validation
content validation
classification
normalization
entity extraction
sensitivity classification
deduplication
persistence orchestration
tag rules
relationship orchestration
search integration
```

Final ownership must match Phase 0A.

---

# 8. Clipboard Domain Concepts

Phase 1A must formally define at least:

```text
Clipboard Capture
Clipboard Item
Capture Event
Clipboard Content
Primary Kind
Entity Occurrence
Tag Assignment
Sensitivity
Retention Class
Clipboard Relationship
Clipboard Action
```

---

# 9. Clipboard Capture

A Capture represents:

```text
a single occurrence of content being captured
```

Example:

```text
14:31
Ctrl+Alt+C
PowerShell
Get-Service Spooler
```

If the same content is captured again at 14:40, that should usually be:

```text
another Capture Event
```

not automatically another unique Clipboard Item.

---

# 10. Clipboard Item

A Clipboard Item represents:

```text
the canonical F7Hub operational record
for a unique or deduplicated clipboard content payload
```

Example:

```text
Clipboard Item #901

Content:
Get-Service Spooler

First seen:
14:31

Last seen:
17:22

Capture count:
8
```

---

# 11. Capture Event vs Clipboard Item

This distinction must be explicit.

```text
Clipboard Item
    │
    ├── Capture Event #1
    ├── Capture Event #2
    ├── Capture Event #3
    └── Capture Event #4
```

Benefits:

```text
deduplication
capture-frequency statistics
source history
storage efficiency
retention flexibility
```

---

# 12. Required Deduplication Decision

Define what makes two captures the same Clipboard Item.

Potential basis:

```text
normalized content
+
content format
```

using a stable content hash.

Example:

```text
SHA-256(normalized content)
```

Do not finalize algorithm without evaluating:

```text
exact-text semantics
whitespace
line endings
Unicode normalization
case sensitivity
URLs
commands
logs
structured data
```

---

# 13. Raw vs Normalized Content

Preserve both concepts.

```text
raw_text
```

represents captured evidence.

```text
normalized_text
```

supports:

```text
search
deduplication
classification
comparison
```

Normalization must not destroy important evidence.

---

# 14. Normalization Rules

Evaluate normalization for:

```text
CRLF / LF
trailing whitespace
leading whitespace
Unicode normalization
repeated blank lines
NUL characters
```

Do not casually normalize:

```text
case
URL query strings
PowerShell syntax
file paths
JSON formatting
```

where meaning may change.

---

# 15. Content Hash

Define semantics.

Potential:

```text
content_hash =
SHA-256(
    format identifier
    +
    canonical normalized content
)
```

Determine whether:

```text
text/plain
```

must be part of the hash input.

---

# 16. Collision Handling

SHA-256 collision risk is negligible, but architecture should not treat hash equality as proof without considering whether:

```text
normalized content
```

should also be compared before merging records.

Recommend a safe approach.

---

# 17. Content Formats

MVP should likely focus on:

```text
text/plain
```

Evaluate future support for:

```text
text/html
file lists
images
RTF
binary clipboard formats
```

Do not design binary storage deeply yet.

---

# 18. MVP Boundary

Recommended initial Clipboard scope:

```text
text only
manual capture
Python classification
SQLite persistence
deduplication
entities
tags
search
retention
relationships
PySide6 management later
```

Explicitly out of initial scope:

```text
images
files copied as binary
OCR
automatic AI analysis
cloud synchronization
full clipboard manager replacement
unlimited history
```

---

# 19. Primary Kind

Each Clipboard Item should have one primary content Kind.

Examples to evaluate:

```text
plain_text
mixed_text
url
powershell_command
powershell_output
powershell_error
error_message
log
json
xml
yaml
csv
markdown
ticket_data
unknown
```

Phase 0C owns the canonical vocabulary.

Phase 1A defines how Clipboard uses it.

---

# 20. Mixed Content

Large pasted troubleshooting notes may contain several Entity Types simultaneously.

Example:

```text
User john@contoso.com
Device PC-1042
IP 10.0.0.87
Error 0x80070005
Get-Service Spooler
```

Primary Kind could be:

```text
mixed_text
```

while Entities preserve detailed structure.

Do not force one Entity Type to define the entire Clipboard Item.

---

# 21. Entity Occurrences

Clipboard Entity Occurrences should reference:

```text
clipboard item
entity type
raw value
normalized value
start offset
end offset
confidence
provenance
optional metadata
```

Exact persistence design must align with Phase 0C.

---

# 22. Offset Semantics

If storing:

```text
start_offset
end_offset
```

define whether offsets refer to:

```text
raw_text
```

or:

```text
normalized_text
```

Preferred default:

```text
raw_text
```

for UI highlighting and evidence fidelity.

Document this explicitly.

---

# 23. Entity Extraction Pipeline

Potential flow:

```text
Raw text
   ↓
Deterministic parsers
   ↓
Regex / format recognizers
   ↓
Domain heuristics
   ↓
Entity normalization
   ↓
Optional contextual classification
   ↓
Persist occurrences
```

AI should not be required for baseline Entity extraction.

---

# 24. Entity Extraction Order

Order may matter.

Example:

```text
URL
```

may contain:

```text
domain
port
IP
```

Decide whether nested Entities are allowed.

Example:

```text
https://10.0.0.87:443/test
```

could produce:

```text
URL
IPV4
PORT
```

This may be desirable.

Document overlap rules.

---

# 25. Entity De-duplication Within an Item

Example:

```text
10.0.0.87 appears 4 times
```

Decide whether to store:

```text
4 Entity Occurrences
```

or:

```text
1 Entity + occurrence count
```

For source highlighting, separate occurrences may be useful.

Evaluate storage implications.

---

# 26. Tags

Clipboard Items may have:

```text
manual tags
rule-based tags
suggested tags
```

Examples:

```text
PowerShell
DNS
Networking
Outlook
Troubleshooting
```

Tag definitions remain owned by the global Tag Catalog.

Clipboard only owns assignments.

---

# 27. Tag Assignment Timing

Determine whether tags are evaluated:

```text
during initial processing
after Entity extraction
after relationships are known
on user request
```

Likely:

```text
initial deterministic tags
    ↓
optional context-aware suggestions later
```

---

# 28. Clipboard Sensitivity

Every captured item should be evaluated for sensitivity before normal persistence.

Potential classes from foundation architecture may include:

```text
normal
personal
confidential
secret_possible
blocked
```

Use approved Phase 0 terminology.

---

# 29. Secret Handling

Clipboard may contain:

```text
password
MFA code
API key
Bearer token
private key
connection string
secret
```

Define safe behavior.

Potential:

```text
capture received
     ↓
secret detector
     ↓
SECRET_POSSIBLE
     ↓
do not persist raw content automatically
```

Possible alternatives:

```text
discard
memory-only
redacted persistence
quarantine
manual override
```

Require explicit recommendation.

---

# 30. Privacy Before Classification

Sensitivity detection may need to happen before:

```text
logging
Mochi
analytics
persistent storage
external AI
```

This ordering must be explicit.

---

# 31. Retention Classes

Design a clear lifecycle taxonomy.

Potential:

```text
TEMPORARY
RECENT
SAVED
PINNED
EVIDENCE
```

These are retention/lifecycle concepts.

Do not model them as Tags.

---

# 32. Temporary

Potential semantics:

```text
default captured content
expires automatically
not manually preserved
```

Example default candidate:

```text
24 hours
```

Actual value comes from Settings.

---

# 33. Recent

Potential semantics:

```text
captured history still available
eligible for routine cleanup
```

Example candidate:

```text
7 days
```

Clarify difference between:

```text
TEMPORARY
RECENT
```

or decide that both are not needed.

Avoid redundant lifecycle states.

---

# 34. Saved

User explicitly preserves content.

Example:

```text
Save
```

means:

```text
do not expire through normal temporary retention
```

Define whether saved records still have policy-based retention.

---

# 35. Pinned

Pinned may mean:

```text
important saved item
easy access
persistent
```

Determine whether:

```text
PINNED
```

is a retention class or an independent property.

Example:

```text
is_pinned
+
retention_class = SAVED
```

may be cleaner than:

```text
retention_class = PINNED
```

Phase 1A must recommend one.

---

# 36. Evidence

If Clipboard content is linked as evidence to a Ticket or Diagnostic:

```text
it should not disappear merely because temporary history expired
```

Define evidence retention semantics.

Potential:

```text
linked evidence inherits related-record lifecycle
```

or:

```text
explicit EVIDENCE retention class
```

Evaluate carefully.

---

# 37. Retention Precedence

Define rules.

Example:

```text
temporary + no references
→ eligible for deletion

temporary + ticket evidence link
→ preserve

saved
→ preserve

pinned
→ preserve

secret_possible
→ do not persist unless explicitly permitted
```

Create a deterministic precedence model.

---

# 38. Retention Policy vs Retention State

Settings may define:

```text
temporary retention = 24h
recent retention = 7d
```

Clipboard domain defines:

```text
whether a record is eligible for deletion
```

These are distinct responsibilities.

---

# 39. Cleanup Process

Plan a background or scheduled cleanup responsibility.

Potential flow:

```text
Find expired candidates
       ↓
Check preservation conditions
       ↓
Check ticket links
       ↓
Check diagnostic links
       ↓
Check saved/pinned state
       ↓
Delete eligible records
       ↓
Record aggregate metrics if needed
```

Do not implement scheduler yet.

---

# 40. Cascade Behavior

If a Clipboard Item is deleted, decide what happens to:

```text
capture events
entities
tag assignments
search index
relationships
```

Likely child records should cascade.

But related external records must remain intact.

Example:

```text
delete clipboard item
```

must not delete:

```text
Ticket
Diagnostic
KB Article
```

---

# 41. Evidence Deletion

If evidence is linked to a Ticket, deletion may require:

```text
unlink first
```

or explicit confirmation.

Plan safety behavior.

---

# 42. Capture Event Retention

Capture Events may have shorter retention than Clipboard Items.

Example:

```text
Clipboard Item preserved for 90 days
Capture history only 14 days
```

This can reduce volume while keeping useful content.

Evaluate whether useful.

---

# 43. Aggregate Preservation

Statistical Analytics may need historical activity after raw capture events expire.

Possible:

```text
daily aggregated metrics
```

such as:

```text
capture_count
unique_item_count
duplicate_count
entity_type_count
```

Analytics design comes later.

Phase 1A must identify which raw facts are safe to delete after aggregation.

---

# 44. Clipboard Storage Size

Establish content size classes.

Potential planning values:

```text
Small
≤ 256 KB

Medium
256 KB to 2 MB

Large
> 2 MB
```

These are only candidate thresholds.

Phase 1A must recommend values or explicitly defer them to Settings.

---

# 45. Large Content Behavior

Potential policy:

```text
small
→ normal processing

medium
→ process but warn / explicit persistence

large
→ preview + metadata only unless explicitly saved
```

Do not blindly persist huge logs.

---

# 46. Preview Text

A Clipboard Item may store:

```text
preview_text
```

for fast GUI display.

Define:

```text
max preview length
generation rules
newline handling
```

Do not use preview as canonical content.

---

# 47. Unsupported Content

If clipboard format is unsupported:

```text
capture event may still be acknowledged
```

but response should clearly state:

```text
UNSUPPORTED_CONTENT_TYPE
```

No silent failure.

---

# 48. URLs

URLs should remain Clipboard Items.

Do not create a separate canonical URL history subsystem unless required.

Instead:

```text
Clipboard Item
kind = url
```

plus extracted:

```text
URL
DOMAIN
HOST
PORT
```

where applicable.

---

# 49. Clipboard URLs View

Future Clipboard Center can expose:

```text
URLs
```

as a filtered view.

Not a duplicate table.

---

# 50. PowerShell Commands

Similarly:

```text
PowerShell
```

view should usually be:

```text
Clipboard Items
filtered by Kind / Entity / Tag
```

not a second storage system.

---

# 51. Errors & Logs

Same principle:

```text
Errors & Logs
```

is a view of canonical Clipboard Items.

Avoid separate silos.

---

# 52. Networking View

Potential filter:

```text
Tag = Networking
OR
Entity Type in:
ipv4
ipv6
fqdn
domain
cidr
mac_address
port
```

Exact semantics belong to the GUI/search planning later.

---

# 53. Relationships

Clipboard Items may link to:

```text
Ticket
Diagnostic Session
KB Article
Script
Automation
```

Each relationship requires clear semantics.

---

# 54. Clipboard → Ticket

Example:

```text
Clipboard Item #901
EVIDENCE_FOR
Ticket #41872
```

This relationship should preserve:

```text
created_at
created_by/provenance
optional note
```

if justified.

---

# 55. Clipboard → Diagnostic

Clipboard may be:

```text
INPUT_TO
Diagnostic Session
```

or:

```text
EVIDENCE_FOR
Diagnostic Session
```

Those are not necessarily identical.

Define semantics.

---

# 56. Clipboard → KB

Potential relationship:

```text
SOURCE_FOR
KB Draft
```

or:

```text
RELATED_TO
KB Article
```

Avoid vague link types when stronger semantics exist.

---

# 57. Clipboard → Script

Example:

```text
Clipboard command
RELATED_TO
approved PowerShell Script
```

Do not automatically treat copied PowerShell as an approved executable script.

---

# 58. Clipboard → Automation

Potential:

```text
source data
trigger context
```

But Clipboard content itself should never become arbitrary executable automation.

---

# 59. Clipboard Actions

Clipboard actions should be contextual.

Examples:

For IPv4:

```text
Ping
DNS lookup
Search Tickets
Run Network Diagnostic
Attach to Ticket
```

For URL:

```text
Open
Search KB
Save
Attach to Ticket
```

For PowerShell command:

```text
Search Script Registry
Save Snippet
Search KB
Explain
```

Do not automatically execute copied commands.

---

# 60. Action Registry

Evaluate whether Clipboard contextual actions should map to approved application action keys.

Example:

```text
clipboard.action.ping
clipboard.action.search_ticket
clipboard.action.run_diagnostic
```

Exact action architecture may be designed in Phase 1B/1C.

---

# 61. Classification vs Action Availability

An Entity or Kind may make an action available.

Example:

```text
Entity Type = ipv4
→ DNS Lookup available
```

This is not the same as automatically running the action.

---

# 62. Manual Capture

MVP recommended entry point:

```text
explicit hotkey
```

such as:

```text
Ctrl+Alt+C
```

subject to Phase 1B hotkey planning.

Manual capture offers:

```text
predictability
privacy
lower data volume
simpler testing
```

---

# 63. Automatic Capture

Treat automatic monitoring as a later capability.

Before implementing it, plan:

```text
privacy
application exclusions
secret filtering
rate limits
deduplication
performance
retention
```

Do not enable by default during early Clipboard implementation.

---

# 64. Source Application Context

Capture metadata may include:

```text
source_application
source_window_title
capture_method
timestamp
```

Optional future:

```text
source_url
```

only when safely available.

---

# 65. Window Title Privacy

Window titles may contain:

```text
names
ticket numbers
email subjects
customer data
```

Decide whether full titles should be persisted.

Potential strategy:

```text
store
redact
truncate
hash
memory-only
```

based on privacy policy.

---

# 66. Source URL

Capturing browser URLs may introduce privacy issues.

Do not automatically persist URL context unless explicitly designed.

This differs from the clipboard content itself being a URL.

---

# 67. Capture Method

Canonical values may include:

```text
AHK_MANUAL
AHK_AUTOMATIC
F7HUB
IMPORT
```

Use approved naming conventions from Phase 0B.

---

# 68. Classification Failure

If classification fails:

```text
do not lose the capture
```

where safe.

Potential:

```text
primary_kind = unknown
```

with processing error recorded separately.

---

# 69. Partial Processing

Example:

```text
classification succeeded
entity parser failed
```

Define whether the Clipboard Item can still persist.

Prefer graceful degradation.

---

# 70. Processing Status

Consider whether Clipboard Items need processing state:

```text
PENDING
PROCESSED
PARTIAL
FAILED
```

or whether that belongs to processing jobs/events instead.

Avoid adding workflow state unnecessarily.

---

# 71. Item State

Potential item lifecycle state:

```text
ACTIVE
REDACTED
QUARANTINED
EXPIRED
```

Evaluate whether these are required.

Avoid duplicating retention state.

---

# 72. Sensitivity vs State

Example:

```text
sensitivity = secret_possible
state = quarantined
```

These describe different things.

One is classification.

One is lifecycle behavior.

---

# 73. Redaction

Define whether redacted Clipboard Items preserve:

```text
content hash
metadata
entity summary
```

without raw content.

Potentially useful for:

```text
audit
deduplication
aggregate counts
```

but privacy must take priority.

---

# 74. Clipboard Search

Clipboard Center should support later search by:

```text
content
preview
kind
tag
entity type
entity value
source application
ticket relationship
date
sensitivity
```

Architecture should support these queries.

---

# 75. FTS5

Evaluate FTS5 for:

```text
normalized_text
preview_text
```

possibly using external-content tables and project conventions.

Do not finalize SQL yet.

Inspect current FTS usage.

---

# 76. Exact Entity Search

Entity lookup should generally not depend on FTS.

Use indexed structured fields for:

```text
entity_type
normalized_value
```

Example:

```text
IPv4 = 10.0.0.87
```

should be an exact structured query.

---

# 77. Tag Search

Tag filtering should use canonical:

```text
tag_id
```

relationships.

Do not search raw text for the word `DNS` and call that a Tag match.

---

# 78. Clipboard Analytics Boundary

Clipboard domain may expose operational facts:

```text
captured_at
content hash
kind
entity types
tags
source
relationships
```

Statistical Analytics derives:

```text
daily capture volume
duplicate rate
top tags
top entity types
source application trends
```

Clipboard should not store every derived metric directly.

---

# 79. Duplicate Analytics

Because Capture Events are separate from Items:

```text
captures = 100
unique items = 62
duplicates = 38
```

can be calculated accurately.

This is one major reason to preserve capture occurrences separately.

---

# 80. Source Application Analytics

Future analytics may calculate:

```text
PowerShell   32%
Outlook      19%
Edge         18%
HaloPSA      15%
```

Ensure Capture Event metadata is sufficient.

Respect privacy.

---

# 81. Clipboard → Ticket Analytics

Potential metric:

```text
Percentage of Clipboard Items later attached as evidence
```

Requires explicit relationship timestamps.

---

# 82. Clipboard → Diagnostic Analytics

Potential:

```text
Clipboard items that led to diagnostics
```

Again requires relationship/event data, not inference from raw content.

---

# 83. Automation Opportunity Analytics

Future Analytics may notice:

```text
Get-MessageTrace
captured 47 times
```

and suggest:

```text
Automation Candidate
```

Clipboard should record facts.

Analytics interprets them.

---

# 84. Mochi Context

Mochi should receive curated Clipboard context.

Potential:

```text
item kind
preview
selected entities
tags
relationships
sensitivity-safe text
```

Mochi should not automatically receive:

```text
entire raw history
secret content
large logs
```

---

# 85. Mochi Context Service

ClipboardService should not depend directly on Mochi.

Preferred:

```text
Clipboard
    ↓
Context Service
    ↓
Mochi
```

This avoids circular coupling.

---

# 86. Ticket Context

Likewise:

```text
Clipboard Item
```

may reference a Ticket.

Clipboard should not become a Ticket business service.

Ticket validation belongs to the appropriate service boundary.

---

# 87. Database Domain Inventory

Without writing SQL, evaluate likely persistence objects:

```text
clipboard_items
clipboard_capture_events
clipboard_entities
clipboard_item_tags
clipboard_ticket_links
clipboard_diagnostic_links
```

Potential additional links:

```text
clipboard_kb_links
clipboard_script_links
```

Only add when justified.

---

# 88. Clipboard Items Conceptual Fields

Evaluate:

```text
clipboard_item_id
primary_kind
content_hash
raw_text
normalized_text
preview_text
content_size_bytes
sensitivity
retention_class
state
first_seen_at
last_seen_at
occurrence_count
expires_at
is_pinned
created_at
updated_at
```

Do not assume all are required.

Recommend minimal durable model.

---

# 89. Occurrence Count

If capture events exist, `occurrence_count` is technically derivable.

Evaluate:

```text
derive dynamically
```

versus:

```text
denormalized cached count
```

Prefer normalized design unless performance justifies denormalization.

---

# 90. First/Last Seen

Similarly evaluate whether:

```text
first_seen_at
last_seen_at
```

should be stored or derived.

Potential benefit:

```text
fast GUI query
```

Potential cost:

```text
denormalized state
```

Recommend based on expected usage.

---

# 91. Capture Event Fields

Evaluate:

```text
capture_event_id
clipboard_item_id
captured_at
source_application
source_window_title
capture_method
requested_action
```

Optional:

```text
source_url
session_id
```

only if justified.

---

# 92. Clipboard Entity Fields

Evaluate:

```text
clipboard_entity_id
clipboard_item_id
entity_type_id
raw_value
normalized_value
confidence
start_offset
end_offset
provenance
metadata_json
```

Use Phase 0C vocabulary.

---

# 93. JSON Metadata

Avoid using:

```text
metadata_json
```

as an excuse to avoid schema design.

Use it only for genuinely variable Entity-specific metadata.

Stable queryable facts should use proper columns or relations.

---

# 94. Tag Relationship Fields

Potential:

```text
clipboard_item_id
tag_id
assignment_source
confidence
assigned_at
```

Do not duplicate Tag display names.

---

# 95. Link Table Principles

Dedicated links provide:

```text
foreign-key integrity
query clarity
domain semantics
```

Prefer them over generic polymorphic links where practical.

---

# 96. Deletion Safety

Clipboard deletion should evaluate:

```text
saved?
pinned?
evidence?
linked?
sensitive?
```

before destruction.

User-facing delete may mean:

```text
remove from Clipboard history
```

not necessarily:

```text
erase all referenced evidence
```

Define semantics.

---

# 97. Soft Delete vs Hard Delete

Evaluate whether Clipboard needs soft deletion.

Potential reasons:

```text
undo
audit
linked evidence
```

Potential drawbacks:

```text
privacy
storage
complexity
```

Do not automatically use soft delete.

For privacy-sensitive clipboard data, hard deletion may actually be preferable.

---

# 98. Expiration

Expiration should be deterministic.

Potential:

```text
expires_at
```

calculated when:

```text
item created
retention state changes
settings change
```

Define whether settings changes recalculate existing expiry.

---

# 99. Settings Changes and Existing Items

Example:

```text
retention changes from 30 days to 7 days
```

Should existing items:

```text
immediately adopt 7 days?
keep original expiry?
```

This requires explicit policy.

Recommend one.

---

# 100. Recommended Principle

Likely safer:

```text
existing items retain calculated expiration
unless a specific cleanup-policy change
explicitly says otherwise
```

This avoids surprising mass deletion.

Phase 1A should evaluate.

---

# 101. Pinning Behavior

Pin:

```text
sets is_pinned
```

and likely preserves item.

Unpin:

```text
returns item to previous/default retention policy
```

Need to define whether previous retention class is remembered.

---

# 102. Saving Behavior

Define difference between:

```text
Save
Pin
Attach as Evidence
```

Possible model:

```text
Save
→ persistent operational item

Pin
→ saved + surfaced prominently

Evidence
→ preserved due to relationship
```

This model may be cleaner than treating them as interchangeable states.

---

# 103. Recommended Retention Dimensions

Consider separating:

```text
retention_class
is_pinned
evidence_reference_count
```

rather than one overloaded enum.

This should be evaluated formally.

---

# 104. Processing Pipeline Order

Recommend and validate a canonical order such as:

```text
1. Receive contract
2. Validate envelope
3. Validate content
4. Enforce size limit
5. Detect sensitivity
6. Apply safe normalization
7. Compute hash
8. Detect primary kind
9. Extract entities
10. Normalize entities
11. Resolve existing Clipboard Item
12. Record capture event
13. Assign deterministic tags
14. Calculate retention
15. Persist
16. Generate available actions
17. Return result
```

Check if sensitivity should occur before hashing or normalization.

Document final order.

---

# 105. No AI Requirement

MVP classification must work without:

```text
OpenAI
cloud API
local LLM
```

Use deterministic methods first.

---

# 106. Classifier Architecture

Evaluate components such as:

```text
ClipboardClassifier
EntityExtractor
SensitivityClassifier
ClipboardNormalizer
ClipboardDeduplicator
TagRuleEvaluator
```

Do not implement classes.

Use responsibilities to guide later service design.

---

# 107. Repository Architecture

Potential responsibilities:

```text
ClipboardRepository
    create/get item
    resolve by hash
    update lifecycle
    search
    manage capture occurrences
```

Actual APIs should follow existing repository conventions.

---

# 108. Service Architecture

Potential:

```text
ClipboardService
ClipboardClassificationService
ClipboardRetentionService
```

Avoid excessive service fragmentation.

Recommend the smallest maintainable set.

---

# 109. Background Processing

Evaluate whether initial processing should be:

```text
synchronous
```

for small manual captures.

Potential later:

```text
background worker
```

for large logs or automatic capture.

Do not introduce background infrastructure without demonstrated need.

---

# 110. User Feedback

Manual capture should return promptly with:

```text
captured
classified
saved
blocked
unsupported
error
```

Quick HUD behavior comes in Phase 1B.

Phase 1A defines result semantics only.

---

# 111. Contract Inputs

Identify exact Phase 0B contracts Clipboard will use.

Potential:

```text
clipboard.capture
clipboard.process
clipboard.result
```

Do not redesign the common envelope.

Only define Clipboard-specific payload requirements.

---

# 112. Contract Outputs

Clipboard result may need:

```text
clipboard_item_id
primary_kind
sensitivity
entities
tags
available_actions
retention summary
duplicate status
```

Determine which fields belong in the immediate response.

---

# 113. Duplicate Response

If content already exists:

```text
duplicate = true
existing_item_id = 901
capture_event_created = true
```

may be useful.

Avoid telling AHK to infer this from database state.

---

# 114. Error Cases

Plan structured outcomes for:

```text
empty clipboard
unsupported format
payload too large
secret blocked
invalid contract
classification failure
database failure
tagging failure
entity parser failure
relationship failure
```

Define which are:

```text
fatal
recoverable
partial
```

---

# 115. Partial Failure

Example:

```text
Clipboard item saved
but tag suggestion failed
```

This should probably not cause the entire capture to be rolled back.

Define transactional boundaries.

---

# 116. Transaction Scope

Potential atomic core:

```text
Clipboard Item
+
Capture Event
+
Entity Occurrences
+
deterministic Tag Assignments
```

But evaluate whether long-running classification should occur before transaction start.

Avoid holding SQLite write locks while performing expensive parsing.

---

# 117. Suggested Persistence Flow

Potential:

```text
Classify in memory
      ↓
Begin transaction
      ↓
Resolve/create item
      ↓
Insert capture event
      ↓
Insert entities
      ↓
Insert tags
      ↓
Commit
```

Validate against existing database architecture.

---

# 118. Post-Commit Actions

Actions such as:

```text
search KB
run diagnostic
notify Mochi
```

should not occur inside core persistence transactions.

---

# 119. Database Failure

If persistence fails:

```text
do not report success
```

AHK/PySide6 should receive structured failure.

Manual clipboard content itself remains in the Windows clipboard, so retry may be possible.

---

# 120. Retry Semantics

Define safe retries.

If same:

```text
message_id
```

is retried, avoid double Capture Events unless protocol says it represents a new capture.

Distinguish:

```text
transport retry
```

from:

```text
new user capture
```

This is important.

---

# 121. Idempotency

Potential:

```text
message_id
```

for transport idempotency.

Content hash handles:

```text
content deduplication
```

These are different concepts.

Document explicitly.

---

# 122. Search Result Identity

Clipboard GUI must always operate on:

```text
clipboard_item_id
```

not content hashes or preview text.

---

# 123. Bilingual Content

Clipboard content may be:

```text
English
French
mixed
```

Entity extraction should not assume English-only content where avoidable.

Technical syntax detection is often language-independent.

---

# 124. Unicode

Clipboard must safely support:

```text
French accents
Unicode symbols
non-ASCII paths
smart quotes
emoji
```

Contract and database encoding should preserve them.

---

# 125. Line Endings

Windows capture likely uses:

```text
CRLF
```

but processing may normalize to:

```text
LF
```

for deduplication.

Raw evidence should preserve original text or clearly documented normalization.

---

# 126. Clipboard History Size

Define expected planning scenarios.

Example:

```text
1,000 items
10,000 items
100,000 capture events
```

Evaluate indexing needs.

Do not assume infinite growth.

---

# 127. Query Patterns

Expected frequent queries:

```text
recent items
items by Kind
items by Tag
items by Entity
pinned items
saved items
URLs
ticket-linked items
diagnostic-linked items
search text
expired candidates
```

Indexes should be planned around real query patterns.

---

# 128. Privacy Query

Operations such as:

```text
show sensitive items
```

should require deliberate filters.

Do not make sensitive content prominent by default.

---

# 129. Clipboard Center Navigation Model

Phase 1A should define the data semantics behind future views:

```text
Recent
Saved
Pinned
URLs
Commands
PowerShell
Errors & Logs
Networking
Ticket Evidence
Diagnostic Evidence
Mixed Content
```

These should be query views, not duplicate storage.

---

# 130. Smart Filters

Potential:

```text
Sensitive
Large Items
Unlinked
This Week
```

Again, views/filters only.

---

# 131. Inspector Data

Future Clipboard Inspector may need:

```text
summary
content
entities
capture history
relationships
retention
privacy
actions
tags
```

Phase 1A defines data availability.

Phase 1C designs actual GUI.

---

# 132. Statistical Analytics Inputs

Explicitly document what Clipboard exposes to future Analytics.

Potential:

```text
capture timestamp
unique item identity
kind
entity types
tags
source application
size
sensitivity class
duplicate state
relationships
retention outcome
```

Avoid exporting raw content by default.

---

# 133. Analytics Privacy

Aggregate:

```text
entity type count
```

not necessarily:

```text
specific email-address frequency
```

Define analytics eligibility by Entity Type.

---

# 134. Mochi Inputs

Explicitly document safe Clipboard context fields available to Mochi.

Potential:

```text
selected item ID
primary kind
redacted preview
safe entities
tags
relationships
suggested actions
```

Raw content may require:

```text
sensitivity check
user action
```

---

# 135. Diagnostic Inputs

Clipboard should be able to supply:

```text
selected Entity
selected content
context references
```

to DiagnosticService.

Example:

```text
IPV4 = 10.0.0.87
```

→ candidate input to:

```text
network diagnostic
```

DiagnosticService remains responsible for validation.

---

# 136. Ticket Inputs

Attach as evidence should reference:

```text
clipboard_item_id
ticket_id
```

through appropriate application service logic.

Clipboard should not write ticket internals directly.

---

# 137. KB Inputs

Create KB Draft may derive content from Clipboard.

But:

```text
Clipboard content
```

should not automatically become published knowledge.

Possible flow:

```text
Clipboard
→ Create Draft
→ KB Service
→ user review
```

---

# 138. Script Inputs

Copied PowerShell may be offered to:

```text
Search Script Registry
```

or:

```text
Save Snippet
```

but never automatically promoted to approved automation.

---

# 139. Audit

Determine which Clipboard actions should be auditable.

Potential:

```text
attach evidence
manual save
manual delete
sensitivity override
export
```

Routine captures may not need heavy audit.

---

# 140. Logging

Safe logs may include:

```text
message_id
clipboard_item_id
kind
size
status
duration
entity count
tag count
```

Avoid logging raw clipboard content.

---

# 141. Performance Measurements

Later implementation should measure:

```text
classification latency
entity extraction latency
database persistence latency
search latency
FTS indexing latency
cleanup duration
```

Do not optimize blindly.

---

# 142. Target UX Latency

Manual text capture should feel near-immediate.

Phase 1A should recommend performance targets.

Example candidates:

```text
small text classification < 100 ms
overall manual capture < 250 ms
```

Do not turn aspirational values into claims.

Mark them as targets.

---

# 143. Large Log Processing

Large logs may require:

```text
deferred entity extraction
```

later.

Do not burden MVP architecture unless necessary.

---

# 144. Extension Strategy

Clipboard architecture should later permit:

```text
image metadata
file-list capture
OCR results
structured log parsing
```

without implementing them now.

---

# 145. Out of Scope

Explicitly exclude from Phase 1A:

```text
final PySide6 layouts
AHK implementation
hotkey registration
IPC transport implementation
PowerShell diagnostics
Statistical Analytics GUI
Mochi conversation engine
AI API integration
OCR
binary clipboard storage
cloud sync
automatic remediation
```

---

# 146. Required Domain Model Diagram

Produce a conceptual diagram showing:

```text
ClipboardItem
     │
     ├── CaptureEvents
     ├── EntityOccurrences
     ├── TagAssignments
     ├── TicketLinks
     └── DiagnosticLinks
```

Include optional KB/Script links only if justified.

---

# 147. Required Lifecycle Diagram

Produce:

```text
Captured
   ↓
Validated
   ↓
Sensitivity Checked
   ↓
Classified
   ↓
Deduplicated
   ↓
Persisted
   ↓
Recent
   ├── Saved
   ├── Pinned
   ├── Evidence
   └── Expired
```

Refine according to recommended retention semantics.

---

# 148. Required Processing Sequence Diagram

Show:

```text
AHK / PySide6
     ↓
Contract Validator
     ↓
ClipboardService
     ↓
Classifiers
     ↓
Repository
     ↓
SQLite
     ↓
Result
```

---

# 149. Required Retention Decision Table

Example format:

| State | Linked | Pinned | Saved | Expired? | Delete? |
|---|---:|---:|---:|---:|---:|
| Temporary | No | No | No | Yes | Yes |
| Temporary | Ticket | No | No | Yes | No |
| Saved | No | No | Yes | N/A | No |
| Saved | No | Yes | Yes | N/A | No |

Refine with actual recommended model.

---

# 150. Required Content Size Matrix

Example:

| Size | Process | Persist | Entity Extraction | UX |
|---|---|---|---|---|
| Small | Full | Yes | Full | Immediate |
| Medium | Full/limited | Maybe | Full/limited | Warning |
| Large | Metadata/preview | Explicit | Deferred | Prompt |

Recommend thresholds or mark them configurable.

---

# 151. Required Failure Matrix

Cover:

```text
invalid contract
empty clipboard
unsupported format
oversize
secret
classifier failure
entity parser failure
database failure
FTS failure
tagging failure
relationship failure
```

For each define:

```text
fatal?
persist?
retryable?
user message?
log severity?
```

---

# 152. Required Privacy Matrix

At minimum cover:

```text
normal text
email address
device name
file path
URL
password-like string
API key
MFA code
private key
large customer log
```

For each recommend:

```text
persist?
redact?
analytics?
Mochi?
search?
```

---

# 153. Required Entity Extraction Inventory

Using Phase 0C taxonomy, mark Clipboard Entity Types:

```text
MVP
LATER
NOT APPLICABLE
```

Likely MVP candidates:

```text
ipv4
ipv6
email
upn
hostname
fqdn
url
domain
file_path
registry_path
error_code
event_id
powershell_command
powershell_cmdlet
service_name
ticket_id
guid
```

Refine carefully.

---

# 154. Required Primary Kind Inventory

Produce Clipboard-specific Kind list.

Mark:

```text
CORE
LIKELY
FUTURE
REJECTED
```

Avoid creating dozens of overlapping Kinds.

---

# 155. Required Action Mapping

Produce conceptual mapping:

| Kind / Entity | Candidate Actions |
|---|---|
| IPv4 | Ping, DNS Lookup, Diagnostic |
| URL | Open, Search KB |
| Error Code | Search Tickets, Search KB |
| PowerShell Command | Search Scripts, Save Snippet |
| Ticket ID | Open Ticket |
| Mixed | Inspect Entities |

Do not implement actions.

---

# 156. Required Settings Inputs

Map all Clipboard settings expected from Phase 0D.

At minimum evaluate:

```text
capture enabled
manual hotkey
automatic capture
retention
max size
deduplication
secret detection
URL handling
FTS
source context
```

Mark:

```text
CORE
LIKELY
FUTURE
REJECTED
```

---

# 157. Required Database Impact Assessment

For each conceptual structure mark:

```text
REUSE
EXTEND
NEW
NOT NEEDED
NOT VERIFIED
```

Potential structures:

```text
clipboard_items
clipboard_capture_events
clipboard_entities
clipboard_item_tags
clipboard_ticket_links
clipboard_diagnostic_links
FTS table
```

Do not write migrations.

---

# 158. Required Service Impact Assessment

Identify likely:

```text
ClipboardService
ClipboardRepository
classification component
entity extraction component
retention component
```

Avoid excessive microservice-style decomposition.

Recommend the smallest cohesive design.

---

# 159. Required Dependency Map

Clipboard may depend on:

```text
Settings
Taxonomy
Tag Service
Search infrastructure
Ticket reference validation
Diagnostic API
```

Clipboard must not depend on:

```text
Mochi implementation
Analytics GUI
raw PowerShell execution
AHK internals
```

Explicitly map dependency direction.

---

# 160. Required Decision Register

At minimum resolve/evaluate:

```text
Clipboard Item vs Capture Event model
deduplication key
normalization strategy
primary Kind strategy
entity persistence
entity offsets
tag assignment timing
sensitivity classes
secret behavior
retention model
Save vs Pin vs Evidence semantics
expiry recalculation
large-content policy
soft vs hard delete
FTS strategy
relationship tables
automatic capture deferral
analytics exposure
Mochi exposure
```

For each:

```text
Decision
Options
Recommendation
Reason
Consequences
Status
```

Use:

```text
RECOMMENDED
REQUIRES_USER_DECISION
DEFERRED
NOT_VERIFIED
```

---

# 161. Required Risk Register

At minimum:

```text
clipboard privacy
secret leakage
unbounded storage
duplicate explosion
over-normalization
entity false positives
tag noise
large-content latency
FTS growth
relationship coupling
retention data loss
automatic capture overreach
Mochi privacy exposure
analytics privacy leakage
```

Give mitigations.

---

# 162. Planning Depth

Classify decisions as:

```text
DECIDE NOW
DESIGN NEXT
DEFER UNTIL IMPLEMENTATION
```

Likely `DECIDE NOW`:

```text
Item vs Event
deduplication semantics
privacy boundary
retention model
entity persistence model
relationship semantics
```

Likely `DESIGN NEXT`:

```text
AHK hotkey
HUD behavior
GUI table columns
exact IPC transport
```

Likely `DEFER`:

```text
binary clipboard
OCR
AI analysis
automatic background capture
```

---

# 163. Acceptance Criteria

Phase 1A is acceptable when:

1. Existing Clipboard-related architecture has been inspected.
2. Clipboard Item and Capture Event are clearly separated.
3. Deduplication semantics are defined.
4. Raw vs normalized content is defined.
5. Content hashing is defined conceptually.
6. Clipboard primary Kinds are inventoried.
7. MVP Entity Types are identified.
8. Entity occurrence semantics are defined.
9. Tag assignment boundaries are defined.
10. Sensitivity handling is defined.
11. Secret handling is defined.
12. Retention semantics are defined.
13. Save, Pin, and Evidence are clearly distinguished.
14. Cleanup behavior is defined.
15. Large-content policy is defined.
16. Search requirements are defined.
17. FTS5 impact is evaluated.
18. Ticket relationships are defined.
19. Diagnostic relationships are defined.
20. Analytics exposure is defined.
21. Mochi exposure is defined.
22. AHK responsibilities are bounded.
23. Python responsibilities are bounded.
24. Database impact is assessed without migrations.
25. Service impact is assessed without implementation.
26. Failure behavior is defined.
27. Privacy risks are addressed.
28. No production code has changed.
29. Phase 1B can now design AHK ↔ Python Clipboard integration without redefining the Clipboard domain.
30. Phase 1C can later design Clipboard Center GUI without redefining data semantics.

---

# 164. Validation

Return:

```text
Current-state inspection              PASS / FAIL / BLOCKED
Clipboard domain model                PASS / FAIL / BLOCKED
Item/Event separation                 PASS / FAIL / BLOCKED
Deduplication model                   PASS / FAIL / BLOCKED
Normalization model                   PASS / FAIL / BLOCKED
Kind classification                   PASS / FAIL / BLOCKED
Entity model                          PASS / FAIL / BLOCKED
Tag integration                       PASS / FAIL / BLOCKED
Privacy/sensitivity                   PASS / FAIL / BLOCKED
Retention/lifecycle                   PASS / FAIL / BLOCKED
Large-content handling                PASS / FAIL / BLOCKED
Relationship model                    PASS / FAIL / BLOCKED
Search/FTS impact                     PASS / FAIL / BLOCKED
Analytics boundary                    PASS / FAIL / BLOCKED
Mochi boundary                        PASS / FAIL / BLOCKED
Database impact                       PASS / FAIL / BLOCKED
Scope control                         PASS / FAIL / BLOCKED
Production changes                    MUST BE NONE
Database changes                      MUST BE NONE
```

---

# 165. Required Final Report

Return in this order:

## Summary

Overall Clipboard architecture recommendation.

## Current State

Relevant existing F7Hub capabilities.

## Clipboard Domain Vocabulary

Definitions of Item, Capture Event, Entity, Tag Assignment, Retention, Sensitivity.

## Data Lifecycle

Full capture-to-expiry lifecycle.

## Deduplication

Normalization and hashing strategy.

## Classification

Primary Kind behavior.

## Entity Extraction

MVP and future entity handling.

## Tags

Assignment and provenance.

## Sensitivity & Privacy

Secrets, redaction, persistence rules.

## Retention

Temporary, saved, pinned, evidence, expiry, cleanup.

## Large Content

Size policy and handling.

## Relationships

Ticket, Diagnostic, KB, Scripts, Automation.

## Search & FTS

Operational search architecture.

## Analytics Boundary

Facts exposed to Statistical Analytics.

## Mochi Boundary

Safe context available to the assistant.

## Settings Inputs

Dependencies on Phase 0D.

## Database Impact

REUSE / EXTEND / NEW / NOT VERIFIED.

## Service Architecture

Recommended responsibility boundaries.

## Contract Usage

Which Phase 0B messages are used.

## Decision Register

Resolved and unresolved decisions.

## Risk Register

Clipboard-specific architectural risks.

## Recommended Phase 1B Inputs

Explicit assumptions the AHK ↔ Python integration plan may now use.

## Result

Return exactly one:

```text
READY_FOR_CLIPBOARD_INTEGRATION_DESIGN
REQUIRES_CLIPBOARD_ARCHITECTURE_DECISIONS
BLOCKED
```

Do not return:

```text
READY_FOR_IMPLEMENTATION
```

Phase 1A remains architecture planning.


## Downstream Contract for Phase 1B

After Phase 1A is APPROVED, Phase 1B may rely on:

- definition of Clipboard Item
- definition of Capture Event
- deduplication semantics
- content normalization semantics
- sensitivity classes
- retention semantics
- Entity vocabulary
- Tag-assignment rules
- persistence boundary

Phase 1B may NOT redefine these concepts without reopening
Phase 1A architecture review.


Clipboard context can contribute information to the active workflow, but clipboard contents must never determine the authoritative selected ticket.
Also, copying a command is not the same as executing it.