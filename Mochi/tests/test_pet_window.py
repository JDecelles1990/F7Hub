import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
import unittest

from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtGui import QColor, QContextMenuEvent, QImage, QMouseEvent
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication

from mochi.core.config import Settings
from mochi.pet.animation import Animation
from mochi.pet.animation_loader import LoadedAnimation
from mochi.pet.pet_state import PetState
from mochi.services.pet_runtime import PetRuntime
from mochi.ui.pet_window import PetWindow


class PetWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        images = []
        for color in (QColor("red"), QColor("blue")):
            image = QImage(24, 30, QImage.Format.Format_ARGB32)
            image.fill(color)
            images.append(image)
        loaded = LoadedAnimation(Animation((Path("0"), Path("1")), 30), tuple(images))
        self.window = PetWindow(Settings(), loaded, PetRuntime(loaded.animation))
        self.window.move(100, 100)
        self.window.start()
        self.window.show()
        self.app.processEvents()
        self.addCleanup(self.dispose)

    def dispose(self):
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()

    def test_window_flags_and_initial_idle(self):
        self.assertTrue(self.window.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground))
        for flag in (Qt.WindowType.FramelessWindowHint, Qt.WindowType.WindowStaysOnTopHint):
            self.assertTrue(self.window.windowFlags() & flag)
        self.assertTrue(self.window.testAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating))
        self.assertEqual(self.window.focusPolicy(), Qt.FocusPolicy.NoFocus)
        self.assertIs(self.window.runtime.state, PetState.IDLE)
        self.assertTrue(self.window.timer.isActive())

    def test_timer_advances_frame(self):
        for _ in range(20):
            QTest.qWait(5)
            if self.window.runtime.frame_index == 1:
                break
        self.assertEqual(self.window.runtime.frame_index, 1)

    def test_pause_resume_menu_actions(self):
        self.assertEqual([action.text() for action in self.window.menu.actions()], ["Pause", "Resume", "Exit"])
        self.assertFalse(self.window.resume_action.isEnabled())
        self.window.pause_action.trigger()
        frozen = self.window.runtime.frame_index
        QTest.qWait(100)
        self.assertEqual(self.window.runtime.frame_index, frozen)
        self.assertFalse(self.window.timer.isActive())
        self.assertFalse(self.window.pause_action.isEnabled())
        self.assertTrue(self.window.resume_action.isEnabled())
        self.window.resume_action.trigger()
        self.assertIs(self.window.runtime.state, PetState.IDLE)
        self.assertTrue(self.window.timer.isActive())
        self.assertFalse(self.window.resume_action.isEnabled())

    def test_drag_while_paused(self):
        self.window.pause()
        local = QPointF(8, 8)
        origin = self.window.pos()
        global_position = QPointF(origin + QPoint(8, 8))
        press = QMouseEvent(QMouseEvent.Type.MouseButtonPress, local, global_position,
                            Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
        move = QMouseEvent(QMouseEvent.Type.MouseMove, local + QPointF(40, 20), global_position + QPointF(40, 20),
                           Qt.MouseButton.NoButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
        release = QMouseEvent(QMouseEvent.Type.MouseButtonRelease, local, global_position + QPointF(40, 20),
                              Qt.MouseButton.LeftButton, Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier)
        for event in (press, move, release):
            self.app.sendEvent(self.window, event)
        self.assertEqual(self.window.pos(), origin + QPoint(40, 20))
        self.assertIs(self.window.runtime.state, PetState.PAUSED)
        self.assertIsNone(self.window._drag_offset)

    def test_context_menu_opens(self):
        event = QContextMenuEvent(QContextMenuEvent.Reason.Mouse, QPoint(8, 8), self.window.mapToGlobal(QPoint(8, 8)))
        self.app.sendEvent(self.window, event)
        self.assertTrue(self.window.menu.isVisible())
        self.window.menu.close()

    def test_exit_action_and_repeated_shutdown(self):
        self.window.exit_action.trigger()
        self.assertFalse(self.window.isVisible())
        self.assertIs(self.window.runtime.state, PetState.EXITING)
        self.assertFalse(self.window.timer.isActive())
        self.window.shutdown()
        self.window.resume()
        self.assertIs(self.window.runtime.state, PetState.EXITING)
        self.assertFalse(self.window.timer.isActive())

    def test_topmost_setting_can_be_disabled(self):
        self.window.close()
        loaded = LoadedAnimation(self.window.runtime.animation, tuple(pixmap.toImage() for pixmap in self.window._frames))
        self.window = PetWindow(Settings(always_on_top=False), loaded, PetRuntime(loaded.animation))
        self.assertFalse(self.window.windowFlags() & Qt.WindowType.WindowStaysOnTopHint)
