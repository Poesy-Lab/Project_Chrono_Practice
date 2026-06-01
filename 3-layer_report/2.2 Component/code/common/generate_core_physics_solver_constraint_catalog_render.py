from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle

sys.path.append(str(Path(__file__).resolve().parents[1] / "common"))

from component_utils import IMAGES_RENDER, save_figure  # noqa: E402


def _box(ax, xy, size, label, *, face, edge, fontsize=8.3, weight="normal", linestyle="-"):
    patch = FancyBboxPatch(
        xy,
        size[0],
        size[1],
        boxstyle="round,pad=0.024,rounding_size=0.045",
        facecolor=face,
        edgecolor=edge,
        linestyle=linestyle,
        linewidth=1.35,
        zorder=4,
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
        zorder=5,
    )
    return patch


def _arrow(ax, start, end, *, color="#475569", width=1.35, rad=0.0, style="-|>"):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle=style,
            mutation_scale=12,
            linewidth=width,
            color=color,
            connectionstyle=f"arc3,rad={rad}",
            shrinkA=3,
            shrinkB=3,
            zorder=3,
        )
    )


def _label(ax, text, xytext, xy, *, color, ha="center"):
    ax.annotate(
        text,
        xy=xy,
        xytext=xytext,
        ha=ha,
        va="center",
        fontsize=7.8,
        color=color,
        bbox={"boxstyle": "round,pad=0.18", "facecolor": "white", "edgecolor": color, "linewidth": 0.9},
        arrowprops={"arrowstyle": "-", "color": color, "linewidth": 0.95, "shrinkA": 2, "shrinkB": 2},
        zorder=9,
    )


def _mechanical_scene(ax):
    ax.add_patch(Rectangle((0.35, 1.05), 2.55, 0.20, facecolor="#e2e8f0", edgecolor="#64748b", zorder=1))
    chassis = FancyBboxPatch(
        (0.70, 3.56),
        1.55,
        0.46,
        boxstyle="round,pad=0.025,rounding_size=0.08",
        facecolor="#bfdbfe",
        edgecolor="#1d4ed8",
        linewidth=1.25,
        zorder=4,
    )
    ax.add_patch(chassis)
    ax.text(1.48, 3.79, "ChBody", ha="center", va="center", fontsize=8.2, weight="bold", color="#1e3a8a", zorder=5)

    for cx in (0.98, 2.02):
        ax.add_patch(Circle((cx, 3.10), 0.27, facecolor="#111827", edgecolor="#020617", zorder=4))
        ax.add_patch(Circle((cx, 3.10), 0.13, facecolor="#e5e7eb", edgecolor="#64748b", zorder=5))
    ax.plot([0.98, 2.02], [3.10, 3.10], color="#334155", linewidth=2.0, zorder=4)
    ax.text(1.50, 3.16, "link frame", ha="center", va="bottom", fontsize=6.8, color="#334155", zorder=6)

    theta = [0.45, 0.72, 0.99, 1.26, 1.53, 1.80]
    spring_x = [2.42, 2.54, 2.42, 2.54, 2.42, 2.54]
    ax.plot(spring_x, theta, color="#16a34a", linewidth=2.0, zorder=4)
    ax.plot([2.48, 2.48], [1.80, 2.92], color="#16a34a", linewidth=1.0, zorder=3)
    ax.plot([2.48, 2.02], [2.92, 3.10], color="#16a34a", linewidth=1.0, zorder=3)

    ax.add_patch(Rectangle((0.82, 1.20), 0.32, 0.08, facecolor="#fed7aa", edgecolor="#ea580c", zorder=5))
    ax.add_patch(Rectangle((1.86, 1.20), 0.32, 0.08, facecolor="#fed7aa", edgecolor="#ea580c", zorder=5))
    ax.add_patch(FancyArrowPatch((0.66, 3.10), (0.66, 3.38), arrowstyle="->", mutation_scale=11, color="#dc2626", linewidth=1.2, zorder=6))

    return {
        "body": (1.48, 3.95),
        "joint": (1.50, 3.10),
        "motor": (0.66, 3.34),
        "spring": (2.48, 1.45),
        "contact": (2.02, 1.24),
    }


def render_core_physics_solver_constraint_catalog() -> Path:
    output = IMAGES_RENDER / "core_physics_solver_constraint_catalog.png"
    fig, ax = plt.subplots(figsize=(11.4, 6.3))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.1)
    ax.axis("off")

    ax.text(5.0, 5.86, "Core physics component catalog: objects become solver contracts", ha="center", va="center", fontsize=12.6, weight="bold", color="#111827")
    ax.text(1.55, 5.36, "Component cards", ha="center", va="center", fontsize=9.4, color="#334155", weight="bold")
    ax.text(4.86, 5.36, "Runtime assembly", ha="center", va="center", fontsize=9.4, color="#334155", weight="bold")
    ax.text(8.30, 5.36, "Validation outputs", ha="center", va="center", fontsize=9.4, color="#334155", weight="bold")

    points = _mechanical_scene(ax)
    _label(ax, "Rigid Body\nmass, inertia, pose", (0.78, 4.72), points["body"], color="#1d4ed8")
    _label(ax, "Joint / Constraint\nbody pair + frames", (2.40, 4.66), points["joint"], color="#2563eb")
    _label(ax, "Motor / Actuator\nfunction + limits", (0.52, 2.42), points["motor"], color="#dc2626")
    _label(ax, "Spring / Damper\nk, c, rest length", (3.02, 2.22), points["spring"], color="#16a34a", ha="left")
    _label(ax, "Contact Material\nNSC/SMC compatible", (2.56, 0.62), points["contact"], color="#ea580c", ha="left")

    _box(
        ax,
        (3.72, 2.12),
        (2.38, 2.26),
        "",
        face="#eef2ff",
        edge="#4f46e5",
    )
    ax.text(
        4.91,
        4.12,
        "ChSystemNSC / ChSystemSMC\nRuntime physics context",
        ha="center",
        va="center",
        fontsize=9.3,
        weight="bold",
        color="#111827",
        zorder=6,
    )
    runtime_rows = [
        (3.94, 3.36, "contact method\nNSC or SMC", "#dbeafe", "#2563eb"),
        (3.94, 2.80, "solver\niterations + tolerance", "#fef3c7", "#d97706"),
        (3.94, 2.24, "timestepper + dt\nintegration contract", "#dcfce7", "#16a34a"),
    ]
    for x, y, label, face, edge in runtime_rows:
        _box(ax, (x, y), (1.94, 0.34), label, face=face, edge=edge, fontsize=7.4)

    _arrow(ax, (2.92, 3.18), (3.72, 3.56), color="#2563eb", rad=0.05)
    _arrow(ax, (2.74, 1.24), (3.72, 2.48), color="#ea580c", rad=-0.12)
    _arrow(ax, (2.76, 4.04), (3.72, 4.02), color="#1d4ed8", rad=0.02)
    _label(ax, "Add body/link/contactable\nobjects to the system", (4.05, 4.88), (3.86, 4.19), color="#4f46e5", ha="left")

    outputs = [
        ((7.26, 4.50), "run_metadata.json\nsolver, dt, backend", "#f8fafc", "#334155"),
        ((7.26, 3.62), "state CSV\npose + velocity", "#eff6ff", "#2563eb"),
        ((7.26, 2.74), "reaction/contact graph\nforces + counts", "#fef2f2", "#dc2626"),
        ((7.26, 1.86), "stability checklist\nviolations + drift", "#ecfdf5", "#16a34a"),
    ]
    for xy, label, face, edge in outputs:
        _box(ax, xy, (2.22, 0.52), label, face=face, edge=edge, fontsize=7.7)

    for end in [(7.26, 4.76), (7.26, 3.88), (7.26, 3.00), (7.26, 2.12)]:
        _arrow(ax, (6.10, 3.25), end, color="#475569", rad=0.03)

    _label(ax, "link reactions and\nconstraint violation", (6.78, 4.55), (7.26, 3.00), color="#334155", ha="right")
    _arrow(ax, (8.36, 1.86), (5.84, 2.46), color="#64748b", width=1.0, rad=-0.22, style="->")
    ax.text(7.22, 1.37, "bad peaks or drift feed back to solver/timestep review", ha="center", va="center", fontsize=7.5, color="#64748b")

    ax.text(
        5.0,
        0.10,
        "Component view: the card owns physical meaning; the Runtime owns numerical method; outputs prove that the contract behaved.",
        ha="center",
        va="center",
        fontsize=8.2,
        color="#475569",
    )
    return save_figure(fig, output)


if __name__ == "__main__":
    print(render_core_physics_solver_constraint_catalog())
