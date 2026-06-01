# 2.2 Component

`2.2 Component`는 Command 단계의 Chrono API를 실제 구현 대상의 부품 단위로 묶어 설명한 보고서 폴더이다. Core Physics/Solver, 로버/차량, 환경/Terrain, 충돌/접촉 측정, 데이터 출력/시각화 Component를 각각 카탈로그처럼 정리하고, 관련 코드와 렌더 이미지, 그래프, CSV 산출물을 함께 보관한다.

## 파일 목록

- [2.2.1 Component 단계의 정의와 역할](2.2.1_component_definition.md) - Core Physics/Solver와 Runtime/Config cross-cutting Component 포함
- [2.2.2 로버/차량 Component 설계](2.2.2_rover_vehicle_components.md)
- [2.2.3 환경/Terrain Component 설계](2.2.3_environment_terrain_components.md)
- [2.2.4 충돌/접촉 측정 Component 설계](2.2.4_collision_contact_components.md)
- [2.2.5 데이터 출력/시각화 Component 설계](2.2.5_data_visualization_components.md)

## 읽는 순서

| 순서 | 문서 | 핵심 내용 |
| --- | --- | --- |
| 1 | `2.2.1_component_definition.md` | Component 단계의 의미, Core Physics/Solver 계약, Runtime/Config 계약, Command와 System 사이의 역할, 설명 기준 |
| 2 | `2.2.2_rover_vehicle_components.md` | Chassis, wheel/tire, joint, motor, powertrain/driveline/brake, steering, suspension, visual/collision shape |
| 3 | `2.2.3_environment_terrain_components.md` | Ground, obstacle, contact material, RigidTerrain, heightmap, SCMTerrain, advanced terrain selection |
| 4 | `2.2.4_collision_contact_components.md` | Collision shape, contact material, reporter, force logger, event detector |
| 5 | `2.2.5_data_visualization_components.md` | CSV schema, state/control/contact logging, graph generation, screenshot/sensor output |

| Component catalog atlas |
|---|
| ![Project Chrono Component catalog atlas](images/renders/component_catalog_atlas.png) |

**설명.** 이 atlas는 2.2 전체의 전역 색인이다. 중앙 장면의 rover, terrain, obstacle, contact point, sensor, output artifact를 먼저 보고, 어떤 책임을 고를지 정한 뒤 해당 문서의 Component card로 들어간다.

## Global Component Catalog

| component_id | Display name | Owner doc | Chrono module/class family | Owns | Primary outputs | Validation artifact |
|---|---|---|---|---|---|---|
| `runtime.system` | Simulation Runtime / Physics Context | `2.2.1` | Core `ChSystem`, `ChAssembly`, `ChPhysicsItem` registry | system identity, item registry, current time, counters/timers | `run_metadata.json`, item registry summary | `runtime_config_component_map.png` |
| `runtime.contact_method` | Contact Method Runtime Boundary | `2.2.1`, `2.2.4` | `ChSystemNSC`, `ChSystemSMC`, contact material families | NSC/SMC choice, material class match, contact force/adhesion/tangential model | contact method metadata, compatibility checklist | `core_physics_solver_constraint_catalog.png` |
| `runtime.solver` | Solver / Backend Selection | `2.2.1` | `ChSolver`, built-in/direct/multicore solver families | solver type, direct/iterative backend, tolerance, max iterations, setup/solve counts | solver evidence fields, convergence notes | `core_physics_solver_constraint_catalog.png` |
| `runtime.timestepper` | Timestepper / Step Policy | `2.2.1` | `ChTimestepper`, `DoStepDynamics`, Vehicle advance loop | timestepper type, fixed `dt_s`, substep/sync policy, hard-contact compatibility | timestep metadata, step count, timestamp alignment | `core_physics_solver_constraint_catalog.png` |
| `runtime.gravity_recovery` | Gravity / Penetration Recovery Runtime Fields | `2.2.1`, `2.2.3`, `2.2.4` | `ChSystem` gravity and recovery speed APIs, NSC bounce threshold | `gravity_mps2`, axis convention, setter source, recovery/bounce speeds | gravity/recovery metadata, stability checklist | `runtime_config_component_map.png` |
| `runtime.collision_system` | Collision System / Backend Runtime Field | `2.2.1`, `2.2.4` | `ChCollisionSystem`, Bullet/Multicore where available | backend type, thread count, envelope/margin, collision timers | collision backend manifest | `collision_contact_measurement_catalog.png` |
| `runtime.config` | Run Config / Model Spec | `2.2.1` | parsers/YAML/JSON/config helpers | resolved parameters, units, seed, fallback policy | resolved config, parameter table | `runtime_config_component_map.png` |
| `model.spec_resolver` | Model Spec Resolver / JSON-YAML Import | `2.2.1` | Chrono Vehicle JSON hierarchy, Chrono::Parsers YAML | raw/resolved paths, source-to-Chrono map, unit/axis transform | `model_import_manifest.json` | `external_integration_component_map.png` |
| `model.urdf_import` | URDF Import Boundary | `2.2.1` | Chrono::Parsers `ChParserURDF` | link/joint/body map, root pose, mesh collision policy | URDF import manifest | `external_integration_component_map.png` |
| `asset.cad_step` | CAD/STEP Asset Import | `2.2.1` | Chrono::Cascade, OpenCASCADE STEP | named shape hierarchy, tessellation, mass/inertia, collision proxy | CAD/asset manifest | `external_integration_component_map.png` |
| `integration.fmi` | FMI / FMU Adapter | `2.2.1`, `2.2.5` | Chrono::FMI, FMU import/export | FMU path/hash, variable map, causality, co-sim step | FMU variable table, synchronized log | `external_integration_component_map.png` |
| `integration.ros` | ROS Bridge / Handler Boundary | `2.2.1`, `2.2.5` | Chrono::ROS handlers, clock/body/tf/vehicle/sensor handlers | topic manifest, message type, handler list, frame map, latency policy | topic/handler manifest | `external_integration_component_map.png` |
| `integration.vehicle_cosim` | Vehicle/Terrain Co-sim Boundary | `2.2.1`, `2.2.2`, `2.2.3` | Vehicle co-simulation MBS/tire/terrain nodes | node role, rank/process, BODY/MESH interface, sync step | node manifest, exchanged state/force log | `external_integration_component_map.png` |
| `integration.synchrono` | SynChrono Distributed Agent Boundary | `2.2.1` | SynChrono MPI/DDS/FlatBuffers agent simulation | agent id, comm backend, sync period, world/GPS frame | agent sync manifest | `external_integration_component_map.png` |
| `core.body` | Rigid Body / Inertial Component | `2.2.1`, `2.2.2` | `ChBody`, `ChBodyEasy*`, `ChBodyAuxRef` | mass, inertia, REF/COM frame, pose, fixed/sleeping policy, visual/collision refs | state CSV fields, body registry row | `chrono_default_shape_types.png` |
| `core.visual_asset` | Visual Asset / Rendering Shape | `2.2.1`, `2.2.5` | `ChVisualModel`, `ChVisualShape*`, `ChVisualMaterial` | shape frame, material/texture path, visibility, mutable/wireframe flag, visual-vs-collision note | visual asset manifest, render screenshot | `chrono_default_shape_types.png` |
| `core.link_constraint` | Link / Bilateral Constraint | `2.2.1`, `2.2.2` | `ChLink*`, mate/lock/revolute/prismatic/distance families | body pair, local/absolute frames, constrained coordinate mask, reaction frame | joint metadata, reaction checks | `core_physics_solver_constraint_catalog.png` |
| `core.spring_damper` | Translational/Rotational Spring-Damper | `2.2.1`, `2.2.2` | `ChLinkTSDA`, `ChLinkRSDA` | endpoints/axis, rest length/angle, stiffness, damping, force law | force/travel or angle/torque log | `core_physics_solver_constraint_catalog.png` |
| `core.motor_constraint` | Speed/Position Motor Constraint | `2.2.1`, `2.2.2` | `ChLinkMotorRotationSpeed`, position/speed motor families | imposed motion function, axis/frame, rate limit, tracking check | command log, actual speed/position | `core_physics_solver_constraint_catalog.png` |
| `core.motor_torque` | Torque / Effort Motor | `2.2.1`, `2.2.2` | `ChLinkMotorRotationTorque`, linear torque/force motor families | torque/force function, saturation, sign convention, body pair | torque log, acceleration response | `core_physics_solver_constraint_catalog.png` |
| `core.shaft_1d` | 1D Shaft / Driveline State | `2.2.1`, `2.2.2` | `ChShaft`, shaft/driveline connector families | inertia, angular speed, torque path, fixed/sleeping state | shaft speed/torque log | `rover_powertrain_driveline_brake_tire_flow.png` |
| `core.function_input` | Function / Command Profile | `2.2.1`, `2.2.2`, `2.2.5` | `ChFunction` family, sampled command sources | function type, unit, time domain, continuity, saturation, derivative risk | sampled command log, profile manifest | `rover_driver_input_controller_component.png` |
| `flex.mesh` | Flexible Mesh / Node Element Registry | `2.2.1` | Chrono::FEA `ChMesh`, node/element families | mesh id, node/element registry, flexible DOF | FEA mesh manifest, node/element count | `flexible_body_fea_modal_component_catalog.png` |
| `flex.material_section` | FEA Material / Section Law | `2.2.1`, `2.2.2`, `2.2.3` | FEA material, beam/shell/solid section families | constitutive law, section geometry, density/damping | material law manifest | `flexible_body_fea_modal_component_catalog.png` |
| `flex.boundary_attachment` | FEA Boundary / Attachment / Load | `2.2.1`, `2.2.2` | FEA constraints, loads, body-node attachment | boundary nodes, body/link/load map | boundary condition map, reaction output | `flexible_body_fea_modal_component_catalog.png` |
| `flex.contact_surface` | Flexible Contact Surface | `2.2.1`, `2.2.4` | FEA contact surface + contact material | flexible contact nodes/elements, material, contact method | flexible contact debug/evidence | `flexible_body_fea_modal_component_catalog.png` |
| `flex.modal_reduction` | Modal Reduced Flexible Assembly | `2.2.1` | Chrono::Modal `ChModalAssembly` | boundary/internal split, modal basis, damping, frequencies | mode table, mode-shape render, basis manifest | `flexible_body_fea_modal_component_catalog.png` |
| `vehicle.chassis` | Chassis / Payload / Sensor Mount | `2.2.2` | Vehicle/Robot/Core body family | reference body, payload pose, mount frames | chassis probe CSV | `rover_vehicle_component_overview.png` |
| `vehicle.wheel_tire_track` | Wheel, Tire, Track Shoe | `2.2.2`, `2.2.3` | Core cylinder, Vehicle tire/track subsystem | rolling body, tire model, contact target | tire/terrain evidence fields | `rover_wheel_tire_component.png`, `tracked_vehicle_components.png` |
| `vehicle.drive` | Motor, Steering, Suspension, Driveline, Brake | `2.2.2` | Vehicle subsystem and Core link/motor family | actuator command, kinematic/force path | control log, flow metadata | `rover_powertrain_driveline_brake_tire_flow.png` |
| `vehicle.system_export` | Vehicle System / Component List Evidence | `2.2.2`, `2.2.5` | `ChWheeledVehicle`, `ChTrackedVehicle`, `ChVehicle` output/export APIs | vehicle frame, subsystem template names, axle/side ids, output enable flags | vehicle component list, subsystem type log | `rover_vehicle_subsystem_ownership_map.png` |
| `vehicle.model_spec` | Vehicle Model Spec / Template Resolver | `2.2.2`, `2.2.1` | Chrono::Vehicle JSON/template hierarchy, data path helpers | top-level JSON, nested subsystem files, template names, source hashes, source-to-Chrono map | `vehicle_model_spec_manifest.json` | `rover_vehicle_subsystem_ownership_map.png` |
| `vehicle.robot_assets` | Built-in Vehicle / Robot Asset Index | `2.2.2` | Chrono Vehicle/Robot data paths and sample asset families | built-in rover/robot/wheeled/tracked model refs, asset base path, module gate | VSG visual asset captures, capture manifests, model spec seed list | `chrono_builtin_robot_rover_assets.png`, `chrono_builtin_wheeled_vehicle_assets.png`, `chrono_builtin_tracked_vehicle_assets.png` |
| `vehicle.frame_hardpoints` | Vehicle Frame / Hardpoint Map | `2.2.2` | ISO vehicle frame, subsystem local frames, hardpoint tables | vehicle/world frame, subsystem location/orientation, hardpoint names, axis vectors, transform checks | hardpoint map manifest | `rover_vehicle_subsystem_ownership_map.png` |
| `vehicle.axle` | Axle / Wheel Index Map | `2.2.2` | `ChAxle`, axle lists, spindle/wheel accessors | axle index, side, wheel location, driven/steerable/dual flags | axle-wheel map, spindle state table | `rover_suspension_steering_components.png` |
| `vehicle.suspension` | Suspension / Spindle Load Path | `2.2.2` | `ChSuspension`, spindle state APIs, hardpoint models | suspension id/type, travel, wheel load, spindle pose, hardpoint source | suspension/spindle metadata, wheel load log | `rover_suspension_steering_components.png` |
| `vehicle.antirollbar` | Anti-roll Bar / Roll Coupling | `2.2.2` | anti-roll bar subsystem family, RSDA/arms where modeled | axle index, left/right travel coupling, stiffness, output flag | anti-roll torque/constraint log | `rover_suspension_steering_components.png` |
| `vehicle.steering` | Steering Mechanism / Wheel Heading | `2.2.2` | `ChSteering`, steering subsystem APIs, skid-steer command split | normalized input, mechanism type, steering angle, rack/tie-rod or side-speed policy | steering command/state log | `rover_steering_component.png` |
| `vehicle.wheel` | Wheel / Spindle Body | `2.2.2` | `ChWheel`, spindle body/state APIs, Core cylinder prototype | wheel id, axle/side/location, mass/inertia, omega, visual/collision mode | wheel state table | `rover_wheel_tire_component.png` |
| `vehicle.tire_model` | Tire Force Model / Contact Patch | `2.2.2`, `2.2.3` | `ChTire`, `RigidTire`, `TMeasy`, `Fiala`, `Pac89/Pac02`, FEA tires | tire family, parameter source, terrain compatibility, slip/contact outputs | tire force/slip schema | `rover_wheel_tire_component.png` |
| `vehicle.powertrain` | Powertrain / Engine-Transmission | `2.2.2` | `ChPowertrainAssembly`, engine/transmission families, `ChShaft` | throttle, engine map, gear, driveshaft speed/torque | engine/gear/driveshaft log | `rover_powertrain_driveline_brake_tire_flow.png` |
| `vehicle.driveline` | Driveline / Torque Split | `2.2.2` | `ChDrivelineWV`, shaft/simple 2WD/4WD/XWD families | drive type, driven axles, torque split, differential/bias/lock state | wheel torque distribution log | `rover_powertrain_driveline_brake_tire_flow.png` |
| `vehicle.brake` | Brake / Wheel-Side Torque | `2.2.2` | `ChBrake`, `ChBrakeSimple`, `ChBrakeShafts`, track brake | brake input, max torque, lock state, axle/side target | brake torque log | `rover_powertrain_driveline_brake_tire_flow.png` |
| `vehicle.track_assembly` | Tracked Vehicle Assembly | `2.2.2`, `2.2.3`, `2.2.4` | `ChTrackedVehicle`, `ChTrackAssembly`, sprocket/idler/road wheel/track shoe families | side, shoe count/type, sprocket profile, idler tension, track contact count | track assembly manifest, contact/tension log | `tracked_vehicle_components.png` |
| `vehicle.track_shoe` | Track Shoe / Pad Contact Segment | `2.2.2`, `2.2.4` | `ChTrackShoe`, single/double pin, band/bushing/ANCF shoe families | shoe type, pitch, guide pin, body state, collision geometry, tension | shoe state/contact sample | `tracked_vehicle_components.png` |
| `vehicle.sprocket` | Sprocket / Track Drive Interface | `2.2.2` | `ChSprocket`, gear body, axle shaft | tooth/profile, assembly radius, compatible shoe type, drive torque | sprocket engagement metadata | `tracked_vehicle_components.png` |
| `vehicle.idler_tensioner` | Idler / Track Tensioner | `2.2.2` | `ChIdler`, idler wheel/tensioner mechanisms | idler location, preload, travel, tension policy | idler travel/tension log | `tracked_vehicle_components.png` |
| `vehicle.road_wheel` | Road Wheel / Roller Support | `2.2.2` | `ChTrackWheel`, road wheel and roller subsystems | wheel count, radius, spacing, suspension id, guide pin compatibility | road-wheel contact/load log | `tracked_vehicle_components.png` |
| `terrain.interface` | Terrain Query Interface / Authority Boundary | `2.2.3`, `2.2.2` | `ChTerrain`, height/normal/friction query APIs | query frame, height/normal/friction source, sync/advance order, tire compatibility | terrain surface probe schema | `terrain_advanced_selection_catalog.png` |
| `terrain.query_contract` | Query Validity / Consumer Contract | `2.2.3`, `2.2.2` | `ChTerrain` consumers, tire/controller query paths | consumer family, valid-for-tire flag, contact-solver flag, height/normal/friction functor ids, placeholder policy | terrain query probe | `terrain_advanced_selection_catalog.png` |
| `terrain.core_ground` | Core Fixed Ground / Contact Plane | `2.2.3`, `2.2.4` | fixed `ChBody`, `ChBodyEasyBox`, contact material | top surface frame, fixed flag, collision material, ground body id | ground render, contact probe | `terrain_ground_obstacle_components.png` |
| `terrain.obstacle_field` | Obstacle / Terrain Collision Target | `2.2.3`, `2.2.4` | fixed/dynamic `ChBody`, collision shape family | obstacle pose, fixed/dynamic policy, shape/material id, event target | obstacle render, event/contact log | `terrain_ground_obstacle_components.png` |
| `terrain.material_region` | Terrain Material / Friction Region | `2.2.3`, `2.2.4` | `ChContactMaterialNSC/SMC`, `ChTerrain::FrictionFunctor`, patch material | `terrain_mu_query`, `contact_material_mu`, region bounds, material provenance | friction map, material effect graph | `terrain_contact_material_regions.png` |
| `terrain.flat` | FlatTerrain / Infinite Query Plane | `2.2.3` | Vehicle `FlatTerrain`, `ChTerrain` interface | height, constant/position friction, no collision geometry, semi-empirical tire guard | flat terrain metadata | `terrain_advanced_selection_catalog.png` |
| `terrain.rigid_patch` | RigidTerrain Patch | `2.2.3` | Vehicle `RigidTerrain`, patch BOX/MESH/HEIGHT_MAP | patch id, pose, bounds, material, texture, source file/hash | rigid patch render, height/friction probe | `terrain_rigid_patch_component.png` |
| `terrain.heightmap_mesh` | Heightmap / Mesh Terrain Source | `2.2.3` | `RigidTerrain` height-map/mesh patch, OBJ/BMP source | source path/hash, height scale, origin, interpolation, bounds | heightmap render, height profile graph | `terrain_heightmap_component.png` |
| `terrain.crg` | CRGTerrain / OpenCRG Road Profile | `2.2.3` | Vehicle `CRGTerrain`, OpenCRG profile | CRG path/hash, road frame, s/l bounds, friction source | CRG profile manifest | `terrain_advanced_selection_catalog.png` |
| `terrain.scm` | SCMTerrain / Soil Contact Model Grid | `2.2.3` | Vehicle `SCMTerrain`, SCM soil callback/node data | Bekker/Mohr/Janosi parameters, grid spacing, moving patch, plot type | sinkage/rut profile, SCM node evidence | `terrain_scm_deformation_component.png` |
| `terrain.granular_dem` | Granular / DEM Particle Terrain | `2.2.3` | Vehicle `GranularTerrain`, DEM/Multicore/GPU backend identity | particle radius/density/count, domain, moving patch, settling checkpoint, backend | particle-domain manifest | `terrain_advanced_selection_catalog.png` |
| `terrain.fea` | FEATerrain / Deformable Mesh Terrain | `2.2.3`, `2.2.1` | Vehicle `FEATerrain`, Chrono::FEA mesh/material | mesh id, element type/count, material law, boundary condition, stress/deformation output | FEA terrain manifest | `terrain_advanced_selection_catalog.png` |
| `terrain.crm` | CRMTerrain / SPH-FSI Continuum Terrain | `2.2.3` | Vehicle `CRMTerrain`, FSI-SPH problem builder | SPH spacing, BCE files, rheology, active domain, coupled advance order | CRM/FSI domain manifest | `terrain_advanced_selection_catalog.png` |
| `environment.field` | Environment Field / Gravity-Slope-Wind | `2.2.3`, `2.2.1` | runtime gravity, terrain frame, `ChForce`/external force profile | gravity vector, slope frame, wind/force vector, planet/scenario metadata | environment field render, run metadata | `terrain_environment_field_component.png` |
| `collision.system_lifecycle` | Collision System Lifecycle / Backend | `2.2.4`, `2.2.1` | `ChSystem`, `ChCollisionSystem`, Bullet/Multicore | backend type, bind/init/run/report sequence, thread count, envelope/margin, timers | `collision_system_manifest.json`, backend comparison | `collision_contact_measurement_catalog.png` |
| `collision.shape_manifest` | Collision Shape / Contactable Target Manifest | `2.2.4` | `ChCollisionModel`, `ChCollisionShape::Type`, `ChContactable` | shape enum/class, primitive/compound/mesh/2D policy, local frames, mutable/parent shape, material id | `collision_shape_manifest.csv/json`, visual/collision comparison | `collision_visual_vs_collision_shape.png` |
| `collision.model_registry` | Collision Model Registry / Body-Shape Binding | `2.2.4`, `2.2.2`, `2.2.3` | `ChBody`, `ChCollisionModel`, `ChMesh` contact surface | owner contactable id, enabled flag, shape count, material sharing, REF-frame pose | collision model registry manifest | `collision_contact_measurement_catalog.png` |
| `collision.family_filter` | Collision Family / Mask Filter Map | `2.2.4` | `ChCollisionModel::SetFamily`, `AllowCollisionsWith`, `DisallowCollisionsWith` | family id/name, resolved mask, included/excluded pairs, reporter scope, failure mode | `collision_family_filter_map.csv/json` | `collision_contact_reporter_scope.png` |
| `collision.material_surface` | Contact Surface Material | `2.2.4`, `2.2.3` | `ChContactMaterialNSC/SMC`, `ChContactMaterialData` | material id, NSC/SMC fields, calibration/provenance, terrain query split | `contact_material_manifest.csv/json`, material table | `collision_contact_material_effect_graph.png` |
| `collision.material_pair_policy` | Contact Pair Composite Material Policy | `2.2.4` | `ChContactContainer::AddContactCallback`, composite material classes | pair material ids, mixing/override rule, modified fields, callback class, contactinfo filter | `contact_pair_material_policy.csv/json` | `collision_contact_material_effect_graph.png` |
| `collision.callback_policy` | Collision/Contact Callback Policy | `2.2.4` | `BroadphaseCallback`, `NarrowphaseCallback`, `AddContactCallback`, `ReportContactCallback`, `VisualizationCallback` | phase, Chrono hook, input object, mutation/report-only policy, fallback behavior | `contact_callback_manifest.csv/json` | `collision_contact_measurement_catalog.png` |
| `contact.container_reporter` | Contact Container / Reporter Scope | `2.2.4` | `ChContactContainer*`, `ReportAllContacts` | container class, callback class, pair filter, frame conversion, reset policy, unsupported contactable type | `contact_container_manifest.csv/json`, pair contact CSV | `collision_contact_reporter_scope.png` |
| `contact.force_torque` | Contact Force/Torque Logger | `2.2.4`, `2.2.5` | `ReportContactCallback`, `ChBody::GetContactForce/Torque`, `ComputeContactForces` | force/torque source, pair order, contact frame, aggregation, sign convention, cache policy | `contact_force_torque_probe.csv`, force graphs | `collision_contact_debug_vectors.png` |
| `contact.event_detector` | Contact Event Detector | `2.2.4`, `2.2.5` | reporter count/force thresholds, CSV/graph pipeline | first/peak/separation/dwell rule, threshold/debounce, event label | event timeline CSV/graph | `collision_event_timeline_graph.png` |
| `contact.debug_visual` | Contact Debug Frame / Visual Evidence | `2.2.4`, `2.2.5` | collision visualization flags, render backend, reporter debug vectors | contact point, normal/tangent frame, force vector, visual-vs-collision link | `contact_frame_debug_manifest.csv/json` | `collision_contact_debug_vectors.png` |
| `data.schema_registry` | Schema Registry / Logger Columns | `2.2.5` | CSV/JSON schema, SI units, frame conventions | schema id, units, required/optional fields, missing-value policy | schema table, writer fieldnames | `data_visualization_artifact_catalog.png` |
| `data.timebase_scheduler` | Logger Timebase / Sampling Alignment | `2.2.5`, `2.2.1` | simulation clock, logger cadence, sensor update/ready time | clock source, step index, sample period, resampling, dropped row policy | logger timebase manifest | `data_visualization_artifact_catalog.png` |
| `data.run_metadata` | Run Metadata / Reproducibility Context | `2.2.5`, `2.2.1` | runtime config, module availability, artifact hashes | run id, Chrono version, dt, solver, seed, fallback policy | `run_metadata.json` contract | `data_visualization_artifact_catalog.png` |
| `data.artifact_manifest` | Artifact Manifest / Evidence Bundle | `2.2.5` | CSV/PNG/raw files, hashes, producer scripts | artifact path/type, input hash, output hash, evidence level | artifact manifest schema | `data_visualization_artifact_catalog.png` |
| `data.io_writer` | Data Writer Backend | `2.2.5` | Python CSV, `ChWriterCSV`, `ChOutputASCII/HDF5` | writer backend, delimiter/output mode, schema id, path/hash | CSV/HDF5/output manifest | `data_visualization_artifact_catalog.png` |
| `data.chrono_output_db` | Chrono Native Output Database | `2.2.5`, `2.2.2` | `ChOutput`, `ChOutputASCII`, `ChOutputHDF5`, subsystem `Output` hooks | output type/mode, section names, frame id, component scope, schema map | `chrono_output_database_manifest.json` | `data_visualization_artifact_catalog.png` |
| `data.checkpoint_restart` | Checkpoint / Replay Artifact | `2.2.5`, `2.2.1`, `2.2.4` | `ChCheckpoint`, `ChCheckpointASCII`, body/shape checkpoint utilities | checkpoint scope, body/shape count, restart validity, restore assumptions | `checkpoint_manifest.csv/json` | `data_visualization_artifact_catalog.png` |
| `visual.runtime` | Runtime Visualization | `2.2.5` | `ChVisualSystemVSG`, Irrlicht, Vehicle visual wrappers | camera, lighting, visible component ids, backend availability | screenshot/render manifest | `data_visualization_sensor_components.png` |
| `visual.asset_manifest` | Visual Asset / Sensor Scene Coverage | `2.2.5`, `2.2.1` | `ChVisualModel`, `ChVisualShape*`, `ChVisualMaterial`, mesh/texture assets | owner item, shape frame, material slots, mesh path/hash, runtime/sensor visibility | `visual_asset_manifest.csv/json` | `data_visualization_sensor_components.png` |
| `visual.offline_export` | Offline Visualization Export | `2.2.5` | `WriteVisualizationAssets`, POV-Ray, Blender/Postprocess | frame CSV, visual assets, mesh paths, render script | offline export manifest | `data_visualization_artifact_catalog.png` |
| `postprocess.plot_export` | Plot / Postprocess Export | `2.2.5` | `ChGnuPlot`, matplotlib, graph manifest | input CSV/hash, axis units, smoothing, output format | graph PNG/PDF/EPS manifest | `data_visualization_artifact_catalog.png` |
| `postprocess.gnuplot_backend` | GNUplot Script / Terminal Export | `2.2.5` | `postprocess::ChGnuPlot`, external GNUplot executable | `.gpl` script, terminal/output format, executable availability, input dat/hash | `gnuplot_plot_manifest.csv/json` | `data_visualization_artifact_catalog.png` |
| `sensor.layout` | Sensor Mount / Sensor Layout | `2.2.2`, `2.2.5` | chassis mount, Chrono::Sensor layout concept | parent body, mount pose, frame triad, intended filter chain | layout render, manifest stub | `data_visualization_sensor_components.png` |
| `sensor.manager` | Sensor Manager / Scene Gate | `2.2.5` | `ChSensorManager`, scene/lights/background, GPU/OptiX | device list, max engines, ray recursions, scene coverage | sensor manager manifest | `data_visualization_sensor_pipeline_catalog.png` |
| `sensor.scene_reconstruction` | Sensor Scene / Compatibility Gate | `2.2.5` | Chrono::Sensor scene, visual assets, OBJ/MTL/material coverage | compatible domain, lights/background, GPU/OptiX status, FSI unsupported note | `sensor_scene_manifest.json` | `data_visualization_sensor_pipeline_catalog.png` |
| `sensor.timing_schedule` | Sensor Timing / Render Engine Schedule | `2.2.5` | `ChSensor` update rate/lag/window, `ChSensorManager` engines/devices | requested/ready time, collection window, engine id, dropped/stale frame | `sensor_timing_schedule.csv/json` | `data_visualization_sensor_pipeline_catalog.png` |
| `sensor.filter_catalog` | Sensor Filter Class Catalog | `2.2.5` | `ChFilter*` save/access/convert/noise/visualize/radar/update families | filter class/order, input/output buffer, CPU copy, output path, failure behavior | `sensor_filter_catalog.csv/json` | `data_visualization_sensor_pipeline_catalog.png` |
| `sensor.filter_chain` | Sensor Filter Chain | `2.2.5` | `ChFilterSave`, access/noise/convert/visualize/radar filters | ordered filters, input/output buffers, save/access policy | filter chain manifest | `data_visualization_sensor_pipeline_catalog.png` |
| `sensor.output_writer` | Module-backed Sensor Output Writer | `2.2.5` | Camera, LiDAR, GPS, IMU, radar, tachometer sensors | artifact path, frame index, timestamps, checksum, dropped frame | frames/clouds/logs, sensor manifest | future module-backed sensor artifact required |

## Developer Lookup Paths

| Task | Start here | Companion sections | Expected artifacts | Metadata/schema to update |
|---|---|---|---|---|
| Core prototype를 Vehicle subsystem으로 올리기 | `2.2.1` Core catalog | `2.2.2` chassis/wheel/tire | shape render, chassis probe | body registry, runtime config |
| terrain을 선택하거나 바꾸기 | `2.2.3` terrain selection | `2.2.2` tire/track, `2.2.5` terrain probe | terrain render, height/sinkage graph | terrain component id, query/contact authority |
| contact force가 이상한 이유 찾기 | `2.2.4` failure catalog | `2.2.1` runtime, `2.2.3` material/terrain | force/count/component graphs, debug render | contact method, backend, material id, filter rule |
| flexible chassis/tire/beam/shell 모델링 | `2.2.1` Flexible Body / FEA catalog | `2.2.2` tire/structure, `2.2.3` FEATerrain, `2.2.4` contact | flexible FEA catalog, mesh manifest, stress/strain artifact | mesh id, node/element count, material law, boundary map |
| FEA assembly를 Modal로 축약 | `2.2.1` Modal Reduction Component | `2.2.2` vehicle attachment, `2.2.5` artifact manifest | mode table, mode-shape render, modal basis manifest | boundary/internal split, basis hash, frequency table |
| camera/LiDAR/IMU output 추가하기 | `2.2.5` sensor catalog | `2.2.2` sensor mount, `2.2.1` module availability | sensor layout render, manifest, raw frame/cloud/log | sensor manifest, filter chain, update rate |
| 증거 이미지/그래프 다시 만들기 | README image table | relevant owner doc | regenerated PNG/CSV | producer script, input hash, evidence level |
| System 단계로 조립하기 | `2.2.1` lifecycle contract | all owner docs | run metadata, resolved config, artifact bundle | component ids, schema registry, fallback policy |
| YAML/URDF/STEP 모델을 Chrono Component로 들이기 | `2.2.1` External Integration / Asset Import | `2.2.2` body/vehicle, `2.2.4` collision, `2.2.5` manifests | resolved import manifest, source-to-Chrono map, collision proxy map | raw path/hash, unit/axis transform, module availability |
| FMU/ROS/co-simulation을 연결하기 | `2.2.1` external integration boundary | `2.2.2` driver/vehicle, `2.2.5` data/sensor I/O | variable/topic/node manifest, synchronized logs | update rate, sync order, lag/timeout policy |

## Cross-Document Ownership Registry

| Shared concept | Canonical owner | Secondary consumers | Does not own | Handoff metadata |
|---|---|---|---|---|
| Contact Material | `2.2.4` solver contact material contract | `2.2.3` terrain patch, `2.2.2` tire/wheel, `2.2.1` runtime method | terrain query friction or SCM soil law | `material_id`, `contact_method`, `contact_material_mu` |
| Collision Shape | `2.2.4` collision geometry/reporting | `2.2.2` rover visual/collision, `2.2.3` obstacle/ground | visual mesh aesthetics | `shape_family`, local pose, envelope/margin, debug render |
| Terrain Query vs Contact Authority | `2.2.3` terrain catalog | `2.2.2` tire/track, `2.2.4` contact logger | tire model internals | `terrain_component_id`, `terrain_mu_query`, contact source |
| Sensor Mount/Pose | `2.2.2` physical mount frame | `2.2.5` sensor manager/output | raw sensor filter output | parent body, offset pose, frame convention |
| Flexible Body / FEA Mesh | `2.2.1` generic Chrono::FEA catalog | `2.2.2` FEA tire/structure, `2.2.3` FEATerrain, `2.2.4` flexible contact | Vehicle tire/terrain semantics or solver-specific contact interpretation | mesh id/hash, node/element registry, material law, boundary map |
| Modal Reduced Assembly | `2.2.1` Chrono::Modal reduction catalog | `2.2.2` flexible vehicle attachment, `2.2.5` artifact manifest | full FEA stress/strain validity outside reduction assumptions | modal basis hash, mode frequency table, boundary/internal map |
| Runtime Config | `2.2.1` runtime/config | all sections | domain-specific physical meaning | `run_id`, `resolved_config_hash`, `module_availability` |
| Artifact Metadata | `2.2.5` metadata/schema registry | all sections | physical validation interpretation | artifact path/hash, producer script, evidence level |
| Driver/Input vs Steering/Driveline | `2.2.2` vehicle subsystem ownership | `2.2.5` control logger, `2.2.1` motor/actuator | raw UI command semantics | command source, actuator id, normalized vs physical units |

## Evidence / Artifact Index

| artifact_path | artifact_type | Validates | Owner doc | Producer | Evidence level |
|---|---|---|---|---|---|
| `images/renders/component_catalog_atlas.png` | global render atlas | report navigation and ownership map | README / `2.2.1` | `code/common/generate_component_catalog_atlas_render.py` | concept render |
| `images/renders/core_physics_solver_constraint_catalog.png` | catalog render | runtime/core solver/link/motor ownership | `2.2.1` | `code/common/generate_core_physics_solver_constraint_catalog_render.py` | concept render |
| `images/renders/flexible_body_fea_modal_component_catalog.png` | catalog render | flexible body FEA/Modal ownership and evidence gates | `2.2.1` | `code/common/generate_flexible_body_fea_modal_component_catalog_render.py` | concept render |
| `images/renders/chrono_optional_module_dependency_ladder.png` | catalog render | requestable optional module dependency/evidence gates | README / `2.2.1` | `code/common/generate_chrono_optional_module_dependency_ladder_render.py` | concept render |
| `images/renders/chrono_builtin_wheeled_vehicle_assets.png` | VSG render capture | HMMWV visual asset/component coverage | `2.2.2` | `code/common/generate_chrono_builtin_wheeled_vehicle_assets_render.py` | PyChrono VSG capture |
| `images/renders/chrono_builtin_tracked_vehicle_assets.png` | VSG render capture | M113 tracked visual asset/component coverage | `2.2.2` | `code/common/generate_chrono_builtin_tracked_vehicle_assets_render.py` | PyChrono VSG capture |
| `images/renders/chrono_viper_vsg_capture.png` | VSG render capture | VIPER robot visual asset/component coverage | `2.2.2` | `code/common/generate_chrono_builtin_robot_rover_assets_render.py` | PyChrono VSG capture |
| `images/renders/chrono_curiosity_vsg_capture.png` | VSG render capture | Curiosity robot visual asset/component coverage | `2.2.2` | `code/common/generate_chrono_builtin_robot_rover_assets_render.py` | PyChrono VSG capture |
| `outputs/json/robot_vsg_capture_manifest.json` | VSG capture manifest | camera pose/FOV, image hashes, build/data roots, visible robot part ids | `2.2.2`, `2.2.5` | `code/common/generate_chrono_builtin_component_assets.py` | PyChrono VSG capture |
| `outputs/json/vehicle_vsg_capture_manifest.json` | VSG capture manifest | camera pose/FOV, image hashes, build/data roots, visible HMMWV/M113 part ids | `2.2.2`, `2.2.5` | `code/common/generate_chrono_builtin_component_assets.py` | PyChrono VSG capture |
| `images/renders/rover_vehicle_subsystem_ownership_map.png` | catalog render | rover/vehicle subsystem ownership and evidence path | `2.2.2` | `code/rover_vehicle/generate_rover_vehicle_subsystem_ownership_map_render.py` | concept render |
| `images/renders/rover_driver_input_controller_component.png` | component render | driver input/controller boundary and control logger contract | `2.2.2` | `code/rover_vehicle/generate_rover_driver_input_controller_component_render.py` | concept render |
| `images/renders/rover_powertrain_driveline_brake_tire_flow.png` | catalog render | vehicle drive/brake/tire flow | `2.2.2` | `code/rover_vehicle/generate_rover_powertrain_driveline_brake_tire_flow_render.py` | concept render |
| `images/renders/terrain_advanced_selection_catalog.png` | catalog render | advanced terrain module/evidence gate | `2.2.3` | `code/environment_terrain/generate_terrain_advanced_selection_catalog_render.py` | concept render |
| `images/renders/collision_contact_measurement_catalog.png` | catalog render | contact measurement pipeline | `2.2.4` | `code/collision_contact/generate_collision_contact_measurement_catalog_render.py` | concept render |
| `images/renders/data_visualization_artifact_catalog.png` | catalog render | output artifact ownership | `2.2.5` | `code/data_visualization/generate_data_visualization_artifact_catalog_render.py` | concept render |
| `images/renders/data_visualization_sensor_pipeline_catalog.png` | catalog render | Chrono::Sensor module lifecycle and artifact contract | `2.2.5` | `code/data_visualization/generate_data_visualization_sensor_pipeline_catalog_render.py` | concept render |
| `images/graphs/*` | graph PNG | linked CSV/probe interpretation | relevant owner doc | per-image graph script | fallback or PyChrono-derived graph depending on CSV `source` |
| `outputs/csv/*` | CSV probe/log | raw component evidence | relevant owner doc | component generator | fallback analytic or live PyChrono probe by `source` |

### Generated Evidence Manifest

Wildcard artifact rows above are only a coarse index. The current generated CSV/graph families below must be read with their `source` values; fallback analytic rows are useful for schema and graph wiring, but they are not proof of a live Chrono module-backed run.

| Artifact family | schema_id | Current `source` values present | Live Chrono? | Validates | Owner |
|---|---|---|---|---|---|
| `rover_vehicle_chassis_probe.csv` / chassis graph | `rover.chassis_smoke_probe.v0` | `deterministic_chassis_probe_pychrono_unavailable` | no | Core rover chassis/motor smoke probe schema with run/schema ids | `2.2.2` |
| `vehicle_axle_wheel_map.csv/json` | `vehicle.axle_wheel_map.v1` | `fallback_vehicle_schema_only_pychrono_unavailable` | no | axle/side/wheel-location ids, tire/brake ids, driven/steerable flags | `2.2.2` |
| `vehicle_frame_hardpoint_map.csv/json` | `vehicle.frame_hardpoint_map.v1` | `fallback_vehicle_schema_only_pychrono_unavailable` | no | ISO vehicle frame, hardpoint transforms, world/render frame separation | `2.2.2` |
| `vehicle_model_spec_manifest.json` | `vehicle.model_spec_manifest.v1` | `fallback_vehicle_schema_only_pychrono_unavailable` | no | top-level/nested Vehicle JSON contract, path base, source-to-Chrono map, unit/axis policy | `2.2.2` |
| `vehicle_component_list.json` / subsystem policy files | `vehicle.component_list.v1` and related | `fallback_vehicle_schema_only_pychrono_unavailable` | no | schema-only Chrono::Vehicle upgrade contract and output policy | `2.2.2` |
| `vehicle_subsystem_probe.csv` | `vehicle.subsystem_probe.v1` | `fallback_vehicle_schema_only_pychrono_unavailable` | no | wide-form driver/powertrain/driveline/brake/tire/suspension schema wiring | `2.2.2` |
| `environment_terrain_height_friction_sinkage.csv` / terrain graphs | `terrain.surface_probe.v1` | `fallback_pychrono_unavailable` | no | terrain query/schema, normal/friction/sinkage fields, graph interpretation | `2.2.3` |
| `terrain_surface_probe.csv` | `terrain.surface_probe.v1` | `fallback_pychrono_unavailable` | no | canonical surface probe alias for terrain query consumers | `2.2.3` |
| `terrain_query_probe.csv` | `terrain.query_probe.v1` | `fallback_pychrono_unavailable` | no | query frame, consumer family, functor ids, tire validity and contact-solver separation | `2.2.3` |
| `environment_terrain_contact_probe.csv` / force graph | `terrain.contact_probe.v1` | `fallback_pychrono_unavailable` | no | terrain contact force schema, source, contact patch fields | `2.2.3` |
| `terrain_component_manifest.json` | `terrain.component_manifest.v1` | `fallback_pychrono_unavailable` | no | terrain component ids, query/contact authority, sync/advance policy | `2.2.3` |
| terrain patch/material/deformable manifests | `terrain.patch_manifest.v1` and related | `fallback_terrain_schema_only_pychrono_unavailable` | no | patch bounds/materials, material region map, SCM/DEM/FEA/CRM domain slots, SCM soil profile | `2.2.3` |
| `collision_contact_probe.csv` / contact graphs | `collision.contact_probe.v1` | `deterministic_contact_probe_pychrono_unavailable` | no | reporter schema, frame/sign/force-torque placeholder fields, event thresholds | `2.2.4` |
| `collision_event_timeline.csv` / event timeline graph | `collision.event_timeline.v1` | `deterministic_contact_probe_pychrono_unavailable` | no | first/peak/end contact event schema with source and threshold metadata | `2.2.4` |
| collision system/shape/material/callback manifests | `collision.*.v1` | `deterministic_contact_probe_pychrono_unavailable` | no | backend, shape, material, family filter, container, callback, debug-frame contracts derived from contact probe | `2.2.4` |
| `data_visualization_state_log.csv` / trajectory graph | `data.state_log.v1` | `fallback_pychrono_unavailable` | no | state logger and graph manifest schema | `2.2.5` |
| `data_visualization_control_log.csv` / control graph | `data.control_log.v1` | `fallback_pychrono_unavailable` | no | control logger schema and input graph | `2.2.5` |
| `sensor_manifest.csv/json` | `sensor.output_manifest.v1` | `fallback_sensor_schema_only_pychrono_unavailable` | no | sensor name/type, parent/world pose, timing, filter chain, artifact path/checksum, dropped-frame policy | `2.2.5` |
| `sensor_timing_schedule.csv/json` | `sensor.timing_schedule.v1` | `fallback_sensor_schema_only_pychrono_unavailable` | no | update rate, requested/ready time, collection window, engine/device id, stale/dropped frame fields | `2.2.5` |
| `sensor_filter_catalog.csv/json` | `sensor.filter_catalog.v1` | `fallback_sensor_schema_only_pychrono_unavailable` | no | filter class/order, role, buffer conversion/access/save policy, CPU copy and failure behavior | `2.2.5` |
| `sensor_scene_manifest.json` | `sensor.scene_manifest.v1` | `fallback_sensor_schema_only_pychrono_unavailable` | no | Sensor module gate, device/engine scene policy, visual asset coverage, compatible-domain fallback | `2.2.5` |
| `sensor_module_capability_manifest.json` | `sensor.module_capability_manifest.v1` | `fallback_sensor_schema_only_pychrono_sensor_unavailable` | no | host/candidate build import checks for `pychrono`, `pychrono.sensor`, and `pychrono.vsg3d`; live sensor output blocker | `2.2.5` |
| `artifact_manifest.csv/json` | `component.artifact_manifest.v1` | generated bundle metadata | no | producer/input/output hash, evidence level, schema/source row count | `2.2.5` |
| `run_metadata.json` | `component.run_metadata.v1` | generated bundle metadata | no | artifact counts, CSV/JSON schema ids, source values, fallback policy, live/VSG evidence flags | `2.2.5` |
| `render_manifest.csv/json` / `visual_asset_manifest.csv/json` | `visual.render_manifest.v1`, `visual.asset_manifest.v1` | generated bundle metadata plus VSG capture rows | mixed | render backend, image dimensions/hash, camera fields where available, visible component ids, visual asset owner, VSG capture evidence level | `2.2.5` |

### Required Artifact Gap Register

The current report intentionally separates generated fallback artifacts from artifacts that are required for a live, replayable System-stage run. Some metadata bundle files are now generated for the current report artifacts; live System-stage evidence still has to replace fallback sources and add runtime-specific Chrono fields.

| Required artifact | Owner component | Why it matters | Current status |
|---|---|---|---|
| `run_metadata.json` | `data.run_metadata` / Runtime Config | binds Chrono version, modules, dt, solver, terrain, body registry, seed, fallback policy | generated as `outputs/json/run_metadata.json` for current fallback bundle; live System run must add Chrono build/module/runtime fields |
| `logger_timebase_manifest.csv/json` | `data.timebase_scheduler` | aligns state/control/contact/terrain/sensor rows by clock source, step index, sampling period, resampling policy, dropped row reason | generated from current CSV headers/time columns |
| `artifact_manifest.csv/json` | Metadata Logger | links every CSV/PNG/raw file to producer, input hash, output hash, evidence level | generated as `outputs/csv/artifact_manifest.csv` and `outputs/json/artifact_manifest.json` for current CSV/PNG/raw artifacts |
| `vehicle_model_spec_manifest.json` | `vehicle.model_spec` | records top-level vehicle JSON/template, nested chassis/suspension/steering/wheel/tire/brake/driveline files, asset base path, source/resolved hashes, and source-to-Chrono name map | generated as schema-only fallback JSON |
| `vehicle_frame_hardpoint_map.csv/json` | `vehicle.frame_hardpoints` | records ISO vehicle frame, subsystem frame ids, parent transforms, hardpoint names, local xyz/axis vectors, axle/side/location ids, and world transform checks | generated as schema-only fallback CSV/JSON |
| `vehicle_axle_wheel_map.csv/json` | `vehicle.axle` / `vehicle.wheel` | records Chrono axle indexing, side, wheel location (`single/inner/outer`), wheel/tire/brake ids, driven/steerable/dual flags | generated as schema-only fallback CSV/JSON |
| `vehicle_component_list.json` | `vehicle.system_export` | stores `ExportComponentList`-style component inventory with Chrono class, subsystem type, body/link ids, owner component id, and source JSON | generated as schema-only fallback JSON |
| `vehicle_subsystem_types.txt/json` | `vehicle.system_export` | stores `LogSubsystemTypes`-style template names for chassis, subchassis, axle, suspension, steering, tire, powertrain, driveline, brake, and tracked subsystems | generated as `vehicle_subsystem_types.json`; live text log still requires Chrono::Vehicle run |
| `vehicle_subsystem_output_policy.json` | `vehicle.system_export` | records output enable flags for chassis, subchassis, suspension, steering, anti-roll bar, driveline, brakes, tires, and tracked components | generated as schema-only fallback JSON |
| `vehicle_subsystem_probe.csv` | `vehicle.system_export` / `vehicle.axle` / `vehicle.tire_model` | stores live or schema-only subsystem state/force/torque rows using dynamic axle/side/wheel-location columns and explicit `source` value | generated as schema-only fallback CSV; live `source=pychrono_vehicle` still required for validation |
| `terrain_component_manifest.json` | `terrain.interface` | records terrain type, Chrono class, module availability, query/contact authority, sync/advance order, source/fallback policy | generated as `outputs/json/terrain_component_manifest.json`, including rigid/query components plus CRG/SCM/Granular/FEA/CRM catalog slots |
| `terrain_query_probe.csv` | `terrain.query_contract` | records `query_frame`, consumer family, height/normal/friction functor ids, placeholder policy, `valid_for_semi_empirical_tires`, and sampled query values | generated as canonical fallback CSV with schema `terrain.query_probe.v1` |
| `terrain_patch_manifest.csv/json` | `terrain.rigid_patch` / `terrain.heightmap_mesh` / `terrain.crg` | records patch id, BOX/MESH/HEIGHT_MAP/CRG source, pose, bounds, texture, material id, source path/hash, height scale, origin frame | generated as catalog/fallback manifest |
| `terrain_material_region_map.csv/json` | `terrain.material_region` | separates `terrain_mu_query`, `contact_material_mu`, spatial region bounds, material class, friction functor, and calibration/provenance | generated as catalog/fallback manifest |
| `terrain_surface_probe.csv` | `terrain.interface` | records height, normal, friction query, source, terrain id/type, and coordinate frame for tire/controller consumers | generated as canonical fallback alias with schema `terrain.surface_probe.v1`; live module-backed source still required for validation |
| `terrain_deformable_domain_manifest.json` | `terrain.scm` / `terrain.granular_dem` / `terrain.fea` / `terrain.crm` | records grid/particle/mesh/SPH spacing, active domain, moving patch, backend identity, timestep, and coupling order | generated as catalog/fallback manifest |
| `scm_soil_profile_manifest.csv/json` | `terrain.scm` | records Bekker/Mohr-Coulomb/Janosi parameters, elastic/plastic stiffness/damping, soil callback id, profile source, calibration provenance | generated as catalog/fallback manifest |
| `scm_node_evidence.csv/json` | `terrain.scm` | records SCM node sinkage, elastic/plastic sinkage, pressure/shear fields, touched/island plot type, moving patch policy | schema/catalog only |
| `scm_modified_nodes.csv` | `terrain.scm` | stores touched/modified SCM nodes, node coordinates, level, pressure, sinkage, shear, island id, and plot field | schema/catalog only |
| `granular_particle_domain_manifest.json` | `terrain.granular_dem` | records particle radius/density/count, domain, backend/device, moving patch, settling checkpoint, contact method, dt | schema/catalog only |
| `granular_domain_manifest.json` | `terrain.granular_dem` | alias/compact manifest for particle bed dimensions, particle count/radius/density, backend identity, moving patch, dt, and checkpoint hash | schema/catalog only |
| `fea_terrain_manifest.json` | `terrain.fea` | records terrain mesh id, element type/count, material law, boundary condition, solver settings, deformation/stress artifact path | schema/catalog only |
| `fea_terrain_mesh_manifest.json` | `terrain.fea` | records mesh source/hash, node/element count, element family, boundary condition map, material law id | schema/catalog only |
| `fea_terrain_stress_strain.csv` | `terrain.fea` | stores stress/strain/deformation evidence proving live FEA terrain response rather than mesh-only render | not generated without live FEA run |
| `crm_fsi_domain_manifest.json` | `terrain.crm` | records SPH spacing, BCE/marker files, rheology, active domain, MBD/CFD timestep, rigid/FEA body coupling registration | schema/catalog only |
| `crm_sph_domain_manifest.json` | `terrain.crm` | records SPH particle spacing, BCE file hashes, fluid/soil material law, active domain, coupled body ids | schema/catalog only |
| `crm_coupling_step_log.csv` | `terrain.crm` | timestamped MBD/FSI advance order, coupling timestep, active domain update, and exchanged force/state fields | not generated without live CRM/FSI run |
| `collision_system_manifest.json` | `collision.system_lifecycle` | records collision system type, bind/init/run/report sequence, backend availability, thread count, envelope/margin, timers, callback registration, fallback reason | generated as schema-only fallback JSON |
| `collision_backend_comparison.csv/json` | `collision.system_lifecycle` | records backend type, Chrono version, module availability, thread count, envelope/margin, broad/narrow timers, total/filtered contact count, source/fallback | generated as schema-only fallback CSV/JSON |
| `collision_shape_manifest.csv/json` | `collision.shape_manifest` | records `ChCollisionShape::Type`, concrete shape class, owner contactable id, local REF-frame pose, material id, mutable/parent shape, mesh path/hash, bounding box, thin-shape risk | generated as schema-only fallback CSV/JSON |
| `collision_model_registry.json` | `collision.model_registry` | maps body/contactable ids to collision models, enable flags, shape counts, material sharing policy, visual-shape link, and debug render | generated as schema-only fallback JSON |
| `collision_family_filter_map.csv/json` | `collision.family_filter` | records family ids 0..15, names, `SetFamily`/allow/disallow calls, resolved mask, included/excluded pairs, reporter scope, debug artifact | generated as schema-only fallback CSV/JSON |
| `contact_material_manifest.csv/json` | `collision.material_surface` | records NSC/SMC material ids, common friction/restitution fields, method-specific compliance/stiffness/damping/adhesion fields, calibration/provenance | generated as schema-only fallback CSV/JSON |
| `contact_pair_material_policy.csv/json` | `collision.material_pair_policy` | records pair material ids, composite material class, mixing/override rule, `AddContactCallback` class, modified fields, contactinfo filter, evidence graph | generated as schema-only fallback CSV/JSON |
| `contact_container_manifest.csv/json` | `contact.container_reporter` | records contact container class, callback class, pair filter, frame conversion, reset policy, unsupported contactable types | generated as schema-only fallback CSV/JSON |
| `contact_force_torque_probe.csv` | `contact.force_torque` | records pA/pB points, normal/tangent/contact frame, effective radius, constraint offset, contact-frame force/torque, world-frame resultant, pair order, force-on target, `ComputeContactForces` cache status | covered inline by generated `outputs/csv/collision_contact_probe.csv`; standalone comparison file remains schema/catalog only |
| `contact_frame_debug_manifest.csv/json` | `contact.debug_visual` | links contact points, normal/tangent basis, force/torque vectors, visual-vs-collision render, backend visualization support, and fallback reason | generated as schema-only fallback CSV/JSON |
| `contact_callback_manifest.csv/json` | `collision.callback_policy` | records Broadphase/Narrowphase/AddContact/ReportContact/Visualization callbacks, phase, hook, input object, mutation/report-only policy, artifact, fallback behavior | generated as schema-only fallback CSV/JSON |
| `writer_backend_manifest.csv/json` | `data.io_writer` | records Python CSV, `ChWriterCSV`, `ChOutputASCII/HDF5`, or `ChGnuPlot` backend, output mode, schema id, row/frame count, path/hash | generated for current CSV/JSON artifacts |
| `chrono_output_database_manifest.json` | `data.chrono_output_db` | records `ChOutput` type/mode, ASCII/HDF5 path, section names, frame/series ids, component scope, row count, schema map, failure mode | generated as catalog/fallback manifest |
| `checkpoint_manifest.csv/json` | `data.checkpoint_restart` | records checkpoint scope, path/hash, body count, collision shape count, restart validity, restore assumptions, not-for-validation warning | generated as catalog/fallback manifest |
| graph/render manifests | Graph Generator / Render Screenshot | prevents stale CSV graphs and untraceable screenshots | generated as `render_manifest.csv/json` plus graph rows in `artifact_manifest.csv/json`; live camera pose still must be extended for System runs |
| `gnuplot_plot_manifest.csv/json` | `postprocess.gnuplot_backend` | records `.gpl` script/hash, input `.dat` hash, terminal/output format, GNUplot executable availability, silent no-output failure | generated as catalog/fallback manifest with raw `.dat/.gpl` inputs |
| `visual_asset_manifest.csv/json` | `visual.asset_manifest` | maps visual models/shapes/materials to owner physics items, local frame, REF/COG convention, mesh/texture hashes, runtime/sensor visibility | generated for current render/VSG assets at `outputs/csv/visual_asset_manifest.csv` and `outputs/json/visual_asset_manifest.json`; live ChVisualShape local frames still required for System runs |
| `sensor_module_capability_manifest.json` | `sensor.manager` | records host/candidate build availability for `pychrono.sensor` and whether live frame/cloud/log output is allowed | generated as module gate evidence; current local candidate build has VSG but no `pychrono.sensor` |
| `sensor_manifest.csv/json` | `sensor.output_writer` | ties frames/clouds/logs to sensor pose, filter chain, timing, checksums, dropped frames | generated as schema-only fallback CSV/JSON; raw frame/cloud/log artifacts still require live Sensor module |
| `sensor_scene_manifest.json` | `sensor.scene_reconstruction` | records Sensor module compatibility, GPU/device list, scene lights/background, ray recursion, visual asset coverage, compatible domain, fallback policy | generated as schema-only fallback JSON |
| `sensor_timing_schedule.csv/json` | `sensor.timing_schedule` | records dynamics dt, sensor update rate, lag/window, requested/ready time, engine/device id, dropped/stale frame reason | generated as schema-only fallback CSV/JSON |
| `sensor_filter_catalog.csv/json` | `sensor.filter_catalog` | records filter class, role, input/output buffer type, save/access/convert/noise/visualize behavior, CPU copy requirement, failure behavior | generated as schema-only fallback CSV/JSON |
| raw sensor folders | Sensor Output Writer | stores camera/depth/segmentation/LiDAR/GPS/IMU/radar/tachometer outputs from module-backed runs | not generated without live Sensor module |
| `offline_visual_export_manifest.csv/json` | `visual.offline_export` | records `WriteVisualizationAssets` frame CSV, mesh paths/hashes, renderer script, frame index/time, rendered image hash | generated as catalog/fallback manifest over current render/VSG assets |
| `fea_mesh_manifest.csv/json` | `flex.mesh` | records mesh id/path/hash, node count, element count, frame, visualization/contact surface ids | generated as catalog/fallback manifest |
| node/element count table | `flex.mesh` | records the intended mesh cardinality contract; live proof still requires a solved mesh hash plus deformation/stress or modal evidence | generated as `fea_node_element_count.csv` catalog/fallback table |
| `material_law_manifest.json` | `flex.material_section` | records density, elastic/plastic law, section area/inertia/thickness/layers, damping | generated as catalog/fallback manifest |
| `boundary_condition_map.csv/json` | `flex.boundary_attachment` | maps boundary nodes to fixed constraints, body attachments, links, loads, and frames | generated as catalog/fallback manifest |
| stress/strain/deformation output | `flex.mesh` / `flex.material_section` | distinguishes live FEA evidence from a mesh screenshot | not generated without live FEA run |
| `mode_frequency_table.csv` | `flex.modal_reduction` | records modal frequencies, mode ids, damping, reduction validity | generated as catalog/fallback manifest |
| `modal_basis_manifest.json` | `flex.modal_reduction` | records source model hash, reduction method, basis/eigenvector hash, boundary/internal split | generated as catalog/fallback manifest |
| `model_import_manifest.json` | `model.spec_resolver` / `model.urdf_import` | records JSON/YAML/URDF source hash, raw/resolved paths, source-to-Chrono name map, unit/axis transform, missing fields | generated as catalog/fallback manifest |
| `asset_manifest.csv/json` | `model.spec_resolver` / `asset.cad_step` | records every config/mesh/texture/STEP/FMU asset role, owner component, path base, hash, fallback behavior | generated as catalog/fallback manifest |
| `cad_shape_manifest.csv/json` | `asset.cad_step` | records named STEP shape hierarchy, tessellation settings, mass/inertia source, collision proxy policy | generated as catalog/fallback manifest |
| `external_interface_map.csv/json` | external integration components | maps external source entities, variables, topics, nodes, frames, units, and directions to Chrono Component fields | generated as catalog/fallback manifest |
| `sync_contract.json` | external integration components | records time source, Chrono/external dt, exchange order, hold/lag policy, timeout, drop/retry policy | generated as catalog/fallback manifest |
| `sync_exchange_log.csv` | `integration.fmi` / `integration.ros` / `integration.vehicle_cosim` / `integration.synchrono` | timestamped proof that external data exchanged with Chrono at the expected rate/order | generated as schema-only exchange fixture; live integration still required for validation |
| `fmu_variable_map.csv/json` | `integration.fmi` | records FMU variables, causality, units, FMI version, step size, Chrono field map | generated as catalog/fallback manifest |
| `ros_topic_handler_manifest.csv/json` | `integration.ros` | records topics, handlers, message types, pub/sub direction, frame transforms, update rates | generated as catalog/fallback manifest |
| `vehicle_cosim_node_manifest.json` | `integration.vehicle_cosim` | records MBS/tire/terrain node roles, rank/process ids, exchanged variables, sync timestep | generated as catalog/fallback manifest |
| `synchrono_agent_manifest.json` | `integration.synchrono` | records agent id, communication backend, synchronization period, world/GPS frame, packet timing | generated as catalog/fallback manifest |

## 2.1 vs 2.2 Boundary Checklist

| API / command concern | 2.2 Component concern | Required ownership field | Required validation artifact | Link back to 2.1 when |
|---|---|---|---|---|
| How to instantiate a class | What physical/data responsibility the class implements | `component_id`, `owns`, `depends_on` | render/graph/CSV tied to component | syntax/import/argument order is the main topic |
| `ChBodyEasyBox(...)` call | chassis, ground, obstacle, payload, or collision envelope contract | mass, pose, visual/collision refs, material id | body render, state/contact probe | explaining primitive constructor behavior |
| `RigidTerrain.AddPatch(...)` call | terrain patch identity and query/contact authority | patch id, frame, material, height source | terrain render, height/friction probe | listing patch overloads |
| `ReportAllContacts(...)` call | reporter scope, frame conversion, aggregation, schema | body pair, filter rule, force source, frame | contact CSV, debug vectors | callback signature details dominate |
| `PushFilter(...)` call | sensor filter chain output contract | filter chain id, input/output buffer, save/access policy | sensor manifest, raw artifact | enumerating filter API syntax |
| `ChSensorManager.Update()` call | sensor lifecycle/scheduling contract | manager id, sensor list, update order, dropped/late frame policy | sensor manifest, raw frame/cloud/log | loop syntax or one demo call is the goal |
| `WriteVisualizationAssets(...)` call | offline visualization artifact contract | output directory, frame index, exporter/backend, visible component ids | render/offline manifest | exporter API options dominate |
| `ChWriterCSV` / `ChOutputHDF5` call | data artifact writer contract | schema id, units, path/hash, source/evidence level | CSV/HDF5 manifest | writer method syntax is the goal |
| YAML parser / `run_chrono` call | resolved model/solver/output spec contract | raw YAML hash, resolved config, Component id map, output policy | resolved import manifest | runner options or parser syntax dominate |
| `ChCascadeDoc.LoadSTEP(...)` call | CAD import and asset resolver contract | named-shape hierarchy, tessellation settings, mass/inertia policy, collision proxy map | CAD import manifest, visual/collision evidence | STEP loading syntax is the goal |
| FMU import/export helper call | FMI adapter contract | FMU hash, variable map, causality, FMI version, co-sim step order | synchronized FMU log | FMU packaging API is the goal |
| ROS handler construction | ROS bridge contract | topic/message type, handler list, pub/sub direction, update rate, frame transform | ROS topic/handler manifest | ROS class constructor syntax dominates |
| Vehicle co-simulation node startup | distributed vehicle-terrain co-sim contract | MBS/tire/terrain node role, rank/process id, exchanged variables, sync timestep | node manifest, force/state exchange log | MPI launch mechanics dominate |
| SynChrono agent launch | distributed multi-agent synchronization contract | agent id, communication backend, sync period, world/GPS frame, packet timing | agent sync manifest | demo launch syntax dominates |
| `matplotlib.plot(...)` call | graph artifact provenance and interpretation | input CSV/hash, axis units, producer script | graph PNG + manifest fields | generic plotting mechanics are the goal |

## 공식 Chrono 모듈 대응

이 보고서는 Chrono API 호출 목록이 아니라 개발자가 조립할 Component 카탈로그이다. 따라서 공식 모듈은 빌드/기능 경계로 보고, 본문에서는 실제 모델링 부품 단위로 다시 묶는다.

| 공식 영역 | Component 카탈로그에서 보는 단위 | 주요 문서 |
|---|---|---|
| Core dynamics | `ChSystem`, solver/timestepper, `ChBody`, `ChLink`, `ChMotor`, visual/collision shape를 묶은 physics system, rigid body, joint, actuator, chassis, wheel, obstacle | `2.2.1`, `2.2.2`, `2.2.4` |
| Chrono::Vehicle | chassis, suspension, steering, tire, powertrain, driveline, brake, terrain subsystem | `2.2.2`, `2.2.3` |
| Chrono::Robot | Curiosity, Viper, Turtlebot 같은 완성 로버/로봇 모델 | `2.2.2` |
| Contact/Collision | contact material, collision shape, reporter, event detector, force logger | `2.2.4` |
| Sensor | sensor manager, camera/depth/segmentation, LiDAR, GPS, IMU, radar, tachometer, filter/output writer | `2.2.5` |
| Visualization/Postprocess | VSG/Irrlicht render, screenshot, CSV, graph, metadata | `2.2.5` |
| Runtime/Config | timestep, solver/contact method, gravity, module availability, seed, resolved config, metadata ownership | `2.2.1` cross-cutting component |

공식 API 기준은 Project Chrono API 문서(https://api.projectchrono.org/), Vehicle terrain 문서(https://api.projectchrono.org/group__vehicle__terrain.html), Sensor overview(https://api.projectchrono.org/sensor_overview.html)를 기준으로 삼는다.

### Official Chrono Module Coverage Matrix

| Official module/component | Catalog component id | Owner doc | Status | Availability key | Validation artifact |
|---|---|---|---|---|---|
| Core Chrono | `runtime.system`, `core.body`, `core.link_constraint`, `core.motor_constraint`, `core.motor_torque` | `2.2.1` | covered core | `core=true` | `core_physics_solver_constraint_catalog.png` |
| Vehicle | `vehicle.*`, `terrain.interface`, `terrain.rigid_patch`, `terrain.scm` | `2.2.2`, `2.2.3` | covered/extension | `vehicle=true` | rover/terrain catalog renders plus HMMWV/M113 VSG visual asset captures |
| Robot | `vehicle.robot_assets` | `2.2.2` | covered as built-in asset index | `robot_assets=true` | Viper/Curiosity VSG visual asset captures |
| Sensor layout | `sensor.layout` | `2.2.5` | concept/layout covered | `sensor=true/false` | `data_visualization_sensor_components.png` |
| Sensor module output | `sensor.manager`, `sensor.filter_chain`, `sensor.output_writer` | `2.2.5` | future/live artifact required; current local build records `pychrono.sensor` unavailable | `sensor=true`, VSG/OptiX availability | `data_visualization_sensor_pipeline_catalog.png`, sensor capability/manifest files, frames/clouds/logs, dropped-frame metadata |
| VSG / Irrlicht / Postprocess | `visual.runtime`, `visual.offline_export`, `postprocess.plot_export` | `2.2.5` | covered for render/artifact contract | `vsg`, `irrlicht`, `postprocess` | render/screenshot/plot manifests |
| Parsers / YAML / URDF / Cascade | `model.spec_resolver`, `model.urdf_import`, `asset.cad_step` | `2.2.1` | indexed extension | `parsers`, `yaml`, `urdf`, `cascade` | import/asset manifests, `external_integration_component_map.png` |
| FMI / ROS / VehicleCosim / Synchrono | `integration.fmi`, `integration.ros`, `integration.vehicle_cosim`, `integration.synchrono` | `2.2.1` | indexed extension | `fmi`, `ros`, `vehicle_cosim`, `synchrono` | interface maps, sync logs, `external_integration_component_map.png` |
| FSI / DEM / FEA / Modal / Multicore | advanced terrain/contact/runtime extensions | `2.2.1`, `2.2.3`, `2.2.4` | extension/fallback unless module is available | module-specific availability key | `chrono_module_coverage_map.png`, terrain advanced catalog |

| Chrono module coverage |
|---|
| ![Chrono module coverage map](images/renders/chrono_module_coverage_map.png) |

| Chrono optional module dependency ladder |
|---|
| ![Chrono optional module dependency ladder](images/renders/chrono_optional_module_dependency_ladder.png) |

### Requestable Chrono Component Lookup

This table is a developer lookup for Chrono components/modules that can appear in build or `find_package` configuration. `Covered` means there is a first-class 2.2 card. `Indexed` means the report records the dependency, interface, and fallback requirements, but does not claim module-backed evidence without matching artifacts.

| Chrono component | Catalog owner | Component-card status | Availability key | Evidence level | Not-in-scope / fallback rule |
|---|---|---|---|---|---|
| `Vehicle` | `2.2.2`, `2.2.3` | covered | `vehicle` | rover/terrain renders plus HMMWV/M113 VSG visual asset captures; current dynamics CSV fallback unless live Vehicle probe exists | require `vehicle_model`, tire/terrain ids for live validation |
| `VehicleCosim` | `2.2.1`, `2.2.2`, `2.2.3` | indexed extension | `vehicle_cosim` | interface metadata only until live exchange log exists | require MBS/tire/terrain node manifest, BODY/MESH interface, sync timestep, state/force exchange log |
| `Robot` | `2.2.2` | covered as model catalog | `robot` | Viper/Curiosity VSG visual asset captures | live robot run needs robot model, wheel ids, driver source |
| `Sensor` | `2.2.5` | layout covered, module output future | `sensor` | layout/schema evidence only now; `sensor_module_capability_manifest.json` records current `pychrono.sensor` unavailability | require sensor manifest and raw frames/clouds/logs from a Sensor-enabled run |
| `VSG`, `Irrlicht` | `2.2.5` | covered render backend | `vsg`, `irrlicht` | render/screenshot manifest | record backend and camera/view policy |
| `Postprocess` | `2.2.5` | indexed extension | `postprocess` | export path metadata | POV-Ray/GNUplot outputs are not current evidence |
| `Parsers`, `YAML`, `URDF` | `2.2.1` | indexed config/import | `parsers`, `yaml`, `urdf` | parsed import manifest only | import validation requires raw path, hash, unit/axis conversion, source-to-Chrono map; not dynamics validation |
| `Cascade` / STEP | `2.2.1` | indexed asset import | `cascade` | CAD import manifest only | require named-shape hierarchy, tessellation, mass/inertia, visual-vs-collision policy before validation |
| `FMI` / FMU | `2.2.1`, `2.2.5` | indexed integration | `fmi` | interface metadata until live exchange log exists | require FMU hash, variable map, causality, co-sim step, timestamped exchange log |
| `ROS` | `2.2.1`, `2.2.5` | indexed I/O bridge | `ros` | topic/handler manifest until live log exists | require `/clock`, topic handlers, message types, frame transforms, latency/drop metadata |
| `Synchrono` | `2.2.1` | record-only extension | `synchrono` | availability/agent metadata until live sync log exists | require agent manifests and heartbeat exchange logs; does not imply contact-force coupling |
| `DEM` / `Granular` / `GPU` | `2.2.3` | indexed advanced terrain | `dem`, `granular`, `gpu` | terrain advanced catalog | require particle domain/timestep and live module source |
| `FSI`, `FSI_SPH`, `FSI_TDPF`, `CRM` | `2.2.3` | indexed advanced terrain | `fsi`, `fsi_sph`, `fsi_tdpf`, `crm` | terrain advanced catalog | require coupling timestep, spacing, active domain |
| `FEA`, `Modal` | `2.2.1`, `2.2.2`, `2.2.3` | indexed flexible upgrade | `fea`, `modal` | flexible/tire/terrain metadata | require mesh/basis/material law artifact |
| `Multicore` | `2.2.1`, `2.2.4` | runtime metadata | `multicore` | module/back-end metadata | require thread count and collision backend comparison |
| `MUMPS`, `PardisoMKL` | `2.2.1` | solver backend index | `mumps`, `pardisomkl` | solver metadata only | require direct-solver availability and convergence log |
| `CSharp`, `Matlab` | README / `2.2.1` | record-only binding/interface | `csharp`, `matlab` | availability metadata | outside current Python report unless adapter used |

| Core physics solver/constraint catalog |
|---|
| ![Core physics solver constraint catalog](images/renders/core_physics_solver_constraint_catalog.png) |

### 고급/외부 의존 Component 범위

아래 항목은 공식 Chrono 기능 경계에는 존재하지만, 이 2.2 카탈로그에서는 기본 rover-terrain-contact-data 흐름의 확장 Component로 둔다. 본문에서 직접 다루지 않는 경우에도 run metadata에는 module availability와 fallback 정책을 남긴다.

| 고급 영역 | Component 관점 | 이번 2.2에서의 취급 |
|---|---|---|
| Vehicle Co-simulation | MBS node, Tire node, Terrain node, BODY/MESH interface, sync timestep | Vehicle/Terrain 확장 Component로 색인 |
| ROS Bridge | topic, handler, update rate, `/clock`, external driver/sensor I/O | Data/Control/Sensor I/O 확장으로 색인 |
| FMI/FMU | FMU file, FMI 2/3, model exchange/co-simulation, variable map | Runtime/Control 외부 동역학 Component로 색인 |
| FSI/CRM/SPH | fluid/soil continuum domain, BCE/particle spacing, coupling timestep | Advanced Terrain 확장으로 색인 |
| DEM/Granular | particle terrain/contact domain, particle material, active box | Advanced Terrain 확장으로 색인 |
| FEA/FEA tire | mesh, element/material law, tire/terrain coupling | Tire/Terrain upgrade path로 색인 |
| Modal | modal basis, reduction type, boundary nodes, mode-shape validation | FEA/flexible structure upgrade path로 색인 |
| Parsers/URDF/YAML/CAD | model spec, asset path, unit/axis transform, collision mesh policy | Run Config / Model Spec / Asset Import Component로 색인 |
| Multicore/parallel collision | collision backend, thread count, solver/backend metadata | Collision Backend / Runtime metadata로 색인 |
| Blender/POV-Ray/GNUplot | offline render/export, plot backend, postprocess script | Visualization/Postprocess 확장으로 색인 |

## 산출물 구조

| 폴더 | 역할 |
| --- | --- |
| [code/](code/) | Component 예시 코드와 이미지/그래프 생성 스크립트 |
| [code/common/](code/common/) | 공통 유틸리티, 전체 실행 스크립트, VSG/Irrlicht 관련 보조 코드 |
| [images/renders/](images/renders/) | Component별 렌더링 이미지 |
| [images/graphs/](images/graphs/) | CSV 또는 예시 데이터 기반 그래프 |
| [images/mermaid_rendered/](images/mermaid_rendered/) | Mermaid 관계도 원본 `.mmd`와 렌더링 이미지 |
| [outputs/csv/](outputs/csv/) | 예시 코드 실행으로 생성된 CSV 데이터 |
| [outputs/raw/](outputs/raw/) | 실행 로그와 실험용 원본 이미지 |

## 대표 시각 자료

| 로버/차량 | 환경/Terrain |
| --- | --- |
| ![로버 Component 개요](images/renders/rover_vehicle_component_overview.png) | ![지형 Component](images/renders/terrain_ground_obstacle_components.png) |

| 충돌/접촉 | 데이터/센서 |
| --- | --- |
| ![충돌 Component](images/renders/collision_contact_components.png) | ![센서 Component](images/renders/data_visualization_sensor_components.png) |

## 코드 실행

전체 Component 예시를 다시 생성하려면 프로젝트 루트에서 Chrono 환경을 활성화한 뒤 다음 스크립트를 실행한다. 이 entry point는 영역별 CSV/aggregate 생성기, 아래 이미지 표에 등록된 PNG별 개별 생성 스크립트, artifact manifest 생성기를 순서대로 호출한다.

```bash
conda activate chrono
source setup_chrono_env.sh
python "3-layer_report/2.2 Component/code/common/run_all_component_examples.py"
```

개별 영역만 다시 생성할 때는 아래 스크립트를 사용한다.

| 영역 | 실행 스크립트 |
| --- | --- |
| 로버/차량 | `code/rover_vehicle/generate_rover_vehicle_components.py` |
| 환경/Terrain | `code/environment_terrain/generate_environment_terrain_components.py` |
| 충돌/접촉 | `code/collision_contact/generate_collision_contact_components.py` |
| 데이터/시각화 | `code/data_visualization/generate_data_visualization_components.py` |
| Chrono 기본 형상 | `code/common/generate_chrono_default_shapes.py` |
| Chrono 내장 차량/로봇 asset | `code/common/generate_chrono_builtin_component_assets.py` |
| Artifact manifest / run metadata | `code/common/generate_component_artifact_manifest.py` |
| Mermaid 관계도 | `code/common/render_mermaid_01.py` ~ `code/common/render_mermaid_06.py` |

## 이미지 생성 스크립트 규칙

보고서 이미지는 수정 중 롤백을 줄이기 위해 가능하면 PNG 하나당 생성 스크립트 하나를 둔다. 전체 재생성 entry point도 이 표의 개별 스크립트를 호출하므로, 보정이 잦은 이미지는 해당 PNG 행의 스크립트만 다시 실행하면 된다.

| 이미지 | 개별 생성 스크립트 |
|---|---|
| `images/mermaid_rendered/2_2_mermaid_01.png` | `code/common/render_mermaid_01.py` |
| `images/mermaid_rendered/2_2_mermaid_02.png` | `code/common/render_mermaid_02.py` |
| `images/mermaid_rendered/2_2_mermaid_03.png` | `code/common/render_mermaid_03.py` |
| `images/mermaid_rendered/2_2_mermaid_04.png` | `code/common/render_mermaid_04.py` |
| `images/mermaid_rendered/2_2_mermaid_05.png` | `code/common/render_mermaid_05.py` |
| `images/mermaid_rendered/2_2_mermaid_06.png` | `code/common/render_mermaid_06.py` |
| `images/renders/runtime_config_component_map.png` | `code/common/generate_runtime_config_component_map_render.py` |
| `images/renders/core_physics_solver_constraint_catalog.png` | `code/common/generate_core_physics_solver_constraint_catalog_render.py` |
| `images/renders/flexible_body_fea_modal_component_catalog.png` | `code/common/generate_flexible_body_fea_modal_component_catalog_render.py` |
| `images/renders/chrono_module_coverage_map.png` | `code/common/generate_chrono_module_coverage_map_render.py` |
| `images/renders/chrono_optional_module_dependency_ladder.png` | `code/common/generate_chrono_optional_module_dependency_ladder_render.py` |
| `images/renders/component_catalog_atlas.png` | `code/common/generate_component_catalog_atlas_render.py` |
| `images/renders/external_integration_component_map.png` | `code/common/generate_external_integration_component_map_render.py` |
| `images/renders/chrono_default_shape_types.png` | `code/common/generate_chrono_default_shape_types_render.py` |
| `images/renders/chrono_builtin_wheeled_vehicle_assets.png` | `code/common/generate_chrono_builtin_wheeled_vehicle_assets_render.py` |
| `images/renders/chrono_builtin_tracked_vehicle_assets.png` | `code/common/generate_chrono_builtin_tracked_vehicle_assets_render.py` |
| `images/renders/chrono_builtin_robot_rover_assets.png` | `code/common/generate_chrono_builtin_robot_rover_assets_render.py` |
| `images/renders/chrono_viper_vsg_capture.png` | `code/common/generate_chrono_builtin_robot_rover_assets_render.py` |
| `images/renders/chrono_curiosity_vsg_capture.png` | `code/common/generate_chrono_builtin_robot_rover_assets_render.py` |
| `images/renders/rover_vehicle_component_overview.png` | `code/rover_vehicle/generate_rover_vehicle_component_overview_render.py` |
| `images/renders/rover_vehicle_subsystem_ownership_map.png` | `code/rover_vehicle/generate_rover_vehicle_subsystem_ownership_map_render.py` |
| `images/renders/rover_payload_sensor_mount_component.png` | `code/rover_vehicle/generate_rover_payload_sensor_mount_component_render.py` |
| `images/renders/rover_wheel_tire_component.png` | `code/rover_vehicle/generate_rover_wheel_tire_component_render.py` |
| `images/renders/rover_axle_joint_component.png` | `code/rover_vehicle/generate_rover_axle_joint_component_render.py` |
| `images/renders/rover_motor_drive_component.png` | `code/rover_vehicle/generate_rover_motor_drive_component_render.py` |
| `images/renders/rover_driver_input_controller_component.png` | `code/rover_vehicle/generate_rover_driver_input_controller_component_render.py` |
| `images/renders/rover_powertrain_driveline_brake_tire_flow.png` | `code/rover_vehicle/generate_rover_powertrain_driveline_brake_tire_flow_render.py` |
| `images/renders/rover_steering_component.png` | `code/rover_vehicle/generate_rover_steering_component_render.py` |
| `images/renders/rover_suspension_steering_components.png` | `code/rover_vehicle/generate_rover_suspension_steering_components_render.py` |
| `images/renders/rover_visual_collision_shapes.png` | `code/rover_vehicle/generate_rover_visual_collision_shapes_render.py` |
| `images/renders/rover_initial_state_component.png` | `code/rover_vehicle/generate_rover_initial_state_component_render.py` |
| `images/renders/tracked_vehicle_components.png` | `code/rover_vehicle/generate_tracked_vehicle_components_render.py` |
| `images/graphs/rover_vehicle_chassis_probe_graph.png` | `code/rover_vehicle/generate_rover_vehicle_chassis_probe_graph.py` |
| `images/renders/terrain_ground_obstacle_components.png` | `code/environment_terrain/generate_terrain_ground_obstacle_components_render.py` |
| `images/renders/terrain_rigid_patch_component.png` | `code/environment_terrain/generate_terrain_rigid_patch_component_render.py` |
| `images/renders/terrain_contact_material_regions.png` | `code/environment_terrain/generate_terrain_contact_material_regions_render.py` |
| `images/renders/terrain_heightmap_component.png` | `code/environment_terrain/generate_terrain_heightmap_component_render.py` |
| `images/renders/terrain_scm_deformation_component.png` | `code/environment_terrain/generate_terrain_scm_deformation_component_render.py` |
| `images/renders/terrain_environment_field_component.png` | `code/environment_terrain/generate_terrain_environment_field_component_render.py` |
| `images/renders/terrain_advanced_selection_catalog.png` | `code/environment_terrain/generate_terrain_advanced_selection_catalog_render.py` |
| `images/graphs/terrain_height_sinkage_profile.png` | `code/environment_terrain/generate_terrain_height_sinkage_profile_graph.py` |
| `images/graphs/terrain_contact_material_friction_map.png` | `code/environment_terrain/generate_terrain_contact_material_friction_map_graph.py` |
| `images/graphs/terrain_contact_force_probe.png` | `code/environment_terrain/generate_terrain_contact_force_probe_graph.py` |
| `images/renders/collision_contact_components.png` | `code/collision_contact/generate_collision_contact_components_render.py` |
| `images/renders/collision_contact_measurement_catalog.png` | `code/collision_contact/generate_collision_contact_measurement_catalog_render.py` |
| `images/renders/collision_visual_vs_collision_shape.png` | `code/collision_contact/generate_collision_visual_vs_collision_shape_render.py` |
| `images/renders/collision_contact_debug_vectors.png` | `code/collision_contact/generate_collision_contact_debug_vectors_render.py` |
| `images/renders/collision_contact_reporter_scope.png` | `code/collision_contact/generate_collision_contact_reporter_scope_render.py` |
| `images/graphs/collision_contact_force_graph.png` | `code/collision_contact/generate_collision_contact_force_graph.py` |
| `images/graphs/collision_contact_count_graph.png` | `code/collision_contact/generate_collision_contact_count_graph.py` |
| `images/graphs/collision_contact_force_components_graph.png` | `code/collision_contact/generate_collision_contact_force_components_graph.py` |
| `images/graphs/collision_contact_material_effect_graph.png` | `code/collision_contact/generate_collision_contact_material_effect_graph.py` |
| `images/graphs/collision_event_timeline_graph.png` | `code/collision_contact/generate_collision_event_timeline_graph.py` |
| `images/renders/data_visualization_artifact_catalog.png` | `code/data_visualization/generate_data_visualization_artifact_catalog_render.py` |
| `images/renders/data_visualization_sensor_pipeline_catalog.png` | `code/data_visualization/generate_data_visualization_sensor_pipeline_catalog_render.py` |
| `images/renders/data_visualization_sensor_components.png` | `code/data_visualization/generate_data_visualization_sensor_components_render.py` |
| `images/graphs/data_visualization_state_trajectory.png` | `code/data_visualization/generate_data_visualization_state_trajectory_graph.py` |
| `images/graphs/data_visualization_control_inputs.png` | `code/data_visualization/generate_data_visualization_control_inputs_graph.py` |

## 문서 작성 기준

각 Component 문서는 같은 흐름을 따른다.

1. Component가 어떤 구현 대상을 표현하는지 설명한다.
2. 관련 Chrono API와 Command 단계의 연결 관계를 정리하되, 먼저 ownership, dependency, parameter contract, outputs, validation, failure mode, upgrade path를 고정한다.
3. 코드 예시로 구현 절차를 보여준다.
4. 렌더 이미지와 그래프를 통해 물리적 의미를 확인한다.
5. CSV/로그 등 데이터 산출물이 있으면 검증 기준과 함께 제시한다.
