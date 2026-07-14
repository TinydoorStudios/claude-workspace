#!/bin/bash
# Find the actual wiki container IP

TAILSCALE_IP="100.99.198.22"
SSH_KEY="$HOME/.ssh/proxmox_tds"

echo "Finding wiki container IP..."
echo ""

# Get all IPs for the wiki container
ssh -i $SSH_KEY root@$TAILSCALE_IP "pct exec 101 -- ip addr show" 2>/dev/null | grep -E "inet " | grep -v "127.0.0.1"

echo ""
echo "Or check via docker:"
ssh -i $SSH_KEY root@$TAILSCALE_IP "pct exec 101 -- docker inspect wikijs-wiki-1 | grep -A 5 'Networks'" 2>/dev/null | grep IPAddress

echo ""
echo "Test connectivity to each IP you see above"
