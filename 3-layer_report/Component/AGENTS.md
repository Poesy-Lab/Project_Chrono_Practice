# AGENTS.md - 2.2 Component 보고서 작성 작업 지침

## 작업 목표

Project Chrono 캡스톤 보고서의 **"2.2 Component: 구현 대상별 부품 설계"** 파트를 작성하고, 관련 코드, 렌더링 이미지, 그래프, CSV 결과를 하나의 폴더 구조로 정리한다.

이 작업은 Command-Component-System 3계층 중 **Component 단계**만 담당한다. 교수님께서 원하시는 방향은 Project Chrono를 Command-Component-System 계층으로 이해할 수 있는 상세 매뉴얼에 가깝다. 따라서 단순 요약이 아니라, Project Chrono를 처음 배우는 팀원이 보고 따라갈 수 있는 설명, 표, 코드 예시, 렌더링 이미지, 그래프를 함께 제공한다.

## 작업 위치

모든 산출물은 반드시 아래 경로 내부에 정리한다.

```text
/Users/poesy/Documents/Praxis/Project_Chrono_Practice/3-layer_report/Component
```

Ubuntu 환경에서 작업할 경우에도 저장소 루트 기준으로 같은 상대 경로를 사용한다.

```text
3-layer_report/Component
```

기존 프로젝트 파일은 가능하면 수정하지 않는다. 로컬 프로젝트의 기존 코드를 참고하거나 이용해도 되지만, 이용한 경우 해당 코드는 반드시 `3-layer_report/Component/code/` 내부에 따로 복사하거나 Component 설명에 맞게 재구성해서 관리한다.

## 권장 폴더 구조

아래 구조를 기준으로 필요한 하위 폴더를 생성한다.

```text
3-layer_report/Component/
├── AGENTS.md
├── README.md
├── markdown/
│   ├── 2.2.1_component_definition.md
│   ├── 2.2.2_rover_vehicle_components.md
│   ├── 2.2.3_environment_terrain_components.md
│   ├── 2.2.4_collision_contact_components.md
│   └── 2.2.5_data_visualization_components.md
├── code/
│   ├── common/
│   ├── rover_vehicle/
│   ├── environment_terrain/
│   ├── collision_contact/
│   └── data_visualization/
├── images/
│   ├── renders/
│   ├── graphs/
│   └── diagrams/
└── outputs/
    ├── csv/
    └── raw/
```

## 작성 파일 관리 방식

- Markdown은 하나의 긴 파일로만 만들지 말고, 목차별로 분리해서 작성한다.
- 반드시 아래 파일들을 각각 작성한다.
  - `markdown/2.2.1_component_definition.md`
  - `markdown/2.2.2_rover_vehicle_components.md`
  - `markdown/2.2.3_environment_terrain_components.md`
  - `markdown/2.2.4_collision_contact_components.md`
  - `markdown/2.2.5_data_visualization_components.md`
- `README.md`에는 각 파일의 역할, 읽는 순서, 생성된 코드/이미지/그래프/CSV 목록을 정리한다.
- 나중에 팀 보고서에 합치기 쉽도록 각 파일의 제목과 번호를 정확히 유지한다.

## 환경 규칙

Project Chrono 실행은 프로젝트 루트의 `AGENTS.md` 규칙을 따른다.

- conda 환경 `chrono` 사용
- `python3` 금지, conda 환경의 `python` 사용
- macOS/Linux:

```bash
conda activate chrono
source setup_chrono_env.sh
python path/to/script.py
```

Ubuntu + NVIDIA CUDA 환경에서 작업할 경우:

- Core, Vehicle, Terrain, Irrlicht/VSG 렌더링은 우선 실제 실행을 시도한다.
- Sensor, DEM, FSI, GranularTerrain 등 CUDA 의존 모듈은 환경에 빌드되어 있을 때만 실제 실행한다.
- 실행 불가 시 공식 문서 기반 설명과 대체 도식/placeholder 이미지를 만들고, `README.md`에 실패 이유와 필요한 환경을 기록한다.

## 조사 요구

로컬 프로젝트와 공식 문서를 모두 조사한다.

### 로컬 조사 대상

- `README.md`
- `AGENTS.md`
- `docs/`
- `lessons/`
- 특히 다음 경로:
  - `docs/core/`
  - `docs/vehicle/`
  - `docs/robot/`
  - `docs/visualization/`
  - `docs/postprocess/`
  - `lessons/phase4/hojin/`

### 공식/인터넷 조사 대상

Project Chrono 공식 문서와 인터넷 자료를 조사해서 최신/정확한 내용을 반영한다.

확인할 공식 문서 범주:

- Chrono Core
- Chrono::Vehicle
- Vehicle Terrain
- Robot models
- Visualization
- Postprocess
- Sensor
- DEM/FSI/GranularTerrain 등 고급 모듈은 확장 Component 설명에 필요한 만큼만 확인

공식 문서 링크는 각 Markdown 파일 또는 `README.md` 참고문헌에 포함한다.

## 작성 관점

Component는 Project Chrono 공식 모듈 이름을 그대로 나열하는 것이 아니다. 본 보고서에서 Component는 **실제 시뮬레이션 대상을 구성하는 물리적/기능적 부품 단위**를 뜻한다.

예:

| 공식 모듈/Command 범주 | 본 보고서에서 Component로 해석할 대상 |
|---|---|
| Core `ChBody` | Chassis, Wheel, Obstacle, Ground |
| Core `ChLink` | Steering joint, Suspension link, Wheel axle |
| Core `ChMotor` | Drive motor, Steering motor |
| Vehicle | Tire, Suspension, Steering, Driveline, Powertrain, Terrain |
| Terrain | Ground, RigidTerrain, SCMTerrain, Heightmap terrain |
| Collision | Collision Shape, Contact Material, Contact Reporter |
| Postprocess/Python I/O | State Logger, CSV Schema, Graph Generator |
| Visualization/Sensor | Render/Screenshot, Camera, LiDAR, GPS, IMU |

특정 MVP0 예제에만 초점을 맞추지 말고, 일반적인 Component 설계 매뉴얼처럼 작성한다. 기존 MVP0 코드는 참고 예시로 사용할 수 있으나 중심 주제로 삼지 않는다.

## 반드시 포함할 목차와 내용

### 2.2.1 Component 단계의 정의와 역할

작성 파일:

```text
markdown/2.2.1_component_definition.md
```

포함 내용:

- Command, Component, System의 관계 설명
- Chrono 공식 module/component와 본 보고서에서 말하는 구현 Component의 차이 설명
- Component를 "여러 Chrono Command를 조합해 만든 재사용 가능한 시뮬레이션 부품"으로 정의
- Component 분류 체계 제시:
  - 로버/차량 Component
  - 환경/Terrain Component
  - 충돌/접촉 측정 Component
  - 데이터 출력/시각화 Component
  - 선택적 확장 Component
- 관계와 계층을 설명하는 Mermaid 다이어그램 적극 사용

### 2.2.2 로버/차량 Component 설계

작성 파일:

```text
markdown/2.2.2_rover_vehicle_components.md
```

다음 Component를 각각 설명한다.

- Chassis Component
- Wheel/Tire Component
- Motor/Drive Component
- Steering Component
- Suspension Component
- Visual Shape Component
- Collision Shape Component
- Vehicle 확장 Component: Driveline, Brake, Powertrain
- Tracked Vehicle 확장 Component: Track Shoe, Sprocket, Idler, Roller

각 Component마다 가능한 한 다음을 모두 포함한다.

- 역할
- 관련 Chrono Command/API
- 사용되는 상황
- 독립적으로 이해 가능한 Python 코드 예시
- 코드 실행 결과로 생성되는 그래픽 렌더링 이미지
- 가능하면 해당 Component와 관련된 그래프
- 주의사항
- 다른 Component와의 관계를 설명하는 Mermaid 다이어그램 또는 표

렌더링 이미지가 매우 중요하다. 각 Component가 무엇인지 시각적으로 이해할 수 있도록 가능하면 Component별 예제 코드를 실행해서 렌더링 이미지를 생성한다. 렌더링이 어려운 Component는 단순한 대체 장면을 만들어서라도 이미지를 제공한다.

### 2.2.3 환경/Terrain Component 설계

작성 파일:

```text
markdown/2.2.3_environment_terrain_components.md
```

다음 Component를 각각 설명한다.

- Ground Component
- Obstacle Component
- RigidTerrain Component
- SCMTerrain Component
- Contact Material Component
- 확장 지형 Component: FlatTerrain, CRGTerrain, GranularTerrain, FEATerrain, CRMTerrain

각 Component마다 가능한 한 다음을 모두 포함한다.

- 역할
- 관련 Chrono Command/API
- 사용되는 상황
- Python 코드 예시
- 코드 실행 결과 렌더링 이미지
- 가능하면 높이/마찰/변형/접촉력 등의 그래프
- 주의사항

RigidTerrain과 SCMTerrain은 Project Chrono Vehicle 모듈의 Terrain 계열이라는 점을 명확히 설명한다.

### 2.2.4 충돌/접촉 측정 Component 설계

작성 파일:

```text
markdown/2.2.4_collision_contact_components.md
```

다음 Component를 설명한다.

- Collision Shape Component
- Contact Reporter Component
- Contact Force Logger Component
- Collision Event Detector Component

내용 요구:

- Visual Shape와 Collision Shape의 차이 설명
- Contact Material과 Contact Reporter의 역할 차이 설명
- 접촉력, 접촉 개수, 충돌 시각을 어떻게 기록하는지 코드 예시 포함
- 코드 실행 결과 렌더링 이미지 포함
- 접촉력 그래프, 접촉 개수 그래프, 충돌 이벤트 타임라인 그래프 등 포함
- 이미지와 그래프는 Markdown 표 안에 보기 좋게 정리

### 2.2.5 데이터 출력/시각화 Component 설계

작성 파일:

```text
markdown/2.2.5_data_visualization_components.md
```

다음 Component를 설명한다.

- State Logger Component
- Control Logger Component
- CSV Schema
- Graph Generator
- Render/Screenshot Component
- 선택적 Sensor Component: Camera, LiDAR, GPS, IMU

내용 요구:

- 위치, 속도, 자세, 접촉력, 제어 입력을 어떤 컬럼으로 저장할지 표로 정리
- CSV 예시 코드 포함
- matplotlib 그래프 생성 예시 코드 포함
- 렌더링 이미지 저장 방식 설명
- 그래프 이미지 저장 방식 설명
- 코드 실행 결과물인 CSV, 렌더링 이미지, 그래프 이미지가 서로 어떻게 연결되는지 설명
- 이미지 여러 개는 Markdown 표 안에 삽입
- Sensor Component는 현재 필수 구현 대상이 아니라 선택적 확장 Component로 설명

## 코드/이미지/그래프 생성 요구

- 가능하면 실제 PyChrono 코드를 작성하고 실행해서 렌더링 이미지와 그래프를 생성한다.
- 그래픽 창이 필요한 경우 VSG/Irrlicht 자동 분기 패턴을 사용한다.
- Ubuntu + RTX CUDA 환경에서는 VSG 또는 Irrlicht 중 사용 가능한 렌더러를 우선 사용한다.
- 실제 3D 렌더링 캡처가 환경 문제로 불가능하면, 그 이유를 명확히 기록하고 matplotlib 3D/2D 대체 렌더링 이미지를 생성한다.
- 그래프는 matplotlib non-interactive backend 사용:

```python
import matplotlib
matplotlib.use("Agg")
```

- 생성된 코드는 `code/` 내부에 저장한다.
- 생성된 CSV는 `outputs/csv/` 내부에 저장한다.
- 생성된 렌더링 이미지는 `images/renders/` 내부에 저장한다.
- 생성된 그래프 이미지는 `images/graphs/` 내부에 저장한다.
- Mermaid 또는 구조 다이어그램은 Markdown 내 Mermaid 코드로 관리하거나 `images/diagrams/`에 저장한다.

## Markdown 스타일 요구

- 한국어로 작성
- 교수님께 제출할 보고서 일부이므로 설명은 충분히 자세하고 매뉴얼처럼 구체적으로 작성
- 표를 적극 사용
- Mermaid는 관계, 계층, 흐름을 설명할 때 적극 사용
- 코드 예시는 너무 긴 전체 프로그램보다 Component별 핵심 코드 위주
- 이미지와 그래프에는 캡션을 붙인다
- 여러 이미지를 나열할 때는 Markdown 표 안에 이미지 삽입
- 온톨로지/AI 파이프라인 설명은 길게 하지 않는다
- 종민/도희 System 파트와 자연스럽게 이어지도록 작성하는 것은 고려하지 않아도 된다
- 최종 결론이나 향후 계획은 길게 쓰지 말고, 이 절의 범위인 Component 설계에 집중한다

## 검증

작업 완료 후 다음을 확인한다.

- 폴더 구조 출력
- Markdown 코드 fence 개수 확인
- Mermaid 문법 육안 점검
- 이미지 링크 경로 확인
- 생성한 코드가 실행 가능한지 가능한 범위에서 테스트
- 실행 실패 코드는 실패 이유와 필요한 환경을 `README.md`에 기록
- 최종 응답에는 생성한 주요 파일 목록, 실행/검증 결과, 렌더링 이미지/그래프 생성 여부를 요약

