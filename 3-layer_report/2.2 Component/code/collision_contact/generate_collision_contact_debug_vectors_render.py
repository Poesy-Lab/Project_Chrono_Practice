from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle

sys.path.append(str(Path(__file__).resolve().parents[1] / "common"))

from component_utils import IMAGES_RENDER, save_figure  # noqa: E402


def _label(ax, text, xytext, xy, *, color, ha="center"):
    ax.annotate(
        text,
        xy=xy,
        xytext=xytext,
        ha=ha,
        va="center",
        fontsize=10,
        color=color,
        bbox={"boxstyle": "round,pad=0.22", "facecolor": "white", "edgecolor": color, "linewidth": 1.0},
        arrowprops={"arrowstyle": "-", "color": color, "linewidth": 1.2, "shrinkA": 2, "shrinkB": 2},
        zorder=20,
    )


def render_collision_contact_debug_vectors() -> Path:
    output = IMAGES_RENDER / "collision_contact_debug_vectors.png"

    fig, ax = plt.subplots(figsize=(9.2, 5.6))
    ax.set_aspect("equal")
    ax.set_xlim(-2.15, 2.05)
    ax.set_ylim(-1.30, 1.30)
    ax.axis("off")

    ax.add_patch(Rectangle((-1.95, -1.15), 3.78, 0.12, facecolor="#d8dee5", edgecolor="#64748b", linewidth=1.3, zorder=1))

    body_xy = (-1.22, -0.52)
    body_size = (1.17, 0.78)
    obstacle_xy = (-0.05, -0.72)
    obstacle_size = (0.36, 1.22)
    contact_point = (-0.05, -0.10)
    normal_end = (-0.86, -0.10)
    force_end = (-0.72, 0.25)

    ax.add_patch(Rectangle(body_xy, *body_size, facecolor="#7fb3ff", edgecolor="#1d4ed8", linewidth=2.0, alpha=0.94, zorder=4))
    ax.add_patch(Rectangle(obstacle_xy, *obstacle_size, facecolor="#f87171", edgecolor="#991b1b", linewidth=2.0, alpha=0.94, zorder=4))
    ax.add_patch(Rectangle((-1.12, -0.42), 1.07, 0.58, fill=False, edgecolor="#ef4444", linewidth=2.0, linestyle="--", zorder=7))
    ax.add_patch(Rectangle((-0.05, -0.63), 0.27, 1.04, fill=False, edgecolor="#ef4444", linewidth=2.0, linestyle="--", zorder=7))

    ax.text(-0.72, -0.34, "rover\nbody", ha="center", va="center", fontsize=9.5, color="#1e3a8a", weight="bold", zorder=8)
    ax.text(0.13, -0.10, "rigid\nobstacle", ha="center", va="center", fontsize=8.4, color="#7f1d1d", rotation=90, weight="bold", zorder=8)

    ax.add_patch(Circle(contact_point, 0.055, facecolor="#facc15", edgecolor="#854d0e", linewidth=1.1, zorder=12))
    ax.add_patch(FancyArrowPatch(contact_point, normal_end, arrowstyle="-|>", mutation_scale=20, color="#22c55e", linewidth=3.0, zorder=10))
    ax.add_patch(FancyArrowPatch(contact_point, force_end, arrowstyle="-|>", mutation_scale=20, color="#f97316", linewidth=3.0, zorder=11))

    _label(ax, "Exact contact point", (0.84, -0.17), contact_point, color="#854d0e")
    _label(ax, "Contact normal\nplane_coord X", (-1.40, 0.64), normal_end, color="#15803d", ha="left")
    _label(ax, "Reported force\nworld-frame after conversion", (-1.28, 0.92), force_end, color="#c2410c", ha="left")
    _label(ax, "Dashed collision\nshape edge", (0.92, 0.58), (0.22, 0.40), color="#dc2626")

    pair_color = "#1d4ed8"
    left, right, bottom, top = -1.34, 0.43, -0.86, 0.62
    tick = 0.12
    ax.plot([left, left], [bottom, top], color=pair_color, linewidth=1.8, zorder=10)
    ax.plot([right, right], [bottom, top], color=pair_color, linewidth=1.8, zorder=10)
    ax.plot([left, left + tick], [top, top], color=pair_color, linewidth=1.8, zorder=10)
    ax.plot([right - tick, right], [top, top], color=pair_color, linewidth=1.8, zorder=10)
    ax.plot([left, left + tick], [bottom, bottom], color=pair_color, linewidth=1.8, zorder=10)
    ax.plot([right - tick, right], [bottom, bottom], color=pair_color, linewidth=1.8, zorder=10)
    _label(ax, "Filtered body pair", (-1.22, -1.02), (left, -0.76), color=pair_color, ha="right")

    ax.text(
        0.0,
        1.12,
        "Debug visualization for contact reporter output",
        ha="center",
        va="center",
        fontsize=13,
        color="#111827",
        weight="bold",
    )
    return save_figure(fig, output)


if __name__ == "__main__":
    print(render_collision_contact_debug_vectors())
