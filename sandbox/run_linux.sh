#!/usr/bin/env bash
# Quick launcher for the physics sandbox GUI on Linux.
# Requires: python3, tkinter, numpy, scipy
set -euo pipefail
cd "$(dirname "$0")/.."
python3 sandbox/physics_app.py "$@"
