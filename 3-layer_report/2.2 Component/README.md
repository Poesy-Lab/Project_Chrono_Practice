# 2.2 Component

`2.2 Component`는 Command 단계의 Chrono API를 실제 구현 대상의 부품 단위로 묶어 설명한 보고서 폴더이다. 로버/차량, 환경/Terrain, 충돌/접촉 측정, 데이터 출력/시각화 Component를 각각 독립 문서로 나누고, 관련 코드와 렌더 이미지, 그래프, CSV 산출물을 함께 보관한다.

## 파일 목록

- [2.2.1 Component 단계의 정의와 역할](2.2.1_component_definition.md)
- [2.2.2 로버/차량 Component 설계](2.2.2_rover_vehicle_components.md)
- [2.2.3 환경/Terrain Component 설계](2.2.3_environment_terrain_components.md)
- [2.2.4 충돌/접촉 측정 Component 설계](2.2.4_collision_contact_components.md)
- [2.2.5 데이터 출력/시각화 Component 설계](2.2.5_data_visualization_components.md)

## 읽는 순서

| 순서 | 문서 | 핵심 내용 |
| --- | --- | --- |
| 1 | `2.2.1_component_definition.md` | Component 단계의 의미, Command와 System 사이의 역할, 설명 기준 |
| 2 | `2.2.2_rover_vehicle_components.md` | Chassis, wheel/tire, joint, motor, steering, suspension, visual/collision shape |
| 3 | `2.2.3_environment_terrain_components.md` | Ground, obstacle, contact material, RigidTerrain, heightmap, SCMTerrain |
| 4 | `2.2.4_collision_contact_components.md` | Collision shape, contact material, reporter, force logger, event detector |
| 5 | `2.2.5_data_visualization_components.md` | CSV schema, state/control/contact logging, graph generation, screenshot/sensor output |

## 산출물 구조

| 폴더 | 역할 |
| --- | --- |
| [code/](code/) | Component 예시 코드와 이미지/그래프 생성 스크립트 |
| [code/common/](code/common/) | 공통 유틸리티, 전체 실행 스크립트, VSG/Irrlicht 관련 보조 코드 |
| [images/renders/](images/renders/) | Component별 렌더링 이미지 |
| [images/graphs/](images/graphs/) | CSV 또는 예시 데이터 기반 그래프 |
| [images/mermaid_rendered/](images/mermaid_rendered/) | Mermaid 관계도 원본 `.mmd`와 렌더링 이미지 |
| [outputs/csv/](outputs/csv/) | 예시 코드 실행으로 생성된 CSV 데이터 |
| [outputs/raw/](outputs/raw/) | 실행 로그와 실험용 원본 이미지 |

## 대표 시각 자료

| 로버/차량 | 환경/Terrain |
| --- | --- |
| ![로버 Component 개요](images/renders/rover_vehicle_component_overview.png) | ![지형 Component](images/renders/terrain_ground_obstacle_components.png) |

| 충돌/접촉 | 데이터/센서 |
| --- | --- |
| ![충돌 Component](images/renders/collision_contact_components.png) | ![센서 Component](images/renders/data_visualization_sensor_components.png) |

## 코드 실행

전체 Component 예시를 다시 생성하려면 프로젝트 루트에서 Chrono 환경을 활성화한 뒤 다음 스크립트를 실행한다.

```bash
conda activate chrono
source setup_chrono_env.sh
python "3-layer_report/2.2 Component/code/common/run_all_component_examples.py"
```

개별 영역만 다시 생성할 때는 아래 스크립트를 사용한다.

| 영역 | 실행 스크립트 |
| --- | --- |
| 로버/차량 | `code/rover_vehicle/generate_rover_vehicle_components.py` |
| 환경/Terrain | `code/environment_terrain/generate_environment_terrain_components.py` |
| 충돌/접촉 | `code/collision_contact/generate_collision_contact_components.py` |
| 데이터/시각화 | `code/data_visualization/generate_data_visualization_components.py` |
| Chrono 기본 형상 | `code/common/generate_chrono_default_shapes.py` |
| Chrono 내장 차량/로봇 asset | `code/common/generate_chrono_builtin_component_assets.py` |

## 문서 작성 기준

각 Component 문서는 같은 흐름을 따른다.

1. Component가 어떤 구현 대상을 표현하는지 설명한다.
2. 관련 Chrono API와 Command 단계의 연결 관계를 정리한다.
3. 코드 예시로 구현 절차를 보여준다.
4. 렌더 이미지와 그래프를 통해 물리적 의미를 확인한다.
5. CSV/로그 등 데이터 산출물이 있으면 검증 기준과 함께 제시한다.

