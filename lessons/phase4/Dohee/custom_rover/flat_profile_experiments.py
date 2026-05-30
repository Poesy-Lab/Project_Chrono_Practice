import argparse
import csv
import math
from dataclasses import replace
from pathlib import Path

import matplotlib.pyplot as plt

from config import SIM_CONFIG, RESULTS_DIR
from simulation import run_simulation_case


EXPERIMENTS = [
    ("straight", 14.0),
    ("step_turn", 16.0),
    ("slalom", 18.0),
    ("pivot_turn", 10.0),
]


OUTPUT_DIR = RESULTS_DIR / "flat_profile_experiments"


def unwrap_degrees(values):
    if not values:
        return []

    result = [values[0]]
    offset = 0.0
    previous = values[0]

    for value in values[1:]:
        delta = value - previous
        if delta > 180.0:
            offset -= 360.0
        elif delta < -180.0:
            offset += 360.0
        result.append(value + offset)
        previous = value

    return result


def compute_metrics(name, rows):
    if len(rows) < 2:
        return {
            "experiment": name,
            "duration_s": 0.0,
            "path_length_m": 0.0,
            "final_x_m": 0.0,
            "final_y_m": 0.0,
            "max_abs_y_m": 0.0,
            "yaw_change_deg": 0.0,
            "max_abs_yaw_rate_deg_s": 0.0,
            "mean_speed_m_s": 0.0,
            "max_speed_m_s": 0.0,
        }

    times = [row["time"] for row in rows]
    xs = [row["x"] for row in rows]
    ys = [row["y"] for row in rows]
    yaws = unwrap_degrees([row["yaw_deg"] for row in rows])
    rolls = [row["roll_deg"] for row in rows]
    pitches = [row["pitch_deg"] for row in rows]

    segment_lengths = [
        math.hypot(xs[i] - xs[i - 1], ys[i] - ys[i - 1])
        for i in range(1, len(rows))
    ]
    speeds = []
    yaw_rates = []

    for i in range(1, len(rows)):
        dt = times[i] - times[i - 1]
        if dt <= 0.0:
            continue
        speeds.append(segment_lengths[i - 1] / dt)
        yaw_rates.append((yaws[i] - yaws[i - 1]) / dt)

    duration = times[-1] - times[0]
    path_length = sum(segment_lengths)

    return {
        "experiment": name,
        "duration_s": duration,
        "path_length_m": path_length,
        "final_x_m": xs[-1],
        "final_y_m": ys[-1],
        "max_abs_y_m": max(abs(y) for y in ys),
        "yaw_change_deg": yaws[-1] - yaws[0],
        "max_abs_yaw_rate_deg_s": max((abs(v) for v in yaw_rates), default=0.0),
        "mean_speed_m_s": path_length / duration if duration > 0.0 else 0.0,
        "max_speed_m_s": max(speeds, default=0.0),
    }


def save_response_plot(name, rows, output_dir):
    if not rows:
        return None

    times = [row["time"] for row in rows]
    xs = [row["x"] for row in rows]
    ys = [row["y"] for row in rows]
    yaws = unwrap_degrees([row["yaw_deg"] for row in rows])
    rolls = [row["roll_deg"] for row in rows]
    pitches = [row["pitch_deg"] for row in rows]
    speed_cmds = [row["speed_cmd"] for row in rows]
    steering_cmds = [row["steering_cmd"] for row in rows]
    turn_modes = [row["turn_mode"] for row in rows]

    speeds = [0.0]
    yaw_rates = [0.0]
    for i in range(1, len(rows)):
        dt = times[i] - times[i - 1]
        if dt <= 0.0:
            speeds.append(speeds[-1])
            yaw_rates.append(yaw_rates[-1])
            continue
        speeds.append(math.hypot(xs[i] - xs[i - 1], ys[i] - ys[i - 1]) / dt)
        yaw_rates.append((yaws[i] - yaws[i - 1]) / dt)

    path = output_dir / f"custom_viper_flat_{name}_response.png"

    fig, axes = plt.subplots(5, 1, figsize=(10, 11), sharex=True)
    axes[0].plot(times, speed_cmds, label="speed command")
    axes[0].plot(times, speeds, label="estimated speed")
    axes[0].set_ylabel("speed [m/s]")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()

    axes[1].plot(times, steering_cmds, label="steering command")
    axes[1].plot(times, turn_modes, label="turn mode")
    axes[1].set_ylabel("input [-]")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()

    axes[2].plot(times, yaws, label="yaw")
    axes[2].plot(times, yaw_rates, label="yaw rate")
    axes[2].set_ylabel("deg / deg/s")
    axes[2].grid(True, alpha=0.3)
    axes[2].legend()

    axes[3].plot(times, xs, label="x")
    axes[3].plot(times, ys, label="y")
    axes[3].set_ylabel("position [m]")
    axes[3].grid(True, alpha=0.3)
    axes[3].legend()

    axes[4].plot(times, rolls, label="roll")
    axes[4].plot(times, pitches, label="pitch")
    axes[4].set_xlabel("time [s]")
    axes[4].set_ylabel("attitude [deg]")
    axes[4].grid(True, alpha=0.3)
    axes[4].legend()

    fig.suptitle(f"Flat Terrain Profile Response: {name}")
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def save_summary(summary_rows, output_dir):
    summary_csv = output_dir / "flat_profile_summary.csv"
    fieldnames = [
        "experiment",
        "duration_s",
        "path_length_m",
        "final_x_m",
        "final_y_m",
        "max_abs_y_m",
        "yaw_change_deg",
        "max_abs_yaw_rate_deg_s",
        "mean_speed_m_s",
        "max_speed_m_s",
    ]

    with open(summary_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)

    names = [row["experiment"] for row in summary_rows]
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    axes = axes.ravel()

    plots = [
        ("path_length_m", "path length [m]"),
        ("max_abs_y_m", "max |y| [m]"),
        ("yaw_change_deg", "yaw change [deg]"),
        ("max_abs_yaw_rate_deg_s", "max |yaw rate| [deg/s]"),
    ]

    for ax, (key, label) in zip(axes, plots):
        ax.bar(names, [row[key] for row in summary_rows], color="#4b78a8")
        ax.set_ylabel(label)
        ax.grid(True, axis="y", alpha=0.3)
        ax.tick_params(axis="x", rotation=20)

    fig.suptitle("Flat Terrain Profile Experiment Summary")
    fig.tight_layout()
    summary_plot = output_dir / "flat_profile_summary.png"
    fig.savefig(summary_plot, dpi=180)
    plt.close(fig)

    return summary_csv, summary_plot


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run flat-terrain profile experiments for the custom rover."
    )
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="show the Chrono/Irrlicht simulation window while each experiment runs",
    )
    parser.add_argument(
        "--show-plots",
        action="store_true",
        help="open matplotlib path plots during the run",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    summary_rows = []

    for experiment_name, sim_time_end in EXPERIMENTS:
        cfg = replace(
            SIM_CONFIG,
            control_mode="profiles",
            experiment_name=experiment_name,
            terrain_mode="flat",
            enable_visualization=args.visualize,
            show_plots=args.show_plots,
            sim_time_end=sim_time_end,
        )

        print(f"[Run] flat profile experiment: {experiment_name}")
        rows, csv_path, path_plot = run_simulation_case(config=cfg, results_dir=OUTPUT_DIR)
        response_plot = save_response_plot(experiment_name, rows, OUTPUT_DIR)
        summary_rows.append(compute_metrics(experiment_name, rows))

        print(f"[Done] {experiment_name}")
        print(f"       csv     : {csv_path}")
        print(f"       path    : {path_plot}")
        print(f"       response: {response_plot}")

    summary_csv, summary_plot = save_summary(summary_rows, OUTPUT_DIR)
    print("[Done] flat profile experiment batch")
    print(f"       summary csv : {summary_csv}")
    print(f"       summary plot: {summary_plot}")


if __name__ == "__main__":
    main()
