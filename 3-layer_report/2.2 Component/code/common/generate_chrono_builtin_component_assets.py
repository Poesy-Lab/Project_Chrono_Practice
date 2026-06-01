from __future__ import annotations

import math
import os
import subprocess
import sys
import textwrap
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Polygon, Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFont, ImageOps

from component_utils import IMAGES_RENDER, OUTPUT_JSON, ensure_output_dirs, save_figure, write_json
from component_utils import add_callout_3d


COMPONENT_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = Path(__file__).resolve().parents[4]
RUN_ID = "component_catalog_fallback_bundle"
CHRONO_DATA = PROJECT_ROOT / "chrono_build" / "data"
VSG_CAPTURE_MANIFEST = OUTPUT_JSON / "robot_vsg_capture_manifest.json"
VEHICLE_VSG_CAPTURE_MANIFEST = OUTPUT_JSON / "vehicle_vsg_capture_manifest.json"
VSG_WINDOW_SIZE = (1280, 800)
VSG_CAMERA_FOV_DEG = 46.0
VSG_CAPTURE_CONFIG = {
    "viper": {
        "robot_class": "pychrono.robot.Viper",
        "driver_class": "pychrono.robot.ViperDCMotorControl",
        "data_path_hint": "robot/viper",
        "camera_eye": (4.4, -4.2, 2.15),
        "camera_target": (0.0, 0.0, 0.62),
        "visible_component_ids": "vehicle.robot_assets;vehicle.chassis;vehicle.wheel;vehicle.steering;visual.runtime",
        "visible_robot_part_ids": "viper.body;viper.suspension;viper.wheels;viper.mast",
    },
    "curiosity": {
        "robot_class": "pychrono.robot.Curiosity",
        "driver_class": "pychrono.robot.CuriosityDCMotorControl",
        "data_path_hint": "robot/curiosity",
        "camera_eye": (4.2, -4.4, 2.35),
        "camera_target": (0.15, 0.0, 0.55),
        "visible_component_ids": "vehicle.robot_assets;vehicle.chassis;vehicle.wheel;vehicle.suspension;visual.runtime",
        "visible_robot_part_ids": "curiosity.body;curiosity.rocker_bogie;curiosity.wheels;curiosity.mast",
    },
}
VEHICLE_VSG_CAPTURE_CONFIG = {
    "hmmwv": {
        "artifact_name": "chrono_builtin_wheeled_vehicle_assets.png",
        "vehicle_family": "wheeled_vehicle",
        "vehicle_model": "HMMWV visual asset assembly",
        "chrono_class": "chrono.vehicle.HMMWV_Full visual assets via ChVisualModel",
        "data_path_hint": "vehicle/hmmwv",
        "camera_eye": (5.0, -6.0, 2.6),
        "camera_target": (0.0, 0.0, 0.45),
        "camera_fov_deg": "42.0",
        "visible_component_ids": "vehicle.robot_assets;vehicle.chassis;vehicle.wheel;vehicle.tire_model;visual.runtime",
        "visible_vehicle_part_ids": "hmmwv.chassis;hmmwv.rims;hmmwv.tires",
    },
    "m113": {
        "artifact_name": "chrono_builtin_tracked_vehicle_assets.png",
        "vehicle_family": "tracked_vehicle",
        "vehicle_model": "M113 visual asset assembly",
        "chrono_class": "chrono.vehicle.M113_Vehicle_SinglePin visual assets via ChVisualModel",
        "data_path_hint": "vehicle/M113",
        "camera_eye": (3.8, -6.2, 2.6),
        "camera_target": (-2.0, 0.0, 0.65),
        "camera_fov_deg": "42.0",
        "visible_component_ids": "vehicle.track_assembly;vehicle.track_shoe;vehicle.sprocket;vehicle.road_wheel;visual.runtime",
        "visible_vehicle_part_ids": "m113.chassis;m113.sprockets;m113.idlers;m113.road_wheels;m113.track_shoes",
    },
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _image_metadata(path: Path) -> dict[str, str]:
    if not path.exists():
        return {"image_width_px": "", "image_height_px": "", "image_sha256": ""}
    with Image.open(path) as image:
        width, height = image.size
    return {"image_width_px": str(width), "image_height_px": str(height), "image_sha256": _sha256(path)}


def _enhance_vsg_image(image: Image.Image) -> Image.Image:
    image = ImageOps.autocontrast(image.convert("RGB"), cutoff=1)
    image = ImageEnhance.Contrast(image).enhance(1.12)
    image = ImageEnhance.Brightness(image).enhance(1.04)
    return image


def _enhance_vsg_capture_file(path: Path) -> None:
    if path.exists():
        _enhance_vsg_image(Image.open(path)).save(path)


def _load_obj(path: Path, *, max_faces: int = 9000) -> tuple[np.ndarray, list[list[int]]]:
    vertices: list[list[float]] = []
    faces: list[list[int]] = []
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            if line.startswith("v "):
                _, x, y, z, *_ = line.split()
                vertices.append([float(x), float(y), float(z)])
            elif line.startswith("f "):
                indices = []
                for item in line.split()[1:]:
                    raw = item.split("/")[0]
                    if not raw:
                        continue
                    idx = int(raw)
                    indices.append(idx - 1 if idx > 0 else len(vertices) + idx)
                if len(indices) >= 3:
                    faces.append(indices)

    if len(faces) > max_faces:
        step = math.ceil(len(faces) / max_faces)
        faces = faces[::step]
    return np.asarray(vertices, dtype=float), faces


def _normalized(vertices: np.ndarray, *, center: tuple[float, float, float], size: float, rotate_z: float = 0.0) -> np.ndarray:
    mins = vertices.min(axis=0)
    maxs = vertices.max(axis=0)
    source_center = (mins + maxs) / 2.0
    extent = float(np.max(maxs - mins))
    scaled = (vertices - source_center) * (size / extent if extent > 0 else 1.0)

    if rotate_z:
        c = math.cos(rotate_z)
        s = math.sin(rotate_z)
        rot = np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])
        scaled = scaled @ rot.T

    return scaled + np.asarray(center, dtype=float)


def _add_obj(ax, rel_path: str, *, center, size: float, color: str, alpha: float = 0.90, rotate_z: float = 0.0, max_faces: int = 9000) -> None:
    path = CHRONO_DATA / rel_path
    vertices, faces = _load_obj(path, max_faces=max_faces)
    vertices = _normalized(vertices, center=center, size=size, rotate_z=rotate_z)
    polygons = [[vertices[idx] for idx in face] for face in faces]
    mesh = Poly3DCollection(polygons, facecolors=color, edgecolors="none", linewidths=0.0, alpha=alpha)
    ax.add_collection3d(mesh)


def _format_asset_ax(ax, *, xlim=(-1.7, 1.7), ylim=(-1.15, 1.15), zlim=(-0.55, 0.85), elev=22, azim=-48) -> None:
    ax.view_init(elev=elev, azim=azim)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_zlim(*zlim)
    ax.set_axis_off()
    try:
        ax.set_box_aspect((xlim[1] - xlim[0], ylim[1] - ylim[0], zlim[1] - zlim[0]))
    except Exception:
        pass


def _trim_white_margin(path: Path, *, margin: int = 36) -> Path:
    image = Image.open(path).convert("RGB")
    background = Image.new("RGB", image.size, (255, 255, 255))
    bbox = ImageChops.difference(image, background).getbbox()
    if bbox is None:
        return path

    left, upper, right, lower = bbox
    left = max(0, left - margin)
    upper = max(0, upper - margin)
    right = min(image.width, right + margin)
    lower = min(image.height, lower + margin)
    image.crop((left, upper, right, lower)).save(path)
    return path


def _chrono_vsg_env() -> tuple[dict[str, str], Path] | tuple[None, None]:
    candidates = [
        PROJECT_ROOT / "chrono_build_cuda129_sm120",
        PROJECT_ROOT / "chrono_build_vsg",
        PROJECT_ROOT / "chrono_build",
    ]
    for base in candidates:
        if not (base / "bin" / "pychrono" / "vsg3d.py").exists():
            continue
        env = os.environ.copy()
        env["PYTHONPATH"] = str(base / "bin") + os.pathsep + env.get("PYTHONPATH", "")
        env["LD_LIBRARY_PATH"] = str(base / "lib") + os.pathsep + env.get("LD_LIBRARY_PATH", "")
        return env, base
    return None, None


def _vsg_capture_code() -> str:
    return textwrap.dedent(
        r"""
        import sys
        from pathlib import Path

        import pychrono as chrono
        import pychrono.robot as robot
        from pychrono import vsg3d as vsg

        model = sys.argv[1]
        output = Path(sys.argv[2]).resolve()
        data_path = Path(sys.argv[3]).resolve()
        chrono.SetChronoDataPath(str(data_path) + "/")

        system = chrono.ChSystemNSC()
        system.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)
        system.SetGravitationalAcceleration(chrono.ChVector3d(0, 0, -9.81))
        chrono.ChCollisionModel.SetDefaultSuggestedEnvelope(0.0025)
        chrono.ChCollisionModel.SetDefaultSuggestedMargin(0.0025)

        ground_mat = chrono.ChContactMaterialNSC()
        ground = chrono.ChBodyEasyBox(12, 12, 0.25, 1000, True, True, ground_mat)
        ground.SetPos(chrono.ChVector3d(0, 0, -0.13))
        ground.SetFixed(True)
        ground.GetVisualShape(0).SetTexture(chrono.GetChronoDataFile("textures/concrete.jpg"), 20, 20)
        system.Add(ground)

        if model == "viper":
            driver = robot.ViperDCMotorControl()
            rover = robot.Viper(system)
            rover.SetDriver(driver)
            rover.Initialize(chrono.ChFramed(chrono.ChVector3d(0, 0, 0.5), chrono.ChQuaterniond(1, 0, 0, 0)))
            camera_pos = chrono.ChVector3d(4.4, -4.2, 2.15)
            camera_target = chrono.ChVector3d(0.0, 0.0, 0.62)
            title = "Chrono Robot VIPER VSG capture"
        elif model == "curiosity":
            driver = robot.CuriosityDCMotorControl()
            rover = robot.Curiosity(system)
            rover.SetDriver(driver)
            rover.Initialize(chrono.ChFramed(chrono.ChVector3d(0, 0, 0.3), chrono.ChQuaterniond(1, 0, 0, 0)))
            camera_pos = chrono.ChVector3d(4.2, -4.4, 2.35)
            camera_target = chrono.ChVector3d(0.15, 0.0, 0.55)
            title = "Chrono Robot Curiosity VSG capture"
        else:
            raise ValueError(model)

        vis = vsg.ChVisualSystemVSG()
        vis.AttachSystem(system)
        vis.SetWindowSize(1280, 800)
        vis.SetWindowTitle(title)
        vis.AddCamera(camera_pos, camera_target)
        vis.SetCameraAngleDeg(46.0)
        vis.SetLightDirection(1.5 * chrono.CH_PI_2, chrono.CH_PI_4)
        vis.EnableShadows()
        for call in (getattr(vis, "SetGuiVisibility", None), getattr(vis, "SetBaseGuiVisibility", None)):
            if call:
                call(False)
        if hasattr(vis, "HideLogo"):
            vis.HideLogo()
        vis.Initialize()

        for _ in range(8):
            rover.Update()
            vis.BeginScene()
            vis.Render()
            vis.EndScene()
            system.DoStepDynamics(1e-3)

        output.parent.mkdir(parents=True, exist_ok=True)
        vis.WriteImageToFile(str(output))
        vis.BeginScene()
        vis.Render()
        vis.EndScene()
        print(f"CHRONO_VERSION={getattr(chrono, 'CHRONO_VERSION', '') or 'unknown'}")
        print(output)
        """
    )


def _vehicle_vsg_capture_code() -> str:
    return textwrap.dedent(
        r"""
        import sys
        from pathlib import Path

        import pychrono.core as chrono
        import pychrono.vsg3d as vsg

        model = sys.argv[1]
        output = Path(sys.argv[2]).resolve()
        data_path = Path(sys.argv[3]).resolve()
        chrono.SetChronoDataPath(str(data_path) + "/")

        def mesh_shape(rel_path, color=None):
            mesh = chrono.ChTriangleMeshConnected.CreateFromWavefrontFile(chrono.GetChronoDataFile(rel_path), True, True)
            shape = chrono.ChVisualShapeTriangleMesh()
            shape.SetMesh(mesh)
            shape.SetName(rel_path)
            shape.SetMutable(False)
            if color is not None:
                shape.SetColor(chrono.ChColor(color[0], color[1], color[2]))
            return shape

        system = chrono.ChSystemNSC()
        vis = vsg.ChVisualSystemVSG()
        vis.AttachSystem(system)
        vis.SetCameraVertical(chrono.CameraVerticalDir_Z)
        vis.SetWindowSize(chrono.ChVector2i(1280, 800))
        vis.SetLightIntensity(1.0)
        vis.SetLightDirection(chrono.CH_PI_2, chrono.CH_PI_4)
        vis.EnableShadows()
        for call in (getattr(vis, "SetGuiVisibility", None), getattr(vis, "SetBaseGuiVisibility", None)):
            if call:
                call(False)
        if hasattr(vis, "HideLogo"):
            vis.HideLogo()

        visual_model = chrono.ChVisualModel()
        if model == "hmmwv":
            vis.SetWindowTitle("Chrono HMMWV visual asset VSG capture")
            vis.AddCamera(chrono.ChVector3d(5.0, -6.0, 2.6), chrono.ChVector3d(0.0, 0.0, 0.45))
            vis.SetCameraAngleDeg(42.0)
            wheel_positions = [
                chrono.ChVector3d(1.64, 0.910, -0.026),
                chrono.ChVector3d(1.64, -0.910, -0.026),
                chrono.ChVector3d(-1.64, 0.910, -0.026),
                chrono.ChVector3d(-1.64, -0.910, -0.026),
            ]
            chassis = mesh_shape("vehicle/hmmwv/hmmwv_chassis.obj")
            rim = mesh_shape("vehicle/hmmwv/hmmwv_rim.obj")
            tire_left = mesh_shape("vehicle/hmmwv/hmmwv_tire_left.obj")
            tire_right = mesh_shape("vehicle/hmmwv/hmmwv_tire_right.obj")
            visual_model.AddShape(chassis)
            for index, pos in enumerate(wheel_positions):
                visual_model.AddShape(rim, chrono.ChFramed(pos, chrono.QuatFromAngleZ(chrono.CH_PI * index)))
            for index, pos in enumerate(wheel_positions):
                tire = tire_left if index % 2 == 0 else tire_right
                visual_model.AddShape(tire, chrono.ChFramed(pos, chrono.QuatFromAngleZ(chrono.CH_PI * index)))
            vis.AddVisualModel(visual_model, chrono.ChFramed(chrono.ChVector3d(0, 0, 0), chrono.QUNIT))
        elif model == "m113":
            vis.SetWindowTitle("Chrono M113 visual asset VSG capture")
            vis.AddCamera(chrono.ChVector3d(3.8, -6.2, 2.6), chrono.ChVector3d(-2.0, 0.0, 0.65))
            vis.SetCameraAngleDeg(42.0)
            chassis = mesh_shape("vehicle/M113/meshes/Chassis.obj", (0.48, 0.50, 0.38))
            sprocket_right = mesh_shape("vehicle/M113/meshes/SprocketSinglePin_R.obj", (0.24, 0.25, 0.22))
            sprocket_left = mesh_shape("vehicle/M113/meshes/SprocketSinglePin_L.obj", (0.24, 0.25, 0.22))
            idler_right = mesh_shape("vehicle/M113/meshes/Idler_R.obj", (0.28, 0.29, 0.25))
            idler_left = mesh_shape("vehicle/M113/meshes/Idler_L.obj", (0.28, 0.29, 0.25))
            road_right = mesh_shape("vehicle/M113/meshes/Roller_R.obj", (0.18, 0.19, 0.18))
            road_left = mesh_shape("vehicle/M113/meshes/Roller_L.obj", (0.18, 0.19, 0.18))
            shoe = mesh_shape("vehicle/M113/meshes/TrackShoeSinglePin.obj", (0.08, 0.08, 0.07))
            visual_model.AddShape(chassis)
            for y, sprocket, idler, road in ((-1.0, sprocket_right, idler_right, road_right), (1.0, sprocket_left, idler_left, road_left)):
                visual_model.AddShape(sprocket, chrono.ChFramed(chrono.ChVector3d(0.0, y, 0.25), chrono.QUNIT))
                visual_model.AddShape(idler, chrono.ChFramed(chrono.ChVector3d(-4.0, y, 0.13), chrono.QUNIT))
                for x in (-0.740, -1.407, -2.074, -2.740, -3.407):
                    visual_model.AddShape(road, chrono.ChFramed(chrono.ChVector3d(x, y, 0.03), chrono.QUNIT))
                for x in (-3.75, -3.35, -2.95, -2.55, -2.15, -1.75, -1.35, -0.95, -0.55, -0.15):
                    visual_model.AddShape(shoe, chrono.ChFramed(chrono.ChVector3d(x, y, -0.33), chrono.QUNIT))
                for x in (-3.55, -3.05, -2.55, -2.05, -1.55, -1.05, -0.55):
                    visual_model.AddShape(shoe, chrono.ChFramed(chrono.ChVector3d(x, y, 0.58), chrono.QUNIT))
            vis.AddVisualModel(visual_model, chrono.ChFramed(chrono.ChVector3d(0, 0, 0), chrono.QUNIT))
        else:
            raise ValueError(model)

        vis.Initialize()
        for _ in range(3):
            vis.BeginScene()
            vis.Render()
            vis.EndScene()
        output.parent.mkdir(parents=True, exist_ok=True)
        vis.WriteImageToFile(str(output))
        vis.BeginScene()
        vis.Render()
        vis.EndScene()
        print(f"CHRONO_VERSION={getattr(chrono, 'CHRONO_VERSION', '') or 'unknown'}")
        print(output)
        """
    )


def _chrono_version_status(chrono_version: str, available: bool) -> str:
    if not available:
        return "capture_not_available"
    if chrono_version in {"", "unknown", "unknown_in_vsg_subprocess"}:
        return "version_accessor_unavailable_after_successful_capture"
    return "reported_by_subprocess"


def _capture_robot_vsg(model: str, output: Path) -> dict[str, str]:
    config = VSG_CAPTURE_CONFIG[model]
    env, build_root = _chrono_vsg_env()
    if env is None or build_root is None:
        return {
            "robot_model": model,
            "robot_class": config["robot_class"],
            "driver_class": config["driver_class"],
            "artifact_path": output.relative_to(COMPONENT_ROOT).as_posix(),
            "available": "false",
            "fallback": "true",
            "source": "fallback_vsg_pychrono_build_unavailable",
            "build_root": "",
            "chrono_data_path": "",
            "data_path_hint": config["data_path_hint"],
            "chrono_version": "",
            "chrono_version_status": "capture_not_available",
            "window_width_px": str(VSG_WINDOW_SIZE[0]),
            "window_height_px": str(VSG_WINDOW_SIZE[1]),
            "camera_eye": ",".join(f"{value:.3f}" for value in config["camera_eye"]),
            "camera_target": ",".join(f"{value:.3f}" for value in config["camera_target"]),
            "camera_fov_deg": f"{VSG_CAMERA_FOV_DEG:.1f}",
            "visible_component_ids": config["visible_component_ids"],
            "visible_robot_part_ids": config["visible_robot_part_ids"],
            "image_width_px": "",
            "image_height_px": "",
            "image_sha256": "",
            "fallback_reason": "no build with pychrono.vsg3d was found",
            "reason": "no build with pychrono.vsg3d was found",
        }

    cmd = [sys.executable, "-c", _vsg_capture_code(), model, str(output), str(build_root / "data")]
    result = subprocess.run(cmd, cwd=PROJECT_ROOT, env=env, text=True, capture_output=True, timeout=30, check=False)
    available = output.exists() and output.stat().st_size > 0 and result.returncode == 0
    if available:
        _enhance_vsg_capture_file(output)
    chrono_version = ""
    for line in result.stdout.splitlines():
        if line.startswith("CHRONO_VERSION="):
            chrono_version = line.split("=", 1)[1].strip()
            break
    if not chrono_version:
        chrono_version = "unknown_in_vsg_subprocess"
    fallback_reason = "" if available else (result.stderr.strip() or result.stdout.strip() or f"returncode={result.returncode}")
    return {
        "robot_model": model,
        "robot_class": config["robot_class"],
        "driver_class": config["driver_class"],
        "artifact_path": output.relative_to(COMPONENT_ROOT).as_posix(),
        "available": str(available).lower(),
        "fallback": str(not available).lower(),
        "source": "pychrono_vsg_capture" if available else "fallback_vsg_capture_unavailable",
        "build_root": build_root.relative_to(PROJECT_ROOT).as_posix(),
        "chrono_data_path": (build_root / "data").relative_to(PROJECT_ROOT).as_posix(),
        "data_path_hint": config["data_path_hint"],
        "chrono_version": chrono_version,
        "chrono_version_status": _chrono_version_status(chrono_version, available),
        "window_width_px": str(VSG_WINDOW_SIZE[0]),
        "window_height_px": str(VSG_WINDOW_SIZE[1]),
        "camera_eye": ",".join(f"{value:.3f}" for value in config["camera_eye"]),
        "camera_target": ",".join(f"{value:.3f}" for value in config["camera_target"]),
        "camera_fov_deg": f"{VSG_CAMERA_FOV_DEG:.1f}",
        "visible_component_ids": config["visible_component_ids"],
        "visible_robot_part_ids": config["visible_robot_part_ids"],
        **_image_metadata(output),
        "fallback_reason": fallback_reason,
        "reason": fallback_reason,
    }


def _vehicle_vsg_fallback_row(model: str, output: Path, source: str, fallback_reason: str) -> dict[str, str]:
    config = VEHICLE_VSG_CAPTURE_CONFIG[model]
    return {
        "vehicle_model": config["vehicle_model"],
        "vehicle_family": config["vehicle_family"],
        "chrono_class": config["chrono_class"],
        "artifact_path": output.relative_to(COMPONENT_ROOT).as_posix(),
        "available": "false",
        "fallback": "true",
        "source": source,
        "build_root": "",
        "chrono_data_path": "",
        "data_path_hint": config["data_path_hint"],
        "chrono_version": "",
        "chrono_version_status": "capture_not_available",
        "window_width_px": str(VSG_WINDOW_SIZE[0]),
        "window_height_px": str(VSG_WINDOW_SIZE[1]),
        "camera_eye": ",".join(f"{value:.3f}" for value in config["camera_eye"]),
        "camera_target": ",".join(f"{value:.3f}" for value in config["camera_target"]),
        "camera_fov_deg": config["camera_fov_deg"],
        "visible_component_ids": config["visible_component_ids"],
        "visible_vehicle_part_ids": config["visible_vehicle_part_ids"],
        **_image_metadata(output),
        "fallback_reason": fallback_reason,
        "reason": fallback_reason,
    }


def _capture_vehicle_vsg(model: str, output: Path) -> dict[str, str]:
    config = VEHICLE_VSG_CAPTURE_CONFIG[model]
    env, build_root = _chrono_vsg_env()
    if env is None or build_root is None:
        return _vehicle_vsg_fallback_row(model, output, "fallback_vsg_pychrono_build_unavailable", "no build with pychrono.vsg3d was found")

    cmd = [sys.executable, "-c", _vehicle_vsg_capture_code(), model, str(output), str(build_root / "data")]
    result = subprocess.run(cmd, cwd=PROJECT_ROOT, env=env, text=True, capture_output=True, timeout=45, check=False)
    available = output.exists() and output.stat().st_size > 0 and result.returncode == 0
    if available:
        _enhance_vsg_capture_file(output)
    chrono_version = ""
    for line in result.stdout.splitlines():
        if line.startswith("CHRONO_VERSION="):
            chrono_version = line.split("=", 1)[1].strip()
            break
    if not chrono_version:
        chrono_version = "unknown_in_vsg_subprocess"
    fallback_reason = "" if available else (result.stderr.strip() or result.stdout.strip() or f"returncode={result.returncode}")
    return {
        "vehicle_model": config["vehicle_model"],
        "vehicle_family": config["vehicle_family"],
        "chrono_class": config["chrono_class"],
        "artifact_path": output.relative_to(COMPONENT_ROOT).as_posix(),
        "available": str(available).lower(),
        "fallback": str(not available).lower(),
        "source": "pychrono_vsg_capture" if available else "fallback_vsg_capture_unavailable",
        "build_root": build_root.relative_to(PROJECT_ROOT).as_posix(),
        "chrono_data_path": (build_root / "data").relative_to(PROJECT_ROOT).as_posix(),
        "data_path_hint": config["data_path_hint"],
        "chrono_version": chrono_version,
        "chrono_version_status": _chrono_version_status(chrono_version, available),
        "window_width_px": str(VSG_WINDOW_SIZE[0]),
        "window_height_px": str(VSG_WINDOW_SIZE[1]),
        "camera_eye": ",".join(f"{value:.3f}" for value in config["camera_eye"]),
        "camera_target": ",".join(f"{value:.3f}" for value in config["camera_target"]),
        "camera_fov_deg": config["camera_fov_deg"],
        "visible_component_ids": config["visible_component_ids"],
        "visible_vehicle_part_ids": config["visible_vehicle_part_ids"],
        **_image_metadata(output),
        "fallback_reason": fallback_reason,
        "reason": fallback_reason,
    }


def _write_vehicle_vsg_manifest(updated_row: dict[str, str]) -> None:
    existing: dict[str, dict[str, str]] = {}
    if VEHICLE_VSG_CAPTURE_MANIFEST.exists():
        try:
            payload = json.load(VEHICLE_VSG_CAPTURE_MANIFEST.open(encoding="utf-8"))
            for row in payload.get("captures", []):
                if isinstance(row, dict) and row.get("artifact_path"):
                    existing[str(row["artifact_path"])] = {str(key): str(value) for key, value in row.items()}
        except Exception:
            existing = {}
    existing[updated_row["artifact_path"]] = updated_row
    rows = [existing[path] for path in sorted(existing)]
    source_values = sorted({row["source"] for row in rows})
    write_json(
        VEHICLE_VSG_CAPTURE_MANIFEST,
        {
            "schema_id": "visual.vsg_vehicle_capture_manifest.v1",
            "run_id": RUN_ID,
            "source": ";".join(source_values),
            "capture_family_id": "chrono_builtin_vehicle_assets",
            "render_backend": "pychrono.vsg3d ChVisualSystemVSG visual model capture",
            "camera_contract": "per-capture camera_eye, camera_target, camera_fov_deg, resolution, visible_component_ids, visible_vehicle_part_ids, and image hash",
            "captures": rows,
        },
    )


def _compose_robot_vsg_panel(output: Path, viper_path: Path, curiosity_path: Path) -> Path:
    captures = []
    for label, path in (("VIPER", viper_path), ("Curiosity", curiosity_path)):
        image = Image.open(path).convert("RGB")
        target_w = 720
        scale = target_w / image.width
        target_h = int(image.height * scale)
        image = image.resize((target_w, target_h), Image.Resampling.LANCZOS)
        captures.append((label, image))

    label_h = 42
    gutter = 20
    margin = 18
    width = captures[0][1].width + captures[1][1].width + gutter + 2 * margin
    height = max(image.height for _, image in captures) + label_h + 2 * margin
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 22)
    except Exception:
        font = ImageFont.load_default()

    x = margin
    for label, image in captures:
        draw.text((x, margin), f"{label} VSG capture", fill=(17, 24, 39), font=font)
        canvas.paste(image, (x, margin + label_h))
        x += image.width + gutter
    canvas.save(output)
    return output


def _write_vsg_manifest(capture_rows: list[dict[str, str]], composite_available: bool) -> None:
    source_values = sorted({row["source"] for row in capture_rows})
    composite_path = IMAGES_RENDER / "chrono_builtin_robot_rover_assets.png"
    composite_metadata = _image_metadata(composite_path) if composite_available else {"image_width_px": "", "image_height_px": "", "image_sha256": ""}
    write_json(
        VSG_CAPTURE_MANIFEST,
        {
            "schema_id": "visual.vsg_robot_capture_manifest.v1",
            "run_id": RUN_ID,
            "source": ";".join(source_values),
            "capture_family_id": "chrono_builtin_robot_rover_assets",
            "composite_artifact_path": "images/renders/chrono_builtin_robot_rover_assets.png",
            "composite_available": composite_available,
            "composite_width_px": composite_metadata["image_width_px"],
            "composite_height_px": composite_metadata["image_height_px"],
            "composite_sha256": composite_metadata["image_sha256"],
            "render_backend": "pychrono.vsg3d ChVisualSystemVSG",
            "camera_contract": "per-capture camera_eye, camera_target, camera_fov_deg, resolution, visible_component_ids, and image hash",
            "captures": capture_rows,
        },
    )


def render_wheeled_vehicle_assets() -> Path:
    output = IMAGES_RENDER / "chrono_builtin_wheeled_vehicle_assets.png"
    capture = _capture_vehicle_vsg("hmmwv", output)
    if capture["available"] == "true":
        _write_vehicle_vsg_manifest(capture)
        return output

    fig = plt.figure(figsize=(9.0, 4.6))
    ax = fig.add_subplot(111, projection="3d")
    _add_obj(ax, "vehicle/hmmwv/hmmwv_chassis_simple.obj", center=(-0.82, 0.16, 0.05), size=1.55, color="#2563eb", rotate_z=0.02)
    _add_obj(ax, "vehicle/hmmwv/hmmwv_tire_right.obj", center=(0.72, 0.42, 0.02), size=0.62, color="#111827", rotate_z=0.20)
    _add_obj(ax, "vehicle/hmmwv/hmmwv_rim.obj", center=(0.72, -0.44, 0.02), size=0.48, color="#64748b", rotate_z=0.20)
    _format_asset_ax(ax)
    add_callout_3d(ax, "HMMWV chassis mesh", (0.12, 0.86), (-0.82, 0.16, 0.20), color="#1d4ed8", size=7)
    add_callout_3d(ax, "Tire mesh", (0.86, 0.70), (0.72, 0.42, 0.28), color="#111827", size=7)
    add_callout_3d(ax, "Rim mesh", (0.62, 0.24), (0.72, -0.44, 0.18), color="#475569", size=7)
    fallback_output = _trim_white_margin(save_figure(fig, output))
    _write_vehicle_vsg_manifest(_vehicle_vsg_fallback_row("hmmwv", output, "fallback_obj_matplotlib_render", capture["fallback_reason"] or "VSG capture unavailable; rendered OBJ fallback"))
    return fallback_output


def render_tracked_vehicle_assets() -> Path:
    output = IMAGES_RENDER / "chrono_builtin_tracked_vehicle_assets.png"
    capture = _capture_vehicle_vsg("m113", output)
    if capture["available"] == "true":
        _write_vehicle_vsg_manifest(capture)
        return output

    fig = plt.figure(figsize=(9.0, 4.6))
    ax = fig.add_subplot(111, projection="3d")
    _add_obj(ax, "vehicle/M113/meshes/Chassis.obj", center=(-0.95, 0.05, 0.08), size=1.55, color="#2563eb", rotate_z=0.02)
    _add_obj(ax, "vehicle/M113/meshes/SprocketSinglePin_R.obj", center=(0.45, 0.58, 0.04), size=0.48, color="#64748b")
    _add_obj(ax, "vehicle/M113/meshes/Roller_R.obj", center=(0.98, 0.12, 0.02), size=0.40, color="#475569")
    _add_obj(ax, "vehicle/M113/meshes/TrackShoeSinglePin.obj", center=(0.48, -0.55, -0.02), size=0.46, color="#111827")
    _format_asset_ax(ax)
    add_callout_3d(ax, "M113 chassis", (0.12, 0.86), (-0.95, 0.05, 0.22), color="#1d4ed8", size=7)
    add_callout_3d(ax, "Sprocket", (0.72, 0.66), (0.45, 0.58, 0.22), color="#475569", size=7)
    add_callout_3d(ax, "Track shoe", (0.64, 0.24), (0.48, -0.55, 0.05), color="#111827", size=7)
    fallback_output = _trim_white_margin(save_figure(fig, output))
    _write_vehicle_vsg_manifest(_vehicle_vsg_fallback_row("m113", output, "fallback_obj_matplotlib_render", capture["fallback_reason"] or "VSG capture unavailable; rendered OBJ fallback"))
    return fallback_output


def render_robot_rover_assets() -> Path:
    output = IMAGES_RENDER / "chrono_builtin_robot_rover_assets.png"
    viper_capture = IMAGES_RENDER / "chrono_viper_vsg_capture.png"
    curiosity_capture = IMAGES_RENDER / "chrono_curiosity_vsg_capture.png"
    capture_rows = [_capture_robot_vsg("viper", viper_capture), _capture_robot_vsg("curiosity", curiosity_capture)]
    if all(row["available"] == "true" for row in capture_rows):
        panel_path = _compose_robot_vsg_panel(output, viper_capture, curiosity_capture)
        _write_vsg_manifest(capture_rows, True)
        return panel_path

    _write_vsg_manifest(capture_rows, False)
    fig, ax = plt.subplots(figsize=(10.0, 5.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.35)
    ax.axis("off")

    def leader(text, xytext, xy, *, color, ha="center"):
        ax.annotate(
            text,
            xy=xy,
            xytext=xytext,
            ha=ha,
            va="center",
            fontsize=9.0,
            color=color,
            bbox={"boxstyle": "round,pad=0.18", "facecolor": "white", "edgecolor": color, "linewidth": 0.9},
            arrowprops={"arrowstyle": "-", "color": color, "linewidth": 1.0, "shrinkA": 2, "shrinkB": 1},
            zorder=30,
        )

    ax.text(2.45, 5.02, "Viper", ha="center", va="center", fontsize=14.0, weight="bold", color="#1d4ed8")
    ax.text(7.45, 5.02, "Curiosity", ha="center", va="center", fontsize=14.0, weight="bold", color="#0f766e")

    ax.add_patch(Rectangle((0.58, 0.55), 3.72, 3.95, facecolor="#f8fafc", edgecolor="#dbeafe", linewidth=0.9, zorder=0))
    ax.add_patch(Rectangle((5.58, 0.55), 3.82, 3.95, facecolor="#f8fafc", edgecolor="#ccfbf1", linewidth=0.9, zorder=0))

    # Viper: solid chassis body, mast, and wheel asset cue.
    viper_chassis = Polygon(
        [(1.25, 2.94), (2.94, 3.28), (3.56, 2.86), (3.40, 2.20), (1.46, 2.02), (0.98, 2.42)],
        closed=True,
        facecolor="#2563eb",
        edgecolor="#1e3a8a",
        linewidth=1.1,
        zorder=5,
    )
    ax.add_patch(viper_chassis)
    ax.add_patch(Polygon([(1.62, 2.98), (2.26, 3.12), (2.58, 2.78), (1.82, 2.68)], closed=True, facecolor="#60a5fa", edgecolor="#1e3a8a", linewidth=0.7, zorder=6))
    ax.add_patch(Rectangle((2.26, 3.22), 0.10, 0.58, facecolor="#1d4ed8", edgecolor="#1e3a8a", linewidth=0.7, zorder=6))
    ax.add_patch(Rectangle((2.05, 3.78), 0.52, 0.16, facecolor="#93c5fd", edgecolor="#1e3a8a", linewidth=0.7, zorder=7))
    for cx, cy in [(1.34, 1.82), (2.92, 1.84)]:
        ax.add_patch(Circle((cx, cy), 0.46, facecolor="#111827", edgecolor="#030712", linewidth=1.0, zorder=8))
        ax.add_patch(Circle((cx, cy), 0.22, facecolor="#f8fafc", edgecolor="#64748b", linewidth=0.8, zorder=9))
        for angle in np.linspace(0, 2 * math.pi, 10, endpoint=False):
            ax.plot([cx + 0.29 * math.cos(angle), cx + 0.45 * math.cos(angle)], [cy + 0.29 * math.sin(angle), cy + 0.45 * math.sin(angle)], color="#f8fafc", linewidth=0.55, zorder=10)

    # Curiosity: solid rocker-bogie body cue, mast, suspension arms, and wheel tread.
    curiosity_body = Polygon(
        [(6.55, 3.04), (7.55, 3.26), (8.16, 2.92), (7.78, 2.46), (6.58, 2.36), (6.18, 2.70)],
        closed=True,
        facecolor="#0f766e",
        edgecolor="#134e4a",
        linewidth=1.1,
        zorder=5,
    )
    ax.add_patch(curiosity_body)
    ax.add_patch(Rectangle((7.24, 3.23), 0.08, 0.58, facecolor="#0f766e", edgecolor="#134e4a", linewidth=0.7, zorder=6))
    ax.add_patch(Circle((7.28, 3.88), 0.16, facecolor="#5eead4", edgecolor="#0f766e", linewidth=0.8, zorder=7))
    ax.plot([6.42, 5.98, 6.76, 7.82, 8.48], [2.50, 1.84, 1.92, 1.90, 2.06], color="#0f766e", linewidth=3.0, zorder=4)
    ax.plot([7.72, 8.12, 8.58], [2.54, 2.05, 1.72], color="#0f766e", linewidth=3.0, zorder=4)
    for cx, cy, r in [(5.92, 1.64, 0.40), (6.78, 1.72, 0.34), (8.50, 1.62, 0.40)]:
        ax.add_patch(Circle((cx, cy), r, facecolor="#374151", edgecolor="#111827", linewidth=1.0, zorder=8))
        ax.add_patch(Circle((cx, cy), r * 0.46, facecolor="#f8fafc", edgecolor="#64748b", linewidth=0.8, zorder=9))
        for angle in np.linspace(0, 2 * math.pi, 12, endpoint=False):
            ax.plot([cx + r * 0.66 * math.cos(angle), cx + r * 0.96 * math.cos(angle)], [cy + r * 0.66 * math.sin(angle), cy + r * 0.96 * math.sin(angle)], color="#cbd5e1", linewidth=0.55, zorder=10)

    leader("Viper chassis", (0.72, 4.10), (2.18, 2.92), color="#1d4ed8", ha="left")
    leader("Viper wheel", (0.92, 1.02), (1.34, 1.82), color="#111827", ha="left")
    leader("Curiosity chassis", (9.10, 4.05), (7.20, 2.86), color="#0f766e", ha="right")
    leader("Curiosity wheel", (9.00, 1.02), (8.50, 1.62), color="#374151", ha="right")

    ax.text(2.45, 0.78, "solid preview of Robot model assets", ha="center", va="center", fontsize=7.2, color="#475569")
    ax.text(7.45, 0.78, "chassis, rocker-bogie, wheel asset cues", ha="center", va="center", fontsize=7.2, color="#475569")
    return _trim_white_margin(save_figure(fig, output))


def main() -> None:
    ensure_output_dirs()
    print("chrono built-in wheeled assets:", render_wheeled_vehicle_assets())
    print("chrono built-in tracked assets:", render_tracked_vehicle_assets())
    print("chrono built-in robot rover assets:", render_robot_rover_assets())


if __name__ == "__main__":
    main()
