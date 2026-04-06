import pychrono as chrono

# NSC 시스템: 접촉/마찰 같은 보완성 문제용
system = chrono.ChSystemNSC()
system.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)
system.SetGravitationalAcceleration(chrono.ChVector3d(0, -9.81, 0))

# VI solver 설정
solver = chrono.ChSolverPSOR()
solver.SetMaxIterations(100)
system.SetSolver(solver)

print("VI solver 설정 완료")

# 접촉 재질(NSC용)
contact_mat = chrono.ChContactMaterialNSC()

# -------------------------
# 바닥 생성
# -------------------------
ground = chrono.ChBodyEasyBox(
    10.0,   # x 길이
    0.2,    # y 두께
    10.0,   # z 길이
    1000,   # 밀도
    True,   # visualization
    True,   # collision
    contact_mat
)
ground.SetFixed(True)
ground.SetPos(chrono.ChVector3d(0, -0.1, 0))  # 윗면이 y=0이 되게
system.Add(ground)

# -------------------------
# 떨어지는 박스 생성
# -------------------------
body = chrono.ChBodyEasyBox(
    0.4,    # x 길이
    0.4,    # y 길이
    0.4,    # z 길이
    1000,   # 밀도
    True,   # visualization
    True,   # collision
    contact_mat
)
body.SetPos(chrono.ChVector3d(0, 1.0, 0))
system.Add(body)

print("접촉 시스템 구성 완료")

# -------------------------
# 시뮬레이션
# -------------------------
step_size = 0.01
end_time = 2.0

print("=== VI solver 시뮬레이션 시작 ===")

while system.GetChTime() < end_time:
    system.DoStepDynamics(step_size)
    print("t:", system.GetChTime(), "y:", body.GetPos().y)

print("=== 끝 ===")