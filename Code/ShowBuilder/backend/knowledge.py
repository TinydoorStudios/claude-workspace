"""
knowledge.py — load the curated knowledge layer and resolve paths.

The brain is sourced from the KB (reverb_presets.json is parsed from the wiki by
build_knowledge.py; venues/mics/eq_rules are curated from CLAUDE.md + the KB).
This module just loads them and exposes lookups for the engines and build.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KDIR = ROOT / "knowledge"


def _load(name):
    return json.loads((KDIR / name).read_text(encoding="utf-8"))


class Knowledge:
    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.venues = _load("venues.json")["venues"]
        self.mics_raw = _load("mics.json")["mics"]
        self.eq = _load("eq_rules.json")
        self.reverb = _load("reverb_presets.json")
        self._mic_index = self._build_mic_index()
        ar = self.config.get("audio_root")
        self.audio_root = Path(ar) if ar else None

    # ---- venues --------------------------------------------------------
    def venue(self, key):
        return self.venues.get(key)

    def venue_list(self):
        out = []
        for k, v in self.venues.items():
            out.append({"key": k, "name": v["name"], "short": v.get("short", k),
                        "console": v.get("console"), "console_label": v.get("console_label"),
                        "pipeline": v.get("pipeline", False), "outdoor": v.get("outdoor", False)})
        # memo + fsq first
        order = {"memo": 0, "fsq": 1}
        out.sort(key=lambda x: (order.get(x["key"], 9), x["name"]))
        return out

    def template_path(self, venue_key):
        v = self.venue(venue_key)
        if not v or not v.get("template") or not self.audio_root:
            return None
        return self.audio_root / v["template"]

    def patcher_path(self, venue_key):
        v = self.venue(venue_key)
        if not v or not v.get("patcher") or not self.audio_root:
            return None
        return self.audio_root / v["patcher"]

    def venue_defaults(self, venue_key):
        """The venue's strict starting patch template (names + best-guess
        instrument), so the wizard can pre-fill rows. Mics are left blank — the
        engineer assigns them per show; un-mic'd rows are skipped at build."""
        v = self.venue(venue_key) or {}
        names = v.get("default_channels") or []
        chans = []
        for i, nm in enumerate(names, 1):
            ik = self.match_instrument(nm)
            inst = self.instrument(ik) if ik else None
            chans.append({"ch": i, "name": nm,
                          "instrument": inst["label"] if inst else "",
                          "section": inst["section"] if inst else ""})
        count = v.get("default_channel_count") or (len(names) or None)
        return {"count": count, "channels": chans}

    def show_folder(self, venue_key, folder_name):
        v = self.venue(venue_key)
        if not v or not self.audio_root:
            return None
        return self.audio_root / v["folder"] / folder_name

    # ---- mics ----------------------------------------------------------
    def _build_mic_index(self):
        idx = {}
        for m in self.mics_raw:
            keys = [m["name"]] + m.get("aka", [])
            for k in keys:
                idx[k.lower().strip()] = m
        return idx

    def match_mic(self, text):
        """Return the mic dict for a name/shorthand, or None."""
        if not text:
            return None
        t = text.lower().strip()
        if t in self._mic_index:
            return self._mic_index[t]
        # substring fallback: longest alias contained in the text
        best = None
        for key, m in self._mic_index.items():
            if key and key in t and (best is None or len(key) > len(best[0])):
                best = (key, m)
        return best[1] if best else None

    def mic_options(self):
        """For the picker, grouped by type."""
        out = []
        for m in self.mics_raw:
            out.append({"name": m["name"], "type": m["type"],
                        "phantom": m["phantom"], "ribbon": m["ribbon"],
                        "notes": m.get("notes", "")})
        return out

    # ---- instruments ---------------------------------------------------
    def instrument_keys(self):
        return list(self.eq["instruments"].keys())

    def instrument(self, key):
        return self.eq["instruments"].get(key)

    def match_instrument(self, text):
        """Map free text / console name to an instrument key."""
        if not text:
            return None
        t = text.lower().strip()
        insts = self.eq["instruments"]
        if t in insts:
            return t
        aliases = self.eq["instrument_aliases"]
        if t in aliases:
            return aliases[t]
        # strip trailing L/R/numbers e.g. "GTR 1" -> "gtr"
        import re
        t2 = re.sub(r"\s*[lr0-9]+\s*$", "", t).strip()
        if t2 in aliases:
            return aliases[t2]
        if t2 in insts:
            return t2
        # token containment
        best = None
        for alias, key in aliases.items():
            if alias in t and (best is None or len(alias) > len(best[0])):
                best = (alias, key)
        return best[1] if best else None

    def instrument_options(self):
        out = []
        for key, v in self.eq["instruments"].items():
            if key == "spare":
                continue
            out.append({"key": key, "label": v["label"], "section": v["section"],
                        "default_mic": v.get("default_mic", "")})
        return out

    # ---- genres --------------------------------------------------------
    def genres(self):
        return self.eq["genres"]

    def match_genre(self, text):
        """Map a free-text genre to a genre rule key (default 'rock' = aggressive)."""
        if not text:
            return "rock"
        t = text.lower().strip()
        genres = self.eq["genres"]
        if t in genres:
            return t
        for key, g in genres.items():
            for a in g.get("aliases", []):
                if a in t or t in a:
                    return key
        return "rock"

    def genre_rule(self, text):
        return self.eq["genres"][self.match_genre(text)]
