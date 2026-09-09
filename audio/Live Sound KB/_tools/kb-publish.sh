#!/usr/bin/env bash
# =============================================================================
# kb-publish.sh — Live Sound KB → Wiki.js publisher
# Runs ON BRIAN'S MAC (needs Tailscale + the proxmox_tds SSH key + LAN access).
# Does the full publish in one shot:
#   1. clear any stale git lock
#   2. commit + push the wiki repo to GitHub  (Wiki.js pulls .md from here)
#   3. rsync binary assets to the n8n VM      (served at /assets/ for downloads)
#   4. force Wiki.js to git-sync now
#   5. (optional) rebuild the Wiki.js left-nav sidebar from kb-nav.json
#   6. verify a sample download URL actually resolves
#
# Usage:   ./kb-publish.sh ["commit message"]
# Config:  override defaults in ~/.claude/kb-secrets.sh (see kb-secrets.example.sh)
# =============================================================================
set -uo pipefail

# resolve the script's own dir so secrets/nav paths work no matter how it's launched
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---- config (defaults from the 2026-06-11 asset-serving handoff) ----
SECRETS="${KB_SECRETS:-$SCRIPT_DIR/kb-secrets.sh}"
[ -f "$SECRETS" ] || SECRETS="$HOME/.claude/kb-secrets.sh"
# shellcheck disable=SC1090
[ -f "$SECRETS" ] && source "$SECRETS"

WIKI="${KB_WIKI:-$HOME/Documents/Claude/audio/Live Sound KB/Wiki}"
SSH_JUMP="${KB_SSH_JUMP:-tds}"                         # ssh alias → Proxmox host (Tailscale)
SSH_KEY="${KB_SSH_KEY:-$HOME/.ssh/proxmox_tds}"
N8N_USER="${KB_N8N_USER:-brian}"
N8N_HOST="${KB_N8N_HOST:-192.168.200.84}"
KB_ASSETS="${KB_ASSETS_DIR:-/opt/kb-assets}"
WIKI_CT="${KB_WIKI_CT:-101}"
WIKI_LAN="${KB_WIKI_LAN:-192.168.200.126:3000}"        # Wiki.js GraphQL, LAN-direct
PUBLIC_URL="${KB_PUBLIC_URL:-https://kb.tinydoorstudios.com}"
BASIC_AUTH="${KB_BASIC_AUTH:-}"                         # "user:pass" for verify step (set in secrets)
WIKI_API_KEY="${KB_WIKI_API_KEY:-}"                     # Wiki.js API token; needed only for nav rebuild
NAV_JSON="${KB_NAV_JSON:-$SCRIPT_DIR/kb-nav.json}"
MSG="${1:-KB publish $(date '+%Y-%m-%d %H:%M')}"

log(){ printf '\n\033[1;36m▶ %s\033[0m\n' "$*"; }
ok(){ printf '\033[1;32m  ✓ %s\033[0m\n' "$*"; }
warn(){ printf '\033[1;33m  ! %s\033[0m\n' "$*"; }
die(){ printf '\033[1;31m  ✗ %s\033[0m\n' "$*"; exit 1; }

cd "$WIKI" || die "wiki repo not found: $WIKI"

# ---- 1. clear stale lock ----
log "Clearing any stale git lock"
rm -f .git/index.lock && ok "lock clear"

# ---- 2. commit + push to GitHub ----
log "Commit + push to GitHub"
git add -A
if git diff --cached --quiet; then
  warn "nothing to commit — pushing current HEAD anyway"
else
  git commit -m "$MSG" >/dev/null && ok "committed: $MSG"
fi
git push origin main && ok "pushed to origin/main" || warn "git push FAILED (deploy key? run: ssh -T git@github.com) — continuing to asset sync anyway"

# ---- 3. rsync binary assets to the n8n VM ----
log "rsync assets → n8n VM ($N8N_HOST:$KB_ASSETS)"
if [ -d "$WIKI/assets" ]; then
  rsync -av --delete --chmod=Da+rx,Fa+r -e "ssh -J $SSH_JUMP -i $SSH_KEY" \
    "$WIKI/assets/" "$N8N_USER@$N8N_HOST:$KB_ASSETS/" \
    && ok "assets synced (server copy in place for cross-device download)" \
    || die "rsync failed — is Tailscale up? is $SSH_KEY present?"
else
  warn "no assets/ dir — skipping asset sync"
fi

# ---- 4. publish pages to Wiki.js now (skip waiting on the launchd watcher) ----
# Wiki.js git storage is permanently DISABLED in this install (confirmed 2026-09-08:
# the storage{executeAction} mutation returns "Invalid or Inactive Storage Target"
# regardless of host/network path) — content only ever reaches the live site via
# kb-publish-pages.py hitting the Wiki.js pages API. That's what the launchd watcher
# runs every 5 min; call it here too so a manual publish doesn't have to wait on it.
log "Publish pages to Wiki.js"
if [ -n "$WIKI_API_KEY" ]; then
  KB_WIKI_API_KEY="$WIKI_API_KEY" python3 "$HOME/.claude/scripts/kb-publish-pages.py" \
    && ok "pages published" || warn "page publish failed — check KB_WIKI_API_KEY / kb.tinydoorstudios.com reachability"
else
  warn "publish skipped — set KB_WIKI_API_KEY in secrets (the launchd watcher will still catch it within 5 min)"
fi

# ---- 5. (optional) rebuild the left-nav sidebar ----
# Uses the public HTTPS endpoint, not the LAN address — the LAN path to CT101
# (192.168.200.126) isn't reliably reachable from the Mac depending on network
# (confirmed 2026-09-08: ARP silently fails even on the same subnet), while the
# public endpoint (same one kb-publish-pages.py uses) works from anywhere.
if [ -n "$WIKI_API_KEY" ] && [ -f "$NAV_JSON" ]; then
  log "Rebuilding Wiki.js navigation sidebar from $(basename "$NAV_JSON")"
  TREE=$(python3 "$SCRIPT_DIR/kb-nav-build.py" "$NAV_JSON") || warn "nav build failed"
  if [ -n "${TREE:-}" ]; then
    curl -s -X POST "$PUBLIC_URL/graphql" \
      -H "Authorization: Bearer $WIKI_API_KEY" \
      -H "Content-Type: application/json" \
      -d "$TREE" >/dev/null \
      && ok "nav sidebar updated" || warn "nav update failed (check WIKI_API_KEY / LAN reachability)"
  fi
else
  warn "nav rebuild skipped — set KB_WIKI_API_KEY in secrets to enable the left sidebar"
fi

# ---- 6. verify a sample download URL ----
log "Verifying a sample download URL"
SAMPLE=$(cd "$WIKI" && ls assets/shows/*/*.pdf 2>/dev/null | head -1)
if [ -n "$SAMPLE" ] && [ -n "$BASIC_AUTH" ]; then
  ENC=$(python3 - "$SAMPLE" <<'PY'
import sys,urllib.parse
print('/'+'/'.join(urllib.parse.quote(p) for p in sys.argv[1].split('/')))
PY
)
  CODE=$(curl -s -o /dev/null -w "%{http_code}" -u "$BASIC_AUTH" "$PUBLIC_URL$ENC")
  [ "$CODE" = "200" ] && ok "download OK (200): $PUBLIC_URL$ENC" || warn "download returned $CODE: $PUBLIC_URL$ENC"
else
  warn "verify skipped (no sample PDF or no KB_BASIC_AUTH set)"
fi

log "Done."
