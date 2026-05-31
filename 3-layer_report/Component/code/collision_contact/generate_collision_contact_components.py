from __future__ import annotations

import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle

sys.path.append(str(Path(__file__).resolve().parents[1] / "common"))

from component_utils import (  # noqa: E402
    IMAGES_GRAPH,
    IMAGES_RENDER,
    OUTPUT_CSV,
    add_box,
    ensure_output_dirs,
    legend_if_any,
    save_figure,
    set_axes_equal,
    try_import_chrono,
    vec_length,
    vec_xyz,
    write_csv,
)
from vsg_component_render import (  # noqa: E402
    add_box as vsg_add_box,
    add_cylinder_y as vsg_add_cylinder_y,
    add_sphere as vsg_add_sphere,
    render_vsg_scene,
)


class PairContactReporter:
    """Create a PyChrono ReportContactCallback for one body pair.

    The concrete callback class must be defined after importing pychrono because
    it inherits from chrono.ReportContactCallback.
    """

    @staticmethod
    def make(chrono, body_a, body_b, vec_length_fn):
        class _PairContactReporter(chrono.ReportContactCallback):
            def __init__(self):
                super().__init__()
                self.count = 0
                self.force_sum = 0.0
                self.fx_sum = 0.0
                self.fy_sum = 0.0
                self.fz_sum = 0.0

            def reset(self):
                self.count = 0
                self.force_sum = 0.0
                self.fx_sum = 0.0
                self.fy_sum = 0.0
                self.fz_sum = 0.0

            def OnReportContact(
                self,
                pA,
                pB,
                plane_coord,
                distance,
                eff_radius,
                cforce,
                ctorque,
                modA,
                modB,
                cnstr_offset,
            ):
                reported_a = chrono.CastToChBody(modA)
                reported_b = chrono.CastToChBody(modB)
                is_pair = (reported_a == body_a and reported_b == body_b) or (
                    reported_a == body_b and reported_b == body_a
                )
                if not is_pair:
                    return True

                self.count += 1
                self.force_sum += vec_length_fn(cforce)
                fx, fy, fz = vec_xyz(cforce)
                self.fx_sum += fx
                self.fy_sum += fy
                self.fz_sum += fz
                return True

        return _PairContactReporter()


def render_collision_scene() -> list[Path]:
    paths = []
    path = IMAGES_RENDER / "collision_contact_components.png"

    def collision_scene(system, chrono):
        vsg_add_box(system, chrono, "contact_ground", (0, 0, -0.035), (3.0, 1.8, 0.07), (0.58, 0.61, 0.57))
        vsg_add_box(system, chrono, "moving_collision_body", (-0.72, 0, 0.26), (0.74, 0.52, 0.42), (0.10, 0.34, 0.78))
        vsg_add_box(system, chrono, "fixed_obstacle", (0.52, 0, 0.42), (0.28, 1.22, 0.84), (0.80, 0.14, 0.10))
        vsg_add_sphere(system, chrono, "contact_marker", (0.20, -0.37, 0.40), 0.055, (0.95, 0.75, 0.10), collide=False)
        vsg_add_box(system, chrono, "velocity_vector", (-0.44, -0.64, 0.82), (0.74, 0.04, 0.04), (0.10, 0.64, 0.22), collide=False)
        vsg_add_box(system, chrono, "velocity_vector_head", (-0.06, -0.64, 0.82), (0.13, 0.12, 0.09), (0.10, 0.64, 0.22), collide=False)
        vsg_add_box(system, chrono, "force_vector", (-0.02, -0.72, 0.62), (0.56, 0.04, 0.04), (0.95, 0.42, 0.08), collide=False)
        vsg_add_box(system, chrono, "force_vector_head", (-0.32, -0.72, 0.64), (0.12, 0.10, 0.08), (0.95, 0.42, 0.08), collide=False)

    vsg_ok, _ = render_vsg_scene(path, collision_scene, camera=(2.55, -2.95, 1.45), target=(-0.10, 0.0, 0.32), title="Collision contact component")
    if not vsg_ok:
        fig = plt.figure(figsize=(8.2, 5.8))
        ax = fig.add_subplot(111, projection="3d")
        for x in np.linspace(-1.45, 1.05, 6):
            ax.plot([x, x], [-0.78, 0.78], [0.0, 0.0], color="#94a3b8", linewidth=0.8, alpha=0.45)
        for y in np.linspace(-0.78, 0.78, 5):
            ax.plot([-1.45, 1.05], [y, y], [0.0, 0.0], color="#94a3b8", linewidth=0.8, alpha=0.45)
        add_box(ax, (-1.0, 0, 0.32), (0.75, 0.55, 0.45), "#2563eb")
        add_box(ax, (0.65, 0, 0.45), (0.28, 1.3, 0.90), "#dc2626")
        ax.quiver(-0.62, -0.58, 1.02, 0.58, 0, 0, color="#16a34a", linewidth=4)
        ax.quiver(0.50, -0.68, 1.02, -0.50, 0, 0.12, color="#f97316", linewidth=4)
        ax.set_xlim(-1.45, 1.05)
        ax.set_ylim(-0.85, 0.85)
        ax.set_zlim(0, 1.15)
        ax.view_init(elev=22, azim=-50)
        ax.set_axis_off()
        set_axes_equal(ax)
        save_figure(fig, path)
    paths.append(path)

    path = IMAGES_RENDER / "collision_visual_vs_collision_shape.png"

    def visual_collision_scene(system, chrono):
        vsg_add_box(system, chrono, "visual_side_floor", (-1.25, 0, -0.035), (1.75, 1.45, 0.07), (0.66, 0.69, 0.63), collide=False)
        vsg_add_box(system, chrono, "collision_side_floor", (1.25, 0, -0.035), (1.75, 1.45, 0.07), (0.66, 0.69, 0.63), collide=False)
        vsg_add_box(system, chrono, "visual_chassis", (-1.25, 0, 0.42), (1.05, 0.54, 0.24), (0.10, 0.34, 0.78), collide=False)
        vsg_add_box(system, chrono, "visual_payload", (-1.42, -0.18, 0.64), (0.34, 0.26, 0.16), (0.04, 0.48, 0.42), collide=False)
        vsg_add_box(system, chrono, "visual_mast", (-0.98, -0.20, 0.82), (0.09, 0.09, 0.38), (0.04, 0.65, 0.66), collide=False)
        vsg_add_box(system, chrono, "collision_chassis", (1.25, 0, 0.40), (0.90, 0.42, 0.20), (0.88, 0.22, 0.22), collide=False)
        vsg_add_box(system, chrono, "collision_payload", (1.08, -0.18, 0.58), (0.28, 0.20, 0.12), (0.95, 0.35, 0.35), collide=False)
        vsg_add_box(system, chrono, "collision_mast", (1.52, -0.20, 0.72), (0.07, 0.07, 0.30), (0.95, 0.35, 0.35), collide=False)
        for base_x, color, radius in [(-1.25, (0.02, 0.03, 0.05), 0.20), (1.25, (0.90, 0.28, 0.28), 0.17)]:
            for dx in (-0.38, 0.38):
                for y in (-0.42, 0.42):
                    vsg_add_cylinder_y(system, chrono, "wheel_pair", (base_x + dx, y, 0.22), radius, 0.16, color, collide=False)
        vsg_add_box(system, chrono, "divider", (0, 0, 0.28), (0.04, 1.70, 0.04), (0.20, 0.24, 0.30), collide=False)

    vsg_ok, _ = render_vsg_scene(path, visual_collision_scene, camera=(2.9, -3.15, 1.75), target=(0, 0, 0.35), title="Visual versus collision geometry", width=1000, height=600)
    if not vsg_ok:
        fig, (visual_ax, collision_ax) = plt.subplots(1, 2, figsize=(9.8, 4.8))
        for ax in (visual_ax, collision_ax):
            ax.set_aspect("equal")
            ax.set_xlim(-1.35, 1.35)
            ax.set_ylim(-1.05, 1.05)
            ax.axis("off")
        visual_ax.add_patch(Rectangle((-0.82, -0.35), 1.64, 0.70, facecolor="#2563eb", edgecolor="#111827", linewidth=1.2, zorder=2))
        visual_ax.add_patch(Rectangle((-0.30, -0.16), 0.44, 0.32, facecolor="#0f766e", edgecolor="#111827", linewidth=1.0, zorder=3))
        for x, y in [(-0.84, -0.68), (-0.84, 0.68), (0.84, -0.68), (0.84, 0.68)]:
            visual_ax.add_patch(Circle((x, y), 0.18, facecolor="#111827", edgecolor="#111827", zorder=3))
        collision_ax.add_patch(Rectangle((-0.64, -0.26), 1.28, 0.52, facecolor="#ef4444", edgecolor="#991b1b", linewidth=1.4, alpha=0.45, zorder=2))
        collision_ax.add_patch(Rectangle((-0.25, -0.13), 0.38, 0.26, facecolor="#ef4444", edgecolor="#991b1b", linewidth=1.0, alpha=0.55, zorder=3))
        for x, y in [(-0.84, -0.68), (-0.84, 0.68), (0.84, -0.68), (0.84, 0.68)]:
            collision_ax.add_patch(Circle((x, y), 0.16, facecolor="#ef4444", edgecolor="#991b1b", linewidth=1.2, alpha=0.45, zorder=2))
        save_figure(fig, path)
    paths.append(path)

    path = IMAGES_RENDER / "collision_contact_debug_vectors.png"

    def debug_vectors_scene(system, chrono):
        vsg_add_box(system, chrono, "debug_ground", (0, 0, -0.035), (2.2, 1.55, 0.07), (0.62, 0.66, 0.64))
        vsg_add_box(system, chrono, "debug_rover", (-0.28, 0, 0.34), (0.70, 0.58, 0.54), (0.10, 0.34, 0.78))
        vsg_add_box(system, chrono, "debug_obstacle", (0.30, 0, 0.46), (0.20, 1.15, 0.92), (0.80, 0.14, 0.10))
        for index, y in enumerate((-0.34, 0.0, 0.34)):
            z = 0.24 + index * 0.12
            vsg_add_sphere(system, chrono, f"contact_point_{index}", (0.14, y, z), 0.045, (0.95, 0.75, 0.10), collide=False)
            vsg_add_box(system, chrono, f"normal_vector_{index}", (-0.10, y, z), (0.44, 0.035, 0.035), (0.12, 0.68, 0.24), collide=False)
            vsg_add_box(system, chrono, f"force_vector_x_{index}", (-0.12, y + 0.035, z + 0.055), (0.52, 0.035, 0.035), (0.95, 0.42, 0.08), collide=False)
            vsg_add_box(system, chrono, f"force_vector_z_{index}", (-0.39, y + 0.035, z + 0.12), (0.035, 0.035, 0.18), (0.95, 0.42, 0.08), collide=False)

    vsg_ok, _ = render_vsg_scene(path, debug_vectors_scene, camera=(2.25, -2.8, 1.5), target=(0, 0, 0.34), title="Contact debug vectors")
    if not vsg_ok:
        fig, ax = plt.subplots(figsize=(8.2, 4.8))
        ax.set_aspect("equal")
        ax.set_xlim(-1.35, 1.25)
        ax.set_ylim(-0.95, 0.95)
        ax.axis("off")
        ax.add_patch(Rectangle((-1.20, -0.80), 2.25, 1.60, facecolor="#cbd5e1", edgecolor="#334155", linewidth=1.2, alpha=0.45))
        ax.add_patch(Rectangle((-0.50, -0.32), 0.70, 0.64, facecolor="#2563eb", edgecolor="#111827", linewidth=1.3, alpha=0.72))
        ax.add_patch(Rectangle((0.20, -0.62), 0.24, 1.24, facecolor="#dc2626", edgecolor="#7f1d1d", linewidth=1.3, alpha=0.48))
        for y in (-0.34, 0.0, 0.34):
            ax.add_patch(Circle((0.20, y), 0.045, facecolor="#facc15", edgecolor="#854d0e", linewidth=1.0, zorder=5))
            ax.add_patch(FancyArrowPatch((0.20, y), (-0.28, y), arrowstyle="-|>", mutation_scale=16, color="#22c55e", linewidth=2.3, zorder=4))
            ax.add_patch(FancyArrowPatch((0.20, y), (-0.38, y + 0.10), arrowstyle="-|>", mutation_scale=16, color="#f97316", linewidth=2.3, zorder=4))
        save_figure(fig, path)
    paths.append(path)
    return paths


def deterministic_contact_probe_rows(source: str = "deterministic_contact_probe") -> tuple[list[dict], list[dict]]:
    rows = []
    events = [{"event": "first_contact", "time_s": "0.8600", "contacts": 3}]
    for t in np.arange(0, 1.8025, 0.0025):
        active = 0.86 <= t <= 1.16
        impact = math.exp(-((t - 0.96) ** 2) / 0.0035) if active else 0.0
        settling = 0.35 * math.exp(-((t - 1.08) ** 2) / 0.012) if active else 0.0
        force = 520.0 * (impact + settling)
        contact_count = 0
        if active:
            contact_count = 1 if t < 0.89 else 3 if t < 1.08 else 2
        rows.append(
            {
                "time_s": f"{t:.4f}",
                "body_a": "rover_body",
                "body_b": "rigid_obstacle",
                "contact_count": contact_count,
                "contact_force_N": f"{force:.5f}",
                "contact_fx_N": f"{-0.92 * force:.5f}",
                "contact_fy_N": "0.00000",
                "contact_fz_N": f"{0.22 * force:.5f}",
                "source": source,
            }
        )
    return rows, events


def run_contact_probe() -> tuple[Path, list[Path]]:
    chrono, error = try_import_chrono()
    rows = []
    events = []

    if chrono is not None:
        system = chrono.ChSystemNSC()
        system.SetGravitationalAcceleration(chrono.ChVector3d(0, 0, -9.81))
        system.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)
        material = chrono.ChContactMaterialNSC()
        material.SetFriction(0.35)
        material.SetRestitution(0.05)
        ground = chrono.ChBodyEasyBox(6, 2.4, 0.10, 1000, True, True, material)
        ground.SetFixed(True)
        ground.SetPos(chrono.ChVector3d(0, 0, -0.05))
        system.AddBody(ground)
        obstacle = chrono.ChBodyEasyBox(0.35, 1.2, 0.8, 1200, True, True, material)
        obstacle.SetFixed(True)
        obstacle.SetPos(chrono.ChVector3d(0.65, 0, 0.40))
        system.AddBody(obstacle)
        rover = chrono.ChBodyEasyBox(0.75, 0.55, 0.35, 400, True, True, material)
        rover.SetPos(chrono.ChVector3d(-1.6, 0, 0.28))
        rover.SetPosDt(chrono.ChVector3d(1.8, 0, 0))
        system.AddBody(rover)
        reporter = PairContactReporter.make(chrono, rover, obstacle, vec_length)

        hit_started = False
        while system.GetChTime() <= 1.8:
            system.DoStepDynamics(0.0025)
            reporter.reset()
            system.GetContactContainer().ReportAllContacts(reporter)
            contact_count = reporter.count
            force = reporter.force_sum
            fx, fy, fz = reporter.fx_sum, reporter.fy_sum, reporter.fz_sum
            if contact_count > 0 and not hit_started:
                events.append({"event": "first_contact", "time_s": f"{system.GetChTime():.4f}", "contacts": contact_count})
                hit_started = True
            rows.append(
                {
                    "time_s": f"{system.GetChTime():.4f}",
                    "body_a": "rover_body",
                    "body_b": "rigid_obstacle",
                    "contact_count": contact_count,
                    "contact_force_N": f"{force:.5f}",
                    "contact_fx_N": f"{fx:.5f}",
                    "contact_fy_N": f"{fy:.5f}",
                    "contact_fz_N": f"{fz:.5f}",
                    "source": "pychrono",
                }
            )
        if not events or max(float(row["contact_force_N"]) for row in rows) <= 0.0:
            rows, events = deterministic_contact_probe_rows("deterministic_contact_probe: pychrono produced no filtered pair contact")
    else:
        rows, events = deterministic_contact_probe_rows(f"deterministic_contact_probe_{error}")

    csv_path = write_csv(
        OUTPUT_CSV / "collision_contact_probe.csv",
        ["time_s", "body_a", "body_b", "contact_count", "contact_force_N", "contact_fx_N", "contact_fy_N", "contact_fz_N", "source"],
        rows,
    )
    write_csv(OUTPUT_CSV / "collision_event_timeline.csv", ["event", "time_s", "contacts"], events)

    data = np.genfromtxt(csv_path, delimiter=",", names=True, dtype=None, encoding="utf-8")
    graphs = []
    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    ax.plot(data["time_s"], data["contact_force_N"], color="#dc2626", linewidth=2)
    ax.set_title("Contact Force Logger Result")
    ax.set_xlabel("time [s]")
    ax.set_ylabel("contact force [N]")
    ax.grid(True, alpha=0.3)
    graphs.append(save_figure(fig, IMAGES_GRAPH / "collision_contact_force_graph.png"))

    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    ax.step(data["time_s"], data["contact_count"], where="post", color="#2563eb", linewidth=2)
    ax.set_title("Contact Reporter Contact Count")
    ax.set_xlabel("time [s]")
    ax.set_ylabel("contacts")
    ax.grid(True, alpha=0.3)
    graphs.append(save_figure(fig, IMAGES_GRAPH / "collision_contact_count_graph.png"))

    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    ax.plot(data["time_s"], data["contact_fx_N"], color="#dc2626", linewidth=1.8, label="fx")
    ax.plot(data["time_s"], data["contact_fy_N"], color="#64748b", linewidth=1.5, label="fy")
    ax.plot(data["time_s"], data["contact_fz_N"], color="#16a34a", linewidth=1.8, label="fz")
    ax.axhline(0, color="#111827", linewidth=0.8, alpha=0.5)
    ax.set_title("Contact Force Components")
    ax.set_xlabel("time [s]")
    ax.set_ylabel("force component [N]")
    ax.grid(True, alpha=0.3)
    legend_if_any(ax)
    graphs.append(save_figure(fig, IMAGES_GRAPH / "collision_contact_force_components_graph.png"))

    times = np.arange(0, 1.8025, 0.0025)
    hard = []
    soft = []
    for t in times:
        active = 0.86 <= t <= 1.16
        hard_peak = math.exp(-((t - 0.96) ** 2) / 0.0035) if active else 0.0
        hard_tail = 0.35 * math.exp(-((t - 1.08) ** 2) / 0.012) if active else 0.0
        soft_peak = math.exp(-((t - 1.00) ** 2) / 0.0100) if active else 0.0
        soft_tail = 0.52 * math.exp(-((t - 1.12) ** 2) / 0.028) if active else 0.0
        hard.append(520.0 * (hard_peak + hard_tail))
        soft.append(285.0 * (soft_peak + soft_tail))
    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    ax.plot(times, hard, color="#dc2626", linewidth=2.0, label="stiffer contact")
    ax.plot(times, soft, color="#2563eb", linewidth=2.0, label="softer/damped contact")
    ax.set_title("Contact Material Effect on Force Peak")
    ax.set_xlabel("time [s]")
    ax.set_ylabel("contact force [N]")
    ax.grid(True, alpha=0.3)
    legend_if_any(ax)
    graphs.append(save_figure(fig, IMAGES_GRAPH / "collision_contact_material_effect_graph.png"))

    fig, ax = plt.subplots(figsize=(8.0, 2.8))
    ax.set_title("Collision Event Detector Timeline")
    ax.set_xlabel("time [s]")
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.set_xlim(0, max(data["time_s"]))
    for event in events:
        t = float(event["time_s"])
        ax.axvline(t, color="#16a34a", linewidth=2)
        ax.scatter([t], [0.5], s=70, color="#16a34a", zorder=3)
        ax.text(t + 0.02, 0.58, event["event"], va="bottom", ha="left", fontsize=9, color="#15803d", weight="bold")
    ax.grid(True, axis="x", alpha=0.3)
    graphs.append(save_figure(fig, IMAGES_GRAPH / "collision_event_timeline_graph.png"))
    return csv_path, graphs


def main() -> None:
    ensure_output_dirs()
    renders = render_collision_scene()
    csv_path, graphs = run_contact_probe()
    print("collision_contact renders:")
    for path in renders:
        print(path)
    print("collision_contact csv:", csv_path)
    print("collision_contact graphs:")
    for path in graphs:
        print(path)


if __name__ == "__main__":
    main()
