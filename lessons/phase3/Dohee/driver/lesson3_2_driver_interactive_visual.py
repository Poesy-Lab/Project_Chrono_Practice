r"""
Phase 3 - Interactive Driver Visual Script

Project Chrono / Vehicle / Driver

Purpose
-------
Run an interactive HMMWV example with Irrlicht and log driver inputs to CSV.
This script should be executed directly as a Python file.

Run
---
conda activate chrono
cd "C:/Project_Chrono/Project_Chrono_Practice"
python lessons/phase3/Dohee/driver/lesson3_2_driver_interactive_visual.py

Controls
--------
W: throttle
S: braking
A/D: steering
J: driver input lock/unlock

Output
------
results/phase3/driver_interactive_visual/driver_interactive_visual_log.csv
"""

import math as m
from pathlib import Path

import pandas as pd

import pychrono as chrono
import pychrono.vehicle as veh
import pychrono.irrlicht as irr


# =============================================================================
# 1. Project path setting
# =============================================================================

def find_project_root(start=None):
    if start is None:
        start = Path.cwd()
    start = Path(start).resolve()

    for p in [start] + list(start.parents):
        if (p / ".git").exists() or (p / "docs").exists():
            return p

    return start


PROJECT_ROOT = find_project_root()
RESULT_DIR = PROJECT_ROOT / "results" / "phase3" / "driver_interactive_visual"
RESULT_DIR.mkdir(parents=True, exist_ok=True)

csv_path = RESULT_DIR / "driver_interactive_visual_log.csv"


# =============================================================================
# 2. Simulation parameters
# =============================================================================

veh.ChWorldFrame.SetYUP()

contact_method = chrono.ChContactMethod_NSC
tire_model = veh.TireModelType_TMEASY

step_size = 3e-3
tire_step_size = 1e-3
t_end = 30.0
terrain_friction = 0.9

checkpoint_interval = 50


# =============================================================================
# 3. Helper functions for logging
# =============================================================================

def get_chassis_body(hmmwv):
    """HMMWV wrapper?먯꽌 chassis body瑜??덉쟾?섍쾶 媛?몄삩??"""
    vehicle = hmmwv.GetVehicle()

    if hasattr(vehicle, "GetChassisBody"):
        return vehicle.GetChassisBody()

    if hasattr(vehicle, "GetChassis"):
        chassis = vehicle.GetChassis()
        if hasattr(chassis, "GetBody"):
            return chassis.GetBody()

    raise RuntimeError("Could not access chassis body.")


def safe_get_rpy_from_body(body):
    """李⑥껜 orientation??roll, pitch, yaw濡?蹂?섑븳?? ?ㅽ뙣?섎㈃ None?쇰줈 ?붾떎."""
    try:
        angles = body.GetRot().GetCardanAnglesXYZ()
        return float(angles.x), float(angles.y), float(angles.z)
    except Exception:
        return None, None, None


def get_vehicle_speed(hmmwv, body):
    """vehicle API?먯꽌 ?띾룄瑜??쎄퀬, ?ㅽ뙣?섎㈃ velocity norm?쇰줈 怨꾩궛?쒕떎."""
    try:
        return float(hmmwv.GetVehicle().GetSpeed())
    except Exception:
        vel = body.GetPosDt()
        return float((vel.x**2 + vel.y**2 + vel.z**2) ** 0.5)


def log_vehicle_state(hmmwv, driver_inputs):
    """
    ?꾩옱 timestep??李⑤웾 ?곹깭? driver input??dictionary濡???ν븳??

    ?????ぉ:
        time, position, velocity, speed, roll/pitch/yaw,
        steering, throttle, braking
    """
    body = get_chassis_body(hmmwv)
    time = float(hmmwv.GetSystem().GetChTime())

    pos = body.GetPos()
    vel = body.GetPosDt()
    roll, pitch, yaw = safe_get_rpy_from_body(body)
    speed = get_vehicle_speed(hmmwv, body)

    return {
        "case_name": "driver_interactive_visual",
        "time": time,

        "x": float(pos.x),
        "y": float(pos.y),
        "z": float(pos.z),

        "vx": float(vel.x),
        "vy": float(vel.y),
        "vz": float(vel.z),

        "speed": speed,
        "roll": roll,
        "pitch": pitch,
        "yaw": yaw,

        "steering": float(driver_inputs.m_steering),
        "throttle": float(driver_inputs.m_throttle),
        "braking": float(driver_inputs.m_braking),
    }


def flush_rows(rows):
    """
    硫붾え由ъ뿉 紐⑥씤 row?ㅼ쓣 CSV??append 諛⑹떇?쇰줈 ??ν븳??

    append 諛⑹떇???곕뒗 ?댁쑀:
        - interactive simulation 以?李쎌쓣 ?レ븘???곗씠???먯떎??以꾩씠湲??꾪빐
        - log_rows ?꾩껜瑜?留덉?留됱뿉 ??踰덈쭔 ??ν븯??諛⑹떇? ?꾪뿕??    """
    if not rows:
        return

    pd.DataFrame(rows).to_csv(
        csv_path,
        mode="a",
        header=not csv_path.exists(),
        index=False,
        encoding="utf-8-sig",
    )


# =============================================================================
# 4. Vehicle creation
# =============================================================================

initLoc = chrono.ChVector3d(0, 1, 10)
initYaw = 0.0

hmmwv = veh.HMMWV_Reduced()

hmmwv.SetContactMethod(contact_method)
hmmwv.SetChassisCollisionType(veh.CollisionType_NONE)
hmmwv.SetChassisFixed(False)
hmmwv.SetInitPosition(chrono.ChCoordsysd(initLoc, chrono.QuatFromAngleY(initYaw)))

hmmwv.SetEngineType(veh.EngineModelType_SIMPLE)
hmmwv.SetTransmissionType(veh.TransmissionModelType_AUTOMATIC_SIMPLE_MAP)
hmmwv.SetDriveType(veh.DrivelineTypeWV_AWD)
hmmwv.SetTireType(tire_model)
hmmwv.SetTireStepSize(tire_step_size)

hmmwv.Initialize()

# Visualization type setting
hmmwv.SetChassisVisualizationType(chrono.VisualizationType_PRIMITIVES)
hmmwv.SetSuspensionVisualizationType(chrono.VisualizationType_PRIMITIVES)
hmmwv.SetSteeringVisualizationType(chrono.VisualizationType_PRIMITIVES)
hmmwv.SetWheelVisualizationType(chrono.VisualizationType_MESH)
hmmwv.SetTireVisualizationType(chrono.VisualizationType_MESH)

hmmwv.GetSystem().SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)


# =============================================================================
# 5. Terrain creation
# =============================================================================

terrain = veh.RigidTerrain(hmmwv.GetSystem())

patch_mat = chrono.ChContactMaterialNSC()
patch_mat.SetFriction(terrain_friction)

patch = terrain.AddPatch(
    patch_mat,
    chrono.ChCoordsysd(chrono.VNULL, chrono.QuatFromAngleX(-m.pi / 2)),
    200.0,
    100.0,
)

try:
    patch.SetTexture(veh.GetVehicleDataFile("terrain/textures/tile4.jpg"), 200, 200)
except Exception:
    pass

patch.SetColor(chrono.ChColor(0.8, 0.8, 0.5))
terrain.Initialize()


# =============================================================================
# 6. Interactive driver creation
# =============================================================================

driver = veh.ChInteractiveDriver(hmmwv.GetVehicle())

driver.SetSteeringDelta(0.06)
driver.SetThrottleDelta(0.02)
driver.SetBrakingDelta(0.06)

driver.Initialize()


# =============================================================================
# 7. Irrlicht visualization
# =============================================================================

vis = veh.ChWheeledVehicleVisualSystemIrrlicht()

vis.SetCameraVertical(chrono.CameraVerticalDir_Y)
vis.SetWindowTitle("Phase3 - Driver Interactive Visual")
vis.SetWindowSize(1280, 900)
vis.SetChaseCamera(chrono.ChVector3d(0.0, 0.0, 0.75), 6.0, 0.5)

vis.Initialize()
vis.AddLogo(chrono.GetChronoDataFile("logo_chrono_alpha.png"))
vis.AddLightDirectional(-60, 300)
vis.AddSkyBox()

vis.AttachVehicle(hmmwv.GetVehicle())
vis.AttachDriver(driver)

# ?щ엺??議곗옉?섎뒗 ?ㅼ떆媛?simulation???곹빀?섎룄濡?realtime mode瑜?耳좊떎.
hmmwv.GetVehicle().EnableRealtime(True)


# =============================================================================
# 8. Simulation loop with streaming CSV logging
# =============================================================================

if csv_path.exists():
    csv_path.unlink()

log_rows = []

print("Simulation started")
print("Click Irrlicht window, then use W/A/S/D.")
print("W: throttle, S: braking, A/D: steering, J: lock/unlock")
print("CSV:", csv_path)

try:
    while vis.Run():
        time = hmmwv.GetSystem().GetChTime()

        if time >= t_end:
            break

        # Render scene
        vis.BeginScene()
        vis.Render()
        vis.EndScene()

        # Read driver inputs from keyboard
        driver_inputs = driver.GetInputs()

        # Log current state
        log_rows.append(log_vehicle_state(hmmwv, driver_inputs))

        # Periodic autosave
        if len(log_rows) >= checkpoint_interval:
            flush_rows(log_rows)
            log_rows = []
            print(f"Autosaved at t = {time:.2f} s")

        # Synchronize modules
        driver.Synchronize(time)
        terrain.Synchronize(time)
        hmmwv.Synchronize(time, driver_inputs, terrain)
        vis.Synchronize(time, driver_inputs)

        # Advance modules
        driver.Advance(step_size)
        terrain.Advance(step_size)
        hmmwv.Advance(step_size)
        vis.Advance(step_size)

except KeyboardInterrupt:
    print("Interrupted by user.")

finally:
    # Save remaining rows
    flush_rows(log_rows)
    print("Final CSV saved:", csv_path)

print("Simulation finished")
