"""Seed the three house rigs from CLAUDE.md so there's something real to open.

    ./.venv/bin/python -m backend.seed        (safe to re-run: skips existing names)
"""
from __future__ import annotations

from .knowledge import Knowledge
from .sheet import blank_input, blank_output, new_sheet
from .store import Store

KB = Knowledge()
STORE = Store()


def _inputs(rows: list[tuple]) -> list[dict]:
    out = []
    for ch, name, mic, stand, section, port, notes in rows:
        row = blank_input(ch)
        m = KB.mic(mic)
        row.update(
            {
                "name": name,
                "mic": m["name"] if m else mic,
                "stand": stand,
                "section": section,
                "port": port,
                "notes": notes,
                "phantom": bool(m and m["phantom"] and not m["ribbon"]),
                "ribbon": bool(m and m["ribbon"]),
            }
        )
        out.append(row)
    return out


def _outputs(rows: list[tuple]) -> list[dict]:
    out = []
    for bus, name, port, device, location in rows:
        o = blank_output(bus, name)
        o.update({"port": port, "device": device, "location": location})
        out.append(o)
    return out


def memo() -> dict:
    console = KB.console("q225")
    s = new_sheet("Memorial Hall — house rig", "q225", "memo", "Memorial Hall", "install", [], channels=0)
    s["meta"]["notes"] = (
        "556 seats, hardwood, working RT60 ~1.6s. Problem zones 63/125/200/250–315Hz standing waves, "
        "200–400Hz mud — treat in EQ, especially on the crowd mics. Piano storage stage right.\n"
        "Crowd rig is permanent: leave the CH numbers to the show, the placements never move."
    )
    s["stageboxes"] = [
        {"id": "sb1", "name": "SD-Rack SL", "location": "Stage Left", "format": "MADI", "inputs": 56, "outputs": 24, "notes": "(CONFIRM rack model + I/O count at the desk)"},
        {"id": "sb2", "name": "Wire array", "location": "Flown, 8' downstage of ensemble, 9' up", "format": "—", "inputs": 2, "outputs": 0, "notes": "Schoeps MK5 ORTF pair (cardioid; omni if the session wants warmth/width)"},
    ]
    s["inputs"] = _inputs([
        (1, "Crowd OM1 L", "Line Audio OM1", "—", "AMBIENT", "", "Flown 18' above stage, 12' apart — omni pressure balls, FOH color"),
        (2, "Crowd OM1 R", "Line Audio OM1", "—", "AMBIENT", "", "Pair with CH1"),
        (3, "Crowd Deity L", "Deity S2", "—", "AMBIENT", "", "Under main-floor PA, aimed into the audience — short shotgun pair"),
        (4, "Crowd Deity R", "Deity S2", "—", "AMBIENT", "", "Pair with CH3"),
        (5, "Crowd CM4 L", "Line Audio CM4", "—", "AMBIENT", "", "Balcony ORTF pair, rear-facing into the room, 34' from the Deity pair"),
        (6, "Crowd CM4 R", "Line Audio CM4", "—", "AMBIENT", "", "Pair with CH5"),
    ])
    s["outputs"] = _outputs([
        ("Group 1", "Drums", "", "", ""),
        ("Group 2", "Rhythm", "", "", ""),
        ("Group 3", "Piano (St)", "", "", ""),
        ("Group 4", "Strings", "", "", ""),
        ("Group 5", "Horns / Winds", "", "", ""),
        ("Group 6", "Vocals", "", "", ""),
        ("Group 7", "FOH Ambient", "", "", ""),
        ("Matrix 1", "PA L", "Local Out 1", "House PA", "FOH"),
        ("Matrix 2", "PA R", "Local Out 2", "House PA", "FOH"),
        ("Aux 1", "Wedge 1", "", "", "Downstage center"),
        ("Aux 2", "Wedge 2", "", "", "Downstage left"),
    ])
    return s


def fsq() -> dict:
    s = new_sheet("Fountain Square — house rig", "q225", "fsq", "Fountain Square", "install", [], channels=0)
    s["meta"]["notes"] = (
        "FOH DiGiCo Quantum 225, monitors on the Midas M32. PA: 4× A15/side, 8× KS21 delayed arch subs, 8× X12 wedges.\n"
        "Tempest weather station 215217. Outdoor EQ: cuts one step deeper than indoor (−6 to −9 dB, up to −10 on mud)."
    )
    s["stageboxes"] = [
        {"id": "sb1", "name": "Stage rack", "location": "Stage Left", "format": "MADI / DMI (CONFIRM)", "inputs": None, "outputs": None, "notes": "Confirm card + channel count at load-in"},
        {"id": "sb2", "name": "M32 monitor split", "location": "Stage Right", "format": "AES50", "inputs": 32, "outputs": 16, "notes": "Monitor world"},
    ]
    s["outputs"] = _outputs([
        ("Matrix 1", "PA L — A15", "", "L-Acoustics A15 ×4", "SL array"),
        ("Matrix 2", "PA R — A15", "", "L-Acoustics A15 ×4", "SR array"),
        ("Matrix 3", "Subs", "", "L-Acoustics KS21 ×8", "Delayed arch"),
        ("Aux 1", "Wedge 1", "", "X12", "DSC"),
        ("Aux 2", "Wedge 2", "", "X12", "DSL"),
        ("Aux 3", "Wedge 3", "", "X12", "DSR"),
        ("Aux 4", "Wedge 4", "", "X12", "Drums"),
        ("Group 1", "Drums", "", "", ""),
        ("Group 2", "Rhythm", "", "", ""),
        ("Group 6", "Vocals", "", "", ""),
    ])
    s["power"] = [
        {"id": "p1", "name": "Stage distro", "location": "Stage Left", "feed": "(CONFIRM service)", "circuits": [
            {"ckt": "L1-1", "load": "Amp rack / PA drive", "amps": "", "notes": "Confirm at load-in"},
            {"ckt": "L2-1", "load": "Backline SL", "amps": "", "notes": ""},
            {"ckt": "L3-1", "load": "FOH world", "amps": "", "notes": "Console, racks, laptop"},
        ]},
    ]
    return s


def wp() -> dict:
    s = new_sheet("Washington Park — house rig", "m32", "wp", "Washington Park", "install", [], channels=0)
    s["meta"]["notes"] = "FOH Midas M32. PA: 1× JBL SRX915 top + 8× SRX906 array per side, 2× SRX928 subs per side."
    s["stageboxes"] = [
        {"id": "sb1", "name": "DL32 stage box", "location": "Stage Left", "format": "AES50 A", "inputs": 32, "outputs": 16, "notes": "(CONFIRM box model)"},
    ]
    s["outputs"] = _outputs([
        ("Matrix 1", "PA L", "Out 1", "JBL SRX915 + SRX906", "SL"),
        ("Matrix 2", "PA R", "Out 2", "JBL SRX915 + SRX906", "SR"),
        ("Matrix 3", "Subs", "Out 3", "JBL SRX928 ×2/side", "Ground"),
        ("Mix 1", "Wedge 1", "Out 5", "", "DSC"),
        ("Mix 2", "Wedge 2", "Out 6", "", "DSL"),
        ("Mix 9", "Drums", "", "", ""),
        ("Mix 11", "Vocals", "", "", ""),
    ])
    return s


def wing_demo() -> dict:
    s = new_sheet("Wing — freelance rig", "wing", "other", "Freelance / one-offs", "install", [], channels=0)
    s["meta"]["notes"] = (
        "Wing travel rig. USB outputs are pre-everything by default (true direct out, no tap point needed) — "
        "48×48 straight to the capture machine. FX preset save/load has been broken since firmware v1.13; "
        ".efx files are not compatible."
    )
    s["outputs"] = _outputs([
        ("Main 1", "Main LR", "Local Out 1", "", "FOH"),
        ("Bus 1", "Wedge 1", "Local Out 3", "", "DSC"),
        ("Bus 3", "IEM 1", "AES Out 1", "", "SL"),
        ("Matrix 1", "PA L", "Local Out 5", "", ""),
        ("Matrix 2", "PA R", "Local Out 6", "", ""),
    ])
    return s


def main() -> None:
    existing = {s["name"] for s in STORE.list()}
    for build in (memo, fsq, wp, wing_demo):
        sheet = build()
        if sheet["name"] in existing:
            print(f"skip  {sheet['name']} (already there)")
            continue
        saved = STORE.create(sheet)
        print(f"seed  {saved['name']}  →  {saved['id']}")


if __name__ == "__main__":
    main()
