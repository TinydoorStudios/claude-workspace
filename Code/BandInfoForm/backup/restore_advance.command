#!/bin/bash
# =============================================================================
# Band Advance — restore, driven from the Mac
# =============================================================================
#   ./restore_advance.command                      # newest archive -> the live VM
#   ./restore_advance.command --list               # what backups exist, where
#   ./restore_advance.command --archive NAME       # restore a specific one
#   ./restore_advance.command --host brian@1.2.3.4 # restore onto a different box
#   ./restore_advance.command --fetch-only         # just pull it to ~/Downloads
#   ./restore_advance.command -- --db-only         # anything after -- goes to restore.sh
#
# Pulls the newest verified archive off Audio NAS, the short-term primary
# (falls back to Cold Storage), checks its sha256 on the Mac, ships it to the
# target host, and runs the archive's own restore.sh there. Everything after
# `--` is passed through.
# =============================================================================
set -o pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LOG="$HERE/restore_log.txt"
NASKEY="$HOME/.ssh/claude_backup"
VMKEY="$HOME/.ssh/proxmox_tds"
TARGET="brian@192.168.200.84"
SSH_NAS="ssh -i $NASKEY -o BatchMode=yes -o ConnectTimeout=15"

SOURCES=(
  "audionas|brian@192.168.200.36|/mnt/AudioNas/brian/band-advance-backups"
  "coldstorage|brian@192.168.200.35|/mnt/The-Pool/ClaudeBackup/band-advance"
)

ARCHIVE=""; LIST=0; FETCH_ONLY=0; PASSTHRU=()
while [ $# -gt 0 ]; do
  case "$1" in
    --list)       LIST=1 ;;
    --archive)    ARCHIVE="$2"; shift ;;
    --host)       TARGET="$2"; shift ;;
    --fetch-only) FETCH_ONLY=1 ;;
    --)           shift; PASSTHRU=("$@"); break ;;
    -h|--help)    sed -n '2,20p' "$0"; exit 0 ;;
    *) echo "unknown option: $1"; exit 2 ;;
  esac
  shift
done

{
echo "=== Band Advance restore — $(date) ==="

if [ "$LIST" = 1 ]; then
  for s in "${SOURCES[@]}"; do
    NM="${s%%|*}"; R="${s#*|}"; HOST="${R%%|*}"; DIR="${R##*|}"
    echo; echo "--- $NM ($HOST:$DIR) ---"
    $SSH_NAS "$HOST" "ls -lh '$DIR'/band-advance-*.tar.gz 2>/dev/null | awk '{print \$5, \$6, \$7, \$8, \$9}'" \
      2>/dev/null || echo "  unreachable"
  done
  exit 0
fi

# --- find a source that is up and has the archive we want -------------------
PICKED=""; PICK_HOST=""; PICK_DIR=""; PICK_NAME=""
for s in "${SOURCES[@]}"; do
  NM="${s%%|*}"; R="${s#*|}"; HOST="${R%%|*}"; DIR="${R##*|}"
  echo "--- checking $NM ---"
  $SSH_NAS "$HOST" exit 2>/dev/null || { echo "  unreachable"; continue; }
  if [ -n "$ARCHIVE" ]; then
    CAND="$ARCHIVE"
    $SSH_NAS "$HOST" "test -f '$DIR/$CAND'" 2>/dev/null || { echo "  $CAND not here"; continue; }
  else
    CAND=$($SSH_NAS "$HOST" "ls -1 '$DIR'/band-advance-*.tar.gz 2>/dev/null | sort -r | head -1 | xargs -r basename" 2>/dev/null)
    [ -z "$CAND" ] && { echo "  no archives here"; continue; }
  fi
  echo "  newest: $CAND"
  PICKED="$NM"; PICK_HOST="$HOST"; PICK_DIR="$DIR"; PICK_NAME="$CAND"; break
done
[ -z "$PICKED" ] && { echo "No archive found on any NAS. Check the boxes are up (--list)."; exit 1; }

echo
echo "--- pulling $PICK_NAME from $PICKED ---"
WORK="$HOME/Downloads/band-advance-restore"
mkdir -p "$WORK"
scp -i "$NASKEY" "$PICK_HOST:$PICK_DIR/$PICK_NAME" "$WORK/" || { echo "download failed"; exit 1; }
scp -i "$NASKEY" "$PICK_HOST:$PICK_DIR/$PICK_NAME.sha256" "$WORK/" 2>/dev/null

echo "--- verifying checksum on the Mac ---"
if [ -f "$WORK/$PICK_NAME.sha256" ]; then
  WANT=$(awk '{print $1}' "$WORK/$PICK_NAME.sha256")
  GOT=$(shasum -a 256 "$WORK/$PICK_NAME" | awk '{print $1}')
  if [ "$WANT" = "$GOT" ]; then echo "  sha256 OK"
  else
    echo "  !! CHECKSUM MISMATCH — this copy is damaged."
    echo "     Try the other NAS, or an older archive:  $0 --list"
    exit 1
  fi
else
  echo "  (no .sha256 alongside — skipping)"
fi
tar tzf "$WORK/$PICK_NAME" >/dev/null 2>&1 && echo "  tarball opens cleanly" || { echo "  !! tarball is unreadable"; exit 1; }

echo
echo "--- manifest ---"
DIRNAME="${PICK_NAME%.tar.gz}"
tar -xOzf "$WORK/$PICK_NAME" "$DIRNAME/MANIFEST.txt" 2>/dev/null | sed -n '1,30p' | sed 's/^/  /'

if [ "$FETCH_ONLY" = 1 ]; then
  echo; echo "Fetched only, as asked: $WORK/$PICK_NAME"
  exit 0
fi

echo
echo "--- shipping to $TARGET ---"
if [[ "$TARGET" == *192.168.200.84* ]]; then
  SSH_T="ssh -J tds -i $VMKEY $TARGET"; SCP_J="-J tds -i $VMKEY"
else
  SSH_T="ssh $TARGET"; SCP_J=""
fi
echo
echo "  This will restore onto $TARGET."
echo "  Nothing is destroyed: an existing database is renamed aside, an existing"
echo "  app dir is moved aside, and a populated Dropbox/Nyquist is left alone."
read -r -p "  proceed? [y/N] " a
[ "$(printf %s "$a" | tr A-Z a-z)" = "y" ] || { echo "  aborted."; exit 0; }

scp $SCP_J "$WORK/$PICK_NAME" "$TARGET:/tmp/" || { echo "upload failed"; exit 1; }
$SSH_T "
  cd /tmp && rm -rf '$DIRNAME' && tar xzf '$PICK_NAME' &&
  sudo ./'$DIRNAME'/restore.sh --yes ${PASSTHRU[*]}
"
RC=$?

echo
echo "=== restore finished (exit $RC) — $(date) ==="
[ $RC -eq 0 ] && echo "Check it: https://advance.tinydoorstudios.com/search   (passcode: lockdown)"
} 2>&1 | tee "$LOG"
