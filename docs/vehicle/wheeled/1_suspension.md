# Suspension

> Project Chrono Phase 3 - Vehicle / Wheeled Vehicle  
> 주제: 바퀴 차량의 서스펜션 구조와 Chrono 모델링 방식

---

## 1. 정의

서스펜션(suspension)은 **차체(chassis)와 바퀴(wheel)를 연결하는 기계 시스템**이다.  
차량이 지형 위를 주행할 때 바퀴는 지면 요철에 의해 위아래로 움직이고, 서스펜션은 이 운동을 차체에 전달하거나 완화한다.

즉, 서스펜션은 단순히 충격을 줄이는 장치가 아니라 다음 역할을 동시에 수행한다.

| 역할 | 설명 |
|---|---|
| 하중 지지 | 차량 무게를 바퀴를 통해 지면에 전달 |
| 충격 흡수 | 지면 요철로 인한 급격한 운동 완화 |
| 자세 안정 | roll, pitch, heave 운동 억제 |
| 접지 유지 | 타이어가 지면을 계속 따라가도록 도움 |
| 휠 운동 제어 | camber, toe, track 변화 제어 |

---

## 2. 물리적 의미

차량이 울퉁불퉁한 지형을 지나가면 바퀴에는 수직 방향 변위가 발생한다.  
서스펜션이 없다면 이 변위가 거의 그대로 차체에 전달되어 차량은 크게 튀거나 불안정해진다.

서스펜션은 보통 다음과 같은 동역학 요소로 이해할 수 있다.

```text
차체 질량
   ↑
 spring + damper
   ↓
바퀴 / 지면 입력
```

가장 단순한 모델은 1자유도 질량-스프링-댐퍼 시스템이다.

```text
m x'' + c x' + k x = F
```

여기서:

| 기호 | 의미 |
|---|---|
| m | 차체 또는 unsprung/sprung mass |
| k | 스프링 강성 |
| c | 감쇠계수 |
| x | 변위 |
| F | 외력 또는 지면 입력에 의한 힘 |

Phase 2에서 학습한 TSDA(Translational Spring-Damper Actuator)가 바로 이런 서스펜션 힘을 구성하는 기본 요소로 사용될 수 있다.

---

## 3. 실제 차량에서의 서스펜션 구성

실제 차량 서스펜션은 단순한 스프링 하나가 아니라 여러 기계 요소로 구성된다.

| 구성 요소 | 역할 |
|---|---|
| Control arm | 바퀴의 위치와 운동 궤적을 제어 |
| Spindle / Upright | 바퀴가 장착되는 회전/지지 부품 |
| Spring | 차량 하중 지지 및 복원력 제공 |
| Damper | 진동 에너지 소산 |
| Joint | 링크 간 회전 또는 구속 관계 제공 |
| Anti-roll bar | 좌우 바퀴 운동 차이로 인한 roll 억제 |

Chrono에서는 이러한 요소들이 강체, 조인트, 힘 요소, 구속조건으로 모델링된다.

---

## 4. Double Wishbone Suspension

Chrono HMMWV 모델의 핵심 서스펜션은 **double wishbone suspension**이다.

Double wishbone은 위쪽 control arm과 아래쪽 control arm, 즉 두 개의 A-arm이 바퀴 쪽 knuckle 또는 spindle을 잡고 있는 독립현가 방식이다.

```text
Chassis
  ├─ Upper Control Arm
  ├─ Lower Control Arm
  │     └─ Spring-Damper
  └─ Spindle / Wheel
```

이 구조의 장점은 바퀴가 위아래로 움직일 때 camber angle, wheel track, roll center 등을 비교적 정밀하게 설계할 수 있다는 점이다.

로버/험지 차량 관점에서는 다음 이유로 중요하다.

| 장점 | 로버 프로젝트와의 의미 |
|---|---|
| 독립현가 가능 | 한 바퀴가 요철을 만나도 다른 바퀴 영향 감소 |
| 접지력 유지 | 험지에서 타이어 접촉 유지에 유리 |
| 자세 안정성 | roll/pitch 변화 완화 |
| 설계 변수 다양 | arm 길이, spring stiffness, damping 변경 가능 |

---

## 5. Chrono에서의 Double Wishbone

Chrono의 `ChDoubleWishbone` 클래스는 double-A arm suspension을 표현하는 기본 클래스이다.  
공식 문서에서는 이 서스펜션이 **bodies and constraints**로 모델링된다고 설명한다.

Chrono의 full double wishbone 모델은 일반적으로 다음 요소를 포함한다.

| Chrono 요소 | 물리적 의미 |
|---|---|
| Upper control arm body | 위쪽 A-arm |
| Lower control arm body | 아래쪽 A-arm |
| Upright / spindle body | 바퀴 지지체 |
| Revolute / spherical joints | 링크 연결 구속 |
| Spring-damper force element | 현가 스프링과 댐퍼 |
| Wheel body | 회전하는 바퀴 |

즉, 서스펜션은 단일 함수가 아니라 여러 rigid body와 constraint가 결합된 하나의 subsystem이다.

---

## 6. HMMWV의 Suspension 모델

Chrono의 HMMWV 차량 모델에는 두 가지 대표적인 double wishbone 방식이 있다.

| 모델 | 설명 |
|---|---|
| HMMWV_Full | upper/lower control arm을 실제 rigid body로 모델링 |
| HMMWV_Reduced | control arm을 distance constraint로 단순화 |

공식 문서 기준으로:

- `HMMWV_Full`은 full double wishbone suspension을 사용한다.
- `HMMWV_Reduced`는 reduced double wishbone suspension을 사용한다.
- reduced 모델에서는 upper/lower control arm이 rigid body가 아니라 distance constraint로 대체된다.

따라서 두 모델의 차이는 다음과 같이 볼 수 있다.

| 항목 | Full model | Reduced model |
|---|---|---|
| Control arm | 강체로 모델링 | 거리 구속조건으로 단순화 |
| 정확도 | 높음 | 상대적으로 낮음 |
| 계산 비용 | 큼 | 작음 |
| 분석 목적 | 구조 하중, 상세 동역학 | 빠른 차량 거동 시뮬레이션 |

---

## 7. Phase 2 내용과의 연결

Phase 2에서 학습한 요소들은 서스펜션 내부에서 다음과 같이 연결된다.

| Phase 2 개념 | Suspension에서의 역할 |
|---|---|
| Rigid body | chassis, control arm, spindle |
| Revolute joint | control arm 회전축 |
| Spherical joint | ball joint |
| TSDA | spring-damper |
| RSDA | 회전 관절의 torsional compliance |
| Constraint | 링크 길이, 조인트 운동 제한 |

즉, Phase 3의 차량 모델은 Phase 2에서 배운 부품들을 조립한 더 큰 시스템이다.

---

## 8. 코드 관점에서 보는 Suspension

PyChrono의 HMMWV 예제에서는 서스펜션을 직접 하나하나 만들기보다는 HMMWV 차량 객체 안에 이미 포함된 모델을 사용한다.

대표적인 흐름은 다음과 같다.

```python
import pychrono.vehicle as veh

hmmwv = veh.HMMWV_Full()
hmmwv.SetContactMethod(chrono.ChContactMethod_NSC)
hmmwv.SetChassisCollisionType(veh.CollisionType_NONE)
hmmwv.SetInitPosition(chrono.ChCoordsysd(initLoc, initRot))
hmmwv.Initialize()
```

이때 `hmmwv.Initialize()` 내부에서 차량의 chassis, suspension, steering, wheels, tires, powertrain 등이 함께 초기화된다.

즉, 사용자는 HMMWV 객체만 생성하지만 내부적으로는 다음 계층 구조가 만들어진다.

```text
HMMWV_Full
 ├─ Chassis
 ├─ Front suspension
 ├─ Rear suspension
 ├─ Steering
 ├─ Wheels
 ├─ Tires
 └─ Powertrain
```

---

## 9. Suspension에서 관찰해야 할 물리량

로버/차량 설계 최적화를 목표로 한다면 서스펜션에서 다음 물리량을 관찰하는 것이 중요하다.

| 물리량 | 의미 |
|---|---|
| Suspension travel | 바퀴가 위아래로 움직인 거리 |
| Spring force | 스프링 복원력 |
| Damper force | 감쇠력 |
| Wheel vertical load | 각 바퀴 수직하중 |
| Chassis roll angle | 좌우 기울기 |
| Chassis pitch angle | 앞뒤 기울기 |
| Tire contact state | 지면 접촉 유지 여부 |

이 값들은 나중에 지형 조건이 바뀔 때 차량 안정성 평가 지표로 사용할 수 있다.

---

## 10. 프로젝트 설계 변수로의 확장

서스펜션은 로버 최적 설계에서 중요한 설계 변수 집합이 될 수 있다.

| 설계 변수 | 영향 |
|---|---|
| Spring stiffness | 너무 크면 충격 전달 증가, 너무 작으면 자세 불안정 |
| Damping coefficient | 진동 억제와 지형 추종성에 영향 |
| Suspension travel | 큰 요철 통과 능력 |
| Control arm geometry | 휠 궤적과 접지성 |
| Vehicle CG height | 전복 안정성 |
| Wheelbase / track width | pitch/roll 안정성 |

예를 들어 같은 지형에서도 서스펜션 강성이 너무 크면 차량이 튀고, 너무 작으면 차체가 크게 흔들릴 수 있다.  
따라서 최적 설계에서는 단순히 속도만 보는 것이 아니라 안정성, 접지 유지, 에너지 소모를 함께 봐야 한다.

---

## 11. 다음 단계

다음 실습에서는 HMMWV 예제를 실행하면서 다음 항목을 확인한다.

```text
1. HMMWV_Full과 HMMWV_Reduced 차이 정리
2. 차량이 주행할 때 roll/pitch 변화 기록
3. terrain 조건 변화에 따른 suspension 반응 비교
4. CSV로 time, position, roll, pitch, velocity 저장
```

이후 tire 모델과 결합하면 지형-타이어-서스펜션의 전체 상호작용을 분석할 수 있다.

---

## 12. 참고 자료

- Project Chrono 공식 문서: ChDoubleWishbone Class Reference  
  https://api.projectchrono.org/classchrono_1_1vehicle_1_1_ch_double_wishbone.html

- Project Chrono 공식 문서: HMMWV Vehicle Models  
  https://api.projectchrono.org/group__vehicle__models__hmmwv.html

- Project Chrono 공식 문서: HMMWV_DoubleWishboneReducedRear  
  https://api.projectchrono.org/classchrono_1_1vehicle_1_1hmmwv_1_1_h_m_m_w_v___double_wishbone_reduced_rear.html

- Project Chrono 공식 문서: Vehicle Models  
  https://api.projectchrono.org/8.0.0/vehicle_models.html

- GitHub Demo: demo_VEH_HMMWV9_YUP.py  
  https://github.com/projectchrono/chrono/blob/main/src/demos/python/vehicle/demo_VEH_HMMWV9_YUP.py
