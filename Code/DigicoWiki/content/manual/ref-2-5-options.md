# 2.5 Options

*Chapter 2: The Master Screen — manual pages 111–124*

The Options menu includes a variety of SD and Quantum system preferences, grouped into ten tabs. Most functions are described fully within the display. Each function’s button displays purple to indicate that it is active or grey to indicate that it is inactive.

### 2.5.1 Surface

The Surface tab includes settings related to the console screen, buttons and encoders:

![Options panel — Surface tab (manual p.111)](/figures/ref-p111-1.png)

**Touch Keyboard**

This option defines whether or not the on-screen keyboard appears when a name box is touched. It is active by default.

**Large LCD Names**

This option allows the names in the LCD displays to be displayed in a larger font, either with the gain value and solo buss (with dBs) or as the channel only (name only). It is inactive by default.

**Round to whole dBs**

Fractional dB values are rounded to the nearest integer value.

**Auto Expand EQ**

This option defines if the EQ display opens when an EQ is adjusted. It is active by default.

**Auto Expand Dynamics**

This option defines if the dynamics display opens when dynamics is adjusted. It is active by default.

**Auto Expand Time**

This control, located to the right of the Auto Expand EQ and Dynamics options, defines how long the EQ and dynamics displays remain open after the parameters within them are adjusted. The current setting is displayed in seconds, below the control. Touching the control assigns it to the Touch-Turn encoder.

The Auto-Expand Exclude Off option prevents dynamics and EQ from auto-expanding when being turned off.

**Panner Type**

Type 1 is the original SD console implementation. The new Type 2 panning applies a new interpretation of the Sine/Cosine Panning rules - Improved spatial positioning of channels within the stereo image.

Note: This setting is global for all channels on the console.

**Aux to Masters (SD7/Q7 Only)**

This option allows all of the aux send levels for one channel to be assigned to the Lower Master faders by pressing that channel’s lower aux button (the button in the third row of aux encoders below the Channel strip panel). This is useful if, for example, all of the fold-back sends from one channel need to be adjusted. The function is inactive by default. If there are more than twelve auxes in the session, the Lower master bank buttons are used to move between banks of twelve auxes.

Note: If the number of auxes is not divisible by twelve, some faders within the last bank half banks will retain their original function, as indicated by their LCD buttons.

**Selected 4 Aux Rotary Assignment (SD7/Q7 only)**

This option defines whether the vertical four aux rotary controls stay assigned to the current four auxes within a gang/bank/layer/surface/all.

**EX-007 Touch Turn (EX-007 only)**

This option allows the first of the four rotary controls to act as the Touch/Turn control when the Master Screen is visible.

**Display Snapshots Overview**

This option allows a floating copy of the Snapshots list to be displayed in the overview screen, for the viewing or triggering of Snapshots.

**Global Quick Select (SD5, SD9, SD11, SD12, Q3, Q5)**

This option defines whether the Quick Select selection will be the same for every bank on a Surface.

Note: On the SD5/Q5, the selection will be different between the left and right surface.

**Global 2nd Function**

This option defines whether the 2nd function button affects just the current surface (no) or all surfaces on the console (yes).

**Auto-cancel 2nd Function**

This option defines whether or not active 2nd Function buttons are cancelled after the time defined in the auto-cancel time pot to its right. It is inactive by default. Touching the pot assigns it to the Touch-Turn encoder.

Note: Both the auto-expand time and auto-cancel time values are set on the console and are not saved as part of the session file.

**(1272+) Auto-revert LCD Menu to Solo**

When this option is turned on, after the set amount of time the LCD function menu will be cancelled and the LCDs will revert to Solo function. The number of seconds for the LCD function menu to display is set using the auto-revert time rotary.

**Engine A/B Switches Audio (SD7/Q7/Q8 Only)**

This option concerns the Engine button in the top left-hand corner of the SD7's master section, shown below, which is used for switching the SD7 to the redundant engine. When this function is inactive, the Engine button switches just the console controls; when this function is active, the Engine button also switches the audio processing. This function is inactive by default.

### 2.5.2 Faders

![Options panel — Faders tab (manual p.113)](/figures/ref-p113-1.png)

Note: Function replaced in v1445+ - see below

**Fader Assigns Channel**

This option allows a channel to be assigned to the worksurface channel controls whenever its fader is touched. It is inactive by default.

Note: When this option is active, accidentally touching a fader will assign it to the worksurface controls.

**Fader 0dB Detent**

This option defines which controls have a detent at 0dB. Options are Inputs, Outputs, Graphic EQ (default) and CGs.

**Fader Touch Control**

This option defines whether or not a fader moves when it doesn't detect a touch. Options are Free (fader moves freely) and Protected (fader is protected from moving without touch).

Note: This setting is set on the console and is not saved as part of the session file.

**CG Faders Control Aux Sends**

Note: This function has been removed in V1445+ in favour of selectable control on each CG – see CG Aux Send Enable in CG section of the manual.

If this option is set to Yes, whenever 'Aux to Faders' is activated (by any means), the Control Group faders jump to the middle and become +/-18dB trims for the selected aux send, on all channels which are members of the Group. The fader for Control Groups which have no members will simply close and do nothing. CG Mutes and Solos continue to operate as normal.

**(V1455+) Fader Response During Snapshot Recall option**

A new option has been added in Options>Fader tab called Fader Response During Snapshot Recall. The option has a Standard and a Fast setting. When set to Fast the console avoids delaying the fader input when recalling snapshots/cues.

![Fader Response During Snapshot Recall control, Standard/Fast (manual p.114)](/figures/ref-p114-1.png)

To avoid delaying fader input when recalling Snapshots/Cues select Fast option.

**Set Spill Direction (on relevant consoles)**

This option defines the way in which Sets are spilled onto the worksurface: L Vert places them on the left side, creating as many banks as are required to spill all the channels in the Set; R Vert does the same on the right side; Horiz places the first 24 channels across both sides of the console before creating as many banks across both sides as are required to spill all the channels.

### 2.5.3 Solo

The Solo tab includes settings related to the console’s solo functions:

![Options panel — Solo tab (manual p.115)](/figures/ref-p115-1.png)

**Solo Displays Inserts and Outputs**

This option defines whether or not to display any internal FX or Graphic EQ on the inserts of direct outs of a channel when that channel’s solo button is pressed. The Graphic EQ panel can only be displayed on the Master screen. It is active by default.

**Solo Assigns Aux to Faders**

This option defines whether or not the send levels to an aux channel are assigned to the channel faders when that aux channel’s solo button is pressed. It is active by default.

**Solo Assigns Aux to Rotaries**

This option defines whether or not the send levels to an aux channel are assigned to the top row of aux encoders when that aux channel’s solo button is pressed. It is active by default.

**Aux to Faders includes Pans**

This Option defines whether or not the pan assignment for the under-screen rotaries will become the stereo aux pan when a stereo aux is soloed if Solo Assigns Aux to Faders is active.

**Solo Assigns Channel**

This option defines whether or not a channel is automatically assigned to the channel worksurface controls when that channel’s solo button is pressed. It is active by default.

**Solo Assigns Channel also Assigns Screen (consoles with master screen button)**

When a channel is selected using its solo button, the bank it’s on is assigned to the screen.

**Solo Reverts to Output**

This option defines what happens if an output channel solo is active when an input channel solo is then activated and deactivated. When this option is active, deactivating the input channel solo will return the solo buss to the output previously in solo mode. When this function is inactive, deactivating the input channel solo will leave all solos inactive.

The option is only available if the solo buss is in single mode. The option is inactive by default.

**Solo Displays Aux Nodal Processing (Quantum Only) / KLANG**

If a channel is selected and an Aux Master that has a corresponding Klang or Nodal Processing (Quantum only) node is soloed, the expanded view of that node is displayed.

**Line Check Listen**

This option changes which solo bus line check is routed to when listening to input sockets in the Audio I/O page.

**Outputs AFL Only**

This option restricts the Solo PFL/AFL choice to input channels only, all outputs being fixed on AFL.

### 2.5.4 Gangs

The Gangs tab allows gang scopes to be specified for each channel type. Selecting/deselecting the controls under each of the channel types will dictate whether those controls will be altered by a gang.

![Options panel — Gangs tab (manual p.116)](/figures/ref-p116-1.png)

### 2.5.5 Delays

This tab is used for defining the delay units used in the Setup panel of Input channels, Output channels and fx channels (fx units). The options are seconds (default), feet, metres, bpm and frames.

Note that these options are also displayed to the right of the numeric keypad opened by pressing the delay's keypad symbol.

![Options panel — Delays tab (manual p.116)](/figures/ref-p116-2.png)

### 2.5.6 Disable

This tab is used for disabling worksurface buttons, to prevent accidental changes if they are not being used. This function does not affect on-screen operation of the functions.

![Options — Disable tab, showing only the options relevant to your console (manual p.117)](/figures/ref-p117-1.png)

### 2.5.7 Brightness

The Brightness tab is used for adjusting the brightness of the console’s bridge, led lights, screens and surface LEDs. Touching each pot assigns it to the Touch-Turn encoder.

![Options panel — Brightness tab (manual p.117)](/figures/ref-p117-2.png)

The SD5 and SD7 console’s LCD buttons are not controlled by the surface LEDs pot but by the Dim LCD buttons and Invert LCD Image options towards the bottom of the screen.

Note: The dimming option only dims the brighter LCD colours.

### 2.5.8 Meters

The Meters tab includes settings related to the console meters:

![Options panel — Meters tab (manual p.117)](/figures/ref-p117-3.png)

The four pots across the middle of the panel affect the attack and release reaction time (attack rate and release rate), the peak hold time and the overs hold time. The current setting for each is displayed in either milliseconds or seconds, below each pot. Touching each pot assigns it to the Touch-Turn encoder. The row of buttons above the pots provide access to preset meter configurations, including the SD default and a number of PPM formats. The second row of buttons allows the system to compensate for changes in operating levels when viewing PPM meters so that all PPM meters are referenced to 0dBu. The default operating level for SD Series consoles and racks is set to +22dBu.

Note: When the overs hold time is set to 0, the hold time is set to infinite, not 0. The overs lights will therefore remain lit until they are manually cleared.

Note: If you activate a metering preset and then edit it, the button for the preset on which the setting is based will still appear selected.

The point being metered within the channel is set using the eight buttons in bottom left of the display. The input channel meters are adjusted using the buttons on the left, and the output channels are adjusted on the right. The options for each are pre-trim, post-trim (pre-processing), pre-fader (post-processing) and post fader. The default setting is post-trim for input channels, and post-fader for output channels. The currently selected button is displayed in purple.

The Overview area in the bottom right of the display allows the size of Input and Output Meters to be set: small or large.

Note: The settings in the bottom half of the display affect the meters on the worksurface, not the onscreen meters.

### 2.5.9 Console

The Console tab includes settings related to the console’s start up procedure:

![Options panel — Console tab (manual p.118)](/figures/ref-p118-1.png)

**Load Startup Session**

This option allows the startup session to be automatically loaded on system start up. When not selected, the desk will always start up in the default state.

**Save Startup Session**

This option allows the startup session to be automatically saved when quitting. When not selected, the desk will always start up in the same state.

**Auto-Save Recovery Session**

This option enables an auto-save function, which saves the active .ses file regularly, in case it needs to be recovered. The time between auto-saves is defined using the save every pot to the right of the option's button.

**Default Positions**

This option allows all windows to be set to their default positions on next launch.

**Enable External Waves**

This option enables Waves features. Waves is an optional extra which provides a set of Waves plug-ins in addition to the console's own fx units.

For SuperRack SoundGrid V14.30+ (Legacy & ProLink)

DiGiCo console software V1742 for SD and Quantum series consoles will support both Legacy & ProLink modes

After applying the DiGiCo software update, the console will launch with Legacy console remote mode selected.

How to set up ProLink:

1. On the console, go to Master screen > Options > Console.

2. Make sure Enable External Waves is set to Yes and that the console network port is selected.

3. The default selected mode is Legacy. Click on ProLink and power cycle the console.

![Options > Console tab: Legacy/ProLink mode selector next to Enable External Waves (manual p.119)](/figures/ref-p119-1.png)

4. Launch SuperRack SoundGrid.

5. In the Controllers pane, add ProLink Console Remote.

![SuperRack SoundGrid Controllers pane, adding ProLink Console Remote (manual p.120)](/figures/ref-p120-1.png)

6. If you have previously used the console remote module, you will see Legacy Console Remote assigned in the Controllers pane. If that’s the case, you will first need to remove it, then assign ProLink Console Remote. The correct network port is selected automatically.

![ProLink Remote Control window with the console's network port auto-selected (manual p.120)](/figures/ref-p120-2.png)

7. Checkmark ‘Assign’ – status will change to ‘Connected’.

![ProLink Remote Control window with Assign checked and Status showing Connected (manual p.120)](/figures/ref-p120-3.png)

A session load command will pass from the console to SuperRack. If there is no matching session in SuperRack’s integrated sessions folder, SuperRack will load an empty session.

SuperRack SoundGrid Integrated session folder location:

Windows: C:\Users\Public\Waves Audio\SuperRack SoundGrid\Integrated Sessions

Mac: Mac HD > Users > Shared > Waves Audio > SuperRack SoundGrid SoundGrid > Integrated Sessions

ProLink features:

- Automated discovery
- Sync to console global tempo
- Console unattended mode sync with SuperRack

To learn more about DiGiCo remote control integration features and console support, please refer to Waves’ DiGiCo Remote Control Integration and Mirroring article. We strongly advise Waves users to read the MultiRack for DiGiCo SD console user guide.pdf explaining the requirements to use Waves MultiRack/Superrack on an external PC and ensuring that all of the necessary equipment and licences are in place to do this. Please visit http://www.waves.com/downloads/digico for more information Need further assistance? Contact Waves Technical Support.

**Enable Fourier Integration**

See Section 2.6

**Enable Fourier Sessions and Snapshot Control**

See Section 2.6

**Enable Optocore**

This option allows Optocore connections to be switched off if not in use. You can have both Optocore loops OFF, or you can enable Loop 1, Loop 2 or Both.

**Enable Console Network**

This option activates networking for remote control PCs and consoles and is explained in the Network and Mirroring section

Note: Enable External Waves and Enable Console Network both require a restart for changes to take effect.

**Mirroring Mode**

This option defines the way control is assigned between networked consoles and is explained in the Network and Mirroring section.

**Single Engine Only (SD7 Only)**

When active, this option allows two SD7's with only one engine to be mirrored together.

### 2.5.10 Status

The Status tab defines whether console status notifications are displayed. All functions are active by default.

![Options panel — Status tab (manual p.122)](/figures/ref-p122-1.png)

**Display System Status Indicators**

This option defines whether or not the Status display is open. This display provides constant monitoring of various elements of the console’s systems. The indication box to the right of each element displays a green OK when that element is running correctly, a red error when that element is malfunctioning, and a blank grey box when that element is not relevant. Touching any indication box will bring up the appropriate Diagnostics page, if there is one.

**SD7 Dual engines**

*Not on the Q225.*

The status display on an SD7 will have two columns listing the same elements. Each column represents one of the SD7s engines, local being the currently viewed engine and the other being the other engine.

![Status display with two engine columns, local and SD7 remote (manual p.122)](/figures/ref-p122-2.png)

**Display System Alerts**

This option defines whether or not system warnings are displayed. The time for which alerts are displayed is adjusted via the message display time pot, located towards the bottom of the window. The current setting is displayed in seconds, below the pot. Touching the pot assigns it to the Touch-Turn encoder.

**Display Overs Alerts**

With this option active, whenever an input or output over-indicator comes on, the Signal Overs panel is displayed showing details of the signals involved and their channels. Touching an entry in the Signal Overs list brings the channel to the surface to be adjusted. The Signal Overs panel also duplicates the Clear Over Indicators button.

Note: The Signal Overs panel can also be opened using the Signal Over Indicators option in the System menu.

**Display Messages until acknowledged**

With this option active, any system alert will remain on the screen until cancelled by the user.

