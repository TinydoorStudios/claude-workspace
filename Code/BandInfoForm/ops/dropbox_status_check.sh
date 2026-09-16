#!/bin/bash
# Dropbox daemon health check (audit 2026-09-16 #5): the pipeline "files"
# docs to a local folder Dropbox never syncs if the daemon died, with no
# error anywhere else in the stack. Piggybacks on the 10:15 lifecycle
# watchdog timer, which already runs daily.
set -uo pipefail
STATUS="$(~/dropbox.py status 2>&1)"
if [ "$STATUS" != "Up to date" ]; then
    /opt/band-advance/venv/bin/python3 /opt/band-advance/ops/alert.py \
        "Dropbox not syncing on the band-advance VM" \
        "dropbox.py status returned: ${STATUS}"
fi
