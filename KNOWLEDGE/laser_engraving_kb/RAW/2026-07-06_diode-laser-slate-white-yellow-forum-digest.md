---
title: "Web search digest — LightBurn forum and slate-engraving guides on white vs. yellow results"
author: unknown (multiple forum posters and guide authors, aggregated)
source_url: unknown
date_added: 2026-07-06
date_published: unknown
type: Web search digest
tags: [slate, white-vs-yellow, dither, air-assist, general-diode-laser]
---

Search context: this digest was compiled by an agent searching LightBurn community forums and independent guide sites for general diode-laser-on-slate technique (yellow/tan discoloration vs. clean white). It is NOT Atomstack Swift-specific — the source threads discuss diode lasers on slate in general, sometimes on other brands/models. Kept in this knowledge base because the physics and technique transfer directly to the Swift, but any claim here should be read as general diode-laser knowledge, not a Swift-specific spec or forum report.

Source pages referenced during the search (titles as returned, not individually re-verified line-by-line):
- LightBurn forum — "Laser Setting for engraving on Slate" (https://forum.lightburnsoftware.com/t/laser-setting-for-engraving-on-slate/150771)
- LightBurn forum — "How to engrave a photo onto slate" (https://forum.lightburnsoftware.com/t/how-to-engrave-a-photo-onto-slate/16750)
- LightBurn forum — "Slate color when using laser" (https://forum.lightburnsoftware.com/t/slate-color-when-using-laser/59465)
- LaserUser — "How To Laser Engrave Slate: 5 Tips" (https://laseruser.com/how-to-laser-engrave-slate/)
- LightBurn docs — Image Mode reference (https://docs.lightburnsoftware.com/2.1/Reference/CutSettingsEditor/ImageMode/)
- Hendrick Studios — "Cleaning/Caring for Slate Coasters" (https://hendrick-studios.myshopify.com/blogs/news/slate-and-how-to-care-for-it)
- X-Creation — "A Beginner's Guide to Laser Engraving Slate Coasters" (https://x-creation.com/a-beginners-guide-to-laser-engraving-slate-coasters/)

## Key findings (paraphrased from the above, not direct quotes)

**Power vs. yellow.** Multiple posters on the "How to engrave a photo onto slate" thread describe excess power pushing the result toward yellow/tan rather than clean white — one reply specifically warns "not too much power as it tends towards yellow." The mechanism described: slate's white mark comes from flash-vaporizing/cleaving the thin surface layer; overdriving power scorches deeper and cooks in carbon/mineral discoloration instead of cleanly ablating. Underpowered passes were described as reading grey/incomplete rather than yellow — so yellow is read as an overcook signal, not an underpower one.

**Units confusion is a known failure mode.** On that same thread, the LightBurn developer ("Oz") caught a user who had set speed to "6000 mm/min" while the firmware's real travel cap was 500mm/min — the controller silently throttled power to compensate, producing inconsistent burns. Mismatches between a requested speed and the machine's real capability are called out as a recurring cause of bad results.

**Image mode for slate.** LightBurn's Jarvis (error-diffusion dither) is generally recommended for photo realism on most materials, but slate has almost no usable tonal range — it jumps from raw grey to white quickly. One long-time engraver quoted in the search results says they "always greyscale... not dithering for slate," maximizing image contrast before conversion rather than trusting the dither algorithm to hold midtones. Newsprint/halftone mode wasn't specifically endorsed for slate in the sources found — more of a decorative choice elsewhere.

**Focus.** One forum tip mentions running the laser deliberately de-focused for a wider damage path alongside a larger scan interval, used to widen/soften the mark and cut engrave time — consistent with the idea that slight defocus can help whiteness/coverage rather than hurt it.

**Passes.** No consensus found favoring multiple passes for whiteness specifically. Guidance leans toward dialing in single-pass power/speed/interval via a test grid; stacking additional passes risks reheating and recarbonizing an already-ablated area.

**Air assist.** Air assist's job is described as cooling the surface and clearing fumes before they redeposit. Soot/smoke particles (cited in the 1–10 micron range by one source) can electrostatically cling to and stain lighter materials if not cleared, and smoke redepositing while still hot is described as yellowing on contact ("the temperature of the smoke is quite high, changing the original color to yellow" per one guide).

**Post-processing.** Multiple slate-specific guides converge on: dry-brush first (soft brush or toothbrush) to avoid smearing loose dust, then wipe with a damp microfiber cloth or isopropyl alcohol, or rinse under water with a soft brush. Pulverized slate dust sitting in the engraved groove is described as normal and can read as dull/off-color until removed — distinct from actual thermal discoloration baked into the stone. Pre-engrave contamination (dust, handling oils) is also flagged as a cause of splotchy/uneven burns.

**Slate material variability.** Guides explicitly warn that natural slate contains mineral inclusions (pyrite/"fool's gold" flecks specifically called out) that don't engrave properly and show as blank or off-color spots regardless of settings. Uneven surface flatness within a single piece can also cause focus drift across the engrave area. The practical workaround cited: visually sort/select flat, unflecked pieces, and run a settings test grid per batch rather than trusting one universal setting across all stock.
