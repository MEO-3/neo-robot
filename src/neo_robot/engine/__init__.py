"""Execution engine package.

Exports
-------
* :class:`CodeExecutor` – sandboxed Python code executor
* :class:`ExecutionResult` – result of a code execution
* :class:`StudentArmAPI` – simplified facade for student code
* :data:`SAFE_BUILTINS` – whitelisted builtins for the sandbox
"""

from neo_robot.engine.apis import SAFE_BUILTINS, StudentArmAPI
from neo_robot.engine.execution_result import ExecutionResult
from neo_robot.engine.executor import CodeExecutor

__all__ = [
    "CodeExecutor",
    "ExecutionResult",
    "SAFE_BUILTINS",
    "StudentArmAPI",
]
