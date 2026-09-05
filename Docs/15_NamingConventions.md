# F7Hub Naming Conventions

> Document: `Docs/15_NamingConventions.md`  
> Project: F7Hub  
> Purpose: Define consistent naming rules for files, folders, Python, PySide6, PowerShell, AutoHotkey v2, SQLite, configuration, tests, logs, documentation, integrations, commands, and identifiers.
> Related Documents: `06_SystemArchitecture.md`, `07_Database.md`, `09_SQLSchema.md`, `10_FolderStructure.md`, `11_AHKArchitecture.md`, `12_PowerShellArchitecture.md`, `13_PythonArchitecture.md`, `14_DesignPrinciples.md`

---

# 1. Purpose

This document defines naming conventions for F7Hub.

It answers:

> How should F7Hub components be named so their purpose is clear and predictable?

Naming should make architecture easier to understand without requiring the reader to inspect implementation details.

Good names should communicate:

- responsibility
- technology
- domain
- intent
- scope

Consistency is more important than cleverness.

---

# 2. Naming Philosophy

Prefer names that are:

```text
clear
specific
predictable
searchable
stable
```

Avoid names that are:

```text
vague
abbreviated without reason
clever
duplicated
context-dependent
```

A good name should reduce the amount of explanation needed.

---

# 3. Naming Priority

When choosing a name, prefer:

```text
1. Domain meaning
2. Responsibility
3. Established language convention
4. Existing F7Hub convention
5. Brevity
```

Do not sacrifice clarity merely to make a name shorter.

---

# 4. Use Consistent Domain Vocabulary

The same concept should use the same term across technologies where practical.

Preferred:

```text
Ticket
KnowledgeArticle
DiagnosticSession
ScriptExecution
Company
Contact
```

Avoid using several names for the same concept:

```text
Ticket
Case
IncidentRecord
SupportItem
```

unless those concepts are actually different.

---

# 5. Avoid Unnecessary Abbreviations

Prefer:

```text
knowledge_article
diagnostic_session
PowerShellGateway
```

over:

```text
kb_art
diag_sess
PSGW
```

Common industry abbreviations may be used where they improve readability.

Examples:

```text
ID
URL
API
GUI
SQL
JSON
HTTP
MFA
DNS
IP
KB
```

---

# 6. Acronyms

When an acronym is widely understood, use its conventional spelling.

Examples:

```text
API
SQL
JSON
URL
DNS
MFA
HTTP
FTS
```

In Python class names:

```text
ApiClient
SqlRepository
JsonParser
```

may be easier to read than:

```text
APIClient
SQLRepository
JSONParser
```

However, F7Hub should remain internally consistent once a convention is selected.

---

# 7. Avoid Meaningless Suffixes

Avoid:

```text
Thing
Stuff
Object
Data2
New
Final
Final2
Updated
TempManager
Misc
```

Names should explain what the component actually does.

---

# 8. Avoid Version Numbers in Source Names

Do not normally create:

```text
TicketServiceV2.py
TicketServiceNew.py
TicketServiceFinal.py
```

Version history belongs in Git.

If multiple protocol versions must coexist, explicit versioning may be appropriate.

Example:

```text
PowerShellResultSchemaV1
PowerShellResultSchemaV2
```

---

# 9. File and Folder Naming

Top-level project folders use approved PascalCase names:

```text
AutoHotkey
PowerShell
Python
Database
Config
Data
Docs
Plugins
Tests
Assets
Build
Installer
Logs
Releases
Tools
```

Do not casually introduce alternate forms such as:

```text
powershell
PS
PythonCode
DatabaseFiles
```

---

# 10. Folder Naming

Use descriptive nouns or domain names.

Examples:

```text
Diagnostics
Reports
Repositories
Services
Integrations
Attachments
Migrations
```

Avoid:

```text
Other
Misc
Stuff
General
NewFolder
```

---

# 11. Folder Creation Rule

Before introducing a new folder:

```text
SEARCH
→ IDENTIFY
→ REUSE / EXTEND
→ CREATE ONLY IF NECESSARY
```

Folder naming should follow the owning technology's conventions.

---

# 12. Python Folder Naming

Python package directories should use:

```text
snake_case
```

Examples:

```text
ticketing
power_shell
external_integrations
```

However, current canonical layer folders already use simple lowercase names:

```text
app
gui
services
domain
repositories
infrastructure
integrations
search
diagnostics
utils
```

---

# 13. Python Module Naming

Python filenames should use:

```text
snake_case.py
```

Examples:

```text
ticket_service.py
ticket_repository.py
power_shell_gateway.py
diagnostic_engine.py
search_service.py
```

Avoid:

```text
TicketService.py
ticket-service.py
Ticket_Service.py
```

---

# 14. Python Package Names

Use short lowercase package names.

Preferred:

```text
f7hub
services
repositories
diagnostics
```

Avoid deeply nested package names unless architecture requires them.

---

# 15. Python Class Naming

Python classes use:

```text
PascalCase
```

Examples:

```text
TicketService
TicketRepository
PowerShellGateway
DiagnosticSession
SearchResult
```

---

# 16. Python Function Naming

Python functions use:

```text
snake_case
```

Examples:

```text
create_ticket()
add_note()
execute_script()
validate_ticket_status()
```

Function names should normally begin with a verb.

---

# 17. Python Method Naming

Methods also use:

```text
snake_case
```

Examples:

```text
get_ticket()
save_ticket()
start_session()
evaluate_condition()
```

---

# 18. Python Variable Naming

Variables use:

```text
snake_case
```

Examples:

```text
ticket_id
current_user
script_path
search_results
```

Avoid excessively short variables outside very small loops.

---

# 19. Python Constants

Constants use:

```text
UPPER_SNAKE_CASE
```

Examples:

```text
DEFAULT_TIMEOUT
MAX_SEARCH_RESULTS
POWER_SHELL_SCHEMA_VERSION
```

---

# 20. Python Private Members

Internal implementation details may use a leading underscore:

```text
_database
_validate_input()
_build_query()
```

Do not use underscores merely to hide poor architecture.

---

# 21. Python Boolean Names

Boolean values should read naturally.

Preferred:

```text
is_enabled
has_permission
can_execute
requires_admin
```

Avoid:

```text
enabled_flag
permission_bool
status_check
```

---

# 22. Python Collection Names

Use plural names for collections.

Preferred:

```text
tickets
results
errors
parameters
```

Use singular names for single objects:

```text
ticket
result
error
parameter
```

---

# 23. Python Repository Naming

Repository classes should follow:

```text
<Entity>Repository
```

Examples:

```text
TicketRepository
CompanyRepository
ContactRepository
KnowledgeRepository
ScriptRepository
```

If a repository spans a strongly related aggregate, name it by that aggregate.

---

# 24. Python Service Naming

Application services should follow:

```text
<Domain>Service
```

Examples:

```text
TicketService
KnowledgeService
DiagnosticService
SearchService
ScriptService
```

Avoid generic:

```text
MainService
DataService
GeneralService
```

---

# 25. Gateway Naming

External or infrastructure adapters should normally use:

```text
<TechnologyOrProvider>Gateway
```

Examples:

```text
PowerShellGateway
GraphGateway
FileSystemGateway
HaloPsaGateway
```

Use `Client` where the object is specifically an API client rather than an application boundary.

---

# 26. Registry Naming

A registry maintains discoverable definitions or mappings.

Examples:

```text
CommandRegistry
ScriptRegistry
IntegrationRegistry
```

Do not call ordinary collections registries unless they actually provide registry behavior.

---

# 27. Builder Naming

Use `Builder` when an object incrementally constructs another object.

Examples:

```text
AIContextBuilder
ReportBuilder
```

Do not use `Builder` as a generic alternative to `Service`.

---

# 28. Validator Naming

Validation components should be explicit.

Examples:

```text
TicketValidator
ScriptParameterValidator
```

Functions may use:

```text
validate_ticket()
validate_script_parameters()
```

---

# 29. Python Exception Naming

Custom exceptions should end with:

```text
Error
```

Examples:

```text
TicketNotFoundError
InvalidTicketStateError
ScriptExecutionError
IntegrationUnavailableError
```

---

# 30. Python DTO Naming

Where DTOs are useful, use meaningful role names.

Examples:

```text
TicketSummary
TicketCreateRequest
TicketSearchResult
ScriptExecutionResult
```

Avoid mechanical names such as:

```text
TicketDTO1
TicketDataObject
```

---

# 31. PySide6 Widget Naming

Python widget classes use PascalCase.

Examples:

```text
TicketView
TicketEditor
SearchPanel
DiagnosticPanel
MainWindow
```

---

# 32. PySide6 View Naming

Use `View` when a component represents a substantial feature screen.

Examples:

```text
TicketView
KnowledgeView
DashboardView
```

Use `Panel` for smaller contextual regions.

Examples:

```text
AIContextPanel
PowerShellOutputPanel
```

---

# 33. PySide6 Dialog Naming

Dialogs should end with:

```text
Dialog
```

Examples:

```text
SettingsDialog
ConfirmExecutionDialog
TicketDeleteDialog
```

---

# 34. PySide6 Widget Variable Names

Use descriptive snake_case.

Examples:

```text
ticket_table
save_button
search_box
status_label
```

Avoid Qt Designer-style generic names such as:

```text
pushButton_7
lineEdit_3
widget_12
```

in maintained application code.

---

# 35. PySide6 Action Naming

Internal Qt actions may use:

```text
action_<verb>_<object>
```

Examples:

```text
action_open_ticket
action_run_diagnostic
action_show_logs
```

Visible labels remain user-friendly.

---

# 36. Qt Signal Naming

Signals should describe events.

Examples:

```text
ticket_selected
ticket_saved
search_requested
diagnostic_completed
script_finished
```

Avoid ambiguous signals such as:

```text
changed
clicked_custom
event_done
```

---

# 37. Qt Slot / Handler Naming

Event handlers should describe the event.

Examples:

```text
on_save_clicked()
on_ticket_selected()
on_search_requested()
```

or use direct descriptive methods such as:

```text
save_ticket()
open_selected_ticket()
```

Do not mix several handler styles randomly.

---

# 38. PowerShell File Naming

PowerShell script files should follow:

```text
Verb-Noun.ps1
```

Examples:

```text
Test-DnsHealth.ps1
Get-SystemInformation.ps1
Invoke-DeviceDiagnostic.ps1
Export-TenantReport.ps1
```

---

# 39. PowerShell Function Naming

Functions use standard PowerShell:

```text
Verb-Noun
```

Examples:

```text
Get-F7HubSystemInfo
Test-F7HubDnsHealth
Invoke-F7HubDiagnostic
New-F7HubResult
```

---

# 40. PowerShell Approved Verbs

Prefer approved PowerShell verbs.

Common examples:

```text
Get
Set
New
Remove
Test
Invoke
Start
Stop
Export
Import
ConvertTo
ConvertFrom
```

Check `Get-Verb` when uncertain.

---

# 41. PowerShell Noun Naming

F7Hub-specific reusable functions should normally include `F7Hub` in the noun when they could conflict with general functions.

Example:

```text
New-F7HubResult
Get-F7HubConfiguration
```

Domain-specific scripts may remain clearer without forcing `F7Hub` everywhere.

Example:

```text
Test-DnsHealth.ps1
```

---

# 42. PowerShell Diagnostic Script Naming

Read-only diagnostic scripts should often use:

```text
Test-<Subject>.ps1
```

Examples:

```text
Test-DnsHealth.ps1
Test-OutlookConnectivity.ps1
Test-NetworkAdapterState.ps1
```

---

# 43. PowerShell Retrieval Script Naming

Information-gathering scripts should often use:

```text
Get-<Subject>.ps1
```

Examples:

```text
Get-MailboxPermission.ps1
Get-DeviceComplianceState.ps1
Get-SystemInformation.ps1
```

---

# 44. PowerShell Remediation Naming

Use a verb that clearly communicates the change.

Examples:

```text
Reset-DnsCache.ps1
Repair-NetworkConfiguration.ps1
Set-MailboxPermission.ps1
Remove-StaleProfile.ps1
```

Avoid naming a modifying script with `Get` or `Test`.

---

# 45. PowerShell Variable Naming

Use conventional PowerShell PascalCase variable names where practical.

Examples:

```powershell
$TicketId
$UserPrincipalName
$ScriptPath
$ExecutionResult
```

Short variables are acceptable in obvious local contexts.

---

# 46. PowerShell Parameters

Parameter names should be explicit.

Examples:

```powershell
-ComputerName
-UserPrincipalName
-DeviceId
-Mailbox
```

Avoid:

```powershell
-Value
-Thing
-Input
```

unless the meaning is genuinely generic.

---

# 47. PowerShell Module Naming

Custom modules should use clear names.

Potential future examples:

```text
F7Hub.Core
F7Hub.Diagnostics
```

Do not create many PowerShell modules before actual reuse justifies them.

---

# 48. AutoHotkey File Naming

AutoHotkey v2 files may use PascalCase for feature files.

Examples:

```text
F7Hub.ahk
ClipboardActions.ahk
WindowLaunchers.ahk
TicketHotstrings.ahk
```

Choose one style and remain consistent.

---

# 49. AutoHotkey Function Naming

Prefer PascalCase for AHK v2 functions.

Examples:

```text
OpenF7Hub()
ActivateOrLaunch()
RestoreClipboard()
ShowQuickMenu()
```

---

# 50. AutoHotkey Class Naming

AHK classes use PascalCase.

Examples:

```text
ClipboardManager
LauncherRegistry
F7HubConfig
```

Use classes only when they improve design.

---

# 51. AutoHotkey Variable Naming

Use readable names.

Examples:

```text
ticketId
scriptPath
previousClipboard
```

A consistent `camelCase` style is recommended for local AHK variables.

---

# 52. AutoHotkey Constants

Constants or values intended as constants should use clear uppercase naming where practical.

Example:

```text
F7HUB_WINDOW_TITLE
DEFAULT_TIMEOUT_MS
```

Exact enforcement depends on AHK implementation style.

---

# 53. AutoHotkey Hotkey Action Names

Internal action identifiers should use stable dot notation.

Examples:

```text
app.open
ticket.new
search.open
diagnostic.start
clipboard.open
```

These action IDs may later be shared with Python.

---

# 54. Hotstring Naming

Hotstring triggers should be:

- short
- memorable
- unlikely to appear accidentally

Examples:

```text
;close
;escalate
;mfa
;vpn
```

Exact triggers should be documented if they become part of standard technician workflows.

---

# 55. SQLite Naming Style

SQLite identifiers use:

```text
snake_case
```

This applies to:

- tables
- columns
- indexes
- views
- triggers
- constraints where explicitly named

---

# 56. SQLite Table Names

Use plural nouns for entity tables.

Examples:

```text
tickets
companies
contacts
knowledge_articles
scripts
diagnostic_sessions
```

This convention should remain consistent throughout the schema.

---

# 57. Junction Table Names

Junction tables should normally combine the related entity names.

Examples:

```text
ticket_tags
knowledge_article_tags
ticket_knowledge_articles
knowledge_article_scripts
```

Use names that make both sides of the relationship obvious.

---

# 58. SQLite Column Names

Columns use descriptive snake_case.

Examples:

```text
ticket_id
created_at
updated_at
company_id
external_id
```

Avoid vague names such as:

```text
value
data
info
field1
```

unless they represent intentionally generic data.

---

# 59. Primary Key Naming

Preferred entity primary key convention:

```text
<table_singular>_id
```

Examples:

```text
ticket_id
company_id
contact_id
script_id
```

This improves clarity in joins.

---

# 60. Foreign Key Naming

Foreign key columns should normally use the referenced primary key name.

Example:

```text
tickets.company_id
```

references:

```text
companies.company_id
```

Avoid inconsistent aliases such as:

```text
company
company_ref
company_fk
```

for the same relationship.

---

# 61. External Identifier Naming

External provider identifiers should remain separate.

Examples:

```text
external_id
provider_id
entra_object_id
halo_ticket_id
```

Use provider-specific names when multiple external systems could supply IDs.

---

# 62. Timestamp Naming

Use:

```text
created_at
updated_at
deleted_at
started_at
completed_at
```

when those semantics apply.

Use `_at` for timestamps.

---

# 63. Date Naming

Use `_date` for date-only values.

Examples:

```text
due_date
resolved_date
```

Do not use `_date` for values containing date and time.

---

# 64. Boolean Column Naming

Boolean columns should read naturally.

Examples:

```text
is_active
is_archived
is_enabled
requires_admin
```

SQLite representation may use integer constraints as defined by the schema.

---

# 65. Status Columns

Use domain-specific status names.

Examples:

```text
status
execution_status
session_status
```

Avoid generic status fields where several statuses exist in one table.

---

# 66. JSON Column Naming

If JSON storage is justified, the name should describe its purpose.

Preferred:

```text
result_payload
layout_state
provider_metadata
```

Avoid:

```text
json
data
blob
```

unless the contents are truly generic.

---

# 67. SQLite Index Naming

Recommended convention:

```text
idx_<table>_<column_or_purpose>
```

Examples:

```text
idx_tickets_status
idx_tickets_company_id
idx_ticket_notes_ticket_id
```

Composite example:

```text
idx_tickets_status_created_at
```

---

# 68. Unique Index Naming

Use:

```text
ux_<table>_<column_or_purpose>
```

when a separately named unique index is required.

Example:

```text
ux_tags_name
```

Unique constraints may instead be defined directly in table schemas.

---

# 69. SQLite Foreign Key Constraint Naming

SQLite does not require explicit foreign key constraint names.

If F7Hub later standardizes named constraints, use a predictable convention.

Possible:

```text
fk_<table>_<referenced_table>
```

Do not introduce unnecessary constraint names solely for appearance.

---

# 70. Check Constraint Naming

Where named check constraints provide value:

```text
ck_<table>_<purpose>
```

Example:

```text
ck_tickets_status
```

Again, use only if the schema style actually benefits.

---

# 71. View Naming

Views should describe the result they expose.

Potential convention:

```text
vw_<purpose>
```

Examples:

```text
vw_ticket_summary
vw_script_execution_history
```

Views should only be introduced when justified.

---

# 72. Trigger Naming

If triggers are justified:

```text
trg_<table>_<timing>_<action>
```

Example:

```text
trg_tickets_after_update
```

Triggers should remain exceptional, not the default place for business logic.

The standardized FTS5 synchronization triggers defined by `09_SQLSchema.md` are an intentional exception and use compact table/event names such as:

```text
tickets_ai
tickets_ad
tickets_au
```

where `ai`, `ad`, and `au` mean after insert, after delete, and after update. Other triggers should follow the descriptive `trg_<table>_<timing>_<action>` form unless `09_SQLSchema.md` explicitly defines another approved pattern.

---

# 73. FTS Table Naming

FTS5 tables should clearly identify their source.

Potential:

```text
knowledge_articles_fts
tickets_fts
scripts_fts
```

FTS tables are derived search infrastructure, not relational source of truth.

---

# 74. Migration File Naming

Migration files should have sortable version prefixes.

Recommended:

```text
0001_core.sql
0002_taxonomy.sql
0003_companies_contacts.sql
```

The exact numbering mechanism must remain consistent.

---

# 75. Migration Naming Rule

Migration names should describe the structural change.

Preferred:

```text
0012_add_script_execution_status.sql
```

Avoid:

```text
0012_update.sql
0013_changes.sql
0014_fix.sql
```

---

# 76. Seed File Naming

Seed files should describe the data they provide.

Examples:

```text
seed_default_ticket_statuses.sql
seed_default_categories.sql
```

Seed data should not be confused with migrations.

---

# 77. SQL Query File Naming

If external query files are used:

```text
get_ticket_by_id.sql
search_knowledge_articles.sql
list_recent_tickets.sql
```

Use snake_case and action-oriented names.

---

# 78. Database File Naming

Development database:

```text
f7hub_dev.db
```

Potential test database:

```text
f7hub_test.db
```

Installed runtime:

```text
f7hub.db
```

Do not use names such as:

```text
database1.db
new.db
final.db
```

---

# 79. Configuration File Naming

Configuration filenames should describe scope or responsibility.

Examples:

```text
app_defaults.json
powershell_defaults.json
ui_defaults.json
```

Do not organize configuration merely by file format.

---

# 80. Configuration Key Naming

Within configuration formats, use one consistent convention.

Recommended:

```text
snake_case
```

Examples:

```text
database_path
power_shell_timeout
default_workspace
```

---

# 81. Environment Variable Naming

Environment variables should use:

```text
F7HUB_<NAME>
```

Examples:

```text
F7HUB_LOG_LEVEL
F7HUB_DATA_DIR
F7HUB_ENVIRONMENT
```

Secrets, if environment variables are used, should also follow this prefix.

---

# 82. Command IDs

Internal application commands should use:

```text
domain.action
```

Examples:

```text
ticket.new
ticket.open
ticket.save
search.open
diagnostic.start
script.execute
workspace.switch
```

These identifiers should remain stable even if visible UI labels change.

---

# 83. Command ID Rules

Use:

```text
lowercase
dot-separated
stable nouns and verbs
```

Avoid:

```text
NewTicketButtonAction
doSearchNow
CMD_001
```

---

# 84. Feature IDs

Feature IDs in documentation follow existing patterns such as:

```text
FEAT-TICKET-001
FEAT-KB-001
FEAT-SEARCH-001
```

IDs should remain stable after publication.

Do not renumber existing IDs merely to close gaps.

---

# 85. Requirement IDs

Requirements use established prefixes:

```text
FR-
NFR-
DATA-
INT-
SEC-
TEST-
DOC-
```

Examples:

```text
FR-TICKET-001
SEC-PS-002
DATA-DB-003
```

Exact established IDs in `02_ProductRequirements.md` should remain the source of truth.

---

# 86. Test Naming

Tests should communicate behavior.

Python example:

```text
test_create_ticket_with_valid_data()
test_create_ticket_rejects_missing_subject()
```

Avoid:

```text
test1()
test_ticket()
test_function()
```

---

# 87. Python Test File Naming

Use:

```text
test_<subject>.py
```

Examples:

```text
test_ticket_service.py
test_ticket_repository.py
test_power_shell_gateway.py
```

---

# 88. PowerShell Test Naming

Pester files commonly use:

```text
<Subject>.Tests.ps1
```

Examples:

```text
Test-DnsHealth.Tests.ps1
F7HubResult.Tests.ps1
```

---

# 89. Test IDs for Manual Tests

Manual tests may use stable IDs.

Potential:

```text
TEST-AHK-LAUNCH-001
TEST-GUI-TICKET-001
TEST-PS-DNS-001
```

Use IDs only where tracking provides value.

---

# 90. Test Fixture Naming

Fixtures should communicate that they are synthetic.

Examples:

```text
sample_ticket.json
synthetic_contacts.csv
test_database_seed.sql
```

Never name production-derived files as generic samples.

---

# 91. Log File Naming

Log filenames should identify source and, where useful, date.

Potential examples:

```text
f7hub.log
f7hub-2026-09-02.log
powershell-execution.log
```

Rotating log strategy should determine final naming.

---

# 92. Export File Naming

Exports should identify content.

Examples:

```text
ticket_report_2026-09-02.csv
script_execution_report_2026-09-02.json
```

Avoid:

```text
export1.csv
output.csv
report-new.csv
```

---

# 93. Attachment Naming

Do not assume original attachment filenames are unique.

Stored files may eventually use:

```text
stable generated identifier
+
sanitized original filename
```

Example concept:

```text
a83f21_invoice.pdf
```

Exact naming should be defined when attachment storage is implemented.

---

# 94. Generated File Naming

Generated outputs should be distinguishable from source.

Names may include:

```text
generated
export
build
version
timestamp
```

where useful.

Do not add timestamps to source-controlled filenames.

---

# 95. Documentation Filenames

Canonical docs use:

```text
NN_Name.md
```

Current canonical set:

```text
00_ProjectVision.md
01_Project.md
02_ProductRequirements.md
03_Features.md
04_UserWorkflows.md
05_GUI.md
06_SystemArchitecture.md
07_Database.md
08_ERD.md
09_SQLSchema.md
10_FolderStructure.md
11_AHKArchitecture.md
12_PowerShellArchitecture.md
13_PythonArchitecture.md
14_DesignPrinciples.md
15_NamingConventions.md
16_Roadmap.md
17_Todo.md
18_ChangeLog.md
19_DocumentationIndex.md
```

These names are canonical.

---

# 96. Documentation Heading Naming

Headings should describe content directly.

Preferred:

```text
# Database Architecture
## Foreign Key Rules
## Migration Strategy
```

Avoid conversational headings such as:

```text
# Some Thoughts
## Other Stuff
```

---

# 97. Archived Documentation Naming

Archived files should preserve enough identity to understand origin.

Potential:

```text
08_ERD_Old_Brainstorm.md
```

or date/version-based archival folders.

Archived documents are not current source of truth.

---

# 98. Diagram Naming

Diagram filenames should describe purpose.

Examples:

```text
system_architecture.svg
open_ticket_sequence.svg
diagnostic_engine_flow.svg
database_domain_map.svg
```

---

# 99. Screenshot Naming

Screenshots should describe feature and state.

Examples:

```text
ticket_view_empty.png
diagnostic_session_running.png
settings_integrations.png
```

Avoid:

```text
Screenshot1.png
image.png
test.png
```

---

# 100. Integration Naming

Use the official provider/product name internally where practical.

Examples:

```text
MicrosoftGraph
ExchangeOnline
NinjaOne
HaloPSA
```

Naming should not imply compatibility with services that are not actually integrated.

---

# 101. Integration Provider IDs

Stable provider identifiers may use lowercase values.

Examples:

```text
microsoft_graph
exchange_online
halo_psa
ninja_one
openai
```

Use internal IDs separately from display labels.

---

# 102. External Mapping Names

External mappings should identify both provider and entity where needed.

Examples:

```text
provider
external_id
external_type
```

or provider-specific columns if the relationship is intentionally fixed.

---

# 103. AI Component Naming

AI components should describe responsibility.

Examples:

```text
AIService
AIProvider
AIContextBuilder
AIResponseValidator
```

Avoid anthropomorphic names for architectural components.

---

# 104. AI Prompt Naming

Prompt templates should identify their purpose.

Examples:

```text
ticket_summary
resolution_draft
kb_article_draft
diagnostic_explanation
```

Do not name prompts:

```text
prompt1
main_prompt
good_prompt
```

---

# 105. Prompt Version Naming

If prompt versioning becomes required, use explicit metadata rather than copying files with names such as:

```text
prompt_final2.txt
```

Possible conceptual identifier:

```text
ticket_summary:v2
```

Exact implementation should be defined later.

---

# 106. Diagnostic Workflow Naming

Workflows should describe the troubleshooting objective.

Examples:

```text
Outlook Cannot Send Email
VPN Connectivity
Windows Login Failure
OneDrive Sync Failure
```

Internal identifiers may use stable normalized names.

Example:

```text
outlook_send_failure
vpn_connectivity
```

---

# 107. Diagnostic Step IDs

Workflow step identifiers must remain stable within a workflow.

Potential:

```text
step_001
step_002
```

or database IDs.

Do not use the visible question text itself as the identifier.

---

# 108. Script Registry Naming

Script display name:

```text
Test DNS Health
```

Script file:

```text
Test-DnsHealth.ps1
```

Stable action or registry identifier may be:

```text
diagnostic.dns.health
```

These concepts should not be confused.

---

# 109. Status Value Naming

Machine status values should be stable and predictable.

Examples:

```text
OPEN
IN_PROGRESS
RESOLVED
CLOSED
```

or lowercase equivalents if the schema standard selects them.

Do not mix:

```text
Open
in_progress
RESOLVED
Closed
```

inside one field.

The exact database representation belongs in `09_SQLSchema.md`.

---

# 110. Enum Value Naming

Python enum member names should generally use:

```text
UPPER_SNAKE_CASE
```

Example:

```python
class ScriptRisk(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
```

Persistent value format should remain stable.

---

# 111. Error Code Naming

If application-level error codes are introduced, use clear stable categories.

Potential:

```text
TICKET_NOT_FOUND
SCRIPT_TIMEOUT
INTEGRATION_UNAVAILABLE
```

Do not create numeric error codes unless they provide a concrete benefit.

---

# 112. Event Naming

Application events should use past-tense or completed-state names where appropriate.

Examples:

```text
TicketCreated
TicketUpdated
DiagnosticCompleted
ScriptExecutionFinished
```

An event represents something that happened.

---

# 113. Event Handler Naming

Handlers should communicate what they react to.

Examples:

```text
handle_ticket_created()
on_diagnostic_completed()
```

Choose one consistent approach per layer.

---

# 114. Database vs Python Naming

Database:

```text
ticket_id
created_at
```

Python:

```text
ticket_id
created_at
```

Keeping field names aligned reduces mapping complexity where practical.

Python classes remain:

```text
Ticket
TicketRepository
```

---

# 115. API Field Naming

When consuming external APIs, preserve provider field names at the adapter boundary when necessary.

Translate them into F7Hub naming before passing them deep into the application.

Example:

```text
Graph field
userPrincipalName
        ↓
adapter
        ↓
user_principal_name
```

---

# 116. Do Not Leak Provider Naming Everywhere

Provider-specific terminology should stay near provider adapters when possible.

This reduces coupling.

Example:

```text
GraphGateway
→ translates Graph response

TicketService
→ uses F7Hub domain terminology
```

---

# 117. Public vs Internal Names

A display label may be:

```text
Run Diagnostic
```

while the stable internal command ID is:

```text
diagnostic.start
```

Visible wording may evolve.

Internal IDs should change rarely.

---

# 118. Singular vs Plural

General convention:

```text
Class
→ singular

Variable containing one item
→ singular

Collection
→ plural

Database entity table
→ plural
```

Examples:

```text
Ticket
ticket
tickets
tickets table
```

---

# 119. Verb Choice

Use verbs that reflect behavior.

Preferred:

```text
get
list
create
update
delete
validate
execute
search
start
complete
```

Avoid ambiguous verbs such as:

```text
process
handle
do
manage
```

unless they genuinely describe the operation.

---

# 120. Get vs List

Recommended semantic distinction:

```text
get_ticket(ticket_id)
→ zero or one specific record

list_tickets(...)
→ collection

search_tickets(query)
→ query-based collection
```

Consistent semantics make APIs easier to predict.

---

# 121. Create vs New

Python/application code should generally use:

```text
create
```

for persistence/use-case operations.

PowerShell should follow approved verb conventions and may use:

```text
New-
```

Example:

```text
TicketService.create_ticket()
New-F7HubResult
```

Technology conventions take precedence where appropriate.

---

# 122. Delete vs Remove

Python/service convention may use:

```text
delete_ticket()
```

PowerShell convention commonly uses:

```text
Remove-
```

The difference is acceptable because each language has established conventions.

---

# 123. Execute vs Run vs Invoke

Use consistently by architectural role.

Recommended:

```text
ScriptService.execute_script()
PowerShellGateway.execute(...)
```

PowerShell cmdlets/scripts may use:

```text
Invoke-
```

Visible GUI wording may use:

```text
Run
```

---

# 124. Search vs Find

Use:

```text
search
```

for multi-result user queries.

Use:

```text
find
```

only where semantics clearly imply locating something specific.

Prefer consistency in the core API.

---

# 125. Load vs Get

Use:

```text
get
```

for domain retrieval.

Use:

```text
load
```

for technical loading of:

- configuration
- files
- resources
- UI state

Example:

```text
load_configuration()
get_ticket()
```

---

# 126. Save Naming

`save` may be acceptable for GUI-level intent when the operation could mean create or update.

At service/repository level, explicit methods may be clearer:

```text
create_ticket()
update_ticket()
```

Do not use `save()` everywhere if behavior is ambiguous.

---

# 127. Manager Naming Rule

Avoid `Manager` unless the component genuinely manages lifecycle or coordination and no more precise term exists.

Before creating:

```text
TicketManager
```

consider:

```text
TicketService
TicketRepository
TicketController
```

---

# 128. Helper Naming Rule

Avoid creating generic classes such as:

```text
TicketHelper
DatabaseHelper
PowerShellHelper
```

Prefer names that reveal responsibility.

---

# 129. Common Name Smells

Names that should trigger review include:

```text
Manager
Helper
Utils
Common
Base
Generic
Misc
Temp
New
Old
Final
Data
Processor
Handler
```

These are not forbidden, but they often indicate unclear ownership.

---

# 130. Base Class Naming

Use `Base` only for a real abstraction intended for inheritance.

Example:

```text
BaseSearchProvider
```

Do not create base classes merely because two classes currently share several lines.

---

# 131. Interface / Protocol Naming

If Python protocols or abstract interfaces are introduced, prefer role-based names.

Examples:

```text
AIProvider
SearchProvider
```

Avoid unnecessary `I` prefixes such as:

```text
IAIProvider
ISearchProvider
```

unless the project deliberately adopts that convention.

---

# 132. Factory Naming

Use `Factory` only when object creation itself has meaningful variation or complexity.

Example:

```text
IntegrationGatewayFactory
```

Do not create factories for simple constructors.

---

# 133. Configuration Class Naming

Examples:

```text
AppSettings
DatabaseSettings
PowerShellSettings
UISettings
```

Prefer `Settings` for user/application configuration and `Config` only where that distinction is useful.

---

# 134. Boolean Method Naming

Methods returning booleans should read as questions.

Examples:

```text
is_running()
has_permission()
can_execute()
requires_elevation()
```

---

# 135. Count Naming

Counts should make the counted entity clear.

Examples:

```text
ticket_count
error_count
result_count
```

Avoid:

```text
count1
total
number
```

when context is not obvious.

---

# 136. Unit Naming

When a numeric value includes a unit, include it in the name if ambiguity is possible.

Examples:

```text
timeout_seconds
duration_ms
file_size_bytes
```

This prevents unit bugs.

---

# 137. Time Naming

Prefer explicit names:

```text
timeout_seconds
poll_interval_seconds
elapsed_ms
```

Avoid generic:

```text
delay
time
duration
```

when the unit is not obvious.

---

# 138. Path Naming

Variables containing filesystem paths should end with:

```text
_path
```

Examples:

```text
script_path
database_path
attachment_path
```

Directories may use:

```text
_dir
```

Examples:

```text
data_dir
logs_dir
```

---

# 139. URL Naming

Use:

```text
_url
```

Examples:

```text
portal_url
api_base_url
documentation_url
```

---

# 140. ID Naming

Use:

```text
ticket_id
company_id
execution_id
```

Do not use generic:

```text
id
```

where multiple identifiers exist in scope.

Short `id` may be acceptable inside an entity itself when context is unmistakable, but explicit names are preferred across layers.

---

# 141. User Principal Name Naming

Use the full domain term where practical:

```text
user_principal_name
```

PowerShell parameter:

```text
UserPrincipalName
```

A local abbreviation such as `upn` may be acceptable in tightly scoped code, but not as the canonical schema name unless specifically standardized.

---

# 142. Microsoft Product Naming

Use current official terminology in documentation and code where applicable.

Examples:

```text
Microsoft Entra ID
Microsoft Graph
Exchange Online
Microsoft Intune
Microsoft Defender
```

Avoid introducing deprecated names into new architecture unless referencing legacy compatibility.

---

# 143. AutoHotkey Naming

Canonical product naming:

```text
AutoHotkey v2
```

In short technical contexts:

```text
AHK
```

is acceptable.

Do not write new source assuming AHK v1.

---

# 144. PowerShell Naming

Canonical technology name:

```text
PowerShell
```

Preferred runtime:

```text
PowerShell 7
```

Executable:

```text
pwsh.exe
```

Use `Windows PowerShell 5.1` explicitly when referring to the legacy Windows runtime.

---

# 145. PyQt Naming

Canonical GUI framework:

```text
PySide6
```

Do not mix documentation references to:

```text
PySide6
PyQt5
PySide2
```

unless discussing alternatives or legacy content.

---

# 146. SQLite Naming

Canonical database technology:

```text
SQLite
```

Use:

```text
SQLite database
```

rather than ambiguous terms such as:

```text
SQL DB
```

when describing F7Hub persistence.

---

# 147. F7Hub Name

Canonical project/product name:

```text
F7Hub
```

Use the same capitalization everywhere.

Avoid:

```text
F7 Hub
F7hub
f7Hub
F7HUB
```

except where lowercase technical identifiers are required.

Examples:

```text
Python package: f7hub
database file: f7hub.db
environment variable prefix: F7HUB_
```

---

# 148. File Extension Naming

Use standard lowercase file extensions:

```text
.py
.ps1
.psm1
.psd1
.ahk
.sql
.md
.json
.ini
.yaml
.csv
```

Do not invent custom extensions unnecessarily.

---

# 149. YAML vs YML

If YAML is used, prefer one extension consistently.

Recommended:

```text
.yaml
```

Do not mix `.yaml` and `.yml` without reason.

---

# 150. JSON Naming

JSON files should use descriptive snake_case filenames.

Examples:

```text
app_defaults.json
script_manifest.json
```

---

# 151. Markdown Naming

Canonical documentation uses PascalCase descriptive names with numeric ordering.

Supporting research docs may use descriptive names consistent with their folder.

Avoid spaces when a stable machine-readable filename is preferable.

---

# 152. Git Branch Naming

Recommended branch patterns:

```text
feature/<short-description>
fix/<short-description>
docs/<short-description>
refactor/<short-description>
experiment/<short-description>
```

Examples:

```text
feature/ticket-creation
fix/powershell-timeout
docs/database-rules
```

---

# 153. Git Branch Naming Rules

Use:

```text
lowercase
hyphen-separated
short descriptive phrases
```

Avoid:

```text
mybranch
new
test
john-work
final
```

---

# 154. Git Commit Naming

Commit messages should describe one coherent change.

Recommended style:

```text
Add ticket creation repository
Fix PowerShell timeout handling
Update database migration rules
```

Exact conventional-commit syntax is optional unless later adopted.

---

# 155. Release Naming

Use semantic versioning where appropriate.

Example:

```text
0.1.0-alpha
0.2.0
1.0.0
```

Release folders should reflect real release versions, not permanent generic categories.

---

# 156. Environment Naming

Potential environment identifiers:

```text
development
test
production
```

Use consistent lowercase machine values.

Avoid creating environments that are not actually needed.

---

# 157. Development Database Naming

Preferred:

```text
f7hub_dev.db
```

Test:

```text
f7hub_test.db
```

Production/runtime:

```text
f7hub.db
```

---

# 158. Feature Flag Naming

If feature flags are introduced, use descriptive booleans.

Examples:

```text
enable_ai_assistant
enable_clipboard_history
enable_plugin_loading
```

Avoid:

```text
feature1
new_mode
experimental_x
```

unless genuinely temporary and documented.

---

# 159. Logging Categories

Logger names should normally follow Python module names.

Example:

```python
logging.getLogger(__name__)
```

Application-level conceptual categories may include:

```text
application
database
powershell
integration
diagnostics
```

Do not invent a large custom logger taxonomy without need.

---

# 160. Audit Event Naming

Audit event action names should be stable.

Potential:

```text
ticket.created
ticket.resolved
script.executed
integration.connected
```

Use machine-friendly internal identifiers separate from human-readable descriptions.

---

# 161. File Naming and Case Sensitivity

Windows is generally case-insensitive, but code should not rely on inconsistent casing.

Treat canonical case as significant for project consistency.

Example:

```text
PowerShell
```

not sometimes:

```text
powershell
```

for the same repository folder.

---

# 162. Avoid Reserved Names

Do not use Windows-reserved filenames such as:

```text
CON
PRN
AUX
NUL
COM1
LPT1
```

Generated file naming should sanitize such values.

---

# 163. User-Generated Names

User-created titles such as ticket subjects and KB titles do not need to follow source-code conventions.

However, when used to create filenames:

```text
sanitize
validate
normalize
```

before filesystem use.

---

# 164. Stable Names vs Display Names

Maintain separation between:

```text
stable identifier
```

and:

```text
editable display name
```

Example:

```text
command ID:
ticket.new

visible label:
New Ticket
```

The display label can change without breaking integrations.

---

# 165. Naming and Localization

Internal identifiers should not depend on translated UI text.

Bad:

```text
if button_label == "Nouveau billet"
```

Better:

```text
command_id == "ticket.new"
```

This preserves future bilingual support.

---

# 166. Naming and Searchability

Names should make repository-wide search effective.

Example:

```text
PowerShellGateway
```

is easier to search than:

```text
PSG
```

Avoid abbreviations that hide architectural roles.

---

# 167. Naming and Refactoring

When a component's responsibility changes significantly, rename it.

Do not preserve a misleading name merely to avoid refactoring.

A wrong name creates permanent confusion.

---

# 168. Renaming Public Contracts

Stable IDs, database columns, migration names, API contracts, and external references require more caution.

Renaming these may require:

- migration
- compatibility handling
- documentation
- tests

---

# 169. Do Not Rename Database History

Applied migration filenames should not be casually renamed after release.

Migration history is part of schema evolution.

---

# 170. Do Not Renumber Requirements

Published requirement and feature IDs should remain stable.

Gaps are acceptable.

Changing IDs creates broken references.

---

# 171. Naming Review Questions

Before accepting a name, ask:

1. What does this component do?
2. Does the name describe that responsibility?
3. Is the same concept named differently elsewhere?
4. Is the abbreviation necessary?
5. Does the name follow the technology convention?
6. Could the name be confused with another layer?
7. Will this name still make sense six months later?
8. Is it easy to search for?

---

# 172. Examples Across Layers

For the Ticket domain:

```text
Database table
→ tickets

Database PK
→ ticket_id

Python entity
→ Ticket

Repository
→ TicketRepository

Service
→ TicketService

GUI view
→ TicketView

Test module
→ test_ticket_service.py

Command ID
→ ticket.new
```

The names differ according to language conventions while preserving the same domain vocabulary.

---

# 173. PowerShell Example

DNS diagnostic:

```text
File
→ Test-DnsHealth.ps1

PowerShell function
→ Test-F7HubDnsHealth

Registry display name
→ Test DNS Health

Internal action ID
→ diagnostic.dns.health
```

Each name serves a different boundary.

---

# 174. Diagnostic Example

```text
Python entity
→ DiagnosticSession

SQLite table
→ diagnostic_sessions

Primary key
→ diagnostic_session_id

Python service
→ DiagnosticService

GUI
→ DiagnosticView

Event
→ DiagnosticCompleted
```

---

# 175. Knowledge Base Example

```text
Python entity
→ KnowledgeArticle

SQLite table
→ knowledge_articles

Primary key
→ knowledge_article_id

Repository
→ KnowledgeRepository

Service
→ KnowledgeService

GUI
→ KnowledgeView

Search provider
→ KnowledgeSearchProvider
```

---

# 176. Script Execution Example

```text
Python entity / result
→ ScriptExecution

SQLite table
→ script_executions

Primary key
→ script_execution_id

Service
→ ScriptService

PowerShell gateway
→ PowerShellGateway

Event
→ ScriptExecutionFinished
```

---

# 177. Naming Anti-Patterns

Avoid structures such as:

```text
Python\
├── Helpers\
├── Managers\
├── Misc\
└── Common\
```

when actual responsibilities can be expressed as:

```text
services
repositories
infrastructure
diagnostics
search
```

---

# 178. Bad vs Better Examples

Bad:

```text
DataManager
```

Better:

```text
TicketRepository
```

Bad:

```text
ProcessThing
```

Better:

```text
PowerShellGateway
```

Bad:

```text
doStuff()
```

Better:

```text
execute_registered_script()
```

Bad:

```text
final_database.db
```

Better:

```text
f7hub_dev.db
```

---

# 179. Naming Should Expose Architecture

A developer should be able to infer:

```text
TicketRepository
```

belongs to persistence,

while:

```text
TicketService
```

belongs to application workflows,

and:

```text
TicketView
```

belongs to presentation.

Names reinforce architectural boundaries.

---

# 180. Naming Should Not Fake Architecture

Do not append architectural words to a class merely to make it appear structured.

Example:

```text
TicketService
```

should actually be a service.

A class that only formats text should not be called:

```text
TicketService
```

---

# 181. Current Naming Status

Repository inspection on 2026-09-03 found the first Python SQLite infrastructure implementation. Its modules, classes, functions, variables, migration filenames and tests follow the conventions in this document. Other application areas remain unimplemented.

```text
SQLite infrastructure naming compliance: PASS
Remaining application naming compliance: PLANNED
```

This document defines the intended naming standard.

Existing implementation should be reviewed before large-scale renaming.

---

# 182. Renaming Existing Code

When implementation begins or existing code is inspected:

```text
SEARCH
→ IDENTIFY INCONSISTENCIES
→ DETERMINE IMPACT
→ RENAME SAFELY
→ TEST
```

Avoid mass renaming merely for cosmetic consistency if it risks breaking working functionality.

---

# 183. Naming Completion Checklist

Before adding a significant new component:

```text
[ ] Uses canonical F7Hub domain vocabulary
[ ] Follows language-specific naming style
[ ] Clearly expresses responsibility
[ ] Avoids unnecessary abbreviation
[ ] Avoids vague Manager/Helper/Misc naming
[ ] Does not duplicate an existing component name
[ ] Stable identifiers are separated from display labels
[ ] Database identifiers use snake_case
[ ] Tests follow test naming conventions
[ ] Documentation references match canonical spelling
```

---

# 184. Golden Naming Rules

1. Use `F7Hub` as the canonical product name.
2. Use consistent domain vocabulary.
3. Prefer clear names over short names.
4. Avoid unnecessary abbreviations.
5. Python modules and functions use `snake_case`.
6. Python classes use `PascalCase`.
7. Python constants use `UPPER_SNAKE_CASE`.
8. PowerShell uses `Verb-Noun`.
9. AutoHotkey v2 functions/classes use clear PascalCase naming.
10. SQLite identifiers use `snake_case`.
11. Entity tables use plural nouns.
12. Primary keys use descriptive `<entity>_id` names.
13. Foreign key names should match referenced key names.
14. Commands use stable `domain.action` identifiers.
15. Tests describe behavior.
16. Migrations have sortable numeric prefixes.
17. Stable internal identifiers are separate from display labels.
18. Avoid `Manager`, `Helper`, `Misc`, and `Utils` unless genuinely appropriate.
19. Do not use filenames such as `final`, `new`, or `v2` as substitutes for version control.
20. Rename components when their names no longer match their responsibility.

---

# 185. Final Naming Model

F7Hub naming should make architecture visible.

```text
Domain concept
     ↓
Technology convention
     ↓
Clear responsibility
     ↓
Predictable name
```

Example:

```text
Ticket

SQLite
→ tickets
→ ticket_id

Python
→ Ticket
→ TicketRepository
→ TicketService
→ TicketView

Commands
→ ticket.new

Tests
→ test_ticket_service.py
```

The guiding principle is:

> A good F7Hub name should tell a developer what something represents, what responsibility it owns, and where it belongs before they need to open the file.
