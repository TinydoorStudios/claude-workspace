# Yellow tint instead of white on slate — diagnosis

**Date:** 2026-07-06
**Filed retroactively** — this question was asked and answered in chat before this knowledge base existed; filed now per the standard question-report protocol.

## The question

Brian's engraving inverted/tweaked photos onto raw (uncoated, sanded flat) slate coasters on the Atomstack Swift 12W. Some areas come out yellow-ish instead of vibrant white. Running 6000mm/min at 60% power (confirmed as mm/min, not mm/sec, after an initial units check). How to get clean vibrant white.

## Setup confirmed during the conversation

- Speed: 6000mm/min (not mm/sec — checked directly, since that distinction changes the diagnosis completely)
- Power: 60%
- Image mode: Jarvis (error-diffusion dither)
- No air assist available on the machine
- Single pass currently, open to running multiple passes at lower power
- Already wiping with isopropyl alcohol after engraving, before judging color

## The answer

Ranked most-to-least likely cause:

1. **No air assist is the biggest lever.** With Jarvis dithering, dense-dot regions of the image (the midtone-to-highlight transitions) get overlapping laser hits close together. Without air clearing smoke and heat between hits, that smoke sits at high temperature and bakes a yellow/tan stain in exactly those zones, while sparser dot areas nearby ablate clean. The fact that IPA wipe doesn't remove the yellow (confirmed) rules out loose surface soot as the explanation — this points to actual thermal discoloration, consistent with the no-air-assist mechanism.

2. **Try splitting the energy across two lower-power passes instead of one hot pass** — e.g. roughly 35-40% power x2 instead of 60% x1 — so the surface gets a chance to shed heat between hits rather than dumping it all at once in dense-dot zones.

3. **Tighten the image's contrast curve before Jarvis dithering.** Slate has almost no usable midtone range — pushing levels/curves harder toward pure black/white before conversion reduces how much the dither has to fake with dot density, which is the direct driver of the heat-buildup problem.

4. **Rule out mineral variability separately.** If any yellow spots don't track the image's tonal/dither pattern at all — just show up as blotches regardless of density — that's iron oxide/mineral content in that specific piece of slate, not a settings problem. No fix but sourcing flatter, cleaner stock.

Suggested first test: cheap air assist (even a basic aquarium pump aimed at the cut point) at the same 6000/60%/single pass, to see how much of the gap that alone closes, before touching power/passes/dither settings.

## Sources

- [[slate-white-vs-yellow]] — full mechanism writeup
- [[no-air-assist-workarounds]] — practical mitigations given no air assist
- [[lightburn-image-modes-for-slate]] — Jarvis dither vs. greyscale/threshold for slate
- [[atomstack-swift-12w-specs]] — machine specs referenced (max rated speed 10,000mm/min, confirming 6000mm/min is a normal working point, not extreme)

## Open follow-up

No test-grid has been run yet on Brian's actual machine/slate stock to confirm which of the above levers (air assist, passes, contrast curve) matters most. Recommended next step once he's ready: a 5x5 power x speed test grid in LightBurn on a scrap piece, then isolate air-assist-on vs. off if/when the F40 add-on gets added.
