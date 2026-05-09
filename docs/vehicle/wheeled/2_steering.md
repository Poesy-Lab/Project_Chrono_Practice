# Steering

> Project Chrono Phase 3 - Vehicle / Wheeled Vehicle  
> 주제: 바퀴 차량의 조향(steering) 시스템과 Chrono 모델링 방식

---

## 1. 정의

조향 시스템(steering system)은 **운전자 입력을 바퀴의 조향각으로 변환하는 차량 서브시스템**이다.  
자동차나 로버가 원하는 방향으로 이동하기 위해서는 앞바퀴 또는 일부 바퀴의 방향을 바꿔야 한다. 이때 운전자의 steering input이 링크, 조인트, 랙, 피니언 등의 기계 구조를 통해 바퀴 방향 변화로 전달된다.

Chrono::Vehicle에서 steering은 차량의 독립적인 subsystem으로 정의되며, suspension, wheel, tire와 연결되어 차량의 횡방향 운동을 만든다.

---

## 2. 물리적 의미

차량이 직진할 때 바퀴의 진행 방향은 차량의 longitudinal axis와 거의 일치한다.  
하지만 steering input이 들어오면 바퀴가 회전하여 타이어의 진행 방향과 실제 속도 방향 사이에 차이가 생긴다. 이 차이로 인해 타이어에는 횡력이 발생하고, 이 횡력이 차량을 회전시킨다.

흐름은 다음과 같다.

```text
Driver steering input
        ↓
Steering mechanism
        ↓
Wheel steer angle
        ↓
Tire slip angle
        ↓
Lateral tire force
        ↓
Yaw motion / turning
```

즉, steering은 단순히 바퀴를 돌리는 장치가 아니라 차량의 yaw motion과 경로 추종 성능을 결정하는 핵심 subsystem이다.

---

## 3. Chrono::Vehicle의 Steering Subsystem

Chrono::Vehicle에서 steering subsystem은 `ChSteering`을 기본 클래스로 하며, 여러 steering mechanism template이 제공된다.

대표적인 클래스는 다음과 같다.

| 클래스 | 의미 |
|---|---|
| `ChSteering` | steering subsystem의 base class |
| `ChPitmanArm` | Pitman arm steering base class |
| `ChPitmanArmShafts` | compliant steering column을 포함한 Pitman arm steering |
| `ChRackPinion` | rack-pinion steering base class |
| `ChRotaryArm` | rotary arm / toe bar steering |
| `PitmanArm` | JSON 기반 Pitman arm steering |
| `RackPinion` | JSON 기반 rack-pinion steering |

Chrono 공식 문서에서 steering subsystem은 wheeled vehicle subsystem 중 하나로 분류되며, Pitman arm, Rack-pinion, Rotary arm 모델이 제공된다.

---

## 4. 좌표계 기준

Chrono::Vehicle의 steering subsystem은 ISO 차량 좌표계를 기준으로 모델링된다.

```text
X axis: 차량 전방
Y axis: 차량 좌측
Z axis: 위쪽
```

따라서 양의 조향 방향, 링크 위치, joint 방향은 이 좌표계를 기준으로 해석해야 한다.

---

## 5. Pitman Arm Steering

Pitman arm steering은 조향 입력을 회전 링크 구조를 통해 steering link로 전달하는 방식이다.  
Chrono 공식 문서에서는 Pitman arm mechanism을 **four-bar linkage** 구조로 설명한다.

기본 구조는 다음과 같다.

```text
Chassis
  ├─ Pitman Arm
  ├─ Idler Arm
  └─ Steering Link
          ├─ Left tie rod
          └─ Right tie rod
```

Chrono의 Pitman arm steering에서:

- Pitman arm body는 chassis에 revolute joint로 연결된다.
- Pitman arm body는 steering link와 universal joint로 연결된다.
- Idler arm은 composite revolute-spherical joint로 단순화될 수 있다.
- Driver steering input은 Pitman arm의 revolute joint 각도를 제어한다.

즉, 운전자 입력은 먼저 Pitman arm의 회전으로 바뀌고, 이 회전이 steering link의 움직임으로 전달되어 좌우 바퀴의 조향각을 만든다.

![[Pasted image 20260508195643.png|433]]

![[Pasted image 20260508195701.png|438]]

![[Pasted image 20260508195718.png|435]]
---

## 6. Rack-Pinion Steering

Rack-pinion steering은 승용차에서 흔히 사용하는 조향 방식이다.  
Pinion gear의 회전을 rack의 직선 운동으로 바꾸고, rack이 tie rod를 밀거나 당겨 바퀴를 조향한다.

Chrono의 Rack-pinion steering template은 기구학적 모델로 표현된다.  
공식 문서 기준으로 steering link body는 prismatic joint를 통해 chassis에 연결되고, rack displacement는 다음 식으로 계산된다.

```text
d = r * (alpha_max * s)
```

여기서:

| 기호 | 의미 |
|---|---|
| d | rack displacement |
| r | pinion radius |
| alpha_max | maximum pinion angle |
| s | driver steering input, -1 ≤ s ≤ 1 |

즉, driver steering input `s`가 -1이면 최대 좌회전 방향, +1이면 최대 우회전 방향의 rack displacement가 생성된다.  
이 변위가 steering link translation을 제어하고, 결과적으로 바퀴 조향각을 만든다.

![[Pasted image 20260508195742.png|363]]

![[Pasted image 20260508195750.png|365]]

![[Pasted image 20260508195800.png|365]]
---

## 7. Pitman Arm vs Rack-Pinion 비교

| 항목 | Pitman Arm | Rack-Pinion |
|---|---|---|
| 기본 원리 | 회전 링크 기반 four-bar linkage | pinion 회전 → rack 직선운동 |
| 주요 부품 | Pitman arm, idler arm, steering link | rack, pinion, tie rod |
| Chrono 모델 | `ChPitmanArm`, `PitmanArm` | `ChRackPinion`, `RackPinion` |
| 입력 변환 | steering input → arm angle | steering input → rack displacement |
| 장점 | 대형/상용/군용 차량 구조 표현에 적합 | 단순하고 직관적인 승용차 모델 |
| HMMWV 관련성 | HMMWV_Full에 사용 | HMMWV JSON 예제에서 사용 가능 |

HMMWV_Full 공식 문서에서는 full double wishbone suspension과 Pitman arm steering mechanism을 사용한다고 설명한다.  
따라서 HMMWV를 기준으로 분석할 때는 Pitman arm steering을 우선 이해하는 것이 좋다.

---

## 8. HMMWV에서의 Steering

Chrono HMMWV 계열 모델에서는 steering subsystem이 차량 객체 내부에 포함되어 있다.

예제 코드에서는 사용자가 steering mechanism을 직접 만들지 않고, HMMWV 객체를 생성하고 초기화하면 내부적으로 steering subsystem이 구성된다.

```python
hmmwv = veh.HMMWV_Full()
hmmwv.SetInitPosition(chrono.ChCoordsysd(initLoc, initRot))
hmmwv.Initialize()
```

이후 운전자 입력은 driver subsystem에서 생성된다.

```python
driver_inputs = driver.GetInputs()
```

그리고 simulation loop에서 vehicle로 전달된다.

```python
hmmwv.Synchronize(time, driver_inputs, terrain)
hmmwv.Advance(step_size)
```

이때 `driver_inputs.m_steering` 값이 steering subsystem으로 전달되어 바퀴의 조향 상태에 영향을 준다.

---

## 9. Simulation Loop에서 Steering의 역할

Chrono Vehicle simulation loop에서 steering은 보통 다음 순서로 작동한다.

```text
1. Driver subsystem이 steering input 생성
2. Vehicle subsystem이 driver input을 받음
3. Steering subsystem이 입력을 steering link motion으로 변환
4. Suspension/wheel subsystem이 조향된 wheel orientation 계산
5. Tire model이 slip angle과 lateral force 계산
6. Vehicle body에 yaw moment 발생
```

즉, steering은 driver와 tire 사이를 연결하는 중간 subsystem이다.

---

## 10. 코드 관점 핵심 변수

PyChrono에서 driver input은 일반적으로 다음 세 가지로 구성된다.

| 변수 | 의미 | 범위 |
|---|---|---|
| `m_steering` | 조향 입력 | -1 ~ 1 |
| `m_throttle` | 가속 입력 | 0 ~ 1 |
| `m_braking` | 제동 입력 | 0 ~ 1 |

따라서 조향 실험을 할 때는 `m_steering` 값을 시간에 따라 바꾸며 차량의 yaw angle, lateral position, path tracking error를 관찰할 수 있다.

예시:

```python
driver_inputs = veh.DriverInputs()
driver_inputs.m_steering = 0.3
driver_inputs.m_throttle = 0.5
driver_inputs.m_braking = 0.0
```

이 경우 차량은 일정한 throttle을 유지하면서 한쪽 방향으로 선회하려고 한다.

---

## 11. Steering에서 관찰해야 할 물리량

로버/차량 설계 관점에서 steering subsystem을 분석할 때는 다음 물리량을 기록하면 좋다.

| 물리량 | 의미 |
|---|---|
| Steering input | 운전자 또는 제어기의 조향 명령 |
| Wheel steer angle | 실제 바퀴 조향각 |
| Yaw angle | 차량 heading 방향 |
| Yaw rate | 차량 회전 속도 |
| Lateral velocity | 횡방향 속도 |
| Slip angle | 타이어 진행 방향과 속도 방향의 차이 |
| Path tracking error | 목표 경로와 실제 경로의 차이 |

이 중 steering input, yaw angle, yaw rate는 Phase 3에서 우선 기록하기 좋은 값이다.

---

## 12. 프로젝트와의 연결

로버 최적 설계에서 steering은 다음 문제들과 직접 연결된다.

| 문제 | Steering과의 관계 |
|---|---|
| 좁은 공간 회전 | 최소 회전 반경 결정 |
| 경사면 주행 | 조향 중 횡방향 미끄러짐 가능 |
| 험지 주행 | 접지 불균일로 인한 조향 성능 저하 |
| 경로 추종 | 목표 경로와 실제 주행 경로 차이 |
| 자율주행 제어 | steering command가 제어 입력이 됨 |

특히 나중에 강화학습 또는 최적제어를 적용할 경우, steering input은 주요 action variable이 될 가능성이 크다.

예를 들어 로버 제어 문제는 다음과 같이 정리할 수 있다.

```text
State:
    position, velocity, yaw, yaw rate, roll, pitch, terrain state

Action:
    steering, throttle, braking

Reward / objective:
    path tracking, stability, energy efficiency, low slip
```

따라서 steering subsystem은 단순 기계 요소가 아니라 자율주행/최적제어와 직접 연결되는 입력 채널이다.

---

## 13. 다음 실험 아이디어

Phase 3에서 steering을 이해하기 위한 간단한 실험은 다음과 같다.

```text
1. Flat rigid terrain에서 일정 throttle 주행
2. steering input = 0.0, 0.2, 0.5로 변경
3. 차량 궤적 x-y plot 비교
4. yaw angle, yaw rate time history 저장
5. steering input이 커질수록 회전 반경이 어떻게 바뀌는지 확인
```

저장할 CSV 예시는 다음과 같다.

```text
time, x, y, z, yaw, yaw_rate, steering, throttle, speed
```

---

## 14. 핵심 정리

```text
Steering subsystem은 driver input을 wheel steer angle로 변환한다.
Pitman arm은 회전 링크 기반 조향 방식이다.
Rack-pinion은 pinion 회전을 rack 직선 운동으로 바꾸는 방식이다.
HMMWV_Full은 full double wishbone suspension과 Pitman arm steering을 사용한다.
Steering은 tire lateral force와 yaw motion을 통해 차량의 선회 성능을 결정한다.
```

---

## 15. 참고 자료

- Project Chrono 공식 문서: Steering mechanism models  
  https://api.projectchrono.org/wheeled_steering.html

- Project Chrono 공식 문서: Steering subsystem  
  https://api.projectchrono.org/group__vehicle__wheeled__steering.html

- Project Chrono 공식 문서: ChPitmanArm Class Reference  
  https://api.projectchrono.org/classchrono_1_1vehicle_1_1_ch_pitman_arm.html

- Project Chrono 공식 문서: HMMWV_Full Class Reference  
  https://api.projectchrono.org/classchrono_1_1vehicle_1_1hmmwv_1_1_h_m_m_w_v___full.html

- Project Chrono 공식 문서: RackPinion Class Reference  
  https://api.projectchrono.org/classchrono_1_1vehicle_1_1_rack_pinion.html

- Project Chrono Reference Manual: Chrono::Vehicle  
  https://api.projectchrono.org/manual_vehicle.html
