# EQ Approach by Instrument — Brian Lloyd

*What to think about per instrument/source. No default values — settings are driven by genre, mic choice, and inline channel notes from the input list. Use this to inform reasoning and Quick Summary prose.*  
*Last updated: May 2026*

---

## Ground Rules

- **Vocals: cuts only, no boosts.** Feedback control. Aggressive. No exceptions.
- **Classical/acoustic shows: conservative cuts-only across the board.** Trust the mic; don't shape what isn't broken.
- **Genre drives everything.** Tonal targets, dynamics aggressiveness, reverb character — all come from the genre/influences description on the input list. These notes are factors to consider, not targets to hit.
- **Mic choice changes the approach.** A Beta 52 inside a kick needs different treatment than an Earthworks DM6. A DPA 4099 on strings is not the same as a Countryman B3. Note the mic, consider its response curve.

---

## Drums

### Kick
**What to address:** Low-end buildup vs. attack/click balance. The fundamental and the beater are often at odds — EQ to serve the genre (more thump for blues/soul, more click for rock, more natural for jazz/acoustic).  
**At Memo:** Standing waves at 63/125/200/250 Hz interact with kick low-end. Any boost in that range needs to be weighed against the room.  
**Dynamics:** Gate is standard. Tight threshold, fast attack, release tuned to tempo so it doesn't chop sustained ring on a jazz or acoustic show.  
**Mic note:** Two-mic kick (Beta 52 + Beta 91 or Earthworks DM6) — the inside dynamic handles body, the boundary/condenser handles attack. EQ them differently and blend.

### Snare
**What to address:** Crack vs. body vs. ring. Genre determines which you're after. A dense gospel choir mix wants crack that cuts through; a Celtic folk set wants body and warmth with minimal snap.  
**Dynamics:** Gate threshold set to reject hi-hat bleed and kick bleed without chopping ghost notes. Release depends on tempo and feel.

### Hi-Hat
**What to address:** Harshness and bleed. The hat mic is almost always fighting bleed from the snare and overhead wash. HPF aggressively, manage the top end for the genre.  
**Dynamics:** Hard gate usually chops cymbal wash in a way that sounds wrong. Prefer a light ducker on acoustic-forward shows — it pulls the hat back during silences without hard-gating the tail.

### Overheads / Cymbals
**True overhead position:** Natural cymbal air is present. HPF to taste, top-end EQ is subtle. Gate is fine if the kit allows it.  
**Underhat / underhead (broadcast restriction):** Position is below the cymbals — natural air is reduced, bleed profile is different, and the HPF needs to go higher. Compensate the lost top end carefully. A ducker is almost always the right dynamics choice here — a gate chops wash that's musical. Polarity check is required. Reverb send offset (+2 to +3 dB) compensates for the reduced natural room feel.  
**DEQ on underhat Band3:** Not automatic — assess per show. If the hat pattern is consistent and predictable, a static cut is cleaner. If playing is variable, DEQ helps.  
**Never carry cymbal processing from one show to the next.** Read the input list every time.

### Toms
**What to address:** Mud in the low-mids, ring control. Gate release must match the feel of the kit — a slow-decay floor tom in a ballad should not be gated with the same release as a snappy funk kit.

---

## Bass

**What to address:** Fundamental vs. upper harmonic content. The fundamental sits in a range that interacts with the kick and the room. Upper harmonics give the bass definition on small speakers and for audience members far from the subs.  
**At Memo:** 125 Hz standing wave is right in the bass fundamental range — be aware.  
**Dynamics:** Gentle compression to control peaks and even out note-to-note level variation. Bass players vary more than they think they do.

---

## Guitar

### Electric (SM57 / R-121 blend at Memo)
**What to address:** Mud around 300–500 Hz is almost always there. Harshness in the upper mids varies by amp, speaker, and how hard the player is hitting.  
**Blend note (Memo CH 13/15):** Polarity check before advancing the R-121. It should make the tone fuller in mono — if it gets thinner, flip polarity. Check 300–500 Hz buildup on the bus after the blend is set. ⚠ No phantom on CH 15.

### Acoustic
**What to address:** Proximity effect if close-miked, body resonance, string noise. Acoustic-forward genres want the natural character preserved — cuts only, and conservative ones at that.

---

## Keys / Synth
**What to address:** Depends entirely on what the keys are doing. Pad sounds need different treatment than piano sounds than synth bass. Read the show context.  
**DI note:** Keys direct are clean sources — the EQ work is mostly about carving space in the mix, not correcting a mic.

---

## Vocals

**Cuts only. No boosts. Aggressive. This is a feedback control requirement, not a stylistic preference.**

**What to address:**  
- Proximity effect — HPF is your first and most important move. More aggressive than you might be on an instrument channel.  
- Low-mid boxiness (300–600 Hz range) — cut to taste; this is where feedback most often starts building.  
- Upper-mid harshness (2–4 kHz) — feedback zone on handheld dynamics; cut to reduce feedback headroom before it becomes a problem.  
- DEQ on problem resonances — an effective tool for feedback prevention on vocal channels where a specific frequency is the issue.  

**Dynamics:** Compression evening out the vocal; gate or expander set to open cleanly on breath and close on silence. Release long enough that it doesn't pump on sustained notes.  

**Choir/group vocals:** Same cuts-only rule. Upper-mid nasality from massed voices is usually the first thing to address. Gate typically off — the group never goes fully silent the way a solo vocalist does.  

**Condenser vocal mics:** Less proximity effect than dynamics, but more sensitive to room reflections and feedback. The cuts-only rule applies with the same aggression.

---

## Piano

### Lid open
**What to address:** Natural and usually good. Main job is carving space and managing low-mid buildup without losing the instrument's character. Classical context: cuts-only, trust the mic.

### Lid closed / short stick (mics inside)
**What to address:** Low-mid buildup from internal reflections. High-frequency loss from the closed lid — this is one of the rare cases where a careful high-shelf lift may be warranted, because the lid is physically blocking top-end energy, not a mix decision. Note this explicitly in the Quick Summary.  
**At Greaves:** Two 9ft Steinways — confirm which one and mic positions before making EQ decisions.

---

## Brass / Horns

**What to address:** Harshness in the upper mids, low-mid buildup depending on directional pattern and distance. Compression with a fast attack — brass transients are aggressive and will jump above the mix without it.  
**AKG C422 in XY:** Stereo pair in one body — polarity check L vs R capsule, verify mono summing is clean before advancing levels.

---

## Strings (Amplified)

**What to address:** Bowing harshness in the upper mids, proximity effects from clip-ons, bleed from adjacent instruments.  
**Dynamics:** Compression slow and gentle — bow attacks are part of the articulation. Gate usually off; the attack is too fast and the gate will chop.  
**Clip-on note (DPA 4099 / Countryman B3):** These mics are designed for the instrument and usually need less correction than you'd expect. Don't over-EQ.

---

## Woodwinds

### Flute
**What to address:** High HPF (the fundamental is high and there's no useful content below it). Breath noise in the high frequencies on close-miked setups. Classical context: cuts-only.

### Clarinet / Saxophone
**What to address:** Upper-mid harshness, body resonance. Sax in a dense mix needs upper harmonics to cut through; in a quiet acoustic setting, pull it back.

### Uilleann Pipes (MKH 40 at Memo)
**What to address:** Chanter brightness vs. bag/bellows noise. The pipes have a wide dynamic range between the chanter melody and the drones — compression helps even this out without killing the expressiveness.

---

## Bodhran (Memo)

**What to address:** The highest-risk channel at Memo. The 200 Hz standing wave interacts directly with the bodhran's fundamental. Low-mid treatment is aggressive here — more so than at any other venue.  
**DEQ on Band 3:** Usually active for bodhran at Memo because the resonance interaction with the room is severe enough that a static cut doesn't fully solve it. Assess per show.

---

## Crowd / Room Mics (Memo)

Fixed EQ — see `venue-notes.md` for the locked Memo crowd mic settings. These don't change show to show.

---

## Genre Modifiers

These shift the approach across all channels:

**Acoustic-forward (Celtic, classical, chamber, folk):** Lighter touch on everything. Cuts only, smaller amounts. Let the mic do the work. Slower gate releases, duckers over gates on cymbals. Reverb: shorter, more natural.

**Dense / loud (gospel choir, rock, R&B):** More aggressive EQ to create separation. Faster comp, tighter gates. Feedback headroom is tighter with more open mics — cuts-only on vocals is non-negotiable.

**Jazz:** Depends on context. Small ensemble at Memo = acoustic-forward rules. Big band with loud brass = treat like a dense mix.

**Classical recording (not live):** Cuts only across the board. The mic placement is doing the work — EQ is correction, not shaping. Trust what you hear.
