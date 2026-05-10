---
title: "운전자 입력"
author: ""
last_modified: "2026-03-31"
tags:
  - chrono
  - vehicle
---

# 운전자 입력

차량 제어를 위한 운전자 모델 (키보드, 경로 추종, 데이터 파일).

## 관련 클래스

| 클래스                      | 설명            |
| ------------------------ | ------------- |
| `ChInteractiveDriverIRR` | 키보드 실시간 조작    |
| `ChPathFollowerDriver`   | PID 경로 추종     |
| `ChDataDriver`           | 미리 정의된 입력 시퀀스 |

## 참고

- [공식 API 문서 (C++)](https://api.projectchrono.org/group__vehicle__driver.html)
- [Vehicle Driver 매뉴얼 (C++)](https://api.projectchrono.org/vehicle_driver.html)
- Python 데모: `chrono/src/demos/python/vehicle/demo_VEH_SteeringController.py`
- Python 데모: `chrono/src/demos/python/vehicle/demo_VEH_HMMWV_circle.py`
- ← [[vehicle/index|Vehicle 개요로 돌아가기]]
