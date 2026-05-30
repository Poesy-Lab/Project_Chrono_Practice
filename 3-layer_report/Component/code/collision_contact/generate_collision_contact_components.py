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
    add_cylinder_y,
    ensure_output_dirs,
    legend_if_any,
    save_figure,
    set_axes_equal,
    style_3d_axes,
    try_import_chrono,
    vec_length,
    vec_xyz,
    write_csv,
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
    fig = plt.figure(figsize=(8.2, 5.8))
    ax = fig.add_subplot(111, projection="3d")
    add_box(ax, (0, 0, -0.05), (5.0, 2.5, 0.10), "#94a3b8", alpha=0.55, label="Ground collision")
    add_box(ax, (-1.0, 0, 0.32), (0.75, 0.55, 0.45), "#2563eb", label="Moving body")
    add_box(ax, (0.65, 0, 0.45), (0.28, 1.3, 0.90), "#dc2626", label="Fixed obstacle")
    ax.quiver(-0.3, 0, 0.45, 0.55, 0, 0, color="#16a34a", linewidth=3, label="velocity")
    ax.quiver(0.55, 0.15, 0.55, -0.45, 0, 0.12, color="#f97316", linewidth=3, label="contact force")
    ax.set_xlim(-2.2, 2.0)
    ax.set_ylim(-1.3, 1.3)
    ax.set_zlim(0, 1.4)
    style_3d_axes(ax, "Collision and Contact Measurement Components")
    legend_if_any(ax, loc="upper left", fontsize=8)
    set_axes_equal(ax)
    paths.append(save_figure(fig, IMAGES_RENDER / "collision_contact_components.png"))

    fig = plt.figure(figsize=(8.2, 5.8))
    ax = fig.add_subplot(111, projection="3d")
    add_box(ax, (0, 0, 0.52), (1.5, 0.8, 0.32), "#2563eb", label="Visual mesh")
    add_box(ax, (0, 0, 0.48), (1.24, 0.62, 0.24), "#ef4444", alpha=0.28, edgecolor="#b91c1c", label="Collision envelope")
    for x in (-0.50, 0.50):
        for y in (-0.50, 0.50):
            add_cylinder_y(ax, (x, y, 0.24), 0.22, 0.14, "#111827")
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.0, 1.0)
    ax.set_zlim(0, 1.1)
    style_3d_axes(ax, "Visual Shape vs Collision Shape")
    legend_if_any(ax, loc="upper left", fontsize=8)
    set_axes_equal(ax)
    paths.append(save_figure(fig, IMAGES_RENDER / "collision_visual_vs_collision_shape.png"))
    return paths


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
                    "contact_count": contact_count,
                    "contact_force_N": f"{force:.5f}",
                    "contact_fx_N": f"{fx:.5f}",
                    "contact_fy_N": f"{fy:.5f}",
                    "contact_fz_N": f"{fz:.5f}",
                    "source": "pychrono",
                }
            )
            system.DoStepDynamics(0.0025)
    else:
        for t in np.arange(0, 1.8025, 0.0025):
            active = 0.86 <= t <= 1.16
            force = 480 * math.exp(-((t - 0.98) ** 2) / 0.006) if active else 0
            rows.append(
                {
                    "time_s": f"{t:.4f}",
                    "contact_count": 3 if active else 0,
                    "contact_force_N": f"{force:.5f}",
                    "contact_fx_N": f"{-force:.5f}",
                    "contact_fy_N": "0.00000",
                    "contact_fz_N": f"{0.2 * force:.5f}",
                    "source": f"fallback: {error}",
                }
            )
        events.append({"event": "first_contact", "time_s": "0.8600", "contacts": 3})

    csv_path = write_csv(
        OUTPUT_CSV / "collision_contact_probe.csv",
        ["time_s", "contact_count", "contact_force_N", "contact_fx_N", "contact_fy_N", "contact_fz_N", "source"],
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

    fig, ax = plt.subplots(figsize=(8.0, 2.4))
    ax.set_title("Collision Event Detector Timeline")
    ax.set_xlabel("time [s]")
    ax.set_yticks([])
    ax.set_xlim(0, max(data["time_s"]))
    for event in events:
        t = float(event["time_s"])
        ax.axvline(t, color="#16a34a", linewidth=2)
        ax.text(t, 0.05, event["event"], rotation=90, va="bottom", ha="right", fontsize=8)
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
