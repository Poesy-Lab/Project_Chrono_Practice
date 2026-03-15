"""
==========================================================
Lesson 06: 재질과 마찰 - 미끄러운 바닥 vs 거친 바닥
==========================================================
학습 목표:
  1. 서로 다른 접촉 재질(마찰/반발)을 비교하기
  2. 경사면에서 마찰 계수의 영향 관찰하기
  3. 반발 계수의 차이로 튕김 정도 비교하기
  4. 같은 물체를 다른 조건에서 실험하는 법 익히기

복습 (Lesson 01~05):
  - 시스템, 충돌, 시각화, 다양한 형태, 초기 속도

새로 배우는 것:
  - 마찰 계수(friction) 비교: 0 (얼음) vs 0.5 (일반) vs 1.0 (고무)
  - 반발 계수(restitution) 비교: 0 (찰흙) vs 0.5 (일반) vs 1.0 (슈퍼볼)
  - 경사면(ramp) 만들기: SetRot() 으로 물체 회전

실행 방법:
  conda activate chrono
  source setup_chrono_env.sh
  python lessons/lesson_06_materials.py
==========================================================
"""

import math
import pychrono as chrono
import pychrono.irrlicht as chronoirr

print("=" * 55)
print("Lesson 06: 재질과 마찰")
print("=" * 55)

# ──────────────────────────────────────────────────
# 1단계: 시스템 설정
# ──────────────────────────────────────────────────
sys = chrono.ChSystemNSC()
sys.SetGravitationalAcceleration(chrono.ChVector3d(0, -9.81, 0))
sys.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)

# ──────────────────────────────────────────────────
# 2단계: 3가지 다른 마찰 재질 만들기 (★ 핵심!)
# ──────────────────────────────────────────────────
# 마찰 계수(friction):
#   0.0 = 완전 미끄러움 (얼음 위)
#   0.5 = 보통 (나무 바닥)
#   1.0 = 매우 거침 (고무)

mat_ice = chrono.ChContactMaterialNSC()
mat_ice.SetFriction(0.0)      # 얼음: 전혀 안 멈춤
mat_ice.SetRestitution(0.3)

mat_wood = chrono.ChContactMaterialNSC()
mat_wood.SetFriction(0.5)     # 나무: 보통
mat_wood.SetRestitution(0.3)

mat_rubber = chrono.ChContactMaterialNSC()
mat_rubber.SetFriction(1.0)   # 고무: 바로 멈춤
mat_rubber.SetRestitution(0.3)

materials = [
    (mat_ice,    "얼음 (마찰=0.0)", chrono.ChColor(0.7, 0.85, 0.95)),   # 밝은 파랑
    (mat_wood,   "나무 (마찰=0.5)", chrono.ChColor(0.7, 0.55, 0.3)),    # 갈색
    (mat_rubber, "고무 (마찰=1.0)", chrono.ChColor(0.3, 0.3, 0.3)),     # 어두운 회색
]

print("\n3가지 재질:")
for mat, name, _ in materials:
    print(f"  - {name}")

# ──────────────────────────────────────────────────
# 3단계: 경사면 3개 만들기 (각각 다른 재질)
# ──────────────────────────────────────────────────
# 경사면 = 기울어진 상자
# SetRot() 으로 Z축 기준 20도 회전

ramp_angle = 20  # 도(degree)
ramp_rad = math.radians(ramp_angle)

print(f"\n경사면 각도: {ramp_angle}°")
print("  같은 각도, 다른 재질의 경사면 3개를 나란히 배치")

ramps = []
balls = []

for i, (mat, name, color) in enumerate(materials):
    z_offset = (i - 1) * 4  # z = -4, 0, 4 (나란히 배치)

    # 경사면 (기울어진 상자)
    ramp = chrono.ChBody()
    ramp.SetPos(chrono.ChVector3d(0, 1.5, z_offset))
    ramp.SetFixed(True)
    ramp.EnableCollision(True)

    # Z축 기준 회전 (경사면 만들기)
    q = chrono.ChQuaterniond()
    q.SetFromAngleZ(ramp_rad)
    ramp.SetRot(q)

    ramp.AddCollisionShape(chrono.ChCollisionShapeBox(mat, 8, 0.3, 2))
    ramp_shape = chrono.ChVisualShapeBox(8, 0.3, 2)
    ramp_shape.SetColor(color)
    ramp.AddVisualShape(ramp_shape)
    sys.AddBody(ramp)
    ramps.append(ramp)

    # 경사면 위에 구 올려놓기
    # 경사면 윗부분 위치 계산
    ball_x = -2.5 * math.cos(ramp_rad)
    ball_y = 1.5 + 2.5 * math.sin(ramp_rad) + 0.5
    ball = chrono.ChBodyEasySphere(0.3, 2000, True, True, mat)
    ball.SetPos(chrono.ChVector3d(ball_x, ball_y, z_offset))
    ball.GetVisualShape(0).SetColor(chrono.ChColor(0.9, 0.2, 0.2))
    sys.AddBody(ball)
    balls.append(ball)

    print(f"  경사면 {i+1} ({name}): z={z_offset}")

# ──────────────────────────────────────────────────
# 4단계: 반발 계수 비교 영역 (오른쪽)
# ──────────────────────────────────────────────────
# 3개의 바닥 위에 같은 높이에서 공을 떨어뜨려서 튕김 비교

print("\n반발 계수 비교:")

mat_clay = chrono.ChContactMaterialNSC()
mat_clay.SetFriction(0.5)
mat_clay.SetRestitution(0.0)   # 찰흙: 전혀 안 튕김

mat_normal = chrono.ChContactMaterialNSC()
mat_normal.SetFriction(0.5)
mat_normal.SetRestitution(0.5)  # 보통

mat_super = chrono.ChContactMaterialNSC()
mat_super.SetFriction(0.5)
mat_super.SetRestitution(0.95)  # 슈퍼볼: 거의 완전 탄성

bounce_mats = [
    (mat_clay,   "찰흙 (반발=0.0)", chrono.ChColor(0.6, 0.4, 0.3)),
    (mat_normal, "보통 (반발=0.5)", chrono.ChColor(0.5, 0.5, 0.5)),
    (mat_super,  "슈퍼볼 (반발=0.95)", chrono.ChColor(0.2, 0.8, 0.3)),
]

bounce_balls = []
for i, (mat, name, color) in enumerate(bounce_mats):
    x_offset = 8 + i * 3  # 오른쪽에 배치

    # 각각의 바닥
    pad = chrono.ChBody()
    pad.SetPos(chrono.ChVector3d(x_offset, -0.5, 0))
    pad.SetFixed(True)
    pad.EnableCollision(True)
    pad.AddCollisionShape(chrono.ChCollisionShapeBox(mat, 2, 1, 2))
    pad_shape = chrono.ChVisualShapeBox(2, 1, 2)
    pad_shape.SetColor(color)
    pad.AddVisualShape(pad_shape)
    sys.AddBody(pad)

    # 같은 높이에서 공 떨어뜨리기
    bb = chrono.ChBodyEasySphere(0.3, 2000, True, True, mat)
    bb.SetPos(chrono.ChVector3d(x_offset, 6, 0))
    bb.GetVisualShape(0).SetColor(chrono.ChColor(0.9, 0.9, 0.2))  # 노랑
    sys.AddBody(bb)
    bounce_balls.append(bb)

    print(f"  {name}: x={x_offset}")

# ──────────────────────────────────────────────────
# 5단계: 시각화
# ──────────────────────────────────────────────────
print("\n3D 시각화 초기화 중...")

vis = chronoirr.ChVisualSystemIrrlicht()
vis.AttachSystem(sys)
vis.SetWindowSize(1280, 720)
# 참고: macOS Retina에서는 렌더링이 창의 일부만 채울 수 있습니다.
vis.SetWindowTitle('Lesson 06: Friction & Restitution')
vis.Initialize()
vis.AddSkyBox()
vis.AddCamera(chrono.ChVector3d(5, 8, 20), chrono.ChVector3d(5, 1, 0))
vis.AddTypicalLights()

print("시각화 준비 완료!")
print("\n" + "─" * 55)
print("  [왼쪽] 경사면 3개: 마찰 계수 비교")
print("    → 얼음(파랑)은 잘 미끄러지고, 고무(회색)는 안 미끄러짐")
print("  [오른쪽] 바닥 3개: 반발 계수 비교")
print("    → 찰흙은 안 튕기고, 슈퍼볼은 높이 튕김")
print("  마우스로 카메라를 돌려서 양쪽을 관찰하세요!")
print("  ESC → 종료")
print("─" * 55)

# ──────────────────────────────────────────────────
# 6단계: 시뮬레이션 루프
# ──────────────────────────────────────────────────
step_size = 0.005
realtime_timer = chrono.ChRealtimeStepTimer()

while vis.Run():
    vis.BeginScene()
    vis.Render()
    vis.EndScene()
    sys.DoStepDynamics(step_size)
    realtime_timer.Spin(step_size)

# ──────────────────────────────────────────────────
# 7단계: 결과
# ──────────────────────────────────────────────────
print(f"\n시뮬레이션 종료! (총 {sys.GetChTime():.2f}초)")

print("\n경사면 실험 결과 (마찰 비교):")
for i, (_, name, _) in enumerate(materials):
    b = balls[i]
    print(f"  {name}: 최종 위치=({b.GetPos().x:.2f}, {b.GetPos().y:.2f})")

print("\n튕김 실험 결과 (반발 비교):")
for i, (_, name, _) in enumerate(bounce_mats):
    b = bounce_balls[i]
    print(f"  {name}: 최종 높이={b.GetPos().y:.3f} m")

print(f"""
핵심 정리:
  1. 마찰 계수 ↑ → 물체가 경사면에서 덜 미끄러짐
  2. 반발 계수 ↑ → 물체가 더 높이 튕김
  3. 같은 형태/질량이라도 재질에 따라 움직임이 완전히 달라짐
  4. SetRot(quaternion) 으로 물체를 기울일 수 있음

다음 단계:
  → lesson_07에서 회전 조인트(경첩)를 배웁니다
""")
