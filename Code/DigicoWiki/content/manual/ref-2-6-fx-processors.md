# 2.6 FX & Processors

*Chapter 2: The Master Screen — manual pages 124–133*

### 2.6.1 The Master FX Display

Selecting the fx menu button in the master screen opens the master fx display, which displays all of the currently assigned fx units in a single rack. Touching any control in this display allows adjustments to be made using the worksurface Touch Turn controls.

![FX & Processors (manual p.124)](/figures/ref-p124-1.png)

It is also possible to create and delete modules from this display:

To create a new module, click on the New button in the top left-hand corner of the fx window to bring up the fx Presets display, then select the appropriate preset in the usual way. Routing to fx modules is then performed in the channel Outputs display. To delete a module, click on the fx presets button on the module, and deselect the preset in the fx Presets display which appears.

Factory presets are provided, and these provide the basis for any user-adjusted presets. Factory presets are indicated by the presence of a red padlock in the lock column on the right and are described below. These include stereo FPGA reverbs and other effects such as delays, choruses, pitch shifters and audio enhancers. Once an effects preset has been adjusted, it can be saved, either as a new preset or as an updated version of the preset that has already been created.

To lock a preset, activate the edit name button and touch the preset’s lock column. A grey padlock appears, indicating that the preset is now locked. Touching the lock again with edit name active unlocks the preset. All master presets are locked and cannot be unlocked. Master presets can be distinguished from user presets by the red colour of their padlocks.

Note: Factory preset group names can be edited, even though the presets themselves cannot.

2.6 FX & Processors

Once an effects preset has been assigned, the fx output button in the channel strip recalls the preset’s controller display. In the case of Input channels, once an effects preset has been assigned, the preset’s display can be recalled by touching the pan area of the channel strip. The fx Presets display can then be recalled by pressing the fx presets button within the controller display.

Each fx unit can be safed by pressing the safe button at the top of its display. The channel’s name and output are also shown at the top of the display, and each effect displays its input and output levels in meters in the left-hand side of the controller.

**(1272+) Global Tap Tempo**

Delay effects can now join a global tap tempo so that a single controller can change the delay amount on all delays in the group. Delays can be set to different scalers. For example, if a delay unit was set to ‘delay x 2’, the delay amount would be set to double the current global tap amount. The options are: off (default, not part of the global tap), x 0.25, x 0.5, x 1, x 2, x 3, x 4.

The global tap can be set using the new macro command type ‘Global Tap Tempo’.

![FX & Processors (manual p.125)](/figures/ref-p125-1.png)

![FX & Processors (manual p.125)](/figures/ref-p125-2.png)

Press to cycle through the options for global tap at various scalers.

![FX & Processors (manual p.125)](/figures/ref-p125-3.png)

The Global Tap value can be entered manually by touching the keypad icon in the Delay FX panel and typing a number.

**FX Graphs**

All reverbs are editable via a graphical display, with each of the coloured adjustable sliders on the graph representing the rotaries on the fx unit below.

![FX & Processors (manual p.125)](/figures/ref-p125-4.png)

2.6 FX & Processors

### 2.6.2 The Spice Rack (Quantum Engines only)

Spice Rack is the new audio processing rack on Quantum engines. It was released with the Chilli 6 Multiband Compressor and also now includes a 6 band Dynamic EQ called Naga 6.

The Spice Rack can be accessed by touching the Master Screen > Processors then Spice Rack.

Soloing a channel with a Spice Rack processor inserted will bring up the Spice Rack and the relevant slot.

### 2.6.3 Chilli & Naga 6 Overview

Open the presets

![FX & Processors (manual p.126)](/figures/ref-p126-1.png)

Safe the current Spice

window

The channel and insert where the

Labels: Link two Chilli 6 units · Rack processor · device is routed · The user interaction · together · Select the Spice Rack · type · device type

![FX & Processors (manual p.126)](/figures/ref-p126-2.png)

![FX & Processors (manual p.126)](/figures/ref-p126-3.png)

List of current units

![FX & Processors (manual p.126)](/figures/ref-p126-4.png)

The current

frequency response of Labels: the processed · in the Spice · Rack slots. · Inserted

Labels: units display · signal · the channel · name.

![FX & Processors (manual p.126)](/figures/ref-p126-5.png)

The dB range

that the compressor will act over

![FX & Processors (manual p.126)](/figures/ref-p126-6.png)

These set the

side chain source and

type

![FX & Processors (manual p.126)](/figures/ref-p126-7.png)

This sets the global Labels: Solo Mode. · This sets the solo source · 2.6 FX & Processors

The Naga 6 can be accessed by selecting a Chilli 6 unit and pressing the type button, then choosing Naga 6.

![FX & Processors (manual p.127)](/figures/ref-p127-1.png)

Open the

![FX & Processors (manual p.127)](/figures/ref-p127-2.png)

Labels: Safe the current Spice · presets · Select the Spice Rack

![FX & Processors (manual p.127)](/figures/ref-p127-3.png)

The channel and insert where

Labels: Rack processor · Link two Naga 6 units · device type · The user

Labels: interaction type · the device is routed · together

![FX & Processors (manual p.127)](/figures/ref-p127-4.png)

The current

![FX & Processors (manual p.127)](/figures/ref-p127-5.png)

frequency response of the

![FX & Processors (manual p.127)](/figures/ref-p127-6.png)

List of Labels: current units · processed · signal · in the Spice · Rack slots. · Inserted

units display

![FX & Processors (manual p.127)](/figures/ref-p127-7.png)

The dB range

that the Labels: compressor will · the channel · name · act over · Select Side Chain · route

![FX & Processors (manual p.127)](/figures/ref-p127-8.png)

These set the

side chain Labels: source and · type · This sets the · global Solo · Mode · This sets the solo source

Chilli 6 is a classic multiband compressor with four flat top filter type bands with shared crossover slope and two separate parametric bands. The Naga 6 is a Multiband Dynamic EQ with six parametric bands and no flat top filters.  They both allow frequency specific dynamic control with compression or expansion applied to audio above a set threshold. When stereo channels are routed to the Spice Rack, two consecutive slots are automatically set to stereo, therefore ganged together. They can be set back to mono to allow the units to have different parameters. Before units can be stereo linked the pair of units have to be set to the same type, Chilli 6 or Naga 6. Pairs must be neighbouring units such as 1 and 2 ,3 and 4, 5 and 6 etc. Note that 2 and 3, 4 and 5 etc cannot be made into a stereo pair.

The green line represents the frequency response of the processed audio and reflects the compression or expansion applied in real time.

The Release Shape is used to alter the release characteristic with curve type exponential (0) through linear (0.5) to inverse exponential (1). Inverse exponential is a new feature which reduces sharp decays between peaks in signal, whilst maintaining the same overall decay time.

![FX & Processors (manual p.127)](/figures/ref-p127-9.png)

2.6 FX & Processors

Dynamic Angle affects how far above the threshold the signal needs to be before the full range of EQ is applied, similar to a ratio with a smooth transition through the threshold. This can be set anywhere between 1 (default) equivalent to a higher ratio and 0, a lower ratio. Also similar to a knee, when the Dynamic Angle is set to a value less than 1, gain reduction will be applied to signal below the threshold however will always maintain a soft curve.

Parametric (Bell) Filters. The six bands on the Naga 6 and two of the bands (P1 and P2) on the Chilli 6, are parametric EQ type filters, which have a centre frequency range of 20Hz – 20kHz and Q of 0.35 – 60. When the band is set to “Split” mode, these bands also have their own independent flat top filter bands, which are used only on the side chain dynamic control and as isolating filters when soloing the band. The centre frequency of these bands follow the frequency control of their main parametric filter, and the width adjusts in sympathy with the main ”Q” control. Setting the band to “Wide” bypasses the flat top filter in the dynamic side chain control such that the side chain is fed directly from the input signal, although these filters remain active as isolating filter when soloing.

Flat top filters. On the Chilli 6 only, bands 1 – 4 have three crossover filters which are used to position the bands over the desired spectrum. A global Crossover Slope adjusts the filter slope between second order (0) and true fourth order (1). When a band is set to split mode, the side chain control signal is fed post the filter and will respond only to audio within the band, but when set to “Wide” the side chain is fed directly from the input and will respond to the whole spectrum. Soloed signals will always pass through the filter regardless of the “Split”/”Wide” state.

Gain acts as a level adjustment for each band.

Range determines the limits of compression or expansion applied to a particular band. When activated, the dynamic range is shown by a blue highlight either above (expansion) or below (compression) the current gain in the graphical display.

External Side Chain. Pressing the “Side Chain Source Route” will allow you to select an external source to be used as a side chain. Each band can be set to use this one signal as its side chain source independently by pressing the “Int” / “Ext” buttons. Any band not using Ext reverts to using self (the input signal) as its source. “Ext” cannot be selected if no external route has been set up.

Soloing Bands. Only one band can be soloed at a time, by pressing the “listen” button in the band. With listen Source set to “Band” the solo will monitor the input signal passing through the bands filter controlled by the dynamics, and in the case of parametric filter bands, the signal will also be passed through a side chain isolating flat top filter. This is so that when notch filters (Bell cut) are used, the affected audio region will be isolated. When Listen source is set to “S/C Listen” the external S/C signal (if set to external) or the input signal, will be passed through its own flat top side chain filter. This filter will not be controlled by the dynamics as it is monitoring the source that is controlling the dynamics.

Listen/Solo Destination. The soloed band can be sent to the “Solo 1” buss, the “Solo2” buss, or both, without altering the normal signal going through the spice rack (non-destructive). Alternatively, Pressing the “Destructive” button will make the soloed band replace the spice racks normal output with the soloed signal. These controls are global to all the units in the spice rack.

Attack and Release determine the speed at which the compression or expansion acts on the signal.

Threshold sets the point where compression or expansion is applied.

There is an overall Output fader which can be used to make-up or reduce a post-effect gain difference.

2.6 FX & Processors

Any of the bands can be set to Bypass which sets the gain and range for that band to 0dB, maintaining the overall phase. Bypass All applies a blanket bypass across all bands which keeps the state of the individual bypasses.

### 2.6.4 User interaction options

1. Faders

Parameters can be touched on screen to determine which row of controls are assigned to the upper master faders (Q7) or centre section faders (Q3/Q5). Mute buttons act as bypass and solos act as listen in this option.

2. Touch turn

Each parameter can be pressed individually to be controlled by the touch turn rotary. The touch turn button toggles the bypass state when on-screen rotaries for that band are selected and listen state when the on- screen faders are selected.

### 2.6.5 Presets

![FX & Processors (manual p.129)](/figures/ref-p129-1.png)

Presets allow the ability to recall and save parameters for a particular setup of a Spice Rack effect. New will create a preset with the current parameters in the effect, this will be stored under a group. Default will recall the default settings for the effect in the current slot.

When edit name is selected, the group name, preset name and notes can be altered. Factory presets are locked and cannot be altered or deleted.

A variety of factory presets are available as starting points for use on different audio sources.

### 2.6.6 Fourier transform.engine - Control Integration (V20xx)

The Fourier transform.engine can be controlled from Quantum consoles (Q8/Q7/Q5/Q3/Q2). There are 2 aspects to the control integration.

- 

Transform Plugin Teleporting and control.

- 

Transform Session and Snapshot integration.

2.6 FX & Processors

Teleporting is enabled with the console Enable Fourier Integration option and, if this is enabled, the Enable Sessions and Snapshot Control option is also displayed as an option. Note that Fourier and Waves integration cannot both be enabled at the same time. To enable this integration:

- 

Connect the console ethernet port to the transform.engine Control port with an ethernet cable.

- 

In the console Options > Console tab, set Enable Fourier Integration to Yes. Then press the Settings button to open the configuration panel.

- 

Enter the IP address of the Control Port on the transform.engine and specify the console network adaptor which is used for the ethernet connection.  The console must be power cycled after any change of IP address. Note that the transform.engine must be in the same subnet as the console.

- 

Select the Audio IO port which will be used for the Transform audio interface which typically will be either a DMI-Dante 64@96 card or an internal Fourier Interface Card. A Fourier Audio logo will appear next to the selected port in the Audio I/O panel.

![FX & Processors (manual p.130)](/figures/ref-p130-1.png)

![FX & Processors (manual p.130)](/figures/ref-p130-2.png)

![FX & Processors (manual p.130)](/figures/ref-p130-3.png)

2.6 FX & Processors

### 2.6.7 Fourier transform.engine - Session and Snapshot integration (V20xx)

Note that on the transform.engine, there will be 2 versions of the showfile related to a particular console session. One has the suffix _autosave and the other does not.

The version of the showfile labelled “session name_autosave” is automatically created on the transform.engine when it performs an autosave and is continuously updated as changes are made. The version simply labelled “session name” is saved whenever the console itself saves a session provided that the console Option > Console > Enable Fourier Sessions and Snapshot Control is set to Yes

If you wish to save the Transform showfile on a removable USB drive for backup/transfer to another transform.engine, please ensure that you Export the version of the showfile without the _autosave suffix. This will then be associated with the console session that has the same name. In the transform.client application running on the standalone computer, navigate to System, select a showfile from the list, press Export Showfile, select a destination and confirm.

The following situations should be considered:

If you don’t have either an existing console session or a Transform showfile Assuming that the console has had a Default All Session Restructure, before saving the new console session, the Transform engine will create a blank showfile named “_default”. When the session is saved on the console, the Transform engine will also save a file of the same name and make that its current showfile. The displayed showfile name will be “sessionname_autosave”. If you have a console session but no matching Transform showfile If a console session is loaded and the transform.engine does not have a showfile with the same name then it will create a default showfile on the transform engine with the same name as the console session, and create a DiGiCo Cuelist. This cuelist will be populated with snapshots to match the snapshots in the console session file. If you have a console session on the console or removable drive and a matching Transform showfile Import the transform showfile onto the transform.engine. Make sure that the showfile name exactly matches the name of the console session file. If it does not, then this must be changed using Rename Showfile within the transform.client, not in a standard file browser. Note that if the showfile has previously been used with DiGiCo console integration and gained the “_autosave” suffix, this will need to be removed from the showfile name in order to synchronise with the console again. Once it has been imported to the transform.client and the session names have been checked, load the session on the console. When the session is loaded onto the console, it will look for the transform showfile of the same name and load this onto the transform.engine. Note that for console sessions made with Fourier Integration turned off, if it is subsequently enabled then by default, console individual Snapshot Recall Scope is not active for the Fourier Transform until the user chooses to enable it. This can be quickly enabled for all snapshots by using the Edit Range function in the Snapshots panel. Since it is possible to load different sessions and make changes to the snapshot list on the transform.engine from the transform.client, it is possible to get out of sync between the console and the transform.engine. If the console detects that the transform.engine session and snapshots are no longer in sync with the console, it will pause the session and snapshot integration. When paused, a message will appear at the top of the Fourier panel. To resync and resume session and snapshot integration, the console session must be reloaded or the Re- synchronise Snapshots button in Fourier > Settings must be pressed.

2.6 FX & Processors

### 2.6.8 Adjusting plugin parameters from the console interface

For plugin teleporting (display and control of the plugin interface on the console), the routed console Transform audio interface socket numbers (typically Dante audio) are associated with the same numbered sockets used with the Transform plugin chain. Note that patching to and from the transform.engine in Dante Controller must be done 1:1. If, for example, console channel 1 has insert send and return routing assigned to the Transform interface sockets input 1 and output 1, selecting/soloing this channel will display the Transform plugin chain with the same numbered socket routes. By default, this would be plugin chain 1. Once all routing to and from the transform.engine has been set up, the Fourier panel can be opened in 3 ways.

- 

Press Processors > Fourier to open the Fourier panel.

- 

Tap the insert routed to the transform engine on the channel strip

- 

Solo a channel that has an insert or output routed to the transform.engine. Note that this will depend on the Solo Displays Insert and Output option found in Options > Solo.

Plugin parameters can be controlled by the touchscreen or a mouse connected to the console. For compatible plugins, control can also be achieved by touching a control in the console Fourier plugin interface and using the console worksurface touch turn encoder. If a plugin is not touch turn compatible, this will be indicated at the top of the console plugin list display. In this case, controls should generally still be controllable with on screen touch. Along the left side of the panel is a list of all of the plugins in the chain. Tap on a plugin to display it. Icons may appear next to plugins in the list to show different states such as bypassed or reloading.

The plugin list on the left can be collapsed and expanded using the Collapse or Expand button at the bottom. This increases the size of the plugin viewer and therefore the size of the plugin.

![FX & Processors (manual p.132)](/figures/ref-p132-1.png)

Displays the plugin chain which is routed from the selected channel

2.7 Matrix Menu

### 2.6.9 Sharing a transform.engine between multiple consoles

It is possible for multiple consoles to connect to the same transform.engine.  If one transform.engine is being shared by multiple consoles (for example FOH and Monitors each using their own chains) then only one of the consoles should be in charge of sessions and snapshots on the transform.engine. This console should have Option > Console > Enable Fourier Sessions and Snapshot Control set to Yes. All other consoles should have this option set to No. If a mirrored set of consoles or engines (for example engine A and B in a Quantum7 or Quantum852) are connecting to the same transform.engine, then both consoles or engines can have Enable Fourier Sessions and Snapshot Control set to Yes. In this setup, the transform.engine will listen to the audio master for session and snapshot commands. If one of these engines can no longer talk to the transform.engine then it will listen to the only console connected, regardless of audio master status.
