두 개의 모터를 고정하는 프레임 생성 및 시각화
~~~python
ground = chrono.ChBody()
ground.SetFixed(True)
sys.AddBody(ground)
ground_bar = chrono.ChVisualShapeBox(4.0, 0.15, 0.15)
ground_bar.SetColor(chrono.ChColor(0.5, 0.5, 0.5))
ground.AddVisualShape(ground_bar)
~~~

모터 A용 회전팔 생성 및 시각화
~~~python
arm_A = chrono.ChBody()
arm_A.SetMass(arm_mass)
arm_A.SetInertiaXX(chrono.ChVector3d(0.1, 0.1, arm_mass * arm_length**2 / 12))
arm_A.SetPos(chrono.ChVector3d(-2, arm_length / 2, 0))
sys.AddBody(arm_A)

arm_A_shape = chrono.ChVisualShapeBox(0.15, arm_length, 0.15)
arm_A_shape.SetColor(chrono.ChColor(0.8, 0.2, 0.2)) # 빨간색
arm_A.AddVisualShape(arm_A_shape)
~~~

모터 A에 일정 속도 부여
~~~python
motor_speed = chrono.ChLinkMotorRotationSpeed()
motor_speed.Initialize(arm_A, ground,
chrono.ChFramed(chrono.ChVector3d(-2, 0, 0), chrono.QUNIT))

speed_func = chrono.ChFunctionConst(omega)
motor_speed.SetSpeedFunction(speed_func)
sys.Add(motor_speed)
~~~

모터 B용 회전팔 생성 및 시각화
~~~python
arm_B = chrono.ChBody()
arm_B.SetMass(arm_mass)
arm_B.SetInertiaXX(chrono.ChVector3d(0.1, 0.1, arm_mass * arm_length**2 / 12))
arm_B.SetPos(chrono.ChVector3d(2, arm_length / 2, 0))
sys.AddBody(arm_B)

arm_B_shape = chrono.ChVisualShapeBox(0.15, arm_length, 0.15)
arm_B_shape.SetColor(chrono.ChColor(0.2, 0.2, 0.8)) # 파란색
arm_B.AddVisualShape(arm_B_shape)
~~~

모터 B에 사인파 형태 목표 각도 부여
~~~python
motor_angle = chrono.ChLinkMotorRotationAngle()
motor_angle.Initialize(arm_B, ground,
chrono.ChFramed(chrono.ChVector3d(2, 0, 0), chrono.QUNIT))

angle_amp = math.radians(45) # 45° 진폭
angle_freq = math.pi # π rad/s → 주기 2초
angle_func = chrono.ChFunctionSine(angle_amp, angle_freq / (2 * math.pi))
motor_angle.SetAngleFunction(angle_func)
sys.Add(motor_angle)
~~~

지지대에 기둥 추가
~~~python
for x_pos in [-2, 2]:
	pillar = chrono.ChVisualShapeBox(0.2, 0.6, 0.2)
	pillar.SetColor(chrono.ChColor(0.4, 0.4, 0.4))
	ground.AddVisualShape(pillar, 
						chrono.ChFramed(chrono.ChVector3d(x_pos, -0.3, 0)))
~~~

현재 모터의 회전각 및 토크 읽기
~~~python
angle_A = math.degrees(motor_speed.GetMotorAngle())
torque_A = motor_speed.GetMotorTorque()
angle_B = math.degrees(motor_angle.GetMotorAngle())
torque_B = motor_angle.GetMotorTorque()
~~~