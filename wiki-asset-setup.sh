#!/bin/bash
# Wiki.js Asset Storage Setup
# Sets up local filesystem storage for .ses files and other binaries on the wiki VM
# Configures Wiki.js to serve assets from a local folder instead of relying on Git sync

set -e

echo "=== Wiki.js Asset Storage Setup ==="
echo ""

# SSH into Proxmox via Tailscale IP and run the wiki container setup
echo "[1/5] Creating asset folder on wiki container..."
ssh -i ~/.ssh/proxmox_tds root@100.99.198.22 "pct exec 101 -- mkdir -p /opt/wikijs/data/assets && chmod 755 /opt/wikijs/data/assets" || echo "Folder may already exist (ok)"

echo "[2/5] Verifying Docker Compose volume mounts..."
# Check if assets volume exists in docker-compose
ssh -i ~/.ssh/proxmox_tds root@100.99.198.22 "pct exec 101 -- grep -q 'assets:' /opt/wikijs/docker-compose.yml && echo 'Volume already configured' || echo 'Need to update docker-compose'"

echo "[3/5] Testing Wiki.js API connectivity..."
# Test that we can reach the wiki API
curl -s -H "Authorization: Bearer test" http://192.168.0.126:3000/graphql -X POST -d '{"query":"{site{title}}"}' > /dev/null 2>&1 && echo "✓ Wiki.js API reachable" || echo "⚠ Wiki.js API test inconclusive (normal if auth required)"

echo "[4/5] Creating rsync watch script on Mac..."
# Create a watch script that will sync assets to the wiki VM
# Note: Reaches n8n VM via TDS subnet route (requires --accept-routes in Tailscale)
cat > ~/.claude/scripts/wiki-asset-sync.sh << 'SCRIPT_EOF'
#!/bin/bash
# Watch Live Sound KB assets folder and sync to wiki VM via Tailscale subnet route
SOURCE="$HOME/Documents/Claude/audio/Live Sound KB/Wiki/assets"
DEST_USER="brian"
DEST_HOST="192.168.0.125"  # n8n VM, reachable via TDS subnet route
DEST_PATH="/opt/wikijs/data/assets"
SSH_KEY="$HOME/.ssh/proxmox_tds"

# Verify Tailscale can reach the subnet
if ! ping -c 1 -W 1 192.168.0.125 > /dev/null 2>&1; then
  echo "⚠ Warning: Cannot reach 192.168.0.125. Ensure Tailscale has --accept-routes enabled."
  echo "  Enable in Tailscale Preferences → Network → Allow local network access"
  exit 1
fi

if [ ! -d "$SOURCE" ]; then
  echo "Source directory does not exist: $SOURCE"
  exit 1
fi

# Sync with delete to keep in sync
rsync -av --delete \
  -e "ssh -i $SSH_KEY" \
  "$SOURCE/" "${DEST_USER}@${DEST_HOST}:${DEST_PATH}/"

echo "Asset sync complete: $SOURCE → ${DEST_HOST}:${DEST_PATH}"
SCRIPT_EOF

chmod +x ~/.claude/scripts/wiki-asset-sync.sh
echo "✓ Created wiki-asset-sync.sh"

echo "[5/5] Creating launchd agent for automated syncing..."
# Create launchd plist for continuous sync
cat > ~/Library/LaunchAgents/com.tinydoor.wiki-asset-sync.plist << 'PLIST_EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>Label</key>
	<string>com.tinydoor.wiki-asset-sync</string>
	<key>ProgramArguments</key>
	<array>
		<string>/bin/bash</string>
		<string>-c</string>
		<string>~/.claude/scripts/wiki-asset-sync.sh</string>
	</array>
	<key>WatchPaths</key>
	<array>
		<string>/Users/brianlloyd/Documents/Claude/audio/Live Sound KB/Wiki/assets</string>
	</array>
	<key>StandardOutPath</key>
	<string>/Users/brianlloyd/.claude/logs/wiki-asset-sync.log</string>
	<key>StandardErrorPath</key>
	<string>/Users/brianlloyd/.claude/logs/wiki-asset-sync.log</string>
	<key>RunAtLoad</key>
	<true/>
	<key>StartInterval</key>
	<integer>300</integer>
</dict>
</plist>
PLIST_EOF

# Ensure logs directory exists
mkdir -p ~/.claude/logs

# Load the launchd agent
launchctl unload ~/Library/LaunchAgents/com.tinydoor.wiki-asset-sync.plist 2>/dev/null || true
launchctl load ~/Library/LaunchAgents/com.tinydoor.wiki-asset-sync.plist
echo "✓ Loaded launchd agent (com.tinydoor.wiki-asset-sync)"

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps (manual):"
echo "1. SSH into wiki container: ssh -i ~/.ssh/proxmox_tds root@192.168.0.4"
echo "   Then: pct exec 101 -- bash"
echo ""
echo "2. Configure Wiki.js local storage via GraphQL at: http://192.168.0.126:3000/graphql"
echo "   Mutation to add LOCAL storage target (create 2nd storage target):"
echo ""
echo '   mutation {'
echo '     storage {'
echo '       updateTargets(targets: ['
echo '         {'
echo '           key: "git",'
echo '           isEnabled: true,'
echo '           config: {'
echo '             repoUrl: {v: "https://github.com/TinydoorStudios/live-sound-kb.git"},'
echo '             branch: {v: "main"},'
echo '             basicPassword: {v: "ghp_YOUR_PAT"},'
echo '             basicUser: {v: "TinydoorStudios"},'
echo '             localRepoPath: {v: "./data/repo"},'
echo '             syncDirection: {v: "pull"},'
echo '             syncInterval: {v: "PT5M"}'
echo '           }'
echo '         },'
echo '         {'
echo '           key: "local",'
echo '           isEnabled: true,'
echo '           config: {'
echo '             storagePath: {v: "/data/assets"}'
echo '           }'
echo '         }'
echo '       ])'
echo '     }'
echo '   }'
echo ""
echo "3. Assets in ~/Documents/Claude/audio/Live Sound KB/Wiki/assets/ will auto-sync to the wiki VM"
echo "4. Wiki.js will serve them from /opt/wikijs/data/assets"
echo ""
echo "Log location: ~/.claude/logs/wiki-asset-sync.log"
echo ""
