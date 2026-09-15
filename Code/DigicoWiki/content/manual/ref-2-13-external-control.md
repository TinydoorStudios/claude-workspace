# 2.13 External Control

*Chapter 2: The Master Screen — manual pages 172–187*

### 2.13.1 iPad Control

The DiGiCo SD/Quantum app allows remote, wireless control of any DiGiCo SD or Quantum mixing console from your Apple iPad.

To activate iPad Control:

1. Navigate to Setup > External Control from the menu on the main screen

2. Enable External Control by pressing the button at the top of the panel - please disable this function

when External Control is not required

3. Press the Add Device button and select DiGiCo Pad

4. Enter a Device Name (user choice) for the device and then enter the IP Address of the iPad 4)

5. Enter Send and Receive Port numbers for the console e.g. Send = 9000 and Receive = 8000 Note: If you

enter multiple devices in this panel, they must all have unique Send and Receive ports.

6. Tick the Enable column for this device.

7. Press the Load button in the bottom right corner of the panel and select the commands button for the

relevant console. There are several different sets of commands, one for SD8, SD9, SD11 and SD12 another for SD5, SD7 and SD10 and others which are specific to Quantum console models.

NOTE: Only one set of commands should be loaded at one time and if in doubt about which one is loaded, please press the Clear All button and then reload the relevant commands for your console.

8. Take note of the console Local IP Address at the bottom of the panel as this information will have to be

entered on the Connect page of the DiGiCo iPad App.

2.13 External Control

![External Control (manual p.173)](/figures/ref-p173-1.png)

Enable External

![External Control (manual p.173)](/figures/ref-p173-2.png)

Control

![External Control (manual p.173)](/figures/ref-p173-1.png)

Add device type –

DiGiCo Pad

![External Control (manual p.173)](/figures/ref-p173-3.png)

![External Control (manual p.173)](/figures/ref-p173-1.png)

Enter iPad details

![External Control (manual p.173)](/figures/ref-p173-4.png)

![External Control (manual p.173)](/figures/ref-p173-5.png)

Load iPad commands for relevant console Labels: (only required on · first setup) · 2.13 External Control

### 2.13.2 Generic OSC

This feature allows any device that can transmit and receive OSC messages to be connected a desk. The Generic OSC control has 8 rotary and 8 switch controllers that can have their names, values and operating ranges defined in the Generic OSC customise section of the External Control panel.

To activate Generic OSC Control:

1. Navigate to Setup > External Control from the menu on the main screen.

2. Enable External Control by pressing the button at the top of the panel - please disable this function

when External Control is not required.

3. Press the Add Device button and select Generic OSC Device.

4. Change the Input Channel Controller to OSC Generic.

5. Select Other OSC from the drop-down list and then enter a device name, the IP address and

Send/Receive ports for the Generic OSC device.

Note: If you enter multiple devices in this panel, they must all have unique Send and Receive.

6. Tick the Enable column for this device.

7. Press the Customise button and enter a label, required OSC message, min, max and default values for

the relevant control. Press rotaries or switches to view the settings for the 2 sets of 8 controls.

Note: The first four rotaries can be controlled by the graphical touch controls within the expanded panel.

8. OSC messages should contain an asterisk (*) to represent the channel number Eg.

/MyDevice/MyParameter/*

![External Control (manual p.174)](/figures/ref-p174-1.png)

2.13 External Control

### 2.13.3 L’Acoustics L-ISA

External Control for an L’Acoustics L-ISA system can be added via this menu, this allows OSC commands to be sent to L-ISA from channel strip controls.

To activate L-ISA Control:

1. Navigate to Setup > External Control from the menu on the main screen.

2. Enable External Control by pressing the button at the top of the panel - please disable this function

when External Control is not required.

3. Change the Input Controller to L-ISA.

4. Press the Add Device button and select L-ISA.

5. Select Other OSC from the drop-down list and then enter a device name, the IP address and

Send/Receive ports for the L-ISA device.

Note: If you enter multiple devices in this panel, they must all have unique Send and Receive

L-ISA control can be activated on a channel by pressing ‘L-ISA Control’ at the bottom of the output panel. This will display a small plot of L-ISA pan position on the channel strip itself, this area can be pressed to open L-ISA Source Control panel (right) where L-ISA parameters can be adjusted. This can be hidden by pressing the ‘view’ button.

![External Control (manual p.175)](/figures/ref-p175-1.png)

![External Control (manual p.175)](/figures/ref-p175-2.png)

2.13 External Control

Stereo channels can also have L-ISA control, in which they gain another row of rotary controls on the Source Control panel, plus ‘pan spread rotary’ and’ ‘link’ button.

![External Control (manual p.176)](/figures/ref-p176-1.png)

![External Control (manual p.176)](/figures/ref-p176-2.png)

Control L-ISA groups from this panel

![External Control (manual p.176)](/figures/ref-p176-3.png)

Adjust the

distance between Labels: the left and · right leg of · the

channel in

L-ISA

Link the left and right leg controls together

L-ISA groups can be pressed in the ‘L-ISA groups’ selection to allow them to be controlled from the L-ISA panel.

2.13 External Control

Selection Sync can be activated in L-ISA controller so that when a channel is selected on the console, it is also selected in L-ISA controller and vice versa.

![External Control (manual p.177)](/figures/ref-p177-1.png)

Have channel selection on desk and L-ISA follow each other

Channel faders can be linked with the L-ISA master fader so that the output of L-ISA can be adjusted without leaving the console surface. This is assigned in the ‘External Control’ panel.

![External Control (manual p.177)](/figures/ref-p177-2.png)

![External Control (manual p.177)](/figures/ref-p177-3.png)

Select the fader to link to the L-ISA master fader

2.13 External Control

### 2.13.4 d&b Soundscape Control

Bi-directional control of d&b Soundscape is also available. For remote control to work, a DS100, a computer running d&b ArrayCalc/R1 and a computer running En-Bridge are required.

There is a d&b button in Setup>External Control.  Adding an other osc device will allow communication.

![External Control (manual p.178)](/figures/ref-p178-1.png)

![External Control (manual p.178)](/figures/ref-p178-2.png)

Once enabled in the External Control panel, d&B Control and view buttons will appear in the bottom of Input Channel and Group Output Output Setup Panels.  When activated for a specific channel, the buttons will have a red background and a Soundscape control will replace the standard channel Pan controller.  When the Soundscape control on the channel strip or the d&b button on a group is pressed, the Soundscape Control panel will open.

![External Control (manual p.178)](/figures/ref-p178-3.png)

The controls are:-

- 

Sound Object x Position (rotary)

- 

Sound Object y Position (rotary)

- 

Sound Object Spread factor (rotary)

- 

Sound Object En-Space Send Gain (rotary)

- 

Sound Object Delay Mode (3 toggle buttons)

- 

Touch the small x/y position display in the expanded view to further expand the display.

- 

Touch on the Object Number button to select which sound object that the channel strip shall control.

- 

Touch on the Mapping button to select which mapping area shall be targeted from the channel strip's controls.

Full details of the integration can be found at www.dbaudio.com

2.13 External Control

### 2.13.5 KLANG Control

![External Control (manual p.179)](/figures/ref-p179-1.png)

Transmit all stored KLANG parameters to the controller on session load

![External Control (manual p.179)](/figures/ref-p179-2.png)

Bypass all KLANG nodes – temporarily reverted to normal aux sends

![External Control (manual p.179)](/figures/ref-p179-3.png)

The KLANG level and aux send level will be stored as the same value (if KLANG is bypassed or disabled, the aux send level will be the KLANG level).

![External Control (manual p.179)](/figures/ref-p179-4.png)

![External Control (manual p.179)](/figures/ref-p179-5.png)

Enable KLANG control and nodes

![External Control (manual p.179)](/figures/ref-p179-6.png)

Enter the details of the KLANG controller

The KLANG automated setup process can be automated to some extent - Please follow this link for more information - https://www.klang.com/product/console-integration/

### 2.13.6 Spacemap Go control (V17xx+)

DiGiCo and Meyer Sound Laboratories, Incorporated have worked in partnership to provide integrated control of a Spacemap Go immersive loudspeaker system from the console interface. Spacemap Go Channels can be associated with console Channels or Groups, with full control of:

Spacemap Go Panner, Crossfade, Spread and Trajectory transport controls are available from the console for each Spacemap Go Channel. The control view also provides the Channel name, both Spacemap names, and the trajectory name if active.

The Spacemap Server runs on the GALAXY network platform processor, and the Spacemap Go iPad app, as well as all external controllers are connected as clients to the server.

This feature is available when using the following software and firmware versions, or more recent releases:

- 

DiGiCo Console software V1742

- 

Meyer Sound Compass version 4.13.1, which includes Meyer Sound GALAXY firmware version 2.8.1

2.13 External Control

- 

Meyer Sound Spacemap Go version 1.2.2, available at the Apple App Store

Spacemap Go Control will be configured in the DiGiCo console’s EXTERNAL CONTROL options tab (MASTER SCREEN > SETUP > OPTIONS). In the Channel Controllers panel, select SpaceMap.

Select Add device and other OSC, then enter the required IP Address and Send/Rcv port numbers as required. Confirm by pressing in the Enabled column.

![External Control (manual p.180)](/figures/ref-p180-1.png)

Control of a Spacemap Go Channel can be enabled on any of the console’s Channel or Groups. Navigate to the channel and open the Controller view by tapping on CHANNEL > OUTPUT SETUP, at the bottom of the popover window enable Spacemap Controller, then View. Close the popover and touch on the 2D XY Panner, the external controls will appear.

![External Control (manual p.180)](/figures/ref-p180-2.png)

The assigned Spacemap Go channel can be changed by clicking on the blue box with the currently assigned Spacemap channel in white.

2.13 External Control

![External Control (manual p.181)](/figures/ref-p181-1.png)

![External Control (manual p.181)](/figures/ref-p181-2.png)

Available Controls from the Console Channel or Group.

When the Spacemap Go Control is enabled on a Channel or Group, the path’s SPACEMAP CONTROL VIEW of each Channel or Group presents the Spacemap Go control interface. This provides control of the following parameters for the associated Spacemap Go Channel:

- 

X/Y of Spacemap Panner

- 

Crossfade

- 

Spread

- 

Trajectory Rate

- 

Trajectory Transport Controls

A 2D panning interface is provided for touch control of the X/Y position of the Spacemap Panner for the assigned Spacemap Go Channel that can be expanded to reveal all of the details.

![External Control (manual p.181)](/figures/ref-p181-3.png)

For more information and connections details please visit https://spacemap-go- help.meyersound.com/digico/

2.13 External Control

### 2.13.7 Adamson AFM control (V17xx+)

Bi-directional control of Adamson’s FletcherMachine is also available. This connects via ethernet to the computer running the FletcherMachine Remote. External Control of an Adamson’s FletcherMachine can be added via this menu, this allows OSC commands to be sent to the AFM from channel strip controls.

Select AFM Channel Controller in Setup>External Control. Select XY (cartesian) or DA (polar) coordinate mode. Select Master: choose a console fader to control the engine’s master fader and mute (optional). Select the additional Layer that can be controlled from the AFM control panel. Choose whether you want Layer Recall with session. Add other OSC device (5321 and 5001 are the default Send and Rcv ports respectively) and make sure the IP address is correct (and in the same subnet as the console) and it is Enabled to allow communication.

![External Control (manual p.182)](/figures/ref-p182-1.png)

When enabled, AFM Control and view buttons are available in the Channel and Group output setup panels.

![External Control (manual p.182)](/figures/ref-p182-2.png)

When activated, the FletcherMachine Controller will replace the regular pan controller. Touch the trackpad on a channel or the AFM button on a group to open the FletcherMachine Controller, with an expanded view available when touching the trackpad in the controller. The following controls are available:

- Object X and Y position (rotaries) – XY mode only - Center object X and Y position (buttons) – XY mode only

2.13 External Control

- Object Distance and Azimuth values (rotaries) – DA mode only - Zero object Distance and Azimuth values (buttons) – DA mode only - Object Amplitude Width factor (rotary) - Object rendering Mode (3-way toggle button: MIN, FULL, NONE) - Additional Layer Send Gain (rotary) - Additional Layer Send On (button) - FletcherMachine Reverb Send Gain (rotary) - FletcherMachine Reverb Send On (button) The following additional controls are available from the expanded controller panel:

- Object number selection (touch) - Rendering Space selection (touch) The following additional controls are available for stereo channels and groups:

- Pair (button) to link/unlink object positions of the stereo pair - Spread factor (rotary) for linked object positions of the stereo pair

![External Control (manual p.183)](/figures/ref-p183-1.png)

For further details please visit www.adamson-fletcher-machine.com. Please email fmsupport@adamson.ai in case of questions and/or support requests.

### 2.13.8 Sound Devices Astral Control (V20xx+)

The Sound Devices transmitters have an innovative set of control options, with magnetic switches on their A20 TX beltpacks and various control rings for the new A20-Handheld transmitter. With the Astral External control device option, Macros can be programmed to be triggered directly from the transmitter, no matter which of the three receivers are in use.

To configure an Astral controller on the console, first navigate to external control, then select add device ->

**Astral**

2.13 External Control

![External Control (manual p.184)](/figures/ref-p184-1.png)

Check the IP addresses of the Sound Devices hardware and the console. You can see console IP in the External Control panel, and the Astral IP in Network menu, under the Control IP header. In console External Control, input your IP Address. Note that Send and Receive ports are fixed when using Astral integration.

![External Control (manual p.184)](/figures/ref-p184-2.png)

On the Astral device, enter your Console IP(s). This can be done by navigating through:

**Menu -> System -> Macros -> DiGiCo Console List**

Next, set your Device ID. You can have up to 5 pairs of redundant boxes, or 15 single boxes on your network.

For example, in a system with two Nexus boxes and two consoles/engines, configure the relevant IP addresses on all devices, and set each Nexus box to 1-A and 1-B on both consoles.

2.13 External Control

![External Control (manual p.185)](/figures/ref-p185-1.png)

Once your IP address has been set on all devices, enable the device(s) in External Control.

When macros have been set up on your Astral device, you are able to select both the Device and Command ID. The Command ID will need to match the OSC ID of the relevant macro on the Astral, while the Device simply matches the DevID set in External Control.

### 2.13.9 Additional Buttons

**HUI Sensing (Not implemented)**

**Suppress OSC Retransmit**

This button blocks the same OSC message from being sent until a new command is sent.

**Bundles**

Selecting Bundles in External Devices will enable the transmission of OSC bundles.

2.13 External Control

3.1 Console Audio Connections
