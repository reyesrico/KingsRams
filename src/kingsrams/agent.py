"""Minimal safe T1 agent for the RCSSServerMJ simulator."""

import argparse
import math
import socket

from kingsrams.formation import assignment_for
from kingsrams.protocol import receive_message, send_message


TEAM_NAME = "KingsRams"
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
HOLD_POSITION_ACTION = "".join(
    f"({motor} {math.degrees(position):.2f} 0.0 25.0 0.6 0.0)"
    for motor, position in zip(T1_MOTORS, T1_NOMINAL_POSITION_RADIANS, strict=True)
)


def run_agent(host: str, port: int, uniform_number: int) -> None:
    assignment = assignment_for(uniform_number)
    with socket.create_connection((host, port)) as connection:
        connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        send_message(connection, f"(init T1 {TEAM_NAME} {uniform_number})")

        has_beamed = False
        while True:
            receive_message(connection)
            action = HOLD_POSITION_ACTION
            if not has_beamed:
                x, y, rotation = assignment.beam_pose
                action += f"(beam {x} {y} {rotation})"
                has_beamed = True
            send_message(connection, action)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one KingsRams T1 agent.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=60000)
    parser.add_argument("--uniform-number", type=int, choices=range(1, 8), required=True)
    args = parser.parse_args()

    try:
        run_agent(args.host, args.port, args.uniform_number)
    except (ConnectionError, KeyboardInterrupt):
        return


if __name__ == "__main__":
    main()