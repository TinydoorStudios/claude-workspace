# Compressor, gate, ducker and de-esser

Each channel has two SD dynamics modules, under the EQ in the strip. Touch **Comp** or **Gate** to open the panel.

![Dynamics panel](/figures/q2-dynamics.png)
*Dynamics panel — Quantum 2 offline software, V22.*

![Dynamics panel](/figures/ref-p051-1.png)

**Module 1** is a compressor, a 3-band multiband compressor, or a de-esser (the *comp / multi / desser* button on its left).

**Module 2** is a gate, a ducker, or a second compressor with an external sidechain.

Panel top buttons: **undo** (last change), **safe**, **presets**, **copy to**, **graph**. The In meter shows arrows for each module's threshold in the module's colour; GR is gain reduction.

## Compressor

Threshold, attack, release, ratio, gain. **auto gain** re-trims make-up as you move the threshold. Knee switches hard/soft. **link** ties the sidechains of a stereo channel's two sides.

## Multiband

Three bands, each with the full compressor set. Crossovers are the purple and red rotaries (20 Hz to 20 kHz). **listen** under each band's gain auditions that band on its own (destructively, i.e. in the main path). Single-band and multiband settings are separate; switching modes doesn't copy anything across.

## De-esser

Compressor controls plus a band-pass sidechain filter with centre frequency and width; **listen** auditions the sidechain so you can find the sibilance first.

## Gate and ducker

Threshold, attack, hold, release, range, plus a band-pass filter in the sidechain (**freq**, **width**). **key** opens a route panel to trigger the gate from another signal (ripple lets consecutive gates key from consecutive channels). The three traffic-light LEDs show open / holding / closed. The ducker is the same set of controls with the opposite action.

## Assign to the encoders

Hold **Assign Switch** on the right of the input section and touch any dynamics control on screen; the under-screen rotary row takes it.

## More options on Quantum

The Mustard strip has four modelled compressors, a gate/ducker with its own attack/release shapes, the **Mustard Source Expander** (a level-based expander for vocals and brass, up to 40 dB depth) and, from V22, the **Levelling Amp**. See [Mustard processing](/how-to/16-mustard-processing). For multiband work on a bus, see [Spice Rack](/how-to/17-spice-rack-chilli-6-and-naga-6).

Manual: [Reference 1.6.5 Channel Dynamics](/reference/1-6-channel-signal-processing), [Getting Started 1.8.2 Dynamics](/console/1-8-channel-processing).
