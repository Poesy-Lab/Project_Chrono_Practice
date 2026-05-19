import pychrono as chrono
import pychrono.vehicle as veh
import pychrono.robot as robot
from pychrono import irrlicht as chronoirr


# =========================
# System
# =========================
system = chrono.ChSystemNSC()
system.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)
system.SetGravitationalAcceleration(chrono.ChVector3d(0, 0, -9.81))

chrono.ChCollisionModel.SetDefaultSuggestedEnvelope(0.0025)
chrono.ChCollisionModel.SetDefaultSuggestedMargin(0.0025)


# =========================
# RigidTerrain
# =========================
terrain_mat = chrono.ChContactMaterialNSC()
terrain_mat.SetFriction(0.9)
terrain_mat.SetRestitution(0.02)

terrain = veh.RigidTerrain(system)

patch = terrain.AddPatch(
    terrain_mat,
    chrono.ChCoordsysd(
        chrono.ChVector3d(0, 0, 0),
        chrono.QUNIT
    ),
    40.0,
    40.0
)

patch.SetTexture(
    veh.GetVehicleDataFile("terrain/textures/tile4.jpg"),
    80,
    80
)

terrain.Initialize()


# =========================
# Wall
# =========================
wall_mat = chrono.ChContactMaterialNSC()
wall_mat.SetFriction(0.9)
wall_mat.SetRestitution(0.25)

wall = chrono.ChBodyEasyBox(
    0.5,
    10.0,
    2.0,
    1000,
    True,
    True,
    wall_mat
)

# 공식 데모 로버 진행 방향 기준으로 앞쪽에 둠
wall.SetPos(
    chrono.ChVector3d(
        6.0,
        0.0,
        1.0
    )
)

wall.SetFixed(True)
system.Add(wall)


# =========================
# Curiosity Rover
# =========================
driver = robot.CuriosityDCMotorControl()

rover = robot.Curiosity(system)
rover.SetDriver(driver)

rover.Initialize(
    chrono.ChFramed(
        chrono.ChVector3d(0, 0.2, 0),
        chrono.ChQuaterniond(1, 0, 0, 0)
    )
)


# =========================
# Visualization
# =========================
vis = chronoirr.ChVisualSystemIrrlicht()
vis.AttachSystem(system)

vis.SetCameraVertical(chrono.CameraVerticalDir_Z)
vis.SetWindowSize(1280, 720)
vis.SetWindowTitle("Curiosity Rover - RigidTerrain Wall Test")

vis.Initialize()
vis.AddLogo(chrono.GetChronoDataFile("logo_chrono_alpha.png"))
vis.AddSkyBox()

vis.AddCamera(
    chrono.ChVector3d(0, 5, 3),
    chrono.ChVector3d(3, 0, 0.5)
)

vis.AddTypicalLights()
vis.AddLightWithShadow(
    chrono.ChVector3d(1.5, -2.5, 5.5),
    chrono.ChVector3d(0, 0, 0),
    3,
    4,
    10,
    40,
    512
)


# =========================
# Simulation loop
# =========================
time_step = 2e-3
time = 0.0

while vis.Run():

    time += time_step

    # 공식 데모와 동일하게 driver는 steering만 건드림
    # 직진 유지
    driver.SetSteering(0.0)

    rover.Update()

    terrain.Synchronize(time)

    vis.BeginScene()
    vis.Render()
    vis.EndScene()

    terrain.Advance(time_step)
    system.DoStepDynamics(time_step)