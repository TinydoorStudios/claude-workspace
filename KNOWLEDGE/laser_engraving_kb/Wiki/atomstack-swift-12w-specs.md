# Atomstack Swift 12W — Specs and Quirks

**Status:** established
**Last updated:** 2026-07-06
**Sources:** [[2026-07-06_atomstack-swift-hoffman-review]], [[2026-07-06_atomstack-swift-laserengraveadvice-review]]

## Summary

The Atomstack Swift is a standalone entry-level diode laser, sold as a switchable 7W/12W module, not an add-on head for another machine. Brian's unit is the 12W version. It's a 455nm blue diode with a 300 x 300mm working area, rated up to 10,000mm/min (≈167mm/s) max travel speed, running through LightBurn (also compatible with AtomStack Studio and LaserGRBL). No air assist ships in the box — there's a port on the module for the optional AtomStack F40 add-on, but Brian's is running without one.

## Body

**Core specs:** 12W optical power (rated ~60,000mW machine power per one source), 455nm blue diode, 300x300mm bed, max engrave speed 10,000mm/min. Spot size is reported two ways across the two reviews in this KB — 0.08 x 0.04mm "compressed" (Hoffman) vs. 0.06 x 0.08mm (Laser Engrave Advice) — likely the same spec rounded/quoted differently rather than two different real numbers. Not reconciled; see Open Questions.

**Focus procedure:** turn the focus knob to extend the probe, lift the X-axis lever, slide the module down until the probe rests on the material, lock it, retract the knob. Fast — a few seconds once you've done it a couple times.

**Clearance caveat:** because focus brings the module very close to the material (good for smoke control, bad for clearance), anything protruding off the workpiece — a button, honeycomb hold-downs, rotary chuck arms — can knock the material out of position mid-job. Worth a visual check before starting any job with hardware or fixtures in the bed.

**Lens is off-center in the module** — not a defect, just how it's built. If you eyeball alignment by looking at the module body, that offset will throw you off. Drawing a small reference mark on the module housing where the lens actually sits fixes this.

**Low acceleration / overscan:** the Swift's acceleration settings are on the low side compared to higher-end machines. This shows up most on stainless steel color marking, where insufficient overscan produces visibly uneven color at the edges of filled areas — tested at both 2.5% and 5% overscan with uneven results in one review, meaning the right number has to be dialed in per job rather than assumed. The same acceleration/overscan relationship applies more generally: overscan disabled anywhere shows up as darker burn at the start/end of scan lines (acceleration and deceleration zones), confirmed on leather engraving specifically.

**No air assist stock.** Air assist port exists on the module for future upgrade. See [[no-air-assist-workarounds]] for what this means in practice.

**Materials confirmed for this machine specifically:** wood (clean single-pass cuts on 3mm birch plywood at 500mm/min, no air assist), black acrylic (two passes, 300mm/min, 3mm material), leather (clean with overscan enabled), slate ("consistent, even engraving across the surface" per Hoffman's hands-on test), anodized aluminum (coating strip), stainless steel (color-marking only, no cutting). Cannot cut clear acrylic or untreated glass — standard diode-laser limitation, needs a marking compound.

**Safety:** Class 4 laser. No goggles included in the box on either reviewed unit — budget for OD4+ goggles rated 445-455nm separately. Reflections off shiny material are the real risk, not just direct beam exposure.

## Related
- [[no-air-assist-workarounds]]
- [[slate-white-vs-yellow]]
- [[lightburn-image-modes-for-slate]]

## Open Questions
- Spot size discrepancy (0.08x0.04mm vs 0.06x0.08mm) between the two reviews — likely a rounding/reporting difference on the same real spec, not confirmed which number to trust.
- No first-hand overscan number confirmed yet for Brian's specific slate/photo work — the overscan issue is documented for stainless steel, not verified on slate.
