"""Policy-backed locomotion controller for the Booster T1 robot."""

import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import torch
from torch import nn
from torch.nn import functional as functional

from kingsrams.motion.standing import T1_MOTORS, T1_NOMINAL_POSITION_RADIANS


POLICY_PATH = Path(__file__).with_name("assets") / "locomotion_nn.pth"
OBSERVATION_SIZE = 82
ACTION_SIZE = len(T1_MOTORS)


@dataclass(frozen=True, slots=True)
class VelocityCommand:
    """Desired normalized robot velocity in its local coordinate frame."""

    forward: float = 0.0
    lateral: float = 0.0
    turn: float = 0.0

    def as_array(self) -> np.ndarray:
        return np.clip(
            np.array([self.forward, self.lateral, self.turn], dtype=np.float32),
            -1.0,
            1.0,
        )


class _FlaxCompatibleGRUCell(nn.Module):
    def __init__(self, input_size: int, hidden_size: int) -> None:
        super().__init__()
        self.ir = nn.Linear(input_size, hidden_size, bias=True)
        self.iz = nn.Linear(input_size, hidden_size, bias=True)
        self.in_proj = nn.Linear(input_size, hidden_size, bias=True)
        self.hr = nn.Linear(hidden_size, hidden_size, bias=False)
        self.hz = nn.Linear(hidden_size, hidden_size, bias=False)
        self.hn = nn.Linear(hidden_size, hidden_size, bias=True)

    def forward(self, inputs: torch.Tensor, hidden: torch.Tensor) -> torch.Tensor:
        reset = torch.sigmoid(self.ir(inputs) + self.hr(hidden))
        update = torch.sigmoid(self.iz(inputs) + self.hz(hidden))
        candidate = torch.tanh(self.in_proj(inputs) + reset * self.hn(hidden))
        return (1.0 - update) * candidate + update * hidden


class _WalkingPolicy(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.register_buffer(
            "policy_observation_indices",
            torch.arange(OBSERVATION_SIZE, dtype=torch.long),
            persistent=False,
        )
        self.gru_obs_encoder_dense = nn.Linear(OBSERVATION_SIZE, 128)
        self.gru_obs_encoder_ln = nn.LayerNorm(128, eps=1e-6)
        self.obs_encoder_dense = nn.Linear(OBSERVATION_SIZE, 128)
        self.obs_encoder_ln = nn.LayerNorm(128, eps=1e-6)
        self.gru = _FlaxCompatibleGRUCell(128, 64)
        self.gru_ln = nn.LayerNorm(64, eps=1e-6)
        self.torso_dense1 = nn.Linear(192, 512)
        self.torso_ln1 = nn.LayerNorm(512, eps=1e-6)
        self.torso_dense2 = nn.Linear(512, 256)
        self.torso_dense3 = nn.Linear(256, 128)
        self.mean_head = nn.Linear(128, ACTION_SIZE)
        self.policy_logstd = nn.Parameter(
            torch.full((1, ACTION_SIZE), math.log(0.0839034914970398), dtype=torch.float32)
        )

    def initialize_carry(self, device: torch.device) -> torch.Tensor:
        return torch.zeros(1, 64, dtype=torch.float32, device=device)

    def forward(self, observation: torch.Tensor, hidden: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        selected = observation.index_select(-1, self.policy_observation_indices)
        gru_observation = functional.elu(self.gru_obs_encoder_ln(self.gru_obs_encoder_dense(selected)))
        next_hidden = self.gru(gru_observation, hidden)
        observation_latent = functional.elu(self.obs_encoder_ln(self.obs_encoder_dense(selected)))
        hidden_latent = functional.elu(self.gru_ln(next_hidden))
        torso = torch.cat([observation_latent, hidden_latent], dim=-1)
        torso = functional.elu(self.torso_ln1(self.torso_dense1(torso)))
        torso = functional.elu(self.torso_dense2(torso))
        torso = functional.elu(self.torso_dense3(torso))
        return self.mean_head(torso), next_hidden


class WalkingController:
    """Convert simulator perceptions and velocity goals into T1 joint commands."""

    def __init__(self, policy_path: Path = POLICY_PATH, warmup_cycles: int = 50) -> None:
        if not policy_path.is_file():
            raise FileNotFoundError(f"walking policy not found: {policy_path}")

        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        self.policy = _WalkingPolicy().to(self.device)
        state = torch.load(policy_path, map_location=self.device, weights_only=True)
        self.policy.load_state_dict(state, strict=True)
        self.policy.eval()

        self.nominal_positions = np.array(T1_NOMINAL_POSITION_RADIANS, dtype=np.float32)
        self.warmup_cycles = warmup_cycles
        self.reset()

    def reset(self) -> None:
        self.previous_action = np.zeros(ACTION_SIZE, dtype=np.float32)
        self.hidden = self.policy.initialize_carry(self.device)
        self.remaining_warmup_cycles = self.warmup_cycles
        self.gait_phase = np.array([0.0, -np.pi], dtype=np.float32)

    def action(self, perception: str, velocity: VelocityCommand) -> str:
        sensors = parse_sensor_message(perception)
        observation = self._observation(sensors, velocity)

        with torch.no_grad():
            tensor = torch.from_numpy(observation).to(self.device).unsqueeze(0)
            policy_action, next_hidden = self.policy(tensor, self.hidden)

        action = policy_action.squeeze(0).cpu().numpy().astype(np.float32)
        targets = self.nominal_positions + 0.5 * action
        self.previous_action = action
        self.hidden = next_hidden
        self.gait_phase = _wrap_to_pi(self.gait_phase + 2.0 * np.pi * 0.02).astype(np.float32)

        return "".join(
            f"({motor} {math.degrees(float(target)):.2f} 0.0 25.00 0.60 0.0)"
            for motor, target in zip(T1_MOTORS, targets, strict=True)
        )

    def _observation(self, sensors: dict[str, Any], velocity: VelocityCommand) -> np.ndarray:
        joints = sensors.get("HJ")
        if not isinstance(joints, list) or len(joints) != ACTION_SIZE:
            raise ValueError(f"expected {ACTION_SIZE} hinge-joint sensors")

        positions = np.deg2rad(np.array([joint["ax"] for joint in joints], dtype=np.float32))
        velocities = np.deg2rad(np.array([joint["vx"] for joint in joints], dtype=np.float32))
        gyroscope = np.deg2rad(np.array(sensors["GYR"]["rt"], dtype=np.float32))
        quaternion = np.array(sensors["quat"]["q"], dtype=np.float32)

        self.remaining_warmup_cycles = max(0, self.remaining_warmup_cycles - 1)
        goal = np.zeros(3, dtype=np.float32) if self.remaining_warmup_cycles else velocity.as_array()
        next_phase = _wrap_to_pi(self.gait_phase + 2.0 * np.pi * 0.02)
        phase_features = np.concatenate([np.sin(next_phase), np.cos(next_phase)]).astype(np.float32)

        observation = np.concatenate(
            [
                (positions - self.nominal_positions) / 3.14,
                velocities / 100.0,
                self.previous_action / 10.0,
                np.clip(gyroscope / 50.0, -1.0, 1.0),
                goal,
                phase_features,
                _project_gravity(quaternion),
            ]
        )
        if observation.size != OBSERVATION_SIZE:
            raise ValueError(f"expected {OBSERVATION_SIZE} policy observations")
        return np.clip(np.nan_to_num(observation), -10.0, 10.0).astype(np.float32)


def parse_sensor_message(message: str) -> dict[str, Any]:
    """Parse RCSSServerMJ's nested sensor groups into a dictionary."""
    result: dict[str, Any] = {}
    for tag, inner in re.findall(r"\((\w+)((?:\s*\([^()]*\))*)\)", message):
        group: dict[str, Any] = {}
        for key, values in re.findall(r"\(\s*(\w+)((?:\s+[^()]+)+)\)", inner):
            parsed = [_parse_token(token) for token in values.strip().split()]
            group[key] = parsed[0] if len(parsed) == 1 else parsed
        if tag in result:
            result[tag] = result[tag] + [group] if isinstance(result[tag], list) else [result[tag], group]
        else:
            result[tag] = group
    return result


def _parse_token(token: str) -> float | str:
    try:
        return float(token)
    except ValueError:
        return token


def _wrap_to_pi(values: np.ndarray) -> np.ndarray:
    return (values + np.pi) % (2.0 * np.pi) - np.pi


def _project_gravity(quaternion: np.ndarray) -> np.ndarray:
    if quaternion.shape != (4,):
        raise ValueError("expected orientation quaternion with four values")
    norm = np.linalg.norm(quaternion)
    if norm == 0:
        raise ValueError("orientation quaternion cannot be zero")
    w, x, y, z = quaternion / norm
    return np.array(
        [2.0 * (y * w - x * z), -2.0 * (y * z + x * w), 2.0 * (x * x + y * y) - 1.0],
        dtype=np.float32,
    )