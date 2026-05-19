import pychrono as chrono
import pychrono.vehicle as veh


# =========================
# Simulation settings
# =========================
step_size = 5e-3
tire_step_size = 1e-3

init_loc = chrono.ChVector3d(0, 0, 1.0)

terrain_length = 600.0
terrain_width = 80.0


def create_collision_wall(system):
    wall_mat = chrono.ChContactMaterialNSC()
    wall_mat.SetFriction(0.9)
    wall_mat.SetRestitution(0.35)

    wall = chrono.ChBodyEasyBox(
        0.8,
        14.0,
        4.0,
        1000.0,
        True,
        True,
        wall_mat
    )

    wall.SetFixed(True)
    wall.SetPos(chrono.ChVector3d(70.0, 0.0, 2.0))

    system.Add(wall)
    return wall


def get_auto_inputs(time):
    inputs = veh.DriverInputs()

    if time < 10.0:
        inputs.m_throttle = 1.0
        inputs.m_braking = 0.0
        inputs.m_steering = 0.0
    else:
        inputs.m_throttle = 0.0
        inputs.m_braking = 0.0
        inputs.m_steering = 0.0

    return inputs


def main():

    # -------------------------
    # Create HMMWV
    # -------------------------
    rover = veh.HMMWV_Reduced()

    rover.SetContactMethod(chrono.ChContactMethod_NSC)

    try:
        rover.SetChassisCollisionType(veh.CollisionType_MESH)
        print("Chassis collision type: MESH")
    except Exception:
        rover.SetChassisCollisionType(veh.CollisionType_PRIMITIVES)
        print("Chassis collision type: PRIMITIVES fallback")

    rover.SetChassisFixed(False)

    rover.SetInitPosition(
        chrono.ChCoordsysd(
            init_loc,
            chrono.QUNIT
        )
    )

    rover.SetEngineType(veh.EngineModelType_SIMPLE)
    rover.SetTransmissionType(
        veh.TransmissionModelType_AUTOMATIC_SIMPLE_MAP
    )
    rover.SetDriveType(veh.DrivelineTypeWV_AWD)
    rover.SetTireType(veh.TireModelType_TMEASY)
    rover.SetTireStepSize(tire_step_size)

    rover.Initialize()

    chassis_body = rover.GetVehicle().GetChassis().GetBody()

    print("===== HMMWV default physical properties =====")
    print(f"Chassis mass: {chassis_body.GetMass():.2f} kg")
    print("Using built-in HMMWV mass/inertia for stability")
    print("============================================")

    # -------------------------
    # Visualization type
    # -------------------------
    rover.SetChassisVisualizationType(chrono.VisualizationType_MESH)
    rover.SetSuspensionVisualizationType(chrono.VisualizationType_PRIMITIVES)
    rover.SetSteeringVisualizationType(chrono.VisualizationType_PRIMITIVES)
    rover.SetWheelVisualizationType(chrono.VisualizationType_MESH)
    rover.SetTireVisualizationType(chrono.VisualizationType_MESH)

    # -------------------------
    # Terrain
    # -------------------------
    terrain = veh.RigidTerrain(rover.GetSystem())

    terrain_mat = chrono.ChContactMaterialNSC()
    terrain_mat.SetFriction(0.9)
    terrain_mat.SetRestitution(0.01)

    patch = terrain.AddPatch(
        terrain_mat,
        chrono.ChCoordsysd(
            chrono.ChVector3d(0, 0, 0),
            chrono.QUNIT
        ),
        terrain_length,
        terrain_width
    )

    patch.SetTexture(
        veh.GetVehicleDataFile("terrain/textures/tile4.jpg"),
        200,
        80
    )

    terrain.Initialize()

    # -------------------------
    # Collision wall
    # -------------------------
    create_collision_wall(rover.GetSystem())

    # -------------------------
    # Visual system
    # -------------------------
    vis = veh.ChWheeledVehicleVisualSystemIrrlicht()

    vis.SetWindowTitle(
        "Project Chrono - HMMWV Mesh Collision Test"
    )

    vis.SetWindowSize(1280, 720)

    vis.Initialize()

    vis.AddLogo(
        chrono.GetChronoDataFile("logo_chrono_alpha.png")
    )

    vis.AddSkyBox()
    vis.AddLightDirectional()

    # 중요: 이거 없으면 vis.Synchronize / vis.Advance에서 죽을 수 있음
    vis.AttachVehicle(
        rover.GetVehicle()
    )

    vis.SetCameraPosition(
        chrono.ChVector3d(20, -35, 12)
    )

    vis.SetCameraTarget(
        chrono.ChVector3d(70, 0, 1.5)
    )

    rover.GetVehicle().EnableRealtime(True)

    # -------------------------
    # Simulation loop
    # -------------------------
    while vis.Run():

        time = rover.GetSystem().GetChTime()

        vis.BeginScene()
        vis.Render()
        vis.EndScene()

        driver_inputs = get_auto_inputs(time)

        terrain.Synchronize(time)

        rover.Synchronize(
            time,
            driver_inputs,
            terrain
        )

        vis.Synchronize(
            time,
            driver_inputs
        )

        terrain.Advance(step_size)
        rover.Advance(step_size)
        vis.Advance(step_size)


if __name__ == "__main__":
    main()