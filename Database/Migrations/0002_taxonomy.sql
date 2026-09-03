CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY,

    scope TEXT NOT NULL CHECK (
        scope IN (
            'GENERAL',
            'TICKET',
            'KNOWLEDGE',
            'SCRIPT',
            'PROMPT',
            'CLIPBOARD',
            'DIAGNOSTIC'
        )
    ),

    name TEXT NOT NULL COLLATE NOCASE
        CHECK (length(trim(name)) > 0),

    slug TEXT NOT NULL COLLATE NOCASE UNIQUE
        CHECK (length(trim(slug)) > 0),

    parent_category_id INTEGER,

    description TEXT,

    is_active INTEGER NOT NULL DEFAULT 1
        CHECK (is_active IN (0, 1)),

    sort_order INTEGER NOT NULL DEFAULT 0,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    FOREIGN KEY (parent_category_id)
        REFERENCES categories(category_id)
        ON DELETE SET NULL,

    CHECK (
        parent_category_id IS NULL
        OR parent_category_id <> category_id
    )
);

CREATE TABLE tags (
    tag_id INTEGER PRIMARY KEY,

    name TEXT NOT NULL COLLATE NOCASE UNIQUE
        CHECK (length(trim(name)) > 0),

    slug TEXT NOT NULL COLLATE NOCASE UNIQUE
        CHECK (length(trim(slug)) > 0),

    description TEXT,

    created_at TEXT NOT NULL
);

CREATE INDEX idx_categories_parent_category_id
    ON categories(parent_category_id);

CREATE INDEX idx_categories_scope_active_sort
    ON categories(
        scope,
        is_active,
        sort_order
    );
