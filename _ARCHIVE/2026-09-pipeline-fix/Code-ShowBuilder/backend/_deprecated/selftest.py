"""Quick end-to-end smoke test of the engines + MD + patcher (no server)."""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from backend.knowledge import Knowledge
from backend.spec import ShowSpec, Channel
from backend.engine import apply_engines, inject_crowd_rig
from backend.build import render_md, run_patcher, readback_check

cfg = json.loads((Path(__file__).resolve().parent.parent / "config.json").read_text())
kn = Knowledge(cfg)


def build_spec(venue, genre, rows):
    spec = ShowSpec(venue=venue, show_name=f"SelfTest {venue.upper()}",
                    artist="Test Artist", genre=genre, eq_on=True, comp_on=True)
    for ch, name, inst, mic in rows:
        spec.channels.append(Channel(ch=ch, name=name, instrument=inst, mic=mic))
    apply_engines(kn, spec)
    inject_crowd_rig(kn, spec)
    return spec


def run(venue, genre, rows):
    print(f"\n{'='*64}\n{venue.upper()} / {genre}\n{'='*64}")
    spec = build_spec(venue, genre, rows)
    md = render_md(kn, spec)
    print(md)
    print("Reverbs:")
    for r in spec.reverbs:
        print("  " + r.line())
    print("  note:", spec.reverb_note[:90])
    with tempfile.TemporaryDirectory() as td:
        mdp = Path(td) / "proc.md"
        mdp.write_text(md, encoding="utf-8")
        dest = Path(td) / f"{venue}.ses"
        ok, log = run_patcher(kn, spec, dest, mdp)
        print("\nPATCHER:", "PASS" if ok else "FAIL")
        print("  " + "\n  ".join(log.strip().splitlines()[-6:]))
        if ok:
            rok, notes = readback_check(kn, spec, dest)
            print("READBACK:", "OK" if rok else "MISMATCH", "—", notes)


run("fsq", "variety rock", [
    (9, "EKIT L", "ekit", "DI"),
    (11, "BASS DI", "bass", "DI"),
    (13, "GTR 1", "guitar", "Sennheiser e609"),
    (17, "KEYS", "keys", "DI"),
    (18, "SAX 1", "sax", "AT Pro 35"),
    (25, "WAYNE", "lead vocal", "Shure SM58"),
])

run("memo", "jazz", [
    (1, "Kick", "kick", "Earthworks DM6"),
    (2, "Snare", "snare", "Shure SM57"),
    (9, "Bass DI", "bass", "Radial J48"),
    (13, "Gtr", "guitar", "Shure SM57"),
    (19, "Lead Vox", "lead vocal", "Shure Beta 58A"),
])
