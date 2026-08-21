"""Minimal safe T1 agent for the RCSSServerMJ simulator."""

import argparse
import socket

from kingsrams.formation import assignment_for
from kingsrams.motion.standing import StandingController
from kingsrams.motion.walking import VelocityCommand, WalkingController
from kingsrams.protocol import receive_message, send_message


TEAM_NAME = "KingsRams"


def run_agent(
    host: str,
    port: int,
    uniform_number: int,
    motion: str,
    velocity: VelocityCommand,
) -> None:
    assignment = assignment_for(uniform_number)
    standing = StandingController()
    walking = WalkingController()
    commanded_velocity = velocity if motion == "walk" else VelocityCommand()
    with socket.create_connection((host, port)) as connection:
        connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        send_message(connection, f"(init T1 {TEAM_NAME} {uniform_number})")

        has_beamed = False
        while True:
            perception = receive_message(connection)
            if not has_beamed:
                x, y, rotation = assignment.beam_pose
                action = standing.action() + f"(beam {x} {y} {rotation})"
                has_beamed = True
                walking.reset()
            else:
                action = walking.action(perception, commanded_velocity)
            send_message(connection, action)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one KingsRams T1 agent.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=60000)
    parser.add_argument("--uniform-number", type=int, choices=range(1, 8), required=True)
    parser.add_argument("--motion", choices=("stand", "walk"), default="stand")
    parser.add_argument("--forward", type=float, default=0.0)
    parser.add_argument("--lateral", type=float, default=0.0)
    parser.add_argument("--turn", type=float, default=0.0)
    args = parser.parse_args()

    try:
        run_agent(
            args.host,
            args.port,
            args.uniform_number,
            args.motion,
            VelocityCommand(args.forward, args.lateral, args.turn),
        )
    except (ConnectionError, KeyboardInterrupt):
        return


if __name__ == "__main__":
    main()