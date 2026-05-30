import csv
from dataclasses import replace

import matplotlib.pyplot as plt
import pychrono as chrono
import pychrono.irrlicht as irr

# config.py에서 시뮬레이션 설정, 결과 저장 경로, waypoint 정보를 불러온다.
from config import CSV_PATH, PLOT_PATH, SIM_CONFIG, WAYPOINTS, get_result_paths

# drivers.py에서 테스트용 controller들을 불러온다.
# EXPERIMENTS: predefined profile dictionary
# ProgrammedDriver: 시간 기반 입력 profile용 driver
# WaypointDriver: waypoint 추종용 driver
from drivers import EXPERIMENTS, ProgrammedDriver, RLDriver, WaypointDriver

# rover.py에서 Custom Viper-style rover 모델 클래스를 불러온다.
from rover import CustomViperRover


# =============================================================================
# 1. Chrono system builder
# =============================================================================

def build_system():
    """
    Chrono 물리 시스템을 생성하고 기본 환경 설정을 적용한다.

    이 함수는 시뮬레이션의 가장 기본이 되는 ChSystemNSC를 만든다.
    모든 body, joint, motor, terrain은 이 system에 추가된다.

    Returns
    -------
    chrono.ChSystemNSC
        NSC contact 기반 Chrono 물리 시스템
    """

    # NSC 방식의 Chrono system 생성
    # NSC는 Non-Smooth Contact 방식으로, rigid body 접촉/마찰 계산에 사용된다.
    system = chrono.ChSystemNSC()

    # 충돌 검출 시스템을 Bullet으로 설정한다.
    # 여러 개의 box, cylinder, terrain feature가 있으므로 충돌 검출 엔진이 필요하다.
    system.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)

    # 중력 설정
    # 이 프로젝트는 Z-up 좌표계를 사용하므로 중력은 -Z 방향이다.
    system.SetGravitationalAcceleration(chrono.ChVector3d(0, 0, -9.81))

    # 충돌 envelope/margin 설정
    # 너무 크면 물체가 실제보다 떨어져 접촉하고,
    # 너무 작으면 충돌 검출이 불안정할 수 있다.
    chrono.ChCollisionModel.SetDefaultSuggestedEnvelope(0.0025)
    chrono.ChCollisionModel.SetDefaultSuggestedMargin(0.0025)

    return system


# =============================================================================
# 2. Driver/controller builder
# =============================================================================

def build_driver(control_mode, experiment_name):
    """
    control mode에 따라 적절한 driver/controller를 생성한다.

    Parameters
    ----------
    control_mode : str
        "waypoints" 또는 "profiles"
    experiment_name : str
        profiles mode에서 사용할 실험 profile 이름

    Returns
    -------
    WaypointDriver or ProgrammedDriver
        로버에 DriverInputs를 제공하는 controller 객체

    Notes
    -----
    이 driver는 로버 설계의 핵심이 아니라,
    로버가 제대로 움직이는지 확인하기 위한 테스트 입력 생성기다.
    """

    # waypoint 추종 모드:
    # config.py에 정의된 WAYPOINTS를 순서대로 따라가는 단순 controller를 사용한다.
    if control_mode == "waypoints":
        return WaypointDriver(WAYPOINTS)

    if control_mode == "rl":
        return RLDriver(waypoints=WAYPOINTS)

    # profiles 모드:
    # straight, slalom, pivot_turn 같은 시간 기반 입력 profile을 사용한다.
    if experiment_name not in EXPERIMENTS:
        raise ValueError(f"Unknown experiment_name: {experiment_name}")

    return ProgrammedDriver(EXPERIMENTS[experiment_name])


# =============================================================================
# 3. Visualization builder
# =============================================================================

def build_visual_system(system):
    """
    Irrlicht 시각화 시스템을 생성하고 Chrono system에 연결한다.

    Parameters
    ----------
    system : chrono.ChSystemNSC
        시각화할 Chrono 물리 시스템

    Returns
    -------
    irr.ChVisualSystemIrrlicht
        Chrono Irrlicht visual system
    """

    # 일반 Irrlicht visual system 생성
    # Vehicle 전용 visual system이 아니라, pychrono.irrlicht의 기본 visual system을 사용한다.
    vis = irr.ChVisualSystemIrrlicht()

    # 물리 system을 visual system에 연결한다.
    vis.AttachSystem(system)

    # 창 크기와 제목 설정
    vis.SetWindowSize(1280, 720)
    vis.SetWindowTitle("Custom Viper Rover With Driver Inputs")

    # Z-up 좌표계 기준으로 카메라 수직 방향 설정
    vis.SetCameraVertical(chrono.CameraVerticalDir_Z)

    # Irrlicht 초기화
    vis.Initialize()

    # 기본 하늘 배경 추가
    vis.AddSkyBox()

    # 초기 카메라 위치와 바라보는 지점 설정
    # 첫 번째 벡터: 카메라 위치
    # 두 번째 벡터: 카메라가 바라보는 target point
    vis.AddCamera(
        chrono.ChVector3d(2.8, -3.4, 1.9),
        chrono.ChVector3d(0.0, 0.0, 0.42),
    )

    # 기본 조명 추가
    vis.AddTypicalLights()

    return vis


# =============================================================================
# 4. CSV logging
# =============================================================================

def save_rows(rows, csv_path=CSV_PATH):
    """
    시뮬레이션 중 기록한 로버 상태를 CSV 파일로 저장한다.

    Parameters
    ----------
    rows : list[dict]
        각 timestep에서 저장한 로버 상태 dictionary 목록

    Output
    ------
    CSV_PATH에 지정된 위치에 csv 파일이 생성된다.
    """

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "time",
                "x",
                "y",
                "z",
                "roll_deg",
                "pitch_deg",
                "yaw_deg",
                "target_x",
                "target_y",
                "speed_cmd",
                "steering_cmd",
                "turn_mode",
                "wheel_omega",
                "steer_left_deg",
                "steer_right_deg",
            ],
        )

        # 첫 줄에 column 이름 저장
        writer.writeheader()

        # 저장된 모든 row를 파일에 기록
        writer.writerows(rows)


# =============================================================================
# 5. Path plot saving
# =============================================================================

def save_path_plot(rows, plot_path=PLOT_PATH, show_plot=True, show_waypoints=True):
    """
    로버의 실제 주행 경로와 waypoint를 비교하는 plot을 저장한다.

    Parameters
    ----------
    rows : list[dict]
        시뮬레이션 로그 데이터

    Output
    ------
    PLOT_PATH에 지정된 위치에 png 파일이 생성된다.
    """

    # 로그가 없으면 plot을 만들 수 없으므로 바로 종료한다.
    if not rows:
        return

    # 로버 실제 경로
    xs = [row["x"] for row in rows]
    ys = [row["y"] for row in rows]

    # 기준 waypoint 경로
    wx = [p[0] for p in WAYPOINTS] if show_waypoints else []
    wy = [p[1] for p in WAYPOINTS] if show_waypoints else []

    # 새 figure 생성
    plt.figure(figsize=(8, 7))

    # 로버 실제 이동 경로
    plt.plot(xs, ys, linewidth=2.0, color="#1f5fbf", label="rover path")

    # 시작 waypoint
    if show_waypoints:
        plt.scatter(wx[0], wy[0], s=90, color="#36a852", label="start waypoint")

    # 중간 waypoint
    if show_waypoints and len(WAYPOINTS) > 2:
        plt.scatter(wx[1:-1], wy[1:-1], s=55, color="#e3b505", label="mid waypoints")

    # 최종 목표 waypoint
    if show_waypoints:
        plt.scatter(wx[-1], wy[-1], s=90, color="#d93025", label="goal waypoint")

    # 실제 시작 위치
    plt.scatter(xs[0], ys[0], s=70, color="#111111", marker="x", label="start pose")

    # 실제 종료 위치
    plt.scatter(xs[-1], ys[-1], s=70, color="#6a1b9a", marker="x", label="end pose")

    # 축 이름과 제목
    plt.xlabel("x position [m]")
    plt.ylabel("y position [m]")
    if show_waypoints:
        plt.title("Custom Viper Rover Path vs Waypoints")
    else:
        plt.title("Custom Viper Rover Path")

    # x, y 축 비율을 동일하게 맞춰 실제 경로 왜곡을 줄인다.
    plt.axis("equal")

    # 격자와 범례
    plt.grid(True, alpha=0.3)
    plt.legend()

    # 여백 자동 조정 후 저장
    plt.tight_layout()
    plt.savefig(plot_path, dpi=180)
    if show_plot:
        plt.show()
    plt.close()


def save_attitude_plot(rows, plot_path, show_plot=True):
    if not rows:
        return None

    attitude_path = plot_path.with_name(plot_path.stem.replace("_path", "_attitude") + plot_path.suffix)
    times = [row["time"] for row in rows]
    rolls = [row["roll_deg"] for row in rows]
    pitches = [row["pitch_deg"] for row in rows]
    yaws = [row["yaw_deg"] for row in rows]
    zs = [row["z"] for row in rows]

    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

    axes[0].plot(times, rolls, color="#c44e52", label="roll")
    axes[0].plot(times, pitches, color="#4c72b0", label="pitch")
    axes[0].set_ylabel("angle [deg]")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()

    axes[1].plot(times, yaws, color="#55a868", label="yaw")
    axes[1].set_ylabel("yaw [deg]")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()

    axes[2].plot(times, zs, color="#8172b2", label="z")
    axes[2].set_xlabel("time [s]")
    axes[2].set_ylabel("z [m]")
    axes[2].grid(True, alpha=0.3)
    axes[2].legend()

    fig.suptitle("Custom Viper Rover Attitude Response")
    fig.tight_layout()
    fig.savefig(attitude_path, dpi=180)
    if show_plot:
        plt.show()
    plt.close(fig)
    return attitude_path


# =============================================================================
# 6. Main simulation loop
# =============================================================================

def run_simulation():
    """
    전체 시뮬레이션을 실행하는 main 함수.

    실행 순서:
        1. control_mode 유효성 검사
        2. Chrono system 생성
        3. CustomViperRover 생성
        4. driver/controller 생성
        5. Irrlicht visual system 생성
        6. simulation loop 실행
        7. CSV 저장
        8. path plot 저장
    """

    # 현재 지원하는 control mode인지 확인한다.
    if SIM_CONFIG.control_mode not in {"waypoints", "profiles", "rl"}:
        raise ValueError(f"Unknown control_mode: {SIM_CONFIG.control_mode}")

    # Chrono 물리 시스템 생성
    system = build_system()

    # 커스텀 로버 생성
    # 이 단계에서 지형, 차체, 바퀴, 조향 모터, 구동 모터가 system에 추가된다.
    rover = CustomViperRover(system, SIM_CONFIG.control_mode, SIM_CONFIG.experiment_name)

    # control mode에 맞는 driver/controller 생성
    driver = build_driver(SIM_CONFIG.control_mode, SIM_CONFIG.experiment_name)

    # Irrlicht 시각화 창 생성
    vis = build_visual_system(system)

    # 터미널에 로버 설계 요약 출력
    rover.print_design_summary()

    # 로그 저장용 리스트
    rows = []

    # 시뮬레이션 시간 변수
    time = 0.0

    # 다음 렌더링 시점
    next_render_time = 0.0

    # 다음 로그 저장 시점
    next_log_time = 0.0

    # -------------------------------------------------------------------------
    # Simulation loop
    # -------------------------------------------------------------------------
    # vis.Run()이 True이고 설정된 종료 시간에 도달하지 않았을 때 반복한다.
    # 사용자가 창을 닫으면 vis.Run()이 False가 되어 종료된다.
    while vis.Run() and time < SIM_CONFIG.sim_time_end:

        # ---------------------------------------------------------------------
        # 1) Controller update
        # ---------------------------------------------------------------------
        if SIM_CONFIG.control_mode in {"waypoints", "rl"}:
            # waypoint driver는 현재 rover 상태를 보고 다음 입력을 계산한다.
            inputs = driver.update(rover)

            # 현재 목표 waypoint를 rover에 저장한다.
            # get_state()에서 target_x, target_y로 기록된다.
            rover.target_x = driver.target_x
            rover.target_y = driver.target_y

        else:
            # profile driver는 현재 시간만 보고 입력을 생성한다.
            inputs = driver.update(time)

            # profile mode에서는 목표 waypoint가 없으므로 0으로 둔다.
            rover.target_x = 0.0
            rover.target_y = 0.0

        # ---------------------------------------------------------------------
        # 2) Apply inputs to rover motors
        # ---------------------------------------------------------------------
        # DriverInputs를 실제 조향 모터 각도와 바퀴 회전속도로 변환한다.
        rover.synchronize(inputs, SIM_CONFIG.time_step)

        # ---------------------------------------------------------------------
        # 3) Rendering
        # ---------------------------------------------------------------------
        # 물리 계산 timestep은 매우 작지만, 화면은 render_step 간격으로만 갱신한다.
        # 이렇게 하면 계산 안정성과 렌더링 효율을 동시에 확보할 수 있다.
        if time >= next_render_time:
            vis.BeginScene()
            vis.Render()
            vis.EndScene()
            next_render_time += SIM_CONFIG.render_step

        # ---------------------------------------------------------------------
        # 4) Dynamics integration
        # ---------------------------------------------------------------------
        # Chrono system을 한 timestep 전진시킨다.
        system.DoStepDynamics(SIM_CONFIG.time_step)

        # 사용자가 관리하는 time 변수도 같은 timestep만큼 증가시킨다.
        time += SIM_CONFIG.time_step

        # ---------------------------------------------------------------------
        # 5) Logging
        # ---------------------------------------------------------------------
        # log_dt 간격마다 로버 상태를 저장한다.
        if time >= next_log_time:
            state = rover.get_state(time)

            rows.append(
                {
                    "time": state.time,
                    "x": state.x,
                    "y": state.y,
                    "z": state.z,
                    "roll_deg": state.roll_deg,
                    "pitch_deg": state.pitch_deg,
                    "yaw_deg": state.yaw_deg,
                    "target_x": state.target_x,
                    "target_y": state.target_y,
                    "speed_cmd": state.speed_cmd,
                    "steering_cmd": state.steering_cmd,
                    "turn_mode": state.turn_mode,
                    "wheel_omega": state.wheel_omega,
                    "steer_left_deg": state.steer_left_deg,
                    "steer_right_deg": state.steer_right_deg,
                }
            )

            # 다음 로그 저장 시간 갱신
            next_log_time += SIM_CONFIG.log_dt

    # -------------------------------------------------------------------------
    # Save results
    # -------------------------------------------------------------------------

    # CSV 로그 저장
    save_rows(rows)
    print(f"[Done] Saved log to {CSV_PATH}")

    # 경로 plot 저장
    save_path_plot(rows)
    if rows:
        print(f"[Done] Saved plot to {PLOT_PATH}")
    attitude_path = save_attitude_plot(rows, PLOT_PATH, SIM_CONFIG.show_plots)
    if attitude_path:
        print(f"[Done] Saved attitude plot to {attitude_path}")


def run_simulation_case(
    config=None,
    experiment_name=None,
    control_mode=None,
    terrain_mode=None,
    enable_visualization=None,
    show_plots=None,
    results_dir=None,
):
    """Run one configured simulation case and return logged rows and output paths."""
    cfg = replace(SIM_CONFIG) if config is None else replace(config)
    if experiment_name is not None:
        cfg.experiment_name = experiment_name
    if control_mode is not None:
        cfg.control_mode = control_mode
    if terrain_mode is not None:
        cfg.terrain_mode = terrain_mode
    if enable_visualization is not None:
        cfg.enable_visualization = enable_visualization
    if show_plots is not None:
        cfg.show_plots = show_plots

    if cfg.control_mode not in {"waypoints", "profiles", "rl"}:
        raise ValueError(f"Unknown control_mode: {cfg.control_mode}")
    if cfg.terrain_mode not in {"obstacles", "flat"}:
        raise ValueError(f"Unknown terrain_mode: {cfg.terrain_mode}")

    csv_path, plot_path = get_result_paths(cfg, results_dir)

    system = build_system()
    rover = CustomViperRover(system, cfg.control_mode, cfg.experiment_name, cfg.terrain_mode)
    driver = build_driver(cfg.control_mode, cfg.experiment_name)
    vis = build_visual_system(system) if cfg.enable_visualization else None

    rover.print_design_summary()

    rows = []
    time = 0.0
    next_render_time = 0.0
    next_log_time = 0.0

    while time < cfg.sim_time_end and (vis is None or vis.Run()):
        if cfg.control_mode in {"waypoints", "rl"}:
            inputs = driver.update(rover)
            rover.target_x = driver.target_x
            rover.target_y = driver.target_y
        else:
            inputs = driver.update(time)
            rover.target_x = 0.0
            rover.target_y = 0.0

        rover.synchronize(inputs, cfg.time_step)

        if vis is not None and time >= next_render_time:
            vis.BeginScene()
            vis.Render()
            vis.EndScene()
            next_render_time += cfg.render_step

        system.DoStepDynamics(cfg.time_step)
        time += cfg.time_step

        if time >= next_log_time:
            state = rover.get_state(time)
            rows.append(
                {
                    "time": state.time,
                    "x": state.x,
                    "y": state.y,
                    "z": state.z,
                    "roll_deg": state.roll_deg,
                    "pitch_deg": state.pitch_deg,
                    "yaw_deg": state.yaw_deg,
                    "target_x": state.target_x,
                    "target_y": state.target_y,
                    "speed_cmd": state.speed_cmd,
                    "steering_cmd": state.steering_cmd,
                    "turn_mode": state.turn_mode,
                    "wheel_omega": state.wheel_omega,
                    "steer_left_deg": state.steer_left_deg,
                    "steer_right_deg": state.steer_right_deg,
                }
            )
            next_log_time += cfg.log_dt

    save_rows(rows, csv_path)
    print(f"[Done] Saved log to {csv_path}")

    save_path_plot(rows, plot_path, cfg.show_plots, cfg.control_mode in {"waypoints", "rl"})
    if rows:
        print(f"[Done] Saved plot to {plot_path}")
    attitude_path = save_attitude_plot(rows, plot_path, cfg.show_plots)
    if attitude_path:
        print(f"[Done] Saved attitude plot to {attitude_path}")

    return rows, csv_path, plot_path
