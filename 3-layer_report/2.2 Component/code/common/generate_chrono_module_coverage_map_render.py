from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

sys.path.append(str(Path(__file__).resolve().parents[1] / "common"))

from component_utils import IMAGES_RENDER, save_figure  # noqa: E402


def _box(ax, x, y, w, h, text, *, face, edge, size=8.8, weight="normal"):
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.025,rounding_size=0.045",
        facecolor=face,
        edgecolor=edge,
        linewidth=1.35,
        zorder=4,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size, color="#111827", weight=weight, zorder=5)
    return patch


def _arrow(ax, start, end, *, color="#475569", rad=0.0, width=1.25):
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


def _label(ax, text, xytext, xy, *, color):
    ax.annotate(
        text,
        xy=xy,
        xytext=xytext,
        ha="center",
        va="center",
        fontsize=8.4,
        color=color,
        bbox={"boxstyle": "round,pad=0.20", "facecolor": "white", "edgecolor": color, "linewidth": 1.0},
        arrowprops={"arrowstyle": "-", "color": color, "linewidth": 1.0, "shrinkA": 2, "shrinkB": 2},
        zorder=8,
    )


def render_chrono_module_coverage_map() -> Path:
    output = IMAGES_RENDER / "chrono_module_coverage_map.png"
    fig, ax = plt.subplots(figsize=(11.8, 7.7))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis("off")

    ax.text(
        5.0,
        7.72,
        "Project Chrono module coverage in the 2.2 Component catalog",
        ha="center",
        va="center",
        fontsize=13,
        color="#111827",
        weight="bold",
    )

    headers = [
        ("Official module group", 0.38, 2.55),
        ("Coverage status", 2.98, 1.62),
        ("Catalog owner", 4.76, 2.08),
        ("Metadata / fallback contract", 7.10, 2.52),
    ]
    for text, x, w in headers:
        _box(ax, x, 7.12, w, 0.38, text, face="#e2e8f0", edge="#475569", size=8.7, weight="bold")

    status_style = {
        "Covered": ("#dcfce7", "#15803d"),
        "Indexed": ("#fef3c7", "#b45309"),
        "Runtime metadata": ("#dbeafe", "#2563eb"),
        "Out of scope": ("#f1f5f9", "#64748b"),
    }
    rows = [
        ("Core dynamics", "Covered", "2.2.1, 2.2.2, 2.2.4", "system/body/link/motor/shape contract"),
        ("Vehicle", "Covered", "2.2.2, 2.2.3", "chassis, tire, terrain, driveline"),
        ("Vehicle Co-sim", "Indexed", "2.2.2/2.2.3 extension", "MBS/tire/terrain node, sync timestep"),
        ("Robot", "Covered", "2.2.2", "built-in rover/robot asset policy"),
        ("Sensor", "Covered", "2.2.5", "manager, sensors, filters, writers"),
        ("ROS bridge", "Indexed", "2.2.5 control/I/O extension", "topics, handlers, update rate, clock"),
        ("VSG / Irrlicht", "Covered", "2.2.5", "render backend and screenshot artifact"),
        ("Postprocess", "Indexed", "2.2.5 extension", "POV-Ray / GNUplot export path"),
        ("Parsers / URDF / YAML", "Indexed", "2.2.1 Runtime/Config", "raw path, schema, resolved_config hash"),
        ("CASCADE / STEP", "Indexed", "2.2.1 asset import", "CAD path, units, axis transform, mesh policy"),
        ("FEA", "Indexed", "2.2.2, 2.2.3 extension", "FEA tire/terrain mesh and material law"),
        ("Modal", "Indexed", "2.2.2 flexible extension", "modal basis, boundary nodes, validation mode"),
        ("DEM / Granular", "Indexed", "2.2.3 Advanced Terrain", "particle radius, domain, timestep"),
        ("FSI / CRM / SPH", "Indexed", "2.2.3 Advanced Terrain", "coupling timestep, spacing, active domain"),
        ("Multicore", "Runtime metadata", "2.2.1, 2.2.4", "backend, threads, collision system"),
        ("FMI / FMU", "Runtime metadata", "2.2.1 control extension", "FMU file, FMI version, variable map"),
        ("Synchrono / Matlab / CSharp / PardisoMKL", "Out of scope", "record only if used", "module_availability and fallback_policy"),
    ]

    y = 6.66
    row_h = 0.36
    for idx, (module, status, owner, contract) in enumerate(rows):
        fill = "#ffffff" if idx % 2 == 0 else "#f8fafc"
        ax.add_patch(FancyBboxPatch((0.30, y - 0.04), 9.35, row_h, boxstyle="square,pad=0.0", facecolor=fill, edgecolor="#e5e7eb", linewidth=0.5, zorder=1))
        ax.text(0.45, y + 0.13, module, ha="left", va="center", fontsize=7.9, color="#111827", zorder=5)
        face, edge = status_style[status]
        _box(ax, 3.05, y, 1.48, 0.26, status, face=face, edge=edge, size=6.8, weight="bold")
        ax.text(4.88, y + 0.13, owner, ha="left", va="center", fontsize=7.4, color="#111827", zorder=5)
        ax.text(7.18, y + 0.13, contract, ha="left", va="center", fontsize=7.1, color="#111827", zorder=5)
        y -= row_h

    _box(
        ax,
        1.18,
        0.32,
        7.70,
        0.48,
        "Covered modules are explained in main chapters; indexed modules stay discoverable through dependency and fallback metadata.",
        face="#f8fafc",
        edge="#334155",
        size=8.0,
        weight="bold",
    )

    ax.text(
        5.0,
        0.08,
        "This is a catalog coverage map, not a build manifest; exact availability is stored per run in Runtime/Config metadata.",
        ha="center",
        va="center",
        fontsize=8.3,
        color="#475569",
    )
    return save_figure(fig, output)


if __name__ == "__main__":
    print(render_chrono_module_coverage_map())
