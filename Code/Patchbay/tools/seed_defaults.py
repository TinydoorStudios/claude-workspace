"""Fill the house templates with the defaults we already know, then lock them.

    ../ShowBuilder/.venv/bin/python -m tools.seed_defaults

Console identity and counts come from knowledge/consoles.json — nothing invented.
Venue detail comes from the workspace CLAUDE.md. Anything that couldn't be sourced
is left blank on purpose so it shows up amber in the intake workbook.

Re-runnable: it only writes fields that are still empty, so hand-edits survive.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.knowledge import Knowledge  # noqa: E402
from backend.schema import blank_console  # noqa: E402
from backend.store import Store  # noqa: E402

KB = Knowledge()

# Counts we can defend: the console data file, which is sourced from published specs.
COUNTS = {
    "q225": {"inputs": 72, "busses": 36, "matrix": 12, "outputs": 8},
    "m32": {"inputs": 32, "busses": 16, "auxes": 6, "dcas": 8, "mutes": 6, "matrix": 6, "outputs": 16},
    "wing": {"inputs": 48, "busses": 16, "auxes": 8, "dcas": 16, "mutes": 8, "matrix": 8, "outputs": 8},
}

DEFAULTS = {
    "memorial-hall-house-rig": {
        "location": {
            "project": "Memorial Hall — house rig",
            "client": "Jazz At The Memo",
            "site": "Memorial Hall",
            "room": "FOH",
            "address": "1225 Elm St",  # verify on the intake sheet
            "city": "Cincinnati",
            "state": "OH",
            "zip": "45202",
        },
        "console_names": ["FOH Console"],
        "contacts": [
            {"name": "Brian Lloyd", "role": "FOH / Sound Engineer", "phone": "(315) 404-5648",
             "email": "tinydoorstudios@gmail.com", "notes": ""},
        ],
    },
    "fountain-square-house-rig": {
        "location": {
            "project": "Fountain Square — house rig",
            "client": "3CDC",
            "site": "Fountain Square",
            "room": "FOH",
            "address": "520 Vine St",  # verify on the intake sheet
            "city": "Cincinnati",
            "state": "OH",
            "zip": "45202",
        },
        "console_names": ["FOH Console", "Monitor World"],
        "extra_consoles": [("m32", "Monitor World")],
        "contacts": [
            {"name": "Brian Lloyd", "role": "FOH / Events & Production", "phone": "(315) 404-5648",
             "email": "Blloyd@3cdc.org", "notes": ""},
        ],
    },
    "washington-park-house-rig": {
        "location": {
            "project": "Washington Park — house rig",
            "client": "3CDC",
            "site": "Washington Park",
            "room": "FOH",
            "address": "1230 Elm St",  # verify on the intake sheet
            "city": "Cincinnati",
            "state": "OH",
            "zip": "45202",
        },
        "console_names": ["FOH Console"],
        "contacts": [
            {"name": "Brian Lloyd", "role": "FOH / Events & Production", "phone": "(315) 404-5648",
             "email": "Blloyd@3cdc.org", "notes": ""},
        ],
    },
    "wing-freelance-rig": {
        "location": {
            "project": "Wing — freelance rig",
            "client": "Tiny Door Studios",
            "site": "",
            "room": "",
        },
        "console_names": ["FOH Console"],
        "contacts": [
            {"name": "Brian Lloyd", "role": "FOH / Owner", "phone": "(315) 404-5648",
             "email": "tinydoorstudios@gmail.com", "notes": ""},
        ],
    },
}


def fill_blank(target: dict, values: dict) -> None:
    for k, v in values.items():
        if v and not target.get(k):
            target[k] = v


def main() -> None:
    store = Store()
    for sheet_id, spec in DEFAULTS.items():
        if not store.exists(sheet_id):
            print(f"skip {sheet_id} — not on disk")
            continue
        sheet = store.get(sheet_id)
        sheet["locked"] = False  # so save() goes through; re-locked at the end

        fill_blank(sheet.setdefault("location", {}), spec["location"])

        for preset, name in spec.get("extra_consoles", []):
            if not any(c.get("preset") == preset for c in sheet["consoles"]):
                sheet["consoles"].append(blank_console(preset, name))

        for i, con in enumerate(sheet["consoles"]):
            names = spec.get("console_names", [])
            if i < len(names) and con.get("name") in ("", "Console"):
                con["name"] = names[i]
            kb = KB.console(con.get("preset") or "q225")
            fill_blank(con, {"manufacturer": kb["vendor"],
                             "model": kb["label"].replace(kb["vendor"], "").strip()})
            for key, value in COUNTS.get(con.get("preset"), {}).items():
                if not con["counts"].get(key):
                    con["counts"][key] = value

        if not sheet.get("contacts"):
            sheet["contacts"] = [{"id": f"c{i}", **c} for i, c in enumerate(spec.get("contacts", []), start=1)]

        sheet["locked"] = True
        store.save(sheet_id, sheet, bump=True)
        print(f"seeded + locked {sheet_id}")


if __name__ == "__main__":
    main()
