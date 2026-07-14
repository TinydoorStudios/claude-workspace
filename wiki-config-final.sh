#!/bin/bash
# Final Wiki.js Configuration - creates folder, updates docker-compose, restarts container

set -e

TAILSCALE_IP="100.99.198.22"
SSH_KEY="$HOME/.ssh/proxmox_tds"

echo "=== Wiki.js Final Configuration ==="
echo ""

echo "[1/3] Creating assets folder on wiki container..."
ssh -i $SSH_KEY root@$TAILSCALE_IP "pct exec 101 -- bash -c 'mkdir -p /opt/wikijs/data/assets && chown 1000:1000 /opt/wikijs/data/assets && chmod 755 /opt/wikijs/data/assets'"
echo "✓ Assets folder created and mounted"

echo ""
echo "[2/3] Checking docker-compose.yml and adding assets volume..."
# Get current docker-compose content
CURRENT=$(ssh -i $SSH_KEY root@$TAILSCALE_IP "pct exec 101 -- cat /opt/wikijs/docker-compose.yml")

# Check if assets volume already exists
if echo "$CURRENT" | grep -q "assets:"; then
  echo "✓ Assets volume already configured"
else
  echo "Adding assets volume to docker-compose..."
  ssh -i $SSH_KEY root@$TAILSCALE_IP << 'DOCKER_EOF'
pct exec 101 -- bash << 'EOF'
cd /opt/wikijs
# Backup original
cp docker-compose.yml docker-compose.yml.backup

# Add assets volume to the wiki service volumes section
# This is a simple append - assumes standard formatting
sed -i.bak '/wiki:/,/^[^ ]/ {
  /volumes:$/a\
        - ./data/assets:/data/assets
}' docker-compose.yml

echo "✓ docker-compose.yml updated"
EOF
DOCKER_EOF
fi

echo ""
echo "[3/3] Restarting wiki container to apply changes..."
ssh -i $SSH_KEY root@$TAILSCALE_IP "pct exec 101 -- bash -c 'cd /opt/wikijs && docker compose restart wiki'"
echo "✓ Container restarted"

echo ""
echo "=== Wiki Container Setup Complete ==="
echo ""
echo "Next: Configure Wiki.js storage via GraphQL"
echo ""
echo "Use curl or Postman to POST to: http://192.168.0.126:3000/graphql"
echo ""
echo 'Paste this GraphQL mutation (with your actual GitHub PAT):'
echo ""
cat << 'MUTATION'
mutation {
  storage {
    updateTargets(targets: [
      {
        key: "git",
        isEnabled: true,
        config: {
          repoUrl: {v: "https://github.com/TinydoorStudios/live-sound-kb.git"},
          branch: {v: "main"},
          basicPassword: {v: "ghp_YOUR_ACTUAL_PAT_HERE"},
          basicUser: {v: "TinydoorStudios"},
          localRepoPath: {v: "./data/repo"},
          syncDirection: {v: "pull"},
          syncInterval: {v: "PT5M"}
        }
      },
      {
        key: "local",
        isEnabled: true,
        config: {
          storagePath: {v: "/data/assets"}
        }
      }
    ])
  }
}
MUTATION

echo ""
echo "Easier: Use this curl command (replace YOUR_PAT):"
echo ""
echo 'curl -X POST http://192.168.0.126:3000/graphql \
  -H "Content-Type: application/json" \
  -d '"'"'{"query":"mutation { storage { updateTargets(targets: [{key:\"git\",isEnabled:true,config:{repoUrl:{v:\"https://github.com/TinydoorStudios/live-sound-kb.git\"},branch:{v:\"main\"},basicPassword:{v:\"ghp_YOUR_PAT\"},basicUser:{v:\"TinydoorStudios\"},localRepoPath:{v:\"./data/repo\"},syncDirection:{v:\"pull\"},syncInterval:{v:\"PT5M\"}}},{key:\"local\",isEnabled:true,config:{storagePath:{v:\"/data/assets\"}}}]) } }"}'"'"
echo ""
echo "After that, .ses files in ~/Documents/Claude/audio/Live Sound KB/Wiki/assets/"
echo "will auto-sync to the wiki and be downloadable."
echo ""
