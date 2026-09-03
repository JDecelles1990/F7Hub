# ============================================================
# Create-F7HubStructure.ps1
# Creates F7Hub project folder structure + documentation files
#
# Compatible:
#   Windows PowerShell 5.1
#   PowerShell 7+
#
# ============================================================

$Root = "C:\Users\Jo\OneDrive\Desktop\LAB\F7Hub"


# -----------------------------
# Folder Structure
# -----------------------------

$Folders = @(
    
    # AutoHotkey
    "AutoHotkey\Core",
    "AutoHotkey\GUI",
    "AutoHotkey\Modules\Dashboard",
    "AutoHotkey\Modules\Tickets",
    "AutoHotkey\Modules\Clipboard",
    "AutoHotkey\Modules\KnowledgeBase",
    "AutoHotkey\Modules\Prompts",
    "AutoHotkey\Modules\Websites",
    "AutoHotkey\Modules\Applications",
    "AutoHotkey\Modules\Search",
    "AutoHotkey\Modules\Settings",
    "AutoHotkey\Modules\AI",
    "AutoHotkey\Modules\Plugins",
    "AutoHotkey\Classes",
    "AutoHotkey\Functions",
    "AutoHotkey\Helpers",
    "AutoHotkey\Includes",
    "AutoHotkey\Lib",
    "AutoHotkey\Resources",
    "AutoHotkey\Themes",
    "AutoHotkey\Templates",
    "AutoHotkey\Hotkeys",
    "AutoHotkey\Icons",

    # PowerShell
    "PowerShell\Core",
    "PowerShell\Modules\Microsoft365",
    "PowerShell\Modules\Azure",
    "PowerShell\Modules\EntraID",
    "PowerShell\Modules\ExchangeOnline",
    "PowerShell\Modules\SharePoint",
    "PowerShell\Modules\Teams",
    "PowerShell\Modules\Intune",
    "PowerShell\Modules\ActiveDirectory",
    "PowerShell\Modules\Windows",
    "PowerShell\Modules\SQLite",
    "PowerShell\Modules\Utilities",
    "PowerShell\Functions",
    "PowerShell\Templates",
    "PowerShell\Reports",
    "PowerShell\Logs",

    # Python
    "Python\Core",
    "Python\AI",
    "Python\Search",
    "Python\OCR",
    "Python\Automation",
    "Python\API",
    "Python\GUI",
    "Python\Reports",
    "Python\Utilities",
    "Python\Tests",

    # Database
    "Database\SQLite\Backups",
    "Database\SQLite\Migrations",
    "Database\SQLite\Seeds",
    "Database\SQLite\Temp",
    "Database\Schema\Tables",
    "Database\Schema\Views",
    "Database\Schema\Indexes",
    "Database\Schema\Triggers",
    "Database\Schema\Queries",
    "Database\Schema\Procedures",
    "Database\ERD",

    # Config
    "Config\INI",
    "Config\JSON",
    "Config\YAML",
    "Config\XML",
    "Config\Defaults",
    "Config\Templates",

    # Data
    "Data\Clipboard",
    "Data\Cache",
    "Data\Imports",
    "Data\Exports",
    "Data\Attachments",
    "Data\Output",
    "Data\Samples",
    "Data\Temp",

    # Assets
    "Assets\Icons",
    "Assets\Images",
    "Assets\Logos",
    "Assets\Mockups",
    "Assets\Fonts",
    "Assets\Sounds",
    "Assets\Themes",
    "Assets\Screenshots",

    # Documentation
    "Docs\Assets\Diagrams",
    "Docs\Assets\Mockups",
    "Docs\Assets\Icons",
    "Docs\Assets\Screenshots",

    "Docs\Research\AutoHotkey",
    "Docs\Research\SQLite",
    "Docs\Research\Python",
    "Docs\Research\PowerShell",
    "Docs\Research\Microsoft365",
    "Docs\Research\GUI",
    "Docs\Research\AI",
    "Docs\Research\HaloPSA",
    "Docs\Research\Copilot",
    "Docs\Research\UX",
    "Docs\Research\Ideas",

    "Docs\Archive",

    # Plugins
    "Plugins\HaloPSA",
    "Plugins\NinjaOne",
    "Plugins\CIPP",
    "Plugins\Microsoft365",
    "Plugins\Custom",

    # Logs
    "Logs\Application",
    "Logs\AutoHotkey",
    "Logs\PowerShell",
    "Logs\Python",
    "Logs\SQLite",
    "Logs\Debug",
    "Logs\Installer",

    # Tests
    "Tests\Unit",
    "Tests\Integration",
    "Tests\Performance",
    "Tests\GUI",
    "Tests\Database",

    # Releases
    "Releases\Alpha",
    "Releases\Beta",
    "Releases\Stable",
    "Releases\Archive",

    # Build
    "Build",

    # Installer
    "Installer",

    # Tools
    "Tools\DBBrowser",
    "Tools\Mermaid",
    "Tools\SQLiteStudio",
    "Tools\Scripts",
    "Tools\Utilities"
)


Write-Host "Creating folders..." -ForegroundColor Cyan

foreach ($Folder in $Folders) {

    $Path = Join-Path $Root $Folder

    if (!(Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path | Out-Null
        Write-Host "Created: $Folder"
    }
}


# -----------------------------
# Create Root Files
# -----------------------------

$Files = @(
    ".gitignore",
    ".editorconfig",
    "README.md",
    "LICENSE",
    "CHANGELOG.md",
    "Project.json",
    "F7Hub.code-workspace",

    "Database\SQLite\F7Hub.db"
)


foreach ($File in $Files) {

    $FilePath = Join-Path $Root $File

    if (!(Test-Path $FilePath)) {

        New-Item -ItemType File -Path $FilePath | Out-Null
        Write-Host "Created file: $File"

    }
}


# -----------------------------
# Documentation Markdown Files
# -----------------------------

$Docs = @(
"00_ProjectVision.md",
"01_Project.md",
"02_ProductRequirements.md",
"03_Features.md",
"04_UserWorkflows.md",
"05_GUI.md",
"06_SystemArchitecture.md",
"07_Database.md",
"08_ERD.md",
"09_SQLSchema.md",
"10_FolderStructure.md",
"11_AHKArchitecture.md",
"12_PowerShellArchitecture.md",
"13_PythonArchitecture.md",
"14_DesignPrinciples.md",
"15_NamingConventions.md",
"16_Roadmap.md",
"17_Todo.md",
"18_ChangeLog.md"
)


$DocsPath = Join-Path $Root "Docs"


foreach ($Doc in $Docs) {

    $FilePath = Join-Path $DocsPath $Doc

    if (!(Test-Path $FilePath)) {

        @"
# $($Doc.Replace(".md",""))

## Purpose

Documentation for F7Hub project.

## Notes

Add project information here.

"@ | Set-Content $FilePath -Encoding UTF8

        Write-Host "Created documentation: $Doc"
    }
}


Write-Host ""
Write-Host "====================================="
Write-Host "F7Hub structure created successfully!"
Write-Host "Location:"
Write-Host $Root
Write-Host "=====================================" -ForegroundColor Green