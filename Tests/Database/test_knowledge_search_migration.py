from __future__ import annotations

import hashlib
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest

from f7hub.infrastructure.database import bootstrap_database, database_connection
from f7hub.infrastructure.migrations import MigrationApplicationError, list_applied_migrations


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PRODUCTION_MIGRATIONS = PROJECT_ROOT / "Database" / "Migrations"
TIMESTAMP = "2026-09-09T12:00:00.000Z"
EXISTING_MIGRATION_HASHES = {
    "0001_core.sql": "84596d21bbae32c05cf92cb3512674eb5e598d3400210af6b67871aac71931da",
    "0002_taxonomy.sql": "46d3f6383e0463ee4130449d23ee87144012e972ac7c6c55c65018e2f5ac1864",
    "0003_companies_contacts.sql": "6a6b01f2cc0be0855e6ae1794ee4db8a1518c0fb6d0cdeb40b7a3c51a2d16a24",
    "0004_tickets.sql": "7168f94abe6fd03429475f87c4851344653bb917a7b5838cabbcc3a9acf282d9",
    "0005_knowledge.sql": "7e976210c37c7c6d46b1dae24c88e578b259449a02d1c58e48f9e9b53c354572",
}


class KnowledgeSearchMigrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.temporary_path = Path(self._temporary_directory.name)
        self.database_path = self.temporary_path / "database" / "knowledge-search.db"
        self.migrations_dir = self.temporary_path / "migrations"
        self.migrations_dir.mkdir()

    def tearDown(self) -> None:
        self._temporary_directory.cleanup()

    def copy_migrations(self, through: int = 6) -> None:
        for version in range(1, through + 1):
            source = next(PRODUCTION_MIGRATIONS.glob(f"{version:04d}_*.sql"))
            destination = self.migrations_dir / source.name
            if not destination.exists():
                shutil.copyfile(source, destination)

    @staticmethod
    def insert_article(
        connection: sqlite3.Connection,
        code: str,
        *,
        title: str = "Knowledge article",
        summary: str | None = "Synthetic summary",
        body: str = "Synthetic body",
        status: str = "DRAFT",
    ) -> int:
        return int(
            connection.execute(
                """
                INSERT INTO knowledge_articles (
                    article_code, title, summary, body_markdown, status,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (code, title, summary, body, status, TIMESTAMP, TIMESTAMP),
            ).lastrowid
        )

    @staticmethod
    def search_ids(
        connection: sqlite3.Connection, expression: str,
    ) -> tuple[int, ...]:
        return tuple(
            int(row[0])
            for row in connection.execute(
                "SELECT rowid FROM knowledge_articles_fts "
                "WHERE knowledge_articles_fts MATCH ? ORDER BY rowid",
                (expression,),
            )
        )

    def test_sequence_history_checksums_idempotency_and_schema_contract(self) -> None:
        self.copy_migrations()
        first = bootstrap_database(self.database_path, self.migrations_dir)
        second = bootstrap_database(self.database_path, self.migrations_dir)

        self.assertEqual(first.migration_result.discovered_versions, (1, 2, 3, 4, 5, 6))
        self.assertEqual(first.migration_result.applied_versions, (1, 2, 3, 4, 5, 6))
        self.assertEqual(second.migration_result.applied_versions, ())
        for filename, expected_hash in EXISTING_MIGRATION_HASHES.items():
            actual = hashlib.sha256((PRODUCTION_MIGRATIONS / filename).read_bytes()).hexdigest()
            self.assertEqual(actual, expected_hash, filename)

        with database_connection(self.database_path) as connection:
            migrations = list_applied_migrations(connection)
            objects = {
                (str(row[0]), str(row[1]))
                for row in connection.execute(
                    "SELECT name, type FROM sqlite_master "
                    "WHERE name LIKE 'knowledge_articles_fts%' "
                    "OR name IN ('knowledge_articles_ai', 'knowledge_articles_ad', 'knowledge_articles_au')"
                )
            }
            columns = tuple(
                str(row[1])
                for row in connection.execute("PRAGMA table_info(knowledge_articles_fts)")
            )
            create_sql = str(
                connection.execute(
                    "SELECT sql FROM sqlite_master WHERE name = 'knowledge_articles_fts'"
                ).fetchone()[0]
            ).lower()
            update_trigger_sql = str(
                connection.execute(
                    "SELECT sql FROM sqlite_master WHERE name = 'knowledge_articles_au'"
                ).fetchone()[0]
            ).lower()

        self.assertEqual(tuple(record.version for record in migrations), (1, 2, 3, 4, 5, 6))
        self.assertEqual(migrations[-1].name, "knowledge_search")
        self.assertEqual(columns, ("article_code", "title", "summary", "body_markdown"))
        self.assertIn("content = 'knowledge_articles'", create_sql)
        self.assertIn("content_rowid = 'knowledge_article_id'", create_sql)
        self.assertIn("tokenize = 'unicode61'", create_sql)
        self.assertIn(
            "after update of article_code, title, summary, body_markdown",
            " ".join(update_trigger_sql.split()),
        )
        self.assertEqual(
            objects,
            {
                ("knowledge_articles_fts", "table"),
                ("knowledge_articles_fts_data", "table"),
                ("knowledge_articles_fts_idx", "table"),
                ("knowledge_articles_fts_docsize", "table"),
                ("knowledge_articles_fts_config", "table"),
                ("knowledge_articles_ai", "trigger"),
                ("knowledge_articles_ad", "trigger"),
                ("knowledge_articles_au", "trigger"),
            },
        )

    def test_existing_rows_are_backfilled_when_0006_is_applied(self) -> None:
        self.copy_migrations(5)
        bootstrap_database(self.database_path, self.migrations_dir)
        with database_connection(self.database_path) as connection:
            article_id = self.insert_article(
                connection,
                "KBBACKFILL",
                title="Existing Outlook article",
                body="Pre-migration searchable body",
            )

        self.copy_migrations(6)
        result = bootstrap_database(self.database_path, self.migrations_dir)
        with database_connection(self.database_path) as connection:
            self.assertEqual(self.search_ids(connection, '"Outlook"'), (article_id,))
            self.assertEqual(self.search_ids(connection, '"migration"'), (article_id,))
            self.assertEqual(self.search_ids(connection, '"KBBACKFILL"'), (article_id,))
        self.assertEqual(result.migration_result.applied_versions, (6,))

    def test_insert_update_delete_and_repeated_edits_stay_consistent(self) -> None:
        self.copy_migrations()
        bootstrap_database(self.database_path, self.migrations_dir)
        with database_connection(self.database_path) as connection:
            article_id = self.insert_article(
                connection,
                "KBOLD",
                title="Legacy title token",
                summary="Legacy summary token",
                body="Legacy body token",
            )
            self.assertEqual(self.search_ids(connection, '"Legacy"'), (article_id,))
            self.assertEqual(self.search_ids(connection, '"KBOLD"'), (article_id,))

            connection.execute(
                """
                UPDATE knowledge_articles
                SET article_code = ?, title = ?, summary = ?, body_markdown = ?
                WHERE knowledge_article_id = ?
                """,
                ("KBNEW", "Current title token", "Current summary token", "Current body token", article_id),
            )
            self.assertEqual(self.search_ids(connection, '"Legacy"'), ())
            self.assertEqual(self.search_ids(connection, '"KBOLD"'), ())
            self.assertEqual(self.search_ids(connection, '"Current"'), (article_id,))
            self.assertEqual(self.search_ids(connection, '"KBNEW"'), (article_id,))

            for body in ("Second edit token", "Final edit token"):
                connection.execute(
                    "UPDATE knowledge_articles SET body_markdown = ? "
                    "WHERE knowledge_article_id = ?",
                    (body, article_id),
                )
            self.assertEqual(self.search_ids(connection, '"Second"'), ())
            self.assertEqual(self.search_ids(connection, '"Final"'), (article_id,))
            self.assertEqual(
                connection.execute(
                    "SELECT count(*) FROM knowledge_articles_fts "
                    "WHERE knowledge_articles_fts MATCH ?",
                    ('"Final"',),
                ).fetchone()[0],
                1,
            )

            connection.execute(
                "INSERT INTO knowledge_articles_fts(knowledge_articles_fts, rank) "
                "VALUES ('integrity-check', 1)"
            )
            connection.execute(
                "DELETE FROM knowledge_articles WHERE knowledge_article_id = ?",
                (article_id,),
            )
            self.assertEqual(self.search_ids(connection, '"Final"'), ())
            connection.execute(
                "INSERT INTO knowledge_articles_fts(knowledge_articles_fts, rank) "
                "VALUES ('integrity-check', 1)"
            )
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])

    def test_failed_0006_rolls_back_schema_and_history_record(self) -> None:
        self.copy_migrations(5)
        bootstrap_database(self.database_path, self.migrations_dir)
        bad_migration = self.migrations_dir / "0006_knowledge_search.sql"
        bad_migration.write_text(
            (PRODUCTION_MIGRATIONS / "0006_knowledge_search.sql").read_text(
                encoding="utf-8"
            )
            + "\nSELECT * FROM table_that_does_not_exist;\n",
            encoding="utf-8",
        )

        with self.assertRaises(MigrationApplicationError):
            bootstrap_database(self.database_path, self.migrations_dir)

        with database_connection(self.database_path) as connection:
            self.assertEqual(
                connection.execute("SELECT count(*) FROM schema_migrations").fetchone()[0],
                5,
            )
            self.assertEqual(
                connection.execute(
                    "SELECT count(*) FROM sqlite_master "
                    "WHERE name LIKE 'knowledge_articles_fts%' "
                    "OR name IN ('knowledge_articles_ai', 'knowledge_articles_ad', "
                    "'knowledge_articles_au')"
                ).fetchone()[0],
                0,
            )
            self.assertIsNotNone(
                connection.execute(
                    "SELECT 1 FROM sqlite_master WHERE name = 'knowledge_articles'"
                ).fetchone()
            )

        shutil.copyfile(
            PRODUCTION_MIGRATIONS / "0006_knowledge_search.sql",
            bad_migration,
        )
        retry = bootstrap_database(self.database_path, self.migrations_dir)
        self.assertEqual(retry.migration_result.applied_versions, (6,))
        with database_connection(self.database_path) as connection:
            self.assertEqual(
                connection.execute(
                    "SELECT count(*) FROM schema_migrations WHERE version = 6"
                ).fetchone()[0],
                1,
            )
            self.assertEqual(
                connection.execute(
                    "SELECT count(*) FROM sqlite_master "
                    "WHERE name LIKE 'knowledge_articles_fts%' "
                    "OR name IN ('knowledge_articles_ai', 'knowledge_articles_ad', "
                    "'knowledge_articles_au')"
                ).fetchone()[0],
                8,
            )


if __name__ == "__main__":
    unittest.main()
