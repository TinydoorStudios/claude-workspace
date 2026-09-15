# 1.6 Channel Signal Processing

*Chapter 1: Channel Types & Function — manual pages 47–54*

Each channel type contains similar signal processing functions, including EQ and dynamics. Input channels also have high-pass and low-pass filters. Pressing on each of these areas of the channel strip will open the relevant signal-processing display.

1.6.1  Channel Filters (All SD and Quantum input channels and on SD8,9,11 output channels)

The filters section of the channel-strip is located below the input section of each input channel. It consists of two frequency rotaries, each with its own on/off button and a display of the filter’s cut off frequency (the -3dB value) in Hertz. The low-pass filter is at the top and the high-pass filter is at the bottom, and both have a roll-off of 24dB per octave.

The filters directly follow the input section in the signal chain. The filters area is replicated at the top of the EQ/filters display, accessed by touching the EQ area of the channel strip. The filter can be configured using the dedicated filter encoders and buttons at the top of the channel worksurface controls:

![Channel Signal Processing (manual p.47)](/figures/ref-p047-1.png)

A graphic representation of the filters is included in the EQ graph located below Insert A in the channel strip, described below. The red line in the graph represents the current filter settings.

Note: that the filters section of the input channel strip may be hidden behind channel meters. In this case, moving the filter encoders will cause them to be displayed momentarily. To hide the meters and retain a permanent display of the filter controls, press the assign down button, located to the left of the encoders above the screen.

### 1.6.2 Input Channel EQ

The SD and Quantum input channel EQ has four bands, each of which can be made dynamic. The four EQ bands are colour coded: Blue for HF, green for HMF, yellow for LMF and red for LF. The in-channel display is located below Insert A and consists of a graphic representation of the current EQ and an on/off button. The button is grey to indicate that the EQ is off, and red to indicate that it is on. The green line in the graph represents the frequency response of the EQ, and the red line represents the response of the filters – each line goes bright to indicate that it is on. The extent and brightness of the opaque area in the bottom half of the graph also indicates which elements are on. The central frequency of each band is displayed by small lines in the band colours, along the bottom of the graph.

Touching the EQ area of the channel strip brings up the EQ/filters display. The EQ section of the display is below the filters section and has another graphic representation of the current EQ at the top. Touching this EQ graph will open an expanded view of the graph. The EQ can be configured using the dedicated encoders and buttons on the worksurface which follow the same layout as the display:

1.6 Channel Signal Processing

![Channel Signal Processing (manual p.48)](/figures/ref-p048-1.png)

![Channel Signal Processing (manual p.48)](/figures/ref-p048-2.png)

![Channel Signal Processing (manual p.48)](/figures/ref-p048-3.png)

In both the EQ/filters display and on the worksurface, each band has a ±18dB gain controller on the left, a frequency controller (ranging from 20Hz to 20kHz) top right and a Q control bottom right. Each rotary has its value displayed to its right.

Bands can be switched between a bell curve (which is the default setting) and a Hi/Lowshelf using the bell button. On SD5, SD7 & Q3, the bell button's 2nd function allows each band to be switched between prec (precision, where the Q is narrower on the cut curve than the boost curve) and class (classic, where the cut and boost Q curves are identical in width). The active setting is shown in red to the right of the bell button. Pressing the precision or classic buttons above the EQ controls will switch all four visible bands to that shape. The active button goes blue – if different bands are employing different shapes, neither button will be lit. The EQ is switched on using the eq on button between the HMF and LMF controls which rings red to indicate that it is on.

Note: that when a band is in dynamic mode, it can also be switched on and off individually in the dynamic display. See below.

Towards the bottom of the EQ/filters display are four grey buttons marked ‘safe’, ‘flat’, ‘preset’ and ‘copy to’. Touching ‘safe’ adds the EQ to that channel’s list of channel safes. Touching ‘flat’ resets the EQ gain controls to 0dB. Touching ‘preset’ brings up the Presets display which can be used to save and recall presets. Touching ‘copy to’ will open the copy to panel with the EQ section pre-selected. Below these buttons is a smaller round button which is also found at the bottom of the channel worksurface controls, for switching the signal- processing order. The default setting is EQ followed by dynamics, as indicated by the eq-dyn label being to the left of the button. Pressing this button reverses the order, as indicated by the labelling switching to a dyn-eq display to the right of the button.

1.6 Channel Signal Processing

### 1.6.3 Dynamic EQ

When any dynamic EQ bands are on, a dynamic EQ icon appears above the EQ graph in the channel strip (as shown on the previous page). The four boxes beneath the icon indicate the status of each band – each box is empty (light grey) when the band dynamics are off, dark grey when the dynamics are on but the band is off, and coloured when the dynamics and band are on. DiGiCo dynamic EQ can operate in two modes: 'over' or 'under'.

**Over Mode**

To place the dynamic module into Over mode, ensure that ‘over’ below the threshold control is highlighted red. When the signal entering the module passes the threshold, the EQ adjustment (as determined by the frequency and Q controls) starts to be applied, up to a maximum adjustment, determined by the EQ band gain control. The manner in which the EQ adjustment is applied once the threshold has been reached is determined by the attack, release and ratio controls.

**Under Mode**

To place the dynamic module into Under mode, ensure that the Over indication below the threshold control is illuminated.

In under mode, the maximum EQ adjustment (as determined by the frequency, Q and band gain controls) is applied when the signal entering the module is below the threshold. As the signal level approaches the threshold, the EQ adjustment is reduced to the point where there is no EQ being applied at the threshold. The manner in which the EQ adjustment is reduced as the signal level approaches the threshold is determined by the attack, release and ratio controls.

![Channel Signal Processing (manual p.49)](/figures/ref-p049-1.png)

**Gain: Sets the maximum EQ adjustment that could be applied**

**Frequency / Q / Curve: Adjusts the EQ characteristics**

Threshold: Sets the threshold at which the EQ starts to be applied

Attack: controls how quickly the dynamic module responds to level passing the threshold

Release: adjusts how quickly the module responds to a fall in level

Ratio: controls how quickly the maximum adjustment is reached once the threshold level is passed.

Over Mode is generally used with a reduction in gain at a specific frequency, such that when the threshold is reached, a gradual reduction of level at that frequency is applied. This could be used to control a change in tonal characteristics as a singer pushes their voice to sing louder.

1.6 Channel Signal Processing

### 1.6.4 Output Channel EQ

The EQ located in each output Channel is similar in operation to the input channel EQ, with the following exceptions: Output channel EQs have either have 4 Bands of EQ and HPF/LPF (SD8,9,11) or eight bands – four pre-insert and four post-insert (SD5,7,10). Buttons in the channel strip (pre-insert eq and post-insert eq) and in the EQ display (pre-insert bands and post-insert bands) select which set of bands is assigned to the worksurface and display controls. All eight bands are shown in the EQ graph, with the pre-insert bands shown in lighter shades than the post-insert bands.

The precision and classic buttons above the EQ bands only affect the four bands currently displayed, and not the full 8 bands available. The pre-insert bands do not have dynamic EQ or bell-shelf switching.

![Channel Signal Processing (manual p.50)](/figures/ref-p050-1.png)

1.6 Channel Signal Processing

### 1.6.5 Channel Dynamics

The SD channel dynamics includes two dynamics modules. Module 1 can be a compressor, multiband compressor or desser; Module 2 can be a gate, ducker, or compressor with high and low-pass filtering on a self or external sidechain.

The channel strip dynamics section is located below the eq. Each module can be enabled individually using the dynamics section next to the screen.

The display includes an input (In) meter and a gain reduction (GR) meter. The input meter has arrows to its right which display the current threshold values for each module.

Each arrow is distinguished by its colour, which matches its associated threshold rotary.

When Module 1 is in Compressor or Multiband mode, threshold and gain rotaries, each with a value display in dB, are also shown in the channel strip (when in Multiband mode, the threshold rotary affects all bands and the mid band's value is displayed).

The Desser only displays a threshold rotary and its value. There is a threshold rotary (with value display) shown for Module 2, with three status indication lights shown when in Gate or Ducker mode.

At the top of the expanded display are buttons marked undo, safe, presets, copy to and graph. Touching the undo button will undo the last change that was made to a parameter of the module. Touching safe adds the dynamics to that channel’s list of channel safes. Touching preset brings up the Presets display which can be used to save and recall presets. Touching copy to will open the copy to panel with the dynamics section pre- selected. Touching graph opens up a view of the module in a graphical format.

![Channel Signal Processing (manual p.51)](/figures/ref-p051-1.png)

**Dynamics 1**

**Dynamics 2**

1.6 Channel Signal Processing

**Dynamics 1: Compressor**

In Module 1's compressor, threshold, attack, release, ratio and gain controls are provided, each of which function in the normal way. The compressor has an auto gain function which is switched on by pressing the auto gain button below the ratio rotary. This function automatically adjusts the gain makeup when changes are made to the threshold, thus keeping the compressor output steady. The threshold knee can be switched between hard, mid and soft using the knee button in the right side of the module. The gain reduction (GR) meter is duplicated in this display.

![Channel Signal Processing (manual p.52)](/figures/ref-p052-1.png)

**Dynamics 1: Multiband Compressor**

In Module 1's multiband compressor, each band includes all of the parameters found in the single band compressor. The link function remains available for the whole compressor and is not assigned to any band. The bands can be switched on individually using the on buttons in the left-hand side of each band, or together using the all on button in the display’s right.

![Channel Signal Processing (manual p.52)](/figures/ref-p052-2.png)

The crossover frequency between bands is controlled using the purple and red rotaries to the left of the hi and lo bands. Each crossover has a range of 20Hz to 20kHz, and the crossover frequencies are displayed below each rotary. Each band can be auditioned (destructively) by pressing the listen button below each gain rotary.

**Dynamics 1: Desser**

The de-esser's controls are similar to those of the compressor, with the following exceptions: In the right side of the module, there is a band-pass filter control for the de-esser sidechain, with rotaries provided for the centre frequency and filter width. The -3dB points for the hi-pass (hp) and lo-pass (lp) frequencies are shown. The filtered sidechain can be auditioned by pressing the listen button. Note that there is no makeup gain included.

![Channel Signal Processing (manual p.52)](/figures/ref-p052-3.png)

1.6 Channel Signal Processing

**Dynamics 2: Gate**

Gates can be keyed by a different signal by pressing the key button below the attack rotary. This brings up a Gate Key Route display from which a key input can be selected. Consecutive channel gates can be keyed by consecutive input signals using the ripple channels function. The key button is ringed red and displays the key input in the text box to its right to indicate that another signal is keying the gate. The key input signal can be auditioned by pressing the key listen button underneath the range rotary.

There is a band-pass filter available: the width control adjusts the width of the band being passed, and the freq control moves that band through the frequency range. The hi- and lo-pass sidechain filter frequencies are displayed. To the right of the link button, there are red, amber and green status indication 'traffic lights'.

**Dynamics 2: Ducker**

The ducker has the same controls as the gate, though the sidechain performs the opposite function of ducking the signal rather than gating it.

**Dynamics 2: Compressor**

Module 2's compressor is identical to the single band mode of Module 1, with the addition of the band-pass filter in the sidechain as described above, and a sidechain input function (S/C) which functions exactly like the key function of the gate.

1.7 Mustard Channels (Quantum only)
