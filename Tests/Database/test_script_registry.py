from __future__ import annotations

from pathlib import Path
from contextlib import contextmanager
import shutil
import sqlite3
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from f7hub.infrastructure.database import (
    bootstrap_database, database_connection, run_foreign_key_check, run_integrity_check,
)
from f7hub.infrastructure.migrations import list_applied_migrations
from f7hub.repositories.script_repository import ScriptRepository
from f7hub.services.script_service import (
    AVAILABLE, INACCESSIBLE, INVALID_REFERENCE, MISSING,
    ScriptReadError, ScriptService, ScriptValidationError, inspect_script_reference,
)


ROOT = Path(__file__).resolve().parents[2]
SOURCE_MIGRATIONS = ROOT / "Database" / "Migrations"
STAMP = "2026-09-30T00:00:00.000Z"


class ScriptRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.database = self.root / "test.db"
        self.migrations = self.root / "migrations"
        self.migrations.mkdir()

    def copy_migrations(self, last_version: int = 7) -> None:
        for source in SOURCE_MIGRATIONS.iterdir():
            if source.suffix == ".sql" and int(source.name[:4]) <= last_version:
                shutil.copyfile(source, self.migrations / source.name)

    def bootstrap(self) -> None:
        self.copy_migrations()
        bootstrap_database(self.database, self.migrations)

    def category(self, scope: str = "SCRIPT") -> int:
        with database_connection(self.database) as connection:
            return int(connection.execute(
                "INSERT INTO categories (scope, name, slug, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (scope, scope.title(), scope.lower(), STAMP, STAMP),
            ).lastrowid)

    def script(self, code: str, *, category_id: int | None = None,
               enabled: int | None = 1, name: str | None = None,
               relative_path: str | None = None, description: str | None = None) -> int:
        with database_connection(self.database) as connection:
            columns = "script_code, name, relative_path, script_type, category_id, created_at, updated_at, description"
            values: tuple[object, ...] = (
                code, name if name is not None else code,
                relative_path or f"PowerShell/Diagnostics/{code}.ps1",
                "DIAGNOSTIC", category_id, STAMP, STAMP, description,
            )
            if enabled is not None:
                columns += ", is_enabled"
                values += (enabled,)
            marks = ", ".join("?" for _ in values)
            return int(connection.execute(
                f"INSERT INTO scripts ({columns}) VALUES ({marks})", values,
            ).lastrowid)

    def test_fresh_and_incremental_migration_preserve_history_and_data(self) -> None:
        self.bootstrap()
        with database_connection(self.database) as connection:
            self.assertEqual(tuple(row.version for row in list_applied_migrations(connection)), tuple(range(1, 8)))
            self.assertEqual(connection.execute("PRAGMA foreign_keys").fetchone()[0], 1)
            self.assertEqual(run_integrity_check(connection), ("ok",))
            self.assertEqual(run_foreign_key_check(connection), ())
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM scripts").fetchone()[0], 0)
            columns = {row[1]: row for row in connection.execute("PRAGMA table_info(scripts)")}
            self.assertEqual(columns["is_enabled"][4], "0")
            indexes = {row[1] for row in connection.execute("PRAGMA index_list(scripts)")}
            self.assertIn("idx_scripts_enabled_name", indexes)
            self.assertIn("idx_scripts_category_id", indexes)

        second = self.root / "incremental.db"
        migration7 = self.migrations / "0007_script_registry.sql"
        migration7.unlink()
        bootstrap_database(second, self.migrations)
        with database_connection(second) as connection:
            connection.execute(
                "INSERT INTO categories (scope, name, slug, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?)",
                ("SCRIPT", "Preserve", "preserve", STAMP, STAMP),
            )
            original = tuple(tuple(row) for row in connection.execute(
                "SELECT version, name, checksum_sha256, applied_at, execution_ms "
                "FROM schema_migrations ORDER BY version"
            ))
        shutil.copyfile(SOURCE_MIGRATIONS / migration7.name, migration7)
        result = bootstrap_database(second, self.migrations)
        self.assertEqual(result.migration_result.applied_versions, (7,))
        with database_connection(second) as connection:
            later = tuple(tuple(row) for row in connection.execute(
                "SELECT version, name, checksum_sha256, applied_at, execution_ms "
                "FROM schema_migrations ORDER BY version"
            ))
            self.assertEqual(later[:6], original)
            self.assertEqual(connection.execute("SELECT name FROM categories WHERE slug='preserve'").fetchone()[0], "Preserve")
            self.assertEqual(run_integrity_check(connection), ("ok",))
            self.assertEqual(run_foreign_key_check(connection), ())

    def test_constraints_and_category_scope(self) -> None:
        self.bootstrap()
        script_category = self.category()
        ticket_category = self.category("TICKET")
        self.script("first", category_id=script_category, enabled=None)
        with database_connection(self.database) as connection:
            self.assertEqual(connection.execute("SELECT is_enabled FROM scripts WHERE script_code='first'").fetchone()[0], 0)
            for sql, values in (
                ("UPDATE scripts SET script_code=? WHERE script_code='first'", ("",)),
                ("UPDATE scripts SET name=? WHERE script_code='first'", ("  ",)),
                ("UPDATE scripts SET relative_path=? WHERE script_code='first'", (None,)),
                ("UPDATE scripts SET is_enabled=? WHERE script_code='first'", (2,)),
                ("UPDATE scripts SET category_id=? WHERE script_code='first'", (99999,)),
                ("UPDATE scripts SET timeout_seconds=? WHERE script_code='first'", (0,)),
            ):
                with self.subTest(sql=sql, values=values), self.assertRaises(sqlite3.IntegrityError):
                    connection.execute(sql, values)
        with self.assertRaises(sqlite3.IntegrityError):
            self.script("FIRST", relative_path="PowerShell/Reports/other.ps1")
        self.script("wrong-scope", category_id=ticket_category)
        eligible = ScriptRepository(self.database).list_scripts(include_disabled=True)
        self.assertEqual(eligible[0].script_code, "first")
        self.assertEqual(eligible[0].category_name, "Script")
        self.assertIsNone(ScriptRepository(self.database).get_script("wrong-scope"))

    def test_repository_enabled_only_exact_lookup_order_and_read_only(self) -> None:
        self.bootstrap()
        self.script("z", name="Zulu")
        self.script("a", name="alpha")
        self.script("disabled", enabled=None)
        repo = ScriptRepository(self.database)
        with database_connection(self.database) as connection:
            before = tuple(connection.iterdump())
        self.assertEqual(tuple(row.script_code for row in repo.list_scripts()), ("a", "z"))
        self.assertEqual(tuple(row.script_code for row in repo.list_scripts(include_disabled=True)), ("a", "disabled", "z"))
        self.assertEqual(repo.get_script("A").script_code, "a")
        self.assertIsNone(repo.get_script("disabled"))
        self.assertIsNone(repo.get_script("absent"))
        self.assertIsNone(repo.get_script("a' OR 1=1 --"))
        with database_connection(self.database) as connection:
            after = tuple(connection.iterdump())
        self.assertEqual(before, after)
        self.assertFalse(any(hasattr(repo, name) for name in ("update_script", "delete_script")))

    def test_service_statuses_and_no_content_reads(self) -> None:
        self.bootstrap()
        self.script("ready", relative_path="PowerShell/Diagnostics/ready.ps1")
        self.script("missing", relative_path="PowerShell/Reports/missing.ps1")
        self.script("invalid", relative_path="PowerShell/Modules/invalid.txt")
        self.script("disabled", enabled=None)
        script_file = self.root / "PowerShell" / "Diagnostics" / "ready.ps1"
        script_file.parent.mkdir(parents=True)
        script_file.write_text("throw 'must never run or read'", encoding="utf-8")
        service = ScriptService(ScriptRepository(self.database), self.root)
        with database_connection(self.database) as connection:
            before = tuple(connection.iterdump())
        with patch.object(Path, "open", side_effect=AssertionError("script content opened")), \
             patch.object(subprocess, "run", side_effect=AssertionError("PowerShell executed")), \
             patch.object(subprocess, "Popen", side_effect=AssertionError("PowerShell executed")):
            entries = {entry.metadata.script_code: entry for entry in service.list_scripts()}
            self.assertEqual(service.get_script("ready").file_status, AVAILABLE)
        self.assertEqual({code: entry.file_status for code, entry in entries.items()}, {
            "ready": AVAILABLE, "missing": MISSING, "invalid": INVALID_REFERENCE,
        })
        self.assertIsNone(service.get_script("disabled"))
        self.assertIsNone(service.get_script("absent"))
        with database_connection(self.database) as connection:
            self.assertEqual(tuple(connection.iterdump()), before)

    def test_service_database_error_is_safe(self) -> None:
        class FailedRepository:
            def list_scripts(self, *, text_query=None) -> None:
                raise sqlite3.OperationalError("private database detail")

        with self.assertRaisesRegex(ScriptReadError, "Could not load the script catalog") as result:
            ScriptService(FailedRepository(), self.root).list_scripts()
        self.assertNotIn("private", str(result.exception))

    def test_text_search_fields_scope_order_and_default_compatibility(self):
        self.bootstrap()
        self.script("n01", name="Zulu needle")
        self.script("needle.code", name="Beta")
        self.script("d01", name="alpha", description="Purpose: needle")
        self.script("needle.multi", name="Delta needle", description="needle")
        self.script("null", name="Other")
        self.script("disabled", name="needle", enabled=0)
        self.script("wrong", name="needle", category_id=self.category("TICKET"))
        repo = ScriptRepository(self.database)
        expected = ("d01", "needle.code", "needle.multi", "n01")
        self.assertEqual(tuple(row.script_code for row in repo.list_scripts(text_query=" NEEDLE ")), expected)
        self.assertEqual(tuple(row.metadata.script_code for row in
                               ScriptService(repo, self.root).list_scripts(text_query="needle")), expected)
        self.assertEqual(len(set(expected)), len(expected))
        self.assertEqual(repo.list_scripts(text_query=" \t\n "), repo.list_scripts())
        self.assertEqual(repo.list_scripts(text_query=""), repo.list_scripts())
        self.assertEqual(repo.list_scripts(text_query=None), repo.list_scripts())
        self.assertEqual(len(repo.list_scripts(include_disabled=True, text_query="needle")), 5)
        self.assertEqual(len(ScriptService(repo, self.root).list_registered_scripts()), 6)

    def test_text_search_literals_null_and_unicode_matching(self):
        self.bootstrap()
        tokens = ("%", "_", "\\", "'", "' OR 1=1 --")
        for i, token in enumerate(tokens):
            self.script(f"literal{i}", name=f"Literal {i}", description=f"prefix {token} suffix")
        self.script("plain", name="Unrelated", description=None)
        self.script("unicode", name="é")
        repo = ScriptRepository(self.database)
        for i, token in enumerate(tokens):
            with self.subTest(token=token):
                rows = repo.list_scripts(text_query=token)
                # A lone quote also literally occurs inside the SQL-looking fixture.
                expected = ("literal3", "literal4") if token == "'" else (f"literal{i}",)
                self.assertEqual(tuple(row.script_code for row in rows), expected)
        self.assertEqual(repo.list_scripts(text_query="É"), ())
        self.assertEqual(tuple(row.script_code for row in repo.list_scripts(text_query="é")), ("unicode",))

    def test_invalid_search_rejected_before_database_access(self):
        repo = ScriptRepository(self.database)
        service = ScriptService(repo, self.root)
        for value in (True, 42, b"text", [], "needle\x00missing"):
            with self.subTest(value=value), \
                    patch("f7hub.repositories.script_repository.database_connection") as connect:
                with self.assertRaises(ValueError):
                    repo.list_scripts(text_query=value)
                connect.assert_not_called()
            with self.subTest(service_value=value), patch.object(repo, "list_scripts") as read:
                with self.assertRaises(ScriptValidationError):
                    service.list_scripts(text_query=value)
                read.assert_not_called()

    def test_search_query_only_no_writes_content_reads_or_processes(self):
        self.bootstrap()
        self.script("ready", description="needle", relative_path="PowerShell/Diagnostics/ready.ps1")
        target = self.root / "PowerShell" / "Diagnostics" / "ready.ps1"
        target.parent.mkdir(parents=True)
        target.write_text("# never read by search", encoding="utf-8")
        with database_connection(self.database) as connection:
            before = tuple(connection.iterdump())

        @contextmanager
        def query_only(path):
            with database_connection(path) as connection:
                connection.execute("PRAGMA query_only = ON")
                yield connection

        with patch("f7hub.repositories.script_repository.database_connection", query_only), \
                patch.object(Path, "open", side_effect=AssertionError("source opened")), \
                patch.object(subprocess, "run", side_effect=AssertionError("process launched")), \
                patch.object(subprocess, "Popen", side_effect=AssertionError("process launched")):
            entries = ScriptService(ScriptRepository(self.database), self.root).list_scripts(text_query="needle")
            self.assertEqual(entries[0].file_status, AVAILABLE)
        with database_connection(self.database) as connection:
            self.assertEqual(tuple(connection.iterdump()), before)
            self.assertEqual(run_integrity_check(connection), ("ok",))
            self.assertEqual(run_foreign_key_check(connection), ())

    def test_path_rejections_and_access_failure(self) -> None:
        valid = self.root / "PowerShell" / "Modules" / "safe.ps1"
        valid.parent.mkdir(parents=True)
        valid.write_text("", encoding="utf-8")
        self.assertEqual(inspect_script_reference(self.root, "PowerShell/Modules/safe.ps1"), AVAILABLE)
        self.assertEqual(inspect_script_reference(self.root, "PowerShell/Modules/gone.ps1"), MISSING)
        invalid = (
            "C:\\PowerShell\\Diagnostics\\x.ps1",
            "C:x.ps1", "\\\\server\\share\\x.ps1", "\\PowerShell\\Diagnostics\\x.ps1",
            "/PowerShell/Diagnostics/x.ps1", "PowerShell/Diagnostics/../Reports/x.ps1",
            "PowerShell/Diagnostics/x.ps1:ads", "PowerShell/Reports/x.txt",
            "Other/Reports/x.ps1", "PowerShell/Other/x.ps1",
            "PowerShell/Diagnostics/CON.ps1", "PowerShell/Diagnostics/x.ps1.",
        )
        for reference in invalid:
            with self.subTest(reference=reference):
                self.assertEqual(inspect_script_reference(self.root, reference), INVALID_REFERENCE)
        with patch.object(Path, "stat", side_effect=PermissionError):
            self.assertEqual(inspect_script_reference(self.root, "PowerShell/Modules/safe.ps1"), INACCESSIBLE)
        self.assertEqual(inspect_script_reference(self.root, "PowerShell/Modules"), INVALID_REFERENCE)
        (self.root / "PowerShell" / "Modules" / "folder.ps1").mkdir()
        self.assertEqual(inspect_script_reference(self.root, "PowerShell/Modules/folder.ps1"), INVALID_REFERENCE)

    def test_symlink_escape_is_invalid(self) -> None:
        outside = self.root / "outside.ps1"
        outside.write_text("", encoding="utf-8")
        inside = self.root / "PowerShell" / "Diagnostics"
        inside.mkdir(parents=True)
        link = inside / "escape.ps1"
        try:
            link.symlink_to(outside)
        except (OSError, NotImplementedError):
            original_resolve = Path.resolve

            def escaped_resolve(path: Path, *, strict: bool = False) -> Path:
                if path == link:
                    return outside
                return original_resolve(path, strict=strict)

            with patch.object(Path, "resolve", escaped_resolve):
                self.assertEqual(inspect_script_reference(self.root, "PowerShell/Diagnostics/escape.ps1"), INVALID_REFERENCE)
            return
        self.assertEqual(inspect_script_reference(self.root, "PowerShell/Diagnostics/escape.ps1"), INVALID_REFERENCE)

    def test_approved_folder_alias_outside_is_invalid(self) -> None:
        source = self.root / "outside"
        source.mkdir()
        (source / "file.ps1").write_text("", encoding="utf-8")
        shell_root = self.root / "PowerShell"
        shell_root.mkdir()
        alias = shell_root / "Diagnostics"
        try:
            alias.symlink_to(source, target_is_directory=True)
        except (OSError, NotImplementedError):
            original_resolve = Path.resolve

            def escaped_resolve(path: Path, *, strict: bool = False) -> Path:
                if path == alias or path == alias / "file.ps1":
                    return source if path == alias else source / "file.ps1"
                return original_resolve(path, strict=strict)

            with patch.object(Path, "resolve", escaped_resolve):
                self.assertEqual(inspect_script_reference(self.root, "PowerShell/Diagnostics/file.ps1"), INVALID_REFERENCE)
            return
        self.assertEqual(inspect_script_reference(self.root, "PowerShell/Diagnostics/file.ps1"), INVALID_REFERENCE)


if __name__ == "__main__":
    unittest.main()
