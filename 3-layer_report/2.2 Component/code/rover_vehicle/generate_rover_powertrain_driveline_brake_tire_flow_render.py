from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle

sys.path.append(str(Path(__file__).resolve().parents[1] / "common"))

from component_utils import IMAGES_RENDER, save_figure  # noqa: E402


def _box(ax, xy, size, label, *, face, edge, fontsize=8.2, weight="normal", linestyle="-"):
    patch = FancyBboxPatch(
        xy,
        size[0],
        size[1],
        boxstyle="round,pad=0.025,rounding_size=0.045",
        facecolor=face,
        edgecolor=edge,
        linestyle=linestyle,
        linewidth=1.35,
        zorder=4,
    )
    ax.add_patch(patch)
    ax.text(
        xy[0] + size[0] / 2,
        xy[1] + size[1] / 2,
        label,
        ha="center",
        va="center",
        fontsize=fontsize,
        color="#111827",
        weight=weight,
        zorder=5,
    )
    return patch


def _arrow(ax, start, end, *, color="#475569", width=1.35, rad=0.0, style="-|>"):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle=style,
            mutation_scale=12,
            linewidth=width,
            color=color,
            connectionstyle=f"arc3,rad={rad}",
            shrinkA=3,
            shrinkB=3,
            zorder=3,
        )
    )


def _label(ax, text, xytext, xy, *, color, ha="center"):
    ax.annotate(
        text,
        xy=xy,
        xytext=xytext,
        ha=ha,
        va="center",
        fontsize=7.7,
        color=color,
        bbox={"boxstyle": "round,pad=0.18", "facecolor": "white", "edgecolor": color, "linewidth": 0.9},
        arrowprops={"arrowstyle": "-", "color": color, "linewidth": 0.95, "shrinkA": 2, "shrinkB": 2},
        zorder=9,
    )


def _wheel(ax, center):
    ax.add_patch(Circle(center, 0.28, facecolor="#111827", edgecolor="#020617", linewidth=1.0, zorder=4))
    ax.add_patch(Circle(center, 0.14, facecolor="#e5e7eb", edgecolor="#64748b", linewidth=1.0, zorder=5))
    ax.add_patch(Rectangle((center[0] - 0.22, center[1] - 0.43), 0.44, 0.06, facecolor="#fed7aa", edgecolor="#ea580c", linewidth=1.0, zorder=5))


def render_rover_powertrain_driveline_brake_tire_flow() -> Path:
    output = IMAGES_RENDER / "rover_powertrain_driveline_brake_tire_flow.png"
    fig, ax = plt.subplots(figsize=(12.5, 6.8))
    ax.set_xlim(0, 10.8)
    ax.set_ylim(0, 6.2)
    ax.axis("off")

    ax.text(5.0, 5.94, "Chrono::Vehicle torque path component catalog", ha="center", va="center", fontsize=12.8, color="#111827", weight="bold")
    ax.text(5.0, 0.10, "Catalog view: driver commands are not wheel forces until powertrain, driveline, brake, tire, and terrain contracts are applied.", ha="center", va="center", fontsize=8.2, color="#475569")

    _box(ax, (0.45, 4.90), (1.85, 0.52), "DriverInputs\nthrottle / braking", face="#f8fafc", edge="#334155", fontsize=7.9, weight="bold")
    _box(ax, (3.00, 4.72), (2.08, 0.72), "Powertrain\nengine + transmission", face="#fef3c7", edge="#d97706", fontsize=8.5, weight="bold")
    _box(ax, (5.86, 4.72), (2.08, 0.72), "Driveline\nsplit + differential", face="#e0f2fe", edge="#0284c7", fontsize=8.5, weight="bold")
    _box(ax, (8.42, 4.90), (1.18, 0.52), "Vehicle\naxles", face="#eff6ff", edge="#2563eb", fontsize=7.9, weight="bold")

    _arrow(ax, (2.30, 5.16), (3.00, 5.16), color="#334155")
    _label(ax, "throttle\n[0,1]", (2.56, 5.58), (2.95, 5.17), color="#334155")
    _arrow(ax, (5.08, 5.08), (5.86, 5.08), color="#d97706")
    _label(ax, "driveshaft torque\nand speed feedback", (5.45, 5.56), (5.46, 5.08), color="#d97706")
    _arrow(ax, (7.94, 5.08), (8.42, 5.08), color="#0284c7")
    _label(ax, "wheel axle torque\nand angular speed", (8.28, 5.56), (8.16, 5.08), color="#0284c7", ha="left")

    ax.add_patch(Rectangle((1.05, 1.34), 7.85, 0.18, facecolor="#e2e8f0", edgecolor="#64748b", linewidth=1.0, zorder=1))
    ax.add_patch(FancyBboxPatch((1.28, 2.80), 6.70, 0.58, boxstyle="round,pad=0.025,rounding_size=0.06", facecolor="#dbeafe", edgecolor="#2563eb", linewidth=1.2, zorder=3))
    ax.text(4.63, 3.09, "chassis reference frame: X forward, Y left, Z up", ha="center", va="center", fontsize=8.2, color="#1e3a8a", weight="bold", zorder=4)

    wheel_points = {
        "front_left": (2.04, 2.22),
        "front_right": (2.04, 1.72),
        "rear_left": (6.96, 2.22),
        "rear_right": (6.96, 1.72),
    }
    for label, center in wheel_points.items():
        _wheel(ax, center)

    ax.plot([2.04, 2.04], [1.72, 2.22], color="#334155", linewidth=2.0, zorder=3)
    ax.plot([6.96, 6.96], [1.72, 2.22], color="#334155", linewidth=2.0, zorder=3)
    ax.text(2.04, 2.64, "front axle", ha="center", va="center", fontsize=7.6, color="#334155")
    ax.text(6.96, 2.64, "rear axle", ha="center", va="center", fontsize=7.6, color="#334155")
    ax.plot([4.94, 6.96], [4.72, 2.22], color="#d97706", linewidth=1.8, zorder=2)
    ax.plot([7.10, 6.96], [4.72, 2.22], color="#0284c7", linewidth=1.8, zorder=2)
    ax.plot([7.10, 6.96], [4.72, 1.72], color="#0284c7", linewidth=1.8, zorder=2)

    _box(ax, (1.24, 3.80), (1.58, 0.42), "Steering\nmechanism", face="#ecfdf5", edge="#16a34a", fontsize=7.8)
    _arrow(ax, (1.24, 4.90), (1.82, 4.22), color="#16a34a", rad=0.08)
    _arrow(ax, (1.72, 3.80), (2.04, 2.22), color="#16a34a", rad=-0.08)
    _arrow(ax, (1.72, 3.80), (2.04, 1.72), color="#16a34a", rad=0.08)
    _label(ax, "steering command\nbecomes wheel heading", (0.82, 3.72), (1.72, 3.80), color="#16a34a", ha="left")

    _box(ax, (4.10, 3.78), (1.64, 0.44), "Brake\nper wheel/side", face="#fee2e2", edge="#dc2626", fontsize=7.8)
    _arrow(ax, (2.12, 4.90), (4.10, 4.02), color="#dc2626", rad=-0.12)
    _label(ax, "braking\n[0,1]", (3.24, 4.18), (4.10, 4.02), color="#dc2626")
    _arrow(ax, (5.32, 3.78), (6.73, 1.48), color="#dc2626", width=1.0, rad=-0.10)
    _label(ax, "brake torque\nopposes wheel rotation", (5.95, 3.28), (6.73, 1.48), color="#dc2626", ha="left")

    _box(ax, (8.78, 1.84), (1.55, 0.48), "Tire model\nrigid / handling / FEA", face="#fff7ed", edge="#ea580c", fontsize=7.6, weight="bold")
    ax.plot([8.78, 8.08, 7.20], [2.08, 2.08, 1.32], color="#ea580c", linewidth=1.35, zorder=3)
    _arrow(ax, (7.20, 1.32), (6.96, 1.32), color="#ea580c", rad=0.0)
    _label(ax, "longitudinal force\nappears at contact patch", (9.50, 0.82), (6.96, 1.32), color="#ea580c")

    _box(ax, (0.55, 0.74), (1.88, 0.42), "metadata\nJSON + logs", face="#f8fafc", edge="#64748b", fontsize=7.7, weight="bold")
    _box(
        ax,
        (2.70, 0.74),
        (4.58, 0.42),
        "engine map | gear | drive type | torque split | brake torque | tire model",
        face="#f8fafc",
        edge="#64748b",
        fontsize=7.4,
    )

    return save_figure(fig, output)


if __name__ == "__main__":
    print(render_rover_powertrain_driveline_brake_tire_flow())
