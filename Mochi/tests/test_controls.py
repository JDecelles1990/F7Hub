import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from pathlib import Path
import tempfile
import unittest

from PySide6.QtCore import QRect
from PySide6.QtGui import QImage, QColor
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest

from mochi.core.config import Settings, load_settings
from mochi.pet.animation import Animation
from mochi.pet.animation_loader import load_animation, AnimationLoadError, LoadedAnimation
from mochi.pet.pet_state import PetState
from mochi.services.pet_runtime import PetRuntime
from mochi.ui.pet_window import PetWindow


def runtime():
    return PetRuntime(Animation((Path('i0'), Path('i1')), 120),
                      Animation(tuple(Path(f'w{i}') for i in range(4)), 120))


class ControlsTests(unittest.TestCase):
    def setUp(self):
        self.r = runtime()
        self.r.start()

    def test_manual_wave_loops_and_repeated_selection_preserves_frame(self):
        self.assertEqual(self.r.command('wave'), 'CHANGED')
        self.assertEqual(self.r.frame_index, 0)
        self.r.advance()
        self.assertEqual(self.r.command('wave'), 'UNCHANGED')
        self.assertEqual(self.r.frame_index, 1)
        for _ in range(12):
            self.r.advance()
        self.assertIs(self.r.state, PetState.WAVE)
        self.assertEqual(self.r.command('idle'), 'CHANGED')
        self.assertEqual(self.r.frame_index, 0)
        self.assertEqual(self.r.command('idle'), 'UNCHANGED')

    def test_one_cycle_greeting_completion_and_runtime_dedupe(self):
        self.assertTrue(self.r.greet('session'))
        for frame in (1, 2, 3):
            self.assertEqual(self.r.advance(), frame)
            self.assertIs(self.r.state, PetState.WAVE)
        self.r.advance()
        self.assertIs(self.r.state, PetState.IDLE)
        self.assertFalse(self.r.greet('session'))

    def test_pause_resume_both_animations_and_reject_switch(self):
        for animation in ('idle', 'wave'):
            with self.subTest(animation=animation):
                self.r.command(animation)
                self.r.advance()
                selected, frame = self.r.selected_animation, self.r.frame_index
                self.assertEqual(self.r.command('pause'), 'CHANGED')
                self.assertEqual(self.r.command('pause'), 'UNCHANGED')
                self.assertEqual(self.r.command('idle'), 'INVALID_TRANSITION')
                self.assertEqual(self.r.command('wave'), 'INVALID_TRANSITION')
                self.r.advance()
                self.assertEqual(self.r.frame_index, frame)
                self.r.command('resume')
                self.assertEqual(self.r.selected_animation, selected)
                self.assertEqual(self.r.frame_index, frame)

    def test_hidden_freezes_frame_and_preserves_pause(self):
        for paused in (False, True):
            with self.subTest(paused=paused):
                self.r = runtime()
                self.r.start()
                self.r.command('wave')
                self.r.advance()
                if paused:
                    self.r.pause()
                state = self.r.state
                self.assertEqual(self.r.command('hide'), 'NO_CONTROLLER')
                self.assertEqual(self.r.command('hide', 1), 'CHANGED')
                self.assertEqual(self.r.command('hide', 1), 'UNCHANGED')
                self.r.advance()
                self.assertEqual(self.r.frame_index, 1)
                self.assertEqual(self.r.command('show'), 'CHANGED')
                self.assertEqual(self.r.command('show'), 'UNCHANGED')
                self.assertIs(self.r.state, state)

    def test_ineligible_attach_is_consumed_and_state_preserved(self):
        for command in ('pause', 'hide', 'wave', 'exit'):
            with self.subTest(command=command):
                r = runtime()
                r.start()
                r.command(command, 1)
                before = r.snapshot('checkout')
                self.assertFalse(r.greet('session'))
                self.assertEqual(r.snapshot('checkout'), before)
                r.command('show')
                r.command('resume')
                r.command('idle')
                self.assertFalse(r.greet('session'))

    def test_every_interruption_invalidates_old_completion_token(self):
        for command in ('idle', 'wave', 'pause', 'hide', 'exit'):
            with self.subTest(command=command):
                r = runtime()
                r.start()
                r.greet('session')
                r.advance()
                token = r.greeting_token
                r.command(command, 1)
                before = r.snapshot('checkout')
                self.assertFalse(r.complete_greeting(token))
                self.assertEqual(r.snapshot('checkout'), before)
                self.assertIsNone(r.greeting_token)

    def test_lru_bounded_and_manual_wave_independent(self):
        for i in range(20):
            self.r.command('idle')
            self.r.greet(str(i))
        self.assertEqual(len(self.r.greeted_sessions), 16)
        self.assertNotIn('0', self.r.greeted_sessions)
        self.r.command('wave')
        for _ in range(9):
            self.r.advance()
        self.assertIs(self.r.state, PetState.WAVE)

    def test_exiting_rejects_every_mutation(self):
        self.r.exit()
        for command in ('idle', 'wave', 'pause', 'resume', 'show', 'hide', 'exit'):
            self.assertEqual(self.r.command(command, 1), 'EXITING')


class WaveLoadingTests(unittest.TestCase):
    def test_actual_wave_has_four_alpha_frames_matching_idle(self):
        directory = Path(__file__).resolve().parents[1] / 'assets/animations/frames'
        idle = load_animation(directory, 0, 120)
        wave = load_animation(directory, 3, 120)
        self.assertEqual([p.name for p in wave.animation.paths], [f'r3c{i}.png' for i in range(4)])
        self.assertEqual(len(wave.images), 4)
        self.assertEqual((wave.images[0].width(), wave.images[0].height()), (192, 208))
        self.assertTrue(all(i.hasAlphaChannel() and i.size() == idle.images[0].size() for i in wave.images))

    def test_missing_corrupt_and_mismatched_wave(self):
        with tempfile.TemporaryDirectory() as name:
            p = Path(name)
            with self.assertRaises(AnimationLoadError):
                load_animation(p, 3, 120)
            (p/'r3c0.png').write_bytes(b'corrupt')
            with self.assertRaises(AnimationLoadError):
                load_animation(p, 3, 120)
            for index, width in enumerate((16, 17)):
                image = QImage(width, 20, QImage.Format.Format_ARGB32)
                image.fill(QColor('red'))
                image.save(str(p/f'r3c{index}.png'))
            with self.assertRaises(AnimationLoadError):
                load_animation(p, 3, 120)

    def test_wave_row_validation_and_default(self):
        import json
        with tempfile.TemporaryDirectory() as name:
            p = Path(name)
            (p/'config').mkdir()
            for value, expected in ((5, 5), (True, 3), (-1, 3), (11, 3), ('3', 3)):
                (p/'config/settings.json').write_text(json.dumps({'animation': {'wave_row': value}}))
                self.assertEqual(load_settings(p).wave_row, expected)

    def test_application_rejects_cross_animation_dimension_mismatch(self):
        from unittest.mock import patch
        from mochi.app import main
        with tempfile.TemporaryDirectory() as name:
            p = Path(name)
            image = QImage(16, 20, QImage.Format.Format_ARGB32)
            other = QImage(17, 20, QImage.Format.Format_ARGB32)
            idle = LoadedAnimation(Animation((Path('idle'),), 120), (image,))
            wave = LoadedAnimation(Animation((Path('wave'),), 120), (other,))
            with patch('mochi.app.load_animation', side_effect=(idle, wave)), patch('mochi.app.QApplication') as app:
                self.assertEqual(main(p), 1)
                app.assert_not_called()


class VisibilityWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.r = runtime()
        images = tuple(QImage(24, 30, QImage.Format.Format_ARGB32) for _ in range(4))
        for image in images:
            image.fill(QColor('red'))
        self.window = PetWindow(Settings(), LoadedAnimation(self.r.animations['IDLE'], images[:2]), self.r,
                                LoadedAnimation(self.r.animations['WAVE'], images))
        self.window.start()
        self.window.show()
        self.addCleanup(self.window.deleteLater)
        self.addCleanup(self.window.shutdown)

    def test_timer_stays_stopped_hidden_and_paused_without_catchup(self):
        self.window.apply('wave')
        self.r.advance()
        self.window.apply('hide', 1)
        QTest.qWait(140)
        self.window._advance()
        self.assertEqual(self.r.frame_index, 1)
        self.assertFalse(self.window.timer.isActive())
        self.window.apply('show')
        self.assertTrue(self.window.timer.isActive())
        self.window.pause()
        self.window.apply('hide', 1)
        self.window.apply('show')
        self.assertFalse(self.window.timer.isActive())
        self.assertEqual(self.r.frame_index, 1)

    def test_negative_position_preserved_and_gap_recovered(self):
        screens = [QRect(-1000, 0, 1000, 900), QRect(300, 0, 1000, 900)]
        self.window.move(-500, 100)
        self.window.recover_position(screens, screens[1])
        self.assertEqual(self.window.x(), -500)
        self.window.move(100, 100)
        self.window.recover_position(screens, screens[1])
        self.assertTrue(screens[1].contains(QRect(self.window.pos(), self.window.size())))

    def test_unavailable_monitor_restores_complete_window(self):
        primary = QRect(0, 0, 800, 600)
        self.window.move(-3000, -1000)
        self.window.recover_position([primary], primary)
        self.assertTrue(primary.contains(QRect(self.window.pos(), self.window.size())))
