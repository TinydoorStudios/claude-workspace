# Unit 04 — Toms × Earthworks DM17 (ch 4, 5, 6)

**INSTRUMENT** — Gretsch USA Custom **maple**, three toms. **The backline quote corrects the input
list here:**

| Ch | List says | Backline quote says | Fundamental (approx) |
|---|---|---|---|
| 4 | "Rack 1" | Tom **7"D × 10"W** | ~180–200 Hz |
| 5 | "Rack 2" | Tom **8"D × 12"W** | ~130–150 Hz |
| 6 | **"Rack 3"** | Tom **14"D × 16"W + 3 Gretsch floor tom legs** | ~70–90 Hz |

**Ch 6 is a FLOOR TOM, not a third rack tom** — the quote lists floor tom legs against it, and
there are only two DW 9900 rack mounts for the 10" and 12". Label fix flagged.

Role in THIS band: fills and turnarounds, not a feature. Sparse. Maple = warm, round, strong
fundamental, long sustain — which suits the dark reference but fights the room.

**MIC** — Earthworks DM17, RM3 rim mount, from the DK-6 (**×4 in the kit — only 3 used here;**
the spare is the fallback snare mic in Unit 02). Cardioid. No switches. Not a ribbon, not TOUR.

**SEARCHES**
1. `Earthworks SR25 SR20sp Gen 2 DM17 frequency response flat review drum overheads hi-hat live`
2. Direct fetch: earthworksaudio.com/drum-microphones/dm17/ (manufacturer spec + copy)

**CAPSULE FACT** — **20 Hz – 17 kHz** frequency response — Earthworks DM17 product spec. The
**17 kHz ceiling** is the number that matters: it is a documented roll-off point, and it sits
**8 kHz lower than the SR25's 25 kHz** and 3 kHz below the SR20sp's 20 kHz. Also: cardioid ·
**148 dB SPL @ 3% THD** · sensitivity **−51 dBV/Pa (2.8 mV/Pa)** · self-noise **28 dBA**.

**That sensitivity figure is a real finding: at 2.8 mV/Pa the DM17 is ~11 dB less sensitive than
the SR25 (10 mV/Pa) sharing this kit** — a deliberate low-output, high-SPL, tight-pattern design.
Earthworks' framing: *"premium on-axis detail"* with *"superior off-axis rejection,"* giving
condenser capture with *"dynamic microphone-like isolation."* Consequence at the desk: expect
noticeably more gain on 4/5/6 than on 3/7/8, and expect **less bleed** than a condenser label
implies.

**WEB SAYS** — Flat, fast, detailed, high-SPL, tight rejection; a condenser built to behave like a
dynamic. No published peaks, dips or contours — the maker markets accuracy, not voicing.

**KB SAYS** — `mic-library.md`: *"Earthworks DM17 — Flat snare/tom condenser, fast, detailed, high
SPL. Honest. Weakness: needs EQ for character."* EQ tendency: **"apply template as-is
(flat/honest)."**

**VERDICT — AGREE.**
Maker and KB say the same thing in the same words — flat, honest, high SPL, needs EQ for
character. The one thing the KB does not carry is the **17 kHz ceiling**, and that is worth
having: it means the DM17 arrives darker than its kit-mates for free, which on this show is a
gift rather than a limitation.

**LOCKER** — **First-call match, no alternative.** The KB's dynamics table calls the MD 421-U
*"Toms (first choice)"* — but the 421 is committed to the bass cab on ch 10, and swapping it here
would break Unit 06's two-mic plan. Among what's free, the DM17 is already the kit's tom mic, it
is rim-mounted (no stands in a tight 22'3" stage depth), and it keeps all eight drum channels
inside the DK-6/DK-25 family. No nameable win available. Specified mic stands.

**GENRE BEND** — Sparse Motown/soul fills. Dark, round, no modern attack click. Toms are not a
feature of this material, so the job is: let them speak when hit, stay out of the way otherwise,
and never sound like a rock kit. The DM17's 17 kHz ceiling does part of the darkening unasked.

**VENUE BEND — this is the interesting one, and it's why the three channels differ.**
Memo's nodes are **63 / 125 / 200 / 250–315**. Each tom's fundamental lands on a *different* node:

- **10" (ch 4): ~200 Hz → straight onto the 200 Hz node.**
- **12" (ch 5): ~130–150 Hz → straight onto the 125 Hz node.**
- **16" floor (ch 6): ~70–90 Hz → sits between the 63 and 125 nodes; the 63 node booms underneath it.**

So the deepest cut on each channel moves with the drum. Three near-identical tom curves would be
a failed build here — the room makes them genuinely different channels. Indoor depth throughout.

**DRAFT BANDS** (Q225 layout, whole dB, cuts first)

### Ch 4 — 10" rack tom
| Band | Setting | Why |
|---|---|---|
| **HPF** | 90 Hz, 18 dB/oct | Well under a 10"'s ~200 Hz fundamental; removes kick spill and room. |
| **LPF** | 12 kHz, 12 dB/oct | Dark reference. (Capsule already stops at 17 kHz.) |
| **Band 4 (HF)** | OFF | No attack boost — the reference has no modern tom click. |
| **Band 3** | −4 dB @ 400 Hz, Q 1.8, Bell | Shell box / mud. |
| **Band 2** | **−4 dB @ 200 Hz, Q 2.0, Bell** | **Its node.** The 200 Hz standing wave sits on this drum's fundamental. |
| **Band 1 (LF)** | OFF | HPF owns it. |

### Ch 5 — 12" rack tom
| Band | Setting | Why |
|---|---|---|
| **HPF** | 70 Hz, 18 dB/oct | Under a 12"'s ~140 Hz fundamental. |
| **LPF** | 12 kHz, 12 dB/oct | Dark reference. |
| **Band 4 (HF)** | OFF | As above. |
| **Band 3** | −4 dB @ 400 Hz, Q 1.8, Bell | Shell box / mud. |
| **Band 2** | **−4 dB @ 125 Hz, Q 2.0, Bell** | **Its node** — different drum, different collision. |
| **Band 1 (LF)** | OFF | HPF owns it. |

### Ch 6 — 16" floor tom
| Band | Setting | Why |
|---|---|---|
| **HPF** | 50 Hz, 18 dB/oct | Under a 16"'s ~80 Hz fundamental — protects the drum, drops the sub. |
| **LPF** | 10 kHz, 12 dB/oct | Darker still. A floor tom has no business up top on this record. |
| **Band 4 (HF)** | OFF | As above. |
| **Band 3** | −4 dB @ 400 Hz, Q 1.8, Bell | Shell box / mud — the constant across all three. |
| **Band 2** | −3 dB @ 250 Hz, Q 1.8, Bell | Memo's 250–315 node; on a floor tom this is the woof. |
| **Band 1 (LF)** | **−3 dB @ 63 Hz, Q 2.0, Bell** | **Its node** — the 63 Hz wave booming *under* the fundamental, which the HPF's corner at 50 deliberately leaves in place. |

**Zero boosts on all three.**

**GATE CHECK** — No boosts to justify anywhere in this unit. Reverse gate: nothing is a correction
of a baked feature; the DM17 has none published. The 400 Hz cut is shell/room, the low cuts are
nodes, and the LPFs are the artist reference.

**DYNAMICS** — Gates, but the release moves with the drum, per the KB (*"gate release must match
the feel of the kit — a slow-decay floor tom in a ballad should not be gated with the same release
as a snappy funk kit"*). All range-limited, never full mutes — the kit stays glued.

| Ch | Gate |
|---|---|
| 4 (10") | thr −35 dB, **range 20 dB**, atk 1 ms, hold 40 ms, rel 150 ms |
| 5 (12") | thr −35 dB, **range 20 dB**, atk 1 ms, hold 40 ms, rel 200 ms |
| 6 (16" floor) | thr −35 dB, **range 20 dB**, atk 1 ms, hold 60 ms, **rel 400 ms** — the long one. *Back to Black* and *Love Is a Losing Game* are ballads; the floor tom must be allowed to ring out under them. |

**Comp:** Mustard **Blue (Neve)**, 3:1, attack 20 ms, release 150 ms, 2–3 dB GR. Light — these are
fills, not a feature.

**QUESTIONS** — one, and it is a label fix rather than a fork: **ch 6 is the 16" floor tom, not
"Rack 3."** The backline quote is unambiguous (14"D × 16"W plus three floor tom legs, and only two
DW 9900 rack mounts supplied for the 10" and 12"). I have built ch 6 as a floor tom. Confirming so
the Input List ships with the right label.
