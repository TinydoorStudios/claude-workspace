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
    # WP copy adapted from the Fountain Square block (Brian, 2026-09-11): FSQ→WP
    # wording, the "load-in process has changed / review attached doc" section
    # removed, and the garage-QR-code paragraph replaced with the validations
    # follow-up line. {location} is filled per show; {lighting_line} and
    # {riser_phrase} are set by draft_emails.py and are EMPTY for Porch/Bandstand
    # — lighting and a drum riser exist only at the Main Stage, so those shows
    # must mention neither.
    "Washington Park": {
        "location": "Washington Park – {location}; 1230 Elm St, Cincinnati, OH 45202",
        "load_in": """\
Load-In & Parking:
Text or call your day-of contact when you're about 5 minutes out, and introduce yourself onsite as soon as you arrive.
We will follow-up with parking validations.""",
        "technical": """\
Technical:
- Backline / instrumentation: artists provide all instruments, including amps and 1/4" cables.
- Audio: we provide an engineer who mixes FOH and monitors from FOH. Coordinate in advance if you're bringing your own. All engineers mix within the 95 dBA-Slow ordinance; the Washington Park engineer may baffle amps to reduce stage volume if needed.{lighting_line}
- Stage plot / input list, {riser_phrase}monitor count, and any scenic elements — all on the form.""",
        "hospitality": """\
Hospitality & Site:
- Merch: if you're selling, you provide the seller, point of sale, and bank; we provide a tent next to the stage with a table and chairs.
- Dressing rooms: no indoor rooms; on request we can provide a 10×10 tent with sidewalls for private band space.
- Hospitality: drink tickets and water are provided for all performers and crew.""",
        "requirements": "- Sound limit: strict 95 dBA-Slow at the FOH position, for all engineers (house or talent).",
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
    email, same as no series at all.

    Exact match wins; failing that, a PREFIX match (2026-09-12, for 513
    Airwaves) — some recurring series get the week's guest act appended
    right into the `series` field itself ('513 Airwaves w/ Inhaler Radio'
    one week, a different act the next), so a file named '513 Airwaves.md'
    matches any series value that starts with '513 airwaves '. Longest
    matching stem wins if more than one file could prefix-match."""
    if not venue or not series:
        return {}
    vdir = (Path(root) if root else SERIES_EMAIL_ROOT) / venue.strip()
    if not vdir.is_dir():
        return {}
    target = _norm_series(series)
    best_prefix = None
    for path in sorted(vdir.glob("*.md")):
        stem = _norm_series(path.stem)
        if stem == target:
            best_prefix = path
            break
        if target.startswith(stem + " ") and (best_prefix is None or
                len(stem) > len(_norm_series(best_prefix.stem))):
            best_prefix = path
    for path in ([best_prefix] if best_prefix else []):
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
    """[(label, time), ...] in file order for this venue + series' locked
    crew schedule — the day-sheet DOCX's own small crew table (top-left of
    the advance, normally Crew Call / Load In-Sound Check / Performance /
    Load-out / Curfew) gets its rows REPLACED wholesale with exactly this
    list when present, one row per entry, instead of trying to cram a
    multi-set series into the template's default 5 rows (Brian, 2026-09-09:
    'each time change should have its own cell in the table' — a prior cut
    that crammed Salsa On The Square's 3 sets + 2 breaks into one
    Performance cell as multiple lines wasn't readable enough). [] if the
    series file has no Crew Schedule section.

    Each non-blank line is 'Label: time' — the label becomes that row's
    right-hand cell, the time (which may be blank, e.g. 'Crew Call:' with
    nothing after it — the row still appears, just unfilled, same as any
    other show) becomes the left-hand cell. Labels are whatever the file
    says, not constrained to the template's original 5 names — write
    'Set #1', 'Dance Instruction #1', etc. and daysheet.py builds exactly
    that many rows."""
    blocks = _load_series_block(venue, series, root)
    raw = blocks.get("crew_schedule")
    if not raw:
        return []
    out = []
    for line in raw.splitlines():
        if ":" not in line:
            continue
        label, _, value = line.partition(":")
        label = label.strip()
        if label:
            out.append((label, value.strip()))
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


class _SafeDict(dict):
    """str.format_map backing that renders an unsupplied placeholder as '' rather
    than raising — so one missing key can't turn a whole block into literal braces."""
    def __missing__(self, key):
        return ""


def blocks_for(venue, series=None, **dynamic):
    v = VENUE_EMAIL.get((venue or "").strip(), {})
    out = dict(DEFAULT)
    out.update({k: val for k, val in v.items() if val is not None})
    if series:
        override = _load_series_block(venue, series)
        out.update({k: val for k, val in override.items() if val is not None})
    if dynamic:
        safe = _SafeDict(dynamic)
        for k, text in out.items():
            if isinstance(text, str) and "{" in text:
                try:
                    # format_map with a blank-defaulting dict: a missing
                    # placeholder renders empty instead of leaving the WHOLE
                    # block's {braces} literal in the email (Brian, 2026-09-11).
                    out[k] = text.format_map(safe)
                except (IndexError, ValueError):
                    pass  # positional/malformed braces — leave as-is
    return out
