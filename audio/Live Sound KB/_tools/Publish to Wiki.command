#!/usr/bin/env bash
# Double-clickable publisher. Lives next to kb-publish.sh.
# Double-click in Finder (or let Claude double-click it) to publish the KB to the wiki.
cd "$(dirname "$0")" || exit 1
chmod +x ./kb-publish.sh 2>/dev/null
./kb-publish.sh "Manual publish $(date '+%Y-%m-%d %H:%M')"
echo
echo "Press any key to close…"
read -n 1 -s
