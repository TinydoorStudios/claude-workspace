#!/bin/bash
# audio-sync-report.sh
# TrueNAS nightly email report
#
# Reads today's sync log written by the Reaper PC PowerShell script
# and emails a summary to Brian.
#
# Schedule: TrueNAS cron job, nightly at 3:00 AM (1 hour after PC script)
# Place this file at: /mnt/AudioNas/Audio/scripts/audio-sync-report.sh
# Make executable: chmod +x /mnt/AudioNas/Audio/scripts/audio-sync-report.sh

LOG_DIR="/mnt/AudioNas/Audio/sync-logs"
TODAY=$(date +%Y-%m-%d)
LOG_FILE="$LOG_DIR/sync-$TODAY.txt"
TO="tinydoorstudios@gmail.com"
SUBJECT="Audio Archive Sync — $TODAY"

if [ -f "$LOG_FILE" ]; then
    mail -s "$SUBJECT" "$TO" < "$LOG_FILE"
else
    echo "No sync log found for $TODAY.

The Reaper PC sync script may not have run, or the NAS share was not accessible from the PC.

Expected log location: $LOG_FILE
" | mail -s "$SUBJECT — NO LOG FOUND" "$TO"
fi
