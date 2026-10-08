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

---

# EXECUTION REPORT

## Summary

Date: 2026-10-07, America/Toronto. Mode: ARCHITECT / PLAN. Planning status: READY_FOR_REVIEW. Authority: UNAPPROVED CANDIDATE. This report executes the complete preserved 165-section contract above. All new choices below are RECOMMENDATION, including defaults and resource limits; FACT identifies inspected evidence. No proposed structure, setting, parser, payload or safeguard is claimed implemented.

Recommend a LOCAL_REQUIRED, manual, text/plain domain. Items own immutable eligible content; genuine Capture Events reference Items; producer-bound operation identities prevent transport replay from adding occurrences. Exact-text deduplication preserves evidence; search normalization is separate. Durable history is optional and disabled by default. Secrets are excluded rather than stored in quarantine. TEMPORARY/SAVED express user preservation intent; pinning is independent; accepted evidence associations impose preservation holds. Settings supplies policy inputs; Clipboard owns eligibility and transitions.

Author-side assessment: all 30 criteria PASS at architecture-planning depth. Blocking Foundation gaps/conflicts: NONE identified. Material choices requiring user decision before independent review: NONE. Independent review, explicit USER approval and controlled integration precede closure and authoritative Phase 1B use. No downstream phase executed.

## Baseline / Candidate Identity

| Item | FRESH evidence / rule |
| --- | --- |
| Repository / initial branch | C:/Dev/F7Hub / main |
| HEAD / origin/main / live remote main | All 69176c2801329fef2f107a35129337c9394b2aa4 |
| Origin | https://github.com/JDecelles1990/F7Hub.git |
| Initial tracked / staged | NONE / empty index; diff check clean |
| Initial untracked inventory | Only AutoHotkey/Troubleshooting_Sections/GuideSettings.ini; pathname observed through Git only |
| Original target Git blob / blob bytes | 79103d3ce17f8005cf0e35cfd75648cc075adee1 / 50,535 |
| Original checkout bytes / LF terminators | 54,355 / 3,820 LF terminators (3,821 logical lines), CRLF representation; original final line has no newline |
| Original checkout SHA-256 | 305a181550f33238f3e4d1d9f03425e41978a81077dda57b72f10e1f89f74d48 |
| Filtered baseline | Original checkout equals git cat-file --filters HEAD:<target> byte for byte |
| Branch | docs/clipboard-1a-execution-20261007, created after baseline gates |
| Sole modified tracked path | This document; Execution Report appended after complete original |
| Final candidate identity | Reported outside file after validation, avoiding a self-changing digest |
| Candidate state | UNSTAGED, UNCOMMITTED, UNPUBLISHED, UNAPPROVED, NOT INTEGRATED |
| Next gate | INDEPENDENT PHASE 1A CLIPBOARD ARCHITECTURE REVIEW |

Initial checks executed: branch, HEAD, origin/main, status, tracked/staged diff names, untracked inventory, whitespace, live remote main, origin URL, target blob/size, raw identity and checkout-filter comparison. Final scope/prefix gates repeat after authoring. Protected-state evidence is pathname-only inventory and absence of operations on that file; deliberately no protected-file hash certificate. No operational database opened.

Two long shell-based append attempts were rejected before process creation: Windows command-length limit, then tool policy rejection with no substantive reason supplied. No document bytes changed through those attempts. That shell-writing route was stopped; an external checkpoint draft was prepared for a short byte-append command. No repeated unchanged validation loop occurred. Checkpoint location: LOCALAPPDATA/F7Hub/CodexCheckpoints/Clipboard-Phase-1A-20261007, outside repository.

## Foundation Inputs

FACT: [0E](../Foundation/0E_Foundation_Architecture_Reconciliation.md#execution-report) read in full before targeted authoritative 0A–0D sections. Its historical candidate labels remain historical. Explicit user CLOSED status is corroborated by first-parent merges and fresh read-only [PR #71](https://github.com/JDecelles1990/F7Hub/pull/71): MERGED at current HEAD, independent APPROVE_WITH_NOTES, explicit USER approval/integration authorization, no blocking Foundation gap. It records 0A–0D CLOSED and Foundation ready for feature planning after 0E integration. Approval does not establish implementation/runtime validity.

| Owner / current Git blob | Sections consumed | Clipboard constraint |
| --- | --- | --- |
| [0A](<../Foundation/0A_Master_Foundation_Architectural_Contract.md#execution-report>) / b2bfc2f330ea582a224cd6d2c72eb899160725e2 | Execution C–F ownership/layers/data/technology; H relationships/context/offline/external; I trust; J configuration; approved D1/D2 | Python lifecycle; AHK desktop; repositories normal SQLite; optional Ticket; producer-owned evidence; no Analytics/Mochi/execution shortcuts |
| [0B](<../Foundation/0B_Global_JSON_Contract_Interoperability_Grammar.md#execution-report>) / e290ba6c9c8cf570f380a10575cb219bdfadfbf4 | Principles/envelope/classes/families; identity/correlation; errors/serialization/compatibility/validation/privacy; AHK/Clipboard/large-payload/IPC | Existing grammar; separate request/fact/result; bounded sensitive channel; retry is not capture; retained v1 unchanged |
| [0C](../Foundation/0C_Taxonomy_Information_Vocabulary.md#execution-report) / 8e6fcbfc24b486c92983b13c2488f57a3a0dd2f4 | Kinds/Entity inventory/occurrences/normalization; Tags/assignment; relationships/provenance/confidence; search/Analytics/privacy/retention/Mochi | Feature profiles, global Tags, typed links; extraction not canonical creation; no invented global/legal sensitivity classes |
| [0D](../Foundation/0D_Settings_Architecture.md#execution-report) / 26c8ec6e399f7c206717dd156eb4e23b5a73454b | Principles/ownership/definitions/precedence/effective values; changes/activation; sensitive/secret/privacy; cross-language/hotkeys/Clipboard inputs | Shared resolution, immutable snapshots, conservative off defaults, no secret bypass, no Settings-triggered evidence purge |
| 0E / d9d0b995c9f6f1a82a22428b15a2aa9aeab036d7 | Full reconciliation/authority/gaps/extension/downstream/result and closure evidence | Feature extension permitted; missing implementation is not a Foundation gap |

FOUNDATION GAP procedure: stop affected design thread; record owning phase, exact source conflict, downstream impact and required architecture review. Never patch locally. No unresolved thread identified. Inline caps, key mappings and preservation rules refine original 1A examples without rewriting questions. Existing AltF7Hub opacity discrepancy remains non-blocking owner follow-up, unchanged.

## Repository Areas Inspected

FRESH source/document inspection on WINDOWS_NATIVE Windows/PowerShell host; source presence is not runtime PASS. Explicit source paths/extensions exclude protected INI and operational database. Tests inspected only, not executed.

| Evidence | Inspected area / sources | Question / limit |
| --- | --- | --- |
| E-G | Required Git inventories, Foundation tree/merge history, read-only PR #71 | Baseline/input/closure, not runtime |
| E-COPY | [ScriptService](../../../Python/f7hub/services/script_service.py), [ScriptWorkspace](../../../Python/f7hub/gui/script_workspace.py), [copy integration test source](../../../Tests/Integration/test_script_catalog_flow.py) | Verified-byte source copy with guarded Qt write; not capture/history |
| E-AHK | [shared host](../../../AutoHotkey/F7Hub.ahk), tracked launcher/hotkey inventory; bounded GuideCore/GuideHost clipboard search; scoped Alt AGENTS read first | F7/Alt+F7/scoped guide keys; no capture hook found in searched host sources |
| E-TAX | [0002 taxonomy](../../../Database/Migrations/0002_taxonomy.sql), [TagRepository](../../../Python/f7hub/repositories/tag_repository.py), CategoryRepository inventory; source/migration Entity/catalog searches | Global Tags/scoped Categories; no live rows |
| E-KB | [0005 Knowledge](../../../Database/Migrations/0005_knowledge.sql), [0006 FTS](../../../Database/Migrations/0006_knowledge_search.sql), KnowledgeService/Repository search/tag methods; [search test source](../../../Tests/Database/test_knowledge_search.py) | Current-article FTS and relational filters; no universal search assumed |
| E-TICKET | [TicketService](../../../Python/f7hub/services/ticket_service.py) note/reference paths, [TicketKnowledgeRepository](../../../Python/f7hub/repositories/ticket_knowledge_repository.py) writer link/unlink; 0004/0005 relationships | Owning mutation/activity and atomic reference rechecks; no Clipboard evidence API inferred |
| E-PS | [PowerShellService](../../../Python/f7hub/services/powershell_service.py) signatures/approved paths; [diagnostic values](../../../Python/f7hub/domain/diagnostic_results.py), PowerShell AGENTS/execution boundary | Current fixed parameterless diagnostics/pack and in-memory results |
| E-APP | [bootstrap](../../../Python/f7hub/app/bootstrap.py), [database](../../../Python/f7hub/infrastructure/database.py), [runner](../../../Python/f7hub/gui/service_task_runner.py), [logger](../../../Python/f7hub/app/logging_config.py); migration inventory 0001–0012 | Composition/connection/finite worker/logging; no durable scheduler or generic audit established |
| E-MOCHI | Mochi AGENTS; bounded README/MVP/Architecture privacy sections; MochiService cosmetic/subscriber source and channel/protocol inventory | No business-context/capture/provider capability established |
| E-DOC | ROOT/router/Planning/Foundation guidance; canonical Clipboard ERD, schema inventory, database/search/Settings/logging and AHK/Python boundaries | Possible tables/classes are not migrated/implemented facts |
| E-NEXT | Bounded 1B/1C dependency/header inspection | Consumers unchanged, not executed |
| E-EXT | Official SQLite FTS5/PRAGMA and Unicode normalization pages consulted 2026-10-07 | Mechanism cautions; installed versions/runtime NOT VERIFIED |

Only vertical-slice-delivery found in project skill inventory. Its implementation/review/integration machinery is not mechanically applied to architecture-only authoring; scoped planning governs. Two early source lookup paths were invalid; actual filename/directory filtering corrected. No absence claim relies on failed lookups. No external DynamicHub backup/prototype inspected.

## Verified Current State

| Classification | Finding / evidence | Treatment |
| --- | --- | --- |
| FACT | ScriptService verifies SHA-256 on one buffer, strictly decodes; GUI copies only current visible selection, failure preserves clipboard (E-COPY) | REUSE outbound-copy precedent; NOT RELATED to history/domain identity |
| FACT | Shared AHK v2 host owns F7/Alt+F7 and scoped guide keys; no OnClipboardChange/history hook found in inspected host sources (E-AHK) | EXTEND only in later authorized 1B work |
| FACT | Migrations 0001–0012 have no Clipboard Item/Capture structures; categories admits CLIPBOARD; Tags global (E-TAX/E-APP) | REUSE catalogs; NEW feature persistence only after approval |
| FACT | Knowledge FTS external-content unicode61 index has insert/update/delete triggers/rebuild; literal queries and structured Tags avoid duplicate rows (E-KB) | ADAPT patterns, no Clipboard in KB index |
| FACT | Ticket notes/timeline and Ticket–KB links have services/atomic writer reference rechecks (E-TICKET) | REUSE authority/patterns, not KB junction for Clipboard |
| FACT | Diagnostic run/pack values memory-only; execute_diagnostic accepts script_code, not arbitrary Clipboard arguments (E-PS) | REUSE execution authority; future input/session actions unavailable today |
| FACT | Bootstrap composes services/repos/gateways; connections enable FKs/default 5000-ms busy_timeout; worker delivers GUI-thread completion (E-APP) | REUSE |
| FACT | Rotating process logger/Ticket activity exist; no general audited Clipboard writer/scheduler established (E-APP/E-TICKET) | REUSE logging; justify feature audit/cleanup extension |
| INFERENCE | No implemented Clipboard domain/shared Settings store/universal Entity parser or store/general Context/Evidence store/Analytics subsystem found in searched source/migrations/bootstrap | Absence limited to inspected inventory; future architecture separate |
| FACT | Canonical ERD proposes optional clipboard_snippets/history, expiration/manual clear/sensitive exclusion; no migrated equivalents (E-DOC/E-APP) | SAVED Items support intentional snippets; no duplicate store for wording |
| NOT VERIFIED | Operational integrity/rows, live clipboard/native registrations, installed providers/runtimes, employer policy/performance | Later gates; no runtime readiness |

## Clipboard Domain Invariants

These refine every original invariant while preserving its safety intent.

1. Identical eligible content may resolve one Item within one data scope/format/identity profile. Item equality is not capture frequency.
2. Each genuine accepted capture creates one Capture Event, including duplicate content. Privacy/unsupported attempts need not create durable events; memory-only acceptance creates bounded transient occurrences.
3. Transport retry never adds an occurrence/counter/last-seen update. Retired operation windows reject stale requests instead of accepting them as new captures.
4. Content, source metadata, parser output and copied commands remain untrusted after storage. Kind/Tag/Entity/hash grants no execution/disclosure authority.
5. Size/shape and complete sensitivity gates precede normal persistence/FTS/Analytics/Mochi/integrations. No content-bearing logs at any stage. Detector success is not safety proof.
6. Extraction never automatically creates Company/Contact/User/Device/Ticket or selects authoritative Ticket. Resolution requires owner-scoped validation/explicit acceptance.
7. Assignments reference existing global Tag identities; literals/lifecycle/sensitivity/link types are not Tags; suggestions are not assignments.
8. Accepted durable evidence survives temporary cleanup, history clear, capture-history expiry and target disappearance. Hold release is an explicit owning association lifecycle.
9. Actions use owning services/approved execution validation. Save/Pin/Attach/command recognition never approves arbitrary copied code.
10. Clipboard owns operational facts; Analytics derives eligible measurements and is not required for capture/deletion.

Additional invariants: immutable content is not edited in place; redaction creates a new eligible snapshot. Item identity is never hash/preview/message ID. Durable acknowledgement requires atomic core commit. No parsing/network/IPC/GUI waits in SQLite write transactions. Bound references cannot retarget with later selection. Clipboard deletion never deletes related Ticket/Diagnostic/KB/Script records.

## Clipboard Domain Vocabulary

| Term | Recommendation |
| --- | --- |
| Capture | Intentional bounded observation attempt; may reject, remain transient or become durable |
| Content | Immutable decoded text/plain scalar sequence plus format; raw text is eligible source evidence, not original OS binary formats |
| Item | Source-owned operational identity for eligible deduplicated content in one data scope/profile; durable local DB ID |
| Capture Event | Genuine accepted occurrence, own identity/time/method/safe source class/Item reference; distinct from 0B EVENT |
| Operation identity | Feature UUID bound to authorized producer/application ingress generation; protects intended effects under replay |
| Primary Kind | One whole-content shape/interpretation key under 0C, not topic/lifecycle or all Entities |
| Entity Occurrence | Typed source-snapshot observation at a raw half-open range, not canonical business identity |
| Tag Assignment | Unique Item/global Tag association with origin/method/acceptance provenance |
| Sensitivity | Feature PERMITTED/NEEDS_REVIEW/POSSIBLE_SECRET assessment and method/completeness, not global legal taxonomy |
| Disposition | BLOCKED/MEMORY_ONLY/PERSISTED/REDACTED_PERSISTED; separate from sensitivity/retention |
| Retention intent | TEMPORARY or SAVED; RECENT a view; pin a property; EVIDENCE an effective hold reason |
| Relationship / hold | Validated typed association; accepted durable evidence/source association prevents ordinary cleanup |
| Action | Contextual operation offered for explicit use and fresh owner validation |
| Processing completeness | COMPLETE/PARTIAL for eligible accepted processing; rejection/core failure never fabricates successful Item |

Transient Items/Events use separately typed opaque handles, not DB integer IDs. They expire with session/TTL; no durable evidence link without explicit eligible persistence. Wire distinguishes handle from durable ID; consumers cannot infer storage mode from number formatting.

## Architecture / Ownership

Preserve presentation/capture adapter → ClipboardService → pure domain policies → ClipboardRepository / owning-service adapters → infrastructure. AHK owns trigger/snapshot/source observation/HUD. Python owns authoritative validation, sensitivity/identity, classification/extraction/Tag eligibility, persistence/retention/search/relationships and safe projections. GUI collects intent/renders truth; SQLite integrity is not business authority. Baseline LOCAL_REQUIRED; no AI/network/Mochi/Analytics prerequisite.

Smallest cohesive design: one ClipboardService, one ClipboardRepository; pure policy responsibilities as modules/functions/values. No service per pipeline step, universal parser platform or new daemon. Sender checks are additional guards, not AHK authority. 1B separately designs/reviews sensitive IPC security; guide fixed v1 and Mochi cosmetic v1 unchanged.

Conceptual domain model; no physical schema approval:

~~~mermaid
classDiagram
    ClipboardItem "1" --> "0..*" CaptureEvent : occurrences
    ClipboardItem "1" --> "0..*" EntityOccurrence : raw spans
    ClipboardItem "1" --> "0..*" TagAssignment : accepted topics
    TagAssignment "0..*" --> "1" GlobalTag : existing identity
    ClipboardItem "1" --> "0..*" TicketEvidenceLink : hold
    TicketEvidenceLink "0..*" --> "1" Ticket : validated target
    ClipboardItem "1" --> "0..*" DiagnosticAssociation : conditional durable target
    DiagnosticAssociation "0..*" --> "1" DiagnosticOwnedReference : no invented session
    CaptureEvent "1" --> "1" OperationReceipt : replay protection
    ClipboardItem : immutable raw_text
    ClipboardItem : format and identity_profile
    ClipboardItem : TEMPORARY or SAVED
    ClipboardItem : is_pinned
    EntityOccurrence : raw scalar start inclusive end exclusive
~~~

Conditional KB/Script/Automation profiles are assessed under Relationships without speculative tables. OperationReceipt is feature replay bookkeeping, not a global message ledger.

## Data Lifecycle

| Stage | Owner/effect | Gate / safe result |
| --- | --- | --- |
| Trigger/snapshot | Adapter explicit manual capture | Bounded snapshot; native clipboard untouched; access/race details 1B |
| Request admission | Boundary | Frame/peer/shape/version/identity; no domain effect on invalid input |
| Content admission | ClipboardService | text/plain scalar-valid, nonempty, no NUL, byte cap; no raw logs |
| Sensitivity | Local policy via service | Complete evaluation before hashing/interpretation/disclosure; failure blocks |
| Derivation | Pure policies | Exact identity, distinct search profile, safe preview; derivative re-assessed |
| Interpretation | Pure recognizers | Bounded no lookup/execution; optional failures PARTIAL |
| Resolve/record | Repository | Atomic operation/Item/Event/summary/accepted children/eligible FTS; authoritative rechecks |
| Acknowledge | Service/boundary | Committed or explicitly memory-only result; ACK is not completion |
| Use/preserve | Owning application use case | Save/Pin/evidence/search/copy with current source/target/policy |
| Expire/clean | Clipboard retention | Bounded batches; transactional eligibility/hold/revision recheck |
| Privacy delete | Authorized owning use case | Resolve evidence first; truthful copied-artifact limits; no other-domain wipe |

~~~mermaid
flowchart TD
    A[Manual capture] --> V[Bounded request and content validation]
    V --> S[Complete sensitivity gate]
    V --> R[Safe rejection]
    S --> R
    S --> N[Identity search and interpretation]
    N --> D[Resolve operation and Item]
    D --> M[Explicit memory only acceptance]
    D --> P[Atomic durable acceptance]
    P --> T[Temporary recent Item]
    P --> K[Existing preserved Item]
    T --> Save[Saved]
    Save --> Pin[Saved and pinned]
    T --> Hold[Accepted evidence hold]
    Save --> Hold
    T --> X[Expiry candidate]
    X --> Check[Transactional hold and intent recheck]
    Check --> Gone[Hard delete eligible Item and children]
    Check --> Hold
    Hold --> Release[Authorized last hold release]
    Release --> Save
    Release --> T
    M --> End[Session or transient TTL expiry]
~~~

Wire created_at (assembly), source observed_at, authoritative received_at and commit time differ. Producer time/application labels are untrusted provenance. Retention uses service time/stored policy, not producer clock. New genuine capture updates last-seen/count once; replay updates neither.

## Deduplication & Normalization

DECIDE NOW: clipboard_text_exact_v1 preserves permitted raw scalar sequence exactly. Identity-normalized text initially equals raw_text. Search profile clipboard_search_v1 derives LF from CRLF/lone CR and NFC for search comparison only; never changes raw/equality/copy/Entity offsets. Record profile and implementation Unicode-data version before release. No NFKC folding. [Unicode normalization specification](https://www.unicode.org/reports/tr15/) supports distinguishing canonical and compatibility forms.

| Dimension | Identity v1 | Search/interpretation |
| --- | --- | --- |
| CRLF/LF/lone CR | Preserve; variants distinct Items | Derived LF only |
| Whitespace/tabs/blank lines | Preserve, no trim/collapse | Tokenization/display only |
| Accents/combining sequences/emoji/smart quotes | Preserve exact scalar sequence | Derived NFC; no translation |
| Case/URL query/fragment/signatures/ordering | Preserve | Type-specific Entity comparison; no generic lowercase/sort/decode |
| PowerShell/log/JSON/path syntax/formatting | Preserve | Recognition never rewrites source |
| Embedded NUL/unpaired surrogate | Reject, no silent removal/replacement | No partial evidence claim |
| Empty/whitespace-only | EMPTY_CLIPBOARD, no Item/Event | No placeholder |

Exact identity avoids raw-variant storage/source-specific offsets required by LF/NFC merging. Repeated exactly identical text still deduplicates. Search matches do not establish equality. Identity-profile change is reviewed evolution/migration, never Settings flip; old IDs/evidence/links cannot silently merge or raw content change.

Content hash: SHA-256 over domain-separated, unambiguous length-prefixed tuple (identity_profile, media_type, strict UTF-8 identity_text). Format text/plain participates. Length units bytes; fixed encoding documented in future implementation profile. Scope enforced separately. No delimiter-only concatenation/JSON-order dependence. Algorithm/profile/format are comparison semantics. No persistent/logged/exported hashes of rejected secrets. Hashes are neither anonymization nor public identity.

Digest lookup compares scope/format/profile/full exact normalized content. Unequal content in same digest bucket yields distinct Items and safe collision code, never merge. Do not make hash alone unique. Serialize/recheck concurrent bucket resolution inside writer transaction; same exact content resolves one Item. Classification/Tags/source/time are not dedup keys. Re-evaluation may restrict an existing Item, never automatically loosen privacy.

Raw content immutable; copying uses raw_text for eligible ordinary Items and only retained derivative for REDACTED_PERSISTED, visibly marked. Preview never complete evidence/identity. Identity-normalized text need not occupy duplicate storage column when equal to raw; derived search text may be computed/stored as justified.

### Three identities and idempotency

| Identity | Scope / representation | Meaning |
| --- | --- | --- |
| Item | Data-scope DB positive integer; wire canonical decimal string; transient separately typed handle | First eligible text creates I; later exact capture resolves I |
| Capture Event | Source-owned occurrence ID; DB integer or transient handle | New trigger creates E2 for I, even unchanged text/source |
| Operation / message | Feature UUID bound to authorized producer/ingress generation; 0B message_id identifies request communication | Same operation retransmission returns prior outcome, no E2 |

Initial capture COMMAND maps one operation to one logical request, but explicit operation_id remains feature identity. New genuine capture creates new operation/message. Retry retains immutable snapshot/context/version/intent and IDs, never rereads newer clipboard under old identity. Changed validated semantic payload with same bound operation/message is CLIPBOARD_OPERATION_CONFLICT, no effects. Recovery query may have new message_id referencing original operation; never a new capture. Content hash handles equality, not replay. A receipt comparison fingerprint is only a lookup accelerator: while the source is available, compare the validated semantic request against the exact immutable eligible source and retained bounded request metadata before returning a same-operation match. Never equate fingerprints alone with semantic equality. If required comparison material was removed, refuse redispatch and report known completion/source unavailable rather than accepting a potentially different request.

Recommend active ingress generation with producer binding, five-minute maximum new-operation admission lease measured by service monotonic deadlines, duplicate lookup before effects. Wire timestamps are not lease/authorization proof. Retired generations reject old requests; restart requires fresh generation and receipt reconciliation rather than re-execution. 1B chooses secure binding/lease/restart mechanics under fixed semantics.

Accepted durable capture stores operation receipt atomically with Event/core. Proposed receipt/Event horizon 14 days; bounded generation-local cache for memory-only/rejected outcomes, no durable secret rejection payload/fingerprint. Receipt keeps safe IDs/outcome and eligible semantic-comparison fingerprint while source exists, not raw wire data. On Item deletion remove its fingerprint; retained justified receipt reports source unavailable and rejects redispatch rather than recreating occurrence. Receipt expiry never readmits retired generations. Cache eviction must not lose replay knowledge in an admissible generation: close/rekey admission first, or retain bounded retired identities while their admission lease lasts.

Receipt query after deletion is not capture. Explicit new capture after deletion may create new Item/occurrence; no historical duplicate claim from retained content hash. Receipt schema/CAS/native fixtures DESIGN NEXT; invariants DECIDE NOW.

### Transient promotion and preservation

When history is disabled, deduplication and capture summaries operate only within the bounded transient store; capture does not silently update durable history. Explicit Save/Pin/Attach of an eligible transient Item is a separate preservation action, re-assessing the immutable source and policy at use. It may resolve an existing durable Item by full equality or create one, but is not another genuine capture. Promote only the selected source occurrence, mapping its transient occurrence handle to a durable Event once, with original observed/received provenance and explicit promotion time. The preservation action has its own operation identity/receipt; repeating it never duplicates the occurrence or increments lifetime counters again. Do not import the entire transient history or lifetime count. Record acceptance_origin (direct durable capture or explicit transient promotion); keep original transient duplicate status distinct from durable resolution status. Analytics can include promoted observations only with a declared grain/time rule, never silently count promotion as another capture. Durable first/last receipt summaries take the minimum/maximum actual occurrence receipt time, not promotion time, so older promoted provenance cannot overwrite a newer last-seen value. A previously acknowledged capture result remains truthful as originally MEMORY_ONLY; later lookup can expose the separate promotion outcome. If transient source/occurrence expired, reject SOURCE_UNAVAILABLE; no reconstruction from preview/hash.

## Classification / Primary Kind

One primary Kind per Item, classifier profile/version/origin/completeness recorded. Deterministic local recognition; no AI/PowerShell execution dependency. Kind is shape/interpretation, not topic/lifecycle/authority. These proposed keys are feature vocabulary extensions under 0C, not installed catalog rows. Optional confidence requires declared method/calibration; no invented 1.0.

| Candidate | Disposition | Meaning |
| --- | --- | --- |
| plain_text | CORE | Ordinary valid text without stronger whole-content profile |
| unknown | CORE | Classifier unavailable/failed; safe content may persist PARTIAL |
| mixed_text | CORE | Positive evidence of heterogeneous sections, no single exclusive whole-content profile |
| url | CORE | Whole analysis view is one parsed URL; raw whitespace retained, no auto-open |
| json | CORE | Whole content validates as bounded JSON data, not instructions |
| powershell_command | LIKELY | Whole snippet recognized by narrow nonexecuting profile; uncertainty falls back |
| error_message, log | LIKELY | Declared namespace/line-oriented profiles; source app alone insufficient |
| markdown, csv | LIKELY | Whole-content recognizers with ambiguity fallback; no dependency selected |
| xml, yaml | FUTURE | Bounded safe profiles, no external-entity/network loading |
| powershell_output, powershell_error | REJECTED initial separate Kinds | Use log/error_message/mixed plus PowerShell topic/provenance |
| ticket_data | REJECTED generic Kind | Ticket reference/context does not prove authoritative Ticket content |
| image, file_list, html, rtf, binary | FUTURE formats | Outside text-only; no automatic evidence-destroying conversion |
| saved, pinned, evidence, sensitive | REJECTED Kinds | Separate lifecycle/privacy dimensions |

Precedence: whole valid structured format (initial JSON), then whole URL, then a declared whole command/log/error/document recognizer. Conflicting specific interpretations yield mixed_text only with heterogeneous evidence, otherwise plain_text with proposals. Entity presence alone never defines whole Kind. Classifier error yields unknown/PARTIAL; ordinary free-text fallback plain_text/COMPLETE. Exact grammars/fixtures defer to implementation; fallback/ownership policy fixed now.

Reclassification is explicit derived-data processing over unchanged eligible source, versioned with expected Item revision. Manual annotation provenance remains distinct; no content identity change. Closed wire Kind enum additions follow 0B breaking-compatibility rules.

## Entity Extraction

Per-source deterministic bounded profiles; structured/composite spans first, nested technical values next, contextual proposals last. No network/registry/filesystem reads, AI, canonical creation or execution. Source is immutable raw_text or retained redacted derivative; bind Item/snapshot revision and parser profile/version.

Offsets: Unicode scalar-value indices in raw_text, zero-based half-open [start_offset,end_offset). Not UTF-8 bytes, UTF-16 units, graphemes or normalized-text positions. Validate 0 <= start < end <= raw scalar length and exact raw slice. AHK/Qt presentation converts explicitly in 1B/1C; emoji/combining accents/CRLF fixtures required. FTS/search-normalized positions cannot highlight raw source without a validated map.

Four identical IPs at different spans are four occurrences. Consolidate only duplicate detections with same type/profile/span/normalized value, retaining bounded method provenance. Nested/overlapping occurrences allowed, optional parent relation; URL may contain host/IP/port. Ambiguous types remain proposals; email does not prove UPN. UI groups values/counts without replacing source occurrences.

| Candidate / 0C mapping | Disposition | Interpretation |
| --- | --- | --- |
| ipv4 → ipv4_address | MVP | Validated value, dotted-decimal comparison, no octal guess |
| ipv6 → ipv6_address | MVP | Declared compressed comparison, zone/context preserved |
| email → email_address | MVP | Preserve local-part; declared domain comparison; not Contact equality |
| upn → account_name profile | LATER | Directory/namespace context; email shape insufficient |
| hostname, fqdn | MVP | Conservative contextual proposals; short/qualified distinct; no DNS query |
| url | MVP | Preserve path/query/fragment/signatures; credential exclusion |
| domain → fqdn/domain-name profile | LATER | Reuse semantic profile; truly distinct meaning needs controlled 0C extension |
| file_path, registry_path | MVP | Preserve source; no expansion/access/global lowercase |
| error_code | MVP | Namespace/radix; not universal integer equality |
| event_id | LATER | Provider/log/host context; arbitrary number not globally identified |
| powershell_cmdlet → powershell_command_name | MVP | Literal recognition, no existence/approval proof |
| full powershell_command occurrence | LATER | Prefer whole Kind/source span and command-name occurrences |
| service_name | LATER | Concrete source context, no service control |
| ticket_id → ticket_reference | MVP | Owner/display namespace; resolve via service, never assume local PK |
| knowledge_reference | LATER | Explicit owner resolver; no auto-link |
| guid | MVP | Syntax normalization, not tenant/device/object identity |
| mac_address, CIDR, port | LATER | Existing MAC profile; CIDR/port justify controlled 0C profile extension/units |
| directory/tenant/provider/resource references | LATER | Verified namespace/provider/type, none selected here |
| process/security/software/temporal/fingerprint/vulnerability profiles | LATER | 0C context/time/algorithm requirements |
| json/xml/csv/yaml generic Entities | NOT APPLICABLE | Format/Kind; contained values can be occurrences |
| passwords/tokens/recovery/MFA/private keys | NOT APPLICABLE | Secret gate, never normal extraction/history |
| internal content_hash | NOT APPLICABLE source Entity | Dedup metadata, not extracted text identity |

Persist Item/source revision, Entity Type/profile/version, span/units, permitted raw or derivable slice, optional normalized value, minimal parser provenance and optional calibrated confidence. Stable queryable fields typed; optional metadata only bounded profile-specific facts. Failed interpretation never replaces raw with guessed normalization. Reprocessing atomically replaces declared derived generation; accepted canonical links remain separate and revalidate upon source loss.

Proposed resource ceiling: 1,024 occurrences per small Item, stable ordering by start/end/type, bounded recognizer work. Overflow reports partial extraction, never full completeness. Resource cap is not taxonomy meaning. Invalid one-parser output discarded with safe code; valid other output can persist PARTIAL.

## Tags

REUSE existing global tags IDs/meaning and catalog reads. EXTEND eligibility/assignment interfaces only through approved taxonomy/domain work. No second Clipboard catalog. Legacy slugs do not automatically equal new 0C keys; reviewed mappings required. PowerShell/DNS/Networking/Outlook/Troubleshooting are topic examples, not verified installed rows.

Generate deterministic suggestions after classification/extraction. Initial durable path is manual acceptance; automatic assignment defaults off until a separately reviewed rule profile exists. Thus timing resolved without pretending 0C authorizes auto-tagging. Rules reference approved Tag identity/method/version, never email/IP/customer literal, lifecycle or sensitivity. Missing/ineligible catalog identity suppresses proposal; no automatic catalog creation. Context/AI suggestions future advisory only.

Association unique Item/Tag pair. Origin/method/rule version and acceptance actor/time separate; human acceptance does not erase RULE/AI/import provenance. Multiple justifications never duplicate assignment. Manual removal must not be silently undone by duplicate capture/reprocessing. Empty assignments valid. No arbitrary topical numeric cap; responses remain bounded. Retirement/merge follows 0C; current Tag lifecycle/merge API not assumed implemented.

## Sensitivity & Privacy

Mandatory local assessment, no bypass. Feature handling labels PERMITTED, NEEDS_REVIEW, POSSIBLE_SECRET plus ASSESSMENT_FAILED/INCOMPLETE. They are findings under Clipboard policy, not global/legal classes. BLOCKED/MEMORY_ONLY/PERSISTED/REDACTED_PERSISTED are dispositions. Sensitive non-secret email/device/path/customer observations differ from credentials. Detector result is uncertainty, not safety certificate; method/version/completeness matter.

Ordering: bounded transport/format/size admission → metadata minimization → complete sensitivity gate → eligible derivation/hash/Kind/Entities → persistence/FTS eligibility → safe facts/context/actions. No content-bearing logging anywhere, including decode errors/debug exceptions. Producer preflight rejects recognized secrets before ordinary IPC; Python repeats authoritative checks. 1B threat-reviews tightly bounded transient handling and peer security. 0B never authorizes sending known credentials for classification.

| Condition | Default | Alternative / limit |
| --- | --- | --- |
| PERMITTED, history off | MEMORY_ONLY, local inspect/classify/safe copy | Explicit Save/Attach may persist one eligible item without enabling history |
| PERMITTED, history enabled/eligible | TEMPORARY PERSISTED | No automatic export/context share |
| NEEDS_REVIEW, non-secret sensitive | MEMORY_ONLY; concealed list preview | Explicit purpose/policy-reviewed local persistence; no default FTS/Analytics/Mochi |
| POSSIBLE_SECRET/known credential | BLOCKED; promptly release app snapshot; OS clipboard untouched | No raw override, file/SQLite quarantine, secret hash/history/Entities/assistant; user may submit separately sanitized new content |
| Assessment failed/incomplete | BLOCKED | Explicit retry only after repair; no unknown-Kind unsafe fallback |
| Reviewed redaction transform | New candidate, re-assessed | Derivative only, new identity/provenance; no original secret hash/raw/offsets |

False positive safely loses optional history convenience; no persist-anyway escape. False negative may still leak undetected material: manual scope, off-by-default persistence/sharing, no raw logs, short TTL, minimized metadata and explicit outbound review reduce consequence. Later detection denies new exposure, removes derived FTS/unsafe occurrences and invokes governed privacy deletion/association repair. No deterministic completeness/physical memory zeroization claim. OS clipboard/paging/crash dumps/backups outside app erase guarantee.

### Privacy matrix

All eligible persistence requires explicit intent/policy and complete assessment. Employer/customer authorization NOT VERIFIED. Type-only means approved coarse nonidentifying facts, not literal values. Baseline automatic Analytics/Mochi sharing off.

| Content | Persist raw? | Redact/omit | Search/FTS | Analytics | Mochi/external AI |
| --- | --- | --- | --- | --- | --- |
| Ordinary non-secret text | Eligible TEMPORARY/SAVED | Safe bounded preview | Eligible opt-in FTS | Coarse facts only | Explicit eligible selection; external preview/Send later |
| Email address | Review-gated local | Concealed preview, no source title | Deliberate structured filter, no default FTS | Entity Type only if eligible | Omit value by default |
| Device/host name | Review-gated local | Minimize customer linkage | Same sensitive filter rule | Type only, no device dimension | Omit value |
| File/UNC/registry path | Review-gated local | Omit username/share/path projections | Local structured filter, no default FTS | Type only | No raw path forwarding/access |
| URL | Review-gated if personal/signed; credential-bearing blocked | Safe display without unsafe userinfo/query | Non-sensitive eligible URL only | Kind/size, no URL history | Explicit safe open; external text gated |
| Password-like string | NO automatic raw persistence | BLOCKED | NONE | No hash/literal; optional content-free blocked count | NONE |
| API/Bearer/connection-string secret | NO | BLOCKED, no ordinary quarantine | NONE | No secret fingerprint | NONE |
| MFA/recovery code | NO when authentication suspicion | BLOCKED; arbitrary numeric detection imperfect | NONE for blocked text | No literal/context | NONE |
| Private key/cookie/session secret | NO | BLOCKED | NONE | Content-free rejection only if justified | NONE |
| Large customer log | No baseline beyond inline cap; future review-gated | No pre-gate persisted preview | No automatic index | Size/status only if eligible | No raw log/history |
| Redacted derivative | Independently eligible derivative only | No original secret value/hash | Re-assessed derivative; sensitive remains non-FTS | Safe facts only | Explicit safe projection |

Source context: optional coarse allowlisted application class (terminal/browser/editor/unknown) and capture method. No full process path/command line/window title/browser source URL or arbitrary metadata in MVP. Future transient title collection requires separately reviewed purpose/minimization; no default persistence or hashed-title substitute. Clipboard content URL differs from browser source context.

Safe technical logs: validated message/operation IDs, contract/component/outcome/code, duration/size class; eligible counts only if useful. No raw content/preview/Entity value/window title/URL/path/content hash/offending payload/raw exception. Routine captures operational facts, not heavy security audit. Save/Pin/evidence attach/release/export/authorized deletion/privacy escalation need purpose-appropriate safe evidence of action/outcome/IDs, not copied content. Current logger/Ticket timeline not generic Clipboard audit. Later sensitive activation remains unavailable until required durable evidence path exists; no generic audit store invented here.

## Retention

DECIDE NOW: two preservation intents TEMPORARY and SAVED. RECENT is ordering/view, not a redundant retention class. Pin is independent property with rule pin implies SAVED. EVIDENCE is effective preservation reason derived from accepted durable associations, not user-editable enum/Tag. Preserve user intent and all holds separately; effective precedence evidence hold → SAVED/pin → unexpired TEMPORARY → eligible expiry. Secret exclusion is earlier admission rule, never a retention class.

| Dimension/action | Semantics |
| --- | --- |
| TEMPORARY | Eligible history with fixed expires_at under policy snapshot; default proposal 24 hours |
| SAVED | Explicit user preservation, no ordinary expiry; quotas visible, no silent saved-item eviction |
| Pin | Atomically Save if needed plus is_pinned=true; prominent view, no independent TTL |
| Unpin | is_pinned=false, remains SAVED; never silently restores old temporary TTL |
| Unsave | Explicit demotion to TEMPORARY; if pinned, explicit combined Unpin/Unsave intent; fresh expiry from action time |
| EVIDENCE hold | Accepted durable target/source association preserves complete eligible Item even if nominal temporary expiry elapsed |
| Last hold release | Authorized review; keep SAVED if saved intent, otherwise arm fresh TEMPORARY expiry from release time/current snapshot with clear feedback |
| Ordinary clear | Deletes only eligible TEMPORARY without holds/pin; never SAVED/evidence; distinct from explicitly scoped delete-saved |
| Explicit delete | Hard-delete eligible Item after source/target policy and evidence release/transfer; cannot silently destroy held evidence |

Duration Settings configures allowed lifetime; Clipboard calculates eligibility. On capture/create, expires_at = authoritative acceptance time + bound temporary duration. A genuine duplicate TEMPORARY capture refreshes expiry from its service receipt time using its current policy snapshot; replay does not refresh. SAVED/held content keeps no effective expiry; optional suspended nominal expiry/policy provenance can remain for explanation, not deletion authority. Decreasing Settings TTL does not recalculate all old Items or trigger purge. Explicit reapply policy requires candidate preview/count, preservation checks, intent and bounded operation; no Settings notification mass deletion.

Cleanup rechecks expiry, Item revision, user intent, pin and live accepted holds inside one writer transaction. Propose startup and periodic application-owned finite batches, at most 100 Items/transaction and 500/dispatch or one-second dispatch budget, yielding between batches. No daemon/global scheduler. Clock anomaly pauses destructive expiry pending safe reconciliation; timestamps alone never prove absence of holds. Save/Attach winning the writer reservation blocks cleanup; if cleanup already removed Item, Save/Attach returns source missing, never invents evidence.

### Retention decision table

| Intent | Link reason | Pin | Nominal expired | Ordinary delete? | Result / transition |
| --- | --- | --- | --- | --- | --- |
| TEMPORARY | None | No | No | No | Recent until expiry |
| TEMPORARY | None | No | Yes | Yes | Atomic hard delete children/index |
| TEMPORARY | Accepted Ticket/Case evidence | No | Yes | No | Hold overrides expiry |
| TEMPORARY | Accepted durable Diagnostic evidence | No | Yes | No | Preserve; absent durable target cannot create hold |
| TEMPORARY | Neutral related/input reference only | No | Yes | Yes | Source lifetime explicit; related target unaffected |
| SAVED | None | No | N/A | No | Explicit delete/demotion only |
| SAVED | None | Yes | N/A | No | Unpin keeps SAVED |
| SAVED | Evidence hold | Either | N/A | No | Both independent preservation reasons |
| TEMPORARY | Target missing but unreleased accepted hold | No | Yes | No | Orphan hold requires owning reconciliation |
| TEMPORARY | Last hold explicitly released | No | Previous expiry ignored | No immediate deletion | Fresh TTL, visible demotion |
| Any | Possible secret discovered later | Either | Any | No ordinary cleanup shortcut | Deny exposure, remove unsafe indexes, governed privacy incident/deletion |

Capture Event retention can be shorter than saved Item lifetime: proposed 14 days for ordinary history/receipts, no raw source titles. Item immutable content and evidence association provenance survive Event expiry. If a specific occurrence is itself accepted evidence (source/time claim), its minimal occurrence metadata is promoted into the durable association or explicitly held; routine Event pruning cannot erase that claim.

Recommend maintained operational summary captured_total, first_received_at and last_received_at because Events intentionally expire. They are no longer fully derivable from retained Events; label them lifetime counters, not Analytics metrics. Update exactly once with accepted operation, including duplicate; no fabricated history after reconstruction. Retained-events count/period distinct. Summary may survive event pruning with Item, not privacy deletion. Analytics aggregates cannot reconstruct deleted raw or veto deletion.

Hard deletion preferred; no soft-delete raw recycle bin by default. Delete Item-owned capture history/occurrences/assignments/neutral links/eligible search projection in same transaction. Hold relations restrict deletion until authorized release; never cascade into targets. Minimal safe receipt/tombstone only if replay/audit purpose requires it, TTL-bound and no raw/content hash after source deletion. Logical SQL deletion is not forensic secure erase: SQLite documents virtual-table shadow traces; backups/WAL/copies require separate reviewed data lifecycle. [SQLite secure_delete limitations](https://www.sqlite.org/pragma.html#pragma_secure_delete)

### Storage bounds

Proposed transient store: at most 32 Items and 2 MiB total eligible UTF-8 content, 15-minute idle TTL, app exit clears; reject/expire oldest unpreserved transient content with truthful feedback. No transient Save/evidence guarantee. Durable TEMPORARY pool: at most 10,000 Items/64 MiB eligible source bytes; occurrence/receipt pool target 100,000 rows within its horizon. Admission first performs bounded eligible cleanup; if still full, return capacity error or explicitly MEMORY_ONLY, never claim saved. Saved/evidence count against visible total budget but cannot be evicted to meet it. Proposed total eligible durable source ceiling: 256 MiB (including SAVED/evidence); derived occurrence ceiling: 100,000 rows. If a prepared derived component exceeds remaining budget, omit it with explicit PARTIAL before the transaction, never ignore an insertion failure. Concrete DB/index/backup disk accounting must be measured and reviewed; no unlimited policy. Saturation disables new durable admission rather than losing preserved work.

## Large Content

Use approved 0B inline caps: at most 64 KiB UTF-8 text and 128 KiB full serialized Clipboard message, including envelope. Both must pass; escaped controls may make a sub-64-KiB text exceed envelope cap. Global 1-MiB cap is not permission to expand Clipboard profile. Settings can lower admitted text size, not raise wire/security maxima.

| Class | Proposed threshold | Process | Persist | Entities | UX |
| --- | --- | --- | --- | --- | --- |
| Small | <=16 KiB content and within message cap | Full bounded local pipeline | Eligibility/intent gated | Bounded extraction | Target prompt acknowledgement |
| Medium | >16 to <=64 KiB and <=128-KiB complete message | Full sensitivity before other bounded work; finite worker | Same policy, explicit sensitive review | Cap/partial result visible | Busy/size indication, no truncation |
| Large | >64 KiB content OR escaped message >128 KiB | Baseline reject PAYLOAD_LIMIT_EXCEEDED before domain admission | NO baseline Item/event/preview/hash | NONE | Safe too-large result, original clipboard unchanged |
| Future managed text reference | Separate approved owner/storage design | Full content inspection before storage/projection | Conditional reviewed limits/lifetimes | Bounded/deferred visibly | Missing/expired/refused reference explicit |
| HTML/RTF/file lists/image/binary | Unsupported baseline | Safe UNSUPPORTED_CONTENT_TYPE | NONE | NONE | No silent conversion/OCR/base64 |

No unreviewed file path/reference mechanism to route around cap. 0B permits future managed references, not arbitrary caller paths or bearer permission. Until storage/security exists, reject large content; even explicit Save does not widen caps. Selecting a smaller fragment is a new capture, labeled selected excerpt, never complete original evidence.

Preview: up to 240 Unicode scalars from independently eligible retained content; line breaks rendered as spaces, controls/bidi effects safely presented and truncation marked separately. No raw secret preview; sensitive list shows generic concealed label. No preview hash or record identity. Escape as plain text; no HTML execution, URL auto-open or rich-content evaluation. Inspector/copy uses authorized full source, not preview. Search matches beyond preview must not imply preview is whole source.

## Relationships

REUSE 0C typed predicate meanings and existing FK/service patterns; no universal graph/parallel evidence ledger. Profiles declare endpoints/direction/cardinality/uniqueness/provenance/acceptance/lifetime. Multiple targets allowed when purpose explicit; unique source/target/predicate association, no duplicate link on retry. Association identity separate from capture operation.

| Profile / direction | Meaning | Authority / retention |
| --- | --- | --- |
| Item EVIDENCE_FOR Ticket / future Case | Explicit accepted source for claim/workflow, source snapshot bound | Owning Ticket/Case association use case validates target; durable hold; no implicit Ticket selection/mutation |
| Item EVIDENCE_FOR durable Diagnostic reference | Evidence association, not diagnostic outcome proof | Conditional Diagnostics-owned durable target; hold; current memory run cannot masquerade as durable session |
| Item INPUT_TO Diagnostic (feature specialization) | Deliberately selected input used/requested | DiagnosticService owns validation/execution/outcome; input link alone not evidence hold; durable actual-used fact only after confirmed use |
| KB draft/article DERIVED_FROM Item | Explicit reviewed content derivation, inverse source-for view | KnowledgeService creates independent draft; no automatic publication; if source must remain reproducible, explicit preservation hold accepted |
| Item RELATES_TO KB / Script | Neutral typed association, no approval/execution claim | Validate existing target; no ordinary hold; expired source ref unavailable |
| Approved Automation USES selected source | Conditional typed data use, not text-triggered automation | Owning Automation validates permitted inputs/freshness/authority; no raw commands or automatic triggers |

Ticket hold transaction validates source/target/revision/policy and atomically inserts association/hold/required audit; does not write Ticket internals from ClipboardRepository. A future application association use case can coordinate owning Ticket validation and shared transaction infrastructure. Existing Ticket–KB junction not repurposed, existing TicketService has no promised Clipboard attach API. Ticket notes/timeline remain Ticket-owned; any requested activity extension must be designed by that owner.

Case Journal remains optional/ticketless under 0A-D2; absence of implemented Case store is not permission to create it in Clipboard. Clipboard Item alone is not a Case Journal. Diagnostic durable link is unavailable until Diagnostics defines stable accessible persistence. Raw result copy creates untrusted Clipboard content, not an authoritative diagnostic result/session.

Target deletion cannot silently cascade away a preservation hold. Owning target deletion must explicitly reconcile release/transfer/retain orphan hold with source owner; absent coordination, restrict deletion of held target. Source never deletes target. Neutral links may cascade/remove association with target while source remains independent. Accepted evidence unlink rechecks intent/revision/all holds and rearms temporary expiry only through explicit last-hold semantics.

Copying eligible content into a Ticket note or KB draft creates a separate owning artifact with its own lifecycle/privacy and provenance. Clipboard clear does not erase that copy; source promotion must be acknowledged accurately. Evidence transfer requires durable target artifact plus lineage/accepted preservation before source hold release. No claim of cross-domain atomicity across arbitrary services; shared-local DB transaction only when owners explicitly support it, otherwise truthful phased outcomes and source retained.

### Action mapping

| Kind / Entity | Candidate actions | Gate / current availability |
| --- | --- | --- |
| IPv4/IPv6/host | Search KB/Tickets; propose DNS/Ping/network diagnostic | Validated selected input and approved operation only; current parameterless diagnostic API does not implement these input actions |
| URL | Inspect, Save, explicit Open, Search KB | Safe scheme/purpose/intent checks; no auto-open, javascript/file/custom execution |
| Error code | Search Tickets/KB | Literal bounded query, namespace carried; not root-cause truth |
| PowerShell command/name | Search Script registry, Save snippet, local inspect | No execution; Explain through separately reviewed advisory workflow |
| Ticket reference | Resolve candidates, explicit Open/Attach | Display code not PK; current target validation/fresh intent, ambiguity safe |
| Mixed content | Inspect Entities, select eligible fragment, Save | No automatic all-actions dispatch |
| Any eligible persisted Item | Save/Pin/Unpin/Unsave/Attach/Delete/Copy | Lifecycle/privacy/holds/ref freshness revalidated, capabilities separately discovered |

Prefer existing application action identities/owning commands; search before extending names such as clipboard.item.save or clipboard.item.attach_evidence. No new ActionRegistry mandated. 1B/1C design routing/presentation later; action key offered is not permission. Stale Item/target/version/policy denies execution. Clipboard never launches PowerShell, mutates Tickets directly or grants copied scripts registration.

## Search & FTS

Search identity always Clipboard Item ID/typed transient handle. Preview/hash/message IDs never selection keys. Results lightweight safe summaries; Inspector revalidates current source/privacy/revision. Recent/Saved/Pinned/URLs/Commands/PowerShell/Errors & Logs/Networking/Ticket Evidence/Diagnostic Evidence/Mixed/Sensitive/Large/Unlinked/This Week are query views, not duplicate stores. Recent sorts authoritative last_received_at; stable Item-ID tie-break. Sensitive requires deliberate local filter, concealed preview; expired unheld content excluded even before physical cleanup.

| Query | Recommended mechanism |
| --- | --- |
| Recent/date/Kind/retention/pin/sensitivity/source class | Bound relational predicates and ordered paged result |
| Tag single/any/all/untagged | Canonical Tag IDs; EXISTS/count over unique junction, one row per Item |
| Entity Type/value | Indexed profile/type + normalized value + Item; exact mode distinct from FTS; raw fallback explicitly named |
| Ticket/Diagnostic/evidence relationship | Typed target/predicate joins/EXISTS; no multiplying result rows |
| Content | Optional derived FTS over eligible search_text; safe literal query |
| Preview | Display; optional explicit bounded local substring mode only, never substitute full-content search |
| Sensitive | Deliberate authorized structured local lookup; no default FTS/auto-suggestions/snippets |

ADAPT Knowledge external-content/index synchronization and safe literal-query patterns, not its table or article schema. Proposed Clipboard FTS uses separate eligible content projection keyed by Item ID, unicode61 as initial reuse candidate. Search_text LF/NFC derivative only for PERMITTED, index-enabled Items; never raw sensitive/secret content, source titles/URLs, Entity values or Tag labels indiscriminately. Preview redundant for indexing when derived from same text; do not index it separately. Kind/Entity/Tag/relationship filters relational, not MATCH magic.

All index eligibility computed before transaction; owner-controlled projection insert/update/delete and FTS sync occur atomically with source/eligibility mutations. Core FTS write failure rolls back capture, no false saved result. FTS disabled is legitimate unindexed capture, explicitly searchable=false; not PARTIAL by itself. Derived rebuild can run bounded later against current eligible projection, never broad raw-history scan that ignores policy. Index corruption/unavailable search returns safe search error and preserves operational source; no hidden fallback that exposes sensitive text.

SQLite requires external-content/index consistency; its documented pitfalls support treating synchronization as a correctness gate. [SQLite FTS5 external-content guidance](https://www.sqlite.org/fts5.html#external_content_tables) Logical index deletion is not forensic erasure; installed SQLite/FTS secure-delete capabilities require future inspection/tests, no configuration changed here.

Indexes conceptually cover hash bucket scope/format/profile, expiry/intent, last-seen/ID, Event Item/time and operation uniqueness, Tag reverse lookup, Entity type/value/Item, and typed relationship targets. Pagination/caps required for 1,000 Items then 10,000 Items/100,000 Events; no benchmark/optimality claim. Tokenizer/ranking/accent semantics tested with English/French/emoji, not assumed exact bilingual identity. Universal search remains downstream extension of owner query API, no new engine here.

## Analytics Boundary

Clipboard owns durable eligible operational facts; Analytics read-derived and optional. No raw clipboard, previews, content hashes, literal email/IP/host/URL/path/window title/command string or full provenance dumps by default. Transient content/private attempts not durable Analytics source; only separately justified nonidentifying blocked/error counters, no rejection fingerprints. No IPC stream becomes permanent operational truth.

Smallest future eligible projection: Event ID/Item ID under local access policy, captured/received time at required granularity, Kind, eligible Entity Type only, accepted eligible Tag IDs, coarse source application class/size class, duplicate flag, relationship type and accepted time, retention outcome. All optional dimensions filtered by purpose/privacy; sensitive NEEDS_REVIEW excluded by default. IDs/timestamps can still identify behavior and are not anonymous; release requires approved retention/access policy.

Declare grain: accepted durable occurrences, distinct Item IDs in time/scope, duplicate captures (Item existed at operation), relationship association facts, retention actions. Distinct join handling prevents multi-Entity/Tag inflation. If 100 accepted captures create 62 Items and 38 resolve existing Items, the duplicate count is 38; preexisting/deleted Items change interpretation, so never compute duplicates merely as captures minus current Item inventory. Event expiry means raw historical rederivation unavailable; lifetime operational summary is separate from retained-event counts.

Type-only dimensions allowed by approved Entity eligibility, not literal frequency profiles. Source class unknown stays unknown; source percentages refer to eligible captures, not every OS copy. Evidence attachment ratio requires explicit target association/time and defined denominator. Automation opportunity insight cannot consume command strings automatically from capture counts.

Deletion does not wait for Analytics aggregation, and aggregates have no exemption from privacy deletion. Optional coarse already-produced aggregates can outlive raw only under approved deletion/purpose policy and cannot reidentify/replay source. Analytics outage never blocks capture/cleanup. No Analytics store/GUI/subsystem designed here.

## Mochi Boundary

Mochi optional/read-only/advisory, no dependency from ClipboardService to MochiService/runtime. Future application-owned context projection reads source services and delivers only explicit selected context. Current cosmetic v1 unchanged; no context capability inferred.

Allowed candidate surface after separate review: typed Item reference/revision, Kind, independently safe/redacted bounded preview, selected safe Entity Types/values only where approved, accepted eligible Tags, minimal relationship references and offered action keys. Baseline raw content/history/source titles/browser URLs/customer literals/large logs excluded. Sensitive context disabled; redaction is additional guard, not certificate.

Every context request revalidates source availability/sensitivity/freshness/purpose and selection. Deleted/expired Item gives unavailable, never stale cached raw fallback. Raw eligible text requires distinct reviewed feature policy and explicit user selection; external AI additionally exact payload preview and explicit Send under verified employer/provider/credential boundaries. Possession of Item ID/context-enabled preference is not disclosure permission. Provider is NOT VERIFIED; no API request or credential setup.

Mochi cannot save/retag/attach/select authoritative Ticket/execute/approve scripts. Action suggestions return to normal user-controlled owning services with fresh validation; advisory origin retained. Clipboard processing remains local when Mochi or network unavailable.

## Settings Inputs

Consume 0D shared typed definitions/override resolution, not Clipboard-local INI/SQLite preference store. Future pure module contributions statically composed; service receives immutable validated snapshot/revision. USER ordinary chain default → stored override → expressly admitted session override; no arbitrary environment/CLI key mapping. Invariants/capabilities/authorization/catalogs outside precedence. Missing shared implementation is a bounded future delivery need, not permission to reinvent Settings.

| Input candidate | Priority | Proposed default / semantics | Activation / scope |
| --- | --- | --- | --- |
| clipboard.capture_enabled | CORE | false until explicitly enabled workflow; manual selection only | USER, next capture; current pause runtime command separate |
| manual hotkey binding | CORE input, exact key DESIGN NEXT | No registered key/default chosen in 1A; binding/action identity separate | 1B validation/host activation; desired vs applied, no DB lock across registration |
| clipboard.auto_capture_enabled | FUTURE | false; monitoring excluded baseline | Separate privacy/rate/exclusion/teardown review |
| clipboard.persistence_enabled | CORE | false; eligible manual transient work; Save single eligible Item possible | USER sensitive opt-in, next capture; no retrospective history import |
| temporary retention duration | CORE | 24 hours proposed, bounded positive duration | USER next new/duplicate/demotion snapshot; no old-item purge |
| event history duration | LIKELY | 14 days proposed; preservation claims independent | Next explicit eligible cleanup; no evidence metadata deletion |
| max content size | CORE | <=64 KiB and complete message <=128 KiB invariant ceiling | USER may lower only, next capture; security caps not editable |
| dedup enabled/profile/case/whitespace switches | REJECTED | Exact identity/replay semantics invariant of profile | No setting permits duplicate explosion/unsafe merge |
| secret_detection_enabled / persist_secret_override | REJECTED | Mandatory gate/no secret retention | Not Settings, no admitted default |
| URL open behavior | LIKELY | No auto-open; explicit safe action | USER next action within supported schemes/authorization |
| FTS enabled | LIKELY | false proposed until explicit eligible indexing choice | USER next eligible indexing operation; disable removes searchable projection atomically |
| source application class collection | LIKELY | off; coarse allowlist if purpose justified | USER next capture, privacy-sensitive |
| full source window title/browser URL collection | FUTURE | off, not baseline persisted | Separate feature privacy policy; no incidental harvest |
| automatic Tag assignment | FUTURE | off until approved rule profile | Next eligible processing; catalog meaning unchanged |
| taxonomy/Kind/Entity/security/action permission definition | REJECTED | Owned semantic/registry/invariant data | Never generic settings values |
| Mochi/context/external sharing availability | FUTURE | off; no blanket consent | Separately approved request and explicit Send where external |

Session overrides cannot enable more collection/retention than reviewed admission permits. Invalid/unavailable sensitive settings fail closed for optional persistence/sharing; manual bounded transient workflow only if its safety dependencies remain valid. Actual manual workflow activation default/gates stay distinguishable from OS capture occurring. Settings commit does not prove hotkey/FTS activation; retain last safe applied value and show desired/applied/pending/failure separately. Disabling persistence stops future automatic history, does not delete SAVED/evidence or silently migrate existing data. Storage budgets are resource policy proposals, not unlimited user knobs.

## Database Impact

Architecture only: no SQL, migration number, schema approval or operational DB opened. Search of migrations, repositories and canonical ERD/schema preceded every NEW recommendation. Tables below conceptual names, not mandated physical count.

| Structure / mechanism | Treatment | Rationale / minimal conceptual data |
| --- | --- | --- |
| Existing connection/migration/backup infrastructure | REUSE | FK ON, 5000-ms timeout, checksums/forward history, short transactions; backups may contain eligible content |
| Existing tags/categories | REUSE / EXTEND eligibility | Global Tag identities; no Category requirement for initial Clipboard; CLIPBOARD scope exists |
| clipboard_items | NEW | No migrated store; immutable source/format/profile/hash, Kind/profile, privacy eligibility, TEMPORARY/SAVED/pin, expiry/policy, lifetime summary/revision |
| clipboard_capture_events | NEW | Own occurrence/Item reference/time/method/safe optional class; operation binding; independent shorter history |
| Capture operation receipts | NEW feature-owned extension of acceptance record | Atomic replay/completion evidence, bounded TTL; may share Event representation; no global envelope ledger |
| clipboard_entities | NEW | Source span/profile/version/typed values/provenance; no universal canonical Entity table |
| clipboard_item_tags | NEW | Unique Item/Tag junction/provenance; reuse catalog; no Tag display-name duplication |
| clipboard_ticket_links | NEW conditional owning association | Typed Ticket FK/predicate/source revision/acceptance/hold; existing KB junction cannot fit |
| clipboard_diagnostic_links | NOT VERIFIED physical target / deferred | Durable Diagnostic target absent; no FK to fabricated Session; source-use profile can remain transient until owner design |
| clipboard_kb_links | NOT NEEDED initial mandatory schema | Future explicit derivation/related purpose then typed junction/owner lineage; no automatic publication |
| clipboard_script_links | NOT NEEDED initial mandatory schema | Metadata search/action can use current script ID; durable typed link only justified use |
| clipboard_automation_links | NOT NEEDED baseline | No copied-command execution/automatic trigger |
| Eligible search projection / Clipboard FTS | NEW / ADAPT existing pattern | Item-keyed eligible search_text; conditional FTS, atomic sync, no full raw sensitive index |
| clipboard_snippets, separate URL/command/log/history silo | NOT NEEDED duplicate model | Saved/query views over one Item store meet intent; canonical possible names not physical implementation |
| Shared Settings override/schema/service | REUSE approved 0D architecture; implementation absent | No local replacement; exact APIs/schema under shared owner |
| Generic graph/Entity/ActionRegistry/job/event-bus/audit platform | NOT NEEDED without concrete shared use | Existing owner patterns plus feature evidence; search before later extension |

Field decisions: Item ID stable; raw immutable; identity-normalized column unnecessary duplication in v1; preview derived optionally cached with policy revision; size UTF-8 bytes; first/last/count maintained explicitly because history expires; expires_at plus policy revision; is_pinned independent. No generic ACTIVE/EXPIRED/QUARANTINED flag duplicating policy; expiry derived, blocked attempts have no Item. Redacted status/provenance describes derivative, not hidden retained original. Processing COMPLETE/PARTIAL with per-component versions/issues, no persisted pending job model needed initially.

Local durable IDs follow existing positive integer conventions; operation UUID distinct. Stable fields/FKs/junctions normalized, parameterized input, no arbitrary metadata_json bags. Compare/reload/update source and links in one owner transaction. Future deletion restrictions/indexes/constraints/integrity_check and foreign_key_check must be executed on isolated fixtures before implementation integration; no DB validity claimed here.

## Service Architecture

| Responsibility | Recommendation / treatment | Existing fit / dependencies / future tests |
| --- | --- | --- |
| ClipboardService | NEW cohesive application use cases | Own capture/policy/lifecycle/search/projection/association intent; injected repo/settings/catalog/owner references; unit/contract/failure tests |
| ClipboardRepository | NEW normal relational mechanics | ADAPT existing writer reservation/mapping/rollback patterns; no GUI/network/policy; DB atomicity/replay/race tests |
| Sensitivity/Normalizer/Dedup/Classifier/Extractor/TagRules | NEW pure feature responsibilities | REUSE validator/dataclass conventions and 0C profiles; no need separate services/classes/platform; adversarial/unit/Unicode tests |
| Retention | NEW policy responsibility within service/pure module | REUSE finite worker for bounded calls; no permanent scheduler; race/expiry/holds tests |
| Tag reads | REUSE TagRepository; EXTEND eligibility if actual feature needs | Current global read API; no fabricated TagService implementation; assignment compatibility/tests |
| Search | ADAPT existing repository/literal-query pattern | Clipboard-owned query API, optional universal integration later; privacy/index tests |
| Ticket/Diagnostic/Knowledge/Script integration | REUSE owning authority; EXTEND narrow use case only when approved | Current services do not magically expose Clipboard attach/durable sessions/input execution; stale-ref/partial-action tests |
| Bootstrap / GUI task adapter / logging | REUSE | Explicit composition, off-event-loop finite work, GUI-thread render, safe logs; integration/native tests later |
| Clipboard capture transport | DESIGN NEXT, not implementation | 1B owner-specific ingress/producer/HUD security under 0B; no cosmetic v1 reuse |

No speculative microservice split, generic plugin, parser registry/database, daemon, dependency or provider framework. New pure profiles packaged/versioned by Clipboard owner; reuse approved vocabulary and actual standard-library support after verifying parser docs during implementation.

## Contract Usage

Consume seven-field 0B envelope: contract, schema_version, message_class, message_id, created_at, producer, payload. Initial proposed profile version 1.0. Response has own ID/correlation_id=request message_id. Optional context only declared bounded owner refs, Ticket absent valid. Strict UTF-8 JSON/closed safety fields, safe missing/null/unknown semantics, canonical decimal-string DB IDs, UTC millisecond wire instants, actual booleans. No copied DB model/raw provider dump. New enums/meaning changes compatibility reviewed. No schema/runtime endpoint written.

| Contract / class | Proposed use / disposition |
| --- | --- |
| clipboard.capture / COMMAND | Baseline explicit bounded capture intent |
| clipboard.result / RESULT | Valid accepted durable or memory-only outcome; bounded safe summary |
| contract.error / ERROR | 0B pinned safe failure: classified code/message/retryable if known, safe correlation only |
| clipboard.captured / EVENT | Optional post-commit eligible fact, not admission/ACK/result and no raw content; NOT NEEDED initial mandatory transport |
| clipboard.lookup / QUERY | Future operation receipt/current Item read profile, not mutation or new capture |
| clipboard.process / COMMAND | Explicit future reprocessing over existing eligible Item/revision; not baseline extra hop |
| clipboard.action_request / COMMAND, action_result / RESULT | Later approved routing to owning operation; no arbitrary command text |

Capture payload semantics: operation_id; current producer/ingress-generation binding; observed_at with availability reason if source instant unknown; capture_method closed AHK_MANUAL/F7HUB (AHK_AUTOMATIC/IMPORT future separate profile); content {format=text/plain, text}; optional coarse allowlisted source class, no raw title/source URL; explicit requested persistence intent within policy, no implicit Attach/Run. Byte/scalar limits enforced independently; declarations don't replace measured size. Ticket reference only if initiating action explicitly bound, never inferred from text. Producer claims untrusted.

Result semantic required core: COMPLETED (accepted), disposition, duplicate boolean when Item resolution performed, capture_event_created, typed Item/Event reference when available, processing completeness, safe component issue codes, effective preservation summary. MEMORY_ONLY explicitly not saved; BLOCKED/rejection ERROR not COMPLETED saved. For accepted duplicate, existing Item ref and new Event ref returned; replay returns original event/ref with replayed indication and no new effect. Receipts with deleted/unavailable source yield explicit unavailable/known-completed observation, not a fresh successful current-content capture.

Optional result Kind, safe redacted preview, Entity Type/count summary, accepted Tag IDs, available action keys only within privacy/budget. Full raw text/history/occurrence arrays not immediate HUD result. Response cap proposal <=16 KiB UTF-8; overflow omits optional detail with explicit detail availability/counts, never truncates JSON. Full source/Entities through separately authorized bounded Inspector query. Safe ERROR <=16 KiB and 0B code/message bounds; no raw payload/exception.

Sender preflight and Python ingress independent. Actual IPC peer authentication/binding, framing/leases/rate/backpressure/reconnect/deadline/security proof DESIGN NEXT in 1B; checkout ID/same-user socket/valid producer string insufficient trust for sensitive channel. No known-secret IPC; no ordinary log/evidence of secret payload. Limits remain <=64-KiB inline/128-KiB complete capture, stricter global bounds unchanged.

## Failure / Transaction Model

Pre-transaction: peer/contract/content/size/sensitivity, normalization/Kind/Entities/Tag proposals, policy snapshot, resource estimates and target proposal checks. All parsing expensive work outside write lock. Validate generated spans and proposed metadata. Abort/cancel before core means no accepted Event, but cancellation does not modify OS clipboard.

Atomic core: writer reservation → receipt/conflict recheck → resolve collision-safe Item → create/update permitted operational summary/lifecycle → exactly one Event/receipt → accepted validated occurrences/assignments → eligible search projection and FTS synchronization → reload authoritative outcome → commit. Privacy/preservation preconditions rechecked; stale snapshot produces conflict/retry preparation, no permissive fallback. No network/IPC/GUI/classifier inside transaction.

Known classifier/extractor/suggestion failures before core can omit failed optional derived component, mark PARTIAL and commit safe core. Once a planned core child/index/receipt write starts, any DB failure rolls back all core; do not silently ignore broken INSERTs. A separately requested Tag assignment or evidence relationship is a later operation with its own atomic unit; failure leaves previously captured Item intact and returns explicit failure for that action.

Post-commit: return outcome; targeted UI notification; optional approved safe facts/context; user-requested follow-on actions through owning services. Observer/read failure cannot pretend commit rolled back. Retry read/receipt query, not capture again. Current runner clears busy before callback; future callers retain pending/generation guard until authoritative completion delivery, matching existing GUI precedent.

~~~mermaid
sequenceDiagram
    participant A as AHK or PySide6 adapter
    participant V as Boundary validator
    participant S as ClipboardService
    participant P as Pure policies
    participant R as ClipboardRepository
    participant D as SQLite
    A->>V: Manual snapshot and immutable operation identity
    V->>S: Valid bounded authorized request
    S->>P: Complete sensitivity then eligible derivation
    P-->>S: Eligible data or safe rejection
    alt Ineligible
        S-->>A: Safe correlated ERROR, no raw echo
    else Eligible durable capture
        S->>R: Prepared data and expected policy
        R->>D: Begin writer transaction
        R->>D: Recheck operation, resolve Item, Event and children
        alt Core write failure
            R->>D: Roll back
            R-->>S: Classified persistence failure
            S-->>A: ERROR, never saved
        else Commit succeeds
            R->>D: Commit including receipt and eligible FTS
            R-->>S: Authoritative Item and Event outcome
            S-->>A: COMPLETED durable result
            Note over S,A: Post-commit presentation failure does not undo capture
        end
    else Eligible memory only
        S-->>A: COMPLETED MEMORY_ONLY, bounded transient references
    end
~~~

### Failure matrix

Fatal means fatal to requested capture core unless noted action/search scope. Retryability never permission to replay automatically. Safe logging uses classified codes/validated IDs only.

| Failure | Fatal? | Persist? | Retry / partial | User-visible outcome | Safe logging |
| --- | --- | --- | --- | --- | --- |
| Invalid contract/version/identity/peer | Yes | No | Correct input/new authorized intent; malformed framing may close, no reply | CONTRACT_VALIDATION_FAILED/UNSUPPORTED_VERSION/denied | WARNING classification, no bytes |
| Empty/whitespace-only | Yes | No | New capture when content changes | EMPTY_CLIPBOARD | INFO code only |
| Unsupported format | Yes | No | New supported snapshot, not repeated conversion | UNSUPPORTED_CONTENT_TYPE | INFO format class only if safe |
| Oversize/content or escaped frame | Yes | No | Explicit smaller selection/new operation or approved future reference | PAYLOAD_LIMIT_EXCEEDED, no truncation | INFO size class |
| Possible secret | Yes | No raw/Event/hash | No persist override; separately sanitized new capture | CLIPBOARD_SECRET_BLOCKED | INFO safe generic code, no detector span/value |
| Sensitivity failed/incomplete | Yes | No | After repaired policy/component only | CLIPBOARD_PRIVACY_CHECK_FAILED | ERROR method/code, no content |
| Kind classifier failure | No | Safe core | PARTIAL unknown, explicit reprocess | Captured with classification unavailable, storage mode clear | WARNING component/code |
| Entity parser failure/cap | No if privacy gate complete | Valid safe subset/core | PARTIAL; no bad spans; explicit bounded reprocess | Captured, extraction incomplete | WARNING component/count if eligible |
| Pre-core Tag suggestion unavailable | No | Core, no unsupported assignment | PARTIAL if promised processing unavailable; suggestions not assignments | Captured, Tags unavailable | WARNING safe catalog/code |
| Planned core child/Tag write fails | Yes | Rollback entire core | Retry same still-admissible operation after cause repair | CLIPBOARD_PERSISTENCE_FAILED | ERROR exception class/code only |
| Database/commit/receipt failure | Yes or uncertain commit | No success until receipt reconciliation | Same-op query before redispatch if commit uncertain; no new operation | Persistence failure or local UNCERTAIN observation | ERROR no SQL/value dump |
| FTS/projection write in core | Yes | Rollback core | Repair/retry same admissible operation; never auto-disable index to claim success | Persistence/index failure | ERROR code |
| Existing FTS read/rebuild failure | Search operation fatal | Existing source preserved | Search unavailable, explicit bounded repair; no raw unsafe fallback | Search error | ERROR safe code |
| Post-capture Tag assignment failure | That action only | Capture remains; assignment transaction rolled back | Explicit retry with current revision | Tag action failed; capture stays acknowledged | WARNING/ERROR action code |
| Relationship/evidence failure | That action only | Capture remains; no link/hold claimed | Fix target/policy, explicit current intent retry | Attach failed, Item still captured | WARNING/ERROR reference class/code |
| Same operation changed payload | Yes | No new effects | No blind retry; new genuine intent identity only | CLIPBOARD_OPERATION_CONFLICT | WARNING IDs/code |
| Late/retired-generation replay | Yes | No new effects | Receipt lookup only, not capture | CLIPBOARD_OPERATION_STALE | INFO code |
| Capacity exhausted | Durable admission fatal | No durable write, optional explicitly permitted transient | Visible MEMORY_ONLY or capacity error, never saved | CLIPBOARD_CAPACITY_EXCEEDED | WARNING coarse class |
| Lost response after commit | Observation uncertain | Committed core remains | Query receipt; no duplicate Event | Local UNCERTAIN until reconciled | WARNING validated ID/code |
| Post-commit UI/context/Analytics failure | No to capture | Committed capture remains | Retry safe read/notification only | Capture committed; enhancement unavailable | WARNING callback/component |

Do not claim cancellation after completed commit. A safe pre-commit cancellation yields no core effect; after dispatch/commit uncertainty query authoritative completion. No general cancellation endpoint exists today; 1B defines its transport/use-case limits without false rollback promises.

## Existing Architecture Reuse

| Mechanism | Current owner/layer/consumers | Fitness / treatment / evidence |
| --- | --- | --- |
| Script verified copy | ScriptService + ScriptWorkspace, service/presentation | REUSE outward integrity/current-selection precedent; no inbound truth (E-COPY); copy tests inspected only |
| Shared AHK host | Desktop host/guide, launcher/global/scoped keys | EXTEND capture adapter later; preserve F7/Alt+F7/fixed guide bridge (E-AHK) |
| DB connections/migrations | Infrastructure, all repos/bootstrap | REUSE guards/forward migrations/transaction patterns; runtime integrity NOT RUN (E-APP) |
| Tag catalog/category scopes | Shared taxonomy repository, current Knowledge/Ticket/Script readers | REUSE IDs, EXTEND consumer eligibility; no Clipboard-private catalog (E-TAX) |
| Knowledge FTS/literal queries | Knowledge service/repository, workspace | ADAPT eligible-index/filter patterns; separate source owner (E-KB) |
| Ticket–KB writer link pattern | Application association service/repository | ADAPT FK/race/atomic link/unlink, not relation endpoints (E-TICKET) |
| Diagnostics/PowerShellService | Execution owner, scripts/workspace | REUSE registered identity/validation; unsupported Clipboard inputs/durable sessions deferred (E-PS) |
| ServiceTaskRunner | GUI infrastructure, finite service calls | REUSE off-thread work/GUI callback; add future pending guard, no daemon (E-APP) |
| Technical logger / Ticket activity | Infrastructure / Ticket domain | REUSE safe logging and owner activity; neither substitutes feature-required audit (E-APP/E-TICKET) |
| Mochi cosmetic channel/subscribers | Mochi service/gateway/renderer | NOT RELATED to raw Clipboard transport; ADAPT subscriber precedent only for approved projections (E-MOCHI) |
| Central Settings architecture | Approved future 0D, application owner | REUSE contract, no current API assumed (E-DOC/0D) |
| Generic Entity/classifier/graph/job registry | None established in searched inventory | NEW pure feature profiles as needed; universal replacement NOT NEEDED |

No REPLACE/DEPRECATE recommendation justified. For future table/service/registry/settings/parser action: search current source/docs/migrations/tests again, identify owner, reuse/extend first. New suggestions here are conceptual only.

## Dependency Map

~~~mermaid
flowchart LR
    UI[AHK or PySide6 presentation] --> C[Clipboard application service]
    C --> P[Pure Clipboard policies using 0C profiles]
    C --> R[Clipboard repository]
    R --> DB[Existing SQLite infrastructure]
    C --> S[Injected 0D Settings snapshot]
    C --> T[Existing Tag catalog read boundary]
    U[Explicit association or action use case] --> C
    U --> O[Ticket Knowledge Diagnostics Script owning services]
    Q[Application selected context projection] --> C
    Q --> M[Optional approved Mochi adapter]
    A[Optional Analytics reader] --> F[Eligible Clipboard facts]
    F --> R
~~~

Runtime dependency arrows indicate consumption/invocation, not new services or circular callback permission. Clipboard knows operation/domain contracts, not AHK internals, Mochi implementation, Analytics GUI or raw PowerShell process APIs. Association owner orchestrates both sides; no Ticket→Clipboard→Ticket construction loop. Settings common mechanics do not call Clipboard use cases; pure definitions avoid reverse imports. Fact/context consumers cannot mutate source or become prerequisite.

## Decision Register

Statuses deliberately exclude APPROVED. All DECIDE NOW recommendations require the candidate's later review/USER approval/integration; recommendations are not unilateral implementation authority.

| ID / decision | Options | Recommendation / reason / evidence | Consequence | Status / depth |
| --- | --- | --- | --- | --- |
| D01 Item/Event | One row per copy; dedup Item+occurrences | Separate identities, all genuine eligible occurrences; original invariants/0B | Frequency without duplication | RECOMMENDED / DECIDE NOW |
| D02 Replay identity | Hash; message only; bound operation | Explicit producer/generation-bound operation receipt and unchanged logical message | No double Event, stale generations reject | RECOMMENDED / DECIDE NOW |
| D03 Dedup key | Raw; LF/NFC merge; topic/source key | Exact text+format+profile/scope, hash bucket/full compare | Raw variants distinct; no source destruction | RECOMMENDED / DECIDE NOW |
| D04 Normalization | Destructive shared fold; identity/search separation | Exact identity, LF/NFC derived search; 0C raw/profile rule | Versioned search, raw offsets intact | RECOMMENDED / DECIDE NOW |
| D05 Primary Kind | Many overlapping enums; whole shape+Entities | Small inventory/fallback/recognizer precedence; 0C | No Kind as state/permission | RECOMMENDED / DECIDE NOW |
| D06 Entity storage | Universal business Entities; source occurrences | Source-bound typed spans/profile/provenance | No canonical auto-create | RECOMMENDED / DECIDE NOW |
| D07 Offsets/repeats | Normalized/UTF16; raw scalar spans | Raw half-open scalar ranges; distinct spans, nested allowed | Explicit native conversion tests | RECOMMENDED / DECIDE NOW |
| D08 Tags | Private catalog; immediate auto assignment; suggestions | Global identity, post-extraction suggestions/manual acceptance; reviewed automation later | Missing catalog suppresses, no auto-create | RECOMMENDED / DECIDE NOW |
| D09 Sensitivity | Adopt invented legal enum; feature findings | PERMITTED/NEEDS_REVIEW/POSSIBLE_SECRET separate from disposition | Compatible with 0C/privacy, no legal claim | RECOMMENDED / DECIDE NOW |
| D10 Secrets | Quarantine/raw override; reject/sanitize derivative | Block recognized/suspected secret, no persistent hash, no bypass | False positives inconvenience; false negatives residual | RECOMMENDED / DECIDE NOW |
| D11 History | Always durable; opt-in | Off default, bounded transient; explicit single Save permitted | Useful local work/minimal collection, 0D aligned | RECOMMENDED / DECIDE NOW |
| D12 Retention | TEMPORARY+RECENT+PINNED enum; orthogonal model | TEMPORARY/SAVED intent, pin property, evidence holds | Simple deterministic precedence | RECOMMENDED / DECIDE NOW |
| D13 Save/Pin/Evidence | Interchangeable; independent reasons | Pin saves; unpin stays saved; evidence explicit accepted hold | No accidental unpin evidence loss | RECOMMENDED / DECIDE NOW |
| D14 Expiry Settings | Immediate mass recalc; prospective | Bound expiry, genuine duplicate refresh, explicit reapply only | No Settings-driven purge | RECOMMENDED / DECIDE NOW |
| D15 Event summary | Derive forever; cache without semantics | Short Event history, maintained lifetime summary, held occurrence claim survives | Counts honest after pruning | RECOMMENDED / DECIDE NOW |
| D16 Large text | Raise caps; silent trim; reject baseline | Respect 0B 64/128-KiB caps; managed refs future | No new binary/file bypass | RECOMMENDED / DECIDE NOW |
| D17 Soft/hard delete | Raw recycle bin; hard deletion | Hard delete eligible source/children; holds gate evidence | No forensic erase promise | RECOMMENDED / DECIDE NOW |
| D18 FTS | Index all raw; eligible projection; none | Optional eligible projection/atomic sync, sensitive non-FTS | No KB silo reuse/privacy leakage | RECOMMENDED / DECIDE NOW |
| D19 Links | Generic graph; typed owner relations | Typed FK/owner association, durable target prerequisite | Diagnostics target absent remains unavailable | RECOMMENDED / DECIDE NOW |
| D20 Auto capture | Early broad monitor; defer | Manual MVP, automatic off/deferred with privacy/rate review | No host hooks now | DEFERRED / DEFER UNTIL IMPLEMENTATION |
| D21 Analytics | Raw/literal feed; minimal facts | Eligible coarse projection, explicit grains, no deletion exemption | Optional derived consumer | RECOMMENDED / DECIDE NOW |
| D22 Mochi | History/raw dump; selected projection | Explicit safe selected refs/summaries, external preview/Send later | No circular dependency/advisory authority | RECOMMENDED / DECIDE NOW |
| D23 Transaction | Parse under lock; atomic prepared core | Preprocess outside, core all-or-nothing, post actions separate | No success on failed core, clear partial components | RECOMMENDED / DECIDE NOW |
| D24 Limits/latency | Unlimited; arbitrary factual performance | Bounded proposals/targets; measure fixtures before release | Capacity refusal preserves held work | RECOMMENDED / DECIDE NOW |
| D25 Source context | Raw titles/URLs; coarse/off | Off default; optional allowlisted class, titles excluded | Reduced provenance detail/privacy impact | RECOMMENDED / DECIDE NOW |
| D26 Audit | Logs as audit; generic platform; feature evidence | Minimal purpose-owned evidence; activate only when required path exists | Later reviewed implementation gate | RECOMMENDED / DECIDE NOW |
| D27 Exact IPC/HUD/hotkey/native identity binding | Repurpose legacy; new owner profile | 1B designs under fixed 1A and 0B security/limits/replay | No 1A domain redefinition | DEFERRED / DESIGN NEXT |
| D28 GUI layout/routing/filter presentation | Implement now; consume model later | 1C designs typed Item views/Inspector/stale guards | No data silos/reinterpreted semantics | DEFERRED / DESIGN NEXT |
| D29 Binary/OCR/AI/managed storage/automatic monitor | Premature broad design; defer | Separate justified feature slices after owner/privacy review | No baseline dependencies | DEFERRED / DEFER UNTIL IMPLEMENTATION |
| D30 Employer/provider/installed-runtime/secure erase facts | Assume; verify at release | NOT VERIFIED; conservative exclusions until actual policy/tests | No current deployment assurance | NOT_VERIFIED / DEFER UNTIL IMPLEMENTATION |

## Requires User Decision

NONE at Phase 1A planning depth. Safe conservative recommendations resolve core semantics without selecting a credential provider, authentication redesign, destructive migration or major dependency. User approval of the exact architecture remains required after independent review. That lifecycle gate is not an invented unresolved design choice. A later real policy requirement could reopen its owning decision; it cannot silently bypass secret/evidence invariants.

## Assumptions

ASSUMPTION A01: first Clipboard use case is one local technician/application data scope, consistent with 0D; no shared enterprise ACL/tenant hierarchy inferred.

ASSUMPTION A02: manual text capture/optional history is the bounded first feature; binary/automatic/provider workflows not necessary to answer this contract.

ASSUMPTION A03: typical manual snippets fit approved 0B inline bounds; larger logs are safely rejected until justified managed storage. No observed size distribution supports a performance claim.

ASSUMPTION A04: a future approved local association use case can coordinate owning source/target checks and required evidence atomically where shared SQLite supports it. Current APIs do not establish that future capability.

Each assumption has a safe failure: unsupported scope/workflow refuses widening; oversize refuses; unavailable owner/association reports unavailable; no secret/evidence/authority workaround.

## Not Verified

Operational database rows/integrity/backups; native clipboard access/sequence/races; active hotkey conflicts/host registrations; installed runtimes/SQLite tokenizer or secure-delete support; actual Windows transport peer authentication/path/locking; production memory/latency/storage distributions; employer/customer retention/disclosure policy; external provider/account/permissions/credentials/data terms; future shared Settings/catalog lifecycle/Context/Evidence/Diagnostic history APIs; physical erase/OS clipboard/paging/crash dump behavior. These are release/use-case verification gates, not evidence that current features are implemented.

No live clipboard, customer content, credential, operational DB or protected GuideSettings.ini inspected. Whole downstream 1B/1C and whole canonical documentation tree not audited. Unsampled areas NOT VERIFIED. Foundation approvals historical architecture inputs; no retained upstream runtime test claimed fresh.

## Risk Register

Likelihood UNKNOWN throughout: source/planning evidence supplies mechanisms, not defensible operational probabilities. Impact qualitative, no invented rates. Mitigations architectural and future tests, not deployed certification.

| Risk | Trigger / impact | Mitigation | Residual / owner / status |
| --- | --- | --- | --- |
| Clipboard privacy | Unintended customer/personal retention/exposure; HIGH impact | Manual/off-default/bounded data/source minimization/explicit purpose | Policy unknown; Clipboard/security, OPEN |
| Secret leakage | Detector false negative/pre-gate logging/IPC; CRITICAL | Mandatory preflight+ingress, no raw logs/history/hash, outbound off/explicit review | Detection imperfect, memory/OS outside guarantee; security/1B, OPEN |
| Unbounded storage | History/Event growth; HIGH | TTL/budgets/bounded cleanup/refuse admission, preserve holds | Real volumes unmeasured; Clipboard, OPEN |
| Duplicate explosion | Retried transport/concurrent resolve; HIGH | Bound operation receipt/generation fence/full equality transaction | Actual producer restart/native fixtures pending; 1B/repository, OPEN |
| Over-normalization | Evidence/command/URL altered; HIGH | Exact raw identity, distinct search/version, no silent profile merge | Similar raw variants remain separate; Clipboard, OPEN |
| Entity false positives | Misidentified host/user/Ticket; HIGH | Context profiles/provenance/ambiguity, no auto-create/actions | Parser profiles untested; taxonomy/Clipboard, OPEN |
| Tag noise | Unreviewed automatic topical assignments; MEDIUM | Global catalog, suggestions/manual acceptance, versioned approved rules | Suggestion relevance unmeasured; taxonomy, OPEN |
| Large-content latency | Adversarial parsing/huge logs; HIGH | Approved byte/frame/occurrence limits, no event-loop work | Targets unmeasured; Clipboard/1B, OPEN |
| FTS growth/privacy | Broad raw index or stale shadow entries; HIGH | Optional eligible projection/atomic sync, deletion tests | Physical traces/backups remain; repository/security, OPEN |
| Relationship coupling | Clipboard writes internals/fabricates session; HIGH | Owning services/typed profiles/current capability checks | New association API absent; owner integration, OPEN |
| Retention data loss | TTL/unpin/target cascade erases evidence; HIGH | Intent/hold precedence, Unpin stays SAVED, last-hold review, race recheck | Release/migration policy needs tests; Clipboard/target, OPEN |
| Automatic capture overreach | Global monitor captures all apps; HIGH | Off/deferred/manual MVP, no early hooks | Future exclusions/teardown review required; 1B/security, OPEN |
| Mochi privacy exposure | Context or raw history forwarded; HIGH | Explicit selected safe projection, current v1 unchanged, preview/Send | Provider/policy not verified; Mochi/security, OPEN |
| Analytics privacy leakage | Literal dimensions/hash reidentification; HIGH | Coarse eligible facts/grains/access/deletion policy | Even IDs/time identify behavior; Analytics/security, OPEN |
| Replay-window expiry | Evicted receipts reaccept stale operation; HIGH | Retired-generation fence/admission lease, no new acceptance after eviction | Transport/restart implementation pending; 1B, OPEN |
| Unicode span divergence | UTF16/scalar/grapheme confusion; MEDIUM/HIGH | Raw half-open scalar ranges and explicit native conversions | Emoji/bidi/combining fixtures pending; 1B/1C, OPEN |
| Capacity/preservation conflict | Saved/evidence fills budget; HIGH | Refuse new durable admission, visible inventory, never evict holds | User capacity planning needed; Clipboard, OPEN |
| Commit acknowledgement uncertainty | Lost reply/retry duplicates or false failure; HIGH | Atomic receipt and reconciliation, no success/cancel guess | Fault-injection/native transport pending; 1B/repository, OPEN |
| Audit activation gap | Logger mistaken for durable change evidence; HIGH | Sensitive activation depends on required reviewed evidence path | No current generic writer; security/use-case, OPEN |
| Planned-as-implemented | Architecture PASS treated runtime readiness; HIGH | Separate labels/matrices/NOT RUN/next lifecycle gate | Future agents/review must maintain boundary; reviewer, OPEN |
| Protected unrelated state | Broad scan/write/stage reaches INI/DB; HIGH | Explicit source allowlists/sole tracked write/path-only inventory | No protected hash deliberately; author/reviewer, MITIGATED for task |

## Testing Implications

No runtime tests run for architecture authoring. Future implementation must cover meaningful success/failure/cancellation/recovery, isolated synthetic data and bounded native supervisors.

| Future test | Environment / required assertion |
| --- | --- |
| Item/Event/replay/collision/concurrency | CLOUD_PORTABLE logic/SQLite fixtures; identical genuine captures distinct Events/one Item, transport replay one Event, forced digest collision distinct Items |
| Exact identity/search profile evolution | CLOUD_PORTABLE; whitespace/case/CRLF/JSON/URL signatures preserved, NFC search does not merge; no source mutation |
| Unicode/English/French spans | Portable pure conversion plus WINDOWS_NATIVE AHK/Qt presentation; scalar/UTF16/emoji/combining/CRLF/bidi parity, no invalid highlights |
| Secret/privacy adversarial cases | Portable policy/contract and WINDOWS_NATIVE producer/channel; known/suspected credentials never ordinary IPC/log/DB/FTS/context; failure closes |
| DB atomicity/FTS/Tag/receipt failure | Portable isolated DB; injected each core failure rolls back; integrity_check ok/foreign_key_check zero; no operational DB |
| Lifetime/holds/target delete races | Portable DB; Save/Attach vs cleanup, last-hold release/rearm, unpin, TTL changes, target orphan and promoted occurrence preservation |
| Search/filter/index rebuild/deletion | Portable; one Item per joined result, exact Entity query, sensitive excluded, deleted index no retrieval; version/trace limitations explicit |
| Lost ACK/restart/lease/cache capacity | Portable protocol model plus native cross-process fixtures; stale generation cannot create Event, receipt reconciliation truthful |
| Large/escaped payload/adversarial parsing | Portable boundary plus native producer; both caps, no silent trim, bounded work/resource refusal |
| GUI pending/stale completion/closing | Portable headless eligible behavior plus native focus/DPI/HUD; pending covers callback gap, no retarget |
| AHK hook/hotkey/clipboard races | WINDOWS_NATIVE, finite input/read retries/external timeout/released modifiers/test-owned cleanup; preserve existing F7/Alt+F7/native copy |
| Integration/observer failure | Portable owner stubs; committed capture survives optional observer/action failure, no false attach or execution |
| Performance/storage/cleanup | Synthetic workloads 1k/10k Items, 100k Events; measure p95/p99/size/caps, separate native GUI latency |

Targets only, NOT VERIFIED measurements: small sensitivity/classification/extraction preparation p95 <100 ms; small manual end-to-end accepted acknowledgement p95 <250 ms; paged common-query p95 <150 ms on declared local reference hardware/data. Medium pipeline target <1 second with finite progress/busy response, no claimed achieved latency. Failure to meet targets narrows/tunes work under same privacy/evidence semantics, never disables gates.

## Documentation Impact

Only this target changed. No canonical synchronization of proposed behavior as implemented. After review/approval and separately authorized delivery: Docs03/04 feature/workflow, Docs05 Inspector/views, Docs06/13 ownership/service/bootstrap, Docs07/08/09 exact approved schema/queries/retention, Docs11 AHK capture/IPC/HUD, Docs14/15 relevant security/naming, Status/CURRENT_STATE and ChangeLog actual lifecycle/evidence. Docs12 only if separately approved Diagnostic input boundary changes; no widening from this plan. Foundation owners unchanged; link instead of duplicating their policies.

Potential canonical clipboard_snippets/history examples reconcile with single Item/SAVED/view model at future authorized architecture-sync gate, preserving historical meaning. No migration number reserved, no class/table created, no 1B/1C edit or execution.

## Recommended Phase 1B Inputs

Conditional downstream contract, authoritative only after independent 1A review → explicit USER approval → controlled integration:

1. Manual text/plain; existing AHK host retained. Clipboard contents never select authoritative Ticket. Native clipboard left unchanged by capture, no known-secret transport.
2. Item/Event/operation identity distinction and genuine-new-capture vs immutable retry fixed. Domain UUID, producer binding/generation/admission lease/receipt reconciliation required; no hash-based transport dedup.
3. Exact raw identity/full collision comparison; separate LF/NFC search profile; immutable source/version; no dedup Settings bypass.
4. Mandatory complete privacy gate before persistence/exposure; off-default history; secret rejection/no raw override; memory-only vs saved truthful; redacted new snapshot only.
5. TEMPORARY/SAVED intent, pin saves/unpin stays saved, evidence hold independent, last-hold release explicit, prospective expiry and cleanup rechecks.
6. 0C profiles/global Tags; raw scalar half-open occurrences/nested/repeated spans; no canonical creation; initial topic suggestions/manual acceptance.
7. Both 0B caps 64-KiB content/128-KiB message; <=16-KiB proposed result; oversize/unsupported safe rejection, no file-path bypass.
8. Preprocess outside write transaction; atomic durable acceptance/receipt/children/eligible FTS; partial optional interpretation explicit; no saved result before commit; post-commit actions separate.
9. Source context off/minimal coarse class; titles/browser URLs excluded. Available action is proposal, current Diagnostic input execution unsupported.
10. 1B owns exact hotkey/native reads/sequence races, JSON composite payload/fixtures, sensitive peer security/framing/rate/backpressure/lease/reconnect/restart, dispatch deadlines/HUD/accessibility/focus and native tests. It must not reinterpret fixed domain semantics.
11. 1C later consumes typed Item views, safe summary/Inspector/raw content availability, component partial status, event-history horizon/lifetime counters, holds/privacy/actions. Layout/columns/paging UX does not redefine source identity/retention.
12. Any genuine 1A conflict returns to 1A owner; shared Foundation conflict returns named phase. No local patch/redefinition or execution authority from candidate self-result.

## Phase 1A Acceptance Criteria

FRESH author-side architecture/documentation assessment, not independent review or runtime verification. Criterion wording preserved exactly from original section 163.

| # | Criterion | Result | Supporting report section / evidence |
| --- | --- | --- | --- |
| 1 | Existing Clipboard-related architecture has been inspected. | PASS | Repository Areas/Verified State, E-COPY/AHK/TAX/KB/TICKET/PS/APP/MOCHI/DOC |
| 2 | Clipboard Item and Capture Event are clearly separated. | PASS | Vocabulary/Invariants/Three identities |
| 3 | Deduplication semantics are defined. | PASS | Exact profile/scope/format/full collision comparison |
| 4 | Raw vs normalized content is defined. | PASS | Identity vs search profiles, immutable raw |
| 5 | Content hashing is defined conceptually. | PASS | Domain-separated length tuple, no secret hashing |
| 6 | Clipboard primary Kinds are inventoried. | PASS | CORE/LIKELY/FUTURE/REJECTED inventory/precedence |
| 7 | MVP Entity Types are identified. | PASS | 0C mapped MVP/LATER/NOT APPLICABLE inventory |
| 8 | Entity occurrence semantics are defined. | PASS | Raw scalar half-open spans, source version, nested/repeated occurrences |
| 9 | Tag assignment boundaries are defined. | PASS | Global catalog, suggestions/manual acceptance/provenance |
| 10 | Sensitivity handling is defined. | PASS | Feature assessment vs disposition, ordered gates/privacy matrix |
| 11 | Secret handling is defined. | PASS | Block/no quarantine/hash/override; false positives/negatives |
| 12 | Retention semantics are defined. | PASS | Two intents/property/holds/expiry/cleanup |
| 13 | Save, Pin, and Evidence are clearly distinguished. | PASS | Save intent, Pin saves/property, Evidence accepted hold |
| 14 | Cleanup behavior is defined. | PASS | Bounded transactional rechecks/cascades/target restrictions |
| 15 | Large-content policy is defined. | PASS | Content/message limits and size matrix/safe rejection |
| 16 | Search requirements are defined. | PASS | Item identity/views/structured filters/Inspector |
| 17 | FTS5 impact is evaluated. | PASS | Existing E-KB, eligible projection/sync/failure/deletion |
| 18 | Ticket relationships are defined. | PASS | EVIDENCE_FOR/owner validation/hold/no internal writes |
| 19 | Diagnostic relationships are defined. | PASS | Input vs evidence, durable target prerequisite, unavailable current capability |
| 20 | Analytics exposure is defined. | PASS | Eligible facts/grains/no literals/deletion independence |
| 21 | Mochi exposure is defined. | PASS | Selected safe context, no prerequisite/raw default, future disclosure gate |
| 22 | AHK responsibilities are bounded. | PASS | Adapter triggers/snapshot/preflight/HUD, no persistence/taxonomy truth |
| 23 | Python responsibilities are bounded. | PASS | Service/pure policies/repository/owning service maps |
| 24 | Database impact is assessed without migrations. | PASS | Structure/field/reuse matrix, no SQL/number/DB access |
| 25 | Service impact is assessed without implementation. | PASS | Minimal responsibilities/reuse/dependency map |
| 26 | Failure behavior is defined. | PASS | Failure matrix/pre-core/atomic/post-commit/uncertain/cancel rules |
| 27 | Privacy risks are addressed. | PASS | Privacy/source/log/audit matrices and risk register |
| 28 | No production code has changed. | PASS | Sole tracked target scope, empty index, final inventories |
| 29 | Phase 1B can now design AHK ↔ Python Clipboard integration without redefining the Clipboard domain. | PASS | Conditional downstream contract fixes identities/privacy/retention/profiles; exact transport DESIGN NEXT |
| 30 | Phase 1C can later design Clipboard Center GUI without redefining data semantics. | PASS | Query views/Inspector/reference units/preservation/action/partial status fixed |

30/30 PASS at architecture-planning depth only. Recommendation acceptance is not USER approval, implementation or measured runtime.

## Validation

Environment: WINDOWS_NATIVE host. Provenance: FRESH author-side source/document checks; no retained runtime results represented as current. Static checks do not certify native application behavior.

| Check | Result | Evidence / limit |
| --- | --- | --- |
| Initial baseline/origin/live main/target blob/checkout | PASS | Required commands, expected identities/size/hash, clean tracked/index |
| Foundation identity/closure/input use | PASS | Five exact blobs, merge history, PR #71; full 0E and targeted approved owners |
| Current-state inspection | PASS | Bounded source/docs/tests inventory, absence claims scoped |
| Clipboard domain model | PASS | Vocabulary/ownership/conceptual diagram |
| Item/Event separation | PASS | Three distinct identities/invariants/receipt semantics |
| Deduplication model | PASS | Exact equality/hash collision/concurrent resolve |
| Normalization model | PASS | Separate identity/search/version/raw evidence |
| Kind classification | PASS | Inventory/precedence/fallback |
| Entity model | PASS | 0C mapping/source/units/overlaps/completeness |
| Tag integration | PASS | Catalog/suggestion/assignment/provenance |
| Privacy/sensitivity | PASS | Ordered gates/secret behavior/matrices/no bypass |
| Retention/lifecycle | PASS | Intent/pin/holds/expiry/decision table/race/deletion |
| Large-content handling | PASS | 0B caps/size matrix/no bypass |
| Relationship model | PASS | Typed owner profiles/evidence preservation/unavailable targets |
| Search/FTS impact | PASS | Existing pattern/eligible projection/atomic consistency |
| Analytics boundary | PASS | Minimal facts/privacy/grain/deletion independence |
| Mochi boundary | PASS | Explicit safe context/optional dependency/advisory only |
| Database impact | PASS | Reuse/new/not-needed/unknown matrix; no SQL/DB changes |
| Scope control | PASS | One append-only target, no other tracked/index mutation |
| Original exact prefix | PASS | Complete original raw checkout bytes equals candidate prefix and checkout-filtered HEAD representation |
| Acceptance mapping/sections/tables/links/anchors | PASS | Standard-library static validator and report inspection; exactly 30 original criteria matched |
| Markdown fences/Mermaid static source | PASS | Balanced fences, three required diagrams plus dependency map, defined flow references/sequence participants; source check only |
| Whitespace/additions-only diff/final identity | PASS | git diff --check/numstat; Git remove/readds the identical formerly unterminated final line when append terminates it; exact original bytes remain prefix; external final digest/blob/bytes/LF count |
| Application runtime | NOT RUN | Architecture only |
| Database runtime/integrity | NOT RUN | No operational DB/fixture database opened |
| GUI | NOT RUN | No Qt application launched |
| PowerShell runtime | NOT RUN | No diagnostic or F7Hub PowerShell runtime invoked |
| AHK runtime | NOT RUN | No host/hotkey/clipboard capture executed |
| Mochi runtime | NOT RUN | No renderer/context/provider |
| Mermaid rendering | NOT RUN | No renderer invoked/installed; visual appearance NOT VERIFIED |
| Independent architecture review | NOT RUN | Next gate |
| Staging/commit/push/PR/merge | NOT RUN | Explicitly excluded |

Production changes: NONE. Database changes: NONE. Runtime regression suite deliberately NOT RUN. GitHub read-only PR evidence is inspection, not publication. Author static assessment proves planning completeness only.

## Result

READY_FOR_CLIPBOARD_INTEGRATION_DESIGN

All 30 criteria PASS at architecture depth; no unresolved blocking Foundation conflict and no material 1A user-choice prerequisite identified. This is the author candidate result, not approval/closure or permission to execute 1B. Candidate remains UNAPPROVED, UNSTAGED, UNCOMMITTED, UNPUBLISHED, NOT INTEGRATED.

Review Record: NOT RUN; next gate INDEPENDENT PHASE 1A CLIPBOARD ARCHITECTURE REVIEW. Approval Record: NONE. Change History: 2026-10-07, original planning contract preserved exactly, append-only Execution Report authored and statically checked. Only after independent review, explicit USER approval and controlled integration may 1A close. STOP here: no 1B/1C/Settings/Clipboard/schema/AHK/IPC/GUI/Diagnostics/Analytics/Mochi implementation or further phase execution.
