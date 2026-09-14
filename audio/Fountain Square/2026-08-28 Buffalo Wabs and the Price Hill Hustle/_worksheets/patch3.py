p="_worksheets/build_spec.py"; s=open(p).read()

start=s.index("reverbs = [")
end=s.index("research = {")
new_reverbs=r'''reverbs = [
 dict(role="vocal",preset="Seventh Heaven Pro — Plates 1 / #06 Vocal Plate",
   settings="Decay 1.5s (factory) · PreDelay 24ms (factory) · VLF -19 (factory) · E/L Max Early · Late -6 (raised from the factory reference for outdoors) · Late Rolloff 6400 (factory)",
   plugin_eq="Return-channel EQ (Q225): HPF 200 · LPF 9k · B3 -3 @ 3.5k Q2 · B2 -3 @ 500 Q1.8",
   why="Lead + harmony-ballad plate. Its tail already rolls at 6.4k with a clean low (VLF -19), so it needs the least top-taming — LPF stays at 9k to keep the sheen that lifts the harmony; -3@3.5k stops it going strident when all four voices stack, -3@500 clears the dense-plate low-mid."),
 dict(role="vocal",preset="Waves CLA Epic — The Vocal 3 preset (plate + slap)",
   settings="CLA Epic lead-vocal preset (Chris Lord-Alge plate + slap/throw). Keep the preset plate time/pre-delay; set HF Damp so the slap repeats do not spit. Bright, forward lead verb.",
   plugin_eq="Return-channel EQ (Q225): HPF 220 · LPF 7.5k · B3 -4 @ 4k Q2 · B2 -3 @ 450 Q1.8",
   why="The brightest, most forward return in the set. Gets the hardest top pull (LPF 7.5k) and deepest de-harsh (-4@4k) or it turns edgy/sibilant outdoors in the humidity and the slap repeats spit; HPF 220 keeps those repeats articulate. Ring this one out at soundcheck — most feedback-prone."),
 dict(role="vocal",preset="Soundtoys EchoBoy Hallway (30% wet) → Seventh Heaven Pro — Chambers 1 / #17 Sunset Chamber",
   settings="Serial chain: EchoBoy Hallway at 30% wet feeding Sunset Chamber (Decay 2.15s factory · PreDelay 20ms factory · VLF -20 factory · E/L Max Early · Late -8 · Late Rolloff 7200 factory). Warm, dark, long — the big-moment/ballad return.",
   plugin_eq="Return-channel EQ (Q225): HPF 260 · LPF 10k · B3 -2 @ 3k Q2 · B2 -4 @ 350 Q1.6",
   why="Warm/dark and LONG (2.15s) with EchoBoy tape warmth ahead of it — already soft up top, so LPF stays gentle at 10k and the 3k cut is only -2 (over-darkening kills the bloom). The work is down low: highest HPF (260) + deepest mud cut (-4@350), because a long tail plus a serial tape stage is where this chain turns to soup on a busy number."),
 dict(role="instrument",preset="Waves CLA Epic — Acoustic Guitar Room 1 preset",
   settings="CLA Epic room voiced for acoustic guitar — tight, present room. Glue for the acoustic pickers (mando/reso/banjo/acoustic). Keep the preset time short.",
   plugin_eq="Return-channel EQ (Q225): HPF 180 · LPF 8k · B3 -4 @ 2.5k Q2 · B2 -3 @ 400 Q1.8",
   why="Key move: -4@2.5k is the exact piezo-quack/metallic zone cut on every string source, so this room tail cannot re-energize what the channel EQ removed. CLA brightness plus banjo/reso metallic top is why LPF sits at 8k; HPF 180 lets a little instrument body bloom while blocking mud."),
 dict(role="drum",preset="Waves Atlas Reverb — Big Drum Room preset",
   settings="Atlas algorithmic large drum room. Big body + cymbal wash; consider trimming the program decay for the open-air mix.",
   plugin_eq="Return-channel EQ (Q225): HPF 160 · LPF 8k · B3 -3 @ 3k Q2 · B2 -4 @ 300 Q1.8",
   why="A big room signature problem is low-mid body and cymbal wash, both amplified by the size — HPF 160 keeps kick/floor tom out so punch stays dry, -4@300 carves the boxy room resonance a big algorithm piles up, -3@3k tames cymbal/hat wash before it smears the outdoor mix. Cuts-only — no snap boost outdoors."),
]

'''
s=s[:start]+new_reverbs+s[end:]

old_rp='''"reverb_pairing":"Two lead vocal returns hand off song to song: Vocal Plate is the default forward lead + the ballad harmony bed; Vocal Chamber is the warmer mid-tempo option; on the fast foot-stompers ride the dry Small Room instead so the lyric stays articulate outdoors. Long Wood Room is the acoustic-instrument glue — mandolin, resonator, banjo, acoustic guitar feed it as a group for cohesion; keep the upright out of it. Snare Chamber is a backbeat-only splash on uptempo numbers, off under ballads. Large Ambience is a whisper of overall band air, ridden up only when a number feels bone-dry. All returns 100% wet, level ridden by the sends."'''
new_rp='''"reverb_pairing":"Five real returns. Three vocal returns hand off by song type: the Seventh Heaven Vocal Plate is the default forward lead + harmony bed; the CLA Epic Vocal 3 (bright plate+slap) is the up-front, aggressive option for a feature or a driving number; the EchoBoy->Sunset Chamber chain is the warm, long big-moment/ballad wash — ride it up only on the slow, spacious tunes and pull it under fast ones. The CLA Epic Acoustic Guitar Room glues the acoustic pickers (mandolin/resonator/banjo/acoustic) as a group; keep the upright out of it. The Atlas Big Drum Room sits under the kit — ride it up on the foot-stompers, off under ballads. All returns 100% wet, level ridden by the sends; return EQ per the plugin_eq lines (Q225 return-channel or the plugin own filter — same targets)."'''
assert old_rp in s, "pairing not found"
s=s.replace(old_rp,new_rp)

s=s.replace('"rev":"Rev 2.0 Deep Think"','"rev":"Rev 2.1 Deep Think"')

s=s.replace('"changes":[\n  "REV 2 (revised input list',
            '"changes":[\n  "REV 2.1: reverb section replaced with the actual return rig (SH Vocal Plate, CLA Epic Vocal 3, EchoBoy Hallway->SH Sunset Chamber, CLA Epic Acoustic Guitar Room, Atlas Big Drum Room) with per-return return-channel EQ researched to each preset voicing. Documentation only — the .ses is unchanged.",\n  "REV 2 (revised input list')

open(p,"w").write(s); print("OK: reverbs replaced, pairing + rev + changes updated")
