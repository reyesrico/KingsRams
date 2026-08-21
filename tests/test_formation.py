import unittest
from collections import Counter

from kingsrams.formation import DEFAULT_FORMATION, PlayerRole, assignment_for


class DefaultFormationTests(unittest.TestCase):
    def test_assigns_every_uniform_number_once(self) -> None:
        uniform_numbers = [assignment.uniform_number for assignment in DEFAULT_FORMATION]

        self.assertEqual(uniform_numbers, list(range(1, 8)))

    def test_uses_balanced_seven_player_roles(self) -> None:
        roles = Counter(assignment.role for assignment in DEFAULT_FORMATION)

        self.assertEqual(
            roles,
            {
                PlayerRole.GOALKEEPER: 1,
                PlayerRole.DEFENDER: 2,
                PlayerRole.MIDFIELDER: 2,
                PlayerRole.STRIKER: 2,
            },
        )

    def test_rejects_uniform_number_outside_team(self) -> None:
        with self.assertRaises(ValueError):
            assignment_for(8)
        with self.assertRaises(ValueError):
            assignment_for(0)


if __name__ == "__main__":
    unittest.main()