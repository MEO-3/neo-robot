"""Application-wide configuration settings."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class HardwareConfig:
    """Pin assignments and hardware mode settings."""

    upper_arm_pin: int = 5
    lower_arm_pin: int = 4
    hand_pin: int = 3
    use_mock: bool = False  # True = simulated mode (no hardware needed)


@dataclass
class AppConfig:
    """Top-level application configuration."""

    hardware: HardwareConfig = field(default_factory=HardwareConfig)
    editor_theme: str = "monokai"
    app_title: str = "NEO Robot - Learn Python with Robotics"
