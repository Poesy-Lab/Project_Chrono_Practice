# CLAUDE.md - Project Chrono 학습 프로젝트

## 프로젝트 개요
이 프로젝트는 Project Chrono(멀티바디 물리 시뮬레이션 엔진)를 **완전 초보자** 팀이 학습하기 위한 공간입니다.
GitHub로 팀원 간 공유되며, 멤버들은 다양한 환경(Windows/Linux/macOS, GPU 유무)을 사용합니다.
**팀원의 사전 지식**: 물리 시뮬레이션, C++/Python 엔지니어링 소프트웨어에 대한 경험 없음.

---

## Python 환경 규칙 (중요!)

- **모든 OS에서 conda 환경 `chrono`를 사용합니다** (Python 버전 통일을 위해).
- 레슨 실행 시 반드시 `conda activate chrono` 후 `python` 명령어를 사용합니다.
- **`python3` 명령어를 사용하지 마세요** — 시스템 Python을 가리켜 버전 불일치/segfault가 발생합니다.
- `.venv` 등 다른 가상환경과 혼용하지 마세요.
- conda 환경 생성: `conda create -n chrono python=3.11 numpy -y`

```bash
# 모든 OS 공통 실행 방법
conda activate chrono
source setup_chrono_env.sh   # Linux/macOS만
python lessons/lesson_XX_주제.py
```

---

## 자동 환경 감지 및 설치 가이드

> **Claude Code가 이 파일을 읽고 있다면:**
> 아래 절차에 따라 사용자의 환경을 감지하고, Chrono가 아직 빌드되지 않았으면 설치를 안내/진행하세요.
> **빌드 전에 반드시 conda 환경 `chrono`를 생성/활성화하고 그 안에서 CMake를 실행하세요.**

### Step 0: conda 환경 생성
```bash
conda create -n chrono python=3.11 numpy -y
conda activate chrono
```

### Step 1: OS 감지
```bash
uname -s   # Linux / Darwin(macOS)
# Windows: systeminfo 또는 ver 명령으로 확인
```

### Step 2: 하드웨어 감지
```bash
# GPU 확인
nvidia-smi 2>/dev/null          # NVIDIA GPU (Linux/Windows)
system_profiler SPDisplaysDataType 2>/dev/null  # macOS GPU
# CPU/칩셋 확인
uname -m                        # x86_64 / arm64 (Apple Silicon)
lscpu 2>/dev/null || sysctl -n machdep.cpu.brand_string 2>/dev/null
```

### Step 3: 플랫폼별 설치 진행

#### Linux (Ubuntu/Debian)
```bash
# 필수 패키지
sudo apt-get install -y build-essential cmake cmake-curses-gui \
  libeigen3-dev libglew-dev libglfw3-dev libglm-dev freeglut3-dev \
  libirrlicht-dev ninja-build swig python3-dev git

# NVIDIA GPU가 있고 CUDA가 없으면:
# sudo apt-get install -y cuda-toolkit-12-8
# CMake에 -DCMAKE_CUDA_COMPILER=/usr/local/cuda/bin/nvcc 추가

# 빌드
mkdir -p chrono_build && cd chrono_build
cmake -G "Ninja" -DCMAKE_BUILD_TYPE=Release \
  -DEIGEN3_INCLUDE_DIR=/usr/include/eigen3 \
  -DCH_ENABLE_MODULE_IRRLICHT:BOOL=ON -DIrrlicht_ROOT=/usr \
  -DCH_ENABLE_MODULE_VEHICLE:BOOL=ON \
  -DCH_ENABLE_MODULE_POSTPROCESS:BOOL=ON \
  -DCH_ENABLE_MODULE_PYTHON:BOOL=ON \
  -DBUILD_DEMOS:BOOL=ON \
  ../chrono
# NVIDIA GPU + CUDA 있으면 추가: -DCH_ENABLE_MODULE_DEM:BOOL=ON -DCH_ENABLE_MODULE_FSI_SPH:BOOL=ON
ninja -j$(nproc)
```

#### macOS (Intel / Apple Silicon)
```bash
# Homebrew로 의존성 설치
brew install cmake ninja eigen irrlicht libomp swig python3

# OpenMP 경로 확인 (Apple clang은 기본 미포함)
HOMEBREW_PREFIX=$(brew --prefix)

# 빌드
mkdir -p chrono_build && cd chrono_build
cmake -G "Ninja" -DCMAKE_BUILD_TYPE=Release \
  -DEIGEN3_INCLUDE_DIR=$(brew --prefix eigen)/include/eigen3 \
  -DCH_ENABLE_MODULE_IRRLICHT:BOOL=ON \
  -DIrrlicht_ROOT=$(brew --prefix irrlicht) \
  -DCH_ENABLE_MODULE_VEHICLE:BOOL=ON \
  -DCH_ENABLE_MODULE_POSTPROCESS:BOOL=ON \
  -DCH_ENABLE_MODULE_PYTHON:BOOL=ON \
  -DOpenMP_CXX_FLAGS="-Xclang -fopenmp" \
  -DOpenMP_CXX_LIB_NAMES="libomp" \
  -DOpenMP_libomp_LIBRARY="${HOMEBREW_PREFIX}/opt/libomp/lib/libomp.dylib" \
  -DBUILD_DEMOS:BOOL=ON \
  ../chrono
# 주의: macOS에서는 CUDA/DEM/FSI-SPH/Sensor 모듈 사용 불가
ninja -j$(sysctl -n hw.ncpu)
```

#### Windows
```powershell
# 사전 설치: Visual Studio 2022 (C++ 워크로드), CMake, Git, Python, SWIG
# Eigen3: git clone --branch 3.4.0 https://gitlab.com/libeigen/eigen.git

mkdir chrono_build && cd chrono_build
cmake -G "Visual Studio 17 2022" ^
  -DEIGEN3_INCLUDE_DIR=C:/path/to/eigen3 ^
  -DCH_ENABLE_MODULE_IRRLICHT:BOOL=ON ^
  -DCH_ENABLE_MODULE_VEHICLE:BOOL=ON ^
  -DCH_ENABLE_MODULE_POSTPROCESS:BOOL=ON ^
  -DCH_ENABLE_MODULE_PYTHON:BOOL=ON ^
  -DBUILD_DEMOS:BOOL=ON ^
  ../chrono
# Visual Studio에서 Release로 빌드, 또는:
cmake --build . --config Release
# NVIDIA GPU + CUDA 있으면 추가: -DCH_ENABLE_MODULE_DEM:BOOL=ON -DCH_ENABLE_MODULE_FSI_SPH:BOOL=ON
```

### Step 4: 환경 변수 설정
- **Linux**: `source setup_chrono_env.sh`
- **macOS**: `source setup_chrono_env.sh`
- **Windows**: `PYTHONPATH`와 `PATH`에 `chrono_build\bin\Release` 추가

### Step 5: 레슨 실행
```bash
conda activate chrono
source setup_chrono_env.sh   # Linux/macOS
python lessons/lesson_01_hello_chrono.py
```

---

## 모듈 가용성 (플랫폼별)

| 모듈 | Linux | macOS (Intel) | macOS (Apple Silicon) | Windows |
|------|:-----:|:------------:|:--------------------:|:-------:|
| Core | O | O | O | O |
| Irrlicht (시각화) | O | O | O | O |
| Vehicle | O | O | O | O |
| Postprocess | O | O | O | O |
| FEA | O | O | O | O |
| Robot | O | O | O | O |
| PyChrono (SWIG) | O | O | O | O |
| Multicore (OpenMP) | O | O | O | O |
| DEM (CUDA) | O* | X | X | O* |
| FSI-SPH (CUDA) | O* | X | X | O* |
| Sensor (CUDA+OptiX) | O* | X | X | O* |
| Pardiso MKL | O | O | X | O |

*O* = NVIDIA GPU + CUDA Toolkit 필요

---

## 디렉토리 구조
```
Project_Chrono_Practice/
├── lessons/                 # 학습 코드 (Git 추적, 팀 공유)
├── chrono/                  # Chrono 소스 (각자 clone, Git 제외)
├── chrono_build/            # 빌드 결과물 (각자 빌드, Git 제외)
├── chrono_install/          # 설치 디렉토리 (Git 제외)
├── setup_chrono_env.sh      # Linux/macOS 환경 설정
├── CLAUDE.md                # 이 파일
├── README.md                # 학습 가이드
├── requirements.txt         # Python 의존성
├── .gitignore               # Git 제외 목록
└── .gitattributes           # 줄바꿈 통일
```

## 코딩 규칙
- 학습 코드는 `lessons/` 디렉토리에 작성
- 파일명: `lesson_XX_주제.py` 형식
- 각 레슨 파일 상단에 한글 주석으로 학습 목표, 실행 방법 명시
- GPU 필요 레슨: 파일명에 `_gpu` 접미사 (예: `lesson_16_dem_gpu.py`)
- **크로스 플랫폼**: 파일 경로는 `os.path.join()` 또는 `pathlib.Path` 사용, 절대 경로 하드코딩 금지
- 데이터 경로: `chrono.GetChronoDataPath()` 사용

## PyChrono API 주의사항
- `ChBody`에 `GetFixed()` 없음 → `SetFixed()`만 존재
- body 추가: `sys.AddBody(body)` 또는 `sys.Add(body)` 모두 가능
- 속도: `GetPosDt()`, 가속도: `GetPosDt2()`
- Linux Anaconda: `LD_PRELOAD` 필요 (setup_chrono_env.sh에 포함)

## macOS Irrlicht 시각화 주의사항
- macOS에서는 기본 비디오 드라이버 대신 **OpenGL 폴백**으로 동작함 (`Cannot use default video driver - fall back to OpenGL` 메시지 정상)
- **Retina 디스플레이**: 렌더링이 창의 왼쪽 아래 1/4만 채움 — Irrlicht가 macOS HiDPI를 지원하지 않는 알려진 제한사항 (코드로 해결 불가)
- **vsync 미지원**: macOS OpenGL 폴백에서는 vsync가 안 걸려서 시뮬레이션이 순식간에 끝남 → 반드시 `ChRealtimeStepTimer`를 사용하여 실시간 동기화 필요
- **창 크기 제한**: 1280x720 초과 시 segfault 발생 가능 (OpenGL 폴백 한계)
- **선(line) 기반 시각화 안 됨**: `ChVisualShapeSpring`, `ChVisualShapeSegment` 등 선으로 그리는 시각 요소가 macOS OpenGL 폴백에서 렌더링되지 않음 → 스프링 등은 작은 구(ChVisualShapeSphere) 마커 체인으로 대체
- **matplotlib + Irrlicht 충돌**: Irrlicht 창 종료 후 `plt.show()`가 빈 화면만 표시됨 → `matplotlib.use('Agg')`로 비대화형 백엔드 설정 후 `plt.savefig()`로 PNG 저장, `os.system("open ...")`으로 열기
- **matplotlib 한글 폰트**: 기본 폰트(DejaVu Sans)가 한글 미지원 → 그래프 라벨은 영어 사용
- 시각화 레슨 작성 시 반드시 아래 패턴 사용:
```python
realtime_timer = chrono.ChRealtimeStepTimer()
while vis.Run():
    vis.BeginScene()
    vis.Render()
    vis.EndScene()
    sys.DoStepDynamics(step_size)
    realtime_timer.Spin(step_size)  # 실시간 속도 동기화 (macOS 필수)
```

## 참고 문서
- API: https://api.projectchrono.org/
- 설치: https://api.projectchrono.org/tutorial_install_chrono.html
- GitHub: https://github.com/projectchrono/chrono
- 소스 내 매뉴얼: `chrono/doxygen/documentation/manuals/`
- macOS 빌드 스크립트: `chrono/contrib/build-scripts/macos/buildChronoMac.sh`
- Windows 빌드 스크립트: `chrono/contrib/build-scripts/windows/buildChrono.bat`
- Linux 빌드 스크립트: `chrono/contrib/build-scripts/linux/buildChrono.sh`
