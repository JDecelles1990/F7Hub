# F7Hub System Architecture
>
> Document: Docs/06_SystemArchitecture.md
> Project: F7Hub
> Purpose: Define how F7Hub subsystems are organized, how components communicate, where responsibilities belong, and which architectural boundaries must be preserved.
> Scope: System-level architecture.
> Related Documents: 00_ProjectVision.md, 01_Project.md, 02_ProductRequirements.md, 05_GUI.md, 07_Database.md, 11_AHKArchitecture.md, 12_PowerShellArchitecture.md, 13_PythonArchitecture.md

# 1. Purpose

This document defines the high-level architecture of F7Hub.

It answers:

How do the components of F7Hub communicate and cooperate?

This document defines:

major system layers

subsystem boundaries

runtime responsibilities

communication patterns

dependency direction

database access rules

cross-language integration

PowerShell execution architecture

AutoHotkey integration

external integration boundaries

AI integration boundaries

plugin boundaries

search architecture

diagnostics architecture

logging and error propagation

startup and shutdown behavior

security boundaries

architectural constraints

Detailed implementation belongs in the subsystem-specific documents.

# 2. Architectural Goals

F7Hub architecture must optimize for:

understandability

modularity

maintainability

testability

security

controlled extensibility

clear responsibility boundaries

recoverability

local-first functionality

predictable cross-language communication

database integrity

incremental development

The system should remain understandable to:

the project author

future contributors

coding agents

reviewers

testers

# 3. Architectural Philosophy

F7Hub follows the principle:

Build the correct system, not the most code.

The architecture should avoid both extremes:

one giant monolithic application

excessive microservices or abstraction for a local desktop tool

F7Hub should use a modular monolith as its primary architectural style.

This means:

one primary desktop application

clearly separated modules

explicit internal interfaces

shared infrastructure where justified

no unnecessary network services between local modules

no hidden cross-module dependencies

# 4. Primary Architectural Model

The preferred dependency direction is:

┌──────────────────────────────────────┐
│                 GUI                  │
│            Python / PySide6          │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│       Application / Services         │
│                                      │
│ Tickets │ KB │ Search │ Diagnostics  │
│ Scripts │ AI │ Reports │ Settings    │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│            Domain Logic              │
│                                      │
│ Models │ Rules │ Validation │ State  │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│       Repositories / Gateways        │
│                                      │
│ DB │ PowerShell │ AHK │ APIs │ Files │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│          Infrastructure              │
│                                      │
│ SQLite │ OS │ External Services      │
└──────────────────────────────────────┘

Dependencies should generally flow downward.

Lower layers should not depend on GUI components.

# 5. Architectural Style

F7Hub should use a:

Modular layered desktop architecture

with domain-oriented modules.

Major principles:

modular monolith

dependency direction

separation of concerns

repositories for persistent data

services for application orchestration

domain logic independent from GUI

adapters/gateways for infrastructure

explicit cross-language contracts

event-driven communication where justified

no unnecessary service fragmentation

# 6. System Context

F7Hub operates between the technician and multiple local or remote systems.

                        ┌───────────────────────┐
                        │      Technician       │
                        └───────────┬───────────┘
                                    │
                                    ▼
                        ┌───────────────────────┐
                        │        F7Hub          │
                        │    Python / PySide6   │
                        └───────────┬───────────┘
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         │                          │                          │
         ▼                          ▼                          ▼
┌──────────────────┐     ┌────────────────────┐     ┌─────────────────────┐
│ Local Subsystems │     │ Microsoft Services │     │ External Platforms  │
│                  │     │                    │     │                     │
│ SQLite           │     │ Microsoft Graph    │     │ HaloPSA             │
│ PowerShell       │     │ Exchange Online    │     │ NinjaOne / RMM      │
│ AutoHotkey       │     │ Entra ID           │     │ AI Providers        │
│ Files            │     │ Intune             │     │ Documentation       │
│ Windows          │     │ Defender           │     │ Web Resources       │
└──────────────────┘     │ Teams              │     └─────────────────────┘
                         │ SharePoint          │
                         └────────────────────┘

F7Hub should remain functional when many external services are unavailable.

# 7. Major Subsystems

The major logical subsystems include:

Application Core
GUI
Tickets
Companies
Contacts
Knowledge Base
Search
Diagnostics
Script Library
PowerShell
AutoHotkey
Clipboard
Prompts
AI
Plugins
Reports
Settings
Logging
Database
External Integrations

Each subsystem must have an explicit responsibility.

# 8. Application Core

The Application Core coordinates the F7Hub runtime.

Responsibilities may include:

startup

dependency initialization

configuration loading

database initialization

service registration

module initialization

application state

shutdown

error routing

lifecycle management

The Application Core should not contain unrelated domain logic.

# 9. GUI Layer

The GUI is designed to be implemented primarily with Python and PySide6.

Responsibilities include:

rendering

navigation

user input

forms

dialogs

dockable panels

visual state

command palette

workspace layouts

output views

The GUI must not directly contain:

raw SQL

business rules

PowerShell command construction

authentication logic

migration logic

Instead:

GUI
 ↓
Application Service
 ↓
Repository / Gateway

# 10. Application Services Layer

Application services orchestrate user-facing use cases.

Examples:

TicketService
KnowledgeService
SearchService
DiagnosticService
ScriptService
PowerShellService
ClipboardService
PromptService
AIService
WorkspaceService
ReportService
SettingsService

Application services may coordinate multiple repositories or gateways.

Example:

TicketService
    │
    ├── TicketRepository
    ├── ContactRepository
    ├── CompanyRepository
    └── TimelineRepository

# 11. Domain Layer

The domain layer contains business concepts and rules.

Examples:

ticket state rules

diagnostic workflow logic

KB article lifecycle

validation

script risk classification

search result metadata

relationships

invariants

Domain logic should be testable without launching the GUI.

# 12. Repository Layer

Repositories provide controlled access to persistent data.

Examples:

TicketRepository
CompanyRepository
ContactRepository
KnowledgeRepository
ScriptRepository
DiagnosticRepository
PromptRepository
SettingsRepository
WorkspaceRepository

Repositories should:

use parameterized queries

encapsulate SQL

map records to domain objects

preserve transactions

handle database errors predictably

GUI code should not issue SQL directly.

# 13. Gateway Layer

Gateways provide controlled access to non-database infrastructure.

Examples:

PowerShellGateway
AutoHotkeyGateway
MicrosoftGraphGateway
HaloPSAGateway
AIGateway
FileSystemGateway
WindowsGateway

Gateways isolate:

external APIs

operating system calls

subprocesses

external applications

authentication

provider-specific behavior

# 14. Infrastructure Layer

Infrastructure includes:

SQLite

filesystem

PowerShell

AutoHotkey

Windows APIs

Microsoft APIs

external tools

network services

AI providers

Infrastructure should remain replaceable where practical.

The application should depend on abstractions rather than deeply embedding provider-specific behavior throughout the codebase.

# 15. Database Architecture Boundary

SQLite is the main persistent data layer.

The preferred path is:

GUI
 ↓
Application Service
 ↓
Repository
 ↓
SQLite

Not:

GUI
 ↓
Raw SQL

Database architecture is defined in more detail in:

07_Database.md

08_ERD.md

09_SQLSchema.md

# 16. Database Access Rules

All database access should follow these rules:

repositories own SQL access

parameterized queries are mandatory

foreign keys must be enabled

transactions must protect multi-step writes

migrations manage schema changes

destructive changes require review

SQL should not be duplicated throughout GUI code

business logic should not be hidden inside SQL without justification

indexes should be justified by query behavior

failures should propagate through controlled error handling

# 17. Database Connection Strategy

F7Hub should use a controlled connection strategy.

For the initial single-user desktop architecture:

one local SQLite database

application-managed connection lifecycle

explicit transaction boundaries

safe concurrency assumptions

no unnecessary connection pooling

The exact Python SQLite library and connection manager belong in 13_PythonArchitecture.md.

# 18. Database Migration Architecture

Schema evolution should follow:

Application Startup
       │
       ▼
Read Schema Version
       │
       ▼
Compare Required Version
       │
       ├── Current
       │      └── Continue
       │
       └── Outdated
              │
              ▼
         Run Migrations
              │
              ▼
         Validate Result
              │
        ┌─────┴─────┐
        │           │
      PASS         FAIL
        │           │
    Continue      Abort / Recover

Migrations should:

be versioned

be ordered

be testable

avoid silent data loss

record execution status where appropriate

# 19. PowerShell Architecture

PowerShell is an execution subsystem, not the primary application architecture.

Preferred flow:

GUI
 ↓
Application Service
 ↓
PowerShell Service
 ↓
PowerShell Gateway
 ↓
Script File
 ↓
pwsh.exe
 ↓
Structured Result
 ↓
Parser
 ↓
Application

Detailed rules belong in:

12_PowerShellArchitecture.md

# 20. PowerShell Execution Boundary

F7Hub should not dynamically construct arbitrary shell commands from untrusted text.

Preferred execution:

known script file

validated parameters

safe argument passing

known working directory

controlled timeout

captured stdout

captured stderr

captured exit code

Execution should be inspectable.

# 21. PowerShell Result Contract

Where possible, PowerShell scripts should return a structured result.

Conceptual example:

{
  "schemaVersion": 1,
  "operation": "Test-DnsHealth",
  "success": true,
  "status": "PASS",
  "message": "DNS resolution succeeded.",
  "data": {
    "hostname": "example.com",
    "resolved": true
  },
  "warnings": [],
  "errors": []
}

Structured output is preferred over parsing human-formatted terminal text.

# 22. PowerShell Script Storage

PowerShell scripts should generally remain stored under:

PowerShell\

The SQLite database may store:

script ID

path

description

category

tags

privilege level

risk

version

execution history

relationships

The database should not become the default storage location for entire PowerShell source files.

# 23. AutoHotkey Architecture

AutoHotkey v2 handles lightweight Windows desktop automation.

Preferred responsibilities:

global hotkeys

hotstrings

clipboard automation

text insertion

quick launch

application focusing

lightweight menus

Windows interaction

Detailed rules belong in:

11_AHKArchitecture.md

# 24. AutoHotkey Communication

AHK integration may occur through:

command-line invocation

local files

controlled IPC

process launching

structured messages

The exact IPC mechanism should be chosen only after a real requirement exists.

Do not introduce sockets, named pipes or custom protocol layers merely for architectural elegance.

# 25. Cross-Language Architecture

F7Hub includes:

Python

PowerShell

AutoHotkey v2

Cross-language communication must be explicit.

Preferred formats:

command-line arguments

JSON

structured stdout

files where justified

database records where appropriate

Avoid:

undocumented global state

fragile screen scraping

arbitrary text parsing

hidden shared temporary files

# 26. Cross-Language Contract Rule

Every important cross-language interaction should define:

Input
Output
Schema
Errors
Exit Codes
Timeout
Security Expectations
Version

This makes communication testable.

# 27. Diagnostic Engine Architecture

The diagnostic engine combines:

workflow definitions

conditions

questions

technician input

scripts

diagnostic results

decision logic

KB relationships

resolution guidance

Conceptual architecture:

Ticket Context
      │
      ▼
DiagnosticService
      │
      ▼
Workflow Definition
      │
      ▼
Current Step
      │
      ├── Question
      ├── Condition
      └── Script
      │
      ▼
Result
      │
      ▼
Rule Evaluation
      │
      ▼
Next Step

# 28. Diagnostic Workflow Separation

Diagnostic definitions should remain separate from PowerShell implementation.

Example:

Diagnostic Workflow
│
├── Step 1: Ask user question
│
├── Step 2: Evaluate condition
│
├── Step 3: Invoke script reference
│
└── Step 4: Evaluate result

The workflow should reference a script.

It should not embed large script bodies directly into the workflow definition.

# 29. Diagnostic Session Architecture

A diagnostic session represents one execution of a workflow.

Potential session data:

diagnostic session ID

ticket ID

workflow ID

start time

completion time

current state

answers

script results

warnings

final outcome

Persistent session data should be designed in the database documentation.

# 30. Knowledge Base Architecture

Knowledge should be accessed through a Knowledge Service.

Conceptual flow:

GUI
 ↓
KnowledgeService
 ↓
KnowledgeRepository
 ↓
SQLite

Searchable KB content may additionally use FTS5.

Knowledge relationships may include:

tickets

companies

technologies

scripts

diagnostic workflows

tags

# 31. Search Architecture

Search should become a shared platform capability.

Conceptual flow:

Search Box
   │
   ▼
SearchService
   │
   ▼
Query Normalizer
   │
   ▼
Search Providers
   │
   ├── Tickets
   ├── KB
   ├── Companies
   ├── Contacts
   ├── Scripts
   ├── Prompts
   └── Clipboard
   │
   ▼
Result Ranking
   │
   ▼
Unified Results

# 32. Search Provider Model

Each domain should provide search through a controlled interface rather than exposing internal SQL to the GUI.

Conceptual example:

SearchProvider
│
├── TicketSearchProvider
├── KnowledgeSearchProvider
├── CompanySearchProvider
├── ContactSearchProvider
└── ScriptSearchProvider

This allows search behavior to evolve independently.

# 33. Local Search First

Core search should work without AI.

AI may assist with:

query rewriting

semantic interpretation

result explanation

reranking

But deterministic local search should remain available.

# 34. Clipboard Architecture

Clipboard features may span Python and AutoHotkey.

Preferred division:

AutoHotkey
→ Windows clipboard interaction
→ hotkeys
→ quick transformations

Python
→ persistent history
→ organization
→ search
→ metadata
→ GUI

This avoids forcing either technology to own the entire subsystem.

# 35. AI Architecture

AI is an optional assistance layer.

Conceptual flow:

User / Ticket / Diagnostic Context
             │
             ▼
         AIService
             │
             ▼
       Context Builder
             │
             ▼
      Privacy Filter
             │
             ▼
        AI Gateway
             │
             ▼
       External Provider
             │
             ▼
         AI Result
             │
             ▼
      Validation / Review
             │
             ▼
            GUI

AI must not directly own administrative execution.

# 36. AI Execution Boundary

Prohibited architecture:

AI
 ↓
Run Arbitrary PowerShell

Preferred architecture:

AI Suggestion
      │
      ▼
Technician Review
      │
      ▼
Validated Action
      │
      ▼
PowerShellService

Technician control remains mandatory.

# 37. AI Context Architecture

The AI context builder may include explicitly selected:

ticket details

diagnostic results

KB content

scripts

company context

notes

prompt templates

Sensitive data should not automatically be sent to external AI providers.

# 38. External Integration Architecture

External systems should be accessed through gateways.

Example:

Application Service
      │
      ▼
Integration Gateway
      │
      ▼
External API / Platform

Examples:

MicrosoftGraphGateway
ExchangeGateway
HaloPSAGateway
NinjaGateway
AIGateway

Provider-specific details should not leak throughout the application.

# 39. Microsoft Graph Architecture

Where appropriate:

GUI
 ↓
Microsoft365Service
 ↓
MicrosoftGraphGateway
 ↓
Authentication
 ↓
Microsoft Graph API

Authentication and token management must be treated as infrastructure/security concerns.

# 40. External Integration Failure

External integrations should fail independently.

Example:

F7Hub Running
   │
   ├── SQLite          ✓
   ├── PowerShell      ✓
   ├── Microsoft Graph ✗
   └── AI              ✗

The application should remain usable for local functions.

# 41. Plugin Architecture

Plugin architecture is future-facing and must remain controlled.

Conceptual architecture:

Plugin Manager
     │
     ▼
Plugin Discovery
     │
     ▼
Metadata Validation
     │
     ▼
Compatibility Check
     │
     ▼
Permission Check
     │
     ▼
Load Plugin

Plugins should not receive unrestricted core access by default.

# 42. Plugin Interfaces

Potential plugin extension points may include:

GUI panels

search providers

diagnostic providers

integrations

reports

utility actions

Plugin extension points must be explicitly defined.

Plugins must not modify core database schema arbitrarily.

# 43. Plugin Failure Boundary

Optional plugin failure should not normally terminate F7Hub.

Preferred behavior:

Plugin Fails
    │
    ▼
Disable Plugin
    │
    ▼
Log Error
    │
    ▼
Notify User
    │
    ▼
Continue F7Hub

# 44. Settings Architecture

Settings should be accessed through a Settings Service.

Sources may include:

configuration files

SQLite

environment

runtime defaults

Different settings types may require different storage.

Secrets must not be treated as normal settings.

# 45. Configuration Architecture

Configuration should follow a layered model where useful:

Default Configuration
       │
       ▼
Application Configuration
       │
       ▼
User Configuration
       │
       ▼
Runtime Overrides

Exact precedence belongs in subsystem documentation.

# 46. Secrets Architecture

Secrets require a separate security mechanism.

Examples:

OAuth tokens

API keys

credentials

Secrets must not be stored:

directly in source

plain text in repository configuration

inside normal logs

inside documentation

A secure secrets design must be approved before persistent credential storage is introduced.

# 47. Logging Architecture

All major subsystems should route useful operational information through a shared logging service.

Conceptual flow:

Module
  │
  ▼
Logging Service
  │
  ├── Application Log
  ├── Error Log
  └── Diagnostic Log

Logging should include sufficient context without exposing sensitive data.

# 48. Logging Context

Useful logging context may include:

timestamp

subsystem

severity

operation

ticket ID

execution ID

plugin ID

error code

Sensitive information must be sanitized.

# 49. Error Architecture

Errors should propagate through structured layers.

Example:

SQLite Error
    │
    ▼
Repository Error
    │
    ▼
Service Error
    │
    ▼
User-Friendly Message

Raw low-level errors may be logged while the GUI presents understandable information.

# 50. Error Categories

Useful error categories may include:

ValidationError
DatabaseError
ConfigurationError
IntegrationError
PowerShellError
AuthenticationError
PluginError
FileSystemError
SecurityError

Exact Python exception architecture belongs in 13_PythonArchitecture.md.

# 51. Background Task Architecture

Long-running tasks must not freeze the GUI.

Examples:

PowerShell execution

network calls

Microsoft Graph

search indexing

AI requests

large reports

Conceptual flow:

GUI
 │
 ▼
Task Request
 │
 ▼
Worker / Background Task
 │
 ▼
Result / Error
 │
 ▼
GUI Update

Qt threading implementation belongs in 13_PythonArchitecture.md.

# 52. Cancellation Architecture

Long-running operations should support cancellation where technically safe.

Cancellation behavior must distinguish:

safely cancellable operations

operations that cannot safely be interrupted

operations already committed

The GUI must not claim cancellation if the underlying administrative action continued.

# 53. Event Architecture

F7Hub may use internal events or signals for loose coupling.

Examples:

TicketOpened
TicketUpdated
DiagnosticCompleted
ScriptExecuted
WorkspaceChanged
KnowledgeLinked
IntegrationStatusChanged

Events should not become a hidden substitute for clear service calls.

Use events when multiple components legitimately need notification.

# 54. State Management

Application state may include:

active workspace

active ticket

active company

active contact

selected module

running operation

current user settings

State ownership should be explicit.

Avoid duplicated copies of the same mutable state across unrelated components.

# 55. Active Context

F7Hub may maintain a shared active support context.

Conceptually:

ActiveContext
│
├── Ticket
├── Company
├── Contact
├── Workspace
└── Diagnostic Session

Modules may read appropriate context through defined interfaces.

Context must not become unrestricted mutable global state.

# 56. Application Startup Architecture

Preferred startup sequence:

Process Start
    │
    ▼
Load Bootstrap Configuration
    │
    ▼
Initialize Logging
    │
    ▼
Validate Environment
    │
    ▼
Initialize Database
    │
    ▼
Check / Apply Migrations
    │
    ▼
Initialize Core Services
    │
    ▼
Initialize Optional Integrations
    │
    ▼
Discover Plugins
    │
    ▼
Load Saved Workspace
    │
    ▼
Create Main Window
    │
    ▼
Ready

Optional integrations should not unnecessarily block main application startup.

# 57. Startup Failure Levels

Startup failures should be classified.

Fatal

Examples:

application files missing

database cannot be initialized

incompatible schema with no safe recovery

critical configuration invalid

Result:

application may need to stop

error must be visible

logs should record cause

Non-Fatal

Examples:

AI unavailable

Microsoft Graph unavailable

optional plugin fails

external utility missing

Result:

application should continue

affected capability should be disabled or degraded

# 58. Application Shutdown Architecture

Preferred shutdown sequence:

Shutdown Requested
      │
      ▼
Check Running Operations
      │
      ▼
Resolve / Cancel Safe Tasks
      │
      ▼
Save Workspace State
      │
      ▼
Flush Logs
      │
      ▼
Close Database
      │
      ▼
Stop Child Processes
      │
      ▼
Exit

Shutdown must avoid data corruption.

# 59. Child Process Management

F7Hub may launch:

PowerShell

AutoHotkey

external utilities

browser links

editors

Child processes should be tracked when F7Hub is responsible for their lifecycle.

Not every externally launched application must be terminated when F7Hub exits.

# 60. Command Palette Architecture

The universal command palette should use registered actions.

Conceptually:

Command Palette
      │
      ▼
Command Registry
      │
      ├── Open Ticket
      ├── Search KB
      ├── Run Script
      ├── Open Workspace
      ├── Launch Tool
      └── Open Integration

Commands should map to application services rather than embed arbitrary implementation code.

# 61. Command Registry

A command may contain:

command ID

label

category

shortcut

handler

permissions

availability condition

This provides a common foundation for:

menus

toolbar actions

command palette

shortcuts

# 62. Reporting Architecture

Reports should consume structured application data.

Preferred flow:

Repositories
    │
    ▼
ReportService
    │
    ▼
Report Model
    │
    ▼
Renderer / Exporter

Reports should not directly query unrelated tables from GUI code.

# 63. File Storage Architecture

Files may be used for:

scripts

attachments

exports

logs

documentation

assets

configuration

backups

The database may store references and metadata.

File ownership must be explicit.

# 64. Attachment Strategy

Large attachments should normally remain as files rather than SQLite BLOBs unless future evidence justifies otherwise.

Database records may store:

attachment ID

ticket ID

filename

relative path

MIME/type

size

hash

timestamp

Exact schema belongs in database documentation.

# 65. Relative Paths

Where practical, project-controlled files should use relative paths rather than machine-specific absolute paths.

This improves:

portability

backup

repository movement

testing

Environment-specific paths should be resolved through configuration.

# 66. Dependency Management

Dependencies should be introduced deliberately.

Each major dependency should answer:

what problem does it solve?

is it maintained?

is it secure?

does Python already provide sufficient functionality?

does it introduce licensing constraints?

can it be replaced?

does it create architectural coupling?

Dependency growth should be controlled.

# 67. Security Boundaries

Major security boundaries include:

User Input
Clipboard
Files
Plugins
AI Output
External APIs
PowerShell
Shell Commands
Database
Credentials

Each boundary requires validation appropriate to its risk.

# 68. Privileged Operations

Administrative actions must remain explicit.

Example:

Technician
    │
    ▼
Select Action
    │
    ▼
Review Target / Parameters
    │
    ▼
Privilege Check
    │
    ▼
Execute
    │
    ▼
Capture Result

F7Hub should not silently elevate privilege.

# 69. Authentication Boundary

Authentication is not part of normal domain logic.

Authentication should be handled through dedicated integration infrastructure.

Examples:

Microsoft identity platform

OAuth

provider SDKs

PowerShell authentication flows

Tokens must not flow freely through unrelated modules.

# 70. Local-First Architecture

F7Hub should provide meaningful local functionality without cloud access.

Local capabilities may include:

SQLite
Tickets
KB
Search
Scripts
Clipboard
Prompts
Settings
Logs
Documentation

Connected capabilities may include:

Microsoft Graph
Exchange Online
Intune
Defender
HaloPSA
NinjaOne
AI Providers

# 71. Integration Status Model

External integrations should expose observable status.

Possible states:

NOT_CONFIGURED
AVAILABLE
AUTHENTICATING
CONNECTED
DEGRADED
UNAVAILABLE
ERROR

The status bar or settings UI may consume these states.

# 72. Testing Architecture

The architecture must support tests at multiple layers.

GUI Tests
   │
Service Tests
   │
Domain Tests
   │
Repository Tests
   │
Database Tests
   │
Integration Tests

Subsystems should be testable independently where practical.

# 73. Database Test Boundary

Database tests should use controlled test databases.

Tests must not operate on the user's production F7Hub database.

Migration tests should create temporary or isolated database copies.

# 74. External Integration Testing

External integrations should support:

mocks where practical

sandbox/test environments where available

explicit opt-in live testing

no destructive production testing by default

# 75. Architectural Dependency Rules

The following dependencies are allowed conceptually:

GUI
→ Application Services

Application Services
→ Domain

Application Services
→ Repositories / Gateways

Repositories
→ Database Infrastructure

Gateways
→ External Infrastructure

Discouraged or forbidden:

Database
→ GUI

PowerShell Script
→ PySide6 Widgets

AHK
→ Direct SQLite Schema Manipulation

Plugin
→ Unrestricted Core Internals

GUI
→ Raw SQL

AI
→ Unreviewed Administrative Execution

# 76. Technology Ownership Matrix

Concern

Primary Technology

Main GUI

Python / PySide6

Application services

Python

Domain logic

Python

Persistent data

SQLite

Database access

Python repositories

Microsoft administration

PowerShell / Graph

Windows administration

PowerShell

Desktop hotkeys

AutoHotkey v2

Hotstrings

AutoHotkey v2

Clipboard hooks

AutoHotkey v2 / Python where appropriate

Knowledge storage

SQLite + files where appropriate

Search

Python + SQLite FTS5

Diagnostic orchestration

Python

Diagnostic scripts

PowerShell

AI orchestration

Python

Plugins

Python-first unless explicitly designed otherwise

Documentation

Markdown

Diagrams

Mermaid

Technology ownership prevents responsibility drift.

# 77. Architectural Decision Rule

When deciding where new functionality belongs, ask:

Is it GUI behavior?

Is it domain logic?

Is it persistence?

Is it Windows/Microsoft administration?

Is it desktop automation?

Is it external integration?

Does an existing subsystem already own this concern?

Then place the implementation in the appropriate layer.

# 78. Example: Ticket Diagnostic Flow

User Opens Ticket
      │
      ▼
Ticket GUI
      │
      ▼
TicketService
      │
      ├──────────────┐
      ▼              ▼
TicketRepository   DiagnosticService
      │              │
      ▼              ▼
SQLite         DiagnosticRepository
                     │
                     ▼
                   SQLite
                     │
                     ▼
              PowerShellService
                     │
                     ▼
              PowerShellGateway
                     │
                     ▼
                Script File
                     │
                     ▼
               Structured JSON
                     │
                     ▼
              DiagnosticService
                     │
                     ▼
              Ticket Timeline

This demonstrates separation between:

UI

ticket domain

diagnostics

PowerShell

persistence

# 79. Example: Knowledge Search Flow

User Query
   │
   ▼
Search GUI
   │
   ▼
SearchService
   │
   ▼
Query Normalizer
   │
   ▼
KnowledgeSearchProvider
   │
   ▼
KnowledgeRepository
   │
   ▼
SQLite / FTS5
   │
   ▼
Ranked Results
   │
   ▼
GUI

# 80. Example: Microsoft 365 Action Flow

Technician
    │
    ▼
GUI Action
    │
    ▼
Microsoft365Service
    │
    ▼
Validate Target / Parameters
    │
    ▼
Choose Gateway
    │
    ├── Microsoft Graph
    └── PowerShell
    │
    ▼
Execute
    │
    ▼
Structured Result
    │
    ▼
Audit / Log
    │
    ▼
GUI Result

# 81. Architecture and Documentation

Architecture changes require documentation updates.

Examples:

GUI Architecture
→ 05_GUI.md
→ 06_SystemArchitecture.md
→ 13_PythonArchitecture.md

Database Architecture
→ 07_Database.md
→ 08_ERD.md
→ 09_SQLSchema.md

PowerShell
→ 12_PowerShellArchitecture.md

AutoHotkey
→ 11_AHKArchitecture.md

Repository Structure
→ 10_FolderStructure.md

# 82. Architecture Change Control

The following changes require explicit review before implementation:

primary GUI framework change

repository restructuring

database technology replacement

destructive migrations

cross-language IPC redesign

plugin architecture redesign

authentication model change

secrets-management change

major dependency introduction

replacement of SQLite

new long-running background service

remote server/backend architecture

multi-user architecture

These changes create long-term constraints.

# 83. Anti-Patterns

Avoid the following:

God Object

One class controls:

GUI

SQL

PowerShell

settings

logging

search

GUI Business Logic

Complex domain rules implemented directly inside button handlers.

SQL Everywhere

SQL queries scattered across UI components.

Script Database Dump

Storing every script's full source in SQLite without justification.

Arbitrary Shell Construction

Building shell commands through string concatenation.

Hidden Global State

Any module can mutate application state without clear ownership.

AI as Controller

AI makes administrative decisions and executes them automatically.

Plugin Free-for-All

Plugins can import and modify any internal subsystem.

Premature Distributed Architecture

Local modules communicate through HTTP services without an actual requirement.

Duplicate Services

Multiple unrelated implementations solve the same domain problem.

# 84. Initial Architecture Scope

The early target architecture should remain small and should be reached through independently tested slices.

Recommended initial system:

PySide6 Application Shell
        │
        ├── SettingsService
        ├── TicketService
        ├── KnowledgeService
        ├── SearchService
        └── ScriptService
                 │
                 ▼
            Repositories
                 │
                 ▼
               SQLite

PowerShellService
        │
        ▼
PowerShellGateway
        │
        ▼
PowerShell Scripts

Additional architecture should be introduced only as required.

# 85. Architecture Evolution Sequence

A reasonable architectural growth path is:

1. SQLite bootstrap and migration infrastructure
       ↓
2. Taxonomy / Companies / Contacts persistence
       ↓
3. Ticket persistence and service
       ↓
4. PySide6 application shell and ticket GUI
       ↓
5. Knowledge Base
       ↓
6. Search
       ↓
7. Script Registry
       ↓
8. PowerShell Execution
       ↓
9. Diagnostic Engine
       ↓
10. Clipboard / AHK Integration
       ↓
11. Microsoft Integrations
       ↓
12. AI Integration
       ↓
13. Plugin Framework when validated requirements justify it

This sequence is directional rather than immutable.

Dependencies and product priorities may alter implementation order.

# 86. Architecture Quality Criteria

The architecture is considered healthy when:

modules have clear responsibilities

database access is centralized

GUI does not contain infrastructure logic

PowerShell execution is controlled

cross-language contracts are explicit

errors are observable

external failures are isolated

tests can target individual layers

new functionality can be added without rewriting unrelated modules

project documentation matches implementation

AI does not bypass security

state ownership is clear

# 87. Architecture Review Checklist

Before accepting a significant implementation:

[ ] Requirement identified
[ ] Relevant documentation inspected
[ ] Existing functionality searched
[ ] Correct subsystem selected
[ ] Dependency direction preserved
[ ] Duplicate architecture avoided
[ ] Database integrity considered
[ ] Security boundary considered
[ ] Error handling defined
[ ] Cross-language contract defined if applicable
[ ] Test strategy defined
[ ] Documentation impact identified
[ ] Unrelated refactoring avoided

# 88. Source of Truth

When architectural information conflicts, use:

explicit user requirement

approved system architecture

project documentation

validated implementation

tests

established conventions

engineering inference

Uninspected implementation remains:

NOT VERIFIED

# 89. Relationship to Other Documents

00_ProjectVision.md

Defines:

Why does F7Hub exist?

01_Project.md

Defines:

What is F7Hub as a software project?

02_ProductRequirements.md

Defines:

What must F7Hub accomplish?

05_GUI.md

Defines:

How should the interface behave?

06_SystemArchitecture.md

Defines:

How do F7Hub subsystems communicate?

07_Database.md

Defines:

How should persistent data architecture work?

11_AHKArchitecture.md

Defines:

How does AutoHotkey fit into the system?

12_PowerShellArchitecture.md

Defines:

How does PowerShell automation operate?

13_PythonArchitecture.md

Defines:

How is the Python/PySide6 application structured internally?

# 90. Final Architecture Summary

F7Hub should be built as a modular Windows desktop application centered on Python and PySide6.

Its core architecture is:

                    Technician
                         │
                         ▼
                  Python / PySide6
                         │
                         ▼
                Application Services
                         │
             ┌───────────┼───────────┐
             │           │           │
             ▼           ▼           ▼
           Domain    Repositories   Gateways
                         │           │
             ┌───────────┘           └─────────────┐
             ▼                                     ▼
           SQLite                           Infrastructure
                                             │    │    │
                                             ▼    ▼    ▼
                                            PS   AHK  APIs

Subsystem ownership is deliberate:

PySide6 owns the primary interface

Python owns application orchestration and domain services

SQLite owns relational persistence

PowerShell owns Windows and Microsoft administration

AutoHotkey owns lightweight desktop automation

gateways isolate external systems

repositories isolate persistence

AI assists but does not control privileged execution

plugins extend only through defined boundaries

The architecture should remain local-first, modular, testable and understandable.

The guiding rule is:

GUI calls services.
Services coordinate domain logic.
Repositories own persistence.
Gateways own infrastructure.
Cross-language communication uses explicit contracts.
Privileged actions remain under technician control.

F7Hub should become more capable without becoming architecturally opaque.
