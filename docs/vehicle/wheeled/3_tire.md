# Tire

> Project Chrono Phase 3 - Vehicle / Wheeled Vehicle  
> 주제: 타이어 모델과 지형-차량 상호작용

---

## 1. 정의

타이어(tire)는 차량의 바퀴와 지면 사이에서 힘을 생성하는 핵심 요소이다.  
차량이 움직이는 이유는 엔진이나 모터가 직접 차체를 미는 것이 아니라, 바퀴에 전달된 토크가 타이어-지면 접촉을 통해 추진력으로 변환되기 때문이다.

Chrono::Vehicle에서 타이어는 wheel subsystem에 장착되며, terrain과 상호작용하여 다음 힘과 모멘트를 계산한다.

| 힘/모멘트 | 의미 |
|---|---|
| Longitudinal force | 전진/제동 방향 힘 |
| Lateral force | 선회 방향 횡력 |
| Vertical force | 지면으로부터 받는 수직하중 |
| Aligning moment | 타이어가 진행 방향으로 정렬되려는 모멘트 |
| Rolling resistance | 구름저항 |

즉, 타이어 모델은 차량 동역학에서 **지면과 차량을 연결하는 물리 인터페이스**이다.

---

## 2. 물리적 의미

타이어가 지면과 접촉하면 접촉 패치(contact patch)에서 변형, 마찰, 미끄러짐이 발생한다.  
이때 타이어는 단순히 굴러가는 물체가 아니라, 차량 운동을 결정하는 힘 생성 장치로 작동한다.

기본 흐름은 다음과 같다.

```text
Engine / Motor torque
        ↓
Wheel rotation
        ↓
Tire-ground contact
        ↓
Longitudinal force
        ↓
Vehicle acceleration
```

조향 상황에서는 다음 흐름이 추가된다.

```text
Steering input
        ↓
Wheel heading change
        ↓
Slip angle
        ↓
Lateral tire force
        ↓
Vehicle yaw motion
```

따라서 차량의 가속, 제동, 선회, 미끄러짐, 험지 주행 성능은 대부분 타이어 모델에 크게 의존한다.

---

## 3. 주요 타이어 개념

### 3.1 Slip Ratio

Slip ratio는 바퀴가 실제 이동 속도보다 얼마나 더 빠르게 또는 느리게 회전하는지를 나타낸다.

```text
slip ratio ≈ (wheel circumferential speed - vehicle longitudinal speed)
             / vehicle longitudinal speed
```

- slip ratio가 0이면 순수 구름에 가깝다.
- 양의 slip ratio는 구동 중 바퀴가 헛도는 상황과 관련된다.
- 음의 slip ratio는 제동 중 바퀴가 잠기는 상황과 관련된다.

로버가 모래나 흙 위에서 주행할 때 slip ratio는 매우 중요한 성능 지표가 된다.

---

### 3.2 Slip Angle

Slip angle은 타이어가 향하는 방향과 실제 속도 방향 사이의 각도이다.

```text
slip angle = tire heading direction - tire velocity direction
```

조향을 하면 타이어 방향이 바뀌고, 이때 slip angle이 생긴다.  
Slip angle이 생기면 타이어는 lateral force를 생성하고, 이 힘이 차량을 회전시킨다.

---

### 3.3 Normal Load

Normal load는 지면이 타이어를 밀어 올리는 수직하중이다.  
타이어가 생성할 수 있는 마찰력은 보통 normal load와 마찰계수에 의해 제한된다.

```text
maximum friction force ≈ μN
```

여기서:

| 기호 | 의미 |
|---|---|
| μ | tire-ground friction coefficient |
| N | normal load |

따라서 경사면, 요철, 차량 무게중심 변화는 각 바퀴의 normal load를 바꾸고, 이는 접지력과 미끄러짐에 영향을 준다.

---

## 4. Chrono::Vehicle의 Tire Model 분류

Chrono::Vehicle은 여러 종류의 타이어 모델을 제공한다.  
공식 문서 기준으로 tire subsystem에는 rigid tire, semi-empirical handling tire, FEA tire 등이 포함된다.

대표 모델은 다음과 같다.

| 모델 | 설명 |
|---|---|
| `ChRigidTire` | rigid cylinder로 표현되는 단순 접촉 타이어 |
| `ChFialaTire` | Fiala 기반 semi-empirical handling tire |
| `ChPac89Tire` | Pacejka 1989 Magic Formula tire |
| `ChPac02Tire` | Pacejka 2002 tire |
| `ChTMeasyTire` | TMeasy semi-empirical tire |
| `ChReissnerTire` | Reissner shell 기반 deformable tire |
| `FEATire` | finite element 기반 변형 타이어 |

이 중 Phase 3에서는 먼저 `RigidTire`, `FialaTire`, `TMeasyTire` 정도를 이해하면 충분하다.

---

## 5. Rigid Tire Model

Rigid tire는 타이어를 변형되지 않는 강체 원통으로 보는 가장 단순한 모델이다.  
Chrono 공식 문서에 따르면 `ChRigidTire`는 rigid cylinder로 모델링되며, friction을 지원하는 rigid contact terrain이 필요하다.

특징은 다음과 같다.

| 항목 | 설명 |
|---|---|
| 계산 속도 | 빠름 |
| 구조 | rigid body + contact |
| 변형 | 타이어 자체 변형 없음 |
| 사용 목적 | 기본 주행, 충돌, 단순 지형 접촉 |
| 한계 | 실제 타이어의 slip-force 특성을 정밀하게 표현하기 어려움 |

Rigid tire는 처음 vehicle simulation을 안정적으로 실행하고, 차량 구조와 terrain interaction을 확인하는 데 적합하다.

---

## 6. Fiala Tire Model

Fiala tire는 차량 동역학에서 자주 사용되는 semi-empirical tire model이다.  
타이어의 lateral force, longitudinal force, aligning moment 등을 slip 상태에 따라 계산한다.

특징은 다음과 같다.

| 항목 | 설명 |
|---|---|
| 모델 성격 | semi-empirical handling tire |
| 입력 | slip ratio, slip angle, normal load 등 |
| 출력 | longitudinal/lateral force, aligning moment |
| 장점 | 비교적 단순하면서 handling 분석 가능 |
| 사용 조건 | 주로 평탄한 road surface에 적합 |

Fiala 모델은 steering input에 따른 lateral force와 차량 yaw motion을 분석할 때 유용하다.

---

## 7. Pacejka Tire Model

Pacejka tire model은 흔히 **Magic Formula**라고 부르는 경험식 기반 타이어 모델이다.  
실험 데이터에 맞춰 계수를 조정하면 실제 차량 타이어의 force-slip curve를 잘 표현할 수 있다.

Chrono에서는 `ChPac89Tire`, `ChPac02Tire` 등이 제공된다.

| 모델 | 의미 |
|---|---|
| Pac89 | Pacejka 1989 기반 |
| Pac02 | Pacejka 2002 기반 |

Pacejka 계열은 타이어 데이터가 충분할 때 차량 handling simulation에 적합하다.  
하지만 계수 해석과 튜닝이 어렵기 때문에 Phase 3 초반에는 개념 이해 정도로 충분하다.

---

## 8. TMeasy Tire Model

TMeasy는 차량 동역학 시뮬레이션에서 많이 쓰이는 semi-empirical tire model이다.  
Chrono 공식 문서에서는 TMeasy가 single point contact 또는 four point contact 방식을 사용할 수 있다고 설명한다.

특징은 다음과 같다.

| 항목 | 설명 |
|---|---|
| 모델 성격 | semi-empirical tire |
| 접촉 방식 | single point 또는 four point contact |
| 장점 | 비교적 안정적이고 다양한 주행 조건에 사용 가능 |
| 활용 | handling, ride, uneven road test |

TMeasy는 로버 프로젝트에서 지형 요철과 타이어 반응을 함께 관찰할 때 좋은 후보가 될 수 있다.

---

## 9. Deformable / FEA Tire

FEA tire는 타이어 자체를 유한요소 모델로 표현하는 방식이다.  
타이어의 구조적 변형까지 계산할 수 있으므로 가장 물리적으로 상세하지만 계산 비용이 크다.

| 항목 | 설명 |
|---|---|
| 정확도 | 높음 |
| 계산 비용 | 큼 |
| 사용 목적 | 타이어 변형, 구조 응답, 정밀 접촉 분석 |
| Phase 3 적합도 | 초반 학습용으로는 과함 |

로버 최적설계 초반에는 FEA tire보다 rigid tire 또는 semi-empirical tire가 적절하다.

---

## 10. Tire와 Terrain의 관계

타이어 모델은 terrain model과 함께 사용되어야 한다.  
같은 타이어라도 지형 모델이 rigid terrain인지, SCM deformable terrain인지에 따라 물리 해석이 달라진다.

| Terrain | Tire interaction |
|---|---|
| RigidTerrain | 마찰 기반 접촉, 기본 주행 확인 |
| Height map terrain | 높이 변화에 따른 접촉점 변화 |
| SCMTerrain | 변형 가능한 토양과 타이어 침하/sinkage 계산 |
| Granular terrain | 입자 기반 복잡 접촉 가능 |

로버 프로젝트에서 가장 중요한 조합은 다음과 같다.

```text
Tire model + SCMTerrain
```

이 조합을 사용하면 바퀴가 흙이나 모래 위에서 얼마나 미끄러지고, 얼마나 침하되며, 어느 정도 추진력을 얻는지 분석할 수 있다.

---

## 11. HMMWV 예제에서 Tire 설정

PyChrono HMMWV 예제에서는 차량 모델과 타이어 타입을 선택할 수 있다.  
예제 구조는 대략 다음과 같다.

```python
import pychrono.vehicle as veh

hmmwv = veh.HMMWV_Full()
hmmwv.SetTireType(veh.TireModelType_TMEASY)
hmmwv.Initialize()
```

또는 특정 예제에서는 다음과 같이 tire model type을 변수로 지정한다.

```python
tire_model = veh.TireModelType_TMEASY
```

사용 가능한 모델은 Chrono 버전과 예제에 따라 다를 수 있으므로, 실제 코드에서는 설치된 PyChrono의 enum 이름을 확인해야 한다.

확인용 코드:

```python
import pychrono.vehicle as veh

print([name for name in dir(veh) if "TireModelType" in name])
print([name for name in dir(veh) if "TIRE" in name.upper()])
```

---

## 12. Simulation Loop에서 Tire의 역할

Chrono Vehicle simulation loop에서 tire는 보통 vehicle subsystem 내부에서 함께 업데이트된다.

흐름은 다음과 같다.

```text
1. Driver가 throttle, brake, steering 입력 생성
2. Powertrain이 wheel torque 계산
3. Steering이 wheel orientation 계산
4. Tire가 terrain과 접촉 상태 계산
5. Tire force/moment 계산
6. Wheel, suspension, chassis에 힘 전달
7. Vehicle state 업데이트
```

사용자는 보통 tire를 직접 advance하지 않고, vehicle 객체의 `Synchronize()`와 `Advance()`를 통해 전체 subsystem을 업데이트한다.

```python
driver_inputs = driver.GetInputs()

hmmwv.Synchronize(time, driver_inputs, terrain)
hmmwv.Advance(step_size)
```

---

## 13. 관찰해야 할 Tire 관련 물리량

로버/차량 최적설계에서 tire 파트는 다음 물리량을 관찰하는 것이 중요하다.

| 물리량 | 의미 |
|---|---|
| Slip ratio | 구동/제동 중 바퀴 헛돎 정도 |
| Slip angle | 조향 중 타이어 진행 방향 차이 |
| Longitudinal force | 추진력/제동력 |
| Lateral force | 선회력 |
| Normal force | 타이어 수직하중 |
| Contact state | 지면 접촉 여부 |
| Sinkage | 변형 지형에서 타이어 침하량 |
| Rolling resistance | 구름저항 |
| Wheel angular speed | 바퀴 회전 속도 |
| Vehicle speed | 실제 차량 속도 |

특히 로버 프로젝트에서는 다음 지표가 중요하다.

```text
높은 traction
낮은 slip ratio
작은 sinkage
안정적인 roll/pitch
낮은 energy consumption
```

---

## 14. 프로젝트 설계 변수로의 확장

타이어는 로버 최적 설계에서 매우 중요한 설계 변수이다.

| 설계 변수 | 영향 |
|---|---|
| Tire radius | 장애물 통과성, 지상고, 요구 토크 |
| Tire width | 접지 면적, sinkage, rolling resistance |
| Tire stiffness | 접지력, 진동, 승차감 |
| Friction coefficient | 추진력/제동력 한계 |
| Tire mass | unsprung mass, 에너지 소비 |
| Tread pattern | 실제 험지 접지력 |
| Inflation pressure | 접촉 면적과 지형 추종성 |

Chrono에서 모든 변수를 쉽게 바꿀 수 있는 것은 아니지만, JSON 기반 tire specification이나 vehicle parameters를 통해 일부 설계 변수를 조정할 수 있다.

---

## 15. 간단한 실험 아이디어

Phase 3에서 tire를 이해하기 위한 실험은 다음과 같다.

### 실험 1: Tire model 비교

```text
Terrain: flat RigidTerrain
Vehicle: HMMWV
Tire models: Rigid, Fiala, TMeasy
Input: constant throttle, steering = 0
Output: speed, acceleration, wheel angular speed
```

목표:

```text
타이어 모델에 따라 차량 가속 특성이 어떻게 달라지는지 확인
```

---

### 실험 2: Steering tire response

```text
Terrain: flat RigidTerrain
Vehicle: HMMWV
Input: constant throttle + step steering
Output: yaw rate, lateral displacement, path radius
```

목표:

```text
slip angle과 lateral tire force가 차량 선회에 미치는 영향 이해
```

---

### 실험 3: Terrain friction 변화

```text
Terrain friction: 0.3, 0.6, 0.9
Input: constant throttle
Output: slip ratio, speed, acceleration
```

목표:

```text
마찰계수가 낮아질 때 바퀴가 얼마나 헛도는지 확인
```

---

## 16. CSV 저장 예시

타이어 분석을 위해 저장하면 좋은 데이터 형식은 다음과 같다.

```text
time, x, y, z, speed, yaw, yaw_rate,
steering, throttle, braking,
wheel_omega_FL, wheel_omega_FR, wheel_omega_RL, wheel_omega_RR,
slip_FL, slip_FR, slip_RL, slip_RR
```

초기에는 모든 tire force를 바로 저장하기 어렵다면, 최소한 차량 속도와 wheel angular speed를 저장해서 slip ratio를 후처리로 계산할 수 있다.

---

## 17. 핵심 정리

```text
타이어는 차량과 지형 사이의 힘을 계산하는 핵심 인터페이스이다.
Rigid tire는 단순하고 빠르지만 실제 tire force 특성 표현은 제한적이다.
Fiala, Pacejka, TMeasy는 slip 기반 semi-empirical handling tire model이다.
TMeasy는 uneven road나 ride test에서도 자주 사용된다.
로버 프로젝트에서는 tire model과 terrain model의 조합이 주행 성능을 결정한다.
```

---

## 18. 참고 자료

- Project Chrono 공식 문서: Tire models  
  https://api.projectchrono.org/wheeled_tire.html

- Project Chrono 공식 문서: Tire subsystem  
  https://api.projectchrono.org/group__vehicle__wheeled__tire.html

- Project Chrono 공식 문서: ChRigidTire Class Reference  
  https://api.projectchrono.org/classchrono_1_1vehicle_1_1_ch_rigid_tire.html

- Project Chrono 공식 문서: ChTMeasyTire Class Reference  
  https://api.projectchrono.org/classchrono_1_1vehicle_1_1_ch_t_measy_tire.html

- Project Chrono 공식 문서: Tire test rig  
  https://api.projectchrono.org/wheeled_rig.html

- Project Chrono VEHICLE module  
  https://api.projectchrono.org/group__vehicle.html
