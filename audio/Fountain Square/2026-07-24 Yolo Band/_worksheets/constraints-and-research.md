# CMF FSQ triple-build — constraint card + research (shared)

Covers Yolo Band (7/24), Natural Progression (7/25), Nasty Nati Band (7/25).
All three are the same 3CDC FSQ house package; ch 1–16 + 24–32 identical, ch 17–23 differ.

## Constraint card (my words)
- Whole dB only. Cuts before boosts. Subtractive first.
- **Vocals cuts-only, every genre** (feedback, not taste). No boost on any VOCALS band.
- No high-shelf boost band unless asked. HPF/LPF as needed.
- Band order/numbering = console: b1 = LF … b4 = HF. Display high→low.
- **FSQ outdoor: cuts run DEEPER than indoor — −6 to −9 typ, up to −10 on mud/box, tight Q.** No room gain; clarity is the whole game. HPF decisive.
- **FSQ ch 10 = RESERVED SNARE PL8 return. OH is a STEREO pair on fader 9. Never split 9/10.**
  Band sheets list OH on 9+10 → collapse to one stereo ch 9; ch 10 stays the plate return.
- Ribbon = NO 48V (none in this kit — n/a).
- TOUR/artist gear never swapped (none flagged; all house FSQ package).
- Two-mic sources: one signal, each mic owns ONE lane top+bottom, no stacked boosts, polarity check.
- Capsule-voicing gate: state the baked peak before any boost; boost inside a baked peak → trim, not boost.
- Dynamics DOCUMENTED (COMP:/GATE: in notes), NEVER patched to the .ses.
- Reverbs REQUIRED every show (FSQ included): 3 complementary vocal + 1–2 instrument + 1 general,
  Seventh Heaven Pro preset names verbatim, every value anchored to factory.
- Genre = R&B for all three (Brian's call; no artist dig). Nasty Nati = R&B/funk brass band.

## Genre + weather layer
- **R&B/funk (web: masteringthemix, musicguymixing):** bass forward, kick carves for bass, 3k beater
  click, snare snap 3–5k + body 150–250, box 300–600 cut, dynamics SPARINGLY for funk (preserve
  player interaction/pocket). Dense/loud = separation cuts (KB Genre Modifiers).
- **Weather (Open-Meteo, show window 6–10pm):**
  - 7/24 Yolo: 80–84°F, RH 31–35% (DRY), wind 2–7mph, rain ~1–2%. Hot+DRY → HF air-loss over throw;
    PROTECT presence/top, don't over-cut HF.
  - 7/25 NP + Nasty: 77–83°F, RH 43–61% (moderate), wind 4–8mph, rain ~1%. HF carries a touch better;
    don't over-boost top. Both low wind → no windscreen flag.

## Per-unit research (fresh web pass + KB cross-check; VERDICT per unit)
Prior-show ground truth: **Izzy Escobar 2.0 (FSQ, pop-soul/indie-R&B, same house kit)** — Brian's own
reference for nearly every shared channel. Used beside the fresh pass, not instead.

- **Beta 91A kick-in** — boundary click engine, flat, contour cuts 7dB@400 if engaged (assume OFF), picks shell box 300–500. KB+web AGREE. Lane: owns click/top.
- **Audix D6 kick-out** — pre-scooped smiley: +peaks ~63 & ~5k, −15@600. Needs almost no EQ. KB+web AGREE. Lane: owns sub/body. GATE the boost at 5k (baked) — none.
- **Audix i5 snare-top** — +5@150 body, +9@5.5k presence, mids scooped. KB+web AGREE. Trim the 5.5k (baked), snap up at 7k.
- **Sennheiser e604 snare-bottom** (Brian-confirmed) — scooped low-mid, voiced attack, thin lows → ideal wire mic. KB AGREE. HPF high, owns wire snap only.
- **SM81 hat** — ruler flat SDC. AGREE. No HF boost; clear bleed.
- **Audix D2 rack ×2** — +150 body, dip 500–1k, upper-mid lift. AGREE. Trust the capsule.
- **Audix D4 floor** — flat to 63, rise 80, reaches 35. AGREE. Body shelf modest, add 1.8k click.
- **Shure Beta 27 OH pair** — flat 60–3k, baked +2@5.5k & +2@9k, supercardioid, −15 pad (web+KB AGREE). Capsule top already lifted → NO HF boost, tame 9k fizz, clear low wash. Stereo on fader 9.
- **Bass DI + Shure PG52 (two-source, INVERTED vs Izzy):** PG52 is a KICK mic on the bass cab — 30Hz–13k, low thump + slight click bump, no top >13k (web: Shure/Gearspace). So **PG52 owns the sub/body, DI owns definition/mids/top** — de-stack the lows. THIN→resolved by lane split. Polarity check.
- **Sennheiser e609 gtr 1/2** — bright 4–5k presence, edgy 2.5–4k, supercardioid. AGREE. Tame edge, cut box.
- **SM57 gtr 3/4** — presence 3–5k, box 300–500. AGREE. Voiced differently from the e609 gtrs so 4 guitars don't pile in the mids.
- **Beta 58A wireless vox ×4** — two baked peaks ~4k & ~10k, boxy 600, supercard, <500 attenuated (KB+web AGREE). Cut-only + dynamic de-ess on 10k. Overrides FSQ template wireless curve/notch → ring out.
- **SM58 wired vox ×2** — presence 4–6k, box 500. AGREE. Cut-only, supportive.
- **SM57 aux perc ×2** (Brian: generic aux perc) — conservative, light presence + box cut, neutral voicing.
- **AT Pro 35 brass ×5 (Nasty Nati)** — 50Hz–15k, 80Hz rolloff 18dB/oct, 145 SPL, rounded top, presence lift baked, STRONG lows (web: A-T/Thomann/Sweetwater). Section-slotted: sousa@90 low, tenor honk@800, bone bark@1.2k, alto@1.5k, trumpet@2.7k — each horn owns a lane.
- **DJ L/R, Bluetooth, NP Stems, NP Drum Pad** — mastered/pre-voiced playback → near-flat, HPF only (Izzy "Tracks" precedent).

TRACE lines ride each channel's eq_summary in the specs.
