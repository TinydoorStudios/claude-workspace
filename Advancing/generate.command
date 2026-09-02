#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
#  ADVANCING — build the whole advance pipeline from advance-list.xlsx
# ═══════════════════════════════════════════════════════════════════════════
#  Edit advance-list.xlsx, then double-click this. It:
#    • uploads the sheet to the advance server
#    • rebuilds events + fills a day-sheet per bill (form answers merged in)
#    • drafts an advance email per band  (NOTHING is sent)
#    • refreshes advance-status.xlsx
#    • mirrors it all back here under  Events/<date — event (venue)>/
#
#  Your form submissions are never touched. Re-run any time — it mirrors the
#  current sheet, replacing the last run's Events/ folders.
# ═══════════════════════════════════════════════════════════════════════════
set -o pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
VM="brian@192.168.200.84"
KEY="$HOME/.ssh/proxmox_tds"
SSH=(ssh -J tds -i "$KEY")
SHEET="$HERE/advance-list.xlsx"

[ -f "$SHEET" ] || { echo "Missing $SHEET"; exit 1; }

echo "Uploading advance-list.xlsx ..."
scp -J tds -i "$KEY" "$SHEET" "$VM:/opt/band-advance/tools/lists/_current.xlsx" \
  || { echo "upload failed — is the VM reachable?"; exit 1; }

echo "Building the package on the server ..."
"${SSH[@]}" "$VM" '
  set -a; . /opt/band-advance/advance.env; set +a
  cd /opt/band-advance/tools
  ../venv/bin/python package_run.py lists/_current.xlsx --out _package
' || { echo "build failed"; exit 1; }

echo "Pulling results into Advancing/ ..."
mkdir -p "$HERE/Events"
# mirror the server's Events/ tree exactly (drops folders no longer in the sheet)
rsync -az --delete -e "ssh -J tds -i $KEY" \
  "$VM:/opt/band-advance/tools/_package/Events/" "$HERE/Events/" \
  || { echo "rsync of Events/ failed"; exit 1; }

# fold the status read-back into advance-list.xlsx as its "Status" tab
# (input tab untouched — only the Status tab is rewritten, locally)
TMP="$HERE/.advance-status.tmp.xlsx"
if scp -J tds -i "$KEY" "$VM:/opt/band-advance/tools/_package/advance-status.xlsx" \
     "$TMP" 2>/dev/null; then
  python3 "$HERE/../Code/BandInfoForm/tools/merge_status.py" \
    --list "$SHEET" --status "$TMP" && rm -f "$TMP"
else
  echo "  (no status sheet built)"
fi

echo
echo "Done."
echo "  advance-list.xlsx  — your input tab + a refreshed 'Status' tab"
echo "  Events/            — a folder per bill: Day Sheet + advance emails"
echo
ls -1 "$HERE/Events/" 2>/dev/null | sed 's/^/  • /'
