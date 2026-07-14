#!/usr/bin/env bash
# sync-and-verify.sh — push renamed assets to the VM, refresh the wiki page,
# and verify the new download URLs through Cloudflare.
#
# Run:  bash "/Users/brianlloyd/Documents/Claude/audio/N8n/sync-and-verify.sh"

set -uo pipefail
SSH_OPTS=(-J tds -i ~/.ssh/proxmox_tds -o StrictHostKeyChecking=no)
VM="brian@192.168.200.84"
ASSETS_SRC="/Users/brianlloyd/Documents/Claude/audio/Live Sound KB/Wiki/assets"
KB="https://kb.tinydoorstudios.com"
SLUG="2026-06-20-blue-eighty-eight"
BASE="/Users/brianlloyd/Documents/Claude/audio/N8n"
LOG="$BASE/sync-and-verify.log"
exec > >(tee "$LOG") 2>&1
echo "=== sync-and-verify $(date) ==="

echo "[1] Rsync renamed assets → VM (removes old-named files)…"
rsync -a --delete --chmod=D755,F644 -e "ssh ${SSH_OPTS[*]}" "$ASSETS_SRC/" "$VM:/opt/kb-assets/" || { echo "   rsync FAILED"; exit 1; }
ssh "${SSH_OPTS[@]}" "$VM" 'sudo chmod -R a+rX /opt/kb-assets' || true
echo "   files now on VM:"
ssh "${SSH_OPTS[@]}" "$VM" "ls -1 /opt/kb-assets/shows/$SLUG/ | sed 's/^/     /'"

echo "[2] Push markdown so the wiki page shows the new links…"
if [ -x "$HOME/.claude/scripts/kb-git-push.sh" ]; then
  "$HOME/.claude/scripts/kb-git-push.sh" >/dev/null 2>&1 && echo "   pushed" || echo "   push returned nonzero (continuing)"
else
  echo "   kb-git-push.sh not found — page links will refresh on the next auto-push"
fi

echo "[3] Force Wiki.js to pull latest markdown…"
ssh tds 'pct exec 101 -- bash -s' <<'EOF' >/dev/null 2>&1 && echo "   sync triggered" || echo "   (sync best-effort)"
curl -s -X POST http://127.0.0.1:3000/graphql -H "Content-Type: application/json" --data '{"query":"mutation{storage{executeAction(handler:\"git\",targetKey:\"sync\"){succeeded}}}"}'
EOF

echo "[4] Wait…"; sleep 5
echo "[5] Verify NEW public download URLs (through Cloudflare):"
ALLOK=1
for f in foh-channel-processing.pdf input-list.xlsx blue-eighty-eight.ses handoff.pdf; do
  code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 30 "$KB/assets/shows/$SLUG/$f")"
  echo "     $code  $f"
  [ "$code" = "200" ] || ALLOK=0
done

echo ""
if [ "$ALLOK" = "1" ]; then
  echo "============================================================"
  echo " DONE — every download returns 200 through Cloudflare."
  echo " Open the show page from your phone and tap a file."
  echo "============================================================"
else
  echo "Not all 200 — paste me the output and I'll finish it."
fi
