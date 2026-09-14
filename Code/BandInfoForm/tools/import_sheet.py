#!/usr/bin/env python3
"""Import the Advance List spreadsheet into events + acts.

Groups rows by Event Name + Date + Venue into events, upserts each band, and
assigns it to its slot (with set time). Idempotent — re-run after editing the
sheet and it updates in place. Emailing is separate (draft_emails.py).

  python3 import_sheet.py lists/advance_list_template.xlsx
"""
import argparse
import datetime as dt
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _cand in (HERE.parent, HERE.parent / "app"):
    if (_cand / "advance_db.py").exists():
        sys.path.insert(0, str(_cand))
        break
import advance_db as db
from sheet import read_advance_sheet
import fieldspec as fs

SLOTS = ("opener", "direct_support", "headliner")


def to_date(s):
    if not s:
        return None
    try:
        return dt.date.fromisoformat(str(s)[:10])
    except ValueError:
        return None


def get_or_create_event(cur, name, venue, event_date, series):
    cur.execute(
        """SELECT id FROM events
           WHERE COALESCE(name,'')=COALESCE(%s,'')
             AND COALESCE(venue,'')=COALESCE(%s,'')
             AND event_date IS NOT DISTINCT FROM %s""",
        (name, venue, event_date),
    )
    row = cur.fetchone()
    if row:
        return row["id"]
    return db.create_event(cur, name, venue, event_date, series=series)


def _report_clashes(clashes):
    """Record each clash once (doc_notices kind 'slot_clash') and email Brian
    the new ones."""
    new = []
    with db.get_conn() as conn, conn.cursor() as cur:
        for venue, edate, ename, slot, kept, skipped in clashes:
            nid = db.insert_doc_notice(cur, venue, to_date(edate), (ename or "").lower(), "slot_clash",
                                       slot, skipped, kept, detail=ename)
            if nid:
                new.append((nid, venue, edate, ename, slot, kept, skipped))
        conn.commit()
    if not new:
        return
    try:
        import mailer
    except ImportError:
        return
    rows = "".join(f"<li>{mailer.esc(v)} {mailer.esc(d)} — {mailer.esc(e or '')}: <b>{mailer.esc(sk)}</b> and "
                   f"<b>{mailer.esc(k)}</b> are both <i>{mailer.esc(sl.replace('_', ' '))}</i>. "
                   f"Only {mailer.esc(k)} is in the advance doc.</li>"
                   for _n, v, d, e, sl, k, sk in new)
    ok, _ = mailer.alert(f"Advance sheet slot clash — {len(new)} to fix",
                         f"<p>Fix the Slot column in advance-list.xlsx:</p><ul>{rows}</ul>")
    if ok:
        with db.get_conn() as conn, conn.cursor() as cur:
            db.mark_doc_notices_notified(cur, [n[0] for n in new])
            conn.commit()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sheet", help="advance list .xlsx")
    args = ap.parse_args()

    rows = read_advance_sheet(args.sheet)
    if not rows:
        print("No data rows found (only examples/blanks?).", file=sys.stderr)
        sys.exit(1)

    # group by (event_name, event_date, venue)
    groups = {}
    for r in rows:
        key = (r.get("event_name") or "", r.get("event_date") or "", r.get("venue") or "")
        groups.setdefault(key, []).append(r)

    events_made = acts_made = 0
    clashes = []
    with db.get_conn() as conn:
        for (ename, edate, evenue), acts in groups.items():
            series = next((a.get("series") for a in acts if a.get("series")), None)
            # event-level details: first non-empty value across the group's rows
            details = {}
            for k in fs.EVENT_DETAIL_KEYS:
                v = next((a.get(k) for a in acts if a.get(k) not in (None, "")), None)
                if v is not None:
                    details[k] = v
            with conn.cursor() as cur:
                eid = get_or_create_event(cur, ename or None, evenue or None,
                                          to_date(edate), series)
                db.update_event_details(cur, eid, details)
                events_made += 1
                taken = {}
                for a in acts:
                    slot = (a.get("slot") or "").strip().lower() or "headliner"
                    if slot not in SLOTS:
                        print(f"  ! bad slot '{slot}' for {a['artist_name']} — skipped")
                        continue
                    if slot in taken and db.normalize(taken[slot]) != db.normalize(a["artist_name"]):
                        # two bands in one slot — the second used to silently
                        # replace the first in the doc (audit #20). Keep the
                        # first, skip the second, tell Brian.
                        print(f"  ! slot clash: {a['artist_name']} and {taken[slot]} are both "
                              f"{slot} on {ename or '(unnamed)'} {edate} — kept {taken[slot]}")
                        clashes.append((evenue, edate, ename, slot, taken[slot], a["artist_name"]))
                        continue
                    taken[slot] = a["artist_name"]
                    artist_id = db.upsert_artist(cur, a["artist_name"],
                                                 email=a.get("contact_email"))
                    # band-detail overrides typed into the sheet (non-empty only)
                    sheet_fields = {k: a[k] for k in fs.BAND_KEYS
                                    if a.get(k) not in (None, "")}
                    db.add_act(cur, eid, slot, artist_id, set_time=a.get("set_time"),
                               sheet_fields=sheet_fields)
                    acts_made += 1
            conn.commit()
            print(f"  event: {ename or '(unnamed)'} @ {evenue or '?'} {edate or '?'} "
                  f"— {len(acts)} act(s)")

    if clashes:
        _report_clashes(clashes)
    print(f"\nImported {events_made} event(s), {acts_made} act(s). "
          f"Generate a day-sheet with:  python3 daysheet.py --event <id>")
    print("List events:  python3 event.py list")


if __name__ == "__main__":
    main()
