# Plan — Back to Black: The Music of Amy Winehouse
**Memorial Hall · Thursday 2026-07-16 · 8:00 PM · DiGiCo Q225 (house)**

Sources this pass: memorialhallotr.com show page · nightowlshows.com · MusicRadar "The making of
Back to Black" (Tom Elmhirst / Mark Ronson) · Billboard "It Ain't Retro" (Dap-Kings) ·
Wikipedia *Back to Black* · Uncut "The Making of Back to Black".

---

## Artist profile

**Not a band tribute — a produced theatre show.** Reine Beau (UK) fronting the Night Owl Shows
band, produced by Night Owl Shows. Their trademark is the **"show-umentary" format**: live music
interleaved with documentary-style storytelling about Amy's career. 25+ international awards,
Edinburgh Fringe pedigree, 5-star reviews. Confirmed setlist material: *Back to Black*, *Valerie*,
*Rehab*, *Me & Mr Jones*, *Love Is a Losing Game*, *Monkey Man*.

**That setlist spans three sonic worlds, and the show is explicitly built on the third:**
- **Back to Black album (2006)** — Mark Ronson + the Dap-Kings at Daptone, Brooklyn. 60s
  girl-group / "synthetic Motown backdrop," Phil Spector influence.
- **Frank (2003)** — Salaam Remi, jazz-infused, more acoustic and conversational.
- **The influences** — the venue page says the show explores "the influences that shaped her own
  writing": jazz standards, 60s girl groups, ska/rocksteady (*Monkey Man* is Toots & the Maytals).

Night Owl's own copy: "the raw honesty, **jazz-infused sound**, and magnetic spirit." So this is
NOT a one-note Dap-Kings soul revue. It swings between jazz-club intimacy and Motown thump, and
the storytelling means **long spoken passages between songs.**

### The production reference — and why it inverts the genre default

The single most load-bearing fact found, mix engineer **Tom Elmhirst** on the Back to Black
sessions (MusicRadar):

> "The drums were recorded with one microphone, and there's lots of spill between the
> instruments, which was great."

Drums, piano, guitar and bass were tracked **together in one room**, to 1" 16-track tape, through
a Neve. Daptone ran a strict no-Pro-Tools ethos. **The bleed IS the record.** The Back to Black
drum sound is mono, dark, midrange-forward, room-glued — the opposite of a modern separated kit.

**This is where the artist profile outranks the generic genre read, and it matters:** the generic
"dense soul/R&B" modifier in the KB says *more aggressive EQ for separation, faster comp, tighter
gates*. The Amy reference says the opposite — a hi-fi, hard-gated, surgically separated 8-mic kit
is exactly wrong for this material. We have an all-Earthworks kit (flat, fast, honest, hears
everything) pointed at a maple Gretsch. The job is to make eight flat condensers read as **one
dark drum kit in a room**, not to win a separation contest. Gate philosophy follows: bleed lives.

Ronson on effects: **"A little bit of spring or plate reverb goes a very long way"** — and he
"caked the tambourine in reverb." Plate/spring is the reverb reference, not a hall.

**Consequence for the room:** Memo's ~1.6 s RT60 is already doing Spector's job for free. Verb
goes short and plate-flavored, decays pulled well back from factory.

---

## Unit table (dedupe: 24 show channels → 13 unique units)

| # | Unit | Channels | Notes / flags |
|---|---|---|---|
| U01 | Kick × Earthworks DM6 | 1 | Gretsch 18"D×22"W maple. Memo's highest-risk channel (63/125 Hz). |
| U02 | Snare × Lauten LS-408 | 2 | **TWO snares in backline — which?** Mic is switchable (HPF/LPF). **Locker flag.** |
| U03 | Hat × Earthworks SR25 | 3 | |
| U04 | Toms × Earthworks DM17 | 4, 5, 6 | 3 ch, one unit, voiced by size. **Ch 6 mislabeled — see below.** |
| U05 | OH × Earthworks SR20sp G2 | 7, 8 | Stereo pair. Carries the kit under the one-mic reference. |
| U06 | **Bass × RNDI + MD 421-U** | 9, 10 | **TWO-MIC.** Aguilar DB751 + DB410. Lane split required. |
| U07 | **Elec Gtr × SM57 + R-121** | 11, 12 | **TWO-MIC.** Fender Blues Deluxe 40W. **⚠ CH 12 RIBBON — NO 48V.** |
| U08 | Acoustic Gtr × Radial J48 | 13 | DI'd — piezo quack 1.5–2 kHz is the primary target. |
| U09 | Keys × RNDI ×2 | 14, 15 | **Keyboard NOT in backline — artist-provided, model unknown.** |
| U10 | Lead Vocal × Beta 58A | 16 | Reine Beau. Cuts only. |
| U11 | BGV × Beta 58A | 17, 18 | **Section — must be slotted in the numbers, not the prose.** |
| U12 | Playback × XLR | 20 | **Show-umentary narration? Or tracks/horns? Fork.** |
| U13 | Crowd/Room × AKG C422 | 23, 24, 31, 32 | **CONFLICTS WITH THE LOCKED MEMO CROWD RIG. Fork.** |
| — | TB × Beta 58A | 19 | Talkback — utility, not a show channel, no EQ. |

---

## Mined notes — every one gets an answer

| Source | Note | What it changes |
|---|---|---|
| xlsx ch 11/12 | "57/121 Blend" | Two-mic lane split; polarity check; **NO 48V on 12**. Memo's standard AxeMount rig lives on CH 13/15 — this show puts it on **11/12**. Input list wins; the venue KB's channel numbers do not. |
| xlsx ch 23/24 | "Stereo Channel" | C422 = XY, one body, two capsules → 2 ch. Polarity-check L vs R, verify mono sum. |
| Quote | Gretsch USA Custom **Maple**, Turquoise Glass | Maple = warm, round, strong fundamental. Suits the dark Daptone reference — don't fight it bright. |
| Quote | Kick **18"D × 22"W** | Shallow-ish 22" — punchy, not a cavernous 24". Fundamental lands near Memo's 63 Hz node. |
| Quote | Toms **10"**, **12"**, **14"D×16"W + 3 floor tom legs** | **The 16" is a FLOOR tom, not "Rack 3."** The input list's ch 6 label is wrong. 10/12 rack + 16 floor. |
| Quote | **Gretsch maple 5.5×14 snare AND Ludwig Supraphonic aluminum 5×14** | Two snares, ONE snare channel. The Supraphonic is *the* Motown/soul snare — Ludwig alum is all over that era. Strong read, but it's a fork. **ASK.** |
| Quote | **Fender Blues Deluxe 40W** (1×12 tube combo) | Bright, chimey Fender clean, tube breakup when pushed. The R-121 is doing real work taming that top. |
| Quote | **Aguilar DB751 + DB410** (4×10) | Modern hi-fi, articulate, extended — the *opposite* of the flatwound/Ampeg tone the Amy record is built on. The 421 is where the vintage weight comes from. |
| Quote | **Keyboard: stand + bench only, $0.00** | No keyboard supplied. Artist brings it. Rhodes? Wurli? Nord? Piano patch? Changes 14/15 entirely. **ASK.** |
| Quote | 2× Yamaha FP9500C **Single** kick pedals | Single pedal — no double-kick. (Second is a spare.) |
| Quote | Spare heads: kick batter, snare top+bottom | Load-in note only. |
| Web | "show-umentary" — storytelling between songs | Ch 20 may be **speech**, and intelligibility becomes its whole job. **ASK.** |
| Web | Setlist has *Rehab*, *Valerie*, *Monkey Man*, *Back to Black* | All horn-forward records. **There are no horn channels on this list.** Horns are on tracks, replaced by keys, or dropped. **ASK — ties directly to ch 20.** |
| Web | Elmhirst: one mic on drums, spill "was great" | Inverts the dense-genre default. Bleed lives; kit reads as one instrument; gates loose or off. |
| Web | Ronson: "a little bit of spring or plate goes a very long way" | Reverb selection → plate/spring character, short, well under factory decay. |

---

## Carried flags
None — new show, no prior rev, no prior Memo Winehouse/soul-tribute show in `active-projects.md`
or the shows index. Nearest relative is **FSQ 2026-06-26 Izzy Escobar** (pop-soul, described in
the KB as "Winehouse grit meets Adele power") — different room, different genre weight, outdoor
aggression rules. Read for reference, **not** carried in as evidence.

---

## Questions collected for the single batched round

1. **The crowd rig (23/24 + 31/32).** The list specifies C422 for Audience L/R *and* Room L/R —
   two C422 bodies — and drops the locked Memo rig (OM1 / Deity S2 / CM4) entirely.
2. **Lauten LS-408.** KB gallery renders it with a faded ring = *reference, not in the locker*,
   but the show's own Mic Inventory sheet lists it as owned/Standalone. Direct KB↔source conflict.
3. **Which snare** — Gretsch maple or Ludwig Supraphonic (or a swap mid-set)?
4. **What keyboard** — not in the backline, and 14/15's EQ depends entirely on the answer.
5. **Ch 20 Playback** — narration, tracks/horns, or both? Mono or stereo?
6. **Ch 6 label** — the backline says the third tom is a 16" floor tom, not "Rack 3."

Answers → `decisions` in the spec. Nothing commits before the round.
