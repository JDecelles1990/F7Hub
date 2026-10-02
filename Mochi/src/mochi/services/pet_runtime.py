"""Pure playback, visibility and greeting transitions; no Qt dependency."""

from collections import OrderedDict
import logging
from ..pet.animation import Animation
from ..pet.pet_state import PetState

logger = logging.getLogger("mochi.state")


class PetRuntime:
    def __init__(self, animation: Animation, wave: Animation | None = None):
        self.animations = {"IDLE": animation}
        if wave is not None:
            self.animations["WAVE"] = wave
        self.selected_animation = "IDLE"
        self.state = PetState.STARTING
        self.frame_index = 0
        self.visible = True
        self.greeting_generation = 0
        self.greeting_token = None
        self.greeted_sessions = OrderedDict()
        logger.info("Pet state=STARTING")

    @property
    def animation(self):
        return self.animations[self.selected_animation]

    @property
    def playing(self):
        return self.visible and self.state in (PetState.IDLE, PetState.WAVE)

    def start(self):
        if self.state is not PetState.STARTING:
            return False
        self.state = PetState.IDLE
        return True

    def _cancel_greeting(self):
        self.greeting_generation += 1
        self.greeting_token = None

    def select(self, animation):
        if self.state not in (PetState.IDLE, PetState.WAVE) or animation not in self.animations:
            return False
        changed = self.selected_animation != animation or self.greeting_token is not None
        self._cancel_greeting()
        if self.selected_animation != animation:
            self.frame_index = 0
        self.selected_animation = animation
        self.state = PetState[animation]
        return changed

    def pause(self):
        if self.state not in (PetState.IDLE, PetState.WAVE):
            return False
        self._cancel_greeting()
        self.state = PetState.PAUSED
        return True

    def resume(self):
        if self.state is not PetState.PAUSED:
            return False
        self.state = PetState[self.selected_animation]
        return True

    def exit(self):
        if self.state is PetState.EXITING:
            return False
        self._cancel_greeting()
        self.state = PetState.EXITING
        return True

    def command(self, command, controller_count=0):
        if self.state is PetState.EXITING:
            return "EXITING"
        if command in ("idle", "wave"):
            if self.state not in (PetState.IDLE, PetState.WAVE) or command.upper() not in self.animations:
                return "INVALID_TRANSITION"
            changed = self.select(command.upper())
        elif command == "pause":
            if self.state is PetState.PAUSED:
                return "UNCHANGED"
            changed = self.pause()
        elif command == "resume":
            if self.state in (PetState.IDLE, PetState.WAVE):
                return "UNCHANGED"
            changed = self.resume()
        elif command == "exit":
            changed = self.exit()
        elif command == "hide":
            if controller_count < 1:
                return "NO_CONTROLLER"
            changed = self.visible
            self._cancel_greeting()
            self.visible = False
        elif command == "show":
            changed = not self.visible
            self.visible = True
        else:
            return "INVALID_TRANSITION"
        return "CHANGED" if changed else "UNCHANGED"

    def greet(self, session_id):
        if session_id in self.greeted_sessions:
            self.greeted_sessions.move_to_end(session_id)
            return False
        self.greeted_sessions[session_id] = None
        if len(self.greeted_sessions) > 16:
            self.greeted_sessions.popitem(last=False)
        if not self.visible or self.state is not PetState.IDLE or "WAVE" not in self.animations:
            return False
        self.select("WAVE")
        self.greeting_token = self.greeting_generation
        return True

    def complete_greeting(self, token):
        if token is not None and token == self.greeting_token and self.playing and self.state is PetState.WAVE:
            self.select("IDLE")
            return True
        return False

    def advance(self):
        if self.playing:
            token = self.greeting_token
            self.frame_index = (self.frame_index + 1) % len(self.animation.paths)
            if self.frame_index == 0:
                self.complete_greeting(token)
        return self.frame_index

    def snapshot(self, checkout_id):
        return {"checkout_id": checkout_id, "behavior": self.state.name,
                "selected_animation": self.selected_animation, "frame": self.frame_index,
                "visibility": "VISIBLE" if self.visible else "HIDDEN",
                "paused": self.state is PetState.PAUSED}
