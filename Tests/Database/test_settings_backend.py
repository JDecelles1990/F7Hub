"""Isolated migration, persistence, CAS and safe-resolution tests for CP-02 S1."""

from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import FrozenInstanceError
from pathlib import Path
import multiprocessing
import shutil
import sqlite3
import tempfile
from threading import Barrier
import unittest
from unittest.mock import patch

from f7hub.domain.clipboard_settings import (
    CLIPBOARD_SETTING_DEFINITIONS, WORKFLOW_ENABLED, SOURCE_PROCESS_ENABLED, SOURCE_TITLE_ENABLED,
)
from f7hub.domain.settings import SettingDefinition, SettingsValidationError
from f7hub.infrastructure.database import bootstrap_database, database_connection, validate_database_integrity
from f7hub.infrastructure.migrations import MigrationApplicationError
from f7hub.repositories.settings_repository import SettingsConflictError, SettingsPersistenceError, SettingsRepository
from f7hub.services.settings_service import SettingsService


ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS = ROOT / "Database/Migrations"
ALL_TRUE = {entry.key: True for entry in CLIPBOARD_SETTING_DEFINITIONS}


def _competing_process(database_path, barrier, outcomes):
    service = SettingsService(SettingsRepository(database_path), CLIPBOARD_SETTING_DEFINITIONS)
    barrier.wait(timeout=10)
    try:
        outcomes.put(service.apply({WORKFLOW_ENABLED: True}, expected_revision=0).snapshot.revision)
    except SettingsConflictError:
        outcomes.put("CONFLICT")


class SettingsBackendTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.path = self.root / "settings.db"
        bootstrap_database(self.path, MIGRATIONS)
        self.repository = SettingsRepository(self.path)
        self.service = self.new_service()

    def new_service(self):
        return SettingsService(SettingsRepository(self.path), CLIPBOARD_SETTING_DEFINITIONS)

    def dump(self):
        with database_connection(self.path, read_only=True) as connection:
            return tuple(connection.iterdump())

    def assert_integrity(self):
        with database_connection(self.path, read_only=True) as connection:
            self.assertEqual(validate_database_integrity(connection), (("ok",), ()))
            self.assertEqual(connection.execute("PRAGMA foreign_keys").fetchone()[0], 1)
            self.assertEqual(connection.execute("PRAGMA busy_timeout").fetchone()[0], 5000)

    def corrupt(self, key, value_text, value_type="BOOLEAN"):
        # Simulate corruption/unreviewed legacy data, never relax production enforcement.
        with database_connection(self.path) as connection:
            connection.execute("PRAGMA ignore_check_constraints = ON")
            connection.execute("INSERT INTO settings_user_overrides VALUES (?, ?, ?)", (key, value_type, value_text))

    def test_fresh_defaults_without_rows_and_exact_schema(self):
        snapshot = self.service.get_snapshot()
        self.assertEqual(snapshot.revision, 0)
        self.assertTrue(snapshot.storage_available)
        self.assertEqual(snapshot.unknown_override_count, 0)
        self.assertTrue(all(entry.value is False and entry.source == "DEFAULT" for entry in snapshot.values))
        self.assertEqual(self.repository.load_state().overrides, ())
        with database_connection(self.path) as connection:
            objects = set(tuple(row) for row in connection.execute(
                "SELECT type, name FROM sqlite_master WHERE name LIKE 'settings_%'"))
            self.assertEqual(objects, {("table", "settings_state"), ("table", "settings_user_overrides")})
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0], 14)
        self.assert_integrity()

    def test_grouped_apply_and_restart(self):
        result = self.service.apply(ALL_TRUE, expected_revision=0)
        self.assertEqual(result.snapshot.revision, 1)
        self.assertEqual(set(result.changed_keys), set(ALL_TRUE))
        self.assertTrue(all(entry.value is True and entry.source == "USER" for entry in result.snapshot.values))
        self.assertEqual(self.new_service().get_snapshot(), result.snapshot)
        self.assert_integrity()

    def test_reset_deletes_override_and_reveals_default(self):
        self.service.apply(ALL_TRUE, expected_revision=0)
        result = self.service.reset((WORKFLOW_ENABLED,), expected_revision=1)
        self.assertEqual(result.snapshot.revision, 2)
        self.assertEqual(result.snapshot.get(WORKFLOW_ENABLED).source, "DEFAULT")
        self.assertFalse(result.snapshot.get(WORKFLOW_ENABLED).value)
        self.assertEqual(len(self.repository.load_state().overrides), 2)
        self.assertTrue(result.snapshot.get(SOURCE_PROCESS_ENABLED).value)
        self.assertTrue(result.snapshot.get(SOURCE_TITLE_ENABLED).value)

    def test_disable_master_preserves_independent_source_overrides(self):
        self.service.apply(ALL_TRUE, expected_revision=0)
        self.service.apply({WORKFLOW_ENABLED: False}, expected_revision=1)
        snapshot = self.new_service().get_snapshot()
        self.assertFalse(snapshot.get(WORKFLOW_ENABLED).value)
        self.assertTrue(snapshot.get(SOURCE_PROCESS_ENABLED).value)
        self.assertTrue(snapshot.get(SOURCE_TITLE_ENABLED).value)
        self.service.apply({SOURCE_TITLE_ENABLED: False}, expected_revision=2)
        self.assertTrue(self.new_service().get_snapshot().get(SOURCE_PROCESS_ENABLED).value)
        self.assertFalse(self.service.get_snapshot().get(SOURCE_TITLE_ENABLED).value)

    def test_source_title_can_be_enabled_without_process(self):
        result = self.service.apply({SOURCE_TITLE_ENABLED: True}, expected_revision=0)
        self.assertTrue(result.snapshot.get(SOURCE_TITLE_ENABLED).value)
        self.assertFalse(result.snapshot.get(SOURCE_PROCESS_ENABLED).value)
        self.assertFalse(result.snapshot.get(WORKFLOW_ENABLED).value)

    def test_noop_group_default_reset_and_same_override(self):
        events = []
        self.service.subscribe(events.append)
        before = self.dump()
        for changes, resets in (({}, ()), ({key: False for key in ALL_TRUE}, ()), ({}, tuple(ALL_TRUE))):
            result = self.service.apply(changes, resets=resets, expected_revision=0)
            self.assertEqual(result.changed_keys, ())
            self.assertEqual(result.snapshot.revision, 0)
            self.assertEqual(self.dump(), before)
        self.assertEqual(events, [])
        self.service.apply(ALL_TRUE, expected_revision=0)
        before = self.dump()
        result = self.service.apply(ALL_TRUE, expected_revision=1)
        self.assertEqual(result.changed_keys, ())
        self.assertEqual(result.snapshot.revision, 1)
        self.assertEqual(self.dump(), before)
        self.assertEqual(len(events), 1)

    def test_invalid_group_rejected_without_partial_writes_or_publish(self):
        events = []
        self.service.subscribe(events.append)
        before = self.dump()
        snapshot = self.service.get_snapshot()
        for invalid in (1, "true", None, "SYNTHETIC_PRIVATE_VALUE"):
            with self.assertRaises(SettingsValidationError) as error:
                self.service.apply({WORKFLOW_ENABLED: True, SOURCE_TITLE_ENABLED: invalid}, expected_revision=0)
            self.assertNotIn("SYNTHETIC_PRIVATE_VALUE", str(error.exception))
            self.assertEqual(self.dump(), before)
            self.assertIs(self.service.get_snapshot(), snapshot)
        self.assertEqual(events, [])

    def test_unknown_write_read_reset_and_invalid_group_shape(self):
        before = self.dump()
        calls = (
            lambda: self.service.apply({"clipboard.secret_override": True}, expected_revision=0),
            lambda: self.service.reset(("clipboard.secret_override",), expected_revision=0),
            lambda: self.service.get_snapshot().get("clipboard.secret_override"),
            lambda: self.service.apply({1: True}, expected_revision=0),
            lambda: self.service.apply([], expected_revision=0),
            lambda: self.service.reset(WORKFLOW_ENABLED, expected_revision=0),
            lambda: self.service.reset(None, expected_revision=0),
            lambda: self.service.reset((WORKFLOW_ENABLED, WORKFLOW_ENABLED), expected_revision=0),
            lambda: self.service.apply({WORKFLOW_ENABLED: True}, resets=(WORKFLOW_ENABLED,), expected_revision=0),
        )
        for call in calls:
            with self.subTest(call=call), self.assertRaises(SettingsValidationError):
                call()
        self.assertEqual(self.dump(), before)

    def test_uneditable_definition_rejects_writes_and_reset(self):
        service = SettingsService(self.repository, (SettingDefinition("example.locked", "example", False, editable=False),))
        with self.assertRaises(SettingsValidationError):
            service.apply({"example.locked": True}, expected_revision=0)
        with self.assertRaises(SettingsValidationError):
            service.reset(("example.locked",), expected_revision=0)

    def test_failure_after_first_group_write_rolls_back_revision_and_values(self):
        with database_connection(self.path) as connection:
            connection.execute("CREATE TRIGGER reject_title BEFORE INSERT ON settings_user_overrides "
                               "WHEN NEW.setting_key = 'clipboard.source_window_title_persistence_enabled' "
                               "BEGIN SELECT RAISE(ABORT, 'SYNTHETIC_PRIVATE_SQL_FAILURE'); END")
        before = self.dump()
        snapshot = self.service.get_snapshot()
        events = []
        self.service.subscribe(events.append)
        with self.assertRaises(SettingsPersistenceError) as error:
            self.service.apply(ALL_TRUE, expected_revision=0)
        self.assertNotIn("SYNTHETIC_PRIVATE_SQL_FAILURE", str(error.exception))
        self.assertEqual(self.dump(), before)
        self.assertIs(self.service.get_snapshot(), snapshot)
        self.assertEqual(events, [])
        self.assert_integrity()
        with database_connection(self.path) as connection:
            connection.execute("DROP TRIGGER reject_title")
        self.assertEqual(self.service.apply(ALL_TRUE, expected_revision=0).snapshot.revision, 1)

    def test_revision_update_failure_rolls_back_all_rows(self):
        with database_connection(self.path) as connection:
            connection.execute("CREATE TRIGGER reject_revision BEFORE UPDATE ON settings_state "
                               "BEGIN SELECT RAISE(ABORT, 'synthetic failure'); END")
        before = self.dump()
        with self.assertRaises(SettingsPersistenceError):
            self.service.apply(ALL_TRUE, expected_revision=0)
        self.assertEqual(self.dump(), before)
        self.assert_integrity()

    def test_commit_failure_rolls_back_and_does_not_publish(self):
        real_connection = database_connection
        class FailedCommit:
            def __init__(self, connection):
                self.connection = connection
            def execute(self, *args, **kwargs):
                return self.connection.execute(*args, **kwargs)
            def commit(self):
                raise sqlite3.OperationalError("synthetic commit failure")
        @contextmanager
        def connection_with_failed_commit(*args, **kwargs):
            with real_connection(*args, **kwargs) as connection:
                yield FailedCommit(connection)
        before = self.dump()
        snapshot = self.service.get_snapshot()
        with patch("f7hub.repositories.settings_repository.database_connection", connection_with_failed_commit):
            with self.assertRaises(SettingsPersistenceError):
                self.service.apply(ALL_TRUE, expected_revision=0)
        self.assertEqual(self.dump(), before)
        self.assertIs(self.service.get_snapshot(), snapshot)
        self.assert_integrity()

    def test_stale_revision_and_stale_noop_conflict(self):
        other = self.new_service()
        self.service.apply(ALL_TRUE, expected_revision=0)
        before = self.dump()
        for changes in ({SOURCE_PROCESS_ENABLED: True}, {}):
            with self.assertRaises(SettingsConflictError):
                other.apply(changes, expected_revision=0)
            self.assertEqual(self.dump(), before)
            self.assertEqual(other.get_snapshot().revision, 0)
        other.refresh()
        self.assertEqual(other.apply({SOURCE_TITLE_ENABLED: False}, expected_revision=1).snapshot.revision, 2)

    def test_stale_reset_cannot_erase_later_writer(self):
        self.service.apply({WORKFLOW_ENABLED: True}, expected_revision=0)
        stale = self.new_service()
        self.service.apply({WORKFLOW_ENABLED: False}, expected_revision=1)
        before = self.dump()
        with self.assertRaises(SettingsConflictError):
            stale.reset((WORKFLOW_ENABLED,), expected_revision=1)
        self.assertEqual(self.dump(), before)

    def test_competing_absent_key_inserts_have_one_commit_one_conflict(self):
        services = (self.new_service(), self.new_service())
        barrier = Barrier(2)
        def write(service):
            barrier.wait(timeout=5)
            try:
                return service.apply({WORKFLOW_ENABLED: True}, expected_revision=0).snapshot.revision
            except SettingsConflictError:
                return "CONFLICT"
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(write, services))
        self.assertCountEqual(results, (1, "CONFLICT"))
        self.assertEqual(self.repository.load_state().revision, 1)
        self.assertEqual(len(self.repository.load_state().overrides), 1)
        self.assert_integrity()

    def test_revision_validation(self):
        for revision in (True, -1, "0", None, 2**63):
            with self.subTest(revision=revision), self.assertRaises(SettingsValidationError):
                self.service.apply(ALL_TRUE, expected_revision=revision)

    def test_competing_process_writers_are_protected_by_database_cas(self):
        context = multiprocessing.get_context("spawn")
        barrier = context.Barrier(2)
        outcomes = context.Queue()
        processes = [context.Process(target=_competing_process, args=(str(self.path), barrier, outcomes))
                     for _ in range(2)]
        try:
            for process in processes:
                process.start()
            for process in processes:
                process.join(timeout=15)
                self.assertFalse(process.is_alive(), "Settings test-owned writer exceeded deadline")
                self.assertEqual(process.exitcode, 0)
            self.assertCountEqual((outcomes.get(timeout=2), outcomes.get(timeout=2)), (1, "CONFLICT"))
            self.assertEqual(self.service.refresh().revision, 1)
            self.assertTrue(self.service.get_snapshot().get(WORKFLOW_ENABLED).value)
            self.assert_integrity()
        finally:
            for process in processes:
                if process.is_alive():
                    process.terminate()
                    process.join(timeout=5)
                if process.pid is not None:
                    process.close()
            outcomes.close()
            outcomes.join_thread()

    def test_revision_overflow_fails_without_partial_values(self):
        with database_connection(self.path) as connection:
            connection.execute("UPDATE settings_state SET revision=?", (2**63 - 1,))
        self.service.refresh()
        before = self.dump()
        with self.assertRaises(SettingsPersistenceError):
            self.service.apply(ALL_TRUE, expected_revision=2**63 - 1)
        self.assertEqual(self.dump(), before)
        self.assert_integrity()

    def test_snapshot_is_immutable_and_operation_keeps_start_values(self):
        original = self.service.get_snapshot()
        self.service.apply(ALL_TRUE, expected_revision=0)
        self.assertEqual(original.revision, 0)
        self.assertTrue(all(entry.value is False for entry in original.values))
        with self.assertRaises(FrozenInstanceError):
            original.values[0].value = True
        with self.assertRaises(FrozenInstanceError):
            original.revision = 99

    def test_unknown_override_is_inert_preserved_and_not_exposed(self):
        self.corrupt("clipboard.removed_private_key", "SYNTHETIC_PRIVATE_VALUE")
        before = self.repository.load_state().overrides
        snapshot = self.service.refresh()
        self.assertEqual(snapshot.unknown_override_count, 1)
        self.assertNotIn("SYNTHETIC_PRIVATE_VALUE", repr(snapshot))
        self.assertNotIn("removed_private_key", repr(snapshot))
        self.service.apply(ALL_TRUE, expected_revision=0)
        self.assertIn(before[0], self.repository.load_state().overrides)

    def test_invalid_sensitive_override_fails_closed_and_stays_for_repair(self):
        for key in ALL_TRUE:
            self.corrupt(key, "SYNTHETIC_PRIVATE_VALUE")
        before = self.dump()
        snapshot = self.service.refresh()
        for entry in snapshot.values:
            self.assertFalse(entry.value)
            self.assertEqual((entry.source, entry.diagnostic), ("FAIL_CLOSED", "INVALID_STORED_VALUE"))
        self.assertNotIn("SYNTHETIC_PRIVATE_VALUE", repr(snapshot))
        self.assertEqual(self.dump(), before)
        repaired = self.service.apply({WORKFLOW_ENABLED: False}, expected_revision=0)
        self.assertEqual(repaired.snapshot.get(WORKFLOW_ENABLED).source, "USER")
        self.assertEqual(repaired.snapshot.get(SOURCE_TITLE_ENABLED).source, "FAIL_CLOSED")
        self.service.reset((SOURCE_PROCESS_ENABLED, SOURCE_TITLE_ENABLED), expected_revision=1)
        self.assert_integrity()

    def test_invalid_type_tag_is_not_coerced(self):
        self.corrupt(WORKFLOW_ENABLED, "true", "STRING")
        self.assertFalse(self.service.refresh().get(WORKFLOW_ENABLED).value)
        self.assertEqual(self.service.get_snapshot().get(WORKFLOW_ENABLED).source, "FAIL_CLOSED")

    def test_invalid_ordinary_value_uses_default_without_overwriting(self):
        key = "example.display_enabled"
        self.corrupt(key, "not a boolean")
        before = self.dump()
        service = SettingsService(self.repository, (SettingDefinition(key, "example", True, sensitivity="ORDINARY"),))
        entry = service.get_snapshot().get(key)
        self.assertTrue(entry.value)
        self.assertEqual((entry.source, entry.diagnostic), ("DEFAULT", "INVALID_STORED_VALUE"))
        self.assertEqual(self.dump(), before)

    def test_missing_storage_is_visible_disabled_and_creates_nothing(self):
        missing = self.root / "missing" / "absent.db"
        service = SettingsService(SettingsRepository(missing), CLIPBOARD_SETTING_DEFINITIONS)
        snapshot = service.get_snapshot()
        self.assertFalse(snapshot.storage_available)
        self.assertIsNone(snapshot.revision)
        self.assertTrue(all(entry.value is False and entry.source == "UNAVAILABLE" for entry in snapshot.values))
        with self.assertRaises(SettingsPersistenceError):
            service.apply(ALL_TRUE, expected_revision=0)
        self.assertFalse(missing.parent.exists())
        with self.assertRaises(SettingsPersistenceError):
            SettingsRepository(missing).apply(changes=ALL_TRUE, resets=(), expected_revision=0)
        self.assertFalse(missing.parent.exists())

    def test_storage_loss_refresh_discards_cached_sensitive_optins_and_recovers(self):
        self.service.apply(ALL_TRUE, expected_revision=0)
        saved = self.root / "saved.db"
        self.path.rename(saved)
        snapshot = self.service.refresh()
        self.assertFalse(snapshot.storage_available)
        self.assertTrue(all(entry.value is False for entry in snapshot.values))
        saved.rename(self.path)
        self.assertTrue(all(entry.value is True for entry in self.service.refresh().values))

    def test_missing_revision_record_is_unavailable_not_fabricated_zero(self):
        with database_connection(self.path) as connection:
            connection.execute("DELETE FROM settings_state")
        self.assertFalse(self.service.refresh().storage_available)
        with self.assertRaises(SettingsPersistenceError):
            self.repository.apply(changes=ALL_TRUE, resets=(), expected_revision=0)

    def test_notifications_only_after_commit_and_callback_failure_is_separate(self):
        events = []
        def observe(event):
            self.assertEqual(self.new_service().get_snapshot(), event.snapshot)
            self.assertIs(self.service.get_snapshot(), event.snapshot)
            events.append(event)
        def fail(event):
            raise RuntimeError("synthetic observer failure")
        self.service.subscribe(observe)
        self.service.subscribe(fail)
        self.service.subscribe(observe)
        result = self.service.apply(ALL_TRUE, expected_revision=0)
        self.assertEqual(result.notification_failures, 1)
        self.assertEqual(len(events), 1)
        self.assertEqual(self.repository.load_state().revision, 1)
        self.service.unsubscribe(fail)
        self.service.unsubscribe(observe)
        self.assertEqual(self.service.reset(tuple(ALL_TRUE), expected_revision=1).notification_failures, 0)
        self.assertEqual(len(events), 1)

    def test_explicit_refresh_observes_another_service_revision(self):
        other = self.new_service()
        self.service.apply(ALL_TRUE, expected_revision=0)
        self.assertEqual(other.get_snapshot().revision, 0)
        self.assertEqual(other.refresh(), self.service.get_snapshot())

    def test_read_cannot_mix_revision_and_values_when_writer_commits_between_queries(self):
        # WAL is fixture-only so a writer can commit while this read is open.
        with database_connection(self.path) as connection:
            self.assertEqual(connection.execute("PRAGMA journal_mode=WAL").fetchone()[0], "wal")
        real_connection = database_connection
        writer = self.new_service()
        injected = False
        @contextmanager
        def read_connection(*args, **kwargs):
            nonlocal injected
            with real_connection(*args, **kwargs) as connection:
                def between_queries(sql):
                    nonlocal injected
                    if sql.startswith("SELECT setting_key") and not injected:
                        injected = True
                        writer.apply(ALL_TRUE, expected_revision=0)
                connection.set_trace_callback(between_queries)
                yield connection
        with patch("f7hub.repositories.settings_repository.database_connection", read_connection):
            state = self.repository.load_state()
        self.assertTrue(injected)
        self.assertEqual((state.revision, state.overrides), (0, ()))
        self.assertEqual(self.repository.load_state().revision, 1)
        self.assertEqual(len(self.repository.load_state().overrides), 3)

    def test_schema_constraints_reject_invalid_rows_and_revision(self):
        with database_connection(self.path) as connection:
            for sql, values in (
                ("INSERT INTO settings_state VALUES (?, ?)", (2, 0)),
                ("UPDATE settings_state SET revision=?", (-1,)),
                ("UPDATE settings_state SET revision=?", (1.5,)),
                ("INSERT INTO settings_user_overrides VALUES (?, ?, ?)", ("x", "BOOLEAN", "true")),
                ("INSERT INTO settings_user_overrides VALUES (?, ?, ?)", (WORKFLOW_ENABLED, "BOOLEAN", "1")),
                ("INSERT INTO settings_user_overrides VALUES (?, ?, ?)", (WORKFLOW_ENABLED, "STRING", "true")),
            ):
                with self.subTest(sql=sql, values=values), self.assertRaises(sqlite3.IntegrityError):
                    connection.execute(sql, values)
        self.assertEqual(self.repository.load_state().revision, 0)
        self.assert_integrity()

    def test_additive_upgrade_repeat_bootstrap_and_existing_history_preserved(self):
        prior = self.root / "prior"
        prior.mkdir()
        for source in MIGRATIONS.glob("*.sql"):
            if int(source.name[:4]) <= 13:
                shutil.copyfile(source, prior / source.name)
        path = self.root / "upgrade.db"
        bootstrap_database(path, prior)
        with database_connection(path) as connection:
            connection.execute("INSERT INTO application_metadata VALUES ('synthetic_settings_upgrade', 'preserve', '2026-10-12T00:00:00.000Z')")
            history = tuple(tuple(row) for row in connection.execute("SELECT * FROM schema_migrations ORDER BY version"))
            scripts = tuple(tuple(row) for row in connection.execute("SELECT * FROM scripts ORDER BY script_id"))
        result = bootstrap_database(path, MIGRATIONS)
        self.assertEqual(result.migration_result.applied_versions, (14,))
        with database_connection(path) as connection:
            self.assertEqual(tuple(tuple(row) for row in connection.execute("SELECT * FROM schema_migrations WHERE version<=13 ORDER BY version")), history)
            self.assertEqual(tuple(tuple(row) for row in connection.execute("SELECT * FROM scripts ORDER BY script_id")), scripts)
            self.assertEqual(connection.execute("SELECT metadata_value FROM application_metadata WHERE metadata_key='synthetic_settings_upgrade'").fetchone()[0], "preserve")
            self.assertEqual(validate_database_integrity(connection), (("ok",), ()))
        repository = SettingsRepository(path)
        repository.apply(changes=ALL_TRUE, resets=(), expected_revision=0)
        before = repository.load_state()
        self.assertEqual(bootstrap_database(path, MIGRATIONS).migration_result.applied_versions, ())
        self.assertEqual(repository.load_state(), before)

    def test_failed_migration_rolls_back_schema_and_history(self):
        migrations = self.root / "failure-migrations"
        shutil.copytree(MIGRATIONS, migrations)
        target = migrations / "0014_shared_settings.sql"
        with target.open("a", encoding="utf-8") as file:
            file.write("\nINSERT INTO settings_state VALUES (2, 0);\n")
        path = self.root / "failed.db"
        with self.assertRaises(MigrationApplicationError):
            bootstrap_database(path, migrations)
        with database_connection(path) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM sqlite_master WHERE name LIKE 'settings_%'").fetchone()[0], 0)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM schema_migrations WHERE version=14").fetchone()[0], 0)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0], 13)
            self.assertEqual(validate_database_integrity(connection), (("ok",), ()))
