# F7Hub Entity Relationship Design

> Document: `Docs/08_ERD.md`  
> Project: F7Hub  
> Purpose: Define the major F7Hub database entities, their ownership, and their relationships before exact SQL implementation.  
> Scope: Conceptual and logical ERD design.  
> Related Documents: `02_ProductRequirements.md`, `03_Features.md`, `04_UserWorkflows.md`, `06_SystemArchitecture.md`, `07_Database.md`, `09_SQLSchema.md`

---

# 1. Purpose

This document defines the Entity Relationship Design for F7Hub.

It answers:

> What persistent entities exist in F7Hub, and how are they related?

This document focuses on:

- entity purpose
- domain ownership
- primary relationships
- cardinality
- junction entities
- lifecycle relationships
- normalization
- external mappings
- relationship rules

It does not define:

- exact SQLite data types
- full `CREATE TABLE` statements
- exact index definitions
- complete migration scripts

Those belong in:

`09_SQLSchema.md`

---

# 2. ERD Design Philosophy

The F7Hub ERD should model real technician workflows.

The database should not be designed by asking:

> How many tables can F7Hub have?

Instead:

> What persistent concepts are required to support the product?

The design process is:

```text
Requirements
    ↓
Domains
    ↓
Entities
    ↓
Relationships
    ↓
Normalization
    ↓
Constraints
    ↓
SQL Schema
```

---

# 3. Current ERD Status

This document defines the intended logical data model. Repository inspection and tests through 2026-09-04 verified the bootstrap-owned `schema_migrations` infrastructure, the versioned core and taxonomy tables, the company/contact tables through `0003_companies_contacts.sql`, the ticket-core tables through `0004_tickets.sql`, the relational knowledge tables through `0005_knowledge.sql`, the Python company/contact repositories, and the transactional ticket creation repository/service boundary. Remaining business domains and workflows are planned.

```text
schema_migrations infrastructure: VERIFIED
application_metadata implementation status: VERIFIED
Taxonomy implementation status: VERIFIED
Company/contact schema and repository status: VERIFIED
Ticket-core schema status: VERIFIED
Ticket creation repository/service status: VERIFIED
Knowledge relational schema status: VERIFIED
Remaining business-domain ERD implementation status: PLANNED
```

The planned baseline entities and relationships are aligned with the physical target in `09_SQLSchema.md`. Deferred concepts are labeled explicitly and are not part of the baseline physical schema.

---

# 4. ERD Scope

Initial F7Hub database domains:

```text
Core
Companies
Contacts
Tickets
Knowledge
Taxonomy
Automation
Diagnostics
Prompts
Clipboard
Workspaces
Integrations
Audit
```

Not every possible future domain belongs in the initial database.

---

# 5. Core Domain

The Core domain supports database lifecycle and application-level metadata.

Potential entities:

```text
schema_migrations
application_metadata
```

---

## 5.1 schema_migrations

Purpose:

Track applied database migrations.

Potential relationships:

```text
schema_migrations
→ no required business-domain parent
```

Typical information:

- migration identifier
- version
- applied timestamp
- status
- checksum if used

The authoritative migration record is `schema_migrations`, as defined in `09_SQLSchema.md`. `PRAGMA user_version` is not a competing migration-state authority.

Implementation status:

```text
VERIFIED — created and exercised by the SQLite bootstrap infrastructure
```

---

## 5.2 application_metadata

Purpose:

Store small application-level metadata values that belong to database lifecycle or application identity rather than a business domain.

It has no required business-domain parent.

---

# 6. Company Domain

Companies provide organizational context for tickets, contacts, knowledge and external systems.

Primary entities:

```text
companies
company_notes
company_links
```

---

## 6.1 companies

Purpose:

Represent an organization supported through F7Hub.

Example:

```text
Contoso
Fabrikam
Northwind
```

Key relationships:

```text
companies
  1 ─────< contacts
  1 ─────< tickets
  1 ─────< company_notes
  1 ─────< company_links
```

A company may exist without any tickets.

---

## 6.2 company_notes

Purpose:

Store reusable company-specific technical or operational notes.

Examples:

- tenant notes
- environment details
- escalation instructions
- network context

Relationship:

```text
companies
1 ─────< company_notes
```

A company note belongs to one company.

---

## 6.3 company_links

Purpose:

Store useful company-specific links.

Examples:

- admin portals
- vendor portals
- internal documentation
- remote-management pages

Relationship:

```text
companies
1 ─────< company_links
```

---

# 7. Contact Domain

Primary entity:

```text
contacts
```

---

## 7.1 contacts

Purpose:

Represent a user or person relevant to support activity.

Typical relationships:

```text
companies
1 ─────< contacts
```

A contact normally belongs to one company in the initial model.

A company may have many contacts.

---

## 7.2 Contact-to-Ticket Relationship

The initial model may allow a ticket to reference a primary contact.

```text
contacts
1 ─────< tickets
```

Conceptually:

```text
Company
   │
   ├──── Contacts
   │
   └──── Tickets
```

If future requirements require multiple contacts on one ticket, a junction table may later be introduced.

Do not introduce it before the workflow requires it.

---

# 8. Ticket Domain

The Ticket domain is one of the central relational areas of F7Hub.

Primary entities:

```text
tickets
ticket_notes
ticket_status_history
ticket_timeline_events
ticket_attachments
ticket_relationships
```

Tagging is handled through shared taxonomy entities later in this document.

---

# 9. tickets

Purpose:

Represent a support issue or case.

Core relationships:

```text
companies
1 ─────< tickets

contacts
1 ─────< tickets

tickets
1 ─────< ticket_notes

tickets
1 ─────< ticket_status_history

tickets
1 ─────< ticket_timeline_events

tickets
1 ─────< ticket_attachments
```

A ticket should remain the central context for troubleshooting activity.

---

# 10. ticket_notes

Purpose:

Store technician notes associated with a ticket.

Examples:

- troubleshooting note
- internal note
- customer communication
- escalation note
- resolution note

Relationship:

```text
tickets
1 ─────< ticket_notes
```

A note must belong to one ticket.

---

# 11. ticket_status_history

Purpose:

Preserve meaningful ticket status transitions.

Example:

```text
NEW
  ↓
OPEN
  ↓
IN_PROGRESS
  ↓
WAITING
  ↓
RESOLVED
  ↓
CLOSED

Alternative terminal path:

NEW / OPEN / IN_PROGRESS / WAITING
  ↓
CANCELLED
```

The implemented initial service policy allows movement among active work states without requiring every example step. Resolving requires a summary; closing follows resolution. Per the user's 2026-09-04 decision, both RESOLVED and CLOSED may reopen to OPEN. CANCELLED remains terminal for now. Reopening clears current resolution/lifecycle fields and preserves previous resolution content in notes. The full service transition table is maintained in `13_PythonArchitecture.md`.

Relationship:

```text
tickets
1 ─────< ticket_status_history
```

The history table should not necessarily replace the current status stored on the ticket.

The current ticket status may remain directly accessible for efficient querying.

---

# 12. ticket_timeline_events

Purpose:

Provide a unified chronological history of major ticket-related events.

Potential event references:

- note added
- diagnostic started
- diagnostic completed
- script executed
- KB linked
- attachment added
- ticket resolved

Relationship:

```text
tickets
1 ─────< ticket_timeline_events
```

Timeline entries should not duplicate entire source records unnecessarily.

Where possible they should reference the originating entity.

---

# 13. ticket_attachments

Purpose:

Store metadata about files associated with a ticket.

Relationship:

```text
tickets
1 ─────< ticket_attachments
```

The file itself normally remains outside SQLite.

Possible metadata:

- file name
- relative path
- file type
- size
- hash
- created time

---

# 14. ticket_relationships

Purpose:

Relate one ticket to another.

Examples:

```text
RELATED_TO
DUPLICATE_OF
PARENT_OF
CHILD_OF
RECURRING_ISSUE
```

Conceptually:

```text
tickets
   │
   └──── ticket_relationships ──── tickets
```

This is a self-referencing many-to-many relationship.

Care must be taken to avoid duplicate inverse relationships.

---

# 15. Knowledge Domain

Primary entities:

```text
knowledge_articles
knowledge_article_versions
knowledge_article_links
knowledge_article_relationships
```

Tags and categories are shared through taxonomy entities.

---

# 16. knowledge_articles

Purpose:

Represent reusable technical knowledge.

Examples:

- troubleshooting guide
- SOP
- known error
- command reference
- PowerShell guide
- escalation procedure

Potential relationships:

```text
knowledge_articles
1 ─────< knowledge_article_versions

knowledge_articles
1 ─────< knowledge_article_links
```

Knowledge articles may also relate to:

- tickets
- scripts
- diagnostic workflows
- tags
- categories

---

# 17. knowledge_article_versions

Purpose:

Preserve meaningful article revisions if version history is required.

Relationship:

```text
knowledge_articles
1 ─────< knowledge_article_versions
```

Version history is valuable when:

- procedures change
- old instructions must remain traceable
- article review lifecycle matters

If this proves unnecessary in early versions, it may be deferred.

---

# 18. knowledge_article_links

Purpose:

Store references associated with an article.

Examples:

- Microsoft Learn
- vendor documentation
- internal documentation
- support resources

Relationship:

```text
knowledge_articles
1 ─────< knowledge_article_links
```

---

# 19. knowledge_article_relationships

Purpose:

Relate one knowledge article to another.

Examples:

```text
RELATED
PREREQUISITE
REPLACES
SEE_ALSO
```

Conceptual model:

```text
knowledge_articles
      │
      └── knowledge_article_relationships ── knowledge_articles
```

This is a self-referencing relationship.

---

# 20. Ticket-to-Knowledge Relationship

Tickets may use or produce knowledge articles.

Junction entity:

```text
ticket_knowledge_articles
```

Relationship:

```text
tickets
   >────< knowledge_articles
```

implemented conceptually as:

```text
tickets
1 ─────< ticket_knowledge_articles >───── 1
                                      knowledge_articles
```

Possible relationship types:

```text
RELATED
USED_FOR_RESOLUTION
CREATED_FROM_TICKET
RECOMMENDED
```

---

# 21. Taxonomy Domain

Shared taxonomy prevents every module from creating its own incompatible tag system.

Primary entities:

```text
tags
categories
```

Junction tables are introduced only where required.

---

# 22. tags

Purpose:

Provide flexible many-to-many classification.

Examples:

```text
outlook
exchange
dns
vpn
intune
mfa
windows
```

Possible relationships:

```text
tags
>────< tickets

tags
>────< knowledge_articles

tags
>────< scripts
```

through dedicated junction tables.

---

# 23. ticket_tags

Junction table:

```text
tickets
1 ─────< ticket_tags >───── 1
                              tags
```

Represents:

```text
tickets
>────< tags
```

---

# 24. knowledge_article_tags

Junction table:

```text
knowledge_articles
1 ─────< knowledge_article_tags >───── 1
                                          tags
```

---

# 25. script_tags

Junction table:

```text
scripts
1 ─────< script_tags >───── 1
                              tags
```

---

# 26. categories

Purpose:

Provide controlled classification.

Categories may support:

- tickets
- KB
- scripts
- diagnostics

However, the final category design must be careful.

A single universal category table may become too generic if domains require very different structures.

Recommended approach:

> Reuse categories where the semantics are genuinely shared. Separate them where the domain meaning differs.

This decision should be finalized during `09_SQLSchema.md`.

---

# 27. Automation Domain

Primary entities:

```text
scripts
script_parameters
script_executions
```

---

# 28. scripts

Purpose:

Represent an automation script registered in F7Hub.

The script source normally remains on disk.

Typical information:

- script name
- relative path
- language
- description
- version
- risk level
- privilege requirement
- enabled state

Relationships:

```text
scripts
1 ─────< script_parameters

scripts
1 ─────< script_executions
```

---

# 29. script_parameters

Purpose:

Define structured parameters expected by a registered script.

Examples:

```text
ComputerName
UserPrincipalName
Mailbox
Hostname
```

Relationship:

```text
scripts
1 ─────< script_parameters
```

Possible parameter metadata:

- parameter name
- type
- required
- default
- validation rule
- description

---

# 30. script_executions

Purpose:

Record meaningful script executions.

Relationship:

```text
scripts
1 ─────< script_executions
```

A script execution may also reference:

```text
ticket
diagnostic_session
```

when applicable.

Conceptually:

```text
ticket
   │
   └──── script_execution ──── script
```

---

# 31. Script Execution Parameters

There are two possible approaches:

1. store execution parameters as structured JSON
2. normalize them into a dedicated child table

Potential child entity:

```text
script_execution_parameters
```

Recommended rule:

- normalize if individual parameter querying/auditing is needed
- JSON may be acceptable if parameters are only preserved as execution context

This should be decided from real query requirements.

---

# 32. Diagnostic Domain

The Diagnostic domain coordinates reusable troubleshooting workflows.

Primary entities:

```text
diagnostic_workflows
diagnostic_steps
diagnostic_conditions
diagnostic_sessions
diagnostic_responses
diagnostic_results
```

---

# 33. diagnostic_workflows

Purpose:

Represent a reusable troubleshooting procedure.

Examples:

```text
Outlook Cannot Connect
VPN Connectivity
DNS Resolution
MFA Failure
Teams Camera
```

Relationships:

```text
diagnostic_workflows
1 ─────< diagnostic_steps

diagnostic_workflows
1 ─────< diagnostic_sessions
```

---

# 34. diagnostic_steps

Purpose:

Represent ordered steps within a workflow.

Possible step types:

```text
QUESTION
CONDITION
SCRIPT
INSTRUCTION
RESULT
```

Relationship:

```text
diagnostic_workflows
1 ─────< diagnostic_steps
```

A step belongs to one workflow.

---

# 35. diagnostic_conditions

Purpose:

Define branching rules between diagnostic steps.

Conceptually:

```text
Diagnostic Step
      │
      ▼
Condition
   ┌──┴──┐
   │     │
 TRUE   FALSE
   │     │
   ▼     ▼
Step B  Step C
```

Relationship:

```text
diagnostic_steps
1 ─────< diagnostic_conditions
```

Conditions may reference destination steps.

---

# 36. Diagnostic Step-to-Script Relationship

A diagnostic step may invoke a registered script.

Preferred relationship:

```text
diagnostic_steps
many ───── 0..1 scripts
```

or through an explicit junction if a step may invoke multiple scripts.

For the simpler initial design:

> one script step references one registered script.

This keeps the workflow easy to understand.

---

# 37. diagnostic_sessions

Purpose:

Represent one execution of a diagnostic workflow.

Relationships:

```text
diagnostic_workflows
1 ─────< diagnostic_sessions

tickets
1 ─────< diagnostic_sessions
```

A session may optionally exist without a ticket for standalone diagnostics, depending on final product requirements.

---

# 38. diagnostic_responses

Purpose:

Store technician/user answers collected during a diagnostic session.

Relationship:

```text
diagnostic_sessions
1 ─────< diagnostic_responses
```

Each response should reference the relevant diagnostic step.

---

# 39. diagnostic_results

Purpose:

Store structured diagnostic findings.

Relationship:

```text
diagnostic_sessions
1 ─────< diagnostic_results
```

Possible information:

- status
- finding
- value
- message
- warning
- error
- evidence

---

# 40. Diagnostic Relationship Summary

```text
diagnostic_workflows
        │
        ├────< diagnostic_steps
        │          │
        │          ├────< diagnostic_conditions
        │          │
        │          └──── scripts
        │
        └────< diagnostic_sessions
                   │
                   ├────< diagnostic_responses
                   ├────< diagnostic_results
                   └────< script_executions
```

---

# 41. Knowledge-to-Diagnostic Relationship

A diagnostic workflow may have related KB articles.

Potential junction:

```text
diagnostic_workflow_articles
```

Relationship:

```text
diagnostic_workflows
>────< knowledge_articles
```

This allows troubleshooting workflows to surface:

- prerequisite KB
- explanation
- remediation guide
- escalation documentation

---

# 42. Knowledge-to-Script Relationship

KB articles may reference scripts.

Potential junction:

```text
knowledge_article_scripts
```

Relationship:

```text
knowledge_articles
>────< scripts
```

This lets an article describe a procedure and reference an approved automation separately.

---

# 43. Prompt Domain

Primary entities:

```text
prompt_templates
prompt_variables
```

---

# 44. prompt_templates

Purpose:

Store reusable AI or text-generation prompt templates.

Typical information:

- name
- purpose
- template
- category
- enabled state
- version

---

# 45. prompt_variables

Purpose:

Define supported placeholders for a prompt.

Relationship:

```text
prompt_templates
1 ─────< prompt_variables
```

Examples:

```text
ticket_title
ticket_description
company_name
diagnostic_results
```

---

# 46. Clipboard Domain

Clipboard persistence must remain minimal because it may contain sensitive content.

Possible entities:

```text
clipboard_snippets
clipboard_history
```

---

# 47. clipboard_snippets

Purpose:

Store intentional reusable technician text.

Examples:

- ticket templates
- standard responses
- escalation wording
- troubleshooting text

This is safer and more durable than automatically storing all copied content.

---

# 48. clipboard_history

Purpose:

Optionally store clipboard history.

This entity should be considered:

```text
OPTIONAL / CONFIGURABLE
```

Requirements should support:

- persistence disabled
- expiration
- manual clear
- sensitive-content exclusion

---

# 49. Workspace Domain

Primary entity:

```text
workspaces
```

Potential secondary entity:

```text
workspace_panels
```

---

# 50. workspaces

Purpose:

Store saved GUI workspace profiles.

Examples:

```text
Helpdesk
Microsoft 365
Networking
Automation
Knowledge Authoring
```

---

# 51. workspace_panels

Purpose:

Store per-workspace panel configuration if normalized persistence is needed.

Relationship:

```text
workspaces
1 ─────< workspace_panels
```

Alternative:

Store Qt workspace state as a controlled opaque value.

The final choice should be driven by whether F7Hub needs to query individual panel settings.

---

# 52. Integration Domain

External provider identifiers should remain separate from F7Hub internal IDs.

Primary concept:

```text
external_entity_mappings
```

---

# 53. external_entity_mappings

Purpose:

Map F7Hub entities to external providers.

Example:

```text
F7Hub ticket_id = 42
provider = HaloPSA
external_id = 10254
```

Potential fields conceptually:

- mapping ID
- entity type
- F7Hub entity ID
- provider
- external ID
- sync timestamp

---

# 54. External Mapping Design Warning

A generic mapping table is convenient but can weaken relational integrity because one field may point to several table types.

Alternative:

Provider/domain-specific mappings such as:

```text
ticket_external_mappings
company_external_mappings
contact_external_mappings
```

may provide stronger foreign keys.

Recommended approach:

> Prefer explicit domain-specific mapping tables when relational integrity is more important than generic convenience.

This should be decided during SQL design.

---

# 55. Audit Domain

Primary entity:

```text
audit_events
```

---

# 56. audit_events

Purpose:

Record important actions where traceability is useful.

Examples:

- privileged PowerShell action
- Microsoft administration
- migration
- diagnostic completion
- significant record change

Potential relationships may include:

- ticket
- script execution
- integration
- target identifier

Audit records should not contain unnecessary secrets.

---

# 57. Audit vs Timeline

These should remain distinct.

Ticket timeline:

> What happened in this support case?

Audit:

> What significant system or administrative action occurred?

They may reference the same operation but serve different purposes.

---

# 58. Core Entity Relationship Overview

```text
companies
   │
   ├────< contacts
   │
   ├────< tickets
   │         │
   │         ├────< ticket_notes
   │         ├────< ticket_status_history
   │         ├────< ticket_timeline_events
   │         ├────< ticket_attachments
   │         ├────< diagnostic_sessions
   │         └────< script_executions
   │
   ├────< company_notes
   └────< company_links
```

---

# 59. Knowledge Relationship Overview

```text
knowledge_articles
      │
      ├────< knowledge_article_versions
      ├────< knowledge_article_links
      ├──── knowledge_articles_fts (derived current-content index)
      │
      ├────< knowledge_article_tags >──── tags
      │
      ├────< ticket_knowledge_articles >─ tickets
      │
      ├────< knowledge_article_scripts >─ scripts
      │
      └────< diagnostic_workflow_articles >─ diagnostic_workflows
```

---

# 60. Automation and Diagnostic Overview

```text
scripts
  │
  ├────< script_parameters
  │
  └────< script_executions
             ▲
             │
diagnostic_sessions
      ▲
      │
diagnostic_workflows
      │
      └────< diagnostic_steps
                  │
                  ├────< diagnostic_conditions
                  └──── script reference
```

---

# 61. High-Level ERD

```text
COMPANIES
   │
   ├────< CONTACTS
   │
   └────< TICKETS
            │
            ├────< TICKET_NOTES
            ├────< TICKET_STATUS_HISTORY
            ├────< TICKET_TIMELINE_EVENTS
            ├────< TICKET_ATTACHMENTS
            ├────< DIAGNOSTIC_SESSIONS
            └────< SCRIPT_EXECUTIONS

TICKETS
   │
   └────< TICKET_KNOWLEDGE_ARTICLES >──── KNOWLEDGE_ARTICLES

KNOWLEDGE_ARTICLES
   │
   ├────< KNOWLEDGE_ARTICLE_VERSIONS
   ├────< KNOWLEDGE_ARTICLE_LINKS
   ├────< KNOWLEDGE_ARTICLE_TAGS >──── TAGS
   └────< KNOWLEDGE_ARTICLE_SCRIPTS >──── SCRIPTS

SCRIPTS
   │
   ├────< SCRIPT_PARAMETERS
   ├────< SCRIPT_EXECUTIONS
   └────< SCRIPT_TAGS >──── TAGS

DIAGNOSTIC_WORKFLOWS
   │
   ├────< DIAGNOSTIC_STEPS
   │          │
   │          └────< DIAGNOSTIC_CONDITIONS
   │
   └────< DIAGNOSTIC_SESSIONS
              │
              ├────< DIAGNOSTIC_RESPONSES
              └────< DIAGNOSTIC_RESULTS
```

---

# 62. Cardinality Rules

Common cardinalities:

```text
Company
1 : many
Contacts

Company
1 : many
Tickets

Ticket
1 : many
Notes

Ticket
1 : many
Diagnostic Sessions

Script
1 : many
Executions

Diagnostic Workflow
1 : many
Steps

Diagnostic Session
1 : many
Responses

Diagnostic Session
1 : many
Results

Ticket
many : many
Knowledge Articles

Knowledge Article
many : many
Tags

Script
many : many
Tags
```

---

# 63. Relationship Ownership

Parent-child ownership matters for deletion behavior.

Example:

```text
Ticket
└── Ticket Note
```

A ticket note has no meaningful independent identity outside its ticket.

Possible deletion behavior may therefore differ from:

```text
Company
└── Ticket
```

where deleting a company should not automatically destroy historical tickets.

Foreign-key actions must be decided per relationship in `09_SQLSchema.md`.

---

# 64. Relationship Strength

Relationships may be:

## Required

Example:

```text
ticket_note
→ must reference ticket
```

## Optional

Example:

```text
ticket
→ may reference contact
```

depending on final workflow rules.

## Historical

Example:

A ticket may need to retain company information even if that company later becomes inactive.

This should normally use lifecycle state rather than destructive deletion.

---

# 65. Soft Delete and Archive

Not all entities should support hard deletion.

Likely archival candidates:

```text
companies
tickets
knowledge_articles
scripts
diagnostic_workflows
```

Possible lifecycle fields:

```text
is_active
status
archived_at
```

The exact pattern should be standardized rather than implemented differently in every table.

---

# 66. Lookup Entities

Possible lookup/reference entities may eventually include:

```text
ticket_statuses
ticket_priorities
knowledge_article_types
script_languages
diagnostic_step_types
```

However, a lookup table should only be created if it provides:

- domain meaning
- referential value
- configurability
- metadata

Do not create a table simply to replace every small fixed enumeration.

---

# 67. Reusable Taxonomy

One of the main normalization goals is to avoid structures such as:

```text
ticket_tags
kb_tags
script_tags
diagnostic_tags
```

where each has a separate tag-definition table.

Prefer a shared:

```text
tags
```

entity with domain-specific junction tables.

---

# 68. External Provider Independence

Core entities should remain independent from providers.

Preferred:

```text
tickets
   │
   └──── external mapping
             │
             └──── HaloPSA
```

Avoid:

```text
halo_ticket_id
halo_company_id
halo_contact_id
```

being spread throughout unrelated core tables.

This keeps F7Hub useful without HaloPSA.

---

# 69. File Relationships

Files such as:

- attachments
- PowerShell scripts
- exports
- documentation

normally remain in the filesystem.

Database entities should reference metadata and relative paths.

Conceptually:

```text
Database Record
      │
      ▼
Relative File Path
      │
      ▼
Filesystem
```

---

# 70. Search Relationships

FTS5 tables should not be treated as normal business entities in the conceptual ERD.

They are derived search infrastructure.

Example:

```text
knowledge_articles
        │
        ▼
knowledge_articles_fts
```

Slice 015 verifies this exact mapping. `knowledge_articles_fts.rowid` maps to `knowledge_articles.knowledge_article_id` and derives article code, title, summary and current body. Insert/update/delete triggers keep the index synchronized, and migration 0006 rebuilds pre-existing current rows. All current lifecycle statuses participate; `knowledge_article_versions` has no FTS relationship. The relational entity remains the source of truth.

---

# 71. Derived Data

Avoid storing data that can be reliably derived unless justified.

Example:

If ticket note count can be calculated:

```sql
COUNT(ticket_notes)
```

do not automatically store:

```text
tickets.note_count
```

unless measured performance justifies it.

---

# 72. Historical Snapshots

Some data may intentionally duplicate information for historical accuracy.

Example:

If a contact changes email address, a historical ticket communication might need the email used at the time.

This is legitimate denormalization only when the historical requirement is explicit.

---

# 73. JSON Usage

JSON may be useful for:

- variable structured diagnostic output
- provider-specific metadata
- script execution context
- GUI state

JSON should not replace ordinary relational modeling.

Avoid:

```text
ticket.data = everything about the ticket
```

when the data has stable relational meaning.

---

# 74. Entity Approval Rule

Before an entity is added to the ERD:

```text
Requirement Exists?
      │
      ▼
Persistent Concept?
      │
      ▼
Existing Entity Already Covers It?
      │
      ▼
Relationships Known?
      │
      ▼
Lifecycle Known?
      │
      ▼
Approve Entity
```

---

# 75. Entity Inventory

Canonical conceptual inventory:

| Domain | Entity | Purpose | Implementation Status |
|---|---|---|---|
| Core | schema_migrations | Track schema evolution | VERIFIED |
| Core | application_metadata | Store application-level metadata | VERIFIED |
| Taxonomy | categories | Shared hierarchical classification | VERIFIED |
| Taxonomy | tags | Shared flexible tags | VERIFIED |
| Companies | companies | Supported organizations | VERIFIED |
| Companies | company_notes | Company technical notes | VERIFIED |
| Companies | company_links | Company resources | VERIFIED |
| Contacts | contacts | Supported contacts | VERIFIED |
| Tickets | tickets | Support cases | VERIFIED |
| Tickets | ticket_notes | Ticket documentation | VERIFIED |
| Tickets | ticket_status_history | Status transitions | VERIFIED |
| Tickets | ticket_timeline_events | Unified case history | VERIFIED |
| Tickets | ticket_attachments | Attachment metadata | PLANNED |
| Tickets | ticket_relationships | Ticket-to-ticket links | PLANNED |
| Tickets | ticket_tags | Ticket/tag junction | PLANNED |
| Knowledge | knowledge_articles | Reusable knowledge | VERIFIED |
| Knowledge | knowledge_article_versions | Article history | VERIFIED |
| Knowledge | knowledge_article_links | Article references | VERIFIED |
| Knowledge | knowledge_article_relationships | Article-to-article links | VERIFIED |
| Knowledge | ticket_knowledge_articles | Ticket/KB junction | VERIFIED |
| Knowledge | knowledge_article_tags | KB/tag junction | VERIFIED |
| Search | knowledge_articles_fts | Derived current Knowledge content index | VERIFIED |
| Knowledge | knowledge_article_scripts | KB/script junction | PLANNED |
| Automation | scripts | Script registry | PLANNED |
| Automation | script_parameters | Script input definitions | PLANNED |
| Automation | script_executions | Execution history | PLANNED |
| Automation | script_tags | Script/tag junction | PLANNED |
| Diagnostics | diagnostic_workflows | Troubleshooting definitions | PLANNED |
| Diagnostics | diagnostic_steps | Workflow steps | PLANNED |
| Diagnostics | diagnostic_conditions | Branch rules | PLANNED |
| Diagnostics | diagnostic_sessions | Workflow executions | PLANNED |
| Diagnostics | diagnostic_responses | Technician answers | PLANNED |
| Diagnostics | diagnostic_results | Findings/results | PLANNED |
| Diagnostics | diagnostic_workflow_articles | Workflow/KB junction | PLANNED |
| Prompts | prompt_templates | Reusable prompts | PLANNED |
| Prompts | prompt_variables | Prompt variables | PLANNED |
| Clipboard | clipboard_snippets | Intentional reusable text | PLANNED |
| Clipboard | clipboard_history | Optional clipboard history | PLANNED |
| Workspaces | workspaces | Saved layouts | PLANNED |
| Audit | audit_events | Significant actions | PLANNED |
| Workspaces | workspace_panels | Optional normalized panel state | DEFERRED |
| Integrations | external_entity_mappings | Generic external mapping concept | DEFERRED |

The baseline entities match the relational table inventory in `09_SQLSchema.md`. Implementation statuses distinguish verified migrations from planned tables, and deferred concepts require a later approved schema decision.

---

# 76. Initial Implementation Subset

The entire ERD should not be implemented at once.

The first coding slice is SQLite bootstrap and migration infrastructure only. No business-domain table in this ERD is part of that first task.

```text
First coding slice status: VERIFIED — 2026-09-03
```

---

# 77. Second Database Slice

After migration infrastructure is stable:

```text
categories
tags
companies
company_notes
company_links
contacts
```

Supporting company tables should be included only when the first real workflow requires them.

---

# 78. Third Database Slice

Then implement ticket persistence:

```text
tickets
ticket_notes
ticket_status_history
ticket_timeline_events
```

Attachments, relationships and tagging may follow when required by the ticket workflow.

```text
Status: VERIFIED — 0004_tickets.sql — 2026-09-03 — 10 focused tests; 79 full database tests
```

---

# 79. Subsequent Database Slices

The relational knowledge slice is verified:

```text
Status: VERIFIED — 0005_knowledge.sql — 2026-09-04 — 11 focused tests; 90 full database tests
```

The first derived search slice is also verified:

```text
Status: VERIFIED — 0006_knowledge_search.sql — 2026-09-09 — current Knowledge article FTS5 only
```

Later slices should introduce, in dependency order:

```text
Script registry and execution history
↓
Diagnostics
↓
Prompts / Clipboard
↓
Workspaces / Audit
```

Each slice requires its own migration, repository behavior and tests. Diagnostics remains the most structurally complex early domain and should follow the simpler relational foundations.

---

# 80. Why Diagnostics Come Later

The Diagnostic Engine contains:

- ordered steps
- branching
- session state
- responses
- script relationships
- result data

Trying to design it before validating simpler domains would increase risk unnecessarily.

It is a good learning milestone after:

- tickets
- KB
- scripts

are stable.

---

# 81. ERD Testing Implications

Each relationship should eventually receive tests.

Examples:

```text
Cannot create ticket_note without valid ticket

Cannot create script_parameter without valid script

Deleting a tag does not delete a KB article

Deleting company must not accidentally destroy historical tickets

Diagnostic response must reference valid session and step
```

---

# 82. ERD Review Checklist

Before converting an ERD domain into SQL:

```text
[ ] Entity has a clear purpose
[ ] Entity belongs to a defined domain
[ ] Primary key strategy known
[ ] Relationships identified
[ ] Cardinalities defined
[ ] Optionality defined
[ ] Many-to-many relationships normalized
[ ] Lifecycle considered
[ ] Delete behavior considered
[ ] External IDs separated
[ ] Duplicate data minimized
[ ] Expected queries understood
[ ] Security/privacy considered
```

---

# 83. ERD Anti-Patterns

Avoid:

## Giant Ticket Table

One table contains ticket, company, contact, diagnostic and resolution data.

## Comma-Separated Relationships

```text
tags = "dns,vpn,m365"
```

## Repeating Columns

```text
contact1
contact2
contact3
```

## Provider-Coupled Core Schema

Core entities are designed entirely around HaloPSA or another external provider.

## JSON Everywhere

Stable relational data is hidden inside arbitrary JSON.

## Premature Entity Explosion

Every possible future concept gets its own table before workflows exist.

## Duplicate Taxonomies

Every module invents separate tags and categories without reason.

---

# 84. Entity Relationship Summary

The central relational backbone of F7Hub is:

```text
                   COMPANIES
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
       CONTACTS                 TICKETS
                                  │
              ┌───────────────────┼────────────────────┐
              ▼                   ▼                    ▼
        TICKET NOTES       DIAGNOSTIC SESSIONS   SCRIPT EXECUTIONS
                                  │                    │
                                  ▼                    ▼
                         DIAGNOSTIC RESULTS          SCRIPTS
                                                       │
                                                       ▼
                                                SCRIPT PARAMETERS

TICKETS
   │
   ▼
TICKET_KNOWLEDGE_ARTICLES
   │
   ▼
KNOWLEDGE ARTICLES
   │
   ├──── TAGS
   ├──── SCRIPTS
   └──── DIAGNOSTIC WORKFLOWS
```

---

# 85. Learning Value of the ERD

The F7Hub database should provide practical experience with:

- entities
- attributes
- primary keys
- foreign keys
- 1-to-many relationships
- many-to-many relationships
- junction tables
- self-referencing relationships
- normalization
- constraints
- transactions
- indexes
- migrations
- FTS5
- audit data
- repository patterns

The goal is not merely to produce a schema.

The goal is to understand why the schema is designed that way.

---

# 86. Relationship to Other Documents

## `07_Database.md`

Defines:

> What rules govern F7Hub data?

## `08_ERD.md`

Defines:

> What entities exist and how are they related?

## `09_SQLSchema.md`

Defines:

> How are those entities implemented in SQLite?

---

# 87. ERD Golden Rules

1. Model real product concepts.
2. Do not design toward a table-count target.
3. Prefer 3NF.
4. Use explicit foreign keys.
5. Use junction tables for many-to-many relationships.
6. Separate external IDs from internal IDs.
7. Avoid unnecessary duplicate taxonomies.
8. Keep files outside SQLite unless there is a reason not to.
9. Keep scripts as files and metadata in SQLite.
10. Do not use JSON to avoid relational modeling.
11. Preserve historical support data.
12. Avoid dangerous cascade deletion.
13. Build the database domain by domain.
14. Validate each slice before adding more complexity.
15. Keep the ERD understandable.

---

# 88. Final ERD Principle

The F7Hub ERD should tell a story that can be understood without reading SQL:

```text
A Company
has Contacts
and Tickets.

A Ticket
has Notes,
History,
Diagnostics,
Scripts,
and Knowledge.

Knowledge
can be reused across Tickets.

Scripts
can support Diagnostics.

Diagnostics
produce structured Results.

All of these relationships
help preserve support knowledge
and technician context.
```

That is the purpose of the F7Hub data model.

> If an entity does not make the technician workflow clearer or more useful, question whether it belongs in the database.
