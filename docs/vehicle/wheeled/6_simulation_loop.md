# Simulation Loop

> Project Chrono Phase 3 - Vehicle / Wheeled Vehicle  
> 주제: Chrono Vehicle simulation loop와 `Synchronize()` / `Advance()` 구조

---

## 1. 목적

이 문서는 Chrono::Vehicle 예제에서 반복적으로 등장하는 simulation loop의 구조를 정리한다.

HMMWV 예제를 처음 보면 vehicle, terrain, driver, visualization이 각각 `Synchronize()`와 `Advance()`를 호출하기 때문에 코드 흐름이 복잡해 보인다.  
하지만 핵심은 단순하다.

```text
현재 시간에서 subsystem 상태를 맞추고
→ timestep만큼 각 subsystem을 전진시킨다
```

즉, simulation loop는 Chrono Vehicle에서 여러 subsystem이 서로 정보를 주고받으며 시간 적분을 수행하는 중심 구조이다.

---

## 2. 기본 구조

Chrono Vehicle 예제의 simulation loop는 보통 다음 형태를 가진다.

```python
while vis.Run():
    time = hmmwv.GetSystem().GetChTime()

    driver_inputs = driver.GetInputs()

    driver.Synchronize(time)
    terrain.Synchronize(time)
    hmmwv.Synchronize(time, driver_inputs, terrain)
    vis.Synchronize(time, driver_inputs)

    driver.Advance(step_size)
    terrain.Advance(step_size)
    hmmwv.Advance(step_size)
    vis.Advance(step_size)
```

이 구조는 크게 두 단계로 나뉜다.

```text
1. Synchronize 단계
2. Advance 단계
```

---

## 3. `Synchronize()`란?

`Synchronize()`는 현재 시뮬레이션 시간에서 각 subsystem이 서로 필요한 정보를 교환하는 단계이다.

예를 들어 vehicle은 다음 정보를 알아야 한다.

| 필요한 정보 | 제공 subsystem |
|---|---|
| throttle, steering, braking | Driver |
| terrain height, contact, friction | Terrain |
| tire force 계산 조건 | Terrain + Tire |
| visualization 상태 | Vehicle + Driver |

즉, `Synchronize()`는 시간 적분을 직접 수행하는 함수라기보다, **현재 timestep에서 subsystem 간 상태를 맞추는 함수**로 이해하면 된다.

---

## 4. `Advance()`란?

`Advance()`는 각 subsystem을 실제로 한 timestep만큼 전진시키는 단계이다.

예를 들어 vehicle의 `Advance(step_size)`에서는 내부적으로 다음 일이 일어난다.

```text
driver input 반영
powertrain / driveline update
steering update
tire force 계산
suspension force 계산
rigid body dynamics 계산
system time integration
```

따라서 `Advance()`는 실제 동역학 계산과 시간 업데이트에 해당한다.

---

## 5. 한 timestep에서 일어나는 일

Chrono Vehicle simulation loop를 한 timestep 기준으로 풀어쓰면 다음과 같다.

```text
1. 현재 시간 t 확인
2. driver input 계산
3. driver, terrain, vehicle, visualization 상태 동기화
4. vehicle 내부 subsystem force/moment 계산 준비
5. timestep dt만큼 driver advance
6. timestep dt만큼 terrain advance
7. timestep dt만큼 vehicle dynamics advance
8. timestep dt만큼 visualization advance
9. 시간 t + dt로 이동
```

도식화하면 다음과 같다.

```text
time t
  ↓
Driver input
  ↓
Synchronize all subsystems
  ↓
Compute force / moment / contact information
  ↓
Advance all subsystems
  ↓
time t + dt
```

---

## 6. 각 subsystem의 역할

### 6.1 Driver

Driver subsystem은 사용자의 키보드 입력, 미리 정의된 steering/throttle 함수, 또는 path-following controller로부터 운전 입력을 만든다.

대표 입력:

```text
steering
throttle
braking
```

코드에서는 보통 다음과 같이 얻는다.

```python
driver_inputs = driver.GetInputs()
```

---

### 6.2 Vehicle

Vehicle subsystem은 차량의 실제 물리 모델을 포함한다.

```text
chassis
suspension
steering
wheels
tires
brakes
driveline
powertrain
```

Vehicle은 driver input과 terrain 정보를 받아 바퀴 힘, 서스펜션 힘, 차체 운동을 계산한다.

---

### 6.3 Terrain

Terrain subsystem은 지형의 높이, 마찰, 접촉 조건을 제공한다.

예시:

```text
RigidTerrain
SCMTerrain
Height map terrain
Granular terrain
```

타이어는 terrain 정보를 사용하여 접촉점과 tire force를 계산한다.

---

### 6.4 Visualization

Visualization subsystem은 시뮬레이션 결과를 화면에 보여준다.

예제에 따라 다음 방식이 사용될 수 있다.

```text
Irrlicht visualization
VSG visualization
No visualization
```

현재 사용자의 환경에서는 `pychrono.vsg3d`가 없으므로 VSG 기반 예제보다 Irrlicht 기반 예제가 더 적합하다.

---

## 7. 왜 `Synchronize()`가 먼저인가?

`Advance()`를 호출하기 전에 `Synchronize()`를 먼저 호출하는 이유는 각 subsystem이 최신 정보를 알아야 하기 때문이다.

예를 들어 차량을 업데이트하려면:

```text
driver가 어떤 steering을 넣었는지 알아야 하고
terrain이 어떤 지면 높이와 마찰을 갖는지 알아야 하며
tire가 어디에서 접촉하는지 알아야 한다
```

만약 정보를 갱신하지 않고 `Advance()`만 하면, vehicle은 이전 timestep의 오래된 입력이나 지형 정보를 사용할 수 있다.

따라서 올바른 순서는 다음과 같다.

```text
Get current information
→ Synchronize
→ Advance
```

---

## 8. Vehicle 내부에서의 계산 흐름

`hmmwv.Advance(step_size)` 내부를 개념적으로 풀면 다음과 같다.

```text
Powertrain:
    throttle input → engine torque

Driveline:
    engine torque → wheel torque distribution

Steering:
    steering input → wheel steer angle

Tire:
    wheel speed + terrain contact → tire force

Suspension:
    wheel motion → spring/damper force

Chassis:
    all external forces → rigid body motion

Integrator:
    position, velocity, orientation update
```

즉, 차량 하나가 움직이기 위해 여러 subsystem이 동시에 작동한다.

---

## 9. `step_size`의 의미

`step_size`는 시뮬레이션의 시간 간격이다.

```python
step_size = 1e-3
```

라면 한 번의 `Advance()`마다 0.001초씩 시간이 진행된다.

작은 timestep을 쓰면:

```text
장점: 정확도와 안정성이 좋아짐
단점: 계산 시간이 증가함
```

큰 timestep을 쓰면:

```text
장점: 빠름
단점: 수치 불안정이나 결과 오차 가능성 증가
```

Vehicle simulation에서는 contact, tire force, suspension dynamics가 함께 작동하므로 timestep 선택이 중요하다.

---

## 10. Rendering step과 dynamics step

시뮬레이션에서는 물리 계산 timestep과 화면 출력 timestep을 다르게 둘 수 있다.

예:

```python
step_size = 1e-3
render_step_size = 1.0 / 50
```

의미:

```text
물리 계산: 0.001초마다 수행
화면 렌더링: 0.02초마다 수행
```

이렇게 하는 이유는 모든 물리 timestep마다 화면을 그리면 너무 느려지기 때문이다.

---

## 11. 실시간 계수

일부 예제에서는 real-time simulation을 맞추기 위해 realtime timer를 사용한다.

개념:

```text
시뮬레이션 시간이 실제 시간보다 너무 빠르면 잠시 대기
시뮬레이션 시간이 실제 시간보다 느리면 그대로 진행
```

이를 통해 사람이 키보드로 조작하는 interactive driver에서 자연스럽게 주행할 수 있다.

---

## 12. 데이터 저장 위치

Phase 3에서는 simulation loop 안에서 데이터를 저장하는 코드가 중요하다.

예시:

```python
log_data = []

while vis.Run():
    time = hmmwv.GetSystem().GetChTime()

    pos = hmmwv.GetVehicle().GetPos()
    speed = hmmwv.GetVehicle().GetSpeed()

    log_data.append([
        time,
        pos.x,
        pos.y,
        pos.z,
        speed
    ])

    # synchronize and advance
```

시뮬레이션이 끝난 후 CSV로 저장한다.

```python
import pandas as pd

df = pd.DataFrame(log_data, columns=["time", "x", "y", "z", "speed"])
df.to_csv("vehicle_log.csv", index=False)
```

---

## 13. 권장 CSV 형식

HMMWV 기본 주행 실험에서는 다음 항목을 저장하면 좋다.

```text
time,
x, y, z,
vx, vy, vz,
speed,
roll, pitch, yaw,
steering, throttle, braking
```

추후 확장 항목:

```text
wheel angular speed
tire slip ratio
tire force
suspension travel
engine speed
engine torque
```

---

## 14. 실험용 loop 구조 예시

아래는 Phase 3 실험용으로 정리한 최소 구조이다.

```python
log_data = []

while vis.Run():
    time = hmmwv.GetSystem().GetChTime()

    driver_inputs = driver.GetInputs()

    vehicle = hmmwv.GetVehicle()
    pos = vehicle.GetPos()
    speed = vehicle.GetSpeed()

    log_data.append([
        time,
        pos.x,
        pos.y,
        pos.z,
        speed,
        driver_inputs.m_steering,
        driver_inputs.m_throttle,
        driver_inputs.m_braking
    ])

    driver.Synchronize(time)
    terrain.Synchronize(time)
    hmmwv.Synchronize(time, driver_inputs, terrain)
    vis.Synchronize(time, driver_inputs)

    driver.Advance(step_size)
    terrain.Advance(step_size)
    hmmwv.Advance(step_size)
    vis.Advance(step_size)
```

---

## 15. Notebook에서의 추천 구성

주피터 노트북에서는 simulation loop를 다음 section으로 나누면 좋다.

```text
1. Import
2. Parameter setting
3. Vehicle creation
4. Terrain creation
5. Driver and visualization
6. Simulation loop
7. CSV save
8. Plot result
9. Analysis
```

노트북 파일명 예시:

```text
notebooks/phase3/chrono4_hmmwv_basic.ipynb
```

문서 정리용 md 파일:

```text
docs/vehicle/wheeled/simulation_loop.md
```

---

## 16. 자주 헷갈리는 점

### 16.1 `Synchronize()`가 적분인가?

아니다.  
`Synchronize()`는 subsystem 간 정보를 맞추는 단계이고, 실제 시간 전진은 `Advance()`에서 일어난다.

---

### 16.2 `Advance()`는 한 번에 전체 시뮬레이션을 끝내는가?

아니다.  
`Advance(step_size)`는 한 timestep만 전진한다.  
따라서 while loop 안에서 반복 호출해야 전체 시뮬레이션이 진행된다.

---

### 16.3 Vehicle만 `Advance()`하면 되는가?

일반적으로는 driver, terrain, vehicle, visualization을 모두 같은 timestep으로 advance한다.  
그래야 subsystem 시간이 서로 어긋나지 않는다.

---

### 16.4 Visualization 없는 simulation도 가능한가?

가능하다.  
나중에 데이터 생성 또는 강화학습을 할 때는 visualization 없이 headless simulation으로 돌리는 것이 더 빠르다.

---

## 17. 프로젝트와의 연결

로버 최적설계 프로젝트에서는 simulation loop가 데이터 생성 파이프라인의 핵심이 된다.

```text
환경 변수 설정
    ↓
차량 설계 변수 설정
    ↓
simulation loop 실행
    ↓
CSV 데이터 저장
    ↓
성능 지표 계산
    ↓
최적화 또는 AI 학습
```

따라서 Phase 3에서 simulation loop를 정확히 이해해야 이후 terrain randomization, rover parameter sweep, RL environment 제작으로 확장할 수 있다.

---

## 18. 핵심 정리

```text
Chrono Vehicle simulation loop는 Synchronize와 Advance의 반복이다.
Synchronize는 subsystem 간 정보를 맞추는 단계이다.
Advance는 timestep만큼 실제 동역학을 전진시키는 단계이다.
Driver, terrain, vehicle, visualization은 같은 loop 안에서 함께 업데이트된다.
Phase 3에서는 loop 안에서 차량 상태를 저장하여 CSV 데이터셋을 만드는 것이 중요하다.
```

---

## 19. 참고 자료

- Project Chrono 공식 문서: PyChrono vehicle tutorial  
  https://api.projectchrono.org/tutorial_pychrono_demo_vehicle.html

- Project Chrono 공식 문서: Chrono::Vehicle overview  
  https://api.projectchrono.org/vehicle_overview.html

- Project Chrono 공식 문서: Wheeled vehicles  
  https://api.projectchrono.org/wheeled_vehicle.html

- GitHub Demo: demo_VEH_HMMWV9_YUP.py  
  https://github.com/projectchrono/chrono/blob/main/src/demos/python/vehicle/demo_VEH_HMMWV9_YUP.py
