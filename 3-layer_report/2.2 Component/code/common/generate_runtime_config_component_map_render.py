from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

sys.path.append(str(Path(__file__).resolve().parents[1] / "common"))

from component_utils import IMAGES_RENDER, save_figure  # noqa: E402


def _box(ax, xy, size, label, *, facecolor, edgecolor, fontsize=9, weight="normal"):
    patch = FancyBboxPatch(
        xy,
        size[0],
        size[1],
        boxstyle="round,pad=0.03,rounding_size=0.04",
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=1.5,
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


def _arrow(ax, start, end, *, color="#475569", width=1.6, rad=0.0):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=13,
            linewidth=width,
            color=color,
            connectionstyle=f"arc3,rad={rad}",
            shrinkA=4,
            shrinkB=4,
            zorder=3,
        )
    )


def _label(ax, text, xytext, xy, *, color):
    ax.annotate(
        text,
        xy=xy,
        xytext=xytext,
        ha="center",
        va="center",
        fontsize=8.5,
        color=color,
        bbox={"boxstyle": "round,pad=0.22", "facecolor": "white", "edgecolor": color, "linewidth": 1.0},
        arrowprops={"arrowstyle": "-", "color": color, "linewidth": 1.0, "shrinkA": 2, "shrinkB": 2},
        zorder=8,
    )


def render_runtime_config_component_map() -> Path:
    output = IMAGES_RENDER / "runtime_config_component_map.png"
    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    runtime = _box(
        ax,
        (3.65, 3.35),
        (2.55, 1.02),
        "Simulation Runtime\nChSystem + solver + contact",
        facecolor="#dbeafe",
        edgecolor="#1d4ed8",
        fontsize=10,
        weight="bold",
    )
    config = _box(
        ax,
        (3.65, 1.72),
        (2.55, 1.02),
        "Run Config / Model Spec\nresolved parameters + units",
        facecolor="#dcfce7",
        edgecolor="#15803d",
        fontsize=10,
        weight="bold",
    )

    _box(ax, (0.45, 4.62), (2.1, 0.72), "Chrono build\nmodules + data path", facecolor="#f8fafc", edgecolor="#64748b")
    _box(ax, (0.45, 2.66), (2.1, 0.72), "Scenario input\nJSON/YAML/CLI", facecolor="#f8fafc", edgecolor="#64748b")
    _box(ax, (0.45, 0.82), (2.1, 0.72), "Reproducibility\nseed + profile id", facecolor="#f8fafc", edgecolor="#64748b")

    targets = [
        ((7.45, 4.82), (1.78, 0.58), "Rover / Vehicle\ncomponents", "#eff6ff", "#2563eb"),
        ((7.45, 3.82), (1.78, 0.58), "Terrain\ncomponents", "#ecfdf5", "#16a34a"),
        ((7.45, 2.82), (1.78, 0.58), "Collision / Contact\ncomponents", "#fef2f2", "#dc2626"),
        ((7.45, 1.82), (1.78, 0.58), "Sensor / Logging\ncomponents", "#fff7ed", "#ea580c"),
        ((7.45, 0.82), (1.78, 0.58), "Run metadata\nand report", "#f8fafc", "#334155"),
    ]
    for xy, size, label, facecolor, edgecolor in targets:
        _box(ax, xy, size, label, facecolor=facecolor, edgecolor=edgecolor, fontsize=8.8)

    _arrow(ax, (2.55, 4.98), (3.65, 4.03), color="#1d4ed8", rad=-0.08)
    _arrow(ax, (2.55, 3.02), (3.65, 2.25), color="#15803d", rad=0.05)
    _arrow(ax, (2.55, 1.18), (3.65, 2.02), color="#15803d", rad=-0.10)

    for y in (5.11, 4.11, 3.11, 2.11):
        _arrow(ax, (6.20, 3.86), (7.45, y), color="#1d4ed8", rad=0.05)
    for y in (5.11, 4.11, 3.11, 2.11, 1.11):
        _arrow(ax, (6.20, 2.23), (7.45, y), color="#15803d", rad=-0.05)

    _arrow(ax, (4.93, 3.35), (4.93, 2.74), color="#475569", width=1.2)

    _label(ax, "dt, gravity,\nsolver tolerance", (4.08, 5.15), (4.35, 4.36), color="#1d4ed8")
    _label(ax, "NSC/SMC and\ncollision backend", (6.78, 4.72), (5.78, 4.34), color="#1d4ed8")
    _label(ax, "unit-checked\nresolved_config.json", (2.95, 0.56), (4.15, 1.72), color="#15803d")
    _label(ax, "metadata owns the\nreplay contract", (6.62, 0.48), (7.45, 1.11), color="#334155")

    ax.text(
        5.0,
        5.72,
        "Runtime/Config components make every physical component reproducible",
        ha="center",
        va="center",
        fontsize=13,
        color="#111827",
        weight="bold",
    )
    ax.text(
        5.0,
        0.13,
        "Component catalog view: runtime owns physics context; config owns parameter provenance.",
        ha="center",
        va="center",
        fontsize=8.5,
        color="#475569",
    )
    return save_figure(fig, output)


if __name__ == "__main__":
    print(render_runtime_config_component_map())
