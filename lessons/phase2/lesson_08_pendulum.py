"""
==========================================================
Lesson 08: 진자 운동 - 단진자 시뮬레이션과 이론 검증
==========================================================
학습 목표:
  1. 회전 조인트로 단진자(simple pendulum)를 구성하기
  2. 시뮬레이션 결과를 이론값(소각도 근사)과 비교하기
  3. 초기 각도에 따른 주기 변화 관찰하기
  4. matplotlib로 결과를 그래프로 저장하기

복습 (Lesson 07):
  - ChLinkRevolute로 두 물체를 경첩 연결

새로 배우는 것:
  - 단진자 물리: 주기 T = 2π√(L/g)
  - SetRot() 으로 물체에 초기 각도 부여
  - 시뮬레이션 vs 이론값 비교 (RMSE 계산)

실행 방법:
  conda activate chrono
  source setup_chrono_env.sh
  python lessons/phase2/lesson_08_pendulum.py
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
# 시뮬레이션 파라미터
# =============================================================================

g = 9.81            # 중력가속도 [m/s²]
L = 2.0             # 진자 길이 [m]
mass = 1.0          # 추의 질량 [kg]
theta0_deg = 15.0   # 초기 각도 [도] (소각도 근사 유효 범위: < 20°)
theta0 = math.radians(theta0_deg)

dt = 0.001          # 시간 스텝 [s]
time_end = 10.0     # 시뮬레이션 시간 [s]

# 이론값: 소각도 근사 주기
T_theory = 2 * math.pi * math.sqrt(L / g)
omega = math.sqrt(g / L)   # 고유 각진동수


# =============================================================================
# 파라미터 출력
# =============================================================================

print("\n============================================================")
print("        Lesson 08: Simple Pendulum Simulation")
print("============================================================")
print(f"  Length   = {L} m")
print(f"  Mass     = {mass} kg")
print(f"  Theta0   = {theta0_deg} deg")
print(f"  Period (theory, small angle) = {T_theory:.4f} s")
print(f"  Angular frequency = {omega:.4f} rad/s")
print("============================================================\n")


# =============================================================================
# Chrono 시스템 생성
# =============================================================================

sys = chrono.ChSystemNSC()
sys.SetGravitationalAcceleration(chrono.ChVector3d(0, -g, 0))


# =============================================================================
# 피벗 (고정점)
# =============================================================================

pivot = chrono.ChBody()
pivot.SetFixed(True)
sys.AddBody(pivot)

# 피벗 위치에 작은 구 표시
pivot_marker = chrono.ChVisualShapeSphere(0.1)
pivot_marker.SetColor(chrono.ChColor(0.0, 0.8, 0.0))
pivot.AddVisualShape(pivot_marker)


# =============================================================================
# 진자 막대 (하나의 강체로 구성)
# =============================================================================
# 핵심: 막대 하나에 줄(실린더) + 추(구) 시각화를 모두 붙입니다.
# 막대의 무게중심을 아래쪽 끝(추 위치)에 놓으면 점질량 진자에 근사합니다.
#
# 로컬 좌표계:
#   - 원점 = 막대 무게중심 = 추 위치 (아래쪽 끝)
#   - 피벗은 로컬 (0, +L, 0) 위치

# 초기 위치: 피벗(0,0,0)에서 L만큼 아래 + 초기 각도만큼 벗어남
x0 = L * math.sin(theta0)
y0 = -L * math.cos(theta0)

pendulum = chrono.ChBody()
pendulum.SetMass(mass)
# 점질량 근사: 관성 최소화 (질량이 끝점에 집중)
pendulum.SetInertiaXX(chrono.ChVector3d(0.01, 0.01, 0.01))
# 무게중심 = 추 위치
pendulum.SetPos(chrono.ChVector3d(x0, y0, 0))
# 초기 각도만큼 회전 (양의 방향이어야 로컬 +Y가 피벗을 향함)
pendulum.SetRot(chrono.QuatFromAngleZ(theta0))
sys.AddBody(pendulum)

# 시각화 1: 추 (빨간 구) — 로컬 원점에 위치
bob_shape = chrono.ChVisualShapeSphere(0.15)
bob_shape.SetColor(chrono.ChColor(0.8, 0.1, 0.1))
pendulum.AddVisualShape(bob_shape)

# 시각화 2: 줄 (얇은 박스) — 로컬 원점에서 위로 L만큼
# macOS Irrlicht에서 가느다란 실린더가 안 보일 수 있으므로 박스 사용
rod_shape = chrono.ChVisualShapeBox(0.06, L, 0.06)
rod_shape.SetColor(chrono.ChColor(0.4, 0.4, 0.4))
pendulum.AddVisualShape(
    rod_shape,
    chrono.ChFramed(chrono.ChVector3d(0, L / 2, 0))
)


# =============================================================================
# 회전 조인트: 피벗과 진자를 연결
# =============================================================================
# 진자의 핵심: 추는 피벗 주위로 Z축 회전만 가능
# 조인트 위치 = 피벗 = 월드 (0, 0, 0)

joint = chrono.ChLinkRevolute()
joint_frame = chrono.ChFramed(
    chrono.ChVector3d(0, 0, 0),    # 피벗 위치 (월드 좌표)
    chrono.QUNIT                   # Z축 회전
)
joint.Initialize(pivot, pendulum, joint_frame)
sys.Add(joint)


# =============================================================================
# 시각화 설정
# =============================================================================

if USE_VSG:
    vis = chronovsg.ChVisualSystemVSG()
    vis.SetCameraVertical(chrono.CameraVerticalDir_Y)
else:
    vis = chronoirr.ChVisualSystemIrrlicht()

vis.AttachSystem(sys)
vis.SetWindowSize(1024, 720)
vis.SetWindowTitle("Lesson 08 - Simple Pendulum")

if USE_VSG:
    vis.AddCamera(chrono.ChVector3d(0, -1, 6), chrono.ChVector3d(0, -1, 0))
    vis.Initialize()
else:
    vis.Initialize()
    vis.AddSkyBox()
    vis.AddCamera(chrono.ChVector3d(0, -1, 6), chrono.ChVector3d(0, -1, 0))
    vis.AddTypicalLights()


# =============================================================================
# 데이터 수집용 리스트
# =============================================================================

time_list = []
theta_sim = []      # 시뮬레이션 각도
theta_theory = []   # 이론 각도 (소각도 근사)


# =============================================================================
# 시뮬레이션 루프
# =============================================================================

frame = 0
realtime_timer = chrono.ChRealtimeStepTimer()

while vis.Run():
    time = sys.GetChTime()
    if time > time_end:
        break

    vis.BeginScene()
    vis.Render()
    vis.EndScene()

    sys.DoStepDynamics(dt)
    realtime_timer.Spin(dt)

    # 추 위치에서 각도 계산 (무게중심 = 추 위치)
    pos = pendulum.GetPos()
    theta = math.atan2(pos.x, -pos.y)

    # 소각도 이론값: theta(t) = theta0 * cos(omega * t)
    theta_th = theta0 * math.cos(omega * time)

    time_list.append(time)
    theta_sim.append(math.degrees(theta))
    theta_theory.append(math.degrees(theta_th))

    if frame % 200 == 0:
        print(
            f"t={time:6.2f}s  "
            f"theta_sim={math.degrees(theta):+8.3f} deg  "
            f"theta_theory={math.degrees(theta_th):+8.3f} deg"
        )

    frame += 1

print("\nSimulation finished")


# =============================================================================
# 결과 분석
# =============================================================================

time_arr = np.array(time_list)
sim_arr = np.array(theta_sim)
th_arr = np.array(theta_theory)
error = sim_arr - th_arr
rmse = np.sqrt(np.mean(error**2))

print(f"\n{'=' * 50}")
print(f"RMSE (simulation vs small-angle theory) = {rmse:.4f} deg")
print(f"Theory period = {T_theory:.4f} s")

# 시뮬레이션 주기 측정: 양→음 제로 크로싱 2개 사이 시간
zero_crossings = []
for i in range(1, len(sim_arr)):
    if sim_arr[i - 1] > 0 and sim_arr[i] <= 0:
        zero_crossings.append(time_arr[i])
    if len(zero_crossings) >= 2:
        break

if len(zero_crossings) >= 2:
    T_sim = zero_crossings[1] - zero_crossings[0]
    print(f"Simulation period = {T_sim:.4f} s")
    err_pct = abs(T_sim - T_theory) / T_theory * 100
    print(f"Period error = {abs(T_sim - T_theory):.4f} s ({err_pct:.2f}%)")
print(f"{'=' * 50}")


# =============================================================================
# 그래프 저장
# =============================================================================

fig, axs = plt.subplots(2, 1, figsize=(10, 7))

# 상단: 각도 비교
axs[0].plot(time_arr, sim_arr, color='red', label="Simulation")
axs[0].plot(time_arr, th_arr, 'k--', label="Theory (small angle)")
axs[0].set_xlabel("Time (s)")
axs[0].set_ylabel("Angle (degrees)")
axs[0].set_title(
    f"Simple Pendulum: L={L}m, theta0={theta0_deg} deg"
)
axs[0].legend()
axs[0].grid()

# 하단: 오차
axs[1].plot(time_arr, error, color='black')
axs[1].axhline(0, color='gray', linewidth=0.8)
axs[1].set_xlabel("Time (s)")
axs[1].set_ylabel("Error (degrees)")
axs[1].set_title(f"Error (Sim - Theory), RMSE = {rmse:.4f} deg")
axs[1].grid()

plt.tight_layout()

output_dir = os.path.dirname(os.path.abspath(__file__))
fig_path = os.path.join(output_dir, "lesson_08_pendulum_plot.png")
plt.savefig(fig_path, dpi=150)
print(f"\nPlot saved: {fig_path}")

import platform
if platform.system() == 'Darwin':
    os.system(f"open '{fig_path}'")

print()
print("다음 단계:")
print("  → lesson_09에서 스프링-댐퍼를 배웁니다")
print("  → lesson_10에서 모터 구동을 배웁니다")
