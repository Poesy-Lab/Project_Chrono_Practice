# HMMWV Structure

> Project Chrono Phase 3 - Vehicle / Wheeled Vehicle  
> 주제: Chrono HMMWV 예제 구조 분석

---

## 1. 목적

이 문서는 Chrono::Vehicle에서 제공하는 대표 바퀴 차량 모델인 **HMMWV**의 구조를 정리한다.  
앞에서 정리한 suspension, steering, tire, driveline 개념이 하나의 완성 차량 모델 안에서 어떻게 결합되는지 이해하는 것이 목표이다.

HMMWV는 Chrono Vehicle 모듈에서 가장 자주 사용되는 reference vehicle 중 하나이다.  
따라서 Phase 3에서 wheeled vehicle을 학습할 때 가장 먼저 분석하기 좋은 모델이다.

---

## 2. HMMWV란?

HMMWV는 High Mobility Multipurpose Wheeled Vehicle의 약자로, 군용 4륜 차량을 의미한다.  
Chrono::Vehicle에서는 HMMWV를 사전 정의된(pre-built) wheeled vehicle model로 제공한다.

Chrono HMMWV 모델은 단순한 하나의 body가 아니라 다음을 포함하는 assembly이다.

```text
HMMWV assembly
 ├─ Vehicle system
 ├─ Powertrain
 ├─ Driveline
 ├─ Tires
 └─ Visualization / driver / terrain interface
```

Chrono 공식 문서에 따르면 HMMWV 클래스는 concrete wheeled vehicle model, powertrain model, four tires를 포함하며, driveline, powertrain, tire type을 지정하는 wrapper 기능을 제공한다.

---

## 3. HMMWV 계층 구조

Chrono HMMWV 관련 클래스는 크게 다음과 같이 구분할 수 있다.

| 클래스 | 역할 |
|---|---|
| `HMMWV` | HMMWV assembly의 abstract base class |
| `HMMWV_Full` | full double wishbone + Pitman arm steering 기반 HMMWV |
| `HMMWV_Reduced` | reduced double wishbone + rack-pinion steering 기반 HMMWV |
| `HMMWV_Vehicle` | HMMWV vehicle base class |
| `HMMWV_VehicleFull` | full suspension vehicle system |
| `HMMWV_VehicleReduced` | reduced suspension vehicle system |
| `HMMWV_Chassis` | chassis subsystem |
| `HMMWV_Wheel` | wheel subsystem |
| `HMMWV_SimpleDriveline` | simple/kinematic driveline |
| `HMMWV_Driveline4WD` | shafts-based 4WD driveline |
| `HMMWV_RigidTire` | rigid tire model |
| `HMMWV_FialaTire` | Fiala tire model |
| `HMMWV_TMeasyTire` | TMeasy tire model |

전체 구조를 단순화하면 다음과 같다.

```text
HMMWV_Full or HMMWV_Reduced
        ↓
HMMWV assembly
        ↓
Vehicle + Powertrain + Tires
        ↓
Subsystems
        ├─ Chassis
        ├─ Suspension
        ├─ Steering
        ├─ Wheels
        ├─ Brakes
        ├─ Driveline
        └─ Tires
```

---

## 4. HMMWV_Full과 HMMWV_Reduced의 차이

Chrono HMMWV에는 대표적으로 `HMMWV_Full`과 `HMMWV_Reduced`가 있다.

| 항목 | HMMWV_Full | HMMWV_Reduced |
|---|---|---|
| Suspension | Full double wishbone | Reduced double wishbone |
| Control arm 표현 | rigid body로 표현 | distance constraint로 단순화 |
| Steering | Pitman arm steering | Rack-pinion steering |
| 물리 상세도 | 높음 | 낮음 |
| 계산 비용 | 큼 | 작음 |
| 추천 용도 | 구조 이해, 상세 동역학 | 빠른 주행 실험, 기본 학습 |

공식 문서 기준으로:

```text
HMMWV_Full:
full double wishbone suspensions + Pitman arm steering mechanism

HMMWV_Reduced:
reduced double wishbone suspensions + rack-pinion steering mechanism
```

따라서 처음에는 `HMMWV_Reduced`로 실행 안정성을 확인하고, 이후 `HMMWV_Full`로 넘어가 상세 구조를 분석하는 방식이 좋다.

---

## 5. HMMWV_Full 구조

`HMMWV_Full`은 다음 특징을 가진다.

```text
HMMWV_Full
 ├─ Full double wishbone suspension
 │   ├─ upper control arm: rigid body
 │   ├─ lower control arm: rigid body
 │   └─ spring-damper
 ├─ Pitman arm steering
 ├─ 4 wheels
 ├─ selectable tire model
 ├─ powertrain
 └─ driveline
```

Full 모델은 control arm을 실제 rigid body로 모델링하므로, Phase 2에서 학습한 rigid body, joint, TSDA 개념과 직접 연결된다.

---

## 6. HMMWV_Reduced 구조

`HMMWV_Reduced`는 full 모델보다 계산을 줄이기 위해 suspension을 단순화한 모델이다.

```text
HMMWV_Reduced
 ├─ Reduced double wishbone suspension
 │   ├─ control arm rigid body 제거
 │   └─ distance constraint로 대체
 ├─ Rack-pinion steering
 ├─ 4 wheels
 ├─ selectable tire model
 ├─ powertrain
 └─ driveline
```

Reduced 모델은 빠른 시뮬레이션과 제어 알고리즘 테스트에 적합하다.  
특히 나중에 강화학습 또는 반복 최적화를 수행할 경우 계산량이 중요하므로 reduced model이 유용할 수 있다.

---

## 7. HMMWV Python 예제 구조

PyChrono tutorial에는 HMMWV 차량을 Python에서 실행하는 예제가 제공된다.  
또한 `demo_VEH_HMMWV9_YUP.py`는 Y축을 수직축으로 사용하는 world frame 예제이며, reduced-order HMMWV 모델을 사용한다.

기본 흐름은 다음과 같다.

```python
import pychrono as chrono
import pychrono.vehicle as veh
import pychrono.irrlicht as irr

# 1. Set data paths
chrono.SetChronoDataPath(...)
veh.SetDataPath(...)

# 2. Create vehicle
hmmwv = veh.HMMWV_Reduced()

# 3. Set initial position
hmmwv.SetInitPosition(...)

# 4. Set vehicle options
hmmwv.SetContactMethod(...)
hmmwv.SetChassisCollisionType(...)
hmmwv.SetTireType(...)

# 5. Initialize vehicle
hmmwv.Initialize()

# 6. Create terrain
terrain = veh.RigidTerrain(...)
terrain.Initialize()

# 7. Create driver
driver = veh.ChInteractiveDriverIRR(...)
driver.Initialize()

# 8. Create visualization
vis = veh.ChWheeledVehicleVisualSystemIrrlicht()
vis.AttachVehicle(hmmwv.GetVehicle())

# 9. Simulation loop
while vis.Run():
    time = hmmwv.GetSystem().GetChTime()

    driver_inputs = driver.GetInputs()

    driver.Synchronize(time)
    terrain.Synchronize(time)
    hmmwv.Synchronize(time, driver_inputs, terrain)
    vis.Synchronize(time, driver_inputs)

    driver.Advance(step_size)
    terrain.Advance(step_size)
    hmmwv.Advance(step_size)
    vis.Advance(step_size)
```

---

## 8. Simulation Loop 핵심

HMMWV 예제에서 가장 중요한 구조는 `Synchronize()`와 `Advance()`의 반복이다.

```text
Synchronize:
    현재 시간에서 subsystem 간 정보 교환

Advance:
    각 subsystem을 timestep만큼 시간 적분
```

흐름은 다음과 같이 이해하면 된다.

```text
Driver input 생성
        ↓
Vehicle이 driver input과 terrain 정보 수신
        ↓
Steering / powertrain / driveline / tire update
        ↓
Vehicle dynamics 계산
        ↓
Visualization update
        ↓
다음 timestep
```

즉, 사용자가 직접 suspension, steering, tire를 각각 업데이트하는 것이 아니라, HMMWV vehicle 객체가 내부 subsystem을 통합적으로 관리한다.

---

## 9. HMMWV에서 Driver Input의 역할

HMMWV 예제에서 driver input은 일반적으로 다음 세 가지로 구성된다.

| 입력 | 의미 | 범위 |
|---|---|---|
| `m_steering` | 조향 입력 | -1 ~ 1 |
| `m_throttle` | 가속 입력 | 0 ~ 1 |
| `m_braking` | 제동 입력 | 0 ~ 1 |

이 입력은 simulation loop에서 vehicle에 전달된다.

```python
driver_inputs = driver.GetInputs()
hmmwv.Synchronize(time, driver_inputs, terrain)
```

이후 내부적으로:

```text
steering input → steering subsystem
throttle input → powertrain/driveline subsystem
braking input → brake subsystem
```

으로 전달된다.

---

## 10. HMMWV와 Terrain의 연결

HMMWV 자체는 차량 모델이고, 실제 주행은 terrain과 연결될 때 완성된다.

대표 terrain은 다음과 같다.

| Terrain | 의미 |
|---|---|
| `RigidTerrain` | 평면/경사면 같은 강체 지형 |
| Height map terrain | 높이맵 기반 요철 지형 |
| `SCMTerrain` | 변형 가능한 흙/모래 지형 |
| Granular terrain | 입자 기반 지형 |

Phase 3 초반에는 다음 순서가 좋다.

```text
1. HMMWV + RigidTerrain
2. HMMWV + 경사 RigidTerrain
3. HMMWV + Height map terrain
4. HMMWV + SCMTerrain
```

로버 최적 설계 관점에서는 최종적으로 `SCMTerrain`과 결합하는 것이 중요하다.

---

## 11. HMMWV에서 선택 가능한 Tire Model

HMMWV는 여러 tire model을 사용할 수 있다.

| Tire model | 특징 |
|---|---|
| Rigid tire | 단순하고 빠름 |
| Fiala tire | slip 기반 handling tire |
| Pacejka tire | Magic Formula 기반 경험식 모델 |
| TMeasy tire | 다양한 주행 조건에서 사용 가능한 semi-empirical 모델 |
| FEA tire | 타이어 변형까지 고려하는 정밀 모델 |

초기 실습에서는 다음 순서를 추천한다.

```text
Rigid tire → TMeasy tire → Fiala/Pacejka → FEA tire
```

로버 프로젝트에서는 계산량과 지형 상호작용을 고려하면 Rigid 또는 TMeasy를 먼저 사용하는 것이 현실적이다.

---

## 12. HMMWV에서 선택 가능한 Driveline / Powertrain

HMMWV 모델에는 simple model과 shafts-based model이 존재한다.

| 시스템 | 단순 모델 | 상세 모델 |
|---|---|---|
| Powertrain | simple engine / simple map | shafts-based engine + transmission |
| Driveline | simple kinematic driveline | shafts-based 4WD driveline |

단순 모델은 빠르고 안정적이며, 상세 모델은 물리 구조를 더 잘 반영한다.

Phase 3에서는 먼저 단순 모델로 전체 흐름을 이해하고, 이후 필요하면 shafts-based model로 넘어간다.

---

## 13. 코드에서 확인할 포인트

HMMWV 예제 코드를 읽을 때는 모든 줄을 세세히 보려 하지 말고, 다음 부분을 중심으로 보면 된다.

```text
1. import 부분
2. data path 설정
3. vehicle 생성
4. vehicle option 설정
5. terrain 생성
6. driver 생성
7. visualization 생성
8. simulation loop
9. Synchronize / Advance 순서
10. output 또는 logging 부분
```

특히 다음 변수 이름을 찾으면 구조 파악이 쉽다.

```text
hmmwv
terrain
driver
vis
driver_inputs
step_size
render_step_size
```

---

## 14. Phase 3 실습용 최소 코드 구조

프로젝트용으로는 공식 예제를 그대로 복사하기보다, 다음처럼 최소 구조로 줄여서 별도 파일을 만드는 것이 좋다.

```text
notebooks/phase3/chrono4_hmmwv_basic.ipynb
or
scripts/phase3/hmmwv_basic.py
```

구성:

```text
1. Import
2. Parameter setting
3. HMMWV creation
4. Terrain creation
5. Driver setting
6. Simulation loop
7. CSV logging
8. Plot
```

---

## 15. CSV 저장 목표

처음부터 모든 subsystem 정보를 저장하려고 하면 복잡해진다.  
Phase 3 초기에는 다음 값만 저장해도 충분하다.

```text
time, x, y, z, vx, vy, vz, speed, roll, pitch, yaw,
steering, throttle, braking
```

이후 확장:

```text
wheel angular speed
wheel torque
tire slip ratio
tire force
suspension travel
engine torque
```

---

## 16. 프로젝트와의 연결

HMMWV는 최종 로버 모델은 아니지만, Chrono Vehicle subsystem을 이해하기 위한 reference model로 매우 유용하다.

프로젝트 연결은 다음과 같다.

```text
HMMWV 분석
    ↓
wheeled vehicle subsystem 이해
    ↓
terrain interaction 이해
    ↓
로버 모델 설계 변수 정의
    ↓
환경 변수별 주행 데이터 수집
    ↓
최적 설계 / AI 기반 분석
```

즉, HMMWV는 최종 결과물이 아니라 **로버 시뮬레이터를 만들기 위한 학습용 표준 모델**이다.

---

## 17. HMMWV 기반 실험 아이디어

### 실험 1: Flat terrain 주행

```text
Vehicle: HMMWV_Reduced
Terrain: flat RigidTerrain
Input: constant throttle
Output: speed, position, yaw
```

목표:

```text
차량이 정상적으로 전진하는지 확인
```

---

### 실험 2: Steering response

```text
Vehicle: HMMWV_Reduced
Terrain: flat RigidTerrain
Input: constant throttle + step steering
Output: x-y trajectory, yaw rate
```

목표:

```text
steering input에 따른 선회 반응 확인
```

---

### 실험 3: Tire model comparison

```text
Vehicle: HMMWV
Terrain: flat RigidTerrain
Tire: Rigid, TMeasy, Fiala
Output: speed, acceleration, path
```

목표:

```text
타이어 모델이 차량 거동에 미치는 영향 확인
```

---

### 실험 4: Terrain friction comparison

```text
Vehicle: HMMWV
Terrain friction: 0.3, 0.6, 0.9
Input: same throttle
Output: speed, slip, distance
```

목표:

```text
지형 마찰계수 변화에 따른 주행 성능 비교
```

---

## 18. 핵심 정리

```text
HMMWV는 Chrono::Vehicle의 대표적인 pre-built wheeled vehicle model이다.
HMMWV_Full은 full double wishbone suspension과 Pitman arm steering을 사용한다.
HMMWV_Reduced는 reduced double wishbone suspension과 rack-pinion steering을 사용한다.
HMMWV 객체는 vehicle, powertrain, tires를 포함하는 assembly이다.
Simulation loop의 핵심은 Synchronize()와 Advance()이다.
Phase 3에서는 HMMWV를 통해 vehicle subsystem 구조와 terrain interaction을 익히는 것이 목표이다.
```

---

## 19. 참고 자료

- Project Chrono 공식 문서: HMMWV vehicle models  
  https://api.projectchrono.org/group__vehicle__models__hmmwv.html

- Project Chrono 공식 문서: HMMWV Class Reference  
  https://api.projectchrono.org/classchrono_1_1vehicle_1_1hmmwv_1_1_h_m_m_w_v.html

- Project Chrono 공식 문서: HMMWV_VehicleFull Class Reference  
  https://api.projectchrono.org/9.0.0/classchrono_1_1vehicle_1_1hmmwv_1_1_h_m_m_w_v___vehicle_full.html

- Project Chrono 공식 문서: PyChrono Vehicle Tutorial  
  https://api.projectchrono.org/tutorial_pychrono_demo_vehicle.html

- Project Chrono 공식 문서: PyChrono Tutorials Table of Contents  
  https://api.projectchrono.org/tutorial_table_of_content_pychrono.html

- GitHub Demo: demo_VEH_HMMWV9_YUP.py  
  https://github.com/projectchrono/chrono/blob/main/src/demos/python/vehicle/demo_VEH_HMMWV9_YUP.py
