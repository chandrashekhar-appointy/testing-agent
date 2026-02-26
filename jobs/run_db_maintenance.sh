#!/bin/sh
set -eu

# Resolve repo root regardless of current working directory.
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="/tmp/testing-agent-venv"

echo "[bootstrap] preparing python runtime"

# Bifrost runner currently uses alpine image. Install python/pip when missing.
if ! command -v python3 >/dev/null 2>&1; then
  if command -v apk >/dev/null 2>&1; then
    apk add --no-cache python3 py3-pip
  else
    echo "python3 is required but not found and apk is unavailable" >&2
    exit 1
  fi
fi

python3 -m venv "$VENV_DIR"
# shellcheck disable=SC1091
. "$VENV_DIR/bin/activate"

pip install --no-cache-dir -r "$REPO_ROOT/requirements.txt"

echo "[bootstrap] dependencies ready, running job"
exec python "$REPO_ROOT/jobs/db_maintenance.py"
