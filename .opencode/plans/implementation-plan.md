# Implementation Plan: NEO Robot TUI Application

## Overview

Build a Textual-based split-screen TUI application for K-12 students to learn Python through robotics. The application has a single main screen with a **code editor** (left) and **console output** (right). Students write Python commands that execute against a robotic arm via the thingbot-telemetrix protocol.

---

## Phase 0: Project Setup & Fixes

### 0.1 Rename package: `src/neo-robot/` → `src/neo_robot/`
- Hyphens are invalid in Python package names
- Rename directory and update any references

### 0.2 Fix existing bugs in `robot_arm.py`
- Fix `current_angle` attribute/method name collision → rename method to `get_current_angle()` or use `@property`
- Fix typo `grap()` → `grab()`
- Fix `pin_mode()` → `set_pin_mode_servo()` for Telemetrix API

### 0.3 Create `pyproject.toml`
- Declare dependencies: `textual`, `thingbot-telemetrix`
- Define entry point: `neo-robot = "neo_robot.ui.app:main"`
- Python version: `>=3.11`

---

## Phase 1: Architecture & Classes

### Package Structure (final)

```
src/neo_robot/
├── __init__.py              # Package root, __version__
├── __main__.py              # Entry point: `python -m neo_robot`
│
├── config/
│   ├── __init__.py
│   └── settings.py          # App-wide settings (pins, defaults, theme)
│
├── hardware/
│   ├── __init__.py
│   ├── robot_arm.py          # RobotArm, Arm, Hand (real hardware)
│   └── mock_arm.py           # MockRobotArm (simulated, logs to console)
│
├── engine/
│   ├── __init__.py
│   └── executor.py           # CodeExecutor - restricted exec() sandbox
│
└── ui/
    ├── __init__.py
    ├── app.py                # NeoRobotApp(textual.App) - main application
    ├── app.tcss              # Textual CSS stylesheet
    ├── screens/
    │   ├── __init__.py
    │   └── main_screen.py    # MainScreen(textual.Screen) - split editor+console
    └── widgets/
        ├── __init__.py
        ├── code_editor.py    # CodeEditor(TextArea) - left panel
        ├── console.py        # ConsoleOutput(RichLog) - right panel
        └── toolbar.py        # Toolbar(Static/Horizontal) - Run/Stop/Clear buttons
```

---

## Phase 2: Class Designs

### 2.1 `config/settings.py` — Settings

```python
@dataclass
class HardwareConfig:
    upper_arm_pin: int = 9
    lower_arm_pin: int = 10
    hand_pin: int = 11
    use_mock: bool = False      # True = simulated mode

@dataclass  
class AppConfig:
    hardware: HardwareConfig
    editor_theme: str = "monokai"
```

### 2.2 `hardware/robot_arm.py` — RobotArm (fix existing)

```python
class Arm:
    """Single servo-controlled joint."""
    def __init__(self, board: Telemetrix, servo_pin: int)
    def turn_left(self, angle: int) -> None
    def turn_right(self, angle: int) -> None
    def set_angle(self, angle: int) -> None
    @property
    def angle(self) -> int              # renamed from current_angle

class Hand(Arm):
    """Gripper/claw end-effector."""
    def grab(self) -> None              # fixed from 'grap'
    def release(self) -> None

class RobotArm:
    """Top-level controller composing joints."""
    board: Telemetrix
    upper_arm: Arm
    lower_arm: Arm
    hand: Hand
    
    def shutdown(self) -> None          # cleanup board connection
```

### 2.3 `hardware/mock_arm.py` — MockRobotArm

```python
class MockArm:
    """Simulated arm joint that logs instead of moving servos."""
    def turn_left(self, angle: int) -> None   # logs "Turning left {angle} degrees"
    def turn_right(self, angle: int) -> None
    def set_angle(self, angle: int) -> None
    @property
    def angle(self) -> int

class MockHand(MockArm):
    def grab(self) -> None
    def release(self) -> None

class MockRobotArm:
    """Simulated robot arm. Same interface as RobotArm."""
    upper_arm: MockArm
    lower_arm: MockArm
    hand: MockHand
    
    def shutdown(self) -> None
```

A callback mechanism or logging handler routes mock log messages to the console widget.

### 2.4 `engine/executor.py` — CodeExecutor

```python
class ExecutionResult:
    """Result of code execution."""
    output: str          # captured stdout/print output
    error: str | None    # error message if failed
    success: bool

class CodeExecutor:
    """Sandboxed Python code executor.
    
    Uses restricted exec() with a pre-built namespace containing
    only the robot arm API. Students see these as global functions:
      - arm.turn_left(angle)
      - arm.turn_right(angle)  
      - arm.set_angle(angle)
      - arm.grab()
      - arm.release()
      - print(...)
    """
    
    def __init__(self, robot_arm: RobotArm | MockRobotArm)
    def execute(self, code: str) -> ExecutionResult
    
    # Internal:
    # - Builds restricted __builtins__ (only print, range, int, etc.)
    # - Injects `arm` object (a facade exposing student-friendly methods)
    # - Captures stdout via io.StringIO
    # - Catches exceptions and returns friendly error messages
    # - Optionally runs in a thread with timeout
```

**Student-facing API object (`arm`):**

```python
class StudentArmAPI:
    """Simplified facade for students. Injected as `arm` in exec namespace."""
    def __init__(self, robot: RobotArm | MockRobotArm)
    def turn_left(self, angle: int) -> None
    def turn_right(self, angle: int) -> None
    def grab(self) -> None
    def release(self) -> None
    def set_angle(self, angle: int) -> None
```

### 2.5 `ui/app.py` — NeoRobotApp

```python
class NeoRobotApp(textual.app.App):
    """Main TUI application."""
    
    CSS_PATH = "app.tcss"
    TITLE = "NEO Robot - Learn Python with Robotics"
    
    def __init__(self, use_mock: bool = False)
    def on_mount(self) -> None           # Push MainScreen
    
    BINDINGS = [
        Binding("f5", "run_code", "Run"),
        Binding("ctrl+c", "stop_code", "Stop"),
        Binding("ctrl+q", "quit", "Quit"),
    ]
```

### 2.6 `ui/screens/main_screen.py` — MainScreen

```python
class MainScreen(textual.screen.Screen):
    """Split-screen: editor (left) + console (right)."""
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="editor-pane"):
                yield Static("Code Editor", classes="pane-title")
                yield CodeEditor(id="editor")
            with Vertical(id="console-pane"):
                yield Static("Console", classes="pane-title")
                yield ConsoleOutput(id="console")
        yield Toolbar()
        yield Footer()
    
    def action_run_code(self) -> None
        # 1. Get code from CodeEditor
        # 2. Clear console
        # 3. Run via CodeExecutor (in a worker thread)
        # 4. Stream output to ConsoleOutput
    
    def action_stop_code(self) -> None
        # Cancel running worker
```

### 2.7 `ui/widgets/code_editor.py` — CodeEditor

```python
class CodeEditor(TextArea):
    """Code editor widget based on Textual's TextArea.
    
    Features:
    - Python syntax highlighting (built into TextArea)
    - Line numbers (built into TextArea)
    - Tab key inserts spaces
    - Starter template with comments
    """
    
    DEFAULT_CODE = '''# Write your Python code here!
# Use 'arm' to control the robot:
#   arm.turn_left(90)
#   arm.turn_right(45)
#   arm.grab()
#   arm.release()

'''
    
    def __init__(self, **kwargs):
        super().__init__(
            self.DEFAULT_CODE,
            language="python",
            theme="monokai",
            show_line_numbers=True,
            tab_behavior="indent",
            **kwargs,
        )
    
    def get_code(self) -> str:
        return self.text
    
    def set_code(self, code: str) -> None:
        self.load_text(code)
```

### 2.8 `ui/widgets/console.py` — ConsoleOutput

```python
class ConsoleOutput(RichLog):
    """Console output widget using Textual's RichLog.
    
    Displays:
    - Student print() output
    - Execution status messages
    - Error messages (highlighted in red)
    - Hardware feedback (arm movements, grabs, etc.)
    """
    
    def write_output(self, text: str) -> None
        # Write normal output text
    
    def write_error(self, text: str) -> None
        # Write error in red styling
    
    def write_status(self, text: str) -> None
        # Write status info in dim/italic
    
    def clear_console(self) -> None:
        self.clear()
```

### 2.9 `ui/widgets/toolbar.py` — Toolbar

```python
class Toolbar(Horizontal):
    """Bottom toolbar with action buttons."""
    
    def compose(self) -> ComposeResult:
        yield Button("Run (F5)", id="run-btn", variant="success")
        yield Button("Stop", id="stop-btn", variant="error")
        yield Button("Clear Console", id="clear-btn", variant="default")
    
    # Button presses post messages to parent screen
```

---

## Phase 3: UI <-> IO Flow (How the UI works with I/O)

### Data Flow Diagram

```
+--------------------------------------------------------------+
|                      MainScreen                               |
|                                                               |
|  +---------------------+     +-------------------------+     |
|  |    CodeEditor        |     |    ConsoleOutput         |     |
|  |    (TextArea)        |     |    (RichLog)             |     |
|  |                      |     |                          |     |
|  |  Student types:      |     |  > Running code...       |     |
|  |  arm.turn_left(90)   |---->|  > Turning left 90deg    |     |
|  |  arm.grab()          |  3  |  > Grabbing...           |     |
|  |  print("done!")      |     |  > done!                 |     |
|  |                      |     |  > Execution complete    |     |
|  +---------------------+     +-------------------------+     |
|           |                            ^                      |
|           | 1. get code                | 4. write output      |
|           v                            |                      |
|  +------------------------------------------+                |
|  |         CodeExecutor                      |                |
|  |   exec(code, restricted_namespace)        |                |
|  |   namespace = {                           |                |
|  |     "arm": StudentArmAPI(robot),          |                |
|  |     "print": captured_print,              |                |
|  |     "__builtins__": safe_builtins,        |                |
|  |   }                                       |                |
|  +------------------+-----------------------+                |
|                     | 2. hardware commands                    |
|                     v                                         |
|  +------------------------------------------+                |
|  |   RobotArm / MockRobotArm                |                |
|  |   +-- upper_arm.turn_left(90)             |                |
|  |   +-- hand.grab()                         |                |
|  |   +-- (Telemetrix serial I/O)             |                |
|  +------------------------------------------+                |
+--------------------------------------------------------------+
```

### Step-by-step I/O Flow

1. **User presses F5 (or clicks Run button)**
   - `MainScreen.action_run_code()` is triggered
   - Code string is extracted from `CodeEditor.get_code()`

2. **Execution begins in a Textual worker thread**
   - `ConsoleOutput.write_status("Running code...")` 
   - `CodeExecutor.execute(code)` runs in `@work(thread=True)` to avoid blocking the UI
   - The executor builds a restricted namespace and calls `exec(code, namespace)`

3. **During execution, I/O flows through callbacks**
   - `print()` calls are intercepted: output captured in `io.StringIO`, forwarded to `ConsoleOutput.write_output()` via `app.call_from_thread()`
   - Hardware commands (e.g., `arm.turn_left(90)`) call `RobotArm.upper_arm.turn_left(90)`, which sends servo commands over serial via Telemetrix
   - In mock mode: hardware calls log descriptive text, routed to `ConsoleOutput.write_status()`

4. **Execution completes**
   - On success: `ConsoleOutput.write_status("Execution complete")`
   - On error: `ConsoleOutput.write_error("Error on line 3: ...")` with a student-friendly message
   - Worker thread finishes, UI is fully responsive again

### Threading Model

```
Main Thread (Textual event loop):
  +-- Handles all UI rendering and input
  +-- Receives messages from worker via call_from_thread()
  +-- Updates ConsoleOutput widget

Worker Thread (per code execution):
  +-- Runs CodeExecutor.execute()
  +-- exec() runs student code synchronously
  +-- print() output captured via StringIO
  +-- Hardware commands run synchronously (blocking I/O to servos)
```

### Key Design Decision: `call_from_thread()`
Since Textual is single-threaded for UI updates, the worker thread must use `self.app.call_from_thread(console.write_output, text)` to safely post output back to the console widget. This is Textual's built-in mechanism for cross-thread communication.

---

## Phase 4: Textual CSS (`app.tcss`)

```css
/* Split-screen layout: 50/50 horizontal */
Horizontal {
    height: 1fr;
}

#editor-pane {
    width: 1fr;
    border: solid green;
}

#console-pane {
    width: 1fr;  
    border: solid blue;
}

.pane-title {
    dock: top;
    text-style: bold;
    background: $accent;
    padding: 0 1;
    height: 1;
}

Toolbar {
    dock: bottom;
    height: 3;
    padding: 0 1;
}
```

---

## Phase 5: Implementation Order

| Step | Task | Files |
|------|------|-------|
| 1 | Rename `src/neo-robot` to `src/neo_robot` | directory rename |
| 2 | Create `pyproject.toml` with dependencies and entry point | `pyproject.toml` |
| 3 | Fix `robot_arm.py` bugs (name collision, typo, pin_mode) | `hardware/robot_arm.py` |
| 4 | Implement `Arm` and `Hand` methods with Telemetrix calls | `hardware/robot_arm.py` |
| 5 | Create `MockRobotArm` with logging | `hardware/mock_arm.py` |
| 6 | Create `settings.py` config | `config/settings.py` |
| 7 | Build `CodeEditor` widget | `ui/widgets/code_editor.py` |
| 8 | Build `ConsoleOutput` widget | `ui/widgets/console.py` |
| 9 | Build `Toolbar` widget | `ui/widgets/toolbar.py` |
| 10 | Build `CodeExecutor` with sandbox | `engine/executor.py` |
| 11 | Build `MainScreen` composing widgets | `ui/screens/main_screen.py` |
| 12 | Build `NeoRobotApp` | `ui/app.py` |
| 13 | Create `app.tcss` stylesheet | `ui/app.tcss` |
| 14 | Create `__main__.py` entry point | `__main__.py` |
| 15 | Test end-to-end with mock hardware | manual testing |

---

## Notes

- **Target hardware (RPi, 2GB RAM)**: Keep dependencies minimal. Textual + thingbot-telemetrix. No heavy frameworks.
- **Python 3.11**: Use modern features (match/case, type hints, dataclasses).
- **Textual version**: Use `textual>=0.40` for `TextArea` widget with syntax highlighting (available since Textual 0.38+).
- **Security**: The restricted exec namespace prevents students from importing modules, accessing the filesystem, or running arbitrary system commands. Only `arm.*`, `print()`, `range()`, `int()`, `float()`, `str()`, `len()`, `list()`, `True`, `False`, `None` are exposed.
