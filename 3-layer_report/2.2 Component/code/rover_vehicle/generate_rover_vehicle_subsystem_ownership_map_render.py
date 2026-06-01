from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

sys.path.append(str(Path(__file__).resolve().parents[1] / "common"))

from component_utils import IMAGES_RENDER, save_figure  # noqa: E402


def _box(ax, xy, size, label, *, face, edge, fontsize=8.0, weight="normal", linestyle="-"):
    patch = FancyBboxPatch(
        xy,
        size[0],
        size[1],
        boxstyle="round,pad=0.025,rounding_size=0.04",
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


def _arrow(ax, start, end, *, color="#475569", width=1.2, rad=0.0, style="-|>"):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle=style,
            mutation_scale=12,
            linewidth=width,
            color=color,
            connectionstyle=f"arc3,rad={rad}",
            shrinkA=4,
            shrinkB=4,
            zorder=3,
        )
    )


def _lane(ax, y, label, color):
    ax.add_patch(Rectangle((0.28, y), 10.44, 0.88, facecolor=color, edgecolor="none", alpha=0.38, zorder=0))
    ax.text(0.68, y + 0.44, label, ha="right", va="center", fontsize=7.8, color="#334155", weight="bold", zorder=2)


def _tag(ax, xy, text, *, color):
    ax.text(
        xy[0],
        xy[1],
        text,
        ha="center",
        va="center",
        fontsize=7.1,
        color=color,
        bbox={"boxstyle": "round,pad=0.16", "facecolor": "white", "edgecolor": color, "linewidth": 0.8},
        zorder=8,
    )


def render_rover_vehicle_subsystem_ownership_map() -> Path:
    output = IMAGES_RENDER / "rover_vehicle_subsystem_ownership_map.png"
    fig, ax = plt.subplots(figsize=(11.4, 6.7))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 6.4)
    ax.axis("off")

    ax.text(5.5, 6.12, "Rover / Vehicle subsystem ownership map", ha="center", va="center", fontsize=13.0, weight="bold", color="#111827")
    ax.text(
        5.5,
        0.20,
        "Component view: each box owns a state boundary, not just a Chrono API call. Evidence must follow the same ownership path.",
        ha="center",
        va="center",
        fontsize=8.0,
        color="#475569",
    )

    _lane(ax, 4.92, "command layer", "#e0f2fe")
    _lane(ax, 3.82, "vehicle mechanism layer", "#ecfdf5")
    _lane(ax, 2.58, "physical interface layer", "#fff7ed")
    _lane(ax, 1.24, "evidence layer", "#f8fafc")

    _box(ax, (0.76, 5.14), (1.38, 0.44), "DriverInputs\nsteer / throttle / brake", face="#eff6ff", edge="#2563eb", fontsize=7.3, weight="bold")
    _box(ax, (2.72, 5.14), (1.28, 0.44), "Controller\noptional feedback", face="#eef2ff", edge="#4f46e5", fontsize=7.3)
    _box(ax, (4.72, 5.14), (1.48, 0.44), "Limiter\nrate + saturation", face="#f5f3ff", edge="#7c3aed", fontsize=7.3)

    _box(ax, (0.84, 4.03), (1.45, 0.50), "Steering\nrack / skid split", face="#dcfce7", edge="#16a34a", fontsize=7.4, weight="bold")
    _box(ax, (2.62, 4.03), (1.45, 0.50), "Powertrain\nengine + gear", face="#fef3c7", edge="#d97706", fontsize=7.4, weight="bold")
    _box(ax, (4.42, 4.03), (1.45, 0.50), "Driveline\nsplit + diff", face="#e0f2fe", edge="#0284c7", fontsize=7.4, weight="bold")
    _box(ax, (6.23, 4.03), (1.45, 0.50), "Brake\nwheel/side torque", face="#fee2e2", edge="#dc2626", fontsize=7.4, weight="bold")
    _box(ax, (8.02, 4.03), (1.44, 0.50), "Suspension\nload path", face="#f3e8ff", edge="#9333ea", fontsize=7.4, weight="bold")

    _box(ax, (0.84, 2.82), (1.34, 0.50), "Chassis\nISO frame", face="#dbeafe", edge="#1d4ed8", fontsize=7.3, weight="bold")
    _box(ax, (2.55, 2.82), (1.34, 0.50), "Wheel\nbody + axis", face="#e5e7eb", edge="#374151", fontsize=7.3, weight="bold")
    _box(ax, (4.24, 2.82), (1.34, 0.50), "Tire\nforce model", face="#ffedd5", edge="#ea580c", fontsize=7.3, weight="bold")
    _box(ax, (5.92, 2.82), (1.34, 0.50), "Terrain\nquery + contact", face="#dcfce7", edge="#15803d", fontsize=7.3, weight="bold")
    _box(ax, (7.60, 2.82), (1.34, 0.50), "Collision\nshape/material", face="#fee2e2", edge="#b91c1c", fontsize=7.3, weight="bold")
    _box(ax, (9.14, 2.82), (1.12, 0.50), "Sensors\nmount pose", face="#cffafe", edge="#0891b2", fontsize=7.3, weight="bold")

    _box(ax, (0.76, 1.48), (1.40, 0.46), "state CSV\npose / speed", face="#ffffff", edge="#64748b", fontsize=7.1)
    _box(ax, (2.48, 1.48), (1.40, 0.46), "control CSV\ncmd vs actual", face="#ffffff", edge="#64748b", fontsize=7.1)
    _box(ax, (4.20, 1.48), (1.40, 0.46), "force CSV\ntire/contact", face="#ffffff", edge="#64748b", fontsize=7.1)
    _box(ax, (5.92, 1.48), (1.40, 0.46), "render PNG\nvisual/collision", face="#ffffff", edge="#64748b", fontsize=7.1)
    _box(ax, (7.64, 1.48), (1.40, 0.46), "metadata JSON\nids + modules", face="#ffffff", edge="#64748b", fontsize=7.1)
    _box(ax, (9.36, 1.48), (1.10, 0.46), "sensor\nframes", face="#ffffff", edge="#64748b", fontsize=7.1)

    _arrow(ax, (2.14, 5.36), (2.72, 5.36), color="#2563eb")
    _arrow(ax, (4.00, 5.36), (4.72, 5.36), color="#4f46e5")
    _arrow(ax, (1.45, 5.14), (1.56, 4.53), color="#16a34a", rad=-0.08)
    _arrow(ax, (5.34, 5.14), (3.34, 4.53), color="#d97706", rad=0.12)
    _arrow(ax, (5.46, 5.14), (6.96, 4.53), color="#dc2626", rad=-0.12)

    _arrow(ax, (4.07, 4.28), (4.42, 4.28), color="#0284c7")
    _arrow(ax, (5.87, 4.28), (4.93, 3.32), color="#0284c7", rad=-0.08)
    _arrow(ax, (1.56, 4.03), (3.22, 3.32), color="#16a34a", rad=-0.10)
    _arrow(ax, (6.96, 4.03), (3.22, 3.32), color="#dc2626", rad=0.12)
    _arrow(ax, (8.74, 4.03), (3.22, 3.32), color="#9333ea", rad=0.08)

    _arrow(ax, (2.18, 3.07), (2.55, 3.07), color="#374151")
    _arrow(ax, (3.89, 3.07), (4.24, 3.07), color="#ea580c")
    _arrow(ax, (5.58, 3.07), (5.92, 3.07), color="#15803d")
    _arrow(ax, (7.26, 3.07), (7.60, 3.07), color="#b91c1c")
    _arrow(ax, (1.50, 2.82), (1.45, 1.94), color="#64748b")
    _arrow(ax, (3.22, 2.82), (3.18, 1.94), color="#64748b")
    _arrow(ax, (4.92, 2.82), (4.90, 1.94), color="#64748b")
    _arrow(ax, (6.60, 2.82), (6.62, 1.94), color="#64748b")
    _arrow(ax, (8.28, 2.82), (8.34, 1.94), color="#64748b")
    _arrow(ax, (9.70, 2.82), (9.91, 1.94), color="#64748b")

    _tag(ax, (8.42, 5.30), "Frame contract: X forward, Y left, Z up", color="#1d4ed8")
    _tag(ax, (8.24, 5.00), "Do not read normalized steering as wheel angle", color="#16a34a")
    _tag(ax, (8.34, 4.70), "Do not read throttle as wheel torque", color="#d97706")
    _tag(ax, (5.48, 2.30), "Tire force is interpreted with terrain + contact method", color="#ea580c")

    return save_figure(fig, output)


if __name__ == "__main__":
    print(render_rover_vehicle_subsystem_ownership_map())
