---
title: "FEA 요소"
author: ""
last_modified: "2026-03-31"
tags:
  - chrono
  - fea
---

# FEA 요소

노드를 연결하는 유한요소 (빔, 쉘, 케이블, 벽돌, 사면체).

## 관련 클래스

| 클래스 | 설명 |
|--------|------|
| `ChElementBeamEuler` | 오일러 빔 요소 |
| `ChElementShellANCF` | ANCF 쉘 요소 |
| `ChElementCableANCF` | ANCF 케이블 요소 |
| `ChElementTetraCorot_4` | 4절점 사면체 |

## 참고

- [공식 API 문서 (C++)](https://api.projectchrono.org/group__fea__elements.html)
- [FEA 매뉴얼 (C++)](https://api.projectchrono.org/manual_fea.html)
- Python 데모: `chrono/src/demos/python/fea/demo_FEA_beams.py`
- Python 데모: `chrono/src/demos/python/fea/demo_FEA_cables.py`
- Python 데모: `chrono/src/demos/python/fea/demo_FEA_shells.py`
- ← [[fea/index|FEA 개요로 돌아가기]]
