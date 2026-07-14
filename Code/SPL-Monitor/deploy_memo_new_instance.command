#!/bin/bash
# First-time stand-up of the Memorial Hall SPL instance: /opt/spl-monitor-memo,
# its own venv, systemd unit, env file, port 8091. Separate process from the
# FSQ instance (/opt/spl-monitor, 8090) — they run independently, forever.
# Tees output to deploy_memo_new_instance.out for Nyquist to read back.
cd "$(dirname "$0")"
OUT="deploy_memo_new_instance.out"
KEY="$HOME/.ssh/proxmox_tds"
VM="brian@192.168.200.84"
SSH="ssh -J tds -i $KEY"
REMOTE_DIR="/opt/spl-monitor-memo"

{
echo "===== Memo SPL instance stand-up  $(date) ====="

echo "----- 1. create remote dir -----"
$SSH "$VM" "sudo mkdir -p $REMOTE_DIR && sudo chown brian:brian $REMOTE_DIR"

echo "----- 2. rsync source (excluding config.json/config.memo.json/.venv/logs) -----"
rsync -az --exclude .venv --exclude logs --exclude __pycache__ \
  --exclude config.json --exclude config.memo.json \
  -e "$SSH" \
  ./ "$VM":"$REMOTE_DIR"/ && echo "rsync OK"

echo "----- 3. push config.memo.json as remote config.json -----"
rsync -az -e "$SSH" ./config.memo.json "$VM":"$REMOTE_DIR"/config.json && echo "config OK"

echo "----- 4. python venv + deps -----"
$SSH "$VM" bash -s <<'REMOTE'
set -e
cd /opt/spl-monitor-memo
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
./.venv/bin/pip install --upgrade pip -q
./.venv/bin/pip install aiohttp -q
# link system-site matplotlib/reportlab/numpy (apt-installed) into the venv,
# same trick used for the FSQ instance, so the nightly PDF report works here too.
PYVER=$(./.venv/bin/python3 -c "import sys; print(f'python{sys.version_info.major}.{sys.version_info.minor}')")
SITE_DIR=".venv/lib/$PYVER/site-packages"
if [ -d "$SITE_DIR" ] && [ ! -f "$SITE_DIR/zz-system-site.pth" ]; then
  echo "/usr/lib/python3/dist-packages" > "$SITE_DIR/zz-system-site.pth"
fi
./.venv/bin/python3 -c "import aiohttp; print('aiohttp OK', aiohttp.__version__)"
./.venv/bin/python3 -c "import matplotlib, reportlab, numpy; print('report deps OK')" || echo "WARN: report deps not linked — nightly PDF email will fail on this instance until fixed"
REMOTE

echo "----- 5. install systemd unit + env file -----"
rsync -az -e "$SSH" ./deploy/spl-monitor-memo.service "$VM":/tmp/spl-monitor-memo.service
rsync -az -e "$SSH" ./deploy/spl-monitor-memo.env "$VM":/tmp/spl-monitor-memo.env
$SSH "$VM" 'sudo mv /tmp/spl-monitor-memo.service /etc/systemd/system/spl-monitor-memo.service && \
  sudo mv /tmp/spl-monitor-memo.env /etc/spl-monitor-memo.env && \
  sudo chmod 600 /etc/spl-monitor-memo.env && \
  sudo systemctl daemon-reload && \
  sudo systemctl enable --now spl-monitor-memo && \
  sleep 3 && systemctl is-active spl-monitor-memo'

echo "----- 6. verify: local curl on the VM -----"
$SSH "$VM" 'curl -s -o /dev/null -w "local 8091 = HTTP %{http_code}\n" --max-time 10 http://127.0.0.1:8091/'

echo "----- 7. verify: Smaart connection in the journal -----"
sleep 2
$SSH "$VM" 'journalctl -u spl-monitor-memo --since "-1 min" --no-pager | tail -30'

echo "===== end ====="
} 2>&1 | tee "$OUT"

echo
echo "Results in: $(pwd)/$OUT"
