#!/usr/bin/env bash
set -uo pipefail
J="ssh -J tds -o StrictHostKeyChecking=no -i $HOME/.ssh/proxmox_tds brian@192.168.200.84"

echo "============ 1. DNS resolution of kb.tinydoorstudios.com ============"
dig +short kb.tinydoorstudios.com
echo "CNAME chain:"
dig CNAME kb.tinydoorstudios.com

echo; echo "============ 2. cloudflared log — live requests (last 20 lines) ============"
$J "sudo journalctl -u cloudflared -n 20 --no-pager 2>&1 | grep -E 'kb|request|connec|route|error|host' | tail -20 || echo '(no matching log lines)'"

echo; echo "============ 3. make public request then immediately check cloudflared log ============"
echo "Making public request..."
curl -sI "https://kb.tinydoorstudios.com/assets/sops/fsq/fsq-m32-failover-sop.pdf" 2>&1 | head -3
sleep 2
echo "cloudflared log after request:"
$J "sudo journalctl -u cloudflared -n 5 --no-pager 2>&1"

echo; echo "============ 4. add httpHostHeader to cloudflared config for kb entry ============"
$J "python3 - << 'PYEOF'
import yaml, re

path = '/etc/cloudflared/config.yml'
with open(path) as f:
    content = f.read()

# Check if already has httpHostHeader
if 'httpHostHeader' in content:
    print('ALREADY HAS httpHostHeader — skipping')
    exit(0)

# Simple text replacement: add originRequest under kb entry
# Find the kb hostname block and add originRequest
new_content = re.sub(
    r'(- hostname: kb\.tinydoorstudios\.com\n\s+service: http://127\.0\.0\.1:8088)',
    r'\1\n    originRequest:\n      httpHostHeader: kb.tinydoorstudios.com',
    content
)
if new_content == content:
    print('ERROR: could not find kb entry in config — check config manually')
    exit(1)

with open(path, 'w') as f:
    f.write(new_content)
print('OK: added httpHostHeader: kb.tinydoorstudios.com')
print('New config:')
print(open(path).read())
PYEOF
"

echo; echo "============ 5. restart cloudflared with new config ============"
$J "sudo systemctl restart cloudflared && echo 'restarted OK'"
sleep 5

echo; echo "============ 6. test public URL ============"
curl -sI "https://kb.tinydoorstudios.com/assets/sops/fsq/fsq-m32-failover-sop.pdf" 2>&1 | grep -E "HTTP|content-type|content-length|server"

echo; echo "============ 7. nginx log — did the public request appear? ============"
$J "docker logs landing --tail 5 2>&1"

echo; echo "============ done ============"
echo "Press any key to close…"; read -n 1 -s
