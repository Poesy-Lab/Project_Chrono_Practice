from __future__ import annotations

import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle

sys.path.append(str(Path(__file__).resolve().parent))

from component_utils import IMAGES_RENDER, save_figure  # noqa: E402


def _leader(ax, text, xytext, xy, *, color, ha="center"):
    ax.annotate(
        text,
        xy=xy,
        xytext=xytext,
        ha=ha,
        va="center",
        fontsize=7.4,
        color=color,
        bbox={"boxstyle": "round,pad=0.15", "facecolor": "white", "edgecolor": color, "linewidth": 0.9},
        arrowprops={"arrowstyle": "-", "color": color, "linewidth": 0.9, "shrinkA": 2, "shrinkB": 1},
        zorder=30,
    )


def _arrow(ax, start, end, *, color="#475569", width=0.95, rad=0.0):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=10,
            linewidth=width,
            color=color,
            connectionstyle=f"arc3,rad={rad}",
            shrinkA=3,
            shrinkB=3,
            zorder=14,
        )
    )


def _sheet(ax, x, y, *, edge, title, rows):
    card = FancyBboxPatch(
        (x, y),
        1.08,
        0.68,
        boxstyle="round,pad=0.018,rounding_size=0.03",
        facecolor="white",
        edgecolor=edge,
        linewidth=1.0,
        zorder=8,
    )
    ax.add_patch(card)
    ax.text(x + 0.54, y + 0.55, title, ha="center", va="center", fontsize=6.0, color=edge, weight="bold", zorder=9)
    for idx, row in enumerate(rows):
        yy = y + 0.38 - idx * 0.13
        ax.plot([x + 0.11, x + 0.96], [yy, yy], color="#cbd5e1", linewidth=0.5, zorder=9)
        ax.text(x + 0.12, yy - 0.055, row, ha="left", va="center", fontsize=4.9, color="#334155", zorder=9)
    return x + 0.54, y + 0.34


def _graph(ax, x, y):
    ax.add_patch(Rectangle((x, y), 0.92, 0.58, facecolor="white", edgecolor="#0f766e", linewidth=1.0, zorder=8))
    ax.plot([x + 0.12, x + 0.12], [y + 0.12, y + 0.48], color="#94a3b8", linewidth=0.55, zorder=9)
    ax.plot([x + 0.12, x + 0.80], [y + 0.12, y + 0.12], color="#94a3b8", linewidth=0.55, zorder=9)
    ax.plot([x + 0.18, x + 0.32, x + 0.47, x + 0.66, x + 0.78], [y + 0.18, y + 0.36, y + 0.29, y + 0.22, y + 0.16], color="#dc2626", linewidth=1.3, zorder=10)
    ax.text(x + 0.50, y + 0.48, "Graph", ha="center", va="center", fontsize=5.5, color="#0f766e", weight="bold", zorder=10)
    return x + 0.46, y + 0.29


def _json_card(ax, x, y):
    ax.add_patch(Rectangle((x, y), 1.08, 0.62, facecolor="#f8fafc", edgecolor="#7c3aed", linewidth=1.0, zorder=8))
    ax.text(x + 0.14, y + 0.42, "{", ha="center", va="center", fontsize=13, color="#7c3aed", weight="bold", zorder=9)
    for idx, row in enumerate(["dt_s", "modules", "hash"]):
        ax.text(x + 0.32, y + 0.42 - idx * 0.15, row, ha="left", va="center", fontsize=5.4, color="#334155", zorder=9)
    ax.text(x + 0.54, y + 0.56, "Metadata JSON", ha="center", va="center", fontsize=5.5, color="#7c3aed", weight="bold", zorder=10)
    return x + 0.54, y + 0.31


def _tile(ax, x, y, *, edge, title, kind):
    ax.add_patch(Rectangle((x, y), 1.08, 0.68, facecolor="white", edgecolor=edge, linewidth=1.0, zorder=8))
    ax.add_patch(Rectangle((x + 0.12, y + 0.13), 0.84, 0.39, facecolor="#e0f2fe", edgecolor="#64748b", linewidth=0.55, zorder=9))
    if kind == "render":
        ax.add_patch(Rectangle((x + 0.24, y + 0.25), 0.32, 0.14, facecolor="#93c5fd", edgecolor="#1d4ed8", linewidth=0.55, zorder=10))
        ax.add_patch(Rectangle((x + 0.66, y + 0.19), 0.10, 0.30, facecolor="#fca5a5", edgecolor="#991b1b", linewidth=0.55, zorder=10))
    elif kind == "camera":
        ax.plot([x + 0.24, x + 0.78], [y + 0.26, y + 0.42], color="#f59e0b", linewidth=1.0, zorder=10)
        ax.plot([x + 0.24, x + 0.78], [y + 0.42, y + 0.24], color="#22c55e", linewidth=1.0, zorder=10)
    else:
        for dx, dy in [(0.20, 0.20), (0.36, 0.40), (0.52, 0.25), (0.68, 0.44), (0.80, 0.28)]:
            ax.add_patch(Circle((x + dx, y + dy), 0.025, facecolor="#22d3ee", edgecolor="#0e7490", linewidth=0.45, zorder=10))
    ax.text(x + 0.54, y + 0.58, title, ha="center", va="center", fontsize=5.6, color=edge, weight="bold", zorder=10)
    return x + 0.54, y + 0.34


def _scene(ax):
    # Runtime/config frame around the physical scene.
    outer = FancyBboxPatch(
        (2.14, 0.98),
        5.86,
        4.48,
        boxstyle="round,pad=0.03,rounding_size=0.055",
        facecolor="#f8fafc",
        edgecolor="#334155",
        linewidth=1.35,
        zorder=1,
    )
    ax.add_patch(outer)
    ax.add_patch(Rectangle((2.46, 1.30), 5.20, 0.13, facecolor="#d1d5db", edgecolor="#64748b", linewidth=0.9, zorder=3))
    ax.add_patch(Rectangle((2.76, 1.43), 1.34, 0.12, facecolor="#fef3c7", edgecolor="#d97706", linewidth=0.7, zorder=4))
    ax.add_patch(Rectangle((4.30, 1.43), 1.24, 0.12, facecolor="#dcfce7", edgecolor="#16a34a", linewidth=0.7, zorder=4))
    ax.add_patch(Rectangle((5.92, 1.43), 1.00, 0.20, facecolor="#dbeafe", edgecolor="#2563eb", linewidth=0.7, zorder=4))

    # Rover chassis, collision envelope, wheels, axle, motor, steering/suspension.
    ax.add_patch(Rectangle((3.42, 2.48), 1.72, 0.58, facecolor="#93c5fd", edgecolor="#1d4ed8", linewidth=1.45, zorder=7))
    ax.add_patch(Rectangle((3.30, 2.38), 1.98, 0.78, fill=False, edgecolor="#dc2626", linewidth=1.3, linestyle="--", zorder=9))
    ax.plot([3.74, 5.04], [2.42, 2.42], color="#64748b", linewidth=2.2, zorder=8)
    ax.add_patch(Circle((3.82, 2.16), 0.22, facecolor="#111827", edgecolor="#111827", zorder=9))
    ax.add_patch(Circle((5.02, 2.16), 0.22, facecolor="#111827", edgecolor="#111827", zorder=9))
    ax.add_patch(Circle((5.02, 2.16), 0.080, facecolor="#f97316", edgecolor="#9a3412", zorder=10))
    ax.add_patch(Rectangle((5.08, 2.25), 0.22, 0.14, facecolor="#fed7aa", edgecolor="#f97316", linewidth=0.8, zorder=10))
    ax.plot([4.60, 5.02], [2.62, 2.16], color="#64748b", linewidth=1.55, zorder=10)
    ax.plot([3.82, 4.22], [2.16, 2.60], color="#64748b", linewidth=1.55, zorder=10)

    # Obstacle/contact.
    ax.add_patch(Rectangle((5.82, 1.72), 0.28, 1.22, facecolor="#fca5a5", edgecolor="#991b1b", linewidth=1.2, zorder=6))
    for yy in (2.22, 2.50):
        ax.add_patch(Circle((5.78, yy), 0.055, facecolor="#facc15", edgecolor="#854d0e", linewidth=0.7, zorder=12))

    # Sensor mast/camera/lidar/IMU.
    ax.add_patch(Rectangle((4.58, 3.06), 0.09, 0.72, facecolor="#0f766e", edgecolor="#134e4a", linewidth=0.9, zorder=8))
    ax.add_patch(Rectangle((4.42, 3.78), 0.42, 0.18, facecolor="#dc2626", edgecolor="#7f1d1d", linewidth=0.9, zorder=9))
    ax.add_patch(Circle((4.64, 3.56), 0.065, facecolor="#16a34a", edgecolor="#14532d", linewidth=0.7, zorder=10))
    for angle in (-0.35, -0.18, 0.0, 0.18, 0.35):
        ax.plot([4.65, 6.18], [3.58, 3.58 + 0.74 * math.sin(angle)], color="#f59e0b", linewidth=1.0, zorder=7)
    ax.plot([4.84, 6.82], [3.87, 4.64], color="#dc2626", linewidth=1.1, linestyle="--", zorder=7)

    ax.text(5.05, 5.24, "runtime/config frame", ha="center", va="center", fontsize=7.2, color="#334155", weight="bold", zorder=12)
    return {
        "runtime_corner": (2.15, 5.43),
        "system_frame": (7.96, 5.43),
        "chassis": (4.28, 2.77),
        "wheel": (5.02, 2.16),
        "axle": (4.36, 2.42),
        "motor": (5.16, 2.32),
        "steering": (4.07, 2.40),
        "terrain": (4.92, 1.48),
        "material": (3.40, 1.49),
        "obstacle": (5.98, 2.64),
        "collision": (5.28, 3.15),
        "contact": (5.78, 2.50),
        "camera": (4.64, 3.87),
        "lidar_origin": (4.65, 3.58),
        "lidar_ray": (5.58, 3.70),
        "imu": (4.64, 3.56),
        "render_ray": (6.82, 4.64),
    }


def render_component_catalog_atlas() -> Path:
    output = IMAGES_RENDER / "component_catalog_atlas.png"
    fig, ax = plt.subplots(figsize=(11.8, 6.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.2)
    ax.axis("off")

    ax.text(5.0, 5.98, "Project Chrono component catalog atlas", ha="center", va="center", fontsize=13.0, weight="bold", color="#111827")
    ax.text(5.0, 5.72, "One scene, many component cards: choose the owned responsibility, then open the matching 2.2 section and evidence artifacts.", ha="center", va="center", fontsize=8.1, color="#475569")

    anchors = _scene(ax)

    state_xy = _sheet(ax, 0.40, 4.46, edge="#2563eb", title="State CSV", rows=["time_s x_m", "body_name", "source"])
    control_xy = _sheet(ax, 0.40, 3.42, edge="#16a34a", title="Control CSV", rows=["throttle", "brake", "steering"])
    contact_xy = _sheet(ax, 0.40, 2.38, edge="#dc2626", title="Contact CSV", rows=["body_a body_b", "count force", "normal frame"])
    graph_xy = _graph(ax, 0.47, 1.20)
    metadata_xy = _json_card(ax, 8.55, 4.54)
    render_xy = _tile(ax, 8.55, 3.45, edge="#2563eb", title="Render PNG", kind="render")
    camera_xy = _tile(ax, 8.55, 2.36, edge="#dc2626", title="Camera", kind="camera")
    cloud_xy = _tile(ax, 8.55, 1.27, edge="#0891b2", title="LiDAR", kind="cloud")

    ax.text(0.94, 5.34, "CSV / graph rail", ha="center", va="center", fontsize=6.6, color="#475569", weight="bold")
    ax.text(9.09, 5.34, "Artifact rail", ha="center", va="center", fontsize=6.6, color="#475569", weight="bold")

    left_ports = {
        "state": (2.06, 4.68),
        "control": (2.06, 3.45),
        "contact": (2.06, 2.68),
        "graph": (2.06, 1.50),
    }
    right_ports = {
        "metadata": (8.10, 4.88),
        "render": (8.10, 3.78),
        "camera": (8.10, 2.70),
        "cloud": (8.10, 1.66),
    }
    ax.plot([2.06, 2.06], [1.44, 4.92], color="#94a3b8", linewidth=1.0, zorder=13)
    ax.plot([8.10, 8.10], [1.60, 4.96], color="#94a3b8", linewidth=1.0, zorder=13)
    for xy, color in [
        (left_ports["state"], "#2563eb"),
        (left_ports["control"], "#16a34a"),
        (left_ports["contact"], "#dc2626"),
        (left_ports["graph"], "#0f766e"),
        (right_ports["metadata"], "#7c3aed"),
        (right_ports["render"], "#2563eb"),
        (right_ports["camera"], "#dc2626"),
        (right_ports["cloud"], "#0891b2"),
    ]:
        ax.add_patch(Circle(xy, 0.045, facecolor="#ffffff", edgecolor=color, linewidth=1.0, zorder=16))

    _arrow(ax, left_ports["state"], state_xy, color="#2563eb", rad=0.05)
    _arrow(ax, left_ports["control"], control_xy, color="#16a34a", rad=-0.05)
    _arrow(ax, left_ports["contact"], contact_xy, color="#dc2626", rad=-0.05)
    _arrow(ax, left_ports["graph"], graph_xy, color="#0f766e")
    _arrow(ax, right_ports["metadata"], metadata_xy, color="#7c3aed", rad=-0.03)
    _arrow(ax, right_ports["render"], render_xy, color="#2563eb", rad=0.03)
    _arrow(ax, right_ports["camera"], camera_xy, color="#dc2626", rad=0.03)
    _arrow(ax, right_ports["cloud"], cloud_xy, color="#0891b2", rad=-0.03)

    _leader(ax, "Runtime /\nConfig", (2.06, 5.24), anchors["runtime_corner"], color="#334155", ha="right")
    _leader(ax, "ChSystem /\nsolver", (6.95, 5.10), anchors["system_frame"], color="#334155", ha="left")
    _leader(ax, "Chassis", (2.64, 3.14), anchors["chassis"], color="#2563eb", ha="left")
    _leader(ax, "Wheel /\nTire", (5.62, 2.06), anchors["wheel"], color="#111827", ha="left")
    _leader(ax, "Axle /\nJoint", (2.70, 2.42), anchors["axle"], color="#64748b", ha="left")
    _leader(ax, "Motor /\nDrive", (5.52, 1.12), anchors["motor"], color="#f97316")
    _leader(ax, "Steering /\nSuspension", (2.74, 3.84), anchors["steering"], color="#64748b", ha="left")
    _leader(ax, "Ground /\nTerrain", (5.20, 0.70), anchors["terrain"], color="#16a34a")
    _leader(ax, "Contact\nMaterial", (3.28, 0.92), anchors["material"], color="#d97706")
    _leader(ax, "Obstacle", (6.72, 2.36), anchors["obstacle"], color="#991b1b")
    _leader(ax, "Collision\nShape", (5.92, 3.30), anchors["collision"], color="#dc2626")
    _leader(ax, "Contact Reporter /\nForce Logger", (6.58, 2.98), anchors["contact"], color="#854d0e")
    _leader(ax, "Camera", (3.34, 4.26), anchors["camera"], color="#dc2626", ha="left")
    _leader(ax, "LiDAR\nrays", (6.78, 4.22), anchors["lidar_ray"], color="#b45309")
    _leader(ax, "IMU /\nGPS", (4.42, 4.56), anchors["imu"], color="#16a34a")
    ax.add_patch(Rectangle((2.80, 0.17), 4.52, 0.34, facecolor="#f8fafc", edgecolor="#cbd5e1", linewidth=0.8, zorder=1))
    ax.text(
        5.00,
        0.34,
        "Indexed extensions: VehicleCosim, ROS, FMI/FMU, Parsers/URDF/YAML/CAD, FEA/FSI/DEM/CRM, Multicore",
        ha="center",
        va="center",
        fontsize=6.6,
        color="#475569",
        zorder=2,
    )
    ax.text(
        5.0,
        0.055,
        "Atlas rule: official modules are availability boundaries; component cards own responsibilities, metadata, outputs, validation, and upgrade paths.",
        ha="center",
        va="center",
        fontsize=7.5,
        color="#475569",
    )
    return save_figure(fig, output)


if __name__ == "__main__":
    print(render_component_catalog_atlas())
