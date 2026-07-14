#!/bin/bash
# Deploy the password-only gate for the Cameras portal page.
#  1. rsync the updated web.py (now serves its own single-password login) to the VM
#  2. restart jvc-cameras-web
#  3. strip auth_basic from ONLY the `location /cameras/` block in the landing
#     nginx, validate with `nginx -t`, reload. Backs up + auto-rolls-back on failure.
# Run from the Mac (Tailscale + LAN). Passcode is "lockdown" (web.py default).
set -e
VM="brian@192.168.200.84"
SSH="ssh -J tds -i $HOME/.ssh/proxmox_tds"
REMOTE="/opt/jvc-reset"
SRC="$(cd "$(dirname "$0")/.." && pwd)/"

cd "$(dirname "$0")"
LOG="deploy_gate_$(date +%Y%m%d_%H%M%S).log"
{
  echo "==> Syncing web.py + code to $REMOTE"
  rsync -az --exclude .venv --exclude '__pycache__' --exclude '*.log' \
        --exclude '.git' -e "$SSH" "$SRC" "$VM:$REMOTE/"

  echo "==> Restarting jvc-cameras-web"
  $SSH "$VM" "sudo systemctl restart jvc-cameras-web && systemctl is-active jvc-cameras-web"

  echo "==> Removing auth_basic from the /cameras/ nginx block"
  $SSH "$VM" 'bash -s' <<"REMOTE_EOF"
set -e
CONF=/opt/landing/nginx.conf
[ -f "$CONF" ] || { echo "!! $CONF not found — find the landing nginx.conf and edit by hand"; exit 1; }

BK="${CONF}.bak.$(date +%Y%m%d_%H%M%S)"
sudo cp "$CONF" "$BK"
echo "   backup: $BK"

# Drop auth_basic / auth_basic_user_file lines that live inside the
# `location /cameras/ { ... }` block only. Brace-counted, surgical.
sudo python3 - "$CONF" <<"PY"
import re, sys
p = sys.argv[1]
s = open(p).read()
m = re.search(r'location\s+/cameras/\s*\{', s)
if not m:
    print("   no `location /cameras/` block found — nothing changed"); sys.exit(0)
i = m.end(); depth = 1; j = i
while j < len(s) and depth:
    if s[j] == '{': depth += 1
    elif s[j] == '}': depth -= 1
    j += 1
block = s[m.start():j]
new = "\n".join(l for l in block.splitlines() if "auth_basic" not in l)
if new != block:
    open(p, "w").write(s[:m.start()] + new + s[j:])
    print("   auth_basic removed from /cameras/ block")
else:
    print("   /cameras/ block had no auth_basic — already clean")
PY

# Find the landing nginx container and validate before reloading.
CT=$(sudo docker ps --format '{{.Names}}' | grep -iE 'landing|nginx' | head -1)
[ -n "$CT" ] || { echo "!! couldn't find the nginx container; restoring backup"; sudo cp "$BK" "$CONF"; exit 1; }
echo "   nginx container: $CT"

if sudo docker exec "$CT" nginx -t; then
    sudo docker exec "$CT" nginx -s reload
    echo "   nginx reloaded OK"
else
    echo "!! nginx -t failed — restoring backup, nothing changed live"
    sudo cp "$BK" "$CONF"
    exit 1
fi
REMOTE_EOF

  echo "==> Done. Visit https://tinydoorstudios.com/cameras/"
  echo "    You should now get ONE password box. Passcode: lockdown"
} 2>&1 | tee "$LOG"

echo "Log: $(pwd)/$LOG"
echo "Press any key to close."
read -r -n 1
