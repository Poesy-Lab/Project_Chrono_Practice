# Driveline

> Project Chrono Phase 3 - Vehicle / Wheeled Vehicle  
> 주제: 동력 전달계(driveline)와 바퀴 토크 분배 구조

---

## 1. 정의

드라이브라인(driveline)은 **엔진 또는 모터에서 생성된 동력을 구동 바퀴까지 전달하는 차량 서브시스템**이다.

차량이 움직이기 위해서는 powertrain에서 생성된 토크가 바퀴로 전달되어야 한다.  
이때 단순히 하나의 축으로 바로 연결되는 것이 아니라, 실제 차량에서는 구동축, 기어, 차동장치, transfer case, clutch 등의 요소를 거쳐 각 바퀴에 토크가 분배된다.

Chrono::Vehicle에서 driveline은 다음 역할을 한다.

| 역할 | 설명 |
|---|---|
| 동력 전달 | powertrain 출력 토크를 구동축으로 전달 |
| 토크 분배 | 앞/뒤 차축 또는 좌/우 바퀴에 토크 분배 |
| 차동 기능 | 좌우 바퀴의 회전속도 차이를 허용 |
| 구동 방식 표현 | 2WD, 4WD, AWD, XWD 표현 |
| 기계 관성 반영 | shaft inertia, differential inertia 등 포함 가능 |

---

## 2. Powertrain과 Driveline의 차이

Chrono::Vehicle에서는 powertrain과 driveline을 구분해서 생각하는 것이 중요하다.

```text
Powertrain:
    engine / motor + torque converter + transmission

Driveline:
    driveshaft + transfer case + differential + axle shafts
```

즉, powertrain은 **토크를 생성하고 변속하는 시스템**이고, driveline은 그 토크를 **어느 바퀴에 어떻게 나누어 전달할지 결정하는 시스템**이다.

전체 흐름은 다음과 같다.

```text
Driver throttle input
        ↓
Engine / Motor
        ↓
Transmission
        ↓
Driveline
        ↓
Driven wheels
        ↓
Tire-ground force
        ↓
Vehicle motion
```

---

## 3. 물리적 의미

드라이브라인은 차량의 추진력 생성에 직접 연결된다.

엔진 또는 모터가 출력 토크를 만들면, 이 토크는 기어비와 구동계 구조에 따라 바퀴 토크로 변환된다.

```text
wheel torque ≈ engine torque × gear ratio × driveline efficiency
```

바퀴 토크가 커지면 타이어 접촉점에서 지면을 뒤로 밀고, 그 반작용으로 차량은 앞으로 나아간다.

```text
longitudinal tire force ≈ wheel torque / tire radius
```

단, 실제 추진력은 타이어-지면 마찰 한계, slip ratio, normal load, terrain deformability에 의해 제한된다.

---

## 4. Chrono::Vehicle의 Driveline Subsystem

Chrono 공식 문서 기준으로 wheeled vehicle은 chassis subsystem, driveline subsystem, 여러 axle로 구성된다.  
각 axle은 앞쪽부터 번호가 매겨지며, driveline은 특정 axle들을 driven axle로 연결한다.

Chrono::Vehicle의 driveline subsystem은 크게 다음 방식으로 나눌 수 있다.

| 모델 | 설명 |
|---|---|
| 4WD shafts-based driveline | Chrono 1-D shaft 요소로 상세 구동계 모델링 |
| 2WD shafts-based driveline | 한 개 axle만 구동하는 shafts-based 모델 |
| 4WD kinematic driveline | 단순 torque split 기반 4WD 모델 |
| XWD kinematic driveline | 여러 개의 구동 axle을 처리할 수 있는 일반화 모델 |

---

## 5. Shafts-Based Driveline

Shafts-based driveline은 Chrono의 1-D shaft 요소를 사용하여 구동계를 물리적으로 모델링한다.

공식 문서에서는 4WD shafts-based drivetrain이 다음 요소들을 사용한다고 설명한다.

| Chrono 요소 | 물리적 의미 |
|---|---|
| `ChShaft` | 회전축 |
| `ChShaftsPlanetary` | differential |
| `ChShaftsGearboxAngled` | conical gear |
| `ChShaftsClutch` | differential locking clutch |

이 모델은 shaft inertia, differential box inertia, gear ratio, locking limit 등을 설정할 수 있다.

개념적으로는 다음 구조이다.

```text
Transmission output
        ↓
Central driveshaft
        ↓
Transfer / central differential
   ┌────┴────┐
Front shaft  Rear shaft
   ↓             ↓
Front diff    Rear diff
   ↓             ↓
Front wheels  Rear wheels
```

---

## 6. 4WD Shafts-Based Driveline

4WD shafts-based driveline은 앞/뒤 axle을 모두 구동하는 모델이다.

예시 JSON 구조는 다음 항목을 포함한다.

```json
{
  "Name": "HMMWV AWD Driveline",
  "Type": "Driveline",
  "Template": "ShaftsDriveline4WD",

  "Shaft Inertia": {
    "Driveshaft": 0.5,
    "Front Driveshaft": 0.5,
    "Rear Driveshaft": 0.5,
    "Central Differential Box": 0.6,
    "Front Differential Box": 0.6,
    "Rear Differential Box": 0.6
  },

  "Gear Ratio": {
    "Front Conical Gear": 0.2,
    "Rear Conical Gear": 0.2
  },

  "Axle Differential Locking Limit": 100,
  "Central Differential Locking Limit": 100
}
```

여기서 중요한 파라미터는 다음과 같다.

| 파라미터 | 의미 |
|---|---|
| Driveshaft inertia | 구동축 회전 관성 |
| Differential box inertia | 차동장치 회전 관성 |
| Gear ratio | 토크/속도 변환 비율 |
| Differential locking limit | 차동 제한 토크 |

이 모델은 실제 구동축 동역학과 차동장치 효과를 더 상세히 표현할 수 있지만, 단순 모델보다 계산량이 크다.

---

## 7. 2WD Shafts-Based Driveline

2WD shafts-based driveline은 특정 axle 하나만 구동하는 모델이다.  
앞 axle을 연결하면 FWD, 뒤 axle을 연결하면 RWD로 해석할 수 있다.

개념 구조는 다음과 같다.

```text
Transmission output
        ↓
Driveshaft
        ↓
Axle differential
   ┌────┴────┐
Left wheel  Right wheel
```

2WD 모델은 다음 상황에서 유용하다.

| 사용 상황 | 예 |
|---|---|
| 단순 차량 모델 | 후륜구동 승용차 |
| 계산량 감소 | 빠른 테스트 |
| 구동 방식 비교 | 2WD vs 4WD 성능 비교 |
| 로버 설계 실험 | 일부 바퀴만 구동하는 구조 분석 |

---

## 8. Kinematic Driveline

Kinematic driveline은 shafts-based driveline보다 단순한 모델이다.  
구동축과 differential을 상세한 1-D shaft 요소로 표현하기보다는, 정해진 torque split 규칙에 따라 토크를 분배한다.

Chrono 문서 기준으로 `ChSimpleDriveline`은 4WD driveline을 모델링할 수 있으며, 일정한 front/rear torque split과 간단한 Torsen limited-slip differential 모델을 사용한다.

예시 구조:

```json
{
  "Name": "HMMWV 4WD Driveline",
  "Type": "Driveline",
  "Template": "SimpleDriveline",
  "Front Torque Fraction": 0.5,
  "Front Differential Max Bias": 2.0,
  "Rear Differential Max Bias": 2.0,
  "Front Conical Gear Ratio": 0.25,
  "Rear Conical Gear Ratio": 0.25
}
```

여기서:

| 파라미터 | 의미 |
|---|---|
| Front Torque Fraction | 전체 토크 중 앞 axle로 가는 비율 |
| Differential Max Bias | 좌우 바퀴 간 최대 토크 bias |
| Conical Gear Ratio | axle gear ratio |

---

## 9. Shafts-Based vs Kinematic 비교

| 항목 | Shafts-Based Driveline | Kinematic Driveline |
|---|---|---|
| 모델링 방식 | 1-D shaft 동역학 기반 | torque split 규칙 기반 |
| 표현 가능 요소 | shaft inertia, differential, clutch | 단순 torque distribution |
| 계산 비용 | 상대적으로 큼 | 작음 |
| 물리 상세도 | 높음 | 낮음 |
| 초기 학습 적합도 | 중간 | 높음 |
| 로버 최적화 초기 실험 | 필요 시 사용 | 우선 추천 |

Phase 3 초반에는 kinematic 또는 simple driveline을 먼저 이해하고, 필요할 때 shafts-based model로 넘어가는 것이 좋다.

---

## 10. HMMWV와 Driveline

Chrono의 HMMWV 모델은 여러 구동계 옵션을 제공한다.  
일반적으로 HMMWV는 4륜 구동 차량으로 해석할 수 있으며, 예제에서는 차량 타입에 따라 simple driveline 또는 shafts-based driveline을 선택할 수 있다.

PyChrono 예제에서는 보통 다음 흐름으로 차량 객체 내부에서 driveline이 설정된다.

```python
hmmwv = veh.HMMWV_Full()
hmmwv.SetInitPosition(chrono.ChCoordsysd(initLoc, initRot))
hmmwv.Initialize()
```

일부 예제 또는 JSON 기반 vehicle에서는 driveline specification file을 통해 구동계 파라미터가 정의된다.

예를 들어 JSON 기반 차량 구성에서는 다음처럼 차량 파일 내부에서 subsystem을 참조할 수 있다.

```text
Vehicle JSON
 ├─ Chassis JSON
 ├─ Suspension JSON
 ├─ Steering JSON
 ├─ Driveline JSON
 ├─ Wheel JSON
 └─ Tire JSON
```

---

## 11. Simulation Loop에서 Driveline의 역할

Chrono Vehicle simulation loop에서 driveline은 powertrain과 wheel 사이에 위치한다.

```text
1. Driver가 throttle input 제공
2. Powertrain이 engine torque 계산
3. Transmission이 torque/speed 변환
4. Driveline이 driven axle/wheel에 torque 분배
5. Wheel angular velocity 변화
6. Tire가 지면과 접촉하여 longitudinal force 생성
7. Vehicle이 가속 또는 감속
```

사용자는 보통 driveline을 직접 `Advance()`하지 않고, vehicle 객체의 `Synchronize()`와 `Advance()`를 통해 전체 차량 subsystem을 업데이트한다.

```python
driver_inputs = driver.GetInputs()

hmmwv.Synchronize(time, driver_inputs, terrain)
hmmwv.Advance(step_size)
```

---

## 12. Driveline에서 관찰해야 할 물리량

로버/차량 최적설계에서 driveline 관련으로 관찰하면 좋은 물리량은 다음과 같다.

| 물리량 | 의미 |
|---|---|
| Engine speed | 엔진 회전속도 |
| Engine torque | 엔진 출력 토크 |
| Transmission gear | 현재 기어 |
| Driveshaft angular speed | 구동축 회전속도 |
| Wheel angular speed | 각 바퀴 회전속도 |
| Wheel torque | 각 바퀴에 전달된 토크 |
| Slip ratio | wheel torque가 실제 추진력으로 변환되는 정도 |
| Vehicle speed | 실제 차량 속도 |
| Energy consumption | 동력 효율 평가 |

Phase 3 초반에는 모든 내부 구동계 값을 직접 얻기 어려울 수 있으므로, 우선 vehicle speed, wheel angular speed, throttle input을 기록하고 이후 확장하는 방식이 좋다.

---

## 13. 프로젝트 설계 변수로의 확장

드라이브라인은 로버 최적 설계에서 매우 중요한 설계 변수이다.

| 설계 변수 | 영향 |
|---|---|
| Drive type | 2WD, 4WD, AWD에 따른 험지 주행성 |
| Torque split | 앞/뒤 axle traction 분배 |
| Gear ratio | 가속력, 최고속도, 등판성 |
| Differential locking | 험지에서 한쪽 바퀴 헛돎 억제 |
| Shaft inertia | 동력 응답성 |
| Motor placement | in-wheel motor vs central motor |
| Wheel torque limit | slip과 에너지 소비 |

특히 로버 프로젝트에서는 다음 질문이 중요하다.

```text
같은 지형 조건에서 2WD와 4WD의 주행 성능 차이는?
모래 지형에서 differential locking이 slip ratio를 줄이는가?
기어비를 키우면 등판 성능은 좋아지지만 최고속도는 얼마나 감소하는가?
토크를 크게 주면 항상 좋은가, 아니면 slip과 sinkage가 증가하는가?
```

---

## 14. Terrain과의 연결

드라이브라인만 보면 “토크를 많이 주면 잘 간다”고 생각하기 쉽다.  
하지만 실제 험지에서는 토크가 커질수록 바퀴가 더 많이 헛돌 수 있다.

```text
높은 wheel torque
        ↓
타이어 접촉력 한계 초과
        ↓
slip ratio 증가
        ↓
terrain shear failure 또는 sinkage 증가
        ↓
실제 차량 속도 감소
```

따라서 로버 최적설계에서는 driveline과 tire, terrain을 함께 봐야 한다.

```text
Driveline torque
    + Tire model
    + Terrain model
    = Mobility performance
```

---

## 15. 간단한 실험 아이디어

### 실험 1: Throttle 변화

```text
Terrain: flat RigidTerrain
Vehicle: HMMWV
Throttle: 0.2, 0.5, 1.0
Output: speed, acceleration, wheel angular speed
```

목표:

```text
구동 입력이 차량 속도와 wheel speed에 미치는 영향 확인
```

---

### 실험 2: 2WD vs 4WD 비교

```text
Terrain: slope or low-friction terrain
Vehicle: same chassis
Driveline: 2WD, 4WD
Output: speed, slip ratio, climb success/failure
```

목표:

```text
구동 방식이 험지 주행 성능에 미치는 영향 확인
```

---

### 실험 3: Gear ratio 변화

```text
Terrain: slope
Gear ratio: low, medium, high
Output: acceleration, max speed, climb ability
```

목표:

```text
기어비가 등판성/최고속도 trade-off에 미치는 영향 이해
```

---

## 16. CSV 저장 예시

드라이브라인 분석을 위해 저장하면 좋은 데이터는 다음과 같다.

```text
time, throttle, braking,
x, y, z, speed, acceleration,
wheel_omega_FL, wheel_omega_FR, wheel_omega_RL, wheel_omega_RR,
estimated_slip_FL, estimated_slip_FR, estimated_slip_RL, estimated_slip_RR
```

추후 가능하면 다음 값도 추가한다.

```text
engine_speed, engine_torque, gear, wheel_torque_FL, wheel_torque_FR, wheel_torque_RL, wheel_torque_RR
```

---

## 17. 핵심 정리

```text
Driveline은 powertrain에서 나온 토크를 구동 바퀴로 전달하고 분배하는 subsystem이다.
Chrono는 shafts-based driveline과 kinematic driveline을 제공한다.
Shafts-based model은 ChShaft, differential, clutch 등을 이용해 더 물리적으로 상세하다.
Simple driveline은 front/rear torque split과 제한 차동장치를 단순하게 표현한다.
로버 프로젝트에서는 drive type, torque split, gear ratio가 주행 성능과 slip에 큰 영향을 준다.
```

---

## 18. 참고 자료

- Project Chrono 공식 문서: Driveline models  
  https://api.projectchrono.org/wheeled_driveline.html

- Project Chrono 공식 문서: Overview of vehicle modeling and simulation  
  https://api.projectchrono.org/vehicle_overview.html

- Project Chrono 공식 문서: Wheeled vehicles  
  https://api.projectchrono.org/wheeled_vehicle.html

- Project Chrono 공식 문서: ChSimpleDriveline Class Reference  
  https://api.projectchrono.org/9.0.0/classchrono_1_1vehicle_1_1_ch_simple_driveline.html

- Project Chrono 공식 문서: Chrono::Vehicle Reference Manual  
  https://api.projectchrono.org/manual_vehicle.html
