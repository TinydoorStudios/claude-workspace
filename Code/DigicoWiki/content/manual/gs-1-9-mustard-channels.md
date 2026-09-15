# 1.9 Mustard Channels

*The Console — manual pages 27–31*

Mustard channels are a feature of Quantum engines and work alongside standard SD channel strip processing, with both being available at once. Mustard provides a tube/preamp modelling section, an EQ, a compressor with four different models and a gate/ducker. Up to 24 Mustard channel strips (Software V1400+) can be used across the console at any one time. A channel is counted as having Mustard processing active once any one of the Mustard modules are turned on. When this is the case, the channel will display the ‘Active’ icon above the Mustard processing icon, as shown below.

Mustard processing enabled

### 1.9.1 Mustard Channel Strip

The Mustard channel strip layout and operation is similar to that of the SD channel strip, as shown below.

Labels: Mustard Tube section · Mustard EQ · Mustard Compressor · Mustard Gate/Ducker · Mustard Processing

Labels: Insert Position · Switch between viewing · SD processing and

Mustard processing

### 1.9.2 Insert Position

There are 5 selectable positions to choose from when enabling Mustard processing on a channel. The default position for Mustard processing is between the EQ & Dynamics module (depending on the EQ/Dynamics order). Two options will be unavailable as these are the locations of the channel’s Insert A and Insert B. These insert positions can be selected for the Mustard processing by changing the location of Insert A/B, at which point they become available.

This comes after channel trim and before channel delay/DiGiTube

This comes after filters and before EQ/dynamics

This comes in between EQ & Dynamics

This comes after processing and before the mute & fader

This comes after the channel’s fader

1.9 Mustard Channels

### 1.9.3 Safes/Scopes

Each Mustard module (tube, EQ, dynamics) can be safed individually with the tube safe including the insert position of the Mustard processing. The global scopes follow SD processing with tube under input/trim, EQ under EQ and the compressor and gate under dynamics. Input/trim scope also includes the insert position of Mustard processing.

### 1.9.4 Presets

Channel presets can be created as normal and each Mustard module can be included or excluded in the recall scope. Recalling a preset from within the view of a particular module will include only that module in the recall scope by default. Similarly to channel safes, the insert position of the Mustard processing is included within the pre-amp scope.

### 1.9.5 Pre-amplifier Modelling

The Mustard pre-amp modelling section provides the user with a choice of either a simple tube model or a more advanced pre-amp model. This is chosen by selecting type, where a menu will display with the two options.

![Mustard Channels (manual p.28)](/figures/gs-p028-1.png)

**Mustard Tubes**

Mustard Tubes has a drive control, an output gain control, an on/off button and six selectable preset options.

Odd harm – This is a modern sounding, low gain distortion preset Even harm – This is a vintage sounding, medium gain distortion preset Overdrive – This is modern sounding, medium gain distortion preset Distortion - This is modern sounding, compressed, high gain distortion preset Crunch – This is a vintage sounding, high gain distortion preset High distortion – This is a modern, heavy sounding, very high gain distortion preset

1.9 Mustard Channels

**Mustard Amp Model**

The Mustard Amp Model is a two-stage, highly customisable distortion & overdrive processor. Both stages can be switched to odd or even harmonics independently of each other. Even harmonics can create a triode-style distortion whereas odd harmonics can create a pentode-style distortion. The drive control alters the input level to the first stage of distortion. A bias control between the two stages can create asymmetrical distortion if desired. The midpoint value of 11 is the most transparent. Turning on the ‘saturate’ option increases the effect of the bias setting. There is a high frequency boost after both stages which applies a shelving boost above 6kHz. This is followed by the output gain.

![Mustard Channels (manual p.29)](/figures/gs-p029-1.png)

Input meter

First stage harmonics

Saturate control

Second stage harmonics

High frequency Labels: boost · Output meter · Drive

control

Bias control

Output gain

### 1.9.6 Equaliser

Mustard EQ operates in a similar manner to the standard SD channel EQ, with four fully parametric bands. When used on a channel alongside the standard SD processing, this allows the user to have double the amount of fully parametric bands. The top and bottom bands can be switched to act as high and low shelf filters respectively, rather than bell. The middle two bands can be switched from bell filters to all-pass filters. There are also high-pass and low-pass filters (both 24dB/8ve).

### 1.9.7 Compressor

The Mustard channel strip gives the user a choice of four different compressor models, which are modelled on classic analogue compressors. All of the compressor types give the user an on/off button, a wet/dry mix knob, and an output gain control. Other controls vary depending on the type selected. The mix knob controls the balance between the wet (compressed) audio and the dry (uncompressed) audio. If it is set to 100%, there will only be the compressed signal at the output. On all but the Green FET Limiter, there is a threshold control, along with high and lowpass filters in the compressor’s side chain controlled by the low and high rotaries. The effect of the filters on the sidechain signal can be monitored by pressing the s/c listen button. An external sidechain, that is shared with the gate/ducker, can be used with the compressor by selecting a sidechain source in the box underneath the gate/ducker controls and then selecting to send it to the compressor sidechain.

**Classic**

The Mustard classic compressor is a general-purpose feed-forward compressor design with multiple controls allowing flexibility. The threshold, attack time, release time, and ratio can be all controlled by the user. A hard or soft knee can also be selected, and the sidechain’s amplitude sensing can be changed between RMS (Root Mean Squared) level and peak (instantaneous) level.

1.9 Mustard Channels

**Vintage VCA**

The Vintage VCA compressor models classic VCA compressors, with a fixed attack time and an auto-release time. The user can set the threshold and ratio.

**Optical**

The optical compressor models classic opto-compressors, with a unique release characteristic that models the gain reduction provided by an optical compressor circuit. It has three options for attack time and recovery time, along with a ratio control. The gain reduction also behaves uniquely by having a ratio-dependent maximum gain reduction value, with the compressor continuing to be linear above this value.

**FET Limiter**

The FET limiter has a fixed threshold like many classic FET limiters, however the input and output gain knobs can be adjusted accordingly in order to achieve the desired output level and gain reduction. The attack and release values can be adjusted and the ratio can be set at either 4:1, 8:1, 12:1 or 20:1.

### 1.9.8 Gate/Ducker

The gate/ducker works functions similarly to the gate and ducker found in the standard SD channel strip, however it has different attack and release shape characteristics. An external sidechain source can be selected, which can then be sent to the sidechain of the compressor and/or gate/ducker.

1.10 Spice Rack
