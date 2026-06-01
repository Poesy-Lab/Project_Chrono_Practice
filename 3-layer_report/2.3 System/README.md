# 2.3 System

통합 보고서의 System 파트(`2.3 system` 및 커스텀 로버 시스템 구현 내용)를 소주제별 Markdown 파일로 분리한 폴더이다. 각 문서는 Component를 조합하여 하나의 시뮬레이션 System을 구성한 사례를 설명하며, 관련 이미지는 `images/` 폴더에 표준 Markdown 링크로 연결한다.

## 파일 목록

- [2.3.1 충돌 시스템 구현](2.3.1_collision_system.md)
- [2.3.2 Curiosity Rover 화성 지형 주행 시스템 구현](2.3.2_curiosity_rover_mars_terrain_system.md)
- [2.3.3 커스텀 로버 시스템 설계 목적](2.3.3_custom_rover_system_purpose.md)
- [2.3.4 커스텀 로버 시스템 설계](2.3.4_custom_rover_system_design.md)
- [2.3.5 커스텀 환경 시스템 설계](2.3.5_custom_environment_system_design.md)
- [2.3.6 커스텀 로버 주행 실험](2.3.6_custom_rover_driving_experiments.md)

## 읽는 순서

| 순서 | 문서 | 핵심 내용 |
| --- | --- | --- |
| 1 | `2.3.1_collision_system.md` | RigidTerrain, Curiosity Rover, 고정 벽을 조합한 충돌 해석 System |
| 2 | `2.3.2_curiosity_rover_mars_terrain_system.md` | SCMTerrain, Heightmap, 화성 중력, Curiosity Rover를 조합한 지형 주행 System |
| 3 | `2.3.3_custom_rover_system_purpose.md` | 커스텀 로버 System 구현의 목적과 미니 프로젝트 성격 |
| 4 | `2.3.4_custom_rover_system_design.md` | 차체, 바퀴, 조향부, 구동부, 시각화 구조물을 조합한 로버 System 설계 |
| 5 | `2.3.5_custom_environment_system_design.md` | 평지, 경사면, 단차, 암석 장애물을 조합한 환경 System 설계 |
| 6 | `2.3.6_custom_rover_driving_experiments.md` | 직진, 조향, Slalom, Pivot Turn, Waypoint Tracking, PPO 실험 결과 |

## System 조합 레시피 요약

System 단계는 Component를 단순히 나열하는 절이 아니라, 구현하려는 주제를 어떤 Command와 Component 순서로 조립하는지 보여주는 단계이다. 본 보고서의 System 예시는 모두 로버/차량 기준 좌표계인 X-forward, Y-left, Z-up을 기본으로 해석한다.

| 구현 주제 | Command 조합 | Component 조합 | System 결과 |
|---|---|---|---|
| Curiosity 충돌 해석 | `veh.RigidTerrain` + `robot.Curiosity` + `ChBodyEasyBox` + `GetContactForce` | RigidTerrain, Rover, Fixed Wall, Contact Logger | 벽 충돌 시 접촉력과 충격량을 계산하는 충돌 해석 System |
| Curiosity 화성 지형 주행 | `veh.SCMTerrain` + heightmap 입력 + `SetGravitationalAcceleration` + `robot.CuriositySpeedDriver` | SCMTerrain, Heightmap, Mars Gravity, Rover, Driver, State Logger | 비정형 화성 지형에서 차체 높이, pitch, roll을 분석하는 주행 System |
| 커스텀 로버 설계 | `ChBodyEasyBox/Cylinder` + `ChLinkMotorRotationSpeed` + `ChLinkMotorRotationAngle` | Chassis, Wheel, Steering Knuckle, Drive Motor, Steering Motor, Sensor Mount | Core API만으로 구조와 구동 방식을 직접 설계한 로버 System |
| 커스텀 장애물 환경 | fixed ground/obstacle body + contact material + slope/step/rock 배치 | Ground, Slope, Step, Rock, Contact Material | 평지, 경사, 단차, 암석 장애물을 포함한 주행 시험장 System |
| 주행 실험/제어 비교 | motor command profile + waypoint controller + PPO driver + CSV logger | Driver/Input, Control Logger, State Logger, Graph Generator | 직진, 조향, slalom, pivot, waypoint, RL 실험을 비교하는 검증 System |

## 이미지

System 문서에서 사용하는 이미지는 `images/` 폴더에 모았다. 기존 Obsidian `attachments/` 임베드와 분산된 로컬 이미지는 표준 Markdown 이미지 링크로 정리하였다.

- 시스템 이미지 01: [images/system_figure_01.png](images/system_figure_01.png) (1,223,359 bytes)
- 시스템 이미지 02: [images/system_figure_02.png](images/system_figure_02.png) (55,332 bytes)
- 시스템 이미지 03: [images/system_figure_03.png](images/system_figure_03.png)
- 시스템 이미지 04: [images/system_figure_04.jpg](images/system_figure_04.jpg)
- 시스템 이미지 05: [images/system_figure_05.png](images/system_figure_05.png) (40,866 bytes)
- 시스템 이미지 06: [images/system_figure_06.png](images/system_figure_06.png)
- 시스템 이미지 07: [images/system_figure_07.png](images/system_figure_07.png) (331,333 bytes)
- 시스템 이미지 08: [images/system_figure_08.png](images/system_figure_08.png) (62,334 bytes)
- 시스템 이미지 09: [images/system_figure_09.png](images/system_figure_09.png) (925,909 bytes)
- 시스템 이미지 10: [images/system_figure_10.png](images/system_figure_10.png) (80,150 bytes)
- 시스템 이미지 11: [images/system_figure_11.png](images/system_figure_11.png) (231,836 bytes)
- 시스템 이미지 12: [images/system_figure_12.png](images/system_figure_12.png) (183,709 bytes)
- 시스템 이미지 13: [images/system_figure_13.png](images/system_figure_13.png) (102,365 bytes)
- 시스템 이미지 14: [images/system_figure_14.png](images/system_figure_14.png) (244,806 bytes)
- 시스템 이미지 15: [images/system_figure_15.png](images/system_figure_15.png) (191,851 bytes)
- 시스템 이미지 16: [images/system_figure_16.png](images/system_figure_16.png) (99,392 bytes)
- 시스템 이미지 17: [images/system_figure_17.png](images/system_figure_17.png) (284,672 bytes)
- 시스템 이미지 18: [images/system_figure_18.png](images/system_figure_18.png) (148,107 bytes)
- 시스템 이미지 19: [images/system_figure_19.png](images/system_figure_19.png) (100,033 bytes)
- 시스템 이미지 20: [images/system_figure_20.png](images/system_figure_20.png) (240,453 bytes)
- 시스템 이미지 21: [images/system_figure_21.png](images/system_figure_21.png) (188,571 bytes)
- 시스템 이미지 22: [images/system_figure_22.png](images/system_figure_22.png) (141,442 bytes)
- 시스템 이미지 23: [images/system_figure_23.png](images/system_figure_23.png) (211,520 bytes)
- 시스템 이미지 24: [images/system_figure_24.png](images/system_figure_24.png) (104,061 bytes)
- 시스템 이미지 25: [images/system_figure_25.png](images/system_figure_25.png) (169,764 bytes)
- Heightmap 이미지: [images/scm_pockmarked_mars_heightmap.png](images/scm_pockmarked_mars_heightmap.png)
