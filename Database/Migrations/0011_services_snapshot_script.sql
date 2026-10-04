-- Install reviewed exact CRLF source bytes and catalog metadata atomically.
-- Reject equivalent Windows paths as well as the schema's NOCASE uniqueness.
CREATE TEMP TABLE _services_snapshot_conflict_assertion (
    conflicting_rows INTEGER NOT NULL CHECK (conflicting_rows = 0)
);
INSERT INTO _services_snapshot_conflict_assertion (conflicting_rows)
SELECT count(*) FROM scripts
WHERE script_code = 'diagnostic.windows.services_snapshot' COLLATE NOCASE
   OR replace(relative_path, char(92), '/') =
      'PowerShell/Diagnostics/Get-ServicesSnapshot.ps1' COLLATE NOCASE;
DROP TABLE _services_snapshot_conflict_assertion;

INSERT INTO scripts (
    category_id, script_code, name, description, relative_path,
    script_type, runtime, risk_level, privilege_level, version,
    checksum_sha256, timeout_seconds, requires_structured_output,
    is_enabled, created_at, updated_at
) VALUES (
    NULL, 'diagnostic.windows.services_snapshot', 'Windows Services Snapshot',
    'Collects a local read-only Windows services snapshot.',
    'PowerShell/Diagnostics/Get-ServicesSnapshot.ps1',
    'DIAGNOSTIC', 'POWERSHELL_7', 'LOW', 'STANDARD_USER', '1.0.0',
    '8a48321800e4d8147f2dd94a9d83eebedace6ac4e45b3e38c00f74d280abc347',
    60, 1, 1, '2026-10-03T00:00:00.000Z', '2026-10-03T00:00:00.000Z'
);
