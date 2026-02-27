"""Toolbar widget with Run / Stop / Clear / Mode-toggle actions."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button


class Toolbar(Horizontal):
    """Bottom toolbar providing action buttons for the editor.

    Buttons
    -------
    * **Run (F5)**         – execute the code in the editor
    * **Stop**             – cancel a running execution
    * **Clear**            – clear the console output
    * **Interactive (F2)** – toggle between script and interactive mode
    """

    DEFAULT_CSS = """
    Toolbar {
        dock: bottom;
        height: 3;
        padding: 0 1;
        background: $surface;
    }

    Toolbar Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Button("Run (F5)", id="run-btn", variant="success")
        yield Button("Stop", id="stop-btn", variant="error", disabled=True)
        yield Button("Clear Console", id="clear-btn", variant="default")
        yield Button("Interactive (F2)", id="mode-btn", variant="primary")

    def set_mode_label(self, interactive: bool) -> None:
        """Update the mode button label to reflect the current mode."""
        btn = self.query_one("#mode-btn", Button)
        btn.label = "Script (F2)" if interactive else "Interactive (F2)"
