# Custom Rover Guide

이 폴더는 Phase 4의 커스텀 로버 설계 예제를 체계적으로 정리한 구조다.
핵심 목표는 다음 두 가지다.

1. 로버 설계 코드와 드라이버 로직을 분리한다.
2. 다른 사용자가 어떤 파일부터 읽고, 어디를 수정해야 하는지 바로 알 수 있게 한다.

## 폴더 구조

```text
custom_rover/
  README.md         사용 가이드
  config.py         실험 설정, 기하 파라미터, 공통 데이터 구조
  drivers.py        입력 생성기: profile driver, waypoint driver
  rover.py          로버 본체와 하부 subsystem 구성
  simulation.py     시뮬레이션 루프, 로그 저장, 경로 플롯
  main.py           실행 진입점
  results/          실행 결과 CSV, PNG 저장 위치
```

## 현재 커스텀 로버 설명

현재 예제의 로버는 **Viper 스타일의 4륜 커스텀 탐사 로버**를 직접 조립한 구조다.
단순히 공식 로봇 모델을 불러오는 것이 아니라, 차체와 바퀴, 조향부, 구동부, 상부 구조물을 코드로 하나씩 만드는 방식이다.

### 1. 전체 개념

이 로버는 다음 목적을 위한 베이스라인 예제다.

- 커스텀 로버 형상 설계
- waypoint 또는 profile 기반 주행 실험
- 지형 장애물 통과 거동 관찰
- CSV 로그와 경로 플롯 생성

즉, "내가 직접 만든 로버를 내가 만든 입력으로 시험해보는 구조"라고 보면 된다.

### 2. 현재 로버 구성

현재 로버는 다음 요소로 이루어진다.

- 메인 차체 `chassis`
- 상부 구조물 `science_deck`
- 센서 기둥 `sensor_mast`
- 센서 헤드 `sensor_head`
- 앞 조향 knuckle 2개
- 바퀴 4개
- 앞바퀴 steering motor 2개
- 바퀴 drive motor 4개

즉 기계적으로는 **4륜 구동 + 앞바퀴 조향** 구조다.

### 3. 바퀴와 차체 배치

바퀴 이름은 다음과 같이 정리되어 있다.

- `FL`: front-left
- `FR`: front-right
- `RL`: rear-left
- `RR`: rear-right

배치는 `wheelbase`, `track_width`, `front_x`, `rear_x`, `left_y`, `right_y`로 결정된다.

즉:

- 앞/뒤 간격은 `wheelbase`
- 좌/우 간격은 `track_width`
- 바퀴 반지름은 `wheel_radius`

이 값을 바꾸면 전체 로버 비율이 같이 달라진다.

### 4. 조향 구조

조향은 앞바퀴 2개만 담당한다.

관련 함수:

- `rover.py`의 `_create_front_knuckles()`
- `rover.py`의 `_create_steering_motors()`
- `rover.py`의 `_compute_steering_angles()`

현재 조향 방식은 **Ackermann 스타일**이다.
즉 좌회전과 우회전 시 안쪽 바퀴와 바깥쪽 바퀴의 조향각을 다르게 계산한다.

### 5. 구동 구조

구동은 4개 바퀴 모두에 drive motor가 연결되어 있다.
다만 제어는 바퀴 하나하나를 완전히 독립적으로 주는 방식이 아니라,
**좌측 바퀴 속도 / 우측 바퀴 속도**를 나누는 구조다.

관련 함수:

- `rover.py`의 `_create_drive_motors()`
- `rover.py`의 `_compute_side_omegas()`
- `rover.py`의 `synchronize()`

이 구조 덕분에 일반 주행뿐 아니라 좌우 속도 차를 이용한 turn 성향도 만들 수 있다.

### 6. turn_mode 의미

`DriverInputs`에는 `turn_mode`가 있다.

- `0.0`: 일반 주행에 가까운 속도 차
- `1.0`: pivot-turn 성향이 강한 속도 차

즉 steering 입력만 있는 것이 아니라,
회전 방식을 얼마나 강하게 줄지까지 같이 제어하는 구조다.

### 7. 상부 구조물

이 로버는 단순 박스 차체가 아니라 탐사 로버처럼 보이도록 시각 요소를 추가해 두었다.

- `science_deck`
- `sensor_mast`
- `sensor_head`
- wheel hub
- grouser

이 요소들은 로버를 더 탐사 로봇처럼 보이게 해 주며,
대부분 차체나 바퀴에 고정된 body로 구현되어 있다.

### 8. 지형 구성

현재 환경은 단순 평지가 아니다.

- 넓은 ground
- 경사로 1개
- step 장애물 2개
- rock block 여러 개
- waypoint marker

즉 현재 예제는 "커스텀 로버를 장애물이 있는 환경에서 시험하는 구조"다.

### 9. 입력 방식

현재 로버는 두 가지 방식으로 움직일 수 있다.

#### waypoint driver

- waypoint를 순서대로 따라간다
- heading error를 계산해서 steering 명령을 만든다
- 회전이 크면 속도를 줄인다

#### profile driver

- 시간 기반 입력을 직접 준다
- `straight`
- `step_turn`
- `slalom`
- `spin_test`
- `pivot_turn`

즉 같은 로버를 두고도
"경로를 따라가게 할지", "미리 정의한 입력으로 시험할지"를 바꿀 수 있다.

### 10. 현재 결과물

시뮬레이션을 돌리면 다음 결과가 저장된다.

- CSV 로그
- 경로 플롯 PNG

CSV에는 다음 정보가 저장된다.

- 시간
- 로버 위치
- yaw 각도
- 목표 waypoint
- 속도 명령
- 조향 명령
- turn_mode
- 바퀴 각속도
- 좌/우 조향각

즉 단순 시각화만 보는 것이 아니라,
후처리와 비교 실험이 가능하도록 로그 구조까지 포함된 예제다.

### 11. 이 예제의 위치

이 커스텀 로버는 다음 단계 사이에 놓인 예제라고 보면 된다.

```text
공식 데모 따라가기
    -> 내 로버 형상 직접 만들기
    -> 입력 방식 바꾸기
    -> 지형 바꾸기
    -> 제어기 추가
    -> 자율 주행 / RL 실험으로 확장
```

즉 지금 코드는 완성형 제품이라기보다,
이후 커스텀 로버 연구를 시작하기 위한 **정리된 출발점**이다.

## 추천 읽기 순서

1. `config.py`
2. `drivers.py`
3. `rover.py`
4. `simulation.py`
5. `main.py`

## 실행 방법

프로젝트 루트에서:

```powershell
conda activate chrono
python lessons/phase4/Dohee/custom_rover.py
```

또는 정식 진입점으로:

```powershell
conda activate chrono
python lessons/phase4/Dohee/custom_rover/main.py
```

## 어디를 수정하면 되는가

### 1. 로버 형상과 기구를 바꾸고 싶을 때

- `config.py`의 치수, 질량, 마찰계수
- `rover.py`의 `_create_*` 계열 함수

#### A. 가장 먼저 보는 파일

로버 자체를 커스텀하려면 아래 두 파일이 중심이다.

- `config.py`
- `rover.py`

권장 순서는 다음과 같다.

```text
1. config.py에서 수치 파라미터 수정
2. rover.py에서 실제 생성 함수 확인
3. 필요한 경우 body / wheel / terrain 생성 로직 수정
4. 실행 후 결과 CSV, 경로 플롯, 시각화로 확인
```

#### B. 치수와 기본 설계값을 바꾸는 방법

`config.py`에는 로버 형상을 결정하는 주요 파라미터가 모여 있다.

예를 들면:

- 차체 크기: `chassis_length`, `chassis_width`, `chassis_height`
- 차체 위치: `chassis_z`
- 바퀴 크기: `wheel_radius`, `wheel_width`
- 휠베이스/트레드: `wheelbase`, `track_width`
- 센서 마스트와 헤드 위치: `mast_*`, `sensor_head_*`
- 지형 크기: `ground_*`, `slope_*`, `step_*`

즉, 비율이나 전체 크기만 바꾸고 싶다면 보통 `config.py`만 수정하면 된다.

#### C. 차체 모양을 바꾸는 방법

차체와 상부 구조는 `rover.py`에서 생성한다.

- `_create_chassis()`
- `_create_body_style()`

예를 들어:

- 메인 차체 박스를 더 길게 만들고 싶다
- science deck를 없애고 싶다
- 센서 마스트 위치를 옮기고 싶다
- 상부 payload를 새로 추가하고 싶다

이런 변경은 `rover.py`의 위 함수들을 수정하면 된다.

#### D. 바퀴를 바꾸는 방법

바퀴 관련 변경은 다음 순서로 보면 된다.

- `config.py`
  - `wheel_radius`
  - `wheel_width`
  - `hub_*`
  - `grouser_*`
- `rover.py`
  - `_create_wheels()`
  - `_create_wheel()`
  - `_add_wheel_visuals()`

예를 들어:

- 바퀴 반지름 확대
- 허브 두께 변경
- grouser 개수 증가
- grouser 형상을 없애고 단순 휠만 남기기

이런 작업은 위 위치에서 처리하면 된다.

#### E. 조향 구조를 바꾸는 방법

조향은 앞바퀴 knuckle + steering motor 구조로 나뉜다.

- `_create_front_knuckles()`
- `_create_steering_motors()`
- `_compute_steering_angles()`

현재는 앞바퀴 2개 조향 + Ackermann 스타일 계산이다.

만약:

- 4륜 조향으로 바꾸고 싶다
- Ackermann 대신 단순 동일 조향각을 쓰고 싶다
- 조향 한계를 줄이고 싶다

이 경우는 `rover.py`와 `config.py`를 함께 수정하면 된다.

#### F. 구동 방식을 바꾸는 방법

현재 구조는 좌/우 바퀴 속도를 나눠서 주는 방식이다.

관련 위치:

- `rover.py`
  - `_create_drive_motors()`
  - `_compute_side_omegas()`
  - `synchronize()`

예를 들어:

- 전륜구동만 쓰기
- 후륜구동만 쓰기
- 4륜 독립 속도 제어
- pivot turn 강도 조정

이런 변경은 구동 모터 연결과 속도 분배 함수 쪽을 보면 된다.

#### G. 지형을 바꾸는 방법

지형은 `rover.py`에서 분리되어 있다.

- `_create_ground()`
- `_create_terrain_features()`
- `_create_waypoint_markers()`

즉 다음 변경이 가능하다.

- 평지 크기 확대
- slope 제거
- step 높이 조정
- rock 배치 수정
- waypoint marker 제거

지형 preset을 나중에 늘리고 싶다면 이 함수들을 terrain 전용 파일로 한 번 더 분리하면 된다.

#### H. 가장 흔한 커스텀 순서

새 사용자가 가장 자주 하는 커스텀 흐름은 보통 이렇다.

```text
1. wheel_radius, wheelbase, track_width 수정
2. chassis_length, chassis_width, chassis_z 수정
3. slope / step / rock 지형 난이도 조정
4. driver 모드 바꿔서 주행 확인
5. 필요하면 steering / drive 로직 수정
```

#### I. 새 body를 추가하는 방법

예를 들어 배터리 박스, 센서 모듈, cargo box를 추가하고 싶다면
`_create_body_style()` 안에서 새 body를 만들고 `self._fix_to_chassis(...)`로 차체에 고정하면 된다.

흐름은 다음과 같다.

```text
1. ChBodyEasyBox / Cylinder 등으로 body 생성
2. 위치와 색상 설정
3. system.Add(...)
4. self._fix_to_chassis(body)
```

#### J. 로버 커스텀 체크리스트

```text
1. config.py 수치가 먼저 정리됐는가
2. rover.py 생성 함수가 그 수치를 실제로 사용하고 있는가
3. 바퀴 위치와 차체 높이가 충돌 없이 배치됐는가
4. steering / drive motor 축 방향이 여전히 맞는가
5. 시각화와 CSV 로그로 결과를 확인했는가
```

### 2. 드라이버를 바꾸고 싶을 때

- `drivers.py`
- `SimulationConfig.control_mode`

#### A. waypoint driver와 profile driver를 바꾸는 방법

`config.py`의 `SimulationConfig`에서 아래 두 값을 본다.

```python
control_mode = "waypoints"
experiment_name = "slalom"
```

- `control_mode = "waypoints"`
  - waypoint 기반 주행
  - `drivers.py`의 `WaypointDriver` 사용
- `control_mode = "profiles"`
  - 시간 기반 입력 주행
  - `drivers.py`의 `ProgrammedDriver` 사용

예를 들어 waypoint 추종 대신 시간 기반 step turn 실험으로 바꾸고 싶다면:

```python
control_mode = "profiles"
experiment_name = "step_turn"
```

#### B. 기존 profile 종류를 바꾸는 방법

`drivers.py`의 `EXPERIMENTS`에서 선택 가능한 profile 이름을 관리한다.

```python
EXPERIMENTS = {
    "straight": straight_profile,
    "step_turn": step_turn_profile,
    "slalom": slalom_profile,
    "spin_test": spin_test_profile,
    "pivot_turn": pivot_turn_profile,
}
```

원하는 실험명을 `config.py`의 `experiment_name`에 넣으면 된다.

#### C. 새로운 profile driver를 추가하는 방법

1. `drivers.py`에 새 함수 추가
2. `EXPERIMENTS` 딕셔너리에 등록
3. `config.py`의 `experiment_name`을 새 이름으로 변경

예시:

```python
def slow_s_curve_profile(t):
    if t < 1.0:
        return DriverInputs(0.0, 0.0, 0.0)
    return DriverInputs(0.5, 0.35 * math.sin(0.6 * (t - 1.0)), 0.0)


EXPERIMENTS = {
    "straight": straight_profile,
    "step_turn": step_turn_profile,
    "slalom": slalom_profile,
    "spin_test": spin_test_profile,
    "pivot_turn": pivot_turn_profile,
    "slow_s_curve": slow_s_curve_profile,
}
```

그리고 `config.py`에서:

```python
control_mode = "profiles"
experiment_name = "slow_s_curve"
```

#### D. waypoint 경로를 바꾸는 방법

`config.py`의 `WAYPOINTS` 리스트를 수정하면 된다.

```python
WAYPOINTS = [
    (0.0, 0.0),
    (2.0, 0.0),
    (4.0, 1.0),
    (6.0, 1.0),
]
```

이 경우 `control_mode = "waypoints"` 여야 한다.

#### E. 아예 새로운 driver 클래스를 추가하는 방법

driver가 더 복잡해져서 별도 클래스가 필요하면 `drivers.py`에 새 클래스를 만들고,
`simulation.py`의 `build_driver()`에서 연결하면 된다.

즉 추가 순서는 다음과 같다.

```text
1. drivers.py에 새 driver 클래스 작성
2. simulation.py의 build_driver()에 선택 분기 추가
3. config.py에서 해당 모드를 고를 수 있게 설정
```

### 3. 실험 이름, 종료 시간, 로그 주기를 바꾸고 싶을 때

- `config.py`의 `SimulationConfig`

## 현재 지원하는 driver

### Profile driver

시간에 따라 미리 정의된 입력을 사용한다.

- `straight`
- `step_turn`
- `slalom`
- `spin_test`
- `pivot_turn`

### Waypoint driver

목표 waypoint를 순서대로 따라간다.

## 빠른 변경 예시

### slalom profile로 실행

```python
control_mode = "profiles"
experiment_name = "slalom"
```

### waypoint 추종으로 실행

```python
control_mode = "waypoints"
experiment_name = "slalom"
```

`waypoints` 모드에서는 `experiment_name`이 주행 로직 선택에 직접 쓰이지 않지만,
출력 파일명에는 반영될 수 있으므로 함께 정리해 두는 것이 좋다.

## 설계 원칙

- 로버 구조와 driver는 분리한다.
- 실행 진입점은 하나로 유지한다.
- 결과 저장 위치는 코드와 가까운 곳에 둔다.
- 새 driver를 추가해도 `rover.py`는 건드리지 않도록 한다.

## 로버를 커스텀할 때 핵심 규칙

- 형상 비율만 바꿀 때는 먼저 `config.py`를 수정한다.
- 구조가 달라질 때만 `rover.py`의 `_create_*` 함수를 수정한다.
- driver 변경과 rover 변경을 한 번에 섞지 않는다.
- geometry 변경 후에는 먼저 직진 또는 waypoint 테스트로 기본 안정성을 본다.

## 다음 확장 포인트

- PID 기반 속도 제어 driver 추가
- Pure pursuit / Stanley path follower 추가
- terrain preset 분리
- rover 파라미터 YAML/JSON 로딩
---

## 2026-05-30 실험 재현 가이드

0530 추가분은 로버의 기본 주행 성능, 장애물 waypoint 주행, 강화학습 적용 가능성을 확인하기 위한 6개 실험으로 정리한다.

```text
실험 1 straight    : 평지 직진 안정성 테스트
실험 2 step_turn   : 평지 단계 조향 응답 테스트
실험 3 slalom      : 평지 반복 조향 응답 테스트
실험 4 pivot_turn  : 평지 좌우 속도차 회전 테스트
실험 5 waypoint    : 장애물 지형 waypoint 주행 테스트
실험 6 RL          : 강화학습 환경/정책 실행 테스트
```

실험 1~4는 장애물이 없는 평지에서 profile driver를 사용한다. 실험 5는 slope, step, rock이 있는 장애물 지형에서 waypoint driver를 사용한다. 실험 6은 Gymnasium wrapper와 PPO 학습/평가 스크립트로 RL 파이프라인이 실행되는지 확인한다.

### 공통 환경

프로젝트 루트 `C:\Project_Chrono`에서 실행한다.

```powershell
conda activate chrono
```

결과 파일은 기본적으로 아래 폴더에 저장된다.

```text
Project_Chrono_Practice/lessons/phase4/Dohee/custom_rover/results/
```

CSV에는 위치, yaw, 명령값, 바퀴/조향 상태가 기록된다. 0530 추가 이후에는 자세 분석을 위해 `roll_deg`, `pitch_deg`도 함께 기록된다.

### 실험 1~4: 평지 주행 성능 테스트

목적은 장애물 영향을 제거하고 로버 자체의 구동, 조향, 회전 응답을 비교하는 것이다. `flat_profile_experiments.py`가 4개 profile을 순서대로 실행한다.

```powershell
conda run -n chrono python Project_Chrono_Practice\lessons\phase4\Dohee\custom_rover\flat_profile_experiments.py
```

시뮬레이션 창을 보려면 `--visualize`를 추가한다.

```powershell
conda run -n chrono python Project_Chrono_Practice\lessons\phase4\Dohee\custom_rover\flat_profile_experiments.py --visualize
```

실행 설정:

```text
control_mode = "profiles"
terrain_mode = "flat"
```

결과 저장 위치:

```text
results/flat_profile_experiments/
```

생성 파일:

```text
custom_viper_flat_<experiment>.csv
custom_viper_flat_<experiment>_path.png
custom_viper_flat_<experiment>_response.png
flat_profile_summary.csv
flat_profile_summary.png
```

주요 정량 지표:

```text
duration_s
path_length_m
final_x_m
final_y_m
max_abs_y_m
yaw_change_deg
max_abs_yaw_rate_deg_s
mean_speed_m_s
max_speed_m_s
```

#### 실험 1: straight

일정한 전진 속도와 0 조향 명령을 입력한다. 좌우 구동계 균형과 직진 안정성을 확인한다.

확인 지표:

```text
final_y_m
max_abs_y_m
yaw_change_deg
mean_speed_m_s
```

`final_y_m`, `max_abs_y_m`, `yaw_change_deg`가 작을수록 의도하지 않은 횡방향 이동과 회전이 적다.

#### 실험 2: step_turn

일정 시간 직진 후 단계 조향 입력을 넣는다. 전륜 Ackermann-style 조향 구조의 회전 응답을 확인한다.

확인 지표:

```text
yaw_change_deg
max_abs_yaw_rate_deg_s
path_length_m
final_x_m
final_y_m
```

`yaw_change_deg`는 전체 회전량, `max_abs_yaw_rate_deg_s`는 조향 입력에 대한 회전 응답 강도를 나타낸다.

#### 실험 3: slalom

sine 형태의 반복 조향 입력을 넣는다. 연속 조향에 대한 좌우 회전 응답과 주행 안정성을 확인한다.

확인 지표:

```text
max_abs_y_m
yaw_change_deg
max_abs_yaw_rate_deg_s
path_length_m
mean_speed_m_s
```

`max_abs_y_m`은 좌우 이동 폭을 나타낸다. `response` 그래프의 yaw와 yaw rate를 함께 보면 반복 조향 응답을 확인할 수 있다.

#### 실험 4: pivot_turn

`turn_mode`를 사용하여 좌우 바퀴 속도 차이를 크게 만든다. 좁은 공간에서 회전할 수 있는지 확인한다.

확인 지표:

```text
yaw_change_deg
max_abs_yaw_rate_deg_s
final_x_m
final_y_m
path_length_m
```

`yaw_change_deg`가 클수록 회전 성능이 강하다. `final_x_m`, `final_y_m`, path 그래프를 함께 보면 제자리 회전에 가까운지 판단할 수 있다.

### 실험 5: waypoint 장애물 지형 실험

목적은 장애물 지형에서 waypoint driver가 목표점을 따라가며 slope, step, rock 구간을 통과하는지 확인하는 것이다.

`config.py`에서 아래 값으로 설정한다.

```python
control_mode = "waypoints"
terrain_mode = "obstacles"
experiment_name = "waypoint_obstacles"
```

실행:

```powershell
conda run -n chrono python Project_Chrono_Practice\lessons\phase4\Dohee\custom_rover\main.py
```

결과 저장 위치:

```text
results/
```

생성 파일:

```text
custom_viper_<experiment>.csv
custom_viper_<experiment>_path.png
custom_viper_<experiment>_attitude.png
```

확인 항목:

```text
path 그래프         : waypoint 추종 경로와 이탈 여부
roll_deg, pitch_deg : 장애물 통과 중 자세 변화
yaw_deg             : 진행 방향 변화와 흔들림
z                   : slope/step/rock 통과 중 높이 변화
```

장애물별 해석 기준:

```text
Slope 등판 : pitch 변화와 z 증가
Step 극복  : pitch peak, roll peak, z 변화
Rock 통과  : roll 변화, yaw 흔들림, 경로 이탈 여부
```

### 실험 6: RL 테스트

목적은 최적 policy 성능을 주장하는 것이 아니라, 강화학습을 적용할 수 있는 `reset()`/`step()` 환경과 PPO 학습/평가 흐름이 동작하는지 확인하는 것이다.

관련 파일:

```text
rl_gym_env.py
rl_train_ppo.py
rl_policy_demo.py
rl_driver_demo.py
```

Gymnasium 환경 구조:

```python
obs, info = env.reset()
obs, reward, terminated, truncated, info = env.step(action)
```

Action은 3차원 정규화 입력이다.

```text
action[0] in [-1, 1] -> speed_cmd
action[1] in [-1, 1] -> steering_cmd
action[2] in [-1, 1] -> turn_mode
```

Observation은 목표 waypoint까지의 상대 위치, heading error, 이전 명령값, waypoint 진행률을 포함한다.

짧은 PPO 학습:

```powershell
conda run -n chrono python Project_Chrono_Practice\lessons\phase4\Dohee\custom_rover\rl_train_ppo.py --timesteps 512 --episode-time 12
```

학습 결과:

```text
results/rl_training/ppo_custom_rover_flat.zip
results/rl_training/monitor_flat.csv.monitor.csv
```

저장된 policy 평가:

```powershell
conda run -n chrono python Project_Chrono_Practice\lessons\phase4\Dohee\custom_rover\rl_policy_demo.py --steps 300 --episode-time 15
```

시각화 평가:

```powershell
conda run -n chrono python Project_Chrono_Practice\lessons\phase4\Dohee\custom_rover\rl_policy_demo.py --steps 300 --episode-time 15 --visualize
```

평가 결과:

```text
results/rl_policy_demo/custom_viper_flat_ppo_policy.csv
results/rl_policy_demo/custom_viper_flat_ppo_policy_path.png
results/rl_policy_demo/custom_viper_flat_ppo_policy_attitude.png
```

장애물 지형에서 학습 또는 평가하려면 `--terrain obstacles`를 추가한다.

```powershell
conda run -n chrono python Project_Chrono_Practice\lessons\phase4\Dohee\custom_rover\rl_train_ppo.py --terrain obstacles --timesteps 512 --episode-time 12
conda run -n chrono python Project_Chrono_Practice\lessons\phase4\Dohee\custom_rover\rl_policy_demo.py --terrain obstacles --steps 300 --episode-time 15
```

### 재현 체크리스트

```text
1. conda 환경 chrono 활성화
2. 실험 1~4는 flat_profile_experiments.py 실행
3. 실험 5는 config.py에서 waypoints + obstacles 설정 후 main.py 실행
4. 실험 6은 rl_train_ppo.py로 학습 후 rl_policy_demo.py로 평가
5. CSV, path 그래프, response/attitude 그래프 생성 여부 확인
6. 실험별 지표를 summary CSV 또는 개별 CSV에서 비교
```


