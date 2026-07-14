#!/usr/bin/env bash
# fix-downloads-path.sh
# Serve downloads under /downloads/ (a path the Cloudflare /assets/ intercept
# rule does NOT match) so requests reach the origin nginx like wiki pages do.
# Installs exact nginx.conf, validates, auto-rolls-back, then verifies via Cloudflare.
#
# Run:  bash "/Users/brianlloyd/Documents/Claude/audio/N8n/fix-downloads-path.sh"

set -uo pipefail
SSH_OPTS=(-J tds -i ~/.ssh/proxmox_tds -o StrictHostKeyChecking=no)
VM="brian@192.168.200.84"
N8N() { ssh "${SSH_OPTS[@]}" "$VM" "$@"; }
KB="https://kb.tinydoorstudios.com"
SLUG="2026-06-20-blue-eighty-eight"
BASE="/Users/brianlloyd/Documents/Claude/audio/N8n"
TS="$(date +%Y%m%d-%H%M%S)"
exec > >(tee "$BASE/fix-downloads-path.log") 2>&1
echo "=== fix-downloads-path $TS ==="

echo "[1] Backup current nginx.conf…"
N8N "sudo cp /opt/landing/nginx.conf /opt/landing/nginx.conf.bak.$TS" || { echo "backup failed"; exit 1; }

echo "[2] Write exact nginx.conf (adds /downloads/)…"
cat > /tmp/landing-nginx.conf <<'EOF'
server {
    listen 8088 default_server;
    server_name tinydoorstudios.com;
    root /usr/share/nginx/html;
    index index.html;
    location / { try_files $uri $uri/ /index.html; }
}

server {
    listen 8088;
    server_name kb.tinydoorstudios.com;

    location /downloads/ {
        alias /kb-assets/;
        autoindex off;
        add_header Content-Disposition attachment;
        add_header Cache-Control "no-store, private, must-revalidate";
    }

    location /assets/ {
        alias /kb-assets/;
        autoindex off;
        add_header Content-Disposition attachment;
        add_header Cache-Control "no-store, private, must-revalidate";
    }

    location / {
        proxy_pass http://192.168.200.126:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 300s;
    }
}

server {
    listen 8088;
    server_name n8n.tinydoorstudios.com;

    auth_basic "Tiny Door Studios";
    auth_basic_user_file /etc/nginx/.htpasswd;

    client_max_body_size 100m;

    location / {
        proxy_pass http://127.0.0.1:5678;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }
}
EOF
scp "${SSH_OPTS[@]}" /tmp/landing-nginx.conf "$VM:/tmp/landing-nginx.conf" >/dev/null || { echo "scp failed"; exit 1; }
N8N 'sudo cp /tmp/landing-nginx.conf /opt/landing/nginx.conf' || { echo "install failed"; exit 1; }

rollback() {
  echo "!!! $* — ROLLING BACK"
  N8N "sudo cp /opt/landing/nginx.conf.bak.$TS /opt/landing/nginx.conf"
  CID="$(N8N "sudo docker ps --format '{{.Names}}' | grep -i landing | head -1" | tr -d '\r')"
  N8N "sudo docker exec $CID nginx -s reload" >/dev/null 2>&1
  exit 1
}

echo "[3] Validate + reload nginx…"
CID="$(N8N "sudo docker ps --format '{{.Names}}' | grep -i landing | head -1" | tr -d '\r')"
N8N "sudo docker exec $CID nginx -t" >/dev/null 2>&1 || rollback "nginx -t failed"
N8N "sudo docker exec $CID nginx -s reload" >/dev/null 2>&1 || rollback "reload failed"
echo "   reloaded (container: $CID)"

echo "[4] Push markdown + force wiki sync…"
[ -x "$HOME/.claude/scripts/kb-git-push.sh" ] && "$HOME/.claude/scripts/kb-git-push.sh" >/dev/null 2>&1 && echo "   pushed" || echo "   (push best-effort)"
ssh tds 'pct exec 101 -- bash -s' <<'EOF' >/dev/null 2>&1 && echo "   wiki sync triggered" || echo "   (wiki sync best-effort)"
curl -s -X POST http://127.0.0.1:3000/graphql -H "Content-Type: application/json" --data '{"query":"mutation{storage{executeAction(handler:\"git\",targetKey:\"sync\"){succeeded}}}"}'
EOF

echo "[5] Verify /downloads/ through Cloudflare:"
ALLOK=1
for f in foh-channel-processing.pdf input-list.xlsx blue-eighty-eight.ses handoff.pdf; do
  code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 30 "$KB/downloads/shows/$SLUG/$f")"
  echo "     $code  /downloads/shows/$SLUG/$f"
  [ "$code" = "200" ] || ALLOK=0
done

echo ""
if [ "$ALLOK" = "1" ]; then
  echo "============================================================"
  echo " DONE — downloads work through Cloudflare under /downloads/."
  echo " Open the show page on your phone and tap a file."
  echo "============================================================"
else
  echo "Still failing — then the Cloudflare intercept also covers /downloads/,"
  echo "and only removing that route in the Cloudflare dashboard will fix it."
fi
