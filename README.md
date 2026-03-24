# Project Chrono 학습 가이드 — 시뮬레이션 레이어

> **프로젝트**: AI 친화적 설계 표현 파이프라인의 **시뮬레이션 레이어**
> **목표**: Project Chrono로 **드론/로버/환경** 가상환경을 구축하고, 시뮬레이션 결과를 온톨로지/AI 레이어에 전달
> **대상**: Project Chrono를 처음 접하는 완전 초보자 (4인 캡스톤 팀)
> **환경**: Windows / Linux / macOS 모두 지원, NVIDIA GPU 선택사항

---

## 0. 프로젝트 목표와 파이프라인

이 저장소는 독립적인 학습 프로젝트가 아니라, **3-Layer 파이프라인**의 시뮬레이션 레이어를 구축하기 위한 학습/개발 공간입니다.

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│  ① 지식 공학 레이어   │     │  ② 시뮬레이션 레이어  │     │  ③ 전처리 레이어     │
│  (Knowledge Layer)   │ ──→ │  (Simulation Layer)  │ ──→ │  (Preprocessing)    │
│                     │ ←── │                     │     │                     │
│  OWL 온톨로지        │     │  ★ Project Chrono ★  │     │  BRepNet, GNN,      │
│  파라미터 범위 정의   │     │  드론/로버/환경 시뮬  │     │  PointNet++, MLP    │
│  시나리오 자동 생성   │     │  CSV/JSON/Mesh 출력  │     │  → AI 입력 벡터     │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
                                 ↑ 우리 팀이 담당
```

### 우리 팀의 범위

- **담당**: ② 시뮬레이션 레이어만 (Project Chrono)
- **시뮬레이션 대상 3가지**:
  - **로버**: Curiosity/Viper 등 탐사 로버 — Chrono::Vehicle/Robot 내장 모델 활용
  - **드론**: UAV 멀티콥터 — Chrono에 전용 모듈 없음 → ChBody + 조인트 + 모터 + Force Functor로 직접 구성
  - **환경**: 지형(RigidTerrain, SCMTerrain, 높이맵) + 외력(바람, 중력 변화, 온도)
- **최종 산출물**: 파라미터를 입력받아 시뮬레이션을 자동 실행하고, 결과(궤적/힘/토크 CSV, 형상 Mesh, 설정 JSON)를 출력하는 파이프라인

### 캡스톤 일정

| 기간 | Phase | 목표 | 상태 |
|------|-------|------|------|
| 1학기 Week 1~2 (3월) | Phase 1: 기초 | 물리 세계 생성, 충돌, 재질 | ✅ 완료 |
| 1학기 Week 3~6 (3~4월) | Phase 2: 메커니즘 | 조인트, 스프링, 모터, 기어 | 🔄 진행 중 |
| 1학기 Week 7~14 (5~6월) | Phase 3: 응용 | 로버 → 드론 → 환경 순차 학습 | 📋 예정 |
| 2학기 (9~12월) | Phase 4: 자동화 파이프라인 | 파라미터화, 배치 실행, 데이터 출력 | 📋 예정 |

---

## 1. Project Chrono란?

Project Chrono는 **멀티바디 물리 시뮬레이션 엔진**입니다.

쉽게 말하면, 현실 세계의 물리 법칙(중력, 충돌, 마찰, 관성 등)을 컴퓨터 안에서 재현하는 소프트웨어입니다.

### 어디에 쓰이나요?

| 분야 | 예시 |
|------|------|
| 자동차 공학 | 차량 주행 시뮬레이션, 서스펜션 테스트 |
| 로봇 공학 | 로봇 팔 동작 시뮬레이션, 보행 로봇 |
| 토목/건축 | 구조물 진동 해석 |
| 우주/항공 | 위성 전개 메커니즘 시뮬레이션 |
| 게임/영화 | 물리 기반 애니메이션 |
| 자율주행 | 센서 시뮬레이션 (카메라, LiDAR) |

### 핵심 개념 5가지

```
1. System (시스템)     → 시뮬레이션 세계 전체를 담는 그릇
2. Body (물체)        → 시뮬레이션 속 강체 (상자, 구, 실린더 등)
3. Link/Joint (조인트) → 물체끼리 연결하는 관절/구속 조건
4. Force (힘)         → 중력, 스프링, 모터 등 물체에 작용하는 힘
5. Solver (솔버)      → 물리 방정식을 풀어 다음 상태를 계산하는 엔진
```

---

## 2. 설치 가이드

자신의 환경에 맞는 섹션을 따라가세요.

### 2-A. 공통 사전 준비

어떤 OS든 아래 소프트웨어가 필요합니다:

| 도구 | 용도 | 다운로드 |
|------|------|----------|
| **Git** | 소스 코드 다운로드 | https://git-scm.com/downloads |
| **Anaconda/Miniconda** | Python 환경 관리 | https://www.anaconda.com/download 또는 https://docs.conda.io/en/latest/miniconda.html |
| **CMake** (3.28+) | 빌드 설정 도구 (소스 빌드 시만) | https://cmake.org/download/ |
| **C++ 컴파일러** | Chrono 빌드 (소스 빌드 시만) | Windows: Visual Studio / Linux: GCC / macOS: Xcode CLT |

> **Windows 사용자**: conda로 PyChrono를 바로 설치할 수 있어 CMake/C++ 컴파일러가 필요 없습니다. (→ 2-B 방법 A 참고)

#### conda 환경 생성 (모든 OS 공통, 가장 먼저!)

```bash
conda create -n chrono python=3.12 numpy -y
conda activate chrono
```

> **왜 conda 환경을 쓰나요?**
> PyChrono는 빌드 시 사용된 Python 버전에 종속됩니다. 시스템 Python 버전은 OS마다 다르고,
> Homebrew/apt 업데이트로 바뀔 수 있어서 팀원 간 충돌이 생깁니다.
> conda로 Python 3.12를 고정하면 모든 OS에서 동일하게 동작합니다.
>
> **주의:** conda 환경에서는 `python3`가 아닌 **`python`** 명령어를 사용하세요.
> `python3`는 시스템 Python을 가리킬 수 있어 버전 불일치로 segfault가 발생합니다.

---

### 2-B. Windows 설치

Windows에서는 **두 가지 방법**으로 설치할 수 있습니다:

| | 방법 A: conda 설치 (권장) | 방법 B: 소스 빌드 (고급) |
|---|---|---|
| 난이도 | 쉬움 (명령어 3줄) | 어려움 (CMake + Visual Studio) |
| 소요 시간 | 약 5분 | 30분~1시간 |
| 필요 도구 | Anaconda만 | Visual Studio, CMake, SWIG, Eigen |
| 포함 모듈 | Core, Irrlicht, Vehicle, Robot, FEA | 모든 모듈 선택 가능 |
| GPU 모듈 (DEM/FSI) | 미포함 | CUDA 있으면 가능 |
| VSG (Vulkan 시각화) | 미포함 | 빌드 가능 |

> **Phase 1~3 학습에는 방법 A로 충분합니다.** GPU 모듈이나 VSG가 필요해지면 그때 방법 B를 시도하세요.

---

#### 방법 A: conda로 설치 (권장)

CMake, Visual Studio, C++ 컴파일러 모두 필요 없습니다.

##### Step 1: Anaconda 설치

- https://www.anaconda.com/download 에서 다운로드 및 설치

##### Step 2: PyChrono 설치

Anaconda Prompt를 열고:

```powershell
conda create -n chrono python=3.12 -c conda-forge -y
conda activate chrono
conda install projectchrono::pychrono -c conda-forge
```

> **주의**: `pip install pychrono`는 완전히 다른 패키지입니다. 반드시 위의 conda 명령어를 사용하세요.

##### Step 3: 설치 확인

```powershell
conda activate chrono
python -c "import pychrono; print('PyChrono OK')"
python -c "import pychrono.irrlicht; print('Irrlicht OK')"
python -c "import pychrono.vehicle; print('Vehicle OK')"
```

세 줄 모두 에러 없이 출력되면 설치 완료입니다.

##### Step 4: 레슨 실행

```powershell
conda activate chrono
python lessons/phase1/lesson_01_hello_chrono.py
```

> **Chrono 데이터 파일 경로**: conda 설치의 경우 데이터 파일이 conda 환경 안에 포함되어 있어
> `chrono.SetChronoDataPath()`를 별도로 설정하지 않아도 됩니다.

---

#### 방법 B: 소스 빌드 (고급)

> GPU 모듈(DEM, FSI)이나 VSG 시각화가 필요할 때, 또는 최신 개발 버전을 쓰고 싶을 때 사용합니다.

##### Step 1: 필수 도구 설치

1. **Visual Studio 2022** (Community, 무료)
   - https://visualstudio.microsoft.com/ko/downloads/
   - 설치 시 **"C++를 사용한 데스크톱 개발"** 워크로드 선택

2. **CMake**
   - https://cmake.org/download/ → Windows x64 Installer
   - 설치 시 **"Add CMake to the system PATH"** 체크

3. **Git**
   - https://git-scm.com/download/win

4. **Anaconda** (Python 환경 관리)
   - https://www.anaconda.com/download
   - 설치 후: `conda create -n chrono python=3.12 numpy -y`

5. **SWIG** (PyChrono 빌드 시 필요)
   - https://www.swig.org/download.html → swigwin 다운로드
   - 압축 풀고 경로를 환경변수 `PATH`에 추가

##### Step 2: Chrono 소스 및 Eigen3 다운로드

```powershell
cd C:\Users\%USERNAME%\Documents
git clone https://github.com/projectchrono/chrono.git
git clone --branch 3.4.0 https://gitlab.com/libeigen/eigen.git eigen3
mkdir chrono_build
```

##### Step 3: CMake 설정

> **중요**: Anaconda Prompt에서 `conda activate chrono`를 먼저 실행한 상태에서 진행하세요.

window에서 고생중인 누군가가 미래에 다운받을 당신을 위해 남기는 글: 아래 B-1 실행전에 반드시 irrlicht-1.8.5가 documents 폴더에 있는지 확인하고 없으면 직접 사이트 들어가서 다운로드 하고 압축을 푼 뒤 실행시켜야 합니다-J. KIm
1. irrlicht 직접 다운로드 후 압축을 documents에 풀기
2. chrono_build 하위에 있는 모든 파일 삭제
3. 아래 코드를 입력하여 swig 다운로드(만약 없다면)
4. ```powershell
   conda install -c conda-forge swig
   ```
5. B-1A 실행 (실행후 --Found Irrlicht 확인 되어야 함)
6. 확인 후 다음 코드 실행
7. ```powershell
   cmake --build . --config Release --target install
   '''

**방법 B-1A(학교 컴퓨터에 설치시 26.03.24): 커맨드라인 (복사-붙여넣기로 간편)**

```powershell
cd C:\Users\%USERNAME%\Documents\chrono_build
cmake -G "Visual Studio 18 2026" ^
  -DCMAKE_INSTALL_PREFIX="C:/Users/user/Documents/chrono_install" ^
  -DEIGEN3_INCLUDE_DIR="C:/Users/user/Documents/eigen3" ^
  -DIrrlicht_ROOT="C:/Users/user/Documents/irrlicht-1.8.5" ^
  -DIRRLICHT_INCLUDE_DIR="C:/Users/user/Documents/irrlicht-1.8.5/include" ^
  -DIRRLICHT_LIBRARY="C:/Users/user/Documents/irrlicht-1.8.5/lib/Win64-visualStudio/Irrlicht.lib" ^
  -DSWIG_EXECUTABLE="C:/Users/user/anaconda3/envs/chrono/Library/bin/swig.exe" ^
  -DCH_ENABLE_MODULE_IRRLICHT:BOOL=ON ^
  -DCH_ENABLE_MODULE_VEHICLE:BOOL=ON ^
  -DCH_ENABLE_MODULE_POSTPROCESS:BOOL=ON ^
  -DCH_ENABLE_MODULE_PYTHON:BOOL=ON ^
  -DBUILD_DEMOS:BOOL=ON ^
  "C:/Users/user/Documents/chrono"
```

**방법 B-1: 커맨드라인 (복사-붙여넣기로 간편)**

```powershell
cd C:\Users\%USERNAME%\Documents\chrono_build
cmake -G "Visual Studio 17 2022" ^
  -DCMAKE_INSTALL_PREFIX=..\chrono_install ^
  -DEIGEN3_INCLUDE_DIR=..\eigen3 ^
  -DCH_ENABLE_MODULE_IRRLICHT:BOOL=ON ^
  -DCH_ENABLE_MODULE_VEHICLE:BOOL=ON ^
  -DCH_ENABLE_MODULE_POSTPROCESS:BOOL=ON ^
  -DCH_ENABLE_MODULE_PYTHON:BOOL=ON ^
  -DBUILD_DEMOS:BOOL=ON ^
  ..\chrono
```

**방법 B-2: CMake GUI (변수를 눈으로 확인하고 싶을 때)**

1. **CMake GUI** 실행 (`cmake-gui`)
2. Source 경로: `C:/Users/사용자명/Documents/chrono`
3. Build 경로: `C:/Users/사용자명/Documents/chrono_build`
4. **Configure** 클릭 → Generator: **Visual Studio 17 2022** 선택
5. 아래 항목 설정:

| CMake 변수 | 값 |
|------------|-----|
| `CMAKE_INSTALL_PREFIX` | `C:/Users/사용자명/Documents/chrono_install` |
| `EIGEN3_INCLUDE_DIR` | `C:/Users/사용자명/Documents/eigen3` |
| `CH_ENABLE_MODULE_IRRLICHT` | `ON` |
| `CH_ENABLE_MODULE_VEHICLE` | `ON` |
| `CH_ENABLE_MODULE_POSTPROCESS` | `ON` |
| `CH_ENABLE_MODULE_PYTHON` | `ON` |
| `BUILD_DEMOS` | `ON` |

> **Irrlicht**: Configure 후 자동으로 다운로드됩니다. 안 되면 수동으로:
> https://irrlicht.sourceforge.io/downloads/ → irrlicht-1.8.5 다운로드 후 경로 지정

6. **Configure** 다시 클릭 → 오류 없으면 **Generate** 클릭
7. **Open Project** 클릭 → Visual Studio 열림

##### Step 4: 빌드

- Visual Studio에서 상단 드롭다운을 **Release**로 변경
- 메뉴 → **빌드** → **솔루션 빌드** (Ctrl+Shift+B)
- 빌드 완료까지 10~30분 소요

##### Step 5: 환경 변수 설정

Anaconda Prompt에서 매 세션마다:
```powershell
conda activate chrono
$env:PYTHONPATH = "C:\Users\사용자명\Documents\chrono_build\bin\Release"
$env:PATH += ";C:\Users\사용자명\Documents\chrono_build\bin\Release"
```

##### Step 6: 설치 확인

```powershell
conda activate chrono
python -c "import pychrono; print('PyChrono OK')"
```

---

### 2-C. Linux (Ubuntu/Debian) 설치

#### Step 1: 시스템 패키지 설치

```bash
sudo apt-get update
sudo apt-get install -y \
  build-essential cmake cmake-curses-gui \
  libeigen3-dev libglew-dev libglfw3-dev libglm-dev freeglut3-dev \
  libirrlicht-dev ninja-build swig python3-dev git
```

#### Step 2: Chrono 소스 다운로드

```bash
cd ~/Documents
mkdir Project_Chrono_Practice && cd Project_Chrono_Practice
git clone https://github.com/projectchrono/chrono.git
mkdir chrono_build
```

#### Step 3: CMake 설정 및 빌드

```bash
conda activate chrono    # 반드시 conda 환경에서 빌드!

cd chrono_build
cmake -G "Ninja" \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX=../chrono_install \
  -DEIGEN3_INCLUDE_DIR=/usr/include/eigen3 \
  -DCH_ENABLE_MODULE_IRRLICHT:BOOL=ON \
  -DIrrlicht_ROOT=/usr \
  -DCH_ENABLE_MODULE_POSTPROCESS:BOOL=ON \
  -DCH_ENABLE_MODULE_VEHICLE:BOOL=ON \
  -DCH_ENABLE_MODULE_PYTHON:BOOL=ON \
  -DBUILD_DEMOS:BOOL=ON \
  ../chrono

ninja -j$(nproc)
```

#### Step 4: 환경 설정

```bash
# 매 세션마다 실행:
conda activate chrono
source setup_chrono_env.sh
```

> **Anaconda 사용자 주의**: libstdc++ 충돌이 발생하면 아래 추가:
> ```bash
> export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6
> ```
> 이 프로젝트의 `setup_chrono_env.sh`에 이미 포함되어 있습니다.

#### Step 5: 설치 확인

```bash
conda activate chrono
source setup_chrono_env.sh
python -c "import pychrono; print('PyChrono OK')"
```

---

### 2-D. macOS 설치 (Intel / Apple Silicon M1~M4)

> macOS에서는 CUDA가 지원되지 않으므로 GPU 모듈(DEM, FSI-SPH, Sensor)은 사용할 수 없습니다.
> 그 외 Core, Vehicle, FEA, Irrlicht 등 대부분의 모듈은 정상 동작합니다.

#### Step 1: Xcode Command Line Tools + Homebrew

```bash
# Xcode CLI 도구 (컴파일러 포함)
xcode-select --install

# Homebrew 설치 (없는 경우)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### Step 2: 의존성 설치

```bash
brew install cmake ninja eigen irrlicht libomp swig python3 git
```

#### Step 3: Chrono 소스 다운로드

```bash
cd ~/Documents
mkdir Project_Chrono_Practice && cd Project_Chrono_Practice
git clone https://github.com/projectchrono/chrono.git
mkdir chrono_build
```

#### Step 4: CMake 설정 및 빌드

```bash
conda activate chrono    # 반드시 conda 환경에서 빌드!
HOMEBREW_PREFIX=$(brew --prefix)

cd chrono_build
cmake -G "Ninja" \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX=../chrono_install \
  -DEIGEN3_INCLUDE_DIR=$(brew --prefix eigen)/include/eigen3 \
  -DCH_ENABLE_MODULE_IRRLICHT:BOOL=ON \
  -DIrrlicht_ROOT=$(brew --prefix irrlicht) \
  -DCH_ENABLE_MODULE_POSTPROCESS:BOOL=ON \
  -DCH_ENABLE_MODULE_VEHICLE:BOOL=ON \
  -DCH_ENABLE_MODULE_PYTHON:BOOL=ON \
  -DOpenMP_CXX_FLAGS="-Xclang -fopenmp" \
  -DOpenMP_CXX_LIB_NAMES="libomp" \
  -DOpenMP_libomp_LIBRARY="${HOMEBREW_PREFIX}/opt/libomp/lib/libomp.dylib" \
  -DBUILD_DEMOS:BOOL=ON \
  ../chrono

ninja -j$(sysctl -n hw.ncpu)
```

> **Apple Silicon 참고**: M1/M2/M3/M4 칩에서 Intel MKL, MATLAB, Pardiso MKL 솔버는 사용 불가합니다.
> Irrlicht 시각화는 정상 작동합니다.

#### Step 5: 환경 설정

```bash
# 매 세션마다 실행:
conda activate chrono
source setup_chrono_env.sh
```

#### Step 6: 설치 확인

```bash
conda activate chrono
source setup_chrono_env.sh
python -c "import pychrono; print('PyChrono OK')"
```

#### macOS에서 사용 가능/불가능한 모듈

| 사용 가능 | 사용 불가 (CUDA 필요) |
|-----------|----------------------|
| Core, FEA, Vehicle | DEM (이산요소법) |
| Irrlicht (3D 시각화) ※ | FSI-SPH (유체-구조) |
| Postprocess, Robot | Sensor (OptiX 레이트레이싱) |
| PyChrono, Multicore | Pardiso MKL (Apple Silicon) |

> ※ **macOS Irrlicht 제한사항:**
> - OpenGL 폴백으로 동작 (정상)
> - Retina 디스플레이에서 렌더링이 창의 1/4만 채워짐 (Irrlicht HiDPI 미지원)
> - vsync가 안 걸리므로 코드에 `ChRealtimeStepTimer` 필수
> - 창 크기 1280x720 초과 시 segfault 가능

---

### 2-E. GPU/CUDA 모듈 설치 (선택사항, Linux/Windows만 해당)

> **필요 조건**: NVIDIA GPU + CUDA Toolkit (macOS에서는 사용 불가)
> **GPU가 없어도** Core, Irrlicht, Vehicle, FEA 등 대부분의 기능은 정상 동작합니다.
> GPU 모듈은 대규모 입자 시뮬레이션이나 유체-구조 상호작용 등에서 필요합니다.

#### 언제 GPU가 필요한가?

| 모듈 | GPU 필요? | 용도 |
|------|-----------|------|
| Core, Vehicle, FEA, Robot | 불필요 | 기본 물리 시뮬레이션 |
| Irrlicht (시각화) | 불필요 | 3D 렌더링 (CPU로 충분) |
| **DEM** | **CUDA 필수** | GPU 가속 입자/과립 시뮬레이션 |
| **FSI-SPH** | **CUDA 필수** | 유체-구조 상호작용 (SPH) |
| **Sensor** | **CUDA 선택** | 카메라/LiDAR 센서 (OptiX 레이트레이싱) |
| Multicore | 불필요 | CPU 멀티코어 병렬 연산 |

#### CUDA Toolkit 설치

**Windows:**
1. https://developer.nvidia.com/cuda-downloads 에서 다운로드
2. CUDA Toolkit 12.8 이상 권장
3. 설치 후 `nvcc --version`으로 확인

**Linux (Ubuntu 24.04):**
```bash
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get install -y cuda-toolkit-12-8
# 터미널 재시작 후:
export PATH=/usr/local/cuda-12.8/bin:$PATH
nvcc --version
```

#### CUDA 모듈 활성화하여 재빌드

CMake에 아래 옵션을 추가합니다:

```
-DCH_ENABLE_MODULE_DEM:BOOL=ON
-DCH_ENABLE_MODULE_FSI:BOOL=ON
-DCH_ENABLE_MODULE_FSI_SPH:BOOL=ON
```

**Linux 전체 명령어:**
```bash
cd chrono_build
cmake -G "Ninja" \
  -DCMAKE_BUILD_TYPE=Release \
  -DEIGEN3_INCLUDE_DIR=/usr/include/eigen3 \
  -DCH_ENABLE_MODULE_IRRLICHT:BOOL=ON \
  -DCH_ENABLE_MODULE_VEHICLE:BOOL=ON \
  -DCH_ENABLE_MODULE_POSTPROCESS:BOOL=ON \
  -DCH_ENABLE_MODULE_PYTHON:BOOL=ON \
  -DCH_ENABLE_MODULE_DEM:BOOL=ON \
  -DCH_ENABLE_MODULE_FSI:BOOL=ON \
  -DCH_ENABLE_MODULE_FSI_SPH:BOOL=ON \
  -DBUILD_DEMOS:BOOL=ON \
  ../chrono

ninja -j$(nproc)
```

**Windows (CMake GUI):** 위와 동일한 옵션을 체크박스로 켜면 됩니다.

---

### 2-F. VSG 시각화 모듈 설치 (선택사항, macOS 권장)

> **VSG(Vulkan Scene Graph)**는 Vulkan 기반의 고품질 시각화 모듈입니다.
> macOS에서 Irrlicht의 OpenGL 폴백 제한(Retina 1/4 렌더링, 선 렌더링 안 됨, vsync 미지원)을
> 해결할 수 있습니다. **Windows/Linux에서도 사용 가능**하지만, Irrlicht만으로도 충분합니다.
>
> **팀원 영향 없음**: VSG는 선택적 추가 모듈로, 기존 Irrlicht 코드에 영향을 주지 않습니다.

#### Step 1: Vulkan SDK 설치

**macOS:**
```bash
brew install vulkan-headers vulkan-loader vulkan-tools
```

**Linux:**
```bash
sudo apt-get install -y libvulkan-dev vulkan-tools
```

**Windows:**
- https://vulkan.lunarg.com/sdk/home 에서 VulkanSDK 설치

#### Step 2: VSG 라이브러리 빌드

Chrono에서 제공하는 빌드 스크립트를 사용합니다:

```bash
mkdir -p /tmp/vsg_build && cd /tmp/vsg_build

# OS에 맞는 스크립트 복사
cp chrono/contrib/build-scripts/macos/buildVSG.sh .    # macOS
# cp chrono/contrib/build-scripts/linux/buildVSG.sh .   # Linux

bash buildVSG.sh   # ~/Packages/vsg/ 에 설치됨 (약 5~10분)
```

#### Step 3: Chrono 재빌드 (VSG 모듈 활성화)

```bash
cd chrono_build
VSG_DIR="$HOME/Packages/vsg"

cmake \
  -DCH_ENABLE_MODULE_VSG:BOOL=ON \
  -Dvsg_DIR:PATH=${VSG_DIR}/lib/cmake/vsg \
  -DvsgImGui_DIR:PATH=${VSG_DIR}/lib/cmake/vsgImGui \
  -DvsgXchange_DIR:PATH=${VSG_DIR}/lib/cmake/vsgXchange \
  -Dglslang_DIR:PATH=${VSG_DIR}/lib/cmake/glslang \
  .

ninja -j$(nproc)     # Linux
# ninja -j$(sysctl -n hw.ncpu)  # macOS
```

#### Step 4: 확인

```bash
conda activate chrono
source setup_chrono_env.sh
python -c "import pychrono.vsg3d; print('VSG OK')"
```

> **주의**: Python 모듈명은 `pychrono.vsg3d`입니다 (`pychrono.vsg`가 아님).

#### VSG vs Irrlicht 비교

| 항목 | Irrlicht | VSG |
|------|----------|-----|
| 텍스처/재질 렌더링 | macOS에서 제한적 | 정상 |
| Retina 디스플레이 | 1/4만 렌더링 | 전체 화면 정상 |
| 선(line) 기반 시각화 | macOS에서 안 됨 | 정상 |
| GUI 패널 (ImGui) | 없음 | 통합 지원 |
| 추가 빌드 필요? | 아니오 | 예 (선택사항) |
| 모든 OS 지원? | 예 | 예 |

---

### 2-G. PyChrono만 빠르게 설치 (conda, 모든 OS)

소스 빌드 없이 Python만 쓰고 싶다면 (Windows 방법 A와 동일):

```bash
conda create -n chrono python=3.12 -c conda-forge -y
conda activate chrono
conda install projectchrono::pychrono -c conda-forge
```

> **포함 모듈**: Core, Irrlicht, Vehicle, Robot, FEA, Postprocess
> **미포함**: VSG (Vulkan 시각화), GPU 모듈 (DEM, FSI, Sensor)
>
> **주의**: `pip install pychrono`는 완전히 다른 패키지입니다. 반드시 위의 conda 명령어를 사용하세요.

---

### 2-H. Docker로 설치 (고급, Linux/Windows)

```bash
docker pull uwsbel/projectchrono:latest
docker run -it uwsbel/projectchrono:latest
```

---

## 3. 학습 로드맵

### Phase 1: 기초 (Week 1~2) - "물리 세계 만들기"

| 순서 | 주제 | 배우는 것 |
|------|------|-----------|
| 01 | Hello Chrono | 시스템 생성, 물체 추가, 시뮬레이션 실행 |
| 02 | 중력과 자유낙하 | 중력 설정, 시간 스텝, 위치 추적 |
| 03 | 3D 시각화 | Irrlicht로 시뮬레이션을 눈으로 보기 |
| 04 | 다양한 형태의 물체 | 상자, 구, 실린더 만들기 |
| 05 | 충돌과 접촉 | 물체끼리 부딪히게 만들기 |
| 06 | 재질과 마찰 | 미끄러운 바닥 vs 거친 바닥 |

### Phase 2: 메커니즘 (Week 3~6) - "움직이는 기계 만들기"

| 순서 | 주제 | 배우는 것 |
|------|------|-----------|
| 07 | 회전 조인트 (Revolute) | 문의 경첩처럼 한 축으로 회전 |
| 08 | 진자 운동 | 실제 진자 시뮬레이션 |
| 09 | 스프링과 댐퍼 | 탄성체 연결, 감쇠 |
| 10 | 모터 구동 | 조인트에 모터를 달아 자동 회전 |
| 11 | 4절 링크 기구 | 크랭크-슬라이더 메커니즘 |
| 12 | 기어와 풀리 | 동력 전달 시스템 |

> **Phase 3 연결**: Phase 2의 조인트/모터/스프링은 로버와 드론 모델링의 공통 기반입니다.
> - 로버: 서스펜션 = 스프링-댐퍼, 바퀴 구동 = 모터 회전
> - 드론: 프로펠러 = 모터 + 회전 조인트, 랜딩기어 = 스프링-댐퍼

### Phase 3: 응용 (Week 7~14) - "로버 · 드론 · 환경 시뮬레이션"

| 순서 | 주제 | 배우는 것 |
|------|------|-----------|
| 13 | 로버 시뮬레이션 | Chrono::Vehicle/Robot의 Curiosity/Viper 로버 구동 |
| 14 | 로버 + 지형 상호작용 | RigidTerrain/SCMTerrain 위 로버 주행, 힘/토크 데이터 수집 |
| 15 | 드론 바디 모델링 | ChBody로 프레임+암 구성, 질량/관성 설정 |
| 16 | 프로펠러와 추력 | 모터 회전 + Force Functor로 추력 생성 |
| 17 | 드론 비행 역학 | 4프로펠러 추력 조합, 호버링/상승/하강/요 |
| 18 | 환경: 지형 모델링 | RigidTerrain(평탄), SCMTerrain(변형 토양), 높이맵 |
| 19 | 환경: 외력과 교란 | 바람(외력), 중력 변화(달/화성), 온도 파라미터 |
| 20 | 통합 시나리오 | 드론 + 로버 + 환경을 결합한 시뮬레이션 |

### Phase 4: 자동화 파이프라인 (2학기) - "온톨로지 연동"

| 순서 | 주제 | 배우는 것 |
|------|------|-----------|
| 21 | 파라미터화 시뮬레이션 | 드론/로버 파라미터를 외부 입력(JSON/YAML)으로 수신 |
| 22 | 배치 시뮬레이션 | 여러 시나리오 자동 실행, 결과 수집 |
| 23 | 데이터 출력 파이프라인 | CSV(궤적/힘), JSON(설정), Mesh(형상) 포맷 출력 |
| 24 | 온톨로지 연동 | 지식 레이어에서 파라미터 수신, 결과 RDF 변환 반환 |

---

## 4. 핵심 API 패턴 (Python)

모든 PyChrono 프로그램은 이 5단계 패턴을 따릅니다:

### 패턴 1: 시스템 생성

```python
import pychrono as chrono

# 물리 세계를 만든다
sys = chrono.ChSystemNSC()                                    # NSC = 비매끄러운 접촉 방식
sys.SetGravitationalAcceleration(chrono.ChVector3d(0, -9.81, 0))  # 중력 설정 (y축 아래)
```

> **NSC vs SMC**: 두 가지 접촉 모델이 있습니다
> - `ChSystemNSC` : Non-Smooth Contact. 빠르고 일반적. 대부분 이걸 사용
> - `ChSystemSMC` : Smooth Contact. 부드러운 접촉이 필요할 때 (고무, 타이어 등)

### 패턴 2: 물체 추가

```python
# 방법 A: 직접 생성 (세밀한 제어)
body = chrono.ChBody()
body.SetMass(10.0)                              # 질량 10kg
body.SetPos(chrono.ChVector3d(0, 5, 0))         # 위치: (x=0, y=5, z=0)
body.SetFixed(False)                            # 고정 안 함 (움직임)
sys.AddBody(body)

# 방법 B: 간편 생성 (형태+밀도로 자동 계산)
sphere = chrono.ChBodyEasySphere(0.5, 1000, True)  # 반지름 0.5m, 밀도 1000kg/m³, 시각화 ON
sys.AddBody(sphere)
```

### 패턴 3: 조인트/구속 추가

```python
# 회전 조인트 (경첩) 만들기
joint = chrono.ChLinkRevolute()
frame = chrono.ChFramed(chrono.ChVector3d(0, 0.5, 0))   # 조인트 위치
joint.Initialize(body_A, body_B, frame)                   # 두 물체를 연결
sys.Add(joint)
```

### 패턴 4: 3D 시각화 설정

> **모든 레슨에서 VSG/Irrlicht 자동 분기 패턴을 사용합니다.**
> VSG가 설치된 환경(macOS 권장)에서는 Vulkan 렌더링, 미설치 환경에서는 Irrlicht 폴백.

```python
# 시각화 시스템 자동 선택 (VSG 우선, Irrlicht 폴백)
try:
    import pychrono.vsg3d as chronovsg
    USE_VSG = True
except ImportError:
    USE_VSG = False
import pychrono.irrlicht as chronoirr

# 시각화 생성
if USE_VSG:
    vis = chronovsg.ChVisualSystemVSG()
else:
    vis = chronoirr.ChVisualSystemIrrlicht()

vis.AttachSystem(sys)                           # 시스템 연결
vis.SetWindowSize(1280, 720)                    # 창 크기
vis.SetWindowTitle('My Simulation')             # 창 제목

if USE_VSG:
    vis.AddCamera(chrono.ChVector3d(3, 3, 3))   # VSG: 카메라를 먼저 설정
    vis.Initialize()
else:
    vis.Initialize()
    vis.AddSkyBox()                              # 하늘 배경
    vis.AddCamera(chrono.ChVector3d(3, 3, 3))    # 카메라 위치
    vis.AddTypicalLights()                       # 조명
```

### 패턴 5: 시뮬레이션 루프

```python
# 시각화 있는 경우
while vis.Run():
    vis.BeginScene()
    vis.Render()
    vis.EndScene()
    sys.DoStepDynamics(0.005)  # 0.005초씩 시간 전진

# 시각화 없는 경우 (빠른 계산)
while sys.GetChTime() < 10.0:
    sys.DoStepDynamics(0.001)
    pos = body.GetPos()
    print(f"t={sys.GetChTime():.3f}  y={pos.y:.4f}")
```

---

## 5. 첫 번째 예제: 자유낙하 시뮬레이션

`lessons/lesson_01_hello_chrono.py` 파일이 이미 준비되어 있습니다.

**Linux / macOS:**
```bash
conda activate chrono          # conda로 빌드한 경우 반드시 먼저 활성화
source setup_chrono_env.sh
python lessons/phase1/lesson_01_hello_chrono.py
```

**Windows:**
```powershell
conda activate chrono          # conda로 빌드한 경우 반드시 먼저 활성화
# 환경변수 설정 후:
python lessons/phase1/lesson_01_hello_chrono.py
```

> **주의: `python3` 대신 `python`을 사용하세요!**
> conda 환경에서 `python3`는 시스템 Python(Homebrew 등)을 가리킬 수 있어
> 빌드에 사용된 Python 버전과 달라 segfault가 발생합니다.
> conda 환경 안에서는 항상 `python` 명령어를 사용하세요.

**예상 출력:**
```
물리 시스템 생성 완료!
  중력: -9.81 m/s²

공 생성 완료!
  질량: 1.0 kg
  초기 위치: y = 10.0 m

   시간(s)       높이(m)     속도(m/s)       이론높이(m)
────────────────────────────────────────────────
    0.20      9.7940     -1.9620        9.8038
    0.40      9.1956     -3.9240        9.2152
    ...
시뮬레이션 결과: y = -9.7181 m
이론값 (물리):   y = -9.6200 m
축하합니다! 첫 번째 물리 시뮬레이션을 완료했습니다!
```

---

## 6. 기존 데모 실행하기

Chrono 소스에는 400개 이상의 예제가 포함되어 있습니다.

### 추천 데모 (난이도순)

| 난이도 | 파일 | 설명 |
|--------|------|------|
| ★☆☆ | `python/core/demo_CH_buildsystem.py` | 기본 시스템 생성, 물체 추가 |
| ★☆☆ | `python/core/demo_CH_coords.py` | 좌표계와 변환 |
| ★★☆ | `python/mbs/demo_MBS_revolute.py` | 회전 조인트 (3D 시각화) |
| ★★☆ | `python/mbs/demo_MBS_spring.py` | 스프링-댐퍼 시스템 |
| ★★☆ | `python/mbs/demo_MBS_collision_2d.py` | 2D 충돌 시뮬레이션 |
| ★★★ | `python/vehicle/demo_VEH_HMMWV.py` | HMMWV 차량 주행 |
| ★★★ | `python/robot/demo_ROBOT_Curiosity_Rigid.py` | 화성 탐사 로버 |

### 실행 방법

**Linux / macOS:**
```bash
conda activate chrono
source setup_chrono_env.sh
python chrono/src/demos/python/mbs/demo_MBS_revolute.py
```

**Windows:**
```powershell
conda activate chrono
python chrono\src\demos\python\mbs\demo_MBS_revolute.py
```

---

## 7. 좌표계와 단위

Project Chrono는 **SI 단위계**를 사용합니다:

| 물리량 | 단위 | 예시 |
|--------|------|------|
| 길이 | 미터 (m) | `ChVector3d(1, 0, 0)` = 1m |
| 질량 | 킬로그램 (kg) | `SetMass(10)` = 10kg |
| 시간 | 초 (s) | `DoStepDynamics(0.01)` = 10ms |
| 힘 | 뉴턴 (N) | F = ma |
| 각도 | 라디안 (rad) | 180도 = 3.14159 rad |

### 좌표계 (오른손 법칙)

```
    Y (위)
    |
    |
    +------→ X (오른쪽)
   /
  Z (앞, 화면 밖으로)
```

- `ChVector3d(x, y, z)` : 3D 위치/방향 벡터
- `ChQuaterniond(w, x, y, z)` : 회전을 나타내는 쿼터니언
- `ChFramed(위치, 회전)` : 위치 + 방향 = 좌표 프레임

---

## 8. 주요 클래스 사전

### 물체 (Body)

| 클래스 | 용도 |
|--------|------|
| `ChBody` | 기본 강체 (위치, 질량, 관성 직접 설정) |
| `ChBodyEasyBox(x,y,z, 밀도, 시각화)` | 상자 형태 간편 생성 |
| `ChBodyEasySphere(반지름, 밀도, 시각화)` | 구 형태 간편 생성 |
| `ChBodyEasyCylinder(반지름, 높이, 밀도, 시각화)` | 실린더 간편 생성 |
| `ChBodyAuxRef` | 무게중심과 기준점이 다른 물체 |

### 조인트/링크 (Joint/Link)

| 클래스 | 자유도 | 실제 예시 |
|--------|--------|-----------|
| `ChLinkRevolute` | 회전 1축 | 문 경첩 |
| `ChLinkSpherical` | 회전 3축 | 볼 조인트 |
| `ChLinkPrismatic` | 직선 1축 | 서랍 레일 |
| `ChLinkLockLock` | 고정 0 | 용접 |
| `ChLinkTSDA` | 스프링-댐퍼 | 자동차 서스펜션 |
| `ChLinkMotorRotationSpeed` | 모터 | 전동기 |

### 시스템 (System)

| 클래스 | 용도 |
|--------|------|
| `ChSystemNSC` | 비매끄러운 접촉 (일반적, 빠름) |
| `ChSystemSMC` | 매끄러운 접촉 (정밀, 느림) |

---

## 9. 문제 해결 (Troubleshooting)

### 공통

| 증상 | 원인 | 해결 |
|------|------|------|
| `ModuleNotFoundError: No module named 'pychrono'` | PYTHONPATH 미설정 | 환경변수에 빌드 디렉토리 추가 |
| `segmentation fault` (segfault) | `python3`가 빌드와 다른 Python 버전을 가리킴 | `python3` 대신 **`python`** 사용, conda 환경 활성화 확인 |
| `ModuleNotFoundError: No module named 'numpy'` + segfault | 시스템 Python에 numpy 미설치 | conda 환경에서 `python`으로 실행 (`.venv` 비활성화) |
| 데이터 파일을 못 찾음 | 데이터 경로 미설정 | 코드에 `chrono.SetChronoDataPath(...)` 추가 |
| Irrlicht 창이 안 열림 | GUI 환경 없음 | X11/데스크톱 환경에서 실행 |

### Linux 전용

| 증상 | 원인 | 해결 |
|------|------|------|
| `GLIBCXX_3.4.32 not found` | Anaconda libstdc++ 충돌 | `source setup_chrono_env.sh` 실행 |
| `libGL error` | 그래픽 드라이버 문제 | `sudo apt install mesa-utils` |

### macOS 전용

| 증상 | 원인 | 해결 |
|------|------|------|
| `ld: library not found for -lomp` | OpenMP 미설치 | `brew install libomp` |
| CMake에서 OpenMP 못 찾음 | Apple clang 기본 미포함 | CMake에 `-DOpenMP_CXX_FLAGS="-Xclang -fopenmp"` 추가 |
| `dyld: Library not loaded` | DYLD_LIBRARY_PATH 미설정 | `source setup_chrono_env.sh` 실행 |
| Irrlicht 관련 오류 | Homebrew 경로 문제 | `-DIrrlicht_ROOT=$(brew --prefix irrlicht)` 확인 |
| Irrlicht 렌더링이 창의 1/4만 채움 | Retina 디스플레이 HiDPI 미지원 | Irrlicht 알려진 제한사항, 기능은 정상 동작 |
| `Cannot use default video driver - fall back to OpenGL` | macOS 기본 드라이버 미지원 | 정상 동작, OpenGL 폴백은 예상된 것 |
| 시뮬레이션이 순식간에 끝남 (애니메이션 안 보임) | macOS OpenGL에서 vsync 미지원 | `ChRealtimeStepTimer` 사용 (코드 참고) |
| Irrlicht 창 크기 크게 설정 시 segfault | OpenGL 폴백의 해상도 제한 | 창 크기를 1280x720 이하로 설정 |
| 스프링 코일(`ChVisualShapeSpring`)이 안 보임 | OpenGL 폴백에서 선(line) 렌더링 미지원 | 작은 구 마커 체인으로 대체하여 시각화 |
| matplotlib 그래프가 빈 화면만 표시 | Irrlicht 종료 후 GUI 백엔드 충돌 | `matplotlib.use('Agg')` 설정 후 `plt.savefig()`로 PNG 저장 |
| matplotlib에서 한글 깨짐 (Glyph missing 경고) | 기본 폰트(DejaVu Sans)가 한글 미지원 | 그래프 라벨은 영어로 작성 |

### Windows 전용

| 증상 | 원인 | 해결 |
|------|------|------|
| DLL not found | PATH에 빌드 디렉토리 없음 | bin/Release 폴더를 PATH에 추가 |
| CMake에서 Eigen 못 찾음 | 경로 오류 | `EIGEN3_INCLUDE_DIR`을 정확히 지정 |
| SWIG 오류 | SWIG 미설치 또는 PATH 없음 | SWIG 설치 후 PATH 추가 |

---

## 10. 참고 자료

| 자료 | 링크 |
|------|------|
| 공식 API 문서 | https://api.projectchrono.org/ |
| 공식 홈페이지 | https://projectchrono.org/ |
| GitHub 저장소 | https://github.com/projectchrono/chrono |
| 설치 가이드 (공식) | https://api.projectchrono.org/tutorial_install_chrono.html |
| PyChrono conda | `conda install -c conda-forge -c projectchrono pychrono` |
| 다운로드 페이지 | https://projectchrono.org/download/ |

소스 빌드 후 사용 가능한 로컬 자료:

| 자료 | 경로 |
|------|------|
| 매뉴얼 (마크다운) | `chrono/doxygen/documentation/manuals/chrono/` |
| Python 데모 109개 | `chrono/src/demos/python/` |
| C++ 데모 182개 | `chrono/src/demos/` |
| 차량 모델 데이터 | `chrono/data/vehicle/` |
| 로봇 모델 데이터 | `chrono/data/robot/` |

---

## 11. 프로젝트 디렉토리 구조

```
Project_Chrono_Practice/
│
├── lessons/                         # [학습] 우리가 작성하는 학습 코드
│   ├── phase1/                      #   Phase 1: 기초 (lesson 01~06)
│   ├── phase2/                      #   Phase 2: 메커니즘 (lesson 07~12)
│   ├── phase3/                      #   Phase 3: 로버/드론/환경 (lesson 13~20)
│   ├── phase4/                      #   Phase 4: 자동화 파이프라인 (lesson 21~24, 2학기)
│   └── extras/                      #   보너스 예제 (로드맵 외)
│
├── chrono/                          # [소스] Chrono 엔진 (git clone, .gitignore됨)
│   ├── src/demos/python/            #   Python 데모 예제들
│   └── data/                        #   모델, 텍스쳐 데이터
│
├── chrono_build/                    # [빌드] 컴파일 결과물 (.gitignore됨)
│   ├── bin/pychrono/                #   PyChrono 모듈
│   └── lib/                         #   공유 라이브러리
│
├── setup_chrono_env.sh              # Linux/macOS 환경 설정 스크립트
├── requirements.txt                 # Python 추가 패키지
├── CLAUDE.md                        # Claude AI 작업 지침
├── README.md                        # 이 파일 (학습 가이드)
└── .gitignore                       # Git 제외 목록
```

> `chrono/`와 `chrono_build/`는 용량이 크므로 Git에 포함되지 않습니다.
> 각 멤버가 자신의 환경에서 직접 빌드해야 합니다.

---

## 12. 플랫폼별 모듈 호환성

| 모듈 | Linux | Windows | macOS Intel | macOS Apple Silicon |
|------|:-----:|:-------:|:-----------:|:-------------------:|
| Core (물리 엔진) | O | O | O | O |
| Irrlicht (3D 시각화) | O | O | O※ | O※ |
| **VSG (Vulkan 시각화)** | **O** | **O** | **O** | **O** |
| Vehicle (차량) | O | O | O | O |
| FEA (유한요소) | O | O | O | O |
| Robot (로봇) | O | O | O | O |
| Postprocess (후처리) | O | O | O | O |
| PyChrono (Python) | O | O | O | O |
| Multicore (병렬) | O | O | O | O |
| **DEM (GPU 입자)** | **O*** | **O*** | X | X |
| **FSI-SPH (GPU 유체)** | **O*** | **O*** | X | X |
| **Sensor (GPU 센서)** | **O*** | **O*** | X | X |
| Pardiso MKL (솔버) | O | O | O | X |

**O*** = NVIDIA GPU + CUDA Toolkit 필요
**O※** = macOS에서 OpenGL 폴백으로 동작 (Retina/선 렌더링 제한 → VSG 권장)

> **GPU가 없어도 걱정 마세요!**
> Phase 1~3의 모든 학습 과정(물리 기초, 메커니즘, 드론/로버/환경)은
> GPU 없이도 완벽하게 수행할 수 있습니다.
> GPU 모듈은 대규모 입자(DEM), 유체(FSI) 시뮬레이션에서만 필요합니다.
