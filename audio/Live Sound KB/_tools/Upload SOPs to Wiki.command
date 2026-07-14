#!/usr/bin/env bash
set -uo pipefail
SSH_OPTS="-o StrictHostKeyChecking=no -i $HOME/.ssh/proxmox_tds"
P="ssh $SSH_OPTS tds"
SOPS="$HOME/Documents/Claude/audio/Live Sound KB/Wiki/assets/sops"

echo "============ Step 1: rsync sops → Proxmox host /tmp/kb-sops/ ============"
rsync -av --delete --exclude '.DS_Store' \
    -e "ssh $SSH_OPTS" \
    "$SOPS/" \
    tds:/tmp/kb-sops/ \
    && echo "✓ rsync done" || { echo "✗ rsync FAILED"; exit 1; }

echo; echo "============ Step 2: create dirs in CT 101 ============"
$P "pct exec 101 -- mkdir -p \
    /opt/wikijs/data/assets/sops/fsq \
    /opt/wikijs/data/assets/sops/memo \
    /opt/wikijs/data/assets/sops/esp \
    /opt/wikijs/data/assets/sops/wp" \
    && echo "✓ dirs created"

echo; echo "============ Step 3: tar-pipe files into CT 101 ============"
# Exclude the stray root-level duplicate (fsq-m32-failover-sop.pdf at sops/ root)
$P "tar -cC /tmp/kb-sops --exclude '.DS_Store' --exclude './fsq-m32-failover-sop.pdf' . 2>/dev/null \
    | pct exec 101 -- tar -xvC /opt/wikijs/data/assets/sops" \
    && echo "✓ files pushed into CT 101"

echo; echo "============ Step 4: set permissions ============"
$P "pct exec 101 -- chmod -R a+rX /opt/wikijs/data/assets/sops" \
    && echo "✓ permissions set"

echo; echo "============ Step 5: verify file count in CT 101 ============"
$P "pct exec 101 -- find /opt/wikijs/data/assets/sops -type f | sort"

echo; echo "============ done ============"
echo "Press any key to close…"; read -n 1 -s
