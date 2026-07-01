from enum import Enum


class State(Enum):
    BOOTING = "booting"
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    LEARNING = "learning"
    SLEEPING = "sleeping"