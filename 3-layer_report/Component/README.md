# 2.2 Component 산출물 README

이 폴더는 Project Chrono 캡스톤 보고서의 **2.2 Component: 구현 대상별 부품 설계** 절을 작성하기 위한 Markdown, 예제 코드, 구조 이미지, 그래프, CSV를 모은 작업 폴더이다.

이번 정리 원칙은 다음과 같다.

- 실제 VSG/Irrlicht 수동 캡처 이미지는 `images/renders/manual_chrono/`에 별도로 저장한다.
- 현재 `images/renders/*.png`에는 VSG 기반 Component 렌더와 matplotlib 기반 구조 이미지가 함께 들어 있다. VSG 생성이 가능한 장면은 VSG 스크린샷을 우선 사용하고, 실패할 때만 matplotlib 구조 이미지로 대체한다.
- CSV와 그래프는 PyChrono/Core 예제 또는 deterministic probe로 생성해 보고서 해석 근거로 사용한다.
- deterministic probe는 PyChrono 모듈이 없는 환경에서도 같은 CSV schema와 그래프 해석 흐름을 재현하기 위한 대체 산출물이다.

## 읽는 순서

| 순서 | 파일 | 역할 |
|---:|---|---|
| 1 | `markdown/2.2.1_component_definition.md` | Command-Component-System 관계와 Component 정의 |
| 2 | `markdown/2.2.2_rover_vehicle_components.md` | Chassis, Wheel/Tire, Motor, Steering, Suspension, Visual/Collision Shape, Vehicle/Robot/Tracked 확장 |
| 3 | `markdown/2.2.3_environment_terrain_components.md` | Ground, Obstacle, Contact Material, RigidTerrain, Heightmap/Mesh, SCMTerrain, 고급 지형 |
| 4 | `markdown/2.2.4_collision_contact_components.md` | Collision Shape, Contact Reporter, Contact Force Logger, Event Detector, Debug Visualization |
| 5 | `markdown/2.2.5_data_visualization_components.md` | State/Control/Contact Logger, CSV Schema, Metadata, Graph Generator, Render/Sensor |

## 코드

| 경로 | 설명 |
|---|---|
| `code/common/component_utils.py` | CSV 저장, matplotlib 기반 구조 이미지 생성, PyChrono import helper |
| `code/common/generate_chrono_default_shapes.py` | Chrono 기본 형상 선택용 구조 이미지 생성 |
| `code/common/generate_chrono_builtin_component_assets.py` | Chrono 제공 vehicle/robot component mesh preview 생성 |
| `code/common/run_all_component_examples.py` | 모든 Component 예제 생성 스크립트 실행 |
| `code/rover_vehicle/generate_rover_vehicle_components.py` | 로버/차량 렌더, Chassis 상태 probe CSV/그래프 생성 |
| `code/environment_terrain/generate_environment_terrain_components.py` | 지형 구조 이미지, 높이/마찰/침하 CSV, 지형 그래프 생성 |
| `code/collision_contact/generate_collision_contact_components.py` | 충돌 구조 이미지, pair 접촉력/접촉 개수/이벤트 CSV와 그래프 생성 |
| `code/data_visualization/generate_data_visualization_components.py` | 상태/제어 CSV, 궤적/입력 그래프, 센서 배치 구조 이미지 생성 |

실행 명령:

```bash
source /opt/homebrew/anaconda3/etc/profile.d/conda.sh
conda activate chrono
source setup_chrono_env.sh
python 3-layer_report/Component/code/common/run_all_component_examples.py
```

## 직접 캡처 렌더 이미지

사용자가 직접 캡처한 Chrono VSG/Irrlicht 이미지는 아래 폴더에 저장한다.

```text
images/renders/manual_chrono/
```

본문에서 기대하는 대표 파일명:

| 파일명 | 연결 Component |
|---|---|
| `rover_chassis_overview_vsg.png` | Chassis |
| `rover_wheel_tire_component_vsg.png` | Wheel/Tire |
| `rover_motor_drive_direction_vsg.png` | Motor/Drive |
| `rover_suspension_links_vsg.png` | Suspension |
| `rover_collision_shape_debug_vsg.png` | Collision Shape |
| `terrain_ground_component_vsg.png` | Ground |
| `terrain_obstacle_component_vsg.png` | Obstacle |
| `terrain_rigid_patch_vsg.png` | RigidTerrain |
| `terrain_scm_sinkage_vsg.png` | SCMTerrain |
| `collision_contact_force_debug_vsg.png` | Contact force debug |
| `data_sensor_layout_vsg.png` | Sensor/Render layout |

## 구조 이미지

| 파일 | 설명 |
|---|---|
| `images/renders/chrono_default_shape_types.png` | Box, sphere, cylinder, capsule, ellipsoid, triangle mesh 기본 형상 |
| `images/renders/chrono_builtin_wheeled_vehicle_assets.png` | HMMWV chassis, rim, tire visual asset preview |
| `images/renders/chrono_builtin_tracked_vehicle_assets.png` | M113 chassis, sprocket, road wheel, track shoe visual asset preview |
| `images/renders/chrono_builtin_robot_rover_assets.png` | Viper/Curiosity chassis와 wheel visual asset preview |
| `images/renders/rover_vehicle_component_overview.png` | Chassis 기준 body와 하위 부품 상대 배치 isometric 렌더 |
| `images/renders/rover_payload_sensor_mount_component.png` | Payload, sensor mast, camera/LiDAR/GPS-IMU 기준점 배치 |
| `images/renders/rover_wheel_tire_component.png` | Wheel/Tire, rim/축 기준, 지형 contact patch 구조 |
| `images/renders/rover_axle_joint_component.png` | Axle, revolute joint frame, wheel 회전축 방향 |
| `images/renders/rover_motor_drive_component.png` | Motor/powertrain, driveline, brake 위치 구분 |
| `images/renders/rover_steering_component.png` | Steering rack/tie rod와 wheel heading 변화 |
| `images/renders/rover_initial_state_component.png` | 초기 pose, 속도 방향, 지면 높이 기준 |
| `images/renders/rover_visual_collision_shapes.png` | Visual Shape와 Collision Shape 분리 isometric 비교 |
| `images/renders/rover_suspension_steering_components.png` | 서스펜션 링크, spring-damper, steering rack 구성 |
| `images/renders/tracked_vehicle_components.png` | Track Shoe, Sprocket, Idler, Roller 확장 isometric 렌더 |
| `images/renders/terrain_ground_obstacle_components.png` | VSG Ground와 고정/원통 obstacle 배치 |
| `images/renders/terrain_rigid_patch_component.png` | RigidTerrain patch 범위, wheel path, obstacle 배치 |
| `images/renders/terrain_contact_material_regions.png` | 서로 다른 contact material patch와 wheel path |
| `images/renders/terrain_heightmap_component.png` | VSG Heightmap terrain 구조 |
| `images/renders/terrain_scm_deformation_component.png` | VSG SCMTerrain 침하/변형 구조 |
| `images/renders/terrain_environment_field_component.png` | slope, gravity, wind/외력, 진행 방향 조건 |
| `images/renders/collision_contact_components.png` | VSG 이동 body, 장애물, 접촉력 벡터 |
| `images/renders/collision_visual_vs_collision_shape.png` | VSG visual shape와 collision primitive 차이 |
| `images/renders/collision_contact_debug_vectors.png` | VSG 접촉점, 법선, 접촉력 벡터 debug 구조 |
| `images/renders/data_visualization_sensor_components.png` | VSG Camera, LiDAR, GPS/IMU 배치 |

## 그래프

| 파일 | 연결 CSV |
|---|---|
| `images/graphs/rover_vehicle_chassis_probe_graph.png` | `outputs/csv/rover_vehicle_chassis_probe.csv` |
| `images/graphs/terrain_height_sinkage_profile.png` | `outputs/csv/environment_terrain_height_friction_sinkage.csv` |
| `images/graphs/terrain_contact_material_friction_map.png` | `outputs/csv/environment_terrain_height_friction_sinkage.csv` |
| `images/graphs/terrain_contact_force_probe.png` | `outputs/csv/environment_terrain_contact_probe.csv` |
| `images/graphs/collision_contact_force_graph.png` | `outputs/csv/collision_contact_probe.csv` |
| `images/graphs/collision_contact_count_graph.png` | `outputs/csv/collision_contact_probe.csv` |
| `images/graphs/collision_contact_force_components_graph.png` | `outputs/csv/collision_contact_probe.csv` |
| `images/graphs/collision_contact_material_effect_graph.png` | deterministic contact material comparison |
| `images/graphs/collision_event_timeline_graph.png` | `outputs/csv/collision_event_timeline.csv` |
| `images/graphs/data_visualization_state_trajectory.png` | `outputs/csv/data_visualization_state_log.csv` |
| `images/graphs/data_visualization_control_inputs.png` | `outputs/csv/data_visualization_control_log.csv` |

## CSV

| 파일 | 내용 |
|---|---|
| `outputs/csv/rover_vehicle_chassis_probe.csv` | Chassis 위치/속도 probe |
| `outputs/csv/environment_terrain_height_friction_sinkage.csv` | heightmap, 마찰, SCM 침하 예시 |
| `outputs/csv/environment_terrain_contact_probe.csv` | ground 접촉력 probe |
| `outputs/csv/collision_contact_probe.csv` | 충돌 접촉력, 접촉 개수, 접촉력 성분 |
| `outputs/csv/collision_event_timeline.csv` | first contact 이벤트 |
| `outputs/csv/data_visualization_state_log.csv` | state logger 예시 |
| `outputs/csv/data_visualization_control_log.csv` | control logger 예시 |

## 실행 결과와 환경 기록

- `pychrono`가 활성화된 Chrono 환경에서는 PyChrono/VSG 기반 산출물을 생성한다.
- `pychrono`가 없는 환경에서는 deterministic probe로 CSV/그래프를 생성해 본문 설명과 schema를 유지한다.
- 수동으로 찍은 최종 VSG/Irrlicht 캡처는 `images/renders/manual_chrono/`에 넣는 방식으로 분리했다.
- `pychrono.sensor`가 없는 환경을 고려해 Sensor Component는 선택적 확장 설계로만 설명했다.

## 참고 문헌

- Project Chrono 공식 저장소: https://github.com/projectchrono/chrono
- Project Chrono API 문서: https://api.projectchrono.org/
- Chrono Vehicle Terrain system: https://api.projectchrono.org/group__vehicle__terrain.html
- SCMTerrain class reference: https://api.projectchrono.org/classchrono_1_1vehicle_1_1_s_c_m_terrain.html
- Chrono Sensor overview: https://api.projectchrono.org/sensor_overview.html
- Chrono Visualization overview: https://api.projectchrono.org/vehicle_visualization.html
- 로컬 참고: `README.md`, `docs/core/`, `docs/vehicle/`, `docs/robot/`, `docs/visualization/`, `docs/postprocess/`, `lessons/phase4/hojin/`
