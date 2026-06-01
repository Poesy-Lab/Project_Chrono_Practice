---
title: "Viper 달 로버"
author: ""
last_modified: "2026-03-31"
tags:
  - chrono
  - robot
---
# Chrono Robot Models – Viper Moon Rover Model

## 1. Viper Rover란?
![[Pasted image 20260518215023.png]]

`Viper`는 Project Chrono에서 제공하는 **달 탐사용 로버 모델**이다. 공식 문서에서는 이 모델을 `Viper moon rover model`로 분류하고 있으며, `chrono::viper` namespace 아래에 관련 클래스들이 정리되어 있다.

Chrono에서 Viper는  **4륜 로버형 robot model**이다. 따라서 기존의 vehicle처럼 track shoe, sprocket, idler를 중심으로 보는 것이 아니라, 다음 요소를 중심으로 이해해야 한다.

|핵심 요소|의미|
|---|---|
|Chassis|로버 본체|
|Wheel|4개의 구동 바퀴|
|Suspension arms|각 바퀴를 지지하는 upper/lower arm|
|Upright / steering rod|조향 및 바퀴 연결부|
|Driver|바퀴 회전 속도, 토크, 조향, 리프팅 제어|
|Contact material|바퀴와 지형 사이의 접촉 물성|

공식 문서에서 Viper 모델은 robot models 하위에 있으며, 주요 클래스에는 `ViperPart`, `ViperChassis`, `ViperWheel`, `ViperUpperArm`, `ViperLowerArm`, `ViperUpright`, `Viper`, `ViperDriver` 및 여러 driver class가 포함된다.

---

## 2. Chrono에서 Viper의 역할

Chrono에서 `Viper`는 로버 전체를 구성하는 wrapper 또는 entry point 역할을 한다.

공식 API 문서에 따르면 `chrono::viper::Viper` 클래스는 **모든 Viper 부품의 위치와 회전을 chassis 기준으로 캡슐화하며, 완전한 rover를 만들기 위한 entry point로 사용되어야 한다**고 설명되어 있다.

즉, 사용자는 보통 개별적으로 chassis, wheel, suspension arm을 직접 하나하나 만드는 것이 아니라, 다음처럼 `Viper` 객체를 중심으로 로버를 생성하고 제어한다.

> ChSystem  
> → Viper rover 생성  
> → Wheel type 선택  
> → Driver 연결  
> → 초기 위치 설정  
> → Simulation loop에서 Viper.Update() 호출  
> → System.DoStepDynamics() 수행

M113 예제에서 `veh.M113()`이 tracked vehicle 전체를 생성하는 진입점이었다면, Viper에서는 `chrono::viper::Viper`가 유사한 역할을 한다고 보면 된다.

---

# 3. Viper 모델의 전체 구조

공식 문서 기준으로 Viper moon rover model은 다음 클래스들로 구성된다.

|클래스|역할|
|---|---|
|`ViperPart`|모든 Viper 부품의 base class|
|`ViperChassis`|로버 chassis|
|`ViperWheel`|로버 wheel|
|`ViperUpperArm`|suspension upper arm|
|`ViperLowerArm`|suspension lower / bottom arm|
|`ViperUpright`|steering rod / upright|
|`Viper`|rover 전체를 생성하고 관리하는 class|
|`ViperDriver`|driver base class|
|`ViperDCMotorControl`|DC motor torque 기반 driver|
|`ViperSpeedDriver`|wheel angular speed 기반 driver|
|`ViperDirectControl`|wheel별 직접 제어 driver|

구조적으로 정리하면 다음과 같다.

> Viper  
> ├─ ViperChassis  
> ├─ 4 × ViperWheel  
> ├─ 4 × ViperUpperArm  
> ├─ 4 × ViperLowerArm  
> ├─ 4 × ViperUpright  
> ├─ 4 × Driveshaft  
> └─ ViperDriver

---

# 4. ViperPart

## 4.1 개념

`ViperPart`는 Viper 모델의 모든 부품에 대한 공통 base class이다. 공식 문서에서는 Viper rover parts가 chassis, steering, upper suspension arm, bottom suspension arm, wheel을 포함한다고 설명한다.

즉, `ViperPart`는 개별 부품들이 공통적으로 가져야 하는 속성과 기능을 정의한다.

---

## 4.2 주요 기능

|함수|의미|
|---|---|
|`GetName()`|부품 이름 반환|
|`SetName()`|부품 이름 설정|
|`SetVisualize(bool)`|시각화 활성/비활성화|
|`EnableCollision(bool)`|collision 활성/비활성화|
|`Initialize(chassis)`|부품을 chassis body에 부착하여 초기화|
|`GetBody()`|해당 부품의 `ChBodyAuxRef` 반환|
|`GetPos()`|부품의 절대 위치 반환|
|`GetRot()`|부품의 절대 자세 반환|
|`GetLinVel()`|부품의 선속도 반환|
|`GetAngVel()`|부품의 각속도 반환|
|`GetLinAcc()`|부품의 선가속도 반환|
|`GetAngAcc()`|부품의 각가속도 반환|

공식 API 문서에 따르면 `GetPos()`, `GetRot()`, `GetLinVel()`, `GetAngVel()` 등은 부품 reference frame의 global frame 기준 위치, 자세, 속도를 반환한다.

---

## 4.3 내부 속성

`ViperPart`는 다음과 같은 protected attributes를 가진다.

|내부 변수|의미|
|---|---|
|`m_name`|부품 이름|
|`m_body`|부품의 rigid body|
|`m_mat`|contact material|
|`m_mesh_name`|visualization mesh 이름|
|`m_mesh_xform`|mesh transform|
|`m_color`|시각화 색상|
|`m_pos`|chassis 기준 상대 위치|
|`m_mass`|질량|
|`m_inertia`|주관성모멘트|
|`m_cog`|COG frame|
|`m_visualize`|visualization flag|
|`m_collide`|collision flag|

기존의 vehicle에서 각 subsystem이 독립적으로 정의되었던 것과 달리, Viper 모델에서는 많은 부품이 `ViperPart`의 공통 구조를 상속받아 만들어진다.

---

# 5. ViperChassis

## 5.1 개념

`ViperChassis`는 Viper rover의 본체이다. 공식 문서에서는 단순히 “Viper rover Chassis”라고 설명한다.

Chassis는 로버의 기준 body에 해당하며, wheel, arm, upright 등이 이 chassis를 기준으로 배치된다.

---

## 5.2 주요 함수

|함수|의미|
|---|---|
|`ViperChassis(name, mat)`|chassis 생성자|
|`Initialize(system, pos)`|chassis를 지정된 절대 위치에 초기화|

`ViperChassis::Initialize()`는 chassis를 지정된 absolute position에 초기화하는 함수이다.

또한 `ViperChassis`는 `ViperPart`를 상속하므로, `GetBody()`, `GetPos()`, `GetRot()`, `SetVisualize()`, `EnableCollision()` 등 공통 기능을 함께 가진다.

---

# 6. ViperWheel

## 6.1 개념

`ViperWheel`은 Viper rover의 바퀴 모델이다. 공식 문서에서는 `Viper rover Wheel`이라고 설명한다.

Viper는 4개의 wheel을 가지며, 각 wheel은 `ViperWheelID` enum으로 구분된다.

|Wheel ID|의미|
|---|---|
|`V_LF`|left front|
|`V_RF`|right front|
|`V_LB`|left back|
|`V_RB`|right back|

공식 문서에서도 `ViperWheelID`는 wheel/suspension identifier이며, `V_LF`, `V_RF`, `V_LB`, `V_RB`를 각각 left front, right front, left back, right back으로 정의한다.

---

## 6.2 Wheel Type

Viper wheel은 세 가지 wheel geometry type 중 하나로 생성할 수 있다.

|Wheel type|의미|
|---|---|
|`RealWheel`|실제 Viper wheel geometry|
|`SimpleWheel`|단순화된 wheel geometry|
|`CylWheel`|원통형 wheel geometry|

공식 문서에서는 `ViperWheelType::RealWheel`을 actual geometry, `SimpleWheel`을 simplified wheel geometry, `CylWheel`을 cylindrical wheel geometry라고 설명한다.

---

## 6.3 Wheel type 선택 기준

|목적|추천 wheel type|
|---|---|
|실제 Viper wheel 형상에 가까운 접촉/시각화|`RealWheel`|
|계산을 가볍게 하고 싶을 때|`SimpleWheel`|
|가장 단순한 wheel contact 검증|`CylWheel`|

초기 예제나 팀원 설치 검증용이라면 `SimpleWheel` 또는 `CylWheel`이 더 안정적일 수 있다. 실제 rover wheel 형상과 지면 접촉을 보고 싶다면 `RealWheel`을 선택하면 된다.

---

# 7. Suspension Arms

## 7.1 ViperUpperArm

`ViperUpperArm`은 Viper rover suspension의 upper arm이다. 공식 문서에서는 “The upper arm of the Viper rover suspension”이라고 설명한다.

생성자는 다음 정보를 받는다.

|인자|의미|
|---|---|
|`name`|부품 이름|
|`rel_pos`|chassis frame 기준 상대 위치|
|`mat`|contact material|
|`side`|차량 좌우 side, 문서 기준 0: L, 1: R|

공식 문서에서도 `side` 인자는 0이 left, 1이 right를 의미한다고 설명한다.

---

## 7.2 ViperLowerArm

`ViperLowerArm`은 Viper rover suspension의 bottom arm이다. 공식 문서에서는 “The bottom arm of the Viper rover suspension”이라고 설명한다.

생성자 인자는 upper arm과 유사하다.

|인자|의미|
|---|---|
|`name`|부품 이름|
|`rel_pos`|chassis frame 기준 상대 위치|
|`mat`|contact material|
|`side`|차량 좌우 side, 문서 기준 0: L, 1: R|

---

## 7.3 Upper/Lower Arm의 역할

Viper의 suspension arm은 바퀴와 chassis 사이의 기구학적 연결을 담당한다.

구조적으로는 다음처럼 이해할 수 있다.

> Chassis  
> → Upper arm / Lower arm  
> → Upright  
> → Wheel

Tracked vehicle의 suspension이 road wheel arm, spring-damper, revolute joint 중심이었다면, Viper에서는 rover wheel을 지지하는 arm mechanism 중심으로 이해하면 된다.

---

# 8. ViperUpright

## 8.1 개념

`ViperUpright`은 공식 문서에서 **steering rod**로 설명된다. 문서에 따르면 steering rod는 steering cylinder에 연결되며, 이 link가 조향 제어를 담당한다. 또한 steering rod에는 두 개의 connecting rod가 있어 suspension의 upper arm과 bottom arm에 연결된다.

즉, `ViperUpright`은 단순한 세로 지지대가 아니라, 바퀴 조향과 suspension linkage를 연결하는 핵심 부품이다.

---

## 8.2 역할

| 역할                 | 설명                                      |
| ------------------ | --------------------------------------- |
| 조향 연결              | steering motor 또는 steering cylinder와 연결 |
| wheel carrier 역할   | wheel과 suspension arm 사이 연결부            |
| upper/lower arm 연결 | 두 connecting rod를 통해 suspension arm과 연결 |
| wheel attitude 결정  | wheel의 조향각과 자세에 영향                      |

구조적으로는 다음과 같다.

> Steering input  
> → ViperUpright / steering rod  
> → Wheel steering angle 변화  
> → Rover 진행 방향 변화

---

# 9. Viper Class

## 9.1 개념

`chrono::viper::Viper`는 로버 전체를 대표하는 class이다. 공식 문서에서는 이 클래스가 모든 Viper 부품의 chassis 기준 위치/회전 정보를 캡슐화하고, 완전한 rover를 만들기 위한 entry point라고 설명한다.

---

## 9.2 생성자

|생성자|의미|
|---|---|
|`Viper(ChSystem* system, ViperWheelType wheel_type = RealWheel)`|지정한 Chrono system 안에 Viper rover를 생성|

기본 wheel type은 `RealWheel`이다. 하지만 계산 비용을 줄이거나 단순 검증을 하려면 `SimpleWheel` 또는 `CylWheel`을 고려할 수 있다.

---

## 9.3 주요 설정 함수

|함수|의미|
|---|---|
|`SetDriver(driver)`|driver system 연결|
|`SetWheelContactMaterial(mat)`|wheel contact material 설정|
|`SetChassisFixed(bool)`|chassis를 ground에 고정할지 설정|
|`SetChassisVisualization(bool)`|chassis 시각화 활성/비활성화|
|`SetWheelVisualization(bool)`|wheel 시각화 활성/비활성화|
|`SetSuspensionVisualization(bool)`|suspension 시각화 활성/비활성화|
|`Initialize(pos)`|지정된 위치에서 rover 초기화|
|`Update()`|매 integration step 전에 호출해야 하는 update 함수|

공식 문서에서는 `Viper::Update()`가 각 integration step 전에 호출되어야 한다고 설명한다.

---

## 9.4 상태 접근 함수

`Viper` 클래스는 로버와 각 wheel의 상태를 얻기 위한 함수들을 제공한다.

|함수|의미|
|---|---|
|`GetSystem()`|로버가 포함된 Chrono system 반환|
|`GetChassis()`|rover chassis 반환|
|`GetWheels()`|모든 wheel 반환|
|`GetWheel(id)`|지정 wheel 반환|
|`GetUpright(id)`|지정 wheel 위치의 upright 반환|
|`GetUpperArm(id)`|지정 wheel 위치의 upper arm 반환|
|`GetLowerArm(id)`|지정 wheel 위치의 lower arm 반환|
|`GetDriveshaft(id)`|지정 wheel의 driveshaft 반환|
|`GetChassisPos()`|chassis 위치|
|`GetChassisRot()`|chassis 자세|
|`GetChassisVel()`|chassis 선속도|
|`GetChassisAcc()`|chassis 선가속도|
|`GetWheelLinVel(id)`|wheel 선속도|
|`GetWheelAngVel(id)`|wheel 각속도|
|`GetWheelContactForce(id)`|wheel 접촉력|
|`GetWheelContactTorque(id)`|wheel 접촉 토크|
|`GetWheelAppliedForce(id)`|wheel에 작용한 전체 힘|
|`GetWheelTracTorque(id)`|wheel tractive torque|
|`GetWheelAppliedTorque(id)`|wheel에 작용한 전체 토크|
|`GetRoverMass()`|전체 rover 질량|
|`GetWheelMass()`|wheel 질량|
|`GetDriveMotorFunc(id)`|drive motor function 반환|
|`GetSteerMotorFunc(id)`|steering motor function 반환|
|`GetDriveMotor(id)`|drive motor 반환|
|`GetSteerMotor(id)`|steering motor 반환|

특히 결과값 저장용 예제를 만들 때는 다음 함수들이 중요하다.

|저장 항목|사용할 함수|
|---|---|
|chassis 위치|`GetChassisPos()`|
|chassis 속도|`GetChassisVel()`|
|wheel 각속도|`GetWheelAngVel(id)`|
|wheel 접촉력|`GetWheelContactForce(id)`|
|wheel tractive torque|`GetWheelTracTorque(id)`|
|rover mass|`GetRoverMass()`|

---

# 10. ViperDriver

## 10.1 개념

`ViperDriver`는 Viper rover driver의 base class이다. 공식 문서에서는 derived class가 현재 시간에서 motor control 값을 설정하기 위해 `Update()` 함수를 구현해야 한다고 설명한다. 또는 derived class가 Viper rover에 직접 접근하여 wheel driveshaft에 torque를 적용하는 방식으로 제어할 수도 있다고 설명한다.

즉, `ViperDriver`는 기존 Vehicle의 throttle/brake/steering driver와 비슷한 역할을 하지만, Viper에서는 wheel별 angular speed, steering angle, lift angle을 직접 다루는 구조에 가깝다.

---

## 10.2 DriveMotorType

`ViperDriver`는 drive motor control type을 다음 두 가지로 구분한다.

|DriveMotorType|의미|
|---|---|
|`SPEED`|angular speed 제어|
|`TORQUE`|torque 제어|

---

## 10.3 Driver 내부 제어값

`ViperDriver`는 다음 배열을 내부적으로 가진다.

|내부 변수|의미|
|---|---|
|`drive_speeds`|4개 drive motor의 angular speed|
|`steer_angles`|4개 steer motor의 steering angle|
|`lift_angles`|4개 lift motor의 lift angle|

즉, Viper는 4개의 wheel을 각각 독립적으로 제어할 수 있는 구조를 가진다.

---

## 10.4 주요 함수

|함수|의미|
|---|---|
|`GetDriveMotorType()`|drive motor 제어 방식 반환|
|`SetSteering(angle)`|전체 steering input 설정|
|`SetSteering(angle, id)`|특정 wheel steering angle 설정|
|`SetLifting(angle)`|lift input angle 설정|
|`Update(time)`|현재 시간 기준 driver input 갱신|

공식 문서에서는 `SetSteering(angle, id)`가 특정 wheel의 steering angle을 설정하며, `Update(time)`은 각 rover update마다 호출되어 drive motor angular speed, steering motor angle, lift motor angle을 갱신해야 한다고 설명한다.

---

# 11. Driver 하위 클래스

## 11.1 ViperSpeedDriver

`ViperSpeedDriver`는 가장 단순하게 사용하기 좋은 driver이다. 공식 문서에서는 이 driver가 **모든 wheel에 같은 angular speed를 적용하며, 이 angular speed를 0에서 지정된 값까지 ramp시킨다**고 설명한다.

|항목|내용|
|---|---|
|클래스|`ViperSpeedDriver`|
|제어 방식|wheel angular speed 제어|
|생성자|`ViperSpeedDriver(time_ramp, speed)`|
|특징|모든 wheel에 동일한 angular speed 적용|
|적합한 용도|단순 직진 주행, 설치 검증, 기본 예제|

예제 문서나 팀원 설치 확인용 코드를 만든다면, `ViperSpeedDriver`가 가장 직관적이다.

---

## 11.2 ViperDCMotorControl

`ViperDCMotorControl`은 단순 DC motor control을 구현한 driver이다. 공식 문서에 따르면 이 driver는 rover의 driveshaft에 직접 torque를 적용하는 방식으로 DC motor control을 구현하며, steering control은 사용자가 `SetSteering()`을 통해 직접 수행해야 한다.

|함수|의미|
|---|---|
|`SetMotorStallTorque(torque, id)`|지정 wheel의 motor stall torque 설정|
|`SetMotorNoLoadSpeed(speed, id)`|지정 wheel의 DC motor no-load speed 설정|

공식 문서에서는 기본 stall torque가 300, 기본 no-load speed가 π라고 설명한다.

이 driver는 실제 모터 특성에 가까운 제어를 보고 싶을 때 사용할 수 있다.

---

## 11.3 ViperDirectControl

`ViperDirectControl`은 각 wheel의 drive speed, steer angle, lift angle을 직접 지정할 수 있는 driver이다. 공식 문서에서는 이 driver가 모든 wheel에 대해 drive speeds, steer angles, lift angles를 개별적으로 직접 제어할 수 있게 해준다고 설명한다.

|함수|의미|
|---|---|
|`SetDirectControl(drive_speeds, steer_angles, lift_angles)`|4개 wheel의 drive speed, steering angle, lifting angle 직접 설정|

이 driver는 단순 예제보다는 다음과 같은 경우에 유용하다.

|사용 목적|설명|
|---|---|
|wheel별 독립 제어|네 바퀴 속도를 다르게 지정|
|steering 실험|앞/뒤/좌/우 wheel 조향각 따로 설정|
|motion planning|로버 제어 알고리즘과 연결|
|obstacle crossing|특정 wheel lift angle 제어 실험|

---

# 12. Viper의 제어 구조

Viper는 일반 자동차처럼 throttle/brake 하나로 움직이는 구조라기보다는, wheel motor와 steering motor를 직접 제어하는 로봇 모델에 가깝다.

구조적으로 보면 다음과 같다.

> Driver  
> → drive_speeds 또는 drive_torques 설정  
> → steering angles 설정  
> → lift angles 설정  
> → Viper.Update()  
> → motor constraints / driveshafts 업데이트  
> → Chrono system integration  
> → rover motion

Driver별 차이를 정리하면 다음과 같다.

| Driver                | Drive 제어                    | Steering 제어             | 특징          |
| --------------------- | --------------------------- | ----------------------- | ----------- |
| `ViperSpeedDriver`    | 모든 wheel 같은 angular speed   | `SetSteering()` 가능      | 가장 단순       |
| `ViperDCMotorControl` | wheel driveshaft에 torque 적용 | 사용자가 직접 `SetSteering()` | DC motor 근사 |
| `ViperDirectControl`  | wheel별 speed 직접 지정          | wheel별 angle 직접 지정      | 가장 유연       |

---

# 13. Tracked Vehicle과의 차이

M113 tracked vehicle과 Viper rover를 비교하면 다음과 같다.

|항목|M113 Tracked Vehicle|Viper Rover|
|---|---|---|
|모델 분류|Vehicle / tracked vehicle|Robot model / rover|
|지면 접촉 요소|track shoe|wheel|
|구동 방식|sprocket이 track shoe 구동|wheel drive motor|
|주요 서브시스템|track assembly, sprocket, idler, suspension|chassis, wheel, arms, upright, driver|
|driver 입력|throttle, brake, steering 중심|wheel speed/torque, steering angle, lift angle|
|접촉 복잡도|track shoe가 많아 contact 수 많음|wheel 4개 중심|
|예제 난이도|상대적으로 무거움|상대적으로 단순한 로버 예제 가능|

캡스톤에서 Chrono 사용법을 익히는 목적이라면, Viper는 M113보다 **로봇 제어, wheel-terrain contact, rover mobility**를 보기 좋다. 반면 track shoe, sprocket, idler 같은 궤도 차량 특성은 M113 쪽이 더 적합하다.

---

# 14. Viper 모델에서 결과값을 얻을 때 중요한 함수

Viper를 이용해 시뮬레이션 결과를 CSV로 저장하거나 그래프로 분석하려면 다음 함수들을 우선적으로 보면 좋다.

|목적|함수|
|---|---|
|로버 위치|`GetChassisPos()`|
|로버 자세|`GetChassisRot()`|
|로버 속도|`GetChassisVel()`|
|로버 가속도|`GetChassisAcc()`|
|wheel 선속도|`GetWheelLinVel(id)`|
|wheel 각속도|`GetWheelAngVel(id)`|
|wheel 접촉력|`GetWheelContactForce(id)`|
|wheel 접촉 토크|`GetWheelContactTorque(id)`|
|wheel 전체 작용력|`GetWheelAppliedForce(id)`|
|wheel 전체 작용 토크|`GetWheelAppliedTorque(id)`|
|wheel 구동 토크|`GetWheelTracTorque(id)`|
|rover 질량|`GetRoverMass()`|
|wheel 질량|`GetWheelMass()`|

특히 로버 주행 검증용 예제에서는 다음 값만 저장해도 충분하다.

|CSV 항목|의미|
|---|---|
|time|시뮬레이션 시간|
|chassis x, y, z|로버 위치|
|chassis vx, vy, vz|로버 속도|
|wheel angular velocity|각 바퀴 회전 속도|
|wheel contact force|각 바퀴 접촉력|
|steering angle|조향 입력|
|drive speed or torque|구동 입력|

---

# 15. Viper 예제 작성 시 추천 구조

팀원들이 실행해볼 수 있는 간단한 예제를 만든다면, 다음 구성이 좋다.

## 15.1 가장 단순한 직진 예제

|항목|설정|
|---|---|
|Wheel type|`SimpleWheel` 또는 `CylWheel`|
|Driver|`ViperSpeedDriver`|
|Terrain|flat rigid terrain|
|입력|wheel angular speed를 0에서 목표값까지 ramp|
|출력|chassis position, velocity, wheel angular velocity 저장|

구조:

> Viper 생성  
> → ViperSpeedDriver 연결  
> → 평지 terrain 생성  
> → 0초부터 wheel speed ramp  
> → rover 직진  
> → CSV 저장

이 방식은 설치 검증 및 기본 작동 확인에 적합하다.

---

## 15.2 조향 예제

|항목|설정|
|---|---|
|Driver|`ViperSpeedDriver` 또는 `ViperDirectControl`|
|입력|일정 wheel speed + steering angle|
|출력|x, y 위치와 yaw 변화|

구조:

> 일정 속도로 전진  
> → steering angle 부여  
> → 원호 주행  
> → trajectory 저장

이 예제는 Viper가 단순 wheel vehicle이 아니라, wheel steering을 가진 rover model이라는 점을 보여주기 좋다.

---

## 15.3 장애물 통과 예제

|항목|설정|
|---|---|
|Terrain|rigid terrain + 작은 box obstacle|
|Driver|`ViperSpeedDriver`|
|출력|chassis z, pitch, wheel contact force|

구조:

> 평지 주행  
> → 작은 장애물 접근  
> → wheel이 장애물 접촉  
> → chassis pitch/z 변화  
> → contact force 저장

이 예제는 rover mobility와 wheel-terrain interaction을 확인하기 좋다.

---

# 16. 주의할 점

## 16.1 `Viper.Update()`를 매 step 전에 호출해야 한다

공식 문서에서 `Viper::Update()`는 각 integration step 전에 호출되어야 한다고 설명한다.

따라서 simulation loop는 대략 다음 순서로 구성해야 한다.

> 현재 시간 확인  
> → driver input 갱신  
> → `viper.Update()` 호출  
> → terrain 또는 기타 system update  
> → `DoStepDynamics(step_size)` 호출  
> → 결과 저장

---

## 16.2 Driver 종류에 따라 motor 접근 방식이 달라진다

`GetDriveMotor()`와 `GetDriveMotorFunc()`는 driver가 torque control을 사용하는 경우 empty pointer를 반환할 수 있다. 공식 문서에서도 drive motor 또는 motor function 접근 함수는 associated driver가 torque control을 사용하면 empty pointer를 반환한다고 설명한다.

즉, 다음을 구분해야 한다.

|Driver 방식|주의점|
|---|---|
|speed control|motor function 접근 가능|
|torque control|drive motor function이 비어 있을 수 있음|
|direct torque 적용|driveshaft torque를 직접 봐야 할 수 있음|

---

## 16.3 Wheel type에 따라 접촉/계산 비용이 달라진다

`RealWheel`은 실제 형상에 가까운 wheel geometry이고, `SimpleWheel`은 단순화된 wheel geometry, `CylWheel`은 원통형 wheel geometry이다.

따라서 wheel-terrain contact 결과는 wheel type에 따라 달라질 수 있다.

|Wheel type|장점|단점|
|---|---|---|
|`RealWheel`|실제 형상 반영|계산 비용 증가 가능|
|`SimpleWheel`|안정적이고 비교적 가벼움|실제 형상 단순화|
|`CylWheel`|가장 단순|wheel lug/복잡 형상 반영 어려움|

---

# 17. 캡스톤 문서에서 강조하면 좋은 내용

Viper 문서를 팀원들과 공유할 목적이라면, 다음 내용을 강조하는 것이 좋다.

|강조 항목|이유|
|---|---|
|Viper는 tracked vehicle이 아니라 robot rover model|M113과 구조가 다르기 때문|
|`Viper` class가 전체 rover entry point|개별 부품보다 이 class 중심으로 사용|
|wheel은 4개이며 ID로 접근|데이터 저장, 제어, 디버깅에 중요|
|driver class 선택이 중요|speed/torque/direct control 방식이 달라짐|
|`Viper.Update()` 호출 필요|simulation loop에서 빠지면 제어 입력 갱신이 안 될 수 있음|
|결과값 접근 함수가 잘 제공됨|contact force, wheel torque, chassis velocity 등 추출 가능|
|wheel type 선택 가능|정확도와 계산 비용 trade-off|

---

# 18. 한 줄 요약

Chrono의 `Viper`는 **달 탐사용 4륜 로버 robot model**이며, tracked vehicle의 sprocket/track shoe/idler 구조가 아니라 **chassis, wheel, suspension arm, upright, wheel motor, driver control**을 중심으로 구성된다.

전체 구조는 다음과 같다.

> `Viper`  
> → `ViperChassis`  
> → 4개의 `ViperWheel`  
> → 4개의 `ViperUpperArm` / `ViperLowerArm`  
> → 4개의 `ViperUpright`  
> → `ViperDriver`로 wheel speed, torque, steering, lifting 제어

팀원 검증용 예제나 간단한 로버 주행 예제를 만들 때는 다음 조합이 가장 적합하다.

|항목|추천|
|---|---|
|Rover class|`chrono::viper::Viper`|
|Wheel type|`SimpleWheel` 또는 `CylWheel`|
|Driver|`ViperSpeedDriver`|
|Task|정지 상태에서 wheel speed ramp로 직진|
|Output|chassis position, velocity, wheel angular velocity, wheel contact force|

Viper를 사용할 때 가장 먼저 봐야 할 핵심 함수는 다음이다.

|핵심 함수|의미|
|---|---|
|`Viper(system, wheel_type)`|rover 생성|
|`SetDriver(driver)`|driver 연결|
|`Initialize(pos)`|초기 위치 설정|
|`Update()`|매 step 전 rover 상태 갱신|
|`GetChassisPos()`|위치 출력|
|`GetChassisVel()`|속도 출력|
|`GetWheelAngVel(id)`|wheel 회전속도 출력|
|`GetWheelContactForce(id)`|wheel 접촉력 출력|
|`SetSteering(angle)`|조향 입력|
|`SetLifting(angle)`|lift 입력|
