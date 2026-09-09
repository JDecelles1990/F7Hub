CREATE VIRTUAL TABLE knowledge_articles_fts
USING fts5(
    article_code,
    title,
    summary,
    body_markdown,

    content = 'knowledge_articles',
    content_rowid = 'knowledge_article_id',

    tokenize = 'unicode61'
);

CREATE TRIGGER knowledge_articles_ai
AFTER INSERT ON knowledge_articles
BEGIN
    INSERT INTO knowledge_articles_fts (
        rowid,
        article_code,
        title,
        summary,
        body_markdown
    )
    VALUES (
        new.knowledge_article_id,
        new.article_code,
        new.title,
        new.summary,
        new.body_markdown
    );
END;

CREATE TRIGGER knowledge_articles_ad
AFTER DELETE ON knowledge_articles
BEGIN
    INSERT INTO knowledge_articles_fts (
        knowledge_articles_fts,
        rowid,
        article_code,
        title,
        summary,
        body_markdown
    )
    VALUES (
        'delete',
        old.knowledge_article_id,
        old.article_code,
        old.title,
        old.summary,
        old.body_markdown
    );
END;

CREATE TRIGGER knowledge_articles_au
AFTER UPDATE OF article_code, title, summary, body_markdown ON knowledge_articles
BEGIN
    INSERT INTO knowledge_articles_fts (
        knowledge_articles_fts,
        rowid,
        article_code,
        title,
        summary,
        body_markdown
    )
    VALUES (
        'delete',
        old.knowledge_article_id,
        old.article_code,
        old.title,
        old.summary,
        old.body_markdown
    );

    INSERT INTO knowledge_articles_fts (
        rowid,
        article_code,
        title,
        summary,
        body_markdown
    )
    VALUES (
        new.knowledge_article_id,
        new.article_code,
        new.title,
        new.summary,
        new.body_markdown
    );
END;

INSERT INTO knowledge_articles_fts(knowledge_articles_fts)
VALUES ('rebuild');
