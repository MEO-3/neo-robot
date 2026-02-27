"""Interactive REPL console widget for line-by-line code execution."""

from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import Input, RichLog
from rich.text import Text


class CommandSubmitted(Message):
    """Posted when the user submits a command in the interactive console."""

    def __init__(self, command: str) -> None:
        super().__init__()
        self.command = command


class InteractiveConsole(Vertical):
    """REPL-style console: a scrollable log with a command input at the bottom.

    Layout::

        +----------------------------------+
        |  >>> arm.turn_right(90)          |
        |  [upper_arm] turn_right -> 90    |
        |  >>> arm.grab()                  |
        |  [hand] grab()                   |
        |  >>>                             |
        +----------------------------------+
        | >>> [input field]                |
        +----------------------------------+

    The widget posts a :class:`CommandSubmitted` message when the user
    presses Enter.  The parent screen is responsible for executing the
    command and writing output back via the public helpers.
    """

    DEFAULT_CSS = """
    InteractiveConsole {
        height: 1fr;
    }

    InteractiveConsole #repl-log {
        height: 1fr;
    }

    InteractiveConsole #repl-input {
        dock: bottom;
        height: 3;
    }
    """

    BINDINGS = [
        ("up", "history_prev", "Previous command"),
        ("down", "history_next", "Next command"),
    ]

    def __init__(self, **kwargs) -> None:  # type: ignore[override]
        super().__init__(**kwargs)
        self._history: list[str] = []
        self._history_index: int = -1

    def compose(self) -> ComposeResult:
        yield RichLog(id="repl-log", highlight=True, markup=True, wrap=True)
        yield Input(placeholder="Type a command and press Enter ...", id="repl-input")

    def on_mount(self) -> None:
        log = self.query_one("#repl-log", RichLog)
        log.write(Text("Interactive Mode (type commands one at a time)", style="bold cyan"))
        log.write(Text("Type 'help' for available commands.\n", style="dim"))

    # -- input handling -------------------------------------------------

    @on(Input.Submitted, "#repl-input")
    def _on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in the input field."""
        command = event.value.strip()
        input_widget = self.query_one("#repl-input", Input)
        input_widget.value = ""

        if not command:
            return

        # Add to history
        self._history.append(command)
        self._history_index = -1

        # Echo the command in the log
        log = self.query_one("#repl-log", RichLog)
        log.write(Text(f">>> {command}", style="bold green"))

        # Handle built-in REPL commands
        if command == "help":
            self._show_help()
            return
        if command == "clear":
            log.clear()
            return
        if command == "history":
            self._show_history()
            return

        # Post message for the parent screen to execute
        self.post_message(CommandSubmitted(command))

    # -- history navigation ---------------------------------------------

    def action_history_prev(self) -> None:
        """Navigate to the previous command in history."""
        if not self._history:
            return
        input_widget = self.query_one("#repl-input", Input)
        if self._history_index == -1:
            self._history_index = len(self._history) - 1
        elif self._history_index > 0:
            self._history_index -= 1
        input_widget.value = self._history[self._history_index]

    def action_history_next(self) -> None:
        """Navigate to the next command in history."""
        if not self._history or self._history_index == -1:
            return
        input_widget = self.query_one("#repl-input", Input)
        if self._history_index < len(self._history) - 1:
            self._history_index += 1
            input_widget.value = self._history[self._history_index]
        else:
            self._history_index = -1
            input_widget.value = ""

    # -- public helpers (called by parent screen) -----------------------

    def write_output(self, text: str) -> None:
        """Write normal output to the REPL log."""
        log = self.query_one("#repl-log", RichLog)
        log.write(Text(text))

    def write_error(self, text: str) -> None:
        """Write an error to the REPL log."""
        log = self.query_one("#repl-log", RichLog)
        log.write(Text(text, style="bold red"))

    def write_status(self, text: str) -> None:
        """Write a status message to the REPL log."""
        log = self.query_one("#repl-log", RichLog)
        log.write(Text(text, style="dim italic"))

    # -- internal helpers -----------------------------------------------

    def _show_help(self) -> None:
        log = self.query_one("#repl-log", RichLog)
        log.write(Text(""))
        log.write(Text("Available commands:", style="bold cyan"))
        log.write(Text("  arm.turn_left(angle)   - rotate arm left"))
        log.write(Text("  arm.turn_right(angle)  - rotate arm right"))
        log.write(Text("  arm.grab()             - close the gripper"))
        log.write(Text("  arm.release()          - open the gripper"))
        log.write(Text("  arm.elbow_left(angle)  - rotate elbow left"))
        log.write(Text("  arm.elbow_right(angle) - rotate elbow right"))
        log.write(Text("  arm.set_angle(angle)   - set absolute angle"))
        log.write(Text("  delay(seconds)         - pause execution"))
        log.write(Text("  print(...)             - print a value"))
        log.write(Text(""))
        log.write(Text("REPL commands:", style="bold cyan"))
        log.write(Text("  help     - show this help"))
        log.write(Text("  clear    - clear the console"))
        log.write(Text("  history  - show command history"))
        log.write(Text(""))

    def _show_history(self) -> None:
        log = self.query_one("#repl-log", RichLog)
        if not self._history:
            log.write(Text("No commands in history.", style="dim"))
            return
        log.write(Text("Command history:", style="bold cyan"))
        for i, cmd in enumerate(self._history, 1):
            log.write(Text(f"  {i}. {cmd}"))
        log.write(Text(""))

    def focus_input(self) -> None:
        """Focus the input field (useful when switching modes)."""
        self.query_one("#repl-input", Input).focus()
