from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Iterable, Sequence

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import proj3d


ROOT = Path(__file__).resolve().parents[2]
IMAGES_RENDER = ROOT / "images" / "renders"
IMAGES_GRAPH = ROOT / "images" / "graphs"
OUTPUT_CSV = ROOT / "outputs" / "csv"
OUTPUT_RAW = ROOT / "outputs" / "raw"


def ensure_output_dirs() -> None:
    for path in (IMAGES_RENDER, IMAGES_GRAPH, OUTPUT_CSV, OUTPUT_RAW):
        path.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, fieldnames: Sequence[str], rows: Iterable[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


def set_axes_equal(ax) -> None:
    limits = np.array([ax.get_xlim3d(), ax.get_ylim3d(), ax.get_zlim3d()])
    centers = limits.mean(axis=1)
    radius = 0.5 * max(limits[:, 1] - limits[:, 0])
    ax.set_xlim3d([centers[0] - radius, centers[0] + radius])
    ax.set_ylim3d([centers[1] - radius, centers[1] + radius])
    ax.set_zlim3d([max(0, centers[2] - radius), centers[2] + radius])


def style_3d_axes(ax, title: str) -> None:
    ax.set_title(title, pad=10)
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_zlabel("z [m]")
    ax.view_init(elev=23, azim=-48)
    ax.grid(True, alpha=0.25)


def legend_if_any(ax, *args, **kwargs) -> None:
    handles, _ = ax.get_legend_handles_labels()
    if handles:
        ax.legend(*args, **kwargs)


def box_vertices(center, size):
    cx, cy, cz = center
    sx, sy, sz = (value / 2.0 for value in size)
    points = np.array(
        [
            [cx - sx, cy - sy, cz - sz],
            [cx + sx, cy - sy, cz - sz],
            [cx + sx, cy + sy, cz - sz],
            [cx - sx, cy + sy, cz - sz],
            [cx - sx, cy - sy, cz + sz],
            [cx + sx, cy - sy, cz + sz],
            [cx + sx, cy + sy, cz + sz],
            [cx - sx, cy + sy, cz + sz],
        ]
    )
    return points


def add_box(ax, center, size, color, alpha=0.88, edgecolor="#1f2933", label=None):
    p = box_vertices(center, size)
    faces = [
        [p[0], p[1], p[2], p[3]],
        [p[4], p[5], p[6], p[7]],
        [p[0], p[1], p[5], p[4]],
        [p[2], p[3], p[7], p[6]],
        [p[1], p[2], p[6], p[5]],
        [p[4], p[7], p[3], p[0]],
    ]
    poly = Poly3DCollection(faces, facecolors=color, edgecolors=edgecolor, linewidths=0.7, alpha=alpha)
    ax.add_collection3d(poly)
    if label:
        ax.text(center[0], center[1], center[2] + size[2] / 2 + 0.08, label, ha="center", fontsize=8)
    return poly


def add_cylinder_x(ax, center, radius, length, color, alpha=0.95, label=None):
    cx, cy, cz = center
    theta = np.linspace(0, 2 * math.pi, 36)
    x = np.linspace(cx - length / 2, cx + length / 2, 2)
    theta_grid, x_grid = np.meshgrid(theta, x)
    y_grid = cy + radius * np.cos(theta_grid)
    z_grid = cz + radius * np.sin(theta_grid)
    ax.plot_surface(x_grid, y_grid, z_grid, color=color, alpha=alpha, linewidth=0, shade=True)
    for xcap in (cx - length / 2, cx + length / 2):
        ax.plot([xcap] * len(theta), cy + radius * np.cos(theta), cz + radius * np.sin(theta), color="#111827", linewidth=0.7)
    if label:
        ax.text(cx, cy, cz + radius + 0.08, label, ha="center", fontsize=8)


def add_cylinder_y(ax, center, radius, length, color, alpha=0.95, label=None):
    cx, cy, cz = center
    theta = np.linspace(0, 2 * math.pi, 36)
    y = np.linspace(cy - length / 2, cy + length / 2, 2)
    theta_grid, y_grid = np.meshgrid(theta, y)
    x_grid = cx + radius * np.cos(theta_grid)
    z_grid = cz + radius * np.sin(theta_grid)
    ax.plot_surface(x_grid, y_grid, z_grid, color=color, alpha=alpha, linewidth=0, shade=True)
    for ycap in (cy - length / 2, cy + length / 2):
        ax.plot(cx + radius * np.cos(theta), [ycap] * len(theta), cz + radius * np.sin(theta), color="#111827", linewidth=0.7)
    if label:
        ax.text(cx, cy, cz + radius + 0.08, label, ha="center", fontsize=8)


def add_terrain_surface(ax, x, y, z, cmap="terrain", alpha=0.9):
    ax.plot_surface(x, y, z, cmap=cmap, alpha=alpha, linewidth=0, antialiased=True)


def add_label_3d(ax, text: str, point, *, color: str = "#111827", size: int = 8, ha: str = "center") -> None:
    ax.text(
        point[0],
        point[1],
        point[2],
        text,
        ha=ha,
        va="center",
        fontsize=size,
        color=color,
        bbox={"boxstyle": "round,pad=0.18", "facecolor": "white", "edgecolor": color, "alpha": 0.82, "linewidth": 0.7},
    )


def add_label_2d(ax, text: str, xy, *, color: str = "#111827", size: int = 8, ha: str = "left") -> None:
    bbox = ax.get_position()
    fig_x = bbox.x0 + xy[0] * bbox.width
    fig_y = bbox.y0 + xy[1] * bbox.height
    ax.figure.text(
        fig_x,
        fig_y,
        text,
        ha=ha,
        va="center",
        fontsize=size,
        color=color,
        zorder=20,
        bbox={"boxstyle": "round,pad=0.18", "facecolor": "white", "edgecolor": color, "alpha": 0.86, "linewidth": 0.7},
    )


def _figure_xy_from_axes_fraction(ax, xy) -> tuple[float, float]:
    bbox = ax.get_position()
    return bbox.x0 + xy[0] * bbox.width, bbox.y0 + xy[1] * bbox.height


def _figure_xy_from_3d_point(ax, xyz) -> tuple[float, float]:
    x2, y2, _ = proj3d.proj_transform(xyz[0], xyz[1], xyz[2], ax.get_proj())
    display_xy = ax.transData.transform((x2, y2))
    fig_xy = ax.figure.transFigure.inverted().transform(display_xy)
    return float(fig_xy[0]), float(fig_xy[1])


def _figure_xy_from_2d_data(ax, xy) -> tuple[float, float]:
    display_xy = ax.transData.transform((xy[0], xy[1]))
    fig_xy = ax.figure.transFigure.inverted().transform(display_xy)
    return float(fig_xy[0]), float(fig_xy[1])


def _queue_callout(ax, text: str, xy, target, *, target_mode: str, color: str, size: int, ha: str) -> None:
    callouts = getattr(ax.figure, "_component_callouts", None)
    if callouts is None:
        callouts = []
        setattr(ax.figure, "_component_callouts", callouts)
    callouts.append(
        {
            "ax": ax,
            "text": text,
            "xy": xy,
            "target": target,
            "target_mode": target_mode,
            "color": color,
            "size": size,
            "ha": ha,
        }
    )


def add_callout_2d(ax, text: str, xy, target_xy, *, color: str = "#111827", size: int = 8, ha: str = "left") -> None:
    _queue_callout(ax, text, xy, target_xy, target_mode="axes_fraction", color=color, size=size, ha=ha)


def add_callout_3d(ax, text: str, xy, target_xyz, *, color: str = "#111827", size: int = 8, ha: str = "left") -> None:
    _queue_callout(ax, text, xy, target_xyz, target_mode="data_3d", color=color, size=size, ha=ha)


def add_callout_data_2d(ax, text: str, xy, target_xy, *, color: str = "#111827", size: int = 8, ha: str = "left") -> None:
    _queue_callout(ax, text, xy, target_xy, target_mode="data_2d", color=color, size=size, ha=ha)


def _draw_component_callouts(fig) -> None:
    for item in getattr(fig, "_component_callouts", []):
        ax = item["ax"]
        start_x, start_y = _figure_xy_from_axes_fraction(ax, item["xy"])
        if item["target_mode"] == "data_3d":
            end_x, end_y = _figure_xy_from_3d_point(ax, item["target"])
        elif item["target_mode"] == "data_2d":
            end_x, end_y = _figure_xy_from_2d_data(ax, item["target"])
        else:
            end_x, end_y = _figure_xy_from_axes_fraction(ax, item["target"])
        color = item["color"]
        line = FancyArrowPatch(
            (start_x, start_y),
            (end_x, end_y),
            transform=fig.transFigure,
            arrowstyle="-",
            mutation_scale=1,
            linewidth=0.8,
            color=color,
            alpha=0.88,
            zorder=24,
        )
        fig.add_artist(line)
        fig.text(
            start_x,
            start_y,
            item["text"],
            ha=item["ha"],
            va="center",
            fontsize=item["size"],
            color=color,
            zorder=30,
            bbox={"boxstyle": "round,pad=0.18", "facecolor": "white", "edgecolor": color, "alpha": 0.90, "linewidth": 0.7},
        )


def save_figure(fig, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.canvas.draw()
    _draw_component_callouts(fig)
    fig.savefig(path, dpi=180, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    return path


def try_import_chrono():
    try:
        import pychrono as chrono

        return chrono, None
    except Exception as exc:  # pragma: no cover - environment dependent
        return None, "pychrono_unavailable"


def vec_xyz(vec) -> tuple[float, float, float]:
    values = []
    for attr in ("x", "y", "z"):
        value = getattr(vec, attr)
        values.append(float(value() if callable(value) else value))
    return tuple(values)


def vec_length(vec) -> float:
    x, y, z = vec_xyz(vec)
    return math.sqrt(x * x + y * y + z * z)
