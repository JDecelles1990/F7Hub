# F7Hub Project Vision

> Document: `Docs/00_ProjectVision.md`  
> Project: F7Hub  
> Purpose: Define why F7Hub exists, what problem it solves, who it serves, and what the project is intended to become.  
> Scope: Product vision and long-term direction.  
> Technical implementation details belong in the specialized architecture and design documents.

---

# 1. Project Identity

| Property | Value |
|---|---|
| Project Name | F7Hub |
| Project Type | Modular Windows IT Support and Technician Productivity Platform |
| Primary Platform | Windows 11 |
| Primary GUI Technology | Python / PySide6 |
| Desktop Automation | AutoHotkey v2 |
| Administration & Automation | PowerShell |
| Persistent Data | SQLite |
| Primary Domain | IT Support, Helpdesk, MSP Operations, Microsoft 365 Administration |
| Development Model | Modular, documentation-driven, testable vertical slices |
| Current Status | Architecture, documentation, database and implementation planning |
| Author | Jonathan Decelles |
| Initial Audience | Individual IT Support Technician |
| Future Audience | MSP teams, internal IT departments, system administrators and technical support teams |

Implementation status must never be inferred from this vision document.

Features described here represent the intended direction of F7Hub unless another project document explicitly marks them as implemented.

---

# 2. Vision Statement

F7Hub is a modular Windows IT support workspace designed to centralize the tools, information, automation, troubleshooting workflows and knowledge required by an IT technician.

Its goal is to reduce the fragmentation of technical support work by bringing ticket context, knowledge, scripts, diagnostics, search, automation, documentation, Microsoft administration utilities, clipboard tools and AI assistance into one coherent environment.

The long-term vision is:

> One workspace for understanding, troubleshooting, automating, documenting and resolving IT support work.

F7Hub is not intended to replace every specialized IT application.

Instead, it acts as a technician command center that connects workflows, tools and information that would otherwise be scattered across many applications.

---

# 3. Why F7Hub Exists

Modern IT support technicians frequently work across many disconnected systems.

A typical support case may require switching between:

- PSA or ticketing platforms such as HaloPSA
- Microsoft 365 Admin Center
- Microsoft Entra ID
- Exchange Online
- Microsoft Intune
- Microsoft Defender
- Microsoft Graph
- PowerShell
- Remote monitoring and management tools
- Password managers
- Knowledge bases
- OneNote
- Browsers
- Search engines
- Microsoft Learn
- Internal documentation
- Command Prompt
- Windows administrative utilities
- Script repositories
- Clipboard history
- File Explorer
- Logs
- AI assistants
- Communication tools
- Diagnostic utilities

Each context switch introduces friction.

Important information may also become fragmented between:

- Ticket notes
- Personal notes
- KB articles
- Browser tabs
- Scripts
- Terminal output
- Clipboard contents
- Chat conversations
- Documentation
- Temporary text files
- Screenshots
- Local folders

F7Hub exists to reduce that fragmentation.

---

# 4. Core Problem Statement

The problem F7Hub addresses is not simply a lack of IT tools.

The problem is that IT technicians already have too many disconnected tools.

The technician must continuously answer questions such as:

- What ticket am I working on?
- Which company and user does it concern?
- What troubleshooting has already been performed?
- What should I check next?
- Is there a relevant KB article?
- Is there an approved PowerShell script?
- Which administrative portal should I open?
- Which commands are safe to execute?
- What information should be collected?
- What happened earlier in the ticket?
- What diagnostic result did the previous command return?
- How should the resolution be documented?
- Does a similar incident already exist?
- What information should be escalated?
- What should be copied back into the PSA?

F7Hub aims to maintain this context inside a persistent technician workspace.

---

# 5. Core Product Idea

F7Hub combines several concepts into one modular application:

- IT technician dashboard
- Ticket workspace
- Knowledge base
- Troubleshooting assistant
- Script library
- PowerShell automation platform
- Diagnostic engine
- Clipboard manager
- Universal search engine
- Prompt library
- AI-assisted workspace
- Microsoft 365 administration launcher
- Company and contact context manager
- Reporting environment
- Plugin host
- Technician utility toolbox
- Documentation platform

The application should behave more like an IT technician operating environment than a traditional single-purpose utility.

---

# 6. Product Philosophy

F7Hub follows several fundamental ideas.

## 6.1 Centralize Context, Not Everything

F7Hub should not attempt to reproduce every external application.

Where appropriate, it should:

- integrate
- launch
- query
- automate
- summarize
- contextualize
- link
- orchestrate

existing systems.

For example, F7Hub may interact with Microsoft 365 services without attempting to recreate the Microsoft 365 Admin Center.

---

## 6.2 Keep the Technician in Control

Automation should assist the technician, not silently replace technical judgment.

Potentially destructive actions must remain deliberate.

AI-generated commands and scripts must be treated as untrusted until reviewed.

The technician should be able to inspect:

- commands
- parameters
- scripts
- targets
- expected effects
- output
- errors

before dangerous operations are executed.

---

## 6.3 Reduce Context Switching

Frequently used support information should be accessible from the active workspace.

A ticket should be able to expose related:

- company information
- contact information
- notes
- timeline
- KB articles
- scripts
- diagnostics
- bookmarks
- attachments
- prompts
- search results
- PowerShell parameters
- AI suggestions

without requiring the technician to manually reconstruct the context.

---

## 6.4 Reuse Before Recreating

Before adding a new subsystem, F7Hub development should determine whether an existing component already provides the required capability.

The development rule is:

> SEARCH → IDENTIFY → REUSE OR EXTEND → CREATE ONLY IF NECESSARY

This helps prevent duplicate:

- tables
- repositories
- services
- utilities
- scripts
- models
- modules
- configuration systems
- APIs

---

## 6.5 Small, Testable Development

F7Hub should not be generated as one enormous AI coding operation.

Development follows:

> UNDERSTAND → INSPECT → PLAN → IMPLEMENT → TEST → REVIEW → DOCUMENT

Large features should be divided into independently testable vertical slices.

Examples:

Instead of:

> Build the entire Ticket Center.

Prefer:

> Implement ticket creation persistence, validation, repository operations and tests.

Instead of:

> Build the complete diagnostic platform.

Prefer:

> Implement diagnostic workflow definitions and their SQLite persistence layer.

---

# 7. Primary Users

## 7.1 Initial User

The first F7Hub implementation is designed primarily for an individual IT support technician working in a Microsoft-centric MSP environment.

Typical responsibilities include:

- Level 1 and Level 2 technical support
- Microsoft 365 troubleshooting
- Windows troubleshooting
- Account management
- Exchange Online support
- Entra ID support
- Intune troubleshooting
- Microsoft Defender investigation
- Endpoint support
- Networking diagnostics
- Ticket documentation
- Knowledge management
- PowerShell administration
- Remote user support

---

## 7.2 Future Users

Potential future users include:

- MSP helpdesk technicians
- System administrators
- Microsoft 365 administrators
- Desktop support technicians
- Internal IT departments
- Technical support teams
- Junior technicians
- IT students building practical troubleshooting experience

Multi-user and enterprise capabilities must not be assumed until explicitly designed.

---

# 8. Primary Use Cases

F7Hub should eventually support workflows such as:

## 8.1 Ticket Investigation

A technician opens or creates a ticket and immediately obtains:

- user context
- company context
- previous notes
- timeline
- related tickets
- relevant KB articles
- suggested diagnostics
- applicable scripts
- bookmarks
- related administrative portals

---

## 8.2 Guided Troubleshooting

Based on the issue category, F7Hub can present structured troubleshooting workflows.

Examples:

- Outlook connectivity
- Microsoft 365 login
- MFA problems
- password reset
- OneDrive synchronization
- Teams microphone or camera issues
- printer problems
- VPN connectivity
- DNS issues
- Windows performance
- Exchange mailbox issues
- Intune enrollment
- Microsoft Defender alerts

Diagnostic workflows may dynamically request information from the technician and invoke approved PowerShell scripts where appropriate.

---

## 8.3 PowerShell Automation

F7Hub should provide a structured way to:

- discover scripts
- categorize scripts
- document scripts
- define parameters
- validate input
- run approved scripts
- capture structured results
- save execution history
- associate execution results with tickets
- review errors
- reuse diagnostic output

PowerShell scripts should primarily remain stored as version-controlled files.

The database may store script metadata, categories, execution history, parameters and relationships.

---

## 8.4 Knowledge Management

F7Hub should allow technicians to create and search structured knowledge such as:

- KB articles
- troubleshooting procedures
- known errors
- SOPs
- commands
- PowerShell examples
- portal links
- diagnostic procedures
- escalation information
- technical notes

Knowledge should be searchable and reusable across tickets.

---

## 8.5 Clipboard Intelligence

The clipboard subsystem should support repetitive IT support work such as:

- storing reusable snippets
- formatting ticket notes
- transforming copied text
- extracting useful information
- maintaining clipboard history
- inserting templates
- generating structured troubleshooting notes
- launching actions from copied data

AutoHotkey v2 is particularly suited to this subsystem.

---

## 8.6 Microsoft 365 Administration

F7Hub should help technicians work with Microsoft environments including:

- Microsoft 365
- Microsoft Entra ID
- Exchange Online
- Microsoft Graph
- Microsoft Intune
- Microsoft Defender
- Microsoft Teams
- SharePoint Online

Integration may occur through:

- PowerShell modules
- Microsoft Graph
- administrative URLs
- scripts
- APIs
- structured queries

Authentication and permissions must follow least-privilege principles.

---

## 8.7 Universal Search

A single search interface should eventually provide access to several F7Hub information domains.

Possible sources include:

- tickets
- companies
- contacts
- KB articles
- scripts
- prompts
- commands
- clipboard entries
- bookmarks
- documentation
- assets
- logs
- plugins

SQLite FTS5 may be used where appropriate for high-performance textual search.

External systems may require separate connectors.

---

# 9. Technology Roles

F7Hub deliberately uses multiple technologies.

Each technology has a defined responsibility.

## 9.1 Python / PySide6

Python and PySide6 form the primary advanced desktop application and GUI layer.

Responsibilities may include:

- main application window
- navigation
- dockable panels
- workspaces
- advanced widgets
- database integration
- service orchestration
- search interface
- ticket workspace
- KB interface
- reporting
- plugin management
- AI workspace
- application state management

Python should not absorb PowerShell or AutoHotkey responsibilities merely because it can technically perform them.

---

## 9.2 AutoHotkey v2

AutoHotkey v2 provides Windows-focused desktop automation.

Responsibilities may include:

- global hotkeys
- hotstrings
- clipboard automation
- quick menus
- Windows interaction
- text insertion
- lightweight popup interfaces
- application launching
- productivity shortcuts

AHK should remain focused on desktop interaction and lightweight automation.

---

## 9.3 PowerShell

PowerShell provides the Windows and Microsoft administration automation layer.

Responsibilities may include:

- Windows diagnostics
- Microsoft 365 administration
- Microsoft Graph operations
- Exchange Online
- Entra ID
- Intune
- Microsoft Defender
- networking diagnostics
- system information
- reporting
- scriptable troubleshooting
- structured diagnostic execution

PowerShell should remain the primary administration language where PowerShell provides the strongest native ecosystem.

---

## 9.4 SQLite

SQLite provides F7Hub's persistent relational data layer.

It may eventually store domains such as:

- tickets
- companies
- contacts
- KB metadata
- prompts
- scripts metadata
- diagnostic workflows
- diagnostic results
- clipboard metadata
- settings
- bookmarks
- workspaces
- plugins metadata
- reports metadata
- audit data
- application history

Database development must preserve:

- normalization
- primary keys
- foreign keys
- constraints
- indexes
- transactions
- migrations
- query performance
- referential integrity
- parameterized queries

SQLite foreign-key enforcement must be enabled.

---

# 10. Architectural Vision

F7Hub should generally follow this application flow:

```text
┌───────────────────────────────────────────┐
│                  GUI                      │
│             Python / PySide6              │
└─────────────────────┬─────────────────────┘
                      │
                      ▼
┌───────────────────────────────────────────┐
│        Application / Service Layer        │
│                                           │
│ Tickets │ Search │ KB │ Scripts │ AI      │
│ Diagnostics │ Plugins │ Clipboard │ etc.  │
└─────────────────────┬─────────────────────┘
                      │
                      ▼
┌───────────────────────────────────────────┐
│               Domain Logic                │
└─────────────────────┬─────────────────────┘
                      │
                      ▼
┌───────────────────────────────────────────┐
│          Repositories / Gateways           │
└──────────────┬──────────────┬─────────────┘
               │              │
               ▼              ▼
        ┌────────────┐   ┌────────────────┐
        │   SQLite   │   │ External Tools │
        │  Database  │   │ APIs / Scripts │
        └────────────┘   └────────────────┘
                              │
                  ┌───────────┼───────────┐
                  ▼           ▼           ▼
             PowerShell     AHK v2    Microsoft APIs
```

Subsystem boundaries should remain explicit.

Cross-language communication must use documented contracts rather than hidden coupling.

---

# 11. F7Hub Project Layers

```text
F7Hub
│
├── Python
│   └── Main Application / PySide6 GUI
│
├── AutoHotkey
│   └── Desktop Automation Layer
│
├── PowerShell
│   └── Administration / Diagnostic Automation Layer
│
├── Database
│   └── SQLite Data Layer
│
├── Config
│   └── Application Configuration
│
├── Data
│   └── Application Data / Import / Export
│
├── Plugins
│   └── Extensibility Layer
│
├── Docs
│   └── Architecture / Requirements / Knowledge
│
├── Tests
│   └── Validation Layer
│
├── Assets
│   └── Application Resources
│
├── Build
│   └── Build Artifacts
│
├── Installer
│   └── Deployment
│
├── Logs
│   └── Operational Logs
│
├── Releases
│   └── Versioned Releases
│
└── Tools
    └── Development / Maintenance Utilities
```

The authoritative folder structure belongs in:

`Docs/10_FolderStructure.md`

---

# 12. Target User Experience

The long-term F7Hub desktop experience is inspired by productivity tools with configurable panes and workspaces.

Conceptually, it combines useful characteristics of:

- Visual Studio Code
- OneNote
- ticketing systems
- PowerShell terminals
- command palettes
- knowledge bases
- clipboard managers
- AI workspaces
- administrative dashboards

without attempting to clone these applications.

---

# 13. Target Main Window

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Menu Bar                                                                                                   │
│ File | Edit | View | Navigate | Ticket | Automation | Database | AI | Tools | Window | Help              │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Toolbar                                                                                                    │
│ New │ Save │ Search │ Command │ Run │ Stop │ PowerShell │ AI │ Notifications │ Theme │ Settings          │
├──────────────────┬────────────────────────────────────────────────────┬──────────────────────────────────────┤
│ Navigation       │ Main Workspace                                     │ Assistant & Context                  │
│                  │                                                    │                                      │
│ ▼ Workspace      │                                                    │ AI Assistant                         │
│   Dashboard      │                                                    │ Suggestions                          │
│   Tickets        │                                                    │ Company                              │
│   Companies      │                                                    │ Contact                              │
│   Contacts       │                                                    │ Timeline                             │
│                  │                                                    │ Related KB                           │
│ ▼ Knowledge      │                                                    │ Attachments                          │
│   Knowledge Base │                                                    │ Script Parameters                    │
│   Clipboard      │                                                    │ Search Results                       │
│   Prompts        │                                                    │                                      │
│                  │                                                    │                                      │
│ ▼ Automation     │                                                    │                                      │
│   Scripts        │                                                    │                                      │
│   AI Center      │                                                    │                                      │
│   Plugins        │                                                    │                                      │
│                  │                                                    │                                      │
│ ▼ Data           │                                                    │                                      │
│   Database       │                                                    │                                      │
│   Assets         │                                                    │                                      │
│                  │                                                    │                                      │
│ ▼ Administration │                                                    │                                      │
│   Reports        │                                                    │                                      │
│   Logs           │                                                    │                                      │
├──────────────────┴────────────────────────────────────────────────────┼──────────────────────────────────────┤
│ Embedded PowerShell Terminal                                          │ Output                               │
│                                                                       │ Logs                                 │
│                                                                       │ SQL                                  │
│                                                                       │ AI                                   │
│                                                                       │ Debug                                │
├───────────────────────────────────────────────────────────────────────┴──────────────────────────────────────┤
│ Ready │ Workspace │ Company │ Contact │ SQLite │ PowerShell │ AI │ Plugins │ Queue │ Memory │ Version │ Time │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

This diagram describes a target interface concept.

Detailed GUI specifications belong in:

- `Docs/05_GUI.md`
- `Docs/06_SystemArchitecture.md`
- `Docs/13_PythonArchitecture.md`

---

# 14. Dockable Workspace Vision

F7Hub should eventually support configurable panels where technically appropriate.

Potential panels include:

- Ticket Queue
- Ticket Details
- Notes
- Timeline
- Attachments
- Company Context
- Contact Context
- AI Assistant
- Knowledge Base
- Related KB
- PowerShell Console
- Script Library
- Script Parameters
- Clipboard History
- Search Results
- Activity Log
- Output
- SQL
- Debug
- Bookmarks

Panels may eventually support states such as:

- docked
- floating
- hidden
- resized
- repositioned
- moved between monitors
- saved as part of a workspace

Exact PySide6 implementation is defined elsewhere.

---

# 15. Workspace Profiles

Different technical activities require different information.

F7Hub should eventually allow workspace layouts optimized for specific tasks.

Examples include:

## Helpdesk Workspace

Focus:

- ticket queue
- ticket details
- user context
- notes
- timeline
- KB
- AI assistance

---

## Microsoft 365 Workspace

Focus:

- PowerShell
- Microsoft Graph
- Exchange Online
- Entra ID
- Intune
- Microsoft Defender
- Microsoft 365 administrative links

---

## Networking Workspace

Focus:

- ping
- DNS
- IP configuration
- route diagnostics
- network commands
- logs
- networking KB
- external diagnostic utilities

---

## AI Workspace

Focus:

- prompt library
- AI conversation
- ticket context
- structured prompt generation
- script review
- troubleshooting assistance

---

## Knowledge Authoring Workspace

Focus:

- KB editor
- related articles
- references
- tags
- search
- attachments
- publishing workflows

---

## Automation Workspace

Focus:

- PowerShell
- AutoHotkey
- script library
- execution output
- parameters
- logs
- scheduling
- diagnostics

---

# 16. Universal Command Palette

A universal command palette is part of the long-term productivity vision.

Conceptual examples:

```text
> Open ticket INC-10254
> Search KB Outlook cached credentials
> Run DNS diagnostics
> Open Exchange Admin Center
> Open Entra ID
> Find PowerShell mailbox scripts
> New KB article
> Search company Contoso
> Show clipboard history
> Switch workspace Microsoft 365
> Open diagnostic workflow Outlook
> Search commands Test-NetConnection
```

The command palette should provide fast keyboard-oriented access to F7Hub functionality.

It must not become a mechanism for bypassing security controls.

---

# 17. Diagnostic Engine Vision

F7Hub should eventually contain a structured diagnostic engine.

The engine can connect:

```text
Ticket / Issue
      │
      ▼
Issue Classification
      │
      ▼
Diagnostic Workflow
      │
      ▼
Questions / Conditions
      │
      ├── Technician Input
      │
      ├── Existing Ticket Data
      │
      └── Automated Diagnostics
      │
      ▼
PowerShell Script Execution
      │
      ▼
Structured JSON Result
      │
      ▼
Evaluation
      │
      ├── Next Diagnostic Step
      ├── Suggested Resolution
      ├── Related KB
      ├── Escalation
      └── Documentation
```

The diagnostic engine should remain deterministic where possible.

AI may assist with interpretation and recommendations, but core workflow rules should not depend exclusively on an LLM.

---

# 18. AI Vision

AI is an assistance layer within F7Hub, not the source of truth.

Potential AI capabilities include:

- ticket summarization
- troubleshooting suggestions
- root-cause hypotheses
- KB retrieval assistance
- prompt generation
- note cleanup
- resolution drafting
- search query normalization
- script explanation
- script review
- classification
- structured information extraction
- related-ticket discovery
- diagnostic interpretation

AI output must be treated as untrusted.

AI must not automatically execute destructive commands.

Where practical, important AI actions should be grounded in:

- ticket data
- KB articles
- database records
- approved scripts
- documentation
- diagnostic results

---

# 19. Search Vision

Search is a foundational capability rather than an isolated feature.

The long-term objective is a unified search experience across F7Hub.

```text
User Query
    │
    ▼
Query Normalization
    │
    ▼
Search Router
    │
    ├── Tickets
    ├── Companies
    ├── Contacts
    ├── KB
    ├── Scripts
    ├── Prompts
    ├── Clipboard
    ├── Commands
    ├── Documentation
    ├── Assets
    └── Plugins
    │
    ▼
Ranking
    │
    ▼
Unified Results
```

Search implementation details belong in the architecture and database documentation.

---

# 20. Plugin Vision

F7Hub should be extensible without requiring every future capability to be embedded into the core application.

A future plugin system may allow additional:

- utilities
- integrations
- ticket providers
- search providers
- diagnostic modules
- reports
- automation actions
- GUI panels

Plugins must have explicitly defined:

- metadata
- lifecycle
- dependencies
- permissions
- interfaces
- compatibility requirements
- error handling

Plugin architecture must not be implemented casually because it creates a major application boundary.

Major plugin architecture changes require architectural review.

---

# 21. Database Vision

SQLite is a foundational part of F7Hub.

The database should act as a structured source of persistent application state rather than a dumping ground for arbitrary data.

The database design should support:

- relational integrity
- normalization
- controlled migrations
- predictable queries
- indexing
- auditability
- efficient search
- future extensibility

Database architecture must be designed domain by domain.

The project should not create approximately one hundred tables merely to reach a numerical target.

Each table must have a justified responsibility and relationship to the domain model.

Detailed database specifications belong in:

- `Docs/07_Database.md`
- `Docs/08_ERD.md`
- `Docs/09_SQLSchema.md`

---

# 22. Security Vision

F7Hub may eventually interact with highly privileged administrative systems.

Security is therefore an architectural requirement rather than a future enhancement.

F7Hub should follow:

- least privilege
- secure defaults
- explicit authorization
- parameterized SQL queries
- validated input
- safe subprocess execution
- secrets separation
- auditable administrative actions
- controlled script execution
- sanitized logging
- defensive handling of external data

F7Hub must never intentionally hard-code:

- passwords
- API secrets
- access tokens
- refresh tokens
- private keys
- customer credentials

Inputs from the following should be considered untrusted:

- users
- clipboard
- files
- URLs
- APIs
- ticket systems
- scripts
- plugins
- AI
- external commands

---

# 23. Documentation-Driven Development

Documentation is part of the F7Hub architecture.

It is not merely a description written after development.

The documentation system defines:

- product intent
- requirements
- workflows
- architecture
- database design
- technology boundaries
- naming rules
- development priorities
- implementation state
- historical changes

Significant development should inspect the relevant documentation before modifying the system.

---

# 24. Documentation Map

The canonical F7Hub documentation set is:

```text
Docs/
│
├── 00_ProjectVision.md
│      Why does F7Hub exist and what should it become?
│
├── 01_Project.md
│      What is F7Hub?
│
├── 02_ProductRequirements.md
│      What must F7Hub accomplish?
│
├── 03_Features.md
│      What capabilities are planned or implemented?
│
├── 04_UserWorkflows.md
│      How do users interact with F7Hub?
│
├── 05_GUI.md
│      How should the user interface behave?
│
├── 06_SystemArchitecture.md
│      How do the components communicate?
│
├── 07_Database.md
│      How is persistent information organized?
│
├── 08_ERD.md
│      What entities and relationships exist?
│
├── 09_SQLSchema.md
│      How is the SQLite schema technically implemented?
│
├── 10_FolderStructure.md
│      How is the repository organized?
│
├── 11_AHKArchitecture.md
│      What responsibilities belong to AutoHotkey v2?
│
├── 12_PowerShellArchitecture.md
│      What responsibilities belong to PowerShell?
│
├── 13_PythonArchitecture.md
│      What responsibilities belong to Python and PySide6?
│
├── 14_DesignPrinciples.md
│      What engineering principles guide development?
│
├── 15_NamingConventions.md
│      What naming and coding conventions must be followed?
│
├── 16_Roadmap.md
│      In what sequence should F7Hub evolve?
│
├── 17_Todo.md
│      What work is currently pending?
│
├── 18_ChangeLog.md
│      What verified project changes occurred?
│
└── 19_DocumentationIndex.md
       How should humans and coding agents navigate the documentation?
```

---

# 25. Documentation Responsibility Boundaries

Documentation should avoid unnecessary duplication.

Each file has a primary responsibility.

For example:

```text
Vision
  ↓
Requirements
  ↓
Features
  ↓
User Workflows
  ↓
Architecture
  ↓
Database / Technology Architecture
  ↓
Implementation
  ↓
Tests
  ↓
ChangeLog
```

When information belongs in another document, this document should reference it instead of becoming a second source of truth.

---

# 26. Source-of-Truth Hierarchy

When F7Hub information conflicts, development should prioritize:

1. Explicit user requirement
2. Approved architecture
3. Project documentation
4. Validated implementation
5. Tests
6. Established conventions
7. Engineering inference

Unverified project state must not be presented as fact.

Useful status labels include:

- FACT
- ASSUMPTION
- INFERENCE
- RECOMMENDATION
- NOT VERIFIED

---

# 27. Mermaid Diagram Strategy

F7Hub architectural diagrams should be stored under:

```text
Docs/
└── Assets/
    └── Diagrams/
        │
        ├── Architecture/
        │   ├── F7Hub_Modular_Architecture.mmd
        │   ├── Application_Startup.mmd
        │   └── Module_Communication.mmd
        │
        ├── Ticketing/
        │   ├── Ticket_Workflow.mmd
        │   ├── Open_Ticket_Sequence.mmd
        │   ├── Ticket_Context.mmd
        │   └── Ticket_AI_Assistant.mmd
        │
        ├── Database/
        │   ├── SQLite_Domain_Architecture.mmd
        │   ├── Entity_Relationship.mmd
        │   └── SQL_Data_Flow.mmd
        │
        ├── GUI/
        │   ├── Dashboard_Layout.mmd
        │   ├── Dockable_Workspace_Manager.mmd
        │   └── User_Interface_Flow.mmd
        │
        ├── Automation/
        │   ├── AHK_Automation_Flow.mmd
        │   ├── PowerShell_Execution_Pipeline.mmd
        │   ├── Diagnostic_Engine.mmd
        │   └── Plugin_Lifecycle.mmd
        │
        ├── Knowledge/
        │   ├── Knowledge_Base_Search_Ranking.mmd
        │   └── Knowledge_Article_Lifecycle.mmd
        │
        ├── Search/
        │   ├── Universal_Search_Architecture.mmd
        │   └── Query_Normalization.mmd
        │
        └── AI/
            ├── AI_Engine.mmd
            ├── AI_Context_Flow.mmd
            └── AI_Safety_Boundary.mmd
```

Diagram filenames and locations must remain synchronized with `10_FolderStructure.md` when finalized.

---

# 28. High-Priority Architecture Diagrams

The most useful diagrams for understanding F7Hub include:

1. F7Hub Modular Architecture
2. Application Startup and Initialization Sequence
3. Module Communication Architecture
4. Open Ticket Sequence
5. Ticket Workflow
6. SQLite Database Domain Architecture
7. Entity Relationship Diagram
8. Knowledge Base Search and Ranking Engine
9. PowerShell Script Execution Pipeline
10. Diagnostic Engine
11. Plugin Lifecycle and Dependency Management
12. Universal Search Architecture
13. Dockable Workspace Layout Manager
14. AI Context and Safety Flow

These diagrams should explain architecture rather than duplicate source code.

---

# 29. External Systems Vision

F7Hub may interact with external tools and platforms.

Examples include:

```text
F7Hub
│
├── PSA / Ticketing
│   └── HaloPSA
│
├── RMM
│   └── NinjaOne / NinjaRMM
│
├── Microsoft
│   ├── Microsoft 365
│   ├── Entra ID
│   ├── Exchange Online
│   ├── Intune
│   ├── Defender
│   ├── Microsoft Graph
│   ├── Teams
│   ├── SharePoint
│   └── OneDrive
│
├── Productivity
│   ├── OneNote
│   ├── Edge
│   ├── Visual Studio Code
│   └── Windows utilities
│
├── Security / Credentials
│   └── Keeper
│
├── Search
│   ├── Local F7Hub search
│   ├── Windows search utilities
│   └── External knowledge sources
│
└── AI
    └── Approved AI providers and integrations
```

The existence of an external system in this vision does not imply that an integration has already been implemented.

---

# 30. Portability Vision

F7Hub should eventually be capable of operating as a portable technician toolkit where technically and legally appropriate.

Portability goals may include:

- predictable configuration
- exportable settings
- portable knowledge
- reproducible database migrations
- version-controlled scripts
- documented dependencies
- backup and restore
- environment validation
- controlled deployment

Portability must not compromise credential security or administrative controls.

---

# 31. Long-Term Product Vision

F7Hub may eventually evolve into four complementary concepts.

## 31.1 Personal IT Operating Workspace

A central application used throughout a technician's working day.

---

## 31.2 Modular Automation Framework

Reusable workflows combining:

- AutoHotkey
- PowerShell
- Python
- SQLite
- APIs
- plugins

---

## 31.3 AI-Assisted Knowledge Platform

A system capable of connecting:

```text
Tickets
   +
Knowledge
   +
Diagnostics
   +
Scripts
   +
Historical Results
   +
AI Assistance
```

to improve troubleshooting and documentation.

---

## 31.4 Portable Technician Toolkit

A structured environment containing:

- tools
- commands
- automation
- knowledge
- documentation
- diagnostics
- workflows
- scripts

that can support a technician across multiple IT environments.

---

# 32. What F7Hub Should Not Become

F7Hub should not become:

- one giant monolithic script
- an uncontrolled collection of utilities
- a database with hundreds of unjustified tables
- a replacement for every Microsoft admin portal
- an undocumented collection of AI-generated code
- a system where every subsystem directly accesses every other subsystem
- an application dependent on hidden global state
- a repository containing credentials
- an AI agent that automatically executes dangerous commands
- an architecture rewritten every time a new feature is requested
- a collection of duplicate services solving the same problem
- a project where documentation and implementation continuously disagree

Complexity must be justified by real product requirements.

---

# 33. Engineering Vision

F7Hub should become more understandable after every development cycle.

Preferred properties include:

- modular
- explicit
- testable
- maintainable
- documented
- secure
- reversible
- observable
- extensible
- searchable
- automation-friendly

The preferred implementation is not necessarily the most sophisticated implementation.

The preferred implementation is the simplest architecture that correctly satisfies the requirement while preserving future maintainability.

---

# 34. Development Strategy

Development should proceed through small vertical slices.

A typical cycle is:

```text
UNDERSTAND
    ↓
INSPECT
    ↓
PLAN
    ↓
IMPLEMENT
    ↓
TEST
    ↓
REVIEW
    ↓
DOCUMENT
```

Before creating a new architectural object:

```text
SEARCH
   ↓
IDENTIFY
   ↓
REUSE?
 ┌─────┴─────┐
Yes          No
 │            │
Extend     Create only
Existing   if justified
```

---

# 35. Testing Vision

A F7Hub feature is not complete simply because the application launches.

Validation may include:

- unit testing
- integration testing
- SQLite testing
- migration testing
- repository testing
- PowerShell testing
- GUI testing
- regression testing
- security testing
- end-to-end workflow testing

Testing results should use explicit status terminology:

```text
PASS
FAIL
NOT RUN
BLOCKED
```

Tests must never be reported as passing unless they were actually executed.

---

# 36. Documentation Synchronization

Architecture-changing implementation work should update the relevant documentation.

Examples:

```text
Database changes
→ 07_Database.md
→ 08_ERD.md
→ 09_SQLSchema.md

GUI changes
→ 05_GUI.md
→ 06_SystemArchitecture.md

AutoHotkey changes
→ 11_AHKArchitecture.md

PowerShell changes
→ 12_PowerShellArchitecture.md

Python / PySide6 changes
→ 13_PythonArchitecture.md

Repository structure changes
→ 10_FolderStructure.md

Major milestone changes
→ 16_Roadmap.md
→ 17_Todo.md
→ 18_ChangeLog.md
```

Documentation should describe verified behavior rather than anticipated implementation unless clearly marked as planned.

---

# 37. Success Criteria

F7Hub succeeds if it measurably improves the technician's ability to:

- find information
- understand ticket context
- troubleshoot systematically
- reuse knowledge
- discover scripts
- safely automate repetitive work
- navigate Microsoft administration environments
- document troubleshooting
- retain diagnostic history
- search technical information
- reduce repetitive typing
- reduce unnecessary application switching
- build reusable troubleshooting workflows
- learn from previous support cases

The project should optimize technician effectiveness rather than maximize feature count.

---

# 38. Ultimate Experience

The target F7Hub experience can be summarized as:

```text
Incoming Ticket
      │
      ▼
Understand Context
      │
      ▼
Search Existing Knowledge
      │
      ▼
Run Structured Diagnostics
      │
      ▼
Use Approved Automation
      │
      ▼
Interpret Results
      │
      ▼
Resolve or Escalate
      │
      ▼
Document the Work
      │
      ▼
Preserve New Knowledge
```

The technician remains at the center of the process.

F7Hub provides the context, structure, automation and knowledge surrounding that technician.

---

# 39. Project Motto

> One workspace.  
> One context.  
> Search, troubleshoot, automate, document.

---

# 40. Vision Summary

F7Hub is intended to become a modular Windows IT support command center built around the real workflow of a technician.

Its major foundations are:

- Python / PySide6 for the primary application experience
- AutoHotkey v2 for Windows desktop automation
- PowerShell for Windows and Microsoft administration
- SQLite for persistent structured data
- Knowledge management for reusable troubleshooting
- Search for fast information retrieval
- Diagnostic workflows for systematic troubleshooting
- AI for contextual assistance
- Plugins for controlled extensibility
- Documentation for architectural continuity
- Testing for reliability
- Security for safe administrative operation

The purpose of F7Hub is not to place every IT tool inside one executable.

The purpose is to give the technician one coherent place from which those tools, workflows, data and knowledge can be understood and controlled.

> F7Hub should become more useful without becoming less understandable.
