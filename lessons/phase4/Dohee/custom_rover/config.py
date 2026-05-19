import math
from dataclasses import dataclass
from pathlib import Path


# =============================================================================
# 1. Simulation configuration
# =============================================================================
# 시뮬레이션 전체 실행 조건을 모아둔 설정 클래스.
# 나중에 실험 조건을 바꾸고 싶을 때 이 클래스만 수정하면 되도록 구성한다.
@dataclass
class SimulationConfig:
    # Chrono 동역학 적분 시간 간격 [s]
    # 값이 작을수록 안정적이지만 계산 시간이 길어진다.
    time_step: float = 5e-4

    # 전체 시뮬레이션 종료 시간 [s]
    sim_time_end: float = 45.0

    # 화면 렌더링 간격 [s]
    # 1/60이면 약 60 FPS 기준으로 화면을 갱신한다.
    render_step: float = 1.0 / 60.0

    # 로그 저장 간격 [s]
    # 0.05초마다 로버 상태를 CSV에 기록한다.
    log_dt: float = 0.05

    # 실험 이름.
    # 결과 파일 이름에 사용된다.
    experiment_name: str = "slalom"

    # 제어 방식.
    # 현재 코드는 waypoint 추종 모드를 기본으로 사용한다.
    control_mode: str = "waypoints"


# =============================================================================
# 2. Driver input data
# =============================================================================
# 로버에 전달되는 제어 입력값.
# 여기서 driver는 실제 운전자가 아니라, 로버 테스트를 위한 입력 생성기를 의미한다.
@dataclass
class DriverInputs:
    # 목표 주행 속도 명령 [m/s]
    speed_cmd: float = 0.0

    # 조향 명령 [-1, 1]
    # + 방향은 코드에서 왼쪽 회전 명령으로 해석한다.
    steering_cmd: float = 0.0

    # 회전 모드 blending 값 [0, 1]
    # 0: 일반 주행, 1: 좌우 바퀴 속도 차이를 크게 주는 pivot-turn 성향
    turn_mode: float = 0.0


# =============================================================================
# 3. Rover state data for logging
# =============================================================================
# 시뮬레이션 중 저장할 로버 상태값.
# CSV 로그와 경로 그래프 생성에 사용된다.
@dataclass
class RoverState:
    # 현재 시뮬레이션 시간 [s]
    time: float

    # 로버 차체 중심 위치 [m]
    x: float
    y: float
    z: float

    # 로버 yaw angle [deg]
    # Z-up 좌표계에서 수평면 방향각을 의미한다.
    yaw_deg: float

    # 현재 추종 중인 waypoint 위치 [m]
    target_x: float
    target_y: float

    # 현재 로버에 입력된 제어 명령
    speed_cmd: float
    steering_cmd: float
    turn_mode: float

    # 바퀴 목표 각속도 [rad/s]
    wheel_omega: float

    # 좌우 앞바퀴 조향각 [deg]
    steer_left_deg: float
    steer_right_deg: float


# 전역 시뮬레이션 설정 객체
SIM_CONFIG = SimulationConfig()


# =============================================================================
# 4. Contact and terrain parameters
# =============================================================================
# 지면 마찰계수.
# 값이 클수록 바퀴가 덜 미끄러진다.
ground_friction = 0.9

# 바퀴 접촉 마찰계수.
# 로버 휠과 지형 사이의 접지력을 결정한다.
wheel_friction = 1.0

# 반발계수.
# 0이면 충돌 후 튀어오르는 효과를 거의 주지 않는다.
restitution = 0.0


# =============================================================================
# 5. Ground and obstacle geometry
# =============================================================================
# 기본 지면 크기 [m]
ground_length = 30.0
ground_width = 30.0
ground_thickness = 1.0

# 경사로 설정
slope_angle = math.radians(6.0)  # 경사각 [rad]
slope_length = 3.2
slope_width = 2.4
slope_thickness = 0.18

# 첫 번째 턱 장애물 설정 [m]
step_length = 0.7
step_width = 1.8
step_height = 0.035

# 두 번째 턱 장애물 설정 [m]
step2_length = 0.9
step2_width = 1.6
step2_height = 0.045

# 작은 돌/블록 장애물의 기준 크기 [m]
rock_size = 0.10


# =============================================================================
# 6. Chassis parameters
# =============================================================================
# 로버 메인 차체 크기 [m]
chassis_length = 1.18
chassis_width = 0.74
chassis_height = 0.14

# 차체 밀도 [kg/m^3]
# Chrono의 ChBodyEasyBox에서 질량과 관성 계산에 사용된다.
chassis_density = 460.0

# 차체 초기 중심 높이 [m]
chassis_z = 0.54


# =============================================================================
# 7. Wheel parameters
# =============================================================================
# 바퀴 형상 및 물성
wheel_radius = 0.24
wheel_width = 0.11
wheel_density = 720.0

# 바퀴 중심 높이 [m]
# 기본적으로 지면이 z=0일 때 바퀴가 지면에 닿도록 wheel_radius와 같게 둔다.
wheel_z = wheel_radius


# =============================================================================
# 8. Front steering knuckle parameters
# =============================================================================
# 앞바퀴 조향을 위한 knuckle body 크기와 밀도.
# knuckle은 chassis와 front wheel 사이에 위치하며 조향 회전축 역할을 한다.
knuckle_size = 0.10
knuckle_density = 550.0


# =============================================================================
# 9. Visual body styling parameters
# =============================================================================
# 아래 부품들은 로버를 더 실제 탐사 로버처럼 보이게 하기 위한 시각적 요소다.
# 일부는 collision을 끄고 chassis에 고정해서 사용한다.

# 상단 science deck
deck_length = 0.78
deck_width = 0.58
deck_height = 0.05
deck_z_offset = 0.12

# 센서 mast
mast_radius = 0.035
mast_height = 0.32
mast_density = 120.0
mast_x_offset = 0.18
mast_z_offset = 0.26

# 센서 head
sensor_head_x = 0.25
sensor_head_y = 0.20
sensor_head_z = 0.08
sensor_head_density = 80.0


# =============================================================================
# 10. Wheel visual detail parameters
# =============================================================================
# 허브와 grouser는 바퀴를 더 로버처럼 보이게 하는 시각적 요소다.
# grouser collision을 끄면 실제 접촉은 원통형 wheel body가 담당한다.

# 휠 허브
hub_radius = 0.085
hub_width = 0.13
hub_density = 60.0

# 휠 외곽 돌기, grouser
grouser_length = 0.045
grouser_height = 0.022
grouser_width = 0.11
grouser_density = 20.0
grouser_count = 8


# =============================================================================
# 11. Rover layout parameters
# =============================================================================
# wheelbase: 앞바퀴와 뒷바퀴 사이 거리 [m]
# track_width: 좌우 바퀴 사이 거리 [m]
wheelbase = 1.16
track_width = 1.04

# 앞/뒤 바퀴의 x 위치
front_x = wheelbase / 2.0
rear_x = -wheelbase / 2.0

# 좌/우 바퀴의 y 위치
# 좌표계 정의: +Y가 left이므로 left_y는 양수, right_y는 음수이다.
left_y = track_width / 2.0
right_y = -track_width / 2.0


# =============================================================================
# 12. Actuator and control limits
# =============================================================================
# 최대 목표 속도 [m/s]
max_speed = 1.4

# 최대 조향각 [rad]
max_steer_angle = math.radians(28.0)

# 조향각 변화율 제한 [rad/s]
# 실제 actuator처럼 조향이 순간적으로 바뀌지 않도록 제한한다.
max_steer_rate = math.radians(60.0)

# 속도 명령 변화율 제한 [m/s^2]
# 급격한 가감속을 막고 시뮬레이션 안정성을 높인다.
max_speed_rate = 1.2


# =============================================================================
# 13. Waypoint path
# =============================================================================
# 로버가 순서대로 추종할 목표점 목록.
# 좌표계: (x, y), 단위 [m]
# +X 방향으로 전진하면서 좌우로 움직이는 slalom 형태의 경로이다.
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


# =============================================================================
# 14. Output paths
# =============================================================================
# 현재 Python 파일이 위치한 폴더를 기준으로 결과 폴더를 생성한다.
PACKAGE_DIR = Path(__file__).resolve().parent

# 시뮬레이션 결과 저장 폴더
RESULTS_DIR = PACKAGE_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# CSV 로그 파일 경로
CSV_PATH = RESULTS_DIR / f"custom_viper_{SIM_CONFIG.experiment_name}.csv"

# 주행 경로 그래프 이미지 저장 경로
PLOT_PATH = RESULTS_DIR / f"custom_viper_{SIM_CONFIG.experiment_name}_path.png"
