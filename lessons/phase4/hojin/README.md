# Hojin Rover - Phase 4

Phase 4의 목표는 박호진 개인 로버를 작은 단위부터 직접 만들고, Phase 5에서 여러 로버가 같은 환경에 들어갈 수 있도록 기본 인터페이스를 정리하는 것입니다.

## MVP 단계

| 단계 | 목표 | 현재 파일 |
|------|------|-----------|
| MVP0 | 단일 차체 강체 + 충돌 + CSV 로그 | `lesson_19_hojin_rover_mvp0_collision_dummy.py` |
| MVP1 | 바퀴/트랙 구조를 분리하고 로버 파라미터 정리 | 예정 |
| MVP2 | 구동 입력, 조향 또는 좌우 차동 구동 추가 | 예정 |
| MVP3 | 지형 위 주행, 센서/결과 출력 포맷 정리 | 예정 |

## MVP0 실행

```bash
conda activate chrono
source setup_chrono_env.sh
python lessons/phase4/hojin/lesson_19_hojin_rover_mvp0_collision_dummy.py
```

창 없이 CSV만 만들려면 다음처럼 실행합니다.

```bash
python lessons/phase4/hojin/lesson_19_hojin_rover_mvp0_collision_dummy.py --no-vis
```

VSG가 계속 불안정하면 Irrlicht를 강제로 선택합니다.

```bash
python lessons/phase4/hojin/lesson_19_hojin_rover_mvp0_collision_dummy.py --vis-backend irrlicht
```

## MVP0 성공 기준

- `hojin_rover_mvp0`이라는 이름의 로버 body가 생성된다.
- 로버가 고정 장애물과 실제 충돌한다.
- 시간, 위치, 속도, 전체 접촉력, 목표물 접촉 개수가 CSV로 저장된다.
- 나중에 Phase 5에서 이 로버를 공통 환경에 불러오기 위한 크기, 질량, 이름, 로그 컬럼이 정해진다.
