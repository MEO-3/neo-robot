"""Main screen – split-pane editor / console with interactive REPL mode."""

from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from neo_robot.engine import CodeExecutor, ExecutionResult
from neo_robot.ui.widgets.code_editor import CodeEditor
from neo_robot.ui.widgets.console import ConsoleOutput
from neo_robot.ui.widgets.interactive_console import CommandSubmitted, InteractiveConsole


class MainScreen(Screen):
    """Primary application screen with two modes.

    **Script mode** (default)::

        +-------------------------------+
        |           Header              |
        +---------------+---------------+
        |  Code Editor  |   Console     |
        |  (left pane)  |  (right pane) |
        +---------------+---------------+
        |           Footer              |
        +-------------------------------+

    **Interactive mode** (toggled with F2)::

        +-------------------------------+
        |           Header              |
        +-------------------------------+
        |    Interactive Console        |
        |    (full width REPL)          |
        +-------------------------------+
        |           Footer              |
        +-------------------------------+

    All actions are driven via keyboard shortcuts shown in the Footer.
    """

    BINDINGS = [
        ("f5", "run_code", "Run"),
        ("f2", "toggle_mode", "Toggle Mode"),
        ("ctrl+x", "stop_code", "Stop"),
        ("ctrl+l", "clear_console", "Clear Console"),
        ("ctrl+e", "clear_editor", "Clear Editor"),
    ]

    def __init__(self, executor: CodeExecutor, **kwargs) -> None:  # type: ignore[override]
        super().__init__(**kwargs)
        self._executor = executor
        self._interactive_mode = False
        self._running = False

    # -- layout ---------------------------------------------------------

    def compose(self) -> ComposeResult:
        yield Header()
        # Script mode panes
        with Horizontal(id="main-split"):
            with Vertical(id="editor-pane"):
                yield Static("Code Editor", classes="pane-title")
                yield CodeEditor(id="editor")
            with Vertical(id="console-pane"):
                yield Static("Console", classes="pane-title")
                yield ConsoleOutput(id="console")
        # Interactive mode pane (hidden by default via CSS)
        with Vertical(id="interactive-pane"):
            yield Static("Interactive Console", classes="pane-title")
            yield InteractiveConsole(id="interactive")
        yield Footer()

    # -- mode toggle ----------------------------------------------------

    def action_toggle_mode(self) -> None:
        """Switch between script and interactive mode."""
        self._interactive_mode = not self._interactive_mode

        main_split = self.query_one("#main-split")
        interactive_pane = self.query_one("#interactive-pane")

        if self._interactive_mode:
            main_split.display = False
            interactive_pane.display = True
            # Focus the REPL input
            repl: InteractiveConsole = self.query_one("#interactive", InteractiveConsole)
            repl.focus_input()
        else:
            main_split.display = True
            interactive_pane.display = False

    # -- event handlers -------------------------------------------------

    def on_command_submitted(self, event: CommandSubmitted) -> None:
        """Handle a command submitted from the interactive console."""
        self._run_interactive_command(event.command)

    # -- actions --------------------------------------------------------

    def action_run_code(self) -> None:
        """Get the code from the editor and execute it (script mode only)."""
        if self._interactive_mode:
            return

        editor: CodeEditor = self.query_one("#editor", CodeEditor)
        console: ConsoleOutput = self.query_one("#console", ConsoleOutput)
        code = editor.get_code()

        if not code.strip():
            console.write_error("No code to run.")
            return

        self._running = True
        console.write_status("Running code...")
        self._run_code_in_worker(code)

    def action_stop_code(self) -> None:
        """Cancel any running worker."""
        self.workers.cancel_all()
        if self._interactive_mode:
            repl: InteractiveConsole = self.query_one("#interactive", InteractiveConsole)
            repl.write_error("Execution stopped by user.")
        else:
            console: ConsoleOutput = self.query_one("#console", ConsoleOutput)
            console.write_error("Execution stopped by user.")
        self._running = False

    def action_clear_console(self) -> None:
        """Clear the console output (or the REPL log in interactive mode)."""
        if self._interactive_mode:
            from textual.widgets import RichLog
            log = self.query_one("#interactive #repl-log", RichLog)
            log.clear()
        else:
            console: ConsoleOutput = self.query_one("#console", ConsoleOutput)
            console.clear_console()

    def action_clear_editor(self) -> None:
        """Clear the code editor (script mode only)."""
        if self._interactive_mode:
            return
        editor: CodeEditor = self.query_one("#editor", CodeEditor)
        editor.set_code("")

    # -- worker (script mode) -------------------------------------------

    @work(thread=True, exclusive=True)
    def _run_code_in_worker(self, code: str) -> None:
        """Execute student code on a background thread.

        Uses ``call_from_thread`` to safely update UI widgets from
        the worker thread.
        """
        console: ConsoleOutput = self.query_one("#console", ConsoleOutput)

        def _live_log(msg: str) -> None:
            """Forward log lines to the console in real time."""
            self.app.call_from_thread(console.write_status, msg)

        self._executor.set_log_callback(_live_log)

        result: ExecutionResult = self._executor.execute(code)

        # Post results back to the UI thread
        if result.output.strip():
            self.app.call_from_thread(console.write_output, result.output.rstrip("\n"))

        if result.success:
            self.app.call_from_thread(
                console.write_status, "Execution complete."
            )
        else:
            self.app.call_from_thread(console.write_error, result.error or "Unknown error")

        self._running = False

    # -- worker (interactive mode) --------------------------------------

    @work(thread=True, exclusive=True)
    def _run_interactive_command(self, command: str) -> None:
        """Execute a single REPL command on a background thread."""
        repl: InteractiveConsole = self.query_one("#interactive", InteractiveConsole)

        def _live_log(msg: str) -> None:
            self.app.call_from_thread(repl.write_status, msg)

        self._executor.set_log_callback(_live_log)

        result: ExecutionResult = self._executor.execute_line(command)

        if result.output.strip():
            self.app.call_from_thread(repl.write_output, result.output.rstrip("\n"))

        if not result.success:
            self.app.call_from_thread(repl.write_error, result.error or "Unknown error")
