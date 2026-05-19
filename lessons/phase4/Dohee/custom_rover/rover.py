import math

import pychrono as chrono

from config import (
    CSV_PATH,
    PLOT_PATH,
    WAYPOINTS,
    chassis_density,
    chassis_height,
    chassis_length,
    chassis_width,
    chassis_z,
    deck_height,
    deck_length,
    deck_width,
    deck_z_offset,
    front_x,
    ground_friction,
    ground_length,
    ground_thickness,
    ground_width,
    grouser_count,
    grouser_density,
    grouser_height,
    grouser_length,
    grouser_width,
    hub_density,
    hub_radius,
    hub_width,
    knuckle_density,
    knuckle_size,
    left_y,
    mast_density,
    mast_height,
    mast_radius,
    mast_x_offset,
    mast_z_offset,
    max_speed_rate,
    max_steer_angle,
    max_steer_rate,
    rear_x,
    restitution,
    right_y,
    rock_size,
    sensor_head_density,
    sensor_head_x,
    sensor_head_y,
    sensor_head_z,
    slope_angle,
    slope_length,
    slope_thickness,
    slope_width,
    step2_height,
    step2_length,
    step2_width,
    step_height,
    step_length,
    step_width,
    track_width,
    wheel_density,
    wheel_friction,
    wheel_radius,
    wheel_width,
    wheel_z,
    wheelbase,
    RoverState,
    DriverInputs,
)


def make_const_function(value):
    if hasattr(chrono, "ChFunctionConst"):
        return chrono.ChFunctionConst(value)
    return chrono.ChFunction_Const(value)


def q_from_axis_angle(axis, angle):
    q = chrono.ChQuaterniond()
    q.SetFromAngleAxis(angle, axis)
    return q


def make_frame(pos, rot=None):
    if rot is None:
        rot = chrono.ChQuaterniond(1, 0, 0, 0)
    return chrono.ChFramed(pos, rot)


def set_body_color(body, color):
    shape = body.GetVisualShape(0)
    if shape:
        shape.SetColor(color)


def approach(current, target, max_delta):
    if target > current:
        return min(current + max_delta, target)
    return max(current - max_delta, target)


def quat_to_yaw_deg(q):
    euler = q.GetCardanAnglesXYZ()
    return math.degrees(euler.z)


class CustomViperRover:
    def __init__(self, system, control_mode, experiment_name):
        self.system = system
        self.control_mode = control_mode
        self.experiment_name = experiment_name

        self.ground_mat = chrono.ChContactMaterialNSC()
        self.ground_mat.SetFriction(ground_friction)
        self.ground_mat.SetRestitution(restitution)

        self.wheel_mat = chrono.ChContactMaterialNSC()
        self.wheel_mat.SetFriction(wheel_friction)
        self.wheel_mat.SetRestitution(restitution)

        self.driver_inputs = DriverInputs()
        self.actual_speed = 0.0
        self.actual_steer_angle = 0.0

        self.ground = None
        self.terrain_features = []
        self.waypoint_markers = []
        self.chassis = None
        self.body_parts = []
        self.knuckles = {}
        self.wheels = {}
        self.wheel_visuals = []
        self.steer_motors = {}
        self.drive_motors = {}
        self.left_wheel_names = ("FL", "RL")
        self.right_wheel_names = ("FR", "RR")
        self.target_x = 0.0
        self.target_y = 0.0

        self._build()

    def _build(self):
        self._create_ground()
        self._create_terrain_features()
        self._create_waypoint_markers()
        self._create_chassis()
        self._create_body_style()
        self._create_front_knuckles()
        self._create_wheels()
        self._create_steering_motors()
        self._create_drive_motors()

    def _create_ground(self):
        ground = chrono.ChBodyEasyBox(
            ground_length, ground_width, ground_thickness, 1000.0, True, True, self.ground_mat
        )
        ground.SetPos(chrono.ChVector3d(0, 0, -ground_thickness))
        ground.SetFixed(True)
        ground.SetName("ground")
        try:
            ground.GetVisualShape(0).SetTexture(
                chrono.GetChronoDataFile("textures/concrete.jpg")
            )
        except Exception:
            set_body_color(ground, chrono.ChColor(0.58, 0.54, 0.48))
        self.system.Add(ground)
        self.ground = ground

    def _create_terrain_features(self):
        ground_top_z = -ground_thickness / 2.0

        slope = chrono.ChBodyEasyBox(
            slope_length, slope_width, slope_thickness, 800.0, True, True, self.ground_mat
        )
        slope.SetName("terrain_slope")
        slope.SetPos(chrono.ChVector3d(3.0, 0.0, ground_top_z + slope_thickness / 2.0))
        slope.SetRot(q_from_axis_angle(chrono.ChVector3d(0, 1, 0), -slope_angle))
        slope.SetFixed(True)
        set_body_color(slope, chrono.ChColor(0.52, 0.46, 0.36))
        self.system.Add(slope)
        self.terrain_features.append(slope)

        step = chrono.ChBodyEasyBox(
            step_length, step_width, step_height, 900.0, True, True, self.ground_mat
        )
        step.SetName("terrain_step")
        step.SetPos(chrono.ChVector3d(0.9, 0.0, ground_top_z + step_height / 2.0))
        step.SetFixed(True)
        set_body_color(step, chrono.ChColor(0.62, 0.54, 0.42))
        self.system.Add(step)
        self.terrain_features.append(step)

        step2 = chrono.ChBodyEasyBox(
            step2_length, step2_width, step2_height, 900.0, True, True, self.ground_mat
        )
        step2.SetName("terrain_step_2")
        step2.SetPos(chrono.ChVector3d(6.9, 0.1, ground_top_z + step2_height / 2.0))
        step2.SetFixed(True)
        set_body_color(step2, chrono.ChColor(0.66, 0.58, 0.46))
        self.system.Add(step2)
        self.terrain_features.append(step2)

        rock_positions = [
            chrono.ChVector3d(-1.4, 0.55, ground_top_z + rock_size / 2.0),
            chrono.ChVector3d(-0.8, -0.50, ground_top_z + rock_size / 2.0),
            chrono.ChVector3d(1.8, 0.65, ground_top_z + rock_size / 2.0),
            chrono.ChVector3d(5.4, -0.35, ground_top_z + rock_size / 2.0),
            chrono.ChVector3d(7.8, 0.55, ground_top_z + rock_size / 2.0),
            chrono.ChVector3d(9.1, -0.15, ground_top_z + rock_size / 2.0),
        ]
        for i, pos in enumerate(rock_positions):
            rock = chrono.ChBodyEasyBox(
                rock_size,
                rock_size * (0.8 + 0.2 * (i % 2)),
                rock_size * (0.9 + 0.15 * i),
                950.0,
                True,
                True,
                self.ground_mat,
            )
            rock.SetName(f"terrain_rock_{i}")
            rock.SetPos(pos)
            rock.SetRot(q_from_axis_angle(chrono.ChVector3d(0, 0, 1), 0.2 * (i + 1)))
            rock.SetFixed(True)
            set_body_color(rock, chrono.ChColor(0.40, 0.36, 0.33))
            self.system.Add(rock)
            self.terrain_features.append(rock)

    def _create_waypoint_markers(self):
        ground_top_z = -ground_thickness / 2.0
        for i, (x, y) in enumerate(WAYPOINTS):
            marker = chrono.ChBodyEasyCylinder(
                chrono.ChAxis_Z, 0.05, 0.16, 20.0, True, False, self.ground_mat
            )
            marker.SetName(f"waypoint_{i}")
            marker.SetPos(chrono.ChVector3d(x, y, ground_top_z + 0.08))
            marker.SetFixed(True)
            marker.EnableCollision(False)
            if i == 0:
                set_body_color(marker, chrono.ChColor(0.20, 0.80, 0.25))
            elif i == len(WAYPOINTS) - 1:
                set_body_color(marker, chrono.ChColor(0.90, 0.25, 0.20))
            else:
                set_body_color(marker, chrono.ChColor(0.95, 0.82, 0.18))
            self.system.Add(marker)
            self.waypoint_markers.append(marker)

    def _create_chassis(self):
        chassis = chrono.ChBodyEasyBox(
            chassis_length,
            chassis_width,
            chassis_height,
            chassis_density,
            True,
            True,
            self.wheel_mat,
        )
        chassis.SetPos(chrono.ChVector3d(0, 0, chassis_z))
        chassis.SetName("chassis")
        set_body_color(chassis, chrono.ChColor(0.12, 0.38, 0.82))
        self.system.Add(chassis)
        self.chassis = chassis

    def _create_body_style(self):
        deck = chrono.ChBodyEasyBox(
            deck_length,
            deck_width,
            deck_height,
            chassis_density * 0.4,
            True,
            False,
            self.wheel_mat,
        )
        deck.SetName("science_deck")
        deck.SetPos(chrono.ChVector3d(0, 0, chassis_z + deck_z_offset))
        deck.EnableCollision(False)
        set_body_color(deck, chrono.ChColor(0.80, 0.78, 0.70))
        self.system.Add(deck)
        self.body_parts.append(deck)
        self._fix_to_chassis(deck)

        mast = chrono.ChBodyEasyCylinder(
            chrono.ChAxis_Z, mast_radius, mast_height, mast_density, True, False, self.wheel_mat
        )
        mast.SetName("sensor_mast")
        mast.SetPos(chrono.ChVector3d(mast_x_offset, 0, chassis_z + mast_z_offset))
        mast.EnableCollision(False)
        set_body_color(mast, chrono.ChColor(0.70, 0.73, 0.76))
        self.system.Add(mast)
        self.body_parts.append(mast)
        self._fix_to_chassis(mast)

        head = chrono.ChBodyEasyBox(
            sensor_head_x,
            sensor_head_y,
            sensor_head_z,
            sensor_head_density,
            True,
            False,
            self.wheel_mat,
        )
        head.SetName("sensor_head")
        head.SetPos(
            chrono.ChVector3d(mast_x_offset + 0.05, 0, chassis_z + mast_z_offset + 0.18)
        )
        head.EnableCollision(False)
        set_body_color(head, chrono.ChColor(0.92, 0.66, 0.16))
        self.system.Add(head)
        self.body_parts.append(head)
        self._fix_to_chassis(head)

    def _fix_to_chassis(self, body):
        joint = chrono.ChLinkMateFix()
        joint.Initialize(body, self.chassis, make_frame(body.GetPos()))
        self.system.Add(joint)

    def _create_front_knuckles(self):
        self.knuckles["FL"] = self._create_knuckle("knuckle_FL", front_x, left_y, wheel_z)
        self.knuckles["FR"] = self._create_knuckle("knuckle_FR", front_x, right_y, wheel_z)

    def _create_knuckle(self, name, x, y, z):
        body = chrono.ChBodyEasyBox(
            knuckle_size, knuckle_size, knuckle_size, knuckle_density, True, False, self.wheel_mat
        )
        body.SetPos(chrono.ChVector3d(x, y, z))
        body.SetName(name)
        body.EnableCollision(False)
        set_body_color(body, chrono.ChColor(0.92, 0.38, 0.12))
        self.system.Add(body)
        return body

    def _create_wheels(self):
        self.wheels["FL"] = self._create_wheel("wheel_FL", front_x, left_y, wheel_z)
        self.wheels["FR"] = self._create_wheel("wheel_FR", front_x, right_y, wheel_z)
        self.wheels["RL"] = self._create_wheel("wheel_RL", rear_x, left_y, wheel_z)
        self.wheels["RR"] = self._create_wheel("wheel_RR", rear_x, right_y, wheel_z)

    def _create_wheel(self, name, x, y, z):
        wheel = chrono.ChBodyEasyCylinder(
            chrono.ChAxis_Y, wheel_radius, wheel_width, wheel_density, True, True, self.wheel_mat
        )
        wheel.SetPos(chrono.ChVector3d(x, y, z))
        wheel.SetName(name)
        set_body_color(wheel, chrono.ChColor(0.10, 0.10, 0.10))
        self.system.Add(wheel)
        self._add_wheel_visuals(wheel, name)
        return wheel

    def _add_wheel_visuals(self, wheel, name):
        hub = chrono.ChBodyEasyCylinder(
            chrono.ChAxis_Y, hub_radius, hub_width, hub_density, True, False, self.wheel_mat
        )
        hub.SetName(f"{name}_hub")
        hub.SetPos(wheel.GetPos())
        hub.EnableCollision(False)
        set_body_color(hub, chrono.ChColor(0.78, 0.78, 0.80))
        self.system.Add(hub)
        self.wheel_visuals.append(hub)
        self._fix_to_body(hub, wheel)

        for i in range(grouser_count):
            angle = 2.0 * math.pi * i / grouser_count
            px = wheel.GetPos().x + (wheel_radius - 0.01) * math.cos(angle)
            pz = wheel.GetPos().z + (wheel_radius - 0.01) * math.sin(angle)

            grouser = chrono.ChBodyEasyBox(
                grouser_length,
                grouser_width,
                grouser_height,
                grouser_density,
                True,
                False,
                self.wheel_mat,
            )
            grouser.SetName(f"{name}_grouser_{i}")
            grouser.SetPos(chrono.ChVector3d(px, wheel.GetPos().y, pz))
            grouser.EnableCollision(False)
            grouser.SetRot(q_from_axis_angle(chrono.ChVector3d(0, 1, 0), -angle))
            set_body_color(grouser, chrono.ChColor(0.55, 0.57, 0.60))
            self.system.Add(grouser)
            self.wheel_visuals.append(grouser)
            self._fix_to_body(grouser, wheel)

    def _fix_to_body(self, body, parent):
        joint = chrono.ChLinkMateFix()
        joint.Initialize(body, parent, make_frame(body.GetPos()))
        self.system.Add(joint)

    def _create_steering_motors(self):
        self.steer_motors["FL"] = self._create_steering_motor(
            "steer_FL", self.knuckles["FL"], self.chassis, front_x, left_y, wheel_z
        )
        self.steer_motors["FR"] = self._create_steering_motor(
            "steer_FR", self.knuckles["FR"], self.chassis, front_x, right_y, wheel_z
        )

    def _create_steering_motor(self, name, child, parent, x, y, z):
        motor = chrono.ChLinkMotorRotationAngle()
        motor.SetName(name)
        motor.Initialize(child, parent, make_frame(chrono.ChVector3d(x, y, z)))
        motor.SetAngleFunction(make_const_function(0.0))
        self.system.Add(motor)
        return motor

    def _create_drive_motors(self):
        self.drive_motors["FL"] = self._create_drive_motor(
            "motor_FL", self.wheels["FL"], self.knuckles["FL"], front_x, left_y, wheel_z
        )
        self.drive_motors["FR"] = self._create_drive_motor(
            "motor_FR", self.wheels["FR"], self.knuckles["FR"], front_x, right_y, wheel_z
        )
        self.drive_motors["RL"] = self._create_drive_motor(
            "motor_RL", self.wheels["RL"], self.chassis, rear_x, left_y, wheel_z
        )
        self.drive_motors["RR"] = self._create_drive_motor(
            "motor_RR", self.wheels["RR"], self.chassis, rear_x, right_y, wheel_z
        )

    def _create_drive_motor(self, name, child, parent, x, y, z):
        motor = chrono.ChLinkMotorRotationSpeed()
        motor.SetName(name)
        rot = q_from_axis_angle(chrono.ChVector3d(1, 0, 0), -math.pi / 2.0)
        motor.Initialize(child, parent, make_frame(chrono.ChVector3d(x, y, z), rot))
        motor.SetSpeedFunction(make_const_function(0.0))
        self.system.Add(motor)
        return motor

    def synchronize(self, driver_inputs, dt):
        self.driver_inputs = driver_inputs
        target_speed = driver_inputs.speed_cmd
        target_steer = driver_inputs.steering_cmd * max_steer_angle

        self.actual_speed = approach(self.actual_speed, target_speed, max_speed_rate * dt)
        self.actual_steer_angle = approach(
            self.actual_steer_angle, target_steer, max_steer_rate * dt
        )

        steer_left, steer_right = self._compute_steering_angles(self.actual_steer_angle)
        left_omega, right_omega = self._compute_side_omegas(
            self.actual_speed / wheel_radius,
            driver_inputs.steering_cmd,
            driver_inputs.turn_mode,
        )

        self.steer_motors["FL"].SetAngleFunction(make_const_function(steer_left))
        self.steer_motors["FR"].SetAngleFunction(make_const_function(steer_right))

        for name in self.left_wheel_names:
            self.drive_motors[name].SetSpeedFunction(make_const_function(left_omega))
        for name in self.right_wheel_names:
            self.drive_motors[name].SetSpeedFunction(make_const_function(right_omega))

    def _compute_steering_angles(self, center_angle):
        if abs(center_angle) < 1e-6:
            return 0.0, 0.0

        turn_sign = 1.0 if center_angle > 0 else -1.0
        base = abs(center_angle)
        radius = wheelbase / math.tan(base)
        inner = math.atan(wheelbase / max(1e-6, radius - track_width / 2.0))
        outer = math.atan(wheelbase / max(1e-6, radius + track_width / 2.0))

        if turn_sign > 0:
            return inner, outer
        return -outer, -inner

    def _compute_side_omegas(self, base_omega, steering_cmd, turn_mode):
        normal_delta = 0.18 * steering_cmd * abs(base_omega)
        pivot_delta = 0.95 * steering_cmd * max(abs(base_omega), 0.6)
        delta = (1.0 - turn_mode) * normal_delta + turn_mode * pivot_delta
        return base_omega - delta, base_omega + delta

    def get_yaw_rad(self):
        return self.chassis.GetRot().GetCardanAnglesXYZ().z

    def get_state(self, time):
        pos = self.chassis.GetPos()
        yaw_deg = quat_to_yaw_deg(self.chassis.GetRot())
        steer_left, steer_right = self._compute_steering_angles(self.actual_steer_angle)
        return RoverState(
            time=time,
            x=pos.x,
            y=pos.y,
            z=pos.z,
            yaw_deg=yaw_deg,
            target_x=self.target_x,
            target_y=self.target_y,
            speed_cmd=self.driver_inputs.speed_cmd,
            steering_cmd=self.driver_inputs.steering_cmd,
            turn_mode=self.driver_inputs.turn_mode,
            wheel_omega=self.actual_speed / wheel_radius,
            steer_left_deg=math.degrees(steer_left),
            steer_right_deg=math.degrees(steer_right),
        )

    def print_design_summary(self):
        print("[Design] Custom Viper-style rover")
        print("  terrain  : textured ground + slope + step + rock blocks")
        print("  chassis  : blue main body")
        print("  deck     : sand-colored science deck")
        print("  mast     : silver sensor mast")
        print("  head     : amber sensor head")
        print("  upright  : orange front steering knuckles")
        print("  wheels   : 4 dark gray wheels with hubs and grousers")
        print("  steering : left/right front Ackermann-style steering")
        print("  drive    : left/right split wheel speed control")
        print("")
        print("[Experiment]")
        print(f"  control  : {self.control_mode}")
        print(f"  profile  : {self.experiment_name}")
        if self.control_mode == 'waypoints':
            print(f"  waypoints: {len(WAYPOINTS)} targets")
        print(f"  log file : {CSV_PATH}")
        print(f"  plot file: {PLOT_PATH}")
