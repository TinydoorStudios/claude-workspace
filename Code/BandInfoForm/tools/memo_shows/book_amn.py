"""One-off (2026-09-29): book A Man Named Cash (Memo, 10/16/26) and load its
approved advance answers, with NO email of any kind.

Why not /booking: that route emails a staff "New booking" summary. This writes
the same rows the route would (bookings row, artist, show) and the answers as
one staff submission — the same shape /memo/submit writes — and registers the
three documents as the show's uploads. Memo welcomes are paused and the booking
is marked manual (skip_welcome_email), so no lifecycle run will email the band.

Run on the n8n VM from /opt/band-advance with advance.env loaded:
    python3 /tmp/book_amn.py /tmp/amn_answers.json /tmp/amn_docs
"""
import datetime as dt
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, "/opt/band-advance")
import advance_db as db  # noqa: E402
import memo_fields as M  # noqa: E402

ans = json.loads(Path(sys.argv[1]).read_text())
docs = Path(sys.argv[2])
sh = ans["_show"]
ARTIST, VENUE, DATE = sh["artist"], sh["venue"], sh["date"]
UPLOADS = Path("/opt/band-advance/data/uploads")
DATA = Path("/opt/band-advance/data")

with db.get_conn() as conn, conn.cursor() as cur:
    cur.execute("SELECT current_database() AS d")
    assert cur.fetchone()["d"] == "advance", "not the live database"
    cur.execute("""SELECT 1 FROM shows s JOIN artists a ON a.id = s.artist_id
                   WHERE a.name = %s AND s.venue = %s AND s.show_date = %s""", (ARTIST, VENUE, DATE))
    assert not cur.fetchone(), "show already exists — nothing done"
    bid = db.insert_booking(cur, {
        "event_name": sh["event"], "event_date": DATE, "venue": VENUE,
        "series": "Stand-Alone Internal", "event_type": "Internal",
        "load_in": "4:00p", "soundcheck": "5:00p", "event_start": "8:00p", "event_end": "10:00p",
        "curfew": "11:30p", "set_time": "100 min",
        "lead_name": "Joe", "lead_phone": "216-288-7269",
        "artist_name": ARTIST, "contact_name": "Bruce Lant",
        "contact_email": ans.get("contact_email"),
        "email_note": "",   # band-visible: never put a note (or any mention of the assistant) here
        "entered_by": "Brian Lloyd",
        "skip_welcome_email": True,
    })
    artist_id = db.upsert_artist(cur, ARTIST, email=ans.get("contact_email"),
                                 phone=ans.get("contact_phone"))
    show_id = db.upsert_show(cur, artist_id, VENUE, dt.date.fromisoformat(DATE), series="Stand-Alone Internal")
    conn.commit()
print("booking", bid, "artist", artist_id, "show", show_id)

stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
files = []
for i, (name, kind) in enumerate((
        ("10.16.26 A Man Named Cash Stage Plot.pdf", "stage_plot"),
        ("10.16.26 A Man Named Cash Tech Rider (MH Redline).pdf", "tech_rider"),
        ("10.16.26 A Man Named Cash Hospitality Rider (MH Redline).pdf", "hospitality_rider"))):
    src = docs / name
    stored = f"{stamp}-{i:02d}__a-man-named-cash__{name.replace(' ', '_')}"
    shutil.copy2(src, UPLOADS / stored)
    files.append({"kind": kind, "filename": name, "stored_name": stored,
                  "mime": "application/pdf", "size": src.stat().st_size})

rec = {k: v for k, v in ans.items() if k in M.FIELDS}
rec.update({"band_name": ARTIST, "venue": VENUE, "show_date": DATE, "show_series": "Stand-Alone Internal",
            "_form": M.FORM_KEY, "_staff_edit": True, "artist_id": str(artist_id),
            "memo_files": files, "_submitted_at": dt.datetime.now().isoformat(timespec="seconds"),
            "_source_note": "Loaded from redlined riders, stage plot, cost model; approved by Brian 2026-09-29"})
(DATA / f"{stamp}__a-man-named-cash__memo.json").write_text(json.dumps(rec, indent=2))
res = db.record_submission(rec, file_info=None, source="staff", carry_plot=False, stamp_responded=False)
with db.get_conn() as conn, conn.cursor() as cur:
    for f in files:
        db.insert_file(cur, res["submission_id"], res["artist_id"], f["filename"], f["stored_name"],
                       kind=f["kind"], mime=f["mime"], size=f["size"])
    conn.commit()
print("submission", res)
