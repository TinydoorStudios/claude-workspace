#!/bin/bash
# =============================================================================
# Band Advance backup — one-time installer
# =============================================================================
# Run once from the Mac. Double-click it, or:
#   ~/Documents/Claude/Code/BandInfoForm/backup/install_backup.command
#
# What it does:
#   1. ships backup/ to the n8n VM at /opt/band-advance/backup/
#   2. makes the VM an ed25519 key and authorises it on BOTH TrueNAS boxes
#   3. creates the backup directories on both NAS boxes
#   4. writes the GPG passphrase file on the VM (0600, root-only)
#   4b. imports + publishes the n8n "Band Advance — Backup Report" workflow,
#       resolving the Graph credential id and the internal token on the VM
#   5. installs + enables the weekly systemd timer (Sundays 03:15)
#   6. runs one backup immediately and reports the result
#
# Safe to re-run — every step is idempotent.
# =============================================================================
set -o pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LOG="$HERE/install_log.txt"
VM="brian@192.168.200.84"
VMKEY="$HOME/.ssh/proxmox_tds"
NASKEY="$HOME/.ssh/claude_backup"
SSH_VM="ssh -J tds -i $VMKEY -o ConnectTimeout=15 $VM"
BACKUP_PASS="${BACKUP_PASS:-lockdown}"

NAS_COLD="brian@192.168.200.35"; DIR_COLD="/mnt/The-Pool/ClaudeBackup/band-advance"
NAS_AUDIO="brian@192.168.200.36"; DIR_AUDIO="/mnt/AudioNas/brian/band-advance-backups"

{
echo "=== Band Advance backup installer — $(date) ==="

echo
echo "--- 1. ship backup kit to the VM ---"
tar -C "$HERE/.." -czf /tmp/adv_backup_kit.tgz backup || exit 1
scp -J tds -i "$VMKEY" /tmp/adv_backup_kit.tgz "$VM:/tmp/" || { echo "SCP FAILED"; exit 1; }
$SSH_VM "
  sudo mkdir -p /opt/band-advance
  sudo tar -C /opt/band-advance -xzf /tmp/adv_backup_kit.tgz
  sudo chmod +x /opt/band-advance/backup/*.sh
  sudo mkdir -p /var/backups/band-advance /var/log/band-advance
  rm -f /tmp/adv_backup_kit.tgz
  echo 'installed:'; ls -1 /opt/band-advance/backup/
" || exit 1

echo
echo "--- 2. VM SSH key for the NAS ---"
PUB=$($SSH_VM "
  test -f ~/.ssh/nas_backup || ssh-keygen -q -t ed25519 -N '' -C 'band-advance-backup@n8n-vm' -f ~/.ssh/nas_backup
  chmod 600 ~/.ssh/nas_backup
  cat ~/.ssh/nas_backup.pub
" | tail -1)
if [ -z "$PUB" ] || [[ "$PUB" != ssh-ed25519* ]]; then echo "could not get the VM public key"; exit 1; fi
echo "VM public key: ${PUB:0:48}..."

for pair in "$NAS_COLD|$DIR_COLD|coldstorage" "$NAS_AUDIO|$DIR_AUDIO|audionas"; do
  HOST="${pair%%|*}"; REST="${pair#*|}"; DIR="${REST%%|*}"; NAME="${REST##*|}"
  echo
  echo "--- 3. $NAME ($HOST) ---"
  if ! ssh -i "$NASKEY" -o BatchMode=yes -o ConnectTimeout=15 "$HOST" exit 2>/dev/null; then
    echo "  UNREACHABLE from the Mac — skipped. Re-run this installer when it's up."
    continue
  fi
  ssh -i "$NASKEY" -o BatchMode=yes "$HOST" "
    mkdir -p ~/.ssh '$DIR'
    touch ~/.ssh/authorized_keys
    grep -qF 'band-advance-backup@n8n-vm' ~/.ssh/authorized_keys || echo '$PUB' >> ~/.ssh/authorized_keys
    chmod 700 ~/.ssh; chmod 600 ~/.ssh/authorized_keys
    echo \"  authorized_keys: \$(grep -c . ~/.ssh/authorized_keys) key(s)\"
    echo \"  backup dir:      \$(ls -ld '$DIR' | awk '{print \$1, \$3, \$9}')\"
  "
  echo "  testing VM -> $NAME ..."
  $SSH_VM "ssh -i ~/.ssh/nas_backup -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=15 $HOST 'echo \"  VM can reach $NAME: OK\"'" \
    || echo "  !! VM could NOT reach $NAME"
done

echo
echo "--- 4. GPG passphrase file on the VM ---"
$SSH_VM "printf '%s\n' '$BACKUP_PASS' | sudo tee /etc/band-advance-backup.pass >/dev/null
         sudo chmod 600 /etc/band-advance-backup.pass
         sudo chown root:root /etc/band-advance-backup.pass
         echo '  /etc/band-advance-backup.pass written (0600 root)'"

echo
echo "--- 4b. n8n backup-report workflow ---"
# Resolves the Graph credential id and the internal token on the VM, stamps them
# into the workflow JSON, imports and publishes it. Same pattern as
# send_internal_email.command — the secrets never land in the repo copy.
TOKEN=$($SSH_VM "grep -m1 '^ADVANCE_INTERNAL_TOKEN=' /opt/band-advance/advance.env | cut -d= -f2-" | tail -1)
if [ -z "$TOKEN" ]; then
  echo "  !! ADVANCE_INTERNAL_TOKEN not found in /opt/band-advance/advance.env — skipping workflow deploy"
else
  $SSH_VM '
    cd /opt/n8n
    sudo docker compose exec -T n8n n8n export:credentials --all --output=/tmp/c.json >/dev/null 2>&1
    sudo docker compose exec -T n8n cat /tmp/c.json
    sudo docker compose exec -T n8n rm -f /tmp/c.json
  ' > /tmp/ba_creds.json 2>/dev/null
  CRED=$(python3 - <<'PY'
import json, re
raw = open('/tmp/ba_creds.json').read()
m = re.search(r'\[.*\]', raw, re.S)
creds = json.loads(m.group(0)) if m else []
c = next((c for c in creds if 'graph' in (c.get('name') or '').lower()), None)
print(f"{c['id']} {c['type']}" if c else "")
PY
)
  rm -f /tmp/ba_creds.json
  CRED_ID="${CRED%% *}"; CRED_TYPE="${CRED##* }"
  if [ -z "$CRED_ID" ]; then
    echo "  !! could not resolve the Graph credential — skipping workflow deploy"
  else
    echo "  Graph credential: $CRED_ID ($CRED_TYPE)"
    python3 - "$HERE/../n8n/backup_report.json" "$CRED_ID" "$CRED_TYPE" "$TOKEN" <<'PY' > /tmp/ba_wf.json
import json, sys
path, cid, ctype, token = sys.argv[1:5]
wf = json.load(open(path))
for n in wf["nodes"]:
    if n["type"] == "n8n-nodes-base.code":
        n["parameters"]["jsCode"] = n["parameters"]["jsCode"].replace(
            "REPLACE_WITH_ADVANCE_INTERNAL_TOKEN", token)
    if n["type"] == "n8n-nodes-base.httpRequest":
        n["parameters"]["genericAuthType"] = ctype
        n["credentials"] = {ctype: {"id": cid,
            "name": "Microsoft Graph - Production@3cdc.org (App-only)"}}
print(json.dumps(wf, ensure_ascii=False))
PY
    scp -q -J tds -i "$VMKEY" /tmp/ba_wf.json "$VM:/tmp/ba_wf.json" && rm -f /tmp/ba_wf.json
    $SSH_VM '
      cd /opt/n8n
      sudo docker compose cp /tmp/ba_wf.json n8n:/tmp/ba_wf.json >/dev/null
      sudo docker compose exec -T n8n n8n import:workflow --input=/tmp/ba_wf.json 2>&1 | tail -1
      sudo docker compose exec -T n8n n8n publish:workflow --id=band-advance-backup-report 2>&1 | tail -1
      sudo docker compose exec -T n8n rm -f /tmp/ba_wf.json; rm -f /tmp/ba_wf.json
      # n8n only mounts a newly imported webhook route on restart — without this
      # the first POST to it comes back 404 from a workflow that is actually fine.
      sudo docker compose restart n8n >/dev/null 2>&1
      for i in $(seq 1 24); do
        curl -sf -o /dev/null http://localhost:5678/healthz && break; sleep 5
      done
      sleep 15   # routes register noticeably AFTER /healthz answers 200
    '
    echo "  workflow imported + published (webhook: band-advance-backup-report)"
  fi
fi

echo
echo "--- 5. systemd timer ---"
$SSH_VM "
  sudo install -m 644 /opt/band-advance/backup/band-advance-backup.service /etc/systemd/system/
  sudo install -m 644 /opt/band-advance/backup/band-advance-backup.timer   /etc/systemd/system/
  sudo systemctl daemon-reload
  sudo systemctl enable --now band-advance-backup.timer
  systemctl list-timers band-advance-backup --no-pager | head -3
"

echo
echo "--- 6. first backup run (this takes a couple of minutes) ---"
$SSH_VM "sudo /opt/band-advance/backup/advance_backup.sh 2>&1 | tail -45"
RC=$?

echo
echo "--- verification: what actually landed on each NAS ---"
for pair in "$NAS_COLD|$DIR_COLD|coldstorage" "$NAS_AUDIO|$DIR_AUDIO|audionas"; do
  HOST="${pair%%|*}"; REST="${pair#*|}"; DIR="${REST%%|*}"; NAME="${REST##*|}"
  echo "  [$NAME]"
  ssh -i "$NASKEY" -o BatchMode=yes -o ConnectTimeout=15 "$HOST" "ls -lh '$DIR' 2>/dev/null | tail -6 | sed 's/^/    /'" \
    2>/dev/null || echo "    unreachable"
done

echo
echo "=== installer done (backup exit $RC) — $(date) ==="
echo "Weekly from now on: Sundays 03:15."
echo "Manual run:  ssh -J tds -i ~/.ssh/proxmox_tds brian@192.168.200.84 'sudo /opt/band-advance/backup/advance_backup.sh'"
echo "Restore:     ~/Documents/Claude/Code/BandInfoForm/backup/restore_advance.command"
} 2>&1 | tee "$LOG"
