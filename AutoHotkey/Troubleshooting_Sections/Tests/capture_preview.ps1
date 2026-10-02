param([string]$Scenario = '85-small')
$ErrorActionPreference = 'Stop'
$evidencePath = Join-Path $PSScriptRoot 'Evidence'
New-Item -ItemType Directory -Path $evidencePath -Force | Out-Null
$request = "$Scenario|$([Guid]::NewGuid().ToString())"
[IO.File]::WriteAllText((Join-Path $evidencePath 'preview-command.txt'), $request)
$statePath = Join-Path $evidencePath 'preview-state.txt'
$deadline = [DateTime]::UtcNow.AddSeconds(12)
do {
    Start-Sleep -Milliseconds 200
    if (Test-Path -LiteralPath $statePath) {
        $state = @{}
        Get-Content -LiteralPath $statePath | ForEach-Object {
            if ($_ -match '^([^=]+)=(.*)$') { $state[$Matches[1]] = $Matches[2] }
        }
        if ($state.command -eq $Scenario -and $state.request -eq $request) { break }
    }
} while ([DateTime]::UtcNow -lt $deadline)
if (!$state -or $state.command -ne $Scenario -or $state.request -ne $request) { throw "Preview did not become ready: $Scenario" }
Copy-Item -LiteralPath $statePath -Destination (Join-Path $evidencePath "$Scenario.state.txt")
Start-Sleep -Milliseconds 500
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
$screenBounds = [Windows.Forms.Screen]::PrimaryScreen.Bounds
$left = [Math]::Max(0, [int]$state.x)
$top = [Math]::Max(0, [int]$state.y)
$captureWidth = [Math]::Min([int]$state.width, $screenBounds.Right - $left)
$captureHeight = [Math]::Min([int]$state.height, $screenBounds.Bottom - $top)
if ($Scenario -in @('editor', 'picker')) {
    $left = 0; $top = 0
    $captureWidth = $screenBounds.Width; $captureHeight = $screenBounds.Height
}
$bitmap = [Drawing.Bitmap]::new($captureWidth, $captureHeight)
$graphics = [Drawing.Graphics]::FromImage($bitmap)
try {
    $graphics.CopyFromScreen($left, $top, 0, 0, $bitmap.Size)
    $outputPath = Join-Path $evidencePath "$Scenario.png"
    $bitmap.Save($outputPath, [Drawing.Imaging.ImageFormat]::Png)
    Write-Output $outputPath
    Write-Output "DPI=$($state.dpi) FONT=$($state.font) OPACITY=$($state.opacity) SCREEN=$($state.screen)"
} finally {
    $graphics.Dispose()
    $bitmap.Dispose()
}
