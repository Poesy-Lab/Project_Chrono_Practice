---
title: "지형 (Terrain)"
author: ""
last_modified: "2026-03-31"
tags:
  - chrono
  - vehicle
---

# 지형 (Terrain)

차량이 주행하는 지형 모델. Vehicle 모듈(`chrono::vehicle`)에 포함된 클래스들입니다.

## 관련 클래스

| 클래스 | 설명 |
|--------|------|
| `RigidTerrain` | 강체 지형 (평면/메시/높이맵) |
| `SCMTerrain` | 변형 가능 토양 (바퀴 자국) |
| `FlatTerrain` | 무한 수평면 |
| `GranularTerrain` | 입자 기반 지형 (GPU) |
| `CRGTerrain` | OpenCRG 도로 프로파일 |

## 참고

- [공식 API 문서 (C++)](https://api.projectchrono.org/group__vehicle__terrain.html)
- [Vehicle Terrain 매뉴얼 (C++)](https://api.projectchrono.org/vehicle_terrain.html)
- Python 데모: `chrono/src/demos/python/vehicle/demo_VEH_RigidTerrain.py`
- Python 데모: `chrono/src/demos/python/vehicle/demo_VEH_DeformableSoil.py`
- Python 데모: `chrono/src/demos/python/vehicle/demo_VEH_HMMWV_DefSoil.py`
- ← [[vehicle/index|Vehicle 개요로 돌아가기]]
