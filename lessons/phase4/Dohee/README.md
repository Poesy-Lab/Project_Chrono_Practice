# Phase 4 Dohee

이 폴더는 Phase 4의 커스텀 로버 설계 예제를 담고 있다.

## 시작점

- 권장 실행 파일: `custom_rover.py`
- 실제 구조화된 코드: `custom_rover/`

## 빠른 실행

```powershell
conda activate chrono
python lessons/phase4/Dohee/custom_rover.py
```

## 읽는 순서

1. `custom_rover/README.md`
2. `custom_rover/config.py`
3. `custom_rover/drivers.py`
4. `custom_rover/rover.py`
5. `custom_rover/simulation.py`

## 구조 원칙

- 로버 형상/기구는 `rover.py`
- 입력 생성은 `drivers.py`
- 실행과 저장은 `simulation.py`
- 파라미터 선택은 `config.py`

## 드라이버를 바꾸려면

가장 먼저 [custom_rover/config.py](/C:/Project_Chrono/Project_Chrono_Practice/lessons/phase4/Dohee/custom_rover/config.py:1) 의 `SimulationConfig`를 본다.

- `control_mode = "waypoints"` 이면 waypoint driver 사용
- `control_mode = "profiles"` 이면 시간 기반 profile driver 사용
- `experiment_name = "..."` 으로 profile 종류 선택

새 profile을 추가하려면 [custom_rover/drivers.py](/C:/Project_Chrono/Project_Chrono_Practice/lessons/phase4/Dohee/custom_rover/drivers.py:1) 에 함수와 `EXPERIMENTS` 등록을 추가하면 된다.

자세한 설명은 [custom_rover/README.md](/C:/Project_Chrono/Project_Chrono_Practice/lessons/phase4/Dohee/custom_rover/README.md:1) 에 정리해뒀다.

## 로버를 커스텀하려면

가장 먼저 보는 파일은 두 개다.

- [custom_rover/config.py](/C:/Project_Chrono/Project_Chrono_Practice/lessons/phase4/Dohee/custom_rover/config.py:1)
- [custom_rover/rover.py](/C:/Project_Chrono/Project_Chrono_Practice/lessons/phase4/Dohee/custom_rover/rover.py:1)

기본 원칙은 이렇다.

- 크기, 질량, 바퀴 반지름, wheelbase 같은 수치 변경은 `config.py`
- 차체 생성, 바퀴 생성, 조향/구동 구조 변경은 `rover.py`
- 지형 수정은 `rover.py`의 ground/terrain 생성 함수

자세한 커스텀 순서와 체크리스트는 [custom_rover/README.md](/C:/Project_Chrono/Project_Chrono_Practice/lessons/phase4/Dohee/custom_rover/README.md:1) 에 추가해뒀다.
---

## 2026-05-30 추가: 평지 주행 평가 실험 1~4

캡스톤디자인 보고서용으로, 기존 장애물 waypoint 주행과 별도로 **장애물 없는 평지 profile 실험**을 추가하였다.

목적은 slope, step, rock 같은 지형 영향을 제거하고, 로버 자체의 기본 구동/조향/회전 응답을 정량적으로 확인하는 것이다.

추가된 실행 파일:

- [custom_rover/flat_profile_experiments.py](/C:/Project_Chrono/Project_Chrono_Practice/lessons/phase4/Dohee/custom_rover/flat_profile_experiments.py:1)

자동 실행되는 실험:

```text
1. straight   : 직진 안정성 평가
2. step_turn  : 단계 조향 입력에 대한 회전 응답 평가
3. slalom     : 반복 조향 입력에 대한 주행 응답 평가
4. pivot_turn : 좌우 바퀴 속도 차이를 이용한 회전 성능 평가
```

빠른 실행:

```powershell
conda run -n chrono python Project_Chrono_Practice\lessons\phase4\Dohee\custom_rover\flat_profile_experiments.py
```

시뮬레이션 창을 보면서 실행:

```powershell
conda run -n chrono python Project_Chrono_Practice\lessons\phase4\Dohee\custom_rover\flat_profile_experiments.py --visualize
```

결과 저장 위치:

- [custom_rover/results/flat_profile_experiments](/C:/Project_Chrono/Project_Chrono_Practice/lessons/phase4/Dohee/custom_rover/results/flat_profile_experiments)

생성 결과:

```text
custom_viper_flat_<experiment>.csv
custom_viper_flat_<experiment>_path.png
custom_viper_flat_<experiment>_response.png
flat_profile_summary.csv
flat_profile_summary.png
```

Profile driver 실험은 waypoint를 사용하지 않으므로, path 그래프에는 waypoint marker를 표시하지 않는다.
Waypoint marker는 기존 waypoint/obstacle 실험 그래프에서만 표시된다.

상세 실험 목적, 지표, 해석 기준은 [custom_rover/README.md](/C:/Project_Chrono/Project_Chrono_Practice/lessons/phase4/Dohee/custom_rover/README.md:552) 하단의 `2026-05-30 추가: 평지 Profile 주행 평가 실험 1~4` 섹션에 정리되어 있다.
---

## 2026-05-30 추가: RL Driver Interface

커스텀 로버에 강화학습 정책을 연결하기 위한 최소 형태의 RL driver interface를 추가하였다.
현재는 학습된 모델이 아니라 dummy policy를 사용하지만, observation/action 구조는 실제 RL policy로 교체할 수 있도록 분리되어 있다.

추가된 실행 파일:

- [custom_rover/rl_driver_demo.py](/C:/Project_Chrono/Project_Chrono_Practice/lessons/phase4/Dohee/custom_rover/rl_driver_demo.py:1)

기본 실행:

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

결과 저장 위치:

- [custom_rover/results/rl_driver_demo](/C:/Project_Chrono/Project_Chrono_Practice/lessons/phase4/Dohee/custom_rover/results/rl_driver_demo)

핵심 구조:

```text
observation
    -> RL policy 또는 dummy policy
    -> action(speed_cmd, steering_cmd, turn_mode)
    -> DriverInputs
    -> rover.synchronize()
```

상세 내용은 [custom_rover/README.md](/C:/Project_Chrono/Project_Chrono_Practice/lessons/phase4/Dohee/custom_rover/README.md:1)의 `2026-05-30 추가: RL Driver Interface` 섹션에 정리되어 있다.
---

## 2026-05-30 추가: Gymnasium RL 학습 Wrapper

RL driver interface 다음 단계로, 실제 강화학습 알고리즘이 사용할 수 있는 Gymnasium wrapper를 추가하였다.

추가된 파일:

- [custom_rover/rl_gym_env.py](/C:/Project_Chrono/Project_Chrono_Practice/lessons/phase4/Dohee/custom_rover/rl_gym_env.py:1)
- [custom_rover/rl_train_ppo.py](/C:/Project_Chrono/Project_Chrono_Practice/lessons/phase4/Dohee/custom_rover/rl_train_ppo.py:1)
- [custom_rover/rl_policy_demo.py](/C:/Project_Chrono/Project_Chrono_Practice/lessons/phase4/Dohee/custom_rover/rl_policy_demo.py:1)
`r`n
PPO 학습:

```powershell
conda run -n chrono python Project_Chrono_Practice\lessons\phase4\Dohee\custom_rover\rl_train_ppo.py --timesteps 512 --episode-time 12
```

저장된 policy 평가:

```powershell
conda run -n chrono python Project_Chrono_Practice\lessons\phase4\Dohee\custom_rover\rl_policy_demo.py --steps 300 --episode-time 15
```

학습된 policy를 시각화하면서 평가:

```powershell
conda run -n chrono python Project_Chrono_Practice\lessons\phase4\Dohee\custom_rover\rl_policy_demo.py --steps 300 --episode-time 15 --visualize
```

평가 결과는 [custom_rover/results/rl_policy_demo](/C:/Project_Chrono/Project_Chrono_Practice/lessons/phase4/Dohee/custom_rover/results/rl_policy_demo)에 CSV, path 그래프, attitude 그래프로 저장된다.

결과 저장 위치:

- [custom_rover/results/rl_training](/C:/Project_Chrono/Project_Chrono_Practice/lessons/phase4/Dohee/custom_rover/results/rl_training)

이 단계는 최적 policy 완성이 아니라, 강화학습을 적용할 수 있는 `reset()`/`step()`/reward 학습 파이프라인 구축이다.
상세 observation, action, reward 설명은 [custom_rover/README.md](/C:/Project_Chrono/Project_Chrono_Practice/lessons/phase4/Dohee/custom_rover/README.md:1)의 `2026-05-30 추가: Gymnasium RL 학습 Wrapper` 섹션에 정리되어 있다.
---

## 2026-05-30 추가: 자세 로그와 Attitude 그래프

장애물 통과 결과 분석을 위해 custom rover CSV 로그에 `roll_deg`, `pitch_deg` 컬럼을 추가하였다.
기존 `yaw_deg`, `z`와 함께 사용하여 slope, step, rock 통과 중 자세 변화를 정량적으로 볼 수 있다.

자동 생성 그래프:

```text
custom_viper_<terrain>_<experiment>_attitude.png
```

그래프에는 다음 값이 포함된다.

```text
roll / pitch vs time
yaw vs time
z position vs time
```

상세 설명은 [custom_rover/README.md](/C:/Project_Chrono/Project_Chrono_Practice/lessons/phase4/Dohee/custom_rover/README.md:1)의 `2026-05-30 추가: 자세 로그와 Attitude 그래프` 섹션에 정리되어 있다.

