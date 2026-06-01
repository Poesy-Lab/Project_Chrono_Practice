# M113 Single-Pin Tracked Vehicle 실행 예제

## 1. 예제 목적

이 예제의 목적은 다음과 같다.
* Tracked vehicle 작동 확인: M113 tracked vehicle이 실제로 생성되고 주행하는지 확인 
* Single-pin track shoe 확인: 가장 단순한 segmented track인 single-pin track shoe 모델 사용
* 결과값 저장 확인: 시간, 위치, 속도, 입력값, contact 개수 등을 CSV로 저장

이 예제는 복잡한 장애물 주행이나 제어 알고리즘 검증용이 아니라, **tracked vehicle simulation의 최소 실행 검증용**이다.

---

## 2. 사용하는 Chrono 모델

이 예제는 Chrono::Vehicle에서 제공하는 `M113` 모델을 사용한다.

설정은 다음과 같다.

|항목|설정|
|---|---|
| Vehicle model | `veh.M113()` |
| Track shoe type | `veh.TrackShoeType_SINGLE_PIN` |
| Contact method | `chrono.ChContactMethod_SMC` |
| Terrain | Flat rigid terrain |
| Driver | Scripted data driver |
| Output | CSV file |

> M113 vehicle  
> → Single-pin track shoes  
> → Sprocket으로부터 구동력 전달  
> → Track shoe와 rigid terrain 접촉  
> → 차량 전진  
> → 상태값 CSV 저장

---

## 3. 왜 Single-pin 모델을 사용하는가?


Chrono의 tracked vehicle에는 single-pin, double-pin, band-bushing, band-ANCF 계열이 있다.

그중 이 예제에서는 `single-pin`을 사용한다.

| 이유 | 설명 |
|---|---|
| 구조가 가장 단순함 | 하나의 shoe body가 이웃 shoe와 revolute joint로 연결됨 |
| 계산 비용이 상대적으로 낮음 | double-pin이나 ANCF band보다 body/joint 수가 적음 |
| 디버깅이 쉬움 | tracked vehicle이 정상 작동하는지 확인하기 좋음 |
| M113 공식 예제와 일치 | Chrono 공식 M113 데모도 single-pin M113 주행 예제를 제공 |

---

## 4. 실행 방법

폴더에 다음 파일이 있어야 한다.

| 파일 | 역할 |
|---|---|
| `m113_singlepin_acceleration.py` | 실행할 Python 코드 |
| `README_M113_singlepin_example.md` | 설명 문서 |

터미널 또는 Anaconda Prompt에서 해당 폴더로 이동한 뒤 실행한다.

일반 실행:

    python m113_singlepin_acceleration.py

시각화 없이 실행:

    python m113_singlepin_acceleration.py --no-vis

시뮬레이션 시간을 15초로 늘려 실행:

    python m113_singlepin_acceleration.py --time 15

---

## 5. 실행 후 생성되는 파일

실행하면 다음 폴더가 생성된다.

    output_m113_singlepin

그 안에 다음 파일들이 저장된다.

| 파일 | 설명 |
|---|---|
| `m113_driver_acceleration.txt` | 차량 입력값 파일 |
| `m113_state.csv` | 시뮬레이션 결과값 |

---

## 6. Driver 입력 파일 설명

코드는 자동으로 `m113_driver_acceleration.txt` 파일을 만든다.

이 파일은 시간에 따른 driver input을 정의한다.

| 열 | 의미 |
|---|---|
| 1열 | time [s] |
| 2열 | steering [-1~1] |
| 3열 | throttle [0~1] |
| 4열 | braking [0~1] |
| 5열 | clutch [0~1] |

이번 예제에서는 steering은 계속 0으로 두고, throttle만 증가시켜 차량이 직진 가속하도록 했다.


입력 흐름은 다음과 같다.

> 0.0초 ~ 0.5초: 정지 상태 유지  
> 0.5초 ~ 2.0초: throttle 0.8까지 증가  
> 2.0초 ~ 10.0초: throttle 0.8 유지  
> 10.0초 ~ 12.0초: throttle 해제 및 brake 적용

---

## 7. CSV 결과 파일 설명

`m113_state.csv`에는 다음 값들이 저장된다.

| 열 이름 | 의미 |
|---|---|
| `time_s` | 시뮬레이션 시간 |
| `x_m`, `y_m`, `z_m` | 차량 위치 |
| `speed_mps` | 차량 전진 방향 속도 |
| `roll_rad` | 차량 roll angle |
| `pitch_rad` | 차량 pitch angle |
| `throttle` | driver throttle input |
| `steering` | driver steering input |
| `braking` | driver braking input |
| `num_contacts` | 현재 contact 개수 |
| `rtf` | real-time factor |

  

가장 먼저 확인할 값은 다음 두 가지이다.

  

| 확인값 | 정상적인 경우 |
|---|---|
| `x_m` | 시간이 지날수록 증가 |
| `speed_mps` | throttle이 들어간 뒤 증가 |

  

즉, CSV에서 `x_m`과 `speed_mps`가 증가하면 M113 tracked vehicle이 정상적으로 굴러가고 있다고 볼 수 있다.

  

---
## 8. 코드 주요 구조


코드는 크게 다음 순서로 진행된다.


> 1. Driver input 파일 생성  
> 2. M113 차량 생성  
> 3. Single-pin track shoe type 지정  
> 4. Rigid terrain 생성  
> 5. Data driver 생성  
> 6. Irrlicht 시각화 생성  
> 7. Simulation loop 실행  
> 8. 차량 상태 CSV 저장


---

## 9. 핵심 코드 설명

### 9.1 M113 생성

`veh.M113()`는 Chrono에서 제공하는 M113 tracked vehicle wrapper이다.

이후 다음 설정으로 single-pin track shoe를 선택한다.

    m113.SetTrackShoeType(veh.TrackShoeType_SINGLE_PIN)

이 한 줄이 이번 예제에서 가장 중요한 부분이다.

---

### 9.2 Contact method

이 예제에서는 SMC contact를 사용한다.

    m113.SetContactMethod(chrono.ChContactMethod_SMC)

SMC는 compliant contact 방식으로, 접촉을 스프링-댐퍼처럼 처리한다.  

tracked vehicle은 track shoe와 지면, sprocket, idler, road wheel 사이의 접촉이 많기 때문에 contact 설정이 중요하다.

---

### 9.3 Data driver

키보드 입력을 사용하면 팀원마다 실행 결과가 달라질 수 있다.  

그래서 이 예제에서는 `ChDataDriver`를 사용한다.

    driver = veh.ChDataDriver(m113.GetVehicle(), str(driver_file))

이 방식은 미리 정의된 시간-입력 데이터를 따라가므로, 같은 조건에서 반복 실행하기 좋다.

---

## 10. 정상 실행 확인 기준

정상적으로 실행되면 다음을 확인할 수 있다.

| 확인 항목 | 정상 결과 |
|---|---|
| 3D 창 | M113 차량이 평지에서 앞으로 움직임 |
| 터미널 | vehicle mass, track shoe 개수 출력 |
| CSV 파일 | `m113_state.csv` 생성 |
| 위치 | `x_m` 증가 |
| 속도 | `speed_mps` 증가 후 brake에서 감소 가능 |
| contact | `num_contacts`가 0이 아닌 값으로 유지 |

---


## 11. 문제가 생겼을 때

### 11.1 `pychrono.irrlicht` import error

Irrlicht visualization이 설치되지 않았거나 빌드에 포함되지 않은 경우이다.

해결:

    python m113_singlepin_acceleration.py --no-vis

이 경우 3D 창은 뜨지 않지만, CSV 결과는 저장된다.

---

### 11.2 `vehicle data file` 관련 오류
 

Chrono vehicle data path가 제대로 잡히지 않은 경우일 수 있다.


확인할 것:

| 항목 | 설명 |
|---|---|
| PyChrono 설치 | `import pychrono`가 되는지 확인 |
| vehicle module | `import pychrono.vehicle as veh`가 되는지 확인 |
| data 폴더 | Chrono data/vehicle 폴더가 설치되어 있는지 확인 |

---

### 11.3 너무 느린 경우

tracked vehicle은 접촉 수가 많아서 simulation이 느릴 수 있다.

우선 다음 방식으로 실행한다.

    python m113_singlepin_acceleration.py --no-vis

또는 simulation time을 줄인다.

    python m113_singlepin_acceleration.py --time 5

---

## 12. 이후 확장 아이디어

이 예제를 성공적으로 실행한 뒤에는 다음 방향으로 확장할 수 있다.

| 확장 방향 | 설명 |
|---|---|
| 작은 턱 추가 | rigid box obstacle을 추가하여 track이 장애물을 넘는지 확인 |
| driver input 변경 | throttle, brake, steering profile 수정 |
| double-pin으로 변경 | `TrackShoeType_DOUBLE_PIN`으로 바꾸어 비교 |
| CSV 항목 추가 | sprocket angular speed, idler 위치, track tension 등 추가 |
| terrain 변경 | rigid terrain에서 SCM deformable terrain으로 변경 |

---

## 13. 한 줄 요약

이 예제는 Chrono::Vehicle의 M113 모델을 사용하여 **single-pin tracked vehicle이 평지에서 정지 상태로부터 가속하는 과정**을 실행하고, 차량 위치와 속도 등의 결과를 CSV로 저장하는 최소 검증용 예제이다.

이 코드를 실행하여 다음을 확인하면 된다.

> PyChrono 실행 가능  
> → M113 tracked vehicle 생성 가능  
> → single-pin track shoe 차량 주행 가능  
> → 결과 CSV 저장 가능


## 14. 코드(m113_singlepin_acceleration.py)

```# =============================================================================

# Minimal Project Chrono / PyChrono M113 Single-Pin Tracked Vehicle Example

#

# Purpose:

#   1. Verify that PyChrono + Chrono::Vehicle works on each team member's PC.

#   2. Run an M113 tracked vehicle with SINGLE_PIN track shoes.

#   3. Start from rest, accelerate using a scripted driver input, and save results.

#

# Output:

#   output_m113_singlepin/m113_state.csv

#   output_m113_singlepin/m113_driver_acceleration.txt

#

# Run:

#   python m113_singlepin_acceleration.py

#   python m113_singlepin_acceleration.py --no-vis

#   python m113_singlepin_acceleration.py --time 15

#

# Notes:

#   This script is based on the official Chrono M113 Python demo structure,

#   but replaces the keyboard driver with a deterministic data driver.

# =============================================================================

  

import argparse

import csv

import math

import os

from pathlib import Path

  

import pychrono as chrono

import pychrono.vehicle as veh

  

# Irrlicht is used only when visualization is enabled.

# If your PyChrono build does not include Irrlicht, run with --no-vis.

try:

    import pychrono.irrlicht as irr

    HAS_IRRLICHT = True

except Exception:

    HAS_IRRLICHT = False

  
  

def write_driver_file(filename: Path) -> None:

    """Create a simple scripted driver input file.

  

    Columns:

        time [s], steering [-1~1], throttle [0~1], braking [0~1], clutch [0~1]

  

    This file makes the vehicle:

        0.0~0.5 s: stay idle

        0.5~2.0 s: ramp throttle to 0.8

        2.0~10.0 s: keep throttle 0.8

        10.0~12.0 s: release throttle and brake

    """

    filename.parent.mkdir(parents=True, exist_ok=True)

  

    rows = [

        [0.0,  0.0, 0.0, 0.0, 0.0],

        [0.5,  0.0, 0.0, 0.0, 0.0],

        [2.0,  0.0, 0.8, 0.0, 0.0],

        [10.0, 0.0, 0.8, 0.0, 0.0],

        [12.0, 0.0, 0.0, 0.5, 0.0],

    ]

  

    with open(filename, "w", encoding="utf-8") as f:

        for row in rows:

            f.write(" ".join(f"{value:.6g}" for value in row) + "\n")

  
  

def create_m113(init_loc: chrono.ChVector3d, init_rot: chrono.ChQuaterniond):

    """Create and initialize the M113 single-pin tracked vehicle."""

    m113 = veh.M113()

  

    # SMC contact is generally convenient for compliant contact simulations.

    m113.SetContactMethod(chrono.ChContactMethod_SMC)

  

    # This is the key choice for this example:

    # use segmented single-pin track shoes.

    m113.SetTrackShoeType(veh.TrackShoeType_SINGLE_PIN)

  

    # Basic drivetrain / powertrain choices.

    m113.SetDrivelineType(veh.DrivelineTypeTV_BDS)

    m113.SetEngineType(veh.EngineModelType_SHAFTS)

    m113.SetTransmissionType(veh.TransmissionModelType_AUTOMATIC_SHAFTS)

    m113.SetBrakeType(veh.BrakeType_SIMPLE)

  

    # Initial condition.

    m113.SetInitPosition(chrono.ChCoordsysd(init_loc, init_rot))

    m113.Initialize()

  

    # Visualization types.

    # Mesh visualization is nicer but can be heavier.

    m113.SetChassisVisualizationType(chrono.VisualizationType_PRIMITIVES)

    m113.SetSprocketVisualizationType(chrono.VisualizationType_MESH)

    m113.SetIdlerVisualizationType(chrono.VisualizationType_MESH)

    m113.SetIdlerWheelVisualizationType(chrono.VisualizationType_MESH)

    m113.SetSuspensionVisualizationType(chrono.VisualizationType_MESH)

    m113.SetRoadWheelVisualizationType(chrono.VisualizationType_MESH)

    m113.SetTrackShoeVisualizationType(chrono.VisualizationType_MESH)

  

    # Collision system.

    m113.GetSystem().SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)

  

    return m113

  
  

def create_rigid_terrain(system, length: float = 100.0, width: float = 30.0):

    """Create a flat rigid terrain patch."""

    terrain = veh.RigidTerrain(system)

  

    contact_method = system.GetContactMethod()

  

    if contact_method == chrono.ChContactMethod_NSC:

        patch_mat = chrono.ChContactMaterialNSC()

        patch_mat.SetFriction(0.9)

        patch_mat.SetRestitution(0.01)

    else:

        patch_mat = chrono.ChContactMaterialSMC()

        patch_mat.SetFriction(0.9)

        patch_mat.SetRestitution(0.01)

        patch_mat.SetYoungModulus(2.0e7)

  

    patch = terrain.AddPatch(patch_mat, chrono.CSYSNORM, length, width)

    patch.SetColor(chrono.ChColor(0.5, 0.8, 0.5))

  

    try:

        patch.SetTexture(veh.GetVehicleDataFile("terrain/textures/tile4.jpg"), 80, 20)

    except Exception:

        pass

  

    terrain.Initialize()

    return terrain

  
  

def create_visual_system(m113, driver, window_title: str):

    """Create the Irrlicht visualization system."""

    if not HAS_IRRLICHT:

        raise RuntimeError("pychrono.irrlicht is not available in this PyChrono installation.")

  

    vis = veh.ChTrackedVehicleVisualSystemIrrlicht()

    vis.SetWindowTitle(window_title)

    vis.SetWindowSize(1280, 800)

    vis.SetChaseCamera(chrono.ChVector3d(0.0, 0.0, 0.0), 7.0, 0.5)

    vis.Initialize()

  

    try:

        vis.AddLogo(chrono.GetChronoDataFile("logo_chrono_alpha.png"))

        vis.AddLightDirectional()

        vis.AddSkyBox()

    except Exception:

        pass

  

    vis.AttachVehicle(m113.GetVehicle())

    vis.AttachDriver(driver)

    return vis

  
  

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--no-vis", action="store_true", help="Run without Irrlicht visualization.")

    parser.add_argument("--time", type=float, default=12.0, help="Simulation end time [s].")

    parser.add_argument("--step", type=float, default=5e-4, help="Simulation step size [s].")

    parser.add_argument("--output-step", type=float, default=0.05, help="CSV output interval [s].")

    args = parser.parse_args()

  

    output_dir = Path("output_m113_singlepin")

    output_dir.mkdir(exist_ok=True)

  

    driver_file = output_dir / "m113_driver_acceleration.txt"

    csv_file = output_dir / "m113_state.csv"

    write_driver_file(driver_file)

  

    # Initial vehicle pose.

    # Z is set above the ground so the track settles onto the terrain at the start.

    init_loc = chrono.ChVector3d(0.0, 0.0, 1.1)

    init_rot = chrono.ChQuaterniond(1.0, 0.0, 0.0, 0.0)

  

    m113 = create_m113(init_loc, init_rot)

    terrain = create_rigid_terrain(m113.GetSystem())

  

    # Scripted driver input.

    # This makes the run reproducible across different computers.

    driver = veh.ChDataDriver(m113.GetVehicle(), str(driver_file))

    driver.Initialize()

  

    use_vis = (not args.no_vis) and HAS_IRRLICHT

    vis = None

    render_step_size = 1.0 / 60.0

    render_steps = max(1, math.ceil(render_step_size / args.step))

  

    if use_vis:

        vis = create_visual_system(m113, driver, "M113 Single-Pin Acceleration Example")

    elif not args.no_vis and not HAS_IRRLICHT:

        print("[Warning] Irrlicht is not available. Running without visualization.")

  

    # Solver setting.

    m113.GetSystem().SetSolverType(chrono.ChSolver.Type_BARZILAIBORWEIN)

  

    vehicle = m113.GetVehicle()

    system = m113.GetSystem()

  

    print("M113 single-pin tracked vehicle example")

    print("--------------------------------------")

    print(f"Chrono time step      : {args.step}")

    print(f"Simulation end time   : {args.time}")

    print(f"Output CSV            : {csv_file}")

    print(f"Driver file           : {driver_file}")

    print(f"Vehicle mass [kg]     : {vehicle.GetMass():.3f}")

    print(f"Left track shoes      : {vehicle.GetNumTrackShoes(veh.LEFT)}")

    print(f"Right track shoes     : {vehicle.GetNumTrackShoes(veh.RIGHT)}")

    print("--------------------------------------")

  

    next_output_time = 0.0

    step_number = 0

  

    with open(csv_file, "w", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)

        writer.writerow([

            "time_s",

            "x_m", "y_m", "z_m",

            "speed_mps",

            "roll_rad", "pitch_rad",

            "throttle", "steering", "braking",

            "num_contacts",

            "rtf"

        ])

  

        while True:

            time = system.GetChTime()

  

            if time >= args.time:

                break

  

            if vis is not None:

                if not vis.Run():

                    break

  

                if step_number % render_steps == 0:

                    vis.BeginScene()

                    vis.Render()

                    vis.EndScene()

  

            # Driver inputs at current time.

            driver_inputs = driver.GetInputs()

  

            # Output vehicle state at fixed interval.

            if time >= next_output_time:

                pos = vehicle.GetPos()

                writer.writerow([

                    f"{time:.6f}",

                    f"{pos.x:.6f}", f"{pos.y:.6f}", f"{pos.z:.6f}",

                    f"{vehicle.GetSpeed():.6f}",

                    f"{vehicle.GetRoll():.6f}",

                    f"{vehicle.GetPitch():.6f}",

                    f"{driver_inputs.m_throttle:.6f}",

                    f"{driver_inputs.m_steering:.6f}",

                    f"{driver_inputs.m_braking:.6f}",

                    system.GetNumContacts(),

                    f"{vehicle.GetRTF():.6f}",

                ])

                next_output_time += args.output_step

  

            # Synchronize all modules.

            driver.Synchronize(time)

            terrain.Synchronize(time)

            m113.Synchronize(time, driver_inputs)

            if vis is not None:

                vis.Synchronize(time, driver_inputs)

  

            # Advance all modules.

            driver.Advance(args.step)

            terrain.Advance(args.step)

            m113.Advance(args.step)

            if vis is not None:

                vis.Advance(args.step)

  

            step_number += 1

  

    print("Simulation finished.")

    print(f"Saved CSV: {csv_file}")

  
  

if __name__ == "__main__":

    main()
```