# 2.12 Setup Menu

*Chapter 2: The Master Screen — manual pages 149–170*

### 2.12.1 Audio I/O

The Audio I/O display is used to configure the physical I/O connected to the SD/Quantum console, including identifying and naming the sockets of the option cards installed in racks, and the setting of pads and phantom power.

![Audio I/O panel — port list, socket grid, Copy Audio To, Cards & Sockets, and Splits & Sharing controls (manual p.150)](/figures/ref-p150-1.png)

### 2.12.2 Port Selection

Each port relates to a set of physical audio connections:

| Port | Description |
|---|---|
| Local I/O | The I/O installed in the rear of the console. |
| Rack | A remote I/O rack connected via MADI or Optocore. |
| Con | A separate console connected using MADI or Optocore. |

To select which port is currently being configured, touch the name of desired port under the Audio I/O port column in the top left corner of the window. Once a port has been selected, the connections contained within it are displayed in the socket's graphic.

New ports can be added to the session by touching the add port button, below the Audio I/O port column. A drop-down list of predefined port configurations will appear, allowing you to select the appropriate device. These user created ports can be deleted by pressing the remove port button, below the add port button.

**Copying Audio and Listening to Copied Audio (MADI Recorder Setup)**

Any incoming MADI or Optocore connected rack stream can be copied to any other MADI Output by selecting the incoming port in the ports list and using the Copy Audio To drop down menu. For example, if you want to copy Rack 1's Audio Inputs to a MADI equipped recorder connected on port 2, select port 1 in the ports list and then select MADI 2 from the Copy Audio To drop down menu. The console will send the 56 or 64 channel MADI stream to MADI Output 2 and it can be recorded as necessary. In addition, by connecting the recorder's MADI Output to the console's MADI 2 Input, the playback can be monitored in the same channels as the original source material. Just press the Listen To Copied Audio button to monitor playback and press it again to return to monitoring the live sources from the rack. When Listen to Copied Audio is active, "Listening to Copied Audio" is displayed in the session status panel of the master screen.

Note: More complex inter port routing is possible using the Copy Audio Panel, please see the Copy Audio section of this manual.

Note: KLANG Konduktor has been added as port and device type in v1528.

### 2.12.3 Port Hardware Configuration

The port is named automatically according to its connection type, as displayed to the right of the ports selection area. However, the name can be edited by touching the Port Name box or the keyboard symbol to its right, typing the new name into the QWERTY keyboard which appears, and pressing OK. The type of device connected to the port can be altered by touching the down arrow next to the Device Type box, located next to the Port Name box, and selecting the appropriate device from the drop-down list that appears. The physical port being used to connect the device can be altered by touching the down arrow next to the Connection box, to the right of the Device Type box, and selecting the appropriate connection port from the drop-down list that appears. The status of the connection is displayed below the Connection box as either connected (in green) or not connected (in red).

Note: The configuration of the Local I/O port is fixed, so no hardware changes are possible. You can, however, change the Port Name, the Group Names (relating to the name of each physical card) and the Socket Names (the name of each physical connector on a card).

### 2.12.4 Port Control

Normally, the input gain, phantom power and pad of each DiGiCo Rack input is controlled remotely from the SD/Quantum console. However, in multi-console systems where Racks are shared between two DiGiCo consoles with MADI Connections, only one of the consoles can remotely control these rack settings. With Optocore connections any console can have control. Therefore, the level of control given to each console must be defined. Control options are displayed in the bottom-right area of the Audio I/O panel when the Splits & Sharing button towards the base of the panel is pressed:

![Splits & Sharing control panel — isolate / receive only / full control options (manual p.152)](/figures/ref-p152-1.png)

There are three levels of control:

| Level | Behavior |
|---|---|
| isolate | The SD/Quantum console will not exchange any control data with the rack. This means that the console will neither be able to adjust rack settings, nor adjust its own settings according to returning control data. |
| receive only | The SD/Quantum console will receive the rack's existing settings but not send control data back. This means that the console will not be able to adjust rack settings but will be able to adjust its own settings according to returning control data. |
| full control | The SD/Quantum console will receive the rack's existing settings and will send control data back. This means that the console will be able to adjust the rack's settings and receive tallies back from the rack. |

Under the Selected Rack column, control can be defined as shared by pressing the Shared button. Individual racks can also be controlled using the isolate, receive only and full control buttons beneath the Shared button — these buttons will only affect the selected port.

### 2.12.5 The Socket Display

When a port has been selected from the ports list on the left, the individual connections within that port are displayed in the Sockets graphic, which makes up most of the rest of the Audio IO display. For Rack or Console ports, each column in the graphic represents an IO card, and the type of IO card is displayed at the bottom of each column. For the Local I/O port, each row represents a type of I/O socket.

Each individual socket displays the following information: the current socket name is across the middle, and the socket number within the card is in the top left-hand corner.

For analogue input sockets, the current gain is at the bottom, and the top right-hand corner displays a red 48 symbol if the socket's phantom power is switched on. For analogue rack output sockets, there is a -10 symbol in the top right-hand corner which is yellow to indicate that the 10dB pad is switched in, and white to indicate that no pad is present.

For digital inputs the status of Sample Rate Conversion On/Off is displayed.

Touching a socket within the graphic assigns that socket and its card to the area below the graphic for configuration, as described below. The number in the top left corner of an output socket will change colour if the socket is being used by the Copy Audio Function.

### 2.12.6 Socket Conforming

In order to use a rack, the on-screen contents of the rack must match the cards physically installed in the connected rack. There are two ways of achieving this:

**Manual Conforming**

Select each card (column) and manually select the appropriate card in the Card/Slot Type drop down menu in the lower section of the window. Once the correct card type is selected, the card type name at the bottom of the selected card will turn green, indicating the card type matches the card installed in the rack. If there is a mismatch, the card type name will be red, and the error should be corrected by selecting the correct card type.

**Automatic Conforming**

The audio I/O can be automatically conformed for the whole console (using the Conform All Ports button in the bottom left of the panel) or the currently selected rack (using the conform rack button below the socket display). Pressing these buttons will correctly select the correct card for each slot. Once complete, all of the card labels beneath each slot should turn green.

The default rack button below the socket's graphic can be used to reset the gains, pads, SRCs and phantom power settings for the selected port.

It is also possible to auto-conform on a card-by-card basis: with a single card selected (by touching any of the sockets on that card), press the Cards & Sockets button towards the base of the screen, followed by the conform card button which appears in the area to its right.

### 2.12.7 Group and Socket Names

Cards and sockets are named automatically, according to the Device Type, Card/Slot Type and their position within the port. To edit these names, press the Cards & Sockets button towards the base of the Audio I/O panel to bring up the Card Setup and Socket Setup displays to its right:

![Card Setup and Socket Setup panels — Group Name and Socket Name editing (manual p.153)](/figures/ref-p153-1.png)

Touch either the Group Name or the Socket Name box (or the keyboard symbols to their right), type the new name into the QWERTY keyboard which appears and press OK. Touching the down arrow in between the Socket Name box and keyboard symbol opens the Channel Name display which enables commonly used words to be inserted quickly without the use of the keyboard.

A range of sockets can be named with the same label and an incrementing number by using the auto-name function below the Socket Name box: to define how many sockets will be auto-named, touch the numeric display, turn the Touch-Turn encoder to the right of the screen until the numeric display below the keyboard symbol displays the correct number. Alternatively, touch the numeric display, type in the number of sockets to auto-name into the keypad that appears, and press OK. Once the number of sockets has been defined, the auto-name button becomes active. Pressing it will cause the name of the assigned socket to be replicated for all the sockets selected for auto-naming. If the assigned socket's name does not end in a number, a '1' will be added to it and incremented for the remaining sockets. If the assigned socket's name already ends in a number, that number will be incremented for the remaining sockets.

### 2.12.8 Socket Options

Depending on the socket type, further Socket Options are displayed below the Socket Name area. E.g. if an input card is selected, an option for phantom would appear.

**Line Check**

When line check mode is active, any input connected to the console, whether it is routed into a channel or not, can have its socket parameters adjusted. Touching any input socket will show the available controls in the socket setup area. Gain is controlled via the touch turn control. When listen is pressed, any audio from the selected socket will be sent to the solo assigned to Line Check — this can be changed in the solo tab in the options panel. There is also a drop-down list of inputs using this socket.

![Line Check socket controls — gain, listen, and the list of inputs using this socket (manual p.154)](/figures/ref-p154-1.png)

### 2.12.9 Copy Audio

The Copy Audio Matrix, located in the Setup Menu, has been designed to serve 2 purposes:

- To provide a flexible system for routing input sources from multiple racks to a recording system.
- To route inputs from one rack to the outputs of another rack without using up console processing resources.

Any input socket connected to a console port can be copied multiple times to any output port socket. One of these "copies" can be nominated as your "Listen Source" for when Listen to Copied Audio is activated.

It is also possible to place a copied input socket in "Listen Safe" so that when Listen to Copy Audio is activated, the original source will be heard rather than the copy source.

Copy Audio settings are not snapshottable and remain constant throughout a session unless they are manually changed by the user.

**Setting up the system**

In Audio IO, conform all your ports, make any required Optocore output allocations and map your system.

Open the Master Screen / Setup / Copy Audio panel and you will see the collapsed matrix with input ports listed down the left side and output ports across the top.

![Copy Audio matrix, expanded — an unavailable output socket, and rack input rows: orange square = copied but not the listen source, red tick = listen safe, red square = the listen source (manual p.155)](/figures/ref-p155-1.png)

The input port list on the left shows all available input ports that have been configured in Audio IO including Local IO, MADI and Optocore connections. Touching on any of these ports will expand the list to show the individual sockets. If a socket has been routed into an input channel, the channel name will be shown in the "Channel" column.

The output port list across the top shows all available output ports that have been configured in Audio IO. When expanded, any output socket that is already in use or is not allocated to your console is shown in blue and its column highlighted. Existing routes from channels/busses cannot be overwritten in Copy Audio.

If a port is expanded, touching anywhere in the sockets list will collapse that port.

To make a copy route, expand an input port and output port and touch/drag on the grid. You will see the selected cells turn red. This first copy, by default, is defined as your Listen Source. Any subsequent copies of the same input socket are shown as orange cells. You may copy an input socket to as many locations as you wish but only one can be defined as your listen source. You can change the defined Listen Source by first pressing the "Set Listen Source" button in the top left corner of the panel and then touching on a cell in the matrix. This cell will turn red, and any previously selected listen source cell will turn orange.

If you have used the "Copy Audio To" function in the Audio IO Panel and then open the relevant ports in the Copy Audio panel, you will see a diagonal line of red cells between the source port and the destination port.

If an output socket is being used as a copy destination, this will be indicated in the Audio IO page by the card socket number showing red (for a Listen Source) or orange (for a copy). You will also see a red/orange square next to any sockets in use in any channel/buss output routing panel. Please note the copy routes CAN be overwritten by output routes.

**Listen Safe**

Listen safe is designed to allow the user to "Safe" a channel from the "Listen to Copied Audio" selection. This means that when listen to copy audio is toggled on, sockets that are safed will be excluded. This can be activated from the Copy Audio Panel, the Channel List (when in Edit mode) or any Input Channel Setup Panel. When active, the Input Channel Name box will turn red. As Listen safe is associated with the input socket, Main and Alt inputs have independent listen safes.

**Copy Audio Presets, Move and Copy Outputs functions**

The move outputs, copy outputs, and presets buttons can be found at the top of the copy audio panel, which can be accessed from Setup > Copy Audio.

![Move outputs, copy outputs, and presets buttons at the top of the Copy Audio panel (manual p.156)](/figures/ref-p156-1.png)

Move outputs allows the output routing to be moved from one place to another. For example, there is a selection of channels sent to the local IO in copy audio, but instead these need to be sent to a rack output.

Press move outputs, select the source output device and then select the destination output device and the copy audio routing will be moved.

Copy outputs allows the copy audio routing from one output device to be copied to another output device.

Press copy outputs, select the source output device and then select the destination device and a copy of the copy audio routing will be created.

Presets can be used to save routing made in Copy Audio, saving time.

![Copy Audio Presets panel — create, update, rename, delete, and clear-all for saved routings (manual p.157)](/figures/ref-p157-1.png)

In the presets panel, presets can be created and updated, their names can be edited and presets that are no longer wanted can be deleted. All presets can also be cleared.

### 2.12.10 Audio Sync

Selecting Audio Sync from the Setup menu opens the Audio Sync display. This is where the clock source is selected:

![Audio Sync panel — clock source selection (manual p.157)](/figures/ref-p157-2.png)

An SD/Quantum console will operate at Sample Rates of either 48000Hz (48kHz) or 96000Hz (96kHz), as configured in the Session Structure panel.

By default, the console will be set to clock internally (master). The console can also be clocked to external sources including: Word Clock, AES/EBU, Video Reference (SD/Q5, SD/Q7), MADI & Optocore.

Note: The Audio sync settings of a console are saved to the session file.

Note: When a valid clock is detected on an external sync input, the corresponding Green OK box will light, even if that input is not selected as the clock source for the console.

In standard operation, all Optocore connected console engines should be set to Audio Sync = Optocore. In this situation the Optocore device with the lowest Optocore ID will automatically become the Master Sync source for the Optocore system. An Optocore system can be synced to an external Word Clock sync source by connecting that Word Clock source to any SD/Quantum engine Word Clock Input and selecting Word Clock as the Sync source in the Setup/Audio Sync panel.

Note: If 2 SD engines have Word Clock connected to them, the system will sync to the Word Clocked engine with the lowest Optocore ID.

An Optocore system can also be synced to a Word Clock source connected to the Word Clock input on any SD Rack. Connecting the Word Clock to the rack automatically sets this as the Master Sync Source. If any SD engine has a Word Clock sync source and is set to Word Clock sync, this will be used as the Master Sync Source instead of the SD rack.

### 2.12.11 Timecode & Transport

![Timecode & Transport panel — Frame Rate, Timecode Source, Output Enable, Machine Control Enable, and Off-line buttons (manual p.159)](/figures/ref-p159-1.png)

When the SD/Quantum console is used in typical live sound applications there will often be no time related control systems (timecode) or motion control (tape transport) connected. Synchronisation and machine control does not need to be considered.

This panel can be accessed by touching the Setup button on the Master screen and then touching the Transport & Timecode button.

**Frame Rate**

This must be set up for the frame rate used by your other equipment. You can select from four different basic frame rates, with a drop-frame option available for 29.97 and 30fps.

**Timecode Source**

You can choose the Console option to make the console generate the master timecode for the setup, or you can choose to make the console "chase" timecode which arrives at one of the external sockets — SMPTE (LTC) (SD/Q7 & Q8 Only), MIDI (MTC), or 9-pin. These external sockets are located on the console rear panel.

*The SMPTE (LTC) socket is SD/Q7 & Q8 only — not on the Q225.*

The 9-pin Eavesdrop option requires a special 9-pin cable. The option is provided for installations where the 9-pin connection runs between two other pieces of equipment (for example, a video machine and DAW), but the console is required to chase this timecode. 9-pin does not normally allow more than a single direct connection between two machines, but using the Eavesdrop cable, you can make the console "listen" to the timecode passing between two other machines, and to sync to and display this timecode on the worksurface.

Note: If you are using 9-Pin Eavesdrop mode, you cannot use any of the options for direct 9-pin connection.

**Timecode Output Enable**

Whether the console is operating as timecode master or deriving its timecode from another device, you can choose to route a timecode signal out from the MIDI (MTC) and/or SMPTE (LTC) sockets. If timecode is being received from another device, it is regenerated before being routed to the output.

**Machine Control Enable**

The console can only send Control signals if you have enabled a Machine Control output. This can be MIDI Machine Control (MMC) and/or 9-pin Disk or Tape. Note that you cannot output 9-pin control if you are using the Eavesdrop option to read timecode. MIDI Machine Control has limited transport features, supporting only the Play, Record, FF, Rewind, Stop and Locate functions. 9-pin control supports Shuttle and Jog functions.

**Off-line Buttons**

The configuration panel allows you to temporarily disable all timecode and transport control to any combination of outputs. The ALL button disables all timecode and machine control output — this is especially useful to prevent external machines trying to chase the console timecode.

### 2.12.12 Macros

Selecting Macros from the Setup menu opens the Macros display. This display is also opened by pressing the assign button in the macros area of the worksurface.

![Macros display — list of created macros with their assigned trigger button, if any (manual p.160)](/figures/ref-p160-1.png)

This is where macro commands can be assigned to the smart keys or Macro buttons in the macros area of the console surface, as well as to the function (F) buttons on the external keyboard and to the console's GPIs. Macros can also be fired directly from this list by touching the macro when none of the right-hand buttons is active.

The macros area has capacity for either 8 or 40 macros, arranged in one bank of eight, four banks of 10 or eight banks of five depending on the console. If the console has bank buttons, pressing any of the bank buttons across the top of the macros area assigns the smart keys below them to that bank. The bank currently assigned to the smart keys is indicated by its button being ringed green.

The Macros display includes a list of all the macro commands which have been created, along with the button to which they have been assigned, if this has been selected. The list is scrollable using the scroll bar to the right of the list. Note that this list therefore includes macros which have been created but have no trigger.

Pressing the Transport Button will automatically assign the console transport controls to the macro buttons, overwriting any existing assignments.

*Not on the Q225.* On SD8, 9, 11, pressing the floating labels button opens a panel on the console's master screen that shows the worksurface macro buttons and their name label if macros have been assigned to them. Touching either the button or the label will fire the macro.

![Floating Labels panel (SD8/SD9/SD11) — worksurface macro buttons with their assigned name labels (manual p.161)](/figures/ref-p161-1.png)

To create a new macro, touch the new button, in the top right-hand corner of the display. To create a macro based on one that already exists, touch the duplicate button below the new button, followed by the macro you wish to duplicate. When either button is touched, a macro is created with the default name macro n, where n is an auto-incrementing number, and the Macro Editor display (described below) is opened. A duplicate macro will contain all of the settings of its parent, apart from the name.

To edit a macro, touch the editor button below the duplicate button, followed by the macro you wish to edit. The Macro Editor display (described below) will then open.

Macros can be assigned from the main Macros display without opening the Macro Editor by touching the assign button below the editor button, touching the macro you wish to assign, and then pressing the button to which you wish to assign the macro.

Macros can be deleted by touching delete files. To delete all the macros in the list, touch select all, followed by confirm. To delete one macro or a selection of macros, touch the macros you wish to delete followed by confirm. To delete a consecutive range of macros, touch select range, touch the first and last macros included in the range to be deleted, and touch confirm.

### 2.12.13 The Macro Editor

The Macro Editor is where macros are defined, including the commands included in them and the control used to trigger them. Virtually any command within the console can be assigned to a macro, ranging from opening master panels to adjusting in-channel signal processing.

Note: fx parameters are only available once fx units are in use in the session.

![Macro Editor — command types, included-commands list, and Smart Keys trigger tab (manual p.162)](/figures/ref-p162-1.png)

The name of the macro being edited is shown at the top of the display. To switch to a different macro in the list, touch the new macro in the Macro display list (you may need to move the displays around the panel to access the list). To rename the macro, touch the macro name text box, type the new name using the on-screen or external keyboard, and touch OK. This name will be used in the Macros display and also in the LCD display within a smart key assigned to that macro.

Note: A line break can be inserted into the smart key macro name by typing a comma within the macro name text.

The list beneath the macro name text box lists the commands currently included in the macro. When there are multiple commands in the included commands list, they are triggered in the order in which they are listed. New commands are added to the selected row in the list, overwriting any command previously in that row. To insert a row for a new command in between two adjacent commands, touch the row above which you want to insert the command, then touch the insert button to the right of the included commands list.

There are two ways of adding a command to the included commands list:

1. Touch the row in the list in which you want the command to appear, then touch the capture button, located in the top right-hand corner of the display. The button turns light blue to indicate that it is active. Any commands now actioned on the console will then be added to the included commands list. Once all the desired commands have been actioned, deselect the capture button.
2. Touch the row in the list in which you want the command to appear, then touch one of the command types in the scrollable command types list to the left of the display. This brings up a list of the commands within that command type in the scrollable commands list in the lower half of the display. Touch the desired command to bring it into the included commands list.

For commands associated with worksurface controls (all command types above System in the command types list), the included commands list displays the command type (in the channel type column), the scope of channels included in the command where appropriate (in the from and to columns), the command's name (controller) and any value associated with the command. For command types associated with the master panel (from System down), the included commands list displays the command, along with any filename or value associated with it. The list can be scrolled if necessary, using the scroll bar to its right.

The values in the from, to and value columns can be adjusted by using the Touch-Turn encoder and value + and value- buttons to the right of the included commands list. Touch the box to be adjusted to assign it to the encoder and value buttons. The present value is shown in the display in between the value buttons. If the value column displays something other than numeric values, the options are cycled using the Touch-Turn encoder and value + and value - buttons (cycling, for example, between on, off and toggle). Values can also be typed in by touching the value box, typing the new value using the external or on-screen keyboard, and touching OK.

To remove a command from the list, touch the command to be removed and touch the remove button to the right of the included commands list.

The bottom-right of the Macro Editor is used to define what triggers the macro. The action buttons below the smart keys / macro buttons are used to define whether pressing the button triggers a macro on or off command. Selecting a new trigger for a macro automatically deselects any old trigger that might have been assigned.

On SD7, SD5, SD10 and SD12 and Quantum consoles, Smart keys are selected by touching one of the bank buttons (the number of bank buttons will depend on the console) below the assigned to legend (causing the button's ring to light green, indicating that it is selected) followed by one of its smart keys. The smart key will then display the first command from the included commands list. The colour of the smart key can be chosen using the arrow buttons in the colour area below the smart keys. The selected colour is displayed between the arrow keys.

*Not on the Q225.* On SD8, SD9 and SD11, Macros are assigned in a similar way but directly to one of the 8 Macro buttons.

Whenever a macro button is pressed, it performs an 'On' action. This is the first press of the macro button. The next press of the same macro performs an Off action.

These On and Off actions can be the inverse of each other, so instead of having alternative presses of the macro button just toggle the state of a controller, the macro can be programmed so that the first press is always a mute on command and the 2nd press of the macro button is always a mute off command.

This has the advantage of being able to provide an indicator on the Macro button of the state of the controller. On and Off states can have different colours and different text.

Macros can be tested by touching the fire macro button, located in the top left-hand corner of the display. Once the macro has been fully configured, close the Macro Editor display.

### 2.12.14 Advanced Macro Triggers (V19xx+)

The Macro Editor has been expanded to include new options for triggering Macros. Existing options have been retained but laid out slightly differently on screen in tabbed sections. Macros can now also be triggered as part of Snapshot recall.

Note: only one trigger type can be selected for each Macro.

The selected, displayed tab will be underlined in orange and the active trigger will be displayed with a green circle.

**Smart Keys**

The smart keys tab allows assignment of the Macro trigger to the console's worksurface Macro buttons. Where relevant, select a Macro bank number and then the required button in that bank. The Macro can be assigned to the ON or OFF action of the button and a background colour selected.

![Macro Editor — Smart Keys trigger tab active, with bank, action, and colour controls (manual p.162)](/figures/ref-p162-1.png)

**External**

The external tab allows assignment of the Macro trigger to a GPI, an incoming OSC command or a MIDI Program change message. Other relevant options are displayed when the external device type is selected.

![Macro Editor — External trigger tab: GPI, OSC, or MIDI PC, with ON/OFF action (manual p.164)](/figures/ref-p164-1.png)

**Snapshots**

A console snapshot can also be defined as a Macro trigger by pressing the edit button in the snapshots tab, which displays a list of available snapshots. Single or multiple snapshots can be added to the list of triggers for any particular Macro.

Note: any snapshot can only trigger a single Macro so, if a snapshot is required to trigger more Macro functions than those included in the existing Macros, create a new Macro which includes all of the required commands for that specific purpose.

![Macro Editor — Snapshots trigger tab: select which snapshots fire this macro (manual p.165)](/figures/ref-p165-1.png)

**Other**

The other tab allows assignment of the Macro trigger to keyboard F keys, the console Audio Mastership switch A or B and the worksurface prev and next snapshot buttons.

![Macro Editor — Other trigger tab: keyboard F keys, Audio Master A/B, snapshot prev/next (manual p.165)](/figures/ref-p165-2.png)

**Advanced**

The advanced tab allows conditional triggers for Macros whereby the status of certain channel controls and meters can be used to trigger a Macro.

Single or multiple triggers can be specified for one or many channels. Required channels can be chosen by touching the ADD button and selecting from the channel list. Each channel touched will be added to the list. Channels can be removed from the list by selecting them from the list and touching REMOVE.

If multiple channels are selected, the Macro can be triggered when either ANY or ALL conditions have been met.

![Macro Editor — Advanced trigger tab: per-channel fader/mute/solo/meter trigger and state list (manual p.166)](/figures/ref-p166-1.png)

Choose the required trigger and state for each of the entries in the list. Options for potential triggers are fader level, mute state, solo state and meter level. For mute and solo, either on or off states can be selected. For faders, a value can be set and the trigger assigned to a level greater than or less than that value. When the relevant fader passes through that value, the condition will be met.

For meters, first select the required meter position from pre-trim, post-trim, pre-fader or post-fader and then enter a value and a state in a similar way to faders. To change the meter position, touch the current selection to display the meter position choices again. Note: for meters, a value of sp represents "signal present".

For any given channel, each trigger and state combination can only be used once. For example, for Channel 1, a fader greater than state can only be used once, but fader greater than and fader less than is a valid combination. If the same trigger/state combination is entered twice for the same channel, the following warning will be displayed.

![Warning dialog — "trigger already exists" for the selected macro (manual p.166)](/figures/ref-p166-2.png)

**OSC Macros**

There is also a Macro type called MacroOSC which allows a Macro to transmit an OSC message via the console's ethernet port.

In the Master Screen > Setup > External Control panel, a new Device Type is used to define the details of the external device which will receive the OSC commands.

Touch the add device button and select Macro OSC from the list of device types, enter an IP address for the receiving device and a Send port number.

Multiple Macro OSC devices can be defined and each should have a unique DevID automatically assigned by the console.

![External Control panel — adding a Macro OSC device (manual p.167)](/figures/ref-p167-1.png)

In the Macro Editor, there is a command type called MacroOSC which offers options of Integer, Float, String and Address Only (no data value required) OSC commands.

Define the required OSC command and data value and then, using the value +/- buttons, specify a destination Device ID in the right-hand column.

![Macro Editor — MacroOSC command: Select Command (Integer/Float/String/Address Only), OSC command text, data value, and destination Device ID (manual p.168)](/figures/ref-p168-1.png)

**Macro list search function**

The Macro command list for each command type can be searched by entering text in the commands search box at the top of the list. A search can be performed for whole or parts of words.

![Macro Editor — command search box above the commands list (manual p.168)](/figures/ref-p168-2.png)

### 2.12.15 Talkback

The Talkback display, where the talkback busses can be configured, is opened by selecting Talkback from the Setup menu.

In the right-hand side of the Talkback display, there is a mic input gain pot which is always assigned to the gain encoder in the worksurface talkback area. The pot's gain value is indicated in the box above the pot. The talkback signal level is shown in the meter to its right.

![Talkback panel — talk buttons a/b/c, mic gain pot and meter (manual p.169)](/figures/ref-p169-2.png)

Touching the white box below the gain pot opens the Talkback Input display which consists of an input route button. The current route is displayed below the button. Pressing the button opens the TB Input Route display, which functions in the same way as all other input routing panels.

![Talkback Setup panel — main/alt input routing, +48V, delay, and digitube warmth (manual p.169)](/figures/ref-p169-4.png)

To the left of the input section of the display, there are talk buttons with text boxes beneath them. Touching each button enables and disables the corresponding talkback button on the worksurface. The button rings red to indicate that the buss is active. Touching the text box beneath the button opens the TB Outputs display for that talk bus. This consists of a naming area and an outputs button. The first output currently selected is displayed below the button.

![TB Outputs panel for a talk bus — output routing list (manual p.169)](/figures/ref-p169-3.png)

Pressing the button opens the TB Output Routes display which functions in the normal way. The first selected route appears in the text box below the talk button.

The three blue coloured text boxes above the buttons provide access to a panel allowing the selection of aux busses. Once selected, the Talkback button will automatically activate the talk To Aux functions on those busses. This enables you to talk to multiple Auxes of your choice at the press of a single button.

**Talk to Auxes**

To talk to individual or multiple Aux outputs there is an assignable row of controls on Aux channels, controllable independently or from the Talkback panel which has a Talk to Aux Setup list for each Talk button.

![Talk to Aux Setup panel — mono/stereo aux selection for a talk button (manual p.169)](/figures/ref-p169-1.png)

This is implemented as a Talkback Input channel which uses a single engine processing channel to provide the aux sends. This channel appears, in a default session, on its own in the last bank on the left of the console.

On the Aux Output channels, hold one of the Assign buttons next to the row of assignable controls and then touch the talk area of the screen. This will assign the selected rotary control and switch to the talk level and talk on/off. These are used to switch Talk to Aux On/Off, control the level of talkback signal and set the level of dim when the talk is active. A dim function is available for reducing the level of aux programme while the talk function is active. This is set using the 2nd Function of the assigned controls.

![Aux output channels 1–4 with Talk, level, and dim controls (manual p.170)](/figures/ref-p170-1.png)

The worksurface talk buttons can also be programmed to activate the Talk function on single or multiple user defined channels. Open the Setup/Talkback panel and touch the label above the talk button, then select any combination of Mono and Stereo Auxes to activate with that button.

### 2.12.16 Text Chat

Text messages can be sent from console to console on any MADI Port that is defined as "Console". This definition uses the last 8 audio inputs and outputs on the port to send text or video communications. The default setup of the SD/Q7 defines MADI Port 4 as "Console". With MADI connections from one SD/Q7's Port 4 In/Out to another SD/Q7's Port 4 In/Out, open the Setup>Text Chat panel, press the 4:Con button to activate the link on that port and then type a message. When you press the keyboard Enter key, the message will be transmitted and will appear in the other console's Text Chat panel. This process is bidirectional, meaning the other console can send messages back in a similar way. This communication can also be achieved across an Optocore connection.

![Chat panel — message box, recipient port, and type-here field (manual p.170)](/figures/ref-p170-2.png)

### 2.12.17 Video Link (SD7 & Quantum 7 Only)

*Not on the Q225.*

The Setup>Video Link panel allows the routing of one of several different video signals to the console video screen. The worksurface buttons to select between these 3 sources can be found at the top of the console's centre section and are duplicated at the top of the on-screen panel. There is also a Self button to send the console's own camera signal to the screen.

![Video Link panel — video monitor source selection, local video inputs, local output feed, and NTSC/PAL format (manual p.171)](/figures/ref-p171-1.png)

To define the source associated with each button, touch the white label box below the on-screen label and a drop-down menu will appear.

Potential sources include the console's two external video inputs (Ext 1 & Ext 2) located on the back panel and any Optocore equipped SD7 engines that are connected. Optocore engines are identified by their Optocore Loop number (normally 1) and their Optocore ID, which can be seen and set at the top of the console's Network panel.

The lower part of the Video Link panel determines which video source is fed from the console to the video network. Only one source can be sent at one time and this is done by pressing the Feed button beneath the required source.

Select the appropriate video format using the NTSC and PAL buttons, ensuring that all connected consoles are using the same format.

The console's camera feed can also be sent as a Mirror image using the on-screen buttons.
