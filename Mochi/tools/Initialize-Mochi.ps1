# ============================================================
# Mochi Luna Light - Initial Project Bootstrap
# Location: C:\Dev\F7Hub\Mochi
# Safe: Existing files are NOT overwritten
# ============================================================

$MochiRoot = "C:\Dev\F7Hub\Mochi"

Write-Host "Initializing Mochi Luna Light..." -ForegroundColor Cyan

# ------------------------------------------------------------
# 1. Create folder structure
# ------------------------------------------------------------

$Folders = @(
    $MochiRoot
    "$MochiRoot\src"
    "$MochiRoot\src\core"
    "$MochiRoot\src\ui"
    "$MochiRoot\src\services"
    "$MochiRoot\src\integrations"
    "$MochiRoot\assets"
    "$MochiRoot\assets\animations"
    "$MochiRoot\config"
    "$MochiRoot\tools"
    "$MochiRoot\tools\guide_generator"
    "$MochiRoot\tests"
    "$MochiRoot\docs"
)

foreach ($Folder in $Folders) {

    if (-not (Test-Path $Folder)) {
        New-Item -ItemType Directory -Path $Folder | Out-Null
        Write-Host "[CREATED] $Folder" -ForegroundColor Green
    }
    else {
        Write-Host "[EXISTS]  $Folder" -ForegroundColor DarkGray
    }
}

# ------------------------------------------------------------
# 2. Define initial files
# ------------------------------------------------------------

$Files = @(
    "$MochiRoot\README.md"
    "$MochiRoot\.gitignore"

    "$MochiRoot\config\settings.json"
    "$MochiRoot\config\guide.json"

    "$MochiRoot\src\__init__.py"
    "$MochiRoot\src\main.py"

    "$MochiRoot\src\core\__init__.py"
    "$MochiRoot\src\ui\__init__.py"
    "$MochiRoot\src\services\__init__.py"
    "$MochiRoot\src\integrations\__init__.py"

    "$MochiRoot\tools\guide_generator\README.md"

    "$MochiRoot\tests\__init__.py"

    "$MochiRoot\docs\Mochi_Luna_Light_MVP_Specification.md"
    "$MochiRoot\docs\Architecture.md"
    "$MochiRoot\docs\Roadmap.md"
)

# ------------------------------------------------------------
# 3. Create files safely
# ------------------------------------------------------------

foreach ($File in $Files) {

    if (-not (Test-Path $File)) {
        New-Item -ItemType File -Path $File | Out-Null
        Write-Host "[CREATED] $File" -ForegroundColor Green
    }
    else {
        Write-Host "[EXISTS]  $File" -ForegroundColor DarkGray
    }
}

# ------------------------------------------------------------
# 4. Add starter settings.json
# ------------------------------------------------------------

$SettingsFile = "$MochiRoot\config\settings.json"

if ((Get-Item $SettingsFile).Length -eq 0) {

@'
{
    "app": {
        "name": "Mochi Luna Light",
        "enabled": true
    },
    "pet": {
        "always_on_top": true,
        "click_through": false,
        "opacity": 1.0
    },
    "privacy": {
        "clipboard_access": false,
        "screen_capture": false,
        "ocr": false
    },
    "f7hub": {
        "integration_enabled": false,
        "read_only": true
    }
}
'@ | Set-Content -Path $SettingsFile -Encoding UTF8
}

# ------------------------------------------------------------
# 5. Add starter main.py
# ------------------------------------------------------------

$MainFile = "$MochiRoot\src\main.py"

if ((Get-Item $MainFile).Length -eq 0) {

@'
"""Mochi Luna Light entry point."""


def main():
    print("Mochi Luna Light starting...")


if __name__ == "__main__":
    main()
'@ | Set-Content -Path $MainFile -Encoding UTF8
}

# ------------------------------------------------------------
# 6. Add README
# ------------------------------------------------------------

$ReadmeFile = "$MochiRoot\README.md"

if ((Get-Item $ReadmeFile).Length -eq 0) {

@'
# Mochi Luna Light

Mochi Luna Light is the desktop AI-pet subsystem of F7Hub.

## Initial responsibilities

- Desktop pet UI and animations
- Context-aware technician assistance
- Controlled F7Hub interaction
- Read-only contextual integration by default
- AHK / Windows Spy assisted GUI awareness
- Filtered clipboard/context processing
- Privacy-first AI features

## Architecture

Mochi is developed as an isolated sub-application inside the F7Hub
modular monolith.

Sensitive capabilities such as screenshots, OCR, clipboard monitoring,
and AI context collection must remain explicit and configurable.
'@ | Set-Content -Path $ReadmeFile -Encoding UTF8
}

# ------------------------------------------------------------
# 7. Add .gitignore
# ------------------------------------------------------------

$GitIgnore = "$MochiRoot\.gitignore"

if ((Get-Item $GitIgnore).Length -eq 0) {

@'
__pycache__/
*.pyc
.venv/
venv/
.env
logs/
temp/
*.log
'@ | Set-Content -Path $GitIgnore -Encoding UTF8
}

# ------------------------------------------------------------
# 8. Display resulting structure
# ------------------------------------------------------------

Write-Host ""
Write-Host "Mochi initialization complete." -ForegroundColor Cyan
Write-Host "Root: $MochiRoot" -ForegroundColor Yellow
Write-Host ""

Get-ChildItem $MochiRoot -Recurse |
    Select-Object FullName