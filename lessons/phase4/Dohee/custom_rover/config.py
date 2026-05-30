import math
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SimulationConfig:
    time_step: float = 5e-4
    sim_time_end: float = 45.0
    render_step: float = 1.0 / 60.0
    log_dt: float = 0.05
#    experiment_name: str = "slalom"
#    control_mode: str = "waypoints"
    experiment_name: str = "straight" # straight, step_turn, slalom, spin_test, pivot_turn, rl_dummy
    control_mode: str = "profiles"  # profiles, waypoints, rl
    terrain_mode: str = "obstacles"  # obstacles, flat
    enable_visualization: bool = True
    show_plots: bool = True


@dataclass
class DriverInputs:
    speed_cmd: float = 0.0
    steering_cmd: float = 0.0
    turn_mode: float = 0.0


@dataclass
class RoverState:
    time: float
    x: float
    y: float
    z: float
    roll_deg: float
    pitch_deg: float
    yaw_deg: float
    target_x: float
    target_y: float
    speed_cmd: float
    steering_cmd: float
    turn_mode: float
    wheel_omega: float
    steer_left_deg: float
    steer_right_deg: float


SIM_CONFIG = SimulationConfig()

ground_friction = 0.9
wheel_friction = 1.0
restitution = 0.0

ground_length = 30.0
ground_width = 30.0
ground_thickness = 1.0
slope_angle = math.radians(6.0)
slope_length = 3.2
slope_width = 2.4
slope_thickness = 0.18
step_length = 0.7
step_width = 1.8
step_height = 0.035
step2_length = 0.9
step2_width = 1.6
step2_height = 0.045
rock_size = 0.10

chassis_length = 1.18
chassis_width = 0.74
chassis_height = 0.14
chassis_density = 460.0
chassis_z = 0.54

wheel_radius = 0.24
wheel_width = 0.11
wheel_density = 720.0
wheel_z = wheel_radius

knuckle_size = 0.10
knuckle_density = 550.0

deck_length = 0.78
deck_width = 0.58
deck_height = 0.05
deck_z_offset = 0.12

mast_radius = 0.035
mast_height = 0.32
mast_density = 120.0
mast_x_offset = 0.18
mast_z_offset = 0.26

sensor_head_x = 0.25
sensor_head_y = 0.20
sensor_head_z = 0.08
sensor_head_density = 80.0

hub_radius = 0.085
hub_width = 0.13
hub_density = 60.0
grouser_length = 0.045
grouser_height = 0.022
grouser_width = 0.11
grouser_density = 20.0
grouser_count = 8

wheelbase = 1.16
track_width = 1.04
front_x = wheelbase / 2.0
rear_x = -wheelbase / 2.0
left_y = track_width / 2.0
right_y = -track_width / 2.0

max_speed = 1.4
max_steer_angle = math.radians(28.0)
max_steer_rate = math.radians(60.0)
max_speed_rate = 1.2

WAYPOINTS = [
    (0.0, 0.0),
    (1.4, 0.0),
    (2.8, 0.55),
    (4.1, 0.15),
    (5.3, -0.55),
    (6.6, -0.10),
    (7.9, 0.60),
    (9.2, 0.10),
    (10.5, -0.50),
    (11.8, 0.0),
]

PACKAGE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = PACKAGE_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
CSV_PATH = RESULTS_DIR / f"custom_viper_{SIM_CONFIG.experiment_name}.csv"
PLOT_PATH = RESULTS_DIR / f"custom_viper_{SIM_CONFIG.experiment_name}_path.png"


def get_result_paths(config=None, results_dir=None):
    cfg = SIM_CONFIG if config is None else config
    output_dir = RESULTS_DIR if results_dir is None else Path(results_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"custom_viper_{cfg.terrain_mode}_{cfg.experiment_name}"
    return output_dir / f"{stem}.csv", output_dir / f"{stem}_path.png"
