# Show brief schema — `<Show>.brief.json` (the app's output)

The ShowBuilder app exports **facts only**. It does NOT compute EQ. The deep-build skill reads the
brief, researches the artist + every source (mining the free-text notes), and produces the
deep-research `spec.json` (see `spec-schema.md`), which then drives the whole packet.

Brief → research → `spec.json` → `build_packet.py` + venue patcher → packet. The app never touches
EQ; the skill never re-keys the input list.

```jsonc
{
  "show_name": "Izzy Escobar",
  "artist": "Izzy Escobar",
  "venue": "fsq",
  "venue_label": "Fountain Square (outdoor)",
  "console_label": "DiGiCo Quantum 225",
  "show_date": "2026-06-26",
  "foh_engineer": "Brian Lloyd",
  "mon_engineer": "Sam Carpender",
  "show_time": "9:00pm",
  "rev": "Rev 1.0",

  // Free-text, show-wide. The skill MINES this for research signals (PA, weather/outdoor,
  // set length, artist tonal requests, anything that should factor into the grand scheme).
  "show_notes": "Outdoor, possible wind. Artist wants intimate vocal, minimal verb. 75-min set.",

  "channels": [
    {
      "ch": 13,
      "name": "Guitar 57",
      "instrument": "Electric Gtr",
      "mic": "Shure SM57",
      "section": "GUITAR",
      "phantom": false,
      "ribbon": false,
      "tour": false,     // optional — artist-provided gear; carries through to the ⚑ TOUR flag
      "stand": "DI",
      "patch": "Local 13",

      // Free-text, per channel. The skill MINES this and RESEARCHES what it finds:
      // amp/cab ("Ampeg SVT + 8x10"), miking technique ("Fredman", "mid-side", "57+121 blend"),
      // instrument specifics ("flatwounds", "5-string"), placement, artist requests.
      "notes": "Vox AC30 top boost, 57 + Beta 27 blend, edge-of-breakup rhythm tone"
    }
  ]
}
```

Rules for the app side:
- **No EQ fields.** No `hpf`/`lpf`/`bands`/`mic_notes`/`eq_summary` — those are the skill's output.
- `notes` and `show_notes` are intentionally unconstrained text. Do not validate/strip them — they
  are the research hooks. Round-trip whatever Brian types, verbatim.
- Everything else is the same vocabulary as the input list (full mic names, `Local N` patch,
  stand vocabulary, ribbon → no 48V).
