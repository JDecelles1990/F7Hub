<#
.SYNOPSIS
    Creates the approved F7Hub folder scaffold.

.DESCRIPTION
    Creates the canonical F7Hub development directory structure.

    The script is:
    - idempotent
    - non-destructive
    - safe to rerun
    - configurable through -RootPath
    - designed to preserve existing files and folders

    It creates missing directories only.
    It does not delete, rename, move, or overwrite project files.

.PARAMETER RootPath
    Root directory of the F7Hub project.

    Default:
    C:\Dev\F7Hub

.EXAMPLE
    .\Initialize-F7HubStructure.ps1

.EXAMPLE
    .\Initialize-F7HubStructure.ps1 -RootPath "D:\Projects\F7Hub"

.NOTES
    Project: F7Hub
    Canonical structure source:
    Docs\10_FolderStructure.md
#>

[CmdletBinding()]
param(
    [Parameter()]
    [ValidateNotNullOrEmpty()]
    [string]$RootPath = 'C:\Dev\F7Hub'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Status {
    param(
        [Parameter(Mandatory)]
        [ValidateSet('CREATED', 'EXISTS', 'INFO', 'ERROR')]
        [string]$Status,

        [Parameter(Mandatory)]
        [string]$Message
    )

    Write-Host ('[{0,-7}] {1}' -f $Status, $Message)
}

function Ensure-Directory {
    param(
        [Parameter(Mandatory)]
        [string]$Path
    )

    if (Test-Path -LiteralPath $Path -PathType Container) {
        Write-Status -Status 'EXISTS' -Message $Path
        return
    }

    if (Test-Path -LiteralPath $Path) {
        throw "A non-directory item already exists at: $Path"
    }

    New-Item -ItemType Directory -Path $Path -Force | Out-Null
    Write-Status -Status 'CREATED' -Message $Path
}

try {
    $resolvedRoot = [System.IO.Path]::GetFullPath($RootPath)

    Write-Host ''
    Write-Host 'F7Hub Folder Structure Initializer'
    Write-Host '================================='
    Write-Host "Root: $resolvedRoot"
    Write-Host ''

    Ensure-Directory -Path $resolvedRoot

    $relativeDirectories = @(
        # Python application
        'Python'
        'Python\f7hub'
        'Python\f7hub\app'
        'Python\f7hub\gui'
        'Python\f7hub\services'
        'Python\f7hub\domain'
        'Python\f7hub\repositories'
        'Python\f7hub\infrastructure'
        'Python\f7hub\utils'

        # AutoHotkey
        'AutoHotkey'
        'AutoHotkey\Core'
        'AutoHotkey\Hotkeys'
        'AutoHotkey\Hotstrings'
        'AutoHotkey\Clipboard'
        'AutoHotkey\Menus'
        'AutoHotkey\Launchers'
        'AutoHotkey\Lib'

        # PowerShell
        'PowerShell'
        'PowerShell\Core'
        'PowerShell\Modules'
        'PowerShell\Diagnostics'
        'PowerShell\Reports'
        'PowerShell\Functions'
        'PowerShell\Templates'

        # Database
        'Database'
        'Database\Migrations'
        'Database\Seeds'
        'Database\Queries'
        'Database\ERD'
        'Database\Dev'

        # Configuration
        'Config'
        'Config\Defaults'
        'Config\Templates'

        # Runtime / data
        'Data'
        'Data\Attachments'
        'Data\Imports'
        'Data\Exports'
        'Data\Cache'
        'Data\Temp'
        'Data\Samples'

        # Documentation
        'Docs'
        'Docs\Assets'
        'Docs\Assets\Diagrams'
        'Docs\Assets\Mockups'
        'Docs\Assets\Screenshots'
        'Docs\Research'
        'Docs\Archive'
        'Docs\Archive\PreviousVersions'

        # Plugins
        'Plugins'

        # Tests
        'Tests'
        'Tests\Unit'
        'Tests\Integration'
        'Tests\Database'
        'Tests\GUI'
        'Tests\PowerShell'
        'Tests\Fixtures'

        # Application assets
        'Assets'
        'Assets\Icons'
        'Assets\Images'
        'Assets\Templates'

        # Logs
        'Logs'
        'Logs\Application'
        'Logs\PowerShell'
        'Logs\Database'
        'Logs\Debug'

        # Tools
        'Tools'
        'Tools\Scripts'
        'Tools\Database'
        'Tools\Development'

        # Build / packaging
        'Build'
        'Installer'
        'Releases'
    )

    foreach ($relativeDirectory in $relativeDirectories) {
        $fullPath = Join-Path -Path $resolvedRoot -ChildPath $relativeDirectory
        Ensure-Directory -Path $fullPath
    }

    Write-Host ''
    Write-Status -Status 'INFO' -Message 'Folder scaffold completed successfully.'
    Write-Status -Status 'INFO' -Message 'Existing files and directories were preserved.'
    Write-Status -Status 'INFO' -Message 'No speculative plugin or technology-specific folders were created.'
    Write-Host ''
}
catch {
    Write-Host ''
    Write-Status -Status 'ERROR' -Message $_.Exception.Message
    Write-Host ''
    exit 1
}

exit 0