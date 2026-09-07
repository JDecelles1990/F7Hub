# F7Hub AutoHotkey v2 Architecture

> Document: `Docs/11_AHKArchitecture.md`  
> Project: F7Hub  
> Technology: AutoHotkey v2  
> Purpose: Define how AutoHotkey v2 is used inside F7Hub, including hotkeys, hotstrings, clipboard automation, launchers, quick menus, Windows integration, security boundaries, and communication with the primary Python/PySide6 application.
> Related Documents: `04_UserWorkflows.md`, `05_GUI.md`, `06_SystemArchitecture.md`, `10_FolderStructure.md`, `12_PowerShellArchitecture.md`, `13_PythonArchitecture.md`

---

# 1. Purpose

This document defines the AutoHotkey v2 architecture for F7Hub.

It answers:

> What responsibilities belong to AutoHotkey v2, and how should AHK interact with the rest of F7Hub?

AutoHotkey v2 is used for:

- global hotkeys
- hotstrings
- clipboard automation
- text insertion
- quick menus
- application launching
- window focusing
- lightweight Windows interaction
- technician productivity shortcuts

AutoHotkey is not the primary F7Hub application layer.

The main desktop application is designed to be implemented with:

```text
Python
+
PySide6
```

---

# 2. Technology Version

F7Hub uses:

```text
AutoHotkey v2
```

AutoHotkey v1 syntax must not be introduced into F7Hub source files.

When using external examples or libraries, verify that they support AutoHotkey v2.

---

# 3. AutoHotkey Role

AutoHotkey v2 is the lightweight desktop automation layer.

Primary responsibility:

```text
Keyboard / Clipboard / Windows
          │
          ▼
     AutoHotkey v2
          │
          ▼
   F7Hub Quick Actions
```

AHK complements the Python application.

It should not duplicate the PySide6 application.

---

# 4. Technology Ownership

Responsibilities are divided as follows:

| Concern | Primary Technology |
|---|---|
| Main GUI | Python / PySide6 |
| Application services | Python |
| Persistent database access | Python repositories |
| Windows/M365 administration | PowerShell |
| Global hotkeys | AutoHotkey v2 |
| Hotstrings | AutoHotkey v2 |
| Clipboard hooks | AutoHotkey v2 |
| Lightweight quick menus | AutoHotkey v2 |
| Application/window launching | AutoHotkey v2 |
| Persistent clipboard organization | Python / SQLite |
| Relational persistence | SQLite |

---

# 5. Architectural Principle

The primary rule is:

> AutoHotkey should automate the Windows desktop, not become a second application framework.

Preferred:

```text
AHK Hotkey
   ↓
Resolve Action
   ↓
Launch / Focus / Communicate
   ↓
F7Hub or Approved Tool
```

Avoid:

```text
AHK
 ↓
Full duplicate Ticket GUI
 ↓
Direct SQLite access
 ↓
Separate application state
```

---

# 6. Canonical Folder Structure

Approved structure:

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

Folders should only be added when justified.

---

# 7. Entry Point

The AutoHotkey subsystem should eventually have one clear entry script.

Recommended example:

```text
AutoHotkey\F7Hub.ahk
```

Its responsibilities should remain minimal:

```text
Startup
  ↓
Load Core
  ↓
Load Hotkeys
  ↓
Load Hotstrings
  ↓
Load Clipboard Features
  ↓
Load Menus / Launchers
  ↓
Ready
```

The entry file should not contain every automation function directly.

---

# 8. Core

Folder:

```text
AutoHotkey\Core\
```

Purpose:

Shared AHK initialization and runtime infrastructure.

Possible responsibilities:

- version validation
- environment validation
- path initialization
- common constants
- error handling
- subsystem loading
- F7Hub process detection

---

# 9. Core Rules

`Core` should contain only cross-cutting AHK infrastructure.

Avoid placing:

- ticket workflows
- large clipboard feature logic
- Microsoft administration
- database queries

inside Core.

---

# 10. Hotkeys

Folder:

```text
AutoHotkey\Hotkeys\
```

Purpose:

Define global keyboard shortcuts.

Potential examples:

```text
F7
→ Open or focus F7Hub

Ctrl+Alt+K
→ Open F7Hub command/search workflow

Ctrl+Alt+C
→ Open clipboard tools

Ctrl+Alt+P
→ Open PowerShell-related action
```

Exact shortcuts must be approved and documented.

---

# 11. Hotkey Design Rules

Hotkeys should:

- avoid common Windows conflicts
- avoid common application conflicts
- remain easy to remember
- execute predictable actions
- be grouped logically
- be configurable where appropriate

Do not create excessive global shortcuts.

A hotkey is useful when it saves meaningful repeated effort.

---

# 12. Hotkey Scope

Not every shortcut should be global.

Possible scopes:

```text
Global
Application-specific
Window-specific
Context-specific
```

Example:

A ticket-note formatting shortcut may only be appropriate in selected applications or when F7Hub is active.

---

# 13. Hotstrings

Folder:

```text
AutoHotkey\Hotstrings\
```

Purpose:

Provide reusable text expansions.

Examples:

```text
;ticketclose
→ standard ticket closure wording

;escalate
→ escalation template

;mfa
→ common MFA troubleshooting text
```

Hotstrings should be:

- predictable
- editable
- reviewable
- non-destructive

---

# 14. Hotstring Design

Hotstrings may support:

- static text
- dynamic text
- clipboard insertion
- date/time insertion
- ticket templates
- common technician phrases

Persistent large template libraries should eventually be managed through F7Hub rather than hard-coded indefinitely in AHK.

---

# 15. Clipboard Architecture

Folder:

```text
AutoHotkey\Clipboard\
```

AHK responsibilities may include:

- detecting clipboard changes
- reading clipboard text
- inserting selected content
- applying quick transformations
- restoring clipboard contents when appropriate

Python responsibilities may include:

- persistent history
- metadata
- categorization
- search
- SQLite storage
- GUI presentation

---

# 16. Clipboard Boundary

Preferred:

```text
Windows Clipboard
      ↓
AutoHotkey v2
      ↓
Quick Transformation / Capture
      ↓
Python Application if Persistence Needed
      ↓
SQLite
```

Avoid:

```text
AutoHotkey
   ↓
Direct SQLite Writes
```

unless explicitly approved.

---

# 17. Clipboard Transformations

Possible AHK transformations:

- remove formatting
- trim whitespace
- normalize line breaks
- uppercase
- lowercase
- title case
- ticket-note formatting
- wrap text
- copy selected text into a template

Complex parsing may be delegated to Python when appropriate.

---

# 18. Sensitive Clipboard Data

Clipboard content must be treated as untrusted and potentially sensitive.

AHK should not automatically persist every copied item.

Potential protections:

- persistence disabled by default or configurable
- ignore known sensitive applications
- exclude suspected secrets
- clear temporary clipboard data
- allow manual clearing
- avoid logging clipboard contents

---

# 19. Menus

Folder:

```text
AutoHotkey\Menus\
```

Purpose:

Lightweight technician popup menus.

Potential contents:

```text
F7 Quick Menu
├── Open F7Hub
├── Tickets
├── Clipboard
├── PowerShell
├── Windows Tools
└── Launchers
```

AHK menus should remain small and fast.

They should not reproduce complex PySide6 screens.

---

# 20. Launcher Architecture

Folder:

```text
AutoHotkey\Launchers\
```

Purpose:

Launch or focus commonly used resources.

Possible targets:

- F7Hub
- Windows Terminal
- PowerShell
- VS Code
- File Explorer
- browser
- Microsoft admin portals
- system utilities

---

# 21. Window Focus Behavior

When possible, launcher actions should prefer:

```text
Detect Existing Window
        │
        ├── Found
        │    ↓
        │  Activate
        │
        └── Not Found
             ↓
           Launch
```

This reduces unnecessary duplicate application instances.

---

# 22. Windows Utility Launching

AHK may provide quick access to tools such as:

```text
Task Manager
Event Viewer
Services
Device Manager
Network Connections
Registry Editor
Windows Terminal
System Information
```

Administrative elevation must not occur silently.

---

# 23. External URLs

AHK may launch approved web portals.

Examples:

- Microsoft 365 Admin Center
- Entra Admin Center
- Exchange Admin Center
- Intune
- Defender
- HaloPSA
- NinjaOne

URLs should preferably come from configuration or registered actions rather than being duplicated across scripts.

---

# 24. Helpers

Folder:

```text
AutoHotkey\Helpers\
```

Purpose:

Small reusable helper functions.

Examples:

- window detection
- safe path handling
- process checking
- clipboard restoration
- notifications

Avoid creating a miscellaneous dumping ground.

If a helper clearly belongs to another subsystem, place it there.

---

# 25. Libraries

Folder:

```text
AutoHotkey\Lib\
```

Purpose:

Reusable internal or approved external AHK v2 libraries.

External libraries must be:

- AutoHotkey v2 compatible
- reviewed
- documented
- license-compatible

Do not copy random code from forums into production source without review.

---

# 26. Templates

Folder:

```text
AutoHotkey\Templates\
```

Purpose:

Developer templates for creating new AHK automation components.

Examples:

```text
HotkeyTemplate.ahk
LauncherTemplate.ahk
ClipboardActionTemplate.ahk
```

Templates are development aids, not runtime configuration.

---

# 27. Configuration

AHK should avoid large amounts of hard-coded configuration.

Configurable values may include:

- hotkeys
- executable paths
- URLs
- feature toggles
- menu items

Canonical application configuration belongs under:

```text
Config\
```

AHK may read approved configuration through a defined format.

---

# 28. Configuration Format

The exact configuration format should be selected based on complexity.

Possible options:

- INI for simple AHK-specific settings
- JSON through Python-generated configuration
- environment or command-line values

Do not introduce several formats for the same settings without a reason.

---

# 29. Communication with Python

AHK and the main Python application may need to communicate.

Start with the simplest sufficient mechanism.

Preferred progression:

```text
1. Launch / Activate F7Hub
2. Command-line arguments
3. Structured local messages if required
4. More advanced IPC only if justified
```

Avoid introducing complex IPC before a real requirement exists.

---

# 30. Command-Line Communication

Example conceptual flow:

```text
AHK Hotkey
    ↓
Start F7Hub with command
    ↓
python/f7hub.exe --action open-search
    ↓
Python validates action
    ↓
Application performs registered action
```

The command must be validated by Python.

AHK should not be allowed to invoke arbitrary internal code by string name.

---

# 31. Structured Messages

If richer communication becomes necessary, JSON may be used.

Example conceptual payload:

```json
{
  "action": "open_ticket",
  "ticket_id": 10254
}
```

The receiving application must validate:

- action
- schema
- values

---

# 32. IPC Decision Rule

Before introducing:

- named pipes
- sockets
- local HTTP
- Windows messages
- shared memory

document:

- why simple process invocation is insufficient
- security impact
- lifecycle behavior
- error handling
- testing requirements

---

# 33. Communication with PowerShell

AHK should not become the primary PowerShell execution controller.

Preferred:

```text
AHK
 ↓
F7Hub Python Application
 ↓
PowerShellService
 ↓
PowerShellGateway
 ↓
Approved Script
```

For simple standalone utility launching, direct AHK-to-PowerShell invocation may be acceptable if explicitly designed.

---

# 34. Direct PowerShell Invocation

If AHK directly launches a PowerShell utility:

- use a known script path
- validate inputs
- avoid shell-string concatenation
- avoid embedded credentials
- avoid silent elevation
- capture/report failure where practical

Complex administrative execution should remain under the main F7Hub execution layer.

---

# 35. Database Boundary

AutoHotkey should not normally access SQLite directly.

Preferred:

```text
AutoHotkey
     ↓
Python Service
     ↓
Repository
     ↓
SQLite
```

Reasons:

- one database-access layer
- transaction consistency
- parameterization
- easier testing
- simpler migrations
- reduced schema coupling

---

# 36. No Direct Schema Knowledge

AHK should not need to know:

```text
tickets table columns
foreign keys
migration version
FTS tables
```

AHK should operate through application-level commands.

This allows the database schema to evolve independently.

---

# 37. Error Handling

AHK automation should fail visibly and safely.

Typical pattern:

```text
Action
  ↓
Validation
  ↓
Execution
  ↓
Success / Failure
  ↓
User Feedback
```

Errors should not be silently ignored.

---

# 38. User Feedback

Lightweight AHK feedback may use:

- tray notifications
- tooltips
- brief status messages
- F7Hub GUI feedback

Avoid disruptive message boxes for routine successful operations.

---

# 39. Logging

AHK should log only useful operational information.

Possible logging:

- startup failure
- launcher failure
- missing application path
- invalid configuration
- automation exception

Do not log:

- passwords
- tokens
- clipboard secrets
- sensitive ticket data unnecessarily

---

# 40. Logging Ownership

Where practical, application-wide logging should ultimately be coordinated with the main F7Hub logging system.

Standalone AHK startup errors may use:

```text
Logs\Application\
```

or another approved path.

Do not create multiple redundant AHK log systems.

---

# 41. Security Boundary

AHK can:

- type text
- launch programs
- activate windows
- interact with clipboard
- automate keyboard/mouse actions

This gives it significant local power.

Therefore all automation must treat external input as untrusted.

---

# 42. Unsafe Input Sources

Potential untrusted inputs include:

- clipboard
- ticket content
- AI responses
- URLs
- external configuration
- user-selected files
- downloaded content

Do not convert arbitrary text into executable commands.

---

# 43. Shell Safety

Avoid:

```ahk
Run("powershell.exe " userInput)
```

where `userInput` is uncontrolled.

Prefer:

- known executable
- known script
- validated arguments
- safe quoting
- allowlisted actions

---

# 44. Elevation

AHK should not silently run itself or other tools as administrator.

If an operation requires elevation:

```text
Identify Requirement
      ↓
Explain to Technician
      ↓
Explicit User Action
      ↓
Elevated Execution
```

Least privilege remains the default.

---

# 45. UI Automation

AHK may automate external application interfaces where no better integration exists.

However UI automation is inherently fragile.

Preferred order:

```text
API
 ↓
Command-line interface
 ↓
PowerShell
 ↓
Application integration
 ↓
UI automation
```

UI automation should generally be a last resort.

---

# 46. Fragile Automation

UI automation may break because of:

- window title changes
- language differences
- UI redesign
- timing
- focus changes
- display scaling
- user interaction

Any important UI automation should include:

- validation
- timeouts
- failure handling
- clear assumptions

---

# 47. Sleep Usage

Fixed `Sleep` calls may sometimes be necessary for desktop automation.

However, prefer state-based waiting where possible.

Less reliable:

```text
Send action
Sleep 2000
Continue
```

Better:

```text
Send action
Wait for expected window/control/state
Continue
```

Timeouts should prevent indefinite waits.

---

# 48. Text Insertion

When sending significant blocks of text, clipboard-based insertion may be more reliable than individual simulated keystrokes.

Conceptual flow:

```text
Save Existing Clipboard
      ↓
Set Temporary Text
      ↓
Paste
      ↓
Restore Clipboard
```

Care must be taken not to destroy user clipboard data.

---

# 49. Clipboard Restoration

Clipboard restoration should:

- preserve previous content where practical
- wait for clipboard operations when needed
- avoid restoring stale content over new intentional user clipboard changes

This must be implemented carefully.

---

# 50. Application Detection

Launchers should use reliable application detection.

Potential methods:

- executable process
- window class
- window executable
- known title patterns

Avoid relying solely on volatile window titles.

---

# 51. F7Hub Launcher

A primary AHK use case is launching or focusing F7Hub.

Conceptual flow:

```text
Press F7
   ↓
Is F7Hub Running?
   │
   ├── Yes
   │    ↓
   │  Activate
   │
   └── No
        ↓
      Launch
```

This can become the core quick-access behavior behind the F7Hub name.

---

# 52. F7Hub Context Menu

A lightweight AHK menu may eventually provide:

```text
F7Hub
├── Open F7Hub
├── New Ticket
├── Search
├── Clipboard
├── Run Diagnostic
├── PowerShell Tools
└── Windows Tools
```

Where possible, items should delegate to registered F7Hub commands.

---

# 53. Hotkey Registry

As the number of hotkeys grows, F7Hub should avoid scattered definitions.

A controlled hotkey registry or clearly organized files should document:

- shortcut
- action ID
- scope
- description
- enabled state

Exact implementation should remain simple.

---

# 54. Action IDs

AHK actions should use stable conceptual identifiers where useful.

Examples:

```text
app.open
ticket.new
search.open
clipboard.open
diagnostic.open
powershell.open
```

These identifiers may map to commands understood by the Python application.

---

# 55. Avoid Hard-Coding Application Behavior

Avoid:

```ahk
F7::Run("C:\Dev\F7Hub\Python\some_random_internal_file.py")
```

Prefer an approved application entry point.

Example:

```text
F7
→ launch F7Hub application entry point
```

Internal implementation paths should be free to change.

---

# 56. Process Ownership

AHK may launch processes but should not automatically assume ownership of every process it starts.

Examples:

F7Hub itself may be tracked.

An external browser opened to Microsoft 365 should generally not be terminated when AHK exits.

---

# 57. Shutdown

AHK shutdown should:

- release transient state
- stop owned timers
- unregister hooks naturally
- preserve user clipboard where possible
- log meaningful failures

It should not terminate unrelated applications.

---

# 58. Performance

AHK scripts should remain lightweight.

Avoid:

- aggressive polling loops
- unnecessary timers
- constant disk writes
- repeated process scans
- expensive clipboard processing

Prefer event-driven behavior where supported.

---

# 59. Startup Performance

AHK startup should be fast.

Load:

- required hotkeys
- required hotstrings
- core helpers

Avoid loading large unused feature libraries at startup.

---

# 60. Maintainability

AHK code should remain modular.

Prefer:

```text
F7Hub.ahk
   ↓
Core
   ↓
Hotkeys / Clipboard / Menus / Launchers
```

Avoid a single thousands-of-lines script containing every F7Hub automation.

---

# 61. Functions and Classes

Use functions and classes where they improve clarity.

Do not force object-oriented design onto trivial automation.

Good candidates for classes may include:

- launcher registry
- clipboard manager
- configuration wrapper

Simple hotkey handlers may remain functions.

Use the simplest maintainable structure.

---

# 62. AutoHotkey v2 Syntax Standard

All project AHK code must follow AutoHotkey v2 conventions.

Examples include:

- function-call syntax
- expression syntax
- v2 hotkey syntax
- v2 object model
- v2 error handling

Do not copy AHK v1 commands without conversion.

---

# 63. Includes

Include files should be explicit.

Avoid deeply nested include chains that make startup behavior difficult to understand.

The main entry script should make major subsystem loading visible.

---

# 64. Path Resolution

Do not assume the current working directory is always the project root.

Paths should be resolved relative to:

- script location
- configured application paths
- installed application root

Avoid brittle hard-coded development-only paths.

---

# 65. Development vs Installed Paths

Development:

```text
C:\Dev\F7Hub\
```

Installed application paths may differ.

AHK should not assume that production F7Hub will permanently run from:

```text
C:\Dev\F7Hub\
```

Deployment-aware path resolution should be introduced before packaging.

---

# 66. Tests

AHK automation should be tested according to risk.

Possible testing categories:

- syntax validation
- helper function tests
- launcher tests
- hotkey tests
- clipboard behavior
- integration tests with Python
- manual UI automation tests

Not every desktop interaction can be reliably unit tested.

---

# 67. Manual Test Documentation

For UI-dependent automation, documented manual tests may be appropriate.

Example:

```text
TEST-AHK-LAUNCH-001

1. Ensure F7Hub is closed.
2. Press F7.
3. Confirm one F7Hub instance launches.
4. Press F7 again.
5. Confirm existing window receives focus.

Expected:
No duplicate instance.
```

---

# 68. Test Status

Use:

```text
PASS
FAIL
NOT RUN
BLOCKED
```

Never claim an AHK automation works across applications unless it was actually tested.

---

# 69. High-Priority Initial AHK Features

Recommended early AHK scope:

```text
1. F7Hub launch/focus hotkey
2. Quick launcher menu
3. Core hotstrings
4. Clipboard text insertion
5. Small safe clipboard transformations
6. Windows utility launchers
```

This provides immediate technician value without creating architectural complexity.

---

# 70. Second-Stage AHK Features

Later:

```text
Application-specific hotkeys
Dynamic quick actions
F7Hub command forwarding
Advanced clipboard workflows
Context-aware menus
```

---

# 71. Deferred AHK Features

Do not prioritize:

- large standalone AHK GUI modules
- direct database CRUD
- complex Microsoft 365 administration in AHK
- large diagnostic engines
- custom IPC servers
- extensive mouse-coordinate automation

unless a real requirement justifies them.

---

# 72. Example F7Hub Hotkey Flow

```text
Technician presses F7
        │
        ▼
AutoHotkey v2
        │
        ▼
Check F7Hub process
        │
   ┌────┴────┐
   │         │
Running    Not Running
   │         │
   ▼         ▼
Activate   Launch
   │         │
   └────┬────┘
        ▼
Technician Workspace
```

---

# 73. Example Clipboard Workflow

```text
Technician Copies Text
        │
        ▼
Windows Clipboard
        │
        ▼
AutoHotkey v2
        │
        ├── Quick Transform
        │
        └── Send to F7Hub if Persistence Requested
                    │
                    ▼
                Python Service
                    │
                    ▼
                 SQLite
```

---

# 74. Example Quick Command Flow

```text
AHK Hotkey
    │
    ▼
Action ID
    │
    ▼
F7Hub Application
    │
    ▼
Command Registry
    │
    ▼
Application Service
```

This keeps desktop automation separate from business logic.

---

# 75. Anti-Patterns

Avoid:

## AutoHotkey Monolith

One large `.ahk` file controls all F7Hub functionality.

## AHK as Database Layer

AHK performs direct CRUD against core SQLite tables.

## AHK as Microsoft Administration Layer

Complex Graph or Exchange administration is implemented directly in AHK.

## AHK GUI Duplication

Large AHK windows recreate PySide6 modules.

## Hard-Coded Paths Everywhere

Every script embeds `C:\Dev\F7Hub`.

## Blind Keystroke Automation

Large sequences rely entirely on fixed `Sleep` delays.

## Clipboard Destruction

Automation replaces clipboard content without preserving user data.

## Command Injection

Untrusted clipboard or ticket text becomes shell input.

---

# 76. Design Decision Rule

Before implementing something in AutoHotkey, ask:

1. Is this primarily desktop automation?
2. Does it involve global keyboard input?
3. Does it involve clipboard interaction?
4. Does it involve lightweight window/process handling?
5. Would Python/PySide6 provide a cleaner application-level solution?
6. Would PowerShell provide a safer administration solution?
7. Does an existing AHK component already provide it?

If the task is not fundamentally desktop automation, it probably belongs elsewhere.

---

# 77. Cross-Technology Boundary

Preferred architecture:

```text
             Python / PySide6
             Primary F7Hub App
                    │
         ┌──────────┴──────────┐
         │                     │
         ▼                     ▼
   PowerShell              AutoHotkey v2
 Administration         Desktop Automation
         │                     │
         └──────────┬──────────┘
                    ▼
                  Windows
```

SQLite remains accessed through Python repositories.

---

# 78. Documentation Synchronization

Changes to AutoHotkey architecture must update:

```text
11_AHKArchitecture.md
```

If the change affects:

- system communication
- IPC
- GUI boundaries
- repository structure

also review:

```text
06_SystemArchitecture.md
10_FolderStructure.md
13_PythonArchitecture.md
```

Major feature changes may also require:

```text
03_Features.md
04_UserWorkflows.md
18_ChangeLog.md
```

---

# 79. Current Implementation Status

On 2026-09-05, `AutoHotkey/F7Hub.ahk` and `Launchers/F7HubLauncher.ahk` implement the F7 launch/focus slice. The entry point registers F7 with one shortcut-script instance and one handler at a time. The launcher derives the project root from the script location, uses `.venv/Scripts/pythonw.exe -m f7hub` without a console, and supplies the project's Python path to the child process.

Existing windows are recognized by exact `F7Hub` title, Qt window class and Python process name. F7 activates the window or restores it from minimized state. A pending process is retained after a 15-second startup timeout to prevent another launch on retry. Missing files, launch failure, early process exit, startup timeout and denied activation produce actionable feedback. This is a development launcher for one checkout: separately started copies with the same window identity are not distinguished. It is not an application-wide single-instance lock.

Start the shortcut by opening `AutoHotkey/F7Hub.ahk` with AutoHotkey v2. Use its tray menu to exit or reload. Login startup registration is not installed by this slice. The default app uses `Database/Dev/f7hub_dev.db`; the launcher class accepts an explicit database path for isolated live tests.

```text
F7 launch/focus: VERIFIED
Prior repository live launcher checks with AutoHotkey 2.0.26: PASS — 2026-09-05
Manual Windows verification: PASS — 2026-09-07
Recent isolated automated recheck: BLOCKED — shell wait timeout
Other AutoHotkey features: PLANNED
```

`Tests/AutoHotkey/test_f7hub_launcher.ahk` accepts a new isolated database path and refuses to run while F7Hub or its shortcut is already active. It checks missing runtime, repeated timeout without duplicate launch, cold launch, parent environment restoration, focus, minimized restoration, repeated calls, unrelated window rejection, actual global F7 input and duplicate shortcut startup. The test closes only the app and shortcut it starts.

Remaining sections describe intended architecture; clipboard integration, quick menus and richer Python command communication remain planned.

---

# 80. Initial Implementation Sequence

Recommended AHK development sequence:

```text
1. AutoHotkey v2 entry point
        ↓
2. Core path/config handling
        ↓
3. F7 launch/focus hotkey
        ↓
4. Launcher helpers
        ↓
5. Quick menu
        ↓
6. Hotstrings
        ↓
7. Clipboard helpers
        ↓
8. Python command integration
        ↓
9. Tests / manual validation
```

Each step should remain independently testable.

---

# 81. Completion Checklist

An AHK feature is complete when applicable:

```text
[ ] AutoHotkey v2 syntax used
[ ] Requirement identified
[ ] Existing automation inspected
[ ] Correct folder selected
[ ] Input validated
[ ] Hard-coded paths avoided
[ ] Clipboard preserved where relevant
[ ] Elevation behavior explicit
[ ] Error handling implemented
[ ] Security considered
[ ] Tests executed
[ ] Documentation synchronized
```

---

# 82. AutoHotkey Golden Rules

1. F7Hub uses AutoHotkey v2 only.
2. Python/PySide6 remains the primary application.
3. AHK owns desktop automation.
4. PowerShell owns administration and diagnostics.
5. AHK should not directly own SQLite persistence.
6. Use global hotkeys sparingly.
7. Keep hotstrings predictable.
8. Protect clipboard contents.
9. Avoid blind keystroke automation when better interfaces exist.
10. Never silently elevate privileges.
11. Never turn untrusted text into commands.
12. Prefer APIs and PowerShell over fragile UI automation.
13. Use state-based waiting where possible.
14. Avoid hard-coded development paths.
15. Keep AHK modular and lightweight.
16. Delegate business logic to Python services.
17. Add complexity only when a real workflow requires it.

---

# 83. Final Architecture Summary

AutoHotkey v2 is F7Hub's Windows productivity accelerator.

Its role is:

```text
Keyboard
Clipboard
Windows
Launchers
Quick Menus
     │
     ▼
AutoHotkey v2
     │
     ▼
F7Hub Actions
```

It should make common technician interactions faster without becoming the application itself.

The architectural boundary is:

```text
PySide6
→ full application interface

Python
→ services, domain logic and persistence coordination

PowerShell
→ Windows and Microsoft administration

AutoHotkey v2
→ keyboard, clipboard and desktop automation

SQLite
→ relational persistence
```

The guiding principle is:

> Use AutoHotkey v2 where Windows automation provides a clear productivity advantage, and use the primary F7Hub application for everything that requires persistent state, complex workflows, or business logic.
