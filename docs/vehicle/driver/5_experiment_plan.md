# Driver Experiment Plan

> Project Chrono Phase 3 - Vehicle / Driver  
> 주제: driver input 생성 방식에 따른 차량 응답 비교 실험

---

## 1. 목적

이 문서는 Phase 3에서 driver subsystem을 학습하기 위한 실험 계획을 정리한다.  
핵심 질문은 하나다.

**같은 차량에 어떤 입력을 주느냐에 따라 차량 응답이 어떻게 달라지는가?**

앞에서 wheeled vehicle 파트에서 차량 구조를 봤다면, 여기서는 그 차량에 들어가는 입력 방식 자체를 비교한다.

## 2. 실험 목록

| 예제 | 목적 |
|---|---|
| `lesson3_1_programmed_driver_inputs_explained.ipynb` | 시간 함수 기반 입력 패턴 비교 |
| `lesson3_3_driver_csv_replay_explained.ipynb` | CSV 기반 입력 replay |
| `lesson3_2_driver_interactive_visual.py` | WASD 수동 조작과 CSV autosave |

## 3. 실험 1: Programmed Driver Inputs

첫 번째 실험은 사용자가 직접 키를 누르지 않고, 시간에 따라 입력을 함수 형태로 정의해 차량에 전달하는 방식이다.

### 입력 case

```text
Case 1: constant throttle
Case 2: step steering
Case 3: sine steering
Case 4: throttle ramp
```

### 보고 싶은 출력

```text
speed vs time
x-z trajectory
driver input vs time
yaw / yaw_rate
```

이 실험의 목적은 입력 패턴이 차량 궤적과 속도 응답에 어떤 차이를 만드는지 비교하는 것이다.

## 4. 실험 2: CSV Driver Replay

두 번째 실험은 미리 준비한 입력 데이터를 시간 순서대로 재생하는 방식이다.

### 입력 CSV 형식

```text
time, steering, throttle, braking
```

### 분석 목적

```text
같은 입력 프로파일을 여러 번 반복 적용할 수 있는지 확인
입력 데이터가 차량 속도, 자세, 궤적에 어떻게 반영되는지 확인
```

이 방식은 재현 가능한 실험, 모델 비교, 제어기 결과 replay에 특히 유리하다.

## 5. 실험 3: Interactive Visual Driver

세 번째 실험은 사용자가 직접 차량을 조작하는 방식이다.

### 조작 키

```text
W: throttle
S: braking
A: steer left
D: steer right
J: input lock/unlock
```

### 주의점

```text
이 예제는 notebook보다 .py 스크립트로 실행하는 편이 안정적이다.
simulation loop 중간에 CSV autosave를 넣어야 예기치 않은 종료에도 로그가 남는다.
```

이 실험의 목적은 driver input이 실시간으로 어떻게 생성되고 차량에 전달되는지 직관적으로 확인하는 것이다.

## 6. 공통 로그 항목

모든 실험에서는 가능한 한 같은 형식으로 차량 상태를 저장하는 것이 좋다.

```text
time
x, y, z
vx, vy, vz
speed
roll, pitch, yaw
steering, throttle, braking
case_name
```

이렇게 맞춰두면 실험 간 비교 그래프를 만들기 쉽다.

## 7. 확장 방향

driver 실험은 여기서 끝나지 않는다.  
입력 생성 방식을 조금씩 일반화하면 다음 주제로 자연스럽게 이어진다.

```text
programmed driver
    -> data replay driver
    -> closed-loop feedback driver
    -> path follower driver
    -> RL action interface
```

즉 이번 phase는 단순 예제 정리가 아니라, 이후 제어와 자율화 실험을 위한 입력 계층 이해 단계라고 볼 수 있다.

## 8. Phase 완료 기준

```text
1. driver 문서가 정리되어 있다
2. programmed driver 예제가 실행된다
3. CSV replay 예제가 실행된다
4. interactive visual script가 실행된다
5. 입력과 차량 응답 그래프가 생성된다
6. 결과가 docs에 요약된다
```
