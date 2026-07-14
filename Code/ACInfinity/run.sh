#!/usr/bin/env bash
# Launch the AC Infinity dashboard locally.
set -euo pipefail
cd "$(dirname "$0")"

# load creds
if [[ -f aci.env ]]; then
  set -a; source aci.env; set +a
else
  echo "Missing aci.env — copy aci.env.example to aci.env and fill it in." >&2
  exit 1
fi

# venv with aiohttp
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
  ./.venv/bin/pip install -q --upgrade pip aiohttp
fi

exec ./.venv/bin/python app/server.py
