-- S05: current trusted Setup evidence; never backfill consent.
CREATE TABLE clipboard_history_consent (
    singleton_id INTEGER PRIMARY KEY CHECK (singleton_id = 1),
    database_instance_id TEXT NOT NULL
        CHECK (typeof(database_instance_id) = 'text'
          AND length(database_instance_id) = 32
          AND database_instance_id NOT GLOB '*[^0-9a-f]*'),
    database_scope TEXT NOT NULL
        CHECK (typeof(database_scope) = 'text' AND length(database_scope) = 64
          AND database_scope NOT GLOB '*[^0-9a-f]*'),
    profile_scope TEXT NOT NULL
        CHECK (typeof(profile_scope) = 'text' AND length(profile_scope) = 64
          AND profile_scope NOT GLOB '*[^0-9a-f]*'),
    purpose TEXT NOT NULL CHECK (purpose = 'clipboard_manual_durable_v1'),
    disclosure_version TEXT NOT NULL
        CHECK (disclosure_version = 'clipboard_setup_manual_history_v1'),
    policy_version TEXT NOT NULL CHECK (policy_version = 'clipboard_history_consent_v1'),
    consent_epoch INTEGER NOT NULL
        CHECK (typeof(consent_epoch) = 'integer' AND consent_epoch > 0),
    state TEXT NOT NULL CHECK (state IN ('GRANTED', 'REVOKED')),
    grant_settings_revision INTEGER NOT NULL
        CHECK (typeof(grant_settings_revision) = 'integer' AND grant_settings_revision >= 0),
    transition_settings_revision INTEGER NOT NULL
        CHECK (typeof(transition_settings_revision) = 'integer'
          AND transition_settings_revision >= grant_settings_revision),
    last_action_id TEXT NOT NULL
        CHECK (typeof(last_action_id) = 'text' AND length(last_action_id) = 32
          AND last_action_id NOT GLOB '*[^0-9a-f]*'),
    granted_at TEXT NOT NULL CHECK (granted_at GLOB
        '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9]Z'),
    revoked_at TEXT CHECK (revoked_at IS NULL OR revoked_at GLOB
        '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9]Z'),
    CHECK ((state = 'GRANTED' AND revoked_at IS NULL)
        OR (state = 'REVOKED' AND revoked_at IS NOT NULL)),
    FOREIGN KEY (singleton_id) REFERENCES settings_state(singleton_id) ON DELETE RESTRICT
);
