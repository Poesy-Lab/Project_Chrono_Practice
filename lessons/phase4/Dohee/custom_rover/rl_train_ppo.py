import argparse
from pathlib import Path

from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor

from config import RESULTS_DIR
from rl_gym_env import CustomRoverRLEnv


def parse_args():
    parser = argparse.ArgumentParser(description="Train PPO on the custom rover env.")
    parser.add_argument("--terrain", choices=["flat", "obstacles"], default="flat")
    parser.add_argument("--timesteps", type=int, default=512)
    parser.add_argument("--episode-time", type=float, default=12.0)
    parser.add_argument("--output-dir", type=Path, default=RESULTS_DIR / "rl_training")
    return parser.parse_args()


def main():
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    env = Monitor(
        CustomRoverRLEnv(
            terrain_mode=args.terrain,
            max_episode_time=args.episode_time,
        ),
        filename=str(args.output_dir / f"monitor_{args.terrain}.csv"),
    )

    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        n_steps=32,
        batch_size=32,
        gamma=0.98,
    )
    model.learn(total_timesteps=args.timesteps)

    model_path = args.output_dir / f"ppo_custom_rover_{args.terrain}"
    model.save(model_path)
    env.close()

    print(f"[Done] Saved PPO model to {model_path}.zip")


if __name__ == "__main__":
    main()
