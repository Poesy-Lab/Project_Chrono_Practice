import pychrono as chrono
import pychrono.vehicle as veh
import pychrono.robot as robot
from pychrono import irrlicht as chronoirr
import numpy as np
import matplotlib.pyplot as plt
import random


# =========================
# Settings
# =========================
time_step = 1e-3

terrain_length = 42.0
terrain_width = 24.0
heightmap_file = "scm_pockmarked_mars_heightmap.png"

terrain_delta = 0.06

h_min = -0.85
h_max = 0.95

random.seed(7)
np.random.seed(7)


# =========================
# Height function
# =========================
def terrain_height(x, y):

    z = 0.0

    # 사진 같은 pockmarked terrain:
    # 촘촘한 둥근 혹 + 구덩이 혼합
    spacing_x = 1.45
    spacing_y = 1.25

    x_centers = np.arange(-14.0, 20.0, spacing_x)
    y_centers = np.arange(-9.0, 9.0, spacing_y)

    for i, cx in enumerate(x_centers):

        for j, cy in enumerate(y_centers):

            # 행마다 조금씩 offset 줘서 벌집/물결 느낌
            cx2 = cx + (0.45 if j % 2 == 0 else -0.15)
            cy2 = cy + 0.20 * np.sin(i * 0.8)

            dx = x - cx2
            dy = y - cy2

            rx = 0.65 + 0.20 * np.sin(i * 1.7 + j)
            ry = 0.55 + 0.18 * np.cos(j * 1.3)

            r2 = (dx / rx) ** 2 + (dy / ry) ** 2

            # 혹/구덩이 번갈아 배치
            if (i + j) % 3 == 0:
                amp = -0.42
            else:
                amp = 0.38

            # dome/crater profile
            z += amp * np.exp(-2.4 * r2)

    # 큰 지형 흐름 추가
    z += 0.16 * np.sin(0.75 * x)
    z += 0.10 * np.cos(0.95 * y)
    z += 0.08 * np.sin(0.35 * x + 1.1 * y)

    return np.clip(z, h_min, h_max)


# =========================
# Generate heightmap
# =========================
def create_heightmap():

    nx = 450
    ny = 260

    x = np.linspace(
        -terrain_length / 2,
        terrain_length / 2,
        nx
    )

    y = np.linspace(
        -terrain_width / 2,
        terrain_width / 2,
        ny
    )

    X, Y = np.meshgrid(x, y)

    Z = np.zeros_like(X)

    for row in range(ny):
        for col in range(nx):
            Z[row, col] = terrain_height(
                X[row, col],
                Y[row, col]
            )

    Z_img = (Z - h_min) / (h_max - h_min)
    Z_img = np.clip(Z_img, 0.0, 1.0)

    plt.imsave(
        heightmap_file,
        Z_img,
        cmap="gray",
        vmin=0.0,
        vmax=1.0
    )


create_heightmap()


# =========================
# System
# =========================
system = chrono.ChSystemNSC()

system.SetCollisionSystemType(
    chrono.ChCollisionSystem.Type_BULLET
)

system.SetGravitationalAcceleration(
    chrono.ChVector3d(0, 0, -3.71)
)

chrono.ChCollisionModel.SetDefaultSuggestedEnvelope(0.0025)
chrono.ChCollisionModel.SetDefaultSuggestedMargin(0.0025)


# =========================
# SCM Terrain
# =========================
terrain = veh.SCMTerrain(system)

terrain.SetSoilParameters(
    1.4e6,    # Bekker Kphi
    0.0,      # Bekker Kc
    1.1,      # Bekker n
    0.0,      # Mohr cohesion
    32.0,     # Mohr friction angle
    0.015,    # Janosi shear
    3.0e7,    # elastic stiffness
    2.5e4     # damping
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
    0.4,    # ramp time
    1.6     # speed command
)

rover = robot.Curiosity(system)

rover.SetDriver(driver)

# 시작 위치 지형 높이에 맞춤
start_x = -17.0
start_y = 0.0
start_z = terrain_height(start_x, start_y) + 0.35

rover.Initialize(
    chrono.ChFramed(
        chrono.ChVector3d(
            start_x,
            start_y,
            start_z
        ),
        chrono.ChQuaterniond(
            1,
            0,
            0,
            0
        )
    )
)


# =========================
# Visualization
# =========================
vis = chronoirr.ChVisualSystemIrrlicht()

vis.AttachSystem(system)

vis.SetCameraVertical(
    chrono.CameraVerticalDir_Z
)

vis.SetWindowSize(
    1280,
    720
)

vis.SetWindowTitle(
    "Curiosity Rover - Pockmarked SCM Mars Terrain"
)

vis.Initialize()

vis.AddLogo(
    chrono.GetChronoDataFile(
        "logo_chrono_alpha.png"
    )
)

vis.AddSkyBox()

vis.AddCamera(
    chrono.ChVector3d(
        -15,
        10,
        5.5
    ),
    chrono.ChVector3d(
        3,
        0,
        0.4
    )
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
# Simulation loop
# =========================
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