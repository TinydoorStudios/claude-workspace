# V22 (v2242) Release Notes — June 2026

*Chapter 1: V22 (v2242) Release Notes — June 2026 — manual pages 2–18*

## Contents

- 1.0 v2242 Bugs Fixed
- 1.1 Setlists
- 1.2 Aux to Faders includes Groups
- 1.3 Mustard Levelling Amp
- 1.4 Snapshot Recall Times
- 1.5 Sound Devices Integration
- 1.6 LiveTrax 3 Integration
  - Macros
  - LiveTrax
  - Automatically Inserting Markers
  - Playback - Recalling Snapshots
- 1.7 Move Snapshots and Macros
- 1.8 Other Features and Changes
  - Macro Search
  - Aux Pan Data
  - New Macros
  - Mustard Dynamics - Overview screen
  - Klang Pickoff Point
  - Nodal Processing Information
  - Snapshot Panel View Options
  - Quantum 1 Surface Offline
- 1.9 Collect Diagnostics
- 1.10 v2232 Bugs Fixed

## 1.0 v2242 Bugs Fixed

- Q852 improved snapshot recall performance when using crossfades.
- Setlists
  - Setlist dropdown menu could occasionally become unresponsive.
  - Partial loading into a session that contains setlists can sometimes remove all or some setlists.
  - Macro to 'Update Current Snapshot' was not removing the asterisk when in a setlists.
- An AV (Access Violation) or corruption could sometimes occur when using setlists.
  - Corrupted sessions can be loaded into version v2242 and all possible setlist data will be recovered.
- Q852 Theatre CG 'Fader off colour' could incorrectly inherit colour from other channel types on the surface.
- Theatre Software – Current status of 'All Settings' and 'CG members only' button was occasionally showing the incorrect state.
- Q225, Q338, Q326, Q5 and Q7 - Improvement made to compressor knee value messaging with audio engine.
- 'Group' and 'Changed' surface LEDs were inverted for Q225 & Q225DS.
- Confirmation box pop ups on the right screen could sometimes appear on the master screen.
- In Audio IO, port connections could not be removed.
- SD12 - DMI-Waves was automatically being added to new sessions when Waves integration was off.

## v22 Features

## 1.1 Setlists

Setlists filter the snapshot list. All original snapshots still remain but the order and visibility can be temporarily changed.

It is important to note that setlists do not create a copy of the snapshots within the lists. It is actually firing them from the original list, now called ALL SNAPSHOTS.

This means that if in Setlist 1, the snapshot for "Snapshot 1" is updated, this change will also be seen when "Snapshot 1" is fired from the Setlists 2, 3 and ALL SNAPSHOTS.

"ALL SNAPSHOTS" list still exists, which is the full snapshot list as it exists in v21.

Please note this feature is not available in the Theatre software.

![Setlists panel button on the Snapshots screen](/figures/v22-release-notes-p003-1.png)

![Setlist options menu: New Setlist, Duplicate, Rename, Delete, Move](/figures/v22-release-notes-p003-2.png)

Click the setlist button for the Setlists panel. This is where setlists options are.

- New Setlist
- Duplicate
- Rename
- Delete
- Move

Click the dropdown to select a setlist.

![Setlist loaded, ready to add snapshots](/figures/v22-release-notes-p004-1.png)

Once a Setlist has been loaded, press the Add button and select snapshots from the list to add them to the current setlist.

![Selecting snapshots to add to the setlist](/figures/v22-release-notes-p004-2.png)

![Snapshots added to the setlist](/figures/v22-release-notes-p004-3.png)

Press the Remove button, Select Range or Select All and choose snapshots from the Setlist to remove them from that setlist - press Confirm.

![Setlist panel with Remove, Select Range, Select All and Confirm](/figures/v22-release-notes-p004-4.png)

There is also a new row on the Session Information Panel highlighting current Snapshot and which Setlist is currently active on the console.

![Session Information Panel showing the current Snapshot and active Setlist](/figures/v22-release-notes-p005-1.png)

## 1.2 Aux to Faders includes Groups

A new option has been added to Options>Solo 'Aux to Faders includes Group'

If this option is set to YES, whenever aux sends are assigned to faders, Group faders will also be included. It is possible to select which Groups this behaviour will apply to.

![Options > Solo panel with "Aux to Faders includes Group" set to YES](/figures/v22-release-notes-p005-2.png)

By default, this will apply to all Groups except the Master Group. This selection can be changed at any time and is saved to the session file. If CG Fader Controls Aux Sends is in use, this will also apply to any Aux Sends on Group faders.

## 1.3 Mustard Levelling Amp

![Mustard Levelling Amp (Silver) strip](/figures/v22-release-notes-p006-1.png)

The new Mustard Levelling Amp, the Silver one, is based on the classic tube-design, electro optical compressor sound giving warmth and thickness to sources like vocals and bass whilst still maintaining their dynamic content.

The Levelling Amp has a fixed attack and release and gives a simple set of controls.

- Peak Reduction alters the amount of signal used to trigger the compressor, effectively altering the threshold.
- Gain provides make up gain once compressed.
- The Limit/Compress switch alters the ratio of the compression.

## 1.4 Snapshot Recall Times

Snapshots have always had the ability to capture recall times at point of insertion and can now can also update their recall time from timecode.

![Snapshot recall-time capture controls](/figures/v22-release-notes-p007-1.png)

Enable capture on insert snapshot - This is the same function as before but has been relabelled from 'capture recall times'.

Update recall time for selected snapshot - This button enables the user to capture a timecode reading for an existing snapshot. This will apply to the selected snapshot.

![Update recall time for selected snapshot control](/figures/v22-release-notes-p007-2.png)

Recall offset edit range - Enables user to offset 'recall at' timecode values within a snapshot (or selection of snapshots). This can be a positive or negative offset.

## 1.5 Sound Devices Integration

Following on from the existing Astal Macro integration, v22 brings the ability to show the following on channel meters for all Quantum consoles.

- Pack on and off (Green or Grey icon)
- Audio Mute - on and off (Blue or Grey icon)
- Nexlink RSSI
- RF Quality (5 purple icons)
- Battery Level

![Sound Devices channel meter icon: pack on, unmuted, RF active](/figures/v22-release-notes-p008-1.png)

![Sound Devices channel meter icon: pack on, muted](/figures/v22-release-notes-p008-2.png)

![Sound Devices channel meter icon: RF inactive](/figures/v22-release-notes-p008-3.png)

![Sound Devices channel meter icon: 30% battery](/figures/v22-release-notes-p008-4.png)

Other meter states shown in the manual: Lost Network, Assigned to Channel, 10% Battery, Connection, no network.

To configure an Astral controller on the console, first navigate to external control, then select add device -> Astral

Check the IP addresses of the Sound Devices hardware and the console

The console IP is seen in the External Control panel, and the Astral IP in the network menu, under the control IP header. In console External Control, input the Astral IP Address. Note that Send and Receive ports are fixed to 6500 when using Astral integration.

![Sound Devices meter states (Lost Network, 10% battery, no data) and External Control panel with Astral added as a device](/figures/v22-release-notes-p008-5.png)

![External Control panel with the Astral device configured and the Open Audio IO shortcut highlighted](/figures/v22-release-notes-p008-6.png)

Next navigate to the Audio IO panel. Note there is a new shortcut button located within the External Control panel to open the Audio IO panel.

In Audio IO, select Cards & Sockets. Within this panel, there is a new integration section. Press the Astral button.

This opens the Sound Devices panel to assign Astral RF data to each socket. Any socket on any input port can be patched.

- Choose the correct Astral ID for the receiver.
- Select the Audio IO socket, then select the Astral RF channel.
- Ripple socket is also available.
- Refresh names will re-synchronise Astral RF channel names with the Console Sound Devices panel.

![Sound Devices panel assigning Astral RF data to Audio IO sockets](/figures/v22-release-notes-p009-1.png)

At the bottom of the panel make sure Enable Astral Integration is selected. There is also a 'Clear All Socket Assignments' button which will clear all socket assignments on all ports.

## 1.6 LiveTrax 3 Integration

To configure LiveTrax on the console, first navigate to External Control, then select add device -> LiveTrax

![External Control panel, add device > LiveTrax](/figures/v22-release-notes-p010-1.png)

Enter the IP address of the computer running LiveTrax. LiveTrax defaults the console send port to 3819 and autofills the send port. The receive port is the end users choice.

![LiveTrax device entry with IP address and send/receive ports](/figures/v22-release-notes-p010-2.png)

**Macros**

In the Macros panel, there is a new LiveTrax command type. The following Macro commands have been added.

![Macros panel with the new LiveTrax command type](/figures/v22-release-notes-p010-3.png)

![LiveTrax macro command list](/figures/v22-release-notes-p010-4.png)

- Play
- Stop
- Rewind
- Forward
- Return to Start
- Record Arm
- Add Marker
- Locate Marker
- Send Snapshot Markers

Note: LiveTrax default markers are labelled 'mark' not 'marker' To use the Locate Marker macro for a specific LiveTrax marker, use the format "mark1", "mark2", etc.

**LiveTrax**

Open LiveTrax, click NEW and name the session file. Click open.

![LiveTrax New Session dialog](/figures/v22-release-notes-p011-1.png)

![LiveTrax session name entry](/figures/v22-release-notes-p011-2.png)

Next, in Audio/MIDI setup, choose your

- Input Device
- Output Device
- Sample Rate
- Once confirmed, press Start.

Press the preferences cog icon on the top right of the menu bar

The preferences panel opens, choose 'Control Surfaces' and tick DiGiCo. 'Show Protocol Settings' will become available. This panel shows available IP addresses. Enter the DiGiCo console IP address and Console Receive Port. Pressing 'Create session from console' will create tracks and import the Console channel names.

![LiveTrax Control Surfaces preferences with DiGiCo protocol settings](/figures/v22-release-notes-p011-3.png)

Note This is only possible if the LiveTrax session is empty. Once this process has been actioned, the button will be greyed out. If the channel names on the console are changed, 'Request ALL Channel names from console' will update track names.

![LiveTrax tracks created from the console channel names](/figures/v22-release-notes-p012-1.png)

**Automatically Inserting Markers**

In the DiGiCo External Control panel, a new section has been added named Integration.

Press the LiveTrax Integration button to open the LiveTrax panel. When Send Snapshot Markers is set to YES and LiveTrax is armed and recording, firing a Snapshot will create a section in LiveTrax with the Snapshot name.

![External Control Integration section with LiveTrax Integration and Send Snapshot Markers](/figures/v22-release-notes-p012-2.png)

![LiveTrax section created from a fired Snapshot name](/figures/v22-release-notes-p012-3.png)

**Playback - Recalling Snapshots**

If LiveTrax is not recording, when a DiGiCo Snapshot is fired it will locate to the section with that snapshot name.

![LiveTrax locating to the section matching the fired Snapshot name](/figures/v22-release-notes-p012-3.png)

When multiple snapshots share the same name within a single LiveTrax session, recalling a snapshot on the DiGiCo console will automatically move the playhead to the most recent take or recording.

## 1.7 Move Snapshots and Macros

Move Snapshots now has a 'touch to select' function. This allows any snapshot, or selection of snapshots to be selected by touching them. When choosing the destination, there is now the option to choose before or after destination.

![Move Snapshots panel with touch-to-select and before/after destination](/figures/v22-release-notes-p013-1.png)

It is now possible to reorder Macros within the Macros panel. Pressing move will open the Move Macros panel. The behaviour in the panel is identical to the Move Snapshots panel.

![Move Macros panel](/figures/v22-release-notes-p013-2.png)

## 1.8 Other Features and Changes

**Macro Search**

Updated search function for Macros, Channel Macros and Macroders

Macro search results are now filtered to only display command types that contain the search parameter.

![Macro search filtered to matching command types](/figures/v22-release-notes-p014-1.png)

![Macro search results](/figures/v22-release-notes-p014-2.png)

**Aux Pan Data**

When using copy levels in Aux set up, the pan level is now also included in that data.

**New Macros**

Lock Console - allows the Security Mode to be set to Live mode or Unattended mode. Switch to Bank - allows a single surface to be switched to a chosen bank.

![Lock Console macro](/figures/v22-release-notes-p015-1.png)

![Switch to Bank macro](/figures/v22-release-notes-p015-2.png)

**Mustard Dynamics - Overview screen**

Mustard Dynamics gain reduction and gate meters have been added to small and large bank meters, which can be placed on the Overview or Master screen.

![Mustard Dynamics gain reduction and gate meters on the Overview screen](/figures/v22-release-notes-p015-3.png)

**Klang Pickoff Point**

When an Aux node has KLANG active, its pickoff point is hidden. Compare v21 and v22 below.

**Nodal Processing Information**

In previous versions the System>Diagnostics>Engine panel showed the Nodal Processing count. It now shows 'in use' and 'remaining' counts.

![System > Diagnostics > Engine panel showing Nodal Processing in use and remaining counts](/figures/v22-release-notes-p016-1.png)

**Snapshot Panel View Options**

Snapshot panel view option settings for brightness and text size now mirror with the floating snapshot panel.

![Snapshot panel view options for brightness and text size](/figures/v22-release-notes-p016-2.png)

**Quantum 1 Surface Offline**

Activating the Surface Offline Macro shows an indicator in the Infobar.

![Infobar indicator for the Surface Offline macro](/figures/v22-release-notes-p016-3.png)

## 1.9 Collect Diagnostics

There is now an easier way to collect log and session files plus extra information from the console and package them into a file to assist with support cases. Open System>Diagnostic>Console. Press Collect Diagnostics.

![System > Diagnostic > Console panel with Collect Diagnostics button](/figures/v22-release-notes-p017-1.png)

This opens the Diagnostics Report panel. There are options to

- save to d:\logs or a removable drive
- delete files
- include session file

![Diagnostics Report panel with save location and file options](/figures/v22-release-notes-p017-2.png)

![Diagnostics Report panel ready to start collection](/figures/v22-release-notes-p017-3.png)

To save to a removable drive, insert, choose location, then press Start to begin collection.

This will create a .ddr file which contains all support-relevant information. Once saved, please send to support@digiconsoles.com Please note this utility is not shown in the offline software.

## 1.10 v2232 Bugs Fixed

- SD7 & Q7 bridge screen brightness value was not loaded with session file if it was all the way down
- Aux Nodes were not always indicating the correct status when "safe"
- Console was intermittently sending wrong mapping information to Klang
- Intermittent issues when selecting Mustard on an LCR buss or larger.
- Loading a template session was not sending the session name to KLANG
- Onscreen LCDs on Q8 did not always draw meters correctly when switching between unpopulated banks
- Restructuring would default metering position options
- Disable master mute only worked if the left leg was the folded view channel
- 8 band EQ numbers were reversed in macros
- Occasionally, fourier plugin chains appeared as blank on the Q1
- Under-screen rotary LCD display did not always match the selected aux on Q8
- Q8 aux mixes on pan rotaries mismatch
- All pass filter in Expanded Channel Control sometimes drawn based on the wrong band after session load
- Patching a matrix input changed the name of the matrix output on the Q8 meter bridge
- Issues on Q8 when saving exceptionally large session files
- Safe padlocks were still shown on onscreen LCDs on Q8 when Spice Rack control was on faders
- Enabling Waves external control or fourier integration was selecting wrong network adaptor by default on Q1
- Q8 far right master fader was not reassigned on a default session
- DMI-Dante64@96 and DMI-OPTO in an Orange box could cause AVs
