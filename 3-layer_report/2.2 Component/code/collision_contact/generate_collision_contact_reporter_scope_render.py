from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle

sys.path.append(str(Path(__file__).resolve().parents[1] / "common"))

from component_utils import IMAGES_RENDER, save_figure  # noqa: E402


def _leader(ax, text, xytext, xy, *, color, ha="center"):
    ax.annotate(
        text,
        xy=xy,
        xytext=xytext,
        ha=ha,
        va="center",
        fontsize=8.1,
        color=color,
        bbox={"boxstyle": "round,pad=0.20", "facecolor": "white", "edgecolor": color, "linewidth": 0.9},
        arrowprops={"arrowstyle": "-", "color": color, "linewidth": 1.0, "shrinkA": 2, "shrinkB": 1},
        zorder=20,
    )


def _arrow(ax, start, end, *, color="#475569", width=1.2, rad=0.0):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=12,
            linewidth=width,
            color=color,
            connectionstyle=f"arc3,rad={rad}",
            shrinkA=3,
            shrinkB=3,
            zorder=8,
        )
    )


def _contact(ax, xy, *, reported=False):
    ax.add_patch(
        Circle(
            xy,
            0.045 if reported else 0.038,
            facecolor="#facc15",
            edgecolor="#15803d" if reported else "#854d0e",
            linewidth=1.2 if reported else 0.8,
            zorder=11,
        )
    )


def _csv_strip(ax, x, y):
    strip = FancyBboxPatch(
        (x, y),
        1.78,
        1.18,
        boxstyle="round,pad=0.035,rounding_size=0.045",
        facecolor="#f8fafc",
        edgecolor="#334155",
        linewidth=1.2,
        zorder=5,
    )
    ax.add_patch(strip)
    ax.text(x + 0.89, y + 1.00, "CSV rows from\nthis reporter", ha="center", va="center", fontsize=8.2, weight="bold", color="#111827", zorder=6)
    rows = [
        "body_a=rover_body",
        "body_b=rigid_obstacle",
        "contact_count=2",
        "source=pair_filter",
    ]
    for idx, row in enumerate(rows):
        ax.text(x + 0.13, y + 0.72 - idx * 0.18, row, ha="left", va="center", fontsize=7.3, color="#334155", zorder=6)


def render_collision_contact_reporter_scope() -> Path:
    output = IMAGES_RENDER / "collision_contact_reporter_scope.png"
    fig, ax = plt.subplots(figsize=(10.4, 5.6))
    ax.set_aspect("equal")
    ax.set_xlim(-2.7, 3.4)
    ax.set_ylim(-1.50, 1.62)
    ax.axis("off")

    ax.text(0.25, 1.45, "Contact reporter scope / pair filter", ha="center", va="center", fontsize=13, weight="bold", color="#111827")

    ax.add_patch(Rectangle((-2.45, -1.03), 4.15, 0.12, facecolor="#d1d5db", edgecolor="#64748b", linewidth=1.1, zorder=1))
    ax.add_patch(Rectangle((-1.55, -0.52), 1.18, 0.56, facecolor="#93c5fd", edgecolor="#1d4ed8", linewidth=1.6, zorder=4))
    ax.add_patch(Rectangle((-1.45, -0.42), 1.02, 0.42, fill=False, edgecolor="#dc2626", linewidth=1.6, linestyle="--", zorder=6))
    ax.text(-0.96, -0.24, "rover_body", ha="center", va="center", fontsize=8.2, color="#1e3a8a", weight="bold", zorder=7)

    wheel_centers = [(-1.42, -0.78), (-0.50, -0.78)]
    for center in wheel_centers:
        ax.add_patch(Circle(center, 0.19, facecolor="#111827", edgecolor="#111827", linewidth=0.8, zorder=5))
        ax.add_patch(Circle(center, 0.07, facecolor="#475569", edgecolor="#111827", linewidth=0.5, zorder=6))

    ax.add_patch(Rectangle((-0.30, -0.90), 0.26, 1.18, facecolor="#fca5a5", edgecolor="#991b1b", linewidth=1.6, zorder=4))
    ax.add_patch(Rectangle((-0.25, -0.80), 0.16, 1.02, fill=False, edgecolor="#dc2626", linewidth=1.6, linestyle="--", zorder=6))
    ax.text(-0.17, -0.20, "rigid\nobstacle", ha="center", va="center", fontsize=8.0, color="#7f1d1d", weight="bold", rotation=90, zorder=7)

    reported_contacts = [(-0.37, -0.40), (-0.37, -0.12)]
    ignored_contacts = [(-1.42, -0.97), (-0.50, -0.97)]
    for point in reported_contacts:
        _contact(ax, point, reported=True)
    for point in ignored_contacts:
        _contact(ax, point, reported=False)

    bracket_color = "#16a34a"
    ax.plot([-0.43, -0.43], [-0.50, -0.02], color=bracket_color, linewidth=2.0, zorder=12)
    ax.plot([-0.43, -0.32], [-0.50, -0.50], color=bracket_color, linewidth=2.0, zorder=12)
    ax.plot([-0.43, -0.32], [-0.02, -0.02], color=bracket_color, linewidth=2.0, zorder=12)

    _leader(
        ax,
        "reported pair:\nrover_body - rigid_obstacle",
        (-1.78, 0.96),
        reported_contacts[1],
        color=bracket_color,
        ha="left",
    )
    _leader(
        ax,
        "ignored by this reporter",
        (-2.34, -1.28),
        ignored_contacts[0],
        color="#854d0e",
        ha="left",
    )
    _leader(
        ax,
        "ignored wheel-ground\ncontact point",
        (0.18, -1.30),
        ignored_contacts[1],
        color="#854d0e",
        ha="left",
    )
    _leader(
        ax,
        "red dashed outlines are\ncollision shapes",
        (0.60, 0.72),
        (-0.24, 0.22),
        color="#dc2626",
        ha="left",
    )

    _csv_strip(ax, 1.40, -0.20)
    _arrow(ax, (-0.31, -0.25), (1.40, 0.39), color=bracket_color, width=1.5, rad=0.10)
    ax.text(
        1.97,
        -0.52,
        "Pair reporter filters after collision detection:\nother contacts may exist but are not logged in this CSV.",
        ha="center",
        va="center",
        fontsize=7.8,
        color="#475569",
        zorder=6,
    )

    return save_figure(fig, output)


if __name__ == "__main__":
    print(render_collision_contact_reporter_scope())
