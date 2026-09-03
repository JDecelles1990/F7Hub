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
PRODUCTION_MIGRATIONS = (
    PROJECT_ROOT / "Database" / "Migrations" / "0001_core.sql",
    PROJECT_ROOT / "Database" / "Migrations" / "0002_taxonomy.sql",
)
TIMESTAMP = "2026-09-03T00:00:00.000Z"
ALLOWED_SCOPES = (
    "GENERAL",
    "TICKET",
    "KNOWLEDGE",
    "SCRIPT",
    "PROMPT",
    "CLIPBOARD",
    "DIAGNOSTIC",
)


class TaxonomyMigrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.temporary_path = Path(self._temporary_directory.name)
        self.database_path = self.temporary_path / "database" / "f7hub_test.db"
        self.migrations_dir = self.temporary_path / "migrations"

    def tearDown(self) -> None:
        self._temporary_directory.cleanup()

    def copy_production_migrations(self) -> tuple[Path, Path]:
        self.migrations_dir.mkdir()
        copied_migrations = []
        for production_migration in PRODUCTION_MIGRATIONS:
            copied_migration = self.migrations_dir / production_migration.name
            shutil.copyfile(production_migration, copied_migration)
            copied_migrations.append(copied_migration)
        return tuple(copied_migrations)

    def bootstrap_taxonomy(self) -> None:
        self.copy_production_migrations()
        bootstrap_database(self.database_path, self.migrations_dir)

    def insert_category(
        self,
        connection: sqlite3.Connection,
        *,
        scope: str | None,
        name: str | None,
        slug: str | None,
        parent_category_id: int | None = None,
    ) -> int:
        cursor = connection.execute(
            """
            INSERT INTO categories (
                scope,
                name,
                slug,
                parent_category_id,
                created_at,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (scope, name, slug, parent_category_id, TIMESTAMP, TIMESTAMP),
        )
        return int(cursor.lastrowid)

    def test_migration_chain_is_ordered_recorded_and_idempotent(self) -> None:
        copied_migrations = self.copy_production_migrations()

        migrations = discover_migrations(self.migrations_dir)
        first_result = bootstrap_database(self.database_path, self.migrations_dir)
        second_result = bootstrap_database(self.database_path, self.migrations_dir)

        with database_connection(self.database_path) as connection:
            records = list_applied_migrations(connection)

        expected_checksums = tuple(
            hashlib.sha256(path.read_bytes()).hexdigest()
            for path in copied_migrations
        )
        self.assertEqual(
            tuple((migration.version, migration.name) for migration in migrations),
            ((1, "core"), (2, "taxonomy")),
        )
        self.assertEqual(first_result.migration_result.discovered_versions, (1, 2))
        self.assertEqual(first_result.migration_result.applied_versions, (1, 2))
        self.assertEqual(second_result.migration_result.applied_versions, ())
        self.assertEqual(
            tuple((record.version, record.name) for record in records),
            ((1, "core"), (2, "taxonomy")),
        )
        self.assertEqual(
            tuple(record.checksum_sha256 for record in records),
            expected_checksums,
        )

    def test_taxonomy_tables_foreign_key_and_indexes_match_schema(self) -> None:
        self.bootstrap_taxonomy()

        with database_connection(self.database_path) as connection:
            tables = {
                row[0]
                for row in connection.execute(
                    """
                    SELECT name
                    FROM sqlite_master
                    WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                    """
                ).fetchall()
            }
            category_columns = tuple(
                (row[1], row[2], row[3], row[4], row[5])
                for row in connection.execute(
                    "PRAGMA table_info(categories)"
                ).fetchall()
            )
            tag_columns = tuple(
                (row[1], row[2], row[3], row[4], row[5])
                for row in connection.execute("PRAGMA table_info(tags)").fetchall()
            )
            category_foreign_keys = tuple(
                (row[2], row[3], row[4], row[6])
                for row in connection.execute(
                    "PRAGMA foreign_key_list(categories)"
                ).fetchall()
            )
            category_indexes = {
                row[1]: (row[2], row[3])
                for row in connection.execute(
                    "PRAGMA index_list(categories)"
                ).fetchall()
            }
            parent_index_columns = tuple(
                row[2]
                for row in connection.execute(
                    "PRAGMA index_info(idx_categories_parent_category_id)"
                ).fetchall()
            )
            scope_index_columns = tuple(
                row[2]
                for row in connection.execute(
                    "PRAGMA index_info(idx_categories_scope_active_sort)"
                ).fetchall()
            )
            tag_indexes = connection.execute("PRAGMA index_list(tags)").fetchall()
            explicit_tag_indexes = {row[1] for row in tag_indexes if row[3] == "c"}
            unique_tag_columns = {
                tuple(
                    index_row[2]
                    for index_row in connection.execute(
                        "SELECT seqno, cid, name FROM pragma_index_info(?) "
                        "ORDER BY seqno",
                        (row[1],),
                    ).fetchall()
                )
                for row in tag_indexes
                if row[2] == 1
            }

        self.assertEqual(
            tables,
            {"schema_migrations", "application_metadata", "categories", "tags"},
        )
        self.assertEqual(
            category_columns,
            (
                ("category_id", "INTEGER", 0, None, 1),
                ("scope", "TEXT", 1, None, 0),
                ("name", "TEXT", 1, None, 0),
                ("slug", "TEXT", 1, None, 0),
                ("parent_category_id", "INTEGER", 0, None, 0),
                ("description", "TEXT", 0, None, 0),
                ("is_active", "INTEGER", 1, "1", 0),
                ("sort_order", "INTEGER", 1, "0", 0),
                ("created_at", "TEXT", 1, None, 0),
                ("updated_at", "TEXT", 1, None, 0),
            ),
        )
        self.assertEqual(
            tag_columns,
            (
                ("tag_id", "INTEGER", 0, None, 1),
                ("name", "TEXT", 1, None, 0),
                ("slug", "TEXT", 1, None, 0),
                ("description", "TEXT", 0, None, 0),
                ("created_at", "TEXT", 1, None, 0),
            ),
        )
        self.assertEqual(
            category_foreign_keys,
            (("categories", "parent_category_id", "category_id", "SET NULL"),),
        )
        self.assertEqual(
            category_indexes["idx_categories_parent_category_id"],
            (0, "c"),
        )
        self.assertEqual(
            category_indexes["idx_categories_scope_active_sort"],
            (0, "c"),
        )
        self.assertEqual(parent_index_columns, ("parent_category_id",))
        self.assertEqual(
            scope_index_columns,
            ("scope", "is_active", "sort_order"),
        )
        self.assertEqual(explicit_tag_indexes, set())
        self.assertEqual(unique_tag_columns, {("name",), ("slug",)})

    def test_category_scope_accepts_only_canonical_values(self) -> None:
        self.bootstrap_taxonomy()

        with database_connection(self.database_path) as connection:
            for scope in ALLOWED_SCOPES:
                with self.subTest(scope=scope):
                    self.insert_category(
                        connection,
                        scope=scope,
                        name=f"{scope} category",
                        slug=scope.lower(),
                    )

            for invalid_scope in (None, "COMPANY", "general", ""):
                with self.subTest(scope=invalid_scope):
                    with self.assertRaises(sqlite3.IntegrityError):
                        self.insert_category(
                            connection,
                            scope=invalid_scope,
                            name="Invalid scope",
                            slug=f"invalid-{invalid_scope}",
                        )

    def test_category_name_and_slug_constraints_use_nocase(self) -> None:
        self.bootstrap_taxonomy()

        with database_connection(self.database_path) as connection:
            self.insert_category(
                connection,
                scope="GENERAL",
                name="VPN",
                slug="vpn",
            )
            self.insert_category(
                connection,
                scope="TICKET",
                name="VPN",
                slug="ticket-vpn",
            )
            case_insensitive_name_matches = connection.execute(
                "SELECT COUNT(*) FROM categories WHERE name = ?",
                ("vpn",),
            ).fetchone()[0]

            for index, invalid_name in enumerate((None, "", "   ")):
                with self.subTest(name=invalid_name):
                    with self.assertRaises(sqlite3.IntegrityError):
                        self.insert_category(
                            connection,
                            scope="GENERAL",
                            name=invalid_name,
                            slug=f"invalid-name-{index}",
                        )

            for index, invalid_slug in enumerate((None, "", "   ")):
                with self.subTest(slug=invalid_slug):
                    with self.assertRaises(sqlite3.IntegrityError):
                        self.insert_category(
                            connection,
                            scope="GENERAL",
                            name=f"Invalid slug {index}",
                            slug=invalid_slug,
                        )

            for duplicate_slug in ("vpn", "VPN"):
                with self.subTest(slug=duplicate_slug):
                    with self.assertRaises(sqlite3.IntegrityError):
                        self.insert_category(
                            connection,
                            scope="GENERAL",
                            name=f"Duplicate {duplicate_slug}",
                            slug=duplicate_slug,
                        )

        self.assertEqual(case_insensitive_name_matches, 2)

    def test_category_parent_constraints_and_delete_behavior(self) -> None:
        self.bootstrap_taxonomy()

        with database_connection(self.database_path) as connection:
            parent_id = self.insert_category(
                connection,
                scope="GENERAL",
                name="Parent",
                slug="parent",
            )
            child_id = self.insert_category(
                connection,
                scope="GENERAL",
                name="Child",
                slug="child",
                parent_category_id=parent_id,
            )

            with self.assertRaises(sqlite3.IntegrityError):
                self.insert_category(
                    connection,
                    scope="GENERAL",
                    name="Missing parent",
                    slug="missing-parent",
                    parent_category_id=999_999,
                )

            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    """
                    INSERT INTO categories (
                        category_id,
                        scope,
                        name,
                        slug,
                        parent_category_id,
                        created_at,
                        updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (999, "GENERAL", "Self", "self", 999, TIMESTAMP, TIMESTAMP),
                )

            connection.execute(
                "DELETE FROM categories WHERE category_id = ?",
                (parent_id,),
            )
            child_parent = connection.execute(
                "SELECT parent_category_id FROM categories WHERE category_id = ?",
                (child_id,),
            ).fetchone()[0]

        self.assertIsNone(child_parent)

    def test_category_active_flag_and_sort_order_match_documented_rules(self) -> None:
        self.bootstrap_taxonomy()

        with database_connection(self.database_path) as connection:
            default_id = self.insert_category(
                connection,
                scope="GENERAL",
                name="Defaults",
                slug="defaults",
            )
            defaults = connection.execute(
                """
                SELECT is_active, sort_order
                FROM categories
                WHERE category_id = ?
                """,
                (default_id,),
            ).fetchone()

            for index, active_value in enumerate((0, 1)):
                with self.subTest(active=active_value):
                    connection.execute(
                        """
                        INSERT INTO categories (
                            scope,
                            name,
                            slug,
                            is_active,
                            sort_order,
                            created_at,
                            updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            "GENERAL",
                            f"Active {active_value}",
                            f"active-{index}",
                            active_value,
                            -10,
                            TIMESTAMP,
                            TIMESTAMP,
                        ),
                    )

            for invalid_value in (-1, 2, 99):
                with self.subTest(active=invalid_value):
                    with self.assertRaises(sqlite3.IntegrityError):
                        connection.execute(
                            """
                            INSERT INTO categories (
                                scope,
                                name,
                                slug,
                                is_active,
                                created_at,
                                updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?)
                            """,
                            (
                                "GENERAL",
                                f"Invalid {invalid_value}",
                                f"invalid-active-{invalid_value}",
                                invalid_value,
                                TIMESTAMP,
                                TIMESTAMP,
                            ),
                        )

        self.assertEqual(tuple(defaults), (1, 0))

    def test_tag_name_constraints_and_case_insensitive_uniqueness(self) -> None:
        self.bootstrap_taxonomy()

        with database_connection(self.database_path) as connection:
            connection.execute(
                "INSERT INTO tags (name, slug, created_at) VALUES (?, ?, ?)",
                ("Networking", "networking", TIMESTAMP),
            )

            for index, invalid_name in enumerate((None, "", "   ")):
                with self.subTest(name=invalid_name):
                    with self.assertRaises(sqlite3.IntegrityError):
                        connection.execute(
                            """
                            INSERT INTO tags (name, slug, created_at)
                            VALUES (?, ?, ?)
                            """,
                            (invalid_name, f"invalid-name-{index}", TIMESTAMP),
                        )

            for index, duplicate_name in enumerate(("Networking", "NETWORKING")):
                with self.subTest(name=duplicate_name):
                    with self.assertRaises(sqlite3.IntegrityError):
                        connection.execute(
                            """
                            INSERT INTO tags (name, slug, created_at)
                            VALUES (?, ?, ?)
                            """,
                            (duplicate_name, f"duplicate-name-{index}", TIMESTAMP),
                        )

    def test_tag_slug_constraints_and_case_insensitive_uniqueness(self) -> None:
        self.bootstrap_taxonomy()

        with database_connection(self.database_path) as connection:
            connection.execute(
                "INSERT INTO tags (name, slug, created_at) VALUES (?, ?, ?)",
                ("Virtual Private Network", "vpn", TIMESTAMP),
            )

            for index, invalid_slug in enumerate((None, "", "   ")):
                with self.subTest(slug=invalid_slug):
                    with self.assertRaises(sqlite3.IntegrityError):
                        connection.execute(
                            """
                            INSERT INTO tags (name, slug, created_at)
                            VALUES (?, ?, ?)
                            """,
                            (f"Invalid slug {index}", invalid_slug, TIMESTAMP),
                        )

            for index, duplicate_slug in enumerate(("vpn", "VPN")):
                with self.subTest(slug=duplicate_slug):
                    with self.assertRaises(sqlite3.IntegrityError):
                        connection.execute(
                            """
                            INSERT INTO tags (name, slug, created_at)
                            VALUES (?, ?, ?)
                            """,
                            (f"Duplicate slug {index}", duplicate_slug, TIMESTAMP),
                        )

    def test_failed_taxonomy_migration_rolls_back_only_taxonomy(self) -> None:
        _, copied_taxonomy = self.copy_production_migrations()
        copied_taxonomy.write_text(
            copied_taxonomy.read_text(encoding="utf-8")
            + """
            CREATE TABLE partial_taxonomy_state (value TEXT NOT NULL);
            INSERT INTO partial_taxonomy_state (value) VALUES ('temporary');
            THIS IS NOT VALID SQL;
            """,
            encoding="utf-8",
        )

        with self.assertRaises(MigrationApplicationError):
            bootstrap_database(self.database_path, self.migrations_dir)

        with database_connection(self.database_path) as connection:
            tables = {
                row[0]
                for row in connection.execute(
                    """
                    SELECT name
                    FROM sqlite_master
                    WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                    """
                ).fetchall()
            }
            records = list_applied_migrations(connection)
            integrity_results = run_integrity_check(connection)
            foreign_key_violations = run_foreign_key_check(connection)

        self.assertEqual(tables, {"schema_migrations", "application_metadata"})
        self.assertEqual(
            tuple((record.version, record.name) for record in records),
            ((1, "core"),),
        )
        self.assertEqual(integrity_results, ("ok",))
        self.assertEqual(foreign_key_violations, ())


if __name__ == "__main__":
    unittest.main()
