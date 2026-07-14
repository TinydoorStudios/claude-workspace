"""
eq_engine.py — compose per-channel EQ from instrument x genre x venue x mic.

Start from the instrument template (Brian's documented starting points), then
layer the genre flags (aggressive vs conservative vs cuts-only), the venue
(Memo problem zones + DEQ; FSQ outdoor softening), and the mic (ribbon = no 48V,
clip-on = lighter hand, piezo DI = guarantee the 1.5-2kHz quack cut). Output is
the locked B1(low)..B4(high) band set + HPF/LPF, whole-dB only.

Comp/gate are produced as packet guidance only — the .ses patcher leaves comp
and gate unwritten (hard constraint from the send-it pipeline).
"""
from __future__ import annotations

import copy
from .spec import Band

CLIP_ON = ("DPA 4099", "Countryman B3", "DPA 4099 CORE+")
MEMO_PROBLEM = (180, 360)   # ensure a cut lands here at Memo


def _round_whole(x):
    return int(round(x))


def _deq_for(role, section, instrument_key):
    thr, atk, rel = -16, 8, 80
    if instrument_key in ("pipes", "flute") or section == "HORNS":
        atk, rel = 10, 110          # sustained / drone — extended release
    elif section == "VOCALS":
        thr, atk, rel = -16, 10, 80
    elif instrument_key in ("tom_rack", "tom_floor", "bodhran"):
        rel = 100
    return {"thr": thr, "atk_ms": atk, "rel_ms": rel}


def compute_channel_eq(kn, *, instrument_key, mic_name, genre_text, venue_key,
                       eq_on=True, comp_on=False):
    """Return a dict of computed channel fields."""
    inst = kn.instrument(instrument_key) or kn.instrument("di_generic")
    genre = kn.genre_rule(genre_text)
    venue = kn.venue(venue_key) or {}
    mic = kn.match_mic(mic_name)

    section = inst["section"]
    result = {
        "section": section,
        "hpf": inst.get("hpf"),
        "lpf": inst.get("lpf"),
        "bands": [],
        "comp": None,
        "gate": False,
        "ribbon": bool(mic and mic.get("ribbon")),
        "phantom": bool(mic and mic.get("phantom")) and not (mic and mic.get("ribbon")),
        "mic_notes": (mic or {}).get("notes", ""),
        "eq_summary": inst.get("summary", ""),
    }

    if not eq_on or not inst.get("bands"):
        # still set comp/gate guidance + summary even with EQ off
        result["bands"] = []
    else:
        moves = copy.deepcopy(inst["bands"])

        # --- mic character: back off template moves the mic already delivers
        #     (soften: role->factor) and add the mic's known problem cuts
        #     (tame). This is why two mics on the same source differ — e.g. an
        #     Audix D6 is pre-scooped so its mud/box/attack moves shrink, while
        #     a flat Beta 91A keeps the full kick shaping plus a box tame. ---
        mic_eq = (mic or {}).get("eq") or {}
        soften = mic_eq.get("soften") or {}
        for mv in moves:
            fac = soften.get(mv.get("role"))
            if fac is not None:
                mv["gain"] = mv["gain"] * fac
        for t in (mic_eq.get("tame") or []):
            moves.append({"freq": t["freq"], "gain": t["gain"],
                          "q": t.get("q", 1.5), "type": t.get("type", "BELL"),
                          "role": t.get("role", "mic")})

        # --- mic scaling: clip-on mics are designed for the instrument ---
        mic_scale = 1.0
        if mic and (mic["name"] in CLIP_ON or mic.get("type") == "lav"):
            mic_scale = 0.7

        # --- venue EQ scaling: a venue may soften OR sharpen the hand.
        #     eq_cut_scale / eq_boost_scale from venues.json win; else outdoor
        #     softens (0.8), indoor is neutral (1.0). FSQ sets >1.0 to run
        #     aggressive for an outdoor PA fighting ambient noise. ---
        if venue.get("eq_cut_scale") is not None:
            venue_cut_scale = venue["eq_cut_scale"]
        else:
            venue_cut_scale = 0.8 if venue.get("outdoor") else 1.0
        venue_boost_scale = venue.get("eq_boost_scale", 1.0)
        memo = (venue_key == "memo") or (venue.get("reverb_profile") == "memo")

        kept = []
        for mv in moves:
            gain = mv["gain"]
            if gain < 0:  # cut
                gain = gain * genre["cut_scale"] * venue_cut_scale * mic_scale
            else:         # boost
                gain = gain * mic_scale * venue_boost_scale
                if genre["cuts_only"] or genre["boost_cap"] == 0:
                    continue  # drop boosts entirely
                if section == "VOCALS":
                    continue  # vocals are CUT-ONLY across every genre (Brian's standing rule)
                gain = min(gain, genre["boost_cap"])
            g = _round_whole(gain)
            if g == 0:
                continue
            mv["gain"] = g
            # DEQ only at Memo, only on flagged bands
            if memo and mv.get("deq_memo"):
                mv["_deq"] = _deq_for(mv.get("role"), section, instrument_key)
            kept.append(mv)

        # --- Memo guarantee: a cut in the problem zone for live sources ---
        if memo and section in ("DRUMS", "RHYTHM", "VOCALS", "HORNS") \
                and instrument_key not in ("click", "video"):
            in_zone = any(MEMO_PROBLEM[0] <= m["freq"] <= MEMO_PROBLEM[1]
                          and m["gain"] < 0 for m in kept)
            if not in_zone and len(kept) < 4:
                kept.append({"freq": 250, "gain": -4, "q": 2.0, "type": "BELL",
                             "role": "mud", "_deq": _deq_for("mud", section, instrument_key)})

        # --- dedupe near-identical freqs (mic tame can collide with a template
        #     band), keep the stronger; then at most 4 bands, sort low->high ---
        kept.sort(key=lambda m: abs(m["gain"]), reverse=True)
        deduped = []
        for m in kept:
            if any(0.92 <= m["freq"] / k["freq"] <= 1.08 for k in deduped):
                continue
            deduped.append(m)
        kept = deduped[:4]
        kept.sort(key=lambda m: m["freq"])
        for i, mv in enumerate(kept, start=1):
            deq = mv.get("_deq")
            result["bands"].append(Band(b=i, gain=mv["gain"], freq=mv["freq"],
                                        q=mv["q"], type=mv["type"], deq=deq))

    # --- comp / gate guidance (packet only) ---
    if comp_on and inst.get("comp"):
        comp = dict(inst["comp"])
        comp["atk_ms"] = max(comp["atk_ms"], genre["comp_attack_min_ms"])
        result["comp"] = comp
    sustained = section in ("STRINGS", "HORNS") or instrument_key in (
        "pipes", "flute", "violin", "viola", "cello", "vocal_lead", "vocal_bg")
    result["gate"] = bool(inst.get("gate")) and (genre["gate_sustained"] or not sustained)

    # --- summary line: genre + venue context ---
    extras = [genre.get("note", "")]
    if result["ribbon"]:
        extras.append("RIBBON — NO 48V.")
    if venue_key == "fsq":
        extras.append("FSQ: aggressive cuts for the outdoor PA; no room DEQ; vocals cut-only.")
    result["eq_summary"] = " ".join(x for x in [inst.get("summary", "")] + extras if x).strip()
    return result
