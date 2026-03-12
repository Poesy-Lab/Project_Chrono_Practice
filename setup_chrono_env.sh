#!/bin/bash
# Project Chrono environment setup script (Linux / macOS)
# Usage: source setup_chrono_env.sh

# ── 프로젝트 루트 자동 감지 ──
CHRONO_BUILD_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/chrono_build"

if [ ! -d "$CHRONO_BUILD_DIR" ]; then
    echo "ERROR: chrono_build/ directory not found."
    echo "  Expected: ${CHRONO_BUILD_DIR}"
    echo "  Please build Chrono first. See README.md for instructions."
    return 1 2>/dev/null || exit 1
fi

# ── OS 감지 ──
OS_TYPE="$(uname -s)"

case "$OS_TYPE" in
    Linux)
        export LD_LIBRARY_PATH="${CHRONO_BUILD_DIR}/lib:${LD_LIBRARY_PATH}"
        export PYTHONPATH="${CHRONO_BUILD_DIR}/bin:${PYTHONPATH}"

        # Anaconda libstdc++ 충돌 방지
        if [ -d "$HOME/anaconda3" ] || [ -d "$HOME/miniconda3" ]; then
            export LD_PRELOAD="/usr/lib/x86_64-linux-gnu/libstdc++.so.6"
        fi

        # CUDA (설치되어 있는 경우)
        if [ -d "/usr/local/cuda/bin" ]; then
            export PATH="/usr/local/cuda/bin:${PATH}"
            export LD_LIBRARY_PATH="/usr/local/cuda/lib64:${LD_LIBRARY_PATH}"
        fi
        ;;

    Darwin)
        export DYLD_LIBRARY_PATH="${CHRONO_BUILD_DIR}/lib:${DYLD_LIBRARY_PATH}"
        export PYTHONPATH="${CHRONO_BUILD_DIR}/bin:${PYTHONPATH}"

        # Homebrew OpenMP (Apple clang 기본 미포함)
        HOMEBREW_PREFIX="$(brew --prefix 2>/dev/null || echo /opt/homebrew)"
        if [ -f "${HOMEBREW_PREFIX}/opt/libomp/lib/libomp.dylib" ]; then
            export DYLD_LIBRARY_PATH="${HOMEBREW_PREFIX}/opt/libomp/lib:${DYLD_LIBRARY_PATH}"
        fi
        ;;

    *)
        echo "WARNING: Unsupported OS ($OS_TYPE). This script supports Linux and macOS."
        echo "  For Windows, set PYTHONPATH and PATH manually. See README.md."
        return 1 2>/dev/null || exit 1
        ;;
esac

# ── 상태 출력 ──
echo "Project Chrono environment configured."
echo "  OS:        ${OS_TYPE} ($(uname -m))"
echo "  Build dir: ${CHRONO_BUILD_DIR}"
echo "  PyChrono:  ready (use 'import pychrono')"
if command -v nvcc &>/dev/null; then
    echo "  CUDA:      $(nvcc --version 2>/dev/null | grep 'release' | awk '{print $6}')"
else
    echo "  CUDA:      not available"
fi
