from dataclasses import asdict
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest
from unittest.mock import mock_open, patch

from f7hub.infrastructure.database import (
    bootstrap_database, database_connection, run_foreign_key_check, run_integrity_check,
)
from f7hub.repositories.script_repository import ScriptRepository
from f7hub.services.script_service import (
    ScriptConflictError, ScriptCopyError, ScriptReadError, ScriptService,
    ScriptValidationError, ScriptWriteError,
)


ROOT = Path(__file__).resolve().parents[2]


class ScriptManagementTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        migrations = self.root / "migrations"
        migrations.mkdir()
        for source in (ROOT / "Database" / "Migrations").glob("*.sql"):
            if int(source.name[:4]) <= 7:
                shutil.copyfile(source, migrations / source.name)
        self.database = self.root / "test.db"
        bootstrap_database(self.database, migrations)
        self.folder = self.root / "PowerShell" / "Diagnostics"
        self.folder.mkdir(parents=True)
        (self.folder / "one.ps1").write_text("# fixture only\n", encoding="utf-8")
        self.repo = ScriptRepository(self.database)
        self.service = ScriptService(self.repo, self.root)
        self.values = dict(script_code="one", name="One", relative_path="PowerShell/Diagnostics/one.ps1",
                           script_type="DIAGNOSTIC", risk_level="LOW", privilege_level="STANDARD_USER")

    def register(self, **overrides):
        return self.service.register_script(**(self.values | overrides))

    def dump(self):
        with database_connection(self.database) as connection:
            return tuple(connection.iterdump())

    def test_registration_normalizes_metadata_and_uses_table_defaults(self):
        with patch("f7hub.services.script_service.hashlib.sha256", side_effect=AssertionError("source hashed")), \
                patch("subprocess.Popen", side_effect=AssertionError("execution")):
            row = self.register(script_code=" one ", name=" One ",
                                relative_path="PowerShell\\Diagnostics\\one.ps1",
                                description=" detail ", version=" ")
        self.assertEqual(row.relative_path, self.values["relative_path"])
        self.assertEqual((row.script_code, row.name, row.description, row.version), ("one", "One", "detail", None))
        self.assertEqual((row.runtime, row.timeout_seconds, row.requires_structured_output, row.is_enabled),
                         ("POWERSHELL_7", 120, 1, 0))
        self.assertIsNone(row.category_id)
        self.assertIsNone(row.checksum_sha256)
        self.assertEqual(row.created_at, row.updated_at)
        self.assertEqual(self.service.list_scripts(), ())
        self.assertEqual(self.service.list_registered_scripts()[0].metadata, row)
        with database_connection(self.database) as connection:
            self.assertEqual(run_integrity_check(connection), ("ok",))
            self.assertEqual(run_foreign_key_check(connection), ())

    def test_duplicate_codes_and_normalized_paths_leave_original_unchanged(self):
        row = self.register()
        (self.folder / "two.ps1").write_text("# fixture", encoding="utf-8")
        before = self.dump()
        for overrides in (dict(script_code="ONE", relative_path="PowerShell/Diagnostics/two.ps1"),
                          dict(script_code="two", relative_path="PowerShell\\Diagnostics\\ONE.ps1")):
            with self.subTest(overrides=overrides), self.assertRaisesRegex(ScriptWriteError, "already registered"):
                self.register(**overrides)
        self.assertEqual(before, self.dump())
        with database_connection(self.database) as connection:
            connection.execute("UPDATE scripts SET relative_path=? WHERE script_id=?",
                               ("PowerShell\\Diagnostics\\one.ps1", row.script_id))
        with self.assertRaisesRegex(ScriptWriteError, "already registered"):
            self.register(script_code="different")

    def test_invalid_fields_and_references_never_write(self):
        before = self.dump()
        for overrides in (
            dict(script_code=" "), dict(name=None), dict(description=3), dict(version=3),
            dict(script_type="unknown"), dict(risk_level="unknown"), dict(privilege_level="unknown"),
            dict(relative_path="PowerShell/Diagnostics/missing.ps1"),
            dict(relative_path="PowerShell/Diagnostics/../Reports/one.ps1"),
            dict(relative_path="C:/outside.ps1"), dict(relative_path="PowerShell/Diagnostics/one.ps1:ads"),
        ):
            with self.subTest(overrides=overrides), self.assertRaises(ScriptValidationError):
                self.register(**overrides)
        with patch("f7hub.services.script_service._resolve_script_reference", return_value=("INACCESSIBLE", None)):
            with self.assertRaises(ScriptValidationError):
                self.register()
        original_resolve = Path.resolve
        outside = self.root / "outside.ps1"
        def escaped(path, *, strict=False):
            return outside if path == self.folder / "one.ps1" else original_resolve(path, strict=strict)
        with patch.object(Path, "resolve", escaped), self.assertRaises(ScriptValidationError):
            self.register()
        self.assertEqual(before, self.dump())

    def test_registration_open_or_read_failure_rejects_without_any_write(self):
        before = self.dump()
        for operation, error in (("open", PermissionError("private ACL path")),
                                 ("read", PermissionError("private ACL path")),
                                 ("open", FileNotFoundError("private vanished path")),
                                 ("read", OSError("private read failure"))):
            opener = mock_open(read_data=b"")
            if operation == "open":
                opener.side_effect = error
            else:
                opener.return_value.read.side_effect = error
            with self.subTest(operation=operation, error=type(error).__name__), \
                    patch.object(self.repo, "register_script", wraps=self.repo.register_script) as write, \
                    patch.object(Path, "open", opener), self.assertRaises(ScriptValidationError) as failure:
                self.register()
            write.assert_not_called()
            self.assertNotIn("private", str(failure.exception))
            self.assertEqual(before, self.dump())
            with database_connection(self.database) as connection:
                self.assertEqual(connection.execute("SELECT count(*) FROM scripts").fetchone()[0], 0)

    def test_enable_open_or_read_failure_preserves_every_persisted_field(self):
        row = self.register()
        for checksum in (None, "a" * 64):
            with database_connection(self.database) as connection:
                connection.execute("UPDATE scripts SET checksum_sha256=? WHERE script_id=?",
                                   (checksum, row.script_id))
            entry = self.service.list_registered_scripts()[0]
            self.assertEqual(entry.file_status, "AVAILABLE")
            before = self.dump()
            for operation in ("open", "read"):
                opener = mock_open(read_data=b"")
                if operation == "open":
                    opener.side_effect = PermissionError("private ACL path")
                else:
                    opener.return_value.read.side_effect = PermissionError("private ACL path")
                with self.subTest(checksum=checksum, operation=operation), \
                        patch.object(self.repo, "set_script_enabled", wraps=self.repo.set_script_enabled) as write, \
                        patch.object(Path, "open", opener), self.assertRaises(ScriptValidationError) as failure:
                    self.service.set_script_enabled(row.script_id, enabled=True,
                                                    expected_updated_at=entry.metadata.updated_at)
                write.assert_not_called()
                self.assertNotIn("private", str(failure.exception))
                self.assertEqual(before, self.dump())
                self.assertEqual(self.service.list_registered_scripts()[0].metadata, entry.metadata)

    def test_disable_unreadable_source_preserves_checksum_and_stale_guard(self):
        row = self.register()
        enabled = self.service.set_script_enabled(row.script_id, enabled=True, expected_updated_at=row.updated_at)
        with database_connection(self.database) as connection:
            connection.execute("UPDATE scripts SET checksum_sha256=? WHERE script_id=?", ("a" * 64, row.script_id))
        original = self.service.list_registered_scripts()[0].metadata
        with patch.object(Path, "open", side_effect=PermissionError("private ACL path")) as opener:
            disabled = self.service.set_script_enabled(row.script_id, enabled=False,
                                                       expected_updated_at=enabled.updated_at)
            before = self.dump()
            with self.assertRaises(ScriptConflictError):
                self.service.set_script_enabled(row.script_id, enabled=False,
                                                expected_updated_at=enabled.updated_at)
            self.assertEqual(before, self.dump())
        opener.assert_not_called()
        self.assertEqual(disabled.is_enabled, 0)
        self.assertGreater(disabled.updated_at, original.updated_at)
        self.assertEqual({k: v for k, v in asdict(original).items() if k not in ("updated_at", "is_enabled")},
                         {k: v for k, v in asdict(disabled).items() if k not in ("updated_at", "is_enabled")})

    def test_readability_probe_accepts_empty_file_reads_one_byte_and_closes(self):
        target = self.folder / "one.ps1"
        target.write_bytes(b"")
        opener = mock_open(read_data=b"")
        with patch.object(Path, "open", opener), \
                patch("f7hub.services.script_service.hashlib.sha256", side_effect=AssertionError("source hashed")):
            row = self.register()
            enabled = self.service.set_script_enabled(row.script_id, enabled=True, expected_updated_at=row.updated_at)
        self.assertEqual(opener.call_count, 2)
        self.assertTrue(all(call.args == ("rb",) for call in opener.call_args_list))
        self.assertEqual([call.args for call in opener.return_value.read.call_args_list], [(1,), (1,)])
        self.assertEqual(opener.return_value.__exit__.call_count, 2)
        self.assertIsNone(enabled.checksum_sha256)
        self.assertEqual(target.read_bytes(), b"")
        self.assertEqual(self.service.set_script_enabled(row.script_id, enabled=True,
                                                        expected_updated_at=enabled.updated_at), enabled)

    def test_denied_registration_and_enable_recover_without_duplicate_or_source_change(self):
        source = (self.folder / "one.ps1").read_bytes()
        with patch.object(Path, "open", side_effect=PermissionError("private ACL path")):
            with self.assertRaises(ScriptValidationError):
                self.register()
        row = self.register()
        with patch.object(Path, "open", side_effect=PermissionError("private ACL path")):
            with self.assertRaises(ScriptValidationError):
                self.service.set_script_enabled(row.script_id, enabled=True, expected_updated_at=row.updated_at)
        enabled = self.service.set_script_enabled(row.script_id, enabled=True, expected_updated_at=row.updated_at)
        self.assertIsNone(enabled.checksum_sha256)
        with self.assertRaises(ScriptCopyError) as failure:
            self.service.read_verified_script(row.script_code)
        self.assertEqual(failure.exception.code, "INTEGRITY_NOT_APPROVED")
        with database_connection(self.database) as connection:
            self.assertEqual(connection.execute("SELECT count(*) FROM scripts").fetchone()[0], 1)
            self.assertEqual(run_integrity_check(connection), ("ok",))
            self.assertEqual(run_foreign_key_check(connection), ())
        self.assertEqual((self.folder / "one.ps1").read_bytes(), source)

    def test_management_preserves_script_category_scope_and_read_only_behavior(self):
        row = self.register()
        with database_connection(self.database) as connection:
            for scope in ("SCRIPT", "TICKET"):
                category = connection.execute(
                    "INSERT INTO categories(scope,name,slug,created_at,updated_at) VALUES(?,?,?,?,?)",
                    (scope, scope, scope, row.created_at, row.updated_at),
                ).lastrowid
                connection.execute(
                    "INSERT INTO scripts(script_code,name,relative_path,script_type,category_id,created_at,updated_at) "
                    "VALUES(?,?,?,'DIAGNOSTIC',?,?,?)",
                    (scope, scope, f"PowerShell/Diagnostics/{scope}.ps1", category, row.created_at, row.updated_at),
                )
        before = self.dump()
        self.assertEqual({entry.metadata.script_code for entry in self.service.list_registered_scripts()}, {"one", "SCRIPT"})
        self.assertEqual(before, self.dump())
        with database_connection(self.database) as connection:
            hidden = connection.execute("SELECT script_id FROM scripts WHERE script_code='TICKET'").fetchone()[0]
        with self.assertRaises(ScriptConflictError):
            self.service.set_script_enabled(hidden, enabled=True, expected_updated_at=row.updated_at)

    def test_toggle_advances_token_and_changes_only_visibility_and_time(self):
        row = self.register()
        with database_connection(self.database) as connection:
            connection.execute("UPDATE scripts SET checksum_sha256=? WHERE script_id=?", ("a" * 64, row.script_id))
        original = self.service.list_registered_scripts()[0].metadata
        with patch("f7hub.services.script_service._timestamp", return_value=original.updated_at):
            enabled = self.service.set_script_enabled(row.script_id, enabled=True, expected_updated_at=row.updated_at)
        self.assertGreater(enabled.updated_at, original.updated_at)
        self.assertEqual({k: v for k, v in asdict(original).items() if k not in ("updated_at", "is_enabled")},
                         {k: v for k, v in asdict(enabled).items() if k not in ("updated_at", "is_enabled")})
        self.assertEqual(self.service.list_scripts()[0].metadata, enabled)
        disabled = self.service.set_script_enabled(row.script_id, enabled=False, expected_updated_at=enabled.updated_at)
        self.assertGreater(disabled.updated_at, enabled.updated_at)
        self.assertEqual(self.service.list_scripts(), ())
        before = self.dump()
        self.assertEqual(self.service.set_script_enabled(row.script_id, enabled=False,
                                                        expected_updated_at=disabled.updated_at), disabled)
        self.assertEqual(self.dump(), before)

    def test_stale_missing_and_changed_path_tokens_cannot_overwrite(self):
        row = self.register()
        enabled = self.service.set_script_enabled(row.script_id, enabled=True, expected_updated_at=row.updated_at)
        before = self.dump()
        with self.assertRaises(ScriptConflictError):
            self.service.set_script_enabled(row.script_id, enabled=False, expected_updated_at=row.updated_at)
        with self.assertRaises(ScriptConflictError):
            self.service.set_script_enabled(999, enabled=True, expected_updated_at=row.updated_at)
        original_write = self.repo.set_script_enabled
        def race(*args, **kwargs):
            with database_connection(self.database) as connection:
                connection.execute("UPDATE scripts SET relative_path=? WHERE script_id=?",
                                   ("PowerShell/Reports/changed.ps1", row.script_id))
            return original_write(*args, **kwargs)
        with patch.object(self.repo, "set_script_enabled", side_effect=race), self.assertRaises(ScriptConflictError):
            self.service.set_script_enabled(row.script_id, enabled=False, expected_updated_at=enabled.updated_at)
        with database_connection(self.database) as connection:
            self.assertEqual(connection.execute("SELECT is_enabled FROM scripts").fetchone()[0], 1)
        # Stale and missing calls did not write; only the explicitly injected external race did.
        self.assertNotEqual(self.dump(), before)

    def test_enable_rechecks_file_but_disable_works_after_removal(self):
        row = self.register()
        (self.folder / "one.ps1").unlink()
        with self.assertRaises(ScriptValidationError):
            self.service.set_script_enabled(row.script_id, enabled=True, expected_updated_at=row.updated_at)
        with database_connection(self.database) as connection:
            connection.execute("UPDATE scripts SET is_enabled=1")
        disabled = self.service.set_script_enabled(row.script_id, enabled=False, expected_updated_at=row.updated_at)
        self.assertEqual(disabled.is_enabled, 0)

    def test_reload_and_sql_failures_roll_back_and_hide_raw_details(self):
        before = self.dump()
        with patch("f7hub.repositories.script_repository._get_registered_script", return_value=None):
            with self.assertRaisesRegex(ScriptWriteError, "Could not register"):
                self.register()
        self.assertEqual(before, self.dump())
        row = self.register()
        before = self.dump()
        with patch("f7hub.repositories.script_repository._get_registered_script",
                   side_effect=[row, None]), self.assertRaises(ScriptWriteError):
            self.service.set_script_enabled(row.script_id, enabled=True, expected_updated_at=row.updated_at)
        self.assertEqual(before, self.dump())
        with database_connection(self.database) as connection:
            connection.execute("CREATE TRIGGER reject_enable BEFORE UPDATE ON scripts BEGIN SELECT RAISE(ABORT, 'private detail'); END")
        with self.assertRaises(ScriptWriteError) as failure:
            self.service.set_script_enabled(row.script_id, enabled=True, expected_updated_at=row.updated_at)
        self.assertNotIn("private", str(failure.exception))
        with patch.object(self.repo, "list_scripts", side_effect=sqlite3.OperationalError("private")):
            with self.assertRaises(ScriptReadError):
                self.service.list_registered_scripts()

    def test_zero_updated_rows_is_conflict_and_does_not_commit(self):
        row = self.register()
        with database_connection(self.database) as connection:
            connection.execute("CREATE TRIGGER ignore_enable BEFORE UPDATE ON scripts BEGIN SELECT RAISE(IGNORE); END")
        before = self.dump()
        with self.assertRaises(ScriptConflictError):
            self.service.set_script_enabled(row.script_id, enabled=True, expected_updated_at=row.updated_at)
        self.assertEqual(before, self.dump())

    def test_new_enabled_registration_is_not_copy_approved(self):
        row = self.register()
        enabled = self.service.set_script_enabled(row.script_id, enabled=True, expected_updated_at=row.updated_at)
        self.assertIsNone(enabled.checksum_sha256)
        with self.assertRaises(ScriptCopyError) as failure:
            self.service.read_verified_script(row.script_code)
        self.assertEqual(failure.exception.code, "INTEGRITY_NOT_APPROVED")

    def test_invalid_toggle_inputs_are_rejected_before_repository_access(self):
        with patch.object(self.repo, "list_scripts", side_effect=AssertionError("accessed")):
            for script_id, enabled, token in ((True, True, "stamp"), (0, True, "stamp"),
                                             (2**63, True, "stamp"), (1, 1, "stamp"), (1, True, "")):
                with self.subTest(script_id=script_id, enabled=enabled, token=token), self.assertRaises(ScriptValidationError):
                    self.service.set_script_enabled(script_id, enabled=enabled, expected_updated_at=token)
