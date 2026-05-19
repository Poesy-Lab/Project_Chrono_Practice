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
