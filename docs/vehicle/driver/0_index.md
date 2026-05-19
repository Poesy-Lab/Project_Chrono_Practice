# Driver Overview

> Project Chrono Phase 3 - Vehicle / Driver  
> 주제: Chrono::Vehicle의 driver subsystem과 입력 전달 구조 이해

---

## Recommended Reading Order

| Order | Document | Topic | Related Example |
|---:|---|---|---|
| 00 | `0_index.md` | Driver subsystem 전체 개요 | 전체 driver 예제 |
| 01 | `1_driver_inputs.md` | `DriverInputs`의 구조와 의미 | `lesson3_1_programmed_driver_inputs_explained.ipynb` |
| 02 | `2_interactive_driver.md` | `ChInteractiveDriver` 기반 수동 조작 | `lesson3_2_driver_interactive_visual.py` |
| 03 | `3_data_driver.md` | 시간 기반 입력 재생과 CSV replay | `lesson3_3_driver_csv_replay_explained.ipynb` |
| 04 | `4_path_follower_driver.md` | 경로 추종 driver 개념 | `TBD` |
| 05 | `5_experiment_plan.md` | 실험 계획과 결과 정리 방향 | driver 관련 전체 결과 |

## 1. 목적

이 문서는 Chrono::Vehicle에서 **driver subsystem**이 어떤 역할을 하는지 정리한다.  
앞에서 suspension, steering, tire, driveline 같은 차량 subsystem을 다뤘다면, driver는 그 subsystem들에 어떤 입력을 줄지 결정하는 부분이다.

즉 driver는 차량의 물리 부품이라기보다, 차량을 움직이게 만드는 **입력 생성 계층**으로 이해하면 된다.

```text
Driver
  -> steering / throttle / braking 입력 생성
  -> Vehicle subsystem으로 전달
  -> steering / powertrain / brake / tire에 반영
  -> vehicle motion 변화
```

## 2. Driver가 다루는 기본 입력

Chrono vehicle driver가 다루는 기본 입력은 다음 세 가지다.

| 입력 | 의미 | 범위 |
|---|---|---|
| steering | 조향 입력 | -1 ~ 1 |
| throttle | 가속 입력 | 0 ~ 1 |
| braking | 제동 입력 | 0 ~ 1 |

상황에 따라 clutch 같은 입력이 추가될 수 있지만, Phase 3에서는 위 세 가지가 핵심이다.

## 3. Driver의 역할

driver는 직접 힘을 만들지 않는다.  
대신 차량 subsystem이 해석할 수 있는 형태로 명령을 전달한다.

```text
steering input
    -> steering subsystem
    -> wheel steer angle
    -> tire slip angle
    -> lateral force
    -> yaw motion

throttle input
    -> engine / motor
    -> driveline
    -> wheel torque
    -> longitudinal tire force
    -> acceleration

braking input
    -> brake subsystem
    -> braking torque
    -> wheel deceleration
    -> tire braking force
    -> vehicle deceleration
```

## 4. Driver 종류

| Driver | 설명 |
|---|---|
| Interactive Driver | 키보드나 조이스틱으로 직접 조작 |
| Data Driver | 시간에 따른 입력 데이터를 재생 |
| Path Follower Driver | 목표 경로를 따라가도록 조향/속도 제어 |
| Closed-loop Driver | feedback 제어 기반 입력 생성 |
| Custom Driver | 사용자가 직접 입력 생성 로직 작성 |

Phase 3에서는 아래 순서로 접근하는 것이 자연스럽다.

```text
1. DriverInputs 구조 이해
2. Interactive Driver로 수동 조작
3. 시간 함수 기반 programmed driver
4. CSV 기반 replay driver
5. Path follower driver 개념 확장
```

## 5. Simulation Loop 안에서의 위치

driver는 simulation loop 안에서 다음 흐름으로 동작한다.

```python
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

핵심은 `driver_inputs`가 `hmmwv.Synchronize()`로 전달된다는 점이다.  
즉 driver는 독립적으로 끝나는 것이 아니라, 차량 subsystem 전체의 입력 소스로 연결된다.

## 6. 왜 중요한가

driver 구조를 이해하면 단순 수동 조작을 넘어서 다양한 제어 문제로 확장할 수 있다.

```text
manual driving
-> programmed test inputs
-> CSV replay
-> path following
-> closed-loop control
-> reinforcement learning action interface
```

특히 자율주행, 제어기 설계, RL 환경 구성에서는 driver input이 곧 action interface 역할을 한다.

## 7. 참고 자료

- Project Chrono 공식 문서: Driver subsystem  
  https://api.projectchrono.org/vehicle_driver.html

- Project Chrono 공식 문서: Driver system group  
  https://api.projectchrono.org/group__vehicle__driver.html

- Project Chrono 공식 문서: `ChInteractiveDriver`  
  https://api.projectchrono.org/classchrono_1_1vehicle_1_1_ch_interactive_driver.html

- Project Chrono 공식 문서: `ChDataDriver`  
  https://api.projectchrono.org/classchrono_1_1vehicle_1_1_ch_data_driver.html

- Project Chrono 공식 문서: `ChPathFollowerDriver`  
  https://api.projectchrono.org/classchrono_1_1vehicle_1_1_ch_path_follower_driver.html
