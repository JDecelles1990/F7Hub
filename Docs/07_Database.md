# F7Hub Database Architecture

> Document: `Docs/07_Database.md`  
> Project: F7Hub  
> Purpose: Define the database architecture, rules, domains, integrity requirements, migration strategy, indexing principles, search strategy, audit expectations and repository boundaries for F7Hub.  
> Scope: SQLite database design principles and persistent-data architecture.  
> Related Documents: `02_ProductRequirements.md`, `06_SystemArchitecture.md`, `08_ERD.md`, `09_SQLSchema.md`, `13_PythonArchitecture.md`

---

# 1. Purpose

Verified application relationship boundary — Slice 012 (2026-09-07): TicketKnowledgeRepository uses the existing ticket_knowledge_articles table for RELATED-only links. A single BEGIN IMMEDIATE transaction verifies both entities and duplicate state, inserts and reloads joined metadata before commit. Failure rolls back; the composite PK prevents duplicates and existing ON DELETE CASCADE keys remove links when either entity is deleted. Candidate and linked-list reads return current code/title/status/version without article bodies. This use case writes no ticket activity fields/events. Five historical migrations and the physical schema remain unchanged; isolated integrity_check = ok and foreign_key_check = zero violations. Full validation counts are in Status/CURRENT_STATE.md.

Verified application unlink boundary — Slice 013 (2026-09-07): the same repository removes one row with ticket_id = ?, knowledge_article_id = ? and relationship_type = 'RELATED'. BEGIN IMMEDIATE precedes ticket, article and relationship checks. DELETE must affect exactly one row before commit; zero yields not-linked, unexpected counts and failures roll back. Both parent entities, other RELATED rows, synthetic APPLIED/RESOLUTION_SOURCE rows and all ticket activity remain unchanged. Independent service operations racing to unlink yield one success and one safe not-linked result. Candidate reads naturally expose the unlinked article for relinking. No physical schema change or new migration; five historical migrations remain unchanged. Isolated integrity_check = ok and foreign_key_check = zero violations after unlink.

SQLite is the primary persistent data store for F7Hub.

This document defines:

- database responsibilities
- database boundaries
- domain organization
- normalization rules
- key strategy
- relationships
- constraints
- indexing
- migrations
- transactions
- FTS5
- auditing
- backups
- data retention
- repository access
- testing requirements
- schema governance

This document answers:

> How should persistent F7Hub data be designed and managed?

Exact entities and relationships belong in:

- `08_ERD.md`

Exact SQL implementation belongs in:

- `09_SQLSchema.md`

---

# 2. Database Role

SQLite stores structured persistent application state.

Examples include:

- tickets
- ticket notes
- ticket history
- companies
- contacts
- knowledge articles
- tags
- script metadata
- diagnostic workflows
- diagnostic sessions
- script execution history
- prompts
- bookmarks
- settings
- saved workspaces
- search metadata
- audit information

SQLite should not become a dumping ground for every file used by F7Hub.

---

# 3. Database Technology

Primary database:

```text
SQLite
```

SQLite is appropriate for the initial F7Hub architecture because F7Hub is:

- local-first
- primarily single-user
- desktop-based
- portable
- modular
- expected to operate without a database server
- expected to support reliable transactional storage

A server database should not be introduced without a demonstrated requirement.

---

# 4. Database Architecture

Preferred data flow:

```text
PySide6 GUI
    │
    ▼
Application Services
    │
    ▼
Repositories
    │
    ▼
SQLite
```

The GUI must not issue raw SQL directly.

Application services should not normally contain SQL.

Repositories own persistent database access.

---

# 5. Database Source of Truth

Database responsibilities are separated across three documents.

```text
07_Database.md
→ Database architecture, policies and rules

08_ERD.md
→ Entities and relationships

09_SQLSchema.md
→ Tables, columns, keys, constraints, indexes and SQL
```

This separation prevents the same schema definition from being maintained in multiple places.

---

# 6. Core Database Principles

F7Hub database development must preserve:

1. data integrity
2. clear entity ownership
3. normalization
4. explicit relationships
5. safe migrations
6. transactional consistency
7. predictable query behavior
8. appropriate indexing
9. controlled full-text search
10. auditability where justified
11. recoverability
12. testability

---

# 7. Database Domain Strategy

The schema should be organized conceptually by business domain rather than as an arbitrary collection of tables.

Potential domains include:

```text
Core
Identity / Contacts
Companies
Tickets
Knowledge
Automation
Diagnostics
Search
Prompts
Clipboard
Configuration
Workspaces
Reporting
Audit
Integrations
Plugins
```

Domains are conceptual groupings.

SQLite does not provide schemas in the same way as enterprise database systems, so naming and documentation must preserve domain clarity.

---

# 8. Planned Database Domains

The planned relational domains are:

```text
Core
Taxonomy
Companies / Contacts
Tickets
Knowledge
Automation
Diagnostics
Prompts
Clipboard
Workspaces
Audit
```

Search uses derived FTS5 infrastructure over selected relational source tables.

The exact table inventory belongs to `09_SQLSchema.md`. In particular:

- shared `categories` and `tags` belong to Taxonomy rather than being duplicated per feature
- `application_metadata` belongs to Core
- `workspaces` is the only baseline workspace table
- `workspace_panels` is deferred unless queryable panel-level state is required
- external mapping tables are deferred until a real provider integration supplies concrete requirements
- secrets are not stored as ordinary database settings
- clipboard history remains optional and privacy-aware

Conceptual relationships belong to `08_ERD.md`; this document owns the governing database rules rather than a competing entity inventory.

---

# 9. Table Creation Rule

Do not create a table merely because it may be useful someday.

Before creating a table:

```text
SEARCH
   ↓
IDENTIFY EXISTING ENTITY
   ↓
REUSE OR EXTEND
   ↓
CREATE ONLY IF NECESSARY
```

Every table must have:

- a clear purpose
- an owning domain
- a reason to persist
- defined relationships
- defined lifecycle
- expected query patterns

---

# 10. No Table-Count Target

F7Hub may eventually contain many tables.

However:

> The number of tables is not a product objective.

Do not create approximately 100 tables merely to reach a planned number.

The correct number is whatever the normalized domain model requires.

A schema with 60 well-designed tables is better than 100 speculative ones.

---

# 11. Normalization Strategy

F7Hub should normally target:

```text
Third Normal Form (3NF)
```

General expectations:

- one concept per table
- eliminate repeating groups
- avoid duplicated facts
- separate many-to-many relationships
- avoid storing multiple values in one field
- avoid derived data unless justified
- avoid duplicated descriptive data across records

---

# 12. First Normal Form

Tables should satisfy 1NF.

Requirements:

- atomic values
- no repeating column groups
- each row uniquely identifiable

Avoid:

```text
phone1
phone2
phone3
```

Prefer a related table if multiple phone numbers are a real domain requirement.

---

# 13. Second Normal Form

Tables should satisfy 2NF.

Non-key attributes must depend on the complete key.

This is especially important in junction tables and composite-key designs.

---

# 14. Third Normal Form

Tables should satisfy 3NF.

Non-key fields should depend on:

> the key, the whole key, and nothing but the key.

Example of undesirable duplication:

```text
tickets
--------------------------------
ticket_id
company_id
company_name
company_phone
```

Company attributes belong in the company domain.

The ticket should reference the company.

---

# 15. Denormalization

Denormalization is allowed only when there is a documented benefit.

Examples may include:

- expensive reporting
- search optimization
- immutable historical snapshot
- measured query bottleneck

Before denormalizing, document:

- reason
- source of truth
- synchronization mechanism
- consistency risk
- performance evidence

---

# 16. Primary Keys

Every persistent entity should have a stable primary key.

Preferred pattern:

```text
INTEGER PRIMARY KEY
```

for internal SQLite entities unless another strategy is justified.

Example:

```sql
ticket_id INTEGER PRIMARY KEY
```

SQLite integer primary keys are efficient and appropriate for local relational entities.

---

# 17. External Identifiers

External system identifiers must remain separate from F7Hub primary keys.

Example:

```text
ticket_id
→ F7Hub internal identifier

external_ticket_id
→ HaloPSA identifier
```

Do not make external provider IDs the core identity of F7Hub entities unless explicitly justified.

This prevents provider coupling.

---

# 18. UUIDs

UUIDs may be used where they provide a real benefit, such as:

- synchronization
- distributed generation
- plugin interoperability
- portable exports

They should not automatically replace SQLite integer primary keys.

Use the simplest identity strategy appropriate to the domain.

---

# 19. Foreign Keys

Foreign keys are mandatory for relational integrity where relationships exist.

Foreign key enforcement must be enabled:

```sql
PRAGMA foreign_keys = ON;
```

F7Hub must not rely only on application code to preserve relationships.

---

# 20. Foreign Key Actions

Foreign-key actions must be chosen intentionally.

Common options:

```text
RESTRICT
NO ACTION
CASCADE
SET NULL
```

Do not use `ON DELETE CASCADE` automatically.

Cascade deletion is appropriate only when the child record has no independent value outside its parent.

---

# 21. Delete Philosophy

F7Hub should avoid silent destructive deletion.

Depending on the domain, records may use:

- hard deletion
- soft deletion
- archived state
- inactive state
- deprecated state

Examples:

A temporary search record may be safely deleted.

A knowledge article may instead become:

```text
ARCHIVED
```

A script may become:

```text
DISABLED
```

A ticket may remain historically preserved.

---

# 22. Constraints

Important domain rules should be enforced at the database level where appropriate.

Use:

- `NOT NULL`
- `UNIQUE`
- `CHECK`
- foreign keys
- defaults

Example:

```sql
CHECK (status IN ('NEW', 'OPEN', 'IN_PROGRESS', 'WAITING', 'RESOLVED', 'CLOSED', 'CANCELLED'))
```

However, frequently changing business rules may belong in domain logic rather than rigid SQL constraints.

---

# 23. NULL Strategy

`NULL` should mean:

> unknown, unavailable or not applicable

It should not be used inconsistently to represent:

- empty string
- zero
- false
- missing relationship
- deleted state

Columns should use `NOT NULL` when missing values are not valid.

---

# 24. Boolean Values

SQLite has no dedicated Boolean storage class.

Boolean values should normally use:

```text
0 = false
1 = true
```

with constraints where appropriate:

```sql
CHECK (is_active IN (0, 1))
```

---

# 25. Date and Time Strategy

Date/time storage must be consistent across the schema.

Preferred storage:

```text
ISO 8601
```

Example:

```text
2026-09-02T12:25:00-04:00
```

or an approved UTC convention.

The exact project-wide date/time convention must be standardized in `15_NamingConventions.md` and `09_SQLSchema.md`.

Do not mix arbitrary date formats.

---

# 26. Created and Updated Timestamps

Persistent business entities should include lifecycle timestamps where useful.

Typical fields:

```text
created_at
updated_at
```

Not every junction table requires both.

Add fields based on actual audit and operational value.

---

# 27. Naming Conventions

Database naming conventions should use predictable lowercase snake_case.

Examples:

```text
tickets
ticket_notes
knowledge_articles
script_executions
diagnostic_sessions
```

Columns:

```text
ticket_id
company_id
created_at
is_active
```

Final naming rules belong in:

`15_NamingConventions.md`

---

# 28. Junction Tables

Many-to-many relationships should use explicit junction tables.

Example:

```text
knowledge_articles
        │
        │ many
        ▼
knowledge_article_tags
        ▲
        │ many
        │
      tags
```

A junction table should normally contain foreign keys to both parent entities.

Additional relationship metadata may be stored when required.

---

# 29. Tags

Tags should normally be normalized rather than stored as comma-separated strings.

Avoid:

```text
tags = "outlook,email,m365"
```

Prefer:

```text
tags
knowledge_article_tags
ticket_tags
script_tags
```

if tagging is a real cross-domain requirement.

---

# 30. Categories vs Tags

Categories and tags serve different purposes.

Categories:

- hierarchical or controlled
- usually one or few per object

Tags:

- flexible
- many-to-many
- descriptive

Do not create separate tag systems for each subsystem unless domain behavior genuinely differs.

Reuse shared taxonomy infrastructure where appropriate.

---

# 31. Script Storage Strategy

PowerShell, AutoHotkey and Python scripts should normally remain files.

Example:

```text
PowerShell\
AutoHotkey\
Python\
```

SQLite may store:

- script ID
- relative path
- title
- description
- language
- category
- tags
- version
- privilege requirement
- risk
- execution metadata

This preserves:

- Git history
- syntax highlighting
- normal code review
- filesystem tooling
- direct script testing

---

# 32. Attachments

Large files should normally remain on disk.

SQLite should primarily store attachment metadata.

Potential metadata:

```text
attachment_id
ticket_id
file_name
relative_path
mime_type
file_size
file_hash
created_at
```

Use BLOB storage only if a documented requirement justifies it.

---

# 33. Relative File Paths

Files controlled by F7Hub should use relative paths where practical.

Example:

```text
Data\Attachments\Tickets\10254\error.png
```

rather than storing machine-specific absolute paths.

This improves portability and backup behavior.

---

# 34. Transactions

Transactions are required when several database changes must succeed or fail as one unit.

Example:

```text
Create Ticket
    │
    ├── Insert ticket
    ├── Insert initial note
    └── Insert timeline event
```

If step 3 fails, partial data may be undesirable.

Use:

```text
BEGIN
→ operations
→ COMMIT
```

or:

```text
ROLLBACK
```

on failure.

---

# 35. Transaction Ownership

Transaction boundaries should normally be managed at the repository or service layer depending on the use case.

A multi-repository business operation may require the application service to coordinate a shared transaction.

Do not scatter transaction control unpredictably across GUI code.

---

# 36. Query Parameterization

All externally influenced SQL values must use parameterized queries.

Correct concept:

```python
cursor.execute(
    "SELECT * FROM tickets WHERE ticket_id = ?",
    (ticket_id,)
)
```

Avoid constructing SQL through string concatenation.

Parameterized queries protect:

- correctness
- escaping
- SQL injection boundaries

---

# 37. Dynamic SQL

Some SQL elements cannot be parameterized directly, such as column names.

Dynamic identifiers must be selected from controlled allowlists.

Never insert arbitrary user text into:

- table names
- column names
- SQL clauses
- sort expressions

---

# 38. Indexing Strategy

Indexes should support actual query patterns.

Likely candidates include:

- foreign keys
- ticket numbers
- frequently filtered status columns
- dates used for ordering/filtering
- unique external identifiers
- junction-table relationships
- high-value lookup fields

Do not index every field automatically.

---

# 39. Composite Indexes

Composite indexes should reflect real multi-column queries.

Example:

```text
WHERE company_id = ?
AND status = ?
ORDER BY created_at DESC
```

may justify an index resembling:

```text
(company_id, status, created_at)
```

Actual indexes should be confirmed through expected query patterns and query-plan analysis.

---

# 40. Index Cost

Indexes improve reads but have costs:

- disk space
- insert performance
- update performance
- maintenance complexity

An index requires justification.

---

# 41. Query Performance

High-value queries should eventually be validated using SQLite query-plan tools.

Example:

```sql
EXPLAIN QUERY PLAN
```

Performance work should focus on measured or predictable bottlenecks rather than premature optimization.

---

# 42. Full-Text Search

SQLite FTS5 should be used for domains with substantial searchable text.

Likely candidates:

- KB articles
- ticket notes
- ticket descriptions
- prompts
- script descriptions

FTS5 should not replace normal relational tables.

---

# 43. FTS Architecture

Conceptually:

```text
Relational Table
      │
      ▼
FTS5 Index
      │
      ▼
Search Query
      │
      ▼
Ranked Results
```

The relational table remains the source of truth.

FTS provides retrieval optimization.

---

# 44. FTS Synchronization

FTS indexes must remain synchronized with source records.

Possible strategies include:

- application-managed updates
- external-content FTS tables
- justified triggers

The strategy should be documented in `09_SQLSchema.md`.

---

# 45. Trigger Strategy

Triggers should be used sparingly.

Appropriate examples may include:

- FTS synchronization
- strict audit requirements
- automatic database-maintained invariants

Avoid implementing complex hidden business workflows in triggers.

Application logic is easier to inspect and test.

---

# 46. Views

Views may be used for:

- stable reporting queries
- common joins
- simplified read models
- search/result projections

Views should not obscure core relationships.

Complex views require documentation.

---

# 47. Migration Architecture

All structural schema changes must use migrations.

Migration files should be:

- ordered
- immutable after release
- versioned
- testable
- reversible where practical

Conceptual structure:

```text
Database\
└── Migrations\
    ├── 0001_core.sql
    ├── 0002_taxonomy.sql
    ├── 0003_companies_contacts.sql
    ├── 0004_tickets.sql
    └── ...
```

Exact folder structure must remain synchronized with `10_FolderStructure.md`.

---

# 48. Migration Versioning

The authoritative migration record is the dedicated `schema_migrations` table defined in `09_SQLSchema.md`.

`PRAGMA user_version` is not a competing migration-state authority.

`schema_migrations` is owned by the migration bootstrap infrastructure and is created before versioned migrations are evaluated. Versioned migration `0001_core.sql` therefore does not recreate it; `0001_core.sql` owns the first versioned application-schema object, `application_metadata`.

---

# 49. Migration Rules

A migration must define:

- previous state
- target state
- SQL changes
- data transformation if required
- failure handling
- validation
- backup requirement if destructive
- test coverage

---

# 50. Destructive Migrations

Operations such as:

- dropping columns
- dropping tables
- rewriting relationships
- deleting data
- changing primary keys
- major normalization changes

require explicit review.

Before a destructive migration:

```text
BACKUP
   ↓
MIGRATE
   ↓
VALIDATE
   ↓
TEST
```

Do not silently destroy data.

---

# 51. Seed Data

Seed data may be used for:

- controlled lookup values
- development environments
- tests
- default categories
- built-in diagnostic definitions if justified

Seed data should be separated from migrations where practical.

User operational data must not be treated as seed data.

---

# 52. Reference Data

Stable values may use reference tables when they carry business meaning.

Examples may include:

- ticket statuses
- article types
- script languages
- diagnostic states

Do not create lookup tables for every trivial Boolean or fixed internal implementation constant.

---

# 53. Audit Strategy

Audit records should be created only where operationally useful.

Potential auditable actions:

- privileged script execution
- administrative action
- ticket state transition
- KB publication
- diagnostic completion
- migration execution

Audit logs should answer:

```text
Who?
What?
When?
Target?
Result?
```

where applicable.

---

# 54. Audit vs Application Log

Audit data and application logs are different.

Application log:

```text
Database connection failed.
```

Audit record:

```text
Technician executed Disable-User against account X.
```

Audit information may require longer retention and stronger integrity rules.

---

# 55. Sensitive Data

Database design must assume that some records may contain:

- customer information
- ticket details
- email addresses
- diagnostic output
- system identifiers
- internal technical information

Do not store:

- plaintext passwords
- API secrets
- private keys
- refresh tokens
- authentication secrets

unless a separately approved secure credential architecture explicitly requires storage.

---

# 56. Data Minimization

Store only what F7Hub needs.

Do not persist information merely because it is available.

Examples:

If a PowerShell command returns hundreds of sensitive attributes but only three are required for diagnostics, store only the necessary information.

---

# 57. Clipboard Privacy

Clipboard persistence is especially sensitive.

The design should support:

- disabling history
- clearing history
- expiration
- excluding sensitive entries
- optional non-persistence

The clipboard database design must not assume all copied text is safe to retain.

---

# 58. Integration Data

External systems may provide identifiers and synchronized data.

Store:

- F7Hub internal ID
- provider
- external ID
- sync metadata where required

Avoid embedding one provider's model throughout core tables.

---

# 59. External Mapping Pattern

Preferred concept:

```text
F7Hub Entity
     │
     ▼
External Mapping
     │
     ├── provider
     └── external_id
```

This supports future integrations without replacing internal identity.

---

# 60. Repository Pattern

Python repositories isolate SQL from the rest of the application.

Conceptual examples:

```text
TicketRepository
CompanyRepository
ContactRepository
KnowledgeRepository
ScriptRepository
DiagnosticRepository
```

Repositories should expose domain-relevant operations rather than generic unrestricted SQL.

---

# 61. Repository Responsibilities

Repositories should handle:

- CRUD persistence
- parameterized SQL
- mapping
- database errors
- queries
- pagination where required
- transactions where appropriate

Repositories should not contain GUI logic.

---

# 62. Service Responsibilities

Application services coordinate business operations.

Example:

```text
TicketService.create_ticket()
    │
    ├── validate data
    ├── create ticket
    ├── create timeline entry
    └── return result
```

The service coordinates.

Repositories persist.

---

# 63. Direct Database Access

Direct database access from:

- PyQt widgets
- AutoHotkey
- PowerShell scripts
- plugins

should generally be prohibited.

Preferred route:

```text
Component
   ↓
Approved Service / Repository Boundary
   ↓
SQLite
```

Exceptions require documented architecture justification.

---

# 64. PowerShell and SQLite

PowerShell should not normally modify the core F7Hub database directly.

Preferred:

```text
PowerShell
   ↓
Structured JSON Result
   ↓
Python
   ↓
Repository
   ↓
SQLite
```

This preserves one controlled database access layer.

---

# 65. AutoHotkey and SQLite

AutoHotkey should not directly manipulate the core database schema or issue arbitrary SQL.

AHK should communicate through defined application interfaces where database persistence is required.

---

# 66. Plugin Database Access

Plugins must not receive unrestricted direct access to core database tables.

Future plugin architecture should provide:

- defined repositories
- service APIs
- controlled extension storage

Plugins must not silently alter the F7Hub schema.

---

# 67. Connection Management

For the initial desktop architecture:

- SQLite is local
- connection lifecycle is controlled by Python
- connection configuration is centralized
- foreign keys are enabled on connections
- transactions are explicit
- GUI components do not create random connections

Exact implementation belongs in `13_PythonArchitecture.md`.

---

# 68. Concurrency

SQLite supports multiple readers and controlled writing.

F7Hub must avoid assumptions that multiple simultaneous writers behave like a client-server database.

Background tasks that write data should use coordinated access.

Concurrency design must be tested before adding significant parallel database activity.

---

# 69. WAL Mode

Write-Ahead Logging may be considered:

```sql
PRAGMA journal_mode = WAL;
```

Potential benefits include improved reader/writer behavior.

WAL mode should be adopted only after testing with:

- application shutdown
- backups
- OneDrive project location
- crash recovery
- deployment environment

It is not automatically assumed as the final configuration.

---

# 70. OneDrive Consideration

The F7Hub project currently resides within a OneDrive path.

SQLite runtime database placement requires special consideration because synchronized folders may introduce:

- file locking
- synchronization conflicts
- duplicate/conflicted files
- latency

The production database location should be explicitly designed before operational use.

Recommended architecture may separate:

```text
Source Repository
→ OneDrive / Git-controlled project

Runtime Database
→ Local application data directory

Backups / Exports
→ Controlled backup location
```

Final runtime data paths belong in configuration and deployment documentation.

---

# 71. Backup Strategy

F7Hub must define a reliable database backup process before important operational data is stored.

Backups should account for:

- active transactions
- SQLite journal mode
- database consistency
- retention
- restoration

A raw file copy while the database is actively changing may not always be the preferred method.

---

# 72. Backup Types

Potential backup methods include:

- SQLite Backup API
- SQLite `.backup`
- controlled application shutdown + copy
- versioned backup files

The final strategy should be tested rather than assumed.

---

# 73. Restore Testing

A backup is not considered reliable merely because it exists.

The project should test:

```text
Create Backup
   ↓
Restore to Test Location
   ↓
Open Database
   ↓
Run Integrity Checks
   ↓
Validate Core Records
```

---

# 74. Integrity Checks

Database maintenance may include:

```sql
PRAGMA integrity_check;
```

and:

```sql
PRAGMA foreign_key_check;
```

These checks may be used in:

- testing
- migration validation
- maintenance
- recovery procedures

---

# 75. Corruption Handling

If corruption is detected:

1. stop destructive writes
2. preserve the affected database
3. log the failure
4. notify the user
5. attempt recovery only through documented procedures
6. restore from backup where required

Never silently recreate an empty database over corrupted operational data.

---

# 76. Development Databases

Development, testing and production-like data must remain separated.

Suggested logical environments:

```text
Development
Test
Operational
```

Automated tests must never run against the user's operational database.

---

# 77. Test Database Strategy

Tests should create isolated databases.

Potential methods:

- temporary files
- test-specific SQLite files
- in-memory SQLite where behavior is equivalent

Migration tests should use real file-based SQLite databases when filesystem behavior matters.

---

# 78. Database Testing

Database tests should cover:

- schema creation
- migrations
- primary keys
- foreign keys
- unique constraints
- check constraints
- inserts
- updates
- deletions
- transaction rollback
- repository queries
- FTS synchronization
- failure paths

---

# 79. Migration Testing

Each migration should be tested from its expected prior schema state.

Example:

```text
Schema v4
   ↓
Migration 0005
   ↓
Schema v5
   ↓
Integrity Check
   ↓
Repository Tests
```

Testing only a fresh final database is insufficient.

---

# 80. Performance Testing

Performance testing should focus on expected dataset sizes.

Possible future test data:

- thousands of tickets
- thousands of notes
- hundreds or thousands of KB articles
- script histories
- diagnostic results
- FTS content

Optimize based on realistic usage.

---

# 81. Pagination

Large record collections should support pagination or incremental loading where appropriate.

Examples:

- tickets
- logs
- audit history
- script executions
- search results

Do not load entire large tables into GUI memory unnecessarily.

---

# 82. Retention Strategy

Some data may require retention rules.

Candidates:

- clipboard history
- logs
- script outputs
- temporary diagnostic data
- search history

Retention should be configurable when appropriate.

Permanent domain records such as KB or ticket history require different lifecycle rules.

---

# 83. Archive Strategy

Historical records may be archived rather than deleted.

Potential examples:

- closed tickets
- deprecated KB articles
- disabled scripts
- old diagnostic workflows

Archiving design should preserve search and reporting requirements.

---

# 84. Schema Documentation

Every table in `09_SQLSchema.md` should eventually document:

```text
Purpose
Primary Key
Columns
Foreign Keys
Constraints
Indexes
Relationships
Lifecycle
Expected Queries
```

This makes schema intent explicit to coding agents.

---

# 85. ERD Documentation

`08_ERD.md` should describe:

- domains
- entities
- one-to-one relationships
- one-to-many relationships
- many-to-many relationships
- optional relationships
- ownership
- major lifecycle dependencies

The ERD should be designed before blindly generating SQL.

---

# 86. Table Inventory

Before implementing the full database, maintain a table inventory.

Suggested columns:

| Field | Meaning |
|---|---|
| Table | Proposed table name |
| Domain | Owning domain |
| Purpose | Why the table exists |
| Status | Proposed / Approved / Implemented |
| Parent | Main related entity |
| Priority | Implementation priority |
| Notes | Design considerations |

This prevents accidental duplication during large schema design.

---

# 87. Database Design Sequence

Recommended process:

```text
Requirements
    ↓
Domain Map
    ↓
Entity Inventory
    ↓
Relationships
    ↓
Normalize to 3NF
    ↓
Primary Keys
    ↓
Foreign Keys
    ↓
Constraints
    ↓
Query Analysis
    ↓
Indexes
    ↓
ERD
    ↓
SQL Schema
    ↓
Migration
    ↓
Repository
    ↓
Tests
```

Do not begin by generating 100 `CREATE TABLE` statements.

---

# 88. Initial Database Implementation Strategy

The database should be created in vertical slices.

Example sequence:

```text
1. Database bootstrap + migrations
2. Taxonomy, companies and contacts
3. Tickets
4. Ticket notes and timeline
5. Knowledge Base
6. Search / FTS5
7. Script registry
8. Script execution history
9. Diagnostics
10. Prompts / clipboard / workspace
11. Audit and reporting support
12. External integration mappings
```

The exact roadmap belongs in `16_Roadmap.md`.

---

# 89. First Database Implementation Slice

The first implementation slice is limited to SQLite bootstrap and migration infrastructure:

```text
database connection
+
foreign-key enforcement
+
busy timeout
+
schema_migrations tracking
+
migration discovery and ordering
+
checksum validation
+
transactional migration execution
+
database tests
```

Taxonomy, companies, contacts, tickets, repositories and GUI work belong to subsequent independently tested slices.

Implementation status as of 2026-09-03:

```text
SQLite connection and path resolution: VERIFIED
Migration discovery and history validation: VERIFIED
Transactional migration execution: VERIFIED
Integrity helpers: VERIFIED
Business-domain migrations through `0005_knowledge.sql`: VERIFIED
```

---

# 90. Database Completion Rule

A database feature is not complete merely because a table exists.

A completed database slice should normally include:

```text
[ ] Requirements identified
[ ] Domain approved
[ ] Entity justified
[ ] 3NF reviewed
[ ] Primary key defined
[ ] Foreign keys defined
[ ] Constraints defined
[ ] Indexes justified
[ ] Migration created
[ ] Repository implemented
[ ] Success paths tested
[ ] Failure paths tested
[ ] Integrity checks passed
[ ] ERD updated
[ ] SQL schema documentation updated
```

---

# 91. Test Status

Database validation must use:

```text
PASS
FAIL
NOT RUN
BLOCKED
```

Do not state that:

- migrations work
- normalization is complete
- integrity is valid
- indexes are optimal
- tests pass

unless those claims were actually verified.

---

# 92. Architecture Change Control

Explicit review is required before:

- replacing SQLite
- changing primary-key strategy globally
- major relationship redesign
- destructive migrations
- introducing direct PowerShell database access
- introducing direct AHK database access
- adding uncontrolled plugin schema access
- changing migration framework
- storing credentials
- introducing database encryption
- introducing multi-user write architecture
- moving to a remote database backend

---

# 93. Current Implementation Status

Repository inspection and tests through 2026-09-04 verified the Python SQLite connection, path-resolution, migration, checksum, rollback, bootstrap and integrity infrastructure. Versioned migrations now create `application_metadata` through `0001_core.sql`, shared taxonomy through `0002_taxonomy.sql`, the company/contact persistence schema through `0003_companies_contacts.sql`, the ticket-core schema through `0004_tickets.sql`, and the relational knowledge schema through `0005_knowledge.sql`. `CompanyRepository`, `ContactRepository` and `TicketRepository` provide parameterized persistence through the approved Python repository boundary. `TicketService` validates and atomically coordinates ticket creation, notes, status changes, resolution, closure and reopening with their history/timeline records. Writer transactions reserve the SQLite writer before reading current state. The first ticket-creation GUI and minimal application shell delegate through that service; notes/status GUI and the knowledge repository remain planned. The existing `Database\SQLite\F7Hub.db` file remains a zero-byte legacy scaffold and was not used by the tests.

```text
SQLite migration infrastructure: VERIFIED
Core application schema — application_metadata: VERIFIED
Taxonomy schema — categories and tags: VERIFIED
Company/contact schema — companies, notes, links and contacts: VERIFIED
Ticket-core schema — tickets, notes, status history and timeline: VERIFIED
Knowledge schema — articles, versions, links and approved junctions: VERIFIED
Company/contact repositories: VERIFIED
Ticket creation repository/service boundary: VERIFIED
Ticket activity repository/service boundary: VERIFIED
Remaining business database implementation: PLANNED
Isolated database tests: PASS — 129 tests
```

This document defines the intended database architecture beyond the verified infrastructure slice.

It must not be interpreted as proof that:

- business-domain tables beyond the knowledge slice exist
- business-domain migrations beyond `0005_knowledge.sql` exist
- indexes beyond the verified migrations exist
- FTS5 is configured
- repositories beyond `CompanyRepository`, `ContactRepository` and `TicketRepository` exist
- tests outside the reported suites pass

---

# 94. Relationship to Product Requirements

This architecture supports requirements such as:

```text
DATA-DB-001
→ SQLite

DATA-DB-002
→ Foreign keys

DATA-DB-003
→ Primary keys

DATA-DB-004
→ Referential integrity

DATA-DB-005
→ Constraints

DATA-DB-006
→ Parameterized queries

DATA-DB-007
→ Transactions

DATA-DB-008
→ Migrations

DATA-DB-009
→ No silent destructive migrations

DATA-DB-010
→ Normalization

DATA-DB-011
→ Indexing

DATA-DB-012
→ FTS5

DATA-DB-013
→ Backups

DATA-DB-014
→ Recovery
```

---

# 95. Related Documents

## Requirements

- `02_ProductRequirements.md`

## Architecture

- `06_SystemArchitecture.md`
- `13_PythonArchitecture.md`

## Database Design

- `08_ERD.md`
- `09_SQLSchema.md`

## Standards

- `14_DesignPrinciples.md`
- `15_NamingConventions.md`

## Planning

- `16_Roadmap.md`
- `17_Todo.md`
- `18_ChangeLog.md`

---

# 96. Database Golden Rules

The F7Hub database should follow these rules:

1. SQLite is the primary local relational database.
2. Repositories own database access.
3. GUI code does not contain raw SQL.
4. PowerShell does not directly manage the core database.
5. AutoHotkey does not directly manage the core database.
6. Every table must represent a justified persistent concept.
7. Normalize to 3NF unless a documented reason requires otherwise.
8. Every relationship must have deliberate foreign-key behavior.
9. Use constraints to protect important invariants.
10. Use parameterized queries.
11. Use transactions for atomic operations.
12. Use migrations for structural changes.
13. Never silently destroy operational data.
14. Index for actual query patterns.
15. Use FTS5 for justified full-text search.
16. Keep scripts and large files outside SQLite by default.
17. Separate F7Hub IDs from external provider IDs.
18. Keep secrets out of normal tables.
19. Test migrations and integrity.
20. Do not optimize for table count.

---

# 97. Final Database Architecture

The preferred database path is:

```text
                    F7Hub
                      │
                      ▼
              Application Services
                      │
                      ▼
                 Repositories
                      │
                      ▼
                    SQLite
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
   Relational      FTS5         Metadata
     Data          Search         / Audit
```

The database should remain:

- normalized
- relational
- constrained
- migration-driven
- testable
- recoverable
- searchable
- secure
- understandable

The central principle is:

> Model the real domain first.  
> Normalize it.  
> Protect it with keys and constraints.  
> Optimize only after understanding how it will be queried.

F7Hub should grow its database one justified, tested domain at a time.
