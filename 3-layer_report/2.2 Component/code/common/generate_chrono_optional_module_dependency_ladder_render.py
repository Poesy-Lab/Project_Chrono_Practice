from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

sys.path.append(str(Path(__file__).resolve().parents[1] / "common"))

from component_utils import IMAGES_RENDER, save_figure  # noqa: E402


def _box(ax, xy, size, label, *, face, edge, fontsize=8.0, weight="normal", linestyle="-"):
    patch = FancyBboxPatch(
        xy,
        size[0],
        size[1],
        boxstyle="round,pad=0.025,rounding_size=0.045",
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


def _arrow(ax, start, end, *, color="#475569", width=1.15, rad=0.0, style="-|>"):
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
            zorder=3,
        )
    )


def _callout(ax, text, xytext, target, *, color, ha="center"):
    ax.annotate(
        text,
        xy=target,
        xytext=xytext,
        ha=ha,
        va="center",
        fontsize=7.25,
        color=color,
        bbox={"boxstyle": "round,pad=0.18", "facecolor": "white", "edgecolor": color, "linewidth": 0.8},
        arrowprops={"arrowstyle": "-", "color": color, "linewidth": 0.85, "shrinkA": 2, "shrinkB": 2},
        zorder=9,
    )


def render_chrono_optional_module_dependency_ladder() -> Path:
    output = IMAGES_RENDER / "chrono_optional_module_dependency_ladder.png"
    fig, ax = plt.subplots(figsize=(12.4, 6.8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.5)
    ax.axis("off")

    ax.text(6.0, 6.18, "Chrono optional module dependency ladder", ha="center", va="center", fontsize=13.0, weight="bold", color="#111827")
    ax.text(
        6.0,
        5.88,
        "Read across each row: a module gate allows a Component family to claim only the evidence artifacts listed for that row.",
        ha="center",
        va="center",
        fontsize=8.1,
        color="#475569",
    )
    ax.text(
        6.0,
        0.13,
        "Catalog rule: module availability is runtime metadata; Component evidence is valid only when the matching module-backed artifact exists.",
        ha="center",
        va="center",
        fontsize=8.0,
        color="#475569",
    )

    columns = [
        (0.42, 1.58, "Module group"),
        (2.16, 1.92, "Build / runtime gate"),
        (4.24, 1.74, "Component owner"),
        (6.14, 2.52, "Evidence artifact"),
        (8.82, 2.72, "Claim policy"),
    ]
    header_y = 5.30
    for x, width, title in columns:
        ax.add_patch(Rectangle((x, header_y), width, 0.34, facecolor="#e2e8f0", edgecolor="#cbd5e1", linewidth=0.8, zorder=1))
        ax.text(x + width / 2, header_y + 0.17, title, ha="center", va="center", fontsize=7.0, color="#334155", weight="bold", zorder=2)

    rows = [
        (
            "Core",
            "Chrono core\nalways indexed",
            "runtime.system\ncore.body / link",
            "run_metadata.json\nsolver + collision manifests",
            "May support fallback evidence;\nlive claim needs source tag",
            "#334155",
            "#f8fafc",
        ),
        (
            "Vehicle / Robot / VSG",
            "VEHICLE, ROBOT,\nVSG or Irrlicht",
            "vehicle.*\nrobot visual assets",
            "vehicle manifests\nVSG capture manifest",
            "VSG screenshots can be live\nwhen capture hash is present",
            "#2563eb",
            "#eff6ff",
        ),
        (
            "Sensor",
            "SENSOR + GPU\nruntime device",
            "sensor.manager\nsensor.output_writer",
            "sensor_manifest.json\nscene/timing/filter maps",
            "Schema/layout only until\nraw frames or clouds exist",
            "#16a34a",
            "#f0fdf4",
        ),
        (
            "Flexible / Modal",
            "FEA, MODAL\nbasis availability",
            "flex.mesh\nflex.modal_reduction",
            "fea_mesh_manifest\nmode_frequency_table",
            "Catalog claim until stress,\ndeformation, or basis hash exists",
            "#9333ea",
            "#faf5ff",
        ),
        (
            "Advanced Terrain",
            "DEM, GRANULAR,\nFSI/SPH, CRM",
            "terrain.granular_dem\nterrain.fea / crm",
            "deformable domain manifest\ncoupling/checkpoint log",
            "No terrain validation from\nheight/friction probes alone",
            "#ea580c",
            "#fff7ed",
        ),
        (
            "External Integration",
            "PARSERS, CASCADE,\nFMI, ROS, Synchrono",
            "model.import\nintegration.*",
            "asset/model manifests\ninterface map + sync contract",
            "Adapter evidence requires\nlive exchange or import log",
            "#7c3aed",
            "#f5f3ff",
        ),
        (
            "Postprocess / Solvers",
            "POSTPROCESS,\nMUMPS, PardisoMKL",
            "data.io_writer\nruntime.solver",
            "gnuplot/writer manifests\nconvergence metadata",
            "Backend name is not enough;\nrecord executable or solver log",
            "#64748b",
            "#f8fafc",
        ),
    ]

    row_h = 0.62
    row_gap = 0.08
    y = 4.58
    for group, gate, owner, artifact, policy, edge, face in rows:
        ax.add_patch(Rectangle((0.34, y - 0.05), 11.36, row_h + 0.08, facecolor=face, edgecolor="none", alpha=0.96, zorder=0))
        cells = [group, gate, owner, artifact, policy]
        for index, (x, width, _) in enumerate(columns):
            linestyle = "--" if index == 1 and group != "Core" else "-"
            _box(
                ax,
                (x, y),
                (width, row_h),
                cells[index],
                face="#ffffff",
                edge=edge if index in (0, 3) else "#cbd5e1",
                fontsize=6.65 if index != 4 else 6.3,
                weight="bold" if index == 0 else "normal",
                linestyle=linestyle,
            )
        for start_x, end_x in ((2.00, 2.16), (4.08, 4.24), (5.98, 6.14), (8.66, 8.82)):
            _arrow(ax, (start_x, y + row_h / 2), (end_x, y + row_h / 2), color=edge, width=0.85)
        y -= row_h + row_gap

    return save_figure(fig, output)


if __name__ == "__main__":
    print(render_chrono_optional_module_dependency_ladder())
