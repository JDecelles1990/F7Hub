<#
.SYNOPSIS
Collects local, read-only Windows network configuration.
.DESCRIPTION
Returns one structured JSON result for the approved F7Hub diagnostic execution path.
#>
# TCP/IP-enabled interfaces are not an exhaustive adapter or connectivity report.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$warningFlags = [ordered]@{
    Metadata = $false
    Addresses = $false
    Gateways = $false
    Dns = $false
    Truncated = $false
}

function Read-NetworkSnapshotProperty($Record, [string]$Name) {
    try {
        $property = $Record.PSObject.Properties[$Name]
        if ($null -eq $property) { return [pscustomobject]@{ Value = $null } }
        return [pscustomobject]@{ Value = $property.Value }
    } catch {
        # Never expose provider exceptions or substitute a scalar default.
        return [pscustomobject]@{ Value = $null }
    }
}

function Convert-NetworkSnapshotText($Value, [int]$Limit) {
    if ($Value -isnot [string] -or [string]::IsNullOrWhiteSpace($Value)) {
        $warningFlags.Metadata = $true
        return $null
    }
    if ($Value.Length -gt $Limit) {
        $warningFlags.Truncated = $true
        # Do not split a UTF-16 surrogate pair at the boundary.
        if ([char]::IsHighSurrogate($Value[$Limit - 1])) { $Limit-- }
        return $Value.Substring(0, $Limit)
    }
    return $Value
}

function Convert-NetworkSnapshotAddresses($Value, [int]$Limit, [string]$WarningKey, [bool]$PreserveOrder) {
    $unavailable = [pscustomobject]@{ IPv4 = $null; IPv6 = $null; All = $null }
    if ($null -eq $Value -or $Value -isnot [array]) {
        $warningFlags[$WarningKey] = $true
        return $unavailable
    }
    $seen = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
    $all = [Collections.Generic.List[string]]::new()
    $v4 = [Collections.Generic.List[string]]::new()
    $v6 = [Collections.Generic.List[string]]::new()
    foreach ($entry in $Value) {
        $address = $null
        if ($entry -isnot [string] -or $entry.Length -gt 64 -or
            -not [Net.IPAddress]::TryParse($entry, [ref]$address)) {
            $warningFlags[$WarningKey] = $true
            return $unavailable
        }
        $normalized = $address.ToString()
        if ($seen.Add($normalized)) {
            $all.Add($normalized)
            if ($address.AddressFamily -eq [Net.Sockets.AddressFamily]::InterNetwork) {
                $v4.Add($normalized)
            } else {
                $v6.Add($normalized)
            }
        }
    }
    $ipv4 = $v4.ToArray()
    $ipv6 = $v6.ToArray()
    [Array]::Sort($ipv4, [StringComparer]::Ordinal)
    [Array]::Sort($ipv6, [StringComparer]::Ordinal)
    $ordered = $all.ToArray()
    if (-not $PreserveOrder) { [Array]::Sort($ordered, [StringComparer]::Ordinal) }
    if (($PreserveOrder -and $ordered.Count -gt $Limit) -or
        (-not $PreserveOrder -and ($ipv4.Count -gt $Limit -or $ipv6.Count -gt $Limit))) {
        $warningFlags.Truncated = $true
    }
    return [pscustomobject]@{
        IPv4 = @($ipv4 | Select-Object -First $Limit)
        IPv6 = @($ipv6 | Select-Object -First $Limit)
        All = @($ordered | Select-Object -First $Limit)
    }
}

$data = [ordered]@{ computerName = $null; interfaces = @() }
$result = [ordered]@{
    schemaVersion = 1
    operation = 'Get-NetworkSnapshot'
    success = $false
    status = 'ERROR'
    message = 'Unable to collect required local Windows network configuration.'
    data = $data
    warnings = @()
    errors = @('Required local network configuration is unavailable.')
}

try {
    $data.computerName = Convert-NetworkSnapshotText ([Environment]::MachineName) 128
} catch {
    $warningFlags.Metadata = $true
}

try {
    $records = @(Get-CimInstance -Namespace root/cimv2 -ClassName Win32_NetworkAdapterConfiguration -Filter 'IPEnabled=True' -Property InterfaceIndex, Description, IPAddress, DefaultIPGateway, DNSServerSearchOrder, DHCPEnabled -OperationTimeoutSec 20 -ErrorAction Stop)
    $indices = [Collections.Generic.HashSet[uint32]]::new()
    $inventory = @(foreach ($record in $records) {
        $index = (Read-NetworkSnapshotProperty $record 'InterfaceIndex').Value
        if (($index -isnot [byte] -and $index -isnot [sbyte] -and
             $index -isnot [int16] -and $index -isnot [uint16] -and
             $index -isnot [int32] -and $index -isnot [uint32] -and
             $index -isnot [int64] -and $index -isnot [uint64]) -or
            $index -lt 0 -or $index -gt [uint32]::MaxValue -or
            -not $indices.Add([uint32]$index)) {
            throw 'Invalid required interface inventory.'
        }
        [pscustomobject]@{ Index = [uint32]$index; Record = $record }
    })
    if ($inventory.Count -gt 64) { $warningFlags.Truncated = $true }
    # Build off-result; a required failure cannot publish a partial inventory.
    $interfaces = @(foreach ($item in @($inventory | Sort-Object Index | Select-Object -First 64)) {
        $record = $item.Record
        $addresses = Convert-NetworkSnapshotAddresses (Read-NetworkSnapshotProperty $record 'IPAddress').Value 16 'Addresses' $false
        $gateways = Convert-NetworkSnapshotAddresses (Read-NetworkSnapshotProperty $record 'DefaultIPGateway').Value 8 'Gateways' $false
        $dns = Convert-NetworkSnapshotAddresses (Read-NetworkSnapshotProperty $record 'DNSServerSearchOrder').Value 16 'Dns' $true
        $dhcp = (Read-NetworkSnapshotProperty $record 'DHCPEnabled').Value
        if ($dhcp -isnot [bool]) {
            $dhcp = $null
            $warningFlags.Metadata = $true
        }
        [ordered]@{
            interfaceIndex = $item.Index
            interfaceDescription = Convert-NetworkSnapshotText (Read-NetworkSnapshotProperty $record 'Description').Value 256
            ipv4Addresses = $addresses.IPv4
            ipv6Addresses = $addresses.IPv6
            ipv4DefaultGateways = $gateways.IPv4
            ipv6DefaultGateways = $gateways.IPv6
            dnsServerAddresses = $dns.All
            dhcpEnabled = $dhcp
        }
    })
    $data.interfaces = $interfaces
    $result.success = $true
    $result.status = 'PASS'
    $result.message = 'Local Windows network configuration snapshot collected.'
    $result.errors = @()
} catch {
    $data.interfaces = @()
    # Deliberately omit exception messages, error records and provider objects.
}

if ($result.success) {
    $warningMessages = [ordered]@{
        Metadata = 'One or more network metadata values are unavailable.'
        Addresses = 'One or more interface address collections are unavailable.'
        Gateways = 'One or more default gateway collections are unavailable.'
        Dns = 'One or more DNS server collections are unavailable.'
        Truncated = 'Network snapshot output was limited to documented bounds.'
    }
    $result.warnings = @(foreach ($key in $warningMessages.Keys) {
        if ($warningFlags[$key]) { $warningMessages[$key] }
    })
    if ($result.warnings.Count -gt 0) {
        $result.status = 'WARNING'
        $result.message = 'Network configuration collected with incomplete or bounded data.'
    }
}

$json = ConvertTo-Json -InputObject $result -Depth 6 -Compress
if ([Text.Encoding]::UTF8.GetByteCount($json) -gt 524288) {
    $data.computerName = $null
    $data.interfaces = @()
    $result.success = $false
    $result.status = 'ERROR'
    $result.message = 'Unable to collect required local Windows network configuration.'
    $result.warnings = @()
    $result.errors = @('Network snapshot exceeded its output size limit.')
    $json = ConvertTo-Json -InputObject $result -Depth 6 -Compress
}
$json
if ($result.success) { exit 0 }
exit 1
