#!/usr/bin/env bash
# Launch Patchbay (patch sheet manager — Q225 / M32 / Wing).
set -e
cd "$(dirname "$0")"
PY=./.venv/bin/python
[ -x "$PY" ] || PY=../ShowBuilder/.venv/bin/python
exec "$PY" -m backend.app
