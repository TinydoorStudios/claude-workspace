"""Form versioning config.

One form engine, many variants. The public form reads optional ?venue= and
?series= params; this module decides which venue is preselected and which
optional question blocks / intro copy apply. Right now every series shares the
base question set — add per-series overrides here as they come up, without
touching the template beyond the {% if cfg... %} hooks already in form.html.

Language (?lang=es) is a separate axis handled by i18n.py/app.py — every
label, help string, and option on the form comes from there regardless of
series. The one thing THIS module owns that's language-sensitive is a
series's `intro` subtitle: get_config's `lang` param picks `intro_es` off a
series override when present, else falls back to i18n's generic default
intro for that language. Add `intro_es` next to a series's own `intro` if
you want a custom Spanish subtitle for it; otherwise the generic one is
used and is always grammatically correct regardless of what intro a series
sets in English.
"""
import i18n

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
            "backline": True,
            "stage_escort": False,
        },
    },
    # Salsa On The Square (Brian, 2026-09-12): a house band situation, not a
    # touring act bringing its own rig — no backline-sharing question (there's
    # no other artist on the bill to share with) and no scenic-elements
    # question. This is also 3CDC's one BILINGUAL series (see
    # venue_email.BILINGUAL_SERIES) — draft_emails.py sends its advance email
    # English-then-Spanish in one message with two form links, and this
    # series's own email content override
    # (~/Dropbox/Nyquist/Series Email Templates/Fountain Square/Salsa On The
    # Square.md) carries matching "(Español)" sections alongside its English
    # ones for exactly that reason.
    "Salsa On The Square": {
        "blocks": {
            "backline": False,
            "scenic": False,
            # audit #15: named stage-escort rep, identified to on-site staff
            "stage_escort": True,
        },
        # audit #15: no drum risers for this series — never ask flat/riser;
        # the advance doc's Stage Type defaults to Flat.
        "drum_riser": False,
    },
    # Example of a leaner variant — a small acoustic series that skips riser/parking:
    # "acoustic": {
    #     "label": "Acoustic Series",
    #     "intro": "A few quick details for your acoustic set.",
    #     "blocks": {"merch": True, "band_tent": False,
    #                "large_vehicle": False, "lighting": True, "scenic": False},
    # },
}


def get_config(series_key=None, venue=None, location=None, lang="en"):
    base = dict(SERIES["default"])
    cfg = dict(base)
    cfg["intro"] = i18n.t("intro_default", lang)
    if series_key and series_key in SERIES:
        override = SERIES[series_key]
        cfg["label"] = override.get("label", base["label"])
        # A series's own `intro` (English) only applies for lang='en' — an
        # `intro_es` override on the series wins for Spanish; absent that,
        # the generic translated default applies rather than showing the
        # series's English intro untranslated.
        if lang == "es":
            if "intro_es" in override:
                cfg["intro"] = override["intro_es"]
        elif "intro" in override:
            cfg["intro"] = override["intro"]
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

    if series_key and SERIES.get(series_key, {}).get("drum_riser") is False:
        cfg["drum_riser_available"] = False

    # Fountain Square used to ask only the headliner about a drum riser and
    # hide the question from the opener and direct support (Brian, 2026-09-11).
    # That went out with the slots on 2026-09-15: every artist is asked, and the
    # option says "if available" instead — hiding it meant the earlier acts'
    # preference existed nowhere and turned up at load-in. A venue or series
    # with no riser at all (WP Porch/Bandstand, see above) still hides it.

    return cfg
