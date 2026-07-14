#!/usr/bin/env bash
cd "$(dirname "$0")" || exit 1
[ -f "$HOME/.claude/kb-secrets.sh" ] && source "$HOME/.claude/kb-secrets.sh"
python3 wiki_assets.py --test
echo
echo "Press any key to close…"
read -n 1 -s
