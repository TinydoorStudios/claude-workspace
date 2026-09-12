"""Form versioning config.

One form engine, many variants. The public form reads optional ?venue= and
?series= params; this module decides which venue is preselected and which
optional question blocks / intro copy apply. Right now every series shares the
base question set — add per-series overrides here as they come up, without
touching the template beyond the {% if cfg... %} hooks already in form.html.
"""

VENUES = [
    "Fountain Square", "Washington Park", "Elm Street Plaza",
    "Court Street Plaza", "Zeigler Park", "Imagination Alley",
]

# Per-venue "tech pack" — a link (PDF or page) showing what 3CDC provides at that
# venue: PA, consoles, monitors, mic inventory, backline, stage size. Best practice
# is to show bands this up front to cut back-and-forth. Fill in a URL per venue and
# the form surfaces a "what we provide" link for the selected venue; leave blank and
# nothing shows. Brian to supply the actual links/PDFs.
TECH_PACKS = {
    "Fountain Square": "",
    "Washington Park": "",
    "Elm Street Plaza": "",
    "Court Street Plaza": "",
    "Zeigler Park": "",
    "Imagination Alley": "",
}


def tech_packs():
    """Only the venues that actually have a link configured."""
    return {v: u for v, u in TECH_PACKS.items() if u}

# WP-only sub-venues (Brian, 2026-09-06). Each has its own monitor cap; Porch
# and Bandstand have no lighting rig at all, so the lighting-request question
# doesn't apply there. Main Stage behaves like every other venue (lighting on,
# generous monitor count) — it's listed mainly so the location itself can be
# selected and printed on the day-sheet.
# stage_size (added 2026-09-07, Brian): footprint quoted to bands in the advance
# email (tools/venue_email.py). Porch + Main Stage are Brian-confirmed; Bandstand
# has no published dimensions anywhere online — TBD until he measures/confirms it.
# drum_riser (added 2026-09-09, Brian): only Main Stage has one available —
# Porch and Bandstand don't, so the "flat stage or drum riser?" question
# doesn't apply there either, same treatment as lighting.
# band_tent (added 2026-09-09, Brian): the private band-tent/dressing-space
# question doesn't apply at the Porch specifically — unlike lighting/drum
# riser, Bandstand keeps it (only Porch is out).
WP_LOCATIONS = {
    "Main Stage": {"monitor_cap": 6, "lighting": True, "drum_riser": True,
                   "band_tent": True, "stage_size": "20' wide x 20' deep"},
    "Porch":      {"monitor_cap": 2, "lighting": False, "drum_riser": False,
                   "band_tent": False, "stage_size": "20' wide x 12' deep"},
    "Bandstand":  {"monitor_cap": 4, "lighting": False, "drum_riser": False,
                   "band_tent": True,
                   "stage_size": "TBD — confirm with your day-of contact"},
}

# Each WP series plays a fixed stage (Brian, 2026-09-11): Neo Soul on the
# Bandstand, Blues & Brews on the Porch. This is the AUTHORITATIVE source of a
# booking's WP location — the per-show/booking location can be blank (it lives
# on the event, not always the show), so the series is what reliably drives the
# monitor cap and which questions (lighting, drum riser, band tent) are hidden.
# Add a WP series here to bind it to a stage.
SERIES_LOCATION = {
    "Neo Soul Nights": "Bandstand",
    "Blues & Brews": "Porch",
}

# Show series -> overrides. `blocks` toggles optional sections; `intro` overrides
# the header subtitle; `label` is the human name. Extend freely.
SERIES = {
    "default": {
        "label": "",
        "intro": "Please complete this so we have everything we need to run your show.",
        "blocks": {
            "merch": True,
            "band_tent": True,
            "large_vehicle": True,
            "lighting": True,
            "scenic": True,
        },
    },
    # Example of a leaner variant — a small acoustic series that skips riser/parking:
    # "acoustic": {
    #     "label": "Acoustic Series",
    #     "intro": "A few quick details for your acoustic set.",
    #     "blocks": {"merch": True, "band_tent": False,
    #                "large_vehicle": False, "lighting": True, "scenic": False},
    # },
}


def get_config(series_key=None, venue=None, location=None, slot=None):
    base = dict(SERIES["default"])
    cfg = dict(base)
    if series_key and series_key in SERIES:
        override = SERIES[series_key]
        cfg["label"] = override.get("label", base["label"])
        cfg["intro"] = override.get("intro", base["intro"])
        merged = dict(base["blocks"])
        merged.update(override.get("blocks", {}))
        cfg["blocks"] = merged
    cfg["venue_preselect"] = venue if venue in VENUES else None
    cfg["series_key"] = series_key or "default"

    # WP sub-venue: monitor cap + (Porch/Bandstand) no lighting, no drum riser,
    # (Porch only) no band tent
    cfg["location"] = None
    cfg["monitor_cap"] = None
    cfg["drum_riser_available"] = True  # every non-WP venue keeps the question
    # WP location is fixed by the series — fall back to it whenever the caller
    # didn't pass a concrete WP location (e.g. a prefill token whose location is
    # blank), so the form still hides the right questions and applies the right
    # monitor cap (Brian, 2026-09-11).
    if venue == "Washington Park" and location not in WP_LOCATIONS:
        location = SERIES_LOCATION.get((series_key or "").strip(), location)
    if venue == "Washington Park" and location in WP_LOCATIONS:
        loc = WP_LOCATIONS[location]
        cfg["location"] = location
        cfg["monitor_cap"] = loc["monitor_cap"]
        cfg["blocks"] = dict(cfg["blocks"])
        cfg["blocks"]["lighting"] = loc["lighting"]
        cfg["blocks"]["band_tent"] = loc["band_tent"]
        cfg["drum_riser_available"] = loc["drum_riser"]

    # Fountain Square: only the headliner is asked about a drum riser — an
    # opener or direct-support act has no riser call of its own, so hide the
    # question on their form (Brian, 2026-09-11).
    if venue == "Fountain Square" and (slot or "").strip().lower() in ("opener", "direct_support"):
        cfg["drum_riser_available"] = False

    return cfg
