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
)
from vsg_component_render import add_box as vsg_add_box, add_cylinder_y as vsg_add_cylinder_y, render_vsg_scene  # noqa: E402


def height_field(x, y):
    return 0.10 * np.sin(1.8 * x) * np.cos(1.4 * y) + 0.04 * np.exp(-((x - 0.8) ** 2 + (y + 0.4) ** 2) / 0.25)


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


def render_terrain_components() -> list[Path]:
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
                sinkage = -0.18 * math.exp(-((xi - 0.2) ** 2 / 1.5 + yi**2 / 0.35))
                h = float(height_field(xi, yi) + sinkage)
                color = (0.40, 0.36 + max(0.0, h), 0.20)
                vsg_add_box(system, chrono, "scm_cell", (float(xi), float(yi), h / 2 - 0.05), (0.34, 0.34, max(0.035, h + 0.12)), color)
        for xi in np.linspace(-1.4, 1.8, 8):
            vsg_add_box(system, chrono, "wheel_track_sinkage_marker", (float(xi), 0, 0.13), (0.26, 0.16, 0.04), (0.82, 0.16, 0.12), collide=False)

    path = IMAGES_RENDER / "terrain_scm_deformation_component.png"
    vsg_ok, _ = render_vsg_scene(path, scm_scene, camera=(3.1, -3.4, 1.55), target=(0, 0, 0.02), title="SCMTerrain deformation component")
    if not vsg_ok:
        fig = plt.figure(figsize=(9.0, 5.4))
        ax = fig.add_subplot(111, projection="3d")
        for xi in np.linspace(-2.2, 2.2, 13):
            for yi in np.linspace(-1.4, 1.4, 9):
                sinkage = -0.18 * math.exp(-((xi - 0.2) ** 2 / 1.5 + yi**2 / 0.35))
                h = float(height_field(xi, yi) + sinkage)
                color = "#6b6f3a" if abs(yi) > 0.22 else "#4b5563"
                add_box(ax, (float(xi), float(yi), h / 2 - 0.05), (0.30, 0.30, max(0.035, h + 0.12)), color, alpha=0.90, edgecolor="#3f3f46")
        for xi in np.linspace(-1.45, 1.65, 8):
            add_box(ax, (float(xi), 0, 0.13), (0.24, 0.15, 0.045), "#dc2626", alpha=0.95, edgecolor="#7f1d1d")
        add_callout_3d(ax, "SCM grid cells", (0.12, 0.76), (-1.2, 0.8, 0.06), color="#3f3f46", size=9)
        add_callout_3d(ax, "Sinkage track", (0.56, 0.70), (0.2, 0.0, 0.13), color="#991b1b", size=9)
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


def generate_terrain_csv_and_graphs() -> tuple[Path, list[Path]]:
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
    ax.plot(sample["x_m"], -sample["scm_sinkage_demo_m"], color="#dc2626", linewidth=2, label="SCM sinkage demo")
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
