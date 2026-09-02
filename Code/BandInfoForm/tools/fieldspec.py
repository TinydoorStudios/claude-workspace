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

VENUES = [
    "Fountain Square", "Washington Park", "Elm Street Plaza",
    "Court Street Plaza", "Zeigler Park", "Imagination Alley",
]
SLOTS = ["opener", "direct_support", "headliner"]

# ── Dropbox filing framework ──────────────────────────────────────────────────
# The finished advance doc files into <VenueAbbr>/<Year>/<MM Month>/, named
# "<MMDDYY> <Event Name> advance.docx". Email drafts go in an "Email Drafts"
# subfolder of the same month. Change these three lines to retune the whole scheme.
VENUE_ABBR = {
    "Fountain Square": "FSQ", "Washington Park": "WP", "Elm Street Plaza": "ESP",
    "Court Street Plaza": "Court", "Imagination Alley": "IA",
    "Zeigler Park": "ZP", "Memorial Hall": "Memo",
}
MONTHS = [None, "January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]
EMAIL_DRAFTS_DIR = "Email Drafts"


def venue_abbr(v):
    return VENUE_ABBR.get((v or "").strip(), (v or "Venue TBD").strip())


def month_folder(d):
    return f"{d.month:02d} {MONTHS[d.month]}"


def advance_stem(event_name, d):
    """Filename stem (no extension): '090626 513 Airwaves w Inhailer Radio advance'."""
    import re
    name = re.sub(r"[/\\:*?\"<>|]+", " ", str(event_name or "Untitled")).strip()
    name = re.sub(r"\s+", " ", name)
    return f"{d.strftime('%m%d%y')} {name} advance"

# (column label, internal key, choices|None)
EVENT_FIELDS = [
    ("Event Name",    "event_name",  None),
    ("Event Date",    "event_date",  None),
    ("Venue",         "venue",       VENUES),
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
    ("Performers",    "performers",    None, "drink tix"),
    ("Large Vehicle", "large_vehicle", ["Yes", "No"], "parking"),
]

# column label -> key, for every column in the sheet, in order
ALL_COLUMNS = (
    [(lbl, key, ch) for (lbl, key, ch) in EVENT_FIELDS] +
    [(lbl, key, ch) for (lbl, key, ch) in ACT_FIELDS] +
    [(lbl, key, ch) for (lbl, key, ch, _row) in BAND_FIELDS]
)
LABEL_TO_KEY = {lbl: key for (lbl, key, _ch) in ALL_COLUMNS}
BAND_KEYS = [key for (_l, key, _c, _r) in BAND_FIELDS]
EVENT_DETAIL_KEYS = ["event_type", "paying_band", "mc", "dj", "lead_name", "lead_phone",
                     "load_in", "soundcheck", "event_start", "event_end", "curfew"]

GROUPS = [
    ("EVENT — fill once per event", len(EVENT_FIELDS)),
    ("ACT", len(ACT_FIELDS)),
    ("BAND DETAILS — usually from the form; fill to override", len(BAND_FIELDS)),
]
