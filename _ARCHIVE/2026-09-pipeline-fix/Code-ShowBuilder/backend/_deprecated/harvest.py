"""
harvest.py — the self-improvement loop.

On finalize: capture new mics into the library, log the show's EQ/reverb choices
(so future runs can learn kept-vs-changed), and return KB write-back suggestions
following NEW-SHOW.md step 6. The actual wiki edits + push run through the
wiki-publish / fsq-wiki-push skill on the Mac — harvest stages the suggestions
rather than editing the live KB blindly.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from .mic_library import append_mics

ROOT = Path(__file__).resolve().parent.parent
LEARN = ROOT / "learning"


def harvest_show(kn, spec, result):
    LEARN.mkdir(exist_ok=True)
    out = {"new_mics_added": [], "kb_suggestions": [], "learning_log": ""}

    # 1. new mics -> library + KB suggestion
    if spec.new_mics:
        added = append_mics(spec.new_mics)
        out["new_mics_added"] = [m["name"] for m in added]
        for m in added:
            out["kb_suggestions"].append(
                f"mic-library: add **{m['name']}** ({m['type']}"
                f"{', NO 48V' if m['ribbon'] else ''}) — {m['notes']}")

    # 2. learning log (kept-vs-changed baseline)
    log = {
        "date": date.today().isoformat(),
        "show": spec.show_name, "venue": spec.venue, "genre": spec.genre,
        "eq_on": spec.eq_on, "comp_on": spec.comp_on,
        "channels": [{"ch": c.ch, "name": c.name, "instrument": c.instrument,
                      "mic": c.mic, "hpf": c.hpf, "lpf": c.lpf,
                      "bands": [{"b": b.b, "gain": b.gain, "freq": b.freq,
                                 "q": b.q, "type": b.type, "deq": bool(b.deq)}
                                for b in c.bands]}
                     for c in spec.channels if not c.is_crowd],
        "reverbs": [{"bank": r.bank, "num": r.num, "name": r.name} for r in spec.reverbs],
        "ses_ok": result.get("ses_ok"),
    }
    slug = spec.slug()
    lp = LEARN / f"{log['date']}_{slug}.json"
    lp.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
    out["learning_log"] = str(lp)

    idx = LEARN / "INDEX.md"
    line = (f"- {log['date']} · {spec.show_name} · {spec.venue} · {spec.genre} · "
            f"{len(log['channels'])} ch · SES {'OK' if result.get('ses_ok') else 'n/a'}\n")
    with open(idx, "a", encoding="utf-8") as f:
        f.write(line)

    # 3. KB harvest suggestions (Nyquist applies these via wiki-publish)
    out["kb_suggestions"].append(
        f"active-projects.md: add Completed row — {spec.show_name} "
        f"({spec.venue.upper()}, {spec.show_date}), built by ShowBuilder.")
    if spec.reverbs:
        rv = ", ".join(f"{r.bank} #{r.num} {r.name}" for r in spec.reverbs[:3])
        out["kb_suggestions"].append(
            f"reverb-reference-memo: confirm picks held up live for {spec.genre} "
            f"at {spec.venue} — {rv}.")
    out["kb_suggestions"].append(
        "eq-starting-points: if any EQ move was changed live, tag it by genre.")
    return out
