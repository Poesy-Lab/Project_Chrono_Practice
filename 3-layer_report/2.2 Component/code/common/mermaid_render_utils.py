from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MERMAID_DIR = ROOT / "images" / "mermaid_rendered"
CONFIG = MERMAID_DIR / "mermaid_config.json"


def png_is_current(source: Path, output: Path) -> bool:
    return output.exists() and output.stat().st_mtime >= source.stat().st_mtime


def _matplotlib_parts():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

    return plt, FancyArrowPatch, FancyBboxPatch


def _save_local_mermaid(fig, output: Path) -> Path:
    plt, _, _ = _matplotlib_parts()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output, dpi=180, bbox_inches="tight", pad_inches=0.12, transparent=True)
    plt.close(fig)
    return output


def _local_box(ax, center, size, label, *, face, edge, fontsize=8.0, weight="normal"):
    _, _, FancyBboxPatch = _matplotlib_parts()
    x = center[0] - size[0] / 2
    y = center[1] - size[1] / 2
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            size[0],
            size[1],
            boxstyle="round,pad=0.035,rounding_size=0.08",
            facecolor=face,
            edgecolor=edge,
            linewidth=1.2,
            zorder=4,
        )
    )
    ax.text(center[0], center[1], label, ha="center", va="center", fontsize=fontsize, color="#111827", weight=weight, zorder=5)
    return center


def _local_arrow(ax, start, end, *, color="#64748b", rad=0.0, style="-|>"):
    _, FancyArrowPatch, _ = _matplotlib_parts()
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle=style,
            mutation_scale=11,
            linewidth=1.05,
            color=color,
            connectionstyle=f"arc3,rad={rad}",
            shrinkA=9,
            shrinkB=9,
            zorder=3,
        )
    )


def _render_local_terrain_mermaid(output: Path) -> Path:
    plt, _, _ = _matplotlib_parts()
    fig, ax = plt.subplots(figsize=(7.6, 5.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis("off")

    ax.text(5.0, 6.65, "Environment / Terrain component tree", ha="center", va="center", fontsize=12.0, weight="bold", color="#111827")
    root = _local_box(ax, (5.0, 5.85), (2.35, 0.50), "Environment /\nTerrain", face="#ecfeff", edge="#0891b2", fontsize=8.8, weight="bold")

    base = _local_box(ax, (1.55, 4.62), (1.90, 0.54), "Base\nscene objects", face="#f8fafc", edge="#475569", fontsize=7.6, weight="bold")
    rigid = _local_box(ax, (4.00, 4.62), (1.90, 0.54), "Rigid\nVehicle terrain", face="#eff6ff", edge="#2563eb", fontsize=7.6, weight="bold")
    deform = _local_box(ax, (6.45, 4.62), (1.90, 0.54), "Deformable\nsoil / particles", face="#f0fdf4", edge="#16a34a", fontsize=7.6, weight="bold")
    field = _local_box(ax, (8.70, 4.62), (1.60, 0.54), "Field\ngravity / wind", face="#fff7ed", edge="#ea580c", fontsize=7.3, weight="bold")

    for node in (base, rigid, deform, field):
        _local_arrow(ax, root, node, color="#64748b")

    ground = _local_box(ax, (0.92, 3.38), (1.38, 0.46), "Ground\nfixed body", face="#ffffff", edge="#64748b", fontsize=6.9)
    obstacle = _local_box(ax, (2.18, 3.38), (1.38, 0.46), "Obstacle\nbody", face="#ffffff", edge="#64748b", fontsize=6.9)
    material = _local_box(ax, (1.55, 2.50), (1.50, 0.46), "Contact\nmaterial map", face="#fff7ed", edge="#d97706", fontsize=6.8)
    patch = _local_box(ax, (4.00, 3.38), (1.70, 0.50), "RigidTerrain\nbox / mesh / heightmap", face="#ffffff", edge="#2563eb", fontsize=6.8)
    scm = _local_box(ax, (6.45, 3.38), (1.70, 0.50), "SCM\nBekker / Mohr-Coulomb", face="#ffffff", edge="#16a34a", fontsize=6.8)
    granular = _local_box(ax, (6.45, 2.50), (1.70, 0.50), "Granular / FEA / CRM\nmodule domain", face="#ffffff", edge="#16a34a", fontsize=6.8)
    gravity = _local_box(ax, (8.70, 3.38), (1.46, 0.46), "scenario\nfield input", face="#ffffff", edge="#ea580c", fontsize=6.8)
    friction = _local_box(ax, (0.96, 1.62), (1.10, 0.40), "friction", face="#ffffff", edge="#d97706", fontsize=6.7)
    restitution = _local_box(ax, (2.10, 1.62), (1.16, 0.40), "restitution", face="#ffffff", edge="#d97706", fontsize=6.7)

    for node in (ground, obstacle, material):
        _local_arrow(ax, base, node, color="#64748b")
    _local_arrow(ax, rigid, patch, color="#2563eb")
    for node in (scm, granular):
        _local_arrow(ax, deform, node, color="#16a34a")
    _local_arrow(ax, field, gravity, color="#ea580c")
    _local_arrow(ax, material, friction, color="#d97706")
    _local_arrow(ax, material, restitution, color="#d97706")

    return _save_local_mermaid(fig, output)


def _render_local_contact_sequence(output: Path) -> Path:
    plt, _, _ = _matplotlib_parts()
    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.4)
    ax.axis("off")

    ax.text(5.0, 6.08, "Collision contact logging sequence", ha="center", va="center", fontsize=12.0, weight="bold", color="#111827")
    participants = [
        ("Body", "ChBody\nshape", 0.9, "#2563eb"),
        ("Solver", "Contact\nsolver", 2.55, "#4f46e5"),
        ("Container", "Contact\ncontainer", 4.25, "#0891b2"),
        ("Reporter", "Contact\nreporter", 5.95, "#16a34a"),
        ("Logger", "CSV\nlogger", 7.55, "#d97706"),
        ("Graph", "Graph\ngenerator", 9.05, "#dc2626"),
    ]
    xs = {}
    for key, label, x, color in participants:
        xs[key] = x
        _local_box(ax, (x, 5.32), (1.14, 0.54), label, face="#ffffff", edge=color, fontsize=6.9, weight="bold")
        ax.plot([x, x], [1.00, 5.03], color="#cbd5e1", linewidth=0.8, linestyle="--", zorder=1)

    messages = [
        ("Body", "Solver", "candidates + constraints", 4.55, "#2563eb"),
        ("Solver", "Container", "points, normal, force", 3.86, "#4f46e5"),
        ("Container", "Reporter", "ReportAllContacts", 3.17, "#0891b2"),
        ("Reporter", "Logger", "count, pair, force xyz", 2.48, "#16a34a"),
        ("Logger", "Graph", "write CSV", 1.79, "#d97706"),
    ]
    for start, end, label, y, color in messages:
        _local_arrow(ax, (xs[start] + 0.40, y), (xs[end] - 0.40, y), color=color)
        ax.text((xs[start] + xs[end]) / 2, y + 0.15, label, ha="center", va="bottom", fontsize=6.6, color="#334155", zorder=6)

    _local_box(ax, (xs["Graph"], 1.23), (1.18, 0.46), "force / count\nevent plots", face="#ffffff", edge="#dc2626", fontsize=6.3)

    return _save_local_mermaid(fig, output)


def _render_local_mermaid(index: int, output: Path) -> Path | None:
    if index == 4:
        return _render_local_terrain_mermaid(output)
    if index == 5:
        return _render_local_contact_sequence(output)
    return None


def render_mermaid(index: int) -> Path:
    source = MERMAID_DIR / f"2_2_mermaid_{index:02d}.mmd"
    output = MERMAID_DIR / f"2_2_mermaid_{index:02d}.png"
    if not source.exists():
        raise FileNotFoundError(source)

    mmdc = shutil.which("mmdc")
    if mmdc:
        command = [mmdc, "-i", str(source), "-o", str(output), "-b", "transparent"]
        if CONFIG.exists():
            command.extend(["-c", str(CONFIG)])
        subprocess.run(command, check=True)
        return output

    local_output = _render_local_mermaid(index, output)
    if local_output is not None:
        print(f"mmdc not found; rendered local fallback {output}")
        return local_output

    if png_is_current(source, output):
        print(f"mmdc not found; keeping existing {output}")
        return output
    if output.exists():
        raise RuntimeError(f"mmdc is not installed and {source.name} is newer than {output.name}")
    raise RuntimeError(f"mmdc is not installed and {output} does not exist")
