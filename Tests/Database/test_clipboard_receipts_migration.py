"""D02 receipt constraints and upgrade tests, synthetic databases only."""

from dataclasses import FrozenInstanceError
import shutil
import sqlite3
from uuid import uuid4

from f7hub.domain.clipboard import ClipboardCaptureOutcome, ClipboardOperation, ClipboardValidationError
from f7hub.infrastructure.database import bootstrap_database, database_connection, validate_database_integrity
from f7hub.infrastructure.migrations import MigrationApplicationError, MigrationChecksumError
from Tests.Database.clipboard_fixtures import ClipboardDatabaseTestCase, PROJECT_ROOT, seed_item


def receipt_values(item_id, **changes):
    values = dict(
        producer_binding="synthetic", ingress_generation=str(uuid4()), operation_id=str(uuid4()),
        database_scope="a" * 64, request_profile="clipboard_manual_durable_v1", media_type="text/plain",
        identity_profile="clipboard_text_exact_v1", capture_method="F7HUB", observed_at=None,
        source_class=None, assessment_method="synthetic", assessment_version="1", policy_version="1",
        sensitivity="PERMITTED", assessment_complete=1, durable_history_authorized=1, temporary_days=7,
        historical_item_id=item_id, historical_event_id=1, live_item_id=item_id, was_duplicate=0,
        captured_total=1, item_revision=1, retention_intent="TEMPORARY", is_pinned=0,
        item_expires_at="2026-10-15T10:00:00.000Z", accepted_at="2026-10-08T10:00:00.000Z",
        expires_at="2026-10-22T10:00:00.000Z",
    )
    values.update(changes)
    return values


def insert_receipt(connection, item_id, **changes):
    values = receipt_values(item_id, **changes)
    connection.execute("INSERT INTO clipboard_operation_receipts (" + ",".join(values)
                       + ") VALUES (" + ",".join("?" for _ in values) + ")", tuple(values.values()))
    return values


class ClipboardReceiptsMigrationTests(ClipboardDatabaseTestCase):
    def test_fresh_install_and_repeat_bootstrap(self):
        with database_connection(self.database_path) as connection:
            self.assertEqual(tuple(r[0] for r in connection.execute("SELECT version FROM schema_migrations ORDER BY version")), tuple(range(1, 16)))
            self.assertEqual(connection.execute("SELECT count(*) FROM clipboard_operation_receipts").fetchone()[0], 0)
            indexes = {r[1] for r in connection.execute("PRAGMA index_list(clipboard_operation_receipts)")}
            self.assertTrue({"idx_clipboard_receipts_expiry", "idx_clipboard_receipts_live_item"} <= indexes)
            self.assertEqual(validate_database_integrity(connection), (("ok",), ()))
        self.assertEqual(bootstrap_database(self.database_path, PROJECT_ROOT / "Database/Migrations").migration_result.applied_versions, ())

    def test_upgrade_from_14_preserves_every_existing_row_and_history(self):
        directory = self.root / "prior"
        directory.mkdir()
        for migration in (PROJECT_ROOT / "Database/Migrations").glob("*.sql"):
            if int(migration.name[:4]) <= 14:
                shutil.copyfile(migration, directory / migration.name)
        path = self.root / "prior.db"
        bootstrap_database(path, directory)
        with database_connection(path) as connection:
            seed_item(connection)
            connection.execute("INSERT INTO settings_user_overrides VALUES ('clipboard.workflow.enabled', 'BOOLEAN', 'true')")
            tables = [r[0] for r in connection.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
            before = {table: tuple(tuple(r) for r in connection.execute('SELECT * FROM "' + table + '"')) for table in tables}
        self.assertEqual(bootstrap_database(path, PROJECT_ROOT / "Database/Migrations").migration_result.applied_versions, (15,))
        with database_connection(path) as connection:
            for table, rows in before.items():
                query = 'SELECT * FROM "' + table + '"' + (" WHERE version <= 14" if table == "schema_migrations" else "")
                self.assertEqual(tuple(tuple(r) for r in connection.execute(query)), rows, table)
            self.assertEqual(validate_database_integrity(connection), (("ok",), ()))

    def test_constraints_nullability_uniqueness_and_no_content_columns(self):
        with database_connection(self.database_path) as connection:
            item_id = seed_item(connection)
            values = insert_receipt(connection, item_id)
            for changes in (
                {"producer_binding": ""}, {"producer_binding": "x" * 129}, {"producer_binding": "private title"},
                {"ingress_generation": "bad"}, {"operation_id": "bad"}, {"database_scope": "bad"},
                {"request_profile": "other"}, {"media_type": "html"}, {"identity_profile": "other"},
                {"capture_method": "AUTO"}, {"observed_at": "bad"}, {"source_class": "private title"},
                {"assessment_method": ""}, {"assessment_version": "x" * 65}, {"policy_version": " "},
                {"sensitivity": "DENIED"}, {"assessment_complete": 0}, {"durable_history_authorized": 0},
                {"temporary_days": 1}, {"historical_item_id": 0}, {"historical_event_id": 0},
                {"live_item_id": 999}, {"captured_total": 1.5}, {"item_revision": 0}, {"was_duplicate": 2},
                {"retention_intent": "OTHER"}, {"is_pinned": 1}, {"item_expires_at": None},
                {"accepted_at": "bad"}, {"expires_at": "2026-10-08T10:00:00.000Z"},
            ):
                with self.subTest(fields=tuple(changes)), self.assertRaises(sqlite3.IntegrityError):
                    insert_receipt(connection, item_id, **changes)
            nullable = {"observed_at", "source_class", "live_item_id", "item_expires_at"}
            for column in set(values) - nullable:
                with self.subTest(null_column=column), self.assertRaises(sqlite3.IntegrityError):
                    insert_receipt(connection, item_id, **{column: None})
            with self.assertRaises(sqlite3.IntegrityError):
                insert_receipt(connection, item_id, **values)
            columns = {r[1] for r in connection.execute("PRAGMA table_info(clipboard_operation_receipts)")}
            self.assertFalse({"raw_text", "preview", "source_title", "payload", "content_hash"} & columns)

    def test_receipt_survives_deletion_and_numeric_id_reuse(self):
        with database_connection(self.database_path) as connection:
            item_id = seed_item(connection)
            values = insert_receipt(connection, item_id)
            connection.execute("DELETE FROM clipboard_items WHERE clipboard_item_id=?", (item_id,))
            seed_item(connection, item_id=item_id, raw_text="Different synthetic replacement")
            row = connection.execute("SELECT * FROM clipboard_operation_receipts").fetchone()
            self.assertIsNone(row["live_item_id"])
            self.assertEqual(row["historical_item_id"], values["historical_item_id"])
            self.assertEqual(row["historical_event_id"], values["historical_event_id"])
            self.assertEqual(validate_database_integrity(connection), (("ok",), ()))

    def test_checksum_enforcement_and_atomic_failed_migration(self):
        directory = self.root / "changed"
        shutil.copytree(PROJECT_ROOT / "Database/Migrations", directory)
        migration = directory / "0015_clipboard_operation_receipts.sql"
        migration.write_bytes(migration.read_bytes() + b"\n-- synthetic alteration\n")
        with self.assertRaises(MigrationChecksumError):
            bootstrap_database(self.database_path, directory)
        migration.write_bytes(migration.read_bytes() + b"\nINVALID SQL;\n")
        path = self.root / "failure.db"
        with self.assertRaises(MigrationApplicationError):
            bootstrap_database(path, directory)
        with database_connection(path) as connection:
            self.assertEqual(connection.execute("SELECT max(version) FROM schema_migrations").fetchone()[0], 14)
            self.assertIsNone(connection.execute("SELECT name FROM sqlite_master WHERE name='clipboard_operation_receipts'").fetchone())
            self.assertEqual(validate_database_integrity(connection), (("ok",), ()))

    def test_original_outcome_contract_is_immutable_and_validated(self):
        operation = ClipboardOperation("synthetic", str(uuid4()), str(uuid4()))
        outcome = ClipboardCaptureOutcome(operation, 1, 2, False, 1, 1, "TEMPORARY", False,
            "2026-10-15T10:00:00.000Z", "2026-10-08T10:00:00.000Z", "2026-10-22T10:00:00.000Z")
        with self.assertRaises(FrozenInstanceError):
            outcome.item_revision = 2
        with self.assertRaises(ClipboardValidationError):
            ClipboardCaptureOutcome(operation, True, 2, False, 1, 1, "TEMPORARY", False,
                outcome.item_expires_at, outcome.accepted_at, outcome.receipt_expires_at)
