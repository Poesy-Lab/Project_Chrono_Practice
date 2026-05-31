#!/usr/bin/env python
"""Run from repository root:

    source ~/anaconda3/etc/profile.d/conda.sh
    conda activate chrono
    source setup_chrono_env.sh
    python 3-layer_report/Component/code/common/vsg_smoke_test.py

This opens a minimal Chrono::VSG window, renders one frame, writes a PNG, and
then calls Quit() immediately. It is intentionally small so it can be used
before running the full Component report generation scripts.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "outputs" / "raw" / "vsg_smoke_test.png"


def main() -> int:
    import pychrono as chrono
    import pychrono.vsg3d as vsg

    system = chrono.ChSystemNSC()
    system.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)
    system.SetGravitationalAcceleration(chrono.ChVector3d(0, 0, -9.81))

    mat = chrono.ChContactMaterialNSC()
    mat.SetFriction(0.7)

    ground = chrono.ChBodyEasyBox(2.0, 1.4, 0.05, 1000, True, True, mat)
    ground.SetName("vsg_smoke_ground")
    ground.SetFixed(True)
    ground.SetPos(chrono.ChVector3d(0, 0, -0.025))
    ground.GetVisualShape(0).SetColor(chrono.ChColor(0.72, 0.72, 0.68))
    system.AddBody(ground)

    box = chrono.ChBodyEasyBox(0.45, 0.32, 0.28, 700, True, True, mat)
    box.SetName("vsg_smoke_box")
    box.SetPos(chrono.ChVector3d(0, 0, 0.16))
    box.GetVisualShape(0).SetColor(chrono.ChColor(0.18, 0.42, 0.72))
    system.AddBody(box)

    vis = vsg.ChVisualSystemVSG()
    vis.AttachSystem(system)
    vis.SetCameraVertical(chrono.CameraVerticalDir_Z)
    vis.SetWindowSize(400, 300)
    vis.SetWindowPosition(80, 80)
    vis.SetWindowTitle("Chrono VSG smoke test")
    vis.AddCamera(chrono.ChVector3d(1.3, -1.8, 0.9), chrono.ChVector3d(0, 0, 0.1))
    vis.SetCameraAngleDeg(38)
    vis.SetLightIntensity(1.0)
    vis.SetLightDirection(chrono.CH_PI_4, chrono.CH_PI_4)
    vis.Initialize()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    vis.Render()
    vis.WriteImageToFile(str(OUTPUT))
    vis.Render()
    vis.Quit()

    if not OUTPUT.exists() or OUTPUT.stat().st_size == 0:
        raise RuntimeError(f"VSG did not create a screenshot: {OUTPUT}")

    print(f"VSG smoke test OK: {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
