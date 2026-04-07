동력 전달 비율만 보기 위해 중력=0
~~~python
sys = chrono.ChSystemNSC()
sys.SetGravitationalAcceleration(chrono.ChVector3d(0, 0, 0))
~~~

기어/풀리가 원형처럼 보이게 하는 함수
macOS Irricht에서 원형 표현이 어색할 수 있기에 사용하는 함수
~~~python
def add_wheel_visual(body, radius, color, n_rim=12, thickness=0.08):
	# 림: 작은 박스를 원형으로 배치
	rim_size = 2 * math.pi * radius / n_rim * 0.7
	for i in range(n_rim):
		angle = 2 * math.pi * i / n_rim
		x = radius * math.cos(angle)
		y = radius * math.sin(angle)
		rim = chrono.ChVisualShapeBox(rim_size, rim_size, thickness)
		rim.SetColor(color)
		body.AddVisualShape(rim, chrono.ChFramed(chrono.ChVector3d(x, y, 0),
							chrono.QuatFromAngleZ(angle)))

	# 스포크: 중심에서 림까지 2개
	for angle in [0, math.pi / 2]:
		spoke = chrono.ChVisualShapeBox(0.05, radius * 1.8, thickness)
		spoke.SetColor(chrono.ChColor(color.R * 0.7, color.G * 0.7, color.B * 0.7))
		body.AddVisualShape(spoke, chrono.ChFramed(chrono.ChVector3d(0, 0, 0),
		chrono.QuatFromAngleZ(angle)))

	# 허브: 중심에 작은 구
	hub = chrono.ChVisualShapeSphere(radius * 0.15)
	hub.SetColor(chrono.ChColor(0.3, 0.3, 0.3))
	body.AddVisualShape(hub)

	# 방향 표시: 한쪽 끝에 노란 구
	tick = chrono.ChVisualShapeSphere(radius * 0.12)
	tick.SetColor(chrono.ChColor(1, 1, 0))
	body.AddVisualShape(tick, chrono.ChFramed(chrono.ChVector3d(0, radius, 0)))
~~~

기어A 생성 및 축 고정
원판의 중심축 기준 관성모멘트 공식 사용
~~~python
body_A = chrono.ChBody()
body_A.SetMass(1.0)
body_A.SetInertiaXX(chrono.ChVector3d(0.5, 0.5, 0.5 * 1.0 * r_A**2))
body_A.SetPos(chrono.ChVector3d(gear_x, 0, 0))
sys.AddBody(body_A)
add_wheel_visual(body_A, r_A, chrono.ChColor(0.8, 0.2, 0.2))

rev_A = chrono.ChLinkRevolute()
rev_A.Initialize(body_A, ground,
				chrono.ChFramed(chrono.ChVector3d(gear_x, 0, 0), chrono.QUNIT))
sys.Add(rev_A)
~~~

기어B 생성 및 축 고정
~~~python
body_B = chrono.ChBody()
body_B.SetMass(3.0)
body_B.SetInertiaXX(chrono.ChVector3d(0.5, 0.5, 0.5 * 3.0 * r_B**2))
body_B.SetPos(chrono.ChVector3d(gear_x, gear_center_dist, 0))
sys.AddBody(body_B)
add_wheel_visual(body_B, r_B, chrono.ChColor(0.2, 0.2, 0.8), n_rim=18)

rev_B = chrono.ChLinkRevolute()
rev_B.Initialize(body_B, ground,chrono.ChFramed(
				chrono.ChVector3d(gear_x, gear_center_dist, 0), chrono.QUNIT))
sys.Add(rev_B)
~~~

1D 축 생성 및 기어 구속
~~~python
shaft_A = chrono.ChShaft()
shaft_A.SetInertia(0.5 * 1.0 * r_A**2)
sys.Add(shaft_A)

shaft_B = chrono.ChShaft()
shaft_B.SetInertia(0.5 * 3.0 * r_B**2)
sys.Add(shaft_B)
~~~

1D 축 <-> 3D 바디 연결
1D shaft의 회전과 3D body의 실제 회전을 동기화하는 연결자이다. 회전축 방향 벡터 `(0,0,1)`을 준 건,  
z축 회전으로 연결하겠다는 뜻이다.
~~~python
connect_A = chrono.ChShaftBodyRotation()
connect_A.Initialize(shaft_A, body_A, chrono.ChVector3d(0, 0, 1))
sys.Add(connect_A)

connect_B = chrono.ChShaftBodyRotation()
connect_B.Initialize(shaft_B, body_B, chrono.ChVector3d(0, 0, 1))
sys.Add(connect_B)
~~~

기어비 구속
 `ChShaftsGear`: 두 shaft 사이에 기어비 관계를 거는 구속
 1D 축 사이의 이상적인 기어비 제약으로 동력 전달을 모델링한다는 것이다. 즉 실제 접촉 해석은 아니다.
~~~python
gear_link = chrono.ChShaftsGear()
gear_link.Initialize(shaft_A, shaft_B)
gear_link.SetTransmissionRatio(gear_ratio)
sys.Add(gear_link)
~~~

기어A 입력 모터: Shaft 모터
`ground_shaft_A`가 필요한 이유:
`ChShaftsMotorSpeed`는 두 shaft 사이에 작동하는 모터이므로  고정 기준이 되는 축 하나가 더 필요하다.
즉 `shaft_A` = 실제 구동축과 `ground_shaft_A` = 안 도는 기준축  둘 사이에 모터를 건다.
~~~python
ground_shaft_A = chrono.ChShaft()
ground_shaft_A.SetFixed(True)
sys.Add(ground_shaft_A)

motor_shaft_A = chrono.ChShaftsMotorSpeed()
motor_shaft_A.Initialize(shaft_A, ground_shaft_A)
motor_shaft_A.SetSpeedFunction(chrono.ChFunctionConst(motor_omega))
sys.Add(motor_shaft_A)
~~~

축 각속도를 RPM으로 환산
속도 크기 비교를 위해 절댓값으로 계산
~~~python
w_A = abs(shaft_A.GetPosDt()) * 60 / (2 * math.pi)
w_B = abs(shaft_B.GetPosDt()) * 60 / (2 * math.pi)
w_C = abs(shaft_C.GetPosDt()) * 60 / (2 * math.pi)
w_D = abs(shaft_D.GetPosDt()) * 60 / (2 * math.pi)
~~~