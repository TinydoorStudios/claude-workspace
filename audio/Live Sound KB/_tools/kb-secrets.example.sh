# kb-secrets.example.sh — copy to ~/.claude/kb-secrets.sh and fill in.
# This file is sourced by kb-publish.sh. Keep it OUT of the git repo.
# chmod 600 ~/.claude/kb-secrets.sh

# --- paths / hosts (defaults already match your handoff; override only if they change) ---
# export KB_WIKI="$HOME/Documents/Claude/audio/Live Sound KB/Wiki"
# export KB_SSH_JUMP="tds"
# export KB_SSH_KEY="$HOME/.ssh/proxmox_tds"
# export KB_N8N_USER="brian"
# export KB_N8N_HOST="192.168.200.84"
# export KB_ASSETS_DIR="/opt/kb-assets"
# export KB_WIKI_CT="101"
# export KB_WIKI_LAN="192.168.200.126:3000"
# export KB_PUBLIC_URL="https://kb.tinydoorstudios.com"

# --- credentials (required for verify + nav steps) ---
# nginx HTTP Basic Auth, used only to verify a download returns 200:
export KB_BASIC_AUTH="tds:CHANGE_ME"

# Wiki.js API token — ONLY needed to auto-rebuild the left-nav sidebar.
# Create one: Wiki.js → Administration → API Access → enable + generate key (full or navigation scope).
# Leave blank to skip the sidebar step (the home page still works as nav).
export KB_WIKI_API_KEY=""

# NOTE: the GitHub PAT lives in the repo's git remote URL, not here.
# It is flagged COMPROMISED in the handoff — rotate it and update the remote:
#   git -C "$KB_WIKI" remote set-url origin https://USER:NEW_TOKEN@github.com/TinydoorStudios/live-sound-kb.git
