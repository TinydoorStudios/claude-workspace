# Units 18–20 — The four vocals × Shure Beta 58A wireless  (faders 33 / 34 / 35 / 36)

*Written as one document because four voices in one band are a **section**, and the whole point
is that they get slotted against each other. The three research units (female voice, male bass
voice, male upper-range voice) share a capsule and a venue; what differs is the instrument —
the voice.*

INSTRUMENT   Four featured vocalists who front this show and trade leads all night:
             · **Wireless 1 — Aretha** (female). Also the evening's MC per the band's own
               press, so this channel carries speech between songs as well as singing.
             · **Wireless 2 — Heather** (female).
             · **Wireless 3 — Vince** (male, **bass voice** — Brian's note).
             · **Wireless 4 — Markay** (male, **upper range** — Brian's note).
             Vince Stroud and Markay both appear in the band's Usher-tribute lineup, which
             corroborates the assignment.
             **Brian has explicitly authorised EQ on these four** — this is the only reason
             they're built rather than left on the template baseline.

MIC          **Shure Beta 58A** handheld capsules on the FSQ house wireless — the model used on
             the Wls channels of the last several FSQ specs (Yolo Band, Nasty Nati). No 48V,
             no stand (—). Faders 33–36 per the house wireless rule.
             **Locker fork: EXEMPT.** House wireless, not a capsule choice on this show.
             ⚠ **Template override.** The FSQ template ships faders 25–36 with a wireless
             baseline: **HPF 184, B4 −18 @ 5 k Q20 (a fixed feedback notch), B2 −6.3 @ 335.**
             Every band written below replaces it. In particular the HPF 184 is *wrong for
             every one of these four voices* — it sits above a bass singer's entire lower
             octave — and writing B4 removes the 5 kHz notch. **Ring these out at soundcheck.**

SEARCHES     1. `Shure Beta 58A frequency response presence peaks 4kHz 10kHz supercardioid live
                vocal EQ female male R&B`
             2. `vocal fundamental frequency ranges bass baritone tenor soprano alto Hz high
                pass filter live vocals chart`
             3. Cross-read of Shure's Beta 58A spec sheet, the Music On Stage technical
                analysis, the Gearspace user review, and the vocal-range frequency references.

CAPSULE FACT **Two high-frequency presence peaks — one at 4 kHz and one at 10 kHz** — described
             across sources as a pronounced rise through 4–9 kHz, "significantly more aggressive
             than the SM58's gentler presence lift," plus a **gradually falling bass response
             below 500 Hz** that prevents boominess at close range. True supercardioid across
             the frequency range (Shure).

             **Voice-type fundamentals and presence regions** (vocal-range references):

             | Voice | Fundamentals | Presence region |
             |---|---|---|
             | Bass (Vince) | E2–E4, **82–330 Hz** | **1–3 kHz** |
             | Tenor / upper male (Markay) | C3–C5, **130–523 Hz** | **2–5 kHz** |
             | Alto (female) | F3–F5, **175–700 Hz** | **2–5 kHz** |
             | Mezzo (female) | A3–A5, **220–880 Hz** | **2–6 kHz** |

             Live HPF guidance from the same sources: **80–120 Hz for female voices, 60–100 Hz
             for male voices** — i.e. *lower* for men, which is the opposite of what a single
             template HPF can deliver.

WEB SAYS     The Beta 58A's twin peaks are why it cuts through a loud stage, and why it can go
             strident and sibilant when it's pushed. The supercardioid pattern is the gain-
             before-feedback advantage over an SM58 — which is the reason it's the right capsule
             for four open handhelds on an outdoor plaza.

KB SAYS      mic-library: "supercardioid vocal dynamic, 50 Hz–16 kHz, <500 Hz attenuated for
             proximity control, **TWO presence peaks (~4 kHz and ~10 kHz)** — brighter/more bite
             than SM58, tighter pattern, more gain-before-feedback. Weakness: those peaks can
             get strident/sibilant. → ease off presence; tame box ~600 Hz."

VERDICT      **AGREE.** The 4 kHz and 10 kHz peaks, the sub-500 Hz attenuation and the
             supercardioid pattern appear identically on both sides. No conflict.

GENRE BEND   R&B/funk/soul, four voices trading leads over a dense band. The genre wants vocals
             forward, warm in the chest and clean in the top — but the *rule* is that vocals are
             cuts-only in every genre, so "forward" is achieved by removing what's in the way,
             not by boosting. Artist layer: this band backs national R&B and gospel acts; their
             vocalists are trained, loud, and work the mic hard. Expect proximity, expect belt,
             expect the capsule's 4 kHz peak to bite on the big notes.

VENUE BEND   FSQ outdoor is the heaviest filter here. **Five open mics** (these four plus the
             talkback) set the gain-before-feedback ceiling for the whole show, and there's no
             room gain to help. Box/chest cuts run at outdoor depth (−6 to −7). Humidity climbs
             50% → 77% across the set, so the top end will get *more* present as the night goes
             on — which is why every de-ess below is **dynamic**, acting only on peaks, rather
             than a static cut that would be wrong at one end of the night or the other.

## The four-vocal slot map

Cuts-only, so the separation is done entirely with *where* each voice is cut — every band is
placed against that singer's own fundamental and presence region, not copied across:

| | **W1 Aretha** (f, lead/MC) | **W2 Heather** (f) | **W3 Vince** (m, bass) | **W4 Markay** (m, upper) |
|---|---|---|---|---|
| HPF | 130 | 140 | **90** | 110 |
| De-ess (dyn) | −3 @ 10000 | −3 @ 9000 | −2 @ 8500 | −3 @ 9500 |
| Box / chest | −6 @ 600 | −6 @ 550 | **−7 @ 350** | −6 @ 450 |
| Upper-mid | −2 @ 1600 | −3 @ 1800 | −4 @ 700 | −3 @ 1200 |

The HPF row is the whole argument: Vince's fundamentals go down to **82 Hz**, so his filter sits
at 90 while the women's sit at 130 and 140. The template's single HPF 184 would have removed the
bottom of his voice entirely.

The box row follows the same logic — a bass voice's chest build-up sits **lower** (350) than a
tenor's (450) or a woman's (550–600), so the four cuts land in four different places instead of
four copies of "−6 at 600."

The upper-mid row is where Vince's channel diverges most: his presence region is **1–3 kHz**, the
lowest of the four, so his cut is placed at **700 Hz — below it** to protect his intelligibility.
The other three are cut *inside* the 1.2–1.8 kHz nasal zone because their presence regions sit
higher and can afford it.

DRAFT BANDS  **Fader 33 — Wireless 1 / Aretha** (female, lead + MC)
             HPF 130 · LPF 16000
             B4  −3 @ 10000 Q 2.0 BELL  **DEQ** thr −18 atk 3 ms rel 80 ms — dynamic de-ess
             B3  −6 @ 600   Q 2.0 BELL  box — outdoor depth
             B2  −2 @ 1600  Q 1.8 BELL  light nasal; light because she's the lead voice
             B1  FLAT

             **Fader 34 — Wireless 2 / Heather** (female)
             HPF 140 · LPF 16000
             B4  −3 @ 9000  Q 2.0 BELL  **DEQ** thr −18 atk 3 ms rel 80 ms
             B3  −6 @ 550   Q 2.0 BELL  box, its own slot
             B2  −3 @ 1800  Q 1.8 BELL  nasal, its own slot
             B1  FLAT

             **Fader 35 — Wireless 3 / Vince** (male, bass voice)
             HPF 90 · LPF 16000
             B4  −2 @ 8500  Q 2.0 BELL  **DEQ** thr −18 atk 3 ms rel 80 ms — lightest of the four
             B3  −7 @ 350   Q 2.0 BELL  chest build-up — the deepest cut of the four
             B2  −4 @ 700   Q 2.0 BELL  honk, placed BELOW his 1–3 kHz presence region
             B1  FLAT

             **Fader 36 — Wireless 4 / Markay** (male, upper range)
             HPF 110 · LPF 16000
             B4  −3 @ 9500  Q 2.0 BELL  **DEQ** thr −18 atk 3 ms rel 80 ms
             B3  −6 @ 450   Q 2.0 BELL  box, between Vince's and the women's
             B2  −3 @ 1200  Q 1.8 BELL  nasal, its own slot

DYNAMICS     Documented in the .md, **not patched into the .ses** (rule 2026-07-16).
             All four: **Mustard Purple (Optical / LA-2A)**, ratio 3:1, attack 10 ms, release
             150 ms, threshold set for **3–5 dB gain reduction on the belt, none on the verse**.
             Optical rather than FET because these are trained singers with a real dynamic range
             — the point is to catch the top of a phrase, not to flatten the voice. Vince's
             threshold will sit lowest of the four; a bass voice pushes the most average energy.

GATE CHECK   **Zero boosts across all four channels.** Vocals are cuts-only in every genre —
             feedback control, not taste — and this is a five-open-mic outdoor stage where that
             rule earns its keep. Separately, the capsule gate would have blocked the two obvious
             boosts anyway: a presence lift at 4 kHz and an air lift at 10 kHz are **exactly** the
             Beta 58A's two baked peaks. Boosting either would stack a documented peak on
             trained, loud singers. So the top of every one of these channels is a trim.
             **Why the de-ess is dynamic and not static:** the 10 kHz peak only misbehaves on
             sibilants. A static −3 there would dull every held note to fix a problem that lasts
             milliseconds — and with humidity climbing all night, a static value set at 6 pm is
             wrong by 11 pm. The DEQ acts on peaks and leaves the air alone.
             **The 4 kHz peak is deliberately left alone on three of four channels.** It's the
             capsule's intelligibility peak and it's what gets these voices over a 10,000-person
             crowd. Only Aretha's channel touches near it (−2 at 1600 is well below), and that's
             a nasal move, not a presence one.
             **Sectional audit:** four HPFs (90/110/130/140), four box cuts (350/450/550/600),
             four upper-mid cuts (700/1200/1600/1800), four de-ess points (8500/9000/9500/10000).
             No two channels share a single value. Every one traces to a stated voice-type fact.

QUESTIONS    1. Confirm the FSQ house wireless handhelds are still **Beta 58A** capsules.
             2. Acknowledge that the template's wireless baseline (HPF 184 + the −18 @ 5 k
                feedback notch) is being overridden on all four — ring out at soundcheck.
