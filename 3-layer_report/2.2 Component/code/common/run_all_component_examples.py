from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
IMAGE_SCRIPT_RE = re.compile(r"\| `images/[^`]+\.png` \| `(?P<script>code/[^`]+\.py)` \|")
MANIFEST_SCRIPT = ROOT / "code" / "common" / "generate_component_artifact_manifest.py"
AREA_GENERATOR_SCRIPTS = [
    ROOT / "code" / "common" / "generate_chrono_default_shapes.py",
    ROOT / "code" / "common" / "generate_chrono_builtin_component_assets.py",
    ROOT / "code" / "rover_vehicle" / "generate_rover_vehicle_components.py",
    ROOT / "code" / "environment_terrain" / "generate_environment_terrain_components.py",
    ROOT / "code" / "collision_contact" / "generate_collision_contact_components.py",
    ROOT / "code" / "data_visualization" / "generate_data_visualization_components.py",
]


def load_image_scripts() -> list[Path]:
    scripts: list[Path] = []
    seen: set[Path] = set()
    for match in IMAGE_SCRIPT_RE.finditer(README.read_text(encoding="utf-8")):
        script = ROOT / match.group("script")
        if script in seen:
            continue
        if not script.exists():
            raise FileNotFoundError(f"README lists missing script: {script.relative_to(ROOT)}")
        scripts.append(script)
        seen.add(script)
    if not scripts:
        raise RuntimeError("No per-image scripts found in README image table.")
    return scripts


def main() -> int:
    failures = []
    print(f"Running {len(AREA_GENERATOR_SCRIPTS)} aggregate Component generators.")
    for script in AREA_GENERATOR_SCRIPTS:
        if not script.exists():
            failures.append((script, "missing"))
            continue
        print(f"\n=== running {script.relative_to(ROOT)} ===")
        result = subprocess.run([sys.executable, str(script)], cwd=ROOT, text=True)
        if result.returncode != 0:
            failures.append((script, result.returncode))
    if failures:
        print("\nFailures:")
        for script, code in failures:
            print(f"- {script}: exit {code}")
        return 1

    scripts = load_image_scripts()
    print(f"Running {len(scripts)} per-image Component generators from README.")
    for script in scripts:
        print(f"\n=== running {script.relative_to(ROOT)} ===")
        result = subprocess.run([sys.executable, str(script)], cwd=ROOT, text=True)
        if result.returncode != 0:
            failures.append((script, result.returncode))
    if failures:
        print("\nFailures:")
        for script, code in failures:
            print(f"- {script}: exit {code}")
        return 1
    print(f"\n=== running {MANIFEST_SCRIPT.relative_to(ROOT)} ===")
    result = subprocess.run([sys.executable, str(MANIFEST_SCRIPT)], cwd=ROOT, text=True)
    if result.returncode != 0:
        print(f"- {MANIFEST_SCRIPT}: exit {result.returncode}")
        return result.returncode
    print("\nAll Component example generators completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
