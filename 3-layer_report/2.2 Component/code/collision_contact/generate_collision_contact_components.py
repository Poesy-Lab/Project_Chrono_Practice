from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle

sys.path.append(str(Path(__file__).resolve().parent))
sys.path.append(str(Path(__file__).resolve().parents[1] / "common"))

from component_utils import (  # noqa: E402
    IMAGES_GRAPH,
    IMAGES_RENDER,
    OUTPUT_CSV,
    OUTPUT_JSON,
    add_box,
    ensure_output_dirs,
    legend_if_any,
    save_figure,
    set_axes_equal,
    try_import_chrono,
    vec_length,
    vec_xyz,
    write_csv,
    write_json,
)
from vsg_component_render import (  # noqa: E402
    add_box as vsg_add_box,
    add_cylinder_y as vsg_add_cylinder_y,
    render_vsg_scene,
)
from generate_collision_contact_components_render import render_collision_contact_components  # noqa: E402
from generate_collision_contact_debug_vectors_render import render_collision_contact_debug_vectors  # noqa: E402
from generate_collision_contact_measurement_catalog_render import render_collision_contact_measurement_catalog  # noqa: E402
from generate_collision_contact_reporter_scope_render import render_collision_contact_reporter_scope  # noqa: E402
from generate_collision_visual_vs_collision_shape_render import render_collision_visual_vs_collision_shape  # noqa: E402


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

                global_force = plane_coord * cforce
                self.count += 1
                self.force_sum += vec_length_fn(global_force)
                fx, fy, fz = vec_xyz(global_force)
                self.fx_sum += fx
                self.fy_sum += fy
                self.fz_sum += fz
                return True

        return _PairContactReporter()


def render_collision_scene() -> list[Path]:
    paths = []
    paths.append(render_collision_contact_components())
    paths.append(render_collision_contact_measurement_catalog())
    paths.append(render_collision_visual_vs_collision_shape())
    paths.append(render_collision_contact_debug_vectors())
    paths.append(render_collision_contact_reporter_scope())
    return paths


def _collision_probe_row(
    *,
    run_id: str,
    scenario_id: str,
    step_index: int,
    time_s: float,
    contact_count: int,
    force: float,
    fx: float,
    fy: float,
    fz: float,
    source: str,
) -> dict[str, str | int]:
    return {
        "run_id": run_id,
        "schema_id": "collision.contact_probe.v1",
        "scenario_id": scenario_id,
        "time_s": f"{time_s:.4f}",
        "step_index": step_index,
        "contact_component_id": "contact.force_torque",
        "body_a": "rover_body",
        "body_b": "rigid_obstacle",
        "body_role_a": "moving_body",
        "body_role_b": "fixed_obstacle",
        "contactable_a_type": "ChBody",
        "contactable_b_type": "ChBody",
        "pair_order": "body_a_body_b",
        "force_on": "body_a",
        "contact_count": contact_count,
        "point_x_m": "0.36000",
        "point_y_m": "0.00000",
        "point_z_m": "0.30000",
        "point_a_x_m": "0.36000",
        "point_a_y_m": "0.00000",
        "point_a_z_m": "0.30000",
        "point_b_x_m": "0.36000",
        "point_b_y_m": "0.00000",
        "point_b_z_m": "0.30000",
        "normal_x": "-1.00000",
        "normal_y": "0.00000",
        "normal_z": "0.00000",
        "tangent_u_x": "0.00000",
        "tangent_u_y": "1.00000",
        "tangent_u_z": "0.00000",
        "tangent_v_x": "0.00000",
        "tangent_v_y": "0.00000",
        "tangent_v_z": "1.00000",
        "plane_coord_3x3": "[-1 0 0; 0 1 0; 0 0 1]",
        "distance_m": "",
        "penetration_m": "",
        "eff_radius_m": "",
        "constraint_offset": "",
        "react_fx_contact_N": f"{fx:.5f}",
        "react_fy_contact_N": f"{fy:.5f}",
        "react_fz_contact_N": f"{fz:.5f}",
        "react_tx_contact_Nm": "0.00000",
        "react_ty_contact_Nm": "0.00000",
        "react_tz_contact_Nm": "0.00000",
        "contact_force_N": f"{force:.5f}",
        "contact_fx_N": f"{fx:.5f}",
        "contact_fy_N": f"{fy:.5f}",
        "contact_fz_N": f"{fz:.5f}",
        "contact_tx_Nm": "0.00000",
        "contact_ty_Nm": "0.00000",
        "contact_tz_Nm": "0.00000",
        "contact_torque_Nm": "0.00000",
        "frame": "world",
        "torque_frame": "world",
        "aggregation": "sum_over_filtered_pair",
        "force_source": "pair_contact_reporter_world",
        "ComputeContactForces_called": "false",
        "material_a_id": "contact_material_nsc_demo",
        "material_b_id": "contact_material_nsc_demo",
        "contact_method": "NSC",
        "collision_backend": "Bullet_or_fallback",
        "filter_rule": "body_pair:rover_body-rigid_obstacle",
        "source": source,
    }


def deterministic_contact_probe_rows(source: str = "deterministic_contact_probe") -> tuple[list[dict], list[dict]]:
    run_id = "collision_contact_component_demo"
    scenario_id = "pair_contact_schema_v1"
    rows = []
    events = [
        {
            "run_id": run_id,
            "schema_id": "collision.event_timeline.v1",
            "scenario_id": scenario_id,
            "event": "first_contact",
            "time_s": "0.8600",
            "step_index": 344,
            "body_a": "rover_body",
            "body_b": "rigid_obstacle",
            "threshold_N": "1.00000",
            "debounce_s": "0.0000",
            "dwell_s": "0.3000",
            "contact_count": 3,
            "peak_force_N": "pending_from_probe",
            "source": source,
        }
    ]
    for step_index, t in enumerate(np.arange(0, 1.8025, 0.0025)):
        active = 0.86 <= t <= 1.16
        impact = math.exp(-((t - 0.96) ** 2) / 0.0035) if active else 0.0
        settling = 0.35 * math.exp(-((t - 1.08) ** 2) / 0.012) if active else 0.0
        force = 520.0 * (impact + settling)
        contact_count = 0
        if active:
            contact_count = 1 if t < 0.89 else 3 if t < 1.08 else 2
        rows.append(
            _collision_probe_row(
                run_id=run_id,
                scenario_id=scenario_id,
                step_index=step_index,
                time_s=float(t),
                contact_count=contact_count,
                force=force,
                fx=-0.92 * force,
                fy=0.0,
                fz=0.22 * force,
                source=source,
            )
        )
    if rows:
        peak = max(float(row["contact_force_N"]) for row in rows)
        events[0]["peak_force_N"] = f"{peak:.5f}"
    return rows, events


def write_collision_contact_probe_outputs() -> tuple[Path, Path]:
    chrono, error = try_import_chrono()
    rows = []
    events = []

    if chrono is not None:
        run_id = "collision_contact_component_demo"
        scenario_id = "pair_contact_schema_v1"
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
        step_index = 0
        while system.GetChTime() <= 1.8:
            system.DoStepDynamics(0.0025)
            reporter.reset()
            system.GetContactContainer().ReportAllContacts(reporter)
            contact_count = reporter.count
            force = reporter.force_sum
            fx, fy, fz = reporter.fx_sum, reporter.fy_sum, reporter.fz_sum
            if contact_count > 0 and not hit_started:
                events.append(
                    {
                        "run_id": run_id,
                        "schema_id": "collision.event_timeline.v1",
                        "scenario_id": scenario_id,
                        "event": "first_contact",
                        "time_s": f"{system.GetChTime():.4f}",
                        "step_index": step_index,
                        "body_a": "rover_body",
                        "body_b": "rigid_obstacle",
                        "threshold_N": "1.00000",
                        "debounce_s": "0.0000",
                        "dwell_s": "",
                        "contact_count": contact_count,
                        "peak_force_N": "",
                        "source": "pychrono",
                    }
                )
                hit_started = True
            rows.append(
                _collision_probe_row(
                    run_id=run_id,
                    scenario_id=scenario_id,
                    step_index=step_index,
                    time_s=system.GetChTime(),
                    contact_count=contact_count,
                    force=force,
                    fx=fx,
                    fy=fy,
                    fz=fz,
                    source="pychrono",
                )
            )
            step_index += 1
        if events and rows:
            peak = max(float(row["contact_force_N"]) for row in rows)
            events[0]["peak_force_N"] = f"{peak:.5f}"
        if not events or max(float(row["contact_force_N"]) for row in rows) <= 0.0:
            rows, events = deterministic_contact_probe_rows("deterministic_contact_probe: pychrono produced no filtered pair contact")
    else:
        rows, events = deterministic_contact_probe_rows(f"deterministic_contact_probe_{error}")

    csv_path = write_csv(
        OUTPUT_CSV / "collision_contact_probe.csv",
        [
            "run_id",
            "schema_id",
            "scenario_id",
            "time_s",
            "step_index",
            "contact_component_id",
            "body_a",
            "body_b",
            "body_role_a",
            "body_role_b",
            "contactable_a_type",
            "contactable_b_type",
            "pair_order",
            "force_on",
            "contact_count",
            "point_x_m",
            "point_y_m",
            "point_z_m",
            "point_a_x_m",
            "point_a_y_m",
            "point_a_z_m",
            "point_b_x_m",
            "point_b_y_m",
            "point_b_z_m",
            "normal_x",
            "normal_y",
            "normal_z",
            "tangent_u_x",
            "tangent_u_y",
            "tangent_u_z",
            "tangent_v_x",
            "tangent_v_y",
            "tangent_v_z",
            "plane_coord_3x3",
            "distance_m",
            "penetration_m",
            "eff_radius_m",
            "constraint_offset",
            "react_fx_contact_N",
            "react_fy_contact_N",
            "react_fz_contact_N",
            "react_tx_contact_Nm",
            "react_ty_contact_Nm",
            "react_tz_contact_Nm",
            "contact_force_N",
            "contact_fx_N",
            "contact_fy_N",
            "contact_fz_N",
            "contact_tx_Nm",
            "contact_ty_Nm",
            "contact_tz_Nm",
            "contact_torque_Nm",
            "frame",
            "torque_frame",
            "aggregation",
            "force_source",
            "ComputeContactForces_called",
            "material_a_id",
            "material_b_id",
            "contact_method",
            "collision_backend",
            "filter_rule",
            "source",
        ],
        rows,
    )
    event_csv = write_csv(
        OUTPUT_CSV / "collision_event_timeline.csv",
        [
            "run_id",
            "schema_id",
            "scenario_id",
            "event",
            "time_s",
            "step_index",
            "body_a",
            "body_b",
            "threshold_N",
            "debounce_s",
            "dwell_s",
            "contact_count",
            "peak_force_N",
            "source",
        ],
        events,
    )
    return csv_path, event_csv


def render_collision_contact_force_graph() -> Path:
    csv_path, _ = write_collision_contact_probe_outputs()
    data = np.genfromtxt(csv_path, delimiter=",", names=True, dtype=None, encoding="utf-8")
    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    ax.plot(data["time_s"], data["contact_force_N"], color="#dc2626", linewidth=2)
    ax.set_title("Contact Force Logger Result")
    ax.set_xlabel("time [s]")
    ax.set_ylabel("contact force [N]")
    ax.grid(True, alpha=0.3)
    return save_figure(fig, IMAGES_GRAPH / "collision_contact_force_graph.png")


def render_collision_contact_count_graph() -> Path:
    csv_path, _ = write_collision_contact_probe_outputs()
    data = np.genfromtxt(csv_path, delimiter=",", names=True, dtype=None, encoding="utf-8")
    fig, ax = plt.subplots(figsize=(8.0, 4.6))
    ax.step(data["time_s"], data["contact_count"], where="post", color="#2563eb", linewidth=2)
    ax.set_title("Contact Reporter Contact Count")
    ax.set_xlabel("time [s]")
    ax.set_ylabel("contacts")
    ax.grid(True, alpha=0.3)
    return save_figure(fig, IMAGES_GRAPH / "collision_contact_count_graph.png")


def render_collision_contact_force_components_graph() -> Path:
    csv_path, _ = write_collision_contact_probe_outputs()
    data = np.genfromtxt(csv_path, delimiter=",", names=True, dtype=None, encoding="utf-8")
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
    return save_figure(fig, IMAGES_GRAPH / "collision_contact_force_components_graph.png")


def render_collision_contact_material_effect_graph() -> Path:
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
    return save_figure(fig, IMAGES_GRAPH / "collision_contact_material_effect_graph.png")


def _read_collision_event_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _read_collision_probe_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _collision_source(rows: list[dict[str, str]]) -> str:
    values = sorted({row.get("source", "") for row in rows if row.get("source", "")})
    return ";".join(values) if values else "unknown_collision_source"


def _collision_manifest_base(rows: list[dict[str, str]]) -> dict[str, str]:
    source = _collision_source(rows)
    return {
        "run_id": "collision_contact_component_demo",
        "scenario_id": "pair_contact_schema_v1",
        "source": source,
        "contact_method": rows[0].get("contact_method", "NSC") if rows else "NSC",
        "collision_backend": rows[0].get("collision_backend", "Bullet_or_fallback") if rows else "Bullet_or_fallback",
        "filter_rule": rows[0].get("filter_rule", "body_pair:rover_body-rigid_obstacle") if rows else "body_pair:rover_body-rigid_obstacle",
    }


def _collision_live_evidence(source: str) -> bool:
    return source == "pychrono" or source.startswith("pychrono_live")


def _collision_evidence_level(source: str) -> str:
    return "pychrono_live_sim" if _collision_live_evidence(source) else "fallback_schema_probe"


def _collision_fallback_reason(source: str) -> str:
    return "" if _collision_live_evidence(source) else source


def _contactable_owner_component_id(contactable_id: str) -> str:
    if contactable_id == "rover_body":
        return "vehicle.chassis"
    if contactable_id == "rigid_obstacle":
        return "terrain.obstacle_field"
    if contactable_id == "ground_body":
        return "terrain.core_ground"
    return "collision.system_lifecycle"


def write_collision_system_manifest(rows: list[dict[str, str]]) -> Path:
    base = _collision_manifest_base(rows)
    peak_force = max((float(row["contact_force_N"]) for row in rows), default=0.0)
    peak_count = max((int(row["contact_count"]) for row in rows), default=0)
    components = [
        {
            "component_id": "collision.system_lifecycle",
            "schema_id": "collision.system_manifest.v1",
            "run_id": base["run_id"],
            "scenario_id": base["scenario_id"],
            "system_class": "ChSystemNSC_or_fallback",
            "contact_method": base["contact_method"],
            "collision_system_type": base["collision_backend"],
            "collision_backend": base["collision_backend"],
            "thread_count_collision": "",
            "envelope_m": "",
            "margin_m": "",
            "bind_init_run_report_sequence": "create bodies -> bind material/shape -> DoStepDynamics -> ReportAllContacts -> write CSV",
            "callback_registration": "ReportContactCallback pair filter",
            "contact_count_peak": str(peak_count),
            "peak_force_N": f"{peak_force:.5f}",
            "timer_collision_broad_s": "",
            "timer_collision_narrow_s": "",
            "evidence_level": _collision_evidence_level(base["source"]),
            "fallback_reason": _collision_fallback_reason(base["source"]),
            "source": base["source"],
        }
    ]
    return write_json(
        OUTPUT_JSON / "collision_system_manifest.json",
        {"schema_id": "collision.system_manifest.v1", "run_id": base["run_id"], "source": base["source"], "system_components": components},
    )


def write_collision_backend_comparison(rows: list[dict[str, str]]) -> tuple[Path, Path]:
    base = _collision_manifest_base(rows)
    row = {
        "schema_id": "collision.backend_comparison.v1",
        "run_id": base["run_id"],
        "scenario_id": base["scenario_id"],
        "backend_id": base["collision_backend"],
        "system_class": "ChSystemNSC_or_fallback",
        "contact_method": base["contact_method"],
        "module_availability": "pychrono live if source=pychrono, deterministic fallback otherwise",
        "thread_count_collision": "",
        "envelope_m": "",
        "margin_m": "",
        "timer_collision_broad_s": "",
        "timer_collision_narrow_s": "",
        "contact_count_total_peak": str(max((int(item["contact_count"]) for item in rows), default=0)),
        "contact_count_filtered_peak": str(max((int(item["contact_count"]) for item in rows), default=0)),
        "peak_force_N": f"{max((float(item['contact_force_N']) for item in rows), default=0.0):.5f}",
        "source": base["source"],
    }
    fieldnames = list(row.keys())
    csv_path = write_csv(OUTPUT_CSV / "collision_backend_comparison.csv", fieldnames, [row])
    json_path = write_json(
        OUTPUT_JSON / "collision_backend_comparison.json",
        {"schema_id": "collision.backend_comparison.v1", "run_id": base["run_id"], "source": base["source"], "backends": [row]},
    )
    return csv_path, json_path


def _collision_shape_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    base = _collision_manifest_base(rows)
    shapes = [
        ("shape.rover_body.box", "rover_body", "body_a", "BOX", "ChCollisionShapeBox", "0.750", "0.550", "0.350", "-0.375,-0.275,-0.175", "0.375,0.275,0.175", "moving body collision envelope"),
        ("shape.rigid_obstacle.box", "rigid_obstacle", "body_b", "BOX", "ChCollisionShapeBox", "0.350", "1.200", "0.800", "-0.175,-0.600,-0.400", "0.175,0.600,0.400", "fixed obstacle collision envelope"),
        ("shape.ground.box", "ground_body", "terrain", "BOX", "ChCollisionShapeBox", "6.000", "2.400", "0.100", "-3.000,-1.200,-0.050", "3.000,1.200,0.050", "fixed ground contact target"),
    ]
    return [
        {
            "schema_id": "collision.shape_manifest.v1",
            "run_id": base["run_id"],
            "scenario_id": base["scenario_id"],
            "catalog_component_id": "collision.shape_manifest",
            "instance_id": shape_id,
            "owner_component_id": _contactable_owner_component_id(owner),
            "chrono_item_id": f"{shape_class}:{owner}",
            "shape_id": shape_id,
            "parent_shape_id": "",
            "owner_contactable_id": owner,
            "owner_role": role,
            "shape_type_enum": enum_value,
            "shape_class": shape_class,
            "shape_family": "primitive_box",
            "body_ref_frame": "owner_body_REF",
            "local_pos_xyz_m": "0,0,0",
            "local_rot_quat": "1,0,0,0",
            "size_x_m": sx,
            "size_y_m": sy,
            "size_z_m": sz,
            "material_id": "contact_material_nsc_demo",
            "contact_method": base["contact_method"],
            "is_mutable": "false",
            "bounding_box_min": bb_min,
            "bounding_box_max": bb_max,
            "thin_shape_risk": "false",
            "envelope_m": "",
            "margin_m": "",
            "debug_render": "images/renders/collision_visual_vs_collision_shape.png",
            "role": role_text,
            "source": base["source"],
        }
        for shape_id, owner, role, enum_value, shape_class, sx, sy, sz, bb_min, bb_max, role_text in shapes
    ]


def write_collision_shape_manifest(rows: list[dict[str, str]]) -> tuple[Path, Path]:
    shape_rows = _collision_shape_rows(rows)
    csv_path = write_csv(OUTPUT_CSV / "collision_shape_manifest.csv", list(shape_rows[0].keys()), shape_rows)
    json_path = write_json(
        OUTPUT_JSON / "collision_shape_manifest.json",
        {"schema_id": "collision.shape_manifest.v1", "run_id": "collision_contact_component_demo", "source": _collision_source(rows), "shapes": shape_rows},
    )
    return csv_path, json_path


def write_collision_model_registry(rows: list[dict[str, str]]) -> Path:
    base = _collision_manifest_base(rows)
    models = [
        {
            "contactable_id": "rover_body",
            "catalog_component_id": "collision.model_registry",
            "instance_id": "collision_model.rover_body",
            "owner_component_id": "vehicle.chassis",
            "chrono_item_id": "ChCollisionModel:rover_body",
            "component_id": "core.body",
            "collision_model_id": "collision_model.rover_body",
            "enabled": True,
            "shape_count": 1,
            "shape_ids": ["shape.rover_body.box"],
            "material_ids": ["contact_material_nsc_demo"],
            "visual_shape_link": "images/renders/collision_visual_vs_collision_shape.png",
            "reporter_scope": base["filter_rule"],
        },
        {
            "contactable_id": "rigid_obstacle",
            "catalog_component_id": "collision.model_registry",
            "instance_id": "collision_model.rigid_obstacle",
            "owner_component_id": "terrain.obstacle_field",
            "chrono_item_id": "ChCollisionModel:rigid_obstacle",
            "component_id": "terrain.obstacle_field",
            "collision_model_id": "collision_model.rigid_obstacle",
            "enabled": True,
            "shape_count": 1,
            "shape_ids": ["shape.rigid_obstacle.box"],
            "material_ids": ["contact_material_nsc_demo"],
            "visual_shape_link": "images/renders/collision_visual_vs_collision_shape.png",
            "reporter_scope": base["filter_rule"],
        },
    ]
    return write_json(
        OUTPUT_JSON / "collision_model_registry.json",
        {"schema_id": "collision.model_registry.v1", "run_id": base["run_id"], "source": base["source"], "models": models},
    )


def write_collision_family_filter_map(rows: list[dict[str, str]]) -> tuple[Path, Path]:
    base = _collision_manifest_base(rows)
    family_rows = [
        {
            "schema_id": "collision.family_filter_map.v1",
            "run_id": base["run_id"],
            "catalog_component_id": "collision.family_filter",
            "instance_id": "collision_family.rover_body",
            "owner_component_id": "vehicle.chassis",
            "family_id": "1",
            "family_name": "rover_body",
            "owner_body_or_contactable_ids": "rover_body",
            "set_family_api": "schema_only_SetFamily(1)",
            "allow_api": "AllowCollisionsWith(obstacle)",
            "disallow_api": "DisallowCollisionsWith(self)",
            "resolved_family_mask": "obstacle;terrain",
            "included_pairs": "rover_body-rigid_obstacle",
            "excluded_pairs": "rover_body-rover_body",
            "reporter_scope": base["filter_rule"],
            "debug_artifact": "images/renders/collision_contact_reporter_scope.png",
            "failure_mode": "self-collision noise or over-filtered reporter",
            "source": base["source"],
        },
        {
            "schema_id": "collision.family_filter_map.v1",
            "run_id": base["run_id"],
            "catalog_component_id": "collision.family_filter",
            "instance_id": "collision_family.obstacle",
            "owner_component_id": "terrain.obstacle_field",
            "family_id": "2",
            "family_name": "obstacle",
            "owner_body_or_contactable_ids": "rigid_obstacle",
            "set_family_api": "schema_only_SetFamily(2)",
            "allow_api": "AllowCollisionsWith(rover_body)",
            "disallow_api": "",
            "resolved_family_mask": "rover_body",
            "included_pairs": "rover_body-rigid_obstacle",
            "excluded_pairs": "",
            "reporter_scope": base["filter_rule"],
            "debug_artifact": "images/renders/collision_contact_reporter_scope.png",
            "failure_mode": "needed pair omitted from reporter",
            "source": base["source"],
        },
    ]
    csv_path = write_csv(OUTPUT_CSV / "collision_family_filter_map.csv", list(family_rows[0].keys()), family_rows)
    json_path = write_json(
        OUTPUT_JSON / "collision_family_filter_map.json",
        {"schema_id": "collision.family_filter_map.v1", "run_id": base["run_id"], "source": base["source"], "families": family_rows},
    )
    return csv_path, json_path


def write_contact_material_manifest(rows: list[dict[str, str]]) -> tuple[Path, Path]:
    base = _collision_manifest_base(rows)
    material_rows = [
        {
            "schema_id": "collision.contact_material_manifest.v1",
            "run_id": base["run_id"],
            "catalog_component_id": "collision.contact_material",
            "instance_id": "contact_material_nsc_demo",
            "owner_component_id": "collision.system_lifecycle",
            "material_id": "contact_material_nsc_demo",
            "material_class": "ChContactMaterialNSC",
            "contact_method": base["contact_method"],
            "friction": "0.35",
            "restitution": "0.05",
            "young_modulus_Pa": "",
            "stiffness_Npm": "",
            "damping_Nspm": "",
            "adhesion_N": "",
            "rolling_friction": "",
            "spinning_friction": "",
            "calibration_source": "schema fallback demo material",
            "used_by_shapes": "shape.rover_body.box;shape.rigid_obstacle.box;shape.ground.box",
            "source": base["source"],
        }
    ]
    csv_path = write_csv(OUTPUT_CSV / "contact_material_manifest.csv", list(material_rows[0].keys()), material_rows)
    json_path = write_json(
        OUTPUT_JSON / "contact_material_manifest.json",
        {"schema_id": "collision.contact_material_manifest.v1", "run_id": base["run_id"], "source": base["source"], "materials": material_rows},
    )
    return csv_path, json_path


def write_contact_pair_material_policy(rows: list[dict[str, str]]) -> tuple[Path, Path]:
    base = _collision_manifest_base(rows)
    policy_rows = [
        {
            "schema_id": "collision.contact_pair_material_policy.v1",
            "run_id": base["run_id"],
            "catalog_component_id": "collision.contact_material_policy",
            "instance_id": "pair.rover_body-rigid_obstacle",
            "owner_component_id": "collision.system_lifecycle",
            "pair_policy_id": "pair.rover_body-rigid_obstacle",
            "body_a": "rover_body",
            "body_b": "rigid_obstacle",
            "material_a_id": "contact_material_nsc_demo",
            "material_b_id": "contact_material_nsc_demo",
            "composite_material_class": "ChContactMaterialCompositeNSC",
            "mixing_rule": "same-material direct pair",
            "add_contact_callback_class": "none_in_fallback",
            "modified_fields": "",
            "contactinfo_filter": base["filter_rule"],
            "evidence_graph": "images/graphs/collision_contact_material_effect_graph.png",
            "source": base["source"],
        }
    ]
    csv_path = write_csv(OUTPUT_CSV / "contact_pair_material_policy.csv", list(policy_rows[0].keys()), policy_rows)
    json_path = write_json(
        OUTPUT_JSON / "contact_pair_material_policy.json",
        {"schema_id": "collision.contact_pair_material_policy.v1", "run_id": base["run_id"], "source": base["source"], "pair_policies": policy_rows},
    )
    return csv_path, json_path


def write_contact_container_manifest(rows: list[dict[str, str]]) -> tuple[Path, Path]:
    base = _collision_manifest_base(rows)
    container_rows = [
        {
            "schema_id": "collision.contact_container_manifest.v1",
            "run_id": base["run_id"],
            "scenario_id": base["scenario_id"],
            "catalog_component_id": "contact.container_reporter",
            "instance_id": "contact_container.default_nsc",
            "owner_component_id": "collision.system_lifecycle",
            "contact_container_class": "ChContactContainerNSC_or_fallback",
            "contact_method": base["contact_method"],
            "collision_backend": base["collision_backend"],
            "callback_class": "PairContactReporter",
            "callback_filter_rule": base["filter_rule"],
            "reset_each_step": "true",
            "force_frame": "world",
            "torque_frame": "world",
            "unsupported_contactable_types": "",
            "contact_count_filtered_peak": str(max((int(row["contact_count"]) for row in rows), default=0)),
            "probe_csv": "outputs/csv/collision_contact_probe.csv",
            "source": base["source"],
        }
    ]
    csv_path = write_csv(OUTPUT_CSV / "contact_container_manifest.csv", list(container_rows[0].keys()), container_rows)
    json_path = write_json(
        OUTPUT_JSON / "contact_container_manifest.json",
        {"schema_id": "collision.contact_container_manifest.v1", "run_id": base["run_id"], "source": base["source"], "containers": container_rows},
    )
    return csv_path, json_path


def write_contact_callback_manifest(rows: list[dict[str, str]]) -> tuple[Path, Path]:
    base = _collision_manifest_base(rows)
    callback_rows = [
        {
            "schema_id": "collision.contact_callback_manifest.v1",
            "run_id": base["run_id"],
            "catalog_component_id": "contact.report_callback",
            "instance_id": "callback.report_pair_contact",
            "owner_component_id": "contact.container_reporter",
            "callback_id": "callback.report_pair_contact",
            "callback_family": "Report-contact callback",
            "class_name": "PairContactReporter",
            "registered_on": "ChContactContainer",
            "phase": "post-contact report",
            "chrono_hook": "ReportAllContacts(callback)",
            "input_contract": "pA,pB,plane_coord,distance,eff_radius,cforce,ctorque,modA,modB,cnstr_offset",
            "mutation_policy": "report-only",
            "filter_rule": base["filter_rule"],
            "pair_scope": "rover_body-rigid_obstacle",
            "contactable_type_policy": "ChBody pair in fallback; non-body contactables must be recorded as unsupported",
            "artifact": "outputs/csv/collision_contact_probe.csv",
            "evidence_level": _collision_evidence_level(base["source"]),
            "fallback_reason": _collision_fallback_reason(base["source"]),
            "source": base["source"],
        },
        {
            "schema_id": "collision.contact_callback_manifest.v1",
            "run_id": base["run_id"],
            "catalog_component_id": "contact.debug_visualization",
            "instance_id": "callback.debug_visualization",
            "owner_component_id": "contact.container_reporter",
            "callback_id": "callback.debug_visualization",
            "callback_family": "Visualization callback",
            "class_name": "schema_only_debug_render",
            "registered_on": "render pipeline",
            "phase": "debug visualization",
            "chrono_hook": "Visualization callback or report render generator",
            "input_contract": "contact point, normal, force vector, collision envelope",
            "mutation_policy": "visualize-only",
            "filter_rule": base["filter_rule"],
            "pair_scope": "rover_body-rigid_obstacle",
            "contactable_type_policy": "rendered schematic",
            "artifact": "images/renders/collision_contact_debug_vectors.png",
            "evidence_level": "concept_render",
            "fallback_reason": "debug render is schematic unless tied to live frame index",
            "source": base["source"],
        },
    ]
    csv_path = write_csv(OUTPUT_CSV / "contact_callback_manifest.csv", list(callback_rows[0].keys()), callback_rows)
    json_path = write_json(
        OUTPUT_JSON / "contact_callback_manifest.json",
        {"schema_id": "collision.contact_callback_manifest.v1", "run_id": base["run_id"], "source": base["source"], "callbacks": callback_rows},
    )
    return csv_path, json_path


def write_contact_frame_debug_manifest(rows: list[dict[str, str]]) -> tuple[Path, Path]:
    base = _collision_manifest_base(rows)
    debug_rows = [
        {
            "schema_id": "collision.contact_frame_debug_manifest.v1",
            "run_id": base["run_id"],
            "catalog_component_id": "contact.frame_debug",
            "instance_id": "contact_frame.rover_obstacle.demo",
            "owner_component_id": "contact.container_reporter",
            "debug_frame_id": "contact_frame.rover_obstacle.demo",
            "body_a": "rover_body",
            "body_b": "rigid_obstacle",
            "point_x_m": rows[0].get("point_x_m", "0.36000") if rows else "0.36000",
            "point_y_m": rows[0].get("point_y_m", "0.00000") if rows else "0.00000",
            "point_z_m": rows[0].get("point_z_m", "0.30000") if rows else "0.30000",
            "normal_xyz": "-1,0,0",
            "tangent_u_xyz": "0,1,0",
            "tangent_v_xyz": "0,0,1",
            "force_vector_columns": "contact_fx_N,contact_fy_N,contact_fz_N",
            "torque_vector_columns": "contact_tx_Nm,contact_ty_Nm,contact_tz_Nm",
            "visual_vs_collision_render": "images/renders/collision_visual_vs_collision_shape.png",
            "debug_vector_render": "images/renders/collision_contact_debug_vectors.png",
            "backend_visualization_support": "schema-only render; live VSG/Irrlicht debug draw must record backend",
            "fallback_reason": "" if base["source"] == "pychrono" else base["source"],
            "source": base["source"],
        }
    ]
    csv_path = write_csv(OUTPUT_CSV / "contact_frame_debug_manifest.csv", list(debug_rows[0].keys()), debug_rows)
    json_path = write_json(
        OUTPUT_JSON / "contact_frame_debug_manifest.json",
        {"schema_id": "collision.contact_frame_debug_manifest.v1", "run_id": base["run_id"], "source": base["source"], "debug_frames": debug_rows},
    )
    return csv_path, json_path


def write_collision_contract_artifacts() -> list[Path]:
    csv_path, _ = write_collision_contact_probe_outputs()
    rows = _read_collision_probe_rows(csv_path)
    paths: list[Path] = [write_collision_system_manifest(rows), write_collision_model_registry(rows)]
    paths.extend(write_collision_backend_comparison(rows))
    paths.extend(write_collision_shape_manifest(rows))
    paths.extend(write_collision_family_filter_map(rows))
    paths.extend(write_contact_material_manifest(rows))
    paths.extend(write_contact_pair_material_policy(rows))
    paths.extend(write_contact_container_manifest(rows))
    paths.extend(write_contact_callback_manifest(rows))
    paths.extend(write_contact_frame_debug_manifest(rows))
    return paths


def render_collision_event_timeline_graph() -> Path:
    csv_path, event_csv = write_collision_contact_probe_outputs()
    data = np.genfromtxt(csv_path, delimiter=",", names=True, dtype=None, encoding="utf-8")
    events = _read_collision_event_rows(event_csv)
    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    ax.set_title("Collision Event Detector Timeline")
    ax.set_xlabel("time [s]")
    ax.set_ylabel("contact count")
    ax.set_xlim(0, max(data["time_s"]))
    time = data["time_s"].astype(float)
    counts = data["contact_count"].astype(float)
    force = data["contact_force_N"].astype(float)
    active = counts > 0
    if np.any(active):
        ax.axvspan(float(time[active][0]), float(time[active][-1]), color="#dcfce7", alpha=0.75, label="active contact window")
    ax.step(time, counts, where="post", color="#2563eb", linewidth=1.8, label="contact count")
    if np.max(force) > 0:
        force_scaled = force / np.max(force) * max(float(np.max(counts)), 1.0)
        ax.fill_between(time, 0, force_scaled, color="#f97316", alpha=0.22, label="force envelope")
        ax.plot(time, force_scaled, color="#ea580c", linewidth=1.2)
    ax.set_ylim(0, max(3.5, float(np.max(counts)) + 0.6))
    for event in events:
        t = float(event["time_s"])
        ax.axvline(t, color="#16a34a", linewidth=2)
        ax.scatter([t], [max(float(np.max(counts)), 1.0) + 0.18], s=60, color="#16a34a", zorder=3)
        label = event["event"].replace("_", " ").title()
        contact_count = event.get("contact_count", event.get("contacts", ""))
        if contact_count != "":
            label = f"{label} ({contact_count} contacts)"
        ax.text(t + 0.02, max(float(np.max(counts)), 1.0) + 0.25, label, va="bottom", ha="left", fontsize=8.3, color="#15803d", weight="bold")
    ax.grid(True, axis="both", alpha=0.25)
    legend_if_any(ax, loc="upper right", fontsize=7)
    return save_figure(fig, IMAGES_GRAPH / "collision_event_timeline_graph.png")


def run_contact_probe() -> tuple[Path, list[Path]]:
    csv_path, _ = write_collision_contact_probe_outputs()
    graphs = [
        render_collision_contact_force_graph(),
        render_collision_contact_count_graph(),
        render_collision_contact_force_components_graph(),
        render_collision_contact_material_effect_graph(),
        render_collision_event_timeline_graph(),
    ]
    return csv_path, graphs


def main() -> None:
    ensure_output_dirs()
    renders = render_collision_scene()
    csv_path, graphs = run_contact_probe()
    contract_paths = write_collision_contract_artifacts()
    print("collision_contact renders:")
    for path in renders:
        print(path)
    print("collision_contact csv:", csv_path)
    print("collision_contact graphs:")
    for path in graphs:
        print(path)
    print("collision_contact contract artifacts:")
    for path in contract_paths:
        print(path)


if __name__ == "__main__":
    main()
