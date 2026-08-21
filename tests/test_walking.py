import unittest

import numpy as np

from kingsrams.motion.standing import T1_MOTORS
from kingsrams.motion.walking import VelocityCommand, WalkingController, parse_sensor_message


def sensor_message() -> str:
    joints = "".join(f"(HJ (n j{index}) (ax 0) (vx 0))" for index in range(len(T1_MOTORS)))
    return joints + "(GYR (rt 0 0 0))(quat (q 1 0 0 0))"


class VelocityCommandTests(unittest.TestCase):
    def test_clips_each_velocity_axis(self) -> None:
        command = VelocityCommand(forward=2.0, lateral=-2.0, turn=0.5)

        np.testing.assert_array_equal(command.as_array(), np.array([1.0, -1.0, 0.5], dtype=np.float32))


class SensorParserTests(unittest.TestCase):
    def test_collects_repeated_joint_sensors(self) -> None:
        sensors = parse_sensor_message(sensor_message())

        self.assertEqual(len(sensors["HJ"]), len(T1_MOTORS))
        self.assertEqual(sensors["GYR"]["rt"], [0.0, 0.0, 0.0])
        self.assertEqual(sensors["quat"]["q"], [1.0, 0.0, 0.0, 0.0])


class WalkingControllerTests(unittest.TestCase):
    def test_policy_emits_finite_command_for_every_motor(self) -> None:
        controller = WalkingController(warmup_cycles=0)

        action = controller.action(sensor_message(), VelocityCommand(forward=0.5))

        for motor in T1_MOTORS:
            self.assertEqual(action.count(f"({motor} "), 1)
        self.assertNotIn("nan", action.lower())
        self.assertNotIn("inf", action.lower())