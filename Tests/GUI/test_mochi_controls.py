import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PySide6.QtCore import QObject, Signal
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from f7hub.gui.main_window import MainWindow
from f7hub.gui.mochi_settings_dialog import MochiSettingsDialog
from f7hub.services.mochi_service import MochiService
from f7hub.infrastructure.mochi_gateway import MochiGateway
from f7hub.app.bootstrap import bootstrap_application


class FakeGateway(QObject):
    changed = Signal(object)
    availability = Signal(str)
    busy_changed = Signal(bool)
    completed = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.starts, self.requests, self.greetings = [], [], []
        self.closed = False

    def start(self, session, supplier, **options):
        self.starts.append(options)
        self.greetings.append(supplier())
        return True

    def send(self, command):
        self.requests.append(command)
        self.busy_changed.emit(True)
        return True

    def close(self):
        self.closed = True


class TicketFixture:
    def list_tickets(self, **_kwargs):
        return ()


class MochiUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.gateway = FakeGateway()
        self.service = MochiService(self.gateway)
        self.window = MainWindow(TicketFixture(), mochi_service=self.service)
        self.addCleanup(self.dispose)

    def dispose(self):
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    def ready(self):
        self.gateway.availability.emit('AVAILABLE')
        self.gateway.changed.emit(dict(behavior='IDLE', visibility='VISIBLE', paused=False,
                                       selected_animation='IDLE', frame=0, checkout_id='fixture'))

    def test_no_start_before_display_and_one_attempt_before_scheduling(self):
        self.assertEqual(self.gateway.starts, [])
        self.assertFalse(self.service.automatic_attempt_started)
        self.window.show()
        self.assertTrue(self.service.automatic_attempt_started)
        self.assertEqual(self.gateway.starts, [])
        QTest.qWait(10)
        self.assertEqual(len(self.gateway.starts), 1)
        for _ in range(3):
            self.window.hide()
            self.window.show()
            self.window.activateWindow()
            self.window.showMinimized()
            self.window.showNormal()
        QTest.qWait(10)
        self.assertEqual(len(self.gateway.starts), 1)

    def test_one_modeless_dialog_reopen_and_controller_lifetime(self):
        self.window.show()
        QTest.qWait(10)
        self.window.show_mochi_settings()
        dialog = self.window._mochi_dialog
        self.assertFalse(dialog.isModal())
        self.window.show_mochi_settings()
        self.assertIs(self.window._mochi_dialog, dialog)
        dialog.close()
        self.assertFalse(self.gateway.closed)
        self.assertEqual(self.service._subscribers, [])
        self.window.show_mochi_settings()
        self.assertIsNot(self.window._mochi_dialog, dialog)
        self.assertEqual(len(self.gateway.starts), 1)
        self.assertEqual(self.gateway.greetings, [True])

    def test_pending_controls_close_and_replacement_ignore_old_callback(self):
        self.ready()
        self.window.show_mochi_settings()
        old = self.window._mochi_dialog
        callback = old.render
        old.buttons['wave'].click()
        self.assertTrue(self.service.busy)
        self.assertFalse(old.buttons['wave'].isEnabled())
        self.assertTrue(self.window.pages.isEnabled())
        self.assertTrue(old.findChild(QObject, 'mochi_close').isEnabled())
        old.close()
        self.window.show_mochi_settings()
        new = self.window._mochi_dialog
        old_text = new.status.text()
        callback(self.service)
        self.assertEqual(new.status.text(), old_text)
        self.gateway.busy_changed.emit(False)
        self.gateway.completed.emit('wave', 'CHANGED')
        self.assertTrue(new.buttons['wave'].isEnabled())
        self.assertFalse(self.gateway.closed)

    def test_controls_snapshot_pause_resume_and_uncertain_feedback(self):
        self.ready()
        self.window.show_mochi_settings()
        dialog = self.window._mochi_dialog
        self.gateway.changed.emit({**self.service.snapshot, 'behavior':'PAUSED', 'paused':True})
        self.assertEqual(dialog.buttons['pause'].text(), 'Resume')
        self.assertFalse(dialog.buttons['wave'].isEnabled())
        dialog.buttons['pause'].click()
        self.assertEqual(self.gateway.requests, ['resume'])
        self.gateway.completed.emit('resume', 'UNCERTAIN')
        self.assertIn('could not be confirmed', dialog.status.text())

    def test_atomic_consumption_and_new_session(self):
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: self.service.consume_greeting(), range(32)))
        self.assertEqual(results.count(True), 1)
        self.assertFalse(self.service.consume_greeting())
        other = MochiService(FakeGateway())
        self.assertNotEqual(other.session_id, self.service.session_id)
        self.assertTrue(other.consume_greeting())

    def test_consumed_before_send_never_renewed_failure_restart_or_eviction(self):
        self.service.automatic_start()
        for _ in range(20):
            self.service.start_show()
        self.assertEqual(self.gateway.greetings, [True]+[False]*20)
        self.assertTrue(self.service.greeting_consumed)
        self.service.command('wave')
        self.assertTrue(self.service.greeting_consumed)

    def test_manual_exit_suppresses_automatic_but_explicit_start_allowed(self):
        self.service.command('exit')
        self.assertFalse(self.service.automatic_start())
        self.assertTrue(self.service.start_show())
        self.assertEqual(len(self.gateway.starts), 1)

    def test_f7hub_close_closes_controller_not_pet_command(self):
        self.window.close()
        self.assertTrue(self.gateway.closed)
        self.assertNotIn('exit', self.gateway.requests)


class MochiStartupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.gateway = MochiGateway(Path(self.temp.name))
        self.service = MochiService(self.gateway)
        self.addCleanup(self.service.close)

    def test_launch_failure_and_coalescing_leave_navigation_usable(self):
        window = MainWindow(TicketFixture(), mochi_service=self.service)
        self.addCleanup(window.deleteLater)
        def failed_launch():
            self.assertFalse(self.service.start_show())
            return False
        with patch.object(self.gateway, 'launch', side_effect=failed_launch) as launch:
            self.service.automatic_start()
            QTest.qWait(30)
            self.assertEqual(launch.call_count, 1)
            self.assertEqual(self.service.availability, 'LAUNCH_FAILED')
            self.assertTrue(window.pages.isEnabled())
            self.assertFalse(self.service.automatic_start())

    def test_timeout_one_launch_no_automatic_retry(self):
        self.gateway.readiness.setInterval(75)
        with patch.object(self.gateway, 'launch', return_value=True) as launch:
            self.service.automatic_start()
            QTest.qWait(130)
            self.assertEqual(self.service.availability, 'TIMEOUT')
            self.assertEqual(launch.call_count, 1)
            self.assertFalse(self.service.automatic_start())
            self.service.start_show()
            QTest.qWait(130)
            self.assertEqual(launch.call_count, 2)

    def test_uncertain_exit_never_replays_or_relaunches(self):
        from f7hub.infrastructure.mochi_channel import Channel
        from PySide6.QtNetwork import QLocalSocket
        self.gateway.session_id = self.service.session_id
        self.gateway.greeting_supplier = self.service.consume_greeting
        self.gateway.socket = QLocalSocket(self.gateway)
        self.gateway.channel = Channel(self.gateway.socket, self.gateway)
        self.gateway.pending = ('request', 'exit')
        with patch.object(self.gateway, 'launch') as launch:
            self.gateway._timeout()
            QTest.qWait(20)
            self.assertEqual(self.service.last_outcome, 'UNCERTAIN')
            launch.assert_not_called()

    def test_explicit_retry_checks_actual_socket_state_after_runtime_exit(self):
        from PySide6.QtNetwork import QLocalSocket
        self.gateway.socket = QLocalSocket(self.gateway)
        self.gateway.attached = True
        with patch.object(self.gateway, 'launch', return_value=False) as launch:
            self.service.start_show()
            QTest.qWait(25)
            self.assertEqual(launch.call_count, 1)
            self.assertEqual(self.service.availability, 'LAUNCH_FAILED')

    def test_explicit_start_clears_failed_reconciliation_intent(self):
        self.gateway._reconcile = True
        with patch.object(self.gateway, '_connect'):
            self.service.start_show()
            self.assertFalse(self.gateway._reconcile)
            self.assertTrue(self.gateway._want_show)

    def test_detached_launch_uses_interpreter_absolute_entry_and_argument_array(self):
        import sys
        with patch('f7hub.infrastructure.mochi_gateway.QProcess.startDetached', return_value=(True, 123)) as launch:
            self.assertTrue(self.gateway.launch())
            launch.assert_called_once_with(sys.executable, ['-B', str(Path(self.temp.name)/'Mochi/src/main.py')], str(Path(self.temp.name).resolve()))
            self.assertEqual(self.gateway.launched_pid, 123)

    def test_bootstrap_composes_without_start(self):
        root = Path(__file__).resolve().parents[2]
        with patch('f7hub.infrastructure.mochi_gateway.MochiGateway.launch') as launch:
            context = bootstrap_application(project_root=root, database_path=Path(self.temp.name)/'fixture.db')
            self.addCleanup(context.main_window.deleteLater)
            self.addCleanup(context.mochi_service.close)
            self.assertIs(context.main_window.mochi_service, context.mochi_service)
            self.assertFalse(context.mochi_service.automatic_attempt_started)
            self.assertIsNone(context.mochi_service.gateway.socket)
            launch.assert_not_called()

    def test_mochi_identity_failure_does_not_break_f7hub(self):
        root = Path(__file__).resolve().parents[2]
        with patch('f7hub.infrastructure.mochi_gateway.CheckoutIdentity.from_root', side_effect=OSError('fixture')):
            context = bootstrap_application(project_root=root, database_path=Path(self.temp.name)/'failure.db')
            self.addCleanup(context.main_window.deleteLater)
            self.addCleanup(context.mochi_service.close)
            context.mochi_service.automatic_start()
            self.assertEqual(context.mochi_service.availability, 'UNAVAILABLE')
            self.assertTrue(context.main_window.pages.isEnabled())
