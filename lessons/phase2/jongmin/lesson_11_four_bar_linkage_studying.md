순수 기구학 운동 전달을 보기 위함이므로 중력=0
~~~python
sys = chrono.ChSystemNSC()
sys.SetGravitationalAcceleration(chrono.ChVector3d(0, 0, 0))
~~~

크랭크 생성 및 시각화
~~~python
crank = chrono.ChBody()
crank.SetMass(1.0)
crank.SetInertiaXX(chrono.ChVector3d(0.01, 0.01, 0.1))
crank.SetPos(chrono.ChVector3d(crank_length / 2, 0, 0))
sys.AddBody(crank)

crank_shape = chrono.ChVisualShapeBox(crank_length, 0.12, 0.12)
crank_shape.SetColor(chrono.ChColor(0.8, 0.2, 0.2)) # 빨간색
crank.AddVisualShape(crank_shape)
~~~

커넥팅로드 생성 및 시각화
~~~python
conrod = chrono.ChBody()
conrod.SetMass(0.5)
conrod.SetInertiaXX(chrono.ChVector3d(0.01, 0.01, 0.05))
conrod.SetPos(chrono.ChVector3d(crank_length + rod_length / 2, 0, 0))
sys.AddBody(conrod)

conrod_shape = chrono.ChVisualShapeBox(rod_length, 0.08, 0.08)
conrod_shape.SetColor(chrono.ChColor(0.3, 0.6, 0.3)) # 초록색
conrod.AddVisualShape(conrod_shape)
~~~

슬라이더 생성 및 시각화
~~~python
slider = chrono.ChBody()
slider.SetMass(0.5)
slider.SetInertiaXX(chrono.ChVector3d(0.01, 0.01, 0.01))
slider.SetPos(chrono.ChVector3d(crank_length + rod_length, 0, 0))
sys.AddBody(slider)

slider_shape = chrono.ChVisualShapeBox(0.3, 0.3, 0.3)
slider_shape.SetColor(chrono.ChColor(0.2, 0.2, 0.8)) # 파란색
slider.AddVisualShape(slider_shape)
~~~

조인트1: 크랭크-땅-모터 연결
~~~python
motor = chrono.ChLinkMotorRotationSpeed()
motor.Initialize(crank, ground,
				chrono.ChFramed(chrono.ChVector3d(0, 0, 0), chrono.QUNIT))
motor.SetSpeedFunction(chrono.ChFunctionConst(crank_omega))
sys.Add(motor)
~~~

조인트2: 크랭크-커넥팅 로드 연결
~~~python
joint_crank_rod = chrono.ChLinkRevolute()
joint_crank_rod.Initialize(crank, conrod,
			chrono.ChFramed(chrono.ChVector3d(crank_length, 0, 0), chrono.QUNIT))
sys.Add(joint_crank_rod)
~~~

조인트3: 커넥팅 로드-슬라이더 연결
~~~python
joint_rod_slider = chrono.ChLinkRevolute()
joint_rod_slider.Initialize(conrod, slider,
chrono.ChFramed(chrono.ChVector3d(crank_length + rod_length, 0, 0), chrono.QUNIT))
sys.Add(joint_rod_slider)
~~~

조인트4: 슬라이더-프리즈매틱 조인트
프리즈매틱 조인트는 횐전은 막고 특정 방향으로만 미끄러지게 함
~~~python
prismatic = chrono.ChLinkLockPrismatic()
prismatic.Initialize(slider, ground, chrono.ChFramed(
chrono.ChVector3d(crank_length + rod_length, 0, 0),
chrono.QuatFromAngleY(math.pi / 2)))

sys.Add(prismatic)
~~~

데이터 기록
예제 10과 다르게 모터 입력->기구 출력->구동 토크 순서로 해석 대상이 넓어짐
~~~python
crank_angle = math.degrees(motor.GetMotorAngle())
slider_x = slider.GetPos().x
slider_v = slider.GetPosDt().x
torque = motor.GetMotorTorque()
~~~