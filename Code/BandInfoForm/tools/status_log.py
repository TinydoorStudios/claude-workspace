#!/usr/bin/env python3
"""Show Status Log — a running, auto-regenerated view across every show in the
advance pipeline (both venues), for "what's the status of X at a glance."

Pulls live from advance-db (the advance_status view + a read-only join against
bookings for date-booked/location/who-booked-it) — same source, same join
pattern as the Show Status Log demo. NOT a mirror of advance-list.xlsx: that
sheet is the working/editing surface with band-detail overrides; this is a
lighter read-mostly status board.

Most columns are fully auto (overwritten fresh every run). A few have no data
source yet — Owner, Advance Deadline, Basic Advance Complete?, Info Complete?,
Feedback Survey Sent?, Notes — and are safe to hand-type into the Dropbox file
directly: a hidden Show ID column keys each row, so a re-run finds the same
show and PRESERVES whatever was typed into those manual columns rather than
blanking them. New shows just get blank manual cells; nothing is ever deleted
out from under a real show, only refreshed.

Called from run_now.py after every booking/submission (best-effort — a bug
here should never block the day-sheet/email pipeline). Can also run by hand:

    python3 status_log.py [--out PATH]
"""
import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _cand in (HERE.parent, HERE.parent / "app"):
    if (_cand / "advance_db.py").exists():
        sys.path.insert(0, str(_cand))
        break
import advance_db as db

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

NYQUIST_DEFAULT = Path.home() / "Dropbox" / "Nyquist"
DEFAULT_OUT = NYQUIST_DEFAULT / "Show Status Log.xlsx"

NAVY = "1A3A5C"
WHITE = "FFFFFF"
MANUAL_TINT = "FFF3CD"  # matches the amber TOUR/hand-filled convention elsewhere

# same state colors as merge_status.py's STATE_FILL, for one consistent palette
# across the whole pipeline
STATE_STYLE = {
    "queued":           ("Not Started",    "E5E7EB", "1F2937"),
    "awaiting":         ("Drafted",        "FEF3C7", "78350F"),
    "ready_to_send":    ("Ready to Send",  "C7D2FE", "1E3A5F"),
    "followup_due":     ("Follow-up Due",  "FFE4B5", "7C2D12"),
    "followup_drafted": ("Follow-up Sent", "DBEAFE", "1E3A5F"),
    "responded":        ("Completed",      "C6EFCE", "14532D"),
}

# (label, width, "live" | "manual")
COLS = [
    ("Event Name", 22, "live"), ("Band", 20, "live"), ("Venue", 14, "live"),
    ("Location", 11, "live"), ("Series", 16, "live"),
    ("Owner", 10, "manual"), ("Booked By", 12, "live"),
    ("Show Date", 11, "live"), ("Days Until Show", 9, "live"),
    ("Date Booked", 11, "live"), ("Advance Deadline", 12, "manual"),
    ("Advance Status", 14, "live"),
    ("Basic Advance Complete?", 11, "manual"), ("Info Complete?", 10, "manual"),
    ("Advance Drafted", 12, "live"), ("Ready to Send", 12, "live"),
    ("Follow-up Drafted", 12, "live"), ("Responded", 12, "live"),
    ("Contact Email", 22, "live"), ("Files", 6, "live"),
    ("Feedback Survey Sent?", 11, "manual"), ("Notes", 28, "manual"),
]
MANUAL_LABELS = {lbl for lbl, _w, kind in COLS if kind == "manual"}
ID_COL = len(COLS) + 1  # hidden Show ID, past every visible column


def fdate(v):
    """timestamptz -> 'YYYY-MM-DD'. Slice, don't parse — sidesteps +00 vs
    +00:00 / variable microsecond-digit fussiness; only the date is shown."""
    if v is None:
        return None
    s = str(v)
    return s[:10] if len(s) >= 10 else None


def fetch_rows(cur):
    cur.execute(
        """SELECT
             ast.show_id, ast.band, ast.venue, ast.show_series, ast.show_date,
             ast.state, ast.days_until_show,
             ast.advance_draft_created_at, ast.send_reminder_sent_at,
             ast.followup_draft_created_at, ast.responded_at, ast.contact_email,
             b.location, b.created_at AS date_booked, b.event_name, b.entered_by,
             (SELECT count(*) FROM files f WHERE f.artist_id = ast.artist_id) AS file_count
           FROM advance_status ast
           LEFT JOIN bookings b ON b.venue = ast.venue
                  AND b.event_date = ast.show_date
                  AND lower(btrim(regexp_replace(b.artist_name, '\\s+', ' ', 'g'))) =
                      lower(btrim(regexp_replace(ast.band, '\\s+', ' ', 'g')))
           ORDER BY ast.show_date ASC NULLS LAST, ast.band"""
    )
    return cur.fetchall()


def read_manual(path):
    """{show_id: {label: value}} preserved from the existing file, if any."""
    if not path.exists():
        return {}
    try:
        wb = load_workbook(path)
    except Exception as e:
        print(f"  ! couldn't open existing {path} to preserve manual cells: {e}", file=sys.stderr)
        return {}
    if "Show Status" not in wb.sheetnames:
        return {}
    ws = wb["Show Status"]
    label_col = {ws.cell(4, c).value: c for c in range(1, len(COLS) + 1)}
    out = {}
    for r in range(5, ws.max_row + 1):
        sid = ws.cell(r, ID_COL).value
        if sid is None:
            continue
        row = {}
        for label in MANUAL_LABELS:
            c = label_col.get(label)
            if c:
                v = ws.cell(r, c).value
                if v not in (None, ""):
                    row[label] = v
        if row:
            out[int(sid)] = row
    return out


def build(rows, manual_by_id):
    wb = Workbook()
    ws = wb.active
    ws.title = "Show Status"
    n = len(COLS)
    last_letter = get_column_letter(n)

    thin = Side(style="thin", color="D9DEE5")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    ws.merge_cells(f"A1:{last_letter}1")
    t = ws.cell(1, 1, "Band Advance — Show Status Log")
    t.font = Font(bold=True, color=WHITE, size=14)
    t.fill = PatternFill("solid", fgColor=NAVY)
    t.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[1].height = 26

    ws.merge_cells(f"A2:{last_letter}2")
    sub = ws.cell(2, 1,
        "Auto-generated from advance-db after every booking/submission. White columns "
        "refresh every run; amber columns (Owner, Advance Deadline, Basic Advance "
        "Complete?, Info Complete?, Feedback Survey Sent?, Notes) are yours to hand-type "
        "here — they're preserved across regenerations, not overwritten.")
    sub.font = Font(italic=True, color="6B7280", size=9)
    sub.alignment = Alignment(horizontal="left", vertical="center", indent=1, wrap_text=True)
    ws.row_dimensions[2].height = 28

    hrow = 4
    for i, (label, width, _kind) in enumerate(COLS, start=1):
        c = ws.cell(hrow, i, label)
        c.font = Font(bold=True, color=WHITE, size=10)
        c.fill = PatternFill("solid", fgColor=NAVY)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = border
        ws.column_dimensions[get_column_letter(i)].width = width
    ws.row_dimensions[hrow].height = 30
    ws.freeze_panes = f"F{hrow + 1}"

    id_letter = get_column_letter(ID_COL)
    ws.cell(hrow, ID_COL, "Show ID")
    ws.column_dimensions[id_letter].hidden = True

    r = hrow + 1
    for row in rows:
        label, fg, txt = STATE_STYLE.get(row["state"], (row["state"] or "—", "E5E7EB", "374151"))
        preserved = manual_by_id.get(row["show_id"], {})
        live = {
            "Event Name": row["event_name"] or "—",
            "Band": row["band"],
            "Venue": row["venue"],
            "Location": row["location"] or "—",
            "Series": row["show_series"] or "—",
            "Booked By": row["entered_by"] or "—",
            "Show Date": row["show_date"].isoformat() if row["show_date"] else "",
            "Days Until Show": row["days_until_show"] if row["days_until_show"] is not None else "",
            "Date Booked": fdate(row["date_booked"]) or "",
            "Advance Status": label,
            "Advance Drafted": fdate(row["advance_draft_created_at"]) or "",
            "Ready to Send": fdate(row["send_reminder_sent_at"]) or "",
            "Follow-up Drafted": fdate(row["followup_draft_created_at"]) or "",
            "Responded": fdate(row["responded_at"]) or "",
            "Contact Email": row["contact_email"] or "—",
            "Files": row["file_count"] or 0,
        }
        for i, (clabel, _w, kind) in enumerate(COLS, start=1):
            value = live.get(clabel, preserved.get(clabel, "")) if kind == "live" else preserved.get(clabel, "")
            cell = ws.cell(r, i, value)
            cell.border = border
            cell.alignment = Alignment(
                horizontal="center" if clabel not in ("Event Name", "Band", "Contact Email", "Notes") else "left",
                vertical="center")
            if clabel == "Advance Status":
                cell.fill = PatternFill("solid", fgColor=fg)
                cell.font = Font(bold=True, color=txt, size=10)
            elif kind == "manual":
                cell.fill = PatternFill("solid", fgColor=MANUAL_TINT)
            elif r % 2 == 0:
                cell.fill = PatternFill("solid", fgColor="F7FAFC")
        ws.cell(r, ID_COL, row["show_id"])
        r += 1
    last_row = max(r - 1, hrow + 1)

    tbl = Table(displayName="ShowStatus", ref=f"A{hrow}:{last_letter}{last_row}")
    tbl.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=False)
    ws.add_table(tbl)

    lg = wb.create_sheet("Legend")
    lg.column_dimensions["A"].width = 18
    lg.column_dimensions["B"].width = 74
    t2 = lg.cell(1, 1, "Advance Status — what each stage means")
    t2.font = Font(bold=True, size=13, color=NAVY)
    lg.merge_cells("A1:B1")
    meanings = {
        "Not Started": "Show is booked but no advance-ask email has been drafted yet.",
        "Drafted": "The advance-ask draft exists in Gmail but the show is still more than 21 days out.",
        "Ready to Send": "Inside the 21-day window — the draft is sitting in Gmail ready to send.",
        "Follow-up Due": "No response yet and the show is inside 7 days out — a reminder needs to go out.",
        "Follow-up Sent": "A follow-up draft exists (still drafts-only — you send it by hand).",
        "Completed": "The band responded — their submission is in.",
    }
    row_i = 3
    for label, desc in meanings.items():
        fg, txt = next((s[1], s[2]) for s in STATE_STYLE.values() if s[0] == label)
        c = lg.cell(row_i, 1, label)
        c.fill = PatternFill("solid", fgColor=fg)
        c.font = Font(bold=True, color=txt)
        c.alignment = Alignment(horizontal="center", vertical="center")
        d = lg.cell(row_i, 2, desc)
        d.alignment = Alignment(wrap_text=True, vertical="center")
        lg.row_dimensions[row_i].height = 32
        row_i += 1
    row_i += 1
    note = lg.cell(row_i, 1, "Manual columns:")
    note.font = Font(bold=True)
    lg.merge_cells(f"A{row_i + 1}:B{row_i + 2}")
    lg.cell(row_i + 1, 1,
        "Owner / Advance Deadline / Basic Advance Complete? / Info Complete? / Feedback "
        "Survey Sent? / Notes have no data source yet — type into them directly in this "
        "file. A hidden Show ID column keys each row so the next auto-regeneration finds "
        "your entry and keeps it, instead of overwriting it blank."
    ).alignment = Alignment(wrap_text=True, vertical="top")

    return wb, last_row - hrow


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)

    manual_by_id = read_manual(args.out)

    with db.get_conn() as conn, conn.cursor() as cur:
        rows = fetch_rows(cur)

    wb, n_shows = build(rows, manual_by_id)
    wb.save(args.out)
    print(f"Show Status Log: {n_shows} show(s) -> {args.out} "
          f"({len(manual_by_id)} row(s) had manual cells preserved)")


if __name__ == "__main__":
    main()
