"""Console output widget for execution feedback."""

from __future__ import annotations

from rich.text import Text
from textual.widgets import RichLog


class ConsoleOutput(RichLog):
    """Real-time console that displays execution output, errors, and status.

    Uses Textual's :class:`~textual.widgets.RichLog` which supports
    Rich renderables and auto-scrolls to the latest entry.
    """

    def __init__(self, **kwargs) -> None:  # type: ignore[override]
        super().__init__(
            highlight=True,
            markup=True,
            wrap=True,
            **kwargs,
        )

    # -- public helpers ------------------------------------------------

    def write_output(self, text: str) -> None:
        """Write normal program output (e.g. from ``print()``)."""
        self.write(Text(text))

    def write_error(self, text: str) -> None:
        """Write an error message highlighted in red."""
        self.write(Text(text, style="bold red"))

    def write_status(self, text: str) -> None:
        """Write a status / info message in dim italic."""
        self.write(Text(text, style="dim italic"))

    def clear_console(self) -> None:
        """Remove all content from the console."""
        self.clear()
