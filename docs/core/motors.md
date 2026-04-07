모터는 움직임이 있는 물체를 나타내는것으로, 크게 선형(linear), 회전(rotational)으로 나뉘며, 또한 3D(예시: body) 혹은 1D(예시: shaft)로 다시 나뉜다.

ChLinkMotorRotation 커맨드와 ChLinkMotorLinear는 ChLinkMate에서 계승되므로 모든 이하 모터에 관한 고려는 이를 따른다.

몇가지 예를 제외하고는 모터는 ChFunction으로 제어된다.

3줄요약:
1. 회전 아님 선형운동이 3차원 혹은 1차원에 존재
2. ChLinkMate 하위항목임
3. ChFunction으로 제어(왠만하면)

|-|3D Rotational|3D Linear|1D Linear/Rotational|
|---|---|---|---|
|Impose displacement|[ChLinkMotorRotationAngle](https://api.projectchrono.org/classchrono_1_1_ch_link_motor_rotation_angle.html)|[ChLinkMotorLinearPosition](https://api.projectchrono.org/classchrono_1_1_ch_link_motor_linear_position.html)|[ChShaftsMotorPosition](https://api.projectchrono.org/classchrono_1_1_ch_shafts_motor_position.html)|
|Impose speed|[ChLinkMotorRotationSpeed](https://api.projectchrono.org/classchrono_1_1_ch_link_motor_rotation_speed.html)|[ChLinkMotorLinearSpeed](https://api.projectchrono.org/classchrono_1_1_ch_link_motor_linear_speed.html)|[ChShaftsMotorSpeed](https://api.projectchrono.org/classchrono_1_1_ch_shafts_motor_speed.html)|
|Apply load|[ChLinkMotorRotationTorque](https://api.projectchrono.org/classchrono_1_1_ch_link_motor_rotation_torque.html)|[ChLinkMotorLinearForce](https://api.projectchrono.org/classchrono_1_1_ch_link_motor_linear_force.html)|[ChShaftsMotorLoad](https://api.projectchrono.org/classchrono_1_1_ch_shafts_motor_load.html)|
|Connect to 1D driveline|[ChLinkMotorRotationDriveline](https://api.projectchrono.org/classchrono_1_1_ch_link_motor_rotation_driveline.html)|[ChLinkMotorLinearDriveline](https://api.projectchrono.org/classchrono_1_1_ch_link_motor_linear_driveline.html)|-|


**3D Rotational Motors

이러한 모터들은 병진과 회전 운동등을 하는 두개의 ChBodyFrame 의 파트를 연결한다.(예: ChBody나 ChNodeFEAxyzrot).
모든 회전 모터는 ChLinkMotorRotation에서 나오며 회전은 고정된 프레임에서 Z축으로 radian을 유닛으로 회전한다.
![[Pasted image 20260406000733.png]]

회전 모터는 여러번 회전이 가능하며, 이때 Wrapped(최대 및 최소의 한계가 존재함)된 GetMotorAngelWrapped() 혹은 GetMotorAngle()옵션을 제공한다.

상대 위치|속도|가속도는 다음과 같은 명령어로 불러올 수 있다. : [GetMotorAngle()](https://api.projectchrono.org/classchrono_1_1_ch_link_motor_rotation.html#a6b88645142bcc95635583160554f6749)


기본적으로 모든 회전 모터는 고정된 z축으로 회전하는 조건을 가지고 있으나 [SetSpindleConstraint()](https://api.projectchrono.org/classchrono_1_1_ch_link_motor_rotation.html#abc15d05136796ed470a4cac1f601d4b4) 를 통해 다음과 같은 옵션을 줄 수 있다.
* FREE: 회전축에 정해진 제약조건(방향이나 정렬)이 없음
* REVOLUTE: x, y, z, rx, ry의 제약조건을 정함
* CYLINDRICAL: x, y, rx, ry의 제약조건을 정함
* OLDHAM: rx, ry의 제약조건을 정함

보통 모터의 추가는 다음과 같은 단계를 동원한다.
* 원하는 ChLinkMotorXxxYyy 클래스로부터 모터를 생성
* 해당 클래스에서 가능한 Initialize() 방법들중 하나 사용
* ChSystem 에 모터 추가
* 모터의 기능을 설명하는 [ChFunction](https://api.projectchrono.org/classchrono_1_1_ch_function.html) 물체 결합; 방법들의 이름은 특정 클래스에 따라 달라짐.


**3D Linear Motors**
이러한 모터들은 병진과 회전 운동등을 하는 두개의 ChBodyFrame 의 파트를 연결한다.(예: ChBody나 ChNodeFEAxyzrot). (데자뷰가 느껴진다면 정상입니다! 아까 본거 그대로 여기도 적혀있음)

모든 [ChLinkMotorLinear](https://api.projectchrono.org/classchrono_1_1_ch_link_motor_linear.html) 에서 나옴 선형 모터는 z축을 움직임이 허용된 축으로 가정한다.

![[Pasted image 20260406002522.png]]

기본적으로 모든 선형 모터는 다른 관계된 relative degree of freedom(자유도)에 대해 prismatic 한 제약조건을 제공하며(Y, Z에 대한 병진운동과 모터에 의해 제어되는 z의 회전 병진을 제외한 RX, RY, **RZ**에 대한 회전운동) 추가적인 ChLinkLockPrismatic등과 같은 접점을 생성할 필요가 없다. 물론 원한다면 이는 ChLinkMotorLinear::SetGuideConstraint() 기능을 이용하여 변경이 가능하며 다음과 같은 옵션을 줄 수 있다.

상대 위치|속도|가속도는 다음과 같은 명령어로 불러올 수 있다
[GetMotorPos()](https://api.projectchrono.org/classchrono_1_1_ch_link_motor_linear.html#a174ed7b286bb76b08d57bbb8cc515698) | [GetMotorPosDt()](https://api.projectchrono.org/classchrono_1_1_ch_link_motor_linear.html#ac09ba336e762f2d1cd04b1a5d4ed7b03) | [GetMotorPosDt2()](https://api.projectchrono.org/classchrono_1_1_ch_link_motor_linear.html#a01cb7fb41651d6f532345e7280f73228)

기본적으로 모든 선형 모터는 z축에 대해 prismatic한 제약조건을 가지나 [SetGuideConstraint()](https://api.projectchrono.org/classchrono_1_1_ch_link_motor_linear.html#ad78aff4322f29242de10299890e06599) 을 통해 다음과 같은 옵션으로 이를 지정할 수 있다.
* FREE: 롤러의 방향, 정렬에 제약조건을 두지 않음
* PRISMATIC: X, Y, RX, RY, RZ 제약조건을 둠(기본)
* SPHERICAL: X, Y 제약조건을 둠

초기화(initialization)은 ChLinkMotorRotation와 비슷하다.


**3D Driveline Motors**
 [ChLinkMotorLinearDriveline](https://api.projectchrono.org/classchrono_1_1_ch_link_motor_linear_driveline.html) 과[ChLinkMotorRotationDriveline](https://api.projectchrono.org/classchrono_1_1_ch_link_motor_rotation_driveline.html) 는 각각 상대적 병진, 회전 운동을 2개의 3차원 물체간에 줄 수 있다. 이는 [ChShaft](https://api.projectchrono.org/classchrono_1_1_ch_shaft.html)(1D 병진 혹은 회전 운동의 요소로 작용 가능함)의 병진/회전 운동을 커플링 함으로서 이뤄진다. 제약조건은 항상 z축으로 이뤄진다.

이러한 커플링으로 인해 축에 가해진 모든 움직임은 제약된 프레임에서 결과적인 움직임으로 연결된다(모터의 형태에 따라 선형이나 회전운동), 그러나 모든 제약된 물체에 대한 반작용 힘/토크는 축으로 다시 돌아온다.

이는 [ChFunction](https://api.projectchrono.org/classchrono_1_1_ch_function.html)를 통해 제공된 "신호"를 받는  [ChLinkMotor](https://api.projectchrono.org/classchrono_1_1_ch_link_motor.html)와 달리, 이 클래스는 파워의 균형을 보존시키며 위치와 힘 단계의 모든 커플링을 설명 가능함을 의미한다.

 [ChShaft](https://api.projectchrono.org/classchrono_1_1_ch_shaft.html)의 적절한 관성값을 세팅 해줘야만 낮은 관성 및 높은 속도에 의한 불안정성을 예방할 수 있으므로 주의를 기울여야 한다.


**1D Motors**
[ChShaftsMotor](https://api.projectchrono.org/classchrono_1_1_ch_shafts_motor.html)의 모터는 1차원 공간에서 짝지어진 물체간에 작동한다. 

이는 [ChLinkMotor](https://api.projectchrono.org/classchrono_1_1_ch_link_motor.html) 타입과 비슷하게 사용되며, 제약된 물체가 [ChShaft](https://api.projectchrono.org/classchrono_1_1_ch_shaft.html) type이라는 차이가 있다.

**Examples**
참조
* [demo_MBS_motors](https://github.com/projectchrono/chrono/blob/main/src/demos/mbs/demo_MBS_motors.cpp)


**3줄요약**
1. 모터는 선형이랑 회전형 있음: 레일따라 움직이거나 회전하거나. 1차원이랑 3차원에서 구현 가능
2. 제약조건 우리가 설정할 수 있음. 어디 고정되어있는지랑 어떻게 어디까지 움직일지등등
3. 모터에 가해진 속도, 힘, 위치등 불러올 수 있음