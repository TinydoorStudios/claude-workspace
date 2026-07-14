# Slate Engraving — White vs. Yellow Results

**Status:** emerging
**Last updated:** 2026-07-06
**Sources:** [[2026-07-06_diode-laser-slate-white-yellow-forum-digest]], [[2026-07-06_atomstack-swift-hoffman-review]]

## Summary

Getting a clean vibrant white on raw (uncoated) slate instead of a yellow/tan cast comes down to heat management more than raw power. Yellow reads as a sign of overcooking the surface — carbonizing or redepositing hot smoke — not undercooking it. Brian's setup (Swift 12W, 6000mm/min, 60% power, single pass, Jarvis dither, no air assist, IPA wipe after) points toward heat buildup in dense-dither regions as the likely driver.

## Body

**Root mechanism.** Slate's white mark comes from flash-vaporizing or cleaving the thin surface layer to reveal the lighter stone underneath. Community reports on LightBurn forums describe excess power pushing the result toward yellow/tan — the surface scorches deeper and cooks in carbon/mineral discoloration instead of cleanly ablating. Underpowered passes read as grey/incomplete, not yellow, so yellow specifically is an overcook signal.

**Why this shows up in some areas but not others on a photo engrave.** With Jarvis (error-diffusion) dithering, dense-dot regions of the image — usually the transition zones between midtones and highlights — get overlapping laser hits close together in time and space. That's where heat has the best chance to build up before it can dissipate, especially with no air assist clearing smoke and cooling the surface between hits. Sparser dot areas nearby ablate clean because they never build up the same heat. If yellow tracks the image's dither density, this is almost certainly the mechanism. If yellow shows up as random blotches that don't follow the image pattern at all, that's more likely mineral content in that particular piece of slate (see below), not a settings problem.

**Post-wipe is a useful diagnostic, not just cleanup.** Isopropyl alcohol removes loose soot/dust sitting on top of the surface. If a yellow area survives an IPA wipe, the discoloration is thermal — actually baked into the stone — not just redeposited smoke sitting on the surface waiting to be cleaned off.

**Speed/power balance.** No single universal number exists across machines or slate batches — community guidance consistently points to a test grid on scrap material rather than borrowing someone else's setting, because slate stock and machine calibration both vary. On the Swift specifically, max rated speed is 10,000mm/min, so 6000mm/min at 60% power is a normal working point, not an extreme one — the number itself isn't the problem, the interaction with dither density and no air assist is more likely the driver.

**Passes.** No consensus favors multiple lower-power passes over one well-tuned single pass for whiteness specifically — stacking passes risks reheating and recarbonizing an area that already ablated clean on the first pass. Splitting power across two passes is a reasonable experiment given no air assist ([[no-air-assist-workarounds]]), but isn't a guaranteed fix on its own.

**Image mode and contrast.** Slate has almost no usable greyscale range — it jumps from raw grey to white fast, unlike wood or leather where midtone shading reads naturally. Pushing the image's contrast curve hard toward pure black/white *before* running Jarvis dither reduces how much the dither algorithm has to fake with dot density, which directly reduces the dense-dot heat-buildup problem described above. Some experienced slate engravers skip dithering entirely and use straight greyscale/threshold conversion instead, precisely because slate can't hold the midtones dithering is designed to represent.

**Focus.** Slight intentional defocus widens the laser's damage path and has been used deliberately by other engravers to soften/widen the mark — this doesn't contradict the heat-buildup mechanism above and is worth testing alongside power/pass changes rather than instead of them.

**Slate mineral variability.** Natural slate contains iron oxide and other mineral inclusions that can engrave yellow/rust or fail to mark at all regardless of settings — this is a stone problem, not a settings problem. Pyrite ("fool's gold") flecks specifically are called out as a known failure point. If yellow spots don't correlate with the image's tonal pattern, sourcing/sorting flatter, cleaner slate stock is the real fix, not more settings tweaking.

## Related
- [[no-air-assist-workarounds]]
- [[lightburn-image-modes-for-slate]]
- [[atomstack-swift-12w-specs]]

## Open Questions
- No test-grid results yet from Brian's own machine/slate batch confirming the exact power/speed threshold where yellow starts — recommended next step.
- Unclear how much of the fix is contrast-curve/dither changes vs. two-pass-lower-power vs. air assist, since these haven't been isolated against each other on Brian's actual setup yet.
