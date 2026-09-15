# 2.13 External Control

*Chapter 2: The Master Screen — manual pages 171–184*

### 2.13.1 iPad Control

The DiGiCo SD/Quantum app allows remote, wireless control of any DiGiCo SD or Quantum mixing console from your Apple iPad.

To activate iPad Control:

1. Navigate to Setup > External Control from the menu on the main screen.
2. Enable External Control by pressing the button at the top of the panel — please disable this function when External Control is not required.
3. Press the Add Device button and select DiGiCo Pad.
4. Enter a Device Name (user choice) for the device and then enter the IP Address of the iPad.
5. Enter Send and Receive Port numbers for the console, e.g. Send = 9000 and Receive = 8000. Note: if you enter multiple devices in this panel, they must all have unique Send and Receive ports.
6. Tick the Enable column for this device.
7. Press the Load button in the bottom right corner of the panel and select the commands button for the relevant console. There are several different sets of commands: one for SD8, SD9, SD11 and SD12, another for SD5, SD7 and SD10, and others which are specific to Quantum console models.

   Note: only one set of commands should be loaded at one time — if in doubt about which one is loaded, press the Clear All button and then reload the relevant commands for your console.

8. Take note of the console Local IP Address at the bottom of the panel, as this information will have to be entered on the Connect page of the DiGiCo iPad App.

Every external device — iPad, OSC, L-ISA, d&b, KLANG, Spacemap, AFM, Astral — is added and managed from the same External Devices list in this panel:

| Column | Description |
|---|---|
| Type | Device protocol (OSC, KLANG, Astral, etc.) |
| Name | User-assigned device name |
| IP Address | IP address of the external device |
| Send | Port the console sends data to |
| Rcv | Port the console receives data on |
| Enabled | Ticked to activate the device |
| Bundles | OSC bundle transmission on/off |
| DevID | Console-assigned device ID, used to target the device (e.g. from a MacroOSC command) |

![External Control panel — Enable External Control, and Add Device with DiGiCo Pad selected (manual p.173)](/figures/ref-p173-1.png)

![External Control panel — iPad device entered and enabled, then Load iPad commands (manual p.173)](/figures/ref-p173-2.png)

![Load iPad commands panel, zoomed (manual p.173)](/figures/ref-p173-3.png)

### 2.13.2 Generic OSC

This feature allows any device that can transmit and receive OSC messages to be connected to a desk. The Generic OSC control has 8 rotary and 8 switch controllers that can have their names, values and operating ranges defined in the Generic OSC customise section of the External Control panel.

To activate Generic OSC Control:

1. Navigate to Setup > External Control from the menu on the main screen.
2. Enable External Control by pressing the button at the top of the panel — please disable this function when External Control is not required.
3. Press the Add Device button and select Generic OSC Device.
4. Change the Input Channel Controller to OSC Generic.
5. Select Other OSC from the drop-down list and then enter a device name, the IP address and Send/Receive ports for the Generic OSC device. Note: if you enter multiple devices in this panel, they must all have unique Send and Receive ports.
6. Tick the Enable column for this device.
7. Press the Customise button and enter a label, required OSC message, min, max and default values for the relevant control. Press rotaries or switches to view the settings for the 2 sets of 8 controls. Note: the first four rotaries can be controlled by the graphical touch controls within the expanded panel.
8. OSC messages should contain an asterisk (*) to represent the channel number, e.g. `/MyDevice/MyParameter/*`

![External Channel Controllers OSC panel — rotaries/switches customise table: Label, OSC, Min, Max, Default (manual p.174)](/figures/ref-p174-1.png)

### 2.13.3 L'Acoustics L-ISA

External Control for an L'Acoustics L-ISA system can be added via this menu; this allows OSC commands to be sent to L-ISA from channel strip controls.

To activate L-ISA Control:

1. Navigate to Setup > External Control from the menu on the main screen.
2. Enable External Control by pressing the button at the top of the panel — please disable this function when External Control is not required.
3. Change the Input Controller to L-ISA.
4. Press the Add Device button and select L-ISA.
5. Select Other OSC from the drop-down list and then enter a device name, the IP address and Send/Receive ports for the L-ISA device. Note: if you enter multiple devices in this panel, they must all have unique Send and Receive ports.

L-ISA control can be activated on a channel by pressing 'L-ISA Control' at the bottom of the output panel. This will display a small plot of L-ISA pan position on the channel strip itself; this area can be pressed to open the L-ISA Source Control panel where L-ISA parameters can be adjusted. This can be hidden by pressing the 'view' button.

![L-ISA Source Control panel opened from a channel strip, with pan/width/distance/elevation/aux send rotaries (manual p.175)](/figures/ref-p175-1.png)

Stereo channels can also have L-ISA control, in which they gain another row of rotary controls on the Source Control panel, plus a 'pan spread' rotary and a 'link' button.

L-ISA groups can be pressed in the 'L-ISA groups' selection to allow them to be controlled from the L-ISA panel.

![L-ISA Source Control panel — stereo pan-spread and link controls, and the L-ISA groups list (manual p.176)](/figures/ref-p176-1.png)

Selection Sync can be activated in L-ISA controller so that when a channel is selected on the console, it is also selected in L-ISA controller and vice versa.

![L-ISA En-Bridge Desk Link Settings — Selection Sync so console and L-ISA channel selection follow each other (manual p.177)](/figures/ref-p177-1.png)

Channel faders can be linked with the L-ISA master fader so that the output of L-ISA can be adjusted without leaving the console surface. This is assigned in the 'External Control' panel.

![External Control panel — L-ISA Select Master fader link (manual p.177)](/figures/ref-p177-2.png)

### 2.13.4 d&b Soundscape Control

Bi-directional control of d&b Soundscape is also available. For remote control to work, a DS100, a computer running d&b ArrayCalc/R1 and a computer running En-Bridge are required.

There is a d&b button in Setup>External Control. Adding an other OSC device will allow communication.

![External Control panel — d&b enabled, D&B device added; d&B Control/view buttons on a channel; Object Number list and Soundscape control view (manual p.178)](/figures/ref-p178-1.png)

Once enabled in the External Control panel, d&B Control and view buttons will appear in the bottom of Input Channel and Group Output Setup Panels. When activated for a specific channel, the buttons will have a red background and a Soundscape control will replace the standard channel Pan controller. When the Soundscape control on the channel strip or the d&b button on a group is pressed, the Soundscape Control panel will open.

![d&b Soundscape control view — Object Number selection, X/Y position pad, and Area/Delay controls (manual p.178)](/figures/ref-p178-2.png)

The controls are:

- Sound Object x Position (rotary)
- Sound Object y Position (rotary)
- Sound Object Spread factor (rotary)
- Sound Object En-Space Send Gain (rotary)
- Sound Object Delay Mode (3 toggle buttons)
- Touch the small x/y position display in the expanded view to further expand the display.
- Touch on the Object Number button to select which sound object the channel strip shall control.
- Touch on the Mapping button to select which mapping area shall be targeted from the channel strip's controls.

Full details of the integration can be found at www.dbaudio.com

### 2.13.5 KLANG Control

| Button | Function |
|---|---|
| Bypass all KLANG nodes | Temporarily reverted to normal aux sends |
| Transmit all stored KLANG parameters to the controller | Sent on session load |

The KLANG level and aux send level will be stored as the same value (if KLANG is bypassed or disabled, the aux send level will be the KLANG level).

![External Control panel — KLANG interface enabled, controller IP details entered (manual p.179)](/figures/ref-p179-2.png)

The KLANG automated setup process can be automated to some extent — please follow this link for more information: https://www.klang.com/product/console-integration/

### 2.13.6 Spacemap Go control (V17xx+)

DiGiCo and Meyer Sound Laboratories, Incorporated have worked in partnership to provide integrated control of a Spacemap Go immersive loudspeaker system from the console interface. Spacemap Go Channels can be associated with console Channels or Groups.

Spacemap Go Panner, Crossfade, Spread and Trajectory transport controls are available from the console for each Spacemap Go Channel. The control view also provides the Channel name, both Spacemap names, and the trajectory name if active.

The Spacemap Server runs on the GALAXY network platform processor, and the Spacemap Go iPad app, as well as all external controllers, are connected as clients to the server.

This feature is available when using the following software and firmware versions, or more recent releases:

- DiGiCo Console software V1742
- Meyer Sound Compass version 4.13.1, which includes Meyer Sound GALAXY firmware version 2.8.1
- Meyer Sound Spacemap Go version 1.2.2, available at the Apple App Store

Spacemap Go Control will be configured in the DiGiCo console's External Control options tab (Master Screen > Setup > Options). In the Channel Controllers panel, select SpaceMap.

Select Add device and other OSC, then enter the required IP Address and Send/Rcv port numbers as required. Confirm by pressing in the Enabled column.

![External Control panel — Spacemap channel controller enabled (manual p.180)](/figures/ref-p180-1.png)

Control of a Spacemap Go Channel can be enabled on any of the console's Channels or Groups. Navigate to the channel and open the Controller view by tapping on Channel > Output Setup; at the bottom of the popover window enable Spacemap Controller, then View. Close the popover and touch on the 2D XY Panner — the external controls will appear.

The assigned Spacemap Go channel can be changed by clicking on the blue box with the currently assigned Spacemap channel in white.

![Spacemap Go Object Number list — channels in red are assigned to other console channels, white/inactive channels are available (manual p.181)](/figures/ref-p181-1.png)

When the Spacemap Go Control is enabled on a Channel or Group, the path's Spacemap Control View of each Channel or Group presents the Spacemap Go control interface. This provides control of the following parameters for the associated Spacemap Go Channel:

- X/Y of Spacemap Panner
- Crossfade
- Spread
- Trajectory Rate
- Trajectory Transport Controls

A 2D panning interface is provided for touch control of the X/Y position of the Spacemap Panner for the assigned Spacemap Go Channel, that can be expanded to reveal all of the details.

![Spacemap Go control view, expanded — X/Y pad, Crossfade, Spread, Rate, and transport controls (manual p.181)](/figures/ref-p181-2.png)

For more information and connection details, please visit https://spacemap-go-help.meyersound.com/digico/

### 2.13.7 Adamson AFM control (V17xx+)

Bi-directional control of Adamson's FletcherMachine is also available. This connects via ethernet to the computer running the FletcherMachine Remote. External Control of an Adamson FletcherMachine can be added via this menu; this allows OSC commands to be sent to the AFM from channel strip controls.

Select AFM Channel Controller in Setup>External Control. Select XY (cartesian) or DA (polar) coordinate mode. Select Master: choose a console fader to control the engine's master fader and mute (optional). Select the additional Layer that can be controlled from the AFM control panel. Choose whether you want Layer Recall with session. Add other OSC device (5321 and 5001 are the default Send and Rcv ports respectively) and make sure the IP address is correct (and in the same subnet as the console) and it is Enabled to allow communication.

![External Control panel — AFM channel controller enabled, XY/DA mode switch and Master select (manual p.182)](/figures/ref-p182-1.png)

When enabled, AFM Control and view buttons are available in the Channel and Group output setup panels.

When activated, the FletcherMachine Controller will replace the regular pan controller. Touch the trackpad on a channel or the AFM button on a group to open the FletcherMachine Controller, with an expanded view available when touching the trackpad in the controller. The following controls are available:

- Object X and Y position (rotaries) — XY mode only
- Center object X and Y position (buttons) — XY mode only
- Object Distance and Azimuth values (rotaries) — DA mode only
- Zero object Distance and Azimuth values (buttons) — DA mode only
- Object Amplitude Width factor (rotary)
- Object rendering Mode (3-way toggle button: MIN, FULL, NONE)
- Additional Layer Send Gain (rotary)
- Additional Layer Send On (button)
- FletcherMachine Reverb Send Gain (rotary)
- FletcherMachine Reverb Send On (button)

The following additional controls are available from the expanded controller panel:

- Object number selection (touch)
- Rendering Space selection (touch)

The following additional controls are available for stereo channels and groups:

- Pair (button) to link/unlink object positions of the stereo pair
- Spread factor (rotary) for linked object positions of the stereo pair

![FletcherMachine Controller, expanded — Object Number list, XY pad, and per-channel rendering controls (manual p.183)](/figures/ref-p183-1.png)

For further details please visit www.adamson-fletcher-machine.com. Please email fmsupport@adamson.ai in case of questions and/or support requests.

### 2.13.8 Sound Devices Astral Control (V20xx+)

The Sound Devices transmitters have an innovative set of control options, with magnetic switches on their A20 TX beltpacks and various control rings for the A20-Handheld transmitter. With the Astral External control device option, Macros can be programmed to be triggered directly from the transmitter, no matter which of the three receivers are in use.

To configure an Astral controller on the console, first navigate to External Control, then select Add Device > Astral.

![External Control panel — Add Device menu with Astral selected (manual p.184)](/figures/ref-p184-1.png)

Check the IP addresses of the Sound Devices hardware and the console. You can see the console IP in the External Control panel, and the Astral IP in the Network menu, under the Control IP header. In console External Control, input your IP Address. Note that Send and Receive ports are fixed when using Astral integration.

![External Control panel — Astral device (Nexus 1) added and enabled (manual p.184)](/figures/ref-p184-2.png)

On the Astral device, enter your Console IP(s). This can be done by navigating through:

**Menu -> System -> Macros -> DiGiCo Console List**

Next, set your Device ID. You can have up to 5 pairs of redundant boxes, or 15 single boxes on your network.

For example, in a system with two Nexus boxes and two consoles/engines, configure the relevant IP addresses on all devices, and set each Nexus box to 1-A and 1-B on both consoles.

| Redundant pairs (up to 5) | Single boxes (up to 15) |
|---|---|
| 1-A / 1-B | 6 |
| 2-A / 2-B | 7 |
| 3-A / 3-B | 8 |
| 4-A / 4-B | 9 |
| 5-A / 5-B | 10 (list continues to 15) |

![Astral Device ID list, in External Control (manual p.185)](/figures/ref-p185-1.png)

Once your IP address has been set on all devices, enable the device(s) in External Control.

When macros have been set up on your Astral device, you are able to select both the Device and Command ID. The Command ID will need to match the OSC ID of the relevant macro on the Astral, while the Device simply matches the DevID set in External Control.

### 2.13.9 Additional Buttons

**HUI Sensing** — Not implemented.

**Suppress OSC Retransmit** — This button blocks the same OSC message from being sent until a new command is sent.

**Bundles** — Selecting Bundles in External Devices will enable the transmission of OSC bundles.
