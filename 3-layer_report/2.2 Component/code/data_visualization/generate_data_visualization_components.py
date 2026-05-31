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
    add_callout_3d,
    add_box,
    add_cylinder_y,
    ensure_output_dirs,
    legend_if_any,
    save_figure,
    set_axes_equal,
    try_import_chrono,
    vec_xyz,
    write_csv,
)
from vsg_component_render import (  # noqa: E402
    add_box as vsg_add_box,
    add_cylinder_y as vsg_add_cylinder_y,
    add_sphere as vsg_add_sphere,
    render_vsg_scene,
)


def render_visualization_components() -> list[Path]:
    paths = []
    output = IMAGES_RENDER / "data_visualization_sensor_components.png"

    def sensor_scene(system, chrono):
        def add_beam(name, start, end, thickness, color):
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            length = math.sqrt(dx * dx + dy * dy)
            if length <= 0:
                return
            center = ((start[0] + end[0]) / 2.0, (start[1] + end[1]) / 2.0, (start[2] + end[2]) / 2.0)
            vsg_add_box(system, chrono, name, center, (length, thickness, thickness), color, collide=False, rot_z=math.atan2(dy, dx))

        vsg_add_box(system, chrono, "sensor_ground", (0, 0, -0.035), (3.4, 2.5, 0.07), (0.58, 0.61, 0.57), collide=False)
        vsg_add_box(system, chrono, "logged_rover_body", (0, 0, 0.36), (1.30, 0.68, 0.26), (0.10, 0.34, 0.78), collide=False)
        vsg_add_box(system, chrono, "sensor_mast", (0.18, -0.18, 0.72), (0.10, 0.10, 0.48), (0.04, 0.65, 0.66), collide=False)
        vsg_add_sphere(system, chrono, "render_camera", (-1.24, -1.05, 1.04), 0.08, (0.82, 0.12, 0.10), collide=False)
        vsg_add_sphere(system, chrono, "gps_imu_origin", (0.0, 0.0, 0.62), 0.07, (0.10, 0.62, 0.22), collide=False)
        add_beam("camera_sightline", (-1.17, -0.98, 0.96), (-0.18, -0.12, 0.58), 0.035, (0.82, 0.12, 0.10))
        lidar_origin = (0.18, -0.18, 0.78)
        for index, y in enumerate(np.linspace(-0.60, 0.60, 7)):
            add_beam(f"lidar_ray_{index}", lidar_origin, (1.42, float(y), 0.72), 0.025, (0.95, 0.58, 0.10))
        for x in (-0.46, 0.46):
            for y in (-0.48, 0.48):
                vsg_add_cylinder_y(system, chrono, "logged_rover_wheel", (x, y, 0.20), 0.20, 0.14, (0.02, 0.03, 0.05), collide=False)

    vsg_ok, _ = render_vsg_scene(output, sensor_scene, camera=(2.55, -3.20, 1.55), target=(0.05, -0.05, 0.46), title="Render and sensor component")
    if vsg_ok:
        paths.append(output)
        return paths

    fig = plt.figure(figsize=(8.4, 5.8))
    ax = fig.add_subplot(111, projection="3d")
    add_box(ax, (0, 0, 0.48), (1.5, 0.8, 0.28), "#2563eb")
    for x in (-0.5, 0.5):
        for y in (-0.52, 0.52):
            add_cylinder_y(ax, (x, y, 0.22), 0.21, 0.14, "#111827")
    ax.scatter([-1.6], [-1.4], [1.15], color="#dc2626", s=70)
    ax.plot([-1.6, 0], [-1.4, 0], [1.15, 0.5], color="#dc2626", linestyle="--")
    ax.scatter([0.0], [0.0], [0.9], color="#16a34a", s=70)
    for angle in np.linspace(-0.7, 0.7, 8):
        ax.plot([0.0, 1.5 * math.cos(angle)], [0.0, 1.5 * math.sin(angle)], [0.92, 0.75], color="#f59e0b", alpha=0.7)
    add_callout_3d(ax, "Render camera", (0.14, 0.76), (-1.6, -1.4, 1.15), color="#991b1b", size=8)
    add_callout_3d(ax, "GPS/IMU", (0.58, 0.76), (0.0, 0.0, 0.9), color="#15803d", size=8)
    add_callout_3d(ax, "LiDAR rays", (0.66, 0.66), (1.0, 0.0, 0.8), color="#b45309", size=8)
    add_callout_3d(ax, "Logged body", (0.26, 0.22), (0.0, 0.0, 0.62), color="#1d4ed8", size=8)
    ax.set_xlim(-1.75, 1.55)
    ax.set_ylim(-1.55, 1.35)
    ax.set_zlim(0, 1.45)
    ax.view_init(elev=22, azim=-50)
    ax.set_axis_off()
    set_axes_equal(ax)
    paths.append(save_figure(fig, output))
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
                    "wheel_speed_radps": f"{8.0 + 5.0 * throttle:.5f}",
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
                    "source": f"fallback_{error}",
                }
            )
            control_rows.append(
                {
                    "time_s": f"{t:.3f}",
                    "throttle": f"{throttle:.5f}",
                    "brake": "0.00000",
                    "steering": f"{steering:.5f}",
                    "drive_torque_Nm": f"{120 * throttle:.5f}",
                    "wheel_speed_radps": f"{8.0 + 5.0 * throttle:.5f}",
                    "source": f"fallback_{error}",
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
        ["time_s", "throttle", "brake", "steering", "drive_torque_Nm", "wheel_speed_radps", "source"],
        control_rows,
    )

    state = np.genfromtxt(state_csv, delimiter=",", names=True, dtype=None, encoding="utf-8")
    control = np.genfromtxt(control_csv, delimiter=",", names=True, dtype=None, encoding="utf-8")
    graphs = []
    fig, (traj_ax, speed_ax) = plt.subplots(1, 2, figsize=(9.2, 4.5))
    traj_ax.plot(state["x_m"], state["y_m"], color="#2563eb", linewidth=2)
    traj_ax.scatter([state["x_m"][0]], [state["y_m"][0]], color="#16a34a", s=35, label="start")
    traj_ax.scatter([state["x_m"][-1]], [state["y_m"][-1]], color="#dc2626", s=35, label="end")
    traj_ax.set_title("Trajectory")
    traj_ax.set_xlabel("x [m]")
    traj_ax.set_ylabel("y [m]")
    traj_ax.grid(True, alpha=0.3)
    legend_if_any(traj_ax, loc="best", fontsize=8)
    speed = np.sqrt(state["vx_mps"] ** 2 + state["vy_mps"] ** 2 + state["vz_mps"] ** 2)
    speed_ax.plot(state["time_s"], speed, color="#0f766e", linewidth=2)
    speed_ax.set_title("Speed")
    speed_ax.set_xlabel("time [s]")
    speed_ax.set_ylabel("speed [m/s]")
    speed_ax.grid(True, alpha=0.3)
    fig.suptitle("State Logger Trajectory and Speed")
    graphs.append(save_figure(fig, IMAGES_GRAPH / "data_visualization_state_trajectory.png"))

    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    ax.plot(control["time_s"], control["throttle"], color="#16a34a", linewidth=2, label="throttle")
    ax.plot(control["time_s"], control["brake"], color="#2563eb", linewidth=1.8, linestyle="--", label="brake")
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
