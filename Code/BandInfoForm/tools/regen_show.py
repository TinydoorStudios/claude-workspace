#!/usr/bin/env python3
"""File ONE show's advance doc after a band submits — scoped, so a submission
never touches any other show (Brian, 2026-09-11).

Goes through docmerge.file_event_doc like every other filing path: the doc
is created if it doesn't exist yet, otherwise only its blank cells are
filled — a hand-edited cell is never overwritten, and a resubmitted value
that differs from the doc is emailed to Brian as a notice instead
(2026-09-13 audit #1). A resubmission's changes to filled cells wait for
his Keep doc / Use new call on /doc-review (2026-09-14).

  regen_show.py --venue "Washington Park" --date 2026-09-16 --artist "Anything Blues"
  regen_show.py ... --submission-id 812   # stamp submissions.doc_checked_at when done
"""
import argparse
import datetime as dt
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _c in (HERE.parent, HERE.parent / "app"):
    if (_c / "advance_db.py").exists():
        sys.path.insert(0, str(_c))
        break
sys.path.insert(0, str(HERE))
import advance_db as db
import docmerge
import fieldspec as fs

UPLOADS = HERE.parent / "data" / "uploads"


def find_event(cur, venue, date, artist):
    cur.execute(
        r"""SELECT DISTINCT e.id
            FROM events e
            JOIN event_acts ea ON ea.event_id = e.id
            JOIN artists a ON a.id = ea.artist_id
            WHERE e.venue = %s AND e.event_date = %s
              AND a.match_key = lower(btrim(regexp_replace(%s, '\s+', ' ', 'g')))
            ORDER BY e.id DESC LIMIT 1""",
        (venue, date, artist),
    )
    r = cur.fetchone()
    return r["id"] if r else None


def regen(venue, date, artist, send_mail=True, submission_id=None):
    # Review 2026-09-14: a submission landing while a package run is mid-way
    # (events/event_acts TRUNCATEd and being rebuilt) used to find "no event"
    # and skip the doc. Take the same lock the package run holds — wait for
    # it, then file against the rebuilt model.
    from run_now import acquire_lock
    lock = acquire_lock()
    res = None
    try:
        res = _regen(venue, date, artist, send_mail=send_mail)
        return res
    finally:
        if submission_id:
            _stamp(submission_id, res)
        try:
            import fcntl
            fcntl.flock(lock, fcntl.LOCK_UN)
            lock.close()
        except OSError:
            pass


def _stamp(submission_id, res):
    if res is None:
        text = "no doc for this show yet"
    else:
        text = {"created": "doc created", "merged": f"{res.get('filled')} cell(s) written",
                "unchanged": "no cells written", "locked": "doc is open in Word — not checked",
                "conflict": "doc was saved mid-check — not checked", "past": "show is past"
                }.get(res.get("action"), res.get("action") or "")
    try:
        with db.get_conn() as conn, conn.cursor() as cur:
            db.stamp_doc_check(cur, submission_id, text)
            conn.commit()
    except Exception as e:
        print(f"doc_check stamp failed: {e!r}", file=sys.stderr)


def _regen(venue, date, artist, send_mail=True):
    with db.get_conn() as conn, conn.cursor() as cur:
        eid = find_event(cur, venue, date, artist)
    if not eid:
        print(f"no event for {artist!r} @ {venue} {date} — nothing to regen",
              file=sys.stderr)
        return None
    return regen_event(eid, send_mail=send_mail)


def regen_event(eid, send_mail=True, force=None):
    """File one event's doc (caller holds the run lock). `force` = Brian's
    "Use new" picks, {cell_key: new text}."""
    with db.get_conn() as conn, conn.cursor() as cur:
        ev = db.get_event(cur, eid)
        acts = db.event_acts(cur, eid)
        cur.execute("SELECT count(*) AS n FROM events WHERE venue=%s AND event_date=%s",
                    (ev.get("venue"), ev.get("event_date")))
        n_same_day = cur.fetchone()["n"]

    d = ev.get("event_date")
    folder = fs.real_dropbox_root() / fs.real_venue_folder(ev.get("venue")) / fs.real_month_folder(ev.get("venue"), d)
    name = fs.event_display_name(ev, acts)
    if docmerge.all_acts_cancelled(ev, acts):
        name = f"CANCELLED - {name}"
    stem = fs.advance_stem(name, d)

    stageplot_names, plot_notices = {}, []
    for act in acts:
        stored = ((act.get("submission") or {}).get("data") or {}).get("stage_plot_file")
        if not stored:
            continue
        src = UPLOADS / stored
        band = act["artist"]["name"] if act.get("artist") else "band"
        fn = f"{fs.stageplot_stem(band, d)}{Path(stored).suffix}"
        if src.exists() and d >= dt.date.today():
            fn, notice = docmerge.file_stage_plot(src, folder, fn)
            if notice:
                plot_notices.append(notice)
        if (folder / fn).exists():
            stageplot_names[band] = fn

    res = docmerge.file_event_doc(eid, ev, acts, stem, stageplot_names=stageplot_names,
                                  n_events_same_day=n_same_day, force=force)
    res["notices"] = (res.get("notices") or []) + plot_notices
    docmerge.record_and_email_notices([(ev, res)], send_mail=send_mail)
    print(f"doc {res['action']}: {res.get('path')}"
          + (f" (renamed from {res['renamed_from']})" if res.get("renamed_from") else "")
          + (f" filled {res['filled']}" if res.get("filled") else "")
          + (f" {len(res['notices'])} notice(s)" if res.get("notices") else ""))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--venue", required=True)
    ap.add_argument("--date", required=True)
    ap.add_argument("--artist", required=True)
    ap.add_argument("--no-mail", action="store_true")
    ap.add_argument("--submission-id", type=int, default=None)
    args = ap.parse_args()
    regen(args.venue, str(args.date)[:10], args.artist, send_mail=not args.no_mail,
          submission_id=args.submission_id)


if __name__ == "__main__":
    main()
