from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = [
    ROOT / "code" / "rover_vehicle" / "generate_rover_vehicle_components.py",
    ROOT / "code" / "environment_terrain" / "generate_environment_terrain_components.py",
    ROOT / "code" / "collision_contact" / "generate_collision_contact_components.py",
    ROOT / "code" / "data_visualization" / "generate_data_visualization_components.py",
]


def main() -> int:
    failures = []
    for script in SCRIPTS:
        print(f"\n=== running {script.relative_to(ROOT)} ===")
        result = subprocess.run([sys.executable, str(script)], cwd=ROOT, text=True)
        if result.returncode != 0:
            failures.append((script, result.returncode))
    if failures:
        print("\nFailures:")
        for script, code in failures:
            print(f"- {script}: exit {code}")
        return 1
    print("\nAll Component example generators completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
