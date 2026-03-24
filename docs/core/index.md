# Chrono Core — 물리 엔진의 심장

> 🟢 우리 팀 필수 | 💻 CPU만으로 동작
> 📖 [공식 매뉴얼](https://api.projectchrono.org/manual_core.html)

모든 Chrono 모듈의 기반이 되는 핵심 엔진입니다.
물리 세계 생성, 강체, 충돌, 조인트, 모터, 힘, 솔버 등 모든 기본 기능을 포함합니다.

## 하위 문서

| 주제 | 문서 | 핵심 클래스 |
|---|---|---|
| 시스템 | [[system]] | `ChSystemNSC`, `ChSystemSMC` |
| 강체 | [[rigid_bodies]] | `ChBody`, `ChBodyEasy*` |
| 충돌 | [[collisions]] | `ChCollisionShape*`, `ChContactMaterial*` |
| 조인트 | [[links]] | `ChLinkRevolute`, `ChLinkLockLock` 외 20+ |
| 모터 | [[motors]] | `ChLinkMotorRotation*`, `ChLinkMotorLinear*` |
| 힘/스프링 | [[loads]] | `ChLinkTSDA`, `ChForce`, `ForceFunctor` |
| 솔버 | [[solver]] | `PSOR`, `APGD`, `HHT` |
| 수학 도구 | [[math]] | `ChVector3d`, `ChQuaterniond`, `ChFunction*` |

## 관련 레슨

- Phase 1 (lesson 01~06): 시스템, 강체, 충돌, 재질, 시각화
- Phase 2 (lesson 07~12): 조인트, 스프링, 모터, 기어

← [[../index|탐사 지도로 돌아가기]]
