#!/usr/bin/env bash
# Adds the assets rsync to kb-git-push.sh, immediately after the git push line.
# Safe to run multiple times — checks for duplication first.

PUSH_SCRIPT="$HOME/.claude/scripts/kb-git-push.sh"

if [ ! -f "$PUSH_SCRIPT" ]; then
  echo "ERROR: $PUSH_SCRIPT not found"
  exit 1
fi

if grep -q "kb-assets" "$PUSH_SCRIPT"; then
  echo "rsync already present in $PUSH_SCRIPT — nothing to do."
  cat "$PUSH_SCRIPT"
  exit 0
fi

cp "$PUSH_SCRIPT" "${PUSH_SCRIPT}.bak"
echo "Backed up to ${PUSH_SCRIPT}.bak"

RSYNC_BLOCK='
# Sync downloadable assets to n8n VM for static serving
rsync -a --delete \
  -e "ssh -J tds -i ~/.ssh/proxmox_tds" \
  "/Users/brianlloyd/Documents/Claude/audio/Live Sound KB/Wiki/assets/" \
  "brian@192.168.200.84:/opt/kb-assets/" \
  >> "$LOG_FILE" 2>&1 && \
  echo "$(date): assets synced" >> "$LOG_FILE" || \
  echo "$(date): assets rsync FAILED" >> "$LOG_FILE"
'

# Insert after the first git push line
awk -v block="$RSYNC_BLOCK" '
  /git push/ && !inserted {
    print
    print block
    inserted=1
    next
  }
  { print }
' "$PUSH_SCRIPT" > /tmp/kb-git-push-new.sh

cp /tmp/kb-git-push-new.sh "$PUSH_SCRIPT"
chmod +x "$PUSH_SCRIPT"

echo "Done. Updated script:"
echo "---"
cat "$PUSH_SCRIPT"
