# 2.2 Component 산출물 README

이 폴더는 Project Chrono 캡스톤 보고서의 **2.2 Component: 구현 대상별 부품 설계** 절을 작성하기 위한 Markdown, 예제 코드, 렌더링 이미지, 그래프, CSV를 모은 작업 폴더이다. Component는 Chrono API를 직접 호출하는 Command보다 한 단계 위의 재사용 가능한 부품 설계 단위로 정의했다.

## 읽는 순서

| 순서 | 파일 | 역할 |
|---:|---|---|
| 1 | `markdown/2.2.1_component_definition.md` | Command-Component-System 관계와 Component 정의 |
| 2 | `markdown/2.2.2_rover_vehicle_components.md` | Chassis, Wheel/Tire, Motor, Steering, Suspension, Vehicle/Tracked 확장 |
| 3 | `markdown/2.2.3_environment_terrain_components.md` | Ground, Obstacle, RigidTerrain, SCMTerrain, Contact Material, 확장 지형 |
| 4 | `markdown/2.2.4_collision_contact_components.md` | Collision Shape, Contact Reporter, Contact Force Logger, Event Detector |
| 5 | `markdown/2.2.5_data_visualization_components.md` | State/Control Logger, CSV Schema, Graph Generator, Render/Sensor |

## 코드

| 경로 | 설명 |
|---|---|
| `code/common/component_utils.py` | CSV 저장, matplotlib 3D 렌더, PyChrono import helper |
| `code/common/run_all_component_examples.py` | 모든 Component 예제 생성 스크립트 실행 |
| `code/rover_vehicle/generate_rover_vehicle_components.py` | 로버/차량 렌더, Chassis PyChrono probe CSV/그래프 생성 |
| `code/environment_terrain/generate_environment_terrain_components.py` | 지형 렌더, 높이/마찰/침하 CSV, 지형 그래프 생성 |
| `code/collision_contact/generate_collision_contact_components.py` | 충돌 렌더, 접촉력/접촉 개수/이벤트 CSV와 그래프 생성 |
| `code/data_visualization/generate_data_visualization_components.py` | 상태/제어 CSV, 궤적/입력 그래프, 센서 배치 렌더 생성 |

실행 명령:

```bash
conda activate chrono
source setup_chrono_env.sh
python 3-layer_report/Component/code/common/run_all_component_examples.py
```

## 렌더링 이미지

| 파일 | 설명 |
|---|---|
| `images/renders/rover_vehicle_component_overview.png` | Chassis, Wheel/Tire, Driveline, Steering 배치 |
| `images/renders/rover_visual_collision_shapes.png` | Visual Shape와 Collision Shape 분리 |
| `images/renders/rover_suspension_steering_components.png` | 서스펜션 링크와 바퀴 축 개념 |
| `images/renders/tracked_vehicle_components.png` | Track Shoe, Sprocket, Idler, Roller 확장 |
| `images/renders/terrain_ground_obstacle_components.png` | Ground, Obstacle, RigidTerrain patch |
| `images/renders/terrain_heightmap_component.png` | Heightmap terrain 개념 |
| `images/renders/terrain_scm_deformation_component.png` | SCMTerrain 침하/변형 개념 |
| `images/renders/collision_contact_components.png` | 이동 body, 장애물, 접촉력 벡터 |
| `images/renders/collision_visual_vs_collision_shape.png` | 충돌 envelope와 시각 mesh 차이 |
| `images/renders/data_visualization_sensor_components.png` | Camera, LiDAR, GPS/IMU 배치 |

## 그래프

| 파일 | 연결 CSV |
|---|---|
| `images/graphs/rover_vehicle_chassis_probe_graph.png` | `outputs/csv/rover_vehicle_chassis_probe.csv` |
| `images/graphs/terrain_height_sinkage_profile.png` | `outputs/csv/environment_terrain_height_friction_sinkage.csv` |
| `images/graphs/terrain_contact_material_friction_map.png` | `outputs/csv/environment_terrain_height_friction_sinkage.csv` |
| `images/graphs/terrain_contact_force_probe.png` | `outputs/csv/environment_terrain_contact_probe.csv` |
| `images/graphs/collision_contact_force_graph.png` | `outputs/csv/collision_contact_probe.csv` |
| `images/graphs/collision_contact_count_graph.png` | `outputs/csv/collision_contact_probe.csv` |
| `images/graphs/collision_event_timeline_graph.png` | `outputs/csv/collision_event_timeline.csv` |
| `images/graphs/data_visualization_state_trajectory.png` | `outputs/csv/data_visualization_state_log.csv` |
| `images/graphs/data_visualization_control_inputs.png` | `outputs/csv/data_visualization_control_log.csv` |

## CSV

| 파일 | 내용 |
|---|---|
| `outputs/csv/rover_vehicle_chassis_probe.csv` | Chassis 위치/속도 PyChrono probe |
| `outputs/csv/environment_terrain_height_friction_sinkage.csv` | heightmap, 마찰, SCM 침하 예시 |
| `outputs/csv/environment_terrain_contact_probe.csv` | ground 접촉력 PyChrono probe |
| `outputs/csv/collision_contact_probe.csv` | 충돌 접촉력, 접촉 개수, 접촉력 성분 |
| `outputs/csv/collision_event_timeline.csv` | first_contact 이벤트 |
| `outputs/csv/data_visualization_state_log.csv` | state logger 예시 |
| `outputs/csv/data_visualization_control_log.csv` | control logger 예시 |

## 실행 결과와 환경 기록

- 실행 성공: `run_all_component_examples.py` 전체 성공.
- PyChrono Core/Vehicle import: 성공.
- `pychrono.irrlicht` import: 성공. 다만 자동화된 창 캡처 대신 제출 안정성을 위해 matplotlib 3D 렌더를 저장했다.
- `pychrono.vsg3d` import: 실패. 현재 conda 환경에 VSG Python 모듈이 없다.
- `pychrono.sensor` import: 실패. 현재 conda 환경에 Sensor Python 모듈이 없다. Sensor Component는 선택적 확장 설계로만 설명했다.
- matplotlib: `chrono` 환경에 없어서 `python -m pip install matplotlib`로 설치 후 실행했다.

## 참고 문헌

- Project Chrono 공식 저장소: https://github.com/projectchrono/chrono
- Chrono Vehicle Terrain system: https://api.projectchrono.org/group__vehicle__terrain.html
- SCMTerrain class reference: https://api.projectchrono.org/9.0.0/classchrono_1_1vehicle_1_1_s_c_m_terrain.html
- Chrono Sensor overview: https://api.projectchrono.org/sensor_overview.html
- Chrono Visualization overview: https://api.projectchrono.org/vehicle_visualization.html
- 로컬 참고: `README.md`, `docs/core/`, `docs/vehicle/`, `docs/robot/`, `docs/visualization/`, `docs/postprocess/`, `lessons/phase4/hojin/`
