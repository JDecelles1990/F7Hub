-- D02: content-free completion receipts survive Item/Event deletion.
CREATE TABLE clipboard_operation_receipts (
    clipboard_operation_receipt_id INTEGER PRIMARY KEY CHECK (clipboard_operation_receipt_id > 0),
    producer_binding TEXT NOT NULL CHECK (length(producer_binding) BETWEEN 1 AND 128 AND producer_binding NOT GLOB '*[^A-Za-z0-9_.:-]*'),
    ingress_generation TEXT NOT NULL CHECK (length(ingress_generation) = 36),
    operation_id TEXT NOT NULL CHECK (length(operation_id) = 36),
    database_scope TEXT NOT NULL CHECK (length(database_scope) = 64 AND database_scope NOT GLOB '*[^0-9a-f]*'),
    request_profile TEXT NOT NULL CHECK (request_profile = 'clipboard_manual_durable_v1'),
    media_type TEXT NOT NULL CHECK (media_type = 'text/plain'),
    identity_profile TEXT NOT NULL CHECK (identity_profile = 'clipboard_text_exact_v1'),
    capture_method TEXT NOT NULL CHECK (capture_method IN ('F7HUB', 'AHK_MANUAL')),
    observed_at TEXT CHECK (observed_at IS NULL OR observed_at GLOB
        '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9]Z'),
    source_class TEXT CHECK (source_class IS NULL OR source_class IN ('terminal', 'browser', 'editor', 'unknown')),
    assessment_method TEXT NOT NULL CHECK (length(assessment_method) BETWEEN 1 AND 64 AND assessment_method NOT GLOB '*[^A-Za-z0-9_.:-]*'),
    assessment_version TEXT NOT NULL CHECK (length(assessment_version) BETWEEN 1 AND 64 AND assessment_version NOT GLOB '*[^A-Za-z0-9_.:-]*'),
    policy_version TEXT NOT NULL CHECK (length(policy_version) BETWEEN 1 AND 64 AND policy_version NOT GLOB '*[^A-Za-z0-9_.:-]*'),
    sensitivity TEXT NOT NULL CHECK (sensitivity = 'PERMITTED'),
    assessment_complete INTEGER NOT NULL CHECK (assessment_complete = 1),
    durable_history_authorized INTEGER NOT NULL CHECK (durable_history_authorized = 1),
    temporary_days INTEGER NOT NULL CHECK (temporary_days = 7),
    historical_item_id INTEGER NOT NULL CHECK (typeof(historical_item_id) = 'integer' AND historical_item_id > 0),
    historical_event_id INTEGER NOT NULL CHECK (typeof(historical_event_id) = 'integer' AND historical_event_id > 0),
    live_item_id INTEGER CHECK (live_item_id IS NULL OR live_item_id = historical_item_id),
    was_duplicate INTEGER NOT NULL CHECK (was_duplicate IN (0, 1)),
    captured_total INTEGER NOT NULL CHECK (typeof(captured_total) = 'integer' AND captured_total > 0),
    item_revision INTEGER NOT NULL CHECK (typeof(item_revision) = 'integer' AND item_revision > 0),
    retention_intent TEXT NOT NULL CHECK (retention_intent IN ('TEMPORARY', 'SAVED')),
    is_pinned INTEGER NOT NULL CHECK (is_pinned IN (0, 1)),
    item_expires_at TEXT CHECK (item_expires_at IS NULL OR item_expires_at GLOB
        '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9]Z'),
    accepted_at TEXT NOT NULL CHECK (accepted_at GLOB
        '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9]Z'),
    expires_at TEXT NOT NULL CHECK (expires_at GLOB
        '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9]Z'),
    CHECK (expires_at > accepted_at),
    CHECK (is_pinned = 0 OR retention_intent = 'SAVED'),
    CHECK ((retention_intent = 'TEMPORARY' AND item_expires_at IS NOT NULL AND item_expires_at > accepted_at)
        OR (retention_intent = 'SAVED' AND item_expires_at IS NULL)),
    FOREIGN KEY (live_item_id) REFERENCES clipboard_items(clipboard_item_id) ON DELETE SET NULL,
    UNIQUE (producer_binding, ingress_generation, operation_id)
);

CREATE INDEX idx_clipboard_receipts_expiry ON clipboard_operation_receipts(expires_at, clipboard_operation_receipt_id);
CREATE INDEX idx_clipboard_receipts_live_item ON clipboard_operation_receipts(live_item_id);
