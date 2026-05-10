---
title: "지형 (Terrain)"
author: ""
last_modified: "2026-03-31"
tags:
  - chrono
  - vehicle
---

# Terrain란?
차량이 주행하는 지면 시스템으로, 단순한 바닥 박스가 아니라, 차량의 타이어나 트랙과 상호작용하는 물리적 환경이다.

 Chrono에서 terrain의 상위 기준점은 `ChTerrain`으로, 모든 terrain 클래스가 공통적으로 가져야 하는 기능을 정의한다.  
  
대표 기능은 다음과 같다.
- `Synchronize(time)` : 현재 시간 기준으로 terrain 상태 갱신  
- `Advance(step)` : 지정된 시간 간격만큼 terrain 진행  
- `GetHeight(loc)` : 특정 위치 아래의 terrain 높이 반환  
- `GetPoint(loc)` : 특정 위치 아래의 terrain 위 점 반환  
- `GetNormal(loc)` : 특정 위치의 terrain 법선벡터 반환  
- `GetCoefficientFriction(loc)` : 특정 위치의 마찰계수 반환  
- `GetProperties(loc, point, height, normal, friction)` : 위 정보를 한 번에 반환  
  
> [!important] 중요한 포인트  
> Chrono의 Terrain은 단순히 시각적으로 보이는 바닥이 아니라, 차량의 타이어/트랙과 접촉하고, 마찰을 만들고, 경우에 따라 변형까지 되는 물리 모델이다.  
>  
> 즉 Terrain은 차량 시뮬레이션에서 `차량이 어디를 밟고 있는지`, `얼마나 미끄러운지`, `얼마나 가라앉는지`, `어떤 법선 방향으로 힘을 받는지`를 결정하는 핵심 요소이다.  
  
# Terrain의 종류 
공식 API 문서 기준으로 Terrain system에는 다음과 같은 주요 클래스가 있다.  

| 클래스                    | 의미                          | 특징                           |
| ---------------------- | --------------------------- | ---------------------------- |
| `ChTerrain`            | terrain의 기본 부모 클래스          | 높이, 법선, 마찰계수 조회 인터페이스 제공     |
| `FlatTerrain`          | 평평한 수평 지면                   | 가장 단순한 terrain               |
| `RigidTerrain`         | 강체 지형                       | 박스, mesh, heightmap 기반 지형 가능 |
| `SCMTerrain`           | Soil Contact Model 기반 변형 지형 | 바퀴가 지나가면 지면이 변형됨             |
| `GranularTerrain`      | 입자 기반 지형                    | 모래, 자갈처럼 입자 지형 표현            |
| `CRMTerrain`           | SPH 기반 연속체 변형 지형            | 고급 deformable terrain        |
| `FEATerrain`           | FEA 기반 변형 지형                | 유한요소 기반 지반 모델                |
| `RandomSurfaceTerrain` | 거칠기 제어가 가능한 랜덤 지형           | 불규칙 노면 생성                    |
| `CRGTerrain`           | OpenCRG 파일 기반 도로            | 실제 도로 프로파일 사용 가능             |
| `ObsModTerrain`        | obstacle modifier terrain   | 장애물/수정 terrain 계열            |

## ChTerrain  
`ChTerrain`은 모든 terrain의 기본 클래스이다.  실제로 차량 시뮬레이션을 만들 때 `ChTerrain`을 직접 쓰기보다는, `RigidTerrain`, `SCMTerrain`, `FlatTerrain` 같은 구체 클래스를 사용한다.  
### `GetHeight(loc)`  
지정한 위치 `loc` 아래에 있는 terrain의 높이를 반환한다.  예를 들어 차량 바퀴 위치가 `(x, y, z)`일 때, 그 아래 지면 높이를 알고 싶으면 이 함수를 사용한다.  
```python
height = terrain.GetHeight(chrono.ChVector3d(x, y, z))
```

### `GetPoint(loc)`
지정한 위치 아래의 실제 terrain 위 점을 반환한다. 즉 입력 위치의 수평 좌표를 기준으로, terrain 표면에 있는 점을 구한다.
```python
point = terrain.GetPoint(chrono.ChVector3d(x, y, z))
```

### `GetNormal(loc)`
terrain 표면의 법선벡터를 반환한다. 평평한 바닥이면 보통 위쪽 방향 벡터가 나오지만, 경사면이나 울퉁불퉁한 terrain에서는 위치마다 법선 방향이 달라진다.
```python
normal = terrain.GetNormal(chrono.ChVector3d(x, y, z))
```

### `GetCoefficientFriction(loc)`
해당 위치의 마찰계수를 반환한다. 이 값은 일부 타이어 모델에서 타이어 특성을 바꾸는 데 사용될 수 있다.  
단, 모든 물체와의 접촉에 무조건 적용되는 전역 마찰값은 아니다.
```python
mu = terrain.GetCoefficientFriction(chrono.ChVector3d(x, y, z))
```
>[!important] 마찰계수 주의  
`GetCoefficientFriction()`으로 얻는 마찰계수는 terrain이 제공하는 지면 특성값이다.
하지만 실제 접촉 계산에서 어떤 식으로 쓰이는지는 사용하는 타이어 모델과 contact material 설정에 따라 달라진다.

## FlatTerrain  
`FlatTerrain`은 가장 단순한 terrain이다. 이름 그대로 평평한 수평 지면을 만든다.
### 사용 상황
- 차량 모델 테스트
- suspension 기본 동작 확인
- 타이어 모델 디버깅
- terrain 자체가 중요하지 않은 경우
- 빠르게 차량이 제대로 굴러가는지 확인할 때
### 특징
- 구조가 단순하다.
- 계산 비용이 낮다.
- 지형 변화가 없다.
- 장애물, heightmap, 지반 변형을 표현하지 못한다.

> [!tip] 사용 기준  
> 처음 차량 모델을 만들 때는 복잡한 terrain부터 쓰지 말고 `FlatTerrain` 또는 단순 `RigidTerrain`으로 시작하는 것이 좋다.
> 차량이 평지에서 제대로 움직이지 않으면, 복잡한 지형에서는 원인 분석이 더 어려워진다.

## RigidTerrain  
`RigidTerrain`은 강체 지형 모델이다. 공식 문서 기준으로 `RigidTerrain`은 접촉 flag가 활성화된 다른 body들과 접촉 및 마찰 상호작용을 할 수 있는 rigid shape 기반 terrain이다.
차량이 지나가도 terrain은 눌리지 않고, 바퀴나 트랙만 terrain 위에서 접촉한다.
### 사용 상황
- 포장도로
- 단단한 바닥
- 콘크리트 도로
- 아스팔트 도로
- 변형되지 않는 장애물 지형
- mesh 기반 시험장
- heightmap 기반 산악/험지 형상
### Patch 개념
Patch는 terrain을 이루는 한 조각으로 `RigidTerrain`은 하나 이상의 `Patch`로 구성된다.  또한 하나의 terrain 안에 여러 patch를 추가할 수 있다.

예시로 아래와 같이 만들 수 있다.
- 첫 번째 patch : 평평한 도로
- 두 번째 patch : 경사로
- 세 번째 patch : mesh 장애물
- 네 번째 patch : heightmap 지형

### PatchType
`RigidTerrain`의 patch 종류는 크게 다음과 같다.

| PatchType    | 의미                                 |
| ------------ | ---------------------------------- |
| `BOX`        | 박스 형태의 직사각형 terrain                |
| `MESH`       | Wavefront OBJ mesh 기반 terrain      |
| `HEIGHT_MAP` | grayscale heightmap 이미지 기반 terrain |
### 주요 함수
#### `AddPatch(material, position, length, width, thickness)`
가장 기본적인 terrain 생성 방식으로, 박스 형태의 rigid terrain patch를 추가한다.
```python
terrain = veh.RigidTerrain(system)  
  
patch = terrain.AddPatch(ground_mat,  
chrono.ChCoordsysd(chrono.ChVector3d(0, 0, 0),  
chrono.QUNIT), 100.0, 100.0, 0.1)  
  
terrain.Initialize()
```

| 인자          | 의미            |
| ----------- | ------------- |
| `material`  | 접촉 재질         |
| `position`  | patch의 위치와 회전 |
| `length`    | patch 길이      |
| `width`     | patch 폭       |
| `thickness` | patch 두께      |

#### `AddPatch(..., mesh_file, ...)`
OBJ mesh 파일을 terrain으로 사용한다. 복잡한 지형, 장애물, 시험장 형상을 만들 때 사용한다.
```python
patch = terrain.AddPatch(ground_mat,  
chrono.ChCoordsysd(chrono.ChVector3d(0, 0, 0),  
chrono.QUNIT), "terrain.obj", True, 0.0, True)
```

#### `AddPatch(..., heightmap_file, length, width, hMin, hMax, ...)`
heightmap 이미지를 terrain으로 사용한다. 흑백 이미지의 밝기를 높이값으로 변환하여 지형을 만든다.
```python
patch = terrain.AddPatch(ground_mat,  
chrono.ChCoordsysd(chrono.ChVector3d(0, 0, 0),  
chrono.QUNIT), "heightmap.bmp", 100.0, 100.0, -1.0, 2.0, True, 0.0, True)
```

| 인자               | 의미               |
| ---------------- | ---------------- |
| `heightmap_file` | BMP heightmap 파일 |
| `length`         | 실제 지형 길이         |
| `width`          | 실제 지형 폭          |
| `hmin`           | 검은색에 대응되는 최소 높이  |
| `hmax`           | 흰색에 대응되는 최대 높이   |

>[!important] heightmap 해석  
>heightmap은 이미지 밝기를 높이로 바꾸는 방식이다.
>검은색은 `hMin`, 흰색은 `hMax`에 가까운 높이로 해석된다.
>따라서 이미지가 너무 거칠거나 해상도가 너무 높으면 collision mesh가 복잡해져 계산이 느려질 수 있다.

아래는 가장 기본적인 `RigidTerrain` 예제이다.
```python
import os
import glob
import pychrono as chrono
import pychrono.vehicle as veh
import pychrono.irrlicht as irr

system = chrono.ChSystemNSC()
system.SetGravitationalAcceleration(chrono.ChVector3d(0, 0, -9.81))

system.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)

ground_mat = chrono.ChContactMaterialNSC()
ground_mat.SetFriction(0.8)
ground_mat.SetRestitution(0.01)

box_mat = chrono.ChContactMaterialNSC()
box_mat.SetFriction(0.5)
box_mat.SetRestitution(0.05)

terrain = veh.RigidTerrain(system)

patch = terrain.AddPatch(
    ground_mat,
    chrono.ChCoordsysd(
        chrono.ChVector3d(0, 0, 0),
        chrono.QUNIT), 100.0, 100.0, 0.1)

conda_prefix = os.environ.get("CONDA_PREFIX", "")
matches = glob.glob(
    os.path.join(conda_prefix, "**", "terrain", "textures", "tile4.jpg"),
    recursive=True)

if matches:
    patch.SetTexture(matches[0], 200, 200)
else:
    print("WARNING: terrain texture not found")

terrain.Initialize()

floor = chrono.ChBodyEasyBox(100.0, 100.0, 0.2, 1000, True, True, ground_mat)

floor.SetPos(chrono.ChVector3d(0, 0, -0.1))
floor.SetFixed(True)
floor.EnableCollision(True)
system.Add(floor)

box = chrono.ChBodyEasyBox(1.0, 1.0, 1.0, 1000, True, True, box_mat)

box.SetPos(chrono.ChVector3d(0, 0, 3.0))
box.SetMass(10.0)
box.EnableCollision(True)
system.Add(box)

vis = irr.ChVisualSystemIrrlicht()
vis.AttachSystem(system)
vis.SetWindowSize(1280, 720)
vis.SetWindowTitle("Chrono Vehicle Terrain Collision Test")
vis.Initialize()
vis.AddSkyBox()
vis.AddCamera(
    chrono.ChVector3d(6, -8, 5),
    chrono.ChVector3d(0, 0, 0))
vis.AddTypicalLights()

step_size = 0.01

while vis.Run():
    time = system.GetChTime()

    terrain.Synchronize(time)

    vis.BeginScene()
    vis.Render()
    vis.EndScene()

    system.DoStepDynamics(step_size)
    terrain.Advance(step_size)

    if int(time * 100) % 50 == 0:
        print(
            "time:",
            round(time, 2),
            "box z:",
            round(box.GetPos().z, 3),
            "terrain height:",
            terrain.GetHeight(chrono.ChVector3d(0, 0, 1)))
```

>[!important] 코드 흐름  
`RigidTerrain`은 보통 다음 순서로 만든다.
>1. `ChSystem` 생성
>2. contact material 생성
>3. `RigidTerrain(system)` 생성
>4. `AddPatch()`로 patch 추가
>5. texture 또는 visual 설정
>6. `terrain.Initialize()` 호출
>7. 시뮬레이션 루프에서 `Synchronize()`, `Advance()` 사용

## SCMTerrain
`SCMTerrain`은 Soil Contact Model 기반의 변형 terrain이다. `RigidTerrain`과 달리, 차량 바퀴나 collision shape가 지나가면 terrain mesh의 수직 좌표가 변형될 수 있다. 즉, 바퀴가 흙을 밟고 지나가면서 rut, sinkage, bulldozing 효과를 만들 수 있다.
### 사용 상황
- 흙길
- 모래 지반
- 진흙 지반
- 오프로드 차량 주행
- 바퀴 침하량 분석
- 지반 변형 분석
- rover mobility 해석

|            | `RigidTerrian` | `SCMTerrian`                 |
| ---------- | -------------- | ---------------------------- |
| 지면 변형      | 없음             | 있음                           |
| 계산 비용      | 낮음             | 높음                           |
| 사용 목적      | 단단한 도로, 단순 테스트 | 흙, 모래, 변형 지반                 |
| 차량 통과 후 자국 | 없음             | 가능                           |
| 주요 파라미터    | 마찰, 형상         | Bekker, Mohr-Coulomb, Janosi |
### 주요 함수
#### `SetSoilParameters(...)`
SCM 지반 물성을 설정한다.
```python
terrain.SetSoilParameters(
    Bekker_Kphi,
    Bekker_Kc,
    Bekker_n,
    Mohr_cohesion,
    Mohr_friction,
    Janosi_shear,
    elastic_K,
    damping_R
)
```

| 인자              | 의미                      |
| --------------- | ----------------------- |
| `Bekker_Kphi`   | Bekker 압력-침하 모델의 마찰성 계수 |
| `Bekker_Kc`     | Bekker 압력-침하 모델의 점착성 계수 |
| `Bekker_n`      | 침하 지수                   |
| `Mohr_cohesion` | Mohr-Coulomb 점착력        |
| `Mohr_friction` | 내부 마찰각                  |
| `Janosi_shear`  | Janosi 전단 변형 계수         |
| `elastic_K`     | 탄성 강성                   |
| `damping_R`     | 감쇠 계수                   |
>[!important] 중요한 포인트  
SCM terrain은 단순히 마찰계수 하나로 지면을 표현하지 않는다.
>지반이 얼마나 눌리는지, 얼마나 전단 저항을 가지는지, 얼마나 탄성적으로 복원되는지를 여러 soil parameter로 표현한다.

#### `Initialize(sizeX, sizeY, delta)`
평평한 SCM terrain을 초기화한다.
```python
terrain.Initialize(20.0, 20.0, 0.05)
```

| 인자      | 의미               |
| ------- | ---------------- |
| `sizeX` | terrain의 X 방향 크기 |
| `sizeY` | terrain의 Y 방향 크기 |
| `delta` | grid 간격          |
`delta`가 작을수록 terrain 해상도가 높아진다.  
하지만 계산량도 증가한다.
> [!warning] delta 설정  
> `delta`를 너무 작게 잡으면 지형은 정밀해지지만 계산 속도가 매우 느려진다.
> 처음에는 `0.05 ~ 0.1` 정도로 시작하고, 결과가 필요 이상으로 거칠 때만 줄이는 것이 좋다.

#### `Initialize(heightmap_file, sizeX, sizeY, hMin, hMax, delta)`
heightmap 기반 SCM terrain을 만든다.
```python
terrain.Initialize(
    "heightmap.bmp",
    20.0,
    20.0,
    -0.5,
    0.5,
    0.05)
```

#### `SetPlotType(plot_type, min_val, max_val)`
SCM terrain의 시각화 색상 기준을 설정한다.
대표 plot type은 다음과 같다.

| PlotType             | 의미            |
| -------------------- | ------------- |
| `PLOT_NONE`          | 별도 색상 표시 없음   |
| `PLOT_LEVEL`         | 현재 terrain 높이 |
| `PLOT_LEVEL_INITIAL` | 초기 terrain 높이 |
| `PLOT_SINKAGE`       | 침하량           |
| `PLOT_PRESSURE`      | 압력            |
| `PLOT_SHEAR`         | 전단            |
| `PLOT_IS_TOUCHED`    | 접촉 여부         |

#### `EnableBulldozing(True)`
바퀴가 지나가면서 흙이 옆으로 밀려나는 효과를 활성화한다.
```python
terrain.EnableBulldozing(True)
```


#### `SetBulldozingParameters(...)`
bulldozing 효과의 세부 파라미터를 설정한다.
```python
terrain.SetBulldozingParameters(
    55.0,
    1.0,
    3,
    10)
```

|인자|의미|
|---|---|
|`erosion_angle`|흙이 무너지는 각도|
|`flow_factor`|흙 흐름 정도|
|`erosion_iterations`|침식 반복 횟수|
|`erosion_propagations`|침식 전파 횟수|

#### `AddActiveDomain(body, center, dims)`
SCM 계산 영역을 특정 body 주변으로 제한한다. 전체 terrain을 매번 계산하지 않고, 차량 주변만 계산하게 만들어 성능을 개선할 수 있다.
```python
terrain.AddActiveDomain(
    chassis_body,
    chrono.ChVector3d(0, 0, 0),
    chrono.ChVector3d(5, 3, 1))
```

>[!tip] 성능 최적화  
SCM terrain은 계산량이 크다.
>차량이 실제로 지나가는 근처만 계산해도 충분한 경우가 많으므로, 큰 terrain에서는 active domain을 사용하는 것이 좋다.

아래는 `SCMTerrian`의 예제이다.
```python
import pychrono as chrono
import pychrono.vehicle as veh
import pychrono.irrlicht as irr

system = chrono.ChSystemSMC()
system.SetGravitationalAcceleration(
chrono.ChVector3d(0, 0, -9.81))

system.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)

terrain = veh.SCMTerrain(system)
terrain.SetSoilParameters(
2e6, # Bekker Kphi
0.0, # Bekker Kc
1.1, # Bekker n
0.0, # Mohr cohesion
30.0, # Mohr friction angle
0.01, # Janosi shear
4e7, # elastic stiffness
3e4 # damping
)

terrain.EnableBulldozing(True)
terrain.SetBulldozingParameters(55.0, 1.0, 3, 10)

terrain.SetPlotType(veh.SCMTerrain.PLOT_SINKAGE, 0.0, 0.2)

terrain.Initialize(20.0, 20.0, 0.05)

sphere_mat = chrono.ChContactMaterialSMC()
sphere_mat.SetFriction(0.8)
sphere_mat.SetRestitution(0.0)
sphere = chrono.ChBodyEasySphere(0.5, 2000, True, True, sphere_mat)

sphere.SetPos(chrono.ChVector3d(0, 0, 2.0))
sphere.SetMass(500.0)
sphere.EnableCollision(True)
system.Add(sphere)

vis = irr.ChVisualSystemIrrlicht()
vis.AttachSystem(system)
vis.SetWindowSize(1280, 720)
vis.SetWindowTitle("SCM Terrain Sinkage Test")
vis.Initialize()
vis.AddSkyBox()
vis.AddCamera(chrono.ChVector3d(3, -6, 3), chrono.ChVector3d(0, 0, 0))
vis.AddTypicalLights()

step_size = 0.01
while vis.Run():
time = system.GetChTime()
terrain.Synchronize(time)
vis.BeginScene()
vis.Render()
vis.EndScene()
system.DoStepDynamics(step_size)
terrain.Advance(step_size)

if int(time * 100) % 50 == 0:

print("time:",
round(time, 2),
"sphere z:",
round(sphere.GetPos().z, 3),
"terrain height:",
round(terrain.GetHeight(chrono.ChVector3d(0, 0, 1)), 4))
```

## GranularTerrain
`GranularTerrain`은 입자 기반 terrain이다. 모래, 자갈, regolith처럼 작은 입자가 모여 있는 지형을 표현할 때 사용한다.
### 특징
- terrain을 연속적인 표면이 아니라 입자들의 집합으로 표현한다.
- 바퀴가 지나가면 입자들이 밀리고 흩어진다.
- 현실적인 granular material 거동을 표현할 수 있다.
- 계산량이 크다.

### 사용 상황
- 모래밭 주행
- 달/화성 rover regolith 해석
- 자갈 지형
- 입자-바퀴 상호작용 연구

> [!warning] 사용 난이도  
> Granular terrain은 단순 차량 예제용으로는 무겁다.
> 처음 Vehicle module을 공부하는 단계에서는 `RigidTerrain` → `SCMTerrain` → `GranularTerrain` 순서로 넘어가는 것이 낫다.

## CRMTerrain
`CRMTerrain`은 Continuum Representation Model 기반 deformable terrain이다. 공식 문서에서는 SPH를 사용하는 deformable terrain model로 설명된다.

### 특징
- SPH 기반 연속체 terrain
- 지반을 입자처럼 다루지만, continuum 관점의 변형을 표현
- 고급 오프로드/지반 상호작용 해석에 사용
- 일반 예제보다 연구용 성격이 강함

## FEATerrain
`FEATerrain`은 FEA 기반 변형 terrain이다. FEA는 Finite Element Analysis, 즉 유한요소해석이다.
### 특징
- 지반을 유한요소 mesh로 표현
- 변형, 응력, 변위 해석에 적합
- 계산 비용이 높음
- 단순 차량 주행 예제보다는 지반 구조 해석에 가까움

## RandomSurfaceTerrain
`RandomSurfaceTerrain`은 거칠기를 제어할 수 있는 불규칙 지형이다.
### 사용 상황
- 랜덤 노면 생성
- suspension 반응 테스트
- 승차감 해석
- 일정 roughness를 가진 도로 생성
### 특징
- 완전히 평평하지 않은 terrain을 자동 생성할 수 있다.
- heightmap 파일 없이 불규칙 표면을 만들 수 있다.
- 노면 roughness 테스트에 유용하다.

## CRGTerrain
`CRGTerrain`은 OpenCRG 파일 기반 terrain이다. OpenCRG는 도로 표면 형상을 저장하는 형식이다.
### 사용 상황
- 실제 도로 프로파일 기반 시뮬레이션
- 도로 roughness 재현
- 차량 동역학 시험
- ADAS/자율주행 도로 환경 재현

# Terrain 선택 기준
| 목표                | 추천 Terrain                  |
| ----------------- | --------------------------- |
| 차량이 제대로 굴러가는지만 확인 | `FlatTerrain`               |
| 평평한 단단한 도로        | `RigidTerrain`              |
| mesh 장애물 위 주행     | `RigidTerrain` + mesh patch |
| heightmap 산악 지형   | `RigidTerrain` + heightmap  |
| 흙길에서 침하량 확인       | `SCMTerrain`                |
| 바퀴 자국/rut 확인      | `SCMTerrain`                |
| 모래 입자 거동 확인       | `GranularTerrain`           |
| 고급 SPH 지반 해석      | `CRMTerrain`                |
| 유한요소 기반 지반 변형     | `FEATerrain`                |
| 랜덤 노면 테스트         | `RandomSurfaceTerrain`      |
| 실제 도로 데이터 사용      | `CRGTerrain`                |



# Terrain 생성 기본 순서
Chrono Vehicle에서 terrain을 만들 때는 보통 다음 흐름을 따른다.

1. `ChSystemNSC()` 또는 `ChSystemSMC()` 생성
2. contact material 생성
3. terrain 객체 생성
4. terrain 형상 또는 soil parameter 설정
5. `Initialize()` 호출
6. 시뮬레이션 루프에서 `Synchronize()`
7. `DoStepDynamics()`
8. `Advance()`

## 기본 흐름 예시
```python
import pychrono as chrono
import pychrono.vehicle as veh

system = chrono.ChSystemNSC()
system.SetGravitationalAcceleration(chrono.ChVector3d(0, 0, -9.81))

ground_mat = chrono.ChContactMaterialNSC()
ground_mat.SetFriction(0.8)

terrain = veh.RigidTerrain(system)

patch = terrain.AddPatch(
    ground_mat,
    chrono.ChCoordsysd(
        chrono.ChVector3d(0, 0, 0),
        chrono.QUNIT
    ),
    100.0,
    100.0,
    0.1
)

terrain.Initialize()

step_size = 0.01

while system.GetChTime() < 2.0:
    time = system.GetChTime()

    terrain.Synchronize(time)
    system.DoStepDynamics(step_size)
    terrain.Advance(step_size)
```

# 자주 헷갈리는 부분
## 1. Terrain과 일반 ground body는 다르다
일반 `ChBodyEasyBox`로 바닥을 만들 수도 있다. 하지만 Vehicle module에서는 terrain 객체를 사용하는 것이 더 적절하다.

그 이유는 아래와 같다.
- 타이어 모델이 terrain의 height, normal, friction 정보를 요구할 수 있음
- vehicle system과 terrain interface가 연결됨
- terrain별 전용 기능을 사용할 수 있음
- SCM, granular, CRG 같은 고급 지형 모델을 사용할 수 있음

## 2. `Initialize()`를 반드시 호출해야 한다
Patch를 추가하거나 soil parameter를 설정한 뒤에는 `terrain.Initialize()`을 호출해야 한다.
`Initialize()`를 호출하지 않으면 terrain이 제대로 생성되지 않거나, collision/visual asset이 반영되지 않을 수 있다.

## 3. `Synchronize()`와 `Advance()`는 simulation loop에 들어간다
terrain도 차량처럼 시간에 따라 상태가 업데이트될 수 있다.
특히 `SCMTerrain`처럼 변형 terrain은 시간 진행에 따라 내부 상태가 변한다.
따라서 루프 안에서 다음 흐름을 유지하는 것이 좋다.
```python
terrain.Synchronize(time)
system.DoStepDynamics(step_size)
terrain.Advance(step_size)
```

## 4. 좌표계 확인이 중요하다
Chrono 기본 예제는 보통 Z-up 좌표계를 사용한다. 즉, 높이 방향이 Z축이다.
하지만 일부 vehicle 예제에서는 Y-up 설정을 쓰는 경우도 있다.
```python
veh.ChWorldFrame.SetYUP()
```

이런 설정이 들어가면 높이 방향과 terrain 배치 방향이 달라질 수 있으므로 주의해야 한다.

> [!warning] 좌표계 실수  
> terrain이 안 보이거나 차량이 이상한 방향으로 떨어지면, 가장 먼저 중력 방향과 world frame 설정을 확인해야 한다.

# 대표 에러 및 해결법
## Terrain이 보이지 않음 
가능한 원인:
- `terrain.Initialize()`를 호출하지 않음
- patch 크기가 너무 작음
- patch 위치가 차량과 너무 멂
- texture 파일 경로가 틀림
- visual system에서 asset 업데이트가 안 됨

해결:
```python
terrain.Initialize()
```

patch 위치 확인:
```python
chrono.ChVector3d(0, 0, 0)
```

## 차량이 terrain을 통과함
가능한 원인:
- collision material 설정 문제
- terrain patch collision 비활성
- 차량 body 또는 tire collision 비활성
- contact method와 material 종류 불일치
- timestep이 너무 큼

해결 기준:
- `ChSystemNSC()`이면 `ChContactMaterialNSC()` 사용
- `ChSystemSMC()`이면 `ChContactMaterialSMC()` 사용
- timestep을 줄임
```python
step_size = 0.001
```

## SCM terrain이 너무 느림
가능한 원인:
- terrain 크기가 너무 큼
- grid spacing `delta`가 너무 작음
- active domain을 사용하지 않음
- bulldozing 계산이 무거움
해결:
- `delta`를 키움
- terrain 크기를 줄임
- `AddActiveDomain()` 사용
- bulldozing을 꺼서 비교
```python
terrain.EnableBulldozing(False)
```

## heightmap terrain이 이상하게 나옴
가능한 원인:
- heightmap 이미지 경로 오류
- BMP가 아닌 파일 사용
- `hMin`, `hMax` 범위 부적절
- length/width와 이미지 비율 불일치

해결:
- BMP 파일 사용
- `hMin`, `hMax`를 작게 잡고 테스트
- 정사각형 heightmap이면 length/width도 같은 값으로 시작










