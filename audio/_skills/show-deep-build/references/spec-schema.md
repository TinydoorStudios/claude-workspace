# Deep-research spec.json schema

One file is the source of truth for the whole packet. `build_packet.py` reads it and writes the
`.md`, `.xlsx`, Show Packet PDF, and EQ Rationale PDF. Band numbering is Brian's console
convention: **b1 = low … b4 = high**. List only ACTIVE bands per channel — any band 1–4 you omit
(or set `gain: null` / `type: "FLAT"`) is treated as flat.

`build_packet.py` **validates the spec before writing anything** (ribbon + 48V = error, a boost
on a VOCALS channel = error unless the band carries `"approved": true` after Brian's explicit OK,
duplicate channels = error, band/freq/gain ranges, whole-dB and high-shelf warnings) and
auto-lints the written `.md` with `audio/_shared/md_lint.py`. A failed validation writes nothing.

```jsonc
{
  "venue": "fsq",
  "venue_label": "Fountain Square (outdoor)",
  "console_label": "DiGiCo Quantum 225",   // "225"/"digico" -> packet uses digico colors, else wing
  "show_name": "Izzy Escobar",
  "artist": "Izzy Escobar",
  "genre": "Pop-soul / indie-R&B (jazz-tinged)",
  "show_date": "2026-06-26",
  "foh_engineer": "Brian Lloyd",
  "mon_engineer": "Sam Carpender",
  "show_time": "9:00pm",
  "rev": "Rev 2.0 Deep Think",
  "app_version": "deep-think-1.0",

  // --- deep-research narrative (drives the Rationale PDF) ---
  "artist_profile": "Who they are + sonic references + what it means for the mix.",
  "room_context": "Venue/room filter — e.g. open-air FSQ: no room gain, support lows + presence.",

  // --- research: STRUCTURED, one object per researched unit (2026-07-27) ---
  // Renders as the Rationale's RESEARCH section: three framing boxes, then a
  // per-unit table (capsule fact + external source · verdict chip · the five
  // TRACE layers on their own lines). Write it structured — a free-text
  // "research_summary" string still builds (it gets chunked) but warns, and it
  // reads worse. Don't write both.
  "research": {
    "genre_verified": "The genre + the NAMED evidence it was verified against, before any research ran.",
    "gig": "What the event actually is (optional but usually worth it).",
    "conditions": "Outdoor shows: the FETCHED weather for the show window, source + pull date.",
    "units": [
      { "ch": "1",                       // "6/7" and "33–36" are fine for shared units
        "source": "Kick in",
        "mic": "Shure Beta 91A",
        "finding": "The QUANTITATIVE capsule fact — a frequency and a dB value.",
        "sources": "The external source(s), named. The KB alone is never research.",
        "verdict": "AGREE",              // AGREE | DISAGREE | THIN — one word, decided first
        "trace": {                       // all five layers; value or an explicit "no change"
          "base":   "91A boundary — 400 Hz box is the capsule's own documented problem, −8@400",
          "equip":  "no kit sizes notated — no change",
          "genre":  "R&B dance kick wants weight not click — top lift held to +3",
          "artist": "programmed kick in the Track channel — live kick narrowed to the attack lane",
          "venue":  "FSQ outdoor — box cut deepened to −8, HPF up to 60"
        } }
    ],
    "reconciliation": ["One line per web-vs-KB fork and how it was settled — or a single "
                       "\"no web/KB disagreements\" line."],
    "kb_writeback": ["Sources with no KB row yet — the write-back candidates."]
  },
  "research_summary": "LEGACY free-text fallback. Structured `research` supersedes it.",
  "style_note": "Short show-style line for the packet cover (optional; falls back to room_context).",
  "changes": [
    "Vocal: static -5@8k -> dynamic de-ess + HPF 130->110 — KMS 105 isn't sibilant; protect the air.",
    "Acoustic: air moved off the 5k piezo-harsh zone to 8k; 2k quack cut made dynamic."
  ],
  "decisions": [                    // optional — the answered question round, verbatim intent.
    "Q: gate the toms? -> Brian: yes, 5 ms attack.",
    // Every locker fork raised gets a line here, swapped or kept (2026-07-26).
    "Locker fork CH4 snare: DM17 offered over i5 -> Brian: swap (kit coherence).",
    "Locker fork CH9 gtr cab: PRO 6L offered over SM57 -> Brian: keep SM57."
  ],
  "monitors": [                     // optional — rides an xlsx Monitors sheet + Rationale header
    { "mix": "MIX 1", "who": "Lead Vox", "type": "wedge", "note": "verb-lite" },
    "MIX 7 drums IEM hardwire"      // plain strings are fine too
  ],
  "reverbs": [                      // REQUIRED every show, FSQ included (Brian 2026-07-08).
    // Structure: 3 complementary "vocal" options + 1-2 "instrument" (horn-specific when
    // asked) + 1 "general" when warranted. Preset names VERBATIM from the reverb KB.
    // Each option: settings (locked line values), plugin_eq (the in-plugin moves —
    // low cut / Late dB / rolloff, not just the preset name), why (the reasoning).
    { "role": "vocal",
      "preset": "Chambers 1 / #10 Vocal Chamber",
      "settings": "Decay 1.0s · PreDelay 10ms · VLF −18 · E/L Max Early · Late −6 · Rolloff 8k",
      "plugin_eq": "LC 200 Hz on the return; Late up to −6 (outdoors carries the late field)",
      "why": "gives place without wash on up-tempo material" },
    { "role": "instrument", "preset": "...", "settings": "...", "plugin_eq": "...", "why": "..." }
  ],
  "reverb_pairing": "How the options work together: which leads on which material, how the vocal options hand off, how the instrument verb sits under them without stacking mud.",
  "no_reverb": false,               // explicit opt-out ONLY when Brian says no reverb —
                                    // the validator errors on a missing/empty reverbs list otherwise
  "reverb_note": "Optional free-text alternative/addition to reverbs.",

  // --- channels (in fader order) ---
  // RESERVED template faders are validation errors — FSQ ch 10 = SNARE PL8 (snare plate
  // reverb return, never an input; the OH pair is STEREO on fader 9, never split 9/10).
  "channels": [
    {
      "ch": 25,
      "name": "Izzy",                 // fader label
      "instrument": "Female Vocal",
      "mic": "Neumann KMS 105",       // full name, no shorthand
      "section": "VOCALS",            // DRUMS/BASS/RHYTHM/GUITAR/KEYS/PIANO/STRINGS/HORNS/VOCALS/AMBIENT
      "phantom": true,                // -> 48V check
      "ribbon": false,                // ribbon -> NO 48V flag (red) auto-prepended to notes; ribbon+phantom = build error
      "tour": false,                  // artist-provided gear -> ⚑ TOUR flag auto-prepended; confirm at load-in
      "stand": "Tall",                // Short/Tall/Boom/Bar/Clip/DI/—
      "patch": "Local 25",            // optional; defaults to "Local <ch>". On a wireless mult
                                      // (2026-07-26) both rows carry the SAME source port —
                                      // the named input's channel and the wireless fader
                                      // (FSQ 33-36 / Memo 41-44, Wireless 1-4).
      "notes": "Blend / patch / stage note for the input list (optional).",
      "hpf": 110,                     // display Hz
      "lpf": 15000,                   // display Hz, or null for OFF
      "bands": [
        { "b": 4, "gain": -3, "freq": 7500, "q": 3.0, "type": "BELL",
          "deq": { "thr": -18, "atk_ms": 3, "rel_ms": 120 } },  // deq optional -> dynamic band
        { "b": 3, "gain": -3, "freq": 1600, "q": 1.4, "type": "BELL", "deq": null },
        { "b": 2, "gain": -4, "freq": 300,  "q": 2.0, "type": "BELL", "deq": null }
        // b1 omitted -> flat
      ],
      "mic_notes": "What the capsule brings (so you don't fight or double it).",
      "eq_summary": "The WHY — the reasoning Brian reads. This is the point of the deep build."
    }
  ]
}
```

Notes:
- `research` is the readable research section (2026-07-27). One `units` row per instrument × mic
  unit, in channel order — the same units the Part II pass ran. The validator warns on a missing
  verdict word, a missing external source, and any TRACE layer left blank.
- `mic_notes` + `eq_summary` carry the reasoning into both the Show Packet (per-channel) and the
  Rationale PDF. Write them like Brian talks — direct, the *why*, not just the number.
- `changes` is the Rationale's amber "what changed and why" box. Populate it with every divergence
  from the KB default / prior rev. If nothing changed, omit it.
- The `.md` `build_packet.py` writes is the patcher's input; don't hand the patcher a separate
  hand-made `.md`.
