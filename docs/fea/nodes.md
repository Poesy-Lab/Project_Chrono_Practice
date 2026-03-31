---
title: "FEA 노드"
author: ""
last_modified: "2026-03-31"
tags:
  - chrono
  - fea
---

# FEA 노드

유한요소 메시의 절점. 위치/회전 자유도를 가짐.

## 관련 클래스

| 클래스 | 설명 |
|--------|------|
| `ChNodeFEAxyz` | 3자유도 노드 (위치만) |
| `ChNodeFEAxyzrot` | 6자유도 노드 (위치+회전) |

## 참고

- [공식 API 문서 (C++)](https://api.projectchrono.org/group__fea__nodes.html)
- [FEA 매뉴얼 (C++)](https://api.projectchrono.org/manual_fea.html)
- Python 데모: `chrono/src/demos/python/fea/demo_FEA_beams.py`
- ← [[fea/index|FEA 개요로 돌아가기]]
