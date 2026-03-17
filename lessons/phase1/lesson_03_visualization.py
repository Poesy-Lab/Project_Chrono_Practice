"""
==========================================================
Lesson 03: 3D 시각화 - Irrlicht로 시뮬레이션을 눈으로 보기!
==========================================================
학습 목표:
  1. Irrlicht 시각화 시스템 설정하기
  2. 물체에 시각적 형태(Visual Shape) 입히기
  3. 카메라, 조명, 하늘 배경 설정하기
  4. 실시간 시뮬레이션 루프 실행하기

복습 (Lesson 01~02):
  - 시스템, 물체, 충돌, 접촉 재질

새로 배우는 것:
  - ChVisualSystemIrrlicht : 3D 렌더링 엔진
  - ChVisualShapeSphere / Box : 눈에 보이는 형태
  - ChColor : 색상 지정
  - vis.Run() / BeginScene() / Render() / EndScene() : 렌더 루프

조작법 (실행 중):
  - 마우스 왼쪽 드래그 : 카메라 회전
  - 마우스 오른쪽 드래그 : 카메라 이동
  - 마우스 휠 : 줌 인/아웃
  - ESC 또는 창 닫기 : 종료

실행 방법:
  conda activate chrono
  source setup_chrono_env.sh
  python lessons/phase1/lesson_03_visualization.py
==========================================================
"""

import pychrono as chrono
import pychrono.irrlicht as chronoirr

print("=" * 55)
print("Lesson 03: 3D 시각화 (Irrlicht)")
print("=" * 55)

# ──────────────────────────────────────────────────
# 1단계: 시스템 + 충돌 설정 (Lesson 02 복습)
# ──────────────────────────────────────────────────
sys = chrono.ChSystemNSC()
sys.SetGravitationalAcceleration(chrono.ChVector3d(0, -9.81, 0))
sys.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)

# 접촉 재질
material = chrono.ChContactMaterialNSC()
material.SetFriction(0.4)
material.SetRestitution(0.5)

# ──────────────────────────────────────────────────
# 2단계: 바닥 만들기 (시각화 형태 포함!)
# ──────────────────────────────────────────────────
floor = chrono.ChBody()
floor.SetPos(chrono.ChVector3d(0, -1, 0))
floor.SetFixed(True)
floor.EnableCollision(True)
floor.AddCollisionShape(chrono.ChCollisionShapeBox(material, 20, 2, 20))

# ★ 새로운 부분: 눈에 보이는 형태 추가
#   Lesson 02에서는 콘솔 출력만 했지만, 이제 3D로 보여줍니다
floor_shape = chrono.ChVisualShapeBox(20, 2, 20)
floor_shape.SetColor(chrono.ChColor(0.4, 0.5, 0.4))  # 연한 녹색 바닥
floor.AddVisualShape(floor_shape)

sys.AddBody(floor)
print("바닥 생성 (녹색 상자)")

# ──────────────────────────────────────────────────
# 3단계: 공 3개 만들기 (각각 다른 색상, 높이)
# ──────────────────────────────────────────────────
# 공 만드는 함수
def create_ball(system, mat, pos, radius, color, name):
    """공 물체를 생성하고 시스템에 추가합니다."""
    ball = chrono.ChBody()
    ball.SetMass(1.0)
    ball.SetPos(pos)
    ball.SetFixed(False)
    ball.EnableCollision(True)

    # 충돌 형태
    ball.AddCollisionShape(chrono.ChCollisionShapeSphere(mat, radius))

    # 관성 모멘트 (구: I = 2/5 * m * r²)
    inertia = 2.0 / 5.0 * ball.GetMass() * radius**2
    ball.SetInertiaXX(chrono.ChVector3d(inertia, inertia, inertia))

    # ★ 시각적 형태 (눈에 보이는 구)
    ball_shape = chrono.ChVisualShapeSphere(radius)
    ball_shape.SetColor(color)
    ball.AddVisualShape(ball_shape)

    system.AddBody(ball)
    print(f"  {name}: 위치=({pos.x}, {pos.y}, {pos.z}), 색상={color.R:.1f},{color.G:.1f},{color.B:.1f}")
    return ball

print("\n공 3개 생성:")

# 빨간 공 - 높이 8m
ball_red = create_ball(
    sys, material,
    chrono.ChVector3d(-2, 8, 0), 0.4,
    chrono.ChColor(0.9, 0.2, 0.2), "빨간 공"
)

# 파란 공 - 높이 5m
ball_blue = create_ball(
    sys, material,
    chrono.ChVector3d(0, 5, 0), 0.3,
    chrono.ChColor(0.2, 0.3, 0.9), "파란 공"
)

# 노란 공 - 높이 3m
ball_yellow = create_ball(
    sys, material,
    chrono.ChVector3d(2, 3, 0), 0.35,
    chrono.ChColor(0.9, 0.8, 0.1), "노란 공"
)

# ──────────────────────────────────────────────────
# 4단계: Irrlicht 시각화 시스템 설정 ★
# ──────────────────────────────────────────────────
# 이 부분이 이번 레슨의 핵심입니다!
print("\n3D 시각화 초기화 중...")

vis = chronoirr.ChVisualSystemIrrlicht()
vis.AttachSystem(sys)               # 물리 시스템과 연결

vis.SetWindowSize(1280, 720)        # 창 크기 (가로 x 세로)
# 참고: macOS Retina에서는 렌더링이 창의 일부만 채울 수 있습니다.
#   이는 Irrlicht가 HiDPI를 지원하지 않는 알려진 제한사항입니다.
vis.SetWindowTitle('Lesson 03: Bouncing Balls')  # 창 제목
vis.Initialize()                    # 초기화

# 하늘 배경
vis.AddSkyBox()

# 카메라 설정
vis.AddCamera(
    chrono.ChVector3d(0, 5, 12),    # 카메라 위치 (약간 위에서 비스듬히)
    chrono.ChVector3d(0, 2, 0)      # 바라보는 지점
)

# 조명
vis.AddTypicalLights()

print("시각화 준비 완료!")
print("\n" + "─" * 55)
print("  3D 창이 열렸습니다!")
print("  마우스로 카메라를 조작할 수 있습니다:")
print("    왼쪽 드래그  → 회전")
print("    오른쪽 드래그 → 이동")
print("    휠           → 줌")
print("    ESC          → 종료")
print("─" * 55)

# ──────────────────────────────────────────────────
# 5단계: 실시간 시뮬레이션 루프
# ──────────────────────────────────────────────────
# vis.Run() = 창이 열려있는 동안 True 반환
# BeginScene() → Render() → EndScene() = 한 프레임 그리기
# DoStepDynamics() = 물리 한 스텝 계산

step_size = 0.005   # 5ms 간격

# ★ 실시간 속도 맞추기 (이게 없으면 물리가 순식간에 끝남!)
#   macOS에서는 vsync가 안 걸릴 수 있어서, 이 타이머가 시뮬레이션을
#   실제 시간과 동기화해줍니다. (없으면 공이 이미 떨어진 상태로 보임)
realtime_timer = chrono.ChRealtimeStepTimer()

while vis.Run():
    vis.BeginScene()       # 프레임 시작
    vis.Render()           # 3D 장면 그리기
    vis.EndScene()         # 프레임 끝
    sys.DoStepDynamics(step_size)  # 물리 계산
    realtime_timer.Spin(step_size) # 실제 시간에 맞춰 대기

# ──────────────────────────────────────────────────
# 6단계: 종료 후 결과
# ──────────────────────────────────────────────────
print(f"\n시뮬레이션 종료! (총 {sys.GetChTime():.2f}초 실행)")
print(f"  빨간 공 최종 높이: {ball_red.GetPos().y:.3f} m")
print(f"  파란 공 최종 높이: {ball_blue.GetPos().y:.3f} m")
print(f"  노란 공 최종 높이: {ball_yellow.GetPos().y:.3f} m")
print(f"""
핵심 정리:
  1. ChVisualSystemIrrlicht() 로 3D 렌더러 생성
  2. vis.AttachSystem(sys) 로 물리 시스템 연결
  3. AddVisualShape() 로 물체에 보이는 형태 추가
  4. while vis.Run(): BeginScene → Render → EndScene 루프

다음 단계:
  → lesson_04에서 다양한 형태의 물체를 만들어봅니다
""")
