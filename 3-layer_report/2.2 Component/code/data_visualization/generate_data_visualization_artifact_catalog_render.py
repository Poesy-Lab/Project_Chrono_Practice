from __future__ import annotations

import math
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle

sys.path.append(str(Path(__file__).resolve().parents[1] / "common"))

from component_utils import IMAGES_RENDER, save_figure  # noqa: E402


def _card(ax, xy, size, *, face="#ffffff", edge="#334155"):
    patch = FancyBboxPatch(
        xy,
        size[0],
        size[1],
        boxstyle="round,pad=0.025,rounding_size=0.045",
        facecolor=face,
        edgecolor=edge,
        linewidth=1.15,
        zorder=3,
    )
    ax.add_patch(patch)
    return patch


def _leader(ax, text, xytext, xy, *, color, ha="center"):
    ax.annotate(
        text,
        xy=xy,
        xytext=xytext,
        ha=ha,
        va="center",
        fontsize=7.8,
        color=color,
        bbox={"boxstyle": "round,pad=0.18", "facecolor": "white", "edgecolor": color, "linewidth": 0.9},
        arrowprops={"arrowstyle": "-", "color": color, "linewidth": 0.9, "shrinkA": 2, "shrinkB": 1},
        zorder=15,
    )


def _arrow(ax, start, end, *, color="#475569", width=1.2, rad=0.0):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=12,
            linewidth=width,
            color=color,
            connectionstyle=f"arc3,rad={rad}",
            shrinkA=4,
            shrinkB=4,
            zorder=5,
        )
    )


def _elbow_arrow(ax, points, *, color="#475569", width=1.2):
    for start, end in zip(points, points[1:-1]):
        ax.plot([start[0], end[0]], [start[1], end[1]], color=color, linewidth=width, zorder=4)
    _arrow(ax, points[-2], points[-1], color=color, width=width)


def _center_scene(ax):
    _card(ax, (4.22, 2.35), (2.35, 1.45), face="#f8fafc", edge="#475569")
    ax.add_patch(Rectangle((4.42, 2.55), 1.92, 0.12, facecolor="#d1d5db", edgecolor="#64748b", linewidth=0.8, zorder=4))
    ax.add_patch(Rectangle((4.72, 2.88), 0.92, 0.38, facecolor="#93c5fd", edgecolor="#1d4ed8", linewidth=1.2, zorder=5))
    ax.add_patch(Rectangle((5.78, 2.73), 0.24, 0.68, facecolor="#fca5a5", edgecolor="#991b1b", linewidth=1.1, zorder=5))
    for x in (4.88, 5.50):
        ax.add_patch(Circle((x, 2.74), 0.15, facecolor="#111827", edgecolor="#111827", linewidth=0.8, zorder=6))
        ax.add_patch(Circle((x, 2.74), 0.055, facecolor="#64748b", edgecolor="#111827", linewidth=0.4, zorder=7))
    ax.scatter([5.76, 5.76], [2.96, 3.14], s=32, color="#facc15", edgecolor="#854d0e", linewidth=0.7, zorder=7)
    ax.plot([5.12, 6.10], [3.42, 3.54], color="#dc2626", linewidth=1.4, linestyle="--", zorder=6)
    for angle in (-0.35, -0.12, 0.12, 0.35):
        ax.plot([5.25, 6.10], [3.38, 3.38 + 0.42 * math.sin(angle)], color="#f59e0b", linewidth=1.0, alpha=0.75, zorder=6)
    ax.text(5.40, 3.64, "simulation scene", ha="center", va="center", fontsize=8.0, color="#334155", weight="bold", zorder=8)


def _csv_sheet(ax, x, y, rows, colors):
    _card(ax, (x, y), (1.58, 0.92), face="#ffffff", edge="#2563eb")
    ax.add_patch(Rectangle((x + 0.12, y + 0.66), 1.34, 0.12, facecolor="#dbeafe", edgecolor="#93c5fd", linewidth=0.5, zorder=4))
    for i, row in enumerate(rows):
        yy = y + 0.52 - i * 0.16
        ax.plot([x + 0.12, x + 1.46], [yy, yy], color="#cbd5e1", linewidth=0.6, zorder=4)
        ax.text(x + 0.18, yy - 0.07, row, ha="left", va="center", fontsize=5.9, color=colors[i % len(colors)], zorder=5)
    for xx in (x + 0.58, x + 1.04):
        ax.plot([xx, xx], [y + 0.14, y + 0.78], color="#cbd5e1", linewidth=0.5, zorder=4)


def _mini_graph(ax, x, y):
    _card(ax, (x, y), (1.58, 0.92), face="#ffffff", edge="#0f766e")
    ax.plot([x + 0.22, x + 0.22], [y + 0.18, y + 0.72], color="#94a3b8", linewidth=0.7, zorder=4)
    ax.plot([x + 0.22, x + 1.36], [y + 0.18, y + 0.18], color="#94a3b8", linewidth=0.7, zorder=4)
    xs = [x + 0.28, x + 0.48, x + 0.68, x + 0.90, x + 1.12, x + 1.30]
    ys = [y + 0.26, y + 0.31, y + 0.56, y + 0.46, y + 0.38, y + 0.30]
    ax.plot(xs, ys, color="#dc2626", linewidth=1.7, zorder=5)
    ax.text(x + 0.92, y + 0.70, "PNG", ha="center", va="center", fontsize=6.6, color="#0f766e", weight="bold", zorder=5)


def _json_card(ax, x, y):
    _card(ax, (x, y), (1.72, 0.92), face="#f8fafc", edge="#7c3aed")
    ax.text(x + 0.16, y + 0.66, "{", ha="left", va="center", fontsize=16, color="#7c3aed", weight="bold", zorder=5)
    for i, row in enumerate(['"dt_s":0.002', '"solver":"NSC"', '"terrain":"SCM"']):
        ax.text(x + 0.38, y + 0.66 - i * 0.20, row, ha="left", va="center", fontsize=6.4, color="#334155", zorder=5)


def _image_tile(ax, x, y, *, edge, kind):
    _card(ax, (x, y), (1.58, 0.92), face="#ffffff", edge=edge)
    ax.add_patch(Rectangle((x + 0.15, y + 0.16), 1.28, 0.60, facecolor="#e0f2fe", edgecolor="#64748b", linewidth=0.7, zorder=4))
    if kind == "screenshot":
        ax.add_patch(Rectangle((x + 0.32, y + 0.31), 0.48, 0.22, facecolor="#93c5fd", edgecolor="#1d4ed8", linewidth=0.7, zorder=5))
        ax.add_patch(Rectangle((x + 0.94, y + 0.23), 0.16, 0.46, facecolor="#fca5a5", edgecolor="#991b1b", linewidth=0.7, zorder=5))
    else:
        ax.add_patch(Rectangle((x + 0.22, y + 0.24), 1.14, 0.42, facecolor="#bae6fd", edgecolor="#0284c7", linewidth=0.7, zorder=5))
        ax.plot([x + 0.34, x + 1.22], [y + 0.34, y + 0.55], color="#f59e0b", linewidth=1.0, zorder=6)
        ax.plot([x + 0.34, x + 1.18], [y + 0.54, y + 0.32], color="#22c55e", linewidth=1.0, zorder=6)


def _cloud_tile(ax, x, y):
    _card(ax, (x, y), (1.58, 0.92), face="#ffffff", edge="#0891b2")
    pts = [
        (0.22, 0.24),
        (0.38, 0.52),
        (0.54, 0.34),
        (0.72, 0.64),
        (0.88, 0.42),
        (1.05, 0.58),
        (1.20, 0.28),
        (1.34, 0.48),
    ]
    for dx, dy in pts:
        ax.add_patch(Circle((x + dx, y + dy), 0.035, facecolor="#22d3ee", edgecolor="#0e7490", linewidth=0.6, zorder=5))
    ax.plot([x + 0.18, x + 1.40], [y + 0.18, y + 0.18], color="#94a3b8", linewidth=0.6, zorder=4)


def _log_strip(ax, x, y):
    _card(ax, (x, y), (1.72, 0.78), face="#ffffff", edge="#475569")
    labels = ["gps lat/lon", "imu accel", "gyro rad/s"]
    for i, label in enumerate(labels):
        yy = y + 0.57 - i * 0.20
        ax.text(x + 0.14, yy, label, ha="left", va="center", fontsize=6.1, color="#334155", zorder=5)
        ax.plot([x + 0.90, x + 1.48], [yy, yy + 0.04 * math.sin(i + 1)], color=("#16a34a" if i == 0 else "#2563eb"), linewidth=1.1, zorder=5)


def render_data_visualization_artifact_catalog() -> Path:
    output = IMAGES_RENDER / "data_visualization_artifact_catalog.png"
    fig, ax = plt.subplots(figsize=(12.6, 6.8))
    ax.set_xlim(0, 10.6)
    ax.set_ylim(0, 6.0)
    ax.axis("off")

    ax.text(5.0, 5.72, "Data output artifact catalog", ha="center", va="center", fontsize=12.8, weight="bold", color="#111827")
    ax.text(5.0, 5.38, "Instrumentation components turn simulation state into reproducible files, manifests, graphs, and sensor artifacts.", ha="center", va="center", fontsize=8.2, color="#475569")

    _center_scene(ax)
    _csv_sheet(ax, 0.66, 4.18, ["time_s  x_m  vx", "body   yaw", "source units"], ["#1d4ed8"])
    _csv_sheet(ax, 0.66, 2.76, ["throttle", "brake", "steering"], ["#16a34a", "#2563eb", "#dc2626"])
    _csv_sheet(ax, 0.66, 1.34, ["body_a body_b", "count force", "normal frame"], ["#dc2626"])
    _json_card(ax, 4.16, 4.28)
    _mini_graph(ax, 4.26, 0.78)
    _image_tile(ax, 7.68, 4.18, edge="#2563eb", kind="screenshot")
    _image_tile(ax, 7.68, 2.92, edge="#dc2626", kind="camera")
    _cloud_tile(ax, 7.68, 1.66)
    _log_strip(ax, 7.60, 0.54)

    ax.plot([3.52, 3.52], [1.76, 4.68], color="#94a3b8", linewidth=1.0, zorder=2)
    ax.plot([7.10, 7.10], [0.94, 4.62], color="#94a3b8", linewidth=1.0, zorder=2)
    for x, ports in ((3.52, (4.62, 3.22, 1.78)), (7.10, (4.56, 3.36, 2.10, 0.93))):
        for port_y in ports:
            ax.add_patch(Circle((x, port_y), 0.035, facecolor="#ffffff", edgecolor="#64748b", linewidth=0.8, zorder=6))

    _elbow_arrow(ax, [(4.22, 3.34), (3.52, 3.34), (3.52, 4.62), (2.24, 4.62)], color="#2563eb")
    _elbow_arrow(ax, [(4.22, 3.12), (3.52, 3.12), (3.52, 3.22), (2.24, 3.22)], color="#16a34a")
    _elbow_arrow(ax, [(4.22, 2.84), (3.52, 2.84), (3.52, 1.78), (2.24, 1.78)], color="#dc2626")
    _elbow_arrow(ax, [(5.48, 3.80), (5.48, 4.10), (4.94, 4.28)], color="#7c3aed")
    _elbow_arrow(ax, [(5.20, 2.35), (5.20, 1.70), (5.05, 1.70)], color="#0f766e")
    _elbow_arrow(ax, [(6.57, 3.54), (7.10, 3.54), (7.10, 4.56), (7.68, 4.56)], color="#2563eb")
    _elbow_arrow(ax, [(6.57, 3.30), (7.10, 3.30), (7.10, 3.36), (7.68, 3.36)], color="#dc2626")
    _elbow_arrow(ax, [(6.57, 3.06), (7.10, 3.06), (7.10, 2.10), (7.68, 2.10)], color="#0891b2")
    _elbow_arrow(ax, [(6.57, 2.80), (7.10, 2.80), (7.10, 0.93), (7.60, 0.93)], color="#475569")

    _leader(ax, "State CSV", (0.54, 5.12), (1.38, 4.66), color="#2563eb", ha="left")
    _leader(ax, "Control CSV", (0.42, 3.70), (1.38, 3.24), color="#16a34a", ha="left")
    _leader(ax, "Contact CSV", (0.55, 1.08), (1.38, 1.76), color="#dc2626", ha="left")
    _leader(ax, "Metadata JSON", (3.68, 5.04), (4.48, 4.72), color="#7c3aed", ha="right")
    _leader(ax, "Graph PNG", (4.08, 0.32), (5.04, 1.28), color="#0f766e", ha="right")
    _leader(ax, "Render Screenshot", (9.76, 5.02), (8.38, 4.55), color="#2563eb", ha="right")
    _leader(ax, "Camera frame", (9.70, 3.76), (8.38, 3.38), color="#dc2626", ha="right")
    _leader(ax, "LiDAR cloud", (9.64, 2.24), (8.43, 2.18), color="#0891b2", ha="right")
    _leader(ax, "IMU/GPS log", (9.70, 0.98), (7.92, 1.11), color="#475569", ha="right")

    ax.text(
        5.0,
        0.08,
        "Catalog rule: every artifact needs a schema, owner component, timestamp, source, and enough metadata to replay the run.",
        ha="center",
        va="center",
        fontsize=8.0,
        color="#475569",
    )
    return save_figure(fig, output)


if __name__ == "__main__":
    print(render_data_visualization_artifact_catalog())
