INSERT INTO scripts (
    category_id, script_code, name, description, relative_path,
    script_type, runtime, risk_level, privilege_level, version,
    checksum_sha256, timeout_seconds, requires_structured_output,
    is_enabled, created_at, updated_at
) VALUES (
    NULL, 'diagnostic.windows.system_snapshot', 'Windows System Snapshot',
    'Collects a local read-only Windows system snapshot.',
    'PowerShell/Diagnostics/Get-SystemSnapshot.ps1',
    'DIAGNOSTIC', 'POWERSHELL_7', 'LOW', 'STANDARD_USER', '1.0.0',
    NULL, 60, 1, 1, '2026-09-30T00:00:00.000Z', '2026-09-30T00:00:00.000Z'
);
