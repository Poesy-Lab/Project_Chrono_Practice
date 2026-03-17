"""
==========================================================
Lesson 05: 물체 간 충돌 - 볼링처럼 물체끼리 부딪히기
==========================================================
학습 목표:
  1. 여러 물체가 서로 충돌하는 장면 만들기
  2. 초기 속도(SetPosDt)를 줘서 물체를 발사하기
  3. 물체 간 충돌에서 운동량 보존 관찰하기
  4. 충돌 후 물체들의 움직임 분석하기

복습 (Lesson 01~04):
  - 시스템, 충돌, 접촉 재질, 시각화, 다양한 형태

새로 배우는 것:
  - SetPosDt() : 초기 속도 설정 (물체를 밀어서 발사!)
  - 여러 물체 간 상호 충돌
  - for 루프로 물체 배열 만들기

실행 방법:
  conda activate chrono
  source setup_chrono_env.sh
  python lessons/phase1/lesson_05_multi_collision.py
==========================================================
"""

import pychrono as chrono

# 시각화 시스템 자동 선택 (VSG 우선, Irrlicht 폴백)
try:
    import pychrono.vsg3d as chronovsg
    USE_VSG = True
except ImportError:
    USE_VSG = False
import pychrono.irrlicht as chronoirr

print("=" * 55)
print("Lesson 05: 물체 간 충돌 (볼링)")
print("=" * 55)

# ──────────────────────────────────────────────────
# 1단계: 시스템 설정
# ──────────────────────────────────────────────────
sys = chrono.ChSystemNSC()
sys.SetGravitationalAcceleration(chrono.ChVector3d(0, -9.81, 0))
sys.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)

material = chrono.ChContactMaterialNSC()
material.SetFriction(0.4)
material.SetRestitution(0.3)

# ──────────────────────────────────────────────────
# 2단계: 바닥 (살짝 마찰이 있는 평면)
# ──────────────────────────────────────────────────
floor = chrono.ChBody()
floor.SetPos(chrono.ChVector3d(0, -0.5, 0))
floor.SetFixed(True)
floor.EnableCollision(True)
floor.AddCollisionShape(chrono.ChCollisionShapeBox(material, 40, 1, 20))
floor_shape = chrono.ChVisualShapeBox(40, 1, 20)
floor_shape.SetColor(chrono.ChColor(0.6, 0.55, 0.45))  # 나무 바닥 색
floor.AddVisualShape(floor_shape)
sys.AddBody(floor)

# ──────────────────────────────────────────────────
# 3단계: 볼링 핀 배치 (피라미드 형태)
# ──────────────────────────────────────────────────
# 실제 볼링처럼 삼각형으로 핀 배치:
#   1열: 1개, 2열: 2개, 3열: 3개, 4열: 4개
print("\n볼링 핀 배치:")

pins = []
pin_positions = [
    # 1열 (가장 앞)
    (3, 0),
    # 2열
    (3.5, -0.3), (3.5, 0.3),
    # 3열
    (4.0, -0.6), (4.0, 0), (4.0, 0.6),
    # 4열 (가장 뒤)
    (4.5, -0.9), (4.5, -0.3), (4.5, 0.3), (4.5, 0.9),
]

for i, (px, pz) in enumerate(pin_positions):
    # 실린더를 핀으로 사용 (반지름 0.06m, 높이 0.4m)
    pin = chrono.ChBodyEasyCylinder(
        chrono.ChAxis_Y, 0.06, 0.4, 700, True, True, material
    )
    pin.SetPos(chrono.ChVector3d(px, 0.2, pz))
    pin.GetVisualShape(0).SetColor(chrono.ChColor(0.95, 0.95, 0.9))  # 흰색
    sys.AddBody(pin)
    pins.append(pin)

print(f"  {len(pins)}개 핀 배치 완료 (피라미드 형태)")

# ──────────────────────────────────────────────────
# 4단계: 볼링 공 만들기 (★ 초기 속도로 발사!)
# ──────────────────────────────────────────────────
# 볼링공: 실제 볼링공과 비슷한 크기/무게
#   실제 볼링공: 반지름 ~0.11m, 질량 ~7kg → 밀도 약 12500
#   여기서는 시각적으로 잘 보이도록 약간 크게 만듦
ball = chrono.ChBodyEasySphere(0.15, 12000, True, True, material)
ball.SetPos(chrono.ChVector3d(-5, 0.15, 0))   # 왼쪽에서 시작

# ★ 새로운 개념: 초기 속도 설정!
#   SetPosDt() = 속도(position derivative = 위치의 시간 미분)
#   x방향으로 6 m/s로 발사 (핀을 향해)
ball.SetPosDt(chrono.ChVector3d(6, 0, 0))

ball.GetVisualShape(0).SetColor(chrono.ChColor(0.1, 0.1, 0.8))  # 진한 파랑
sys.AddBody(ball)

print(f"\n볼링 공 생성:")
print(f"  질량: {ball.GetMass():.2f} kg")
print(f"  초기 위치: x = -5.0 m (왼쪽)")
print(f"  초기 속도: 6.0 m/s (오른쪽으로 →)")
print(f"  운동량: {ball.GetMass() * 6.0:.1f} kg·m/s")

# ──────────────────────────────────────────────────
# 5단계: 시각화
# ──────────────────────────────────────────────────
print("\n3D 시각화 초기화 중...")

if USE_VSG:
    vis = chronovsg.ChVisualSystemVSG()
    vis.SetCameraVertical(chrono.CameraVerticalDir_Y)
else:
    vis = chronoirr.ChVisualSystemIrrlicht()

vis.AttachSystem(sys)
vis.SetWindowSize(1280, 720)
vis.SetWindowTitle('Lesson 05: Bowling Collision')

if USE_VSG:
    vis.AddCamera(chrono.ChVector3d(0, 5, 8), chrono.ChVector3d(2, 0, 0))
    vis.Initialize()
else:
    vis.Initialize()
    vis.AddSkyBox()
    vis.AddCamera(chrono.ChVector3d(0, 5, 8), chrono.ChVector3d(2, 0, 0))
    vis.AddTypicalLights()

print("시각화 준비 완료!")
print("\n" + "─" * 55)
print("  파란 볼링공이 흰색 핀을 향해 굴러갑니다!")
print("  충돌 후 핀이 쓰러지는 모습을 관찰하세요.")
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
# 7단계: 결과 분석
# ──────────────────────────────────────────────────
# 쓰러진 핀 세기: 원래 높이(y=0.2)에서 벗어났으면 쓰러진 것
fallen = sum(1 for p in pins if abs(p.GetPos().y - 0.2) > 0.1)

print(f"\n시뮬레이션 종료! (총 {sys.GetChTime():.2f}초)")
print(f"  쓰러진 핀: {fallen} / {len(pins)}")
print(f"  볼링공 최종 위치: ({ball.GetPos().x:.1f}, {ball.GetPos().y:.1f}, {ball.GetPos().z:.1f})")
print(f"  볼링공 최종 속도: {ball.GetPosDt().x:.2f} m/s")
print("""
핵심 정리:
  1. SetPosDt() 로 물체에 초기 속도를 줄 수 있음
  2. 여러 물체가 자동으로 서로 충돌/반응함
  3. 무거운 물체 → 가벼운 물체: 운동량 전달됨
  4. for 루프로 물체를 대량 배치할 수 있음

다음 단계:
  → lesson_06에서 마찰과 재질의 차이를 비교합니다
""")
