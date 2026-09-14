#!/usr/bin/env python3
"""Orphan-show hold (2026-09-13 audit #4).

A show that is no longer in the advance sheet (row deleted, or a date / venue /
band name corrected — which makes a NEW show row) must never keep emailing a
band. After every package run this compares every current show against the
sheet (plus bookings not seeded into it yet). A show missing from both is put
ON HOLD — no sends of any kind — and Brian gets one email with Cancel /
Restore / "typo for → corrected show" (merge) choices.

A brand-new show that looks like the corrected version of a held one (same
band on another date/venue, or same venue+date under another name, created in
the last 2 days, no welcome sent yet) is held too, so the band never gets a
second welcome while Brian decides. Restore/Cancel releases those; Merge moves
the held show's history onto it.

Guard: if the sheet reads empty, or more than max(3, 30%) of current shows
would be held at once, nothing is held — a broken/half-synced sheet must not
freeze the whole pipeline — and Brian is alerted once that day instead.
"""
import datetime as dt
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _c in (HERE.parent, HERE.parent / "app"):
    if (_c / "advance_db.py").exists():
        sys.path.insert(0, str(_c))
        break
sys.path.insert(0, str(HERE))
import advance_db as db
from sheet import read_advance_sheet

PUBLIC_URL = os.environ.get("ADVANCE_PUBLIC_URL", "https://advance.tinydoorstudios.com")
MISSING_REASON = "missing from the advance sheet"


def _ident(name, venue, date):
    return (db.normalize(name), (venue or "").strip().lower(), str(date or "")[:10])


def run(sheet_path, send_mail=True, dry_run=False):
    import mailer
    rows = read_advance_sheet(sheet_path)
    idents = {_ident(r.get("artist_name"), r.get("venue"), r.get("event_date")) for r in rows}
    with db.get_conn() as conn, conn.cursor() as cur:
        for b in db.unseeded_bookings(cur):
            idents.add(_ident(b.get("artist_name"), b.get("venue"), b.get("event_date")))
        active = [s for s in db.active_future_shows(cur)
                  if s["held_at"] is None and s["hold_dismissed_at"] is None]
        cur.execute("""SELECT DISTINCT sub.show_id FROM submission_matches m
                       JOIN submissions sub ON sub.id = m.submission_id
                       WHERE m.status = 'pending_pick' AND m.resolved_at IS NULL""")
        pending = {r["show_id"] for r in cur.fetchall()}

    if not rows:
        print("  ! holds: sheet read returned no rows — skipped")
        return {"held": 0, "skipped": "empty sheet"}
    orphans = [s for s in active
               if _ident(s["artist_name"], s["venue"], s["show_date"]) not in idents
               and s["id"] not in pending]
    limit = max(3, int(0.3 * len(active)))
    if len(orphans) > limit:
        print(f"  ! holds: {len(orphans)} of {len(active)} shows missing from the sheet — "
              "looks like a bad sheet read, nothing held")
        if send_mail and not dry_run:
            with db.get_conn() as conn, conn.cursor() as cur:
                already = db.job_ran_since(cur, "holds-guard-alert", "auto",
                                           dt.datetime.combine(dt.date.today(), dt.time()))
                if not already:
                    ok, _ = mailer.alert(
                        "Advance sheet check skipped — too many shows missing",
                        f"<p>{len(orphans)} of {len(active)} current shows weren't found in "
                        "advance-list.xlsx on this run, so none were put on hold (a sheet that "
                        "was mid-sync or damaged shouldn't freeze everything). Check the sheet.</p>")
                    if ok:
                        db.record_job_run(cur, "holds-guard-alert", "auto")
                        conn.commit()
        return {"held": 0, "skipped": "too many"}

    held = 0
    if orphans and not dry_run:
        with db.get_conn() as conn, conn.cursor() as cur:
            for o in orphans:
                if db.hold_show(cur, o["id"], MISSING_REASON):
                    held += 1
                    for c in db.merge_candidates(cur, o["id"]):
                        if (c["advance_draft_created_at"] is None and c["responded_at"] is None
                                and c["held_at"] is None and c["hold_dismissed_at"] is None
                                and c["created_at"] >= dt.datetime.now(c["created_at"].tzinfo)
                                - dt.timedelta(days=2)):
                            db.hold_show(cur, c["id"], f"possible correction of show {o['id']}")
            conn.commit()
    for o in orphans:
        print(f"  {'would hold' if dry_run else 'HOLD'}: {o['artist_name']} @ {o['venue']} {o['show_date']}")

    if send_mail and not dry_run:
        notify()
    return {"held": held, "orphans": len(orphans)}


def notify():
    import mailer
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("""SELECT s.*, a.name AS artist_name FROM shows s JOIN artists a ON a.id=s.artist_id
                       WHERE s.held_at IS NOT NULL AND s.hold_notified_at IS NULL
                         AND s.hold_reason = %s ORDER BY s.show_date""", (MISSING_REASON,))
        held = cur.fetchall()
        if not held:
            return 0
        blocks = []
        for h in held:
            cands = db.merge_candidates(cur, h["id"])
            cand_html = "".join(
                f"<li>{mailer.esc(c['artist_name'])} — {mailer.esc(c['venue'])} "
                f"{c['show_date'].strftime('%m/%d/%Y') if c['show_date'] else '?'}</li>" for c in cands)
            sent = " (welcome already sent)" if h["advance_draft_created_at"] else ""
            blocks.append(
                f"<div style='margin:12px 0;padding:10px;border:1px solid #ddd'>"
                f"<b>{mailer.esc(h['artist_name'])}</b> — {mailer.esc(h['venue'])} "
                f"{h['show_date'].strftime('%m/%d/%Y')}{sent}<br>"
                + (f"Possible corrected version(s):<ul>{cand_html}</ul>" if cand_html else
                   "<i>No likely corrected version found.</i><br>")
                + f"<a href='{PUBLIC_URL}/show/{h['id']}/hold'>Decide: cancel / restore / merge →</a></div>")
    html = ("<div style='font-family:-apple-system,sans-serif;font-size:13px'>"
            "<p>These shows are no longer in advance-list.xlsx, so they're <b>on hold</b> — "
            "nothing will be emailed for them until you decide. If one was a typo fix, merge it into "
            "the corrected show so the band doesn't get a second welcome.</p>"
            + "".join(blocks) + "</div>")
    ok, _ = mailer.alert(f"Advance shows on hold — {len(held)} need a decision", html)
    if ok:
        with db.get_conn() as conn, conn.cursor() as cur:
            cur.execute("UPDATE shows SET hold_notified_at = now() WHERE id = ANY(%s)",
                        ([h["id"] for h in held],))
            conn.commit()
    return len(held)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("sheet")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-mail", action="store_true")
    a = ap.parse_args()
    print(run(a.sheet, send_mail=not a.no_mail, dry_run=a.dry_run))
