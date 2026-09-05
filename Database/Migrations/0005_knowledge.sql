CREATE TABLE knowledge_articles (
    knowledge_article_id INTEGER PRIMARY KEY,

    article_code TEXT NOT NULL COLLATE NOCASE UNIQUE
        CHECK (length(trim(article_code)) > 0),

    category_id INTEGER,

    title TEXT NOT NULL
        CHECK (length(trim(title)) > 0),

    summary TEXT,

    body_markdown TEXT NOT NULL,

    status TEXT NOT NULL DEFAULT 'DRAFT'
        CHECK (
            status IN (
                'DRAFT',
                'PUBLISHED',
                'ARCHIVED'
            )
        ),

    version_number INTEGER NOT NULL DEFAULT 1
        CHECK (version_number >= 1),

    created_by TEXT,
    updated_by TEXT,

    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    published_at TEXT,

    FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
        ON DELETE SET NULL,

    CHECK (
        published_at IS NULL
        OR status IN ('PUBLISHED', 'ARCHIVED')
    )
);

CREATE TABLE knowledge_article_versions (
    knowledge_article_version_id INTEGER PRIMARY KEY,

    knowledge_article_id INTEGER NOT NULL,

    version_number INTEGER NOT NULL
        CHECK (version_number >= 1),

    title TEXT NOT NULL
        CHECK (length(trim(title)) > 0),

    summary TEXT,
    body_markdown TEXT NOT NULL,

    change_summary TEXT,
    created_by TEXT,
    created_at TEXT NOT NULL,

    FOREIGN KEY (knowledge_article_id)
        REFERENCES knowledge_articles(knowledge_article_id)
        ON DELETE CASCADE,

    UNIQUE (
        knowledge_article_id,
        version_number
    )
);

CREATE TABLE knowledge_article_links (
    knowledge_article_link_id INTEGER PRIMARY KEY,

    knowledge_article_id INTEGER NOT NULL,

    link_type TEXT,

    label TEXT NOT NULL
        CHECK (length(trim(label)) > 0),

    url TEXT NOT NULL
        CHECK (length(trim(url)) > 0),

    sort_order INTEGER NOT NULL DEFAULT 0,

    created_at TEXT NOT NULL,

    FOREIGN KEY (knowledge_article_id)
        REFERENCES knowledge_articles(knowledge_article_id)
        ON DELETE CASCADE
);

CREATE TABLE knowledge_article_relationships (
    knowledge_article_relationship_id INTEGER PRIMARY KEY,

    knowledge_article_id INTEGER NOT NULL,
    related_knowledge_article_id INTEGER NOT NULL,

    relationship_type TEXT NOT NULL
        CHECK (
            relationship_type IN (
                'RELATED',
                'PREREQUISITE',
                'SUPERSEDES',
                'DUPLICATES'
            )
        ),

    created_at TEXT NOT NULL,

    FOREIGN KEY (knowledge_article_id)
        REFERENCES knowledge_articles(knowledge_article_id)
        ON DELETE CASCADE,

    FOREIGN KEY (related_knowledge_article_id)
        REFERENCES knowledge_articles(knowledge_article_id)
        ON DELETE CASCADE,

    CHECK (
        knowledge_article_id
        <> related_knowledge_article_id
    ),

    UNIQUE (
        knowledge_article_id,
        related_knowledge_article_id,
        relationship_type
    )
);

CREATE TABLE ticket_knowledge_articles (
    ticket_id INTEGER NOT NULL,
    knowledge_article_id INTEGER NOT NULL,

    relationship_type TEXT NOT NULL DEFAULT 'RELATED'
        CHECK (
            relationship_type IN (
                'RELATED',
                'APPLIED',
                'RESOLUTION_SOURCE'
            )
        ),

    linked_by TEXT,
    linked_at TEXT NOT NULL,

    PRIMARY KEY (
        ticket_id,
        knowledge_article_id,
        relationship_type
    ),

    FOREIGN KEY (ticket_id)
        REFERENCES tickets(ticket_id)
        ON DELETE CASCADE,

    FOREIGN KEY (knowledge_article_id)
        REFERENCES knowledge_articles(knowledge_article_id)
        ON DELETE CASCADE
);

CREATE TABLE knowledge_article_tags (
    knowledge_article_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,

    created_at TEXT NOT NULL,

    PRIMARY KEY (
        knowledge_article_id,
        tag_id
    ),

    FOREIGN KEY (knowledge_article_id)
        REFERENCES knowledge_articles(knowledge_article_id)
        ON DELETE CASCADE,

    FOREIGN KEY (tag_id)
        REFERENCES tags(tag_id)
        ON DELETE CASCADE
);

CREATE INDEX idx_knowledge_articles_status_updated
    ON knowledge_articles(
        status,
        updated_at DESC
    );

CREATE INDEX idx_knowledge_articles_category_status
    ON knowledge_articles(
        category_id,
        status
    );

CREATE INDEX idx_knowledge_versions_article_version
    ON knowledge_article_versions(
        knowledge_article_id,
        version_number DESC
    );

CREATE INDEX idx_knowledge_links_article_sort
    ON knowledge_article_links(
        knowledge_article_id,
        sort_order
    );

CREATE INDEX idx_knowledge_relationships_related_article
    ON knowledge_article_relationships(
        related_knowledge_article_id
    );

CREATE INDEX idx_ticket_knowledge_articles_article
    ON ticket_knowledge_articles(
        knowledge_article_id,
        ticket_id
    );

CREATE INDEX idx_knowledge_article_tags_tag_id
    ON knowledge_article_tags(
        tag_id,
        knowledge_article_id
    );
