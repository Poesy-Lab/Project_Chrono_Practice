from __future__ import annotations

import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.append(str(Path(__file__).resolve().parents[1] / "common"))

from component_utils import (  # noqa: E402
    IMAGES_GRAPH,
    IMAGES_RENDER,
    OUTPUT_CSV,
    add_box,
    add_cylinder_y,
    ensure_output_dirs,
    legend_if_any,
    save_figure,
    set_axes_equal,
    style_3d_axes,
    try_import_chrono,
    vec_xyz,
    write_csv,
)


def render_visualization_components() -> list[Path]:
    paths = []
    fig = plt.figure(figsize=(8.4, 5.8))
    ax = fig.add_subplot(111, projection="3d")
    add_box(ax, (0, 0, 0.48), (1.5, 0.8, 0.28), "#2563eb", label="rover body")
    for x in (-0.5, 0.5):
        for y in (-0.52, 0.52):
            add_cylinder_y(ax, (x, y, 0.22), 0.21, 0.14, "#111827")
    ax.scatter([-1.6], [-1.4], [1.15], color="#dc2626", s=70, label="Camera")
    ax.plot([-1.6, 0], [-1.4, 0], [1.15, 0.5], color="#dc2626", linestyle="--")
    ax.scatter([0.0], [0.0], [0.9], color="#16a34a", s=70, label="GPS/IMU")
    for angle in np.linspace(-0.7, 0.7, 8):
        ax.plot([0.0, 1.5 * math.cos(angle)], [0.0, 1.5 * math.sin(angle)], [0.92, 0.75], color="#f59e0b", alpha=0.7)
    ax.text(0.65, 0.55, 1.0, "LiDAR scan rays", fontsize=8)
    ax.set_xlim(-2.0, 2.0)
    ax.set_ylim(-1.8, 1.8)
    ax.set_zlim(0, 1.7)
    style_3d_axes(ax, "Render, Screenshot, and Sensor Components")
    legend_if_any(ax, loc="upper left", fontsize=8)
    set_axes_equal(ax)
    paths.append(save_figure(fig, IMAGES_RENDER / "data_visualization_sensor_components.png"))
    return paths


def generate_state_and_control_logs() -> tuple[list[Path], list[Path]]:
    chrono, error = try_import_chrono()
    state_rows = []
    control_rows = []

    if chrono is not None:
        system = chrono.ChSystemNSC()
        system.SetGravitationalAcceleration(chrono.ChVector3d(0, 0, -9.81))
        material = chrono.ChContactMaterialNSC()
        material.SetFriction(0.5)
        ground = chrono.ChBodyEasyBox(8, 4, 0.1, 1000, True, True, material)
        ground.SetFixed(True)
        ground.SetPos(chrono.ChVector3d(0, 0, -0.05))
        rover = chrono.ChBodyEasyBox(0.8, 0.5, 0.25, 300, True, True, material)
        rover.SetPos(chrono.ChVector3d(-2.5, 0, 0.25))
        system.AddBody(ground)
        system.AddBody(rover)
        while system.GetChTime() <= 3.0:
            t = system.GetChTime()
            throttle = 0.45 + 0.25 * math.sin(2.2 * t)
            steering = 0.28 * math.sin(1.4 * t)
            rover.SetPosDt(chrono.ChVector3d(0.25 + 0.9 * throttle, 0.18 * steering, 0))
            pos = rover.GetPos()
            vel = rover.GetPosDt()
            px, py, pz = vec_xyz(pos)
            vx, vy, vz = vec_xyz(vel)
            state_rows.append(
                {
                    "time_s": f"{t:.3f}",
                    "body_name": "component_demo_rover",
                    "x_m": f"{px:.5f}",
                    "y_m": f"{py:.5f}",
                    "z_m": f"{pz:.5f}",
                    "vx_mps": f"{vx:.5f}",
                    "vy_mps": f"{vy:.5f}",
                    "vz_mps": f"{vz:.5f}",
                    "roll_rad": "0.00000",
                    "pitch_rad": "0.00000",
                    "yaw_rad": "0.00000",
                    "contact_force_N": "0.00000",
                    "source": "pychrono",
                }
            )
            control_rows.append(
                {
                    "time_s": f"{t:.3f}",
                    "throttle": f"{throttle:.5f}",
                    "brake": "0.00000",
                    "steering": f"{steering:.5f}",
                    "drive_torque_Nm": f"{120 * throttle:.5f}",
                    "source": "pychrono",
                }
            )
            system.DoStepDynamics(0.02)
    else:
        for t in np.arange(0, 3.02, 0.02):
            throttle = 0.45 + 0.25 * math.sin(2.2 * t)
            steering = 0.28 * math.sin(1.4 * t)
            state_rows.append(
                {
                    "time_s": f"{t:.3f}",
                    "body_name": "component_demo_rover",
                    "x_m": f"{-2.5 + 0.35 * t * t:.5f}",
                    "y_m": f"{0.12 * math.sin(1.1 * t):.5f}",
                    "z_m": "0.25000",
                    "vx_mps": f"{0.7 * t:.5f}",
                    "vy_mps": f"{0.132 * math.cos(1.1 * t):.5f}",
                    "vz_mps": "0.00000",
                    "roll_rad": "0.00000",
                    "pitch_rad": "0.00000",
                    "yaw_rad": f"{0.1 * steering:.5f}",
                    "contact_force_N": "0.00000",
                    "source": f"fallback: {error}",
                }
            )
            control_rows.append(
                {
                    "time_s": f"{t:.3f}",
                    "throttle": f"{throttle:.5f}",
                    "brake": "0.00000",
                    "steering": f"{steering:.5f}",
                    "drive_torque_Nm": f"{120 * throttle:.5f}",
                    "source": f"fallback: {error}",
                }
            )

    state_csv = write_csv(
        OUTPUT_CSV / "data_visualization_state_log.csv",
        [
            "time_s",
            "body_name",
            "x_m",
            "y_m",
            "z_m",
            "vx_mps",
            "vy_mps",
            "vz_mps",
            "roll_rad",
            "pitch_rad",
            "yaw_rad",
            "contact_force_N",
            "source",
        ],
        state_rows,
    )
    control_csv = write_csv(
        OUTPUT_CSV / "data_visualization_control_log.csv",
        ["time_s", "throttle", "brake", "steering", "drive_torque_Nm", "source"],
        control_rows,
    )

    state = np.genfromtxt(state_csv, delimiter=",", names=True, dtype=None, encoding="utf-8")
    control = np.genfromtxt(control_csv, delimiter=",", names=True, dtype=None, encoding="utf-8")
    graphs = []
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    ax.plot(state["x_m"], state["y_m"], color="#2563eb", linewidth=2)
    ax.set_title("State Logger Trajectory")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.grid(True, alpha=0.3)
    ax.set_aspect("equal", adjustable="box")
    graphs.append(save_figure(fig, IMAGES_GRAPH / "data_visualization_state_trajectory.png"))

    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    ax.plot(control["time_s"], control["throttle"], color="#16a34a", linewidth=2, label="throttle")
    ax.plot(control["time_s"], control["steering"], color="#dc2626", linewidth=2, label="steering")
    ax.set_title("Control Logger Inputs")
    ax.set_xlabel("time [s]")
    ax.set_ylabel("normalized input")
    ax.grid(True, alpha=0.3)
    legend_if_any(ax)
    graphs.append(save_figure(fig, IMAGES_GRAPH / "data_visualization_control_inputs.png"))
    return [state_csv, control_csv], graphs


def main() -> None:
    ensure_output_dirs()
    renders = render_visualization_components()
    csv_paths, graphs = generate_state_and_control_logs()
    print("data_visualization renders:")
    for path in renders:
        print(path)
    print("data_visualization csv:")
    for path in csv_paths:
        print(path)
    print("data_visualization graphs:")
    for path in graphs:
        print(path)


if __name__ == "__main__":
    main()
