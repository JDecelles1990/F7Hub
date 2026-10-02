from pathlib import Path
import unittest

from mochi.pet.animation import Animation
from mochi.pet.pet_state import PetState
from mochi.services.pet_runtime import PetRuntime


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.runtime = PetRuntime(Animation((Path("first.png"), Path("second.png")), 120))

    def test_initial_pet_state(self):
        self.assertIs(self.runtime.state, PetState.STARTING)
        self.assertEqual(self.runtime.frame_index, 0)
        self.assertTrue(self.runtime.start())
        self.assertIs(self.runtime.state, PetState.IDLE)

    def test_pause_transition_freezes_frame(self):
        self.runtime.start()
        self.runtime.advance()
        self.assertTrue(self.runtime.pause())
        self.assertIs(self.runtime.state, PetState.PAUSED)
        self.assertEqual(self.runtime.advance(), 1)

    def test_resume_transition_continues_from_frozen_frame(self):
        self.runtime.start()
        self.runtime.advance()
        self.runtime.pause()
        self.assertTrue(self.runtime.resume())
        self.assertIs(self.runtime.state, PetState.IDLE)
        self.assertEqual(self.runtime.advance(), 0)

    def test_exit_transition_from_every_active_state(self):
        for state in (PetState.STARTING, PetState.IDLE, PetState.PAUSED):
            with self.subTest(state=state):
                runtime = PetRuntime(self.runtime.animation)
                if state is not PetState.STARTING:
                    runtime.start()
                if state is PetState.PAUSED:
                    runtime.pause()
                self.assertTrue(runtime.exit())
                self.assertIs(runtime.state, PetState.EXITING)
                self.assertFalse(runtime.resume())
                self.assertFalse(runtime.start())
                self.assertEqual(runtime.advance(), 0)

    def test_repeated_and_out_of_order_actions(self):
        self.assertFalse(self.runtime.pause())
        self.assertFalse(self.runtime.resume())
        self.runtime.start()
        self.assertFalse(self.runtime.start())
        self.runtime.pause()
        self.assertFalse(self.runtime.pause())
        self.runtime.resume()
        self.assertFalse(self.runtime.resume())
        self.runtime.exit()
        self.assertFalse(self.runtime.exit())

    def test_playback_wraps(self):
        self.runtime.start()
        self.assertEqual([self.runtime.advance() for _ in range(5)], [1, 0, 1, 0, 1])

    def test_animation_rejects_empty_and_invalid_interval(self):
        for paths, interval in (((), 120), ((Path("x"),), 0), ((Path("x"),), True)):
            with self.assertRaises(ValueError):
                Animation(paths, interval)
