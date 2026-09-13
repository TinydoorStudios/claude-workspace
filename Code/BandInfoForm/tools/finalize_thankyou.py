#!/usr/bin/env python3
"""Thank-you email sent when Brian marks a show's advance Finalized
(2026-09-13, reversing a same-day "no thank-you emails" decision — see
ARCHITECTURE.md's Finalized-status section for that history).

Recap + day schedule are read from the filed advance .docx, NOT the
database — reuses daysheet.read_filed_advance/find_schedule_table wholesale
rather than re-parsing the doc from scratch, since that's already the
proven, tested path draft_emails.py's own returning-artist feature and
extract_advance_recap.py both already rely on. The doc (not the DB) is the
source specifically so a same-day hand-edit Brian makes directly in the
file — correcting a monitor count after a call with the band, say — reaches
the band; every OTHER automated email in this system only ever reads the
database, but that wouldn't see a Word-doc-only edit.

Fails closed: if the doc can't be found or this artist's own column in it
can't be resolved, build_recap() returns None and nothing is sent —
finalize_show() (app.py) must never let that block or fail the actual
sign-off, only skip the email.

Bilingual (Salsa On The Square only, matching venue_email.BILINGUAL_SERIES):
one message, English on top, the full Spanish version directly beneath it —
same separator draft_emails.py already uses for the welcome email. The
schedule/recap block itself is never duplicated/translated into the Spanish
half, same decision already made and documented for the welcome email
(advance_es.md.j2's own comment: those labels are the filed doc's own
English column headers, shown once).

    python3 finalize_thankyou.py --dry-run --venue "Fountain Square" \\
        --date 2026-09-18 --artist Wishy
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
import daysheet
import venue_email as ve
from regen_show import find_event
from docx import Document

# Recap rows worth telling the band about again, in this order — everything
# else read_filed_advance() returns (contact info, input notes, own-engineer
# coordination, stage type, etc.) is either redundant to echo back to them
# or staff-internal detail, left out on purpose, not an oversight. Doc label
# -> (friendly label shown in the email, value override or None to use the
# doc's own text verbatim).
RECAP_ROWS = [
    ("Number of Performers", "Performers", None),
    ("Monitors",             "Monitors", None),
    ("Backline",             "Backline", None),
    ("Merch",                "Merch", None),
    ("Dressing Room Tent",   "Dressing tent", None),
    ("Parking",              "Parking", None),
    ("Drink Tix",            "Drink tickets", None),
    # Stage Plot's doc text is an internal pointer ("See DB — file.pdf") —
    # meaningless to the band; just confirm one is on file.
    ("Stage Plot",           "Stage plot", "on file"),
]

# Schedule-table row-label fragments per slot (daysheet.find_schedule_table:
# time in cells[0], label in cells[-1]). A combined cell like "Opener Set
# Starts/ Direct Support Load-In" is matched as one string against every
# fragment below — either side can hit. Curfew applies to everyone and is
# handled separately, always appended last when present.
SLOT_SCHEDULE_FRAGMENTS = {
    "opener": [
        ("Load-in", ["Opener Load-In"]),
        ("Sound check", ["Opener Sound Check"]),
        ("Set starts", ["Opener Starts", "Opener Set Starts"]),
        ("Set ends", ["Opener Set End", "Opener End"]),
    ],
    "direct_support": [
        ("Load-in", ["Direct Support Load-In"]),
        ("Line check", ["Direct Support Line Check", "Direct Support Sound Check"]),
        ("Set starts", ["Direct Support Starts"]),
        ("Set ends", ["Direct Support Set End", "Direct Support End"]),
    ],
    "headliner": [
        ("Load-in", ["Headliner Load-In"]),
        ("Sound check", ["Headliner Sound Check"]),
        ("Set starts", ["Headliner Starts"]),
        ("Set ends", ["Headliner End", "Headliner Set End"]),
    ],
}


def _artist_slot(venue, show_date, artist_name):
    """This artist's slot (opener/direct_support/headliner) on the bill at
    venue/date, or None if it can't be resolved — the schedule block is
    just omitted in that case, not fatal to the recap."""
    with db.get_conn() as conn, conn.cursor() as cur:
        eid = find_event(cur, venue, show_date, artist_name)
        if not eid:
            return None
        acts = db.event_acts(cur, eid)
    target = daysheet.norm(artist_name)
    for a in acts:
        if a.get("artist") and daysheet.norm(a["artist"]["name"]) == target:
            return a.get("slot")
    return None


def _schedule_lines(doc, slot):
    """[(human label, time), ...] for this slot's relevant rows plus
    Curfew, in schedule order. Any single row that can't be matched is
    just skipped, never fatal to the rest."""
    table = daysheet.find_schedule_table(doc)
    if table is None:
        return []
    fragments = SLOT_SCHEDULE_FRAGMENTS.get(slot, [])
    found = {}
    curfew_time = None
    all_rows = []  # every (label, time) row seen, for the single-band fallback below
    for row in table.rows:
        if not row.cells:
            continue
        label_text = row.cells[-1].text.strip()
        time_text = row.cells[0].text.strip()
        if not label_text or not time_text:
            continue
        if daysheet.norm(label_text) == "curfew":
            curfew_time = time_text
            continue
        all_rows.append((label_text, time_text))
        label_norm = daysheet.norm(label_text)
        for human, candidates in fragments:
            if human in found:
                continue
            if any(daysheet.norm(c) in label_norm for c in candidates):
                found[human] = time_text
    lines = [(human, found[human]) for human, _ in fragments if human in found]
    if not lines and all_rows:
        # Opener/Direct Support/Headliner labels didn't match anything — a
        # single-house-band series (Salsa On The Square's "Set #1" / "Dance
        # Instruction #1" / "Set #2" format, confirmed 2026-09-13, is nothing
        # like the standard multi-act schedule) or a template variant this
        # doesn't recognize. There's no other band's info to filter out on a
        # single-band bill anyway, so show every row exactly as filed rather
        # than silently dropping the whole schedule.
        lines = all_rows
    if curfew_time:
        lines.append(("Curfew", curfew_time))
    return lines


def build_recap(venue, show_date, artist_name):
    """(schedule_lines, recap_lines) for this artist's finalized show, or
    None if the filed doc — or this artist's own column in it — can't be
    resolved. None is the fail-closed signal: callers must not send
    anything when this comes back None, and must not guess at a
    replacement."""
    found = daysheet.read_filed_advance(venue, show_date, artist_name)
    if not found:
        return None
    path, rows = found
    rows_by_label = {label: text for label, text in rows}
    recap_lines = []
    for doc_label, friendly, override in RECAP_ROWS:
        if doc_label in rows_by_label:
            recap_lines.append((friendly, override or rows_by_label[doc_label]))

    schedule_lines = []
    try:
        doc = Document(str(path))
    except Exception:
        doc = None
    if doc is not None:
        slot = _artist_slot(venue, show_date, artist_name)
        if slot:
            schedule_lines = _schedule_lines(doc, slot)
    return schedule_lines, recap_lines


def _day_phrase(show_date):
    """'Friday, September 18th' — matches the tone of the sample draft
    Brian approved, not us_date()'s M/D/Y (that's for structured email
    fields, not conversational prose)."""
    day = show_date.day
    suffix = "th" if 11 <= day % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return show_date.strftime(f"%A, %B {day}{suffix}")


def build_email(band, venue, show_date, schedule_lines, recap_lines, bilingual):
    """(subject, body) — bilingual=True appends a Spanish version of the
    surrounding prose (not the schedule/recap block — see module docstring)
    beneath the English body, same separator style as the welcome email."""
    day_phrase = _day_phrase(show_date)
    subject = f"You're All Set — {band} at {venue} ({show_date.strftime('%-m/%-d')})"

    sched_block = "\n".join(f"  {label}: {time}" for label, time in schedule_lines)
    recap_block = "\n".join(f"  {label}: {value}" for label, value in recap_lines)

    body_en = (
        f"Hey {band},\n\n"
        f"Everything's locked in for your set at {venue} on {day_phrase}. "
        f"Thanks for getting the advance squared away — makes the whole night "
        f"run smoother for everybody.\n\n"
    )
    if sched_block:
        body_en += f"Here's the day, start to finish:\n\n{sched_block}\n\n"
    if recap_block:
        body_en += f"And a quick recap of what we've got on file for you:\n\n{recap_block}\n\n"
    body_en += (
        f"If anything changes before the show — headcount, gear, anything — "
        f"just reply to this email and I'll get it updated. Same goes for "
        f"show day: if something comes up, reply here and I'll get right "
        f"back to you.\n\n"
        f"See you {day_phrase.split(',')[0]}.\n\n"
        f"3CDC Events / Production"
    )

    if not bilingual:
        return subject, body_en

    body_es = (
        f"Hola {band},\n\n"
        f"Todo está confirmado para su presentación en {venue} el {show_date.strftime('%d/%m/%Y')}. "
        f"Gracias por completar el formulario de avance — esto ayuda a que "
        f"la noche salga bien para todos.\n\n"
        f"Si algo cambia antes del show — el número de personas, equipo, lo "
        f"que sea — respondan a este correo y lo actualizamos. Lo mismo "
        f"aplica el día del evento: si surge algo, respondan aquí y les "
        f"contestamos enseguida.\n\n"
        f"Nos vemos pronto.\n\n"
        f"3CDC Events / Production"
    )
    sep = "─" * 42
    body = f"{body_en}\n\n{sep}\nESPAÑOL / SPANISH VERSION BELOW\n{sep}\n\n{body_es}"
    return subject, body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--venue", required=True)
    ap.add_argument("--date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--artist", required=True)
    ap.add_argument("--dry-run", action="store_true", help="print, never send")
    args = ap.parse_args()
    show_date = dt.date.fromisoformat(args.date)

    result = build_recap(args.venue, show_date, args.artist)
    if result is None:
        print(f"NO MATCH — could not resolve a filed doc/column for "
              f"{args.artist!r} @ {args.venue} {show_date}", file=sys.stderr)
        sys.exit(1)
    schedule_lines, recap_lines = result
    print("schedule:", schedule_lines)
    print("recap:", recap_lines)
    bilingual = ve.is_bilingual_series(args.artist)  # placeholder for CLI testing only
    subject, body = build_email(args.artist, args.venue, show_date,
                                 schedule_lines, recap_lines, bilingual=False)
    print(f"\nSubject: {subject}\n\n{body}")


if __name__ == "__main__":
    main()
