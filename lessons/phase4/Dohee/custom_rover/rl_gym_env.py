import math
from dataclasses import replace

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from config import DriverInputs, SIM_CONFIG, WAYPOINTS, max_speed
from drivers import clamp, wrap_to_pi
from rover import CustomViperRover
from simulation import build_system


class CustomRoverRLEnv(gym.Env):
    """
    Gymnasium environment wrapper for the custom rover.

    The action is normalized:
        action[0] in [-1, 1] -> speed command in [-max_speed, max_speed]
        action[1] in [-1, 1] -> steering command in [-1, 1]
        action[2] in [-1, 1] -> turn_mode in [0, 1]
    """

    metadata = {"render_modes": []}

    def __init__(
        self,
        terrain_mode="flat",
        max_episode_time=20.0,
        control_dt=0.05,
        goal_tolerance=0.45,
    ):
        super().__init__()
        self.terrain_mode = terrain_mode
        self.max_episode_time = max_episode_time
        self.control_dt = control_dt
        self.goal_tolerance = goal_tolerance

        self.cfg = replace(
            SIM_CONFIG,
            control_mode="rl",
            experiment_name="rl_gym",
            terrain_mode=terrain_mode,
            enable_visualization=False,
            show_plots=False,
            sim_time_end=max_episode_time,
        )

        self.action_space = spaces.Box(
            low=np.array([-1.0, -1.0, -1.0], dtype=np.float32),
            high=np.array([1.0, 1.0, 1.0], dtype=np.float32),
            dtype=np.float32,
        )

        self.observation_space = spaces.Box(
            low=np.array(
                [-30.0, -30.0, -30.0, -30.0, 0.0, -1.0, -1.0, -2.0, -1.0, 0.0],
                dtype=np.float32,
            ),
            high=np.array(
                [30.0, 30.0, 30.0, 30.0, 50.0, 1.0, 1.0, 2.0, 1.0, 1.0],
                dtype=np.float32,
            ),
            dtype=np.float32,
        )

        self.system = None
        self.rover = None
        self.time = 0.0
        self.waypoint_index = 0
        self.previous_distance = 0.0
        self.last_inputs = DriverInputs()

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.system = build_system()
        self.rover = CustomViperRover(
            self.system,
            self.cfg.control_mode,
            self.cfg.experiment_name,
            self.cfg.terrain_mode,
        )
        self.time = 0.0
        self.waypoint_index = 0
        self.last_inputs = DriverInputs()

        obs, info = self._get_observation()
        self.previous_distance = info["distance_to_target"]
        return obs, info

    def step(self, action):
        action = np.asarray(action, dtype=np.float32)
        action = np.clip(action, self.action_space.low, self.action_space.high)

        inputs = DriverInputs(
            speed_cmd=float(action[0]) * max_speed,
            steering_cmd=float(action[1]),
            turn_mode=0.5 * (float(action[2]) + 1.0),
        )
        self.last_inputs = inputs

        steps = max(1, int(round(self.control_dt / self.cfg.time_step)))
        for _ in range(steps):
            self.rover.synchronize(inputs, self.cfg.time_step)
            self.system.DoStepDynamics(self.cfg.time_step)
            self.time += self.cfg.time_step

        obs, info = self._get_observation()
        reward = self._compute_reward(info, action)

        terminated = info["goal_reached"]
        truncated = self.time >= self.max_episode_time
        self.previous_distance = info["distance_to_target"]

        return obs, reward, terminated, truncated, info

    def close(self):
        self.system = None
        self.rover = None

    def _get_observation(self):
        pos = self.rover.chassis.GetPos()
        yaw = self.rover.get_yaw_rad()

        if self.waypoint_index >= len(WAYPOINTS):
            target_x, target_y = WAYPOINTS[-1]
        else:
            target_x, target_y = WAYPOINTS[self.waypoint_index]

        dx = target_x - pos.x
        dy = target_y - pos.y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance < self.goal_tolerance and self.waypoint_index < len(WAYPOINTS) - 1:
            self.waypoint_index += 1
            target_x, target_y = WAYPOINTS[self.waypoint_index]
            dx = target_x - pos.x
            dy = target_y - pos.y
            distance = math.sqrt(dx * dx + dy * dy)

        heading = math.atan2(dy, dx)
        heading_error = wrap_to_pi(heading - yaw)
        local_x = math.cos(yaw) * dx + math.sin(yaw) * dy
        local_y = -math.sin(yaw) * dx + math.cos(yaw) * dy
        waypoint_fraction = self.waypoint_index / max(1, len(WAYPOINTS) - 1)

        self.rover.target_x = target_x
        self.rover.target_y = target_y

        obs = np.array(
            [
                pos.x,
                pos.y,
                local_x,
                local_y,
                distance,
                math.sin(heading_error),
                math.cos(heading_error),
                self.last_inputs.speed_cmd,
                self.last_inputs.steering_cmd,
                waypoint_fraction,
            ],
            dtype=np.float32,
        )

        info = {
            "time": self.time,
            "x": pos.x,
            "y": pos.y,
            "target_x": target_x,
            "target_y": target_y,
            "waypoint_index": self.waypoint_index,
            "distance_to_target": distance,
            "heading_error": heading_error,
            "goal_reached": (
                self.waypoint_index >= len(WAYPOINTS) - 1
                and distance < self.goal_tolerance
            ),
        }
        return obs, info

    def _compute_reward(self, info, action):
        progress = self.previous_distance - info["distance_to_target"]
        heading_penalty = 0.05 * abs(info["heading_error"])
        action_penalty = 0.01 * float(np.linalg.norm(action))
        reward = 5.0 * progress - heading_penalty - action_penalty

        if info["distance_to_target"] < self.goal_tolerance:
            reward += 1.0
        if info["goal_reached"]:
            reward += 10.0

        return float(reward)
