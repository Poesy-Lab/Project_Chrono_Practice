"""
==========================================================
Lesson 10: 모터 구동 - 조인트에 모터를 달아 자동 회전
==========================================================
학습 목표:
  1. ChLinkMotorRotationSpeed 로 일정 속도 회전 모터 만들기
  2. ChLinkMotorRotationAngle 로 각도 제어 모터 만들기
  3. 모터 토크/회전 정보 읽기
  4. ChFunctionConst, ChFunctionSine 등 입력 함수 사용법

복습 (Lesson 07~09):
  - 회전 조인트, 진자 운동, 스프링-댐퍼

새로 배우는 것:
  - ChLinkMotorRotationSpeed: 지정 속도로 회전 (RPM 제어)
  - ChLinkMotorRotationAngle: 지정 각도 궤적 추종
  - ChFunctionConst / ChFunctionSine: 모터 입력 함수
  - 모터 토크 조회: GetMotorTorque()

실행 방법:
  conda activate chrono
  source setup_chrono_env.sh
  python lessons/phase2/lesson_10_motor.py
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

rpm = 30.0                              # 목표 회전 속도 [RPM]
omega = rpm * 2 * math.pi / 60.0        # → rad/s 변환
arm_length = 1.5                        # 회전팔 길이 [m]
arm_mass = 2.0                          # 회전팔 질량 [kg]

dt = 0.005
time_end = 10.0


# =============================================================================
# 파라미터 출력
# =============================================================================

print("\n============================================================")
print("        Lesson 10: Motor-Driven Rotation")
print("============================================================")
print(f"  Target RPM    = {rpm}")
print(f"  Angular speed = {omega:.3f} rad/s")
print(f"  Arm length    = {arm_length} m")
print(f"  Arm mass      = {arm_mass} kg")
print("============================================================\n")


# =============================================================================
# 시스템 생성
# =============================================================================

sys = chrono.ChSystemNSC()
sys.SetGravitationalAcceleration(chrono.ChVector3d(0, -9.81, 0))


# =============================================================================
# 고정 지지대
# =============================================================================

ground = chrono.ChBody()
ground.SetFixed(True)
sys.AddBody(ground)

# 지지대 시각화: 두 모터 피벗을 연결하는 수평 바
ground_bar = chrono.ChVisualShapeBox(4.0, 0.15, 0.15)
ground_bar.SetColor(chrono.ChColor(0.5, 0.5, 0.5))
ground.AddVisualShape(ground_bar)


# =============================================================================
# 모터 A: 일정 속도 회전 (ChLinkMotorRotationSpeed)
# =============================================================================
# "프로펠러처럼 일정 속도로 계속 돈다"

arm_A = chrono.ChBody()
arm_A.SetMass(arm_mass)
arm_A.SetInertiaXX(chrono.ChVector3d(0.1, 0.1, arm_mass * arm_length**2 / 12))
arm_A.SetPos(chrono.ChVector3d(-2, arm_length / 2, 0))
sys.AddBody(arm_A)

arm_A_shape = chrono.ChVisualShapeBox(0.15, arm_length, 0.15)
arm_A_shape.SetColor(chrono.ChColor(0.8, 0.2, 0.2))   # 빨간색
arm_A.AddVisualShape(arm_A_shape)

# 모터 생성: 일정 속도
motor_speed = chrono.ChLinkMotorRotationSpeed()
motor_speed.Initialize(
    arm_A, ground,
    chrono.ChFramed(chrono.ChVector3d(-2, 0, 0), chrono.QUNIT)
)

# 속도 함수: 상수 (일정 RPM)
speed_func = chrono.ChFunctionConst(omega)
motor_speed.SetSpeedFunction(speed_func)
sys.Add(motor_speed)

print("Motor A: Constant Speed")
print(f"  Type: ChLinkMotorRotationSpeed")
print(f"  Speed: {rpm} RPM = {omega:.3f} rad/s")
print()

# 피벗 마커
marker_A = chrono.ChVisualShapeSphere(0.1)
marker_A.SetColor(chrono.ChColor(1, 1, 0))
ground.AddVisualShape(marker_A, chrono.ChFramed(chrono.ChVector3d(-2, 0, 0)))


# =============================================================================
# 모터 B: 사인파 각도 제어 (ChLinkMotorRotationAngle)
# =============================================================================
# "시계추처럼 왕복 운동한다"

arm_B = chrono.ChBody()
arm_B.SetMass(arm_mass)
arm_B.SetInertiaXX(chrono.ChVector3d(0.1, 0.1, arm_mass * arm_length**2 / 12))
arm_B.SetPos(chrono.ChVector3d(2, arm_length / 2, 0))
sys.AddBody(arm_B)

arm_B_shape = chrono.ChVisualShapeBox(0.15, arm_length, 0.15)
arm_B_shape.SetColor(chrono.ChColor(0.2, 0.2, 0.8))   # 파란색
arm_B.AddVisualShape(arm_B_shape)

# 모터 생성: 각도 제어
motor_angle = chrono.ChLinkMotorRotationAngle()
motor_angle.Initialize(
    arm_B, ground,
    chrono.ChFramed(chrono.ChVector3d(2, 0, 0), chrono.QUNIT)
)

# 각도 함수: 사인파 (진폭 45°, 주기 2초)
angle_amp = math.radians(45)    # 45° 진폭
angle_freq = math.pi            # π rad/s → 주기 2초
angle_func = chrono.ChFunctionSine(angle_amp, angle_freq / (2 * math.pi))
motor_angle.SetAngleFunction(angle_func)
sys.Add(motor_angle)

print("Motor B: Sinusoidal Angle")
print(f"  Type: ChLinkMotorRotationAngle")
print(f"  Amplitude: 45 deg, Frequency: {angle_freq:.3f} rad/s (period 2s)")
print()

# 피벗 마커
marker_B = chrono.ChVisualShapeSphere(0.1)
marker_B.SetColor(chrono.ChColor(1, 1, 0))
ground.AddVisualShape(marker_B, chrono.ChFramed(chrono.ChVector3d(2, 0, 0)))


# 지지대 기둥 (각 모터 위치에 수직 지지대)
for x_pos in [-2, 2]:
    pillar = chrono.ChVisualShapeBox(0.2, 0.6, 0.2)
    pillar.SetColor(chrono.ChColor(0.4, 0.4, 0.4))
    ground.AddVisualShape(
        pillar,
        chrono.ChFramed(chrono.ChVector3d(x_pos, -0.3, 0))
    )


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
vis.SetWindowTitle("Lesson 10 - Motor-Driven Rotation")

if USE_VSG:
    vis.AddCamera(chrono.ChVector3d(0, 1, 8), chrono.ChVector3d(0, 0, 0))
    vis.Initialize()
else:
    vis.Initialize()
    vis.AddSkyBox()
    vis.AddCamera(chrono.ChVector3d(0, 1, 8), chrono.ChVector3d(0, 0, 0))
    vis.AddTypicalLights()


# =============================================================================
# 데이터 수집
# =============================================================================

time_list = []
torque_A_list = []
torque_B_list = []
angle_A_list = []
angle_B_list = []


# =============================================================================
# 시뮬레이션 루프
# =============================================================================

frame = 0
realtime_timer = chrono.ChRealtimeStepTimer()

print(f"{'time(s)':>8}  {'Angle A(deg)':>13}  {'Torque A(Nm)':>13}  "
      f"{'Angle B(deg)':>13}  {'Torque B(Nm)':>13}")
print("─" * 70)

while vis.Run():
    time = sys.GetChTime()
    if time > time_end:
        break

    vis.BeginScene()
    vis.Render()
    vis.EndScene()

    sys.DoStepDynamics(dt)
    realtime_timer.Spin(dt)

    # 모터 상태 기록
    angle_A = math.degrees(motor_speed.GetMotorAngle())
    torque_A = motor_speed.GetMotorTorque()
    angle_B = math.degrees(motor_angle.GetMotorAngle())
    torque_B = motor_angle.GetMotorTorque()

    time_list.append(time)
    angle_A_list.append(angle_A)
    torque_A_list.append(torque_A)
    angle_B_list.append(angle_B)
    torque_B_list.append(torque_B)

    if frame % 100 == 0:
        print(f"{time:8.2f}  {angle_A:13.2f}  {torque_A:13.4f}  "
              f"{angle_B:13.2f}  {torque_B:13.4f}")

    frame += 1

print("\nSimulation finished")


# =============================================================================
# 그래프 저장
# =============================================================================

time_arr = np.array(time_list)

fig, axs = plt.subplots(2, 2, figsize=(12, 8))

# Motor A: 각도 (선형 증가해야 함)
axs[0, 0].plot(time_arr, angle_A_list, color='red')
axs[0, 0].set_title("Motor A: Angle (Constant Speed)")
axs[0, 0].set_xlabel("Time (s)")
axs[0, 0].set_ylabel("Angle (deg)")
axs[0, 0].grid()

# Motor A: 토크
axs[1, 0].plot(time_arr, torque_A_list, color='red')
axs[1, 0].set_title("Motor A: Torque")
axs[1, 0].set_xlabel("Time (s)")
axs[1, 0].set_ylabel("Torque (Nm)")
axs[1, 0].grid()

# Motor B: 각도 (사인파)
axs[0, 1].plot(time_arr, angle_B_list, color='blue')
axs[0, 1].set_title("Motor B: Angle (Sinusoidal)")
axs[0, 1].set_xlabel("Time (s)")
axs[0, 1].set_ylabel("Angle (deg)")
axs[0, 1].grid()

# Motor B: 토크
axs[1, 1].plot(time_arr, torque_B_list, color='blue')
axs[1, 1].set_title("Motor B: Torque")
axs[1, 1].set_xlabel("Time (s)")
axs[1, 1].set_ylabel("Torque (Nm)")
axs[1, 1].grid()

plt.tight_layout()

output_dir = os.path.dirname(os.path.abspath(__file__))
fig_path = os.path.join(output_dir, "lesson_10_motor_plot.png")
plt.savefig(fig_path, dpi=150)
print(f"\nPlot saved: {fig_path}")

import platform
if platform.system() == 'Darwin':
    os.system(f"open '{fig_path}'")

print()
print("배운 내용:")
print("  1. ChLinkMotorRotationSpeed — 일정 속도 회전 (프로펠러, 바퀴)")
print("  2. ChLinkMotorRotationAngle — 각도 궤적 추종 (로봇팔, 서보)")
print("  3. ChFunctionConst / ChFunctionSine — 모터 입력 함수")
print("  4. GetMotorTorque() — 모터가 발휘하는 토크 확인")
print()
print("다음 단계:")
print("  → lesson_11에서 4절 링크 기구를 만듭니다")
print("  → lesson_12에서 기어와 풀리를 배웁니다")
