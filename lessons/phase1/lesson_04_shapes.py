"""
==========================================================
Lesson 04: 다양한 형태의 물체 - 상자, 구, 실린더
==========================================================
학습 목표:
  1. ChBodyEasySphere / Box / Cylinder 간편 생성법 배우기
  2. 다양한 형태의 물체를 한 장면에 배치하기
  3. 밀도(density)로 질량을 자동 계산하는 법 이해하기
  4. 물체별 색상과 시각적 형태 설정하기

복습 (Lesson 01~03):
  - 시스템, 충돌, 접촉 재질, 3D 시각화

새로 배우는 것:
  - ChBodyEasySphere(반지름, 밀도, 시각화, 충돌, 재질) : 구 간편 생성
  - ChBodyEasyBox(x, y, z, 밀도, 시각화, 충돌, 재질) : 상자 간편 생성
  - ChBodyEasyCylinder(축방향, 반지름, 높이, 밀도, 시각화, 충돌, 재질) : 실린더 간편 생성
  - 밀도(density) : kg/m³ 단위, 물=1000, 철=7800, 나무=600

실행 방법:
  conda activate chrono
  source setup_chrono_env.sh
  python lessons/phase1/lesson_04_shapes.py
==========================================================
"""

import pychrono as chrono
import pychrono.irrlicht as chronoirr

print("=" * 55)
print("Lesson 04: 다양한 형태의 물체")
print("=" * 55)

# ──────────────────────────────────────────────────
# 1단계: 시스템 설정
# ──────────────────────────────────────────────────
sys = chrono.ChSystemNSC()
sys.SetGravitationalAcceleration(chrono.ChVector3d(0, -9.81, 0))
sys.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)

material = chrono.ChContactMaterialNSC()
material.SetFriction(0.5)
material.SetRestitution(0.3)

# ──────────────────────────────────────────────────
# 2단계: 바닥
# ──────────────────────────────────────────────────
floor = chrono.ChBody()
floor.SetPos(chrono.ChVector3d(0, -1, 0))
floor.SetFixed(True)
floor.EnableCollision(True)
floor.AddCollisionShape(chrono.ChCollisionShapeBox(material, 30, 2, 30))
floor_shape = chrono.ChVisualShapeBox(30, 2, 30)
floor_shape.SetColor(chrono.ChColor(0.5, 0.55, 0.5))
floor.AddVisualShape(floor_shape)
sys.AddBody(floor)

# ──────────────────────────────────────────────────
# 3단계: 다양한 물체 만들기 (★ 이번 레슨의 핵심!)
# ──────────────────────────────────────────────────
# ChBodyEasy~ 시리즈는 한 줄로 물체를 만들어줍니다:
#   - 형태(충돌+시각) 자동 생성
#   - 밀도로 질량/관성 자동 계산
#   - 훨씬 편리! (Lesson 02~03에서 했던 수동 설정을 자동으로)

# ── 구(Sphere) ──
# ChBodyEasySphere(반지름, 밀도, 시각화, 충돌, 재질)
#   밀도 7800 = 철(steel)
sphere = chrono.ChBodyEasySphere(0.4, 7800, True, True, material)
sphere.SetPos(chrono.ChVector3d(-3, 6, 0))
sphere.GetVisualShape(0).SetColor(chrono.ChColor(0.9, 0.2, 0.2))  # 빨강
sys.AddBody(sphere)

print("\n구(Sphere) 생성:")
print("  반지름: 0.4 m, 밀도: 7800 kg/m³ (철)")
print(f"  자동 계산된 질량: {sphere.GetMass():.2f} kg")

# ── 상자(Box) ──
# ChBodyEasyBox(x크기, y크기, z크기, 밀도, 시각화, 충돌, 재질)
#   밀도 600 = 나무(wood)
box = chrono.ChBodyEasyBox(0.8, 0.8, 0.8, 600, True, True, material)
box.SetPos(chrono.ChVector3d(0, 5, 0))
box.GetVisualShape(0).SetColor(chrono.ChColor(0.2, 0.6, 0.9))  # 파랑
sys.AddBody(box)

print("\n상자(Box) 생성:")
print("  크기: 0.8 x 0.8 x 0.8 m, 밀도: 600 kg/m³ (나무)")
print(f"  자동 계산된 질량: {box.GetMass():.2f} kg")

# ── 실린더(Cylinder) ──
# ChBodyEasyCylinder(형태, 반지름, 높이, 밀도, 충돌여부, 재질)
#   ChAxis_Y = Y축 방향으로 세운 실린더
#   밀도 2700 = 알루미늄(aluminum)
cylinder = chrono.ChBodyEasyCylinder(
    chrono.ChAxis_Y,    # 실린더 축 방향
    0.3,                # 반지름
    1.0,                # 높이
    2700,               # 밀도 (알루미늄)
    True,               # 시각화 활성화
    True,               # 충돌 활성화
    material            # 접촉 재질
)
cylinder.SetPos(chrono.ChVector3d(3, 7, 0))
cylinder.GetVisualShape(0).SetColor(chrono.ChColor(0.9, 0.8, 0.1))  # 노랑
sys.AddBody(cylinder)

print("\n실린더(Cylinder) 생성:")
print("  반지름: 0.3 m, 높이: 1.0 m, 밀도: 2700 kg/m³ (알루미늄)")
print(f"  자동 계산된 질량: {cylinder.GetMass():.2f} kg")

# ── 추가 물체들 (높은 곳에서 떨어뜨리기) ──
# 작은 구 여러 개
print("\n작은 구 5개 추가 생성 (높이 10~14m)")
small_balls = []
for i in range(5):
    sb = chrono.ChBodyEasySphere(0.2, 3000, True, True, material)
    sb.SetPos(chrono.ChVector3d(-2 + i, 10 + i, 0.5 * i))
    sb.GetVisualShape(0).SetColor(
        chrono.ChColor(0.6 + i * 0.08, 0.3, 0.8 - i * 0.1)
    )
    sys.AddBody(sb)
    small_balls.append(sb)

print(f"\n총 물체 수: {len(sys.GetBodies())} (바닥 포함)")

# ──────────────────────────────────────────────────
# 4단계: 시각화
# ──────────────────────────────────────────────────
print("\n3D 시각화 초기화 중...")

vis = chronoirr.ChVisualSystemIrrlicht()
vis.AttachSystem(sys)
vis.SetWindowSize(1280, 720)
# 참고: macOS Retina에서는 렌더링이 창의 일부만 채울 수 있습니다.
#   이는 Irrlicht가 HiDPI를 지원하지 않는 알려진 제한사항입니다.
vis.SetWindowTitle('Lesson 04: Various Shapes')
vis.Initialize()
vis.AddSkyBox()
vis.AddCamera(chrono.ChVector3d(0, 6, 18), chrono.ChVector3d(0, 2, 0))
vis.AddTypicalLights()

print("시각화 준비 완료!")
print("\n" + "─" * 55)
print("  빨간 구(철), 파란 상자(나무), 노란 실린더(알루미늄)")
print("  + 보라색 작은 구 5개가 떨어집니다!")
print("  ESC → 종료")
print("─" * 55)

# ──────────────────────────────────────────────────
# 5단계: 시뮬레이션 루프
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
# 6단계: 결과
# ──────────────────────────────────────────────────
print(f"\n시뮬레이션 종료! (총 {sys.GetChTime():.2f}초)")
print(f"  구(철) 최종 높이:       {sphere.GetPos().y:.3f} m")
print(f"  상자(나무) 최종 높이:   {box.GetPos().y:.3f} m")
print(f"  실린더(알루미늄) 최종 높이: {cylinder.GetPos().y:.3f} m")
print("""
핵심 정리:
  1. ChBodyEasySphere/Box/Cylinder 로 한 줄로 물체 생성 가능
  2. 밀도(density)를 넣으면 질량과 관성이 자동 계산됨
  3. GetVisualShape(0).SetColor() 로 색상 변경 가능
  4. 같은 바닥 위에 다양한 형태의 물체를 동시에 시뮬레이션 가능

다음 단계:
  → lesson_05에서 물체끼리 부딪히는 충돌을 실험합니다
""")
