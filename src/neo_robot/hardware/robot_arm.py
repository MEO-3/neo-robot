"""Hardware control for the physical robotic arm via Telemetrix."""

from __future__ import annotations

from thingbot_telemetrix import Telemetrix


# Servo angle limits
_MIN_ANGLE = 0
_MAX_ANGLE = 180


class Arm:
    """Single servo-controlled joint.

    Wraps a servo connected to the Telemetrix board and provides
    directional movement helpers.
    """

    _MIN_ANGLE = 0
    _MAX_ANGLE = 180

    def __init__(self, board: Telemetrix, servo_pin: int, name: str = "arm") -> None:
        self.board = board.thingbot()
        self.pin = servo_pin
        self.name = name
        self._current_angle: int = 0

    def turn_left(self, angle: int) -> None:
        """Decrease the servo angle by *angle* degrees (turn left)."""
        new_angle = self._current_angle + angle
        self.board.control_servo(self.pin, new_angle)

    def turn_right(self, angle: int) -> None:
        """Increase the servo angle by *angle* degrees (turn right)."""
        new_angle = self._current_angle - angle
        self.board.control_servo(self.pin, new_angle)
        
    def set_angle(self, angle: int) -> None:
        """Set the servo to an absolute angle."""
        self.board.control_servo(self.pin, angle)
        self._current_angle = angle

    @property
    def angle(self) -> int:
        """Return the current angle of this joint."""
        return self._current_angle


class Hand(Arm):
    """Gripper / claw end-effector attached to a servo."""
    _GRAP_ANGLE = 0
    _RELEASE_ANGLE = 45

    def __init__(self, board: Telemetrix, servo_pin: int) -> None:
        super().__init__(board, servo_pin, name="hand")
        self._grabbed = False

    def grab(self) -> None:
        """Close the gripper."""
        self.board.control_servo(self.pin, self._GRAP_ANGLE)
        self._grabbed = True

    def release(self) -> None:
        """Open the gripper."""
        self.board.control_servo(self.pin, self._RELEASE_ANGLE)
        self._grabbed = False

    @property
    def is_grabbed(self) -> bool:
        return self._grabbed


class RobotArm:
    """Top-level controller that composes three servo joints.

    Joints
    ------
    * ``upper_arm`` – shoulder / base rotation (pin 9)
    * ``lower_arm`` – elbow (pin 10)
    * ``hand``      – gripper (pin 11)
    """

    def __init__(
        self,
        upper_arm_pin: int = 9,
        lower_arm_pin: int = 10,
        hand_pin: int = 11,
    ) -> None:
        self.board = Telemetrix()
        self.upper_arm = Arm(self.board, servo_pin=upper_arm_pin, name="upper_arm")
        self.lower_arm = Arm(self.board, servo_pin=lower_arm_pin, name="lower_arm")
        self.hand = Hand(self.board, servo_pin=hand_pin)
        
        self.lower_arm.set_angle(90)  # Start with the lower arm at a neutral position
        self.upper_arm.set_angle(90)  # Start with the upper arm at a neutral position
        self.hand.release()  # Start with the hand open

    def shutdown(self) -> None:
        """Release all servos and close the board connection."""
        self.board.shutdown()
