param(
    [Parameter(Mandatory)][string]$EvidenceRoot,
    [ValidateSet('Policy', 'Harness', 'Native', 'Office', 'F7', 'AltF7', 'AltF7Toggle', 'Follower')][string]$Suite = 'Policy',
    [switch]$NativeInteractive,
    [ValidateRange(1, 32)][int]$Monitor = 1,
    [string]$AhkPath = 'C:/Program Files/AutoHotkey/v2/AutoHotkey64.exe',
    [string]$PythonPath = 'C:/Dev/F7Hub/.venv/Scripts/pythonw.exe',
    [string]$RuntimeRoot,
    [ValidateRange(10, 180)][int]$TimeoutSeconds = 60
)
$ErrorActionPreference = 'Stop'
$interactive = $Suite -in @('Native', 'Office', 'F7', 'AltF7', 'AltF7Toggle', 'Follower')
if ($interactive) {
    if (!$NativeInteractive) { throw 'Interactive desktop suites are opt-in: use -NativeInteractive, then confirm the test window. No test was launched.' }
    $confirmation = Read-Host "One $Suite attempt will use foreground focus and synthetic input on monitor $Monitor. Close other automation and leave this desktop idle for at most $TimeoutSeconds seconds. Type RUN ONE ATTEMPT to confirm this test window"
    if ($confirmation -cne 'RUN ONE ATTEMPT') { throw 'Interactive attempt not confirmed. No test was launched.' }
} elseif ($NativeInteractive) { throw '-NativeInteractive applies only to interactive suites' }
$sourceRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$evidenceParent = [IO.Path]::GetFullPath($EvidenceRoot).TrimEnd([IO.Path]::DirectorySeparatorChar)
if ($evidenceParent -eq $sourceRoot -or $evidenceParent.StartsWith($sourceRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
    throw 'Evidence must be outside the candidate'
}
$stamp = [DateTimeOffset]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')
$evidence = Join-Path $evidenceParent "$Suite-$stamp-$([Guid]::NewGuid().ToString('N'))"
New-Item -ItemType Directory -Path $evidence | Out-Null
$log = Join-Path $evidence "$Suite-$stamp.log"
$errLog = Join-Path $evidence "$Suite-$stamp.err"
$resultPath = Join-Path $evidence "$Suite-$stamp.result.json"
$started = [DateTimeOffset]::UtcNow
$root = if ($RuntimeRoot) { [IO.Path]::GetFullPath($RuntimeRoot) } else { $sourceRoot }
if ($Suite -in @('Policy', 'Harness', 'Native', 'Office') -and $root -ne $sourceRoot) {
    throw 'Focused CP-01 suites must execute the candidate whose input hashes are recorded'
}
if ($Suite -in @('F7', 'AltF7', 'AltF7Toggle') -and (!$RuntimeRoot -or $root -eq $sourceRoot -or $root -eq 'C:\Dev\F7Hub')) {
    throw 'F7/AltF7 require an external isolated runtime copy'
}
$arguments = @('/ErrorStdOut=utf-8')
switch ($Suite) {
    Policy { $arguments += "`"$root/Tests/AutoHotkey/test_clipboard_hotkey_policy.ahk`"" }
    Harness { $arguments += "`"$root/Tests/AutoHotkey/test_cp01_harness_support.ahk`"", "`"$evidence`"" }
    Office { $arguments += "`"$root/Tests/AutoHotkey/test_clipboard_office_acceptance.ahk`"" }
    Native {
        $targets = Join-Path $evidence 'targets'
        New-Item -ItemType Directory -Path $targets -Force | Out-Null
        foreach ($name in @('allowed.exe','WINWORD.EXE','EXCEL.EXE','OUTLOOK.EXE','OLK.EXE','POWERPNT.EXE',
            'WinWord.Exe','WINWORD2.EXE','MYOUTLOOK.EXE','OUTLOOK.EXE.BAK','OLKHELPER.EXE','POWERPNT2.EXE')) {
            $folder = Join-Path $targets $name
            # Case-insensitive Windows paths need a separate folder for mixed case.
            if ($name -ceq 'WinWord.Exe') { $folder = Join-Path $targets 'mixed-case' }
            New-Item -ItemType Directory -Path $folder -Force | Out-Null
            Copy-Item -LiteralPath $AhkPath -Destination (Join-Path $folder $name)
        }
        $arguments += "`"$root/Tests/AutoHotkey/test_clipboard_press_cycle_native.ahk`"", "`"$evidence`"", 'native-interactive-confirmed', "$Monitor"
    }
    F7 { $arguments += "`"$root/Tests/AutoHotkey/test_f7hub_launcher.ahk`"", "`"$evidence/f7-fixture.sqlite`"", "`"$PythonPath`"" }
    AltF7 { $arguments += "`"$root/Tests/AutoHotkey/test_altf7hub_host.ahk`"" }
    AltF7Toggle { $arguments += "`"$sourceRoot/Tests/AutoHotkey/test_altf7hub_toggle.ahk`"", "`"$root`"" }
    Follower { $arguments += "`"$root/Tests/AutoHotkey/test_magnetic_window_follower.ahk`"" }
}
$owned = [Collections.Generic.HashSet[int]]::new()
$identities = @{}
$timedOut = $false
$process = $null
$completion = 'INCOMPLETE'
$exitCode = $null
$inputHashes = [ordered]@{}
$inputFiles = @('AutoHotkey/Helpers/ClipboardHotkeyPolicy.ahk', 'AutoHotkey/Hotkeys/ClipboardPressCycleController.ahk',
    'Tests/AutoHotkey/run_clipboard_cp01_tests.ps1')
if ($Suite -eq 'Policy') { $inputFiles += 'Tests/AutoHotkey/test_clipboard_hotkey_policy.ahk' }
if ($Suite -eq 'Native') { $inputFiles += 'Tests/AutoHotkey/test_clipboard_press_cycle_native.ahk', 'Tests/AutoHotkey/fixtures/clipboard_policy_target.ahk' }
if ($Suite -eq 'Harness') { $inputFiles += 'Tests/AutoHotkey/test_cp01_harness_support.ahk', 'Tests/AutoHotkey/fixtures/clipboard_policy_target.ahk' }
if ($Suite -in @('Native', 'Harness')) { $inputFiles += 'Tests/AutoHotkey/fixtures/cp01_harness_support.ahk' }
if ($Suite -eq 'Office') { $inputFiles += 'Tests/AutoHotkey/test_clipboard_office_acceptance.ahk' }
if ($Suite -eq 'AltF7Toggle') { $inputFiles += 'Tests/AutoHotkey/test_altf7hub_toggle.ahk' }
foreach ($relative in $inputFiles) {
    $inputHashes[$relative] = (Get-FileHash -LiteralPath (Join-Path $sourceRoot $relative) -Algorithm SHA256).Hash.ToLowerInvariant()
}
$inputHashes['runtime/AutoHotkey64.exe'] = (Get-FileHash -LiteralPath $AhkPath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($Suite -in @('F7','AltF7','AltF7Toggle','Follower')) {
    $runtimeFiles = & git -C $sourceRoot ls-files AutoHotkey Python Database Config Mochi Tests/AutoHotkey
    foreach ($relative in $runtimeFiles) {
        if ($relative -eq 'AutoHotkey/Troubleshooting_Sections/GuideSettings.ini') { continue }
        $sourceHash = (Get-FileHash -LiteralPath (Join-Path $sourceRoot $relative) -Algorithm SHA256).Hash.ToLowerInvariant()
        $runtimeHash = (Get-FileHash -LiteralPath (Join-Path $root $relative) -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($sourceHash -ne $runtimeHash) { throw "Runtime copy differs: $relative" }
        $inputHashes[$relative] = $sourceHash
    }
}
try {
    $process = Start-Process -FilePath $AhkPath -ArgumentList $arguments -WorkingDirectory $root -WindowStyle Hidden -PassThru -RedirectStandardOutput $log -RedirectStandardError $errLog
    [void]$owned.Add($process.Id)
    $identities[$process.Id] = $process.StartTime
    $deadline = [DateTimeOffset]::UtcNow.AddSeconds($TimeoutSeconds)
    do {
        $inventory = @(Get-CimInstance Win32_Process | Select-Object ProcessId, ParentProcessId, CreationDate, ExecutablePath)
        $currentIdentities = @{}
        foreach ($entry in $inventory) { $currentIdentities[[int]$entry.ProcessId] = $entry.CreationDate }
        # Track descendants by parent and creation time; never stop unrelated apps.
        do {
            $added = $false
            foreach ($entry in $inventory) {
                $parentId = [int]$entry.ParentProcessId
                if ($owned.Contains($parentId) -and $identities.ContainsKey($parentId) -and
                    $currentIdentities.ContainsKey($parentId) -and $currentIdentities[$parentId] -eq $identities[$parentId] -and
                    $entry.CreationDate.ToUniversalTime() -ge $started.UtcDateTime -and $owned.Add([int]$entry.ProcessId)) {
                    $identities[[int]$entry.ProcessId] = $entry.CreationDate
                    $added = $true
                }
            }
        } while ($added)
        if ([DateTimeOffset]::UtcNow -ge $deadline) { $timedOut = $true; break }
        Start-Sleep -Milliseconds 200
        $process.Refresh()
    } while (!$process.HasExited)
    if (!$timedOut) {
        $process.WaitForExit()
        $exitCode = $process.ExitCode
        $completion = if ($exitCode -eq 0) { 'PASS' } elseif ($exitCode -eq 2 -and $Suite -eq 'Office') { 'NOT RUN' } elseif ($exitCode -eq 2 -and $Suite -eq 'Native') { 'BLOCKED' } else { 'FAIL' }
    } else { $completion = 'FAIL' }
} finally {
    # External recovery remains effective even if an AHK callback blocks.
    if ($Suite -in @('Native', 'F7', 'AltF7', 'AltF7Toggle')) {
        if (-not ('Cp01KeyRelease' -as [type])) {
            Add-Type 'using System.Runtime.InteropServices; public static class Cp01KeyRelease { [DllImport("user32.dll")] public static extern void keybd_event(byte key, byte scan, uint flags, System.UIntPtr extra); }'
        }
        $releaseKeys = if ($Suite -eq 'Native') { @(0x86,0x87,0xA2,0xA3,0xA4,0xA5) } else { @(0x76,0xA2,0xA3,0xA4,0xA5) }
        foreach ($key in $releaseKeys) { [Cp01KeyRelease]::keybd_event([byte]$key, 0, 2, [UIntPtr]::Zero) }
    }
    $pidFile = Join-Path $evidence 'owned-pids.txt'
    if (Test-Path -LiteralPath $pidFile) {
        foreach ($line in Get-Content -LiteralPath $pidFile) {
            $trackedPid = [int]$line
            $entry = Get-CimInstance Win32_Process -Filter "ProcessId=$trackedPid"
            if ($entry -and $entry.CreationDate.ToUniversalTime() -ge $started.UtcDateTime -and $entry.ExecutablePath -and $entry.ExecutablePath.StartsWith($evidence + '\', [StringComparison]::OrdinalIgnoreCase)) {
                [void]$owned.Add($trackedPid)
                $identities[$trackedPid] = $entry.CreationDate
            }
        }
    }
    foreach ($trackedPid in $owned) {
        $entry = Get-CimInstance Win32_Process -Filter "ProcessId=$trackedPid"
        if ($entry -and $identities.ContainsKey($trackedPid) -and $entry.CreationDate -eq $identities[$trackedPid]) {
            Stop-Process -Id $trackedPid -ErrorAction SilentlyContinue
            Wait-Process -Id $trackedPid -Timeout 3 -ErrorAction SilentlyContinue
        }
    }
    $survivors = @()
    foreach ($trackedPid in $owned) {
        $entry = Get-CimInstance Win32_Process -Filter "ProcessId=$trackedPid"
        if ($entry -and $identities.ContainsKey($trackedPid) -and $entry.CreationDate -eq $identities[$trackedPid]) { $survivors += $trackedPid }
    }
    if ($survivors.Count) { $completion = 'FAIL' }
    $assertions = $null
    $logText = if (Test-Path -LiteralPath $log) { Get-Content -LiteralPath $log -Raw } else { '' }
    $classification = if ($logText -match 'RESULT ([^\r\n]+)') { $Matches[1] } else { $null }
    if ($Suite -eq 'Native' -and $logText -match 'BLOCKED / INCONCLUSIVE - FOREGROUND INTERFERENCE' -and !$survivors.Count) {
        $completion = 'BLOCKED'
    }
    if ($Suite -in @('Native', 'Harness') -and !$survivors.Count) {
        # Exact run-owned artifacts only; retain logs/results and runtime copies.
        $artifactDirectory = if ($Suite -eq 'Native') { Join-Path $evidence 'targets' } else { $evidence }
        Get-ChildItem -LiteralPath $artifactDirectory -File | Where-Object { $_.Name -match '\.(ready|pending|input)$' } |
            ForEach-Object { Remove-Item -LiteralPath $_.FullName }
    }
    if ($logText -match 'PASS assertions=(\d+)') { $assertions = [int]$Matches[1] }
    elseif ($logText -match 'ALL CHECKS PASSED: (\d+)') { $assertions = [int]$Matches[1] }
    if ($Suite -in @('Policy', 'Harness', 'Native') -and $completion -eq 'PASS' -and !$assertions) { $completion = 'FAIL' }
    $legacyReport = if ($Suite -eq 'F7') { Join-Path $env:TEMP 'F7Hub-test_f7hub_launcher.txt' } elseif ($Suite -eq 'Follower') { Join-Path $env:TEMP 'F7Hub-test_magnetic_window_follower.txt' } else { $null }
    if ($legacyReport -and (Test-Path -LiteralPath $legacyReport)) {
        Copy-Item -LiteralPath $legacyReport -Destination (Join-Path $evidence "$Suite-$stamp.legacy.txt")
    }
    $result = [ordered]@{
        schema_version = 1; suite = $Suite; result = $completion; provenance = 'FRESH'; environment = 'WINDOWS_NATIVE'
        started_at = $started.ToString('o'); finished_at = [DateTimeOffset]::UtcNow.ToString('o')
        command = @($AhkPath) + $arguments; working_directory = $root; exit_code = $exitCode
        timeout_seconds = $TimeoutSeconds; timed_out = $timedOut; log_path = $log; error_log_path = $errLog
        owned_pids = @($owned); survivors = $survivors; assertions = $assertions; input_sha256 = $inputHashes
        interactive = $interactive; monitor = if ($interactive) { $Monitor } else { $null }; classification = $classification
        candidate_manifest = $null; notes = 'Bind final manifest after validation; native input is injected, not manual physical hardware acceptance.'
    }
    $result | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $resultPath -Encoding utf8
    $readback = Get-Content -LiteralPath $resultPath -Raw | ConvertFrom-Json
    Write-Output "Result=$($readback.result) suite=$Suite exit=$exitCode assertions=$assertions survivors=$($survivors.Count) evidence=$resultPath"
    Get-Content -LiteralPath $log -Tail 8
    Get-Content -LiteralPath $errLog -Tail 8
}
if ($completion -notin @('PASS', 'NOT RUN')) { exit 1 }
