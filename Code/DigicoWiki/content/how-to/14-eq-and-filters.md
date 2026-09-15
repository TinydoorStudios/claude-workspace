# EQ, filters and dynamic EQ

![Eq — Quantum 2](/figures/q2-eq.png)

Every input channel has a 24 dB/oct high-pass and low-pass, then four fully parametric bands, each of which can be made dynamic. Output channels have EQ too (see the manual for bus EQ).

## Filters

The filters area sits under the input area of the strip: two frequency rotaries with on/off buttons, LPF on top, HPF below. Dedicated filter encoders are at the top of the channel worksurface controls. If meters are hiding the filters, moving a filter encoder shows them briefly; the assign-down button hides the meters for good.

## The four bands

Touch the **EQ area** of the strip to open the EQ/filters panel. Bands are colour coded: blue HF, green HMF, yellow LMF, red LF. Each band has gain (±18 dB) on the left, frequency (20 Hz to 20 kHz) top right, Q bottom right; the worksurface encoders follow the same layout.

![EQ panel](/figures/ref-p048-1.png)

- **bell** toggles the outer bands to shelf. Successive presses of the curve button on the Q225 step through the filter types for the top and bottom bands.
- **precision / classic** (all bands): precision narrows the Q on cuts; classic keeps cut and boost symmetrical.
- **on** (grey off, red on) for the whole EQ, plus per-band on buttons.
- Bottom buttons: **safe** (protect from snapshots), **flat** (all gains to 0), **preset**, **copy to**.
- Touch the response graph for an expanded view.

If the panel doesn't pop open when you turn an encoder, Options > Surface > *Auto expand EQ* is off.

## Dynamic EQ

Touch the small arrow on any band to reveal its dynamic controls. Two modes:

- **Over**: nothing happens below the threshold; above it the band's gain is applied progressively up to the amount set on the gain control. Set a cut at 3 kHz and it only bites when the singer pushes. This is the usual one.
- **Under**: the full gain is applied *below* the threshold and comes off as the signal rises.

![Dynamic EQ](/figures/ref-p049-1.png)

Controls: **threshold**, **attack**, **release**, **ratio** (how fast the full adjustment is reached past the threshold). When any band is dynamic a small icon appears above the EQ graph in the strip with four boxes showing each band's state.

## Mustard EQ

Quantum channels have a second 4-band EQ in the Mustard strip, with its own HPF/LPF, shelf options on the outer bands and all-pass on the middle two. See [Mustard processing](/how-to/16-mustard-processing).

Manual: [Reference 1.6.1–1.6.3](/reference/1-6-channel-signal-processing), [Getting Started 1.8.1 Dynamic EQ](/console/1-8-channel-processing).
