라이브러리 부르기
~~~python
import math
import pychrono as chrono
~~~

시각화 엔진 설정: VSG가 있다면 VSG 사용, 없다면 Irrlicht 사용
~~~python
try:
	import pychrono.vsg3d as chronovsg
	USE_VSG = True
except ImportError:
	USE_VSG = False
import pychrono.irrlicht as chronoirr
~~~

시뮬레이션 세계 및 중력 생성
~~~python
sys = chrono.ChSystemNSC()
sys.SetGravitationalAcceleration(chrono.ChVector3d(0, -9.81, 0))
~~~

고정된 기둥 생성
~~~python
pillar = chrono.ChBody()
pillar.SetFixed(True)
sys.AddBody(pillar)
~~~

위에서 생성한 기둥 시각화
~~~python
pillar_shape = chrono.ChVisualShapeBox(0.2, 2.0, 0.2)
pillar_shape.SetColor(chrono.ChColor(0.5, 0.5, 0.5))
pillar.AddVisualShape(pillar_shape)
~~~

첫 번째 막대 생성
~~~python
bar_length = 2.0
bar = chrono.ChBody()
bar.SetMass(2.0)
bar.SetInertiaXX(chrono.ChVector3d(0.1, 0.1, 2.0))
bar.SetPos(chrono.ChVector3d(bar_length / 2, 0, 0))
sys.AddBody(bar)
~~~

첫 번째 회전 조인트 생성 및 기준 프레임 정의, 기둥-막대1 연결
~~~python
joint = chrono.ChLinkRevolute()
joint_frame = chrono.ChFramed(chrono.ChVector3d(0, 0, 0), chrono.QUNIT)
joint.Initialize(pillar, bar, joint_frame)
sys.Add(joint)
~~~

두 번째 막대 생성
~~~python
bar2 = chrono.ChBody()
bar2.SetMass(1.0)
bar2.SetInertiaXX(chrono.ChVector3d(0.05, 0.05, 0.5))
bar2.SetPos(chrono.ChVector3d(bar_length + bar_length / 2, 0, 0))
sys.AddBody(bar2)
~~~

두 번째 회전 조인트 생성 및 기준 프레임 정의, 막대1-막대2 연결
~~~python
joint2 = chrono.ChLinkRevolute()
joint2_frame = chrono.ChFramed(chrono.ChVector3d(bar_length, 0, 0), chrono.QUNIT)
joint2.Initialize(bar, bar2, joint2_frame)
sys.Add(joint2)
~~~

조인트 위치 마커
~~~python
marker1 = chrono.ChVisualShapeSphere(0.12)
marker1.SetColor(chrono.ChColor(0.0, 0.8, 0.0))
pillar.AddVisualShape(marker1, chrono.ChFramed(chrono.ChVector3d(0, 0, 0)))

marker2 = chrono.ChVisualShapeSphere(0.12)
marker2.SetColor(chrono.ChColor(0.0, 0.8, 0.0))
bar.AddVisualShape(marker2, chrono.ChFramed(chrono.ChVector3d(bar_length / 2, 0, 0)))
~~~
