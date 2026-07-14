#!/usr/bin/env bash
# Launch the ShowBuilder backend (serves the wizard + runs the engines/build).
set -e
cd "$(dirname "$0")"
exec ./.venv/bin/python -m backend.app
