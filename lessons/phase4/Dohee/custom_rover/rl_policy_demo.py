import argparse
from pathlib import Path

from stable_baselines3 import PPO

from config import RESULTS_DIR
from rl_gym_env import CustomRoverRLEnv
from simulation import build_visual_system, save_attitude_plot, save_path_plot, save_rows


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate a trained PPO rover policy.")
    parser.add_argument("--terrain", choices=["flat", "obstacles"], default="flat")
    parser.add_argument("--model", type=Path, default=None)
    parser.add_argument("--steps", type=int, default=300)
    parser.add_argument("--episode-time", type=float, default=15.0)
    parser.add_argument("--visualize", action="store_true")
    parser.add_argument("--show-plots", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=RESULTS_DIR / "rl_policy_demo")
    return parser.parse_args()


def main():
    args = parse_args()
    model_path = args.model
    if model_path is None:
        model_path = RESULTS_DIR / "rl_training" / f"ppo_custom_rover_{args.terrain}.zip"

    model = PPO.load(model_path)
    env = CustomRoverRLEnv(
        terrain_mode=args.terrain,
        max_episode_time=args.episode_time,
    )

    obs, info = env.reset()
    vis = build_visual_system(env.system) if args.visualize else None
    total_reward = 0.0
    rows = []

    for step_index in range(args.steps):
        if vis is not None and not vis.Run():
            break

        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward

        if vis is not None:
            vis.BeginScene()
            vis.Render()
            vis.EndScene()

        state = env.rover.get_state(env.time)
        rows.append(
            {
                "time": state.time,
                "x": state.x,
                "y": state.y,
                "z": state.z,
                "roll_deg": state.roll_deg,
                "pitch_deg": state.pitch_deg,
                "yaw_deg": state.yaw_deg,
                "target_x": state.target_x,
                "target_y": state.target_y,
                "speed_cmd": state.speed_cmd,
                "steering_cmd": state.steering_cmd,
                "turn_mode": state.turn_mode,
                "wheel_omega": state.wheel_omega,
                "steer_left_deg": state.steer_left_deg,
                "steer_right_deg": state.steer_right_deg,
            }
        )

        if terminated or truncated:
            break

    args.output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.output_dir / f"custom_viper_{args.terrain}_ppo_policy.csv"
    path_plot = args.output_dir / f"custom_viper_{args.terrain}_ppo_policy_path.png"
    save_rows(rows, csv_path)
    save_path_plot(rows, path_plot, args.show_plots, show_waypoints=True)
    attitude_plot = save_attitude_plot(rows, path_plot, args.show_plots)

    env.close()
    print(
        "[Done]"
        f" total_reward={total_reward:.3f}"
        f" waypoint={info['waypoint_index']}"
        f" distance={info['distance_to_target']:.3f}"
    )
    print(f"[Done] Saved log to {csv_path}")
    print(f"[Done] Saved path plot to {path_plot}")
    print(f"[Done] Saved attitude plot to {attitude_plot}")


if __name__ == "__main__":
    main()
