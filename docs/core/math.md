---
title: "수학 도구"
author: ""
last_modified: "2026-03-31"
tags:
  - chrono
  - core
---
# multicore math란?
Chrono의 `Multicore Math`는 Chrono Multicore 모듈 내부에서 사용하는 수학 자료형과 연산 함수들을 모아둔 모듈이다.  
일반적인 Chrono에서는 `ChVector3d`, `ChMatrix33d`, `ChQuaterniond` 같은 Core 자료형을 많이 사용하지만, Multicore 내부에서는 병렬 계산 효율을 위해 더 단순하고 가벼운 자료형인 다음 타입들을 사용한다.  
- `real`  
- `real2`  
- `real3`  
- `real4`  
- `quaternion`  
- `Mat33`  
  
이 자료형들은 충돌 계산, 접촉 계산, 병렬 연산, granular dynamics 같은 Multicore 내부 계산에서 사용된다.  
  
>[!important] 중요한 포인트  
> Multicore Math는 일반 사용자가 물체를 만드는 고수준 API라기보다는,  
> **Chrono Multicore 내부 계산을 빠르게 수행하기 위한 저수준 수학 구조**에 가깝다.  
> 따라서 일반 PyChrono 예제에서는 직접 사용할 일이 적지만, 내부 solver나 contact 구조를 이해할 때 매우 중요하다.  
  
## 일반 Chrono와 Multicore Math의 차이
| 구분                | 일반 Chrono Core  | Multicore Math |
| ----------------- | --------------- | -------------- |
| 벡터                | `ChVector3d`    | `real3`        |
| 회전                | `ChQuaterniond` | `quaternion`   |
| 행렬                | `ChMatrix33d`   | `Mat33`        |
| 목적                | 일반 시뮬레이션 API    | 병렬 계산 내부 처리    |
| 사용 위치             | 사용자 코드          | Multicore 내부   |
| PyChrono 직접 사용 빈도 | 많음              | 적음             |
>[!note]  
> PyChrono에서는 실제로 `real3` 대신 대부분 `ChVector3d`를 사용한다.  
> 따라서 Python 사용자는 `real3 ≈ ChVector3d`처럼 대응해서 이해하면 된다.  
  
# 기본 실수 타입  
## (1) `real`  
`real`은 Chrono Multicore에서 사용하는 기본 실수 타입이다.  
  
공식 문서에서는 보통 다음처럼 정의된다.  
  
```cpp  
typedef double real;
```

즉 기본적으로 double precision 실수형이다.

## (2) `real1`
`real1`은 사실상 단일 실수값을 의미한다.

즉:
- 질량
- 거리
- 속도 크기
- 스프링 상수
- damping 값

같은 하나의 숫자를 표현한다고 이해하면 된다.

실제로는 대부분 그냥 `real` 자체를 사용하기 때문에 `real1`은 독립적인 벡터 타입처럼 자주 등장하지는 않는다.
> [!important]  
> `real2`, `real3`, `real4`는 벡터 구조체 느낌이 강하지만,  
> `real1`은 사실상 scalar(스칼라) 값이라고 이해하는 것이 맞다.

# 벡터 자료형
## (1) `real2`
`real2`는 2차원 벡터이다.
구조는 개념적으로 다음과 같다.
```
(x, y)
```

주로 다음에 사용된다.
- 2D 좌표
- texture 좌표
- 2D 접촉 계산
- 보조 벡터 계산

대표 연산:
- 덧셈
- 뺄셈
- scalar 곱
- 내적
- Normalize

## 2) `real3`
`real3`는 3차원 벡터이다.
Chrono Multicore에서 가장 많이 사용되는 벡터 타입이다.

주로 다음 데이터를 표현한다.
- 위치(position)
- 속도(velocity)
- 가속도(acceleration)
- 힘(force)
- 토크(torque)
- 방향(direction)

개념 구조:
```
(x, y, z)
```

대표 연산:
- `Dot(a, b)`
- `Cross(a, b)`
- `Normalize(v)`
- `Length(v)`
- `Clamp(v, min, max)`

> [!important]  
> Multicore 내부에서는 `real3`를 많이 사용하지만,  
> PyChrono에서는 대부분 `ChVector3d`로 대응해서 사용한다.

## (3) `real4`
`real4`는 4개의 실수값을 가지는 자료형이다.

개념 구조:
```
(x, y, z, w)
```

주로 다음 상황에서 사용된다.
- quaternion 저장
- SIMD 스타일 계산
- 병렬 메모리 정렬
- GPU 계산용 구조

# Quaternion
## (1) `quaternion`
`quaternion`은 회전을 표현하기 위한 자료형이다.
3차원 회전은 Euler angle로도 표현 가능하지만, Euler angle은 특정 각도에서 singularity 문제가 발생할 수 있다.
그래서 Chrono는 quaternion 기반 회전을 많이 사용한다.

구조:
```
(e0, e1, e2, e3)
```

일반적으로:
- `e0` → scalar part
- `e1,e2,e3` → vector part
이다.

# 행렬 자료형
## (1) `Mat33`
`Mat33`은 3x3 행렬이다.

주로 다음에 사용된다.
- 회전 행렬
- 관성 텐서
- 좌표 변환
- 접촉 계산
- 외적 행렬

대표 연산:
```
A + BA - BA * BA * v
```

# 주요 수학 함수
## (1) `Dot`
`Dot`은 벡터의 내적을 계산한다.

수식:
$$  
a \cdot b = a_x b_x + a_y b_y + a_z b_z  
$$

의미:
- 방향 비교
- 투영 계산
- 접촉 방향 계산
- 힘 성분 계산

PyChrono에서는 보통 다음처럼 사용한다.
```python
import pychrono as chrono

a = chrono.ChVector3d(1, 2, 3)
b = chrono.ChVector3d(4, 5, 6)

d = a.Dot(b)

print(d)
```

## (2) `Cross`
`Cross`는 벡터 외적을 계산한다.

수식:
$$  
a × b 
$$

외적 결과는 두 벡터 모두에 수직인 벡터이다.

주로 다음에 사용된다.
- 토크 계산
- 회전축 계산
- 법선 벡터 계산

PyChrono 예시:
```python
import pychrono as chrono

a = chrono.ChVector3d(1, 0, 0)
b = chrono.ChVector3d(0, 1, 0)

c = a.Cross(b)

print(c)
```

결과:
```
(0,0,1)
```

## (3) `Normalize`

`Normalize`는 벡터 길이를 1로 만드는 함수이다.

수식:
$$
\hat{v}=\frac{v}{|v|}
$$
즉 방향만 유지하고 크기를 제거한다.

PyChrono 예시:
```python
import pychrono as chrono

v = chrono.ChVector3d(3, 4, 0)

n = v.GetNormalized()

print(n)
```

## (4) `Length`
`Length`는 벡터 크기를 계산한다.

수식:
$$
|v|=\sqrt{x^2+y^2+z^2}​
$$
PyChrono 예시:
```python
import pychrono as chrono

v = chrono.ChVector3d(3, 4, 0)

print(v.Length())
```

결과:
```
5
```

## (5) `Length2`
`Length2`는 길이의 제곱을 계산한다.

수식:
$$
|v|^2=x^2+y^2+z^2
$$

> [!important]  
> `Length()`는 sqrt 계산이 필요하다.  
> 단순 거리 비교 목적이면 `Length2()`가 더 빠르다.

## (6) `Clamp`
`Clamp`는 값을 특정 범위 안으로 제한한다.

수식 개념:
```
Clamp(x, low, high)
```

의미:
- `x < low` → low 반환
- `x > high` → high 반환
- 범위 안 → 그대로 반환

예시:
```
Clamp(12, 0, 10) = 10
```

## (7) `SkewSymmetric`
`SkewSymmetric`은 벡터를 skew-symmetric matrix로 바꾸는 함수이다.

벡터:
```
r = [x,y,z]
```
를 다음 행렬로 변환한다.

```
[  0  -z   y ][  z   0  -x ][ -y   x   0 ]
```
이 행렬은 외적을 행렬곱 형태로 표현할 때 사용된다.

수식:
$$
r×v=S(r)v
$$

> [!important]  
> `SkewSymmetric`은 단순한 행렬 생성 함수가 아니라,  
> 외적 연산을 행렬 형태로 표현하기 위한 도구이다.

# PyChrono에서는 어떻게 이해하면 되는가?
실제 Python 사용자 입장에서는 다음처럼 대응해서 이해하면 된다.

|Multicore Math|PyChrono|
|---|---|
|`real`|`float`|
|`real1`|scalar 값|
|`real2`|2D 벡터 개념|
|`real3`|`ChVector3d`|
|`real4`|quaternion/4성분 벡터 개념|
|`quaternion`|`ChQuaterniond`|
|`Mat33`|`ChMatrix33d`|

즉 Python에서는 보통 아래처럼 사용한다.
```python
import pychrono as chrono

v = chrono.ChVector3d(1,2,3)

print(v.Length())
print(v.Dot(v))
print(v.GetNormalized())
```

# 왜 Multicore Math를 배우는가?
Multicore Math는 다음 내용을 이해할 때 중요하다.
1. contact solver
2. granular dynamics
3. GPU/CUDA 기반 계산
4. 병렬 충돌 검출
5. Chrono Multicore 내부 구조
6. low-level dynamics 계산

반면 일반적인 차량 시뮬레이션이나 단순 강체 운동만 한다면 우선순위는 높지 않다.
> [!important]  
> 지금 단계에서는 다음만 이해해도 충분하다.
> 
> - `real3`
> - `quaternion`
> - `Mat33`
> - `Dot`
> - `Cross`
> - `Normalize`
> - `Clamp`
> - `SkewSymmetric`

# 관련 클래스

| 클래스               | 설명           |
| ----------------- | ------------ |
| `ChVector3d`      | 3D 벡터        |
| `ChQuaterniond`   | 쿼터니언 (회전 표현) |
| `ChFramed`        | 위치 + 회전 프레임  |
| `ChFunctionConst` | 상수 함수        |
| `ChFunctionSine`  | 사인파 함수       |

# 참고

- [공식 API 문서 (C++)](https://api.projectchrono.org/group__chrono__mc__math.html)
- [Mathematical Objects 매뉴얼 (C++)](https://api.projectchrono.org/mathematical_objects.html)
- Python 데모: `chrono/src/demos/python/core/demo_CH_coords.py`
- Python 데모: `chrono/src/demos/python/core/demo_CH_functions.py`
- Python 데모: `chrono/src/demos/python/core/demo_CH_EulerAngles.py`
- ← [[core/index|Core 개요로 돌아가기]]
