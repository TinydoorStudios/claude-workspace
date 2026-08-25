# Unit 11 — Bass cabinet × Shure PG52 · CH 12

INSTRUMENT   The bass player's cabinet, close-miked. Same instrument as ch 11, different capture.
             Its job in THIS mix is the low body a dance crowd feels — the part the 8× KS21
             delayed arch actually moves air with — plus whatever grit and compression the amp
             adds that a line-level out never carries.
             **Channel repurposed this week** — fader 12 was "Bass Synth" on a J48 in rev 1. It is
             now a mic'd cab, so nothing carries over. **Two-mic (mic + DI) source with CH 11.**

MIC          Shure PG52. Cardioid dynamic, **30 Hz–13 kHz**, 1.8 mV/Pa, neodymium, internal shock
             mount, 470 g. Discontinued (superseded by the PGA52). No phantom, no switches.
             Short stand (a cab mic takes a Short stand, not a clip).

SEARCHES     1. `Shure PG52 bass cabinet mic frequency response 60-100Hz hump dip 200-800Hz rise
                4-5kHz rolloff 10kHz`
             2. RecordingHacks PG52 profile (fetched directly) + Shure/Sweetwater PGA52 spec and
                review copy (the PG52's direct successor) + TalkBass, *Shure PG-52 for miking bass
                amp?*

CAPSULE FACT **30 Hz–13 kHz, cardioid, 1.8 mV/Pa** (RecordingHacks PG52 profile, fetched today) —
             the 13 kHz upper limit is the externally sourced roll-off point. On curve SHAPE, the
             PG52's own chart is published only as an image, so the corroboration comes from its
             direct successor: Shure/Sweetwater describe the **PGA52** as having "a slight presence
             peak in the upper mids to capture the click of the kick beater and **the snap attack of
             a bass string**, with a **scoop in the midsection** and **not a lot of upper top
             end**" (PGA52: 50 Hz–12 kHz, −55 dBV/Pa, 150 Ω).

WEB SAYS     Two useful things. First, Shure's own product copy names **close-miked bass amps** as
             an intended application for this cartridge — this is not an off-label use, and
             TalkBass has a dedicated thread on exactly this pairing. Second, the successor's
             published description independently confirms the three features that drive this
             channel's numbers: a **midsection scoop**, an **upper-mid presence peak**, and a
             **limited top**.

KB SAYS      mic-library: "Cardioid dynamic, 30 Hz–13 kHz, 300 Ω, −55 dBV/Pa, neodymium, internal
             shock mount, 470 g. Published curve humps 60–100 Hz, dips broadly through
             200–800 Hz, rises at 4–5 kHz, then rolls off hard above 10 kHz. Sold as a kick mic and
             a step below a Beta 52 there — but the community rates it well above its price on
             BASS CABINETS, where that exact curve is the right shape. Weakness: less detailed and
             open than a Beta 52; lacks snap on toms." Bias: **never boost the 60–100 Hz hump — own
             the low end by letting it through; never cut into the 200–800 Hz dip (sit a box cut at
             ~160 Hz instead); ease off presence ~4500 Hz.**

VERDICT      **AGREE.** Honest note on sourcing: the fine dB values for the PG52's hump and dip
             remain KB-sourced from Shure's published PG52 curve — today's pass could not retrieve
             that chart as data. But the SHAPE is externally corroborated through the PGA52's
             published description (midsection scoop + upper-mid presence + limited top), the range
             figures agree across sources, and Shure independently confirms the bass-cab
             application. Nothing contradicts the KB row, and the research floor is met by the
             13 kHz roll-off point and the successor's documented voicing. Not THIN — the two sides
             describe the same curve from different angles.

LOCKER       Silent pass — first-call match, and emphatically so. Both mic-library ("**Bass
             cabinet** — the job it's genuinely good at") and the root CLAUDE.md mic table
             ("**Bass cabinet** (its real strength)") name this exact pairing as the PG52's best
             use. There is no alternative to offer that wins on a nameable margin for this source.

GENRE BEND   Funk/Motown bass wants weight that stays musical — a note, not a boom. The PG52's
             published hump sits at 60–100 Hz, which is where a 4-string's low register lives, so
             the genre's ask is served by the capsule rather than by the desk. Artist layer:
             programmed low end already occupies the sub region via the Track channel, so this
             channel takes the 60–100 Hz band and deliberately claims nothing below it.

VENUE BEND   FSQ outdoor. The box cut runs at FSQ depth and sits at **160 Hz** — not at the usual
             300–500 — because 200–800 Hz is inside the capsule's own broad dip (see gate check).
             HPF at **35**, the lowest on this show: ch 12 is the designated bottom of the bass
             lane, so it is the one channel allowed to reach. Weather layer: **no change** — the
             capsule stops at 13 kHz and carries "not a lot of upper top end," so dry-air HF loss
             has nothing to act on here.

DRAFT BANDS  HPF 35 · LPF 8000
             B4  −4 | 4500 | 1.5 | BELL
             B3  FLAT
             B2  −6 |  160 | 1.8 | BELL
             B1  FLAT

GATE CHECK   **No boosts on this channel — nothing to permit.** All three of the KB's bias
             instructions are honoured literally, and each is a refused reflex:
             - **B1 FLAT — the low end is claimed by letting the hump through, not by boosting it.**
               The published curve humps **60–100 Hz**; a low boost there stacks on voiced response
               and turns weight into boom on a plaza. Gain and placement own the bottom.
             - **B3 FLAT — the reverse gate.** The capsule dips broadly through **200–800 Hz**. The
               FSQ outdoor override would normally push a box/mud cut in that span to −7 or −8;
               doing it here would double-dip a hole the mic already dug. So the box cut moves DOWN
               to 160 Hz, exactly where the KB says to sit it, and that band is B2.
             - **B4 −4 @ 4500 is a trim on the documented presence rise** (KB: rises at 4–5 kHz;
               PGA52 copy: "slight presence peak in the upper mids… snap attack of a bass string").
               It also de-stacks from ch 11, which trims at 5000 — offset frequencies, and no boost
               on either leg.
             - LPF 8000 is housekeeping on a capsule that rolls off hard above 10 kHz anyway; its
               real value is rejecting the cymbal and snare bleed a stage-level cab mic collects.

TWO-MIC LANES (restated from unit 10, held identical)
             CH 11 (post-EQ DI)  = DEFINITION / TOP. HPF 50 · trims at 5000 and 2000 · 250 mud cut.
             CH 12 (PG52 on cab) = LOW BODY / BOTTOM. HPF 35 · B1 flat (baked hump) · 160 box cut ·
                                   B3 flat (baked dip).
             Shared zones: 4–5 kHz (offset trims, no boosts) · 60–100 Hz (ch 12 owns) ·
             200–800 Hz (ch 11 cuts at 250, ch 12 leaves alone — capsule-driven, not arbitrary).
             ⚠ **Polarity-check in mono at soundcheck; flip ch 12 if the sum thins.**

QUESTIONS    None.

TRACE        base(bass cabinet close-miked — 200–800 Hz box is the usual target, but RecordingHacks
             30 Hz–13 kHz plus the PGA52's documented midsection scoop and upper-mid presence peak
             move both the cut and the trim off their default frequencies) ·
             equip(no cab model, driver count or string type notated — no rig-driven bend beyond the
             mic itself; if the band names an 8×10 or flatwounds at load-in, revisit 160) ·
             genre(funk/Motown wants weight that stays a note — served by the capsule's 60–100 Hz
             hump rather than by the desk) ·
             artist(programmed low end in the Track channel — ch 12 takes 60–100 and claims nothing
             below it) ·
             venue(FSQ outdoor: box cut at FSQ depth but MOVED to 160 to stay out of the capsule's
             200–800 dip; HPF 35, the lowest on the show, because this is the designated bottom;
             dry air = no change on a 13 kHz-limited capsule)
