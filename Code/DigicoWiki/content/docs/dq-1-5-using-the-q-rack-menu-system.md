# 1.5 Using the Q-Rack Menu System

* — manual pages 10–18*

The LCD Menu System on the rack is normally in a locked state and cannot be accessed.

The main display will be visible and if the rack is not connected to a console the background colour will be light blue with a band of red on the MQ-Rack and flashing red on the DQ-Rack.

If the rack is connected to a console the display will flash green.

MQ-Rack Lock screen

![Using the Q-Rack Menu System (manual p.10)](/figures/dq-p010-1.png)

DQ-Rack Lock screen

![Using the Q-Rack Menu System (manual p.10)](/figures/dq-p010-2.png)

Pressing and holding the 2 buttons marked with left and right arrows for 2 seconds unlocks the Menu System.

The Left/Right buttons scroll through the pages in the Menu System and the Up/Down buttons are used to select each item within pages that have multiple items. When an item's value can be changed the Left/Right arrows are used for this.

If the rack is left in an idle state for 2 minutes, it will relock itself.

Please refer to the following diagram for menu navigation details.

9

DQ & MQ-Rack User Guide 1.5 Using the Q-Rack Menu System

**MQ-Rack navigation**

![Using the Q-Rack Menu System (manual p.11)](/figures/dq-p011-1.png)

**DQ-Rack navigation**

![Using the Q-Rack Menu System (manual p.11)](/figures/dq-p011-2.png)

Note: The Q-Rack navigation maps display DQ-Rack and MQ-Rack menu pages in order from left to right. Wherever a “/” (or alternatively a menu page has been created underneath another menu page) has been used, the messages listed can be displayed depending on the rack’s connections. These cannot be changed by the user in the rack menu.  Where a “<” or “>” has been used this means the displayed parameter values can be changed by the user in rack system settings using the left and right arrows, the use of “<…>” means there is a selection of values to choose from in between the displayed parameter values.

10

DQ & MQ-Rack User Guide 1.5 Using the Q-Rack Menu System

Main Display.......................................................................

The main display is always visible when the Menu System is in a locked state.

On the MQ-Rack it indicates:

Link: whether the rack and the console are linked.

96k/48k: the current sample rate of the rack.

S: the clock source to which the rack is syncing.

Outs: which MADI input has control/access to the output sockets.

Lock: this reports whether the incoming MADI clock is stable (LOCK) or not (NO LOCK).

MQ-Rack Main Display

![Using the Q-Rack Menu System (manual p.12)](/figures/dq-p010-1.png)

On the DQ-Rack it indicates:

SR: sample rate at which the rack is running at.

Mode: whether the rack is in switched or redundant connection mode.

Link: this shows if the rack is receiving control information from the connected device. When receiving control data, the rack will display OK and when not receiving control data it will display NO CTRL.

Note: On a DQ-Rack, the DANTE device name (which can be set in DANTE Controller) is displayed at the top of the system setting LCD screen when in a locked state.

DQ-Rack Main Display

![Using the Q-Rack Menu System (manual p.12)](/figures/dq-p010-2.png)

11

DQ & MQ-Rack User Guide 1.5 Using the Q-Rack Menu System

Status Menu.......................................................

The Status menu is the first menu visible once the rack is unlocked. No adjustments are possible from this menu.

On the MQ-Rack the status menu page displays the sample rate the rack is working at, whether it has a link via the MADI MAIN, MADI AUX or both and the current temperature of the rack.

MQ-Rack Status Menu

![Using the Q-Rack Menu System (manual p.13)](/figures/dq-p013-1.png)

On the DQ-Rack the status menu shows the working sample rate, whether the rack is receiving control information and the current internal temperature of the rack.

DQ- Rack Status Menu

![Using the Q-Rack Menu System (manual p.13)](/figures/dq-p013-2.png)

Line/AES Menu ...................................................

In the Line/AES menu page, the user can change the state of the 4 switchable Line/AES outputs, by selecting the desired socket and changing it between Line and AES using the left and right buttons. When the socket is in AES mode the LED light below the socket will light up blue.

Note: On Quantum consoles, this setting’s status can be displayed and switched from within the Audio I/O panel on the console.

![Using the Q-Rack Menu System (manual p.13)](/figures/dq-p013-3.png)

12

DQ & MQ-Rack User Guide 1.5 Using the Q-Rack Menu System

Oscillators Menu........................................................................

In the Oscillators menu, the user can apply the rack’s internal oscillator signal all output sockets. To enable the oscillator, select the out option, hold the right button down and a bar next to the word OFF will begin to fill, when the bar fills, the word will change to ON and signal will be applied to all 24 outputs.

From within the Oscillators menu one of 8 frequencies can be selected between 20Hz and 20KHz, on default settings the frequency is set to 1KHz.

The level of the oscillator can also be changed to be a range of volumes between a value of -96dB and 0dB, at default setting the level is -96dB.

![Using the Q-Rack Menu System (manual p.14)](/figures/dq-p014-1.png)

PSU Status Menu .........................................................................

The PSU Status menu page shows readings for all rack PSU voltages. No adjustments are possible from this menu.

![Using the Q-Rack Menu System (manual p.14)](/figures/dq-p014-2.png)

Version Menu .................................................

The Version menu page shows the software versions of the Host and FPGA currently installed in the rack.

No adjustments are possible from this menu.

MQ-Rack version menu

![Using the Q-Rack Menu System (manual p.14)](/figures/dq-p014-3.png)

On the DQ-Rack there are additional versions displayed, for the DNT and Dante software versions.

DQ-Rack version menu

![Using the Q-Rack Menu System (manual p.14)](/figures/dq-p014-4.png)

13

DQ & MQ-Rack User Guide 1.5 Using the Q-Rack Menu System

Display Menu ................................................................

The brightness of the LCD system settings screen can be adjusted from within the rack in the display menu.

The default value is set to 100% brightness and can be adjusted using the left and right buttons in increments of 10%, down to a minimum of 10% brightness.

![Using the Q-Rack Menu System (manual p.15)](/figures/dq-p015-1.png)

Default Rack Menu ................................................................

This page allows the user to set all rack parameters to their default values.

When the display shows Hold Right To Default… as highlighted, hold the Right arrow button to confirm and a bar will begin to fill underneath the text, when the bar fills the rack will reset and the system setting will lock again.

![Using the Q-Rack Menu System (manual p.15)](/figures/dq-p015-2.png)

14

DQ & MQ-Rack User Guide 1.5 Using the Q-Rack Menu System

MADI Sync Menu (MQ-Rack only) ................................................................

This page allows selection of the MQ-Rack sync source.

When selecting a sync source:

Auto will automatically sync to any connection with a clock signal. If the rack is not receiving a connection with a valid clock signal it will use its internal sync. MADI MAIN and MADI AUX sockets can be given priority so that if a clock signal comes into the rack it will sync to the port with priority.

Selecting the Main or Aux setting in the Select parameter forces the active sync source to be the selected connection and is not affected by the priority option.

The Active parameter shows which socket the rack is currently syncing to.

The Lock parameter displays from which sources a stable clocking source is received.

![Using the Q-Rack Menu System (manual p.16)](/figures/dq-p016-1.png)

Out Routing Menu (MQ-Rack only) ..............................................................

The Out Routing menu is for selecting which MADI inputs from a console can output via the MQ-Rack’s 24 physical outputs.

![Using the Q-Rack Menu System (manual p.16)](/figures/dq-p016-2.png)

Internal SR Menu (MQ-Rack only) ...........................................................

The Internal SR menu allows selection of the rack’s sample rate.

This is only possible to sync from the internal clock if the MADI Sync Active is internal.

Available options are 48K and 96K

![Using the Q-Rack Menu System (manual p.16)](/figures/dq-p016-3.png)

15

DQ & MQ-Rack User Guide 1.5 Using the Q-Rack Menu System

Network Menu (DQ-Rack only) ...........................................................

The DQ-Rack has two ethernet ports (Primary and Secondary) which can be used to connect the rack to a DANTE network. The rack can either operate in SWITCHED or REDUNDANT mode which can be set in DANTE Controller. Primary and secondary port status are reported in the DQ-Rack Network menu as either UP meaning the port is connected with a valid IP address or DOWN meaning the port is not connected with a valid IP address. The IP address for each ethernet port is reported below primary and secondary port status.

Note: When first powering on a DQ-Rack, whilst the rack is initialising a “Reset” message will be displayed in network mode field.

![Using the Q-Rack Menu System (manual p.17)](/figures/dq-p017-1.png)

16

DQ & MQ-Rack User Guide 1.6 Connecting a DANTE rack
