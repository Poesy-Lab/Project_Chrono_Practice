from __future__ import annotations

import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle

sys.path.append(str(Path(__file__).resolve().parents[1] / "common"))

from component_utils import IMAGES_RENDER, save_figure  # noqa: E402


def _box(ax, xy, size, label, *, face="#ffffff", edge="#334155", fontsize=6.8, weight="normal", linestyle="-"):
    patch = FancyBboxPatch(
        xy,
        size[0],
        size[1],
        boxstyle="round,pad=0.024,rounding_size=0.040",
        facecolor=face,
        edgecolor=edge,
        linestyle=linestyle,
        linewidth=1.15,
        zorder=5,
    )
    ax.add_patch(patch)
    ax.text(
        xy[0] + size[0] / 2,
        xy[1] + size[1] / 2,
        label,
        ha="center",
        va="center",
        fontsize=fontsize,
        color="#111827",
        weight=weight,
        zorder=6,
    )
    return patch


def _arrow(ax, start, end, *, color="#475569", width=1.05, rad=0.0):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=10.5,
            linewidth=width,
            color=color,
            connectionstyle=f"arc3,rad={rad}",
            shrinkA=3,
            shrinkB=3,
            zorder=4,
        )
    )


def _callout(ax, text, xytext, target, *, color, ha="center"):
    ax.annotate(
        text,
        xy=target,
        xytext=xytext,
        ha=ha,
        va="center",
        fontsize=6.6,
        color=color,
        bbox={"boxstyle": "round,pad=0.15", "facecolor": "white", "edgecolor": color, "linewidth": 0.8},
        arrowprops={"arrowstyle": "-", "color": color, "linewidth": 0.85, "shrinkA": 2, "shrinkB": 2},
        zorder=12,
    )


def _body_icon(ax, x, y, color):
    ax.add_patch(Rectangle((x, y), 0.88, 0.28, facecolor="#93c5fd", edgecolor=color, linewidth=1.0, zorder=7))
    ax.add_patch(Rectangle((x + 0.18, y + 0.28), 0.46, 0.18, facecolor="#bfdbfe", edgecolor=color, linewidth=0.8, zorder=7))
    for wx in (x + 0.18, x + 0.70):
        ax.add_patch(Circle((wx, y - 0.02), 0.105, facecolor="#111827", edgecolor="#020617", linewidth=0.6, zorder=8))
        ax.add_patch(Circle((wx, y - 0.02), 0.040, facecolor="#e5e7eb", edgecolor="#64748b", linewidth=0.5, zorder=9))
    ax.add_patch(Circle((x + 0.42, y + 0.55), 0.055, facecolor="#16a34a", edgecolor="#166534", linewidth=0.6, zorder=8))
    ax.plot([x + 0.42, x + 0.86], [y + 0.55, y + 0.52], color="#f59e0b", linewidth=1.0, zorder=8)


def _camera_icon(ax, x, y, color):
    ax.add_patch(Rectangle((x, y), 0.36, 0.22, facecolor="#fee2e2", edgecolor=color, linewidth=0.8, zorder=7))
    ax.add_patch(Polygon([(x + 0.36, y + 0.04), (x + 0.55, y - 0.03), (x + 0.55, y + 0.25), (x + 0.36, y + 0.18)], facecolor="#fecaca", edgecolor=color, linewidth=0.8, zorder=7))
    ax.plot([x + 0.56, x + 0.82], [y + 0.11, y + 0.25], color=color, linewidth=0.7, zorder=7)
    ax.plot([x + 0.56, x + 0.82], [y + 0.11, y - 0.03], color=color, linewidth=0.7, zorder=7)


def _lidar_icon(ax, x, y, color):
    ax.add_patch(Circle((x + 0.20, y + 0.12), 0.12, facecolor="#cffafe", edgecolor=color, linewidth=0.8, zorder=7))
    for angle in (-0.42, -0.18, 0.08, 0.34):
        ax.plot([x + 0.30, x + 0.72], [y + 0.12, y + 0.12 + 0.33 * math.sin(angle)], color=color, linewidth=0.8, zorder=7)


def _imu_icon(ax, x, y, color):
    ax.add_patch(Rectangle((x, y), 0.45, 0.30, facecolor="#dcfce7", edgecolor=color, linewidth=0.8, zorder=7))
    ax.plot([x + 0.10, x + 0.34], [y + 0.15, y + 0.15], color=color, linewidth=0.8, zorder=8)
    ax.plot([x + 0.22, x + 0.22], [y + 0.05, y + 0.25], color=color, linewidth=0.8, zorder=8)
    ax.text(x + 0.56, y + 0.15, "GPS/IMU", ha="left", va="center", fontsize=5.9, color="#166534", zorder=8)


def _manifest_icon(ax, x, y):
    ax.add_patch(Rectangle((x, y), 0.70, 0.44, facecolor="#f8fafc", edgecolor="#475569", linewidth=0.8, zorder=7))
    for i, text in enumerate(["time", "pose", "path", "hash"]):
        ax.text(x + 0.10, y + 0.34 - i * 0.095, text, ha="left", va="center", fontsize=5.3, color="#334155", zorder=8)
        ax.plot([x + 0.42, x + 0.62], [y + 0.34 - i * 0.095, y + 0.34 - i * 0.095], color="#cbd5e1", linewidth=0.5, zorder=8)


def render_data_visualization_sensor_pipeline_catalog() -> Path:
    output = IMAGES_RENDER / "data_visualization_sensor_pipeline_catalog.png"
    fig, ax = plt.subplots(figsize=(11.8, 6.8))
    ax.set_xlim(0, 11.2)
    ax.set_ylim(0, 6.55)
    ax.axis("off")

    ax.text(5.6, 6.22, "Chrono::Sensor module output contract", ha="center", va="center", fontsize=13.0, weight="bold", color="#111827")
    ax.text(
        5.6,
        5.92,
        "A sensor artifact is valid only when parent pose, manager update, filter chain, and manifest evidence agree.",
        ha="center",
        va="center",
        fontsize=8.0,
        color="#475569",
    )

    headers = [
        ("Parent body\n+ offsetPose", 0.46, 1.62, "#dbeafe", "#2563eb"),
        ("Sensor manager\nmodule gate", 2.52, 1.72, "#ede9fe", "#7c3aed"),
        ("Sensor model", 4.66, 1.68, "#f8fafc", "#475569"),
        ("Filter chain", 6.72, 1.70, "#ecfdf5", "#059669"),
        ("Manifest\n+ raw artifact", 8.86, 1.82, "#fff7ed", "#ea580c"),
    ]
    for title, x, w, face, edge in headers:
        _box(ax, (x, 5.28), (w, 0.44), title, face=face, edge=edge, fontsize=7.2, weight="bold")

    rows = [
        {
            "y": 4.42,
            "name": "Camera / depth /\nsegmentation",
            "color": "#dc2626",
            "manager": "ChSensorManager\nAddSensor + Update",
            "sensor": "ChCameraSensor\nresolution / FOV / lag",
            "filter": "render -> noise\nRGBA/depth/seg\nsave or access",
            "artifact": "frame PNG\nor depth buffer\nmanifest row",
            "icon": "camera",
        },
        {
            "y": 3.36,
            "name": "LiDAR\nrange cloud",
            "color": "#0891b2",
            "manager": "GPU/OptiX\nscene ready",
            "sensor": "ChLidarSensor\nsamples / channels\nrange / FOV",
            "filter": "ray buffer -> XYZI\nnoise / point cloud\nsave/access",
            "artifact": "cloud CSV/PCD\nrange image\nmanifest row",
            "icon": "lidar",
        },
        {
            "y": 2.30,
            "name": "GPS / IMU\nnumeric stream",
            "color": "#16a34a",
            "manager": "dynamics sensor\nupdate lifecycle",
            "sensor": "GPS / accel /\ngyro / magnetometer\nframe convention",
            "filter": "state update -> noise\nhost buffer\nCSV writer",
            "artifact": "gps_log.csv\nimu_log.csv\npose manifest",
            "icon": "imu",
        },
        {
            "y": 1.24,
            "name": "Radar /\ntachometer",
            "color": "#f59e0b",
            "manager": "Sensor module\navailability true",
            "sensor": "radar returns\nwheel / shaft target\nupdate rate",
            "filter": "process returns\nrpm/radps access\nsave CSV",
            "artifact": "radar_returns\nshaft speed log\nmanifest row",
            "icon": "manifest",
        },
    ]

    for idx, row in enumerate(rows):
        y = row["y"]
        color = row["color"]
        ax.add_patch(Rectangle((0.30, y - 0.20), 10.55, 0.84, facecolor="#ffffff" if idx % 2 == 0 else "#f8fafc", edgecolor="#e5e7eb", linewidth=0.5, zorder=0))
        _box(ax, (0.54, y), (1.54, 0.46), row["name"], face="#ffffff", edge=color, fontsize=6.6, weight="bold")
        _box(ax, (2.60, y - 0.03), (1.58, 0.52), row["manager"], face="#ffffff", edge="#7c3aed", fontsize=6.25, weight="bold")
        _box(ax, (4.74, y - 0.06), (1.58, 0.58), row["sensor"], face="#ffffff", edge=color, fontsize=6.1)
        _box(ax, (6.80, y - 0.06), (1.58, 0.58), row["filter"], face="#ffffff", edge="#059669", fontsize=6.0)
        _box(ax, (8.94, y - 0.06), (1.66, 0.58), row["artifact"], face="#fff7ed", edge="#ea580c", fontsize=6.0)

        _arrow(ax, (2.08, y + 0.23), (2.60, y + 0.23), color=color)
        _arrow(ax, (4.18, y + 0.23), (4.74, y + 0.23), color=color)
        _arrow(ax, (6.32, y + 0.23), (6.80, y + 0.23), color=color)
        _arrow(ax, (8.38, y + 0.23), (8.94, y + 0.23), color=color)

    _body_icon(ax, 0.78, 0.34, "#2563eb")
    _box(ax, (2.56, 0.28), (1.70, 0.46), "module_available=true\nmanager.Update() called", face="#f3e8ff", edge="#7c3aed", fontsize=6.4, weight="bold")
    _box(ax, (4.72, 0.28), (1.66, 0.46), "ChSensor fields:\nparent, rate, lag, window", face="#f8fafc", edge="#475569", fontsize=6.4)
    _box(ax, (6.78, 0.28), (1.64, 0.46), "PushFilter before\nAddSensor/lock", face="#dcfce7", edge="#059669", fontsize=6.4, weight="bold")
    _box(ax, (8.94, 0.28), (1.66, 0.46), "time + pose + path\nchecksum + source", face="#ffedd5", edge="#ea580c", fontsize=6.4, weight="bold")
    _arrow(ax, (1.80, 0.55), (2.56, 0.55), color="#2563eb")
    _arrow(ax, (4.26, 0.55), (4.72, 0.55), color="#7c3aed")
    _arrow(ax, (6.38, 0.55), (6.78, 0.55), color="#475569")
    _arrow(ax, (8.42, 0.55), (8.94, 0.55), color="#059669")

    _callout(ax, "offsetPose belongs\nto the parent body", (0.92, 5.02), (1.27, 5.50), color="#2563eb", ha="left")
    _callout(ax, "manager is the\nmodule-backed gate", (3.38, 5.02), (3.39, 4.95), color="#7c3aed")
    _callout(ax, "filter order defines\nwhat can be saved", (7.50, 5.02), (7.58, 4.95), color="#059669")
    _callout(ax, "raw files are not enough\nwithout a manifest", (10.24, 5.02), (9.78, 4.95), color="#ea580c", ha="right")

    ax.text(
        5.6,
        0.06,
        "Fallback rule: a layout render can verify mount intent, but live sensor evidence requires Sensor module availability and artifact manifests.",
        ha="center",
        va="center",
        fontsize=7.8,
        color="#475569",
    )
    return save_figure(fig, output)


if __name__ == "__main__":
    print(render_data_visualization_sensor_pipeline_catalog())
