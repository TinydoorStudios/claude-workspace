#!/bin/bash
# Process the advance spreadsheet end to end and drop the results in ./output/:
#   - imports the sheet into the database (events + acts)
#   - generates a filled day-sheet .docx for every event
#   - drafts the advance email .md for every band (nothing is sent)
# Then pulls it all back to your Mac under Code/BandInfoForm/output/.
#
# Usage:  double-click, or:  ./generate.command [path-to-xlsx]
set -o pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
VM="brian@192.168.200.84"
KEY="$HOME/.ssh/proxmox_tds"
SHEET="${1:-$HERE/tools/lists/advance_list_template.xlsx}"
OUT="$HERE/output"
mkdir -p "$OUT/day-sheets" "$OUT/emails"

echo "Processing: $SHEET"
scp -J tds -i "$KEY" "$SHEET" "$VM:/opt/band-advance/tools/lists/_current.xlsx" || { echo "upload failed"; exit 1; }

ssh -J tds -i "$KEY" "$VM" '
  set -a; . /opt/band-advance/advance.env; set +a
  cd /opt/band-advance/tools
  rm -f filled/*.docx drafts/*.md 2>/dev/null
  # rebuild events from the sheet (the source of truth); form submissions are untouched
  sudo docker exec advance-db psql -U advance -d advance -c "TRUNCATE events, event_acts RESTART IDENTITY CASCADE;" >/dev/null 2>&1
  ../venv/bin/python import_sheet.py lists/_current.xlsx
  for id in $(sudo docker exec advance-db psql -U advance -d advance -tAc "SELECT id FROM events ORDER BY id"); do
    ../venv/bin/python daysheet.py --event "$id" >/dev/null && echo "  day-sheet: event $id"
  done
  ../venv/bin/python draft_emails.py lists/_current.xlsx | tail -n +1
  rm -f followups/*.md 2>/dev/null
  ../venv/bin/python dump_followups.py >/dev/null 2>&1
  ../venv/bin/python status_sheet.py >/dev/null 2>&1
'

echo "--- pulling results into output/ ---"
mkdir -p "$OUT/emails/followups"
# clear last run's files so output/ mirrors the current sheet
rm -f "$OUT/day-sheets/"*.docx "$OUT/emails/"*.md "$OUT/emails/followups/"*.md 2>/dev/null
scp -J tds -i "$KEY" "$VM:/opt/band-advance/tools/filled/*.docx"     "$OUT/day-sheets/"       2>/dev/null || echo "  (no day-sheets)"
scp -J tds -i "$KEY" "$VM:/opt/band-advance/tools/drafts/*.md"       "$OUT/emails/"           2>/dev/null || echo "  (no drafts)"
scp -J tds -i "$KEY" "$VM:/opt/band-advance/tools/followups/*.md"    "$OUT/emails/followups/" 2>/dev/null || true
scp -J tds -i "$KEY" "$VM:/opt/band-advance/tools/advance_status.xlsx" "$OUT/" 2>/dev/null || true
echo
echo "Done. Results in:"
echo "  $OUT/day-sheets/"
echo "  $OUT/emails/"
ls -1 "$OUT/day-sheets/" "$OUT/emails/" 2>/dev/null
