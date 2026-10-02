import logging

from ..pet.animation import Animation
from ..pet.pet_state import PetState

logger = logging.getLogger("mochi.state")


class PetRuntime:
    def __init__(self, animation: Animation):
        self.animation = animation
        self.state = PetState.STARTING
        self.frame_index = 0
        logger.info("Pet state=STARTING")

    def _transition(self, target: PetState, allowed: tuple[PetState, ...]) -> bool:
        if self.state not in allowed:
            return False
        previous = self.state
        self.state = target
        logger.info("Pet transition=%s->%s", previous.name, target.name)
        return True

    def start(self) -> bool:
        return self._transition(PetState.IDLE, (PetState.STARTING,))

    def pause(self) -> bool:
        return self._transition(PetState.PAUSED, (PetState.IDLE,))

    def resume(self) -> bool:
        return self._transition(PetState.IDLE, (PetState.PAUSED,))

    def exit(self) -> bool:
        return self._transition(PetState.EXITING, (PetState.STARTING, PetState.IDLE, PetState.PAUSED))

    def advance(self) -> int:
        if self.state is PetState.IDLE:
            self.frame_index = (self.frame_index + 1) % len(self.animation.paths)
        return self.frame_index
