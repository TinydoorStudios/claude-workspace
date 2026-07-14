#!/usr/bin/env bash
# Go through Proxmox host to exec into the wiki CT (id 101)
P="ssh -o StrictHostKeyChecking=no -i $HOME/.ssh/proxmox_tds tds"

echo "============ Proxmox CTs ============"
$P "pct list"

echo; echo "============ wiki data/uploads path ============"
$P "pct exec 101 -- find /wiki/data -type d 2>/dev/null | head -20"

echo; echo "============ upload route source ============"
$P "pct exec 101 -- grep -n 'mediaUpload\|req.files\|req.body' /wiki/server/routes.js 2>/dev/null | head -30"

echo; echo "============ find upload handler ============"
$P "pct exec 101 -- grep -rn 'app.post.*\/u\b\|router.post.*\/u\b' /wiki/server/ 2>/dev/null | head -10"

echo; echo "============ done ============"
echo "Press any key to close…"; read -n 1 -s
