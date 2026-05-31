from __future__ import annotations

import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

sys.path.append(str(Path(__file__).resolve().parents[1] / "common"))

from component_utils import (  # noqa: E402
    IMAGES_RENDER,
    add_callout_3d,
    add_box,
    add_cylinder_x,
    add_cylinder_y,
    ensure_output_dirs,
    save_figure,
)


def _surface_sphere(ax, center, radius: float, color: str, *, alpha: float = 0.92, scale=(1.0, 1.0, 1.0)) -> None:
    cx, cy, cz = center
    u = np.linspace(0, 2 * math.pi, 42)
    v = np.linspace(0, math.pi, 24)
    x = cx + radius * scale[0] * np.outer(np.cos(u), np.sin(v))
    y = cy + radius * scale[1] * np.outer(np.sin(u), np.sin(v))
    z = cz + radius * scale[2] * np.outer(np.ones_like(u), np.cos(v))
    ax.plot_surface(x, y, z, color=color, alpha=alpha, linewidth=0, shade=True)


def _surface_capsule_x(ax, center, radius: float, length: float, color: str) -> None:
    cx, cy, cz = center
    cylinder_length = max(0.01, length - 2 * radius)
    add_cylinder_x(ax, center, radius, cylinder_length, color, alpha=0.92)
    _surface_sphere(ax, (cx - cylinder_length / 2, cy, cz), radius, color, alpha=0.92)
    _surface_sphere(ax, (cx + cylinder_length / 2, cy, cz), radius, color, alpha=0.92)


def _surface_mesh(ax, center, color: str) -> None:
    cx, cy, cz = center
    vertices = np.array(
        [
            [-0.46, -0.32, -0.18],
            [0.46, -0.28, -0.18],
            [0.38, 0.34, -0.18],
            [-0.44, 0.30, -0.18],
            [-0.22, -0.18, 0.28],
            [0.34, -0.04, 0.34],
            [0.02, 0.26, 0.18],
        ]
    )
    vertices += np.array([cx, cy, cz])
    faces = [
        [vertices[i] for i in [0, 1, 2, 3]],
        [vertices[i] for i in [0, 1, 5, 4]],
        [vertices[i] for i in [1, 2, 6, 5]],
        [vertices[i] for i in [2, 3, 6]],
        [vertices[i] for i in [3, 0, 4, 6]],
        [vertices[i] for i in [4, 5, 6]],
    ]
    ax.add_collection3d(Poly3DCollection(faces, facecolors=color, edgecolors="#334155", linewidths=0.8, alpha=0.86))


def render_default_shapes() -> Path:
    output = IMAGES_RENDER / "chrono_default_shape_types.png"
    fig = plt.figure(figsize=(10.0, 5.4))
    ax = fig.add_subplot(111, projection="3d")

    add_box(ax, (-2.4, 0.72, 0.42), (0.82, 0.62, 0.52), "#2563eb", alpha=0.90)
    _surface_sphere(ax, (-1.2, 0.72, 0.42), 0.34, "#16a34a")
    add_cylinder_y(ax, (0.0, 0.72, 0.42), 0.32, 0.68, "#111827", alpha=0.94)
    _surface_capsule_x(ax, (-2.4, -0.72, 0.42), 0.25, 0.98, "#f59e0b")
    _surface_sphere(ax, (-1.2, -0.72, 0.42), 0.34, "#8b5cf6", scale=(1.25, 0.72, 0.52))
    _surface_mesh(ax, (0.0, -0.72, 0.42), "#ef4444")
    ax.view_init(elev=24, azim=-48)
    ax.set_xlim(-3.05, 0.70)
    ax.set_ylim(-1.34, 1.34)
    ax.set_zlim(0.0, 1.15)
    ax.set_axis_off()
    try:
        ax.set_box_aspect((3.75, 2.68, 1.15))
    except Exception:
        pass
    add_callout_3d(ax, "Box", (0.42, 0.87), (-2.4, 0.72, 0.68), color="#1d4ed8", size=8)
    add_callout_3d(ax, "Sphere", (0.68, 0.75), (-1.2, 0.72, 0.72), color="#15803d", size=8)
    add_callout_3d(ax, "Cylinder", (0.90, 0.58), (0.0, 0.72, 0.55), color="#111827", size=8)
    add_callout_3d(ax, "Capsule", (0.06, 0.50), (-2.4, -0.72, 0.56), color="#b45309", size=8)
    add_callout_3d(ax, "Ellipsoid", (0.36, 0.24), (-1.2, -0.72, 0.54), color="#6d28d9", size=8)
    add_callout_3d(ax, "Mesh", (0.72, 0.22), (0.0, -0.72, 0.62), color="#991b1b", size=8)
    return save_figure(fig, output)


def main() -> None:
    ensure_output_dirs()
    print("chrono default shape render:", render_default_shapes())


if __name__ == "__main__":
    main()
