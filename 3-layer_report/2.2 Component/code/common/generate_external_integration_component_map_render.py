from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

sys.path.append(str(Path(__file__).resolve().parents[1] / "common"))

from component_utils import IMAGES_RENDER, save_figure  # noqa: E402


def _box(ax, xy, size, label, *, face, edge, fontsize=8.5, weight="normal", linestyle="-"):
    patch = FancyBboxPatch(
        xy,
        size[0],
        size[1],
        boxstyle="round,pad=0.025,rounding_size=0.045",
        facecolor=face,
        edgecolor=edge,
        linestyle=linestyle,
        linewidth=1.45,
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


def _arrow(ax, start, end, *, color, rad=0.0, width=1.45):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=13,
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
        fontsize=8.2,
        color=color,
        bbox={"boxstyle": "round,pad=0.20", "facecolor": "white", "edgecolor": color, "linewidth": 1.0},
        arrowprops={"arrowstyle": "-", "color": color, "linewidth": 1.0, "shrinkA": 2, "shrinkB": 2},
        zorder=9,
    )


def render_external_integration_component_map() -> Path:
    output = IMAGES_RENDER / "external_integration_component_map.png"
    fig, ax = plt.subplots(figsize=(11.2, 6.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.2)
    ax.axis("off")

    ax.text(1.55, 5.38, "External source", ha="center", va="center", fontsize=9.5, color="#334155", weight="bold")
    ax.text(4.95, 5.38, "Adapter / Component boundary", ha="center", va="center", fontsize=9.5, color="#334155", weight="bold")
    ax.text(8.18, 5.38, "Chrono runtime target", ha="center", va="center", fontsize=9.5, color="#334155", weight="bold")

    rows = [
        (
            4.60,
            "#0284c7",
            "#f0f9ff",
            "Model files\nYAML / JSON / URDF / STEP",
            "Run Config / Model Spec\nAsset Import Component\n(indexed)",
            "Rover / Vehicle\nTerrain assets",
            "resolved_config.json\nunit + axis transform",
        ),
        (
            3.55,
            "#2563eb",
            "#eff6ff",
            "FMU package\nexternal dynamics",
            "Runtime / Control\nExternal Dynamics\n(runtime metadata)",
            "Simulation Runtime\nDriver/Input",
            "FMU variable map\nstep coupling",
        ),
        (
            2.50,
            "#ea580c",
            "#fff7ed",
            "ROS graph\nclock + topics",
            "Data / Control / Sensor I/O\nROS Bridge Component\n(indexed)",
            "DriverInputs\nSensor output",
            "topic, handler,\nupdate rate",
        ),
        (
            1.45,
            "#16a34a",
            "#ecfdf5",
            "Vehicle co-sim\nMBS / tire / terrain nodes",
            "Vehicle / Terrain\nCo-sim Boundary\n(indexed)",
            "Rover + Terrain\ncontact exchange",
            "sync timestep\nBODY/MESH interface",
        ),
        (
            0.40,
            "#9333ea",
            "#faf5ff",
            "Modal / FEA basis\nflexible structure",
            "Flexible Structure\nModal Adapter\n(indexed)",
            "Chassis / tire\nflexible upgrade",
            "basis, boundary nodes\nmode validation",
        ),
    ]

    for y, color, face, source, boundary, target, contract in rows:
        _box(ax, (0.36, y), (2.30, 0.64), source, face=face, edge=color, fontsize=7.8)
        _box(ax, (3.56, y), (2.78, 0.64), boundary, face=face, edge=color, fontsize=7.6, weight="bold", linestyle="--")
        _box(ax, (7.18, y), (2.38, 0.64), target, face="#f8fafc", edge="#334155", fontsize=7.8)
        _arrow(ax, (2.66, y + 0.32), (3.56, y + 0.32), color=color)
        _arrow(ax, (6.34, y + 0.32), (7.18, y + 0.32), color=color)
        label_xy = (4.95, y - 0.23)
        target_xy = (4.95, y)
        if source.startswith("Modal"):
            label_xy = (6.42, y + 0.28)
            target_xy = (6.34, y + 0.32)
        _label(ax, contract, label_xy, target_xy, color=color)

    _arrow(ax, (7.18, 1.77), (6.34, 1.77), color="#16a34a", rad=-0.18, width=1.05)
    _label(ax, "feedback loop", (6.86, 2.08), (6.70, 1.78), color="#16a34a")

    _box(
        ax,
        (7.38, 5.72),
        (2.16, 0.30),
        "dashed = indexed adapter",
        face="#f8fafc",
        edge="#64748b",
        fontsize=7.4,
        weight="bold",
        linestyle="--",
    )
    ax.annotate(
        "",
        xy=(6.34, 5.12),
        xytext=(7.38, 5.72),
        arrowprops={"arrowstyle": "-", "color": "#64748b", "linewidth": 1.0, "shrinkA": 2, "shrinkB": 2},
        zorder=8,
    )

    ax.text(
        5.0,
        5.95,
        "External integration component boundaries",
        ha="center",
        va="center",
        fontsize=12.8,
        color="#111827",
        weight="bold",
    )
    ax.text(
        5.0,
        0.04,
        "Each integration component must record ownership, update rate or timestep coupling, and fallback behavior.",
        ha="center",
        va="center",
        fontsize=8.4,
        color="#475569",
    )
    return save_figure(fig, output)


if __name__ == "__main__":
    print(render_external_integration_component_map())
