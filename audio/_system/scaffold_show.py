#!/usr/bin/env python3
"""
Show-folder scaffold — one command replaces the manual setup every show
starts with.

Usage:
    python3 scaffold_show.py --venue memo|fsq|wp|esp|csp|zp|ia|greaves \
        --date YYYY-MM-DD --name "Show Name" [--short showname]

Creates:
    <Venue folder>/YYYY-MM-DD Show Name/
        apply_<short>.py                      (memo/fsq only — venue patcher copy)
        Show Name - FOH Channel Processing.md (skeleton, deep-build fills it)

It does NOT invent any EQ — the MD skeleton is a stub. EQ comes from the
show-deep-build ("Deep Think") flow driving eq-advisor, per the pipeline
specs. The scaffold just removes the folder/patcher/file-naming setup.
"""
import argparse, datetime, os, shutil, sys

AUDIO = os.path.expanduser("~/Documents/Claude/audio")

VENUES = {
    'memo':    ("Memorial Hall",
                "Memorial Hall/Q225 SES Patcher SOP/apply_show_TEMPLATE.py"),
    'fsq':     ("Fountain Square",
                "Fountain Square/Q225 SES Patcher SOP/apply_show_TEMPLATE_FSQ.py"),
    'wp':      ("Washington Park", None),
    'esp':     ("Elm Street Plaza", None),
    'csp':     ("Court Street Plaza", None),
    'zp':      ("Zeigler Park", None),
    'ia':      ("Imagination Alley", None),
    'greaves': ("Greaves Concert Hall", None),
}

SKELETON = """# {name} — FOH Channel Processing
Venue: {venue_name} · Date: {date} · Console: {console}

STUB — filled by the show-deep-build ("Deep Think") flow. Locked format,
one block per processed channel (B1 = console LOW band .. B4 = HIGH):

    ## Ch N | CONSOLE NAME | MIC/DI
    HPF: hz | LPF: hz-or-OFF
    B1: gain | freq_hz | Q | SHELF-or-BELL
    B2: gain | freq_hz | Q | BELL | DEQ: thr=-16 atk=10ms rel=100ms
    B3: FLAT
    B4: gain | freq_hz | Q | SHELF-or-BELL

Rules: console name <= 12 chars · whole-dB gains · display Hz (the patcher
scales) · FLAT for a bypassed band · lint runs automatically on every patch.
{venue_notes}"""

MEMO_NOTES = """
Memo don't-forgets:
  - Crowd rig is always patched: Above Stage Mics = fader 57, Floor Crowd =
    fader 58, Balcony Crowd = fader 59 in the june-2026 template. KB crowd
    EQ lives in eq-starting-points; confirm with Brian before writing them
    into this MD.
  - Wireless 1-4 = faders 41-44, and they ship a baked-in starting vocal
    curve — MD-unnamed bands inherit it.
  - Vocals are cuts only. Room: RT60 ~1.6 s; treat 63/125/200/250-315 Hz.
"""

FSQ_NOTES = """
FSQ don't-forgets:
  - Channels 1-32 only; MIC/DI column decides what gets processed.
  - Vocals/wireless faders 25-36 ship a baked-in starting curve.
  - Outdoor: HPFs trend higher, cuts over boosts, reverb minimal to none.
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description="Scaffold a show folder.")
    ap.add_argument('--venue', required=True, choices=sorted(VENUES))
    ap.add_argument('--date', required=True, help="YYYY-MM-DD")
    ap.add_argument('--name', required=True, help="show name")
    ap.add_argument('--short', help="short lowercase name for apply_<short>.py")
    a = ap.parse_args(argv)

    try:
        datetime.date.fromisoformat(a.date)
    except ValueError:
        print(f"ERROR: --date {a.date!r} is not YYYY-MM-DD"); return 2

    folder_name, patcher_rel = VENUES[a.venue]
    venue_dir = os.path.join(AUDIO, folder_name)
    os.makedirs(venue_dir, exist_ok=True)
    show_dir = os.path.join(venue_dir, f"{a.date} {a.name}")
    if os.path.exists(show_dir):
        print(f"ERROR: {show_dir} already exists — not touching it."); return 2
    os.makedirs(show_dir)
    made = [show_dir]

    if patcher_rel:
        short = a.short or ''.join(c for c in a.name.lower() if c.isalnum())[:12]
        dst = os.path.join(show_dir, f"apply_{short}.py")
        shutil.copy(os.path.join(AUDIO, patcher_rel), dst)
        made.append(dst)

    console = ("DiGiCo Quantum 225" if a.venue in ('memo', 'fsq')
               else "Behringer Wing" if a.venue == 'greaves'
               else "Midas M32" if a.venue == 'wp' else "confirm console")
    notes = (MEMO_NOTES if a.venue == 'memo'
             else FSQ_NOTES if a.venue == 'fsq' else "")
    md = os.path.join(show_dir, f"{a.name} - FOH Channel Processing.md")
    open(md, 'w', encoding='utf-8').write(SKELETON.format(
        name=a.name, venue_name=folder_name, date=a.date, console=console,
        venue_notes=notes))
    made.append(md)

    print("Created:")
    for p in made:
        print(f"  {p}")
    print("\nNext: run the deep build (show-deep-build / eq-advisor) to fill "
          "the MD,\nthen 'send it {}' to build the .ses.".format(
              a.venue if a.venue in ('memo', 'fsq') else '<no .ses pipeline>'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
