---
title: "Engine Models"
author: ""
last_modified: "2026-05-11"
tags:
  - chrono
  - vehicle
  - powertrain
  - engine
---

# Engine Models

Chrono::Vehicle의 engine subsystem은 운전자 throttle 입력과 transmission에서 되돌아오는 motorshaft speed를 이용해 엔진 출력 토크를 계산한다.

```text
Input:
  throttle u
  motorshaft speed omega_m

Output:
  motorshaft torque T_m
```

---

## 1. 공통 인터페이스

모든 engine model은 `ChEngine`에서 파생된다.

| 함수 | 의미 |
|---|---|
| `GetMotorSpeed()` | 현재 엔진축 각속도 |
| `GetOutputMotorshaftTorque()` | transmission으로 전달되는 엔진 토크 |
| `GetChassisReactionTorque()` | chassis에 작용하는 반작용 토크 |

engine의 핵심 입력은 다음과 같다.

```text
driver_inputs.m_throttle in [0, 1]
motorshaft_speed in rad/s
```

---

## 2. `EngineSimple`

`EngineSimple`은 가장 단순한 엔진 모델이다.
JSON에는 최대 토크, 최대 출력, 최대 엔진 속도만 들어간다.

```json
{
  "Name": "HMMWV Simple Engine",
  "Type": "Engine",
  "Template": "EngineSimple",

  "Maximum Engine Torque": 330,
  "Maximum Engine Power": 110000,
  "Maximum Engine Speed": 10000
}
```

Chrono 소스의 동작은 다음과 같이 요약할 수 있다.

1. 임계 속도 계산

$$
\omega_c = \frac{P_{\max}}{T_{\max}}
$$

2. 속도에 따른 기본 토크

$$
T_{\text{base}}(\omega) =
\begin{cases}
T_{\max}, & \omega \le \omega_c \\
\frac{P_{\max}}{\omega}, & \omega > \omega_c
\end{cases}
$$

3. 최대 속도 이상에서는 토크를 0으로 제한

$$
T_{\text{base}}(\omega) = 0 \quad \text{if } \omega \ge \omega_{\max}
$$

4. throttle로 선형 스케일

$$
T_m = u T_{\text{base}}(\omega)
$$

| 기호 | 의미 |
|---|---|
| $T_{\max}$ | maximum engine torque |
| $P_{\max}$ | maximum engine power |
| $\omega_c$ | constant torque 영역과 constant power 영역의 경계 |
| $\omega_{\max}$ | maximum engine speed |
| $u$ | throttle |

### 물리적 해석

`EngineSimple`은 실제 엔진의 복잡한 토크 곡선을 표현하기보다, 다음 형태의 이상화된 모터/엔진으로 보는 것이 좋다.

```text
저속: 최대 토크 일정
고속: 최대 출력 제한 때문에 torque 감소
최대속도 초과: torque = 0
```

입문 실험에서는 baseline으로 좋지만, 실제 차량의 RPM별 토크 특성을 분석하기에는 부족하다.

---

## 3. `EngineSimpleMap`

`EngineSimpleMap`은 속도-토크 맵을 사용한다.
입문 단계에서 가장 추천되는 엔진 모델이다.

```json
{
  "Name": "HMMWV Simple Map Engine",
  "Type": "Engine",
  "Template": "EngineSimpleMap",

  "Maximal Engine Speed RPM": 2600,

  "Map Full Throttle": [
    [ -100, 300 ],
    [ 800, 382 ],
    [ 900, 490 ],
    [ 1000, 579 ],
    [ 1600, 793 ],
    [ 2500, 558 ],
    [ 2700, -400 ]
  ],

  "Map Zero Throttle": [
    [ -100, 0 ],
    [ 0, 0 ],
    [ 1000, -50 ],
    [ 2000, -70 ],
    [ 3000, -90 ]
  ]
}
```

### 3.1 단위

JSON의 map은 보통 다음 형식이다.

```text
[engine_speed_rpm, torque_Nm]
```

Chrono 내부에서는 RPM을 rad/s로 변환한다.

$$
\omega_{\text{rad/s}} =
\text{rpm} \cdot \frac{2\pi}{60}
$$

### 3.2 토크 보간 수식

Chrono 소스의 핵심은 다음과 같다.

```cpp
double fullThrottleTorque = m_full_throttle_map.GetVal(m_motor_speed);
double zeroThrottleTorque = m_zero_throttle_map.GetVal(m_motor_speed);
m_motor_torque = zeroThrottleTorque * (1 - throttle) + fullThrottleTorque * throttle;
```

수식으로 쓰면:

$$
T_m(\omega, u)
= (1-u)T_0(\omega) + uT_F(\omega)
$$

| 항 | 의미 |
|---|---|
| $T_0(\omega)$ | zero throttle torque map |
| $T_F(\omega)$ | full throttle torque map |
| $u$ | throttle |

### 3.3 zero throttle map의 의미

zero throttle map은 단순히 토크 0이 아니다.
고속에서 음수 토크가 들어갈 수 있다.
이는 engine braking 또는 내부 손실을 단순화한 효과로 볼 수 있다.

```text
Throttle = 0
High RPM
Engine torque < 0
=> 차량을 조금 감속시키는 방향의 토크
```

### 3.4 full throttle map의 의미

full throttle map은 throttle이 1일 때 가능한 최대 엔진 토크 곡선이다.
일반적으로 다음 형태를 가진다.

```text
저속: 낮거나 중간 토크
중속: 최대 토크 구간
고속: 토크 감소
redline 근처: 음수 또는 급격한 감소
```

---

## 4. `EngineShafts`

`EngineShafts`는 Chrono의 1-D shaft 요소를 이용해 엔진을 더 물리적으로 표현한다.

공식 문서와 소스 기준으로 다음 요소를 포함한다.

| 요소 | Chrono 클래스 | 의미 |
|---|---|---|
| crankshaft/flywheel | `ChShaft` | 엔진 출력축 관성 |
| motor block | `ChShaft` | chassis에 연결되는 엔진 블록 관성 |
| engine torque | `ChShaftsThermalEngine` | throttle 기반 열기관 토크 |
| engine losses | `ChShaftsThermalEngine` | 내부 마찰/손실 토크 |
| chassis reaction | `ChShaftBodyRotation` | 엔진 반작용이 chassis에 전달 |

HMMWV shafts engine JSON 예시는 다음과 같다.

```json
{
  "Name": "HMMWV Shafts Engine",
  "Type": "Engine",
  "Template": "EngineShafts",

  "Motor Block Inertia": 10.5,
  "Motorshaft Inertia": 1.1,

  "Torque Map": [
    [ -100, 300 ],
    [ 800, 382 ],
    [ 1600, 793 ],
    [ 2500, 558 ],
    [ 2700, -400 ]
  ],

  "Losses Map": [
    [ -50, 30 ],
    [ 0, 0 ],
    [ 1000, -50 ],
    [ 2000, -70 ],
    [ 3000, -90 ]
  ]
}
```

### 4.1 단순 map 모델과의 차이

| 항목 | `EngineSimpleMap` | `EngineShafts` |
|---|---|---|
| 핵심 계산 | map 보간 후 토크 직접 계산 | shaft 요소와 engine/loss torque element |
| 관성 | 엔진 관성 직접 모델링 약함 | motor block, motorshaft inertia 포함 |
| chassis reaction | 보통 0 | engine block reaction torque 가능 |
| 계산량 | 낮음 | 상대적으로 높음 |
| 입문 난이도 | 낮음 | 중간 |

### 4.2 언제 shafts engine을 쓰나?

다음 분석을 하고 싶을 때 shafts engine이 의미 있다.

| 목적 | 이유 |
|---|---|
| 급가속 시 chassis roll/pitch 반응 | motor block reaction torque가 표현될 수 있음 |
| torque converter와 함께 분석 | shafts transmission과 자연스럽게 연결 |
| shaft inertia 효과 | 회전계 관성이 응답을 지연시킬 수 있음 |
| 물리 상세도가 필요한 검증 | simple map보다 더 많은 내부 state 포함 |

---

## 5. Engine torque와 차량 추진력 연결

엔진 토크는 곧바로 차량 추진력이 되지 않는다.
중간에 transmission, driveline, tire, terrain을 거친다.

```text
Engine torque T_m
    -> Transmission gear ratio
    -> Driveshaft torque T_d
    -> Driveline torque split
    -> Wheel torque T_w
    -> Tire force F_x
```

단순 근사:

$$
T_d \approx \frac{T_m}{r_g}
$$

$$
T_w \approx T_d \cdot r_{\text{driveline}}
$$

$$
F_x \approx \frac{T_w}{R}
$$

하지만 실제로는 다음 제한이 있다.

$$
|F_x| \le \mu F_z
$$

따라서 같은 engine map이라도 terrain 마찰계수, tire model, driveline 방식에 따라 차량 속도 응답이 달라진다.

---

## 6. 설계 변수로 볼 항목

| 변수 | JSON 위치 | 영향 |
|---|---|---|
| maximum engine speed | `Maximal Engine Speed RPM` | 최고속도, shift 가능 범위 |
| full throttle torque map | `Map Full Throttle` | 가속/등판 성능 |
| zero throttle torque map | `Map Zero Throttle` | 엔진 브레이크, 감속 |
| maximum torque | `Maximum Engine Torque` | 단순 엔진의 저속 토크 |
| maximum power | `Maximum Engine Power` | 고속 영역 출력 제한 |
| motorshaft inertia | `Motorshaft Inertia` | 엔진 응답성 |
| motor block inertia | `Motor Block Inertia` | chassis reaction 효과 |

---

## 7. 실험 아이디어

### 실험 1: full throttle map scaling

```text
Case A: original torque map
Case B: full throttle torque x 0.7
Case C: full throttle torque x 1.3

Output:
speed, acceleration, engine_rpm, gear, estimated slip
```

관찰 질문:

```text
토크를 키우면 항상 속도가 증가하는가?
낮은 마찰 지형에서 slip이 먼저 증가하지 않는가?
```

### 실험 2: zero throttle map 비교

```text
Case A: original zero throttle map
Case B: zero throttle torque = 0
Case C: stronger negative torque at high RPM

Output:
coasting deceleration, stopping distance
```

### 실험 3: max engine speed 변경

```text
Case A: 2600 RPM
Case B: 2200 RPM
Case C: 3200 RPM

Output:
max speed, shift timing, engine torque history
```

---

## 8. Python 로깅 예시

```python
import math

vehicle = hmmwv.GetVehicle()
engine = vehicle.GetEngine()

engine_omega = engine.GetMotorSpeed()
engine_rpm = engine_omega * 60.0 / (2.0 * math.pi)
engine_torque = engine.GetOutputMotorshaftTorque()

row = {
    "time": vehicle.GetSystem().GetChTime(),
    "engine_rpm": engine_rpm,
    "engine_torque_Nm": engine_torque,
}
```

---

## 9. 핵심 정리

```text
EngineSimple은 최대 토크/출력 기반의 가장 단순한 엔진이다.
EngineSimpleMap은 zero/full throttle speed-torque map을 throttle로 선형 보간한다.
EngineShafts는 ChShaft 기반으로 엔진 관성, 손실, chassis reaction을 더 자세히 표현한다.
로버 실험에서는 engine torque만 보지 말고 tire slip과 terrain 조건을 함께 봐야 한다.
```

---

## 10. 참고 자료

- Project Chrono 공식 문서: Powertrain models  
  https://api.projectchrono.org/vehicle_powertrain.html

- 로컬 소스:
  - `chrono/src/chrono_vehicle/powertrain/ChEngineSimple.cpp`
  - `chrono/src/chrono_vehicle/powertrain/ChEngineSimpleMap.cpp`
  - `chrono/src/chrono_vehicle/powertrain/ChEngineShafts.cpp`
  - `chrono/data/vehicle/hmmwv/powertrain/HMMWV_EngineSimpleMap.json`

