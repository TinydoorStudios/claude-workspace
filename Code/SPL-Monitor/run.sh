#!/usr/bin/env bash
# Launch the SPL-Monitor backend (serves the dashboard + runs the data source).
set -e
cd "$(dirname "$0")"
exec ./.venv/bin/python -m backend.app
