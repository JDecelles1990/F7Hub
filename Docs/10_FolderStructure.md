# F7Hub Folder Structure

> Document: `Docs/10_FolderStructure.md`  
> Project: F7Hub  
> Purpose: Define the canonical repository organization, folder ownership, and rules governing where F7Hub source code, configuration, data, documentation, tests, tools, and deployment artifacts belong.  
> Project Root: `C:\Dev\F7Hub\`  
> Related Documents: `01_Project.md`, `06_SystemArchitecture.md`, `07_Database.md`, `11_AHKArchitecture.md`, `12_PowerShellArchitecture.md`, `13_PythonArchitecture.md`, `15_NamingConventions.md`

---

# 1. Purpose

The F7Hub folder structure separates:

- application source code
- desktop automation
- PowerShell administration
- database resources
- configuration
- runtime data
- documentation
- plugins
- tests
- development tools
- build artifacts
- installer resources
- logs
- releases

This document answers:

> Where should each type of F7Hub resource live?

The folder structure should remain understandable without requiring knowledge of the entire codebase.

---

# 2. Canonical Project Root

The approved development root is:

```text
C:\Dev\F7Hub\
```

This replaces the previous OneDrive-based project location.

The repository root should remain stable unless restructuring is explicitly approved.

---

# 3. Technology Ownership

F7Hub uses several technologies with deliberately separate responsibilities.

```text
Python / PyQt6
→ Primary application and GUI

SQLite
→ Persistent relational data

PowerShell
→ Windows and Microsoft administration, diagnostics and reporting

AutoHotkey v2
→ Desktop automation, global hotkeys, clipboard and lightweight Windows integration

Markdown / Mermaid
→ Documentation and diagrams
```

No subsystem should absorb another subsystem's responsibilities without architectural justification.

---

# 4. Canonical Top-Level Structure

```text
C:\Dev\F7Hub\
│
├── AutoHotkey\
├── PowerShell\
├── Python\
├── Database\
├── Config\
├── Data\
├── Docs\
├── Plugins\
├── Tests\
├── Assets\
├── Build\
├── Installer\
├── Logs\
├── Releases\
└── Tools\
```

These are the primary architectural directories.

---

# 5. Folder Creation Policy

Not every conceivable subfolder should be created immediately.

Folders fall into two categories.

## Canonical Foundation

Stable architectural folders that may be created during project scaffolding.

Examples:

```text
Python\
PowerShell\
AutoHotkey\
Database\
Docs\
Tests\
Config\
```

## Feature-Specific Folders

Created only when implementation requires them.

Examples:

```text
Plugins\HaloPSA\
Python\plugins\
PowerShell\Modules\Defender\
```

The rule is:

```text
SEARCH
   ↓
IDENTIFY EXISTING LOCATION
   ↓
REUSE OR EXTEND
   ↓
CREATE NEW FOLDER ONLY IF NECESSARY
```

---

# 6. Repository Overview

```text
F7Hub\
│
├── Python\
│   └── Primary application
│
├── AutoHotkey\
│   └── Desktop automation
│
├── PowerShell\
│   └── Administration and diagnostics
│
├── Database\
│   └── SQLite schema and migrations
│
├── Config\
│   └── Application configuration
│
├── Data\
│   └── Runtime/import/export data
│
├── Docs\
│   └── Canonical documentation
│
├── Plugins\
│   └── Optional extensions
│
├── Tests\
│   └── Automated tests
│
├── Assets\
│   └── Application resources
│
├── Logs\
│   └── Runtime/development logs
│
├── Tools\
│   └── Development utilities
│
├── Build\
│   └── Build output
│
├── Installer\
│   └── Packaging/installer definitions
│
└── Releases\
    └── Versioned release artifacts
```

---

# 7. Python

Python is the primary application and orchestration layer.

Canonical root:

```text
Python\
```

Recommended initial structure:

```text
Python\
│
├── f7hub\
│   ├── app\
│   ├── gui\
│   ├── services\
│   ├── domain\
│   ├── repositories\
│   ├── infrastructure\
│   ├── integrations\
│   ├── search\
│   ├── diagnostics\
│   └── utils\
│
└── scripts\
```

Exact Python package organization belongs in:

`13_PythonArchitecture.md`

---

# 8. Python\f7hub

The `f7hub` package contains application source code.

```text
Python\f7hub\
```

---

# 9. Python\f7hub\app

Purpose:

Application lifecycle and coordination.

Potential responsibilities:

- startup
- application bootstrap
- dependency initialization
- application context
- shutdown
- configuration initialization

---

# 10. Python\f7hub\gui

Purpose:

PyQt6 interface implementation.

Potential contents:

```text
gui\
├── windows\
├── widgets\
├── dialogs\
├── docks\
├── models\
└── resources\
```

These should be created only as implementation requires them.

GUI code must not become the owner of SQL or business logic.

---

# 11. Python\f7hub\services

Purpose:

Application services coordinating product workflows.

Potential examples:

```text
TicketService
KnowledgeService
SearchService
DiagnosticService
ScriptService
SettingsService
```

---

# 12. Python\f7hub\domain

Purpose:

Domain concepts and rules.

Potential contents:

- models
- validation
- enums
- workflow rules
- domain exceptions

Domain logic should remain independent of PyQt6.

---

# 13. Python\f7hub\repositories

Purpose:

SQLite persistence boundaries.

Examples:

```text
TicketRepository
CompanyRepository
KnowledgeRepository
ScriptRepository
DiagnosticRepository
```

Repositories own SQL access.

---

# 14. Python\f7hub\infrastructure

Purpose:

Technical infrastructure used by application services.

Potential responsibilities:

- database connections
- subprocess execution
- filesystem access
- logging adapters
- configuration loading

---

# 15. Python\f7hub\integrations

Purpose:

External-system gateways.

Potential integrations may include:

```text
Microsoft Graph
Exchange Online
HaloPSA
NinjaOne
AI providers
```

Provider-specific folders should be created only when those integrations are implemented.

---

# 16. Python\f7hub\search

Purpose:

Search orchestration.

Potential contents:

- query normalization
- search providers
- result ranking
- FTS integration

---

# 17. Python\f7hub\diagnostics

Purpose:

Diagnostic Engine application logic.

Potential contents:

- workflow engine
- condition evaluation
- session orchestration
- result interpretation

PowerShell diagnostic scripts themselves belong under `PowerShell\`.

---

# 18. Python\f7hub\utils

Purpose:

Small reusable Python utilities.

Avoid placing domain logic here simply because code is shared.

---

# 19. AutoHotkey

AutoHotkey v2 is the desktop-automation subsystem.

```text
AutoHotkey\
```

Recommended structure:

```text
AutoHotkey\
├── Core\
├── Hotkeys\
├── Hotstrings\
├── Clipboard\
├── Menus\
├── Launchers\
├── Lib\
├── Helpers\
└── Templates\
```

Exact design belongs in:

`11_AHKArchitecture.md`

---

# 20. AutoHotkey\Core

Purpose:

AHK initialization and common automation infrastructure.

This should not become a second primary F7Hub application layer.

---

# 21. AutoHotkey\Hotkeys

Purpose:

Global keyboard shortcuts.

Examples:

- F7Hub launcher
- clipboard actions
- quick tool access
- text workflows

---

# 22. AutoHotkey\Hotstrings

Purpose:

Reusable text expansions.

Examples:

- technician phrases
- troubleshooting templates
- ticket text

---

# 23. AutoHotkey\Clipboard

Purpose:

Windows clipboard interaction requiring AHK.

Persistent clipboard management should remain coordinated with Python when database storage is required.

---

# 24. AutoHotkey\Menus

Purpose:

Lightweight popup or context menus.

Do not recreate major PyQt6 application screens here.

---

# 25. AutoHotkey\Launchers

Purpose:

Launch or focus:

- F7Hub
- Windows tools
- applications
- websites
- approved scripts

---

# 26. AutoHotkey\Lib

Purpose:

Reusable AHK libraries.

Third-party libraries should be documented and reviewed.

---

# 27. PowerShell

PowerShell is the Windows and Microsoft administration subsystem.

```text
PowerShell\
```

Recommended structure:

```text
PowerShell\
├── Core\
├── Modules\
├── Diagnostics\
├── Reports\
├── Functions\
├── Templates\
└── Tests\
```

Exact architecture belongs in:

`12_PowerShellArchitecture.md`

---

# 28. PowerShell\Core

Purpose:

Shared execution contracts and foundational PowerShell logic.

Potential content:

- structured result helpers
- common validation
- shared error handling

---

# 29. PowerShell\Modules

Purpose:

Technology-oriented administrative automation.

Create technology folders only when actual scripts exist.

Potential future structure:

```text
Modules\
├── Microsoft365\
├── MicrosoftGraph\
├── EntraID\
├── ExchangeOnline\
├── Intune\
├── Defender\
├── Teams\
├── SharePoint\
├── Azure\
├── Windows\
└── Networking\
```

These are approved categories, not a requirement to create all folders immediately.

---

# 30. PowerShell\Diagnostics

Purpose:

Scripts used by F7Hub diagnostic workflows.

Possible future organization:

```text
Diagnostics\
├── Windows\
├── Networking\
├── Microsoft365\
├── Outlook\
├── Teams\
└── Intune\
```

---

# 31. PowerShell\Reports

Purpose:

PowerShell scripts used to generate structured reports.

Generated report output belongs in `Data\Exports\`, not here.

---

# 32. PowerShell\Functions

Purpose:

Shared reusable PowerShell functions.

---

# 33. PowerShell\Templates

Purpose:

Reusable development templates for new PowerShell scripts.

---

# 34. Database

Database resources belong under:

```text
Database\
```

Recommended structure:

```text
Database\
├── Migrations\
├── Seeds\
├── Queries\
├── Views\
├── Triggers\
├── ERD\
└── Dev\
```

Do not create speculative folders if they remain empty.

---

# 35. Database\Migrations

Purpose:

Versioned SQLite schema migrations.

Example:

```text
0001_core.sql
0002_taxonomy.sql
0003_companies_contacts.sql
```

Migrations should be immutable after release.

---

# 36. Database\Seeds

Purpose:

Development, test, or approved default seed data.

Operational user data does not belong here.

---

# 37. Database\Queries

Purpose:

Reusable SQL resources if the architecture benefits from external SQL files.

SQL owned directly by repositories does not need to be duplicated here.

---

# 38. Database\Views

Purpose:

SQL definitions for documented SQLite views.

Create only when views are justified.

---

# 39. Database\Triggers

Purpose:

SQL trigger definitions.

Triggers should be used sparingly.

A folder does not imply that triggers are required.

---

# 40. Database\ERD

Purpose:

Generated or supporting database diagrams.

The canonical textual ERD specification remains:

`Docs\08_ERD.md`

---

# 41. Database\Dev

Purpose:

Development-only SQLite databases where appropriate.

Example:

```text
Database\Dev\f7hub_dev.db
```

Development databases should normally be excluded from Git if they contain mutable development data.

Automated tests must not use this database.

---

# 42. Runtime SQLite Database

The development repository and installed runtime database are different concerns.

During development, a development database may live under:

```text
C:\Dev\F7Hub\Database\Dev\
```

For an installed application, the preferred runtime location should eventually be similar to:

```text
%LOCALAPPDATA%\F7Hub\Data\f7hub.db
```

The final deployment path must be defined before production use.

---

# 43. Config

Configuration belongs under:

```text
Config\
```

Recommended initial structure:

```text
Config\
├── Defaults\
├── Templates\
└── Development\
```

Do not create separate `INI`, `JSON`, and `YAML` directories merely because those formats might be used.

Organize configuration by purpose first.

---

# 44. Config\Defaults

Purpose:

Safe default application configuration.

No secrets.

---

# 45. Config\Templates

Purpose:

Configuration templates users or developers may copy.

No real credentials.

---

# 46. Config\Development

Purpose:

Development-specific non-secret settings.

Sensitive local configuration must remain outside version control where required.

---

# 47. Data

Runtime/import/export files belong under:

```text
Data\
```

Recommended structure:

```text
Data\
├── Attachments\
├── Imports\
├── Exports\
├── Cache\
├── Temp\
└── Samples\
```

---

# 48. Data\Attachments

Purpose:

Development-time ticket or record attachments.

Installed runtime attachment paths may later move to `%LOCALAPPDATA%`.

---

# 49. Data\Imports

Purpose:

Input files imported into F7Hub.

---

# 50. Data\Exports

Purpose:

Generated:

- CSV
- JSON
- HTML
- Markdown
- reports

---

# 51. Data\Cache

Purpose:

Regenerable cached information.

Cache data should never become the only source of important information.

---

# 52. Data\Temp

Purpose:

Temporary processing files.

F7Hub must not depend on these surviving indefinitely.

---

# 53. Data\Samples

Purpose:

Safe sample/demo data used for learning, documentation, or development.

No client production data.

---

# 54. Docs

Canonical project documentation lives directly under:

```text
Docs\
```

The previous `Docs\F7Hub\` nesting is removed.

---

# 55. Canonical Documentation Files

```text
Docs\
├── 00_ProjectVision.md
├── 01_Project.md
├── 02_ProductRequirements.md
├── 03_Features.md
├── 04_UserWorkflows.md
├── 05_GUI.md
├── 06_SystemArchitecture.md
├── 07_Database.md
├── 08_ERD.md
├── 09_SQLSchema.md
├── 10_FolderStructure.md
├── 11_AHKArchitecture.md
├── 12_PowerShellArchitecture.md
├── 13_PythonArchitecture.md
├── 14_DesignPrinciples.md
├── 15_NamingConventions.md
├── 16_Roadmap.md
├── 17_Todo.md
├── 18_ChangeLog.md
└── 19_DocumentationIndex.md
```

These documents form the primary project documentation source of truth.

---

# 56. Docs Supporting Structure

```text
Docs\
├── Assets\
│   ├── Diagrams\
│   ├── Mockups\
│   └── Screenshots\
│
├── Research\
│
└── Archive\
    └── PreviousVersions\
```

---

# 57. Docs\Assets\Diagrams

Recommended organization may eventually include:

```text
Diagrams\
├── Architecture\
├── Database\
├── GUI\
├── Ticketing\
├── Automation\
├── Knowledge\
├── Search\
└── AI\
```

Create categories as diagrams are actually added.

---

# 58. Docs\Assets\Mockups

Purpose:

GUI mockups and design concepts.

---

# 59. Docs\Assets\Screenshots

Purpose:

Verified application screenshots.

Do not use screenshots as substitutes for architecture documentation.

---

# 60. Docs\Research

Research notes are not project requirements.

Potential structure may include:

```text
Research\
├── AI\
├── AutoHotkey\
├── GUI\
├── HaloPSA\
├── Microsoft365\
├── PowerShell\
├── Python\
├── SQLite\
└── UX\
```

Create topics only when research material exists.

---

# 61. Docs\Archive

Purpose:

Historical or superseded documentation.

Example:

```text
Docs\Archive\
└── PreviousVersions\
```

Old brainstorming documents may be moved here instead of deleted.

Example:

```text
08_ERD_Old_Brainstorm.md
```

Archived documents are not project sources of truth.

---

# 62. Plugins

Optional extensions belong under:

```text
Plugins\
```

Initially:

```text
Plugins\
└── README.md
```

or an otherwise minimal structure is sufficient.

Do not pre-create:

```text
HaloPSA
NinjaOne
CIPP
Microsoft365
```

until plugin implementations are approved.

---

# 63. Plugin Folder Rule

When a plugin is implemented:

```text
Plugins\
└── <PluginName>\
```

The plugin should define its own:

- metadata
- entry point
- configuration
- tests
- documentation where required

Exact design belongs in future plugin architecture work.

---

# 64. Tests

Tests belong under:

```text
Tests\
```

Recommended structure:

```text
Tests\
├── Unit\
├── Integration\
├── Database\
├── GUI\
├── PowerShell\
└── Fixtures\
```

---

# 65. Tests\Unit

Purpose:

Fast isolated tests of:

- domain logic
- services
- utilities
- validation

---

# 66. Tests\Integration

Purpose:

Validate communication between subsystems.

Examples:

- service + repository
- service + PowerShell gateway
- search + FTS

---

# 67. Tests\Database

Purpose:

SQLite-specific tests.

Examples:

- migrations
- foreign keys
- constraints
- transactions
- repositories
- FTS

---

# 68. Tests\GUI

Purpose:

PyQt6 GUI tests and workflow validation.

---

# 69. Tests\PowerShell

Purpose:

PowerShell-specific validation where appropriate.

---

# 70. Tests\Fixtures

Purpose:

Reusable safe test data.

Test fixtures must not contain real customer data.

---

# 71. Assets

Application resources belong under:

```text
Assets\
```

Recommended structure:

```text
Assets\
├── Icons\
├── Images\
└── Templates\
```

Application assets are distinct from documentation assets under `Docs\Assets\`.

---

# 72. Assets\Icons

Purpose:

Application icons.

Licensing must be documented where necessary.

---

# 73. Assets\Images

Purpose:

Application graphics and branding.

---

# 74. Assets\Templates

Purpose:

Reusable non-code templates used by application features.

---

# 75. Logs

Development/runtime logs may be stored under:

```text
Logs\
```

Recommended development structure:

```text
Logs\
├── Application\
├── PowerShell\
├── Database\
└── Debug\
```

Do not create a separate folder for every subsystem unless actual log output justifies it.

Installed application logging may later move to:

```text
%LOCALAPPDATA%\F7Hub\Logs\
```

---

# 76. Logs\Application

Purpose:

Main application logs.

---

# 77. Logs\PowerShell

Purpose:

Controlled PowerShell execution logs where file logging is needed.

---

# 78. Logs\Database

Purpose:

Database maintenance or migration logs where appropriate.

SQLite itself does not require a generic log folder for ordinary queries.

---

# 79. Logs\Debug

Purpose:

Developer diagnostics.

Debug logs should not normally be included in releases.

---

# 80. Tools

Development utilities and project-maintenance scripts belong under:

```text
Tools\
```

Recommended structure:

```text
Tools\
├── Scripts\
├── Database\
└── Development\
```

Do not copy full third-party applications into the repository unless there is a clear reason and licensing permits it.

---

# 81. Tools\Scripts

Purpose:

Project maintenance scripts.

Examples:

```text
Initialize-F7Hub.ps1
Validate-ProjectStructure.ps1
Backup-F7HubDatabase.ps1
```

The folder-scaffolding PowerShell script should live here.

---

# 82. Tools\Database

Purpose:

Database maintenance helpers.

Examples:

- schema validation
- migration helpers
- database inspection scripts

---

# 83. Tools\Development

Purpose:

Miscellaneous development utilities that do not belong to application runtime code.

---

# 84. Build

Build artifacts belong under:

```text
Build\
```

This directory may contain:

- intermediate build output
- packaging staging
- generated files

Most generated contents should be excluded from Git.

---

# 85. Installer

Installer resources belong under:

```text
Installer\
```

Create detailed structure only when packaging work begins.

Potential future contents:

- installer configuration
- install scripts
- upgrade scripts
- uninstall definitions

---

# 86. Releases

Release artifacts belong under:

```text
Releases\
```

Do not require permanent `Alpha`, `Beta`, and `Stable` subfolders.

Prefer version-oriented output.

Example:

```text
Releases\
├── 0.1.0-alpha\
├── 0.2.0-alpha\
└── 1.0.0\
```

Release state is already encoded in the version.

---

# 87. Source vs Runtime Separation

Source-controlled content:

```text
Python\
PowerShell\
AutoHotkey\
Database\Migrations\
Config\
Docs\
Tests\
Assets\
Tools\
```

Runtime/generated content may include:

```text
Data\
Logs\
Build\
Releases\
Database\Dev\
```

Generated content should not be committed blindly.

---

# 88. Git Ignore Candidates

The `.gitignore` should eventually consider:

```text
__pycache__/
*.pyc
.venv/
.env
*.db
*.db-shm
*.db-wal
Data/Temp/
Data/Cache/
Logs/
Build/
```

Exceptions may be made for intentional test fixtures or sample databases.

Never commit:

- passwords
- tokens
- API keys
- client credentials
- production ticket exports

---

# 89. Development Database vs Operational Database

During development:

```text
C:\Dev\F7Hub\Database\Dev\f7hub_dev.db
```

may be acceptable.

Automated tests should instead use isolated temporary databases.

For a packaged application:

```text
%LOCALAPPDATA%\F7Hub\Data\f7hub.db
```

is the preferred architectural direction.

The source repository should not become the permanent storage location for real operational data.

---

# 90. Folder Naming Conventions

General rules:

- use clear English names
- avoid spaces where practical
- use stable naming
- use consistent capitalization
- do not create synonym folders

Avoid structures like:

```text
Utils\
Utilities\
Helpers\
Common\
Shared\
```

all representing the same concept.

Final naming standards belong in:

`15_NamingConventions.md`

---

# 91. Folder Ownership Rule

Every significant folder should have an identifiable owner.

Examples:

| Folder | Owner |
|---|---|
| `Python\f7hub\gui` | Python/PyQt6 application |
| `Python\f7hub\repositories` | Persistence layer |
| `PowerShell\Diagnostics` | PowerShell subsystem |
| `AutoHotkey\Hotkeys` | AHK subsystem |
| `Database\Migrations` | Database architecture |
| `Docs` | Documentation system |
| `Tests\Database` | Database testing |

If folder ownership is unclear, the folder may be unnecessary.

---

# 92. Architecture Dependency Direction

Folder organization should support:

```text
Python\f7hub\gui
        ↓
Python\f7hub\services
        ↓
Python\f7hub\domain
        ↓
Python\f7hub\repositories / infrastructure
        ↓
SQLite / PowerShell / APIs
```

The directory structure should make undesirable coupling harder.

---

# 93. Cross-Language Separation

Do not mix languages within arbitrary feature folders without a strong reason.

Preferred:

```text
Python\
→ application code

PowerShell\
→ administrative scripts

AutoHotkey\
→ desktop automation
```

Cross-language coordination occurs through documented interfaces.

---

# 94. Documentation Structure

Canonical docs remain directly accessible:

```text
C:\Dev\F7Hub\Docs\00_ProjectVision.md
C:\Dev\F7Hub\Docs\01_Project.md
...
C:\Dev\F7Hub\Docs\19_DocumentationIndex.md
```

This makes documentation discovery easy for:

- humans
- VS Code
- Codex
- other coding agents

---

# 95. Codex Folder Rule

Before creating a new folder, a coding agent should:

1. inspect `10_FolderStructure.md`
2. determine the owning subsystem
3. search for an existing appropriate location
4. create a new folder only if necessary
5. update `10_FolderStructure.md` if the new folder represents a meaningful architectural addition

Do not allow implementation to silently redefine repository structure.

---

# 96. Scaffold Strategy

The initial project scaffold should create only stable folders.

Recommended initial scaffold:

```text
F7Hub\
│
├── Python\
│   └── f7hub\
│       ├── app\
│       ├── gui\
│       ├── services\
│       ├── domain\
│       ├── repositories\
│       ├── infrastructure\
│       └── utils\
│
├── AutoHotkey\
│   ├── Core\
│   ├── Hotkeys\
│   ├── Hotstrings\
│   ├── Clipboard\
│   ├── Menus\
│   ├── Launchers\
│   └── Lib\
│
├── PowerShell\
│   ├── Core\
│   ├── Modules\
│   ├── Diagnostics\
│   ├── Reports\
│   ├── Functions\
│   └── Templates\
│
├── Database\
│   ├── Migrations\
│   ├── Seeds\
│   ├── Queries\
│   ├── ERD\
│   └── Dev\
│
├── Config\
│   ├── Defaults\
│   └── Templates\
│
├── Data\
│   ├── Attachments\
│   ├── Imports\
│   ├── Exports\
│   ├── Cache\
│   ├── Temp\
│   └── Samples\
│
├── Docs\
│   ├── Assets\
│   │   ├── Diagrams\
│   │   ├── Mockups\
│   │   └── Screenshots\
│   ├── Research\
│   └── Archive\
│
├── Plugins\
├── Tests\
│   ├── Unit\
│   ├── Integration\
│   ├── Database\
│   ├── GUI\
│   ├── PowerShell\
│   └── Fixtures\
│
├── Assets\
│   ├── Icons\
│   ├── Images\
│   └── Templates\
│
├── Logs\
│   ├── Application\
│   ├── PowerShell\
│   ├── Database\
│   └── Debug\
│
├── Tools\
│   ├── Scripts\
│   ├── Database\
│   └── Development\
│
├── Build\
├── Installer\
└── Releases\
```

This is the recommended initial physical scaffold.

---

# 97. Folders Intentionally Deferred

Do not automatically create all of these until required:

```text
Plugins\HaloPSA\
Plugins\NinjaOne\
Plugins\CIPP\
PowerShell\Modules\Defender\
PowerShell\Modules\Intune\
Python\f7hub\plugins\
Database\Triggers\
Database\Views\
Releases\0.x.x\
```

The documentation may identify them as possible future locations without requiring empty directories.

---

# 98. Scaffold Script

The approved folder structure should be reproducible through a PowerShell script.

Recommended location:

```text
Tools\Scripts\Initialize-F7HubStructure.ps1
```

The script should:

- use `C:\Dev\F7Hub` by default
- be idempotent
- create missing folders
- preserve existing files
- never delete content
- report created/existing folders
- support a configurable root path

The script should not create application source files unless explicitly requested.

---

# 99. Validation Script

A future companion script may validate repository structure.

Recommended:

```text
Tools\Scripts\Test-F7HubStructure.ps1
```

Potential behavior:

```text
Required folder exists
→ PASS

Missing required folder
→ FAIL

Optional folder missing
→ PASS / informational
```

---

# 100. Structure Change Control

Explicit review is required before:

- moving canonical documentation
- moving the Python application root
- restructuring database migration locations
- merging PowerShell and Python subsystems
- replacing the top-level directory model
- introducing a separate backend/server project
- introducing multiple applications inside the same repository
- major plugin structure changes

Small feature-specific folders do not require architectural review if they follow existing structure.

---

# 101. Current Repository Status

This document defines the intended canonical structure.

Repository inspection on 2026-09-03 confirmed:

```text
Top-level canonical directories: PASS
Canonical Docs/00–19 files: PASS
Canonical scaffold script location: PASS
SQLite infrastructure substructure: PASS
Remaining implementation substructure: PLANNED
```

`Python\f7hub\infrastructure\` now contains the verified SQLite path, connection, migration, bootstrap and integrity implementation, with isolated tests under `Tests\Database\`. Other application source areas remain unimplemented. `Database\SQLite\F7Hub.db` is still a zero-byte legacy scaffold artifact rather than the planned development database at `Database\Dev\f7hub_dev.db`; the test suite did not use either file.

Two root-level legacy PowerShell scripts still contain the former OneDrive path. They are not canonical architecture and require a separate source-cleanup decision; this documentation-only review does not modify them. The repository also contains an empty noncanonical `zip\` directory whose disposition remains a follow-up.

---

# 102. Relationship to Other Documents

## `06_SystemArchitecture.md`

Defines:

> How components communicate.

## `10_FolderStructure.md`

Defines:

> Where those components belong in the repository.

## `11_AHKArchitecture.md`

Defines:

> How `AutoHotkey\` is structured internally.

## `12_PowerShellArchitecture.md`

Defines:

> How `PowerShell\` is structured internally.

## `13_PythonArchitecture.md`

Defines:

> How `Python\` is structured internally.

---

# 103. Folder Structure Golden Rules

1. `C:\Dev\F7Hub` is the canonical development root.
2. Python/PyQt6 is the primary application layer.
3. PowerShell owns Windows/Microsoft administration and diagnostics.
4. AutoHotkey owns lightweight desktop automation.
5. SQLite persistence is accessed through Python repositories.
6. Canonical documentation lives directly under `Docs\`.
7. Source and runtime data remain separated.
8. Scripts remain normal source files.
9. Generated data is not committed blindly.
10. Empty speculative folder trees should be avoided.
11. New folders require a clear purpose and owner.
12. Reuse existing structure before creating new structure.
13. Tests remain separate from operational data.
14. Runtime secrets never belong in source-controlled folders.
15. Structural changes must update this document.

---

# 104. Final Structure Principle

The folder tree should explain F7Hub before the code does.

A developer or coding agent looking at:

```text
C:\Dev\F7Hub\
```

should immediately understand:

```text
Python
→ application

PowerShell
→ administration

AutoHotkey
→ desktop automation

Database
→ persistence design

Docs
→ architecture and requirements

Tests
→ validation

Config
→ configuration

Data
→ runtime/import/export data

Assets
→ application resources

Tools
→ development utilities
```

The project structure should grow only when the architecture requires it.

> A folder should exist because it has a responsibility, not because it might contain something someday.
