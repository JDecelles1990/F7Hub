from __future__ import annotations

import hashlib
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest

from f7hub.infrastructure.database import (
    bootstrap_database,
    database_connection,
    run_foreign_key_check,
    run_integrity_check,
)
from f7hub.infrastructure.migrations import (
    MigrationApplicationError,
    discover_migrations,
    list_applied_migrations,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PRODUCTION_MIGRATIONS = tuple(
    PROJECT_ROOT / "Database" / "Migrations" / filename
    for filename in (
        "0001_core.sql",
        "0002_taxonomy.sql",
        "0003_companies_contacts.sql",
        "0004_tickets.sql",
        "0005_knowledge.sql",
    )
)
TIMESTAMP = "2026-09-04T00:00:00.000Z"


class KnowledgeMigrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.temporary_path = Path(self._temporary_directory.name)
        self.database_path = self.temporary_path / "database" / "f7hub_test.db"
        self.migrations_dir = self.temporary_path / "migrations"

    def tearDown(self) -> None:
        self._temporary_directory.cleanup()

    def copy_production_migrations(self) -> tuple[Path, ...]:
        self.migrations_dir.mkdir()
        copied = []
        for production_migration in PRODUCTION_MIGRATIONS:
            copied_migration = self.migrations_dir / production_migration.name
            shutil.copyfile(production_migration, copied_migration)
            copied.append(copied_migration)
        return tuple(copied)

    def bootstrap_schema(self) -> None:
        self.copy_production_migrations()
        bootstrap_database(self.database_path, self.migrations_dir)

    def insert_category(self, connection: sqlite3.Connection) -> int:
        return int(
            connection.execute(
                """
                INSERT INTO categories (
                    scope, name, slug, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                ("KNOWLEDGE", "Knowledge", "knowledge", TIMESTAMP, TIMESTAMP),
            ).lastrowid
        )

    def insert_ticket(self, connection: sqlite3.Connection, number: str) -> int:
        return int(
            connection.execute(
                """
                INSERT INTO tickets (
                    ticket_number, subject, created_at, updated_at
                ) VALUES (?, ?, ?, ?)
                """,
                (number, f"Ticket {number}", TIMESTAMP, TIMESTAMP),
            ).lastrowid
        )

    def insert_tag(self, connection: sqlite3.Connection, slug: str) -> int:
        return int(
            connection.execute(
                "INSERT INTO tags (name, slug, created_at) VALUES (?, ?, ?)",
                (slug.title(), slug, TIMESTAMP),
            ).lastrowid
        )

    def insert_article(
        self,
        connection: sqlite3.Connection,
        code: str,
        *,
        title: str = "Knowledge article",
        category_id: int | None = None,
    ) -> int:
        return int(
            connection.execute(
                """
                INSERT INTO knowledge_articles (
                    article_code,
                    category_id,
                    title,
                    body_markdown,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (code, category_id, title, "# Body", TIMESTAMP, TIMESTAMP),
            ).lastrowid
        )

    def table_columns(
        self,
        connection: sqlite3.Connection,
        table_name: str,
    ) -> tuple[tuple[object, ...], ...]:
        rows = connection.execute(
            """
            SELECT name, type, "notnull", dflt_value, pk
            FROM pragma_table_info(?)
            ORDER BY cid
            """,
            (table_name,),
        ).fetchall()
        return tuple(tuple(row) for row in rows)

    def foreign_keys(
        self,
        connection: sqlite3.Connection,
        table_name: str,
    ) -> set[tuple[str, str, str, str]]:
        rows = connection.execute(
            """
            SELECT "table", "from", "to", on_delete
            FROM pragma_foreign_key_list(?)
            """,
            (table_name,),
        ).fetchall()
        return {tuple(row) for row in rows}

    def index_columns(
        self,
        connection: sqlite3.Connection,
        index_name: str,
    ) -> tuple[tuple[str, int, str], ...]:
        rows = connection.execute(
            """
            SELECT name, "desc", coll, key
            FROM pragma_index_xinfo(?)
            ORDER BY seqno
            """,
            (index_name,),
        ).fetchall()
        return tuple(
            (str(row[0]), int(row[1]), str(row[2]))
            for row in rows
            if row[3] == 1
        )

    def test_migration_chain_is_ordered_recorded_and_idempotent(self) -> None:
        copied_migrations = self.copy_production_migrations()

        migrations = discover_migrations(self.migrations_dir)
        first = bootstrap_database(self.database_path, self.migrations_dir)
        second = bootstrap_database(self.database_path, self.migrations_dir)

        with database_connection(self.database_path) as connection:
            records = list_applied_migrations(connection)

        self.assertEqual(
            tuple((migration.version, migration.name) for migration in migrations),
            (
                (1, "core"),
                (2, "taxonomy"),
                (3, "companies_contacts"),
                (4, "tickets"),
                (5, "knowledge"),
            ),
        )
        self.assertEqual(first.migration_result.applied_versions, (1, 2, 3, 4, 5))
        self.assertEqual(second.migration_result.applied_versions, ())
        self.assertEqual(tuple(record.version for record in records), (1, 2, 3, 4, 5))
        self.assertEqual(
            tuple(record.checksum_sha256 for record in records),
            tuple(
                hashlib.sha256(path.read_bytes()).hexdigest()
                for path in copied_migrations
            ),
        )

    def test_tables_foreign_keys_and_indexes_match_canonical_schema(self) -> None:
        self.bootstrap_schema()

        with database_connection(self.database_path) as connection:
            tables = {
                row[0]
                for row in connection.execute(
                    """
                    SELECT name FROM sqlite_master
                    WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                    """
                ).fetchall()
            }
            triggers = connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'trigger'"
            ).fetchall()
            columns = {
                table: self.table_columns(connection, table)
                for table in (
                    "knowledge_articles",
                    "knowledge_article_versions",
                    "knowledge_article_links",
                    "knowledge_article_relationships",
                    "ticket_knowledge_articles",
                    "knowledge_article_tags",
                )
            }
            foreign_keys = {
                table: self.foreign_keys(connection, table)
                for table in columns
            }
            explicit_indexes = {
                table: {
                    row[1]
                    for row in connection.execute(
                        "SELECT seq, name, \"unique\", origin, partial "
                        "FROM pragma_index_list(?)",
                        (table,),
                    ).fetchall()
                    if row[3] == "c"
                }
                for table in columns
            }
            index_columns = {
                name: self.index_columns(connection, name)
                for name in (
                    "idx_knowledge_articles_status_updated",
                    "idx_knowledge_articles_category_status",
                    "idx_knowledge_versions_article_version",
                    "idx_knowledge_links_article_sort",
                    "idx_knowledge_relationships_related_article",
                    "idx_ticket_knowledge_articles_article",
                    "idx_knowledge_article_tags_tag_id",
                )
            }

        self.assertTrue(
            {
                "knowledge_articles",
                "knowledge_article_versions",
                "knowledge_article_links",
                "knowledge_article_relationships",
                "ticket_knowledge_articles",
                "knowledge_article_tags",
            }.issubset(tables)
        )
        self.assertNotIn("knowledge_article_scripts", tables)
        self.assertNotIn("knowledge_articles_fts", tables)
        self.assertEqual(triggers, [])
        self.assertEqual(
            columns["knowledge_articles"],
            (
                ("knowledge_article_id", "INTEGER", 0, None, 1),
                ("article_code", "TEXT", 1, None, 0),
                ("category_id", "INTEGER", 0, None, 0),
                ("title", "TEXT", 1, None, 0),
                ("summary", "TEXT", 0, None, 0),
                ("body_markdown", "TEXT", 1, None, 0),
                ("status", "TEXT", 1, "'DRAFT'", 0),
                ("version_number", "INTEGER", 1, "1", 0),
                ("created_by", "TEXT", 0, None, 0),
                ("updated_by", "TEXT", 0, None, 0),
                ("created_at", "TEXT", 1, None, 0),
                ("updated_at", "TEXT", 1, None, 0),
                ("published_at", "TEXT", 0, None, 0),
            ),
        )
        self.assertEqual(
            columns["knowledge_article_versions"],
            (
                ("knowledge_article_version_id", "INTEGER", 0, None, 1),
                ("knowledge_article_id", "INTEGER", 1, None, 0),
                ("version_number", "INTEGER", 1, None, 0),
                ("title", "TEXT", 1, None, 0),
                ("summary", "TEXT", 0, None, 0),
                ("body_markdown", "TEXT", 1, None, 0),
                ("change_summary", "TEXT", 0, None, 0),
                ("created_by", "TEXT", 0, None, 0),
                ("created_at", "TEXT", 1, None, 0),
            ),
        )
        self.assertEqual(
            columns["knowledge_article_links"],
            (
                ("knowledge_article_link_id", "INTEGER", 0, None, 1),
                ("knowledge_article_id", "INTEGER", 1, None, 0),
                ("link_type", "TEXT", 0, None, 0),
                ("label", "TEXT", 1, None, 0),
                ("url", "TEXT", 1, None, 0),
                ("sort_order", "INTEGER", 1, "0", 0),
                ("created_at", "TEXT", 1, None, 0),
            ),
        )
        self.assertEqual(
            columns["knowledge_article_relationships"],
            (
                ("knowledge_article_relationship_id", "INTEGER", 0, None, 1),
                ("knowledge_article_id", "INTEGER", 1, None, 0),
                ("related_knowledge_article_id", "INTEGER", 1, None, 0),
                ("relationship_type", "TEXT", 1, None, 0),
                ("created_at", "TEXT", 1, None, 0),
            ),
        )
        self.assertEqual(
            columns["ticket_knowledge_articles"],
            (
                ("ticket_id", "INTEGER", 1, None, 1),
                ("knowledge_article_id", "INTEGER", 1, None, 2),
                ("relationship_type", "TEXT", 1, "'RELATED'", 3),
                ("linked_by", "TEXT", 0, None, 0),
                ("linked_at", "TEXT", 1, None, 0),
            ),
        )
        self.assertEqual(
            columns["knowledge_article_tags"],
            (
                ("knowledge_article_id", "INTEGER", 1, None, 1),
                ("tag_id", "INTEGER", 1, None, 2),
                ("created_at", "TEXT", 1, None, 0),
            ),
        )
        self.assertEqual(
            foreign_keys,
            {
                "knowledge_articles": {
                    ("categories", "category_id", "category_id", "SET NULL")
                },
                "knowledge_article_versions": {
                    (
                        "knowledge_articles",
                        "knowledge_article_id",
                        "knowledge_article_id",
                        "CASCADE",
                    )
                },
                "knowledge_article_links": {
                    (
                        "knowledge_articles",
                        "knowledge_article_id",
                        "knowledge_article_id",
                        "CASCADE",
                    )
                },
                "knowledge_article_relationships": {
                    (
                        "knowledge_articles",
                        "knowledge_article_id",
                        "knowledge_article_id",
                        "CASCADE",
                    ),
                    (
                        "knowledge_articles",
                        "related_knowledge_article_id",
                        "knowledge_article_id",
                        "CASCADE",
                    ),
                },
                "ticket_knowledge_articles": {
                    ("tickets", "ticket_id", "ticket_id", "CASCADE"),
                    (
                        "knowledge_articles",
                        "knowledge_article_id",
                        "knowledge_article_id",
                        "CASCADE",
                    ),
                },
                "knowledge_article_tags": {
                    (
                        "knowledge_articles",
                        "knowledge_article_id",
                        "knowledge_article_id",
                        "CASCADE",
                    ),
                    ("tags", "tag_id", "tag_id", "CASCADE"),
                },
            },
        )
        self.assertEqual(
            explicit_indexes,
            {
                "knowledge_articles": {
                    "idx_knowledge_articles_status_updated",
                    "idx_knowledge_articles_category_status",
                },
                "knowledge_article_versions": {
                    "idx_knowledge_versions_article_version"
                },
                "knowledge_article_links": {"idx_knowledge_links_article_sort"},
                "knowledge_article_relationships": {
                    "idx_knowledge_relationships_related_article"
                },
                "ticket_knowledge_articles": {
                    "idx_ticket_knowledge_articles_article"
                },
                "knowledge_article_tags": {"idx_knowledge_article_tags_tag_id"},
            },
        )
        self.assertEqual(
            index_columns,
            {
                "idx_knowledge_articles_status_updated": (
                    ("status", 0, "BINARY"),
                    ("updated_at", 1, "BINARY"),
                ),
                "idx_knowledge_articles_category_status": (
                    ("category_id", 0, "BINARY"),
                    ("status", 0, "BINARY"),
                ),
                "idx_knowledge_versions_article_version": (
                    ("knowledge_article_id", 0, "BINARY"),
                    ("version_number", 1, "BINARY"),
                ),
                "idx_knowledge_links_article_sort": (
                    ("knowledge_article_id", 0, "BINARY"),
                    ("sort_order", 0, "BINARY"),
                ),
                "idx_knowledge_relationships_related_article": (
                    ("related_knowledge_article_id", 0, "BINARY"),
                ),
                "idx_ticket_knowledge_articles_article": (
                    ("knowledge_article_id", 0, "BINARY"),
                    ("ticket_id", 0, "BINARY"),
                ),
                "idx_knowledge_article_tags_tag_id": (
                    ("tag_id", 0, "BINARY"),
                    ("knowledge_article_id", 0, "BINARY"),
                ),
            },
        )

    def test_article_constraints_defaults_and_category_delete_behavior(self) -> None:
        self.bootstrap_schema()

        with database_connection(self.database_path) as connection:
            category_id = self.insert_category(connection)
            article_id = self.insert_article(
                connection,
                "KB0001",
                category_id=category_id,
            )
            defaults = connection.execute(
                """
                SELECT status, version_number
                FROM knowledge_articles
                WHERE knowledge_article_id = ?
                """,
                (article_id,),
            ).fetchone()
            connection.execute(
                """
                INSERT INTO knowledge_articles (
                    article_code, title, body_markdown, status,
                    published_at, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                ("KB0002", "Published", "", "PUBLISHED", TIMESTAMP, TIMESTAMP, TIMESTAMP),
            )

            with self.assertRaises(sqlite3.IntegrityError):
                self.insert_article(connection, "kb0001", title="Duplicate code")

            invalid_rows = (
                (None, "Title", "Body", "DRAFT", 1, None),
                ("", "Title", "Body", "DRAFT", 1, None),
                ("   ", "Title", "Body", "DRAFT", 1, None),
                ("KB-A", None, "Body", "DRAFT", 1, None),
                ("KB-B", "", "Body", "DRAFT", 1, None),
                ("KB-C", "   ", "Body", "DRAFT", 1, None),
                ("KB-D", "Title", None, "DRAFT", 1, None),
                ("KB-E", "Title", "Body", "INVALID", 1, None),
                ("KB-F", "Title", "Body", "DRAFT", 0, None),
                ("KB-G", "Title", "Body", "DRAFT", 1, TIMESTAMP),
            )
            for row in invalid_rows:
                with self.subTest(row=row):
                    with self.assertRaises(sqlite3.IntegrityError):
                        connection.execute(
                            """
                            INSERT INTO knowledge_articles (
                                article_code, title, body_markdown, status,
                                version_number, published_at, created_at, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (*row, TIMESTAMP, TIMESTAMP),
                        )

            connection.execute(
                "DELETE FROM categories WHERE category_id = ?",
                (category_id,),
            )
            category_after_delete = connection.execute(
                """
                SELECT category_id FROM knowledge_articles
                WHERE knowledge_article_id = ?
                """,
                (article_id,),
            ).fetchone()[0]

        self.assertEqual(tuple(defaults), ("DRAFT", 1))
        self.assertIsNone(category_after_delete)

    def test_article_version_constraints_and_uniqueness(self) -> None:
        self.bootstrap_schema()

        with database_connection(self.database_path) as connection:
            article_id = self.insert_article(connection, "KB-VERSIONS")
            connection.execute(
                """
                INSERT INTO knowledge_article_versions (
                    knowledge_article_id, version_number, title,
                    body_markdown, created_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (article_id, 1, "Version 1", "Body", TIMESTAMP),
            )
            invalid_rows = (
                (article_id, 1, "Duplicate", "Body"),
                (article_id, 0, "Invalid version", "Body"),
                (article_id, 2, None, "Body"),
                (article_id, 2, "", "Body"),
                (article_id, 2, "   ", "Body"),
                (article_id, 2, "Title", None),
                (999_999, 1, "Missing article", "Body"),
            )
            for row in invalid_rows:
                with self.subTest(row=row):
                    with self.assertRaises(sqlite3.IntegrityError):
                        connection.execute(
                            """
                            INSERT INTO knowledge_article_versions (
                                knowledge_article_id, version_number, title,
                                body_markdown, created_at
                            ) VALUES (?, ?, ?, ?, ?)
                            """,
                            (*row, TIMESTAMP),
                        )

    def test_article_link_constraints_and_defaults(self) -> None:
        self.bootstrap_schema()

        with database_connection(self.database_path) as connection:
            article_id = self.insert_article(connection, "KB-LINKS")
            link_id = connection.execute(
                """
                INSERT INTO knowledge_article_links (
                    knowledge_article_id, label, url, created_at
                ) VALUES (?, ?, ?, ?)
                """,
                (article_id, "Portal", "not-url-validated", TIMESTAMP),
            ).lastrowid
            default_sort = connection.execute(
                """
                SELECT sort_order FROM knowledge_article_links
                WHERE knowledge_article_link_id = ?
                """,
                (link_id,),
            ).fetchone()[0]
            invalid_rows = (
                (999_999, "Label", "value"),
                (article_id, None, "value"),
                (article_id, "", "value"),
                (article_id, "   ", "value"),
                (article_id, "Label", None),
                (article_id, "Label", ""),
                (article_id, "Label", "   "),
            )
            for row in invalid_rows:
                with self.subTest(row=row):
                    with self.assertRaises(sqlite3.IntegrityError):
                        connection.execute(
                            """
                            INSERT INTO knowledge_article_links (
                                knowledge_article_id, label, url, created_at
                            ) VALUES (?, ?, ?, ?)
                            """,
                            (*row, TIMESTAMP),
                        )

        self.assertEqual(default_sort, 0)

    def test_article_relationship_constraints(self) -> None:
        self.bootstrap_schema()

        with database_connection(self.database_path) as connection:
            first_id = self.insert_article(connection, "KB-REL-1")
            second_id = self.insert_article(connection, "KB-REL-2")
            for relationship_type in (
                "RELATED",
                "PREREQUISITE",
                "SUPERSEDES",
                "DUPLICATES",
            ):
                connection.execute(
                    """
                    INSERT INTO knowledge_article_relationships (
                        knowledge_article_id,
                        related_knowledge_article_id,
                        relationship_type,
                        created_at
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (first_id, second_id, relationship_type, TIMESTAMP),
                )
            invalid_rows = (
                (first_id, first_id, "RELATED"),
                (first_id, second_id, "INVALID"),
                (first_id, second_id, "RELATED"),
                (999_999, second_id, "RELATED"),
                (first_id, 999_999, "RELATED"),
            )
            for row in invalid_rows:
                with self.subTest(row=row):
                    with self.assertRaises(sqlite3.IntegrityError):
                        connection.execute(
                            """
                            INSERT INTO knowledge_article_relationships (
                                knowledge_article_id,
                                related_knowledge_article_id,
                                relationship_type,
                                created_at
                            ) VALUES (?, ?, ?, ?)
                            """,
                            (*row, TIMESTAMP),
                        )

    def test_ticket_article_relationship_constraints_and_cascade(self) -> None:
        self.bootstrap_schema()

        with database_connection(self.database_path) as connection:
            ticket_id = self.insert_ticket(connection, "T-KB-1")
            article_id = self.insert_article(connection, "KB-TICKET")
            connection.execute(
                """
                INSERT INTO ticket_knowledge_articles (
                    ticket_id, knowledge_article_id, linked_at
                ) VALUES (?, ?, ?)
                """,
                (ticket_id, article_id, TIMESTAMP),
            )
            default_type = connection.execute(
                "SELECT relationship_type FROM ticket_knowledge_articles"
            ).fetchone()[0]
            for relationship_type in ("APPLIED", "RESOLUTION_SOURCE"):
                connection.execute(
                    """
                    INSERT INTO ticket_knowledge_articles (
                        ticket_id, knowledge_article_id,
                        relationship_type, linked_at
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (ticket_id, article_id, relationship_type, TIMESTAMP),
                )
            invalid_rows = (
                (ticket_id, article_id, "RELATED"),
                (ticket_id, article_id, "INVALID"),
                (999_999, article_id, "RELATED"),
                (ticket_id, 999_999, "RELATED"),
            )
            for row in invalid_rows:
                with self.subTest(row=row):
                    with self.assertRaises(sqlite3.IntegrityError):
                        connection.execute(
                            """
                            INSERT INTO ticket_knowledge_articles (
                                ticket_id, knowledge_article_id,
                                relationship_type, linked_at
                            ) VALUES (?, ?, ?, ?)
                            """,
                            (*row, TIMESTAMP),
                        )
            connection.execute("DELETE FROM tickets WHERE ticket_id = ?", (ticket_id,))
            remaining = connection.execute(
                "SELECT COUNT(*) FROM ticket_knowledge_articles"
            ).fetchone()[0]

        self.assertEqual(default_type, "RELATED")
        self.assertEqual(remaining, 0)

    def test_article_tag_constraints_and_tag_delete_cascade(self) -> None:
        self.bootstrap_schema()

        with database_connection(self.database_path) as connection:
            article_id = self.insert_article(connection, "KB-TAG")
            tag_id = self.insert_tag(connection, "network")
            connection.execute(
                """
                INSERT INTO knowledge_article_tags (
                    knowledge_article_id, tag_id, created_at
                ) VALUES (?, ?, ?)
                """,
                (article_id, tag_id, TIMESTAMP),
            )
            for row in (
                (article_id, tag_id),
                (999_999, tag_id),
                (article_id, 999_999),
            ):
                with self.subTest(row=row):
                    with self.assertRaises(sqlite3.IntegrityError):
                        connection.execute(
                            """
                            INSERT INTO knowledge_article_tags (
                                knowledge_article_id, tag_id, created_at
                            ) VALUES (?, ?, ?)
                            """,
                            (*row, TIMESTAMP),
                        )
            connection.execute("DELETE FROM tags WHERE tag_id = ?", (tag_id,))
            remaining = connection.execute(
                "SELECT COUNT(*) FROM knowledge_article_tags"
            ).fetchone()[0]

        self.assertEqual(remaining, 0)

    def test_article_delete_cascades_owned_knowledge_rows(self) -> None:
        self.bootstrap_schema()

        with database_connection(self.database_path) as connection:
            article_id = self.insert_article(connection, "KB-CASCADE")
            related_id = self.insert_article(connection, "KB-CASCADE-RELATED")
            ticket_id = self.insert_ticket(connection, "T-KB-CASCADE")
            tag_id = self.insert_tag(connection, "cascade")
            connection.execute(
                """
                INSERT INTO knowledge_article_versions (
                    knowledge_article_id, version_number, title,
                    body_markdown, created_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (article_id, 1, "Version", "Body", TIMESTAMP),
            )
            connection.execute(
                """
                INSERT INTO knowledge_article_links (
                    knowledge_article_id, label, url, created_at
                ) VALUES (?, ?, ?, ?)
                """,
                (article_id, "Link", "value", TIMESTAMP),
            )
            connection.execute(
                """
                INSERT INTO knowledge_article_relationships (
                    knowledge_article_id, related_knowledge_article_id,
                    relationship_type, created_at
                ) VALUES (?, ?, ?, ?)
                """,
                (related_id, article_id, "RELATED", TIMESTAMP),
            )
            connection.execute(
                """
                INSERT INTO ticket_knowledge_articles (
                    ticket_id, knowledge_article_id, linked_at
                ) VALUES (?, ?, ?)
                """,
                (ticket_id, article_id, TIMESTAMP),
            )
            connection.execute(
                """
                INSERT INTO knowledge_article_tags (
                    knowledge_article_id, tag_id, created_at
                ) VALUES (?, ?, ?)
                """,
                (article_id, tag_id, TIMESTAMP),
            )

            connection.execute(
                "DELETE FROM knowledge_articles WHERE knowledge_article_id = ?",
                (article_id,),
            )
            remaining = tuple(
                connection.execute(statement).fetchone()[0]
                for statement in (
                    "SELECT COUNT(*) FROM knowledge_article_versions",
                    "SELECT COUNT(*) FROM knowledge_article_links",
                    "SELECT COUNT(*) FROM knowledge_article_relationships",
                    "SELECT COUNT(*) FROM ticket_knowledge_articles",
                    "SELECT COUNT(*) FROM knowledge_article_tags",
                )
            )

        self.assertEqual(remaining, (0, 0, 0, 0, 0))

    def test_integrity_after_knowledge_inserts(self) -> None:
        self.bootstrap_schema()

        with database_connection(self.database_path) as connection:
            category_id = self.insert_category(connection)
            self.insert_article(connection, "KB-INTEGRITY", category_id=category_id)
            self.assertEqual(run_integrity_check(connection), ("ok",))
            self.assertEqual(run_foreign_key_check(connection), ())

    def test_failed_migration_rolls_back_knowledge_schema_only(self) -> None:
        copied = self.copy_production_migrations()
        copied_knowledge = copied[-1]
        copied_knowledge.write_text(
            copied_knowledge.read_text(encoding="utf-8")
            + """
            CREATE TABLE partial_knowledge_state (value TEXT NOT NULL);
            INSERT INTO partial_knowledge_state (value) VALUES ('temporary');
            THIS IS NOT VALID SQL;
            """,
            encoding="utf-8",
        )

        with self.assertRaises(MigrationApplicationError):
            bootstrap_database(self.database_path, self.migrations_dir)

        with database_connection(self.database_path) as connection:
            knowledge_table_count = connection.execute(
                """
                SELECT COUNT(*) FROM sqlite_master
                WHERE type = 'table'
                  AND (
                      name LIKE 'knowledge_%'
                      OR name = 'ticket_knowledge_articles'
                      OR name = 'partial_knowledge_state'
                  )
                """
            ).fetchone()[0]
            records = list_applied_migrations(connection)
            integrity = run_integrity_check(connection)
            foreign_keys = run_foreign_key_check(connection)

        self.assertEqual(knowledge_table_count, 0)
        self.assertEqual(tuple(record.version for record in records), (1, 2, 3, 4))
        self.assertEqual(integrity, ("ok",))
        self.assertEqual(foreign_keys, ())


if __name__ == "__main__":
    unittest.main()
