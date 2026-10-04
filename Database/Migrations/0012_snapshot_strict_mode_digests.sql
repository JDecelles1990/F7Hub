-- Refresh only the three reviewed diagnostic source identities.
-- Every expected prior registration must match, or the migration rolls back.
CREATE TEMP TABLE _snapshot_digest_assertion (
    updated_rows INTEGER NOT NULL CHECK (updated_rows = 1)
);

UPDATE scripts SET checksum_sha256 = 'c2b3931341a0a6d7e858f8a728e50c9cdc1bfbb41dd5545588c24a11e5103e19'
WHERE script_code = 'diagnostic.windows.system_snapshot' COLLATE BINARY
  AND category_id IS NULL
  AND name = 'Windows System Snapshot'
  AND description = 'Collects a local read-only Windows system snapshot.'
  AND relative_path = 'PowerShell/Diagnostics/Get-SystemSnapshot.ps1' COLLATE BINARY
  AND script_type = 'DIAGNOSTIC' AND runtime = 'POWERSHELL_7'
  AND risk_level = 'LOW' AND privilege_level = 'STANDARD_USER'
  AND version = '1.0.0'
  AND checksum_sha256 = '7389e1b402050da4811270d71b92b1a1c53fff151e5300c2b2c6bdbc3fcef758'
  AND timeout_seconds = 60 AND requires_structured_output = 1 AND is_enabled = 1
  AND created_at = '2026-09-30T00:00:00.000Z'
  AND updated_at = '2026-09-30T00:00:00.000Z';
INSERT INTO _snapshot_digest_assertion VALUES (changes());
DELETE FROM _snapshot_digest_assertion;

UPDATE scripts SET checksum_sha256 = 'f0b81a4a73c0db35333245be2ea4d0de76dbbd85d24b97a8ed39f2c74155400c'
WHERE script_code = 'diagnostic.windows.network_snapshot' COLLATE BINARY
  AND category_id IS NULL
  AND name = 'Windows Network Configuration Snapshot'
  AND description = 'Collects a local read-only Windows network configuration snapshot.'
  AND relative_path = 'PowerShell/Diagnostics/Get-NetworkSnapshot.ps1' COLLATE BINARY
  AND script_type = 'DIAGNOSTIC' AND runtime = 'POWERSHELL_7'
  AND risk_level = 'LOW' AND privilege_level = 'STANDARD_USER'
  AND version = '1.0.0'
  AND checksum_sha256 = 'aa126985b01c840b588ee3769d4c0a4a43e57ae5415f422cc8c9db1bafcb02b7'
  AND timeout_seconds = 60 AND requires_structured_output = 1 AND is_enabled = 1
  AND created_at = '2026-10-02T00:00:00.000Z'
  AND updated_at = '2026-10-02T00:00:00.000Z';
INSERT INTO _snapshot_digest_assertion VALUES (changes());
DELETE FROM _snapshot_digest_assertion;

UPDATE scripts SET checksum_sha256 = 'c747c65992518551c72e168e55ffc61bd1829572f804e318528d73fe53981a18'
WHERE script_code = 'diagnostic.windows.services_snapshot' COLLATE BINARY
  AND category_id IS NULL
  AND name = 'Windows Services Snapshot'
  AND description = 'Collects a local read-only Windows services snapshot.'
  AND relative_path = 'PowerShell/Diagnostics/Get-ServicesSnapshot.ps1' COLLATE BINARY
  AND script_type = 'DIAGNOSTIC' AND runtime = 'POWERSHELL_7'
  AND risk_level = 'LOW' AND privilege_level = 'STANDARD_USER'
  AND version = '1.0.0'
  AND checksum_sha256 = '8a48321800e4d8147f2dd94a9d83eebedace6ac4e45b3e38c00f74d280abc347'
  AND timeout_seconds = 60 AND requires_structured_output = 1 AND is_enabled = 1
  AND created_at = '2026-10-03T00:00:00.000Z'
  AND updated_at = '2026-10-03T00:00:00.000Z';
INSERT INTO _snapshot_digest_assertion VALUES (changes());
DROP TABLE _snapshot_digest_assertion;
