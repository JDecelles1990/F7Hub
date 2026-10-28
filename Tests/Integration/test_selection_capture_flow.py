"""Real service, consent and isolated SQLite; acquisition is synthetic."""

import threading
from unittest.mock import patch

from Tests.Database.test_clipboard_consent import _ConsentFixture
from f7hub.domain.clipboard import ClipboardValidationError
from f7hub.domain.clipboard_settings import WORKFLOW_ENABLED


class SelectionCaptureFlowTests(_ConsentFixture):
    def receive(self, text='NEW SELECTED TEXT', acquire=None):
        return self.service.capture_active_selection(acquire or (lambda: text), threading.Event())

    def test_no_consent_is_preview_only_with_zero_records(self):
        with self.assertNoLogs(level='DEBUG'):
            result = self.receive()
        self.assertEqual((result.text, result.persistence), ('NEW SELECTED TEXT', 'PREVIEW_ONLY'))
        self.assertNotIn('NEW SELECTED TEXT', repr(result))
        self.assertEqual(self.counts(), (0, 0, 0))

    def test_saved_true_without_affirmative_consent_does_not_persist(self):
        self.settings.apply({WORKFLOW_ENABLED: True}, expected_revision=0)
        self.assertEqual(self.receive().persistence, 'PREVIEW_ONLY')
        self.assertEqual(self.counts(), (0, 0, 0))

    def test_explicit_consent_persists_through_existing_service(self):
        self.grant()
        self.assertEqual(self.receive().persistence, 'PERSISTED')
        self.assertEqual(self.counts(), (1, 1, 1))
        self.assertEqual(self.receive().persistence, 'PERSISTED')
        self.assertEqual(self.counts(), (1, 2, 2))  # Genuine new press reuses Item, creates Event.

    def test_secret_and_sensitive_never_preview_or_persist(self):
        self.grant()
        for text in ('password=synthetic-only', 'lab@example.invalid'):
            with self.assertNoLogs(level='DEBUG'), self.assertRaises(ClipboardValidationError): self.receive(text)
        self.assertEqual(self.counts(), (0, 0, 0))

    def test_empty_and_malformed_never_persist(self):
        self.grant()
        for text in ('', ' ', 'bad\0text'):
            with self.assertRaises(ClipboardValidationError): self.receive(text)
        self.assertEqual(self.counts(), (0, 0, 0))

    def test_failed_acquisition_never_calls_writer(self):
        self.grant()
        def fail(): raise RuntimeError('synthetic failure')
        with patch.object(self.service, 'capture_manual_text') as writer:
            with self.assertRaises(RuntimeError): self.receive(acquire=fail)
            writer.assert_not_called()
        self.assertEqual(self.counts(), (0, 0, 0))

    def test_revocation_during_copy_denies_persistence(self):
        self.grant()
        def acquire():
            self.settings.apply({WORKFLOW_ENABLED: False}, expected_revision=1)
            return 'NEW SELECTED TEXT'
        self.assertEqual(self.receive(acquire=acquire).persistence, 'NOT_SAVED')
        self.assertEqual(self.counts(), (0, 0, 0))

    def test_new_grant_during_copy_does_not_retarget_to_persistence(self):
        def acquire():
            self.grant()
            return 'NEW SELECTED TEXT'
        self.assertEqual(self.receive(acquire=acquire).persistence, 'PREVIEW_ONLY')
        self.assertEqual(self.counts(), (0, 0, 0))

    def test_cancelled_copy_has_no_service_success(self):
        event = threading.Event()
        def acquire():
            event.set()
            return 'NEW SELECTED TEXT'
        with self.assertRaises(ClipboardValidationError):
            self.service.capture_active_selection(acquire, event)
        self.assertEqual(self.counts(), (0, 0, 0))

    def test_bootstrapped_f7hub_receives_preview_via_existing_lifecycle(self):
        import time
        from PySide6.QtWidgets import QApplication
        from f7hub.app.bootstrap import bootstrap_application
        from Tests.Database.clipboard_fixtures import PROJECT_ROOT
        from Tests.GUI.test_selection_capture import FakeHotkeyAPI
        app = QApplication.instance() or QApplication([])
        with patch('f7hub.services.mochi_service.MochiService.automatic_start', return_value=False):
            context = bootstrap_application(project_root=PROJECT_ROOT, database_path=self.database_path)
        window = context.main_window
        capture = window.selection_capture
        capture.api = FakeHotkeyAPI()
        try:
            deadline = time.monotonic() + 5
            while window.runner.busy and time.monotonic() < deadline:
                app.processEvents()
                time.sleep(.005)
            self.assertFalse(window.runner.busy)
            window.lifecycle.start()
            self.assertTrue(capture.registered)
            self.assertTrue(capture.trigger())
            while capture.busy and time.monotonic() < deadline:
                app.processEvents()
                capture.poll()
                time.sleep(.005)
            self.assertFalse(capture.busy)
            self.assertIn('NEW SELECTED TEXT', window.statusBar().currentMessage())
            self.assertIn('not saved', window.statusBar().currentMessage())
            self.assertEqual(self.counts(), (0, 0, 0))
            self.assertTrue(window.cleanup_shutdown())
            self.assertFalse(capture.registered)
        finally:
            window.lifecycle.recovery_timer.stop()
            window.lifecycle.tray.hide()
            window.cleanup_shutdown()
            window.deleteLater()
            app.processEvents()
