#!/bin/bash
# Runs every 5 min via cron on the n8n VM. Dropbox's own local ".dropbox.cache"
# folder (a normal cache of recently-changed/deleted content, NOT synced data)
# can balloon and fill the disk — discovered 2026-09-12 when widening the
# Dropbox sync scope to the real 3CDC venue folders caused it to spike to 13G
# and stall syncing. Clearing its CONTENTS is safe and Dropbox-documented:
# local-only, does not touch the cloud copy or any other device, and Dropbox
# rebuilds it as needed. This just keeps it from ever taking the disk down.
#
# Live copy: ~/dropbox_cache_guard.sh + crontab -l on the VM (192.168.200.84).
# This file is the checked-in reference copy — redeploy by copying it over
# (see deploy_app.command's pattern) and re-running the crontab install below.
#
# Install (one-time, already done 2026-09-12):
#   (crontab -l 2>/dev/null; echo "*/5 * * * * $HOME/dropbox_cache_guard.sh >> $HOME/dropbox_cache_guard.log 2>&1") | crontab -
LOG="$HOME/dropbox_cache_guard.log"
THRESHOLD=85

used=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
if [ "$used" -ge "$THRESHOLD" ]; then
  cache=$(du -sh "$HOME/Dropbox/.dropbox.cache" 2>/dev/null | cut -f1)
  rm -rf "$HOME/Dropbox/.dropbox.cache/"* 2>/dev/null
  echo "$(date '+%Y-%m-%d %H:%M:%S') disk=${used}% cache=${cache} -> CLEARED"
fi

# Keep the guard's own log from becoming the next disk problem — cap at 500 lines.
if [ -f "$LOG" ] && [ "$(wc -l < "$LOG")" -gt 500 ]; then
  tail -n 500 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
fi
