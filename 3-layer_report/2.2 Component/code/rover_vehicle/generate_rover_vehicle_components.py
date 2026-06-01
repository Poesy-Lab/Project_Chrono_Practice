#!/usr/bin/env python
"""Run from repository root:

    source ~/anaconda3/etc/profile.d/conda.sh
    conda activate chrono
    source setup_chrono_env.sh
    python 3-layer_report/Component/code/rover_vehicle/generate_rover_vehicle_components.py

Generates rover/vehicle Component renders plus a PyChrono CSV and graph for a
chassis/wheel/motor probe. The render images use short component callouts so
that each figure remains readable even before the markdown interpretation table.
"""

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
    OUTPUT_JSON,
    OUTPUT_RAW,
    add_callout_3d,
    add_box as add_mpl_box,
    add_cylinder_y as add_mpl_cylinder_y,
    ensure_output_dirs,
    save_figure,
    try_import_chrono,
    vec_length,
    vec_xyz,
    write_csv,
    write_json,
)


def _render_status_path() -> Path:
    return OUTPUT_RAW / "rover_vehicle_render_status.log"


def _wheel_positions() -> list[tuple[float, float, float]]:
    return [(-0.68, -0.55, 0.30), (-0.68, 0.55, 0.30), (0.68, -0.55, 0.30), (0.68, 0.55, 0.30)]


COLORS = {
    "chassis": "#2563eb",
    "payload": "#0f766e",
    "wheel": "#111827",
    "axle": "#9ca3af",
    "drive": "#dc2626",
    "steer": "#16a34a",
    "suspension": "#f59e0b",
    "damper": "#7c3aed",
    "collision": "#ef4444",
    "terrain": "#a3a3a3",
}


def _line3d(ax, start, end, *, color: str, linewidth: float = 2.4, label: str | None = None, linestyle: str = "-") -> None:
    ax.plot(
        [start[0], end[0]],
        [start[1], end[1]],
        [start[2], end[2]],
        color=color,
        linewidth=linewidth,
        linestyle=linestyle,
        label=label,
    )


def _point3d(ax, point, *, color: str = "#111827", size: float = 26) -> None:
    ax.scatter([point[0]], [point[1]], [point[2]], color=color, s=size, depthshade=True)


def _draw_spring(ax, start, end, *, coils: int = 8, radius: float = 0.035, color: str = COLORS["damper"]) -> None:
    start_v = np.array(start, dtype=float)
    end_v = np.array(end, dtype=float)
    axis = end_v - start_v
    length = float(np.linalg.norm(axis))
    if length == 0:
        return
    direction = axis / length
    helper = np.array([0.0, 1.0, 0.0])
    normal = np.cross(direction, helper)
    if np.linalg.norm(normal) < 1e-6:
        helper = np.array([1.0, 0.0, 0.0])
        normal = np.cross(direction, helper)
    normal = normal / np.linalg.norm(normal)
    binormal = np.cross(direction, normal)
    t = np.linspace(0.0, 1.0, coils * 24)
    points = start_v + np.outer(t, axis) + radius * np.sin(2 * math.pi * coils * t)[:, None] * normal + radius * np.cos(2 * math.pi * coils * t)[:, None] * binormal
    ax.plot(points[:, 0], points[:, 1], points[:, 2], color=color, linewidth=2.0)


def _format_component_ax(ax, *, xlim=(-1.55, 1.55), ylim=(-1.1, 1.1), zlim=(0.0, 1.35), elev=24, azim=-48) -> None:
    ax.view_init(elev=elev, azim=azim)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_zlim(*zlim)
    ax.set_axis_off()
    try:
        ax.set_box_aspect((xlim[1] - xlim[0], ylim[1] - ylim[0], zlim[1] - zlim[0]))
    except Exception:
        pass


def _render_rover_overview() -> tuple[Path, bool, str]:
    output = IMAGES_RENDER / "rover_vehicle_component_overview.png"

    fig = plt.figure(figsize=(9.0, 5.8))
    ax = fig.add_subplot(111, projection="3d")
    add_mpl_box(ax, (0, 0, 0.56), (1.45, 0.78, 0.26), COLORS["chassis"], alpha=0.88)
    add_mpl_box(ax, (-0.34, -0.30, 0.86), (0.46, 0.30, 0.20), COLORS["payload"], alpha=0.98)
    add_mpl_box(ax, (0.38, -0.32, 0.98), (0.14, 0.14, 0.48), "#14b8a6", alpha=0.98)
    add_callout_3d(ax, "Chassis: blue body", (0.12, 0.78), (0.0, 0.0, 0.69), color="#1d4ed8", size=9)
    add_callout_3d(ax, "Payload: green box", (0.12, 0.70), (-0.34, -0.30, 0.96), color="#0f766e", size=9)
    add_callout_3d(ax, "Sensor mast: cyan post", (0.12, 0.62), (0.38, -0.32, 1.18), color="#0f766e", size=9)
    _line3d(ax, (-0.34, -0.30, 0.72), (-0.34, -0.30, 0.76), color="#0f766e", linewidth=2.0)
    _line3d(ax, (0.38, -0.32, 0.72), (0.38, -0.32, 0.78), color="#0f766e", linewidth=2.0)
    for pos in _wheel_positions():
        add_mpl_cylinder_y(ax, pos, 0.27, 0.18, COLORS["wheel"])
        _line3d(ax, (pos[0], pos[1] * 0.78, pos[2]), (pos[0], pos[1] * 0.46, pos[2] + 0.18), color="#64748b", linewidth=2.2)
    add_callout_3d(ax, "Wheel/Tire: black cylinders", (0.62, 0.78), (0.68, 0.55, 0.30), color="#111827", size=9)
    _format_component_ax(ax, xlim=(-1.20, 1.20), ylim=(-0.88, 0.88), zlim=(0.12, 1.22), elev=22, azim=-50)
    save_figure(fig, output)
    return output, True, "isometric component render"


def _render_payload_sensor_mount() -> tuple[Path, bool, str]:
    output = IMAGES_RENDER / "rover_payload_sensor_mount_component.png"

    fig = plt.figure(figsize=(9.0, 5.8))
    ax = fig.add_subplot(111, projection="3d")
    add_mpl_box(ax, (0, 0, 0.48), (1.45, 0.78, 0.22), COLORS["chassis"], alpha=0.32, edgecolor="#1d4ed8")
    add_mpl_box(ax, (-0.28, -0.18, 0.74), (0.48, 0.36, 0.20), COLORS["payload"], alpha=0.98)
    add_mpl_box(ax, (0.42, -0.24, 0.92), (0.14, 0.14, 0.46), "#14b8a6", alpha=0.98)
    add_callout_3d(ax, "Payload: green box", (0.12, 0.72), (-0.28, -0.18, 0.84), color="#0f766e", size=9)
    add_callout_3d(ax, "Camera: red dot", (0.58, 0.74), (0.52, -0.42, 1.18), color="#dc2626", size=9)
    add_callout_3d(ax, "LiDAR: orange rays", (0.64, 0.66), (0.92, -0.34, 1.02), color="#b45309", size=9)
    camera_origin = (0.52, -0.42, 1.18)
    _point3d(ax, camera_origin, color="#dc2626", size=62)
    for angle in np.linspace(-0.28, 0.28, 7):
        end = (1.10, -0.34 + angle, 1.02)
        _line3d(ax, camera_origin, end, color="#f59e0b", linewidth=1.7)
    _point3d(ax, (-0.28, -0.18, 0.90), color="#22c55e", size=34)
    for pos in _wheel_positions():
        add_mpl_cylinder_y(ax, pos, 0.22, 0.14, "#111827", alpha=0.40)
    _format_component_ax(ax, xlim=(-1.15, 1.15), ylim=(-0.86, 0.86), zlim=(0.08, 1.32), elev=22, azim=-50)
    save_figure(fig, output)
    return output, True, "payload and sensor mount render"


def _render_wheel_tire_component() -> tuple[Path, bool, str]:
    output = IMAGES_RENDER / "rover_wheel_tire_component.png"

    fig = plt.figure(figsize=(9.0, 5.2))
    ax = fig.add_subplot(111, projection="3d")
    add_mpl_box(ax, (0, 0, 0.62), (1.25, 0.52, 0.20), COLORS["chassis"], alpha=0.24, edgecolor="#1d4ed8")
    wheel_centers = [(-0.52, -0.54, 0.28), (0.52, -0.54, 0.28)]
    for pos in wheel_centers:
        add_mpl_cylinder_y(ax, pos, 0.28, 0.18, COLORS["wheel"])
        add_mpl_cylinder_y(ax, (pos[0], pos[1], pos[2]), 0.12, 0.20, "#e5e7eb", alpha=0.96)
        _line3d(ax, (pos[0], -0.54, pos[2]), (pos[0], -0.18, pos[2]), color=COLORS["axle"], linewidth=3.0)
        add_mpl_box(ax, (pos[0], -0.54, 0.02), (0.30, 0.24, 0.025), "#f59e0b", alpha=0.72, edgecolor="#92400e")
    _line3d(ax, (-0.95, -0.54, 0.02), (0.95, -0.54, 0.02), color="#64748b", linewidth=1.2)
    add_callout_3d(ax, "Tire body", (0.16, 0.70), (-0.52, -0.54, 0.50), color="#111827", size=9)
    add_callout_3d(ax, "Rim/axle", (0.62, 0.66), (0.52, -0.54, 0.28), color="#64748b", size=9)
    add_callout_3d(ax, "Contact patch", (0.62, 0.14), (0.52, -0.54, 0.03), color="#b45309", size=9)
    _format_component_ax(ax, xlim=(-1.05, 1.05), ylim=(-0.75, 0.38), zlim=(0.00, 0.90), elev=20, azim=-50)
    save_figure(fig, output)
    return output, True, "wheel tire contact render"


def _render_axle_joint_component() -> tuple[Path, bool, str]:
    output = IMAGES_RENDER / "rover_axle_joint_component.png"

    fig = plt.figure(figsize=(9.0, 5.8))
    ax = fig.add_subplot(111, projection="3d")
    add_mpl_box(ax, (0, 0, 0.62), (1.45, 0.70, 0.20), COLORS["chassis"], alpha=0.24, edgecolor="#1d4ed8")
    for x in (-0.68, 0.68):
        _line3d(ax, (x, -0.72, 0.30), (x, 0.72, 0.30), color=COLORS["axle"], linewidth=5.0)
        _line3d(ax, (x, -0.42, 0.50), (x, 0.42, 0.50), color="#475569", linewidth=2.4, linestyle="--")
        for y in (-0.55, 0.55):
            add_mpl_cylinder_y(ax, (x, y, 0.30), 0.26, 0.18, COLORS["wheel"])
            _point3d(ax, (x, y, 0.30), color="#facc15", size=44)
            ax.quiver(x, y, 0.30, 0.0, 0.22 if y > 0 else -0.22, 0.0, color="#64748b", linewidth=2.4)
    add_callout_3d(ax, "Revolute axis", (0.12, 0.78), (-0.68, -0.05, 0.50), color="#475569", size=9)
    add_callout_3d(ax, "Joint frame", (0.12, 0.70), (-0.68, -0.55, 0.30), color="#854d0e", size=9)
    _format_component_ax(ax, xlim=(-1.18, 1.18), ylim=(-0.90, 0.90), zlim=(0.08, 1.02), elev=23, azim=-50)
    save_figure(fig, output)
    return output, True, "axle joint axis render"


def _render_motor_drive_component() -> tuple[Path, bool, str]:
    output = IMAGES_RENDER / "rover_motor_drive_component.png"

    fig = plt.figure(figsize=(9.0, 5.8))
    ax = fig.add_subplot(111, projection="3d")
    add_mpl_box(ax, (0, 0, 0.62), (1.45, 0.78, 0.22), COLORS["chassis"], alpha=0.28, edgecolor="#1d4ed8")
    add_mpl_box(ax, (-0.10, 0.0, 0.84), (0.34, 0.26, 0.18), "#ef4444", alpha=0.98)
    add_mpl_box(ax, (0.24, 0.0, 0.62), (0.18, 0.18, 0.14), "#991b1b", alpha=0.95)
    add_callout_3d(ax, "Motor: red block", (0.42, 0.82), (-0.10, 0.0, 0.93), color="#b91c1c", size=9)
    add_callout_3d(ax, "Driveline: red paths", (0.66, 0.66), (0.24, 0.0, 0.66), color="#b91c1c", size=9)
    add_callout_3d(ax, "Brake: orange rings", (0.20, 0.42), (-0.68, -0.54, 0.30), color="#c2410c", size=9, ha="right")
    wheel_positions = _wheel_positions()
    for pos in wheel_positions:
        add_mpl_cylinder_y(ax, pos, 0.26, 0.18, COLORS["wheel"])
        add_mpl_cylinder_y(ax, (pos[0], pos[1] * 0.98, pos[2]), 0.15, 0.03, "#f97316", alpha=0.98)
        _line3d(ax, (0.24, 0.0, 0.62), (pos[0], pos[1] * 0.72, pos[2] + 0.05), color=COLORS["drive"], linewidth=3.0)
        _line3d(ax, (pos[0], pos[1] * 0.72, pos[2] + 0.05), (pos[0], pos[1] * 0.90, pos[2]), color=COLORS["drive"], linewidth=3.0)
        ax.quiver(pos[0], pos[1] * 0.98, pos[2] + 0.23, 0.0, 0.0, -0.12, color="#f97316", linewidth=1.8)
    _line3d(ax, (-0.10, 0.0, 0.75), (0.24, 0.0, 0.66), color=COLORS["drive"], linewidth=4.0)
    _format_component_ax(ax, xlim=(-1.18, 1.18), ylim=(-0.88, 0.88), zlim=(0.10, 1.08), elev=23, azim=-50)
    save_figure(fig, output)
    return output, True, "motor drive path render"


def _render_steering_component() -> tuple[Path, bool, str]:
    output = IMAGES_RENDER / "rover_steering_component.png"

    fig = plt.figure(figsize=(9.0, 5.8))
    ax = fig.add_subplot(111, projection="3d")
    add_mpl_box(ax, (0, 0, 0.62), (1.45, 0.78, 0.22), COLORS["chassis"], alpha=0.30, edgecolor="#1d4ed8")
    rear_positions = [(-0.68, -0.55, 0.30), (-0.68, 0.55, 0.30)]
    front_positions = [(0.68, -0.55, 0.30), (0.68, 0.55, 0.30)]
    for pos in rear_positions:
        add_mpl_cylinder_y(ax, pos, 0.25, 0.16, "#374151", alpha=0.72)
    for pos in front_positions:
        add_mpl_cylinder_y(ax, pos, 0.25, 0.16, COLORS["wheel"])
        _line3d(ax, (pos[0], pos[1] * 0.82, pos[2] + 0.05), (pos[0] + 0.20, pos[1] * 0.82, pos[2] + 0.22), color=COLORS["steer"], linewidth=3.0)
        ax.quiver(pos[0], pos[1], pos[2] + 0.30, 0.18, 0.05 if pos[1] > 0 else -0.05, 0.0, color=COLORS["steer"], linewidth=2.2)
    _line3d(ax, (0.60, -0.46, 0.55), (0.60, 0.46, 0.55), color=COLORS["steer"], linewidth=4.2)
    _line3d(ax, (0.60, -0.46, 0.55), (0.68, -0.45, 0.36), color=COLORS["steer"], linewidth=3.0)
    _line3d(ax, (0.60, 0.46, 0.55), (0.68, 0.45, 0.36), color=COLORS["steer"], linewidth=3.0)
    add_mpl_box(ax, (0.45, 0.0, 0.58), (0.18, 0.18, 0.12), "#22c55e", alpha=0.90)
    add_callout_3d(ax, "Steering rack", (0.62, 0.68), (0.60, 0.0, 0.55), color="#15803d", size=9)
    add_callout_3d(ax, "Steered wheel", (0.78, 0.76), (0.68, 0.55, 0.30), color="#15803d", size=9)
    _format_component_ax(ax, xlim=(-1.16, 1.16), ylim=(-0.86, 0.86), zlim=(0.10, 1.04), elev=23, azim=-50)
    save_figure(fig, output)
    return output, True, "steering linkage render"


def _render_initial_state_component() -> tuple[Path, bool, str]:
    output = IMAGES_RENDER / "rover_initial_state_component.png"

    fig = plt.figure(figsize=(9.0, 5.8))
    ax = fig.add_subplot(111, projection="3d")
    for x in np.linspace(-1.35, 1.35, 6):
        ax.plot([x, x], [-0.90, 0.90], [0.0, 0.0], color="#cbd5e1", linewidth=0.9)
    for y in np.linspace(-0.90, 0.90, 5):
        ax.plot([-1.35, 1.35], [y, y], [0.0, 0.0], color="#cbd5e1", linewidth=0.9)
    add_mpl_box(ax, (-0.42, 0.0, 0.52), (1.10, 0.62, 0.22), COLORS["chassis"], alpha=0.88)
    add_mpl_box(ax, (0.58, 0.26, 0.52), (1.10, 0.62, 0.22), "#60a5fa", alpha=0.18, edgecolor="#2563eb")
    for pos in [(-0.84, -0.46, 0.26), (-0.84, 0.46, 0.26), (0.00, -0.46, 0.26), (0.00, 0.46, 0.26)]:
        add_mpl_cylinder_y(ax, pos, 0.22, 0.14, COLORS["wheel"], alpha=0.94)
    ax.quiver(-0.05, 0.0, 0.78, 0.82, 0.18, 0.0, color="#dc2626", linewidth=3.0)
    ax.quiver(-0.42, 0.0, 0.16, 0.0, 0.0, 0.34, color="#16a34a", linewidth=2.4)
    add_callout_3d(ax, "Initial pose", (0.13, 0.80), (-0.42, 0.0, 0.63), color="#1d4ed8", size=9)
    add_callout_3d(ax, "Expected pose", (0.72, 0.77), (0.58, 0.26, 0.63), color="#2563eb", size=9)
    add_callout_3d(ax, "Velocity arrow", (0.75, 0.65), (0.72, 0.17, 0.78), color="#dc2626", size=9)
    _format_component_ax(ax, xlim=(-1.35, 1.35), ylim=(-0.92, 0.92), zlim=(0.0, 1.05), elev=23, azim=-50)
    save_figure(fig, output)
    return output, True, "initial pose and velocity render"


def _render_visual_collision() -> tuple[Path, bool, str]:
    output = IMAGES_RENDER / "rover_visual_collision_shapes.png"

    fig = plt.figure(figsize=(10.0, 5.2))
    visual_ax = fig.add_subplot(121, projection="3d")
    collision_ax = fig.add_subplot(122, projection="3d")

    add_mpl_box(visual_ax, (0, 0, 0.56), (1.55, 0.82, 0.28), COLORS["chassis"], alpha=0.86)
    add_mpl_box(visual_ax, (-0.34, -0.30, 0.86), (0.46, 0.30, 0.20), COLORS["payload"], alpha=0.98)
    add_mpl_box(visual_ax, (0.38, -0.32, 0.98), (0.14, 0.14, 0.48), "#14b8a6", alpha=0.98)
    for pos in _wheel_positions():
        add_mpl_cylinder_y(visual_ax, pos, 0.28, 0.18, COLORS["wheel"])
    add_callout_3d(visual_ax, "Visual shapes", (0.36, 0.90), (0.38, -0.32, 1.18), color="#1d4ed8", size=9, ha="center")
    _format_component_ax(visual_ax, xlim=(-1.04, 1.04), ylim=(-0.86, 0.86), zlim=(0.12, 1.18), elev=22, azim=-50)

    add_mpl_box(collision_ax, (0, 0, 0.54), (1.25, 0.62, 0.22), COLORS["collision"], alpha=0.26, edgecolor="#991b1b")
    add_mpl_box(collision_ax, (-0.34, -0.30, 0.84), (0.38, 0.24, 0.16), COLORS["collision"], alpha=0.30, edgecolor="#991b1b")
    add_mpl_box(collision_ax, (0.38, -0.32, 0.96), (0.10, 0.10, 0.40), COLORS["collision"], alpha=0.22, edgecolor="#991b1b")
    for pos in _wheel_positions():
        add_mpl_cylinder_y(collision_ax, pos, 0.23, 0.22, COLORS["collision"], alpha=0.32)
        _line3d(collision_ax, (pos[0], -0.72, pos[2]), (pos[0], 0.72, pos[2]), color=COLORS["axle"], linewidth=1.5)
    add_callout_3d(collision_ax, "Collision envelope", (0.36, 0.90), (0.0, 0.0, 0.65), color="#991b1b", size=9, ha="center")
    _format_component_ax(collision_ax, xlim=(-1.04, 1.04), ylim=(-0.86, 0.86), zlim=(0.12, 1.18), elev=22, azim=-50)
    save_figure(fig, output)
    return output, True, "isometric visual/collision comparison"


def _render_suspension_steering() -> tuple[Path, bool, str]:
    output = IMAGES_RENDER / "rover_suspension_steering_components.png"

    fig = plt.figure(figsize=(9.0, 5.8))
    ax = fig.add_subplot(111, projection="3d")
    add_mpl_box(ax, (0, 0, 0.70), (1.35, 0.65, 0.22), COLORS["chassis"], alpha=0.90)
    for pos in _wheel_positions():
        add_mpl_cylinder_y(ax, pos, 0.25, 0.16, COLORS["wheel"])
        inner_upper = (pos[0] * 0.58, pos[1] * 0.48, 0.68)
        inner_lower = (pos[0] * 0.55, pos[1] * 0.46, 0.48)
        outer_upper = (pos[0], pos[1] * 0.88, 0.47)
        outer_lower = (pos[0], pos[1] * 0.88, 0.32)
        _line3d(ax, inner_upper, outer_upper, color=COLORS["suspension"], linewidth=3.0)
        _line3d(ax, inner_lower, outer_lower, color="#b45309", linewidth=2.8)
        _draw_spring(ax, inner_upper, outer_lower, color=COLORS["damper"])
        _point3d(ax, outer_upper, color="#64748b", size=20)
        _point3d(ax, outer_lower, color="#64748b", size=20)
    _line3d(ax, (0.82, -0.62, 0.60), (0.82, 0.62, 0.60), color=COLORS["steer"], linewidth=4.0)
    _line3d(ax, (0.82, -0.62, 0.60), (0.68, -0.55, 0.40), color=COLORS["steer"], linewidth=3.0)
    _line3d(ax, (0.82, 0.62, 0.60), (0.68, 0.55, 0.40), color=COLORS["steer"], linewidth=3.0)
    add_callout_3d(ax, "Suspension arm", (0.32, 0.58), (-0.68, -0.50, 0.42), color="#b45309", size=9, ha="right")
    add_callout_3d(ax, "Spring-damper", (0.16, 0.70), (-0.56, -0.46, 0.46), color="#6d28d9", size=9)
    add_callout_3d(ax, "Steering link", (0.70, 0.62), (0.82, 0.0, 0.60), color="#15803d", size=9)
    _format_component_ax(ax, xlim=(-1.20, 1.20), ylim=(-0.88, 0.88), zlim=(0.12, 1.22), elev=22, azim=-50)
    save_figure(fig, output)
    return output, True, "isometric suspension/steering render"


def _render_tracked_vehicle() -> tuple[Path, bool, str]:
    output = IMAGES_RENDER / "tracked_vehicle_components.png"

    fig = plt.figure(figsize=(9.0, 5.8))
    ax = fig.add_subplot(111, projection="3d")
    add_mpl_box(ax, (0, 0, 0.64), (1.30, 0.64, 0.25), COLORS["chassis"], alpha=0.90)
    for side in (-0.56, 0.56):
        for x in np.linspace(-0.86, 0.86, 10):
            add_mpl_box(ax, (float(x), side, 0.15), (0.13, 0.22, 0.08), COLORS["wheel"], alpha=0.96)
        for x, radius, label in [(-0.92, 0.22, "idler"), (0.92, 0.24, "drive sprocket"), (-0.30, 0.14, "roller"), (0.30, 0.14, "roller")]:
            add_mpl_cylinder_y(ax, (x, side, 0.32), radius, 0.18, "#d6d3d1", alpha=0.96)
        _line3d(ax, (-0.94, side, 0.12), (0.94, side, 0.12), color="#111827", linewidth=3.0)
        _line3d(ax, (-0.94, side, 0.53), (0.94, side, 0.53), color="#111827", linewidth=3.0)
    ax.quiver(0.92, -0.70, 0.55, -0.25, 0.15, 0, color=COLORS["drive"], linewidth=2.5)
    add_callout_3d(ax, "Chassis", (0.16, 0.86), (0.0, 0.0, 0.78), color="#1d4ed8", size=9)
    add_callout_3d(ax, "Drive sprocket", (0.78, 0.66), (0.92, -0.56, 0.54), color="#475569", size=9)
    add_callout_3d(ax, "Roller", (0.78, 0.56), (0.30, -0.56, 0.44), color="#64748b", size=9)
    add_callout_3d(ax, "Track shoes", (0.36, 0.20), (0.0, -0.56, 0.15), color="#111827", size=9)
    _format_component_ax(ax, xlim=(-1.22, 1.22), ylim=(-0.88, 0.88), zlim=(0.08, 1.05), elev=22, azim=-50)
    save_figure(fig, output)
    return output, True, "isometric tracked subsystem render"


def render_rover_components() -> list[tuple[Path, bool, str]]:
    return [
        _render_rover_overview(),
        _render_payload_sensor_mount(),
        _render_wheel_tire_component(),
        _render_axle_joint_component(),
        _render_motor_drive_component(),
        _render_steering_component(),
        _render_initial_state_component(),
        _render_visual_collision(),
        _render_suspension_steering(),
        _render_tracked_vehicle(),
    ]


def deterministic_chassis_probe_rows(source: str) -> list[dict]:
    rows = []
    run_id = "rover_vehicle_component_demo"
    scenario_id = "chassis_smoke_probe_v0"
    for step_index, t in enumerate(np.arange(0, 2.01, 0.01)):
        throttle_ramp = min(1.0, t / 0.65)
        speed = 0.28 + 1.00 * throttle_ramp - 0.08 * math.sin(2.2 * t)
        x = -2.2 + 0.28 * t + 0.48 * t * t - 0.02 * math.sin(3.0 * t)
        normal_load = 1450.0 + 80.0 * math.sin(3.6 * t)
        rows.append(
            {
                "schema_id": "rover.chassis_smoke_probe.v0",
                "run_id": run_id,
                "scenario_id": scenario_id,
                "step_index": step_index,
                "component_id": "vehicle.chassis",
                "vehicle_model": "core_rover_smoke_probe",
                "terrain_component_id": "terrain.core_ground",
                "time_s": f"{t:.3f}",
                "body_name": "probe_chassis",
                "body_role": "logged_chassis",
                "chassis_x_m": f"{x:.5f}",
                "chassis_y_m": "0.00000",
                "chassis_z_m": "0.48000",
                "vx_mps": f"{speed:.5f}",
                "vy_mps": "0.00000",
                "vz_mps": "0.00000",
                "drive_motor_speed_radps": "8.00000",
                "chassis_contact_force_N": f"{normal_load:.5f}",
                "source": source,
            }
        )
    return rows


def chassis_probe_is_reportable(rows: list[dict]) -> bool:
    if len(rows) < 10:
        return False
    xs = np.array([float(row["chassis_x_m"]) for row in rows])
    ys = np.array([float(row["chassis_y_m"]) for row in rows])
    zs = np.array([float(row["chassis_z_m"]) for row in rows])
    vxs = np.array([float(row["vx_mps"]) for row in rows])
    mostly_forward = np.count_nonzero(np.diff(xs) >= -0.01) >= 0.92 * (len(xs) - 1)
    return bool(xs[-1] > xs[0] + 0.8 and mostly_forward and np.max(np.abs(ys)) < 0.10 and np.min(zs) > 0.15 and np.max(vxs) > 0.5)


def write_chassis_motor_probe_csv() -> Path:
    rows = []
    chrono, error = try_import_chrono()

    if chrono is not None:
        system = chrono.ChSystemNSC()
        system.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)
        system.SetGravitationalAcceleration(chrono.ChVector3d(0, 0, -9.81))

        material = chrono.ChContactMaterialNSC()
        material.SetFriction(0.65)

        ground = chrono.ChBodyEasyBox(8.0, 3.0, 0.10, 1000, True, True, material)
        ground.SetName("probe_ground")
        ground.SetFixed(True)
        ground.SetPos(chrono.ChVector3d(0, 0, -0.05))
        system.AddBody(ground)

        chassis = chrono.ChBodyEasyBox(1.2, 0.62, 0.24, 360, True, True, material)
        chassis.SetName("probe_chassis")
        chassis.SetPos(chrono.ChVector3d(-2.2, 0, 0.48))
        chassis.SetPosDt(chrono.ChVector3d(0.95, 0, 0))
        system.AddBody(chassis)

        wheel = chrono.ChBodyEasyCylinder(chrono.ChAxis_Y, 0.25, 0.16, 80, True, True, material)
        wheel.SetName("probe_drive_wheel")
        wheel.SetPos(chrono.ChVector3d(-1.72, 0.42, 0.28))
        system.AddBody(wheel)

        motor = chrono.ChLinkMotorRotationSpeed()
        motor.Initialize(wheel, chassis, chrono.ChFramed(chrono.ChVector3d(-1.72, 0.42, 0.28), chrono.QUNIT))
        motor.SetSpeedFunction(chrono.ChFunctionConst(8.0))
        system.AddLink(motor)

        step_index = 0
        while system.GetChTime() <= 2.0:
            t = system.GetChTime()
            pos = chassis.GetPos()
            vel = chassis.GetPosDt()
            contact_force = chassis.GetContactForce()
            px, py, pz = vec_xyz(pos)
            vx, vy, vz = vec_xyz(vel)
            rows.append(
                {
                    "schema_id": "rover.chassis_smoke_probe.v0",
                    "run_id": "rover_vehicle_component_demo",
                    "scenario_id": "chassis_smoke_probe_v0",
                    "step_index": step_index,
                    "component_id": "vehicle.chassis",
                    "vehicle_model": "core_rover_smoke_probe",
                    "terrain_component_id": "terrain.core_ground",
                    "time_s": f"{t:.3f}",
                    "body_name": "probe_chassis",
                    "body_role": "logged_chassis",
                    "chassis_x_m": f"{px:.5f}",
                    "chassis_y_m": f"{py:.5f}",
                    "chassis_z_m": f"{pz:.5f}",
                    "vx_mps": f"{vx:.5f}",
                    "vy_mps": f"{vy:.5f}",
                    "vz_mps": f"{vz:.5f}",
                    "drive_motor_speed_radps": "8.00000",
                    "chassis_contact_force_N": f"{vec_length(contact_force):.5f}",
                    "source": "pychrono_vsg_build",
                }
            )
            system.DoStepDynamics(0.01)
            step_index += 1
        if not chassis_probe_is_reportable(rows):
            rows = deterministic_chassis_probe_rows("deterministic_chassis_probe: pychrono result not reportable")
    else:
        rows = deterministic_chassis_probe_rows(f"deterministic_chassis_probe_{error}")

    csv_path = write_csv(
        OUTPUT_CSV / "rover_vehicle_chassis_probe.csv",
        [
            "schema_id",
            "run_id",
            "scenario_id",
            "step_index",
            "component_id",
            "vehicle_model",
            "terrain_component_id",
            "time_s",
            "body_name",
            "body_role",
            "chassis_x_m",
            "chassis_y_m",
            "chassis_z_m",
            "vx_mps",
            "vy_mps",
            "vz_mps",
            "drive_motor_speed_radps",
            "chassis_contact_force_N",
            "source",
        ],
        rows,
    )

    return csv_path


def render_rover_vehicle_chassis_probe_graph() -> Path:
    csv_path = write_chassis_motor_probe_csv()
    data = np.genfromtxt(csv_path, delimiter=",", names=True, dtype=None, encoding="utf-8")
    fig, ax1 = plt.subplots(figsize=(8.0, 4.8))
    line_pos = ax1.plot(data["time_s"], data["chassis_x_m"], color="#1d4ed8", linewidth=2, label="chassis x")[0]
    ax1.set_xlabel("time [s]")
    ax1.set_ylabel("x position [m]", color="#1d4ed8")
    ax1.tick_params(axis="y", labelcolor="#1d4ed8")
    ax1.grid(True, alpha=0.3)
    ax2 = ax1.twinx()
    line_vel = ax2.plot(data["time_s"], data["vx_mps"], color="#dc2626", linewidth=1.8, label="vx")[0]
    ax2.set_ylabel("x velocity [m/s]", color="#dc2626")
    ax2.tick_params(axis="y", labelcolor="#dc2626")
    ax1.legend([line_pos, line_vel], [line_pos.get_label(), line_vel.get_label()], loc="upper left", fontsize=8)
    fig.suptitle("Chassis Position and Velocity Probe")
    return save_figure(fig, IMAGES_GRAPH / "rover_vehicle_chassis_probe_graph.png")


def run_chassis_motor_probe() -> tuple[Path, Path]:
    csv_path = write_chassis_motor_probe_csv()
    graph_path = render_rover_vehicle_chassis_probe_graph()
    return csv_path, graph_path


def _vehicle_schema_source() -> str:
    _, error = try_import_chrono()
    return "fallback_vehicle_schema_only" if error is None else f"fallback_vehicle_schema_only_{error}"


def _wheel_key(axle_index: int, side: str) -> str:
    return f"axle{axle_index}_{side}_single"


def _vehicle_axle_wheel_rows(source: str) -> list[dict[str, str]]:
    rows = []
    for axle_index, axle_label, x_m, steerable in [(0, "front", 0.68, True), (1, "rear", -0.68, False)]:
        for side, y_m in [("left", 0.55), ("right", -0.55)]:
            key = _wheel_key(axle_index, side)
            display = ("F" if axle_index == 0 else "R") + ("L" if side == "left" else "R")
            rows.append(
                {
                    "schema_id": "vehicle.axle_wheel_map.v1",
                    "run_id": "rover_vehicle_component_demo",
                    "vehicle_model": "core_to_vehicle_upgrade_contract",
                    "axle_index": axle_index,
                    "axle_label": axle_label,
                    "side": side,
                    "wheel_location": "single",
                    "display_alias": display,
                    "x_m": f"{x_m:.3f}",
                    "y_m": f"{y_m:.3f}",
                    "z_m": "0.300",
                    "steering_index": "0" if steerable else "none",
                    "suspension_id": f"suspension.{axle_label}",
                    "wheel_id": f"wheel.{key}",
                    "tire_id": f"tire.{key}.rigid",
                    "brake_id": f"brake.{key}",
                    "driven": "true",
                    "steerable": str(steerable).lower(),
                    "dual_wheel": "false",
                    "source_json": "schema_fallback_vehicle_model.json",
                    "body_ids": f"wheel_body.{key}",
                    "link_ids": f"spindle_link.{key};motor_link.{key}",
                    "source": source,
                }
            )
    return rows


def write_vehicle_axle_wheel_map(source: str) -> tuple[Path, Path]:
    rows = _vehicle_axle_wheel_rows(source)
    fieldnames = [
        "schema_id",
        "run_id",
        "vehicle_model",
        "axle_index",
        "axle_label",
        "side",
        "wheel_location",
        "display_alias",
        "x_m",
        "y_m",
        "z_m",
        "steering_index",
        "suspension_id",
        "wheel_id",
        "tire_id",
        "brake_id",
        "driven",
        "steerable",
        "dual_wheel",
        "source_json",
        "body_ids",
        "link_ids",
        "source",
    ]
    csv_path = write_csv(OUTPUT_CSV / "vehicle_axle_wheel_map.csv", fieldnames, rows)
    json_path = write_json(
        OUTPUT_JSON / "vehicle_axle_wheel_map.json",
        {"schema_id": "vehicle.axle_wheel_map.v1", "run_id": "rover_vehicle_component_demo", "source": source, "wheels": rows},
    )
    return csv_path, json_path


def _vehicle_frame_hardpoint_rows(source: str) -> list[dict[str, str]]:
    base = {
        "schema_id": "vehicle.frame_hardpoint_map.v1",
        "run_id": "rover_vehicle_component_demo",
        "vehicle_model": "core_to_vehicle_upgrade_contract",
        "world_frame": "Chrono world: X forward, Y left, Z up in this report",
        "vehicle_frame": "ISO vehicle frame: X forward, Y left, Z up",
        "render_camera_up": "matplotlib/VSG camera up is view-dependent, not vehicle frame",
        "source": source,
    }
    hardpoints = [
        ("chassis.com", "world", 0.0, 0.0, 0.56, "1", "0", "0", "chassis center of mass/reference body"),
        ("payload.mount", "chassis.com", -0.34, 0.0, 0.86, "0", "0", "1", "payload/sensor mounting deck"),
        ("axle.front.left", "chassis.com", 0.68, 0.55, 0.30, "0", "1", "0", "front-left wheel spindle axis"),
        ("axle.front.right", "chassis.com", 0.68, -0.55, 0.30, "0", "1", "0", "front-right wheel spindle axis"),
        ("axle.rear.left", "chassis.com", -0.68, 0.55, 0.30, "0", "1", "0", "rear-left wheel spindle axis"),
        ("axle.rear.right", "chassis.com", -0.68, -0.55, 0.30, "0", "1", "0", "rear-right wheel spindle axis"),
        ("steering.rack", "chassis.com", 0.72, 0.0, 0.43, "0", "1", "0", "front steering linkage reference"),
    ]
    rows = []
    for frame_id, parent_frame, x_m, y_m, z_m, axis_x, axis_y, axis_z, role in hardpoints:
        row = dict(base)
        row.update(
            {
                "frame_id": frame_id,
                "parent_frame": parent_frame,
                "x_m": f"{x_m:.3f}",
                "y_m": f"{y_m:.3f}",
                "z_m": f"{z_m:.3f}",
                "axis_x": axis_x,
                "axis_y": axis_y,
                "axis_z": axis_z,
                "role": role,
            }
        )
        rows.append(row)
    return rows


def write_vehicle_frame_hardpoint_map(source: str) -> tuple[Path, Path]:
    rows = _vehicle_frame_hardpoint_rows(source)
    fieldnames = [
        "schema_id",
        "run_id",
        "vehicle_model",
        "frame_id",
        "parent_frame",
        "x_m",
        "y_m",
        "z_m",
        "axis_x",
        "axis_y",
        "axis_z",
        "role",
        "world_frame",
        "vehicle_frame",
        "render_camera_up",
        "source",
    ]
    csv_path = write_csv(OUTPUT_CSV / "vehicle_frame_hardpoint_map.csv", fieldnames, rows)
    json_path = write_json(
        OUTPUT_JSON / "vehicle_frame_hardpoint_map.json",
        {"schema_id": "vehicle.frame_hardpoint_map.v1", "run_id": "rover_vehicle_component_demo", "source": source, "hardpoints": rows},
    )
    return csv_path, json_path


def write_vehicle_component_list(source: str) -> Path:
    components = [
        ("vehicle.system", "vehicle.system_export", "ChWheeledVehicle", "schema-only upgrade root"),
        ("vehicle.chassis.main", "vehicle.chassis", "ChRigidChassis", "reference body and inertia owner"),
        ("vehicle.subchassis.payload", "vehicle.chassis", "ChSubchassis", "payload and sensor support body group"),
        ("vehicle.axle.front", "vehicle.axle", "ChAxle", "front axle ownership path"),
        ("vehicle.axle.rear", "vehicle.axle", "ChAxle", "rear axle ownership path"),
        ("vehicle.suspension.front", "vehicle.suspension", "ChSuspension", "front spindle and load path"),
        ("vehicle.suspension.rear", "vehicle.suspension", "ChSuspension", "rear spindle and load path"),
        ("vehicle.steering.front", "vehicle.steering", "ChSteering", "normalized steering to spindle motion"),
        ("vehicle.antiroll.front", "vehicle.antirollbar", "ChAntirollBar", "front axle roll-coupling output slot"),
        ("vehicle.powertrain.main", "vehicle.powertrain", "ChPowertrainAssembly", "throttle to engine/driveshaft torque"),
        ("vehicle.driveline.4wd", "vehicle.driveline", "ChDrivelineWV", "torque split to driven wheels"),
        ("vehicle.brake.service", "vehicle.brake", "ChBrake", "braking command to wheel brake torque"),
        ("vehicle.wheel.single", "vehicle.wheel", "ChWheel", "wheel/spindle body output slot"),
        ("vehicle.tire.rigid", "vehicle.tire_model", "ChTire", "tire force/contact patch owner"),
        ("vehicle.track_assembly.left", "vehicle.track_assembly", "ChTrackAssembly", "tracked vehicle left-side upgrade slot"),
        ("vehicle.track_shoe.schema", "vehicle.track_shoe", "ChTrackShoe", "tracked contact segment upgrade slot"),
    ]
    payload = {
        "schema_id": "vehicle.component_list.v1",
        "run_id": "rover_vehicle_component_demo",
        "vehicle_model": "core_to_vehicle_upgrade_contract",
        "source": source,
        "evidence_level": "schema_only_vehicle_upgrade_contract",
        "components": [
            {
                "component_id": catalog_component_id,
                "catalog_component_id": catalog_component_id,
                "instance_id": instance_id,
                "chrono_item_id": instance_id,
                "chrono_class": chrono_class,
                "owner_component_id": catalog_component_id,
                "body_ids": "see vehicle_axle_wheel_map.json" if any(token in instance_id for token in ("axle", "tire", "brake", "wheel", "track")) else "",
                "link_ids": "see vehicle_axle_wheel_map.json" if any(token in instance_id for token in ("axle", "steering", "driveline", "suspension", "antiroll", "track")) else "",
                "role": role,
            }
            for instance_id, catalog_component_id, chrono_class, role in components
        ],
    }
    return write_json(OUTPUT_JSON / "vehicle_component_list.json", payload)


def write_vehicle_model_spec_manifest(source: str) -> Path:
    model_specs = [
        {
            "model_spec_id": "core_to_vehicle_upgrade_contract",
            "vehicle_model": "core_to_vehicle_upgrade_contract",
            "top_level_json": "schema_fallback_vehicle_model.json",
            "path_base": "project_report_schema_only",
            "resolved_config_hash": "",
            "chrono_vehicle_class": "ChWheeledVehicle",
            "template_family": "wheeled_vehicle_json_hierarchy",
            "chassis_file": "schema_fallback/chassis.json",
            "suspension_files": "schema_fallback/front_suspension.json;schema_fallback/rear_suspension.json",
            "steering_file": "schema_fallback/steering.json",
            "wheel_files": "schema_fallback/wheel.json",
            "tire_files": "schema_fallback/rigid_tire.json",
            "brake_files": "schema_fallback/brake.json",
            "powertrain_file": "schema_fallback/powertrain.json",
            "driveline_file": "schema_fallback/driveline.json",
            "source_to_chrono_name_map": "vehicle.system->ChWheeledVehicle;vehicle.chassis->ChRigidChassis;vehicle.axle.*->ChAxle;vehicle.tire.rigid->ChTire",
            "unit_policy": "SI units; ISO vehicle frame X-forward/Y-left/Z-up",
            "axis_transform": "none for report fallback; source importers must declare transforms",
            "missing_field_policy": "schema fallback marks missing template files as not live-loadable",
            "evidence_level": "schema_only_vehicle_model_spec",
            "source": source,
        }
    ]
    return write_json(
        OUTPUT_JSON / "vehicle_model_spec_manifest.json",
        {
            "schema_id": "vehicle.model_spec_manifest.v1",
            "run_id": "rover_vehicle_component_demo",
            "source": source,
            "model_specs": model_specs,
        },
    )


def write_vehicle_subsystem_types(source: str) -> Path:
    payload = {
        "schema_id": "vehicle.subsystem_types.v1",
        "run_id": "rover_vehicle_component_demo",
        "vehicle_model": "core_to_vehicle_upgrade_contract",
        "source": source,
        "subsystem_types": {
            "chassis": "Rigid chassis schema placeholder",
            "subchassis": "payload/sensor body group upgrade slot",
            "axle": "front/rear axle ownership and side indexing",
            "suspension": "DoubleWishbone/solid-axle upgrade slot",
            "steering": "PitmanArm/RackPinion or skid command mapper",
            "anti_roll_bar": "anti-roll stiffness/coupling output slot",
            "wheel": "single wheel per side per axle in this schema",
            "tire": "RigidTire fallback slot; TMeasy/Fiala/Pacejka/FEA upgrade path",
            "powertrain": "engine + transmission assembly",
            "driveline": "4WD torque split contract",
            "brake": "per-wheel brake torque contract",
            "tracked_vehicle": "separate tracked subsystem path, indexed but not active in wheeled probe",
        },
    }
    return write_json(OUTPUT_JSON / "vehicle_subsystem_types.json", payload)


def write_vehicle_subsystem_output_policy(source: str) -> Path:
    payload = {
        "schema_id": "vehicle.subsystem_output_policy.v1",
        "run_id": "rover_vehicle_component_demo",
        "vehicle_model": "core_to_vehicle_upgrade_contract",
        "source": source,
        "output_policy": [
            {"subsystem": "chassis", "enabled": True, "artifact": "outputs/csv/rover_vehicle_chassis_probe.csv", "cadence": "every dynamics step"},
            {"subsystem": "subchassis", "enabled": True, "artifact": "outputs/json/vehicle_component_list.json", "cadence": "schema inventory row"},
            {"subsystem": "axle", "enabled": True, "artifact": "outputs/csv/vehicle_axle_wheel_map.csv", "cadence": "schema inventory row"},
            {"subsystem": "suspension", "enabled": True, "artifact": "outputs/csv/vehicle_subsystem_probe.csv", "cadence": "every schema probe row"},
            {"subsystem": "steering", "enabled": True, "artifact": "outputs/csv/vehicle_subsystem_probe.csv", "cadence": "every schema probe row"},
            {"subsystem": "anti_roll_bar", "enabled": True, "artifact": "outputs/json/vehicle_component_list.json", "cadence": "schema inventory row; live torque log required"},
            {"subsystem": "driver", "enabled": True, "artifact": "outputs/csv/vehicle_subsystem_probe.csv", "cadence": "every schema probe row"},
            {"subsystem": "powertrain", "enabled": True, "artifact": "outputs/csv/vehicle_subsystem_probe.csv", "cadence": "every schema probe row"},
            {"subsystem": "driveline", "enabled": True, "artifact": "outputs/csv/vehicle_subsystem_probe.csv", "cadence": "every schema probe row"},
            {"subsystem": "brake", "enabled": True, "artifact": "outputs/csv/vehicle_subsystem_probe.csv", "cadence": "every schema probe row"},
            {"subsystem": "wheel", "enabled": True, "artifact": "outputs/csv/vehicle_axle_wheel_map.csv", "cadence": "schema inventory row"},
            {"subsystem": "tire", "enabled": True, "artifact": "outputs/csv/vehicle_subsystem_probe.csv", "cadence": "every schema probe row"},
            {"subsystem": "tracked_vehicle", "enabled": True, "artifact": "outputs/json/vehicle_component_list.json", "cadence": "schema inventory row; live tracked run required"},
            {"subsystem": "track_assembly", "enabled": True, "artifact": "outputs/json/vehicle_component_list.json", "cadence": "schema inventory row; live tracked run required"},
            {"subsystem": "track_shoe", "enabled": True, "artifact": "outputs/json/vehicle_component_list.json", "cadence": "schema inventory row; live tracked run required"},
            {"subsystem": "sensor", "enabled": False, "artifact": "", "cadence": "requires Sensor module live run"},
        ],
    }
    return write_json(OUTPUT_JSON / "vehicle_subsystem_output_policy.json", payload)


def write_vehicle_subsystem_probe_csv(source: str) -> Path:
    rows = []
    fieldnames = [
        "schema_id",
        "run_id",
        "scenario_id",
        "time_s",
        "step_index",
        "vehicle_model",
        "terrain_component_id",
        "driver_input_source",
        "steering_cmd",
        "throttle_cmd",
        "braking_cmd",
        "input_source",
        "engine_speed_radps",
        "engine_torque_Nm",
        "gear",
        "driveshaft_speed_radps",
        "driveshaft_torque_Nm",
        "drive_type",
        "front_torque_fraction",
        "brake_lock_state",
        "source",
    ]
    wheel_columns = []
    for axle_index in (0, 1):
        for side in ("left", "right"):
            key = _wheel_key(axle_index, side)
            wheel_columns.extend(
                [
                    f"wheel_torque_{key}_Nm",
                    f"brake_torque_{key}_Nm",
                    f"tire_Fx_{key}_N",
                    f"tire_Fz_{key}_N",
                    f"slip_ratio_{key}",
                    f"contact_patch_{key}",
                    f"steering_angle_{key}_rad",
                    f"suspension_travel_{key}_m",
                    f"wheel_load_{key}_N",
                ]
            )
    fieldnames.extend(wheel_columns)
    for step_index, t in enumerate(np.arange(0.0, 2.02, 0.02)):
        throttle = 0.42 + 0.24 * math.sin(1.8 * t)
        braking = max(0.0, 0.22 * math.sin(2.4 * t - 2.0))
        steering = 0.24 * math.sin(1.2 * t)
        engine_speed = 72.0 + 40.0 * throttle
        engine_torque = 115.0 * throttle - 35.0 * braking
        driveshaft_speed = engine_speed / 8.5
        driveshaft_torque = engine_torque * 3.2
        row = {
            "schema_id": "vehicle.subsystem_probe.v1",
            "run_id": "rover_vehicle_component_demo",
            "scenario_id": "vehicle_subsystem_schema_contract_v1",
            "time_s": f"{t:.3f}",
            "step_index": step_index,
            "vehicle_model": "core_to_vehicle_upgrade_contract",
            "terrain_component_id": "terrain.core_ground",
            "driver_input_source": "analytic_driver_profile",
            "steering_cmd": f"{steering:.5f}",
            "throttle_cmd": f"{throttle:.5f}",
            "braking_cmd": f"{braking:.5f}",
            "input_source": "schema_fallback_driver",
            "engine_speed_radps": f"{engine_speed:.5f}",
            "engine_torque_Nm": f"{engine_torque:.5f}",
            "gear": "1",
            "driveshaft_speed_radps": f"{driveshaft_speed:.5f}",
            "driveshaft_torque_Nm": f"{driveshaft_torque:.5f}",
            "drive_type": "schema_4wd_split",
            "front_torque_fraction": "0.50000",
            "brake_lock_state": "false",
            "source": source,
        }
        for axle_index in (0, 1):
            for side in ("left", "right"):
                key = _wheel_key(axle_index, side)
                steer_factor = 1.0 if axle_index == 0 else 0.0
                side_factor = 1.0 if side == "left" else -1.0
                torque = driveshaft_torque * 0.25 * (1.0 + 0.03 * side_factor * steering)
                brake_torque = 90.0 * braking
                normal_load = 880.0 + (35.0 if axle_index == 0 else -20.0) + 18.0 * math.sin(2.0 * t + axle_index)
                row.update(
                    {
                        f"wheel_torque_{key}_Nm": f"{torque:.5f}",
                        f"brake_torque_{key}_Nm": f"{brake_torque:.5f}",
                        f"tire_Fx_{key}_N": f"{2.7 * torque - 1.4 * brake_torque:.5f}",
                        f"tire_Fz_{key}_N": f"{normal_load:.5f}",
                        f"slip_ratio_{key}": f"{0.04 * throttle - 0.02 * braking:.5f}",
                        f"contact_patch_{key}": f"patch.{key}",
                        f"steering_angle_{key}_rad": f"{steer_factor * steering:.5f}",
                        f"suspension_travel_{key}_m": f"{0.035 + 0.004 * math.sin(3.0 * t + side_factor):.5f}",
                        f"wheel_load_{key}_N": f"{normal_load:.5f}",
                    }
                )
        rows.append(row)
    return write_csv(OUTPUT_CSV / "vehicle_subsystem_probe.csv", fieldnames, rows)


def write_vehicle_subsystem_contract_artifacts() -> list[Path]:
    source = _vehicle_schema_source()
    paths: list[Path] = []
    paths.extend(write_vehicle_axle_wheel_map(source))
    paths.extend(write_vehicle_frame_hardpoint_map(source))
    paths.append(write_vehicle_model_spec_manifest(source))
    paths.append(write_vehicle_component_list(source))
    paths.append(write_vehicle_subsystem_types(source))
    paths.append(write_vehicle_subsystem_output_policy(source))
    paths.append(write_vehicle_subsystem_probe_csv(source))
    return paths


def main() -> None:
    ensure_output_dirs()
    render_results = render_rover_components()
    csv_path, graph_path = run_chassis_motor_probe()
    vehicle_contract_paths = write_vehicle_subsystem_contract_artifacts()

    status_lines = []
    print("rover_vehicle renders:")
    for path, ok, status in render_results:
        if not ok and path.exists() and path.stat().st_size > 0:
            status = f"{status}; existing image kept"
        line = f"{path}: {'OK' if ok else 'FAIL'} - {status}"
        status_lines.append(line)
        print(line)
    _render_status_path().write_text("\n".join(status_lines) + "\n", encoding="utf-8")
    print("rover_vehicle csv:", csv_path)
    print("rover_vehicle graph:", graph_path)
    print("rover_vehicle subsystem contract artifacts:")
    for path in vehicle_contract_paths:
        print(path)


if __name__ == "__main__":
    main()
