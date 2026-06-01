from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

from component_utils import save_figure


ROOT = Path(__file__).resolve().parents[2]
MERMAID_DIR = ROOT / "images" / "mermaid_rendered"


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
            mutation_scale=13,
            linewidth=width,
            color=color,
            connectionstyle=f"arc3,rad={rad}",
            shrinkA=3,
            shrinkB=3,
            zorder=3,
        )
    )


def render_component_card_structure() -> Path:
    output = MERMAID_DIR / "2_2_mermaid_02.png"
    fig, ax = plt.subplots(figsize=(12.5, 6.3))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.1)
    ax.axis("off")

    ax.text(6.0, 5.82, "Component catalog card structure", ha="center", va="center", fontsize=13.2, weight="bold", color="#111827")
    ax.text(
        6.0,
        0.16,
        "2.1 Command knowledge enters as inputs; 2.2 Component cards own physical/data contracts; System scenarios consume validated outputs.",
        ha="center",
        va="center",
        fontsize=8.0,
        color="#475569",
    )

    ax.add_patch(Rectangle((0.34, 1.02), 2.80, 4.28, facecolor="#eff6ff", edgecolor="none", alpha=0.70, zorder=0))
    ax.add_patch(Rectangle((3.54, 0.74), 4.92, 4.84, facecolor="#f8fafc", edgecolor="none", alpha=0.95, zorder=0))
    ax.add_patch(Rectangle((8.88, 1.02), 2.78, 4.28, facecolor="#ecfdf5", edgecolor="none", alpha=0.65, zorder=0))

    ax.text(1.74, 5.18, "Chrono Command inputs", ha="center", va="center", fontsize=9.0, color="#1d4ed8", weight="bold")
    ax.text(6.00, 5.44, "Component Card", ha="center", va="center", fontsize=10.2, color="#334155", weight="bold")
    ax.text(10.27, 5.18, "System Scenario outputs", ha="center", va="center", fontsize=9.0, color="#15803d", weight="bold")

    _box(ax, (0.70, 4.34), (2.08, 0.48), "API call\nconstructor / setter", face="#ffffff", edge="#2563eb", fontsize=7.3)
    _box(ax, (0.70, 3.54), (2.08, 0.48), "object creation\nbody / link / terrain", face="#ffffff", edge="#2563eb", fontsize=7.3)
    _box(ax, (0.70, 2.74), (2.08, 0.48), "state update\nDoStep / Advance", face="#ffffff", edge="#2563eb", fontsize=7.3)
    _box(ax, (0.70, 1.94), (2.08, 0.48), "raw parameters\nnumbers / files", face="#ffffff", edge="#2563eb", fontsize=7.3)

    _box(ax, (3.78, 4.50), (1.90, 0.50), "Physical\nmass, inertia, pose\nfixed/dynamic", face="#dbeafe", edge="#2563eb", fontsize=7.05, weight="bold")
    _box(ax, (6.26, 4.50), (1.82, 0.50), "Connection\njoint, motor\nconstraint", face="#e0f2fe", edge="#0284c7", fontsize=7.05, weight="bold")
    _box(ax, (3.78, 3.62), (1.90, 0.50), "Contact\ncollision shape\nmaterial, envelope", face="#fee2e2", edge="#dc2626", fontsize=7.05, weight="bold")
    _box(ax, (6.26, 3.62), (1.82, 0.50), "Visual\nrender shape\ncolor, camera", face="#f3e8ff", edge="#7c3aed", fontsize=7.05, weight="bold")
    _box(ax, (3.78, 2.74), (1.90, 0.50), "Data\nCSV schema\ngraph, metadata", face="#fef3c7", edge="#d97706", fontsize=7.05, weight="bold")
    _box(ax, (6.26, 2.74), (1.82, 0.50), "Validation\nrender, probe CSV\nsanity check", face="#dcfce7", edge="#16a34a", fontsize=7.05, weight="bold")
    _box(ax, (4.78, 1.56), (2.24, 0.56), "Owner + boundary\nowns / depends_on / outputs\nfailure modes / upgrade path", face="#ffffff", edge="#334155", fontsize=7.35, weight="bold")

    _box(ax, (9.20, 4.34), (2.08, 0.48), "assembled model\nrover + terrain + sensor", face="#ffffff", edge="#15803d", fontsize=7.3)
    _box(ax, (9.20, 3.54), (2.08, 0.48), "simulation loop\nsync + advance order", face="#ffffff", edge="#15803d", fontsize=7.3)
    _box(ax, (9.20, 2.74), (2.08, 0.48), "evidence bundle\nCSV / graph / PNG", face="#ffffff", edge="#15803d", fontsize=7.3)
    _box(ax, (9.20, 1.94), (2.08, 0.48), "run metadata\nversion + modules", face="#ffffff", edge="#15803d", fontsize=7.3)

    for y in (4.58, 3.78, 2.98):
        _arrow(ax, (2.78, y), (3.78, y), color="#2563eb")
    _arrow(ax, (2.78, 2.18), (4.78, 1.84), color="#2563eb", rad=-0.08)
    _arrow(ax, (8.08, 4.58), (9.20, 4.58), color="#15803d")
    _arrow(ax, (8.08, 3.78), (9.20, 3.78), color="#15803d")
    _arrow(ax, (8.08, 2.98), (9.20, 2.98), color="#15803d")
    _arrow(ax, (7.02, 1.84), (9.20, 2.18), color="#15803d", rad=0.08)
    _arrow(ax, (5.68, 4.50), (5.70, 2.12), color="#334155", rad=0.05)
    _arrow(ax, (6.26, 4.50), (6.98, 2.12), color="#334155", rad=-0.05)
    _arrow(ax, (4.72, 2.74), (5.56, 2.12), color="#d97706", rad=0.02)
    _arrow(ax, (7.18, 2.74), (6.44, 2.12), color="#16a34a", rad=-0.02)

    ax.text(3.30, 5.04, "compose", ha="center", va="center", fontsize=8.0, color="#2563eb", weight="bold")
    ax.text(8.64, 5.04, "place", ha="center", va="center", fontsize=8.0, color="#15803d", weight="bold")
    ax.text(
        6.00,
        0.70,
        "A Component card is not a raw API wrapper; it is the smallest reusable ownership and validation unit.",
        ha="center",
        va="center",
        fontsize=8.2,
        color="#334155",
        bbox={"boxstyle": "round,pad=0.22", "facecolor": "white", "edgecolor": "#64748b", "linewidth": 0.9},
        zorder=8,
    )

    return save_figure(fig, output)


if __name__ == "__main__":
    print(render_component_card_structure())
