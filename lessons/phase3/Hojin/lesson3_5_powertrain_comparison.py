# %%
# 학습 목표:
# - Chrono::Vehicle에서 Powertrain = Engine + Transmission 구조를 이해한다.
# - HMMWV 차량에서 powertrain model 조합(SimpleMap, Shafts, SimpleCVT)에 따른 주행 응답을 비교한다.
# - engine RPM, engine torque, gear, driveshaft torque, wheel speed를 CSV와 그래프로 저장한다.
#
# 실행 방법:
# conda activate chrono
# cd /Users/poesy/Documents/Praxis/Project_Chrono_Practice
# source setup_chrono_env.sh
# python lessons/phase3/Hojin/lesson3_5_powertrain_comparison.py
#
# Hojin 폴더에서 바로 실행할 때:
# conda activate chrono
# source ../../../setup_chrono_env.sh
# python lesson3_5_powertrain_comparison.py
#
# 주의:
# pip install pychrono 로 설치되는 패키지는 Project Chrono가 아니므로 사용하지 않는다.

# %% [markdown]
# # Phase 3 - Powertrain Comparison
#
# > Project Chrono / Vehicle / Powertrain
# > 목표: HMMWV 차량에서 engine/transmission model 조합이 주행 응답에 미치는 영향을 비교한다.
#
# 이번 예제는 같은 차량, 같은 지형, 같은 driveline, 같은 throttle 조건에서 **powertrain model**만 바꾸어 실험한다.
#
# 비교 후보:
#
# ```text
# SimpleMap: EngineSimpleMap + AutomaticTransmissionSimpleMap
# Shafts:    EngineShafts + AutomaticTransmissionShafts
# SimpleCVT: EngineSimpleMap + AutomaticTransmissionSimpleCVT
# ```
#
# 핵심 흐름:
#
# ```text
# Driver throttle input
#     -> Engine torque
#     -> Transmission torque/speed conversion
#     -> Driveline torque distribution
#     -> Wheel angular speed
#     -> Tire-ground force
#     -> Vehicle speed
# ```

# %% [markdown]
# ## 1. Import

# %%
import matplotlib.pyplot as plt
import csv
import math as m
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

try:
    import pychrono as chrono
    import pychrono.vehicle as veh
except (ImportError, ModuleNotFoundError) as exc:
    raise SystemExit(
        "\n"
        "ERROR: Project Chrono의 PyChrono 모듈을 찾지 못했습니다.\n"
        "\n"
        "이 프로젝트에서는 PyPI의 `pychrono` 패키지를 사용하지 않습니다.\n"
        "이미 `pip install pychrono`를 실행했다면 먼저 지워주세요:\n"
        "\n"
        "    pip uninstall -y pychrono\n"
        "\n"
        "그 다음 Hojin 폴더 기준으로 아래처럼 실행하세요:\n"
        "\n"
        "    conda activate chrono\n"
        "    source ../../../setup_chrono_env.sh\n"
        "    python lesson3_5_powertrain_comparison.py\n"
        "\n"
        "또는 프로젝트 루트 기준으로:\n"
        "\n"
        "    conda activate chrono\n"
        "    source setup_chrono_env.sh\n"
        "    python lessons/phase3/Hojin/lesson3_5_powertrain_comparison.py\n"
    ) from exc

print("Chrono import success")

# %% [markdown]
# ## 2. Path Setting

# %%


def find_project_root(start=None):
    if start is None:
        try:
            start = Path(__file__).resolve()
        except NameError:
            start = Path.cwd()

    start = Path(start).resolve()
    if start.is_file():
        start = start.parent

    for p in [start] + list(start.parents):
        if (p / ".git").exists() or (p / "docs").exists():
            return p

    return start


PROJECT_ROOT = find_project_root()
LESSON_DIR = PROJECT_ROOT / "lessons" / "phase3" / "Hojin"
RESULT_DIR = LESSON_DIR / "results" / "powertrain_comparison"
FIGURE_DIR = RESULT_DIR / "figures"

RESULT_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

print("PROJECT_ROOT:", PROJECT_ROOT)
print("LESSON_DIR:", LESSON_DIR)
print("RESULT_DIR:", RESULT_DIR)
print("FIGURE_DIR:", FIGURE_DIR)

# %% [markdown]
# ## 3. Simulation Parameters

# %%
# Dohee phase3 examples use Y-up, so this lesson follows the same convention.
veh.ChWorldFrame.SetYUP()

# Contact / tire / driveline settings
contact_method = chrono.ChContactMethod_NSC
tire_model = veh.TireModelType_TMEASY
drive_type = veh.DrivelineTypeWV_AWD

# Simulation setting
step_size = 5e-3
tire_step_size = 1e-3
t_end = 8.0

# Terrain
terrain_friction = 0.9

# Fixed driver input
fixed_steering = 0.0
fixed_throttle = 0.45
fixed_braking = 0.0

# HMMWV TMeasy unloaded radius is about 0.4699 m.
tire_radius = 0.4699

print("Simulation parameters ready")

# %% [markdown]
# ## 4. Available Powertrain Cases

# %%


def get_enum(enum_name):
    return getattr(veh, enum_name, None)


def get_available_powertrain_cases():
    """Return powertrain cases supported by the current PyChrono build."""

    candidates = [
        {
            "case_name": "powertrain_simple_map",
            "label": "SimpleMap",
            "engine_enum": "EngineModelType_SIMPLE_MAP",
            "transmission_enum": "TransmissionModelType_AUTOMATIC_SIMPLE_MAP",
        },
        {
            "case_name": "powertrain_shafts",
            "label": "Shafts",
            "engine_enum": "EngineModelType_SHAFTS",
            "transmission_enum": "TransmissionModelType_AUTOMATIC_SHAFTS",
        },
        {
            "case_name": "powertrain_simple_cvt",
            "label": "SimpleCVT",
            "engine_enum": "EngineModelType_SIMPLE_MAP",
            "transmission_enum": "TransmissionModelType_AUTOMATIC_SIMPLE_CVT",
        },
        {
            "case_name": "powertrain_simple_engine",
            "label": "SimpleEngine",
            "engine_enum": "EngineModelType_SIMPLE",
            "transmission_enum": "TransmissionModelType_AUTOMATIC_SIMPLE_MAP",
        },
    ]

    cases = []

    for candidate in candidates:
        engine = get_enum(candidate["engine_enum"])
        transmission = get_enum(candidate["transmission_enum"])

        if engine is None or transmission is None:
            print("Skip unsupported case:", candidate["label"])
            continue

        case = dict(candidate)
        case["engine"] = engine
        case["transmission"] = transmission
        cases.append(case)

    return cases


powertrain_cases = get_available_powertrain_cases()

print("Available powertrain cases:")
for case in powertrain_cases:
    print(
        case["label"],
        "->",
        case["engine_enum"],
        "+",
        case["transmission_enum"],
    )

if len(powertrain_cases) == 0:
    raise RuntimeError(
        "No powertrain cases found. Check pychrono.vehicle enum names.")

# %% [markdown]
# ## 5. Helper Functions

# %%


def safe_float(value, default=float("nan")):
    try:
        return float(value)
    except Exception:
        return default


def safe_call(default, func):
    try:
        return func()
    except Exception:
        return default


def get_chassis_body(hmmwv):
    vehicle = hmmwv.GetVehicle()

    if hasattr(vehicle, "GetChassisBody"):
        return vehicle.GetChassisBody()

    if hasattr(vehicle, "GetChassis"):
        chassis = vehicle.GetChassis()
        if hasattr(chassis, "GetBody"):
            return chassis.GetBody()

    raise RuntimeError(
        "Could not access chassis body. Check PyChrono vehicle API.")


def safe_get_rpy_from_body(body):
    rot = body.GetRot()

    try:
        angles = rot.GetCardanAnglesXYZ()
        return safe_float(angles.x), safe_float(angles.y), safe_float(angles.z)
    except Exception:
        return float("nan"), float("nan"), float("nan")


def get_vehicle_speed(hmmwv, body):
    try:
        return safe_float(hmmwv.GetVehicle().GetSpeed())
    except Exception:
        vel = body.GetPosDt()
        return safe_float((vel.x**2 + vel.y**2 + vel.z**2) ** 0.5)


def get_powertrain_state(vehicle):
    row = {}

    engine = safe_call(None, vehicle.GetEngine)
    transmission = safe_call(None, vehicle.GetTransmission)

    if engine is not None:
        engine_speed = safe_float(
            safe_call(float("nan"), engine.GetMotorSpeed))
        row["engine_speed_rad_s"] = engine_speed
        row["engine_rpm"] = engine_speed * 60.0 / (2.0 * m.pi)
        row["engine_torque_Nm"] = safe_float(
            safe_call(float("nan"), engine.GetOutputMotorshaftTorque)
        )
        row["engine_reaction_torque_Nm"] = safe_float(
            safe_call(float("nan"), engine.GetChassisReactionTorque)
        )

    if transmission is not None:
        row["gear"] = safe_float(
            safe_call(float("nan"), transmission.GetCurrentGear))
        row["driveshaft_torque_Nm"] = safe_float(
            safe_call(float("nan"), transmission.GetOutputDriveshaftTorque)
        )
        row["motorshaft_speed_rad_s"] = safe_float(
            safe_call(float("nan"), transmission.GetOutputMotorshaftSpeed)
        )
        row["transmission_reaction_torque_Nm"] = safe_float(
            safe_call(float("nan"), transmission.GetChassisReactionTorque)
        )

        is_automatic = bool(safe_call(False, transmission.IsAutomatic))
        row["is_automatic"] = int(is_automatic)

        if is_automatic:
            auto = safe_call(None, transmission.asAutomatic)
            if auto is not None:
                row["has_torque_converter"] = int(
                    bool(safe_call(False, auto.HasTorqueConverter))
                )
                row["tc_slippage"] = safe_float(
                    safe_call(float("nan"), auto.GetTorqueConverterSlippage)
                )
                row["tc_input_torque_Nm"] = safe_float(
                    safe_call(float("nan"), auto.GetTorqueConverterInputTorque)
                )
                row["tc_output_torque_Nm"] = safe_float(
                    safe_call(float("nan"),
                              auto.GetTorqueConverterOutputTorque)
                )
                row["tc_output_speed_rad_s"] = safe_float(
                    safe_call(float("nan"), auto.GetTorqueConverterOutputSpeed)
                )

    return row


def get_wheel_state(vehicle, speed):
    omega_fl = safe_float(
        safe_call(float("nan"), lambda: vehicle.GetSpindleOmega(0, veh.LEFT)))
    omega_fr = safe_float(
        safe_call(float("nan"), lambda: vehicle.GetSpindleOmega(0, veh.RIGHT)))
    omega_rl = safe_float(
        safe_call(float("nan"), lambda: vehicle.GetSpindleOmega(1, veh.LEFT)))
    omega_rr = safe_float(
        safe_call(float("nan"), lambda: vehicle.GetSpindleOmega(1, veh.RIGHT)))

    return {
        "omega_FL_rad_s": omega_fl,
        "omega_FR_rad_s": omega_fr,
        "omega_RL_rad_s": omega_rl,
        "omega_RR_rad_s": omega_rr,
        "slip_FL_est": estimate_slip(speed, omega_fl),
        "slip_FR_est": estimate_slip(speed, omega_fr),
        "slip_RL_est": estimate_slip(speed, omega_rl),
        "slip_RR_est": estimate_slip(speed, omega_rr),
    }


def estimate_slip(vehicle_speed, wheel_omega, eps=0.1):
    if not m.isfinite(vehicle_speed) or not m.isfinite(wheel_omega):
        return float("nan")

    return (tire_radius * wheel_omega - vehicle_speed) / max(abs(vehicle_speed), eps)


def log_vehicle_state(hmmwv, driver_inputs, case):
    system = hmmwv.GetSystem()
    vehicle = hmmwv.GetVehicle()
    body = get_chassis_body(hmmwv)

    time = safe_float(system.GetChTime())
    pos = body.GetPos()
    vel = body.GetPosDt()
    roll, pitch, yaw = safe_get_rpy_from_body(body)
    speed = get_vehicle_speed(hmmwv, body)

    row = {
        "case_name": case["case_name"],
        "powertrain": case["label"],
        "engine_enum": case["engine_enum"],
        "transmission_enum": case["transmission_enum"],
        "time": time,
        # Y-up coordinate: X forward, Y vertical, Z lateral
        "x": safe_float(pos.x),
        "y": safe_float(pos.y),
        "z": safe_float(pos.z),
        "vx": safe_float(vel.x),
        "vy": safe_float(vel.y),
        "vz": safe_float(vel.z),
        "speed": speed,
        "roll": roll,
        "pitch": pitch,
        "yaw": yaw,
        "steering": safe_float(driver_inputs.m_steering),
        "throttle": safe_float(driver_inputs.m_throttle),
        "braking": safe_float(driver_inputs.m_braking),
    }

    row.update(get_powertrain_state(vehicle))
    row.update(get_wheel_state(vehicle, speed))

    return row


def add_derived_metrics(rows):
    if len(rows) == 0:
        return rows

    rows[0]["acceleration"] = 0.0

    for i in range(1, len(rows)):
        dt = rows[i]["time"] - rows[i - 1]["time"]
        if dt > 0:
            rows[i]["acceleration"] = (
                rows[i]["speed"] - rows[i - 1]["speed"]) / dt
        else:
            rows[i]["acceleration"] = float("nan")

    return rows


print("Helper functions ready")

# %% [markdown]
# ## 6. Simulation Function

# %%


def run_powertrain_case(case):
    """Run one powertrain comparison case and return a list of log rows."""

    init_loc = chrono.ChVector3d(0, 1.2, 0)
    init_yaw = 0.0

    hmmwv = veh.HMMWV_Reduced()

    hmmwv.SetContactMethod(contact_method)
    hmmwv.SetChassisCollisionType(veh.CollisionType_NONE)
    hmmwv.SetChassisFixed(False)
    hmmwv.SetInitPosition(chrono.ChCoordsysd(
        init_loc, chrono.QuatFromAngleY(init_yaw)))

    hmmwv.SetEngineType(case["engine"])
    hmmwv.SetTransmissionType(case["transmission"])
    hmmwv.SetDriveType(drive_type)
    hmmwv.SetTireType(tire_model)
    hmmwv.SetTireStepSize(tire_step_size)

    hmmwv.Initialize()
    hmmwv.GetSystem().SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)

    terrain = veh.RigidTerrain(hmmwv.GetSystem())

    patch_mat = chrono.ChContactMaterialNSC()
    patch_mat.SetFriction(terrain_friction)
    patch_mat.SetRestitution(0.01)

    terrain.AddPatch(
        patch_mat,
        chrono.ChCoordsysd(
            chrono.ChVector3d(0, 0, 0),
            chrono.QuatFromAngleX(-m.pi / 2),
        ),
        200.0,
        60.0,
    )
    terrain.Initialize()

    driver_inputs = veh.DriverInputs()
    driver_inputs.m_steering = fixed_steering
    driver_inputs.m_throttle = fixed_throttle
    driver_inputs.m_braking = fixed_braking

    rows = []

    while hmmwv.GetSystem().GetChTime() < t_end:
        time = hmmwv.GetSystem().GetChTime()

        terrain.Synchronize(time)
        hmmwv.Synchronize(time, driver_inputs, terrain)

        rows.append(log_vehicle_state(hmmwv, driver_inputs, case))

        terrain.Advance(step_size)
        hmmwv.Advance(step_size)

    return add_derived_metrics(rows)


print("run_powertrain_case() ready")

# %% [markdown]
# ## 7. Run Cases and Save CSV

# %%
FIELDNAMES = [
    "case_name",
    "powertrain",
    "engine_enum",
    "transmission_enum",
    "time",
    "x",
    "y",
    "z",
    "vx",
    "vy",
    "vz",
    "speed",
    "acceleration",
    "roll",
    "pitch",
    "yaw",
    "steering",
    "throttle",
    "braking",
    "engine_speed_rad_s",
    "engine_rpm",
    "engine_torque_Nm",
    "engine_reaction_torque_Nm",
    "gear",
    "driveshaft_torque_Nm",
    "motorshaft_speed_rad_s",
    "transmission_reaction_torque_Nm",
    "is_automatic",
    "has_torque_converter",
    "tc_slippage",
    "tc_input_torque_Nm",
    "tc_output_torque_Nm",
    "tc_output_speed_rad_s",
    "omega_FL_rad_s",
    "omega_FR_rad_s",
    "omega_RL_rad_s",
    "omega_RR_rad_s",
    "slip_FL_est",
    "slip_FR_est",
    "slip_RL_est",
    "slip_RR_est",
]


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "")
                            for field in FIELDNAMES})


all_rows = []

for case in powertrain_cases:
    print("Running:", case["label"])

    try:
        case_rows = run_powertrain_case(case)
        case_csv_path = RESULT_DIR / f'{case["case_name"]}.csv'
        write_csv(case_csv_path, case_rows)
        print("Saved:", case_csv_path)
        all_rows.extend(case_rows)

    except Exception as exc:
        print("Failed:", case["label"])
        print("Reason:", exc)

if len(all_rows) == 0:
    raise RuntimeError("All powertrain cases failed.")

combined_csv_path = RESULT_DIR / "powertrain_comparison_all_cases.csv"
write_csv(combined_csv_path, all_rows)

print("All available powertrain cases finished")
print("Saved combined CSV:", combined_csv_path)
print("Total rows:", len(all_rows))

# %% [markdown]
# ## 8. Plot Results

# %%


def group_rows_by_powertrain(rows):
    grouped = {}
    for row in rows:
        grouped.setdefault(row["powertrain"], []).append(row)
    return grouped


def finite_xy(rows, x_key, y_key):
    xs = []
    ys = []

    for row in rows:
        x = row.get(x_key, float("nan"))
        y = row.get(y_key, float("nan"))
        if m.isfinite(x) and m.isfinite(y):
            xs.append(x)
            ys.append(y)

    return xs, ys


def plot_metric(rows, y_key, ylabel, title, filename, step_plot=False):
    plt.figure(figsize=(8, 5))

    for label, case_rows in group_rows_by_powertrain(rows).items():
        xs, ys = finite_xy(case_rows, "time", y_key)
        if step_plot:
            plt.step(xs, ys, where="post", label=label)
        else:
            plt.plot(xs, ys, label=label)

    plt.xlabel("Time [s]")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True)
    plt.legend()

    fig_path = FIGURE_DIR / filename
    plt.savefig(fig_path, dpi=200, bbox_inches="tight")
    plt.close()

    print("Saved figure:", fig_path)


plot_metric(
    all_rows,
    "speed",
    "Speed [m/s]",
    "Powertrain Comparison - Speed",
    "powertrain_speed.png",
)

plot_metric(
    all_rows,
    "engine_rpm",
    "Engine speed [RPM]",
    "Powertrain Comparison - Engine RPM",
    "powertrain_engine_rpm.png",
)

plot_metric(
    all_rows,
    "driveshaft_torque_Nm",
    "Driveshaft torque [N m]",
    "Powertrain Comparison - Driveshaft Torque",
    "powertrain_driveshaft_torque.png",
)

plot_metric(
    all_rows,
    "gear",
    "Gear",
    "Powertrain Comparison - Gear",
    "powertrain_gear.png",
    step_plot=True,
)

# %% [markdown]
# ## 9. Summary

# %%


def mean(values):
    values = [v for v in values if m.isfinite(v)]
    if len(values) == 0:
        return float("nan")
    return sum(values) / len(values)


def max_finite(values):
    values = [v for v in values if m.isfinite(v)]
    if len(values) == 0:
        return float("nan")
    return max(values)


def count_gear_changes(rows):
    gears = [row.get("gear", float("nan")) for row in rows]
    count = 0
    previous = None

    for gear in gears:
        if not m.isfinite(gear):
            continue
        gear = int(gear)
        if previous is None:
            previous = gear
            continue
        if gear != previous:
            count += 1
            previous = gear

    return count


summary_rows = []

for label, rows in group_rows_by_powertrain(all_rows).items():
    first = rows[0]
    last = rows[-1]

    summary_rows.append(
        {
            "powertrain": label,
            "travel_x_m": last["x"] - first["x"],
            "travel_z_m": last["z"] - first["z"],
            "final_speed_mps": last["speed"],
            "mean_speed_mps": mean([row["speed"] for row in rows]),
            "max_speed_mps": max_finite([row["speed"] for row in rows]),
            "max_engine_rpm": max_finite([row.get("engine_rpm", float("nan")) for row in rows]),
            "mean_driveshaft_torque_Nm": mean(
                [row.get("driveshaft_torque_Nm", float("nan")) for row in rows]
            ),
            "max_abs_slip_RR_est": max_finite(
                [abs(row.get("slip_RR_est", float("nan"))) for row in rows]
            ),
            "gear_changes": count_gear_changes(rows),
            "fixed_throttle": fixed_throttle,
            "terrain_friction": terrain_friction,
        }
    )


summary_path = RESULT_DIR / "powertrain_comparison_summary.csv"
summary_fields = list(summary_rows[0].keys())

with summary_path.open("w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=summary_fields)
    writer.writeheader()
    writer.writerows(summary_rows)

print("Saved summary:", summary_path)
print()
print("Powertrain summary")
print("-" * 96)
print(
    f"{'Powertrain':<14} {'Travel X [m]':>12} {'Mean speed':>12} "
    f"{'Max RPM':>12} {'Mean T_d':>12} {'Gear changes':>14}"
)
print("-" * 96)

for row in summary_rows:
    print(
        f"{row['powertrain']:<14} "
        f"{row['travel_x_m']:>12.3f} "
        f"{row['mean_speed_mps']:>12.3f} "
        f"{row['max_engine_rpm']:>12.1f} "
        f"{row['mean_driveshaft_torque_Nm']:>12.1f} "
        f"{row['gear_changes']:>14}"
    )

print("-" * 96)

# %% [markdown]
# ## 10. Interpretation Notes
#
# 관찰할 포인트:
#
# ```text
# 1. SimpleMap과 Shafts의 engine RPM 상승 패턴이 같은가?
# 2. Shafts model에서 torque converter 관련 값이 기록되는가?
# 3. CVT case는 gear가 고정되어 있어도 engine RPM / torque 응답이 어떻게 달라지는가?
# 4. driveshaft torque가 커질 때 wheel slip 추정값도 같이 커지는가?
# ```
#
# 주의:
#
# - `slip_*_est`는 단순 근사값이다.
# - 실제 tire model 내부 slip 정의와 완전히 같지 않다.
# - powertrain 결과는 driveline, tire, terrain과 함께 해석해야 한다.
