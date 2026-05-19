# Path Follower Driver

> Project Chrono Phase 3 - Vehicle / Driver  
> 주제: 목표 경로를 따라가기 위한 closed-loop driver

---

## 1. 정의

Path Follower Driver는 차량이 미리 정의된 경로를 따라가도록 steering과 speed input을 자동으로 계산하는 driver이다.

공식 문서의 `ChPathFollowerDriver`는 기본 PID lateral steering controller를 사용하여 path following을 수행하는 driver system으로 설명된다. `ChPathFollowerACCDriver`는 path steering controller와 speed controller를 함께 사용하여 경로 추종과 속도 유지 기능을 수행한다.

---

## 2. Interactive / Data / Path Follower 비교

| Driver | 입력 생성 방식 | 사용 목적 |
|---|---|---|
| Interactive Driver | 사람이 키보드 입력 | 수동 테스트 |
| Data Driver | 미리 정의된 time-series | 반복 가능한 실험 |
| Path Follower Driver | 경로 오차 기반 feedback control | 자율주행/경로추종 |

Path follower는 단순 replay가 아니라 현재 차량 위치와 목표 경로의 차이를 이용해 steering을 계산한다.

---

## 3. 경로 추종의 기본 구조

```text
Vehicle state
    ↓
현재 위치와 목표 경로 비교
    ↓
lateral error / heading error 계산
    ↓
steering controller
    ↓
steering input
    ↓
vehicle motion
```

속도 제어까지 포함하면:

```text
desired speed - current speed
    ↓
speed controller
    ↓
throttle / braking input
```

---

## 4. PID 제어 관점

```text
steering = Kp * error + Ki * integral(error) + Kd * derivative(error)
```

| 항 | 의미 |
|---|---|
| P | 현재 경로 오차를 줄임 |
| I | 누적 오차를 줄임 |
| D | 오차 변화율을 억제해 진동을 줄임 |

---

## 5. Phase 3에서의 접근 방법

처음부터 Chrono의 path follower API를 복잡하게 쓰기보다 다음 순서를 추천한다.

```text
1. 수동 driver로 차량 반응 확인
2. programmed driver로 step steering 실험
3. CSV replay driver로 입력 재현
4. 간단한 pure pursuit 또는 heading controller 직접 구현
5. Chrono ChPathFollowerDriver API 실험
```

---

## 6. 직접 구현 가능한 간단한 경로 추종

목표 경로를 `z = 0` 직선으로 두면 lateral error는 `z`로 볼 수 있다.

```python
steering = np.clip(-0.05 * z, -0.5, 0.5)
throttle = 0.4
braking = 0.0
```

이 방식은 실제 path follower보다는 단순하지만, driver input이 feedback으로 생성된다는 개념을 이해하기 좋다.

---

## 7. 핵심 정리

```text
Path Follower Driver는 경로 오차를 이용해 driver input을 자동 생성한다.
ChPathFollowerDriver는 PID lateral steering controller 기반 path following driver이다.
ChPathFollowerACCDriver는 path steering과 speed control을 함께 제공한다.
Phase 3에서는 직접 구현한 간단한 feedback driver로 개념을 먼저 확인하는 것이 좋다.
```
