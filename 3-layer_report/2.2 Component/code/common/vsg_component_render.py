from __future__ import annotations

from pathlib import Path
from typing import Callable


def _set_color(body, chrono, rgb: tuple[float, float, float]) -> None:
    try:
        body.GetVisualShape(0).SetColor(chrono.ChColor(*rgb))
    except Exception:
        pass


def add_box(system, chrono, name: str, pos, size, color, fixed: bool = True, collide: bool = True, rot_z: float = 0.0):
    mat = chrono.ChContactMaterialNSC()
    mat.SetFriction(0.65)
    body = chrono.ChBodyEasyBox(size[0], size[1], size[2], 1000, True, collide, mat)
    body.SetName(name)
    body.SetPos(chrono.ChVector3d(*pos))
    if rot_z:
        body.SetRot(chrono.QuatFromAngleZ(rot_z))
    body.SetFixed(fixed)
    _set_color(body, chrono, color)
    system.AddBody(body)
    return body


def add_cylinder_y(system, chrono, name: str, pos, radius: float, length: float, color, fixed: bool = True, collide: bool = True):
    mat = chrono.ChContactMaterialNSC()
    mat.SetFriction(0.85)
    body = chrono.ChBodyEasyCylinder(chrono.ChAxis_Y, radius, length, 1000, True, collide, mat)
    body.SetName(name)
    body.SetPos(chrono.ChVector3d(*pos))
    body.SetFixed(fixed)
    _set_color(body, chrono, color)
    system.AddBody(body)
    return body


def add_sphere(system, chrono, name: str, pos, radius: float, color, fixed: bool = True, collide: bool = True):
    mat = chrono.ChContactMaterialNSC()
    mat.SetFriction(0.65)
    body = chrono.ChBodyEasySphere(radius, 1000, True, collide, mat)
    body.SetName(name)
    body.SetPos(chrono.ChVector3d(*pos))
    body.SetFixed(fixed)
    _set_color(body, chrono, color)
    system.AddBody(body)
    return body


def add_grid(vis, chrono, z: float = 0.0) -> None:
    try:
        vis.AddGrid(0.25, 0.25, 16, 12, chrono.ChCoordsysd(chrono.ChVector3d(0, 0, z), chrono.QUNIT), chrono.ChColor(0.35, 0.35, 0.35))
    except Exception:
        pass


def render_vsg_scene(
    output_path: Path,
    build_scene: Callable,
    *,
    camera=(3.0, -4.0, 2.0),
    target=(0.0, 0.0, 0.35),
    title="Chrono VSG Component Render",
    width=900,
    height=580,
) -> tuple[bool, str]:
    try:
        import pychrono as chrono
        import pychrono.vsg3d as vsg

        system = chrono.ChSystemNSC()
        system.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)
        system.SetGravitationalAcceleration(chrono.ChVector3d(0, 0, -9.81))

        build_scene(system, chrono)

        vis = vsg.ChVisualSystemVSG()
        vis.AttachSystem(system)
        vis.SetCameraVertical(chrono.CameraVerticalDir_Z)
        vis.SetWindowSize(width, height)
        vis.SetWindowPosition(60, 60)
        vis.SetWindowTitle(title)
        vis.AddCamera(chrono.ChVector3d(*camera), chrono.ChVector3d(*target))
        vis.SetCameraAngleDeg(38)
        vis.SetLightIntensity(1.15)
        vis.SetLightDirection(chrono.CH_PI_4, chrono.CH_PI_4)
        add_grid(vis, chrono)
        vis.Initialize()

        output_path.parent.mkdir(parents=True, exist_ok=True)
        vis.Render()
        vis.WriteImageToFile(str(output_path))
        vis.Render()
        vis.Quit()

        ok = output_path.exists() and output_path.stat().st_size > 0
        return ok, "VSG" if ok else "VSG failed: no image file was produced"
    except Exception as exc:
        return False, f"VSG failed: {type(exc).__name__}: {exc}"
