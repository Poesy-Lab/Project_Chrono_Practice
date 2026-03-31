---
title: "힘과 스프링-댐퍼"
author: ""
last_modified: "2026-03-31"
tags:
  - chrono
  - core
---

# 힘과 스프링-댐퍼

외력, 스프링-댐퍼, 사용자 정의 힘 함수(ForceFunctor) 적용.

## 관련 클래스

| 클래스 | 설명 |
|--------|------|
| `ChLinkTSDA` | 1D 스프링-댐퍼 |
| `ChForce` | 물체에 직접 힘 적용 |
| `ForceFunctor` | 사용자 정의 힘 함수 |
| `ChLoadBodyForce` | 분산 하중 |

## 참고

- [공식 API 문서 (C++)](https://api.projectchrono.org/classchrono_1_1_ch_link_t_s_d_a.html)
- [Loads 매뉴얼 (C++)](https://api.projectchrono.org/loads.html)
- Python 데모: `chrono/src/demos/python/mbs/demo_MBS_spring.py`
- Python 데모: `chrono/src/demos/python/mbs/demo_MBS_prismatic_force.py`
- ← [[core/index|Core 개요로 돌아가기]]
