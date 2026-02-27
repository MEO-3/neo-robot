"""Main screen – split-pane editor and console."""

from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from neo_robot.engine import CodeExecutor, ExecutionResult
from neo_robot.ui.widgets.code_editor import CodeEditor
from neo_robot.ui.widgets.console import ConsoleOutput
from neo_robot.ui.widgets.toolbar import Toolbar


class MainScreen(Screen):
    """Primary application screen with a code editor and console output.

    Layout::

        +-------------------------------+
        |           Header              |
        +---------------+---------------+
        |  Code Editor  |   Console     |
        |  (left pane)  |  (right pane) |
        +---------------+---------------+
        | [Run] [Stop] [Clear Console]  |
        +-------------------------------+
        |           Footer              |
        +-------------------------------+
    """

    BINDINGS = [
        ("f5", "run_code", "Run"),
        ("ctrl+l", "clear_console", "Clear Console"),
    ]

    def __init__(self, executor: CodeExecutor, **kwargs) -> None:  # type: ignore[override]
        super().__init__(**kwargs)
        self._executor = executor

    # -- layout ---------------------------------------------------------

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main-split"):
            with Vertical(id="editor-pane"):
                yield Static("Code Editor", classes="pane-title")
                yield CodeEditor(id="editor")
            with Vertical(id="console-pane"):
                yield Static("Console", classes="pane-title")
                yield ConsoleOutput(id="console")
        yield Toolbar()
        yield Footer()

    # -- event handlers -------------------------------------------------

    def on_button_pressed(self, event: Toolbar.ButtonPressed) -> None:  # type: ignore[name-defined]
        """Route toolbar button clicks to the appropriate action."""
        btn_id = event.button.id
        if btn_id == "run-btn":
            self.action_run_code()
        elif btn_id == "stop-btn":
            self.action_stop_code()
        elif btn_id == "clear-btn":
            self.action_clear_console()

    # -- actions --------------------------------------------------------

    def action_run_code(self) -> None:
        """Get the code from the editor and execute it."""
        editor: CodeEditor = self.query_one("#editor", CodeEditor)
        console: ConsoleOutput = self.query_one("#console", ConsoleOutput)
        code = editor.get_code()

        if not code.strip():
            console.write_error("No code to run.")
            return

        # Disable Run, enable Stop
        self.query_one("#run-btn").disabled = True
        self.query_one("#stop-btn").disabled = False

        console.write_status("Running code...")
        self._run_code_in_worker(code)

    def action_stop_code(self) -> None:
        """Cancel any running worker."""
        # Cancel all workers owned by this screen
        self.workers.cancel_all()
        console: ConsoleOutput = self.query_one("#console", ConsoleOutput)
        console.write_error("Execution stopped by user.")
        self._reset_toolbar()

    def action_clear_console(self) -> None:
        console: ConsoleOutput = self.query_one("#console", ConsoleOutput)
        console.clear_console()

    # -- worker ---------------------------------------------------------

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

        self.app.call_from_thread(self._reset_toolbar)

    # -- helpers --------------------------------------------------------

    def _reset_toolbar(self) -> None:
        self.query_one("#run-btn").disabled = False
        self.query_one("#stop-btn").disabled = True
