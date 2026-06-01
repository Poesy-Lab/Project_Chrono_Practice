from __future__ import annotations

import math
import os
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, Polygon, Rectangle

sys.path.append(str(Path(__file__).resolve().parents[1] / "common"))

from component_utils import (  # noqa: E402
    IMAGES_GRAPH,
    IMAGES_RENDER,
    OUTPUT_CSV,
    OUTPUT_JSON,
    add_callout_3d,
    add_box,
    add_cylinder_y,
    ensure_output_dirs,
    legend_if_any,
    save_figure,
    set_axes_equal,
    try_import_chrono,
    vec_xyz,
    write_csv,
    write_json,
)
from vsg_component_render import (  # noqa: E402
    add_box as vsg_add_box,
    add_cylinder_y as vsg_add_cylinder_y,
    add_sphere as vsg_add_sphere,
    render_vsg_scene,
)
from generate_data_visualization_artifact_catalog_render import render_data_visualization_artifact_catalog  # noqa: E402
from generate_data_visualization_sensor_pipeline_catalog_render import render_data_visualization_sensor_pipeline_catalog  # noqa: E402


def render_visualization_components() -> list[Path]:
    paths = []
    output = IMAGES_RENDER / "data_visualization_sensor_components.png"

    def leader(ax, text, xytext, xy, *, color, ha="center"):
        ax.annotate(
            text,
            xy=xy,
            xytext=xytext,
            ha=ha,
            va="center",
            fontsize=9.0,
            color=color,
            bbox={"boxstyle": "round,pad=0.20", "facecolor": "white", "edgecolor": color, "linewidth": 1.0},
            arrowprops={"arrowstyle": "-", "color": color, "linewidth": 1.1, "shrinkA": 2, "shrinkB": 2},
            zorder=20,
        )

    def arrow(ax, start, end, *, color, width=1.6, style="-|>"):
        ax.add_patch(
            FancyArrowPatch(
                start,
                end,
                arrowstyle=style,
                mutation_scale=13,
                linewidth=width,
                color=color,
                shrinkA=0,
                shrinkB=0,
                zorder=9,
            )
        )

    fig, ax = plt.subplots(figsize=(9.8, 6.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.2)
    ax.axis("off")
    ax.set_aspect("equal")

    ax.text(5.0, 5.86, "Sensor layout verification component", ha="center", va="center", fontsize=13.2, weight="bold", color="#111827")
    ax.text(5.0, 5.55, "Mount pose, sensor origin, local frame, and artifact capture intent must point to the same chassis body.", ha="center", va="center", fontsize=8.2, color="#475569")

    ax.add_patch(Rectangle((0.62, 0.54), 8.86, 0.34, facecolor="#d1d5db", edgecolor="#64748b", linewidth=1.0, zorder=1))

    body_xy = (3.02, 2.25)
    body_size = (3.50, 1.18)
    roof_y = body_xy[1] + body_size[1]
    body_center = (body_xy[0] + body_size[0] / 2, body_xy[1] + body_size[1] / 2)
    chassis_face = "#2563eb"
    ax.add_patch(Rectangle(body_xy, *body_size, facecolor="#3b82f6", edgecolor="#1d4ed8", linewidth=2.0, alpha=0.92, zorder=4))
    ax.add_patch(Polygon([(3.55, roof_y), (5.88, roof_y), (5.48, 3.86), (3.95, 3.86)], facecolor="#60a5fa", edgecolor="#1d4ed8", linewidth=1.6, zorder=5))
    ax.text(body_center[0], body_center[1] - 0.05, "logged chassis body", ha="center", va="center", fontsize=9.4, color="#eff6ff", weight="bold", zorder=7)

    for wx, wy in [(3.42, 2.08), (5.95, 2.08), (3.42, 3.56), (5.95, 3.56)]:
        ax.add_patch(Circle((wx, wy), 0.31, facecolor="#111827", edgecolor="#020617", linewidth=1.1, zorder=6))
        ax.add_patch(Circle((wx, wy), 0.11, facecolor="#e5e7eb", edgecolor="#475569", linewidth=0.7, zorder=7))

    gps = (4.62, 3.86)
    lidar = (5.50, 3.86)
    camera = (1.56, 4.38)
    camera_target = (3.35, 2.86)

    ax.add_patch(Circle(gps, 0.115, facecolor="#16a34a", edgecolor="#166534", linewidth=1.1, zorder=10))
    ax.add_patch(Circle(lidar, 0.105, facecolor="#f59e0b", edgecolor="#92400e", linewidth=1.1, zorder=10))
    ax.add_patch(Rectangle((camera[0] - 0.20, camera[1] - 0.12), 0.34, 0.24, facecolor="#fecaca", edgecolor="#991b1b", linewidth=1.2, zorder=10))
    ax.add_patch(Polygon([(camera[0] + 0.14, camera[1] - 0.08), (camera[0] + 0.42, camera[1] - 0.20), (camera[0] + 0.42, camera[1] + 0.20), (camera[0] + 0.14, camera[1] + 0.08)], facecolor="#fca5a5", edgecolor="#991b1b", linewidth=1.1, zorder=10))
    ax.plot([camera[0] + 0.42, camera_target[0]], [camera[1], camera_target[1]], color="#dc2626", linewidth=2.1, linestyle="--", zorder=8)
    ax.add_patch(Circle(camera, 0.055, facecolor="#dc2626", edgecolor="#991b1b", linewidth=0.8, zorder=11))

    ray_ends = [(8.04, 3.18), (8.08, 3.48), (7.96, 3.78), (7.70, 4.05), (7.30, 4.28), (6.90, 4.44)]
    for end in ray_ends:
        ax.plot([lidar[0], end[0]], [lidar[1], end[1]], color="#f59e0b", linewidth=2.0, alpha=0.80, zorder=8)

    arrow(ax, gps, (5.06, 3.86), color="#1d4ed8", width=1.7)
    ax.text(5.12, 3.70, "x forward", ha="left", va="center", fontsize=7.7, color="#1d4ed8", weight="bold", zorder=12)
    arrow(ax, gps, (4.62, 4.52), color="#16a34a", width=1.7)
    ax.text(4.70, 4.55, "z up", ha="left", va="center", fontsize=7.7, color="#15803d", weight="bold", zorder=12)

    leader(ax, "External render\ncamera", (1.04, 5.08), camera, color="#991b1b", ha="left")
    leader(ax, "Dashed view line\nterminates on chassis", (1.12, 1.58), camera_target, color="#dc2626", ha="left")
    leader(ax, "GPS/IMU puck\non chassis roof", (3.60, 4.92), gps, color="#15803d")
    leader(ax, "Local sensor frame\nx forward / z up", (5.72, 5.02), gps, color="#1d4ed8", ha="left")
    leader(ax, "LiDAR origin", (6.92, 4.82), lidar, color="#b45309", ha="left")
    leader(ax, "One LiDAR ray", (8.76, 4.12), ray_ends[3], color="#b45309", ha="right")
    leader(ax, "Logged body", (8.24, 2.42), (body_xy[0] + body_size[0], body_center[1]), color=chassis_face, ha="right")

    ax.text(
        5.0,
        0.18,
        "This render verifies sensor placement only; module-backed evidence still requires a sensor manifest, frame/cloud files, timestamps, and checksums.",
        ha="center",
        va="center",
        fontsize=8.0,
        color="#475569",
    )
    paths.append(save_figure(fig, output))
    return paths


def write_state_and_control_logs() -> tuple[Path, Path]:
    chrono, error = try_import_chrono()
    state_rows = []
    control_rows = []
    run_id = "data_visualization_component_demo"
    scenario_id = "logger_schema_v1"

    if chrono is not None:
        system = chrono.ChSystemNSC()
        system.SetGravitationalAcceleration(chrono.ChVector3d(0, 0, -9.81))
        material = chrono.ChContactMaterialNSC()
        material.SetFriction(0.5)
        ground = chrono.ChBodyEasyBox(8, 4, 0.1, 1000, True, True, material)
        ground.SetFixed(True)
        ground.SetPos(chrono.ChVector3d(0, 0, -0.05))
        rover = chrono.ChBodyEasyBox(0.8, 0.5, 0.25, 300, True, True, material)
        rover.SetPos(chrono.ChVector3d(-2.5, 0, 0.25))
        system.AddBody(ground)
        system.AddBody(rover)
        step_index = 0
        while system.GetChTime() <= 3.0:
            t = system.GetChTime()
            throttle = 0.45 + 0.25 * math.sin(2.2 * t)
            steering = 0.28 * math.sin(1.4 * t)
            rover.SetPosDt(chrono.ChVector3d(0.25 + 0.9 * throttle, 0.18 * steering, 0))
            pos = rover.GetPos()
            vel = rover.GetPosDt()
            px, py, pz = vec_xyz(pos)
            vx, vy, vz = vec_xyz(vel)
            state_rows.append(
                {
                    "run_id": run_id,
                    "schema_id": "data.state_log.v1",
                    "scenario_id": scenario_id,
                    "time_s": f"{t:.3f}",
                    "step_index": step_index,
                    "component_id": "vehicle.chassis",
                    "body_name": "component_demo_rover",
                    "body_role": "logged_chassis",
                    "x_m": f"{px:.5f}",
                    "y_m": f"{py:.5f}",
                    "z_m": f"{pz:.5f}",
                    "vx_mps": f"{vx:.5f}",
                    "vy_mps": f"{vy:.5f}",
                    "vz_mps": f"{vz:.5f}",
                    "roll_rad": "0.00000",
                    "pitch_rad": "0.00000",
                    "yaw_rad": "0.00000",
                    "contact_force_N": "0.00000",
                    "source": "pychrono",
                }
            )
            control_rows.append(
                {
                    "run_id": run_id,
                    "schema_id": "data.control_log.v1",
                    "scenario_id": scenario_id,
                    "time_s": f"{t:.3f}",
                    "step_index": step_index,
                    "component_id": "core.function_input",
                    "catalog_component_id": "core.function_input",
                    "controller_id": "driver.controller",
                    "target_component_id": "vehicle.drive",
                    "actuator_instance_id": "actuator.drive_motor.demo",
                    "ownership_role": "command_owner_with_physical_target",
                    "command_type": "normalized_driver_inputs",
                    "command_source": "analytic_driver_profile",
                    "throttle": f"{throttle:.5f}",
                    "brake": "0.00000",
                    "steering": f"{steering:.5f}",
                    "drive_torque_Nm": f"{120 * throttle:.5f}",
                    "wheel_speed_radps": f"{8.0 + 5.0 * throttle:.5f}",
                    "source": "pychrono",
                }
            )
            system.DoStepDynamics(0.02)
            step_index += 1
    else:
        for step_index, t in enumerate(np.arange(0, 3.02, 0.02)):
            throttle = 0.45 + 0.25 * math.sin(2.2 * t)
            steering = 0.28 * math.sin(1.4 * t)
            state_rows.append(
                {
                    "run_id": run_id,
                    "schema_id": "data.state_log.v1",
                    "scenario_id": scenario_id,
                    "time_s": f"{t:.3f}",
                    "step_index": step_index,
                    "component_id": "vehicle.chassis",
                    "body_name": "component_demo_rover",
                    "body_role": "logged_chassis",
                    "x_m": f"{-2.5 + 0.35 * t * t:.5f}",
                    "y_m": f"{0.12 * math.sin(1.1 * t):.5f}",
                    "z_m": "0.25000",
                    "vx_mps": f"{0.7 * t:.5f}",
                    "vy_mps": f"{0.132 * math.cos(1.1 * t):.5f}",
                    "vz_mps": "0.00000",
                    "roll_rad": "0.00000",
                    "pitch_rad": "0.00000",
                    "yaw_rad": f"{0.1 * steering:.5f}",
                    "contact_force_N": "0.00000",
                    "source": f"fallback_{error}",
                }
            )
            control_rows.append(
                {
                    "run_id": run_id,
                    "schema_id": "data.control_log.v1",
                    "scenario_id": scenario_id,
                    "time_s": f"{t:.3f}",
                    "step_index": step_index,
                    "component_id": "core.function_input",
                    "catalog_component_id": "core.function_input",
                    "controller_id": "driver.controller",
                    "target_component_id": "vehicle.drive",
                    "actuator_instance_id": "actuator.drive_motor.demo",
                    "ownership_role": "command_owner_with_physical_target",
                    "command_type": "normalized_driver_inputs",
                    "command_source": "analytic_driver_profile",
                    "throttle": f"{throttle:.5f}",
                    "brake": "0.00000",
                    "steering": f"{steering:.5f}",
                    "drive_torque_Nm": f"{120 * throttle:.5f}",
                    "wheel_speed_radps": f"{8.0 + 5.0 * throttle:.5f}",
                    "source": f"fallback_{error}",
                }
            )

    state_csv = write_csv(
        OUTPUT_CSV / "data_visualization_state_log.csv",
        [
            "run_id",
            "schema_id",
            "scenario_id",
            "time_s",
            "step_index",
            "component_id",
            "body_name",
            "body_role",
            "x_m",
            "y_m",
            "z_m",
            "vx_mps",
            "vy_mps",
            "vz_mps",
            "roll_rad",
            "pitch_rad",
            "yaw_rad",
            "contact_force_N",
            "source",
        ],
        state_rows,
    )
    control_csv = write_csv(
        OUTPUT_CSV / "data_visualization_control_log.csv",
        [
            "run_id",
            "schema_id",
            "scenario_id",
            "time_s",
            "step_index",
            "component_id",
            "catalog_component_id",
            "controller_id",
            "target_component_id",
            "actuator_instance_id",
            "ownership_role",
            "command_type",
            "command_source",
            "throttle",
            "brake",
            "steering",
            "drive_torque_Nm",
            "wheel_speed_radps",
            "source",
        ],
        control_rows,
    )

    return state_csv, control_csv


def _sensor_schema_source() -> tuple[str, bool, str]:
    summary = _sensor_capability_summary()
    if summary["pychrono_sensor_available"]:
        return "fallback_sensor_schema_only_sensor_module_not_executed", True, "not_executed"
    if summary["pychrono_available"]:
        return "fallback_sensor_schema_only_pychrono_sensor_unavailable", False, "pychrono_sensor_unavailable"
    return "fallback_sensor_schema_only_pychrono_unavailable", False, "pychrono_unavailable"


def _project_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _probe_pychrono_modules(build_root: Path | None = None) -> dict[str, str]:
    env = os.environ.copy()
    if build_root is not None:
        env["PYTHONPATH"] = str(build_root / "bin") + os.pathsep + env.get("PYTHONPATH", "")
        env["LD_LIBRARY_PATH"] = str(build_root / "lib") + os.pathsep + env.get("LD_LIBRARY_PATH", "")
    code = (
        "import importlib, json\n"
        "mods=['pychrono','pychrono.sensor','pychrono.vsg3d']\n"
        "out={}\n"
        "for mod in mods:\n"
        "    try:\n"
        "        module=importlib.import_module(mod)\n"
        "        out[mod]={'available': True, 'path': getattr(module, '__file__', '')}\n"
        "    except Exception as exc:\n"
        "        out[mod]={'available': False, 'error': type(exc).__name__ + ': ' + str(exc)}\n"
        "print(json.dumps(out, sort_keys=True))\n"
    )
    result = subprocess.run([sys.executable, "-c", code], cwd=_project_root(), env=env, text=True, capture_output=True, timeout=10, check=False)
    if result.returncode != 0:
        return {
            "pychrono_available": "false",
            "pychrono_sensor_available": "false",
            "pychrono_vsg3d_available": "false",
            "pychrono_path": "",
            "sensor_path": "",
            "vsg3d_path": "",
            "error": (result.stderr.strip() or result.stdout.strip() or f"returncode={result.returncode}")[:500],
        }
    import json

    payload = json.loads(result.stdout)
    core = payload.get("pychrono", {})
    sensor = payload.get("pychrono.sensor", {})
    vsg3d = payload.get("pychrono.vsg3d", {})
    return {
        "pychrono_available": str(bool(core.get("available"))).lower(),
        "pychrono_sensor_available": str(bool(sensor.get("available"))).lower(),
        "pychrono_vsg3d_available": str(bool(vsg3d.get("available"))).lower(),
        "pychrono_path": str(core.get("path", "")),
        "sensor_path": str(sensor.get("path", "")),
        "vsg3d_path": str(vsg3d.get("path", "")),
        "error": str(sensor.get("error") or core.get("error") or ""),
    }


@lru_cache(maxsize=1)
def _sensor_capability_rows_cached() -> tuple[tuple[tuple[str, str], ...], ...]:
    rows: list[dict[str, str]] = []
    host = _probe_pychrono_modules(None)
    rows.append(
        {
            "schema_id": "sensor.module_capability_manifest.v1",
            "run_id": "data_visualization_component_demo",
            "component_id": "sensor.manager",
            "capability_id": "host_python_pychrono_sensor",
            "check_scope": "host_python",
            "build_root": "",
            "pythonpath_entry": "",
            "pychrono_available": host["pychrono_available"],
            "pychrono_sensor_available": host["pychrono_sensor_available"],
            "pychrono_vsg3d_available": host["pychrono_vsg3d_available"],
            "pychrono_path": host["pychrono_path"],
            "sensor_path": host["sensor_path"],
            "vsg3d_path": host["vsg3d_path"],
            "live_sensor_output_allowed": str(host["pychrono_sensor_available"] == "true").lower(),
            "blocker": "" if host["pychrono_sensor_available"] == "true" else host["error"],
        }
    )
    for name in ("chrono_build_cuda129_sm120", "chrono_build_vsg", "chrono_build"):
        build_root = _project_root() / name
        if not build_root.exists():
            continue
        probe = _probe_pychrono_modules(build_root)
        rows.append(
            {
                "schema_id": "sensor.module_capability_manifest.v1",
                "run_id": "data_visualization_component_demo",
                "component_id": "sensor.manager",
                "capability_id": f"{name}_pychrono_sensor",
                "check_scope": "candidate_build",
                "build_root": name,
                "pythonpath_entry": (build_root / "bin").relative_to(_project_root()).as_posix(),
                "pychrono_available": probe["pychrono_available"],
                "pychrono_sensor_available": probe["pychrono_sensor_available"],
                "pychrono_vsg3d_available": probe["pychrono_vsg3d_available"],
                "pychrono_path": probe["pychrono_path"],
                "sensor_path": probe["sensor_path"],
                "vsg3d_path": probe["vsg3d_path"],
                "live_sensor_output_allowed": str(probe["pychrono_sensor_available"] == "true").lower(),
                "blocker": "" if probe["pychrono_sensor_available"] == "true" else probe["error"],
            }
        )
    return tuple(tuple(sorted(row.items())) for row in rows)


def _sensor_capability_rows() -> list[dict[str, str]]:
    return [dict(row) for row in _sensor_capability_rows_cached()]


def _sensor_capability_summary() -> dict[str, bool | str]:
    rows = _sensor_capability_rows()
    pychrono_available = any(row["pychrono_available"] == "true" for row in rows)
    sensor_available = any(row["pychrono_sensor_available"] == "true" for row in rows)
    source = "pychrono_sensor_available" if sensor_available else ("fallback_sensor_schema_only_pychrono_sensor_unavailable" if pychrono_available else "fallback_sensor_schema_only_pychrono_unavailable")
    blocker = "" if sensor_available else "; ".join(row["blocker"] for row in rows if row["blocker"])[:700]
    return {
        "pychrono_available": pychrono_available,
        "pychrono_sensor_available": sensor_available,
        "source": source,
        "blocker": blocker,
        "row_count": len(rows),
    }


def write_sensor_module_capability_manifest() -> Path:
    import json

    rows = _sensor_capability_rows()
    summary = _sensor_capability_summary()
    return write_json(
        OUTPUT_JSON / "sensor_module_capability_manifest.json",
        {
            "schema_id": "sensor.module_capability_manifest.v1",
            "run_id": "data_visualization_component_demo",
            "source": summary["source"],
            "sensor_module_available": summary["pychrono_sensor_available"],
            "pychrono_available": summary["pychrono_available"],
            "live_sensor_output_allowed": summary["pychrono_sensor_available"],
            "live_output_blocker": summary["blocker"],
            "capabilities": rows,
        },
    )


def _sensor_specs() -> list[dict[str, str]]:
    return [
        {
            "sensor_name": "front_rgb_camera",
            "component_id": "sensor.output_writer",
            "catalog_component_id": "sensor.output_writer",
            "layout_component_id": "sensor.layout",
            "instance_id": "sensor.camera.front_rgb",
            "sensor_type": "ChCameraSensor",
            "parent_body": "component_demo_rover",
            "parent_component_id": "vehicle.chassis",
            "parent_frame": "chassis.payload_mount",
            "sensor_frame": "sensor_front_rgb_x_forward_y_left_z_up",
            "mount_x_m": "0.420",
            "mount_y_m": "0.000",
            "mount_z_m": "0.720",
            "mount_qw": "1.00000",
            "mount_qx": "0.00000",
            "mount_qy": "0.00000",
            "mount_qz": "0.00000",
            "update_rate_hz": "10.0",
            "lag_s": "0.020",
            "collection_window_s": "0.010",
            "width_px": "1280",
            "height_px": "720",
            "horizontal_samples": "",
            "vertical_channels": "",
            "points_per_frame": "",
            "hfov_rad": "1.396",
            "vfov_rad": "",
            "max_range_m": "",
            "raw_buffer_format": "RGBA8",
            "output_path_pattern": "outputs/raw/sensors/front_rgb/frame_%06d.png",
            "filter_chain_id": "front_rgb_camera_chain",
        },
        {
            "sensor_name": "roof_lidar_xyzi",
            "component_id": "sensor.output_writer",
            "catalog_component_id": "sensor.output_writer",
            "layout_component_id": "sensor.layout",
            "instance_id": "sensor.lidar.roof_xyzi",
            "sensor_type": "ChLidarSensor",
            "parent_body": "component_demo_rover",
            "parent_component_id": "vehicle.chassis",
            "parent_frame": "chassis.sensor_mast",
            "sensor_frame": "sensor_lidar_x_forward_y_left_z_up",
            "mount_x_m": "0.180",
            "mount_y_m": "0.000",
            "mount_z_m": "0.860",
            "mount_qw": "1.00000",
            "mount_qx": "0.00000",
            "mount_qy": "0.00000",
            "mount_qz": "0.00000",
            "update_rate_hz": "10.0",
            "lag_s": "0.015",
            "collection_window_s": "0.020",
            "width_px": "",
            "height_px": "",
            "horizontal_samples": "2048",
            "vertical_channels": "32",
            "points_per_frame": "65536",
            "hfov_rad": "6.283",
            "vfov_rad": "0.524",
            "max_range_m": "80.0",
            "raw_buffer_format": "XYZI",
            "output_path_pattern": "outputs/raw/sensors/lidar_xyzi/cloud_%06d.csv",
            "filter_chain_id": "roof_lidar_xyzi_chain",
        },
        {
            "sensor_name": "roof_gps",
            "component_id": "sensor.output_writer",
            "catalog_component_id": "sensor.output_writer",
            "layout_component_id": "sensor.layout",
            "instance_id": "sensor.gps.roof",
            "sensor_type": "ChGPSSensor",
            "parent_body": "component_demo_rover",
            "parent_component_id": "vehicle.chassis",
            "parent_frame": "chassis.sensor_mast",
            "sensor_frame": "gps_x_east_y_north_z_up",
            "mount_x_m": "0.050",
            "mount_y_m": "0.000",
            "mount_z_m": "0.920",
            "mount_qw": "1.00000",
            "mount_qx": "0.00000",
            "mount_qy": "0.00000",
            "mount_qz": "0.00000",
            "update_rate_hz": "20.0",
            "lag_s": "0.005",
            "collection_window_s": "0.000",
            "width_px": "",
            "height_px": "",
            "horizontal_samples": "",
            "vertical_channels": "",
            "points_per_frame": "",
            "hfov_rad": "",
            "vfov_rad": "",
            "max_range_m": "",
            "raw_buffer_format": "GPS",
            "output_path_pattern": "outputs/raw/sensors/gps/gps_log.csv",
            "filter_chain_id": "roof_gps_chain",
        },
        {
            "sensor_name": "roof_imu",
            "component_id": "sensor.output_writer",
            "catalog_component_id": "sensor.output_writer",
            "layout_component_id": "sensor.layout",
            "instance_id": "sensor.imu.roof",
            "sensor_type": "accelerometer_gyroscope_magnetometer",
            "parent_body": "component_demo_rover",
            "parent_component_id": "vehicle.chassis",
            "parent_frame": "chassis.sensor_mast",
            "sensor_frame": "imu_x_forward_y_left_z_up",
            "mount_x_m": "0.040",
            "mount_y_m": "0.000",
            "mount_z_m": "0.900",
            "mount_qw": "1.00000",
            "mount_qx": "0.00000",
            "mount_qy": "0.00000",
            "mount_qz": "0.00000",
            "update_rate_hz": "100.0",
            "lag_s": "0.002",
            "collection_window_s": "0.000",
            "width_px": "",
            "height_px": "",
            "horizontal_samples": "",
            "vertical_channels": "",
            "points_per_frame": "",
            "hfov_rad": "",
            "vfov_rad": "",
            "max_range_m": "",
            "raw_buffer_format": "accel_gyro_magnet",
            "output_path_pattern": "outputs/raw/sensors/imu/imu_log.csv",
            "filter_chain_id": "roof_imu_chain",
        },
    ]


def _sensor_drop_reason(sensor_module_available: bool) -> str:
    return "" if sensor_module_available else "sensor_module_unavailable_schema_only"


def write_sensor_manifest_artifacts() -> tuple[Path, Path]:
    source, sensor_module_available, _ = _sensor_schema_source()
    rows = []
    for spec in _sensor_specs():
        row = {
            "schema_id": "sensor.output_manifest.v1",
            "run_id": "data_visualization_component_demo",
            "sequence_id": "sensor_layout_schema_v1",
            "frame_index": "0",
            "time_s": "0.000",
            "sensor_name": spec["sensor_name"],
            "sensor_type": spec["sensor_type"],
            "parent_body": spec["parent_body"],
            "component_id": spec["component_id"],
            "catalog_component_id": spec["catalog_component_id"],
            "layout_component_id": spec["layout_component_id"],
            "instance_id": spec["instance_id"],
            "parent_component_id": spec["parent_component_id"],
            "parent_frame": spec["parent_frame"],
            "sensor_frame": spec["sensor_frame"],
            "world_pose_frame": "Chrono world: X forward, Y left, Z up",
            "parent_x_m": spec["mount_x_m"],
            "parent_y_m": spec["mount_y_m"],
            "parent_z_m": spec["mount_z_m"],
            "parent_qw": spec["mount_qw"],
            "parent_qx": spec["mount_qx"],
            "parent_qy": spec["mount_qy"],
            "parent_qz": spec["mount_qz"],
            "world_x_m": spec["mount_x_m"],
            "world_y_m": spec["mount_y_m"],
            "world_z_m": spec["mount_z_m"],
            "world_qw": spec["mount_qw"],
            "world_qx": spec["mount_qx"],
            "world_qy": spec["mount_qy"],
            "world_qz": spec["mount_qz"],
            "update_rate_hz": spec["update_rate_hz"],
            "lag_s": spec["lag_s"],
            "collection_window_s": spec["collection_window_s"],
            "filter_chain_id": spec["filter_chain_id"],
            "raw_buffer_format": spec["raw_buffer_format"],
            "output_path_pattern": spec["output_path_pattern"],
            "artifact_path": "",
            "artifact_checksum": "",
            "available": "false",
            "dropped_frame": "true",
            "drop_reason": _sensor_drop_reason(sensor_module_available),
            "source": source,
        }
        rows.append(row)
    fieldnames = list(rows[0].keys())
    csv_path = write_csv(OUTPUT_CSV / "sensor_manifest.csv", fieldnames, rows)
    json_path = write_json(
        OUTPUT_JSON / "sensor_manifest.json",
        {
            "schema_id": "sensor.output_manifest.v1",
            "run_id": "data_visualization_component_demo",
            "source": source,
            "sensor_module_available": sensor_module_available,
            "sensors": rows,
        },
    )
    return csv_path, json_path


def write_sensor_timing_schedule_artifacts() -> tuple[Path, Path]:
    source, sensor_module_available, _ = _sensor_schema_source()
    rows = []
    dynamics_dt_s = 0.02
    for spec in _sensor_specs():
        update_rate = float(spec["update_rate_hz"])
        lag_s = float(spec["lag_s"])
        collection_window_s = float(spec["collection_window_s"])
        for frame_index in range(6):
            requested_time = frame_index / update_rate
            collection_start = max(0.0, requested_time - 0.5 * collection_window_s)
            collection_end = requested_time + 0.5 * collection_window_s
            rows.append(
                {
                    "schema_id": "sensor.timing_schedule.v1",
                    "run_id": "data_visualization_component_demo",
                    "sequence_id": "sensor_layout_schema_v1",
                    "component_id": spec["component_id"],
                    "catalog_component_id": spec["catalog_component_id"],
                    "layout_component_id": spec["layout_component_id"],
                    "instance_id": spec["instance_id"],
                    "owner_component_id": spec["parent_component_id"],
                    "dynamics_dt_s": f"{dynamics_dt_s:.5f}",
                    "dynamics_step_index": str(round(requested_time / dynamics_dt_s)),
                    "sensor_name": spec["sensor_name"],
                    "sensor_type": spec["sensor_type"],
                    "sensor_update_rate_hz": spec["update_rate_hz"],
                    "frame_index": str(frame_index),
                    "num_launches": str(frame_index + 1),
                    "frame_requested_time_s": f"{requested_time:.5f}",
                    "collection_start_s": f"{collection_start:.5f}",
                    "collection_end_s": f"{collection_end:.5f}",
                    "lag_s": spec["lag_s"],
                    "frame_ready_time_s": f"{requested_time + lag_s:.5f}",
                    "engine_id": "schema_only_engine_0",
                    "device_id": "schema_only_device_0",
                    "max_engines": "1",
                    "filter_chain_id": spec["filter_chain_id"],
                    "filter_list_locked": "true",
                    "dropped_frame": "true",
                    "drop_reason": _sensor_drop_reason(sensor_module_available),
                    "stale_buffer": "false",
                    "source": source,
                }
            )
    fieldnames = list(rows[0].keys())
    csv_path = write_csv(OUTPUT_CSV / "sensor_timing_schedule.csv", fieldnames, rows)
    json_path = write_json(
        OUTPUT_JSON / "sensor_timing_schedule.json",
        {
            "schema_id": "sensor.timing_schedule.v1",
            "run_id": "data_visualization_component_demo",
            "source": source,
            "sensor_module_available": sensor_module_available,
            "schedule": rows,
        },
    )
    return csv_path, json_path


def _filter_rows(source: str) -> list[dict[str, str]]:
    specs = {spec["sensor_name"]: spec for spec in _sensor_specs()}
    chains = [
        ("front_rgb_camera", "ChFilterRGBA8Access", "access", "RGBA8", "host_rgba8", "", "true", "", "", "false", "missing access buffer when Sensor module is unavailable"),
        ("front_rgb_camera", "ChFilterSave", "save", "RGBA8", "PNG", specs["front_rgb_camera"]["output_path_pattern"], "false", "", "", "false", "no file written in schema-only fallback"),
        ("front_rgb_camera", "ChFilterVisualize", "visualize", "RGBA8", "debug_window", "", "false", "", "", "true", "visualize-only filter is not report evidence"),
        ("roof_lidar_xyzi", "ChFilterDIAccess", "access", "depth_intensity", "host_depth_intensity", "", "true", "", "", "false", "missing access buffer when Sensor module is unavailable"),
        ("roof_lidar_xyzi", "ChFilterPCfromDepth", "convert", "depth_intensity", "XYZI", "", "false", "", "", "false", "conversion not executed in schema-only fallback"),
        ("roof_lidar_xyzi", "ChFilterXYZIAccess", "access", "XYZI", "host_xyzi", "", "true", "", "", "false", "missing point cloud access when Sensor module is unavailable"),
        ("roof_lidar_xyzi", "ChFilterSavePtCloud", "save", "XYZI", "point_cloud_csv", specs["roof_lidar_xyzi"]["output_path_pattern"], "false", "", "", "false", "no point cloud written in schema-only fallback"),
        ("roof_gps", "ChFilterGPSAccess", "access", "GPS", "host_gps", "", "true", "none", "", "false", "missing GPS access buffer when Sensor module is unavailable"),
        ("roof_imu", "ChFilterAccelAccess", "access", "accelerometer", "host_accel", "", "true", "none", "", "false", "missing accelerometer buffer when Sensor module is unavailable"),
        ("roof_imu", "ChFilterGyroAccess", "access", "gyroscope", "host_gyro", "", "true", "none", "", "false", "missing gyroscope buffer when Sensor module is unavailable"),
        ("roof_imu", "ChFilterMagnetAccess", "access", "magnetometer", "host_magnet", "", "true", "none", "", "false", "missing magnetometer buffer when Sensor module is unavailable"),
    ]
    rows = []
    per_chain_index: dict[str, int] = {}
    for sensor_name, filter_class, role, input_buffer, output_buffer, path_pattern, cpu_copy, noise_model, seed, visualize_only, failure_behavior in chains:
        spec = specs[sensor_name]
        chain_id = spec["filter_chain_id"]
        index = per_chain_index.get(chain_id, 0)
        per_chain_index[chain_id] = index + 1
        rows.append(
            {
                "schema_id": "sensor.filter_catalog.v1",
                "run_id": "data_visualization_component_demo",
                "component_id": spec["component_id"],
                "catalog_component_id": spec["catalog_component_id"],
                "layout_component_id": spec["layout_component_id"],
                "instance_id": spec["instance_id"],
                "owner_component_id": spec["parent_component_id"],
                "filter_chain_id": chain_id,
                "filter_index": str(index),
                "sensor_name": sensor_name,
                "sensor_type": spec["sensor_type"],
                "filter_class": filter_class,
                "filter_role": role,
                "input_buffer_type": input_buffer,
                "output_buffer_type": output_buffer,
                "output_path_pattern": path_pattern,
                "cpu_copy_required": cpu_copy,
                "noise_model": noise_model,
                "seed": seed,
                "parameters": "schema-only catalog row",
                "visualize_only": visualize_only,
                "failure_behavior": failure_behavior,
                "source": source,
            }
        )
    return rows


def write_sensor_filter_catalog_artifacts() -> tuple[Path, Path]:
    source, _, _ = _sensor_schema_source()
    rows = _filter_rows(source)
    fieldnames = list(rows[0].keys())
    csv_path = write_csv(OUTPUT_CSV / "sensor_filter_catalog.csv", fieldnames, rows)
    json_path = write_json(
        OUTPUT_JSON / "sensor_filter_catalog.json",
        {
            "schema_id": "sensor.filter_catalog.v1",
            "run_id": "data_visualization_component_demo",
            "source": source,
            "filters": rows,
        },
    )
    return csv_path, json_path


def write_sensor_scene_manifest() -> Path:
    source, sensor_module_available, sensor_status = _sensor_schema_source()
    capability_summary = _sensor_capability_summary()
    scene_components = [
        {
            "component_id": "sensor.manager",
            "catalog_component_id": "sensor.manager",
            "instance_id": "sensor.manager.schema_only",
            "component_type": "ChSensorManager",
            "sensor_module_available": sensor_module_available,
            "module_status": sensor_status,
            "compatible_simulation_domain": "core rigid body, Chrono::Vehicle, SCM terrain; FSI/CRM perception evidence must be explicitly gated",
            "device_list": [] if not sensor_module_available else ["default_sensor_device"],
            "max_engines": 1,
            "ray_recursions": 2,
            "scene_lights": ["ambient_key_light", "sun_directional_light"],
            "background_policy": "schema-only clear sky/background setting",
            "visual_asset_coverage": ["component_demo_rover", "terrain.core_ground", "sensor_mounts"],
            "update_order": "DoStepDynamics(dt) then ChSensorManager.Update() in live runs",
            "capability_manifest_path": "outputs/json/sensor_module_capability_manifest.json",
            "live_sensor_output_allowed": capability_summary["pychrono_sensor_available"],
            "live_output_blocker": capability_summary["blocker"],
            "fallback_policy": "available=false rows in sensor_manifest; no raw frames/clouds/logs are generated without Sensor module execution",
        }
    ]
    return write_json(
        OUTPUT_JSON / "sensor_scene_manifest.json",
        {
            "schema_id": "sensor.scene_manifest.v1",
            "run_id": "data_visualization_component_demo",
            "source": source,
            "sensor_module_available": sensor_module_available,
            "scene_components": scene_components,
            "sensors": _sensor_specs(),
        },
    )


def generate_sensor_schema_artifacts() -> list[Path]:
    capability_json = write_sensor_module_capability_manifest()
    sensor_csv, sensor_json = write_sensor_manifest_artifacts()
    timing_csv, timing_json = write_sensor_timing_schedule_artifacts()
    filter_csv, filter_json = write_sensor_filter_catalog_artifacts()
    scene_json = write_sensor_scene_manifest()
    return [capability_json, sensor_csv, sensor_json, timing_csv, timing_json, filter_csv, filter_json, scene_json]


def render_data_visualization_state_trajectory_graph() -> Path:
    state_csv, _ = write_state_and_control_logs()
    state = np.genfromtxt(state_csv, delimiter=",", names=True, dtype=None, encoding="utf-8")
    fig, (traj_ax, speed_ax) = plt.subplots(1, 2, figsize=(9.2, 4.5))
    traj_ax.plot(state["x_m"], state["y_m"], color="#2563eb", linewidth=2)
    traj_ax.scatter([state["x_m"][0]], [state["y_m"][0]], color="#16a34a", s=35, label="start")
    traj_ax.scatter([state["x_m"][-1]], [state["y_m"][-1]], color="#dc2626", s=35, label="end")
    traj_ax.set_title("Trajectory")
    traj_ax.set_xlabel("x [m]")
    traj_ax.set_ylabel("y [m]")
    traj_ax.grid(True, alpha=0.3)
    legend_if_any(traj_ax, loc="best", fontsize=8)
    speed = np.sqrt(state["vx_mps"] ** 2 + state["vy_mps"] ** 2 + state["vz_mps"] ** 2)
    speed_ax.plot(state["time_s"], speed, color="#0f766e", linewidth=2)
    speed_ax.set_title("Speed")
    speed_ax.set_xlabel("time [s]")
    speed_ax.set_ylabel("speed [m/s]")
    speed_ax.grid(True, alpha=0.3)
    fig.suptitle("State Logger Trajectory and Speed")
    return save_figure(fig, IMAGES_GRAPH / "data_visualization_state_trajectory.png")


def render_data_visualization_control_inputs_graph() -> Path:
    _, control_csv = write_state_and_control_logs()
    control = np.genfromtxt(control_csv, delimiter=",", names=True, dtype=None, encoding="utf-8")
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    ax.plot(control["time_s"], control["throttle"], color="#16a34a", linewidth=2, label="throttle")
    ax.plot(control["time_s"], control["brake"], color="#2563eb", linewidth=1.8, linestyle="--", label="brake")
    ax.plot(control["time_s"], control["steering"], color="#dc2626", linewidth=2, label="steering")
    ax.set_title("Control Logger Inputs")
    ax.set_xlabel("time [s]")
    ax.set_ylabel("normalized input")
    ax.grid(True, alpha=0.3)
    legend_if_any(ax)
    return save_figure(fig, IMAGES_GRAPH / "data_visualization_control_inputs.png")


def generate_state_and_control_logs() -> tuple[list[Path], list[Path]]:
    state_csv, control_csv = write_state_and_control_logs()
    graphs = [
        render_data_visualization_state_trajectory_graph(),
        render_data_visualization_control_inputs_graph(),
    ]
    return [state_csv, control_csv], graphs


def main() -> None:
    ensure_output_dirs()
    renders = render_visualization_components()
    renders.append(render_data_visualization_artifact_catalog())
    renders.append(render_data_visualization_sensor_pipeline_catalog())
    csv_paths, graphs = generate_state_and_control_logs()
    sensor_paths = generate_sensor_schema_artifacts()
    print("data_visualization renders:")
    for path in renders:
        print(path)
    print("data_visualization csv:")
    for path in csv_paths:
        print(path)
    print("data_visualization graphs:")
    for path in graphs:
        print(path)
    print("data_visualization sensor schema artifacts:")
    for path in sensor_paths:
        print(path)


if __name__ == "__main__":
    main()
