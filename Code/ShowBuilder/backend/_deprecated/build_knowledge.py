#!/usr/bin/env python3
"""
build_knowledge.py — derive reverb_presets.json from the KB.

The Seventh Heaven Pro reverb data is authored once, in the wiki article
`reverb-reference-memo.md`. This script parses that article so the KB stays the
single source of truth: factory bank tables become the preset library, and the
"By Genre — Starting Presets (Memo)" tables + the FSQ section become the
selection rules the reverb engine uses. Re-run after editing the KB article.

    python3 backend/build_knowledge.py

Writes knowledge/reverb_presets.json. Never invents preset names — every name and
number comes verbatim from the article.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
KB = (ROOT.parent.parent / "audio" / "Live Sound KB" / "Wiki"
      / "reverb-reference-memo.md")
OUT = ROOT / "knowledge" / "reverb_presets.json"


def norm(s: str) -> str:
    """Normalize unicode minus/dashes and whitespace."""
    return (s.replace("−", "-").replace("–", "-")
            .replace("—", "-").strip())


def num_or_none(s):
    s = norm(s)
    if s in ("", "-", "off", "OFF", "Off"):
        return None
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    return float(m.group()) if m else None


def parse_factory_banks(text):
    """Each `### Bank Name (Vx)` followed by a 7-col factory table."""
    banks = []
    # split on level-3 headers, keep header text
    parts = re.split(r"\n###\s+", text)
    for part in parts[1:]:
        header, _, body = part.partition("\n")
        header = norm(header)
        # only factory banks live before "## By Genre"; the control-reference
        # ### sections (Decay Time, VLF, ...) have no 7-col preset table.
        algo = "V1"
        m = re.search(r"\((V1|V2)\)", header)
        if m:
            algo = m.group(1)
        elif header.lower().startswith("nonlinear"):
            algo = "Nonlinear"
        else:
            continue  # not a preset bank
        bank_name = re.sub(r"\s*\((V1|V2)\)\s*$", "", header).strip()
        presets = []
        for line in body.splitlines():
            line = line.strip()
            if not line.startswith("|"):
                if presets:
                    break  # table ended
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) != 7:
                continue
            if cells[0] in ("#", "---") or set(cells[0]) <= set("-: "):
                continue
            if not re.match(r"\d+", cells[0]):
                continue
            presets.append({
                "num": cells[0].zfill(2),
                "name": norm(cells[1]),
                "decay_s": num_or_none(cells[2]),
                "predelay_ms": num_or_none(cells[3]) or 0,
                "vlf_db": num_or_none(cells[4]),
                "lateroll_hz": num_or_none(cells[5]),
                "es": int(num_or_none(cells[6])) if num_or_none(cells[6]) is not None else None,
            })
        if presets:
            banks.append({"bank": bank_name, "algo": algo, "presets": presets})
    return banks


GENRE_KEYS = {
    "classical": "classical",
    "jazz": "jazz",
    "celtic": "celtic",
    "gospel": "gospel",
    "rock": "rock",
}


def genre_key(header):
    h = header.lower()
    for token, key in GENRE_KEYS.items():
        if token in h:
            return key
    return None


def parse_preset_cell(cell):
    """'Halls 1 / #10 Concert Hall' -> ('Halls 1', '10', 'Concert Hall')."""
    cell = norm(cell)
    m = re.match(r"(.+?)\s*/\s*#?(\d+)\s+(.+)", cell)
    if not m:
        return None
    return m.group(1).strip(), m.group(2).zfill(2), m.group(3).strip()


def parse_genre_tables(text):
    """The '## By Genre — Starting Presets (Memo)' block: ### per genre with a
    `Use | Preset | Factory | Memo Target | Notes` table."""
    out = {}
    block = text.split("## By Genre")[1] if "## By Genre" in text else ""
    block = block.split("## By Source")[0]
    parts = re.split(r"\n###\s+", block)
    for part in parts[1:]:
        header, _, body = part.partition("\n")
        gkey = genre_key(header)
        if not gkey:
            continue
        rows = []
        for line in body.splitlines():
            line = line.strip()
            if not line.startswith("|"):
                if rows:
                    break
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) != 5 or cells[0].lower() == "use" or set(cells[0]) <= set("-: "):
                continue
            parsed = parse_preset_cell(cells[1])
            if not parsed:
                continue
            bank, num, name = parsed
            rows.append({
                "use": norm(cells[0]),
                "bank": bank, "num": num, "name": name,
                "factory": norm(cells[2]),
                "memo_target": norm(cells[3]),
                "notes": norm(cells[4]),
            })
        if rows:
            out[gkey] = rows
    return out


def main():
    if not KB.exists():
        print(f"ERROR: KB article not found: {KB}", file=sys.stderr)
        return 2
    text = KB.read_text(encoding="utf-8")
    banks = parse_factory_banks(text)
    by_genre = parse_genre_tables(text)
    total = sum(len(b["presets"]) for b in banks)

    data = {
        "_source": "Live Sound KB/Wiki/reverb-reference-memo.md",
        "_note": ("Seventh Heaven Pro factory library + Memo genre selections, "
                  "parsed verbatim from the KB. Re-run build_knowledge.py after "
                  "editing the article. Reverb preset names/numbers are never "
                  "invented — they come from here."),
        "plugin": "LiquidSonics Seventh Heaven Professional",
        "always": "100% wet on a dedicated FX return; level ridden by the send.",
        "banks": banks,
        "by_genre_memo": by_genre,
        "fsq_logic": {
            "default": "minimal-to-none — most FSQ shows take no reverb send",
            "when_used": "short and bright; Rooms/Plates over long Halls; decay near factory",
            "vlf": "nearer factory (no 60-315Hz room buildup to fight)",
            "early_late": "Late carries more work outdoors — Equal to about -6 dB; Early still MAX",
            "lateroll": "brighter, 8-10kHz (no audience HF absorption)",
        },
        "memo_tweak_priorities": [
            "Decay — pull 30-40% from factory",
            "VLF — cut hard from factory (room reinforces 60-315Hz)",
            "Pre-delay — 10ms min, 20-30ms on vocals",
            "Late Rolloff — 4-6kHz classical/acoustic, 6-9kHz jazz/folk, 8-10kHz contemporary",
            "Early/Late — Early MAX, pull Late down toward -20/OFF",
            "Ducker (Reverb mode) on vocals",
        ],
    }
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Parsed {len(banks)} banks / {total} presets; "
          f"{len(by_genre)} genre tables ({', '.join(by_genre)}).")
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
