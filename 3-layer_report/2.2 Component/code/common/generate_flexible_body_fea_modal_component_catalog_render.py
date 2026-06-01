from __future__ import annotations

import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle

sys.path.append(str(Path(__file__).resolve().parents[1] / "common"))

from component_utils import IMAGES_RENDER, save_figure  # noqa: E402


def _box(ax, xy, size, label, *, face="#ffffff", edge="#334155", fontsize=6.7, weight="normal", linestyle="-"):
    patch = FancyBboxPatch(
        xy,
        size[0],
        size[1],
        boxstyle="round,pad=0.024,rounding_size=0.040",
        facecolor=face,
        edgecolor=edge,
        linestyle=linestyle,
        linewidth=1.15,
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


def _arrow(ax, start, end, *, color="#475569", width=1.05, rad=0.0):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=10.5,
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
        fontsize=6.6,
        color=color,
        bbox={"boxstyle": "round,pad=0.15", "facecolor": "white", "edgecolor": color, "linewidth": 0.8},
        arrowprops={"arrowstyle": "-", "color": color, "linewidth": 0.85, "shrinkA": 2, "shrinkB": 2},
        zorder=12,
    )


def _mesh_icon(ax, x, y, kind, color):
    if kind == "cable":
        pts = [(x + i * 0.15, y + 0.08 + 0.04 * math.sin(i * 0.9)) for i in range(7)]
        for p1, p2 in zip(pts, pts[1:]):
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=color, linewidth=1.6, zorder=7)
        for px, py in pts:
            ax.add_patch(Circle((px, py), 0.026, facecolor="#ffffff", edgecolor=color, linewidth=0.8, zorder=8))
    elif kind == "shell":
        base = [(x, y), (x + 0.78, y + 0.04), (x + 0.86, y + 0.34), (x + 0.10, y + 0.30)]
        ax.add_patch(Polygon(base, facecolor="#dbeafe", edgecolor=color, linewidth=0.9, zorder=6))
        for i in range(1, 4):
            ax.plot([x + 0.04 + i * 0.18, x + 0.11 + i * 0.18], [y + 0.02, y + 0.30], color=color, linewidth=0.55, zorder=7)
        for j in range(1, 3):
            ax.plot([x + 0.03, x + 0.82], [y + j * 0.10, y + 0.04 + j * 0.10], color=color, linewidth=0.55, zorder=7)
    elif kind == "solid":
        ax.add_patch(Rectangle((x + 0.08, y + 0.02), 0.58, 0.30, facecolor="#fef3c7", edgecolor=color, linewidth=0.9, zorder=6))
        ax.add_patch(Polygon([(x + 0.08, y + 0.32), (x + 0.22, y + 0.46), (x + 0.80, y + 0.46), (x + 0.66, y + 0.32)], facecolor="#fde68a", edgecolor=color, linewidth=0.9, zorder=6))
        ax.add_patch(Polygon([(x + 0.66, y + 0.02), (x + 0.80, y + 0.16), (x + 0.80, y + 0.46), (x + 0.66, y + 0.32)], facecolor="#fcd34d", edgecolor=color, linewidth=0.9, zorder=6))
        for i in range(3):
            ax.plot([x + 0.18 + i * 0.16, x + 0.32 + i * 0.16], [y + 0.02, y + 0.46], color="#b45309", linewidth=0.45, alpha=0.8, zorder=7)
    else:
        ax.add_patch(Rectangle((x + 0.04, y + 0.06), 0.66, 0.22, facecolor="#e0e7ff", edgecolor=color, linewidth=0.9, zorder=6))
        for i in range(4):
            ax.plot([x + 0.12 + i * 0.15, x + 0.12 + i * 0.15], [y + 0.06, y + 0.28], color=color, linewidth=0.55, zorder=7)
        for px in (x + 0.05, x + 0.70):
            ax.add_patch(Circle((px, y + 0.17), 0.045, facecolor="#ffffff", edgecolor="#4f46e5", linewidth=0.8, zorder=8))
        ax.plot([x + 0.20, x + 0.62], [y + 0.38, y + 0.40], color="#4f46e5", linewidth=1.4, zorder=7)


def render_flexible_body_fea_modal_component_catalog() -> Path:
    output = IMAGES_RENDER / "flexible_body_fea_modal_component_catalog.png"
    fig, ax = plt.subplots(figsize=(11.8, 6.7))
    ax.set_xlim(0, 11.2)
    ax.set_ylim(0, 6.45)
    ax.axis("off")

    ax.text(5.6, 6.14, "Flexible body / FEA / Modal component catalog", ha="center", va="center", fontsize=13.0, weight="bold", color="#111827")
    ax.text(
        5.6,
        5.84,
        "Flexible evidence is valid only when mesh identity, element/material law, boundary/load contract, solver metadata, and deformation or modal artifacts agree.",
        ha="center",
        va="center",
        fontsize=7.8,
        color="#475569",
    )

    headers = [
        ("Use case", 0.42, 1.48, "#f8fafc", "#475569"),
        ("ChMesh owner\nnodes + elements", 2.30, 1.72, "#e0f2fe", "#0891b2"),
        ("Element + material\ncontract", 4.48, 1.82, "#ecfdf5", "#059669"),
        ("Boundary / load /\nsolver gate", 6.84, 1.72, "#ede9fe", "#7c3aed"),
        ("Evidence artifact", 8.92, 1.82, "#fff7ed", "#ea580c"),
    ]
    for title, x, w, face, edge in headers:
        _box(ax, (x, 5.18), (w, 0.46), title, face=face, edge=edge, fontsize=7.0, weight="bold")

    rows = [
        {
            "y": 4.28,
            "color": "#0891b2",
            "kind": "cable",
            "use": "Cable / beam\nwire, shaft, link",
            "mesh": "ChMesh\nChNodeFEAxyzD\nor xyzrot",
            "elem": "Cable/Beam\nsection A/I/E/rho\ndamping",
            "gate": "node constraints\nbody attachment\nsmall dt",
            "ev": "deflection curve\nend force / stress\nmesh render",
        },
        {
            "y": 3.18,
            "color": "#2563eb",
            "kind": "shell",
            "use": "Shell / thin part\ntire carcass, panel",
            "mesh": "shell node grid\nxyzD / xyzrot\nconnectivity",
            "elem": "ANCF/Reissner/BST\nthickness layers\nmaterial law",
            "gate": "edge boundary\npressure/contact\nsolver residual",
            "ev": "strain/stress map\ndeformed shape\nlayer metadata",
        },
        {
            "y": 2.08,
            "color": "#d97706",
            "kind": "solid",
            "use": "Solid volume\nrubber, metal, soil block",
            "mesh": "tetra / hexa mesh\nnode count\nvolume domain",
            "elem": "corotational or ANCF\nelastic/plastic law\nintegration",
            "gate": "fixed nodes\nloads/contact\nlinear solver",
            "ev": "stress/strain field\nreaction force\nmesh hash",
        },
        {
            "y": 0.98,
            "color": "#4f46e5",
            "kind": "modal",
            "use": "Modal reduced\nflexible subassembly",
            "mesh": "ChModalAssembly\nboundary vs internal\nitems",
            "elem": "basis/modes\nHerting or\nCraig-Bampton",
            "gate": "modal solver\nboundary map\ndamping model",
            "ev": "mode shapes\nfrequencies\nreduction log",
        },
    ]

    for idx, row in enumerate(rows):
        y = row["y"]
        color = row["color"]
        ax.add_patch(Rectangle((0.28, y - 0.20), 10.60, 0.84, facecolor="#ffffff" if idx % 2 == 0 else "#f8fafc", edgecolor="#e5e7eb", linewidth=0.5, zorder=0))
        _box(ax, (0.52, y), (1.46, 0.46), row["use"], face="#ffffff", edge=color, fontsize=6.35, weight="bold")
        _mesh_icon(ax, 2.16, y + 0.04, row["kind"], color)
        _box(ax, (2.96, y - 0.04), (1.46, 0.54), row["mesh"], face="#ffffff", edge="#0891b2", fontsize=6.2, weight="bold")
        _box(ax, (4.74, y - 0.06), (1.68, 0.58), row["elem"], face="#ffffff", edge="#059669", fontsize=6.0)
        _box(ax, (7.02, y - 0.06), (1.48, 0.58), row["gate"], face="#ffffff", edge="#7c3aed", fontsize=6.0)
        _box(ax, (9.06, y - 0.06), (1.62, 0.58), row["ev"], face="#fff7ed", edge="#ea580c", fontsize=5.9)

        _arrow(ax, (1.98, y + 0.23), (2.96, y + 0.23), color=color)
        _arrow(ax, (4.42, y + 0.23), (4.74, y + 0.23), color=color)
        _arrow(ax, (6.42, y + 0.23), (7.02, y + 0.23), color=color)
        _arrow(ax, (8.50, y + 0.23), (9.06, y + 0.23), color=color)

    _box(ax, (2.22, 0.16), (1.92, 0.40), "module_availability:\nfea/modal must be explicit", face="#dbeafe", edge="#0891b2", fontsize=6.4, weight="bold")
    _box(ax, (4.54, 0.16), (1.88, 0.40), "material law:\nrho, E, nu, thickness/layers", face="#dcfce7", edge="#059669", fontsize=6.4, weight="bold")
    _box(ax, (6.90, 0.16), (1.84, 0.40), "boundary map:\nnode/body/link/load ids", face="#ede9fe", edge="#7c3aed", fontsize=6.4, weight="bold")
    _box(ax, (9.08, 0.16), (1.66, 0.40), "live evidence:\nnot just mesh exists", face="#ffedd5", edge="#ea580c", fontsize=6.4, weight="bold")
    _arrow(ax, (4.14, 0.36), (4.54, 0.36), color="#0891b2")
    _arrow(ax, (6.42, 0.36), (6.90, 0.36), color="#059669")
    _arrow(ax, (8.74, 0.36), (9.08, 0.36), color="#7c3aed")

    _callout(ax, "ChMesh owns\nnodes + elements", (3.36, 4.96), (3.42, 4.54), color="#0891b2")
    _callout(ax, "element type and\nmaterial law required", (5.56, 4.96), (5.58, 4.54), color="#059669")
    _callout(ax, "boundary nodes connect\nto ChBody / links / loads", (7.82, 4.96), (7.76, 4.54), color="#7c3aed")
    _callout(ax, "deformation, stress,\nor modes prove it", (10.42, 4.96), (9.94, 4.54), color="#ea580c", ha="right")

    ax.text(
        5.6,
        0.02,
        "Fallback rule: mesh screenshots or imported basis files are indexed evidence until a live solve records deformation, stress, residuals, or modal frequencies.",
        ha="center",
        va="bottom",
        fontsize=7.6,
        color="#475569",
    )
    return save_figure(fig, output)


if __name__ == "__main__":
    print(render_flexible_body_fea_modal_component_catalog())
