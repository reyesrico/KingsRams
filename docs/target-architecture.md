```
src/kingsrams/
├── agent.py              # Perception-action loop
├── protocol.py           # Server message transport
├── formation.py          # Team roles and starting positions
├── perception/
│   ├── parser.py         # Convert messages into sensor values
│   ├── localization.py   # Estimate robot position
│   └── world_model.py    # Ball, teammates, opponents
├── motion/
│   ├── standing.py
│   ├── walking.py
│   ├── turning.py
│   ├── kicking.py
│   └── recovery.py
├── strategy/
│   ├── roles.py
│   ├── decisions.py
│   ├── positioning.py
│   └── passing.py
└── learning/
    └── policies.py

## Implemented motion

- `motion/standing.py` owns the nominal Booster T1 initialization posture.
- `motion/walking.py` parses hinge-joint, gyroscope, and orientation sensors and
    runs the official RCSSServerMJ recurrent T1 locomotion policy. A zero velocity
    command provides active standing balance; nonzero velocity produces walking.
- `agent.py` remains the perception-action coordinator and selects a motion
    controller; it should not absorb controller internals.
```

## About run_agent()

```
while True:
    raw_perception = receive_message(connection)
    observation = perception_parser.parse(raw_perception)
    world_state.update(observation)

    decision = strategy.choose_action(
        world_state=world_state,
        role=assignment.role,
    )

    motor_command = motion_controller.execute(decision)
    send_message(connection, motor_command)
```