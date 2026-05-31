from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image, ImageChops

from component_utils import IMAGES_RENDER, ensure_output_dirs, save_figure
from component_utils import add_callout_3d


COMPONENT_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = Path(__file__).resolve().parents[4]
CHRONO_DATA = PROJECT_ROOT / "chrono_build" / "data"


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


def _add_obj(ax, rel_path: str, *, center, size: float, color: str, alpha: float = 0.90, rotate_z: float = 0.0) -> None:
    path = CHRONO_DATA / rel_path
    vertices, faces = _load_obj(path)
    vertices = _normalized(vertices, center=center, size=size, rotate_z=rotate_z)
    polygons = [[vertices[idx] for idx in face] for face in faces]
    mesh = Poly3DCollection(polygons, facecolors=color, edgecolors="none", linewidths=0.0, alpha=alpha)
    ax.add_collection3d(mesh)


def _format_asset_ax(ax, *, xlim=(-1.7, 1.7), ylim=(-1.15, 1.15), zlim=(-0.55, 0.85)) -> None:
    ax.view_init(elev=22, azim=-48)
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


def render_wheeled_vehicle_assets() -> Path:
    output = IMAGES_RENDER / "chrono_builtin_wheeled_vehicle_assets.png"
    fig = plt.figure(figsize=(9.0, 4.6))
    ax = fig.add_subplot(111, projection="3d")
    _add_obj(ax, "vehicle/hmmwv/hmmwv_chassis_simple.obj", center=(-0.82, 0.16, 0.05), size=1.55, color="#2563eb", rotate_z=0.02)
    _add_obj(ax, "vehicle/hmmwv/hmmwv_tire_right.obj", center=(0.72, 0.42, 0.02), size=0.62, color="#111827", rotate_z=0.20)
    _add_obj(ax, "vehicle/hmmwv/hmmwv_rim.obj", center=(0.72, -0.44, 0.02), size=0.48, color="#64748b", rotate_z=0.20)
    _format_asset_ax(ax)
    add_callout_3d(ax, "HMMWV chassis mesh", (0.12, 0.86), (-0.82, 0.16, 0.20), color="#1d4ed8", size=7)
    add_callout_3d(ax, "Tire mesh", (0.86, 0.70), (0.72, 0.42, 0.28), color="#111827", size=7)
    add_callout_3d(ax, "Rim mesh", (0.62, 0.24), (0.72, -0.44, 0.18), color="#475569", size=7)
    return _trim_white_margin(save_figure(fig, output))


def render_tracked_vehicle_assets() -> Path:
    output = IMAGES_RENDER / "chrono_builtin_tracked_vehicle_assets.png"
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
    return _trim_white_margin(save_figure(fig, output))


def render_robot_rover_assets() -> Path:
    output = IMAGES_RENDER / "chrono_builtin_robot_rover_assets.png"
    fig = plt.figure(figsize=(9.0, 4.6))
    ax = fig.add_subplot(111, projection="3d")
    _add_obj(ax, "robot/viper/obj/viper_chassis.obj", center=(-1.08, 0.25, 0.00), size=1.10, color="#2563eb", rotate_z=-0.20)
    _add_obj(ax, "robot/viper/obj/nasa_viper_wheel.obj", center=(-0.22, -0.54, 0.00), size=0.48, color="#111827", rotate_z=0.40)
    _add_obj(ax, "robot/curiosity/obj/curiosity_chassis.obj", center=(0.72, 0.28, 0.00), size=1.10, color="#0f766e", rotate_z=0.10)
    _add_obj(ax, "robot/curiosity/obj/curiosity_wheel.obj", center=(1.15, -0.55, 0.00), size=0.46, color="#374151", rotate_z=-0.25)
    _format_asset_ax(ax)
    add_callout_3d(ax, "Viper chassis", (0.12, 0.86), (-1.08, 0.25, 0.12), color="#1d4ed8", size=7)
    add_callout_3d(ax, "Viper wheel", (0.20, 0.24), (-0.22, -0.54, 0.18), color="#111827", size=7)
    add_callout_3d(ax, "Curiosity mesh", (0.66, 0.68), (0.72, 0.28, 0.12), color="#0f766e", size=7)
    return _trim_white_margin(save_figure(fig, output))


def main() -> None:
    ensure_output_dirs()
    print("chrono built-in wheeled assets:", render_wheeled_vehicle_assets())
    print("chrono built-in tracked assets:", render_tracked_vehicle_assets())
    print("chrono built-in robot rover assets:", render_robot_rover_assets())


if __name__ == "__main__":
    main()
