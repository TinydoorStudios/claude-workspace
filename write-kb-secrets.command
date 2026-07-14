#!/bin/bash
mkdir -p ~/.claude
cat > ~/.claude/kb-secrets.sh << 'EOF'
# kb-secrets.sh — Live Sound KB publish credentials
# Sourced by kb-publish.sh. Keep out of git.

# Wiki.js API token — key name: kb-publish, expires June 14 2027
export KB_WIKI_API_KEY="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGkiOjIsImdycCI6MSwiaWF0IjoxNzgxNDAxNzQ2LCJleHAiOjE4MTI5NTkzNDYsImF1ZCI6InVybjp3aWtpLmpzIiwiaXNzIjoidXJuOndpa2kuanMifQ.Gk3E1k97aglSNUYT0JnhbamTjA3aUnZPD4bEwuZEFucAC7Y9M_nWWEOzXOU6NxbpU6HeLozTqR1tO9RQU8bDxFkW4ZAhHttGgNVAP2HU9VkSkFAcmJBmhoXjloUQZCqeoSEkawa930Lkso0vKL88umHKzRccp2VDaS41QGJ4XIoySJpk7o7fSJcg2BugjL8qBCk5gSoKP3r_xVtZTqkubYkefAPjOi8gOGH_b_vLf_Ts7Tvyvw1GOmssndOgnKKXcqt04XBbtU7GtUntBgc5YknL9Xd8dgrtC3s524GrRNCacCjJ-i0kvwvhqOKEdjNZKs5-U39I0T-gLfOCQk88bg"
EOF
chmod 600 ~/.claude/kb-secrets.sh
echo "Done — $(cat ~/.claude/kb-secrets.sh | grep KB_WIKI | cut -c1-40)..."
