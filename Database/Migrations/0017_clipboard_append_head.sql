-- H01-B: content-free current append identity. Deliberately no historical backfill.
CREATE TABLE clipboard_append_head (
    singleton_id INTEGER PRIMARY KEY CHECK (singleton_id = 1),
    append_token TEXT NOT NULL UNIQUE CHECK (
        typeof(append_token) = 'text' AND length(append_token) = 36
        AND substr(append_token, 9, 1) = '-'
        AND substr(append_token, 14, 1) = '-'
        AND substr(append_token, 19, 1) = '-'
        AND substr(append_token, 24, 1) = '-'
        AND length(replace(append_token, '-', '')) = 32
        AND replace(append_token, '-', '') NOT GLOB '*[^0-9a-f]*'
    ),
    live_item_id INTEGER CHECK (
        live_item_id IS NULL OR (typeof(live_item_id) = 'integer' AND live_item_id > 0)
    ),
    item_revision INTEGER NOT NULL CHECK (
        typeof(item_revision) = 'integer' AND item_revision > 0
    ),
    FOREIGN KEY (live_item_id) REFERENCES clipboard_items(clipboard_item_id) ON DELETE SET NULL
);
