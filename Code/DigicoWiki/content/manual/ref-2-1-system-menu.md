# 2.1 System Menu

*Chapter 2: The Master Screen — manual pages 67–72*

### 2.1.1 Diagnostics

The Diagnostics displays status reports for various elements of the console system.

Note: Indicators displayed may differ according to console model.

![System Menu (manual p.67)](/figures/ref-p067-1.png)

### 2.1.2 Oscillator

The oscillator is configured in the Oscillator display.

![System Menu (manual p.67)](/figures/ref-p067-2.png)

The frequency of the oscillator is controlled by the left-hand frequency on-screen rotary, and its audio level is controlled by the right-hand level rotary. The buttons below each rotary, can be used to set the oscillator to standard frequencies (100Hz, 440Hz, 1kHz, 10kHz) and levels (-3dB, -6dB, -12dB, -18dB). The current value of each parameter is displayed below its respective rotary.

For Stereo channels, the 1 kHz oscillator can be set to produce a pulsing ID signal on the left signal or a GLITS signal as indicated by the on-screen graphic.

2.1 System Menu

### 2.1.3 GPIO Relays

Selecting GPIO Relays opens a panel displaying the current GPI and GPO states. The panel will show the GPIO configuration for your console. The numbered 'out:' buttons allow GPOs to be triggered. If the toggle button above them is active (lighter), then touching a GPO button will switch it on (red) or off (brown). If the pulse button is active, touching a GPO button will send an 'on' pulse.

Note: GPOs which are on when entering pulse mode will stay on. Touching them while in pulse mode will switch them off.

The GPI event light in the top right-hand corner indicates when GPI messages arrive.  Below the GPO buttons is a row of indicators (labelled 'in:') showing the current state of each GPI.

The GPI macro mode can be selected, either ‘ON and OFF’ to trigger a macro on both a low to high and high to low voltage transition or ‘ON only’ to trigger only on low to high transitions.

![System Menu (manual p.68)](/figures/ref-p068-1.png)

### 2.1.4 Security

Security modes are selected in the system menu, with a choice of three levels of access:

Setup: Users have full access to every function on the console.

Live: Access to elements of the console can be limited, and password protected.

Unattended: The console worksurface is locked and cannot be operated.

![System Menu (manual p.68)](/figures/ref-p068-2.png)

User passwords can be defined for the Live and Unattended modes. To set a password, press the Set Password button. Enter the old password then the new one twice and press OK. By default, the passwords are blank.

2.1 System Menu

![System Menu (manual p.69)](/figures/ref-p069-1.png)

Note: If you should forget your password, call your Distributor to obtain a reset password. Entering the master override password will allow new passwords to be set.

To modify restrictions in Live mode, press the Set Live Restrictions button in the Console Security Panel. A range of parameters are shown, with a tick indicating that access is allowed and a cross that the item will be locked out in Live mode. Each group list can be expanded for item-specific restrictions by pressing on the down arrow in the left-hand column, as shown for FX below:

![System Menu (manual p.69)](/figures/ref-p069-2.png)

2.1 System Menu

### 2.1.5 Signal Over Indicators

Pressing this entry in the System menu opens the Signal Overs panel, showing details of any signals which have peaked. Touching an entry in the Signal Overs list brings the channel to the surface to be adjusted. The Signal Overs panel also duplicates the Clear Over Indicators button.

Note: The Signal Overs panel can also be set to open automatically when a signal peaks. This is done in the Status tab in the Options menu.

### 2.1.6 Overview Clear Screen

Some panels such as the information bar and the status indicators can be dragged with the trackball to an external overview screen. To quickly reset the position of these panels back to the Master screen, press the Overview Clear Screen button, and select Yes in the confirmation pop-up which appears.

### 2.1.7 Clear Master screen

[V1455+] A System Menu item and associated Macro “Clear Master Screen” has been added under the System Command Type.  This closes all the panels which can be opened by the user using the master screen menu buttons, except for the Snapshots/Cues panel.

### 2.1.8 Keyboard Help

The Keyboard Help button opens up a display detailing the console control elements which are available via an external keyboard (useful when using offline software):

![System Menu (manual p.70)](/figures/ref-p070-1.png)

### 2.1.9 F10: Reset FX

Pressing this entry in the System sub-menu will reset the FX module audio. This allows, for example, lengthy delay and reverb tails to be killed. To complete the reset, select Yes in the warning pop-up which appears.

Note: This will briefly bypass all of the FX units.

2.1 System Menu

### 2.1.10 F11: Reset Engine

Pressing this entry in the System sub-menu will restart the audio engine

Note: that this will briefly interrupt the audio - do not use this function unless absolutely necessary.

### 2.1.11 F12: Reset Surfaces

Pressing this entry in the System sub-menu will reset all of the worksurface controls. This function will briefly interrupt the audio on the Local I/O only.

### 2.1.12 Reset Computer

Pressing this entry in the System sub-menu shuts the console’s control computer down and restarts it. If the session is not saved, pressing Restart will bring up a warning display. Press Yes to restart without saving, or No to cancel the restart.

### 2.1.13 Set Date & Time

Pressing this entry in the System sub-menu will open the Date and Time window for the console's operating system.

### 2.1.14 Enable Extensions

Some SD and Quantum consoles can be upgraded to include a theatre mode (SD7, SD9, SD10, Q7, Q2) and a broadcast mode (SD7, SD9, SD10, SD11, Q5, Q7) which can be purchased from DiGiCo or an authorised dealer.

Navigate to System > Enable Extensions, provide the dealer with your console’s license number and they will provide you with instructions on how to complete the upgrade.

### 2.1.15 Quit to Windows/Home

Pressing this entry in the System sub-menu quits the console software but leaves Windows or Quantum Home running.  If the session is not saved, pressing Quit to Windows/Home will bring up a warning display. Press Yes to quit without saving, or No to cancel the quit.

### 2.1.16 Shutdown

Pressing this entry in the System sub-menu shuts the console’s control computer down. If the session is not saved, pressing Shutdown will bring up a warning display. Press Yes to shut down without saving, or No to cancel the shutdown.

### 2.1.17 Shutdown All

When consoles, engines or remotes are mirrored together in Full Mirror or expander mode, an additional Shutdown All button will appear at the bottom of the system menu.  When pressed, it will shut down all SD/Quantum consoles or remotes which are in either Full Mirror or Expander mirroring modes.

2.2 Files Menu
