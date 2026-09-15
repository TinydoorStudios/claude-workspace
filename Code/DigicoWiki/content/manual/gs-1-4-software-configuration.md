# 1.4 Software Configuration

*The Console — manual pages 16–21*

The QUANTUM 2 has a default setup which means that the new user need not get involved in configuring the desk at this stage. However, here is a brief overview of how the different displays are used in putting together a session. Each of the master displays introduced below are described fully within the rest of the manual. The Files > Templates display is used for loading pre-configured session templates. The Files > Session Structure display is used for configuring how the console’s audio channels are to be divided between channel types, and where the format of the channels is defined The Session Structure display can be used to automatically assign the channels to the worksurface. However, channels can also be manually added to the worksurface using the Layout > Channel List display. The Setup > Audio IO display is used to configure the physical I/O connected to the QUANTUM 2, including configuring and naming the sockets of the option cards installed in racks, and the setting of pads and phantom power.

### 1.4.1 Templates

If any templates have been created, they provide an easy starting point for sessions which are already customised to your context. To load a session template, open the Session Templates display by selecting the Templates option at the top of the Files menu. Now touch the template you wish to load from the list shown and press OK.

### 1.4.2 Session Structure Overview

When starting a new session from scratch, it is important to decide how many of each type of channel is required. While changes to session structure can be made once a session has been started, it is best to try and set these parameters before configuring the session. The structure will set items such as the number of input channels, the number and type of aux channels and group channels available

Select session sample rate

![Software Configuration (manual p.16)](/figures/gs-p016-1.png)

![Software Configuration (manual p.16)](/figures/gs-p016-2.png)

Enter session title

Set number of input channels

Set number of Aux busses

Set number of group busses

![Software Configuration (manual p.16)](/figures/gs-p016-3.png)

Total number of spare busses

Total number of unallocated processing

Begin by setting the sample rate at the top of the panel. There is a total of 72 input channels available and 36 busses (plus a Master buss which can be stereo or LCR). Channel resources can be split into input or output channels in almost any configuration. The default configuration is : 48 input channels (Input channel formats are defined within each channel, not within the Session Structure)

1.4 Software Configuration

6 Mono Aux busses & 6 Stereo Aux busses 6 Mono Group busses & 6 Stereo Group busses 12 Matrix Inputs and 12 Matrix Outputs 12 Control Groups

Note that a Talkback channel is also assigned to the control surface, though it isn't configurable within the Session Structure and is therefore not displayed there. To adjust any of the channel allocations, touch on the associated channel count box, and either enter a number using the pop-up number keypad, or adjust using the assigned touch turn controller. Clear All Buttons : When changing routing, you have the option of clearing any non-default routing or processing (EQ, dynamics etc) from the channels in the session. This is especially useful when restructuring an existing session to make a new session.  The other 'clear' buttons in the display perform similar operations. Aux Sends and Direct Sends : By toggling the state of the Aux Sends and Direct Sends Buttons in the Input Channels section, it is possible to change the default operation of the Aux Sends and Direct Sends. These functions toggle between “Post Fader”, “Pre-Fader” and “Pre- Mute”. Aux Order and Group Order : The Aux Order and Group Order buttons open a second window, providing you with the ability to change the order of auxes and groups. By default, mono busses come first, followed by stereo busses. The Master buss is the first stereo buss, regardless of the order you place the busses in. Auto-Route : The Auto-route functions automatically routes consecutive inputs for input channels, and consecutive outputs for busses. For example, auto-routing 72 inputs will route the first physical input (eg 1:Mic 1) to input channel 1, the second physical input (1:Mic 2) to input channel 2…  until you either run out of inputs or channels. Auto-routes are as follows : Input Channels auto-route with physical inputs Aux, Group and Matrix Channels auto route to physical outputs Matrix Inputs auto-route with group outputs

NOTE : Auto-Routing can only be used in conjunction with the “Clear All” button. Rebuild Banks : When changing the number of allocated channels in any section (input channels, busses etc), you can restructure the session without rebuilding banks, meaning that any additional channels you have allocated will not be “placed” on the worksurface, and need to be manually assigned to faders.  If however, you restructure a session with Rebuild Banks (either Horizontally or Vertically) enabled, the worksurface will be built with all channels available on the worksurface in a default layout. Rebuilding horizontally will result in input channels being spread across the top layer of both sides of the console, using as many banks as required, with output channels being assigned to Layer 2. Rebuilding vertically will result in input channels being assigned to Layer 1 on the left side of the console, and output channels to Layer 1 on the right.

### 1.4.3 Audio I/O Overview

The Audio I/O window is used to configure the physical I/O connected to the QUANTUM 2, including configuring and naming the sockets of the option cards installed in racks, and the setting of Pads and phantom power. Local I/O : The QUANTUM 2 provides local audio I/O on the rear of the console. These operate independently of connected racks, providing additional audio I/O. To access the QUANTUM 2 Audio I/O Setup Touch “Setup” on the Master Screen, followed by “Audio I/O” The Audio I/O window that opens is divided up into the following sections

![Software Configuration (manual p.17)](/figures/gs-p017-1.png)

1.4 Software Configuration

The top-left corner of the window shows the ports. Each port relates to an available physical audio connection (Local IO, IO Rack, or MADI Port, USB Audio (UBMADI), DMI cards). Ports can be added and removed using the buttons towards the bottom-left corner of the window.

NOTE: Please refer to the DMI card section of this document for more details on the use of DMI cards in the system The top-right area contains the controls relating to specific ports. When a port is selected, this section changes to reflect the status of the selected port and allows its configuration to be changed as required. Most of the right-hand section of the panel consists of a graphical representation of the rack configuration connected to the selected port. Depending on the port selected, the graphic will change, showing the available physical I/O. Each small “square” on the image represents a single physical audio connection or socket, with these arranged in columns or rows, representing I/O cards in racks, or the local I/O on the back of the console. The section below the graphical rack picture allows configuration of either the cards or slots and sockets (including custom naming, phantom power and pad selection), or card splits and control sharing. The Cards & Sockets and Splits & Sharing buttons define which elements are displayed for configuration. The local I/O configuration is fixed, so no hardware changes are possible. You can, however, change the Port Name, the Group Names (relating to the name of each physical card) and the Socket Names (the name of each physical connector on a card).

### 1.4.4 Opto V221 (SD Racks)

IMPORTANT NOTE: The QUANTUM 2 can only use Optocore via the optional Optocore connections on the console itself. The QUANTUM 2 cannot use an Optocore DMI card to connect to an Optocore system

SD Series consoles can operate with either one of two different Optocore firmware versions - V220 and V221. The Quantum Series can only operate with Optocore firmware version V221. V220  is compatible with DiGiRacks and MiNiRacks and cannot be used with SD Racks or DRacks. V221 is compatible with SD Racks, SD MiNiRacks, NaNoRacks and DRacks, and cannot be used with DiGiRacks and MiNiRacks.

Note: Any type of rack can be used with a Quantum Series console if it is connected with Coaxial BNC MADI irrespective of the Optocore version that the console is using. Sessions that have been created using Optocore connected DiGiRacks and MiNiRacks can be used with SD Racks and DRacks but a procedure must be followed to achieve this. Sessions created using Optocore connected SD Racks and DRacks can also be used with DiGiRacks and MiNiRacks but this also involves a “conversion” procedure.

Note: For detailed information on Optocore system setup please refer to the SD/Quantum Software Reference manual Appendix - DiGiCo Optocore V221 - For SD Rack Optocore Operation

### 1.4.5 Single SD Console System

On a QUANTUM 2, go to Setup > Audio I/O.  Press the Setup Optocore button and the Single Console button will be shown with a bright red background.  Press this button, press Yes at the confirmation stage and the console will create ports for all connected racks, allocate all output cards to your console and create the Optocore map.  The system is now ready to use.

![Software Configuration (manual p.18)](/figures/gs-p018-1.png)

Audio I/O Panel Optocore Setup Single Console

### 1.4.6 Automatic Conforming

Once all hardware is connected, go to System/Diagnostics/Optocore. This will list all connected Optocore devices either SDeng (console engines) to SDRack (SD Rack or D Rack) by ID.  If any expected devices are not listed, please check all physical connections, Optocore ID’s and Fibre Speeds.  Once all devices are present, close the Diagnostics panel. Irrespective of the type of rack being used, the system needs to be conformed. This involves the console checking the type of racks connected and their I/O capability There are three levels of automatic conforming: - globally, using the red Conform All Ports button in the bottom left of the window; - on a rack-by-rack basis, using the conform rack button just below the rack view section of the window;

1.4 Software Configuration

- on a card-by-card basis, by selecting a socket from the card in the graphical display and using the conform card button next to the Card/Slot type button selector in the lower section of the window. (Note that the Cards & Sockets button towards the bottom-left should be selected) Pressing any of these buttons will correctly select the card types for the range in question. Once complete, all of the Card Labels beneath each slot should turn green.

### 1.4.7 Manual Conforming of Racks

With a Rack selected in the left-hand port selection list, the window will look something like the image below, depending on the cards installed in the connected rack. The graphic shows the 14 available card slots, 7 input & 7 output.

![Software Configuration (manual p.19)](/figures/gs-p017-1.png)

In order to use the rack, the on-screen contents of the rack must match the cards physically installed in the rack connected. This is normally achieved by pressing the Conform All Ports button but can also be achieved manually if necessary. Select each card (column) and manually select the appropriate card in the Card/Slot Type drop down menu in the lower section of the window (displayed when the Cards & Sockets button towards the bottom-left is selected). Once the correct card type is selected, the Label at the bottom the selected card will turn green, indicating the card type matches the card installed in the rack. If the Card Type name is Red, then there is a mismatch, and the error should be corrected by selecting the correct card type.

Copying Audio and Listening to Copied Audio (MADI Recorder Setup)

Audio from a Rack can be copied to the MADI Port Output by selecting the incoming Port in the Ports list and using the Copy Audio To drop down menu. For example, if you want to copy the Rack Audio Inputs to a recorder connected over MADI, select Rack 1 in the ports list and then select MADI from the Copy Audio To drop down menu. The 56 inputs on Rack 1 will be copied to the QUANTUM 2 MADI output. In addition, by connecting the recorder's MADI Output to the QUANTUM 2 MADI Input, the playback can be monitored in the same channels as the original source material. Just press the Listen To Copied Audio button to monitor playback and press it again to return to monitoring the live sources from the rack

**Standard MADI Connections**

If you have a standard MADI connection (not a DiGiCo Rack) to your QUANTUM 2, you can set the console to display the MADI with generic signal names, i.e. MADI 1, MADI 2.. etc. through to MADI 56 (or 64) instead of the usual rack style names. The naming does not affect the signal, but makes routing signals easier.

1.4 Software Configuration

**Unrouting All Outputs**

All outputs to the selected port can be unrouted at once by pressing the unroute all outputs button below the cards graphic and selecting yes in the warning pop-up which appears. "Copied" audio is not unrouted by this action.

Note that this will cancel all routing created in the channel screens and cannot be undone.

### 1.4.8 Rack Sharing

In a multi-console system where Racks are connected with MADI and shared between two DiGiCo Consoles, only one of the consoles can take control of the rack, with respect to Gain, Phantom Power and Pads. To overcome this, it is possible to place the QUANTUM 2 into one of 3 states of operation: Isolate : The QUANTUM 2 will not communicate with the rack and therefore any adjustment of input gain or +48V switch will have no effect on the rack settings Receive Only : The QUANTUM 2 will receive the rack’s existing settings but will not be able to control the gain etc on the racks. Full Control : The QUANTUM 2 will send its settings to the racks and change them accordingly. Sharing is configured in the Rack Sharing area, found in bottom right-hand corner of the window when the Splits & Sharing button is selected:

![Software Configuration (manual p.20)](/figures/gs-p020-1.png)

These three states can be set on a per-rack basis (right column), or globally for all shared racks (left column).

### 1.4.9 Assigning Faders to the Worksurface

If, after a Session Restructure, you find that newly created channels do not appear on the worksurface, open the Layout/Channel List panel on the Master screen and you will see a full list of all input and output channels that are present in the session. To assign channels to the worksurface, select a bank and press the LCD Function button. Then press the LCD button labelled Assign Faders to enter that mode and press each of the LCD buttons for the channels that you wish to assign. Now press the first channel that you wish to assign on the Layout > Channel List on the Master screen. Consecutive channels will be assigned to the worksurface for each LCD button that is in Assign mode. Now press the LCD Function button again and return to the standard mode by pressing the LCD button labelled Solo

Note that column widths can be adjusted by dragging their borders within the title row. To return all columns to their default widths, press RESET WIDTHS, in the top left-hand corner of the window.

![Software Configuration (manual p.20)](/figures/gs-p020-2.png)

1.5 Saving and Loading Sessions
