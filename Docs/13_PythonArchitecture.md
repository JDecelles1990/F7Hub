# F7Hub Python Architecture

> Document: `Docs/13_PythonArchitecture.md`  
> Project: F7Hub  
> Technology: Python + PyQt6  
> Purpose: Define the internal Python architecture of F7Hub, including application startup, GUI composition, services, domain logic, repositories, infrastructure, integrations, background execution, state management, diagnostics, search, AI boundaries, and testing.  
> Related Documents: `04_UserWorkflows.md`, `05_GUI.md`, `06_SystemArchitecture.md`, `07_Database.md`, `10_FolderStructure.md`, `11_AHKArchitecture.md`, `12_PowerShellArchitecture.md`

---

# 1. Purpose

This document defines the Python architecture for F7Hub.

It answers:

> How should the primary F7Hub application be structured internally?

Python is responsible for:

- application startup
- PyQt6 GUI
- application services
- domain logic
- repository coordination
- SQLite access
- PowerShell execution orchestration
- diagnostic workflows
- universal search
- AI integration boundaries
- external integration gateways
- workspace management
- settings
- reporting coordination
- application state
- background execution

Python is the primary application technology for F7Hub.

---

# 2. Technology Role

The main application stack is:

```text
Python
+
PyQt6
+
SQLite
```

Supporting technologies are:

```text
PowerShell
→ Windows and Microsoft administration

AutoHotkey v2
→ desktop automation, hotkeys, clipboard and launchers
```

Python coordinates the application-level workflow between these systems.

---

# 3. Architectural Style

F7Hub should initially use a:

```text
Modular Monolith
```

with layered boundaries.

Preferred architecture:

```text
GUI
 ↓
Application Services
 ↓
Domain Logic
 ↓
Repositories / Gateways
 ↓
Infrastructure
```

This gives F7Hub strong separation without introducing unnecessary distributed-system complexity.

---

# 4. Main Architecture

```text
PyQt6 GUI
    │
    ▼
Application Services
    │
    ▼
Domain Logic
    │
    ├───────────────┐
    ▼               ▼
Repositories      Gateways
    │               │
    ▼               ▼
SQLite        PowerShell / APIs / Filesystem
```

The GUI should not bypass the service layer.

---

# 5. Canonical Python Structure

Approved structure:

```text
Python\
└── f7hub\
    ├── app\
    ├── gui\
    ├── services\
    ├── domain\
    ├── repositories\
    ├── infrastructure\
    ├── integrations\
    ├── search\
    ├── diagnostics\
    └── utils\
```

Additional folders should be created only when justified.

---

# 6. Package Root

Primary Python package:

```text
Python\f7hub\
```

This package contains the main F7Hub application implementation.

The package should not become a flat collection of unrelated files.

---

# 7. Application Entry Point

F7Hub should have one clear application entry point.

Potential future example:

```text
Python\f7hub\__main__.py
```

or:

```text
Python\f7hub\app\main.py
```

The final entry-point convention should be standardized before implementation.

---

# 8. Startup Responsibility

The entry point should remain thin.

Conceptually:

```text
Start Process
    ↓
Load Configuration
    ↓
Initialize Logging
    ↓
Initialize Database
    ↓
Run Migrations
    ↓
Initialize Services
    ↓
Register Commands
    ↓
Initialize Integrations
    ↓
Create QApplication
    ↓
Create Main Window
    ↓
Restore Workspace
    ↓
Enter Event Loop
```

Business logic should not accumulate inside the entry point.

---

# 9. app Package

Folder:

```text
Python\f7hub\app\
```

Purpose:

Coordinate application lifecycle and global application concerns.

Potential responsibilities:

- bootstrap
- dependency construction
- application context
- command registry
- startup
- shutdown
- global lifecycle events

---

# 10. Dependency Construction

Dependencies should be constructed centrally.

Conceptually:

```text
Database Connection
      ↓
Repositories
      ↓
Services
      ↓
GUI Controllers / Views
```

Avoid constructing repositories or database connections independently inside random widgets.

---

# 11. Dependency Injection

F7Hub does not require a complex dependency-injection framework initially.

Preferred:

```python
ticket_repository = TicketRepository(db)
ticket_service = TicketService(ticket_repository)
ticket_view = TicketView(ticket_service)
```

Explicit construction is easier to understand and test.

A DI framework should only be introduced if complexity later justifies it.

---

# 12. Application Context

A small application context may hold stable global service references.

Potential contents:

```text
settings
logging
database
command registry
workspace manager
integration registry
```

Avoid turning the context into a global container containing every object in the application.

---

# 13. gui Package

Folder:

```text
Python\f7hub\gui\
```

Purpose:

Implement the PyQt6 interface described in `05_GUI.md`.

Potential structure:

```text
gui\
├── windows\
├── docks\
├── widgets\
├── dialogs\
├── models\
├── delegates\
├── controllers\
└── resources\
```

Create these subfolders only when implementation requires them.

---

# 14. Main Window

The main GUI shell should likely use:

```python
QMainWindow
```

because F7Hub requires:

- menu bar
- toolbar
- dockable panels
- status bar
- central workspace
- persistent layout

This matches the VS Code-like workspace direction.

---

# 15. Main Window Responsibilities

The main window may own:

- main navigation
- dock containers
- central workspace container
- status bar
- menu integration
- toolbar integration
- window geometry
- layout restoration

It should not own:

- raw SQL
- PowerShell command creation
- Microsoft authentication logic
- domain validation
- migration logic

---

# 16. Dockable Panels

PyQt6 dockable areas should use:

```python
QDockWidget
```

where appropriate.

Potential panels:

```text
Navigation
Context
AI Assistant
PowerShell Output
Logs
Activity
Search
```

Docking behavior should remain consistent across workspaces.

---

# 17. Central Workspace

The main workspace may use a controlled stack or tab model.

Potential components:

```text
Dashboard
Ticket Center
Knowledge Base
Search
Script Library
Diagnostics
Companies
Contacts
Settings
Reports
```

A feature workspace should be treated as a cohesive view rather than a random collection of widgets.

---

# 18. GUI Component Rule

A PyQt6 widget should primarily handle:

- presentation
- user interaction
- input collection
- display state
- signal emission

It should delegate application work to services.

---

# 19. GUI-to-Service Flow

Preferred:

```text
Button Click
    ↓
GUI Handler
    ↓
Service Method
    ↓
Domain / Repository / Gateway
    ↓
Result
    ↓
GUI Update
```

Avoid:

```text
Button Click
    ↓
SQL Query
```

or:

```text
Button Click
    ↓
Raw PowerShell String
```

---

# 20. Controllers

Controllers may be used where GUI logic becomes complex.

Potential responsibilities:

- coordinate view and service
- translate service results into view state
- manage selections
- coordinate multi-widget workflows

Do not introduce controllers everywhere automatically.

Simple views may call application services directly if the boundary remains clean.

---

# 21. Qt Signals and Slots

Signals and slots should be used for UI-level event communication.

Examples:

```text
ticket_selected
search_requested
diagnostic_started
workspace_changed
script_finished
```

Signals should not become an invisible application-wide message bus.

---

# 22. Signal Design

Signals should:

- have clear ownership
- use predictable names
- carry minimal required data
- avoid circular chains
- avoid hidden business logic

Prefer direct service calls for normal application operations.

---

# 23. Models

Qt models should be used where data presentation benefits from Qt's model/view architecture.

Potential examples:

```text
TicketTableModel
KnowledgeArticleModel
SearchResultsModel
ScriptListModel
```

---

# 24. Qt Model/View Architecture

For large lists and tables, prefer:

```text
QAbstractTableModel
QAbstractListModel
```

over manually inserting thousands of individual widgets.

Benefits:

- performance
- separation
- sorting
- filtering
- reuse
- testing

---

# 25. Table Views

Potential use:

```python
QTableView
```

for:

- ticket queue
- contacts
- companies
- scripts
- logs
- report data

Do not use database tables as GUI models directly.

The application model should transform repository data into presentation data.

---

# 26. GUI State

GUI state includes:

- selected ticket
- active workspace
- visible panels
- active tab
- filter settings
- window geometry

GUI state is not the same as persistent business data.

---

# 27. Workspace State

Workspace state may include:

```text
dock layout
panel visibility
active workspace
splitter positions
geometry
```

Qt-generated state may be stored as controlled opaque application state where appropriate.

Do not normalize GUI layout into many database tables unless queryability is actually needed.

---

# 28. services Package

Folder:

```text
Python\f7hub\services\
```

Purpose:

Implement application use cases.

Potential services:

```text
TicketService
CompanyService
ContactService
KnowledgeService
SearchService
ScriptService
PowerShellService
DiagnosticService
ClipboardService
PromptService
AIService
WorkspaceService
SettingsService
ReportService
```

---

# 29. Service Responsibility

Services answer:

> What does the application need to accomplish?

Examples:

```python
ticket_service.create_ticket(...)
ticket_service.add_note(...)
knowledge_service.search_articles(...)
diagnostic_service.start_session(...)
script_service.execute_registered_script(...)
```

Services coordinate operations across repositories and gateways.

---

# 30. Service Boundary

Services may:

- validate workflow-level input
- coordinate repositories
- coordinate external gateways
- enforce application rules
- manage transactions
- return structured results

Services should not contain PyQt6-specific code.

---

# 31. Domain Package

Folder:

```text
Python\f7hub\domain\
```

Purpose:

Represent stable F7Hub concepts and rules.

Potential contents:

```text
entities
value objects
enums
validation
domain exceptions
workflow rules
```

Domain code should remain usable without PyQt6.

---

# 32. Domain Entities

Potential examples:

```text
Ticket
Company
Contact
KnowledgeArticle
ScriptDefinition
DiagnosticWorkflow
DiagnosticSession
```

These are application concepts, not necessarily one-to-one mirrors of SQLite rows.

---

# 33. Domain Model Rule

Avoid turning every database table into an automatic Python class if no application value exists.

Model domain concepts where they clarify behavior.

Junction tables and internal infrastructure tables may not require full domain objects.

---

# 34. Dataclasses

Python dataclasses may be useful for simple domain data.

Example:

```python
from dataclasses import dataclass

@dataclass
class Ticket:
    id: int | None
    subject: str
    description: str
    status: str
```

Exact models should be created only after the schema is approved.

---

# 35. Enums

Enums may represent stable application states.

Examples:

```text
TicketStatus
ScriptRisk
ExecutionStatus
DiagnosticStepType
```

Avoid duplicating lookup values across code and database without a synchronization strategy.

---

# 36. Validation

Validation should exist at appropriate boundaries.

Possible layers:

```text
GUI validation
→ user feedback

Service validation
→ workflow requirements

Domain validation
→ invariant enforcement

Database constraints
→ final integrity protection
```

Do not rely on GUI validation alone.

---

# 37. Domain Exceptions

Use meaningful exceptions where appropriate.

Examples:

```text
TicketNotFoundError
InvalidDiagnosticStateError
ScriptNotRegisteredError
IntegrationUnavailableError
```

Avoid using generic `Exception` for every expected application failure.

---

# 38. repositories Package

Folder:

```text
Python\f7hub\repositories\
```

Purpose:

Provide persistence boundaries for SQLite.

Potential repositories:

```text
CompanyRepository
ContactRepository
TicketRepository
KnowledgeRepository
ScriptRepository
DiagnosticRepository
SettingsRepository
AuditRepository
```

---

# 39. Repository Responsibility

Repositories handle:

- SQL execution
- parameter binding
- persistence mapping
- retrieval
- inserts
- updates
- transactional persistence where appropriate

They should not own GUI logic.

---

# 40. Repository Principle

Preferred:

```text
Service
   ↓
Repository
   ↓
SQLite
```

Avoid:

```text
Widget
 ↓
sqlite3.execute(...)
```

---

# 41. SQL Placement

SQL may live:

- inside small repository methods
- in centralized query modules
- in external SQL files where complexity justifies it

Do not duplicate the same query in several places.

---

# 42. Parameterized Queries

All dynamic values must use parameterized queries.

Example:

```python
cursor.execute(
    "SELECT * FROM tickets WHERE ticket_id = ?",
    (ticket_id,)
)
```

Avoid SQL string interpolation.

---

# 43. Repository Return Values

Repositories should return structured Python data.

Potential forms:

- domain entities
- dataclasses
- DTOs
- lightweight records

Avoid returning raw cursor objects to services.

---

# 44. DTOs

Data Transfer Objects may be useful when a service needs a specific projection.

Example:

```text
TicketSummary
TicketSearchResult
ScriptExecutionSummary
```

Do not create DTOs mechanically for every table.

---

# 45. Database Connection Ownership

Database connection creation should be centralized.

Potential infrastructure component:

```text
DatabaseManager
```

Responsibilities may include:

- connection creation
- foreign key enforcement
- transaction boundaries
- migration startup
- connection lifecycle

---

# 46. SQLite Connection

Each SQLite connection must enable:

```sql
PRAGMA foreign_keys = ON;
```

Other pragmas such as WAL mode should only be enabled after testing and documented justification.

---

# 47. Transaction Ownership

Transactions should usually be owned by the service or repository operation that represents one logical unit of work.

Example:

```text
Create Ticket
+
Initial Timeline Event
+
Initial Note
```

may need to succeed or fail together.

---

# 48. Migration Integration

Application startup should verify schema version before normal repository use.

Conceptually:

```text
Open Database
    ↓
Inspect Migration State
    ↓
Apply Approved Migrations
    ↓
Validate
    ↓
Start Application
```

Migration implementation must align with `07_Database.md` and `09_SQLSchema.md`.

---

# 49. infrastructure Package

Folder:

```text
Python\f7hub\infrastructure\
```

Purpose:

Implement technical capabilities.

Potential contents:

```text
database
filesystem
logging
process execution
configuration
serialization
runtime paths
```

---

# 50. Infrastructure Rule

Infrastructure answers:

> How does the application technically perform this operation?

Services answer:

> Why and when should the application perform it?

---

# 51. PowerShell Gateway

A key infrastructure component will be the PowerShell gateway.

Conceptual class:

```text
PowerShellGateway
```

Responsibilities:

- locate `pwsh.exe`
- construct safe argument lists
- execute known scripts
- capture stdout
- capture stderr
- capture exit code
- apply timeout
- return process result

---

# 52. PowerShell Service

The service layer may contain:

```text
PowerShellService
```

Responsibilities:

- validate registered script
- validate parameters
- inspect privilege metadata
- request confirmation state
- call gateway
- validate structured output
- record execution

---

# 53. PowerShell Separation

```text
ScriptService / DiagnosticService
            ↓
PowerShellService
            ↓
PowerShellGateway
            ↓
pwsh.exe
```

This avoids letting every module independently launch PowerShell.

---

# 54. Subprocess Safety

Python should use controlled subprocess execution.

Prefer:

```python
subprocess.run(
    args,
    shell=False,
    capture_output=True,
    text=True,
    timeout=...
)
```

or an appropriate non-blocking equivalent.

Avoid:

```python
shell=True
```

unless there is a specific reviewed requirement.

---

# 55. Command Arguments

Construct commands as argument arrays.

Preferred:

```python
[
    "pwsh.exe",
    "-NoProfile",
    "-File",
    script_path,
    "-Hostname",
    hostname
]
```

Avoid building one giant shell string.

---

# 56. Background Execution

Long-running work must not block the PyQt6 event loop.

Examples:

- PowerShell execution
- Microsoft Graph calls
- database-heavy reports
- filesystem indexing
- AI requests
- network operations

---

# 57. Qt Background Workers

Potential implementation options include:

```text
QThread
QThreadPool
QRunnable
```

The simplest suitable mechanism should be used.

Do not introduce Python multiprocessing unless justified.

---

# 58. Worker Responsibilities

Background workers should:

- execute blocking work
- report progress
- return structured results
- report errors
- support cancellation where safe

GUI updates must occur on the GUI thread.

---

# 59. Cancellation

Cancellation behavior must be explicit.

Operations may be:

```text
CANCELLABLE
NOT_CANCELLABLE
BEST_EFFORT
```

Do not claim a remote operation was cancelled if it already completed.

---

# 60. integrations Package

Folder:

```text
Python\f7hub\integrations\
```

Purpose:

Contain gateways/adapters for external systems.

Potential integrations:

```text
Microsoft Graph
HaloPSA
NinjaOne
OpenAI / AI providers
Microsoft Learn
```

Create provider folders only when implemented.

---

# 61. Integration Gateway Pattern

Preferred:

```text
Application Service
        ↓
Integration Gateway Interface
        ↓
Provider Adapter
        ↓
External Service
```

This reduces provider-specific logic inside application services.

---

# 62. Microsoft Integration Boundary

PowerShell may perform many Microsoft administration operations.

Python may also interact directly with APIs where that provides a clearer architecture.

Decision rule:

```text
PowerShell
→ strong administrative cmdlet workflow

Python API client
→ application-native structured integration

Either
→ choose simplest maintainable option
```

Do not duplicate the same integration path unnecessarily.

---

# 63. External Failure Isolation

External-service failures should not crash F7Hub.

Examples:

```text
Graph unavailable
→ Ticket Center still works

AI unavailable
→ KB and Search still work

HaloPSA unavailable
→ local ticket context remains usable
```

Local functionality should degrade gracefully.

---

# 64. search Package

Folder:

```text
Python\f7hub\search\
```

Purpose:

Implement universal search orchestration.

Potential structure:

```text
query normalization
search providers
ranking
filters
FTS adapter
result models
```

---

# 65. Search Service

Potential flow:

```text
User Query
    ↓
SearchService
    ↓
Normalize Query
    ↓
Search Providers
    ↓
SQLite / FTS
    ↓
Rank Results
    ↓
Return Unified Results
```

---

# 66. Search Providers

Potential providers:

```text
TicketSearchProvider
CompanySearchProvider
ContactSearchProvider
KnowledgeSearchProvider
ScriptSearchProvider
PromptSearchProvider
```

Each provider should search its own domain.

---

# 67. Search Result Model

A unified search result may conceptually contain:

```text
entity_type
entity_id
title
summary
score
action
```

The exact schema should be defined during implementation.

---

# 68. FTS5

FTS5 should be accessed through repository/search infrastructure.

The GUI should never interact with FTS tables directly.

Relational records remain the source of truth.

---

# 69. Search Ranking

Initial ranking should be deterministic.

Possible signals:

```text
exact match
prefix match
FTS relevance
recency
favorite
usage
entity type
```

AI ranking should not be required for basic search.

---

# 70. diagnostics Package

Folder:

```text
Python\f7hub\diagnostics\
```

Purpose:

Implement the F7Hub Diagnostic Engine.

Potential components:

```text
workflow definitions
step evaluation
condition evaluation
session state
response validation
script coordination
result interpretation
```

---

# 71. Diagnostic Engine Flow

```text
Ticket / Issue
      ↓
Select Workflow
      ↓
Start Session
      ↓
Load Step
      ↓
Question / Condition / Script
      ↓
Store Response / Result
      ↓
Evaluate Next Step
      ↓
Repeat
      ↓
Completion
```

---

# 72. Diagnostic Workflow Model

Potential domain concepts:

```text
DiagnosticWorkflow
DiagnosticStep
DiagnosticCondition
DiagnosticSession
DiagnosticResponse
DiagnosticResult
```

These should align with `08_ERD.md`.

---

# 73. Diagnostic Step Types

Potential step types:

```text
QUESTION
INSTRUCTION
CONDITION
SCRIPT
RESULT
```

The workflow engine should operate on explicit types.

---

# 74. Diagnostic State

The current diagnostic session should track:

```text
workflow
current step
responses
results
status
related ticket
```

Persistent session history belongs in SQLite.

---

# 75. Diagnostic Condition Evaluation

Conditions should be deterministic.

Example:

```text
IF response == "No"
THEN next_step = 7
```

Avoid requiring AI to determine normal workflow branching.

---

# 76. Diagnostic Script Execution

Script steps should reference registered scripts.

Preferred:

```text
Diagnostic Step
     ↓
Script ID
     ↓
ScriptService
     ↓
PowerShellService
```

Do not embed arbitrary PowerShell inside workflow definitions.

---

# 77. Dynamic Diagnostic Forms

PyQt6 diagnostic forms may be generated from workflow step definitions.

Example:

```text
QUESTION / text
→ QLineEdit

QUESTION / boolean
→ Yes / No controls

QUESTION / selection
→ QComboBox

INSTRUCTION
→ read-only instruction widget
```

Exact widget design belongs in GUI implementation.

---

# 78. Prompt Service

The application may include:

```text
PromptService
```

Responsibilities:

- load prompt templates
- validate variables
- resolve context
- render prompt
- preserve version/context metadata

Prompt rendering should be deterministic before AI submission.

---

# 79. AI Service

Potential service:

```text
AIService
```

Responsibilities:

- receive approved context
- apply privacy filtering
- call provider gateway
- validate provider response
- return structured application result

AIService must not directly execute privileged actions.

---

# 80. AI Architecture

Preferred:

```text
Ticket / KB / Diagnostic Context
          ↓
Context Builder
          ↓
Privacy / Data Filter
          ↓
AIService
          ↓
Provider Gateway
          ↓
AI Provider
          ↓
Validation
          ↓
Technician Review
```

---

# 81. AI Context Builder

The context builder should select only information required for the task.

Avoid sending entire database records or unrelated ticket history by default.

---

# 82. AI Provider Independence

Application services should not depend directly on one provider's SDK everywhere.

Preferred:

```text
AIService
    ↓
AIProvider interface
    ↓
Specific provider adapter
```

This makes providers replaceable.

---

# 83. AI Output Validation

AI output should be treated as untrusted.

If structured output is expected:

- parse
- validate schema
- validate values
- reject malformed responses
- present safely

---

# 84. AI Action Boundary

AI may recommend:

```text
KB article
diagnostic
script
next troubleshooting step
ticket summary
resolution draft
```

AI must not directly:

```text
run PowerShell
modify tenant settings
delete records
execute shell commands
```

without explicit application-controlled review and approval.

---

# 85. Configuration

Python should own primary application configuration loading.

Potential configuration sources:

```text
Config\Defaults\
Config\Templates\
runtime user settings
environment variables where appropriate
```

Configuration should be validated.

---

# 86. Configuration Model

Use typed or validated configuration objects where practical.

Potential example:

```text
AppSettings
DatabaseSettings
PowerShellSettings
IntegrationSettings
UISettings
```

Do not pass raw dictionaries through the entire application if clear models would improve safety.

---

# 87. Secrets

Secrets must remain separate from ordinary configuration.

Never store:

```text
API keys
passwords
tokens
private keys
```

inside committed JSON, YAML, INI, or Python source.

---

# 88. Settings Service

Potential:

```text
SettingsService
```

Responsibilities:

- retrieve user settings
- validate changes
- persist approved settings
- expose defaults

The GUI should not know how settings are physically stored.

---

# 89. Logging

Python should coordinate application-wide logging.

Potential categories:

```text
application
database
PowerShell execution
integration
diagnostic
error
```

Avoid creating a different logging system for each feature.

---

# 90. Python Logging

Use Python's standard:

```python
logging
```

unless a later requirement justifies another framework.

Potential configuration:

```text
console handler
file handler
rotating handler
structured fields where useful
```

---

# 91. Logger Naming

Use module-based loggers.

Example:

```python
logger = logging.getLogger(__name__)
```

This preserves source context.

---

# 92. Logging Sensitive Data

Never log secrets.

Be cautious with:

- clipboard contents
- ticket descriptions
- tokens
- Graph responses
- AI context
- PowerShell parameters

Logging should be useful without becoming a second uncontrolled data store.

---

# 93. Audit vs Logging

Application logs answer:

> What happened technically?

Audit records answer:

> What significant user or administrative action occurred?

They should remain separate concepts.

---

# 94. Error Architecture

Errors should move through layers cleanly.

Example:

```text
SQLite error
    ↓
Repository exception
    ↓
Service-level error
    ↓
GUI-safe message
```

The user should not see raw SQLite tracebacks during normal operation.

---

# 95. Technical Error Detail

Detailed errors may be written to logs.

The GUI may show:

```text
Could not save ticket.
```

with optional technical details available separately.

---

# 96. Exception Boundaries

Catch exceptions where the layer can meaningfully handle or translate them.

Avoid:

```python
try:
    ...
except Exception:
    pass
```

Silent failures are unacceptable.

---

# 97. Application Result Objects

For expected operational outcomes, structured result objects may be preferable to exceptions.

Example:

```text
success
message
data
warnings
errors
```

Use exceptions for exceptional conditions, not every validation failure.

---

# 98. Command Registry

F7Hub should eventually have a command registry.

Purpose:

Provide stable application actions for:

- menus
- command palette
- hotkeys
- AHK integration
- toolbar actions

Potential IDs:

```text
ticket.new
ticket.open
search.open
diagnostic.start
script.library
workspace.switch
```

---

# 99. Command Architecture

```text
Command Source
(menu / palette / AHK)
        ↓
Command Registry
        ↓
Validated Command
        ↓
Application Service
```

This reduces duplicated action logic.

---

# 100. Active Context

F7Hub may maintain an active application context.

Potential values:

```text
active ticket
active company
active contact
active diagnostic session
active workspace
```

This helps coordinate contextual tools.

---

# 101. Context Ownership

Context should be managed by a dedicated component rather than stored independently in every widget.

Potential:

```text
ContextService
```

or:

```text
ApplicationContext
```

Keep it simple.

---

# 102. Event Architecture

Some cross-feature events may be useful.

Examples:

```text
TicketUpdated
DiagnosticCompleted
KnowledgeArticleCreated
ScriptExecutionCompleted
```

However, do not introduce a complex event-bus architecture prematurely.

---

# 103. Event Decision Rule

Use direct service calls when:

```text
one component clearly owns the workflow
```

Use an event when:

```text
multiple independent listeners need to react
```

---

# 104. Reporting

Python may coordinate reporting even when PowerShell collects the raw information.

Conceptually:

```text
ReportService
     ↓
Repository / PowerShell / Integration
     ↓
Structured Data
     ↓
Formatter / Exporter
     ↓
Data\Exports
```

---

# 105. Export Formats

Potential:

```text
CSV
JSON
HTML
Markdown
PDF
```

PDF and advanced document output should be added only when required.

---

# 106. File Handling

Filesystem access should be centralized where possible.

Potential infrastructure component:

```text
FileService
```

or:

```text
FileSystemGateway
```

Responsibilities:

- resolve safe paths
- validate files
- copy attachments
- export files
- sanitize names

---

# 107. Attachments

Ticket attachment metadata belongs in SQLite.

Files themselves normally remain in the filesystem.

Preferred:

```text
Ticket
  ↓
Attachment Metadata
  ↓
Relative File Path
  ↓
Filesystem
```

---

# 108. Path Safety

Treat paths as untrusted input.

Validate:

- path traversal
- invalid characters
- unexpected network paths
- file existence
- allowed locations

Do not blindly concatenate user strings into filesystem paths.

---

# 109. Runtime Paths

Development root:

```text
C:\Dev\F7Hub\
```

Installed runtime should not depend permanently on this location.

Potential future runtime paths:

```text
%LOCALAPPDATA%\F7Hub\
```

A runtime path service may later resolve:

```text
database path
logs path
attachments path
cache path
exports path
```

---

# 110. utils Package

Folder:

```text
Python\f7hub\utils\
```

Purpose:

Contain genuinely generic small helpers.

Examples:

```text
datetime formatting
string normalization
safe identifier helpers
```

Avoid moving business logic into `utils` simply because multiple modules use it.

---

# 111. Utilities Rule

Before placing code in `utils`, ask:

> Does this belong to a specific domain, service, repository, or infrastructure component?

If yes, place it there instead.

---

# 112. Package Dependency Direction

Preferred:

```text
gui
 ↓
services
 ↓
domain
 ↓
repositories / infrastructure
```

Integrations are accessed through services/gateways.

Avoid reverse dependencies such as:

```text
domain
→ imports PyQt6
```

or:

```text
repositories
→ import GUI widgets
```

---

# 113. Domain Independence

The domain layer should not depend directly on:

- PyQt6
- SQLite
- PowerShell
- Microsoft Graph SDK
- AI SDK

This keeps core rules testable.

---

# 114. Repository Independence

Repositories should not depend on:

- GUI widgets
- PowerShell
- AI
- AHK

They exist to persist and retrieve application data.

---

# 115. GUI Independence from Infrastructure

Widgets should not directly know:

```text
database filenames
pwsh.exe path
Graph endpoint URLs
migration version
```

They should interact with application services.

---

# 116. Type Hints

Python code should use type hints where practical.

Example:

```python
def get_ticket(self, ticket_id: int) -> Ticket | None:
    ...
```

Benefits:

- clarity
- IDE support
- static analysis
- safer refactoring

---

# 117. Static Analysis

Potential future tools:

```text
ruff
mypy
pyright
```

The final toolchain should remain minimal.

Do not add overlapping tools without a reason.

---

# 118. Formatting

Python should eventually use one consistent formatter.

Potential:

```text
ruff format
```

or another approved formatter.

Do not manually maintain conflicting style conventions.

---

# 119. Naming

General Python naming should follow:

```text
snake_case
→ functions, variables, modules

PascalCase
→ classes

UPPER_CASE
→ constants
```

Final project-wide naming conventions belong in `15_NamingConventions.md`.

---

# 120. Imports

Prefer explicit imports.

Avoid wildcard imports:

```python
from module import *
```

except where a library explicitly requires them.

---

# 121. Circular Dependencies

Circular imports are a warning that subsystem responsibilities may be unclear.

Before solving them with import tricks, review architecture ownership.

---

# 122. Third-Party Dependencies

Each dependency should have a real purpose.

Potential major dependencies may include:

```text
PyQt6
```

Additional packages should be introduced only when justified.

---

# 123. Dependency Management

The final environment approach may use:

```text
requirements files
pyproject.toml
virtual environment
```

The exact packaging standard should be selected before substantial implementation.

Avoid maintaining several conflicting dependency files.

---

# 124. Virtual Environment

Development should use an isolated Python environment.

Potential:

```text
.venv\
```

This should not be committed to Git.

---

# 125. Python Version

The project should choose and document a supported Python version before implementation.

Until verified:

```text
Python version: NOT YET FINALIZED
```

The chosen version must support the selected PyQt6 release and other dependencies.

---

# 126. PyQt6 Version

The supported PyQt6 version should be pinned or constrained during implementation.

Until verified:

```text
PyQt6 version: NOT YET FINALIZED
```

---

# 127. Testing Architecture

Python testing should include:

```text
unit
integration
database
GUI
PowerShell integration
end-to-end
```

Use the smallest appropriate test level.

---

# 128. pytest

`pytest` is a strong candidate for Python tests.

Potential structure:

```text
Tests\
├── Unit\
├── Integration\
├── Database\
├── GUI\
└── Fixtures\
```

Final testing conventions belong in the testing skill/process.

---

# 129. Unit Tests

Unit tests should focus on:

- domain rules
- validation
- service logic
- search ranking
- diagnostic condition evaluation
- utility functions

They should not require live Microsoft services.

---

# 130. Repository Tests

Repository tests should use isolated SQLite databases.

Test:

- insert
- update
- delete behavior
- foreign keys
- constraints
- transactions
- not-found cases

---

# 131. Migration Tests

Migration tests should verify:

```text
empty DB
→ latest schema

previous schema
→ latest schema

constraints remain valid
```

Never test migrations only against the development database.

---

# 132. GUI Tests

GUI tests may cover:

- widget creation
- signals
- navigation
- validation
- major workflows
- state restoration

Avoid excessive pixel-perfect testing.

---

# 133. PowerShell Integration Tests

Test:

```text
known script
→ Python gateway
→ structured result
```

Failure cases should include:

- missing pwsh
- missing script
- timeout
- invalid JSON
- non-zero exit code

---

# 134. External Integration Tests

Live integration tests must be isolated from normal unit tests.

Potential marker:

```text
integration_live
```

They may require credentials and safe test environments.

---

# 135. Test Status

Use:

```text
PASS
FAIL
NOT RUN
BLOCKED
```

Never claim a test passed unless it was actually executed.

---

# 136. Mocking

Mock external boundaries where useful:

```text
Microsoft Graph
AI provider
PowerShell gateway
filesystem
```

Do not over-mock domain logic.

---

# 137. Test Fixtures

Fixtures should contain safe synthetic data.

Never use production ticket or customer data in committed tests.

---

# 138. Thread Safety

SQLite and GUI threading require deliberate handling.

Do not casually share:

- SQLite connection objects
- Qt widgets

across worker threads.

---

# 139. SQLite and Threads

Database connection ownership should be explicit.

Possible strategies:

```text
one connection per worker/thread
```

or a controlled database service.

The final strategy must be tested.

---

# 140. Qt Thread Rule

GUI widgets should be accessed only from the main GUI thread.

Background workers should emit signals or return results to the main thread.

---

# 141. Performance

Performance should be measured before introducing complexity.

Potential areas to watch:

- large ticket lists
- universal search
- FTS5
- log views
- PowerShell startup
- external APIs
- AI requests

---

# 142. Lazy Loading

Large datasets should not necessarily be loaded entirely at startup.

Potential approaches:

```text
pagination
incremental loading
filtered queries
lazy panels
```

Use only when actual volume requires it.

---

# 143. Caching

Caching may be useful for:

- external lookups
- search metadata
- expensive calculations

Cache should remain:

```text
regenerable
bounded
invalidatable
```

Do not treat cache as source of truth.

---

# 144. Search Debouncing

Universal search should avoid triggering expensive operations for every keystroke without control.

Possible GUI behavior:

```text
user types
↓
short debounce
↓
search
```

The exact delay should be tested for usability.

---

# 145. Startup Performance

Startup should initialize only what is required.

Avoid connecting to every external platform at launch.

Preferred:

```text
load local app
↓
start quickly
↓
connect external systems when needed
```

---

# 146. Integration Authentication Timing

Authentication should generally occur:

```text
when user invokes a feature requiring it
```

rather than forcing all integrations to authenticate during startup.

---

# 147. Graceful Degradation

F7Hub should remain useful when external services fail.

Example:

```text
AI unavailable
→ local search still works

Graph unavailable
→ local ticket notes still work

PowerShell unavailable
→ KB remains available
```

---

# 148. Plugin Architecture

Plugins are future scope.

Python should not build a complex plugin framework before real extension requirements exist.

When introduced, plugin architecture must define:

- metadata
- discovery
- loading
- permissions
- extension points
- version compatibility
- failure isolation

---

# 149. Plugin Isolation

A plugin failure should not crash the application where practical.

Plugins should not receive unrestricted database access by default.

---

# 150. Security

Python is responsible for enforcing important application security boundaries.

Examples:

- input validation
- safe subprocess execution
- path validation
- SQL parameterization
- AI review boundaries
- secret handling
- privilege awareness

---

# 151. Untrusted Input

Treat as untrusted:

```text
ticket text
clipboard
files
URLs
API responses
PowerShell output
AI output
user-entered paths
external identifiers
```

---

# 152. SQL Injection

Prevent through:

```text
parameterized queries
```

Do not build SQL by concatenating user input.

---

# 153. Command Injection

Prevent through:

```text
argument arrays
known executables
known scripts
validated values
shell=False
```

---

# 154. File Security

Before opening or processing files:

- validate path
- validate expected type where needed
- avoid automatic execution
- treat imported content as untrusted

---

# 155. Secret Management

No secrets in:

```text
Python source
Git
Docs
normal SQLite settings
plain-text Config files
```

A proper secret-storage approach should be selected when integrations require persistent credentials.

---

# 156. Authentication Boundaries

F7Hub should not automatically assume the technician has permission for an operation.

The application should surface:

- required role
- required authentication
- expected impact

---

# 157. Privileged Operations

Preferred:

```text
User requests action
      ↓
F7Hub validates target
      ↓
Risk / privilege displayed
      ↓
Explicit confirmation
      ↓
Gateway executes
      ↓
Result recorded
```

---

# 158. AI Safety Boundary

AI suggestions should never bypass services.

Avoid:

```text
AI response
→ subprocess.run()
```

or:

```text
AI response
→ SQL execute()
```

---

# 159. Documentation

Python architectural changes must update:

```text
13_PythonArchitecture.md
```

If they affect system architecture:

```text
06_SystemArchitecture.md
```

If they affect GUI:

```text
05_GUI.md
```

If they affect folders:

```text
10_FolderStructure.md
```

If they affect persistence:

```text
07_Database.md
08_ERD.md
09_SQLSchema.md
```

---

# 160. Initial Python Implementation Scope

Recommended early Python implementation sequence:

```text
SQLite connection
      ↓
Migration infrastructure
      ↓
Taxonomy / Company / Contact persistence
      ↓
Ticket repository and service
      ↓
Application bootstrap and PyQt6 shell
      ↓
Basic PyQt6 ticket workflow
      ↓
Tests
```

Each arrow represents a separate focused, tested slice. The SQLite connection and migration infrastructure slice was verified on 2026-09-03 with 28 isolated database tests. It does not include domain repositories or GUI work.

Together, the completed sequence validates the architectural path.

---

# 161. Why the Initial Slices Are Small

The early slices should eventually prove:

```text
GUI
↓
Service
↓
Repository
↓
SQLite
```

before implementing:

- AI
- plugins
- Microsoft Graph
- diagnostics
- advanced search

This gives F7Hub a tested architectural spine.

---

# 162. Second Python Slice

After basic ticket persistence works:

```text
Ticket notes
Ticket timeline
Ticket search
Company/contact context
```

---

# 163. Third Python Slice

Then:

```text
Knowledge Base
FTS5 search
Ticket-to-KB relationships
```

---

# 164. Fourth Python Slice

Then:

```text
Script registry
PowerShellGateway
structured PowerShell execution
execution history
```

---

# 165. Fifth Python Slice

Then:

```text
Diagnostic Engine
dynamic forms
workflow sessions
script integration
```

---

# 166. Later Slices

Later:

```text
AI
Microsoft Graph
Exchange Online
Intune
Defender
Plugins
advanced reporting
external PSA/RMM integrations
```

Each should remain independently testable.

---

# 167. Anti-Patterns

Avoid:

## Giant Main Window

All business logic lives in `MainWindow`.

## GUI-Owned SQL

Widgets execute SQLite queries.

## GUI-Owned PowerShell

Buttons construct shell commands.

## Repository Business Logic

Repositories decide ticket workflow.

## Python Monolith

Every subsystem is placed in one package/file.

## Utility Dumping Ground

Most shared code is put into `utils.py`.

## Hidden Global State

Services rely on mutable globals.

## Premature Frameworks

Dependency injection, event buses, ORMs, plugins and async frameworks are added before they are needed.

## Provider Coupling

Application services directly depend on one external vendor everywhere.

## AI Execution Bridge

AI output directly executes commands.

---

# 168. ORM Decision

F7Hub does not require an ORM by default.

SQLite access through explicit repositories may provide:

- clearer SQL learning
- predictable queries
- simpler migrations
- better understanding of relationships

An ORM should only be introduced if it provides a demonstrated benefit.

---

# 169. SQL Learning Value

Because F7Hub is also a learning project, explicit SQL and repository design can help develop practical understanding of:

- joins
- foreign keys
- transactions
- indexes
- query plans
- normalization

Abstraction should not hide these concepts unnecessarily.

---

# 170. PyQt6 Designer

Qt Designer may be used for selected interface layouts if useful.

However, F7Hub architecture should not depend on Designer-generated code owning application logic.

If `.ui` files are used:

```text
UI definition
↓
Python view/controller
↓
service
```

---

# 171. Generated UI Files

Avoid manually editing generated files if the build workflow regenerates them.

Document whether F7Hub uses:

```text
runtime .ui loading
```

or:

```text
compiled Python UI modules
```

before implementation.

---

# 172. Resource Management

Application resources such as icons should be centrally managed.

Potential source:

```text
Assets\Icons\
```

Avoid embedding absolute paths throughout widgets.

---

# 173. Theme Architecture

Themes should primarily affect presentation.

They should not change business behavior.

Potential future theme data:

```text
light
dark
system
```

Exact theme implementation belongs in GUI work.

---

# 174. Accessibility

PyQt6 implementation should consider:

- keyboard navigation
- focus order
- readable labels
- high-DPI support
- scalable layout
- clear status feedback

Do not rely only on color to communicate status.

---

# 175. Internationalization

F7Hub may eventually need bilingual UI support.

Do not hard-code architecture around a single language if translation becomes a requirement.

However, full localization infrastructure should not be added until justified.

---

# 176. Current Implementation Status

Repository inspection and tests on 2026-09-03 verified the SQLite infrastructure under `Python\f7hub\infrastructure\` and the company/contact persistence boundaries under `Python\f7hub\repositories\`. `CompanyRepository` and `ContactRepository` return frozen structured records and use parameterized SQL through configured SQLite connections. No GUI, application service, domain model, ticket repository or other business repository has been implemented.

```text
Python SQLite infrastructure: VERIFIED
CompanyRepository and ContactRepository: VERIFIED
Remaining Python application implementation: PLANNED
Isolated database tests: PASS — 69 tests
```

This verification does not prove that:

- PyQt6 is installed
- GUI or application bootstrap exists
- business repositories beyond companies and contacts exist
- services exist
- PowerShell integration exists
- tests outside the isolated database infrastructure suite pass

It defines intended architecture only.

---

# 177. Recommended Initial Package Scaffold

When Python implementation begins, an initial minimal package may be:

```text
Python\
└── f7hub\
    ├── __init__.py
    ├── __main__.py
    │
    ├── app\
    │   └── __init__.py
    │
    ├── gui\
    │   └── __init__.py
    │
    ├── services\
    │   └── __init__.py
    │
    ├── domain\
    │   └── __init__.py
    │
    ├── repositories\
    │   └── __init__.py
    │
    ├── infrastructure\
    │   └── __init__.py
    │
    └── utils\
        └── __init__.py
```

Do not populate every folder with speculative abstractions immediately.

---

# 178. Implementation Decision Rule

Before creating a Python class or module, ask:

1. What requirement does it satisfy?
2. Which layer owns it?
3. Does an existing component already perform this responsibility?
4. Does it depend in the correct architectural direction?
5. Can it be tested independently?
6. Does it introduce unnecessary abstraction?
7. Does documentation need updating?

---

# 179. Completion Checklist

A Python feature is complete when applicable:

```text
[ ] Requirement identified
[ ] Relevant docs inspected
[ ] Existing implementation searched
[ ] Correct architectural layer chosen
[ ] Input validated
[ ] Errors handled
[ ] Security reviewed
[ ] Database integrity preserved
[ ] Blocking work kept off GUI thread
[ ] Success path tested
[ ] Failure path tested
[ ] Documentation synchronized
```

---

# 180. Python Golden Rules

1. Python/PyQt6 is the primary F7Hub application.
2. GUI handles presentation, not persistence.
3. Services coordinate use cases.
4. Domain logic remains independent of PyQt6.
5. Repositories own SQLite access.
6. Infrastructure owns technical adapters.
7. PowerShell execution goes through one controlled gateway.
8. AutoHotkey remains the desktop automation layer.
9. Use explicit dependencies before complex DI frameworks.
10. Prefer a modular monolith.
11. Avoid premature microservices.
12. Use parameterized SQL.
13. Use safe subprocess argument lists.
14. Keep blocking operations off the GUI thread.
15. Treat external and AI data as untrusted.
16. Keep AI outside privileged execution paths.
17. Prefer deterministic diagnostics and search before AI enhancement.
18. Build small vertical slices.
19. Test failure paths.
20. Add abstractions only when they make the system easier to understand.

---

# 181. Final Architecture Summary

Python is the architectural center of F7Hub.

```text
                     PyQt6
                      GUI
                       │
                       ▼
                Application Services
                       │
            ┌──────────┼──────────┐
            │          │          │
            ▼          ▼          ▼
         Domain    Search /    Diagnostics
                    AI
            │          │          │
            └──────────┼──────────┘
                       ▼
             Repositories / Gateways
                 │             │
                 ▼             ▼
              SQLite       PowerShell
                                │
                                ▼
                         Windows / M365
```

AutoHotkey v2 remains alongside the application for:

```text
hotkeys
hotstrings
clipboard
launchers
desktop automation
```

The architectural responsibility is:

```text
PyQt6
→ presentation

Python Services
→ application workflows

Python Domain
→ business rules

Repositories
→ persistence

Infrastructure
→ technical implementation

PowerShell
→ administration and diagnostics

AutoHotkey v2
→ desktop productivity

SQLite
→ relational storage
```

The guiding principle is:

> Python should coordinate F7Hub without becoming a monolith. Each layer should have one understandable responsibility, and every feature should travel through clear boundaries from GUI to service to domain to persistence or external gateway.
