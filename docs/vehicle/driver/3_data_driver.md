# Data Driver

> Project Chrono Phase 3 - Vehicle / Driver  
> 주제: 시간표 기반 driver input replay

---

## 1. 정의

Data Driver는 시간에 따라 미리 정의된 steering, throttle, braking 입력을 차량에 적용하는 driver model이다.

공식 문서의 `ChDataDriver`는 사용자 입력을 time series 형태로 제공받는 driver model이다. 텍스트 파일을 사용할 경우 각 줄에는 시간, steering, throttle, braking, clutch 값이 들어갈 수 있으며, 중간 시간의 입력은 선형 보간으로 계산된다.

---

## 2. 왜 Data Driver가 필요한가?

Interactive driver는 사람이 직접 조작하므로 매번 입력이 달라진다. 반면 Data Driver는 항상 같은 입력을 재현할 수 있다.

```text
1. 같은 throttle profile로 tire model 비교
2. 같은 steering step으로 yaw response 비교
3. 같은 braking input으로 제동 성능 비교
4. 외부 제어기 또는 RL policy 입력 replay
```

---

## 3. 입력 파일 형식

공식 문서의 driver data file 개념은 다음과 같다.

```text
time steering throttle braking clutch
```

Phase 3에서는 clutch를 사용하지 않는 경우가 많으므로 CSV replay 예제에서는 다음 4개 컬럼을 우선 사용한다.

```text
time, steering, throttle, braking
```

---

## 4. 보간의 의미

입력 데이터가 다음과 같다고 하자.

```text
time = 0 s, throttle = 0.0
time = 2 s, throttle = 0.6
```

1초 시점의 throttle은 선형 보간으로 약 0.3이 된다.

---

## 5. PyChrono에서의 안전한 구현 전략

PyChrono 버전별로 `ChDataDriver` 생성자나 파일 형식이 다를 수 있다. 따라서 Phase 3 예제에서는 직접 보간해서 `veh.DriverInputs()`에 넣는 방식을 사용한다.

```python
steering = np.interp(time, input_df["time"], input_df["steering"])
throttle = np.interp(time, input_df["time"], input_df["throttle"])
braking  = np.interp(time, input_df["time"], input_df["braking"])

driver_inputs = veh.DriverInputs()
driver_inputs.m_steering = steering
driver_inputs.m_throttle = throttle
driver_inputs.m_braking = braking
```

이 방식은 `ChDataDriver`와 개념적으로 같은 time-series replay이며, PyChrono API 차이에 덜 민감하다.

---

## 6. 프로젝트와의 연결

Data Driver는 반복 가능한 실험에 필수이다.

```text
같은 driver input
    ↓
차량 설계 변수 변경
    ↓
terrain 변수 변경
    ↓
성능 비교
```

---

## 7. 핵심 정리

```text
Data Driver는 시간표 기반 driver input replay 방식이다.
반복 가능한 실험과 모델 비교에 적합하다.
공식 ChDataDriver 대신 직접 보간 방식으로 구현하면 PyChrono 버전 차이에 더 안정적이다.
driver input CSV는 time, steering, throttle, braking 컬럼으로 시작하면 충분하다.
```
