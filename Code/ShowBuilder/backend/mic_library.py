"""
mic_library.py — mic picker support + "add a new mic" capture.

The wizard's mic field is populated from mics.json. If Brian types a mic that
isn't in the library, the spec records it under new_mics; on finalize these get
appended to mics.json AND queued for the mic-library KB article (harvest.py).
"""
from __future__ import annotations

import json
from pathlib import Path

KDIR = Path(__file__).resolve().parent.parent / "knowledge"
MICS = KDIR / "mics.json"

GUESS_TYPES = {
    "ribbon": ("ribbon",),
    "di": ("di", "d.i", "direct"),
    "condenser": ("condenser", "sdc", "pencil", "clip", "lav", "shotgun"),
    "ldc": ("ldc", "large diaphragm"),
    "dynamic": ("dynamic", "sm", "beta", "md", "e60", "e90"),
}


def guess_mic_record(name, type_hint="", phantom=None, ribbon=None, notes=""):
    """Build a mic dict from partial wizard input, guessing sane defaults."""
    t = (type_hint or "").lower().strip()
    mtype = None
    for canon, toks in GUESS_TYPES.items():
        if any(tok in t for tok in toks) or any(tok in name.lower() for tok in toks):
            mtype = canon
            break
    mtype = mtype or "dynamic"
    is_ribbon = ribbon if ribbon is not None else (mtype == "ribbon")
    if phantom is None:
        phantom = False if (is_ribbon or mtype == "dynamic") else True
    return {
        "name": name.strip(),
        "aka": [],
        "type": "ribbon" if is_ribbon else mtype,
        "phantom": bool(phantom) and not is_ribbon,
        "ribbon": bool(is_ribbon),
        "notes": notes.strip() or "Added via ShowBuilder — confirm specs.",
    }


def append_mics(new_mics):
    """Append new mic records to mics.json (skip ones already present). Returns
    the list actually added."""
    data = json.loads(MICS.read_text(encoding="utf-8"))
    existing = {m["name"].lower() for m in data["mics"]}
    for m in data["mics"]:
        existing.update(a.lower() for a in m.get("aka", []))
    added = []
    for nm in new_mics:
        rec = nm if isinstance(nm, dict) and "type" in nm else guess_mic_record(
            nm["name"] if isinstance(nm, dict) else str(nm),
            (nm.get("type_hint", "") if isinstance(nm, dict) else ""),
            (nm.get("phantom") if isinstance(nm, dict) else None),
            (nm.get("ribbon") if isinstance(nm, dict) else None),
            (nm.get("notes", "") if isinstance(nm, dict) else ""))
        if rec["name"].lower() in existing:
            continue
        data["mics"].append(rec)
        existing.add(rec["name"].lower())
        added.append(rec)
    if added:
        MICS.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return added
