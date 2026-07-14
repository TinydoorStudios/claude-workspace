# Deep-research workflow — making the research real

The failure mode this skill exists to prevent: a finished packet appearing **instantly**, which
means the research didn't run and the output silently inherited a KB/template default. (Real
example: a kick channel's notes referenced a "D6/Beta 91A blend" on a show that had no D6 — a KB
template bled in.) Speed is the tell. A multi-channel deep build is minutes of visible searching,
not one beat.

## Make it visible
Run the searches as actual tool calls Brian can see. Don't summarize from memory. If you already
know the answer cold from a prior show, the KB is the right source — but say so; don't fake a search.

## Per-source order (each step narrows the last)
Order of importance = order of process (locked 2026-07-05): instrument → mic → genre → venue.
The room bends hardest in dB but ranks last in authority — it trims and vetoes, never rewrites
the instrument + mic foundation.

1. **Instrument/source** — be specific (electric cab cranked vs. acoustic fingerstyle).
2. **Mic on it** — research the actual capsule's behavior. Self-present mics already bring
   presence/scoop/air; note that so you *ease* boosts instead of stacking them. Don't guess the mic.
   **Then the locker loop** (EQ method Step 2b in SKILL.md): sweep `mic-library.md` for an owned mic that
   concretely beats the specified one for this show — one alternative max, one-line why, never on
   TOUR gear, batched to the review stop. EQ still targets the specified mic.
3. **Forum/web** — Pro Sound Web, Gearspace, Sound on Sound, maker docs. Cross-check against the KB
   (`eq-starting-points`, `mic-library`). When web and KB agree, you're solid; when they disagree,
   STOP and ask. Dedupe first: research once per unique instrument × mic unit, fan out to the
   channels that share it.
4. **Genre + artist** — tonal target + how aggressive. Pop-soul/classical/acoustic = restraint;
   most else = aggressive, whole-dB. The artist_profile refines the generic genre read per channel
   (vocal character, tone references, density, production style) and wins where they differ.
5. **Room** — applied last. Memo standing waves (63/125/200/250–315). FSQ/outdoor: no room
   gain, low end + HF dissipate, façade slap but no tail → support lows + presence, ease the deep
   low-mid cuts a room would need.

## Mine the notes — they are deliberate research signals
Brian types details into a channel's `notes` (and the show-level `show_notes`) specifically so the
deep build will pick them up. Treat every note as a possible research trigger, not a label. Read
them first, extract the signals, research each, and let them bend the EQ.

| Note says… | Research | Likely EQ/processing effect |
|---|---|---|
| "Ampeg SVT + 8x10, flatwounds" | SVT voicing + flatwound character | Dark, mid-forward; ease the top, lean the low-mid "wool" |
| "Vox AC30, top boost" | AC30 voicing | Chimey upper-mids — tame 2–4k harshness |
| "Fender Twin, edge of breakup" | Twin voicing | Scooped mids, bright top — watch 3–4k ice |
| "Fredman on the cab" | Fredman = two angled 57s | Phase/comb management; scooped highs — align polarity |
| "mid-side overheads" | M-S decode/width | Phase + width; EQ the M and S sensibly, check mono |
| "5-string, low B" | extended low end | Protect/clear sub; HPF lower, watch 30–50 |
| "no gate" / "broadcast feed" | artist/engineer constraint | Don't gate; broadcast = underheads not overheads |
| "lead line" / "comping behind horns" | role in the mix | Feature = carve space for it; support = tuck the presence, deeper separation cuts |

If a note names gear or a technique you don't know cold, **search it** (web + KB). If it stays
ambiguous or you can't source it, **stop and ask** — never drop a note on the floor. Whatever a note
changes must show up in that channel's `mic_notes` / `eq_summary`, and in `changes` if it moved you
off the KB default.

## Beyond the input list — the other evidence channels
- **Live footage + setlists** (step 2): recent YouTube live videos and setlist.fm tell you the
  real arrangement, stage volume, and lineup — press copy doesn't. Mismatches vs. the input list
  go in the question round.
- **Prior verified shows**: the shows index / `active-projects.md` for the same artist, the same
  weekly series, or a twin act at this venue. Brian's verified past build is his ground truth —
  evidence beside the fresh research, never a substitute for it.
- **Tech rider / stage plot**: densest single input when it exists — ask for it.
- **Show-day weather** (outdoor venues): wind, temp/RH, rain window → windscreens, HF air loss,
  contingency. Goes in `room_context`.

## Two-mic sources
Kick (boundary + dynamic), bass (DI + cab), guitar (dark + bright). Decide which mic owns which
job, keep them from doubling the same band, and always note: same VCA, pan together, polarity
check (sum mono, flip if thinner), watch the bus build at 300–500.

## Capture the WHY
Every channel needs `mic_notes` (what the capsule brings) and `eq_summary` (why these moves, in
plain talk). Every divergence from the KB default goes in `changes`. This is how the Rationale PDF
teaches — it's not decoration, it's the deliverable.

## Stop-and-ask triggers
Unknown artist/genre · mic or instrument missing · web vs KB conflict · a value you can't source ·
a move that fights a known room problem · a template-baseline override (e.g. FSQ vocal feedback
notch). A clean "here's what I know, here's the fork, which way?" always beats a confident guess.

**Batch the round:** collect every trigger during the plan pass (dedupe + locker + note mining)
and ask them all — with the locker alternatives — in ONE message before committing any EQ. Then
build straight through; stop mid-build only for a new fork the scan missed.

## Known failure modes — recognize and stop (catalog added 2026-07-12)

- **The memory search.** Writing "forums consistently recommend…" when no search ran this
  session. If no tool call happened, no research happened.
- **The false-agreement paraphrase.** Softening a web↔KB conflict into "broadly consistent."
  The one-word AGREE/DISAGREE/THIN verdict exists to kill this — name both sides' numbers first.
- **The confident mic guess.** An unrecognized shorthand or missing mic resolved by assumption.
  Always a stop-and-ask — an unsure answer is ~3× more damaging than a pause.
- **The template bleed.** A value or note referencing gear this show doesn't have (the D6/91A
  blend on a show with no D6). If it wasn't researched this session, it doesn't get written.
- **The vanishing constraint.** A half-dB, a vocal boost, or a high shelf appearing deep into a
  long build. This is why the constraint card is re-read before the round and before the spec.
- **The uniform section.** Sectional separation stated in prose, absent from the numbers.
- **The question-round collapse.** Zero questions (gaps papered over) or fifteen trivial ones
  (judgment offloaded). Few, sharp, genuinely-forked, each with your read attached.
- **The polite outdoor cut.** −4 at FSQ. Torn between two depths outdoors → take the deeper.
