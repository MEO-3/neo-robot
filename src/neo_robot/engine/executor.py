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
        # Persistent namespace for interactive (REPL) mode.
        # Lazily initialised by the first call to ``execute_line``.
        self._interactive_ns: dict[str, Any] | None = None

    def set_log_callback(self, callback: Callable[[str], None]) -> None:
        """Set a callback that receives real-time log lines."""
        self._log_callback = callback

    # -- helpers --------------------------------------------------------

    def _make_print(self, output_buf: io.StringIO) -> Callable[..., None]:
        """Build a sandboxed ``print`` that captures to *output_buf*."""

        def _print(*args: Any, **kwargs: Any) -> None:
            kwargs.pop("file", None)
            print(*args, **kwargs, file=output_buf)
            line = io.StringIO()
            print(*args, **kwargs, file=line)
            if self._log_callback:
                self._log_callback(line.getvalue().rstrip("\n"))

        return _print

    def _make_namespace(self, output_buf: io.StringIO) -> dict[str, Any]:
        """Build a restricted namespace containing the student API."""
        arm_api = StudentArmAPI(self._robot, log=self._log_callback)

        def _delay(seconds: float) -> None:
            arm_api.delay(seconds)

        return {
            "__builtins__": {**SAFE_BUILTINS, "print": self._make_print(output_buf)},
            "arm": arm_api,
            "delay": _delay,
        }

    @staticmethod
    def _extract_error(exc: Exception) -> str:
        """Return a student-friendly error string with line info."""
        tb_lines = traceback.format_exception(type(exc), exc, exc.__traceback__)
        line_num = ""
        for tb_line in tb_lines:
            if "<student>" in tb_line:
                parts = tb_line.strip().split(", ")
                for part in parts:
                    if part.startswith("line "):
                        line_num = f" ({part})"
                        break
        return f"Error{line_num}: {exc}"

    # -- batch mode (script editor) -------------------------------------

    def execute(self, code: str) -> ExecutionResult:
        """Run *code* in a fresh namespace and return an :class:`ExecutionResult`."""
        output_buf = io.StringIO()
        namespace = self._make_namespace(output_buf)

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
            return ExecutionResult(
                output=output_buf.getvalue(),
                error=self._extract_error(exc),
                success=False,
            )

    # -- interactive mode (REPL) ----------------------------------------

    def execute_line(self, line: str) -> ExecutionResult:
        """Execute a single *line* in a persistent namespace.

        Unlike :meth:`execute`, the namespace is kept between calls so
        that variables defined in one command are available in the next,
        behaving like a Python REPL session.
        """
        output_buf = io.StringIO()

        # Lazily create the persistent namespace on first use
        if self._interactive_ns is None:
            self._interactive_ns = self._make_namespace(output_buf)
        else:
            # Swap in a fresh print that writes to this call's buffer
            builtins = self._interactive_ns["__builtins__"]
            builtins["print"] = self._make_print(output_buf)

        try:
            exec(compile(line, "<student>", "exec"), self._interactive_ns)  # noqa: S102
            return ExecutionResult(
                output=output_buf.getvalue(),
                success=True,
            )
        except SyntaxError as exc:
            return ExecutionResult(
                output=output_buf.getvalue(),
                error=f"Syntax Error: {exc.msg}",
                success=False,
            )
        except Exception as exc:  # noqa: BLE001
            return ExecutionResult(
                output=output_buf.getvalue(),
                error=f"{type(exc).__name__}: {exc}",
                success=False,
            )

    def reset_session(self) -> None:
        """Discard the interactive namespace so the next call starts fresh."""
        self._interactive_ns = None
