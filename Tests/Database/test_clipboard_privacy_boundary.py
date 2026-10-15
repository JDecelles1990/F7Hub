"""S05 negative boundaries and reproducible Settings provenance-gap evidence.

No real consent authority is implemented here. D02 default unavailability must
hold even when the independently callable assessment reports PERMITTED.
"""

from unittest.mock import patch

from f7hub.domain.clipboard import (
    AdmittedManualText, ClipboardCaptureCommand, ClipboardPersistenceError,
    ClipboardPersistenceCode as Code,
)
from f7hub.domain.clipboard_privacy import assess_manual_text, ClipboardPrivacyFinding as F
from f7hub.domain.clipboard_settings import CLIPBOARD_SETTING_DEFINITIONS, WORKFLOW_ENABLED
from f7hub.infrastructure.database import bootstrap_database, database_connection, validate_database_integrity
from f7hub.repositories.clipboard_repository import ClipboardRepository
from f7hub.repositories.settings_repository import SettingsRepository
from f7hub.services.clipboard_service import ClipboardService
from f7hub.services.settings_service import SettingsService
from Tests.Database.clipboard_fixtures import ClipboardDatabaseTestCase, PROJECT_ROOT


class ClipboardPrivacyBoundaryTests(ClipboardDatabaseTestCase):
    def settings(self, path=None):
        return SettingsService(SettingsRepository(path or self.database_path), CLIPBOARD_SETTING_DEFINITIONS)

    def assert_no_capture(self, text="Synthetic eligible ordinary text"):
        service = ClipboardService(ClipboardRepository(self.database_path))
        context = service.open_admission_context("synthetic-s05")
        command = ClipboardCaptureCommand(service.new_operation(context), AdmittedManualText(text))
        before = self.database_path.read_bytes()
        with self.assertNoLogs(level="DEBUG"):
            with self.assertRaises(ClipboardPersistenceError) as caught:
                service.capture_manual_text(context, command)
        self.assertEqual(caught.exception.code, Code.ADMISSION_UNAVAILABLE)
        self.assertEqual(str(caught.exception), "Clipboard persistence: ADMISSION_UNAVAILABLE.")
        self.assertIsNone(caught.exception.__context__)
        self.assertEqual(self.database_path.read_bytes(), before)
        with database_connection(self.database_path, read_only=True) as connection:
            for table in ("clipboard_items", "clipboard_capture_events", "clipboard_operation_receipts"):
                self.assertEqual(connection.execute("SELECT count(*) FROM " + table).fetchone()[0], 0)
            self.assertEqual(validate_database_integrity(connection), (("ok",), ()))
            self.assertEqual(connection.execute("PRAGMA foreign_keys").fetchone()[0], 1)
            self.assertEqual(connection.execute("PRAGMA busy_timeout").fetchone()[0], 5000)

    def test_disabled_and_programmatically_enabled_preferences_cannot_activate_capture(self):
        self.assert_no_capture()
        self.settings().apply({entry.key: True for entry in CLIPBOARD_SETTING_DEFINITIONS}, expected_revision=0)
        self.assert_no_capture()

    def test_imported_enablement_and_restart_cannot_activate_capture(self):
        with database_connection(self.database_path) as connection:
            connection.execute("INSERT INTO settings_user_overrides VALUES (?, 'BOOLEAN', 'true')", (WORKFLOW_ENABLED,))
            connection.execute("UPDATE settings_state SET revision=1")
            connection.commit()
        self.assertTrue(self.settings().get_snapshot().get(WORKFLOW_ENABLED).value)
        self.assert_no_capture()
        self.assert_no_capture()  # New service/context each time; no permission survives restart.

    def test_invalid_settings_stay_disabled_and_capture_unavailable(self):
        with database_connection(self.database_path) as connection:
            connection.execute("PRAGMA ignore_check_constraints=ON")
            connection.execute("INSERT INTO settings_user_overrides VALUES (?, 'BOOLEAN', 'invalid')", (WORKFLOW_ENABLED,))
            connection.commit()
        self.assertFalse(self.settings().get_snapshot().get(WORKFLOW_ENABLED).value)
        self.assert_no_capture()

    def test_unavailable_settings_do_not_supply_default_capture_permission(self):
        with database_connection(self.database_path) as connection:
            connection.execute("DELETE FROM settings_state")
            connection.commit()
        self.assertFalse(self.settings().get_snapshot().storage_available)
        self.assert_no_capture()

    def test_assessment_alone_cannot_grant_permission_and_rejected_text_has_zero_effects(self):
        for index, (text, finding) in enumerate((
            ("Synthetic ordinary text", F.PERMITTED),
            ("password=synthetic-rejected-sentinel", F.POSSIBLE_SECRET),
            ("Authorization: Bearer synthetic-rejected-sentinel", F.POSSIBLE_SECRET),
            ("-----BEGIN PRIVATE KEY-----\nSYNTHETIC NOT A KEY", F.POSSIBLE_SECRET),
            ("lab@example.invalid", F.NEEDS_REVIEW),
        )):
            with self.subTest(profile=index):
                self.assertEqual(assess_manual_text(AdmittedManualText(text)).finding, finding)
                self.assert_no_capture(text)
        with patch("f7hub.domain.clipboard_privacy._scan", side_effect=RuntimeError("synthetic-rejected-sentinel")):
            self.assertEqual(assess_manual_text(AdmittedManualText("Synthetic ordinary text")).finding,
                             F.ASSESSMENT_FAILED)
            self.assert_no_capture()

    def test_existing_settings_cannot_distinguish_apply_from_import_across_restart(self):
        # Reproduce the decision-gate gap using two temporary synthetic databases.
        # Setup invokes exactly this same general apply API; no origin parameter exists.
        saved = self.settings().apply({WORKFLOW_ENABLED: True}, expected_revision=0).snapshot
        imported_path = self.root / "imported.db"
        bootstrap_database(imported_path, PROJECT_ROOT / "Database/Migrations")
        with database_connection(imported_path) as connection:
            connection.execute("INSERT INTO settings_user_overrides VALUES (?, 'BOOLEAN', 'true')", (WORKFLOW_ENABLED,))
            connection.execute("UPDATE settings_state SET revision=1")
            connection.commit()
        self.assertEqual(saved, self.settings().get_snapshot())
        self.assertEqual(saved, self.settings(imported_path).get_snapshot())
        self.assertNotEqual(ClipboardRepository(imported_path).database_scope,
                            ClipboardRepository(self.database_path).database_scope)
        self.assert_no_capture()

    def test_workflow_revocation_preserves_existing_history_and_denies_future_capture(self):
        from Tests.Database.clipboard_fixtures import seed_item
        with database_connection(self.database_path) as connection:
            seed_item(connection, retention_intent="SAVED", expires_at=None)
            before = tuple(connection.execute("SELECT * FROM clipboard_items").fetchall())
            events = tuple(connection.execute("SELECT * FROM clipboard_capture_events").fetchall())
        settings = self.settings()
        settings.apply({WORKFLOW_ENABLED: True}, expected_revision=0)
        settings.apply({WORKFLOW_ENABLED: False}, expected_revision=1)
        with database_connection(self.database_path, read_only=True) as connection:
            self.assertEqual(tuple(connection.execute("SELECT * FROM clipboard_items").fetchall()), before)
            self.assertEqual(tuple(connection.execute("SELECT * FROM clipboard_capture_events").fetchall()), events)
            self.assertEqual(validate_database_integrity(connection), (("ok",), ()))
        service = ClipboardService(ClipboardRepository(self.database_path))
        context = service.open_admission_context("synthetic-s05")
        command = ClipboardCaptureCommand(service.new_operation(context), AdmittedManualText("Synthetic future note"))
        before_bytes = self.database_path.read_bytes()
        with self.assertRaises(ClipboardPersistenceError) as caught:
            service.capture_manual_text(context, command)
        self.assertEqual(caught.exception.code, Code.ADMISSION_UNAVAILABLE)
        self.assertEqual(self.database_path.read_bytes(), before_bytes)
        # This does not establish a consent/commit race mechanism; B remains blocked.
