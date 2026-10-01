-- Approve the exact CRLF checkout bytes of the reviewed production script.
-- A changed or missing Slice 042 row must fail the whole migration.
CREATE TEMP TABLE _system_snapshot_checksum_assertion (
    updated_rows INTEGER NOT NULL CHECK (updated_rows = 1)
);

UPDATE scripts SET checksum_sha256 =
    '7389e1b402050da4811270d71b92b1a1c53fff151e5300c2b2c6bdbc3fcef758'
WHERE script_code = 'diagnostic.windows.system_snapshot' COLLATE BINARY
  AND category_id IS NULL
  AND name = 'Windows System Snapshot'
  AND description = 'Collects a local read-only Windows system snapshot.'
  AND relative_path = 'PowerShell/Diagnostics/Get-SystemSnapshot.ps1' COLLATE BINARY
  AND script_type = 'DIAGNOSTIC'
  AND runtime = 'POWERSHELL_7'
  AND risk_level = 'LOW'
  AND privilege_level = 'STANDARD_USER'
  AND version = '1.0.0'
  AND checksum_sha256 IS NULL
  AND timeout_seconds = 60
  AND requires_structured_output = 1
  AND is_enabled = 1
  AND created_at = '2026-09-30T00:00:00.000Z'
  AND updated_at = '2026-09-30T00:00:00.000Z';

INSERT INTO _system_snapshot_checksum_assertion (updated_rows) VALUES (changes());
DROP TABLE _system_snapshot_checksum_assertion;
