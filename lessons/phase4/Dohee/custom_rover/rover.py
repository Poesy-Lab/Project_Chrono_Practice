import math

import pychrono as chrono

# config.py에 정의된 시뮬레이션/로버 설계 파라미터를 불러온다.
# 이 파일에서는 로버 구조를 실제로 생성하고, config.py는 수치 설정을 담당한다.
from config import (
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
    SIM_CONFIG,
)


# =============================================================================
# 1. Utility functions
# =============================================================================

def make_const_function(value):
    """
    Chrono motor 입력에 사용할 상수 함수 생성.

    Chrono 버전에 따라 함수 이름이 다를 수 있어서,
    ChFunctionConst가 있으면 그것을 사용하고,
    없으면 구버전 이름인 ChFunction_Const를 사용한다.
    """
    if hasattr(chrono, "ChFunctionConst"):
        return chrono.ChFunctionConst(value)
    return chrono.ChFunction_Const(value)


def q_from_axis_angle(axis, angle):
    """
    axis-angle 표현으로부터 quaternion을 생성한다.

    Parameters
    ----------
    axis : chrono.ChVector3d
        회전축
    angle : float
        회전각 [rad]

    Returns
    -------
    chrono.ChQuaterniond
        Chrono에서 사용하는 quaternion 회전 표현
    """
    q = chrono.ChQuaterniond()
    q.SetFromAngleAxis(angle, axis)
    return q


def make_frame(pos, rot=None):
    """
    Chrono joint/motor 초기화에 사용할 frame을 생성한다.

    Parameters
    ----------
    pos : chrono.ChVector3d
        frame의 위치
    rot : chrono.ChQuaterniond, optional
        frame의 회전. 지정하지 않으면 단위 quaternion을 사용한다.

    Returns
    -------
    chrono.ChFramed
        Chrono link 초기화용 frame
    """
    if rot is None:
        rot = chrono.ChQuaterniond(1, 0, 0, 0)
    return chrono.ChFramed(pos, rot)


def set_body_color(body, color):
    """
    body의 첫 번째 visual shape 색상을 설정한다.

    주의:
    - body에 visual shape가 없는 경우 shape가 None일 수 있다.
    - 현재 코드는 대부분 ChBodyEasyBox/Cylinder로 생성되므로 visual shape가 존재한다.
    """
    shape = body.GetVisualShape(0)
    if shape:
        shape.SetColor(color)


def approach(current, target, max_delta):
    """
    current 값을 target 방향으로 max_delta만큼 서서히 이동시킨다.

    이 함수는 속도 명령과 조향각 명령이 순간적으로 바뀌지 않도록 제한하는 데 사용된다.
    실제 로버의 actuator가 무한히 빠르게 반응하지 않는 효과를 단순하게 모사한다.
    """
    if target > current:
        return min(current + max_delta, target)
    return max(current - max_delta, target)


def quat_to_yaw_deg(q):
    """
    quaternion에서 yaw angle을 추출하고 degree 단위로 변환한다.

    이 코드의 좌표계는 Z-up이므로 yaw는 수평면에서의 방향각이다.
    """
    euler = q.GetCardanAnglesXYZ()
    return math.degrees(euler.z)


def quat_to_rpy_deg(q):
    euler = q.GetCardanAnglesXYZ()
    return math.degrees(euler.x), math.degrees(euler.y), math.degrees(euler.z)


# =============================================================================
# 2. Custom rover model
# =============================================================================

class CustomViperRover:
    """
    Custom Viper-style rover 모델을 생성하고 제어 입력을 적용하는 클래스.

    이 클래스의 주요 역할:
    1. 지형 생성
    2. 로버 차체 생성
    3. 앞바퀴 조향 knuckle 생성
    4. 네 개의 바퀴 생성
    5. 조향 모터 생성
    6. 구동 모터 생성
    7. driver input을 실제 motor 명령으로 변환
    8. 로버 상태를 logging용 RoverState로 반환

    구조:
        front wheels:
            chassis -> steering motor -> knuckle -> drive motor -> wheel

        rear wheels:
            chassis -> drive motor -> wheel
    """

    def __init__(self, system, control_mode, experiment_name, terrain_mode=None):
        """
        로버 객체 초기화.

        Parameters
        ----------
        system : chrono.ChSystemNSC
            로버와 지형이 추가될 Chrono 물리 시스템
        control_mode : str
            현재 제어 방식 이름. 출력 요약용으로 사용된다.
        experiment_name : str
            현재 실험 이름. 출력 요약용으로 사용된다.
        """
        self.system = system
        self.control_mode = control_mode
        self.experiment_name = experiment_name
        self.terrain_mode = SIM_CONFIG.terrain_mode if terrain_mode is None else terrain_mode

        # 지형 접촉 재질 생성
        # NSC contact system에서 사용할 마찰계수와 반발계수를 설정한다.
        self.ground_mat = chrono.ChContactMaterialNSC()
        self.ground_mat.SetFriction(ground_friction)
        self.ground_mat.SetRestitution(restitution)

        # 바퀴 및 로버 부품 접촉 재질 생성
        self.wheel_mat = chrono.ChContactMaterialNSC()
        self.wheel_mat.SetFriction(wheel_friction)
        self.wheel_mat.SetRestitution(restitution)

        # 현재 입력과 실제 적용 상태
        # driver input은 목표값이고, actual_*은 변화율 제한을 거쳐 실제 적용되는 값이다.
        self.driver_inputs = DriverInputs()
        self.actual_speed = 0.0
        self.actual_steer_angle = 0.0

        # 생성된 Chrono body/link들을 저장하는 변수들
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

        # 좌우 바퀴 이름 묶음
        # 좌우 바퀴 속도 차이를 줄 때 사용한다.
        self.left_wheel_names = ("FL", "RL")
        self.right_wheel_names = ("FR", "RR")

        # waypoint 추종 시 현재 목표점을 logging하기 위한 변수
        self.target_x = 0.0
        self.target_y = 0.0

        # 실제 로버와 지형 생성
        self._build()

    def _build(self):
        """
        로버와 환경을 순서대로 생성한다.

        생성 순서가 중요하다.
        예를 들어, body style 부품은 chassis에 고정되어야 하므로 chassis 생성 이후에 만들어야 한다.
        앞바퀴 drive motor는 knuckle에 연결되므로 knuckle 생성 이후에 만들어야 한다.
        """
        self._create_ground()
        if self.terrain_mode == "obstacles":
            self._create_terrain_features()
        if self.control_mode in {"waypoints", "rl"}:
            self._create_waypoint_markers()
        self._create_chassis()
        self._create_body_style()
        self._create_front_knuckles()
        self._create_wheels()
        self._create_steering_motors()
        self._create_drive_motors()

    # =========================================================================
    # 3. Terrain generation
    # =========================================================================

    def _create_ground(self):
        """
        기본 평지 지형을 생성한다.

        ground는 큰 box body로 생성하고 fixed body로 설정한다.
        즉, 물리 시뮬레이션 중 움직이지 않는 고정 지면이다.
        """
        ground = chrono.ChBodyEasyBox(
            ground_length,
            ground_width,
            ground_thickness,
            1000.0,
            True,   # visualization enabled
            True,   # collision enabled
            self.ground_mat,
        )

        # 현재 설정에서는 지면 중심이 z = -ground_thickness에 놓인다.
        # ground_thickness = 1.0이면 지면 윗면은 z = -0.5가 된다.
        # 지면 윗면을 z=0으로 맞추려면 -ground_thickness / 2.0을 사용하는 것이 더 직관적이다.
        ground.SetPos(chrono.ChVector3d(0, 0, -ground_thickness))

        ground.SetFixed(True)
        ground.SetName("ground")

        # Chrono 기본 concrete texture를 적용한다.
        # texture 파일을 찾지 못하는 환경에서는 색상으로 대체한다.
        try:
            ground.GetVisualShape(0).SetTexture(
                chrono.GetChronoDataFile("textures/concrete.jpg")
            )
        except Exception:
            set_body_color(ground, chrono.ChColor(0.58, 0.54, 0.48))

        self.system.Add(ground)
        self.ground = ground

    def _create_terrain_features(self):
        """
        경사로, 턱, 돌 장애물 등 간단한 지형 요소를 생성한다.

        목적:
        - 평지 주행뿐 아니라 장애물 통과 가능성 확인
        - 로버 바퀴/차체 설계가 지형 변화에 어떻게 반응하는지 관찰
        """
        # 현재 ground 생성 방식 기준으로 지면 윗면 높이를 계산한다.
        ground_top_z = -ground_thickness / 2.0

        # ---------------------------------------------------------------------
        # Slope
        # ---------------------------------------------------------------------
        slope = chrono.ChBodyEasyBox(
            slope_length,
            slope_width,
            slope_thickness,
            800.0,
            True,
            True,
            self.ground_mat,
        )
        slope.SetName("terrain_slope")

        # slope 중심 위치 설정
        slope.SetPos(chrono.ChVector3d(3.0, 0.0, ground_top_z + slope_thickness / 2.0))

        # Y축 기준으로 회전시켜 X-Z 평면상 경사로를 만든다.
        slope.SetRot(q_from_axis_angle(chrono.ChVector3d(0, 1, 0), -slope_angle))

        slope.SetFixed(True)
        set_body_color(slope, chrono.ChColor(0.52, 0.46, 0.36))
        self.system.Add(slope)
        self.terrain_features.append(slope)

        # ---------------------------------------------------------------------
        # First step obstacle
        # ---------------------------------------------------------------------
        step = chrono.ChBodyEasyBox(
            step_length,
            step_width,
            step_height,
            900.0,
            True,
            True,
            self.ground_mat,
        )
        step.SetName("terrain_step")
        step.SetPos(chrono.ChVector3d(0.9, 0.0, ground_top_z + step_height / 2.0))
        step.SetFixed(True)
        set_body_color(step, chrono.ChColor(0.62, 0.54, 0.42))
        self.system.Add(step)
        self.terrain_features.append(step)

        # ---------------------------------------------------------------------
        # Second step obstacle
        # ---------------------------------------------------------------------
        step2 = chrono.ChBodyEasyBox(
            step2_length,
            step2_width,
            step2_height,
            900.0,
            True,
            True,
            self.ground_mat,
        )
        step2.SetName("terrain_step_2")
        step2.SetPos(chrono.ChVector3d(6.9, 0.1, ground_top_z + step2_height / 2.0))
        step2.SetFixed(True)
        set_body_color(step2, chrono.ChColor(0.66, 0.58, 0.46))
        self.system.Add(step2)
        self.terrain_features.append(step2)

        # ---------------------------------------------------------------------
        # Rock obstacles
        # ---------------------------------------------------------------------
        # 작은 box들을 돌 장애물처럼 배치한다.
        # 현재는 고정 장애물이며 실제 암석 mesh가 아니라 단순화된 box geometry다.
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

            # 각 rock에 약간씩 다른 yaw 회전을 주어 배치가 덜 인위적으로 보이게 한다.
            rock.SetRot(q_from_axis_angle(chrono.ChVector3d(0, 0, 1), 0.2 * (i + 1)))

            rock.SetFixed(True)
            set_body_color(rock, chrono.ChColor(0.40, 0.36, 0.33))
            self.system.Add(rock)
            self.terrain_features.append(rock)

    def _create_waypoint_markers(self):
        """
        waypoint 위치를 시각적으로 표시하는 marker를 생성한다.

        marker는 주행에 영향을 주면 안 되므로 collision을 비활성화한다.
        """
        ground_top_z = -ground_thickness / 2.0

        for i, (x, y) in enumerate(WAYPOINTS):
            marker = chrono.ChBodyEasyCylinder(
                chrono.ChAxis_Z,
                0.05,
                0.16,
                20.0,
                True,
                False,
                self.ground_mat,
            )
            marker.SetName(f"waypoint_{i}")
            marker.SetPos(chrono.ChVector3d(x, y, ground_top_z + 0.08))
            marker.SetFixed(True)
            marker.EnableCollision(False)

            # 시작점, 중간점, 목표점을 색상으로 구분한다.
            if i == 0:
                set_body_color(marker, chrono.ChColor(0.20, 0.80, 0.25))
            elif i == len(WAYPOINTS) - 1:
                set_body_color(marker, chrono.ChColor(0.90, 0.25, 0.20))
            else:
                set_body_color(marker, chrono.ChColor(0.95, 0.82, 0.18))

            self.system.Add(marker)
            self.waypoint_markers.append(marker)

    # =========================================================================
    # 4. Rover body generation
    # =========================================================================

    def _create_chassis(self):
        """
        로버의 메인 차체를 생성한다.

        이 body가 로버의 기준 body 역할을 한다.
        센서 mast, deck 등 부가 시각 요소는 이 chassis에 고정된다.
        """
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
        """
        로버 외형을 구성하는 부가 body들을 생성한다.

        science deck, sensor mast, sensor head는 로버 외형을 위한 부품이다.
        collision을 끄고 chassis에 fixed joint로 연결한다.
        """
        # ---------------------------------------------------------------------
        # Science deck
        # ---------------------------------------------------------------------
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

        # ---------------------------------------------------------------------
        # Sensor mast
        # ---------------------------------------------------------------------
        mast = chrono.ChBodyEasyCylinder(
            chrono.ChAxis_Z,
            mast_radius,
            mast_height,
            mast_density,
            True,
            False,
            self.wheel_mat,
        )
        mast.SetName("sensor_mast")
        mast.SetPos(chrono.ChVector3d(mast_x_offset, 0, chassis_z + mast_z_offset))
        mast.EnableCollision(False)
        set_body_color(mast, chrono.ChColor(0.70, 0.73, 0.76))
        self.system.Add(mast)
        self.body_parts.append(mast)
        self._fix_to_chassis(mast)

        # ---------------------------------------------------------------------
        # Sensor head
        # ---------------------------------------------------------------------
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
        """
        주어진 body를 chassis에 완전히 고정한다.

        ChLinkMateFix는 두 body 사이의 상대 운동을 모두 구속한다.
        즉, body는 chassis와 하나의 강체처럼 움직인다.
        """
        joint = chrono.ChLinkMateFix()
        joint.Initialize(body, self.chassis, make_frame(body.GetPos()))
        self.system.Add(joint)

    # =========================================================================
    # 5. Knuckle and wheel generation
    # =========================================================================

    def _create_front_knuckles(self):
        """
        앞바퀴 조향용 knuckle body를 생성한다.

        FL, FR knuckle은 chassis와 steering motor로 연결되고,
        앞바퀴는 각각의 knuckle에 drive motor로 연결된다.
        """
        self.knuckles["FL"] = self._create_knuckle("knuckle_FL", front_x, left_y, wheel_z)
        self.knuckles["FR"] = self._create_knuckle("knuckle_FR", front_x, right_y, wheel_z)

    def _create_knuckle(self, name, x, y, z):
        """
        개별 steering knuckle body를 생성한다.

        knuckle 자체는 작은 box이며, steering axis를 가진 중간 body 역할을 한다.
        """
        body = chrono.ChBodyEasyBox(
            knuckle_size,
            knuckle_size,
            knuckle_size,
            knuckle_density,
            True,
            False,
            self.wheel_mat,
        )
        body.SetPos(chrono.ChVector3d(x, y, z))
        body.SetName(name)

        # knuckle은 실제 접촉 부품이 아니라 조향 연결용 body이므로 collision을 끈다.
        body.EnableCollision(False)

        set_body_color(body, chrono.ChColor(0.92, 0.38, 0.12))
        self.system.Add(body)
        return body

    def _create_wheels(self):
        """
        네 개의 바퀴를 생성한다.

        FL, FR은 앞바퀴이며 knuckle에 연결된다.
        RL, RR은 뒷바퀴이며 chassis에 직접 연결된다.
        """
        self.wheels["FL"] = self._create_wheel("wheel_FL", front_x, left_y, wheel_z)
        self.wheels["FR"] = self._create_wheel("wheel_FR", front_x, right_y, wheel_z)
        self.wheels["RL"] = self._create_wheel("wheel_RL", rear_x, left_y, wheel_z)
        self.wheels["RR"] = self._create_wheel("wheel_RR", rear_x, right_y, wheel_z)

    def _create_wheel(self, name, x, y, z):
        """
        원통형 바퀴 body를 생성한다.

        좌표계:
            +X forward
            +Y left
            +Z up

        바퀴 회전축은 좌우 방향인 Y축이므로 ChAxis_Y를 사용한다.
        """
        wheel = chrono.ChBodyEasyCylinder(
            chrono.ChAxis_Y,
            wheel_radius,
            wheel_width,
            wheel_density,
            True,
            True,
            self.wheel_mat,
        )
        wheel.SetPos(chrono.ChVector3d(x, y, z))
        wheel.SetName(name)
        set_body_color(wheel, chrono.ChColor(0.10, 0.10, 0.10))
        self.system.Add(wheel)

        # 허브와 grouser 같은 시각 요소를 바퀴에 부착한다.
        self._add_wheel_visuals(wheel, name)

        return wheel

    def _add_wheel_visuals(self, wheel, name):
        """
        바퀴에 hub와 grouser를 추가한다.

        주의:
        - hub와 grouser는 collision이 꺼져 있다.
        - 실제 지면 접촉은 원통형 wheel body가 담당한다.
        """
        # ---------------------------------------------------------------------
        # Wheel hub
        # ---------------------------------------------------------------------
        hub = chrono.ChBodyEasyCylinder(
            chrono.ChAxis_Y,
            hub_radius,
            hub_width,
            hub_density,
            True,
            False,
            self.wheel_mat,
        )
        hub.SetName(f"{name}_hub")
        hub.SetPos(wheel.GetPos())
        hub.EnableCollision(False)
        set_body_color(hub, chrono.ChColor(0.78, 0.78, 0.80))
        self.system.Add(hub)
        self.wheel_visuals.append(hub)

        # hub가 wheel과 함께 움직이도록 fixed joint로 연결한다.
        self._fix_to_body(hub, wheel)

        # ---------------------------------------------------------------------
        # Wheel grousers
        # ---------------------------------------------------------------------
        for i in range(grouser_count):
            # 바퀴 둘레를 grouser_count 개수만큼 등분한다.
            angle = 2.0 * math.pi * i / grouser_count

            # X-Z 평면에서 바퀴 둘레 위치 계산
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

            # grouser가 바퀴 둘레 방향에 맞게 놓이도록 회전시킨다.
            grouser.SetRot(q_from_axis_angle(chrono.ChVector3d(0, 1, 0), -angle))

            set_body_color(grouser, chrono.ChColor(0.55, 0.57, 0.60))
            self.system.Add(grouser)
            self.wheel_visuals.append(grouser)

            # grouser가 wheel과 함께 회전하도록 고정한다.
            self._fix_to_body(grouser, wheel)

    def _fix_to_body(self, body, parent):
        """
        body를 parent body에 fixed joint로 연결한다.

        hub/grouser처럼 바퀴와 함께 움직여야 하는 시각 요소를 wheel에 부착할 때 사용한다.
        """
        joint = chrono.ChLinkMateFix()
        joint.Initialize(body, parent, make_frame(body.GetPos()))
        self.system.Add(joint)

    # =========================================================================
    # 6. Steering and drive motors
    # =========================================================================

    def _create_steering_motors(self):
        """
        앞바퀴 조향 모터를 생성한다.

        steering motor는 chassis와 knuckle 사이에 연결된다.
        모터 각도 명령을 바꾸면 knuckle이 회전하고, 그 결과 앞바퀴 방향이 바뀐다.
        """
        self.steer_motors["FL"] = self._create_steering_motor(
            "steer_FL", self.knuckles["FL"], self.chassis, front_x, left_y, wheel_z
        )
        self.steer_motors["FR"] = self._create_steering_motor(
            "steer_FR", self.knuckles["FR"], self.chassis, front_x, right_y, wheel_z
        )

    def _create_steering_motor(self, name, child, parent, x, y, z):
        """
        회전각 제어 방식의 조향 모터를 생성한다.

        ChLinkMotorRotationAngle:
            지정된 angle function을 따라 두 body 사이의 상대 회전각을 제어한다.
        """
        motor = chrono.ChLinkMotorRotationAngle()
        motor.SetName(name)

        # 조향축 위치에 frame을 둔다.
        # 기본 회전축 convention은 Chrono link motor 설정에 따른다.
        motor.Initialize(child, parent, make_frame(chrono.ChVector3d(x, y, z)))

        # 초기 조향각은 0 rad
        motor.SetAngleFunction(make_const_function(0.0))

        self.system.Add(motor)
        return motor

    def _create_drive_motors(self):
        """
        네 바퀴의 구동 모터를 생성한다.

        앞바퀴:
            wheel과 knuckle 사이에 drive motor 연결

        뒷바퀴:
            wheel과 chassis 사이에 drive motor 연결
        """
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
        """
        바퀴 회전 속도 모터를 생성한다.

        ChLinkMotorRotationSpeed:
            지정된 speed function을 따라 두 body 사이의 상대 회전속도를 제어한다.

        현재 모델에서는 torque limit이 없는 ideal speed motor에 가까우므로,
        실제 구동계보다 강한 구동이 걸릴 수 있다.
        """
        motor = chrono.ChLinkMotorRotationSpeed()
        motor.SetName(name)

        # 바퀴가 Y축을 기준으로 회전하도록 motor frame을 보정한다.
        rot = q_from_axis_angle(chrono.ChVector3d(1, 0, 0), -math.pi / 2.0)

        motor.Initialize(child, parent, make_frame(chrono.ChVector3d(x, y, z), rot))

        # 초기 바퀴 회전속도는 0 rad/s
        motor.SetSpeedFunction(make_const_function(0.0))

        self.system.Add(motor)
        return motor

    # =========================================================================
    # 7. Control update
    # =========================================================================

    def synchronize(self, driver_inputs, dt):
        """
        driver/controller 입력을 로버의 실제 motor 명령으로 변환한다.

        입력:
            speed_cmd
            steering_cmd
            turn_mode

        출력:
            front steering motor angle
            left/right wheel motor speed
        """
        self.driver_inputs = driver_inputs

        # 목표 속도 [m/s]
        target_speed = driver_inputs.speed_cmd

        # 목표 조향각 [rad]
        # steering_cmd는 [-1, 1] 범위이고 max_steer_angle을 곱해 실제 조향각으로 변환한다.
        # steering_cmd > 0 means turn left (+Y).
        target_steer = driver_inputs.steering_cmd * max_steer_angle

        # 속도와 조향각이 순간적으로 바뀌지 않도록 변화율 제한을 적용한다.
        self.actual_speed = approach(self.actual_speed, target_speed, max_speed_rate * dt)
        self.actual_steer_angle = approach(
            self.actual_steer_angle, target_steer, max_steer_rate * dt
        )

        # 중심 조향각으로부터 좌우 앞바퀴 조향각을 계산한다.
        steer_left, steer_right = self._compute_steering_angles(self.actual_steer_angle)

        # 목표 선속도를 바퀴 각속도로 변환하고,
        # 좌우 바퀴 속도 차이를 추가해 회전을 보조한다.
        left_omega, right_omega = self._compute_side_omegas(
            self.actual_speed / wheel_radius,
            driver_inputs.steering_cmd,
            driver_inputs.turn_mode,
        )

        # 앞바퀴 조향 모터에 좌우 조향각 적용
        self.steer_motors["FL"].SetAngleFunction(make_const_function(steer_left))
        self.steer_motors["FR"].SetAngleFunction(make_const_function(steer_right))

        # 왼쪽 바퀴와 오른쪽 바퀴에 서로 다른 회전속도 적용
        for name in self.left_wheel_names:
            self.drive_motors[name].SetSpeedFunction(make_const_function(left_omega))
        for name in self.right_wheel_names:
            self.drive_motors[name].SetSpeedFunction(make_const_function(right_omega))

    def _compute_steering_angles(self, center_angle):
        """
        중심 조향각으로부터 좌우 앞바퀴 조향각을 계산한다.

        Ackermann-style steering:
            회전 시 안쪽 바퀴가 바깥쪽 바퀴보다 더 크게 꺾이도록 한다.

        Parameters
        ----------
        center_angle : float
            중심 조향각 [rad]

        Returns
        -------
        tuple[float, float]
            steer_left, steer_right [rad]
        """
        if abs(center_angle) < 1e-6:
            return 0.0, 0.0

        # 조향 방향
        turn_sign = 1.0 if center_angle > 0 else -1.0

        # 중심 조향각의 크기
        base = abs(center_angle)

        # 단순 bicycle model 기반 회전반경
        radius = wheelbase / math.tan(base)

        # 안쪽/바깥쪽 바퀴의 조향각
        inner = math.atan(wheelbase / max(1e-6, radius - track_width / 2.0))
        outer = math.atan(wheelbase / max(1e-6, radius + track_width / 2.0))

        # 회전 방향에 따라 좌우 바퀴에 inner/outer를 배정한다.
        if turn_sign > 0:
            return inner, outer
        return -outer, -inner

    def _compute_side_omegas(self, base_omega, steering_cmd, turn_mode):
        """
        좌우 바퀴 회전속도를 계산한다.

        기본 각속도:
            omega = v / r

        여기에 steering_cmd에 비례한 좌우 속도 차이를 추가한다.
        turn_mode가 커질수록 pivot-turn에 가까운 큰 좌우 속도 차이를 준다.
        """
        # 일반 조향 시 사용하는 작은 좌우 속도 차이
        normal_delta = 0.18 * steering_cmd * abs(base_omega)

        # pivot-turn 성향을 위한 큰 좌우 속도 차이
        pivot_delta = 0.95 * steering_cmd * max(abs(base_omega), 0.6)

        # turn_mode로 normal_delta와 pivot_delta를 blending
        delta = (1.0 - turn_mode) * normal_delta + turn_mode * pivot_delta

        # steering_cmd > 0 means turn left, so the right wheels should run faster.
        return base_omega - delta, base_omega + delta

    # =========================================================================
    # 8. State query and summary
    # =========================================================================

    def get_yaw_rad(self):
        """
        현재 chassis의 yaw angle을 rad 단위로 반환한다.
        waypoint controller에서 heading error 계산에 사용된다.
        """
        return self.chassis.GetRot().GetCardanAnglesXYZ().z

    def get_state(self, time):
        """
        현재 로버 상태를 RoverState dataclass로 반환한다.

        이 함수의 결과는 CSV logging과 path plot 생성에 사용된다.
        """
        pos = self.chassis.GetPos()
        roll_deg, pitch_deg, yaw_deg = quat_to_rpy_deg(self.chassis.GetRot())
        steer_left, steer_right = self._compute_steering_angles(self.actual_steer_angle)

        return RoverState(
            time=time,
            x=pos.x,
            y=pos.y,
            z=pos.z,
            roll_deg=roll_deg,
            pitch_deg=pitch_deg,
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
        """
        로버 설계와 실험 설정을 터미널에 출력한다.

        실행 직후 현재 모델이 어떤 구조인지 빠르게 확인하기 위한 요약 함수다.
        """
        print("[Design] Custom Viper-style rover")
        if self.terrain_mode == "flat":
            print("  terrain  : flat textured ground")
        else:
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

        if self.control_mode in {"waypoints", "rl"}:
            print(f"  waypoints: {len(WAYPOINTS)} targets")
