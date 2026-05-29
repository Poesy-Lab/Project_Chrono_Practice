import pychrono as chrono
import pychrono.vehicle as veh
import pychrono.robot as robot
from pychrono import irrlicht as chronoirr
import numpy as np
import matplotlib.pyplot as plt


# =========================
# Settings
# =========================
time_step = 1.5e-3

terrain_length = 42.0
terrain_width = 24.0
heightmap_file = "scm_pockmarked_mars_heightmap.png"

terrain_delta = 0.10

h_min = -0.75
h_max = 0.85


# =========================
# Height function
# =========================
def terrain_height(x, y):
    z = 0.0

    spacing_x = 1.6
    spacing_y = 1.35

    x_centers = np.arange(-14.0, 20.0, spacing_x)
    y_centers = np.arange(-9.0, 9.0, spacing_y)

    for i, cx in enumerate(x_centers):
        for j, cy in enumerate(y_centers):

            cx2 = cx + (0.45 if j % 2 == 0 else -0.15)
            cy2 = cy + 0.20 * np.sin(i * 0.8)

            dx = x - cx2
            dy = y - cy2

            rx = 0.75 + 0.18 * np.sin(i * 1.7 + j)
            ry = 0.65 + 0.15 * np.cos(j * 1.3)

            r2 = (dx / rx) ** 2 + (dy / ry) ** 2

            if (i + j) % 3 == 0:
                amp = -0.32
            else:
                amp = 0.30

            z += amp * np.exp(-2.2 * r2)

    z += 0.12 * np.sin(0.65 * x)
    z += 0.08 * np.cos(0.85 * y)
    z += 0.06 * np.sin(0.35 * x + 1.0 * y)

    return np.clip(z, h_min, h_max)


# =========================
# Generate heightmap
# =========================
def create_heightmap():
    nx = 450
    ny = 260

    x = np.linspace(-terrain_length / 2, terrain_length / 2, nx)
    y = np.linspace(-terrain_width / 2, terrain_width / 2, ny)

    X, Y = np.meshgrid(x, y)
    Z = np.zeros_like(X)

    for row in range(ny):
        for col in range(nx):
            Z[row, col] = terrain_height(X[row, col], Y[row, col])

    Z_img = (Z - h_min) / (h_max - h_min)
    Z_img = np.clip(Z_img, 0.0, 1.0)

    plt.imsave(
        heightmap_file,
        Z_img,
        cmap="gray",
        vmin=0.0,
        vmax=1.0
    )


# =========================
# Quaternion to pitch/roll
# =========================
def quat_component(q, name):
    value = getattr(q, name)

    if callable(value):
        return value()

    return value


def get_pitch_roll_deg(body):
    q = body.GetRot()

    w = quat_component(q, "e0")
    x = quat_component(q, "e1")
    y = quat_component(q, "e2")
    z = quat_component(q, "e3")

    roll = np.arctan2(
        2.0 * (w * x + y * z),
        1.0 - 2.0 * (x * x + y * y)
    )

    pitch_arg = 2.0 * (w * y - z * x)
    pitch_arg = np.clip(pitch_arg, -1.0, 1.0)
    pitch = np.arcsin(pitch_arg)

    return np.degrees(pitch), np.degrees(roll)


def get_tracking_body(rover):
    if hasattr(rover, "GetChassis"):
        chassis = rover.GetChassis()

        if hasattr(chassis, "GetBody"):
            return chassis.GetBody()

        if hasattr(chassis, "GetPos"):
            return chassis

    if hasattr(rover, "GetChassisBody"):
        return rover.GetChassisBody()

    raise RuntimeError(
        "Cannot access Curiosity chassis body. "
        "Run: python -c \"import pychrono.robot as robot; "
        "print([x for x in dir(robot.Curiosity) if 'Chassis' in x or 'Body' in x])\""
    )


# =========================
# Create heightmap
# =========================
create_heightmap()


# =========================
# System
# =========================
system = chrono.ChSystemNSC()
system.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)
system.SetGravitationalAcceleration(chrono.ChVector3d(0, 0, -3.71))

chrono.ChCollisionModel.SetDefaultSuggestedEnvelope(0.0025)
chrono.ChCollisionModel.SetDefaultSuggestedMargin(0.0025)


# =========================
# SCM Terrain
# =========================
terrain = veh.SCMTerrain(system)

terrain.SetSoilParameters(
    1.4e6,
    0.0,
    1.1,
    0.0,
    32.0,
    0.015,
    3.0e7,
    2.5e4
)

terrain.EnableBulldozing(True)

terrain.SetBulldozingParameters(
    55.0,
    1.0,
    3,
    10
)

terrain.Initialize(
    heightmap_file,
    terrain_length,
    terrain_width,
    h_min,
    h_max,
    terrain_delta
)

terrain.SetPlotType(
    veh.SCMTerrain.PLOT_SINKAGE,
    0.0,
    0.45
)


# =========================
# Curiosity Rover
# =========================
driver = robot.CuriositySpeedDriver(
    0.4,
    1.2
)

rover = robot.Curiosity(system)
rover.SetDriver(driver)

start_x = -12.0
start_y = 0.0
start_z = terrain_height(start_x, start_y) + 0.05

rover.Initialize(
    chrono.ChFramed(
        chrono.ChVector3d(
            start_x,
            start_y,
            start_z
        ),
        chrono.ChQuaterniond(1, 0, 0, 0)
    )
)

tracking_body = get_tracking_body(rover)


# =========================
# Visualization
# =========================
vis = chronoirr.ChVisualSystemIrrlicht()
vis.AttachSystem(system)

vis.SetCameraVertical(chrono.CameraVerticalDir_Z)
vis.SetWindowSize(1280, 720)
vis.SetWindowTitle("Curiosity Rover - SCM Mars Terrain Data Test")

vis.Initialize()
vis.AddLogo(chrono.GetChronoDataFile("logo_chrono_alpha.png"))
vis.AddSkyBox()

vis.AddCamera(
    chrono.ChVector3d(-20, 10, 6),
    chrono.ChVector3d(start_x, 0, 0.8)
)

vis.AddTypicalLights()

vis.AddLightWithShadow(
    chrono.ChVector3d(2.0, -3.0, 8.0),
    chrono.ChVector3d(0, 0, 0),
    5,
    6,
    18,
    60,
    512
)


# =========================
# Data storage
# =========================
time_data = []
height_data = []
pitch_data = []
roll_data = []


# =========================
# Simulation loop
# =========================
time = 0.0

while vis.Run():

    time += time_step

    driver.SetSteering(0.0)

    rover.Update()

    terrain.Synchronize(time)

    pos = tracking_body.GetPos()

    pitch_deg, roll_deg = get_pitch_roll_deg(tracking_body)

    time_data.append(time)
    height_data.append(pos.z)
    pitch_data.append(pitch_deg)
    roll_data.append(roll_deg)

    # =========================
    # Follow camera
    # =========================
    camera_pos = chrono.ChVector3d(
        pos.x - 7.0,
        pos.y + 6.0,
        pos.z + 3.5
    )

    camera_target = chrono.ChVector3d(
        pos.x + 1.5,
        pos.y,
        pos.z + 0.5
    )

    if hasattr(vis, "SetCameraPosition"):
        vis.SetCameraPosition(camera_pos)

    if hasattr(vis, "SetCameraTarget"):
        vis.SetCameraTarget(camera_target)

    vis.BeginScene()
    vis.Render()
    vis.EndScene()

    terrain.Advance(time_step)
    system.DoStepDynamics(time_step)


# =========================
# Graph 1: Body height
# =========================
plt.figure()
plt.plot(time_data, height_data)
plt.xlabel("Time [s]")
plt.ylabel("Chassis Height Z [m]")
plt.title("Rover Chassis Height over SCM Terrain")
plt.grid(True)


# =========================
# Graph 2: Pitch / Roll
# =========================
plt.figure()
plt.plot(time_data, pitch_data, label="Pitch [deg]")
plt.plot(time_data, roll_data, label="Roll [deg]")
plt.xlabel("Time [s]")
plt.ylabel("Angle [deg]")
plt.title("Rover Pitch and Roll over SCM Terrain")
plt.legend()
plt.grid(True)

plt.show()