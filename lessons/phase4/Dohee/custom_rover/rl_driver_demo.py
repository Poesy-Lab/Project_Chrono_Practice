import argparse
from dataclasses import replace

from config import SIM_CONFIG, RESULTS_DIR
from simulation import run_simulation_case


def parse_args():
    parser = argparse.ArgumentParser(description="Run the dummy RL driver interface.")
    parser.add_argument(
        "--terrain",
        choices=["flat", "obstacles"],
        default="flat",
        help="terrain mode for the RL driver demo",
    )
    parser.add_argument(
        "--sim-time",
        type=float,
        default=25.0,
        help="simulation duration in seconds",
    )
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="show the Chrono/Irrlicht simulation window",
    )
    parser.add_argument(
        "--show-plots",
        action="store_true",
        help="open matplotlib path plots during the run",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    cfg = replace(
        SIM_CONFIG,
        control_mode="rl",
        experiment_name="rl_dummy",
        terrain_mode=args.terrain,
        sim_time_end=args.sim_time,
        enable_visualization=args.visualize,
        show_plots=args.show_plots,
    )

    output_dir = RESULTS_DIR / "rl_driver_demo"
    run_simulation_case(config=cfg, results_dir=output_dir)


if __name__ == "__main__":
    main()
