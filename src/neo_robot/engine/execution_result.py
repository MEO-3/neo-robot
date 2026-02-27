"""Data class for code execution outcomes."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ExecutionResult:
    """Outcome of a single code execution."""

    output: str = ""
    error: str | None = None
    success: bool = True
