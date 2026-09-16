#!/usr/bin/env python3
"""Import the Advance List spreadsheet into events + acts.

Groups rows by Event Name + Date + Venue into events and upserts each artist
onto the bill with its own schedule. Nothing assigns a position: Artist 1/2/3
is derived from set start at read time (advance_db.order_acts). Idempotent —
re-run after editing the sheet and it updates in place. Emailing is separate
(draft_emails.py).

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
    """Two artists on one bill with the SAME set start — record each once
    (doc_notices kind 'set_time_clash') and put it in Brian's digest.

    2026-09-15: this used to be a slot clash, and the second band was DROPPED
    from the advance doc to protect the slot. Nothing is dropped now — both
    artists stay on the bill and the tie breaks on entry order — but identical
    start times still mean somebody typed one wrong, and which of them is
    Artist 1 is a coin flip until it's fixed."""
    new = []
    with db.get_conn() as conn, conn.cursor() as cur:
        for venue, edate, ename, set_start, first, second in clashes:
            nid = db.insert_doc_notice(cur, venue, to_date(edate), (ename or "").lower(),
                                       "set_time_clash", set_start, second, first, detail=ename)
            if nid:
                new.append((nid, venue, edate, ename, set_start, first, second))
        conn.commit()
    if not new:
        return
    try:
        import mailer
    except ImportError:
        return
    rows = "".join(f"<li>{mailer.esc(v)} {mailer.esc(d)} — {mailer.esc(e or '')}: <b>{mailer.esc(f1)}</b> and "
                   f"<b>{mailer.esc(s2)}</b> both start at <i>{mailer.esc(ss or 'no time')}</i>. "
                   f"Both are in the advance doc, in the order they were entered.</li>"
                   for _n, v, d, e, ss, f1, s2 in new)
    # review 2026-09-14 (E1): rides the digest, not its own email
    with db.get_conn() as conn, conn.cursor() as cur:
        db.queue_digest_item(cur, "set_time_clash", f"Same set start on one bill — {len(new)} to fix",
                             f"<p>Fix the Start column in advance-list.xlsx — it decides who is "
                             f"Artist 1:</p><ul>{rows}</ul>")
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

    # group by (event_name, event_date, venue). Brian, 2026-09-14: every
    # internal booking at a venue on a date is ONE bill (event name blank or
    # not); a '3rd Party' booking is its own event on that date, named after
    # its event (or its band), so it gets its own advance doc.
    groups = {}
    for r in rows:
        if db.is_third_party(r.get("series")):
            ename = r.get("event_name") or f"3rd Party - {r.get('artist_name')}"
        else:
            ename = ""
        key = (ename, r.get("event_date") or "", r.get("venue") or "")
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
            if not ename:
                # the internal bill keeps whatever event name staff typed (first non-empty)
                ename = next((a.get("event_name") for a in acts if a.get("event_name")), None)
            with conn.cursor() as cur:
                eid = get_or_create_event(cur, ename or None, evenue or None,
                                          to_date(edate), series)
                db.update_event_details(cur, eid, details)
                events_made += 1
                # Position on the bill is derived from the act's own Start, so
                # nothing here assigns anything — each artist just goes on with
                # its own schedule and the read path orders them. Same start
                # time twice is still a typo worth telling Brian about.
                by_start = {}
                for a in acts:
                    if not (a.get("artist_name") or "").strip():
                        continue
                    start = (a.get("event_start") or "").strip()
                    if start:
                        prior = by_start.get(db.parse_clock(start))
                        if prior and db.normalize(prior) != db.normalize(a["artist_name"]):
                            print(f"  ! same set start: {a['artist_name']} and {prior} both start "
                                  f"{start} on {ename or '(unnamed)'} {edate} — both kept")
                            clashes.append((evenue, edate, ename, start, prior, a["artist_name"]))
                        else:
                            by_start[db.parse_clock(start)] = a["artist_name"]
                    artist_id = db.upsert_artist(cur, a["artist_name"],
                                                 email=a.get("contact_email"))
                    # band-detail overrides typed into the sheet (non-empty only)
                    sheet_fields = {k: a[k] for k in fs.BAND_KEYS
                                    if a.get(k) not in (None, "")}
                    db.add_act(cur, eid, artist_id, set_time=a.get("set_time"),
                               set_start=a.get("event_start"), set_end=a.get("event_end"),
                               load_in=a.get("load_in"), soundcheck=a.get("soundcheck"),
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
