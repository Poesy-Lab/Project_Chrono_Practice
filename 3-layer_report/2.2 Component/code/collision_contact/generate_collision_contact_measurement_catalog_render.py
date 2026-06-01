from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle

sys.path.append(str(Path(__file__).resolve().parents[1] / "common"))

from component_utils import IMAGES_RENDER, save_figure  # noqa: E402


def _box(ax, xy, size, label, *, face, edge, fontsize=7.8, weight="normal"):
    patch = FancyBboxPatch(
        xy,
        size[0],
        size[1],
        boxstyle="round,pad=0.026,rounding_size=0.045",
        facecolor=face,
        edgecolor=edge,
        linewidth=1.3,
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
        zorder=6,
    )
    return patch


def _arrow(ax, start, end, *, color="#475569", width=1.25, rad=0.0):
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
        fontsize=7.6,
        color=color,
        bbox={"boxstyle": "round,pad=0.18", "facecolor": "white", "edgecolor": color, "linewidth": 0.9},
        arrowprops={"arrowstyle": "-", "color": color, "linewidth": 0.9, "shrinkA": 2, "shrinkB": 2},
        zorder=10,
    )


def _mini_collision_scene(ax, x, y):
    ax.add_patch(Rectangle((x - 0.56, y - 0.24), 1.12, 0.12, facecolor="#d1d5db", edgecolor="#64748b", linewidth=0.8, zorder=5))
    ax.add_patch(Rectangle((x - 0.46, y - 0.04), 0.54, 0.30, facecolor="#93c5fd", edgecolor="#1d4ed8", linewidth=1.0, zorder=6))
    ax.add_patch(Rectangle((x + 0.02, y - 0.07), 0.46, 0.34, fill=False, edgecolor="#dc2626", linewidth=1.2, linestyle="--", zorder=7))
    ax.add_patch(Rectangle((x + 0.35, y - 0.18), 0.18, 0.58, facecolor="#fca5a5", edgecolor="#991b1b", linewidth=1.0, zorder=6))
    for cy in (y - 0.02, y + 0.13):
        ax.add_patch(Circle((x + 0.34, cy), 0.035, facecolor="#facc15", edgecolor="#854d0e", linewidth=0.6, zorder=8))
        _arrow(ax, (x + 0.34, cy), (x + 0.13, cy + 0.04), color="#16a34a", width=1.0)


def _mini_graph(ax, x, y):
    ax.add_patch(Rectangle((x - 0.50, y - 0.22), 1.00, 0.44, facecolor="white", edgecolor="#64748b", linewidth=0.8, zorder=5))
    xs = [x - 0.40, x - 0.25, x - 0.10, x + 0.05, x + 0.20, x + 0.38]
    ys = [y - 0.13, y - 0.10, y + 0.13, y + 0.02, y - 0.04, y - 0.11]
    ax.plot(xs, ys, color="#dc2626", linewidth=1.6, zorder=7)
    ax.plot([x - 0.42, x + 0.42], [y - 0.14, y - 0.14], color="#94a3b8", linewidth=0.6, zorder=6)
    ax.plot([x - 0.42, x - 0.42], [y - 0.14, y + 0.16], color="#94a3b8", linewidth=0.6, zorder=6)


def render_collision_contact_measurement_catalog() -> Path:
    output = IMAGES_RENDER / "collision_contact_measurement_catalog.png"
    fig, ax = plt.subplots(figsize=(11.0, 6.0))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.0)
    ax.axis("off")

    ax.text(5.0, 5.72, "Collision/contact measurement component catalog", ha="center", va="center", fontsize=12.6, weight="bold", color="#111827")
    ax.text(1.48, 5.18, "Contact geometry", ha="center", va="center", fontsize=9.2, weight="bold", color="#334155")
    ax.text(4.60, 5.18, "Chrono contact pipeline", ha="center", va="center", fontsize=9.2, weight="bold", color="#334155")
    ax.text(8.00, 5.18, "Evidence products", ha="center", va="center", fontsize=9.2, weight="bold", color="#334155")

    _box(ax, (0.38, 4.30), (2.20, 0.58), "ChContactable body\ncollision model + shapes", face="#eff6ff", edge="#2563eb", weight="bold")
    _box(ax, (0.38, 3.42), (2.20, 0.58), "Contact material\nNSC or SMC", face="#fff7ed", edge="#ea580c", weight="bold")
    _box(ax, (0.38, 2.54), (2.20, 0.58), "Collision family/filter\nself-collision policy", face="#f8fafc", edge="#334155", weight="bold")
    _box(ax, (0.38, 1.28), (2.20, 0.82), "", face="#ffffff", edge="#64748b")
    _mini_collision_scene(ax, 1.48, 1.68)

    _box(ax, (3.18, 4.38), (2.54, 0.50), "CollisionSystem.Run()", face="#f8fafc", edge="#475569", weight="bold")
    _box(ax, (3.18, 3.62), (2.54, 0.50), "ReportContacts()\nfill contact container", face="#f8fafc", edge="#475569", weight="bold")
    _box(ax, (3.18, 2.86), (2.54, 0.50), "ReportContactCallback\npair + frame filter", face="#ecfdf5", edge="#16a34a", weight="bold")
    _box(ax, (3.18, 2.10), (2.54, 0.50), "Force logger\nworld/contact frame", face="#fef2f2", edge="#dc2626", weight="bold")
    _box(ax, (3.18, 1.34), (2.54, 0.50), "Event detector\nfirst/peak/separation", face="#f5f3ff", edge="#7c3aed", weight="bold")

    _arrow(ax, (2.58, 4.59), (3.18, 4.63), color="#2563eb")
    _arrow(ax, (2.58, 3.71), (3.18, 3.87), color="#ea580c", rad=-0.06)
    _arrow(ax, (2.58, 2.83), (3.18, 3.11), color="#334155", rad=0.08)
    _arrow(ax, (4.45, 4.38), (4.45, 4.12), color="#475569")
    _arrow(ax, (4.45, 3.62), (4.45, 3.36), color="#475569")
    _arrow(ax, (4.45, 2.86), (4.45, 2.60), color="#16a34a")
    _arrow(ax, (4.45, 2.10), (4.45, 1.84), color="#dc2626")

    _box(ax, (6.65, 4.38), (2.56, 0.54), "debug render\nshape + contact normal", face="#eff6ff", edge="#2563eb", weight="bold")
    _box(ax, (6.65, 3.44), (2.56, 0.54), "contact probe CSV\ncount + force components", face="#ecfdf5", edge="#16a34a", weight="bold")
    _box(ax, (6.65, 2.50), (2.56, 0.54), "material effect graph\npeak + duration", face="#fff7ed", edge="#ea580c", weight="bold")
    _box(ax, (6.65, 1.56), (2.56, 0.54), "event timeline\nfirst / dwell / separation", face="#f5f3ff", edge="#7c3aed", weight="bold")
    _box(ax, (6.65, 0.56), (2.56, 0.64), "", face="#ffffff", edge="#64748b")
    _mini_graph(ax, 7.93, 0.88)

    _arrow(ax, (5.72, 3.87), (6.65, 4.65), color="#2563eb", rad=0.08)
    _arrow(ax, (5.72, 3.11), (6.65, 3.71), color="#16a34a", rad=0.04)
    _arrow(ax, (5.72, 2.35), (6.65, 2.77), color="#ea580c", rad=-0.02)
    _arrow(ax, (5.72, 1.59), (6.65, 1.83), color="#7c3aed", rad=-0.04)

    _label(ax, "visual mesh and\ncollision envelope can differ", (1.34, 0.70), (1.52, 1.94), color="#2563eb")
    _label(ax, "plane_coord X is\ncontact normal", (2.88, 0.96), (1.61, 1.85), color="#16a34a")
    _label(ax, "NSC/SMC material\nmust match system method", (2.36, 3.18), (1.48, 3.71), color="#ea580c")
    _label(ax, "CSV needs pair,\nframe, source", (9.58, 3.76), (7.93, 3.71), color="#16a34a", ha="right")

    ax.text(
        5.0,
        0.12,
        "Catalog view: separate contact geometry, material/contact method, collision detection, reporter filtering, and evidence schemas.",
        ha="center",
        va="center",
        fontsize=8.1,
        color="#475569",
    )
    return save_figure(fig, output)


if __name__ == "__main__":
    print(render_collision_contact_measurement_catalog())
