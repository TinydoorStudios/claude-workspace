"""
reverb_engine.py — pick 4-6 Seventh Heaven Pro presets for genre x venue.

Memo: use the KB's by-genre Memo selections, pull decay to the working target,
cut VLF, Early MAX / Late pulled down. FSQ: short/bright, Late higher, default
note that most outdoor shows take no send. Post/other indoor: near factory.

Names and numbers are verbatim from the KB library — never invented.
"""
from __future__ import annotations

import re
from .spec import ReverbRec

VLF_TARGET = {"classical": "-20dB", "celtic": "-15dB", "acoustic": "-15dB",
              "jazz": "-15dB", "gospel": "-12dB", "rock": "-12dB"}
LATEROLL = {"classical": "4-5kHz", "celtic": "5-6kHz", "acoustic": "5-6kHz",
            "jazz": "6-9kHz", "gospel": "8-10kHz", "rock": "6-9kHz"}


def _first_num(s):
    m = re.search(r"-?\d+(?:\.\d+)?", s or "")
    return float(m.group()) if m else None


def _late_db(use):
    u = (use or "").lower()
    if "vocal" in u or "vox" in u:
        return "Max Early · Late -12dB"
    if any(w in u for w in ("snare", "drum", "kick", "bodhran", "perc")):
        return "Max Early · Late -16dB"
    if any(w in u for w in ("hall", "choir", "main", "ensemble", "orchestral")):
        return "Max Early · Late -10dB"
    return "Max Early · Late -14dB"


def _factory_preset(kn, bank, num):
    for b in kn.reverb["banks"]:
        if b["bank"].lower() == bank.lower():
            for p in b["presets"]:
                if p["num"] == num.zfill(2):
                    return p
    return None


def suggest_reverbs(kn, genre_text, venue_key, max_n=6):
    """Return (list[ReverbRec], context_note)."""
    gkey = kn.match_genre(genre_text)
    venue = kn.venue(venue_key) or {}
    profile = venue.get("reverb_profile", "post")
    recs = []

    if profile == "fsq":
        note = ("FSQ is outdoors — default is no reverb send; the open air gives "
                "nothing back and wash competes with building reflections. Use only "
                "when the show calls for it. When used: short, bright, Late higher.")
        # curated short/bright outdoor picks
        picks = [("Plates 1", "06", "vocal — short, forward"),
                 ("Rooms 1", "02", "drum bus / instruments — tight"),
                 ("Plates 1", "17", "small bright plate for snare/inst"),
                 ("Halls 1", "03", "subtle size if a tail is wanted")]
        for bank, num, use in picks:
            p = _factory_preset(kn, bank, num)
            if not p:
                continue
            recs.append(ReverbRec(
                bank=bank, num=p["num"], name=p["name"],
                decay_s=p["decay_s"], predelay_ms=p["predelay_ms"],
                vlf="near factory", early_late="Max Early · Late Equal to -6dB",
                late_rolloff="8-10kHz", use=use,
                rationale=f"FSQ: {use}. Decay near factory (no room to subtract)."))
        return recs[:max_n], note

    if profile == "memo":
        note = ("Memo: pull factory decay 30-40% (room adds ~1.6s), cut VLF hard, "
                "Early MAX with Late pulled down. 100% wet on a dedicated return.")
        rows = kn.reverb["by_genre_memo"].get(gkey, [])
        for r in rows[:max_n]:
            p = _factory_preset(kn, r["bank"], r["num"])
            decay = _first_num(r.get("memo_target")) or (p["decay_s"] if p else None)
            recs.append(ReverbRec(
                bank=r["bank"], num=r["num"], name=r["name"],
                decay_s=decay,
                predelay_ms=(p["predelay_ms"] if p else None),
                vlf=VLF_TARGET.get(gkey, "-15dB"),
                early_late=_late_db(r.get("use")),
                late_rolloff=LATEROLL.get(gkey, "6-9kHz"),
                use=r.get("use", ""),
                rationale=f"{r.get('use','')} — {r.get('notes','')}".strip(" -")))
        return recs[:max_n], note

    # post / other indoor: near factory
    note = ("Indoor (no calibrated room profile): start near factory decay and "
            "tune to the mix. VLF to taste. 100% wet on a return.")
    rows = kn.reverb["by_genre_memo"].get(gkey, [])
    for r in rows[:max_n]:
        p = _factory_preset(kn, r["bank"], r["num"])
        recs.append(ReverbRec(
            bank=r["bank"], num=r["num"], name=r["name"],
            decay_s=(p["decay_s"] if p else _first_num(r.get("factory"))),
            predelay_ms=(p["predelay_ms"] if p else None),
            vlf="to taste", early_late="Max Early · Late Equal",
            late_rolloff=LATEROLL.get(gkey, "6-9kHz"),
            use=r.get("use", ""),
            rationale=f"{r.get('use','')} — near factory, tune to the mix.".strip(" -")))
    return recs[:max_n], note
