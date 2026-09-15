# 2.4 Snapshots Menu

*Chapter 2: The Master Screen — manual pages 92–111*

Any number of Snapshots of the entire current console settings can be stored and recalled using the Snapshots panel. (This is only limited by system memory)

These Snapshots can be independent or grouped with other snapshots.

The recall scope of the snapshot (how many controls it will affect when fired) can be set by controller or by channel.

To display the Snapshots panel, touch the Snapshots button at the top of the Master Screen.

Worksurface controls are detailed in Getting Started.

![Snapshots Menu (manual p.92)](/figures/ref-p092-2.png)

Opens Global scope panel

Inserts new snapshot after selected (Green) snapshot

Duplicates selected (Green)

Opens snapshot notes panel

Adds current snapshot to group

Updates current (Highlighted)snapshot

Lock prevents snasphot update

Updates all members of Snapshot Group

Snapshot under control of sequence

Updates selected (Green)snapshot

Edit multiple snapshots after selection

Allows changing of order of snapshot list

Removes snapshot from prev/next control

Shows individual snapshot option buttons

Press and select snapshot to rename

Press to open Renumber panel

Opens individual snapshot recall scope

Opens group/auto-update scope

Press and select snapshot(s) to delete

Opens snapshot crossfades panel

Fires previous snapshot in list

Opens snapshot recall times panel

Fires selected (Green) snapshot

Opens snapshot MIDI list

Fires next snapshot in list

Opens snapshot MIDI program change

Opens snapshot GPO panel

Undo firing of last snapshot

Opens snapshot transport control panel

Activate snapshot fire by touching list

Activate snapshot Auto Update

Opens control by MIDI panel

Group Update Mode

Note: The current snapshot appears in the panel as the highlighted entry in the list. The snapshot name displayed in green indicates that it is the selected snapshot on the worksurface and its name is indicated in the display. The Fire button recalls this selected snapshot and highlights it in the screen list as the current snapshot.

Note: An “update Waves only” button appears below the Scope buttons when Waves is active.

If the current snapshot shows an asterisk next to the number (e.g. 001*) this indicates that a controller has changed since the snapshot was fired. If a Snapshot name appears in black in the list, it is a standard Snapshot and if it appears in red or blue then it is a member of a group of snapshots

### 2.4.1 Storing a Snapshot

When a snapshot is stored all the console settings are saved but when the snapshot is recalled its effect can be limited to certain channels and controllers using the Global and Recall Scopes. To store a snapshot of the current state of all the console controls, touch the Snapshot panel or worksurface Insert New button and a new snapshot will be inserted below the currently selected (green) snapshot. Alternatively, if the Touch to Fire function is active, touch an unused button in the list and a new snapshot will be added to the end of the list, then type a name for the snapshot. Another method of creating a Snapshot is to press the Duplicate Selected button and this will create a copy of the selected (green) Snapshot below it.

Note: If Duplicate Selected is used, the Snapshot that is stored may not reflect the current state of the console's controls - it will simply create a copy of the Snapshot that was selected when the button was pressed.

### 2.4.2 Recalling a Snapshot

There are several ways to recall a snapshot:

1. Activate the Touch to Fire function using the button on the Snapshot panel and then touch the

snapshot button you require.

2. The buttons on the Worksurface provide Scroll Up/Down buttons to change the selected snapshot

named in the worksurface display and listed on screen in green.

The Fire button then recalls the assigned snapshot.

3. The worksurface Previous and Next buttons can be used to step up and down the list firing snapshots

in consecutive order.

4. Snapshot firing can also be controlled by specific events on MIDI channel 16 (See Snapshots and MIDI).

5. Assign a Macro button to fire the Snapshot.

### 2.4.3 Replacing a Snapshot

To update or change a snapshot, set the console controls as required and then touch the one of the Update buttons (Current, Selected or Group)

Note: The Current snapshot is not necessarily the one whose name appears in the display on the worksurface, this is the Selected snapshot. For a snapshot to be Current it must have been the last one that was fired and be highlighted in the on-screen panel's list.

2.4 Snapshots Menu

### 2.4.4 Editing Multiple Snapshots

Individual controller changes can be written to several snapshots simultaneously using the Edit Range button. This does not replace all of the data associated with the snapshot, just the elements that are changed at the time. When the Edit Range button is pressed, a panel pops up allowing you to Select Range, Select All, or select individual Snapshots. You can now select the relevant snapshot(s) from the list. If you press the Select Range button, touching the first and last snapshots in a range will automatically select all the snapshots in that range. Once snapshots have been selected for editing, press the confirm button, or press cancel to cancel the Edit Range button.

![Snapshots Menu (manual p.94)](/figures/ref-p094-1.png)

With the Edit Range button active, pressing the Snapshot buttons does not fire the snapshots; it only selects them for editing. The selection may be changed by pressing and releasing snapshot buttons at any time during the operation of the Edit command, so a variety of controllers or routes may be changed in a variety of snapshots before completing the operation by pressing the Confirm button. The Snapshots window may even

2.4 Snapshots Menu

be closed to gain access to other editable functions - In this case, a warning message will appear to advise the user that they are still in snapshot edit mode. While any Snapshot is selected, changes to any snapshottable controller, routing changes, and any changes to the Snapshot Scope controls can be written to every selected Snapshot, overwriting the previous settings. Pressing the Confirm button keeps the changes.

For example, if Snapshots 1 and 2 are selected and the input gain for channel 1 is changed, subsequent recall of Snapshots 1 or 2 will set channel 1’s input gain to the new value.

Only channels which are altered while the Edit command is active will be affected and only in snapshots that are selected at the time.

Note: Snapshot Scopes and Crossfade Times can also be edited for multiple Snapshots using the Edit Range function

### 2.4.5 Moving a Snapshot

If you wish the Snapshot list to appear in a specific order, you may change the order of the list by moving the entries. Touch the Move button and then touch the Snapshot that you wish to move. You then touch the point in the list where the snapshot should be moved to.

### 2.4.6 Renaming a Snapshot

To rename a snapshot, touch the Rename button, then the name that you wish to change and enter a new name using the keyboard.

### 2.4.7 Renumbering Snapshots

As snapshots can be inserted at any point in the list you may find that you wish to renumber part or all of the list.

Press the Renumber button at the bottom of the snapshots panel and a new panel will open. Enter the range that you wish to renumber using the touch turn control or by touching the entry and typing and then enter the steps to renumber to (1.00 is the default value). Then press the OK button and the list will be adjusted accordingly.

### 2.4.8 Deleting a Snapshot

To delete snapshots, touch the Delete button and then Select Range or Select All. If you have pressed Select Range, touch the Snapshots in the list that you wish to delete and then press Confirm. If you have pressed Select All, the complete list of Snapshots will be highlighted and pressing Confirm will delete all Snapshots.

Note: To cancel a Delete operation before it has been confirmed, press the Delete button again.

### 2.4.9 Snapshot Undo

When a snapshot is fired, a separate hidden snapshot of the complete console is stored before the fired snapshot has its effect. If the Undo button is pressed, the hidden snapshot is fired using the same scope as the previously fired snapshot to undo its effect.

2.4 Snapshots Menu

### 2.4.10 Snapshot Groups

A standard Snapshot (black entry in the list) is an independent snapshot of the current state of all the console controls. A Snapshot can also be a member of a Group (red or blue entry in the list). Making Snapshots members of a Group allows all members of that Group to be updated together according to the Group Update mode that is selected. To make a Snapshot a member of a group, first select the groups button on the left of the snapshots panel. Create a group by pushing the new group button and then select the change members button. While the change members button is toggled, snapshots can be added or removed from the group by selecting them from the main snapshots panel. Once of the desired snapshots have been added or removed from the group, untoggle the change members button.

If a Snapshot is a member of a Group, the colour of its entry in the list is determined by the current setting of the Relative Groups button in the bottom right of the Snapshots panel. This determines how the Group of Snapshots will be updated when Update Group is pressed.

Red entry in the list = Relative Update mode selected

Blue entry in the list = Non-Relative Update mode selected.

**Relative Group Update Mode (Red entries in the list)**

If Update Group is pressed when the relative groups button is active, all dB controls such as faders and aux sends will be updated relatively. This means that if a fader is moved by +10dB in one snapshot, the same fader will be moved by +10dB in all Snapshots that are members of the same group, irrespective of the original level of that fader. So +10dB will be applied to the stored level of that fader in all of the Snapshots in the group.

Non dB controls such as Dynamics times, EQ Frequency & Q and Pans will only be changed in members of the group that had the same value for that control before it was moved. So, if one channel pan is in the same position in all the members of a group of Snapshots and you change one of them and press Update Group in Relative mode then the same channel pan will change in the same way in all the other snapshots that are members of that group. If, however, any one of the Snapshots in the group has that channel pan in a different position to the current Snapshot then this one will not be changed when you press Update Group.

**Non Relative Group Update Mode (Blue entries in the list)**

If Update Group is pressed when the relative groups button is not active, then all controls behave in exactly the same way. Changes are only applied to the other Snapshots in the group if the controls that are being changed had the same value as the current Snapshot before the change was made. This is exactly the same behaviour as non-dB controllers in Relative mode but in this case all controls are included.

2.4 Snapshots Menu

**Group & Auto Update Scope**

The behaviour of the Group Update function explained above is also dependent on the Global Auto Scope and the Group and Auto Update Scope settings that can be set per Snapshot for different types of controls.

Pressing the Global Scope button at the top left of the Snapshot panel opens the following display:

![Snapshots Menu (manual p.97)](/figures/ref-p097-1.png)

Horizontal rows show the different sections of the console and the vertical rows show the Recall and Auto Update status for each of the different types of control. A red X indicates not included and a green tick indicates included. These settings can be changed individually by touching the X or tick symbols or by touching the name of a row or column to change all of its contents.

Recall Scope is dealt with in the next section but the Auto scope columns determine which controls will be included in the automatic group update. Any elements that have a red X will not be updated in any snapshots when Update Group is pressed.

In the picture above the Input Devices (rack and local input sockets) are not included in the Auto scope so none of their gains or phantom power can be updated using the Update Group function. All other elements are ticked and therefore can be included in the Update Group function.

Note: If elements are included in the Global Auto Scope they can still be prevented from Group Updating by the individual Snapshot's Group and Auto Update Scope.

Selecting a Snapshot in the list and pressing the Group & Auto Update Scope button opens the following panel:

2.4 Snapshots Menu

![Snapshots Menu (manual p.98)](/figures/ref-p098-1.png)

The Global & auto update scope is similar to the Global Scope panel but represents the Group and Auto Update Scope for one individual snapshot which is indicated by its name and number at the top of the panel.

The down arrows on the left of the panel can be clicked to expand the list to show and edit the status of individual sockets and channels for each Snapshot.

Changes in Control Group membership and ganging can also be included or excluded using the tick boxes at the base of the panel.

In the picture above the Audio Enhancer input trim has been excluded from the Group Update in this particular Snapshot.

Note: When using Snapshot Groups, it is advisable to set the Global Auto Update scope before attempting to change the update settings for each individual Snapshot. Use of the Global Scope alone probably offers quite sufficient control for most common applications.

2.4 Snapshots Menu

### 2.4.11 Global Recall Scope

When a snapshot is stored all the console settings are saved but when the snapshot is recalled its effect can be limited to certain channels and controllers.

Note: All elements of console channels and several other features such as Graphic EQ and Effects have their own SAFE settings. If any of these SAFE settings are active, then the relevant controls cannot be affected by any Snapshots. This is in addition to the Global Scope settings described here.

Pressing the Global Scope button expands the panel to display and edit the scope for all snapshots.

![Snapshots Menu (manual p.99)](/figures/ref-p099-1.png)

Horizontal rows show the different sections of the console and the vertical rows show the Recall and Auto Update status for each of the different types of control. A red X indicates not included and a green tick indicates included. These settings can be changed individually by touching the X or tick symbols or by touching the name of a row or column to change all of its contents.

The Recall scope columns determine which controls will be included in the Snapshot recall. Any elements that have a red X will not be recalled in any snapshots.

In the picture above the Input Devices (rack and local input sockets) are not included in the Recall scope so none of their gains or phantom power can be changed by firing Snapshots. All other elements are ticked and therefore can potentially be changed when a Snapshot is fired.

Note: If elements are included in the Global Recall Scope, they can still be prevented from recall by the individual Snapshot's Recall Scope.

2.4 Snapshots Menu

### 2.4.12 Individual Snapshot Recall Scope

Selecting a Snapshot in the list and pressing the Recall Scope button opens the following panel:

![Snapshots Menu (manual p.100)](/figures/ref-p100-1.png)

The controls that are included in each of the Recall Scope columns can be seen at the bottom of the panel when any of the entries are changed and are as follows: Controllers

Input/Trim (Local I/O and Racks) - analogue gains, switches and phantom power

Input/Trim (Input Channels) - input routes, digital trim, phase, channel name, Mustard input position

Input/Trim (Aux Outputs/Group Outputs/Matrix Outputs) - digital trim, phase, delays, buss name and tubes

Input/Trim (Matrix Inputs) - input routes, matrix input name and tubes.

**Delay (All channel types) - Channel delay**

**Filters (All channel types) -  HPF and LPF**

EQ (All channel types) - all controllers except channel HPF and LPF.

Dynamics (All channel types) - all controllers except stereo link.

Inserts (All channel types) - Insert Send & Return routes and ON/OFF switch

Sends (Input Channels) - Aux send levels, ON/OFF & PRE/POST switches and Aux pans

Sends (Matrix Inputs) - Matrix send levels and switches Fader (All channel types) - channel fader. Mute (All

**channel types) - channel mute**

**Panner (Input Channels) - channel pan**

To Groups (Input Channels) - Input Channel to Buss routing switches

2.4 Snapshots Menu

To Groups (Group Channels) - Group to Group routing switches

Outputs (Input Channels) - Direct output routes, direct gains and ON/OFF switches Outputs (Aux Outputs/Group Outputs/Matrix Outputs) - Output routes and gains

Outputs (Local I/O and Racks) - analogue output 10dB pads and AES SRC switches. Misc

External- All External Controllers and Generic OSC controls can be saved and recalled.

Control Group Members - Control Group label and a complete list of each group’s members.

Gangs - Channel gang members.

Banks - Current assignment for all controllers and selected bank on the worksurface.

Copy Recall Scope From - Entire recall scope can be copied from another snapshot.

Note: that if Waves is active, a Waves scope button is also shown.

The down arrows on the left of the panel can be clicked to expand the list to show and edit the status of individual sockets and channels for each Snapshot.

### 2.4.13 Snapshot Recall Times

In addition to being fired manually, snapshots can be timed to fire automatically in sequence. This is done in the Snapshot Recall Times panel, opened by pressing the scope>recall times button on the left-hand side of the Snapshots panel.

Each snapshot can be given a recall at time (the timecode value at which the snapshot will fire) and a duration (the amount of time before moving onto the following snapshot). With the capture recall times button toggled, the recall at time of the next snapshot created will be set to the current timecode. Both the duration and recall times must be activated by ensuring that their Active column is ticked. The smallest time units can be switched between 1/100ths of a second and frames using the duration display buttons in the bottom right- hand corner of the panel.

![Snapshots Menu (manual p.101)](/figures/ref-p101-1.png)

2.4 Snapshots Menu

The first snapshot can be fired manually in the main Snapshot window, if no specific recall at time is set. When this snapshot is fired, the next snapshot in the list will automatically be fired after the set time has elapsed and a progress bar in the snapshot's entry in the Snapshots panel will show the time remaining until the snapshot is fired. Pressing the duration active button while the progress bar is moving will halt the process. The recall at time overrides any active duration time.

**Cancelling Crossfades**

Once a snapshot containing a crossfade has be fired, a cancel crossfade button will appear on the snapshots panel. Pressing the cancel crossfade button will skip the crossfade and the snapshot will be recalled instantly.

### 2.4.14 Snapshot Crossfades

A crossfade time which is measured in seconds and frames can be applied to different controls in a Snapshot by adjusting the Crossfade Time in the Cross Fades panel. This crossfade occurs as you go into the Snapshot.

Select an individual time by touching it or select a column or row by touching its heading. Then enter a time in the Secs/Frames boxes at the bottom of the panel. Either touch and type or use the Touch Turn rotary to enter a figure.

Different Crossfade times can be applied to input trims, filters, EQs, dynamics, sends, faders and pans.

The down arrows on the left of the panel can be clicked to expand the list to show and edit the status of individual channels for each Snapshot so different Crossfade times can be applied to different channels as well.

A value of zero switches it off.

The faders & panners wait time field located in the crossfades times panel is used to insert a wait time before the crossfade begins.

![Snapshots Menu (manual p.102)](/figures/ref-p102-1.png)

2.4 Snapshots Menu

### 2.4.15 Snapshots and MIDI

There are two separate areas of MIDI control:

1. A snapshot can have a MIDI Message attached to it and will output that MIDI when fired. The MIDI

message must be created in either the Scope>MIDI Program panel or the Scope>MIDI List panel.

2. The firing of snapshots can be controlled by incoming MIDI messages on channel 16 and can cause

these same messages to be output in addition to any MIDI List data contained in the snapshot.

The specific MIDI messages that are being responded to can be edited in the Snapshot Control By MIDI panel, accessed via the Control By MIDI button.

To change the default message for any particular snapshot, select the snapshot and press the Change button to select a specific available controller number. The Clear button will remove the existing message completely.

The MIDI Received Fires Snapshots button allows the Snapshot system to respond by default to the following incoming MIDI messages:

General Purpose Controller 16; Values 1 to 127 will fire snapshots 1 to 127 General Purpose Controller 17; Values 0 to 127 will fire snapshots 128 to 255

General Purpose Controller 18; Values 0 to 127 will fire snapshots 256 to 383.

General Purpose Controller 19; Values 0 to 125 will fire snapshots 384 to 509.

General Purpose Controller 19; Value 126 will fire the previous snapshot in list.

General Purpose Controller 19; Value 127 will fire the next snapshot in list.

When active, the Fire Snapshot Sends MIDI button causes the above messages 1 to 509 (or customised versions - see below) to be sent whenever a snapshot button is pressed.  Previous and Next buttons do not output MIDI messages of their own.

![Snapshots Menu (manual p.103)](/figures/ref-p103-1.png)

2.4 Snapshots Menu

### 2.4.16 MIDI Devices

If you intend to send MIDI to external devices, it is advisable to first define your receiving devices - this will make the programming of MIDI messages in Snapshots easier to achieve.

Press either the Scope>MIDI Program or the Scope>MIDI List button and then press the Devices button - the following panel will open:

![Snapshots Menu (manual p.104)](/figures/ref-p104-1.png)

The SD and Quantum Console's built in MIDI port is referred to as Port A in the Port column. Set the receiving MIDI channel and name for each of your receiving devices and set 1 or 0 in the PC column according to whether the device uses 0-127 (0) or 1-128 (1) for its data values. If you don't know this piece of information, then leave the setting as 1.

The column marked Chng determines whether Program Changes are only sent when they are different to the last sent message (Y) or whether they are always sent irrespective of the last message sent. This would be useful if there was no need to change the program on the receiving device and if you did this it might interrupt the signal passing through the receiving device as its program changes.

The Clear PC button at the bottom of the panel ensures that the next message will be sent.

This has defined your devices for later use and the panel can now be closed.

2.4 Snapshots Menu

### 2.4.17 MIDI Program and MIDI List

The Snapshot MIDI Program Changes panel, accessed via the midi program button has a column for each of the 16 MIDI channels on Port A and a row for each existing Snapshot. Touch and type, use the value up/down buttons or enter a value using the Touch Turn rotary control for each program change that you wish to send with each snapshot and ensure that the act (active) box is ticked for each relevant Snapshot. With the ripple down button active, entries will be copied to all consecutive following Snapshots that have the same value as the one which was changed or have no value. Once entered, this MIDI information will be sent when the Snapshot is fired.

![Snapshots Menu (manual p.105)](/figures/ref-p105-1.png)

If MIDI program change messages have been entered in this way, they will also appear in the Scope>MIDI List panel which allows entry and editing of other types of MIDI message. There are columns for the midi device name (mentioned in the last section), the MIDI Port, MIDI Channel, type of command and two data values.

Note: If you have already defined MIDI Devices, selecting one of these in the MIDI Device column will automatically enter the Port and MIDI channel that you have previously entered for that device.

![Snapshots Menu (manual p.105)](/figures/ref-p105-2.png)

2.4 Snapshots Menu

If you want to send multiple MIDI messages with a single Snapshot, use the Insert button to add extra lines for message entry. You can then configure the message by editing each column using the value controls to the right of the list. Below the value controls is a key for the command column. To test the MIDI message without firing the Snapshot, press the Send button - the display at the bottom right of the panel shows the presence of incoming and outgoing MIDI messages. The move up/down buttons allow MIDI messages to be moved up/down within a snapshot. The edit hex button option can be used to quickly edit the entire messages parameters at once. MIDI messages can also be automatically entered into the list by generating the required message from the external MIDI device, sending this to the console's MIDI In and pressing the Capture button.

### 2.4.18 Snapshot GPO Relays

The Snapshot GPO relays panel allows the state of each GPO to be set when a snapshot is fired. The Global Recall scope for each GPO can be set by touching the appropriate box at the top of the column.

![Snapshots Menu (manual p.106)](/figures/ref-p106-1.png)

### 2.4.19 Surface Offline & Snapshot Editing (Not SD11)

In the Snapshot section of the console worksurface there are 2 buttons labelled Surface Offline and RTN To Audio. When pressed and held, the Surface Offline button stops the communication between the worksurface controls and the audio engine - this means that anything that is done on the surface of the console will have no effect on the audio passing through the console.

Pressing the RTN To Audio button will reconnect the surface controls to the audio engine ignoring any worksurface changes that have been made since the surface was put Offline and returning the console to its state before the Surface was put Offline.

Important Note: if the Surface Offline button is pressed, worksurface changes are made and the Surface Offline button is pressed a second time, the changes that have been made on the worksurface will immediately applied to the current audio - be careful with this function...!

The main purpose of the Surface Offline and RTN To Audio buttons is to enable Snapshots to be edited with the worksurface offline so that any Snapshot can be previewed, adjusted and updated without affecting the current audio.

While Surface Offline is active, any of the Snapshot functions already described can be used.

2.4 Snapshots Menu

For example, if you are currently in Snapshot number one and wish to check or edit Snapshot number two you should:

Press and hold the Surface Offline button and the audio will continue normally.

Scroll down and fire Snapshot two to see its settings on the worksurface.

Edit the settings for Snapshot two and Update either Current or Selected according to requirements.

Press the RTN to Audio button to automatically put the surface back online and back in Snapshot one.

Alternatively, pressing the Surface Offline button again applies the current state of the console to the audio, causing any changes made with the surface offline to be applied to the audio.

### 2.4.20 Auto Update

The Auto Update button in the Snapshots panel activates automatic updating of the current Snapshot whenever a control is adjusted. The current Snapshot will be updated without using the Update Current, Selected or Group functions. While auto update is enabled, the background of the snapshots panel will be highlighted. The elements of the Snapshot that are automatically updated is dictated by the Group and Auto Update Scope settings that are described in the Group Snapshots section of this chapter.

Note: In view of the potential for changing Snapshots without active manual intervention, it is probably advisable to leave this function OFF unless you are absolutely certain that you require it.

2.4 Snapshots Menu

### 2.4.21 Snapshots & MTC ................................................................

Snapshots can also be programmed to send MMC messages, allowing control of external playback devices. Within the snapshot scope section, press the transport control button. This opens the Snapshot Transport Control panel. The panel lists all current session snapshots and allows entry, per snapshot, of the following MMC commands.

PLAY: Basic Play command. External device will play from current location

play from: External device will play from specified time value

play to: External device will stop when the specified time is reached.

locate to: External device will Locate to specified time.

STOP: Basic Stop command. External device will stop.

Commands can be sent via MIDI, selected at the bottom of this panel.

Note: Correct MMC operation relies on a correctly configured MIDI system, with MTC from the external device connected to the console MIDI Input. If this MTC connection is not present, the MMC snapshot system will not work.

A Transport Control panel is also provided in the Layout Menu. This provides a MTC readout of incoming MTC and allows direct control of the external device.

![Snapshots Menu (manual p.108)](/figures/ref-p108-1.png)

2.4 Snapshots Menu

### 2.4.21 Snapshot Notes

Pressing the notes button (towards the top left-hand corner of the main Snapshots panel) opens a notes panel, displaying any notes associated with the current Snapshot. This panel stays open whenever the notes button is active, switching to the next Snapshot when it is fired. The selected and next snapshots are shown below the text box.

![Snapshots Menu (manual p.109)](/figures/ref-p109-1.png)

To add notes, simply touch inside the notes space in the centre of the window and type your notes. To clear the text, touch the clear button in the top left-hand corner of the panel.

To format the text or background, touch the style button (next to the clear button) to open the Notes Style panel:

![Snapshots Menu (manual p.109)](/figures/ref-p109-2.png)

The text can be formatted using the text size controller and bold, italic and underline buttons in the left side of the panel. To change the colour of the text or background, select either the text colour or background button in the left side of the panel, touch inside the colour palette in the centre of the panel, and adjust the brightness using the brightness controller. The selected colour is displayed above the brightness controller.

Note: that text defaults to minimum brightness (black), and the background to maximum (white). You may need to move the brightness controller towards the middle to see the colour content.

2.4 Snapshots Menu

You can save your selected colour as one of the twelve custom colours in the right of the panel. To do this, simply select the add colour button and touch inside the desired custom colour box.

You can also copy styles from other snapshots using the copy from snapshot controls beneath the main colour palette. Use the up and down arrows to move through the snapshot list – the snapshot whose style is currently displayed is shown in the copy from snapshot text box.

Note: that copying a style from another snapshot will overwrite the current style.

### 2.4.22 Snapshot Locked

Note: Only available on non-Theatre software versions

To lock a Snapshot and prevent it from being updated, select the Snapshot and then press the Locked button on the right of the panel. It can be unlocked in a similar way.

When a Snapshot is Locked, it cannot be updated using update selected/current or deleted.

2.5 Options
