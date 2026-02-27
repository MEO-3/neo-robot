"""Sandboxed Python code executor for student programs."""

from __future__ import annotations

import io
import traceback
from typing import Any, Callable

from neo_robot.engine.apis import SAFE_BUILTINS, StudentArmAPI
from neo_robot.engine.execution_result import ExecutionResult


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

        def _delay(seconds: float) -> None:
            """Top-level ``delay(seconds)`` available in student code."""
            arm_api.delay(seconds)

        namespace: dict[str, Any] = {
            "__builtins__": {**SAFE_BUILTINS, "print": _print},
            "arm": arm_api,
            "delay": _delay,
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
