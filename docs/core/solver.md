---
title: "솔버와 시간 적분기"
author: ""
last_modified: "2026-03-31"
tags:
  - chrono
  - core
---

# 솔버와 시간 적분기

물리 방정식을 풀어 다음 상태를 계산하는 수치 해법.

## 관련 클래스

| 클래스 | 설명 |
|--------|------|
| `ChSolverPSOR` | Projected SOR (기본) |
| `ChSolverAPGD` | 가속 경사 하강법 |
| `ChTimestepperHHT` | HHT 적분기 (정밀) |

## 참고

- [공식 API 문서 (C++)](https://api.projectchrono.org/group__chrono__solver.html)
- [Simulation System 매뉴얼 (C++)](https://api.projectchrono.org/simulation_system.html)
- Python 유틸: `chrono/src/demos/python/SetChronoSolver.py`
- ← [[core/index|Core 개요로 돌아가기]]
