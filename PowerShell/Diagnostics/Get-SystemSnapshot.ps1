# Local, read-only Windows snapshot. No application execution path is provided.
$data = [ordered]@{
    computerName = $null
    windowsCaption = $null
    windowsVersion = $null
    windowsBuild = $null
    osArchitecture = $null
    lastBootUtc = $null
    uptimeSeconds = $null
    powerShellVersion = $PSVersionTable.PSVersion.ToString()
    physicalMemoryBytes = $null
    fixedDrives = @()
}
$result = [ordered]@{
    schemaVersion = 1
    operation = 'Get-SystemSnapshot'
    success = $false
    status = 'ERROR'
    message = 'Unable to collect required Windows operating system information.'
    data = $data
    warnings = @()
    errors = @('Required operating system information is unavailable.')
}

try {
    $os = Get-CimInstance -ClassName Win32_OperatingSystem -Property CSName, Caption, Version, BuildNumber, OSArchitecture, LastBootUpTime, TotalVisibleMemorySize -OperationTimeoutSec 20 -ErrorAction Stop
    if ($null -eq $os) {
        throw 'No operating system result.'
    }
    $bootUtc = ([datetime]$os.LastBootUpTime).ToUniversalTime()
    $data.computerName = [string]$os.CSName
    $data.windowsCaption = [string]$os.Caption
    $data.windowsVersion = [string]$os.Version
    $data.windowsBuild = [string]$os.BuildNumber
    $data.osArchitecture = [string]$os.OSArchitecture
    $data.lastBootUtc = $bootUtc.ToString('yyyy-MM-ddTHH:mm:ss.fffZ', [cultureinfo]::InvariantCulture)
    $data.uptimeSeconds = [long][math]::Max(0, [math]::Floor(([datetime]::UtcNow - $bootUtc).TotalSeconds))
    $data.physicalMemoryBytes = [long]$os.TotalVisibleMemorySize * 1024L
    $result.success = $true
    $result.status = 'PASS'
    $result.message = 'Local Windows system snapshot collected.'
    $result.errors = @()
} catch {
    # Deliberately omit the exception text from the machine-readable result.
}

if ($result.success) {
    try {
        $drives = @(Get-CimInstance -ClassName Win32_LogicalDisk -Filter 'DriveType=3' -Property DeviceID, Size, FreeSpace -OperationTimeoutSec 20 -ErrorAction Stop)
        $missingDriveMeasurement = $false
        $data.fixedDrives = @(foreach ($drive in @($drives | Sort-Object -Property DeviceID | Select-Object -First 64)) {
            $capacityBytes = $null
            if ($null -eq $drive.Size) {
                $missingDriveMeasurement = $true
            } else {
                $capacityBytes = [long]$drive.Size
            }
            $freeBytes = $null
            if ($null -eq $drive.FreeSpace) {
                $missingDriveMeasurement = $true
            } else {
                $freeBytes = [long]$drive.FreeSpace
            }
            [ordered]@{
                device = [string]$drive.DeviceID
                capacityBytes = $capacityBytes
                freeBytes = $freeBytes
            }
        })
        if ($missingDriveMeasurement) {
            $result.status = 'WARNING'
            $result.message = 'System information collected; one or more fixed-drive measurements are unavailable.'
            $result.warnings = @('One or more fixed-drive measurements are unavailable.')
        }
    } catch {
        $data.fixedDrives = @()
        $result.status = 'WARNING'
        $result.message = 'System information collected; fixed-drive information is unavailable.'
        $result.warnings = @('Fixed-drive information is unavailable.')
    }
}

ConvertTo-Json -InputObject $result -Depth 6 -Compress
if ($result.success) { exit 0 }
exit 1
