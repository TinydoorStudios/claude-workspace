#!/usr/bin/env bash
# DigiBot installer — runs on the Mac, ships the service to the n8n VM and stands it up.
#   deploy/install.sh            first install or code update (rebuilds the api image)
#   deploy/install.sh --n8n      also (re)import the n8n workflows + placeholder Slack credential and restart n8n
#
# Secrets are moved server-to-server through ssh pipes and never printed:
#   DIGICO_WIKI_KEY  ← /root/.digico-apikey on CT 101 (via tds)
#   KB_WIKI_KEY      ← audio/Live Sound KB/_tools/kb-secrets.sh on this Mac
#   GROQ_API_KEY     ← the n8n "Triage LLM" header credential, exported decrypted on the VM
# Existing values in /opt/digibot/.env are kept; only empty ones are filled.
set -euo pipefail
cd "$(dirname "$0")/.."
VM="brian@192.168.200.84"; SSH=(ssh -o ConnectTimeout=10 -J tds -i "$HOME/.ssh/proxmox_tds" "$VM")
REMOTE=/opt/digibot

tar -czf /tmp/digibot.tgz service deploy/docker-compose.yml deploy/env.example n8n
scp -q -o ProxyJump=tds -i "$HOME/.ssh/proxmox_tds" /tmp/digibot.tgz "$VM:/tmp/digibot.tgz"

"${SSH[@]}" 'sudo mkdir -p '"$REMOTE"' && sudo tar -C '"$REMOTE"' -xzf /tmp/digibot.tgz && rm /tmp/digibot.tgz
  cd '"$REMOTE"' && sudo mv -f deploy/docker-compose.yml docker-compose.yml && sudo mv -f deploy/env.example env.example && sudo rmdir deploy 2>/dev/null || true
  if [ ! -f .env ]; then sudo cp env.example .env; sudo chmod 600 .env; sudo sed -i "s/^DIGIBOT_DB_PASSWORD=.*/DIGIBOT_DB_PASSWORD=$(openssl rand -hex 16)/" .env; fi
  echo "tree in place"'

# --- secrets: fill only if empty -------------------------------------------------------------
fill() {  # fill VAR <<< value-on-stdin
  "${SSH[@]}" 'V="'"$1"'"; read -r val; cur=$(sudo grep -E "^$V=" '"$REMOTE"'/.env | cut -d= -f2-);
    if [ -z "$cur" ] && [ -n "$val" ]; then sudo sed -i "s|^$V=.*|$V=$val|" '"$REMOTE"'/.env; echo "filled $V"; else echo "kept $V"; fi'
}
ssh -o ConnectTimeout=10 tds 'pct exec 101 -- bash -c "source /root/.digico-apikey; printf %s \"\$API_KEY\""' | fill DIGICO_WIKI_KEY
( set +u; source "$HOME/Documents/Claude/audio/Live Sound KB/_tools/kb-secrets.sh"; printf %s "${KB_WIKI_API_KEY:-}" ) | fill KB_WIKI_KEY
scp -q -o ProxyJump=tds -i "$HOME/.ssh/proxmox_tds" deploy/groq_from_n8n.py "$VM:/tmp/groq_from_n8n.py"
"${SSH[@]}" 'cd /opt/n8n && sudo docker compose exec -T n8n n8n export:credentials --id=GearTixTriageLLM --decrypted 2>/dev/null | python3 /tmp/groq_from_n8n.py; rm -f /tmp/groq_from_n8n.py' | fill GROQ_API_KEY

# --- build + up ------------------------------------------------------------------------------
"${SSH[@]}" 'cd '"$REMOTE"' && sudo docker compose build --quiet api && sudo docker compose up -d && sleep 6 && curl -s -m 5 localhost:8098/health; echo'

if [ "${1:-}" = "--n8n" ]; then
  # n8n can only read files inside its container: push them through docker cp.
  "${SSH[@]}" 'for f in '"$REMOTE"'/n8n/*.json; do sudo docker cp "$f" n8n-n8n-1:/tmp/$(basename "$f"); done
    cd /opt/n8n
    sudo docker compose exec -T n8n sh -c "n8n import:credentials --input=/tmp/credentials_digibot.json" 2>&1 | grep -v "^Postgres 16\|migration lock" || true
    for f in digibot_slack digibot_nightly digibot_weekly; do sudo docker compose exec -T n8n sh -c "n8n import:workflow --input=/tmp/$f.json && n8n publish:workflow --id=$f" 2>&1 | grep -v "^Postgres 16\|migration lock" || true; done
    sudo docker compose restart n8n >/dev/null && echo "n8n restarted (routes mount ~20s after healthz)"'
fi
echo "done"
