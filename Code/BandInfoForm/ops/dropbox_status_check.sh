#!/bin/bash
# Dropbox daemon health check (audit 2026-09-16 #5): the pipeline "files"
# docs to a local folder Dropbox never syncs if the daemon died, with no
# error anywhere else in the stack. Piggybacks on the 10:15 lifecycle
# watchdog timer, which already runs daily.
# 2026-09-21 sweep (OPS-15): one mid-sync sample ("Syncing…", "Indexing…", boot-time
# "Starting…") used to alert. Re-check every 30s for ~10 min; a dead daemon still alerts at once.
set -uo pipefail
TRIES=21
GAP=30
STATUS=""
for i in $(seq 1 "$TRIES"); do
    STATUS="$(python3 ~/dropbox.py status 2>&1)"
    FIRST="${STATUS%%$'\n'*}"
    case "$FIRST" in
        "Up to date") exit 0 ;;
        *"isn't running"*|*"isn't responding"*|*"Couldn't"*|*"not linked"*|*"can't open file"*) break ;;
    esac
    if [ "$i" -lt "$TRIES" ]; then
        sleep "$GAP"
    fi
done
/opt/band-advance/venv/bin/python3 /opt/band-advance/ops/alert.py \
    "Dropbox not syncing on the band-advance VM" \
    "dropbox.py status after ${i} check(s) over ~$(( (i-1)*GAP ))s never reached 'Up to date'. Last status: ${STATUS}"
