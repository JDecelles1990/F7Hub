"""Fail-closed source reads at the ScriptService boundary."""

from __future__ import annotations

import hashlib
import io
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from f7hub.infrastructure.database import bootstrap_database, database_connection
from f7hub.repositories.script_repository import ScriptRepository
from f7hub.services.script_service import ScriptCopyError, ScriptService


ROOT = Path(__file__).resolve().parents[2]
STAMP = "2026-09-30T00:00:00.000Z"
CODE = "test.script"
REFERENCE = "PowerShell/Diagnostics/test.ps1"


class VerifiedScriptCopyTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        migrations = self.root / "migrations"
        migrations.mkdir()
        for source in (ROOT / "Database/Migrations").glob("*.sql"):
            if int(source.name[:4]) <= 7:
                shutil.copyfile(source, migrations / source.name)
        self.database = self.root / "test.db"
        bootstrap_database(self.database, migrations)
        self.script = self.root / REFERENCE
        self.script.parent.mkdir(parents=True)
        self.content = b"# exact CRLF\r\nWrite-Output 'copy only'\r\n"
        self.script.write_bytes(self.content)
        self.approved = hashlib.sha256(self.content).hexdigest()
        with database_connection(self.database) as connection:
            connection.execute(
                "INSERT INTO scripts (script_code,name,relative_path,script_type,checksum_sha256,"
                "is_enabled,created_at,updated_at) VALUES (?, 'Test', ?, 'DIAGNOSTIC', ?, 1, ?, ?)",
                (CODE, REFERENCE, self.approved, STAMP, STAMP),
            )
        self.service = ScriptService(ScriptRepository(self.database), self.root)

    def update(self, **values):
        with database_connection(self.database) as connection:
            for column, value in values.items():
                connection.execute(f"UPDATE scripts SET {column}=? WHERE script_code=?", (value, CODE))

    def blocked(self, code):
        with self.assertRaises(ScriptCopyError) as result:
            self.service.read_verified_script(CODE)
        self.assertEqual(result.exception.code, code)
        self.assertNotIn(str(self.root), str(result.exception))

    def test_success_decodes_the_one_read_buffer_without_normalizing(self):
        reads = []

        def open_once(path, mode):
            self.assertEqual(path, self.script)
            self.assertEqual(mode, "rb")
            reads.append(path)
            return io.BytesIO(self.content)

        with patch.object(Path, "open", autospec=True, side_effect=open_once):
            text = self.service.read_verified_script(CODE)
        self.assertEqual(reads, [self.script])
        self.assertEqual(text, self.content.decode("utf-8"))
        self.assertIn("\r\n", text)

    def test_unapproved_malformed_and_mismatched_checksums(self):
        for checksum in (None, "", "a" * 63, "z" * 64, " " + self.approved):
            with self.subTest(checksum=checksum):
                self.update(checksum_sha256=checksum)
                self.blocked("INTEGRITY_NOT_APPROVED")
        self.update(checksum_sha256="0" * 64)
        self.blocked("INTEGRITY_MISMATCH")
        self.update(checksum_sha256=self.approved.upper())
        self.assertEqual(self.service.read_verified_script(CODE), self.content.decode("utf-8"))
        self.script.write_bytes(self.content + b"# changed")
        self.blocked("INTEGRITY_MISMATCH")

    def test_invalid_utf8_is_blocked_after_matching_hash(self):
        self.script.write_bytes(b"\xff\xfe")
        self.update(checksum_sha256=hashlib.sha256(b"\xff\xfe").hexdigest())
        self.blocked("READ_FAILED")

    def test_missing_inaccessible_and_failed_read(self):
        self.script.unlink()
        self.blocked("FILE_UNAVAILABLE")
        self.script.write_bytes(self.content)
        with patch("f7hub.services.script_service.os.access", return_value=False):
            self.blocked("FILE_UNAVAILABLE")
        with patch.object(Path, "open", side_effect=PermissionError("private path")):
            self.blocked("READ_FAILED")

    def test_reference_escape_and_nonfile_are_blocked(self):
        for reference in (
            "PowerShell/Diagnostics/../Reports/test.ps1",
            "C:/outside.ps1", "//server/share/script.ps1",
            "PowerShell/Other/test.ps1", "PowerShell/Diagnostics/test.ps1:ads",
        ):
            with self.subTest(reference=reference):
                self.update(relative_path=reference)
                self.blocked("INVALID_REFERENCE")
        self.update(relative_path="PowerShell/Diagnostics/folder.ps1")
        (self.script.parent / "folder.ps1").mkdir()
        self.blocked("INVALID_REFERENCE")

    def test_disabled_unknown_and_repository_failure(self):
        self.update(is_enabled=0)
        self.blocked("SCRIPT_NOT_ELIGIBLE")
        with self.assertRaises(ScriptCopyError) as result:
            self.service.read_verified_script("unknown")
        self.assertEqual(result.exception.code, "SCRIPT_NOT_ELIGIBLE")
        with patch.object(ScriptRepository, "get_script", side_effect=RuntimeError("private database detail")):
            self.blocked("SCRIPT_NOT_ELIGIBLE")


if __name__ == "__main__":
    unittest.main()
