# Wheeled Vehicle Overview

> Project Chrono Phase 3 - Vehicle / Wheeled Vehicle  
> 역할: 바퀴 차량(wheeled vehicle)의 기본 구조와 주요 서브시스템 이해

---

## 1. 목적

이 문서는 Chrono::Vehicle에서 **바퀴 차량(Wheeled Vehicle)** 이 어떻게 구성되는지 정리한다.  
Phase 1~2에서 학습한 강체, 조인트, 스프링-댐퍼, 회전 스프링-댐퍼 개념이 실제 차량 시스템 안에서 어떻게 결합되는지 이해하는 것이 목표이다.

최종적으로는 로버/차량이 다양한 지형 위를 주행할 때, 차량 구조와 지형 조건이 주행 성능에 어떤 영향을 주는지 분석할 수 있어야 한다.

---

## 2. Chrono::Vehicle에서 Wheeled Vehicle이란?

Chrono::Vehicle의 wheeled vehicle은 단순히 바퀴가 달린 물체가 아니라, 여러 개의 차량 서브시스템이 조립된 **멀티바디 동역학 기반 차량 모델**이다.

기본적으로 다음 요소들이 결합된다.

| 구성 요소 | 역할 |
|---|---|
| Chassis | 차량의 기준이 되는 차체 |
| Suspension | 차체와 바퀴를 연결하고 충격을 흡수 |
| Steering | 운전자 입력을 바퀴 조향각으로 변환 |
| Wheel | 타이어가 장착되는 회전 부품 |
| Tire | 지면과 접촉하여 종방향/횡방향 힘 생성 |
| Driveline | 엔진/변속기 출력을 구동 바퀴에 전달 |
| Brake | 바퀴 회전에 제동 토크 부여 |

즉, Chrono의 wheeled vehicle은 다음과 같이 볼 수 있다.

```text
Driver Input
    ↓
Powertrain / Steering / Brake
    ↓
Vehicle Subsystems
    ↓
Tire-Ground Interaction
    ↓
Vehicle Motion
```

---

## 3. 물리적 의미

바퀴 차량의 핵심은 **차체 운동**과 **타이어-지면 상호작용**이다.

차량은 엔진이나 모터에서 나온 구동 토크를 바퀴에 전달하고, 바퀴는 지면과 접촉하면서 추진력, 제동력, 횡력을 만든다.  
이 힘들이 서스펜션과 차체에 전달되면서 차량의 위치, 속도, 자세가 변한다.

Chrono에서는 이 과정을 다음 물리 요소들로 표현한다.

| 물리 요소 | Chrono에서의 표현 |
|---|---|
| 차체 질량/관성 | Rigid body |
| 바퀴 회전 | Rotational DOF |
| 서스펜션 링크 | Bodies + joints |
| 스프링/댐퍼 | TSDA, force element |
| 조향축 | Revolute / steering mechanism |
| 타이어 힘 | Tire model |
| 접촉 | Terrain + tire contact model |

따라서 Phase 1~2에서 학습한 내용이 그대로 차량 모델 내부에 들어간다.

---

## 4. Chrono 내부 구조

Chrono::Vehicle의 바퀴 차량은 보통 `ChWheeledVehicle` 또는 `WheeledVehicle` 클래스를 중심으로 구성된다.

- `ChWheeledVehicle`: wheeled vehicle의 기본 인터페이스를 제공하는 base class
- `WheeledVehicle`: JSON specification file로부터 차량을 생성할 수 있는 클래스
- Predefined vehicle model: HMMWV, Sedan, CityBus 등 미리 정의된 차량 모델

Chrono 공식 문서에 따르면 `ChWheeledVehicle`은 차량 시스템과 타이어, 운전자 모델, 지형 등 다른 시스템 사이의 인터페이스 역할을 한다.

---

## 5. 대표 예제: HMMWV

Phase 3에서 우선 분석하기 좋은 모델은 **HMMWV**이다.

HMMWV는 Chrono::Vehicle에서 제공하는 대표적인 wheeled vehicle 예제이며, 다음 요소를 포함한다.

| 요소 | HMMWV에서의 예 |
|---|---|
| 차량 종류 | 4륜 군용 차량 |
| 서스펜션 | Reduced double wishbone suspension |
| 조향 | Rack-pinion steering |
| 타이어 | 다양한 tire model 선택 가능 |
| 구동계 | Engine, transmission, driveline 포함 |

HMMWV 예제를 실행하면 기본적인 차량 생성, 지형 생성, 운전자 입력, 시각화, 시뮬레이션 루프 구조를 한 번에 확인할 수 있다.

---

## 6. 기본 코드 흐름

PyChrono에서 HMMWV 차량 예제는 대략 다음 흐름으로 구성된다.

```python
import pychrono as chrono
import pychrono.vehicle as veh
import pychrono.irrlicht as irr

# 1. Chrono data path 설정
veh.SetDataPath(...)

# 2. 차량 생성
hmmwv = veh.HMMWV_Full()

# 3. 차량 초기 위치 설정
hmmwv.SetInitPosition(...)

# 4. 차량 초기화
hmmwv.Initialize()

# 5. 지형 생성
terrain = veh.RigidTerrain(...)
terrain.Initialize()

# 6. Driver 생성
driver = veh.ChInteractiveDriverIRR(...)

# 7. Simulation loop
while vis.Run():
    time = hmmwv.GetSystem().GetChTime()

    driver.Synchronize(time)
    terrain.Synchronize(time)
    hmmwv.Synchronize(time, driver_inputs, terrain)

    driver.Advance(step_size)
    terrain.Advance(step_size)
    hmmwv.Advance(step_size)
```

핵심은 `Synchronize()`와 `Advance()`이다.

| 함수 | 의미 |
|---|---|
| `Synchronize()` | 현재 시간에서 driver, terrain, vehicle 상태를 서로 맞춤 |
| `Advance()` | 각 subsystem을 한 timestep만큼 전진시킴 |

---

## 7. Wheeled Vehicle을 이해할 때 봐야 할 핵심 서브시스템

앞으로 wheeled 파트에서는 다음 문서들을 순서대로 정리하면 좋다.

| 문서 | 내용 |
|---|---|
| `suspension.md` | 서스펜션 구조, spring-damper, double wishbone |
| `steering.md` | 조향 입력이 바퀴 각도로 변환되는 과정 |
| `tire.md` | 타이어 모델과 지면 접촉력 |
| `driveline.md` | 엔진/변속기/구동축에서 바퀴까지 동력 전달 |
| `hmmwv_structure.md` | HMMWV 예제 코드 기반 차량 구조 분석 |

---

## 8. 프로젝트와의 연결

우리 프로젝트의 최종 목표는 환경 변수에 따른 로버/차량 최적 설계이다.  
따라서 wheeled vehicle 파트에서는 단순히 차량을 실행하는 것보다, 어떤 차량 파라미터가 주행 성능에 영향을 주는지 파악하는 것이 중요하다.

예를 들어 다음 변수들이 설계 변수 또는 분석 변수로 확장될 수 있다.

| 변수 | 의미 | 성능 영향 |
|---|---|---|
| Wheel radius | 바퀴 반지름 | 장애물 통과성, 지상고, 구동 토크 |
| Tire stiffness | 타이어 강성 | 접지력, 승차감, 진동 |
| Suspension stiffness | 서스펜션 강성 | 차체 안정성, 지형 추종성 |
| Damping coefficient | 감쇠계수 | 진동 억제, 안정성 |
| Vehicle mass | 차량 질량 | 가속 성능, 침하량, 에너지 소모 |
| CG position | 무게중심 위치 | 전복 안정성, 등판 성능 |
| Drive type | 2WD/4WD/AWD | 험지 주행 성능 |

이후 terrain 파트와 결합하면 다음과 같은 분석이 가능하다.

```text
환경 변수: 지형 기울기, 마찰계수, 토양 강도, 요철 크기
차량 변수: 바퀴 크기, 질량, 서스펜션 강성, 타이어 모델
성능 지표: 속도, slip ratio, sinkage, pitch/roll 안정성, 에너지 소비
```

---

## 9. 이번 단계에서의 최소 산출물

wheeled 파트의 첫 번째 목표는 다음과 같다.

```text
1. HMMWV 예제 실행
2. 차량 구성 요소 정리
3. Chrono Vehicle simulation loop 이해
4. wheeled vehicle subsystem map 작성
```

---

## 10. 참고 자료

- Project Chrono 공식 문서: Wheeled vehicles  
  https://api.projectchrono.org/wheeled_vehicle.html

- Project Chrono 공식 문서: ChWheeledVehicle Class Reference  
  https://api.projectchrono.org/classchrono_1_1vehicle_1_1_ch_wheeled_vehicle.html

- Project Chrono 공식 문서: WheeledVehicle Class Reference  
  https://api.projectchrono.org/classchrono_1_1vehicle_1_1_wheeled_vehicle.html

- Project Chrono 공식 문서: HMMWV Vehicle Models  
  https://api.projectchrono.org/group__vehicle__models__hmmwv.html

- PyChrono Tutorial: Simulate vehicle dynamics in Python  
  https://api.projectchrono.org/tutorial_pychrono_demo_vehicle.html

- GitHub Demo: demo_VEH_HMMWV9_YUP.py  
  https://github.com/projectchrono/chrono/blob/main/src/demos/python/vehicle/demo_VEH_HMMWV9_YUP.py
