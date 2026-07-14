#!/bin/bash
# One-shot deploy from the Mac to the n8n VM (over Tailscale via the tds jump).
# Mirrors the SPL-monitor deploy pattern: rsync the code, build the venv,
# install the systemd timer. Safe to re-run.

set -e
VM="brian@192.168.200.84"
SSH="ssh -J tds -i $HOME/.ssh/proxmox_tds"
REMOTE="/opt/jvc-reset"
SRC="$(cd "$(dirname "$0")/.." && pwd)/"

cd "$(dirname "$0")"
LOG="deploy_$(date +%Y%m%d_%H%M%S).log"
{
  echo "==> Creating $REMOTE on the VM"
  $SSH "$VM" "sudo mkdir -p $REMOTE && sudo chown brian:brian $REMOTE"

  echo "==> Syncing code"
  rsync -az --exclude .venv --exclude '__pycache__' --exclude '*.log' \
        --exclude '.git' -e "$SSH" "$SRC" "$VM:$REMOTE/"

  echo "==> Building venv + installing requests"
  $SSH "$VM" "test -d $REMOTE/.venv || python3 -m venv $REMOTE/.venv; \
              $REMOTE/.venv/bin/pip install -q --upgrade pip; \
              $REMOTE/.venv/bin/pip install -q -r $REMOTE/requirements.txt"

  echo "==> Installing systemd timer (installed but NOT enabled yet)"
  $SSH "$VM" "sudo cp $REMOTE/deploy/jvc-reset.service /etc/systemd/system/; \
              sudo cp $REMOTE/deploy/jvc-reset.timer /etc/systemd/system/; \
              sudo systemctl daemon-reload"

  echo "==> Installing + starting the portal web button service"
  $SSH "$VM" "sudo cp $REMOTE/deploy/jvc-cameras-web.service /etc/systemd/system/; \
              sudo systemctl daemon-reload; \
              sudo systemctl enable --now jvc-cameras-web; \
              sudo systemctl restart jvc-cameras-web; \
              systemctl is-active jvc-cameras-web"

  echo "==> Done."
  echo "    Portal button: https://tinydoorstudios.com/cameras/  (login: tds)"
  echo "    Scheduled auto-healer is installed but OFF. Enable when ready:"
  echo "      sudo systemctl enable --now jvc-reset.timer"
  echo "    NOTE: the /cameras/ nginx proxy + portal card are a one-time edit to"
  echo "    /opt/landing (nginx.conf + index.html) -- see deploy/DEPLOY.md."
} 2>&1 | tee "$LOG"

echo "Log: $(pwd)/$LOG"
echo "Press any key to close."
read -r -n 1
