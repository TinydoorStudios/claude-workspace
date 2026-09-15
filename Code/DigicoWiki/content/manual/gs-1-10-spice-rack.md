# 1.10 Spice Rack

*The Console — manual pages 31–35*

Spice Rack is the new audio processing rack on Quantum engines. It was released with the Chilli 6 Multiband Compressor and also now includes a 6 band Dynamic EQ called Naga 6. The Spice Rack can be accessed by touching the Master Screen > Processors then Spice Rack. Soloing a channel with a Spice Rack processor inserted will bring up the Spice Rack and the relevant slot.

### 1.10.1 Chilli & Naga 6 Overview

Open the

![Spice Rack (manual p.31)](/figures/gs-p031-1.png)

Safe the current Spice Rack Labels: processor · presets · Link two Chilli 6 · The user

interaction type

The channel and insert where

units together

Select the Spice Rack device type

the device is routed

![Spice Rack (manual p.31)](/figures/gs-p031-2.png)

![Spice Rack (manual p.31)](/figures/gs-p031-3.png)

List of current units in the

![Spice Rack (manual p.31)](/figures/gs-p031-4.png)

The current frequency response of the Labels: processed · Spice Rack · slots.

Inserted

units display the

![Spice Rack (manual p.31)](/figures/gs-p031-5.png)

The dB range that the compressor Labels: will act over · channel · name.

![Spice Rack (manual p.31)](/figures/gs-p031-6.png)

These set the side chain source and type

This sets Labels: the global · Solo · This sets the solo · 1.10 Spice Rack

The Naga 6 can be accessed by selecting a Chilli 6 unit and pressing the type button, then choosing Naga 6.

![Spice Rack (manual p.32)](/figures/gs-p032-1.png)

Open the presets

![Spice Rack (manual p.32)](/figures/gs-p032-2.png)

Safe the current Spice Rack processor

Select the Spice Rack device type

![Spice Rack (manual p.32)](/figures/gs-p032-3.png)

The channel and insert where the device is routed

![Spice Rack (manual p.32)](/figures/gs-p032-4.png)

The user interaction type

Link two Naga 6 units together

![Spice Rack (manual p.32)](/figures/gs-p032-5.png)

The current frequency response of the processed signal

![Spice Rack (manual p.32)](/figures/gs-p032-6.png)

![Spice Rack (manual p.32)](/figures/gs-p032-7.png)

List of current Labels: units in the · Spice Rack · slots.

Inserted

![Spice Rack (manual p.32)](/figures/gs-p032-8.png)

The dB range that the compressor will act over

units Labels: display the · channel · name · Select Side

Chain route

![Spice Rack (manual p.32)](/figures/gs-p032-9.png)

These set the side chain source and Labels: type · This sets the · global Solo · Mode · This sets the solo

Chilli 6 is a classic multiband compressor with four flat top filter type bands with shared crossover slope and two separate parametric bands. The Naga 6 is a Multiband Dynamic EQ with six parametric bands and no flat top filters.  They both allow frequency specific dynamic control with compression or expansion applied to audio above a set threshold. When stereo channels are routed to the Spice Rack, two consecutive slots are automatically set to stereo, therefore ganged together. They can be set back to mono to allow the units to have different parameters. Before units can be stereo linked the pair of units have to be set to the same type Chilli 6 or Naga 6. Pairs have to be neighbouring units such as 1 and 2 ,3 and 4, 5 and 6 etc. Note that 2 and 3, 4 and 5 etc cannot be made into a stereo pair. The green line represents the frequency response of the processed audio and reflects the compression or expansion applied in real time. The Release Shape is used to alter the release characteristic with curve type exponential (0) through linear (0.5) to inverse exponential (1). Inverse exponential is a new feature which reduces sharp decays between peaks in signal, whilst maintaining the same overall decay time.

![Spice Rack (manual p.32)](/figures/gs-p032-10.png)

Dynamic Angle affects how far above the threshold the signal needs to be before the full range of EQ is applied, similar to a ratio with a smooth transition through the threshold. This can be set anywhere between 1 (default) equivalent to a higher ratio and 0, a lower ratio. Also similar to a knee, when the Dynamic Angle is set to a value less than 1, gain reduction will be applied to signal below the threshold however will always maintain a soft curve.

1.10 Spice Rack

Parametric (Bell) Filters. The six bands on the Naga 6 and two of the bands (P1 and P2) on the Chilli 6, are parametric EQ type filters, which have a centre frequency range of 20Hz – 20kHz and Q of 0.35 – 60. When the band is set to “Split” mode, these bands also have their own independent flat top filter bands, which are used only on the side chain dynamic control and as isolating filters when soloing the band. The centre frequency of these bands follow the frequency control of their main parametric filter, and the width adjusts in sympathy with the main ”Q” control. Setting the band to “Wide” bypasses the flat top filter in the dynamic side chain control such that the side chain is fed directly from the input signal, although these filters remain active as isolating filter when soloing. Flat top filters. On the Chilli 6 only, bands 1 – 4 have three crossover filters which are used to position the bands over the desired spectrum. A global Crossover Slope adjusts the filter slope between second order (0) and true fourth order (1). When a band is set to split mode, the side chain control signal is fed post the filter and will respond only to audio within the band, but when set to “Wide” the side chain is fed directly from the input and will respond to the whole spectrum. Soloed signals will always pass through the filter regardless of the “Split”/”Wide” state. Gain acts as a level adjustment for each band. Range determines the limits of compression or expansion applied to a particular band. When activated, the dynamic range is shown by a blue highlight either above (expansion) or below (compression) the current gain in the graphical display. External Side Chain. Pressing the “Side Chain Source Route” will allow you to select an external source to be used as a side chain. Each band can be set to use this one signal as it’s side chain source independently by pressing the “Int” / “Ext” buttons. Any band not using Ext reverts to using self (the input signal) as it’s source. “Ext” cannot be selected if no externally route has been set up. Soloing Bands. Only one band can be soloed at a time, by pressing the “listen” button in the band. With listen Source set to “Band” the solo will monitor the input signal passing through the bands filter controlled by the dynamics, and in the case of parametric filter bands, the signal will also be passed through a side chain isolating flat top filter. This is so that when notch filters (Bell cut) are used, the effected audio region will be isolated. When Listen source is set to “S/C Listen” the external S/C signal (if set to external) or the input signal, will be passed through its own flat top side chain filter. This filter will not be controlled by the dynamics as it is monitoring the source that is controlling the dynamics. Listen/Solo Destination. The soloed band can be sent to the “Solo 1”buss , the “Solo2” buss, or both, without altering the normal signal going through the spice rack (non-destructive). Alternatively, Pressing the “Destructive” button will make the soloed band replace the spice racks normal output with the soloed signal. These controls are global to all the units in the spice rack. Attack and Release determine the speed at which the compression or expansion acts on the signal. Threshold sets the point where compression or expansion is applied. There is an overall Output fader which can be used to make-up or reduce a post-effect gain difference. Any of the bands can be set to Bypass which sets the gain and range for that band to 0dB, maintaining the overall phase. Bypass All applies a blanket bypass across all bands which keeps the state of the individual bypasses.

### 1.10.2 User interaction options

1.

**Faders**

Parameters can be touched on screen to determine which row of controls are assigned to the Quantum 2 faders. Mute buttons act as bypass and solos act as listen in this option.

2.

**Touch turn**

Each parameter can be pressed individually to be controlled by the touch turn rotary. The touch turn button toggles the bypass state when on-screen rotaries for that band are selected and listen state when the on-screen faders are selected.

1.10 Spice Rack

### 1.10.3 Presets

![Spice Rack (manual p.34)](/figures/gs-p034-1.png)

Presets allow the ability to recall and save parameters for a particular setup of a Spice Rack effect. New will create a preset with the current parameters in the effect, this will be stored under a group. Default will recall the default settings for the effect in the current slot. When edit name is selected, the group name, preset name and notes can be altered. Factory presets are locked and cannot be altered or deleted. A variety of factory presets are available as starting points for use on different audio sources. The Naga 6 has the addition of six static gain curves (Band Gains), colour coded to the appropriate band, and as such there are three display option buttons which allow you to mix and match the graphic display. The live animated spectral gain indicator (the green line) remains visible at all times.

**Band Gain Filters only**

![Spice Rack (manual p.34)](/figures/gs-p034-2.png)

**Side Chain/isolating Filters only**

![Spice Rack (manual p.34)](/figures/gs-p034-3.png)

**Range only**

![Spice Rack (manual p.34)](/figures/gs-p034-4.png)

1.11 Auxiliaries
