#!/bin/bash
# Enable local asset storage in Wiki.js

echo "Querying current Wiki.js storage configuration..."
echo ""

# Query current storage config
RESPONSE=$(curl -s -X POST http://192.168.0.126:3000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ storage { targets { key isEnabled config } } }"}')

echo "Current storage targets:"
echo "$RESPONSE" | grep -o '"key":"[^"]*"' || echo "(Could not retrieve - may need authentication)"

echo ""
echo "To complete setup, visit this URL and paste the mutation:"
echo ""
echo "🔗 http://192.168.0.126:3000/graphql"
echo ""
echo "Query to run (PASTE THIS in the left panel):"
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
          basicPassword: {v: "YOUR_GITHUB_PAT"},
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
echo "Steps:"
echo "1. Go to http://192.168.0.126:3000/graphql"
echo "2. Paste the mutation above into the left panel"
echo "3. Replace YOUR_GITHUB_PAT with your actual GitHub token"
echo "4. Click the Play button (▶)"
echo ""
echo "✓ After that, your .ses files will be downloadable from the wiki!"
echo ""
