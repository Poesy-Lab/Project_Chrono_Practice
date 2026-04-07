다른 예제와 동일
~~~python
import os
import matplotlib
matplotlib.use('Agg') # Irrlicht 창과의 충돌 방지를 위해 비대화형 백엔드 사용
import pychrono as chrono

# 시각화 시스템 자동 선택 (VSG 우선, Irrlicht 폴백)
try:
	import pychrono.vsg3d as chronovsg
	USE_VSG = True
except ImportError:
	USE_VSG = False
import pychrono.irrlicht as chronoirr
import numpy as np
import matplotlib.pyplot as plt
~~~

시뮬레이션 상수 정의
~~~python
mass = 1.0
k1 = 50
c1 = 1
k2 = 50
c2 = 1
rest_length = 1.5
F_amp = 10
F_freq = 10
dt = 0.001
time_end = 10
~~~

스프링-댐퍼 이론값 계산
~~~python
wn1 = np.sqrt(k1 / mass)
zeta1 = c1 / (2 * np.sqrt(k1 * mass))
wd1 = wn1 * np.sqrt(1 - zeta1**2)
wn2 = np.sqrt(k2 / mass)
zeta2 = c2 / (2 * np.sqrt(k2 * mass))
wd2 = wn2 * np.sqrt(1 - zeta2**2)
~~~

감쇠 영역 판별 함수
~~~python
def damping_regime(zeta):
	if zeta < 1:
		return "Under-damped"
	elif np.isclose(zeta, 1):
		return "Critical"
	else:
		return "Over-damped"
~~~

사용자 정의 힘 함수 생성
이 부분은 `chrono.ForceFunctor`에 구속을 받음
~~~python
class MySpringForce(chrono.ForceFunctor):
	def evaluate(self, time, rest_length, length, vel, link):
		Fs = -k2 * (length - rest_length)
		Fd = -c2 * vel
		Fext = F_amp * np.sin(F_freq * time)
		return Fs + Fd + Fext
~~~

크로노 시스템 생성
스프림-댐퍼 응답만 관찰하기 위해 중력=0으로 설정
~~~python
sys = chrono.ChSystemNSC()
sys.SetGravitationalAcceleration(chrono.ChVector3d(0, 0, 0))
~~~

땅 생성 및 고정점 시각화
~~~python
ground = chrono.ChBody()
ground.SetFixed(True)
sys.AddBody(ground)

ground.AddVisualShape(
	chrono.ChVisualShapeSphere(0.1),
	chrono.ChFramed(chrono.ChVector3d(-1, 0, 0)))

ground.AddVisualShape(
	chrono.ChVisualShapeSphere(0.1),
	chrono.ChFramed(chrono.ChVector3d(1, 0, 0)))
~~~

바디1, 2 생성 및 시각화
~~~python
body_1 = chrono.ChBody()
body_1.SetMass(mass)
body_1.SetInertiaXX(chrono.ChVector3d(1, 1, 1))
body_1.SetPos(chrono.ChVector3d(-1, -3, 0)) # 초기 위치 (평형점 아래)
sys.AddBody(body_1)
  
box1 = chrono.ChVisualShapeBox(0.4, 0.4, 0.4)
box1.SetColor(chrono.ChColor(0.7, 0, 0)) # 빨간색
body_1.AddVisualShape(box1)

body_2 = chrono.ChBody()
body_2.SetMass(mass)
body_2.SetInertiaXX(chrono.ChVector3d(1, 1, 1))
body_2.SetPos(chrono.ChVector3d(1, -3, 0)) # 초기 위치 (평형점 아래)
sys.AddBody(body_2)

box2 = chrono.ChVisualShapeBox(0.4, 0.4, 0.4)
box2.SetColor(chrono.ChColor(0, 0, 0.7)) # 파란색
body_2.AddVisualShape(box2)
~~~

내장 스프링-댐퍼 연결 및 시각화
~~~python
spring_1 = chrono.ChLinkTSDA()
spring_1.Initialize(body_1, ground, True,
					chrono.ChVector3d(0, 0, 0), # body_1의 로컬 연결점
					chrono.ChVector3d(-1, 0, 0)) # ground의 로컬 연결점

spring_1.SetRestLength(rest_length)
spring_1.SetSpringCoefficient(k1)
spring_1.SetDampingCoefficient(c1)

# 스프링 코일 시각화
# - VSG / Irrlicht(Windows/Linux): ChVisualShapeSpring 정상 동작
# - Irrlicht(macOS): 선 렌더링 안 됨 → 구 마커 체인으로 보완
spring_1.AddVisualShape(chrono.ChVisualShapeSpring(0.1, 80, 15))
sys.AddLink(spring_1)
~~~

커스텀 스프링-댐퍼 연결 및 시각화
~~~python
force_functor = MySpringForce()
spring_2 = chrono.ChLinkTSDA()
spring_2.Initialize(body_2, ground, True,
					chrono.ChVector3d(0, 0, 0),
					chrono.ChVector3d(1, 0, 0))

spring_2.SetRestLength(rest_length)
spring_2.RegisterForceFunctor(force_functor)

spring_2.AddVisualShape(chrono.ChVisualShapeSpring(0.1, 80, 15))
sys.AddLink(spring_2)
~~~

현재 위치 기록 및 이론해 계산
~~~python
y1 = body_1.GetPos().y
y2 = body_2.GetPos().y

# 해석해: 부족감쇠 자유진동 x(t) = x0 * e^(-ζωn*t) * cos(ωd*t)
x_theory = x0 * np.exp(-zeta1 * wn1 * time) * np.cos(wd1 * time)
y_theory = x_theory + y_eq
~~~