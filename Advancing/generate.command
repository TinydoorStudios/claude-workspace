#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
#  ADVANCING — build the advance pipeline from advance-list.xlsx
# ═══════════════════════════════════════════════════════════════════════════
#  Edit advance-list.xlsx, then double-click this. It:
#    • uploads the sheet to the advance server
#    • rebuilds events + fills the advance doc per bill (form answers merged in)
#    • drafts an advance email per band  (NOTHING is sent)
#    • files each show into the venue tree:  <Venue>/<Year>/<MM Month>/
#    • refreshes the Status tab inside advance-list.xlsx
#
#  It FILES, it doesn't mirror — the tree accumulates as your archive. Re-running
#  a show updates its files in place; other shows/months are never touched.
#  Form submissions are never touched either.
#
#  ADVANCE_ROOT: where the tree + sheet live. Defaults to this folder; set it to
#  a Dropbox path when you're ready to share (export ADVANCE_ROOT=/path/to/Dropbox/Advancing).
# ═══════════════════════════════════════════════════════════════════════════
set -o pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="${ADVANCE_ROOT:-$HERE}"
VM="brian@192.168.200.84"
KEY="$HOME/.ssh/proxmox_tds"
TOOLS="$HERE/../Code/BandInfoForm/tools"      # bundled into ROOT/_bin when this moves to Dropbox
SSH=(ssh -J tds -i "$KEY")
SHEET="$ROOT/advance-list.xlsx"

[ -f "$SHEET" ] || { echo "Missing $SHEET"; exit 1; }

echo "Pulling any new staff bookings into the sheet ..."
BK="$ROOT/.bookings.tmp.json"
if "${SSH[@]}" "$VM" 'set -a; . /opt/band-advance/advance.env; set +a; cd /opt/band-advance/tools; ../venv/bin/python seed_bookings.py --json' > "$BK" 2>/dev/null; then
  IDS=$(python3 "$TOOLS/append_bookings.py" --list "$SHEET" --data "$BK" 2>/dev/null)
  if [ -n "$IDS" ]; then
    "${SSH[@]}" "$VM" "set -a; . /opt/band-advance/advance.env; set +a; cd /opt/band-advance/tools; ../venv/bin/python seed_bookings.py --seed '$IDS'" 2>/dev/null
    echo "  seeded $(echo "$IDS" | tr ',' '\n' | grep -c .) booking(s) from the intake form"
  fi
fi
rm -f "$BK"

echo "Uploading advance-list.xlsx ..."
scp -J tds -i "$KEY" "$SHEET" "$VM:/opt/band-advance/tools/lists/_current.xlsx" \
  || { echo "upload failed — is the VM reachable?"; exit 1; }

echo "Building the package on the server ..."
"${SSH[@]}" "$VM" '
  set -a; . /opt/band-advance/advance.env; set +a
  cd /opt/band-advance/tools
  ../venv/bin/python package_run.py lists/_current.xlsx --out _package
' || { echo "build failed"; exit 1; }

echo "Filing results into the venue tree ..."
# OVERLAY the built venue tree into ROOT (NO --delete: this is an archive, not a mirror).
# status.json rides along but is consumed separately below, then removed.
rsync -az -e "ssh -J tds -i $KEY" --exclude="status.json" \
  "$VM:/opt/band-advance/tools/_package/" "$ROOT/" \
  || { echo "rsync failed"; exit 1; }

# fold status + the band's form answers into advance-list.xlsx (one tab):
# blanks get filled (tinted) and a color-coded STATUS block is appended. Your
# own typed cells are never overwritten.
TMP="$ROOT/.status.tmp.json"
if scp -J tds -i "$KEY" "$VM:/opt/band-advance/tools/_package/status.json" \
     "$TMP" 2>/dev/null; then
  python3 "$TOOLS/merge_status.py" --list "$SHEET" --data "$TMP" && rm -f "$TMP"
else
  echo "  (no status data built)"
fi

echo
echo "Done."
echo "  advance-list.xlsx  — your rows, band answers filled in (tinted) + STATUS block"
echo "  <Venue>/<Year>/<Month>/  — filed advance docs + Email Drafts"
echo
find "$ROOT" -name "*advance.docx" -newermt "-2 min" 2>/dev/null \
  | sed "s|$ROOT/|  • |" | sort
