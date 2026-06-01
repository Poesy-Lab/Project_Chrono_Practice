from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle

sys.path.append(str(Path(__file__).resolve().parents[1] / "common"))

from component_utils import IMAGES_RENDER, save_figure  # noqa: E402
from vsg_component_render import (  # noqa: E402
    add_box as vsg_add_box,
    add_cylinder_y as vsg_add_cylinder_y,
    render_vsg_scene,
)


def _label(ax, text, xytext, xy, *, color):
    ax.annotate(
        text,
        xy=xy,
        xytext=xytext,
        ha="center",
        va="center",
        fontsize=9,
        color=color,
        bbox={"boxstyle": "round,pad=0.22", "facecolor": "white", "edgecolor": color, "linewidth": 1.0},
        arrowprops={"arrowstyle": "-", "color": color, "linewidth": 1.1, "shrinkA": 2, "shrinkB": 2},
        zorder=20,
    )


def render_collision_visual_vs_collision_shape() -> Path:
    output = IMAGES_RENDER / "collision_visual_vs_collision_shape.png"

    def visual_collision_scene(system, chrono):
        vsg_add_box(system, chrono, "visual_side_floor", (-1.25, 0, -0.035), (1.75, 1.45, 0.07), (0.66, 0.69, 0.63), collide=False)
        vsg_add_box(system, chrono, "collision_side_floor", (1.25, 0, -0.035), (1.75, 1.45, 0.07), (0.66, 0.69, 0.63), collide=False)
        vsg_add_box(system, chrono, "visual_chassis", (-1.25, 0, 0.42), (1.05, 0.54, 0.24), (0.10, 0.34, 0.78), collide=False)
        vsg_add_box(system, chrono, "visual_payload", (-1.42, -0.18, 0.64), (0.34, 0.26, 0.16), (0.04, 0.48, 0.42), collide=False)
        vsg_add_box(system, chrono, "visual_mast", (-0.98, -0.20, 0.82), (0.09, 0.09, 0.38), (0.04, 0.65, 0.66), collide=False)
        vsg_add_box(system, chrono, "collision_chassis", (1.25, 0, 0.40), (0.90, 0.42, 0.20), (0.88, 0.22, 0.22), collide=False)
        vsg_add_box(system, chrono, "collision_payload", (1.08, -0.18, 0.58), (0.28, 0.20, 0.12), (0.95, 0.35, 0.35), collide=False)
        vsg_add_box(system, chrono, "collision_mast", (1.52, -0.20, 0.72), (0.07, 0.07, 0.30), (0.95, 0.35, 0.35), collide=False)
        for base_x, color, radius in [(-1.25, (0.02, 0.03, 0.05), 0.20), (1.25, (0.90, 0.28, 0.28), 0.17)]:
            for dx in (-0.38, 0.38):
                for y in (-0.42, 0.42):
                    vsg_add_cylinder_y(system, chrono, "wheel_pair", (base_x + dx, y, 0.22), radius, 0.16, color, collide=False)
        vsg_add_box(system, chrono, "divider", (0, 0, 0.28), (0.04, 1.70, 0.04), (0.20, 0.24, 0.30), collide=False)

    # Use a deterministic annotated report figure so labels are never lost on VSG-capable machines.
    vsg_ok = False

    fig, (visual_ax, collision_ax) = plt.subplots(1, 2, figsize=(9.8, 4.8))
    for ax in (visual_ax, collision_ax):
        ax.set_aspect("equal")
        ax.set_xlim(-1.35, 1.35)
        ax.set_ylim(-1.05, 1.05)
        ax.axis("off")
    visual_ax.set_title("Visual Shape", fontsize=13, color="#1d4ed8", weight="bold")
    collision_ax.set_title("Collision Shape", fontsize=13, color="#991b1b", weight="bold")
    visual_ax.add_patch(Rectangle((-0.82, -0.35), 1.64, 0.70, facecolor="#2563eb", edgecolor="#111827", linewidth=1.2, zorder=2))
    visual_ax.add_patch(Rectangle((-0.30, -0.16), 0.44, 0.32, facecolor="#0f766e", edgecolor="#111827", linewidth=1.0, zorder=3))
    for x, y in [(-0.84, -0.68), (-0.84, 0.68), (0.84, -0.68), (0.84, 0.68)]:
        visual_ax.add_patch(Circle((x, y), 0.18, facecolor="#111827", edgecolor="#111827", zorder=3))
    _label(visual_ax, "visible chassis mesh", (-0.48, 0.88), (-0.18, 0.34), color="#1d4ed8")
    _label(visual_ax, "payload detail", (0.52, 0.68), (-0.08, 0.16), color="#0f766e")
    _label(visual_ax, "visual wheel radius", (0.38, -0.86), (0.84, -0.68), color="#111827")
    collision_ax.add_patch(Rectangle((-0.64, -0.26), 1.28, 0.52, facecolor="#ef4444", edgecolor="#991b1b", linewidth=1.4, alpha=0.45, zorder=2))
    collision_ax.add_patch(Rectangle((-0.25, -0.13), 0.38, 0.26, facecolor="#ef4444", edgecolor="#991b1b", linewidth=1.0, alpha=0.55, zorder=3))
    for x, y in [(-0.84, -0.68), (-0.84, 0.68), (0.84, -0.68), (0.84, 0.68)]:
        collision_ax.add_patch(Circle((x, y), 0.16, facecolor="#ef4444", edgecolor="#991b1b", linewidth=1.2, alpha=0.45, zorder=2))
    _label(collision_ax, "simplified envelope", (-0.42, 0.88), (-0.30, 0.25), color="#991b1b")
    _label(collision_ax, "smaller wheel contact", (0.48, -0.86), (0.84, -0.68), color="#991b1b")
    fig.suptitle("Visual geometry is for inspection; collision geometry is for contact solving", fontsize=12, color="#111827")
    return save_figure(fig, output)


if __name__ == "__main__":
    print(render_collision_visual_vs_collision_shape())
