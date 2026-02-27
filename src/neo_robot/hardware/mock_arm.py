"""Simulated robotic arm for development and testing.

Provides the same public interface as :mod:`neo_robot.hardware.robot_arm` but
logs actions to a callback instead of driving real servos.
"""

from __future__ import annotations

from typing import Callable

# Type alias for the logging callback.  The mock classes call this
# function with a human-readable message every time a command executes.
LogCallback = Callable[[str], None]


def _noop(msg: str) -> None:  # pragma: no cover
    """Default no-op logger used when no callback is provided."""


class MockArm:
    """Simulated single servo joint that logs movements."""

    def __init__(self, name: str = "arm", log: LogCallback = _noop) -> None:
        self.name = name
        self._log = log
        self._current_angle: int = 0

    def turn_left(self, angle: int) -> None:
        new_angle = max(0, self._current_angle - int(angle))
        self._log(f"[{self.name}] turn_left({angle}) -> {new_angle} deg")
        self._current_angle = new_angle

    def turn_right(self, angle: int) -> None:
        new_angle = min(180, self._current_angle + int(angle))
        self._log(f"[{self.name}] turn_right({angle}) -> {new_angle} deg")
        self._current_angle = new_angle

    def set_angle(self, angle: int) -> None:
        clamped = max(0, min(180, int(angle)))
        self._log(f"[{self.name}] set_angle({angle}) -> {clamped} deg")
        self._current_angle = clamped

    @property
    def angle(self) -> int:
        return self._current_angle


class MockHand(MockArm):
    """Simulated gripper that logs grab/release actions."""

    def __init__(self, log: LogCallback = _noop) -> None:
        super().__init__(name="hand", log=log)
        self._grabbed = False

    def grab(self) -> None:
        self._log("[hand] grab()")
        self.set_angle(60)
        self._grabbed = True

    def release(self) -> None:
        self._log("[hand] release()")
        self.set_angle(0)
        self._grabbed = False

    @property
    def is_grabbed(self) -> bool:
        return self._grabbed


class MockRobotArm:
    """Simulated robot arm — same public interface as :class:`RobotArm`.

    Parameters
    ----------
    log : LogCallback, optional
        A callable that receives descriptive strings for every hardware
        action.  Typically wired to :meth:`ConsoleOutput.write_status`.
    """

    def __init__(self, log: LogCallback = _noop) -> None:
        self._log = log
        self._log("[system] MockRobotArm initialised (simulation mode)")
        self.upper_arm = MockArm(name="upper_arm", log=log)
        self.lower_arm = MockArm(name="lower_arm", log=log)
        self.hand = MockHand(log=log)

    def shutdown(self) -> None:
        self._log("[system] MockRobotArm shutdown")
