from __future__ import annotations

import csv
import hashlib
import json
import platform
import re
import shutil
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

sys.path.append(str(Path(__file__).resolve().parent))

from component_utils import OUTPUT_CSV, OUTPUT_JSON, OUTPUT_RAW, ROOT, ensure_output_dirs, try_import_chrono, write_csv, write_json  # noqa: E402


RUN_ID = "component_catalog_fallback_bundle"
MANIFEST_SCHEMA_ID = "component.artifact_manifest.v1"
RUN_METADATA_SCHEMA_ID = "component.run_metadata.v1"
README = ROOT / "README.md"
MANIFEST_CSV = OUTPUT_CSV / "artifact_manifest.csv"
MANIFEST_JSON = OUTPUT_JSON / "artifact_manifest.json"
RUN_METADATA = OUTPUT_JSON / "run_metadata.json"
LOGGER_TIMEBASE_CSV = OUTPUT_CSV / "logger_timebase_manifest.csv"
LOGGER_TIMEBASE_JSON = OUTPUT_JSON / "logger_timebase_manifest.json"
WRITER_BACKEND_CSV = OUTPUT_CSV / "writer_backend_manifest.csv"
WRITER_BACKEND_JSON = OUTPUT_JSON / "writer_backend_manifest.json"
RENDER_MANIFEST_CSV = OUTPUT_CSV / "render_manifest.csv"
RENDER_MANIFEST_JSON = OUTPUT_JSON / "render_manifest.json"
VISUAL_ASSET_MANIFEST_CSV = OUTPUT_CSV / "visual_asset_manifest.csv"
VISUAL_ASSET_MANIFEST_JSON = OUTPUT_JSON / "visual_asset_manifest.json"
CHRONO_OUTPUT_DATABASE_JSON = OUTPUT_JSON / "chrono_output_database_manifest.json"
CHECKPOINT_MANIFEST_CSV = OUTPUT_CSV / "checkpoint_manifest.csv"
CHECKPOINT_MANIFEST_JSON = OUTPUT_JSON / "checkpoint_manifest.json"
GNUPLOT_PLOT_MANIFEST_CSV = OUTPUT_CSV / "gnuplot_plot_manifest.csv"
GNUPLOT_PLOT_MANIFEST_JSON = OUTPUT_JSON / "gnuplot_plot_manifest.json"
OFFLINE_VISUAL_EXPORT_MANIFEST_CSV = OUTPUT_CSV / "offline_visual_export_manifest.csv"
OFFLINE_VISUAL_EXPORT_MANIFEST_JSON = OUTPUT_JSON / "offline_visual_export_manifest.json"
GNUPLOT_RAW_DIR = OUTPUT_RAW / "gnuplot"
FEA_MESH_MANIFEST_CSV = OUTPUT_CSV / "fea_mesh_manifest.csv"
FEA_MESH_MANIFEST_JSON = OUTPUT_JSON / "fea_mesh_manifest.json"
FEA_NODE_ELEMENT_COUNT_CSV = OUTPUT_CSV / "fea_node_element_count.csv"
MATERIAL_LAW_MANIFEST_JSON = OUTPUT_JSON / "material_law_manifest.json"
BOUNDARY_CONDITION_MAP_CSV = OUTPUT_CSV / "boundary_condition_map.csv"
BOUNDARY_CONDITION_MAP_JSON = OUTPUT_JSON / "boundary_condition_map.json"
MODE_FREQUENCY_TABLE_CSV = OUTPUT_CSV / "mode_frequency_table.csv"
MODAL_BASIS_MANIFEST_JSON = OUTPUT_JSON / "modal_basis_manifest.json"
MODEL_IMPORT_MANIFEST_JSON = OUTPUT_JSON / "model_import_manifest.json"
ASSET_MANIFEST_CSV = OUTPUT_CSV / "asset_manifest.csv"
ASSET_MANIFEST_JSON = OUTPUT_JSON / "asset_manifest.json"
CAD_SHAPE_MANIFEST_CSV = OUTPUT_CSV / "cad_shape_manifest.csv"
CAD_SHAPE_MANIFEST_JSON = OUTPUT_JSON / "cad_shape_manifest.json"
EXTERNAL_INTERFACE_MAP_CSV = OUTPUT_CSV / "external_interface_map.csv"
EXTERNAL_INTERFACE_MAP_JSON = OUTPUT_JSON / "external_interface_map.json"
SYNC_CONTRACT_JSON = OUTPUT_JSON / "sync_contract.json"
SYNC_EXCHANGE_LOG_CSV = OUTPUT_CSV / "sync_exchange_log.csv"
FMU_VARIABLE_MAP_CSV = OUTPUT_CSV / "fmu_variable_map.csv"
FMU_VARIABLE_MAP_JSON = OUTPUT_JSON / "fmu_variable_map.json"
ROS_TOPIC_HANDLER_MANIFEST_CSV = OUTPUT_CSV / "ros_topic_handler_manifest.csv"
ROS_TOPIC_HANDLER_MANIFEST_JSON = OUTPUT_JSON / "ros_topic_handler_manifest.json"
VEHICLE_COSIM_NODE_MANIFEST_JSON = OUTPUT_JSON / "vehicle_cosim_node_manifest.json"
SYNCHRONO_AGENT_MANIFEST_JSON = OUTPUT_JSON / "synchrono_agent_manifest.json"

CSV_PRODUCERS = {
    "outputs/csv/rover_vehicle_chassis_probe.csv": "code/rover_vehicle/generate_rover_vehicle_components.py",
    "outputs/csv/vehicle_axle_wheel_map.csv": "code/rover_vehicle/generate_rover_vehicle_components.py",
    "outputs/csv/vehicle_frame_hardpoint_map.csv": "code/rover_vehicle/generate_rover_vehicle_components.py",
    "outputs/csv/vehicle_subsystem_probe.csv": "code/rover_vehicle/generate_rover_vehicle_components.py",
    "outputs/json/vehicle_axle_wheel_map.json": "code/rover_vehicle/generate_rover_vehicle_components.py",
    "outputs/json/vehicle_frame_hardpoint_map.json": "code/rover_vehicle/generate_rover_vehicle_components.py",
    "outputs/json/vehicle_component_list.json": "code/rover_vehicle/generate_rover_vehicle_components.py",
    "outputs/json/vehicle_model_spec_manifest.json": "code/rover_vehicle/generate_rover_vehicle_components.py",
    "outputs/json/vehicle_subsystem_types.json": "code/rover_vehicle/generate_rover_vehicle_components.py",
    "outputs/json/vehicle_subsystem_output_policy.json": "code/rover_vehicle/generate_rover_vehicle_components.py",
    "outputs/csv/environment_terrain_height_friction_sinkage.csv": "code/environment_terrain/generate_environment_terrain_components.py",
    "outputs/csv/terrain_surface_probe.csv": "code/environment_terrain/generate_environment_terrain_components.py",
    "outputs/csv/terrain_query_probe.csv": "code/environment_terrain/generate_environment_terrain_components.py",
    "outputs/csv/environment_terrain_contact_probe.csv": "code/environment_terrain/generate_environment_terrain_components.py",
    "outputs/csv/terrain_patch_manifest.csv": "code/environment_terrain/generate_environment_terrain_components.py",
    "outputs/json/terrain_patch_manifest.json": "code/environment_terrain/generate_environment_terrain_components.py",
    "outputs/csv/terrain_material_region_map.csv": "code/environment_terrain/generate_environment_terrain_components.py",
    "outputs/json/terrain_material_region_map.json": "code/environment_terrain/generate_environment_terrain_components.py",
    "outputs/json/terrain_deformable_domain_manifest.json": "code/environment_terrain/generate_environment_terrain_components.py",
    "outputs/csv/scm_soil_profile_manifest.csv": "code/environment_terrain/generate_environment_terrain_components.py",
    "outputs/json/scm_soil_profile_manifest.json": "code/environment_terrain/generate_environment_terrain_components.py",
    "outputs/csv/collision_contact_probe.csv": "code/collision_contact/generate_collision_contact_components.py",
    "outputs/csv/collision_event_timeline.csv": "code/collision_contact/generate_collision_contact_components.py",
    "outputs/json/collision_system_manifest.json": "code/collision_contact/generate_collision_contact_components.py",
    "outputs/csv/collision_backend_comparison.csv": "code/collision_contact/generate_collision_contact_components.py",
    "outputs/json/collision_backend_comparison.json": "code/collision_contact/generate_collision_contact_components.py",
    "outputs/csv/collision_shape_manifest.csv": "code/collision_contact/generate_collision_contact_components.py",
    "outputs/json/collision_shape_manifest.json": "code/collision_contact/generate_collision_contact_components.py",
    "outputs/json/collision_model_registry.json": "code/collision_contact/generate_collision_contact_components.py",
    "outputs/csv/collision_family_filter_map.csv": "code/collision_contact/generate_collision_contact_components.py",
    "outputs/json/collision_family_filter_map.json": "code/collision_contact/generate_collision_contact_components.py",
    "outputs/csv/contact_material_manifest.csv": "code/collision_contact/generate_collision_contact_components.py",
    "outputs/json/contact_material_manifest.json": "code/collision_contact/generate_collision_contact_components.py",
    "outputs/csv/contact_pair_material_policy.csv": "code/collision_contact/generate_collision_contact_components.py",
    "outputs/json/contact_pair_material_policy.json": "code/collision_contact/generate_collision_contact_components.py",
    "outputs/csv/contact_container_manifest.csv": "code/collision_contact/generate_collision_contact_components.py",
    "outputs/json/contact_container_manifest.json": "code/collision_contact/generate_collision_contact_components.py",
    "outputs/csv/contact_callback_manifest.csv": "code/collision_contact/generate_collision_contact_components.py",
    "outputs/json/contact_callback_manifest.json": "code/collision_contact/generate_collision_contact_components.py",
    "outputs/csv/contact_frame_debug_manifest.csv": "code/collision_contact/generate_collision_contact_components.py",
    "outputs/json/contact_frame_debug_manifest.json": "code/collision_contact/generate_collision_contact_components.py",
    "outputs/csv/data_visualization_state_log.csv": "code/data_visualization/generate_data_visualization_components.py",
    "outputs/csv/data_visualization_control_log.csv": "code/data_visualization/generate_data_visualization_components.py",
    "outputs/csv/sensor_manifest.csv": "code/data_visualization/generate_data_visualization_components.py",
    "outputs/json/sensor_manifest.json": "code/data_visualization/generate_data_visualization_components.py",
    "outputs/csv/sensor_timing_schedule.csv": "code/data_visualization/generate_data_visualization_components.py",
    "outputs/json/sensor_timing_schedule.json": "code/data_visualization/generate_data_visualization_components.py",
    "outputs/csv/sensor_filter_catalog.csv": "code/data_visualization/generate_data_visualization_components.py",
    "outputs/json/sensor_filter_catalog.json": "code/data_visualization/generate_data_visualization_components.py",
    "outputs/json/sensor_scene_manifest.json": "code/data_visualization/generate_data_visualization_components.py",
    "outputs/json/sensor_module_capability_manifest.json": "code/data_visualization/generate_data_visualization_components.py",
    "outputs/json/terrain_component_manifest.json": "code/environment_terrain/generate_environment_terrain_components.py",
    "outputs/json/robot_vsg_capture_manifest.json": "code/common/generate_chrono_builtin_component_assets.py",
    "outputs/json/vehicle_vsg_capture_manifest.json": "code/common/generate_chrono_builtin_component_assets.py",
    "outputs/csv/render_manifest.csv": "code/common/generate_component_artifact_manifest.py",
    "outputs/json/render_manifest.json": "code/common/generate_component_artifact_manifest.py",
    "outputs/csv/visual_asset_manifest.csv": "code/common/generate_component_artifact_manifest.py",
    "outputs/json/visual_asset_manifest.json": "code/common/generate_component_artifact_manifest.py",
    "outputs/json/chrono_output_database_manifest.json": "code/common/generate_component_artifact_manifest.py",
    "outputs/csv/checkpoint_manifest.csv": "code/common/generate_component_artifact_manifest.py",
    "outputs/json/checkpoint_manifest.json": "code/common/generate_component_artifact_manifest.py",
    "outputs/csv/gnuplot_plot_manifest.csv": "code/common/generate_component_artifact_manifest.py",
    "outputs/json/gnuplot_plot_manifest.json": "code/common/generate_component_artifact_manifest.py",
    "outputs/raw/gnuplot/data_visualization_control_inputs.dat": "code/common/generate_component_artifact_manifest.py",
    "outputs/raw/gnuplot/data_visualization_control_inputs.gpl": "code/common/generate_component_artifact_manifest.py",
    "outputs/csv/offline_visual_export_manifest.csv": "code/common/generate_component_artifact_manifest.py",
    "outputs/json/offline_visual_export_manifest.json": "code/common/generate_component_artifact_manifest.py",
    "outputs/csv/logger_timebase_manifest.csv": "code/common/generate_component_artifact_manifest.py",
    "outputs/json/logger_timebase_manifest.json": "code/common/generate_component_artifact_manifest.py",
    "outputs/csv/writer_backend_manifest.csv": "code/common/generate_component_artifact_manifest.py",
    "outputs/json/writer_backend_manifest.json": "code/common/generate_component_artifact_manifest.py",
}

CSV_PRODUCERS.update(
    {
        "outputs/csv/fea_mesh_manifest.csv": "code/common/generate_component_artifact_manifest.py",
        "outputs/json/fea_mesh_manifest.json": "code/common/generate_component_artifact_manifest.py",
        "outputs/csv/fea_node_element_count.csv": "code/common/generate_component_artifact_manifest.py",
        "outputs/json/material_law_manifest.json": "code/common/generate_component_artifact_manifest.py",
        "outputs/csv/boundary_condition_map.csv": "code/common/generate_component_artifact_manifest.py",
        "outputs/json/boundary_condition_map.json": "code/common/generate_component_artifact_manifest.py",
        "outputs/csv/mode_frequency_table.csv": "code/common/generate_component_artifact_manifest.py",
        "outputs/json/modal_basis_manifest.json": "code/common/generate_component_artifact_manifest.py",
        "outputs/json/model_import_manifest.json": "code/common/generate_component_artifact_manifest.py",
        "outputs/csv/asset_manifest.csv": "code/common/generate_component_artifact_manifest.py",
        "outputs/json/asset_manifest.json": "code/common/generate_component_artifact_manifest.py",
        "outputs/csv/cad_shape_manifest.csv": "code/common/generate_component_artifact_manifest.py",
        "outputs/json/cad_shape_manifest.json": "code/common/generate_component_artifact_manifest.py",
        "outputs/csv/external_interface_map.csv": "code/common/generate_component_artifact_manifest.py",
        "outputs/json/external_interface_map.json": "code/common/generate_component_artifact_manifest.py",
        "outputs/json/sync_contract.json": "code/common/generate_component_artifact_manifest.py",
        "outputs/csv/sync_exchange_log.csv": "code/common/generate_component_artifact_manifest.py",
        "outputs/csv/fmu_variable_map.csv": "code/common/generate_component_artifact_manifest.py",
        "outputs/json/fmu_variable_map.json": "code/common/generate_component_artifact_manifest.py",
        "outputs/csv/ros_topic_handler_manifest.csv": "code/common/generate_component_artifact_manifest.py",
        "outputs/json/ros_topic_handler_manifest.json": "code/common/generate_component_artifact_manifest.py",
        "outputs/json/vehicle_cosim_node_manifest.json": "code/common/generate_component_artifact_manifest.py",
        "outputs/json/synchrono_agent_manifest.json": "code/common/generate_component_artifact_manifest.py",
    }
)

GRAPH_INPUTS = {
    "images/graphs/rover_vehicle_chassis_probe_graph.png": "outputs/csv/rover_vehicle_chassis_probe.csv",
    "images/graphs/terrain_height_sinkage_profile.png": "outputs/csv/environment_terrain_height_friction_sinkage.csv",
    "images/graphs/terrain_contact_material_friction_map.png": "outputs/csv/environment_terrain_height_friction_sinkage.csv",
    "images/graphs/terrain_contact_force_probe.png": "outputs/csv/environment_terrain_contact_probe.csv",
    "images/graphs/collision_contact_force_graph.png": "outputs/csv/collision_contact_probe.csv",
    "images/graphs/collision_contact_count_graph.png": "outputs/csv/collision_contact_probe.csv",
    "images/graphs/collision_contact_force_components_graph.png": "outputs/csv/collision_contact_probe.csv",
    "images/graphs/collision_contact_material_effect_graph.png": "outputs/csv/collision_contact_probe.csv",
    "images/graphs/collision_event_timeline_graph.png": "outputs/csv/collision_event_timeline.csv",
    "images/graphs/data_visualization_state_trajectory.png": "outputs/csv/data_visualization_state_log.csv",
    "images/graphs/data_visualization_control_inputs.png": "outputs/csv/data_visualization_control_log.csv",
}

GRAPH_DETAILS = {
    "images/graphs/rover_vehicle_chassis_probe_graph.png": {
        "axis_units": "x=time_s [s]; y=z_m [m], vx_mps [m/s], motor_speed_radps [rad/s]",
        "smoothing_policy": "raw rows",
        "event_markers": "none",
    },
    "images/graphs/terrain_height_sinkage_profile.png": {
        "axis_units": "x=x_m [m]; y=height_m [m], sinkage_m [m]",
        "smoothing_policy": "raw sampled surface profile",
        "event_markers": "none",
    },
    "images/graphs/terrain_contact_material_friction_map.png": {
        "axis_units": "x=x_m [m]; y=y_m [m]; color=terrain_mu_query/contact_material_mu [-]",
        "smoothing_policy": "raw sampled material map",
        "event_markers": "none",
    },
    "images/graphs/terrain_contact_force_probe.png": {
        "axis_units": "x=time_s [s]; y=contact_force_N/contact_fx_N/contact_fy_N/contact_fz_N [N]",
        "smoothing_policy": "raw rows",
        "event_markers": "none",
    },
    "images/graphs/collision_contact_force_graph.png": {
        "axis_units": "x=time_s [s]; y=contact_force_N [N]",
        "smoothing_policy": "raw rows",
        "event_markers": "none",
    },
    "images/graphs/collision_contact_count_graph.png": {
        "axis_units": "x=time_s [s]; y=contact_count [-]",
        "smoothing_policy": "raw rows",
        "event_markers": "none",
    },
    "images/graphs/collision_contact_force_components_graph.png": {
        "axis_units": "x=time_s [s]; y=contact_fx_N/contact_fy_N/contact_fz_N [N]",
        "smoothing_policy": "raw rows",
        "event_markers": "none",
    },
    "images/graphs/collision_contact_material_effect_graph.png": {
        "axis_units": "x=time_s [s]; y=contact_force_N [N]",
        "smoothing_policy": "raw rows grouped by material_id_a/material_id_b",
        "event_markers": "none",
    },
    "images/graphs/collision_event_timeline_graph.png": {
        "axis_units": "x=time_s [s]; y=event/contact_count [-]",
        "smoothing_policy": "raw event rows",
        "event_markers": "collision.event_timeline.v1 event column",
    },
    "images/graphs/data_visualization_state_trajectory.png": {
        "axis_units": "trajectory x=x_m [m], y=y_m [m]; speed x=time_s [s], y=speed [m/s]",
        "smoothing_policy": "raw rows",
        "event_markers": "start/end row markers",
    },
    "images/graphs/data_visualization_control_inputs.png": {
        "axis_units": "x=time_s [s]; y=throttle/brake/steering normalized [-]",
        "smoothing_policy": "raw rows",
        "event_markers": "none",
    },
}

MANIFEST_OUTPUTS = {
    "outputs/csv/artifact_manifest.csv",
    "outputs/json/artifact_manifest.json",
    "outputs/json/run_metadata.json",
}

METADATA_DERIVED_OUTPUTS = MANIFEST_OUTPUTS | {
    "outputs/csv/logger_timebase_manifest.csv",
    "outputs/json/logger_timebase_manifest.json",
    "outputs/csv/writer_backend_manifest.csv",
    "outputs/json/writer_backend_manifest.json",
    "outputs/csv/render_manifest.csv",
    "outputs/json/render_manifest.json",
    "outputs/csv/visual_asset_manifest.csv",
    "outputs/json/visual_asset_manifest.json",
    "outputs/json/chrono_output_database_manifest.json",
    "outputs/csv/checkpoint_manifest.csv",
    "outputs/json/checkpoint_manifest.json",
    "outputs/csv/gnuplot_plot_manifest.csv",
    "outputs/json/gnuplot_plot_manifest.json",
    "outputs/csv/offline_visual_export_manifest.csv",
    "outputs/json/offline_visual_export_manifest.json",
    "outputs/csv/fea_mesh_manifest.csv",
    "outputs/json/fea_mesh_manifest.json",
    "outputs/csv/fea_node_element_count.csv",
    "outputs/json/material_law_manifest.json",
    "outputs/csv/boundary_condition_map.csv",
    "outputs/json/boundary_condition_map.json",
    "outputs/csv/mode_frequency_table.csv",
    "outputs/json/modal_basis_manifest.json",
    "outputs/json/model_import_manifest.json",
    "outputs/csv/asset_manifest.csv",
    "outputs/json/asset_manifest.json",
    "outputs/csv/cad_shape_manifest.csv",
    "outputs/json/cad_shape_manifest.json",
    "outputs/csv/external_interface_map.csv",
    "outputs/json/external_interface_map.json",
    "outputs/json/sync_contract.json",
    "outputs/csv/sync_exchange_log.csv",
    "outputs/csv/fmu_variable_map.csv",
    "outputs/json/fmu_variable_map.json",
    "outputs/csv/ros_topic_handler_manifest.csv",
    "outputs/json/ros_topic_handler_manifest.json",
    "outputs/json/vehicle_cosim_node_manifest.json",
    "outputs/json/synchrono_agent_manifest.json",
}


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _mtime_utc(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).replace(microsecond=0).isoformat()


def _read_csv_metadata(path: Path) -> dict[str, str]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    schema_values = sorted({row.get("schema_id", "") for row in rows if row.get("schema_id", "")})
    source_values = sorted({row.get("source", "") for row in rows if row.get("source", "")})
    return {
        "schema_id": ";".join(schema_values),
        "source": ";".join(source_values),
        "row_count": str(len(rows)),
    }


def _read_json_metadata(path: Path) -> dict[str, str]:
    payload = json.load(path.open(encoding="utf-8"))
    schema_id = str(payload.get("schema_id", ""))
    source = str(payload.get("source", ""))
    row_count = ""
    for key in (
        "artifacts",
        "terrain_components",
        "wheels",
        "hardpoints",
        "components",
        "output_policy",
        "timebases",
        "writers",
        "scene_components",
        "sensors",
        "schedule",
        "filters",
        "model_specs",
        "system_components",
        "backends",
        "shapes",
        "models",
        "families",
        "materials",
        "pair_policies",
        "containers",
        "callbacks",
        "debug_frames",
        "captures",
        "renders",
        "visual_assets",
        "output_databases",
        "checkpoints",
        "gnuplot_plots",
        "offline_exports",
        "meshes",
        "material_laws",
        "boundary_conditions",
        "modal_bases",
        "model_imports",
        "assets",
        "cad_shapes",
        "external_interfaces",
        "sync_contracts",
        "fmu_variables",
        "ros_topics",
        "cosim_nodes",
        "synchrono_agents",
        "capabilities",
        "patches",
        "material_regions",
        "domains",
        "soil_profiles",
    ):
        value = payload.get(key)
        if isinstance(value, list):
            row_count = str(len(value))
            break
    if not row_count and isinstance(payload.get("subsystem_types"), dict):
        row_count = str(len(payload["subsystem_types"]))
    return {"schema_id": schema_id, "source": source, "row_count": row_count}


def _metadata_for_path(path: Path) -> dict[str, str]:
    rel_path = _rel(path)
    if path.suffix == ".csv":
        metadata = _read_csv_metadata(path)
        if rel_path in METADATA_DERIVED_OUTPUTS:
            metadata["child_source_values"] = metadata["source"]
            metadata["source"] = "generated_report_metadata"
        return metadata
    if path.suffix == ".json":
        metadata = _read_json_metadata(path)
        if rel_path in METADATA_DERIVED_OUTPUTS:
            metadata["child_source_values"] = metadata["source"]
            metadata["source"] = "generated_report_metadata"
        return metadata
    return {"schema_id": "", "source": "", "row_count": ""}


def _csv_dict_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _median_step(values: list[float]) -> str:
    if len(values) < 2:
        return ""
    deltas = sorted(round(values[i + 1] - values[i], 9) for i in range(len(values) - 1))
    mid = len(deltas) // 2
    median = deltas[mid] if len(deltas) % 2 else 0.5 * (deltas[mid - 1] + deltas[mid])
    return f"{median:.9g}"


def _metadata_scan_targets() -> list[Path]:
    targets = []
    for base in (OUTPUT_CSV, OUTPUT_JSON):
        if not base.exists():
            continue
        for path in base.rglob("*"):
            rel_path = _rel(path) if path.is_file() else ""
            if path.is_file() and rel_path not in METADATA_DERIVED_OUTPUTS:
                targets.append(path)
    return sorted(targets, key=_rel)


def generate_logger_timebase_manifest() -> tuple[Path, Path]:
    rows = []
    for path in sorted(OUTPUT_CSV.glob("*.csv")):
        rel_path = _rel(path)
        if rel_path in METADATA_DERIVED_OUTPUTS:
            continue
        data_rows = _csv_dict_rows(path)
        if not data_rows:
            continue
        header = data_rows[0].keys()
        metadata = _read_csv_metadata(path)
        time_values = [float(row["time_s"]) for row in data_rows if "time_s" in row and row.get("time_s", "") not in ("", "nan")]
        sample_values = [int(row["sample_index"]) for row in data_rows if "sample_index" in row and row.get("sample_index", "").isdigit()]
        has_time = bool(time_values)
        has_step = "step_index" in header
        if has_time:
            clock_source = "ChSystem::GetChTime or deterministic fallback time_s"
            index_column = "step_index" if has_step else "time_s"
            time_start = f"{min(time_values):.6g}"
            time_end = f"{max(time_values):.6g}"
            sample_period = _median_step(time_values)
        else:
            clock_source = "surface/sample index, no simulation clock"
            index_column = "sample_index" if sample_values else ""
            time_start = ""
            time_end = ""
            sample_period = "1 sample index" if sample_values else ""
        rows.append(
            {
                "schema_id": "data.logger_timebase_manifest.v1",
                "run_id": RUN_ID,
                "artifact_path": rel_path,
                "source_schema_id": metadata["schema_id"],
                "clock_source": clock_source,
                "has_time_s": str(has_time).lower(),
                "has_step_index": str(has_step).lower(),
                "index_column": index_column,
                "row_count": metadata["row_count"],
                "time_start_s": time_start,
                "time_end_s": time_end,
                "sample_period_s": sample_period if has_time else "",
                "sample_period_index": sample_period if not has_time else "",
                "alignment_key": "run_id + scenario_id + step_index" if has_step else "run_id + scenario_id + sample_index",
                "dropped_sample_policy": "not simulated in fallback bundle; live runs must mark dropped_sample/drop_reason",
                "resampling_policy": "raw rows",
                "source": metadata["source"],
            }
        )
    fieldnames = [
        "schema_id",
        "run_id",
        "artifact_path",
        "source_schema_id",
        "clock_source",
        "has_time_s",
        "has_step_index",
        "index_column",
        "row_count",
        "time_start_s",
        "time_end_s",
        "sample_period_s",
        "sample_period_index",
        "alignment_key",
        "dropped_sample_policy",
        "resampling_policy",
        "source",
    ]
    csv_path = write_csv(LOGGER_TIMEBASE_CSV, fieldnames, rows)
    json_path = write_json(LOGGER_TIMEBASE_JSON, {"schema_id": "data.logger_timebase_manifest.v1", "run_id": RUN_ID, "source": "generated_report_metadata", "timebases": rows})
    return csv_path, json_path


def generate_writer_backend_manifest() -> tuple[Path, Path]:
    rows = []
    for path in _metadata_scan_targets():
        rel_path = _rel(path)
        metadata = _metadata_for_path(path)
        producer_script = CSV_PRODUCERS.get(rel_path, "")
        if path.suffix == ".csv":
            writer_backend = "python_csv"
            output_mode = "row_stream"
        elif path.suffix == ".json":
            writer_backend = "python_json"
            output_mode = "document"
        else:
            writer_backend = "unknown"
            output_mode = "file"
        rows.append(
            {
                "schema_id": "data.writer_backend_manifest.v1",
                "run_id": RUN_ID,
                "artifact_path": rel_path,
                "artifact_type": _artifact_type(rel_path),
                "writer_backend": writer_backend,
                "output_mode": output_mode,
                "producer_script": producer_script,
                "artifact_hash": _sha256(path),
                "row_count": metadata["row_count"],
                "source_schema_id": metadata["schema_id"],
                "source": metadata["source"],
                "unit_policy": "SI units in column names where applicable",
                "evidence_level": _evidence_level(rel_path, metadata),
            }
        )
    fieldnames = [
        "schema_id",
        "run_id",
        "artifact_path",
        "artifact_type",
        "writer_backend",
        "output_mode",
        "producer_script",
        "artifact_hash",
        "row_count",
        "source_schema_id",
        "source",
        "unit_policy",
        "evidence_level",
    ]
    csv_path = write_csv(WRITER_BACKEND_CSV, fieldnames, rows)
    json_path = write_json(WRITER_BACKEND_JSON, {"schema_id": "data.writer_backend_manifest.v1", "run_id": RUN_ID, "source": "generated_report_metadata", "writers": rows})
    return csv_path, json_path


def _producer_map_from_readme() -> dict[str, str]:
    if not README.exists():
        return {}
    mapping: dict[str, str] = {}
    cell_re = re.compile(r"`([^`]+)`")
    for line in README.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = cell_re.findall(line)
        image_cells = [cell for cell in cells if cell.startswith("images/") and cell.endswith(".png")]
        script_cells = [cell for cell in cells if cell.startswith("code/") and cell.endswith(".py")]
        if image_cells and script_cells:
            mapping[image_cells[0]] = script_cells[-1]
    return mapping


def _render_image_targets() -> list[Path]:
    bases = [ROOT / "images" / "renders", ROOT / "images" / "graphs", ROOT / "images" / "mermaid_rendered"]
    targets: list[Path] = []
    for base in bases:
        if base.exists():
            targets.extend(path for path in base.glob("*.png") if path.is_file())
    return sorted(targets, key=_rel)


def _visible_component_ids(rel_path: str) -> str:
    name = Path(rel_path).stem
    vehicle_capture = _vehicle_vsg_capture_row(rel_path)
    if vehicle_capture.get("visible_component_ids"):
        return vehicle_capture["visible_component_ids"]
    capture = _robot_vsg_capture_row(rel_path)
    if capture.get("visible_component_ids"):
        return capture["visible_component_ids"]
    if name == "chrono_builtin_robot_rover_assets" and _robot_vsg_capture_available():
        payload = _robot_vsg_capture_payload()
        ids: set[str] = set()
        for row in payload.get("captures", []):
            if isinstance(row, dict):
                ids.update(part.strip() for part in str(row.get("visible_component_ids", "")).split(";") if part.strip())
        return ";".join(sorted(ids)) if ids else "vehicle.robot_assets;visual.runtime"
    if name.startswith("chrono_viper") or name.startswith("chrono_curiosity"):
        return "vehicle.robot_assets;visual.runtime"
    if name.startswith("rover_driver"):
        return "core.function_input;vehicle.steering;vehicle.powertrain;vehicle.brake"
    if name.startswith("rover_powertrain"):
        return "vehicle.powertrain;vehicle.driveline;vehicle.brake;vehicle.tire_model"
    if name.startswith("rover_"):
        return "vehicle.chassis;vehicle.wheel;vehicle.axle;core.visual_asset"
    if name.startswith("tracked_vehicle"):
        return "vehicle.track_assembly;vehicle.track_shoe;vehicle.sprocket;vehicle.road_wheel"
    if name.startswith("terrain_"):
        return "terrain.interface;terrain.core_ground;terrain.material_region;environment.field"
    if name.startswith("collision_"):
        return "collision.system_lifecycle;collision.shape_manifest;contact.container_reporter"
    if name.startswith("data_visualization"):
        return "data.artifact_manifest;visual.runtime;sensor.output_writer"
    if name.startswith("component_catalog_atlas"):
        return "runtime.system;vehicle.chassis;terrain.interface;collision.system_lifecycle;data.artifact_manifest"
    if name.startswith("core_") or name.startswith("chrono_default"):
        return "runtime.system;core.body;core.visual_asset;core.link_constraint"
    if name.startswith("chrono_module") or name.startswith("chrono_optional"):
        return "runtime.config;runtime.system"
    if name.startswith("external_integration"):
        return "model.spec_resolver;model.urdf_import;asset.cad_step;integration.ros;integration.fmi"
    if name.startswith("flexible_body"):
        return "flex.mesh;flex.material_section;flex.modal_reduction"
    if name.startswith("2_2_mermaid"):
        return "report.flow_diagram"
    return "visual.runtime"


def _render_backend(rel_path: str) -> str:
    if rel_path.startswith("images/mermaid_rendered/"):
        return "mmdc or local matplotlib Mermaid fallback"
    if _vehicle_vsg_capture_row(rel_path).get("available") == "true":
        return "pychrono.vsg3d ChVisualSystemVSG visual asset capture"
    if Path(rel_path).name in {"chrono_builtin_robot_rover_assets.png", "chrono_viper_vsg_capture.png", "chrono_curiosity_vsg_capture.png"}:
        return "pychrono.vsg3d ChVisualSystemVSG"
    if rel_path.startswith("images/graphs/"):
        return "matplotlib Agg graph"
    return "matplotlib Agg render"


def _render_source(rel_path: str) -> str:
    vehicle_capture = _vehicle_vsg_capture_row(rel_path)
    if vehicle_capture.get("source"):
        return vehicle_capture["source"]
    if Path(rel_path).name in {"chrono_builtin_robot_rover_assets.png", "chrono_viper_vsg_capture.png", "chrono_curiosity_vsg_capture.png"} and _robot_vsg_capture_available():
        return "pychrono_vsg_capture"
    if rel_path.startswith("images/graphs/"):
        graph_input = GRAPH_INPUTS.get(rel_path, "")
        if graph_input and (ROOT / graph_input).exists():
            return _read_csv_metadata(ROOT / graph_input)["source"]
        return "generated_graph"
    if rel_path.startswith("images/mermaid_rendered/"):
        return "rendered_mermaid"
    return "concept_render"


def _robot_vsg_capture_payload() -> dict:
    manifest = OUTPUT_JSON / "robot_vsg_capture_manifest.json"
    if not manifest.exists():
        return {}
    try:
        payload = json.load(manifest.open(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _robot_vsg_capture_row(rel_path: str) -> dict[str, str]:
    payload = _robot_vsg_capture_payload()
    for row in payload.get("captures", []):
        if isinstance(row, dict) and row.get("artifact_path") == rel_path:
            return {str(key): str(value) for key, value in row.items()}
    return {}


def _vehicle_vsg_capture_payload() -> dict:
    manifest = OUTPUT_JSON / "vehicle_vsg_capture_manifest.json"
    if not manifest.exists():
        return {}
    try:
        payload = json.load(manifest.open(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _vehicle_vsg_capture_row(rel_path: str) -> dict[str, str]:
    payload = _vehicle_vsg_capture_payload()
    for row in payload.get("captures", []):
        if isinstance(row, dict) and row.get("artifact_path") == rel_path:
            return {str(key): str(value) for key, value in row.items()}
    return {}


def _render_camera_fields(rel_path: str) -> dict[str, str]:
    vehicle_row = _vehicle_vsg_capture_row(rel_path)
    if vehicle_row:
        return {
            "camera_or_layout": "pychrono.vsg3d visual asset camera",
            "camera_eye": vehicle_row.get("camera_eye", ""),
            "camera_target": vehicle_row.get("camera_target", ""),
            "camera_fov_deg": vehicle_row.get("camera_fov_deg", ""),
        }
    row = _robot_vsg_capture_row(rel_path)
    if row:
        return {
            "camera_or_layout": "pychrono.vsg3d camera",
            "camera_eye": row.get("camera_eye", ""),
            "camera_target": row.get("camera_target", ""),
            "camera_fov_deg": row.get("camera_fov_deg", ""),
        }
    if Path(rel_path).name == "chrono_builtin_robot_rover_assets.png" and _robot_vsg_capture_available():
        payload = _robot_vsg_capture_payload()
        return {
            "camera_or_layout": "composite panel of VSG captures; see robot_vsg_capture_manifest captures",
            "camera_eye": "per_capture",
            "camera_target": "per_capture",
            "camera_fov_deg": ";".join(sorted({str(row.get("camera_fov_deg", "")) for row in payload.get("captures", []) if isinstance(row, dict) and row.get("camera_fov_deg")})),
        }
    return {"camera_or_layout": "see producer script", "camera_eye": "", "camera_target": "", "camera_fov_deg": ""}


def generate_render_manifest() -> tuple[Path, Path]:
    producer_map = _producer_map_from_readme()
    rows = []
    for path in _render_image_targets():
        rel_path = _rel(path)
        producer_script = CSV_PRODUCERS.get(rel_path, producer_map.get(rel_path, ""))
        with Image.open(path) as image:
            width_px, height_px = image.size
        camera_fields = _render_camera_fields(rel_path)
        rows.append(
            {
                "schema_id": "visual.render_manifest.v1",
                "run_id": RUN_ID,
                "artifact_path": rel_path,
                "artifact_type": _artifact_type(rel_path),
                "producer_script": producer_script,
                "producer_hash": _sha256(ROOT / producer_script) if producer_script and (ROOT / producer_script).exists() else "",
                "artifact_hash": _sha256(path),
                "image_width_px": str(width_px),
                "image_height_px": str(height_px),
                "render_backend": _render_backend(rel_path),
                "camera_or_layout": camera_fields["camera_or_layout"],
                "camera_eye": camera_fields["camera_eye"],
                "camera_target": camera_fields["camera_target"],
                "camera_fov_deg": camera_fields["camera_fov_deg"],
                "visible_component_ids": _visible_component_ids(rel_path),
                "source": _render_source(rel_path),
                "evidence_level": _evidence_level(rel_path, {"source": _render_source(rel_path)}),
            }
        )
    fieldnames = list(rows[0].keys()) if rows else [
        "schema_id",
        "run_id",
        "artifact_path",
        "artifact_type",
        "producer_script",
        "producer_hash",
        "artifact_hash",
        "image_width_px",
        "image_height_px",
        "render_backend",
        "camera_or_layout",
        "camera_eye",
        "camera_target",
        "camera_fov_deg",
        "visible_component_ids",
        "source",
        "evidence_level",
    ]
    csv_path = write_csv(RENDER_MANIFEST_CSV, fieldnames, rows)
    json_path = write_json(RENDER_MANIFEST_JSON, {"schema_id": "visual.render_manifest.v1", "run_id": RUN_ID, "source": "generated_report_metadata", "renders": rows})
    return csv_path, json_path


def _visual_asset_owner(rel_path: str) -> str:
    visible_ids = _visible_component_ids(rel_path).split(";")
    return visible_ids[0] if visible_ids and visible_ids[0] != "report.flow_diagram" else "visual.runtime"


def _asset_source_hint(rel_path: str) -> str:
    name = Path(rel_path).name
    if name == "chrono_viper_vsg_capture.png":
        return "chrono_build_cuda129_sm120/data/robot/viper"
    if name == "chrono_curiosity_vsg_capture.png":
        return "chrono_build_cuda129_sm120/data/robot/curiosity"
    if name == "chrono_builtin_robot_rover_assets.png":
        return "composite of VIPER and Curiosity VSG captures"
    if name.startswith("chrono_builtin_wheeled"):
        return "chrono_build/data/vehicle/hmmwv"
    if name.startswith("chrono_builtin_tracked"):
        return "chrono_build/data/vehicle/M113"
    return "procedural report render"


def _is_vsg_robot_asset(rel_path: str) -> bool:
    return Path(rel_path).name in {"chrono_builtin_robot_rover_assets.png", "chrono_viper_vsg_capture.png", "chrono_curiosity_vsg_capture.png"} and _robot_vsg_capture_available()


def _is_vsg_vehicle_asset(rel_path: str) -> bool:
    row = _vehicle_vsg_capture_row(rel_path)
    return row.get("available") == "true" and row.get("source") == "pychrono_vsg_capture"


def _visual_asset_contract_fields(rel_path: str) -> dict[str, str]:
    name = Path(rel_path).name
    if _is_vsg_vehicle_asset(rel_path):
        capture = _vehicle_vsg_capture_row(rel_path)
        return {
            "owner_physics_item": capture.get("vehicle_model", "Chrono vehicle visual asset assembly"),
            "visual_model_id": f"{Path(rel_path).stem}.vsg_visual_model",
            "shape_id": capture.get("visible_vehicle_part_ids", ""),
            "shape_class": "Chrono Vehicle OBJ visual shapes captured through ChVisualSystemVSG",
            "shape_local_frame": "Chrono Vehicle visual asset frames; see vehicle_vsg_capture_manifest camera/part ids",
            "REF_or_COG_frame": "vehicle visual asset frames",
            "material_slots": "runtime VSG mesh materials",
            "visual_material_id": "vehicle_runtime_materials",
            "mesh_path": capture.get("data_path_hint", ""),
            "mesh_hash": "",
            "texture_path_hash": "",
            "visible_in_runtime": "true",
            "visible_in_sensor_scene": "unknown",
            "sensor_scene_material_policy": "not exported by VSG capture; Sensor scene material must be logged by live Sensor run",
            "fallback_reason": "",
        }
    if _is_vsg_robot_asset(rel_path):
        capture = _robot_vsg_capture_row(rel_path)
        if name == "chrono_builtin_robot_rover_assets.png":
            owner = "robot.Viper + robot.Curiosity visual assemblies"
            visual_model_id = "robot_rover_assets.vsg_composite"
            shape_id = "viper.parts;curiosity.parts"
            mesh_path = "composite of VSG runtime captures"
        else:
            model = capture.get("robot_model", Path(rel_path).stem)
            owner = f"robot.{model} body/wheel/mast visual assemblies"
            visual_model_id = f"robot.{model}.visual_model"
            shape_id = capture.get("visible_robot_part_ids", "")
            mesh_path = capture.get("data_path_hint", "")
        return {
            "owner_physics_item": owner,
            "visual_model_id": visual_model_id,
            "shape_id": shape_id,
            "shape_class": "Chrono Robot visual shapes captured through ChVisualSystemVSG",
            "shape_local_frame": "Chrono robot model frames; see robot_vsg_capture_manifest camera/part ids",
            "REF_or_COG_frame": "robot subsystem REF frames",
            "material_slots": "runtime VSG materials/textures",
            "visual_material_id": "robot_runtime_materials",
            "mesh_path": mesh_path,
            "mesh_hash": "",
            "texture_path_hash": "",
            "visible_in_runtime": "true",
            "visible_in_sensor_scene": "unknown",
            "sensor_scene_material_policy": "not exported by VSG capture; Sensor scene material must be logged by live Sensor run",
            "fallback_reason": "",
        }
    return {
        "owner_physics_item": "report_concept_render",
        "visual_model_id": "",
        "shape_id": "",
        "shape_class": "report PNG concept/rendered diagram",
        "shape_local_frame": "report image frame",
        "REF_or_COG_frame": "not applicable",
        "material_slots": "matplotlib/report colors",
        "visual_material_id": "",
        "mesh_path": "",
        "mesh_hash": "",
        "texture_path_hash": "",
        "visible_in_runtime": "false",
        "visible_in_sensor_scene": "unknown",
        "sensor_scene_material_policy": "not a Chrono sensor scene asset",
        "fallback_reason": "concept_render_only",
    }


def generate_visual_asset_manifest() -> tuple[Path, Path]:
    rows = []
    for path in _render_image_targets():
        rel_path = _rel(path)
        if rel_path.startswith(("images/graphs/", "images/mermaid_rendered/")):
            continue
        source = _render_source(rel_path)
        contract = _visual_asset_contract_fields(rel_path)
        rows.append(
            {
                "schema_id": "visual.asset_manifest.v1",
                "run_id": RUN_ID,
                "visual_asset_id": Path(rel_path).stem,
                "owner_component_id": _visual_asset_owner(rel_path),
                "owner_physics_item": contract["owner_physics_item"],
                "visual_model_id": contract["visual_model_id"],
                "shape_id": contract["shape_id"],
                "shape_class": contract["shape_class"],
                "artifact_path": rel_path,
                "visual_backend": _render_backend(rel_path),
                "source_asset_or_generator": _asset_source_hint(rel_path),
                "mesh_or_texture_hash": _sha256(path),
                "shape_local_frame": contract["shape_local_frame"],
                "local_frame": contract["shape_local_frame"],
                "REF_or_COG_frame": contract["REF_or_COG_frame"],
                "material_slots": contract["material_slots"],
                "visual_material_id": contract["visual_material_id"],
                "mesh_path": contract["mesh_path"],
                "mesh_hash": contract["mesh_hash"],
                "texture_path_hash": contract["texture_path_hash"],
                "runtime_visible": contract["visible_in_runtime"],
                "sensor_scene_visible": contract["visible_in_sensor_scene"],
                "visible_in_runtime": contract["visible_in_runtime"],
                "visible_in_sensor_scene": contract["visible_in_sensor_scene"],
                "sensor_scene_material_policy": contract["sensor_scene_material_policy"],
                "fallback_reason": contract["fallback_reason"],
                "source": source,
                "evidence_level": _evidence_level(rel_path, {"source": source}),
            }
        )
    fieldnames = list(rows[0].keys()) if rows else [
        "schema_id",
        "run_id",
        "visual_asset_id",
        "owner_component_id",
        "owner_physics_item",
        "visual_model_id",
        "shape_id",
        "shape_class",
        "artifact_path",
        "visual_backend",
        "source_asset_or_generator",
        "mesh_or_texture_hash",
        "shape_local_frame",
        "local_frame",
        "REF_or_COG_frame",
        "material_slots",
        "visual_material_id",
        "mesh_path",
        "mesh_hash",
        "texture_path_hash",
        "runtime_visible",
        "sensor_scene_visible",
        "visible_in_runtime",
        "visible_in_sensor_scene",
        "sensor_scene_material_policy",
        "fallback_reason",
        "source",
        "evidence_level",
    ]
    csv_path = write_csv(VISUAL_ASSET_MANIFEST_CSV, fieldnames, rows)
    json_path = write_json(
        VISUAL_ASSET_MANIFEST_JSON,
        {"schema_id": "visual.asset_manifest.v1", "run_id": RUN_ID, "source": "generated_report_metadata", "visual_assets": rows},
    )
    return csv_path, json_path


def generate_chrono_output_database_manifest() -> Path:
    source = "fallback_chrono_native_output_not_executed"
    targets = [
        ("state_series", "outputs/csv/data_visualization_state_log.csv", "vehicle.chassis", "time_s series"),
        ("control_series", "outputs/csv/data_visualization_control_log.csv", "core.function_input;vehicle.drive", "time_s series"),
        ("contact_series", "outputs/csv/collision_contact_probe.csv", "contact.force_torque", "time_s series"),
        ("terrain_surface_samples", "outputs/csv/terrain_surface_probe.csv", "terrain.interface", "sample_index grid"),
        ("sensor_output_manifest", "outputs/csv/sensor_manifest.csv", "sensor.output_writer", "frame_index manifest"),
        ("render_index", "outputs/csv/render_manifest.csv", "visual.render_manifest", "artifact index"),
    ]
    rows = []
    for section_name, rel_path, component_scope, frame_or_series_id in targets:
        path = ROOT / rel_path
        if not path.exists():
            continue
        metadata = _metadata_for_path(path)
        rows.append(
            {
                "schema_id": "data.chrono_output_database_manifest.v1",
                "run_id": RUN_ID,
                "catalog_component_id": "data.chrono_output_db",
                "instance_id": f"chrono_output.{section_name}",
                "output_database_id": "component_catalog_output_bundle",
                "output_type": "ChOutputASCII/HDF5 contract; current artifact is Python CSV/JSON fallback",
                "output_mode": "row_stream" if path.suffix == ".csv" else "document",
                "database_path": rel_path,
                "section_name": section_name,
                "frame_or_series_id": frame_or_series_id,
                "component_scope": component_scope,
                "row_count": metadata["row_count"],
                "schema_map": metadata["schema_id"],
                "artifact_hash": _sha256(path),
                "writer_backend": "python_csv" if path.suffix == ".csv" else "python_json",
                "failure_mode": "native Chrono output database not executed in fallback bundle; use this row as the expected ChOutput section contract",
                "source": source,
            }
        )
    return write_json(
        CHRONO_OUTPUT_DATABASE_JSON,
        {"schema_id": "data.chrono_output_database_manifest.v1", "run_id": RUN_ID, "source": source, "output_databases": rows},
    )


def generate_checkpoint_manifest() -> tuple[Path, Path]:
    source = "fallback_checkpoint_manifest_only"
    checkpoint_scope = [
        ("core_rover_smoke_probe", "probe_ground;probe_chassis;probe_drive_wheel", "3", "3"),
        ("collision_contact_probe", "rover_body;rigid_obstacle;ground_body", "3", "3"),
        ("terrain_contact_probe", "sphere_probe;terrain.core_ground", "2", "2"),
    ]
    rows = []
    for scope_id, body_ids, body_count, collision_shape_count in checkpoint_scope:
        rows.append(
            {
                "schema_id": "data.checkpoint_manifest.v1",
                "run_id": RUN_ID,
                "catalog_component_id": "data.checkpoint_restart",
                "instance_id": f"checkpoint.{scope_id}",
                "checkpoint_id": f"checkpoint.{scope_id}",
                "checkpoint_scope": scope_id,
                "checkpoint_path": "",
                "checkpoint_hash": "",
                "checkpoint_time_s": "not_written",
                "body_count": body_count,
                "body_ids": body_ids,
                "collision_shape_count": collision_shape_count,
                "constraint_count": "schema_only",
                "sensor_state_included": "false",
                "terrain_state_included": "false",
                "restart_validity": "false",
                "restore_preconditions": "same Chrono version/build, modules, contact method, body registry, and terrain state must be available",
                "restore_assumptions": "fallback bundle records restart contract only; no binary/ASCII checkpoint is written",
                "not_for_validation_warning": "true",
                "source": source,
            }
        )
    fieldnames = list(rows[0].keys())
    csv_path = write_csv(CHECKPOINT_MANIFEST_CSV, fieldnames, rows)
    json_path = write_json(
        CHECKPOINT_MANIFEST_JSON,
        {"schema_id": "data.checkpoint_manifest.v1", "run_id": RUN_ID, "source": source, "checkpoints": rows},
    )
    return csv_path, json_path


def _write_gnuplot_inputs() -> tuple[Path, Path]:
    GNUPLOT_RAW_DIR.mkdir(parents=True, exist_ok=True)
    source_csv = OUTPUT_CSV / "data_visualization_control_log.csv"
    dat_path = GNUPLOT_RAW_DIR / "data_visualization_control_inputs.dat"
    gpl_path = GNUPLOT_RAW_DIR / "data_visualization_control_inputs.gpl"
    rows = _csv_dict_rows(source_csv) if source_csv.exists() else []
    with dat_path.open("w", encoding="utf-8") as handle:
        handle.write("# time_s throttle brake steering\n")
        for row in rows:
            handle.write(f"{row.get('time_s', '')} {row.get('throttle', '')} {row.get('brake', '')} {row.get('steering', '')}\n")
    gpl_path.write_text(
        "\n".join(
            [
                "set terminal pngcairo size 1280,720",
                "set output 'images/graphs/data_visualization_control_inputs_gnuplot.png'",
                "set title 'Control Logger Inputs'",
                "set xlabel 'time [s]'",
                "set ylabel 'normalized input'",
                "set grid",
                "plot 'outputs/raw/gnuplot/data_visualization_control_inputs.dat' using 1:2 with lines title 'throttle', \\",
                "     'outputs/raw/gnuplot/data_visualization_control_inputs.dat' using 1:3 with lines title 'brake', \\",
                "     'outputs/raw/gnuplot/data_visualization_control_inputs.dat' using 1:4 with lines title 'steering'",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return dat_path, gpl_path


def generate_gnuplot_plot_manifest() -> tuple[Path, Path]:
    dat_path, gpl_path = _write_gnuplot_inputs()
    source = "fallback_gnuplot_manifest_only"
    gnuplot_path = shutil.which("gnuplot") or ""
    output_path = ROOT / "images/graphs/data_visualization_control_inputs_gnuplot.png"
    rows = [
        {
            "schema_id": "postprocess.gnuplot_plot_manifest.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "postprocess.gnuplot_backend",
            "instance_id": "gnuplot.control_inputs",
            "plot_id": "control_inputs_time_series",
            "script_path": _rel(gpl_path),
            "script_hash": _sha256(gpl_path),
            "input_dat_path": _rel(dat_path),
            "input_dat_hash": _sha256(dat_path),
            "source_csv_path": "outputs/csv/data_visualization_control_log.csv",
            "source_csv_hash": _sha256(OUTPUT_CSV / "data_visualization_control_log.csv") if (OUTPUT_CSV / "data_visualization_control_log.csv").exists() else "",
            "terminal": "pngcairo",
            "output_format": "png",
            "output_path": _rel(output_path) if output_path.exists() else "images/graphs/data_visualization_control_inputs_gnuplot.png",
            "output_hash": _sha256(output_path) if output_path.exists() else "",
            "gnuplot_executable": gnuplot_path,
            "gnuplot_executable_available": str(bool(gnuplot_path)).lower(),
            "silent_no_output_failure": "true" if not output_path.exists() else "false",
            "fallback_reason": "" if output_path.exists() else "gnuplot command not executed by fallback bundle",
            "source": source,
        }
    ]
    fieldnames = list(rows[0].keys())
    csv_path = write_csv(GNUPLOT_PLOT_MANIFEST_CSV, fieldnames, rows)
    json_path = write_json(
        GNUPLOT_PLOT_MANIFEST_JSON,
        {"schema_id": "postprocess.gnuplot_plot_manifest.v1", "run_id": RUN_ID, "source": source, "gnuplot_plots": rows},
    )
    return csv_path, json_path


def _render_row_map() -> dict[str, dict[str, str]]:
    if not RENDER_MANIFEST_CSV.exists():
        return {}
    return {row["artifact_path"]: row for row in _csv_dict_rows(RENDER_MANIFEST_CSV)}


def generate_offline_visual_export_manifest() -> tuple[Path, Path]:
    source = "fallback_offline_visual_export_manifest_only"
    render_rows = _render_row_map()
    visual_asset_count = ""
    if VISUAL_ASSET_MANIFEST_CSV.exists():
        visual_asset_count = str(len(_csv_dict_rows(VISUAL_ASSET_MANIFEST_CSV)))
    target_images = [
        ("frame.vsg_robot_assets", "images/renders/chrono_builtin_robot_rover_assets.png", "code/common/generate_chrono_builtin_component_assets.py", "0.000"),
        ("frame.component_catalog_atlas", "images/renders/component_catalog_atlas.png", "code/common/generate_component_catalog_atlas_render.py", "0.000"),
        ("frame.sensor_layout", "images/renders/data_visualization_sensor_components.png", "code/data_visualization/generate_data_visualization_sensor_components_render.py", "0.000"),
    ]
    rows = []
    for frame_id, rel_path, renderer_script, system_time_s in target_images:
        path = ROOT / rel_path
        if not path.exists():
            continue
        render_row = render_rows.get(rel_path, {})
        rows.append(
            {
                "schema_id": "visual.offline_export_manifest.v1",
                "run_id": RUN_ID,
                "catalog_component_id": "visual.offline_export",
                "instance_id": frame_id,
                "frame_id": frame_id,
                "system_time_s": system_time_s,
                "visual_asset_manifest_path": _rel(VISUAL_ASSET_MANIFEST_CSV) if VISUAL_ASSET_MANIFEST_CSV.exists() else "",
                "visual_asset_manifest_hash": _sha256(VISUAL_ASSET_MANIFEST_CSV) if VISUAL_ASSET_MANIFEST_CSV.exists() else "",
                "visual_asset_count": visual_asset_count,
                "mesh_path_hash_policy": "current report hashes rendered bitmap assets; live WriteVisualizationAssets export must add mesh/texture CSV rows",
                "renderer_script": renderer_script,
                "renderer_script_hash": _sha256(ROOT / renderer_script) if (ROOT / renderer_script).exists() else "",
                "render_backend": render_row.get("render_backend", _render_backend(rel_path)),
                "rendered_image_path": rel_path,
                "rendered_image_hash": _sha256(path),
                "image_width_px": render_row.get("image_width_px", ""),
                "image_height_px": render_row.get("image_height_px", ""),
                "source_run_id": RUN_ID,
                "fallback_reason": "offline renderer export is represented by current report render assets; no separate WriteVisualizationAssets frame CSV was emitted",
                "source": source,
            }
        )
    fieldnames = list(rows[0].keys()) if rows else [
        "schema_id",
        "run_id",
        "catalog_component_id",
        "instance_id",
        "frame_id",
        "system_time_s",
        "visual_asset_manifest_path",
        "visual_asset_manifest_hash",
        "visual_asset_count",
        "mesh_path_hash_policy",
        "renderer_script",
        "renderer_script_hash",
        "render_backend",
        "rendered_image_path",
        "rendered_image_hash",
        "image_width_px",
        "image_height_px",
        "source_run_id",
        "fallback_reason",
        "source",
    ]
    csv_path = write_csv(OFFLINE_VISUAL_EXPORT_MANIFEST_CSV, fieldnames, rows)
    json_path = write_json(
        OFFLINE_VISUAL_EXPORT_MANIFEST_JSON,
        {"schema_id": "visual.offline_export_manifest.v1", "run_id": RUN_ID, "source": source, "offline_exports": rows},
    )
    return csv_path, json_path


def generate_flex_fea_catalog_manifests() -> list[Path]:
    source = "fallback_flex_fea_schema_only"
    mesh_rows = [
        {
            "schema_id": "flex.fea_mesh_manifest.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "flex.mesh",
            "instance_id": "flex.mesh.rover_panel_demo",
            "mesh_id": "fea_mesh.rover_panel_demo",
            "mesh_family": "ANCF_shell_or_solid_catalog_slot",
            "mesh_source_path": "not_bound_in_fallback_bundle",
            "mesh_source_hash": "",
            "node_count": "24",
            "element_count": "18",
            "element_family": "shell_quad_catalog_fixture",
            "frame": "body_REF",
            "visualization_surface_ids": "surface.panel_top;surface.panel_edge",
            "contact_surface_ids": "contact.panel_proxy",
            "material_law_id": "material.flex.aluminum_panel",
            "boundary_condition_ids": "bc.panel_root_fixed;bc.sensor_payload_load",
            "deformation_artifact_path": "",
            "source": source,
        }
    ]
    mesh_csv = write_csv(FEA_MESH_MANIFEST_CSV, list(mesh_rows[0].keys()), mesh_rows)
    mesh_json = write_json(
        FEA_MESH_MANIFEST_JSON,
        {"schema_id": "flex.fea_mesh_manifest.v1", "run_id": RUN_ID, "source": source, "meshes": mesh_rows},
    )

    count_rows = [
        {
            "schema_id": "flex.node_element_count.v1",
            "run_id": RUN_ID,
            "mesh_id": "fea_mesh.rover_panel_demo",
            "node_count": "24",
            "element_count": "18",
            "boundary_node_count": "6",
            "contact_surface_element_count": "4",
            "visual_surface_element_count": "18",
            "source": source,
        }
    ]
    count_csv = write_csv(FEA_NODE_ELEMENT_COUNT_CSV, list(count_rows[0].keys()), count_rows)

    material_rows = [
        {
            "schema_id": "flex.material_law_manifest.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "flex.material_section",
            "instance_id": "material.flex.aluminum_panel",
            "material_law_id": "material.flex.aluminum_panel",
            "chrono_class": "ChMaterialShellANCF / ChContinuumElastic",
            "density_kg_m3": "2700",
            "young_modulus_Pa": "7.0e10",
            "poisson_ratio": "0.33",
            "damping": "catalog_only",
            "section_area_m2": "",
            "section_Ixx_m4": "",
            "section_Iyy_m4": "",
            "thickness_m": "0.004",
            "layer_count": "1",
            "plasticity_model": "none_in_fixture",
            "source": source,
        }
    ]
    material_json = write_json(
        MATERIAL_LAW_MANIFEST_JSON,
        {"schema_id": "flex.material_law_manifest.v1", "run_id": RUN_ID, "source": source, "material_laws": material_rows},
    )

    bc_rows = [
        {
            "schema_id": "flex.boundary_condition_map.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "flex.boundary_attachment",
            "instance_id": "bc.panel_root_fixed",
            "mesh_id": "fea_mesh.rover_panel_demo",
            "boundary_condition_id": "bc.panel_root_fixed",
            "node_set": "root_edge_nodes",
            "attached_body_id": "vehicle.chassis",
            "constraint_class": "fixed_nodes_or_ChLinkPointFrame",
            "load_id": "",
            "frame": "body_REF",
            "local_xyz_m": "0.0,0.0,0.0",
            "dof_policy": "all translational/rotational DOF fixed",
            "source": source,
        },
        {
            "schema_id": "flex.boundary_condition_map.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "flex.boundary_attachment",
            "instance_id": "bc.sensor_payload_load",
            "mesh_id": "fea_mesh.rover_panel_demo",
            "boundary_condition_id": "bc.sensor_payload_load",
            "node_set": "payload_mount_nodes",
            "attached_body_id": "sensor.mount_payload",
            "constraint_class": "distributed_load_catalog",
            "load_id": "load.sensor_payload_weight",
            "frame": "body_REF",
            "local_xyz_m": "0.35,0.0,0.12",
            "dof_policy": "force only; live FEA run must export reaction/deformation",
            "source": source,
        },
    ]
    bc_csv = write_csv(BOUNDARY_CONDITION_MAP_CSV, list(bc_rows[0].keys()), bc_rows)
    bc_json = write_json(
        BOUNDARY_CONDITION_MAP_JSON,
        {"schema_id": "flex.boundary_condition_map.v1", "run_id": RUN_ID, "source": source, "boundary_conditions": bc_rows},
    )

    mode_rows = [
        {
            "schema_id": "flex.mode_frequency_table.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "flex.modal_reduction",
            "modal_basis_id": "modal_basis.panel_demo",
            "mode_id": "mode_001",
            "frequency_hz": "42.0",
            "damping_ratio": "0.020",
            "boundary_condition_id": "bc.panel_root_fixed",
            "reduction_validity": "catalog_fixture_only",
            "source": source,
        },
        {
            "schema_id": "flex.mode_frequency_table.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "flex.modal_reduction",
            "modal_basis_id": "modal_basis.panel_demo",
            "mode_id": "mode_002",
            "frequency_hz": "86.5",
            "damping_ratio": "0.020",
            "boundary_condition_id": "bc.panel_root_fixed",
            "reduction_validity": "catalog_fixture_only",
            "source": source,
        },
    ]
    mode_csv = write_csv(MODE_FREQUENCY_TABLE_CSV, list(mode_rows[0].keys()), mode_rows)

    modal_rows = [
        {
            "schema_id": "flex.modal_basis_manifest.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "flex.modal_reduction",
            "instance_id": "modal_basis.panel_demo",
            "modal_basis_id": "modal_basis.panel_demo",
            "source_model_hash": "",
            "reduction_method": "Craig-Bampton or eigenmode basis contract",
            "basis_vector_hash": "",
            "mode_count": "2",
            "boundary_dof_count": "catalog_only",
            "internal_dof_count": "catalog_only",
            "frequency_table_path": _rel(MODE_FREQUENCY_TABLE_CSV),
            "validity_note": "schema-only modal contract; live run must attach real eigenvectors/frequencies",
            "source": source,
        }
    ]
    modal_json = write_json(
        MODAL_BASIS_MANIFEST_JSON,
        {"schema_id": "flex.modal_basis_manifest.v1", "run_id": RUN_ID, "source": source, "modal_bases": modal_rows},
    )
    return [mesh_csv, mesh_json, count_csv, material_json, bc_csv, bc_json, mode_csv, modal_json]


def generate_model_asset_integration_manifests() -> list[Path]:
    source = "fallback_model_integration_schema_only"
    model_rows = [
        {
            "schema_id": "model.import_manifest.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "model.spec_resolver",
            "instance_id": "model.import.rover_vehicle_json",
            "model_import_id": "model.import.rover_vehicle_json",
            "source_format": "Chrono Vehicle JSON",
            "source_path": "not_bound_in_fallback_bundle",
            "source_hash": "",
            "raw_path": "not_bound_in_fallback_bundle",
            "raw_hash": "",
            "resolved_path": "",
            "resolved_hash": "",
            "path_base": "VehicleData or ChronoData",
            "import_status": "schema_only_not_executed",
            "owner_component_ids": "vehicle.model_spec;vehicle.chassis;vehicle.suspension;vehicle.tire_model",
            "linked_interface_rows": "",
            "unit_transform": "SI",
            "axis_transform": "Chrono vehicle ISO: X forward, Y left, Z up",
            "source_to_chrono_name_map": "chassis->vehicle.chassis;suspension->vehicle.suspension;tire->vehicle.tire_model",
            "missing_fields": "live JSON path/hash not available in fallback bundle",
            "fallback_behavior": "catalog contract only",
            "source": source,
        },
        {
            "schema_id": "model.import_manifest.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "model.spec_resolver",
            "instance_id": "model.import.runtime_yaml",
            "model_import_id": "model.import.runtime_yaml",
            "source_format": "Chrono parser YAML",
            "source_path": "not_bound_in_fallback_bundle",
            "source_hash": "",
            "raw_path": "not_bound_in_fallback_bundle",
            "raw_hash": "",
            "resolved_path": "",
            "resolved_hash": "",
            "path_base": "ChronoData or repo-relative YAML",
            "import_status": "schema_only_not_executed",
            "owner_component_ids": "runtime.config;model.spec_resolver",
            "linked_interface_rows": "",
            "unit_transform": "YAML-declared units normalized to Chrono SI",
            "axis_transform": "source frame to Chrono world frame must be recorded",
            "source_to_chrono_name_map": "yaml key path->runtime component id",
            "missing_fields": "YAML file not executed in fallback bundle",
            "fallback_behavior": "catalog contract only",
            "source": source,
        },
        {
            "schema_id": "model.import_manifest.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "model.urdf_import",
            "instance_id": "model.import.robot_urdf",
            "model_import_id": "model.import.robot_urdf",
            "source_format": "URDF",
            "source_path": "not_bound_in_fallback_bundle",
            "source_hash": "",
            "raw_path": "not_bound_in_fallback_bundle",
            "raw_hash": "",
            "resolved_path": "",
            "resolved_hash": "",
            "path_base": "ChronoData/robot or external URDF directory",
            "import_status": "schema_only_not_executed",
            "owner_component_ids": "model.urdf_import;core.body;core.link_constraint",
            "linked_interface_rows": "",
            "unit_transform": "URDF meters/radians to Chrono SI",
            "axis_transform": "URDF base_link to Chrono world frame must be recorded",
            "source_to_chrono_name_map": "link->ChBody;joint->ChLink",
            "missing_fields": "URDF file not executed in fallback bundle",
            "fallback_behavior": "catalog contract only",
            "source": source,
        },
    ]
    model_json = write_json(
        MODEL_IMPORT_MANIFEST_JSON,
        {"schema_id": "model.import_manifest.v1", "run_id": RUN_ID, "source": source, "model_imports": model_rows},
    )

    asset_rows = [
        {
            "schema_id": "model.asset_manifest.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "model.spec_resolver",
            "instance_id": "asset.vehicle_json",
            "asset_id": "asset.vehicle_json",
            "owner_component_id": "vehicle.model_spec",
            "asset_role": "source_config",
            "path_base": "chrono_build/data/vehicle",
            "asset_path": "not_bound_in_fallback_bundle",
            "asset_hash": "",
            "asset_type": "json",
            "fallback_behavior": "schema-only placeholder",
            "source": source,
        },
        {
            "schema_id": "model.asset_manifest.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "asset.cad_step",
            "instance_id": "asset.cad_step_proxy",
            "asset_id": "asset.cad.step_proxy",
            "owner_component_id": "asset.cad_step",
            "asset_role": "cad_source",
            "path_base": "project CAD directory",
            "asset_path": "not_bound_in_fallback_bundle",
            "asset_hash": "",
            "asset_type": "step",
            "fallback_behavior": "named shape hierarchy recorded in cad_shape_manifest",
            "source": source,
        },
        {
            "schema_id": "model.asset_manifest.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "integration.fmi",
            "instance_id": "asset.fmu.catalog_slot",
            "asset_id": "asset.fmu.catalog_slot",
            "owner_component_id": "integration.fmi",
            "asset_role": "external_model_binary",
            "path_base": "external FMU directory",
            "asset_path": "not_bound_in_fallback_bundle",
            "asset_hash": "",
            "asset_type": "fmu",
            "fallback_behavior": "variables mapped without executing FMU",
            "source": source,
        },
        {
            "schema_id": "model.asset_manifest.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "vehicle.robot_assets",
            "instance_id": "asset.vehicle.hmmwv_vsg_visual",
            "asset_id": "asset.vehicle.hmmwv_vsg_visual",
            "owner_component_id": "vehicle.robot_assets",
            "asset_role": "built_in_vehicle_visual_asset",
            "path_base": "ChronoData vehicle/hmmwv",
            "asset_path": "images/renders/chrono_builtin_wheeled_vehicle_assets.png",
            "asset_hash": _sha256(ROOT / "images/renders/chrono_builtin_wheeled_vehicle_assets.png") if (ROOT / "images/renders/chrono_builtin_wheeled_vehicle_assets.png").exists() else "",
            "asset_type": "vsg_capture_png",
            "fallback_behavior": "VSG visual asset capture; fallback is explicit OBJ preview if capture unavailable",
            "source": _vehicle_vsg_capture_row("images/renders/chrono_builtin_wheeled_vehicle_assets.png").get("source", source),
        },
        {
            "schema_id": "model.asset_manifest.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "vehicle.robot_assets",
            "instance_id": "asset.vehicle.m113_vsg_visual",
            "asset_id": "asset.vehicle.m113_vsg_visual",
            "owner_component_id": "vehicle.robot_assets",
            "asset_role": "built_in_vehicle_visual_asset",
            "path_base": "ChronoData vehicle/M113",
            "asset_path": "images/renders/chrono_builtin_tracked_vehicle_assets.png",
            "asset_hash": _sha256(ROOT / "images/renders/chrono_builtin_tracked_vehicle_assets.png") if (ROOT / "images/renders/chrono_builtin_tracked_vehicle_assets.png").exists() else "",
            "asset_type": "vsg_capture_png",
            "fallback_behavior": "VSG visual asset capture; fallback is explicit OBJ preview if capture unavailable",
            "source": _vehicle_vsg_capture_row("images/renders/chrono_builtin_tracked_vehicle_assets.png").get("source", source),
        },
        {
            "schema_id": "model.asset_manifest.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "vehicle.robot_assets",
            "instance_id": "asset.robot.viper_vsg_visual",
            "asset_id": "asset.robot.viper_vsg_visual",
            "owner_component_id": "vehicle.robot_assets",
            "asset_role": "built_in_robot_visual_asset",
            "path_base": "ChronoData robot/viper",
            "asset_path": "images/renders/chrono_viper_vsg_capture.png",
            "asset_hash": _sha256(ROOT / "images/renders/chrono_viper_vsg_capture.png") if (ROOT / "images/renders/chrono_viper_vsg_capture.png").exists() else "",
            "asset_type": "vsg_capture_png",
            "fallback_behavior": "VSG robot capture; fallback is explicit robot asset preview if capture unavailable",
            "source": _robot_vsg_capture_row("images/renders/chrono_viper_vsg_capture.png").get("source", source),
        },
        {
            "schema_id": "model.asset_manifest.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "vehicle.robot_assets",
            "instance_id": "asset.robot.curiosity_vsg_visual",
            "asset_id": "asset.robot.curiosity_vsg_visual",
            "owner_component_id": "vehicle.robot_assets",
            "asset_role": "built_in_robot_visual_asset",
            "path_base": "ChronoData robot/curiosity",
            "asset_path": "images/renders/chrono_curiosity_vsg_capture.png",
            "asset_hash": _sha256(ROOT / "images/renders/chrono_curiosity_vsg_capture.png") if (ROOT / "images/renders/chrono_curiosity_vsg_capture.png").exists() else "",
            "asset_type": "vsg_capture_png",
            "fallback_behavior": "VSG robot capture; fallback is explicit robot asset preview if capture unavailable",
            "source": _robot_vsg_capture_row("images/renders/chrono_curiosity_vsg_capture.png").get("source", source),
        },
    ]
    asset_csv = write_csv(ASSET_MANIFEST_CSV, list(asset_rows[0].keys()), asset_rows)
    asset_json = write_json(
        ASSET_MANIFEST_JSON,
        {"schema_id": "model.asset_manifest.v1", "run_id": RUN_ID, "source": source, "assets": asset_rows},
    )

    cad_rows = [
        {
            "schema_id": "asset.cad_shape_manifest.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "asset.cad_step",
            "instance_id": "cad_shape.chassis_proxy",
            "cad_shape_id": "cad_shape.chassis_proxy",
            "parent_shape_id": "",
            "shape_name": "chassis_proxy",
            "step_source_path": "not_bound_in_fallback_bundle",
            "step_source_hash": "",
            "tessellation_chord_tol_m": "0.002",
            "tessellation_angle_tol_deg": "12",
            "mass_inertia_source": "computed_or_external_required",
            "collision_proxy_policy": "use primitive/convex proxy; never raw decorative CAD for collision without review",
            "source": source,
        }
    ]
    cad_csv = write_csv(CAD_SHAPE_MANIFEST_CSV, list(cad_rows[0].keys()), cad_rows)
    cad_json = write_json(
        CAD_SHAPE_MANIFEST_JSON,
        {"schema_id": "asset.cad_shape_manifest.v1", "run_id": RUN_ID, "source": source, "cad_shapes": cad_rows},
    )

    interface_rows = [
        {
            "schema_id": "integration.external_interface_map.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "integration.fmi",
            "instance_id": "external_interface.fmu_throttle",
            "external_component_id": "FMU.vehicle_controller",
            "source_entity": "throttle_cmd",
            "chrono_component_id": "core.function_input",
            "chrono_item_name": "DriverInputs.m_throttle",
            "field": "throttle",
            "direction": "external_to_chrono",
            "unit": "normalized",
            "source_frame": "",
            "chrono_frame": "",
            "transform": "identity_scalar",
            "rate_hz": "50",
            "validation_artifact": _rel(SYNC_EXCHANGE_LOG_CSV),
            "source": source,
        },
        {
            "schema_id": "integration.external_interface_map.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "integration.ros",
            "instance_id": "external_interface.ros_odometry",
            "external_component_id": "ROS.topic./chrono/odom",
            "source_entity": "nav_msgs/Odometry.pose_twist",
            "chrono_component_id": "vehicle.chassis",
            "chrono_item_name": "vehicle.chassis",
            "field": "pose_twist",
            "direction": "chrono_to_external",
            "unit": "SI",
            "source_frame": "chrono_world_X_forward_Y_left_Z_up",
            "chrono_frame": "world_X_forward_Y_left_Z_up",
            "transform": "identity_pose_twist",
            "rate_hz": "50",
            "validation_artifact": _rel(SYNC_EXCHANGE_LOG_CSV),
            "source": source,
        },
        {
            "schema_id": "integration.external_interface_map.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "integration.vehicle_cosim",
            "instance_id": "external_interface.vehicle_cosim_terrain_force",
            "external_component_id": "cosim_node.terrain",
            "source_entity": "terrain_force",
            "chrono_component_id": "vehicle.wheel",
            "chrono_item_name": "wheel spindle state / tire force exchange",
            "field": "terrain_force",
            "direction": "bidirectional",
            "unit": "N",
            "source_frame": "terrain_node_frame",
            "chrono_frame": "wheel_spindle_frame",
            "transform": "force_vector_frame_transform_required_in_live_run",
            "rate_hz": "1000",
            "validation_artifact": _rel(SYNC_EXCHANGE_LOG_CSV),
            "source": source,
        },
        {
            "schema_id": "integration.external_interface_map.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "integration.synchrono",
            "instance_id": "external_interface.synchrono_agent_state",
            "external_component_id": "synchrono.agent.rover_001",
            "source_entity": "agent_state_packet",
            "chrono_component_id": "vehicle.chassis",
            "chrono_item_name": "synchronized agent state",
            "field": "pose_velocity_control_packet",
            "direction": "bidirectional",
            "unit": "SI",
            "source_frame": "Synchrono world/GPS projection",
            "chrono_frame": "Chrono world X forward Y left Z up",
            "transform": "gps_world_projection_required_in_live_run",
            "rate_hz": "50",
            "validation_artifact": _rel(SYNC_EXCHANGE_LOG_CSV),
            "source": source,
        },
    ]
    interface_csv = write_csv(EXTERNAL_INTERFACE_MAP_CSV, list(interface_rows[0].keys()), interface_rows)
    interface_json = write_json(
        EXTERNAL_INTERFACE_MAP_JSON,
        {"schema_id": "integration.external_interface_map.v1", "run_id": RUN_ID, "source": source, "external_interfaces": interface_rows},
    )

    sync_rows = [
        {
            "schema_id": "integration.sync_contract.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "integration.fmi",
            "instance_id": "sync.fmi_controller",
            "time_source": "Chrono master clock",
            "chrono_dt_s": "0.002",
            "external_dt_s": "0.020",
            "exchange_order": "read external command -> Synchronize -> Advance -> publish state",
            "hold_policy": "zero_order_hold",
            "lag_policy": "timestamp and reject stale frame",
            "hold_or_lag_policy": "zero_order_hold; timestamp and reject stale frame",
            "timeout_s": "0.100",
            "drop_retry_policy": "drop late external sample; continue with last valid command",
            "clock_skew_tolerance": "0.005",
            "message_count": "0",
            "dropped_count": "0",
            "last_status": "schema_only_not_executed",
            "source": source,
        },
        {
            "schema_id": "integration.sync_contract.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "integration.ros",
            "instance_id": "sync.ros_bridge",
            "time_source": "ROS /clock bridged to Chrono master clock",
            "chrono_dt_s": "0.002",
            "external_dt_s": "0.020",
            "exchange_order": "publish /clock and state -> receive command topic -> apply next Chrono step",
            "hold_policy": "last valid subscribed command",
            "lag_policy": "timestamp and mark stale ROS message",
            "hold_or_lag_policy": "last valid command; timestamp and mark stale ROS message",
            "timeout_s": "0.100",
            "drop_retry_policy": "drop stale topic sample; publish dropped_count in live log",
            "clock_skew_tolerance": "0.010",
            "message_count": "0",
            "dropped_count": "0",
            "last_status": "schema_only_not_executed",
            "source": source,
        },
        {
            "schema_id": "integration.sync_contract.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "integration.vehicle_cosim",
            "instance_id": "sync.vehicle_cosim",
            "time_source": "co-simulation barrier",
            "chrono_dt_s": "0.001",
            "external_dt_s": "0.001",
            "exchange_order": "MBS state -> tire/terrain force exchange -> barrier",
            "hold_policy": "barrier_synchronized",
            "lag_policy": "rank timeout failure",
            "hold_or_lag_policy": "barrier_synchronized; rank timeout failure",
            "timeout_s": "1.000",
            "drop_retry_policy": "fail closed; no silent extrapolation",
            "clock_skew_tolerance": "0.001",
            "message_count": "0",
            "dropped_count": "0",
            "last_status": "schema_only_not_executed",
            "source": source,
        },
        {
            "schema_id": "integration.sync_contract.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "integration.synchrono",
            "instance_id": "sync.synchrono_agent",
            "time_source": "Synchrono agent heartbeat / Chrono master clock",
            "chrono_dt_s": "0.002",
            "external_dt_s": "0.020",
            "exchange_order": "pack local agent state -> exchange network packet -> apply remote state/control",
            "hold_policy": "hold last remote agent state with packet timestamp",
            "lag_policy": "reject packet beyond heartbeat tolerance",
            "hold_or_lag_policy": "hold last remote state; reject packet beyond heartbeat tolerance",
            "timeout_s": "0.200",
            "drop_retry_policy": "count dropped packet; no contact-force extrapolation",
            "clock_skew_tolerance": "0.020",
            "message_count": "0",
            "dropped_count": "0",
            "last_status": "schema_only_not_executed",
            "source": source,
        },
    ]
    sync_json = write_json(
        SYNC_CONTRACT_JSON,
        {"schema_id": "integration.sync_contract.v1", "run_id": RUN_ID, "source": source, "sync_contracts": sync_rows},
    )

    exchange_rows = [
        {
            "schema_id": "integration.sync_exchange_log.v1",
            "run_id": RUN_ID,
            "sample_index": "0",
            "time_s": "0.000",
            "catalog_component_id": "integration.fmi",
            "exchange_id": "exchange.fmi_throttle_000000",
            "direction": "external_to_chrono",
            "chrono_component_id": "core.function_input",
            "external_variable": "throttle_cmd",
            "value": "0.450",
            "unit": "normalized",
            "status": "schema_only_not_executed",
            "source": source,
        },
        {
            "schema_id": "integration.sync_exchange_log.v1",
            "run_id": RUN_ID,
            "sample_index": "0",
            "time_s": "0.000",
            "catalog_component_id": "integration.ros",
            "exchange_id": "exchange.ros_odom_000000",
            "direction": "chrono_to_external",
            "chrono_component_id": "vehicle.chassis",
            "external_variable": "/chrono/odom",
            "value": "pose_twist_row",
            "unit": "SI",
            "status": "schema_only_not_executed",
            "source": source,
        },
        {
            "schema_id": "integration.sync_exchange_log.v1",
            "run_id": RUN_ID,
            "sample_index": "0",
            "time_s": "0.000",
            "catalog_component_id": "integration.vehicle_cosim",
            "exchange_id": "exchange.vehicle_cosim_barrier_000000",
            "direction": "bidirectional",
            "chrono_component_id": "vehicle.wheel",
            "external_variable": "terrain_force",
            "value": "barrier_schema_row",
            "unit": "N",
            "status": "schema_only_not_executed",
            "source": source,
        },
        {
            "schema_id": "integration.sync_exchange_log.v1",
            "run_id": RUN_ID,
            "sample_index": "0",
            "time_s": "0.000",
            "catalog_component_id": "integration.synchrono",
            "exchange_id": "exchange.synchrono_agent_000000",
            "direction": "bidirectional",
            "chrono_component_id": "vehicle.chassis",
            "external_variable": "agent_state_packet",
            "value": "agent_state_schema_row",
            "unit": "SI",
            "status": "schema_only_not_executed",
            "source": source,
        },
    ]
    exchange_csv = write_csv(SYNC_EXCHANGE_LOG_CSV, list(exchange_rows[0].keys()), exchange_rows)

    fmu_rows = [
        {
            "schema_id": "integration.fmu_variable_map.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "integration.fmi",
            "instance_id": "fmu.variable.throttle_cmd",
            "fmu_variable": "throttle_cmd",
            "causality": "input",
            "unit": "1",
            "fmi_version": "2.0_or_3.0",
            "step_size_s": "0.020",
            "chrono_component_id": "core.function_input",
            "chrono_field": "throttle",
            "direction": "external_to_chrono",
            "source": source,
        },
        {
            "schema_id": "integration.fmu_variable_map.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "integration.fmi",
            "instance_id": "fmu.variable.vehicle_speed",
            "fmu_variable": "vehicle_speed",
            "causality": "output",
            "unit": "m/s",
            "fmi_version": "2.0_or_3.0",
            "step_size_s": "0.020",
            "chrono_component_id": "vehicle.chassis",
            "chrono_field": "speed",
            "direction": "chrono_to_external",
            "source": source,
        },
    ]
    fmu_csv = write_csv(FMU_VARIABLE_MAP_CSV, list(fmu_rows[0].keys()), fmu_rows)
    fmu_json = write_json(
        FMU_VARIABLE_MAP_JSON,
        {"schema_id": "integration.fmu_variable_map.v1", "run_id": RUN_ID, "source": source, "fmu_variables": fmu_rows},
    )

    ros_rows = [
        {
            "schema_id": "integration.ros_topic_handler_manifest.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "integration.ros",
            "instance_id": "ros.topic.clock",
            "topic": "/clock",
            "handler_class": "ChROSClockHandler",
            "message_type": "rosgraph_msgs/Clock",
            "direction": "publish",
            "frame_id": "",
            "update_rate_hz": "50",
            "chrono_component_ids": "runtime.system",
            "source": source,
        },
        {
            "schema_id": "integration.ros_topic_handler_manifest.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "integration.ros",
            "instance_id": "ros.topic.driver_inputs",
            "topic": "/cmd/driver_inputs",
            "handler_class": "custom_driver_input_handler",
            "message_type": "chrono_msgs/DriverInputs",
            "direction": "subscribe",
            "frame_id": "base_link",
            "update_rate_hz": "50",
            "chrono_component_ids": "core.function_input",
            "source": source,
        },
    ]
    ros_csv = write_csv(ROS_TOPIC_HANDLER_MANIFEST_CSV, list(ros_rows[0].keys()), ros_rows)
    ros_json = write_json(
        ROS_TOPIC_HANDLER_MANIFEST_JSON,
        {"schema_id": "integration.ros_topic_handler_manifest.v1", "run_id": RUN_ID, "source": source, "ros_topics": ros_rows},
    )

    cosim_rows = [
        {
            "schema_id": "integration.vehicle_cosim_node_manifest.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "integration.vehicle_cosim",
            "instance_id": "cosim_node.mbs_rover",
            "node_role": "MBS",
            "rank_or_process_id": "0",
            "exchanged_variables": "wheel_state;terrain_force;tire_force",
            "sync_timestep_s": "0.001",
            "body_or_subsystem_ids": "vehicle.chassis;vehicle.axle;vehicle.wheel",
            "source": source,
        },
        {
            "schema_id": "integration.vehicle_cosim_node_manifest.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "integration.vehicle_cosim",
            "instance_id": "cosim_node.terrain",
            "node_role": "Terrain",
            "rank_or_process_id": "1",
            "exchanged_variables": "terrain_height;terrain_force;contact_patch",
            "sync_timestep_s": "0.001",
            "body_or_subsystem_ids": "terrain.core_ground;terrain.scm",
            "source": source,
        },
    ]
    cosim_json = write_json(
        VEHICLE_COSIM_NODE_MANIFEST_JSON,
        {"schema_id": "integration.vehicle_cosim_node_manifest.v1", "run_id": RUN_ID, "source": source, "cosim_nodes": cosim_rows},
    )

    synchrono_rows = [
        {
            "schema_id": "integration.synchrono_agent_manifest.v1",
            "run_id": RUN_ID,
            "catalog_component_id": "integration.synchrono",
            "instance_id": "synchrono.agent.rover_001",
            "agent_id": "rover_001",
            "communication_backend": "DDS/MPI catalog slot",
            "synchronization_period_s": "0.020",
            "world_frame": "Chrono world X forward Y left Z up",
            "gps_frame": "lat/lon/alt ENU projection required in live run",
            "packet_timing_policy": "timestamped state/control packets",
            "owned_component_ids": "vehicle.chassis;sensor.manager;core.function_input",
            "source": source,
        }
    ]
    synchrono_json = write_json(
        SYNCHRONO_AGENT_MANIFEST_JSON,
        {"schema_id": "integration.synchrono_agent_manifest.v1", "run_id": RUN_ID, "source": source, "synchrono_agents": synchrono_rows},
    )

    return [
        model_json,
        asset_csv,
        asset_json,
        cad_csv,
        cad_json,
        interface_csv,
        interface_json,
        sync_json,
        exchange_csv,
        fmu_csv,
        fmu_json,
        ros_csv,
        ros_json,
        cosim_json,
        synchrono_json,
    ]


def _artifact_type(rel_path: str) -> str:
    if rel_path.endswith(".csv"):
        return "csv"
    if rel_path.endswith(".json"):
        return "json"
    if rel_path.endswith(".png") and rel_path.startswith("images/graphs/"):
        return "graph_png"
    if rel_path.endswith(".png") and rel_path.startswith("images/mermaid_rendered/"):
        return "mermaid_png"
    if rel_path.endswith(".mmd"):
        return "mermaid_source"
    if rel_path.endswith(".png") and rel_path.startswith("images/renders/"):
        return "render_png"
    if rel_path.startswith("outputs/raw/"):
        return "raw_debug"
    return Path(rel_path).suffix.lstrip(".") or "file"


def _robot_vsg_capture_available() -> bool:
    payload = _robot_vsg_capture_payload()
    return bool(payload.get("composite_available")) and payload.get("source") == "pychrono_vsg_capture"


def _evidence_level(rel_path: str, metadata: dict[str, str]) -> str:
    source = metadata.get("source", "")
    if _is_vsg_vehicle_asset(rel_path):
        return "pychrono_vsg_capture"
    if rel_path in {
        "images/renders/chrono_builtin_robot_rover_assets.png",
        "images/renders/chrono_viper_vsg_capture.png",
        "images/renders/chrono_curiosity_vsg_capture.png",
    } and _robot_vsg_capture_available():
        return "pychrono_vsg_capture"
    if source == "pychrono_vsg_capture":
        return "pychrono_vsg_capture"
    if rel_path.startswith("images/renders/"):
        return "concept_render"
    if rel_path.startswith("images/mermaid_rendered/"):
        return "rendered_mermaid"
    if rel_path.startswith("images/graphs/"):
        return "fallback_or_csv_derived_graph"
    if rel_path.startswith("outputs/raw/"):
        return "raw_debug_artifact"
    if "fallback" in source or "unavailable" in source or "schema_only" in source:
        return "fallback_schema_probe"
    if source == "pychrono" or source.startswith("pychrono_live"):
        return "pychrono_live_sim"
    return "generated_report_artifact"


def _manifest_targets() -> list[Path]:
    targets: list[Path] = []
    for base in (ROOT / "images" / "renders", ROOT / "images" / "graphs", ROOT / "images" / "mermaid_rendered", OUTPUT_CSV, OUTPUT_JSON, OUTPUT_RAW):
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and _rel(path) not in MANIFEST_OUTPUTS:
                targets.append(path)
    return sorted(targets, key=_rel)


def build_manifest_rows() -> list[dict[str, str]]:
    producer_map = _producer_map_from_readme()
    rows: list[dict[str, str]] = []
    for path in _manifest_targets():
        rel_path = _rel(path)
        graph_input = GRAPH_INPUTS.get(rel_path, "")
        if path.suffix in (".csv", ".json"):
            metadata = _metadata_for_path(path)
        elif graph_input and (ROOT / graph_input).exists():
            metadata = _read_csv_metadata(ROOT / graph_input)
        elif rel_path.startswith("images/renders/") and (_is_vsg_robot_asset(rel_path) or _is_vsg_vehicle_asset(rel_path)):
            metadata = {"schema_id": "visual.render_manifest.v1", "source": "pychrono_vsg_capture", "row_count": ""}
        else:
            metadata = {"schema_id": "", "source": "", "row_count": ""}
        graph_details = GRAPH_DETAILS.get(rel_path, {"axis_units": "", "smoothing_policy": "", "event_markers": ""})
        producer_script = CSV_PRODUCERS.get(rel_path, producer_map.get(rel_path, ""))
        input_path = graph_input or producer_script
        input_hash = _sha256(ROOT / input_path) if input_path and (ROOT / input_path).exists() else ""
        producer_hash = _sha256(ROOT / producer_script) if producer_script and (ROOT / producer_script).exists() else ""
        rows.append(
            {
                "manifest_schema_id": MANIFEST_SCHEMA_ID,
                "run_id": RUN_ID,
                "artifact_path": rel_path,
                "artifact_type": _artifact_type(rel_path),
                "producer_script": producer_script,
                "producer_hash": producer_hash,
                "input_path": input_path,
                "input_hash": input_hash,
                "artifact_hash": _sha256(path),
                "created_time": _mtime_utc(path),
                "byte_size": str(path.stat().st_size),
                "schema_id": metadata["schema_id"],
                "source": metadata["source"],
                "child_source_values": metadata.get("child_source_values", ""),
                "row_count": metadata["row_count"],
                "axis_units": graph_details["axis_units"],
                "smoothing_policy": graph_details["smoothing_policy"],
                "event_markers": graph_details["event_markers"],
                "dpi": "180" if rel_path.startswith(("images/graphs/", "images/renders/")) and rel_path.endswith(".png") else "",
                "figsize": "see producer_script" if rel_path.startswith(("images/graphs/", "images/renders/")) and rel_path.endswith(".png") else "",
                "backend": "matplotlib Agg" if rel_path.startswith("images/graphs/") and rel_path.endswith(".png") else "",
                "evidence_level": _evidence_level(rel_path, metadata),
            }
        )
    return rows


def _terrain_component_ids_from_manifests() -> list[str]:
    ids: set[str] = set()
    json_targets = [
        (OUTPUT_JSON / "terrain_component_manifest.json", "terrain_components"),
        (OUTPUT_JSON / "terrain_patch_manifest.json", "patches"),
        (OUTPUT_JSON / "terrain_material_region_map.json", "material_regions"),
        (OUTPUT_JSON / "terrain_deformable_domain_manifest.json", "domains"),
    ]
    for path, list_key in json_targets:
        if not path.exists():
            continue
        try:
            payload = json.load(path.open(encoding="utf-8"))
        except Exception:
            continue
        for row in payload.get(list_key, []):
            if isinstance(row, dict) and row.get("terrain_component_id"):
                ids.add(str(row["terrain_component_id"]))
    return sorted(ids)


def _vsg_environment_metadata() -> dict:
    robot_payload = _robot_vsg_capture_payload()
    vehicle_payload = _vehicle_vsg_capture_payload()
    robot_captures = [row for row in robot_payload.get("captures", []) if isinstance(row, dict)]
    vehicle_captures = [row for row in vehicle_payload.get("captures", []) if isinstance(row, dict)]
    captures = robot_captures + vehicle_captures
    available = any(str(row.get("source", "")) == "pychrono_vsg_capture" and str(row.get("available", "")) == "true" for row in captures)
    return {
        "available": available,
        "source": ";".join(sorted({str(row.get("source", "")) for row in captures if row.get("source")})),
        "schema_id": ";".join(
            value
            for value in (str(robot_payload.get("schema_id", "")), str(vehicle_payload.get("schema_id", "")))
            if value
        ),
        "build_roots": sorted({str(row.get("build_root", "")) for row in captures if row.get("build_root")}),
        "chrono_data_paths": sorted({str(row.get("chrono_data_path", "")) for row in captures if row.get("chrono_data_path")}),
        "chrono_versions": sorted({str(row.get("chrono_version", "")) for row in captures if row.get("chrono_version")}),
        "capture_count": len(captures),
        "robot_capture_count": len(robot_captures),
        "vehicle_visual_asset_capture_count": len(vehicle_captures),
        "composite_artifact_path": robot_payload.get("composite_artifact_path", ""),
        "composite_sha256": robot_payload.get("composite_sha256", ""),
    }


def _sensor_capability_metadata() -> dict:
    manifest = OUTPUT_JSON / "sensor_module_capability_manifest.json"
    if not manifest.exists():
        return {
            "available": False,
            "source": "sensor_capability_manifest_missing",
            "live_sensor_output_allowed": False,
            "live_output_blocker": "outputs/json/sensor_module_capability_manifest.json not generated",
            "capability_count": 0,
        }
    try:
        payload = json.load(manifest.open(encoding="utf-8"))
    except Exception as exc:
        return {
            "available": False,
            "source": "sensor_capability_manifest_unreadable",
            "live_sensor_output_allowed": False,
            "live_output_blocker": str(exc),
            "capability_count": 0,
        }
    return {
        "available": bool(payload.get("sensor_module_available")),
        "source": str(payload.get("source", "")),
        "live_sensor_output_allowed": bool(payload.get("live_sensor_output_allowed")),
        "live_output_blocker": str(payload.get("live_output_blocker", "")),
        "capability_count": len(payload.get("capabilities", [])) if isinstance(payload.get("capabilities"), list) else 0,
    }


def write_run_metadata(rows: list[dict[str, str]]) -> Path:
    evidence_counts = Counter(row["evidence_level"] for row in rows)
    artifact_type_counts = Counter(row["artifact_type"] for row in rows)
    sources = sorted({row["source"] for row in rows if row["source"]})
    chrono, error = try_import_chrono()
    vsg_environment = _vsg_environment_metadata()
    sensor_capability = _sensor_capability_metadata()
    terrain_component_ids = _terrain_component_ids_from_manifests() or ["terrain.core_ground", "terrain.heightmap_mesh"]
    csv_schemas = sorted({row["schema_id"] for row in rows if row["artifact_type"] == "csv" and row["schema_id"]})
    json_schemas = sorted({row["schema_id"] for row in rows if row["artifact_type"] == "json" and row["schema_id"]})
    all_schemas = sorted({row["schema_id"] for row in rows if row["schema_id"]} | {MANIFEST_SCHEMA_ID, RUN_METADATA_SCHEMA_ID})
    schema_counts = Counter(row["schema_id"] for row in rows if row["schema_id"])
    schema_counts.update([MANIFEST_SCHEMA_ID, RUN_METADATA_SCHEMA_ID])
    payload = {
        "run_id": RUN_ID,
        "schema_id": RUN_METADATA_SCHEMA_ID,
        "report_root": ROOT.as_posix(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "chrono_available": chrono is not None or bool(vsg_environment["available"]),
        "chrono_available_scope": "true if either host Python can import pychrono or a producer subprocess captured VSG evidence",
        "host_pychrono_available": chrono is not None,
        "host_chrono_import_error": "" if error is None else error,
        "chrono_import_error": "" if error is None else error,
        "chrono_version": getattr(chrono, "CHRONO_VERSION", "unknown") if chrono is not None else "",
        "chrono_build_hash": "",
        "enabled_modules": {
            "host_pychrono": chrono is not None,
            "vsg_capture_pychrono": bool(vsg_environment["available"]),
            "vsg3d": bool(vsg_environment["available"]),
            "sensor": bool(sensor_capability["available"]),
            "parsers": False,
            "cascade": False,
            "fmi": False,
            "ros": False,
            "vehicle_cosim": False,
            "synchrono": False,
            "modal": False,
            "fea": False,
        },
        "optional_module_availability": {
            "sensor": sensor_capability["source"],
            "parsers": "catalog_manifest_only_not_executed",
            "cascade": "catalog_manifest_only_not_executed",
            "fmi": "catalog_manifest_only_not_executed",
            "ros": "catalog_manifest_only_not_executed",
            "vehicle_cosim": "catalog_manifest_only_not_executed",
            "synchrono": "catalog_manifest_only_not_executed",
            "modal": "catalog_manifest_only_not_executed",
            "fea": "catalog_manifest_only_not_executed",
        },
        "producer_environments": {"vsg_capture": vsg_environment, "sensor_capability": sensor_capability},
        "dt_s": {"rover_vehicle_chassis_probe": 0.01, "terrain_contact_probe": 0.005, "collision_contact_probe": 0.005, "data_visualization_log": 0.02, "sensor_schema_schedule": 0.02},
        "solver": "fallback_or_default_ChSystemNSC",
        "solver_type": "fallback_or_default_iterative_nsc",
        "timestepper": "fallback_fixed_step; live runs must record ChTimestepper type",
        "contact_method": "NSC for PyChrono probes; deterministic fallback otherwise",
        "collision_system_type": "Bullet_or_fallback",
        "collision_backend": "Bullet_or_fallback",
        "thread_count_collision": "",
        "collision_envelope_m": "",
        "collision_margin_m": "",
        "recovery_speed_mps": "",
        "bounce_speed_mps": "",
        "gravity_mps2": [0.0, 0.0, -9.81],
        "gravity_axis": "Z-up world with negative z gravity",
        "gravity_setter_source": "ChSystem::SetGravitationalAcceleration in PyChrono probes; deterministic fallback otherwise",
        "terrain_component_ids": terrain_component_ids,
        "sensor_component_ids": ["sensor.manager", "sensor.layout", "sensor.output_writer"],
        "sensor_instance_ids": ["sensor.camera.front_rgb", "sensor.lidar.roof_xyzi", "sensor.gps.roof", "sensor.imu.roof"],
        "body_registry_summary": {
            "core_rover_smoke_probe": ["probe_ground", "probe_chassis", "probe_drive_wheel"],
            "collision_contact_probe": ["rover_body", "rigid_obstacle"],
            "terrain_contact_probe": ["sphere_probe", "terrain.core_ground"],
        },
        "seed": "deterministic analytic fallback; no random seed",
        "schema_ids_present": all_schemas,
        "csv_schema_ids_present": csv_schemas,
        "json_schema_ids_present": json_schemas,
        "schema_id_counts": dict(sorted(schema_counts.items())),
        "artifact_count": len(rows),
        "artifact_manifest_csv": _rel(MANIFEST_CSV),
        "artifact_manifest_json": _rel(MANIFEST_JSON),
        "artifact_type_counts": dict(sorted(artifact_type_counts.items())),
        "evidence_level_counts": dict(sorted(evidence_counts.items())),
        "source_values": sources,
        "live_chrono_evidence_present": any(row["evidence_level"] == "pychrono_live_sim" for row in rows),
        "vsg_capture_evidence_present": any(row["evidence_level"] == "pychrono_vsg_capture" for row in rows),
        "fallback_policy": "Generated report artifacts are valid for schema/catalog wiring; live Chrono validation must replace fallback sources.",
    }
    return write_json(RUN_METADATA, payload)


def generate_artifact_manifest() -> tuple[Path, Path, Path]:
    ensure_output_dirs()
    generate_render_manifest()
    generate_visual_asset_manifest()
    generate_chrono_output_database_manifest()
    generate_checkpoint_manifest()
    generate_gnuplot_plot_manifest()
    generate_offline_visual_export_manifest()
    generate_flex_fea_catalog_manifests()
    generate_model_asset_integration_manifests()
    generate_logger_timebase_manifest()
    generate_writer_backend_manifest()
    rows = build_manifest_rows()
    fieldnames = [
        "manifest_schema_id",
        "run_id",
        "artifact_path",
        "artifact_type",
        "producer_script",
        "producer_hash",
        "input_path",
        "input_hash",
        "artifact_hash",
        "created_time",
        "byte_size",
        "schema_id",
        "source",
        "child_source_values",
        "row_count",
        "axis_units",
        "smoothing_policy",
        "event_markers",
        "dpi",
        "figsize",
        "backend",
        "evidence_level",
    ]
    csv_path = write_csv(MANIFEST_CSV, fieldnames, rows)
    json_path = write_json(MANIFEST_JSON, {"schema_id": MANIFEST_SCHEMA_ID, "run_id": RUN_ID, "artifacts": rows})
    metadata_path = write_run_metadata(rows)
    return csv_path, json_path, metadata_path


def main() -> None:
    for path in generate_artifact_manifest():
        print(path)


if __name__ == "__main__":
    main()
