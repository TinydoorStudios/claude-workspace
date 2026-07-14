#!/bin/bash
# Extract GitHub PAT from Wiki.js database

ssh -i ~/.ssh/proxmox_tds root@100.99.198.22 << 'EOF'
pct exec 101 -- docker exec wikijs-db-1 psql -U wiki -d wiki -t -c "SELECT config FROM config WHERE key = 'storage';" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if 'git' in data and 'config' in data['git']:
        pat = data['git']['config'].get('basicPassword')
        if pat:
            print('GITHUB_PAT=' + pat)
        else:
            print('PAT not found in config')
except Exception as e:
    print(f'Error: {e}')
"
EOF
