#!/usr/bin/env python3
"""Per-venue (and per-series) advance-email content blocks.

The advance email's body is venue-specific — Fountain Square's garage QR codes and
95 dBA-Slow ordinance have no business in a Washington Park or Memorial Hall email. This
keeps one email skeleton (greeting, form link, schedule, common rules) and swaps the
venue-specific blocks: location, load-in/parking, technical, hospitality, and any
venue-only performance rules.

To add a venue: copy the FSQ dict, replace the prose. Anything you leave out falls
back to DEFAULT (a generic, non-FSQ-specific block that is safe to send as-is).
COMMON_REQUIREMENTS is the 3CDC-wide policy and appends to every venue.

A series can override any of those same blocks on top of its venue's content.
That content lives as files in Dropbox, not in this module (Brian, 2026-09-09:
"one central location" he edits directly, no code deploy needed) —
~/Dropbox/Nyquist/Series Email Templates/<Venue>/<Series>.md, read live on
every call. A series with no file there, or no series on the booking at all,
falls straight through to the plain venue email. See the README in that
folder for the file format.

A block's prose can reference `{some_key}` placeholders — draft_emails.py fills
them per show via blocks_for's **dynamic kwargs (e.g. WP's {location}/{stage_size},
sourced from the booking's Location field and forms_config.WP_LOCATIONS). Only
blocks containing the referenced placeholder are touched; everything else is a
plain string, unaffected by the substitution pass.
"""
import re
import sys
from pathlib import Path

# 3CDC-wide, appended under Performance Requirements for every venue.
COMMON_REQUIREMENTS = """\
- Content: family-friendly only — no foul language or gestures, including prerecorded tracks, live vocals, and sound check.
- Performer safety: stay on the stage. No crowd surfing, climbing, jumping off stage, or stepping on sound equipment.
- Audience safety: do not throw or shoot anything into the crowd (confetti, t-shirts, bottles, merch/CDs, etc.).
- Weather: rain or shine. Booking evaluates weather about 3 hours before start; if you don't hear otherwise, assume the show goes on.
- Payment: all groups are paid after the performance, not before."""

# Generic, safe-to-send blocks for a venue we haven't customized yet (no FSQ specifics).
DEFAULT = {
    "location": None,   # falls back to the venue name in the template
    "load_in": """\
Load-In & Parking:
Your day-of contact will coordinate load-in and parking with you. Text or call them when you're about 5 minutes out, and introduce yourself onsite as soon as you arrive. Note any large-vehicle needs on the form.""",
    "technical": """\
Technical:
- Backline / instrumentation: artists provide all instruments, including amps and 1/4" cables.
- Audio: we provide an engineer who mixes FOH and monitors. Coordinate in advance if you're bringing your own.
- Stage plot / input list, stage layout, monitor count, and any scenic elements — all on the form.""",
    "hospitality": """\
Hospitality & Site:
- Merch: if you're selling, you provide the seller, point of sale, and bank; ask your day-of contact about a table.
- Hospitality: water is provided for all performers and crew.""",
    "requirements": "",   # venue-specific rule lines (optional)
}

VENUE_EMAIL = {
    "Fountain Square": {
        "location": "Fountain Square – Mainstage; 520 Vine St. Cincinnati, OH 45202",
        "load_in": """\
Load-In & Parking:
The load-in process at Fountain Square has changed — please review the attached document and acknowledge understanding on the form. Text or call your day-of contact when you're about 5 minutes out, and introduce yourself onsite as soon as you arrive.
Attached are QR codes that serve as your Fountain Square Garage validations (5 included). Each vehicle needs its own QR code before arriving; scan at the kiosk on entry or exit (please don't pay). Garage clearance is 6'8". Need more validations or large-vehicle parking? Note it on the form.""",
        "technical": """\
Technical:
- Backline / instrumentation: artists provide all instruments, including amps and 1/4" cables.
- Audio: we provide an engineer who mixes FOH and monitors from FOH. Coordinate in advance if you're bringing your own. All engineers mix within the 95 dBA-Slow ordinance; the FSQ engineer may baffle amps to reduce stage volume if needed.
- Lighting: we provide a house LD.
- Stage plot / input list, flat vs. drum riser, monitor count, and any scenic elements — all on the form.""",
        "hospitality": """\
Hospitality & Site:
- Merch: if you're selling, you provide the seller, point of sale, and bank; we provide a tent next to the stage with a table and chairs.
- Dressing rooms: no indoor rooms; on request we can provide a 10×10 tent with sidewalls for private band space.
- Hospitality: drink tickets and water are provided for all performers and crew.""",
        "requirements": "- Sound limit: strict 95 dBA-Slow at the FOH position, for all engineers (house or talent).",
    },
    # One generic block for all three WP locations (Brian, 2026-09-07) — {location}
    # and {stage_size} are filled per show by draft_emails.py; monitor count isn't
    # quoted here since it varies 6/2/4 by location and is already a hard cap on
    # the band form itself.
    "Washington Park": {
        "location": "Washington Park – {location}; 1230 Elm St, Cincinnati, OH 45202",
        "load_in": """\
Load-In & Parking:
Unload on Elm St., across from Memorial Hall, next to the park. This is 15-minute unloading only — the vehicle must be moved before going into sound check. Text or call your day-of contact when you're about 5 minutes out, and introduce yourself onsite as soon as you arrive.
Parking: we can validate parking if all band members are traveling in personal vehicles — larger vehicles are more difficult. Note your vehicle count and any large-vehicle needs on the form.""",
        "technical": """\
Technical:
- Stage: your footprint is {stage_size}.
- Backline / instrumentation: artists provide all instruments, including amps.
- Audio: we provide access to power, mics, monitor wedges, stands, cables, and a sound system, plus a house engineer who mixes FOH and monitors. Coordinate in advance if you're bringing your own.
- Stage plot / input list and monitor count — all on the form.""",
        "hospitality": """\
Hospitality & Site:
- Merch: if you're selling, you provide the seller, point of sale, and bank.
- Hospitality: drink tickets and water are provided for all performers — confirm your total headcount on the form.""",
        "requirements": "",
    },
    # Add Memorial Hall / etc. here as Brian supplies the content.
}

# Where Brian's per-series email content actually lives — see that folder's
# own README.md for the exact file format (## Location / Load-In / Technical
# / Hospitality / Requirements sections, only fill in what you want to
# override). One subfolder per venue, one .md file per series within it.
SERIES_EMAIL_ROOT = Path.home() / "Dropbox" / "Nyquist" / "Series Email Templates"

# Section-header aliases a series file's "## Heading" can use, matched after
# lowercasing and folding "&", "/", "-" to spaces — e.g. "Load-In & Parking"
# and "load in" both normalize to "load in" and hit load_in. Deliberately not
# exhaustive: an unrecognized header is skipped with a log line rather than
# guessed at, so a typo never silently drops content into the wrong block.
_BLOCK_HEADER_ALIASES = {
    "location": "location",
    "load in": "load_in",
    "load in parking": "load_in",
    "technical": "technical",
    "hospitality": "hospitality",
    "hospitality site": "hospitality",
    "requirements": "requirements",
    "performance requirements": "requirements",
    "schedule": "schedule",
    "day schedule": "schedule",
    "crew schedule": "crew_schedule",
}

# A "## Crew Schedule" section's lines are "Label: value" (unlike every
# other section, which is free text) — it fills the day-sheet DOCX's own
# small crew-schedule table (Crew Call / Load In-Sound Check / Performance /
# Load-out / Curfew, top-left of the advance), separate from the email's
# free-text "## Schedule" block. Only include the lines a series actually
# wants filled; leave one out (or the whole section) and daysheet.py leaves
# that row for a same-day hand call, same as always.
CREW_SCHEDULE_LABEL_ALIASES = {
    "crew call": "crew_call",
    "load in sound check": "load_in_soundcheck",
    "performance": "performance",
    "load out": "load_out",
    "curfew": "curfew",
}

# A "## Schedule" section is free text, same as every other section — it
# becomes the email's whole "Day Schedule:" block verbatim, not just a fill
# for the 5 generic fields. For a series with a fixed schedule that never
# changes (Brian, 2026-09-09: Salsa On The Square is the first) this is a
# hard override of what a staffer typed on the booking, not a blank-filler —
# see schedule_block_for().


def _norm_series(s):
    return re.sub(r"\s+", " ", (s or "").strip()).lower()


def norm_header(s):
    s = re.sub(r"[&/\-]+", " ", s.strip().lower())
    return re.sub(r"\s+", " ", s).strip().rstrip(":")


def _parse_series_email_file(text, label=""):
    """A series .md file's text -> {block_key: content}. See
    SERIES_EMAIL_ROOT's README for the section-header format."""
    blocks, current_key, buf = {}, None, []

    def commit():
        if not current_key:
            return
        # Trim blank lines off each edge (the blank line right after a "##
        # Header" and right before the next one) WITHOUT touching a real
        # line's own leading whitespace — a block like Schedule relies on
        # indentation to line up, and str.strip() on the joined text would
        # have eaten only the first line's indent, not the rest.
        lines = list(buf)
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        if lines:
            blocks[current_key] = "\n".join(lines)

    for line in text.splitlines():
        m = re.match(r"^#{1,3}\s+(.+?)\s*$", line)
        if not m:
            buf.append(line)
            continue
        commit()
        buf = []
        header = norm_header(m.group(1))
        key = _BLOCK_HEADER_ALIASES.get(header)
        if key is None:
            for alias, block_key in _BLOCK_HEADER_ALIASES.items():
                if header.startswith(alias + " "):
                    key = block_key
                    break
        if key is None:
            print(f"[venue_email] {label}: unrecognized section {m.group(1)!r}, skipped",
                  file=sys.stderr)
        current_key = key
    commit()
    return blocks


def _load_series_block(venue, series, root=None):
    """{block_key: content} for this exact venue + series, read fresh from
    <root>/<Venue>/<Series>.md — {} if the venue has no folder, no filename
    matches (case/whitespace-insensitive, since series is freeform text
    typed per booking), or the file can't be read. Never raises — a missing
    or malformed template just means that series renders the plain venue
    email, same as no series at all."""
    if not venue or not series:
        return {}
    vdir = (Path(root) if root else SERIES_EMAIL_ROOT) / venue.strip()
    if not vdir.is_dir():
        return {}
    target = _norm_series(series)
    for path in sorted(vdir.glob("*.md")):
        if _norm_series(path.stem) != target:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception as e:  # noqa: BLE001 — an unreadable template isn't fatal
            print(f"[venue_email] couldn't read {path}: {e!r}", file=sys.stderr)
            return {}
        return _parse_series_email_file(text, label=str(path))
    return {}


def schedule_block_for(venue, series, root=None):
    """The whole 'Day Schedule:' block, verbatim, for this venue + series —
    None if the series file has no Schedule section (or no series/file at
    all), meaning the generic per-show schedule fields apply as usual.
    Callers should let a non-None result WIN over whatever a booking's own
    schedule fields say — that's the point of a series whose schedule never
    changes (Brian, 2026-09-09: Salsa On The Square is the first)."""
    blocks = _load_series_block(venue, series, root)
    return blocks.get("schedule") or None


def crew_schedule_for(venue, series, root=None):
    """{crew_call, load_in_soundcheck, performance, load_out, curfew} (any
    subset) for this venue + series — fills the day-sheet DOCX's own small
    crew-schedule table (top-left of the advance) straight from a series'
    locked times, instead of leaving it blank for a same-day hand call
    (Brian, 2026-09-09: 'those never change' — same reasoning as the
    email's Schedule lock, applied to the document itself). {} if the
    series file has no Crew Schedule section.

    A value can be one line ('Load In/Sound Check: 6:00 PM - 7:00 PM') or,
    for a row that's really several sub-events (Performance covering
    several sets with breaks between them — Brian, 2026-09-09), several:
    put nothing after the label's colon and list the sub-lines below it,
    up to the next recognized label. daysheet.set_cell_lines() renders each
    line as its own paragraph in that cell."""
    blocks = _load_series_block(venue, series, root)
    raw = blocks.get("crew_schedule")
    if not raw:
        return {}
    out, current_key, buf = {}, None, []

    def commit():
        if not current_key:
            return
        lines = list(buf)
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        if lines:
            out[current_key] = "\n".join(lines)

    for line in raw.splitlines():
        label, sep, value = line.partition(":")
        key = CREW_SCHEDULE_LABEL_ALIASES.get(norm_header(label)) if sep else None
        if key:
            commit()
            current_key = key
            value = value.strip()
            buf = [value] if value else []
        elif current_key:
            buf.append(line)
    commit()
    return out


def locked_schedule_series(root=None):
    """Every series name (flat across all venues) that has a locked '##
    Schedule' section — used by the booking form to hide the schedule-time
    fields entirely for a series whose times are fixed in code, rather than
    silently accepting and ignoring whatever gets typed there (Brian,
    2026-09-09). Flat rather than venue-scoped: on the rare chance the same
    series name is ever locked at one venue and free at another, this errs
    toward hiding the fields — a UI nicety, not the actual enforcement
    (schedule_block_for stays properly venue-scoped and authoritative
    regardless of what the form shows). Never raises — a missing folder or
    an unreadable file just means nothing's reported as locked."""
    root = Path(root) if root else SERIES_EMAIL_ROOT
    out = set()
    if not root.is_dir():
        return []
    for vdir in root.iterdir():
        if not vdir.is_dir():
            continue
        for path in vdir.glob("*.md"):
            try:
                text = path.read_text(encoding="utf-8")
            except Exception:  # noqa: BLE001 — best-effort, skip a bad file
                continue
            if _parse_series_email_file(text, label=str(path)).get("schedule"):
                out.add(path.stem)
    return sorted(out)


def blocks_for(venue, series=None, **dynamic):
    v = VENUE_EMAIL.get((venue or "").strip(), {})
    out = dict(DEFAULT)
    out.update({k: val for k, val in v.items() if val is not None})
    if series:
        override = _load_series_block(venue, series)
        out.update({k: val for k, val in override.items() if val is not None})
    if dynamic:
        for k, text in out.items():
            if isinstance(text, str) and "{" in text:
                try:
                    out[k] = text.format(**dynamic)
                except (KeyError, IndexError):
                    pass  # a referenced placeholder wasn't supplied — leave as-is
    return out
