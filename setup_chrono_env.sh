#!/bin/bash
# Project Chrono environment setup script (Linux / macOS)
# Usage: source setup_chrono_env.sh

# ── 프로젝트 루트 자동 감지 ──
# Works when sourced from bash or zsh, even if the current directory is not the
# project root.
if [ -n "${BASH_SOURCE[0]:-}" ]; then
    SCRIPT_PATH="${BASH_SOURCE[0]}"
elif [ -n "${ZSH_VERSION:-}" ]; then
    SCRIPT_PATH="${(%):-%x}"
else
    SCRIPT_PATH="$0"
fi

SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
if [ -z "${CHRONO_BUILD_DIR:-}" ]; then
    if [ -d "${SCRIPT_DIR}/chrono_build_cuda129_sm120" ]; then
        CHRONO_BUILD_DIR="${SCRIPT_DIR}/chrono_build_cuda129_sm120"
    elif [ -d "${SCRIPT_DIR}/chrono_build_vsg" ]; then
        CHRONO_BUILD_DIR="${SCRIPT_DIR}/chrono_build_vsg"
    else
        CHRONO_BUILD_DIR="${SCRIPT_DIR}/chrono_build"
    fi
fi

if [ ! -d "$CHRONO_BUILD_DIR" ]; then
    echo "ERROR: Chrono build directory not found."
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

        # Preferred local CUDA toolkit for the RTX 5060 Ti Chrono build.
        CHRONO_CONDA_ENV="${CHRONO_CONDA_ENV:-$HOME/anaconda3/envs/chrono}"
        if [ -x "${CHRONO_CONDA_ENV}/bin/nvcc" ]; then
            export PATH="${CHRONO_CONDA_ENV}/bin:${PATH}"
            if [ -d "${CHRONO_CONDA_ENV}/targets/x86_64-linux/lib" ]; then
                export LD_LIBRARY_PATH="${CHRONO_CONDA_ENV}/targets/x86_64-linux/lib:${LD_LIBRARY_PATH}"
            fi
            if [ -d "${CHRONO_CONDA_ENV}/lib" ]; then
                export LD_LIBRARY_PATH="${CHRONO_CONDA_ENV}/lib:${LD_LIBRARY_PATH}"
            fi
        fi

        # VSG (Vulkan Scene Graph) libraries, if available.
        VSG_LIB_DIR="$HOME/Packages/vsg/lib"
        if [ -d "${VSG_LIB_DIR}" ]; then
            export LD_LIBRARY_PATH="${VSG_LIB_DIR}:${LD_LIBRARY_PATH}"
            export VSG_FILE_PATH="${CHRONO_BUILD_DIR}/data"
        fi

        # Anaconda libstdc++ 충돌 방지
        if [ -d "$HOME/anaconda3" ] || [ -d "$HOME/miniconda3" ]; then
            export LD_PRELOAD="/usr/lib/x86_64-linux-gnu/libstdc++.so.6"
        fi

        # System CUDA fallback.
        if ! command -v nvcc &>/dev/null && [ -d "/usr/local/cuda/bin" ]; then
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

        # VSG (Vulkan Scene Graph) 라이브러리 — 빌드된 경우에만
        VSG_LIB_DIR="$HOME/Packages/vsg/lib"
        if [ -d "${VSG_LIB_DIR}" ]; then
            export DYLD_LIBRARY_PATH="${VSG_LIB_DIR}:${DYLD_LIBRARY_PATH}"
            export VSG_FILE_PATH="$HOME/Packages/vsg/share/vsgExamples"
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
