---
title: "PyChrono JSON Powertrain Workflow"
author: ""
last_modified: "2026-05-11"
tags:
  - chrono
  - vehicle
  - pychrono
  - json
  - powertrain
---

# PyChrono JSON Powertrain Workflow

이 문서는 PyChrono에서 JSON 기반 powertrain을 만들고, 실험 파라미터를 바꾸고, 결과를 CSV로 저장하는 흐름을 정리한다.

> [!important] 실행 환경
> 이 프로젝트에서는 모든 레슨 실행 시 conda 환경 `chrono`를 사용한다.
>
> ```bash
> conda activate chrono
> source setup_chrono_env.sh
> python lessons/phase3/your_lesson.py
> ```
>
> `python3` 대신 반드시 `python` 명령을 사용한다.

---

## 1. JSON 기반 powertrain 생성

가장 기본적인 흐름은 다음과 같다.

```python
import pychrono as chrono
import pychrono.vehicle as veh

vehicle_file = veh.GetVehicleDataFile("hmmwv/vehicle/HMMWV_Vehicle.json")
engine_file = veh.GetVehicleDataFile("hmmwv/powertrain/HMMWV_EngineSimpleMap.json")
transmission_file = veh.GetVehicleDataFile(
    "hmmwv/powertrain/HMMWV_AutomaticTransmissionSimpleMap.json"
)

vehicle = veh.WheeledVehicle(vehicle_file, chrono.ChContactMethod_NSC)
vehicle.Initialize(
    chrono.ChCoordsysd(
        chrono.ChVector3d(0, 0, 0.5),
        chrono.QUNIT,
    )
)

engine = veh.ReadEngineJSON(engine_file)
transmission = veh.ReadTransmissionJSON(transmission_file)
powertrain = veh.ChPowertrainAssembly(engine, transmission)
vehicle.InitializePowertrain(powertrain)
```

핵심은 engine JSON과 transmission JSON을 따로 읽는 것이다.

```text
Engine JSON -> ReadEngineJSON()
Transmission JSON -> ReadTransmissionJSON()
Engine + Transmission -> ChPowertrainAssembly()
Assembly -> vehicle.InitializePowertrain()
```

---

## 2. HMMWV wrapper에서 선택하기

HMMWV 같은 내장 모델 wrapper는 enum으로 powertrain type을 고를 수 있다.

```python
hmmwv = veh.HMMWV_Full()
hmmwv.SetContactMethod(chrono.ChContactMethod_SMC)
hmmwv.SetInitPosition(
    chrono.ChCoordsysd(
        chrono.ChVector3d(0, 0, 1.0),
        chrono.QUNIT,
    )
)

hmmwv.SetEngineType(veh.EngineModelType_SIMPLE_MAP)
hmmwv.SetTransmissionType(veh.TransmissionModelType_AUTOMATIC_SIMPLE_MAP)
hmmwv.SetDriveType(veh.DrivelineTypeWV_AWD)
hmmwv.Initialize()
```

다른 조합:

```python
hmmwv.SetEngineType(veh.EngineModelType_SHAFTS)
hmmwv.SetTransmissionType(veh.TransmissionModelType_AUTOMATIC_SHAFTS)
```

또는:

```python
hmmwv.SetEngineType(veh.EngineModelType_SIMPLE)
hmmwv.SetTransmissionType(veh.TransmissionModelType_AUTOMATIC_SIMPLE_CVT)
```

> [!warning] enum 이름 확인
> PyChrono 빌드 버전에 따라 enum 이름이 다를 수 있다.
> 실행 전 다음처럼 확인할 수 있다.
>
> ```python
> import pychrono.vehicle as veh
>
> print([name for name in dir(veh) if "EngineModelType" in name])
> print([name for name in dir(veh) if "TransmissionModelType" in name])
> ```

---

## 3. Powertrain 상태 읽기

시뮬레이션 루프 안에서 engine과 transmission 값을 읽어 CSV로 저장할 수 있다.

```python
import math

def read_powertrain_state(vehicle):
    engine = vehicle.GetEngine()
    transmission = vehicle.GetTransmission()

    row = {}

    if engine:
        engine_speed = engine.GetMotorSpeed()
        row["engine_rpm"] = engine_speed * 60.0 / (2.0 * math.pi)
        row["engine_torque_Nm"] = engine.GetOutputMotorshaftTorque()
        row["engine_reaction_torque_Nm"] = engine.GetChassisReactionTorque()

    if transmission:
        row["gear"] = transmission.GetCurrentGear()
        row["driveshaft_torque_Nm"] = transmission.GetOutputDriveshaftTorque()
        row["motorshaft_speed_rad_s"] = transmission.GetOutputMotorshaftSpeed()
        row["transmission_reaction_torque_Nm"] = (
            transmission.GetChassisReactionTorque()
        )

        if transmission.IsAutomatic():
            auto = transmission.asAutomatic()
            if auto:
                row["has_torque_converter"] = auto.HasTorqueConverter()
                row["tc_slippage"] = auto.GetTorqueConverterSlippage()
                row["tc_input_torque_Nm"] = auto.GetTorqueConverterInputTorque()
                row["tc_output_torque_Nm"] = auto.GetTorqueConverterOutputTorque()
                row["tc_output_speed_rad_s"] = auto.GetTorqueConverterOutputSpeed()

    return row
```

HMMWV wrapper를 쓰면 vehicle 객체를 한 번 꺼내면 된다.

```python
vehicle = hmmwv.GetVehicle()
state = read_powertrain_state(vehicle)
```

JSON `WheeledVehicle`을 직접 쓰는 경우에는 그대로 `vehicle`을 넘긴다.

---

## 4. Wheel speed 함께 기록하기

powertrain만 기록하면 실제 지면 추진으로 연결됐는지 알기 어렵다.
wheel speed와 vehicle speed도 같이 저장하는 것이 좋다.

```python
def read_wheel_state(vehicle):
    return {
        "omega_FL": vehicle.GetSpindleOmega(0, veh.LEFT),
        "omega_FR": vehicle.GetSpindleOmega(0, veh.RIGHT),
        "omega_RL": vehicle.GetSpindleOmega(1, veh.LEFT),
        "omega_RR": vehicle.GetSpindleOmega(1, veh.RIGHT),
    }
```

간단한 slip ratio 근사는 다음처럼 계산할 수 있다.

$$
\kappa \approx \frac{R\omega - V_x}{\max(|V_x|, \epsilon)}
$$

| 기호 | 의미 |
|---|---|
| $\kappa$ | slip ratio 근사 |
| $R$ | tire rolling radius |
| $\omega$ | wheel angular speed |
| $V_x$ | vehicle longitudinal speed |
| $\epsilon$ | 0 나눗셈 방지용 작은 값 |

```python
def estimate_slip(vehicle_speed, wheel_omega, tire_radius, eps=0.1):
    return (tire_radius * wheel_omega - vehicle_speed) / max(abs(vehicle_speed), eps)
```

> [!warning] slip ratio 근사 주의
> 타이어 모델 내부의 정확한 slip 정의와 다를 수 있다.
> 하지만 초기 실험에서 "토크를 키웠더니 바퀴만 빨리 돌고 차량은 덜 움직이는가?"를 확인하기에는 유용하다.

---

## 5. CSV 저장 예시

```python
import csv
from pathlib import Path

result_dir = Path("results") / "phase3" / "powertrain"
result_dir.mkdir(parents=True, exist_ok=True)
csv_path = result_dir / "powertrain_log.csv"

fieldnames = [
    "time",
    "throttle",
    "braking",
    "speed",
    "x",
    "y",
    "z",
    "engine_rpm",
    "engine_torque_Nm",
    "gear",
    "driveshaft_torque_Nm",
    "omega_FL",
    "omega_FR",
    "omega_RL",
    "omega_RR",
]

with csv_path.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    while vis.Run():
        time = vehicle.GetSystem().GetChTime()
        driver_inputs = driver.GetInputs()

        # synchronize
        driver.Synchronize(time)
        vehicle.Synchronize(time, driver_inputs, terrain)
        terrain.Synchronize(time)
        vis.Synchronize(time, driver_inputs)

        # log
        pos = vehicle.GetPos()
        row = {
            "time": time,
            "throttle": driver_inputs.m_throttle,
            "braking": driver_inputs.m_braking,
            "speed": vehicle.GetSpeed(),
            "x": pos.x,
            "y": pos.y,
            "z": pos.z,
        }
        row.update(read_powertrain_state(vehicle))
        row.update(read_wheel_state(vehicle))
        writer.writerow({key: row.get(key, "") for key in fieldnames})

        # advance
        driver.Advance(step_size)
        vehicle.Advance(step_size)
        terrain.Advance(step_size)
        vis.Advance(step_size)
```

---

## 6. JSON 파라미터 sweep 방식

Chrono data 폴더의 원본 JSON을 직접 수정하지 말고, 프로젝트 안의 실험용 JSON으로 복사해서 수정하는 것이 안전하다.

추천 구조:

```text
lessons/phase3/your_name/data/powertrain/
  HMMWV_EngineSimpleMap_torque_low.json
  HMMWV_EngineSimpleMap_torque_high.json
  HMMWV_AutomaticTransmissionSimpleMap_short_gears.json
  HMMWV_AutomaticTransmissionSimpleMap_long_gears.json
```

Python에서 `Path`를 사용한다.

```python
from pathlib import Path

project_root = Path(__file__).resolve().parents[2]
engine_file = project_root / "lessons" / "phase3" / "data" / "powertrain" / (
    "HMMWV_EngineSimpleMap_torque_high.json"
)

engine = veh.ReadEngineJSON(str(engine_file))
```

> [!important] 경로 규칙
> 이 프로젝트는 Windows/Linux/macOS 팀원이 함께 사용하므로 절대 경로를 코드에 하드코딩하지 않는다.
> `pathlib.Path` 또는 `os.path.join()`을 사용한다.

---

## 7. JSON을 코드로 복사/수정하는 예시

실험 자동화를 위해 원본 JSON을 읽고, 일부 값만 바꿔 새 파일로 저장할 수 있다.

```python
import json
from pathlib import Path

src = Path("chrono/data/vehicle/hmmwv/powertrain/HMMWV_EngineSimpleMap.json")
dst = Path("lessons/phase3/data/powertrain/HMMWV_EngineSimpleMap_torque_120.json")
dst.parent.mkdir(parents=True, exist_ok=True)

with src.open("r", encoding="utf-8") as f:
    engine_data = json.load(f)

scale = 1.2
engine_data["Name"] = "HMMWV EngineSimpleMap Torque 120%"
engine_data["Map Full Throttle"] = [
    [rpm, torque * scale]
    for rpm, torque in engine_data["Map Full Throttle"]
]

with dst.open("w", encoding="utf-8") as f:
    json.dump(engine_data, f, indent=2)
```

> [!warning] Chrono JSON 주석
> Chrono의 일부 JSON 예시는 C++ 스타일 주석을 포함할 수 있다.
> Python 표준 `json` 모듈은 주석이 있는 JSON을 읽지 못한다.
> 실험용 JSON은 주석을 제거한 표준 JSON으로 관리하는 것이 안전하다.

---

## 8. 실험 결과 해석 체크리스트

| 질문 | 확인할 컬럼 |
|---|---|
| throttle이 증가하면 engine torque가 증가하는가? | `throttle`, `engine_torque_Nm` |
| 변속 시점이 예상 RPM 근처인가? | `engine_rpm`, `gear` |
| gear ratio 변경이 가속도에 영향을 주는가? | `gear`, `speed`, `driveshaft_torque_Nm` |
| 토크 증가가 slip 증가로 이어지는가? | `wheel_omega_*`, `speed`, `estimated_slip_*` |
| shafts model에서 converter slip이 큰 구간은 언제인가? | `tc_slippage`, `speed`, `throttle` |
| 계산 속도는 충분한가? | `vehicle.GetRTF()` 또는 wall-clock time |

---

## 9. VSG/Irrlicht 시각화와 함께 쓰기

레슨 파일에서는 팀원 환경 호환성을 위해 VSG 우선, Irrlicht fallback 패턴을 사용한다.
Powertrain 실험 자체는 렌더러와 무관하지만, 결과 확인을 위해 시각화가 필요할 수 있다.

```python
try:
    import pychrono.vsg3d as chronovsg
    USE_VSG = True
except ImportError:
    USE_VSG = False
    import pychrono.irrlicht as chronoirr

if USE_VSG:
    vis = chronovsg.ChVisualSystemVSG()
    vis.SetCameraVertical(chrono.CameraVerticalDir_Z)
else:
    vis = chronoirr.ChVisualSystemIrrlicht()
```

> [!note] Vehicle은 Z-up
> Chrono::Vehicle 예제는 보통 Z-up이다.
> VSG camera vertical도 vehicle 실험에서는 Z-up으로 두는 것이 자연스럽다.

---

## 10. 참고 자료

- Project Chrono 공식 문서: Powertrain models  
  https://api.projectchrono.org/vehicle_powertrain.html

- Python 데모:
  - `chrono/src/demos/python/vehicle/demo_VEH_WheeledJSON.py`
  - `chrono/src/demos/python/vehicle/demo_VEH_HMMWV.py`

- 관련 문서:
  - [[../powertrain]]
  - [[../wheeled/4_driveline]]
  - [[../wheeled/6_simulation_loop]]
