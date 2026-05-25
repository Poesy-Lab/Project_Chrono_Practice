"""
============================================================
Lesson 19: Hojin Rover MVP0 - 충돌 가능한 최소 로버
============================================================
학습 목표:
  1. "내 로버"의 가장 작은 버전(MVP0)을 하나의 강체로 만든다.
  2. 초기 속도(SetPosDt)를 주어 장애물과 충돌시킨다.
  3. 위치, 속도, 목표물 접촉 여부를 CSV로 기록한다.

MVP0의 의미:
  - 아직 바퀴 구동, 서스펜션, 센서는 없다.
  - 대신 Phase 5에서 여러 로버를 한 환경에 불러오기 위한 최소 단위
    (이름, 크기, 질량, 충돌 형상, 로그 포맷)를 먼저 정한다.

실행 방법:
  conda activate chrono
  source setup_chrono_env.sh
  python lessons/phase4/hojin/lesson_19_hojin_rover_mvp0_collision_dummy.py

창 없이 빠르게 실행:
  python lessons/phase4/hojin/lesson_19_hojin_rover_mvp0_collision_dummy.py --no-vis
============================================================
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

try:
    import pychrono as chrono
except ImportError as exc:
    raise SystemExit(
        "pychrono를 불러오지 못했습니다.\n"
        "conda activate chrono 후 source setup_chrono_env.sh 를 먼저 실행하세요."
    ) from exc


ROVER_NAME = "hojin_rover_mvp0"
CHASSIS_SIZE = chrono.ChVector3d(1.20, 0.70, 0.35)  # x 길이, y 폭, z 높이
ROVER_START = chrono.ChVector3d(-4.0, 0.0, CHASSIS_SIZE.z / 2)
TARGET_POS = chrono.ChVector3d(1.8, 0.0, 0.40)
TARGET_SIZE = chrono.ChVector3d(0.35, 2.20, 0.80)
DEFAULT_OUTPUT = Path(__file__).resolve().parent / \
    "results" / "mvp0" / "hojin_rover_mvp0_log.csv"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
CHRONO_DATA_DIR = PROJECT_ROOT / "chrono" / "data"

if CHRONO_DATA_DIR.exists() and hasattr(chrono, "SetChronoDataPath"):
    chrono.SetChronoDataPath(str(CHRONO_DATA_DIR) + "/")


def vec_xyz(vec: chrono.ChVector3d) -> tuple[float, float, float]:
    """PyChrono 버전에 따라 x가 속성/메서드일 수 있어 안전하게 꺼낸다."""
    values = []
    for attr in ("x", "y", "z"):
        value = getattr(vec, attr)
        values.append(float(value() if callable(value) else value))
    return tuple(values)


def vec_length(vec: chrono.ChVector3d) -> float:
    x, y, z = vec_xyz(vec)
    return math.sqrt(x * x + y * y + z * z)


def make_material(friction: float, restitution: float) -> chrono.ChContactMaterialNSC:
    material = chrono.ChContactMaterialNSC()
    material.SetFriction(friction)
    material.SetRestitution(restitution)
    return material


def set_body_color(body: chrono.ChBody, color: tuple[float, float, float]) -> None:
    try:
        shape = body.GetVisualShape(0)
    except Exception:
        shape = None
    if shape:
        shape.SetColor(chrono.ChColor(*color))


def add_rover_visual_hints(rover: chrono.ChBody) -> None:
    """MVP0는 단일 충돌 박스지만, 눈으로는 로버처럼 보이도록 바퀴 힌트를 붙인다."""
    wheel_offsets = [
        (-0.38, -0.42, -0.03),
        (-0.38, 0.42, -0.03),
        (0.38, -0.42, -0.03),
        (0.38, 0.42, -0.03),
    ]
    for x, y, z in wheel_offsets:
        wheel = chrono.ChVisualShapeCylinder(0.16, 0.12)
        wheel.SetColor(chrono.ChColor(0.04, 0.05, 0.05))
        rover.AddVisualShape(
            wheel,
            chrono.ChFramed(
                chrono.ChVector3d(x, y, z),
                chrono.QuatFromAngleX(chrono.CH_PI_2),
            ),
        )

    nose = chrono.ChVisualShapeBox(0.12, 0.42, 0.08)
    nose.SetColor(chrono.ChColor(0.95, 0.68, 0.18))
    rover.AddVisualShape(
        nose,
        chrono.ChFramed(chrono.ChVector3d(
            CHASSIS_SIZE.x / 2 + 0.04, 0.0, 0.08)),
    )


class PairContactReporter(chrono.ReportContactCallback):
    """두 물체 사이의 접촉 개수와 접촉력 크기 합을 기록한다."""

    def __init__(self, body_a: chrono.ChBody, body_b: chrono.ChBody):
        self.body_a = body_a
        self.body_b = body_b
        self.count = 0
        self.force_sum = 0.0
        super().__init__()

    def reset(self) -> None:
        self.count = 0
        self.force_sum = 0.0

    def OnReportContact(
        self,
        pA,
        pB,
        plane_coord,
        distance,
        eff_radius,
        cforce,
        ctorque,
        modA,
        modB,
        cnstr_offset,
    ) -> bool:
        body_a = chrono.CastToChBody(modA)
        body_b = chrono.CastToChBody(modB)
        is_pair = (body_a == self.body_a and body_b == self.body_b) or (
            body_a == self.body_b and body_b == self.body_a
        )
        if not is_pair:
            return True

        self.count += 1
        try:
            self.force_sum += vec_length(cforce)
        except Exception:
            self.force_sum += abs(float(cforce))
        return True


def build_scene(initial_speed: float) -> tuple[chrono.ChSystemNSC, chrono.ChBody, chrono.ChBody]:
    system = chrono.ChSystemNSC()
    system.SetGravitationalAcceleration(chrono.ChVector3d(0.0, 0.0, -9.81))
    system.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)

    solver = system.GetSolver()
    if solver and hasattr(solver, "AsIterative"):
        iterative_solver = solver.AsIterative()
        if iterative_solver:
            iterative_solver.SetMaxIterations(120)

    ground_material = make_material(friction=0.04, restitution=0.10)
    rover_material = make_material(friction=0.28, restitution=0.12)
    target_material = make_material(friction=0.70, restitution=0.08)

    ground = chrono.ChBodyEasyBox(
        14.0, 6.0, 0.16, 1000, True, True, ground_material)
    ground.SetName("mvp0_flat_arena")
    ground.SetFixed(True)
    ground.SetPos(chrono.ChVector3d(0.0, 0.0, -0.08))
    set_body_color(ground, (0.45, 0.50, 0.45))
    system.AddBody(ground)

    target = chrono.ChBodyEasyBox(
        TARGET_SIZE.x,
        TARGET_SIZE.y,
        TARGET_SIZE.z,
        1200,
        True,
        True,
        target_material,
    )
    target.SetName("fixed_collision_target")
    target.SetFixed(True)
    target.SetPos(TARGET_POS)
    set_body_color(target, (0.75, 0.18, 0.15))
    system.AddBody(target)

    rover = chrono.ChBodyEasyBox(
        CHASSIS_SIZE.x,
        CHASSIS_SIZE.y,
        CHASSIS_SIZE.z,
        260,
        True,
        True,
        rover_material,
    )
    rover.SetName(ROVER_NAME)
    rover.SetPos(ROVER_START)
    rover.SetPosDt(chrono.ChVector3d(initial_speed, 0.0, 0.0))
    set_body_color(rover, (0.10, 0.32, 0.68))
    add_rover_visual_hints(rover)
    system.AddBody(rover)

    return system, rover, target


def _create_vsg_system(system: chrono.ChSystemNSC):
    try:
        import pychrono.vsg3d as chronovsg

        vis = chronovsg.ChVisualSystemVSG()
        if hasattr(chrono, "CameraVerticalDir_Z"):
            vis.SetCameraVertical(chrono.CameraVerticalDir_Z)
    except ImportError:
        return None

    vis.AttachSystem(system)
    vis.SetWindowSize(1280, 720)
    vis.SetWindowTitle("Phase 4 - Hojin Rover MVP0")
    vis.AddCamera(chrono.ChVector3d(-4.5, -4.0, 2.6),
                  chrono.ChVector3d(0.0, 0.0, 0.25))
    vis.Initialize()
    return vis


def _create_irrlicht_system(system: chrono.ChSystemNSC):
    try:
        import pychrono.irrlicht as chronoirr
    except ImportError:
        return None

    vis = chronoirr.ChVisualSystemIrrlicht()

    vis.AttachSystem(system)
    vis.SetWindowSize(1280, 720)
    vis.SetWindowTitle("Phase 4 - Hojin Rover MVP0")
    vis.Initialize()
    vis.AddSkyBox()
    vis.AddCamera(chrono.ChVector3d(-4.5, -4.0, 2.6),
                  chrono.ChVector3d(0.0, 0.0, 0.25))
    vis.AddTypicalLights()
    return vis


def create_visual_system(system: chrono.ChSystemNSC, preferred_backend: str):
    if preferred_backend == "auto":
        backend_order = ["vsg", "irrlicht"]
    else:
        backend_order = [preferred_backend]

    for backend in backend_order:
        if backend == "vsg":
            vis = _create_vsg_system(system)
            if vis is not None:
                return vis, "VSG"
        elif backend == "irrlicht":
            vis = _create_irrlicht_system(system)
            if vis is not None:
                return vis, "Irrlicht"

    return None, "none"


def write_state(writer, time, rover, target_contacts, target_contact_force):
    pos = rover.GetPos()
    vel = rover.GetPosDt()
    contact_force = rover.GetContactForce()

    px, py, pz = vec_xyz(pos)
    vx, vy, vz = vec_xyz(vel)
    cfx, cfy, cfz = vec_xyz(contact_force)

    writer.writerow(
        {
            "time_s": f"{time:.4f}",
            "x_m": f"{px:.5f}",
            "y_m": f"{py:.5f}",
            "z_m": f"{pz:.5f}",
            "vx_mps": f"{vx:.5f}",
            "vy_mps": f"{vy:.5f}",
            "vz_mps": f"{vz:.5f}",
            "speed_mps": f"{math.sqrt(vx * vx + vy * vy + vz * vz):.5f}",
            "body_contact_force_N": f"{vec_length(contact_force):.5f}",
            "body_contact_fx_N": f"{cfx:.5f}",
            "body_contact_fy_N": f"{cfy:.5f}",
            "body_contact_fz_N": f"{cfz:.5f}",
            "target_contacts": target_contacts,
            "target_contact_force_sum_N": f"{target_contact_force:.5f}",
        }
    )


def run(args: argparse.Namespace) -> Path:
    system, rover, target = build_scene(args.speed)
    reporter = PairContactReporter(rover, target)

    log_path = args.output
    if not log_path.is_absolute():
        log_path = Path.cwd() / log_path
    log_path.parent.mkdir(parents=True, exist_ok=True)

    vis = None
    backend = "headless"
    if not args.no_vis and args.vis_backend != "none":
        vis, backend = create_visual_system(system, args.vis_backend)
        if vis is None:
            print("시각화 모듈이 없어 headless 모드로 실행합니다.")
            backend = "headless"

    print("=" * 72)
    print("Phase 4 / Hojin Rover MVP0")
    print(f"로버 이름: {rover.GetName()}")
    print(f"로버 질량: {rover.GetMass():.2f} kg")
    print(f"초기 속도: {args.speed:.2f} m/s")
    print(f"실행 모드: {backend}")
    print(f"CSV 로그: {log_path}")
    print("=" * 72)

    fieldnames = [
        "time_s",
        "x_m",
        "y_m",
        "z_m",
        "vx_mps",
        "vy_mps",
        "vz_mps",
        "speed_mps",
        "body_contact_force_N",
        "body_contact_fx_N",
        "body_contact_fy_N",
        "body_contact_fz_N",
        "target_contacts",
        "target_contact_force_sum_N",
    ]

    hit_time = None
    max_target_force = 0.0
    next_log_time = args.log_interval
    realtime_timer = chrono.ChRealtimeStepTimer()

    with log_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        write_state(writer, 0.0, rover, 0, 0.0)

        while system.GetChTime() < args.duration:
            if vis is not None:
                if not vis.Run():
                    break
                vis.BeginScene()
                vis.Render()
                vis.EndScene()

            system.DoStepDynamics(args.step)

            reporter.reset()
            system.GetContactContainer().ReportAllContacts(reporter)
            max_target_force = max(max_target_force, reporter.force_sum)

            time = system.GetChTime()
            if reporter.count > 0 and hit_time is None:
                hit_time = time
                print(
                    f"목표물 접촉 감지: t = {hit_time:.3f} s, contacts = {reporter.count}")

            if time + 1e-12 >= next_log_time:
                write_state(writer, time, rover,
                            reporter.count, reporter.force_sum)
                next_log_time += args.log_interval

            if vis is not None:
                realtime_timer.Spin(args.step)

    final_pos = rover.GetPos()
    final_vel = rover.GetPosDt()
    print("-" * 72)
    if hit_time is None:
        print("목표물 접촉이 감지되지 않았습니다. --speed 또는 --duration 값을 키워보세요.")
    else:
        print(f"MVP0 성공: 목표물 접촉 시각 = {hit_time:.3f} s")
    print(
        "최종 위치: "
        f"({final_pos.x:.3f}, {final_pos.y:.3f}, {final_pos.z:.3f}) m"
    )
    print(
        "최종 속도: "
        f"({final_vel.x:.3f}, {final_vel.y:.3f}, {final_vel.z:.3f}) m/s"
    )
    print(f"최대 목표물 접촉력 합: {max_target_force:.3f} N")
    print("-" * 72)

    return log_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Hojin rover MVP0 collision dummy")
    parser.add_argument("--no-vis", action="store_true",
                        help="3D 창 없이 headless 모드로 실행")
    parser.add_argument("--duration", type=float,
                        default=4.0, help="시뮬레이션 시간 [s]")
    parser.add_argument("--step", type=float,
                        default=0.002, help="물리 시간 스텝 [s]")
    parser.add_argument("--speed", type=float, default=4.0,
                        help="로버 초기 x방향 속도 [m/s]")
    parser.add_argument("--log-interval", type=float,
                        default=0.02, help="CSV 기록 간격 [s]")
    parser.add_argument("--output", type=Path,
                        default=DEFAULT_OUTPUT, help="CSV 로그 저장 경로")
    parser.add_argument(
        "--vis-backend",
        choices=("auto", "irrlicht", "vsg", "none"),
        default="auto",
        help="시각화 백엔드 선택. auto는 VSG 우선, 실패 시 Irrlicht",
    )
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())
