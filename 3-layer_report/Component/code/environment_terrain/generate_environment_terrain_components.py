from __future__ import annotations

import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.append(str(Path(__file__).resolve().parents[1] / "common"))

from component_utils import (  # noqa: E402
    IMAGES_GRAPH,
    IMAGES_RENDER,
    OUTPUT_CSV,
    add_box,
    add_cylinder_x,
    add_terrain_surface,
    ensure_output_dirs,
    legend_if_any,
    save_figure,
    set_axes_equal,
    style_3d_axes,
    try_import_chrono,
    vec_length,
    write_csv,
)


def height_field(x, y):
    return 0.10 * np.sin(1.8 * x) * np.cos(1.4 * y) + 0.04 * np.exp(-((x - 0.8) ** 2 + (y + 0.4) ** 2) / 0.25)


def render_terrain_components() -> list[Path]:
    paths = []
    x = np.linspace(-3.0, 3.0, 80)
    y = np.linspace(-2.0, 2.0, 60)
    xx, yy = np.meshgrid(x, y)
    zz = height_field(xx, yy)

    fig = plt.figure(figsize=(8.4, 5.8))
    ax = fig.add_subplot(111, projection="3d")
    add_box(ax, (0, 0, -0.05), (6.4, 4.4, 0.10), "#94a3b8", alpha=0.55, label="Ground/RigidTerrain patch")
    add_box(ax, (-1.2, 0.65, 0.20), (0.45, 0.45, 0.40), "#b91c1c", label="Obstacle")
    add_cylinder_x(ax, (1.3, -0.65, 0.20), 0.20, 0.85, "#92400e", label="Log obstacle")
    ax.set_xlim(-3.4, 3.4)
    ax.set_ylim(-2.4, 2.4)
    ax.set_zlim(0, 1.2)
    style_3d_axes(ax, "Ground, Obstacle, and RigidTerrain Components")
    legend_if_any(ax, loc="upper left", fontsize=8)
    set_axes_equal(ax)
    paths.append(save_figure(fig, IMAGES_RENDER / "terrain_ground_obstacle_components.png"))

    fig = plt.figure(figsize=(8.4, 5.8))
    ax = fig.add_subplot(111, projection="3d")
    add_terrain_surface(ax, xx, yy, zz, cmap="viridis", alpha=0.92)
    ax.text(-2.7, -1.7, 0.36, "Heightmap/uneven rigid surface", fontsize=8)
    ax.set_xlim(-3.2, 3.2)
    ax.set_ylim(-2.2, 2.2)
    ax.set_zlim(-0.25, 0.55)
    style_3d_axes(ax, "Heightmap Terrain Component")
    paths.append(save_figure(fig, IMAGES_RENDER / "terrain_heightmap_component.png"))

    sinkage = -0.18 * np.exp(-((xx - 0.2) ** 2 / 1.5 + yy**2 / 0.35))
    fig = plt.figure(figsize=(8.4, 5.8))
    ax = fig.add_subplot(111, projection="3d")
    add_terrain_surface(ax, xx, yy, zz + sinkage, cmap="cividis", alpha=0.94)
    ax.plot(np.linspace(-1.4, 1.8, 20), np.zeros(20), 0.22 * np.ones(20), color="#ef4444", linewidth=3, label="wheel/track path")
    ax.set_xlim(-3.2, 3.2)
    ax.set_ylim(-2.2, 2.2)
    ax.set_zlim(-0.35, 0.55)
    style_3d_axes(ax, "SCMTerrain Deformation Concept")
    legend_if_any(ax, fontsize=8)
    paths.append(save_figure(fig, IMAGES_RENDER / "terrain_scm_deformation_component.png"))
    return paths


def generate_terrain_csv_and_graphs() -> tuple[Path, list[Path]]:
    chrono, error = try_import_chrono()
    rows = []
    material_source = "pychrono" if chrono is not None else f"fallback: {error}"
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
    legend_if_any(ax)
    graphs.append(save_figure(fig, IMAGES_GRAPH / "terrain_height_sinkage_profile.png"))

    fig, ax = plt.subplots(figsize=(7.8, 4.8))
    scatter = ax.scatter(data["x_m"], data["y_m"], c=data["estimated_friction"], cmap="magma", s=9)
    ax.set_title("Contact Material Friction Map")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_aspect("equal")
    fig.colorbar(scatter, ax=ax, label="friction")
    graphs.append(save_figure(fig, IMAGES_GRAPH / "terrain_contact_material_friction_map.png"))

    if chrono is not None:
        system = chrono.ChSystemNSC()
        material = chrono.ChContactMaterialNSC()
        material.SetFriction(0.62)
        falling = chrono.ChBodyEasySphere(0.16, 900, True, True, material)
        falling.SetPos(chrono.ChVector3d(0, 0, 1.1))
        ground = chrono.ChBodyEasyBox(2, 2, 0.1, 1000, True, True, material)
        ground.SetFixed(True)
        ground.SetPos(chrono.ChVector3d(0, 0, -0.05))
        system.AddBody(falling)
        system.AddBody(ground)
        force_rows = []
        while system.GetChTime() <= 1.0:
            cf = falling.GetContactForce()
            force_rows.append({"time_s": f"{system.GetChTime():.3f}", "contact_force_N": f"{vec_length(cf):.5f}"})
            system.DoStepDynamics(0.005)
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
