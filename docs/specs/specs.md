---
title: NEO Robot Project Summary
last_updated: 2026-03-19
---

# NEO Robot – Project Summary

## Purpose
NEO Robot is a terminal-based educational platform for K–12 students to learn Python by controlling a 3‑joint robotic arm. It runs as a Textual TUI on Raspberry Pi and supports real hardware or a simulation mode.

## Key Features
- Split-screen TUI: code editor (left) + live console (right)
- Script mode (F5) for multi-line programs
- Interactive REPL mode (F2) with persistent state and command history
- Sandboxed execution with a restricted builtins whitelist
- Real hardware via Telemetrix or auto-fallback mock simulation
- Background worker execution to keep UI responsive
- Student-friendly error messages with line numbers

## Runtime Entry Points
- CLI: `neo-robot` (from `pyproject.toml` scripts)
- Module: `python -m neo_robot`
- Main entry: `neo_robot.ui.app:main` in `src/neo_robot/ui/app.py`

## Architecture Overview
```
neo_robot/
  ui/              Textual TUI
  engine/          Sandboxed code execution
  hardware/        Real + mock robot arm implementations
  config/          App + hardware configuration
```

### UI Layer (Textual)
- `NeoRobotApp` (`src/neo_robot/ui/app.py`)
  - Parses CLI args (`--mock`)
  - Initializes hardware (real or mock)
  - Creates `CodeExecutor` and pushes `MainScreen`
- `MainScreen` (`src/neo_robot/ui/screens/main_screen.py`)
  - Two modes: Script (editor+console) and Interactive REPL
  - Uses background workers for execution (`@work(thread=True)`)
  - Hotkeys: F5 run, F2 toggle, Ctrl+X stop, Ctrl+L clear console, Ctrl+E clear editor, Ctrl+Q quit
- Widgets:
  - `CodeEditor` (`src/neo-robot/src/neo_robot/ui/widgets/code_editor.py`): TextArea with Python syntax highlighting
  - `ConsoleOutput` (`src/neo-robot/src/neo_robot/ui/widgets/console.py`): RichLog for status/output/errors
  - `InteractiveConsole` (`src/neo-robot/src/neo_robot/ui/widgets/interactive_console.py`): REPL with history and built-in commands (`help`, `clear`, `history`)

### Engine Layer (Sandboxed Execution)
- `CodeExecutor` (`src/neo_robot/engine/executor.py`)
  - Runs code with restricted `__builtins__`
  - Injects `arm` (StudentArmAPI) and `delay()` alias
  - Captures `print()` output
  - Script mode: `execute(code)` runs in fresh namespace
  - Interactive mode: `execute_line(line)` runs in persistent namespace
- `SAFE_BUILTINS` whitelist (`src/neo_robot/engine/apis.py`)
  - Types/functions: `int`, `float`, `str`, `list`, `range`, `len`, `abs`, `min`, `max`, etc.

### Student API
- `StudentArmAPI` (`src/neo_robot/engine/apis.py`)
  - `arm.turn_left(angle)`, `arm.turn_right(angle)`, `arm.set_angle(angle)`
  - `arm.lift_up(angle)`, `arm.lower_down(angle)`
  - `arm.grab()`, `arm.release()`
  - `arm.delay(seconds)` (aliased as global `delay()`)

### Hardware Layer
- Real hardware: `RobotArm` (`src/neo_robot/hardware/robot_arm.py`)
  - Uses `thingbot-telemetrix` to drive servo pins
  - Joints: `upper_arm`, `lower_arm`, `hand`
- Mock hardware: `MockRobotArm` (`src/neo_robot/hardware/mock_arm.py`)
  - Logs actions instead of driving servos
  - Auto-used when `--mock` is set or real hardware fails to init

### Configuration
- `AppConfig` / `HardwareConfig` (`src/neo_robot/config/settings.py`)
  - Hardware pin assignments and mock-mode flag
  - Editor theme and app title defaults

## Dependencies
- Python 3.11+
- `textual>=0.40`
- `thingbot-telemetrix` (only for real hardware)

## Behavior Notes
- Hardware initialization attempts real hardware unless `--mock` is set; failures fall back to mock with a warning.
- Execution runs in background worker threads; UI updates happen via `call_from_thread`.
- Interactive mode preserves variables between commands.

## Files of Interest
- `README.md` – user-facing overview and shortcuts
- `src/neo_robot/ui/app.py` – CLI + app bootstrapping
- `src/neo_robot/ui/screens/main_screen.py` – core UI flow and bindings
- `src/neo_robot/engine/executor.py` – sandboxed execution
- `src/neo_robot/engine/apis.py` – Student API + safe builtins
- `src/neo_robot/hardware/robot_arm.py` – real hardware control
- `src/neo_robot/hardware/mock_arm.py` – simulation
- `src/neo_robot/config/settings.py` – configuration defaults
