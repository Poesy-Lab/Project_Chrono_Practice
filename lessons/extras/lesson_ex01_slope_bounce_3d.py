"""
lesson_ex01_slope_bounce_3d.py  (보너스 예제 — 로드맵 외)

설명:
- 넓은 경사면 위로 서로 다른 재질의 공 2개를 동시에 떨어뜨리는 3D 시뮬레이션
- 빨간 공: 고무 (반발 큼), 은색 공: 강철 (반발 작음)
- Phase 1 재질/충돌 개념을 3D 경사면에 응용한 실습 예제

실행:
    conda activate chrono
    source setup_chrono_env.sh
    python lessons/extras/lesson_ex01_slope_bounce_3d.py
"""

import math
import pychrono as chrono

# 시각화 시스템 자동 선택 (VSG 우선, Irrlicht 폴백)
try:
    import pychrono.vsg3d as chronovsg
    USE_VSG = True
except ImportError:
    USE_VSG = False
import pychrono.irrlicht as chronoirr


# =========================================================
# 1. 시스템 생성
# =========================================================
system = chrono.ChSystemNSC()
system.SetGravitationalAcceleration(chrono.ChVector3d(0, -9.81, 0))
system.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)

solver = system.GetSolver()
if solver and hasattr(solver, "AsIterative"):
    iterative_solver = solver.AsIterative()
    if iterative_solver:
        iterative_solver.SetMaxIterations(150)


# =========================================================
# 2. 재질 생성
# =========================================================
# 고무: 마찰 큼, 반발 매우 큼
rubber_material = chrono.ChContactMaterialNSC()
rubber_material.SetFriction(0.85)
rubber_material.SetRestitution(0.95)

# 강철: 마찰 보통, 반발 낮음
steel_material = chrono.ChContactMaterialNSC()
steel_material.SetFriction(0.40)
steel_material.SetRestitution(0.35)


# =========================================================
# 3. 바닥 생성
# =========================================================
floor = chrono.ChBodyEasyBox(
    24.0,   # x 길이
    2.0,    # y 두께
    10.0,   # z 길이
    1000,
    True,
    True,
    steel_material
)
floor.SetFixed(True)
floor.SetPos(chrono.ChVector3d(0, -1.0, 0))

floor_visual_shape = floor.GetVisualShape(0)
if floor_visual_shape:
    floor_visual_shape.SetColor(chrono.ChColor(0.55, 0.55, 0.55))   # 회색

system.Add(floor)


# =========================================================
# 4. 경사면 생성
# =========================================================
ramp = chrono.ChBodyEasyBox(
    10.0,   # x 길이
    1.0,    # y 두께
    6.0,    # z 길이
    1000,
    True,
    True,
    steel_material
)
ramp.SetFixed(True)
ramp.SetPos(chrono.ChVector3d(0.5, 1.5, 0.0))

ramp_angle_deg = -25.0
ramp_angle_rad = math.radians(ramp_angle_deg)
ramp.SetRot(chrono.QuatFromAngleZ(ramp_angle_rad))

ramp_visual_shape = ramp.GetVisualShape(0)
if ramp_visual_shape:
    ramp_visual_shape.SetColor(chrono.ChColor(0.20, 0.45, 0.85))    # 파란색

system.Add(ramp)


# =========================================================
# 5. 공 2개 생성
# =========================================================
ball_radius = 0.25

# 고무 공
rubber_ball = chrono.ChBodyEasySphere(
    ball_radius,
    1200,
    True,
    True,
    rubber_material
)
rubber_ball.SetPos(chrono.ChVector3d(-2.0, 5.0, -0.8))
rubber_ball.SetPosDt(chrono.ChVector3d(0.0, 0.0, 0.0))

rubber_visual_shape = rubber_ball.GetVisualShape(0)
if rubber_visual_shape:
    rubber_visual_shape.SetColor(chrono.ChColor(0.95, 0.15, 0.15))  # 빨간색

system.Add(rubber_ball)

# 강철 공
steel_ball = chrono.ChBodyEasySphere(
    ball_radius,
    7800,
    True,
    True,
    steel_material
)
steel_ball.SetPos(chrono.ChVector3d(-2.0, 5.0, 0.8))
steel_ball.SetPosDt(chrono.ChVector3d(0.0, 0.0, 0.0))

steel_visual_shape = steel_ball.GetVisualShape(0)
if steel_visual_shape:
    steel_visual_shape.SetColor(chrono.ChColor(0.85, 0.85, 0.90))   # 은색

system.Add(steel_ball)


# =========================================================
# 6. 실행 안내 출력
# =========================================================
print("=" * 70)
print("lesson_07_slope_bounce_3d 시작")
print("빨간 공 = 고무(반발 매우 큼), 은색 공 = 강철(반발 작음)")
print("정상이라면 고무 공이 더 크게 튀고, 강철 공은 덜 튄다.")
print("=" * 70)


# =========================================================
# 7. Irrlicht 3D 시각화
# =========================================================
if USE_VSG:
    vis = chronovsg.ChVisualSystemVSG()
else:
    vis = chronoirr.ChVisualSystemIrrlicht()

vis.AttachSystem(system)
vis.SetWindowSize(1280, 720)
vis.SetWindowTitle("Lesson 07 - Two Balls on Wide Ramp")

if USE_VSG:
    vis.AddCamera(chrono.ChVector3d(0, 4.5, 11))
    vis.Initialize()
else:
    vis.Initialize()
    vis.AddLogo()
    vis.AddSkyBox()
    vis.AddTypicalLights()
    vis.AddCamera(chrono.ChVector3d(0, 4.5, 11))


# =========================================================
# 8. 시뮬레이션 루프
# =========================================================
dt = 0.002
print_time = 0.0
realtime_timer = chrono.ChRealtimeStepTimer()

while vis.Run():
    vis.BeginScene()
    vis.Render()
    vis.EndScene()

    system.DoStepDynamics(dt)
    realtime_timer.Spin(dt)

    t = system.GetChTime()

    rubber_pos = rubber_ball.GetPos()
    rubber_vel = rubber_ball.GetPosDt()

    steel_pos = steel_ball.GetPos()
    steel_vel = steel_ball.GetPosDt()

    if t >= print_time:
        print(
            f"time={t:.2f}s | "
            f"rubber_pos=({rubber_pos.x:.3f}, {rubber_pos.y:.3f}, {rubber_pos.z:.3f}) | "
            f"rubber_vel=({rubber_vel.x:.3f}, {rubber_vel.y:.3f}, {rubber_vel.z:.3f})"
        )
        print(
            f"           steel_pos =({steel_pos.x:.3f}, {steel_pos.y:.3f}, {steel_pos.z:.3f}) | "
            f"steel_vel =({steel_vel.x:.3f}, {steel_vel.y:.3f}, {steel_vel.z:.3f})"
        )
        print_time += 0.5
