# 2.2 Files Menu

*Chapter 2: The Master Screen — manual pages 72–83*

### 2.2.1 Templates

Touching on Templates in the Files menu brings up the Session Templates display. This lists any ordinary session files which are located in the folder D:\Templates (or C:\Templates in offline), along with key session information.

Note: If this folder doesn't exist, it should be created manually. The required template sessions can then be copied into it.

[V1455+] A Save as template option in the Save as New File panel allows the user to save the entire session as a single template, the session template is saved into the templates folder, subsequent saves using the save session button or macro will save changes into the sessions folder not the templates folder.

![Files Menu (manual p.72)](/figures/ref-p072-1.png)

To load a Session Template, simply select it in the list and touch the Load button.

### 2.2.2 Session Structure

Touching on Session Structure in the Files menu brings up the Session Structure display. This is where a session is named and where the channel allocation and sample rate for the session are configured. While changes to session structure can be made once a session has been started, it is best to try and set these parameters before configuring the session. Session Structure changes are not implemented until the Restructure button in the bottom right-hand corner of the display is pressed.

To name the session, touch the session title box, type the session name using the either the on-screen or external keyboard, and press OK.

Set the Session sample rate at the top of the panel.

2.2 Files Menu

Below the session title, each channel type has its own setup row, which includes clear all and auto-route buttons, and a display of the current number of channels in the session. To adjust any of the channel allocations, touch on the associated channel count box, and either enter a number using the pop-up number keypad or adjust using the assigned touch turn controller.

On some consoles, the matrix inputs, matrix outputs and control group allocations are fixed.

For specific console model information, please refer to Configuring Session page in the Getting Started Section.

Note: That processing channels are reserved for the master buss, talkback channel and stereo solos.

![Files Menu (manual p.73)](/figures/ref-p073-1.png)

Touch numbers to

edit with pop-up

![Files Menu (manual p.73)](/figures/ref-p073-2.png)

Select session

keypad or TouchTurn

sample rate

![Files Menu (manual p.73)](/figures/ref-p073-3.png)

![Files Menu (manual p.73)](/figures/ref-p073-4.png)

Enter Session title

Set number of Inputs Channels

Set number and type of Aux

Set number and type of Group

![Files Menu (manual p.73)](/figures/ref-p073-5.png)

Set number of Matrix Inputs

Set number of Matrix Outputs

Set number of Control Groups

![Files Menu (manual p.73)](/figures/ref-p073-6.png)

Total number of unallocated

![Files Menu (manual p.73)](/figures/ref-p073-7.png)

Labels: Total number · of spare · busses · processing

The above figure shows the SD7 Session Structure Panel. Pressing the Default All button followed by the Restructure button will automatically configure a new session where the inputs from Audio I/O Port 1 are routed to input channels and the Master Buss is routed to Local outputs 1 & 2, also to Port 1 rack outputs 1 &

2. All input channels will be routed to the Master Buss and the console headphones will be fed by the Master

Buss when nothing else is soloed.

If the clear all button is pressed, any non-default routing or processing (EQ, dynamics etc) will be cleared from the channels in the session when the Restructure button is pressed. This is especially useful when restructuring an existing session to make a new session.

2.2 Files Menu

The auto-route button automatically routes the physical inputs and outputs in the rack to the inputs and output channels in the session when the Restructure button is pressed, thus saving the operator from manually routing them in the channel Setup and Output displays. For example, auto-routing 48 inputs will route the first physical input (e.g. 1: Mic 1) to input channel 1, the second physical input (1: Mic 2) to input channel 2 until you either run out of inputs or channels. Auto-routes are as follows:

- Input Channels auto-route with physical inputs

- Aux, Group and Matrix Channels auto-route to physical outputs

- Matrix Inputs auto-route with group outputs

Note: Auto-routing can only be used in conjunction with the Clear All button and is not available for input channel direct outs.

Important Note: Auto-routing overwrites any previous input and output routing.

Note: The outputs of Aux, Group and Matrix channels are auto-routed in sequence: Aux outputs followed by Group outputs, followed by Matrix outputs.

The send point for input channel direct outs can be set globally using the direct sends button toward the top right-hand corner of the display. The button is made active by touching the input channels Clear All button. The direct sends button then toggles between Post-Fader, Pre-Fader and Pre-Mute.

Similarly, the send point for aux channel outputs can be set globally using the aux sends button to the left of the direct sends button. The button is made active by touching the aux busses Clear All button. The aux sends button then toggles between Post-Fader, Pre-Fader and Pre-Mute.

**Aux and Group Order**

By default, the aux and group channels are ordered with the stereo channels following the mono channels. These orders can be altered in the Order of Aux Busses and Order of Group Busses displays, accessed by pressing the Aux Order and Group Order buttons on the right-hand side of the display.

Busses can be added using the buttons in the top-right of the display. To change a busses position or delete it, touch the buss in the display’s list and use the buttons in the bottom-right of the display.

Note: that only the mono/stereo format of the Busses and their display within the input channel can be reordered in this display. Channel settings are not reordered. The console layout can be reordered using the Rebuild Banks function described below.

(1272+) Channel Order As with aux and group order, channels can be reordered in the session structure panel where mono or stereo channels can be quickly added, deleted or moved.

The Master buss is the first of the largest buss type (or first stereo buss on SD7/Q7), regardless of the order you place the busses in.

The audio i/o and comms rows beneath the standard channel-type rows allow the settings of the audio io cards and talkback function to be reset.

The clear snapshots and clear macros buttons towards the bottom-right of the window can be used to clear any existing snapshots and macros when making a new session.

2.2 Files Menu

Rebuild Banks: When changing the number of allocated channels in any section (input channels, busses etc), you can restructure the session without rebuilding banks, meaning that any additional channels you have allocated will not be “placed” on the worksurface, and need to be manually assigned to faders.  If, however, you restructure a session with Rebuild Banks (either Horizontally or Vertically) enabled, the worksurface will be built with all channels available on the worksurface in a default layout. Rebuilding horizontally will result in input channels being spread across the top layer of both sides of the console, using as many banks as required, with output channels being assigned to Layer 2. Rebuilding vertically will result in input channels being assigned to Layer 1 on the left side of the console, and output channels to Layer 1 on the right. See the Session Structure section of Chapter 3 for more details.

Note: that when Rebuild Banks is used, any non-default configuration of the channel layout is lost.

To implement changes in the Session Structure display, touch the Restructure button in the bottom right-hand corner. To exit the display without implementing the changes, touch Cancel, located below the Restructure button.

To clear unimplemented changes from the display, touch REVERT, located in the top left-hand corner of the display.

### 2.2.3 Load Session

Touching this entry in the File menu opens the Load Session display. The left-hand column of the display shows the file directory. At the top of the directory are two buttons which switch the list of folders below them between the contents of the console computer’s internal d:\Projects folder and the contents of a removable USB drive. Each folder can be expanded by clicking the + symbol to its right. The list can be scrolled using the scroll bar to its right.

When a folder or sub-folder in the left-hand directory is expanded, a list of the session files contained within it appears in the list in the centre of the screen. The list displays the Filename, creation Date & Time, and Description of the session. In addition, the list also displays the number of Inputs, Auxes (mono, stereo), Groups (mono, stereo) and Matrix channels (ins/outs).

To load a session, touch the session in the list and press Load, located in the bottom right-hand corner of the display. To close the display without loading a session, press Cancel, located below the Load button and also found in the top right-hand corner of the display.

Once a session is loaded, a summary of the currently loaded session is displayed in the Information Bar which is normally found on the Master screen. Once any changes have been made to the session, the File: indication in this display will only show the folder of the most recently saved session, not the file name.

When active, keep old presets will add any existing console presets to the session being loaded.  When disabled, existing presets will be cleared before session load.

Note: If any of the buttons in the right-hand column of the window are active, sessions cannot be selected for loading from the list.

2.2 Files Menu

![Files Menu (manual p.76)](/figures/ref-p076-1.png)

Select Internal or removable USB, Internal files saved in D:\Projects

Select a file

File details

![Files Menu (manual p.76)](/figures/ref-p076-2.png)

Note: that column widths can be adjusted by dragging their borders within the title row. To return all columns to their default widths, press RESET WIDTHS, in the top left-hand corner of the window.

**Partial Load**

When a session file is selected from the list, the Partial Load button becomes available in the top right corner of the panel. Pressing this button opens the panel shown below where elements of the session can be selected for Partial Loading. Possible selections include ranges of Input channels, Matrix inputs, Matrix outputs and Graphic EQs, banks and layout, Presets and Macros.

There are also options to Partial Load all or some of the Snapshots from the selected session.

Replace Snapshots will remove the existing Snapshot list and replace it with the partially loaded one.

Add Snapshots will open a Snapshot list where snapshots can be selected to be imported into the existing session.

Note: that if Snapshots are imported that contain data that the existing session is not capable of recalling (e.g. channels that don't exist) then this data will be ignored when the Snapshot is recalled.

The numbering of imported Snapshots will be the same as their original numbers so there may be duplication in Snapshot numbers after the import.

2.2 Files Menu

![Files Menu (manual p.77)](/figures/ref-p077-1.png)

![Files Menu (manual p.77)](/figures/ref-p077-2.png)

### 2.2.4 Save Session

Touching this entry in the File menu saves the current session. Once the session has been saved, a confirmation pop-up appears displaying the location of the saved session file.

Note: This function overwrites the most recently saved session. If you want to retain the most recently saved session, save the current session as a new session.

2.2 Files Menu

### 2.2.5 Save As New File

Touching this entry in the File menu opens the Save Session display. At the top of the display are two text boxes showing a file name and session title. The file name will normally be ‘sessionxxx.ses’ where xxx is an auto-incrementing number and the session title is the same as the current session. If the session has not been changed since it was last saved, the file name will be the same as the current session. To edit the file name and session title, touch the relevant text box, enter the new name or title in the on-screen or external keyboard, and press OK. To overwrite another session, or to save the session in a new folder but with a previously used name, touch the session of that name and its name will appear in the file name box.

The location of the session file to be saved is defined in the directory in the left-hand side of the display. At the top of the directory are two buttons which switch the list of folders below them between the contents of the console computer’s internal d:\Projects folder and the contents of a removable USB drive. Each folder can be expanded by clicking the + symbol to its right. The list can be scrolled using the scroll bar to its right. Touch the button and folder within which you want to save the session.

To create a new folder, select the location for the folder in the way described above, touch the new folder button in the right-hand side of the display, type the folder’s name using the external keyboard and press the external keyboard’s return button. To rename a folder, touch the folder within the directory, touch the rename folder button in the right-hand side of the display, type the folder’s new name using the external keyboard and press the external keyboard’s return button.

To delete a folder, touch the delete folder button in the right-hand side of the display, touch the folder to be deleted and touch Yes in the confirmation pop-up which appears.

Note: This action cannot be undone.

Once the session has been named and its save location has been selected, save the session by pressing Save, located in the bottom right-hand corner of the display. To close the display without saving, press Cancel, located below the Save button and also found in the top right-hand corner of the display. If you attempt to save the session under a file name which already exists within that folder, a pop-up appears, warning that continuing will cause the file with that name to be overwritten. Touch Yes to continue, No to cancel.

Note: Overwriting the most recently saved session can be performed more quickly using the Save Session function described above.

Once the session has been saved, a confirmation pop-up appears displaying the location of the saved session file.

To rename a file, touch the file to be renamed followed by rename file, located in the right-hand side of the display, enter the new name into the on-screen or external keyboard and press OK. If rename file is pressed without a file being selected, the first file in the list will be automatically selected for renaming.

Note: The file name is the only file element that can be edited once the file has been saved.

To delete files, select the folder containing the files to be deleted and touch delete files. To delete all files in the folder, touch select all, followed by confirm delete. To delete one file or a selection of files, touch the files you wish to delete followed by confirm delete. To delete a consecutive range of files, touch select range, touch the first and last files included in the range to be deleted, and touch confirm delete.  To complete the deletion process, touch Yes in the confirmation pop-up which appears.

2.2 Files Menu

[V1455+] A Save as template option allows the user to save the entire session as a single template, the session template is saved into the templates folder, subsequent saves using the save session button or macro will save changes into the sessions folder not the templates folder.

![Files Menu (manual p.79)](/figures/ref-p079-1.png)

Select Internal or removable USB, Internal files saved in D:\Projects

Enter file name

Enter description

![Files Menu (manual p.79)](/figures/ref-p079-2.png)

Save As Template

Note: Column widths can be adjusted by dragging their borders within the title row. To return all columns to their default widths, press RESET WIDTHS, in the top left-hand corner of the window.

**Set Backup**

Located on the right-hand side of both the Load Session and Save as new file panels, are the Set backup and Copy Backup Buttons.  The backup function enables batch copying of session files to and from a connected removable drive.  Press the set backup button and touch on the session files to copy to/from the removable drive. Once selected, an asterisk will appear in the "B" column of the panel.  Now press the copy backup button and after the confirmation stage, the selected session files will be copied to/from the removable drive.

Note: The Copy Backup button will not be available until a valid removable drive has been connected to the console's USB port.

2.2 Files Menu

### 2.2.6 Load Presets

Touching this entry in the File menu opens the Load Presets display. This allows Channel, FX, Graphic EQ and Matrix presets created in other sessions to be imported into the current session. The left-hand column of the display shows the file directory. At the top of the directory are two buttons which switch the list of folders below them between the contents of the console computer’s internal d:\Projects folder and the contents of a removable USB drive. Each folder can be expanded by clicking the + symbol to its right. The list can be scrolled using the scroll bar to its right.

When a folder or sub-folder in the left-hand directory is touched, a list of the Preset files contained within it appears in the list in the centre of the screen. The list displays the Filename, creation Date & Time, and Description of the preset file. In addition, the list also displays the number of Input, Out (fx), GrEQ (Graphic EQ) and Matrix presets contained within the preset file.

To load a set of presets, touch the preset file in the list and press Load, located in the bottom right-hand corner of the display. To close the display without loading a session, press Cancel, located below the Load button, also found in the top right-hand corner of the display.

Note: A session’s presets are also saved as part of the session file.

Note: If any of the buttons in the right-hand column of the window are active, sessions cannot be selected for loading from the list.

### 2.2.7 Save Presets

Touching this entry in the File menu opens the Save Presets display. At the top of the display is a text box showing the file name of the most recently created presets file. It will normally be ‘presetsxxx.pre’ where xxx is an auto-incrementing number. To edit the file name, touch the text box, enter the new name or title in the on-screen or external keyboard, and press OK. To overwrite another file, or to save the file in a new folder but with a previously used name, touch the file of that name and its name will appear in the file name box.

The location of the presets file to be saved is defined in the directory in the left-hand side of the display. At the top of the directory are two buttons which switch the list of folders below them between the contents of the console computer’s internal d:\Projects folder and the contents of a removable USB drive. Each folder can be expanded by clicking the + symbol to its right. The list can be scrolled using the scroll bar to its right. Touch the button and folder within which you want to save the session.

Once the presets file has been named and its save location has been selected, save it by pressing Save, located in the bottom right-hand corner of the display. To close the display without saving, press Cancel, located below the Save button, also found in the top right-hand corner of the display. If you attempt to save the set of presets under a file name which already exists within that folder, a pop-up appears, warning that continuing will cause the file with that name to be overwritten. Touch Yes to continue, No to cancel.

Note: A session’s presets are also saved as part of the session file.

2.2 Files Menu

### 2.2.8 Global Set to Defaults

The Global Set to Defaults Panel, opened via the Files menu, allows certain settings to be applied globally to the console. Select the Channel type from the list on the left side of the panel, and then select the action from the list to the right. Most actions are self-explanatory, with the possible exception of the following: - blend LR only moves all the LR/LCR blend controls to LR.

**-**

**blend LCR**

moves all the LR/LCR blend controls to LCR

**-**

**groups off**

unroutes all sends to Groups

Note: that multiple channel types can be selected simultaneously.

![Files Menu (manual p.81)](/figures/ref-p081-1.png)

The undo button in the top left undoes all changes since the panel was opened.

Note: Once the panel is closed, changes cannot be undone.

2.2 Files Menu

### 2.2.9 Session Notes

The File menu Session Notes button opens a panel in which can be used for saving any important session information:

![Files Menu (manual p.82)](/figures/ref-p082-1.png)

### 2.2.10 Session Report

In the Files menu there is also a Session Report button.  This lists the session details on the master screen in an RTF compatible format.

Across the top, the three include buttons can be used to define what optional extras are included in the report: channels, audio i/o and snapshots.

The save to internal button at the top right of the panel will save the report in the D:\Projects as the session file name suffixed with .rtf. The save to removable will save the report to any USB drive insert in the consoles USB port.

![Files Menu (manual p.82)](/figures/ref-p082-2.png)

2.3 Layout Menu
