from enum import Enum, auto


class PetState(Enum):
    STARTING = auto()
    IDLE = auto()
    PAUSED = auto()
    EXITING = auto()
