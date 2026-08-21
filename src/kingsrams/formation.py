"""Player roles and the default KingsRams formation."""

from dataclasses import dataclass
from enum import StrEnum


class PlayerRole(StrEnum):
    GOALKEEPER = "goalkeeper"
    DEFENDER = "defender"
    MIDFIELDER = "midfielder"
    STRIKER = "striker"


@dataclass(frozen=True, slots=True)
class RoleAssignment:
    uniform_number: int
    role: PlayerRole
    beam_pose: tuple[float, float, float]


DEFAULT_FORMATION = (
    RoleAssignment(1, PlayerRole.GOALKEEPER, (29.0, 0.0, 0.0)),
    RoleAssignment(2, PlayerRole.DEFENDER, (22.0, 8.0, 0.0)),
    RoleAssignment(3, PlayerRole.DEFENDER, (22.0, -8.0, 0.0)),
    RoleAssignment(4, PlayerRole.MIDFIELDER, (14.0, 10.0, 0.0)),
    RoleAssignment(5, PlayerRole.MIDFIELDER, (14.0, -10.0, 0.0)),
    RoleAssignment(6, PlayerRole.STRIKER, (7.0, 6.0, 0.0)),
    RoleAssignment(7, PlayerRole.STRIKER, (7.0, -6.0, 0.0)),
)


def assignment_for(uniform_number: int) -> RoleAssignment:
    """Return the formation assignment for a valid uniform number."""
    if not 1 <= uniform_number <= len(DEFAULT_FORMATION):
        raise ValueError(f"uniform number must be between 1 and {len(DEFAULT_FORMATION)}")
    return DEFAULT_FORMATION[uniform_number - 1]