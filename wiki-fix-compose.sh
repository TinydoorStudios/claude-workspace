#!/bin/bash
# Fix docker-compose.yml and restart wiki

TAILSCALE_IP="100.99.198.22"
SSH_KEY="$HOME/.ssh/proxmox_tds"

echo "Restoring docker-compose from backup..."
ssh -i $SSH_KEY root@$TAILSCALE_IP "pct exec 101 -- bash -c 'cd /opt/wikijs && mv docker-compose.yml.bak docker-compose.yml'"

echo "Fetching current docker-compose..."
ssh -i $SSH_KEY root@$TAILSCALE_IP "pct exec 101 -- cat /opt/wikijs/docker-compose.yml" > /tmp/docker-compose.yml

# Add assets volume using Python for reliable YAML manipulation
python3 << 'PYTHON_EOF'
import yaml

with open('/tmp/docker-compose.yml', 'r') as f:
    compose = yaml.safe_load(f)

# Ensure wiki service has volumes
if 'services' in compose and 'wiki' in compose['services']:
    if 'volumes' not in compose['services']['wiki']:
        compose['services']['wiki']['volumes'] = []

    # Add assets volume if not already present
    assets_vol = './data/assets:/data/assets'
    if assets_vol not in compose['services']['wiki']['volumes']:
        compose['services']['wiki']['volumes'].append(assets_vol)
        print("✓ Added assets volume to wiki service")
    else:
        print("✓ Assets volume already present")

# Write back
with open('/tmp/docker-compose.yml', 'w') as f:
    yaml.dump(compose, f, default_flow_style=False, sort_keys=False)
    print("✓ Updated docker-compose.yml")
PYTHON_EOF

echo "Uploading updated docker-compose..."
ssh -i $SSH_KEY root@$TAILSCALE_IP "pct exec 101 -- bash -c 'cat > /opt/wikijs/docker-compose.yml'" < /tmp/docker-compose.yml

echo "Restarting wiki container..."
ssh -i $SSH_KEY root@$TAILSCALE_IP "pct exec 101 -- bash -c 'cd /opt/wikijs && docker compose restart wiki'"

echo ""
echo "✓ docker-compose fixed and wiki restarted"
echo ""
echo "Now run the GraphQL mutation to configure Wiki.js storage."
echo "Go to: http://192.168.0.126:3000/graphql"
echo ""
echo "Paste this (replace ghp_YOUR_PAT with your actual GitHub PAT):"
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
          basicPassword: {v: "ghp_YOUR_PAT"},
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
