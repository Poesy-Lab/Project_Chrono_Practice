from __future__ import annotations

import shutil
from pathlib import Path

import matplotlib.pyplot as plt

from mermaid_render_utils import ROOT, MERMAID_DIR, png_is_current, render_mermaid


def render_data_flow_fallback() -> Path:
    output = ROOT / "images" / "mermaid_rendered" / "2_2_mermaid_06.png"
    fig, ax = plt.subplots(figsize=(12.5, 6.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis("off")

    nodes = {
        "Sim": (1.2, 3.2, "Chrono\nSimulation Loop"),
        "State": (3.2, 5.0, "State\nLogger"),
        "Control": (3.2, 4.0, "Control\nLogger"),
        "Contact": (3.2, 3.0, "Contact\nLogger"),
        "Render": (10.0, 1.0, "Render /\nScreenshot"),
        "Meta": (10.0, 2.2, "Metadata\nLogger"),
        "Manager": (3.2, 2.0, "ChSensor\nManager"),
        "Sensors": (5.2, 2.0, "Sensor\nComponents"),
        "Filters": (7.0, 2.0, "Filter\nChain"),
        "SensorFiles": (8.4, 2.4, "Sensor Files /\nBuffers"),
        "CSV": (7.0, 4.6, "CSV\nSchema"),
        "Graph": (9.2, 4.6, "Graph\nGenerator"),
        "Report": (11.3, 4.6, "Markdown\nReport"),
    }
    edges = [
        ("Sim", "State"),
        ("Sim", "Control"),
        ("Sim", "Contact"),
        ("Sim", "Manager"),
        ("State", "CSV"),
        ("Control", "CSV"),
        ("Contact", "CSV"),
        ("Manager", "Sensors"),
        ("Sensors", "Filters"),
        ("Filters", "SensorFiles"),
        ("CSV", "Graph"),
        ("Graph", "Report"),
    ]

    for key, (x, y, label) in nodes.items():
        ax.text(
            x,
            y,
            label,
            ha="center",
            va="center",
            fontsize=9,
            color="#111827",
            bbox={"boxstyle": "round,pad=0.35", "facecolor": "#f8fafc", "edgecolor": "#334155", "linewidth": 1.1},
            zorder=3,
        )
    for start, end in edges:
        sx, sy, _ = nodes[start]
        ex, ey, _ = nodes[end]
        ax.annotate(
            "",
            xy=(ex - 0.58 if ex > sx else ex + 0.58, ey),
            xytext=(sx + 0.58 if ex > sx else sx - 0.58, sy),
            arrowprops={"arrowstyle": "-|>", "color": "#475569", "linewidth": 1.45, "mutation_scale": 14, "shrinkA": 0, "shrinkB": 0},
            zorder=2,
        )
    sensor_x, sensor_y, _ = nodes["SensorFiles"]
    csv_x, csv_y, _ = nodes["CSV"]
    ax.plot([sensor_x, sensor_x], [sensor_y + 0.45, csv_y - 0.48], color="#475569", linewidth=1.45, zorder=2)
    ax.annotate(
        "",
        xy=(csv_x + 0.58, csv_y),
        xytext=(sensor_x, csv_y - 0.48),
        arrowprops={"arrowstyle": "-|>", "color": "#475569", "linewidth": 1.45, "mutation_scale": 14, "shrinkA": 0, "shrinkB": 0},
        zorder=2,
    )
    for start_key, end_xy in (("Render", (10.92, 4.28)), ("Meta", (11.42, 4.28))):
        sx, sy, _ = nodes[start_key]
        ax.annotate(
            "",
            xy=end_xy,
            xytext=(sx + 0.58, sy),
            arrowprops={"arrowstyle": "-|>", "color": "#475569", "linewidth": 1.45, "mutation_scale": 14, "shrinkA": 0, "shrinkB": 0},
            zorder=2,
        )

    fig.savefig(output, dpi=220, bbox_inches="tight", transparent=True)
    plt.close(fig)
    return output


if __name__ == "__main__":
    if shutil.which("mmdc"):
        print(render_mermaid(6))
    else:
        print(render_data_flow_fallback())
