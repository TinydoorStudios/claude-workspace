#!/bin/zsh
# Deploy ShowBuilder to the n8n VM (package instance) and verify it came back up.
# Double-click from Finder or run from a terminal. Output tees to last_deploy.log.
set -e
SRC="$HOME/Documents/Claude/Code/ShowBuilder"
LOG="$SRC/deploy/last_deploy.log"
{
  echo "== ShowBuilder deploy $(date '+%Y-%m-%d %H:%M:%S') =="
  rsync -az --delete \
    --exclude .venv --exclude __pycache__ --exclude _archive --exclude inbox \
    --exclude .DS_Store --exclude .claude --exclude '*.log' --exclude mac/ShowBuilder.app \
    -e "ssh -i ~/.ssh/proxmox_tds -J tds" \
    "$SRC/" brian@192.168.200.84:/opt/showbuilder/
  ssh -J tds -i ~/.ssh/proxmox_tds brian@192.168.200.84 \
    'sudo systemctl restart showbuilder && sleep 2 && systemctl is-active showbuilder'
  echo "-- public health check --"
  curl -s --max-time 15 https://showbuilder.tinydoorstudios.com/health
  echo
  echo "== DEPLOY OK =="
} 2>&1 | tee "$LOG"
