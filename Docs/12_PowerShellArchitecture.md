# F7Hub PowerShell Architecture

> Document: `Docs/12_PowerShellArchitecture.md`  
> Project: F7Hub  
> Technology: PowerShell 7  
> Purpose: Define how PowerShell is used inside F7Hub for Windows administration, Microsoft 365 administration, diagnostics, reporting, automation, structured execution, and integration with the Python/PyQt6 application.  
> Related Documents: `02_ProductRequirements.md`, `04_UserWorkflows.md`, `06_SystemArchitecture.md`, `07_Database.md`, `10_FolderStructure.md`, `11_AHKArchitecture.md`, `13_PythonArchitecture.md`

---

# 1. Purpose

This document defines the PowerShell architecture for F7Hub.

It answers:

> What responsibilities belong to PowerShell, how should scripts be organized, and how should PowerShell communicate with the rest of F7Hub?

PowerShell is used for:

- Windows administration
- Microsoft 365 administration
- Microsoft Graph operations where PowerShell is appropriate
- Exchange Online
- Entra ID
- Intune
- Defender
- Teams
- SharePoint
- networking diagnostics
- system diagnostics
- reporting
- structured troubleshooting scripts
- technician automation

PowerShell is not the primary F7Hub application layer.

The main application remains:

```text
Python
+
PyQt6
```

---

# 2. PowerShell Version

Preferred runtime:

```text
PowerShell 7
```

Executable:

```text
pwsh.exe
```

Windows PowerShell 5.1 may be used only when required by a specific module, API, legacy component, or compatibility constraint.

Do not assume PowerShell 5.1 compatibility unless required.

---

# 3. PowerShell Role

PowerShell is F7Hub's administrative and diagnostic execution layer.

Conceptually:

```text
Technician
    ↓
F7Hub GUI
    ↓
Python Service
    ↓
PowerShell Gateway
    ↓
Approved PowerShell Script
    ↓
Windows / Microsoft Service
    ↓
Structured Result
    ↓
F7Hub
```

PowerShell should provide capabilities rather than own application state.

---

# 4. Technology Ownership

| Concern | Primary Technology |
|---|---|
| Main GUI | Python / PyQt6 |
| Application services | Python |
| Domain logic | Python |
| Database persistence | Python repositories / SQLite |
| Windows administration | PowerShell |
| Microsoft 365 administration | PowerShell / Microsoft Graph |
| Diagnostic scripts | PowerShell |
| Reports from administrative data | PowerShell where appropriate |
| Desktop hotkeys | AutoHotkey v2 |
| Clipboard hooks | AutoHotkey v2 |
| Relational persistence | SQLite |

---

# 5. Architectural Principle

The primary rule is:

> PowerShell performs administrative operations and diagnostics. Python controls when and why they run.

Preferred:

```text
GUI
 ↓
Application Service
 ↓
PowerShellService
 ↓
PowerShellGateway
 ↓
Script
```

Avoid:

```text
GUI Button
 ↓
Raw PowerShell String
 ↓
pwsh.exe
```

---

# 6. Canonical Folder Structure

Approved PowerShell structure:

```text
PowerShell\
├── Core\
├── Modules\
├── Diagnostics\
├── Reports\
├── Functions\
└── Templates\
```

PowerShell tests belong under the canonical top-level `Tests\PowerShell\` hierarchy.

Technology-specific folders under `Modules\` should be created only when justified.

Potential examples:

```text
PowerShell\Modules\
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

---

# 7. Core

Folder:

```text
PowerShell\Core\
```

Purpose:

Provide shared PowerShell execution conventions.

Potential responsibilities:

- common result creation
- validation helpers
- shared error handling
- environment detection
- module validation
- logging helpers
- common parameter handling

Core should remain small.

---

# 8. Functions

Folder:

```text
PowerShell\Functions\
```

Purpose:

Reusable PowerShell functions shared by multiple scripts.

Examples:

```text
Test-F7HubEnvironment
New-F7HubResult
Test-RequiredModule
ConvertTo-F7HubError
```

Shared functions should not contain unrelated domain-specific logic.

---

# 9. Modules

Folder:

```text
PowerShell\Modules\
```

Purpose:

Organize administrative automation by technology or service.

Example:

```text
Modules\
├── MicrosoftGraph\
├── ExchangeOnline\
├── EntraID\
├── Intune\
├── Defender\
├── Teams\
├── SharePoint\
├── Windows\
└── Networking\
```

The folder structure should reflect actual automation responsibilities.

---

# 10. Microsoft 365

Potential location:

```text
PowerShell\Modules\Microsoft365\
```

Purpose:

General Microsoft 365 operations that do not clearly belong to a more specialized service.

Examples may include:

- tenant information
- licensing checks
- service health support
- user environment diagnostics

Avoid duplicating functionality that belongs in:

- Exchange Online
- Entra ID
- Intune
- Teams
- SharePoint

---

# 11. Microsoft Graph

Potential location:

```text
PowerShell\Modules\MicrosoftGraph\
```

Purpose:

Administrative and diagnostic workflows using supported Microsoft Graph PowerShell tooling.

Possible capabilities:

- user lookup
- group lookup
- license information
- device information
- directory queries
- supported administrative changes

Graph operations must follow least privilege.

---

# 12. Entra ID

Potential location:

```text
PowerShell\Modules\EntraID\
```

Possible responsibilities:

- user diagnostics
- group membership
- sign-in-related information where available
- directory object queries
- account state checks

Modern supported tooling should be preferred over deprecated Azure AD modules.

---

# 13. Exchange Online

Potential location:

```text
PowerShell\Modules\ExchangeOnline\
```

Possible responsibilities:

- mailbox diagnostics
- permissions
- shared mailboxes
- distribution groups
- mail flow support
- mailbox configuration
- recipient queries

Use supported Exchange Online PowerShell modules.

---

# 14. Intune

Potential location:

```text
PowerShell\Modules\Intune\
```

Possible responsibilities:

- device context
- compliance information
- configuration diagnostics
- application deployment information
- enrollment-related investigation

Implementation may use Graph where appropriate.

---

# 15. Defender

Potential location:

```text
PowerShell\Modules\Defender\
```

Possible responsibilities:

- endpoint diagnostics
- security state
- device protection checks
- approved investigation helpers

Security actions require additional review.

---

# 16. Teams

Potential location:

```text
PowerShell\Modules\Teams\
```

Possible responsibilities:

- Teams user diagnostics
- supported configuration queries
- service-related administrative tasks

---

# 17. SharePoint

Potential location:

```text
PowerShell\Modules\SharePoint\
```

Possible responsibilities:

- site information
- permissions diagnostics
- supported administrative workflows

---

# 18. Windows

Potential location:

```text
PowerShell\Modules\Windows\
```

Possible responsibilities:

- system information
- services
- processes
- event logs
- storage
- network configuration
- Windows Update diagnostics
- local account checks
- registry queries where appropriate

---

# 19. Networking

Potential location:

```text
PowerShell\Modules\Networking\
```

Possible capabilities:

- DNS resolution
- gateway reachability
- IP configuration
- routing
- TCP connectivity
- adapter status
- proxy state
- network reset helpers

Diagnostics should distinguish information collection from remediation.

---

# 20. Diagnostics

Folder:

```text
PowerShell\Diagnostics\
```

Purpose:

Contain scripts designed for use by the F7Hub Diagnostic Engine.

Diagnostic scripts should prefer:

- read-only inspection
- predictable parameters
- structured results
- clear status
- explicit remediation separation

---

# 21. Diagnostic Script Principle

A diagnostic script should answer a narrow question.

Good:

```text
Test-DnsHealth.ps1
Test-OutlookConnectivity.ps1
Get-DeviceComplianceState.ps1
```

Less desirable:

```text
Fix-Everything.ps1
```

Narrow scripts are:

- easier to test
- easier to reuse
- safer
- easier to explain
- easier to compose into workflows

---

# 22. Diagnostic vs Remediation

Diagnostics and remediation should be separated where practical.

Example:

```text
Test-DnsHealth.ps1
→ diagnostic

Reset-DnsConfiguration.ps1
→ remediation
```

This makes technician intent explicit.

---

# 23. Reports

Folder:

```text
PowerShell\Reports\
```

Purpose:

Scripts that collect or transform administrative information into structured reports.

Generated files should normally be written to:

```text
Data\Exports\
```

not stored beside source scripts.

---

# 24. Templates

Folder:

```text
PowerShell\Templates\
```

Purpose:

Provide reusable development templates.

Examples:

```text
DiagnosticScript.Template.ps1
AdministrativeAction.Template.ps1
Report.Template.ps1
```

Templates should reinforce architectural conventions.

---

# 25. Script Storage

PowerShell source remains as normal version-controlled `.ps1`, `.psm1`, and `.psd1` files.

SQLite may store:

- script identifier
- relative path
- title
- description
- category
- version
- parameters
- privilege requirement
- risk
- tags
- execution history

Do not store full PowerShell source in SQLite by default.

---

# 26. Script Registry

F7Hub should eventually maintain a script registry.

Conceptual flow:

```text
PowerShell Script File
        ↓
Script Registry Metadata
        ↓
F7Hub Script Library
```

Metadata may identify:

- script ID
- file path
- operation type
- supported platform
- required modules
- risk
- privilege
- parameters

---

# 27. Script Types

Useful conceptual classifications:

```text
DIAGNOSTIC
REMEDIATION
ADMINISTRATIVE
REPORT
UTILITY
INTEGRATION
```

A script's type should help F7Hub determine how it can be executed.

---

# 28. Risk Classification

Scripts should eventually support a simple risk model.

Example:

```text
LOW
→ read-only information gathering

MEDIUM
→ reversible configuration change

HIGH
→ impactful administrative change

CRITICAL
→ destructive or broad privileged operation
```

Exact risk semantics should remain documented and consistent.

---

# 29. Privilege Classification

Scripts may require:

```text
STANDARD_USER
LOCAL_ADMIN
M365_AUTHENTICATED
M365_PRIVILEGED
SPECIAL_ROLE
```

F7Hub should identify this before execution.

---

# 30. Structured Result Contract

PowerShell scripts used by F7Hub should return structured data where practical.

Preferred JSON contract:

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

This contract should remain machine-readable.

---

# 31. Result Status

Recommended script result statuses:

```text
PASS
FAIL
WARNING
ERROR
NOT_APPLICABLE
```

These describe operation results.

They are distinct from project test statuses:

```text
PASS
FAIL
NOT RUN
BLOCKED
```

---

# 32. Result Object

PowerShell should construct results consistently.

Conceptually:

```powershell
$result = @{
    schemaVersion = 1
    operation     = 'Test-DnsHealth'
    success       = $true
    status        = 'PASS'
    message       = 'DNS resolution succeeded.'
    data          = @{}
    warnings      = @()
    errors        = @()
}
```

Then:

```powershell
$result | ConvertTo-Json -Depth 10
```

---

# 33. stdout Contract

For machine-integrated scripts, stdout should contain predictable structured output.

Avoid mixing:

```text
human banners
debug text
Write-Host decoration
JSON
```

on the same machine-readable stream.

Debug information should use appropriate verbose/debug streams or logging.

---

# 34. stderr and Errors

Execution architecture should capture:

- stdout
- stderr
- exit code
- timeout
- execution duration

PowerShell exceptions should be translated into structured errors where possible.

---

# 35. Exit Codes

Scripts should use meaningful process exit codes.

Recommended baseline:

```text
0
→ successful execution

non-zero
→ execution failed
```

Do not use dozens of undocumented exit codes.

If more detail is required, return it inside the structured result.

---

# 36. Error Handling

Scripts should generally use:

```powershell
$ErrorActionPreference = 'Stop'
```

within controlled scripts where terminating behavior is required.

Potential pattern:

```powershell
try {
    # operation
}
catch {
    # structured error result
}
```

Do not suppress errors without explanation.

---

# 37. Parameters

PowerShell scripts should expose explicit parameters.

Example:

```powershell
param(
    [Parameter(Mandatory)]
    [string]$ComputerName
)
```

Avoid hidden dependencies on:

- global variables
- manual edits
- current shell state

---

# 38. Parameter Validation

Use PowerShell validation where appropriate:

```powershell
[ValidateNotNullOrEmpty()]
[string]$UserPrincipalName
```

Other options include:

```text
ValidateSet
ValidateRange
ValidatePattern
ValidateScript
```

Application-side validation should also exist where required.

---

# 39. Parameter Security

User input must not be concatenated into arbitrary command strings.

Preferred:

```text
known script
+
validated arguments
```

Avoid:

```text
Invoke-Expression
```

for dynamic user-controlled execution.

---

# 40. Invoke-Expression

`Invoke-Expression` should generally be prohibited in F7Hub automation unless a specific reviewed requirement proves it necessary.

It creates unnecessary command-injection risk.

---

# 41. Shell Execution

Python should invoke PowerShell using:

- explicit executable path
- explicit script path
- separate argument values
- controlled working directory
- timeout
- captured streams

Avoid building one giant shell command string.

---

# 42. Execution Flow

Preferred execution architecture:

```text
Technician
    ↓
GUI
    ↓
ScriptService
    ↓
Validate Script Registration
    ↓
Validate Parameters
    ↓
Privilege Check
    ↓
PowerShellGateway
    ↓
pwsh.exe
    ↓
.ps1 Script
    ↓
Structured JSON
    ↓
Parse / Validate
    ↓
Display Result
    ↓
Record History
```

---

# 43. Python-to-PowerShell Boundary

Python should know:

- script path
- script metadata
- expected parameters
- timeout
- expected result schema

Python should not need to understand internal PowerShell implementation details.

---

# 44. PowerShell-to-Python Boundary

PowerShell should return:

```text
structured result
exit status
errors
warnings
```

It should not directly manipulate PyQt6 widgets or Python application state.

---

# 45. Database Boundary

PowerShell should not normally modify the F7Hub SQLite database directly.

Preferred:

```text
PowerShell
   ↓
Structured Result
   ↓
Python
   ↓
Repository
   ↓
SQLite
```

This preserves one controlled data-access layer.

---

# 46. Why PowerShell Does Not Own SQLite

Benefits:

- one persistence architecture
- centralized transactions
- centralized migrations
- parameterized queries
- fewer schema dependencies
- easier tests
- cleaner technology boundaries

PowerShell should return data, not become a second repository implementation.

---

# 47. Exceptions

A standalone database maintenance script may exist under:

```text
Tools\Database\
```

if explicitly designed for development or recovery.

Such scripts should not become normal runtime application behavior.

---

# 48. Authentication

PowerShell may require authentication to Microsoft services.

Authentication should use supported mechanisms.

Possible examples:

- interactive OAuth
- device code where supported
- delegated permissions
- application authentication where explicitly designed

Secrets management requires separate architectural approval.

---

# 49. Authentication Principle

The default approach should favor:

```text
interactive technician authentication
+
least privilege
```

over permanent stored credentials.

---

# 50. Token Handling

Authentication tokens must not be:

- written to source
- committed to Git
- exposed in logs
- embedded in documentation
- stored as ordinary SQLite settings

---

# 51. Microsoft Graph Permissions

Graph permissions should be:

- minimal
- documented
- aligned to operation
- understandable before consent

Avoid requesting broad tenant-wide permissions simply for convenience.

---

# 52. Exchange Online Authentication

Exchange Online scripts should use currently supported Microsoft modules and authentication methods.

Legacy basic authentication must not be introduced.

---

# 53. Module Dependency Management

Scripts requiring modules should declare or document those dependencies.

Examples:

```text
Microsoft.Graph
ExchangeOnlineManagement
MicrosoftTeams
```

F7Hub should be able to identify missing dependencies before execution.

---

# 54. Module Validation

Conceptual flow:

```text
Select Script
    ↓
Check Required Modules
    │
    ├── Available
    │      ↓
    │    Continue
    │
    └── Missing
           ↓
         Report Dependency
```

Do not silently install modules during an administrative operation unless that behavior is explicitly designed.

---

# 55. Module Installation

Module installation should be a separate technician-controlled setup action.

Potential requirements:

- package source validation
- version validation
- trust awareness
- user vs administrator install scope

---

# 56. Version Compatibility

Scripts should account for:

- PowerShell version
- module version
- Windows version
- API changes

Compatibility assumptions should be documented in script metadata where relevant.

---

# 57. Microsoft API Changes

Microsoft cloud tooling changes over time.

Before implementing important integrations, verify current official documentation.

Deprecated modules and APIs should not be introduced merely because old examples exist online.

---

# 58. Windows PowerShell 5.1 Compatibility

If a specific operation requires Windows PowerShell 5.1:

```text
Script Metadata
→ runtime = powershell.exe
```

Otherwise:

```text
runtime = pwsh.exe
```

The runtime should be explicit.

---

# 59. Diagnostics Philosophy

Diagnostics should prefer:

```text
Observe
→ Measure
→ Report
```

before:

```text
Modify
```

This helps preserve technician understanding and safety.

---

# 60. Diagnostic Categories

Potential categories:

```text
Windows
Networking
Outlook
Microsoft365
ExchangeOnline
EntraID
Intune
Defender
Teams
OneDrive
Printers
Performance
```

Create folders only when scripts actually exist.

---

# 61. Diagnostic Input

A diagnostic script should consume only the information it needs.

Examples:

```text
ComputerName
UserPrincipalName
Hostname
Mailbox
DeviceId
```

Avoid passing full ticket objects into PowerShell unless required.

---

# 62. Diagnostic Output

Return structured evidence.

Example:

```json
{
  "status": "FAIL",
  "message": "DNS resolution failed.",
  "data": {
    "server": "8.8.8.8",
    "hostname": "example.com",
    "resolved": false
  }
}
```

This makes results useful for:

- ticket notes
- diagnostic branching
- reports
- AI interpretation
- history

---

# 63. Remediation Scripts

Remediation scripts should clearly state:

- target
- intended change
- expected impact
- privilege requirement
- reversibility
- risk

The technician should understand the action before execution.

---

# 64. Confirmation

PowerShell itself should not necessarily own GUI confirmation.

Preferred:

```text
Python GUI
→ display impact
→ technician confirms
→ PowerShell executes
```

This keeps the confirmation experience consistent.

---

# 65. WhatIf Support

Where practical, administrative functions may support:

```powershell
SupportsShouldProcess
```

and:

```text
-WhatIf
```

for safer review.

This is especially useful for impactful changes.

---

# 66. Idempotency

Administrative scripts should be idempotent where practical.

Meaning:

Running the same action twice should not unexpectedly create duplicate or harmful state.

Example:

```text
Ensure setting X is enabled
```

is generally better than:

```text
Blindly add X every time
```

---

# 67. Read-Only First

Where both read and write operations exist, implement and validate read-only diagnostics first.

Example:

```text
Get-MailboxPermission
```

before:

```text
Add-MailboxPermission
```

This provides learning value and reduces risk.

---

# 68. Logging

PowerShell execution metadata may be recorded by F7Hub.

Potential metadata:

- script
- execution ID
- timestamp
- duration
- result
- exit code
- related ticket
- target
- sanitized parameters

Do not log secrets.

---

# 69. Raw Output Retention

Raw command output should not automatically be stored forever.

Consider:

- size
- privacy
- usefulness
- retention
- duplication

Structured results are generally more valuable.

---

# 70. Transcript Logging

PowerShell transcription may be useful for development or selected administrative workflows.

It should not be enabled indiscriminately because transcripts may capture sensitive information.

Use deliberately.

---

# 71. Audit Logging

High-impact administrative actions may require audit records.

Potential fields:

```text
operation
target
timestamp
result
technician
ticket
```

Audit records should be written through the F7Hub application where practical.

---

# 72. Sensitive Output

PowerShell commands may return:

- email addresses
- tenant identifiers
- device identifiers
- security information
- authentication-related information

Scripts should return only what the workflow needs.

---

# 73. Secret Filtering

Before data is:

- logged
- stored
- exported
- sent to AI

sensitive values should be removed where appropriate.

---

# 74. AI Boundary

AI may:

- explain a PowerShell script
- recommend a script
- summarize output
- propose improvements

AI must not directly execute privileged PowerShell.

Preferred:

```text
AI Suggestion
    ↓
Technician Review
    ↓
Approved Registered Script
    ↓
PowerShellGateway
```

---

# 75. AI-Generated PowerShell

AI-generated PowerShell should be treated as untrusted code.

Before execution:

```text
Review
↓
Security Check
↓
Architecture Check
↓
Test
↓
Approval
```

Do not automatically save generated code into the approved script registry.

---

# 76. AutoHotkey Boundary

AHK may launch simple PowerShell utilities where justified.

However normal F7Hub PowerShell execution should flow through Python.

Preferred:

```text
AHK Hotkey
   ↓
F7Hub Command
   ↓
Python
   ↓
PowerShell
```

---

# 77. Report Generation

PowerShell may generate structured administrative reports.

Preferred intermediate format:

```text
PowerShell Objects
       ↓
Structured Data
       ↓
CSV / JSON / HTML
```

Avoid formatting too early if F7Hub needs to consume the data.

---

# 78. Output Formatting

Use:

```text
Select-Object
PSCustomObject
ConvertTo-Json
Export-Csv
```

appropriately.

Avoid relying on:

```text
Format-Table
Format-List
```

for machine-readable application output.

Formatting cmdlets are primarily presentation tools.

---

# 79. Object Pipeline

PowerShell scripts should preserve object-oriented pipeline behavior internally.

Prefer:

```powershell
Get-Process |
    Where-Object CPU -gt 100 |
    Select-Object Name, Id, CPU
```

over converting everything to formatted strings early.

---

# 80. Functions

Reusable functions should:

- have clear names
- use approved verbs where possible
- define explicit parameters
- return objects
- avoid hidden global dependencies

---

# 81. Function Naming

Use standard PowerShell naming:

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

Avoid arbitrary verbs where approved PowerShell verbs exist.

---

# 82. Scope

Avoid unnecessary global variables.

Preferred:

- local variables
- script scope where justified
- explicit parameters
- returned objects

Global state makes testing and integration harder.

---

# 83. Profiles

F7Hub scripts should not depend on the technician's PowerShell profile.

The application runtime should behave predictably regardless of personal shell customization.

Where possible, execution should use:

```text
-NoProfile
```

---

# 84. Execution Policy

F7Hub should not globally weaken PowerShell execution policy.

Development users may configure an appropriate policy such as:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

but application architecture should not silently modify machine policy.

---

# 85. Code Signing

Future production releases may consider signing PowerShell scripts.

Benefits may include:

- provenance
- integrity
- trust
- enterprise compatibility

This is a future security/deployment decision.

---

# 86. File Paths

Scripts should not hard-code:

```text
C:\Dev\F7Hub
```

for runtime behavior.

Paths should come from:

- script location
- arguments
- configuration
- installed application paths

Development paths may appear in tooling scripts only where appropriate.

---

# 87. Relative Paths

Project-controlled resources should use relative paths where practical.

For example:

```text
PowerShell\Diagnostics\Networking\Test-DnsHealth.ps1
```

The application resolves the full path.

---

# 88. Temporary Files

Avoid temporary files when structured stdout is sufficient.

If temporary files are required, use:

```text
Data\Temp\
```

or the appropriate runtime temp location.

Clean them safely.

---

# 89. External Commands

PowerShell may call external tools when necessary.

External command invocation should:

- validate executable location
- validate arguments
- capture exit code
- avoid shell injection
- handle missing executable

---

# 90. Native Command Errors

Native programs do not necessarily follow PowerShell's error semantics.

Scripts should inspect:

```powershell
$LASTEXITCODE
```

where relevant.

---

# 91. Timeouts

Long-running operations should have a defined timeout at the gateway or workflow level where appropriate.

Examples:

- network diagnostics
- Graph requests
- external commands

Timeout should result in a structured failure rather than an indefinite blocked GUI.

---

# 92. Cancellation

Some PowerShell operations may support cancellation.

The Python execution layer should distinguish:

- safe to terminate
- unsafe to interrupt
- already committed remote operation

Never tell the user an administrative operation was cancelled if the service already completed it.

---

# 93. Background Execution

PowerShell processes should not block the PyQt6 event loop.

Conceptually:

```text
GUI
 ↓
Background Worker
 ↓
PowerShell Process
 ↓
Result
 ↓
GUI
```

Exact threading/async design belongs in `13_PythonArchitecture.md`.

---

# 94. Process Isolation

Running PowerShell as a separate process provides a useful boundary.

Benefits:

- crash isolation
- output capture
- timeout control
- runtime selection
- cleaner environment

---

# 95. Persistent PowerShell Session

A persistent PowerShell runspace/session may eventually improve performance for repeated Microsoft operations.

However, it introduces complexity:

- connection lifecycle
- authentication state
- module state
- stale sessions
- cleanup
- thread safety

Do not introduce persistent sessions until measured need exists.

---

# 96. Initial Execution Model

Initial architecture should prefer:

```text
one controlled process execution
per script/action
```

because it is simpler to understand and test.

Optimize later if necessary.

---

# 97. Connection Reuse

Microsoft cloud connections may eventually justify controlled session reuse.

If introduced, connection ownership must be explicit.

Possible service:

```text
Microsoft365ConnectionService
```

rather than random scripts maintaining independent global sessions.

---

# 98. Tests

PowerShell testing should include appropriate:

- syntax validation
- unit tests
- parameter validation
- structured result tests
- failure-path tests
- integration tests
- manual live-service validation

Pester may be used where appropriate.

---

# 99. Pester

Pester is the preferred PowerShell testing framework when automated PowerShell tests are justified.

Potential tests:

```text
script returns valid JSON
required parameters are enforced
invalid input fails safely
helper returns expected status
```

---

# 100. Live Cloud Tests

Live Microsoft 365 tests should be:

- explicit
- controlled
- non-destructive by default
- performed against safe targets where possible

Do not run destructive tests against production tenants automatically.

---

# 101. Test Status

Use:

```text
PASS
FAIL
NOT RUN
BLOCKED
```

Never claim Microsoft Graph, Exchange, Intune, or other administrative integration works unless it was actually validated.

---

# 102. Initial PowerShell Scope

Recommended first-stage PowerShell capabilities:

```text
1. Execution contract
2. Structured JSON result helper
3. Environment validation
4. Basic Windows diagnostics
5. Basic networking diagnostics
6. Script registry integration
7. Execution history
8. Tests
```

This validates the architecture before cloud complexity is added.

---

# 103. Second Stage

After the local execution layer is reliable:

```text
Microsoft Graph read-only queries
Exchange Online read-only diagnostics
Entra ID queries
M365 tenant/user information
```

Start with read-only operations.

---

# 104. Third Stage

Later:

```text
Intune
Defender
Teams
SharePoint
controlled remediation actions
administrative workflows
```

Each should be added through focused vertical slices.

---

# 105. Example DNS Diagnostic

Conceptual script:

```powershell
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$Hostname
)

$ErrorActionPreference = 'Stop'

try {
    $result = Resolve-DnsName -Name $Hostname -ErrorAction Stop

    [pscustomobject]@{
        schemaVersion = 1
        operation     = 'Test-DnsHealth'
        success       = $true
        status        = 'PASS'
        message       = 'DNS resolution succeeded.'
        data          = @{
            hostname = $Hostname
            addresses = @($result.IPAddress)
        }
        warnings      = @()
        errors        = @()
    } | ConvertTo-Json -Depth 10
}
catch {
    [pscustomobject]@{
        schemaVersion = 1
        operation     = 'Test-DnsHealth'
        success       = $false
        status        = 'FAIL'
        message       = 'DNS resolution failed.'
        data          = @{
            hostname = $Hostname
        }
        warnings      = @()
        errors        = @($_.Exception.Message)
    } | ConvertTo-Json -Depth 10

    exit 1
}
```

This is an architectural example, not a verified production script.

---

# 106. Example Script Metadata

Conceptually, F7Hub may register the script as:

```text
Name:
Test DNS Health

Path:
PowerShell\Diagnostics\Networking\Test-DnsHealth.ps1

Type:
DIAGNOSTIC

Runtime:
PowerShell 7

Privilege:
STANDARD_USER

Risk:
LOW

Parameter:
Hostname
```

---

# 107. Example Microsoft 365 Flow

```text
Open Ticket
    ↓
Run User License Diagnostic
    ↓
Python validates UPN
    ↓
PowerShell Graph script
    ↓
Authenticate if required
    ↓
Query Graph
    ↓
Return structured result
    ↓
Display user licenses
    ↓
Attach result to diagnostic session
```

---

# 108. Example Remediation Flow

```text
Diagnostic identifies issue
        ↓
Suggested remediation appears
        ↓
Technician reviews
        ↓
Target and impact displayed
        ↓
Technician confirms
        ↓
PowerShell remediation script
        ↓
Structured result
        ↓
Verification diagnostic
        ↓
Ticket timeline
```

Verification should follow remediation where practical.

---

# 109. Anti-Patterns

Avoid:

## Giant PowerShell Script

One script performs every M365 and Windows operation.

## Raw Shell Strings from GUI

PyQt6 buttons construct arbitrary commands.

## PowerShell-Owned Database

Scripts directly update core SQLite records.

## Hidden Authentication

Scripts silently connect with stored privileged credentials.

## Invoke-Expression Automation

Untrusted strings become executable commands.

## Human-Formatted Output Parsing

Python tries to parse decorative `Format-Table` output.

## Silent Elevation

Scripts relaunch as admin without explicit technician intent.

## Auto-Install Everything

A script changes execution policy and installs modules during routine execution.

## AI-to-PowerShell Direct Execution

AI output bypasses technician review.

---

# 110. Design Decision Rule

Before implementing something in PowerShell, ask:

1. Is this a Windows or Microsoft administration task?
2. Is this a diagnostic or reporting task?
3. Would Python provide a cleaner application-level implementation?
4. Is an official API better?
5. Does an existing PowerShell script already solve it?
6. Can the operation be read-only first?
7. What privileges are required?
8. What result should Python receive?
9. How will failure be reported?
10. How will it be tested?

---

# 111. Cross-Technology Architecture

```text
                      PyQt6 GUI
                         │
                         ▼
                  Python Services
                         │
             ┌───────────┼───────────┐
             │                       │
             ▼                       ▼
       Repositories            PowerShellService
             │                       │
             ▼                       ▼
           SQLite               PowerShellGateway
                                     │
                                     ▼
                                PowerShell 7
                                     │
                   ┌─────────────────┼─────────────────┐
                   ▼                 ▼                 ▼
                Windows         Microsoft 365       Diagnostics
```

AutoHotkey remains separate for desktop automation.

---

# 112. Documentation Synchronization

PowerShell architectural changes must update:

```text
12_PowerShellArchitecture.md
```

If changes affect system boundaries, also review:

```text
06_SystemArchitecture.md
10_FolderStructure.md
13_PythonArchitecture.md
```

Database changes require:

```text
07_Database.md
08_ERD.md
09_SQLSchema.md
```

Major verified changes should update:

```text
18_ChangeLog.md
```

---

# 113. Current Implementation Status

Repository inspection on 2026-09-02 found no PowerShell implementation under `PowerShell\`.

```text
PowerShell implementation status: PLANNED
```

This document does not prove that:

- scripts exist
- Graph connectivity exists
- Exchange connectivity exists
- structured results are implemented
- tests pass

---

# 114. Initial Implementation Sequence

Recommended implementation order:

```text
1. PowerShell folder foundation
        ↓
2. Structured result contract
        ↓
3. Shared result/error helpers
        ↓
4. Python PowerShellGateway
        ↓
5. Simple read-only Windows diagnostic
        ↓
6. Networking diagnostic
        ↓
7. Script registry metadata
        ↓
8. Execution history
        ↓
9. Pester / integration tests
        ↓
10. Microsoft Graph read-only integration
```

This proves the execution architecture before adding broad cloud administration.

---

# 115. Completion Checklist

A PowerShell feature is complete when applicable:

```text
[ ] Requirement identified
[ ] Existing script searched
[ ] Correct subsystem selected
[ ] PowerShell 7 compatibility checked
[ ] Parameters explicit
[ ] Input validated
[ ] Privilege requirement documented
[ ] Risk classified
[ ] Structured result returned
[ ] Errors handled
[ ] Secrets protected
[ ] No unsafe command construction
[ ] Python integration tested
[ ] Failure path tested
[ ] Documentation synchronized
```

---

# 116. PowerShell Golden Rules

1. PowerShell 7 is the preferred runtime.
2. Python/PyQt6 controls application workflows.
3. PowerShell owns Windows and Microsoft administration.
4. Scripts should be narrow and reusable.
5. Separate diagnostics from remediation.
6. Prefer read-only operations first.
7. Use explicit parameters.
8. Validate all external input.
9. Avoid `Invoke-Expression`.
10. Return structured machine-readable results.
11. Preserve PowerShell objects internally.
12. Do not parse formatted console tables.
13. Do not directly own the core SQLite database.
14. Never hard-code credentials or tokens.
15. Follow least privilege.
16. Do not silently elevate.
17. Do not silently install modules or weaken execution policy.
18. Treat AI-generated code as untrusted.
19. Test success and failure paths.
20. Add Microsoft integrations incrementally.

---

# 117. Final Architecture Summary

PowerShell is F7Hub's administrative execution engine.

Its role is:

```text
Windows
Microsoft 365
Microsoft Graph
Exchange
Entra
Intune
Defender
Networking
Diagnostics
Reporting
      │
      ▼
 PowerShell 7
      │
      ▼
Structured Results
      │
      ▼
Python / PyQt6
```

The responsibility boundary is:

```text
Python
→ decides what workflow is being performed

PowerShell
→ performs approved administrative or diagnostic operation

SQLite
→ stores persistent application state through Python repositories

AutoHotkey v2
→ handles desktop productivity automation
```

The guiding principle is:

> PowerShell should expose small, safe, testable administrative capabilities that F7Hub can compose into technician workflows.

F7Hub should make PowerShell easier to discover, safer to execute, and easier to understand without hiding what the script actually does.
