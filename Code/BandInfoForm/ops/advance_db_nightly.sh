#!/usr/bin/env bash
# Band Advance — nightly database dump to both TrueNAS boxes (2026-09-13 audit #9).
# The weekly full archive (backup/advance_backup.sh) is unchanged; this closes
# the up-to-7-days gap for bookings, send/reminder stamps and finalize state.
# Keeps 14 nightly dumps per box. Emails Brian ONLY on failure.
set -uo pipefail
KEEP=14
WORK=/var/backups/band-advance/nightly
SSH_KEY=/home/brian/.ssh/nas_backup
SSH_OPTS="-i $SSH_KEY -o BatchMode=yes -o ConnectTimeout=15 -o StrictHostKeyChecking=accept-new"
TARGETS=(
  "coldstorage|brian@192.168.200.35|/mnt/The-Pool/ClaudeBackup/band-advance/nightly"
  "audionas|brian@192.168.200.36|/mnt/AudioNas/brian/band-advance-backups/nightly"
)
STAMP=$(date +%Y%m%d-%H%M%S)
NAME="advance-$STAMP.dump"
FAILS=()

mkdir -p "$WORK"
if ! docker exec advance-db pg_dump -U advance -d advance -Fc > "$WORK/$NAME" 2>"$WORK/.err"; then
  FAILS+=("pg_dump failed: $(head -c 300 "$WORK/.err")")
fi
if [ -s "$WORK/$NAME" ] && ! docker exec -i advance-db pg_restore --list < "$WORK/$NAME" >/dev/null 2>&1; then
  FAILS+=("dump did not verify with pg_restore --list")
fi
SHA=$(sha256sum "$WORK/$NAME" | awk '{print $1}')

if [ ${#FAILS[@]} -eq 0 ]; then
  for t in "${TARGETS[@]}"; do
    IFS='|' read -r NM HOST DIR <<<"$t"
    if ! ssh $SSH_OPTS "$HOST" "mkdir -p '$DIR'"; then FAILS+=("$NM: unreachable"); continue; fi
    if ! rsync -a -e "ssh $SSH_OPTS" "$WORK/$NAME" "$HOST:$DIR/"; then FAILS+=("$NM: copy failed"); continue; fi
    RSHA=$(ssh $SSH_OPTS "$HOST" "sha256sum '$DIR/$NAME'" 2>/dev/null | awk '{print $1}')
    [ "$RSHA" = "$SHA" ] || { FAILS+=("$NM: checksum mismatch on NAS"); continue; }
    # zsh-safe retention on TrueNAS: find, never a glob
    ssh $SSH_OPTS "$HOST" "find '$DIR' -maxdepth 1 -type f -name 'advance-*.dump' -printf '%T@ %p\n' | sort -rn | awk 'NR>$KEEP {print \$2}' | xargs -r rm -f" \
      || FAILS+=("$NM: retention cleanup failed")
    # audit 2026-09-16 ops #4: only the DB dump rode this nightly job —
    # uploaded stage plots + disk-first submission JSON (data/) had up to
    # a week's gap same as the DB used to, now closed the same way. A
    # mirror, not versioned dumps — --delete keeps it matching live.
    DATADIR="$(dirname "$DIR")/data"
    if ! ssh $SSH_OPTS "$HOST" "mkdir -p '$DATADIR'"; then FAILS+=("$NM: data dir unreachable"); continue; fi
    rsync -a --delete -e "ssh $SSH_OPTS" /opt/band-advance/data/ "$HOST:$DATADIR/" \
      || FAILS+=("$NM: data/ mirror failed")
  done
fi
# local: keep 3
find "$WORK" -maxdepth 1 -type f -name 'advance-*.dump' -printf '%T@ %p\n' | sort -rn | awk 'NR>3 {print $2}' | xargs -r rm -f

if [ ${#FAILS[@]} -gt 0 ]; then
  MSG=$(printf '%s\n' "${FAILS[@]}")
  echo "FAILED: $MSG"
  sudo -u brian /bin/bash -c 'set -a; . /opt/band-advance/advance.env; set +a; exec /opt/band-advance/venv/bin/python /opt/band-advance/ops/alert.py "$@"' _ \
    "Band Advance nightly DB backup FAILED" "$MSG"
  exit 1
fi
echo "ok: $NAME ($SHA) on ${#TARGETS[@]} NAS boxes"
