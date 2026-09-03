from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from f7hub.infrastructure.database import (
    DatabaseIntegrityError,
    database_connection,
    run_foreign_key_check,
    run_integrity_check,
    validate_database_integrity,
)


class DatabaseIntegrityTests(unittest.TestCase):
    def test_integrity_check_returns_ok(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "f7hub_test.db"

            with database_connection(database_path) as connection:
                integrity_results = run_integrity_check(connection)

            self.assertEqual(integrity_results, ("ok",))

    def test_foreign_key_check_returns_zero_violations(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "f7hub_test.db"

            with database_connection(database_path) as connection:
                connection.execute(
                    "CREATE TABLE parents (parent_id INTEGER PRIMARY KEY)"
                )
                connection.execute(
                    """
                    CREATE TABLE children (
                        child_id INTEGER PRIMARY KEY,
                        parent_id INTEGER NOT NULL,
                        FOREIGN KEY (parent_id) REFERENCES parents(parent_id)
                    )
                    """
                )
                connection.execute("INSERT INTO parents DEFAULT VALUES")
                connection.execute(
                    "INSERT INTO children (parent_id) VALUES (?)",
                    (1,),
                )
                violations = run_foreign_key_check(connection)

            self.assertEqual(violations, ())

    def test_integrity_validation_rejects_foreign_key_violation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "f7hub_test.db"

            with database_connection(database_path) as connection:
                connection.execute(
                    "CREATE TABLE parents (parent_id INTEGER PRIMARY KEY)"
                )
                connection.execute(
                    """
                    CREATE TABLE children (
                        child_id INTEGER PRIMARY KEY,
                        parent_id INTEGER NOT NULL,
                        FOREIGN KEY (parent_id) REFERENCES parents(parent_id)
                    )
                    """
                )
                connection.execute("PRAGMA foreign_keys = OFF")
                connection.execute(
                    "INSERT INTO children (parent_id) VALUES (?)",
                    (999,),
                )
                connection.execute("PRAGMA foreign_keys = ON")

                with self.assertRaises(DatabaseIntegrityError):
                    validate_database_integrity(connection)


if __name__ == "__main__":
    unittest.main()

