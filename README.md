# KingsRams

KingsRams is a personal RoboCup 3D Soccer Simulation team for experimenting with
AI decision models, coordinated tactics, and humanoid control.

## macOS setup

Requirements: macOS on Apple Silicon or Intel, Python 3.10+, and the Xcode
Command Line Tools. On the current machine, Python 3.12.8 and the command-line
tools are already available.

```sh
chmod +x scripts/setup-macos.sh run-simulator.sh start.sh kill.sh
scripts/setup-macos.sh
./run-simulator.sh
./start.sh
```

Run `./run-simulator.sh` in Terminal 1 to keep the simulator and viewer in the
foreground. Run `./start.sh` in Terminal 2 to connect the seven KingsRams agents.
Close the simulator window or press `Ctrl+C` in Terminal 1 to stop the server.
The team launcher refuses a second start while its existing agents are alive.

Stop the team and simulator with:

```sh
./kill.sh
```

Environment overrides `KINGRAMS_HOST` and `KINGRAMS_PORT` let the qualification
scripts connect to a simulator on another machine.

## Current capability

The first client connects all seven Booster T1 robots allowed by the `ssim26`
rule book and places a balanced formation: one goalkeeper, two defenders, two midfielders, and two
strikers. Standing is the default motion and uses the locomotion policy with a
zero velocity target to actively balance the free-root humanoid. A fixed joint
pose alone cannot keep a simulated humanoid upright. Walking uses the same
official RCSSServerMJ T1 policy and accepts normalized forward, lateral, and turn
velocities in the range `-1.0` to `1.0`.

Start the full team standing:

```sh
./start.sh
```

Start the full team walking forward at half speed:

```sh
KINGRAMS_MOTION=walk KINGRAMS_FORWARD=0.5 ./start.sh
```

For isolated motion development, start one robot directly:

```sh
.venv/bin/kingsrams-agent --uniform-number 1 --motion walk --forward 0.5
```

The walking controller stabilizes for 50 simulation cycles before applying the
requested velocity. Ball-playing behavior still requires localization, world
state, role decisions, passing, and coordinated strategy.

## Layout

```text
src/kingsrams/       Team-owned agent, formation, and protocol code
tests/               Fast team tests
scripts/             macOS environment setup
simulator/           Simulator boundary and legacy SimSpark decision
docs/                League and qualification research notes
run-simulator.sh      Foreground graphical simulator launcher for macOS
start.sh / kill.sh   Competition-compatible team lifecycle entry points
```

Run tests with:

```sh
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
```

See [docs/robocup-3d.md](docs/robocup-3d.md) for league context and
[simulator/README.md](simulator/README.md) for the simulator decision.