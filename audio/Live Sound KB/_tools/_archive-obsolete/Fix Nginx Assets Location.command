#!/usr/bin/env bash
set -uo pipefail
J="ssh -J tds -o StrictHostKeyChecking=no -i $HOME/.ssh/proxmox_tds brian@192.168.200.84"

echo "============ 1. current /opt/landing/nginx.conf ============"
$J "cat /opt/landing/nginx.conf"

echo; echo "============ 2. back up config ============"
$J "cp /opt/landing/nginx.conf /opt/landing/nginx.conf.bak && echo 'backup created: /opt/landing/nginx.conf.bak'"

echo; echo "============ 3. inject /assets/ location block ============"
# Use Python to insert the location /assets/ block before the first "location /" block
$J "python3 - << 'PYEOF'
import re, shutil

path = '/opt/landing/nginx.conf'
with open(path) as f:
    content = f.read()

# Check if already patched
if 'location /assets/' in content:
    print('ALREADY PATCHED — /assets/ block already present')
    exit(0)

# Insert before the first 'location /' block
assets_block = '''    location /assets/ {
        alias /kb-assets/;
        autoindex off;
    }

'''
# Find the first 'location /' and insert before it
new_content = re.sub(r'(\s+location\s+/\s*\{)', '\n' + assets_block + r'\1', content, count=1)
if new_content == content:
    print('ERROR: could not find location / block to insert before — check config manually')
    exit(1)

with open(path, 'w') as f:
    f.write(new_content)
print('OK: /assets/ block inserted')
PYEOF
"

echo; echo "============ 4. show updated config ============"
$J "cat /opt/landing/nginx.conf"

echo; echo "============ 5. test nginx config ============"
$J "docker exec landing nginx -t 2>&1"

echo; echo "============ 6. reload nginx ============"
$J "docker exec landing nginx -s reload && echo 'nginx reloaded OK' || echo 'ERROR: reload failed'"

echo; echo "============ 7. verify SOP URLs return PDF content ============"
sleep 2
$J "curl -s -o /dev/null -w 'fsq-m32-failover-sop: HTTP %{http_code} | type: %{content_type} | bytes: %{size_download}\n' \
    http://127.0.0.1:8088/assets/sops/fsq/fsq-m32-failover-sop.pdf"
$J "curl -s -o /dev/null -w 'memo-crowd-mics: HTTP %{http_code} | type: %{content_type} | bytes: %{size_download}\n' \
    http://127.0.0.1:8088/assets/sops/memo/memo-crowd-mics.pdf"
$J "curl -s -o /dev/null -w 'esp-led-board: HTTP %{http_code} | type: %{content_type} | bytes: %{size_download}\n' \
    http://127.0.0.1:8088/assets/sops/esp/esp-led-board-sop.pdf"
$J "curl -s -o /dev/null -w 'wp-clearcom: HTTP %{http_code} | type: %{content_type} | bytes: %{size_download}\n' \
    http://127.0.0.1:8088/assets/sops/wp/wp-clearcom-main-stage.pdf"

echo; echo "============ done — check the types above should be application/pdf ============"
echo "Press any key to close…"; read -n 1 -s
