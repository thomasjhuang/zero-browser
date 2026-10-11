#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
OFFLINE=0
SYNC_ARGS=(sync --frozen --extra local)
BROWSER_ARGS=(--install-browser)
MODEL_ARGS=(--no-write-lock)
case "${1:-}" in
    "") ;;
    --offline) OFFLINE=1; SYNC_ARGS+=(--offline); BROWSER_ARGS+=(--offline); MODEL_ARGS+=(--offline) ;;
    --help|-h) echo 'Usage: bash install.sh [--offline]'; exit 0 ;;
    *) echo 'Usage: bash install.sh [--offline]' >&2; exit 2 ;;
esac
if [[ $# -gt 1 ]]; then
    echo 'Usage: bash install.sh [--offline]' >&2
    exit 2
fi
if [[ "$(uname -s)" != Darwin || "$(uname -m)" != arm64 ]]; then
    echo 'This version needs an Apple Silicon Mac with Metal.' >&2
    exit 1
fi

cd "$ROOT"
if command -v uv >/dev/null 2>&1; then
    UV_BIN="$(command -v uv)"
elif [[ -x "$ROOT/.zero-browser/tools/uv" ]]; then
    UV_BIN="$ROOT/.zero-browser/tools/uv"
else
    if [[ "$OFFLINE" == 1 ]]; then
        echo 'uv is absent. Run bash install.sh with network access first.' >&2
        exit 1
    fi
    mkdir -p "$ROOT/.zero-browser/tools"
    echo 'Installing uv into .zero-browser/tools.'
    curl --proto '=https' --tlsv1.2 -LsSf https://astral.sh/uv/install.sh \
        -o "$ROOT/.zero-browser/tools/install-uv.sh"
    UV_UNMANAGED_INSTALL="$ROOT/.zero-browser/tools" sh "$ROOT/.zero-browser/tools/install-uv.sh"
    UV_BIN="$ROOT/.zero-browser/tools/uv"
fi

echo 'Installing locked Python dependencies.'
"$UV_BIN" "${SYNC_ARGS[@]}"
echo 'Preparing the pinned Qwen model (about 2.3 GB).'
"$ROOT/.venv/bin/python" scripts/download_local_model.py "${MODEL_ARGS[@]}"
"$ROOT/.venv/bin/python" scripts/run_cli.py "${BROWSER_ARGS[@]}"
"$ROOT/zero-browser" --doctor
echo 'Setup passed. Run ./zero-browser --url https://www.google.com "Your browser goal"'
