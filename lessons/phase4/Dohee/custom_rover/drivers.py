import math

from config import DriverInputs, WAYPOINTS, max_speed


def clamp(value, low, high):
    return max(low, min(high, value))


def wrap_to_pi(angle):
    while angle > math.pi:
        angle -= 2.0 * math.pi
    while angle < -math.pi:
        angle += 2.0 * math.pi
    return angle


def straight_profile(t):
    if t < 1.0:
        return DriverInputs(0.0, 0.0)
    return DriverInputs(0.9, 0.0)


def step_turn_profile(t):
    if t < 1.0:
        return DriverInputs(0.0, 0.0, 0.0)
    if t < 4.0:
        return DriverInputs(0.9, 0.0, 0.0)
    if t < 9.0:
        return DriverInputs(0.9, 0.65, 0.0)
    if t < 13.0:
        return DriverInputs(0.9, -0.30, 0.0)
    return DriverInputs(0.7, 0.0, 0.0)


def slalom_profile(t):
    if t < 1.0:
        return DriverInputs(0.0, 0.0, 0.0)
    return DriverInputs(1.0, 0.55 * math.sin(1.15 * (t - 1.0)), 0.0)


def spin_test_profile(t):
    if t < 1.0:
        return DriverInputs(0.0, 0.0, 0.0)
    if t < 3.0:
        return DriverInputs(0.6, 0.0, 0.0)
    return DriverInputs(0.45, 0.95, 0.0)


def pivot_turn_profile(t):
    if t < 1.0:
        return DriverInputs(0.0, 0.0, 0.0)
    if t < 2.5:
        return DriverInputs(0.35, 0.0, 0.0)
    if t < 7.0:
        return DriverInputs(0.4, 0.95, 1.0)
    return DriverInputs(0.4, 0.0, 0.0)


EXPERIMENTS = {
    "straight": straight_profile,
    "step_turn": step_turn_profile,
    "slalom": slalom_profile,
    "spin_test": spin_test_profile,
    "pivot_turn": pivot_turn_profile,
}


class ProgrammedDriver:
    def __init__(self, profile_func):
        self.profile_func = profile_func
        self.inputs = DriverInputs()

    def update(self, time):
        self.inputs = self.profile_func(time)
        self.inputs.speed_cmd = clamp(self.inputs.speed_cmd, -max_speed, max_speed)
        self.inputs.steering_cmd = clamp(self.inputs.steering_cmd, -1.0, 1.0)
        self.inputs.turn_mode = clamp(self.inputs.turn_mode, 0.0, 1.0)
        return self.inputs


class WaypointDriver:
    def __init__(self, waypoints=None):
        self.waypoints = WAYPOINTS if waypoints is None else waypoints
        self.index = 0
        self.inputs = DriverInputs()
        self.target_x = self.waypoints[0][0]
        self.target_y = self.waypoints[0][1]

    def update(self, rover):
        pos = rover.chassis.GetPos()
        yaw = rover.get_yaw_rad()

        if self.index >= len(self.waypoints):
            self.inputs = DriverInputs(0.0, 0.0, 0.0)
            return self.inputs

        tx, ty = self.waypoints[self.index]
        dx = tx - pos.x
        dy = ty - pos.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 0.45 and self.index < len(self.waypoints) - 1:
            self.index += 1
            tx, ty = self.waypoints[self.index]
            dx = tx - pos.x
            dy = ty - pos.y

        self.target_x = tx
        self.target_y = ty

        heading = math.atan2(dy, dx)
        heading_error = wrap_to_pi(heading - yaw)
        local_x = math.cos(yaw) * dx + math.sin(yaw) * dy

        steering_cmd = clamp(1.45 * heading_error, -1.0, 1.0)
        speed_cmd = 0.9

        if local_x < 0.0:
            speed_cmd = -0.35
            steering_cmd = clamp(-1.10 * heading_error, -1.0, 1.0)
            if abs(heading_error) > math.radians(55.0):
                speed_cmd = -0.20
        else:
            if abs(heading_error) > math.radians(30.0):
                speed_cmd = 0.45
            if abs(heading_error) > math.radians(55.0):
                speed_cmd = 0.25
            if abs(heading_error) > math.radians(80.0):
                speed_cmd = 0.15

        turn_mode = 0.0
        if abs(heading_error) > math.radians(40.0):
            turn_mode = 0.6
        if abs(heading_error) > math.radians(70.0):
            turn_mode = 1.0

        self.inputs = DriverInputs(speed_cmd, steering_cmd, turn_mode)
        return self.inputs


class RLDriver:
    """
    Minimal RL-style driver interface.

    A real trained policy can replace dummy_policy as long as it returns:
        (speed_cmd, steering_cmd, turn_mode)
    """

    def __init__(self, policy=None, waypoints=None):
        self.policy = policy
        self.waypoints = WAYPOINTS if waypoints is None else waypoints
        self.index = 0
        self.inputs = DriverInputs()
        self.observation = {}
        self.target_x = self.waypoints[0][0]
        self.target_y = self.waypoints[0][1]

    def make_observation(self, rover):
        pos = rover.chassis.GetPos()
        yaw = rover.get_yaw_rad()

        if self.index >= len(self.waypoints):
            tx, ty = self.waypoints[-1]
        else:
            tx, ty = self.waypoints[self.index]

        dx = tx - pos.x
        dy = ty - pos.y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance < 0.45 and self.index < len(self.waypoints) - 1:
            self.index += 1
            tx, ty = self.waypoints[self.index]
            dx = tx - pos.x
            dy = ty - pos.y
            distance = math.sqrt(dx * dx + dy * dy)

        heading = math.atan2(dy, dx)
        heading_error = wrap_to_pi(heading - yaw)
        local_x = math.cos(yaw) * dx + math.sin(yaw) * dy
        local_y = -math.sin(yaw) * dx + math.cos(yaw) * dy

        self.target_x = tx
        self.target_y = ty
        self.observation = {
            "x": pos.x,
            "y": pos.y,
            "yaw_rad": yaw,
            "target_x": tx,
            "target_y": ty,
            "dx": dx,
            "dy": dy,
            "local_x": local_x,
            "local_y": local_y,
            "distance_to_target": distance,
            "heading_error": heading_error,
            "previous_speed_cmd": self.inputs.speed_cmd,
            "previous_steering_cmd": self.inputs.steering_cmd,
            "previous_turn_mode": self.inputs.turn_mode,
        }
        return self.observation

    def dummy_policy(self, obs):
        heading_error = obs["heading_error"]
        distance = obs["distance_to_target"]
        local_x = obs["local_x"]

        speed_cmd = 0.8
        if distance < 0.8:
            speed_cmd = 0.45
        if abs(heading_error) > math.radians(35.0):
            speed_cmd = 0.35
        if abs(heading_error) > math.radians(70.0):
            speed_cmd = 0.20
        if local_x < 0.0:
            speed_cmd = -0.25

        steering_cmd = clamp(1.35 * heading_error, -1.0, 1.0)
        if local_x < 0.0:
            steering_cmd = clamp(-1.0 * heading_error, -1.0, 1.0)

        turn_mode = 0.0
        if abs(heading_error) > math.radians(45.0):
            turn_mode = 0.6
        if abs(heading_error) > math.radians(75.0):
            turn_mode = 1.0

        return speed_cmd, steering_cmd, turn_mode

    def update(self, rover):
        obs = self.make_observation(rover)
        action = self.dummy_policy(obs) if self.policy is None else self.policy(obs)

        self.inputs = DriverInputs(
            clamp(float(action[0]), -max_speed, max_speed),
            clamp(float(action[1]), -1.0, 1.0),
            clamp(float(action[2]), 0.0, 1.0),
        )
        return self.inputs
