-- Install reviewed exact CRLF source bytes and catalog metadata atomically.
-- Reject equivalent Windows paths as well as the schema's NOCASE uniqueness.
CREATE TEMP TABLE _network_snapshot_conflict_assertion (
    conflicting_rows INTEGER NOT NULL CHECK (conflicting_rows = 0)
);
INSERT INTO _network_snapshot_conflict_assertion (conflicting_rows)
SELECT count(*) FROM scripts
WHERE script_code = 'diagnostic.windows.network_snapshot' COLLATE NOCASE
   OR replace(relative_path, char(92), '/') =
      'PowerShell/Diagnostics/Get-NetworkSnapshot.ps1' COLLATE NOCASE;
DROP TABLE _network_snapshot_conflict_assertion;

INSERT INTO scripts (
    category_id, script_code, name, description, relative_path,
    script_type, runtime, risk_level, privilege_level, version,
    checksum_sha256, timeout_seconds, requires_structured_output,
    is_enabled, created_at, updated_at
) VALUES (
    NULL, 'diagnostic.windows.network_snapshot', 'Windows Network Configuration Snapshot',
    'Collects a local read-only Windows network configuration snapshot.',
    'PowerShell/Diagnostics/Get-NetworkSnapshot.ps1',
    'DIAGNOSTIC', 'POWERSHELL_7', 'LOW', 'STANDARD_USER', '1.0.0',
    'aa126985b01c840b588ee3769d4c0a4a43e57ae5415f422cc8c9db1bafcb02b7',
    60, 1, 1, '2026-10-02T00:00:00.000Z', '2026-10-02T00:00:00.000Z'
);
