from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle

sys.path.append(str(Path(__file__).resolve().parents[1] / "common"))

from component_utils import IMAGES_RENDER, save_figure  # noqa: E402


def _box(ax, xy, size, label, *, face, edge, fontsize=8.0, weight="normal", linestyle="-"):
    patch = FancyBboxPatch(
        xy,
        size[0],
        size[1],
        boxstyle="round,pad=0.03,rounding_size=0.045",
        facecolor=face,
        edgecolor=edge,
        linestyle=linestyle,
        linewidth=1.25,
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


def _arrow(ax, start, end, *, color="#475569", width=1.25, rad=0.0, style="-|>"):
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


def _poly_arrow(ax, points, *, color="#475569", width=1.25):
    for start, end in zip(points, points[1:-1]):
        ax.plot([start[0], end[0]], [start[1], end[1]], color=color, linewidth=width, zorder=3)
    _arrow(ax, points[-2], points[-1], color=color, width=width, rad=0.0)


def _tag(ax, xy, text, *, color):
    ax.text(
        xy[0],
        xy[1],
        text,
        ha="center",
        va="center",
        fontsize=7.2,
        color=color,
        bbox={"boxstyle": "round,pad=0.18", "facecolor": "white", "edgecolor": color, "linewidth": 0.8},
        zorder=9,
    )


def _label(ax, text, xytext, xy, *, color, ha="center"):
    ax.annotate(
        text,
        xy=xy,
        xytext=xytext,
        ha=ha,
        va="center",
        fontsize=7.2,
        color=color,
        bbox={"boxstyle": "round,pad=0.18", "facecolor": "white", "edgecolor": color, "linewidth": 0.8},
        arrowprops={"arrowstyle": "-", "color": color, "linewidth": 0.9, "shrinkA": 2, "shrinkB": 2},
        zorder=10,
    )


def _rover(ax):
    ax.add_patch(FancyBboxPatch((7.70, 2.20), 1.76, 0.82, boxstyle="round,pad=0.02,rounding_size=0.06", facecolor="#dbeafe", edgecolor="#1d4ed8", linewidth=1.2, zorder=3))
    ax.add_patch(Rectangle((8.18, 2.98), 0.72, 0.18, facecolor="#93c5fd", edgecolor="#1d4ed8", linewidth=0.9, zorder=4))
    for x in (7.86, 9.30):
        for y in (2.12, 3.07):
            ax.add_patch(Circle((x, y), 0.19, facecolor="#111827", edgecolor="#020617", linewidth=0.8, zorder=4))
            ax.add_patch(Circle((x, y), 0.08, facecolor="#e5e7eb", edgecolor="#64748b", linewidth=0.7, zorder=5))
    ax.text(8.58, 2.61, "rover\nstate", ha="center", va="center", fontsize=7.7, color="#1e3a8a", weight="bold", zorder=5)


def render_rover_driver_input_controller_component() -> Path:
    output = IMAGES_RENDER / "rover_driver_input_controller_component.png"
    fig, ax = plt.subplots(figsize=(12.4, 6.7))
    ax.set_xlim(0, 10.8)
    ax.set_ylim(0, 6)
    ax.axis("off")

    ax.text(5.0, 5.72, "Driver / Input / Controller Component", ha="center", va="center", fontsize=13.0, weight="bold", color="#111827")
    ax.text(
        5.0,
        0.18,
        "Driver owns normalized commands and provenance. Steering, powertrain, driveline, and brake convert those commands into physical states.",
        ha="center",
        va="center",
        fontsize=8.0,
        color="#475569",
    )

    ax.add_patch(Rectangle((0.35, 4.42), 9.30, 0.74, facecolor="#eff6ff", edgecolor="none", alpha=0.65, zorder=0))
    ax.add_patch(Rectangle((0.35, 2.52), 9.30, 1.26, facecolor="#f8fafc", edgecolor="none", alpha=0.95, zorder=0))
    ax.add_patch(Rectangle((0.35, 1.00), 9.30, 0.84, facecolor="#f1f5f9", edgecolor="none", alpha=0.90, zorder=0))

    _box(ax, (0.62, 4.54), (1.42, 0.46), "interactive\nkeyboard / joystick", face="#ffffff", edge="#2563eb", fontsize=7.3)
    _box(ax, (2.16, 4.54), (1.42, 0.46), "CSV data\nopen-loop replay", face="#ffffff", edge="#2563eb", fontsize=7.3)
    _box(ax, (3.70, 4.54), (1.52, 0.46), "path follower\nclosed-loop", face="#ffffff", edge="#2563eb", fontsize=7.3)

    _box(ax, (1.45, 3.46), (2.12, 0.62), "DriverInputs\nm_steering [-1,+1]\nm_throttle [0,1]\nm_braking [0,1]", face="#dbeafe", edge="#2563eb", fontsize=7.5, weight="bold")
    _box(ax, (4.18, 3.46), (1.72, 0.62), "controller state\ntarget path/speed\ntracking error", face="#eef2ff", edge="#4f46e5", fontsize=7.4, weight="bold")
    _box(ax, (6.46, 3.46), (1.58, 0.62), "command limiter\nrate + saturation\nactual command", face="#f5f3ff", edge="#7c3aed", fontsize=7.3, weight="bold")

    _box(ax, (0.78, 2.50), (1.38, 0.48), "Steering\nmechanism", face="#dcfce7", edge="#16a34a", fontsize=7.5, weight="bold")
    _box(ax, (2.72, 2.50), (1.38, 0.48), "Powertrain /\nDriveline", face="#fef3c7", edge="#d97706", fontsize=7.5, weight="bold")
    _box(ax, (4.66, 2.50), (1.38, 0.48), "Brake\nsubsystem", face="#fee2e2", edge="#dc2626", fontsize=7.5, weight="bold")
    _rover(ax)

    _box(ax, (0.86, 1.14), (2.08, 0.48), "control CSV\nsource, steer, throttle, brake", face="#ffffff", edge="#64748b", fontsize=7.3)
    _box(ax, (3.18, 1.14), (2.08, 0.48), "actual command log\nrate-limited values", face="#ffffff", edge="#64748b", fontsize=7.3)
    _box(ax, (5.50, 1.14), (2.08, 0.48), "target-state trace\npath, speed, error", face="#ffffff", edge="#64748b", fontsize=7.3)
    _box(ax, (7.82, 1.14), (1.34, 0.48), "metadata\ninput mode", face="#ffffff", edge="#64748b", fontsize=7.3)

    for start in [(1.33, 4.54), (2.87, 4.54), (4.46, 4.54)]:
        _arrow(ax, start, (2.50, 4.08), color="#2563eb", rad=-0.06)
    _arrow(ax, (4.46, 4.54), (5.04, 4.08), color="#4f46e5", rad=0.08)
    _arrow(ax, (3.57, 3.77), (4.18, 3.77), color="#4f46e5")
    _arrow(ax, (5.90, 3.77), (6.46, 3.77), color="#7c3aed")
    _arrow(ax, (2.04, 3.46), (1.47, 2.98), color="#16a34a", rad=0.04)
    _arrow(ax, (2.52, 3.46), (3.41, 2.98), color="#d97706", rad=-0.04)
    _arrow(ax, (2.96, 3.46), (5.35, 2.98), color="#dc2626", rad=-0.10)
    _arrow(ax, (7.24, 3.46), (7.90, 3.02), color="#7c3aed", rad=-0.04)

    ax.plot([9.74, 9.74], [2.05, 3.30], color="#334155", linewidth=2.0, zorder=4)
    ax.text(9.86, 3.42, "physical\noutput bus", ha="left", va="center", fontsize=6.8, color="#334155", zorder=6)
    _arrow(ax, (8.04, 3.63), (9.70, 3.22), color="#334155", rad=-0.03)
    for port_y, color, label in ((3.12, "#16a34a", "heading"), (2.58, "#d97706", "torque"), (2.16, "#dc2626", "brake")):
        ax.add_patch(Circle((9.74, port_y), 0.035, facecolor=color, edgecolor="white", linewidth=0.6, zorder=8))
        ax.text(9.84, port_y, label, ha="left", va="center", fontsize=5.9, color=color, zorder=8)
    _arrow(ax, (9.70, 3.12), (9.30, 3.07), color="#16a34a", rad=0.0)
    _arrow(ax, (9.70, 2.58), (9.30, 2.12), color="#d97706", rad=0.0)
    _arrow(ax, (9.70, 2.16), (9.30, 2.12), color="#dc2626", rad=0.0)
    _arrow(ax, (8.58, 3.16), (5.04, 4.08), color="#4f46e5", rad=0.12, style="<|-")

    ax.plot([1.46, 8.50], [1.94, 1.94], color="#64748b", linewidth=1.0, linestyle=(0, (3, 3)), zorder=2)
    _poly_arrow(ax, [(2.50, 3.46), (2.50, 2.08), (1.90, 2.08), (1.90, 1.62)], color="#64748b", width=1.0)
    _poly_arrow(ax, [(7.24, 3.46), (7.24, 2.08), (4.22, 2.08), (4.22, 1.62)], color="#64748b", width=1.0)
    _poly_arrow(ax, [(5.04, 3.46), (5.04, 3.18), (6.24, 3.18), (6.24, 2.08), (6.54, 2.08), (6.54, 1.62)], color="#64748b", width=1.0)
    _poly_arrow(ax, [(7.24, 3.46), (7.24, 2.24), (8.48, 2.24), (8.48, 1.62)], color="#64748b", width=1.0)

    _label(
        ax,
        "normalized command !=\nwheel angle / engine torque / brake torque",
        (6.86, 4.88),
        (2.50, 3.46),
        color="#b45309",
    )
    _label(ax, "feedback reads\nrover state, not raw commands", (8.82, 4.38), (8.58, 3.16), color="#4f46e5")
    _label(ax, "physical outputs:\nwheel heading, torque split,\nbrake torque", (10.35, 3.86), (9.74, 3.30), color="#334155", ha="right")

    return save_figure(fig, output)


if __name__ == "__main__":
    print(render_rover_driver_input_controller_component())
