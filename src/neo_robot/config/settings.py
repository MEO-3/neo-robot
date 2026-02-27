"""Application-wide configuration settings."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class HardwareConfig:
    """Pin assignments and hardware mode settings."""

    upper_arm_pin: int = 9
    lower_arm_pin: int = 10
    hand_pin: int = 11
    use_mock: bool = False  # True = simulated mode (no hardware needed)


@dataclass
class AppConfig:
    """Top-level application configuration."""

    hardware: HardwareConfig = field(default_factory=HardwareConfig)
    editor_theme: str = "monokai"
    app_title: str = "NEO Robot - Learn Python with Robotics"
