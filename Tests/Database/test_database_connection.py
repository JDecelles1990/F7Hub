from __future__ import annotations

from pathlib import Path
import sqlite3
import tempfile
import unittest

from f7hub.infrastructure.database import (
    DatabaseConfigurationError,
    database_connection,
    open_database,
)


class DatabaseConnectionTests(unittest.TestCase):
    def test_open_database_creates_temporary_database(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "nested" / "test.db"

            connection = open_database(database_path)
            try:
                self.assertTrue(database_path.is_file())
            finally:
                connection.close()

    def test_open_database_enables_foreign_keys(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "test.db"

            with database_connection(database_path) as connection:
                foreign_keys_enabled = connection.execute(
                    "PRAGMA foreign_keys"
                ).fetchone()[0]

            self.assertEqual(foreign_keys_enabled, 1)

    def test_open_database_sets_busy_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "test.db"

            with database_connection(
                database_path,
                busy_timeout_ms=1_234,
            ) as connection:
                busy_timeout_ms = connection.execute(
                    "PRAGMA busy_timeout"
                ).fetchone()[0]

            self.assertEqual(busy_timeout_ms, 1_234)

    def test_database_connection_closes_connection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "test.db"

            with database_connection(database_path) as connection:
                connection.execute("SELECT 1")

            with self.assertRaises(sqlite3.ProgrammingError):
                connection.execute("SELECT 1")

    def test_database_connection_rolls_back_unfinished_transaction(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "test.db"

            with database_connection(database_path) as connection:
                connection.execute("CREATE TABLE values_table (value TEXT NOT NULL)")
                connection.execute("BEGIN")
                connection.execute(
                    "INSERT INTO values_table (value) VALUES (?)",
                    ("not committed",),
                )

            with database_connection(database_path) as verification_connection:
                value_count = verification_connection.execute(
                    "SELECT COUNT(*) FROM values_table"
                ).fetchone()[0]

            self.assertEqual(value_count, 0)

    def test_open_database_rejects_invalid_busy_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "test.db"

            with self.assertRaises(DatabaseConfigurationError):
                open_database(database_path, busy_timeout_ms=-1)


if __name__ == "__main__":
    unittest.main()

