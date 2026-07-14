"""
engine.py — shared core: apply the EQ + reverb engines to a ShowSpec.

This is the part that runs on BOTH the Mac and the future Proxmox instance. It
fills every channel's computed EQ/comp/section/phantom, injects the Memo crowd
rig as documentation-only channels, and populates the reverb set. Nothing here
writes a .ses or a PDF — that's build.py (Mac only).
"""
from __future__ import annotations

import re

from .spec import Band, ReverbRec
from .eq_engine import compute_channel_eq
from .reverb_engine import suggest_reverbs

# mic-position / descriptor words to strip when finding a shared source name
_BLEND_STRIP = re.compile(
    r"\b(dynamic|dyn|condenser|cond|ribbon|mic|in|out|top|bottom|btm|close|far|"
    r"edge|cone|cap|amp|blend|sm\s*57|57|beta\s*27|27|r-?121|121|r-?10|md\s*421|421)\b",
    re.I)


def _source_stem(name: str) -> str:
    s = _BLEND_STRIP.sub(" ", (name or "").lower())
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


# engine-added blend guidance is prefixed with this sentinel (never typed by a
# user) so a rebuild strips the old text instead of doubling it
_BLEND_MARK = "§"
_BLEND_ENGINE = re.compile(r"\s*" + _BLEND_MARK + r".*$", re.S)


def _strip_blend(notes: str) -> str:
    """Remove any previously engine-appended blend guidance, leaving the user note."""
    return _BLEND_ENGINE.sub("", notes or "").strip()


def _mic_short(name: str) -> str:
    """Short label for blend notes: 'Shure SM57' -> 'SM57', 'Shure Beta 27' -> 'Beta 27'."""
    n = re.sub(r"^(shure|sennheiser|audix|neumann|royer|akg|warm audio|earthworks|"
               r"telefunken|line audio|deity|aea|radial|neve|bss|whirlwind|lauten|"
               r"audio-technica|schoeps)\s+", "", (name or "").strip(), flags=re.I)
    return n or name

SECTION_STAND = {
    "DRUMS": "Boom", "RHYTHM": "DI", "PIANO": "Clip", "STRINGS": "Clip",
    "HORNS": "Clip", "VOCALS": "Tall", "AMBIENT": "—", "SPARE": "—",
}


def apply_engines(kn, spec):
    """Mutate spec in place: fill each channel's EQ/comp + the reverb set."""
    for ch in spec.channels:
        if ch.is_crowd:
            continue  # crowd rig EQ is fixed (set at injection)
        if (ch.name or "").upper() == "SPARE" or ch.instrument in ("", "spare"):
            ch.section = "SPARE"
            ch.bands = []
            continue
        ikey = kn.match_instrument(ch.instrument) or kn.match_instrument(ch.name) or "di_generic"
        res = compute_channel_eq(
            kn, instrument_key=ikey, mic_name=ch.mic,
            genre_text=spec.genre, venue_key=spec.venue,
            eq_on=spec.eq_on, comp_on=spec.comp_on)
        ch.section = res["section"]
        ch.hpf = res["hpf"]
        ch.lpf = res["lpf"]
        ch.bands = res["bands"]
        ch.comp = res["comp"]
        ch.gate = res["gate"]
        ch.ribbon = res["ribbon"]
        # keep an explicitly-set phantom if the wizard already decided; else engine
        ch.phantom = res["phantom"] if ch.phantom in (None,) else (ch.phantom or res["phantom"])
        if res["ribbon"]:
            ch.phantom = False
        if not ch.mic_notes:
            ch.mic_notes = res["mic_notes"]
        ch.eq_summary = res["eq_summary"]
        if ch.stand in ("", "—", None):
            ch.stand = SECTION_STAND.get(ch.section, "—")

    apply_tom_voicing(kn, spec)
    apply_blends(kn, spec)

    reverbs, note = suggest_reverbs(kn, spec.genre, spec.venue)
    spec.reverbs = reverbs
    spec.reverb_note = note
    return spec


def apply_tom_voicing(kn, spec):
    """Multiple toms of the same type are different drums (a 10" vs a 13" rack),
    so they must not share one EQ. Spread each same-type group by pitch position
    — the highest-numbered/last tom sits lowest — by scaling its HPF + band
    centre frequencies. Stereo pairs (OH L/R) are untouched: only tom_rack /
    tom_floor are voiced. Mic-aware gains (set upstream) are preserved."""
    toms = []  # (channel, key)
    for ch in spec.channels:
        if ch.is_crowd or ch.ch is None:
            continue
        key = kn.match_instrument(ch.instrument) or kn.match_instrument(ch.name) or ""
        if key in ("tom_rack", "tom_floor"):
            toms.append((ch, key))
    if len(toms) < 2:
        return spec

    # racks (by channel) first, then floors (by channel): one high -> low series
    toms.sort(key=lambda ck: (0 if ck[1] == "tom_rack" else 1, ck[0].ch or 0))
    chans = [c for c, _ in toms]
    n = len(chans)
    facs = [1.12 + (0.90 - 1.12) * i / (n - 1) for i in range(n)]  # 1.12 high -> 0.90 low
    r5 = lambda x: int(round(x / 5.0) * 5)                          # tidy to nearest 5 Hz
    for idx, (ch, f) in enumerate(zip(chans, facs), start=1):
        if abs(f - 1.0) >= 1e-6:
            if ch.hpf:
                ch.hpf = r5(ch.hpf * f)
            for b in ch.bands:
                b.freq = r5(b.freq * f)
        pos = "highest" if idx == 1 else ("lowest" if idx == n else "mid")
        ch.eq_summary = _join(ch.eq_summary,
                              f"Tom {idx} of {n} ({pos}) — voiced in the high→low kit series.")
    return spec


def apply_blends(kn, spec):
    """Detect same-source multi-mic blends (two mics on one cab/source, e.g. a
    57/27 on a guitar amp) and post-process them as a single signal: the
    complement mic gets its overlapping low-mid/presence moves backed off so it
    doesn't stack on the primary, and both get polarity/bus/VCA guidance.

    A blend is two+ numbered channels in the same section whose names reduce to
    the same stem (mic-position words stripped) with different mics — exactly
    how Brian patches 'Guitar 1 Dynamic' + 'Guitar 1 Condenser'."""
    cfg = kn.eq.get("blends") or {}
    overlap = set(cfg.get("overlap_roles", []))
    cscale = cfg.get("complement_scale", 0.5)
    pairs = cfg.get("pairs", {})
    generic = cfg.get("generic", "")

    # idempotency: strip any blend guidance a previous build appended, so a
    # rebuild from a saved spec doesn't double (or stack) the notes
    for ch in spec.channels:
        if not ch.is_crowd:
            ch.notes = _strip_blend(ch.notes)

    groups = {}
    labels = {}
    for ch in spec.channels:
        if ch.is_crowd or ch.ch is None or ch.section == "SPARE":
            continue
        blob = f"{ch.name} {ch.notes}".lower()
        if "blend" in blob:
            # Brian flags both channels with a shared note like
            # "57/27 guitar mic blend Fender deluxe 65 amp" — group by that.
            src = _source_stem(ch.notes if "blend" in (ch.notes or "").lower() else ch.name)
            key = ("note", ch.section, src)
        else:
            src = _source_stem(ch.name)
            if not src:
                continue
            key = ("stem", ch.section, src)
        groups.setdefault(key, []).append(ch)
        labels[key] = src

    def mic_rank(ch):
        m = kn.match_mic(ch.mic) or {}
        t = m.get("type", "")
        # foundation first: a DI (clean lows, e.g. bass DI under a cab) is the
        # core, then the mid-forward dynamic, then condenser/ribbon complements
        return {"di": 0, "dynamic": 1, "condenser": 2, "ldc": 2, "lav": 2,
                "ribbon": 3}.get(t, 1)

    for key, chans in groups.items():
        section, stem = key[1], labels.get(key, "")
        if len(chans) < 2 or len({c.mic.lower() for c in chans if c.mic}) < 2:
            continue
        chans.sort(key=mic_rank)
        primary, *complements = chans
        pm = _mic_short(primary.mic)
        label = "/".join([pm] + [_mic_short(c.mic) for c in complements])
        src = _source_stem(primary.name) or stem or section.lower()

        # tailored guidance if this exact pair is documented, else generic
        guidance = generic
        if len(complements) == 1:
            a, b = primary.mic, complements[0].mic
            guidance = pairs.get(f"{a}|{b}") or pairs.get(f"{b}|{a}") or generic

        primary.notes = _join(primary.notes,
            f"{_BLEND_MARK} {label} blend on {src} — MID/PRESENCE core mic. "
            f"Treat the pair as ONE: pan together, same VCA, keep the blend constant. {guidance}")
        primary.eq_summary = _join(primary.eq_summary, f"Blend core ({label}).")

        for c in complements:
            # back off the bands that would stack on the primary's body/mids
            kept = []
            for bd in c.bands:
                # low-mid 150-800 Hz is the stack zone — back the complement off there
                if 150 <= bd.freq <= 800 and bd.gain != 0:
                    bd.gain = int(round(bd.gain * cscale))
                if bd.gain != 0:
                    kept.append(bd)
            c.bands = [Band(b=i + 1, gain=b.gain, freq=b.freq, q=b.q, type=b.type, deq=b.deq)
                       for i, b in enumerate(sorted(kept, key=lambda x: x.freq))]
            mt = (kn.match_mic(c.mic) or {}).get("type", "")
            role_word = {"ribbon": "WARMTH (tames the dynamic's top)",
                         "condenser": "BODY + TOP", "ldc": "BODY + TOP"}.get(mt, "COMPLEMENT")
            c.notes = _join(c.notes,
                f"{_BLEND_MARK} {label} blend — {role_word} to the {pm}; low-mids backed off so they "
                f"don't stack. Polarity: sum in mono, flip ⌀ on one mic if thinner. "
                f"Bus: notch -2/-3 dB @300-500 if it builds.")
            c.eq_summary = _join(c.eq_summary, f"Blend complement to {pm}.")
    return spec


def _join(existing, add):
    existing = (existing or "").strip()
    return f"{existing} {add}".strip() if existing else add


def inject_crowd_rig(kn, spec):
    """Append the venue crowd-mic rig as documentation-only channels (ch=None,
    fixed EQ). Memo always; others only if defined. Skips if already present."""
    venue = kn.venue(spec.venue) or {}
    rig = venue.get("crowd_rig") or []
    if not rig:
        return spec
    if any(c.is_crowd for c in spec.channels):
        return spec
    from .spec import Channel
    for entry in rig:
        bands = []
        for bnum, line in sorted(entry.get("bands", {}).items()):
            parts = [p.strip() for p in line.split("|")]
            bands.append(Band(b=int(bnum), gain=float(parts[0]), freq=float(parts[1]),
                              q=float(parts[2]), type=parts[3]))
        lpf = entry.get("lpf")
        lpf = None if (lpf in ("OFF", None)) else float(lpf)
        spec.channels.append(Channel(
            ch=None, name=entry["name"], instrument="crowd", mic=entry["mic"],
            section="AMBIENT", phantom=True, stand="—",
            notes="Crowd rig — fixed EQ, blank CH, set by hand on the console.",
            hpf=float(entry["hpf"]) if entry.get("hpf") else None, lpf=lpf,
            bands=bands, is_crowd=True,
            mic_notes=(kn.match_mic(entry["mic"]) or {}).get("notes", ""),
            eq_summary="Memo crowd rig — fixed EQ; documentation only (not written to the .ses)."))
    return spec
