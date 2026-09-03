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
    PROJECT_ROOT / "Database" / "Migrations" / migration_name
    for migration_name in (
        "0001_core.sql",
        "0002_taxonomy.sql",
        "0003_companies_contacts.sql",
        "0004_tickets.sql",
    )
)
TIMESTAMP = "2026-09-03T00:00:00.000Z"


class TicketsMigrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.temporary_path = Path(self._temporary_directory.name)
        self.database_path = self.temporary_path / "database" / "f7hub_test.db"
        self.migrations_dir = self.temporary_path / "migrations"

    def tearDown(self) -> None:
        self._temporary_directory.cleanup()

    def copy_production_migrations(self) -> tuple[Path, ...]:
        self.migrations_dir.mkdir()
        copied_migrations = []
        for production_migration in PRODUCTION_MIGRATIONS:
            copied_migration = self.migrations_dir / production_migration.name
            shutil.copyfile(production_migration, copied_migration)
            copied_migrations.append(copied_migration)
        return tuple(copied_migrations)

    def bootstrap_schema(self) -> None:
        self.copy_production_migrations()
        bootstrap_database(self.database_path, self.migrations_dir)

    def insert_ticket(
        self,
        connection: sqlite3.Connection,
        *,
        ticket_number: str | None,
        subject: str | None = "Test ticket",
        ticket_type: str = "INCIDENT",
        status: str = "NEW",
        priority: str = "MEDIUM",
        company_id: int | None = None,
        contact_id: int | None = None,
        category_id: int | None = None,
        resolved_at: str | None = None,
        closed_at: str | None = None,
    ) -> int:
        cursor = connection.execute(
            """
            INSERT INTO tickets (
                ticket_number,
                ticket_type,
                status,
                priority,
                company_id,
                contact_id,
                category_id,
                subject,
                created_at,
                updated_at,
                resolved_at,
                closed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticket_number,
                ticket_type,
                status,
                priority,
                company_id,
                contact_id,
                category_id,
                subject,
                TIMESTAMP,
                TIMESTAMP,
                resolved_at,
                closed_at,
            ),
        )
        return int(cursor.lastrowid)

    def index_key_columns(
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
        first_result = bootstrap_database(self.database_path, self.migrations_dir)
        second_result = bootstrap_database(self.database_path, self.migrations_dir)

        with database_connection(self.database_path) as connection:
            records = list_applied_migrations(connection)

        expected_checksums = tuple(
            hashlib.sha256(path.read_bytes()).hexdigest()
            for path in copied_migrations
        )
        expected_history = (
            (1, "core"),
            (2, "taxonomy"),
            (3, "companies_contacts"),
            (4, "tickets"),
        )
        self.assertEqual(
            tuple((migration.version, migration.name) for migration in migrations),
            expected_history,
        )
        self.assertEqual(
            first_result.migration_result.discovered_versions,
            (1, 2, 3, 4),
        )
        self.assertEqual(
            first_result.migration_result.applied_versions,
            (1, 2, 3, 4),
        )
        self.assertEqual(second_result.migration_result.applied_versions, ())
        self.assertEqual(
            tuple((record.version, record.name) for record in records),
            expected_history,
        )
        self.assertEqual(
            tuple(record.checksum_sha256 for record in records),
            expected_checksums,
        )

    def test_tables_columns_foreign_keys_and_indexes_match_schema(self) -> None:
        self.bootstrap_schema()

        ticket_tables = (
            "tickets",
            "ticket_notes",
            "ticket_status_history",
            "ticket_timeline_events",
        )
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
            columns = {
                table_name: tuple(
                    (row[1], row[2], row[3], row[4], row[5])
                    for row in connection.execute(
                        """
                        SELECT cid, name, type, "notnull", dflt_value, pk
                        FROM pragma_table_info(?)
                        ORDER BY cid
                        """,
                        (table_name,),
                    ).fetchall()
                )
                for table_name in ticket_tables
            }
            foreign_keys = {
                table_name: {
                    (row[2], row[3], row[4], row[6])
                    for row in connection.execute(
                        """
                        SELECT id, seq, "table", "from", "to", on_update,
                               on_delete, match
                        FROM pragma_foreign_key_list(?)
                        """,
                        (table_name,),
                    ).fetchall()
                }
                for table_name in ticket_tables
            }
            explicit_indexes = {
                table_name: {
                    row[1]
                    for row in connection.execute(
                        "SELECT * FROM pragma_index_list(?)",
                        (table_name,),
                    ).fetchall()
                    if row[3] == "c"
                }
                for table_name in ticket_tables
            }
            index_columns = {
                index_name: self.index_key_columns(connection, index_name)
                for index_name in (
                    "idx_tickets_status_updated",
                    "idx_tickets_company_status",
                    "idx_tickets_contact_id",
                    "idx_tickets_priority_status",
                    "idx_tickets_category_id",
                    "idx_tickets_created_at",
                    "idx_ticket_notes_ticket_created",
                    "idx_ticket_status_history_ticket_changed",
                    "idx_ticket_timeline_ticket_occurred",
                )
            }

        self.assertTrue(set(ticket_tables).issubset(tables))
        self.assertEqual(
            columns["tickets"],
            (
                ("ticket_id", "INTEGER", 0, None, 1),
                ("ticket_number", "TEXT", 1, None, 0),
                ("ticket_type", "TEXT", 1, "'INCIDENT'", 0),
                ("status", "TEXT", 1, "'NEW'", 0),
                ("priority", "TEXT", 1, "'MEDIUM'", 0),
                ("company_id", "INTEGER", 0, None, 0),
                ("contact_id", "INTEGER", 0, None, 0),
                ("category_id", "INTEGER", 0, None, 0),
                ("subject", "TEXT", 1, None, 0),
                ("description", "TEXT", 0, None, 0),
                ("resolution", "TEXT", 0, None, 0),
                ("assigned_to", "TEXT", 0, None, 0),
                ("source", "TEXT", 0, None, 0),
                ("created_at", "TEXT", 1, None, 0),
                ("updated_at", "TEXT", 1, None, 0),
                ("resolved_at", "TEXT", 0, None, 0),
                ("closed_at", "TEXT", 0, None, 0),
            ),
        )
        self.assertEqual(
            tuple(column[0] for column in columns["ticket_notes"]),
            (
                "ticket_note_id",
                "ticket_id",
                "note_type",
                "note_text",
                "author_label",
                "source",
                "is_ai_generated",
                "created_at",
                "updated_at",
            ),
        )
        self.assertEqual(
            tuple(column[0] for column in columns["ticket_status_history"]),
            (
                "ticket_status_history_id",
                "ticket_id",
                "previous_status",
                "new_status",
                "reason",
                "changed_by",
                "changed_at",
            ),
        )
        self.assertEqual(
            tuple(column[0] for column in columns["ticket_timeline_events"]),
            (
                "ticket_timeline_event_id",
                "ticket_id",
                "event_type",
                "title",
                "details",
                "metadata_json",
                "actor_label",
                "occurred_at",
            ),
        )
        self.assertEqual(
            foreign_keys["tickets"],
            {
                ("companies", "company_id", "company_id", "SET NULL"),
                ("contacts", "contact_id", "contact_id", "SET NULL"),
                ("categories", "category_id", "category_id", "SET NULL"),
            },
        )
        for detail_table in ticket_tables[1:]:
            self.assertEqual(
                foreign_keys[detail_table],
                {("tickets", "ticket_id", "ticket_id", "CASCADE")},
            )
        self.assertEqual(
            explicit_indexes["tickets"],
            {
                "idx_tickets_status_updated",
                "idx_tickets_company_status",
                "idx_tickets_contact_id",
                "idx_tickets_priority_status",
                "idx_tickets_category_id",
                "idx_tickets_created_at",
            },
        )
        self.assertEqual(
            explicit_indexes["ticket_notes"],
            {"idx_ticket_notes_ticket_created"},
        )
        self.assertEqual(
            explicit_indexes["ticket_status_history"],
            {"idx_ticket_status_history_ticket_changed"},
        )
        self.assertEqual(
            explicit_indexes["ticket_timeline_events"],
            {"idx_ticket_timeline_ticket_occurred"},
        )
        self.assertEqual(
            index_columns["idx_tickets_status_updated"],
            (("status", 0, "BINARY"), ("updated_at", 1, "BINARY")),
        )
        self.assertEqual(
            index_columns["idx_tickets_company_status"],
            (("company_id", 0, "BINARY"), ("status", 0, "BINARY")),
        )
        self.assertEqual(
            index_columns["idx_tickets_contact_id"],
            (("contact_id", 0, "BINARY"),),
        )
        self.assertEqual(
            index_columns["idx_tickets_priority_status"],
            (("priority", 0, "BINARY"), ("status", 0, "BINARY")),
        )
        self.assertEqual(
            index_columns["idx_tickets_category_id"],
            (("category_id", 0, "BINARY"),),
        )
        self.assertEqual(
            index_columns["idx_tickets_created_at"],
            (("created_at", 1, "BINARY"),),
        )
        self.assertEqual(
            index_columns["idx_ticket_notes_ticket_created"],
            (("ticket_id", 0, "BINARY"), ("created_at", 1, "BINARY")),
        )
        self.assertEqual(
            index_columns["idx_ticket_status_history_ticket_changed"],
            (("ticket_id", 0, "BINARY"), ("changed_at", 1, "BINARY")),
        )
        self.assertEqual(
            index_columns["idx_ticket_timeline_ticket_occurred"],
            (("ticket_id", 0, "BINARY"), ("occurred_at", 1, "BINARY")),
        )

    def test_ticket_defaults_identity_and_case_insensitive_number(self) -> None:
        self.bootstrap_schema()

        with database_connection(self.database_path) as connection:
            ticket_id = connection.execute(
                """
                INSERT INTO tickets (
                    ticket_number,
                    subject,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?)
                """,
                ("INC-1001", "Default values", TIMESTAMP, TIMESTAMP),
            ).lastrowid
            row = connection.execute(
                """
                SELECT ticket_type, status, priority
                FROM tickets
                WHERE ticket_id = ?
                """,
                (ticket_id,),
            ).fetchone()
            with self.assertRaises(sqlite3.IntegrityError):
                self.insert_ticket(
                    connection,
                    ticket_number="inc-1001",
                    subject="Duplicate number",
                )

        self.assertEqual(tuple(row), ("INCIDENT", "NEW", "MEDIUM"))

    def test_ticket_required_fields_enums_and_lifecycle_constraints(self) -> None:
        self.bootstrap_schema()

        invalid_values = (
            {"ticket_number": None},
            {"ticket_number": ""},
            {"ticket_number": "   "},
            {"ticket_number": "INC-BAD-SUBJECT-1", "subject": None},
            {"ticket_number": "INC-BAD-SUBJECT-2", "subject": ""},
            {"ticket_number": "INC-BAD-SUBJECT-3", "subject": "   "},
            {"ticket_number": "INC-BAD-TYPE", "ticket_type": "CHANGE"},
            {"ticket_number": "INC-BAD-STATUS", "status": "REOPENED"},
            {"ticket_number": "INC-BAD-PRIORITY", "priority": "URGENT"},
            {
                "ticket_number": "INC-BAD-RESOLVED",
                "status": "OPEN",
                "resolved_at": TIMESTAMP,
            },
            {
                "ticket_number": "INC-BAD-CLOSED",
                "status": "RESOLVED",
                "closed_at": TIMESTAMP,
            },
        )
        for values in invalid_values:
            with self.subTest(values=values):
                with self.assertRaises(sqlite3.IntegrityError):
                    with database_connection(self.database_path) as connection:
                        self.insert_ticket(connection, **values)

        with database_connection(self.database_path) as connection:
            resolved_id = self.insert_ticket(
                connection,
                ticket_number="INC-RESOLVED",
                status="RESOLVED",
                resolved_at=TIMESTAMP,
            )
            closed_id = self.insert_ticket(
                connection,
                ticket_number="INC-CLOSED",
                status="CLOSED",
                resolved_at=TIMESTAMP,
                closed_at=TIMESTAMP,
            )

        self.assertGreater(resolved_id, 0)
        self.assertGreater(closed_id, 0)

    def test_ticket_foreign_keys_reject_missing_rows_and_set_null_on_delete(self) -> None:
        self.bootstrap_schema()

        for foreign_key in ("company_id", "contact_id", "category_id"):
            with self.subTest(foreign_key=foreign_key):
                with self.assertRaises(sqlite3.IntegrityError):
                    with database_connection(self.database_path) as connection:
                        self.insert_ticket(
                            connection,
                            ticket_number=f"INC-MISSING-{foreign_key}",
                            **{foreign_key: 999_999},
                        )

        with database_connection(self.database_path) as connection:
            company_id = connection.execute(
                """
                INSERT INTO companies (name, created_at, updated_at)
                VALUES (?, ?, ?)
                """,
                ("Ticket Company", TIMESTAMP, TIMESTAMP),
            ).lastrowid
            contact_id = connection.execute(
                """
                INSERT INTO contacts (
                    company_id, display_name, created_at, updated_at
                ) VALUES (?, ?, ?, ?)
                """,
                (company_id, "Ticket Contact", TIMESTAMP, TIMESTAMP),
            ).lastrowid
            category_id = connection.execute(
                """
                INSERT INTO categories (
                    scope, name, slug, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                ("TICKET", "Ticket Category", "ticket-category", TIMESTAMP, TIMESTAMP),
            ).lastrowid
            ticket_id = self.insert_ticket(
                connection,
                ticket_number="INC-RELATIONSHIPS",
                company_id=company_id,
                contact_id=contact_id,
                category_id=category_id,
            )
            connection.execute(
                "DELETE FROM companies WHERE company_id = ?",
                (company_id,),
            )
            connection.execute(
                "DELETE FROM contacts WHERE contact_id = ?",
                (contact_id,),
            )
            connection.execute(
                "DELETE FROM categories WHERE category_id = ?",
                (category_id,),
            )
            relationships = connection.execute(
                """
                SELECT company_id, contact_id, category_id
                FROM tickets
                WHERE ticket_id = ?
                """,
                (ticket_id,),
            ).fetchone()

        self.assertEqual(tuple(relationships), (None, None, None))

    def test_ticket_note_constraints_and_defaults(self) -> None:
        self.bootstrap_schema()

        with database_connection(self.database_path) as connection:
            ticket_id = self.insert_ticket(connection, ticket_number="INC-NOTES")
            note_id = connection.execute(
                """
                INSERT INTO ticket_notes (
                    ticket_id, note_text, created_at, updated_at
                ) VALUES (?, ?, ?, ?)
                """,
                (ticket_id, "Initial note", TIMESTAMP, TIMESTAMP),
            ).lastrowid
            defaults = connection.execute(
                """
                SELECT note_type, is_ai_generated
                FROM ticket_notes
                WHERE ticket_note_id = ?
                """,
                (note_id,),
            ).fetchone()

            invalid_notes = (
                (ticket_id, "INVALID", "Text", 0),
                (ticket_id, "INTERNAL", "", 0),
                (ticket_id, "INTERNAL", "   ", 0),
                (ticket_id, "INTERNAL", "Text", -1),
                (ticket_id, "INTERNAL", "Text", 2),
                (999_999, "INTERNAL", "Text", 0),
            )
            for invalid_note in invalid_notes:
                with self.subTest(invalid_note=invalid_note):
                    with self.assertRaises(sqlite3.IntegrityError):
                        connection.execute(
                            """
                            INSERT INTO ticket_notes (
                                ticket_id,
                                note_type,
                                note_text,
                                is_ai_generated,
                                created_at,
                                updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?)
                            """,
                            (*invalid_note, TIMESTAMP, TIMESTAMP),
                        )

        self.assertEqual(tuple(defaults), ("INTERNAL", 0))

    def test_status_history_constraints(self) -> None:
        self.bootstrap_schema()

        with database_connection(self.database_path) as connection:
            ticket_id = self.insert_ticket(connection, ticket_number="INC-HISTORY")
            connection.execute(
                """
                INSERT INTO ticket_status_history (
                    ticket_id, previous_status, new_status, changed_at
                ) VALUES (?, ?, ?, ?)
                """,
                (ticket_id, None, "NEW", TIMESTAMP),
            )

            invalid_history = (
                (ticket_id, "INVALID", "OPEN"),
                (ticket_id, "NEW", "INVALID"),
                (ticket_id, "OPEN", "OPEN"),
                (999_999, None, "NEW"),
            )
            for invalid_entry in invalid_history:
                with self.subTest(invalid_entry=invalid_entry):
                    with self.assertRaises(sqlite3.IntegrityError):
                        connection.execute(
                            """
                            INSERT INTO ticket_status_history (
                                ticket_id,
                                previous_status,
                                new_status,
                                changed_at
                            ) VALUES (?, ?, ?, ?)
                            """,
                            (*invalid_entry, TIMESTAMP),
                        )

            history_count = connection.execute(
                "SELECT COUNT(*) FROM ticket_status_history"
            ).fetchone()[0]

        self.assertEqual(history_count, 1)

    def test_timeline_constraints_and_owned_rows_cascade(self) -> None:
        self.bootstrap_schema()

        with database_connection(self.database_path) as connection:
            ticket_id = self.insert_ticket(connection, ticket_number="INC-TIMELINE")
            connection.execute(
                """
                INSERT INTO ticket_notes (
                    ticket_id, note_text, created_at, updated_at
                ) VALUES (?, ?, ?, ?)
                """,
                (ticket_id, "Owned note", TIMESTAMP, TIMESTAMP),
            )
            connection.execute(
                """
                INSERT INTO ticket_status_history (
                    ticket_id, previous_status, new_status, changed_at
                ) VALUES (?, ?, ?, ?)
                """,
                (ticket_id, None, "NEW", TIMESTAMP),
            )
            connection.execute(
                """
                INSERT INTO ticket_timeline_events (
                    ticket_id, event_type, title, occurred_at
                ) VALUES (?, ?, ?, ?)
                """,
                (ticket_id, "TICKET_CREATED", "Ticket created", TIMESTAMP),
            )

            for event_type, title, related_ticket_id in (
                ("", "Title", ticket_id),
                ("   ", "Title", ticket_id),
                ("EVENT", "", ticket_id),
                ("EVENT", "   ", ticket_id),
                ("EVENT", "Title", 999_999),
            ):
                with self.subTest(
                    event_type=event_type,
                    title=title,
                    ticket_id=related_ticket_id,
                ):
                    with self.assertRaises(sqlite3.IntegrityError):
                        connection.execute(
                            """
                            INSERT INTO ticket_timeline_events (
                                ticket_id, event_type, title, occurred_at
                            ) VALUES (?, ?, ?, ?)
                            """,
                            (related_ticket_id, event_type, title, TIMESTAMP),
                        )

            connection.execute(
                "DELETE FROM tickets WHERE ticket_id = ?",
                (ticket_id,),
            )
            remaining_counts = tuple(
                connection.execute(
                    f"SELECT COUNT(*) FROM {table_name}"
                ).fetchone()[0]
                for table_name in (
                    "ticket_notes",
                    "ticket_status_history",
                    "ticket_timeline_events",
                )
            )

        self.assertEqual(remaining_counts, (0, 0, 0))

    def test_database_integrity_after_ticket_inserts(self) -> None:
        self.bootstrap_schema()

        with database_connection(self.database_path) as connection:
            ticket_id = self.insert_ticket(connection, ticket_number="INC-INTEGRITY")
            connection.execute(
                """
                INSERT INTO ticket_status_history (
                    ticket_id, previous_status, new_status, changed_at
                ) VALUES (?, ?, ?, ?)
                """,
                (ticket_id, None, "NEW", TIMESTAMP),
            )
            integrity_results = run_integrity_check(connection)
            foreign_key_violations = run_foreign_key_check(connection)

        self.assertEqual(integrity_results, ("ok",))
        self.assertEqual(foreign_key_violations, ())

    def test_failed_migration_rolls_back_ticket_schema_only(self) -> None:
        copied_migrations = self.copy_production_migrations()
        copied_ticket_migration = copied_migrations[-1]
        copied_ticket_migration.write_text(
            copied_ticket_migration.read_text(encoding="utf-8")
            + """
            CREATE TABLE partial_ticket_state (value TEXT NOT NULL);
            INSERT INTO partial_ticket_state (value) VALUES ('temporary');
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

        self.assertFalse(
            {
                "tickets",
                "ticket_notes",
                "ticket_status_history",
                "ticket_timeline_events",
                "partial_ticket_state",
            }
            & tables
        )
        self.assertEqual(
            tuple((record.version, record.name) for record in records),
            ((1, "core"), (2, "taxonomy"), (3, "companies_contacts")),
        )
        self.assertEqual(integrity_results, ("ok",))
        self.assertEqual(foreign_key_violations, ())


if __name__ == "__main__":
    unittest.main()
