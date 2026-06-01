from __future__ import annotations

import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

sys.path.append(str(Path(__file__).resolve().parents[1] / "common"))

from component_utils import (  # noqa: E402
    IMAGES_GRAPH,
    IMAGES_RENDER,
    OUTPUT_CSV,
    OUTPUT_JSON,
    add_callout_3d,
    add_box,
    add_cylinder_x,
    add_terrain_surface,
    ensure_output_dirs,
    save_figure,
    set_axes_equal,
    style_3d_axes,
    try_import_chrono,
    vec_length,
    write_csv,
    write_json,
)
from vsg_component_render import add_box as vsg_add_box, add_cylinder_y as vsg_add_cylinder_y, render_vsg_scene  # noqa: E402


SURFACE_PROBE_FIELDNAMES = [
    "run_id",
    "schema_id",
    "scenario_id",
    "sample_index",
    "terrain_component_id",
    "terrain_type",
    "x_m",
    "y_m",
    "height_m",
    "normal_x",
    "normal_y",
    "normal_z",
    "terrain_mu_query",
    "contact_material_mu",
    "sinkage_m",
    "estimated_friction",
    "scm_sinkage_demo_m",
    "source",
]


def height_field(x, y):
    return 0.10 * np.sin(1.8 * x) * np.cos(1.4 * y) + 0.04 * np.exp(-((x - 0.8) ** 2 + (y + 0.4) ** 2) / 0.25)


def scm_sinkage_depth(x, y):
    return 0.18 * np.exp(-((x - 0.2) ** 2 / 1.5 + y**2 / 0.35))


def scm_surface_height(x, y):
    return height_field(x, y) - scm_sinkage_depth(x, y)


def _format_terrain_ax(ax, *, xlim=(-2.0, 2.0), ylim=(-1.4, 1.4), zlim=(0.0, 1.2), elev=24, azim=-48) -> None:
    ax.view_init(elev=elev, azim=azim)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_zlim(*zlim)
    ax.set_axis_off()
    try:
        ax.set_box_aspect((xlim[1] - xlim[0], ylim[1] - ylim[0], zlim[1] - zlim[0]))
    except Exception:
        pass


def _line3d(ax, start, end, *, color: str, linewidth: float = 2.4, linestyle: str = "-", alpha: float = 1.0) -> None:
    ax.plot(
        [start[0], end[0]],
        [start[1], end[1]],
        [start[2], end[2]],
        color=color,
        linewidth=linewidth,
        linestyle=linestyle,
        alpha=alpha,
    )


def _add_reference_plane(
    ax,
    *,
    center: tuple[float, float, float],
    size: tuple[float, float],
    facecolor: str,
    edgecolor: str,
    fill_alpha: float = 0.12,
    grid_color: str = "#cbd5e1",
    grid_alpha: float = 0.70,
    grid: tuple[int, int] = (6, 5),
) -> None:
    cx, cy, z = center
    sx, sy = size
    xmin, xmax = cx - sx / 2.0, cx + sx / 2.0
    ymin, ymax = cy - sy / 2.0, cy + sy / 2.0
    verts = [[(xmin, ymin, z), (xmax, ymin, z), (xmax, ymax, z), (xmin, ymax, z)]]
    ax.add_collection3d(
        Poly3DCollection(verts, facecolors=facecolor, edgecolors=edgecolor, linewidths=0.8, alpha=fill_alpha)
    )

    line_z = z + 0.006
    corners = [(xmin, ymin, line_z), (xmax, ymin, line_z), (xmax, ymax, line_z), (xmin, ymax, line_z)]
    for start, end in zip(corners, corners[1:] + corners[:1]):
        _line3d(ax, start, end, color=edgecolor, linewidth=1.0, alpha=0.88)
    for x in np.linspace(xmin, xmax, grid[0]):
        _line3d(ax, (float(x), ymin, line_z), (float(x), ymax, line_z), color=grid_color, linewidth=0.8, alpha=grid_alpha)
    for y in np.linspace(ymin, ymax, grid[1]):
        _line3d(ax, (xmin, float(y), line_z), (xmax, float(y), line_z), color=grid_color, linewidth=0.8, alpha=grid_alpha)


def render_terrain_ground_obstacle_components() -> Path:
    def ground_scene(system, chrono):
        vsg_add_box(system, chrono, "rigid_ground_patch", (0, 0, -0.04), (4.8, 3.0, 0.08), (0.58, 0.62, 0.55))
        vsg_add_box(system, chrono, "box_obstacle", (-1.15, 0.62, 0.21), (0.46, 0.46, 0.42), (0.70, 0.12, 0.10))
        vsg_add_cylinder_y(system, chrono, "log_obstacle", (1.15, -0.62, 0.20), 0.20, 0.85, (0.48, 0.28, 0.10))
        vsg_add_box(system, chrono, "rigidterrain_patch_marker", (0.55, 0.55, 0.025), (0.95, 0.60, 0.03), (0.20, 0.42, 0.68), collide=False)

    path = IMAGES_RENDER / "terrain_ground_obstacle_components.png"
    # Use the annotated matplotlib path for report figures so callout anchors stay deterministic.
    vsg_ok = False
    if not vsg_ok:
        fig = plt.figure(figsize=(9.0, 5.4))
        ax = fig.add_subplot(111, projection="3d")
        _add_reference_plane(
            ax,
            center=(0, 0, 0.0),
            size=(2.75, 1.65),
            facecolor="#94a3b8",
            edgecolor="#475569",
            fill_alpha=0.12,
            grid_color="#cbd5e1",
        )
        add_box(ax, (-0.82, 0.38, 0.18), (0.34, 0.34, 0.36), "#dc2626", alpha=0.90, edgecolor="#7f1d1d")
        add_cylinder_x(ax, (0.70, -0.30, 0.18), 0.18, 0.62, "#92400e", alpha=0.94)
        _add_reference_plane(
            ax,
            center=(0.45, 0.42, 0.028),
            size=(0.58, 0.36),
            facecolor="#2563eb",
            edgecolor="#1e40af",
            fill_alpha=0.22,
            grid_color="#93c5fd",
            grid=(3, 3),
        )
        add_callout_3d(ax, "Ground: gray plane", (0.10, 0.72), (-1.05, -0.48, 0.01), color="#475569", size=9)
        add_callout_3d(ax, "Box obstacle", (0.42, 0.76), (-0.82, 0.38, 0.36), color="#991b1b", size=9)
        add_callout_3d(ax, "Log obstacle", (0.66, 0.30), (0.70, -0.30, 0.18), color="#92400e", size=9)
        add_callout_3d(ax, "Patch marker", (0.66, 0.68), (0.45, 0.42, 0.05), color="#1e40af", size=9)
        _format_terrain_ax(ax, xlim=(-1.45, 1.45), ylim=(-0.88, 0.88), zlim=(0.0, 0.70), elev=25, azim=-49)
        save_figure(fig, path)
    return path


def render_terrain_rigid_patch_component() -> Path:
    fig = plt.figure(figsize=(9.0, 5.4))
    ax = fig.add_subplot(111, projection="3d")
    _add_reference_plane(
        ax,
        center=(0.0, 0.0, 0.0),
        size=(2.70, 1.55),
        facecolor="#60a5fa",
        edgecolor="#1d4ed8",
        fill_alpha=0.12,
        grid_color="#2563eb",
        grid_alpha=0.82,
    )
    add_box(ax, (-0.72, -0.32, 0.14), (0.28, 0.20, 0.18), "#2563eb", alpha=0.88)
    add_cylinder_x(ax, (-0.72, -0.32, 0.055), 0.08, 0.30, "#111827", alpha=0.92)
    add_box(ax, (0.72, 0.28, 0.10), (0.38, 0.28, 0.16), "#dc2626", alpha=0.82, edgecolor="#7f1d1d")
    _line3d(ax, (-1.05, -0.32, 0.065), (1.05, -0.32, 0.065), color="#f97316", linewidth=2.8)
    add_callout_3d(ax, "RigidTerrain patch", (0.18, 0.78), (0.0, 0.0, 0.06), color="#1d4ed8", size=9)
    add_callout_3d(ax, "Wheel path", (0.18, 0.70), (-0.15, -0.32, 0.07), color="#c2410c", size=9)
    add_callout_3d(ax, "Obstacle", (0.70, 0.70), (0.72, 0.28, 0.18), color="#991b1b", size=9)
    _format_terrain_ax(ax, xlim=(-1.45, 1.45), ylim=(-0.88, 0.88), zlim=(0.0, 0.62), elev=25, azim=-49)
    return save_figure(fig, IMAGES_RENDER / "terrain_rigid_patch_component.png")


def render_terrain_contact_material_regions() -> Path:
    fig = plt.figure(figsize=(9.0, 5.4))
    ax = fig.add_subplot(111, projection="3d")
    _add_reference_plane(
        ax,
        center=(-0.70, 0, 0.0),
        size=(1.45, 1.35),
        facecolor="#64748b",
        edgecolor="#334155",
        fill_alpha=0.22,
        grid_color="#cbd5e1",
    )
    _add_reference_plane(
        ax,
        center=(0.80, 0, 0.0),
        size=(1.45, 1.35),
        facecolor="#f59e0b",
        edgecolor="#92400e",
        fill_alpha=0.22,
        grid_color="#fed7aa",
    )
    for x in np.linspace(-1.15, 1.25, 7):
        add_cylinder_x(ax, (float(x), -0.18, 0.17), 0.10, 0.12, "#111827", alpha=0.92)
        add_cylinder_x(ax, (float(x), 0.18, 0.17), 0.10, 0.12, "#111827", alpha=0.92)
    _line3d(ax, (-1.35, -0.18, 0.05), (1.42, -0.18, 0.05), color="#dc2626", linewidth=2.8)
    _line3d(ax, (-1.35, 0.18, 0.05), (1.42, 0.18, 0.05), color="#dc2626", linewidth=2.8)
    add_callout_3d(ax, "High friction", (0.58, 0.76), (-0.88, 0.28, 0.05), color="#334155", size=9)
    add_callout_3d(ax, "Low friction", (0.76, 0.56), (1.25, -0.48, 0.05), color="#92400e", size=9)
    add_callout_3d(ax, "Wheel tracks", (0.18, 0.64), (-0.95, -0.18, 0.06), color="#991b1b", size=9)
    _format_terrain_ax(ax, xlim=(-1.55, 1.60), ylim=(-0.86, 0.86), zlim=(0.0, 0.62), elev=25, azim=-49)
    return save_figure(fig, IMAGES_RENDER / "terrain_contact_material_regions.png")


def render_terrain_heightmap_component() -> Path:
    def heightmap_scene(system, chrono):
        for xi in np.linspace(-2.4, 2.4, 13):
            for yi in np.linspace(-1.6, 1.6, 9):
                h = float(height_field(xi, yi))
                color = (0.22 + max(h, -0.1) * 1.2, 0.42 + h, 0.22)
                vsg_add_box(system, chrono, "height_cell", (float(xi), float(yi), h / 2 - 0.04), (0.34, 0.34, max(0.035, h + 0.11)), color)
        vsg_add_box(system, chrono, "heightmap_base", (0, 0, -0.10), (5.2, 3.5, 0.04), (0.42, 0.42, 0.38), collide=False)

    path = IMAGES_RENDER / "terrain_heightmap_component.png"
    # Use the annotated matplotlib path for report figures so callout anchors stay deterministic.
    vsg_ok = False
    if not vsg_ok:
        fig = plt.figure(figsize=(9.0, 5.4))
        ax = fig.add_subplot(111, projection="3d")
        x_grid = np.linspace(-2.4, 2.4, 40)
        y_grid = np.linspace(-1.6, 1.6, 28)
        xx, yy = np.meshgrid(x_grid, y_grid)
        zz = height_field(xx, yy)
        ax.plot_surface(xx, yy, zz, cmap="terrain", alpha=0.96, linewidth=0, antialiased=True)
        for x in np.linspace(-2.4, 2.4, 7):
            _line3d(ax, (float(x), -1.6, 0.13), (float(x), 1.6, 0.13), color="#ffffff", linewidth=0.7)
        for y in np.linspace(-1.6, 1.6, 5):
            _line3d(ax, (-2.4, float(y), 0.13), (2.4, float(y), 0.13), color="#ffffff", linewidth=0.7)
        add_callout_3d(ax, "Heightmap surface", (0.62, 0.74), (0.0, 0.0, float(height_field(0.0, 0.0))), color="#365314", size=9)
        add_callout_3d(ax, "Height samples", (0.66, 0.36), (1.1, -0.4, float(height_field(1.1, -0.4))), color="#475569", size=9)
        _format_terrain_ax(ax, xlim=(-2.55, 2.55), ylim=(-1.75, 1.75), zlim=(-0.18, 0.28), elev=25, azim=-49)
        save_figure(fig, path)
    return path


def render_terrain_scm_deformation_component() -> Path:
    def scm_scene(system, chrono):
        for xi in np.linspace(-2.2, 2.2, 12):
            for yi in np.linspace(-1.4, 1.4, 8):
                h = float(scm_surface_height(xi, yi))
                color = (0.40, 0.36 + max(0.0, h), 0.20)
                vsg_add_box(system, chrono, "scm_cell", (float(xi), float(yi), h / 2 - 0.05), (0.34, 0.34, max(0.035, h + 0.12)), color)

    path = IMAGES_RENDER / "terrain_scm_deformation_component.png"
    # Use the annotated matplotlib path for report figures so callout anchors stay deterministic.
    vsg_ok = False
    if not vsg_ok:
        fig = plt.figure(figsize=(9.0, 5.4))
        ax = fig.add_subplot(111, projection="3d")
        x = np.linspace(-2.2, 2.2, 70)
        y = np.linspace(-1.4, 1.4, 46)
        xx, yy = np.meshgrid(x, y)
        zz = scm_surface_height(xx, yy)
        sinkage = scm_sinkage_depth(xx, yy)
        facecolors = plt.cm.gist_earth(np.clip((zz + 0.23) / 0.43, 0.0, 1.0))
        rut = sinkage / max(float(np.max(sinkage)), 1e-6)
        facecolors[..., 0] = facecolors[..., 0] * (1 - 0.38 * rut) + 0.18 * rut
        facecolors[..., 1] = facecolors[..., 1] * (1 - 0.34 * rut) + 0.15 * rut
        facecolors[..., 2] = facecolors[..., 2] * (1 - 0.28 * rut) + 0.13 * rut
        ax.plot_surface(xx, yy, zz, facecolors=facecolors, linewidth=0, antialiased=True, shade=False, alpha=0.98)
        for xi in np.linspace(-2.1, 2.1, 9):
            zs = scm_surface_height(np.full_like(y, xi), y)
            _line3d(ax, (float(xi), -1.35, float(zs[0]) + 0.004), (float(xi), 1.35, float(zs[-1]) + 0.004), color="#3f3f46", linewidth=0.45, alpha=0.35)
        for yi in np.linspace(-1.2, 1.2, 7):
            zs = scm_surface_height(x, np.full_like(x, yi))
            ax.plot(x, np.full_like(x, yi), zs + 0.004, color="#3f3f46", linewidth=0.45, alpha=0.35)
        rut_x = np.linspace(-1.45, 1.65, 120)
        rut_y = np.zeros_like(rut_x)
        rut_z = scm_surface_height(rut_x, rut_y) + 0.010
        ax.plot(rut_x, rut_y, rut_z, color="#78350f", linewidth=3.0, alpha=0.70)
        rut_bottom = (0.2, 0.0, float(scm_surface_height(0.2, 0.0)))
        add_callout_3d(ax, "SCM grid cells", (0.12, 0.76), (-1.2, 0.8, float(scm_surface_height(-1.2, 0.8)) + 0.01), color="#3f3f46", size=9)
        add_callout_3d(ax, "Sinkage track", (0.56, 0.70), rut_bottom, color="#78350f", size=9)
        _format_terrain_ax(ax, xlim=(-2.45, 2.45), ylim=(-1.60, 1.60), zlim=(-0.22, 0.28), elev=25, azim=-49)
        save_figure(fig, path)
    return path


def render_terrain_environment_field_component() -> Path:
    fig = plt.figure(figsize=(9.0, 5.4))
    ax = fig.add_subplot(111, projection="3d")
    xs = np.array([-1.25, 1.25, 1.25, -1.25])
    ys = np.array([-0.75, -0.75, 0.75, 0.75])
    slope = 0.18 * xs
    verts = [[(xs[i], ys[i], slope[i] + 0.08) for i in range(4)]]
    ax.add_collection3d(Poly3DCollection(verts, facecolors="#94a3b8", edgecolors="#334155", linewidths=1.0, alpha=0.24))
    slope_outline = [(xs[i], ys[i], slope[i] + 0.095) for i in range(4)]
    for start, end in zip(slope_outline, slope_outline[1:] + slope_outline[:1]):
        _line3d(ax, start, end, color="#334155", linewidth=1.0, alpha=0.88)
    add_box(ax, (-0.30, 0.0, 0.36), (0.55, 0.42, 0.22), "#2563eb", alpha=0.86)
    ax.quiver(-0.30, 0.0, 0.72, 0.0, 0.0, -0.42, color="#dc2626", linewidth=3.2)
    ax.quiver(-1.10, -0.55, 0.38, 1.10, 0.0, 0.0, color="#f97316", linewidth=3.0)
    ax.quiver(0.30, 0.0, 0.55, 0.45, 0.0, 0.08, color="#16a34a", linewidth=2.6)
    add_callout_3d(ax, "Slope frame", (0.24, 0.72), (-0.30, 0.0, 0.36), color="#475569", size=9)
    add_callout_3d(ax, "Gravity", (0.28, 0.84), (-0.30, 0.0, 0.72), color="#991b1b", size=9)
    add_callout_3d(ax, "Wind/force", (0.10, 0.52), (0.02, -0.55, 0.38), color="#7c2d12", size=9)
    add_callout_3d(ax, "Travel direction", (0.64, 0.60), (0.72, 0.0, 0.63), color="#15803d", size=9)
    _format_terrain_ax(ax, xlim=(-1.45, 1.45), ylim=(-0.95, 0.95), zlim=(0.0, 1.0), elev=24, azim=-50)
    return save_figure(fig, IMAGES_RENDER / "terrain_environment_field_component.png")


def render_terrain_components() -> list[Path]:
    return [
        render_terrain_ground_obstacle_components(),
        render_terrain_rigid_patch_component(),
        render_terrain_contact_material_regions(),
        render_terrain_heightmap_component(),
        render_terrain_scm_deformation_component(),
        render_terrain_environment_field_component(),
    ]


def _terrain_height_friction_sinkage_rows() -> list[dict[str, str]]:
    chrono, error = try_import_chrono()
    material_source = "pychrono" if chrono is not None else f"fallback_{error}"
    rows = []
    run_id = "environment_terrain_component_demo"
    scenario_id = "surface_probe_schema_v1"
    sample_index = 0
    for xi in np.linspace(-3.0, 3.0, 61):
        for yi in np.linspace(-2.0, 2.0, 41):
            h = float(height_field(xi, yi))
            friction = 0.62 - 0.10 * min(1.0, abs(h) / 0.14)
            sinkage = max(0.0, 0.16 * math.exp(-((xi - 0.2) ** 2 / 1.5 + yi**2 / 0.35)))
            dx = 0.10 * 1.8 * math.cos(1.8 * xi) * math.cos(1.4 * yi)
            dy = -0.10 * 1.4 * math.sin(1.8 * xi) * math.sin(1.4 * yi)
            normal = np.array([-dx, -dy, 1.0], dtype=float)
            normal = normal / np.linalg.norm(normal)
            rows.append(
                {
                    "run_id": run_id,
                    "schema_id": "terrain.surface_probe.v1",
                    "scenario_id": scenario_id,
                    "sample_index": sample_index,
                    "terrain_component_id": "terrain.heightmap_mesh",
                    "terrain_type": "analytic_heightmap_with_scm_sinkage",
                    "x_m": f"{xi:.3f}",
                    "y_m": f"{yi:.3f}",
                    "height_m": f"{h:.5f}",
                    "normal_x": f"{normal[0]:.5f}",
                    "normal_y": f"{normal[1]:.5f}",
                    "normal_z": f"{normal[2]:.5f}",
                    "terrain_mu_query": f"{friction:.4f}",
                    "contact_material_mu": f"{friction:.4f}",
                    "sinkage_m": f"{sinkage:.5f}",
                    "estimated_friction": f"{friction:.4f}",
                    "scm_sinkage_demo_m": f"{sinkage:.5f}",
                    "source": material_source,
                }
            )
            sample_index += 1
    return rows


def write_terrain_height_friction_sinkage_csv() -> Path:
    return write_csv(OUTPUT_CSV / "environment_terrain_height_friction_sinkage.csv", SURFACE_PROBE_FIELDNAMES, _terrain_height_friction_sinkage_rows())


def write_terrain_surface_probe_csv() -> Path:
    return write_csv(OUTPUT_CSV / "terrain_surface_probe.csv", SURFACE_PROBE_FIELDNAMES, _terrain_height_friction_sinkage_rows())


def write_terrain_query_probe_csv() -> Path:
    rows = []
    for row in _terrain_height_friction_sinkage_rows():
        rows.append(
            {
                "run_id": row["run_id"],
                "schema_id": "terrain.query_probe.v1",
                "scenario_id": row["scenario_id"],
                "sample_index": row["sample_index"],
                "terrain_component_id": row["terrain_component_id"],
                "query_frame": "world_X_forward_Y_left_Z_up",
                "consumer_family": "semi_empirical_tire;controller;height_query",
                "valid_for_semi_empirical_tires": "true",
                "uses_contact_solver": "false",
                "height_functor_id": "analytic_height_field.v1",
                "normal_functor_id": "finite_difference_height_normal.v1",
                "friction_functor_id": "analytic_region_friction.v1",
                "placeholder_policy": "fallback analytic query; live Vehicle terrain must replace source",
                "x_m": row["x_m"],
                "y_m": row["y_m"],
                "height_m": row["height_m"],
                "normal_x": row["normal_x"],
                "normal_y": row["normal_y"],
                "normal_z": row["normal_z"],
                "terrain_mu_query": row["terrain_mu_query"],
                "contact_material_mu": row["contact_material_mu"],
                "source": row["source"],
            }
        )
    return write_csv(OUTPUT_CSV / "terrain_query_probe.csv", list(rows[0].keys()), rows)


def write_terrain_component_manifest_json() -> Path:
    chrono, error = try_import_chrono()
    source = "pychrono" if chrono is not None else f"fallback_{error}"
    payload = {
        "schema_id": "terrain.component_manifest.v1",
        "run_id": "environment_terrain_component_demo",
        "source": source,
        "fallback_policy": "Analytic height/friction/sinkage fields validate schema and graph wiring; live terrain modules must replace source with pychrono/module-backed evidence.",
        "terrain_components": [
            {
                "catalog_component_id": "terrain.heightmap_mesh",
                "instance_id": "terrain.heightmap_mesh.analytic_surface",
                "terrain_component_id": "terrain.heightmap_mesh",
                "terrain_type": "analytic_heightmap_with_scm_sinkage",
                "chrono_class": "schema_fallback_height_field",
                "module_availability": "fallback_analytic",
                "module_dependency": "none_for_fallback; Vehicle terrain module for live RigidTerrain/SCMTerrain/CRGTerrain",
                "query_authority": True,
                "contact_authority": False,
                "sync_order": "scenario loop samples analytic terrain before graph generation",
                "advance_order": "static query surface; no terrain Advance() in fallback",
                "probe_csv": "outputs/csv/terrain_surface_probe.csv",
            },
            {
                "catalog_component_id": "terrain.core_ground",
                "instance_id": "terrain.core_ground.contact_probe",
                "terrain_component_id": "terrain.core_ground",
                "terrain_type": "rigid_ground_contact_probe",
                "chrono_class": "ChBodyEasyBox ground when PyChrono is available; analytic fallback otherwise",
                "module_availability": "fallback_or_core_pychrono",
                "module_dependency": "Chrono Core",
                "query_authority": False,
                "contact_authority": True,
                "sync_order": "contact probe integrates before row write",
                "advance_order": "ChSystem.DoStepDynamics(dt) or deterministic fallback time row",
                "probe_csv": "outputs/csv/environment_terrain_contact_probe.csv",
            },
            {
                "catalog_component_id": "terrain.crg",
                "instance_id": "terrain.crg_road_profile.catalog_slot",
                "terrain_component_id": "terrain.crg_road_profile",
                "terrain_type": "CRGTerrain",
                "chrono_class": "chrono.vehicle.CRGTerrain",
                "module_availability": "not_executed",
                "module_dependency": "Vehicle + OpenCRG/profile file",
                "query_authority": True,
                "contact_authority": "tire_model_dependent",
                "sync_order": "CRG profile query consumed by vehicle/tire synchronization in live runs",
                "advance_order": "static road profile; live run must record vehicle dt and CRG source hash",
                "probe_csv": "",
            },
            {
                "catalog_component_id": "terrain.scm",
                "instance_id": "terrain.scm.catalog_domain",
                "terrain_component_id": "terrain.scm",
                "terrain_type": "SCMTerrain",
                "chrono_class": "chrono.vehicle.SCMTerrain",
                "module_availability": "not_executed",
                "module_dependency": "Vehicle",
                "query_authority": "deformable soil grid",
                "contact_authority": "SCM soil-wheel/track coupling",
                "sync_order": "vehicle/contact load update before SCM evidence export",
                "advance_order": "SCMTerrain.Advance or equivalent soil update in live runs",
                "probe_csv": "outputs/csv/scm_soil_profile_manifest.csv",
            },
            {
                "catalog_component_id": "terrain.granular_dem",
                "instance_id": "terrain.granular_dem.catalog_domain",
                "terrain_component_id": "terrain.granular_dem",
                "terrain_type": "GranularTerrain",
                "chrono_class": "chrono.vehicle.GranularTerrain / Chrono granular backend",
                "module_availability": "not_executed",
                "module_dependency": "Vehicle + Granular/Multicore/GPU backend",
                "query_authority": False,
                "contact_authority": "DEM particle contact",
                "sync_order": "settle/checkpoint before MBD coupling",
                "advance_order": "particle domain advance exchanges forces with MBD bodies",
                "probe_csv": "",
            },
            {
                "catalog_component_id": "terrain.fea",
                "instance_id": "terrain.fea.catalog_domain",
                "terrain_component_id": "terrain.fea",
                "terrain_type": "FEATerrain",
                "chrono_class": "chrono.vehicle.FEATerrain",
                "module_availability": "not_executed",
                "module_dependency": "Vehicle + FEA",
                "query_authority": "mesh surface query when exported",
                "contact_authority": "FEA contact/coupling",
                "sync_order": "MBD contact/coupling before FEA solve export",
                "advance_order": "FEA solver advances mesh state in live runs",
                "probe_csv": "",
            },
            {
                "catalog_component_id": "terrain.crm",
                "instance_id": "terrain.crm.catalog_domain",
                "terrain_component_id": "terrain.crm",
                "terrain_type": "CRMTerrain",
                "chrono_class": "chrono.vehicle.CRMTerrain / Chrono::FSI SPH",
                "module_availability": "not_executed",
                "module_dependency": "Vehicle + FSI/SPH",
                "query_authority": False,
                "contact_authority": "FSI/SPH coupling",
                "sync_order": "MBD synchronize before FSI/SPH force exchange",
                "advance_order": "MBD dt and FSI dt coupling order must be logged in live runs",
                "probe_csv": "",
            },
        ],
    }
    return write_json(OUTPUT_JSON / "terrain_component_manifest.json", payload)


def _terrain_catalog_source() -> str:
    chrono, error = try_import_chrono()
    if chrono is None:
        return f"fallback_terrain_schema_only_{error}"
    return "fallback_terrain_schema_only_module_runs_not_executed"


def write_terrain_patch_manifest() -> tuple[Path, Path]:
    source = _terrain_catalog_source()
    rows = [
        {
            "schema_id": "terrain.patch_manifest.v1",
            "run_id": "environment_terrain_component_demo",
            "catalog_component_id": "terrain.rigid_patch",
            "instance_id": "terrain.patch.rigid_demo",
            "terrain_component_id": "terrain.core_ground",
            "patch_type": "BOX",
            "chrono_class": "veh.RigidTerrain::AddPatch or ChBodyEasyBox fallback",
            "origin_frame": "world_X_forward_Y_left_Z_up",
            "pose_xyz_m": "0.000,0.000,0.000",
            "pose_quat_wxyz": "1.000,0.000,0.000,0.000",
            "bounds_min_xyz_m": "-3.000,-1.200,-0.050",
            "bounds_max_xyz_m": "3.000,1.200,0.050",
            "texture_asset": "textures/concrete.jpg",
            "material_id": "terrain.material.rigid_mu_0p62",
            "source_path": "",
            "source_hash": "",
            "height_scale_m": "",
            "crg_s_bounds_m": "",
            "crg_l_bounds_m": "",
            "query_authority": "false",
            "contact_authority": "true",
            "source": source,
        },
        {
            "schema_id": "terrain.patch_manifest.v1",
            "run_id": "environment_terrain_component_demo",
            "catalog_component_id": "terrain.heightmap_mesh",
            "instance_id": "terrain.patch.analytic_heightmap_demo",
            "terrain_component_id": "terrain.heightmap_mesh",
            "patch_type": "HEIGHT_MAP",
            "chrono_class": "analytic_height_field fallback; veh.RigidTerrain height map for live runs",
            "origin_frame": "world_X_forward_Y_left_Z_up",
            "pose_xyz_m": "0.000,0.000,0.000",
            "pose_quat_wxyz": "1.000,0.000,0.000,0.000",
            "bounds_min_xyz_m": "-3.000,-2.000,-0.200",
            "bounds_max_xyz_m": "3.000,2.000,0.200",
            "texture_asset": "procedural terrain colormap",
            "material_id": "terrain.material.region_map",
            "source_path": "analytic_height_field.v1",
            "source_hash": "",
            "height_scale_m": "1.000",
            "crg_s_bounds_m": "",
            "crg_l_bounds_m": "",
            "query_authority": "true",
            "contact_authority": "false",
            "source": source,
        },
        {
            "schema_id": "terrain.patch_manifest.v1",
            "run_id": "environment_terrain_component_demo",
            "catalog_component_id": "terrain.crg",
            "instance_id": "terrain.patch.crg_catalog_slot",
            "terrain_component_id": "terrain.crg_road_profile",
            "patch_type": "CRG",
            "chrono_class": "veh.CRGTerrain",
            "origin_frame": "road_s_l_h",
            "pose_xyz_m": "",
            "pose_quat_wxyz": "",
            "bounds_min_xyz_m": "",
            "bounds_max_xyz_m": "",
            "texture_asset": "",
            "material_id": "terrain.material.crg_default",
            "source_path": "not_bound_in_fallback_bundle",
            "source_hash": "",
            "height_scale_m": "file_defined",
            "crg_s_bounds_m": "required_in_live_run",
            "crg_l_bounds_m": "required_in_live_run",
            "query_authority": "true",
            "contact_authority": "tire_model_dependent",
            "source": source,
        },
    ]
    fieldnames = list(rows[0].keys())
    csv_path = write_csv(OUTPUT_CSV / "terrain_patch_manifest.csv", fieldnames, rows)
    json_path = write_json(
        OUTPUT_JSON / "terrain_patch_manifest.json",
        {"schema_id": "terrain.patch_manifest.v1", "run_id": "environment_terrain_component_demo", "source": source, "patches": rows},
    )
    return csv_path, json_path


def write_terrain_material_region_map() -> tuple[Path, Path]:
    source = _terrain_catalog_source()
    rows = [
        {
            "schema_id": "terrain.material_region_map.v1",
            "run_id": "environment_terrain_component_demo",
            "catalog_component_id": "terrain.material_region",
            "instance_id": "terrain.region.high_friction",
            "terrain_component_id": "terrain.heightmap_mesh",
            "region_id": "high_friction_left",
            "region_shape": "AABB",
            "bounds_min_xy_m": "-3.000,-2.000",
            "bounds_max_xy_m": "0.000,2.000",
            "terrain_mu_query": "0.6200",
            "contact_material_mu": "0.6200",
            "material_class": "ChContactMaterialNSC",
            "material_id": "terrain.material.rigid_mu_0p62",
            "friction_functor_id": "analytic_region_friction.v1",
            "calibration_source": "schema fixture for tire/contact query wiring",
            "source": source,
        },
        {
            "schema_id": "terrain.material_region_map.v1",
            "run_id": "environment_terrain_component_demo",
            "catalog_component_id": "terrain.material_region",
            "instance_id": "terrain.region.low_friction",
            "terrain_component_id": "terrain.heightmap_mesh",
            "region_id": "low_friction_right",
            "region_shape": "AABB",
            "bounds_min_xy_m": "0.000,-2.000",
            "bounds_max_xy_m": "3.000,2.000",
            "terrain_mu_query": "0.4800",
            "contact_material_mu": "0.4800",
            "material_class": "ChContactMaterialNSC",
            "material_id": "terrain.material.rigid_mu_0p48",
            "friction_functor_id": "analytic_region_friction.v1",
            "calibration_source": "schema fixture for material map handoff",
            "source": source,
        },
        {
            "schema_id": "terrain.material_region_map.v1",
            "run_id": "environment_terrain_component_demo",
            "catalog_component_id": "terrain.material_region",
            "instance_id": "terrain.region.scm_soil_profile",
            "terrain_component_id": "terrain.scm",
            "region_id": "scm_profile_default",
            "region_shape": "active_domain",
            "bounds_min_xy_m": "-2.200,-1.400",
            "bounds_max_xy_m": "2.200,1.400",
            "terrain_mu_query": "soil_model",
            "contact_material_mu": "soil_model",
            "material_class": "SCMTerrain soil profile",
            "material_id": "scm.soil_profile.default_loam",
            "friction_functor_id": "Bekker_Mohr_Janosi_profile.v1",
            "calibration_source": "catalog values only; live calibration required",
            "source": source,
        },
    ]
    fieldnames = list(rows[0].keys())
    csv_path = write_csv(OUTPUT_CSV / "terrain_material_region_map.csv", fieldnames, rows)
    json_path = write_json(
        OUTPUT_JSON / "terrain_material_region_map.json",
        {"schema_id": "terrain.material_region_map.v1", "run_id": "environment_terrain_component_demo", "source": source, "material_regions": rows},
    )
    return csv_path, json_path


def write_terrain_deformable_domain_manifest() -> Path:
    source = _terrain_catalog_source()
    domains = [
        {
            "schema_id": "terrain.deformable_domain_manifest.v1",
            "run_id": "environment_terrain_component_demo",
            "catalog_component_id": "terrain.scm",
            "instance_id": "terrain.domain.scm_demo",
            "terrain_component_id": "terrain.scm",
            "terrain_type": "SCMTerrain",
            "chrono_class": "chrono.vehicle.SCMTerrain",
            "module_dependency": "Vehicle",
            "module_availability": "catalog_only",
            "backend_identity": "SCM grid",
            "domain_size_m": "4.400,2.800",
            "terrain_dimension_m": "4.400,2.800",
            "active_domain_m": "moving_patch_or_full_grid",
            "terrain_discretization": "SCM grid spacing 0.050 m",
            "grid_spacing_m": "0.050",
            "particle_radius_m": "",
            "particle_density_kg_m3": "",
            "particle_count": "",
            "sph_spacing_m": "",
            "mesh_id": "",
            "element_type": "",
            "rho": "",
            "Emod": "",
            "nu": "",
            "yield_stress": "",
            "hardening_slope": "",
            "friction_angle": "from scm_soil_profile_manifest",
            "dilatancy_angle": "",
            "boundary_condition_id": "",
            "contact_method": "soil-wheel SCM coupling",
            "solver_dt_s": "required_in_live_run",
            "deformation_or_stress_artifact": "",
            "terrain_advance_order": "vehicle/contact load update -> SCMTerrain.Advance",
            "coupling_order": "SCM owns soil deformation; tire/track owns vehicle response",
            "source": source,
        },
        {
            "schema_id": "terrain.deformable_domain_manifest.v1",
            "run_id": "environment_terrain_component_demo",
            "catalog_component_id": "terrain.granular_dem",
            "instance_id": "terrain.domain.granular_catalog_slot",
            "terrain_component_id": "terrain.granular_dem",
            "terrain_type": "GranularTerrain",
            "chrono_class": "chrono.vehicle.GranularTerrain / Chrono::Multicore granular backend",
            "module_dependency": "Vehicle + Granular/Multicore",
            "module_availability": "not_executed",
            "backend_identity": "DEM particle domain",
            "domain_size_m": "required_in_live_run",
            "terrain_dimension_m": "required_in_live_run",
            "active_domain_m": "moving_patch_or_full_domain",
            "terrain_discretization": "DEM particle radius/layers required in live run",
            "grid_spacing_m": "",
            "particle_radius_m": "required_in_live_run",
            "particle_density_kg_m3": "required_in_live_run",
            "particle_count": "required_in_live_run",
            "sph_spacing_m": "",
            "mesh_id": "",
            "element_type": "",
            "rho": "",
            "Emod": "",
            "nu": "",
            "yield_stress": "",
            "hardening_slope": "",
            "friction_angle": "required_in_live_run",
            "dilatancy_angle": "",
            "boundary_condition_id": "",
            "contact_method": "DEM contact",
            "solver_dt_s": "required_in_live_run",
            "deformation_or_stress_artifact": "",
            "terrain_advance_order": "settle/checkpoint -> MBD/terrain coupled advance",
            "coupling_order": "particle contact forces exchanged with MBD bodies",
            "source": source,
        },
        {
            "schema_id": "terrain.deformable_domain_manifest.v1",
            "run_id": "environment_terrain_component_demo",
            "catalog_component_id": "terrain.fea",
            "instance_id": "terrain.domain.fea_catalog_slot",
            "terrain_component_id": "terrain.fea",
            "terrain_type": "FEATerrain",
            "chrono_class": "chrono.vehicle.FEATerrain",
            "module_dependency": "Vehicle + FEA",
            "module_availability": "not_executed",
            "backend_identity": "FEA mesh domain",
            "domain_size_m": "required_in_live_run",
            "terrain_dimension_m": "required_in_live_run",
            "active_domain_m": "mesh boundary condition domain",
            "terrain_discretization": "required_in_live_run",
            "grid_spacing_m": "",
            "particle_radius_m": "",
            "particle_density_kg_m3": "",
            "particle_count": "",
            "sph_spacing_m": "",
            "mesh_id": "required_in_live_run",
            "element_type": "required_in_live_run",
            "rho": "required_in_live_run",
            "Emod": "required_in_live_run",
            "nu": "required_in_live_run",
            "yield_stress": "required_in_live_run",
            "hardening_slope": "required_in_live_run",
            "friction_angle": "required_in_live_run",
            "dilatancy_angle": "required_in_live_run",
            "boundary_condition_id": "required_in_live_run",
            "contact_method": "FEA/contact coupling",
            "solver_dt_s": "required_in_live_run",
            "deformation_or_stress_artifact": "required_in_live_run",
            "terrain_advance_order": "MBD contact/coupling -> FEA solve -> state export",
            "coupling_order": "mesh state and contact reaction must be logged together",
            "source": source,
        },
        {
            "schema_id": "terrain.deformable_domain_manifest.v1",
            "run_id": "environment_terrain_component_demo",
            "catalog_component_id": "terrain.crm",
            "instance_id": "terrain.domain.crm_catalog_slot",
            "terrain_component_id": "terrain.crm",
            "terrain_type": "CRMTerrain",
            "chrono_class": "chrono.vehicle.CRMTerrain / Chrono::FSI SPH",
            "module_dependency": "Vehicle + FSI/SPH",
            "module_availability": "not_executed",
            "backend_identity": "CRM SPH/BCE domain",
            "domain_size_m": "required_in_live_run",
            "terrain_dimension_m": "required_in_live_run",
            "active_domain_m": "SPH active box",
            "terrain_discretization": "SPH spacing and BCE marker files required in live run",
            "grid_spacing_m": "",
            "particle_radius_m": "",
            "particle_density_kg_m3": "",
            "particle_count": "",
            "sph_spacing_m": "required_in_live_run",
            "mesh_id": "",
            "element_type": "",
            "rho": "required_in_live_run",
            "Emod": "",
            "nu": "",
            "yield_stress": "",
            "hardening_slope": "",
            "friction_angle": "",
            "dilatancy_angle": "",
            "boundary_condition_id": "BCE_marker_boundary_required_in_live_run",
            "contact_method": "FSI/SPH coupling",
            "solver_dt_s": "MBD and FSI dt required in live run",
            "deformation_or_stress_artifact": "crm_coupling_step_log_or_sph_state_required_in_live_run",
            "terrain_advance_order": "MBD synchronize -> FSI advance -> exchange forces/state",
            "coupling_order": "BCE/marker files and coupled body ids must be hash-logged",
            "source": source,
        },
    ]
    return write_json(
        OUTPUT_JSON / "terrain_deformable_domain_manifest.json",
        {"schema_id": "terrain.deformable_domain_manifest.v1", "run_id": "environment_terrain_component_demo", "source": source, "domains": domains},
    )


def write_scm_soil_profile_manifest() -> tuple[Path, Path]:
    source = _terrain_catalog_source()
    rows = [
        {
            "schema_id": "terrain.scm_soil_profile_manifest.v1",
            "run_id": "environment_terrain_component_demo",
            "catalog_component_id": "terrain.scm",
            "instance_id": "scm.soil_profile.default_loam",
            "terrain_component_id": "terrain.scm",
            "soil_profile_id": "scm.soil_profile.default_loam",
            "soil_profile_name": "catalog loam fixture",
            "bekker_Kphi": "0.82e6",
            "bekker_Kc": "0.14e4",
            "bekker_n": "1.10",
            "mohr_cohesion_Pa": "1200",
            "mohr_friction_angle_deg": "28.0",
            "janosi_shear_m": "0.018",
            "elastic_stiffness_Pa_per_m": "2.0e7",
            "damping_Ns_per_m3": "3.0e4",
            "soil_callback_id": "none_in_fallback",
            "grid_spacing_m": "0.050",
            "moving_patch_policy": "record body id/OOBB in live run",
            "profile_source": "catalog fixture",
            "calibration_provenance": "illustrative only; replace with plate/wheel calibration before validation",
            "source": source,
        }
    ]
    fieldnames = list(rows[0].keys())
    csv_path = write_csv(OUTPUT_CSV / "scm_soil_profile_manifest.csv", fieldnames, rows)
    json_path = write_json(
        OUTPUT_JSON / "scm_soil_profile_manifest.json",
        {"schema_id": "terrain.scm_soil_profile_manifest.v1", "run_id": "environment_terrain_component_demo", "source": source, "soil_profiles": rows},
    )
    return csv_path, json_path


def _load_terrain_height_friction_sinkage_data():
    csv_path = write_terrain_height_friction_sinkage_csv()
    return np.genfromtxt(csv_path, delimiter=",", names=True, dtype=None, encoding="utf-8")


def render_terrain_height_sinkage_profile_graph() -> Path:
    data = _load_terrain_height_friction_sinkage_data()
    fig, ax = plt.subplots(figsize=(7.8, 4.8))
    sample = data[np.isclose(data["y_m"], 0.0)]
    ax.plot(sample["x_m"], sample["height_m"], color="#2563eb", linewidth=2, label="height")
    ax.plot(sample["x_m"], -sample["scm_sinkage_demo_m"], color="#dc2626", linewidth=2, label="sinkage depth (down)")
    ax.set_title("Terrain Height and SCM Sinkage Profile")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("z [m]")
    ax.grid(True, alpha=0.3)
    ax.legend()
    return save_figure(fig, IMAGES_GRAPH / "terrain_height_sinkage_profile.png")


def render_terrain_contact_material_friction_map_graph() -> Path:
    data = _load_terrain_height_friction_sinkage_data()
    fig, ax = plt.subplots(figsize=(7.8, 4.8))
    scatter = ax.scatter(data["x_m"], data["y_m"], c=data["estimated_friction"], cmap="magma", s=9)
    ax.set_title("Contact Material Friction Map")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_aspect("equal")
    fig.colorbar(scatter, ax=ax, label="friction")
    return save_figure(fig, IMAGES_GRAPH / "terrain_contact_material_friction_map.png")


def _terrain_contact_force_rows() -> list[dict[str, str]]:
    chrono, error = try_import_chrono()
    force_rows = []
    run_id = "environment_terrain_component_demo"
    scenario_id = "contact_probe_schema_v1"
    if chrono is not None:
        system = chrono.ChSystemNSC()
        system.SetGravitationalAcceleration(chrono.ChVector3d(0, 0, -9.81))
        material = chrono.ChContactMaterialNSC()
        material.SetFriction(0.62)
        falling = chrono.ChBodyEasySphere(0.16, 900, True, True, material)
        falling.SetPos(chrono.ChVector3d(0, 0, 1.1))
        ground = chrono.ChBodyEasyBox(2, 2, 0.1, 1000, True, True, material)
        ground.SetFixed(True)
        ground.SetPos(chrono.ChVector3d(0, 0, -0.05))
        system.AddBody(falling)
        system.AddBody(ground)
        step_index = 0
        while system.GetChTime() <= 1.0:
            system.DoStepDynamics(0.005)
            cf = falling.GetContactForce()
            force = vec_length(cf)
            force_rows.append(
                {
                    "run_id": run_id,
                    "schema_id": "terrain.contact_probe.v1",
                    "scenario_id": scenario_id,
                    "time_s": f"{system.GetChTime():.3f}",
                    "step_index": step_index,
                    "terrain_component_id": "terrain.core_ground",
                    "wheel_id": "sphere_probe",
                    "tire_model": "none_sphere_contact_probe",
                    "x_m": "0.000",
                    "y_m": "0.000",
                    "contact_fx_N": "0.00000",
                    "contact_fy_N": "0.00000",
                    "contact_fz_N": f"{force:.5f}",
                    "contact_force_N": f"{force:.5f}",
                    "slip_ratio": "",
                    "drawbar_pull_N": "",
                    "contact_patch": "sphere_ground",
                    "source": "pychrono",
                }
            )
            step_index += 1
        if not force_rows or max(float(row["contact_force_N"]) for row in force_rows) <= 0.0:
            force_rows = []

    if not force_rows:
        for step_index, t in enumerate(np.arange(0, 1.005, 0.005)):
            active = 0.42 <= t <= 0.72
            impact = math.exp(-((t - 0.49) ** 2) / 0.0018) if active else 0.0
            damping = 0.42 * math.exp(-((t - 0.60) ** 2) / 0.018) if active else 0.0
            force = 260.0 * (impact + damping)
            force_rows.append(
                {
                    "run_id": run_id,
                    "schema_id": "terrain.contact_probe.v1",
                    "scenario_id": scenario_id,
                    "time_s": f"{t:.3f}",
                    "step_index": step_index,
                    "terrain_component_id": "terrain.core_ground",
                    "wheel_id": "sphere_probe",
                    "tire_model": "none_sphere_contact_probe",
                    "x_m": "0.000",
                    "y_m": "0.000",
                    "contact_fx_N": "0.00000",
                    "contact_fy_N": "0.00000",
                    "contact_fz_N": f"{force:.5f}",
                    "contact_force_N": f"{force:.5f}",
                    "slip_ratio": "",
                    "drawbar_pull_N": "",
                    "contact_patch": "sphere_ground",
                    "source": f"fallback_{error}",
                }
            )
    return force_rows


def write_terrain_contact_probe_csv() -> Path:
    return write_csv(
        OUTPUT_CSV / "environment_terrain_contact_probe.csv",
        [
            "run_id",
            "schema_id",
            "scenario_id",
            "time_s",
            "step_index",
            "terrain_component_id",
            "wheel_id",
            "tire_model",
            "x_m",
            "y_m",
            "contact_fx_N",
            "contact_fy_N",
            "contact_fz_N",
            "contact_force_N",
            "slip_ratio",
            "drawbar_pull_N",
            "contact_patch",
            "source",
        ],
        _terrain_contact_force_rows(),
    )


def render_terrain_contact_force_probe_graph() -> Path:
    force_csv = write_terrain_contact_probe_csv()
    fdata = np.genfromtxt(force_csv, delimiter=",", names=True)
    fig, ax = plt.subplots(figsize=(7.8, 4.8))
    ax.plot(fdata["time_s"], fdata["contact_force_N"], color="#16a34a", linewidth=2)
    ax.set_title("Ground Contact Material Force Probe")
    ax.set_xlabel("time [s]")
    ax.set_ylabel("contact force [N]")
    ax.grid(True, alpha=0.3)
    return save_figure(fig, IMAGES_GRAPH / "terrain_contact_force_probe.png")


def generate_terrain_csv_and_graphs() -> tuple[Path, list[Path]]:
    csv_path = write_terrain_height_friction_sinkage_csv()
    write_terrain_surface_probe_csv()
    write_terrain_query_probe_csv()
    write_terrain_component_manifest_json()
    write_terrain_patch_manifest()
    write_terrain_material_region_map()
    write_terrain_deformable_domain_manifest()
    write_scm_soil_profile_manifest()
    graphs = [
        render_terrain_height_sinkage_profile_graph(),
        render_terrain_contact_material_friction_map_graph(),
        render_terrain_contact_force_probe_graph(),
    ]
    return csv_path, graphs


def _render_terrain_components_legacy() -> list[Path]:
    paths = []

    def ground_scene(system, chrono):
        vsg_add_box(system, chrono, "rigid_ground_patch", (0, 0, -0.04), (4.8, 3.0, 0.08), (0.58, 0.62, 0.55))
        vsg_add_box(system, chrono, "box_obstacle", (-1.15, 0.62, 0.21), (0.46, 0.46, 0.42), (0.70, 0.12, 0.10))
        vsg_add_cylinder_y(system, chrono, "log_obstacle", (1.15, -0.62, 0.20), 0.20, 0.85, (0.48, 0.28, 0.10))
        vsg_add_box(system, chrono, "rigidterrain_patch_marker", (0.55, 0.55, 0.025), (0.95, 0.60, 0.03), (0.20, 0.42, 0.68), collide=False)

    path = IMAGES_RENDER / "terrain_ground_obstacle_components.png"
    vsg_ok, _ = render_vsg_scene(path, ground_scene, camera=(3.2, -3.4, 1.55), target=(0, 0, 0.22), title="Ground obstacle terrain components")
    if not vsg_ok:
        fig = plt.figure(figsize=(9.0, 5.4))
        ax = fig.add_subplot(111, projection="3d")
        _add_reference_plane(
            ax,
            center=(0, 0, 0.0),
            size=(2.75, 1.65),
            facecolor="#94a3b8",
            edgecolor="#475569",
            fill_alpha=0.12,
            grid_color="#cbd5e1",
        )
        add_box(ax, (-0.82, 0.38, 0.18), (0.34, 0.34, 0.36), "#dc2626", alpha=0.90, edgecolor="#7f1d1d")
        add_cylinder_x(ax, (0.70, -0.30, 0.18), 0.18, 0.62, "#92400e", alpha=0.94)
        _add_reference_plane(
            ax,
            center=(0.45, 0.42, 0.028),
            size=(0.58, 0.36),
            facecolor="#2563eb",
            edgecolor="#1e40af",
            fill_alpha=0.22,
            grid_color="#93c5fd",
            grid=(3, 3),
        )
        add_callout_3d(ax, "Ground: gray plane", (0.10, 0.72), (-1.05, -0.48, 0.01), color="#475569", size=9)
        add_callout_3d(ax, "Box obstacle", (0.42, 0.76), (-0.82, 0.38, 0.36), color="#991b1b", size=9)
        add_callout_3d(ax, "Log obstacle", (0.66, 0.30), (0.70, -0.30, 0.18), color="#92400e", size=9)
        add_callout_3d(ax, "Patch marker", (0.66, 0.68), (0.45, 0.42, 0.05), color="#1e40af", size=9)
        _format_terrain_ax(ax, xlim=(-1.45, 1.45), ylim=(-0.88, 0.88), zlim=(0.0, 0.70), elev=25, azim=-49)
        save_figure(fig, path)
    paths.append(path)

    fig = plt.figure(figsize=(9.0, 5.4))
    ax = fig.add_subplot(111, projection="3d")
    _add_reference_plane(
        ax,
        center=(0.0, 0.0, 0.0),
        size=(2.70, 1.55),
        facecolor="#60a5fa",
        edgecolor="#1d4ed8",
        fill_alpha=0.12,
        grid_color="#2563eb",
        grid_alpha=0.82,
    )
    add_box(ax, (-0.72, -0.32, 0.14), (0.28, 0.20, 0.18), "#2563eb", alpha=0.88)
    add_cylinder_x(ax, (-0.72, -0.32, 0.055), 0.08, 0.30, "#111827", alpha=0.92)
    add_box(ax, (0.72, 0.28, 0.10), (0.38, 0.28, 0.16), "#dc2626", alpha=0.82, edgecolor="#7f1d1d")
    _line3d(ax, (-1.05, -0.32, 0.065), (1.05, -0.32, 0.065), color="#f97316", linewidth=2.8)
    add_callout_3d(ax, "RigidTerrain patch", (0.18, 0.78), (0.0, 0.0, 0.06), color="#1d4ed8", size=9)
    add_callout_3d(ax, "Wheel path", (0.18, 0.70), (-0.15, -0.32, 0.07), color="#c2410c", size=9)
    add_callout_3d(ax, "Obstacle", (0.70, 0.70), (0.72, 0.28, 0.18), color="#991b1b", size=9)
    _format_terrain_ax(ax, xlim=(-1.45, 1.45), ylim=(-0.88, 0.88), zlim=(0.0, 0.62), elev=25, azim=-49)
    paths.append(save_figure(fig, IMAGES_RENDER / "terrain_rigid_patch_component.png"))

    fig = plt.figure(figsize=(9.0, 5.4))
    ax = fig.add_subplot(111, projection="3d")
    _add_reference_plane(
        ax,
        center=(-0.70, 0, 0.0),
        size=(1.45, 1.35),
        facecolor="#64748b",
        edgecolor="#334155",
        fill_alpha=0.22,
        grid_color="#cbd5e1",
    )
    _add_reference_plane(
        ax,
        center=(0.80, 0, 0.0),
        size=(1.45, 1.35),
        facecolor="#f59e0b",
        edgecolor="#92400e",
        fill_alpha=0.22,
        grid_color="#fed7aa",
    )
    for x in np.linspace(-1.15, 1.25, 7):
        add_cylinder_x(ax, (float(x), -0.18, 0.17), 0.10, 0.12, "#111827", alpha=0.92)
        add_cylinder_x(ax, (float(x), 0.18, 0.17), 0.10, 0.12, "#111827", alpha=0.92)
    _line3d(ax, (-1.35, -0.18, 0.05), (1.42, -0.18, 0.05), color="#dc2626", linewidth=2.8)
    _line3d(ax, (-1.35, 0.18, 0.05), (1.42, 0.18, 0.05), color="#dc2626", linewidth=2.8)
    add_callout_3d(ax, "High friction", (0.58, 0.76), (-0.70, 0.0, 0.05), color="#334155", size=9)
    add_callout_3d(ax, "Low friction", (0.72, 0.58), (0.80, 0.0, 0.05), color="#92400e", size=9)
    add_callout_3d(ax, "Wheel tracks", (0.18, 0.64), (-0.45, -0.18, 0.17), color="#991b1b", size=9)
    _format_terrain_ax(ax, xlim=(-1.55, 1.60), ylim=(-0.86, 0.86), zlim=(0.0, 0.62), elev=25, azim=-49)
    paths.append(save_figure(fig, IMAGES_RENDER / "terrain_contact_material_regions.png"))

    def heightmap_scene(system, chrono):
        for xi in np.linspace(-2.4, 2.4, 13):
            for yi in np.linspace(-1.6, 1.6, 9):
                h = float(height_field(xi, yi))
                color = (0.22 + max(h, -0.1) * 1.2, 0.42 + h, 0.22)
                vsg_add_box(system, chrono, "height_cell", (float(xi), float(yi), h / 2 - 0.04), (0.34, 0.34, max(0.035, h + 0.11)), color)
        vsg_add_box(system, chrono, "heightmap_base", (0, 0, -0.10), (5.2, 3.5, 0.04), (0.42, 0.42, 0.38), collide=False)

    path = IMAGES_RENDER / "terrain_heightmap_component.png"
    vsg_ok, _ = render_vsg_scene(path, heightmap_scene, camera=(3.3, -3.5, 1.65), target=(0, 0, 0.05), title="Heightmap terrain component")
    if not vsg_ok:
        fig = plt.figure(figsize=(9.0, 5.4))
        ax = fig.add_subplot(111, projection="3d")
        x_grid = np.linspace(-2.4, 2.4, 40)
        y_grid = np.linspace(-1.6, 1.6, 28)
        xx, yy = np.meshgrid(x_grid, y_grid)
        zz = height_field(xx, yy)
        ax.plot_surface(xx, yy, zz, cmap="terrain", alpha=0.96, linewidth=0, antialiased=True)
        for x in np.linspace(-2.4, 2.4, 7):
            _line3d(ax, (float(x), -1.6, 0.13), (float(x), 1.6, 0.13), color="#ffffff", linewidth=0.7)
        for y in np.linspace(-1.6, 1.6, 5):
            _line3d(ax, (-2.4, float(y), 0.13), (2.4, float(y), 0.13), color="#ffffff", linewidth=0.7)
        add_callout_3d(ax, "Heightmap surface", (0.62, 0.74), (0.0, 0.0, float(height_field(0.0, 0.0))), color="#365314", size=9)
        add_callout_3d(ax, "Height samples", (0.66, 0.36), (1.1, -0.4, float(height_field(1.1, -0.4))), color="#475569", size=9)
        _format_terrain_ax(ax, xlim=(-2.55, 2.55), ylim=(-1.75, 1.75), zlim=(-0.18, 0.28), elev=25, azim=-49)
        save_figure(fig, path)
    paths.append(path)

    def scm_scene(system, chrono):
        for xi in np.linspace(-2.2, 2.2, 12):
            for yi in np.linspace(-1.4, 1.4, 8):
                h = float(scm_surface_height(xi, yi))
                color = (0.40, 0.36 + max(0.0, h), 0.20)
                vsg_add_box(system, chrono, "scm_cell", (float(xi), float(yi), h / 2 - 0.05), (0.34, 0.34, max(0.035, h + 0.12)), color)

    path = IMAGES_RENDER / "terrain_scm_deformation_component.png"
    # Keep the annotated matplotlib path for this report figure so the sinkage
    # leader lands on the actual rut bottom instead of on a raised marker.
    vsg_ok = False
    if not vsg_ok:
        fig = plt.figure(figsize=(9.0, 5.4))
        ax = fig.add_subplot(111, projection="3d")
        x = np.linspace(-2.2, 2.2, 70)
        y = np.linspace(-1.4, 1.4, 46)
        xx, yy = np.meshgrid(x, y)
        zz = scm_surface_height(xx, yy)
        sinkage = scm_sinkage_depth(xx, yy)
        facecolors = plt.cm.gist_earth(np.clip((zz + 0.23) / 0.43, 0.0, 1.0))
        rut = sinkage / max(float(np.max(sinkage)), 1e-6)
        facecolors[..., 0] = facecolors[..., 0] * (1 - 0.38 * rut) + 0.18 * rut
        facecolors[..., 1] = facecolors[..., 1] * (1 - 0.34 * rut) + 0.15 * rut
        facecolors[..., 2] = facecolors[..., 2] * (1 - 0.28 * rut) + 0.13 * rut
        ax.plot_surface(xx, yy, zz, facecolors=facecolors, linewidth=0, antialiased=True, shade=False, alpha=0.98)
        for xi in np.linspace(-2.1, 2.1, 9):
            zs = scm_surface_height(np.full_like(y, xi), y)
            _line3d(ax, (float(xi), -1.35, float(zs[0]) + 0.004), (float(xi), 1.35, float(zs[-1]) + 0.004), color="#3f3f46", linewidth=0.45, alpha=0.35)
        for yi in np.linspace(-1.2, 1.2, 7):
            zs = scm_surface_height(x, np.full_like(x, yi))
            ax.plot(x, np.full_like(x, yi), zs + 0.004, color="#3f3f46", linewidth=0.45, alpha=0.35)
        rut_x = np.linspace(-1.45, 1.65, 120)
        rut_y = np.zeros_like(rut_x)
        rut_z = scm_surface_height(rut_x, rut_y) + 0.010
        ax.plot(rut_x, rut_y, rut_z, color="#78350f", linewidth=3.0, alpha=0.70)
        rut_bottom = (0.2, 0.0, float(scm_surface_height(0.2, 0.0)))
        add_callout_3d(ax, "SCM grid cells", (0.12, 0.76), (-1.2, 0.8, float(scm_surface_height(-1.2, 0.8)) + 0.01), color="#3f3f46", size=9)
        add_callout_3d(ax, "Sinkage track", (0.56, 0.70), rut_bottom, color="#78350f", size=9)
        _format_terrain_ax(ax, xlim=(-2.45, 2.45), ylim=(-1.60, 1.60), zlim=(-0.22, 0.28), elev=25, azim=-49)
        save_figure(fig, path)
    paths.append(path)

    fig = plt.figure(figsize=(9.0, 5.4))
    ax = fig.add_subplot(111, projection="3d")
    xs = np.array([-1.25, 1.25, 1.25, -1.25])
    ys = np.array([-0.75, -0.75, 0.75, 0.75])
    slope = 0.18 * xs
    verts = [[(xs[i], ys[i], slope[i] + 0.08) for i in range(4)]]
    ax.add_collection3d(Poly3DCollection(verts, facecolors="#94a3b8", edgecolors="#334155", linewidths=1.0, alpha=0.24))
    slope_outline = [(xs[i], ys[i], slope[i] + 0.095) for i in range(4)]
    for start, end in zip(slope_outline, slope_outline[1:] + slope_outline[:1]):
        _line3d(ax, start, end, color="#334155", linewidth=1.0, alpha=0.88)
    add_box(ax, (-0.30, 0.0, 0.36), (0.55, 0.42, 0.22), "#2563eb", alpha=0.86)
    ax.quiver(-0.30, 0.0, 0.72, 0.0, 0.0, -0.42, color="#dc2626", linewidth=3.2)
    ax.quiver(-1.10, -0.55, 0.38, 1.10, 0.0, 0.0, color="#f97316", linewidth=3.0)
    ax.quiver(0.30, 0.0, 0.55, 0.45, 0.0, 0.08, color="#16a34a", linewidth=2.6)
    add_callout_3d(ax, "Slope frame", (0.24, 0.72), (-0.30, 0.0, 0.36), color="#475569", size=9)
    add_callout_3d(ax, "Gravity", (0.28, 0.84), (-0.30, 0.0, 0.72), color="#991b1b", size=9)
    add_callout_3d(ax, "Wind/force", (0.12, 0.56), (-0.50, -0.55, 0.38), color="#c2410c", size=9)
    add_callout_3d(ax, "Travel direction", (0.64, 0.60), (0.72, 0.0, 0.63), color="#15803d", size=9)
    _format_terrain_ax(ax, xlim=(-1.45, 1.45), ylim=(-0.95, 0.95), zlim=(0.0, 1.0), elev=24, azim=-50)
    paths.append(save_figure(fig, IMAGES_RENDER / "terrain_environment_field_component.png"))
    return paths


def _generate_terrain_csv_and_graphs_legacy() -> tuple[Path, list[Path]]:
    chrono, error = try_import_chrono()
    rows = []
    material_source = "pychrono" if chrono is not None else f"fallback_{error}"
    for xi in np.linspace(-3.0, 3.0, 61):
        for yi in np.linspace(-2.0, 2.0, 41):
            h = float(height_field(xi, yi))
            friction = 0.62 - 0.10 * min(1.0, abs(h) / 0.14)
            sinkage = max(0.0, 0.16 * math.exp(-((xi - 0.2) ** 2 / 1.5 + yi**2 / 0.35)))
            rows.append(
                {
                    "x_m": f"{xi:.3f}",
                    "y_m": f"{yi:.3f}",
                    "height_m": f"{h:.5f}",
                    "estimated_friction": f"{friction:.4f}",
                    "scm_sinkage_demo_m": f"{sinkage:.5f}",
                    "source": material_source,
                }
            )
    csv_path = write_csv(
        OUTPUT_CSV / "environment_terrain_height_friction_sinkage.csv",
        ["x_m", "y_m", "height_m", "estimated_friction", "scm_sinkage_demo_m", "source"],
        rows,
    )

    data = np.genfromtxt(csv_path, delimiter=",", names=True, dtype=None, encoding="utf-8")
    graphs = []
    fig, ax = plt.subplots(figsize=(7.8, 4.8))
    sample = data[np.isclose(data["y_m"], 0.0)]
    ax.plot(sample["x_m"], sample["height_m"], color="#2563eb", linewidth=2, label="height")
    ax.plot(sample["x_m"], -sample["scm_sinkage_demo_m"], color="#dc2626", linewidth=2, label="sinkage depth (down)")
    ax.set_title("Terrain Height and SCM Sinkage Profile")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("z [m]")
    ax.grid(True, alpha=0.3)
    ax.legend()
    graphs.append(save_figure(fig, IMAGES_GRAPH / "terrain_height_sinkage_profile.png"))

    fig, ax = plt.subplots(figsize=(7.8, 4.8))
    scatter = ax.scatter(data["x_m"], data["y_m"], c=data["estimated_friction"], cmap="magma", s=9)
    ax.set_title("Contact Material Friction Map")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_aspect("equal")
    fig.colorbar(scatter, ax=ax, label="friction")
    graphs.append(save_figure(fig, IMAGES_GRAPH / "terrain_contact_material_friction_map.png"))

    force_rows = []
    if chrono is not None:
        system = chrono.ChSystemNSC()
        system.SetGravitationalAcceleration(chrono.ChVector3d(0, 0, -9.81))
        material = chrono.ChContactMaterialNSC()
        material.SetFriction(0.62)
        falling = chrono.ChBodyEasySphere(0.16, 900, True, True, material)
        falling.SetPos(chrono.ChVector3d(0, 0, 1.1))
        ground = chrono.ChBodyEasyBox(2, 2, 0.1, 1000, True, True, material)
        ground.SetFixed(True)
        ground.SetPos(chrono.ChVector3d(0, 0, -0.05))
        system.AddBody(falling)
        system.AddBody(ground)
        while system.GetChTime() <= 1.0:
            system.DoStepDynamics(0.005)
            cf = falling.GetContactForce()
            force_rows.append({"time_s": f"{system.GetChTime():.3f}", "contact_force_N": f"{vec_length(cf):.5f}"})
        if not force_rows or max(float(row["contact_force_N"]) for row in force_rows) <= 0.0:
            force_rows = []

    if not force_rows:
        for t in np.arange(0, 1.005, 0.005):
            active = 0.42 <= t <= 0.72
            impact = math.exp(-((t - 0.49) ** 2) / 0.0018) if active else 0.0
            damping = 0.42 * math.exp(-((t - 0.60) ** 2) / 0.018) if active else 0.0
            force = 260.0 * (impact + damping)
            force_rows.append({"time_s": f"{t:.3f}", "contact_force_N": f"{force:.5f}"})

    force_csv = write_csv(OUTPUT_CSV / "environment_terrain_contact_probe.csv", ["time_s", "contact_force_N"], force_rows)
    fdata = np.genfromtxt(force_csv, delimiter=",", names=True)
    fig, ax = plt.subplots(figsize=(7.8, 4.8))
    ax.plot(fdata["time_s"], fdata["contact_force_N"], color="#16a34a", linewidth=2)
    ax.set_title("Ground Contact Material Force Probe")
    ax.set_xlabel("time [s]")
    ax.set_ylabel("contact force [N]")
    ax.grid(True, alpha=0.3)
    graphs.append(save_figure(fig, IMAGES_GRAPH / "terrain_contact_force_probe.png"))

    return csv_path, graphs


def main() -> None:
    ensure_output_dirs()
    renders = render_terrain_components()
    csv_path, graphs = generate_terrain_csv_and_graphs()
    print("environment_terrain renders:")
    for path in renders:
        print(path)
    print("environment_terrain csv:", csv_path)
    print("environment_terrain graphs:")
    for path in graphs:
        print(path)


if __name__ == "__main__":
    main()
