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

## 2026-05-30 추가: 평지 Profile 주행 평가 실험 1~4

캡스톤디자인 보고서에서 로버의 기본 주행 성능을 정량적으로 설명하기 위해,
장애물 지형과 분리된 **평지 전용 profile driver 실험**을 추가하였다.

기존 waypoint 실험은 목표점을 따라가는 closed-loop 경로 추종 평가이고,
이번 실험 1~4는 미리 정한 입력을 시간에 따라 넣는 open-loop profile 평가이다.
따라서 slope, step, rock 같은 장애물은 생성하지 않고 평탄 지형에서 수행한다.
이렇게 하면 장애물 접촉 영향 없이 로버 자체의 구동, 조향, 회전 응답을 비교할 수 있다.

### 추가된 실행 파일

```text
flat_profile_experiments.py
```

이 파일은 아래 4개 실험을 순서대로 자동 실행하고, 각 실험의 CSV와 그래프를 저장한다.

```text
1. straight
2. step_turn
3. slalom
4. pivot_turn
```

### 실행 방법

그래프와 CSV만 빠르게 생성:

```powershell
conda run -n chrono python Project_Chrono_Practice\lessons\phase4\Dohee\custom_rover\flat_profile_experiments.py
```

Chrono 시뮬레이션 창을 보면서 실행:

```powershell
conda run -n chrono python Project_Chrono_Practice\lessons\phase4\Dohee\custom_rover\flat_profile_experiments.py --visualize
```

Matplotlib 그래프 창까지 같이 표시:

```powershell
conda run -n chrono python Project_Chrono_Practice\lessons\phase4\Dohee\custom_rover\flat_profile_experiments.py --visualize --show-plots
```

### 결과 저장 위치

```text
results/flat_profile_experiments/
```

각 실험마다 다음 파일이 생성된다.

```text
custom_viper_flat_<experiment>.csv
custom_viper_flat_<experiment>_path.png
custom_viper_flat_<experiment>_response.png
```

전체 요약 결과는 다음 파일에 저장된다.

```text
flat_profile_summary.csv
flat_profile_summary.png
```

`_path.png`는 로버의 실제 x-y 이동 경로를 보여준다.
Profile driver 실험은 waypoint를 쓰지 않으므로, 이 그래프에는 waypoint marker를 표시하지 않는다.

`_response.png`는 시간에 따른 입력과 응답을 함께 보여준다.

```text
speed command / estimated speed
steering command / turn mode
yaw / yaw rate
x, y position
```

`flat_profile_summary.csv`에는 보고서 표로 쓰기 좋은 정량 지표가 저장된다.

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

### 실험 1: Straight 주행 안정성

`straight` 실험은 일정한 속도 명령과 0 조향 명령을 주어 로버가 평지에서 직진하는지 확인한다.

목적:

```text
좌우 구동계 균형 확인
기본 차체 안정성 확인
조향 명령이 없을 때 lateral drift가 작은지 확인
```

보고서에서 사용할 주요 지표:

```text
final_y_m
max_abs_y_m
yaw_change_deg
mean_speed_m_s
```

해석 기준:

```text
final_y_m과 max_abs_y_m이 작을수록 직진성이 좋다.
yaw_change_deg가 작을수록 의도하지 않은 회전이 적다.
```

### 실험 2: Step Turn 조향 응답

`step_turn` 실험은 일정 시간 직진 후 조향 명령을 단계적으로 넣어 회전 응답을 확인한다.

목적:

```text
전륜 Ackermann-style 조향 구조의 응답 확인
조향 입력에 따른 yaw 변화 확인
회전 경로와 안정성 확인
```

보고서에서 사용할 주요 지표:

```text
yaw_change_deg
max_abs_yaw_rate_deg_s
path_length_m
final_x_m, final_y_m
```

해석 기준:

```text
yaw_change_deg는 전체 회전량을 나타낸다.
max_abs_yaw_rate_deg_s는 조향 입력에 대한 회전 응답 강도를 나타낸다.
경로 그래프를 통해 회전 반경과 궤적이 자연스러운지 확인한다.
```

### 실험 3: Slalom 반복 조향 응답

`slalom` 실험은 sine 형태의 조향 입력을 넣어 좌우 반복 회전 응답을 확인한다.

목적:

```text
연속 조향 입력에 대한 로버의 추종성 확인
좌우 반복 회전 중 자세 안정성 확인
profile driver 기반 반복 실험 결과 확보
```

보고서에서 사용할 주요 지표:

```text
max_abs_y_m
yaw_change_deg
max_abs_yaw_rate_deg_s
path_length_m
mean_speed_m_s
```

해석 기준:

```text
max_abs_y_m은 slalom 중 좌우 이동 폭을 나타낸다.
yaw와 yaw rate 그래프를 통해 반복 조향에 대한 회전 응답을 확인한다.
path 그래프에는 waypoint가 없으며, open-loop 입력에 의해 형성된 실제 주행 궤적만 표시한다.
```

### 실험 4: Pivot Turn 회전 성능

`pivot_turn` 실험은 turn_mode를 사용하여 좌우 바퀴 속도 차이를 크게 만들고 강한 회전 동작을 확인한다.

목적:

```text
4륜 구동 및 좌우 분리 속도 제어 구조 확인
turn_mode 기반 회전 성능 확인
좁은 공간 회전 가능성 평가
```

보고서에서 사용할 주요 지표:

```text
yaw_change_deg
max_abs_yaw_rate_deg_s
final_x_m, final_y_m
path_length_m
```

해석 기준:

```text
yaw_change_deg가 클수록 회전 성능이 강하다.
final_x_m, final_y_m과 path 그래프를 함께 보면 제자리 회전에 가까운지, 전진 이동이 많이 섞였는지 판단할 수 있다.
```

### 코드 변경 요약

`config.py`에는 평지/장애물 지형을 선택하기 위한 `terrain_mode`가 추가되었다.

```python
terrain_mode = "obstacles"  # obstacles, flat
```

`rover.py`는 `terrain_mode == "flat"`일 때 slope, step, rock obstacle을 만들지 않는다.

```text
flat      : ground만 생성
obstacles : ground + slope + step + rock 생성
```

`simulation.py`에는 batch 실행용 `run_simulation_case()`가 추가되었다.
이 함수는 실험 이름, 지형 모드, 시각화 여부, 결과 저장 폴더를 인자로 받아 한 번의 실험을 수행한다.

`flat_profile_experiments.py`는 실험 1~4를 자동 실행하고 결과 그래프와 summary 파일을 생성한다.
---

## 2026-05-30 추가: RL Driver Interface

커스텀 로버에 강화학습 정책을 연결할 수 있도록 최소 형태의 `RLDriver` 인터페이스를 추가하였다.
현재 단계에서는 실제 학습된 모델을 사용하지 않고, waypoint를 향해 이동하는 dummy policy를 사용한다.
이 구조는 이후 PyTorch, Stable-Baselines3, ONNX policy 등으로 교체할 수 있는 연결 지점이다.

### 추가된 파일

```text
rl_driver_demo.py
```

### 실행 방법

평지에서 dummy RL driver 실행:

```powershell
conda run -n chrono python Project_Chrono_Practice\lessons\phase4\Dohee\custom_rover\rl_driver_demo.py
```

시뮬레이션 창을 보면서 실행:

```powershell
conda run -n chrono python Project_Chrono_Practice\lessons\phase4\Dohee\custom_rover\rl_driver_demo.py --visualize
```

장애물 지형에서 실행:

```powershell
conda run -n chrono python Project_Chrono_Practice\lessons\phase4\Dohee\custom_rover\rl_driver_demo.py --terrain obstacles --visualize
```

실행 시간을 바꾸고 싶으면:

```powershell
conda run -n chrono python Project_Chrono_Practice\lessons\phase4\Dohee\custom_rover\rl_driver_demo.py --sim-time 15
```

### 결과 저장 위치

```text
results/rl_driver_demo/
```

생성 파일:

```text
custom_viper_<terrain>_rl_dummy.csv
custom_viper_<terrain>_rl_dummy_path.png
```

### Driver 구조

`drivers.py`에 `RLDriver` 클래스가 추가되었다.
RL driver는 매 timestep마다 rover 상태를 observation으로 만들고, policy가 action을 반환한다고 가정한다.

Observation 예:

```text
x
y
yaw_rad
target_x
target_y
dx
dy
local_x
local_y
distance_to_target
heading_error
previous_speed_cmd
previous_steering_cmd
previous_turn_mode
```

Action 형식:

```text
action[0] -> speed_cmd
action[1] -> steering_cmd
action[2] -> turn_mode
```

최종적으로 action은 기존 rover 제어 입력과 같은 `DriverInputs`로 변환된다.

```python
DriverInputs(
    speed_cmd=...,
    steering_cmd=...,
    turn_mode=...,
)
```

### 현재 dummy policy의 의미

현재 `RLDriver`의 dummy policy는 학습된 RL 모델이 아니다.
다만 실제 RL policy가 들어갈 위치와 입출력 구조를 검증하기 위한 rule-based policy이다.

보고서에서는 다음과 같이 설명할 수 있다.

```text
본 프로젝트에서는 향후 강화학습 기반 자율주행 제어기로 확장할 수 있도록
observation-action 구조를 갖는 RL driver interface를 설계하였다.
현재 구현에서는 학습된 policy 대신 dummy policy를 사용하여
DriverInputs 연결 구조와 시뮬레이션 실행 가능성을 검증하였다.
```

### 이후 확장 방향

```text
1. reward 설계
2. Gymnasium 환경 wrapper 작성
3. reset/step 함수 분리
4. 학습된 policy를 RLDriver(policy=...)에 연결
5. waypoint driver와 RL driver의 경로 추종 성능 비교
```
---

## 2026-05-30 추가: Gymnasium RL 학습 Wrapper

`RLDriver`는 policy를 연결하는 driver interface이고,
`CustomRoverRLEnv`는 실제 강화학습 알고리즘이 사용할 수 있는 Gymnasium 환경 wrapper이다.

추가된 파일:

```text
rl_gym_env.py
rl_train_ppo.py
rl_policy_demo.py
```

### Gymnasium 환경 구조

`rl_gym_env.py`의 `CustomRoverRLEnv`는 다음 Gymnasium API를 제공한다.

```python
obs, info = env.reset()
obs, reward, terminated, truncated, info = env.step(action)
```

Action은 학습이 쉽도록 정규화된 3차원 벡터를 사용한다.

```text
action[0] in [-1, 1] -> speed_cmd in [-max_speed, max_speed]
action[1] in [-1, 1] -> steering_cmd in [-1, 1]
action[2] in [-1, 1] -> turn_mode in [0, 1]
```

Observation은 10차원 벡터이다.

```text
x
y
local_x
local_y
distance_to_target
sin(heading_error)
cos(heading_error)
previous_speed_cmd
previous_steering_cmd
waypoint_fraction
```

Reward는 다음 요소를 사용한다.

```text
목표 waypoint에 가까워진 거리 progress
heading error penalty
action 크기 penalty
waypoint 도달 bonus
최종 goal 도달 bonus
```
`r`n### PPO 학습

`stable-baselines3`의 PPO를 사용하여 학습을 시작할 수 있다.

짧은 테스트 학습:

```powershell
conda run -n chrono python Project_Chrono_Practice\lessons\phase4\Dohee\custom_rover\rl_train_ppo.py --timesteps 512 --episode-time 12
```

더 길게 학습하려면 `--timesteps`를 늘린다.

```powershell
conda run -n chrono python Project_Chrono_Practice\lessons\phase4\Dohee\custom_rover\rl_train_ppo.py --timesteps 10000 --episode-time 20
```

학습 결과 저장 위치:

```text
results/rl_training/
```

생성 파일 예:

```text
ppo_custom_rover_flat.zip
monitor_flat.csv.monitor.csv
```

### 학습된 Policy 평가

저장된 PPO policy를 불러와 deterministic action으로 평가한다.

```powershell
conda run -n chrono python Project_Chrono_Practice\lessons\phase4\Dohee\custom_rover\rl_policy_demo.py --steps 300 --episode-time 15
```

시뮬레이션 창을 보면서 평가하려면:

```powershell
conda run -n chrono python Project_Chrono_Practice\lessons\phase4\Dohee\custom_rover\rl_policy_demo.py --steps 300 --episode-time 15 --visualize
```

평가가 끝나면 다음 결과가 저장된다.

```text
results/rl_policy_demo/custom_viper_<terrain>_ppo_policy.csv
results/rl_policy_demo/custom_viper_<terrain>_ppo_policy_path.png
results/rl_policy_demo/custom_viper_<terrain>_ppo_policy_attitude.png
```

장애물 지형용 모델을 평가하려면:

```powershell
conda run -n chrono python Project_Chrono_Practice\lessons\phase4\Dohee\custom_rover\rl_policy_demo.py --terrain obstacles
```

### 현재 구현의 의미

현재 단계에서 완성된 것은 다음이다.

```text
1. RL action interface
2. Gymnasium reset/step wrapper
3. reward 구조
4. stable-baselines3 PPO 학습 스크립트
5. 저장된 policy 평가 스크립트
```

아직 최적 성능을 내는 policy를 학습한 것은 아니다.
보고서에서는 "강화학습 적용을 위한 시뮬레이션 환경과 학습 인터페이스를 구축하고,
짧은 PPO 학습 실행을 통해 학습 파이프라인이 동작함을 확인하였다"라고 정리하는 것이 정확하다.
---

## 2026-05-30 추가: 자세 로그와 Attitude 그래프

장애물 통과 실험에서 자세 변화를 분석할 수 있도록 CSV 로그에 roll/pitch 컬럼을 추가하였다.

추가된 CSV 컬럼:

```text
roll_deg
pitch_deg
```

기존 `yaw_deg`와 함께 사용하면 장애물 통과 중 차체 자세 변화를 분석할 수 있다.

```text
roll_deg  : 좌우 기울어짐
pitch_deg : 전후 기울어짐
yaw_deg   : 수평면 회전 방향
z         : 차체 높이 변화
```

시뮬레이션 종료 후 path 그래프와 별도로 attitude 그래프가 자동 저장된다.

```text
custom_viper_<terrain>_<experiment>_attitude.png
```

그래프 구성:

```text
roll / pitch vs time
yaw vs time
z position vs time
```

보고서의 장애물 통과 실험에서는 다음 항목에 사용할 수 있다.

```text
Slope 등판      : pitch 변화와 z 변화
Step 극복       : pitch/roll peak와 z 변화
Rock 통과       : roll 변화와 yaw 흔들림
자세 안정성     : roll_deg, pitch_deg의 최대값과 진동 정도
```

