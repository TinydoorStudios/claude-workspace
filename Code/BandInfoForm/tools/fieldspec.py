#!/usr/bin/env python3
"""Single source of truth tying the three surfaces together:

  the Advance List SPREADSHEET  (Brian's master source)
  the advance FORM              (band fills the band-detail fields)
  the day-sheet DOCUMENT        (generated from spreadsheet + form, merged)

Each field has: column label (spreadsheet), internal key (matches the FORM field
name where the band provides it), an optional dropdown choice list, and — for
band fields — the day-sheet row it maps to.

Merge rule (Brian's directive): the SPREADSHEET value wins when present; the FORM
submission fills anything the spreadsheet left blank.
"""
import os
from pathlib import Path

VENUES = [
    "Fountain Square", "Washington Park", "Elm Street Plaza",
    "Court Street Plaza", "Zeigler Park", "Imagination Alley",
]
SLOTS = ["opener", "direct_support", "headliner"]

# ── Dropbox filing framework (2026-09-12 — real venue folders) ────────────────
# The finished advance doc + stage plot file into the REAL, human-used venue
# folder in Brian's actual Dropbox — not the Nyquist working archive:
#
#   ~/Dropbox/<Real Venue Folder>/<MM.YYYY Code>/<MMDDYY> <Event Name> - <Headliner> Prod Adv.docx
#   ~/Dropbox/<Real Venue Folder>/<MM.YYYY Code>/<MMDDYY> <Event Name> Stageplot.<ext>
#
# e.g. ~/Dropbox/3CDC Fountain Square/09.2026 FSQ/091826 513 Airwaves w Inhaler
# Radio - RatBoys Prod Adv.docx — matching the convention Brian and the rest
# of the 3CDC production team have always hand-typed into that folder, so the
# pipeline's output sits exactly where a human would look for it, named the
# way a human would name it. The " - <Headliner>" segment was added 2026-09-13
# (see package_run.py's event_stem/headliner_name) — reversing the 2026-09-11
# "no band name in the filename" rule below, on purpose: Brian wants to see
# who's playing without opening the file, and accepts that the filename now
# changes (old one left orphaned on disk) if the headliner changes before
# the show — the exact tradeoff 2026-09-11 was written to avoid.
#
# Email drafts have no analog in the real, shared folders (they're an internal
# working artifact, not a finished document) and stay under the Nyquist
# cockpit instead, in the OLD scheme: Nyquist/<VenueAbbr>/<Year>/<MM Month>/
# Email Drafts/ — see VENUE_ABBR + month_folder() below, unchanged from before
# this migration. real_venue_folder()/real_month_folder() are the new ones;
# venue_abbr()/month_folder() are legacy-but-still-live, Nyquist-drafts-only.
# ADVANCE_DROPBOX_ROOT overrides the root for staging/tests (2026-09-13 audit)
# so a test run can never write into the real shared venue folders.
REAL_DROPBOX_ROOT = Path(os.environ.get("ADVANCE_DROPBOX_ROOT") or (Path.home() / "Dropbox"))

VENUE_REAL_FOLDER = {
    "Fountain Square": "3CDC Fountain Square", "Washington Park": "3CDC Washington Park",
    "Elm Street Plaza": "3CDC Elm Street Plaza", "Court Street Plaza": "3CDC Court Street",
    "Imagination Alley": "3CDC Imagination Alley",
    "Zeigler Park": "3CDC Ziegler Park",  # real folder spells it "Ziegler", not "Zeigler"
    "Memorial Hall": "3CDC Memorial Hall",
}
VENUE_MONTH_CODE = {
    "Fountain Square": "FSQ", "Washington Park": "WP", "Elm Street Plaza": "ESP",
    "Court Street Plaza": "CSP", "Imagination Alley": "IA",
    "Zeigler Park": "ZP", "Memorial Hall": "MEMO",
}

# Legacy Nyquist-drafts scheme (Email Drafts/ only, as of 2026-09-12) — do not
# repoint these at the real folders, and do not rename the codes below (WP/FSQ
# folders already exist on disk under these names); Court/Memo casing here is
# cosmetic and only ever touched Nyquist's own working tree, never the real one.
VENUE_ABBR = {
    "Fountain Square": "FSQ", "Washington Park": "WP", "Elm Street Plaza": "ESP",
    "Court Street Plaza": "Court", "Imagination Alley": "IA",
    "Zeigler Park": "ZP", "Memorial Hall": "Memo",
}
MONTHS = [None, "January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]
EMAIL_DRAFTS_DIR = "Email Drafts"


def real_dropbox_root():
    return REAL_DROPBOX_ROOT


def nyquist_root():
    """The Nyquist cockpit (advance-list.xlsx, Series Email Templates, Show
    Status Log) — always under the same Dropbox root as the venue folders."""
    return REAL_DROPBOX_ROOT / "Nyquist"


def real_venue_folder(v):
    return VENUE_REAL_FOLDER.get((v or "").strip(), (v or "Venue TBD").strip())


def real_month_folder(v, d):
    code = VENUE_MONTH_CODE.get((v or "").strip(), venue_abbr(v))
    return f"{d.month:02d}.{d.year} {code}"


def venue_abbr(v):
    return VENUE_ABBR.get((v or "").strip(), (v or "Venue TBD").strip())


def month_folder(d):
    return f"{d.month:02d} {MONTHS[d.month]}"


def _clean(name):
    import re
    name = re.sub(r"[/\\:*?\"<>|]+", " ", str(name or "Untitled")).strip()
    return re.sub(r"\s+", " ", name)


def advance_stem(event_name, d):
    """Filename stem (no extension): '090626 513 Airwaves w Inhaler Radio Prod Adv'
    — matches the real folders' own hand-typed convention (Brian/3CDC staff)."""
    return f"{d.strftime('%m%d%y')} {_clean(event_name)} Prod Adv"


def headliner_name(acts):
    """Top-of-the-bill act's name, for the filename (Brian, 2026-09-13 —
    reversing the 2026-09-11 "no band name in the filename" rule: he wants to
    see who's playing without opening the file, and accepts that the
    filename now changes if the headliner changes before the show). Prefers
    the act actually slotted "headliner"; falls back to the last act in slot
    order (event_acts is always queried ORDER BY slot_order, so the last one
    is the closest guess at "top of the bill") if none is explicitly marked.
    None if there are no acts with an artist attached yet.

    Single source of truth — package_run.py (the full rebuild) and
    regen_show.py (the single-show regen used by /submit, added 2026-09-11
    specifically so a submit doesn't have to touch every file) both call
    this and event_display_name below, so there's exactly one place that
    decides what an event's filename looks like, not two copies that can
    drift apart."""
    for a in acts:
        if a.get("slot") == "headliner" and a.get("artist"):
            return a["artist"]["name"]
    for a in reversed(acts):
        if a.get("artist"):
            return a["artist"]["name"]
    return None


def event_display_name(ev, acts):
    """The <Event/Series> - <Headliner> name that goes into advance_stem — see
    headliner_name above for why the headliner is appended and by whom.

    Real-data dry run (2026-09-13, against every currently active event)
    caught a real duplication bug before this ever shipped: several bookings
    already have the headliner hand-typed right into the Event Name field
    itself (e.g. "Blues & Brews - Ricky Nye", "Tailgate w The Closers") —
    appending the headliner again there would produce "... - Ricky Nye -
    Ricky Nye". A substring check on the base name skips the append whenever
    it's already there."""
    base = ev.get("name") or ev.get("series")
    headliner = headliner_name(acts)
    if base and headliner:
        if headliner.lower() in base.lower():
            return base
        return f"{base} - {headliner}"
    if headliner:
        return headliner
    if base:
        return base
    return ", ".join(a["artist"]["name"] for a in acts if a.get("artist")) or "Untitled"


def stageplot_stem(event_name, d):
    """Filename stem for a filed stage plot: '090626 513 Airwaves... Stageplot'."""
    return f"{d.strftime('%m%d%y')} {_clean(event_name)} Stageplot"

# (column label, internal key, choices|None)
EVENT_FIELDS = [
    ("Event Name",    "event_name",  None),
    ("Event Date",    "event_date",  None),
    ("Venue",         "venue",       VENUES),
    # WP-only sub-venue (Brian, 2026-09-06): Main Stage / Porch / Bandstand —
    # each has its own monitor cap and Porch/Bandstand have no lighting.
    # Blank for every other venue. See forms_config.WP_LOCATIONS (app side).
    ("Location",      "location",    ["Main Stage", "Porch", "Bandstand"]),
    # Brian, 2026-09-08: declared per booking so a multi-band bill entered one
    # act at a time still knows it's multi-band on day one — see
    # draft_emails.py (drops "take set breaks as needed" when >1) and
    # daysheet.py (picks the N-band template even before every act has a row
    # yet). Physically appended as its OWN column at the end of the live
    # sheet, not inserted mid-layout — see the 2026-09-08 session notes on why
    # (merge-range + _advance_meta address safety).
    ("Band Count",    "band_count",  ["1", "2", "3"]),
    ("Series",        "series",      None),
    ("Event Type",    "event_type",  ["Internal", "Third Party"]),
    ("Paying Band?",  "paying_band", ["Yes", "No"]),
    ("MC",            "mc",          None),
    ("DJ",            "dj",          None),
    ("Lead Name",     "lead_name",   None),   # day-of / onsite contact
    ("Lead Phone",    "lead_phone",  None),
    ("Load-In",       "load_in",     None),   # day schedule (blank -> FSQ standard)
    ("Sound Check",   "soundcheck",  None),
    ("Start",         "event_start", None),
    ("End",           "event_end",   None),
    ("Curfew",        "curfew",      None),
]

# Fixed reference used in the advance email.
ADVANCING_CONTACT = "Brian Lloyd (315-404-5648)"
VENUE_LOCATION = {
    "Fountain Square": "Fountain Square – Mainstage; 520 Vine St. Cincinnati, OH 45202",
    # add the other venues' location lines as they're confirmed
}
# fallback day schedule when the sheet leaves a field blank (FSQ standard)
SCHEDULE_DEFAULTS = {
    "load_in": "6:00p", "soundcheck": "6:30p", "event_start": "7:00p",
    "event_end": "10:00p", "curfew": "11:00p",
}

ACT_FIELDS = [
    ("Slot",          "slot",         SLOTS),
    ("Set Length",    "set_time",     None),   # duration of the act's set (key kept as set_time)
    ("Artist Name",   "artist_name",  None),
    ("Contact Email", "contact_email", None),
    ("Email Note",    "email_note",   None),   # a personal line woven into THIS band's advance email
]

# Band detail — normally from the form; fill in the sheet to override.
# `dsrow` = normalized day-sheet row label this field contributes to.
BAND_FIELDS = [
    ("Contact Name",  "contact_name",  None, "contact"),
    ("Contact Phone", "contact_phone", None, "contact"),
    ("Stage Type",    "stage_type",    ["Flat stage", "Drum riser"], "scenic"),
    ("Monitors",      "monitors",      None, "monitors/ iem"),
    ("Own IEMs",      "own_iems",      ["Yes", "No"], "monitors/ iem"),
    ("Split Snake",   "split_snake",   ["Yes", "No"], "monitors/ iem"),
    ("Stage Plot",    "stage_plot_desc", None, "stage plot"),
    ("Input Notes",   "input_notes",   None, "input notes"),
    ("Backline",      "backline",      None, "backline"),
    ("Own Engineer",  "own_engineer",  ["No — use house engineers",
                                        "Yes — bringing our own (we'll coordinate)"], "engineer"),
    ("Scenic",        "scenic",        None, "scenic"),
    ("Lighting",      "lighting",      None, "lighting"),
    ("Merch",         "merch",         ["Yes", "No"], "merch"),
    ("Band Tent",     "band_tent",     ["Yes, please provide the tent",
                                        "No, not needed"], "dressing room tent"),
    ("Performers",    "performers",    None, "number of performers"),
    ("Vehicle Count", "vehicle_count", None, "parking"),
    # large_vehicle (Yes/No) replaced by a count (Brian, 2026-09-13) — kept
    # here so old submissions' answers still surface in the sheet/exports;
    # nothing new ever writes it. Large Vehicle Count is what the form
    # actually asks now.
    ("Large Vehicle", "large_vehicle", ["Yes", "No"], "parking"),
    ("Large Vehicle Count", "large_vehicle_count", None, "parking"),
]

# column label -> key, for every column in the sheet, in order
ALL_COLUMNS = (
    [(lbl, key, ch) for (lbl, key, ch) in EVENT_FIELDS] +
    [(lbl, key, ch) for (lbl, key, ch) in ACT_FIELDS] +
    [(lbl, key, ch) for (lbl, key, ch, _row) in BAND_FIELDS]
)
LABEL_TO_KEY = {lbl: key for (lbl, key, _ch) in ALL_COLUMNS}
BAND_KEYS = [key for (_l, key, _c, _r) in BAND_FIELDS]
EVENT_DETAIL_KEYS = ["location", "event_type", "paying_band", "mc", "dj", "lead_name", "lead_phone",
                     "load_in", "soundcheck", "event_start", "event_end", "curfew", "band_count"]

GROUPS = [
    ("EVENT — fill once per event", len(EVENT_FIELDS)),
    ("ACT", len(ACT_FIELDS)),
    ("BAND DETAILS — usually from the form; fill to override", len(BAND_FIELDS)),
]
