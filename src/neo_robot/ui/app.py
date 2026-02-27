"""NEO Robot – main Textual application."""

from __future__ import annotations

import argparse
from typing import Any

from textual.app import App

from neo_robot.config.settings import AppConfig, HardwareConfig
from neo_robot.engine import CodeExecutor
from neo_robot.hardware.mock_arm import MockRobotArm
from neo_robot.ui.screens.main_screen import MainScreen


class NeoRobotApp(App):
    """Textual TUI application for the NEO ThingBot educational platform."""

    CSS_PATH = "app.tcss"
    TITLE = "Bình dân học STEM"

    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
    ]

    def __init__(self, config: AppConfig | None = None, **kwargs) -> None:  # type: ignore[override]
        super().__init__(**kwargs)
        self.config = config or AppConfig()
        self._robot: Any = None
        self._executor: CodeExecutor | None = None

    # -- lifecycle ------------------------------------------------------

    def on_mount(self) -> None:
        """Initialise hardware and push the main screen."""
        hw = self.config.hardware

        if hw.use_mock:
            self._robot = MockRobotArm()
        else:
            # Attempt real hardware; fall back to mock on import/connection error
            try:
                from neo_robot.hardware.robot_arm import RobotArm

                self._robot = RobotArm(
                    upper_arm_pin=hw.upper_arm_pin,
                    lower_arm_pin=hw.lower_arm_pin,
                    hand_pin=hw.hand_pin,
                )
            except Exception:
                self.notify(
                    "Could not connect to hardware – using simulation mode.",
                    severity="warning",
                    timeout=5,
                )
                self._robot = MockRobotArm()

        self._executor = CodeExecutor(self._robot)
        self.push_screen(MainScreen(self._executor))

    def on_unmount(self) -> None:
        """Clean up hardware on exit."""
        if self._robot is not None:
            self._robot.shutdown()


# -- CLI entry point -------------------------------------------------------


def main() -> None:
    """Parse CLI arguments and launch the TUI."""
    parser = argparse.ArgumentParser(
        description="NEO ThingBot: a Textual TUI for controlling a simple robot arm and learning programming concepts.",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        default=False,
        help="Run in simulation mode (no hardware required)",
    )
    args = parser.parse_args()

    config = AppConfig(
        hardware=HardwareConfig(use_mock=args.mock),
    )
    app = NeoRobotApp(config=config)
    app.run()


if __name__ == "__main__":
    main()
