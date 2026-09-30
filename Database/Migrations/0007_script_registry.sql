CREATE TABLE scripts (
    script_id INTEGER PRIMARY KEY,
    category_id INTEGER,
    script_code TEXT NOT NULL COLLATE NOCASE UNIQUE
        CHECK (length(trim(script_code)) > 0),
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    description TEXT,
    relative_path TEXT NOT NULL COLLATE NOCASE UNIQUE
        CHECK (length(trim(relative_path)) > 0),
    script_type TEXT NOT NULL CHECK (script_type IN (
        'DIAGNOSTIC', 'REMEDIATION', 'ADMINISTRATIVE',
        'REPORT', 'UTILITY', 'INTEGRATION'
    )),
    runtime TEXT NOT NULL DEFAULT 'POWERSHELL_7'
        CHECK (runtime IN ('POWERSHELL_7', 'WINDOWS_POWERSHELL_5_1')),
    risk_level TEXT NOT NULL DEFAULT 'LOW'
        CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    privilege_level TEXT NOT NULL DEFAULT 'STANDARD_USER'
        CHECK (privilege_level IN (
            'STANDARD_USER', 'LOCAL_ADMIN', 'M365_AUTHENTICATED',
            'M365_PRIVILEGED', 'SPECIAL_ROLE'
        )),
    version TEXT,
    checksum_sha256 TEXT,
    timeout_seconds INTEGER NOT NULL DEFAULT 120
        CHECK (timeout_seconds > 0),
    requires_structured_output INTEGER NOT NULL DEFAULT 1
        CHECK (requires_structured_output IN (0, 1)),
    is_enabled INTEGER NOT NULL DEFAULT 0
        CHECK (is_enabled IN (0, 1)),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE SET NULL
);

CREATE INDEX idx_scripts_enabled_name
    ON scripts(is_enabled, name COLLATE NOCASE, script_id);

CREATE INDEX idx_scripts_category_id ON scripts(category_id);
