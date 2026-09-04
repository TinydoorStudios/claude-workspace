#!/usr/bin/env python3
"""Per-venue advance-email content blocks.

The advance email's body is venue-specific — Fountain Square's garage QR codes and
95 dBA-Slow ordinance have no business in a Washington Park or Memorial Hall email. This
keeps one email skeleton (greeting, form link, schedule, common rules) and swaps the
venue-specific blocks: location, load-in/parking, technical, hospitality, and any
venue-only performance rules.

To add a venue: copy the FSQ dict, replace the prose. Anything you leave out falls
back to DEFAULT (a generic, non-FSQ-specific block that is safe to send as-is).
COMMON_REQUIREMENTS is the 3CDC-wide policy and appends to every venue.
"""

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
    # Add Washington Park / Memorial Hall / etc. here as Brian supplies the content.
}


def blocks_for(venue):
    v = VENUE_EMAIL.get((venue or "").strip(), {})
    out = dict(DEFAULT)
    out.update({k: val for k, val in v.items() if val is not None})
    return out
