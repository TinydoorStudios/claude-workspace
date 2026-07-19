# Pre-commit audit — run before writing spec.json, every show build

Answer each line in visible output with the evidence quoted — channel numbers and values, not
"verified" or "all good." An audit that passes without quoting evidence is a failed audit. Fix
what fails, then re-run the failed lines. build_packet.py catches the mechanical subset of this;
the judgment lines (5, 6, 8, 13, 14) are on you.

1. **Whole-dB scan** — any .5 anywhere in any band?
2. **Vocal channels** — any boost? Cuts only, every genre (feedback control, not taste).
3. **High shelf** anywhere without Brian explicitly asking?
4. **Ribbon channels** — NO 48V flag present and red? TOUR flags on all artist-provided gear?
5. **Every boost** — quote the researched capsule fact that clears the voicing gate (no boost
   inside a baked peak; no deep cut inside a baked scoop).
6. **Sections** (horns, BGVs, twin guitars) — quote each member's differing lane values. Three
   near-identical curves under a "slot the section" note = failed build; fix the values or drop
   the claim.
7. **Two-mic pairs** — lane ownership stated in both channels' `mic_notes`, no stacked low boost,
   polarity/mono check planned?
8. **Research floor** — per unit, quote the quantitative capsule fact + named external source that
   rides `research_summary`; confirm the closing reconciliation line ("no web↔KB disagreements" or
   the list) and each unit's one-word AGREE/DISAGREE/THIN verdict.
9. **Venue** — Memo: any boost in 63/125/200/250–315? FSQ/outdoor: are the cuts at outdoor depth
   (−6 to −9), not polite indoor depth? Outdoor: real fetched weather numbers with source named in
   `research_summary`?
10. **Reverbs** — preset names verbatim from the reverb KB, every settings value anchored
    "(factory)" or "(from X factory)", selection justified by THIS band's material?
11. **Reserved faders** — FSQ ch 10 = SNARE PL8 return; OH stereo on fader 9, never split 9/10?
12. **decisions + notes** — every question-round answer recorded in `decisions`? Every mined note
    traceable to a `mic_notes`/`eq_summary`/`changes` entry — nothing dropped on the floor?
13. **eq_summary spot-check** — read three at random; if any would fit a different band's show
    unchanged, it's generic — rewrite it around the channel's role in THIS band.
14. **TRACE lines** — every unit's `research_summary` closes with the five-layer TRACE
    (base(instr+mic) · equip · genre · artist · venue), each layer a value or "no change"; pick
    two at random and check the trace against the channel's actual band values — a trace the
    numbers don't back is a failed line.
