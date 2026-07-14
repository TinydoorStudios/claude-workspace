#!/bin/bash
mkdir -p ~/.claude
mv ~/Documents/Claude/kb-secrets.sh ~/.claude/kb-secrets.sh
chmod 600 ~/.claude/kb-secrets.sh
echo "Done — kb-secrets.sh is in place."
