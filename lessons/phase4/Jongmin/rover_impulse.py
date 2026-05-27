import pychrono as chrono
import pychrono.vehicle as veh
import pychrono.robot as robot
from pychrono import irrlicht as chronoirr
import matplotlib.pyplot as plt


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
wall_mat.SetRestitution(0.02)

wall = chrono.ChBodyEasyBox(
    0.5,
    10.0,
    2.0,
    1000,
    True,
    True,
    wall_mat
)

wall.SetPos(
    chrono.ChVector3d(
        7.0,
        0.0,
        1.0
    )
)

wall.SetFixed(True)
system.Add(wall)


# =========================
# Curiosity Rover
# =========================
driver = robot.CuriositySpeedDriver(0.2, 7.0)

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
vis.SetWindowTitle("Curiosity Rover - Initial Impact Measurement")

vis.Initialize()
vis.AddLogo(chrono.GetChronoDataFile("logo_chrono_alpha.png"))
vis.AddSkyBox()

vis.AddCamera(
    chrono.ChVector3d(0, 6, 4),
    chrono.ChVector3d(4, 0, 0.6)
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
# Impact data
# =========================
time_list = []
force_list = []
impulse_list = []

total_impulse = 0.0
max_force = 0.0

impact_started = False
impact_start_time = None

force_threshold = 100.0
impact_window = 0.8


# =========================
# Simulation loop
# =========================
time_step = 2e-3
time = 0.0

while vis.Run():

    time += time_step

    driver.SetSteering(0.0)

    rover.Update()

    terrain.Synchronize(time)

    vis.BeginScene()
    vis.Render()
    vis.EndScene()

    terrain.Advance(time_step)
    system.DoStepDynamics(time_step)

    contact_force = wall.GetContactForce()
    force_magnitude = contact_force.Length()

    if not impact_started and force_magnitude > force_threshold:
        impact_started = True
        impact_start_time = time
        print(f"Impact started at {impact_start_time:.3f} s")

    if impact_started:
        local_time = time - impact_start_time

        impulse_step = force_magnitude * time_step
        total_impulse += impulse_step

        if force_magnitude > max_force:
            max_force = force_magnitude

        time_list.append(local_time)
        force_list.append(force_magnitude)
        impulse_list.append(total_impulse)

        if local_time >= impact_window:
            break


print("========== Initial Impact Result ==========")
print(f"Impact duration   : {impact_window:.3f} s")
print(f"Max contact force : {max_force:.3f} N")
print(f"Impact impulse    : {total_impulse:.3f} N*s")
print("===========================================")


plt.figure()
plt.plot(time_list, force_list)
plt.xlabel("Time after impact [s]")
plt.ylabel("Contact Force [N]")
plt.title("Initial Wall Contact Force")
plt.grid(True)

plt.figure()
plt.plot(time_list, impulse_list)
plt.xlabel("Time after impact [s]")
plt.ylabel("Impulse [N*s]")
plt.title("Initial Impact Impulse")
plt.grid(True)

plt.show()