#!/bin/bash
# Double-click on the Mac to reset the JVC PZ100 control plane.
# The Mac can't reach the cameras directly -- it reaches the n8n VM over
# Tailscale, and the VM (on the camera LAN) runs the actual reset.
#
# Edit METHOD to "reboot" if the stream toggle doesn't clear the wedge for you.

METHOD="video"           # video (real off/on fix) | stream | reboot | status
VM="brian@192.168.200.84"
SSH_KEY="$HOME/.ssh/proxmox_tds"
REMOTE_DIR="/opt/jvc-reset"

cd "$(dirname "$0")" || exit 1
LOG="reset_$(date +%Y%m%d_%H%M%S).log"

echo "Resetting JVC PZ100 cameras via the n8n VM (method: $METHOD)..."
echo "-----------------------------------------------------------------"

ssh -J tds -i "$SSH_KEY" "$VM" \
    "$REMOTE_DIR/.venv/bin/python $REMOTE_DIR/reset_cameras.py --method $METHOD" \
    2>&1 | tee "$LOG"

echo "-----------------------------------------------------------------"
echo "Done. Log saved to: $(pwd)/$LOG"
echo "Press any key to close."
read -r -n 1
