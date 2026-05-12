---
title: "Powertrain 학습 지도"
author: ""
last_modified: "2026-05-11"
tags:
  - chrono
  - vehicle
  - powertrain
---

# Powertrain 학습 지도

> Project Chrono Phase 3 - Vehicle / Powertrain  
> 목표: 엔진과 변속기가 차량 주행 성능에 어떤 방식으로 영향을 주는지 이해하고, JSON 파라미터를 실험 변수로 다룰 수 있게 한다.

---

## 1. 먼저 알아야 할 한 문장

Chrono::Vehicle에서 powertrain은 **운전자 throttle 입력을 받아 엔진 토크를 만들고, 변속기를 거쳐 driveline으로 전달되는 driveshaft torque를 계산하는 subsystem**이다.

```text
Driver throttle
    -> Engine torque
    -> Transmission torque/speed conversion
    -> Driveline torque distribution
    -> Wheel torque
    -> Tire-ground force
```

---

## 2. 전체 학습 순서

| 순서 | 문서 | 질문 |
|---|---|---|
| 1 | [[1_architecture]] | Chrono에서 engine과 transmission은 어떻게 연결되는가? |
| 2 | [[2_engine_models]] | throttle과 engine speed로 torque를 어떻게 계산하는가? |
| 3 | [[3_transmission_models]] | gear ratio와 torque converter는 torque/speed를 어떻게 바꾸는가? |
| 4 | [[4_pychrono_json_workflow]] | PyChrono에서 JSON powertrain을 어떻게 만들고 실험하는가? |
| 5 | [[../wheeled/4_driveline]] | transmission 출력이 바퀴 토크로 어떻게 분배되는가? |

---

## 3. 팀 프로젝트 관점에서 중요한 이유

우리 프로젝트는 드론/로버/환경 가상환경을 만들고, 시뮬레이션 결과를 온톨로지/AI 레이어에 넘기는 것이 목표이다.
로버 또는 차량 모델에서 powertrain은 다음 성능 지표에 직접 영향을 준다.

| 성능 지표   | powertrain 관련 원인                               |
| ------- | ---------------------------------------------- |
| 가속 성능   | engine torque map, gear ratio                  |
| 최고 속도   | max engine speed, high gear ratio              |
| 등판 성능   | low-speed torque, driveline, tire traction     |
| slip 증가 | 과도한 wheel torque, 낮은 마찰, deformable soil       |
| 에너지 소비  | throttle history, torque demand, speed profile |
| 실시간성    | simple model vs shafts model 계산량               |

> [!important] 험지에서는 토크만 키우면 안 된다
> 바퀴 토크가 커지면 추진력이 커질 수 있지만, 마찰 한계나 토양 전단 한계를 넘으면 slip과 sinkage가 증가한다.
> 즉 powertrain 설계는 tire/terrain과 함께 봐야 한다.

---

## 4. 모델 선택 기준

| 목적 | 추천 모델 | 이유 |
|---|---|---|
| 첫 실행 | `EngineSimpleMap + AutomaticTransmissionSimpleMap` | JSON이 짧고 수식이 명확함 |
| 빠른 배치 실험 | simple map 계열 | 계산량이 낮고 파라미터 sweep이 쉬움 |
| torque converter 분석 | `EngineShafts + AutomaticTransmissionShafts` | converter slip과 shaft inertia 포함 |
| clutch/수동변속 학습 | `ManualTransmissionShafts` | clutch torque limit과 clutch input 확인 가능 |
| 아주 단순한 baseline | `EngineSimple` | 최대 토크/출력만으로 빠르게 비교 가능 |
| CVT 유사 모델 | `AutomaticTransmissionSimpleCVT` | driveshaft speed에 따라 연속 gear ratio 변화 |

---

## 5. Powertrain과 다른 subsystem의 경계

```text
Powertrain
  Engine:
    throttle + motorshaft speed -> motorshaft torque

  Transmission:
    motorshaft torque + driveshaft speed -> driveshaft torque

Driveline
  driveshaft torque -> axle/wheel torque distribution

Tire/Terrain
  wheel torque -> contact force -> vehicle motion
```

| subsystem | 다루는 것 | 다루지 않는 것 |
|---|---|---|
| Engine | torque-speed curve, throttle response | 어느 바퀴에 토크가 가는지 |
| Transmission | gear ratio, shift, converter, clutch | tire slip, terrain contact |
| Driveline | front/rear/left/right torque split | 엔진 토크 생성 |
| Tire | slip에 따른 접촉력 | 엔진 내부 동역학 |
| Terrain | 지형 높이, 마찰, 변형 | 기어비와 엔진 맵 |

---

## 6. 가장 먼저 기록할 CSV 컬럼

입문 단계에서는 내부 torque를 모두 얻으려고 하기보다, 접근 가능한 값부터 기록하는 것이 좋다.

```text
time,
throttle, braking,
x, y, z, speed,
engine_rpm, engine_torque,
gear, driveshaft_torque,
wheel_omega_FL, wheel_omega_FR, wheel_omega_RL, wheel_omega_RR
```

추후 확장:

```text
torque_converter_slippage,
torque_converter_input_torque,
torque_converter_output_torque,
estimated_slip_FL, estimated_slip_FR, estimated_slip_RL, estimated_slip_RR,
terrain_height, terrain_mu
```

---

## 7. 해석할 때 자주 하는 실수

| 실수 | 왜 문제인가 |
|---|---|
| engine torque만 보고 차량 성능을 판단 | gear ratio, driveline, tire slip을 놓친다 |
| wheel torque가 크면 무조건 좋다고 생각 | 마찰 한계 초과 시 slip만 증가할 수 있다 |
| Chrono gear ratio를 일반 자동차 표기와 동일하게 해석 | Chrono simple transmission 수식은 $T_d = T_m / r_g$이다 |
| simple model 결과를 실제 차량처럼 과해석 | torque converter, clutch, shaft inertia가 빠져 있을 수 있다 |
| shafts model부터 시작 | 초보자는 디버깅 포인트가 너무 많아진다 |

---

## 8. 추천 실습 루트

```text
1. HMMWV 기본 예제 실행
2. engine/transmission type만 바꿔보기
3. engine JSON의 torque map 읽기
4. transmission JSON의 gear ratio 읽기
5. speed, engine_rpm, gear를 CSV로 저장
6. throttle sweep 실험
7. gear ratio sweep 실험
8. driveline/terrain 문서와 결합
```

---

## 9. 참고 링크

- [[../powertrain|Powertrain 개요]]
- [[../wheeled/4_driveline|Driveline]]
- [[../wheeled/6_simulation_loop|Simulation Loop]]
- Project Chrono 공식 문서: https://api.projectchrono.org/vehicle_powertrain.html

