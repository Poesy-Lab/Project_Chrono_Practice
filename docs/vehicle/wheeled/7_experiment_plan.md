# Experiment Plan

> Project Chrono Phase 3 - Vehicle / Wheeled Vehicle  
> 주제: HMMWV 기반 wheeled vehicle 실험 계획

---

## 1. 목적

이 문서는 Phase 3에서 수행할 wheeled vehicle 실험 계획을 정리한다.

앞선 문서에서는 Chrono Vehicle의 주요 subsystem을 정리했다.

```text
wheeled vehicle
 ├─ suspension
 ├─ steering
 ├─ tire
 ├─ driveline
 ├─ HMMWV structure
 └─ simulation loop
```

이제 목표는 단순히 문서를 읽는 것이 아니라, 실제로 Chrono에서 차량을 주행시키고 데이터를 저장하여 분석하는 것이다.

최종 목표는 다음과 같다.

```text
HMMWV 예제 실행
    ↓
차량 상태 데이터 저장
    ↓
주행 성능 지표 계산
    ↓
terrain / tire / steering 조건 변화 비교
    ↓
로버 최적 설계로 확장
```

---

## 2. Phase 3 전체 실험 목표

Phase 3에서 달성해야 할 최소 목표는 다음과 같다.

| 단계 | 목표 |
|---|---|
| Step 1 | HMMWV 예제 실행 |
| Step 2 | simulation loop 구조 이해 |
| Step 3 | 차량 위치, 속도, 자세 데이터 저장 |
| Step 4 | steering/throttle 입력에 따른 차량 반응 확인 |
| Step 5 | terrain 조건 변화에 따른 주행 성능 비교 |
| Step 6 | tire model 또는 friction 변화 실험 |
| Step 7 | 로버 최적 설계용 변수와 성능 지표 정의 |

---

## 3. 사용 모델

초기 실험 모델은 Chrono에서 제공하는 HMMWV를 사용한다.

| 항목 | 선택 |
|---|---|
| Vehicle | HMMWV |
| 초기 추천 모델 | HMMWV_Reduced |
| 상세 분석 모델 | HMMWV_Full |
| Terrain | RigidTerrain |
| Tire | Rigid tire 또는 TMeasy tire |
| Visualization | Irrlicht |
| Output | CSV + plot |

처음부터 복잡한 SCMTerrain이나 FEA tire로 가지 않고, 기본 차량 주행과 데이터 저장이 안정적으로 되는지 확인하는 것이 우선이다.

---

## 4. 추천 폴더 구조

프로젝트 레포에서는 다음 구조를 추천한다.

```text
docs/vehicle/wheeled/
 ├─ index.md
 ├─ suspension.md
 ├─ steering.md
 ├─ tire.md
 ├─ driveline.md
 ├─ hmmwv_structure.md
 ├─ simulation_loop.md
 └─ experiment_plan.md

notebooks/phase3/
 ├─ chrono4_hmmwv_basic.ipynb
 ├─ chrono5_steering_response.ipynb
 └─ chrono6_tire_terrain_test.ipynb

results/phase3/
 ├─ hmmwv_basic_log.csv
 ├─ steering_response_log.csv
 ├─ tire_comparison_log.csv
 └─ figures/
```

팀 레포 구조가 다르면 `notebooks`와 `results` 위치는 프로젝트 규칙에 맞게 조정한다.

---

## 5. 실험 1: HMMWV 기본 주행

### 5.1 목적

HMMWV가 평탄한 rigid terrain 위에서 정상적으로 주행하는지 확인한다.

### 5.2 조건

| 항목 | 값 |
|---|---|
| Vehicle | HMMWV_Reduced |
| Terrain | Flat RigidTerrain |
| Tire | Rigid 또는 TMeasy |
| Steering | 0 |
| Throttle | 일정 값 |
| Braking | 0 |
| Simulation time | 10~20 s |

### 5.3 저장 데이터

```text
time, x, y, z, speed, steering, throttle, braking
```

가능하면 다음도 추가한다.

```text
roll, pitch, yaw
```

### 5.4 분석 항목

| 분석 | 의미 |
|---|---|
| x-position vs time | 전진 거리 확인 |
| speed vs time | 가속 및 정상 속도 확인 |
| yaw vs time | 직진 안정성 확인 |
| pitch vs time | 가속 시 차체 자세 변화 확인 |

### 5.5 기대 결과

```text
차량이 일정 throttle 입력에 따라 전진해야 한다.
평탄 지형에서 steering = 0이면 yaw 변화는 작아야 한다.
속도는 초기에 증가하다가 저항/동력 한계에 따라 완만해져야 한다.
```

---

## 6. 실험 2: Steering Response

### 6.1 목적

조향 입력이 차량 궤적과 yaw motion에 미치는 영향을 확인한다.

### 6.2 조건

| 항목 | 값 |
|---|---|
| Vehicle | HMMWV_Reduced |
| Terrain | Flat RigidTerrain |
| Tire | TMeasy 권장 |
| Throttle | 일정 값 |
| Steering | 0.0, 0.2, 0.5 |
| Simulation time | 10~20 s |

### 6.3 입력 시나리오

```text
Case 1: steering = 0.0
Case 2: steering = 0.2
Case 3: steering = 0.5
```

또는 step input:

```text
0~3 s: steering = 0.0
3~10 s: steering = 0.3
```

### 6.4 저장 데이터

```text
time, x, y, yaw, yaw_rate, speed, steering, throttle
```

### 6.5 분석 항목

| 분석 | 의미 |
|---|---|
| x-y trajectory | 차량 경로 확인 |
| yaw vs time | heading 변화 확인 |
| yaw rate vs time | 회전 응답 확인 |
| turning radius | 조향 입력별 회전 반경 비교 |

### 6.6 기대 결과

```text
steering 입력이 커질수록 차량의 yaw 변화가 커진다.
x-y trajectory에서 회전 반경이 작아진다.
너무 큰 steering에서는 slip이나 불안정한 거동이 나타날 수 있다.
```

---

## 7. 실험 3: Terrain Friction 변화

### 7.1 목적

지형 마찰계수가 차량 주행 성능에 미치는 영향을 확인한다.

### 7.2 조건

| 항목 | 값 |
|---|---|
| Vehicle | HMMWV_Reduced |
| Terrain | RigidTerrain |
| Friction coefficient | 0.3, 0.6, 0.9 |
| Throttle | 일정 |
| Steering | 0 |
| Tire | Rigid 또는 TMeasy |

### 7.3 저장 데이터

```text
time, x, speed, throttle, friction
```

가능하면 다음도 추가한다.

```text
wheel angular speed, estimated slip ratio
```

### 7.4 분석 항목

| 분석 | 의미 |
|---|---|
| speed vs time | 마찰계수별 가속 성능 |
| distance vs time | 주행 거리 비교 |
| slip ratio | 바퀴 헛돎 정도 |
| acceleration | 초기 가속 성능 |

### 7.5 기대 결과

```text
마찰계수가 낮을수록 같은 throttle에서도 실제 추진력이 작아질 수 있다.
마찰계수가 너무 낮으면 wheel spin 또는 slip이 증가할 수 있다.
```

---

## 8. 실험 4: Tire Model 비교

### 8.1 목적

타이어 모델 선택이 차량 주행 결과에 미치는 영향을 확인한다.

### 8.2 조건

| 항목 | 값 |
|---|---|
| Vehicle | HMMWV |
| Terrain | Flat RigidTerrain |
| Tire models | Rigid, Fiala, TMeasy |
| Steering | 0 또는 step steering |
| Throttle | 일정 |
| Simulation time | 10~20 s |

### 8.3 저장 데이터

```text
time, x, y, speed, yaw, steering, throttle, tire_model
```

가능하면 다음도 추가한다.

```text
wheel angular speed, slip ratio
```

### 8.4 분석 항목

| 분석 | 의미 |
|---|---|
| speed curve | tire model별 가속 특성 |
| x-y trajectory | tire model별 경로 차이 |
| yaw response | 선회 반응 차이 |
| stability | 진동 또는 불안정성 확인 |

### 8.5 기대 결과

```text
Rigid tire는 단순 접촉 기반이므로 빠르게 실행된다.
TMeasy/Fiala는 slip 기반 힘 모델을 사용하므로 handling 특성이 더 잘 나타날 수 있다.
타이어 모델에 따라 같은 입력에서도 차량 속도와 선회 응답이 달라질 수 있다.
```

---

## 9. 실험 5: Slope Terrain 주행

### 9.1 목적

경사 지형에서 차량의 등판 성능과 안정성을 확인한다.

### 9.2 조건

| 항목 | 값 |
|---|---|
| Vehicle | HMMWV_Reduced |
| Terrain | Inclined RigidTerrain |
| Slope angle | 5°, 10°, 15° |
| Throttle | 일정 |
| Steering | 0 |
| Tire | TMeasy 권장 |

### 9.3 저장 데이터

```text
time, x, z, speed, pitch, throttle, slope_angle
```

가능하면 다음도 추가한다.

```text
wheel angular speed, slip ratio
```

### 9.4 분석 항목

| 분석 | 의미 |
|---|---|
| climb success | 등판 성공 여부 |
| speed loss | 경사 증가에 따른 속도 감소 |
| pitch angle | 차체 자세 변화 |
| distance traveled | 주행 가능 거리 |

### 9.5 기대 결과

```text
경사각이 증가할수록 속도가 감소한다.
일정 경사 이상에서는 등판 실패 또는 slip 증가가 발생할 수 있다.
```

---

## 10. 실험 6: SCMTerrain 기초 실험

### 10.1 목적

변형 가능한 지형에서 차량/타이어 반응을 확인한다.

### 10.2 조건

| 항목 | 값 |
|---|---|
| Vehicle | HMMWV 또는 간단한 rover |
| Terrain | SCMTerrain |
| Soil parameters | 기본값에서 시작 |
| Throttle | 일정 |
| Steering | 0 |
| Tire | Rigid 또는 TMeasy |

### 10.3 저장 데이터

```text
time, x, speed, z, pitch, throttle
```

가능하면 다음도 추가한다.

```text
sinkage, slip ratio, wheel angular speed
```

### 10.4 분석 항목

| 분석 | 의미 |
|---|---|
| sinkage | 바퀴 또는 차량 침하량 |
| speed reduction | deformable terrain에서의 속도 감소 |
| slip | 흙/모래 지형에서 바퀴 헛돎 |
| terrain deformation | 바퀴 궤적에 따른 지형 변형 |

### 10.5 기대 결과

```text
RigidTerrain보다 SCMTerrain에서 차량 속도가 낮아질 수 있다.
토양 강도가 낮으면 sinkage와 slip이 증가할 수 있다.
```

---

## 11. 공통 CSV 저장 항목

모든 실험에서 공통으로 저장하면 좋은 항목은 다음과 같다.

```text
time,
x, y, z,
speed,
roll, pitch, yaw,
steering, throttle, braking,
case_name
```

추가 확장 항목:

```text
vx, vy, vz,
yaw_rate,
wheel_omega_FL, wheel_omega_FR, wheel_omega_RL, wheel_omega_RR,
slip_FL, slip_FR, slip_RL, slip_RR,
terrain_friction,
tire_model,
slope_angle
```

---

## 12. 기본 성능 지표

실험 결과를 단순 그래프에서 끝내지 않고 성능 지표로 정리하면 좋다.

| 지표 | 계산/의미 |
|---|---|
| Average speed | 평균 주행 속도 |
| Travel distance | 총 이동 거리 |
| Max roll angle | 전복 위험성 |
| Max pitch angle | 등판/제동 안정성 |
| RMS yaw rate | 조향 안정성 |
| Slip ratio 평균 | 바퀴 헛돎 정도 |
| Energy proxy | throttle × time 등 단순 지표 |
| Success/failure | 목표 거리 도달 여부 |

최적화 문제로 확장할 때는 다음과 같은 objective를 생각할 수 있다.

```text
maximize: travel distance, average speed, stability
minimize: slip ratio, energy consumption, roll/pitch angle
```

---

## 13. Notebook 작성 순서

실제 노트북은 다음 순서로 작성한다.

```text
1. Import libraries
2. Set paths
3. Define simulation parameters
4. Create vehicle
5. Create terrain
6. Create driver
7. Run simulation loop
8. Save CSV
9. Plot result
10. Write analysis
```

노트북 안에는 단순 코드만 두지 말고, 각 셀 위에 Markdown 설명을 추가한다.

예시:

```text
## 1. Vehicle Initialization
이 셀에서는 HMMWV_Reduced 모델을 생성하고 초기 위치를 설정한다.
```

---

## 14. 첫 번째 노트북 목표

가장 먼저 만들 노트북은 다음이다.

```text
notebooks/phase3/chrono4_hmmwv_basic.ipynb
```

목표:

```text
HMMWV_Reduced + RigidTerrain
기본 주행
CSV 저장
speed-time plot
x-y trajectory plot
```

성공 기준:

```text
1. 차량이 정상적으로 주행한다.
2. CSV 파일이 저장된다.
3. speed vs time 그래프가 나온다.
4. x-y trajectory 그래프가 나온다.
5. markdown 분석이 포함된다.
```

---

## 15. GitHub 문서화 기준

실험이 끝나면 docs 문서에 다음을 추가한다.

```text
1. 실험 목적
2. 사용한 vehicle/terrain/tire 조건
3. 주요 코드 구조
4. 그래프 이미지
5. 결과 해석
6. 다음 개선 방향
```

이미지는 다음 위치에 저장한다.

```text
docs/vehicle/wheeled/figures/
```

Markdown에서는 다음처럼 삽입한다.

```md
![Speed plot](figures/hmmwv_basic_speed.png)
```

---

## 16. Phase 3 완료 기준

Phase 3 wheeled 파트의 완료 기준은 다음과 같다.

```text
1. docs/vehicle/wheeled 문서 8개 작성
2. HMMWV 기본 예제 실행 성공
3. HMMWV basic notebook 작성
4. CSV logging 성공
5. speed-time plot 생성
6. x-y trajectory plot 생성
7. steering 또는 terrain friction 조건 변화 실험 1개 이상 수행
8. 결과를 md에 정리
```

---

## 17. 프로젝트 최종 목표와의 연결

이번 Phase 3의 역할은 최종 로버 최적 설계 프로젝트의 기초이다.

```text
Phase 3:
    Chrono Vehicle 구조 이해
    HMMWV로 차량-지형 interaction 실습
    주행 데이터 저장

Next:
    Rover model 구성
    Terrain randomization
    Design variable sweep
    Optimization / AI model
```

즉, Phase 3는 단순한 차량 예제 실행이 아니라, 이후 최적화와 AI 기반 설계로 넘어가기 위한 simulation data pipeline의 출발점이다.

---

## 18. 핵심 정리

```text
Phase 3 실험은 HMMWV + terrain + driver input + CSV logging으로 시작한다.
처음에는 RigidTerrain에서 기본 주행을 확인한다.
이후 steering, friction, tire model, slope, SCMTerrain 순서로 확장한다.
모든 실험은 성능 지표와 연결되어야 한다.
최종 목표는 환경 변수와 차량 설계 변수가 주행 성능에 미치는 영향을 정량화하는 것이다.
```

---

## 19. 참고 자료

- Project Chrono 공식 문서: PyChrono vehicle tutorial  
  https://api.projectchrono.org/tutorial_pychrono_demo_vehicle.html

- Project Chrono 공식 문서: Wheeled vehicles  
  https://api.projectchrono.org/wheeled_vehicle.html

- Project Chrono 공식 문서: Vehicle overview  
  https://api.projectchrono.org/vehicle_overview.html

- Project Chrono 공식 문서: Tire models  
  https://api.projectchrono.org/wheeled_tire.html

- Project Chrono 공식 문서: Driveline models  
  https://api.projectchrono.org/wheeled_driveline.html

- Project Chrono 공식 문서: HMMWV vehicle models  
  https://api.projectchrono.org/group__vehicle__models__hmmwv.html

- GitHub Demo: demo_VEH_HMMWV9_YUP.py  
  https://github.com/projectchrono/chrono/blob/main/src/demos/python/vehicle/demo_VEH_HMMWV9_YUP.py
