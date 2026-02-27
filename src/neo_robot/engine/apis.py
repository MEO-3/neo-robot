"""Student-facing API and sandbox builtins whitelist."""

from __future__ import annotations

import time
from typing import Any, Callable


# ---------------------------------------------------------------------------
# Student-facing API
# ---------------------------------------------------------------------------

class StudentArmAPI:
    """Simplified facade injected as ``arm`` in the student's namespace.

    This class delegates to whichever robot implementation is active
    (real hardware or mock) and provides a flat, beginner-friendly API.
    """

    def __init__(self, robot: Any, log: Callable[[str], None] | None = None) -> None:
        self._robot = robot
        self._log = log or (lambda _: None)

    # -- movement -------------------------------------------------------

    def turn_left(self, angle: int = 90) -> None:
        """Rotate the arm to the left by *angle* degrees."""
        self._log(f"arm.turn_left({angle})")
        self._robot.upper_arm.turn_left(angle)

    def turn_right(self, angle: int = 90) -> None:
        """Rotate the arm to the right by *angle* degrees."""
        self._log(f"arm.turn_right({angle})")
        self._robot.upper_arm.turn_right(angle)

    def set_angle(self, angle: int) -> None:
        """Set the arm to an absolute angle (0-180)."""
        self._log(f"arm.set_angle({angle})")
        self._robot.upper_arm.set_angle(angle)

    # -- gripper --------------------------------------------------------

    def grab(self) -> None:
        """Close the gripper."""
        self._log("arm.grab()")
        self._robot.hand.grab()

    def release(self) -> None:
        """Open the gripper."""
        self._log("arm.release()")
        self._robot.hand.release()

    # -- elbow ----------------------------------------------------------

    def elbow_left(self, angle: int = 90) -> None:
        """Rotate the lower arm (elbow) to the left by *angle* degrees."""
        self._log(f"arm.elbow_left({angle})")
        self._robot.lower_arm.turn_left(angle)

    def elbow_right(self, angle: int = 90) -> None:
        """Rotate the lower arm (elbow) to the right by *angle* degrees."""
        self._log(f"arm.elbow_right({angle})")
        self._robot.lower_arm.turn_right(angle)

    # -- timing ---------------------------------------------------------

    def delay(self, seconds: float) -> None:
        """Pause execution for *seconds* (can be fractional, e.g. 0.5)."""
        self._log(f"arm.delay({seconds})")
        time.sleep(float(seconds))


# ---------------------------------------------------------------------------
# Safe builtins whitelist
# ---------------------------------------------------------------------------

SAFE_BUILTINS: dict[str, Any] = {
    # Types
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,
    "list": list,
    "tuple": tuple,
    "dict": dict,
    "set": set,
    # Functions
    "range": range,
    "len": len,
    "abs": abs,
    "min": min,
    "max": max,
    "round": round,
    "sorted": sorted,
    "reversed": reversed,
    "enumerate": enumerate,
    "zip": zip,
    "map": map,
    "filter": filter,
    # Constants
    "True": True,
    "False": False,
    "None": None,
}
