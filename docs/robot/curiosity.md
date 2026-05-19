---
title: "Curiosity 화성 로버"
author: "Hojin Park"
last_modified: "2026-05-19"
tags:
  - chrono
  - robot
  - rover
  - curiosity
---

# Curiosity 화성 로버

> [!info] 코드 표기
> 이 문서의 코드 예시는 **PyChrono(Python)** 기준이다.
> Chrono 공식 문서의 C++ namespace는 `chrono::curiosity`이지만, PyChrono에서는 보통 `import pychrono.robot as robot` 후 `robot.Curiosity(...)`처럼 사용한다.

Curiosity는 Chrono::Robot에서 제공하는 **NASA Curiosity 기반 6륜 화성 탐사 로버 모델**이다.
직접 `ChBody`, 조인트, 바퀴, 모터를 모두 조립하지 않아도, 내장 모델을 불러와 로버 주행을 바로 실험할 수 있다.

우리 프로젝트에서 Curiosity는 다음 역할을 한다.

```text
로버를 처음부터 직접 만들기 전,
Chrono가 로버를 어떤 구조로 모델링하는지 보는 기준 예제
```

즉, Curiosity 문서의 목표는 "Curiosity 자체를 완벽히 분석"하는 것보다, 아래 질문에 답할 수 있게 하는 것이다.

```text
1. 로버를 Chrono system에 어떻게 추가하는가?
2. 바퀴 모터와 조향 입력은 어떻게 주는가?
3. 지형/장애물/충돌 실험에서 어떤 값을 기록해야 하는가?
4. 1인 1로버 프로젝트에서 어떤 구조를 참고할 수 있는가?
```

---

## 1. Curiosity 모델의 구성

공식 API 기준으로 Curiosity 모델은 여러 part class로 구성된다.
우리가 처음부터 모두 직접 만질 필요는 없지만, 어떤 부품들이 들어 있는지는 알아두는 것이 좋다.

| 구성 | 관련 클래스 | 의미 |
|---|---|---|
| 전체 로버 | `Curiosity` | 로버 생성, 초기화, 업데이트의 진입점 |
| 차체 | `CuriosityChassis` | 로버 중심 body |
| 바퀴 | `CuriosityWheel` | 6개의 wheel body |
| Rocker | `CuriosityRocker` | rocker-bogie suspension의 앞/중간 링크 |
| Bogie | `CuriosityBogie` | 뒤쪽 wheel linkage |
| 조향 upright | `CuriosityUpright` | 앞/뒤 조향 바퀴 연결부 |
| differential | `CuriosityDifferentialBar`, `CuriosityDifferentialLink` | 좌우 rocker 움직임 연결 |
| driver | `CuriosityDriver` | 로버 입력 시스템의 base class |
| DC motor driver | `CuriosityDCMotorControl` | 단순 DC 모터 토크 제어 |
| speed driver | `CuriositySpeedDriver` | 바퀴 각속도를 직접 주는 driver |

Curiosity는 6개 바퀴를 가진다.

| Wheel ID | 의미 |
|---|---|
| `C_LF` | left front |
| `C_RF` | right front |
| `C_LM` | left middle |
| `C_RM` | right middle |
| `C_LB` | left back |
| `C_RB` | right back |

> [!note] 조향 가능한 바퀴
> 공식 코드 기준으로 middle wheel(`C_LM`, `C_RM`)에는 개별 조향 입력이 적용되지 않는다.
> 앞/뒤 바퀴 조향과 6개 wheel drive를 통해 로버가 움직인다.

---

## 2. 가장 기본적인 생성 흐름

Python 데모 `demo_ROBOT_Curiosity_Rigid.py`의 핵심 흐름은 아래와 같다.

```python
import pychrono as chrono
import pychrono.robot as robot

system = chrono.ChSystemNSC()
system.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)
system.SetGravitationalAcceleration(chrono.ChVector3d(0, 0, -9.81))

# 바닥 또는 지형
ground_mat = chrono.ChContactMaterialNSC()
ground = chrono.ChBodyEasyBox(20, 20, 1, 1000, True, True, ground_mat)
ground.SetPos(chrono.ChVector3d(0, 0, -0.5))
ground.SetFixed(True)
system.Add(ground)

# Curiosity rover
driver = robot.CuriosityDCMotorControl()
rover = robot.Curiosity(system)
rover.SetDriver(driver)

init_frame = chrono.ChFramed(
    chrono.ChVector3d(0, 0.2, 0),
    chrono.ChQuaterniond(1, 0, 0, 0),
)
rover.Initialize(init_frame)
```

핵심 순서:

```text
1. ChSystemNSC 생성
2. collision system과 gravity 설정
3. 지형 또는 바닥 생성
4. Curiosity driver 생성
5. Curiosity(system) 생성
6. rover.SetDriver(driver)
7. rover.Initialize(initial_frame)
```

> [!important] `SetDriver()`가 먼저다
> `Curiosity.Initialize(...)` 내부에서는 driver가 있다고 가정한다.
> 따라서 `rover.SetDriver(driver)`를 먼저 호출하고, 그 다음에 `rover.Initialize(...)`를 호출해야 한다.

---

## 3. 좌표계와 중력 방향

Curiosity 공식 Python demo는 **Z-up** 기준이다.

```python
system.SetGravitationalAcceleration(chrono.ChVector3d(0, 0, -9.81))
```

이는 일부 Phase 1~2 예제에서 사용한 Y-up 구조와 다르다.
Robot/Vehicle 계열 예제에서는 Z-up으로 두는 것이 자연스럽다.

| 축 | 의미 |
|---|---|
| X | 전후 방향 |
| Y | 좌우 방향 |
| Z | 위/아래 방향 |

시각화에서도 Z-up을 맞춘다.

```python
vis.SetCameraVertical(chrono.CameraVerticalDir_Z)
```

> [!warning] Y-up 코드와 섞지 않기
> `ChVector3d(0, -9.81, 0)` 중력 예제를 그대로 가져오면 Curiosity가 이상한 방향으로 떨어질 수 있다.
> Curiosity/Vehicle/로버 실험에서는 우선 `ChVector3d(0, 0, -9.81)`로 통일하자.

---

## 4. Driver와 모터 제어

Curiosity는 driver 객체를 통해 바퀴 drive와 steering을 제어한다.
입문 단계에서는 두 가지 driver만 알면 된다.

| Driver | 제어 방식 | 사용 상황 |
|---|---|---|
| `CuriosityDCMotorControl` | DC motor torque model | 공식 Python demo의 기본 |
| `CuriositySpeedDriver` | wheel angular speed 직접 지정 | 일정 속도 실험, SCM C++ demo 참고 |

### 4.1 `CuriosityDCMotorControl`

Python demo에서 사용하는 방식이다.

```python
driver = robot.CuriosityDCMotorControl()
rover = robot.Curiosity(system)
rover.SetDriver(driver)
rover.Initialize(init_frame)
```

이 driver는 내부적으로 각 wheel driveshaft에 토크를 적용한다.
공식 API 기준 기본값은 다음과 같다.

| 값 | 기본 의미 |
|---|---|
| stall torque | wheel당 기본 `300` |
| no-load speed | wheel당 기본 `pi` rad/s |

필요하면 wheel별로 값을 바꿀 수 있다.

```python
# 설치된 PyChrono에서 wheel ID enum 노출 이름은 버전에 따라 확인 필요
driver.SetMotorStallTorque(250.0, robot.C_LF)
driver.SetMotorNoLoadSpeed(2.5, robot.C_LF)
```

> [!note] enum 이름 확인
> C++에서는 `CuriosityWheelID::C_LF`처럼 쓴다.
> PyChrono에서는 보통 `robot.C_LF`처럼 노출되지만, 설치 버전에 따라 `dir(robot)`로 확인하는 것이 안전하다.

### 4.2 조향 입력

모든 조향 바퀴에 같은 각도를 주려면 다음처럼 쓴다.

```python
steering = 0.2
driver.SetSteering(steering)
```

공식 Python demo는 시간이 1초를 지난 뒤 steering을 서서히 증가시킨다.

```python
time = system.GetChTime()

steering = 0.0
if time >= 1.0:
    steering = (time - 1.0) * 0.2

driver.SetSteering(steering)
```

> [!warning] steering 부호
> 공식 문서에는 steering 부호 설명이 버전/문맥에 따라 다르게 보일 수 있다.
> 우리 실험에서는 처음에 작은 양수/음수 값을 각각 넣고, 실제 회전 방향을 시각화로 확인한 뒤 convention을 기록하자.

---

## 5. Simulation loop에서 가장 중요한 점

Curiosity는 매 timestep마다 `rover.Update()`를 호출해야 driver 입력이 motor function과 driveshaft torque에 반영된다.

공식 API 문서에서도 `Update()`는 각 integration step 전에 호출해야 한다고 설명한다.

```python
time_step = 1e-3

while vis.Run():
    time = system.GetChTime()

    driver.SetSteering(0.0)

    # 중요: dynamics step 전에 호출
    rover.Update()

    vis.BeginScene()
    vis.Render()
    vis.EndScene()

    system.DoStepDynamics(time_step)
```

정리하면:

```text
driver 입력 설정
    ↓
rover.Update()
    ↓
system.DoStepDynamics(dt)
```

> [!important] `rover.Update()`를 빼먹으면?
> 로버가 생성은 되었지만 driver 입력이 실제 motor/steering에 반영되지 않아 기대한 주행이 나오지 않을 수 있다.

---

## 6. 지형 만들기

공식 Python demo는 `RigidTerrain` 클래스 대신, 고정된 `ChBodyEasyBox`를 ground로 사용한다.

```python
ground_mat = chrono.ChContactMaterialNSC()
ground = chrono.ChBodyEasyBox(20, 20, 1, 1000, True, True, ground_mat)
ground.SetPos(chrono.ChVector3d(0, 0, -0.5))
ground.SetFixed(True)
system.Add(ground)
```

장애물도 같은 방식으로 추가할 수 있다.

```python
obstacle = chrono.ChBodyEasyBox(0.8, 1.0, 0.3, 1000, True, True, ground_mat)
obstacle.SetPos(chrono.ChVector3d(3.0, 1.0, 0.15))
obstacle.SetFixed(True)
obstacle.EnableCollision(True)
system.Add(obstacle)
```

이 방식의 장점:

| 장점 | 설명 |
|---|---|
| 단순함 | `pychrono.vehicle` terrain 없이도 로버를 굴릴 수 있음 |
| 충돌 확인 쉬움 | ground/obstacle이 일반 body라 contact force 디버깅이 쉬움 |
| 1인 1로버 프로젝트와 연결 쉬움 | 여러 로버와 장애물을 같은 `ChSystem`에 넣기 좋음 |

나중에 더 차량다운 실험이 필요하면 `RigidTerrain`, `SCMTerrain`과 연결하는 방향으로 확장하면 된다.

---

## 7. 관찰해야 할 값

Curiosity는 chassis와 wheel 상태를 조회하는 API를 제공한다.
로버 실험에서는 아래 값부터 저장하면 좋다.

| 관찰 대상 | API | 의미 |
|---|---|---|
| chassis 위치 | `rover.GetChassisPos()` | 로버 중심 궤적 |
| chassis 회전 | `rover.GetChassisRot()` | 자세 변화 |
| chassis 속도 | `rover.GetChassisVel()` | 주행 속도 |
| chassis 가속도 | `rover.GetChassisAcc()` | 충돌/장애물 반응 |
| wheel 선속도 | `rover.GetWheelLinVel(id)` | wheel별 움직임 |
| wheel 각속도 | `rover.GetWheelAngVel(id)` | 바퀴 회전 |
| wheel 접촉힘 | `rover.GetWheelContactForce(id)` | 지면/장애물 접촉 |
| wheel 접촉토크 | `rover.GetWheelContactTorque(id)` | 접촉 토크 |
| 전체 질량 | `rover.GetRoverMass()` | 모델 규모 확인 |
| wheel 질량 | `rover.GetWheelMass()` | wheel 단위 질량 |

CSV로 저장할 최소 컬럼:

```text
time,
chassis_x, chassis_y, chassis_z,
speed,
steering,
wheel_LF_contact_force,
wheel_RF_contact_force,
wheel_LM_contact_force,
wheel_RM_contact_force,
wheel_LB_contact_force,
wheel_RB_contact_force
```

wheel contact force는 `Length()`로 크기를 저장하면 처음 분석이 쉽다.

```python
force = rover.GetWheelContactForce(robot.C_LF)
force_mag = force.Length()
```

---

## 8. 로버 충돌 실험과 연결

1인 1로버 프로젝트에서 Curiosity는 두 가지 방식으로 쓸 수 있다.

### 방식 A: 기준 로버로 그대로 사용

Curiosity를 그대로 한 대 spawn해서, 다른 팀원이 만든 로버와 충돌시키는 기준 모델로 쓴다.

```python
driver = robot.CuriosityDCMotorControl()
curiosity = robot.Curiosity(system)
curiosity.SetDriver(driver)
curiosity.Initialize(chrono.ChFramed(chrono.ChVector3d(-3, 0, 0.2), chrono.QUNIT))
```

장점:

- 이미 검증된 로버 구조를 바로 사용 가능
- wheel contact force, chassis velocity 등을 바로 기록 가능
- rocker-bogie suspension 반응을 관찰 가능

주의:

- 모델이 단순 box rover보다 무겁고 복잡하다.
- 4대 모두 복잡한 로버면 충돌 계산이 느릴 수 있다.

### 방식 B: 직접 제작 로버의 참고 구조로 사용

Curiosity 구조를 보고 직접 만든 Rover A에 다음 개념만 가져온다.

```text
chassis
  + 6 wheels
  + wheel motor
  + steering input
  + contact force logging
```

처음부터 rocker-bogie suspension을 그대로 재현하려고 하면 범위가 너무 커진다.
12주차 개인 로버 설계에서는 단순 chassis + wheel collision부터 시작하는 것이 좋다.

---

## 9. 최소 실험 아이디어

### 실험 1: Curiosity 기본 주행

목표:

```text
Curiosity가 rigid ground 위에서 정상적으로 앞으로 움직이는지 확인
```

조건:

| 항목 | 값 |
|---|---|
| system | `ChSystemNSC` |
| collision | Bullet |
| ground | fixed `ChBodyEasyBox` |
| driver | `CuriosityDCMotorControl` |
| steering | `0.0` |
| timestep | `1e-3` |

저장:

```text
time, chassis_x, chassis_y, chassis_z, speed
```

### 실험 2: Steering ramp

목표:

```text
조향 입력 증가에 따른 Curiosity 궤적 변화 확인
```

입력:

```python
time = system.GetChTime()
steering = 0.0 if time < 1.0 else (time - 1.0) * 0.2
driver.SetSteering(steering)
```

저장:

```text
time, steering, chassis_x, chassis_y, yaw_like_direction, speed
```

### 실험 3: 장애물 통과

목표:

```text
rocker-bogie suspension이 장애물에서 어떤 자세 변화를 만드는지 관찰
```

방법:

- 낮은 box obstacle 1개 추가
- wheel contact force와 chassis z 변화를 저장
- obstacle 높이를 0.1, 0.2, 0.3 m로 바꾸며 비교

### 실험 4: 충돌 이벤트 기록

목표:

```text
다른 로버 또는 장애물과 접촉했을 때 contact force threshold로 이벤트 기록
```

예시:

```python
wheel_ids = [robot.C_LF, robot.C_RF, robot.C_LM, robot.C_RM, robot.C_LB, robot.C_RB]
threshold = 10.0

for wid in wheel_ids:
    force = rover.GetWheelContactForce(wid)
    if force.Length() > threshold:
        print("contact event:", system.GetChTime(), wid, force.Length())
```

---

## 10. 자주 생기는 문제

### 로버가 안 움직임

확인할 것:

- `rover.SetDriver(driver)`를 `Initialize()` 전에 호출했는가?
- simulation loop에서 `rover.Update()`를 `DoStepDynamics()` 전에 호출했는가?
- ground와 wheel이 충돌 가능한 상태인가?
- timestep이 너무 크지 않은가?

### 로버가 이상한 방향으로 떨어짐

확인할 것:

- 중력이 `chrono.ChVector3d(0, 0, -9.81)`인지 확인
- 시각화 카메라도 `CameraVerticalDir_Z`로 맞추기

### wheel contact force가 계속 0임

가능한 원인:

- 로버가 아직 지면에 닿지 않음
- ground collision이 꺼져 있음
- wheel material 또는 collision shape 문제
- 관찰하는 wheel ID가 잘못됨

### 시뮬레이션이 느림

가능한 원인:

- RealWheel collision이 무거움
- 장애물/로버 수가 많음
- timestep이 너무 작음
- 시각화 shadow/contact drawing이 켜져 있음

해결 방향:

- 처음에는 로버 수를 1대로 테스트
- 장애물은 box primitive만 사용
- 필요하면 wheel type을 단순화하는 C++ 옵션(`SimpleWheel`, `CylWheel`) 개념을 참고
- VSG/Irrlicht visualization 옵션을 최소화

---

## 11. 발표용 핵심 요약

Curiosity 파트 발표에서는 아래 정도만 말하면 된다.

```text
Curiosity는 Chrono::Robot 내장 6륜 화성 로버 모델이다.
핵심 사용 흐름은 system 생성 -> driver 생성 -> rover 생성 -> Initialize -> 매 step rover.Update()이다.
DC motor driver를 통해 wheel driveshaft torque를 적용하고, SetSteering으로 조향 입력을 준다.
우리 프로젝트에서는 직접 로버를 만들기 전, 로버 구조/모터 제어/contact logging의 기준 예제로 사용한다.
```

---

## 참고

- [공식 API 문서: Curiosity Mars rover model](https://api.projectchrono.org/group__robot__models__curiosity.html)
- [공식 API 문서: Curiosity class](https://api.projectchrono.org/classchrono_1_1curiosity_1_1_curiosity.html)
- [공식 API 문서: CuriosityDCMotorControl](https://api.projectchrono.org/classchrono_1_1curiosity_1_1_curiosity_d_c_motor_control.html)
- Python 데모: `chrono/src/demos/python/robot/demo_ROBOT_Curiosity_Rigid.py`
- C++ 데모: `chrono/src/demos/robot/curiosity/demo_ROBOT_Curiosity_Rigid.cpp`
- C++ 데모: `chrono/src/demos/robot/curiosity/demo_ROBOT_Curiosity_SCM.cpp`
- 소스: `chrono/src/chrono_models/robot/curiosity/Curiosity.h`
- 소스: `chrono/src/chrono_models/robot/curiosity/Curiosity.cpp`
- ← [[robot/index|Robot 개요로 돌아가기]]
