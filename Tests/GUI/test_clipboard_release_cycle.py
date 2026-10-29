"""Deterministic key-cycle coordination with fake native effects; no live input."""
import os
import threading
import unittest
from unittest.mock import Mock, patch
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtWidgets import QApplication, QMainWindow
from f7hub.gui.selection_capture import SelectionCapture
from f7hub.services.clipboard_service import SelectionCaptureResult
from Tests.GUI.test_selection_capture import FakeHotkeyAPI


class CycleAPI(FakeHotkeyAPI):
    def __init__(self):
        super().__init__()
        self.capture_waiting = threading.Event()
        self.paste_waiting = threading.Event()
    def pin(self, target):
        self.sequences = [10, 11, 11]
        return 999
    def pin_paste(self, target): return 999
    def keys_down(self):
        if self.held: self.capture_waiting.set()
        return self.held
    def paste_keys_down(self):
        if self.held: self.paste_waiting.set()
        return self.held


class ClipboardReleaseCycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app = QApplication.instance() or QApplication([])
    def setUp(self):
        self.mode = patch.dict(os.environ, {'F7HUB_DEV_PASTE_TARGET_DIAGNOSTIC': '1'})
        self.mode.start(); self.addCleanup(self.mode.stop)
        self.window = QMainWindow(); self.api = CycleAPI(); self.service = Mock()
        self.service.capture_active_selection.side_effect = lambda acquire, cancel: SelectionCaptureResult(acquire())
        self.owner = SelectionCapture(self.window, self.service, api=self.api)
        self.owner.start(); self.owner.timer.stop()  # Explicitly schedule observations; no timer luck.
    def join_worker(self):
        worker = self.owner._worker
        if worker is not None:
            worker.join(2)
            self.assertFalse(worker.is_alive())
    def drain(self): self.join_worker(); self.owner.poll()
    def tearDown(self):
        self.api.held = False; self.owner.cancel(); self.drain()
        self.api.cleanup_ok = True; self.owner.close()
        self.window.deleteLater(); self.app.processEvents()
    def press(self, action):
        self.api.held = True
        waiting = self.api.capture_waiting if action == 'capture' else self.api.paste_waiting
        waiting.clear()
        self.assertTrue(self.owner.trigger(action=action))
        self.assertTrue(waiting.wait(1))
    def finish_before_next_down_without_gui_release_sample(self):
        self.api.held = False
        self.join_worker()  # Worker sees release; GUI never polls while keys are up.
        self.api.held = True
        self.owner.poll()  # New chord is already down when old completion is drained.
    def test_capture_then_paste_reuses_worker_release_observation(self):
        self.press('capture')
        self.finish_before_next_down_without_gui_release_sample()
        self.assertTrue(self.owner.trigger(action='paste'))
        self.api.held = False; self.drain()
        self.assertIn('TARGET_VALIDATED_AFTER_RELEASE', self.window.statusBar().currentMessage())
        self.service.paste_latest.assert_not_called()

    def test_initial_key_down_reserves_one_operation_then_waits_for_release(self):
        self.assertFalse(self.owner._release_required)
        self.press('paste')
        self.assertTrue(self.owner.busy)
        self.assertTrue(self.owner._release_required)
        self.assertFalse(self.owner._release_observed.is_set())
        self.assertFalse(self.owner.trigger(action='paste'))
        self.api.held = False; self.drain()
        self.assertFalse(self.owner.busy)
        self.assertFalse(self.owner._release_required)
        self.assertIn('TARGET_VALIDATED_AFTER_RELEASE', self.window.statusBar().currentMessage())
        self.assertEqual(self.service.mock_calls, [])
        self.assertEqual((self.api.sent, self.api.reads), (0, 0))

    def test_paste_then_capture_reuses_worker_release_observation(self):
        self.press('paste')
        self.finish_before_next_down_without_gui_release_sample()
        self.assertTrue(self.owner.trigger(action='capture'))
        self.api.held = False; self.drain()
        self.service.capture_active_selection.assert_called_once()
        self.assertEqual((self.api.sent, self.api.reads), (1, 1))

    def test_new_paste_press_has_its_own_release_requirement(self):
        self.press('paste'); previous = self.owner._release_observed
        self.finish_before_next_down_without_gui_release_sample()
        self.assertTrue(self.owner.trigger(action='paste'))
        self.assertIsNot(self.owner._release_observed, previous)
        self.assertTrue(previous.is_set())
        self.assertFalse(self.owner._release_observed.is_set())
        self.assertTrue(self.owner._release_required)
        self.assertFalse(self.owner.trigger(action='paste'))
        self.api.held = False; self.drain()
        self.assertIn('TARGET_VALIDATED_AFTER_RELEASE', self.window.statusBar().currentMessage())

    def test_busy_capture_prevents_concurrent_paste(self):
        self.press('capture')
        self.assertFalse(self.owner.trigger(action='paste'))
        self.assertIn('ADMISSION_OTHER_OPERATION_PENDING', self.window.statusBar().currentMessage())
        self.api.held = False; self.drain()

    def test_completion_without_observed_release_cannot_rearm_held_duplicate(self):
        self.api.held = True
        self.service.capture_active_selection.side_effect = lambda acquire, cancel: SelectionCaptureResult('Synthetic')
        self.assertTrue(self.owner.trigger(action='capture')); self.drain()
        self.assertTrue(self.owner._release_required)
        self.assertFalse(self.owner._release_observed.is_set())
        self.assertFalse(self.owner.trigger(action='paste'))
        self.assertIn('ADMISSION_RELEASE_EVENT_UNSIGNALED_KEYS_DOWN', self.window.statusBar().currentMessage())
        self.api.held = False; self.owner.poll()
        self.assertFalse(self.owner._release_required)

    def test_cancellation_drains_ownership_but_requires_observed_release(self):
        self.press('paste'); self.owner.cancel(); self.drain()
        self.assertFalse(self.owner.busy)
        self.assertIn('RELEASE_CANCELLED', self.window.statusBar().currentMessage())
        self.assertTrue(self.owner._release_required)
        self.assertFalse(self.owner.trigger(action='paste'))
        self.api.held = False; self.owner.poll()
        self.press('paste'); self.api.held = False; self.drain()
        self.assertIn('TARGET_VALIDATED_AFTER_RELEASE', self.window.statusBar().currentMessage())

    def test_worker_start_failure_rearms_on_release_without_timer_tick(self):
        self.api.held = True
        with patch('f7hub.gui.selection_capture.threading.Thread.start', side_effect=RuntimeError('synthetic')):
            self.assertFalse(self.owner.trigger(action='paste'))
        self.assertFalse(self.owner.busy)
        self.assertTrue(self.owner._release_required)
        self.assertFalse(self.owner.trigger(action='paste'))
        self.api.held = False  # Admission itself may observe release when the timer has not run.
        self.assertTrue(self.owner.trigger(action='paste')); self.drain()
        self.assertIn('TARGET_VALIDATED_AFTER_RELEASE', self.window.statusBar().currentMessage())

    def test_initial_binding_failure_rearms_only_after_release(self):
        original = self.api.foreground; self.api.held = True
        self.api.foreground = Mock(side_effect=RuntimeError('synthetic'))
        self.assertFalse(self.owner.trigger(action='paste'))
        self.api.foreground = original
        self.assertFalse(self.owner.trigger(action='paste'))
        self.api.held = False; self.owner.poll()
        self.press('paste'); self.api.held = False; self.drain()
        self.assertIn('TARGET_VALIDATED_AFTER_RELEASE', self.window.statusBar().currentMessage())

    def test_exit_cancels_drains_then_unregisters(self):
        self.press('paste')
        self.assertFalse(self.owner.close())
        self.assertTrue(self.owner._cancelled.is_set())
        self.drain(); self.assertTrue(self.owner.close())
        self.assertFalse(self.owner.registered or self.owner.paste_registered)
        self.assertFalse(self.owner.trigger(action='paste'))

    def test_target_policy_refusal_still_precedes_release_and_authorization(self):
        from f7hub.infrastructure.windows_selection_copy import SelectionCopyError
        self.api.pin_paste = Mock(side_effect=SelectionCopyError('UNSUPPORTED_TARGET', guard='OFFICE_POLICY'))
        self.api.held = True
        self.assertTrue(self.owner.trigger(action='paste')); self.drain()
        self.assertIn('PIN_OFFICE_POLICY', self.window.statusBar().currentMessage())
        self.assertFalse(self.owner._release_observed.is_set())
        self.assertEqual(self.service.mock_calls, [])
        self.assertEqual((self.api.sent, self.api.reads), (0, 0))

    def test_diagnostic_records_successful_c_release_on_same_coordinator(self):
        self.press('capture'); self.api.held = False; self.drain()
        snapshot = self.owner._release_diagnostic_snapshot()
        self.assertIn('C[A1 W1 R1 G1 L1 F1 D1 S1]', snapshot)
        self.assertIn('O=CAPTURE; E=SAME; LATCH=0; EVENT=1', snapshot)
        self.press('paste'); self.api.held = False; self.drain()
        self.assertIn('TARGET_VALIDATED_AFTER_RELEASE', self.window.statusBar().currentMessage())
        self.assertIn('E=OTHER', self.window.statusBar().currentMessage())

    def test_signaled_event_before_completion_still_refuses_concurrency(self):
        original = self.service.capture_active_selection.side_effect
        acquired, finish = threading.Event(), threading.Event()
        def delayed(acquire, cancel):
            result = original(acquire, cancel); acquired.set(); finish.wait(1); return result
        self.service.capture_active_selection.side_effect = delayed
        self.press('capture'); self.api.held = False
        self.assertTrue(acquired.wait(1))
        try:
            self.owner.poll()
            self.assertTrue(self.owner._release_observed.is_set())
            self.assertFalse(self.owner._release_required)
            self.assertTrue(self.owner.busy)
            self.assertFalse(self.owner.trigger(action='paste'))
            self.assertIn('ADMISSION_OTHER_OPERATION_PENDING', self.window.statusBar().currentMessage())
        finally: finish.set()
        self.drain()

    def test_v_before_poll_reports_completed_worker_pending_drain(self):
        self.press('capture'); self.api.held = False; self.join_worker()
        self.api.held = True
        self.assertFalse(self.owner.trigger(action='paste'))
        self.assertIn('ADMISSION_WORKER_COMPLETE_PENDING_DRAIN', self.window.statusBar().currentMessage())
        self.owner.poll()
        self.assertTrue(self.owner.trigger(action='paste'))
        self.api.held = False; self.drain()

    def test_unsignaled_capture_completion_reports_exact_missing_release_state(self):
        self.service.capture_active_selection.side_effect = lambda acquire, cancel: SelectionCaptureResult('SYNTHETIC PRIVATE')
        self.api.held = True; self.owner.trigger(action='capture'); self.drain()
        self.assertFalse(self.owner.trigger(action='paste'))
        message = self.window.statusBar().currentMessage()
        self.assertIn('ADMISSION_RELEASE_EVENT_UNSIGNALED_KEYS_DOWN', message)
        self.assertIn('C[A1 W0 R0 G0 L0 F1 D1 S1]', message)
        self.assertNotIn('SYNTHETIC PRIVATE', message)

    def test_signaled_but_unreconciled_guard_is_distinct_without_bypass(self):
        self.press('capture'); self.api.held = False; self.join_worker()
        self.api.held = True
        with patch.object(self.owner, '_rearm_if_released', return_value=None):
            self.owner.poll()
            self.assertFalse(self.owner.trigger(action='paste'))
        self.assertIn('ADMISSION_RELEASE_EVENT_SIGNALED_NOT_RECONCILED', self.window.statusBar().currentMessage())
        self.assertTrue(self.owner._release_required)

    def test_consecutive_capture_cycles_keep_independent_release_events(self):
        self.press('capture'); self.finish_before_next_down_without_gui_release_sample()
        previous = self.owner._release_observed
        self.assertTrue(self.owner.trigger(action='capture'))
        self.assertIsNot(self.owner._release_observed, previous)
        self.api.held = False; self.drain()
        self.assertEqual(self.service.capture_active_selection.call_count, 2)
        self.assertIn('C[A1 W1 R1 G1 L1 F1 D1 S1]', self.owner._release_diagnostic_snapshot())

    def test_diagnostic_snapshot_has_no_capture_context_before_capture(self):
        self.press('paste'); self.api.held = False; self.drain()
        message = self.window.statusBar().currentMessage()
        self.assertIn('C[NONE]', message)
        self.assertIn('TARGET_VALIDATED_AFTER_RELEASE', message)
        self.assertIn('authorization: NOT_REQUESTED', message)
        self.assertEqual(self.service.mock_calls, [])

    def test_normal_mode_does_not_allocate_capture_diagnostic_record(self):
        self.owner.target_diagnostic = False
        self.press('capture'); self.api.held = False; self.drain()
        self.assertIsNone(self.owner._capture_release_diagnostic)
