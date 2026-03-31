"""
==========================================================
Lesson 11: 4절 링크 기구 - 크랭크-슬라이더 메커니즘
==========================================================
학습 목표:
  1. 여러 회전 조인트를 조합해 4절 링크 기구 만들기
  2. 크랭크(입력) → 커넥팅로드 → 슬라이더(출력) 동력 전달 이해
  3. ChLinkLockPrismatic 으로 직선 운동 구속 (슬라이더)
  4. 모터로 크랭크를 회전시켜 메커니즘 자동 구동

복습 (Lesson 07~10):
  - 회전 조인트, 모터 구동

새로 배우는 것:
  - 크랭크-슬라이더 메커니즘: 회전 → 직선 운동 변환
  - ChLinkLockPrismatic: 직선 방향만 이동 허용 (서랍 레일)
  - 다중 조인트 체인: 크랭크 ↔ 커넥팅로드 ↔ 슬라이더

실행 방법:
  conda activate chrono
  source setup_chrono_env.sh
  python lessons/phase2/lesson_11_four_bar_linkage.py
==========================================================
"""

import os
import math
import matplotlib
matplotlib.use('Agg')

import pychrono as chrono

# 시각화 시스템 자동 선택 (VSG 우선, Irrlicht 폴백)
try:
    import pychrono.vsg3d as chronovsg
    USE_VSG = True
except ImportError:
    USE_VSG = False
import pychrono.irrlicht as chronoirr
import numpy as np
import matplotlib.pyplot as plt


# =============================================================================
# 기구 파라미터
# =============================================================================
# 크랭크-슬라이더 (Slider-Crank) 기구:
#   - 크랭크 (crank): 모터로 회전하는 짧은 팔
#   - 커넥팅로드 (connecting rod): 크랭크 끝과 슬라이더를 잇는 막대
#   - 슬라이더 (slider): 수평으로만 이동하는 피스톤

crank_length = 0.5      # 크랭크 길이 [m]
rod_length = 1.5        # 커넥팅로드 길이 [m]
crank_rpm = 60.0        # 크랭크 회전 속도 [RPM]
crank_omega = crank_rpm * 2 * math.pi / 60.0   # → rad/s

dt = 0.002
time_end = 5.0          # 5초 = 5바퀴


# =============================================================================
# 파라미터 출력
# =============================================================================

print("\n============================================================")
print("        Lesson 11: Slider-Crank Mechanism")
print("============================================================")
print(f"  Crank length     = {crank_length} m")
print(f"  Connecting rod   = {rod_length} m")
print(f"  Crank RPM        = {crank_rpm}")
print(f"  Crank omega      = {crank_omega:.3f} rad/s")
print(f"  Slider stroke    = {2 * crank_length} m (theory)")
print("============================================================\n")


# =============================================================================
# 시스템 생성
# =============================================================================

sys = chrono.ChSystemNSC()
sys.SetGravitationalAcceleration(chrono.ChVector3d(0, 0, 0))  # 중력 없음 (순수 기구학)


# =============================================================================
# 고정 지면 (크랭크 축 + 슬라이더 레일)
# =============================================================================

ground = chrono.ChBody()
ground.SetFixed(True)
sys.AddBody(ground)


# =============================================================================
# 크랭크 (Crank)
# =============================================================================

crank = chrono.ChBody()
crank.SetMass(1.0)
crank.SetInertiaXX(chrono.ChVector3d(0.01, 0.01, 0.1))
crank.SetPos(chrono.ChVector3d(crank_length / 2, 0, 0))
sys.AddBody(crank)

crank_shape = chrono.ChVisualShapeBox(crank_length, 0.12, 0.12)
crank_shape.SetColor(chrono.ChColor(0.8, 0.2, 0.2))   # 빨간색
crank.AddVisualShape(crank_shape)


# =============================================================================
# 커넥팅로드 (Connecting Rod)
# =============================================================================

# 초기 위치: 크랭크 끝(crank_length, 0)에서 수평으로 rod_length만큼
conrod = chrono.ChBody()
conrod.SetMass(0.5)
conrod.SetInertiaXX(chrono.ChVector3d(0.01, 0.01, 0.05))
conrod.SetPos(chrono.ChVector3d(crank_length + rod_length / 2, 0, 0))
sys.AddBody(conrod)

conrod_shape = chrono.ChVisualShapeBox(rod_length, 0.08, 0.08)
conrod_shape.SetColor(chrono.ChColor(0.3, 0.6, 0.3))   # 초록색
conrod.AddVisualShape(conrod_shape)


# =============================================================================
# 슬라이더 (Slider / Piston)
# =============================================================================

slider = chrono.ChBody()
slider.SetMass(0.5)
slider.SetInertiaXX(chrono.ChVector3d(0.01, 0.01, 0.01))
slider.SetPos(chrono.ChVector3d(crank_length + rod_length, 0, 0))
sys.AddBody(slider)

slider_shape = chrono.ChVisualShapeBox(0.3, 0.3, 0.3)
slider_shape.SetColor(chrono.ChColor(0.2, 0.2, 0.8))   # 파란색
slider.AddVisualShape(slider_shape)


# =============================================================================
# 조인트 1: 크랭크 축 (모터 회전 조인트)
# =============================================================================
# 크랭크의 왼쪽 끝을 지면에 고정하고 모터로 회전

motor = chrono.ChLinkMotorRotationSpeed()
motor.Initialize(
    crank, ground,
    chrono.ChFramed(chrono.ChVector3d(0, 0, 0), chrono.QUNIT)
)
motor.SetSpeedFunction(chrono.ChFunctionConst(crank_omega))
sys.Add(motor)


# =============================================================================
# 조인트 2: 크랭크 끝 ↔ 커넥팅로드 (회전)
# =============================================================================

joint_crank_rod = chrono.ChLinkRevolute()
joint_crank_rod.Initialize(
    crank, conrod,
    chrono.ChFramed(chrono.ChVector3d(crank_length, 0, 0), chrono.QUNIT)
)
sys.Add(joint_crank_rod)


# =============================================================================
# 조인트 3: 커넥팅로드 끝 ↔ 슬라이더 (회전)
# =============================================================================

joint_rod_slider = chrono.ChLinkRevolute()
joint_rod_slider.Initialize(
    conrod, slider,
    chrono.ChFramed(chrono.ChVector3d(crank_length + rod_length, 0, 0), chrono.QUNIT)
)
sys.Add(joint_rod_slider)


# =============================================================================
# 조인트 4: 슬라이더 ↔ 지면 (프리즈매틱 — 수평 직선만 허용)
# =============================================================================

prismatic = chrono.ChLinkLockPrismatic()
prismatic.Initialize(
    slider, ground,
    chrono.ChFramed(
        chrono.ChVector3d(crank_length + rod_length, 0, 0),
        chrono.QuatFromAngleY(math.pi / 2)  # X축 방향으로 직선 이동
    )
)
sys.Add(prismatic)


# =============================================================================
# 조인트 위치 마커
# =============================================================================

for pos in [chrono.ChVector3d(0, 0, 0)]:
    m = chrono.ChVisualShapeSphere(0.08)
    m.SetColor(chrono.ChColor(1, 1, 0))
    ground.AddVisualShape(m, chrono.ChFramed(pos))

# 슬라이더 레일 시각화 (수평선 대체 — 얇은 박스)
rail = chrono.ChVisualShapeBox(4.0, 0.02, 0.15)
rail.SetColor(chrono.ChColor(0.7, 0.7, 0.7))
ground.AddVisualShape(rail, chrono.ChFramed(chrono.ChVector3d(1.0, -0.2, 0)))


# =============================================================================
# 시각화
# =============================================================================

if USE_VSG:
    vis = chronovsg.ChVisualSystemVSG()
    vis.SetCameraVertical(chrono.CameraVerticalDir_Y)
else:
    vis = chronoirr.ChVisualSystemIrrlicht()

vis.AttachSystem(sys)
vis.SetWindowSize(1024, 720)
vis.SetWindowTitle("Lesson 11 - Slider-Crank Mechanism")

if USE_VSG:
    vis.AddCamera(chrono.ChVector3d(1, 0.5, 5), chrono.ChVector3d(1, 0, 0))
    vis.Initialize()
else:
    vis.Initialize()
    vis.AddSkyBox()
    vis.AddCamera(chrono.ChVector3d(1, 0.5, 5), chrono.ChVector3d(1, 0, 0))
    vis.AddTypicalLights()


# =============================================================================
# 데이터 수집
# =============================================================================

time_list = []
slider_x_list = []
slider_v_list = []
crank_angle_list = []
motor_torque_list = []


# =============================================================================
# 시뮬레이션 루프
# =============================================================================

frame = 0
realtime_timer = chrono.ChRealtimeStepTimer()

print(f"{'time(s)':>8}  {'crank(deg)':>11}  {'slider_x(m)':>12}  "
      f"{'slider_v(m/s)':>14}  {'torque(Nm)':>11}")
print("─" * 65)

while vis.Run():
    time = sys.GetChTime()
    if time > time_end:
        break

    vis.BeginScene()
    vis.Render()
    vis.EndScene()

    sys.DoStepDynamics(dt)
    realtime_timer.Spin(dt)

    # 데이터 기록
    crank_angle = math.degrees(motor.GetMotorAngle())
    slider_x = slider.GetPos().x
    slider_v = slider.GetPosDt().x
    torque = motor.GetMotorTorque()

    time_list.append(time)
    crank_angle_list.append(crank_angle)
    slider_x_list.append(slider_x)
    slider_v_list.append(slider_v)
    motor_torque_list.append(torque)

    if frame % 100 == 0:
        print(f"{time:8.2f}  {crank_angle:11.2f}  {slider_x:12.4f}  "
              f"{slider_v:14.4f}  {torque:11.4f}")

    frame += 1

print("\nSimulation finished")


# =============================================================================
# 이론값 비교: 슬라이더 위치
# - x = crank_length * cos(θ) + sqrt(rod_length² - crank_length² * sin²(θ))
# =============================================================================

time_arr = np.array(time_list)
theta_arr = np.radians(np.array(crank_angle_list))

x_theory = (crank_length * np.cos(theta_arr)
            + np.sqrt(rod_length**2 - (crank_length * np.sin(theta_arr))**2))

slider_x_arr = np.array(slider_x_list)
error = slider_x_arr - x_theory
rmse = np.sqrt(np.mean(error**2))

print(f"\nSlider X: RMSE vs theory = {rmse:.6f} m")


# =============================================================================
# 그래프 저장
# =============================================================================

fig, axs = plt.subplots(2, 2, figsize=(12, 8))

# 크랭크 각도 vs 슬라이더 위치
axs[0, 0].plot(crank_angle_list, slider_x_list, color='blue', label='Simulation')
axs[0, 0].plot(np.degrees(theta_arr), x_theory, 'k--', label='Theory')
axs[0, 0].set_title("Slider Position vs Crank Angle")
axs[0, 0].set_xlabel("Crank Angle (deg)")
axs[0, 0].set_ylabel("Slider X (m)")
axs[0, 0].legend()
axs[0, 0].grid()

# 슬라이더 위치 vs 시간
axs[0, 1].plot(time_arr, slider_x_list, color='blue', label='Slider X')
axs[0, 1].plot(time_arr, x_theory, 'k--', label='Theory')
axs[0, 1].set_title("Slider Position vs Time")
axs[0, 1].set_xlabel("Time (s)")
axs[0, 1].set_ylabel("X position (m)")
axs[0, 1].legend()
axs[0, 1].grid()

# 슬라이더 속도
axs[1, 0].plot(time_arr, slider_v_list, color='green')
axs[1, 0].set_title("Slider Velocity vs Time")
axs[1, 0].set_xlabel("Time (s)")
axs[1, 0].set_ylabel("Velocity (m/s)")
axs[1, 0].grid()

# 모터 토크
axs[1, 1].plot(time_arr, motor_torque_list, color='red')
axs[1, 1].set_title("Motor Torque vs Time")
axs[1, 1].set_xlabel("Time (s)")
axs[1, 1].set_ylabel("Torque (Nm)")
axs[1, 1].grid()

plt.tight_layout()

output_dir = os.path.dirname(os.path.abspath(__file__))
fig_path = os.path.join(output_dir, "lesson_11_slider_crank_plot.png")
plt.savefig(fig_path, dpi=150)
print(f"\nPlot saved: {fig_path}")

import platform
if platform.system() == 'Darwin':
    os.system(f"open '{fig_path}'")

print()
print("배운 내용:")
print("  1. 크랭크-슬라이더: 회전 운동 → 직선 왕복 운동 변환")
print("  2. ChLinkLockPrismatic — 한 방향 직선 이동만 허용")
print("  3. 모터 + 다중 조인트 체인으로 메커니즘 구성")
print("  4. 기구학 이론값과 시뮬레이션 비교 검증")
print()
print("다음 단계:")
print("  → lesson_12에서 기어와 풀리로 동력을 전달합니다")
