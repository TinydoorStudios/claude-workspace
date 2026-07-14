# No Air Assist — Workarounds

**Status:** emerging
**Last updated:** 2026-07-06
**Sources:** [[2026-07-06_atomstack-swift-hoffman-review]], [[2026-07-06_diode-laser-slate-white-yellow-forum-digest]], [[2026-07-06_atomstack-air-assist-accessory-digest]]

## Summary

Brian's Swift 12W runs with no air assist installed — the port on the module is there, but there's no pump attached. Air assist's real job is cooling the surface and clearing smoke/fumes before they redeposit; running without it means heat and smoke management has to come from settings and technique instead of airflow.

## Body

The Swift doesn't ship with air assist (confirmed directly for this machine) and AtomStack's own product copy for its air assist accessories describes the job as reducing surface temperature quickly, preventing excessive burning, and keeping edges clean — which is exactly the gap Brian is working around. The manufacturer-matched option is the AtomStack F40 Air Assist Set (~$59, sold specifically for the Swift's port), the only compatibility confirmed in research so far.

Without it, on Brian's slate/photo work specifically, the main risk is smoke and heat sitting on the surface instead of being blown clear — smoke redepositing on a still-hot surface is described as a direct cause of yellow/tan discoloration in slate engraving generally (see [[slate-white-vs-yellow]]). This matters most in dense-dither regions of a photo engrave, where repeated close-together laser hits build up local heat with nowhere for the smoke to go.

Practical mitigations, in rough order of impact, given no air assist:

**Split power across more passes at lower intensity per pass**, rather than one hot single pass. Less heat dumped at once gives the surface more chance to shed it between hits instead of cooking it in.

**Widen the gap between passes if multi-passing** (even a few seconds) so residual heat has time to dissipate before the next pass — without moving air, that dissipation is doing more work than it would with a fan running.

**Keep an eye on smoke visibly hanging over the work** rather than clearing — if it's not moving on its own, it's sitting there long enough to redeposit before it cools. A simple desk fan or window venting fan aimed *across* the bed (not into the beam path) helps even without a proper air assist nozzle, though it's not a substitute for the real thing.

**Clean before judging results.** Brian already wipes with isopropyl alcohol after engraving — that's the right move regardless of air assist, since it separates "residue sitting on top" from "actual thermal discoloration baked into the stone." If IPA doesn't lift a yellow area, that's a thermal problem, not a smoke-residue problem, and points back to power/speed rather than airflow.

**Test grid first on any new slate batch or new image**, since without air assist the safe power/speed window for clean white (vs. yellow) is narrower than it would be with cooling — small changes in dither density or image contrast can push a formerly-fine setting into the yellow zone.

The F40 add-on ($59, direct from AtomStack) is the lowest-friction real fix if this keeps being a recurring problem rather than a one-off — it plugs directly into the existing port, no machine modification needed.

## Related
- [[atomstack-swift-12w-specs]]
- [[slate-white-vs-yellow]]

## Open Questions
- Whether a generic (non-AtomStack) aquarium-pump-style air assist would work with the Swift's port, or whether it needs the matched F40 fitting — not confirmed in research so far.
- Real-world before/after comparison on Brian's own slate once/if air assist gets added — would confirm how much of the yellow issue is airflow vs. settings.
