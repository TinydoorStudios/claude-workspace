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
import os
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

PUBLIC_URL = os.environ.get("ADVANCE_PUBLIC_URL", "https://advance.tinydoorstudios.com")


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
    # review 2026-09-14 (E1): rides the digest, not its own email
    with db.get_conn() as conn, conn.cursor() as cur:
        # 2026-09-21 sweep (FLOW-12): a booked act's Start is fixed on its Edit page —
        # a sheet-only fix never reaches the bookings row (band emails) and is
        # reverted by the next app edit. No link = a hand-typed sheet row.
        def _edit_link(v, d, name):
            if not db.find_booking(cur, v, to_date(d), name):
                return ""
            show = db.show_for_booking(cur, name, v, to_date(d))
            return f' (<a href="{PUBLIC_URL}/show/{show["id"]}/edit">edit</a>)' if show else ""

        rows = "".join(f"<li>{mailer.esc(v)} {mailer.esc(d)} — {mailer.esc(e or '')}: <b>{mailer.esc(f1)}</b>"
                       f"{_edit_link(v, d, f1)} and "
                       f"<b>{mailer.esc(s2)}</b>{_edit_link(v, d, s2)} both start at "
                       f"<i>{mailer.esc(ss or 'no time')}</i>. "
                       f"Both are in the advance doc, in the order they were entered.</li>"
                       for _n, v, d, e, ss, f1, s2 in new)
        db.queue_digest_item(cur, "set_time_clash", f"Same set start on one bill — {len(new)} to fix",
                             f"<p>Change one of the two start times. It decides who is Artist 1. "
                             f"For an act with an edit link, change it there so the sheet, the doc "
                             f"and the band's emails all agree. An act with no link is a hand-typed "
                             f"sheet row: fix its Start column in advance-list.xlsx.</p><ul>{rows}</ul>")
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
    today = dt.date.today()
    with db.get_conn() as conn:
        # root cause A (audit 2026-09-16): a show purged or merged away in the
        # app whose sheet row hasn't been deleted yet must not come back as an
        # act (and from there a filed doc).
        with conn.cursor() as cur:
            removed = db.pending_removal_idents(cur)
        # audit 2026-09-16 #18: the truncate used to run in package_run.py
        # BEFORE this script was even invoked, so an unreadable/mid-sync
        # sheet (the empty-rows exit above) left events/event_acts wiped
        # until the next good run. It lives here now, and (2026-09-21 sweep,
        # PRIOR-10) the truncate plus the WHOLE rebuild is one transaction with
        # a single commit after the last group: a bad row anywhere rolls back to
        # the previous model instead of leaving it half-built. The truncate's
        # ACCESS EXCLUSIVE lock is held for the import's few seconds — readers
        # wait rather than see a partial model. 2026-09-21 sweep (PIPE-6): so nothing
        # in the loop may open a second connection touching events/event_acts (it'd hang).
        with conn.cursor() as cur:
            cur.execute("TRUNCATE events, event_acts RESTART IDENTITY CASCADE;")
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
                # audit 2026-09-16 #23 / Brian 2026-09-17: a cancelled act's
                # sheet row can still be sitting there (cancelling a show only
                # sets shows.cancelled_at — nothing removes its sheet row or
                # booking). It keeps its own column, marked CANCELLED (M4) —
                # UNLESS a real booking has since taken its exact set start,
                # in which case that new band's act replaces it outright
                # rather than crowding in as an extra column. Two passes: the
                # first just learns which acts are cancelled and which start
                # times a REAL act now owns, so the second pass (which
                # actually adds acts) can tell a cancelled act apart from one
                # that's been taken over.
                cancelled_flags, real_starts = {}, set()
                for a in acts:
                    name = (a.get("artist_name") or "").strip()
                    if not name or db.removal_ident(name, evenue, edate) in removed:
                        continue
                    show = db.show_for_booking(cur, name, evenue, to_date(edate))
                    cancelled = bool(show and show.get("cancelled_at"))
                    cancelled_flags[id(a)] = cancelled
                    if not cancelled:
                        st = db.parse_clock(str(a.get("event_start") or "").strip())
                        if st is not None:
                            real_starts.add(st)
                for a in acts:
                    name = (a.get("artist_name") or "").strip()
                    if not name:
                        continue
                    if db.removal_ident(name, evenue, edate) in removed:
                        print(f"  skip {name} {edate}: removed in the app, sheet row pending deletion")
                        continue
                    cancelled = cancelled_flags.get(id(a), False)
                    start_min = db.parse_clock(str(a.get("event_start") or "").strip())
                    if cancelled and start_min is not None and start_min in real_starts:
                        print(f"  skip {name} {edate}: cancelled, a new booking took its {a.get('event_start')} slot")
                        continue
                    start = str(a.get("event_start") or "").strip()
                    if start and not cancelled:
                        prior = by_start.get(db.parse_clock(start))
                        if prior and db.normalize(prior) != db.normalize(name):
                            print(f"  ! same set start: {name} and {prior} both start "
                                  f"{start} on {ename or '(unnamed)'} {edate} — both kept")
                            clashes.append((evenue, edate, ename, start, prior, name))
                        else:
                            by_start[db.parse_clock(start)] = name
                    if to_date(edate) and to_date(edate) < today:
                        # a past row never mints an artist — only an act for a
                        # band already on file (the recap/status paths read those)
                        # 2026-09-21 sweep (DBA-3): key computed in SQL, same as the column
                        cur.execute(f"SELECT id FROM artists WHERE match_key = {db._SQL_MATCH_KEY}",
                                    (a["artist_name"],))
                        hit = cur.fetchone()
                        if not hit:
                            continue
                        artist_id = hit["id"]
                    else:
                        artist_id = db.upsert_artist(cur, a["artist_name"],
                                                     email=a.get("contact_email"))
                    # band-detail overrides typed into the sheet (non-empty only)
                    sheet_fields = {k: a[k] for k in fs.BAND_KEYS
                                    if a.get(k) not in (None, "")}
                    # 2026-09-21 sweep (PRIOR-8): a Contact Name equal to the booking's was
                    # seeded by append_bookings (before today), not typed by Brian — no override.
                    if sheet_fields.get("contact_name"):
                        bk = db.find_booking(cur, evenue, to_date(edate), name)
                        if bk and db.normalize(bk.get("contact_name") or "") == \
                                db.normalize(str(sheet_fields["contact_name"])):
                            sheet_fields.pop("contact_name")
                    db.add_act(cur, eid, artist_id, set_time=a.get("set_time"),
                               set_start=a.get("event_start"), set_end=a.get("event_end"),
                               load_in=a.get("load_in"), soundcheck=a.get("soundcheck"),
                               sheet_fields=sheet_fields)
                    acts_made += 1
            print(f"  event: {ename or '(unnamed)'} @ {evenue or '?'} {edate or '?'} "
                  f"— {len(acts)} act(s)")
        conn.commit()

    if clashes:
        _report_clashes(clashes)
    print(f"\nImported {events_made} event(s), {acts_made} act(s). "
          f"Generate a day-sheet with:  python3 daysheet.py --event <id>")
    print("List events:  python3 event.py list")


if __name__ == "__main__":
    main()
