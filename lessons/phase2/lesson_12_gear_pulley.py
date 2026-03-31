"""
==========================================================
Lesson 12: 기어와 풀리 - 동력 전달 시스템
==========================================================
학습 목표:
  1. ChShaftsGear 로 두 축 사이의 기어비 구속 만들기
  2. 구동 기어(모터) → 피동 기어(출력) 동력 전달 관찰
  3. 기어비에 따른 속도/토크 변환 이해
  4. 1D 축(ChShaft) + 3D 물체(ChBody) 연결 패턴

복습 (Lesson 07~11):
  - 회전 조인트, 모터, 4절 링크

새로 배우는 것:
  - ChShaft: 1D 회전축 (관성만 가짐)
  - ChShaftsGear: 두 축 사이 기어비 구속
  - ChShaftsMotorSpeed: 축에 모터 부착
  - ChShaftBodyRotation: 1D 축 ↔ 3D 물체 연결
  - 기어비: 큰 기어 → 느린 속도, 큰 토크

실행 방법:
  conda activate chrono
  source setup_chrono_env.sh
  python lessons/phase2/lesson_12_gear_pulley.py
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
# 파라미터
# =============================================================================

# 기어 A (구동, 작은 기어)
r_A = 0.3
# 기어 B (피동, 큰 기어)
r_B = 0.9
# 기어비: B는 A보다 3배 느리게 회전
gear_ratio = -r_A / r_B   # 음수 = 반대 방향 회전 (외접 기어)

# 기어 C (구동, 작은 풀리)
r_C = 0.3
# 기어 D (피동, 큰 풀리)
r_D = 0.6
# 풀리비: 같은 방향 회전 (벨트 연결)
pulley_ratio = r_C / r_D   # 양수 = 같은 방향

# 모터
motor_rpm = 120.0
motor_omega = motor_rpm * 2 * math.pi / 60.0

dt = 0.002
time_end = 8.0


# =============================================================================
# 파라미터 출력
# =============================================================================

print("\n============================================================")
print("        Lesson 12: Gear & Pulley Power Transmission")
print("============================================================")
print(f"\n--- Gear Train (left) ---")
print(f"  Drive gear radius   = {r_A} m")
print(f"  Driven gear radius  = {r_B} m")
print(f"  Gear ratio          = 1:{r_B / r_A:.0f} (opposite rotation)")
print(f"  Motor RPM           = {motor_rpm}")
print(f"  Expected driven RPM = {motor_rpm * abs(gear_ratio):.1f}")
print(f"\n--- Pulley System (right) ---")
print(f"  Pulley C radius     = {r_C} m")
print(f"  Pulley D radius     = {r_D} m")
print(f"  Speed ratio         = 1:{r_D / r_C:.0f} (same rotation)")
print(f"  Expected D RPM      = {motor_rpm * pulley_ratio:.1f}")
print("============================================================\n")


# =============================================================================
# 시스템 생성
# =============================================================================

sys = chrono.ChSystemNSC()
sys.SetGravitationalAcceleration(chrono.ChVector3d(0, 0, 0))


# =============================================================================
# 고정 지면
# =============================================================================

ground = chrono.ChBody()
ground.SetFixed(True)
sys.AddBody(ground)

# --- 휠 시각화 헬퍼 ---
# macOS Irrlicht에서 원형을 근사하기 위해 작은 박스를 원형으로 배치
def add_wheel_visual(body, radius, color, n_rim=12, thickness=0.08):
    """원형 휠 시각화: 림(외곽) + 스포크(살) + 허브(중심)"""
    # 림: 작은 박스를 원형으로 배치
    rim_size = 2 * math.pi * radius / n_rim * 0.7
    for i in range(n_rim):
        angle = 2 * math.pi * i / n_rim
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        rim = chrono.ChVisualShapeBox(rim_size, rim_size, thickness)
        rim.SetColor(color)
        body.AddVisualShape(
            rim, chrono.ChFramed(chrono.ChVector3d(x, y, 0),
                                 chrono.QuatFromAngleZ(angle))
        )
    # 스포크: 중심에서 림까지 2개
    for angle in [0, math.pi / 2]:
        spoke = chrono.ChVisualShapeBox(0.05, radius * 1.8, thickness)
        spoke.SetColor(chrono.ChColor(color.R * 0.7, color.G * 0.7, color.B * 0.7))
        body.AddVisualShape(
            spoke, chrono.ChFramed(chrono.ChVector3d(0, 0, 0),
                                   chrono.QuatFromAngleZ(angle))
        )
    # 허브: 중심에 작은 구
    hub = chrono.ChVisualShapeSphere(radius * 0.15)
    hub.SetColor(chrono.ChColor(0.3, 0.3, 0.3))
    body.AddVisualShape(hub)
    # 방향 표시: 한쪽 끝에 노란 구
    tick = chrono.ChVisualShapeSphere(radius * 0.12)
    tick.SetColor(chrono.ChColor(1, 1, 0))
    body.AddVisualShape(
        tick, chrono.ChFramed(chrono.ChVector3d(0, radius, 0))
    )


# 지지대 시각화: 기어/풀리 축 위치에 수직 기둥
for x_pos in [-1.5, 1.5]:
    bar = chrono.ChVisualShapeBox(0.15, 3.5, 0.15)
    bar.SetColor(chrono.ChColor(0.5, 0.5, 0.5))
    ground.AddVisualShape(
        bar, chrono.ChFramed(chrono.ChVector3d(x_pos, 0.5, 0))
    )


# =============================================================================
# ===== 기어 트레인 (왼쪽, x = -1.5) =====
# =============================================================================

gear_x = -1.5
gear_center_dist = r_A + r_B   # 두 기어 중심 간 거리

# --- 3D 물체: 기어 A (구동, 빨간) ---
body_A = chrono.ChBody()
body_A.SetMass(1.0)
body_A.SetInertiaXX(chrono.ChVector3d(0.5, 0.5, 0.5 * 1.0 * r_A**2))
body_A.SetPos(chrono.ChVector3d(gear_x, 0, 0))
sys.AddBody(body_A)

add_wheel_visual(body_A, r_A, chrono.ChColor(0.8, 0.2, 0.2))

# 축 고정: 회전 조인트
rev_A = chrono.ChLinkRevolute()
rev_A.Initialize(
    body_A, ground,
    chrono.ChFramed(chrono.ChVector3d(gear_x, 0, 0), chrono.QUNIT)
)
sys.Add(rev_A)


# --- 3D 물체: 기어 B (피동, 파란) ---
body_B = chrono.ChBody()
body_B.SetMass(3.0)
body_B.SetInertiaXX(chrono.ChVector3d(0.5, 0.5, 0.5 * 3.0 * r_B**2))
body_B.SetPos(chrono.ChVector3d(gear_x, gear_center_dist, 0))
sys.AddBody(body_B)

add_wheel_visual(body_B, r_B, chrono.ChColor(0.2, 0.2, 0.8), n_rim=18)

rev_B = chrono.ChLinkRevolute()
rev_B.Initialize(
    body_B, ground,
    chrono.ChFramed(
        chrono.ChVector3d(gear_x, gear_center_dist, 0), chrono.QUNIT
    )
)
sys.Add(rev_B)


# --- 1D 축 + 기어 구속 ---
# ChShaft: 회전 자유도 1개만 가진 가상의 축
shaft_A = chrono.ChShaft()
shaft_A.SetInertia(0.5 * 1.0 * r_A**2)
sys.Add(shaft_A)

shaft_B = chrono.ChShaft()
shaft_B.SetInertia(0.5 * 3.0 * r_B**2)
sys.Add(shaft_B)

# ChShaftBodyRotation: 1D 축의 회전 ↔ 3D 물체의 Z축 회전을 동기화
connect_A = chrono.ChShaftBodyRotation()
connect_A.Initialize(shaft_A, body_A, chrono.ChVector3d(0, 0, 1))
sys.Add(connect_A)

connect_B = chrono.ChShaftBodyRotation()
connect_B.Initialize(shaft_B, body_B, chrono.ChVector3d(0, 0, 1))
sys.Add(connect_B)

# ChShaftsGear: 두 축 사이 기어비 구속
gear_link = chrono.ChShaftsGear()
gear_link.Initialize(shaft_A, shaft_B)
gear_link.SetTransmissionRatio(gear_ratio)
sys.Add(gear_link)

# 모터: shaft_A를 일정 속도로 구동
# ChShaftsMotorSpeed는 두 개의 ChShaft 필요 → 고정 축 생성
ground_shaft_A = chrono.ChShaft()
ground_shaft_A.SetFixed(True)
sys.Add(ground_shaft_A)

motor_shaft_A = chrono.ChShaftsMotorSpeed()
motor_shaft_A.Initialize(shaft_A, ground_shaft_A)
motor_shaft_A.SetSpeedFunction(chrono.ChFunctionConst(motor_omega))
sys.Add(motor_shaft_A)


# =============================================================================
# ===== 풀리 시스템 (오른쪽, x = 1.5) =====
# =============================================================================

pulley_x = 1.5
pulley_gap = 2.0   # 풀리 간 수직 거리

# --- 3D 물체: 풀리 C (구동, 주황) ---
body_C = chrono.ChBody()
body_C.SetMass(1.0)
body_C.SetInertiaXX(chrono.ChVector3d(0.5, 0.5, 0.5 * 1.0 * r_C**2))
body_C.SetPos(chrono.ChVector3d(pulley_x, 0, 0))
sys.AddBody(body_C)

add_wheel_visual(body_C, r_C, chrono.ChColor(0.8, 0.5, 0.0))

rev_C = chrono.ChLinkRevolute()
rev_C.Initialize(
    body_C, ground,
    chrono.ChFramed(chrono.ChVector3d(pulley_x, 0, 0), chrono.QUNIT)
)
sys.Add(rev_C)


# --- 3D 물체: 풀리 D (피동, 청록) ---
body_D = chrono.ChBody()
body_D.SetMass(2.0)
body_D.SetInertiaXX(chrono.ChVector3d(0.5, 0.5, 0.5 * 2.0 * r_D**2))
body_D.SetPos(chrono.ChVector3d(pulley_x, pulley_gap, 0))
sys.AddBody(body_D)

add_wheel_visual(body_D, r_D, chrono.ChColor(0.0, 0.6, 0.6), n_rim=15)

rev_D = chrono.ChLinkRevolute()
rev_D.Initialize(
    body_D, ground,
    chrono.ChFramed(
        chrono.ChVector3d(pulley_x, pulley_gap, 0), chrono.QUNIT
    )
)
sys.Add(rev_D)


# --- 1D 축 + 풀리(기어) 구속 ---
shaft_C = chrono.ChShaft()
shaft_C.SetInertia(0.5 * 1.0 * r_C**2)
sys.Add(shaft_C)

shaft_D = chrono.ChShaft()
shaft_D.SetInertia(0.5 * 2.0 * r_D**2)
sys.Add(shaft_D)

connect_C = chrono.ChShaftBodyRotation()
connect_C.Initialize(shaft_C, body_C, chrono.ChVector3d(0, 0, 1))
sys.Add(connect_C)

connect_D = chrono.ChShaftBodyRotation()
connect_D.Initialize(shaft_D, body_D, chrono.ChVector3d(0, 0, 1))
sys.Add(connect_D)

# 풀리 = 같은 방향 기어 (양수 비율)
pulley_link = chrono.ChShaftsGear()
pulley_link.Initialize(shaft_C, shaft_D)
pulley_link.SetTransmissionRatio(pulley_ratio)
sys.Add(pulley_link)

# 모터
ground_shaft_C = chrono.ChShaft()
ground_shaft_C.SetFixed(True)
sys.Add(ground_shaft_C)

motor_shaft_C = chrono.ChShaftsMotorSpeed()
motor_shaft_C.Initialize(shaft_C, ground_shaft_C)
motor_shaft_C.SetSpeedFunction(chrono.ChFunctionConst(motor_omega))
sys.Add(motor_shaft_C)


# =============================================================================
# 축 위치 마커 (초록 구)
# =============================================================================

for pos in [chrono.ChVector3d(gear_x, 0, 0),
            chrono.ChVector3d(gear_x, gear_center_dist, 0),
            chrono.ChVector3d(pulley_x, 0, 0),
            chrono.ChVector3d(pulley_x, pulley_gap, 0)]:
    m = chrono.ChVisualShapeSphere(0.06)
    m.SetColor(chrono.ChColor(0.0, 0.8, 0.0))
    ground.AddVisualShape(m, chrono.ChFramed(pos))


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
vis.SetWindowTitle("Lesson 12 - Gear & Pulley")

if USE_VSG:
    vis.AddCamera(chrono.ChVector3d(0, 1.5, 7), chrono.ChVector3d(0, 1, 0))
    vis.Initialize()
else:
    vis.Initialize()
    vis.AddSkyBox()
    vis.AddCamera(chrono.ChVector3d(0, 1.5, 7), chrono.ChVector3d(0, 1, 0))
    vis.AddTypicalLights()


# =============================================================================
# 데이터 수집
# =============================================================================

time_list = []
rpm_A_list = []
rpm_B_list = []
rpm_C_list = []
rpm_D_list = []


# =============================================================================
# 시뮬레이션 루프
# =============================================================================

frame = 0
realtime_timer = chrono.ChRealtimeStepTimer()

print(f"{'time':>6}  {'Gear A':>10}  {'Gear B':>10}  "
      f"{'Pulley C':>10}  {'Pulley D':>10}  (RPM)")
print("─" * 56)

while vis.Run():
    time = sys.GetChTime()
    if time > time_end:
        break

    vis.BeginScene()
    vis.Render()
    vis.EndScene()

    sys.DoStepDynamics(dt)
    realtime_timer.Spin(dt)

    # 각속도 → RPM
    w_A = abs(shaft_A.GetPosDt()) * 60 / (2 * math.pi)
    w_B = abs(shaft_B.GetPosDt()) * 60 / (2 * math.pi)
    w_C = abs(shaft_C.GetPosDt()) * 60 / (2 * math.pi)
    w_D = abs(shaft_D.GetPosDt()) * 60 / (2 * math.pi)

    time_list.append(time)
    rpm_A_list.append(w_A)
    rpm_B_list.append(w_B)
    rpm_C_list.append(w_C)
    rpm_D_list.append(w_D)

    if frame % 100 == 0:
        print(f"{time:6.2f}  {w_A:10.2f}  {w_B:10.2f}  "
              f"{w_C:10.2f}  {w_D:10.2f}")

    frame += 1

print("\nSimulation finished")


# =============================================================================
# 결과 검증
# =============================================================================

expected_B = motor_rpm * abs(gear_ratio)
expected_D = motor_rpm * pulley_ratio
avg_B = np.mean(rpm_B_list[-500:])
avg_D = np.mean(rpm_D_list[-500:])

print(f"\n{'=' * 56}")
print("Gear Train (opposite rotation):")
print(f"  Expected B RPM = {expected_B:.1f}")
print(f"  Measured B RPM = {avg_B:.1f}")
print(f"  Error = {abs(avg_B - expected_B):.2f} RPM")

print(f"\nPulley System (same rotation):")
print(f"  Expected D RPM = {expected_D:.1f}")
print(f"  Measured D RPM = {avg_D:.1f}")
print(f"  Error = {abs(avg_D - expected_D):.2f} RPM")
print(f"{'=' * 56}")


# =============================================================================
# 그래프 저장
# =============================================================================

time_arr = np.array(time_list)

fig, axs = plt.subplots(1, 2, figsize=(12, 5))

# 기어 RPM
axs[0].plot(time_arr, rpm_A_list, color='red',
            label=f"Gear A (r={r_A}m)")
axs[0].plot(time_arr, rpm_B_list, color='blue',
            label=f"Gear B (r={r_B}m)")
axs[0].axhline(motor_rpm, color='red', ls=':', alpha=0.5,
               label=f"Expected A={motor_rpm:.0f}")
axs[0].axhline(expected_B, color='blue', ls=':', alpha=0.5,
               label=f"Expected B={expected_B:.0f}")
axs[0].set_title("Gear Train: RPM")
axs[0].set_xlabel("Time (s)")
axs[0].set_ylabel("RPM")
axs[0].legend()
axs[0].grid()

# 풀리 RPM
axs[1].plot(time_arr, rpm_C_list, color='orange',
            label=f"Pulley C (r={r_C}m)")
axs[1].plot(time_arr, rpm_D_list, color='teal',
            label=f"Pulley D (r={r_D}m)")
axs[1].axhline(motor_rpm, color='orange', ls=':', alpha=0.5)
axs[1].axhline(expected_D, color='teal', ls=':', alpha=0.5,
               label=f"Expected D={expected_D:.0f}")
axs[1].set_title("Pulley System: RPM")
axs[1].set_xlabel("Time (s)")
axs[1].set_ylabel("RPM")
axs[1].legend()
axs[1].grid()

plt.tight_layout()

output_dir = os.path.dirname(os.path.abspath(__file__))
fig_path = os.path.join(output_dir, "lesson_12_gear_pulley_plot.png")
plt.savefig(fig_path, dpi=150)
print(f"\nPlot saved: {fig_path}")

import platform
if platform.system() == 'Darwin':
    os.system(f"open '{fig_path}'")

print()
print("배운 내용:")
print("  1. ChShaft — 1D 회전축 (관성만 가진 가상 축)")
print("  2. ChShaftsGear — 두 축 사이 기어비 구속")
print("     - 음수 비율 = 반대 방향 (외접 기어)")
print("     - 양수 비율 = 같은 방향 (벨트/풀리)")
print("  3. ChShaftBodyRotation — 1D 축 ↔ 3D 물체 연결")
print("  4. 큰 기어/풀리 → 느린 속도, 큰 토크 (감속 = 토크 증폭)")
print()
print("Phase 2 완료! 다음 단계:")
print("  → Phase 3에서 로버, 드론, 환경 시뮬레이션을 시작합니다")
