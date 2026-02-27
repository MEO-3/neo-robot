# NEO Robot

A terminal-based educational platform that teaches K-12 students Python programming through controlling a physical robotic arm. Built with [Textual](https://textual.textualize.io/) for the Raspberry Pi (CLI-only, no desktop required).

Students write Python code in a split-screen TUI — code editor on the left, live console output on the right — and see their programs drive a 3-joint robotic arm in real time. A simulation mode (`--mock`) allows development and learning without hardware.

## Features

- **Split-screen TUI** — syntax-highlighted code editor + live console output
- **Two modes** — Script mode (F5 to run multi-line programs) and Interactive REPL mode (F2 to toggle, line-by-line execution with persistent state)
- **Sandboxed execution** — restricted `exec()` with whitelisted builtins; no imports, no filesystem, no system calls
- **Real hardware** — drives servos via Telemetrix protocol over serial
- **Simulation mode** — `--mock` flag logs arm movements to console; auto-fallback if hardware connection fails
- **Threaded execution** — code runs in a background worker thread to keep the UI responsive
- **Student-friendly errors** — error messages include line numbers
- **Command history** — Up/Down arrows in interactive mode

## Requirements

- Python 3.11+
- [Textual](https://pypi.org/project/textual/) >= 0.40
- [thingbot-telemetrix](https://pypi.org/project/thingbot-telemetrix/) (only needed for real hardware)

## Installation

```bash
# Install in development mode
pip install -e .

# With dev dependencies (textual-dev, pytest)
pip install -e ".[dev]"
```

## Usage

```bash
# Run with real hardware
neo-robot

# Run in simulation mode (no hardware required)
neo-robot --mock

# Or via Python module
python -m neo_robot --mock
```

If `--mock` is not passed, the app attempts real hardware. On failure it automatically falls back to simulation mode with a warning.

## Keyboard Shortcuts

| Key | Action |
|---|---|
| `F5` | Run code (script mode) |
| `F2` | Toggle script / interactive mode |
| `Ctrl+X` | Stop execution |
| `Ctrl+L` | Clear console output |
| `Ctrl+E` | Clear code editor |
| `Ctrl+Q` | Quit |
| `Up/Down` | Navigate command history (interactive mode) |

## Student API

All code runs in a sandbox with an `arm` object and a small set of safe builtins.

### Robot arm

```python
arm.turn_left(angle)      # Rotate upper arm left (default 90)
arm.turn_right(angle)     # Rotate upper arm right (default 90)
arm.set_angle(angle)      # Set upper arm to absolute angle (0-180)
arm.elbow_left(angle)     # Rotate elbow left (default 90)
arm.elbow_right(angle)    # Rotate elbow right (default 90)
arm.grab()                # Close the gripper
arm.release()             # Open the gripper
arm.delay(seconds)        # Pause execution
```

### Built-in functions

```python
delay(seconds)            # Pause execution (alias for arm.delay)
print(...)                # Print to console (captured, sandboxed)
```

### Interactive mode commands

| Command | Description |
|---|---|
| `help` | Show available commands |
| `clear` | Clear the REPL log |
| `history` | Show command history |

## License

AGPL-3.0 License (see LICENSE file)