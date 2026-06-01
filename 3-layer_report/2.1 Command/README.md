# 2.1 Command

Project Chrono 기능을 Command 관점에서 분류한 자료이다. 이 폴더는 시스템 생성, 강체, 충돌, 힘, 조인트, 모터, 수학/좌표계, solver처럼 여러 Component와 System 구현에서 반복적으로 사용되는 Core API를 중심으로 정리한다.

## 좌표계 기준

Chrono Core 예제는 목적에 따라 Y-up 또는 Z-up으로 구성할 수 있지만, 본 보고서의 Vehicle/Robot/커스텀 로버 System은 ISO 차량 좌표계인 X-forward, Y-left, Z-up을 기준으로 설명한다. 따라서 로버/지형 System과 연결되는 예제는 중력을 -Z 방향으로 두고, 별도 Y-up 예제를 사용할 때는 그 차이를 명시한다.

## 파일 목록

| 구분 | 파일 | 핵심 내용 |
| --- | --- | --- |
| Overview | [2.1.0 Command 단계 전체 구조](2.1.0_command_stage_overview.md) | Command 분류, Component/System 연결, 전체 학습 로드맵 |
| Core | [2.1.1 System](2.1.1_system.md) | 시뮬레이션 시스템, 중력, 시간 적분, body/link 등록 |
| Core | [2.1.2 Collision](2.1.2_collision.md) | 충돌 시스템, 접촉 재질, 충돌 형상, NSC/SMC |
| Core | [2.1.3 Force & Spring](2.1.3_force_spring.md) | 외력, 토크, 스프링/댐퍼, 시간 의존 하중 |
| Core | [2.1.4 Joint & Links](2.1.4_joint_and_links.md) | 제약 조건, 링크, 힌지/슬라이더/거리 조인트 |
| Core | [2.1.5 Math](2.1.5_math.md) | 벡터, 좌표계, 쿼터니언, 프레임 변환 |
| Core | [2.1.6 Motors](2.1.6_motors.md) | 회전/병진 모터, 속도/위치/토크 제어 |
| Core | [2.1.7 Rigid Bodies](2.1.7_rigid_bodies.md) | 강체 생성, 질량/관성, 위치/속도, 시각화 형상 |
| Core | [2.1.8 Solver](2.1.8_solver.md) | Solver 종류, 반복 횟수, 수렴 조건, timestep 영향 |
| Applied | [2.1.9 Terrain, Vehicle, Robot, Visualization, Data](2.1.9_terrain_vehicle_robot_visualization_data.md) | 지형, 차량, 로봇, 렌더링, CSV/그래프 출력 Command |

## 읽는 순서

1. `2.1.0`에서 Command 단계가 Component/System으로 이어지는 전체 분류를 먼저 확인한다.
2. `System`과 `Rigid Bodies`에서 Chrono 시뮬레이션의 기본 구성 단위를 확인한다.
3. `Collision`, `Force & Spring`, `Joint & Links`, `Motors`를 통해 물체 사이 상호작용과 구동 방식을 연결한다.
4. `Solver`와 `Math`를 함께 보며 timestep, 좌표계, 수치 안정성 문제를 점검한다.
5. `Terrain, Vehicle, Robot, Visualization, Data`에서 로버/환경 System에 필요한 고수준 Command 또는 Factory API를 확인한다.

## 이미지 관리

본문에 사용되는 이미지는 `images/` 폴더에 모아두었다. Markdown 파일에는 `data:image` 인라인 이미지 대신 `images/...png` 형태의 상대 경로만 남겨, GitHub와 로컬 Markdown 뷰어에서 모두 같은 방식으로 확인할 수 있다. Vehicle/Robot 모델 설명과 관련 이미지는 `2.2 Component`의 로버/차량 Component 문서로 통합했다.
