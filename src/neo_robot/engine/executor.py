"""Sandboxed Python code executor for student programs."""

from __future__ import annotations

import io
import traceback
from dataclasses import dataclass, field
from typing import Any, Callable

from neo_robot.hardware.mock_arm import MockRobotArm


# ---------------------------------------------------------------------------
# Execution result
# ---------------------------------------------------------------------------

@dataclass
class ExecutionResult:
    """Outcome of a single code execution."""

    output: str = ""
    error: str | None = None
    success: bool = True


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


# ---------------------------------------------------------------------------
# Safe builtins whitelist
# ---------------------------------------------------------------------------

_SAFE_BUILTINS: dict[str, Any] = {
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


# ---------------------------------------------------------------------------
# Executor
# ---------------------------------------------------------------------------

class CodeExecutor:
    """Execute student Python code in a restricted sandbox.

    The sandbox:
    * Injects an ``arm`` object (:class:`StudentArmAPI`) into the namespace.
    * Replaces ``print()`` with a version that captures to a buffer.
    * Strips ``__builtins__`` down to a safe whitelist.
    * Catches all exceptions and returns friendly error messages.
    """

    def __init__(self, robot: Any) -> None:
        self._robot = robot
        self._log_callback: Callable[[str], None] | None = None

    def set_log_callback(self, callback: Callable[[str], None]) -> None:
        """Set a callback that receives real-time log lines."""
        self._log_callback = callback

    def execute(self, code: str) -> ExecutionResult:
        """Run *code* and return an :class:`ExecutionResult`."""
        output_buf = io.StringIO()

        def _print(*args: Any, **kwargs: Any) -> None:
            """Replacement ``print`` that writes to our buffer."""
            kwargs.pop("file", None)  # ignore file= to prevent escape
            print(*args, **kwargs, file=output_buf)
            # Also forward to the real-time callback if set
            line = io.StringIO()
            print(*args, **kwargs, file=line)
            if self._log_callback:
                self._log_callback(line.getvalue().rstrip("\n"))

        arm_api = StudentArmAPI(self._robot, log=self._log_callback)

        namespace: dict[str, Any] = {
            "__builtins__": {**_SAFE_BUILTINS, "print": _print},
            "arm": arm_api,
        }

        try:
            exec(compile(code, "<student>", "exec"), namespace)  # noqa: S102
            return ExecutionResult(
                output=output_buf.getvalue(),
                success=True,
            )
        except SyntaxError as exc:
            line_info = f" (line {exc.lineno})" if exc.lineno else ""
            return ExecutionResult(
                output=output_buf.getvalue(),
                error=f"Syntax Error{line_info}: {exc.msg}",
                success=False,
            )
        except Exception as exc:  # noqa: BLE001
            # Try to extract a meaningful line number from the traceback
            tb_lines = traceback.format_exception(type(exc), exc, exc.__traceback__)
            # Find the last frame that references "<student>"
            line_num = ""
            for tb_line in tb_lines:
                if "<student>" in tb_line:
                    # e.g. '  File "<student>", line 3, in <module>\n'
                    parts = tb_line.strip().split(", ")
                    for part in parts:
                        if part.startswith("line "):
                            line_num = f" ({part})"
                            break

            return ExecutionResult(
                output=output_buf.getvalue(),
                error=f"Error{line_num}: {exc}",
                success=False,
            )
