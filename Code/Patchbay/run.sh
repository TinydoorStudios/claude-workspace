#!/usr/bin/env bash
# Launch Patchbay (patch sheet manager — Q225 / M32 / Wing).
set -e
cd "$(dirname "$0")"
PY=./.venv/bin/python
[ -x "$PY" ] || { echo "no .venv — run: python3 -m venv .venv && .venv/bin/pip install aiohttp openpyxl"; exit 1; }
exec "$PY" -m backend.app
