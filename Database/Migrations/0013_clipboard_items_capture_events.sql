-- D01: storage/query foundation only; no capture admission or seed data.
CREATE TABLE clipboard_items (
    clipboard_item_id INTEGER PRIMARY KEY CHECK (clipboard_item_id > 0),
    raw_text TEXT NOT NULL CHECK (
        typeof(raw_text) = 'text' AND length(raw_text) > 0
        AND instr(raw_text, char(0)) = 0
        AND length(CAST(raw_text AS BLOB)) <= 65536
    ),
    media_type TEXT NOT NULL CHECK (media_type = 'text/plain'),
    identity_profile TEXT NOT NULL CHECK (identity_profile = 'clipboard_text_exact_v1'),
    sensitivity TEXT NOT NULL CHECK (sensitivity = 'PERMITTED'),
    assessment_complete INTEGER NOT NULL CHECK (assessment_complete = 1),
    assessment_method TEXT NOT NULL CHECK (length(trim(assessment_method)) > 0),
    assessment_version TEXT NOT NULL CHECK (length(trim(assessment_version)) > 0),
    retention_intent TEXT NOT NULL CHECK (retention_intent IN ('TEMPORARY', 'SAVED')),
    is_pinned INTEGER NOT NULL DEFAULT 0 CHECK (is_pinned IN (0, 1)),
    expires_at TEXT CHECK (
        expires_at IS NULL OR expires_at GLOB
        '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9]Z'
    ),
    first_received_at TEXT NOT NULL CHECK (first_received_at GLOB
        '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9]Z'),
    last_received_at TEXT NOT NULL CHECK (last_received_at GLOB
        '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9]Z'),
    captured_total INTEGER NOT NULL CHECK (typeof(captured_total) = 'integer' AND captured_total > 0),
    revision INTEGER NOT NULL DEFAULT 1 CHECK (typeof(revision) = 'integer' AND revision > 0),
    CHECK (first_received_at <= last_received_at),
    CHECK (is_pinned = 0 OR retention_intent = 'SAVED'),
    CHECK (
        (retention_intent = 'TEMPORARY' AND expires_at IS NOT NULL AND expires_at > last_received_at)
        OR (retention_intent = 'SAVED' AND expires_at IS NULL)
    )
);

CREATE TABLE clipboard_capture_events (
    clipboard_capture_event_id INTEGER PRIMARY KEY CHECK (clipboard_capture_event_id > 0),
    clipboard_item_id INTEGER NOT NULL,
    received_at TEXT NOT NULL CHECK (received_at GLOB
        '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9]Z'),
    observed_at TEXT CHECK (observed_at IS NULL OR observed_at GLOB
        '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9]Z'),
    capture_method TEXT NOT NULL CHECK (capture_method IN ('F7HUB', 'AHK_MANUAL')),
    source_class TEXT CHECK (source_class IS NULL OR source_class IN ('terminal', 'browser', 'editor', 'unknown')),
    producer_binding TEXT NOT NULL CHECK (length(producer_binding) BETWEEN 1 AND 128 AND length(trim(producer_binding)) > 0),
    ingress_generation TEXT NOT NULL CHECK (length(ingress_generation) BETWEEN 1 AND 128 AND length(trim(ingress_generation)) > 0),
    operation_id TEXT NOT NULL CHECK (length(operation_id) = 36),
    FOREIGN KEY (clipboard_item_id) REFERENCES clipboard_items(clipboard_item_id) ON DELETE CASCADE,
    UNIQUE (producer_binding, ingress_generation, operation_id)
);

CREATE INDEX idx_clipboard_items_recent
    ON clipboard_items(last_received_at DESC, clipboard_item_id DESC);
CREATE INDEX idx_clipboard_capture_events_item
    ON clipboard_capture_events(clipboard_item_id);
