"""One-off acceptance check: export a facts-only Izzy brief (19ch FSQ) with
amp + miking-technique notes, then assert no EQ keys leaked and notes are
verbatim. Run from the ShowBuilder root with the venv python. Non-destructive:
writes to a '(Brief Test)' folder, not the real Izzy show folder."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.app import _brief_from_payload, CONFIG
from backend.knowledge import Knowledge

KN = Knowledge(CONFIG)

# amp + miking-technique notes Brian would type — the deep build's research hooks
NOTE_KICK = "Beta 91A inside + 52A at the port. Treat as one blend."
NOTE_BASS_MIC = "Ampeg SVT + 8x10, SM57 on the cab. Flatwounds, fingerstyle."
NOTE_GTR57 = "Vox AC30 top boost, edge-of-breakup. 57 + Beta 27 blend (off-axis pair)."

rows = [
    (1, "Kick In", "Kick", "Shure Beta 91A", "DRUMS", True, "Boom", NOTE_KICK),
    (2, "Kick Out", "Kick", "Shure Beta 52A", "DRUMS", False, "Boom", ""),
    (3, "Snare Top", "Snare", "Audix i5", "DRUMS", False, "Boom", ""),
    (5, "Hat", "Hi-Hat", "Shure SM81", "DRUMS", True, "Boom", ""),
    (6, "Rack 1", "Rack Tom", "Audix D2", "DRUMS", False, "Boom", ""),
    (7, "Rack 2", "Rack Tom", "Audix D2", "DRUMS", False, "Boom", ""),
    (8, "Floor", "Floor Tom", "Audix D4", "DRUMS", False, "Boom", ""),
    (9, "OH HL", "Overhead L", "Shure SM81", "DRUMS", True, "Boom", ""),
    (10, "OH HR", "Overhead R", "Shure SM81", "DRUMS", True, "Boom", ""),
    (11, "Bass DI", "Bass", "XLR (DI)", "RHYTHM", False, "DI", "Bass DI + cab blend."),
    (12, "Bass Mic", "Bass Cab", "Shure SM57", "RHYTHM", False, "DI", NOTE_BASS_MIC),
    (13, "Guitar 57", "Electric Gtr", "Shure SM57", "RHYTHM", False, "DI", NOTE_GTR57),
    (14, "Guitar 27", "Electric Gtr", "Shure Beta 27", "RHYTHM", True, "DI", "57/27 blend pair."),
    (15, "Acoustic Guitar", "Acoustic Gtr", "BSS AR-133", "RHYTHM", False, "DI", "Piezo DI."),
    (17, "Keys", "Keys", "Whirlwind IMP (DI)", "RHYTHM", False, "DI", "Piano-forward writing."),
    (18, "Click", "Click", "Whirlwind IMP (DI)", "RHYTHM", False, "DI", "Monitors/IEM only — not FOH."),
    (19, "Guide", "Guide Vocal", "Whirlwind IMP (DI)", "RHYTHM", False, "DI", "Cue track — monitors only."),
    (20, "Tracks", "Playback", "Whirlwind IMP (DI)", "RHYTHM", False, "DI", "Mastered full-range stem."),
    (25, "Izzy", "Female Vocal", "Neumann KMS 105", "VOCALS", True, "Tall", "Wired handheld on a stand."),
]

payload = {
    "venue": "fsq",
    "venue_label": "Fountain Square (outdoor)",
    "console_label": "DiGiCo Quantum 225",
    "show_name": "Izzy Escobar (Brief Test)",
    "artist": "Izzy Escobar",
    "genre": "Pop / R&B",
    "show_date": "2026-06-26",
    "foh_engineer": "Brian Lloyd",
    "mon_engineer": "Sam Carpender",
    "show_time": "9:00pm",
    "rev": "Rev 1.0",
    "show_notes": "Outdoor, possible wind. Intimate vocal, minimal verb. 75-min set. Winehouse+Adele vocal reference.",
    "channels": [
        {"ch": r[0], "name": r[1], "instrument": r[2], "mic": r[3], "section": r[4],
         "phantom": r[5], "stand": r[6], "notes": r[7]}
        for r in rows
    ],
}
# explicit patch override (e.g. Dante wireless) must round-trip untouched
payload["channels"][17]["patch"] = "Dante 52"

brief = _brief_from_payload(payload)
folder = KN.show_folder(brief.venue, brief.folder_name())
folder.mkdir(parents=True, exist_ok=True)
path = folder / f"{brief.slug()}.brief.json"
brief.save(path)
d = brief.to_dict()

# ---- assertions ----
EQ_KEYS = {"hpf", "lpf", "bands", "comp", "gate", "mic_notes", "eq_summary",
           "eq_on", "comp_on", "reverbs", "research"}
leaked = set()
for c in d["channels"]:
    leaked |= (EQ_KEYS & set(c.keys()))
assert not leaked, f"EQ keys leaked into the brief: {leaked}"
assert "reverbs" not in d and "eq_on" not in d, "show-level EQ keys leaked"

byname = {c["name"]: c for c in d["channels"]}
assert byname["Guitar 57"]["notes"] == NOTE_GTR57, "Guitar 57 note not verbatim"
assert byname["Bass Mic"]["notes"] == NOTE_BASS_MIC, "Bass Mic note not verbatim"
assert byname["Kick In"]["notes"] == NOTE_KICK, "Kick In note not verbatim"
assert d["show_notes"] == payload["show_notes"], "show_notes not verbatim"

non_crowd = [c for c in d["channels"] if not c.get("is_crowd")]
assert len(non_crowd) == 19, f"expected 19 channels, got {len(non_crowd)}"
# patch default + explicit override + ribbon/phantom + genre facts
assert byname["Izzy"]["phantom"] is True and byname["Izzy"]["patch"] == "Local 25"
assert byname["Tracks"]["patch"] == "Dante 52", "explicit patch not preserved"
assert byname["Kick Out"]["phantom"] is False
assert d["genre"] == "Pop / R&B", "genre not carried in the brief"

print(f"PASS — wrote {path}")
print(f"  channels: {len(non_crowd)} · no EQ keys · notes verbatim")
print(f"  amp/technique notes present on Guitar 57, Bass Mic, Kick In")
print("\n--- first channel ---")
print(json.dumps(d["channels"][0], indent=2, ensure_ascii=False))
