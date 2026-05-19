# Interactive Driver

> Project Chrono Phase 3 - Vehicle / Driver  
> 주제: 키보드 기반 수동 차량 조작

---

## 1. 정의

Interactive Driver는 사용자가 키보드 또는 조이스틱으로 차량을 직접 조작할 수 있게 하는 driver model이다.

Chrono 공식 문서의 `ChInteractiveDriver`는 keyboard 또는 joystick control을 지원하기 위한 base 기능을 제공한다. Irrlicht visualization과 결합하면 차량 시뮬레이션 창에서 수동 운전이 가능하다.

---

## 2. 키 조작

| 키 | 기능 |
|---|---|
| W | throttle 증가 |
| S | braking 증가 |
| A | steering left |
| D | steering right |
| J | driver input lock/unlock |

주의할 점은 방향키가 아니라 **W/A/S/D**를 사용한다는 것이다.

---

## 3. 코드 구조

```python
driver = veh.ChInteractiveDriver(hmmwv.GetVehicle())

driver.SetSteeringDelta(0.06)
driver.SetThrottleDelta(0.02)
driver.SetBrakingDelta(0.06)

driver.Initialize()
```

| 함수 | 의미 |
|---|---|
| `SetSteeringDelta()` | 조향 입력 증가/감소 속도 |
| `SetThrottleDelta()` | throttle 증가/감소 속도 |
| `SetBrakingDelta()` | braking 증가/감소 속도 |

---

## 4. Visualization과 연결

```python
vis = veh.ChWheeledVehicleVisualSystemIrrlicht()
vis.Initialize()
vis.AttachVehicle(hmmwv.GetVehicle())
vis.AttachDriver(driver)
```

중요한 점은 `vis.Initialize()` 후 바로 simulation loop가 돌아야 한다는 것이다. Jupyter에서 visualization cell만 실행하고 loop가 없으면 창이 하얗게 뜨거나 응답 없음처럼 보일 수 있다.

---

## 5. Simulation Loop

```python
while vis.Run():
    time = hmmwv.GetSystem().GetChTime()

    vis.BeginScene()
    vis.Render()
    vis.EndScene()

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

---

## 6. Jupyter에서 주의할 점

Irrlicht 창은 Jupyter/VSCode 노트북에서 불안정할 수 있다.

```text
.ipynb → headless 데이터 생성, 그래프 분석
.py    → Irrlicht 수동 조작
```

---

## 7. Autosave 필요성

창을 닫거나 커널이 죽으면 메모리에 있던 `log_rows`가 사라질 수 있다. 따라서 interactive 실험에서는 simulation loop 안에서 CSV streaming 저장을 해야 한다.

```python
df_chunk.to_csv(csv_path, mode="a", header=not csv_path.exists(), index=False)
```

---

## 8. 핵심 정리

```text
Interactive driver는 사람이 WASD로 차량을 직접 조작하는 driver이다.
Jupyter보다 .py 스크립트에서 안정적으로 작동한다.
simulation loop가 없으면 Irrlicht 창이 응답 없음처럼 보일 수 있다.
수동 실험에서는 CSV autosave가 필수이다.
```
---
## 9. Wheeled Basic Example과의 차이

`driver_interactive_visual.py`는 이전의 wheeled vehicle 기본 예제와 구조가 매우 비슷하다.  
둘 다 HMMWV 차량, RigidTerrain, Irrlicht visualization, WASD 조작을 사용한다.

하지만 두 예제의 목적은 다르다.

| 예제 | 주요 목적 |
|---|---|
| `hmmwv_basic.py` | HMMWV 차량이 terrain 위에서 정상적으로 움직이는지 확인 |
| `driver_interactive_visual.py` | 키보드 입력이 `DriverInputs`로 변환되어 차량에 전달되는 구조 이해 |

즉, wheeled 예제는 차량 subsystem과 terrain interaction을 확인하는 예제이고, driver 예제는 입력 생성과 전달 흐름을 확인하는 예제이다.

Driver 예제의 핵심 흐름은 다음과 같다.

```text
W/A/S/D keyboard input
    ↓
ChInteractiveDriver
    ↓
DriverInputs
    ├─ m_steering
    ├─ m_throttle
    └─ m_braking
    ↓
hmmwv.Synchronize(time, driver_inputs, terrain)
    ↓
Vehicle motion
