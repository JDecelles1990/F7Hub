from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from f7hub.infrastructure.database_paths import (
    DatabasePathError,
    resolve_development_database_path,
    resolve_runtime_database_path,
    local_profile_scope,
)


class DatabasePathTests(unittest.TestCase):
    def test_consent_profile_scope_is_local_and_missing_or_relative_denies(self):
        for value in ('', 'relative-profile'):
            with self.subTest(value=value), patch.dict(os.environ, {'LOCALAPPDATA':value}):
                with self.assertRaises(DatabasePathError):local_profile_scope()
        with tempfile.TemporaryDirectory() as directory,patch.dict(os.environ,{'LOCALAPPDATA':directory}):
            first=local_profile_scope()
            self.assertEqual(len(first),64)
            self.assertEqual(local_profile_scope(),first)
            self.assertNotIn(directory,first)

    def test_resolves_development_database_below_explicit_project_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project_root = Path(temporary_directory)

            database_path = resolve_development_database_path(project_root)

            self.assertEqual(
                database_path,
                project_root.resolve() / "Database" / "Dev" / "f7hub_dev.db",
            )

    def test_resolves_runtime_database_below_explicit_local_app_data(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            local_app_data = Path(temporary_directory)

            database_path = resolve_runtime_database_path(local_app_data)

            self.assertEqual(
                database_path,
                local_app_data.resolve() / "F7Hub" / "Data" / "f7hub.db",
            )

    def test_runtime_path_fails_when_local_app_data_is_unavailable(self) -> None:
        environment = dict(os.environ)
        environment.pop("LOCALAPPDATA", None)

        with patch.dict(os.environ, environment, clear=True):
            with self.assertRaises(DatabasePathError):
                resolve_runtime_database_path()

    def test_path_resolution_rejects_empty_input(self) -> None:
        with self.assertRaises(DatabasePathError):
            resolve_development_database_path("   ")


if __name__ == "__main__":
    unittest.main()

