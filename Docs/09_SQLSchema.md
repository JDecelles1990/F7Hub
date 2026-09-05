# F7Hub SQL Schema

> Document: `Docs/09_SQLSchema.md`  
> Project: F7Hub  
> Database: SQLite  
> Purpose: Define the canonical physical SQLite schema for F7Hub, including tables, columns, data types, keys, constraints, indexes, views, FTS5 virtual tables, triggers, migration requirements, query patterns, and persistence invariants.  
> Related Documents: `02_ProductRequirements.md`, `04_UserWorkflows.md`, `06_SystemArchitecture.md`, `07_Database.md`, `08_ERD.md`, `10_FolderStructure.md`, `13_PythonArchitecture.md`, `14_DesignPrinciples.md`, `15_NamingConventions.md`, `16_Roadmap.md`, `19_DocumentationIndex.md`

---

# 1. Purpose

This document defines the physical SQLite implementation of the F7Hub data model.

It answers:

> Exactly how should F7Hub data be represented in SQLite?

This document owns:

```text
Tables
Columns
SQLite data types
Primary keys
Foreign keys
Unique constraints
Check constraints
Default values
Indexes
Views
FTS5 virtual tables
Database triggers
Migration boundaries
Canonical query patterns
Persistence invariants
```

The database design chain is:

```text
Requirements
    ↓
Workflows
    ↓
Database Architecture
    ↓
ERD
    ↓
SQL Schema
    ↓
Migrations
    ↓
Repositories
    ↓
Tests
```

Specifically:

```text
02_ProductRequirements.md
        ↓
04_UserWorkflows.md
        ↓
07_Database.md
        ↓
08_ERD.md
        ↓
09_SQLSchema.md
        ↓
Database\Migrations\
        ↓
SQLite
        ↓
Python Repositories
```

---

# 2. Authority

The database documents have distinct authority.

## `07_Database.md`

Defines:

```text
database rules
normalization strategy
integrity principles
migration policy
transaction policy
indexing principles
FTS5 strategy
backup strategy
repository ownership
```

## `08_ERD.md`

Defines:

```text
entities
relationships
cardinality
domain ownership
conceptual structure
```

## `09_SQLSchema.md`

Defines:

```text
exact tables
exact columns
exact SQLite data types
exact foreign keys
exact constraints
exact indexes
exact views
exact FTS5 structures
exact approved triggers
```

If the physical schema changes structurally, review all three:

```text
07_Database.md
08_ERD.md
09_SQLSchema.md
```

---

# 3. Current Status

This document defines the intended physical schema.

Current implementation status:

```text
SCHEMA DESIGN: REVIEW
SCHEMA DDL VALIDATION: PASS
MIGRATION INFRASTRUCTURE: VERIFIED
CORE APPLICATION MIGRATION: VERIFIED — 0001_core.sql
TAXONOMY MIGRATION: VERIFIED — 0002_taxonomy.sql
COMPANY/CONTACT MIGRATION: VERIFIED — 0003_companies_contacts.sql
TICKET-CORE MIGRATION: VERIFIED — 0004_tickets.sql
KNOWLEDGE MIGRATION: VERIFIED — 0005_knowledge.sql
REMAINING BUSINESS-DOMAIN MIGRATIONS: PLANNED
COMPANY/CONTACT REPOSITORIES: VERIFIED
TICKET REPOSITORY/SERVICE CREATION BOUNDARY: VERIFIED
TICKET NOTES/STATUS/RESOLUTION/REOPENING SERVICE BOUNDARY: VERIFIED
REMAINING REPOSITORIES: PLANNED
ISOLATED DATABASE TESTS: PASS — 129 tests
```

Repository inspection and tests through 2026-09-04 verified the Python SQLite connection, path-resolution, migration, checksum, rollback, bootstrap and integrity infrastructure. Versioned migration `0001_core.sql` creates only `application_metadata`, `0002_taxonomy.sql` creates shared taxonomy, `0003_companies_contacts.sql` creates the canonical company/contact tables and indexes, `0004_tickets.sql` creates the canonical ticket-core tables and indexes, and `0005_knowledge.sql` creates the canonical relational knowledge tables and indexes. `CompanyRepository`, `ContactRepository` and `TicketRepository` implement approved Python persistence boundaries. `TicketService` validates and transactionally coordinates ticket creation, initial status history and the initial timeline event. The tested ticket-creation GUI and minimal application shell use this boundary; no knowledge repository was added. The existing `Database\SQLite\F7Hub.db` file remains a zero-byte legacy scaffold and was not used by the tests.

The documented `CREATE` blocks were executed in order against a fresh in-memory SQLite database on 2026-09-02. All 71 DDL blocks executed successfully; `PRAGMA integrity_check` returned `ok` and `PRAGMA foreign_key_check` returned zero violations. This validates the documented DDL only, not application migrations or runtime behavior.

A table appearing in this document does not mean the corresponding migration has already been implemented.

The `schema_migrations` table is the exception: the verified bootstrap infrastructure creates it directly as migration-engine infrastructure before applying versioned migration files. It is not recreated by `0001_core.sql`.

---

# 4. Schema Philosophy

F7Hub does not target an arbitrary number of tables.

There is no requirement for:

```text
100 tables
120 tables
or any other predetermined table count
```

Tables exist because a validated domain relationship or workflow requires persistent relational data.

The design principle is:

```text
Requirement
    ↓
Persistent data need
    ↓
Entity
    ↓
Relationship
    ↓
Normalization
    ↓
Constraint
    ↓
Query pattern
    ↓
Index
```

---

# 5. Physical Database Principles

The F7Hub schema should preserve:

- relational integrity
- approximately third normal form where appropriate
- explicit primary keys
- explicit foreign keys
- intentional `ON DELETE` behavior
- check constraints
- unique constraints
- parameterized access
- transaction safety
- migration history
- predictable timestamps
- explicit many-to-many junction tables
- query-driven indexing
- controlled FTS5 usage
- filesystem/database separation
- one primary application persistence path

---

# 6. SQLite Ownership

Normal runtime database writes flow through:

```text
PySide6 GUI
    ↓
Application Service
    ↓
Repository
    ↓
SQLite
```

PowerShell should normally return structured results to Python.

AutoHotkey v2 should normally send application-level actions to Python.

Avoid:

```text
PowerShell
→ direct ticket table writes
```

and:

```text
AutoHotkey
→ direct ticket table writes
```

unless a future explicitly approved architecture requires it.

---

# 7. SQLite Data Type Strategy

SQLite uses dynamic typing, but F7Hub will use a controlled type convention.

Primary physical types:

| Logical Value | SQLite Type |
|---|---|
| Internal ID | `INTEGER` |
| Boolean | `INTEGER` |
| Integer number | `INTEGER` |
| Decimal | `REAL` |
| Text | `TEXT` |
| UTC timestamp | `TEXT` |
| JSON payload | `TEXT` |
| Binary Qt state | `BLOB` |
| File content | normally filesystem, not SQLite |

---

# 8. Primary Key Standard

Preferred entity primary key:

```sql
<entity>_id INTEGER PRIMARY KEY
```

Example:

```sql
ticket_id INTEGER PRIMARY KEY
```

Do not use `AUTOINCREMENT` by default.

SQLite's:

```sql
INTEGER PRIMARY KEY
```

already maps to the row identifier mechanism.

`AUTOINCREMENT` should only be introduced if its additional non-reuse guarantee becomes a concrete requirement.

---

# 9. Internal IDs vs External IDs

Internal F7Hub identifiers and external provider identifiers are different concepts.

Example:

```text
ticket_id
→ F7Hub internal identity

external_ticket_id
→ identifier belonging to HaloPSA or another provider
```

External identifiers should not normally become F7Hub primary keys.

---

# 10. Boolean Standard

SQLite has no dedicated Boolean storage class.

F7Hub represents Boolean values as:

```sql
INTEGER NOT NULL CHECK (value IN (0, 1))
```

Example:

```sql
is_active INTEGER NOT NULL DEFAULT 1
    CHECK (is_active IN (0, 1))
```

Meaning:

```text
0 = false
1 = true
```

---

# 11. Timestamp Standard

F7Hub timestamps are stored as:

```text
TEXT
```

using normalized UTC ISO-8601 values generated by the application layer.

Preferred form:

```text
2026-09-02T18:45:32.481Z
```

Timestamp columns use names such as:

```text
created_at
updated_at
started_at
completed_at
resolved_at
closed_at
captured_at
published_at
```

F7Hub should not mix:

```text
Created
CreatedDate
DateCreated
CreatedOn
```

---

# 12. Timestamp Ownership

Python should normally create normalized application timestamps.

This avoids multiple timestamp formats generated by different:

- SQLite functions
- PowerShell scripts
- AHK scripts
- external integrations

SQLite constraints should preserve structure where practical, but time formatting remains an application-layer responsibility.

---

# 13. JSON Storage

JSON may be stored in `TEXT` columns when the information is:

- variable
- structured
- provider-specific
- workflow-specific
- configuration-like
- not naturally relational

Examples:

```text
metadata_json
config_json
context_json
response_json
result_json
validation_json
```

JSON should not replace normal relational modeling.

Do not store an entire ticket or company record as one JSON object.

---

# 14. JSON Validation

The application must validate JSON before persistence.

Database-level `json_valid()` constraints may be considered once the minimum runtime SQLite feature set is finalized.

They are not required by the baseline schema in this document.

This prevents prematurely tying schema creation to an unverified runtime build configuration.

---

# 15. Enumerated Values

Stable domain states may be represented using `TEXT` plus `CHECK`.

Example:

```sql
status TEXT NOT NULL CHECK (
    status IN ('NEW', 'OPEN', 'CLOSED')
)
```

This provides:

- readable database data
- integrity
- predictable domain mapping

Lookup tables should not be created for every tiny enumeration without a reason.

---

# 16. Configurable Values vs Enumerations

Use a lookup/entity table when values require:

- metadata
- hierarchy
- user configuration
- activation/deactivation
- relationships
- descriptions
- independent lifecycle

Use `CHECK` enumeration when values represent a small stable application state machine.

This is why:

```text
ticket status
→ CHECK enumeration
```

while:

```text
categories
→ relational table
```

---

# 17. Deletion Strategy

Deletion actions must preserve history appropriately.

General strategy:

```text
Dependent detail records
→ CASCADE where the parent truly owns them

Historical references
→ RESTRICT or preserve parent

Optional context
→ SET NULL
```

Examples:

```text
Company deleted
→ ticket remains
→ company_id becomes NULL

Ticket deleted
→ ticket notes cascade

Script with execution history
→ deletion restricted

Workflow with diagnostic sessions
→ deletion restricted
```

Hard deletion should be used cautiously.

Archive/disable state is preferred for many historical entities.

---

# 18. Foreign Key Enforcement

Every SQLite connection must execute:

```sql
PRAGMA foreign_keys = ON;
```

This is mandatory.

Application startup should verify it.

Example verification:

```sql
PRAGMA foreign_keys;
```

Expected:

```text
1
```

---

# 19. Connection PRAGMAs

Recommended connection initialization:

```sql
PRAGMA foreign_keys = ON;
PRAGMA busy_timeout = 5000;
```

`busy_timeout` may later become configurable.

The following are not yet mandatory baseline assumptions:

```sql
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
```

WAL should be introduced only after concurrency and backup behavior are validated.

---

# 20. Integrity Checks

Maintenance and test workflows should support:

```sql
PRAGMA integrity_check;
```

Expected:

```text
ok
```

Foreign-key validation:

```sql
PRAGMA foreign_key_check;
```

Expected:

```text
zero rows
```

---

# 21. Migration Authority

F7Hub will use a dedicated migration table as the authoritative schema migration record.

Authoritative table:

```text
schema_migrations
```

Migration filenames should follow:

```text
NNNN_description.sql
```

Example:

```text
0001_core.sql
0002_taxonomy.sql
0003_companies_contacts.sql
0004_tickets.sql
0005_knowledge.sql
```

---

# 22. `PRAGMA user_version`

`PRAGMA user_version` is not the authoritative migration record.

This avoids maintaining two competing sources of migration state.

The migration runner should determine applied migrations from:

```text
schema_migrations
```

Implementation status as of 2026-09-03:

```text
VERIFIED
```

---

# 23. Migration Immutability

Once a migration has been applied to a released database, do not silently edit it.

Each migration should record a checksum.

If a previously applied migration file changes, migration validation should fail visibly.

Preferred flow:

```text
Discover migrations
        ↓
Read schema_migrations
        ↓
Validate checksums
        ↓
Find unapplied migrations
        ↓
Execute sequentially
        ↓
Record result
```

---

# 24. Migration Transactions

Each migration should run transactionally where SQLite permits.

Conceptually:

```text
BEGIN
↓
Apply migration
↓
Validate
↓
Record migration
↓
COMMIT
```

Failure:

```text
ERROR
↓
ROLLBACK
↓
Report failure
```

Never mark a failed migration as applied.

---

# 25. Canonical Schema Domains

The target schema is grouped into these domains:

```text
Core
Taxonomy
Companies
Contacts
Tickets
Knowledge
Automation
Diagnostics
Prompts
Clipboard
Workspaces
Audit
Search Infrastructure
```

---

# 26. Target Relational Table Inventory

## Core

```text
schema_migrations
application_metadata
```

## Taxonomy

```text
categories
tags
```

## Companies / Contacts

```text
companies
company_notes
company_links
contacts
```

## Tickets

```text
tickets
ticket_notes
ticket_status_history
ticket_timeline_events
ticket_attachments
ticket_relationships
ticket_tags
```

## Knowledge

```text
knowledge_articles
knowledge_article_versions
knowledge_article_links
knowledge_article_relationships
ticket_knowledge_articles
knowledge_article_tags
knowledge_article_scripts
```

## Automation

```text
scripts
script_parameters
script_executions
script_tags
```

## Diagnostics

```text
diagnostic_workflows
diagnostic_steps
diagnostic_conditions
diagnostic_sessions
diagnostic_responses
diagnostic_results
diagnostic_workflow_articles
```

## Prompts

```text
prompt_templates
prompt_variables
```

## Clipboard

```text
clipboard_snippets
clipboard_history
```

## Workspaces

```text
workspaces
```

## Audit

```text
audit_events
```

---

# 27. Deferred Tables

The following are intentionally not part of the baseline physical schema yet.

## `workspace_panels`

Deferred because Qt can persist opaque layout state efficiently.

Add a relational panel-state table only if F7Hub later needs to query or independently manage individual panel configuration.

## Generic external mappings

Deferred until the first real PSA/RMM/provider integration.

A premature generic polymorphic mapping table would weaken foreign-key integrity.

When HaloPSA, NinjaOne, or another provider becomes real implementation work, design the mapping against actual provider requirements.

## User/account tables

Deferred because F7Hub is currently a local desktop application and no approved multi-user authentication domain exists.

---

# 28. Search Infrastructure

FTS5 target virtual tables:

```text
knowledge_articles_fts
tickets_fts
scripts_fts
prompt_templates_fts
```

These are derived indexes.

They are not source-of-truth tables.

---

# 29. Core Schema

## `schema_migrations`

Purpose:

Record immutable database migration history.

| Column | Type | Required | Key | Description |
|---|---|---:|---|---|
| `version` | INTEGER | Yes | PK | Numeric migration sequence |
| `name` | TEXT | Yes | | Migration description |
| `checksum_sha256` | TEXT | Yes | | Migration file checksum |
| `applied_at` | TEXT | Yes | | UTC application time |
| `execution_ms` | INTEGER | Yes | | Migration execution duration |

DDL:

```sql
CREATE TABLE schema_migrations (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    checksum_sha256 TEXT NOT NULL,
    applied_at TEXT NOT NULL,
    execution_ms INTEGER NOT NULL CHECK (execution_ms >= 0)
);
```

Ownership:

```text
Migration bootstrap infrastructure
→ creates schema_migrations
→ validates versioned migration history
→ applies 0001_core.sql and later migrations
```

---

# 30. `application_metadata`

Purpose:

Store low-volume database/application metadata that does not represent user preferences.

Examples:

```text
database_uuid
database_created_at
schema_family
```

It must not become a generic dumping ground for arbitrary configuration.

| Column | Type | Required | Key |
|---|---|---:|---|
| `metadata_key` | TEXT | Yes | PK |
| `metadata_value` | TEXT | Yes | |
| `updated_at` | TEXT | Yes | |

DDL:

```sql
CREATE TABLE application_metadata (
    metadata_key TEXT NOT NULL PRIMARY KEY,
    metadata_value TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

Implementation status:

```text
VERIFIED — created by Database\Migrations\0001_core.sql
```

---

# 31. Taxonomy Domain

F7Hub uses shared taxonomy where meaningful instead of creating unrelated category tables for every module.

---

# 32. `categories`

Purpose:

Hierarchical classification shared by appropriate modules.

Supported scopes:

```text
GENERAL
TICKET
KNOWLEDGE
SCRIPT
PROMPT
CLIPBOARD
DIAGNOSTIC
```

| Column | Type | Required | Description |
|---|---|---:|---|
| `category_id` | INTEGER | Yes | Internal ID |
| `scope` | TEXT | Yes | Entity domain |
| `name` | TEXT | Yes | Display name |
| `slug` | TEXT | Yes | Stable machine identifier |
| `parent_category_id` | INTEGER | No | Parent category |
| `description` | TEXT | No | Description |
| `is_active` | INTEGER | Yes | Active flag |
| `sort_order` | INTEGER | Yes | Display ordering |
| `created_at` | TEXT | Yes | Created UTC |
| `updated_at` | TEXT | Yes | Updated UTC |

DDL:

```sql
CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY,

    scope TEXT NOT NULL CHECK (
        scope IN (
            'GENERAL',
            'TICKET',
            'KNOWLEDGE',
            'SCRIPT',
            'PROMPT',
            'CLIPBOARD',
            'DIAGNOSTIC'
        )
    ),

    name TEXT NOT NULL COLLATE NOCASE
        CHECK (length(trim(name)) > 0),

    slug TEXT NOT NULL COLLATE NOCASE UNIQUE
        CHECK (length(trim(slug)) > 0),

    parent_category_id INTEGER,

    description TEXT,

    is_active INTEGER NOT NULL DEFAULT 1
        CHECK (is_active IN (0, 1)),

    sort_order INTEGER NOT NULL DEFAULT 0,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    FOREIGN KEY (parent_category_id)
        REFERENCES categories(category_id)
        ON DELETE SET NULL,

    CHECK (
        parent_category_id IS NULL
        OR parent_category_id <> category_id
    )
);
```

Application-level invariant:

> A parent category must be compatible with the child's scope and category cycles must be rejected.

SQLite should not attempt to implement recursive cycle-detection triggers for this initial design.

---

# 33. `tags`

Purpose:

Reusable flat labels.

Examples:

```text
vpn
outlook
m365
security
password-reset
printer
```

DDL:

```sql
CREATE TABLE tags (
    tag_id INTEGER PRIMARY KEY,

    name TEXT NOT NULL COLLATE NOCASE UNIQUE
        CHECK (length(trim(name)) > 0),

    slug TEXT NOT NULL COLLATE NOCASE UNIQUE
        CHECK (length(trim(slug)) > 0),

    description TEXT,

    created_at TEXT NOT NULL
);
```

Tags remain flat.

Categories handle hierarchy.

---

# 34. Company Domain

## `companies`

Purpose:

Represent organizations associated with tickets, contacts, KB context, integrations, and support work.

DDL:

```sql
CREATE TABLE companies (
    company_id INTEGER PRIMARY KEY,

    company_code TEXT COLLATE NOCASE UNIQUE,

    name TEXT NOT NULL
        CHECK (length(trim(name)) > 0),

    domain TEXT COLLATE NOCASE,
    phone TEXT,
    website_url TEXT,

    address_line1 TEXT,
    address_line2 TEXT,
    city TEXT,
    region TEXT,
    postal_code TEXT,
    country_code TEXT,

    is_active INTEGER NOT NULL DEFAULT 1
        CHECK (is_active IN (0, 1)),

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

`name` is intentionally not unique.

Different organizations may legitimately have similar or identical names.

`company_code` may provide a stable short identifier when needed.

---

# 35. `company_notes`

Purpose:

Store internal contextual notes about a company.

DDL:

```sql
CREATE TABLE company_notes (
    company_note_id INTEGER PRIMARY KEY,

    company_id INTEGER NOT NULL,

    note_text TEXT NOT NULL
        CHECK (length(trim(note_text)) > 0),

    is_pinned INTEGER NOT NULL DEFAULT 0
        CHECK (is_pinned IN (0, 1)),

    created_by TEXT,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    FOREIGN KEY (company_id)
        REFERENCES companies(company_id)
        ON DELETE CASCADE
);
```

---

# 36. `company_links`

Purpose:

Store useful URLs associated with companies.

Examples:

```text
customer portal
documentation
remote management portal
SharePoint site
vendor page
```

DDL:

```sql
CREATE TABLE company_links (
    company_link_id INTEGER PRIMARY KEY,

    company_id INTEGER NOT NULL,

    link_type TEXT,

    label TEXT NOT NULL
        CHECK (length(trim(label)) > 0),

    url TEXT NOT NULL
        CHECK (length(trim(url)) > 0),

    sort_order INTEGER NOT NULL DEFAULT 0,

    created_at TEXT NOT NULL,

    FOREIGN KEY (company_id)
        REFERENCES companies(company_id)
        ON DELETE CASCADE
);
```

---

# 37. Contact Domain

## `contacts`

Purpose:

Represent people associated with companies and support tickets.

DDL:

```sql
CREATE TABLE contacts (
    contact_id INTEGER PRIMARY KEY,

    company_id INTEGER,

    display_name TEXT NOT NULL
        CHECK (length(trim(display_name)) > 0),

    first_name TEXT,
    last_name TEXT,
    job_title TEXT,

    email TEXT COLLATE NOCASE,

    phone TEXT,
    mobile_phone TEXT,
    notes TEXT,

    is_active INTEGER NOT NULL DEFAULT 1
        CHECK (is_active IN (0, 1)),

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    FOREIGN KEY (company_id)
        REFERENCES companies(company_id)
        ON DELETE SET NULL
);
```

Email is not globally unique.

Potential realities include:

- shared mailboxes
- duplicate contacts
- incomplete data
- aliases

---

# 38. Company / Contact Invariant

When both:

```text
ticket.company_id
ticket.contact_id
```

are present, the application should normally validate that the contact belongs to the selected company.

This relationship is enforced in the service/domain layer because enforcing it through a composite SQLite foreign key would complicate nullable and reassignment behavior.

---

# 39. Ticket Domain

The ticket schema is central to F7Hub.

Ticket lifecycle:

```text
NEW
OPEN
IN_PROGRESS
WAITING
RESOLVED
CLOSED
CANCELLED
```

Supported ticket types:

```text
INCIDENT
SERVICE_REQUEST
PROBLEM
TASK
```

Priority:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

---

# 40. `tickets`

DDL:

```sql
CREATE TABLE tickets (
    ticket_id INTEGER PRIMARY KEY,

    ticket_number TEXT NOT NULL COLLATE NOCASE UNIQUE
        CHECK (length(trim(ticket_number)) > 0),

    ticket_type TEXT NOT NULL DEFAULT 'INCIDENT'
        CHECK (
            ticket_type IN (
                'INCIDENT',
                'SERVICE_REQUEST',
                'PROBLEM',
                'TASK'
            )
        ),

    status TEXT NOT NULL DEFAULT 'NEW'
        CHECK (
            status IN (
                'NEW',
                'OPEN',
                'IN_PROGRESS',
                'WAITING',
                'RESOLVED',
                'CLOSED',
                'CANCELLED'
            )
        ),

    priority TEXT NOT NULL DEFAULT 'MEDIUM'
        CHECK (
            priority IN (
                'LOW',
                'MEDIUM',
                'HIGH',
                'CRITICAL'
            )
        ),

    company_id INTEGER,
    contact_id INTEGER,
    category_id INTEGER,

    subject TEXT NOT NULL
        CHECK (length(trim(subject)) > 0),

    description TEXT,
    resolution TEXT,

    assigned_to TEXT,
    source TEXT,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    resolved_at TEXT,
    closed_at TEXT,

    FOREIGN KEY (company_id)
        REFERENCES companies(company_id)
        ON DELETE SET NULL,

    FOREIGN KEY (contact_id)
        REFERENCES contacts(contact_id)
        ON DELETE SET NULL,

    FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
        ON DELETE SET NULL,

    CHECK (
        resolved_at IS NULL
        OR status IN ('RESOLVED', 'CLOSED')
    ),

    CHECK (
        closed_at IS NULL
        OR status = 'CLOSED'
    )
);
```

---

# 41. Ticket Number

`ticket_id` and `ticket_number` are different.

Example:

```text
ticket_id
→ 472

ticket_number
→ INC-1023
```

`ticket_id` is the relational key.

`ticket_number` is a stable technician-facing reference.

Generation belongs to the application service.

---

# 42. Ticket Source

`source` is intentionally flexible initially.

Potential values:

```text
MANUAL
PORTAL
EMAIL
HALOPSA
IMPORT
API
```

It is not constrained yet because external integration architecture is not finalized.

If source behavior becomes domain-critical, standardize it later.

---

# 43. `ticket_notes`

Purpose:

Persistent technician/user/resolution notes.

DDL:

```sql
CREATE TABLE ticket_notes (
    ticket_note_id INTEGER PRIMARY KEY,

    ticket_id INTEGER NOT NULL,

    note_type TEXT NOT NULL DEFAULT 'INTERNAL'
        CHECK (
            note_type IN (
                'INTERNAL',
                'PUBLIC',
                'WORKLOG',
                'RESOLUTION'
            )
        ),

    note_text TEXT NOT NULL
        CHECK (length(trim(note_text)) > 0),

    author_label TEXT,
    source TEXT,

    is_ai_generated INTEGER NOT NULL DEFAULT 0
        CHECK (is_ai_generated IN (0, 1)),

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    FOREIGN KEY (ticket_id)
        REFERENCES tickets(ticket_id)
        ON DELETE CASCADE
);
```

AI-generated notes must remain explicitly identifiable.

---

# 44. `ticket_status_history`

Purpose:

Preserve ticket lifecycle transitions.

DDL:

```sql
CREATE TABLE ticket_status_history (
    ticket_status_history_id INTEGER PRIMARY KEY,

    ticket_id INTEGER NOT NULL,

    previous_status TEXT
        CHECK (
            previous_status IS NULL
            OR previous_status IN (
                'NEW',
                'OPEN',
                'IN_PROGRESS',
                'WAITING',
                'RESOLVED',
                'CLOSED',
                'CANCELLED'
            )
        ),

    new_status TEXT NOT NULL
        CHECK (
            new_status IN (
                'NEW',
                'OPEN',
                'IN_PROGRESS',
                'WAITING',
                'RESOLVED',
                'CLOSED',
                'CANCELLED'
            )
        ),

    reason TEXT,
    changed_by TEXT,
    changed_at TEXT NOT NULL,

    FOREIGN KEY (ticket_id)
        REFERENCES tickets(ticket_id)
        ON DELETE CASCADE,

    CHECK (
        previous_status IS NULL
        OR previous_status <> new_status
    )
);
```

Status history should be created by `TicketService` in the same transaction as the status update.

The notes and lifecycle service boundary was verified on 2026-09-04 using this unchanged schema. Notes, resolution notes, history and timeline events are written within service-coordinated transactions. Reopening clears incompatible lifecycle timestamps while preserving prior resolution content in notes. The exact transition policy belongs to `13_PythonArchitecture.md`.

---

# 45. Ticket Status Transaction

Changing status should conceptually perform:

```text
BEGIN
    ↓
Validate transition
    ↓
UPDATE tickets
    ↓
INSERT ticket_status_history
    ↓
INSERT ticket_timeline_events if required
    ↓
COMMIT
```

All operations should succeed together.

---

# 46. `ticket_timeline_events`

Purpose:

Represent significant chronological ticket activity.

Examples:

```text
ticket created
status changed
note added
diagnostic completed
script executed
KB linked
attachment added
external sync occurred
```

DDL:

```sql
CREATE TABLE ticket_timeline_events (
    ticket_timeline_event_id INTEGER PRIMARY KEY,

    ticket_id INTEGER NOT NULL,

    event_type TEXT NOT NULL
        CHECK (length(trim(event_type)) > 0),

    title TEXT NOT NULL
        CHECK (length(trim(title)) > 0),

    details TEXT,
    metadata_json TEXT,
    actor_label TEXT,

    occurred_at TEXT NOT NULL,

    FOREIGN KEY (ticket_id)
        REFERENCES tickets(ticket_id)
        ON DELETE CASCADE
);
```

`metadata_json` is appropriate because event-specific metadata varies widely.

---

# 47. Timeline Is Not Audit

Ticket timeline:

```text
technician-oriented ticket history
```

Audit log:

```text
system/security/administrative trace
```

They must not be treated as identical systems.

---

# 48. `ticket_attachments`

Files remain in the filesystem.

SQLite stores metadata.

DDL:

```sql
CREATE TABLE ticket_attachments (
    ticket_attachment_id INTEGER PRIMARY KEY,

    ticket_id INTEGER NOT NULL,

    original_file_name TEXT NOT NULL
        CHECK (length(trim(original_file_name)) > 0),

    stored_file_name TEXT NOT NULL
        CHECK (length(trim(stored_file_name)) > 0),

    relative_path TEXT NOT NULL COLLATE NOCASE UNIQUE
        CHECK (length(trim(relative_path)) > 0),

    media_type TEXT,

    size_bytes INTEGER NOT NULL
        CHECK (size_bytes >= 0),

    sha256 TEXT,
    description TEXT,
    added_by TEXT,
    added_at TEXT NOT NULL,

    FOREIGN KEY (ticket_id)
        REFERENCES tickets(ticket_id)
        ON DELETE CASCADE
);
```

Preferred physical relationship:

```text
ticket_attachments
        ↓
relative_path
        ↓
Data\Attachments\
```

Do not store large attachments as SQLite BLOBs by default.

---

# 49. Attachment Safety

File handling must validate:

- generated storage filename
- relative path
- path traversal
- file existence
- duplicate collisions
- file size
- optional hash
- unsafe execution

Deleting metadata should not silently delete files without an explicitly designed coordinated workflow.

---

# 50. `ticket_relationships`

Purpose:

Connect related tickets.

DDL:

```sql
CREATE TABLE ticket_relationships (
    ticket_relationship_id INTEGER PRIMARY KEY,

    ticket_id INTEGER NOT NULL,
    related_ticket_id INTEGER NOT NULL,

    relationship_type TEXT NOT NULL
        CHECK (
            relationship_type IN (
                'RELATED_TO',
                'DUPLICATE_OF',
                'PARENT_OF',
                'BLOCKS'
            )
        ),

    created_by TEXT,
    created_at TEXT NOT NULL,

    FOREIGN KEY (ticket_id)
        REFERENCES tickets(ticket_id)
        ON DELETE CASCADE,

    FOREIGN KEY (related_ticket_id)
        REFERENCES tickets(ticket_id)
        ON DELETE CASCADE,

    CHECK (ticket_id <> related_ticket_id),

    UNIQUE (
        ticket_id,
        related_ticket_id,
        relationship_type
    )
);
```

Do not automatically store a reciprocal relationship unless application semantics require one.

---

# 51. `ticket_tags`

Many-to-many ticket/tag relationship.

```sql
CREATE TABLE ticket_tags (
    ticket_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,

    created_at TEXT NOT NULL,

    PRIMARY KEY (
        ticket_id,
        tag_id
    ),

    FOREIGN KEY (ticket_id)
        REFERENCES tickets(ticket_id)
        ON DELETE CASCADE,

    FOREIGN KEY (tag_id)
        REFERENCES tags(tag_id)
        ON DELETE CASCADE
);
```

---

# 52. Knowledge Domain

Knowledge lifecycle:

```text
DRAFT
PUBLISHED
ARCHIVED
```

Knowledge articles use Markdown as their canonical rich-text representation.

---

# 53. `knowledge_articles`

```sql
CREATE TABLE knowledge_articles (
    knowledge_article_id INTEGER PRIMARY KEY,

    article_code TEXT NOT NULL COLLATE NOCASE UNIQUE
        CHECK (length(trim(article_code)) > 0),

    category_id INTEGER,

    title TEXT NOT NULL
        CHECK (length(trim(title)) > 0),

    summary TEXT,

    body_markdown TEXT NOT NULL,

    status TEXT NOT NULL DEFAULT 'DRAFT'
        CHECK (
            status IN (
                'DRAFT',
                'PUBLISHED',
                'ARCHIVED'
            )
        ),

    version_number INTEGER NOT NULL DEFAULT 1
        CHECK (version_number >= 1),

    created_by TEXT,
    updated_by TEXT,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    published_at TEXT,

    FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
        ON DELETE SET NULL,

    CHECK (
        published_at IS NULL
        OR status IN ('PUBLISHED', 'ARCHIVED')
    )
);
```

---

# 54. Article Code

Example:

```text
knowledge_article_id
→ 125

article_code
→ KB00125
```

The internal ID is relational.

The article code is technician-facing.

---

# 55. `knowledge_article_versions`

Purpose:

Preserve historical snapshots.

```sql
CREATE TABLE knowledge_article_versions (
    knowledge_article_version_id INTEGER PRIMARY KEY,

    knowledge_article_id INTEGER NOT NULL,

    version_number INTEGER NOT NULL
        CHECK (version_number >= 1),

    title TEXT NOT NULL
        CHECK (length(trim(title)) > 0),

    summary TEXT,
    body_markdown TEXT NOT NULL,

    change_summary TEXT,
    created_by TEXT,
    created_at TEXT NOT NULL,

    FOREIGN KEY (knowledge_article_id)
        REFERENCES knowledge_articles(knowledge_article_id)
        ON DELETE CASCADE,

    UNIQUE (
        knowledge_article_id,
        version_number
    )
);
```

The current version remains in `knowledge_articles`.

Historical snapshots live here.

---

# 56. Knowledge Version Transaction

Article update may perform:

```text
BEGIN
    ↓
Snapshot current version
    ↓
Increment version_number
    ↓
Update current article
    ↓
COMMIT
```

Exact snapshot timing should be implemented consistently.

---

# 57. `knowledge_article_links`

```sql
CREATE TABLE knowledge_article_links (
    knowledge_article_link_id INTEGER PRIMARY KEY,

    knowledge_article_id INTEGER NOT NULL,

    link_type TEXT,

    label TEXT NOT NULL
        CHECK (length(trim(label)) > 0),

    url TEXT NOT NULL
        CHECK (length(trim(url)) > 0),

    sort_order INTEGER NOT NULL DEFAULT 0,

    created_at TEXT NOT NULL,

    FOREIGN KEY (knowledge_article_id)
        REFERENCES knowledge_articles(knowledge_article_id)
        ON DELETE CASCADE
);
```

---

# 58. `knowledge_article_relationships`

```sql
CREATE TABLE knowledge_article_relationships (
    knowledge_article_relationship_id INTEGER PRIMARY KEY,

    knowledge_article_id INTEGER NOT NULL,
    related_knowledge_article_id INTEGER NOT NULL,

    relationship_type TEXT NOT NULL
        CHECK (
            relationship_type IN (
                'RELATED',
                'PREREQUISITE',
                'SUPERSEDES',
                'DUPLICATES'
            )
        ),

    created_at TEXT NOT NULL,

    FOREIGN KEY (knowledge_article_id)
        REFERENCES knowledge_articles(knowledge_article_id)
        ON DELETE CASCADE,

    FOREIGN KEY (related_knowledge_article_id)
        REFERENCES knowledge_articles(knowledge_article_id)
        ON DELETE CASCADE,

    CHECK (
        knowledge_article_id
        <> related_knowledge_article_id
    ),

    UNIQUE (
        knowledge_article_id,
        related_knowledge_article_id,
        relationship_type
    )
);
```

---

# 59. `ticket_knowledge_articles`

Purpose:

Link knowledge to actual support work.

```sql
CREATE TABLE ticket_knowledge_articles (
    ticket_id INTEGER NOT NULL,
    knowledge_article_id INTEGER NOT NULL,

    relationship_type TEXT NOT NULL DEFAULT 'RELATED'
        CHECK (
            relationship_type IN (
                'RELATED',
                'APPLIED',
                'RESOLUTION_SOURCE'
            )
        ),

    linked_by TEXT,
    linked_at TEXT NOT NULL,

    PRIMARY KEY (
        ticket_id,
        knowledge_article_id,
        relationship_type
    ),

    FOREIGN KEY (ticket_id)
        REFERENCES tickets(ticket_id)
        ON DELETE CASCADE,

    FOREIGN KEY (knowledge_article_id)
        REFERENCES knowledge_articles(knowledge_article_id)
        ON DELETE CASCADE
);
```

This enables workflows such as:

```text
Ticket
→ suggested KB

Ticket
→ KB used during troubleshooting

Resolved Ticket
→ KB responsible for resolution
```

---

# 60. `knowledge_article_tags`

```sql
CREATE TABLE knowledge_article_tags (
    knowledge_article_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,

    created_at TEXT NOT NULL,

    PRIMARY KEY (
        knowledge_article_id,
        tag_id
    ),

    FOREIGN KEY (knowledge_article_id)
        REFERENCES knowledge_articles(knowledge_article_id)
        ON DELETE CASCADE,

    FOREIGN KEY (tag_id)
        REFERENCES tags(tag_id)
        ON DELETE CASCADE
);
```

---

# 61. Automation Domain

PowerShell source remains in files.

SQLite stores registry metadata.

Preferred source:

```text
PowerShell\
```

Registry:

```text
scripts
script_parameters
script_tags
```

Execution history:

```text
script_executions
```

---

# 62. `scripts`

```sql
CREATE TABLE scripts (
    script_id INTEGER PRIMARY KEY,

    category_id INTEGER,

    script_code TEXT NOT NULL COLLATE NOCASE UNIQUE
        CHECK (length(trim(script_code)) > 0),

    name TEXT NOT NULL
        CHECK (length(trim(name)) > 0),

    description TEXT,

    relative_path TEXT NOT NULL COLLATE NOCASE UNIQUE
        CHECK (length(trim(relative_path)) > 0),

    script_type TEXT NOT NULL
        CHECK (
            script_type IN (
                'DIAGNOSTIC',
                'REMEDIATION',
                'ADMINISTRATIVE',
                'REPORT',
                'UTILITY',
                'INTEGRATION'
            )
        ),

    runtime TEXT NOT NULL DEFAULT 'POWERSHELL_7'
        CHECK (
            runtime IN (
                'POWERSHELL_7',
                'WINDOWS_POWERSHELL_5_1'
            )
        ),

    risk_level TEXT NOT NULL DEFAULT 'LOW'
        CHECK (
            risk_level IN (
                'LOW',
                'MEDIUM',
                'HIGH',
                'CRITICAL'
            )
        ),

    privilege_level TEXT NOT NULL DEFAULT 'STANDARD_USER'
        CHECK (
            privilege_level IN (
                'STANDARD_USER',
                'LOCAL_ADMIN',
                'M365_AUTHENTICATED',
                'M365_PRIVILEGED',
                'SPECIAL_ROLE'
            )
        ),

    version TEXT,
    checksum_sha256 TEXT,

    timeout_seconds INTEGER NOT NULL DEFAULT 120
        CHECK (timeout_seconds > 0),

    requires_structured_output INTEGER NOT NULL DEFAULT 1
        CHECK (
            requires_structured_output IN (0, 1)
        ),

    is_enabled INTEGER NOT NULL DEFAULT 1
        CHECK (is_enabled IN (0, 1)),

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
        ON DELETE SET NULL
);
```

---

# 63. Script Code vs Filename

Example:

```text
script_id
→ 14

script_code
→ diagnostic.dns.health

name
→ Test DNS Health

relative_path
→ PowerShell\Diagnostics\Networking\Test-DnsHealth.ps1
```

These are distinct concepts.

---

# 64. Script Deletion

Scripts with execution history should generally not be deleted.

Instead:

```text
is_enabled = 0
```

Execution history uses:

```sql
ON DELETE RESTRICT
```

to preserve historical integrity.

---

# 65. `script_parameters`

```sql
CREATE TABLE script_parameters (
    script_parameter_id INTEGER PRIMARY KEY,

    script_id INTEGER NOT NULL,

    parameter_name TEXT NOT NULL COLLATE NOCASE
        CHECK (length(trim(parameter_name)) > 0),

    parameter_type TEXT NOT NULL
        CHECK (
            parameter_type IN (
                'STRING',
                'INTEGER',
                'BOOLEAN',
                'DECIMAL',
                'CHOICE',
                'STRING_LIST',
                'PATH',
                'UPN',
                'HOSTNAME'
            )
        ),

    is_required INTEGER NOT NULL DEFAULT 0
        CHECK (is_required IN (0, 1)),

    is_sensitive INTEGER NOT NULL DEFAULT 0
        CHECK (is_sensitive IN (0, 1)),

    default_value_json TEXT,
    validation_json TEXT,
    help_text TEXT,

    sort_order INTEGER NOT NULL DEFAULT 0,

    FOREIGN KEY (script_id)
        REFERENCES scripts(script_id)
        ON DELETE CASCADE,

    UNIQUE (
        script_id,
        parameter_name
    )
);
```

---

# 66. Sensitive Parameters

Examples:

```text
password
secret
token
private key
```

should not normally be persisted as parameter defaults.

`is_sensitive` indicates that execution/logging paths must redact or exclude the value.

---

# 67. `script_executions`

Purpose:

Record meaningful execution history without turning SQLite into a transcript archive.

```sql
CREATE TABLE script_executions (
    script_execution_id INTEGER PRIMARY KEY,

    script_id INTEGER NOT NULL,
    ticket_id INTEGER,

    status TEXT NOT NULL
        CHECK (
            status IN (
                'QUEUED',
                'RUNNING',
                'PASS',
                'FAIL',
                'WARNING',
                'ERROR',
                'CANCELLED',
                'TIMED_OUT'
            )
        ),

    initiated_by TEXT,

    sanitized_parameters_json TEXT,
    result_json TEXT,

    result_message TEXT,
    error_summary TEXT,

    log_relative_path TEXT,

    exit_code INTEGER,

    started_at TEXT NOT NULL,
    completed_at TEXT,

    duration_ms INTEGER
        CHECK (
            duration_ms IS NULL
            OR duration_ms >= 0
        ),

    correlation_id TEXT,

    FOREIGN KEY (script_id)
        REFERENCES scripts(script_id)
        ON DELETE RESTRICT,

    FOREIGN KEY (ticket_id)
        REFERENCES tickets(ticket_id)
        ON DELETE SET NULL,

    CHECK (
        completed_at IS NULL
        OR status NOT IN ('QUEUED', 'RUNNING')
    )
);
```

Raw stdout/stderr are captured during execution but are not automatically stored forever in SQLite.

If raw execution output must be retained:

```text
Logs\
or
another controlled file location
```

may be referenced using `log_relative_path`.

---

# 68. `script_tags`

```sql
CREATE TABLE script_tags (
    script_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,

    created_at TEXT NOT NULL,

    PRIMARY KEY (
        script_id,
        tag_id
    ),

    FOREIGN KEY (script_id)
        REFERENCES scripts(script_id)
        ON DELETE CASCADE,

    FOREIGN KEY (tag_id)
        REFERENCES tags(tag_id)
        ON DELETE CASCADE
);
```

---

# 69. `knowledge_article_scripts`

Links KB documentation to automation.

```sql
CREATE TABLE knowledge_article_scripts (
    knowledge_article_id INTEGER NOT NULL,
    script_id INTEGER NOT NULL,

    relationship_type TEXT NOT NULL DEFAULT 'RELATED'
        CHECK (
            relationship_type IN (
                'RELATED',
                'DIAGNOSTIC',
                'REMEDIATION',
                'REFERENCE'
            )
        ),

    created_at TEXT NOT NULL,

    PRIMARY KEY (
        knowledge_article_id,
        script_id,
        relationship_type
    ),

    FOREIGN KEY (knowledge_article_id)
        REFERENCES knowledge_articles(knowledge_article_id)
        ON DELETE CASCADE,

    FOREIGN KEY (script_id)
        REFERENCES scripts(script_id)
        ON DELETE RESTRICT
);
```

---

# 70. Diagnostic Domain

The Diagnostic Engine requires deterministic workflow persistence.

Core chain:

```text
diagnostic_workflows
        ↓
diagnostic_steps
        ↓
diagnostic_conditions
        ↓
diagnostic_sessions
        ↓
diagnostic_responses
        ↓
diagnostic_results
```

---

# 71. `diagnostic_workflows`

```sql
CREATE TABLE diagnostic_workflows (
    diagnostic_workflow_id INTEGER PRIMARY KEY,

    category_id INTEGER,

    workflow_code TEXT NOT NULL COLLATE NOCASE UNIQUE
        CHECK (length(trim(workflow_code)) > 0),

    name TEXT NOT NULL
        CHECK (length(trim(name)) > 0),

    description TEXT,

    version_number INTEGER NOT NULL DEFAULT 1
        CHECK (version_number >= 1),

    status TEXT NOT NULL DEFAULT 'DRAFT'
        CHECK (
            status IN (
                'DRAFT',
                'ACTIVE',
                'ARCHIVED'
            )
        ),

    created_by TEXT,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
        ON DELETE SET NULL
);
```

---

# 72. Workflow Versioning

Published/active workflow definitions should not be silently modified in ways that invalidate historical sessions.

A diagnostic session records:

```text
workflow_version_number
```

Later, if workflow-definition version history becomes sophisticated enough to require immutable workflow revisions, a dedicated revision model may be added.

Do not create that complexity until necessary.

---

# 73. `diagnostic_steps`

```sql
CREATE TABLE diagnostic_steps (
    diagnostic_step_id INTEGER PRIMARY KEY,

    diagnostic_workflow_id INTEGER NOT NULL,

    step_key TEXT NOT NULL COLLATE NOCASE
        CHECK (length(trim(step_key)) > 0),

    step_order INTEGER NOT NULL DEFAULT 0,

    step_type TEXT NOT NULL
        CHECK (
            step_type IN (
                'QUESTION',
                'INSTRUCTION',
                'CONDITION',
                'SCRIPT',
                'RESULT'
            )
        ),

    title TEXT NOT NULL
        CHECK (length(trim(title)) > 0),

    prompt_text TEXT,

    input_type TEXT NOT NULL DEFAULT 'NONE'
        CHECK (
            input_type IN (
                'NONE',
                'TEXT',
                'MULTILINE',
                'BOOLEAN',
                'INTEGER',
                'DECIMAL',
                'SELECT',
                'MULTISELECT'
            )
        ),

    is_required INTEGER NOT NULL DEFAULT 0
        CHECK (is_required IN (0, 1)),

    is_entry INTEGER NOT NULL DEFAULT 0
        CHECK (is_entry IN (0, 1)),

    script_id INTEGER,

    default_next_step_id INTEGER,

    config_json TEXT,

    FOREIGN KEY (diagnostic_workflow_id)
        REFERENCES diagnostic_workflows(
            diagnostic_workflow_id
        )
        ON DELETE CASCADE,

    FOREIGN KEY (script_id)
        REFERENCES scripts(script_id)
        ON DELETE RESTRICT,

    FOREIGN KEY (default_next_step_id)
        REFERENCES diagnostic_steps(
            diagnostic_step_id
        )
        ON DELETE SET NULL
        DEFERRABLE INITIALLY DEFERRED,

    UNIQUE (
        diagnostic_workflow_id,
        step_key
    )
);
```

---

# 74. Diagnostic Entry Step

Each workflow may have at most one entry step.

This is enforced with the partial unique index `ux_diagnostic_steps_one_entry` in the canonical Diagnostic Indexes section below.

Application validation should also require exactly one entry step before a workflow can become `ACTIVE`.

---

# 75. `diagnostic_conditions`

Purpose:

Define deterministic branch rules.

```sql
CREATE TABLE diagnostic_conditions (
    diagnostic_condition_id INTEGER PRIMARY KEY,

    source_step_id INTEGER NOT NULL,

    operator TEXT NOT NULL
        CHECK (
            operator IN (
                'EQUALS',
                'NOT_EQUALS',
                'CONTAINS',
                'NOT_CONTAINS',
                'GT',
                'GTE',
                'LT',
                'LTE',
                'IS_TRUE',
                'IS_FALSE',
                'IS_EMPTY',
                'NOT_EMPTY',
                'STATUS_IS'
            )
        ),

    comparison_value_json TEXT,

    next_step_id INTEGER NOT NULL,

    priority INTEGER NOT NULL DEFAULT 0,

    FOREIGN KEY (source_step_id)
        REFERENCES diagnostic_steps(
            diagnostic_step_id
        )
        ON DELETE CASCADE,

    FOREIGN KEY (next_step_id)
        REFERENCES diagnostic_steps(
            diagnostic_step_id
        )
        ON DELETE RESTRICT
);
```

---

# 76. Condition Evaluation

Example:

```text
Question:
Can the user resolve the VPN gateway hostname?

Response:
false

Condition:
IS_FALSE

Next step:
Test-DnsHealth
```

Evaluation must be deterministic.

AI should not determine ordinary branching.

---

# 77. Cross-Workflow Step Protection

The application must validate:

> `next_step_id` belongs to the same workflow as `source_step_id`.

SQLite does not enforce this cross-row domain invariant in the initial schema.

`DiagnosticService` must enforce it.

Tests are required.

---

# 78. `diagnostic_sessions`

```sql
CREATE TABLE diagnostic_sessions (
    diagnostic_session_id INTEGER PRIMARY KEY,

    diagnostic_workflow_id INTEGER NOT NULL,

    ticket_id INTEGER,

    current_step_id INTEGER,

    workflow_version_number INTEGER NOT NULL
        CHECK (workflow_version_number >= 1),

    status TEXT NOT NULL DEFAULT 'IN_PROGRESS'
        CHECK (
            status IN (
                'IN_PROGRESS',
                'COMPLETED',
                'CANCELLED',
                'FAILED'
            )
        ),

    started_by TEXT,

    context_json TEXT,

    started_at TEXT NOT NULL,
    completed_at TEXT,

    FOREIGN KEY (diagnostic_workflow_id)
        REFERENCES diagnostic_workflows(
            diagnostic_workflow_id
        )
        ON DELETE RESTRICT,

    FOREIGN KEY (ticket_id)
        REFERENCES tickets(ticket_id)
        ON DELETE SET NULL,

    FOREIGN KEY (current_step_id)
        REFERENCES diagnostic_steps(
            diagnostic_step_id
        )
        ON DELETE SET NULL,

    CHECK (
        completed_at IS NULL
        OR status IN (
            'COMPLETED',
            'CANCELLED',
            'FAILED'
        )
    )
);
```

---

# 79. `diagnostic_responses`

```sql
CREATE TABLE diagnostic_responses (
    diagnostic_response_id INTEGER PRIMARY KEY,

    diagnostic_session_id INTEGER NOT NULL,

    diagnostic_step_id INTEGER NOT NULL,

    response_json TEXT NOT NULL,

    responded_at TEXT NOT NULL,

    FOREIGN KEY (diagnostic_session_id)
        REFERENCES diagnostic_sessions(
            diagnostic_session_id
        )
        ON DELETE CASCADE,

    FOREIGN KEY (diagnostic_step_id)
        REFERENCES diagnostic_steps(
            diagnostic_step_id
        )
        ON DELETE RESTRICT,

    UNIQUE (
        diagnostic_session_id,
        diagnostic_step_id
    )
);
```

One current response is retained per step/session.

If response revision history later becomes necessary, add a dedicated response-history model rather than weakening this invariant.

---

# 80. `diagnostic_results`

```sql
CREATE TABLE diagnostic_results (
    diagnostic_result_id INTEGER PRIMARY KEY,

    diagnostic_session_id INTEGER NOT NULL,

    diagnostic_step_id INTEGER,

    script_execution_id INTEGER,

    status TEXT NOT NULL
        CHECK (
            status IN (
                'PASS',
                'FAIL',
                'WARNING',
                'ERROR',
                'NOT_APPLICABLE'
            )
        ),

    summary TEXT,

    data_json TEXT,
    warnings_json TEXT,
    errors_json TEXT,

    created_at TEXT NOT NULL,

    FOREIGN KEY (diagnostic_session_id)
        REFERENCES diagnostic_sessions(
            diagnostic_session_id
        )
        ON DELETE CASCADE,

    FOREIGN KEY (diagnostic_step_id)
        REFERENCES diagnostic_steps(
            diagnostic_step_id
        )
        ON DELETE SET NULL,

    FOREIGN KEY (script_execution_id)
        REFERENCES script_executions(
            script_execution_id
        )
        ON DELETE SET NULL
);
```

---

# 81. Diagnostic Result Contract

The PowerShell layer may return:

```json
{
  "schemaVersion": 1,
  "operation": "Test-DnsHealth",
  "success": true,
  "status": "PASS",
  "message": "DNS resolution succeeded.",
  "data": {},
  "warnings": [],
  "errors": []
}
```

Python validates this.

Relevant structured information may then be stored in:

```text
diagnostic_results
```

---

# 82. `diagnostic_workflow_articles`

```sql
CREATE TABLE diagnostic_workflow_articles (
    diagnostic_workflow_id INTEGER NOT NULL,
    knowledge_article_id INTEGER NOT NULL,

    created_at TEXT NOT NULL,

    PRIMARY KEY (
        diagnostic_workflow_id,
        knowledge_article_id
    ),

    FOREIGN KEY (diagnostic_workflow_id)
        REFERENCES diagnostic_workflows(
            diagnostic_workflow_id
        )
        ON DELETE CASCADE,

    FOREIGN KEY (knowledge_article_id)
        REFERENCES knowledge_articles(
            knowledge_article_id
        )
        ON DELETE CASCADE
);
```

This allows workflow steps and diagnostic sessions to surface relevant KB material without duplicating article content.

---

# 83. Prompt Domain

Prompts are stored as structured reusable templates.

AI provider configuration does not belong directly inside the prompt entity unless future requirements justify it.

---

# 84. `prompt_templates`

```sql
CREATE TABLE prompt_templates (
    prompt_template_id INTEGER PRIMARY KEY,

    category_id INTEGER,

    prompt_code TEXT NOT NULL COLLATE NOCASE UNIQUE
        CHECK (length(trim(prompt_code)) > 0),

    name TEXT NOT NULL
        CHECK (length(trim(name)) > 0),

    description TEXT,
    purpose TEXT,

    template_text TEXT NOT NULL,

    status TEXT NOT NULL DEFAULT 'DRAFT'
        CHECK (
            status IN (
                'DRAFT',
                'ACTIVE',
                'ARCHIVED'
            )
        ),

    version_number INTEGER NOT NULL DEFAULT 1
        CHECK (version_number >= 1),

    created_by TEXT,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
        ON DELETE SET NULL
);
```

---

# 85. `prompt_variables`

```sql
CREATE TABLE prompt_variables (
    prompt_variable_id INTEGER PRIMARY KEY,

    prompt_template_id INTEGER NOT NULL,

    variable_name TEXT NOT NULL COLLATE NOCASE
        CHECK (length(trim(variable_name)) > 0),

    data_type TEXT NOT NULL DEFAULT 'TEXT'
        CHECK (
            data_type IN (
                'TEXT',
                'INTEGER',
                'BOOLEAN',
                'JSON'
            )
        ),

    is_required INTEGER NOT NULL DEFAULT 0
        CHECK (is_required IN (0, 1)),

    is_sensitive INTEGER NOT NULL DEFAULT 0
        CHECK (is_sensitive IN (0, 1)),

    default_value TEXT,
    description TEXT,

    sort_order INTEGER NOT NULL DEFAULT 0,

    FOREIGN KEY (prompt_template_id)
        REFERENCES prompt_templates(
            prompt_template_id
        )
        ON DELETE CASCADE,

    UNIQUE (
        prompt_template_id,
        variable_name
    )
);
```

---

# 86. Prompt Security

Sensitive prompt variables must not automatically be:

- logged
- exported
- persisted into AI history
- sent to providers without appropriate controls

`is_sensitive` supports application policy.

It is not itself sufficient protection.

---

# 87. Clipboard Domain

Persistent clipboard storage and normal Windows clipboard interaction are different concerns.

AHK may handle capture/automation.

Python owns persistent storage.

---

# 88. `clipboard_snippets`

Purpose:

Store technician-approved reusable text snippets.

```sql
CREATE TABLE clipboard_snippets (
    clipboard_snippet_id INTEGER PRIMARY KEY,

    category_id INTEGER,

    title TEXT NOT NULL
        CHECK (length(trim(title)) > 0),

    content_text TEXT NOT NULL,

    content_format TEXT NOT NULL DEFAULT 'PLAIN_TEXT'
        CHECK (
            content_format IN (
                'PLAIN_TEXT',
                'MARKDOWN',
                'HTML'
            )
        ),

    hotstring_trigger TEXT COLLATE NOCASE UNIQUE,

    is_favorite INTEGER NOT NULL DEFAULT 0
        CHECK (is_favorite IN (0, 1)),

    is_sensitive INTEGER NOT NULL DEFAULT 0
        CHECK (is_sensitive IN (0, 1)),

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
        ON DELETE SET NULL
);
```

---

# 89. `clipboard_history`

This feature is optional and should not be enabled merely because the table exists.

DDL:

```sql
CREATE TABLE clipboard_history (
    clipboard_history_id INTEGER PRIMARY KEY,

    content_text TEXT NOT NULL,

    content_hash TEXT,

    source_application TEXT,

    is_sensitive INTEGER NOT NULL DEFAULT 0
        CHECK (is_sensitive IN (0, 1)),

    captured_at TEXT NOT NULL,

    expires_at TEXT
);
```

---

# 90. Clipboard History Policy

Clipboard history should be:

```text
optional
configurable
clearable
retention-limited
sensitive-data aware
```

A later implementation may choose not to create this table until the clipboard-history feature becomes active.

It belongs to the target schema but not the initial migration slice.

---

# 91. Workspace Domain

Qt workspace persistence can use opaque state.

No relational decomposition is required merely because the GUI contains many panels.

---

# 92. `workspaces`

```sql
CREATE TABLE workspaces (
    workspace_id INTEGER PRIMARY KEY,

    workspace_code TEXT NOT NULL COLLATE NOCASE UNIQUE
        CHECK (length(trim(workspace_code)) > 0),

    name TEXT NOT NULL
        CHECK (length(trim(name)) > 0),

    description TEXT,

    is_default INTEGER NOT NULL DEFAULT 0
        CHECK (is_default IN (0, 1)),

    layout_state BLOB,
    geometry_state BLOB,

    settings_json TEXT,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

---

# 93. Workspace Default Constraint

At most one workspace may be the default.

```sql
CREATE UNIQUE INDEX ux_workspaces_one_default
    ON workspaces(is_default)
    WHERE is_default = 1;
```

The application may require at least one default once user-created workspaces exist.

---

# 94. Audit Domain

Audit records capture important actions.

They are not a replacement for application logs.

---

# 95. `audit_events`

```sql
CREATE TABLE audit_events (
    audit_event_id INTEGER PRIMARY KEY,

    event_type TEXT NOT NULL
        CHECK (length(trim(event_type)) > 0),

    entity_type TEXT,
    entity_id INTEGER,

    actor_type TEXT NOT NULL DEFAULT 'USER'
        CHECK (
            actor_type IN (
                'USER',
                'SYSTEM',
                'AI',
                'INTEGRATION'
            )
        ),

    actor_label TEXT,

    summary TEXT NOT NULL
        CHECK (length(trim(summary)) > 0),

    details_json TEXT,

    correlation_id TEXT,

    created_at TEXT NOT NULL
);
```

---

# 96. Audit Polymorphic Reference Exception

`entity_type + entity_id` is intentionally polymorphic.

SQLite cannot enforce a foreign key from one column to several possible entity tables.

This is a documented integrity exception.

Audit records preserve historical context even if the referenced application entity no longer exists.

---

# 97. Audit Event Examples

Potential event types:

```text
ticket.created
ticket.resolved
script.executed
diagnostic.completed
integration.connected
settings.changed
```

Do not audit every button click.

---

# 98. Indexing Strategy

Indexes should support real query patterns.

They should not be added merely because a column exists.

Primary goals:

```text
ticket queue
ticket context
recent activity
company/contact lookup
KB filtering
script library filtering
execution history
diagnostic session loading
search
audit investigation
```

---

# 99. Taxonomy Indexes

```sql
CREATE INDEX idx_categories_parent_category_id
    ON categories(parent_category_id);

CREATE INDEX idx_categories_scope_active_sort
    ON categories(
        scope,
        is_active,
        sort_order
    );
```

---

# 100. Company Indexes

```sql
CREATE INDEX idx_companies_name
    ON companies(name COLLATE NOCASE);

CREATE INDEX idx_companies_domain
    ON companies(domain);

CREATE INDEX idx_company_notes_company_created
    ON company_notes(
        company_id,
        created_at DESC
    );

CREATE INDEX idx_company_links_company_sort
    ON company_links(
        company_id,
        sort_order
    );
```

---

# 101. Contact Indexes

```sql
CREATE INDEX idx_contacts_company_name
    ON contacts(
        company_id,
        display_name COLLATE NOCASE
    );

CREATE INDEX idx_contacts_email
    ON contacts(email);
```

---

# 102. Ticket Indexes

```sql
CREATE INDEX idx_tickets_status_updated
    ON tickets(
        status,
        updated_at DESC
    );

CREATE INDEX idx_tickets_company_status
    ON tickets(
        company_id,
        status
    );

CREATE INDEX idx_tickets_contact_id
    ON tickets(contact_id);

CREATE INDEX idx_tickets_priority_status
    ON tickets(
        priority,
        status
    );

CREATE INDEX idx_tickets_category_id
    ON tickets(category_id);

CREATE INDEX idx_tickets_created_at
    ON tickets(created_at DESC);
```

---

# 103. Ticket Detail Indexes

```sql
CREATE INDEX idx_ticket_notes_ticket_created
    ON ticket_notes(
        ticket_id,
        created_at DESC
    );

CREATE INDEX idx_ticket_status_history_ticket_changed
    ON ticket_status_history(
        ticket_id,
        changed_at DESC
    );

CREATE INDEX idx_ticket_timeline_ticket_occurred
    ON ticket_timeline_events(
        ticket_id,
        occurred_at DESC
    );

CREATE INDEX idx_ticket_attachments_ticket_id
    ON ticket_attachments(ticket_id);

CREATE INDEX idx_ticket_relationships_related_ticket_id
    ON ticket_relationships(
        related_ticket_id
    );

CREATE INDEX idx_ticket_tags_tag_id
    ON ticket_tags(
        tag_id,
        ticket_id
    );
```

---

# 104. Knowledge Indexes

```sql
CREATE INDEX idx_knowledge_articles_status_updated
    ON knowledge_articles(
        status,
        updated_at DESC
    );

CREATE INDEX idx_knowledge_articles_category_status
    ON knowledge_articles(
        category_id,
        status
    );

CREATE INDEX idx_knowledge_versions_article_version
    ON knowledge_article_versions(
        knowledge_article_id,
        version_number DESC
    );

CREATE INDEX idx_knowledge_links_article_sort
    ON knowledge_article_links(
        knowledge_article_id,
        sort_order
    );

CREATE INDEX idx_knowledge_relationships_related_article
    ON knowledge_article_relationships(
        related_knowledge_article_id
    );

CREATE INDEX idx_ticket_knowledge_articles_article
    ON ticket_knowledge_articles(
        knowledge_article_id,
        ticket_id
    );

CREATE INDEX idx_knowledge_article_tags_tag_id
    ON knowledge_article_tags(
        tag_id,
        knowledge_article_id
    );
```

---

# 105. Script Indexes

```sql
CREATE INDEX idx_scripts_enabled_type
    ON scripts(
        is_enabled,
        script_type
    );

CREATE INDEX idx_scripts_name
    ON scripts(name COLLATE NOCASE);

CREATE INDEX idx_scripts_category_id
    ON scripts(category_id);

CREATE INDEX idx_script_executions_script_started
    ON script_executions(
        script_id,
        started_at DESC
    );

CREATE INDEX idx_script_executions_ticket_started
    ON script_executions(
        ticket_id,
        started_at DESC
    );

CREATE INDEX idx_script_executions_status_started
    ON script_executions(
        status,
        started_at DESC
    );

CREATE INDEX idx_script_tags_tag_id
    ON script_tags(
        tag_id,
        script_id
    );

CREATE INDEX idx_knowledge_article_scripts_script_id
    ON knowledge_article_scripts(
        script_id,
        knowledge_article_id
    );
```

---

# 106. Diagnostic Indexes

```sql
CREATE INDEX idx_diagnostic_workflows_status
    ON diagnostic_workflows(
        status,
        name COLLATE NOCASE
    );

CREATE INDEX idx_diagnostic_workflows_category
    ON diagnostic_workflows(category_id);

CREATE INDEX idx_diagnostic_steps_workflow_order
    ON diagnostic_steps(
        diagnostic_workflow_id,
        step_order
    );

CREATE UNIQUE INDEX ux_diagnostic_steps_one_entry
    ON diagnostic_steps(
        diagnostic_workflow_id
    )
    WHERE is_entry = 1;

CREATE INDEX idx_diagnostic_conditions_source_priority
    ON diagnostic_conditions(
        source_step_id,
        priority DESC
    );

CREATE INDEX idx_diagnostic_conditions_next_step
    ON diagnostic_conditions(next_step_id);

CREATE INDEX idx_diagnostic_sessions_workflow_status
    ON diagnostic_sessions(
        diagnostic_workflow_id,
        status
    );

CREATE INDEX idx_diagnostic_sessions_ticket_started
    ON diagnostic_sessions(
        ticket_id,
        started_at DESC
    );

CREATE INDEX idx_diagnostic_responses_session
    ON diagnostic_responses(
        diagnostic_session_id
    );

CREATE INDEX idx_diagnostic_results_session_created
    ON diagnostic_results(
        diagnostic_session_id,
        created_at
    );

CREATE INDEX idx_diagnostic_workflow_articles_article
    ON diagnostic_workflow_articles(
        knowledge_article_id,
        diagnostic_workflow_id
    );
```

---

# 107. Prompt Indexes

```sql
CREATE INDEX idx_prompt_templates_status_name
    ON prompt_templates(
        status,
        name COLLATE NOCASE
    );

CREATE INDEX idx_prompt_templates_category
    ON prompt_templates(category_id);
```

---

# 108. Clipboard Indexes

```sql
CREATE INDEX idx_clipboard_snippets_favorite
    ON clipboard_snippets(
        is_favorite,
        title COLLATE NOCASE
    );

CREATE INDEX idx_clipboard_snippets_category
    ON clipboard_snippets(category_id);

CREATE INDEX idx_clipboard_history_captured
    ON clipboard_history(
        captured_at DESC
    );

CREATE INDEX idx_clipboard_history_hash
    ON clipboard_history(content_hash);
```

---

# 109. Audit Indexes

```sql
CREATE INDEX idx_audit_events_entity_created
    ON audit_events(
        entity_type,
        entity_id,
        created_at DESC
    );

CREATE INDEX idx_audit_events_type_created
    ON audit_events(
        event_type,
        created_at DESC
    );

CREATE INDEX idx_audit_events_correlation
    ON audit_events(correlation_id);
```

---

# 110. Index Review Rule

Indexes must be reviewed after real repository queries exist.

Use:

```sql
EXPLAIN QUERY PLAN
```

to verify actual use.

An index that is never useful should be reconsidered.

---

# 111. Views

Views should simplify common stable projections.

They must not become a hidden business-logic layer.

Initial planned views:

```text
vw_ticket_summary
vw_knowledge_article_summary
vw_script_execution_summary
vw_diagnostic_session_summary
```

---

# 112. `vw_ticket_summary`

```sql
CREATE VIEW vw_ticket_summary AS
SELECT
    t.ticket_id,
    t.ticket_number,
    t.ticket_type,
    t.status,
    t.priority,
    t.subject,
    t.assigned_to,
    t.created_at,
    t.updated_at,
    t.resolved_at,
    t.closed_at,

    c.company_id,
    c.name AS company_name,

    ct.contact_id,
    ct.display_name AS contact_name,

    cat.category_id,
    cat.name AS category_name

FROM tickets AS t

LEFT JOIN companies AS c
    ON c.company_id = t.company_id

LEFT JOIN contacts AS ct
    ON ct.contact_id = t.contact_id

LEFT JOIN categories AS cat
    ON cat.category_id = t.category_id;
```

Use case:

```text
ticket queue
ticket search result
dashboard recent tickets
```

---

# 113. `vw_knowledge_article_summary`

```sql
CREATE VIEW vw_knowledge_article_summary AS
SELECT
    ka.knowledge_article_id,
    ka.article_code,
    ka.title,
    ka.summary,
    ka.status,
    ka.version_number,
    ka.updated_at,
    ka.published_at,

    cat.category_id,
    cat.name AS category_name

FROM knowledge_articles AS ka

LEFT JOIN categories AS cat
    ON cat.category_id = ka.category_id;
```

---

# 114. `vw_script_execution_summary`

```sql
CREATE VIEW vw_script_execution_summary AS
SELECT
    se.script_execution_id,
    se.status,
    se.started_at,
    se.completed_at,
    se.duration_ms,
    se.exit_code,
    se.result_message,
    se.error_summary,

    s.script_id,
    s.script_code,
    s.name AS script_name,
    s.script_type,
    s.risk_level,

    t.ticket_id,
    t.ticket_number

FROM script_executions AS se

JOIN scripts AS s
    ON s.script_id = se.script_id

LEFT JOIN tickets AS t
    ON t.ticket_id = se.ticket_id;
```

---

# 115. `vw_diagnostic_session_summary`

```sql
CREATE VIEW vw_diagnostic_session_summary AS
SELECT
    ds.diagnostic_session_id,
    ds.status,
    ds.started_at,
    ds.completed_at,
    ds.workflow_version_number,

    dw.diagnostic_workflow_id,
    dw.workflow_code,
    dw.name AS workflow_name,

    t.ticket_id,
    t.ticket_number

FROM diagnostic_sessions AS ds

JOIN diagnostic_workflows AS dw
    ON dw.diagnostic_workflow_id =
       ds.diagnostic_workflow_id

LEFT JOIN tickets AS t
    ON t.ticket_id = ds.ticket_id;
```

---

# 116. Trigger Policy

F7Hub should avoid placing ordinary business logic in database triggers.

Do not use triggers for:

```text
ticket status decisions
diagnostic branching
permissions
AI actions
workflow logic
PowerShell execution
```

Application services own those responsibilities.

---

# 117. Approved Trigger Use

The initial justified trigger use is:

```text
FTS5 synchronization
```

This is infrastructure behavior, not business behavior.

---

# 118. FTS5 Strategy

FTS5 should support:

```text
Knowledge Base
Tickets
Scripts
Prompt Templates
```

FTS tables are derived from relational source tables.

Search flow:

```text
User Query
    ↓
SearchService
    ↓
FTS5
    ↓
Rank
    ↓
Join relational source
    ↓
Unified Result
```

---

# 119. FTS5 Runtime Requirement

Before enabling the FTS migration, the application should verify FTS5 capability.

Failure should be reported clearly.

Core relational data must remain intact even if search infrastructure fails.

---

# 120. `knowledge_articles_fts`

```sql
CREATE VIRTUAL TABLE knowledge_articles_fts
USING fts5(
    title,
    summary,
    body_markdown,

    content = 'knowledge_articles',
    content_rowid = 'knowledge_article_id',

    tokenize = 'unicode61 remove_diacritics 2'
);
```

`unicode61` with diacritic normalization supports practical English/French technician searching.

---

# 121. Knowledge FTS Insert Trigger

```sql
CREATE TRIGGER knowledge_articles_ai
AFTER INSERT ON knowledge_articles
BEGIN
    INSERT INTO knowledge_articles_fts(
        rowid,
        title,
        summary,
        body_markdown
    )
    VALUES (
        new.knowledge_article_id,
        new.title,
        new.summary,
        new.body_markdown
    );
END;
```

---

# 122. Knowledge FTS Delete Trigger

```sql
CREATE TRIGGER knowledge_articles_ad
AFTER DELETE ON knowledge_articles
BEGIN
    INSERT INTO knowledge_articles_fts(
        knowledge_articles_fts,
        rowid,
        title,
        summary,
        body_markdown
    )
    VALUES (
        'delete',
        old.knowledge_article_id,
        old.title,
        old.summary,
        old.body_markdown
    );
END;
```

---

# 123. Knowledge FTS Update Trigger

```sql
CREATE TRIGGER knowledge_articles_au
AFTER UPDATE ON knowledge_articles
BEGIN
    INSERT INTO knowledge_articles_fts(
        knowledge_articles_fts,
        rowid,
        title,
        summary,
        body_markdown
    )
    VALUES (
        'delete',
        old.knowledge_article_id,
        old.title,
        old.summary,
        old.body_markdown
    );

    INSERT INTO knowledge_articles_fts(
        rowid,
        title,
        summary,
        body_markdown
    )
    VALUES (
        new.knowledge_article_id,
        new.title,
        new.summary,
        new.body_markdown
    );
END;
```

---

# 124. `tickets_fts`

```sql
CREATE VIRTUAL TABLE tickets_fts
USING fts5(
    ticket_number,
    subject,
    description,
    resolution,

    content = 'tickets',
    content_rowid = 'ticket_id',

    tokenize = 'unicode61 remove_diacritics 2'
);
```

Ticket notes are intentionally not duplicated into this FTS table yet.

If note search becomes important, either:

```text
create ticket_notes_fts
```

or implement a carefully designed aggregate search index.

Do not denormalize notes into `tickets` merely for search.

---

# 125. Ticket FTS Insert Trigger

```sql
CREATE TRIGGER tickets_ai
AFTER INSERT ON tickets
BEGIN
    INSERT INTO tickets_fts(
        rowid,
        ticket_number,
        subject,
        description,
        resolution
    )
    VALUES (
        new.ticket_id,
        new.ticket_number,
        new.subject,
        new.description,
        new.resolution
    );
END;
```

---

# 126. Ticket FTS Delete Trigger

```sql
CREATE TRIGGER tickets_ad
AFTER DELETE ON tickets
BEGIN
    INSERT INTO tickets_fts(
        tickets_fts,
        rowid,
        ticket_number,
        subject,
        description,
        resolution
    )
    VALUES (
        'delete',
        old.ticket_id,
        old.ticket_number,
        old.subject,
        old.description,
        old.resolution
    );
END;
```

---

# 127. Ticket FTS Update Trigger

```sql
CREATE TRIGGER tickets_au
AFTER UPDATE ON tickets
BEGIN
    INSERT INTO tickets_fts(
        tickets_fts,
        rowid,
        ticket_number,
        subject,
        description,
        resolution
    )
    VALUES (
        'delete',
        old.ticket_id,
        old.ticket_number,
        old.subject,
        old.description,
        old.resolution
    );

    INSERT INTO tickets_fts(
        rowid,
        ticket_number,
        subject,
        description,
        resolution
    )
    VALUES (
        new.ticket_id,
        new.ticket_number,
        new.subject,
        new.description,
        new.resolution
    );
END;
```

---

# 128. `scripts_fts`

```sql
CREATE VIRTUAL TABLE scripts_fts
USING fts5(
    name,
    description,
    relative_path,

    content = 'scripts',
    content_rowid = 'script_id',

    tokenize = 'unicode61 remove_diacritics 2'
);
```

---

# 129. Script FTS Triggers

```sql
CREATE TRIGGER scripts_ai
AFTER INSERT ON scripts
BEGIN
    INSERT INTO scripts_fts(
        rowid,
        name,
        description,
        relative_path
    )
    VALUES (
        new.script_id,
        new.name,
        new.description,
        new.relative_path
    );
END;
```

```sql
CREATE TRIGGER scripts_ad
AFTER DELETE ON scripts
BEGIN
    INSERT INTO scripts_fts(
        scripts_fts,
        rowid,
        name,
        description,
        relative_path
    )
    VALUES (
        'delete',
        old.script_id,
        old.name,
        old.description,
        old.relative_path
    );
END;
```

```sql
CREATE TRIGGER scripts_au
AFTER UPDATE ON scripts
BEGIN
    INSERT INTO scripts_fts(
        scripts_fts,
        rowid,
        name,
        description,
        relative_path
    )
    VALUES (
        'delete',
        old.script_id,
        old.name,
        old.description,
        old.relative_path
    );

    INSERT INTO scripts_fts(
        rowid,
        name,
        description,
        relative_path
    )
    VALUES (
        new.script_id,
        new.name,
        new.description,
        new.relative_path
    );
END;
```

---

# 130. `prompt_templates_fts`

```sql
CREATE VIRTUAL TABLE prompt_templates_fts
USING fts5(
    name,
    description,
    template_text,

    content = 'prompt_templates',
    content_rowid = 'prompt_template_id',

    tokenize = 'unicode61 remove_diacritics 2'
);
```

---

# 131. Prompt FTS Triggers

```sql
CREATE TRIGGER prompt_templates_ai
AFTER INSERT ON prompt_templates
BEGIN
    INSERT INTO prompt_templates_fts(
        rowid,
        name,
        description,
        template_text
    )
    VALUES (
        new.prompt_template_id,
        new.name,
        new.description,
        new.template_text
    );
END;
```

```sql
CREATE TRIGGER prompt_templates_ad
AFTER DELETE ON prompt_templates
BEGIN
    INSERT INTO prompt_templates_fts(
        prompt_templates_fts,
        rowid,
        name,
        description,
        template_text
    )
    VALUES (
        'delete',
        old.prompt_template_id,
        old.name,
        old.description,
        old.template_text
    );
END;
```

```sql
CREATE TRIGGER prompt_templates_au
AFTER UPDATE ON prompt_templates
BEGIN
    INSERT INTO prompt_templates_fts(
        prompt_templates_fts,
        rowid,
        name,
        description,
        template_text
    )
    VALUES (
        'delete',
        old.prompt_template_id,
        old.name,
        old.description,
        old.template_text
    );

    INSERT INTO prompt_templates_fts(
        rowid,
        name,
        description,
        template_text
    )
    VALUES (
        new.prompt_template_id,
        new.name,
        new.description,
        new.template_text
    );
END;
```

---

# 132. FTS Rebuild

After bulk import or FTS repair, external-content FTS tables may be rebuilt using their supported rebuild mechanism.

This should be exposed through controlled database maintenance tooling rather than routine application behavior.

Search indexes must always remain recoverable from relational source data.

---

# 133. Search Ranking

Initial ranking should use deterministic logic.

Potential signals:

```text
FTS bm25 score
exact identifier match
exact title match
prefix match
recency
entity type
favorite state
```

AI is not required to perform ordinary search.

---

# 134. Parameterized Queries

All application queries with dynamic values must use parameter binding.

Python:

```python
cursor.execute(
    """
    SELECT
        ticket_id,
        ticket_number,
        subject,
        status
    FROM tickets
    WHERE ticket_id = ?
    """,
    (ticket_id,)
)
```

Never:

```python
cursor.execute(
    f"SELECT * FROM tickets WHERE ticket_id = {ticket_id}"
)
```

---

# 135. Canonical Ticket Queue Query

Conceptual repository query:

```sql
SELECT
    ticket_id,
    ticket_number,
    ticket_type,
    status,
    priority,
    subject,
    company_name,
    contact_name,
    updated_at
FROM vw_ticket_summary
WHERE status <> 'CLOSED'
ORDER BY updated_at DESC
LIMIT ?
OFFSET ?;
```

---

# 136. Company Ticket Query

```sql
SELECT
    ticket_id,
    ticket_number,
    status,
    priority,
    subject,
    updated_at
FROM tickets
WHERE company_id = ?
ORDER BY updated_at DESC
LIMIT ?;
```

---

# 137. Ticket Notes Query

```sql
SELECT
    ticket_note_id,
    note_type,
    note_text,
    author_label,
    source,
    is_ai_generated,
    created_at,
    updated_at
FROM ticket_notes
WHERE ticket_id = ?
ORDER BY created_at ASC;
```

---

# 138. Ticket Timeline Query

```sql
SELECT
    ticket_timeline_event_id,
    event_type,
    title,
    details,
    metadata_json,
    actor_label,
    occurred_at
FROM ticket_timeline_events
WHERE ticket_id = ?
ORDER BY occurred_at DESC;
```

---

# 139. Knowledge Search Query

Conceptual:

```sql
SELECT
    ka.knowledge_article_id,
    ka.article_code,
    ka.title,
    ka.summary,
    ka.status,
    bm25(knowledge_articles_fts) AS rank
FROM knowledge_articles_fts
JOIN knowledge_articles AS ka
    ON ka.knowledge_article_id =
       knowledge_articles_fts.rowid
WHERE knowledge_articles_fts MATCH ?
  AND ka.status = 'PUBLISHED'
ORDER BY rank
LIMIT ?;
```

The query is parameterized.

However, FTS query syntax is still meaningful input.

`SearchService` should normalize or safely construct the FTS expression rather than blindly exposing advanced FTS syntax to ordinary search users.

---

# 140. Script Library Query

```sql
SELECT
    script_id,
    script_code,
    name,
    description,
    script_type,
    runtime,
    risk_level,
    privilege_level,
    relative_path
FROM scripts
WHERE is_enabled = 1
ORDER BY name COLLATE NOCASE;
```

---

# 141. Script Execution History Query

```sql
SELECT
    script_execution_id,
    script_name,
    script_type,
    status,
    started_at,
    completed_at,
    duration_ms,
    ticket_number,
    result_message
FROM vw_script_execution_summary
ORDER BY started_at DESC
LIMIT ?;
```

---

# 142. Diagnostic Session Query

```sql
SELECT
    diagnostic_session_id,
    workflow_code,
    workflow_name,
    status,
    started_at,
    completed_at,
    ticket_number
FROM vw_diagnostic_session_summary
ORDER BY started_at DESC
LIMIT ?;
```

---

# 143. Recent KB Query

```sql
SELECT
    knowledge_article_id,
    article_code,
    title,
    summary,
    updated_at
FROM knowledge_articles
WHERE status = 'PUBLISHED'
ORDER BY updated_at DESC
LIMIT ?;
```

---

# 144. Transaction Boundary: Ticket Creation

Creating a ticket may involve:

```text
tickets
ticket_status_history
ticket_timeline_events
```

Preferred transaction:

```text
BEGIN
↓
INSERT tickets
↓
INSERT initial ticket_status_history
↓
INSERT ticket_timeline_events
↓
COMMIT
```

If any mandatory part fails:

```text
ROLLBACK
```

---

# 145. Transaction Boundary: Add Ticket Note

Potential:

```text
BEGIN
↓
INSERT ticket_notes
↓
INSERT ticket_timeline_events
↓
UPDATE tickets.updated_at
↓
COMMIT
```

---

# 146. Transaction Boundary: Resolve Ticket

Potential:

```text
BEGIN
↓
Validate current state
↓
UPDATE tickets
    status = RESOLVED
    resolution = ...
    resolved_at = ...
↓
INSERT status history
↓
INSERT resolution note if required
↓
INSERT timeline event
↓
COMMIT
```

---

# 147. Transaction Boundary: Run Script

Database transaction should not remain open while PowerShell runs.

Wrong:

```text
BEGIN SQLite transaction
↓
Start PowerShell
↓
Wait 90 seconds
↓
Commit
```

Preferred:

```text
Record QUEUED/RUNNING state
↓
Commit
↓
Execute PowerShell outside DB transaction
↓
Validate result
↓
Short DB transaction
↓
Record completed execution
```

This prevents unnecessarily long SQLite locks.

---

# 148. Transaction Boundary: Diagnostic Step

A diagnostic script step may flow:

```text
Persist current response
↓
Commit
↓
Run PowerShell
↓
Validate structured result
↓
BEGIN
↓
Insert script execution result
↓
Insert diagnostic result
↓
Update current step
↓
COMMIT
```

---

# 149. Seed Data Philosophy

Seed data should be minimal.

Do not seed hundreds of:

- companies
- tickets
- categories
- scripts
- KB articles

into production databases merely for convenience.

Separate:

```text
required baseline data
```

from:

```text
development/demo fixtures
```

---

# 150. Production Seed Data

Potential initial production seed data may include:

```text
default categories
default workspace
application metadata
```

Only add these once actual defaults are approved.

---

# 151. Test Seed Data

Synthetic fixtures belong under:

```text
Tests\Fixtures\
```

or:

```text
Data\Samples\
```

where appropriate.

Never use real customer data in committed seed files.

---

# 152. Migration Sequence

Recommended planned migration sequence:

```text
0001_core.sql
0002_taxonomy.sql
0003_companies_contacts.sql
0004_tickets.sql
0005_knowledge.sql
0006_scripts.sql
0007_diagnostics.sql
0008_prompts_clipboard.sql
0009_workspaces_audit.sql
0010_fts.sql
```

This is a recommended logical sequence.

Do not create all ten immediately just because they appear here.

---

# 153. Planned Domain Migration Sequence

After the migration runner and its isolated tests are working, domain migrations should be introduced one independently tested slice at a time.

The planned sequence begins:

```text
0001_core.sql
0002_taxonomy.sql
0003_companies_contacts.sql
0004_tickets.sql
0005_knowledge.sql
```

This list is a dependency map, not the scope of the first coding task. The first completed task was limited to the bootstrap and migration infrastructure defined in Section 202.

---

# 154. Why FTS Is Later

FTS should be introduced after relational source entities work correctly.

Sequence:

```text
Relational records
↓
Repository tests
↓
Search requirements
↓
FTS5 migration
↓
SearchService
↓
Search tests
```

Search infrastructure must not complicate the first ticket persistence slice.

---

# 155. Why Diagnostics Are Later

Diagnostics depend on:

```text
tickets
knowledge
scripts
PowerShell execution
```

Therefore:

```text
diagnostic tables
```

should not be part of the first persistence milestone.

---

# 156. Repository Mapping

Suggested repository ownership:

| Table Group | Repository |
|---|---|
| `companies`, `company_notes`, `company_links` | `CompanyRepository` |
| `contacts` | `ContactRepository` |
| `tickets`, notes, status, timeline, attachments, relationships | `TicketRepository` |
| `knowledge_*` | `KnowledgeRepository` |
| `scripts`, parameters, executions | `ScriptRepository` |
| `diagnostic_*` | `DiagnosticRepository` |
| `prompt_*` | `PromptRepository` |
| `clipboard_*` | `ClipboardRepository` |
| `workspaces` | `WorkspaceRepository` |
| `audit_events` | `AuditRepository` |

This is conceptual ownership.

Do not create repositories mechanically until their application use cases require them.

---

# 157. Repository Return Values

Repositories should return structured Python values such as:

```text
domain entities
dataclasses
DTOs
specific projections
```

Avoid returning raw SQLite cursors to GUI code.

---

# 158. Database Connection Ownership

Database connection management belongs to Python infrastructure.

Potential component:

```text
DatabaseManager
```

Responsibilities:

```text
open connection
set PRAGMAs
verify database
run migrations
manage transaction helpers
close cleanly
```

---

# 159. Threading

Do not casually share SQLite connection objects between PySide6 worker threads.

Connection ownership must be explicit.

Potential baseline:

```text
main-thread operations
→ main connection

background DB worker
→ worker-owned connection
```

The final strategy should be validated during implementation.

---

# 160. Database Location

Development example:

```text
C:\Dev\F7Hub\Database\Dev\f7hub_dev.db
```

Installed runtime preferred direction:

```text
%LOCALAPPDATA%\F7Hub\Data\f7hub.db
```

The production application must not assume:

```text
C:\Dev\F7Hub\
```

exists.

---

# 161. Test Database

Tests should not use the development database.

Preferred:

```text
temporary database
```

or:

```text
isolated f7hub_test.db
```

created specifically for a test run.

---

# 162. Database Test Categories

Required database tests eventually include:

```text
bootstrap
migration
foreign key
constraint
repository
transaction
query
FTS
backup / restore
failure path
```

---

# 163. Bootstrap Tests

Examples:

```text
empty path
→ DB created

foreign_keys
→ enabled

migration table
→ initialized

current migrations
→ applied exactly once
```

---

# 164. Migration Tests

Test:

```text
empty DB
→ latest expected schema

partially migrated DB
→ latest schema

already current DB
→ no-op

changed historical checksum
→ failure

invalid migration
→ rollback

failed migration
→ not recorded as applied
```

The isolated infrastructure suite verified these cases on 2026-09-03, including DDL/DML rollback, denial of migration-authored transaction control, missing applied files, duplicate versions, malformed filenames, numeric ordering and unchanged/changed checksum behavior.

---

# 165. Constraint Tests

Test examples:

```text
ticket without subject
→ rejected

invalid ticket status
→ rejected

attachment with negative size
→ rejected

ticket linked to itself
→ rejected

KB article linked to itself
→ rejected

duplicate tag link
→ rejected

second default workspace
→ rejected
```

---

# 166. Foreign Key Tests

Examples:

```text
ticket note for nonexistent ticket
→ rejected

delete ticket
→ notes cascade

delete company
→ ticket survives with company_id NULL

delete script with execution history
→ rejected

delete diagnostic workflow with session history
→ rejected
```

---

# 167. Transaction Tests

Test that multi-write workflows leave no partial state.

Example:

```text
ticket created
+
status history fails
```

Expected:

```text
ticket creation transaction rolls back
```

---

# 168. FTS Tests

Test:

```text
insert article
→ searchable

update article
→ old text disappears
→ new text appears

delete article
→ removed from FTS

rebuild FTS
→ same searchable records

French accented text
→ expected normalized search behavior
```

---

# 169. Query Plan Tests

High-frequency queries should be inspected with:

```sql
EXPLAIN QUERY PLAN
```

Initial candidates:

```text
ticket queue
company ticket list
ticket timeline
KB search
script execution history
diagnostic session history
```

Do not assert an index improves performance without measuring the plan.

---

# 170. Backup Requirements

Before destructive schema work:

```text
backup
↓
migration
↓
integrity validation
```

The application should eventually provide controlled backup and restore operations.

---

# 171. Database File Backup

SQLite backup should account for the journal mode actually in use.

Do not implement naive file-copy backup while assuming no active transactions.

Use a SQLite-aware backup strategy when runtime backup functionality is implemented.

---

# 172. Data Integrity Priority

When application convenience conflicts with persistent integrity:

```text
persistent integrity wins
```

Do not disable constraints to make an operation easier.

---

# 173. Application Validation vs DB Constraints

Use defense in depth.

Example:

```text
GUI
→ immediate friendly validation

Service
→ workflow validation

Repository
→ safe persistence mapping

SQLite
→ final data-integrity constraints
```

---

# 174. Scope Validation for Categories

The schema allows:

```text
tickets.category_id
→ categories.category_id
```

but it cannot directly enforce:

```text
category.scope = 'TICKET'
```

without unnecessary trigger complexity.

The service layer must validate the scope.

Equivalent rules apply to:

```text
knowledge article
script
prompt
clipboard snippet
diagnostic workflow
```

Tests are required.

---

# 175. Diagnostic Cross-Reference Validation

The application must validate:

- session current step belongs to session workflow
- condition next step belongs to same workflow
- response step belongs to session workflow
- script step has a valid script
- non-script step does not improperly require script execution
- active workflow has exactly one entry step

These are domain invariants.

They do not all need SQL triggers.

---

# 176. No Business Logic Triggers

Do not implement triggers such as:

```text
if ticket closes then automatically invoke script
if diagnostic fails then create ticket
if KB article changes then call AI
```

Those belong in services.

---

# 177. Generated Columns

No generated columns are required in the baseline schema.

They may be introduced later for demonstrated query or integrity benefits.

Do not add generated columns merely because SQLite supports them.

---

# 178. STRICT Tables

SQLite `STRICT` tables are not part of the baseline DDL yet.

Before adopting them:

```text
select minimum supported SQLite version
verify Python runtime
verify migrations
verify test environment
```

If later approved, STRICT mode should be introduced deliberately and documented.

---

# 179. Views vs Repository Queries

Use a view when the projection:

- is stable
- is reused
- improves clarity
- does not hide complex business decisions

Use repository SQL when the query:

- belongs to one use case
- has dynamic filtering
- changes frequently
- requires application-controlled composition

---

# 180. FTS vs Normal Index

Use FTS5 for:

```text
natural-language text search
```

Use B-tree indexes for:

```text
status
IDs
dates
company
priority
category
exact values
```

Do not use FTS5 as a substitute for normal relational filtering.

---

# 181. Universal Search

Universal search is composed at the Python service level.

Conceptually:

```text
SearchService
    ├── TicketSearchProvider
    ├── CompanySearchProvider
    ├── ContactSearchProvider
    ├── KnowledgeSearchProvider
    ├── ScriptSearchProvider
    └── PromptSearchProvider
```

No giant universal-search table is required initially.

---

# 182. Search Result Identity

A normalized Python search result may include:

```text
entity_type
entity_id
title
summary
score
action
```

This is an application-level projection.

It does not require a relational `search_results` table.

---

# 183. Derived Data

Do not persist derived data unless necessary.

Examples:

```text
ticket age
→ calculate

number of company tickets
→ query/count

FTS index
→ derived

script result display formatting
→ derive from structured result
```

---

# 184. Counters

Do not store:

```text
companies.open_ticket_count
```

unless performance evidence later justifies denormalization.

Initial query:

```sql
SELECT COUNT(*)
FROM tickets
WHERE company_id = ?
  AND status NOT IN ('RESOLVED', 'CLOSED', 'CANCELLED');
```

---

# 185. Denormalization Rule

Before denormalizing:

1. identify actual performance issue
2. capture query plan
3. measure
4. document derived value
5. define synchronization strategy
6. test consistency

No speculative denormalization.

---

# 186. External Integrations

External integration persistence is deliberately deferred.

Potential future needs:

```text
provider connection metadata
external entity mappings
sync cursors
sync history
provider-specific cache
```

These should be designed from actual:

```text
HaloPSA
NinjaOne
Microsoft Graph
or other provider
```

requirements.

---

# 187. Microsoft Graph Data

Do not replicate the entire Microsoft tenant into SQLite by default.

Store only information needed for F7Hub workflows.

External systems remain authoritative for their own objects.

---

# 188. AI Data

Do not automatically persist every AI request/response.

If AI history later becomes a requirement, design it explicitly with:

- privacy
- retention
- context
- provider metadata
- model metadata
- redaction

Do not overload `audit_events` or `prompt_templates` to become AI history tables.

---

# 189. Secrets

Never store ordinary secrets in this schema.

Examples:

```text
password
API key
OAuth refresh token
private key
client secret
```

unless a future dedicated encrypted secret architecture is approved.

The database should not become a plaintext credential vault.

---

# 190. Sensitive Ticket Data

Ticket and contact data may contain sensitive information.

Design principles:

```text
collect only what is useful
avoid duplicate copies
avoid unnecessary logging
control exports
protect backups
```

---

# 191. SQL Naming Standard

All SQLite identifiers use:

```text
snake_case
```

Examples:

```text
tickets
ticket_id
created_at
ticket_status_history
idx_tickets_status_updated
vw_ticket_summary
```

---

# 192. Table Naming

Entity tables use plural nouns:

```text
tickets
companies
contacts
scripts
```

Junction tables combine related entities:

```text
ticket_tags
knowledge_article_tags
ticket_knowledge_articles
```

---

# 193. Index Naming

Normal index:

```text
idx_<table>_<purpose>
```

Example:

```text
idx_tickets_status_updated
```

Unique index:

```text
ux_<table>_<purpose>
```

Example:

```text
ux_workspaces_one_default
```

---

# 194. View Naming

Views use:

```text
vw_<purpose>
```

Examples:

```text
vw_ticket_summary
vw_script_execution_summary
```

---

# 195. Trigger Naming

Triggers use names reflecting table/event.

FTS examples:

```text
tickets_ai
tickets_ad
tickets_au
```

Where:

```text
ai
→ after insert

ad
→ after delete

au
→ after update
```

These short suffixes are acceptable for the tightly standardized FTS synchronization pattern.

---

# 196. Migration Naming

```text
0001_core.sql
0002_taxonomy.sql
0003_companies_contacts.sql
```

Do not use:

```text
new.sql
fix.sql
final.sql
schema2.sql
```

---

# 197. SQL Formatting

DDL should use:

```text
UPPERCASE SQL keywords
snake_case identifiers
one constraint per readable block
explicit FK actions
```

Readability is more important than minimizing line count.

---

# 198. Schema Change Procedure

Before changing the physical schema:

```text
Requirement
↓
Inspect existing schema
↓
Review 07
↓
Review 08
↓
Update 09
↓
Design migration
↓
Implement migration
↓
Update repositories
↓
Tests
↓
ChangeLog
```

---

# 199. Breaking Schema Changes

Examples:

```text
rename column
change key
split table
merge table
change relationship cardinality
change nullability on existing populated field
delete column
```

These require deliberate migration planning.

---

# 200. SQLite Rename / Rebuild Awareness

Some SQLite structural changes may require table rebuild workflows.

Do not casually generate:

```sql
ALTER TABLE ...
```

without validating SQLite support and existing data implications.

Migration tests must use realistic pre-migration data.

---

# 201. Destructive Migration Review

Review is mandatory before:

- dropping a table
- dropping populated columns
- changing PK structure
- replacing key relationships
- changing delete behavior
- destroying historical data

Backup strategy must be defined.

---

# 202. First Database Implementation Objective

The first coding objective after documentation review should be:

> Implement the SQLite bootstrap and migration infrastructure.

Scope:

```text
Database connection
PRAGMA foreign_keys
PRAGMA busy_timeout
migration table
migration discovery
migration ordering
checksum validation
transactional migration
tests
```

Out of scope:

```text
AI
Plugins
PowerShell execution
Diagnostics
Full GUI
All 39 target relational tables
```

Status as of 2026-09-03:

```text
VERIFIED — 28 isolated database infrastructure tests passed
```

No business-domain migration was created by this objective.

---

# 203. Second Database Objective

After migration infrastructure:

> Implement taxonomy, companies, and contacts.

Includes:

```text
categories
tags
companies
company_notes
company_links
contacts
```

However, only create supporting company tables if the first real workflow needs them.

---

# 204. Third Database Objective

Then implement the ticket persistence slice:

```text
tickets
ticket_notes
ticket_status_history
ticket_timeline_events
```

Attachments, relationships, and tagging may be added as the ticket workflow expands.

```text
Status: VERIFIED — 0004_tickets.sql — 2026-09-03 — 10 focused tests; 79 full database tests
```

---

# 205. First End-to-End Persistence Slice

The first architectural proof should be:

```text
PySide6 Ticket Form
        ↓
TicketService
        ↓
TicketRepository
        ↓
SQLite
        ↓
Ticket persisted
        ↓
Application restart
        ↓
Ticket still available
```

This proves the architectural spine.

---

# 206. Database Definition of Done

A database slice is not complete until applicable:

```text
[ ] Requirement exists
[ ] ERD relationship reviewed
[ ] SQL schema updated
[ ] Migration created
[ ] Migration tested
[ ] Foreign keys tested
[ ] Constraints tested
[ ] Repository implemented
[ ] Repository tests pass
[ ] Failure paths tested
[ ] Query plan reviewed where relevant
[ ] Documentation synchronized
[ ] ChangeLog updated when meaningful
```

---

# 207. Schema Test Status Vocabulary

Use:

```text
PASS
FAIL
NOT RUN
BLOCKED
```

Never claim a migration or constraint works merely because the SQL looks correct.

---

# 208. Schema Anti-Patterns

Avoid:

## Arbitrary Table Count

```text
"We need 100 tables."
```

## Lookup Table Explosion

Creating separate tables for every tiny static enum.

## JSON Blob Database

Putting entire relational domains into JSON.

## Giant Universal Table

Trying to store tickets, KB, prompts, scripts, and diagnostics in one generic entity table.

## Direct GUI SQL

PySide6 widgets executing raw SQL.

## Direct AHK SQL

AHK modifying application tables.

## Direct PowerShell SQL

Administrative scripts writing application state directly.

## Silent Cascades Everywhere

Using `ON DELETE CASCADE` without ownership analysis.

## Index Everything

Creating an index on every column.

## Trigger Business Logic

Hiding workflow behavior in SQLite triggers.

## Credentials in SQLite

Using normal tables as a password/token vault.

## Production Data in Tests

Committing customer information as fixtures.

---

# 209. Schema Review Questions

Before approving a table:

1. What requirement requires it?
2. What domain owns it?
3. Does an existing table already model this concept?
4. Is the table normalized appropriately?
5. What is its primary key?
6. What relationships exist?
7. Which relationships are mandatory?
8. What should happen on delete?
9. Which values need database constraints?
10. Which fields are nullable?
11. What are the primary queries?
12. Which indexes support those queries?
13. Does it need FTS?
14. Does it really need JSON?
15. Does it contain sensitive data?
16. How is it migrated?
17. How is it tested?
18. Which repository owns it?

---

# 210. Current Target Schema Summary

The target schema currently contains these principal relational areas:

```text
Core
    schema_migrations
    application_metadata

Taxonomy
    categories
    tags

Companies
    companies
    company_notes
    company_links
    contacts

Tickets
    tickets
    ticket_notes
    ticket_status_history
    ticket_timeline_events
    ticket_attachments
    ticket_relationships
    ticket_tags

Knowledge
    knowledge_articles
    knowledge_article_versions
    knowledge_article_links
    knowledge_article_relationships
    ticket_knowledge_articles
    knowledge_article_tags
    knowledge_article_scripts

Automation
    scripts
    script_parameters
    script_executions
    script_tags

Diagnostics
    diagnostic_workflows
    diagnostic_steps
    diagnostic_conditions
    diagnostic_sessions
    diagnostic_responses
    diagnostic_results
    diagnostic_workflow_articles

Prompts
    prompt_templates
    prompt_variables

Clipboard
    clipboard_snippets
    clipboard_history

Workspaces
    workspaces

Audit
    audit_events
```

Search infrastructure:

```text
knowledge_articles_fts
tickets_fts
scripts_fts
prompt_templates_fts
```

Initial views:

```text
vw_ticket_summary
vw_knowledge_article_summary
vw_script_execution_summary
vw_diagnostic_session_summary
```

---

# 211. Initial Implementation Does Not Equal Target Schema

The target schema is a design map.

Implementation should remain sliced.

Initial implementation:

```text
Core
↓
Taxonomy
↓
Companies / Contacts
↓
Ticket Core
```

Later:

```text
Knowledge
↓
Search
↓
Scripts
↓
Diagnostics
↓
Prompts / Clipboard
↓
Workspace / Audit
```

---

# 212. Schema Synchronization Requirements

Database architecture change:

```text
07_Database.md
08_ERD.md
09_SQLSchema.md
```

Python persistence change:

```text
13_PythonArchitecture.md
```

Naming change:

```text
15_NamingConventions.md
```

Major implementation:

```text
18_ChangeLog.md
```

Current task:

```text
17_Todo.md
```

---

# 213. Final Database Architecture

The physical architecture is:

```text
PySide6 GUI
    ↓
Application Services
    ↓
Domain Validation
    ↓
Repositories
    ↓
SQLite
    │
    ├── Relational Tables
    ├── Constraints
    ├── Indexes
    ├── Views
    └── FTS5
```

PowerShell:

```text
PowerShell Script
    ↓
Structured Result
    ↓
Python Service
    ↓
Repository
    ↓
SQLite
```

AutoHotkey:

```text
AHK Action
    ↓
F7Hub Command
    ↓
Python
    ↓
Service
    ↓
Repository if persistence is required
```

---

# 214. Final Principle

The SQL schema should be strict enough to protect F7Hub data, simple enough to understand, and flexible enough to evolve through migrations.

The governing rule is:

> Model real technician workflows as normalized relational data, enforce integrity at the lowest appropriate layer, keep business logic out of SQLite triggers, and evolve the schema through small tested migrations rather than attempting to create the entire future database at once.
