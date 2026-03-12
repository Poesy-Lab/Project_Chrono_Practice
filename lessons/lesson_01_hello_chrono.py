"""
==========================================================
Lesson 01: Hello Chrono - 자유낙하 시뮬레이션
==========================================================
학습 목표:
  1. ChSystemNSC 로 물리 세계를 만드는 법
  2. ChBody 로 물체를 만들고 추가하는 법
  3. DoStepDynamics 로 시뮬레이션을 실행하는 법
  4. 물체의 위치/속도를 읽는 법

실행 방법:
  source setup_chrono_env.sh
  python3 lessons/lesson_01_hello_chrono.py
==========================================================
"""

import pychrono as chrono

# ──────────────────────────────────────────────────
# 1단계: 물리 세계(시스템) 만들기
# ──────────────────────────────────────────────────
# ChSystemNSC = Non-Smooth Contact 방식의 물리 시스템
# 이것이 모든 시뮬레이션의 출발점입니다.
sys = chrono.ChSystemNSC()

# 중력 설정: y축 방향으로 -9.81 m/s² (지구 표면 중력)
sys.SetGravitationalAcceleration(chrono.ChVector3d(0, -9.81, 0))

print("물리 시스템 생성 완료!")
print(f"  중력: {sys.GetGravitationalAcceleration().y} m/s²")

# ──────────────────────────────────────────────────
# 2단계: 물체(공) 만들기
# ──────────────────────────────────────────────────
# ChBody = 강체 (rigid body). 형태가 변하지 않는 단단한 물체.
ball = chrono.ChBody()
ball.SetMass(1.0)                           # 질량: 1 kg
ball.SetPos(chrono.ChVector3d(0, 10, 0))    # 초기 위치: 높이 10m
ball.SetFixed(False)                        # 고정하지 않음 → 자유롭게 움직임
sys.AddBody(ball)

print(f"\n공 생성 완료!")
print(f"  질량: {ball.GetMass()} kg")
print(f"  초기 위치: y = {ball.GetPos().y} m")
print(f"  고정 여부: False (자유 낙하)")

# ──────────────────────────────────────────────────
# 3단계: 시뮬레이션 실행
# ──────────────────────────────────────────────────
# DoStepDynamics(dt) = 시간을 dt초만큼 전진시킨다.
# dt가 작을수록 정확하지만, 계산이 더 오래 걸립니다.

dt = 0.01   # 시간 간격: 10ms (0.01초)

print(f"\n{'시간(s)':>8}  {'높이(m)':>10}  {'속도(m/s)':>10}  {'이론높이(m)':>12}")
print("─" * 48)

while sys.GetChTime() < 2.0:
    sys.DoStepDynamics(dt)

    t = sys.GetChTime()
    y = ball.GetPos().y          # 현재 높이
    vy = ball.GetPosDt().y       # 현재 y방향 속도 (GetPosDt = 위치의 시간 미분 = 속도)

    # 이론값: y = y0 - (1/2) * g * t²
    y_theory = 10.0 - 0.5 * 9.81 * t * t

    # 0.2초마다 출력
    if abs(t % 0.2) < dt * 0.5 or abs(t % 0.2 - 0.2) < dt * 0.5:
        print(f"{t:8.2f}  {y:10.4f}  {vy:10.4f}  {y_theory:12.4f}")

# ──────────────────────────────────────────────────
# 4단계: 결과 확인
# ──────────────────────────────────────────────────
final_y = ball.GetPos().y
theory_y = 10 - 0.5 * 9.81 * 2.0**2

print(f"\n{'='*48}")
print(f"시뮬레이션 결과: y = {final_y:.4f} m")
print(f"이론값 (물리):   y = {theory_y:.4f} m")
print(f"오차:            {abs(final_y - theory_y):.6f} m")
print(f"{'='*48}")
print()
print("축하합니다! 첫 번째 물리 시뮬레이션을 완료했습니다!")
print()
print("다음 단계:")
print("  → lesson_02에서 바닥과의 충돌을 추가해 봅시다")
print("  → lesson_03에서 3D 시각화를 추가해 봅시다")
