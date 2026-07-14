#!/bin/bash
# Extract existing GitHub PAT from Wiki.js database

TAILSCALE_IP="100.99.198.22"
SSH_KEY="$HOME/.ssh/proxmox_tds"

echo "Extracting GitHub PAT from Wiki.js database..."
echo ""

# Query the wiki postgres database directly to get the storage config
# The storage targets are stored in the "config" table as JSON
RESULT=$(ssh -i $SSH_KEY root@$TAILSCALE_IP << 'EOF'
pct exec 101 -- docker exec wikijs-postgres-1 psql -U wiki -d wiki -t -c \
  "SELECT config FROM config WHERE key = 'storage';" 2>/dev/null || echo "null"
EOF
)

if [ "$RESULT" = "null" ] || [ -z "$RESULT" ]; then
  echo "Could not extract PAT from database."
  echo ""
  echo "Option 1: Create a new GitHub PAT"
  echo "  1. Go to https://github.com/settings/tokens"
  echo "  2. Click 'Generate new token (classic)'"
  echo "  3. Name: 'TDS Wiki KB'"
  echo "  4. Select scopes: repo (full control)"
  echo "  5. Generate and copy the token"
  echo "  6. Run: export GITHUB_PAT='ghp_xxxxx...'"
  echo ""
  echo "Option 2: Use Wiki.js web UI"
  echo "  1. Go to http://192.168.0.126:3000"
  echo "  2. Admin → Storage → Git"
  echo "  3. Enter/verify your PAT there"
  echo ""
  exit 1
fi

echo "✓ Found storage config in database"
echo ""
echo "Extracting PAT..."

# Parse the JSON to get the basicPassword field
PAT=$(echo "$RESULT" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if 'git' in data and 'config' in data['git']:
        pat = data['git']['config'].get('basicPassword', '')
        print(pat)
except:
    print('')
" 2>/dev/null)

if [ -n "$PAT" ] && [ "$PAT" != "null" ] && [ "$PAT" != "" ]; then
  echo "✓ PAT extracted successfully"
  echo ""
  echo "Using existing PAT to configure local asset storage..."
  echo ""

  # Use the extracted PAT
  export GITHUB_PAT="$PAT"
  bash /Users/brianlloyd/Documents/Claude/wiki-complete-setup.sh
else
  echo "Could not parse PAT from config"
  echo ""
  echo "Please manually create a GitHub PAT:"
  echo "1. Go to https://github.com/settings/tokens"
  echo "2. Click 'Generate new token (classic)'"
  echo "3. Name: 'TDS Wiki KB'"
  echo "4. Select scope: 'repo'"
  echo "5. Generate and copy"
  echo ""
  echo "Then run:"
  echo "  export GITHUB_PAT='ghp_xxxxx...'"
  echo "  bash /Users/brianlloyd/Documents/Claude/wiki-complete-setup.sh"
fi
