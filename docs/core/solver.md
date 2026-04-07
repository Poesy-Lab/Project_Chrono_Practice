---
title: Solver
author: ""
last_modified: 2026-03-31
tags:
  - chrono
  - core
---
# Solver란?
Chrono 시스템이 만든 수학 문제를 푸는 모듈로, 단순 계산이 아닌 제약 조건이 포함된 물리계의 상태를 만족시키는 해를 찾는다. 상위 기준점은  "ChSolver"이다.
ChSolver는 다음과 같은 기능을 제공한다.
- 종류를 식별하는 `GetType()` 
- 반복형인지 확인하는 `IsIterative()` 
- 직접형인지 확인하는 `IsDirect()`
- 계산 전 준비를 수행하는 `Setup()`
- 실제 계산을 수행하는 `Solve()` 

>[!important] 중요한 포인트
Chrono의 solver는 단순히 수식을 푸는 함수가 아니라, **ChSystemDescriptor에 저장된 변수와 제약조건을 기반으로 전체 물리 시스템의 상태를 계산하는 모듈**이다.  
> 즉 solver가 푸는 대상은 개별 식이 아니라, **시스템 전체의 연립 방정식 + 제약조건 구조**이다.   

# Solver의 종류
Solver는 문제의 종류에 따라 다음과 같이 나뉜다.
- 선형 시스템을 푸는 `ChSolverLS`
- 접촉 /마찰 등 보완성 문제를 푸는 `ChSolverVI` 
특히 접촉/마찰이 포함된 경우 VI 계열이 필수적으로 사용된다.

## (1) 선형 문제(ChSolverLS)
선형 연립방정식을 푸는 문제를 다룬다. 제약이 있어도 최종적으로는 선형 시스템으로 정리되는 경우에 사용된다.
선형 계열은 계산 방식에 따라 다음과 같이 나뉜다.
- 희소 행렬 직접해법(ChDirectSolverLS) 
- 반복형 선형해법(ChIterativeSolverLS) 
### 희소 행렬 직접해법(ChDirectSolverLS) 
이 계열은 희소 행렬을 분해(factorization)하여 해를 직접 구하는 방식이다.
공식 문서에서 이 계열은 VI나 complementarity 문제는 처리할 수 없고, NSC formulation에는 사용할 수 없다고 명시한다. 따라서 행렬을 직접 분해해서 푸는 선형 문제 전용으로 사용하는 것이 적절하다.

이 방식은 다음과 같은 특징을 가진다.  
- 행렬을 직접 분해하여 해를 계산 (factorization 기반)  
- 반복 과정이 없기 때문에 수렴 문제 없이 안정적인 해를 구할 수 있음  
- 계산 정확도가 높은 대신, 메모리 사용량과 계산 비용이 클 수 있음   
    
대표적인 solver는 다음과 같다.  
- `ChSolverSparseLU`
LU분해 기반으로 빠르고 정확하지만 메모리를 많이 사용해 큰 시스템에서는 부담
- `ChSolverSparseQR`
QR분해 기반으로 가장 안정적이지만 LU보다 느리며 계산량이 큼

아래는 `ChSolverSparseQR`을 이용한 예제이다.
~~~python
import pychrono as chrono

system = chrono.ChSystemSMC()
system.SetGravitationalAcceleration(chrono.ChVector3d(0, -9.81, 0))
system.SetTimestepperType(chrono.ChTimestepper.Type_EULER_IMPLICIT_LINEARIZED)

solver = chrono.ChSolverSparseQR()
system.SetSolver(solver)

ground = chrono.ChBody()
ground.SetFixed(True)
system.Add(ground)

body = chrono.ChBody()
body.SetMass(1.0)
body.SetInertiaXX(chrono.ChVector3d(0.1, 0.1, 0.1))
body.SetPos(chrono.ChVector3d(0, 1.0, 0))
system.Add(body)

spring = chrono.ChLinkTSDA()
spring.Initialize(ground, body, False,
chrono.ChVector3d(0, 0, 0), chrono.ChVector3d(0, 1.0, 0))

spring.SetSpringCoefficient(200)
spring.SetDampingCoefficient(5)
spring.SetRestLength(1.0)
system.Add(spring)

step_size = 0.01
end_time = 2.0

while system.GetChTime() < end_time:
	system.DoStepDynamics(step_size)
	print("t:", system.GetChTime(), "y:", body.GetPos().y)
~~~

### 반복형 선형해법(ChIterativeSolverLS) 
반복 계산을 통해 해를 점진적으로 근사하는 방식이다.  행렬을 직접 분해하지 않고, 반복적인 연산을 통해 수렴하는 해를 찾는다.  또한 이 계열 역시 VI나 complementarity 문제는 처리할 수 없고, NSC formulation에는 사용할 수 없다.

이 방식은 다음과 같은 특징을 가진다.  
- tolerance(오차 기준)에 따라 계산 종료  
- max iteration(최대 반복 횟수) 설정 가능  
- diagonal preconditioner 사용 가능  
  
대표적인 solver는 다음과 같다.  
- `ChSolverGMRES`
비대칭 행렬도 처리 가능하며 오차를 최소화하는 방향으로 반복함. 범용적이지만 반복수가 늘어날 수 있음.
- `ChSolverMINRES`  
대칭 행렬 전용으로 오차 최소화 방식. 물리 문제에 잘 맞지만 비대칭 행렬 문제는 불가능.
- `ChSolverBiCGSTAB`
CG기반 개선형으로 비대칭 행렬도 처리 가능. 수렴이 빠른 경우가 많지만 경우에 따라  결과가 불안정할 수 있음.

아래는 `ChSolverMINRES`을 이용한 예제이다.
~~~python
import pychrono as chrono

system = chrono.ChSystemSMC()
system.SetGravitationalAcceleration(chrono.ChVector3d(0, -9.81, 0))
system.SetTimestepperType(chrono.ChTimestepper.Type_EULER_IMPLICIT_LINEARIZED)

solver = chrono.ChSolverMINRES()
solver.SetMaxIterations(100)
solver.SetTolerance(1e-10)
system.SetSolver(solver)

ground = chrono.ChBody()
ground.SetFixed(True)
system.Add(ground)

body = chrono.ChBody()
body.SetMass(1.0)
body.SetInertiaXX(chrono.ChVector3d(0.1, 0.1, 0.1))
body.SetPos(chrono.ChVector3d(0, 1.0, 0))
system.Add(body)

spring = chrono.ChLinkTSDA()
spring.Initialize(ground, body, False,
chrono.ChVector3d(0, 0, 0), chrono.ChVector3d(0, 1.0, 0))

spring.SetSpringCoefficient(200)
spring.SetDampingCoefficient(5)
spring.SetRestLength(1.0)
system.Add(spring)

step_size = 0.01
end_time = 2.0

while system.GetChTime() < end_time:
	system.DoStepDynamics(step_size)
	print("t:", system.GetChTime(), "y:", body.GetPos().y)
~~~
>[!important] 두 코드의 차이점
>- `ChSolverSparseQR(), ChSolverMINRES()`으로 각 사용 솔버가 다르다.
>- 아래와 같은 반복 해법 필수 옵션을 사용했다.
>`solver.SetMaxIterations()`: 최대 반복 횟수
>`solver.SetTolerance()`: 오차 허용 기준


|     |    직접 해법     |     반복 해법     |
| :-: | :----------: | :-----------: |
| 방식  | 분해하여 한 번에 계산 |    반복하며 근사    |
| 특징  |    정확, 안정    | 유연, 큰 시스템에 유리 |
| 조건  |  선형 문제만 가능   |   선형+확장 가능    |

## (2) 보완성 문제(ChSolverVI)
보완성 문제는 단순한 선형 연립방정식과 달리, 접촉(contact)이나 마찰(friction)과 같은 부등식 제약을 포함하는 문제를 의미한다.
이러한 문제는 일반적으로 LCP (Linear Complementarity Problem)와 CCP (Cone Complementarity Problem) 형태로 표현된다.  
- LCP: 접촉 조건과 같은 부등식 제약을 포함한 문제  
- CCP: LCP에 마찰까지 포함된 보다 현실적인 문제  

Chrono에서는 이러한 보완성 문제를 해결하기 위해 `ChSolverVI` 계열을 사용하고, 선형 문제와는 다르게 직접 해법이 없고 모두 반복형이기 때문에 `ChInterativeSolverVI`가 다음 계열이다.
### ChSolverPSOR
- projected fixed-point 방식
- overrelaxation 사용
- 변수 값을 바로 갱신하는 방식
- 비교적 직관적인 구조라 설명용으로 좋음
### ChSolverPJacobi
- projected fixed-point 방식 + Jacobi 스타일 업데이트
- PSOR보다 업데이트 방식이 더 단순
### ChSolverBB
- Barzilai-Borwein step 사용
- Spectral Projected Gradient 기반 
- diagonal preconditioner 사용 가능, 기본 활성화
- stiffness/damping block 포함 문제는 처리 불가
### ChSolverAPGD
- Accelerated Projected Gradient Descent 계열이다.
- Nesterov 가속 사용
### ChSolverADMM
- Alternating Direction Method of Multipliers 계열이다.
- multiplier를 사용하는 분할 최적화 계열


아래는 `ChSolverPSOR`을 이용한 예제이다.
~~~python
import pychrono as chrono

system = chrono.ChSystemNSC()
system.SetCollisionSystemType(chrono.ChCollisionSystem.Type_BULLET)
system.SetGravitationalAcceleration(chrono.ChVector3d(0, -9.81, 0))

solver = chrono.ChSolverPSOR()
solver.SetMaxIterations(100)
system.SetSolver(solver)

contact_mat = chrono.ChContactMaterialNSC()

ground = chrono.ChBodyEasyBox(10.0, 0.2, 10.0, 1000, 
	True, True, contact_mat)
ground.SetFixed(True)
ground.SetPos(chrono.ChVector3d(0, -0.1, 0))
system.Add(ground)

body = chrono.ChBodyEasyBox(0.4, 0.4, 0.4, 1000,
    True, True, contact_mat)
body.SetPos(chrono.ChVector3d(0, 1.0, 0))
system.Add(body)

step_size = 0.01
end_time = 2.0

while system.GetChTime() < end_time:
    system.DoStepDynamics(step_size)
    print("t:", system.GetChTime(), "y:", body.GetPos().y)
~~~

![[Pasted image 20260402142010.png]]

# 참고

- [공식 API 문서 (C++)](https://api.projectchrono.org/group__chrono__solver.html)
- [Simulation System 매뉴얼 (C++)](https://api.projectchrono.org/simulation_system.html)
- Python 유틸: `chrono/src/demos/python/SetChronoSolver.py`
- ← [[core/index|Core 개요로 돌아가기]]
