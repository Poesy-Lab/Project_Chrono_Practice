"""
==========================================================
Lesson 02: 충돌과 바닥 - 공이 바닥에 부딪혀 튕기기
==========================================================
학습 목표:
  1. 고정된 바닥(floor) 물체 만들기
  2. 충돌(collision) 시스템 활성화하기
  3. 접촉 재질(contact material) 설정하기
  4. 반발 계수(restitution)로 튕김 정도 조절하기

복습 (Lesson 01):
  - ChSystemNSC 로 시스템 생성
  - ChBody 로 물체 생성 및 추가
  - DoStepDynamics 로 시뮬레이션 실행

새로 배우는 것:
  - ChContactMaterialNSC : 접촉 재질 (마찰, 반발 계수)
  - ChCollisionShapeBox / Sphere : 충돌 형태 정의
  - EnableCollision(True) : 충돌 활성화
  - SetFixed(True) : 물체 고정 (바닥처럼 안 움직이게)

실행 방법:
  conda activate chrono
  source setup_chrono_env.sh
  python lessons/lesson_02_collision.py
==========================================================
"""

import pychrono as chrono

# ──────────────────────────────────────────────────
# 1단계: 시스템 생성
# ──────────────────────────────────────────────────
sys = chrono.ChSystemNSC()
sys.SetGravitationalAcceleration(chrono.ChVector3d(0, -9.81, 0))

# 충돌 감지 시스템 설정
# Bullet = 오픈소스 물리 엔진의 충돌 감지 알고리즘
sys.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)

print("=" * 55)
print("Lesson 02: 충돌과 바닥")
print("=" * 55)

# ──────────────────────────────────────────────────
# 2단계: 접촉 재질(Contact Material) 만들기
# ──────────────────────────────────────────────────
# 접촉 재질 = 두 물체가 부딪힐 때 어떻게 반응할지 결정
#
# 주요 속성:
#   - 마찰 계수 (friction): 0=미끄러움, 1=거침
#   - 반발 계수 (restitution): 0=안 튕김(찰흙), 1=완전 튕김(슈퍼볼)

material = chrono.ChContactMaterialNSC()
material.SetFriction(0.3)        # 마찰 계수 0.3
material.SetRestitution(0.7)     # 반발 계수 0.7 (꽤 잘 튕김)

print(f"\n접촉 재질 생성:")
print(f"  마찰 계수:   0.3")
print(f"  반발 계수:   0.7 (꽤 잘 튕김)")

# ──────────────────────────────────────────────────
# 3단계: 바닥 만들기
# ──────────────────────────────────────────────────
# 바닥 = 고정된(Fixed) 물체 + 충돌 형태
floor = chrono.ChBody()
floor.SetMass(1)                                # 질량 (고정체라 무관하지만 필요)
floor.SetPos(chrono.ChVector3d(0, -1, 0))       # 위치: y=-1 (바닥면이 y=0이 되도록)
floor.SetFixed(True)                            # 고정! 중력에 안 떨어짐
floor.EnableCollision(True)                     # 충돌 활성화

# 충돌 형태 추가: 가로 20m x 세로 2m x 깊이 20m 상자
floor.AddCollisionShape(chrono.ChCollisionShapeBox(material, 20, 2, 20))
sys.AddBody(floor)

print(f"\n바닥 생성:")
print(f"  위치: y = {floor.GetPos().y} m")
print(f"  크기: 20m x 2m x 20m (상자)")
print(f"  고정: True (움직이지 않음)")

# ──────────────────────────────────────────────────
# 4단계: 공 만들기
# ──────────────────────────────────────────────────
ball = chrono.ChBody()
ball.SetMass(1.0)                               # 1 kg
ball.SetPos(chrono.ChVector3d(0, 5, 0))         # 높이 5m에서 시작
ball.SetFixed(False)                            # 자유롭게 움직임
ball.EnableCollision(True)                      # 충돌 활성화

# 충돌 형태 추가: 반지름 0.3m 구
ball.AddCollisionShape(chrono.ChCollisionShapeSphere(material, 0.3))

# 관성 모멘트 설정 (구의 공식: I = 2/5 * m * r²)
radius = 0.3
inertia = 2.0 / 5.0 * ball.GetMass() * radius**2
ball.SetInertiaXX(chrono.ChVector3d(inertia, inertia, inertia))

sys.AddBody(ball)

print(f"\n공 생성:")
print(f"  질량: {ball.GetMass()} kg")
print(f"  반지름: {radius} m")
print(f"  초기 높이: y = {ball.GetPos().y} m")
print(f"  충돌: 활성화됨")

# ──────────────────────────────────────────────────
# 5단계: 시뮬레이션 실행
# ──────────────────────────────────────────────────
dt = 0.001       # 시간 간격: 1ms (충돌 정확도를 위해 작게)
end_time = 4.0   # 총 4초 시뮬레이션

print(f"\n{'시간(s)':>8}  {'높이(m)':>10}  {'속도(m/s)':>10}  상태")
print("─" * 50)

prev_vy = 0          # 이전 속도 (바운스 감지용)
bounce_count = 0     # 바운스 횟수

while sys.GetChTime() < end_time:
    sys.DoStepDynamics(dt)

    t = sys.GetChTime()
    y = ball.GetPos().y
    vy = ball.GetPosDt().y

    # 바운스 감지: 속도가 음→양으로 바뀌는 순간
    if prev_vy < -0.5 and vy > 0:
        bounce_count += 1
        print(f"{t:8.3f}  {y:10.4f}  {vy:10.4f}  *** 바운스 #{bounce_count}! ***")

    # 0.2초마다 일반 출력
    elif abs(t % 0.2) < dt * 0.5 or abs(t % 0.2 - 0.2) < dt * 0.5:
        status = "낙하 중" if vy < -0.1 else ("상승 중" if vy > 0.1 else "정지")
        print(f"{t:8.3f}  {y:10.4f}  {vy:10.4f}  {status}")

    prev_vy = vy

# ──────────────────────────────────────────────────
# 6단계: 결과 요약
# ──────────────────────────────────────────────────
print(f"\n{'=' * 50}")
print(f"시뮬레이션 결과:")
print(f"  총 바운스 횟수: {bounce_count}")
print(f"  최종 높이:      {ball.GetPos().y:.4f} m")
print(f"  최종 속도:      {ball.GetPosDt().y:.4f} m/s")
print(f"  반발 계수:      0.7")
print(f"{'=' * 50}")

print(f"""
핵심 정리:
  1. 충돌하려면 두 물체 모두 EnableCollision(True)
  2. 충돌 형태(CollisionShape)를 반드시 추가해야 함
  3. 접촉 재질(ChContactMaterialNSC)로 마찰/반발 설정
  4. 바닥은 SetFixed(True)로 고정

다음 단계:
  → lesson_03에서 이 시뮬레이션을 Irrlicht 3D로 시각화합니다
""")
