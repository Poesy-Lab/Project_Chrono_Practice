---
title: "Transmission Models"
author: ""
last_modified: "2026-05-11"
tags:
  - chrono
  - vehicle
  - powertrain
  - transmission
---

# Transmission Models

Transmission은 engine에서 나온 torque와 driveline에서 되돌아온 driveshaft speed를 이용해, driveline으로 전달할 torque와 engine으로 되돌려줄 motorshaft speed를 계산한다.

```text
Input:
  motorshaft torque T_m
  driveshaft speed omega_d

Output:
  driveshaft torque T_d
  motorshaft speed omega_m
```

---

## 1. 공통 인터페이스

모든 transmission model은 `ChTransmission`에서 파생된다.

| 함수 | 의미 |
|---|---|
| `GetCurrentGear()` | 현재 기어. reverse는 `-1`, neutral은 `0`, forward는 `1...Gmax` |
| `GetMaxGear()` | 최고 forward gear |
| `SetGear(gear)` | 지정 기어로 변경 |
| `ShiftUp()` / `ShiftDown()` | 한 단계 변속 |
| `GetOutputDriveshaftTorque()` | driveline으로 전달되는 torque |
| `GetOutputMotorshaftSpeed()` | engine으로 되돌아가는 speed |

automatic transmission은 drive mode를 가진다.

| mode | 의미 |
|---|---|
| `FORWARD` | 전진 |
| `NEUTRAL` | 중립 |
| `REVERSE` | 후진 |

---

## 2. 기어비의 기본 수식

Chrono의 `AutomaticTransmissionSimpleMap`은 현재 gear ratio를 $r_g$라고 할 때 다음을 사용한다.

$$
\omega_m = \frac{|\omega_d|}{r_g}
$$

$$
T_d = \frac{T_m}{r_g}
$$

| 기호 | 의미 |
|---|---|
| $\omega_m$ | motorshaft speed, engine 쪽 |
| $\omega_d$ | driveshaft speed, driveline 쪽 |
| $T_m$ | motorshaft torque, engine 출력 |
| $T_d$ | driveshaft torque, driveline 입력 |
| $r_g$ | Chrono gear ratio |

### 예시

엔진 토크가 $T_m = 300\,\text{N m}$이고 gear ratio가 $r_g=0.2$이면:

$$
T_d = \frac{300}{0.2}=1500\,\text{N m}
$$

즉 이 convention에서는 작은 gear ratio가 큰 torque multiplication을 만든다.

> [!warning] 일반 자동차 기어비 표기와 다름
> 자동차 교재에서 "1단 4.0:1"이라고 쓰는 값과 Chrono JSON의 `0.2` 같은 값은 같은 방식으로 읽으면 안 된다.
> Chrono simple transmission에서는 코드 수식 기준으로 해석한다.

---

## 3. `AutomaticTransmissionSimpleMap`

`AutomaticTransmissionSimpleMap`은 torque converter 없이, gear ratio와 shift point map으로 자동 변속을 구현한다.

HMMWV 예시:

```json
{
  "Name": "HMMWV Simple Map Transmission",
  "Type": "Transmission",
  "Template": "AutomaticTransmissionSimpleMap",

  "Gear Box": {
    "Reverse Gear Ratio": -0.151,
    "Forward Gear Ratios": [
      0.1708,
      0.2791,
      0.4218,
      0.6223,
      1.0173,
      1.5361
    ],
    "Shift Points Map RPM": [
      [ 1000, 2226 ],
      [ 1000, 2225 ],
      [ 1000, 2210 ],
      [ 1000, 2226 ],
      [ 1000, 2225 ],
      [ 1000, 2700 ]
    ]
  }
}
```

### 3.1 shift point

`Shift Points Map RPM`의 각 행은 대략 다음 의미를 가진다.

```text
[downshift_rpm, upshift_rpm]
```

자동변속 모드에서:

```text
if current_gear < max_gear and motor_speed > upshift_rpm:
    shift up

if current_gear > 1 and motor_speed < downshift_rpm:
    shift down
```

수식처럼 쓰면:

$$
g(t^+) =
\begin{cases}
g+1, & \omega_m > \omega_{\text{up},g} \\
g-1, & \omega_m < \omega_{\text{down},g} \\
g, & \text{otherwise}
\end{cases}
$$

### 3.2 장점과 한계

| 항목 | 내용 |
|---|---|
| 장점 | 단순하고 빠르며 JSON sweep이 쉬움 |
| 장점 | gear ratio와 shift point 영향이 명확함 |
| 한계 | torque converter 없음 |
| 한계 | clutch/shaft inertia의 상세 동역학 없음 |
| 추천 | Phase 3 초기 실험, 배치 실험 |

---

## 4. `AutomaticTransmissionSimpleCVT`

CVT 모델은 driveshaft speed에 따라 gear ratio를 연속적으로 바꾼다.
Chrono의 simple CVT JSON은 다음 형태이다.

```json
{
  "Name": "HMMWV Simple CVT Transmission",
  "Type": "Transmission",
  "Template": "AutomaticTransmissionSimpleCVT",

  "Gear Box": {
    "Efficiency": 0.8,
    "Minimum Gear Ratio": 0.1708,
    "Maximum Gear Ratio": 1.5361,
    "Driveshaft Speed Begin": 23.8,
    "Driveshaft Speed End": 238.0
  }
}
```

Chrono 소스 기준으로 gear ratio는 driveshaft speed의 함수로 보간된다.

$$
r_{\text{cvt}} = f(|\omega_d|)
$$

출력 torque는 drive mode 부호와 efficiency를 포함한다.

$$
T_d = s \eta \frac{T_m}{r_{\text{cvt}}}
$$

| 기호 | 의미 |
|---|---|
| $s$ | forward면 $+1$, reverse면 $-1$, neutral이면 $0$ |
| $\eta$ | gearbox efficiency |
| $r_{\text{cvt}}$ | 현재 CVT gear ratio |

CVT는 gear shift 이벤트가 없으므로 속도 응답이 부드러울 수 있다.
단, 실제 CVT 제어기까지 정밀하게 표현하는 모델로 과해석하지 않는 것이 좋다.

---

## 5. `AutomaticTransmissionShafts`

`AutomaticTransmissionShafts`는 torque converter와 gearbox를 포함한 shaft 기반 자동변속기이다.
공식 문서에 따르면 shafts-based powertrain은 Chrono 1-D shaft 요소와 shaft connection 요소를 이용한다.

구성 요소:

| 요소 | Chrono 클래스 | 의미 |
|---|---|---|
| motorshaft | `ChShaft` | engine과 transmission 연결 |
| driveshaft | `ChShaft` | transmission과 driveline 연결 |
| transmission block | `ChShaft` + `ChShaftBodyRotation` | chassis 반작용 |
| torque converter | `ChShaftsTorqueConverter` | 유체식 토크 증폭/슬립 |
| gearbox | `ChShaftsGearbox` | gear ratio constraint |

HMMWV shafts transmission JSON:

```json
{
  "Name": "HMMWV Shafts Automatic Transmission",
  "Type": "Transmission",
  "Template": "AutomaticTransmissionShafts",

  "Transmission Block Inertia": 10.5,
  "Input Shaft Inertia": 0.3,
  "Motorshaft Inertia": 0.5,
  "Driveshaft Inertia": 0.5,

  "Torque Converter": {
    "Capacity Factor Map": [
      [ 0.00, 15.00 ],
      [ 0.25, 15.00 ],
      [ 0.50, 15.00 ],
      [ 0.75, 16.00 ],
      [ 0.90, 18.00 ],
      [ 1.00, 35.00 ]
    ],
    "Torque Ratio Map": [
      [ 0.00, 2.00 ],
      [ 0.25, 1.80 ],
      [ 0.50, 1.50 ],
      [ 0.75, 1.15 ],
      [ 1.00, 1.00 ]
    ]
  },

  "Gear Box": {
    "Forward Gear Ratios": [ 0.2, 0.4, 0.8 ],
    "Reverse Gear Ratio": -0.1,
    "Upshift RPM": 2500,
    "Downshift RPM": 1200,
    "Shift Latency": 1.0
  }
}
```

### 5.1 torque converter

Torque converter는 입력축과 출력축 사이에 slip을 허용하면서 torque를 증폭할 수 있다.
기본적으로 speed ratio를 사용한다.

$$
\text{speed ratio} =
\frac{\omega_{\text{out}}}{\omega_{\text{in}}}
$$

torque ratio map은 다음 관계를 나타낸다.

$$
\text{torque ratio} =
\frac{T_{\text{out}}}{T_{\text{in}}}
$$

낮은 speed ratio에서는 torque ratio가 2.0처럼 커질 수 있고, speed ratio가 1에 가까워지면 torque ratio가 1에 가까워진다.

```text
차량 출발:
  output speed 낮음
  speed ratio 낮음
  torque ratio 큼
  출발 토크 증폭

고속 주행:
  input/output speed 비슷
  speed ratio 1에 가까움
  torque ratio 1에 가까움
```

### 5.2 shift latency

shafts automatic은 급격한 연속 변속을 막기 위해 shift latency를 둔다.

```text
if time - last_shift_time < shift_latency:
    no gear shift
```

이 값이 너무 작으면 변속이 자주 일어나고, 너무 크면 적절한 시점에 변속하지 못할 수 있다.

---

## 6. `ManualTransmissionShafts`

수동변속기 shafts model은 torque converter 대신 clutch를 사용한다.

구성 요소:

| 요소 | 의미 |
|---|---|
| `ChShaftsClutch` | engine shaft와 gearbox shaft 사이 torque 전달 |
| `Clutch Torque Limit` | clutch가 slip 없이 전달할 수 있는 최대 토크 |
| `driver_inputs.m_clutch` | clutch 조작 입력 |

예시 JSON:

```json
{
  "Name": "Sedan Shafts Manual Transmission",
  "Type": "Transmission",
  "Template": "ManualTransmissionShafts",

  "Transmission Block Inertia": 10.5,
  "Input Shaft Inertia": 0.05,
  "Motorshaft Inertia": 0.05,
  "Driveshaft Inertia": 0.05,
  "Clutch Torque Limit": 500,

  "Gear Box": {
    "Forward Gear Ratios": [ 0.265, 0.489, 0.784, 1.063, 1.276, 1.499 ],
    "Reverse Gear Ratio": -0.333
  }
}
```

Chrono 소스에서는 neutral이면 clutch modulation을 0으로 두고, 기어가 들어가 있으면 운전자 clutch 입력을 반영한다.

$$
m_{\text{clutch}} =
\begin{cases}
0, & g = 0 \\
1 - u_{\text{clutch}}, & g \ne 0
\end{cases}
$$

---

## 7. 모델 비교

| 항목 | SimpleMap | SimpleCVT | AutomaticShafts | ManualShafts |
|---|---|---|---|---|
| torque converter | 없음 | 없음 | 있음 | 없음 |
| clutch | 없음 | 없음 | 없음 | 있음 |
| gear shift | RPM shift map | 연속 ratio | up/down RPM + latency | 사용자/제어 입력 |
| shaft inertia | 낮음 | 낮음 | 있음 | 있음 |
| chassis reaction | 보통 낮음 | 보통 낮음 | 있음 | 있음 |
| 계산량 | 낮음 | 낮음 | 중간 | 중간 |
| 입문 적합도 | 높음 | 중간 | 중간 | 중간 |

---

## 8. 설계 변수로 볼 항목

| 변수 | 영향 |
|---|---|
| `Forward Gear Ratios` | 가속, 최고속도, 등판 성능 |
| `Reverse Gear Ratio` | 후진 주행 응답 |
| `Shift Points Map RPM` | 변속 시점, 엔진 RPM 유지 범위 |
| `Upshift RPM` / `Downshift RPM` | shafts automatic 변속 시점 |
| `Shift Latency` | 변속 안정성, 응답성 |
| `Torque Ratio Map` | 출발 토크 증폭 |
| `Capacity Factor Map` | torque converter 특성 |
| `Efficiency` | CVT torque 손실 |
| `Clutch Torque Limit` | clutch slip과 torque 전달 |

---

## 9. Python 로깅 예시

```python
import math

vehicle = hmmwv.GetVehicle()
transmission = vehicle.GetTransmission()

gear = transmission.GetCurrentGear()
driveshaft_torque = transmission.GetOutputDriveshaftTorque()
motorshaft_speed = transmission.GetOutputMotorshaftSpeed()
motorshaft_rpm = motorshaft_speed * 60.0 / (2.0 * math.pi)

row = {
    "gear": gear,
    "driveshaft_torque_Nm": driveshaft_torque,
    "motorshaft_rpm": motorshaft_rpm,
}

if transmission.IsAutomatic() and transmission.asAutomatic():
    auto = transmission.asAutomatic()
    row["has_torque_converter"] = auto.HasTorqueConverter()
    row["tc_slippage"] = auto.GetTorqueConverterSlippage()
```

> [!warning] 단순 모델의 torque converter 값
> `AutomaticTransmissionSimpleMap`과 `AutomaticTransmissionSimpleCVT`는 torque converter가 없으므로 관련 함수는 0 또는 false를 반환한다.

---

## 10. 핵심 정리

```text
Transmission은 engine torque와 driveline speed 사이의 변환기이다.
Chrono simple transmission은 T_d = T_m / r_g, omega_m = |omega_d| / r_g 형태를 사용한다.
AutomaticTransmissionSimpleMap은 gear ratio와 shift point만으로 빠르게 실험하기 좋다.
AutomaticTransmissionShafts는 torque converter, shaft inertia, shift latency를 포함한다.
ManualTransmissionShafts는 clutch torque limit과 clutch input을 포함한다.
```

---

## 11. 참고 자료

- Project Chrono 공식 문서: Powertrain models  
  https://api.projectchrono.org/vehicle_powertrain.html

- 로컬 소스:
  - `chrono/src/chrono_vehicle/powertrain/ChAutomaticTransmissionSimpleMap.cpp`
  - `chrono/src/chrono_vehicle/powertrain/ChAutomaticTransmissionSimpleCVT.cpp`
  - `chrono/src/chrono_vehicle/powertrain/ChAutomaticTransmissionShafts.cpp`
  - `chrono/src/chrono_vehicle/powertrain/ChManualTransmissionShafts.cpp`
  - `chrono/data/vehicle/hmmwv/powertrain/HMMWV_AutomaticTransmissionShafts.json`

