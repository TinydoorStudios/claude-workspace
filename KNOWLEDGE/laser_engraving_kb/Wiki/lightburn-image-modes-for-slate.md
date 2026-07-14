# LightBurn Image Modes for Slate

**Status:** emerging
**Last updated:** 2026-07-06
**Sources:** [[2026-07-06_diode-laser-slate-white-yellow-forum-digest]]

## Summary

Slate's near-binary tonal response (it jumps from raw grey to white, with almost no usable midtone) makes it behave differently from wood or leather in LightBurn's image processing. Dither-based modes like Jarvis have to fake shading with dot density, which is exactly what drives the heat-buildup/yellow problem described in [[slate-white-vs-yellow]].

## Body

**Jarvis (error-diffusion dither).** LightBurn's general-purpose recommendation for photo realism — turns grayscale into a dot pattern that reads as continuous tone from a normal viewing distance. Works well on materials with real tonal range. On slate, the density of dots in transition zones (midtone-to-highlight) is where overlapping laser hits build up heat fastest, especially without air assist.

**Greyscale / Threshold approach.** At least one experienced slate engraver in community discussion skips dithering entirely for slate, converting to a harder greyscale/threshold curve instead — reasoning that slate can't hold subtle midtone shading anyway, so asking the dither algorithm to represent it with dot density just adds risk without adding real tonal benefit.

**Contrast curve before conversion.** Regardless of which mode is used, pushing the source image's levels/curves harder toward pure black/white before it goes into LightBurn's image processing reduces the amount of "fake" midtone the dither has to represent — directly reducing dense-dot regions and the heat buildup they cause.

**Newsprint/halftone.** Not specifically endorsed for slate in research gathered so far — more commonly used as a deliberate decorative dot-pattern look on other materials.

## Related
- [[slate-white-vs-yellow]]
- [[atomstack-swift-12w-specs]]

## Open Questions
- No side-by-side test yet on Brian's actual photo between Jarvis (current) and straight greyscale/threshold — would directly test the mechanism described above.
