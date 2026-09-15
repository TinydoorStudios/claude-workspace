# 3.1 Console Audio Connections

*Chapter 3: Connections & Multiple Console Setups — manual pages 187–207*

SD/Quantum console external audio connections can be made using either BNC MADI (AES10), Optocore or the DiGiCo Cat5e Connection. There are 2 types of MADI connection available. A DiGiCo Stage rack can be connected to a console via a bi-directional MADI connection will have up to 112 channels (56 in, 56out) of audio plus the control data for the Rack (located on CH57). A Bidirectional standard MADI stream will contain up to 128 channels of Audio (64in, 64out) and can be connected to any 3rd party device that has MADI connection.

A DiGiCo Cat5e connection is a Bidirectional up to 64 Channel l/O interface that uses STP Cat5e Cable with interference suppressors fitted on each end used to connect D-Racks and SD9 and SD11 Consoles, along with MADI-C DMI cards.

### 3.1.1 Optocore V221

*The Q225 here has no Optocore; kept for reference.*

![Optocore setup panel with card status ticks/crosses, rack assignment, lock and remap controls](/figures/ref-p187-1.png)

- Card status for Optocore: Green tick = this console · Red cross = available · Red cross greyed out = unavailable.
- Indicates card type and which Optocore ID has ownership of output cards.
- Assign or disable all Optocore inputs or outputs on selected rack for this console.
- Remaps inputs to local console only.
- Prevents changes to Optocore settings on all consoles in the system.
- Select setup Optocore to view the Optocore settings.
- Optocore remap button - should be used if a message appears indicating "remap required".

**System Overview**

The V221 DiGiCo Optocore fibre system provides users with a highly flexible system. For correct and safe operation of the system, the basic principles need to be understood.

A DiGiCo fibre loop supports up to 10 SD Engines (5 Redundant Consoles) and 14 Racks. These are identified as follows.

Note: For more information on Dual Loop Optocore systems please refer to the relevant section of this document.

SD Engines are allocated ID's between 1 and 10. SD/Quantum consoles with 2 Engines are allocated ID's in consecutive pairs; 1&2, 3&4 etc. Consoles with only one engine such as the SD8 only have a single ID. If 2 SD8s are to be configured as a redundant pair, then their ID's should be allocated consecutively, in the same way that SD/Quantum redundant Engines are paired.

SD Racks (and Optocore enabled D-Racks) are allocated ID's between 11 and 24.

Note: SD Racks can be set to Optocore IDs 1 to 10 but the racks will not work on the Optocore loop if set to these values. These values are used for factory testing only.

As with previous Optocore systems, each device must have a unique ID. Additionally, each device must also be set to run at the same speed. The previous Optocore system was fixed at 1G. The default speed for the Optocore V221 system is 2G.

Each Optocore loop (running at 2G) is capable of 504 channels of audio at either 48k or 96k. On an SD7, up to 2 loops can be operated, providing up to 1008 channels of Optocore I/O.

The Optocore Interface card (between Optocore connected devices and the SD/Quantum Engine) supports 496 Input and 496 Outputs. Inter-console IO is also catered for, allowing the transmission of Audio and Video between SD Engines.

This Optocore system allows for many more channels of audio than can be simultaneously routed into and out of the console. The limit of simultaneously routed signals is 384 inputs and 384 outputs, including routing to local IO and MADI connected devices.

The V221 Optocore implementation provides additional functionality and features over the original Optocore system, as follows.

All inputs (to racks) are available to all consoles. However, it is possible for any console to opt-out of inputs, on a per-input card basis. This means that when the channel routing panel is then opened, only the relevant inputs are accessible. This is particularly in a larger shared system.

Output cards can be allocated / assigned to individual consoles. In practice, this means multiple consoles sharing a single SD Rack to have an output card each.

The Optocore system can be "locked" by any console and reconfiguring of the system is then not possible until all consoles have been placed in an unlocked state. Within a large shared system, this protection mechanism ensures that audio cannot be disrupted by another console on the loop.

To configure these allocations, the Optocore system must be mapped. This map tells each device on the loop which fibre channels it is accessing – Racks insert audio onto the loop and consoles extract audio from the loop or vice versa. For this to operate correctly, a map is built telling each device where it inserts signals onto the loop, and where it extracts audio from the loop.

The process of building this map has been made as simple as possible and can be reduced to a few basic steps.

1. Connect the Consoles and Racks together, as required.
2. Input cards on the racks must be installed in a single block with no gaps between input cards. (So, if your SD Rack only needs 5 input cards, they must occupy the first 5 slots in the rack.)
3. On every console (SD/Quantum Engine), open Audio IO and press the "Conform All Ports". This then will populate the Audio IO panel with all the connected devices. Every console must have the same Audio IO panel configuration.
4. Allocate Rack output cards to consoles as required.
5. Press the "Remap All Optocore" button.

### 3.1.2 FOH & Mons sharing a Stage Rack (MADI)

It is possible for 2 SD/Quantum consoles to share the inputs from a remote rack by using the 2 sets of MADI ports on the rack. In this situation, only one of the consoles can control the rack functions such as the analogue gain of the mic pre-amp and the phantom power switching.

The suggested setup for two SD/Q7 consoles which are sharing the same racks is as follows:

![Shared stage rack wired to FOH and Monitors over MADI, with uni-directional gain tracking from FOH](/figures/ref-p189-1.png)

When using racks on MADI, because each SD/Q7 & Q8 has 2 engines there is a requirement to split the rack's MAIN and AUX MADI OUT signals to feed the second console's MADI IN ports.

The recommended connection between the Monitor console and Stage Rack is a single MADI OUT from the Stage Rack's AUX MADI connected to the console's MADI 1 IN.

The FOH (Master console) is connected via MADI IN and OUT to the stage rack.

A similar method can be used if the Monitor console requires gain control and the FOH console will track the gain changes.

MADI OUT from the Stage Rack's AUX MADI connected to the FOH console's MADI 1 IN.

The Monitor (Master console) is connected via MADI IN and OUT to the stage rack.

1. Open the Setup>Audio I/O panel, select the shared rack port from the port's list (eg Port 1) and then press the Shared button for that rack. Do this on both consoles and the rack control functions Isolate/Receive Only/Full Control will become available.
2. One console should be fully connected to the racks using the Setup>Audio I/O panel's Full Control button for the Shared racks.
3. The operators should agree on and set a level of analogue gain that provides enough headroom for the required application.
4. The second console should connect to the Shared racks in Receive Only mode.
5. Gain Tracking (the Track buttons at the top of the Input channel screen) can be switched on for the console that is in Receive Only mode for all the channels that are being shared.
6. When an analogue gain control is changed on the "Master" console, the "Slave" console's analogue gain should reflect the changes and the digital trim control should compensate for this change by moving by the same amount in the opposite direction.

**Relative Gain-Tracking - Snapshot Recalls Total Gain**

"Relative Gain-Tracking" is implemented as a "Snapshot Recalls Total Gain" option at the bottom of the Snapshot Global Scope panel. When a snapshot recalls an input channel trim, it compares the snapshot's stored analogue gain against the current gain on the channel's input socket. If there's a difference it offsets the value recalled by the trim. This only happens when the socket's rack is in Receive Only, or the analogue gain is not in Recall Scope.

### 3.1.3 FOH & Mons sharing a stage SD Series Rack (MADI)

When using SD Racks, the setup is very similar, but the rack split from an SD Rack can be achieved without an external splitter. The SD rack has two built in split outputs which can each provide a 56 channel MADI stream at 48KHz. The added advantage of the SD rack split is that it can be set to provide an automatically gain tracked MADI stream. This can be set on the rack itself or from the Audio I/O panel on the console. This means that the receiving console does not need to provide the gain tracking facility.

Note: The console that is controlling the gains should be set to setup/audio sync = Master and the console that is tracking should be set to setup/audio sync = MADI 1.

### 3.1.4 FOH & Mons sharing DiGiRacks (Optocore V220)

*The Q225 here has no Optocore; kept for reference.*

If 2 SD7's and DiGiRacks are connected via optical fibre, a similar setup can be achieved in the following way:

![Two SD7 consoles and two Optocore DiGiRacks in a redundant fibre loop, each console also carrying a local MADI DiGiRack](/figures/ref-p191-1.png)

In this setup, you are limited by Optocore firmware Version 220 to four SD7 engines (2 consoles) and four Optocore connected racks. The system can only run at a sample rate of 48KHz.

Only one of these consoles will be able to use the outputs on Optocore connected racks and this console must be set to Optocore ID1 (Engine A) and ID2 (Engine B), The other console should be set to ID3 (Engine A) and ID4 (Engine B).

These IDs are set from the Network panel in the Master screen.

The four racks can have any Optocore ID in the range ID30 to ID33. In the above example they have ID30 and ID32. These IDs are set on the racks themselves.

The connections that should be made are shown in the diagram, as follows:

The fibre optic cables connect between each device on the optic loop and connect an "A Port" to a "B Port". You should not connect the optic cables in A-A or B-B configurations. The cables connect between each device to form a closed loop. This is necessary for the redundant loop to operate correctly.

The diagram also shows each console having a local MADI connected DiGiRack using BNC MADI cables.

The DiGiRack Main MADI Port is connected to one of the MADI Ports on Engine A and the Aux MADI Port is connected to the same numbered port on Engine B.

Open the Setup > Audio Sync panel and set the Sync source to be Optocore. Do this on both engines of both consoles. Save and Send the Session from the A engine on each console to its B engine and Mirror each pair of engines.

Now open the Setup > Audio IO panel on the A engine of both consoles and press the Conform All Ports button in the bottom left corner. The console will "look" down the connected optical fibre cables and auto discover and conform all the racks it can find. In this example, they will find 2 optic stage racks. This function will be automatically mirrored to the B engine on each console.

In its default setup, none of the Optocore connected DiGiRacks will be defined as shared. This means that either console will be able to control the rack and adjust Mic Amp Gain, Phantom Power, output pads etc.

If you are happy for either desk to control the racks, then you can leave the sessions with these default settings. Making changes to this default state allows you to define the shared status of each rack. If you set a rack to be in full control, then that console will have full control of the rack.

If you set a rack to be in receive only mode, then that console will not be able to make changes to mic amp gain etc but will "see" the changes made by the other console. This is necessary for Gain Tracking to function. The third option is isolate, and when in this mode, the console will not be able to make changes, nor see changes made by someone else. Gain tracking will not work if the rack is set in isolate mode.

To set a console as the master controller for the racks: In the Audio IO Panel, select the appropriate stage rack. Press the Splits and Sharing button. In the section titled Selected Rack, press the shared button. It will default to the Isolate setting. Then press the full control button. A warning will remind you that going into full control may affect the live audio. then press Yes. If required, repeat this process for the second stage rack.

To set racks to be in receive only mode: In the Audio IO Panel, select the appropriate stage rack. Press the Splits and Sharing button. In the section titled Selected Rack, press the shared button. It will default to the Isolate setting. Then press the receive only button. A warning will remind you that your session will change to correctly reflect the actual settings on the rack. then press Yes. If required, repeat this process for the second stage rack.

### 3.1.5 FOH & Mons sharing SD Series Racks (Optocore V221)

*The Q225 here has no Optocore; kept for reference.*

![Two consoles and a pair of SD Racks in a redundant Optocore fibre loop, each console also carrying a local MADI SD Rack](/figures/ref-p193-1.png)

It is possible for up to 5 DiGiCo consoles to share the inputs from remote stage SD Racks using optical fibre cables. It is also possible for the output cards in the SD Racks to be allocated to the consoles on a card by card basis.

The following example describes how to set up 2 consoles with a pair of stage racks in a Front of House & Monitors configuration. The connections that should be made are shown in the diagram, as follows.

The fibre optic cables connect between each device on the optic loop and connect an "A Port" to a "B Port". You should not connect the optic cables in A-A or B-B configurations. The cables connect between each device to form a closed loop. This is necessary for the redundant loop to operate correctly.

The diagram also shows each console having a local MADI connected SD Rack. These are connected using pairs of BNC MADI Cables between one of the MADI ports on the console and the Main MADI ports on the SD Racks. Additional redundant MADI cables can be used, connected the redundant MADI ports on the console to the Aux MADI Ports on the SD Rack.

**Console Setup & Operation**

To ensure correct operation of this system, it is necessary to ensure that the console and session settings are correct.

Each optically connected device must have a unique ID. On each console, open the Network panel on the Master Screen. From the drop-down list at the top of the panel, set the ID of each console. We would recommend setting the FOH console to ID1 and ID2 and the monitor console to ID3 and ID4. Even numbered IDs are used for Redundant engines in Mirrored engine setups therefore if you were mirroring two single engine consoles, they should be set as ID1 for the FOH console and ID3 as the Monitor console.

Similarly, each SD Rack should have its ID set. Rack ID's start from 11; this example uses Optocore ID's 11 & 12 for the 2 connected racks.

On each console, ensure that the session sample rates are the same. The sample rate is set in the Files > Session Structure panel. Open the Setup > Audio Sync panel and set the Sync source to be Optocore. Do this on both engines of both consoles. Save and Send the Session from the A engine on each console to its B engine and Mirror each pair of engines. Then open the Setup > Audio IO panel on the A engine of both consoles and press the Conform All Ports button in the bottom left corner. The console will "look" down the connected optical fibre cables and auto discover and conform all the racks it can find. In this example, they will find 2 optic stage racks.

If the conformed racks in each of the engine's Audio IO panels do not match the other console, then the system will not map correctly. Before the system is mapped, you should allocate any SD Rack output cards. Press the Setup Optocore button select / deselect output cards as required. Once this is complete, press the Remap All Optocore button.

[For more detailed information on the Optocore Setup, please refer to Optocore_221_User_D.pdf which is available for download from the Support section of the DiGiCo website).

In its default setup, none of the Optocore connected SD Racks will be defined as shared. This means that either console will be able to control the rack and adjust Mic Amp Gain, Phantom Power, output pads etc.

If you are happy for either desk to control the racks, then you can leave the sessions with these default settings. Making changes to this default state allows you to define the shared status of each rack. If you set a rack to be in full control, then that console will have full control of the rack. If you set a rack to be in receive only mode, then that console will not be able to make changes to mic amp gain etc but will "see" the changes made by the other console. This is necessary for Gain Tracking to function. The third option is isolate, and when in this mode, the console will not be able to make changes, nor see changes made by someone else. Gain tracking will not work if the rack is set in isolate mode.

To set a console as the master controller for the racks: In the Audio IO Panel, select the appropriate stage rack. Press the Splits and Sharing button. In the section titled Selected Rack, press the shared button. It will default to the Isolate setting. Then press the full control button. A warning will remind you that going into full control may affect the live audio. then press Yes. If required, repeat this process for the second stage rack.

To set racks to be in receive only mode: In the Audio IO Panel, select the appropriate stage rack. Press the Splits and Sharing button. In the section titled Selected Rack, press the shared button. It will default to the Isolate setting. Then press the receive only button. A warning will remind you that your session will change to correctly reflect the actual settings on the rack. then press Yes. If required, repeat this process for the second stage rack.

### 3.1.6 4REA4 I/O Control (Optocore V221 and MADI)

An SD/Quantum console can control the IO of a DiGiCo 4REA4 over either MADI or Optocore.

This enables a 4REA4 to be used similarly to a Rack, and as part of an Optocore loop configuration.

NOTE: In this configuration the SD/Quantum console must be running at 96KHz to match the sample rate of the 4REA4.

Connect any SD/Quantum console to a 4REA4 with MADI or Optocore and have Rack audio and parameter control of up to 64 IO sockets on Racks connected to the 4REA4.

With an external Rack connected via MADI to the 4REA4, the MADI Mode Selection should be set to "Rack Control" and Rack Control Mode to "Full Control" in order to send control data to the connected Rack.

This is found under the relevant DMI port I/O settings in Engine -> Audio on the 4REA4 controller. A168 Racks can also be controlled in this manner when connected to the 4REA4 via an A3232 port.

![4REA4 DMI Port panel: MADI-B, Rack Control Mode set to Full Control](/figures/ref-p195-1.png)

With an SD/Quantum console connected via Optocore to the 4REA4, the Input Channel Count and Output Channel Count should be set to the number of channels that need to be controlled. The SD/Quantum console can also be connected via MADI to the 4REA4 with the MADI Mode Selection set to "SD console."

![4REA4 DMI Port panel in Optocore mode, showing Optocore ID, fibre speed, and Input/Output Channel Count](/figures/ref-p196-1.png)

Tie Lines connecting the MADI Rack inputs to the Optocore outputs, Tie Lines can be set up in the other direction to allow output socket control. This creates a link for audio and control data. The whole IO or specific sockets can be tie lined up to a total of 64.

![Routing > Tie Lines matrix patching DMI 1 Optocore outputs to DMI 2 MADI inputs](/figures/ref-p196-2.png)

Once the 4REA4 has been set up with the correct DMI card settings and Tie Lines are in place, in the SD/Quantum console Audio IO window, a "4REA4 Port" can be added from the Add Port drop down menu and then using the Conform Port function or by using the Conform All Ports function.

![Audio IO panel with a 4REA4 port added from the Add Port menu](/figures/ref-p197-1.png)

This will populate that port with the relevant socket types that have been declared and "tie-lined" in the 4REA4.

When 4REA4 Rack input sockets are subsequently routed into channels on the SD/Quantum console, the relevant analogue gain and +48V controls will be available in those channels. For output sockets, the output pads can be toggled (if applicable) and SRC can be turned on or off on AES outputs.

### 3.1.7 MADI DMI (SRC) (for consoles with DMI slots)

Sample rate conversion (SRC) is available for DMI MADI cards running V167+. The settings for this are managed in the audio I/O panel.

Three sample rates are available to select - 48kHz, 96kHz smux and 96kHz hispeed.

The selected sample rate must match the sample rate of the connected device. There is no auto SRC function.

The internal console sample rate and the sample rate of the connected device will determine the SRC state shown. It will either show as SRC active or SRC inactive.

![Audio IO panel for a MADI 64 port showing SRC Inactive, connected device at 48kHz, smux/hispeed options](/figures/ref-p198-1.png)

### 3.1.8 Dante 64@96 (for consoles with DMI slots)

The Dante 64@96 DMI card allows the console to route 64 channels to and 64 channels from a Dante network at either 48kHz or 96kHz. The console can have a different internal sample rate to the Dante network by turning 'Auto SRC' on. This feature will automatically detect a difference in sample rate (either 48kHz or 96kHz) and activate sample rate conversion.

![Audio IO panel for a Dante64 port: current sample rate of the Dante network and console, Auto SRC toggle, and SRC state](/figures/ref-p199-1.png)

**Clocking**

All control and configuration of the Dante interface is done externally by the Dante controller software. A separate control computer must be provided to do this.

The Dante network can be set to use the console as the network system clock (in the Dante Controller software) or the Dante card can be selected as the console clock source.

In the picture below, the Dante Controller software displays a Dante 64@96 DMI card and an A168D rack.

In the Dante Device Config tab, the A168D rack must be set to match the Dante 64@96 DMI card sample rate at 48kHz or 96kHz.

**Example 1 - Console is Master clock for Dante Network**

In the Dante Clock Status tab, the Dante 64@96 DMI card is set to "Sync To External" and "Preferred Master". This setup enables the DMI card to take its Audio Sync Source from the console itself and in turn provide sync to the rest of the Dante network. The console would typically be set to sync MASTER.

![Dante Controller Clock Status tab with Display/Set Preferred Master and Sync To External, and the console's Sample Rate dialog](/figures/ref-p200-1.png)

**Example 2 - Dante Network is Master clock for console**

If the console is required to use the Dante network as its sync source the following settings should be applied.

Enable Sync to External = OFF

**Dante IO (V1280+)**

Socket parameters on A168D and A164D IO racks can be controlled in the same way as other DiGiCo I/O racks when connected to a Dante 64@96 DMI card and routed in Audinate's "Dante Controller" software.

With a Dante DMI 64@96 card installed in a console, access to 64 channels of IO to/from the Dante network is provided.

A Dante IO box can provide a specific number of IO on the Dante network according to the rack's capability.

168D = 16 analogue In and 8 Analogue Out.

Any Dante network may have many more devices on it than just a single console and rack.

There might be multiple Dante equipped consoles, multiple racks and other Dante devices.

When a console has a Dante DMI fitted, it "sees" that DMI as a 64 channel interface device to/from the Dante network.

The source device of the audio signals it is receiving across that interface and the destination device of any signals that it is sending out across that interface are generally "unknown" to the console.

The critical component in determining where the audio is going to/from is the Dante network controller which is responsible for setting up audio paths (routing) on the network.

As an example, using just a single console and a single rack, the console could use its Dante DMI channel 1 as an input signal to its own console Input Channel 1 but the audio signal which appeared on that DMI Dante channel could be any signal from the Dante IO rack and is determined by the routing in the Dante Controller.

With the following routing in place, a console that selects any of the DMI card channels 1-16 as an input source will receive the signal from the same numbered Rack Input socket – this is a logical setup.

### 3.1.9 DQ-Rack (for consoles with DMI cards) [V1455+]

PLEASE NOTE that for the connection and use of the DQ-Rack, there is a requirement for the following firmware updates to the Dante 64@96 DMI card:

1. DMI Dante 64@96 firmware update (v103) which is included in the update package.
2. A Dante firmware update (4.0.20) for the DMI card which can be updated using Dante Updater in Dante Controller.

Socket parameters on the DQ-Rack can be controlled in the same way as other DiGiCo I/O racks when connected to a Dante 64@96 DMI card and routed in Audinate's "Dante Controller" software.

With a DMI Dante 64@96 card installed in a console, access to 64 channels of IO to/from the Dante network is provided.

DQ-Rack can provide access to 48 analogue Inputs and 24 analogue outputs.

If the DQ-Rack AES outputs are active, these are accessed using Dante Channels 49-56.

![Audio IO panel with Device Type set to DMI DANTE64, showing the DQ-Rack's 48 analogue inputs](/figures/ref-p202-1.png)

![A168D Rack as a Transmitter: each of its 16 input sockets routed to the same-numbered DMI 64@96 channel, shown in Dante Controller routing with the receiving console](/figures/ref-p203-1.png)

![Dante Controller routing view: Dante Receivers column with the matched channels highlighted](/figures/ref-p203-2.png)

![Dante Controller routing view, Dante Receivers column zoomed](/figures/ref-p203-3.png)

![Console 1's DMI 64@96 port showing Auto SRC On and SRC Active](/figures/ref-p203-4.png)

![Console 1's DMI 64@96 port connected OK, Dante SR and Console SR both shown](/figures/ref-p203-5.png)

In this example, a console that routes signal to DMI card output channels 1-8 will be sending them to the same numbered Rack Output socket.

![Console 1's DMI 64@96 as a Transmitter: outputs 1-8 routed via the network switch to the same-numbered Rack output sockets in Dante Controller routing](/figures/ref-p204-1.png)

### 3.1.10 MQ-Rack [V1528+]

Socket parameters on the MQ-Rack can be controlled in the same way as other DIGiCo I/O racks when connected to local console MADI or DMI MADI card.

MQ-Rack can provide access to 48 analogue Inputs and 24 analogue outputs.

MQ-Rack provides interchangeable AES outputs on output sockets: 6, 12, 18 and 24. Output sockets can be changed to AES Outs in Audio I/O panel found in Setup>Audio I/O. Changing an analogue socket to AES will give access to two 2 AES Outs. Changing socket type makes the other type inactive. Audio can be routed to an inactive socket, but no audio will pass until socket type is active.

![Audio IO panel with Device Type set to MQ-Rack, showing 48 analogue inputs and the Line Out/AES switch on the outputs, with inactive outputs blanked out](/figures/ref-p205-1.png)

![Ch01 Direct Output Routes window with an inactive output greyed out in the channel output routing view](/figures/ref-p205-2.png)

Note analogue and AES outputs are switchable from the Audio I/O panel on SD/Quantum consoles as of the V1528 release.
