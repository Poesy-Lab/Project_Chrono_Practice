from __future__ import annotations

import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle

sys.path.append(str(Path(__file__).resolve().parents[1] / "common"))

from component_utils import IMAGES_RENDER, save_figure  # noqa: E402


def _box(ax, xy, size, label, *, face, edge, fontsize=7.3, weight="normal", linestyle="-"):
    patch = FancyBboxPatch(
        xy,
        size[0],
        size[1],
        boxstyle="round,pad=0.024,rounding_size=0.042",
        facecolor=face,
        edgecolor=edge,
        linestyle=linestyle,
        linewidth=1.2,
        zorder=5,
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


def _arrow(ax, start, end, *, color="#475569", width=1.1, rad=0.0, style="-|>"):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle=style,
            mutation_scale=11,
            linewidth=width,
            color=color,
            connectionstyle=f"arc3,rad={rad}",
            shrinkA=3,
            shrinkB=3,
            zorder=4,
        )
    )


def _callout(ax, text, xytext, target, *, color, ha="center"):
    ax.annotate(
        text,
        xy=target,
        xytext=xytext,
        ha=ha,
        va="center",
        fontsize=7.4,
        color=color,
        bbox={"boxstyle": "round,pad=0.16", "facecolor": "white", "edgecolor": color, "linewidth": 0.8},
        arrowprops={"arrowstyle": "-", "color": color, "linewidth": 0.9, "shrinkA": 2, "shrinkB": 1},
        zorder=10,
    )


def _wheel(ax, center):
    ax.add_patch(Circle(center, 0.10, facecolor="#111827", edgecolor="#020617", linewidth=0.7, zorder=8))
    ax.add_patch(Circle(center, 0.045, facecolor="#e5e7eb", edgecolor="#64748b", linewidth=0.6, zorder=9))


def _terrain_icon(ax, x, y, kind, color):
    ax.add_patch(Rectangle((x, y), 0.86, 0.20, facecolor="#f8fafc", edgecolor="#94a3b8", linewidth=0.7, zorder=2))
    if kind == "scm":
        for i in range(6):
            xx = x + 0.06 + i * 0.15
            ax.plot([xx, xx], [y + 0.02, y + 0.18], color="#86efac", linewidth=0.65, zorder=3)
        xs = [x + 0.04 + i * 0.075 for i in range(11)]
        ys = [y + 0.16 - 0.07 * math.exp(-((i - 5) / 1.8) ** 2) for i in range(11)]
        ax.plot(xs, ys, color=color, linewidth=1.8, zorder=7)
    elif kind == "dem":
        for i in range(17):
            px = x + 0.05 + (i % 7) * 0.12
            py = y + 0.04 + (i // 7) * 0.07 + 0.01 * math.sin(i)
            ax.add_patch(Circle((px, py), 0.022, facecolor=color, edgecolor="#9a3412", linewidth=0.4, zorder=7))
    elif kind == "fea":
        for i in range(4):
            ax.plot([x + 0.04, x + 0.82], [y + 0.04 + i * 0.045, y + 0.03 + i * 0.050], color=color, linewidth=0.8, zorder=7)
        for i in range(5):
            ax.plot([x + 0.08 + i * 0.17, x + 0.04 + i * 0.17], [y + 0.03, y + 0.18], color=color, linewidth=0.7, zorder=7)
        ax.add_patch(Polygon([(x + 0.34, y + 0.18), (x + 0.58, y + 0.17), (x + 0.52, y + 0.11), (x + 0.30, y + 0.11)], facecolor="#e9d5ff", edgecolor="#7e22ce", linewidth=0.7, zorder=8))
    elif kind == "crm":
        ax.add_patch(Rectangle((x + 0.18, y + 0.02), 0.52, 0.16, facecolor="#cffafe", edgecolor="#0891b2", linewidth=0.7, zorder=3))
        for i in range(18):
            px = x + 0.05 + (i % 7) * 0.12
            py = y + 0.04 + (i // 7) * 0.055 + 0.010 * math.sin(i * 0.7)
            ax.add_patch(Circle((px, py), 0.018, facecolor=color, edgecolor="#0e7490", linewidth=0.35, zorder=7))
    _wheel(ax, (x + 0.43, y + 0.30))


def render_terrain_advanced_selection_catalog() -> Path:
    output = IMAGES_RENDER / "terrain_advanced_selection_catalog.png"
    fig, ax = plt.subplots(figsize=(11.6, 6.6))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 6.45)
    ax.axis("off")

    ax.text(5.5, 6.12, "Advanced terrain official-module evidence gates", ha="center", va="center", fontsize=13.0, weight="bold", color="#111827")
    ax.text(
        5.5,
        0.14,
        "Terrain choice is validated only after module availability, live evidence, and fallback wording agree.",
        ha="center",
        va="center",
        fontsize=8.0,
        color="#475569",
    )

    headers = [
        ("Terrain choice", 0.46, 1.95),
        ("Official module gate", 2.72, 2.05),
        ("Required live evidence", 5.12, 2.32),
        ("Allowed fallback label", 7.94, 2.58),
    ]
    for text, x, w in headers:
        _box(ax, (x, 5.46), (w, 0.38), text, face="#e2e8f0", edge="#475569", fontsize=8.0, weight="bold")

    rows = [
        {
            "y": 4.54,
            "title": "SCMTerrain\nsoil grid",
            "kind": "scm",
            "color": "#16a34a",
            "gate": "Vehicle module\nSCMTerrain class",
            "evidence": "soil profile id\ngrid spacing\nwheel load\nsinkage/rut probe",
            "fallback": "concept / schema\nnot live soil validation",
        },
        {
            "y": 3.46,
            "title": "GranularTerrain\nDEM particles",
            "kind": "dem",
            "color": "#ea580c",
            "gate": "DEM / Granular\nGPU or Multicore",
            "evidence": "particle count/radius\nactive domain\nsolver dt\nsource=pychrono_live",
            "fallback": "indexed extension\nor analytic schema only",
        },
        {
            "y": 2.38,
            "title": "FEATerrain\nmesh domain",
            "kind": "fea",
            "color": "#9333ea",
            "gate": "FEA module\nFEATerrain class",
            "evidence": "mesh id/path\nelement type\nmaterial law\nsolver settings",
            "fallback": "mesh card only\nnot deformation evidence",
        },
        {
            "y": 1.30,
            "title": "CRMTerrain\nFSI / SPH",
            "kind": "crm",
            "color": "#0891b2",
            "gate": "FSI-SPH / CRM\nCRMTerrain class",
            "evidence": "SPH spacing\nBCE files\nactive domain\ncoupling advance order",
            "fallback": "concept indexed\nnot coupled SPH run",
        },
    ]

    for row in rows:
        y = row["y"]
        color = row["color"]
        ax.add_patch(Rectangle((0.34, y - 0.17), 10.32, 0.82, facecolor="#ffffff" if int(y * 10) % 2 else "#f8fafc", edgecolor="#e5e7eb", linewidth=0.5, zorder=0))
        _box(ax, (0.58, y), (1.52, 0.46), row["title"], face="#ffffff", edge=color, fontsize=7.35, weight="bold")
        _terrain_icon(ax, 2.16, y + 0.09, row["kind"], color)
        _box(ax, (2.96, y), (1.72, 0.46), row["gate"], face="#ffffff", edge=color, fontsize=6.95, weight="bold")
        _box(ax, (5.32, y - 0.06), (1.94, 0.58), row["evidence"], face="#ffffff", edge=color, fontsize=6.75)
        _box(ax, (8.28, y - 0.02), (1.98, 0.50), row["fallback"], face="#fef3c7", edge="#b45309", fontsize=6.75, linestyle="--")

        _arrow(ax, (2.10, y + 0.23), (2.96, y + 0.23), color=color)
        _arrow(ax, (4.68, y + 0.23), (5.32, y + 0.23), color=color)
        _arrow(ax, (4.68, y + 0.05), (8.28, y + 0.08), color="#b45309", rad=0.08, style="-|>")

    _box(ax, (4.68, 0.64), (2.02, 0.38), "Gate passes:\nmodule-backed evidence", face="#dcfce7", edge="#15803d", fontsize=7.0, weight="bold")
    _box(ax, (7.34, 0.64), (2.02, 0.38), "Gate fails:\nfallback is not validation", face="#fee2e2", edge="#dc2626", fontsize=7.0, weight="bold")
    _arrow(ax, (6.70, 0.84), (7.34, 0.84), color="#dc2626")

    _callout(ax, "module_availability\nmust be true", (3.88, 5.12), (3.82, 4.54), color="#15803d")
    _callout(ax, "live evidence\nrequired", (6.50, 5.12), (6.30, 4.54), color="#2563eb")
    _callout(ax, "fallback is\nnot validation", (9.70, 5.12), (9.28, 4.78), color="#dc2626")

    return save_figure(fig, output)


if __name__ == "__main__":
    print(render_terrain_advanced_selection_catalog())
