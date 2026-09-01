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


def get_config(series_key=None, venue=None):
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
    return cfg
