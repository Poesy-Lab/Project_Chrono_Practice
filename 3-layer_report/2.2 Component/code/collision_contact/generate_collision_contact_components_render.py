from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle

sys.path.append(str(Path(__file__).resolve().parents[1] / "common"))

from component_utils import IMAGES_RENDER, save_figure  # noqa: E402


def _label(ax, text, xytext, xy, *, color):
    ax.annotate(
        text,
        xy=xy,
        xytext=xytext,
        ha="center",
        va="center",
        fontsize=10,
        color=color,
        bbox={"boxstyle": "round,pad=0.22", "facecolor": "white", "edgecolor": color, "linewidth": 1.0},
        arrowprops={"arrowstyle": "-", "color": color, "linewidth": 1.2, "shrinkA": 2, "shrinkB": 2},
        zorder=20,
    )


def render_collision_contact_components() -> Path:
    output = IMAGES_RENDER / "collision_contact_components.png"

    fig, ax = plt.subplots(figsize=(9.2, 5.8))
    ax.set_aspect("equal")
    ax.set_xlim(-2.2, 2.15)
    ax.set_ylim(-1.30, 1.34)
    ax.axis("off")

    ax.add_patch(Rectangle((-2.05, -0.94), 4.05, 0.14, facecolor="#d8dee5", edgecolor="#64748b", linewidth=1.4, zorder=1))
    ax.add_patch(Rectangle((-1.52, -0.83), 2.42, 0.07, facecolor="#9ca3af", edgecolor="none", alpha=0.35, zorder=2))

    body_xy = (-1.34, -0.58)
    body_w, body_h = 1.70, 0.56
    ax.add_patch(Rectangle(body_xy, body_w, body_h, facecolor="#7fb3ff", edgecolor="#1d4ed8", linewidth=1.8, zorder=5))
    ax.add_patch(
        Polygon(
            [(-1.34, -0.02), (-1.24, 0.08), (0.46, 0.08), (0.36, -0.02)],
            closed=True,
            facecolor="#a8ccff",
            edgecolor="#1d4ed8",
            linewidth=1.0,
            zorder=4,
        )
    )
    ax.add_patch(
        Polygon(
            [(0.36, -0.58), (0.46, -0.48), (0.46, 0.08), (0.36, -0.02)],
            closed=True,
            facecolor="#5b9df5",
            edgecolor="#1d4ed8",
            linewidth=1.0,
            zorder=4,
        )
    )
    ax.add_patch(Rectangle((-1.22, -0.46), 1.50, 0.32, fill=False, edgecolor="#ef4444", linewidth=2.1, linestyle="--", zorder=7))

    ax.add_patch(Rectangle((0.36, -0.88), 0.36, 1.16, facecolor="#f87171", edgecolor="#991b1b", linewidth=1.8, zorder=5))
    ax.add_patch(
        Polygon(
            [(0.72, -0.88), (0.84, -0.76), (0.84, 0.40), (0.72, 0.28)],
            closed=True,
            facecolor="#ef4444",
            edgecolor="#991b1b",
            linewidth=1.0,
            zorder=4,
        )
    )
    ax.add_patch(
        Polygon(
            [(0.36, 0.28), (0.48, 0.40), (0.84, 0.40), (0.72, 0.28)],
            closed=True,
            facecolor="#fca5a5",
            edgecolor="#991b1b",
            linewidth=1.0,
            zorder=4,
        )
    )
    ax.add_patch(Rectangle((0.43, -0.75), 0.18, 0.90, fill=False, edgecolor="#ef4444", linewidth=2.0, linestyle="--", zorder=7))

    contact = (0.36, -0.30)
    ax.scatter([contact[0]], [contact[1]], s=90, color="#facc15", edgecolor="#854d0e", linewidth=1.0, zorder=8)
    ax.add_patch(FancyArrowPatch((-1.18, 0.18), (-0.42, 0.18), arrowstyle="-|>", mutation_scale=18, color="#0ea5e9", linewidth=3.0, zorder=9))
    ax.add_patch(FancyArrowPatch((0.38, -0.30), (-0.22, -0.10), arrowstyle="-|>", mutation_scale=18, color="#f97316", linewidth=3.0, zorder=10))
    ax.add_patch(FancyArrowPatch(contact, (-0.30, -0.30), arrowstyle="-|>", mutation_scale=18, color="#22c55e", linewidth=2.5, zorder=9))

    ax.text(-0.89, -0.32, "moving body", ha="center", va="center", fontsize=9, color="#1e3a8a", weight="bold")
    ax.text(0.56, -0.34, "fixed\nobstacle", ha="center", va="center", fontsize=9, color="#7f1d1d", weight="bold")

    _label(ax, "Collision body", (-1.55, 0.86), (-0.92, -0.02), color="#1d4ed8")
    _label(ax, "Collision envelope", (-1.08, 1.12), (-0.88, -0.15), color="#dc2626")
    _label(ax, "Approach velocity", (-1.30, 0.46), (-0.42, 0.18), color="#0284c7")
    _label(ax, "Contact point", (0.42, 0.82), contact, color="#854d0e")
    _label(ax, "Contact normal", (-0.42, 0.70), (-0.22, -0.30), color="#15803d")
    _label(ax, "Contact force", (0.92, 0.62), (-0.22, -0.10), color="#c2410c")
    _label(ax, "Ground", (1.34, -1.08), (0.78, -0.86), color="#475569")

    ax.text(
        0.0,
        1.20,
        "Collision/contact component scene",
        ha="center",
        va="center",
        fontsize=13,
        color="#111827",
        weight="bold",
    )
    return save_figure(fig, output)


if __name__ == "__main__":
    print(render_collision_contact_components())
