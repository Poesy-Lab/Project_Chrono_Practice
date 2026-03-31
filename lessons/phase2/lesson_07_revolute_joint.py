"""
==========================================================
Lesson 07: 회전 조인트 (Revolute Joint) - 문의 경첩
==========================================================
학습 목표:
  1. ChLinkRevolute 로 두 물체를 회전축으로 연결하는 법
  2. 조인트 프레임(위치, 방향) 설정하기
  3. 중력에 의한 자유 회전 운동 관찰하기
  4. 조인트 반력(reaction force) 읽는 법

복습 (Phase 1):
  - 시스템, 물체, 시각화, 충돌, 재질

새로 배우는 것:
  - ChLinkRevolute: 한 축으로만 회전 가능한 구속 (문 경첩)
  - ChFramed: 조인트의 위치와 방향 정의
  - 조인트 반력 조회: GetReaction2().force

실행 방법:
  conda activate chrono
  source setup_chrono_env.sh
  python lessons/phase2/lesson_07_revolute_joint.py
==========================================================
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


# ──────────────────────────────────────────────────
# 1단계: 물리 시스템 생성
# ──────────────────────────────────────────────────

sys = chrono.ChSystemNSC()
sys.SetGravitationalAcceleration(chrono.ChVector3d(0, -9.81, 0))

print("Lesson 07: 회전 조인트 (Revolute Joint)")
print("=" * 50)


# ──────────────────────────────────────────────────
# 2단계: 고정 기둥 (벽 역할)
# ──────────────────────────────────────────────────
# 조인트의 한쪽은 고정 물체에 연결됩니다 (문틀 역할).

pillar = chrono.ChBody()
pillar.SetFixed(True)
sys.AddBody(pillar)

# 시각화: 기둥 (가느다란 수직 박스)
pillar_shape = chrono.ChVisualShapeBox(0.2, 2.0, 0.2)
pillar_shape.SetColor(chrono.ChColor(0.5, 0.5, 0.5))
pillar.AddVisualShape(pillar_shape)


# ──────────────────────────────────────────────────
# 3단계: 회전하는 막대 (문짝 역할)
# ──────────────────────────────────────────────────
# 막대의 한쪽 끝이 기둥에 경첩으로 연결됩니다.

bar_length = 2.0
bar = chrono.ChBody()
bar.SetMass(2.0)
bar.SetInertiaXX(chrono.ChVector3d(0.1, 0.1, 2.0))  # z축 회전에 적합한 관성
# 막대 중심을 오른쪽으로 배치 (왼쪽 끝이 기둥 근처)
bar.SetPos(chrono.ChVector3d(bar_length / 2, 0, 0))
sys.AddBody(bar)

# 시각화: 수평 막대
bar_shape = chrono.ChVisualShapeBox(bar_length, 0.15, 0.15)
bar_shape.SetColor(chrono.ChColor(0.8, 0.2, 0.2))
bar.AddVisualShape(bar_shape)


# ──────────────────────────────────────────────────
# 4단계: 회전 조인트 (Revolute Joint) 연결
# ──────────────────────────────────────────────────
# ChLinkRevolute: 한 축(여기서는 Z축)으로만 회전을 허용
#
# 조인트 프레임:
#   - 위치: 막대의 왼쪽 끝 = 기둥 위치 (0, 0, 0)
#   - 방향: Z축이 회전축 (기본값)

joint = chrono.ChLinkRevolute()

# 조인트 위치와 방향을 정의하는 프레임
joint_frame = chrono.ChFramed(
    chrono.ChVector3d(0, 0, 0),    # 위치: 원점 (기둥 위치)
    chrono.QUNIT                   # 방향: 기본값 (Z축 회전)
)

# 두 물체를 조인트로 연결
# Initialize(body_1, body_2, frame): frame은 월드 좌표계 기준
joint.Initialize(pillar, bar, joint_frame)
sys.Add(joint)

print(f"  기둥: 고정, 원점에 위치")
print(f"  막대: 질량 {bar.GetMass()} kg, 길이 {bar_length} m")
print(f"  조인트 위치: (0, 0, 0) — Z축 회전")
print()


# ──────────────────────────────────────────────────
# 5단계: 두 번째 조인트 체인 (2중 진자 맛보기)
# ──────────────────────────────────────────────────
# 첫 번째 막대 끝에 두 번째 막대를 연결합니다.

bar2 = chrono.ChBody()
bar2.SetMass(1.0)
bar2.SetInertiaXX(chrono.ChVector3d(0.05, 0.05, 0.5))
bar2.SetPos(chrono.ChVector3d(bar_length + bar_length / 2, 0, 0))
sys.AddBody(bar2)

bar2_shape = chrono.ChVisualShapeBox(bar_length, 0.12, 0.12)
bar2_shape.SetColor(chrono.ChColor(0.2, 0.2, 0.8))
bar2.AddVisualShape(bar2_shape)

# 두 번째 조인트: bar의 오른쪽 끝 ↔ bar2의 왼쪽 끝
joint2 = chrono.ChLinkRevolute()
joint2_frame = chrono.ChFramed(
    chrono.ChVector3d(bar_length, 0, 0),   # bar의 오른쪽 끝
    chrono.QUNIT
)
joint2.Initialize(bar, bar2, joint2_frame)
sys.Add(joint2)

print(f"  막대2: 질량 {bar2.GetMass()} kg, 길이 {bar_length} m")
print(f"  조인트2 위치: ({bar_length}, 0, 0) — bar 끝과 bar2 시작점 연결")
print()


# ──────────────────────────────────────────────────
# 6단계: 조인트 위치 마커 (시각적 표시)
# ──────────────────────────────────────────────────

# 조인트1 마커: pillar(고정)에 부착 — 원점에 고정이므로 OK
marker1 = chrono.ChVisualShapeSphere(0.12)
marker1.SetColor(chrono.ChColor(0.0, 0.8, 0.0))
pillar.AddVisualShape(marker1, chrono.ChFramed(chrono.ChVector3d(0, 0, 0)))

# 조인트2 마커: bar(움직이는 물체)의 오른쪽 끝에 부착 — 막대와 함께 이동
marker2 = chrono.ChVisualShapeSphere(0.12)
marker2.SetColor(chrono.ChColor(0.0, 0.8, 0.0))
bar.AddVisualShape(marker2, chrono.ChFramed(chrono.ChVector3d(bar_length / 2, 0, 0)))


# ──────────────────────────────────────────────────
# 7단계: 시각화 설정
# ──────────────────────────────────────────────────

if USE_VSG:
    vis = chronovsg.ChVisualSystemVSG()
    vis.SetCameraVertical(chrono.CameraVerticalDir_Y)
else:
    vis = chronoirr.ChVisualSystemIrrlicht()

vis.AttachSystem(sys)
vis.SetWindowSize(1024, 720)
vis.SetWindowTitle("Lesson 07 - Revolute Joint (Double Pendulum)")

if USE_VSG:
    vis.AddCamera(chrono.ChVector3d(2, 0, 8), chrono.ChVector3d(2, -1, 0))
    vis.Initialize()
else:
    vis.Initialize()
    vis.AddSkyBox()
    vis.AddCamera(chrono.ChVector3d(2, 0, 8), chrono.ChVector3d(2, -1, 0))
    vis.AddTypicalLights()


# ──────────────────────────────────────────────────
# 8단계: 시뮬레이션 루프
# ──────────────────────────────────────────────────

dt = 0.005
frame_count = 0
realtime_timer = chrono.ChRealtimeStepTimer()

print(f"{'시간(s)':>8}  {'막대1 각도(°)':>14}  {'막대2 위치 y(m)':>16}  {'조인트1 반력(N)':>16}")
print("─" * 60)

while vis.Run():
    time = sys.GetChTime()
    if time > 10.0:
        break

    vis.BeginScene()
    vis.Render()
    vis.EndScene()

    sys.DoStepDynamics(dt)
    realtime_timer.Spin(dt)

    # 100프레임마다 상태 출력
    if frame_count % 100 == 0:
        # 막대1의 대략적 각도 (y좌표로 추정)
        bar_center = bar.GetPos()
        angle_rad = math.atan2(-bar_center.y, bar_center.x)
        angle_deg = math.degrees(angle_rad)

        # 조인트 반력
        reaction = joint.GetReaction2().force
        react_mag = math.sqrt(reaction.x**2 + reaction.y**2 + reaction.z**2)

        print(f"{time:8.2f}  {angle_deg:14.2f}  {bar2.GetPos().y:16.4f}  {react_mag:16.4f}")

    frame_count += 1


# ──────────────────────────────────────────────────
# 9단계: 결과 요약
# ──────────────────────────────────────────────────

print(f"\n{'=' * 50}")
print("시뮬레이션 완료!")
print()
print("배운 내용:")
print("  1. ChLinkRevolute — 한 축 회전만 허용하는 경첩 조인트")
print("  2. ChFramed — 조인트 위치/방향을 월드 좌표로 지정")
print("  3. 여러 조인트를 체인으로 연결하면 복잡한 운동 생성")
print("  4. GetReaction2() — 조인트에 걸리는 반력 확인")
print()
print("다음 단계:")
print("  → lesson_08에서 진자 운동을 이론값과 비교합니다")
print("  → lesson_10에서 조인트에 모터를 달아 자동 회전합니다")
