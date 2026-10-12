-- USER overrides only. Definitions/defaults and operational capability stay in Python.
CREATE TABLE settings_state (
    singleton_id INTEGER PRIMARY KEY CHECK (singleton_id = 1),
    revision INTEGER NOT NULL CHECK (typeof(revision) = 'integer' AND revision >= 0)
);
INSERT INTO settings_state (singleton_id, revision) VALUES (1, 0);

CREATE TABLE settings_user_overrides (
    setting_key TEXT PRIMARY KEY NOT NULL
        CHECK (typeof(setting_key) = 'text' AND length(setting_key) BETWEEN 3 AND 128),
    value_type TEXT NOT NULL CHECK (value_type = 'BOOLEAN'),
    value_text TEXT NOT NULL CHECK (value_text IN ('true', 'false'))
);
