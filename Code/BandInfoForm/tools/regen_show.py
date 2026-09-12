#!/usr/bin/env python3
"""Regenerate ONE show's advance doc — scoped, so a single band's form
submission never re-files every other show (Brian, 2026-09-11).

The full pipeline (run_now.py -> package_run.py) rebuilds every event and
overlays the whole venue tree, which restamps all files on any submit. This
does the minimum a submit actually needs: find the event for the submitting
show, refill just its advance .docx into the venue archive, and file that
band's stage plot next to it. No sheet re-import, no other events, no
full-tree overlay.

  regen_show.py --venue "Washington Park" --date 2026-09-16 --artist "Anything Blues"
"""
import argparse
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _c in (HERE.parent, HERE.parent / "app"):
    if (_c / "advance_db.py").exists():
        sys.path.insert(0, str(_c))
        break
sys.path.insert(0, str(HERE))
import advance_db as db
import fieldspec as fs
import daysheet

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


def regen(venue, date, artist, root=None):
    with db.get_conn() as conn, conn.cursor() as cur:
        eid = find_event(cur, venue, date, artist)
        if not eid:
            print(f"no event for {artist!r} @ {venue} {date} — nothing to regen",
                  file=sys.stderr)
            return None
        ev = db.get_event(cur, eid)
        acts = db.event_acts(cur, eid)

    d = ev.get("event_date")
    root = root or fs.real_dropbox_root()
    folder = root / fs.real_venue_folder(ev.get("venue")) / fs.real_month_folder(ev.get("venue"), d)
    folder.mkdir(parents=True, exist_ok=True)
    # Same stable-name rule as package_run.event_stem: event name, else series,
    # else the band — never let the filename drift with the act list.
    stem = fs.advance_stem(ev.get("name") or ev.get("series") or artist, d)

    # file each act's uploaded stage plot next to the doc (band-named), same as
    # package_run does, so the day-sheet's Stage Plot cell can point at it.
    stageplot_names = {}
    for act in acts:
        stored = ((act.get("submission") or {}).get("data") or {}).get("stage_plot_file")
        if not stored:
            continue
        src = UPLOADS / stored
        if not src.exists():
            continue
        band = act["artist"]["name"] if act.get("artist") else "band"
        fn = f"{fs.stageplot_stem(band, d)}{Path(stored).suffix}"
        shutil.copy(src, folder / fn)
        stageplot_names[band] = fn

    out = folder / f"{stem}.docx"
    daysheet.fill(eid, out_path=out, stageplot_names=stageplot_names)
    print(f"regenerated: {out}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--venue", required=True)
    ap.add_argument("--date", required=True)
    ap.add_argument("--artist", required=True)
    args = ap.parse_args()
    regen(args.venue, str(args.date)[:10], args.artist)


if __name__ == "__main__":
    main()
