"""Stable standing controller for the Booster T1 robot."""

import math


T1_MOTORS = (
    "he1", "he2",
    "lae1", "lae2", "lae3", "lae4",
    "rae1", "rae2", "rae3", "rae4",
    "te1",
    "lle1", "lle2", "lle3", "lle4", "lle5", "lle6",
    "rle1", "rle2", "rle3", "rle4", "rle5", "rle6",
)

T1_NOMINAL_POSITION_RADIANS = (
    0.0, 0.0,
    0.0, -1.4, 0.0, -0.4,
    0.0, 1.4, 0.0, 0.4,
    0.0,
    -0.4, 0.0, 0.0, 0.8, -0.4, 0.0,
    -0.4, 0.0, 0.0, 0.8, -0.4, 0.0,
)


class StandingController:
    """Place the T1 in its nominal pose before active balance takes over."""

    def __init__(self, proportional_gain: float = 25.0, derivative_gain: float = 0.6) -> None:
        self.proportional_gain = proportional_gain
        self.derivative_gain = derivative_gain

    def action(self) -> str:
        return "".join(
            self._motor_command(motor, position)
            for motor, position in zip(T1_MOTORS, T1_NOMINAL_POSITION_RADIANS, strict=True)
        )

    def _motor_command(self, motor: str, position_radians: float) -> str:
        position_degrees = math.degrees(position_radians)
        return (
            f"({motor} {position_degrees:.2f} 0.0 "
            f"{self.proportional_gain:.1f} {self.derivative_gain:.1f} 0.0)"
        )