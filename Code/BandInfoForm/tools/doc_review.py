#!/usr/bin/env python3
"""Apply Brian's "Use new" decisions from /doc-review (2026-09-14).

  doc_review.py --apply 41 42 43

Cell notices: re-runs the merge for that show's doc with those cells forced
to the fresh value — only when the fresh value still matches what the review
page showed; otherwise the notice is superseded by a new one for the new
value. Stage-plot notices: the updated upload takes the plot's filename and
the old file is kept beside it as '(replaced MMDDYY-HHMM)'.
Anything that couldn't be applied gets doc_notices.apply_error.
"""
import argparse
import datetime as dt
import sys
import traceback
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
import regen_show

ERRORS = {"locked": "the doc is open in Word — close it and try again",
          "conflict": "the doc was saved while this ran — try again",
          "past": "the show is past", "no-date": "the show has no date"}
# 2026-09-21 sweep (DOC-11): notice keys no merge path can write (no cell is
# ever compared under them), so "Use new" can only fail
NOT_APPLIABLE = {"schedule|shape"}


def _set_error(nid, msg):
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("UPDATE doc_notices SET apply_error=%s WHERE id=%s AND resolved_at IS NULL", (msg, nid))
        conn.commit()


def _event_for(venue, date, key):
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, name, series FROM events WHERE venue=%s AND event_date=%s ORDER BY id DESC",
                    (venue, date))
        rows = cur.fetchall()
    exact = [r["id"] for r in rows if docmerge.event_key(r) == key]
    if exact:
        return exact[0]
    return rows[0]["id"] if len(rows) == 1 else None


def apply_plot(n):
    alt = n["cell_key"][len("plot:"):]
    folder = fs.real_dropbox_root() / fs.real_venue_folder(n["venue"]) / fs.real_month_folder(n["venue"], n["event_date"])
    cur_p, new_p = folder / (n["doc_value"] or ""), folder / alt
    if not new_p.exists():
        return _set_error(n["id"], f"{alt} is no longer in the show folder")
    if cur_p.exists():
        stamp = dt.datetime.now().strftime("%m%d%y-%H%M")
        cur_p.rename(folder / f"{cur_p.stem} (replaced {stamp}){cur_p.suffix}")
    new_p.rename(cur_p)
    with db.get_conn() as conn, conn.cursor() as cur:
        db.resolve_doc_notice(cur, n["id"], "applied")
        conn.commit()


def apply(ids):
    with db.get_conn() as conn, conn.cursor() as cur:
        notices = [db.get_doc_notice(cur, i) for i in ids]
    notices = [n for n in notices if n and n["resolved_at"] is None]
    groups = {}
    for n in notices:
        if not n.get("cell_key"):
            _set_error(n["id"], "this change predates decisions — update the doc by hand, then Keep doc")
        elif n["cell_key"].lower() in NOT_APPLIABLE:
            _set_error(n["id"], "this one can't be written automatically — rebuild the schedule in the doc "
                                "by hand (or clear its times so the next run rebuilds it), then Keep doc")
        elif n["cell_key"].startswith("plot:"):
            # 2026-09-21 sweep (DOC-5): a crash here must not strand this notice
            # (both radios disabled forever) or abort the rest of the batch
            try:
                apply_plot(n)
            except (Exception, SystemExit) as e:
                traceback.print_exc()
                _set_error(n["id"], f"couldn't move the stage plot ({type(e).__name__}) — see data/doc_review.log")
        else:
            groups.setdefault((n["venue"], n["event_date"], n["event_key"]), []).append(n)
    for (venue, date, key), ns in groups.items():
        eid = _event_for(venue, date, key)
        if not eid:
            for n in ns:
                _set_error(n["id"], "couldn't find this show's event")
            continue
        # 2026-09-21 sweep (DOC-5): a failed regen marks this group's notices and
        # moves on to the next group instead of leaving them 'Writing it into the doc…'
        try:
            res = regen_show.regen_event(eid, force={n["cell_key"]: n["new_value"] for n in ns})
        except (Exception, SystemExit) as e:
            traceback.print_exc()
            for n in ns:
                _set_error(n["id"], f"couldn't write the doc ({type(e).__name__}: {str(e)[:120]})"
                                    " — see data/doc_review.log")
            continue
        if res is None:
            continue
        applied = {k.lower() for k in res.get("applied") or ()}
        try:
            for n in ns:
                if res.get("action") in ERRORS:
                    _set_error(n["id"], ERRORS[res["action"]])
                elif n["cell_key"].lower() not in applied:
                    # superseded by a newer value (already recorded) or the cell moved
                    with db.get_conn() as conn, conn.cursor() as cur:
                        cur.execute("SELECT resolved_at FROM doc_notices WHERE id=%s", (n["id"],))
                        if cur.fetchone()["resolved_at"] is None:
                            _set_error(n["id"], "the form's answer changed again — review the new value")
                else:
                    # 2026-09-21 sweep (IDENT-11): written into the doc — close it even if
                    # the merge pass didn't (no-op when it already did)
                    with db.get_conn() as conn, conn.cursor() as cur:
                        db.resolve_doc_notice(cur, n["id"], "applied")
                        conn.commit()
        except (Exception, SystemExit) as e:
            traceback.print_exc()
            for n in ns:
                _set_error(n["id"], f"couldn't apply ({type(e).__name__}) — see data/doc_review.log")
            continue
        print(f"{venue} {date}: doc {res.get('action')}, applied {len(applied)}/{len(ns)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", type=int, nargs="+", required=True)
    args = ap.parse_args()
    from run_now import acquire_lock
    try:
        lock = acquire_lock()
    except SystemExit:
        # 2026-09-21 sweep (DOC-5): gave up waiting for the run lock — say so on the
        # page instead of leaving the notices pending forever
        for i in args.apply:
            _set_error(i, "a pipeline run is still going — try again in a few minutes")
        raise
    try:
        apply(args.apply)
    except (Exception, SystemExit) as e:
        traceback.print_exc()
        try:
            for i in args.apply:
                _set_error(i, f"couldn't apply ({type(e).__name__}) — see data/doc_review.log")
        except Exception:
            pass
        raise
    finally:
        try:
            import fcntl
            fcntl.flock(lock, fcntl.LOCK_UN)
            lock.close()
        except OSError:
            pass


if __name__ == "__main__":
    main()
