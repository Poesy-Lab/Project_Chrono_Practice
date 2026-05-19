---
title: "충돌과 접촉 재질"
author: "Hojin Park"
last_modified: "2026-05-19"
tags:
  - chrono
  - core
  - collision
  - contact
---

# 충돌과 접촉 재질

> [!info] 코드 표기
> 이 문서의 코드 예시는 **PyChrono(Python)** 기준이다.
> C++ 공식 문서와 이름이 거의 같지만, Python에서는 `chrono.ChContactMaterialNSC()`처럼 `chrono.` 네임스페이스를 붙여 사용한다.

Chrono에서 충돌(collision)은 단순히 "물체가 닿았다"를 감지하는 기능이 아니라, 두 물체가 접촉했을 때 **어떤 힘이 생기는지**까지 계산하는 물리 모델이다.

공식 문서 기준으로 접촉 문제는 크게 두 단계로 나뉜다.

| 단계 | 의미 | 우리가 신경 쓸 것 |
|---|---|---|
| Collision detection | 어떤 형상들이 서로 닿거나 곧 닿을지 찾음 | 충돌 형상, 충돌 시스템, timestep |
| Contact formulation | 접촉점에서 반력, 마찰, 반발을 계산함 | NSC/SMC 방식, 접촉 재질 |

초보 단계에서는 아래처럼 기억하면 충분하다.

```text
시각 형상(VisualShape) = 화면에 보이는 모양
충돌 형상(CollisionShape) = 물리적으로 부딪히는 모양
접촉 재질(ContactMaterial) = 부딪힐 때의 마찰/반발 특성
```

> [!warning] 가장 흔한 실수
> 물체가 화면에는 보이는데 서로 통과하면, 대부분 다음 중 하나이다.
> - `EnableCollision(True)`를 하지 않았다.
> - `AddCollisionShape(...)`를 하지 않았다.
> - `ChSystemNSC()`인데 `ChContactMaterialSMC()`를 쓰는 등 contact method와 material 종류가 맞지 않는다.
> - timestep이 너무 커서 빠른 물체가 얇은 물체를 통과한다.

---

## 1. 충돌을 켜기 위한 최소 조건

두 물체가 실제로 충돌하려면 보통 다음 네 가지가 필요하다.

| 조건 | 예시 코드 | 설명 |
|---|---|---|
| 충돌 시스템 설정 | `sys.SetCollisionSystemType(...)` | 어떤 collision engine을 쓸지 결정 |
| 접촉 재질 생성 | `chrono.ChContactMaterialNSC()` | 마찰, 반발 계수 등 |
| 충돌 형상 추가 | `body.AddCollisionShape(...)` | 물리 계산용 형상 |
| 충돌 활성화 | `body.EnableCollision(True)` | 이 body가 충돌 계산에 참여 |

입문용 기본 조합은 다음과 같다.

```python
import pychrono as chrono

sys = chrono.ChSystemNSC()
sys.SetGravitationalAcceleration(chrono.ChVector3d(0, -9.81, 0))
sys.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)

mat = chrono.ChContactMaterialNSC()
mat.SetFriction(0.6)
mat.SetRestitution(0.2)
```

> [!tip] 왜 Bullet을 쓰나?
> Chrono에는 Bullet 기반 collision system과 multicore collision system이 있다.
> 우리 입문 학습과 CPU 기반 팀원 환경에서는 `Type_BULLET`부터 쓰는 것이 가장 단순하다.

---

## 2. NSC와 SMC

Chrono의 접촉 방식은 크게 NSC와 SMC로 나뉜다.
처음에는 **NSC부터 사용**하는 것을 권장한다.

| 방식 | 시스템 | 재질 | 특징 | 입문 추천도 |
|---|---|---|---|:---:|
| NSC | `ChSystemNSC()` | `ChContactMaterialNSC()` | 딱딱한 접촉을 constraint처럼 처리. 비교적 큰 timestep 가능 | 높음 |
| SMC | `ChSystemSMC()` | `ChContactMaterialSMC()` | 침투량에 비례한 penalty force 사용. 강성/감쇠 설정 중요 | 낮음 |

핵심 규칙:

```text
ChSystemNSC  <->  ChContactMaterialNSC
ChSystemSMC  <->  ChContactMaterialSMC
```

서로 섞지 않는 것이 좋다.
로버 4대 충돌 실험의 첫 버전도 `ChSystemNSC + ChContactMaterialNSC`로 시작하면 된다.

---

## 3. 접촉 재질(Contact Material)

접촉 재질은 충돌 형상에 붙는 물리 속성이다.
가장 자주 쓰는 값은 마찰계수와 반발계수이다.

```python
mat = chrono.ChContactMaterialNSC()

# 마찰: 0에 가까울수록 미끄러움, 클수록 잘 안 미끄러짐
mat.SetFriction(0.6)

# 반발: 0이면 거의 안 튕김, 1에 가까울수록 잘 튕김
mat.SetRestitution(0.1)
```

| 속성 | 메서드 | 의미 | 예시 |
|---|---|---|---|
| 마찰 | `SetFriction(mu)` | 정지/동마찰을 같은 값으로 설정 | 바퀴와 지면 접지 |
| 정지 마찰 | `SetStaticFriction(mu)` | 미끄러지기 전 버티는 정도 | 고무 바닥 |
| 동마찰 | `SetSlidingFriction(mu)` | 미끄러지는 중 저항 | 얼음/흙 비교 |
| 반발 | `SetRestitution(e)` | 튕기는 정도 | 공 튀기기 |
| 구름 저항 | `SetRollingFriction(r)` | 굴러가는 물체의 저항 | 바퀴 감속 |
| 스핀 저항 | `SetSpinningFriction(r)` | 접촉점에서 회전 저항 | 타이어/구체 회전 |

> [!note] 공유 재질 주의
> 여러 body가 같은 `mat` 객체를 공유하면, 나중에 `mat.SetFriction(...)`을 바꿨을 때 그 재질을 쓰는 모든 충돌 형상에 영향이 간다.
> 실험 조건을 명확히 나누고 싶으면 `mat_ground`, `mat_rover`, `mat_obstacle`처럼 재질 객체를 따로 만들자.

---

## 4. 충돌 형상(Collision Shape)

`ChBody`는 여러 개의 collision shape을 가질 수 있다.
복잡한 로버도 처음에는 단순한 상자/구/실린더 조합으로 충돌 형상을 잡는 것이 좋다.

| 형상 | 클래스 | 사용 예 |
|---|---|---|
| 상자 | `ChCollisionShapeBox` | 바닥, 장애물, 로버 body |
| 구 | `ChCollisionShapeSphere` | 공, 단순 바퀴 대체, 센서 marker |
| 실린더 | `ChCollisionShapeCylinder` | 바퀴, 롤러 |
| 캡슐 | `ChCollisionShapeCapsule` | 둥근 막대, link |
| 삼각 메시 | `ChCollisionShapeTriangleMesh` | 복잡한 지형/형상 |

단순 body에 충돌 형상을 직접 추가하는 패턴:

```python
body = chrono.ChBody()
body.SetMass(1.0)
body.SetInertiaXX(chrono.ChVector3d(0.1, 0.1, 0.1))
body.SetPos(chrono.ChVector3d(0, 2, 0))

mat = chrono.ChContactMaterialNSC()
mat.SetFriction(0.5)
mat.SetRestitution(0.2)

shape = chrono.ChCollisionShapeBox(mat, 1.0, 0.4, 0.6)
body.AddCollisionShape(shape)
body.EnableCollision(True)

sys.AddBody(body)
```

> [!important] collision shape은 body 기준 좌표계에 붙는다
> 충돌 형상은 기본적으로 body의 reference frame 기준으로 배치된다.
> body가 움직이고 회전하면 collision shape도 함께 움직인다.

---

## 5. `ChBodyEasy*`로 더 짧게 만들기

상자, 구, 실린더처럼 기본 형상은 `ChBodyEasy*`를 쓰면 질량/관성/시각화/충돌을 한 번에 만들 수 있다.

```python
mat = chrono.ChContactMaterialNSC()
mat.SetFriction(0.6)
mat.SetRestitution(0.1)

# 반지름 0.3 m, 밀도 1000 kg/m^3
# True, True는 각각 visualization, collision 활성화
sphere = chrono.ChBodyEasySphere(0.3, 1000, True, True, mat)
sphere.SetPos(chrono.ChVector3d(0, 3, 0))
sys.AddBody(sphere)
```

> [!warning] 생성자 인자 확인
> `ChBodyEasySphere(radius, density, True)`처럼 쓰면 보이는 형상만 추가되고 충돌 형상은 빠질 수 있다.
> 충돌까지 필요하면 로컬 레슨처럼 `ChBodyEasySphere(radius, density, True, True, mat)` 형태를 쓰자.

---

## 6. 최소 예제: 공이 바닥에 부딪혀 튕기기

아래 코드는 시각화 없이 콘솔에서만 공의 높이를 확인하는 최소 예제이다.
처음 충돌을 확인할 때는 이렇게 작게 시작하면 디버깅이 쉽다.

```python
import pychrono as chrono

sys = chrono.ChSystemNSC()
sys.SetGravitationalAcceleration(chrono.ChVector3d(0, -9.81, 0))
sys.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)

floor_mat = chrono.ChContactMaterialNSC()
floor_mat.SetFriction(0.8)
floor_mat.SetRestitution(0.1)

ball_mat = chrono.ChContactMaterialNSC()
ball_mat.SetFriction(0.4)
ball_mat.SetRestitution(0.7)

# 바닥
floor = chrono.ChBody()
floor.SetFixed(True)
floor.SetPos(chrono.ChVector3d(0, -0.1, 0))
floor.EnableCollision(True)
floor.AddCollisionShape(chrono.ChCollisionShapeBox(floor_mat, 10, 0.2, 10))
sys.AddBody(floor)

# 공
ball = chrono.ChBody()
ball.SetMass(1.0)
ball.SetPos(chrono.ChVector3d(0, 3, 0))
ball.EnableCollision(True)
ball.AddCollisionShape(chrono.ChCollisionShapeSphere(ball_mat, 0.3))

radius = 0.3
inertia = 2.0 / 5.0 * ball.GetMass() * radius**2
ball.SetInertiaXX(chrono.ChVector3d(inertia, inertia, inertia))
sys.AddBody(ball)

dt = 0.001
end_time = 3.0

while sys.GetChTime() < end_time:
    sys.DoStepDynamics(dt)

    time = sys.GetChTime()
    if int(time * 1000) % 200 == 0:
        print(
            "time:",
            round(time, 2),
            "height:",
            round(ball.GetPos().y, 3),
            "vy:",
            round(ball.GetPosDt().y, 3),
        )
```

실행 방법:

```bash
conda activate chrono
source setup_chrono_env.sh
python lessons/phase1/lesson_02_collision.py
```

---

## 7. 충돌 힘 확인하기

충돌이 실제로 일어나는지 숫자로 보고 싶으면 body의 contact force를 확인할 수 있다.

```python
contact_force = ball.GetContactForce()
force_mag = contact_force.Length()

if force_mag > 1e-6:
    print("contact force:", force_mag)
```

로버 충돌 실험에서는 다음처럼 기록하면 좋다.

```text
time, rover_name, x, y, z, speed, contact_force_x, contact_force_y, contact_force_z
```

처음에는 "어떤 body가 어떤 body와 부딪혔는지"까지 완벽하게 분류하지 않아도 된다.
각 로버 body의 `GetContactForce()` 크기가 특정 threshold를 넘는 순간을 충돌 이벤트로 기록하면 충분하다.

---

## 8. 충돌 family로 선택적 충돌 제어

복잡한 모델에서는 모든 부품이 서로 충돌하면 이상한 힘이 생기거나 계산이 느려질 수 있다.
Chrono는 collision family를 사용해 특정 그룹끼리 충돌하지 않게 만들 수 있다.

개념 예시:

```python
# PyChrono 바인딩에서 사용 가능 여부는 설치 버전에 따라 확인 필요
body.GetCollisionModel().SetFamily(2)
body.GetCollisionModel().DisallowCollisionsWith(4)
```

우리 프로젝트에서는 처음부터 family를 복잡하게 쓰지 말고, 다음 순서로 가는 것이 좋다.

```text
1. 로버를 단순 body 1개 또는 body + wheel 몇 개로 만든다.
2. 모든 로버끼리 충돌이 일어나는지 확인한다.
3. 자기 로버 내부 부품끼리 부딪혀 문제가 생길 때만 collision family를 도입한다.
```

---

## 9. 성능과 안정성을 위한 규칙

충돌 계산은 시뮬레이션에서 꽤 비싼 작업이다.
특히 4대 로버를 동시에 충돌시키면 collision shape 수가 금방 늘어난다.

| 상황 | 권장 |
|---|---|
| 처음 충돌 실험 | box, sphere, cylinder 같은 primitive 사용 |
| 복잡한 외형 필요 | visual shape만 복잡하게, collision shape은 단순하게 |
| 얇은 벽/판 | 너무 얇게 만들지 않기 |
| 빠른 물체가 통과함 | timestep 줄이기 |
| 로버가 떨림 | 접촉 재질, timestep, solver 설정 확인 |
| 계산이 느림 | collision shape 수 줄이기 |

기본 timestep 기준:

```python
# 충돌이 많은 실험은 작게 시작
step_size = 0.001
```

> [!tip] visual과 collision을 다르게 두기
> 로버를 멋지게 보여주고 싶으면 visual shape은 자세히 만들고, collision shape은 상자/실린더 몇 개로 단순화하는 것이 좋다.
> 공식 문서에서도 복잡한 collision shape은 성능 저하를 만들 수 있으므로 단순 형상을 권장한다.

---

## 10. 1인 1로버 프로젝트에서의 적용

12주차 이후 로버 4대 충돌 실험에서 박호진 파트가 담당해야 할 핵심 기준은 다음과 같다.

### 공통 충돌 환경 기준

```text
ChSystemNSC
  + ChCollisionSystem.Type_BULLET
  + ChContactMaterialNSC
  + RigidTerrain 또는 고정 바닥 body
```

### 로버 body 최소 조건

각 로버는 적어도 다음을 가져야 한다.

```text
1. body 또는 chassis
2. collision shape
3. contact material
4. EnableCollision(True)
5. 초기 위치와 속도
6. contact force logging
```

### 충돌 성공 판정

초기 목표는 정교한 손상 모델이 아니라 "접촉이 일어났다"를 확인하는 것이다.

```python
collision_threshold = 5.0  # N, 초기 실험용 임계값

force = rover_body.GetContactForce()
if force.Length() > collision_threshold:
    print("collision event:", sys.GetChTime(), force.Length())
```

---

## 11. 디버깅 체크리스트

### 물체가 서로 통과함

- `EnableCollision(True)` 확인
- `AddCollisionShape(...)` 확인
- `sys.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)` 확인
- `ChSystemNSC()`와 `ChContactMaterialNSC()` 조합 확인
- timestep을 `0.001` 이하로 줄여 보기
- 물체가 너무 얇거나 너무 빠르지 않은지 확인

### 물체가 보이지 않음

- collision shape은 렌더링용이 아니다.
- 보이게 하려면 `ChVisualShape*`를 추가하거나 `ChBodyEasy*`에서 visualization 인자를 `True`로 둔다.

### 너무 많이 튕김

- `SetRestitution(...)` 값을 낮춘다.
- `0.0`은 거의 안 튕김, `1.0`에 가까울수록 잘 튕김.

### 너무 미끄러짐

- `SetFriction(...)` 값을 높인다.
- 지형 재질과 로버 재질이 같은 객체를 공유하고 있는지도 확인한다.

### 계산이 느림

- collision shape 개수를 줄인다.
- triangle mesh collision 대신 box/sphere/cylinder 조합을 먼저 쓴다.
- 로버 내부 부품끼리 불필요하게 충돌하지 않는지 확인한다.

---

## 12. 관련 클래스 요약

| 클래스 | 역할 |
|---|---|
| `ChCollisionSystem` | collision engine 선택의 기준 클래스 |
| `ChCollisionModel` | body가 가진 collision shape 묶음 |
| `ChCollisionShape` | 모든 collision shape의 base class |
| `ChCollisionShapeBox` | 상자 collision shape |
| `ChCollisionShapeSphere` | 구 collision shape |
| `ChCollisionShapeCylinder` | 실린더 collision shape |
| `ChContactMaterialNSC` | NSC 접촉 재질 |
| `ChContactMaterialSMC` | SMC 접촉 재질 |
| `ChBody.GetContactForce()` | body에 작용한 접촉 힘 조회 |

---

## 참고

- [공식 API 문서: Collision detection](https://api.projectchrono.org/group__chrono__collision.html)
- [공식 매뉴얼: Collisions](https://api.projectchrono.org/collisions.html)
- [공식 API 문서: ChContactMaterialNSC](https://api.projectchrono.org/classchrono_1_1_ch_contact_material_n_s_c.html)
- [공식 API 문서: ChContactMaterialSMC](https://api.projectchrono.org/classchrono_1_1_ch_contact_material_s_m_c.html)
- Python 데모: `chrono/src/demos/python/mbs/demo_MBS_collisionNSC.py`
- Python 데모: `chrono/src/demos/python/mbs/demo_MBS_collisionSMC.py`
- 로컬 레슨: `lessons/phase1/lesson_02_collision.py`
- 로컬 레슨: `lessons/phase1/lesson_06_materials.py`
- ← [[core/index|Core 개요로 돌아가기]]
