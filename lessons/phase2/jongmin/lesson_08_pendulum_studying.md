라이브러리 부르기
~~~python
import os
import math
import matplotlib
matplotlib.use('Agg') # 그래프 창 없이 파일 저장이 가능한 백엔드 설정
import pychrono as chrono
~~~

시뮬레이션 변수 설정
~~~python
g = 9.81 # 중력가속도
L = 2.0 # 진자 길이
mass = 1.0 # 질량
theta0_deg = 15.0 # 초기 각도
theta0 = math.radians(theta0_deg)
dt = 0.001 # 시간 스텝
time_end = 10.0 # 시뮬레이션 시간
~~~

이론값 계산
~~~python
T_theory = 2 * math.pi * math.sqrt(L / g)
omega = math.sqrt(g / L)
~~~

고정점 생성
~~~python
pivot = chrono.ChBody()
pivot.SetFixed(True)
sys.AddBody(pivot)
pivot_marker = chrono.ChVisualShapeSphere(0.1)
pivot_marker.SetColor(chrono.ChColor(0.0, 0.8, 0.0))
pivot.AddVisualShape(pivot_marker)
~~~

초기 위치 계산
~~~python
x0 = L * math.sin(theta0)
y0 = -L * math.cos(theta0)
~~~

진자 강체 생성 및 초기 자세 설정
~~~python
pendulum = chrono.ChBody()
pendulum.SetMass(mass)
pendulum.SetInertiaXX(chrono.ChVector3d(0.01, 0.01, 0.01))
pendulum.SetPos(chrono.ChVector3d(x0, y0, 0))
pendulum.SetRot(chrono.QuatFromAngleZ(theta0))
sys.AddBody(pendulum)
~~~

진자 시각화 및 줄 붙이기
~~~python
bob_shape = chrono.ChVisualShapeSphere(0.15)
bob_shape.SetColor(chrono.ChColor(0.8, 0.1, 0.1))
pendulum.AddVisualShape(bob_shape)

rod_shape = chrono.ChVisualShapeBox(0.06, L, 0.06)
rod_shape.SetColor(chrono.ChColor(0.4, 0.4, 0.4))
pendulum.AddVisualShape(rod_shape, chrono.ChFramed(chrono.ChVector3d(0, L / 2, 0))
~~~

고정점과 진자 연결
~~~python
joint = chrono.ChLinkRevolute()
joint_frame = chrono.ChFramed(
chrono.ChVector3d(0, 0, 0),chrono.QUNIT)
joint.Initialize(pivot, pendulum, joint_frame)
sys.Add(joint)
~~~

시각화 설정
~~~python
if USE_VSG:
	vis = chronovsg.ChVisualSystemVSG()
	vis.SetCameraVertical(chrono.CameraVerticalDir_Y)
else:
	vis = chronoirr.ChVisualSystemIrrlicht()

vis.AttachSystem(sys)
vis.SetWindowSize(1024, 720)
vis.SetWindowTitle("Lesson 08 - Simple Pendulum")
  
if USE_VSG:
	vis.AddCamera(chrono.ChVector3d(0, -1, 6), chrono.ChVector3d(0, -1, 0))
	vis.Initialize()
else:
	vis.Initialize()
	vis.AddSkyBox()
	vis.AddCamera(chrono.ChVector3d(0, -1, 6), chrono.ChVector3d(0, -1, 0))
	vis.AddTypicalLights()
~~~

데이터 저장용 리스트 생성
~~~python
time_list = []
theta_sim = [] # 시뮬레이션 각도
theta_theory = [] # 이론 각도
~~~

시뮬레이션 루프 시작
~~~python
frame = 0
realtime_timer = chrono.ChRealtimeStepTimer()

while vis.Run():
	time = sys.GetChTime()
	if time > time_end:
		break

vis.BeginScene()
vis.Render()
vis.EndScene()
sys.DoStepDynamics(dt)
realtime_timer.Spin(dt)
~~~

시뮬레이션 및 이론 각도 계산
~~~python
pos = pendulum.GetPos()
theta = math.atan2(pos.x, -pos.y)
theta_th = theta0 * math.cos(omega * time)
~~~

데이터 저장
~~~python
time_list.append(time)
theta_sim.append(math.degrees(theta))
theta_theory.append(math.degrees(theta_th))
~~~

배열 변환 및 RSME 계산
~~~python
time_arr = np.array(time_list)
sim_arr = np.array(theta_sim)
th_arr = np.array(theta_theory)
error = sim_arr - th_arr
rmse = np.sqrt(np.mean(error**2))
~~~

이론 주기 및 시뮬레이션 주기 비교
~~~python
zero_crossings = []
for i in range(1, len(sim_arr)):
	if sim_arr[i - 1] > 0 and sim_arr[i] <= 0:
		zero_crossings.append(time_arr[i])
	if len(zero_crossings) >= 2:
		break
~~~