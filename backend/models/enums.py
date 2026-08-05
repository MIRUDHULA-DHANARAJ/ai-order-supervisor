from enum import Enum


class RunStatus(str, Enum):
    """
    Represents the lifecycle status of an Order Supervisor run.
    """

    RUNNING = "RUNNING"
    SLEEPING = "SLEEPING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    TERMINATED = "TERMINATED"


class ActivityType(str, Enum):
    """
    Represents the type of activity recorded in the activity log.
    """

    EVENT = "EVENT"
    ACTION = "ACTION"
    WAKE = "WAKE"
    SLEEP = "SLEEP"
    INSTRUCTION = "INSTRUCTION"
    FINAL = "FINAL"