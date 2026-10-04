<#
.SYNOPSIS
Collects a local, read-only Windows services inventory.
.DESCRIPTION
Returns one structured JSON result; it does not control services or judge their health.
#>
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$warningFlags = [ordered]@{ Metadata = $false; Truncated = $false }

function Read-ServicesSnapshotProperty($Record, [string]$Name) {
    try {
        $property = $Record.PSObject.Properties[$Name]
        return [pscustomobject]@{ Value = $(if ($null -eq $property) { $null } else { $property.Value }) }
    } catch {
        return [pscustomobject]@{ Value = $null }
    }
}

function Convert-ServicesSnapshotText($Value, [int]$Limit, [bool]$Required) {
    $valid = $Value -is [string] -and -not [string]::IsNullOrWhiteSpace($Value)
    if ($valid) {
        for ($index = 0; $index -lt $Value.Length; $index++) {
            $category = [Globalization.CharUnicodeInfo]::GetUnicodeCategory($Value, $index)
            if ($category -in @('Control', 'Format', 'Surrogate', 'PrivateUse', 'OtherNotAssigned')) { $valid = $false; break }
            if ([char]::IsHighSurrogate($Value[$index])) { $index++ }
        }
    }
    if (-not $valid -or ($Required -and $Value.Length -gt $Limit)) {
        if ($Required) { throw 'Invalid required service identity.' }
        $warningFlags.Metadata = $true
        return $null
    }
    if ($Value.Length -gt $Limit) {
        $warningFlags.Truncated = $true
        if ([char]::IsHighSurrogate($Value[$Limit - 1])) { $Limit-- }
        return $Value.Substring(0, $Limit)
    }
    return $Value
}

$data = [ordered]@{ computerName = $null; services = @() }
$result = [ordered]@{
    schemaVersion = 1; operation = 'Get-ServicesSnapshot'; success = $false; status = 'ERROR'
    message = 'Unable to collect required local Windows services information.'
    data = $data; warnings = @(); errors = @('Required local services information is unavailable.')
}
try { $data.computerName = Convert-ServicesSnapshotText ([Environment]::MachineName) 128 $false }
catch { $warningFlags.Metadata = $true }
try {
    $records = @(Get-CimInstance -Namespace root/cimv2 -ClassName Win32_Service -Property Name,DisplayName,State,StartMode -OperationTimeoutSec 20 -ErrorAction Stop)
    $seen = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    $byName = [Collections.Generic.Dictionary[string,object]]::new([StringComparer]::Ordinal)
    foreach ($record in $records) {
        $name = Convert-ServicesSnapshotText (Read-ServicesSnapshotProperty $record 'Name').Value 256 $true
        if (-not $seen.Add($name)) { throw 'Duplicate required service identity.' }
        $byName.Add($name, $record)
    }
    $names = [string[]]@($byName.Keys)
    [Array]::Sort($names, [StringComparer]::Ordinal)
    if ($names.Count -gt 512) { $warningFlags.Truncated = $true }
    $services = @(foreach ($name in @($names | Select-Object -First 512)) {
        $record = $byName[$name]
        $state = (Read-ServicesSnapshotProperty $record 'State').Value
        if ($state -isnot [string] -or $state -cnotin @('Running','Stopped','Start Pending','Stop Pending','Continue Pending','Pause Pending','Paused')) {
            $state = $null; $warningFlags.Metadata = $true
        }
        $mode = (Read-ServicesSnapshotProperty $record 'StartMode').Value
        if ($mode -isnot [string] -or $mode -cnotin @('Auto','Manual','Disabled','Boot','System')) {
            $mode = $null; $warningFlags.Metadata = $true
        }
        [ordered]@{
            name = $name
            displayName = Convert-ServicesSnapshotText (Read-ServicesSnapshotProperty $record 'DisplayName').Value 256 $false
            state = $state; startupMode = $mode
        }
    })
    $data.services = $services
    $result.success = $true; $result.status = 'PASS'
    $result.message = 'Local Windows services snapshot collected.'; $result.errors = @()
} catch {
    $data.services = @()
    # Never serialize exception messages, provider objects or partial inventory.
}
if ($result.success) {
    $messages = [ordered]@{
        Metadata = 'One or more services metadata values are unavailable.'
        Truncated = 'Services snapshot output was limited to documented bounds.'
    }
    $result.warnings = @(foreach ($key in $messages.Keys) { if ($warningFlags[$key]) { $messages[$key] } })
    if ($result.warnings.Count) {
        $result.status = 'WARNING'
        $result.message = 'Services snapshot collected with incomplete or bounded data.'
    }
}
$json = ConvertTo-Json -InputObject $result -Depth 6 -Compress
if ([Text.Encoding]::UTF8.GetByteCount($json) -gt 524288) {
    $data.computerName = $null; $data.services = @()
    $result.success = $false; $result.status = 'ERROR'
    $result.message = 'Unable to collect required local Windows services information.'
    $result.warnings = @(); $result.errors = @('Services snapshot exceeded its output size limit.')
    $json = ConvertTo-Json -InputObject $result -Depth 6 -Compress
}
$json
if ($result.success) { exit 0 }
exit 1
