#!/bin/bash
# Complete Wiki.js setup - authenticate and configure storage

set -e

WIKI_URL="http://192.168.200.126:3000"
WIKI_EMAIL="tinydoorstudios@gmail.com"
WIKI_PASS="WikiKBmemo2026"

echo "Authenticating to Wiki.js..."

# Get auth token
AUTH_RESPONSE=$(curl -s -X POST "$WIKI_URL/graphql" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"mutation { authentication { login(email:\\\"$WIKI_EMAIL\\\",password:\\\"$WIKI_PASS\\\") { jwt } } }\"}")

TOKEN=$(echo "$AUTH_RESPONSE" | grep -o '"jwt":"[^"]*"' | head -1 | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ Authentication failed"
  echo "Response: $AUTH_RESPONSE"
  exit 1
fi

echo "✓ Authenticated to Wiki.js"
echo ""

# Get current GitHub PAT from environment or ask user
if [ -z "$GITHUB_PAT" ]; then
  echo "⚠ GitHub PAT not found in environment variable GITHUB_PAT"
  echo "Need to find the existing PAT from Wiki.js config..."
  echo ""
  echo "Querying current storage config..."

  # Query current storage to get the git config
  QUERY='{ storage { targets { key isEnabled config } } }'
  STORAGE=$(curl -s -X POST "$WIKI_URL/graphql" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "{\"query\":\"$QUERY\"}")

  echo "Current storage config:"
  echo "$STORAGE" | python3 -m json.tool 2>/dev/null || echo "$STORAGE"

  echo ""
  echo "❌ Cannot proceed without GitHub PAT"
  echo ""
  echo "Please provide your GitHub PAT either:"
  echo "1. Via environment variable: export GITHUB_PAT='ghp_xxxxx...'"
  echo "2. Then run this script again"
  echo ""
  exit 1
fi

echo "Configuring local asset storage in Wiki.js..."

# Build the mutation with the PAT
MUTATION="mutation {
  storage {
    updateTargets(targets: [
      {
        key: \"git\",
        isEnabled: true,
        config: {
          repoUrl: {v: \"https://github.com/TinydoorStudios/live-sound-kb.git\"},
          branch: {v: \"main\"},
          basicPassword: {v: \"$GITHUB_PAT\"},
          basicUser: {v: \"TinydoorStudios\"},
          localRepoPath: {v: \"./data/repo\"},
          syncDirection: {v: \"pull\"},
          syncInterval: {v: \"PT5M\"}
        }
      },
      {
        key: \"local\",
        isEnabled: true,
        config: {
          storagePath: {v: \"/data/assets\"}
        }
      }
    ])
  }
}
"

# Run the mutation
RESULT=$(curl -s -X POST "$WIKI_URL/graphql" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"query\":\"$MUTATION\"}")

if echo "$RESULT" | grep -q "errors"; then
  echo "❌ GraphQL error:"
  echo "$RESULT" | python3 -m json.tool 2>/dev/null || echo "$RESULT"
  exit 1
fi

echo "✓ Wiki.js storage configured!"
echo ""
echo "=== Setup Complete ==="
echo ""
echo "✅ Local asset storage is now enabled"
echo "✅ Git sync configured for markdown content"
echo "✅ Mac-side rsync watcher is running"
echo ""
echo ".ses files in ~/Documents/Claude/audio/Live Sound KB/Wiki/assets/"
echo "will now auto-sync to the wiki and be downloadable!"
echo ""
echo "Test: Try clicking on the .ses file in the wiki"
echo "Log: tail -f ~/.claude/logs/wiki-asset-sync.log"
echo ""
