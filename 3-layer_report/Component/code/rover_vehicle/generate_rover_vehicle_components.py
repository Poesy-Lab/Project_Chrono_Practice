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
    save_figure,
    set_axes_equal,
    style_3d_axes,
    try_import_chrono,
    vec_xyz,
    write_csv,
)


def render_rover_components() -> list[Path]:
    paths = []

    fig = plt.figure(figsize=(8.2, 5.8))
    ax = fig.add_subplot(111, projection="3d")
    add_box(ax, (0, 0, 0.55), (1.8, 1.05, 0.42), "#2563eb", label="Chassis")
    add_box(ax, (0.55, 0, 0.87), (0.36, 0.54, 0.20), "#f59e0b", label="Visual payload")
    for x in (-0.58, 0.58):
        for y in (-0.66, 0.66):
            add_cylinder_y(ax, (x, y, 0.30), 0.28, 0.20, "#111827", label="Wheel/Tire" if x < 0 and y < 0 else None)
            add_box(ax, (x, y * 0.72, 0.42), (0.45, 0.06, 0.07), "#64748b", alpha=0.9)
    ax.plot([-0.70, 0.70], [0, 0], [0.32, 0.32], color="#dc2626", linewidth=3, label="Driveline")
    ax.quiver(0.72, 0.66, 0.3, 0.25, 0.14, 0, color="#16a34a", linewidth=2, label="Steering")
    ax.set_xlim(-1.25, 1.25)
    ax.set_ylim(-1.15, 1.15)
    ax.set_zlim(0, 1.4)
    style_3d_axes(ax, "Rover/Vehicle Component Layout")
    ax.legend(loc="upper left", fontsize=8)
    set_axes_equal(ax)
    paths.append(save_figure(fig, IMAGES_RENDER / "rover_vehicle_component_overview.png"))

    fig = plt.figure(figsize=(8.2, 5.8))
    ax = fig.add_subplot(111, projection="3d")
    add_box(ax, (0, 0, 0.62), (1.9, 0.95, 0.34), "#1d4ed8", label="Visual Shape")
    add_box(ax, (0, 0, 0.58), (1.7, 0.78, 0.30), "#ef4444", alpha=0.25, edgecolor="#b91c1c", label="Collision Shape")
    for x in (-0.62, 0.62):
        for y in (-0.59, 0.59):
            add_cylinder_y(ax, (x, y, 0.31), 0.25, 0.16, "#0f172a")
    ax.set_xlim(-1.25, 1.25)
    ax.set_ylim(-1.0, 1.0)
    ax.set_zlim(0, 1.2)
    style_3d_axes(ax, "Visual Shape vs Collision Shape")
    ax.legend(loc="upper left", fontsize=8)
    set_axes_equal(ax)
    paths.append(save_figure(fig, IMAGES_RENDER / "rover_visual_collision_shapes.png"))

    fig = plt.figure(figsize=(8.2, 5.8))
    ax = fig.add_subplot(111, projection="3d")
    add_box(ax, (0, 0, 0.62), (1.8, 0.9, 0.32), "#2563eb", label="Chassis")
    for x in (-0.55, 0.55):
        for y in (-0.62, 0.62):
            add_cylinder_y(ax, (x, y, 0.28), 0.25, 0.16, "#111827")
            ax.plot([x, x], [y * 0.78, y], [0.52, 0.28], color="#f97316", linewidth=3)
            ax.plot([x - 0.22, x + 0.22], [y * 0.78, y * 0.78], [0.52, 0.52], color="#64748b", linewidth=2)
    ax.text(-0.75, -0.22, 0.82, "Suspension link", fontsize=8)
    ax.text(0.70, 0.50, 0.62, "Wheel axle", fontsize=8)
    ax.set_xlim(-1.25, 1.25)
    ax.set_ylim(-1.0, 1.0)
    ax.set_zlim(0, 1.25)
    style_3d_axes(ax, "Suspension and Axle Components")
    set_axes_equal(ax)
    paths.append(save_figure(fig, IMAGES_RENDER / "rover_suspension_steering_components.png"))

    fig = plt.figure(figsize=(8.2, 5.8))
    ax = fig.add_subplot(111, projection="3d")
    add_box(ax, (0, 0, 0.58), (1.6, 0.75, 0.28), "#334155", label="Tracked chassis")
    for y in (-0.48, 0.48):
        for x, label in [(-0.62, "Idler"), (0.0, "Roller"), (0.62, "Sprocket")]:
            add_cylinder_y(ax, (x, y, 0.28), 0.22, 0.12, "#111827", label=label if y < 0 else None)
        xs = np.linspace(-0.8, 0.8, 18)
        for x in xs:
            add_box(ax, (x, y, 0.08), (0.07, 0.20, 0.05), "#f59e0b", alpha=0.95)
    ax.set_xlim(-1.15, 1.15)
    ax.set_ylim(-0.9, 0.9)
    ax.set_zlim(0, 1.1)
    style_3d_axes(ax, "Tracked Vehicle Extension Components")
    ax.legend(loc="upper left", fontsize=8)
    set_axes_equal(ax)
    paths.append(save_figure(fig, IMAGES_RENDER / "tracked_vehicle_components.png"))

    return paths


def run_chrono_rover_probe() -> tuple[Path, Path]:
    chrono, error = try_import_chrono()
    rows = []
    if chrono is not None:
        system = chrono.ChSystemNSC()
        system.SetGravitationalAcceleration(chrono.ChVector3d(0, 0, -9.81))
        material = chrono.ChContactMaterialNSC()
        material.SetFriction(0.45)
        ground = chrono.ChBodyEasyBox(8, 4, 0.12, 1000, True, True, material)
        ground.SetFixed(True)
        ground.SetPos(chrono.ChVector3d(0, 0, -0.06))
        system.AddBody(ground)
        chassis = chrono.ChBodyEasyBox(1.4, 0.8, 0.28, 350, True, True, material)
        chassis.SetPos(chrono.ChVector3d(-2.0, 0, 0.45))
        chassis.SetPosDt(chrono.ChVector3d(1.3, 0, 0))
        system.AddBody(chassis)
        t = 0.0
        while t <= 2.4 + 1e-9:
            pos = chassis.GetPos()
            vel = chassis.GetPosDt()
            px, py, pz = vec_xyz(pos)
            vx, vy, vz = vec_xyz(vel)
            rows.append(
                {
                    "time_s": f"{t:.3f}",
                    "x_m": f"{px:.5f}",
                    "y_m": f"{py:.5f}",
                    "z_m": f"{pz:.5f}",
                    "speed_mps": f"{math.sqrt(vx * vx + vy * vy + vz * vz):.5f}",
                    "source": "pychrono",
                }
            )
            system.DoStepDynamics(0.02)
            t = system.GetChTime()
    else:
        for t in np.arange(0, 2.42, 0.02):
            rows.append(
                {
                    "time_s": f"{t:.3f}",
                    "x_m": f"{-2.0 + 1.3 * t:.5f}",
                    "y_m": "0.00000",
                    "z_m": "0.45000",
                    "speed_mps": "1.30000",
                    "source": f"fallback: {error}",
                }
            )

    csv_path = write_csv(OUTPUT_CSV / "rover_vehicle_chassis_probe.csv", ["time_s", "x_m", "y_m", "z_m", "speed_mps", "source"], rows)

    data = np.genfromtxt(csv_path, delimiter=",", names=True, dtype=None, encoding="utf-8")
    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    ax.plot(data["time_s"], data["x_m"], color="#2563eb", linewidth=2, label="chassis x")
    ax.plot(data["time_s"], data["speed_mps"], color="#dc2626", linewidth=2, label="speed")
    ax.set_title("Chassis Component State Probe")
    ax.set_xlabel("time [s]")
    ax.set_ylabel("value")
    ax.grid(True, alpha=0.3)
    ax.legend()
    graph_path = save_figure(fig, IMAGES_GRAPH / "rover_vehicle_chassis_probe_graph.png")
    return csv_path, graph_path


def main() -> None:
    ensure_output_dirs()
    render_paths = render_rover_components()
    csv_path, graph_path = run_chrono_rover_probe()
    print("rover_vehicle renders:")
    for path in render_paths:
        print(path)
    print("rover_vehicle csv:", csv_path)
    print("rover_vehicle graph:", graph_path)


if __name__ == "__main__":
    main()
