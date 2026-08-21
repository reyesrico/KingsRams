import unittest

from kingsrams.motion.standing import StandingController, T1_MOTORS


class StandingControllerTests(unittest.TestCase):
    def test_commands_every_t1_motor_once(self) -> None:
        action = StandingController().action()

        for motor in T1_MOTORS:
            self.assertEqual(action.count(f"({motor} "), 1)

    def test_uses_nominal_pd_gains(self) -> None:
        action = StandingController().action()

        self.assertEqual(action.count(" 25.0 0.6 0.0)"), len(T1_MOTORS))