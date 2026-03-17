"""
lesson_09_spring_damper.py

설명:
- 스프링-댐퍼 시스템의 자유진동과 강제진동을 비교하는 시뮬레이션
- Body1 (빨간색): Chrono 내장 스프링-댐퍼 모델 → 자유진동 (외력 없음)
- Body2 (파란색): 커스텀 ForceFunctor → 강제진동 (사인파 외력 적용)
- 해석해(이론값)와의 오차를 RMSE로 정량 비교
- 중력 없음 (순수 스프링-댐퍼 동역학만 관찰)

핵심 개념:
- ChLinkTSDA: Chrono의 1차원 스프링-댐퍼 요소
- ForceFunctor: 사용자 정의 힘 함수 (스프링력 + 감쇠력 + 외력)
- 고유진동수(wn), 감쇠비(zeta), 감쇠진동수(wd)

실행:
    cd ~/Documents/Pneuma/Project_Chrono_Practice
    conda activate chrono
    source setup_chrono_env.sh
    python lessons/phase2/lesson_09_spring_damper.py
"""

import os
import matplotlib
matplotlib.use('Agg')           # Irrlicht 창과의 충돌 방지를 위해 비대화형 백엔드 사용

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
# 시뮬레이션 파라미터 정의
# 여기서 파라미터 값 조정하면서 시뮬레이션 결과가 어떻게 달라지는지 관찰
# =============================================================================

mass = 1.0          # 질량 [kg]

# Body1 파라미터 (내장 스프링-댐퍼)
k1 = 50             # 스프링 강성 [N/m]
c1 = 1              # 감쇠 계수 [Ns/m]

# Body2 파라미터 (커스텀 ForceFunctor)
k2 = 50             # 스프링 강성 [N/m]
c2 = 1              # 감쇠 계수 [Ns/m]

rest_length = 1.5   # 스프링 자연 길이 [m]

# 외력 파라미터 (Body2에만 적용)
F_amp = 10          # 외력 진폭 [N]
F_freq = 10         # 외력 주파수 [rad/s]

dt = 0.001          # 시간 스텝 [s]
time_end = 10       # 시뮬레이션 종료 시간 [s]


# =============================================================================
# 해석 모델 (이론값 계산용)
# =============================================================================

# Body1: 고유진동수, 감쇠비, 감쇠진동수
wn1 = np.sqrt(k1 / mass)                   # 고유진동수 [rad/s]
zeta1 = c1 / (2 * np.sqrt(k1 * mass))      # 감쇠비 [-]
wd1 = wn1 * np.sqrt(1 - zeta1**2)          # 감쇠진동수 [rad/s]

# Body2: 동일한 스프링/댐퍼 파라미터이므로 이론값도 동일
wn2 = np.sqrt(k2 / mass)
zeta2 = c2 / (2 * np.sqrt(k2 * mass))
wd2 = wn2 * np.sqrt(1 - zeta2**2)


# =============================================================================
# 감쇠 영역 판별 함수
# =============================================================================

def damping_regime(zeta):
    """감쇠비에 따른 진동 영역 분류"""
    if zeta < 1:
        return "Under-damped"       # 부족감쇠: 진동하며 감쇠
    elif np.isclose(zeta, 1):
        return "Critical"           # 임계감쇠: 가장 빠르게 평형으로 복귀
    else:
        return "Over-damped"        # 과감쇠: 진동 없이 느리게 복귀


# =============================================================================
# 파라미터 요약 출력
# =============================================================================

print("\n============================================================")
print("        Chrono Spring-Damper Validation Test")
print("============================================================")

print(f"\nMass = {mass} kg")

print("\n------------------------------------------------------------")
print(f"{'Body':<8}{'k(N/m)':<10}{'c(Ns/m)':<10}{'wn(rad/s)':<12}{'zeta':<10}{'Regime'}")
print("------------------------------------------------------------")

print(f"{'Body1':<8}{k1:<10}{c1:<10}{wn1:<12.3f}{zeta1:<10.3f}{damping_regime(zeta1)}")
print(f"{'Body2':<8}{k2:<10}{c2:<10}{wn2:<12.3f}{zeta2:<10.3f}{damping_regime(zeta2)}")

print("------------------------------------------------------------")

print("\nExternal Force (Body2 only)")
print("-----------------------")
print(f"Amplitude  = {F_amp} N")
print(f"Frequency  = {F_freq} rad/s")

print("============================================================\n")


# =============================================================================
# 커스텀 힘 모델 (Body2용)
# - 스프링력 + 감쇠력 + 사인파 외력을 하나의 ForceFunctor로 정의
# =============================================================================

class MySpringForce(chrono.ForceFunctor):

    def evaluate(self, time, rest_length, length, vel, link):
        Fs = -k2 * (length - rest_length)       # 스프링 복원력
        Fd = -c2 * vel                           # 감쇠력
        Fext = F_amp * np.sin(F_freq * time)     # 외력 (사인파)

        return Fs + Fd + Fext


# =============================================================================
# Chrono 시스템 생성
# - 중력 제거: 순수 스프링-댐퍼 응답만 관찰
# =============================================================================

sys = chrono.ChSystemNSC()
sys.SetGravitationalAcceleration(chrono.ChVector3d(0, 0, 0))


# =============================================================================
# 지면 (고정 기준점)
# - 두 스프링의 상단 고정점 역할
# =============================================================================

ground = chrono.ChBody()
ground.SetFixed(True)
sys.AddBody(ground)

# 고정점 위치를 시각적으로 표시 (작은 구)
ground.AddVisualShape(
    chrono.ChVisualShapeSphere(0.1),
    chrono.ChFramed(chrono.ChVector3d(-1, 0, 0))    # Body1 고정점
)

ground.AddVisualShape(
    chrono.ChVisualShapeSphere(0.1),
    chrono.ChFramed(chrono.ChVector3d(1, 0, 0))     # Body2 고정점
)


# =============================================================================
# 진동 물체 생성
# - 두 물체 모두 고정점 아래 rest_length + 1.5m 위치에서 시작 (초기 변위)
# =============================================================================

# Body1: 빨간색 — 내장 스프링-댐퍼 사용 (자유진동)
body_1 = chrono.ChBody()
body_1.SetMass(mass)
body_1.SetInertiaXX(chrono.ChVector3d(1, 1, 1))
body_1.SetPos(chrono.ChVector3d(-1, -3, 0))     # 초기 위치 (평형점 아래)
sys.AddBody(body_1)

box1 = chrono.ChVisualShapeBox(0.4, 0.4, 0.4)
box1.SetColor(chrono.ChColor(0.7, 0, 0))        # 빨간색
body_1.AddVisualShape(box1)


# Body2: 파란색 — 커스텀 ForceFunctor 사용 (강제진동)
body_2 = chrono.ChBody()
body_2.SetMass(mass)
body_2.SetInertiaXX(chrono.ChVector3d(1, 1, 1))
body_2.SetPos(chrono.ChVector3d(1, -3, 0))      # 초기 위치 (평형점 아래)
sys.AddBody(body_2)

box2 = chrono.ChVisualShapeBox(0.4, 0.4, 0.4)
box2.SetColor(chrono.ChColor(0, 0, 0.7))        # 파란색
body_2.AddVisualShape(box2)


# =============================================================================
# 스프링-댐퍼 링크 (ChLinkTSDA)
# - TSDA = Translational Spring-Damper Actuator
# - Initialize(body, ground, local좌표사용, body측연결점, ground측연결점)
# =============================================================================

# Spring 1: 내장 스프링-댐퍼 (Body1 → Ground)
spring_1 = chrono.ChLinkTSDA()
spring_1.Initialize(body_1, ground, True,
                    chrono.ChVector3d(0, 0, 0),      # body_1의 로컬 연결점
                    chrono.ChVector3d(-1, 0, 0))      # ground의 로컬 연결점

spring_1.SetRestLength(rest_length)
spring_1.SetSpringCoefficient(k1)
spring_1.SetDampingCoefficient(c1)

# 스프링 코일 시각화
# - VSG / Irrlicht(Windows/Linux): ChVisualShapeSpring 정상 동작
# - Irrlicht(macOS): 선 렌더링 안 됨 → 구 마커 체인으로 보완
spring_1.AddVisualShape(chrono.ChVisualShapeSpring(0.1, 80, 15))

sys.AddLink(spring_1)


# Spring 2: 커스텀 ForceFunctor (Body2 → Ground)
force_functor = MySpringForce()

spring_2 = chrono.ChLinkTSDA()
spring_2.Initialize(body_2, ground, True,
                    chrono.ChVector3d(0, 0, 0),
                    chrono.ChVector3d(1, 0, 0))

spring_2.SetRestLength(rest_length)
spring_2.RegisterForceFunctor(force_functor)

spring_2.AddVisualShape(chrono.ChVisualShapeSpring(0.1, 80, 15))

sys.AddLink(spring_2)


# =============================================================================
# 스프링 시각화 보완 (macOS Irrlicht 전용): 구 마커 체인
# - macOS Irrlicht OpenGL에서만 선 렌더링이 안 됨
# - macOS + Irrlicht 조합일 때만 구 마커 생성
# =============================================================================

import platform
IS_MACOS_IRRLICHT = (platform.system() == 'Darwin' and not USE_VSG)

NUM_MARKERS = 5
marker_radius = 0.06

spring1_markers = []
spring2_markers = []

if IS_MACOS_IRRLICHT:
    for i in range(NUM_MARKERS):
        m1 = chrono.ChBody()
        m1.SetFixed(True)
        m1.EnableCollision(False)
        s1 = chrono.ChVisualShapeSphere(marker_radius)
        s1.SetColor(chrono.ChColor(0.9, 0.3, 0.3))
        m1.AddVisualShape(s1)
        sys.AddBody(m1)
        spring1_markers.append(m1)

        m2 = chrono.ChBody()
        m2.SetFixed(True)
        m2.EnableCollision(False)
        s2 = chrono.ChVisualShapeSphere(marker_radius)
        s2.SetColor(chrono.ChColor(0.3, 0.3, 0.9))
        m2.AddVisualShape(s2)
        sys.AddBody(m2)
        spring2_markers.append(m2)


# =============================================================================
# Irrlicht 3D 시각화
# - macOS: 창 크기 1280x720 이하, ChRealtimeStepTimer 필수
# =============================================================================

if USE_VSG:
    vis = chronovsg.ChVisualSystemVSG()
    vis.SetCameraVertical(chrono.CameraVerticalDir_Y)
else:
    vis = chronoirr.ChVisualSystemIrrlicht()

vis.AttachSystem(sys)
vis.SetWindowSize(1024, 720)
vis.SetWindowTitle("Lesson 09 - Spring-Damper Comparison")

if USE_VSG:
    vis.AddCamera(chrono.ChVector3d(0, 0, 6))
    vis.Initialize()
else:
    vis.Initialize()
    vis.AddSkyBox()
    vis.AddCamera(chrono.ChVector3d(0, 0, 6))
    vis.AddTypicalLights()


# =============================================================================
# 데이터 저장용 리스트
# =============================================================================

time_list = []
disp1 = []      # Body1 시뮬레이션 변위
disp2 = []      # Body2 시뮬레이션 변위
theory = []     # 해석해 (Body1 이론값)


# =============================================================================
# 시뮬레이션 루프
# =============================================================================

frame = 0

# 평형점: 스프링 자연길이만큼 아래 (중력 없으므로 y = -rest_length)
y_eq = -rest_length

# 초기 변위: 현재 위치 - 평형점
x0 = body_1.GetPos().y - y_eq

# macOS 실시간 동기화 타이머
realtime_timer = chrono.ChRealtimeStepTimer()

while vis.Run():

    time = sys.GetChTime()

    # 종료 조건
    if time > time_end:
        print("\nSimulation finished")
        if not USE_VSG:
            vis.GetDevice().closeDevice()
        break

    vis.BeginScene()
    vis.Render()
    vis.EndScene()

    sys.DoStepDynamics(dt)
    realtime_timer.Spin(dt)     # macOS 실시간 속도 동기화 (필수)

    # 스프링 마커 위치 갱신 (macOS Irrlicht 전용)
    if IS_MACOS_IRRLICHT:
        p1_top = chrono.ChVector3d(-1, 0, 0)
        p1_bot = body_1.GetPos()
        p2_top = chrono.ChVector3d(1, 0, 0)
        p2_bot = body_2.GetPos()

        for i in range(NUM_MARKERS):
            t_ratio = (i + 1) / (NUM_MARKERS + 1)
            spring1_markers[i].SetPos(chrono.ChVector3d(
                p1_top.x + t_ratio * (p1_bot.x - p1_top.x),
                p1_top.y + t_ratio * (p1_bot.y - p1_top.y),
                p1_top.z + t_ratio * (p1_bot.z - p1_top.z)
            ))
            spring2_markers[i].SetPos(chrono.ChVector3d(
                p2_top.x + t_ratio * (p2_bot.x - p2_top.x),
                p2_top.y + t_ratio * (p2_bot.y - p2_top.y),
                p2_top.z + t_ratio * (p2_bot.z - p2_top.z)
            ))

    # 시뮬레이션 위치 기록
    y1 = body_1.GetPos().y
    y2 = body_2.GetPos().y

    # 해석해: 부족감쇠 자유진동 x(t) = x0 * e^(-ζωn*t) * cos(ωd*t)
    x_theory = x0 * np.exp(-zeta1 * wn1 * time) * np.cos(wd1 * time)
    y_theory = x_theory + y_eq

    time_list.append(time)
    disp1.append(y1)
    disp2.append(y2)
    theory.append(y_theory)

    # 50프레임마다 상태 출력
    if frame % 50 == 0:
        print(
            f"t={time:.3f}s  "
            f"L1:{spring_1.GetLength():.3f}  "
            f"F1:{spring_1.GetForce():.3f}  |  "
            f"y1:{y1:.3f}  y2:{y2:.3f}"
        )

    frame += 1


# =============================================================================
# 결과 분석 — RMSE 계산
# =============================================================================

time_arr = np.array(time_list)
disp1 = np.array(disp1)
disp2 = np.array(disp2)
theory = np.array(theory)

# Body1은 이론해와 일치해야 함 (내장 스프링, 외력 없음)
error1 = disp1 - theory
# Body2는 외력이 있으므로 이론해와 차이 발생 (예상된 차이)
error2 = disp2 - theory

rmse1 = np.sqrt(np.mean(error1**2))
rmse2 = np.sqrt(np.mean(error2**2))

print(f"\nRMSE Body1 (자유진동 vs 이론해) = {rmse1:.6f}")
print(f"RMSE Body2 (강제진동 vs 이론해) = {rmse2:.6f}")
print("→ Body1 RMSE가 ~0이면 Chrono 내장 스프링이 이론과 일치함을 의미")
print("→ Body2 RMSE가 크면 외력에 의한 강제진동 효과가 나타남을 의미")


# =============================================================================
# 그래프 1: Body1 vs Body2 변위 비교
# =============================================================================

plt.figure()

plt.plot(time_arr, disp1, color='red', label="Body1 (Free Vibration)")
plt.plot(time_arr, disp2, color='blue', linestyle='--', label="Body2 (Forced Vibration)")

plt.xlabel("Time (s)")
plt.ylabel("Displacement (m)")
plt.title("Body Displacement Comparison")

plt.legend()
plt.grid()

# 그래프 1 저장
output_dir = os.path.dirname(os.path.abspath(__file__))
fig1_path = os.path.join(output_dir, "lesson_08_plot1_comparison.png")
plt.savefig(fig1_path, dpi=150)
print(f"\nPlot 1 saved: {fig1_path}")


# =============================================================================
# 그래프 2: 2x2 상세 분석
# - 상단: 시뮬레이션 vs 이론해
# - 하단: 오차 (시뮬레이션 - 이론해)
# =============================================================================

fig, axs = plt.subplots(2, 2, figsize=(12, 8))

# RMSE 텍스트 표시
axs[1, 0].text(0.7, 0.9, f"RMSE={rmse1:.4f}", color='red', transform=axs[1, 0].transAxes)
axs[1, 1].text(0.7, 0.9, f"RMSE={rmse2:.4f}", color='blue', transform=axs[1, 1].transAxes)

# 오차 그래프 스케일 통일
max_error = max(np.max(np.abs(error1)), np.max(np.abs(error2)))

# 오차 = 0 기준선
axs[1, 0].axhline(0, color='gray', linewidth=0.9)
axs[1, 1].axhline(0, color='gray', linewidth=0.9)

# --- Body1 vs Theory ---
axs[0, 0].plot(time_arr, disp1, color='red', label="Body1 Simulation")
axs[0, 0].plot(time_arr, theory, color='black', linestyle='--', label="Theory")
axs[0, 0].set_title("Body1 (Free Vibration) vs Theory")
axs[0, 0].set_xlabel("Time (s)")
axs[0, 0].set_ylabel("Displacement (m)")
axs[0, 0].legend()
axs[0, 0].grid()

# --- Body2 vs Theory ---
axs[0, 1].plot(time_arr, disp2, color='blue', label="Body2 Simulation")
axs[0, 1].plot(time_arr, theory, color='black', linestyle='--', label="Theory")
axs[0, 1].set_title("Body2 (Forced Vibration) vs Theory")
axs[0, 1].set_xlabel("Time (s)")
axs[0, 1].set_ylabel("Displacement (m)")
axs[0, 1].legend()
axs[0, 1].grid()

# --- Body1 Error ---
axs[1, 0].plot(time_arr, error1, color='black')
axs[1, 0].set_title("Body1 Error (Sim - Theory)")
axs[1, 0].set_xlabel("Time (s)")
axs[1, 0].set_ylabel("Error (m)")
axs[1, 0].set_ylim(-max_error, max_error)
axs[1, 0].grid()

# --- Body2 Error ---
axs[1, 1].plot(time_arr, error2, color='black')
axs[1, 1].set_title("Body2 Error (Sim - Theory)")
axs[1, 1].set_xlabel("Time (s)")
axs[1, 1].set_ylabel("Error (m)")
axs[1, 1].set_ylim(-max_error, max_error)
axs[1, 1].grid()

plt.tight_layout()

# 그래프 2 저장
fig2_path = os.path.join(output_dir, "lesson_08_plot2_analysis.png")
plt.savefig(fig2_path, dpi=150)
print(f"Plot 2 saved: {fig2_path}")

# 저장된 그래프 자동 열기 (macOS)
os.system(f"open '{fig1_path}'")
os.system(f"open '{fig2_path}'")
