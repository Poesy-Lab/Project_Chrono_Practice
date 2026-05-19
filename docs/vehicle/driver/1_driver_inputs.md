# Driver Inputs

> Project Chrono Phase 3 - Vehicle / Driver  
> 주제: steering, throttle, braking 입력 구조

---

## 1. 정의

`DriverInputs`는 Chrono::Vehicle에서 차량에 전달되는 기본 운전 입력 묶음이다.

| 변수 | 의미 | 범위 |
|---|---|---|
| `m_steering` | 조향 입력 | -1 ~ 1 |
| `m_throttle` | 가속 입력 | 0 ~ 1 |
| `m_braking` | 제동 입력 | 0 ~ 1 |

일부 driver data에서는 clutch 값까지 포함할 수 있다.

---

## 2. Steering Input

```text
m_steering = -1.0 → 최대 좌회전
m_steering =  0.0 → 직진
m_steering =  1.0 → 최대 우회전
```

실제 바퀴 조향각은 vehicle의 steering mechanism과 steering limit에 의해 결정된다.  
즉, `m_steering = 0.5`가 바퀴 각도 0.5 rad를 의미하는 것은 아니다.

---

## 3. Throttle Input

```text
m_throttle = 0.0 → 가속 없음
m_throttle = 1.0 → 최대 throttle
```

이 값은 engine/motor torque 계산에 영향을 주고, driveline을 통해 바퀴 토크로 전달된다.

---

## 4. Braking Input

```text
m_braking = 0.0 → 제동 없음
m_braking = 1.0 → 최대 제동
```

브레이크 입력은 바퀴 회전을 늦추고, 타이어-지면 접촉을 통해 차량 속도를 줄인다.

---

## 5. 코드 예시

```python
driver_inputs = veh.DriverInputs()
driver_inputs.m_steering = 0.0
driver_inputs.m_throttle = 0.4
driver_inputs.m_braking = 0.0
```

그리고 simulation loop에서 차량에 전달한다.

```python
hmmwv.Synchronize(time, driver_inputs, terrain)
hmmwv.Advance(step_size)
```

---

## 6. 시간 함수 기반 입력

### Step steering

```python
if time < 3.0:
    steering = 0.0
else:
    steering = 0.3
```

### Throttle ramp

```python
throttle = min(0.6, 0.1 * time)
```

### Sine steering

```python
steering = 0.3 * np.sin(2 * np.pi * 0.2 * time)
```

---

## 7. CSV 저장 항목

```text
time, x, y, z, speed, roll, pitch, yaw,
steering, throttle, braking
```

입력값을 저장해야 결과 그래프에서 차량 반응과 입력의 관계를 해석할 수 있다.

---

## 8. 핵심 정리

```text
DriverInputs는 차량에 들어가는 제어 입력 묶음이다.
steering은 -1~1, throttle/braking은 0~1 범위의 무차원 입력이다.
입력값은 steering, powertrain, brake subsystem으로 전달된다.
실험에서는 driver input과 차량 상태를 함께 저장해야 한다.
```
