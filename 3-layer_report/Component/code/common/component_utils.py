from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Iterable, Sequence

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


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


def save_figure(fig, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def try_import_chrono():
    try:
        import pychrono as chrono

        return chrono, None
    except Exception as exc:  # pragma: no cover - environment dependent
        return None, f"{type(exc).__name__}: {exc}"


def vec_xyz(vec) -> tuple[float, float, float]:
    values = []
    for attr in ("x", "y", "z"):
        value = getattr(vec, attr)
        values.append(float(value() if callable(value) else value))
    return tuple(values)


def vec_length(vec) -> float:
    x, y, z = vec_xyz(vec)
    return math.sqrt(x * x + y * y + z * z)
