# 1.8 LCD Functions

*Chapter 1: Channel Types & Function — manual pages 59–63*

The LCD button/display is located above the channel fader and is included in every channel in both the centre section and side sections of the consoles. The channel number is displayed in the top half and the current function mode of the button is displayed in the bottom half of the display and is also indicated by its colour.

![LCD Functions (manual p.59)](/figures/ref-p059-1.png)

LCD buttons (SD5,7) or Select Buttons (SD8,9,10,11,12, Quantum consoles) are able to fulfil a number of different functions, and are even involved in selecting their own function. These functions are accessed by pressing the LCD function button, located above the bank buttons on each section of the desk. When this button is pressed, LCD displays for the channels associated with it turn yellow, indicating that they have become function mode selectors:

Selecting one of these options assigns that function mode to the LCD/select buttons for all the channels within the banks associated with that lcd function button. There are twelve different function mode options.

(1260+) The LCD function menu can be closed and have LCDs revert back to Solo function after a set period of time by turning on ‘Auto-revert LCD menu to solo’ and setting the duration in Options -> Surface.

1.8 LCD Functions

### 1.8.1 Solo

When an LCD function button is pressed, the left-hand LCD display is labelled SOLO. When SOLO mode is selected, the LCD/select buttons become solo buttons. The bottom half of the LCD display indicates which solo busses are available to the channel, as defined in the channel Setup display and the SOLO CHOICE function mode (described below). The display also shows whether each buss is AFL or PFL, as defined in the top-left corner of the master solo display.

In SOLO mode, the LCD displays are coloured according to their channel type when not soloed, and coloured green when soloed.

Note: this is the default mode of the LCD/select buttons, current when no other function modes have been selected.

### 1.8.2 Solo Choice

When an LCD function button is pressed, the second LCD display from the left is labelled SOLO CHOICE. When this mode is selected, the LCD/select buttons are used to select the solo bus assignment for that channel, toggling between 1, 2 and 1+2. In SOLO CHOICE mode, the LCD displays are coloured cyan.

### 1.8.3 Gang

When an LCD function button is pressed, the third LCD display from the left is labelled GANG. When this mode is selected, the LCD/select buttons are used for linking together all channel controls. All LCD/select buttons which are then pressed will have their controls linked. In the case of currently ganged channels, the LCD/select button can be used to remove them from their ganging group. The colour of the GANG symbols in the bottom left-hand corner of the on-screen channel display indicates what ganging groups exist: All faders which are ganged together will share one colour. Each time the GANG LCD function is selected, a new ganging group is started, as indicated by the GANG symbols turning a different colour.

To gang channels across different surfaces of the console, activate the GANG LCD function on each surface before starting to build the gang. A single cross-surface gang can then be created using the LCD/select buttons in the usual way.

To stop adding channels to the current gang and start a new gang, simply reselect the GANG LCD function. When channels are ganged together, operating any of their channel controls will cause all other channels within the ganging group to replicate that movement. Pan and phase controls are not included in gangs.

Note: it is the level change associated with the fader movement which is replicated, not the physical distance the fader is moved.

Note: that when a ganged channel is muted, those channels within the ganging group which were already muted will stay muted. When the channel is then unmuted, all channels unmute, irrespective of whether they had been initially muted.

Note: that when any member of a gang is Assigned, the Undo function will always take the faders back to their position when the channel Assignment was made. Channels can be temporarily isolated from Gangs by pressing the Option button.

Note: gangs cannot be edited once they have been created.

1.8 LCD Functions

### 1.8.4 Join CG (Control Group)

When an LCD function button is pressed, the fourth LCD display from the left is labelled JOIN CG. When this mode is selected, the LCD/select buttons can be used for assigning channels to Control Groups. Control Groups enable a number of channel output levels and mute functions to be controlled from one master fader. Control Groups can include any combination of channels from all four channel types. For more detailed information on Control Groups, please refer to the Master Section of this Manual.

### 1.8.5 Assign Faders

To assign channels to the worksurface, enter ASSIGNFADERS mode. The LCD displays will turn dark green and their lower halves will read ASSIGN. Press the LCD/select buttons for each of the channel strips to which you wish to assign new channels.

![LCD Functions (manual p.61)](/figures/ref-p061-1.png)

Press the LCD

**function**

button then

![LCD Functions (manual p.61)](/figures/ref-p061-2.png)

Press the LCD buttons for assignment

**ASSIGN**

**FADERS**

![LCD Functions (manual p.61)](/figures/ref-p061-3.png)

![LCD Functions (manual p.61)](/figures/ref-p061-4.png)

Go to Layout >

**Channel List on the**

Master Screen and expand the group of channels you want to assign and then click on the first channel you want to apply

![LCD Functions (manual p.61)](/figures/ref-p061-5.png)

To select the channels you wish to assign to those channel strips, open up the Channel List display, accessed by going to the master screen and touching Layout > Channel List. There you will find a list of all input, output and control channels that are present in the session structure, grouped by channel type. Open up the channel list for the channel type of the first channel to be assigned by touching the appropriate down arrow in the left- hand column.

The channel list can be scrolled using the scroll bar on the right of the display: To assign one of the listed channels to the channel strip, simply touch the channel name in the list. The remaining channels can now be assigned in the same way, the channels selected in the Channel List display are assigned to the selected channel strips in ascending order, starting with the lowest channel in the bank.

Note: the assign function is restricted to the currently selected bank.

Note: that when new channels are added to a session, or when a session is created, all of the existing channels can be assigned to the worksurface using the rebuild banks function within the Session Structure display.

1.8 LCD Functions

### 1.8.6 Unassign Faders

To remove channel assignments from a channel strip, enter UNASSIGN FADERS mode. The LCD displays will turn dark green and their lower halves will read UNASSIGN. Press the LCD/select button for any channel strip you wish to clear, and the strip will go blank.

### 1.8.7 Swap Faders

To swap the positions of two channels, enter SWAP FADERS mode. The LCD buttons will turn dark green and their lower halves will read SWAP. Press the LCD button for the two channels you wish to swap, and they will swap places.

### 1.8.8 Move Faders

To move channels within a channel strip, enter MOVE FADERS mode. The LCD buttons will turn dark green and their lower halves will read MOVE>>. Pressing any LCD button will result in that channel moving one space to the right. If the bank is full all channels to the right of the moved channel will move right, and any channel which had been occupying channel-strip 12 will be lost from the layout. If there is a blank channel strip anywhere to the right of the moved channel, any channels further right than the blank will not move, and the moved channels will simply fill the blank space.

For example, if the bank is occupied by input channels 1 to 12, pressing MOVE>> on channel 6 will result in channels 6 to 11 moving one space to the right, leaving a space in channel strip 6, and channel 12 being removed from the layout. Pressing MOVE>> on channel 4 will then result in channels 4 and 5 moving one space to the right, filling the space that was in channel strip 6 and leaving a space in channel strip 4.

When blank channels are moved they simply swap positions with the channel to their right. Note that any blank channels immediately to the right of the one being moved will move as well, and the blanks will move by as many channel strips as there are blank spaces being moved.

For example, if channel strips 1 to 3 are blank and Input channels 1 to 9 are occupying strips 4 to 12, pressing MOVE>> on channel strip 2 will result in blanks 2 and 3 swapping places with Input channels 1 and 2.

### 1.8.9 Copy Bank From

To copy a different bank of channels to the current bank location, press COPY BNK FROM. The message ‘PRESS | A BANK | BUTTON | FOR | COPYIN | FROM’ will be shown across the LCD displays. Simply press the bank button for the bank which you want to copy to the current location.

### 1.8.10 Copy Bank To

To copy the current bank to different bank location, press COPY BNK TO. The message ‘PRESS | A BANK | BUTTON | FOR | COPYIN | TO’ will be shown across the LCD displays. Simply press the bank button for the bank to which you want to copy.

### 1.8.11 Clear Bank

To clear all channels from a bank, press CLEAR BANK. ‘The message ‘CONFIR| CLEAR| BANK:| YES| NO’ will be shown across the LCD displays. Press NO to cancel the action or YES to continue.

Note: banks can be moved between layers, and also between sections of the console.

Note: also, that the Fader Banks display on the master screen can also be used for altering the bank layout.

Note: also, that there is no undo function for these actions. Proceed with care!

1.9 Multi Channels

### 1.8.12 Create Multi

The final LCD function, CREATE MULTI, is used to place new Multi channels onto the surface. When active, the LCD function buttons of any assigned faders will remain in their SOLO mode, whereas all unassigned faders will be available for creating new Multis. Once created, Multis can be configured in the normal way, as described below.
