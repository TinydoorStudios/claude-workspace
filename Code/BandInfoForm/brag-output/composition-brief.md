# Hyperframes Composition Brief: 3CDC Band Advance

## Objective
Create a short, polished launch-style brag video for the 3CDC Band Advance system — an internal self-serve show-advancing tool.

## Output
- Composition directory: `brag-output/composition/`
- Rendered video: `brag-output/brag.mp4`
- Format: landscape — 1920x1080
- Duration: ~21 seconds

## Source Material
- Project root: `/Users/brianlloyd/Documents/Claude/Code/BandInfoForm`
- Primary files read: `app/templates/form.html`, `app/templates/dashboard.html`, `app/templates/staff.html`, `app/i18n.py`, `README.md`, `ARCHITECTURE.md`
- Product name: 3CDC Band Advance
- Tagline / strongest claim: "One form. Every venue. Nothing typed twice."
- Key UI to recreate: the dark band-facing form ("Band Advance / Show Details") and the "Band Advance — Live" dashboard cards
- Copy that must appear verbatim:
  - "Band Advance / Show Details"
  - "Submit show details"
  - "Band Advance — Live"
  - "Needs you"
  - "A human approves every send."

## Creative Direction
- Tone preset: polished
- Creative direction: quiet, confident internal-tools product film with a dry wink
- Interpretation: fewer scenes, longer holds, restrained motion; energy from clean sequential reveals and one satisfying cascade, not from speed or flash.
- Angle: The anti-glamour brag — the unsexy back-office grind of advancing every band at every venue, quietly automated end to end. Specificity does the bragging.
- Hook: the real dark form with a cursor clicking "Submit show details," over the line "A band fills out one form."
- Outro / punchline: "3CDC Band Advance — One form. Every venue. Nothing typed twice."
- Avoid: generic SaaS language, abstract filler visuals, unrelated redesign.

## Visual Identity
- Background: #0d1117
- Card: #161b22
- Text: #e6edf3 (muted #8b97a6)
- Accent: #4da3ff · brand navy #1A3A5C · green #3fb950 · required-red #f87171 · hairline #2a323d
- Display font: system sans stack (matches the real app) — -apple-system, "Segoe UI", Arial
- Body font: same system stack
- Visual references: the dark form card, checkbox rows, the venue-color-coded dashboard cards (FSQ blue / WP green), the "Needs you" panel

## Storyboard
Contract: `brag-output/brag-plan.md`.

Scene summary:
1. The form (hook) — 4s — recreate the dark form; cursor clicks "Submit show details"; line "A band fills out one form."
2. The cascade (reveal) — 5.5s — three outputs arrive one by one: day-sheet auto-filled (checkboxes tick), advance email drafted, status log updated live; caption "No one clicked anything."
3. The smart bits (highlights) — 5s — three feature cards: "Knows a returning artist," "Drafts 21 days out. Nudges at 7.," "A human approves every send."
4. The dashboard (result) — 4s — "Band Advance — Live," venue-color-coded show cards, "Needs you" panel pulses.
5. Outro — 2.5s — name lockup + tagline, music fades.

## Audio
- Audio role: warm corporate bed with tasteful, motion-matched UI accents
- Audio arc: low optimistic bed throughout; single click on submit; three restrained switch ticks on the cascade; soft card sounds on features; opens slightly on the dashboard; fades on the lockup
- Music: `assets/music/bed.mp3` (Happy Beats / Business Moves vol-1, ~120 BPM)
- Music treatment: start 0s, sit low (~0.45), gentle fade over the final ~1.5s
- Music cue guidance: vol-1 preset (120 BPM). Strong cues in-window ~16.0/17.5/20.0s; beat grid ~0.5s. Cascade arrivals are the sequential reveal — hold the full set ~1s after the third. Cues are light hints only.
- Audio-reactive treatment: subtle — accent elements may breathe slightly with the bed; no waveform bars.
- Audio-coupled moments:
  - Scene 1 Submit — simulated cursor click (click1.ogg)
  - Scene 2 cascade — three cards one by one (switch1/switch3/switch4.ogg) + checkbox ticks
  - Scene 3 features — sequential card reveal (rollover1/2/5.ogg)
  - Scene 4 dashboard — soft settle (switch7.ogg)
- SFX selection guidance: click for the button; soft switches for card arrivals; keep it sparse and polished.
- SFX analysis guidance: `/Users/brianlloyd/Documents/Claude/.agents/skills/brag/assets/sfx/sfx-analysis.md`
- Exact SFX choice: local `.ogg` files already copied into `assets/sfx/`.
- Audio files: music at `assets/music/bed.mp3`, SFX in `assets/sfx/`.

## Hyperframes Instructions
Single self-contained `index.html`, GSAP root timeline registered on `window.__timelines["main"]`, deterministic only. Show real UI/copy from the project. Keep text readable (hold each line to its floor). Duration 15–25s. `hyperframes check` must pass before render.
